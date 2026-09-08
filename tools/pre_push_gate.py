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
  6. installed-skill consistency (owner requirement 2026-09-08): the installed
     copies under ~/.agents, ~/.claude, ~/.codex must equal this repo; stale
     copies are auto-synced from the repo and re-checked.  CI cannot cover
     this (runners have no install roots).

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
       [--skip-install-sync]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _safe_console() -> None:
    """Windows consoles default to GBK; a captured tool output containing any
    non-GBK byte would crash the gate while *reporting* a failure, masking the
    real result.  Reconfigure to UTF-8 with replacement (filing-fetch hit this
    in its gate; revenue hit it on 2026-09-08 while printing a drift diff)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def _run(
    cmd: list[str], label: str, timeout: int = 600, *, blocking: bool = True
) -> int:
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
        if blocking:
            print(f"FAILED: {label}")
    else:
        print("ok")
    return proc.returncode


def _no_bom_check() -> int:
    """Root-fix: CA-304/final_ratchet require ZERO UTF-8 BOM python files in
    scripts/tests/tools/e2e.  CI #113 failed because pre_push_gate.py
    itself was written with a BOM (PowerShell Set-Content) and no local
    gate caught it.  This check makes that failure class local."""
    bad: list[str] = []
    for directory in ("scripts", "tests", "tools", "e2e"):
        base = PROJECT_ROOT / directory
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            raw = path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                bad.append(str(path.relative_to(PROJECT_ROOT)))
    if bad:
        print("FAILED: UTF-8 BOM python files must be zero:")
        for name in bad:
            print(f"  {name}")
        return 1
    print("ok")
    return 0


def _install_sync() -> int:
    """Keep the installed copies of this skill in step with the repo.

    Owner requirement (2026-09-08): every installed skill must equal its
    Projects git repo.  CI can never catch this class — GitHub runners have no
    install roots, so ``installation_diff`` returns [] there — hence the check
    lives here: check, auto-sync when stale (repo is the source of truth), then
    re-check.  The sync tool is atomic per skill and keeps an ``output/`` dir.
    """
    tool = PROJECT_ROOT / "tools" / "sync_installations.py"
    rc = _run([sys.executable, str(tool)],
              "installed-skill consistency (check)", blocking=False)
    if rc == 0:
        return 0
    print("installed copies were stale: applying the repo -> install sync ...")
    rc = _run([sys.executable, str(tool), "--apply"],
              "installed-skill sync (repo -> install)", blocking=False)
    if rc != 0:
        return rc
    return _run([sys.executable, str(tool)],
                "installed-skill consistency (re-check)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-mypy", action="store_true")
    parser.add_argument("--skip-meta-tests", action="store_true")
    parser.add_argument("--skip-install-sync", action="store_true")
    args = parser.parse_args(argv)
    _safe_console()

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
    # CA-304/final_ratchet zero-BOM gate (root-fix; CI #113 regression)
    print("\n=== UTF-8 BOM scan (CA-304/final_ratchet surface) ===")
    if _no_bom_check() != 0:
        return 1
    if not args.skip_install_sync:
        rc = _install_sync()
        if rc != 0:
            print("\nGATE RED at: installed-skill consistency\n"
                  "Fix: python tools/sync_installations.py --apply")
            return rc
    print("\npre-push gate GREEN — safe to push (then self-monitor CI).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
