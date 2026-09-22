"""Generate changes.diff: (1) the SRC oracle append (pre -> post), (2) every
file this attempt authored (empty -> content), (3) the frozen node copy check.

Pure-python difflib (no git dependency); read-only inputs; one output file.
Usage: python make_changes_diff.py <attempt_root> <src_oracle_path> <out.diff>
"""
from __future__ import annotations

import difflib
import sys
from pathlib import Path

MY = Path(sys.argv[1])
SRC_ORACLE = Path(sys.argv[2])
OUT = Path(sys.argv[3])

AUTHORED = [
    "oracle.md",
    "test_r13_equiv_rem41.py",
    "conftest.py",
    "runner/run_arm.ps1",
    "commands.json",
    "evidence/README.md",
    "scratch/apply_m6.py",
    "scratch/verify_m6_delta.py",
    "scratch/append_revision.py",
    "scratch/build_freeze.py",
    "scratch/final_integrity_check.py",
    "scratch/probe_e21_binding.py",
    "scratch/oracle_revision_r5.md",
    "scratch/oracle_revision_r6.md",
    "scratch/final_integrity_check_v2.py",
    "scratch/make_changes_diff.py",
    "decision.md",
    "recovery/README.md",
    # --- added in correction round r2 (record-only; disclosed in decision.md §r2)
    "scratch/oracle_revision_r7.md",
    "scratch/r2_verify.py",
    "scratch/r2_append_r7_dryrun.py",
    "scratch/r2_post_append.py",
    "scratch/r2_fix_probe_docstring.py",
    "scratch/r2_run_check.py",
]


def diff_text(old: str, new: str, old_name: str, new_name: str) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=old_name,
            tofile=new_name,
        )
    )


def main() -> int:
    parts: list[str] = []
    # 1. SRC oracle append (this card's ONLY write into B1's attempt)
    pre = (MY / "scratch" / "oracle_pre_r5.md").read_text(encoding="utf-8")
    post = SRC_ORACLE.read_text(encoding="utf-8")
    parts.append(
        "# changes.diff — B1-PREREQ a20260922-01\n"
        "# Section 1: SRC oracle.md (execution_runs/B1-I08C-product-fixes/a20260921-01/oracle.md)\n"
        "#   append-only Revisions r5 (F1/REM-40) + r6 (F2/REM-41) + r7 (r2 round,\n"
        "#   F-REV-B1P-01 F4 gap re-scope); r1-r4 bytes untouched (prefix proofs\n"
        "#   scratch/append_oracle_r{5,6,7}.stdout.json + evidence/r2/r2_09_post_append_verification.json)\n"
        "# Section 2: files authored by this attempt (new files; no product file appears here)\n"
        "# Boundary: iso/fixed/rf/**, iso/rf/**, production scripts/tests/config/artifacts — NOT CHANGED\n"
        "#   (see evidence/final_integrity_check_v2.stdout.txt: 14/14 ok; r2 re-checks:\n"
        "#    evidence/r2/r2_11_*post_r7_prefixefix.json all_ok=true, and r2_12_*post_docstring_fix.json\n"
        "#    whose SOLE expected failure is freeze entry my_probe_e21 after the commissioned\n"
        "#    F-REV-B1P-03 docstring fix — frozen bytes preserved in evidence/r2/)\n"
    )
    parts.append(diff_text(pre, post, "a/SRC/oracle.md.pre_r5", "b/SRC/oracle.md"))
    parts.append("\n")
    for rel in AUTHORED:
        path = MY / rel
        if not path.is_file():
            parts.append(f"### MISSING AUTHORED FILE: {rel}\n")
            continue
        content = path.read_text(encoding="utf-8")
        parts.append(
            diff_text("", content, "/dev/null", f"b/B1-PREREQ/a20260922-01/{rel}")
        )
        parts.append("\n")
    # NOTE: freeze.json, binding.json, handoff.json, SHA256SUMS are generated
    # artifacts pinned by binding.json (they cannot hash themselves); freeze.json
    # content is reproduced implicitly via freeze.json itself.
    OUT.write_text("".join(parts), encoding="utf-8")
    print(f"changes.diff bytes={OUT.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
