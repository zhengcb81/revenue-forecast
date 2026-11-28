"""Fast developer smoke or measured CI execution of the owning test roots."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_POLICY = PROJECT_ROOT / "tools" / "s6-test-policy.json"
_NO_CONSOLE = getattr(subprocess, "CREATE_NO_WINDOW", 0)
_HOST_ENVIRONMENT = {
    "APPDATA", "COMSPEC", "HOME", "HOMEDRIVE", "HOMEPATH", "LANG",
    "LC_ALL", "LOCALAPPDATA", "NUMBER_OF_PROCESSORS", "PATH", "PATHEXT",
    "PROCESSOR_ARCHITECTURE", "PROGRAMDATA", "PROGRAMFILES", "SYSTEMDRIVE",
    "SYSTEMROOT", "TEMP", "TMP", "TMPDIR", "USERPROFILE", "WINDIR",
}


def _subprocess_environment(profile: Path | None = None) -> dict[str, str]:
    """Give engineering checks only the host environment they need."""
    environment = {
        key: value for key, value in os.environ.items() if key.upper() in _HOST_ENVIRONMENT
    }
    environment.update(
        PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHON_DOTENV_DISABLED="1",
        REVENUE_ATTESTATION_PROVIDER="", GIT_TERMINAL_PROMPT="0", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
    )
    if profile is not None:
        for name in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_STATE_HOME"):
            environment[name] = str(profile)
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


def _run(cmd: list[str], label: str, timeout: int = 300, *, profile: Path | None = None) -> int:
    print(f"\n=== {label} ===", flush=True)
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            creationflags=_NO_CONSOLE,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_subprocess_environment(profile),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        for stream, partial in ((sys.stdout, error.stdout), (sys.stderr, error.stderr)):
            if partial:
                text = partial.decode("utf-8", errors="replace") if isinstance(partial, bytes) else partial
                print(text, end="", file=stream)
        print(f"FAILED: {label} exceeded {timeout:g}s", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"FAILED: {label} could not start ({type(error).__name__})", file=sys.stderr)
        return 1
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr)
        print(f"FAILED: {label}")
    else:
        print(((proc.stdout or "") + (proc.stderr or "")).strip()[-3000:] or "ok")
    return proc.returncode


# Explicit nodes keep routine push work stable when other files gain tests.
# Authors separately run the behavior suites relevant to their change.
LOCAL_SMOKE_TESTS = (
    "tests/test_p5_source_default_v2.py::test_default_entry_uses_source_ref_v2_without_opt_in",
    "tests/test_p5_source_default_v2.py::test_repeated_default_preparation_reuses_without_shadow_jobs",
    "tests/test_company_wiki_source_ref_v2.py::test_producer_golden_is_pinned_and_accepted_by_reader",
    "tests/test_company_wiki_source_ref_v2.py::test_malformed_source_ref_is_rejected_before_reader_io",
    "tests/test_company_wiki_source_v2.py::test_verified_ref_builds_schema_compatible_record_without_physical_path",
    "tests/test_data_contract.py::DataContractTests::test_valid_document",
    "tests/test_data_contract.py::DataContractTests::test_claim_must_bind_to_captured_snapshot",
    "tests/test_data_contract.py::DataContractTests::test_rejects_future_information",
    "tests/test_data_contract.py::DataContractTests::test_reported_revenue_dimension_is_enforced",
    "tests/test_recognition_bridge.py::RecognitionBridgeTests::test_company_aggregates_recognized_segments",
    "tests/test_published_foundation_roundtrip.py::test_foundation_inventory_roundtrips_actual_base_total_and_stock_ids",
    "tests/test_published_foundation_roundtrip.py::test_forged_opening_base_or_adjustment_is_rejected",
)


def _revision(requested: str | None) -> str:
    actual = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, env=_subprocess_environment(),
        stdin=subprocess.DEVNULL, creationflags=_NO_CONSOLE, encoding="ascii", timeout=10,
    ).strip()
    if requested is not None and requested != actual:
        raise ValueError("requested test revision differs from the checked out revision")
    return actual


def _ci_commands(
    evidence_dir: Path, scratch: Path, revision: str, platform: str, *, workers: int = 1,
) -> list[tuple[list[str], str]]:
    policy = json.loads(TEST_POLICY.read_text(encoding="utf-8"))["platforms"][platform]
    collected, executed = [str(evidence_dir / f"{name}.json") for name in ("collected", "executed")]
    pytest = [
        sys.executable, "-m", "pytest", "-q", "--tb=short", "--capture=sys", "-p", "no:cacheprovider",
        "-p", "tools.anti_trick_gate_spec.pytest_probe", "--s6-revision", revision,
        "-m", policy["markexpr"], "--basetemp", str(scratch), *policy["roots"],
    ]
    executor = [] if workers == 1 else ["-p", "xdist.plugin", "-n", str(workers), "--dist", "loadfile"]
    return [
        ([sys.executable, "-m", "mypy", "scripts/contracts/", "scripts/schema_compatibility.py",
          "scripts/filing_fetch_client.py", "scripts/trust_anchor.py",
          "scripts/company_wiki_narrative_contracts.py"], "public contract types"),
        ([*pytest, "--collect-only", "--s6-evidence", collected], "owner test inventory"),
        ([*pytest, *executor, "--durations=20", "--s6-evidence", executed], "owner offline behavior"),
        ([sys.executable, "-m", "tools.anti_trick_gate_spec", "coverage", "--revision", revision,
          "--policy", str(TEST_POLICY), "--platform", platform, collected, executed],
         "actual owner test coverage"),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ci", action="store_true", help="Discover and measure the owner tests for this OS.")
    parser.add_argument("--revision", help="CI revision, checked against the checkout.")
    parser.add_argument("--evidence-dir", type=Path, help="Keep test evidence outside the temporary test tree.")
    parser.add_argument("--workers", type=int, choices=(1, 2, 4), help="Test workers for CI execution only.")
    options = parser.parse_args(argv)
    if not options.ci and (options.revision or options.evidence_dir or options.workers):
        parser.error("--revision, --evidence-dir and --workers apply to --ci")
    _safe_console()
    platform = {"win32": "windows", "linux": "linux"}.get(sys.platform, sys.platform)
    if options.ci and platform not in {"linux", "windows"}:
        parser.error("the release test policy covers Linux and Windows")
    gates = [([sys.executable, "-m", "ruff", "check", "scripts", "tests", "tools", "e2e"], "ruff")]
    with tempfile.TemporaryDirectory(prefix="rf-ci-" if options.ci else "rf-local-") as scratch:
        temporary = Path(scratch)
        if options.ci:
            evidence = (options.evidence_dir or (temporary / "evidence")).resolve()
            evidence.mkdir(parents=True, exist_ok=True)
            gates.extend(_ci_commands(
                evidence, temporary / "t", _revision(options.revision), platform, workers=options.workers or 1,
            ))
        else:
            gates.append((
                [sys.executable, "-m", "pytest", "-q", "--tb=short", "--capture=sys", "-p", "no:cacheprovider",
                 *LOCAL_SMOKE_TESTS, "--basetemp", str(temporary / "t")], "fixed local source/ref/forecast smoke",
            ))
        profile = temporary / "home"
        profile.mkdir()
        for command, label in gates:
            code = _run(command, label, timeout=900 if options.ci else 120, profile=profile)
            if code:
                return code
    print("\nOwner behavior and coverage GREEN" if options.ci else "\nlocal_fast_pass: fixed smoke GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
