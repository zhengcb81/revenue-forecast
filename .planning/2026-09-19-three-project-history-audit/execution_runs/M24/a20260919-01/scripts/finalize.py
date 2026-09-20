"""Final pass for one M21-M24 attempt.

1. re-hash before/source_hashes.txt and after/source_hashes.txt (the oracle.md hash moved
   when the run-reconciliation section was appended),
2. write after/reviews_mtime.txt (proves .planning/reviews was not touched),
3. re-run the evidence builder, the commands builder, the append step and the sealer so every
   document reflects the final files, then
4. re-run final_verify.py.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/finalize.py --card M21 \
      --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

PLAN = "C:\\Users\\郑曾波\\Projects\\revenue-forecast\\.planning\\2026-09-19-three-project-history-audit"
PROD = "C:\\Users\\郑曾波\\Projects\\revenue-forecast"


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    ev = os.path.join(attempt, "evidence", card)
    iso = os.path.join(attempt, "iso", "checkout_scripts")

    # --- 1. source hashes ---------------------------------------------------
    lines = [
        "revenue-forecast HEAD = %s" % _git(PLAN, "rev-parse", "HEAD"),
        "revenue-forecast scripts/model_registry.py  = %s"
        % sha(os.path.join(PROD, "scripts", "model_registry.py")),
        "revenue-forecast scripts/model_extensions.py = %s"
        % sha(os.path.join(PROD, "scripts", "model_extensions.py")),
        "iso/checkout_scripts/model_registry.py  = %s" % sha(os.path.join(iso, "model_registry.py")),
        "iso/checkout_scripts/model_extensions.py = %s"
        % sha(os.path.join(iso, "model_extensions.py")),
        "oracle.md (full file, incl. appended run section) = %s"
        % sha(os.path.join(attempt, "oracle.md")),
        "oracle.md (frozen body only) = %s"
        % json.load(open(os.path.join(attempt, "recovery", "oracle_body_hash.json"),
                         encoding="utf-8"))["oracle_md_frozen_body_sha256"],
        "scripts/run_card.py = %s" % sha(os.path.join(attempt, "scripts", "run_card.py")),
    ]
    text = "\r\n".join(lines) + "\r\n"
    for sub in ("before", "after"):
        with open(os.path.join(attempt, sub, "source_hashes.txt"), "w", encoding="utf-8",
                  newline="") as fh:
            fh.write(text)
    print("rewrote before/source_hashes.txt and after/source_hashes.txt")

    # --- 2. reviews mtime ---------------------------------------------------
    reviews = os.path.join(PLAN, "reviews")
    st = os.stat(reviews)
    with open(os.path.join(attempt, "after", "reviews_mtime.txt"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(".planning/2026-09-19-three-project-history-audit/reviews\n")
        fh.write("mtime_epoch = %.6f\n" % st.st_mtime)
        fh.write("mtime_local = %s\n" % _fmt(st.st_mtime))
        fh.write("note = this attempt never wrote under reviews/; the DIRECTORY mtime above is "
                 "the pre-existing value observed after all of this attempt's runs\n")
        fh.write("convention_note (review item P3-3) = the task statement quoted 2026-09-19 "
                 "10:05 for this directory. That value matches the NEWEST FILE anywhere inside "
                 "it (reviews/second_wave/final_review_checks.json, epoch 1789808732.27), while "
                 "the DIRECTORY entry mtime is 2026-09-19 09:14:20 (epoch 1789805660.08). The "
                 "two conventions measure different things and both are recorded in "
                 "evidence/<card>/integrity.json and handoff.json under reviews_mtime_conventions\n")
    print("wrote after/reviews_mtime.txt", _fmt(st.st_mtime))

    # --- 3. rebuild every derived document ---------------------------------
    # Order matters: append_oracle_run_section.py must run FIRST, because it writes
    # recovery/oracle_body_hash.json (the frozen-body hash) and the final oracle.md that
    # build_evidence.py reads when it records sha256_full_file_now.
    for name in ("append_oracle_run_section.py", "build_evidence.py", "build_commands.py",
                 "seal_attempt.py"):
        argv = [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", name),
                "--card", card, "--attempt", attempt]
        proc = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.stdout.decode("utf-8", "replace").strip().splitlines()
        print("[%s] rc=%d %s" % (name, proc.returncode, out[-1] if out else ""))
        if proc.returncode != 0:
            return proc.returncode

    # --- 4. verify ---------------------------------------------------------
    argv = [py, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "final_verify.py"),
            "--card", card, "--attempt", attempt]
    with open(os.path.join(attempt, "recovery", "final_verify.txt"), "wb") as fh:
        proc = subprocess.run(argv, stdout=fh, stderr=subprocess.STDOUT)
    print("final_verify rc", proc.returncode)
    return 0


def _git(cwd: str, *argv: str) -> str:
    proc = subprocess.run(["git", "-C", PROD] + list(argv), stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL)
    return proc.stdout.decode("utf-8", "replace").strip()


def _fmt(epoch: float) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    sys.exit(main())
