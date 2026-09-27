"""I-14-B changes.diff generator (attempt-local only).

Emits a unified diff between the BEFORE revision of the subject under test and
the AFTER revision, prefixed with both sha256 values so a reviewer can verify the
diff is complete and regenerates identically.

Usage:
  <iso-python> -X utf8 -B harness/make_diff.py
"""

from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
BEFORE = ATTEMPT / "before" / "natural_window.baseline.py"
AFTER = ATTEMPT / "iso" / "natural_window.py"
OUT = ATTEMPT / "changes.diff"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    before_lines = BEFORE.read_text(encoding="utf-8").splitlines(keepends=True)
    after_lines = AFTER.read_text(encoding="utf-8").splitlines(keepends=True)
    header = (
        "# I-14-B changes.diff -- attempt-local subject under test ONLY\n"
        "# product trees (revenue-forecast / filing-fetch / company-wiki) are NOT modified by this card\n"
        f"# before: before/natural_window.baseline.py  sha256={sha256(BEFORE)}\n"
        f"# after:  iso/natural_window.py              sha256={sha256(AFTER)}\n"
        "# regenerate: <iso-python> -X utf8 -B harness/make_diff.py\n"
    )
    diff = difflib.unified_diff(
        before_lines, after_lines,
        fromfile="a/iso/natural_window.py (BEFORE)",
        tofile="b/iso/natural_window.py (AFTER)",
        n=3,
    )
    text = header + "".join(diff)
    OUT.write_text(text, encoding="utf-8")
    added = sum(1 for line in text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in text.splitlines() if line.startswith("-") and not line.startswith("---"))
    print(f"changes.diff written: +{added} -{removed} lines, {len(text)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
