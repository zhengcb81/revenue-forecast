"""Local fixed smoke and CI coverage have distinct, executable plans."""
from __future__ import annotations

import importlib.util
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _gate():
    spec = importlib.util.spec_from_file_location("rf_fast_gate_test", ROOT / "tools/pre_push_gate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _commands(monkeypatch, mode):
    gate = _gate()
    calls = []
    monkeypatch.setattr(gate, "_run", lambda command, label, **kw: calls.append(command) or 0)
    assert gate.main(mode) == 0
    return gate, calls


def test_workflow_explicitly_selects_the_complete_ci_plan():
    workflow = yaml.safe_load((ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))
    assert len(workflow["jobs"]) == 1
    commands = [shlex.split(line) for job in workflow["jobs"].values()
                for step in job["steps"] for line in step.get("run", "").splitlines() if line.strip()]
    gates = [tokens for tokens in commands if tokens[:2] == ["python", "tools/pre_push_gate.py"]]
    assert gates == [["python", "tools/pre_push_gate.py", "--ci"]]


def test_default_local_plan_is_fixed_small_smoke_without_repeated_mypy(monkeypatch):
    gate, commands = _commands(monkeypatch, [])
    assert not any(command[1:3] == ["-m", "mypy"] for command in commands)
    pytests = [command for command in commands if command[:3] == [sys.executable, "-m", "pytest"]]
    assert len(pytests) == 1
    selected = [arg for arg in pytests[0] if arg.startswith("tests/")]
    assert selected == list(gate.LOCAL_SMOKE_TESTS)
    assert all("::" in node for node in selected)
    assert len(selected) == len(set(selected))
    assert set(node.split("::")[0] for node in selected) <= set(gate.CI_TESTS)
    assert "tests/test_p5_source_default_v2.py::test_default_entry_uses_source_ref_v2_without_opt_in" in selected
    assert "tests/test_company_wiki_source_ref_v2.py::test_producer_golden_is_pinned_and_accepted_by_reader" in selected
    assert "tests/test_recognition_bridge.py::RecognitionBridgeTests::test_company_aggregates_recognized_segments" in selected
    assert "tests/test_published_foundation_roundtrip.py::test_forged_opening_base_or_adjustment_is_rejected" in selected


def test_ci_preserves_the_complete_behavior_set_and_types_once(monkeypatch):
    gate, commands = _commands(monkeypatch, ["--ci"])
    assert sum(command[1:3] == ["-m", "ruff"] for command in commands) == 1
    assert sum(command[1:3] == ["-m", "mypy"] for command in commands) == 1
    pytests = [command for command in commands if command[:3] == [sys.executable, "-m", "pytest"]]
    assert len(pytests) == 1
    assert [arg for arg in pytests[0] if arg.startswith("tests/")] == list(gate.CI_TESTS)
    assert gate.SMOKE_TESTS == gate.CI_TESTS  # Historical import alias keeps its meaning.
    assert "tests/test_registry_confidence_generations.py" in gate.CI_TESTS
    assert "tests/test_p5_source_default_cli_e2e.py" in gate.CI_TESTS
    assert "tests/test_confidence_determinism.py" in gate.CI_TESTS


@pytest.mark.parametrize("mode", [[], ["--ci"]])
def test_child_failure_remains_blocking_in_either_plan(monkeypatch, mode):
    gate = _gate()
    def child(command, *_args, **_kwargs):
        return 19 if command[:3] == [sys.executable, "-m", "pytest"] else 0
    monkeypatch.setattr(gate, "_run", child)
    assert gate.main(mode) == 19


def test_local_nodes_really_collect_fewer_than_fifty_cases(tmp_path):
    gate = _gate()
    nodes = getattr(gate, "LOCAL_SMOKE_TESTS", gate.SMOKE_TESTS)
    proc = subprocess.run([sys.executable, "-B", "-m", "pytest", "--collect-only", "-q",
        "-p", "no:cacheprovider", *nodes, "--basetemp", str(tmp_path / "collection")],
        cwd=ROOT, env=gate._subprocess_environment(), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30)
    assert proc.returncode == 0, (proc.stdout + proc.stderr)[-1200:]
    count = re.search(r"(\d+) tests? collected", proc.stdout)
    assert count is not None, proc.stdout[-1200:]
    assert 0 < int(count.group(1)) < 50


def test_unsupported_flags_are_not_a_skip_channel():
    with pytest.raises(SystemExit) as stopped:
        _gate().main(["--skip-tests"])
    assert stopped.value.code == 2


def test_default_cli_fixture_requires_siblings_without_opt_in(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location("p5_roots_test", ROOT / "tests/test_p5_source_default_cli_e2e.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.delenv("FF_V2_CODE_ROOT", raising=False)
    monkeypatch.delenv("CWP_V2_CODE_ROOT", raising=False)
    rf = tmp_path / "revenue-forecast"
    rf.mkdir()
    monkeypatch.setattr(module, "ROOT", rf)
    for name in ("filing-fetch", "company-wiki"):
        (tmp_path / name).mkdir()
    assert module._env_roots() == (tmp_path / "filing-fetch", tmp_path / "company-wiki")
    (tmp_path / "company-wiki").rmdir()
    with pytest.raises(FileNotFoundError):
        module._env_roots()
