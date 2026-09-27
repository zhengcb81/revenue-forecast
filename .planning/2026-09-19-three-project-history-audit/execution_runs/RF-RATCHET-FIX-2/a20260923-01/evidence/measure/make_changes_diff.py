"""Build changes.diff — the delivery vehicle for RF-RATCHET-FIX-2.

Exactly 2 files, unified diff, a/ b/ paths relative to the RF repo root:
  scripts/analysis/confidence.py
  scripts/model_extensions.py
Inputs = the attempt's pinned baseline copies (byte == live source per binding.json)
vs the refactored copies actually judged in %TEMP%\\rf2-iso-work.
"""
from __future__ import annotations

import difflib
from pathlib import Path

A = Path(__file__).resolve().parents[2]  # attempt root a20260923-01
OUT = A / "changes.diff"

FILES = [
    ("scripts/analysis/confidence.py", A / "iso" / "confidence.py.baseline", A / "iso" / "confidence.py.refactored"),
    ("scripts/model_extensions.py", A / "iso" / "model_extensions.py.baseline", A / "iso" / "model_extensions.py.refactored"),
]

chunks: list[str] = []
for rel, before, after in FILES:
    # bytes -> decode: no newline translation (byte-exact hunks)
    old = before.read_bytes().decode("utf-8").splitlines(keepends=True)
    new = after.read_bytes().decode("utf-8").splitlines(keepends=True)
    diff = list(
        difflib.unified_diff(
            old, new, fromfile="a/" + rel, tofile="b/" + rel, n=3
        )
    )
    assert diff, f"no diff for {rel}"
    chunks.append("".join(diff))

OUT.write_text("".join(chunks), encoding="utf-8", newline="")
names = [rel for rel, _, _ in FILES]
print(f"changes.diff written: {OUT} ({OUT.stat().st_size} bytes)")
print("files:", names)
assert names == ["scripts/analysis/confidence.py", "scripts/model_extensions.py"]
