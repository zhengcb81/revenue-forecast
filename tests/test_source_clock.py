"""18 source-clock responsibility cases; no providers/models/original mutation."""
from __future__ import annotations

from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import company_wiki_source_reader_v2 as reader  # noqa: E402
from company_wiki_source import CompanyWikiSourceError  # noqa: E402
from company_wiki_source_v2 import build_revenue_source_record_from_verified_read  # noqa: E402
from contracts.document import validate_evidence_claims, validate_sources  # noqa: E402
from contracts.evidence import ForecastInputError, build_host_receipt, canonical_sha256, text_sha256  # noqa: E402
from test_company_wiki_source_v2 import BODY, _inputs, _candidate  # noqa: E402
from test_company_wiki_source_reader_v2 import _receipt as transport_receipt, _ref as transport_ref, BODY as TRANSPORT_BODY  # noqa: E402

AS_OF = date(2026, 10, 8)
NOW = "2026-10-09T12:00:00+00:00"


def build(ref, receipt, manifest, body=BODY):
    return build_revenue_source_record_from_verified_read(
        source_ref=ref, read_receipt=receipt, source_bytes=body,
        source_manifest=manifest, source_candidate=_candidate(ref, manifest),
        as_of_date=AS_OF.isoformat(), source_type="regulatory_filing",
        publisher="Securities and Exchange Commission", page_or_section="Revenue note",
    )


def inputs():
    ref, receipt, manifest = deepcopy(_inputs())
    receipt["read_at"] = NOW
    manifest["published_date"] = "2026-10-01"
    manifest["retrieved_at"] = None
    return ref, receipt, manifest


def proof(sha):
    return {"schema_version": "source-availability-evidence/1", "source_sha256": sha,
            "available_by": "2026-10-07", "basis": "prior_verified_capture",
            "evidence_ref": "urn:fixture:immutable-capture:prior", "locator": "capture/read_at"}


def source(captured="2026-10-02", published="2026-10-01", host_timestamp=None):
    capture = {"capture_schema_version": "1.0", "capture_method": "local_document",
               "tool_name": "fixture-reader", "tool_call_id": "fixture-actual-event",
               "captured_date": captured, "snapshot_sha256": "a" * 64,
               "content_treatment": "untrusted_data_only", "prompt_injection_status": "not_reviewed",
               "host_receipt": build_host_receipt(issuer="fixture", environment="unit-test",
                   tool_name="fixture-reader", action="verified_read", event_sha256="a" * 64,
                   timestamp=host_timestamp or captured + "T12:00:00+00:00")}
    capture["receipt_sha256"] = canonical_sha256(capture)
    return {"source_id": "fixture-source", "source_type": "regulatory_filing",
            "title": "Annual report", "publisher": "Official publisher",
            "url": "https://www.sec.gov/Archives/fixture.htm", "published_date": published,
            "accessed_date": captured, "page_or_section": "Revenue note", "capture": capture}


def claim(src, verified="2026-10-09"):
    excerpt = "Revenue is recognized when the contractual performance obligation is satisfied."
    return {"claim_id": "clock-claim", "source_id": src["source_id"],
            "target_type": "recognition_policy", "target_id": "policy",
            "support_type": "policy_support", "locator": "Revenue note", "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt), "content_sha256": src["capture"]["snapshot_sha256"],
            "capture_receipt_sha256": src["capture"]["receipt_sha256"],
            "verification_status": "opened_and_checked", "verified_by": "unit-test-checker",
            "verified_date": verified}


def open_transport(monkeypatch, tmp_path, receipt, *, version=None):
    monkeypatch.setattr(reader, "_run_reader", lambda *a, **kw: subprocess.CompletedProcess(
        [], 0, TRANSPORT_BODY, (json.dumps(receipt) + "\n").encode()))
    kwargs = {} if version is None else {"source_reader_receipt_version": version}
    return reader.open_source_version_v2(source_ref=transport_ref(),
        catalog_config=tmp_path / "catalog.yaml", as_of_date=AS_OF.isoformat(),
        expected_fiscal_year=2025, **kwargs)


