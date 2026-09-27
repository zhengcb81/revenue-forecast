#!/usr/bin/env python3
"""Diff two parse_junit maps: report every testcase whose status changed.

Exit 0 always; the JSON report carries:
  regressed   passed|skipped -> failed|error  (must be exactly the
              frozen flip-surface expectation, or empty for untouched families)
  fixed       failed|error -> passed
  other       any other transition (must be empty)
Counts both directions so before==after proof is mechanical.
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: diff_family.py <before.json> <after.json> <out.json>")
        return 1
    before = json.load(open(sys.argv[1], encoding="utf-8"))
    after = json.load(open(sys.argv[2], encoding="utf-8"))
    regressed, fixed, other, added, removed = [], [], [], [], []
    for cid in sorted(set(before) | set(after)):
        b, a = before.get(cid), after.get(cid)
        if b is None:
            added.append(cid)
        elif a is None:
            removed.append(cid)
        elif b == a:
            continue
        elif b == "passed" and a in ("failed", "error"):
            regressed.append({"id": cid, "before": b, "after": a})
        elif b in ("failed", "error") and a == "passed":
            fixed.append({"id": cid, "before": b, "after": a})
        else:
            other.append({"id": cid, "before": b, "after": a})
    report = {
        "before_total": len(before),
        "after_total": len(after),
        "regressed": regressed,
        "fixed": fixed,
        "other": other,
        "added": added,
        "removed": removed,
        "identical": not (regressed or fixed or other or added or removed),
    }
    with open(sys.argv[3], "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(json.dumps({k: len(report[k]) for k in ("regressed", "fixed", "other", "added", "removed")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
