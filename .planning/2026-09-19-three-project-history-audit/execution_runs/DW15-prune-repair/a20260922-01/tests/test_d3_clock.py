"""D3 — 时钟取目录名: no system-clock read may decide a path or the clock.

Frozen expectations: oracle.md §2 rows t_d3_1..t_d3_4.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dw15_fixtures import (
    ARCHIVED_AT_TAKE,
    NOW_PRUNE,
    RETENTION_DAYS,
    SAMPLE_DOCUMENTS,
    build_scratch_catalog,
    call_archive,
    call_prune,
    live_span_ids,
    make_config,
    write_manifest_tree,
)

# any system-clock API; none of these may appear in the two repaired modules
CLOCK_API = re.compile(
    r"datetime\.now\b|\.utcnow\s*\(|date\.today\s*\(|time\.gmtime"
    r"|time\.strftime|time\.time\s*\(|fromtimestamp")

REPAIRED_MODULES = ("prune_retired_evidence.py", "archive_retired_evidence.py")


def test_d3_repaired_sources_never_read_the_system_clock():
    """t_d3_1: static guard — path/decision inputs come only from `now`+uuid."""
    variant = Path(os.environ["DW15_VARIANT"])
    for name in REPAIRED_MODULES:
        source = (variant / "company_wiki" / "source_catalog" / name
                  ).read_text(encoding="utf-8")
        match = CLOCK_API.search(source)
        assert match is None, (
            f"{name} reads the system clock: {match.group(0)!r} "
            f"at offset {match.start()}")


def test_d3_recent_verified_completion_stays_inside_the_window(tmp_path):
    """t_d3_2: verified completion 1 day before `now` -> not due, delete 0."""
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               SAMPLE_DOCUMENTS)
    archive_root = tmp_path / "manifests"
    write_manifest_tree(db, archive_root, day="2026-05-01",
                        span_ids=ARCHIVED_AT_TAKE,
                        verified_completed_at="2026-09-18T00:00:00Z")

    before = live_span_ids(db)
    report = call_prune(make_config(db), archive_root, now=NOW_PRUNE,
                        apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(db)

    deleted = sorted(set(before) - set(after))
    assert deleted == [], (
        f"retention ran from the directory name/wall clock and deleted {deleted}")
    assert report.due is False, (
        f"1-day-old verified completion must not be due, got due={report.due}")


def test_d3_ancient_directory_name_is_not_the_clock(tmp_path):
    """t_d3_3: I-15-A n2 verbatim — dir 2021-01-01, verified 2026-09-18."""
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               SAMPLE_DOCUMENTS)
    archive_root = tmp_path / "manifests"
    write_manifest_tree(db, archive_root, day="2021-01-01",
                        span_ids=ARCHIVED_AT_TAKE,
                        verified_completed_at="2026-09-18T00:00:00Z")

    before = live_span_ids(db)
    report = call_prune(make_config(db), archive_root, now=NOW_PRUNE,
                        apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(db)

    deleted = sorted(set(before) - set(after))
    assert deleted == [], (
        f"the ancient directory name acted as the retention clock: {deleted}")
    assert report.due is False


def test_d3_archive_date_directory_follows_injected_now(tmp_path):
    """t_d3_4: injected now=2021-03-04 publishes under archive/2021-03-04/."""
    db = build_scratch_catalog(tmp_path / "catalog" / "catalog.sqlite3",
                               SAMPLE_DOCUMENTS)
    archive_root = tmp_path / "manifests"
    report = call_archive(db, archive_root,
                          now=datetime(2021, 3, 4, tzinfo=timezone.utc))
    path = Path(report.archive_path)
    assert path.parent.name == "2021-03-04", (
        f"snapshot published under {path.parent.name!r}; the system clock "
        "decided the path instead of the injected now")
    assert path.is_file()
