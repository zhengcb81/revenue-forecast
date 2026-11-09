"""Controlled recorder-shaped author fixtures, never real research evidence."""

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import report_catalog_research_attempt as admission  # noqa:E402
from report_catalog import CatalogError, ReportCatalog  # noqa:E402

ENT = "ENT_1b2a4d3e-0000-4a1b-8c2d-000000000001"
LISTING = "LST_2c3b5e4f-0000-4b2c-9d3e-000000000001"
CAP = "a" * 32
RECORDER_SHA = "c" * 64


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def fixture_run(root):
    run = root / "delivery" / "controlled-research"
    run.mkdir(parents=True)
    past = datetime.now(timezone.utc) - timedelta(hours=1)

    def stamp(seconds):
        return (past + timedelta(seconds=seconds)).isoformat()

    metadata = {
        "schema_version": "1.0",
        "run_id": run.name,
        "company_query": "药明康德",
        "as_of_date": "2026-11-01",
        "created_at": stamp(0),
        "usage": None,
        "cost": None,
    }
    write(run / "run.json", metadata)
    limits = {
        "company_attempts": 1,
        "new_source_downloads": 0,
        "external_paid_model_calls": 0,
        "web_search_requests": 4,
        "official_body_reads": 8,
        "native_call_timeout_seconds": 90,
        "native_total_timeout_seconds": 600,
    }
    scope = {
        "schema_version": "b34-research-attempt-scope/1",
        "run_id": run.name,
        "attempt_id": "attempt01",
        "company_query": "药明康德",
        "as_of_date": "2026-11-01",
        "root": run.as_posix(),
        "RF_code_root": ROOT.as_posix(),
        "RF_code_commit": "1" * 40,
        "limits": limits,
    }
    write(run / "execution/scope.json", scope)
    ledger = {
        "schema_version": "b34-research-step-ledger/1",
        "run_id": run.name,
        "state": "FAILED",
        "current_stage": "source_preparation",
        "terminal_research_failure": True,
        "steps": [
            {
                "step": "2 history_and_base",
                "state": "FAILED",
                "native_failure_refs": [CAP],
            }
        ],
    }
    write(run / "execution/step-ledger.json", ledger)
    budget = {
        "schema_version": "b34-research-budget/1",
        "state": "FAILED_SOURCE_PREPARATION",
        "native_capture_elapsed_seconds": 1,
        "native_total_budget_seconds": 600,
        "per_capture_budget_seconds": 90,
        "recorded_captures": [
            {
                "capture_id": CAP,
                "child_started": True,
                "child_exit": 3,
                "elapsed_seconds": 1,
                "timed_out": False,
                "input_complete": True,
                "output_complete": True,
            }
        ],
        "web_search_requests_used": 0,
        "official_body_open_requests_used": 0,
        "paid_external_model_calls": 0,
        "new_source_downloads": 0,
        "harness_LLM_usage": None,
        "harness_LLM_cost": None,
    }
    write(run / "execution/budget-observation.json", budget)
    request = {
        "schema_version": "2.0",
        "company_query": "药明康德",
        "market": "CN",
        "document_kind": "annual_report",
        "mode": "exact",
        "fiscal_year": 2025,
        "as_of_date": "2026-11-01",
        "filing_intent": "reuse_only",
    }
    original = run / "execution/requests/annual.json"
    write(original, request)
    command = [
        sys.executable,
        "-B",
        str(ROOT / "scripts/source_preparation.py"),
        "--request-file",
        str(original),
        "--result-envelope",
        "--company-wiki-config",
        str(root / "operator" / "ff.json"),
        "--company-wiki-catalog-config",
        str(root / "operator" / "cwp.json"),
        "--source-reader-receipt-version",
        "2.2",
        "--timeout-seconds",
        "90",
    ]
    folder = run / "roles/executor/commands" / CAP
    frozen = folder / "input-0001.json"
    write(frozen, request)
    raw = frozen.read_bytes()
    consumed = folder / "consume-0001.json"
    row = {
        "original_path": str(original),
        "frozen_path": str(frozen),
        "consumed_path": str(consumed),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
        "argument_indices": [4],
        "observed_at": stamp(1),
        "consumed_unchanged": True,
        "consumed_after_bytes": len(raw),
        "consumed_after_sha256": hashlib.sha256(raw).hexdigest(),
    }
    executed = list(command)
    executed[4] = str(consumed)
    observation = {
        "capture_tool_sha256": RECORDER_SHA,
        "observed_at": stamp(1),
        "python_version": sys.version,
        "platform": "Windows",
    }
    shared = {
        "capture_id": CAP,
        "command": command,
        "executed_command": executed,
        "started_at": stamp(1),
        "input_snapshots": [row],
        "runtime_observation": observation,
        "timeout_seconds": 90,
        "max_log_bytes": 1048576,
        "max_input_bytes": 4194304,
    }
    started = {
        "schema_version": "1.0",
        "event_id": "start-event",
        "run_id": run.name,
        "role": "executor",
        "kind": "command_started",
        "recorded_at": stamp(1),
        "data": shared,
    }
    finish = {
        **shared,
        "finished_at": stamp(2),
        "exit_code": 3,
        "timed_out": False,
        "child_started": True,
        "input_complete": True,
        "input_cleanup_complete": True,
        "input_cleanup_failures": 0,
        "execution_error": None,
        "output_complete": True,
        "warnings": [],
    }
    for stream, body in [
        ("stdout", b""),
        (
            "stderr",
            b'{"error_code":"upstream","stage":"source_reader","calls":2,"downloads":0}\n',
        ),
    ]:
        file = folder / (stream + ".txt")
        file.write_bytes(body)
        finish.update(
            {
                stream + "_artifact": str(file),
                stream + "_total_bytes": len(body),
                stream + "_retained_bytes": len(body),
                stream + "_truncated": False,
            }
        )
    ended = {
        "schema_version": "1.0",
        "event_id": "end-event",
        "run_id": run.name,
        "role": "executor",
        "kind": "command_finished",
        "recorded_at": stamp(2),
        "data": finish,
    }
    events = run / "roles/executor/events.jsonl"
    events.write_text(
        json.dumps(started, ensure_ascii=False)
        + "\n"
        + json.dumps(ended, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    terminal = {
        "schema_version": "rf-research-terminal/1",
        "run_id": run.name,
        "attempt_id": "attempt01",
        "status": "failed",
        "terminal_stage": "source_preparation",
        "terminal_capture_id": CAP,
        "reason_code": "upstream",
        "closed_at": stamp(3),
        "research_manifest_sha256": hashlib.sha256(
            (run / "execution/step-ledger.json").read_bytes()
        ).hexdigest(),
        "code_refs": {"RF": "1" * 40},
        "source_budget": limits,
    }
    write(run / "execution/terminal.json", terminal)
    return run


def identity(entity):
    return {
        "authority": "stockwiki",
        "entity_id": entity,
        "resolution_status": "resolved",
        "display_name": "药明康德",
        "source_revision": "rev1",
        "lookup_receipt_sha256": "b" * 64,
    }


def admit(root, run, **extra):
    return admission.import_research_attempt(
        ReportCatalog(root=root),
        run_id=run.name,
        entity_id=ENT,
        listing_id=LISTING,
        identity_resolver=identity,
        recorder_sha256=extra.pop("recorder_sha256", RECORDER_SHA),
        **extra,
    )


def mutate(run, relative, callback):
    file = run / relative
    value = json.loads(file.read_text(encoding="utf-8"))
    callback(value)
    write(file, value)


def test_terminal_failure_admission_and_exact_replay(tmp_path):
    run = fixture_run(tmp_path)
    first = admit(tmp_path, run)
    catalog = ReportCatalog(root=tmp_path)
    before = catalog.file.read_bytes()
    assert admit(tmp_path, run) == first
    assert catalog.file.read_bytes() == before
    attempt = catalog.get_attempt(run.name, "attempt01")["attempt"]
    assert attempt["status"] == "failed" and attempt["report_ids"] == []
    assert catalog.list_reports(ENT)["items"] == []
    assert first["scope"] == "failed_research_attempt_only_not_report_publication"
    seal = list((catalog.file.parent / "evidence").iterdir())
    assert len(seal) == 1
    assert json.loads(seal[0].read_text(encoding="utf-8"))["native_usage"] == {
        "scope": "selected_source_preparation_invocation",
        "calls": 2,
        "downloads": 0,
    }
    assert str(tmp_path) not in seal[0].read_text(encoding="utf-8")
    assert tmp_path.as_posix() not in seal[0].read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "which",
    [
        "ledger_running",
        "budget_running",
        "no_terminal",
        "not_failed",
        "calculator",
        "wrong_capture",
        "changed_manifest",
        "wrong_company",
        "wrong_asof",
        "diagnostic_exit",
        "config_diagnostic",
        "unfrozen_input",
        "truncated_log",
        "stdout_path",
        "changed_code_refs",
        "budget_exceeded",
    ],
)
def test_bad_terminal_context_refused_without_catalog(tmp_path, which):
    run = fixture_run(tmp_path)
    if which == "ledger_running":
        mutate(run, "execution/step-ledger.json", lambda d: d.update(state="RUNNING"))
    elif which == "budget_running":
        mutate(
            run,
            "execution/budget-observation.json",
            lambda d: d.update(state="RUNNING"),
        )
    elif which == "no_terminal":
        (run / "execution/terminal.json").unlink()
    elif which == "not_failed":
        mutate(run, "execution/terminal.json", lambda d: d.update(status="running"))
    elif which == "calculator":
        mutate(
            run, "execution/terminal.json", lambda d: d.update(terminal_stage="compute")
        )
    elif which == "wrong_capture":
        mutate(
            run,
            "execution/terminal.json",
            lambda d: d.update(terminal_capture_id="f" * 32),
        )
    elif which == "changed_manifest":
        mutate(
            run,
            "execution/terminal.json",
            lambda d: d.update(research_manifest_sha256="0" * 64),
        )
    elif which == "wrong_company":
        mutate(run, "run.json", lambda d: d.update(company_query="Other"))
    elif which == "wrong_asof":
        mutate(run, "execution/scope.json", lambda d: d.update(as_of_date="2026-10-21"))
    elif which == "changed_code_refs":
        mutate(
            run,
            "execution/terminal.json",
            lambda d: d.update(code_refs={"RF": "f" * 40}),
        )
    elif which == "budget_exceeded":
        mutate(
            run,
            "execution/budget-observation.json",
            lambda d: d.update(new_source_downloads=1),
        )
    else:
        file = run / "roles/executor/events.jsonl"
        events = [json.loads(x) for x in file.read_text(encoding="utf-8").splitlines()]
        data = events[1]["data"]
        if which == "diagnostic_exit":
            data["exit_code"] = 2
        elif which == "unfrozen_input":
            data["input_snapshots"][0]["sha256"] = "0" * 64
        elif which == "truncated_log":
            data["stderr_truncated"] = True
        elif which == "stdout_path":
            data["stdout_artifact"] = str(tmp_path / "foreign.txt")
        elif which == "config_diagnostic":
            path = Path(data["stderr_artifact"])
            raw = b'{"error_code":"upstream","error":"status=config_error"}'
            path.write_bytes(raw)
            data["stderr_total_bytes"] = data["stderr_retained_bytes"] = len(raw)
        file.write_text(
            "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in events),
            encoding="utf-8",
        )
    with pytest.raises(CatalogError):
        admit(tmp_path, run)
    assert not (tmp_path / "artifacts").exists()


def test_consistent_same_id_different_payload_conflicts(tmp_path):
    run = fixture_run(tmp_path)
    admit(tmp_path, run)
    catalog = ReportCatalog(root=tmp_path)
    before = catalog.file.read_bytes()
    mutate(
        run,
        "execution/terminal.json",
        lambda d: d.update(
            closed_at=(
                datetime.fromisoformat(d["closed_at"]) + timedelta(seconds=1)
            ).isoformat()
        ),
    )
    with pytest.raises(CatalogError, match="different admission evidence"):
        admit(tmp_path, run)
    assert catalog.file.read_bytes() == before


def test_subject_scope_cannot_be_self_assigned(tmp_path):
    run = fixture_run(tmp_path)
    admit(tmp_path, run)
    with pytest.raises(CatalogError):
        admit(tmp_path, run, analysis_subject_id="invented-subject")


def test_budget_cannot_lie_about_capture_elapsed(tmp_path):
    run = fixture_run(tmp_path)
    mutate(
        run,
        "execution/budget-observation.json",
        lambda d: d.update(native_capture_elapsed_seconds=0),
    )
    with pytest.raises(CatalogError):
        admit(tmp_path, run)
    assert not (tmp_path / "artifacts").exists()


def native_events(run):
    return [
        json.loads(line)
        for line in (run / "roles/executor/events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]


def save_events(run, values):
    (run / "roles/executor/events.jsonl").write_text(
        "".join(json.dumps(value, ensure_ascii=False) + "\n" for value in values),
        encoding="utf-8",
    )


def sync_budget(run):
    values = [
        event["data"]
        for event in native_events(run)
        if event["kind"] == "command_finished"
    ]
    rows = []
    for data in values:
        seconds = (
            datetime.fromisoformat(data["finished_at"])
            - datetime.fromisoformat(data["started_at"])
        ).total_seconds()
        rows.append(
            {
                "capture_id": data["capture_id"],
                "child_started": data["child_started"],
                "child_exit": data["exit_code"],
                "elapsed_seconds": seconds,
                "timed_out": data["timed_out"],
                "input_complete": data["input_complete"],
                "output_complete": data["output_complete"],
            }
        )
    mutate(
        run,
        "execution/budget-observation.json",
        lambda data: data.update(
            recorded_captures=rows,
            native_capture_elapsed_seconds=sum(row["elapsed_seconds"] for row in rows),
        ),
    )


def test_recorded_producer_must_match_trusted_pin(tmp_path):
    run = fixture_run(tmp_path)
    with pytest.raises(CatalogError, match="trusted recorder producer"):
        admit(tmp_path, run, recorder_sha256="d" * 64)
    assert not (tmp_path / "artifacts").exists()


def test_wrong_producer_pair_or_frame_is_refused(tmp_path):
    run = fixture_run(tmp_path)
    events = native_events(run)
    events[1]["data"]["runtime_observation"]["capture_tool_sha256"] = "d" * 64
    save_events(run, events)
    with pytest.raises(CatalogError, match="trusted recorder producer"):
        admit(tmp_path, run)


def test_unfinished_native_command_is_not_terminal(tmp_path):
    run = fixture_run(tmp_path)
    events = native_events(run)
    pending = json.loads(json.dumps(events[0]))
    pending.update(event_id="pending-start")
    pending["data"]["capture_id"] = "f" * 32
    save_events(run, events + [pending])
    with pytest.raises(CatalogError, match="unfinished native command"):
        admit(tmp_path, run)


def test_files_changed_during_identity_lookup_are_not_admitted(tmp_path):
    run = fixture_run(tmp_path)

    def changed(entity):
        mutate(
            run, "execution/step-ledger.json", lambda data: data.update(state="RUNNING")
        )
        return identity(entity)

    with pytest.raises(CatalogError, match="changed"):
        admission.import_research_attempt(
            ReportCatalog(root=tmp_path),
            run_id=run.name,
            entity_id=ENT,
            listing_id=LISTING,
            identity_resolver=changed,
            recorder_sha256=RECORDER_SHA,
        )
    assert not (tmp_path / "artifacts").exists()


def test_changed_identity_before_append_refused(tmp_path):
    run = fixture_run(tmp_path)
    calls = []

    def changed(entity):
        result = identity(entity)
        calls.append(entity)
        if len(calls) > 1:
            result["source_revision"] = "rev2"
        return result

    with pytest.raises(CatalogError, match="identity changed"):
        admission.import_research_attempt(
            ReportCatalog(root=tmp_path),
            run_id=run.name,
            entity_id=ENT,
            listing_id=LISTING,
            identity_resolver=changed,
            recorder_sha256=RECORDER_SHA,
        )
    assert not list((tmp_path / "artifacts/report_catalog").glob("*.jsonl"))


def test_completed_capture_cannot_be_relabelled_failure(tmp_path):
    run = fixture_run(tmp_path)
    events = native_events(run)
    events[1]["data"]["exit_code"] = 0
    save_events(run, events)
    sync_budget(run)
    with pytest.raises(CatalogError, match="real native research-stage failure"):
        admit(tmp_path, run)


def test_diagnostic_cannot_fake_the_whitelisted_script(tmp_path):
    run = fixture_run(tmp_path)
    events = native_events(run)
    for event in events:
        event["data"]["command"][2] = str(ROOT / "scripts/revenue_forecast.py")
        event["data"]["executed_command"][2] = str(ROOT / "scripts/revenue_forecast.py")
    save_events(run, events)
    with pytest.raises(CatalogError, match="fixed RF source-preparation stage"):
        admit(tmp_path, run)


def test_old_failure_after_same_request_success_refused(tmp_path):
    run = fixture_run(tmp_path)
    events = native_events(run)
    later = json.loads(json.dumps(events))
    old_folder = run / "roles/executor/commands" / CAP
    new_id = "e" * 32
    new_folder = old_folder.with_name(new_id)
    new_folder.mkdir()
    for file in old_folder.iterdir():
        (new_folder / file.name).write_bytes(file.read_bytes())
    for index, event in enumerate(later):
        event["event_id"] = "later-" + str(index)
        data = event["data"]
        data["capture_id"] = new_id
        data["started_at"] = (
            datetime.fromisoformat(data["started_at"]) + timedelta(seconds=3)
        ).isoformat()
        event["recorded_at"] = (
            datetime.fromisoformat(event["recorded_at"]) + timedelta(seconds=3)
        ).isoformat()
        for row in data["input_snapshots"]:
            row["frozen_path"] = str(new_folder / Path(row["frozen_path"]).name)
            row["consumed_path"] = str(new_folder / Path(row["consumed_path"]).name)
        data["executed_command"][4] = data["input_snapshots"][0]["consumed_path"]
        if index == 1:
            data["exit_code"] = 0
            data["finished_at"] = (
                datetime.fromisoformat(data["finished_at"]) + timedelta(seconds=3)
            ).isoformat()
            for stream in ("stdout", "stderr"):
                data[stream + "_artifact"] = str(new_folder / (stream + ".txt"))
    save_events(run, events + later)
    sync_budget(run)
    mutate(
        run,
        "execution/terminal.json",
        lambda data: data.update(
            closed_at=(
                datetime.fromisoformat(data["closed_at"]) + timedelta(seconds=6)
            ).isoformat()
        ),
    )
    with pytest.raises(CatalogError, match="superseded by a later same-request"):
        admit(tmp_path, run)


def test_existing_catalog_prefix_is_preserved(tmp_path):
    run = fixture_run(tmp_path)
    catalog = ReportCatalog(root=tmp_path)
    old = {
        "run_id": "old-success",
        "company": {
            "entity_id": ENT,
            "listing_id": LISTING,
            "analysis_subject_id": None,
            "resolution_status": "resolved",
            "display_name": "药明康德",
        },
        "source_as_of": "2026-10-21",
        "created_at": "2026-10-22T00:00:00Z",
        "status": "succeeded",
    }
    catalog.add_records(runs=[old])
    before = catalog.file.read_bytes()
    admit(tmp_path, run)
    assert catalog.file.read_bytes().startswith(before)
    assert catalog.get_run("old-success")["run"]["status"] == "succeeded"


def test_cli_requires_owner_root_before_config_lookup(tmp_path, monkeypatch, capsys):
    import report_catalog_identity_cli as cli

    monkeypatch.setattr(
        cli,
        "load_bridge_config",
        lambda *args: pytest.fail("configuration lookup must not run"),
    )
    assert (
        cli.main(
            [
                "import-research-attempt",
                "--entity-id",
                ENT,
                "--run-id",
                "run-a",
                "--recorder-sha256",
                RECORDER_SHA,
            ]
        )
        == 2
    )
    assert json.loads(capsys.readouterr().err)["error_code"] == "owner_root_required"


def test_management_lock_released_after_actual_child_kill(tmp_path):
    import subprocess

    root = tmp_path.resolve()
    lock = root / "admission.lock"
    script = "import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import report_catalog_research_attempt as a;fd=a._admission_lock(Path(sys.argv[2]),Path(sys.argv[3]));print('LOCKED',flush=True);sys.stdin.readline()"
    child = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-B",
            "-c",
            script,
            str(ROOT / "scripts"),
            str(root),
            str(lock),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert child.stdout.readline().strip() == "LOCKED"
        with pytest.raises(CatalogError, match="another research admission"):
            admission._admission_lock(root, lock)
        child.kill()
        child.wait(timeout=10)
        fd = admission._admission_lock(root, lock)
        admission._admission_unlock(fd)
        assert lock.is_file() and lock.stat().st_size == 0
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=10)
        for handle in (child.stdin, child.stdout, child.stderr):
            handle.close()


def test_partial_seal_publish_never_claims_final_name(tmp_path, monkeypatch):
    body = b'{"complete":"sealed facts"}\n'
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    seal = evidence / "seal.json"
    original = admission.os.link

    def unavailable(*args):
        raise OSError("controlled publication failure")

    monkeypatch.setattr(admission.os, "link", unavailable)
    with pytest.raises(CatalogError, match="cannot be published"):
        admission._publish_seal(tmp_path, seal, body)
    assert not seal.exists() and list(evidence.iterdir()) == []
    monkeypatch.setattr(admission.os, "link", original)
    admission._publish_seal(tmp_path, seal, body)
    assert seal.read_bytes() == body
    with pytest.raises(CatalogError, match="sealed admission bytes disagree"):
        admission._publish_seal(tmp_path, seal, b'{"different":true}')
    assert seal.read_bytes() == body


@pytest.mark.parametrize("raw", [b'{"x":"\\ud800"}', b'{"x":1e999}', b'{"x":1,"x":2}'])
def test_strict_evidence_json_rejects_unserializable_or_ambiguous_values(raw):
    with pytest.raises(CatalogError):
        admission._json(raw)


def test_sealed_facts_refuse_hidden_physical_usage_values(tmp_path):
    run = fixture_run(tmp_path)
    mutate(
        run,
        "execution/budget-observation.json",
        lambda data: data.update(
            harness_LLM_usage={"note": str(tmp_path / "private" / "usage")}
        ),
    )
    with pytest.raises(CatalogError):
        admit(tmp_path, run)
    assert not (tmp_path / "artifacts").exists()


def test_invalid_filing_request_shape_is_not_a_research_gate(tmp_path):
    run = fixture_run(tmp_path)
    events = native_events(run)
    row = events[1]["data"]["input_snapshots"][0]
    frozen = Path(row["frozen_path"])
    request = json.loads(frozen.read_text(encoding="utf-8"))
    request["document_kind"] = "not-a-filing"
    request.pop("fiscal_year")
    write(frozen, request)
    write(Path(row["original_path"]), request)
    raw = frozen.read_bytes()
    for event in events:
        observation = event["data"]["input_snapshots"][0]
        observation.update(
            sha256=hashlib.sha256(raw).hexdigest(),
            byte_size=len(raw),
            consumed_after_bytes=len(raw),
            consumed_after_sha256=hashlib.sha256(raw).hexdigest(),
        )
    save_events(run, events)
    with pytest.raises(CatalogError, match="filing period"):
        admit(tmp_path, run)
    assert not (tmp_path / "artifacts").exists()


def test_timeout_flag_without_elapsed_native_timeout_is_rejected(tmp_path):
    run = fixture_run(tmp_path)
    events = native_events(run)
    events[1]["data"].update(exit_code=124, timed_out=True, output_complete=False)
    save_events(run, events)
    sync_budget(run)
    mutate(
        run,
        "execution/terminal.json",
        lambda data: data.update(reason_code="source_preparation_timeout"),
    )
    with pytest.raises(CatalogError, match="timeout clock"):
        admit(tmp_path, run)
    assert not (tmp_path / "artifacts").exists()


# Independent four RED cases remain frozen outside this author tree. These
# nearby producer-boundary cases exercise the same corrected admission rules.
def replace_error(run, envelope):
    events = native_events(run)
    data = events[-1]["data"]
    raw = (json.dumps(envelope) + "\n").encode("utf-8")
    Path(data["stderr_artifact"]).write_bytes(raw)
    data["stderr_total_bytes"] = data["stderr_retained_bytes"] = len(raw)
    save_events(run, events)


@pytest.mark.parametrize(
    "field,value",
    [
        ("calls", True),
        ("calls", -1),
        ("downloads", False),
        ("downloads", "0"),
        ("downloads", None),
    ],
)
def test_native_usage_counters_are_known_nonnegative_integers(tmp_path, field, value):
    run = fixture_run(tmp_path)
    envelope = {
        "error_code": "upstream",
        "stage": "source_reader",
        "calls": 2,
        "downloads": 0,
    }
    envelope[field] = value
    replace_error(run, envelope)
    with pytest.raises(CatalogError, match="native stage usage"):
        admit(tmp_path, run)
    assert not (tmp_path / "artifacts").exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("new_source_downloads", 0.5),
        ("web_search_requests_used", 0.5),
        ("paid_external_model_calls", False),
    ],
)
def test_research_operation_counts_are_not_fractional_or_boolean(
    tmp_path, field, value
):
    run = fixture_run(tmp_path)
    mutate(run, "execution/budget-observation.json", lambda v: v.update({field: value}))
    with pytest.raises(CatalogError, match="research budget observation"):
        admit(tmp_path, run)
    assert not (tmp_path / "artifacts").exists()


