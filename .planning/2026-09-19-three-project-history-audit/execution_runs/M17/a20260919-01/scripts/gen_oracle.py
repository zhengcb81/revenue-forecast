"""Freeze record + oracle generation for one card.

Order matters: the hash and mtime of oracle.md are recorded BEFORE the oracle
script runs, so the "expectations were frozen before anything ran" chain does not
depend on a hash captured after the fact.  The child's raw return code is returned
unchanged.

Usage:
  python -X utf8 -B gen_oracle.py --card M17 --attempt-root <attempt> --interpreter <python.exe>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess

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
    parser.add_argument("--interpreter", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    oracle_md = os.path.join(attempt, "oracle.md")
    oracle_script = os.path.join(attempt, "scripts", "oracle_%s.py" % card)

    if not os.path.isfile(oracle_md):
        raise SystemExit("ORACLE FREEZE ERROR: oracle.md must exist before oracle generation")
    if not os.path.isfile(oracle_script):
        raise SystemExit("ORACLE FREEZE ERROR: missing " + oracle_script)

    before = {
        "oracle_md_path": oracle_md,
        "oracle_md_sha256": sha256(oracle_md),
        "oracle_md_mtime": os.path.getmtime(oracle_md),
        "recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "oracle_md_existed_before_generation": True,
    }

    child_argv = [args.interpreter, "-X", "utf8", "-B", oracle_script,
                  "--card", card, "--out-root", attempt]
    completed = subprocess.run(child_argv)
    after = {}
    for name in ("input.json", "oracle.json", "cases.json", "oracle_selfcheck.json"):
        path = os.path.join(evidence, name)
        after["evidence/%s/%s" % (card, name)] = {
            "sha256": sha256(path) if os.path.isfile(path) else None,
            "mtime": os.path.getmtime(path) if os.path.isfile(path) else None,
            "exists": os.path.isfile(path),
        }

    record = {
        "card_id": card,
        "model_id": CARDS[card],
        "oracle_document": before,
        "child_argv": child_argv,
        "child_returncode": completed.returncode,
        "generated_files": after,
        "oracle_md_unchanged_by_generation": sha256(oracle_md) == before["oracle_md_sha256"],
        "mtime_ordering_within_this_step": {
            "oracle_md_mtime": before["oracle_md_mtime"],
            "oracle_json_mtime": after["evidence/%s/oracle.json" % card]["mtime"],
            "oracle_md_precedes_oracle_json": (
                before["oracle_md_mtime"] <= after["evidence/%s/oracle.json" % card]["mtime"]),
        },
        "rule": ("oracle.json is regenerable byte-for-byte from scripts/oracle_%s.py; see "
                 "evidence/%s/oracle_regen_proof.json" % (card, card)),
    }
    out = os.path.join(attempt, "evidence", card, "oracle_document_freeze.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)
    print("oracle frozen: %s sha256 %s" % (oracle_md, before["oracle_md_sha256"]))
    print("child_returncode", completed.returncode)
    print("freeze record ->", out)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
