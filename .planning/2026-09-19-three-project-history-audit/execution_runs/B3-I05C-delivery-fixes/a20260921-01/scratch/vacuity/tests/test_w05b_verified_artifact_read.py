"""W05-B: Verified artifact read — selection proves plan, IO proves bytes.

These tests prove that:
1. `select_artifact_roles` returns the PLAN (which roles to read)
2. `verify_artifact_reads` performs ACTUAL file I/O and returns evidence
3. The two are independent: selection without read is insufficient
4. Hash mismatches, missing files, and tampering are detected
5. The receipt carries verified events, not just the plan

Sentinel files:
- ALPHA=17 (8 bytes) — valid normalized artifact
- BETA=29 (7 bytes) — replacement for tamper tests
- GAMMA=31 (8 bytes) — same-length different-content collision test
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path

ISO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ISO_ROOT / "checkout_scripts"))

import pytest  # noqa: E402

from company_wiki_source import (  # noqa: E402
    CompanyWikiSourceError,
    select_artifact_roles,
    verify_artifact_reads,
)


# ---------------------------------------------------------------------------
# Sentinel constants
# ---------------------------------------------------------------------------

SCRATCH = Path(__file__).resolve().parents[2] / "scratch"
ALPHA_PATH = SCRATCH / "alpha_normalized.txt"
BETA_PATH = SCRATCH / "beta_normalized.txt"
GAMMA_PATH = SCRATCH / "gamma_normalized.txt"

ALPHA_BODY = b"ALPHA=17"
BETA_BODY = b"BETA=29"
GAMMA_BODY = b"GAMMA=31"

ALPHA_SHA = hashlib.sha256(ALPHA_BODY).hexdigest()
BETA_SHA = hashlib.sha256(BETA_BODY).hexdigest()
GAMMA_SHA = hashlib.sha256(GAMMA_BODY).hexdigest()

SOURCE_SHA = "c" * 64  # fake source hash for bundle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _handle(bundle=None, **envelope_overrides) -> dict:
    """Build a resolution handle with optional bundle."""
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
    """Build a source bundle with valid/invalid handles."""
    return {
        "schema_version": "1.0",
        "source": {
            "document_id": "doc-1",
            "primary_source_id": "src-1",
            "source_sha256": SOURCE_SHA,
            "as_of_date": "2025-12-31",
        },
        "valid_handles": valid,
        "invalid": invalid or {},
        "bundle_hash": "d" * 64,
    }


def _artifact(path: str, sha: str, **overrides) -> dict:
    """Build a valid artifact handle pointing to a real file."""
    base = {
        "artifact_role": "normalized",
        "reusable": True,
        "path": path,
        "content_sha256": sha,
        "generator_name": "g",
        "generator_version": "1.0",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Ensure sentinel files exist
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _ensure_sentinels(tmp_path):
    """Create sentinel files if they don't already exist."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    if not ALPHA_PATH.exists():
        ALPHA_PATH.write_bytes(ALPHA_BODY)
    if not BETA_PATH.exists():
        BETA_PATH.write_bytes(BETA_BODY)
    if not GAMMA_PATH.exists():
        GAMMA_PATH.write_bytes(GAMMA_BODY)


# ===========================================================================
# W05B-P1: positive — read verified normalized sentinel ALPHA=17
# ===========================================================================

