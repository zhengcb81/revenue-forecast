"""T1-F2-FIX: build changes.diff WITHOUT git (difflib, labels a/ b/).

Base = T1-10-FIX's FIXED iso (sha256 064e5381..., i.e. their changes.diff
625ecfe4... already applied).  Merge order: theirs first, mine second,
T1-F3-FIX third.  This script diffs that fixed iso against this card's fixed
iso, so the hunks apply ON TOP of their tree.

Usage:
  <python> scripts/make_diff.py --baseline <t1_10_fixed.py> --fixed <fixed.py>
      --new-file <new_test.py> --out changes.diff --stats diff_stats.json
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--fixed", required=True)
    ap.add_argument("--new-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stats", required=True)
    args = ap.parse_args()

    baseline = Path(args.baseline)
    fixed = Path(args.fixed)
    new_file = Path(args.new_file)

    parts: list[str] = []

    a_lines = baseline.read_text(encoding="utf-8").splitlines(keepends=True)
    b_lines = fixed.read_text(encoding="utf-8").splitlines(keepends=True)
    parts.extend(difflib.unified_diff(
        a_lines, b_lines,
        fromfile="a/iso/natural_window.py",
        tofile="b/iso/natural_window.py"))

    n_lines = new_file.read_text(encoding="utf-8").splitlines(keepends=True)
    parts.extend(difflib.unified_diff(
        [], n_lines,
        fromfile="/dev/null",
        tofile="b/harness/tests/test_i14b_natural_window_container_total.py"))

    text = "".join(parts)
    out = Path(args.out)
    out.write_text(text, encoding="utf-8", newline="")

    added = sum(1 for ln in parts if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in parts if ln.startswith("-") and not ln.startswith("---"))

    # hunk inventory + context-range measurement (merge-order line bookkeeping)
    hunks = []
    old_lines = a_lines
    for ln in parts:
        if ln.startswith("@@"):
            head = ln.splitlines()[0]
            # @@ -a,b +c,d @@
            first = head.split()[1].lstrip("-").split(",")[0]
            count = head.split()[1].lstrip("-").split(",")[1] if "," in head.split()[1] \
                else "1"
            start, cnt = int(first), int(count)
            hunks.append({"old_start": start, "old_count": cnt,
                          "old_range": [start, start + cnt - 1] if cnt else [start, start]})
    stats = {
        "files_touched": [
            {"path": "iso/natural_window.py",
             "change": "modified (F-1 clock tuple + F-2 fail-closed carrier guard "
                       "+ P4 classify-entry container normalisation)",
             "baseline_sha256": sha256_file(baseline),
             "baseline_meaning": "T1-10-FIX fixed iso (their changes.diff 625ecfe4... applied)",
             "fixed_sha256": sha256_file(fixed)},
            {"path": "harness/tests/test_i14b_natural_window_container_total.py",
             "change": "added (F-1/F-2/P4 container-totality negative family + "
                       "batch/adjudication controls)",
             "sha256": sha256_file(new_file)},
        ],
        "lines_added": added,
        "lines_removed": removed,
        "hunks": hunks,
        "changes_diff_bytes": out.stat().st_size,
        "changes_diff_sha256": sha256_file(out),
        "merge_order": "T1-10-FIX 625ecfe4... first -> this diff (base 064e5381...) "
                       "second -> T1-F3-FIX third",
        "no_git": True,
    }
    Path(args.stats).write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
