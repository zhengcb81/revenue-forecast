"""R1 cross-process companion failure retention and source-clock compatibility."""

from __future__ import annotations
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import filing_fetch_client as client
import source_preparation as prep
from filing_upstream_cause import failure_observation
from contracts.source_clock import (
    qualify_source_information,
    SourceClockError,
    source_information_eligibility,
)


def companion():
    return {
        "status": "not_run",
        "reason": "filing_failed_before_companion_dispatch",
        "retryable": False,
        "intent": "fetch_if_missing",
        "provider": "fmp",
        "fiscal_year": 2026,
        "fiscal_quarter": 2,
        "acquisition_limits": {
            "max_bytes": 100000,
            "timeout_seconds": 10,
            "max_cost_usd": "0",
        },
        "provider_started": False,
        "provider_requests": 0,
        "provider_response_bytes": 0,
        "provider_usage_complete": True,
    }


def failed():
    return {
        "schema_version": "2.0",
        "status": "upstream_error",
        "request_period": {
            "mode": "exact",
            "fiscal_year": 2026,
            "fiscal_period": "H1",
            "as_of_date": "2026-10-21",
        },
        "filing": {
            "status": "upstream_error",
            "reason": "company-wiki ensure unavailable",
            "retryable": False,
            "producer_exit_code": 2,
            "upstream_cause": {
                "schema_version": "filing-upstream-cause/1",
                "operation": "ensure",
                "code": "local_candidate_limit",
                "provider_started": False,
                "usage_complete": True,
                "retry_scope": "none",
            },
        },
        "transcript": companion(),
        "calls": 2,
        "downloads": 0,
    }


def test_failure_safe_projection_retains_requested_companion_and_exit():
    observed = failure_observation(failed())
    assert observed["companion_observation"] == companion()
    assert observed["producer_exit_code"] == 2
    assert observed["upstream_cause"]["code"] == "local_candidate_limit"


def test_client_exception_keeps_complete_ff_sidecar(tmp_path):
    script = tmp_path / "scripts" / "fetch_filing.py"
    script.parent.mkdir()
    script.write_text("", encoding="utf-8")
    payload = failed()
    with patch.object(
        client.subprocess,
        "run",
        return_value=subprocess.CompletedProcess([], 2, json.dumps(payload), ""),
    ):
        with pytest.raises(client._ClientError) as caught:
            client.resolve_filing_result(
                {}, filing_fetch_root=tmp_path, source_ref_v2=True
            )
    assert caught.value.filing_fetch_result == payload
    assert caught.value.companion_observation == companion()


def test_actual_rf_cli_chain_preserves_both_results(tmp_path):
    fake = tmp_path / "ff"
    (fake / "scripts").mkdir(parents=True)
    payload = failed()
    (fake / "scripts" / "fetch_filing.py").write_text(
        "import json,sys;print(json.dumps(" + repr(payload) + "));sys.exit(2)",
        encoding="utf-8",
    )
    # The catalog config is validated for existence; no source reader runs after filing failure.
    config = tmp_path / "catalog.yaml"
    config.write_text("{}", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(Path(prep.__file__)),
            "--result-envelope",
            "--company-wiki-catalog-config",
            str(config),
            "--filing-fetch-root",
            str(fake),
            "--timeout-seconds",
            "10",
        ],
        input=json.dumps({"document_kind": "semi_annual_report"}),
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 3, result.stdout + result.stderr
    error = json.loads(result.stderr)
    assert error["companion_observation"] == companion()
    assert error["filing_fetch_result"] == payload
    assert error["producer_exit_code"] == 2


@pytest.mark.parametrize(
    "mutate", ["path", "wrong_count", "wrong_reason", "wrong_period", "unknown_field"]
)
def test_unsafe_companion_is_not_projected(mutate):
    payload = failed()
    bad = payload["transcript"]
    if mutate == "path":
        bad["storage_path"] = "secrets/original.txt"
    elif mutate == "wrong_count":
        bad["provider_requests"] = 1
    elif mutate == "wrong_reason":
        bad["reason"] = "https://private/key"
    elif mutate == "wrong_period":
        bad["fiscal_quarter"] = 5
    else:
        bad["opaque"] = "unknown"
    observed = failure_observation(payload)
    assert "companion_observation" not in observed
    assert "filing_fetch_result" not in observed


def proof():
    return {
        "schema_version": "source-availability-evidence/1",
        "source_sha256": "a" * 64,
        "available_by": "2026-10-21",
        "basis": "current_verified_open",
        "evidence_ref": "source-verified-open:sha256:fixture",
        "locator": "/read_at + /content_sha256",
    }


