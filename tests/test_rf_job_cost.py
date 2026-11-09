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
