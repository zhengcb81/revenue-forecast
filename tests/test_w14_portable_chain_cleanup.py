"""W14 E06 unit tests: exclusive attempt spaces never delete caller data.

Fast, chain-free checks of ``e2e/replay_support/cleanup.py``: allocation,
sentinel preservation, owned-deletion boundaries, and restore proofs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "e2e"))

from replay_support import cleanup as cleanup_mod  # noqa: E402


def test_attempt_is_exclusive_child_and_sentinel_survives(tmp_path):
    root = tmp_path / "work"
    root.mkdir()
    sentinel = root / "sentinel.txt"
    sentinel.write_text("pre-existing user data", encoding="utf-8")
    space = cleanup_mod.AttemptSpace(root, tmp_path / "ev").allocate()
    assert space.path.is_dir()
    assert space.path.parent == root
    assert sentinel.read_text(encoding="utf-8") == "pre-existing user data"
    assert sentinel.name in space.initial_work_inventory

    (space.path / "scratch.bin").write_bytes(b"x" * 10)
    report = space.cleanup()
    assert report["attempt_removed"] is True
    assert report["work_root_restored"] is True
    assert sentinel.read_text(encoding="utf-8") == "pre-existing user data"
    assert list(root.iterdir()) == [sentinel]


def test_second_attempt_gets_a_distinct_directory(tmp_path):
    root = tmp_path / "work"
    first = cleanup_mod.AttemptSpace(root, tmp_path / "ev").allocate()
    first.cleanup()
    second = cleanup_mod.AttemptSpace(root, tmp_path / "ev").allocate()
    assert first.path != second.path
    assert second.path.is_dir()


def test_owned_rmtree_refuses_paths_outside_the_attempt(tmp_path):
    root = tmp_path / "work"
    outsider = tmp_path / "not-mine"
    outsider.mkdir()
    (outsider / "keep.txt").write_text("keep", encoding="utf-8")
    space = cleanup_mod.AttemptSpace(root, tmp_path / "ev").allocate()
    with pytest.raises(cleanup_mod.CleanupViolation):
        space.rmtree_owned(outsider)
    with pytest.raises(cleanup_mod.CleanupViolation):
        space.rmtree_owned(root)  # the caller's own root is not deletable
    assert (outsider / "keep.txt").read_text(encoding="utf-8") == "keep"


def test_evidence_attempts_never_touch_prior_receipts(tmp_path):
    import json
    evidence_root = tmp_path / "evidence"
    prior = evidence_root / "attempt-20260101-000000Z-deadbeef"
    prior.mkdir(parents=True)
    (prior / "summary.json").write_text('{"history": true}', encoding="utf-8")
    space = cleanup_mod.AttemptSpace(tmp_path / "work", evidence_root).allocate()
    fresh = space.evidence_dir()
    assert fresh != prior
    (fresh / "summary.json").write_text('{"new": true}', encoding="utf-8")
    assert json.loads(prior.joinpath("summary.json").read_text(
        encoding="utf-8")) == {"history": True}


def test_cleanup_report_carries_before_after_hash_inventory(tmp_path):
    """W14 F3: the cleanup receipt must persist the full before/after hash
    inventories and the diff fields, not just a self-reported boolean."""
    root = tmp_path / "work"
    root.mkdir()
    sentinel = root / "sentinel.txt"
    sentinel.write_text("owner data", encoding="utf-8")
    space = cleanup_mod.AttemptSpace(root, tmp_path / "ev").allocate()
    (space.path / "scratch.bin").write_bytes(b"scratch")
    report = space.cleanup()
    before = report["initial_inventory"]
    after = report["remaining_inventory"]
    assert report["attempt_removed"] is True
    assert report["work_root_restored"] is True
    assert set(before) == {"sentinel.txt"}  # attempt dir excluded from snapshot
    assert set(after) == {"sentinel.txt"}
    assert len(before["sentinel.txt"]["sha256"]) == 64
    assert before["sentinel.txt"]["sha256"] == after["sentinel.txt"]["sha256"]
    assert report["added"] == [] and report["removed"] == []
    assert report["changed"] == []


def test_cleanup_report_detects_external_modification(tmp_path):
    """An external change to a pre-existing file during the run is visible
    in the persisted diff fields (so a stale restore claim is detectable)."""
    root = tmp_path / "work"
    root.mkdir()
    sentinel = root / "sentinel.txt"
    sentinel.write_text("owner data", encoding="utf-8")
    space = cleanup_mod.AttemptSpace(root, tmp_path / "ev").allocate()
    sentinel.write_text("modified during run", encoding="utf-8")
    report = space.cleanup()
    assert report["work_root_restored"] is False
    assert report["changed"] == ["sentinel.txt"]
    assert report["initial_inventory"]["sentinel.txt"]["sha256"] != \
        report["remaining_inventory"]["sentinel.txt"]["sha256"]
