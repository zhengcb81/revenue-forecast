"""Generate changes.diff (unified, before -> after) for the patched runner copy.

Usage: make_diff.py <before/run_card.py> <iso/run_card.py> <changes.diff>
Also prints diff_stats (added/removed lines).
"""
from __future__ import annotations

import difflib
import hashlib
import json
import sys


def main() -> int:
    before_path, after_path, out_path = sys.argv[1:4]
    before = open(before_path, encoding="utf-8").read().splitlines(keepends=True)
    after = open(after_path, encoding="utf-8").read().splitlines(keepends=True)
    diff = list(difflib.unified_diff(
        before, after,
        fromfile="before/run_card.py (historical b5fcc685..., byte copy)",
        tofile="iso/run_card.py (M01-M04-PROPAGATE patched copy, REM-21 form)",
        n=3))
    added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.writelines(diff)
    stats = {"added_lines": added, "removed_lines": removed,
             "changes_diff_sha256": hashlib.sha256(open(out_path, "rb").read()).hexdigest(),
             "mirror": "B5-fix-g1a-g3/a20260922-01/M05-M08/runner.diff "
                       "(8263fc833fb48cbe..., 10431 B; its patched runner 489ba7e3... "
                       "is byte-identical to B5-plan-level-remediation's M05-M08 copy)"}
    print(json.dumps(stats, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
