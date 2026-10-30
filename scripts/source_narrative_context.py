"""Connect one verified narrative read to RF input claims and used parameters.

This module never resolves paths, downloads, parses originals, or starts a model.
The existing reader verifies the bundle once; this adapter only links excerpts
selected by the caller to an existing revenue calculation graph. The source
owner's support/context closure and a bounded coverage diagnostic are retained in
a versioned citation trace; the claim fields and the formula dependencies stay
exactly as they were.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from company_wiki_narrative_contracts import NarrativeContext
from company_wiki_narrative_reader import read_narrative_context
from contracts.evidence import text_sha256
from contracts.source_clock import utc_timestamp
from forecast.calc import collect_parameter_roles
from forecast.dependencies import parameter_formula_refs
from narrative_citation_context import (
    NarrativeCitationError, citation_dependency, citation_trace, resolve_span, selection,
)

BASE_BINDING_FIELDS = {"span_id", "claim_id", "parameter_id", "support_type"}
SELECTION_FIELDS = {"citation_group_id", "citation_view"}


def _read_time(value: dict) -> str:
    receipt = value["read_receipt"]
    return receipt["observed_at"] if value["schema_version"] == "revenue-narrative-context/3" else receipt["read_at"]


def narrative_read_receipt(context: NarrativeContext) -> dict:
    value = context.to_dict()
    projected = value["schema_version"] == "revenue-narrative-context/3"
    receipt = {"schema_version": "revenue-narrative-consumption/3" if projected else "revenue-narrative-consumption/1",
        "status": "not_consumed", "narrative_ref": value["narrative_ref"], "read_at": _read_time(value),
        "quality_status": value["quality_status"], "selection": value["selection"], "dependencies": []}
    if projected:
        receipt.update(subject_ref=value["narrative_ref"]["subject_ref"],
                       parent_count=value["read_receipt"]["parent_count"],
                       lineage_sha256=value["read_receipt"]["lineage_sha256"])
    receipt["citation_trace"] = citation_trace(value)
    if "summary_assessment" in value:
        receipt["summary_assessment"] = deepcopy(value["summary_assessment"])
    return receipt


def _captured_parent(value: dict, source: dict | None) -> dict:
    if source is None:
        raise ValueError("narrative source does not bind to the input source capture")
    refs = value["parent_source_refs"] if value["schema_version"] == "revenue-narrative-context/3" else [value["source_ref"]]
    matches = [ref for ref in refs if ref["content_sha256"] == source["capture"]["snapshot_sha256"]]
    if len(matches) != 1:
        raise ValueError("narrative source does not bind to the input source capture")
    ref = matches[0]
    trace = source.get("company_wiki_trace", {}).get("source_ref")
    if trace is not None and trace != ref:
        raise ValueError("narrative parent differs from the prepared SourceRef")
    return ref


def _source_locator(span: dict, *, projected: bool) -> str:
    return span["structured_value"]["source_locator"] if projected else span["locator"]


def _formula_refs(data: dict, parameter_id: str, index: dict) -> list[dict]:
    return parameter_formula_refs(data, parameter_id, index)


def _claim(binding: dict, span: dict, source: dict, verified_date: str, verified_by: str, *, projected: bool = False) -> dict:
    excerpt = span["raw_text"]
    if not isinstance(excerpt, str) or not excerpt.strip() or span["parse_status"] != "parsed":
        raise ValueError("selected narrative span has no usable parsed text")
    support = binding["support_type"]
    if support not in {"rationale_support"}:
        raise ValueError("narrative qualitative claim requires an explicit evidence role")
    return {"claim_id": binding["claim_id"], "source_id": source["source_id"],
            "target_type": "parameter", "target_id": binding["parameter_id"],
            "support_type": support, "locator": _source_locator(span, projected=projected), "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt),
            "content_sha256": source["capture"]["snapshot_sha256"],
            "capture_receipt_sha256": source["capture"]["receipt_sha256"],
            "verification_status": "opened_and_checked", "verified_by": verified_by,
            "verified_date": verified_date}


def _binding_selection(binding: dict) -> tuple[str | None, int | None]:
    """Keep the old field refusal, with a named code for citation selection fields."""
    missing = BASE_BINDING_FIELDS - set(binding)
    if missing:
        raise ValueError("narrative binding fields are invalid")
    extra = set(binding) - BASE_BINDING_FIELDS
    if extra - SELECTION_FIELDS:
        if any(isinstance(key, str) and key.startswith("citation_") for key in extra):
            raise NarrativeCitationError(
                "narrative_citation_binding_fields",
                f"unsupported citation selection fields: {sorted(str(key) for key in extra - SELECTION_FIELDS)}",
            )
        raise ValueError("narrative binding fields are invalid")
    return selection(binding)


def consume_narrative_input(
    data: dict, *, request: dict, bindings: list[dict], source_id: str,
    catalog_config: Path, timeout_seconds: float = 30, verified_by: str = "RF narrative reader",
) -> tuple[dict, dict]:
    """Read a bundle once and bind selected spans to existing used parameters.

    A metadata reference or an unreferenced summary yields not_consumed. No
    assumption value or evidence role is inferred from a summary's existence.
    Invalid/unavailable references propagate the existing bounded read failure.
    A span the source attributes to the context partition never becomes support.
    """
    context = read_narrative_context(request, catalog_config=catalog_config,
                                     timeout_seconds=timeout_seconds)
    value = context.to_dict()
    updated = deepcopy(data)
    source = next((item for item in updated.get("sources", []) if item["source_id"] == source_id), None)
    parent = _captured_parent(value, source)
    projected = value["schema_version"] == "revenue-narrative-context/3"
    if data.get("as_of_date") != request["as_of_date"]:
        raise ValueError("narrative information date does not match input")
    index = {item["parameter_id"]: item for item in updated.get("parameters", [])}
    used = collect_parameter_roles(updated, index)["used"]
    spans = {item["span_id"]: item for item in value["evidence_spans"]}
    receipt = narrative_read_receipt(context)
    verified_date = utc_timestamp(_read_time(value), "narrative read_at").date().isoformat()
    claims = updated.setdefault("evidence_claims", [])
    claim_ids = {item["claim_id"] for item in claims}
    trace_dependencies: list[dict] = []
    for binding in bindings:
        group_id, view = _binding_selection(binding)
        pid, cid = binding["parameter_id"], binding["claim_id"]
        if pid not in used or cid in claim_ids or binding["span_id"] not in spans:
            raise ValueError("narrative binding requires a unique claim and a used parameter/span")
        span = spans[binding["span_id"]]
        if span["source_id"] != parent["source_id"]:
            raise ValueError("selected narrative span differs from the captured parent source")
        formula_refs = _formula_refs(updated, pid, index)
        if not formula_refs:
            raise ValueError("narrative binding does not reach an actual segment formula")
        resolution = resolve_span(value, span_id=binding["span_id"],
                                  group_id=group_id, view=view)
        claims.append(_claim(binding, span, source, verified_date, verified_by, projected=projected))
        claim_ids.add(cid)
        parameter = index[pid]
        parameter.setdefault("claim_ids", []).append(cid)
        if source_id not in parameter.setdefault("source_ids", []):
            parameter["source_ids"].append(source_id)
        receipt["dependencies"].append({
            "span_id": span["span_id"], "locator": span["locator"],
            "parser_name": span["parser_name"], "parser_version": span["parser_version"],
            "source_id": parent["source_id"],
            "source_sha256": parent["content_sha256"],
            "claim_id": cid, "parameter_id": pid, "formula_refs": formula_refs,
        })
        if projected:
            receipt["dependencies"][-1].update(source_locator=span["structured_value"]["source_locator"],
                pointer=span["structured_value"]["pointer"], subject_ref=value["narrative_ref"]["subject_ref"])
        trace_dependencies.append(citation_dependency(resolution=resolution, claim_id=cid, parameter_id=pid))
    if receipt["dependencies"]:
        receipt["status"] = "consumed"
    receipt["citation_trace"] = citation_trace(value, dependencies=trace_dependencies)
    return updated, receipt
