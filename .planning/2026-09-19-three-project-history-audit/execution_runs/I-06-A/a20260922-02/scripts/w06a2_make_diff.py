#!/usr/bin/env python3
"""Produce changes.diff: before/cw -> iso/cw (difflib unified; no git writes)."""

from __future__ import annotations

import difflib
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
BEFORE = ATTEMPT / "before" / "cw"
ISO = ATTEMPT / "iso" / "cw"


def main() -> int:
    out: list[str] = []
    for iso_file in sorted(ISO.rglob("*.py")):
        rel = iso_file.relative_to(ISO)
        before_file = BEFORE / rel
        old = before_file.read_text(encoding="utf-8").splitlines(keepends=True)
        new = iso_file.read_text(encoding="utf-8").splitlines(keepends=True)
        if old == new:
            continue
        diff = difflib.unified_diff(
            old, new,
            fromfile=f"before/cw/{rel.as_posix()}",
            tofile=f"iso/cw/{rel.as_posix()}",
        )
        out.extend(diff)
    target = ATTEMPT / "changes.diff"
    target.write_text("".join(out), encoding="utf-8")
    print(f"changes.diff written: {len(out)} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
