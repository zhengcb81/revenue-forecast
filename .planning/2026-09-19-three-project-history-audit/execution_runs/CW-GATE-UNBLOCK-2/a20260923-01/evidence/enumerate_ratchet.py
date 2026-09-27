"""Enumerate EVERY ratchet violation (test logic verbatim) — no first-abort masking.

Usage (cwd = iso repo root): python enumerate_ratchet.py
Prints every frozen-file violation + every new-file violation.
"""
import importlib.util as u
import sys
from pathlib import Path

spec = u.spec_from_file_location("ratchet", r"tests\contract\test_fc1204_complexity_ratchet.py")
m = u.module_from_spec(spec)
spec.loader.exec_module(m)

SRC = Path(r"src\company_wiki\source_catalog")
viol = []
for rel, frozen in sorted(m.FROZEN_MAX.items()):
    p = SRC / rel
    if not p.is_file():
        viol.append((rel, "MISSING", frozen))
        continue
    a = m._max_complexity(p.read_text(encoding="utf-8"))
    if a > frozen:
        viol.append((rel, a, frozen))
print("FROZEN-FILE VIOLATIONS:", len(viol))
for rel, a, f in viol:
    print(f"  VIOLATION {rel}: actual={a} frozen={f}")

extra = []
for p in sorted(SRC.rglob("*.py")):
    rel = str(p.relative_to(SRC)).replace("\\", "/")
    if rel in m.FROZEN_MAX:
        continue
    a = m._max_complexity(p.read_text(encoding="utf-8"))
    if a > m.NEW_FILE_MAX:
        extra.append((rel, a))
print("NEW-FILE VIOLATIONS:", len(extra))
for rel, a in extra:
    print(f"  NEWVIOLATION {rel}: actual={a} max={m.NEW_FILE_MAX}")
sys.exit(0)
