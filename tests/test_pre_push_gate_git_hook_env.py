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
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "synthetic-sensitive-git-config")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "synthetic-private-fixture")

    def fake_run(command, **kwargs):
        child_env = kwargs.get("env") or os.environ
        for name in (*_REPOSITORY_CONTEXT, "GIT_CONFIG_PARAMETERS", "ANTHROPIC_AUTH_TOKEN"):
            if name in child_env:
                captured[name] = child_env[name]
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(pre_push_gate.subprocess, "run", fake_run)
    assert pre_push_gate._run([sys.executable, "-c", "pass"], "environment test") == 0

    for name in _REPOSITORY_CONTEXT:
        assert name not in captured
    assert "GIT_CONFIG_PARAMETERS" not in captured
    assert "ANTHROPIC_AUTH_TOKEN" not in captured


def test_actual_child_git_uses_its_own_repo_under_parent_hook_context(monkeypatch, tmp_path):
    child = tmp_path / "child-repo"
    subprocess.run(["git", "init", "-q", str(child)], check=True,
        stdin=subprocess.DEVNULL, capture_output=True, env=pre_push_gate._subprocess_environment(),
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    monkeypatch.setenv("GIT_DIR", str(ROOT / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(ROOT))
    monkeypatch.setenv("GIT_INDEX_FILE", str(ROOT / ".git" / "index"))
    monkeypatch.setenv("REVENUE_ATTESTATION_PROVIDER", "should-not-be-called-in-tests")
    code = (
        "import os,pathlib,subprocess,sys;"
        "assert not os.environ.get('REVENUE_ATTESTATION_PROVIDER');"
        "assert os.environ.get('PYTHON_DOTENV_DISABLED')=='1';"
        "actual=subprocess.check_output(['git','-C',sys.argv[1],'rev-parse','--show-toplevel'],text=True).strip();"
        "assert pathlib.Path(actual).resolve()==pathlib.Path(sys.argv[1]).resolve()"
    )
    assert pre_push_gate._run([sys.executable, "-B", "-c", code, str(child)], "isolated child Git") == 0


def test_engineering_subprocess_uses_disposable_owner_profile(monkeypatch, tmp_path):
    monkeypatch.setenv("USERPROFILE", "/unrelated-owner-profile")
    environment = pre_push_gate._subprocess_environment(tmp_path)
    assert {
        environment[key] for key in ("HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_STATE_HOME")
    } == {str(tmp_path)}


def test_failed_gate_preserves_the_first_collection_error(monkeypatch, capsys):
    def failed(command, **_kwargs):
        return subprocess.CompletedProcess(
            command, 4, "first reason: missing fixture\n" + "x" * 2400,
            "ERROR: first affected test\n" + "z" * 1200,
        )

    monkeypatch.setattr(pre_push_gate.subprocess, "run", failed)

    assert pre_push_gate._run(["pytest"], "consumer checks") == 4
    output = capsys.readouterr()
    assert "first reason: missing fixture" in output.out
    assert "ERROR: first affected test" in output.err


def test_timeout_preserves_recorded_progress_without_an_exception_trace(monkeypatch, capsys):
    def stalled(command, **options):
        raise subprocess.TimeoutExpired(
            command, options["timeout"], output=b"173 realistic fixtures started\n",
            stderr=b"phase: a native lock acquisition\n",
        )

    monkeypatch.setattr(pre_push_gate.subprocess, "run", stalled)
    assert pre_push_gate._run(["pytest"], "owner offline behavior", timeout=2) == 1
    output = capsys.readouterr()
    assert "173 realistic fixtures started" in output.out
    assert "phase: a native lock acquisition" in output.err
    assert "owner offline behavior exceeded 2s" in output.err
