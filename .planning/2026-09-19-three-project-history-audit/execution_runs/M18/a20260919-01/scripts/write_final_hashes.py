"""Final hash table for one attempt: absolute path + sha256 of every deliverable.

Written AFTER review.md / decision.md / handoff.json / changes.diff exist, so the table
covers the finished attempt.  iso/venv is excluded (thousands of interpreter files) but
iso/checkout_scripts is included, and the interpreter path is recorded explicitly.

Usage:
  python -X utf8 -B write_final_hashes.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os

import card_units

SKIP_DIRS = {os.path.normcase(os.path.join("iso", "venv"))}
# The closing unit's own capture records are written by the capture wrapper AFTER the closing unit
# returns, i.e. after this table.  They are therefore excluded here instead of being listed with a
# stale hash; each rc.json self-describes the sha256 of its own stdout/stderr, and commands.json
# records the rc_record_sha256 of that unit.
SKIP_PREFIXES = (os.path.normcase("evidence"), )


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    closing_run_dir = os.path.normcase(os.path.join("evidence", card, "runs", "Z-close-attempt"))
    # Records written by the closing DRIVERS after the last unit returns; they cannot be inside a
    # table that the last unit writes.
    closing_driver_records = {
        os.path.normcase("recovery/closing_run.json"),
        os.path.normcase("recovery/r2_run.json"),
    }
    files = {}
    excluded = []
    for root, dirs, names in os.walk(attempt):
        rel_root = os.path.relpath(root, attempt)
        if rel_root != "." and os.path.normcase(rel_root) in SKIP_DIRS:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs
                   if os.path.normcase(os.path.join(rel_root, d)) not in SKIP_DIRS]
        for name in sorted(names):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, attempt).replace("\\", "/")
            if rel.endswith("final_deliverable_hashes.json"):
                excluded.append(rel)
                continue
            if os.path.normcase(rel).startswith(closing_run_dir):
                excluded.append(rel)
                continue
            if os.path.normcase(rel) in closing_driver_records:
                excluded.append(rel)
                continue
            files[rel] = {"absolute_path": path, "sha256": sha256(path),
                          "size_bytes": os.path.getsize(path)}

    doc = {
        "card_id": card,
        "model_id": card_units.CARDS[card]["model_id"],
        "attempt_root": attempt,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "interpreter_path": os.path.join(attempt, "iso", "venv", "Scripts", "python.exe"),
        "excluded_from_the_table": [
            "iso/venv/** (attempt-local interpreter, not an evidence file)",
            ("this table itself (a file cannot contain its own hash)"),
            ("evidence/%s/runs/Z-close-attempt/** (the closing unit's own capture records: the "
             "capture wrapper writes them after the unit returns, i.e. after this table; "
             "evidence/%s/runs/Z-close-attempt/rc.json self-describes the sha256 of its own "
             "stdout/stderr, and commands.json records that unit's rc_record_sha256)" % (card, card)),
            ("recovery/closing_run.json and recovery/r2_run.json (written by the closing DRIVERS "
             "after the last unit returns; closing_run.json lists the units and their failures, and "
             "the per-unit rc.json records carry the raw rc)"),
        ] + excluded,
        "excluded_paths_present": sorted(set(excluded)),
        "file_count": len(files),
        "files": files,
    }
    out = os.path.join(attempt, "after", "final_deliverable_hashes.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("final hashes", len(files), "->", out)
    for rel in sorted(files):
        if rel.count("/") <= 1:
            print("  %s  %s" % (files[rel]["sha256"], rel))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
