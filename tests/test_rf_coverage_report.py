"""Coverage reporting stays a diagnostic: no hidden suite, no repo writes.

C1  the compatibility shapes that ``uc.quality._revenue_coverage`` AST-reads
    (``.coveragerc`` ``fail_under`` and ``PER_MODULE_MINIMUM``) stay
    parseable and carry no qualification floors.
C2  default mode only REPORTS coverage data that already exists; with no
    data it says ``not_supplied`` and never starts pytest.
C3  ``--run`` is explicit, runs the offline pytest exactly once, keeps every
    coverage file inside the explicit scratch, and never erases the
    repository's existing ``.coverage``.
C4  a real pytest failure, a coverage launch failure, a timeout and an
    unusable scratch are all non-zero; low numbers stay diagnostics.
"""

from __future__ import annotations

import ast
import configparser
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UC_ROOT = ROOT / "assurance" / "unified_completion"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(UC_ROOT))

import run_coverage_gates as rcg  # noqa: E402
from uc import quality as uc_quality  # noqa: E402

TOOL = ROOT / "tools" / "run_coverage_gates.py"
SHORT_TARGET = "tests/test_schema_compatibility.py"


def _env(**overrides: str) -> dict[str, str]:
    env = dict(os.environ)
    env.pop("COVERAGE_FILE", None)
    env.pop("PYTEST_COVERAGE_EXTRA_ARGS", None)
    env.update(overrides)
    return env


def _run(
    args: list[str], env: dict[str, str] | None = None, timeout: int = 600
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(TOOL), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ROOT),
        env=env if env is not None else _env(),
        timeout=timeout,
    )


