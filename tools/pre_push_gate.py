"""Shared daily CI/pre-push checks; milestone suites remain explicit.

One curated offline behavior set covers default source reads and forecast
calculations. No production catalog, install synchronization, full coverage,
mutation patrol or historical workflow byte-signature is a daily gate.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_GIT_REPOSITORY_CONTEXT = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_PREFIX", "GIT_NAMESPACE", "GIT_QUARANTINE_PATH",
)


def _subprocess_environment() -> dict[str, str]:
    """Let child Git commands resolve their cwd instead of the parent hook."""
    environment = os.environ.copy()
    for name in _GIT_REPOSITORY_CONTEXT:
        environment.pop(name, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONUTF8"] = "1"
    return environment


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
    cmd: list[str], label: str, timeout: int = 300, *, blocking: bool = True
) -> int:
    print(f"\n=== {label} ===")
    proc = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_subprocess_environment(),
        timeout=timeout,
    )
    tail = (proc.stdout or "")[-2000:] + (proc.stderr or "")[-1000:]
    if proc.returncode != 0:
        print(tail)
        if blocking:
            print(f"FAILED: {label}")
    else:
        print(tail.strip()[-500:] or "ok")
    return proc.returncode



SMOKE_TESTS = (
    "tests/test_ci_smoke_plan.py",
    "tests/test_pre_push_gate_git_hook_env.py",
    "tests/test_p5_source_default_v2.py",
    "tests/test_p5_source_default_cli_e2e.py",
    "tests/test_company_wiki_source_ref_v2.py",
    "tests/test_company_wiki_source_v2.py",
    "tests/test_source_preparation.py",
    "tests/test_data_contract.py",
    "tests/test_recognition_bridge.py",
    "tests/test_confidence_determinism.py",
    "tests/test_sensitivity_dependency_dag.py",
    "tests/test_published_foundation_roundtrip.py",
    "tests/test_growth_driver_tree.py",
    "tests/test_revenue_constraints.py",
    "tests/test_schema_compatibility.py",
)


def main(argv: list[str] | None = None) -> int:
    if argv:
        raise ValueError("The daily gate has no skip flags; run milestone commands explicitly.")
    _safe_console()
    gates = (
        ([sys.executable, "-m", "ruff", "check", "scripts", "tests", "tools", "e2e"], "ruff"),
        ([sys.executable, "-m", "mypy", "scripts/contracts/", "scripts/schema_compatibility.py",
          "scripts/filing_fetch_client.py", "scripts/trust_anchor.py"], "public contract types"),
        ([sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider", *SMOKE_TESTS],
         "current source and forecast behavior"),
    )
    with tempfile.TemporaryDirectory(prefix="rf-ci-") as scratch:
        for command, label in gates:
            if command[:3] == [sys.executable, "-m", "pytest"]:
                command = [*command, "--basetemp", scratch]
            rc = _run(command, label)
            if rc:
                return rc
    print("\npre-push/CI checks GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