def test_T01_reader_late_original_download_is_legal(monkeypatch, tmp_path):
    receipt = transport_receipt()
    receipt["read_at"] = NOW
    receipt["manifest"]["retrieved_at"] = "2026-10-09T10:00:00Z"
    body, actual, manifest = open_transport(monkeypatch, tmp_path, receipt)
    assert body == TRANSPORT_BODY and actual["read_at"] == NOW
    assert manifest["retrieved_at"] == "2026-10-09T10:00:00Z"


def test_T02_null_original_capture_keeps_actual_next_day_read():
    ref, receipt, manifest = inputs()
    result = build(ref, receipt, manifest)
    assert result["capture"]["captured_date"] == "2026-10-09"
    assert result["accessed_date"] == "2026-10-09"
    assert result["company_wiki_trace"]["source_manifest"]["retrieved_at"] is None


def test_T03_original_capture_is_not_this_read_date():
    ref, receipt, manifest = inputs()
    manifest["retrieved_at"] = "2026-10-02T00:00:00Z"
    result = build(ref, receipt, manifest)
    assert result["capture"]["captured_date"] == "2026-10-09"
    assert result["capture"]["host_receipt"]["timestamp"] == NOW
    assert result["company_wiki_trace"]["source_manifest"]["retrieved_at"] == "2026-10-02T00:00:00Z"


def test_T04_formal_source_capture_can_be_after_information_day():
    src = source("2026-10-09")
    result = validate_sources({"sources": [src]}, AS_OF, require_capture=True)
    assert result[src["source_id"]]["capture"] == src["capture"]


def test_T05_actual_claim_verification_can_be_after_information_day():
    src = source()
    index = validate_sources({"sources": [src]}, AS_OF, require_capture=True)
    checked = claim(src)
    result = validate_evidence_claims({"schema_version": "3.7", "evidence_claims": [checked]}, index, {}, AS_OF)
    assert result["clock-claim"]["verified_date"] == "2026-10-09"


def test_T06_auto_narrative_claim_uses_actual_check_UTC_day(monkeypatch, tmp_path):
    import source_narrative_context as consumption
    from test_evidence_input_lineage import build_narrative_fixture
    from test_recognition_bridge import forecast_document
    from fix_hashes import apply_hash_fixes
    text = "Management expects recurring customer demand to support the next quarter."
    value = build_narrative_fixture(text, [text], read_at=NOW)
    data = forecast_document()
    data["as_of_date"] = AS_OF.isoformat()
    src = data["sources"][0]
    src["capture"]["snapshot_sha256"] = value["source_ref"]["content_sha256"]
    apply_hash_fixes(data)
    pid = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][0]
    binding = {"span_id": value["evidence_spans"][0]["span_id"], "claim_id": "next-day-check",
               "parameter_id": pid, "support_type": "rationale_support"}
    calls = []
    def read(*a, **kw):
        calls.append(1)
        return SimpleNamespace(to_dict=lambda: value)
    monkeypatch.setattr(consumption, "read_narrative_context", read)
    before = canonical_sha256(data)
    updated, consumed = consumption.consume_narrative_input(data,
        request={"as_of_date": AS_OF.isoformat()}, bindings=[binding], source_id=src["source_id"],
        catalog_config=tmp_path / "catalog.yaml")
    checked = next(c for c in updated["evidence_claims"] if c["claim_id"] == "next-day-check")
    assert checked["verified_date"] == "2026-10-09"
    assert consumed["read_at"] == NOW and len(calls) == 1
    assert canonical_sha256(data) == before


def test_T07_future_publication_cannot_be_overridden_by_early_proof():
    ref, receipt, manifest = inputs()
    manifest["published_date"] = "2026-10-09"
    receipt["schema_version"] = "2.2"
    receipt["availability_evidence"] = proof(ref["content_sha256"])
    with pytest.raises(CompanyWikiSourceError, match="source_publication_after_asof"):
        build(ref, receipt, manifest)


def test_T08_later_actual_fact_does_not_enter_old_information_set():
    src = source("2026-10-10", "2026-10-09")
    with pytest.raises(ForecastInputError, match="future information leak|source_publication_after_asof"):
        validate_sources({"sources": [src]}, AS_OF, require_capture=True)


