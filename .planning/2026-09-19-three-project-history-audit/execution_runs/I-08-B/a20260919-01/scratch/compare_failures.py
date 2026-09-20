"""Compare the baseline and post-change failure sets nodeid by nodeid.

The two raw transcripts were captured with PowerShell's ``*>`` file redirection,
which writes UTF-16 in Windows PowerShell; the reader therefore sniffs the
encoding instead of assuming UTF-8 (a lesson worth recording: text redirection is
not byte-transparent).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff") or raw[:1] == b"\x00":
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-16", errors="replace")


attempt = Path(sys.argv[1])
pattern = re.compile(r"^FAILED\s+(\S+)")
baseline = {
    pattern.match(line).group(1)
    for line in read_text(attempt / "before" / "c8_baseline_suite.stdout.txt").splitlines()
    if pattern.match(line)
}
after = {
    pattern.match(line).group(1)
    for line in read_text(attempt / "after" / "c8_full_suite.stdout.txt").splitlines()
    if pattern.match(line)
}
print("baseline failures:", len(baseline))
print("after failures   :", len(after))
print()
new = sorted(after - baseline)
fixed = sorted(baseline - after)
print(f"NEW failures introduced by this card: {len(new)}")
for node in new:
    print("  +", node)
print(f"failures that disappeared: {len(fixed)}")
for node in fixed:
    print("  -", node)
(attempt / "after" / "c8_new_failures.txt").write_text(
    "\n".join(new) + "\n", encoding="ascii"
)
(attempt / "after" / "c8_fixed_failures.txt").write_text(
    "\n".join(fixed) + "\n", encoding="ascii"
)
