"""RF's native S6 diagnostics checks. All inputs and state are isolated."""

from __future__ import annotations

from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
from uuid import NAMESPACE_URL, uuid5

import pytest

from test_rf_job_facade_cli import _deployment, _request


ROOT = Path(__file__).resolve().parents[1]
ENTRIES = (
    "scripts/revenue_forecast.py", "scripts/revenue_backtest.py",
    "scripts/research_projection.py", "scripts/research_support_diagnostics.py",
    "scripts/generate_input_template.py", "scripts/lint_input.py", "scripts/fix_hashes.py",
    "scripts/source_preparation.py", "scripts/narrative_source_preparation.py",
    "scripts/financial_statement_source.py", "scripts/filing_fetch_client.py",
    "scripts/report_catalog_cli.py", "scripts/report_catalog_compare_cli.py",
    "scripts/report_catalog_identity_cli.py", "scripts/report_catalog_identity_resolver.py",
    "scripts/report_catalog_verified_compare_cli.py", "scripts/publication_registry.py",
    "scripts/rf_job_cli.py", "scripts/rf_job_feedback.py",
    "tools/daily_t2_schedule.py", "tools/daily_t2_runner.py",
    "tools/weekly_t3_schedule.py", "tools/weekly_t3_runner.py",
    "tools/monthly_broker_schedule.py", "tools/release_readiness.py",
    "tools/release_gate.py", "tools/slo_probe.py",
)
PRIVATE_VALUES = (
    "rf-fixture-original-header", "rf-fixture-folded-continuation",
    "rf-fixture-userinfo-password", "sk-RFS6FakeCredential123",
    "tvly-RFS6FakeCredential123", "ghp_RFS6FakeCredential123", "AIzaRFS6FakeCredential123",
)
PRIVATE = ("Authorization: Bearer " + PRIVATE_VALUES[0] + "\r\n\t" + PRIVATE_VALUES[1]
           + "\r\nnext-diagnostic https://user:" + PRIVATE_VALUES[2]
           + "@example.invalid " + " ".join(PRIVATE_VALUES[3:]))


