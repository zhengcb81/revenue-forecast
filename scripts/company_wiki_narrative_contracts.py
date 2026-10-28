"""RF-owned wire contract for CWP's bounded, source-oriented narrative export.

No CWP Python implementation is imported. Data is checked against the published
reference, receipt, bundle and EvidenceSpan formats before RF may use a snippet.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import hashlib
import json
import re
from urllib.parse import quote
from typing import Any, cast

from contracts.source_clock import (
    InformationEligibility, SourceClockError, iso_date, qualify_source_information,
    validate_availability_evidence, validate_source_events,
)

BODY_LIMIT = 1_310_720
RECEIPT_LIMIT = 16 * 1024
REQUEST_LIMIT = 16 * 1024
SOURCE_PREFIX = "urn:company-wiki:source:sha256:"
SPAN_PREFIX = "urn:company-wiki:evidence-span:sha256:"
EXPECTED_FIELDS = {"canonical_entity_id", "market", "security_id", "document_kind",
                   "fiscal_year", "fiscal_period"}
PROJECTED_REF_FIELDS = {"schema_version", "artifact_version_id", "artifact_sha256", "byte_size", "generation_sha256", "subject_ref"}
SUBJECT_REF_FIELDS = {"schema_version", "kind", "item_key", "subject_sha256"}
PROJECTION_PREFIX = "urn:company-wiki:source-projection:sha256:"
ISSUER_FIELDS = {"market", "security_id", "provider_company_id", "provider_activity_company_id", "canonical_name", "entity_name"}
PROJECTED_RECEIPT_FIELDS = {"schema_version", "status", "narrative_ref", "as_of_date", "observed_at", "locator_count", "parent_count", "lineage_sha256", "selection_status", "quality_status", "replay_status"}
REF_FIELDS = {"schema_version", "artifact_version_id", "artifact_sha256", "byte_size", "source_ref"}
SOURCE_FIELDS = {"schema_version", "document_id", "source_id", "content_sha256", "byte_size", "mime_type"}
RECEIPT_FIELDS = {"schema_version", "status", "narrative_ref", "as_of_date", "manifest",
                  "source_read_policy_sha256", "read_at", "locator_count", "selection_status",
                  "quality_status", "replay_status"}
MANIFEST_FIELDS = {"document_id", "source_id", "content_sha256", "byte_size", "mime_type",
                   "title", "document_kind", "published_date", "source_url", "retrieved_at",
                   "collector_name", "collector_version", "canonical_entity_id", "display_name",
                   "market", "security_id", "fiscal_year", "fiscal_period", "period_end",
                   "form_type", "provider", "provider_document_id", "language"}
BUNDLE_FIELDS = {"schema_version", "source_ref", "expected_read_policy_sha256",
                 "source_metadata", "quality_status", "selection", "evidence_spans",
                 "summary", "prompt_review", "transcript_lineage", "transcript_byte_bindings",
                 "versions", "replay"}
SPAN_FIELDS = {"schema_version", "span_id", "source_id", "locator", "coordinates", "raw_text",
               "structured_value", "parser_name", "parser_version", "output_sha256",
               "parse_status", "quality_flags"}
COORD_FIELDS = {"page_number", "paragraph_index", "table_index", "row_index",
                "column_index", "char_start", "char_end"}
SELECTION_FIELDS = {"status", "coverage_complete", "source_units", "candidate_count",
                    "selected_count", "omitted_candidate_count", "dropped_financial_count",
                    "pages_total", "pages_read", "lines_total", "tables_total", "tables_scanned"}
QUALITY = {"verified", "needs_review", "skipped_no_narrative"}
SELECTION = {"selected", "partial", "needs_review", "blocked", "skipped_no_narrative"}
# Native containers replay through page/paragraph locators; ET text/JSON
# separately binds extracted lines to original byte ranges.
RICH_DOCUMENT_MIMES = frozenset({
    "application/pdf", "text/html", "application/xhtml+xml",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
})
_PATH_KEYS = {"path", "root", "object_key", "absolute_path", "local_path", "raw_path",
              "root_path", "wiki_root", "catalog_path", "physical_path"}
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")


class NarrativeTransportError(RuntimeError):
    """A bounded diagnostic; never include raw text, secrets or physical paths."""

    def __init__(self, status: str, reason: str):
        self.status, self.reason = status, reason
        super().__init__(f"{status}: {reason}")


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise NarrativeTransportError("blocked", reason)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _pathless(value: Any) -> None:
    if isinstance(value, dict):
        _require(not (_PATH_KEYS & set(value)), "physical_location_forbidden")
        for child in value.values():
            _pathless(child)
    elif isinstance(value, list):
        for child in value:
            _pathless(child)


def _exact(value: Any, fields: set[str], reason: str) -> dict:
    _require(isinstance(value, dict) and set(value) == fields, reason)
    return value


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _sha(value: Any) -> bool:
    return isinstance(value, str) and _SHA.fullmatch(value) is not None


def _integer(value: Any, minimum: int = 0) -> bool:
    return type(value) is int and value >= minimum


def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        _require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def _nonfinite(_value: str) -> None:
    raise NarrativeTransportError("blocked", "nonfinite_json")


def decode_object(raw: bytes, *, limit: int, one_line: bool = False) -> dict:
    _require(isinstance(raw, bytes) and len(raw) <= limit, "wire_size_limit")
    try:
        text = raw.decode("utf-8", errors="strict")
        if one_line:
            _require(text.endswith("\n") and len(text.splitlines()) == 1, "receipt_line_count")
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_nonfinite)
        _require(isinstance(value, dict), "wire_object_required")
        _pathless(value)
        return value
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise NarrativeTransportError("blocked", "invalid_json") from exc


def _date(value: Any) -> date:
    _require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None,
             "invalid_as_of_date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise NarrativeTransportError("blocked", "invalid_as_of_date") from exc


def _utc(value: Any) -> datetime:
    _require(_text(value), "invalid_capture_time")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise NarrativeTransportError("blocked", "invalid_capture_time") from exc
    _require(parsed.tzinfo is not None and parsed.utcoffset() == timedelta(0), "invalid_capture_time")
    return parsed


def validate_source_ref(value: Any) -> dict:
    ref = _exact(value, SOURCE_FIELDS, "invalid_source_reference")
    _require(ref["schema_version"] == "2.0", "unsupported_source_reference")
    _require(all(_text(ref[key]) for key in ("document_id", "source_id", "mime_type")),
             "invalid_source_reference")
    _require(_sha(ref["content_sha256"]) and ref["source_id"] == SOURCE_PREFIX + ref["content_sha256"],
             "source_hash_binding")
    _require(_integer(ref["byte_size"], 1), "invalid_source_reference")
    return ref


def validate_subject_ref(value: Any) -> dict:
    ref = _exact(value, SUBJECT_REF_FIELDS, "invalid_subject_reference")
    _require(ref["schema_version"] == "narrative-subject-ref/1" and
             ref["kind"] == "official_json" and _sha(ref["subject_sha256"]) and
             ref["item_key"] == PROJECTION_PREFIX + ref["subject_sha256"], "subject_hash_binding")
    return ref


def validate_narrative_ref(value: Any) -> dict:
    projected = isinstance(value, dict) and value.get("schema_version") == "narrative-ref/3"
    ref = _exact(value, PROJECTED_REF_FIELDS if projected else REF_FIELDS, "invalid_narrative_reference")
    _require(ref["schema_version"] == ("narrative-ref/3" if projected else "narrative-ref/1"),
             "unsupported_narrative_reference")
    _require(isinstance(ref["artifact_version_id"], str) and
             _ID.fullmatch(ref["artifact_version_id"]) is not None, "invalid_artifact_id")
    _require(_sha(ref["artifact_sha256"]), "invalid_artifact_sha")
    _require(_integer(ref["byte_size"], 1) and ref["byte_size"] <= BODY_LIMIT, "invalid_artifact_size")
    if projected:
        validate_subject_ref(ref["subject_ref"])
        _require(_sha(ref["generation_sha256"]), "invalid_generation_sha")
    else:
        validate_source_ref(ref["source_ref"])
    _pathless(ref)
    return ref


def _constraints(value: Any) -> dict:
    fields = _exact(value, EXPECTED_FIELDS, "invalid_source_constraints")
    for key, constraint in fields.items():
        if constraint is None:
            continue
        if key == "fiscal_year":
            _require(_integer(constraint, 1900) and constraint <= 9999, "invalid_fiscal_year")
        else:
            _require(_text(constraint) and len(constraint) <= 256, "invalid_source_constraint")
    return fields


def _issuer_constraint(key: str, value: Any) -> None:
    if key in {"provider_company_id", "provider_activity_company_id"} and type(value) is int:
        return
    _require(_text(value) and len(value) <= 256, "invalid_issuer_constraint")


def _issuer_constraints(value: Any) -> dict | None:
    if value is None:
        return None
    _require(isinstance(value, dict) and bool(value) and set(value) <= ISSUER_FIELDS,
             "invalid_issuer_constraints")
    for key, constraint in value.items():
        _issuer_constraint(key, constraint)
    return value


def validate_narrative_request(value: Any) -> dict:
    projected = isinstance(value, dict) and value.get("schema_version") == "narrative-read-request/3"
    constraint_key = "expected_issuer" if projected else "expected_source"
    request = _exact(value, {"schema_version", "narrative_ref", "as_of_date", constraint_key},
                     "invalid_read_request")
    _require(request["schema_version"] == ("narrative-read-request/3" if projected else "narrative-read-request/1"),
             "unsupported_read_request")
    ref = validate_narrative_ref(request["narrative_ref"])
    _require(ref["schema_version"] == ("narrative-ref/3" if projected else "narrative-ref/1"), "request_reference_kind_mismatch")
    if request["as_of_date"] is not None:
        _date(request["as_of_date"])
    (_issuer_constraints if projected else _constraints)(request[constraint_key])
    _pathless(request)
    _require(len(canonical_bytes(request)) + 1 <= REQUEST_LIMIT, "request_size_limit")
    return deepcopy(request)


def validate_reference_request(value: Any) -> dict:
    projected = isinstance(value, dict) and value.get("schema_version") == "narrative-reference-request/3"
    fields = {"schema_version", "subject_ref", "generation_sha256"} if projected else {"schema_version", "source_ref"}
    request = _exact(value, fields, "invalid_reference_request")
    _require(request["schema_version"] == ("narrative-reference-request/3" if projected else "narrative-reference-request/1"),
             "unsupported_reference_request")
    if projected:
        validate_subject_ref(request["subject_ref"])
        _require(_sha(request["generation_sha256"]), "invalid_generation_sha")
    else:
        validate_source_ref(request["source_ref"])
    _pathless(request)
    _require(len(canonical_bytes(request)) + 1 <= REQUEST_LIMIT, "request_size_limit")
    return deepcopy(request)


def _manifest_information_time(manifest: dict, receipt: dict, as_of: str | None) -> None:
    """Reuse source-clock qualification after the existing ref/manifest binding."""
    published = manifest["published_date"]
    if published is not None:
        _date(published)  # Empty or malformed publication is not an unknown date.
    proof = receipt.get("availability_evidence")
    try:
        if as_of is None:
            checked = validate_availability_evidence(proof, manifest["content_sha256"])
            if checked is None:
                return  # Current metadata reading makes no historical claim.
            eligibility = InformationEligibility(
                available_by=iso_date(checked["available_by"], "availability_evidence.available_by"),
                basis=checked["basis"], source_sha256=manifest["content_sha256"],
                published_date=None,
            )
        else:
            eligibility = qualify_source_information(
                source_sha256=manifest["content_sha256"], published_date=published,
                as_of=_date(as_of), availability_evidence=proof,
            )
        validate_source_events(
            eligibility=eligibility, current_read_at=receipt["read_at"],
            original_retrieved_at=manifest["retrieved_at"],
        )
    except SourceClockError as exc:
        reason = str(exc).partition(":")[0]
        # Preserve the two existing narrative refusal codes for legacy callers.
        reason = {"source_publication_after_asof": "source_after_as_of",
                  "source_availability_unknown": "source_publication_unknown"}.get(reason, reason)
        raise NarrativeTransportError("blocked", reason) from exc


def _manifest(receipt: dict, request: dict) -> dict:
    manifest = _exact(receipt["manifest"], MANIFEST_FIELDS, "invalid_source_manifest")
    source = request["narrative_ref"]["source_ref"]
    for key in SOURCE_FIELDS - {"schema_version"}:
        _require(type(manifest[key]) is type(source[key]) and manifest[key] == source[key],
                 "manifest_source_mismatch")
    for key, value in request["expected_source"].items():
        if value is not None:
            _require(type(manifest[key]) is type(value) and manifest[key] == value, "manifest_request_mismatch")
    _manifest_information_time(manifest, receipt, request["as_of_date"])
    if manifest["retrieved_at"] is not None:
        _utc(manifest["retrieved_at"])  # Unknown collection time stays unknown.
    return manifest


def _receipt(receipt: dict, request: dict) -> dict:
    optional = {"availability_evidence"} if "availability_evidence" in receipt else set()
    _exact(receipt, RECEIPT_FIELDS | optional, "invalid_read_receipt")
    _require(receipt["schema_version"] == "narrative-read-receipt/1", "unsupported_read_receipt")
    _require(receipt["status"] == "ok" and receipt["replay_status"] == "verified", "unverified_read_receipt")
    validate_narrative_ref(receipt["narrative_ref"])
    _require(receipt["narrative_ref"] == request["narrative_ref"] and
             receipt["as_of_date"] == request["as_of_date"], "receipt_request_mismatch")
    _require(_sha(receipt["source_read_policy_sha256"]), "invalid_read_policy")
    _utc(receipt["read_at"])
    _require(_integer(receipt["locator_count"]), "invalid_locator_count")
    return _manifest(receipt, request)


def _coordinate_shape(value: Any) -> dict:
    coordinates = _exact(value, COORD_FIELDS, "invalid_coordinates")
    for key, number in coordinates.items():
        _require(number is None or _integer(number, 1 if key == "page_number" else 0), "invalid_coordinates")
    _require(any(value is not None for value in coordinates.values()), "invalid_coordinates")
    start, end = coordinates["char_start"], coordinates["char_end"]
    _require((start is None) == (end is None), "invalid_coordinates")
    if start is not None:
        _require(end > start, "invalid_coordinates")
    _coordinate_relations(coordinates)
    return coordinates


def _coordinate_relations(coordinates: dict) -> None:
    _require(not (coordinates["paragraph_index"] is not None and coordinates["table_index"] is not None),
             "invalid_coordinates")
    _require(coordinates["table_index"] is not None or (
        coordinates["row_index"] is None and coordinates["column_index"] is None), "invalid_coordinates")


def _coordinates(value: Any) -> str:
    coordinates = _coordinate_shape(value)
    parts = ["loc:v1"]
    for label, key in (("page", "page_number"), ("paragraph", "paragraph_index"),
                       ("table", "table_index"), ("row", "row_index"), ("column", "column_index")):
        if coordinates[key] is not None:
            parts.append(f"{label}:{coordinates[key]}")
    if coordinates["char_start"] is not None:
        parts.append(f"chars:{coordinates['char_start']}-{coordinates['char_end']}")
    return "/".join(parts)


def _span_core(value: Any) -> dict:
    span = _exact(value, SPAN_FIELDS, "invalid_evidence_span")
    _require(span["schema_version"] == "1.0.0", "unsupported_evidence_span")
    locator = _coordinates(span["coordinates"])
    _require(span["locator"] == locator, "span_locator_mismatch")
    _require(span["raw_text"] is None or isinstance(span["raw_text"], str), "invalid_span_text")
    output_sha = hashlib.sha256(canonical_bytes({
        "raw_text": span["raw_text"], "structured_value": span["structured_value"],
    })).hexdigest()
    _require(span["output_sha256"] == output_sha, "span_output_hash_mismatch")
    span_sha = hashlib.sha256(canonical_bytes({
        "source_id": span["source_id"], "locator": locator, "output_sha256": output_sha,
    })).hexdigest()
    _require(span["span_id"] == SPAN_PREFIX + span_sha, "span_identity_mismatch")
    _span_quality(span)
    return span


def _span(value: Any, source: dict) -> dict:
    span = _span_core(value)
    _require(span["source_id"] == source["source_id"], "span_source_mismatch")
    return span


def _span_quality(span: dict) -> None:
    flags = span["quality_flags"]
    _require(isinstance(flags, list) and all(_text(flag) for flag in flags)
             and len(flags) == len(set(flags)), "invalid_span_quality")
    _require(span["parse_status"] in {"parsed", "partial", "failed", "quarantined"}, "invalid_span_quality")
    _require(_text(span["parser_name"]) and _text(span["parser_version"]), "invalid_span_parser")
    if span["parse_status"] == "partial":
        _require(bool(flags), "invalid_span_quality")


def _selection(value: Any, span_count: int) -> dict:
    selected = _exact(value, SELECTION_FIELDS, "invalid_selection")
    _require(selected["status"] in SELECTION and type(selected["coverage_complete"]) is bool,
             "invalid_selection")
    _require(all(_integer(selected[key]) for key in SELECTION_FIELDS - {"status", "coverage_complete"}),
             "invalid_selection_count")
    _require(selected["selected_count"] == span_count, "selection_count_mismatch")
    _require(selected["pages_read"] <= selected["pages_total"] and
             selected["tables_scanned"] <= selected["tables_total"], "invalid_selection_coverage")
    return selected


def _claim(value: Any, spans: dict[str, dict]) -> dict:
    extra = {"context_evidence_ids"} if isinstance(value, dict) and "context_evidence_ids" in value else set()
    claim = _exact(value, {"claim_id", "text", "evidence_ids", "claim_type", "modality", "needs_review"} | extra,
                   "invalid_summary_claim")
    _require(_text(claim["claim_id"]) and _text(claim["text"]), "invalid_summary_claim")
    ids = claim["evidence_ids"]
    _require(isinstance(ids, list) and bool(ids) and all(isinstance(key, str) and key in spans for key in ids)
             and len(ids) == len(set(ids)), "unbound_summary_citation")
    _require(type(claim["needs_review"]) is bool, "invalid_summary_claim")
    _require(claim["claim_type"] in {"company_statement", "analyst_question", "editorial", "uncertain"},
             "invalid_claim_type")
    _require(claim["modality"] in {"actual", "planned", "forecast", "question", "negation", "uncertain"},
             "invalid_claim_modality")
    context = claim.get("context_evidence_ids", [])
    _require(isinstance(context, list) and all(isinstance(key, str) and key in spans for key in context)
             and len(context) == len(set(context)) and not set(context).intersection(ids),
             "unbound_summary_context")
    support_sources = {spans[key]["source_id"] for key in ids}
    _require(all(spans[key]["source_id"] in support_sources for key in context),
             "summary_context_parent_mismatch")
    _claim_roles(claim, spans)
    return claim


def _claim_roles(claim: dict, spans: dict[str, dict]) -> None:
    roles = {spans[key]["structured_value"].get("source_role")
             for key in claim["evidence_ids"] if isinstance(spans[key]["structured_value"], dict)}
    if claim["claim_type"] == "analyst_question":
        _require(bool(roles) and roles <= {"analyst", "investor_question"} and claim["modality"] == "question",
                 "claim_role_mismatch")
    elif claim["claim_type"] == "company_statement":
        _require(bool(roles) and roles <= {"company_filing", "management"}, "claim_role_mismatch")


def _summary(value: Any, source: dict, spans: dict[str, dict], language: str, skipped: bool) -> dict:
    summary = _exact(value, {"status", "translate", "draft", "model"}, "invalid_summary")
    _require(summary["translate"] is False, "translated_summary_forbidden")
    if skipped:
        _require(summary["status"] == "summary_not_needed" and
                 summary["draft"] is None and summary["model"] is None, "invalid_skip_summary")
        return summary
    _require(summary["status"] == "completed", "invalid_summary_status")
    _summary_draft(summary["draft"], source, spans, language)
    _summary_model(summary["model"])
    return summary


def _summary_draft(value: Any, source: dict, spans: dict[str, dict], language: str) -> None:
    draft = _exact(value, {"source_id", "source_sha256", "language", "claims", "status"},
                   "invalid_summary_draft")
    _require(draft["source_id"] == source["source_id"] and draft["source_sha256"] == source["content_sha256"]
             and draft["language"] == language, "summary_source_mismatch")
    _require(draft["status"] in {"draft", "needs_review"}, "invalid_summary_status")
    _require(isinstance(draft["claims"], list) and bool(draft["claims"]), "invalid_summary_claims")
    claims = [_claim(claim, spans) for claim in draft["claims"]]
    _require(len({claim["claim_id"] for claim in claims}) == len(claims), "duplicate_summary_claim")


def _summary_model(value: Any) -> None:
    model = _exact(value, {"adapter_id", "model_id", "prompt_version", "response_sha256"},
                   "invalid_summary_model")
    _require(_sha(model["response_sha256"]), "invalid_summary_model")
    _require(all(_text(model[key]) for key in ("adapter_id", "model_id", "prompt_version")),
             "invalid_summary_model")


def _lineage(bundle: dict, source: dict, span_ids: set[str]) -> None:
    lineage = bundle["transcript_lineage"]
    bindings = bundle["transcript_byte_bindings"]
    _require(isinstance(bindings, list), "invalid_transcript_bindings")
    if lineage is None:
        _require(not bindings and source["mime_type"] in RICH_DOCUMENT_MIMES,
                 "missing_transcript_lineage")
        return
    _lineage_source(lineage, source)
    _require({binding.get("evidence_id") for binding in bindings if isinstance(binding, dict)} == span_ids
             and len(bindings) == len(span_ids), "incomplete_transcript_bindings")
    for binding in bindings:
        _byte_binding(binding, lineage, source)


def _lineage_source(lineage: Any, source: dict) -> None:
    lineage_fields = {"schema_version", "original_source_id", "original_sha256", "original_byte_size",
                      "original_mime_type", "text_sha256", "text_byte_size", "line_count", "extractor_version"}
    _exact(lineage, lineage_fields, "invalid_transcript_lineage")
    _require(lineage["schema_version"] == "transcript-material/2", "unsupported_transcript_lineage")
    for key, source_key in (("original_source_id", "source_id"), ("original_sha256", "content_sha256"),
                            ("original_byte_size", "byte_size"), ("original_mime_type", "mime_type")):
        _require(type(lineage[key]) is type(source[source_key]) and lineage[key] == source[source_key],
                 "lineage_source_mismatch")
    _require(_sha(lineage["text_sha256"]) and _integer(lineage["text_byte_size"]) and
             _integer(lineage["line_count"]), "invalid_transcript_lineage")


def _byte_binding(binding: Any, lineage: dict, source: dict) -> None:
    _exact(binding, {"evidence_id", "material_line_start", "material_line_end", "source_byte_ranges"},
           "invalid_transcript_binding")
    start, end = binding["material_line_start"], binding["material_line_end"]
    _require(_integer(start, 1) and _integer(end, start) and end <= lineage["line_count"],
             "invalid_transcript_binding")
    ranges = binding["source_byte_ranges"]
    _require(isinstance(ranges, list) and bool(ranges), "invalid_transcript_binding")
    for part in ranges:
        _exact(part, {"start", "end"}, "invalid_transcript_binding")
        _require(_integer(part["start"]) and _integer(part["end"], part["start"] + 1)
                 and part["end"] <= source["byte_size"], "invalid_transcript_binding")


def _diagnostics(bundle: dict, source_sha256: str | None = None) -> None:
    review = _exact(bundle["prompt_review"], {"status", "source_sha256", "evidence_sha256", "policy_hash",
                                            "reviewed_at"}, "invalid_prompt_diagnostic")
    _require(review["status"] in {"not_detected", "detected_and_ignored", "not_reviewed"},
             "invalid_prompt_diagnostic")
    if review["source_sha256"] is not None:
        _require(review["source_sha256"] == (source_sha256 or bundle["source_ref"]["content_sha256"]), "prompt_source_mismatch")
    versions = _exact(bundle["versions"], {"parser", "selector", "material", "model", "prompt",
                                         "bundle_producer"}, "invalid_bundle_versions")
    _require(all(_text(versions[key]) for key in ("parser", "selector", "bundle_producer")),
             "invalid_bundle_versions")



READING_CONTEXT_LIMIT = 192 * 1024
_READING_FIELDS = {"schema_version", "reading_policy_version", "reading_policies", "business_facets",
                   "constraints", "groups", "unread", "deferred", "layout_coverage"}
_READING_SAMPLING_FIELDS = {"deferred_count", "deferred_limited", "selection_diagnostics"}
_READING_POLICY_FIELDS = {"profile_id", "profile_version", "family", "summary_focus", "policy_components",
    "reading_questions", "context_requirements", "family_policy", "negative_hints", "semantic_units", "section_priorities"}
_READING_FACET_FIELDS = {"id", "version", "content_digest", "selection_basis", "business_questions", "summary_focus",
                       "required_context", "absence_rules", "confusion_checks", "applicable_mechanisms"}
_READING_FORBIDDEN = _PATH_KEYS | {"raw_text", "body", "observation", "evidence_packages", "members",
    "wrong_assertion", "correct_assertion", "source_meaning", "confusions", "examples", "example"}


def _reading_json(value: Any) -> None:
    """Bound policy data before recursive projection; never interpret it as code.

    These are the producer's published finite-wire ceilings. Arbitrary policy
    content stays data; no source IO, policy lookup or original-byte verification
    is repeated by this consumer.
    """
    stack = [(value, 0)]
    visited = 0
    while stack:
        item, depth = stack.pop()
        visited += 1
        _require(visited <= 30000 and depth <= 12, "reading_structure_limit")
        if item is None or type(item) in {bool, int, float}:
            continue  # The existing JSON decoder already rejects nonfinite numbers.
        if isinstance(item, str):
            _require(len(item) <= 16384, "reading_string_limit")
        elif isinstance(item, dict):
            _require(len(item) <= 256, "reading_object_limit")
            _require(all(isinstance(key, str) and len(key) <= 128 for key in item), "invalid_reading_key")
            _require(not (_READING_FORBIDDEN & set(item)), "reading_payload_forbidden")
            stack.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            _require(len(item) <= 4096, "reading_array_limit")
            stack.extend((child, depth + 1) for child in item)
        else:
            raise NarrativeTransportError("blocked", "invalid_reading_json")


def _reading_rows(value: Any, *, limit: int = 4096) -> list:
    _require(isinstance(value, list), "invalid_reading_array")
    _require(len(value) <= limit, "reading_array_limit")
    return value


def _reading_texts(value: Any, *, limit: int = 4096) -> list:
    values = _reading_rows(value, limit=limit)
    _require(all(_text(entry) for entry in values), "invalid_reading_text")
    return values


def _reading_sample(value: dict, lists: set[str], count_key: str, limited_key: str) -> None:
    counts = _exact(value[count_key], lists, "invalid_reading_counts")
    _require(all(_integer(counts[key], len(value[key])) for key in lists), "invalid_reading_counts")
    _require(type(value[limited_key]) is bool and value[limited_key] == any(
        counts[key] > len(value[key]) for key in lists), "invalid_reading_limited")



_TRACE_CODE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,79}\Z")
_NARRATIVE_UNIT_ID = re.compile(r"urn:company-wiki:narrative-unit:sha256:[0-9a-f]{64}\Z")
_READING_PACKAGE_ID = re.compile(r"urn:company-wiki:reading-package:sha256:[0-9a-f]{64}\Z")
_READING_GROUP_ID = re.compile(r"urn:company-wiki:reading-group:sha256:[0-9a-f]{64}\Z")
_EVIDENCE_SPAN_ID = re.compile(r"urn:company-wiki:evidence-span:sha256:[0-9a-f]{64}\Z")
_READING_LOCATOR = re.compile(r"loc:v1(?:/(?:page|paragraph|table|row|column):[0-9]+)*(?:/chars:[0-9]+-[0-9]+)?\Z")
_DOCUMENT_WORK_DETAIL = "unexamined source content remains unknown; original is unchanged"


def _trace_code(value: Any) -> bool:
    return isinstance(value, str) and _TRACE_CODE.fullmatch(value) is not None


def _trace_section(value: Any, *, cap: int) -> tuple[int, list[dict]]:
    section = _exact(value, {"count", "limited", "samples"}, "invalid_selection_trace_section")
    samples = _reading_rows(section["samples"], limit=cap)
    _require(all(isinstance(row, dict) for row in samples)
             and _integer(section["count"], len(samples))
             and type(section["limited"]) is bool
             and section["limited"] == (section["count"] > len(samples)),
             "invalid_selection_trace_counts")
    return section["count"], samples


def _trace_id_list(value: Any, *, cap: int, pattern: re.Pattern) -> list[str]:
    rows = _reading_texts(value, limit=cap)
    _require(all(pattern.fullmatch(row) is not None for row in rows), "invalid_selection_trace_ids")
    return rows


def _trace_sample_count(row: dict, ids_key: str, count_key: str, limited_key: str,
                        *, cap: int) -> None:
    ids = _trace_id_list(row[ids_key], cap=cap, pattern=_NARRATIVE_UNIT_ID)
    count = row[count_key]
    _require(_integer(count, len(ids)) and type(row[limited_key]) is bool
             and row[limited_key] == (count > len(ids)), "invalid_selection_trace_ids")


def _selection_trace(value: Any, spans: dict[str, dict]) -> None:
    trace = _exact(value, {"schema_version", "source_unit_count", "admission",
                           "eligible_packages", "withheld", "selected"},
                   "invalid_selection_trace")
    _require(trace["schema_version"] == "selection-trace/1"
             and _integer(trace["source_unit_count"]), "invalid_selection_trace")
    admission = _exact(trace["admission"], {
        "count", "admitted_count", "rejected_count", "limited", "rejection_counts", "samples",
    }, "invalid_selection_trace_admission")
    admission_count, samples = _trace_section({
        "count": admission["count"], "limited": admission["limited"], "samples": admission["samples"],
    }, cap=16)
    admitted, rejected, rejection_counts = (
        admission["admitted_count"], admission["rejected_count"], admission["rejection_counts"]
    )
    _require(_integer(admitted) and _integer(rejected) and admitted + rejected == admission_count
             and isinstance(rejection_counts, dict) and len(rejection_counts) <= 32
             and all(_trace_code(code) and _integer(count, 1)
                     for code, count in rejection_counts.items())
             and sum(rejection_counts.values()) == rejected,
             "invalid_selection_trace_admission")
    sampled_admitted = sampled_rejected = 0
    for row in samples:
        _exact(row, {"unit_id", "package_ref", "status", "reason", "fact_purpose",
                     "fact_reasons", "fact_reason_count", "fact_reasons_limited",
                     "required_unit_ids", "required_unit_count", "required_unit_ids_limited",
                     "priority", "selected_span_id"}, "invalid_selection_trace_admission_sample")
        _require(_NARRATIVE_UNIT_ID.fullmatch(row["unit_id"]) is not None
                 and _READING_PACKAGE_ID.fullmatch(row["package_ref"]) is not None
                 and row["status"] in {"admitted", "not_admitted"}
                 and _trace_code(row["fact_purpose"]), "invalid_selection_trace_admission_sample")
        if row["status"] == "admitted":
            sampled_admitted += 1
            _require(row["reason"] is None, "invalid_selection_trace_admission_sample")
        else:
            sampled_rejected += 1
            _require(_trace_code(row["reason"]), "invalid_selection_trace_admission_sample")
        fact_reasons = _trace_id_list(row["fact_reasons"], cap=4, pattern=_TRACE_CODE)
        _require(_integer(row["fact_reason_count"], len(fact_reasons))
                 and type(row["fact_reasons_limited"]) is bool
                 and row["fact_reasons_limited"] == (row["fact_reason_count"] > len(fact_reasons)),
                 "invalid_selection_trace_admission_sample")
        _trace_sample_count(row, "required_unit_ids", "required_unit_count",
                            "required_unit_ids_limited", cap=8)
        _require(_integer(row["priority"], 1), "invalid_selection_trace_admission_sample")
        selected = row["selected_span_id"]
        _require(selected is None or (isinstance(selected, str)
                 and _EVIDENCE_SPAN_ID.fullmatch(selected) is not None and selected in spans),
                 "invalid_selection_trace_admission_sample")
    _require(sampled_admitted <= admitted and sampled_rejected <= rejected,
             "invalid_selection_trace_admission")

    package_count, packages = _trace_section(trace["eligible_packages"], cap=16)
    for row in packages:
        _exact(row, {"package_ref", "kind", "member_unit_ids", "member_count", "member_limited",
                     "anchor_unit_ids", "anchor_count", "anchor_limited", "required_unit_ids",
                     "required_count", "required_limited"}, "invalid_selection_trace_package")
        _require(_READING_PACKAGE_ID.fullmatch(row["package_ref"]) is not None
                 and _trace_code(row["kind"]), "invalid_selection_trace_package")
        for ids_key, count_key, limited_key in (
            ("member_unit_ids", "member_count", "member_limited"),
            ("anchor_unit_ids", "anchor_count", "anchor_limited"),
            ("required_unit_ids", "required_count", "required_limited"),
        ):
            _trace_sample_count(row, ids_key, count_key, limited_key, cap=8)
    _require(package_count >= len(packages), "invalid_selection_trace_package")

    withheld_count, withheld = _trace_section(trace["withheld"], cap=32)
    for row in withheld:
        _exact(row, {"package_ref", "reason", "status", "known_unit_ids",
                     "known_unit_count", "known_unit_ids_limited"}, "invalid_selection_trace_withheld")
        _require(_READING_PACKAGE_ID.fullmatch(row["package_ref"]) is not None
                 and _trace_code(row["reason"])
                 and (row["status"] is None or _trace_code(row["status"])),
                 "invalid_selection_trace_withheld")
        _trace_sample_count(row, "known_unit_ids", "known_unit_count",
                            "known_unit_ids_limited", cap=8)
    _require(withheld_count >= len(withheld), "invalid_selection_trace_withheld")

    selected_count, selected = _trace_section(trace["selected"], cap=32)
    _require(len(spans) <= selected_count <= trace["source_unit_count"]
             and (bool(spans) or selected_count == 0), "invalid_selection_trace_selected")
    seen_units: set[str] = set()
    for row in selected:
        _exact(row, {"unit_id", "span_id"}, "invalid_selection_trace_selected")
        unit_id, span_id = row["unit_id"], row["span_id"]
        _require(isinstance(unit_id, str) and _NARRATIVE_UNIT_ID.fullmatch(unit_id) is not None
                 and isinstance(span_id, str) and _EVIDENCE_SPAN_ID.fullmatch(span_id) is not None
                 and span_id in spans and unit_id not in seen_units,
                 "invalid_selection_trace_selected")
        seen_units.add(unit_id)
    _require(selected_count >= len(selected), "invalid_selection_trace_selected")


def _reading_proofs(group: dict, schema: str) -> set[str]:
    fields = {"source_proof_unit_ids", "source_proof_target_unit_ids", "source_proofs"}
    present = fields & group.keys()
    _require(not present or (schema in {"du-production-reading/2", "du-production-reading/3", "du-production-reading/4"}
                             and present == fields), "invalid_reading_group_proof_fields")
    if not present:
        return set()
    proof_ids = _trace_id_list(group["source_proof_unit_ids"], cap=128, pattern=_NARRATIVE_UNIT_ID)
    targets = _trace_id_list(group["source_proof_target_unit_ids"], cap=256, pattern=_NARRATIVE_UNIT_ID)
    _require(bool(proof_ids) and len(proof_ids) == len(set(proof_ids))
             and len(targets) == len(set(targets)), "invalid_reading_group_proof_ids")
    closure = set(proof_ids) | set(targets)
    proofs = _reading_rows(group["source_proofs"], limit=128)
    _require(bool(proofs), "invalid_reading_group_proofs")
    edges: set[tuple[str, str]] = set()
    for raw in proofs:
        proof = _exact(raw, {"basis", "left", "right", "left_page", "right_page",
                             "left_ordinal", "right_ordinal", "column", "coordinate_frame",
                             "furniture_unit_ids"}, "invalid_reading_group_proof")
        left, right = proof["left"], proof["right"]
        _require(proof["basis"] == "observed_adjacent_page_flow"
                 and isinstance(left, str) and _NARRATIVE_UNIT_ID.fullmatch(left) is not None
                 and isinstance(right, str) and _NARRATIVE_UNIT_ID.fullmatch(right) is not None
                 and left != right and {left, right} <= closure,
                 "invalid_reading_group_proof_endpoints")
        _require((left, right) not in edges, "duplicate_reading_group_proof")
        edges.add((left, right))
        _require(_integer(proof["left_page"], 1) and _integer(proof["right_page"], 1)
                 and proof["right_page"] == proof["left_page"] + 1
                 and _integer(proof["left_ordinal"]) and _integer(proof["right_ordinal"])
                 and proof["right_ordinal"] > proof["left_ordinal"],
                 "invalid_reading_group_proof_coordinates")
        column, frame = proof["column"], proof["coordinate_frame"]
        _require((type(column) is int or (_text(column) and len(column) <= 256))
                 and _text(frame) and len(frame) <= 256,
                 "invalid_reading_group_proof_coordinates")
        furniture = _trace_id_list(proof["furniture_unit_ids"], cap=24, pattern=_NARRATIVE_UNIT_ID)
        _require(len(furniture) == len(set(furniture)) and set(furniture) <= closure,
                 "invalid_reading_group_proof_furniture")
    return fields


def _diagnostic_target(value: Any, code: str) -> dict:
    item = _exact(value, {"item_id", "item_ids", "item_count", "item_ids_limited",
                          "group_id", "locator", "used", "requested", "limit", "closure_size"},
                  "invalid_reading_diagnostic_target")
    _require(isinstance(item["item_id"], str)
             and _NARRATIVE_UNIT_ID.fullmatch(item["item_id"]) is not None,
             "invalid_reading_diagnostic_target")
    ids = _trace_id_list(item["item_ids"], cap=16, pattern=_NARRATIVE_UNIT_ID)
    _require(_integer(item["item_count"], 1) and item["item_count"] >= len(ids)
             and type(item["item_ids_limited"]) is bool
             and item["item_ids_limited"] == (item["item_count"] > len(ids)),
             "invalid_reading_diagnostic_target")
    group_id = item["group_id"]
    _require(group_id is None or (isinstance(group_id, str)
             and _READING_GROUP_ID.fullmatch(group_id) is not None),
             "invalid_reading_diagnostic_target")
    _require(isinstance(item["locator"], str) and _READING_LOCATOR.fullmatch(item["locator"]) is not None
             and len(item["locator"]) <= 512, "invalid_reading_diagnostic_target")
    used, requested, limit, closure = (item[k] for k in ("used", "requested", "limit", "closure_size"))
    _require(_integer(used) and _integer(requested, 1)
             and _integer(limit, 0 if code == "character_budget" else 1)
             and _integer(closure, 1) and used <= limit and used + requested > limit,
             "invalid_reading_diagnostic_target")
    if code == "group_exceeds_limit":
        _require(closure > limit, "invalid_reading_diagnostic_target")
    return item


def _selection_diagnostic(value: Any, *, legacy_aggregate: bool) -> None:
    required = {"code", "count"}
    _require(isinstance(value, dict), "invalid_reading_diagnostic")
    if legacy_aggregate and value.keys() == required:
        _require(_trace_code(value["code"]) and _integer(value["count"], 1),
                 "invalid_reading_diagnostic")
        return
    allowed = required | {"phase", "external_model_cost", "dimension", "used", "requested",
                          "limit", "detail", "targets", "targets_limited", "max_closure_size"}
    _require(required <= value.keys() <= allowed and _trace_code(value["code"])
             and _integer(value["count"], 1), "invalid_reading_diagnostic")
    code = value["code"]
    if value.keys() == required:
        _require(code == "DECISION_DEPENDENCIES_UNAVAILABLE",
                 "invalid_reading_diagnostic")
        return
    phase, cost, dimension = value.get("phase"), value.get("external_model_cost"), value.get("dimension")
    dimensions = {"budget_full": {"selection_spans"},
                  "group_exceeds_limit": {"selection_spans"},
                  "character_budget": {"selection_characters"},
                  "work_budget_exhausted": {"selection_work", "document_work"},
                  "missing_required_context": {"selection_policy"}}
    _require(_text(phase) and len(phase) <= 80 and cost is False and _text(dimension)
             and len(dimension) <= 80 and dimension in dimensions.get(code, set()),
             "invalid_reading_diagnostic")
    if code in {"budget_full", "character_budget"}:
        base = required | {"phase", "external_model_cost", "dimension", "used", "limit"}
        enriched = base | {"targets", "targets_limited"}
        _require(value.keys() in (base, enriched), "invalid_reading_diagnostic")
        low = 0 if code == "character_budget" else 1
        _require(_integer(value["used"]) and _integer(value["limit"], low)
                 and value["used"] <= value["limit"], "invalid_reading_diagnostic")
        if value.keys() == enriched:
            targets = _reading_rows(value["targets"], limit=32)
            _require(type(value["targets_limited"]) is bool and len(targets) <= value["count"]
                     and value["targets_limited"] == (value["count"] > len(targets)),
                     "invalid_reading_diagnostic")
            _require(all(_diagnostic_target(target, code)["limit"] == value["limit"]
                         for target in targets), "invalid_reading_diagnostic")
    elif dimension == "document_work":
        fields = required | {"phase", "external_model_cost", "dimension",
                             "used", "requested", "limit", "detail"}
        _require(value.keys() == fields and _integer(value["used"])
                 and _integer(value["limit"]) and value["used"] <= value["limit"]
                 and (value["requested"] is None or _integer(value["requested"]))
                 and value["detail"] == _DOCUMENT_WORK_DETAIL,
                 "invalid_reading_diagnostic")
    elif code == "group_exceeds_limit":
        base = required | {"phase", "external_model_cost", "dimension"}
        enriched = base | {"limit", "max_closure_size", "targets", "targets_limited"}
        _require(value.keys() in (base, enriched), "invalid_reading_diagnostic")
        if value.keys() == enriched:
            limit, maximum = value["limit"], value["max_closure_size"]
            targets = _reading_rows(value["targets"], limit=32)
            _require(_integer(limit, 1) and _integer(maximum, 1) and maximum > limit
                     and type(value["targets_limited"]) is bool and len(targets) <= value["count"]
                     and value["targets_limited"] == (value["count"] > len(targets)),
                     "invalid_reading_diagnostic")
            _require(all((target := _diagnostic_target(row, code))["limit"] == limit
                         and target["closure_size"] <= maximum for row in targets),
                     "invalid_reading_diagnostic")
    else:
        _require(value.keys() == required | {"phase", "external_model_cost", "dimension"},
                 "invalid_reading_diagnostic")


def _reading_context(value: Any, spans: dict[str, dict]) -> None:
    """Validate finite reading-context versions against transported spans."""
    if value is None:
        return
    _reading_json(value)
    _require(len(canonical_bytes(value)) <= READING_CONTEXT_LIMIT, "reading_bytes_limit")
    schema_value = value.get("schema_version") if isinstance(value, dict) else None
    _require(isinstance(schema_value, str) and schema_value in {
        "du-production-reading/1", "du-production-reading/2", "du-production-reading/3", "du-production-reading/4",
    }, "unsupported_reading_context")
    schema = cast(str, schema_value)
    present_sampling = _READING_SAMPLING_FIELDS & value.keys()
    if present_sampling:
        _require(present_sampling == _READING_SAMPLING_FIELDS, "invalid_reading_context")
    if schema in {"du-production-reading/3", "du-production-reading/4"}:
        _require(present_sampling == _READING_SAMPLING_FIELDS and "selection_trace" in value,
                 "invalid_reading_context")
        extra = _READING_SAMPLING_FIELDS | {"selection_trace"}
    else:
        _require("selection_trace" not in value, "invalid_reading_context")
        extra = _READING_SAMPLING_FIELDS if present_sampling else set()
    context = _exact(value, _READING_FIELDS | extra, "invalid_reading_context")
    attributed = schema in {"du-production-reading/2", "du-production-reading/3", "du-production-reading/4"}
    version = context["reading_policy_version"]
    prefix = "du-sent-policy/1+"
    _require(isinstance(version, str) and version.startswith(prefix)
             and _sha(version[len(prefix):]), "invalid_reading_policy_version")
    for policy in _reading_rows(context["reading_policies"], limit=128):
        _exact(policy, _READING_POLICY_FIELDS, "invalid_reading_policy")
        for component in _reading_rows([] if policy["policy_components"] is None else policy["policy_components"]):
            _exact(component, {"kind", "id", "version", "content_digest"}, "invalid_reading_component")
            _require(_sha(component["content_digest"]), "invalid_reading_component_digest")
    for facet in _reading_rows(context["business_facets"], limit=16):
        _exact(facet, _READING_FACET_FIELDS, "invalid_reading_facet")
        _require(_sha(facet["content_digest"]), "invalid_reading_facet_digest")
        for check in _reading_rows([] if facet["confusion_checks"] is None else facet["confusion_checks"]):
            _exact(check, {"risk", "required_context_slots"}, "invalid_reading_confusion_check")
            _require(_text(check["risk"]), "invalid_reading_confusion_check")
            _reading_texts(check["required_context_slots"])
    _reading_texts(context["constraints"], limit=32)
    group_ids: set[str] = set()
    for group in _reading_rows(context["groups"], limit=512):
        _require(isinstance(group, dict), "invalid_reading_group")
        proof_extra = _reading_proofs(group, schema)
        _exact(group, {"group_id", "kind", "section_role", "evidence_ids"}
               | ({"citation_views"} if attributed else set()) | proof_extra,
               "invalid_reading_group")
        _require(all(_text(group[key]) for key in ("group_id", "kind", "section_role")),
                 "invalid_reading_group")
        _require(group["group_id"] not in group_ids, "duplicate_reading_group")
        group_ids.add(group["group_id"])
        refs = _reading_texts(group["evidence_ids"])
        _require(bool(refs) and len(refs) == len(set(refs)) and set(refs) <= spans.keys(),
                 "invalid_reading_group_references")
        _require(len({spans[ref]["source_id"] for ref in refs}) == 1,
                 "reading_group_parent_mismatch")
        if attributed:
            views = _reading_rows(group["citation_views"], limit=2)
            _require(bool(views), "missing_reading_citation_view")
            seen_support: set[frozenset[str]] = set()
            for raw_view in views:
                use_fields = {"reading_support_use", "reading_support_reason"} if schema == "du-production-reading/4" else set()
                view = _exact(raw_view, {"support_evidence_ids", "context_evidence_ids"} | use_fields,
                              "invalid_reading_citation_view")
                if use_fields:
                    _require(isinstance(view["reading_support_use"], str)
                             and view["reading_support_use"] in {"support", "context_only", "unresolved"}
                             and isinstance(view["reading_support_reason"], str)
                             and re.fullmatch(r"[a-z][a-z0-9_]{0,79}", view["reading_support_reason"]) is not None,
                             "invalid_reading_support_use")
                support = _reading_texts(view["support_evidence_ids"])
                context_refs = _reading_texts(view["context_evidence_ids"])
                _require(bool(support) and len(support) == len(set(support))
                         and len(context_refs) == len(set(context_refs))
                         and not set(support).intersection(context_refs)
                         and set(support) | set(context_refs) == set(refs),
                         "invalid_reading_citation_partition")
                identity = frozenset(support)
                _require(identity not in seen_support, "duplicate_reading_citation_view")
                seen_support.add(identity)
    lists = {"opaque_pages", "deferred_pages", "deferred_unit_ids", "unassigned_unit_ids"}
    unread = context["unread"]
    sampled = isinstance(unread, dict) and bool({"counts", "limited"} & unread.keys())
    _exact(unread, lists | {"native_scan", "structure_complete"}
           | ({"counts", "limited"} if sampled else set()), "invalid_reading_unread")
    _require(unread["native_scan"] is None or _text(unread["native_scan"]),
             "invalid_reading_native_scan")
    _require(unread["structure_complete"] is None or type(unread["structure_complete"]) is bool,
             "invalid_reading_structure_coverage")
    for name in ("opaque_pages", "deferred_pages"):
        _require(all(_integer(page, 1) for page in _reading_rows(unread[name])),
                 "invalid_reading_page")
    for name in ("deferred_unit_ids", "unassigned_unit_ids"):
        _reading_texts(unread[name])
    if sampled:
        _reading_sample(unread, lists, "counts", "limited")
    for row in _reading_rows(context["deferred"]):
        _exact(row, {"package_id", "reason"}, "invalid_reading_deferred")
        _require(_text(row["package_id"]) and _text(row["reason"]), "invalid_reading_deferred")
    _require(isinstance(context["layout_coverage"], dict), "invalid_reading_layout_coverage")
    if extra:
        _require(_integer(context["deferred_count"], len(context["deferred"]))
                 and type(context["deferred_limited"]) is bool
                 and context["deferred_limited"] == (context["deferred_count"] > len(context["deferred"])),
                 "invalid_reading_deferred_counts")
        for row in _reading_rows(context["selection_diagnostics"], limit=128):
            _selection_diagnostic(row, legacy_aggregate=schema in {
                "du-production-reading/1", "du-production-reading/2",
            })
    if schema in {"du-production-reading/3", "du-production-reading/4"}:
        _selection_trace(context["selection_trace"], spans)


def _reading_extension(bundle: dict) -> dict:
    return {"reading_context": bundle["reading_context"]} if "reading_context" in bundle else {}


def _bundle_fields(bundle: dict, base: set[str]) -> None:
    _exact(bundle, base | ({"reading_context"} if "reading_context" in bundle else set()), "invalid_narrative_bundle")


def _bundle(body: bytes, request: dict, receipt: dict, manifest: dict) -> dict:
    ref = request["narrative_ref"]
    _require(len(body) == ref["byte_size"] and hashlib.sha256(body).hexdigest() == ref["artifact_sha256"],
             "artifact_bytes_mismatch")
    bundle = decode_object(body, limit=BODY_LIMIT)
    _require(canonical_bytes(bundle) == body, "noncanonical_bundle")
    _bundle_fields(bundle, BUNDLE_FIELDS)
    _require(bundle["schema_version"] == "narrative-bundle/2.0", "unsupported_narrative_bundle")
    _require(bundle["source_ref"] == ref["source_ref"] and _sha(bundle["expected_read_policy_sha256"]),
             "bundle_source_mismatch")
    _bundle_contents(bundle, receipt, manifest)
    return bundle


def _bundle_contents(bundle: dict, receipt: dict, manifest: dict) -> None:
    metadata = _bundle_metadata(bundle, manifest)
    spans = _bundle_spans(bundle)
    by_id = {span["span_id"]: span for span in spans}
    selection = _selection(bundle["selection"], len(spans))
    _bundle_quality(bundle, receipt, selection, len(spans))
    if "reading_context" in bundle:
        _reading_context(bundle["reading_context"], by_id)
    skipped = selection["status"] == "skipped_no_narrative"
    _summary(bundle["summary"], bundle["source_ref"], by_id, metadata["language"], skipped)
    _replay(bundle["replay"], len(spans))
    _lineage(bundle, bundle["source_ref"], set(by_id))
    _diagnostics(bundle)


def _declared_language(metadata: dict) -> None:
    declared = metadata.get("declared_language")
    if declared is None:
        return
    _require(_text(declared), "invalid_declared_language")
    if declared in {"zh", "en", "mixed"}:
        family = declared
    else:
        family = _locale_family(declared)
    _require(family == metadata["language"], "declared_language_family_mismatch")


def _locale_family(declared: str) -> str:
    match = re.fullmatch(r"(zh|en)(?:-(Hans|Hant|Latn))?(?:-([a-z]{2}|[0-9]{3}))?", declared, re.IGNORECASE)
    _require(match is not None, "invalid_declared_language")
    match = cast(re.Match[str], match)
    family, script, _region = match.groups()
    family = family.lower()
    scripts = {"hans", "hant"} if family == "zh" else {"latn"}
    _require(not script or script.lower() in scripts, "invalid_declared_language")
    return family


def _metadata(value: Any, *, projected: bool = False) -> dict:
    fields = {"source_class", "title", "document_kind", "language"}
    if isinstance(value, dict) and "declared_language" in value:
        fields.add("declared_language")
    metadata = _exact(value, fields, "invalid_source_metadata")
    _require(metadata["title"] is None or _text(metadata["title"]), "invalid_source_metadata")
    _require(_text(metadata["document_kind"]), "invalid_source_metadata")
    classes = {"official_json"} if projected else {"filing", "transcript"}
    languages = {"en", "zh", "mixed", "unknown"} if projected else {"en", "zh", "mixed"}
    _require(isinstance(metadata["source_class"], str) and metadata["source_class"] in classes, "invalid_source_metadata")
    _require(isinstance(metadata["language"], str) and metadata["language"] in languages, "invalid_source_metadata")
    _declared_language(metadata)
    return metadata


def _manifest_language_family(value: Any) -> str:
    _require(_text(value), "invalid_manifest_language")
    return value if value in {"en", "zh", "mixed"} else _locale_family(value)


def _bundle_metadata(bundle: dict, manifest: dict) -> dict:
    metadata = _metadata(bundle["source_metadata"])
    _require(metadata["document_kind"] == manifest["document_kind"], "bundle_manifest_mismatch")
    if manifest["language"] is not None:
        _require(metadata["language"] == _manifest_language_family(manifest["language"]), "bundle_manifest_mismatch")
    return metadata


def _bundle_quality(bundle: dict, receipt: dict, selection: dict, count: int) -> None:
    _require(bundle["quality_status"] in QUALITY and bundle["quality_status"] == receipt["quality_status"],
             "quality_status_mismatch")
    _require(receipt["selection_status"] == selection["status"] and receipt["locator_count"] == count,
             "receipt_bundle_mismatch")
    skipped = selection["status"] == "skipped_no_narrative"
    _require(skipped == (bundle["quality_status"] == "skipped_no_narrative") and
             (not skipped or count == 0), "invalid_skip_bundle")


def _bundle_spans(bundle: dict) -> list[dict]:
    _require(isinstance(bundle["evidence_spans"], list), "invalid_evidence_spans")
    spans = [_span(span, bundle["source_ref"]) for span in bundle["evidence_spans"]]
    by_id = {span["span_id"]: span for span in spans}
    _require(len(by_id) == len(spans), "duplicate_evidence")
    return spans


def _replay(value: Any, count: int) -> None:
    replay = _exact(value, {"required", "locator_count"}, "invalid_replay")
    _require(replay["required"] is True and type(replay["locator_count"]) is int
             and replay["locator_count"] == count, "invalid_replay")


@dataclass(frozen=True)
class NarrativeContext:
    """Validated source excerpts and draft claims; never a calculated forecast."""
    value: dict

    def to_dict(self) -> dict:
        return deepcopy(self.value)


def _projection_parents(subject: dict, receipt: dict) -> None:
    parents = subject["parent_source_refs"]
    _require(isinstance(parents, list) and bool(parents), "invalid_parent_references")
    for parent in parents:
        validate_source_ref(parent)
    _require(len({parent["source_id"] for parent in parents}) == len(parents), "duplicate_parent_reference")
    _require(_integer(receipt["parent_count"], 1) and receipt["parent_count"] == len(parents), "projection_parent_count_mismatch")
    _require(_sha(receipt["lineage_sha256"]) and receipt["lineage_sha256"] ==
             hashlib.sha256(canonical_bytes(subject)).hexdigest(), "projection_lineage_mismatch")


def _projection_constraints(subject: dict, request: dict) -> None:
    _date(subject["as_of_date"])
    _require(request["as_of_date"] is None or subject["as_of_date"] == request["as_of_date"],
             "projection_as_of_mismatch")
    for key in ("issuer", "adapter", "coverage"):
        _require(isinstance(subject[key], dict), "invalid_subject_context")
    for key, expected in (request["expected_issuer"] or {}).items():
        actual = subject["issuer"].get(key)
        _require(type(actual) is type(expected) and actual == expected, "projection_issuer_mismatch")


def _projected_subject(value: Any, request: dict, receipt: dict) -> dict:
    subject = _exact(value, {"kind", "item_key", "subject_sha256", "parent_source_refs",
                            "issuer", "as_of_date", "adapter", "coverage"}, "invalid_subject_binding")
    compact = {"schema_version": "narrative-subject-ref/1", **{key: subject[key]
               for key in ("kind", "item_key", "subject_sha256")}}
    _require(compact == request["narrative_ref"]["subject_ref"], "bundle_subject_mismatch")
    validate_subject_ref(compact)
    _projection_parents(subject, receipt)
    _projection_constraints(subject, request)
    return subject


def _span_parent(span: dict, binding: dict, subject: dict) -> dict:
    parent = next((item for item in subject["parent_source_refs"] if
                   item["source_id"] == span["source_id"] and
                   item["content_sha256"] == binding.get("parent_content_sha256")), None)
    _require(parent is not None, "projection_span_parent_mismatch")
    _require(binding.get("projection_id") == subject["item_key"], "projection_span_parent_mismatch")
    return cast(dict[str, Any], parent)


def _projection_pointer(binding: dict) -> str:
    pointer, record = binding.get("pointer"), binding.get("record_pointer")
    _require(_text(pointer) and _text(record), "invalid_projection_pointer")
    pointer, record = cast(str, pointer), cast(str, record)
    _require(record.startswith("/") and pointer.startswith(record + "/"), "invalid_projection_pointer")
    suffix = pointer[len(record) + 1:]
    _require(bool(suffix) and "/" not in suffix, "invalid_projection_pointer")
    _require(not re.search(r"~(?![01])", pointer), "invalid_projection_pointer")
    return pointer


def _projection_range(value: Any, parent: dict) -> list[int]:
    _require(isinstance(value, list) and len(value) == 2, "invalid_projection_byte_range")
    _require(_integer(value[0]) and _integer(value[1], value[0]), "invalid_projection_byte_range")
    _require(value[1] <= parent["byte_size"], "invalid_projection_byte_range")
    return value


def _projection_byte_binding(binding: dict, parent: dict) -> list[int]:
    token = _projection_range(binding.get("token_range"), parent)
    encoded = _projection_range(binding.get("encoded_body_range"), parent)
    _require(token[0] < token[1], "invalid_projection_byte_binding")
    _require(token[0] <= encoded[0] <= encoded[1] <= token[1], "invalid_projection_byte_binding")
    for key in ("encoded_token_sha256", "decoded_sha256"):
        _require(_sha(binding.get(key)), "invalid_projection_byte_binding")
    return token


def _projection_locator(binding: dict, pointer: str, token: list[int]) -> None:
    locator = binding.get("source_locator")
    prefix = "cwp-json-pointer/1|p=" + quote(pointer, safe="") + "|b=" + str(token[0]) + ":" + str(token[1]) + "|d=0:"
    _require(isinstance(locator, str) and locator.startswith(prefix), "projection_pointer_locator_mismatch")
    locator = cast(str, locator)
    _require(re.fullmatch(r"[0-9]+\|x=json-string-decode/1", locator[len(prefix):]) is not None,
             "projection_pointer_locator_mismatch")


def _projected_span(value: Any, subject: dict) -> dict:
    """Each field retains its own parent and pointer; the first parent is no anchor."""
    span = _span_core(value)
    binding = span["structured_value"]
    _require(isinstance(binding, dict), "invalid_projection_span_binding")
    parent = _span_parent(span, binding, subject)
    pointer = _projection_pointer(binding)
    token = _projection_byte_binding(binding, parent)
    _projection_locator(binding, pointer, token)
    return span


def _projected_summary_draft(value: Any, subject: dict, spans: dict[str, dict], language: str) -> None:
    draft = _exact(value, {"subject_id", "subject_sha256", "language", "claims", "status"},
                   "invalid_subject_summary_draft")
    _require(draft["subject_id"] == subject["item_key"] and draft["subject_sha256"] == subject["subject_sha256"]
             and draft["language"] == language, "summary_subject_mismatch")
    _require(draft["status"] in {"draft", "needs_review"}, "invalid_summary_status")
    _require(isinstance(draft["claims"], list) and bool(draft["claims"]), "invalid_summary_claims")
    claims = [_claim(claim, spans) for claim in draft["claims"]]
    _require(len({claim["claim_id"] for claim in claims}) == len(claims), "duplicate_summary_claim")


def _projected_summary(value: Any, subject: dict, spans: dict[str, dict], language: str, skipped: bool) -> None:
    summary = _exact(value, {"status", "translate", "draft", "model"}, "invalid_summary")
    _require(summary["translate"] is False, "translated_summary_forbidden")
    if skipped:
        _require(summary["status"] == "summary_not_needed" and summary["draft"] is None and
                 summary["model"] is None, "invalid_skip_summary")
        return
    _require(summary["status"] == "completed", "invalid_summary_status")
    _projected_summary_draft(summary["draft"], subject, spans, language)
    _summary_model(summary["model"])


def _projected_receipt(receipt: dict, request: dict) -> None:
    _exact(receipt, PROJECTED_RECEIPT_FIELDS, "invalid_read_receipt")
    _require(receipt["schema_version"] == "narrative-read-receipt/3" and receipt["status"] == "ok" and
             receipt["replay_status"] == "verified", "unverified_read_receipt")
    validate_narrative_ref(receipt["narrative_ref"])
    _require(receipt["narrative_ref"] == request["narrative_ref"] and
             receipt["as_of_date"] == request["as_of_date"], "receipt_request_mismatch")
    _utc(receipt["observed_at"])
    _require(_integer(receipt["locator_count"]), "invalid_locator_count")


def _projection_bundle(body: bytes, ref: dict) -> dict:
    _require(len(body) == ref["byte_size"] and hashlib.sha256(body).hexdigest() == ref["artifact_sha256"],
             "artifact_bytes_mismatch")
    bundle = decode_object(body, limit=BODY_LIMIT)
    _require(canonical_bytes(bundle) == body, "noncanonical_bundle")
    fields = (BUNDLE_FIELDS - {"source_ref", "expected_read_policy_sha256", "transcript_lineage",
                             "transcript_byte_bindings"}) | {"subject_binding"}
    _bundle_fields(bundle, fields)
    _require(bundle["schema_version"] == "narrative-bundle/3.0", "unsupported_narrative_bundle")
    return bundle


def _projection_spans(bundle: dict, subject: dict) -> tuple[list[dict], dict[str, dict]]:
    _require(isinstance(bundle["evidence_spans"], list), "invalid_evidence_spans")
    spans = [_projected_span(span, subject) for span in bundle["evidence_spans"]]
    by_id = {span["span_id"]: span for span in spans}
    _require(len(by_id) == len(spans), "duplicate_evidence")
    return spans, by_id


def _projected_response(request: dict, body: bytes, receipt: dict) -> NarrativeContext:
    _projected_receipt(receipt, request)
    ref = request["narrative_ref"]
    bundle = _projection_bundle(body, ref)
    subject = _projected_subject(bundle["subject_binding"], request, receipt)
    metadata = _metadata(bundle["source_metadata"], projected=True)
    spans, by_id = _projection_spans(bundle, subject)
    selection = _selection(bundle["selection"], len(spans))
    _require(not selection["coverage_complete"] or (subject["coverage"].get("pagination_complete") is True and
             subject["coverage"].get("page_envelope_complete") is True), "projection_coverage_mismatch")
    _bundle_quality(bundle, receipt, selection, len(spans))
    if "reading_context" in bundle:
        _reading_context(bundle["reading_context"], by_id)
    _projected_summary(bundle["summary"], subject, by_id, metadata["language"],
                       selection["status"] == "skipped_no_narrative")
    _replay(bundle["replay"], len(spans))
    _diagnostics(bundle, subject["parent_source_refs"][0]["content_sha256"])
    return NarrativeContext({"schema_version": "revenue-narrative-context/3", "narrative_ref": ref,
        "subject_binding": subject, "parent_source_refs": subject["parent_source_refs"],
        "as_of_date": request["as_of_date"], "source_metadata": metadata, "selection": selection,
        "quality_status": bundle["quality_status"], "evidence_spans": spans,
        "summary": bundle["summary"], "read_receipt": receipt, **_reading_extension(bundle)})


def _validated_response(request: dict, body: bytes, receipt_bytes: bytes) -> NarrativeContext:
    request = validate_narrative_request(request)
    receipt = decode_object(receipt_bytes, limit=RECEIPT_LIMIT, one_line=True)
    if request["schema_version"] == "narrative-read-request/3":
        return _projected_response(request, body, receipt)
    manifest = _receipt(receipt, request)
    bundle = _bundle(body, request, receipt, manifest)
    return NarrativeContext({
        "schema_version": "revenue-narrative-context/1",
        "narrative_ref": request["narrative_ref"], "source_ref": bundle["source_ref"],
        "as_of_date": request["as_of_date"], "manifest": manifest,
        "source_metadata": bundle["source_metadata"], "selection": bundle["selection"],
        "quality_status": bundle["quality_status"], "evidence_spans": bundle["evidence_spans"],
        "summary": bundle["summary"], "read_receipt": receipt, **_reading_extension(bundle),
    })



def validate_narrative_response(request: dict, body: bytes, receipt_bytes: bytes) -> NarrativeContext:
    """Invalid JSON field types are a contract refusal, never a raw exception."""
    try:
        return _validated_response(request, body, receipt_bytes)
    except (TypeError, ValueError, RecursionError) as exc:
        raise NarrativeTransportError("blocked", "invalid_narrative_wire") from exc


def validate_reference_response(request: dict, body: bytes, receipt_bytes: bytes) -> dict:
    request = validate_reference_request(request)
    ref = validate_narrative_ref(decode_object(body, limit=REQUEST_LIMIT))
    receipt = decode_object(receipt_bytes, limit=RECEIPT_LIMIT, one_line=True)
    _exact(receipt, {"schema_version", "status", "narrative_ref"}, "invalid_reference_receipt")
    projected = request["schema_version"] == "narrative-reference-request/3"
    _require(receipt["schema_version"] == ("narrative-read-receipt/3" if projected else "narrative-read-receipt/1") and
             receipt["status"] == "metadata_only" and receipt["narrative_ref"] == ref,
             "invalid_reference_receipt")
    if projected:
        _require(ref["schema_version"] == "narrative-ref/3" and ref["subject_ref"] == request["subject_ref"] and
                 ref["generation_sha256"] == request["generation_sha256"], "reference_subject_mismatch")
    else:
        _require(ref["schema_version"] == "narrative-ref/1" and ref["source_ref"] == request["source_ref"],
                 "reference_source_mismatch")
    return deepcopy(ref)
