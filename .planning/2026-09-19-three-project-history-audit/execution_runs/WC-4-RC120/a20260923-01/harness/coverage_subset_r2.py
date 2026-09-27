"""r2 coverage subset for scripts/revenue_forecast.py (per-module gate face).

Runs the CLI-touching tests that are executable in this sandbox (pytest's
tmp_path basetemp is denied here, so the tmp_path-heavy family files cannot
run) plus the WC-4 product test, then reports coverage for the one module the
gate watches (tools/run_coverage_gates.py: scripts/revenue_forecast.py >= 60%).

Raw rc of every step is recorded; evidence/rgm2/coverage_subset_r2.txt is a
NEW file (r1's evidence/rgm/coverage_subset_fixed.txt is never rewritten).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "rf"
OUT = ATTEMPT / "evidence" / "rgm2" / "coverage_subset_r2.txt"

TESTS = [
    "tests/test_stdout_flush_exit_domain.py",
    "tests/test_verbose_validation.py",
]


def run(argv, env):
    proc = subprocess.run(argv, cwd=str(ISO), env=env,
                          capture_output=True, timeout=3600)
    return proc.returncode, ((proc.stdout or b"") + (proc.stderr or b"")).decode(
        "utf-8", "replace")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    env = dict(os.environ)
    env["REVENUE_PUBLICATION_REGISTRY"] = str(
        ATTEMPT / "evidence" / "rgm2" / "registry" / "coverage_r2")
    for stale in ISO.glob(".coverage*"):
        stale.unlink(missing_ok=True)

    lines = [
        "WC-4 r2 coverage subset: CLI-touching tests executable in this sandbox",
        "+ the WC-4 product test (per-module gate lower bound)",
        "",
    ]
    run_argv = [sys.executable, "-B", "-m", "coverage", "run",
                "-m", "pytest", *TESTS, "-q", "-p", "no:cacheprovider",
                "--noconftest"]
    rc_run, out_run = run(run_argv, env)
    lines += [f"## {' '.join(run_argv)}", f"raw_rc={rc_run}", out_run, ""]

    rc_comb, out_comb = run([sys.executable, "-B", "-m", "coverage", "combine"], env)
    lines += [f"## coverage combine", f"raw_rc={rc_comb}", out_comb, ""]

    rc_rep, out_rep = run(
        [sys.executable, "-B", "-m", "coverage", "report",
         "--include=scripts/revenue_forecast.py"], env)
    lines += [f"## coverage report --include=scripts/revenue_forecast.py",
              f"raw_rc={rc_rep}", out_rep, ""]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"coverage run raw_rc={rc_run}")
    print(f"coverage combine raw_rc={rc_comb}")
    print(f"coverage report raw_rc={rc_rep}")
    for line in out_rep.splitlines():
        print("   ", line)
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