def test_T09_unknown_publication_without_proof_is_named_gap():
    ref, receipt, manifest = inputs()
    manifest["published_date"] = None
    with pytest.raises(CompanyWikiSourceError, match="source_availability_unknown"):
        build(ref, receipt, manifest)


def test_T10_same_SHA_prior_availability_does_not_invent_publication():
    ref, receipt, manifest = inputs()
    manifest["published_date"] = None
    receipt["schema_version"] = "2.2"
    receipt["availability_evidence"] = proof(ref["content_sha256"])
    result = build(ref, receipt, manifest)
    assert result["published_date"] is None
    assert result["availability_evidence"] == receipt["availability_evidence"]
    validate_sources({"sources": [result]}, AS_OF, require_capture=True)
    checked = claim(result)
    validate_evidence_claims({"schema_version": "3.7", "evidence_claims": [checked]},
                             {result["source_id"]: result}, {}, AS_OF)


def test_T11_only_later_proof_still_refused():
    ref, receipt, manifest = inputs()
    manifest["published_date"] = None
    receipt["schema_version"] = "2.2"
    receipt["availability_evidence"] = {**proof(ref["content_sha256"]), "available_by": "2026-10-09"}
    with pytest.raises(CompanyWikiSourceError, match="source_availability_after_asof"):
        build(ref, receipt, manifest)


def test_T12_new_raw_SHA_cannot_reuse_old_proof():
    ref, receipt, manifest = inputs()
    manifest["published_date"] = None
    receipt["schema_version"] = "2.2"
    receipt["availability_evidence"] = proof("0" * 64)
    with pytest.raises(CompanyWikiSourceError, match="source_availability_version_mismatch"):
        build(ref, receipt, manifest)


def test_T13_bare_old_retrieved_is_not_unknown_publication_proof():
    ref, receipt, manifest = inputs()
    manifest["published_date"] = None
    manifest["retrieved_at"] = "2026-10-07T00:00:00Z"
    with pytest.raises(CompanyWikiSourceError, match="source_availability_unknown"):
        build(ref, receipt, manifest)


def test_T14_conflicting_events_are_named_without_backdating():
    src = source("2026-10-09", host_timestamp="2026-10-08T12:00:00Z")
    with pytest.raises(ForecastInputError, match="source_clock_conflict.*captured_date.*timestamp"):
        validate_sources({"sources": [src]}, AS_OF, require_capture=True)
    src = source("2026-10-02")
    checked = claim(src, "2026-10-01")
    with pytest.raises(ForecastInputError, match="source_clock_conflict.*verified_date.*captured_date"):
        validate_evidence_claims({"schema_version": "3.7", "evidence_claims": [checked]},
                                 {src["source_id"]: src}, {}, AS_OF)


def test_T15_receipt_22_requires_explicit_capability_and_exact_fields(monkeypatch, tmp_path):
    receipt = transport_receipt()
    receipt["schema_version"] = "2.2"
    receipt["availability_evidence"] = None
    body, bare, _ = open_transport(monkeypatch, tmp_path, receipt, version="2.2")
    assert body == TRANSPORT_BODY and bare["availability_evidence"] is None
    with pytest.raises(reader.SourceVersionTransportError, match="receipt"):
        open_transport(monkeypatch, tmp_path, receipt)
    receipt["surprise"] = True
    with pytest.raises(reader.SourceVersionTransportError, match="receipt"):
        open_transport(monkeypatch, tmp_path, receipt, version="2.2")


def test_T16_frozen_input_and_old_runtime_pair_are_not_rewritten():
    from schema_compatibility import validating_engine_allowed
    src = source()
    document = {"sources": [src]}
    before = json.dumps(document, sort_keys=True).encode()
    validate_sources(document, AS_OF, require_capture=True)
    assert json.dumps(document, sort_keys=True).encode() == before
    assert validating_engine_allowed("3.7", "4.1.0", "snapshot")
    assert not validating_engine_allowed("3.7", "9.9.9", "snapshot")
    fixture = ROOT / "tests/fixtures/cwp_verified_open_receipt_normalized.json"
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == "b27dccb3d8f4adf101d8f66b8feb1dcc98b987ec7993fbcc9c995f865f3d5869"