def test_current_open_qualifies_today_without_backdating_publication():
    actual = qualify_source_information(
        source_sha256="a" * 64,
        published_date=None,
        as_of=date(2026, 10, 21),
        availability_evidence=proof(),
    )
    assert actual.basis == "current_verified_open" and actual.published_date is None
    with pytest.raises(SourceClockError, match="after_asof"):
        qualify_source_information(
            source_sha256="a" * 64,
            published_date=None,
            as_of=date(2026, 10, 20),
            availability_evidence=proof(),
        )
    with pytest.raises(SourceClockError, match="publication_after_asof"):
        qualify_source_information(
            source_sha256="a" * 64,
            published_date="2026-10-22",
            as_of=date(2026, 10, 21),
            availability_evidence=proof(),
        )
    with pytest.raises(SourceClockError, match="version_mismatch"):
        qualify_source_information(
            source_sha256="b" * 64,
            published_date=None,
            as_of=date(2026, 10, 21),
            availability_evidence=proof(),
        )


def test_current_open_requires_existing_public_receipt_lineage():
    with pytest.raises(SourceClockError, match="lineage"):
        source_information_eligibility(
            {
                "capture": {"snapshot_sha256": "a" * 64},
                "published_date": None,
                "availability_evidence": proof(),
            },
            date(2026, 10, 21),
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", []),
        ("intent", {}),
        ("provider", []),
        ("fiscal_year", "2026"),
        ("fiscal_quarter", True),
        ("provider_requests", False),
    ],
)
def test_malformed_companion_field_types_stay_safe(field, value):
    payload = failed()
    payload["transcript"][field] = value
    observed = failure_observation(payload)
    assert "companion_observation" not in observed
    assert "filing_fetch_result" not in observed


def test_current_basis_through_public_reader_and_source_record(tmp_path, monkeypatch):
    from test_company_wiki_source_reader_v2 import _ref, _receipt, BODY
    import company_wiki_source_reader_v2 as reader
    from company_wiki_source_v2 import build_revenue_source_record_from_verified_read
    from test_company_wiki_source_v2 import _candidate

    receipt = _receipt()
    receipt["schema_version"] = "2.2"
    receipt["read_at"] = "2026-10-21T15:00:00+00:00"
    receipt["manifest"]["published_date"] = None
    receipt["manifest"]["retrieved_at"] = None
    receipt["availability_evidence"] = {
        **proof(),
        "source_sha256": _ref()["content_sha256"],
    }
    monkeypatch.setattr(
        reader,
        "_run_reader",
        lambda *a, **kw: subprocess.CompletedProcess(
            [], 0, BODY, (json.dumps(receipt) + "\n").encode()
        ),
    )
    raw, observed, manifest = reader.open_source_version_v2(
        source_ref=_ref(),
        catalog_config=tmp_path / "catalog.yaml",
        as_of_date="2026-10-21",
        expected_fiscal_year=2025,
        source_reader_receipt_version="2.2",
    )
    record = build_revenue_source_record_from_verified_read(
        source_ref=_ref(),
        read_receipt=observed,
        source_bytes=raw,
        source_manifest=manifest,
        source_candidate=_candidate(_ref(), manifest),
        as_of_date="2026-10-21",
        source_type="regulatory_filing",
        publisher="Official publisher",
        page_or_section="Revenue note",
    )
    assert record["published_date"] is None
    assert record["availability_evidence"]["basis"] == "current_verified_open"
    assert (
        source_information_eligibility(record, date(2026, 10, 21)).basis
        == "current_verified_open"
    )


