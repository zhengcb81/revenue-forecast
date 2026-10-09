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
from typing import Any

BODY_LIMIT = 1_310_720
RECEIPT_LIMIT = 16 * 1024
REQUEST_LIMIT = 16 * 1024
SOURCE_PREFIX = "urn:company-wiki:source:sha256:"
SPAN_PREFIX = "urn:company-wiki:evidence-span:sha256:"
EXPECTED_FIELDS = {"canonical_entity_id", "market", "security_id", "document_kind",
                   "fiscal_year", "fiscal_period"}
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


def validate_narrative_ref(value: Any) -> dict:
    ref = _exact(value, REF_FIELDS, "invalid_narrative_reference")
    _require(ref["schema_version"] == "narrative-ref/1", "unsupported_narrative_reference")
    _require(isinstance(ref["artifact_version_id"], str) and
             _ID.fullmatch(ref["artifact_version_id"]) is not None, "invalid_artifact_id")
    _require(_sha(ref["artifact_sha256"]), "invalid_artifact_sha")
    _require(_integer(ref["byte_size"], 1) and ref["byte_size"] <= BODY_LIMIT, "invalid_artifact_size")
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


def validate_narrative_request(value: Any) -> dict:
    request = _exact(value, {"schema_version", "narrative_ref", "as_of_date", "expected_source"},
                     "invalid_read_request")
    _require(request["schema_version"] == "narrative-read-request/1", "unsupported_read_request")
    validate_narrative_ref(request["narrative_ref"])
    if request["as_of_date"] is not None:
        _date(request["as_of_date"])
    _constraints(request["expected_source"])
    _pathless(request)
    _require(len(canonical_bytes(request)) <= REQUEST_LIMIT, "request_size_limit")
    return deepcopy(request)


def validate_reference_request(value: Any) -> dict:
    request = _exact(value, {"schema_version", "source_ref"}, "invalid_reference_request")
    _require(request["schema_version"] == "narrative-reference-request/1", "unsupported_reference_request")
    validate_source_ref(request["source_ref"])
    _pathless(request)
    return deepcopy(request)


def _manifest(receipt: dict, request: dict) -> dict:
    manifest = _exact(receipt["manifest"], MANIFEST_FIELDS, "invalid_source_manifest")
    source = request["narrative_ref"]["source_ref"]
    for key in SOURCE_FIELDS - {"schema_version"}:
        _require(type(manifest[key]) is type(source[key]) and manifest[key] == source[key],
                 "manifest_source_mismatch")
    for key, value in request["expected_source"].items():
        if value is not None:
            _require(type(manifest[key]) is type(value) and manifest[key] == value, "manifest_request_mismatch")
    if request["as_of_date"] is not None:
        cutoff = _date(request["as_of_date"])
        _require(manifest["published_date"] is not None, "source_publication_unknown")
        _require(_date(manifest["published_date"]) <= cutoff, "source_after_as_of")
    elif manifest["published_date"] is not None:
        _date(manifest["published_date"])  # Current mode preserves typed metadata.
    if manifest["retrieved_at"] is not None:
        _utc(manifest["retrieved_at"])  # Unknown collection time stays unknown.
    return manifest


def _receipt(receipt: dict, request: dict) -> dict:
    _exact(receipt, RECEIPT_FIELDS, "invalid_read_receipt")
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


def _span(value: Any, source: dict) -> dict:
    span = _exact(value, SPAN_FIELDS, "invalid_evidence_span")
    _require(span["schema_version"] == "1.0.0" and span["source_id"] == source["source_id"],
             "span_source_mismatch")
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
    claim = _exact(value, {"claim_id", "text", "evidence_ids", "claim_type", "modality", "needs_review"},
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


def _diagnostics(bundle: dict) -> None:
    review = _exact(bundle["prompt_review"], {"status", "source_sha256", "evidence_sha256", "policy_hash",
                                            "reviewed_at"}, "invalid_prompt_diagnostic")
    _require(review["status"] in {"not_detected", "detected_and_ignored", "not_reviewed"},
             "invalid_prompt_diagnostic")
    if review["source_sha256"] is not None:
        _require(review["source_sha256"] == bundle["source_ref"]["content_sha256"], "prompt_source_mismatch")
    versions = _exact(bundle["versions"], {"parser", "selector", "material", "model", "prompt",
                                         "bundle_producer"}, "invalid_bundle_versions")
    _require(all(_text(versions[key]) for key in ("parser", "selector", "bundle_producer")),
             "invalid_bundle_versions")


def _bundle(body: bytes, request: dict, receipt: dict, manifest: dict) -> dict:
    ref = request["narrative_ref"]
    _require(len(body) == ref["byte_size"] and hashlib.sha256(body).hexdigest() == ref["artifact_sha256"],
             "artifact_bytes_mismatch")
    bundle = decode_object(body, limit=BODY_LIMIT)
    _require(canonical_bytes(bundle) == body, "noncanonical_bundle")
    _exact(bundle, BUNDLE_FIELDS, "invalid_narrative_bundle")
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
    skipped = selection["status"] == "skipped_no_narrative"
    _summary(bundle["summary"], bundle["source_ref"], by_id, metadata["language"], skipped)
    _replay(bundle["replay"], len(spans))
    _lineage(bundle, bundle["source_ref"], set(by_id))
    _diagnostics(bundle)


def _bundle_metadata(bundle: dict, manifest: dict) -> dict:
    metadata = _exact(bundle["source_metadata"], {"source_class", "title", "document_kind", "language"},
                      "invalid_source_metadata")
    _require(metadata["document_kind"] == manifest["document_kind"] and
             (manifest["language"] is None or metadata["language"] == manifest["language"]),
             "bundle_manifest_mismatch")
    _require(metadata["source_class"] in {"filing", "transcript"} and metadata["language"] in {"en", "zh", "mixed"},
             "invalid_source_metadata")
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


def _validated_response(request: dict, body: bytes, receipt_bytes: bytes) -> NarrativeContext:
    request = validate_narrative_request(request)
    receipt = decode_object(receipt_bytes, limit=RECEIPT_LIMIT, one_line=True)
    manifest = _receipt(receipt, request)
    bundle = _bundle(body, request, receipt, manifest)
    return NarrativeContext({
        "schema_version": "revenue-narrative-context/1",
        "narrative_ref": request["narrative_ref"], "source_ref": bundle["source_ref"],
        "as_of_date": request["as_of_date"], "manifest": manifest,
        "source_metadata": bundle["source_metadata"], "selection": bundle["selection"],
        "quality_status": bundle["quality_status"], "evidence_spans": bundle["evidence_spans"],
        "summary": bundle["summary"], "read_receipt": receipt,
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
    _require(receipt["schema_version"] == "narrative-read-receipt/1" and
             receipt["status"] == "metadata_only" and receipt["narrative_ref"] == ref,
             "invalid_reference_receipt")
    _require(ref["source_ref"] == request["source_ref"], "reference_source_mismatch")
    return deepcopy(ref)
