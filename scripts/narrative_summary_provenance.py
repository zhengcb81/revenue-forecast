"""Bounded RF evidence DTO for an actually read, explicitly adopted summary.

The source adapter constructs this from the verified public reader exactly once.
Calculation/publication only revalidate the frozen RF data; they never reopen a
catalog, reparse a source, invoke a model, or create an authorization receipt.
Input/publication hashes bind research reasons too. Partial source records prove
local consistency, not external authenticity independently of the source reader.
"""

from copy import deepcopy
import json

from company_wiki_narrative_contracts import (
    NarrativeTransportError,
    validate_narrative_ref,
    validate_source_ref,
    validate_evidence_span_record,
    validate_summary_claim_record,
)
from contracts.evidence import canonical_sha256
from forecast.dependencies import parameter_formula_refs
from narrative_citation_context import resolve_span, citation_dependency
from narrative_summary_usage import (
    SummaryUsageError,
    MAX_REASON_CHARS,
    validate_summary_scope,
)

SCHEMA = "revenue-summary-provenance/1"
MAX_BYTES = 128 * 1024
FIELDS = {
    "schema_version",
    "narrative_ref",
    "read_receipt",
    "source_ref",
    "context_schema_version",
    "summary_claim",
    "entry",
    "evidence_spans",
    "reading_context",
    "quality_status",
    "draft_status",
    "semantic_status",
    "subfact_coverage_status",
    "excerpt_scope",
}


def _require(condition, code):
    if not condition:
        raise SummaryUsageError("summary_provenance_" + code)


def _wire(operation, *args):
    try:
        return operation(*args)
    except NarrativeTransportError as error:
        raise SummaryUsageError("summary_provenance_" + error.reason) from error


def build_summary_provenance(value, entry):
    """Copy one verified claim closure, never the whole source/bundle."""
    selected = next(
        c
        for c in value["summary"]["draft"]["claims"]
        if c["claim_id"] == entry["summary_claim_id"]
    )
    wanted = set(entry["support_evidence_ids"] + entry["context_evidence_ids"])
    reading = value.get("reading_context")
    group_id = entry["citation"]["group_id"]
    local_reading = (
        None
        if group_id is None
        else {
            "schema_version": reading["schema_version"],
            "groups": [g for g in reading["groups"] if g["group_id"] == group_id],
        }
    )
    assessment = value.get("summary_assessment") or {}
    return deepcopy(
        {
            "schema_version": SCHEMA,
            "narrative_ref": value["narrative_ref"],
            "read_receipt": value["read_receipt"],
            "source_ref": entry["source_ref"],
            "context_schema_version": value["schema_version"],
            "summary_claim": selected,
            "entry": entry,
            "evidence_spans": [
                s for s in value["evidence_spans"] if s["span_id"] in wanted
            ],
            "reading_context": local_reading,
            "quality_status": value["quality_status"],
            "draft_status": value["summary"]["draft"]["status"],
            "semantic_status": assessment.get("semantic_status"),
            "subfact_coverage_status": assessment.get("subfact_coverage_status"),
            "excerpt_scope": "source_anchor_only",
        }
    )


