"""P5-RF: the production source-preparation default is SourceRef v2.

Pins, without any opt-in flag:
- the default entry always requests a pathless SourceRef from filing-fetch;
- a missing/unavailable catalog config fails with a named error BEFORE any
  outbound subprocess;
- the legacy body-reading path (select_artifact_roles/verify_artifact_reads)
  is never invoked by the production default;
- the reuse receipt keeps honest null/empty semantics (artifact_read == []).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import source_preparation as sp  # noqa: E402

REQUEST = {
    "schema_version": "1.1",
    "company_query": "Acme",
    "document_kind": "annual_report",
    "fiscal_year": 2025,
    "as_of_date": "2026-09-27",
    "fiscal_period": None,
}
SHA = "a" * 64


def _v2_handle() -> dict:
    return {
        "source_ref": {
            "schema_version": "2.0",
            "document_id": "doc-1",
            "source_id": "src-1",
            "content_sha256": SHA,
            "byte_size": 3,
            "mime_type": "application/pdf",
        },
        "document_kind": "annual_report",
        "fiscal_year": 2025,
        "fiscal_period": None,
        "provider": "company-wiki",
        "prompt_injection_status": None,
        "resolution_outcome": "reused_existing",
        "download_events": 0,
    }


def _patch_v2_read(monkeypatch):
    """Patch the verified reader + builder at their module attributes."""
    import company_wiki_source_reader_v2 as reader_v2
    import company_wiki_source_v2 as builder_v2

    captured = {}

    def fake_open(**kwargs):
        captured.update(kwargs)
        return (
            b"PDF",
            {
                "schema_version": "2.1",
                "status": "ok",
                "document_id": "doc-1",
                "source_id": "src-1",
                "content_sha256": SHA,
                "byte_size": 3,
                "policy_sha256": "b" * 64,
                "source_read_policy_sha256": "c" * 64,
            },
            {"keep": True},
        )

    def fake_builder(**kwargs):  # noqa: ARG001
        return {
            "source_id": "src-1",
            "source_sha256": SHA,
            "capture": {"prompt_injection_status": None},
        }

    monkeypatch.setattr(reader_v2, "open_source_version_v2", fake_open)
    monkeypatch.setattr(
        builder_v2,
        "build_revenue_source_record_from_verified_read",
        fake_builder,
    )
    return captured


def _tripwire_legacy(monkeypatch):
    import company_wiki_source as cws

    def _blocked(*args, **kwargs):  # noqa: ARG001
        raise AssertionError(
            "legacy body reader reached from the production default path"
        )

    monkeypatch.setattr(cws, "select_artifact_roles", _blocked)
    monkeypatch.setattr(cws, "verify_artifact_reads", _blocked)


def _config(tmp_path) -> Path:
    config = tmp_path / "source_catalog.yaml"
    config.write_text("schema_version: '1.0'\n", encoding="utf-8")
    return config


def test_default_entry_uses_source_ref_v2_without_opt_in(monkeypatch, tmp_path):
    """No legacy flag is passed: the default production entry must drive the
    SourceRef v2 route and never touch the legacy body reader."""
    _tripwire_legacy(monkeypatch)
    captured = _patch_v2_read(monkeypatch)
    calls = {"command": None}

    def fake_run(command, **kwargs):  # noqa: ARG001
        calls["command"] = list(command)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(_v2_handle()),
            stderr="",
        )

    monkeypatch.setattr(sp.subprocess, "run", fake_run)
    record = sp.prepare_source(
        REQUEST,
        company_wiki_catalog_config=_config(tmp_path),
    )
    assert record["source_id"] == "src-1"
    assert record["reuse_receipt"]["outcome"] == "reused_existing"
    # the exact same verified SourceRef opened by the reader
    assert captured["source_ref"] == _v2_handle()["source_ref"]
    assert captured["catalog_config"].is_file()
    # the FF request asked for a pathless SourceRef, never a legacy envelope
    assert "--source-ref-v2" in calls["command"]


def test_legacy_reader_tripwire_and_forwarding(monkeypatch, tmp_path):
    """The legacy flag is a no-op; the FF command always carries
    --source-ref-v2 and explicit roots/forwards."""
    _tripwire_legacy(monkeypatch)
    captured = _patch_v2_read(monkeypatch)
    seen = {}

    def fake_run(command, **kwargs):  # noqa: ARG001
        seen["command"] = list(command)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(_v2_handle()),
            stderr="",
        )

    monkeypatch.setattr(sp.subprocess, "run", fake_run)
    first = sp.prepare_source(
        REQUEST,
        company_wiki_catalog_config=_config(tmp_path),
        allow_download=True,
        filing_fetch_root=Path("X"),
    )
    assert captured["source_ref"] == _v2_handle()["source_ref"]
    assert "--allow-download" in seen["command"]
    assert "--filing-fetch-root" in seen["command"]
    assert "--source-ref-v2" in seen["command"]
    again = sp.prepare_source(
        REQUEST,
        company_wiki_catalog_config=_config(tmp_path),
        source_reader_v2=True,
    )
    assert again == first


def test_missing_catalog_config_fails_named_before_outbound(monkeypatch):
    """A missing company_wiki_catalog_config is a named failure raised BEFORE
    any outbound subprocess/network/download may happen."""

    def fake_run(*args, **kwargs):  # noqa: ARG001
        raise AssertionError("subprocess spawned despite missing config")

    monkeypatch.setattr(sp.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="company_wiki_catalog_config"):
        sp.prepare_source(REQUEST)
    assert True


def test_unavailable_catalog_config_fails_named(monkeypatch, tmp_path):
    absent = tmp_path / "does-not-exist.yaml"

    def fake_run(*args, **kwargs):  # noqa: ARG001
        raise AssertionError("subprocess spawned despite broken config")

    monkeypatch.setattr(sp.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="catalog config"):
        sp.prepare_source(REQUEST, company_wiki_catalog_config=absent)


def test_default_reuse_receipt_keeps_honest_empty_semantics(
    monkeypatch,
    tmp_path,
):
    _tripwire_legacy(monkeypatch)
    _patch_v2_read(monkeypatch)

    def fake_run(command, **kwargs):  # noqa: ARG001
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(_v2_handle()),
            stderr="",
        )

    monkeypatch.setattr(sp.subprocess, "run", fake_run)
    record = sp.prepare_source(
        REQUEST,
        company_wiki_catalog_config=_config(tmp_path),
    )
    receipt = record["reuse_receipt"]
    # no legacy artifact-body read may be claimed: artifact_read cannot be a
    # storage-path reference; parser/LLM stay honest-None without real usage
    assert receipt["artifact_read"] == []
    assert receipt["producer_events"] == []
    assert receipt["artifact_read_events"] == []
    assert receipt["artifact_failed_events"] == []
    assert receipt["parser_calls"] is None
    assert receipt["llm_calls"] is None
    assert receipt["download_calls"] == 0
    assert receipt["outcome"] == "reused_existing"


def test_repeated_default_preparation_dedupes_demand(monkeypatch, tmp_path):
    _tripwire_legacy(monkeypatch)
    _patch_v2_read(monkeypatch)

    def fake_run(command, **kwargs):  # noqa: ARG001
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(_v2_handle()),
            stderr="",
        )

    monkeypatch.setattr(sp.subprocess, "run", fake_run)
    for _ in range(2):
        record = sp.prepare_source(
            REQUEST,
            company_wiki_catalog_config=_config(tmp_path),
        )
        assert record["reuse_receipt"]["outcome"] == "reused_existing"
    demands = sp.preparation_demands().snapshot()
    # the process-level queue is shared across tests: pin dedupe for THIS key
    assert [d.key for d in demands].count("src-1") == 1
    assert demands[-1].key == "src-1"
    assert demands[-1].kind == "source_preparation"


def test_cli_default_forwards_catalog_config_and_tolerates_legacy_flag(
    monkeypatch,
    tmp_path,
):
    """The CLI must forward the catalog config; passing --source-reader-v2
    stays accepted as a compatibility no-op."""
    captured = {}

    def fake_prepare(request, **kwargs):
        captured.update(kwargs)
        return {"ok": request["company_query"]}

    monkeypatch.setattr(sp, "prepare_source", fake_prepare)
    request_path = tmp_path / "req.json"
    request_path.write_text(json.dumps(REQUEST), encoding="utf-8")
    config = _config(tmp_path)
    exit_code = sp.main(
        [
            "--request-file",
            str(request_path),
            "--company-wiki-catalog-config",
            str(config),
            "--source-reader-v2",
        ]
    )
    assert exit_code == 0
    assert captured["company_wiki_catalog_config"] == config
    assert captured["source_reader_v2"] is True


def test_legacy_helper_is_isolated_non_production_fixture_entry(monkeypatch):
    """The legacy envelope parser survives only as an isolated fixture entry
    for historical offline replay; it is not reachable from the default path."""
    import company_wiki_source as cws

    monkeypatch.setattr(cws, "select_artifact_roles", lambda handle: ([], []))
    monkeypatch.setattr(
        cws,
        "verify_artifact_reads",
        lambda handle, read: {"verified_read_events": [], "failed_read_events": []},
    )
    monkeypatch.setattr(
        cws,
        "build_revenue_source_record",
        lambda handle, **kwargs: {"request_id": handle["request_id"]},
    )
    handle = {
        "request_id": "r1",
        "resolution_envelope": {
            "outcome": "reused_existing",
            "download_events": 0,
            "policy_hash": "a" * 64,
            "activation_epoch": "epoch-1",
            "bundle_status": "available",
            "prompt_injection_status": "not_detected",
            "parser_calls": 0,
            "llm_calls": 0,
        },
        "document_kind": "annual_report",
        "provider": "cninfo",
    }
    record = sp._prepare_legacy_source(REQUEST, handle)
    assert record["reuse_receipt"]["outcome"] == "reused_existing"
    assert record["reuse_receipt"]["download_calls"] == 0


@pytest.mark.parametrize("field,value,reason", [("fiscal_year", 2024, "fiscal_year_mismatch"),
    ("document_kind", "quarterly_report", "document_kind_mismatch"),
    ("fiscal_period", "Q1", "fiscal_period_mismatch")])
def test_default_failure_keeps_error_semantics_for_bad_candidate(
    monkeypatch,
    tmp_path,
    field,
    value,
    reason,
):
    _tripwire_legacy(monkeypatch)
    captured = _patch_v2_read(monkeypatch)
    bad = _v2_handle()
    bad[field] = value

    def fake_run(command, **kwargs):  # noqa: ARG001
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(bad),
            stderr="",
        )

    monkeypatch.setattr(sp.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match=reason.replace("_mismatch", " mismatch")) as caught:
        sp.prepare_source(REQUEST, company_wiki_catalog_config=_config(tmp_path))
    assert caught.value.source_failure_reason == reason
    assert caught.value.stage == "source_reader"
    assert caught.value.calls is None and caught.value.downloads is None
    assert captured == {}, "a mismatched candidate must be refused before verified opening"