@pytest.mark.parametrize(
    "which",
    [
        "start_after_native_end",
        "finish_before_native_end",
        "producer_after_native_start",
    ],
)
def test_header_and_producer_clocks_bind_native_lifetime(tmp_path, which):
    run = fixture_run(tmp_path)
    events = native_events(run)
    if which == "start_after_native_end":
        events[0]["recorded_at"] = events[1]["data"]["finished_at"]
        events[0]["recorded_at"] = (
            datetime.fromisoformat(events[0]["recorded_at"]) + timedelta(microseconds=1)
        ).isoformat()
    elif which == "finish_before_native_end":
        events[1]["recorded_at"] = events[0]["data"]["started_at"]
    else:
        events[0]["data"]["runtime_observation"]["observed_at"] = events[1]["data"][
            "finished_at"
        ]
        events[1]["data"]["runtime_observation"]["observed_at"] = events[1]["data"][
            "finished_at"
        ]
    save_events(run, events)
    with pytest.raises(CatalogError):
        admit(tmp_path, run)
    assert not (tmp_path / "artifacts").exists()


def test_real_header_append_delay_and_existing_ff_root_flag_are_supported(tmp_path):
    run = fixture_run(tmp_path)
    events = native_events(run)
    for event in events:
        event["recorded_at"] = (
            datetime.fromisoformat(event["recorded_at"]) + timedelta(milliseconds=2)
        ).isoformat()
        event["data"]["command"] += [
            "--filing-fetch-root",
            str(tmp_path / "trusted-ff-code"),
        ]
        event["data"]["executed_command"] += [
            "--filing-fetch-root",
            str(tmp_path / "trusted-ff-code"),
        ]
    save_events(run, events)
    assert admit(tmp_path, run)["registered"]["reports"] == []


