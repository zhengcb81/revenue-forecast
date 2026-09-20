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
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt_root)
    failures = []
    for unit in card_units.closing_units(args.card, attempt):
        code = run_unit.capture(unit["argv"], unit["stdout"], unit["stderr"], unit["rc_record"],
                                unit["unit_id"], cwd=unit["cwd"])
        print("[%s] rc=%s expected=%s" % (unit["unit_id"], code, unit["expected_rc"]))
        if code != unit["expected_rc"]:
            failures.append(unit["unit_id"])
    out = os.path.join(attempt, "recovery", "closing_run.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump({"card_id": args.card, "attempt_root": attempt, "failed_units": failures},
                  handle, ensure_ascii=False, indent=1)
    print("closing failures:", failures)
    return 0 if not failures else 3


if __name__ == "__main__":
    raise SystemExit(main())
