"""ZR-903 weekly ledger, freshness and public receipt recovery tests."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import weekly_t3_schedule as w3  # noqa: E402
from weekly_t3_assurance import CASE_NAMES, WeeklyT3Result, read_weekly_t3  # noqa: E402

NOW = datetime.now(UTC)
WEEK_MAX_HOURS = 7 * 24


def _ledger(ok: bool = True, started_at: str | None = None) -> dict:
    return {
        "latest_run_id": "weekly-test",
        "started_at": started_at or NOW.isoformat(),
        "triplet": {"revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40},
        "ok": ok,
        "report_path": "weekly-run-test",
    }


def _old_iso(days: int) -> str:
    return (NOW - timedelta(days=days)).isoformat()


def test_c2_fresh_within_week():
    status, detail = w3.freshness_status(_ledger(ok=True), now=NOW.isoformat(),
                                         max_age_hours=WEEK_MAX_HOURS)
    assert status == "fresh", detail


def test_c2_stale_after_week():
    status, detail = w3.freshness_status(
        _ledger(ok=True, started_at=_old_iso(8)),
        now=NOW.isoformat(), max_age_hours=WEEK_MAX_HOURS)
    assert status == "stale", detail


def test_c2_stale_when_not_ok():
    status, _d = w3.freshness_status(_ledger(ok=False), now=NOW.isoformat(),
                                     max_age_hours=WEEK_MAX_HOURS)
    assert status == "stale"


def test_c2_missing():
    status, _d = w3.freshness_status(None, now=NOW.isoformat(),
                                     max_age_hours=WEEK_MAX_HOURS)
    assert status == "missing"


def test_c3_release_blocked_on_stale_and_missing(tmp_path):
    stale = tmp_path / "stale.json"
    w3.write_ledger(stale, "r", _old_iso(9), {}, True, "x")
    ready, _r = w3.release_gate(stale, now=NOW.isoformat(),
                                max_age_hours=WEEK_MAX_HOURS)
    assert ready is False
    ready2, _r2 = w3.release_gate(tmp_path / "absent.json", now=NOW.isoformat(),
                                  max_age_hours=WEEK_MAX_HOURS)
    assert ready2 is False


def test_c4_release_ready_on_fresh_ok(tmp_path):
    ledger = tmp_path / "weekly_manifest.json"
    w3.write_ledger(ledger, "r", NOW.isoformat(), {}, True, "x")
    ready, reason = w3.release_gate(ledger, now=NOW.isoformat(),
                                    max_age_hours=WEEK_MAX_HOURS)
    assert ready is True
    assert "ready" in reason


def test_c4_subcommands_positional():
    proc = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "weekly_t3_schedule.py"),
         "--help"],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    for name in ("run-weekly", "register", "unregister", "query", "verify"):
        assert name in proc.stdout, f"missing subcommand {name}"


def test_repeated_lookup_does_not_extend_owner_freshness(tmp_path, monkeypatch):
    completed = NOW - timedelta(days=7)
    source = {
        "schema_version": "ff-t3-assurance/1", "run_id": "original-run",
        "owner_revision": "a" * 40, "mode": "live", "state": "completed",
        "completed_at": completed.isoformat(),
        "cases": {name: {"outcome": "passed", "evidence_ref": f"ff-t3/original-run/{name}",
                          "reason": None} for name in CASE_NAMES},
    }
    commands = []

    def get(command, **options):
        assert "env" not in options
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, json.dumps(source), "")

    monkeypatch.setattr(subprocess, "run", get)
    first = read_weekly_t3(tmp_path, now=NOW)
    second = read_weekly_t3(tmp_path, now=NOW + timedelta(seconds=1))
    assert first.ok and not second.ok and second.detail == "owner_receipt_stale"
    assert first.ledger_time == second.ledger_time == completed.isoformat()
    assert all(command[3:] == ["get", "--latest"] for command in commands)


def test_diagnostic_write_failure_preserves_owner_verdict_ledger_and_alert(tmp_path, monkeypatch):
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"
    real_write = w3.write_json
    result = WeeklyT3Result("not-ok", "owner_case_failed", NOW.isoformat())

    def selective(path, *args, **kwargs):
        if path.suffix == ".log":
            raise OSError("LOCAL_PATH_PRIVATE_SENTINEL")
        return real_write(path, *args, **kwargs)

    monkeypatch.setattr(w3, "read_weekly_t3", lambda *args, **kwargs: result)
    monkeypatch.setattr(w3, "write_json", selective)
    assert w3.run_weekly(ledger, alerts) == 1
    loaded = w3.read_ledger(ledger)
    assert loaded["ok"] is False
    assert loaded["report_path"].endswith(".log (NOT WRITTEN: OSError)")
    assert "LOCAL_PATH_PRIVATE_SENTINEL" not in ledger.read_text(encoding="utf-8")
    assert json.loads(alerts.read_bytes())["status"] == "not-ok"
    original = w3.get_run(ledger, "weekly", loaded["latest_run_id"])
    assert original["state"] == "failed" and original["diagnostic"]["reason"] == "owner_case_failed"


def test_owner_timeout_replaces_green_ledger_with_named_blocker(tmp_path, monkeypatch):
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"
    previous = _ledger(ok=True)
    ledger.write_text(json.dumps(previous), encoding="utf-8")

    def timeout(command, **_kwargs):
        raise subprocess.TimeoutExpired(command, timeout=30, stderr=b"UNSAFE_RAW_FF_ERR")

    monkeypatch.setattr(subprocess, "run", timeout)
    assert w3.run_weekly(ledger, alerts, filing_fetch_root=tmp_path / "owner") == 124
    current = w3.read_ledger(ledger)
    assert not current["ok"] and current["latest_run_id"] != previous["latest_run_id"]
    report = json.loads(ledger.with_name(current["report_path"]).read_bytes())
    assert (report["status"], report["detail"]) == ("blocked", "owner_lookup_timeout")
    assert "UNSAFE_RAW_FF_ERR" not in json.dumps(report)
    assert json.loads(alerts.read_bytes())["exit_code"] == 124


def test_historical_ledger_and_text_report_are_readable_without_rewriting(tmp_path):
    ledger = tmp_path / "weekly_manifest.json"
    previous = {**_ledger(ok=True), "report_path": "weekly-run-before.log",
                "observation_period": 29}
    old_report = ledger.with_name(previous["report_path"])
    ledger.write_text(json.dumps(previous), encoding="utf-8")
    old_report.write_text("status=ok\nold pytest output\n", encoding="utf-8")
    exact = (ledger.read_bytes(), old_report.read_bytes())
    assert w3.read_ledger(ledger) == previous
    assert w3.release_gate(ledger, now=NOW.isoformat(), max_age_hours=WEEK_MAX_HOURS)[0]
    assert (ledger.read_bytes(), old_report.read_bytes()) == exact
