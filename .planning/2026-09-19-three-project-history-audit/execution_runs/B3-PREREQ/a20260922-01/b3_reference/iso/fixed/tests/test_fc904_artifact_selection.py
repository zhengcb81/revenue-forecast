"""FC-904 acceptance tests — B3 production-bound rerun carrier.

This is the production `revenue-forecast/tests/test_fc904_artifact_selection.py`
verbatim, re-hosted inside the B3-I05C-delivery-fixes attempt so that a single
prepended block can bind the module under test to THIS attempt's remediated
copy of `scripts/company_wiki_source.py` (REM-11 + REM-13).

Reason for re-hosting rather than editing in place: production repos are
read-only for this card, and the FC-904 file is a frozen acceptance test.  The
only difference from the original is the marked "B3 binding" block plus the
`TestB3ProductionProvenance` class at the end; every assertion of the original
is preserved byte-for-byte in spirit and unmodified in content.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# B3 binding (added by B3-I05C-delivery-fixes a20260921-01) — binds the module
# under test explicitly instead of relying on sys.path search order.
#   B3_BYTES: unset/"fixed" -> attempt-local remediated copy (default)
#             "production"  -> current production repo file
# ---------------------------------------------------------------------------
_ISO_ROOT = Path(__file__).resolve().parents[1]
_ATTEMPT_ROOT = _ISO_ROOT.parent
_RF_ROOT = Path("C:/Users/郑曾波/Projects/revenue-forecast")
_CW_ROOT = Path("C:/Users/郑曾波/Projects/company-wiki")
_FIXED_CWS = _ISO_ROOT / "rf_scripts" / "company_wiki_source.py"
_FIXED_SP = _ISO_ROOT / "rf_scripts" / "source_preparation.py"
_BYTES = os.environ.get("B3_BYTES", "fixed").strip().lower()
if _BYTES == "fixed":
    _TARGET_CWS, _TARGET_SP = _FIXED_CWS, _FIXED_SP
elif _BYTES == "production":
    _TARGET_CWS = _RF_ROOT / "scripts" / "company_wiki_source.py"
    _TARGET_SP = _RF_ROOT / "scripts" / "source_preparation.py"
else:
    raise RuntimeError(f"B3_BYTES must be 'fixed' or 'production', got {_BYTES!r}")

# `source_preparation.py` imports `company_wiki.source_catalog.artifact_dag`,
# whose single source of truth is the CW repo.  In the FIXED run that package
# resolves through the attempt-local skeleton copied from production; in the
# PRODUCTION run it must come from the CW repo itself.
for _entry in (str(_RF_ROOT / "scripts"), str(_CW_ROOT / "src"),
               str(_ISO_ROOT / "rf_scripts"),
               str(_ISO_ROOT / "cw_source_catalog")):
    while _entry in sys.path:
        sys.path.remove(_entry)
if _BYTES == "fixed":
    _PATH_ENTRIES = (str(_ISO_ROOT / "rf_scripts"), str(_CW_ROOT / "src"))
else:
    _PATH_ENTRIES = (str(_RF_ROOT / "scripts"), str(_CW_ROOT / "src"))
for _entry in _PATH_ENTRIES:
    sys.path.insert(0, _entry)
sys.path_importer_cache.clear()


def _bind_module(module_name: str, origin: Path):
    """Import ``module_name`` from ``origin`` regardless of path search order."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, origin)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"B3 binding failed: no loader for {origin}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_BOUND_CWS = _bind_module("company_wiki_source", _TARGET_CWS)
# source_preparation imports company_wiki_source at module level, so binding it
# second means it picks up the module already registered above.
_BOUND_SP = _bind_module("source_preparation", _TARGET_SP)

for _name, _module, _expected in (
        ("company_wiki_source", _BOUND_CWS, _TARGET_CWS),
        ("source_preparation", _BOUND_SP, _TARGET_SP)):
    _actual = Path(_module.__file__).resolve()
    if _actual != Path(_expected).resolve():
        raise RuntimeError(
            f"B3 binding failed: {_name} binds to {_actual}, expected "
            f"{Path(_expected).resolve()} (REM-12).")
_BOUND_SHA256 = hashlib.sha256(
    Path(_BOUND_CWS.__file__).resolve().read_bytes()).hexdigest().upper()

# ---------------------------------------------------------------------------
# original FC-904 test body (verbatim)
# ---------------------------------------------------------------------------

ROOT = Path("C:/Users/郑曾波/Projects/revenue-forecast")
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


# ---------------------------------------------------------------------------
# B3 production-provenance proofs (added by B3-I05C-delivery-fixes)
# ---------------------------------------------------------------------------

PRODUCTION_CWS_SHA256 = (
    "225FECDD7E48938A97C68724318F0860602A4B86A8D9E834A257243480094294")
FIXED_CWS_SHA256 = (
    "7D1BD8F9D9122DC4A99465A8F9201E855417A5D0756F5BFDD6D404F7CA9E48CE")

class TestB3ProductionProvenance:
    """REM-12: prove WHICH bytes this suite executed, and prove the frozen
    FC-904 file in the production repo was not modified to make them pass."""

    def test_module_under_test_is_the_bound_copy(self):
        resolved = Path(_BOUND_CWS.__file__).resolve()
        expected = Path(_TARGET_CWS).resolve()
        assert resolved == expected
        assert "B3-I05C-delivery-fixes" in str(resolved) or _BYTES == "production"

    def test_bound_bytes_match_the_declared_hash(self):
        assert _BOUND_SHA256 == (
            FIXED_CWS_SHA256 if _BYTES == "fixed" else PRODUCTION_CWS_SHA256)

    def test_source_preparation_uses_the_bound_module(self):
        import source_preparation as sp
        import company_wiki_source as cws

        assert Path(sp.__file__).resolve() == Path(_TARGET_SP).resolve()
        assert cws is _BOUND_CWS

    def test_production_fc904_file_was_not_edited(self):
        """The frozen production acceptance test must be byte-identical to the
        recorded hash: this card fixed the implementation, not the test."""
        production = Path(
            "C:/Users/郑曾波/Projects/revenue-forecast/tests/"
            "test_fc904_artifact_selection.py")
        actual = hashlib.sha256(production.read_bytes()).hexdigest().upper()
        assert actual == (
            "8C0B8E390307C33B8C03D51FD742CA984BA6774B84638500FD8D7CDD7D46BF3F")

    def test_fc904_no_bundle_assertion_is_the_unchanged_default_scope(self):
        """D1a: FC-904's `test_no_bundle_all_produced` passes because the
        DEFAULT request names all five roles — not because the no-bundle branch
        is a global all-roles constant.  Pin both readings here so the
        distinction cannot be lost."""
        read, produced = select_artifact_roles(_handle(bundle=None))
        assert read == []
        assert produced == sorted(ALL_ROLES)

        # ...and the subset request is scoped, which the old branch got wrong
        read2, produced2 = select_artifact_roles(
            _handle(bundle=None), roles=("normalized",))
        assert read2 == []
        assert produced2 == ["normalized"]
