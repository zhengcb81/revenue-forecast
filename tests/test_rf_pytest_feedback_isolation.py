"""Exercise the default feedback route from pytest and its CLI child."""

import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
PROBE = """
import os
from pathlib import Path
import subprocess
import sys

scripts = Path(os.environ["RF_FEEDBACK_TEST_SCRIPTS"])
sys.path.insert(0, str(scripts))

from rf_feedback_outbox import publish
from rf_local_diagnostics import state_dir


def test_emit(tmp_path, monkeypatch):
    publish({
        "schema_version": "feedback-observation/1", "owner": "revenue-forecast",
        "run_id": "pytest-run", "attempt_id": "pytest-attempt", "step_id": "pytest",
        "check_id": "test", "expected": "ok", "actual": "ok",
    })
    command = [sys.executable, "-B", str(scripts / "rf_job_cli.py"), "list-jobs", "--owner-root"]
    result = subprocess.run(command, timeout=20, stdin=subprocess.DEVNULL, capture_output=True,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert result.returncode == 2
    assert (state_dir() / "feedback.sqlite3").is_file()
    assert len(list((state_dir() / "observations").glob("*.ready"))) == 2

    explicit = tmp_path / "explicit.jsonl"
    monkeypatch.setenv("RESEARCH_FEEDBACK_OUT", str(explicit))
    result = subprocess.run(command, timeout=20, stdin=subprocess.DEVNULL, capture_output=True,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert result.returncode == 2
    assert len(explicit.read_bytes().splitlines()) == 1
"""


@pytest.mark.parametrize("inherit_explicit", (False, True))
def test_pytest_feedback_stays_out_of_inherited_desktop(tmp_path, inherit_explicit):
    suite = tmp_path / "suite"
    tool_tests = suite / "tools" / "tests"
    tool_tests.mkdir(parents=True)
    (suite / "conftest.py").write_bytes((ROOT / "conftest.py").read_bytes())
    (tool_tests / "test_probe.py").write_text(PROBE, encoding="utf-8")
    (suite / "pytest.ini").write_text("[pytest]\n", encoding="ascii")
    desktop = tmp_path / "desktop"
    desktop.mkdir()
    inherited_out = tmp_path / "desktop.jsonl"
    inherited_dir = tmp_path / "desktop-inbox"
    allow = {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "PATHEXT", "SYSTEMDRIVE", "TEMP", "TMP"}
    environment = {key: value for key, value in os.environ.items() if key.upper() in allow}
    environment.update(
        LOCALAPPDATA=str(desktop), XDG_STATE_HOME=str(desktop),
        RF_FEEDBACK_TEST_SCRIPTS=str(ROOT / "scripts"), PYTHONUTF8="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHON_DOTENV_DISABLED="1",
    )
    if inherit_explicit:
        environment.update(RESEARCH_FEEDBACK_OUT=str(inherited_out), RESEARCH_FEEDBACK_DIR=str(inherited_dir))
    child = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "--confcutdir", str(suite), "--basetemp", str(tmp_path / "pt"), "tools/tests/test_probe.py"],
        cwd=suite, env=environment, stdin=subprocess.DEVNULL, capture_output=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), text=True, encoding="utf-8", timeout=60,
    )
    assert not any(desktop.iterdir()), "pytest wrote to the inherited RF owner state"
    assert not inherited_out.exists() and not inherited_dir.exists()
    assert child.returncode == 0, child.stdout + child.stderr
