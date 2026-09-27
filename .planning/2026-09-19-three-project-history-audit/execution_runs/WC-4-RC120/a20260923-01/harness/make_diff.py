"""Build changes.diff for WC-4 = F12-RC120 WITHOUT git.

Compares, byte for byte:
  1. production scripts/revenue_forecast.py (READ-ONLY source, never written)
     vs the fixed iso copy
  2. a file the production tree does not have yet (the new product test)
     vs the iso copy

Emits attempt-local changes.diff in unified-diff form with a/ b/ paths so it can
be applied to the production tree by the parent batch.
"""
from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "rf"
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
OUT = ATTEMPT / "changes.diff"

TARGETS = [
    ("scripts/revenue_forecast.py", RF / "scripts/revenue_forecast.py", ISO / "scripts/revenue_forecast.py"),
    ("tests/test_stdout_flush_exit_domain.py", None, ISO / "tests/test_stdout_flush_exit_domain.py"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    chunks = []
    summary = []
    for rel, prod, iso in TARGETS:
        new_text = iso.read_text(encoding="utf-8")
        old_text = prod.read_text(encoding="utf-8") if prod else ""
        if new_text == old_text:
            raise SystemExit(f"NO-OP diff for {rel} - fix missing?")
        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{rel}", tofile=f"b/{rel}",
            # r2: zero context so the r1 fix (new helper functions) and the r2
            # fix (entry wrapper covering SystemExit raised inside main()) stay
            # in two separate, separately reviewable hunks; with n=3 the single
            # unchanged `if __name__` guard line would merge them into one hunk.
            n=0,
        ))
        if not diff:
            raise SystemExit(f"empty diff for {rel}")
        # difflib does not emit "\ No newline at end of file"; normalize endings
        chunks.append("".join(diff))
        summary.append({
            "path": rel,
            "old_sha256": sha(old_text.encode("utf-8")) or None,
            "new_sha256": sha(new_text.encode("utf-8")),
            "old_bytes": len(old_text.encode("utf-8")),
            "new_bytes": len(new_text.encode("utf-8")),
            "diff_lines": len(diff),
        })
    OUT.write_text("\n".join(chunks), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} bytes={OUT.stat().st_size}")
    for entry in summary:
        print(entry)
    prod_sha_before = sha((RF / "scripts/revenue_forecast.py").read_bytes())
    print(f"production_cli_sha256_after_delivery_prep={prod_sha_before} (must equal binding pin)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
