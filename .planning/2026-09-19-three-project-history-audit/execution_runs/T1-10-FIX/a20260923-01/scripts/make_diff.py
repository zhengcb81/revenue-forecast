"""T1-10-FIX: build changes.diff WITHOUT git (difflib, labels a/ b/).

Generates the delivery artifact from two pairs:
  1. iso/natural_window.py               : pristine r2 baseline -> fixed (the repair)
  2. harness/tests/test_i14b_natural_window_basis_total.py : /dev/null -> new file
     (the durable malformed-basis negative family + machinery-intact control the
      M-T-REVIEW block asks the fix card to carry)

Usage:
  <python> scripts/make_diff.py --baseline <pristine.py> --fixed <fixed.py>
      --new-file <new_test.py> --out changes.diff
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
        tofile="b/harness/tests/test_i14b_natural_window_basis_total.py"))

    text = "".join(parts)
    out = Path(args.out)
    out.write_text(text, encoding="utf-8", newline="")

    added = sum(1 for ln in parts if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in parts if ln.startswith("-") and not ln.startswith("---"))
    stats = {
        "files_touched": [
            {"path": "iso/natural_window.py",
             "change": "modified (defect-1 total claim.basis validation)",
             "baseline_sha256": sha256_file(baseline),
             "fixed_sha256": sha256_file(fixed)},
            {"path": "harness/tests/test_i14b_natural_window_basis_total.py",
             "change": "added (malformed-basis negative family + batch-intact control)",
             "sha256": sha256_file(new_file)},
        ],
        "lines_added": added,
        "lines_removed": removed,
        "changes_diff_bytes": out.stat().st_size,
        "changes_diff_sha256": sha256_file(out),
        "no_git": True,
    }
    Path(args.stats).write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
