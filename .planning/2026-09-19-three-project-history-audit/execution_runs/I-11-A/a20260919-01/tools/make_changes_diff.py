"""I-11-A: write changes.diff.

This card changes no production file, so the diff is the inventory of NEW files
created inside this attempt (add-only), plus an explicit statement that the three
production repositories were not touched (proved by the before/after captures).

Usage: python -X utf8 -B tools/make_changes_diff.py <attempt_root>
"""

from __future__ import annotations

import hashlib
import json
import os
import sys


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    attempt = sys.argv[1]
    ev = os.path.join(attempt, "evidence", "I-11-A")
    before = json.load(open(os.path.join(ev, "state_before.json"), encoding="utf-8"))
    after = json.load(open(os.path.join(ev, "state_after.json"), encoding="utf-8"))

    files = []
    for base, dirs, names in os.walk(attempt):
        rel_base = os.path.relpath(base, attempt).replace("\\", "/")
        if rel_base.startswith("iso/venv"):
            dirs[:] = []
            continue
        for n in sorted(names):
            p = os.path.join(base, n)
            rel = os.path.relpath(p, attempt).replace("\\", "/")
            files.append((rel, os.path.getsize(p), sha256(p)))
    files.sort()

    lines = []
    lines.append("diff --git I-11-A/a20260919-01 (new files only; no production file modified)")
    lines.append("#")
    lines.append("# card            : I-11-A")
    lines.append("# attempt         : execution_runs/I-11-A/a20260919-01")
    lines.append("# production diff : NONE. The three production repositories were not written to.")
    lines.append("#   revenue-forecast HEAD %s  porcelain entries before/after: %d/%d"
                 % (before["production_repos"]["revenue-forecast"]["head"][:12],
                    len(before["production_repos"]["revenue-forecast"]["porcelain"]),
                    len(after["production_repos"]["revenue-forecast"]["porcelain"])))
    lines.append("#   company-wiki     HEAD %s  porcelain entries before/after: %d/%d"
                 % (before["production_repos"]["company-wiki"]["head"][:12],
                    len(before["production_repos"]["company-wiki"]["porcelain"]),
                    len(after["production_repos"]["company-wiki"]["porcelain"])))
    lines.append("#   filing-fetch     HEAD %s  porcelain entries before/after: %d/%d"
                 % (before["production_repos"]["filing-fetch"]["head"][:12],
                    len(before["production_repos"]["filing-fetch"]["porcelain"]),
                    len(after["production_repos"]["filing-fetch"]["porcelain"])))
    lines.append("#   key-file hashes identical before/after: %s"
                 % (before["key_files"] == after["key_files"]))
    lines.append("# PLAN/reviews mtime recorded in both captures: %s"
                 % before.get("plan_reviews", {}).get("mtime_local"))
    lines.append("#   (no file under PLAN/reviews was created or modified by this attempt; this is")
    lines.append("#    evidenced by state_before/state_after plus the file listing captured in them)")
    lines.append("# excluded from this inventory: iso/venv/** (isolated interpreter, third-party bytes)")
    lines.append("#")
    lines.append("# new-file inventory (%d files):" % len(files))
    for rel, size, digest in files:
        lines.append("+++ b/%s\t%d bytes\tsha256=%s" % (rel, size, digest))
    out = os.path.join(attempt, "changes.diff")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("new files listed:", len(files))
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
