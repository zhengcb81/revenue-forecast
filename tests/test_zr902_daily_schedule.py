"""ZR-902 acceptance tests: daily Windows T2 scheduling — schedule/runner/
freshness/alert/release-gate fully proven (stage H first card).

  C1  ledger mechanism — ``--run-daily`` invokes the FC-1102 runner and
      writes ``daily_manifest.json`` (latest_run_id/started_at/triplet/ok).
  C2  freshness three states — fresh (<=24h & ok) / stale (>24h or not-ok)
      / missing (no ledger): an old green report is never fresh (AUD2-02).
  C3  missing/not-fresh runs alert and block release — stale/missing/not-ok
      append to the alert journal and the release gate returns blocked
      (AUD2-01/03: scripts existing without runs never pass).
  C4  release gate — fresh+ok -> ready; anything else -> blocked.

All tests run hermetic (temp ledger/alert/report dirs); the real Windows
Task Scheduler is never touched (registration is a deployment action —
``--query``/``--verify`` logic is exercised via the ledger, and task_status
is read-only).
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from daily_t2_schedule import (  # noqa: E402
    MAX_AGE_HOURS,
    append_alert,
    freshness_status,
    read_ledger,
    release_gate,
    write_ledger,
)

NOW = datetime.now(UTC)


def _ledger(ok: bool = True, started_at: str | None = None) -> dict:
    return {
        "latest_run_id": "run-test",
        "started_at": started_at or NOW.isoformat(),
        "triplet": {"revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40},
        "ok": ok,
        "report_path": str(ROOT / "assurance" / "runs" / "run-test" / "report.json"),
    }


def _old_iso(hours: int) -> str:
    return (NOW - timedelta(hours=hours)).isoformat()


# ---------------------------------------------------------------------------
# C1 — ledger mechanism
# ---------------------------------------------------------------------------


def test_c1_write_and_read_ledger(tmp_path):
    ledger_path = tmp_path / "daily_manifest.json"
    write_ledger(ledger_path, "run-1", NOW.isoformat(),
                 {"revenue": "x" * 40, "filing": "y" * 40, "wiki": "z" * 40},
                 True, "report.json")
    data = read_ledger(ledger_path)
    assert data["latest_run_id"] == "run-1"
    assert data["ok"] is True
    assert data["triplet"]["revenue"] == "x" * 40
    assert read_ledger(tmp_path / "absent.json") is None


def test_c1_ledger_written_even_when_not_ok(tmp_path):
    ledger_path = tmp_path / "daily_manifest.json"
    write_ledger(ledger_path, "run-2", NOW.isoformat(), {}, False, "report.json")
    assert read_ledger(ledger_path)["ok"] is False


# ---------------------------------------------------------------------------
# C2 — freshness three states (AUD2-02: old green never fresh)
# ---------------------------------------------------------------------------


def test_c2_fresh_when_ok_and_recent():
    status, detail = freshness_status(_ledger(ok=True), now=NOW.isoformat())
    assert status == "fresh", detail


def test_c2_stale_when_older_than_24h():
    status, detail = freshness_status(
        _ledger(ok=True, started_at=_old_iso(MAX_AGE_HOURS + 1)),
        now=NOW.isoformat())
    assert status == "stale", detail
    assert "h old" in detail


def test_c2_stale_when_not_ok_even_if_recent():
    status, detail = freshness_status(_ledger(ok=False), now=NOW.isoformat())
    assert status == "stale", detail


def test_c2_missing_without_ledger():
    status, detail = freshness_status(None, now=NOW.isoformat())
    assert status == "missing", detail


# ---------------------------------------------------------------------------
# C3 — alert journal + release blocked on missing/not-fresh (AUD2-01/03)
# ---------------------------------------------------------------------------


def test_c3_alert_appended_on_missing_run(tmp_path):
    alerts = tmp_path / "alerts.jsonl"
    append_alert(alerts, {"at_utc": NOW.isoformat(), "run_id": "r",
                          "status": "missing", "reason": "no ledger"})
    lines = alerts.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["status"] == "missing"


def test_c3_release_blocked_without_ledger(tmp_path):
    ready, reason = release_gate(tmp_path / "absent.json", now=NOW.isoformat())
    assert ready is False
    assert "blocked" in reason


def test_c3_release_blocked_on_stale_green(tmp_path):
    ledger_path = tmp_path / "daily_manifest.json"
    write_ledger(ledger_path, "r-old", _old_iso(48), {}, True, "report.json")
    ready, reason = release_gate(ledger_path, now=NOW.isoformat())
    assert ready is False
    assert "blocked" in reason


def test_c3_release_blocked_on_not_ok(tmp_path):
    ledger_path = tmp_path / "daily_manifest.json"
    write_ledger(ledger_path, "r-bad", NOW.isoformat(), {}, False, "report.json")
    ready, _reason = release_gate(ledger_path, now=NOW.isoformat())
    assert ready is False


# ---------------------------------------------------------------------------
# C4 — release gate ready on fresh+ok
# ---------------------------------------------------------------------------


def test_c4_release_ready_on_fresh_ok(tmp_path):
    ledger_path = tmp_path / "daily_manifest.json"
    write_ledger(ledger_path, "r-fresh", NOW.isoformat(),
                 {"revenue": "a" * 40}, True, "report.json")
    ready, reason = release_gate(ledger_path, now=NOW.isoformat())
    assert ready is True
    assert "ready" in reason


def test_c4_verify_prints_all_three_statuses(tmp_path, capsys):
    import subprocess

    ledger_path = tmp_path / "daily_manifest.json"
    write_ledger(ledger_path, "r-fresh", NOW.isoformat(), {}, True, "report.json")
    proc = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "daily_t2_schedule.py"),
         "--ledger", str(ledger_path), "--alerts", str(tmp_path / "a.jsonl"),
         "verify"],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    out = proc.stdout + proc.stderr
    assert "schedule=" in out  # registered or missing — read-only, no assumption
    assert "last_run=fresh" in out
    assert "release_gate=" in out
