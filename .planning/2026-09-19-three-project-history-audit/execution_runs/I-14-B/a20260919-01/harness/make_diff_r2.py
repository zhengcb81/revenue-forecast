"""I-14-B changes.r2.diff generator: the P1/P2 fix only (r1 -> r2 SUT).

changes.diff (r1: BEFORE -> AFTER-r1) is preserved byte-identically; this script
writes a second, separate diff so the reviewer can see exactly what the
`changes_required` fix touched.

Usage:
  <iso-python> -X utf8 -B harness/make_diff_r2.py
"""

from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
R1 = HERE / "archive" / "natural_window.after-r1.py"
R2 = ATTEMPT / "iso" / "natural_window.py"
OUT = ATTEMPT / "changes.r2.diff"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    before_lines = R1.read_text(encoding="utf-8").splitlines(keepends=True)
    after_lines = R2.read_text(encoding="utf-8").splitlines(keepends=True)
    header = (
        "# I-14-B changes.r2.diff -- the fix for the independent review's blocking findings\n"
        "# r1 (reviewed, preserved at harness/archive/natural_window.after-r1.py) sha256="
        f"{sha256(R1)}\n"
        f"# r2 (fixed) iso/natural_window.py sha256={sha256(R2)}\n"
        "# findings fixed: P1 claim.basis closed enumeration (J16); P2 quick_check excluded from the\n"
        "# natural observation intervals + J15 for a declared window that covers quick_check;\n"
        "# sibling J4b (absent interval is unmeasured); P3-a J10c (same-UTC-day run ignored and reported)\n"
        "# regenerate: <iso-python> -X utf8 -B harness/make_diff_r2.py\n"
        "# changes.diff remains the r1 diff (BEFORE -> AFTER-r1) and is NOT overwritten.\n"
    )
    diff = difflib.unified_diff(
        before_lines, after_lines,
        fromfile="a/iso/natural_window.py (AFTER-r1, reviewed)",
        tofile="b/iso/natural_window.py (AFTER-r2, P1/P2 fixed)",
        n=3,
    )
    text = header + "".join(diff)
    OUT.write_text(text, encoding="utf-8")
    added = sum(1 for line in text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in text.splitlines() if line.startswith("-") and not line.startswith("---"))
    print(f"changes.r2.diff written: +{added} -{removed} lines, {len(text)} bytes, "
          f"sha256 {sha256(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