def test_T17_actual_UTC_day_does_not_follow_original_event_day():
    ref, receipt, manifest = inputs()
    receipt["read_at"] = "2026-10-09T00:30:00+00:00"
    manifest["retrieved_at"] = "2026-10-02T00:00:00Z"
    result = build(ref, receipt, manifest)
    assert result["capture"]["captured_date"] == "2026-10-09"
    receipt["read_at"] = "2026-10-09T00:30:00+01:00"
    with pytest.raises(CompanyWikiSourceError, match="UTC"):
        build(ref, receipt, manifest)


def test_T18_shared_source_preparation_covers_markets_formats(monkeypatch, tmp_path):
    import source_preparation as prep
    receipt = transport_receipt()
    receipt["read_at"] = NOW
    receipt["manifest"]["retrieved_at"] = None
    calls = []
    def read(*a, **kw):
        calls.append(1)
        return subprocess.CompletedProcess([], 0, TRANSPORT_BODY, (json.dumps(receipt) + "\n").encode())
    monkeypatch.setattr(reader, "_run_reader", read)
    ref = transport_ref()
    handle = {"status": "source_candidate", "source_ref": ref,
              "byte_verification": "pending_verified_open", "document_kind": "annual_report",
              "fiscal_year": 2025, "fiscal_period": None,
              "resolution_outcome": "reused_existing", "download_events": 0}
    for market, name, mime in [("CN", "Other CN company", "application/pdf"),
                               ("HK", "Other HK company", "application/pdf"),
                               ("US", "Other US company", "text/html")]:
        ref["mime_type"] = mime
        receipt["manifest"].update(market=market, display_name=name, mime_type=mime)
        result = prep._prepare_source_ref_v2({"document_kind": "annual_report", "as_of_date": AS_OF.isoformat()},
                                            handle, tmp_path / "catalog.yaml", timeout_seconds=30)
        assert result["capture"]["captured_date"] == "2026-10-09"
        assert result["reuse_receipt"]["download_calls"] == 0
        validate_sources({"sources": [result]}, AS_OF, require_capture=True)
    assert len(calls) == 3


def test_declared_22_capability_reaches_one_reader_invocation(monkeypatch, tmp_path):
    import source_preparation as prep
    receipt = transport_receipt()
    receipt["schema_version"] = "2.2"
    receipt["read_at"] = NOW
    receipt["availability_evidence"] = proof(receipt["content_sha256"])
    receipt["manifest"]["published_date"] = None
    receipt["manifest"]["retrieved_at"] = None
    calls = []
    def read(*args, **kwargs):
        calls.append(kwargs)
        return subprocess.CompletedProcess([], 0, TRANSPORT_BODY, (json.dumps(receipt) + "\n").encode())
    monkeypatch.setattr(reader, "_run_reader", read)
    handle = {"status": "source_candidate", "source_ref": transport_ref(),
              "byte_verification": "pending_verified_open", "document_kind": "annual_report",
              "fiscal_year": 2025, "fiscal_period": None,
              "resolution_outcome": "reused_existing", "download_events": 0}
    result = prep._prepare_source_ref_v2({"document_kind": "annual_report", "as_of_date": AS_OF.isoformat()},
        handle, tmp_path / "catalog.yaml", timeout_seconds=30, source_reader_receipt_version="2.2")
    assert result["published_date"] is None
    assert result["availability_evidence"] == receipt["availability_evidence"]
    assert calls == [{"source_reader_receipt_version": "2.2"}]
    assert result["reuse_receipt"]["download_calls"] == 0


def test_bad_capability_refused_before_filing_fetch(monkeypatch, tmp_path):
    import source_preparation as prep
    config = tmp_path / "catalog.yaml"
    config.write_text("{}", encoding="utf-8")
    calls = []
    monkeypatch.setattr(prep, "_run_filing_fetch", lambda *a, **kw: calls.append(1))
    with pytest.raises(RuntimeError, match="receipt capability"):
        prep.prepare_source_result({}, company_wiki_catalog_config=config,
                                   source_reader_receipt_version="2.9")
    assert calls == []
