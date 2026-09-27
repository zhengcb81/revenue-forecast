"""String-literal multiset diff: original (production) vs refactored (iso_after).

Zero-behavior evidence: every string literal of the promotion payload must survive the
refactor with the same multiplicity (messages/conditions/comments are the behavior
surface the batteries assert on). Additions are listed explicitly and must each be a
DISCLOSED docstring/prose line, never a modified message.
Usage: python -B literal_diff.py
"""
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
ISO = Path(r"C:\Users\郑曾波\AppData\Local\Temp\rf-rest-b\iso_after\scripts")
FILES = ["model_registry.py", "revenue_core.py", "revenue_publication.py"]


def literals(path: Path) -> Counter:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: Counter = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            # covers plain strings AND the literal pieces of f-strings
            out[node.value] += 1
    return out


ok = True
for name in FILES:
    before = literals(RF / "scripts" / name)
    after = literals(ISO / name)
    missing = before - after
    added = after - before
    print(f"== {name}: before={sum(before.values())} after={sum(after.values())} "
          f"missing={sum(missing.values())} added={sum(added.values())}")
    for lit, n in missing.items():
        ok = False
        print(f"   MISSING x{n}: {lit!r}")
    for lit, n in added.items():
        print(f"   ADDED   x{n}: {lit[:120]!r}")
print("LITERAL_PARITY" if ok else "LITERAL_PARITY_FAILED")
