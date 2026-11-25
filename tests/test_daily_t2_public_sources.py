"""Current daily assurance uses the CWP public ports and local RF receipts."""
from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from tools import daily_t2_runner, daily_t2_schedule


def _reply(command, payload, *, status=0):
    raw = json.dumps(payload)
    if command[-1] == "status":
        return CompletedProcess(command, status, raw if not status else "", raw if status else "")
    return CompletedProcess(command, status, raw.encode() if not status else b"",
                            raw.encode() if status else b"")


def _counts(documents: int, active_locations: int) -> dict:
    return {"documents": documents, "active_locations": active_locations,
            "sources": documents, "missing_locations": 0}


def test_daily_catalog_health_accepts_current_sources_without_legacy_artifacts(tmp_path, monkeypatch):
    config = tmp_path / "config" / "source_catalog.yaml"
    invocations = []

    def owner(command, **kwargs):
        invocations.append(command[3:])
        return _reply(command, {
            **_counts(16, 14),
            "normalized_artifacts": 0,
            "producer_events": 473,
        })

    monkeypatch.setattr(daily_t2_runner.subprocess, "run", owner)
    report, code = daily_t2_runner.run_checks(config, "isolated")

    assert code == 0 and report["ok"] is True
    assert report["problems"] == []
    assert report["checks"]["catalog"]["active_locations"] == 14
    assert invocations == [["company_wiki.source_catalog.cli", "--config", str(config), "status"]]


def test_pin_missing_is_visible_even_when_other_catalog_sources_are_available(tmp_path, monkeypatch):
    config = tmp_path / "source_catalog.yaml"
    source = {
        "schema_version": "2.0", "document_id": "local-doc", "source_id": "original",
        "content_sha256": "a" * 64, "byte_size": 1024, "mime_type": "application/pdf",
    }
    invocations = []

    def owner(command, **kwargs):
        invocations.append(command[3:])
        if command[-1] == "status":
            return _reply(command, _counts(16, 14))
        assert json.loads(kwargs["input"]) == {
            "schema_version": "2.0", "source_refs": [source], "evidence_spans": [],
        }
        return _reply(command, {"schema_version": "2.0", "status": "not_found",
                                "reason": "unknown_source"}, status=2)

    monkeypatch.setattr(daily_t2_runner.subprocess, "run", owner)
    report, code = daily_t2_runner.run_checks(config, "missing", source_refs=[source])

    assert code == 1 and report["ok"] is False
    assert report["checks"]["source_verification"] == {"status": "not_found", "reason": "unknown_source"}
    assert invocations == [
        ["company_wiki.source_catalog.cli", "--config", str(config), "status"],
        ["company_wiki.source_catalog.source_export_v2_cli", "--config", str(config)],
    ]


@pytest.mark.parametrize("modified", [
    {}, {"source_id": "other"}, {"document_id": "other"}, {"content_sha256": "b" * 64},
    {"byte_size": 42}, {"byte_size": True}, {"mime_type": "text/html"},
])
def test_exact_verification_binds_each_returned_manifest(tmp_path, monkeypatch, modified):
    source = {"schema_version": "2.0", "document_id": "one", "source_id": "first",
              "content_sha256": "a" * 64, "byte_size": 1, "mime_type": "application/pdf"}
    second = {**source, "document_id": "two", "source_id": "second", "content_sha256": "c" * 64}

    def owner(command, **kwargs):
        if command[-1] == "status":
            return _reply(command, _counts(2, 3))
        assert json.loads(kwargs["input"])["source_refs"] == [source, second]
        return _reply(command, {"manifests": [
            {**second, "display_name": "extra owner field"},
            {**source, **modified},
        ], "export_id": "fixture-export"})

    monkeypatch.setattr(daily_t2_runner.subprocess, "run", owner)
    report, code = daily_t2_runner.run_checks(
        tmp_path / "source_catalog.yaml", "pin", source_refs=[source, second],
    )

    if modified:
        assert code == 2 and report["ok"] is False
        assert report["checks"]["source_verification"] == {
            "status": "unavailable", "reason": "owner_export_reference_mismatch",
        }
    else:
        assert code == 0 and report["ok"] is True
        assert report["checks"]["source_verification"]["source_count"] == 2


def test_empty_catalog_is_available_but_missing_database_preserves_owner_error(tmp_path, monkeypatch):
    config = tmp_path / "source_catalog.yaml"
    missing = False

    def owner(command, **kwargs):
        if not missing:
            return _reply(command, _counts(0, 0))
        return _reply(command, {
            "status": "failed", "error_type": "fatal",
            "error": "catalog does not exist (not created, not touched): fake-SECRET",
        }, status=1)

    monkeypatch.setattr(daily_t2_runner.subprocess, "run", owner)
    empty, code = daily_t2_runner.run_checks(config, "empty")
    assert code == 0 and empty["checks"]["catalog"]["status"] == "available"

    missing = True
    failed, code = daily_t2_runner.run_checks(config, "missing")
    assert code == 2 and failed["outcome"] == "blocked"
    assert failed["checks"]["catalog"] == {"status": "unavailable", "reason": "catalog_missing"}
    assert "fake-SECRET" not in json.dumps(failed)


def test_daily_schedule_joins_only_rf_owned_runner_and_reads_old_receipts(tmp_path, monkeypatch):
    run_root = tmp_path / "runs"
    archive = tmp_path / "archived-ledger.json"
    prior = {"latest_run_id": "before", "started_at": "2026-11-23T22:00:00+00:00",
             "triplet": {"revenue": "r", "filing": "f", "wiki": "w"},
             "ok": True, "report_path": "before/report.json", "observation_period": 27}
    archive.write_text(json.dumps(prior), encoding="utf-8")
    invocations = []

    def run(command, **kwargs):
        invocations.append(command)
        target = run_root / command[command.index("--run-id") + 1]
        target.mkdir(parents=True)
        (target / "report.json").write_text(
            json.dumps({"ok": True, "problems": [], "triplet": {"revenue": "r"}}),
            encoding="utf-8",
        )
        return CompletedProcess(command, 0, "", "")

    config = tmp_path / "source_catalog.yaml"
    ledger = tmp_path / "ledger.json"
    alerts = tmp_path / "alerts.jsonl"
    monkeypatch.setattr(daily_t2_schedule.subprocess, "run", run)
    code = daily_t2_schedule.run_daily(config, run_root, ledger, alerts)

    assert code == 0 and len(invocations) == 1
    assert Path(invocations[0][2]).name == "daily_t2_runner.py"
    assert invocations[0][invocations[0].index("--config") + 1] == str(config)
    assert not alerts.exists()
    assert daily_t2_schedule.read_ledger(ledger)["ok"] is True
    assert daily_t2_schedule.read_ledger(archive) == prior
