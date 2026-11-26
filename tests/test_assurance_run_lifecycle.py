"""Scheduled owner reads remain traceable across a killed Windows or POSIX host."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from test_f4_failure_coverage import env, observations, reconcile_observation
from test_rf_job_attempt_lifecycle import _wait_for


TOOLS = Path(__file__).resolve().parents[1] / "tools"


@pytest.mark.parametrize("period", ["daily", "weekly"])
def test_schedule_leaves_current_attempt_before_owner_read(tmp_path, period):
    config = env(tmp_path)
    ledger = tmp_path / ("manifest-" + period + ".json")
    ledger.write_bytes(b'{"latest_run_id":"previous-success","ok":true}')
    alerts = tmp_path / "alerts"
    if period == "daily":
        script = TOOLS / "daily_t2_schedule.py"
        producer = tmp_path / "company_wiki" / "source_catalog" / "cli.py"
        config["PYTHONPATH"] = str(tmp_path)
        options = ["--config", str(tmp_path / "catalog"), "--report-root", str(tmp_path / "reports")]
        finish = "print(json.dumps(dict(documents=0,sources=0,active_locations=0,missing_locations=0)))\n"
    else:
        script = TOOLS / "weekly_t3_schedule.py"
        producer = tmp_path / "ff" / "scripts" / "ff_t3_receipt.py"
        options = ["--filing-fetch-root", str(tmp_path / "ff"), "--run-id", "ff-existing"]
        finish = "raise PermissionError(13, 'fixture-unmarked-secret')\n"
    producer.parent.mkdir(parents=True)
    if period == "daily":
        (producer.parent / "__init__.py").touch()
        (producer.parent.parent / "__init__.py").touch()
    producer.write_text(
        "import json,pathlib,time,os\n"
        "r=pathlib.Path(os.environ['RF_FIXTURE_ROOT'])\n"
        "with (r/'called').open('a') as out: out.write('read\\n')\n"
        "(r/'ready').touch()\n"
        "until=time.monotonic()+20\n"
        "while not (r/'release').exists() and time.monotonic()<until: time.sleep(.05)\n"
        "(r/'finished').touch()\n" + finish, encoding="utf-8",
    )
    config["RF_FIXTURE_ROOT"] = str(tmp_path)
    command = [sys.executable, "-B", str(script), "--ledger", str(ledger), "--alerts", str(alerts)]
    before = ledger.read_bytes()
    process = subprocess.Popen(
        command + ["run-" + period, *options], cwd=tmp_path, env=config,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )

    def fetch(*args):
        response = subprocess.run(
            command + ["get-run", *args], capture_output=True, text=True, encoding="utf-8",
            cwd=tmp_path, env=config, timeout=20,
        )
        assert response.returncode == 0, response.stderr
        return json.loads(response.stdout)

    try:
        _wait_for(tmp_path / "ready", process=process)
        original = fetch()
        assert original["state"] == "started" and original["ended_at"] is None
        assert original["period"] == period and original["code_version"]
        assert original["effect"] == "read_only"
        if period == "weekly":
            assert original["request"]["owner_run_id"] == "ff-existing"
        process.kill()
        process.wait(timeout=10)
        (tmp_path / "release").touch()
        _wait_for(tmp_path / "finished")
        assert fetch("--run-id", original["run_id"]) == original
        assert fetch("--run-id", original["run_id"]) == original
        [started] = observations(tmp_path / "box")
        assert started["run_id"] == original["run_id"] and started["check_id"] == "action-started"
        def lookup(row):
            return reconcile_observation(tmp_path, config, row, ledger=(period, ledger))
        assert lookup(started) == lookup(started) == {"state": "pending"}
        assert ledger.read_bytes() == before and not alerts.exists()
        assert (tmp_path / "called").read_text().splitlines() == ["read"]

        terminal = subprocess.run(command + ["run-" + period, *options], cwd=tmp_path, env=config,
                                  capture_output=True, text=True, encoding="utf-8", timeout=20)
        assert terminal.returncode == (0 if period == "daily" else 2)
        latest = fetch()
        assert latest["state"] == ("completed" if period == "daily" else "failed")
        assert latest["exit_code"] == terminal.returncode and latest["ended_at"]
        assert latest["run_id"] != original["run_id"]
        assert fetch("--run-id", original["run_id"]) == original
        [outcome] = [row for row in observations(tmp_path / "box")
                     if row["run_id"] == latest["run_id"] and row["check_id"] == "stage-outcome"]
        assert lookup(outcome)["result"]["cost_state"] == "not_applicable"
        assert lookup(outcome)["result"]["job_status"] == ("succeeded" if period == "daily" else "failed")
        assert lookup(started) == {"state": "pending"}
        assert (tmp_path / "called").read_text().splitlines() == ["read", "read"]
        if period == "weekly":
            [cause] = latest["diagnostic"]["cause_chain"]
            assert cause["type"] == "PermissionError" and cause["errno"] == 13
            assert cause["file"] == "ff_t3_receipt.py" and cause["line"] > 0
            assert "fixture-unmarked-secret" not in json.dumps(latest) + terminal.stdout + terminal.stderr
    finally:
        (tmp_path / "release").touch(exist_ok=True)
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
