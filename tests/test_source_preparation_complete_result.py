"""W04 responsibility tests: complete results and actual narrative consumption."""
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
import filing_fetch_client as client  # noqa: E402
import source_preparation as prep  # noqa: E402
from company_wiki_narrative_contracts import validate_narrative_response  # noqa: E402


def candidate(year=2026):
    return {"status": "source_candidate", "source_ref": {"schema_version": "2.0"},
            "byte_verification": "pending_verified_open", "document_kind": "annual_report",
            "fiscal_year": year, "fiscal_period": "FY", "resolution_outcome": "reused_existing",
            "download_events": 0}


def result():
    return {"schema_version": "2.0", "status": "source_candidate", "filing": candidate(),
            "request_period": {"mode": "latest_as_of", "fiscal_year": None},
            "transcript": {"status": "not_found", "reason": "provider_entitlement_required",
                           "retryable": False, "usage": {"requests": 1, "response_bytes": 0}},
            "calls": 3, "downloads": 0, "usage": {"model_tokens": None}}


def test_latest_uses_resolved_candidate_and_exact_stays_strict():
    latest = {"document_kind": "annual_report", "period_selection": "latest_as_of"}
    assert prep._validate_v2_candidate(latest, candidate()) == 2026
    assert prep._validate_v2_candidate(latest, candidate(2025)) == 2025
    with pytest.raises(RuntimeError, match="fiscal_year mismatch"):
        prep._validate_v2_candidate({**latest, "fiscal_year": 2025}, candidate())


@pytest.mark.parametrize("year", [True, -1, None])
def test_latest_rejects_unresolved_or_invalid_year(year):
    with pytest.raises(RuntimeError, match="fiscal_year"):
        prep._validate_v2_candidate({"document_kind": "annual_report"}, candidate(year))


def test_complete_result_retains_companion_and_unknown_usage(tmp_path):
    script = tmp_path / "scripts" / "fetch_filing.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")
    complete = result()
    completed = subprocess.CompletedProcess([], 0, json.dumps(complete), "")
    with patch.object(client.subprocess, "run", return_value=completed):
        received = client.resolve_filing_result({}, filing_fetch_root=tmp_path, source_ref_v2=True)
        assert received == complete
        assert received["usage"]["model_tokens"] is None
        assert client.resolve_filing({}, filing_fetch_root=tmp_path, source_ref_v2=True) == complete["filing"]


def test_prepare_result_adds_envelope_without_changing_formal_source(tmp_path):
    config = tmp_path / "catalog.json"
    config.write_text("{}", encoding="utf-8")
    source = {"source_id": "source", "capture": {"snapshot_sha256": "a" * 64}}
    with patch.object(prep, "_run_filing_fetch", return_value=result()) as run, patch.object(
        prep, "_prepare_source_ref_v2", return_value=source
    ):
        envelope = prep.prepare_source_result({"document_kind": "annual_report"},
                                             company_wiki_catalog_config=config)
    assert run.call_count == 1
    assert envelope == {"schema_version": "source-preparation-result/1", "source": source,
                        "filing_fetch": result(), "narrative": None}
    assert "filing_fetch" not in source


def golden_context():
    folder = ROOT / "tests" / "fixtures" / "cwp_narrative_transport_v1"
    request = json.loads((folder / "read_request.json").read_bytes())
    receipt = (folder / "read_receipt.json").read_bytes().rstrip() + b"\n"
    context = validate_narrative_response(request, (folder / "bundle.json").read_bytes(), receipt)
    return request, context


def test_real_span_claim_parameter_formula_dependency_and_metadata_is_not_consumed(tmp_path):
    from source_narrative_context import consume_narrative_input
    from test_recognition_bridge import forecast_document
    from revenue_core import run_forecast
    request, context = golden_context()
    data = forecast_document()
    source = data["sources"][0]
    source["capture"]["snapshot_sha256"] = request["narrative_ref"]["source_ref"]["content_sha256"]
    from fix_hashes import apply_hash_fixes
    data["as_of_date"] = request["as_of_date"]
    apply_hash_fixes(data)
    pid = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][0]
    parameter = next(p for p in data["parameters"] if p["parameter_id"] == pid)
    binding = {"span_id": context.to_dict()["evidence_spans"][0]["span_id"],
               "claim_id": "narrative_mechanism", "parameter_id": parameter["parameter_id"],
               "support_type": "rationale_support"}
    with patch("source_narrative_context.read_narrative_context", return_value=context) as read:
        updated, receipt = consume_narrative_input(data, request=request, bindings=[binding],
                                                  source_id=source["source_id"], catalog_config=tmp_path / "catalog.json")
    assert read.call_count == 1
    assert receipt["status"] == "consumed"
    claim = next(c for c in updated["evidence_claims"] if c["claim_id"] == binding["claim_id"])
    assert claim["excerpt"] == context.to_dict()["evidence_spans"][0]["raw_text"]
    assert claim["locator"] == context.to_dict()["evidence_spans"][0]["locator"]
    assert binding["claim_id"] in next(p for p in updated["parameters"] if p["parameter_id"] == binding["parameter_id"])["claim_ids"]
    output = run_forecast(updated, mode="draft")
    assert receipt["dependencies"][0]["formula_refs"]
    assert output["consolidated_forecast"]
    with patch("source_narrative_context.read_narrative_context", return_value=context):
        _, unused = consume_narrative_input(data, request=request, bindings=[],
                                            source_id=source["source_id"], catalog_config=tmp_path / "catalog.json")
    assert unused["status"] == "not_consumed"


