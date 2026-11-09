"""OWNERPKG-REVENUE-FORECAST-01 unit tests — G-m8-RF-04: recovery semantics.

Interruption leaves recoverable durable state; reconcile re-derives and
repairs from the records+artifacts authority; resume never re-runs completed
stages; unreadable state is honestly unknown with reconcile as the only
allowed action.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rf_job_facade import (  # noqa: E402
    JobFacade,
    SimulatedProcessDeath,
    JobFacadeError,
)

from test_rf_job_facade import _deployment, _facade, _request  # noqa: E402


def test_simulated_death_leaves_recoverable_state(tmp_path):
    facade_obj, _ = _facade(tmp_path, die_on_stage="source")
    with pytest.raises(SimulatedProcessDeath):
        facade_obj.submit(_request())
    # a NEW facade instance (the restarted harness) reads the durable state
    restarted, _ = _facade(tmp_path)
    job_id = restarted.store.list_job_ids()[0]
    view = restarted.get_status(job_id)["job_view"]
    assert view["status"] == "interrupted"
    assert view["status_known"] is True
    assert view["allowed_actions"] == ["resume", "reconcile"]
    assert view["cost_state"] == "unknown"
    assert view["cost"] is None
    assert view["stages"][0]["status"] == "interrupted"


def test_resume_after_death_completes_without_rerunning_completed_stages(tmp_path):
    facade_obj, _ = _facade(tmp_path, die_on_stage="compute")
    with pytest.raises(SimulatedProcessDeath):
        facade_obj.submit(_request())
    restarted, _ = _facade(tmp_path)
    job_id = restarted.store.list_job_ids()[0]
    # source completed before the death; compute never produced a result
    view = restarted.get_status(job_id)["job_view"]
    assert view["stages"][0]["status"] == "completed"
    assert view["stages"][1]["status"] == "interrupted"
    resumed = restarted.act(job_id, "resume")
    assert resumed["job_view"]["status"] == "succeeded"
    job = restarted.store.load_job(job_id)
    # the completed source stage was NOT re-run (one attempt only); the
    # interrupted compute stage legitimately got a second attempt
    assert len(job["stages"]["source"]["attempts"]) == 1
    assert len(job["stages"]["compute"]["attempts"]) == 2
    assert len(job["stages"]["publication"]["attempts"]) == 1


def test_reconcile_repairs_state_and_reports_completed_stages(tmp_path):
    facade_obj, _ = _facade(tmp_path, die_on_stage="compute")
    with pytest.raises(SimulatedProcessDeath):
        facade_obj.submit(_request())
    restarted, _ = _facade(tmp_path)
    job_id = restarted.store.list_job_ids()[0]
    result = restarted.act(job_id, "reconcile")
    view = result["job_view"]
    assert view["status"] == "interrupted"
    assert view["status_known"] is True
    job = restarted.store.load_job(job_id)
    # reconcile stamped the durable record with the interrupted-attempt fact
    compute_attempt = job["stages"]["compute"]["attempts"][0]
    assert compute_attempt["status"] == "interrupted"
    assert compute_attempt["interrupted_by"] == "reconcile"


def test_corrupt_state_yields_unknown_and_only_reconcile(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    result = facade_obj.submit(_request())
    job_id = result["owner_job_id"]
    job_file = facade_obj.store.job_file(job_id)
    job_file.write_text("{not json", encoding="utf-8")
    restarted, _ = _facade(tmp_path)
    view = restarted.get_status(job_id)["job_view"]
    assert view["status"] == "unknown"
    assert view["status_known"] is False
    assert view["allowed_actions"] == ["reconcile"]
    assert view["cost_state"] == "unknown"
    # reconcile cannot invent semantics for unreadable records: unknown stands
    reconciled = restarted.act(job_id, "reconcile")
    assert reconciled["job_view"]["status"] == "unknown"
    assert reconciled["job_view"]["status_known"] is False


def test_queued_job_resumes_from_scratch(tmp_path):
    owner_root = tmp_path / "owner"
    owner_root.mkdir()
    deployment = _deployment(tmp_path)

    class DyingFactory:
        def __call__(self, store, owner_job_id):
            raise SimulatedProcessDeath

    facade_obj = JobFacade(owner_root, deployment, runner_factory=DyingFactory())
    with pytest.raises(SimulatedProcessDeath):
        facade_obj.submit(_request())
    restarted, _ = _facade(tmp_path)
    job_id = restarted.store.list_job_ids()[0]
    view = restarted.get_status(job_id)["job_view"]
    assert view["status"] == "queued"
    assert view["allowed_actions"] == ["resume"]
    assert view["cost_state"] == "not_applicable"
    resumed = restarted.act(job_id, "resume")
    assert resumed["job_view"]["status"] == "succeeded"


def test_resume_of_succeeded_job_is_refused(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    result = facade_obj.submit(_request())
    with pytest.raises(JobFacadeError) as excinfo:
        facade_obj.act(result["owner_job_id"], "resume")
    assert excinfo.value.code == "action_not_allowed"


def test_compute_timeout_is_recorded_as_interrupted(tmp_path):
    import rf_job_facade as facade

    behavior = {
        "compute": lambda stage, command: facade.AttemptOutcome(
            exit_code=None, killed=True, elapsed_seconds=120.0),
    }
    facade_obj, _ = _facade(tmp_path, behavior=behavior)
    result = facade_obj.submit(_request(idempotency_key="timeout-key"))
    view = result["job_view"]
    assert view["status"] == "interrupted"
    assert view["stages"][0]["status"] == "completed"
    assert view["stages"][1]["status"] == "interrupted"
    assert view["stages"][1]["attempts"][0]["exit_code"] is None
    assert view["cost_state"] == "unknown"


def test_illegal_attempt_status_keeps_unknown_status_known_false_pairing(tmp_path):
    """FND-A1 regression: an attempt record with an unrecognized status value
    must keep the contract pairing status=unknown <-> status_known=false,
    both in get_status and after a persisted reconcile."""
    import json as _json

    facade_obj, _ = _facade(tmp_path)
    result = facade_obj.submit(_request())
    job_id = result["owner_job_id"]
    job_file = facade_obj.store.job_file(job_id)
    job = _json.loads(job_file.read_text(encoding="utf-8"))
    job["stages"]["source"]["attempts"][0]["status"] = "garbage"
    job_file.write_text(_json.dumps(job, ensure_ascii=False), encoding="utf-8")
    restarted, _ = _facade(tmp_path)
    view = restarted.get_status(job_id)["job_view"]
    assert view["status"] == "unknown"
    assert view["status_known"] is False
    assert view["allowed_actions"] == ["reconcile"]
    reconciled = restarted.act(job_id, "reconcile")["job_view"]
    assert reconciled["status"] == "unknown"
    assert reconciled["status_known"] is False
    assert reconciled["allowed_actions"] == ["reconcile"]