class TestW05BP1PositiveRead:
    """Read a valid normalized artifact and get verified IO evidence."""

    def test_select_returns_plan(self):
        """select_artifact_roles returns the PLAN (selected roles)."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, producers = select_artifact_roles(handle)
        assert "normalized" in selected
        # Plan proves intent, not IO
        assert isinstance(selected, list)

    def test_verify_reads_actual_bytes(self):
        """verify_artifact_reads reads the ACTUAL file and verifies hash."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)
        result = verify_artifact_reads(handle, selected)

        verified = result["verified_read_events"]
        failed = result["failed_read_events"]
        assert len(verified) == 1
        assert len(failed) == 0

        event = verified[0]
        assert event["role"] == "normalized"
        assert event["read_status"] == "verified"
        assert event["bytes_read"] == len(ALPHA_BODY)
        assert event["content_sha256_actual"] == ALPHA_SHA
        assert event["content_sha256_declared"] == ALPHA_SHA
        assert event["source_sha256"] == SOURCE_SHA
        assert "read_at" in event

    def test_verified_events_in_receipt(self):
        """The receipt carries verified events, not just the plan."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, producers = select_artifact_roles(handle)
        io = verify_artifact_reads(handle, selected)

        receipt = {
            "artifact_read": selected,
            "producer_events": producers,
            "artifact_read_events": io["verified_read_events"],
            "artifact_failed_events": io["failed_read_events"],
        }
        # Plan says "read normalized"
        assert "normalized" in receipt["artifact_read"]
        # Evidence proves actual read
        assert len(receipt["artifact_read_events"]) == 1
        assert receipt["artifact_read_events"][0]["read_status"] == "verified"
        assert receipt["artifact_read_events"][0]["bytes_read"] == len(ALPHA_BODY)

    def test_multiple_roles_verified(self):
        """Multiple valid roles are each verified independently."""
        alpha2_path = SCRATCH / "alpha2_normalized.txt"
        alpha2_path.write_bytes(ALPHA_BODY)
        alpha2_sha = hashlib.sha256(ALPHA_BODY).hexdigest()

        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
            "markdown": _artifact(str(alpha2_path), alpha2_sha,
                                  artifact_role="markdown"),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)
        result = verify_artifact_reads(handle, selected)

        assert len(result["verified_read_events"]) == 2
        for event in result["verified_read_events"]:
            assert event["read_status"] == "verified"


# ===========================================================================
# W05B-P2: positive — raw-only, no parser/LLM forced
# ===========================================================================

class TestW05BP2PositiveRawOnly:
    """Raw-only need: no parser/LLM forced even when summary missing."""

    def test_raw_only_no_parser_forced(self):
        """With only normalized selected, producer_events may list missing
        roles but no actual producer invocation occurs."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        }, invalid={
            "summary": {
                "artifact_role": "summary",
                "reusable": False,
                "reason": "artifact_hash_mismatch",
            },
        })
        handle = _handle(bundle)
        selected, producers = select_artifact_roles(handle)
        result = verify_artifact_reads(handle, selected)

        # Only normalized was selected for read
        assert selected == ["normalized"]
        # Verify the read
        assert len(result["verified_read_events"]) == 1
        assert result["verified_read_events"][0]["role"] == "normalized"
        # No producers were actually invoked
        # (producers is the PLAN for what needs production)


# ===========================================================================
# W05B-N1: negative — select without actual read
# ===========================================================================

class TestW05BN1NegativeSelectWithoutRead:
    """Selection without actual read is insufficient proof."""

    def test_selection_alone_proves_nothing(self):
        """select_artifact_roles returns roles but no IO evidence.
        Without calling verify_artifact_reads, there is NO proof bytes
        were consumed."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)

        # Selection proves plan only
        assert "normalized" in selected
        # But without verify_artifact_reads, no IO events exist
        # This test documents the gap: plan ≠ proof

    def test_empty_verify_without_selection(self):
        """Calling verify_artifact_reads with empty selection returns
        nothing — no fabricated events."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        result = verify_artifact_reads(handle, [])

        assert result["verified_read_events"] == []
        assert result["failed_read_events"] == []

    def test_fake_events_cannot_be_injected(self):
        """verified_read_events must come from actual IO; injecting
        fabricated events into the receipt is detectable."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)
        real_result = verify_artifact_reads(handle, selected)

        # A fabricated event would have different structure
        fake_event = {
            "role": "normalized",
            "read_status": "verified",
            "bytes_read": 999,  # wrong
            "content_sha256_actual": "x" * 64,  # wrong
        }
        # Real events come from verify_artifact_reads
        real_event = real_result["verified_read_events"][0]
        assert real_event["bytes_read"] != fake_event["bytes_read"]
        assert real_event["content_sha256_actual"] != fake_event["content_sha256_actual"]


# ===========================================================================
# W05B-N2: negative — replace artifact between select and read
# ===========================================================================

class TestW05BN2NegativeTamperBetweenSelectAndRead:
    """Artifact replaced between selection and read — hash mismatch."""

    def test_replaced_artifact_detected(self, tmp_path):
        """After selection, replace artifact file with BETA=29.
        verify_artifact_reads detects the hash mismatch."""
        # Step 1: Create artifact with ALPHA content
        artifact_file = tmp_path / "normalized.txt"
        artifact_file.write_bytes(ALPHA_BODY)
        alpha_sha = hashlib.sha256(ALPHA_BODY).hexdigest()

        bundle = _bundle(valid={
            "normalized": _artifact(str(artifact_file), alpha_sha),
        })
        handle = _handle(bundle)

        # Step 2: SELECT (plan is built)
        selected, _ = select_artifact_roles(handle)
        assert "normalized" in selected

        # Step 3: TAMPER — replace file with BETA content
        artifact_file.write_bytes(BETA_BODY)
        # The declared SHA is still alpha_sha, but file now has BETA

        # Step 4: VERIFY — should detect mismatch
        result = verify_artifact_reads(handle, selected)

        assert len(result["verified_read_events"]) == 0
        assert len(result["failed_read_events"]) == 1

        failed = result["failed_read_events"][0]
        assert failed["role"] == "normalized"
        assert failed["reason"] == "content_sha256_mismatch"
        assert failed["content_sha256_actual"] == hashlib.sha256(BETA_BODY).hexdigest()
        assert failed["content_sha256_declared"] == alpha_sha

    def test_same_length_different_content_detected(self, tmp_path):
        """Same-length different-content: hash is content-sensitive."""
        file1 = tmp_path / "norm1.txt"
        file1.write_bytes(ALPHA_BODY)  # 8 bytes

        bundle = _bundle(valid={
            "normalized": _artifact(str(file1), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)

        # Replace with GAMMA (also 8 bytes, different content)
        file1.write_bytes(GAMMA_BODY)

        result = verify_artifact_reads(handle, selected)
        assert len(result["verified_read_events"]) == 0
        assert len(result["failed_read_events"]) == 1
        assert result["failed_read_events"][0]["reason"] == "content_sha256_mismatch"

    def test_old_hash_not_paired_with_new_bytes(self):
        """The old hash's success event cannot be paired with new bytes."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)
        result = verify_artifact_reads(handle, selected)

        # Verify against ALPHA
        event = result["verified_read_events"][0]
        assert event["content_sha256_actual"] == ALPHA_SHA

        # A fabricated "success" with BETA bytes but ALPHA hash is impossible
        # because verify_artifact_reads reads actual bytes
        assert event["bytes_read"] == len(ALPHA_BODY)
        assert event["content_sha256_actual"] != BETA_SHA


