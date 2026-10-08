"""Independent RF wire validation against CWP's published producer golden."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from company_wiki_narrative_contracts import (  # noqa: E402
    NarrativeTransportError, validate_narrative_request, validate_narrative_response,
)

GOLDEN = ROOT / "tests" / "fixtures" / "cwp_narrative_transport_v1"


def _json(name):
    return json.loads((GOLDEN / name).read_bytes())


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _valid():
    return _json("read_request.json"), (GOLDEN / "bundle.json").read_bytes(), (
        _canonical(_json("read_receipt.json")) + b"\n"
    )


def _resign(request, bundle, receipt):
    body = _canonical(bundle)
    ref = request["narrative_ref"]
    ref["artifact_sha256"] = hashlib.sha256(body).hexdigest()
    ref["byte_size"] = len(body)
    receipt["narrative_ref"] = deepcopy(ref)
    return body, _canonical(receipt) + b"\n"


def test_producer_golden_becomes_source_context_without_financial_prediction():
    request, body, receipt = _valid()
    context = validate_narrative_response(request, body, receipt).to_dict()
    assert context["schema_version"] == "revenue-narrative-context/1"
    assert context["source_ref"] == request["narrative_ref"]["source_ref"]
    assert context["narrative_ref"] == request["narrative_ref"]
    assert context["as_of_date"] == request["as_of_date"]
    assert len(context["evidence_spans"]) == 1
    assert context["summary"]["translate"] is False
    assert context["quality_status"] == "verified"
    assert "forecast" not in context
    assert "root" not in context and "path" not in context


@pytest.mark.parametrize("mutation", [
    "version", "source_version", "missing_constraint", "string_year", "boolean_size",
    "extra_path", "source_id_hash", "bad_date",
])
def test_request_is_exact_versioned_and_typed(mutation):
    request, _, _ = _valid()
    if mutation == "version":
        request["schema_version"] = "narrative-read-request/2"
    elif mutation == "source_version":
        request["narrative_ref"]["source_ref"]["schema_version"] = "1.0"
    elif mutation == "missing_constraint":
        del request["expected_source"]["security_id"]
    elif mutation == "string_year":
        request["expected_source"]["fiscal_year"] = "2026"
    elif mutation == "boolean_size":
        request["narrative_ref"]["byte_size"] = True
    elif mutation == "extra_path":
        request["narrative_ref"]["object_key"] = "objects/local"
    elif mutation == "source_id_hash":
        request["narrative_ref"]["source_ref"]["content_sha256"] = "a" * 64
    else:
        request["as_of_date"] = "2026-02-30"
    with pytest.raises(NarrativeTransportError):
        validate_narrative_request(request)


@pytest.mark.parametrize("mutation", [
    "metadata_only", "receipt_version", "wrong_asof", "wrong_ref", "raw_sha",
    "unknown_publication", "future_publication", "invalid_publication", "nonutc_capture", "invalid_capture", "wrong_entity",
    "wrong_year", "wrong_period", "locator_count", "wrong_quality", "extra_path",
])
def test_response_receipt_cannot_misstate_eligibility_or_identity(mutation):
    request, body, raw = _valid()
    receipt = json.loads(raw)
    if mutation == "metadata_only":
        receipt["status"] = "metadata_only"
    elif mutation == "receipt_version":
        receipt["schema_version"] = "narrative-read-receipt/2"
    elif mutation == "wrong_asof":
        receipt["as_of_date"] = "2026-10-01"
    elif mutation == "wrong_ref":
        receipt["narrative_ref"]["artifact_version_id"] = "narrative-other"
    elif mutation == "raw_sha":
        receipt["manifest"]["content_sha256"] = "a" * 64
    elif mutation == "unknown_publication":
        receipt["manifest"]["published_date"] = None
    elif mutation == "future_publication":
        receipt["manifest"]["published_date"] = "2026-09-02"
    elif mutation == "invalid_publication":
        receipt["manifest"]["published_date"] = "2026-02-30"
    elif mutation == "invalid_capture":
        receipt["manifest"]["retrieved_at"] = "2026-02-30T00:00:00Z"
    elif mutation == "nonutc_capture":
        receipt["manifest"]["retrieved_at"] = "2026-08-02T00:00:00+01:00"
    elif mutation == "wrong_entity":
        receipt["manifest"]["canonical_entity_id"] = "wrong"
    elif mutation == "wrong_year":
        receipt["manifest"]["fiscal_year"] = 2025
    elif mutation == "wrong_period":
        receipt["manifest"]["fiscal_period"] = "Q3"
    elif mutation == "locator_count":
        receipt["locator_count"] = 0
    elif mutation == "wrong_quality":
        receipt["quality_status"] = "needs_review"
    else:
        receipt["absolute_path"] = "forbidden-location"
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(request, body, _canonical(receipt) + b"\n")


@pytest.mark.parametrize("mutation", [
    "bundle_version", "bundle_source", "unbound_citation", "summary_source", "translate",
    "locator", "span_sha", "span_identity", "selected_count", "quality", "extra_path",
])
def test_even_resigned_bundle_must_preserve_source_locator_and_citation_contract(mutation):
    request, body, raw = _valid()
    bundle, receipt = json.loads(body), json.loads(raw)
    span = bundle["evidence_spans"][0]
    if mutation == "bundle_version":
        bundle["schema_version"] = "narrative-bundle/3.0"
    elif mutation == "bundle_source":
        bundle["source_ref"]["document_id"] = "wrong-document"
    elif mutation == "unbound_citation":
        bundle["summary"]["draft"]["claims"][0]["evidence_ids"] = ["missing-span"]
    elif mutation == "summary_source":
        bundle["summary"]["draft"]["source_sha256"] = "a" * 64
    elif mutation == "translate":
        bundle["summary"]["translate"] = True
    elif mutation == "locator":
        span["locator"] = "loc:v1/page:99"
    elif mutation == "span_sha":
        span["output_sha256"] = "a" * 64
    elif mutation == "span_identity":
        span["span_id"] = "urn:company-wiki:evidence-span:sha256:" + "a" * 64
    elif mutation == "selected_count":
        bundle["selection"]["selected_count"] = 0
    elif mutation == "quality":
        bundle["quality_status"] = "accepted_investment_thesis"
    else:
        span["structured_value"]["local_path"] = "forbidden-location"
    resigned, raw_receipt = _resign(request, bundle, receipt)
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(request, resigned, raw_receipt)


def test_actual_stdout_bytes_hash_size_and_canonical_json_are_required():
    request, body, receipt = _valid()
    for corrupt in (body[:-1] + b"X", body + b"\n", body[:100]):
        with pytest.raises(NarrativeTransportError):
            validate_narrative_response(request, corrupt, receipt)


@pytest.mark.parametrize("receipt", [b"{}\n{}\n", b'{"status":NaN}\n', b'{"status":"x","status":"x"}\n',
                                       b'[]\n', b"\xff\n"])
def test_receipt_is_exactly_one_finite_utf8_json_object(receipt):
    request, body, _ = _valid()
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(request, body, receipt)


def test_partial_and_needs_review_are_preserved_as_diagnostics():
    request, body, raw = _valid()
    bundle, receipt = json.loads(body), json.loads(raw)
    bundle["selection"]["status"] = "partial"
    bundle["selection"]["coverage_complete"] = False
    bundle["quality_status"] = "needs_review"
    receipt["selection_status"] = "partial"
    receipt["quality_status"] = "needs_review"
    resigned, raw_receipt = _resign(request, bundle, receipt)
    context = validate_narrative_response(request, resigned, raw_receipt).to_dict()
    assert context["selection"]["status"] == "partial"
    assert context["quality_status"] == "needs_review"
    assert context["selection"]["coverage_complete"] is False


@pytest.mark.parametrize("field", ["quality_status", "selection.status", "evidence_spans.parse_status",
                                  "summary.draft.status", "summary.draft.claims.claim_type"])
def test_malformed_json_types_return_a_bounded_contract_error(field):
    request, body, raw = _valid()
    bundle, receipt = json.loads(body), json.loads(raw)
    target = bundle
    parts = field.split(".")
    for part in parts[:-1]:
        target = target[part]
        if isinstance(target, list):
            target = target[0]
    target[parts[-1]] = []
    resigned, raw_receipt = _resign(request, bundle, receipt)
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(request, resigned, raw_receipt)



def test_current_read_policy_may_change_without_rewriting_persisted_artifact():
    request, body, raw = _valid()
    receipt = json.loads(raw)
    receipt["source_read_policy_sha256"] = "a" * 64
    context = validate_narrative_response(request, body, _canonical(receipt) + b"\n").to_dict()
    assert context["narrative_ref"] == request["narrative_ref"]
    assert context["read_receipt"]["source_read_policy_sha256"] == "a" * 64


@pytest.mark.parametrize("published_date", ["2026-08-01", "2026-09-01"])
def test_publication_cutoff_accepts_later_download_without_rewriting_metadata(published_date):
    request, body, raw = _valid()
    receipt = json.loads(raw)
    receipt["manifest"]["published_date"] = published_date
    receipt["manifest"]["retrieved_at"] = "2026-09-02T00:00:00Z"
    context = validate_narrative_response(request, body, _canonical(receipt) + b"\n").to_dict()
    assert context["as_of_date"] == "2026-09-01"
    assert context["read_receipt"]["manifest"] == receipt["manifest"]
    assert context["evidence_spans"] == json.loads(body)["evidence_spans"]
    assert context["narrative_ref"] == request["narrative_ref"]


@pytest.mark.parametrize("published_date", [None, "2026-08-01", "2026-09-02"])
def test_current_material_preserves_publication_without_historical_claim(published_date):
    request, body, raw = _valid()
    request["as_of_date"] = None
    receipt = json.loads(raw)
    receipt["as_of_date"] = None
    receipt["manifest"]["published_date"] = published_date
    dto = validate_narrative_response(request, body, _canonical(receipt) + b"\n").to_dict()
    assert dto["as_of_date"] is None
    assert dto["manifest"]["published_date"] == published_date
    assert dto["narrative_ref"] == request["narrative_ref"]
    assert dto["evidence_spans"] == json.loads(body)["evidence_spans"]
    assert "forecast" not in dto


def test_current_request_cannot_accept_historical_receipt_or_bad_bytes():
    request, body, raw = _valid()
    request["as_of_date"] = None
    receipt = json.loads(raw)
    receipt["as_of_date"] = None
    receipt["manifest"]["published_date"] = None
    valid = _canonical(receipt) + b"\n"
    assert validate_narrative_response(request, body, valid).to_dict()["as_of_date"] is None
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(request, body + b" ", valid)
    receipt["as_of_date"] = "2026-09-01"
    with pytest.raises(NarrativeTransportError, match="receipt_request_mismatch"):
        validate_narrative_response(request, body, _canonical(receipt) + b"\n")


@pytest.mark.parametrize("cutoff", [False, [], "", "2026-02-30"])
def test_invalid_cutoff_never_becomes_current_mode(cutoff):
    request, _, _ = _valid()
    request["as_of_date"] = cutoff
    with pytest.raises(NarrativeTransportError):
        validate_narrative_request(request)


@pytest.mark.parametrize("cutoff", [None, "2026-09-01"])
def test_unknown_collection_time_is_preserved_not_fabricated(cutoff):
    request, body, raw = _valid()
    receipt = json.loads(raw)
    request["as_of_date"] = receipt["as_of_date"] = cutoff
    receipt["manifest"]["retrieved_at"] = None
    dto = validate_narrative_response(request, body, _canonical(receipt) + b"\n").to_dict()
    assert dto["manifest"]["retrieved_at"] is None
    assert dto["manifest"]["published_date"] == receipt["manifest"]["published_date"]
    assert dto["evidence_spans"] == json.loads(body)["evidence_spans"]


@pytest.mark.parametrize("retrieved_at", ["", "not-a-date", "2026-01-01", []])
def test_present_invalid_collection_time_is_rejected(retrieved_at):
    request, body, raw = _valid()
    receipt = json.loads(raw)
    receipt["manifest"]["retrieved_at"] = retrieved_at
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(request, body, _canonical(receipt) + b"\n")


@pytest.mark.parametrize("language, allowed", [(None, True), ("en", True), ("zh", False)])
def test_missing_registered_language_does_not_contradict_detected_language(language, allowed):
    request, body, raw = _valid()
    receipt = json.loads(raw)
    request["as_of_date"] = receipt["as_of_date"] = None
    receipt["manifest"]["language"] = language
    if allowed:
        dto = validate_narrative_response(request, body, _canonical(receipt) + b"\n").to_dict()
        assert dto["manifest"]["language"] == language
        assert dto["source_metadata"]["language"] == "en"
    else:
        with pytest.raises(NarrativeTransportError, match="bundle_manifest_mismatch"):
            validate_narrative_response(request, body, _canonical(receipt) + b"\n")
