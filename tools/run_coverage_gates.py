"""Report, or explicitly produce, revenue coverage results.

Default mode REPORTS coverage data that already exists — ``--data-file``,
the ``COVERAGE_FILE`` environment variable, or the repository's own
``.coverage`` — and starts nothing.  When no data exists it says
``not_supplied`` and exits 0.

  python tools/run_coverage_gates.py                     # report existing results
  python tools/run_coverage_gates.py --data-file PATH     # report explicit results
  python tools/run_coverage_gates.py --run --scratch DIR [--target PATH ...]
                                          # explicit: run the offline pytest
                                          # exactly once, data confined to DIR

Every coverage file produced by ``--run`` lives inside the explicit scratch:
the repository's existing ``.coverage`` is never erased or touched.  Low
numbers are diagnostics — ``PER_MODULE_MINIMUM`` and ``.coveragerc``'s
``fail_under`` are historical report decoders (AST-read by
``uc.quality._revenue_coverage``) and decide nothing.  A pytest run that
fails, fails to start, or times out, and a coverage toolchain that cannot
start, are non-zero.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RC = ROOT / ".coveragerc"

# Historical report decoder (AST-read by uc.quality._revenue_coverage).
# Empty on purpose: per-module floors no longer decide qualification.
PER_MODULE_MINIMUM = {}

DEFAULT_TARGETS = ("tests",)
DEFAULT_TIMEOUT = 900


def _base_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _coverage_tool(env: dict[str, str]) -> tuple[bool, str]:
    """Preflight: ``python -m coverage --version`` must really be coverage."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "coverage", "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(ROOT),
            env=env,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"coverage unavailable: {exc}"
    banner = f"{proc.stdout or ''}{proc.stderr or ''}"
    if proc.returncode != 0 or "coverage" not in banner.lower():
        return False, (
            f"coverage unavailable (python -m coverage --version rc={proc.returncode})"
        )
    return True, banner.splitlines()[0] if banner.splitlines() else "coverage"


def _coverage(
    args: list[str], env: dict[str, str], timeout: int = 300
) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            [sys.executable, "-m", "coverage", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(ROOT),
            env=env,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"COVERAGE-TOOL-FAILURE: coverage {' '.join(args)}: {exc}")
        return None


def _resolve_data_file(explicit: Path | None) -> Path:
    if explicit is not None:
        return Path(explicit)
    ambient = os.environ.get("COVERAGE_FILE")
    if ambient:
        return Path(ambient)
    return ROOT / ".coverage"


def _has_data(path: Path) -> bool:
    if path.is_file():
        return True
    parent = path.parent
    if not parent.is_dir():
        return False
    return any(parent.glob(f"{path.name}.*"))


def _per_module_failures(rows: str) -> list[str]:
    failures: list[str] = []
    lines = [row.replace("\\", "/") for row in rows.splitlines()]
    for path, minimum in PER_MODULE_MINIMUM.items():
        line = next((row for row in lines if row.lstrip().startswith(path)), None)
        if line is None:
            failures.append(f"{path}: not measured")
            continue
        parts = [p for p in line.split() if p]
        try:
            percent = float(parts[5].rstrip("%"))
        except (IndexError, ValueError):
            failures.append(f"{path}: cannot parse {line!r}")
            continue
        if percent < minimum:
            failures.append(f"{path}: {percent:.0f}% < {minimum}%")
    return failures


