"""Run a pytest command for WC-4 r2 and store its console output as UTF-8.

The sandbox denies pytest its default ``--basetemp`` (PermissionError on
``%TEMP%\\pytest-of-<user>``), and r1's ``tests/conftest.py`` session fixture
needs ``tmp_path_factory.mktemp``.  This runner therefore invokes pytest with
``--noconftest`` (the only fixture there sets ``REVENUE_PUBLICATION_REGISTRY``,
which is set explicitly in the child environment instead) and parks every
byte under ``evidence/rgm2/pytest_r2/`` — a new directory, so r1 evidence is
never rewritten.

Usage:
  python -B run_pytest_r2.py --name <label> -- <pytest args...>
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "rf"
OUTDIR = ATTEMPT / "evidence" / "rgm2" / "pytest_r2"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    pytest_args = [a for a in args.pytest_args if a != "--"]
    if not pytest_args:
        raise SystemExit("no pytest args given")

    env = dict(os.environ)
    env["REVENUE_PUBLICATION_REGISTRY"] = str(ATTEMPT / "evidence" / "rgm2" / "registry" / args.name)
    argv = [sys.executable, "-B", "-m", "pytest", *pytest_args,
            "-q", "-p", "no:cacheprovider", "--noconftest"]
    OUTDIR.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(argv, cwd=str(ISO), env=env,
                          capture_output=True, timeout=3600)
    out = (proc.stdout or b"").decode("utf-8", "replace")
    err = (proc.stderr or b"").decode("utf-8", "replace")
    target = OUTDIR / f"{args.name}.txt"
    target.write_text(
        f"# argv: {' '.join(argv)}\n"
        f"# cwd: {ISO}\n"
        f"# REVENUE_PUBLICATION_REGISTRY: {env['REVENUE_PUBLICATION_REGISTRY']}\n"
        f"# raw_rc: {proc.returncode}\n\n"
        f"--- stdout ---\n{out}\n--- stderr ---\n{err}",
        encoding="utf-8",
    )
    print(f"raw_rc={proc.returncode} wrote={target}")
    tail = [line for line in (out + err).splitlines() if line.strip()][-6:]
    print("\n".join(tail))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
