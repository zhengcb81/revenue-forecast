"""Final two corrections; dump context when a pattern misses."""

from __future__ import annotations

import pathlib
import re
import sys

TEST = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\iso\filing-fetch\tests\test_fetch_filing_lease.py"
)
text = TEST.read_text(encoding="utf-8")

for label, needle in (
    ("both-leases", 'joined = s["participants"]'),
    ("w1b", 'third["reports"]["C"]["action"]'),
):
    index = text.find(needle)
    print(f"--- {label} context ---")
    print(text[max(0, index - 500) : index + 700] if index >= 0 else "NOT FOUND")