@pytest.fixture
def isolation(tmp_path):
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "sitecustomize.py").write_text(
        "import sys\n"
        "def deny(event, args):\n"
        "    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.sendto'):\n"
        "        raise AssertionError('isolated S6 fixture forbids network')\n"
        "sys.addaudithook(deny)\n",
        encoding="utf-8",
    )
    env = {key: value for key, value in os.environ.items()
           if key.upper() in {"PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "COMSPEC", "LANG"}}
    env.update(
        HOME=str(profile), USERPROFILE=str(profile), LOCALAPPDATA=str(profile),
        XDG_STATE_HOME=str(profile), APPDATA=str(profile), TEMP=str(tmp_path), TMP=str(tmp_path),
        PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PYTHON_DOTENV_DISABLED="1", PYTHONPATH=str(profile),
        RESEARCH_FEEDBACK_OUT=str(tmp_path / "observations.jsonl"),
        RESEARCH_FEEDBACK_RUN_ID="rf-s6-startup", RESEARCH_FEEDBACK_ATTEMPT_ID="attempt-one",
    )
    return env, profile / "revenue-forecast"


def invoke(tmp_path, env, entry, *args, body=b""):
    return subprocess.run(
        [sys.executable, "-B", str(ROOT / entry), *map(str, args)], input=body,
        cwd=tmp_path, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=28, check=False, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def events(state) -> Iterable[dict]:
    for logfile in (state / "logs").glob("runtime-errors.jsonl*"):
        for line in logfile.read_text(encoding="utf-8").splitlines():
            value = json.loads(line)
            if isinstance(value, dict):
                yield value


def assert_no_credentials(*values):
    assert all(token.encode() not in value for value in values for token in PRIVATE_VALUES)


@pytest.mark.parametrize("entry", ENTRIES)
def test_original_entry_invalid_invocation_is_durable_and_pre_dispatch(tmp_path, isolation, entry):
    env, state = isolation
    result = invoke(tmp_path, env, entry, "--rf-s6-nonexistent", PRIVATE)
    assert result.returncode != 0
    name = Path(entry).stem
    matches = [row for row in events(state) if row.get("entrypoint") == name]
    assert matches and any(row.get("exit_code") == result.returncode for row in matches)
    assert all(row["run_id"] == "rf-s6-startup" and row["attempt_id"] == "attempt-one"
               and row["code_version"] == hashlib.sha256((ROOT / entry).read_bytes()).hexdigest()
               for row in matches)
    assert not (tmp_path / "dispatches").exists()
    assert_no_credentials(result.stderr, json.dumps(matches).encode())


def test_deep_compare_keeps_original_machine_refusal_and_true_cause(tmp_path, isolation):
    env, state = isolation
    (tmp_path / "artifacts" / "report_catalog").mkdir(parents=True)
    result = invoke(tmp_path, env, "scripts/report_catalog_compare_cli.py",
                    "--owner-root", tmp_path, "compare", body=PRIVATE.encode())
    assert result.returncode == 2 and result.stdout == b""
    payload = json.loads(result.stderr)
    assert payload["error"]["code"] == "invalid_json"
    row, = [row for row in events(state) if row.get("entrypoint") == "report_catalog_compare_cli"]
    assert row["input_ref"] == "sha256:" + hashlib.sha256(PRIVATE.encode()).hexdigest()
    traceback = row["cause_chain"]
    assert any(part["type"] == "JSONDecodeError" and part["frames"]
               and part["frames"][-1]["line"] for part in traceback)
    assert_no_credentials(result.stderr, json.dumps(row).encode())


def test_dual_io_failure_warns_human_and_preserves_machine_receipt(tmp_path, isolation):
    env, _ = isolation
    for name in ("LOCALAPPDATA", "XDG_STATE_HOME", "RESEARCH_FEEDBACK_OUT"):
        blocker = tmp_path / name
        blocker.write_bytes(b"unchanged")
        env[name] = str(blocker / "blocked")
    human = invoke(tmp_path, env, "scripts/revenue_forecast.py", "--rf-s6-invalid", PRIVATE)
    assert human.returncode == 2 and b"usage:" in human.stderr
    assert b"warning:" in human.stderr and b"rf_" in human.stderr
    (tmp_path / "artifacts" / "report_catalog").mkdir(parents=True)
    machine = invoke(tmp_path, env, "scripts/report_catalog_compare_cli.py",
                     "--owner-root", tmp_path, "compare", body=PRIVATE.encode())
    assert machine.returncode == 2 and machine.stdout == b""
    assert json.loads(machine.stderr)["error"]["code"] == "invalid_json"
    assert all((tmp_path / name).read_bytes() == b"unchanged"
               for name in ("LOCALAPPDATA", "XDG_STATE_HOME", "RESEARCH_FEEDBACK_OUT"))
    assert_no_credentials(human.stderr, machine.stderr)


def test_windows_archive_busy_preserves_old_and_current_bytes(tmp_path, isolation):
    env, state = isolation
    target = tmp_path / "blocked"
    target.write_bytes(b"unavailable destination")
    env["RESEARCH_FEEDBACK_OUT"] = str(target / "out")
    active = state / "logs" / "runtime-errors.jsonl"
    active.parent.mkdir(parents=True)
    newest, oldest = [active.with_name(active.name + suffix) for suffix in (".1", ".2")]
    current = (json.dumps({"row": "r" * (1024 * 1024)}) + "\n").encode()
    recent, oldest_data = b'{"history":1}\n', b'{"history":2}\n'
    active.write_bytes(current)
    newest.write_bytes(recent)
    oldest.write_bytes(oldest_data)
    with newest.open("rb") as held:
        result = invoke(tmp_path, env, "scripts/revenue_forecast.py", "--rf-s6-invalid")
        assert held.read() == recent
    assert result.returncode == 2
    if sys.platform == "win32":
        assert oldest.read_bytes() == oldest_data
        assert newest.read_bytes() == recent
        assert active.read_bytes().startswith(current)
    else:
        assert oldest.read_bytes() == recent
        assert newest.read_bytes() == current
    assert any(row.get("run_id") == "rf-s6-startup" for row in events(state))


def _canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


@pytest.mark.parametrize("single", [False, True], ids=["inbox", "sidecar"])
@pytest.mark.parametrize("phase", ["pending", "unacknowledged", "packet-only", "bad-transport"])
def test_legacy_outbox_flush_projects_only_new_deliveries(tmp_path, isolation, single, phase):
    env, state = isolation
    original = {
        "schema_version": "feedback-observation/1", "owner": "revenue-forecast",
        "run_id": "sk-valid-native-legacy-fixture", "attempt_id": "tvly-valid-native-legacy-fixture",
        "step_id": "rf_job_cli/legacy", "check_id": "process-outcome", "expected": "exit:0",
        "actual": "exit:2", "disposition": "deviation",
    }
    target = tmp_path / ("frozen.jsonl" if single else "frozen")
    body = _canonical({"row": original, "target": str(target), "single": single})
    key = uuid5(NAMESPACE_URL, body).hex
    state.mkdir()
    db = state / "feedback.sqlite3"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE pending(id TEXT PRIMARY KEY,body TEXT NOT NULL)")
        conn.execute("INSERT INTO pending VALUES(?,?)", (key, body))
    conn.close()
    legacy_packet = target if single else target / f"feedback-{key}.jsonl"
    payload = (_canonical(original) + "\n").encode("ascii")
    if phase in {"unacknowledged", "packet-only"} or (phase == "bad-transport" and not single):
        legacy_packet.parent.mkdir(parents=True, exist_ok=True)
        legacy_packet.write_bytes(payload.removesuffix(b"\n") if single and phase == "packet-only" else payload)
    if not single and phase == "unacknowledged":
        marker = {field: original[field] for field in ("owner", "run_id", "attempt_id", "step_id")}
        legacy_packet.with_suffix(".ready").write_bytes((_canonical(marker) + "\n").encode("ascii"))
    if phase == "bad-transport":
        invalid_leaf = target if single else legacy_packet.with_suffix(".ready")
        invalid_leaf.mkdir()

    def flush():
        result = invoke(tmp_path, env, "scripts/rf_job_feedback.py", "flush-feedback")
        assert (result.returncode, result.stderr) == (0, b"")
        return json.loads(result.stdout)

    first = flush()
    shadow = Path(env["RESEARCH_FEEDBACK_OUT"])
    assert not shadow.exists()
    if phase == "bad-transport":
        assert first == flush() == {"found": 1, "remaining": 1}
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT id,body FROM pending").fetchall() == [(key, body)]
        conn.close()
        if not single:
            assert legacy_packet.read_bytes() == payload
            assert list(target.glob("feedback-*.jsonl")) == [legacy_packet]
        return

    assert first == {"found": 1, "remaining": 0}
    packets = [target] if single else sorted(target.glob("feedback-*.jsonl"))
    packet, = packets
    landed = packet.read_bytes()
    if phase in {"unacknowledged", "packet-only"}:
        assert packet == legacy_packet and landed == payload
    else:
        expected = dict(original)
        for field, label in (("run_id", "run"), ("attempt_id", "attempt")):
            expected[field] = label + "-" + hashlib.sha256(original[field].encode()).hexdigest()[:16]
        assert landed == (_canonical(expected) + "\n").encode("ascii")
        if not single:
            marker = json.loads(packet.with_suffix(".ready").read_bytes())
            assert all(marker[field] == expected[field] for field in marker)
            assert not legacy_packet.exists()
    assert flush() == {"found": 0, "remaining": 0}
    assert packet.read_bytes() == landed


def _retained_retry_fixture(state, target, legacy):
    row = {
        "schema_version": "feedback-observation/1", "owner": "revenue-forecast",
        "run_id": "retry-run", "attempt_id": "retry-attempt", "step_id": "rf_job_cli/retry",
        "check_id": "process-outcome", "expected": "exit:0", "actual": "exit:2",
        "disposition": "deviation", "evidence_ref": "rf-fixture/retry",
    }
    if legacy:
        row.update(run_id="sk-valid-retry-fixture", attempt_id="tvly-valid-retry-fixture")
    body = _canonical({"row": row, "target": str(target), "single": False})
    retained = uuid5(NAMESPACE_URL, body).hex, body
    state.mkdir()
    db = state / "feedback.sqlite3"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE pending(id TEXT PRIMARY KEY,body TEXT NOT NULL)")
        conn.execute("INSERT INTO pending VALUES(?,?)", retained)
        conn.execute("CREATE TRIGGER reject_fixture_ack BEFORE DELETE ON pending "
                     "BEGIN SELECT RAISE(FAIL, 'isolated ACK failure'); END")
    conn.close()
    return db, retained


@pytest.mark.parametrize("legacy", [False, True], ids=["normal", "projected"])
@pytest.mark.parametrize("phase", ["consumed", "complete", "marker-only", "wrong-marker", "wrong-packet"])
def test_flush_reuses_the_final_delivery_after_sqlite_ack_failure(tmp_path, isolation, legacy, phase):
    env, state = isolation
    target = tmp_path / "retained-inbox"
    db, retained = _retained_retry_fixture(state, target, legacy)

    def flush():
        result = invoke(tmp_path, env, "scripts/rf_job_feedback.py", "flush-feedback")
        assert (result.returncode, result.stderr) == (0, b"")
        return json.loads(result.stdout)

    assert flush() == {"found": 1, "remaining": 1}
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT id,body FROM pending").fetchall() == [retained]
        conn.execute("DROP TRIGGER reject_fixture_ack")
    conn.close()
    packet, = target.glob("*.jsonl")
    marker = packet.with_suffix(".ready")
    payload = packet.read_bytes()
    if legacy:
        assert b"sk-valid-retry-fixture" not in payload and b"tvly-valid-retry-fixture" not in payload

    if phase == "consumed":
        marker.unlink()
    elif phase == "marker-only":
        packet.unlink()
    elif phase == "wrong-marker":
        marker.write_bytes(b'{"owner":"other-owner"}\n')
    elif phase == "wrong-packet":
        packet.write_bytes(b'{"owner":"other-owner"}\n')
    existing = {path: (path.read_bytes(), path.stat()) for path in (packet, marker) if path.exists()}
    remaining = int(phase in {"wrong-marker", "wrong-packet"})
    assert flush() == {"found": 1, "remaining": remaining}
    assert flush() == {"found": remaining, "remaining": remaining}
    assert marker.exists() == (phase != "consumed")
    for path, (data, st) in existing.items():
        current = path.stat()
        assert path.read_bytes() == data
        assert (current.st_ino, current.st_mtime_ns) == (st.st_ino, st.st_mtime_ns)
    if phase == "marker-only":
        assert packet.read_bytes() == payload
    assert list(target.glob("*.jsonl")) == [packet]
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT id,body FROM pending").fetchall() == ([retained] if remaining else [])
    conn.close()


@pytest.mark.parametrize("entry", ["rf_job_feedback", "report_catalog_compare_cli"])
@pytest.mark.parametrize("seed", [b'{"original":"complete"}', b'{"interrupted":'], ids=["unterminated", "torn"])
def test_cold_failure_survives_unterminated_native_journal(tmp_path, isolation, entry, seed):
    env, state = isolation
    log = state / "logs" / "runtime-errors.jsonl"
    log.parent.mkdir(parents=True)
    log.write_bytes(seed)
    blocker = tmp_path / "blocked-f4"
    blocker.write_bytes(b"unchanged")
    env["RESEARCH_FEEDBACK_OUT"] = str(blocker / "out.jsonl")
    env["RESEARCH_FEEDBACK_PROCESS_STEP_ID"] = "caller/native"
    if entry == "rf_job_feedback":
        arguments = ("reconcile", "--owner-root", tmp_path)
        types = ["JSONDecodeError"]
    else:
        (tmp_path / "artifacts" / "report_catalog").mkdir(parents=True)
        with sqlite3.connect(state / "feedback.sqlite3") as db:
            db.execute("CREATE TABLE failures(id TEXT PRIMARY KEY,body TEXT NOT NULL)")
            db.execute("CREATE TRIGGER refuse_fixture_detail BEFORE INSERT ON failures "
                       "BEGIN SELECT RAISE(FAIL,'fixture refuses the optional detail'); END")
        db.close()
        arguments = ("--owner-root", tmp_path, "compare")
        types = ["CompareError", "JSONDecodeError"]
    original = invoke(tmp_path, env, f"scripts/{entry}.py", *arguments, body=b"{")
    if entry == "rf_job_feedback":
        assert (original.returncode, original.stderr) == (1, b"")
        assert json.loads(original.stdout) == {"error": "JSONDecodeError"}
    else:
        assert (original.returncode, original.stdout) == (2, b"")
        assert len(original.stderr.splitlines()) == 1
        assert json.loads(original.stderr)["error"]["code"] == "invalid_json"

    identifier = uuid5(NAMESPACE_URL, repr(("rf-s6-startup", "attempt-one", "caller/native", entry))).hex
    saved = log.read_bytes()
    assert saved.startswith(seed + b"\n")
    persisted, = [row for line in saved[len(seed) + 1:].splitlines()
                  if (row := json.loads(line)).get("id") == identifier]
    assert [fact["type"] for fact in persisted["cause_chain"]] == types
    cold = invoke(tmp_path, env, "scripts/rf_job_feedback.py", "get-failure", identifier)
    assert (cold.returncode, cold.stderr) == (0, b"")
    assert [fact["type"] for fact in json.loads(cold.stdout)["cause_chain"]] == types
    assert log.read_bytes() == saved and blocker.read_bytes() == b"unchanged"


def _lookup_payload(identifier, run, attempt):
    observation = {"owner": "revenue-forecast", "run_id": run, "attempt_id": attempt,
                   "step_id": "report_catalog_cli/" + identifier, "evidence_ref": "rf-cli/1/" + identifier}
    return _action_payload(observation)


def _action_payload(observation):
    payload = {"observation": observation}
    key = "a" * 64
    digest = hashlib.sha256(_canonical(["revenue-forecast", "reconcile", key, payload]).encode()).hexdigest()
    return _canonical({
        "schema_version": "feedback-action/1", "owner": "revenue-forecast", "kind": "reconcile",
        "method": "lookup", "action_id": key, "request_digest": digest, "payload": payload,
    }).encode()


def test_frozen_raw_and_projected_rf_identities_resolve_without_writes(tmp_path, isolation):
    env, state = isolation
    state.mkdir()
    db = state / "feedback.sqlite3"
    identifier = "b" * 32
    run, attempt = "sk-RFOldRunIdentity", "tvly-RFOldAttemptIdentity"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE failures(id TEXT PRIMARY KEY, body TEXT NOT NULL)")
        connection.execute("INSERT INTO failures VALUES(?,?)", (identifier, _canonical({
            "id": identifier, "entrypoint": "report_catalog_cli", "native_code": "invalid_arguments",
            "run_id": run, "attempt_id": attempt, "exit_code": 2,
            "code_version": "old-record", "side_effect_state": "not_started",
        })))
    original = db.read_bytes()
    ids = [(run, attempt), ("run-" + hashlib.sha256(run.encode()).hexdigest()[:16],
                             "attempt-" + hashlib.sha256(attempt.encode()).hexdigest()[:16])]
    replies = []
    for run_id, attempt_id in ids:
        result = invoke(tmp_path, env, "scripts/rf_job_feedback.py", "reconcile",
                        "--owner-root", tmp_path, body=_lookup_payload(identifier, run_id, attempt_id))
        assert result.returncode == 0 and not result.stderr
        replies.append(json.loads(result.stdout))
    assert replies[0] == replies[1]
    assert replies[0]["state"] == "done" and replies[0]["result"]["cost_state"] == "not_applicable"
    assert db.read_bytes() == original and list(state.iterdir()) == [db]
    assert not Path(env["RESEARCH_FEEDBACK_OUT"]).exists()


def test_rotating_rf_log_has_no_lost_records_with_two_real_writers(tmp_path, isolation):
    env, state = isolation
    target = state / "logs" / "runtime-errors.jsonl"
    target.parent.mkdir(parents=True)
    seed = (json.dumps({"seed": "s" * (1024 * 1024)}) + "\n").encode()
    target.write_bytes(seed)

    def child(index):
        return invoke(tmp_path, {**env, "RESEARCH_FEEDBACK_RUN_ID": f"rf-writer-{index}"},
                      "scripts/revenue_forecast.py", "--invalid-s6-argument")

    with ThreadPoolExecutor(max_workers=2) as workers:
        results = tuple(workers.map(child, range(2)))
    assert all(result.returncode == 2 and not result.stdout for result in results)
    assert target.with_name(target.name + ".1").read_bytes() == seed
    assert {row["run_id"] for row in events(state) if row.get("entrypoint") == "revenue_forecast"} == {
        "rf-writer-0", "rf-writer-1",
    }


@pytest.mark.parametrize("dispatch", (False, True), ids=("before-dispatch", "after-dispatch"))
def test_rf_hard_stop_recovers_the_original_stage_without_replaying_or_charging(tmp_path, isolation, dispatch):
    deployment, _ = _deployment(tmp_path)
    root = tmp_path / "owner"
    root.mkdir()
    env, _ = isolation
    raw_run, raw_attempt = "sk-RFNativePhysicalRun34", "tvly-RFNativePhysicalAttempt34"
    env.update(RESEARCH_FEEDBACK_RUN_ID=raw_run, RESEARCH_FEEDBACK_ATTEMPT_ID=raw_attempt)
    remote = tmp_path / "ff" / "scripts" / "fetch_filing.py"
    remote.write_text(
        "import json, pathlib, sys, time\n"
        "request = json.load(sys.stdin)\n"
        "assert request['filing_intent'] == 'reuse_only'\n"
        "root = pathlib.Path(__file__).resolve().parents[2]\n"
        + ("with (root / 'dispatches').open('ab') as out: out.write(b'original\\n')\n" if dispatch else "")
        + "(root / 'ff_started').touch()\n"
        "until = time.monotonic() + 45\n"
        "while not (root / 'ff_release').is_file() and time.monotonic() < until:\n"
        "    time.sleep(0.04)\n"
        "(root / 'ff_finished').touch()\n"
        "raise SystemExit(2)\n", encoding="utf-8",
    )
    flags = ("--owner-root", str(root), "--deployment-config", str(deployment))
    process = subprocess.Popen(
        [sys.executable, "-B", str(ROOT / "scripts/rf_job_cli.py"), *flags, "submit"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tmp_path,
        env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        process.stdin.write(_canonical(_request()).encode())
        process.stdin.close()
        process.stdin = None
        wait_marker(tmp_path / "ff_started", process)
        expected_count = (tmp_path / "dispatches").read_bytes() if dispatch else None
        assert expected_count == (b"original\n" if dispatch else None)
        journal = Path(env["RESEARCH_FEEDBACK_OUT"])
        original, = [row for row in map(json.loads, journal.read_bytes().splitlines())
                     if row.get("check_id") == "action-started" and row["step_id"].endswith("/source-1")]
        job_id, stage = original["step_id"].split("/")
        assert stage == "source-1"
        process.kill()
        process.communicate(timeout=8)
        view = invoke(tmp_path, env, "scripts/rf_job_cli.py", *flags, "get-status", "--job-id", job_id)
        assert view.returncode == 0 and json.loads(view.stdout)["job_view"]["status"] == "interrupted"
        before = journal.read_bytes()
        answers = []
        for row in (dict(original, run_id=raw_run, attempt_id=raw_attempt), original, original):
            result = invoke(tmp_path, env, "scripts/rf_job_feedback.py", "reconcile",
                            "--owner-root", root, body=_action_payload(row))
            assert result.returncode == 0 and not result.stderr
            answers.append(json.loads(result.stdout))
        assert answers[0] == answers[1] == answers[2]
        assert answers[0]["state"] == "done"
        assert answers[0]["result"]["job_status"] == "interrupted"
        assert answers[0]["result"]["cost_state"] == "unknown"
        assert journal.read_bytes() == before
        observed_count = (tmp_path / "dispatches").read_bytes() if dispatch else None
        assert observed_count == expected_count
        assert (tmp_path / "dispatches").exists() is dispatch
    finally:
        (tmp_path / "ff_release").touch(exist_ok=True)
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=8)
        if (tmp_path / "ff_started").exists():
            wait_marker(tmp_path / "ff_finished")


def wait_marker(path, process=None):
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        if path.is_file():
            return
        if process is not None and process.poll() is not None:
            raise AssertionError(f"RF exited before {path.name}")
        time.sleep(0.05)
    raise AssertionError(f"RF did not reach {path.name}")


def test_archived_owned_failure_is_cold_readable_when_outbox_database_is_corrupt(tmp_path, isolation):
    env, state = isolation
    log = state / "logs" / "runtime-errors.jsonl.rotate"
    log.parent.mkdir(parents=True)
    key, run = "f" * 32, "sk-RFArchivedDiagnosticRun34"
    original = _canonical({"id": key, "run_id": run, "attempt_id": "same-attempt", "exit_code": 2,
                           "entrypoint": "filing_fetch_client", "native_code": "upstream_exit"})
    log.write_text(original + "\n", encoding="ascii")
    db = state / "feedback.sqlite3"
    db.write_bytes(b"damaged delivery index")
    result = invoke(tmp_path, env, "scripts/rf_job_feedback.py", "get-failure", key)
    assert result.returncode == 0 and not result.stderr and run.encode() not in result.stdout
    detail = json.loads(result.stdout)
    assert detail["id"] == key and detail["native_code"] == "upstream_exit"
    assert log.read_text(encoding="ascii") == original + "\n"
    assert db.read_bytes() == b"damaged delivery index"
    assert not Path(env["RESEARCH_FEEDBACK_OUT"]).exists()


def test_file_open_failure_keeps_type_without_exposing_a_credential_shaped_name(tmp_path, isolation):
    env, state = isolation
    result = invoke(tmp_path, env, "scripts/revenue_forecast.py", tmp_path / (PRIVATE_VALUES[3] + ".json"),
                    "--validate-only")
    assert result.returncode == 2 and not result.stdout
    assert b"No such file" in result.stderr
    row, = [row for row in events(state) if row.get("entrypoint") == "revenue_forecast"]
    assert any(part["type"] == "FileNotFoundError" and part["frames"] for part in row["cause_chain"])
    assert_no_credentials(result.stderr, json.dumps(row).encode())
