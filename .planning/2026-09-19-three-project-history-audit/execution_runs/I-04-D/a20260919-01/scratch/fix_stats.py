"""Install the lock-attempt counter (correct patterns) and rerun the corrections."""

from __future__ import annotations

import pathlib
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)
text = PATCHER.read_text(encoding="utf-8")

OLD_STATS = '''    stats.setdefault("lease_lock_waits", 0)
    stats.setdefault("lease_lock_acquisitions", 0)'''
NEW_STATS = '''    stats.setdefault("lease_lock_waits", 0)
    stats.setdefault("lease_lock_attempts", 0)
    stats.setdefault("lease_lock_acquisitions", 0)'''
actual = text.count('stats.setdefault("lease_lock_waits", 0)')
print(f"lease_lock_waits setdefault occurrences: {actual}")
if OLD_STATS in text:
    text = text.replace(OLD_STATS, NEW_STATS, 1)
    print("stats defaults patched")
else:
    # find the real shape
    index = text.find('lease_lock_waits')
    print("context:", repr(text[index - 200 : index + 300]))
    sys.exit(1)
PATCHER.write_text(text, encoding="utf-8")
