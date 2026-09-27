"""I-14-B login tolerance sweep (algorithm-level, NOT the real UI trial).

The tolerance is an INPUT parameter, never a constant: this script sweeps it and
reports where each synthetic login case flips.  It therefore cannot be used to
"pick a tolerance that looks good" -- the deliverable is the whole curve plus the
flip point, and oracle.md section 6 pre-registers the proposed value separately
as awaiting reviewer freeze.

Usage:
  <iso-python> -X utf8 -B harness/tolerance_sweep.py --out evidence/tolerance_sweep.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SUT = ATTEMPT / "iso" / "natural_window.py"
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
BY_ID = {c["case_id"]: c for c in CASES["cases"]}
LOGIN_CASES = ["L1", "L2", "L2b", "L3", "L4", "L5"]
TOLERANCES = [0, 1, 2, 5, 10, 20, 30, 60, 86, 87, 90, 120]


def load_sut():
    spec = importlib.util.spec_from_file_location("i14b_sut", SUT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ATTEMPT / "evidence" / "tolerance_sweep.json"))
    args = ap.parse_args()

    sut = load_sut()
    frozen_now = datetime.fromisoformat(CASES["frozen_now_utc"].replace("Z", "+00:00")).astimezone(timezone.utc)

    table = []
    for tol in TOLERANCES:
        row = {"tolerance_seconds": tol, "verdicts": {}}
        for case_id in LOGIN_CASES:
            got = sut.classify(BY_ID[case_id], frozen_now, float(tol), 5.0)
            row["verdicts"][case_id] = {
                "verdict": got["verdict"],
                "refusals": got["refusals"],
                "max_error_seconds": got["computed"]["label_offset_max_error_seconds"],
            }
        table.append(row)

    flips = {}
    for case_id in LOGIN_CASES:
        first_accept = None
        for row in table:
            if row["verdicts"][case_id]["verdict"] == "accept_claim":
                first_accept = row["tolerance_seconds"]
                break
        flips[case_id] = first_accept

    doc = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "kind": "ALGORITHM-LEVEL SWEEP ON SYNTHETIC INPUTS -- not a real UI observation trial",
        "sut_sha256": __import__("hashlib").sha256(SUT.read_bytes()).hexdigest(),
        "tolerances_seconds": TOLERANCES,
        "capture_tolerance_seconds_fixed_at": 5.0,
        "hand_computed_expectation": {
            "L2": "max error 87 s at label 120 -> rejected for tol <= 86, accepted from tol 87",
            "L2b": "post-hoc evidence is refused at every tolerance",
            "L3": "3600 s capture latency is refused at every tolerance in this sweep",
            "L4": "same-instant labels are refused at every tolerance (R-SAME-INSTANT)",
            "L5": "a non-shared anchor is refused at every tolerance",
            "L1": "exact offsets are accepted at every tolerance",
        },
        "first_tolerance_that_accepts": flips,
        "table": table,
    }
    Path(args.out).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    for case_id in LOGIN_CASES:
        verdicts = "".join("A" if row["verdicts"][case_id]["verdict"] == "accept_claim" else "R"
                           for row in table)
        print(f"{case_id}: {verdicts}  (tol order {TOLERANCES})  first_accept={flips[case_id]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
