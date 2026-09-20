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



def atomic_dump(path, doc):
    """Write JSON through a temp file + os.replace so an interrupted write cannot truncate it."""
    tmp = path + ".tmp-atomic"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

def measure_drift(attempt, entries):
    """Re-read every entry of the table just written and count mismatches (P2-A)."""
    drifted = []
    missing = []
    for rel, entry in entries.items():
        wanted = entry["sha256"] if isinstance(entry, dict) else entry
        path = os.path.join(attempt, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            missing.append(rel)
            continue
        if sha256(path) != wanted:
            drifted.append(rel)
    return {"drift_count": len(drifted), "missing_count": len(missing),
            "drifted_paths": sorted(drifted + ["missing:" + m for m in missing])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    closing_run_dir = os.path.normcase(os.path.join("evidence", card, "runs", "Z-close-attempt"))
    verifier_run_dir = os.path.normcase(os.path.join("evidence", card, "runs", "V-verify-hash-tables"))
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
            if os.path.normcase(rel).startswith(verifier_run_dir):
                excluded.append(rel)
                continue
            if os.path.normcase(rel) == os.path.normcase("after/hash_table_verification.json"):
                excluded.append(rel)
                continue
            files[rel] = {"absolute_path": path, "sha256": sha256(path),
                          "size_bytes": os.path.getsize(path)}

    drift = measure_drift(attempt, files)
    verified_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc = {
        "card_id": card,
        "model_id": card_units.CARDS[card]["model_id"],
        "attempt_root": attempt,
        "generated_utc": verified_utc,
        "verified_utc": verified_utc,
        "drift_count": drift["drift_count"],
        "missing_count": drift["missing_count"],
        "drifted_paths": drift["drifted_paths"],
        "drift_measurement": ("after writing this table it is re-read entry by entry; drift_count is "
                              "the number of entries whose file no longer matches the recorded sha256 "
                              "at verified_utc"),
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
            ("evidence/%s/runs/V-verify-hash-tables/** and after/hash_table_verification.json (written "
             "by the verifier unit that runs AFTER this table, so that drift can be measured "
             "post-hoc)" % card),
        ] + excluded,
        "excluded_paths_present": sorted(set(excluded)),
        "file_count": len(files),
        "files": files,
    }
    out = os.path.join(attempt, "after", "final_deliverable_hashes.json")
    atomic_dump(out, doc)
    print("final hashes", len(files), "->", out)
    print("drift_count", drift["drift_count"], "missing_count", drift["missing_count"],
          "verified_utc", verified_utc)
    if drift["drifted_paths"]:
        print("drifted_paths", drift["drifted_paths"][:20])
    for rel in sorted(files):
        if rel.count("/") <= 1:
            print("  %s  %s" % (files[rel]["sha256"], rel))
    return 0 if not (drift["drift_count"] or drift["missing_count"]) else 3


if __name__ == "__main__":
    raise SystemExit(main())
