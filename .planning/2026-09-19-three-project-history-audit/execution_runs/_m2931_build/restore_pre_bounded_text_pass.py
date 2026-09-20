"""Restore the pre-bounded-text-pass copies of the files that pass rewrites.

Development-iteration helper: the pass is append-only / supersede-based, so re-running it after a
failed attempt needs the inputs back in their pre-pass state.  Copies come from
recovery/pre_bounded_text_pass/ (taken before the first write) and are reported with sha256.

Usage:
  python -X utf8 -B restore_pre_bounded_text_pass.py --card M29 --attempt-root <attempt>
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
    backup_dir = os.path.join(attempt, "recovery", "pre_bounded_text_pass")
    restored = []
    for root, _dirs, names in os.walk(backup_dir):
        for name in names:
            src = os.path.join(root, name)
            rel = os.path.relpath(src, backup_dir)
            dst = os.path.join(attempt, rel)
            before = sha256(dst) if os.path.isfile(dst) else None
            shutil.copyfile(src, dst)
            restored.append(rel.replace("\\", "/"))
            print("%-52s %s -> %s" % (rel.replace("\\", "/"), (before or "None")[:16],
                                      sha256(dst)[:16]))
    print("restored", len(restored), "files", restored)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
