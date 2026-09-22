#!/usr/bin/env python3
"""pack_evidence.py — compact live findings list, marker histogram, changes.diff.

Reads evidence/live/live_scan.json (raw checker output) and writes:
  evidence/live/findings_file_line_list.txt  (file:line:[markers] excerpt)
  evidence/live/summary.json                 (counts + marker histogram)
  changes.diff                               (RED -> GREEN code delta)
"""
import collections
import difflib
import json
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent


def main() -> int:
    rep = json.loads(
        (ATTEMPT / "evidence/live/live_scan.json").read_text(encoding="utf-8")
    )
    out = []
    hist = collections.Counter()
    per_file = {}
    for f in rep["files"]:
        path = f["path"]
        per_file[path] = len(f["violations"])
        for v in f["violations"]:
            hist.update(v["markers"])
            out.append(
                f"{path}:{v['line']}:[{','.join(v['markers'])}] {v['excerpt'][:110]}"
            )
    (ATTEMPT / "evidence/live/findings_file_line_list.txt").write_text(
        "\n".join(out) + "\n", encoding="utf-8"
    )
    summary = {
        "total_violations": rep["totals"]["violations"],
        "per_file": per_file,
        "marker_histogram": dict(hist.most_common()),
        "note": "per the frozen REM-79 contract these are DETECTIONS by a "
        "heuristic, not adjudicated defects; the plan-file owners decide",
    }
    (ATTEMPT / "evidence/live/summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    a = (ATTEMPT / "harness/naive_checker_marker_only.py").read_text(
        encoding="utf-8"
    ).splitlines(keepends=True)
    b = (ATTEMPT / "tools/check_domain_assertions.py").read_text(
        encoding="utf-8"
    ).splitlines(keepends=True)
    diff = list(
        difflib.unified_diff(
            a, b,
            fromfile="harness/naive_checker_marker_only.py (RED)",
            tofile="tools/check_domain_assertions.py (GREEN)",
            n=3,
        )
    )
    header = [
        "# changes.diff — REM79-MECHANIZATION\n",
        "# The RED->GREEN code delta: naive marker-only detection gains the frozen\n",
        "# same-line domain requirement (D1-D7). All other attempt files (oracle.md,\n",
        "# oracle_table.json, corpus/, harness/, evidence/) are NEW files created inside\n",
        "# this attempt; NO plan file, product file, other attempt or git state was\n",
        "# modified by this card.\n",
    ]
    (ATTEMPT / "changes.diff").write_text(
        "".join(header + diff), encoding="utf-8"
    )
    print(f"changes.diff lines: {len(header) + len(diff)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
