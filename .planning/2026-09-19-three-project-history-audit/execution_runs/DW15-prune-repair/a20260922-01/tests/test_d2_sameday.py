"""D2 — 同日覆写: same-instant runs must not clobber each other.

Frozen expectations: oracle.md §2 rows t_d2_1, t_d2_2.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from dw15_fixtures import (
    EXPECTED_DELETE,
    NOW_ARCHIVE,
    NOW_PRUNE,
    RETIRED_AT_TAKE,
    RETENTION_DAYS,
    SAMPLE_DOCUMENTS,
    build_scratch_catalog,
    call_archive,
    call_prune,
    live_span_ids,
    pre_to_post_case,
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


def test_d2_two_archive_runs_in_the_same_instant_both_survive(tmp_path):
    """t_d2_1: run 1's snapshot must be byte-identical after run 2."""
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               SAMPLE_DOCUMENTS)
    archive_root = tmp_path / "manifests"

    first = call_archive(db, archive_root, now=NOW_ARCHIVE)
    first_path = Path(first.archive_path)
    first_bytes = first_path.read_bytes()

    second = call_archive(db, archive_root, now=NOW_ARCHIVE)  # same instant
    second_path = Path(second.archive_path)

    snapshots = sorted(archive_root.rglob("retired-evidence*.jsonl.gz"))
    assert len(snapshots) == 2, (
        f"expected two coexisting snapshots, found {[p.name for p in snapshots]}")
    assert first_path.exists(), "run 1's snapshot was removed by run 2"
    assert first_path.read_bytes() == first_bytes, (
        "run 2 truncated/overwrote run 1's published snapshot")
    assert first_path.resolve() != second_path.resolve(), (
        "both runs published to the same path")
    for snapshot in snapshots:
        assert _fully_read(snapshot) == RETIRED_AT_TAKE, (
            f"snapshot {snapshot.name} is not complete: "
            f"{_fully_read(snapshot)}")


def test_d2_two_prune_applies_in_the_same_second_keep_separate_receipts(tmp_path):
    """t_d2_2: each apply keeps its own receipt; neither overwrites the other."""
    case = pre_to_post_case(tmp_path)
    config = case["config"]

    apply_one = call_prune(config, case["archive_root"], now=NOW_PRUNE,
                           apply=True, retention_days=RETENTION_DAYS)
    receipts_after_first = receipts_for(config)
    assert len(receipts_after_first) == 1, (
        f"expected 1 receipt after the first apply: {receipts_after_first}")
    first_receipt_path = receipts_after_first[0]
    first_receipt = json.loads(first_receipt_path.read_text(encoding="utf-8"))
    after_first = live_span_ids(case["db"])

    apply_two = call_prune(config, case["archive_root"], now=NOW_PRUNE,
                           apply=True, retention_days=RETENTION_DAYS)
    receipts_after_second = receipts_for(config)

    assert len(receipts_after_second) == 2, (
        "the second apply in the same second overwrote the first receipt: "
        f"{[p.name for p in receipts_after_second]}")
    assert first_receipt_path.exists(), "run 1's receipt was clobbered"
    assert first_receipt["deleted_rows"] == len(EXPECTED_DELETE), (
        f"first receipt lost its own deletion record: {first_receipt}")
    still_first = json.loads(first_receipt_path.read_text(encoding="utf-8"))
    assert still_first == first_receipt, "receipt 1 changed after apply 2"
    second_receipt_path = next(p for p in receipts_after_second
                               if p != first_receipt_path)
    second_receipt = json.loads(second_receipt_path.read_text(encoding="utf-8"))
    assert second_receipt["deleted_rows"] == 0, (
        f"second apply must report 0 deleted: {second_receipt}")

    assert sorted(set(after_first) - set(live_span_ids(case["db"]))) == []
    assert apply_one.deleted_rows == len(EXPECTED_DELETE)
    assert apply_two.deleted_rows == 0