def report(data_file: Path | None) -> int:
    """Report existing coverage data.  Starts no pytest, erases nothing."""
    target = _resolve_data_file(data_file)
    if not _has_data(target):
        print(f"coverage data not_supplied ({target}); no run started")
        return 0
    env = _base_env()
    env["COVERAGE_FILE"] = str(target)
    ok, detail = _coverage_tool(env)
    if not ok:
        print(f"COVERAGE-TOOL-FAILURE: {detail}")
        return 1
    proc = _coverage(["report", "--rcfile", str(RC)], env=env)
    if proc is None:
        return 1
    output = f"{proc.stdout or ''}{proc.stderr or ''}"
    print(proc.stdout or "")
    if proc.returncode != 0:
        if "no data to report" in output.lower():
            print(f"coverage data not_supplied ({target}); nothing measured")
            return 0
        print(f"COVERAGE-TOOL-FAILURE: coverage report rc={proc.returncode}")
        return 1
    failures = _per_module_failures(proc.stdout or "")
    if failures:
        print("PER-MODULE COVERAGE FAILURES:")
        for item in failures:
            print(f"  {item}")
        return 1
    print("COVERAGE REPORT OK (diagnostic numbers, no qualification floors)")
    return 0


def _extra_pytest_args() -> list[str]:
    extra_env = os.environ.get("PYTEST_COVERAGE_EXTRA_ARGS", "").strip()
    return extra_env.split() if extra_env else []


def run(scratch: Path, targets: list[str], timeout: int) -> int:
    """Explicit run: one offline pytest under coverage, data confined to scratch."""
    scratch = Path(scratch)
    if scratch.exists() and not scratch.is_dir():
        print(f"scratch is not a directory: {scratch}", file=sys.stderr)
        return 1
    scratch.mkdir(parents=True, exist_ok=True)
    env = _base_env()
    env["COVERAGE_FILE"] = str(scratch / ".coverage")
    env["COVERAGE_PROCESS_START"] = str(RC)
    ok, detail = _coverage_tool(env)
    if not ok:
        print(f"COVERAGE-TOOL-FAILURE: {detail}")
        return 1
    erased = _coverage(["erase"], env=env, timeout=120)
    if erased is None:
        return 1
    if erased.returncode != 0:
        print(f"COVERAGE-TOOL-FAILURE: coverage erase rc={erased.returncode}")
        return 1
    cmd = [
        sys.executable,
        "-m",
        "coverage",
        "run",
        "--rcfile",
        str(RC),
        "-m",
        "pytest",
        *targets,
        "-q",
        "-p",
        "no:cacheprovider",
        "-k",
        "not fc1103",
        *_extra_pytest_args(),
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        print(f"PYTEST-FAILURE: timed out after {exc.timeout}s")
        return 1
    except OSError as exc:
        print(f"PYTEST-FAILURE: could not start pytest: {exc}")
        return 1
    print((proc.stdout or "")[-4000:])
    if proc.returncode != 0:
        print((proc.stderr or "")[-2000:])
        print(f"PYTEST-FAILURE: exit code {proc.returncode}")
        return proc.returncode if proc.returncode > 0 else 1
    combined = _coverage(["combine", "--rcfile", str(RC)], env=env, timeout=180)
    if combined is None:
        return 1
    if combined.returncode != 0:
        output = f"{combined.stdout or ''}{combined.stderr or ''}"
        if "no data to combine" not in output.lower():
            print(f"COVERAGE-TOOL-FAILURE: coverage combine rc={combined.returncode}")
            return 1
    return report(scratch / ".coverage")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report or explicitly produce revenue coverage results"
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=None,
        dest="data_file",
        help="existing coverage data to report",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="explicitly run the offline pytest once under coverage",
    )
    parser.add_argument(
        "--scratch",
        type=Path,
        default=None,
        help="directory that receives every coverage file (required with --run)",
    )
    parser.add_argument(
        "--target",
        action="append",
        default=None,
        metavar="PATH",
        help=f"pytest target for --run (repeatable; default: {DEFAULT_TARGETS[0]})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="seconds before the explicit pytest run is abandoned",
    )
    args = parser.parse_args(argv)
    if args.run:
        if args.scratch is None:
            parser.error(
                "--run requires --scratch DIR so every coverage file stays in "
                "an explicit scratch"
            )
        return run(args.scratch, args.target or list(DEFAULT_TARGETS), args.timeout)
    if args.scratch is not None or args.target is not None:
        parser.error("--scratch/--target only apply to --run")
    return report(args.data_file)


if __name__ == "__main__":
    raise SystemExit(main())
