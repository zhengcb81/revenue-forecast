"""Run the full chronological unit list of one card attempt, capturing every raw rc.

This driver only starts subprocesses and stores their raw output; it never rewrites a
return code and never decides a business result.  The unit list is the single source of
truth in card_units.py, so the argv recorded in commands.json is literally the argv
executed here.

Usage:
  python -X utf8 -B run_pipeline.py --card M17 --attempt-root <attempt>
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
    units = card_units.build_units(card, attempt)

    driver = {
        "card_id": card,
        "attempt_root": attempt,
        "orchestrator_interpreter": sys.executable,
        "orchestrator_note": ("the orchestrator creates the attempt venv and starts each unit as a "
                             "subprocess; it decides nothing about the business result"),
        "units_run": [],
    }
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
    os.makedirs(attempt, exist_ok=True)
    with open(os.path.join(attempt, "pipeline_run.json"), "w", encoding="utf-8") as handle:
        json.dump(driver, handle, ensure_ascii=False, indent=1)
    print("units run:", len(driver["units_run"]), "failures:", failures)
    return 0 if not failures else 3


if __name__ == "__main__":
    raise SystemExit(main())
