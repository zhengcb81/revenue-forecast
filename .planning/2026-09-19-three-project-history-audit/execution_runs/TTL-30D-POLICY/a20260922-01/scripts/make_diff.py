"""Emit changes.diff: unified diff production-guard -> iso-guard (no git).

Usage: python make_diff.py <production_guard.py> <iso_guard.py> <out.diff>
"""
import difflib
import sys
from pathlib import Path

prod = Path(sys.argv[1])
iso = Path(sys.argv[2])
out = Path(sys.argv[3])
a = prod.read_text(encoding="utf-8").splitlines(keepends=True)
b = iso.read_text(encoding="utf-8").splitlines(keepends=True)
text = "".join(
    difflib.unified_diff(
        a, b,
        fromfile="company-wiki/src/company_wiki/source_catalog/prompt_injection_guard.py",
        tofile="execution_runs/TTL-30D-POLICY/a20260922-01/iso/prompt_injection_guard.py",
    )
)
out.write_text(text, encoding="utf-8")
print(f"diff_lines={len(text.splitlines())} hunks={text.count(chr(10) + '@@') + text.startswith('@@')}")
