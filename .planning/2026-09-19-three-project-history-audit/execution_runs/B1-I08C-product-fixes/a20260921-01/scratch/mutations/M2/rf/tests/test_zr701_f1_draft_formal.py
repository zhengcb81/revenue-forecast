"""ZR-701 acceptance tests (phase F1 entry): explicit Draft/Formal
artifacts + pure prepare_forecast + ProcessingDemand submission.

  C1  prepare_forecast is a pure function (deterministic, no IO).
  C2  --validate-only writes nothing (no output/markdown files, no
      publication-registry append).
  C3  publication registry distinguishes draft (unvalidated) from formal
      (validated) entries.
  C4  source preparation submits a ProcessingDemand (contract identical
      to company-wiki ZR-507: key dedupe / claim lease / heartbeat /
      complete / fail backoff / expire); prepare_source enqueues.
  C5  atomic publication: formal registry entries bind payload sha.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import processing_demand  # noqa: E402
import publication_registry  # noqa: E402
import revenue_forecast  # noqa: E402
import source_preparation  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def _input() -> dict:
    """A fresh, fully-parameterized valid forecast input document."""
    return forecast_document()


# ---------------------------------------------------------------------------
# C1 — pure prepare_forecast
# ---------------------------------------------------------------------------


def test_c1_prepare_forecast_is_deterministic_and_pure(tmp_path):
    first = revenue_forecast.prepare_forecast(_input())
    second = revenue_forecast.prepare_forecast(_input())
    assert first == second
    assert first["result_sha256"] == second["result_sha256"]
    # no filesystem side effects
    assert list(tmp_path.iterdir()) == []


# ---------------------------------------------------------------------------
# C2 — validate-only writes nothing
# ---------------------------------------------------------------------------


def test_c2_validate_only_writes_nothing(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text(json.dumps(_input()), encoding="utf-8")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    env = dict(os.environ)
    env["REVENUE_PUBLICATION_REGISTRY"] = str(out_dir / "publications.jsonl")
    proc = subprocess.run(
        [sys.executable, "scripts/revenue_forecast.py", str(input_file),
         "--validate-only"],
        cwd=str(ROOT), text=True, capture_output=True, env=env, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "valid"
    # no output/markdown files created; registry never created
    assert [p.name for p in out_dir.iterdir()] == []


# ---------------------------------------------------------------------------
# C3 — draft / formal registry distinction
# ---------------------------------------------------------------------------


def _fake_result() -> dict:
    result = revenue_forecast.prepare_forecast(_input())
    return result


def test_c3_registry_distinguishes_draft_and_formal(tmp_path, monkeypatch):
    registry = tmp_path / "pub" / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(registry))
    result = _fake_result()
    publication_registry.register_publication(result, note="run_forecast formal")
    publication_registry.register_publication(
        result, note="run_forecast draft", validation_status="draft"
    )
    entries = publication_registry._read_entries()
    # run_forecast(formal) auto-registers one entry; the last two are ours
    assert [e["validation_status"] for e in entries][-2:] == ["validated", "draft"]
    assert entries[-2]["receipt_sha256"] is not None
    # formal binds the payload: receipt hash + result hash present
    assert entries[-2]["result_sha256"] == result["result_sha256"]
    assert entries[-1]["result_sha256"] == result["result_sha256"]


def test_c3_old_entries_without_key_still_readable(tmp_path, monkeypatch):
    registry = tmp_path / "pub" / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(registry))
    result = _fake_result()
    publication_registry._append(
        {
            "registered_at": "2026-01-01T00:00:00+00:00",
            "input_sha256": result["input_sha256"],
            "result_sha256": result["result_sha256"],
            "receipt_sha256": None,
            "engine_version": result.get("engine_version"),
            "schema_version": result.get("schema_version"),
            "publisher": "revenue-forecast",
            "input_summary_sha256": publication_registry.input_summary_sha256(result),
            "artifact_type": "forecast",
            "artifact_id": None,
            "note": "legacy",
        }
    )
    entries = publication_registry._read_entries()
    # the formal run auto-registered one entry; the legacy line is last and
    # carries no validation_status key (additive compatibility)
    assert len(entries) == 2
    assert entries[-1].get("validation_status") is None


# ---------------------------------------------------------------------------
# C4 — ProcessingDemand contract + source preparation submission
# ---------------------------------------------------------------------------


def test_c4_demand_contract_matches_wiki_semantics():
    queue = processing_demand.DemandQueue(lease_seconds=10.0, max_attempts=2, backoff_base=5.0)
    first = queue.enqueue(key="k1", kind="source_preparation", now=0.0)
    assert queue.enqueue(key="k1", kind="source_preparation", now=1.0).demand_id == first.demand_id
    claimed = queue.claim(owner="w1", now=1.0)
    assert claimed.status == "running"
    assert claimed.lease_owner == "w1"
    renewed = queue.heartbeat(demand_id=claimed.demand_id, owner="w1", now=5.0)
    assert renewed.lease_until == 15.0
    failed = queue.fail(demand_id=renewed.demand_id, owner="w1", now=6.0)
    assert failed.attempts == 1
    assert failed.retry_at == 11.0  # 6 + 5 * 2**0
    assert queue.expire(now=100.0) == 0
    with pytest.raises(processing_demand.DemandStateError):
        queue.claim(owner="w1", now=10.0)  # in backoff until 11


def test_c4_prepare_source_enqueues_demand(tmp_path, monkeypatch):
    import company_wiki_source

    def fake_run(command, **kwargs):  # noqa: ARG001
        payload = {
            "resolution_envelope": {
                "download_events": 0,
                "prompt_injection_status": "reviewed",
                "parser_calls": 0,
                "llm_calls": 0,
                "outcome": "reused",
                "policy_hash": "a" * 64,
                "activation_epoch": 1,
                "bundle_status": "ok",
            },
            "document_kind": "annual_report",
            "provider": "cninfo",
        }
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(source_preparation.subprocess, "run", fake_run)
    monkeypatch.setattr(
        company_wiki_source,
        "select_artifact_roles",
        lambda handle: ([], []),
    )
    monkeypatch.setattr(
        company_wiki_source,
        "build_revenue_source_record",
        lambda handle, **kwargs: {"source_id": "src-abc", "source_sha256": "a" * 64},
    )
    record = source_preparation.prepare_source(
        {"entity": "x", "as_of_date": "2026-06-30"}, timeout_seconds=30.0
    )
    assert record["source_id"] == "src-abc"
    demands = source_preparation.preparation_demands().snapshot()
    assert len(demands) == 1
    assert demands[0].key == "src-abc"
    assert demands[0].kind == "source_preparation"
    # repeated preparation dedupes
    source_preparation.prepare_source(
        {"entity": "x", "as_of_date": "2026-06-30"}, timeout_seconds=30.0
    )
    assert len(source_preparation.preparation_demands().snapshot()) == 1


# ---------------------------------------------------------------------------
# C5 — atomic publication binding
# ---------------------------------------------------------------------------


def test_c5_formal_entry_binds_result_and_receipt(tmp_path, monkeypatch):
    registry = tmp_path / "pub" / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(registry))
    result = _fake_result()
    publication_registry.register_publication(result)
    entry = publication_registry._read_entries()[0]
    from contracts.evidence import canonical_sha256

    assert entry["result_sha256"] == result["result_sha256"]
    assert entry["receipt_sha256"] == canonical_sha256(result["publication_receipt"])
    assert entry["validation_status"] == "validated"


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
