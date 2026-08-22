"""ZR-903 acceptance tests: weekly / pre-release T3 scheduling.

  C1  weekly ledger mechanism — ``run-weekly`` invokes the T3 suite (opt-in)
      and writes ``weekly_manifest.json`` (run_id/started_at/triplet/ok).
  C2  freshness <=7d — fresh (<=7d & ok) / stale (>7d or not-ok) / missing
      (old green never fresh, AUD2-02).
  C3  blocked alerts + release blocking — stale/missing/not-ok append to the
      weekly alert journal and block the release gate; an ALL-SKIPPED T3
      suite (missing credentials/network) records BLOCKED, never a pass
      (CA-203 RED reversal).
  C4  release gate + verify — fresh+ok -> ready; subcommands positional.

Hermetic: fake T3 runner stub via monkeypatched ``_run_t3_suite``; the real
suite, real Task Scheduler and real downloads are never touched.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import weekly_t3_schedule as w3  # noqa: E402

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


def _fake_proc(returncode: int, out: str) -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=out, stderr="")


# ---------------------------------------------------------------------------
# C1 — weekly ledger mechanism
# ---------------------------------------------------------------------------


def test_c1_run_weekly_writes_ledger(tmp_path, monkeypatch):
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def fake_suite(timeout=3600):
        return _fake_proc(0, "3 passed in 5.00s")

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    rc = w3.run_weekly(ledger, alerts)
    assert rc == 0
    data = w3.read_ledger(ledger)
    assert data["ok"] is True
    assert data["latest_run_id"].startswith("20")
    assert not alerts.exists()


def test_c1_not_ok_still_recorded(tmp_path, monkeypatch):
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def fake_suite(timeout=3600):
        return _fake_proc(1, "1 failed, 2 passed")

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    rc = w3.run_weekly(ledger, alerts)
    assert rc != 0
    assert w3.read_ledger(ledger)["ok"] is False
    lines = alerts.read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(lines[0])["status"] == "not-ok"


# ---------------------------------------------------------------------------
# C2 — freshness <=7d (AUD2-02)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# C3 — blocked alerts + release blocking (CA-203 RED reversal)
# ---------------------------------------------------------------------------


def test_c3_all_skipped_suite_is_blocked_never_pass(tmp_path, monkeypatch):
    """Missing credentials/network -> fully skipped suite -> BLOCKED alert,
    release gate stays red (CA-203: never recorded as a pass)."""
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def fake_suite(timeout=3600):
        return _fake_proc(0, "5 skipped in 0.10s")

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    ok, status, detail = w3._suite_outcome(_fake_proc(0, "5 skipped in 0.10s"))
    assert status == "blocked"
    assert ok is False
    w3.run_weekly(ledger, alerts)
    lines = alerts.read_text(encoding="utf-8").strip().splitlines()
    entry = json.loads(lines[0])
    assert entry["status"] == "blocked"
    assert "skipped" in entry["reason"]
    ready, _g = w3.release_gate(ledger, now=NOW.isoformat(),
                                max_age_hours=WEEK_MAX_HOURS)
    assert ready is False


def test_c3_release_blocked_on_stale_and_missing(tmp_path):
    stale = tmp_path / "stale.json"
    w3.write_ledger(stale, "r", _old_iso(9), {}, True, "x")
    ready, _r = w3.release_gate(stale, now=NOW.isoformat(),
                                max_age_hours=WEEK_MAX_HOURS)
    assert ready is False
    ready2, _r2 = w3.release_gate(tmp_path / "absent.json", now=NOW.isoformat(),
                                  max_age_hours=WEEK_MAX_HOURS)
    assert ready2 is False


# ---------------------------------------------------------------------------
# C4 — release gate ready + positional subcommands
# ---------------------------------------------------------------------------


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
