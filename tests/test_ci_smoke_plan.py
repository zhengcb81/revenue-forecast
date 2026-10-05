"""The daily gate covers current behavior once and never touches owner data."""
from __future__ import annotations

import importlib.util
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


def test_daily_ci_runs_one_shared_gate():
    workflow = yaml.safe_load((ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))
    assert len(workflow["jobs"]) == 1
    runs = [step.get("run", "") for job in workflow["jobs"].values() for step in job["steps"]]
    assert sum("python tools/pre_push_gate.py" in run for run in runs) == 1
    forbidden = ("run_coverage_gates", "mutation_patrol", "sync_installations", "verify_plan_claims")
    assert not any(name in run for name in forbidden for run in runs)


def test_fast_gate_covers_default_cli_and_calculation_once(monkeypatch):
    gate = _gate()
    calls = []
    monkeypatch.setattr(gate, "_run", lambda command, label, **kw: calls.append(command) or 0)
    assert gate.main([]) == 0
    pytest_commands = [command for command in calls if command[:3] == [sys.executable, "-m", "pytest"]]
    assert len(pytest_commands) == 1
    command = pytest_commands[0]
    for name in ("tests/test_p5_source_default_v2.py", "tests/test_p5_source_default_cli_e2e.py", "tests/test_recognition_bridge.py", "tests/test_growth_driver_tree.py"):
        assert name in command
    assert not any("sync_installations" in item or "production" in item for call in calls for item in call)
    monkeypatch.setattr(gate, "_run", lambda *a, **kw: 7)
    assert gate.main([]) == 7


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
