"""Comment-line multiset diff: original (production) vs refactored (iso_after).

Catches comment-text drift that the string-literal diff cannot see. Comments are
allowed to MOVE (helper extraction) but their multiset must be identical, except for
explicitly whitelisted NEW comments (none planned — flag any).
Usage: python -B comment_diff.py
"""
from __future__ import annotations

import io
import tokenize
from collections import Counter
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
ISO = Path(r"C:\Users\郑曾波\AppData\Local\Temp\rf-rest-b\iso_after\scripts")
FILES = ["model_registry.py", "revenue_core.py", "revenue_publication.py"]


def comments(path: Path) -> Counter:
    out: Counter = Counter()
    src = path.read_bytes()
    for tok in tokenize.tokenize(io.BytesIO(src).readline):
        if tok.type == tokenize.COMMENT:
            out[tok.string.strip()] += 1
    return out


ok = True
for name in FILES:
    before = comments(RF / "scripts" / name)
    after = comments(ISO / name)
    missing = before - after
    added = after - before
    print(f"== {name}: before={sum(before.values())} after={sum(after.values())} "
          f"missing={sum(missing.values())} added={sum(added.values())}")
    for c, n in missing.items():
        ok = False
        print(f"   MISSING x{n}: {c!r}")
    for c, n in added.items():
        print(f"   ADDED   x{n}: {c[:140]!r}")
print("COMMENT_PARITY" if ok else "COMMENT_PARITY_FAILED")
