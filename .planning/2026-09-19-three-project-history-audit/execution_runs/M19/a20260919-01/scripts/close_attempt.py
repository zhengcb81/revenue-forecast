"""Close one attempt: record the command list, then hash every artefact.

This is deliberately the LAST command of the attempt, so the dependency runs one way:

  1. write_handoff.py                 -> handoff.json, refreshed here so that the H unit's own raw
                                         rc is already recorded when the handoff is written
  2. write_commands.py --phase final  -> commands.json with every unit's raw rc read back
                                         from its own rc.json (this closing unit's own rc is the
                                         single value that cannot exist yet; that is stated in the
                                         record instead of being invented)
  3. write_final_hashes.py            -> after/final_deliverable_hashes.json covering everything
                                         that exists, including commands.json itself

Usage:
  python -X utf8 -B close_attempt.py --card M17 --attempt-root <attempt> --interpreter <python.exe>
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

import card_units


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(card_units.CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--interpreter", default=sys.executable)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    scripts = os.path.join(attempt, "scripts")

    steps = [
        [args.interpreter, "-X", "utf8", "-B", os.path.join(scripts, "write_handoff.py"),
         "--card", card, "--attempt-root", attempt],
        [args.interpreter, "-X", "utf8", "-B", os.path.join(scripts, "write_commands.py"),
         "--card", card, "--attempt-root", attempt, "--interpreter", args.interpreter,
         "--phase", "final"],
        [args.interpreter, "-X", "utf8", "-B", os.path.join(scripts, "write_final_hashes.py"),
         "--card", card, "--attempt-root", attempt],
    ]
    codes = []
    for argv in steps:
        print("close_attempt step:", os.path.basename(argv[4]))
        code = subprocess.run(argv).returncode
        codes.append(code)
        if code != 0:
            print("close_attempt: step failed with rc", code)
            return code
    print("close_attempt: handoff refreshed, commands.json refreshed and final hash table written; "
          "rcs", codes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
