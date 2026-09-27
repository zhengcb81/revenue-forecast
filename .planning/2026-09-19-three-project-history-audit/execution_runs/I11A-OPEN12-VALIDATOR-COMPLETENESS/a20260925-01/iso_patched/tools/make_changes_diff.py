"""I-11-A: write changes.diff.

This card changes no production file, so the diff is the inventory of files inside
this attempt (add-only) plus a timepoint-qualified statement about the production
repositories.

TIME POINT RULE (post-review correction, finding P1-1): the production porcelain
counts printed here are the values observed AT GENERATION TIME, with that time
printed next to them. Other actors commit to these repositories concurrently (for
example commit ddc81ab on 2026-09-20 04:09 local), so the counts must not be read as
a property of the card; they are a dated observation.

SELF-REFERENCE RULE (finding P1-2): this file is listed inside itself and inside
attempt_hashes.json. It can therefore never contain its own final hash. Re-run this
tool after every other edit, then re-run tools/hash_attempt.py last.

Usage: python -X utf8 -B tools/make_changes_diff.py <attempt_root>
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def porcelain(path: str):
    p = subprocess.run(["git", "-C", path, "status", "--porcelain"], capture_output=True)
    text = p.stdout.decode("utf-8", "replace")
    lines = text.splitlines()
    return len(lines), sum(1 for x in lines if not x.startswith("??"))


def main() -> int:
    attempt = sys.argv[1]
    ev = os.path.join(attempt, "evidence", "I-11-A")
    b = json.load(open(os.path.join(ev, "state_before.json"), encoding="utf-8"))
    after = json.load(open(os.path.join(ev, "state_after.json"), encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    files = []
    excluded = []
    for base, dirs, names in os.walk(attempt):
        rel_base = os.path.relpath(base, attempt).replace("\\", "/")
        if rel_base.startswith("iso/venv"):
            excluded.append("iso/venv/**")
            dirs[:] = []
            continue
        if os.path.basename(base) == "__pycache__":
            excluded.append(rel_base + "/**")
            dirs[:] = []
            continue
        for n in sorted(names):
            if n.endswith(".pyc"):
                excluded.append(os.path.relpath(os.path.join(base, n), attempt).replace("\\", "/"))
                continue
            p = os.path.join(base, n)
            rel = os.path.relpath(p, attempt).replace("\\", "/")
            files.append((rel, os.path.getsize(p), sha256(p)))
    files.sort()

    lines = []
    lines.append("diff --git I-11-A/a20260919-01 (new files only; no production file modified)")
    lines.append("# generated_at_utc : %s" % now)
    lines.append("# card             : I-11-A")
    lines.append("# attempt          : execution_runs/I-11-A/a20260919-01")
    lines.append("#")
    lines.append("# PRODUCTION DIFF  : NONE. This card has no write path to the three production")
    lines.append("#                    repositories; the only bound write root is this attempt directory.")
    lines.append("#                    That claim is supported by the independent review (review.md")
    lines.append("#                    section 5), NOT by the state-capture pair alone: both captures were")
    lines.append("#                    taken during this attempt (review finding P1-1).")
    lines.append("#")
    lines.append("# dated observation (porcelain entries at generation time; other actors commit to")
    lines.append("# these repositories concurrently, so these counts are NOT a property of this card):")
    for name in ("revenue-forecast", "company-wiki", "filing-fetch"):
        repo = b["production_repos"][name]["path"]
        total, tracked = porcelain(repo)
        lines.append("#   %-18s HEAD(captured)=%s  porcelain(now)=%d (tracked %d, untracked %d)"
                     % (name, b["production_repos"][name]["head"][:12], total, tracked,
                        total - tracked))
    lines.append("#   key files identical between the two captures: %s"
                 % (b["key_files"] == after["key_files"]))
    lines.append("#   PLAN/reviews directory mtime: %s ; newest file inside: %s"
                 % (b.get("plan_reviews", {}).get("mtime_local"),
                    (b.get("plan_reviews", {}).get("newest_file") or {}).get("mtime_local")))
    lines.append("#   (this attempt created or modified no file under PLAN/reviews)")
    lines.append("#")
    lines.append("# SELF-REFERENCE    : changes.diff and attempt_hashes.json each list themselves and")
    lines.append("#                    therefore cannot carry their own final hash; both are")
    lines.append("#                    regenerated last (tools/make_changes_diff.py, then")
    lines.append("#                    tools/hash_attempt.py).")
    lines.append("#")
    lines.append("# excluded from this inventory: %s" % ", ".join(sorted(set(excluded))))
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
