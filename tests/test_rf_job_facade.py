"""OWNERPKG-REVENUE-FORECAST-01 unit tests — G-m8-RF-01: public job submission.

rf-job/1 submit contract: fixed request shape, engine fail-fast validation
with scope cross-checks, fixed stage argv, trusted-root discipline.  These
tests exercise the facade state machine with the injected fake stage runner
(the documented test double) — they are NOT the real cross-repo evidence;
the real drill artifacts live under .planning/rf-job-facade-01/evidence/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rf_job_facade as facade  # noqa: E402
from rf_job_facade import (  # noqa: E402
    Deployment,
    FakeStageRunner,
    JobFacade,
    JobFacadeError,
    SubprocessStageRunner,
)

from test_data_contract import valid_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

LIMITS_REF = "unit-drill-0usd"


def _deployment(tmp_path: Path, *, limits_ref: str = LIMITS_REF) -> Deployment:
    source_root = tmp_path / "deployment"
    source_root.mkdir(exist_ok=True)
    return Deployment({
        "schema_version": "rf-job-deployment/1",
        "python": sys.executable,
        "stages": {
            "source": {
                "filing_fetch_root": str(source_root / "ff"),
                "company_wiki_config": str(source_root / "ff" / "config.json"),
                "company_wiki_catalog_config": str(source_root / "wiki" / "catalog.yaml"),
                "source_reader_receipt_version": "2.2",
                "timeout_seconds": 60.0,
                "request_template": {"schema_version": "2.0", "market": "CN",
                                     "document_kind": "annual_report",
                                     "fiscal_year": 2025,
                                     "mode": "exact",
                                     "filing_intent": "reuse_only"},
            },
            "compute": {"timeout_seconds": 120.0},
            "publication": {"timeout_seconds": 30.0},
        },
        "limits": {"refs": {limits_ref: {"max_cost_usd": "0.00", "max_wall_seconds": 600,
                                         "max_new_downloads": 0,
                                         "max_attempts_per_stage": 3}},
                   "default_ref": limits_ref},
    })


def _request(document: dict | None = None, **overrides) -> dict:
    document = document if document is not None else forecast_document()
    request = {
        "schema_version": "rf-job/1",
        "workflow": "full_research",
        "company_query": "Test Co",
        "information_as_of": document["as_of_date"],
        "horizon_end_year": max(document["forecast_years"]),
        "scenario_set": ["low", "base", "high"],
        "source_snapshot_ids": [],
        "idempotency_key": "unit-key-1",
        "limits_ref": LIMITS_REF,
        "forecast_input": document,
    }
    request.update(overrides)
    return request


def _facade(tmp_path: Path, *, calls: list | None = None,
            **runner_kwargs) -> tuple[JobFacade, Path]:
    owner_root = tmp_path / "owner"
    owner_root.mkdir(exist_ok=True)
    deployment = _deployment(tmp_path)
    collected = calls if calls is not None else []

    def factory(store, owner_job_id):
        runner = FakeStageRunner(store, owner_job_id, **runner_kwargs)
        collected.append(runner)
        return runner

    facade_obj = JobFacade(owner_root, deployment, runner_factory=factory)
    return facade_obj, owner_root


def _recorded_requests(calls: list) -> list[dict]:
    return [request for runner in calls for request in runner.requests]


# ------------------------------------------------------------- submit contract


def test_submit_runs_three_stages_and_succeeds(tmp_path):
    facade_obj, owner_root = _facade(tmp_path)
    result = facade_obj.submit(_request())
    view = result["job_view"]
    assert result["owner_job_id"].startswith("rfjob-")
    assert view["status"] == "succeeded"
    assert view["status_known"] is True
    assert view["allowed_actions"] == []
    assert view["cost"] == {"currency": "USD", "value": "0.00"}
    assert view["cost_state"] == "known"
    assert view["recovery_capability"] == "durable_owner_job"
    assert set(view["command_recovery"]) == set(facade.COMMAND_RECOVERY)
    stage_status = {stage["stage"]: stage["status"] for stage in view["stages"]}
    assert stage_status == {"source": "completed", "compute": "completed",
                            "publication": "completed"}
    # G-m8-RF-05: the trusted root is never in any stage command
    for request in facade_obj.store.load_job(result["owner_job_id"])["stages"]["source"]["attempts"]:
        assert "--owner-root" not in request["command_shape"]
    # durable layout exists
    job_dir = owner_root / "artifacts" / "rf_jobs" / "jobs" / result["owner_job_id"]
    assert (job_dir / "stages" / "source" / "result-envelope.json").exists()
    assert (job_dir / "stages" / "compute" / "result.json").exists()
    assert (job_dir / "stages" / "publication" / "audit.json").exists()


def test_stage_commands_are_fixed_and_pathless_to_business(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    document = forecast_document()
    facade_obj.submit(_request(document=document))
    job_ids = facade_obj.store.list_job_ids()
    job = facade_obj.store.load_job(job_ids[0])
    commands = {attempt["stage"]: attempt["command_shape"]
                for stage in facade.STAGES
                for attempt in job["stages"][stage]["attempts"]}
    source = commands["source"]
    assert source[2].endswith("source_preparation.py")
    assert "--result-envelope" in source
    assert "--allow-download" not in source
    assert source[source.index("--request-file") + 1].endswith("request.json")
    compute = commands["compute"]
    assert compute[2].endswith("revenue_forecast.py")
    publication = commands["publication"]
    assert publication[2].endswith("publication_registry.py")
    assert publication[3:5] == ["audit", "--result"]
    # the compute input written by the facade is the exact request document
    stored_input = json.loads((facade_obj.store.stage_dir(job["owner_job_id"], "compute")
                               / "input.json").read_text(encoding="utf-8"))
    assert stored_input == document


def test_request_cross_checks(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    document = forecast_document()
    with pytest.raises(JobFacadeError) as excinfo:
        facade_obj.submit(_request(document=document, information_as_of="2026-01-01"))
    assert excinfo.value.code == "request_invalid"
    with pytest.raises(JobFacadeError) as excinfo:
        facade_obj.submit(_request(document=document, horizon_end_year=2025))
    assert excinfo.value.code == "request_invalid"
    with pytest.raises(JobFacadeError) as excinfo:
        facade_obj.submit(_request(document=document, scenario_set=["low", "moonshot"]))
    assert excinfo.value.code == "request_invalid"
    broken = valid_document()
    broken.pop("segments")
    with pytest.raises(JobFacadeError) as excinfo:
        facade_obj.submit(_request(document=broken, scenario_set=["low", "base", "high"]))
    assert excinfo.value.code == "request_invalid"


def test_subprocess_runner_is_the_default(tmp_path):
    owner_root = tmp_path / "owner"
    owner_root.mkdir()
    facade_obj = JobFacade(owner_root, _deployment(tmp_path))
    runner = facade_obj._runner_factory(facade_obj.store, "rfjob-x")
    assert isinstance(runner, SubprocessStageRunner)
