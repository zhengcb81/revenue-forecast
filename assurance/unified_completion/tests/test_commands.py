"""CA-104 command registry + execution attestation."""

from __future__ import annotations

import hashlib
import json
import sys

import pytest

from uc.commands import CommandSpec, replay_diff, run


def _spec(**overrides) -> CommandSpec:
    payload = {
        "id": "t1",
        "argv": [sys.executable, "-c", "print('hello')"],
        "cwd": ".",
        "env_allowlist": [],
        "timeout_seconds": 120,
        "expected_tier": "T0",
        "side_effect_budget": {"downloads": 0},
    }
    payload.update(overrides)
    return CommandSpec.from_dict(payload)


def test_run_captures_fields_and_hashes(tmp_path):
    result = run(_spec(), tmp_path)
    assert result["exit_code"] == 0
    assert result["business_outcome"] == "pass"
    assert result["stdout_sha256"] == hashlib.sha256(b"hello\n").hexdigest()
    assert result["duration_seconds"] >= 0
    assert result["argv"][0] == sys.executable


def test_env_values_never_recorded(tmp_path, monkeypatch):
    monkeypatch.setenv("MY_SECRET", "s3cr3t-value")
    result = run(_spec(env_allowlist=["MY_SECRET"]), tmp_path)
    serialized = json.dumps(result)
    assert "s3cr3t-value" not in serialized
    assert "MY_SECRET" not in serialized


def test_structured_failure_marker(tmp_path):
    spec = _spec(
        argv=[sys.executable, "-c", "print('engine rejected 41 items'); "],
        failure_markers=["engine rejected"],
    )
    result = run(spec, tmp_path)
    assert result["exit_code"] == 0
    assert result["business_outcome"] == "structured_failure"


def test_infra_error_marker(tmp_path):
    spec = _spec(
        argv=[sys.executable, "-c", "print('network unreachable')"],
        infra_markers=["network unreachable"],
    )
    result = run(spec, tmp_path)
    assert result["business_outcome"] == "infra_error"


def test_pytest_stats_parsing(tmp_path):
    spec = _spec(
        argv=[sys.executable, "-c", "print('116 passed in 157.14s (0:02:37)')"]
    )
    result = run(spec, tmp_path)
    assert result["passed"] == 116
    assert result["collected"] == 116


def test_replay_diff_detects_changed_output(tmp_path):
    spec = _spec()
    recorded = run(spec, tmp_path)
    changed = _spec(argv=[sys.executable, "-c", "print('changed output')"])
    diff = replay_diff(changed, recorded, tmp_path)
    assert diff["stdout_changed"] is True
    same = replay_diff(spec, recorded, tmp_path)
    assert same["stdout_changed"] is False


def test_spec_requires_nonempty_argv():
    with pytest.raises(ValueError):
        CommandSpec.from_dict({"id": "x", "argv": []})
