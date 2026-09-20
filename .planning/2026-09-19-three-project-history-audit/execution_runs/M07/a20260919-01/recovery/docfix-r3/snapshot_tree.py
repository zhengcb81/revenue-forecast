"""Snapshot every file of the four attempts as  <relpath>  <sha256>  <bytes>.

The doc fix must be provable as a *closed* change set: snapshot before, snapshot
after, diff the two snapshots. iso/venv is excluded (it is the template
interpreter, thousands of third-party files, and is never touched).

Usage:
  <iso venv python> -X utf8 -B snapshot_tree.py <label> <out.txt>

Writes <out.txt> (ASCII, LF) and prints only the file count and the total.
"""
from __future__ import annotations

import hashlib
import os
import sys

BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    label = argv[1] if len(argv) > 1 else "snapshot"
    out = argv[2] if len(argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), f"tree_{label}.txt"
    )
    rows: list[str] = []
    for card in CARDS:
        root = os.path.join(BASE, card, "a20260919-01")
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("venv", "__pycache__")]
            for name in filenames:
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, root).replace("\\", "/")
                rows.append(f"{card}/{rel}\t{sha256_file(full)}\t{os.path.getsize(full)}")
    rows.sort()
    with open(out, "w", encoding="ascii", newline="\n") as fh:
        fh.write(f"# label={label}\n")
        fh.write("# card/relpath\tsha256\tbytes\n")
        for row in rows:
            fh.write(row + "\n")
    print(f"{label}: files={len(rows)} out={out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
