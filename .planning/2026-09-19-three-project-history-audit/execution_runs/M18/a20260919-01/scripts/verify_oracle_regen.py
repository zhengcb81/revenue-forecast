"""Prove that the frozen oracle files are byte-for-byte regenerable from the script.

Regenerates input.json / oracle.json / cases.json into an empty scratch tree with the
SAME oracle script and compares sha256 against the frozen files.  The frozen files are
never written to.

Usage:
  python -X utf8 -B verify_oracle_regen.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

CARDS = {
    "M17": "licensing_commercial",
    "M18": "advertising",
    "M19": "gaming",
    "M20": "cohort_subscription",
}


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--interpreter", default=sys.executable,
                        help="interpreter used for the regeneration child (the bound attempt venv)")
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    scratch = os.path.join(attempt, "recovery", "regen_verify")
    if os.path.isdir(scratch):
        shutil.rmtree(scratch)
    os.makedirs(scratch)

    oracle_script = os.path.join(attempt, "scripts", "oracle_%s.py" % card)
    argv = [args.interpreter, "-X", "utf8", "-B", oracle_script,
            "--card", card, "--out-root", scratch]
    completed = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                               errors="replace")
    os.makedirs(os.path.join(scratch, "runs"), exist_ok=True)
    with open(os.path.join(scratch, "default_stdout.txt"), "w", encoding="utf-8") as handle:
        handle.write(completed.stdout or "")
    with open(os.path.join(scratch, "default_stderr.txt"), "w", encoding="utf-8") as handle:
        handle.write(completed.stderr or "")

    comparisons = {}
    all_identical = completed.returncode == 0
    for name in ("input.json", "oracle.json", "cases.json"):
        frozen = os.path.join(evidence, name)
        regenerated = os.path.join(scratch, "evidence", card, name)
        frozen_hash = sha256(frozen)
        regenerated_hash = sha256(regenerated) if os.path.isfile(regenerated) else None
        same = frozen_hash == regenerated_hash
        all_identical = all_identical and same
        comparisons[name] = {
            "frozen_sha256": frozen_hash,
            "regenerated_sha256": regenerated_hash,
            "byte_identical": same,
        }
        print(name, "byte_identical", same, frozen_hash, regenerated_hash)

    doc = {
        "card_id": card,
        "model_id": CARDS[card],
        "rule": ("the frozen oracle files must be reproducible byte-for-byte from the independent "
                 "oracle script, so no hand-edited expectation can hide in them"),
        "argv": argv,
        "raw_returncode": completed.returncode,
        "scratch_root": scratch,
        "frozen_files_untouched_by_this_step": True,
        "comparisons": comparisons,
        "all_byte_identical": all_identical,
    }
    out = os.path.join(evidence, "oracle_regen_proof.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    print("all_byte_identical", all_identical, "->", out)
    return 0 if all_identical else 3


if __name__ == "__main__":
    raise SystemExit(main())
