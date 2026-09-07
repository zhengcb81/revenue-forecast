"""Pre-push gate: CI-equivalent fast checks BEFORE pushing (root-cause fix).

Recurring failure pattern (2026-09-02..09-06): commits passed local
single-file tests and pre-commit, then CI turned red on gates the local
run never exercised — complexity/coverage ratchets, byte-binding
contracts (zr901 workflow hash), manifest/registry hashes, full-tree
ruff, and OS-dependent fixtures (Windows enumeration order masked a
Linux-only document-selection bug in wiki fixtures).

This gate runs the CI-equivalent FAST surface locally so those failures
cannot reach CI again:

  1. ruff check scripts tests tools e2e      (mirrors CI WU-1.2 scope)
  2. compileall scripts tests tools e2e
  3. tools/check_unique_test_symbols.py      (mirrors CI WU-1.1)
  4. mypy on the FC-1204-c contract set      (mirrors CI exactly)
  5. meta/binding tests that guard the surfaces most often broken:
     - tests/test_zr901_pr_fanout.py        (workflow byte-binding,
       required-checks contract — MUST run after ANY quality.yml change)
     - tests/test_compatibility_manifest.py (manifest + contract/scenario/
       command registry hashes — MUST run after ANY registry/config change)

Exit non-zero on the first red check.  The FULL pytest suite is NOT part
of this gate: on Windows it contains a pre-existing hang
(test_fc1103_t3_runner.test_with_force blocks on a subprocess I/O join
that pytest-timeout cannot interrupt).  Push protocol (see
assurance/runs/2026-09-02_remaining-gap-closure/ci_root_fix.md):

    python tools/pre_push_gate.py   # fast, ~1-2 min
    git push ...
    # THEN self-monitor the GitHub Actions run until green; on red, fix
    # the ROOT CAUSE and extend this gate so it would have caught it.

Usage: python tools/pre_push_gate.py [--skip-mypy] [--skip-meta-tests]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], label: str, timeout: int = 600) -> int:
    print(f"\n=== {label} ===")
    proc = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    tail = (proc.stdout or "")[-2000:] + (proc.stderr or "")[-1000:]
    if proc.returncode != 0:
        print(tail)
        print(f"FAILED: {label}")
    else:
        print("ok")
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-mypy", action="store_true")
    parser.add_argument("--skip-meta-tests", action="store_true")
    args = parser.parse_args(argv)

    gates: list[tuple[list[str], str]] = [
        (["ruff", "check", "scripts", "tests", "tools", "e2e"],
         "ruff (CI WU-1.2 full scope)"),
        ([sys.executable, "-m", "compileall", "-q",
          "scripts", "tests", "tools", "e2e"],
         "compileall"),
        ([sys.executable, str(PROJECT_ROOT / "tools" / "check_unique_test_symbols.py")],
         "unique test symbols (CI WU-1.1)"),
    ]
    if not args.skip_mypy:
        gates.append((
            [sys.executable, "-m", "mypy",
             "scripts/contracts/", "scripts/schema_compatibility.py",
             "scripts/filing_fetch_client.py", "scripts/trust_anchor.py"],
            "mypy public contracts (CI FC-1204-c set)",
        ))
    if not args.skip_meta_tests:
        gates.append((
            [sys.executable, "-m", "pytest", "-q", "--timeout=180",
             "tests/test_zr901_pr_fanout.py",
             "tests/test_compatibility_manifest.py"],
            "meta/binding tests (workflow byte-binding + manifest hashes)",
        ))

    for cmd, label in gates:
        rc = _run(cmd, label)
        if rc != 0:
            print(f"\nGATE RED at: {label}\nFix the root cause (see "
                  f"assurance/runs/2026-09-02_remaining-gap-closure/"
                  f"ci_root_fix.md), do not bypass.")
            return rc
    print("\npre-push gate GREEN — safe to push (then self-monitor CI).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
