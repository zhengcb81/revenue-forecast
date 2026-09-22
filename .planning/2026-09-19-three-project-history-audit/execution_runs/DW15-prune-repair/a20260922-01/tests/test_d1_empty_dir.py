"""D1 — 空目录也删: only a verified archive manifest may authorise deletion.

Frozen expectations: oracle.md §2 rows t_d1_1..t_d1_4.
"""
from __future__ import annotations

import gzip
import json

from dw15_fixtures import (
    ARCHIVED_AT_TAKE,
    EXPECTED_DELETE,
    EXPECTED_RETAIN,
    NOW_PRUNE,
    RETENTION_DAYS,
    SAMPLE_DOCUMENTS,
    build_scratch_catalog,
    call_prune,
    guard_scratch,
    live_span_ids,
    make_config,
    pre_to_post_case,
    write_manifest_tree,
)


def test_d1_empty_old_directory_authorises_nothing(tmp_path):
    """t_d1_1: an empty `archive/2026-05-01` must not look like retired evidence."""
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               SAMPLE_DOCUMENTS)
    archive_root = tmp_path / "manifests"
    (archive_root / "archive" / "2026-05-01").mkdir(parents=True)  # empty, old

    before = live_span_ids(db)
    report = call_prune(make_config(db), archive_root, now=NOW_PRUNE,
                        apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(db)

    deleted = sorted(set(before) - set(after))
    assert deleted == [], (
        f"an empty old directory authorised the deletion of {deleted}")
    assert report.due is False, (
        f"due must be false with no verified manifest, got {report.due}")


def test_d1_snapshot_without_manifest_authorises_nothing(tmp_path):
    """t_d1_2: a gzip snapshot but no manifest is not authorisation."""
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               SAMPLE_DOCUMENTS)
    archive_root = tmp_path / "manifests"
    day_dir = archive_root / "archive" / "2026-05-01"
    day_dir.mkdir(parents=True)
    body = "".join(json.dumps({"span_id": sid}) + "\n"
                   for sid in ("a1", "a2", "c1"))
    (day_dir / "retired-evidence-orphan.jsonl.gz").write_bytes(
        gzip.compress(body.encode("utf-8")))

    before = live_span_ids(db)
    report = call_prune(make_config(db), archive_root, now=NOW_PRUNE,
                        apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(db)

    deleted = sorted(set(before) - set(after))
    assert deleted == [], (
        f"a manifest-less snapshot authorised the deletion of {deleted}")
    assert report.due is False


def test_d1_manifest_with_broken_snapshot_authorises_nothing(tmp_path):
    """t_d1_3: manifest present, snapshot corrupt -> verification fails closed."""
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               SAMPLE_DOCUMENTS)
    archive_root = tmp_path / "manifests"
    day_dir = guard_scratch(archive_root / "archive" / "2026-05-01")
    day_dir.mkdir(parents=True)
    snapshot = day_dir / "retired-evidence-broken.jsonl.gz"
    snapshot.write_bytes(b"\x1f\x8b\x08\x00 not a valid gzip body")
    manifest = {
        "schema_version": "archive-verified-manifest-1.0",
        "catalog_identity": "catalog.sqlite3:synthetic",
        "archive_path": str(snapshot.resolve()),
        "archive_sha256": "0" * 64,
        "archive_bytes": snapshot.stat().st_size,
        "rows_in_archive": 3,
        "verified_completed_at": "2026-05-01T00:00:00Z",
        "span_ids": ["a1", "a2", "c1"],
        "row_digests": {"a1": "0" * 64, "a2": "0" * 64, "c1": "0" * 64},
        "verifier": "attempt fixture",
        "problems": [],
        "ok": True,
    }
    (day_dir / f"{snapshot.name}.manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    before = live_span_ids(db)
    report = call_prune(make_config(db), archive_root, now=NOW_PRUNE,
                        apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(db)

    deleted = sorted(set(before) - set(after))
    assert deleted == [], (
        f"a manifest whose snapshot cannot be verified authorised {deleted}")
    assert report.due is False


def test_d1_deletes_exactly_the_verified_set(tmp_path):
    """t_d1_4: real archive + real prune -> exactly [a1,a2], retain [a3,b1,c1]."""
    case = pre_to_post_case(tmp_path)

    before = live_span_ids(case["db"])
    assert sorted(before) == sorted(EXPECTED_DELETE + EXPECTED_RETAIN)
    report = call_prune(case["config"], case["archive_root"], now=NOW_PRUNE,
                        apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(case["db"])

    deleted = sorted(set(before) - set(after))
    assert deleted == EXPECTED_DELETE, (
        f"prune deleted {deleted}, verified archive authorises only "
        f"{EXPECTED_DELETE}; retained={sorted(after)}; report={report.to_dict()}")
    assert sorted(after) == EXPECTED_RETAIN
    assert sorted(ARCHIVED_AT_TAKE) == ["a1", "a2", "c1"]
