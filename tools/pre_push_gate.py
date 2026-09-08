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
  6. real-roots E2E (GP-006): the sibling-dependent suite that CI's blocking
     real-roots job runs on windows-latest — same set, so gate and CI cannot
     diverge (skipped when the sibling repos are absent).
  7. real-data suite (GP-006): the production-catalog tests that cannot run on
     a GitHub-hosted runner; enforced here on the machine that owns the
     catalog (skipped when the catalog is absent).
  8. installed-skill consistency (owner requirement 2026-09-08): the installed
     copies under ~/.agents, ~/.claude, ~/.codex must equal this repo; stale
     copies are auto-synced from the repo and re-checked.  CI cannot cover
     this (runners have no install roots).

Exit non-zero on the first red check.  The FULL pytest suite is NOT part
of this gate: on Windows it contains a pre-existing hang
(test_fc1103_t3_runner.test_with_force blocks on a subprocess I/O join
that pytest-timeout cannot interrupt).  Push protocol (see
assurance/runs/2026-09-02_remaining-gap-closure/ci_root_fix.md):

    python tools/pre_push_gate.py   # ~4-5 min
    git push ...
    # THEN self-monitor the GitHub Actions run until green; on red, fix
    # the ROOT CAUSE and extend this gate so it would have caught it.

Usage: python tools/pre_push_gate.py [--skip-mypy] [--skip-meta-tests]
       [--skip-install-sync] [--skip-real-roots] [--skip-real-data]
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


REAL_ROOTS_TESTS = (
    "tests/test_zr803_chaos_recovery.py",
    "tests/test_zr1103_journey_reverify.py",
    "tests/test_ca203_weekly_t3.py",
    "tests/test_fc1101_ci_manifest.py",
    "tests/test_compatibility_manifest.py",
    "tests/test_fc1002_three_process_e2e.py",
    "tests/test_ca302_three_journeys.py",
)
REAL_DATA_TESTS = (
    "tests/test_zr806_real_t2_samples.py",
    "tests/test_zr1004_small_cohort.py",
    "tests/test_fc1001_isolated_lake.py",
    "tests/test_fc1003_uj.py",
    "tests/test_fc1004_platform.py",
    "tests/test_fc1105_fault_injection.py",
    "tests/test_preparation_e2e_success.py",
    "tests/test_zr709_zijin_journey.py",
    "tests/test_zr907_drift_patrol.py",
    "tests/test_ca202_daily_t2_runner.py",
)


def _real_roots() -> int:
    """GP-006: the sibling-dependent E2E suite is blocking in CI's real-roots
    job; this runs the same set locally so the gate and CI cannot diverge."""
    missing = [
        name
        for name in ("company-wiki", "filing-fetch")
        if not (PROJECT_ROOT.parent / name).is_dir()
    ]
    if missing:
        print(
            "\n=== real-roots E2E (CI real-roots job) ===\n"
            f"SKIP: sibling repos missing: {', '.join(missing)}"
        )
        return 0
    return _run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short", *REAL_ROOTS_TESTS],
        "real-roots E2E (CI real-roots job)",
    )


def _real_data() -> int:
    """GP-006: the REAL_DATA suite needs the production catalog, which cannot
    live on a GitHub-hosted runner.  It is enforced here, on the machine that
    owns the catalog; a self-hosted runner would be required to move it into
    CI."""
    catalog = PROJECT_ROOT.parent / "company-wiki" / ".source_catalog" / "catalog.sqlite3"
    if not catalog.is_file():
        print(
            "\n=== real-data suite (production catalog) ===\n"
            f"SKIP: no production catalog at {catalog}"
        )
        return 0
    return _run(
        [sys.executable, "-m", "pytest", "-q", "--tb=line", *REAL_DATA_TESTS],
        "real-data suite (production catalog; CI needs a self-hosted runner)",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-mypy", action="store_true")
    parser.add_argument("--skip-meta-tests", action="store_true")
    parser.add_argument("--skip-install-sync", action="store_true")
    parser.add_argument("--skip-real-roots", action="store_true")
    parser.add_argument("--skip-real-data", action="store_true")
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
    if not args.skip_real_roots:
        rc = _real_roots()
        if rc != 0:
            print("\nGATE RED at: real-roots E2E (CI real-roots job)\n"
                  "Fix the root cause; do not bypass.")
            return rc
    if not args.skip_real_data:
        rc = _real_data()
        if rc != 0:
            print("\nGATE RED at: real-data suite (production catalog)\n"
                  "Fix the root cause; do not bypass.")
            return rc
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
