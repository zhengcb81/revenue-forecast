"""Exercise a real abandoned stage process against the public job and F4 APIs."""

import json
from hashlib import sha256
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from test_f4_failure_coverage import SCRIPTS, env, invoke, observations, reconcile_observation
from test_rf_job_facade_cli import _deployment, _request
from rf_job_facade import JobStore
from owner_atomic_io import native_path, replace_file_bytes
from rf_job_artifacts import selected_artifacts


def _wait_for(path, *, process=None):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if path.is_file():
            return
        if process is not None and process.poll() is not None:
            raise AssertionError(process.communicate())
        time.sleep(0.05)
    raise AssertionError(f"Fixture did not reach {path.name}")


def test_late_compute_cannot_replace_selected_attempt_or_erase_its_own_history(tmp_path):
    deployment, _ = _deployment(tmp_path)
    owner_root = tmp_path / "owner"
    owner_root.mkdir()
    fixture = tmp_path / "compute_fixture.py"
    fixture.write_text(
        "import os, pathlib, sys, time\n"
        "p = pathlib.Path(__file__).parent\n"
        "output = pathlib.Path(sys.argv[sys.argv.index('--output') + 1])\n"
        "(p / 'started').write_text(str(output), encoding='utf-8')\n"
        "until = time.monotonic() + 50\n"
        "while not (p / 'release').exists():\n"
        "    if time.monotonic() >= until: raise SystemExit(1)\n"
        "    time.sleep(0.05)\n"
        "output.write_text('{\"synthetic_late_stage\": true}', encoding='utf-8')\n"
        "pathlib.Path(os.environ['REVENUE_PUBLICATION_REGISTRY']).write_text('late stage registry')\n"
        "pathlib.Path(sys.argv[sys.argv.index('--markdown') + 1]).write_text('late report')\n"
        "(p / 'finished').touch()\n",
        encoding="utf-8",
    )
    launcher = tmp_path / "submit_fixture.py"
    launcher.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        f"sys.path.insert(0, {str(SCRIPTS)!r})\n"
        "import rf_job_facade, rf_job_cli\n"
        f"rf_job_facade._COMPUTE_SCRIPT = Path({str(fixture)!r})\n"
        "raise SystemExit(rf_job_cli.main())\n",
        encoding="utf-8",
    )
    first_environment = env(tmp_path)
    first_environment.update(RESEARCH_FEEDBACK_RUN_ID="original-run", RESEARCH_FEEDBACK_ATTEMPT_ID="original-request")
    args = ("--owner-root", str(owner_root), "--deployment-config", str(deployment))
    child = subprocess.Popen(
        [sys.executable, "-B", str(launcher), *args, "submit"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", env=first_environment, cwd=tmp_path,
    )

    later_environment = env(tmp_path)
    later_environment.update(RESEARCH_FEEDBACK_RUN_ID="restart-run", RESEARCH_FEEDBACK_ATTEMPT_ID="restart-request")

    def call(*flags):
        result = invoke(tmp_path, later_environment, "rf_job_cli", *args, *flags)
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    try:
        child.stdin.write(json.dumps(_request()))
        child.stdin.close()
        # Popen.communicate should not try to flush a closed stdin on error.
        child.stdin = None
        _wait_for(tmp_path / "started", process=child)
        [job] = call("list-jobs")["jobs"]
        job_id = job["owner_job_id"]
        assert job["status"] == "running"
        [started] = [
            row for row in observations(tmp_path / "box")
            if row["check_id"] == "action-started" and row["step_id"].endswith("/compute-1")
        ]
        assert (started["run_id"], started["attempt_id"]) == ("original-run", "original-request")

        child.kill()
        child.communicate(timeout=10)
        status_args = ("--job-id", job_id,)
        assert call("get-status", *status_args)["job_view"]["status"] == "interrupted"
        reconciled = call("act", *status_args, "--action", "reconcile")["job_view"]
        assert reconciled["cost_state"] == "unknown"
        before = reconcile_observation(tmp_path, later_environment, started, owner_root=owner_root)
        assert before["state"] == "done" and before["result"]["job_status"] == "interrupted"

        resumed = call("act", *status_args, "--action", "resume")["job_view"]
        assert resumed["status"] == "succeeded"
        assert resumed["cost_state"] == "unknown"
        assert [stage["attempt_count"] for stage in resumed["stages"]] == [1, 2, 1]
        store = JobStore(owner_root)
        job_dir = store.job_dir(job_id)
        results = selected_artifacts(store.load_job(job_id))
        keys = ("compute_result", "report_markdown", "publication_registry")
        published = {key: sha256((job_dir / results[key]).read_bytes()).hexdigest() for key in keys}
        (tmp_path / "release").touch()
        _wait_for(tmp_path / "finished")
        assert json.loads(Path((tmp_path / "started").read_text(encoding="utf-8")).read_bytes()) == {
            "synthetic_late_stage": True,
        }
        after = call("get-status", *status_args)["job_view"]
        assert after["status"] == "succeeded" and after["result"] == resumed["result"]
        assert {key: sha256((job_dir / results[key]).read_bytes()).hexdigest() for key in keys} == published
        assert reconcile_observation(tmp_path, later_environment, started, owner_root=owner_root) == before
        [terminal] = [
            row for row in observations(tmp_path / "box")
            if row["check_id"] == "stage-outcome" and row["step_id"] == started["step_id"]
        ]
        assert terminal["actual"] == "interrupted"
        assert (terminal["run_id"], terminal["attempt_id"]) == ("original-run", "original-request")
    finally:
        (tmp_path / "release").touch(exist_ok=True)
        if child.poll() is None:
            child.kill()
            child.communicate(timeout=10)


@pytest.mark.parametrize("sink_blocked", (False, True))
def test_native_stage_diagnostics_are_structured_and_do_not_gate_owner_result(tmp_path, sink_blocked):
    deployment, _ = _deployment(tmp_path)
    owner = tmp_path / "owner"
    owner.mkdir()
    fixture = tmp_path / "fault.py"
    fixture.write_text(
        "print('unstructured-private-sentinel')\n"
        "raise PermissionError(13, 'Authorization: Bearer stage-private-sentinel')\n",
        encoding="utf-8",
    )
    launcher = tmp_path / "fault_launcher.py"
    block_logs = (
        "def diagnostic_paths(self, owner_job_id, stage, attempt_no):\n"
        "    target = self.job_dir(owner_job_id) / 'logs-blocker'\n"
        "    target.touch(exist_ok=True)\n"
        "    return target / 'out', target / 'err'\n"
        "rf_job_facade.JobStore.log_paths = diagnostic_paths\n"
    )
    launcher.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        f"sys.path.insert(0, {str(SCRIPTS)!r})\n"
        "import rf_job_facade, rf_job_cli\n"
        f"rf_job_facade._COMPUTE_SCRIPT = Path({str(fixture)!r})\n"
        + (block_logs if sink_blocked else "")
        + "raise SystemExit(rf_job_cli.main())\n",
        encoding="utf-8",
    )
    config = env(tmp_path)
    args = ("--owner-root", str(owner), "--deployment-config", str(deployment))
    response = subprocess.run(
        [sys.executable, "-B", str(launcher), *args, "submit"], input=json.dumps(_request()),
        capture_output=True, text=True, encoding="utf-8", timeout=30, env=config, cwd=tmp_path,
    )
    assert response.returncode == 0, response.stderr
    body = json.loads(response.stdout)
    view = body["job_view"]
    assert [stage["status"] for stage in view["stages"]] == ["completed", "failed", "pending"]
    [attempt] = view["stages"][1]["attempts"]
    assert attempt["exit_code"] == 1 and attempt["execution_state"] == "exited"
    [cause] = attempt["diagnostics"]["child_errors"]
    assert cause["type"] == "PermissionError" and cause["errno"] == 13
    assert cause["file"] == "fault.py" and cause["line"] == 2
    status = invoke(tmp_path, config, "rf_job_cli", *args, "get-status", "--job-id", body["owner_job_id"])
    assert json.loads(status.stdout)["job_view"]["stages"] == view["stages"]
    persisted = b"".join(path.read_bytes() for path in owner.rglob("*") if path.is_file())
    assert b"stage-private-sentinel" not in persisted and b"unstructured-private-sentinel" not in persisted


@pytest.mark.windows_only
@pytest.mark.skipif(os.name != "nt", reason="Windows replacement sharing semantics")
def test_owner_atomic_retries_the_same_prepared_replacement(tmp_path, monkeypatch):
    path = tmp_path / "job-state.json"
    path.write_bytes(b"old state")
    real_replace = os.replace
    observed = []

    def temporarily_blocked(source, target):
        observed.append(source)
        assert target == native_path(path)
        assert path.read_bytes() == b"old state"
        assert source.read_bytes() == b"complete new state"
        if len(observed) < 3:
            raise OSError(13, "sharing conflict", str(source), 32)
        real_replace(source, target)

    monkeypatch.setattr(os, "replace", temporarily_blocked)
    replace_file_bytes(path, b"complete new state")
    assert path.read_bytes() == b"complete new state" and len(set(observed)) == 1 and len(observed) == 3
