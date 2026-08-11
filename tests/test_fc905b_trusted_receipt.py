"""FC-905-b RED/acceptance tests: source_preparation consumes trusted
capture/safety evidence from the envelope.

The hardcoded `prompt_injection_status="not_detected"` and
`parser_calls: 0, llm_calls: 0` must be GONE:

- prompt_injection_status comes from the envelope; `not_reviewed` BLOCKS
  (RuntimeError) — an unreviewed source is never prepared.
- parser_calls/llm_calls come from the envelope; absent (None) FAILS CLOSED —
  never fabricated as 0.
- input/source/artifact hash, model/prompt and schema tampering each trigger
  minimal invalidation (the role is never read; DAG-minimal producer events).

RED phase: the envelope fields are ignored / hardcoded values remain.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pytest  # noqa: E402

from company_wiki_source import CompanyWikiSourceError, select_artifact_roles  # noqa: E402


def _envelope(**overrides) -> dict:
    envelope = {
        "envelope_schema_version": "1.0",
        "outcome": "reused_existing",
        "download_events": 0,
        "policy_hash": "a" * 64,
        "activation_epoch": "epoch-1",
        "bundle_status": "unavailable",
        "prompt_injection_status": "not_detected",
        "parser_calls": 0,
        "llm_calls": 0,
    }
    envelope.update(overrides)
    return envelope


def _run(monkeypatch, envelope, *, record_extra=None):
    from source_preparation import prepare_source
    import company_wiki_source as cws

    payload = {"request_id": "r1", "resolution_envelope": envelope}

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0], returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    calls = {}

    def fake_record(handle, **kwargs):
        calls["kwargs"] = kwargs
        return {"request_id": handle.get("request_id", "r1")}

    monkeypatch.setattr(cws, "build_revenue_source_record", fake_record)
    record = prepare_source({"company_query": "Acme",
                             "document_kind": "annual_report",
                             "as_of_date": "2026-12-31"})
    return record, calls


# --- PI-B1: not_reviewed blocks (never prepared) ------------------------------


def test_b1_not_reviewed_blocks(monkeypatch):
    with pytest.raises(RuntimeError, match="not reviewed|blocked"):
        _run(monkeypatch, _envelope(prompt_injection_status="not_reviewed"))


def test_b2_missing_status_blocks_defensively(monkeypatch):
    """A defensive N-1 envelope without the field is treated as not_reviewed
    -> blocked (filing-fetch normalizes N-1 upstream; revenue never assumes)."""
    envelope = _envelope()
    del envelope["prompt_injection_status"]
    with pytest.raises(RuntimeError, match="not reviewed|blocked"):
        _run(monkeypatch, envelope)


# --- PI-B3: reviewed status passes through to the capture record --------------


def test_b3_reviewed_status_forwarded(monkeypatch):
    record, calls = _run(
        monkeypatch, _envelope(prompt_injection_status="detected_and_ignored"))
    assert calls["kwargs"]["prompt_injection_status"] == "detected_and_ignored"
    assert record["reuse_receipt"]["prompt_injection_status"] == (
        "detected_and_ignored")


# --- PI-B4: parser/llm counts come from the envelope --------------------------


def test_b4_counts_from_envelope(monkeypatch):
    record, _ = _run(monkeypatch, _envelope(parser_calls=2, llm_calls=1))
    assert record["reuse_receipt"]["parser_calls"] == 2
    assert record["reuse_receipt"]["llm_calls"] == 1


def test_b5_counts_absent_fail_closed(monkeypatch):
    """None counts -> RuntimeError, never fabricated as 0."""
    with pytest.raises(RuntimeError, match="parser|llm|counts"):
        _run(monkeypatch, _envelope(parser_calls=None))
    with pytest.raises(RuntimeError, match="parser|llm|counts"):
        _run(monkeypatch, _envelope(llm_calls=None))


# --- PI-B6: tampering triggers minimal invalidation ---------------------------


def _bundle(valid: dict, invalid: dict | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "source": {"document_id": "doc-1", "primary_source_id": "src-1",
                   "source_sha256": "c" * 64, "as_of_date": "2025-12-31"},
        "valid_handles": valid,
        "invalid": invalid or {},
        "bundle_hash": "d" * 64,
    }


def _handle(bundle) -> dict:
    return {"request_id": "r1", "resolution_envelope": {
        "envelope_schema_version": "1.0", "outcome": "reused_existing",
        "download_events": 0, "policy_hash": "a" * 64,
        "activation_epoch": "epoch-1", "bundle_status": "available",
        "bundle_hash": bundle["bundle_hash"], "bundle": bundle}}


def _artifact(**overrides) -> dict:
    base = {"artifact_role": "normalized", "reusable": True,
            "content_sha256": "e" * 64, "generator_name": "g",
            "generator_version": "1.0"}
    base.update(overrides)
    return base


def test_b6_tampered_roles_never_read_minimal_invalidation():
    """Each tamper type removes the role from artifact_read while the DAG
    keeps the read set minimal (valid siblings stay read)."""
    # model/prompt tamper -> consumer_analysis not read (its DAG closure
    # [consumer_analysis] produced); the other four roles stay read
    bundle = _bundle(valid={
        "normalized": _artifact(artifact_role="normalized"),
        "markdown": _artifact(artifact_role="markdown"),
        "summary": _artifact(artifact_role="summary"),
        "sections": _artifact(artifact_role="sections"),
        "consumer_analysis": _artifact(
            artifact_role="consumer_analysis", engine="e1", model="m1",
            prompt="p1", input_bundle_hash="h1"),
    })
    read, produced = select_artifact_roles(
        _handle(bundle),
        expected_provenance={"engine": "e1", "model": "m2", "prompt": "p1",
                             "input_bundle_hash": "h1"})
    assert read == ["markdown", "normalized", "sections", "summary"]
    assert produced == ["consumer_analysis"]
    # source-hash tamper -> the artifact is invalid in the bundle -> never
    # read; the role + its DAG dependents are produced
    bundle2 = _bundle(valid={}, invalid={
        "normalized": _artifact(artifact_role="normalized", reusable=False,
                                reason="artifact_source_sha_mismatch"),
    })
    read2, produced2 = select_artifact_roles(_handle(bundle2))
    assert read2 == []
    assert "normalized" in produced2
    # schema tamper -> legacy_unbound-style rejection
    bundle3 = _bundle(valid={}, invalid={
        "summary": _artifact(artifact_role="summary", reusable=False,
                             reason="artifact_schema_unsupported"),
    })
    read3, produced3 = select_artifact_roles(_handle(bundle3))
    assert "summary" not in read3
    assert "consumer_analysis" in produced3 and "summary" in produced3
    # malformed bundle never trusted
    bad = {"request_id": "r1", "resolution_envelope": {
        "envelope_schema_version": "1.0", "outcome": "reused_existing",
        "download_events": 0, "bundle_status": "available",
        "bundle_hash": "d" * 64, "bundle": "not-a-dict"}}
    with pytest.raises(CompanyWikiSourceError):
        select_artifact_roles(bad)
