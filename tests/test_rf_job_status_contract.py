"""OWNERPKG-REVENUE-FORECAST-01 unit tests — G-m8-RF-02: status and actions.

get_status exposes real stage/attempt state and allowed actions, and keeps
catalog history (read-only, separate CLI) distinct from the live job.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rf_job_facade as facade  # noqa: E402
from rf_job_facade import (  # noqa: E402
    JobFacadeError,
    _allowed_actions,
)

from test_rf_job_facade import _facade, _request  # noqa: E402


def test_jobview_carries_every_required_contract_field(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    result = facade_obj.submit(_request())
    view = result["job_view"]
    for field in ("owner_job_id", "status", "status_known", "allowed_actions",
                  "cost", "cost_state", "recovery_capability"):
        assert field in view
    assert view["catalog_history"]["this_job_registered"] is False
    assert "import-research-attempt" in view["catalog_history"]["registration"]


def test_natural_source_failure_exposes_failed_attempts(tmp_path):
    behavior = {
        "source": lambda stage, command: facade.AttemptOutcome(
            exit_code=1, killed=False, elapsed_seconds=0.01),
    }
    facade_obj, _ = _facade(
        tmp_path,
        behavior=behavior,
        failure_stderr={"error_code": "upstream", "downloads": 0, "calls": 2},
    )
    result = facade_obj.submit(_request())
    view = result["job_view"]
    assert view["status"] == "failed"
    assert view["status_known"] is True
    assert view["allowed_actions"] == ["resume", "reconcile"]
    source_stage = view["stages"][0]
    assert source_stage["status"] == "failed"
    attempt = source_stage["attempts"][0]
    assert attempt["status"] == "failed"
    assert attempt["exit_code"] == 1
    # The FF calls count records local subprocesses. A read-only source
    # can be retried even if that count cannot establish paid usage.
    assert attempt["observations"] == {"download_events": 0, "acquisition_calls": 2}
    assert view["cost_state"] == "unknown"
    assert view["cost"] is None


def test_interrupted_stage_view_exposes_attempt_without_exit(tmp_path):
    behavior = {
        "compute": lambda stage, command: facade.AttemptOutcome(
            exit_code=None, killed=True, elapsed_seconds=120.0),
    }
    facade_obj, _ = _facade(tmp_path, behavior=behavior)
    result = facade_obj.submit(_request())
    view = result["job_view"]
    assert view["status"] == "interrupted"
    compute_stage = view["stages"][1]
    assert compute_stage["status"] == "interrupted"
    assert compute_stage["attempts"][0]["exit_code"] is None


def test_list_jobs_reports_job_views(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    first = facade_obj.submit(_request())
    listing = facade_obj.list_jobs()
    ids = [job["owner_job_id"] for job in listing["jobs"]]
    assert ids == [first["owner_job_id"]]
    assert listing["jobs"][0]["status"] == "succeeded"


def test_get_status_of_unknown_job_is_a_named_error(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    with pytest.raises(JobFacadeError) as excinfo:
        facade_obj.get_status("rfjob-nope")
    assert excinfo.value.code == "owner_job_not_found"


def test_allowed_actions_matrix():
    assert _allowed_actions("queued") == ["resume"]
    assert _allowed_actions("running") == []
    assert _allowed_actions("succeeded") == []
    assert _allowed_actions("failed") == ["resume", "reconcile"]
    assert _allowed_actions("interrupted") == ["resume", "reconcile"]
    assert _allowed_actions("unknown") == ["reconcile"]
