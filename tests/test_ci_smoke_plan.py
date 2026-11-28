"""Local fixed smoke and CI coverage have distinct, executable plans."""
from __future__ import annotations

import importlib.util
import json
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
    monkeypatch.setattr(gate, "_revision", lambda requested: requested or "a" * 40)
    monkeypatch.setattr(gate, "_run", lambda command, label, **kw: calls.append(command) or 0)
    assert gate.main(mode) == 0
    return gate, calls


def test_workflow_runs_canonical_suite_on_both_platforms():
    workflow = yaml.safe_load((ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))
    job = workflow["jobs"]["verify"]
    assert job["strategy"]["matrix"]["os"] == ["ubuntu-latest", "windows-latest"]
    assert job["runs-on"] == "${{ matrix.os }}"
    checked_out = job["steps"][0]["with"]
    assert checked_out["persist-credentials"] is False
    revision = "${{ github.event.pull_request.head.sha || github.sha }}"
    assert checked_out["ref"] == revision
    commands = [shlex.split(line) for step in job["steps"]
                for line in step.get("run", "").splitlines() if line.strip()]
    gates = [tokens for tokens in commands if tokens[:2] == ["python", "tools/pre_push_gate.py"]]
    assert gates == [[
        "python", "tools/pre_push_gate.py", "--ci", "--revision", revision,
        "--evidence-dir", "${{ runner.temp }}/rf-s6",
    ]]
    assert any(step.get("uses") == "actions/upload-artifact@v4" for step in job["steps"])


def test_default_local_plan_is_fixed_small_smoke_without_repeated_mypy(monkeypatch):
    gate, commands = _commands(monkeypatch, [])
    assert not any(command[1:3] == ["-m", "mypy"] for command in commands)
    pytests = [command for command in commands if command[:3] == [sys.executable, "-m", "pytest"]]
    assert len(pytests) == 1
    selected = [arg for arg in pytests[0] if arg.startswith("tests/")]
    assert selected == list(gate.LOCAL_SMOKE_TESTS)
    assert all("::" in node for node in selected)
    assert len(selected) == len(set(selected))
    assert "tests/test_p5_source_default_v2.py::test_default_entry_uses_source_ref_v2_without_opt_in" in selected
    assert "tests/test_company_wiki_source_ref_v2.py::test_producer_golden_is_pinned_and_accepted_by_reader" in selected
    assert "tests/test_recognition_bridge.py::RecognitionBridgeTests::test_company_aggregates_recognized_segments" in selected
    assert "tests/test_published_foundation_roundtrip.py::test_forged_opening_base_or_adjustment_is_rejected" in selected


@pytest.mark.parametrize("platform,boundary", [("linux", "windows_only"), ("windows", "posix_only")])
def test_ci_collects_once_and_executes_once_per_os(monkeypatch, platform, boundary, tmp_path):
    gate = _gate()
    commands = [command for command, _ in gate._ci_commands(
        tmp_path / "receipts", tmp_path / "temp", "b" * 40, platform,
    )]
    pytests = [command for command in commands if command[:3] == [sys.executable, "-m", "pytest"]]
    assert len(pytests) == 2
    assert "--collect-only" in pytests[0]
    assert "--collect-only" not in pytests[1]
    for command in pytests:
        assert "tools.anti_trick_gate_spec.pytest_probe" in command
        assert [arg for arg in command if arg in {"tests", "tools/tests"}] == ["tests", "tools/tests"]
        expression = command[command.index("-m", 3) + 1]
        assert expression == f"not live and not composition and not {boundary}"
    assert pytests[0][pytests[0].index("--s6-evidence") + 1].endswith("collected.json")
    assert pytests[1][pytests[1].index("--s6-evidence") + 1].endswith("executed.json")
    assert commands[-1][2:4] == ["tools.anti_trick_gate_spec", "coverage"]
    assert sum(command[1:3] == ["-m", "mypy"] for command in commands) == 1
    assert set(json.loads(gate.TEST_POLICY.read_text(encoding="utf-8"))["platforms"]) == {"linux", "windows"}


@pytest.mark.parametrize("mode", [[], ["--ci"]])
def test_child_failure_remains_blocking_in_either_plan(monkeypatch, mode):
    gate = _gate()
    def child(command, *_args, **_kwargs):
        return 19 if command[:3] == [sys.executable, "-m", "pytest"] else 0
    monkeypatch.setattr(gate, "_run", child)
    monkeypatch.setattr(gate, "_revision", lambda _requested: "a" * 40)
    assert gate.main(mode) == 19


def test_local_nodes_really_collect_fewer_than_fifty_cases(tmp_path):
    gate = _gate()
    nodes = gate.LOCAL_SMOKE_TESTS
    proc = subprocess.run([sys.executable, "-B", "-m", "pytest", "--collect-only", "-q",
        "-p", "no:cacheprovider", *nodes, "--basetemp", str(tmp_path / "collection")],
        cwd=ROOT, env=gate._subprocess_environment(), stdin=subprocess.DEVNULL,
        capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        encoding="utf-8", errors="replace", timeout=30)
    assert proc.returncode == 0, (proc.stdout + proc.stderr)[-1200:]
    count = re.search(r"(\d+) tests? collected", proc.stdout)
    assert count is not None, proc.stdout[-1200:]
    assert 0 < int(count.group(1)) < 50


def test_unsupported_flags_are_not_a_skip_channel():
    with pytest.raises(SystemExit) as stopped:
        _gate().main(["--skip-tests"])
    assert stopped.value.code == 2


def test_consumer_ci_never_bootstraps_a_sibling_checkout():
    workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
    assert "ci_checkout_siblings.py" not in workflow
    assert "company-wiki/src" not in workflow
