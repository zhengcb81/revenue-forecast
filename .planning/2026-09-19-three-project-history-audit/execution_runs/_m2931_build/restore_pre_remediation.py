"""Restore the pre-remediation copies of every file the remediation pass rewrites.

This is a development-iteration helper: the pass is append-only, so re-running it requires the
inputs to be back in their pre-remediation state.  It copies from recovery/pre_remediation/ (which
was made before the first write) over the working files, and reports before/after sha256.

Usage:
  python -X utf8 -B restore_pre_remediation.py --card M29 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil

CARDS = ("M29", "M30", "M31")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=CARDS)
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    backup_dir = os.path.join(attempt, "recovery", "pre_remediation")
    rels = ["review.md", "binding.json", "handoff.json", "oracle.md",
            "evidence/%s/source_manifest.json" % card,
            "evidence/%s/oq_rulings.json" % card,
            "after/final_deliverable_hashes.json"]
    restored = []
    for rel in rels:
        src = os.path.join(backup_dir, rel.replace("/", os.sep))
        dst = os.path.join(attempt, rel.replace("/", os.sep))
        if not os.path.isfile(src):
            print("skip (no copy):", rel)
            continue
        before = sha256(dst) if os.path.isfile(dst) else None
        shutil.copyfile(src, dst)
        after = sha256(dst)
        restored.append(rel)
        print("%-46s %s -> %s" % (rel, (before or "None")[:16], after[:16]))
    print("restored", len(restored), "files from", backup_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