def validate_summary_provenance(data, claim, source, parameters):
    """Validate optional durable linkage using existing span/citation/DAG owners."""
    if "narrative_summary_use" not in claim:
        return
    proof = claim["narrative_summary_use"]
    _require(
        isinstance(proof, dict)
        and set(proof) == FIELDS
        and proof.get("schema_version") == SCHEMA,
        "schema",
    )
    _require(
        len(json.dumps(proof, ensure_ascii=False, allow_nan=False).encode())
        <= MAX_BYTES,
        "byte_bound",
    )
    ref = _wire(validate_narrative_ref, proof["narrative_ref"])
    parent = _wire(validate_source_ref, proof["source_ref"])
    _require(
        proof["context_schema_version"]
        in {
            "revenue-narrative-context/1",
            "revenue-narrative-context/2",
            "revenue-narrative-context/3",
        },
        "context_schema",
    )
    read = proof["read_receipt"]
    _require(
        isinstance(read, dict)
        and read.get("status") == "ok"
        and read.get("replay_status") == "verified"
        and read.get("narrative_ref") == ref,
        "read_binding",
    )
    if "source_ref" in ref:
        _require(ref["source_ref"] == parent, "parent")
    _require(
        parent["content_sha256"]
        == source["capture"]["snapshot_sha256"]
        == claim["content_sha256"],
        "source",
    )
    observed = source.get("company_wiki_trace", {}).get("source_ref")
    _require(observed is None or observed == parent, "source")
    _require(proof["excerpt_scope"] == "source_anchor_only", "excerpt_scope")
    spans = proof["evidence_spans"]
    _require(isinstance(spans, list) and bool(spans), "scope")
    projected = proof["context_schema_version"] == "revenue-narrative-context/3"
    _require(
        projected == (ref["schema_version"] == "narrative-ref/3"), "context_schema"
    )
    # The persisted reference has a compact subject identity, not the bundle's
    # full parent list. Validate this selected parent only, without asserting
    # anything about other parents that are outside this bounded proof.
    subject = (
        {"item_key": ref["subject_ref"]["item_key"], "parent_source_refs": [parent]}
        if projected
        else None
    )
    spans = [_wire(validate_evidence_span_record, s, subject) for s in spans]
    known = {s["span_id"]: s for s in spans}
    _require(
        len(known) == len(spans)
        and all(s["source_id"] == parent["source_id"] for s in spans),
        "scope",
    )
    summary = _wire(validate_summary_claim_record, proof["summary_claim"], spans)
    entry = proof["entry"]
    _require(
        isinstance(entry, dict)
        and entry.get("summary_claim_id") == summary["claim_id"]
        and entry.get("summary_claim_sha256") == canonical_sha256(summary),
        "summary",
    )
    _require(
        entry.get("support_evidence_ids") == summary["evidence_ids"]
        and entry.get("context_evidence_ids") == summary.get("context_evidence_ids", [])
        and set(known)
        == set(entry["support_evidence_ids"] + entry["context_evidence_ids"]),
        "scope",
    )
    _require(
        entry.get("source_ref") == parent
        and entry.get("rf_claim_id") == claim["claim_id"]
        and entry.get("parameter_id") == claim["target_id"]
        and claim["target_type"] == "parameter"
        and claim["support_type"] == "rationale_support",
        "native_binding",
    )
    _require(
        entry.get("claim_type") == summary["claim_type"]
        and entry.get("modality") == summary["modality"]
        and entry.get("needs_review") is summary["needs_review"],
        "quality",
    )
    _require(
        not summary["needs_review"]
        or proof["quality_status"] == proof["draft_status"] == "needs_review",
        "quality",
    )
    _require(
        proof["semantic_status"] in {None, "not_evaluated"}
        and proof["subfact_coverage_status"] == proof["semantic_status"],
        "quality",
    )
    reason = entry.get("research_reason")
    _require(
        isinstance(reason, str)
        and bool(reason)
        and reason == reason.strip()
        and len(reason) <= MAX_REASON_CHARS,
        "reason",
    )
    sid = entry.get("span_id")
    _require(sid in known and sid in entry["support_evidence_ids"], "anchor")
    _require(claim["excerpt"] == known[sid]["raw_text"], "anchor")
    locator = (
        known[sid]["structured_value"]["source_locator"]
        if projected
        else known[sid]["locator"]
    )
    _require(claim["locator"] == locator, "anchor")
    citation = entry.get("citation")
    _require(
        isinstance(citation, dict)
        and "group_id" in citation
        and "view_index" in citation,
        "citation",
    )
    local = {
        "schema_version": proof["context_schema_version"],
        "evidence_spans": spans,
        "reading_context": proof["reading_context"],
    }
    resolved = resolve_span(
        local, span_id=sid, group_id=citation["group_id"], view=citation["view_index"]
    )
    _require(
        citation
        == citation_dependency(
            resolution=resolved,
            claim_id=claim["claim_id"],
            parameter_id=claim["target_id"],
        ),
        "citation",
    )
    validate_summary_scope(
        resolved, entry["support_evidence_ids"], entry["context_evidence_ids"]
    )
    parameter = parameters.get(claim["target_id"])
    _require(
        parameter is not None and claim["claim_id"] in parameter.get("claim_ids", []),
        "parameter_backlink",
    )
    formula = parameter_formula_refs(data, claim["target_id"], parameters)
    _require(bool(formula) and entry.get("formula_refs") == formula, "formula")
