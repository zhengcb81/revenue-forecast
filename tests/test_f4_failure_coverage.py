"""Cold tests at the four RF entry points, using strictly local provider fixtures."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from test_rf_job_facade_cli import _deployment, _request
from owner_atomic_io import native_path

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


def reconcile_observation(root, config, observation, *, owner_root=None, ledger=None):
    def digest(value):
        content = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        return sha256(content.encode("ascii")).hexdigest()

    owner = "revenue-forecast"
    original = dict(observation, origin_owner=observation.get("origin_owner", observation["owner"]))
    identity = [original[key] for key in ("owner", "origin_owner", "run_id", "attempt_id", "step_id", "check_id")]
    occurrence = digest(identity)
    key = digest(["reconcile", owner, occurrence])
    payload = {"occurrence_id": occurrence, "observation": original}
    request = dict(schema_version="feedback-action/1", owner=owner, kind="reconcile", method="lookup",
                   payload=payload, action_id=key, request_digest=digest([owner, "reconcile", key, payload]))
    args = ("--assurance-ledger", *ledger) if ledger is not None else ()
    reply = invoke(root, config, "rf_job_feedback", "reconcile", "--owner-root", owner_root or root,
                   *args, data=json.dumps(request))
    assert reply.returncode == 0, reply.stderr
    return json.loads(reply.stdout)


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


@pytest.mark.parametrize(("script", "exception_type", "exit_code"), [
    ("revenue_forecast", "KeyError", 1),
    ("rf_job_cli", "AttributeError", 3),
])
def test_engine_fault_keeps_its_frames_without_becoming_input_refusal(
    tmp_path, script, exception_type, exit_code,
):
    request = _request()
    path = tmp_path / "input.json"
    path.write_text(json.dumps(request["forecast_input"]), encoding="utf-8")
    if script == "rf_job_cli":
        deployment, _ = _deployment(tmp_path)
        flags = ("--owner-root", str(tmp_path), "--deployment-config", str(deployment), "submit")
    else:
        flags = (str(path), "--validate-only", "--verbose")
    launcher = (
        "import importlib, sys\n"
        "from unittest.mock import patch\n"
        "sys.path.insert(0, sys.argv.pop(1))\n"
        "entry = importlib.import_module(sys.argv.pop(1))\n"
        "exception_type = getattr(__import__('builtins'), sys.argv.pop(1))\n"
        "with patch('contracts.document.validate_source_coverage', "
        "side_effect=exception_type('do-not-copy-request')):\n"
        "    raise SystemExit(entry.main())\n"
    )
    configuration = {
        key: value for key, value in env(tmp_path).items()
        if key.upper() in {"SYSTEMROOT", "SYSTEMDRIVE", "PATH", "TEMP", "TMP",
                           "RESEARCH_FEEDBACK_DIR", "LOCALAPPDATA", "XDG_STATE_HOME",
                           "PYTHONDONTWRITEBYTECODE", "PYTHONUTF8", "PYTHON_DOTENV_DISABLED"}
    }
    result = subprocess.run(
        [sys.executable, "-B", "-c", launcher, str(SCRIPTS), script, exception_type, *flags],
        input=json.dumps(request) if script == "rf_job_cli" else "",
        env=configuration, cwd=tmp_path, capture_output=True, text=True,
        encoding="utf-8", timeout=30,
    )
    assert result.returncode == exit_code and result.stdout == "", result
    if script == "rf_job_cli":
        assert json.loads(result.stderr)["error"]["code"] == "internal"
        assert not list((tmp_path / "artifacts" / "rf_jobs" / "jobs").glob("*"))
    else:
        assert result.stderr.strip() == f"error: internal forecast failure ({exception_type})"

    row, = observations(tmp_path / "box")
    assert row["actual"] == f"exit:{exit_code}" and "refusal_code" not in row
    lookup = invoke(tmp_path, configuration, "rf_job_feedback", "get-failure",
                    row["details_ref"].split("/")[-1])
    assert lookup.returncode == 0, lookup.stderr
    detail = json.loads(lookup.stdout)
    cause, = detail["cause_chain"]
    assert cause["type"] == exception_type
    assert {"validate_document", "_run_gate"} <= {
        frame["function"] for frame in cause["frames"] if frame["file"] == "contracts/document.py"
    }
    assert "do-not-copy-request" not in lookup.stdout and str(tmp_path) not in lookup.stdout


def test_ordinary_failure_spools_and_recovers_without_reexecuting_business(tmp_path):
    path = tmp_path / "blocked"
    path.write_text("occupied")
    config = env(tmp_path)
    config["RESEARCH_FEEDBACK_OUT"] = str(path / "legacy.jsonl")
    request = tmp_path / "input.json"
    request.write_text("{")
    result = invoke(tmp_path, config, "revenue_forecast", request, "--validate-only")
    assert result.returncode == 2
    outbox_log = tmp_path / "state" / "revenue-forecast" / "logs" / "runtime-errors.jsonl"
    diagnostic, = (json.loads(line) for line in outbox_log.read_bytes().splitlines())
    assert diagnostic["operation"] == "feedback_delivery" and diagnostic["code"] == "outbox_delayed"
    request.unlink()
    path.unlink()
    path.mkdir()
    for _ in range(2):
        restored = invoke(tmp_path, config, "rf_job_feedback", "flush-feedback")
        assert restored.returncode == 0, restored.stderr
    rows = [json.loads(line) for line in (path / "legacy.jsonl").read_bytes().splitlines()]
    assert len(rows) == 1 and rows[0]["reason"] == "JSONDecodeError"


@pytest.mark.parametrize(("operation", "reason", "effect", "exit_code"), [
    ("get-status", "owner_job_id_invalid", "not_started", 2),
    ("list-jobs", "internal", "not_started", 3),
    ("reconcile", "owner_job_id_invalid", "not_started", 2),
    ("resume", "owner_job_id_invalid", "unknown", 2),
])
def test_job_cli_failure_distinguishes_local_operations_from_execution(
    tmp_path, operation, reason, effect, exit_code,
):
    if operation == "list-jobs":
        (tmp_path / "artifacts/rf_jobs/index/jobs.jsonl").mkdir(parents=True)
        args = ("list-jobs",)
    elif operation == "get-status":
        args = ("get-status", "--job-id", "not-a-job")
    else:
        args = ("act", "--job-id", "not-a-job", "--action", operation)
    config = env(tmp_path)
    result = invoke(tmp_path, config, "rf_job_cli", "--owner-root", tmp_path, *args)
    assert result.returncode == exit_code and json.loads(result.stderr)["error"]["code"] == reason
    row, = observations(tmp_path / "box")
    lookup = invoke(tmp_path, config, "rf_job_feedback", "get-failure", row["evidence_ref"].rsplit("/", 1)[1])
    assert lookup.returncode == 0, lookup.stderr
    detail = json.loads(lookup.stdout)
    assert detail["operation"] == operation and detail["side_effect_state"] == effect
    assert "not-a-job" not in lookup.stdout and str(tmp_path) not in lookup.stdout
    recovery = reconcile_observation(tmp_path, config, row)["result"]
    assert recovery["job_status"] == "failed"
    assert recovery["cost_state"] == ("unknown" if effect == "unknown" else "not_applicable")


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
    stage = reconcile_observation(tmp_path, config, usage, owner_root=owner)
    assert stage == {"state": "done", "result": {"status": "cost_unknown", "job_status": "failed",
                     "cost_state": "unknown", "evidence_ref": usage["evidence_ref"]}}
    for field in ("run_id", "attempt_id"):
        other_scope = {**usage, field: "some-other-run-scope"}
        assert reconcile_observation(tmp_path, config, other_scope, owner_root=owner) == {
            "state": "unknown", "code": "native_attempt_mismatch",
        }
    native = reconcile_observation(tmp_path, config, child, owner_root=owner)
    assert native == {"state": "done", "result": {"status": "cost_unknown", "job_status": "failed",
                      "cost_state": "unknown", "native_code": "source_bytes_mismatch",
                      "side_effect_state": "unknown", "evidence_ref": child["evidence_ref"]}}
    assert reconcile_observation(tmp_path, config, child, owner_root=owner) == native
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
    config = env(tmp_path)
    config.update(RESEARCH_FEEDBACK_RUN_ID="r", RESEARCH_FEEDBACK_ATTEMPT_ID="a",
                  RESEARCH_FEEDBACK_PROCESS_STEP_ID="root")
    failed = invoke(tmp_path, config, "rf_job_cli", "--owner-root", tmp_path, "submit", data="{")
    assert failed.returncode == 2
    row, = observations(tmp_path / "box")

    receipt = {"state": "done", "result": {"status": "known", "job_status": "failed",
               "cost_state": "not_applicable", "native_code": "request_invalid",
               "side_effect_state": "not_started", "evidence_ref": row["evidence_ref"]}}
    assert reconcile_observation(tmp_path, config, row) == receipt
    assert reconcile_observation(tmp_path, config, row) == receipt
    assert reconcile_observation(tmp_path, config, dict(row, step_id="unrelated")) == {"state": "unknown"}
    missing = dict(row, evidence_ref="rf-cli/1/" + "0" * 32)
    assert reconcile_observation(tmp_path, config, missing) == {"state": "unknown"}



def test_untrusted_exception_attributes_and_failing_feedback_never_replace_native_outcome(tmp_path):
    config = env(tmp_path)
    (tmp_path / "valid.json").write_text("{}")
    (tmp_path / "invalid.json").write_text("{")
    body = """import sys
