"""The push hook must not pin child Git commands to the parent repository."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pre_push_gate  # noqa: E402


_REPOSITORY_CONTEXT = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_PREFIX", "GIT_NAMESPACE", "GIT_QUARANTINE_PATH",
)


def test_pre_push_child_environment_drops_parent_git_context(
    monkeypatch,
) -> None:
    captured: dict[str, str] = {}
    for name in _REPOSITORY_CONTEXT:
        monkeypatch.setenv(name, f"parent-{name}")
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "scoped-safe-directory")

    def fake_run(command, **kwargs):
        child_env = kwargs.get("env") or os.environ
        for name in (*_REPOSITORY_CONTEXT, "GIT_CONFIG_PARAMETERS"):
            if name in child_env:
                captured[name] = child_env[name]
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(pre_push_gate.subprocess, "run", fake_run)
    assert pre_push_gate._run([sys.executable, "-c", "pass"], "environment test") == 0

    for name in _REPOSITORY_CONTEXT:
        assert name not in captured
    assert captured["GIT_CONFIG_PARAMETERS"] == "scoped-safe-directory"