def test_mixed_source_and_unavailable_never_fallback(tmp_path):
    from source_narrative_context import consume_narrative_input
    from company_wiki_narrative_contracts import NarrativeTransportError
    request, context = golden_context()
    data = {"sources": [{"source_id": "x", "capture": {"snapshot_sha256": "0" * 64}}]}
    with patch("source_narrative_context.read_narrative_context", return_value=context):
        with pytest.raises(ValueError, match="source"):
            consume_narrative_input(data, request=request, bindings=[], source_id="x",
                                    catalog_config=tmp_path / "catalog.json")
    with patch("source_narrative_context.read_narrative_context", side_effect=NarrativeTransportError("unavailable", "source_unavailable")):
        with pytest.raises(NarrativeTransportError):
            consume_narrative_input(data, request=request, bindings=[], source_id="x",
                                    catalog_config=tmp_path / "catalog.json")


def test_recorded_full_success_replays_without_requery(tmp_path):
    payload = json.loads((ROOT / "tests" / "fixtures" / "ff_complete_success_v2.json").read_text(encoding="utf-8"))
    script = tmp_path / "scripts" / "fetch_filing.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")
    with patch.object(client.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(payload), "")) as run:
        actual = client.resolve_filing_result({}, filing_fetch_root=tmp_path, source_ref_v2=True)
    assert actual == payload
    assert run.call_count == 1
    assert actual["calls"] == 3 and actual["downloads"] == 0
    assert actual["transcript"]["provider_requests"] == 1
    assert actual["transcript"]["retryable"] is False


def test_complete_v2_result_refuses_companion_storage_paths(tmp_path):
    script = tmp_path / "scripts" / "fetch_filing.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")
    complete = result()
    complete["transcript"]["storage_path"] = "private/path"
    with patch.object(client.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(complete), "")):
        with pytest.raises(client._ClientError, match="storage location"):
            client.resolve_filing_result({}, filing_fetch_root=tmp_path, source_ref_v2=True)


@pytest.mark.parametrize(("name", "year", "period_end"), [("CalendarCo", 2025, "2025-12-31"), ("JanuaryCo", 2026, "2026-01-31")])
def test_latest_verified_manifest_with_different_financial_calendars(tmp_path, name, year, period_end):
    from test_company_wiki_source_reader_v2 import _ref, _receipt, BODY
    import company_wiki_source_reader_v2 as reader
    receipt = _receipt()
    receipt["manifest"].update(display_name=name, fiscal_year=year, fiscal_period="FY", period_end=period_end)
    handle = candidate(year)
    handle["source_ref"] = _ref()
    with patch.object(reader, "_run_reader", return_value=subprocess.CompletedProcess([], 0, BODY, (json.dumps(receipt) + "\n").encode())):
        record = prep._prepare_source_ref_v2({"document_kind": "annual_report", "as_of_date": "2026-10-09"}, handle,
                                             tmp_path / "catalog.json", timeout_seconds=30)
    assert record["company_wiki_trace"]["source_manifest"]["fiscal_year"] == year
    assert record["capture"]["snapshot_sha256"] == _ref()["content_sha256"]


@pytest.mark.parametrize("mutation", ["period", "future"])
def test_latest_still_rejects_manifest_period_or_publication_conflict(tmp_path, mutation):
    from test_company_wiki_source_reader_v2 import _ref, _receipt, BODY
    import company_wiki_source_reader_v2 as reader
    receipt = _receipt()
    if mutation == "period":
        receipt["manifest"]["fiscal_year"] = 2026
    else:
        receipt["manifest"]["published_date"] = "2026-10-10"
    handle = candidate(2025)
    handle["source_ref"] = _ref()
    with patch.object(reader, "_run_reader", return_value=subprocess.CompletedProcess([], 0, BODY, (json.dumps(receipt) + "\n").encode())):
        with pytest.raises(RuntimeError):
            prep._prepare_source_ref_v2({"document_kind": "annual_report", "as_of_date": "2026-10-09"}, handle,
                                        tmp_path / "catalog.json", timeout_seconds=30)
