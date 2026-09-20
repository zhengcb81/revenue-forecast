"""Execute the closing units of one attempt, then the verifier unit (P3-A of the r3 review).

Order, in ONE command so that the last step is reproducible by a single invocation:

  1. card_units.closing_units()   -> P-write-process-history, T-transcribe-review-verdict,
                                     H-write-handoff, Z-close-attempt
  2. card_units.verifier_units()  -> V-verify-hash-tables (measures both hash tables AFTER Z wrote
                                     them, and exits non-zero if either table drifted)

Before P3-A the verifier unit had no driver at all: `verifier_units()` was only *listed* by
write_commands.py / write_process_history.py, so the last step could not be reproduced by a single
command.  Both phases now run here, and recovery/closing_run.json records the unit list of each
phase plus its raw rc.

Usage:
  python -X utf8 -B run_closing.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import datetime
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
                              "closing = process history, transcription, handoff, closing recorder, "
                              "then the verifier unit"))
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt_root)
    if args.phase == "r2":
        phases = [("r2", card_units.r2_units(args.card, attempt))]
        record_name = "r2_run.json"
    else:
        phases = [("closing", card_units.closing_units(args.card, attempt)),
                  ("verifier", card_units.verifier_units(args.card, attempt))]
        record_name = "closing_run.json"

    failures = []
    phase_records = []
    ordered_units = []
    for phase_name, units in phases:
        for unit in units:
            ordered_units.append(unit["unit_id"])
            code = run_unit.capture(unit["argv"], unit["stdout"], unit["stderr"], unit["rc_record"],
                                    unit["unit_id"], cwd=unit["cwd"])
            print("[%s] %s rc=%s expected=%s" % (phase_name, unit["unit_id"], code,
                                                 unit["expected_rc"]))
            phase_records.append({"phase": phase_name, "unit_id": unit["unit_id"],
                                  "raw_rc": code, "expected_rc": unit["expected_rc"]})
            if code != unit["expected_rc"]:
                failures.append(unit["unit_id"])
    os.makedirs(os.path.join(attempt, "recovery"), exist_ok=True)
    out = os.path.join(attempt, "recovery", record_name)
    doc = {
        "card_id": args.card,
        "attempt_root": attempt,
        "phase": args.phase,
        "units": ordered_units,
        "phases": [{"phase": name, "units": [u["unit_id"] for u in units]} for name, units in phases],
        "unit_results": phase_records,
        "failed_units": failures,
        "driver": "scripts/run_closing.py",
        "p3_a_note": ("the verifier unit runs inside this same driver, after the closing units, so "
                      "'the last step' is reproducible with one command (r3 review P3-A)"),
        "executed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("phase", args.phase, "failures:", failures, "->", out)
    return 0 if not failures else 3


if __name__ == "__main__":
    raise SystemExit(main())
