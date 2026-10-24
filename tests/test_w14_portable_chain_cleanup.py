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


def test_restore_report_detects_added_removed_changed(tmp_path):
    target = tmp_path / "watched"
    target.mkdir()
    (target / "a.txt").write_text("a", encoding="utf-8")
    (target / "c.txt").write_text("c", encoding="utf-8")
    from replay_support import observe
    before = observe.tree_snapshot(target)
    (target / "a.txt").write_text("changed", encoding="utf-8")
    (target / "b.txt").write_text("b", encoding="utf-8")
    (target / "c.txt").unlink()
    # a file created AND deleted after the snapshot leaves no residue and is
    # invisible to the diff — that is exactly the no-residue guarantee
    gone = target / "transient.txt"
    gone.write_text("t", encoding="utf-8")
    gone.unlink()
    report = cleanup_mod.restore_report(target, before)
    assert report["checked"] is True
    assert report["unchanged"] is False
    assert report["added"] == ["b.txt"]
    assert report["removed"] == ["c.txt"]
    assert report["changed"] == ["a.txt"]
