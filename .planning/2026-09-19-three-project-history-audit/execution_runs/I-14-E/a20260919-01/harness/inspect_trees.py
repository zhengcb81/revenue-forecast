"""I-14-E glue (not a card run): inventory + hash compare of the candidate trees.

Read-only. Compares, file by file:
  CW/src                     (production HEAD worktree, READ-ONLY)
  I-14-C iso/product/src     (T0 = pristine HEAD copy)
  I-14-C iso/product_fixed/src (T4 = the variant used by the frozen 24-run band)
  I-14-F iso/tree/src        (I-14-F's isolated tree copy)

Writes nothing into any production repo. Output goes to stdout (captured by the caller).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

RF_PLAN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
               r"\2026-09-19-three-project-history-audit")
RUNS = RF_PLAN / "execution_runs"
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")

WAIT_TREES = {
    "CW_HEAD": CW / "src",
    "I14C_T0": RUNS / "I-14-C" / "a20260919-01" / "iso" / "product" / "src",
    "I14C_T4": RUNS / "I-14-C" / "a20260919-01" / "iso" / "product_fixed" / "src",
    "I14F_TREE": RUNS / "I-14-F" / "a20260919-01" / "iso" / "tree" / "src",
}


def inventory(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if name.endswith(".pyc"):
                continue
            fp = Path(dirpath) / name
            rel = fp.relative_to(root).as_posix()
            out[rel] = hashlib.sha256(fp.read_bytes()).hexdigest()
    return out


def main() -> int:
    trees = {label: inventory(p) for label, p in WAIT_TREES.items()}
    for label, files in trees.items():
        print(f"{label}: {len(files)} files")
    base = trees["CW_HEAD"]
    for label, files in trees.items():
        if label == "CW_HEAD":
            continue
        only_a = sorted(set(base) - set(files))
        only_b = sorted(set(files) - set(base))
        diff = sorted(k for k in set(base) & set(files) if base[k] != files[k])
        print(f"\n== {label} vs CW_HEAD: identical={not (only_a or only_b or diff)}")
        print(f"   only in CW_HEAD: {only_a}")
        print(f"   only in {label}: {only_b}")
        print(f"   content-diff files ({len(diff)}):")
        for k in diff:
            print(f"     {k}\n        CW={base[k]}\n        OTH={files[k]}")
    # extra anchors
    print("\n== anchors ==")
    anchors = [
        (CW / "tests" / "contract" / "test_source_catalog_worker_bootstrap.py", "CW test file"),
        (CW / "scripts" / "source_catalog_worker.ps1", "CW supervisor ps1"),
        (CW / "scripts" / "source_catalog_worker_at_logon.ps1", "CW logon ps1"),
        (CW / "tests" / "contract" / "conftest.py", "CW tests/contract conftest"),
        (CW / "conftest.py", "CW root conftest"),
        (CW / "pytest.ini", "CW pytest.ini"),
    ]
    for path, label in anchors:
        if path.exists():
            print(f"  {label}: sha256={hashlib.sha256(path.read_bytes()).hexdigest()} "
                  f"bytes={path.stat().st_size}")
        else:
            print(f"  {label}: MISSING ({path})")
    # r5 diff hashes (the candidate T4 material)
    diffs = [
        RUNS / "I-14-C" / "a20260919-01" / "r2-changes.diff",
        RUNS / "I-14-C" / "a20260919-01" / "r5-changes.diff",
        RUNS / "I-14-C" / "a20260919-01" / "changes.diff",
    ]
    print("\n== candidate diffs ==")
    for d in diffs:
        if d.exists():
            print(f"  {d.name}: sha256={hashlib.sha256(d.read_bytes()).hexdigest()} "
                  f"bytes={d.stat().st_size}")
        else:
            print(f"  {d.name}: MISSING")
    print("\nfrequency evidence (frozen band):")
    freq = (RUNS / "I-14-C" / "a20260919-01" / "r5" / "flake-evidence"
            / "frequency-child_without_runtime.json")
    print(f"  {freq}: sha256={hashlib.sha256(freq.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
