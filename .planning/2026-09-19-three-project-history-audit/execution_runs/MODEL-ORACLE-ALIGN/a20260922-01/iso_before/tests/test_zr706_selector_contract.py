"""ZR-706 acceptance tests: FC-904 artifact selector contract completion.

  C1  read/produced mutual exclusion: for every bundle shape
      (full valid / summary missing / normalized missing / tampered)
      artifact_read ∩ producer_events == ∅.
  C2  custom roles subset: select_artifact_roles(roles=subset) restricts
      both read and produced to the subset (DAG closure within the
      subset, never blind recompute of roles outside it).
  C3  consumer_analysis provenance match -> read; mismatch -> not read
      (produced) — AR-06 covered the mismatch side; this pins the match
      side.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from company_wiki_source import select_artifact_roles  # noqa: E402

ALL_ROLES = ("normalized", "markdown", "summary", "sections",
             "consumer_analysis")


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


def _artifact(role: str = "normalized", **overrides) -> dict:
    base = {"artifact_role": role, "reusable": True,
            "content_sha256": "e" * 64, "generator_name": "g",
            "generator_version": "1.0"}
    base.update(overrides)
    return base


def _full_valid_bundle() -> dict:
    return _bundle(valid={
        "normalized": _artifact(role="normalized"),
        "markdown": _artifact(role="markdown"),
        "sections": _artifact(role="sections"),
        "summary": _artifact(role="summary"),
        "consumer_analysis": _artifact(
            role="consumer_analysis",
            engine="e", model="m", prompt="p", input_bundle_hash="h",
        ),
    })


# ---------------------------------------------------------------------------
# C1 — read/produced mutual exclusion
# ---------------------------------------------------------------------------


def test_c1_mutual_exclusion_full_valid():
    read, produced = select_artifact_roles(_handle(_full_valid_bundle()))
    assert set(read).isdisjoint(set(produced))


def test_c1_mutual_exclusion_summary_missing():
    bundle = _bundle(valid={
        "normalized": _artifact(role="normalized"),
        "markdown": _artifact(role="markdown"),
        "sections": _artifact(role="sections"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert set(read).isdisjoint(set(produced))


def test_c1_mutual_exclusion_normalized_missing():
    bundle = _bundle(valid={
        "markdown": _artifact(role="markdown"),
        "summary": _artifact(role="summary"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert set(read).isdisjoint(set(produced))


def test_c1_mutual_exclusion_tampered():
    bundle = _bundle(valid={
        "normalized": _artifact(role="normalized"),
    }, invalid={
        "summary": _artifact(role="summary", reusable=False,
                             reason="artifact_hash_mismatch"),
    })
    read, produced = select_artifact_roles(_handle(bundle))
    assert set(read).isdisjoint(set(produced))


def test_c1_mutual_exclusion_no_bundle():
    read, produced = select_artifact_roles(_handle())
    assert set(read).isdisjoint(set(produced))
    assert read == []
    assert set(produced) == set(ALL_ROLES)


# ---------------------------------------------------------------------------
# C2 — custom roles subset
# ---------------------------------------------------------------------------


def test_c2_subset_read_only_normalized():
    read, produced = select_artifact_roles(
        _handle(_full_valid_bundle()), roles=("normalized",)
    )
    assert read == ["normalized"]
    assert produced == []


def test_c2_subset_produced_limited_to_subset():
    bundle = _bundle(valid={
        "normalized": _artifact(role="normalized"),
    })
    # markdown missing: its DAG closure (markdown + transitive dependents)
    # is produced; roles outside the subset are not *scanned* but the
    # closure of a non-reusable in-subset role still names its dependents.
    read, produced = select_artifact_roles(
        _handle(bundle), roles=("normalized", "markdown")
    )
    assert read == ["normalized"]
    assert "markdown" in produced


def test_c2_subset_never_touches_roles_outside():
    bundle = _bundle(valid={})
    read, produced = select_artifact_roles(
        _handle(bundle), roles=("normalized",)
    )
    assert read == []
    # the in-subset role's closure includes its transitive dependents
    assert "normalized" in produced


# ---------------------------------------------------------------------------
# C3 — consumer_analysis provenance match -> read
# ---------------------------------------------------------------------------


def test_c3_provenance_match_reads_consumer_analysis():
    bundle = _full_valid_bundle()
    expected = {"engine": "e", "model": "m", "prompt": "p",
                "input_bundle_hash": "h"}
    read, produced = select_artifact_roles(
        _handle(bundle), expected_provenance=expected
    )
    assert "consumer_analysis" in read
    assert "consumer_analysis" not in produced


def test_c3_provenance_mismatch_not_read():
    bundle = _full_valid_bundle()
    expected = {"engine": "OTHER", "model": "m", "prompt": "p",
                "input_bundle_hash": "h"}
    read, produced = select_artifact_roles(
        _handle(bundle), expected_provenance=expected
    )
    assert "consumer_analysis" not in read
    assert "consumer_analysis" in produced


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
