"""D5 — 崩溃后不可恢复: crash-safe snapshot writes and plan receipts.

Frozen expectations: oracle.md §2 rows t_d5_1..t_d5_3.
"""
from __future__ import annotations

import gzip
import json
import sqlite3
from pathlib import Path

import pytest

from dw15_fixtures import (
    ARCHIVED_AT_TAKE,
    EXPECTED_DELETE,
    EXPECTED_RETAIN,
    NOW_ARCHIVE,
    NOW_PRUNE,
    RETENTION_DAYS,
    RETIRED_AT_TAKE,
    SAMPLE_DOCUMENTS,
    build_scratch_catalog,
    call_archive,
    call_prune,
    live_span_ids,
    pre_to_post_case,
    prune_module,
    receipts_for,
)


def _fully_read(path: Path) -> list[str]:
    ids = []
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                ids.append(json.loads(line)["span_id"])
    return sorted(ids)


class Boom(RuntimeError):
    """Simulated kill."""


def test_d5_killed_snapshot_write_publishes_no_truncated_snapshot(
        tmp_path, monkeypatch):
    """t_d5_1: kill mid-write -> no truncated published snapshot; run-0 intact;
    catalog untouched (evidence present)."""
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               SAMPLE_DOCUMENTS)
    archive_root = tmp_path / "manifests"
    before = live_span_ids(db)

    run0 = call_archive(db, archive_root, now=NOW_ARCHIVE)
    run0_path = Path(run0.archive_path)
    run0_bytes = run0_path.read_bytes()

    import gzip as gzip_module
    real_open = gzip_module.open

    class KillAfterTwoRows:
        def __init__(self, inner):
            self._inner = inner
            self._writes = 0

        def __enter__(self):
            self._inner.__enter__()
            return self

        def __exit__(self, *exc_info):
            return self._inner.__exit__(*exc_info)

        def write(self, data):
            self._writes += 1
            if self._writes > 2:
                raise Boom("simulated kill during snapshot write")
            return self._inner.write(data)

        def __getattr__(self, name):
            return getattr(self._inner, name)

    def fake_open(*args, **kwargs):
        mode = (kwargs.get("mode") if "mode" in kwargs
                else (args[1] if len(args) > 1 else "rb"))
        handle = real_open(*args, **kwargs)
        if isinstance(mode, str) and "w" in mode and "r" not in mode:
            return KillAfterTwoRows(handle)
        return handle

    monkeypatch.setattr(gzip_module, "open", fake_open)
    with pytest.raises(Boom):
        call_archive(db, archive_root, now=NOW_ARCHIVE)
    monkeypatch.setattr(gzip_module, "open", real_open)   # restore for assertions

    problems = []
    for snapshot in sorted(archive_root.rglob("retired-evidence*.jsonl.gz")):
        try:
            ids = _fully_read(snapshot)
        except Exception as exc:
            problems.append(f"{snapshot.name}: truncated/unreadable ({exc})")
            continue
        if ids != RETIRED_AT_TAKE:
            problems.append(f"{snapshot.name}: {len(ids)} rows, "
                            f"expected {len(RETIRED_AT_TAKE)}")
    assert problems == [], f"a published snapshot is not crash-safe: {problems}"
    assert run0_path.exists() and run0_path.read_bytes() == run0_bytes, (
        "the previously published snapshot was destroyed by the killed run")
    assert live_span_ids(db) == before, (
        "a failed archive run must leave the evidence rows untouched")


def test_d5_kill_after_pending_receipt_before_first_delete(tmp_path, monkeypatch):
    """t_d5_2: kill between snapshot-write and delete -> receipt names the full
    plan, snapshot complete, evidence intact."""
    case = pre_to_post_case(tmp_path)
    module = prune_module()
    real_store = module.CatalogStore

    class ExplodingStore:
        def __init__(self, database_path):
            self._inner = real_store(database_path)

        def transaction(self):
            raise Boom("simulated kill before the first delete")

    monkeypatch.setattr(module, "CatalogStore", ExplodingStore)

    before = live_span_ids(case["db"])
    with pytest.raises(Boom):
        call_prune(case["config"], case["archive_root"], now=NOW_PRUNE,
                   apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(case["db"])
    monkeypatch.setattr(module, "CatalogStore", real_store)

    receipts = receipts_for(case["config"])
    assert receipts, (
        "kill between snapshot-write and delete left no pending receipt; "
        "the full plan is not on disk")
    receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert sorted(receipt["span_ids"]) == EXPECTED_DELETE, (
        f"pending receipt does not name the pre-listed plan: {receipt}")
    assert receipt["status"] == "pending"
    assert after == before, "evidence rows must still be present"

    snapshot_ids = _fully_read(Path(case["archive_report"].archive_path))
    assert snapshot_ids == sorted(ARCHIVED_AT_TAKE), (
        f"snapshot incomplete after the kill: {snapshot_ids}")


def test_d5_kill_after_first_batch_commit_leaves_an_exact_receipt(
        tmp_path, monkeypatch):
    """t_d5_3: crash after batch 1 -> every deleted id is recoverable from the
    receipt (subset of plan) and restorable (subset of the snapshot)."""
    case = pre_to_post_case(tmp_path)
    module = prune_module()
    monkeypatch.setattr(module, "BATCH_SIZE", 1)
    real_store = module.CatalogStore

    class ExplodingStore:
        def __init__(self, database_path):
            self._conn = sqlite3.connect(database_path)
            self._conn.row_factory = sqlite3.Row
            self._commits = 0

        def transaction(self):
            conn = self._conn
            outer = self

            class _Ctx:
                def __enter__(_self):
                    conn.execute("BEGIN IMMEDIATE")
                    return conn

                def __exit__(_self, exc_type, exc, tb):
                    if exc_type is not None:
                        conn.rollback()
                        return False
                    conn.commit()
                    outer._commits += 1
                    if outer._commits >= 1:
                        raise Boom("simulated kill after the first batch commit")
                    return False

            return _Ctx()

    monkeypatch.setattr(module, "CatalogStore", ExplodingStore)

    before = live_span_ids(case["db"])
    with pytest.raises(Boom):
        call_prune(case["config"], case["archive_root"], now=NOW_PRUNE,
                   apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(case["db"])
    deleted = sorted(set(before) - set(after))
    monkeypatch.setattr(module, "CatalogStore", real_store)

    receipts = receipts_for(case["config"])
    assert receipts, (
        f"crash after batch 1 left no receipt; deleted={deleted} is "
        "unrecoverable from any durable artifact")
    receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
    assert sorted(receipt["span_ids"]) == EXPECTED_DELETE, (
        f"receipt does not name the pre-listed full plan: {receipt}")
    assert receipt["status"] == "pending"
    assert deleted, "fixture expects at least one committed batch before the kill"
    assert set(deleted) <= set(receipt["span_ids"]), (
        f"deleted {deleted} escapes the receipt plan {receipt['span_ids']}")
    assert set(deleted) <= set(ARCHIVED_AT_TAKE), (
        "a deleted id must be restorable from the verified snapshot")
    assert set(EXPECTED_RETAIN) <= set(after), (
        f"rows outside the plan were destroyed: {sorted(after)}")
