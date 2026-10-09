"""Connect one verified narrative read to RF input claims and used parameters.

This module never resolves paths, downloads, parses originals, or starts a model.
The existing reader verifies the bundle once; this adapter only links excerpts
selected by the caller to an existing revenue calculation graph.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from company_wiki_narrative_contracts import NarrativeContext
from company_wiki_narrative_reader import read_narrative_context
from contracts.evidence import text_sha256
from forecast.calc import collect_parameter_roles


def narrative_read_receipt(context: NarrativeContext) -> dict:
    value = context.to_dict()
    return {"schema_version": "revenue-narrative-consumption/1", "status": "not_consumed",
            "narrative_ref": value["narrative_ref"], "read_at": value["read_receipt"]["read_at"],
            "quality_status": value["quality_status"], "selection": value["selection"],
            "dependencies": []}


def _formula_refs(data: dict, parameter_id: str, index: dict) -> list[dict]:
    """Trace an input through derived inputs into actual segment driver formulas."""
    def depends(identifier, seen):
        if identifier == parameter_id:
            return True
        if identifier in seen:
            return False
        parameter = index.get(identifier, {})
        inputs = parameter.get("input_parameter_ids", [])
        return any(depends(child, seen | {identifier}) for child in inputs)

    refs = []
    for segment in data.get("segments", []):
        for scenario, config in segment.get("scenarios", {}).items():
            for driver, ids in config.get("driver_parameter_ids", {}).items():
                if any(depends(identifier, set()) for identifier in ids):
                    refs.append({"segment": segment["name"], "scenario": scenario,
                                 "model": config["model"], "driver": driver,
                                 "output": "recognized_revenue"})
    return refs


def _claim(binding: dict, span: dict, source: dict, as_of: str, verified_by: str) -> dict:
    excerpt = span["raw_text"]
    if not isinstance(excerpt, str) or not excerpt.strip() or span["parse_status"] != "parsed":
        raise ValueError("selected narrative span has no usable parsed text")
    support = binding["support_type"]
    if support not in {"rationale_support"}:
        raise ValueError("narrative qualitative claim requires an explicit evidence role")
    return {"claim_id": binding["claim_id"], "source_id": source["source_id"],
            "target_type": "parameter", "target_id": binding["parameter_id"],
            "support_type": support, "locator": span["locator"], "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt),
            "content_sha256": source["capture"]["snapshot_sha256"],
            "capture_receipt_sha256": source["capture"]["receipt_sha256"],
            "verification_status": "opened_and_checked", "verified_by": verified_by,
            "verified_date": as_of}


def consume_narrative_input(
    data: dict, *, request: dict, bindings: list[dict], source_id: str,
    catalog_config: Path, timeout_seconds: float = 30, verified_by: str = "RF narrative reader",
) -> tuple[dict, dict]:
    """Read a bundle once and bind selected spans to existing used parameters.

    A metadata reference or an unreferenced summary yields not_consumed. No
    assumption value or evidence role is inferred from a summary's existence.
    Invalid/unavailable references propagate the existing bounded read failure.
    """
    context = read_narrative_context(request, catalog_config=catalog_config,
                                     timeout_seconds=timeout_seconds)
    value = context.to_dict()
    updated = deepcopy(data)
    source = next((item for item in updated.get("sources", []) if item["source_id"] == source_id), None)
    if source is None or source["capture"]["snapshot_sha256"] != value["source_ref"]["content_sha256"]:
        raise ValueError("narrative source does not bind to the input source capture")
    if data.get("as_of_date") != request["as_of_date"]:
        raise ValueError("narrative information date does not match input")
    index = {item["parameter_id"]: item for item in updated.get("parameters", [])}
    used = collect_parameter_roles(updated, index)["used"]
    spans = {item["span_id"]: item for item in value["evidence_spans"]}
    receipt = narrative_read_receipt(context)
    claims = updated.setdefault("evidence_claims", [])
    claim_ids = {item["claim_id"] for item in claims}
    for binding in bindings:
        if set(binding) != {"span_id", "claim_id", "parameter_id", "support_type"}:
            raise ValueError("narrative binding fields are invalid")
        pid, cid = binding["parameter_id"], binding["claim_id"]
        if pid not in used or cid in claim_ids or binding["span_id"] not in spans:
            raise ValueError("narrative binding requires a unique claim and a used parameter/span")
        span = spans[binding["span_id"]]
        claims.append(_claim(binding, span, source, data["as_of_date"], verified_by))
        claim_ids.add(cid)
        parameter = index[pid]
        parameter.setdefault("claim_ids", []).append(cid)
        if source_id not in parameter.setdefault("source_ids", []):
            parameter["source_ids"].append(source_id)
        receipt["dependencies"].append({
            "span_id": span["span_id"], "locator": span["locator"],
            "parser_name": span["parser_name"], "parser_version": span["parser_version"],
            "source_id": value["source_ref"]["source_id"],
            "source_sha256": value["source_ref"]["content_sha256"],
            "claim_id": cid, "parameter_id": pid, "formula_refs": _formula_refs(updated, pid, index),
        })
    if receipt["dependencies"]:
        receipt["status"] = "consumed"
    return updated, receipt
