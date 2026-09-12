"""Apply/revert one literal replacement in a file.

usage: python b06_review_patch.py <file> <old-file> <new-file> [--revert]
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

target = Path(sys.argv[1])
old = Path(sys.argv[2]).read_text(encoding="utf-8")
new = Path(sys.argv[3]).read_text(encoding="utf-8")
revert = "--revert" in sys.argv

source = target.read_text(encoding="utf-8")
if revert:
    source, count = source.replace(new, old, 1), source.count(new)
else:
    source, count = source.replace(old, new, 1), source.count(old)
if count != 1:
    raise SystemExit(f"anchor count={count}, refusing to patch")
target.write_text(source, encoding="utf-8")
print("patched", target, "revert" if revert else "apply")
print("sha256", hashlib.sha256(target.read_bytes()).hexdigest())