def test_real_cwp_ff_rf_cold_catalog_offline_contract(tmp_path):
    """Opt-in exact three-checkout CLI chain, with synthetic state only."""
    import os

    cwp_text = os.environ.get("CWP_V2_CODE_ROOT")
    ff_text = os.environ.get("W02_FF_CODE_ROOT")
    if not cwp_text or not ff_text:
        pytest.skip("set CWP_V2_CODE_ROOT and W02_FF_CODE_ROOT for cross-repo contract")
    cwp = Path(cwp_text).resolve(strict=True)
    ff = Path(ff_text).resolve(strict=True)
    wiki = tmp_path / "isolated-wiki"
    (wiki / "companies").mkdir(parents=True)
    (wiki / "config").mkdir()
    (wiki / "config" / "source_catalog.yaml").write_text(
        'schema_version: "1.0"\ncatalog_dir: "${PROJECT_ROOT}/.source_catalog"\nroots:\n'
        '  - root_id: company_raw\n    kind: company_raw\n    path: "${PROJECT_ROOT}/companies"\n    priority: 10\n',
        encoding="utf-8",
    )
    master = wiki / ".source_catalog" / "security_master"
    master.mkdir(parents=True)
    record = {
        "schema_version": "1.0",
        "canonical_name": "騰訊控股",
        "market": "HK",
        "exchange": "HKEX",
        "ticker": "00700",
        "security_id": "00700",
        "aliases": ["TENCENT"],
        "identifiers": {"org_id": "w02-hk-1"},
        "active": True,
        "source_name": "hkexnews",
        "source_record_id": "w02-hk-1",
        "source_url": "https://www.hkex.com.hk/",
    }
    (master / "hk.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "market": "HK",
                "retrieved_at": "2026-10-21T00:00:00Z",
                "sources": [record["source_url"]],
                "record_count": 1,
                "records": [record],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    connection = wiki / "connection.json"
    connection.write_text(
        json.dumps({"schema_version": "1.0", "company_wiki_root": str(wiki)}),
        encoding="utf-8",
    )
    request = {
        "schema_version": "2.0",
        "company_query": "00700",
        "market": "HK",
        "document_kind": "semi_annual_report",
        "fiscal_year": 2026,
        "fiscal_period": "H1",
        "as_of_date": "2026-10-21",
        "filing_intent": "reuse_only",
        "companion_transcript": {
            "intent": "reuse_only",
            "fiscal_year": 2026,
            "fiscal_quarter": 2,
            "provider": "fmp",
        },
    }
    env = {
        **os.environ,
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(cwp / "src"),
    }
    result = subprocess.run(
        [
            sys.executable,
            str(Path(prep.__file__)),
            "--result-envelope",
            "--company-wiki-catalog-config",
            str(wiki / "config" / "source_catalog.yaml"),
            "--company-wiki-config",
            str(connection),
            "--filing-fetch-root",
            str(ff),
            "--timeout-seconds",
            "30",
        ],
        input=json.dumps(request),
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=50,
    )
    assert result.returncode == 3, result.stdout + result.stderr
    error = json.loads(result.stderr)
    assert error["upstream_cause"]["code"] in {
        "catalog_unavailable",
        "reader_unavailable",
    }
    assert error["producer_exit_code"] == 2
    assert error["upstream_cause"]["provider_started"] is False
    assert error["companion_observation"]["status"] == "not_run"
    assert error["companion_observation"]["fiscal_quarter"] == 2
    assert error["companion_observation"]["provider_requests"] == 0
    assert error["filing_fetch_result"]["transcript"] == error["companion_observation"]
    assert not list((wiki / "companies").rglob("*.pdf"))
    assert not (wiki / ".source_catalog" / "acquisition_attempts.jsonl").exists()


def test_companion_preserves_valid_request_budget_without_new_consumer_cap():
    payload = failed()
    payload["transcript"]["acquisition_limits"]["timeout_seconds"] = 1800
    assert (
        failure_observation(payload)["companion_observation"]["acquisition_limits"][
            "timeout_seconds"
        ]
        == 1800
    )


def normal_gap():
    value = failed()
    value.update(status="gap", calls=3)
    value["filing"] = {
        "status": "gap",
        "reason": "metadata_only_gap_plan",
        "gap_hash": "e" * 64,
        "download_events": 0,
    }
    value["transcript"] = {
        "status": "not_applicable",
        "reason": "filing_not_capture_ready",
        "retryable": False,
    }
    return value


def test_normal_gap_complete_result_is_preserved_without_error_retryable():
    payload = normal_gap()
    observed = failure_observation(payload)
    assert observed["filing_fetch_result"] == payload
    assert observed["companion_observation"] == payload["transcript"]


def test_undispatched_provider_is_an_intent_token_not_a_second_capability_list():
    payload = failed()
    payload["transcript"]["provider"] = "company_ir"
    assert (
        failure_observation(payload)["companion_observation"] == payload["transcript"]
    )
    assert failure_observation(payload)["filing_fetch_result"] == payload


@pytest.mark.parametrize(
    "change",
    [
        {"gap_hash": "bad"},
        {"download_events": 1},
        {"download_events": False},
        {"path": "hidden/source.pdf"},
        {"unknown": "opaque"},
    ],
)
def test_normal_gap_shape_does_not_admit_invalid_or_physical_fields(change):
    payload = normal_gap()
    payload["filing"].update(change)
    assert "filing_fetch_result" not in failure_observation(payload)


@pytest.mark.parametrize(
    "provider", ["https://private/provider", "FMP", "a", {"name": "fmp"}]
)
def test_undispatched_provider_still_follows_published_ff_token_syntax(provider):
    payload = failed()
    payload["transcript"]["provider"] = provider
    assert "companion_observation" not in failure_observation(payload)
