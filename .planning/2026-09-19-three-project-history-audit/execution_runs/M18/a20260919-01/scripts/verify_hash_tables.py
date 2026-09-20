"""Verify BOTH hash tables of one attempt and publish the measurement (P2-A).

Runs after the closing unit, so it can detect a table that stopped matching the files on disk.  It
writes after/hash_table_verification.json and exits non-zero when either table has drift or missing
entries, which makes "drift = 0" a measured output rather than a claim.

Usage:
  python -X utf8 -B verify_hash_tables.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os

import card_units


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()



def atomic_dump(path, doc):
    """Write JSON through a temp file + os.replace so an interrupted write cannot truncate it."""
    tmp = path + ".tmp-atomic"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def check(attempt, table_path):
    table = load(table_path)
    drifted = []
    missing = []
    for rel, entry in table["files"].items():
        wanted = entry["sha256"] if isinstance(entry, dict) else entry
        want_size = entry.get("size_bytes") if isinstance(entry, dict) else None
        path = os.path.join(attempt, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            missing.append(rel)
            continue
        got = sha256(path)
        if got != wanted or (want_size is not None and os.path.getsize(path) != want_size):
            drifted.append({"path": rel, "recorded_sha256": wanted, "actual_sha256": got,
                            "recorded_size": want_size, "actual_size": os.path.getsize(path)})
    return {"table": os.path.relpath(table_path, attempt).replace("\\", "/"),
            "entries": len(table["files"]),
            "drift_count": len(drifted),
            "missing_count": len(missing),
            "drifted": drifted,
            "missing": missing,
            "table_recorded_drift_count": table.get("drift_count"),
            "table_verified_utc": table.get("verified_utc"),
            "table_excluded_paths": table.get("excluded_paths_present")
                                     or (table.get("excluded_from_this_table") or {}).get("paths")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    checks = [
        check(attempt, os.path.join(evidence, "evidence_hashes.json")),
        check(attempt, os.path.join(attempt, "after", "final_deliverable_hashes.json")),
    ]
    total_drift = sum(c["drift_count"] for c in checks)
    total_missing = sum(c["missing_count"] for c in checks)
    doc = {
        "card_id": card,
        "model_id": card_units.CARDS[card]["model_id"],
        "purpose": ("measure, not claim: re-read both hash tables entry by entry after the closing "
                    "unit has returned"),
        "tables": checks,
        "total_drift_count": total_drift,
        "total_missing_count": total_missing,
        "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "runner_sha256": sha256(os.path.join(attempt, "scripts", "run_card.py")),
        "self_exclusions": ("this verification's own capture records and its output file are excluded "
                            "from the final table by construction (they are written after it)"),
    }
    out = os.path.join(attempt, "after", "hash_table_verification.json")
    atomic_dump(out, doc)
    for c in checks:
        print("table %-46s entries=%-4d drift=%d missing=%d (table-recorded drift=%s)"
              % (c["table"], c["entries"], c["drift_count"], c["missing_count"],
                 c["table_recorded_drift_count"]))
        for d in c["drifted"][:5]:
            print("    drift:", d["path"], d["recorded_size"], "->", d["actual_size"])
    print("total_drift_count:", total_drift, "total_missing_count:", total_missing)
    print("verified_utc:", doc["verified_utc"])
    print("written", out)
    return 0 if not (total_drift or total_missing) else 3


if __name__ == "__main__":
    raise SystemExit(main())
