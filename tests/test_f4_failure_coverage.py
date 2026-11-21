"""Cold tests at the four RF entry points, using strictly local provider fixtures."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from test_rf_job_facade_cli import _deployment, _request

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def env(root):
    values = {k: v for k, v in os.environ.items() if not k.startswith("RESEARCH_FEEDBACK_")}
    values.update(RESEARCH_FEEDBACK_DIR=str(root / "box"), LOCALAPPDATA=str(root / "state"),
                  XDG_STATE_HOME=str(root / "state"), PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
                  PYTHON_DOTENV_DISABLED="1")
    return values


def invoke(root, environment, script, *args, data=None):
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / (script + ".py")), *map(str, args)],
                          input=data, text=True, encoding="utf-8", capture_output=True, env=environment,
                          cwd=root, timeout=60)


def observations(root):
    events = []
    for ready in root.glob("feedback-*.ready"):
        ident = json.loads(ready.read_bytes())
        assert len(ready.stem.removeprefix("feedback-")) == 32
        for line in ready.with_suffix(".jsonl").read_bytes().splitlines():
            row = json.loads(line)
            assert all(row[k] == ident[k] for k in ("owner", "run_id", "attempt_id", "step_id"))
            events.append(row)
    return events


@pytest.mark.parametrize(("script", "flags", "data", "reason"), [
    ("revenue_forecast", ["bad.json", "--validate-only"], None, "JSONDecodeError"),
    ("source_preparation", ["--request-file", "bad.json"], None, "bad_request"),
    ("report_catalog_cli", ["--owner-root", "OWNER", "get-report", "--report-id", "do-not-copy-request"], None, "not_found"),
    ("rf_job_cli", ["--owner-root", "OWNER", "submit"], "{", "request_invalid"),
])
def test_ordinary_cli_records_original_exit_and_native_reason(tmp_path, script, flags, data, reason):
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    config = env(tmp_path)
    (tmp_path / "artifacts" / "report_catalog").mkdir(parents=True)
    config.update(RESEARCH_FEEDBACK_RUN_ID="one", RESEARCH_FEEDBACK_ATTEMPT_ID="try-one",
                  RESEARCH_FEEDBACK_PROCESS_STEP_ID="root-process")
    flags = [str(tmp_path) if item == "OWNER" else item for item in flags]
    result = invoke(tmp_path, config, script, *flags, data=data)
    assert result.returncode == 2 and result.stderr, result
    row, = observations(tmp_path / "box")
    assert row["check_id"] == "process-outcome" and row["actual"] == "exit:2"
    assert row["run_id"] == "one" and row["attempt_id"] == "try-one"
    assert row["step_id"] != row["parent_step_id"] == "root-process"
    assert reason.lower() in row["reason"].lower()
    assert row["details_ref"].startswith("rf-cli/1/")
    lookup = invoke(tmp_path, config, "rf_job_feedback", "get-failure", row["details_ref"].split("/")[-1])
    assert lookup.returncode == 0, lookup.stderr
    detail = json.loads(lookup.stdout)
    assert detail["native_code"] == row["reason"] and detail["code_version"]
    assert detail["entrypoint"] == script and detail["cause_chain"]
    for secret in ("do-not-copy-request", str(tmp_path)):
        assert secret not in json.dumps([detail, row])


def test_ordinary_failure_spools_and_recovers_without_reexecuting_business(tmp_path):
    path = tmp_path / "blocked"
    path.write_text("occupied")
    config = env(tmp_path)
    config["RESEARCH_FEEDBACK_OUT"] = str(path / "legacy.jsonl")
    request = tmp_path / "input.json"
    request.write_text("{")
    result = invoke(tmp_path, config, "revenue_forecast", request, "--validate-only")
    assert result.returncode == 2
    request.unlink()
    path.unlink()
    path.mkdir()
    for _ in range(2):
        restored = invoke(tmp_path, config, "rf_job_feedback", "flush-feedback")
        assert restored.returncode == 0, restored.stderr
    rows = [json.loads(line) for line in (path / "legacy.jsonl").read_bytes().splitlines()]
    assert len(rows) == 1 and rows[0]["reason"] == "JSONDecodeError"


def test_failed_source_and_unknown_usage_remain_independently_visible(tmp_path):
    owner = tmp_path / "owner"
    owner.mkdir()
    config = env(tmp_path)
    deployment, body = _deployment(tmp_path)
    body.write_bytes(b"X" * body.stat().st_size)
    args = ("--owner-root", owner)
    run = invoke(tmp_path, config, "rf_job_cli", *args, "--deployment-config", deployment,
                 "submit", data=json.dumps(_request()))
    assert run.returncode == 0, run.stderr
    submitted = json.loads(run.stdout)
    job = submitted["owner_job_id"]
    cold = invoke(tmp_path, config, "rf_job_cli", *args, "get-status", "--job-id", job)
    view = json.loads(cold.stdout)["job_view"]
    assert view["status"] == "failed" and view["cost_state"] == "unknown"
    assert [s["status"] for s in view["stages"]] == ["failed", "pending", "pending"]
    assert sum(len(s["attempts"]) for s in view["stages"]) == 1
    rows = observations(tmp_path / "box")
    failure, = (r for r in rows if r["check_id"] == "stage-outcome" and r["actual"] == "failed")
    usage, = (r for r in rows if r["check_id"] == "job-usage")
    assert failure["disposition"] == "deviation" and failure["reason"] == "source_bytes_mismatch"
    assert len([event for event in rows if event["disposition"] == "deviation"]) == 1
    child, = (event for event in rows if event["check_id"] == "stage-native-evidence")
    assert child["parent_step_id"] == failure["step_id"]
    info = json.loads(invoke(tmp_path, config, "rf_job_feedback", "get-failure", child["details_ref"].split("/")[-1]).stdout)
    assert info["native_code"] == "source_bytes_mismatch" and info["exit_code"] == 3
    assert view["stages"][0]["attempts"][0]["observations"]["failure_reason"] == failure["reason"]
    assert usage["disposition"] == "unknown" and usage["actual"] == "unknown"
    assert usage["evidence_ref"] == failure["evidence_ref"] == f"rf-job/1/{job}/source-1"
    assert not any(r["check_id"] == "process-outcome" and r["actual"] == "exit:0" for r in rows)
    assert json.loads(invoke(tmp_path, config, "rf_job_cli", *args, "get-status", "--job-id", job).stdout)["job_view"] == view



def test_default_outbox_and_failed_semantic_native_job_have_separate_causes(tmp_path):
    config = env(tmp_path)
    config.pop("RESEARCH_FEEDBACK_DIR")
    # Empty workspace is a real deployment refusal. Unlike a queried but missing report,
    # this happens before catalog access. It must be separately reproducible.
    result = invoke(tmp_path, config, "report_catalog_cli", "--owner-root", tmp_path, "get-report",
                    "--report-id", "private-argument-not-for-feedback")
    row, = observations(tmp_path / "state" / "revenue-forecast" / "observations")
    assert result.returncode == 2 and row["reason"] == "owner_root_missing"
    assert row["refusal_code"] == "owner_root_missing"
    detail = json.loads(invoke(tmp_path, config, "rf_job_feedback", "get-failure", row["evidence_ref"].split("/")[-1]).stdout)
    assert detail["classification"] == "refusal" and detail["side_effect_state"] == "not_started"
    assert detail["cause_chain"][0]["type"] == "DeploymentError"


def test_native_lookup_will_not_attribute_cli_failure_to_another_step(tmp_path):
    from hashlib import sha256
    config = env(tmp_path)
    config.update(RESEARCH_FEEDBACK_RUN_ID="r", RESEARCH_FEEDBACK_ATTEMPT_ID="a",
                  RESEARCH_FEEDBACK_PROCESS_STEP_ID="root")
    failed = invoke(tmp_path, config, "rf_job_cli", "--owner-root", tmp_path, "submit", data="{")
    assert failed.returncode == 2
    row, = observations(tmp_path / "box")

    def lookup(observation):
        owner = "revenue-forecast"
        key = "3" * 64
        value = {"observation": observation}
        digest = sha256(json.dumps([owner, "reconcile", key, value], sort_keys=True, ensure_ascii=True,
                                   separators=(",", ":")).encode("ascii")).hexdigest()
        request = dict(schema_version="feedback-action/1", owner=owner, kind="reconcile", method="lookup",
                       payload=value, action_id=key, request_digest=digest)
        return json.loads(invoke(tmp_path, config, "rf_job_feedback", "reconcile", "--owner-root", tmp_path,
                                 data=json.dumps(request)).stdout)
    assert lookup(row)["result"]["native_code"] == "request_invalid"
    assert lookup(dict(row, step_id="unrelated"))["state"] == "unknown"