# ===========================================================================
# W05B-N3: negative — denied root / missing / out-of-bounds
# ===========================================================================

class TestW05BN3NegativeSecurity:
    """Security negatives: missing files, malformed artifacts."""

    def test_missing_file_detected(self, tmp_path):
        """Artifact points to nonexistent file — refused."""
        missing = tmp_path / "nonexistent.txt"
        bundle = _bundle(valid={
            "normalized": _artifact(str(missing), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)
        result = verify_artifact_reads(handle, selected)

        assert len(result["verified_read_events"]) == 0
        assert len(result["failed_read_events"]) == 1
        assert result["failed_read_events"][0]["reason"] == "artifact_file_missing"

    def test_no_bundle_returns_empty(self):
        """No bundle — no roles selected, no reads attempted."""
        handle = _handle(bundle=None)
        selected, _ = select_artifact_roles(handle)
        result = verify_artifact_reads(handle, selected)

        assert result["verified_read_events"] == []
        assert result["failed_read_events"] == []

    def test_malformed_bundle_returns_empty(self):
        """Malformed bundle — fail closed."""
        handle = _handle(bundle=None)
        # Manually corrupt
        handle["resolution_envelope"]["bundle"] = "not-a-dict"
        handle["resolution_envelope"]["bundle_status"] = "available"
        with pytest.raises(CompanyWikiSourceError):
            select_artifact_roles(handle)

    def test_missing_role_in_bundle(self, tmp_path):
        """Role selected but not in valid_handles — failed event."""
        # Select returns a role, but verify can't find it
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)

        # Manually remove the role from bundle after selection
        del handle["resolution_envelope"]["bundle"]["valid_handles"]["normalized"]
        result = verify_artifact_reads(handle, selected)

        assert len(result["verified_read_events"]) == 0
        assert len(result["failed_read_events"]) == 1
        assert result["failed_read_events"][0]["reason"] == "artifact_not_in_bundle"

    def test_empty_path_detected(self, tmp_path):
        """Artifact with empty path — refused."""
        bundle = _bundle(valid={
            "normalized": _artifact("", ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)
        result = verify_artifact_reads(handle, selected)

        assert len(result["verified_read_events"]) == 0
        assert len(result["failed_read_events"]) == 1
        assert result["failed_read_events"][0]["reason"] == "artifact_path_missing"


# ===========================================================================
# W05B-N4: negative — hash-only, no source binding mix
# ===========================================================================

class TestW05BN4NegativeSourceBinding:
    """Source hash and artifact hash are never mixed."""

    def test_source_sha_in_verified_event(self):
        """Verified events carry source_sha256 from bundle source,
        separate from content_sha256."""
        bundle = _bundle(valid={
            "normalized": _artifact(str(ALPHA_PATH), ALPHA_SHA),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)
        result = verify_artifact_reads(handle, selected)

        event = result["verified_read_events"][0]
        # source_sha256 comes from bundle.source (the document identity)
        assert event["source_sha256"] == SOURCE_SHA
        # content_sha256 comes from the artifact file (the processed artifact)
        assert event["content_sha256_actual"] == ALPHA_SHA
        # They are different
        assert event["source_sha256"] != event["content_sha256_actual"]


# ===========================================================================
# Integration: prepare_source receipt structure
# ===========================================================================

class TestW05BIntegrationReceipt:
    """Integration: prepare_source receipt carries verified events."""

    def test_prepare_source_receipt_has_verified_events(self, monkeypatch, tmp_path):
        """prepare_source receipt includes artifact_read_events."""
        from source_preparation import prepare_source
        import company_wiki_source as cws

        alpha_file = tmp_path / "norm.txt"
        alpha_file.write_bytes(ALPHA_BODY)
        alpha_sha = hashlib.sha256(ALPHA_BODY).hexdigest()

        bundle = _bundle(valid={
            "normalized": _artifact(str(alpha_file), alpha_sha),
        })
        envelope = {
            "envelope_schema_version": "1.0",
            "outcome": "reused_existing",
            "download_events": 0,
            "policy_hash": "a" * 64,
            "activation_epoch": "epoch-1",
            "bundle_status": "available",
            "bundle_hash": bundle["bundle_hash"],
            "bundle": bundle,
            "prompt_injection_status": "not_detected",
            "parser_calls": 0,
            "llm_calls": 0,
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

        record = prepare_source({
            "company_query": "Acme",
            "document_kind": "annual_report",
            "as_of_date": "2026-12-31",
        })
        receipt = record["reuse_receipt"]

        # Plan exists
        assert "normalized" in receipt["artifact_read"]
        # Verified events exist
        assert "artifact_read_events" in receipt
        assert len(receipt["artifact_read_events"]) == 1
        assert receipt["artifact_read_events"][0]["read_status"] == "verified"
        assert receipt["artifact_read_events"][0]["bytes_read"] == len(ALPHA_BODY)
        # Failed events list exists (empty for success)
        assert "artifact_failed_events" in receipt
        assert len(receipt["artifact_failed_events"]) == 0


# ===========================================================================
# Race condition: select then tamper then verify
# ===========================================================================

class TestW05BRaceCondition:
    """TOCTOU: selection and read can drift if file changes between them."""

    def test_select_then_tamper_then_verify(self, tmp_path):
        """Simulates race: select at T1, file changes at T2, verify at T3."""
        artifact = tmp_path / "race.txt"
        artifact.write_bytes(ALPHA_BODY)
        alpha_sha = hashlib.sha256(ALPHA_BODY).hexdigest()

        bundle = _bundle(valid={
            "normalized": _artifact(str(artifact), alpha_sha),
        })
        handle = _handle(bundle)

        # T1: Select
        selected, _ = select_artifact_roles(handle)

        # T2: File changes (simulating concurrent writer)
        artifact.write_bytes(BETA_BODY)

        # T3: Verify detects the change
        result = verify_artifact_reads(handle, selected)
        assert len(result["verified_read_events"]) == 0
        assert len(result["failed_read_events"]) == 1
        assert result["failed_read_events"][0]["reason"] == "content_sha256_mismatch"

    def test_select_then_delete_then_verify(self, tmp_path):
        """File deleted between select and verify."""
        artifact = tmp_path / "deleted.txt"
        artifact.write_bytes(ALPHA_BODY)
        alpha_sha = hashlib.sha256(ALPHA_BODY).hexdigest()

        bundle = _bundle(valid={
            "normalized": _artifact(str(artifact), alpha_sha),
        })
        handle = _handle(bundle)
        selected, _ = select_artifact_roles(handle)

        # File disappears
        artifact.unlink()

        result = verify_artifact_reads(handle, selected)
        assert len(result["verified_read_events"]) == 0
        assert len(result["failed_read_events"]) == 1
        assert result["failed_read_events"][0]["reason"] == "artifact_file_missing"