def _coverage_root_files() -> dict[str, str]:
    """Coverage DATA files at the repository root (``.coveragerc`` is config)."""
    state: dict[str, str] = {}
    for path in sorted(ROOT.iterdir()):
        if not path.is_file():
            continue
        if path.name != ".coverage" and not path.name.startswith(".coverage."):
            continue
        state[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return state


def _stub(tmp_path: Path, module: str, body: str) -> Path:
    directory = tmp_path / f"stub-{module}"
    directory.mkdir()
    (directory / f"{module}.py").write_text(body, encoding="utf-8")
    return directory


# ---------------------------------------------------------------------------
# C1 — compatibility shapes read by uc.quality._revenue_coverage
# ---------------------------------------------------------------------------


def test_c1_per_module_minimum_is_an_empty_dict_literal():
    tree = ast.parse(TOOL.read_text(encoding="utf-8"))
    assigns: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigns[target.id] = node.value
    assert "PER_MODULE_MINIMUM" in assigns, (
        "uc.quality._revenue_coverage AST-reads PER_MODULE_MINIMUM"
    )
    floors = ast.literal_eval(assigns["PER_MODULE_MINIMUM"])
    assert isinstance(floors, dict)
    assert floors == {}


def test_c1_coveragerc_fail_under_is_zero():
    parser = configparser.ConfigParser()
    parser.read(ROOT / ".coveragerc", encoding="utf-8")
    assert parser.getfloat("report", "fail_under") == 0.0


def test_c1_uc_quality_reads_both_shapes():
    payload = uc_quality._revenue_coverage(ROOT)
    assert payload["total_floor"] == 0.0
    assert payload["per_module_floors"] == {}
    assert payload["sources"] == {
        ".coveragerc": "[report] fail_under",
        "tools/run_coverage_gates.py": "PER_MODULE_MINIMUM",
    }


# ---------------------------------------------------------------------------
# C2 — default mode reports; it never starts the suite
# ---------------------------------------------------------------------------


def test_c2_default_without_data_is_not_supplied(tmp_path):
    env = _env(COVERAGE_FILE=str(tmp_path / "absent" / ".coverage"))
    before = _coverage_root_files()
    proc = _run([], env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "not_supplied" in proc.stdout
    assert "passed" not in proc.stdout
    assert _coverage_root_files() == before


def test_c2_explicit_missing_data_file_is_not_supplied(tmp_path):
    proc = _run(["--data-file", str(tmp_path / "nope" / ".coverage")])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "not_supplied" in proc.stdout


# ---------------------------------------------------------------------------
# C3 — explicit run: one pytest, all data in the scratch, repo untouched
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def explicit_run(tmp_path_factory) -> Path:
    scratch = tmp_path_factory.mktemp("g2-cov-scratch")
    created = not (ROOT / ".coverage").exists()
    if created:
        (ROOT / ".coverage").write_bytes(b"g2-owner-coverage-bytes")
    before = _coverage_root_files()
    try:
        proc = _run(["--run", "--scratch", str(scratch), "--target", SHORT_TARGET])
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert _coverage_root_files() == before, (
            "the explicit run must not touch the repository's .coverage"
        )
    finally:
        if created and (ROOT / ".coverage").exists():
            (ROOT / ".coverage").unlink()
    data_files = [p.name for p in scratch.iterdir() if p.is_file()]
    assert data_files, "the explicit run must leave coverage data in its scratch"
    assert all(name.startswith(".coverage") for name in data_files), data_files
    return scratch


def test_c3_run_keeps_every_coverage_file_in_its_scratch(explicit_run):
    scratch = explicit_run
    assert list(_coverage_root_files()) in ([], [".coverage"]), (
        _coverage_root_files())
    assert any(p.name.startswith(".coverage") for p in scratch.iterdir())


def test_c3_report_reads_the_explicit_run_results_without_pytest(
    explicit_run,
    tmp_path,
):
    stub = _stub(tmp_path, "pytest", "raise SystemExit(9)\n")
    proc = _run(
        ["--data-file", str(explicit_run / ".coverage")],
        env=_env(PYTHONPATH=str(stub)),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "passed" not in proc.stdout
    assert "%" in proc.stdout


def test_c3_run_is_explicit_about_its_scratch():
    proc = _run(["--run"])
    assert proc.returncode != 0
    assert "scratch" in (proc.stdout + proc.stderr)


def test_c3_run_scratch_must_be_a_directory(tmp_path):
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x", encoding="utf-8")
    proc = _run(["--run", "--scratch", str(blocker), "--target", SHORT_TARGET])
    assert proc.returncode != 0, proc.stdout + proc.stderr


def test_c3_run_pytest_failure_is_nonzero(tmp_path):
    proc = _run(
        [
            "--run",
            "--scratch",
            str(tmp_path / "s"),
            "--target",
            str(tmp_path / "does_not_exist.py"),
        ]
    )
    assert proc.returncode != 0, proc.stdout + proc.stderr


def test_c3_run_coverage_launch_failure_is_nonzero(tmp_path):
    stub = _stub(tmp_path, "coverage", "raise SystemExit(7)\n")
    proc = _run(
        ["--run", "--scratch", str(tmp_path / "s"), "--target", SHORT_TARGET],
        env=_env(PYTHONPATH=str(stub)),
        timeout=120,
    )
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "coverage" in (proc.stdout + proc.stderr).lower()


def test_c3_run_timeout_is_nonzero(tmp_path):
    slow = tmp_path / "test_g2_slow.py"
    slow.write_text(
        "import time\n\n\ndef test_slow():\n    time.sleep(5)\n",
        encoding="utf-8",
    )
    proc = _run(
        [
            "--run",
            "--scratch",
            str(tmp_path / "s"),
            "--target",
            str(slow),
            "--timeout",
            "1",
        ],
        timeout=120,
    )
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "time" in (proc.stdout + proc.stderr).lower()


def test_c3_run_builds_exactly_one_pytest_command():
    tree = ast.parse(TOOL.read_text(encoding="utf-8"))
    pytest_lists = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.List):
            continue
        literals = [
            element.value
            for element in node.elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        ]
        if "-m" in literals and "pytest" in literals:
            pytest_lists += 1
    assert pytest_lists == 1, (
        f"expected exactly one literal pytest command, found {pytest_lists}"
    )


# ---------------------------------------------------------------------------
# C4 — real failures stay failures; low numbers stay diagnostics
# ---------------------------------------------------------------------------


def test_c4_low_numbers_do_not_block(explicit_run):
    proc = _run(["--data-file", str(explicit_run / ".coverage")])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    percentages = [
        token.rstrip("%")
        for line in proc.stdout.splitlines()
        for token in line.split()
        if token.endswith("%") and token[:-1].isdigit()
    ]
    assert percentages, proc.stdout
    assert min(float(p) for p in percentages) < 84.0, (
        "the short run must exercise a genuinely low number"
    )


def test_c4_report_mode_tool_failure_is_nonzero(explicit_run, tmp_path):
    stub = _stub(tmp_path, "coverage", "raise SystemExit(7)\n")
    proc = _run(
        ["--data-file", str(explicit_run / ".coverage")],
        env=_env(PYTHONPATH=str(stub)),
    )
    assert proc.returncode != 0, proc.stdout + proc.stderr


def test_c4_module_declares_no_qualification_floors():
    assert json.dumps(rcg.PER_MODULE_MINIMUM) == "{}"
    parser = configparser.ConfigParser()
    parser.read(ROOT / ".coveragerc", encoding="utf-8")
    assert parser.getfloat("report", "fail_under") == 0.0