sys.path.insert(0, sys.argv[1])
import rf_cli_feedback, revenue_forecast as rf
class BrokenReport(Exception):
    @property
    def lineno(self):
        raise RuntimeError("optional_diagnostic_override")
def crash(*args, **kwargs):
    raise BrokenReport()
def broken_projection(*args, **kwargs):
    raise RuntimeError("optional_diagnostic_override")
name = sys.argv[2]
sys.argv[:] = ["revenue_forecast.py", name + ".json", "--validate-only"]
if name == "valid":
    rf.prepare_forecast = crash
else:
    rf_cli_feedback._observe = broken_projection
raise SystemExit(rf.main())"""
    for name, expected in (("valid", 1), ("invalid", 2)):
        result = subprocess.run([sys.executable, "-B", "-c", body, str(SCRIPTS), name], env=config, cwd=tmp_path,
                                capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == expected
        assert "optional_diagnostic_override" not in result.stderr
        if name == "valid":
            assert "BrokenReport" in result.stderr
    row, = observations(tmp_path / "box")
    detail = json.loads(invoke(tmp_path, config, "rf_job_feedback", "get-failure", row["details_ref"].split("/")[-1]).stdout)
    assert detail["cause_chain"][0]["type"] == "BrokenReport" and detail["code_version"]
    assert detail["side_effect_state"] == "unknown"


@pytest.fixture
def long_windows_dir(tmp_path):
    import shutil
    top = tmp_path / ("statepart" * 8)
    assert top.parent == tmp_path
    try:
        yield top / ("longpath" * 8) / ("longpath" * 8)
    finally:
        native = native_path(top)
        if native.is_dir():
            shutil.rmtree(native)


@pytest.mark.windows_only
@pytest.mark.skipif(os.name != "nt", reason="Win32 extended-length paths")
def test_long_windows_outbox_publishes_complete_ready_and_cold_reopens(tmp_path, long_windows_dir):
    baseline = long_windows_dir
    config = env(tmp_path)
    config["RESEARCH_FEEDBACK_DIR"] = str(baseline)
    config["RESEARCH_FEEDBACK_OUT"] = ""
    result = invoke(tmp_path, config, "rf_job_cli", "--owner-root", tmp_path, "submit", data="{")
    assert result.returncode == 2
    extended = native_path(baseline)
    row, = observations(extended)
    assert row["reason"] == "request_invalid"
    cold = invoke(tmp_path, config, "rf_job_feedback", "get-failure", row["evidence_ref"].split("/")[-1])
    assert cold.returncode == 0 and json.loads(cold.stdout)["exit_code"] == 2


@pytest.mark.windows_only
@pytest.mark.skipif(os.name != "nt", reason="Win32 extended-length paths")
def test_long_state_keeps_original_pending_even_if_explicit_destination_is_unwritable(tmp_path, long_windows_dir):
    root = long_windows_dir
    broken = tmp_path / "legacy"
    broken.write_text("blocked")
    config = env(tmp_path)
    config.update(LOCALAPPDATA=str(root), XDG_STATE_HOME=str(root), RESEARCH_FEEDBACK_OUT=str(broken / "result.jsonl"))
    result = invoke(tmp_path, config, "rf_job_cli", "--owner-root", tmp_path, "submit", data="{")
    assert result.returncode == 2
    db = native_path(root / "revenue-forecast" / "feedback.sqlite3")
    assert db.is_file()
    broken.unlink()
    broken.mkdir()
    recovered = invoke(tmp_path, config, "rf_job_feedback", "flush-feedback")
    assert recovered.returncode == 0
    row, = [json.loads(line) for line in (broken / "result.jsonl").read_bytes().splitlines()]
    details = invoke(tmp_path, config, "rf_job_feedback", "get-failure", row["details_ref"].split("/")[-1])
    assert details.returncode == 0 and json.loads(details.stdout)["native_code"] == "request_invalid"


@pytest.mark.parametrize(("producer_exit", "reason"), [
    (7, "filing_fetch_invalid_error_document"),
    (0, "filing_fetch_invalid_response_json"),
])
@pytest.mark.parametrize("invalid_pipe", (None, "stdout", "stderr"))
def test_filing_transport_failure_keeps_one_safe_wire_and_cold_f4_record(tmp_path, producer_exit, reason, invalid_pipe):
    calls = tmp_path / "calls"
    fixture_root = tmp_path / "ff"
    scripts = fixture_root / "scripts"
    scripts.mkdir(parents=True)
    fixture = scripts / "fetch_filing.py"
    sentinels = ("synthetic-bearer-not-for-output", "synthetic-unmarked-not-for-output")
    fixture.write_text(
        "import pathlib, sys\n"
        "with pathlib.Path(" + repr(str(calls)) + ").open('a') as sink: sink.write('called\\n')\n"
        "print('{not-json')\n"
        "print(" + repr("ImportError: Authorization: Bearer " + sentinels[0]) + ", file=sys.stderr)\n"
        "print(" + repr(sentinels[1]) + ", file=sys.stderr)\n"
        + (f"sys.{invalid_pipe}.buffer.write(bytes([255]))\n" if invalid_pipe else "")
        + "raise SystemExit(" + repr(producer_exit) + ")\n",
        encoding="utf-8",
    )
    config = env(tmp_path)
    request = json.dumps({"company": "Acme", "document_kind": "annual_report", "fiscal_year": 2025})
    direct = invoke(tmp_path, config, "filing_fetch_client", "--filing-fetch-root", fixture_root, data=request)
    assert direct.returncode == 2 and not direct.stdout
    wire_lines = len(direct.stderr.splitlines())
    assert wire_lines == 1
    error = json.loads(direct.stderr)
    assert error["producer_exit_code"] == producer_exit
    assert error["source_failure_reason"] == reason

    catalog_config = tmp_path / "catalog.json"
    catalog_config.write_text("{}", encoding="utf-8")
    prepared = invoke(tmp_path, config, "source_preparation", "--filing-fetch-root", fixture_root,
                      "--company-wiki-catalog-config", catalog_config, data=request)
    assert prepared.returncode == 3 and not prepared.stdout
    assert json.loads(prepared.stderr)["producer_exit_code"] == producer_exit
    assert calls.read_text(encoding="utf-8").splitlines() == ["called", "called"]

    row, = observations(tmp_path / "box")
    assert row["reason"] == reason and row["actual"] == "exit:3"
    evidence = row["details_ref"].split("/")[-1]
    first = invoke(tmp_path, config, "rf_job_feedback", "get-failure", evidence)
    second = invoke(tmp_path, config, "rf_job_feedback", "get-failure", evidence)
    assert first.returncode == second.returncode == 0 and first.stdout == second.stdout
    detail = json.loads(first.stdout)
    assert detail["producer_exit_code"] == producer_exit
    assert detail["native_code"] == reason and detail["side_effect_state"] == "unknown"
    assert reconcile_observation(tmp_path, config, row)["result"]["cost_state"] == "unknown"
    assert calls.read_text(encoding="utf-8").splitlines() == ["called", "called"]
    persisted = b''.join(path.read_bytes() for path in (tmp_path / 'box').iterdir() if path.is_file())
    captured = (direct.stderr + prepared.stderr + first.stdout).encode('utf-8')
    assert not any(secret.encode('utf-8') in captured + persisted for secret in sentinels)


@pytest.mark.parametrize("log_available", (True, False))
def test_filing_transport_retains_redacted_child_trace_tail_without_changing_wire(tmp_path, log_available):
    fixture_root = tmp_path / "ff"
    scripts = fixture_root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "fetch_filing.py").write_text(
        "import sqlite3, sys\n"
        "class FilingFetchError(Exception): pass\n"
        "sys.stderr.write('x' * 14000 + '\\n')\n"
        "try:\n"
        "    raise FileNotFoundError(2, 'fixture-unmarked-value')\n"
        "except FileNotFoundError as exc:\n"
        "    try:\n"
        "        raise PermissionError(13, 'Authorization: Bearer fixture-bearer-value') from exc\n"
        "    except PermissionError as permission:\n"
        "        try:\n"
        "            raise FilingFetchError('fixture-unmarked-value') from permission\n"
        "        except FilingFetchError as filing:\n"
        "            raise sqlite3.OperationalError('fixture-bearer-value') from filing\n",
        encoding="utf-8",
    )
    config = env(tmp_path)
    config["RESEARCH_FEEDBACK_RUN_ID"] = "actual-trace-fixture"
    log = tmp_path / "state" / "revenue-forecast" / "logs" / "runtime-errors.jsonl"
    if not log_available:
        log.parent.parent.mkdir(parents=True)
        log.parent.write_text("blocked", encoding="utf-8")
    request = json.dumps({"company": "Acme", "document_kind": "annual_report", "fiscal_year": 2025})
    result = invoke(tmp_path, config, "filing_fetch_client", "--filing-fetch-root", fixture_root, data=request)
    assert result.returncode == 2 and not result.stdout
    assert json.loads(result.stderr) == {
        "error_code": "fatal",
        "error": "filing-fetch exited 1: invalid upstream error document",
        "retryable": False,
        "source_failure_reason": "filing_fetch_invalid_error_document",
        "producer_exit_code": 1,
    }

    if not log_available:
        assert log.parent.read_text(encoding="utf-8") == "blocked"
        return
    record, = (json.loads(line) for line in log.read_bytes().splitlines())
    assert record["run_id"] == "actual-trace-fixture"
    assert record["operation"] == "filing_fetch"
    assert record["child_errors"] == [
        {"type": "FileNotFoundError", "errno": 2},
        {"type": "PermissionError", "errno": 13},
        {"type": "FilingFetchError"},
        {"type": "sqlite3.OperationalError"},
    ]
    assert record["producer_exit_code"] == 1
    assert b"fixture-unmarked-value" not in log.read_bytes()
    assert b"fixture-bearer-value" not in log.read_bytes()
