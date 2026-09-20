"""Execute the closing units of one attempt (H-write-handoff, Z-close-attempt).

Kept separate from run_pipeline.py on purpose: the measurement chain stops after the evidence
pack, and these two units only read evidence and write records.  Each still runs through the same
capture mechanism, so each gets its own command-run-id directory with raw stdout/stderr/rc.

Usage:
  python -X utf8 -B run_closing.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import json
import os

import card_units
import run_unit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--phase", default="closing", choices=("r2", "closing"),
                        help=("r2 = the sanctioned oracle.md addendum command (M17 only); "
                              "closing = process history, handoff and the closing recorder"))
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt_root)
    if args.phase == "r2":
        units = card_units.r2_units(args.card, attempt)
        record_name = "r2_run.json"
    else:
        units = card_units.closing_units(args.card, attempt)
        record_name = "closing_run.json"
    failures = []
    for unit in units:
        code = run_unit.capture(unit["argv"], unit["stdout"], unit["stderr"], unit["rc_record"],
                                unit["unit_id"], cwd=unit["cwd"])
        print("[%s] rc=%s expected=%s" % (unit["unit_id"], code, unit["expected_rc"]))
        if code != unit["expected_rc"]:
            failures.append(unit["unit_id"])
    os.makedirs(os.path.join(attempt, "recovery"), exist_ok=True)
    out = os.path.join(attempt, "recovery", record_name)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump({"card_id": args.card, "attempt_root": attempt, "phase": args.phase,
                   "units": [u["unit_id"] for u in units], "failed_units": failures},
                  handle, ensure_ascii=False, indent=1)
    print("phase", args.phase, "failures:", failures, "->", out)
    return 0 if not failures else 3


if __name__ == "__main__":
    raise SystemExit(main())
