"""Read-only F4 reattachment to explicitly configured RF owner stores."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
from shutil import copytree
import sys
from threading import Barrier

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from owner_atomic_io import native_path, open_regular_file  # noqa: E402
from rf_feedback_outbox import flush, publish, was_published  # noqa: E402
from rf_job_facade import JobFacade  # noqa: E402
from rf_job_feedback import digest, lookup  # noqa: E402
from test_f4_failure_coverage import env, invoke, observations  # noqa: E402
from test_rf_job_facade import _facade, _request  # noqa: E402

OWNER = "revenue-forecast"


@pytest.fixture
def completed_job(tmp_path, monkeypatch, request):
    allowed = {"PATH", "PATHEXT", "COMSPEC", "SYSTEMROOT", "WINDIR", "TEMP", "TMP",
               "PYTHONUTF8", "PYTHONDONTWRITEBYTECODE", "PYTHON_DOTENV_DISABLED",
               "LOCALAPPDATA", "XDG_STATE_HOME", "RESEARCH_FEEDBACK_DIR"}
    config = {key: value for key, value in env(tmp_path).items() if key.upper() in allowed}
    for key in ("LOCALAPPDATA", "XDG_STATE_HOME", "RESEARCH_FEEDBACK_DIR"):
        monkeypatch.setenv(key, config[key])
    for key in ("RESEARCH_FEEDBACK_OUT", "RESEARCH_FEEDBACK_RUN_ID", "RESEARCH_FEEDBACK_ATTEMPT_ID"):
        monkeypatch.delenv(key, raising=False)
    transport = getattr(request, "param", "direct")
    if transport != "direct":
        monkeypatch.setenv("RESEARCH_FEEDBACK_RUN_ID", "original-run")
        monkeypatch.setenv("RESEARCH_FEEDBACK_ATTEMPT_ID", "original-wrapper-attempt")
    if transport == "single-file":
        config["RESEARCH_FEEDBACK_OUT"] = str(tmp_path / "owner-out.jsonl")
        monkeypatch.setenv("RESEARCH_FEEDBACK_OUT", config["RESEARCH_FEEDBACK_OUT"])
    facade, root = _facade(tmp_path)
    submitted = facade.submit(_request())
    assert submitted["job_view"]["status"] == "succeeded"
    job_id = submitted["owner_job_id"]
    job_path = facade.store.job_file(job_id).relative_to(facade.store.owner_root)
    if transport == "single-file":
        rows = [json.loads(line) for line in Path(config["RESEARCH_FEEDBACK_OUT"]).read_bytes().splitlines()]
    else:
        rows = observations(tmp_path / "box")
    [usage] = [row for row in rows if row["check_id"] == "job-usage"]
    return root, job_path, config, job_id, usage


def lookup_request(observation, **overrides):
    event = dict(observation, origin_owner=OWNER)
    event.update(overrides)
    occurrence = digest([event[key] for key in (
        "owner", "origin_owner", "run_id", "attempt_id", "step_id", "check_id",
    )])
    key = digest(["reconcile", OWNER, occurrence])
    payload = {"observation": event, "occurrence_id": occurrence}
    return {
        "schema_version": "feedback-action/1", "owner": OWNER, "kind": "reconcile", "method": "lookup",
        "action_id": key, "payload": payload, "request_digest": digest([OWNER, "reconcile", key, payload]),
    }


def cold(tmp_path, config, payload, *roots):
    flags = [item for root in roots for item in ("--owner-root", root)]
    result = invoke(tmp_path, config, "rf_job_feedback", "reconcile", *flags, data=json.dumps(payload))
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def snapshot(root):
    return {item.relative_to(root).as_posix(): sha256(item.read_bytes()).hexdigest()
            for item in root.rglob("*") if item.is_file()}


@pytest.mark.parametrize("completed_job", ("direct", "wrapper"), indirect=True)
def test_exact_job_is_found_in_configured_root_regardless_of_order(tmp_path, completed_job):
    found, _, config, job_id, usage = completed_job
    missing = tmp_path / "default-store"
    missing.mkdir()
    payload = lookup_request(usage, owner_root=str(found))
    expected = {"state": "done", "result": {
        "status": "known", "job_status": "succeeded", "cost_state": "known",
        "evidence_ref": f"rf-job/1/{job_id}/publication-1",
    }}
    before = snapshot(tmp_path)
    assert cold(tmp_path, config, payload, missing) == {"state": "unknown"}
    assert cold(tmp_path, config, payload, found) == expected
    assert cold(tmp_path, config, payload, found, missing) == expected
    assert cold(tmp_path, config, payload, missing, found) == expected
    assert snapshot(tmp_path) == before


def test_replicas_need_the_same_original_scope_and_result(tmp_path, completed_job):
    original, original_job, config, _, usage = completed_job
    replica = tmp_path / "frozen-copy"
    copytree(original, replica)
    payload = lookup_request(usage)
    first = cold(tmp_path, config, payload, original)
    assert first["state"] == "done" and first["result"]["job_status"] == "succeeded"
    assert cold(tmp_path, config, payload, original, replica) == first
    replica_job = replica / original_job
    state = json.loads(replica_job.read_bytes())
    state["scope"]["company_query"] = "Another issuer"
    replica_job.write_text(json.dumps(state), encoding="utf-8")
    assert cold(tmp_path, config, payload, replica) == first  # Both public summaries alone look identical.
    before = snapshot(tmp_path)
    conflict = {"state": "unknown", "code": "native_owner_conflict"}
    assert cold(tmp_path, config, payload, original, replica) == conflict
    assert cold(tmp_path, config, payload, replica, original) == conflict
    assert snapshot(tmp_path) == before


def test_unreadable_existing_job_is_not_a_missing_replica(tmp_path, completed_job):
    original, original_job, config, _, usage = completed_job
    replica = tmp_path / "damaged-copy"
    copytree(original, replica)
    (replica / original_job).write_text("{", encoding="utf-8")
    before = snapshot(tmp_path)
    assert cold(tmp_path, config, lookup_request(usage), replica, original) == {
        "state": "unknown", "code": "native_owner_unverified",
    }
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("repeat", [False, True])
def test_a_single_effective_root_reports_an_unverified_existing_job(tmp_path, completed_job, repeat):
    original, original_job, config, _, usage = completed_job
    (original / original_job).write_text("{", encoding="utf-8")
    roots = (original, original.parent / original.name) if repeat else (original,)
    before = snapshot(tmp_path)
    assert cold(tmp_path, config, lookup_request(usage), *roots) == {
        "state": "unknown", "code": "native_owner_unverified",
    }
    assert snapshot(tmp_path) == before


def test_duplicate_resolved_roots_read_once_and_keep_old_attempt_refusal(tmp_path, completed_job, monkeypatch):
    original, _, _, job_id, usage = completed_job
    original_get_status = JobFacade.get_status
    calls = []

    def observed(facade, owner_job_id):
        calls.append((facade.owner_root, owner_job_id))
        return original_get_status(facade, owner_job_id)

    monkeypatch.setattr(JobFacade, "get_status", observed)
    result = lookup(original, lookup_request(usage, step_id=f"{job_id}/publication-2",
                                            evidence_ref=f"rf-job/1/{job_id}/publication-2"),
                    additional_owner_roots=(original / ".." / original.name, original))
    assert result == {"state": "unknown", "code": "native_attempt_mismatch"}
    assert len(calls) == 1


@pytest.mark.parametrize("field", ("run_id", "attempt_id"))
def test_exact_evidence_reference_cannot_override_a_recorded_identity(tmp_path, completed_job, field):
    original, _, config, _, usage = completed_job
    assert cold(tmp_path, config, lookup_request(usage, **{field: "conflicting-owner-identity"}), original) == {
        "state": "unknown", "code": "native_attempt_mismatch",
    }


@pytest.mark.parametrize("completed_job", ("wrapper", "single-file"), indirect=True)
def test_legacy_job_without_wrapper_metadata_recovers_original_reference(tmp_path, completed_job):
    original, original_job, config, job_id, usage = completed_job
    expected = cold(tmp_path, config, lookup_request(usage), original)
    assert expected["state"] == "done"
    state = json.loads((original / original_job).read_bytes())
    [attempt] = state["stages"]["publication"]["attempts"]
    assert attempt.pop("feedback_run_id") == usage["run_id"]
    assert attempt.pop("feedback_attempt_id") == usage["attempt_id"]
    (original / original_job).write_text(json.dumps(state), encoding="utf-8")
    if "RESEARCH_FEEDBACK_OUT" not in config:
        for marker in (tmp_path / "box").glob("*.ready"):
            marker.unlink()  # The feedback intake already acknowledged these packets.
    state_before_lookup = snapshot(tmp_path)
    assert cold(tmp_path, config, lookup_request(usage), original) == expected
    assert cold(tmp_path, config, lookup_request(usage, run_id="unrelated-wrapper"), original) == {
        "state": "unknown", "code": "native_attempt_mismatch",
    }
    unavailable = dict(config, RESEARCH_FEEDBACK_DIR=str(tmp_path / "missing-outbox"))
    unavailable.pop("RESEARCH_FEEDBACK_OUT", None)
    assert cold(tmp_path, unavailable, lookup_request(usage), original) == {
        "state": "unknown", "code": "native_attempt_mismatch",
    }
    canonical = lookup_request(usage, run_id=job_id, attempt_id="publication-1")
    assert cold(tmp_path, unavailable, canonical, original) == expected
    assert snapshot(tmp_path) == state_before_lookup


@pytest.fixture
def isolated_outbox(tmp_path, monkeypatch):
    config = env(tmp_path)
    for key in ("LOCALAPPDATA", "XDG_STATE_HOME", "RESEARCH_FEEDBACK_DIR"):
        monkeypatch.setenv(key, config[key])
    monkeypatch.delenv("RESEARCH_FEEDBACK_OUT", raising=False)
    return {
        "schema_version": "feedback-observation/1", "owner": OWNER, "run_id": "local-run",
        "attempt_id": "local-attempt", "step_id": "fixture-stage", "check_id": "action-started",
        "expected": "started", "actual": "started",
    }


def _record_no_descriptor_access(monkeypatch, *paths):
    protected = {native_path(path) for path in paths}
    path_open, os_open = Path.open, os.open

    def assert_not_protected(path):
        if not isinstance(path, int):
            assert native_path(Path(os.fsdecode(path))) not in protected, "rejected leaf reached file open"

    def path_guard(path, *args, **kwargs):
        assert_not_protected(path)
        return path_open(path, *args, **kwargs)

    def descriptor_guard(path, *args, **kwargs):
        assert_not_protected(path)
        return os_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", path_guard)
    monkeypatch.setattr(os, "open", descriptor_guard)


@pytest.mark.skipif(os.name != "posix", reason="uses real POSIX symbolic links")
def test_outbox_allows_configured_parent_alias_and_rejects_leaf_link(tmp_path, monkeypatch, isolated_outbox):
    physical = tmp_path / "owner"
    physical.mkdir()
    alias = tmp_path / "configured-alias"
    alias.symlink_to(physical, target_is_directory=True)
    monkeypatch.setenv("RESEARCH_FEEDBACK_DIR", str(alias))
    publish(isolated_outbox)
    assert was_published(isolated_outbox)
    [packet] = alias.glob("feedback-*.jsonl")
    detached = tmp_path / "unrelated-synthetic-file"
    detached.write_bytes(b"unrelated fixture bytes")
    packet.unlink()
    packet.symlink_to(detached)

    with monkeypatch.context() as guard:
        _record_no_descriptor_access(guard, packet, physical / packet.name, detached)
        assert not was_published(isolated_outbox)
    assert packet.is_symlink()
    assert detached.read_bytes() == b"unrelated fixture bytes"


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="uses a real POSIX FIFO")
def test_special_single_file_retains_original_pending_record_without_opening_node(tmp_path, monkeypatch, isolated_outbox):
    output = tmp_path / "explicit-outbox.jsonl"
    monkeypatch.setenv("RESEARCH_FEEDBACK_OUT", str(output))
    os.mkfifo(output)
    with monkeypatch.context() as guard:
        _record_no_descriptor_access(guard, output)
        publish(isolated_outbox)
        assert flush() == {"found": 1, "remaining": 1}
        assert not was_published(isolated_outbox)
    output.unlink()
    assert flush() == {"found": 1, "remaining": 0}
    assert [json.loads(line) for line in output.read_bytes().splitlines()] == [isolated_outbox]
    assert was_published(isolated_outbox)


@pytest.mark.parametrize("creating", (False, True), ids=("descriptor", "exclusive-create"))
def test_owner_file_checks_descriptor_identity_and_preserves_concurrent_file(tmp_path, monkeypatch, creating):
    candidate = tmp_path / "owner.jsonl"
    separate = tmp_path / "separate-fixture.jsonl"
    separate.write_bytes(b"separate fixture")
    if not creating:
        candidate.write_bytes(b"original fixture")
    real_open = os.open

    def changed_at_open(path, flags, mode=0o777, **kwargs):
        assert Path(path) == native_path(candidate)
        if os.name == "posix":
            assert flags & os.O_NOFOLLOW and flags & os.O_NONBLOCK
        if creating:
            if flags & os.O_EXCL:
                assert flags & os.O_CREAT
                candidate.write_bytes(b"concurrent fixture")
            else:
                assert not flags & (os.O_CREAT | os.O_TRUNC)
        else:
            path = native_path(separate)
        return real_open(path, flags, mode, **kwargs)

    with monkeypatch.context() as override:
        override.setattr(os, "open", changed_at_open)
        if creating:
            with open_regular_file(candidate, append=True) as stream:
                stream.seek(0)
                assert stream.read() == b"concurrent fixture"
        else:
            with pytest.raises(OSError, match="identity changed"), open_regular_file(candidate):
                pytest.fail("A descriptor for a different file must be rejected")
    assert candidate.read_bytes() == (b"concurrent fixture" if creating else b"original fixture")
    assert separate.read_bytes() == b"separate fixture"


def test_single_file_fallback_preserves_two_original_observations(tmp_path, monkeypatch, isolated_outbox):
    blocked_state = tmp_path / "unavailable-state"
    blocked_state.write_bytes(b"synthetic blocker")
    for key in ("LOCALAPPDATA", "XDG_STATE_HOME"):
        monkeypatch.setenv(key, str(blocked_state))
    output = tmp_path / "first-publication.jsonl"
    monkeypatch.setenv("RESEARCH_FEEDBACK_OUT", str(output))
    expected = [dict(isolated_outbox, run_id=run) for run in ("original-1", "original-2")]
    real_open = os.open
    creation = Barrier(2, timeout=5)
    initial_opens = []

    def simultaneous_creation(path, flags, *args, **kwargs):
        if Path(path) == native_path(output) and flags & os.O_EXCL:
            initial_opens.append(flags)
            creation.wait()
        return real_open(path, flags, *args, **kwargs)

    with monkeypatch.context() as overlap:
        overlap.setattr(os, "open", simultaneous_creation)
        with ThreadPoolExecutor(max_workers=2) as workers:
            calls = [workers.submit(publish, row) for row in expected]
            for call in calls:
                call.result(timeout=10)

    assert len(initial_opens) == 2
    assert blocked_state.read_bytes() == b"synthetic blocker"
    rows = [json.loads(line) for line in output.read_bytes().splitlines()]
    assert sorted(rows, key=lambda row: row["run_id"]) == expected
    assert all(was_published(row) for row in expected)
    blocked_state.unlink()
    assert flush() == {"found": 0, "remaining": 0}
    assert [json.loads(line) for line in output.read_bytes().splitlines()] == rows


@pytest.mark.skipif(os.name != "posix", reason="uses a real POSIX leaf substitution")
@pytest.mark.parametrize("substitute", ("symlink", "fifo"))
def test_rejected_leaf_won_the_first_creation_race(tmp_path, monkeypatch, substitute):
    candidate = tmp_path / "first-publication.jsonl"
    detached = tmp_path / "separate-fixture.jsonl"
    detached.write_bytes(b"unrelated synthetic bytes")
    competing_leaf = tmp_path / "competing-leaf"
    if substitute == "symlink":
        competing_leaf.symlink_to(detached)
    else:
        os.mkfifo(competing_leaf)
    real_open = os.open

    def concurrent_creation(path, flags, *args, **kwargs):
        assert Path(path) == candidate and flags & os.O_CREAT and flags & os.O_EXCL
        competing_leaf.rename(candidate)
        return real_open(path, flags, *args, **kwargs)

    with monkeypatch.context() as race:
        race.setattr(os, "open", concurrent_creation)
        with pytest.raises(OSError, match="ordinary file leaf"), open_regular_file(candidate, append=True):
            pytest.fail("A substituted leaf cannot be used as the owner's outbox")
    assert detached.read_bytes() == b"unrelated synthetic bytes"
