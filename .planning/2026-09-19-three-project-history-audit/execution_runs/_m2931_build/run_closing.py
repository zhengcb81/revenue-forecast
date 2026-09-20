"""Run the closing units of one M29/M30/M31 attempt (handoff, docs, command record, hashes).

The closing units live in card_units.closing_units() and are NOT part of the measurement chain
that run_pipeline.py drives; this script executes exactly that list through the same capture
mechanism (run_unit.capture), in order, and stops on the first unit that does not return its
expected raw return code.

Usage:
  python -X utf8 -B run_closing.py --card M29 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import card_units
import run_unit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    units = card_units.closing_units(card, attempt)

    driver = {"card_id": card, "attempt_root": attempt, "stage": "closing",
              "orchestrator_interpreter": sys.executable, "units_run": []}
    failures = []
    for unit in units:
        code = run_unit.capture(unit["argv"], unit["stdout"], unit["stderr"], unit["rc_record"],
                                unit["unit_id"], cwd=unit["cwd"])
        print("[%s] rc=%s expected=%s" % (unit["unit_id"], code, unit["expected_rc"]))
        driver["units_run"].append({"unit_id": unit["unit_id"], "raw_rc": code,
                                    "expected_rc": unit["expected_rc"],
                                    "rc_record": unit["rc_record"]})
        if code != unit["expected_rc"]:
            failures.append(unit["unit_id"])
            print("  !! unit %s returned %s but %s was expected; stopping"
                  % (unit["unit_id"], code, unit["expected_rc"]))
            break

    driver["failed_units"] = failures
    driver["all_units_matched_expected_rc"] = not failures
    out = os.path.join(attempt, "closing_run.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(driver, handle, ensure_ascii=False, indent=1)
    print("closing units run:", len(driver["units_run"]), "failures:", failures, "->", out)
    return 0 if not failures else 3


if __name__ == "__main__":
    raise SystemExit(main())
