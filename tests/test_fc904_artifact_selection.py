"""FC-904 RED/acceptance tests: source_preparation consumes the artifact
SCENARIO: AR-01 AR-02 AR-03 UJ-06 UJ-08
selector (DAG-minimal) from the envelope bundle.

The unsourced ``payload.get("selected_artifacts", [])`` path is removed: the
reuse receipt derives ``artifact_read`` (roles with a verified artifact in
the FC-902 envelope bundle's valid_handles) and ``producer_events`` (DAG
closure over the non-reusable roles — never a blind full recompute).

RED phase: ``select_artifact_roles`` does not exist and the receipt still
carries the unsourced ``selected_artifacts`` default.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pytest  # noqa: E402

from company_wiki_source import (  # noqa: E402
    CompanyWikiSourceError,
    select_artifact_roles,
)


def _handle(bundle=None, **envelope_overrides) -> dict:
    envelope = {
        "envelope_schema_version": "1.0",
        "outcome": "reused_existing",
        "download_events": 0,
        "policy_hash": "a" * 64,
        "activation_epoch": "epoch-1",
        "bundle_status": "unavailable",
    }
    if bundle is not None:
        envelope["bundle_status"] = "available"
        envelope["bundle_hash"] = bundle["bundle_hash"]
        envelope["bundle"] = bundle
    envelope.update(envelope_overrides)
    return {"request_id": "r1", "resolution_envelope": envelope}


def _bundle(valid: dict, invalid: dict | None = None) -> dict:
    return {
        "schema_version": "1.0",
        "source": {"document_id": "doc-1", "primary_source_id": "src-1",
                   "source_sha256": "c" * 64, "as_of_date": "2025-12-31"},
        "valid_handles": valid,
        "invalid": invalid or {},
        "bundle_hash": "d" * 64,
    }


def _artifact(**overrides) -> dict:
    base = {"artifact_role": "normalized", "reusable": True,
            "content_sha256": "e" * 64, "generator_name": "g",
            "generator_version": "1.0"}
    base.update(overrides)
    return base


ALL_ROLES = ("normalized", "markdown", "summary", "sections",
             "consumer_analysis")


# --- AR-01: valid artifacts are read, producers do not run --------------------


def test_ar01_valid_roles_read():
    """Every role with a verified artifact (and DAG-valid ancestors) is read;
    with all five roles reusable nothing is produced (parser/LLM=0)."""
    bundle = _bundle(valid={
        "normalized": _artifact(artifact_role="normalized"),
        "markdown": _artifact(artifact_role="markdown"),
        "summary": _artifact(artifact_role="summary"),
        "sections": _artifact(artifact_role="sections"),
        "consumer_analysis": _artifact(artifact_role="consumer_analysis"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert read == sorted(ALL_ROLES)
    assert produced == []


# --- AR-02: only the missing role + its DAG dependents are produced -----------


def test_ar02_only_summary_missing():
    """summary absent -> producer_events = DAG closure of summary
    (summary + consumer_analysis); the other roles are read unchanged."""
    bundle = _bundle(valid={
        "normalized": _artifact(artifact_role="normalized"),
        "markdown": _artifact(artifact_role="markdown"),
        "sections": _artifact(artifact_role="sections"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert set(read) == {"normalized", "markdown", "sections"}
    assert produced == ["consumer_analysis", "summary"]


# --- AR-03: normalized missing -> DAG invalidation of its dependents ----------


def test_ar03_normalized_missing_dag_invalidation():
    """normalized not reusable -> every role deriving from it needs
    production (the DAG closure), never a blind recompute of valid siblings."""
    bundle = _bundle(valid={
        "markdown": _artifact(artifact_role="markdown"),
        "summary": _artifact(artifact_role="summary"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert read == []
    assert produced == sorted(ALL_ROLES)


# --- AR-04: nothing reusable -> everything produced ---------------------------


def test_ar04_nothing_reusable():
    bundle = _bundle(valid={}, invalid={
        "normalized": _artifact(reusable=False, reason="artifact_hash_mismatch"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert read == []
    assert produced == sorted(ALL_ROLES)


# --- AR-05: tampered artifact is never read -----------------------------------


def test_ar05_tampered_not_read_fail_closed():
    bundle = _bundle(valid={
        "normalized": _artifact(artifact_role="normalized"),
    }, invalid={
        "summary": _artifact(artifact_role="summary", reusable=False,
                             reason="artifact_hash_mismatch"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert read == ["normalized"]
    assert "summary" in produced and "consumer_analysis" in produced


# --- AR-06: consumer_analysis provenance mismatch -----------------------------


def test_ar06_consumer_analysis_provenance_mismatch():
    """A consumer_analysis artifact whose engine/model/prompt/input_bundle_hash
    differ from the expected values is NOT read; base markdown (with a valid
    normalized ancestor) continues to be read."""
    bundle = _bundle(valid={
        "normalized": _artifact(artifact_role="normalized"),
        "markdown": _artifact(artifact_role="markdown"),
        "consumer_analysis": _artifact(
            artifact_role="consumer_analysis",
            engine="e1", model="m1", prompt="p1", input_bundle_hash="h1"),
    })
    read, produced = select_artifact_roles(
        _handle(bundle),
        expected_provenance={"engine": "e2", "model": "m2", "prompt": "p2",
                             "input_bundle_hash": "h2"},
    )
    assert read == ["markdown", "normalized"]
    assert "consumer_analysis" in produced


# --- AR-08: legacy_unbound is never trusted -----------------------------------


def test_ar08_legacy_unbound_not_reused():
    bundle = _bundle(valid={}, invalid={
        "normalized": _artifact(artifact_role="normalized", reusable=False,
                                reason="artifact_schema_unsupported"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert read == []
    assert "normalized" in produced


# --- bundle unavailable -> everything must be produced ------------------------


def test_no_bundle_all_produced():
    read, produced = select_artifact_roles(_handle(bundle=None))
    assert read == []
    assert produced == sorted(ALL_ROLES)


# --- fail closed: malformed bundle raises -------------------------------------


def test_malformed_bundle_raises():
    def handle_with(bundle):
        envelope = {
            "envelope_schema_version": "1.0", "outcome": "reused_existing",
            "download_events": 0, "policy_hash": "a" * 64,
            "activation_epoch": "epoch-1", "bundle_status": "available",
            "bundle_hash": "d" * 64, "bundle": bundle,
        }
        return {"request_id": "r1", "resolution_envelope": envelope}

    with pytest.raises(CompanyWikiSourceError):
        select_artifact_roles(handle_with("not-a-dict"))
    with pytest.raises(CompanyWikiSourceError):
        select_artifact_roles(handle_with(_bundle(valid="not-a-dict")))


# --- prepare_source: receipt is SOURCED, unsourced path removed ---------------


def test_prepare_source_receipt_sourced_from_bundle(monkeypatch, tmp_path):
    """The reuse receipt's artifact_read/producer_events derive from the
    envelope bundle — and the unsourced 'selected_artifacts' key is GONE."""
    from source_preparation import prepare_source
    import company_wiki_source as cws

    bundle = _bundle(valid={
        "normalized": _artifact(artifact_role="normalized"),
        "markdown": _artifact(artifact_role="markdown"),
        "summary": _artifact(artifact_role="summary"),
    })
    envelope = {
        "envelope_schema_version": "1.0", "outcome": "reused_existing",
        "download_events": 0, "policy_hash": "a" * 64,
        "activation_epoch": "epoch-1", "bundle_status": "available",
        "bundle_hash": bundle["bundle_hash"], "bundle": bundle,
        "prompt_injection_status": "not_detected",
        "parser_calls": 0, "llm_calls": 0,
    }
    payload = {"request_id": "r1", "resolution_envelope": envelope}

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0], returncode=0,
            stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        cws, "build_revenue_source_record",
        lambda handle, **kwargs: {"request_id": handle.get("request_id", "r1")},
    )
    record = prepare_source({"company_query": "Acme",
                             "document_kind": "annual_report",
                             "as_of_date": "2026-12-31"})
    receipt = record["reuse_receipt"]
    assert "selected_artifacts" not in receipt       # unsourced path removed
    assert receipt["artifact_read"] == ["markdown", "normalized", "summary"]
    assert receipt["producer_events"] == ["consumer_analysis", "sections"]


def test_prepare_source_unavailable_envelope_all_produced(monkeypatch):
    """bundle_status=unavailable -> artifact_read=[] and every role needs
    production (honest, not faked)."""
    from source_preparation import prepare_source
    import company_wiki_source as cws

    envelope = {
        "envelope_schema_version": "1.0", "outcome": "reused_existing",
        "download_events": 0, "policy_hash": "a" * 64,
        "activation_epoch": "epoch-1", "bundle_status": "unavailable",
        "prompt_injection_status": "not_detected",
        "parser_calls": 0, "llm_calls": 0,
    }
    payload = {"request_id": "r1", "resolution_envelope": envelope}

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0], returncode=0,
            stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        cws, "build_revenue_source_record",
        lambda handle, **kwargs: {"request_id": handle.get("request_id", "r1")},
    )
    record = prepare_source({"company_query": "Acme",
                             "document_kind": "annual_report",
                             "as_of_date": "2026-12-31"})
    receipt = record["reuse_receipt"]
    assert receipt["artifact_read"] == []
    assert receipt["producer_events"] == sorted(ALL_ROLES)
