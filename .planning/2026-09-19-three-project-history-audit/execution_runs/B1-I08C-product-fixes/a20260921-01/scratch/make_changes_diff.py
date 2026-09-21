"""Generate changes.diff: the exact delta between production and the fixed tree."""
from __future__ import annotations

import difflib
import hashlib
import sys
from pathlib import Path

UNFIXED = Path(sys.argv[1]).resolve()   # iso/rf        (byte-identical to production)
FIXED = Path(sys.argv[2]).resolve()     # iso/fixed/rf
OUT = Path(sys.argv[3]).resolve()

parts: list[str] = []
parts.append("# B1-I08C-product-fixes / a20260921-01 — changes.diff\n")
parts.append("#\n")
parts.append("# Left side  : iso/rf/scripts/**   (byte-identical copy of the production tree;\n")
parts.append("#              the copy integrity is recorded in before/iso_tree_manifest.json and\n")
parts.append("#              re-printed at run time by scratch/probe_defects.py)\n")
parts.append("# Right side : iso/fixed/rf/scripts/**  (the fixed tree)\n")
parts.append("#\n")
parts.append("# Production itself is NOT modified by this card. This diff is the change set\n")
parts.append("# a promotion would apply; promotion is a separate owner decision.\n")
parts.append("#\n")
parts.append("# Only scripts/ is diffed: tests/ and config/ are byte-identical between the two\n")
parts.append("# trees (the card adds its own test file at the attempt root, not inside the tree).\n")
parts.append("\n")

changed: list[str] = []
identical: list[str] = []
for left in sorted((UNFIXED / "scripts").rglob("*.py")):
    rel = left.relative_to(UNFIXED).as_posix()
    right = FIXED / rel
    left_bytes = left.read_bytes()
    right_bytes = right.read_bytes() if right.is_file() else b""
    if left_bytes == right_bytes:
        identical.append(rel)
        continue
    changed.append(rel)
    parts.append(f"{'=' * 78}\n")
    parts.append(f"# {rel}\n")
    parts.append(
        f"#   production: sha256 {hashlib.sha256(left_bytes).hexdigest()} "
        f"({len(left_bytes)} bytes)\n"
    )
    parts.append(
        f"#   fixed     : sha256 {hashlib.sha256(right_bytes).hexdigest()} "
        f"({len(right_bytes)} bytes)\n"
    )
    parts.append(f"{'=' * 78}\n")
    diff = difflib.unified_diff(
        left_bytes.decode("utf-8").splitlines(keepends=True),
        right_bytes.decode("utf-8").splitlines(keepends=True),
        fromfile=f"a/{rel}",
        tofile=f"b/{rel}",
        n=4,
    )
    parts.extend(diff)
    parts.append("\n")

summary = [
    "# ------------------------------------------------\n",
    f"# files changed : {len(changed)}\n",
    *[f"#   M {rel}\n" for rel in changed],
    f"# files identical: {len(identical)}\n",
    "#\n",
    "# No production file was written.\n",
]
OUT.write_text("".join(parts) + "".join(summary), encoding="utf-8")
print("changed:", changed)
print("identical file count:", len(identical))
print("bytes:", OUT.stat().st_size, "sha256:", hashlib.sha256(OUT.read_bytes()).hexdigest())
