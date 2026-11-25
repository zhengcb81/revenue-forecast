"""Read-only F4 reattachment to explicitly configured RF owner stores."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from shutil import copytree
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from rf_job_facade import JobFacade  # noqa: E402
from rf_job_feedback import digest, lookup  # noqa: E402
from test_f4_failure_coverage import env, invoke  # noqa: E402
from test_rf_job_facade import _facade, _request  # noqa: E402

OWNER = "revenue-forecast"


@pytest.fixture
def completed_job(tmp_path, monkeypatch):
    allowed = {"PATH", "PATHEXT", "COMSPEC", "SYSTEMROOT", "WINDIR", "TEMP", "TMP",
               "PYTHONUTF8", "PYTHONDONTWRITEBYTECODE", "PYTHON_DOTENV_DISABLED",
               "LOCALAPPDATA", "XDG_STATE_HOME", "RESEARCH_FEEDBACK_DIR"}
    config = {key: value for key, value in env(tmp_path).items() if key.upper() in allowed}
    for key in ("LOCALAPPDATA", "XDG_STATE_HOME", "RESEARCH_FEEDBACK_DIR"):
        monkeypatch.setenv(key, config[key])
    for key in ("RESEARCH_FEEDBACK_OUT", "RESEARCH_FEEDBACK_RUN_ID", "RESEARCH_FEEDBACK_ATTEMPT_ID"):
        monkeypatch.delenv(key, raising=False)
    facade, root = _facade(tmp_path)
    submitted = facade.submit(_request())
    assert submitted["job_view"]["status"] == "succeeded"
    job_id = submitted["owner_job_id"]
    job_path = facade.store.job_file(job_id).relative_to(facade.store.owner_root)
    return root, job_path, config, job_id


def request(job_id, *, attempt="publication-1", **extra):
    ref = f"rf-job/1/{job_id}/{attempt}"
    event = {
        "owner": OWNER, "origin_owner": OWNER, "run_id": "original-run",
        "attempt_id": "original-wrapper-attempt", "step_id": f"{job_id}/{attempt}",
        "check_id": "job-usage", "evidence_ref": ref, **extra,
    }
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


def test_exact_job_is_found_in_configured_root_regardless_of_order(tmp_path, completed_job):
    found, _, config, job_id = completed_job
    missing = tmp_path / "default-store"
    missing.mkdir()
    payload = request(job_id, owner_root=str(found))
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
    original, original_job, config, job_id = completed_job
    replica = tmp_path / "frozen-copy"
    copytree(original, replica)
    payload = request(job_id)
    first = cold(tmp_path, config, payload, original)
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
    original, original_job, config, job_id = completed_job
    replica = tmp_path / "damaged-copy"
    copytree(original, replica)
    (replica / original_job).write_text("{", encoding="utf-8")
    before = snapshot(tmp_path)
    assert cold(tmp_path, config, request(job_id), replica, original) == {
        "state": "unknown", "code": "native_owner_unverified",
    }
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("repeat", [False, True])
def test_a_single_effective_root_reports_an_unverified_existing_job(tmp_path, completed_job, repeat):
    original, original_job, config, job_id = completed_job
    (original / original_job).write_text("{", encoding="utf-8")
    roots = (original, original.parent / original.name) if repeat else (original,)
    before = snapshot(tmp_path)
    assert cold(tmp_path, config, request(job_id), *roots) == {
        "state": "unknown", "code": "native_owner_unverified",
    }
    assert snapshot(tmp_path) == before


def test_duplicate_resolved_roots_read_once_and_keep_old_attempt_refusal(tmp_path, completed_job, monkeypatch):
    original, _, _, job_id = completed_job
    original_get_status = JobFacade.get_status
    calls = []

    def observed(facade, owner_job_id):
        calls.append((facade.owner_root, owner_job_id))
        return original_get_status(facade, owner_job_id)

    monkeypatch.setattr(JobFacade, "get_status", observed)
    result = lookup(original, request(job_id, attempt="publication-2"),
                    additional_owner_roots=(original / ".." / original.name, original))
    assert result == {"state": "unknown", "code": "native_attempt_mismatch"}
    assert len(calls) == 1
