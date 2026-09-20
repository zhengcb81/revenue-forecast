"""Report the PHASE wall clock (r2 P3-5): reported, never bounded.

The frozen acceptance rule (I-04-A/B) is per SUB-CALL with explicit means: the
lock wait, each probe, each CLI call.  What the phase wall clock measures is the
composition of those, and the standing rule is that it is REPORTED, never capped
by an acceptance threshold.  This tool prints it so a reviewer has a readable
number instead of a claim.

Definition used here: from the participant's first lease-lock acquisition
(``lock_acq`` with name=lease) to its last lock release, per case, aggregated
over all participants of that case.
"""

from __future__ import annotations

import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_ROOT = os.path.join(ATTEMPT, "evidence", "run")


def read_journal(path):
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def case_phase_wall(case_dir):
    journal = os.path.join(case_dir, "journal.jsonl")
    if not os.path.exists(journal):
        return None
    rows = [r for r in read_journal(journal)
            if r.get("event") in {"lock_acq", "lock_rel"} and r.get("name") == "lease"]
    if not rows:
        return None
    times = [r["monotonic"] for r in rows if isinstance(r.get("monotonic"), (int, float))]
    if len(times) < 2:
        return None
    return {
        "case": os.path.basename(case_dir),
        "lease_lock_acquisitions": sum(1 for r in rows if r["event"] == "lock_acq"),
        "first_lock_acq": round(min(r["monotonic"] for r in rows
                                    if r["event"] == "lock_acq"), 3),
        "last_lock_rel": round(max(r["monotonic"] for r in rows
                                   if r["event"] == "lock_rel"), 3),
        "phase_wall_seconds": round(max(times) - min(times), 3),
        "max_lock_wait_seconds": round(max((r.get("waited") or 0.0) for r in rows
                                           if r["event"] == "lock_acq"), 6),
        "acceptance": "reported only; the per-subcall bounds (lock wait, probe, CLI) are the acceptance口径",
    }


def main():
    if not os.path.isdir(RUN_ROOT):
        print("no evidence/run directory")
        return 2
    records = []
    for name in sorted(os.listdir(RUN_ROOT)):
        case_dir = os.path.join(RUN_ROOT, name)
        if os.path.isdir(case_dir):
            record = case_phase_wall(case_dir)
            if record:
                records.append(record)
    out = os.path.join(ATTEMPT, "evidence", "phase-wall.txt")
    with open(out, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    for record in records:
        print(json.dumps(record, sort_keys=True))
    print(f"cases_with_lock_activity={len(records)} report={out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
