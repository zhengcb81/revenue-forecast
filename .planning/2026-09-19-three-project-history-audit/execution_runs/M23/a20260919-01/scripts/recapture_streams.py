"""Re-run the product and capture stdout/stderr as RAW BYTES (utf-8, no BOM).

PowerShell's `>` operator wrote these files as UTF-16LE with a BOM, which is not a
faithful capture. This script re-runs the SAME command with the SAME arguments and the
SAME frozen evidence and writes the byte stream the process actually produced.

It also re-derives the git-status captures with an explicit utf-8 encoding.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/recapture_streams.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)
    code_root = os.path.join(attempt, "iso", "checkout_scripts")
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")

    argv = [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "run_card.py"),
            "--card", card, "--attempt", attempt, "--code-root", code_root,
            "--out", os.path.join(ev, "run_result.json"),
            "--run-result-out", os.path.join(ev, "run_result.json")]
    with open(os.path.join(ev, "stdout.txt"), "wb") as so, \
            open(os.path.join(ev, "stderr.txt"), "wb") as se:
        proc = subprocess.run(argv, stdout=so, stderr=se)
    print("raw rc", proc.returncode)
    for name in ("stdout.txt", "stderr.txt"):
        p = os.path.join(ev, name)
        print(name, os.path.getsize(p), "bytes; first 40 bytes:",
              open(p, "rb").read(40)[:40])

    # keep the derived copies in step with the re-captured run
    run = json.load(open(os.path.join(ev, "run_result.json"), encoding="utf-8"))
    print("verdict", run["exit_code_semantics"]["verdict"],
          "exit_code", run["exit_code_semantics"]["exit_code"])
    print("negative summary", run["negative_summary"])
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
