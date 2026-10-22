"""W03 raw receipt availability: real RF validators, no CWP imports or APIs."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from company_wiki_narrative_contracts import (  # noqa: E402
    RECEIPT_LIMIT, NarrativeTransportError, canonical_bytes, validate_narrative_response,
)
from company_wiki_narrative_reader import read_narrative_context  # noqa: E402
from test_company_wiki_narrative_reader import _resign, _valid  # noqa: E402
from test_narrative_source_preparation_transport import _fake  # noqa: E402
from test_w04_public_consumer import projected_wire  # noqa: E402

_ABSENT = object()


def _proof(digest, *, basis="prior_verified_capture", available_by="2026-08-01"):
    return {"schema_version": "source-availability-evidence/1", "source_sha256": digest,
            "available_by": available_by, "basis": basis,
            "evidence_ref": "urn:company-wiki:verified-capture:fixture", "locator": "capture:fixture"}


def _wire(*, publication=None, proof=_ABSENT, as_of="2026-09-01"):
    request, body, raw = _valid()
    receipt = json.loads(raw)
    request["as_of_date"] = receipt["as_of_date"] = as_of
    receipt["manifest"]["published_date"] = publication
    if proof is not _ABSENT:
        receipt["availability_evidence"] = deepcopy(proof)
    return request, body, canonical_bytes(receipt) + b"\n"


def _valid_proof(**kwargs):
    request, _, _ = _valid()
    return _proof(request["narrative_ref"]["source_ref"]["content_sha256"], **kwargs)


@pytest.mark.parametrize("basis,available_by,as_of", [
    ("prior_verified_capture", "2026-08-01", "2026-09-01"),
    ("primary_archive", "2026-08-01", "2026-09-01"),
    ("current_verified_open", "2026-10-03", "2026-10-03"),
])
def test_unknown_publication_consumes_same_source_proof_without_mutating_artifact(basis, available_by, as_of):
    proof = _valid_proof(basis=basis, available_by=available_by)
    wire = _wire(proof=proof, as_of=as_of)
    request_before = deepcopy(wire[0])
    body_sha = hashlib.sha256(wire[1]).hexdigest()
    context = validate_narrative_response(*wire)
    result = context.to_dict()
    assert result["manifest"]["published_date"] is None
    assert result["read_receipt"]["availability_evidence"] == proof
    assert result["narrative_ref"] == wire[0]["narrative_ref"]
    assert result["narrative_ref"]["artifact_sha256"] == body_sha
    assert wire[0] == request_before and wire[1] == _valid()[1]
    assert set(result) == set(validate_narrative_response(*_valid()).to_dict())
    result["read_receipt"]["availability_evidence"]["available_by"] = "1900-01-01"
    assert context.to_dict()["read_receipt"]["availability_evidence"] == proof


@pytest.mark.parametrize("proof", [_ABSENT, None])
def test_known_publication_legacy_omitted_or_null_proof_keeps_context_shape(proof):
    original = validate_narrative_response(*_valid()).to_dict()
    result = validate_narrative_response(*_wire(publication="2026-08-01", proof=proof)).to_dict()
    if proof is _ABSENT:
        assert "availability_evidence" not in result["read_receipt"]
        assert canonical_bytes(result) == canonical_bytes(original)
    else:
        assert result["read_receipt"].pop("availability_evidence") is None
        assert canonical_bytes(result) == canonical_bytes(original)


def test_known_past_publication_is_not_limited_by_late_current_capture():
    proof = _valid_proof(basis="current_verified_open", available_by="2026-10-03")
    result = validate_narrative_response(*_wire(publication="2026-08-01", proof=proof)).to_dict()
    assert result["manifest"]["published_date"] == "2026-08-01"
    assert result["read_receipt"]["availability_evidence"] == proof


@pytest.mark.parametrize("proof", [_ABSENT, None])
def test_unknown_publication_without_proof_does_not_borrow_retrieval_time(proof):
    wire = _wire(proof=proof)
    assert json.loads(wire[2])["manifest"]["retrieved_at"] == "2026-08-02T00:00:00Z"
    with pytest.raises(NarrativeTransportError, match="source_publication_unknown"):
        validate_narrative_response(*wire)


@pytest.mark.parametrize("proof", [_ABSENT, None, _valid_proof()])
def test_current_mode_retains_unknown_publication_without_historical_claim(proof):
    value = validate_narrative_response(*_wire(proof=proof, as_of=None)).to_dict()
    assert value["as_of_date"] is None and value["manifest"]["published_date"] is None


def test_future_publication_still_wins_over_early_or_broken_proof():
    bad = {**_valid_proof(), "source_sha256": "0" * 64}
    with pytest.raises(NarrativeTransportError, match="source_after_as_of"):
        validate_narrative_response(*_wire(publication="2026-09-02", proof=bad))


@pytest.mark.parametrize("publication", ["", "2026-02-30", False, []])
def test_invalid_publication_cannot_be_hidden_by_valid_proof(publication):
    with pytest.raises(NarrativeTransportError, match="invalid_as_of_date"):
        validate_narrative_response(*_wire(publication=publication, proof=_valid_proof()))


@pytest.mark.parametrize("available_by", ["2026-09-02", "2026-10-03"])
def test_later_availability_cannot_backfill_an_old_cutoff(available_by):
    proof = _valid_proof(available_by=available_by)
    with pytest.raises(NarrativeTransportError, match="source_availability_after_asof"):
        validate_narrative_response(*_wire(proof=proof))


@pytest.mark.parametrize("as_of", ["2026-09-01", None])
def test_proof_cannot_be_borrowed_from_a_different_raw_sha_even_in_current_mode(as_of):
    proof = {**_valid_proof(), "source_sha256": "0" * 64}
    with pytest.raises(NarrativeTransportError, match="source_availability_version_mismatch"):
        validate_narrative_response(*_wire(proof=proof, as_of=as_of))


@pytest.mark.parametrize("mutation", [
    "schema", "missing", "extra", "path", "bad_date", "bool_date", "list_basis", "bool_sha",
    "absolute_reference", "blank_locator", "control_reference", "oversize_locator", "list_proof",
])
def test_malformed_availability_is_a_bounded_contract_refusal(mutation):
    proof = _valid_proof()
    if mutation == "schema":
        proof["schema_version"] = "source-availability-evidence/2"
    elif mutation == "missing":
        del proof["locator"]
    elif mutation == "extra":
        proof["surprise"] = True
    elif mutation == "path":
        proof["local_path"] = "untrusted"
    elif mutation == "bad_date":
        proof["available_by"] = "2026-02-30"
    elif mutation == "bool_date":
        proof["available_by"] = True
    elif mutation == "list_basis":
        proof["basis"] = []
    elif mutation == "bool_sha":
        proof["source_sha256"] = True
    elif mutation == "absolute_reference":
        proof["evidence_ref"] = "file:untrusted-material"
    elif mutation == "blank_locator":
        proof["locator"] = " "
    elif mutation == "control_reference":
        proof["evidence_ref"] = "capture:\nsecret"
    elif mutation == "oversize_locator":
        proof["locator"] = "x" * 2049
    else:
        proof = []
    with pytest.raises(NarrativeTransportError) as caught:
        validate_narrative_response(*_wire(proof=proof))
    assert caught.value.status == "blocked"
    assert "untrusted" not in str(caught.value) and "secret" not in str(caught.value)


@pytest.mark.parametrize("mutation,reason", [("raw_sha", "manifest_source_mismatch"),
                                           ("request_security", "manifest_request_mismatch")])
def test_new_proof_does_not_replace_existing_source_or_request_binding(mutation, reason):
    request, body, raw = _wire(proof=_valid_proof())
    receipt = json.loads(raw)
    if mutation == "raw_sha":
        receipt["manifest"]["content_sha256"] = "0" * 64
    else:
        request["expected_source"]["security_id"] = "OTHER"
    with pytest.raises(NarrativeTransportError, match=reason):
        validate_narrative_response(request, body, canonical_bytes(receipt) + b"\n")


def test_only_named_optional_receipt_key_is_admitted_and_size_limit_remains():
    request, body, raw = _wire(proof=_valid_proof())
    receipt = json.loads(raw)
    receipt["unexpected"] = True
    with pytest.raises(NarrativeTransportError, match="invalid_read_receipt"):
        validate_narrative_response(request, body, canonical_bytes(receipt) + b"\n")
    receipt["unexpected"] = "x" * RECEIPT_LIMIT
    with pytest.raises(NarrativeTransportError, match="wire_size_limit"):
        validate_narrative_response(request, body, canonical_bytes(receipt) + b"\n")
    duplicate = raw.replace(b'"availability_evidence":', b'"availability_evidence":null,"availability_evidence":', 1)
    with pytest.raises(NarrativeTransportError, match="duplicate_json_key"):
        validate_narrative_response(request, body, duplicate)


@pytest.mark.parametrize("proof_parent", [None, 0, 1])
def test_projected_two_parent_receipt_does_not_admit_a_root_single_proof(proof_parent):
    request, body, raw = projected_wire()
    receipt = json.loads(raw)
    parents = json.loads(body)["subject_binding"]["parent_source_refs"]
    receipt["availability_evidence"] = None if proof_parent is None else _proof(parents[proof_parent]["content_sha256"])
    with pytest.raises(NarrativeTransportError, match="invalid_read_receipt"):
        validate_narrative_response(request, body, canonical_bytes(receipt) + b"\n")
    assert validate_narrative_response(request, body, raw).to_dict()["schema_version"] == "revenue-narrative-context/3"


def test_read_metadata_proof_does_not_become_immutable_bundle_or_cache_identity():
    left = _wire(proof=_valid_proof(available_by="2026-08-01"))
    right = _wire(proof=_valid_proof(available_by="2026-08-02"))
    first, second = (validate_narrative_response(*wire).to_dict() for wire in (left, right))
    assert first["narrative_ref"] == second["narrative_ref"] and left[1] == right[1]
    assert first["read_receipt"]["availability_evidence"] != second["read_receipt"]["availability_evidence"]
    bundle, receipt = json.loads(left[1]), json.loads(left[2])
    bundle["availability_evidence"] = _valid_proof()
    body, raw = _resign(left[0], bundle, receipt)
    with pytest.raises(NarrativeTransportError):
        validate_narrative_response(left[0], body, raw)


def test_real_rf_reader_process_keeps_complete_availability_receipt(tmp_path):
    request, body, receipt = _wire(proof=_valid_proof())
    context = read_narrative_context(request, catalog_config=tmp_path / "catalog.yaml",
                                    reader_command=_fake(tmp_path, body, receipt)).to_dict()
    assert context["read_receipt"] == json.loads(receipt)
    assert context["manifest"]["published_date"] is None


def test_public_preparation_output_retains_proof_only_inside_read_receipt(monkeypatch, tmp_path):
    import narrative_source_preparation as cli
    request, body, receipt = _wire(proof=_valid_proof())
    context = validate_narrative_response(request, body, receipt)
    output, errors = io.BytesIO(), io.BytesIO()
    monkeypatch.setattr(cli, "read_narrative_context", lambda *args, **kwargs: context)
    monkeypatch.setattr(cli.sys, "stdin", SimpleNamespace(buffer=io.BytesIO(canonical_bytes(request))))
    monkeypatch.setattr(cli.sys, "stdout", SimpleNamespace(buffer=output))
    monkeypatch.setattr(cli.sys, "stderr", SimpleNamespace(buffer=errors))
    assert cli.main(["--company-wiki-catalog-config", str(tmp_path / "catalog.yaml")]) == 0
    value = json.loads(output.getvalue())
    assert not errors.getvalue() and value["manifest"]["published_date"] is None
    assert value["read_receipt"]["availability_evidence"] == json.loads(receipt)["availability_evidence"]
    assert "availability_evidence" not in value