def test_unhashable_stage_refuses_as_catalog_error(tmp_path):
    run = fixture_run(tmp_path)
    replace_error(
        run, {"error_code": "upstream", "stage": {}, "calls": 2, "downloads": 0}
    )
    with pytest.raises(CatalogError, match="structured research-stage"):
        admit(tmp_path, run)


@pytest.mark.parametrize(
    "mutation", [None, "downloads", "calls", "period", "invalid_schema"]
)
def test_complete_native_filing_failure_usage_and_period_match_request(
    tmp_path, mutation
):
    run = fixture_run(tmp_path)
    nested = {
        "schema_version": "2.0",
        "status": "not_found",
        "request_period": {
            "mode": "exact",
            "fiscal_year": 2025,
            "fiscal_period": None,
            "as_of_date": "2026-11-01",
        },
        "filing": {
            "status": "not_found",
            "reason": "no local filing",
            "retryable": False,
        },
        "transcript": {"status": "not_requested", "retryable": False},
        "calls": 2,
        "downloads": 0,
    }
    if mutation in {"calls", "downloads"}:
        nested[mutation] += 1
    elif mutation == "period":
        nested["request_period"]["fiscal_year"] = 2024
    elif mutation == "invalid_schema":
        nested["schema_version"] = "unknown"
    replace_error(
        run,
        {
            "error_code": "upstream",
            "stage": "not_found",
            "calls": 2,
            "downloads": 0,
            "filing_fetch_result": nested,
        },
    )
    if mutation is None:
        assert admit(tmp_path, run)["registered"]["reports"] == []
    else:
        with pytest.raises(CatalogError, match="native stage usage disagrees"):
            admit(tmp_path, run)
        assert not (tmp_path / "artifacts").exists()
