"""Watch the REAL dayu_portfolio root to attribute the 2026-09-19 full-suite failure.

Context: in the 2026-09-19 full-suite coverage run,
`tests/contract/test_zr409_fourth_root_real_journeys.py::test_c2_journey_dayu_only_real_sample`
FAILED on `assert portfolio_before == _shallow_fingerprint(_root_dir(catalog, "dayu_portfolio"))`
(two snapshots taken milliseconds apart inside the test), and the same test PASSED in isolation
on the identical tree immediately after.  That test's fingerprint is (top-level child name,
size, mtime_ns) of a LIVE production root, so a concurrent writer flips it - this script measures
whether the directory really does move on its own, instead of asserting "flaky".

Read-only: config load + `iterdir()` + `stat()` on a real root, plus a size/mtime_ns read of the
production catalog.  Nothing is written anywhere except the --out JSON.

Usage::

    python zr409_live_root_watch.py --seconds 180 --out zr409-live-root-watch.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(WIKI / "src"))
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

PRODUCTION_CONFIG = WIKI / "config" / "source_catalog.yaml"
PRODUCTION_DB = WIKI / ".source_catalog" / "catalog.sqlite3"


def shallow(directory: Path) -> tuple[str, dict[str, tuple[int, int]]]:
    """Exactly the test's fingerprint, plus the per-child detail needed to attribute a change."""
    detail: dict[str, tuple[int, int]] = {}
    digest = hashlib.sha256()
    for child in sorted(directory.iterdir()):
        digest.update(child.name.encode())
        try:
            stat = child.stat()
            detail[child.name] = (stat.st_size, stat.st_mtime_ns)
            digest.update(str(stat.st_size).encode())
            digest.update(str(stat.st_mtime_ns).encode())
        except OSError:
            detail[child.name] = (-1, -1)
            digest.update(b"inaccessible")
    return digest.hexdigest(), detail


def db_state() -> tuple[int, int]:
    stat = PRODUCTION_DB.stat()
    return stat.st_size, stat.st_mtime_ns


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seconds", type=float, default=180.0)
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_suffix(".json"))
    args = parser.parse_args(argv)

    from company_wiki.source_catalog.config import load_catalog_config

    config = load_catalog_config(PRODUCTION_CONFIG, project_root=WIKI)
    roots = {root.root_id: Path(root.path) for root in config.roots}
    target = roots["dayu_portfolio"]

    db_before = db_state()
    digest, detail = shallow(target)
    first = {"digest": digest, "children": len(detail), "at": datetime.now(UTC).isoformat()}
    changes: list[dict] = []
    samples = 1
    deadline = time.monotonic() + args.seconds
    while time.monotonic() < deadline:
        time.sleep(args.interval)
        now_digest, now_detail = shallow(target)
        samples += 1
        if now_digest != digest:
            added = sorted(set(now_detail) - set(detail))
            removed = sorted(set(detail) - set(now_detail))
            touched = sorted(
                name for name in set(detail) & set(now_detail)
                if detail[name] != now_detail[name]
            )
            changes.append({
                "at": datetime.now(UTC).isoformat(),
                "previous_digest": digest,
                "new_digest": now_digest,
                "added_children": added,
                "removed_children": removed,
                "touched_children": [
                    {"name": name, "before": detail[name], "after": now_detail[name]}
                    for name in touched
                ],
            })
            digest, detail = now_digest, now_detail
    db_after = db_state()

    record = {
        "artifact": "zr409-live-root-watch",
        "question": ("does the LIVE dayu_portfolio root change on its own, which is what the "
                     "2026-09-19 full-suite assertion compared?"),
        "root_path": str(target),
        "observed_seconds": args.seconds,
        "samples": samples,
        "first_snapshot": first,
        "changes": changes,
        "live_root_changed_during_watch": bool(changes),
        "production_db_unchanged": db_before == db_after,
        "production_db_before": {"byte_size": db_before[0], "mtime_ns": db_before[1]},
        "production_db_after": {"byte_size": db_after[0], "mtime_ns": db_after[1]},
        "repo_status": None,
        "ran_at_utc": datetime.now(UTC).isoformat(),
    }
    import subprocess

    record["repo_status"] = subprocess.run(
        ["git", "-C", str(WIKI), "status", "--porcelain"],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines()
    args.out.write_text(json.dumps(record, ensure_ascii=True, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(json.dumps({key: record[key] for key in (
        "samples", "live_root_changed_during_watch", "production_db_unchanged",
        "changes")}, ensure_ascii=True, indent=2)[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
