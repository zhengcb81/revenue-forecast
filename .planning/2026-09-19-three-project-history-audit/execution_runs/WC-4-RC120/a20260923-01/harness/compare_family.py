"""Compare two family pytest logs byte for byte.

Usage: compare_family.py [before] [after] [outfile]   (paths relative to the
attempt directory; defaults to evidence/rgm/family_{before,after}_raw.txt and
evidence/rgm/family_compare.txt).  The logs were produced by PowerShell `*>`
redirection (UTF-16); this decodes them, diffs them, and writes the comparison
as UTF-8.
"""
from __future__ import annotations

import difflib
import hashlib
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
BEFORE = ATTEMPT / "evidence" / "rgm" / "family_before_raw.txt"
AFTER = ATTEMPT / "evidence" / "rgm" / "family_after_raw.txt"
OUT = ATTEMPT / "evidence" / "rgm" / "family_compare.txt"


def main() -> int:
    before_path = ATTEMPT / sys.argv[1] if len(sys.argv) > 1 else BEFORE
    after_path = ATTEMPT / sys.argv[2] if len(sys.argv) > 2 else AFTER
    out_path = ATTEMPT / sys.argv[3] if len(sys.argv) > 3 else OUT
    before = before_path.read_text("utf-16")
    after = after_path.read_text("utf-16")
    a = before.splitlines()
    b = after.splitlines()
    diff = list(difflib.unified_diff(
        a, b, fromfile="family_before", tofile="family_after", lineterm=""))
    tail_a = [ln for ln in a if "passed" in ln or "failed" in ln]
    tail_b = [ln for ln in b if "passed" in ln or "failed" in ln]
    out = [
        "=== family BEFORE (iso pristine + sibling filing-fetch checkout) ===",
        before,
        "=== family AFTER (iso fixed + identical environment) ===",
        after,
        "=== summary lines ===",
        f"before_summary={tail_a}",
        f"after_summary ={tail_b}",
        "=== unified diff (empty => identical outcomes incl. counts) ===",
    ]
    out.extend(diff if diff else ["<no differences>"])
    out.append(f"diff_lines={len(diff)}")
    out.append(f"before={before_path} sha256={hashlib.sha256(before_path.read_bytes()).hexdigest()}")
    out.append(f"after={after_path} sha256={hashlib.sha256(after_path.read_bytes()).hexdigest()}")
    out.append("skip_xfail_markers_before=" + str(sum(ln.count("s") for ln in a if "skip" in ln)))
    text = "\n".join(out) + "\n"
    out_path.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
