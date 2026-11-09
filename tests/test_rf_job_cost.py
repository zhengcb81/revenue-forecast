"""OWNERPKG-REVENUE-FORECAST-01 unit tests — G-m8-RF-03: idempotency and cost.

Same idempotency_key returns the existing owner_job_id without re-orchestration;
cost/cost_state project real observations; limits_ref maps to the owner budget
table.
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
)

from test_rf_job_facade import (  # noqa: E402
    _deployment,
    _facade,
    _request,
    _recorded_requests,
)


def test_same_idempotency_key_returns_same_job_without_rerun(tmp_path):
    calls: list = []
    facade_obj, _ = _facade(tmp_path, calls=calls)
    first = facade_obj.submit(_request())
    request_count_after_first = len(first["job_view"]["stages"][0]["attempts"])
    runner_calls_before = len(_recorded_requests(calls))
    second = facade_obj.submit(_request())
    assert second["owner_job_id"] == first["owner_job_id"]
    assert second["job_view"]["idempotent_replay"] is True
    assert second["job_view"]["status"] == "succeeded"
    assert len(_recorded_requests(calls)) == runner_calls_before
    # the durable attempt records did not grow either
    job = facade_obj.store.load_job(first["owner_job_id"])
    assert len(job["stages"]["source"]["attempts"]) == request_count_after_first


def test_different_request_under_same_key_conflicts(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    facade_obj.submit(_request())
    with pytest.raises(JobFacadeError) as excinfo:
        facade_obj.submit(_request(company_query="Other Co"))
    assert excinfo.value.code == "idempotency_key_conflict"


def test_idempotency_key_never_stored_in_the_clear(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    result = facade_obj.submit(_request())
    job = facade_obj.store.load_job(result["owner_job_id"])
    job_text = json.dumps(job)
    assert '"idempotency_key"' not in job_text
    assert "unit-key-1" not in job_text
    index_text = (facade_obj.store.idempotency_file).read_text(encoding="utf-8")
    assert "unit-key-1" not in index_text


def test_limits_ref_unknown_rejected(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    with pytest.raises(JobFacadeError) as excinfo:
        facade_obj.submit(_request(limits_ref="no-such-ref"))
    assert excinfo.value.code == "limits_ref_unknown"


def test_budget_gate_stops_the_pipeline(tmp_path):
    calls: list = []
    owner_root = tmp_path / "owner"
    owner_root.mkdir()
    deployment_payload = {
        "schema_version": "rf-job-deployment/1",
        "python": sys.executable,
        "stages": {
            "source": {
                "filing_fetch_root": str(tmp_path / "ff"),
                "company_wiki_config": str(tmp_path / "ff" / "config.json"),
                "company_wiki_catalog_config": str(tmp_path / "wiki" / "catalog.yaml"),
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
        "limits": {"refs": {"tiny": {"max_cost_usd": "0.00", "max_wall_seconds": 0.01,
                                     "max_new_downloads": 0,
                                     "max_attempts_per_stage": 3}},
                   "default_ref": "tiny"},
    }
    deployment = Deployment(deployment_payload)

    def factory(store, owner_job_id):
        runner = FakeStageRunner(store, owner_job_id)
        calls.append(runner)
        return runner

    facade_obj = JobFacade(owner_root, deployment, runner_factory=factory)
    result = facade_obj.submit(_request(limits_ref="tiny"))
    view = result["job_view"]
    assert view["status"] == "failed"
    # the source attempt itself completed; the budget gate stopped the
    # pipeline before compute, and derive reports the recorded facts
    assert _recorded_requests(calls)[0]["stage"] == "source"
    assert len(_recorded_requests(calls)) == 1


def test_cost_known_on_success_and_unknown_on_gap(tmp_path):
    facade_obj, _ = _facade(tmp_path)
    result = facade_obj.submit(_request())
    view = result["job_view"]
    assert view["cost"] == {"currency": "USD", "value": "0.00"}
    assert view["cost_state"] == "known"

    behavior = {
        "compute": lambda stage, command: facade.AttemptOutcome(
            exit_code=None, killed=True, elapsed_seconds=120.0),
    }
    other_facade, _ = _facade(tmp_path, behavior=behavior)
    gap_result = other_facade.submit(_request(idempotency_key="gap-key"))
    gap_view = gap_result["job_view"]
    assert gap_view["cost_state"] == "unknown"
    assert gap_view["cost"] is None


def test_cost_not_applicable_before_any_attempt(tmp_path):
    owner_root = tmp_path / "owner"
    owner_root.mkdir()

    class DyingFactory:
        def __call__(self, store, owner_job_id):
            raise facade.SimulatedProcessDeath

    facade_obj = JobFacade(owner_root, _deployment(tmp_path), runner_factory=DyingFactory())
    with pytest.raises(facade.SimulatedProcessDeath):
        facade_obj.submit(_request(idempotency_key="queued-cost-key"))
    restarted, _ = _facade(tmp_path)
    job_id = restarted.store.list_job_ids()[0]
    view = restarted.get_status(job_id)["job_view"]
    assert view["status"] == "queued"
    assert view["cost_state"] == "not_applicable"
    assert view["cost"] is None


def test_deployment_rejects_negative_cost_limit(tmp_path):
    from rf_job_facade import Deployment as _D
    bad = {
        "schema_version": "rf-job-deployment/1",
        "python": sys.executable,
        "stages": {
            "source": {"filing_fetch_root": str(tmp_path / "ff"),
                       "company_wiki_config": str(tmp_path / "ff" / "config.json"),
                       "company_wiki_catalog_config": str(tmp_path / "wiki" / "catalog.yaml"),
                       "source_reader_receipt_version": "2.2",
                       "timeout_seconds": 60.0,
                       "request_template": {"schema_version": "2.0", "market": "CN",
                                            "document_kind": "annual_report",
                                            "fiscal_year": 2025, "mode": "exact",
                                            "filing_intent": "reuse_only"}},
            "compute": {"timeout_seconds": 120.0},
            "publication": {"timeout_seconds": 30.0},
        },
        "limits": {"refs": {"neg": {"max_cost_usd": "-1.00", "max_wall_seconds": 600,
                                    "max_new_downloads": 0, "max_attempts_per_stage": 3}},
                   "default_ref": "neg"},
    }
    with pytest.raises(JobFacadeError) as excinfo:
        _D(bad)
    assert excinfo.value.code == "deployment_config_invalid"


@pytest.mark.parametrize("companion_only", [False, True])
def test_uncertain_provider_effect_keeps_cost_unknown_and_resume_read_only(tmp_path, companion_only):
    calls = []
    behavior = {"source": lambda stage, command: facade.AttemptOutcome(
        exit_code=3, killed=False, elapsed_seconds=0.01)}
    running, _ = _facade(tmp_path, calls=calls, behavior=behavior, failure_stderr={
        "stage": "ensure", "calls": 2, "downloads": 0, "upstream_cause": {
            "schema_version": "filing-upstream-cause/1", "operation": "ensure",
            "code": "adapter_timeout", "provider_started": None, "usage_complete": None,
            "retry_scope": "caller_decision",
        },
    })
    if companion_only:
        running.deployment.source_request_template["companion_transcript"] = {"intent": "fetch_if_missing"}
    else:
        running.deployment.source_request_template["filing_intent"] = "fetch_if_missing"
    result = running.submit(_request())
    view = result["job_view"]
    assert view["status"] == "failed" and view["cost_state"] == "unknown" and view["cost"] is None
    assert view["allowed_actions"] == ["reconcile"]
    with pytest.raises(JobFacadeError):
        running.act(result["owner_job_id"], "resume")
    assert running.act(result["owner_job_id"], "reconcile")["job_view"]["cost_state"] == "unknown"
    assert [row["stage"] for row in _recorded_requests(calls)] == ["source"]


def test_confirmed_pre_provider_failure_can_resume_under_the_same_contract(tmp_path):
    calls = []
    first, _ = _facade(tmp_path, calls=calls, behavior={
        "source": lambda stage, command: facade.AttemptOutcome(exit_code=3, killed=False, elapsed_seconds=0.01)
    }, failure_stderr={
        "stage": "local_prepare", "calls": 2, "downloads": 0, "upstream_cause": {
            "schema_version": "filing-upstream-cause/1", "operation": "local_prepare",
            "code": "catalog_busy", "provider_started": False, "usage_complete": True,
            "retry_scope": "catalog_contention",
        },
    })
    first.deployment.source_request_template["filing_intent"] = "fetch_if_missing"
    result = first.submit(_request())
    assert result["job_view"]["allowed_actions"] == ["resume", "reconcile"]
    assert result["job_view"]["cost"] == {"currency": "USD", "value": "0.00"}
    restarted, _ = _facade(tmp_path, calls=calls)
    restarted.deployment.source_request_template["filing_intent"] = "fetch_if_missing"
    assert restarted.act(result["owner_job_id"], "resume")["job_view"]["status"] == "succeeded"
    assert [row["stage"] for row in _recorded_requests(calls)] == ["source", "source", "compute", "publication"]



@pytest.mark.parametrize("companion_can_fetch", [False, True])
def test_primary_reuse_does_not_supply_companion_cost(tmp_path, companion_can_fetch):
    running, _ = _facade(tmp_path)
    running.deployment.source_request_template["filing_intent"] = "fetch_if_missing"
    if companion_can_fetch:
        running.deployment.source_request_template["companion_transcript"] = {"intent": "fetch_if_missing"}
    view = running.submit(_request())["job_view"]
    assert view["status"] == "succeeded"
    assert view["cost_state"] == ("unknown" if companion_can_fetch else "known")
    assert view["cost"] == (None if companion_can_fetch else {"currency": "USD", "value": "0.00"})
