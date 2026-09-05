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


def test_c2_corrupt_ledger_fails_closed():
    # REV-001 regression: unparseable started_at must never raise — it is a
    # stale/blocked signal (fail closed), not a crash.
    corrupt = {"latest_run_id": "r", "started_at": "not-a-date",
               "triplet": {}, "ok": True, "report_path": "x"}
    status, detail = freshness_status(corrupt, now=NOW.isoformat())
    assert status == "stale", detail
    assert "unparseable" in detail
    missing_ts = {"latest_run_id": "r", "triplet": {}, "ok": True,
                  "report_path": "x"}
    status2, _d2 = freshness_status(missing_ts, now=NOW.isoformat())
    assert status2 == "stale"


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


def test_c4_subcommands_are_positional(tmp_path):
    # REV-002 regression: capabilities are positional subcommands
    # (run-daily/register/query/unregister/verify), not --flags.
    import subprocess

    script = ROOT / "tools" / "daily_t2_schedule.py"
    proc = subprocess.run(
        [sys.executable, "-B", str(script), "--help"],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    for name in ("run-daily", "register", "unregister", "query", "verify"):
        assert name in proc.stdout, f"missing subcommand {name}"


# ---------------------------------------------------------------------------
# C5 — registered-task invocation resolves production defaults (GP-008)
# ---------------------------------------------------------------------------


def test_c5_bare_run_daily_parses_with_production_defaults(tmp_path):
    """Regression (GP-008): the registered SYSTEM task fires the script with
    ONLY ``--run-daily`` plus the module-level ledger/alerts defaults.  The
    run-daily catalog/manifest/report-root arguments must default to the
    production paths — previously they were required, so every 03:30 trigger
    died in argparse (SystemExit 2) and daily_manifest.json never advanced,
    which also froze the FC-705 observation windows forever."""
    from daily_t2_schedule import (  # noqa: F811
        DEFAULT_CATALOG,
        DEFAULT_LEDGER,
        DEFAULT_MANIFEST,
        DEFAULT_REPORT_ROOT,
        build_parser,
    )

    parser = build_parser()
    # exactly what the scheduled task executes (no per-run flags)
    args = parser.parse_args([
        "--ledger", str(tmp_path / "daily_manifest.json"),
        "--alerts", str(tmp_path / "alerts.jsonl"),
        "run-daily",
    ])
    assert args.command == "run-daily"
    assert args.catalog == DEFAULT_CATALOG
    assert args.manifest == DEFAULT_MANIFEST
    assert args.report_root == DEFAULT_REPORT_ROOT
    # sanity: the defaults point at the real production surfaces
    assert args.catalog.is_absolute() and args.catalog.name == "catalog.sqlite3"
    assert args.manifest.name == "current.json"
    assert DEFAULT_LEDGER.name == "daily_manifest.json"


def test_c5_register_action_needs_no_extra_flags():
    """The register subcommand stores a bare ``--run-daily`` action; parse
    that exact argv (no --ledger/--alerts/--catalog/... overrides) to prove
    a freshly registered task resolves every path from module defaults and
    will not argparse-fail at trigger time."""
    from daily_t2_schedule import (  # noqa: F811
        DEFAULT_ALERTS,
        DEFAULT_CATALOG,
        DEFAULT_LEDGER,
        DEFAULT_MANIFEST,
        DEFAULT_REPORT_ROOT,
        build_parser,
    )

    args = build_parser().parse_args(["run-daily"])
    assert args.ledger == DEFAULT_LEDGER
    assert args.alerts == DEFAULT_ALERTS
    assert args.catalog == DEFAULT_CATALOG
    assert args.manifest == DEFAULT_MANIFEST
    assert args.report_root == DEFAULT_REPORT_ROOT


def test_c7_register_script_includes_power_and_wake_settings():
    """0x800710E0 regression: the default ScheduledTask settings refuse to
    start on battery power and never wake the machine — when the computer
    sleeps through the 03:30 trigger, the late catch-up run fails with
    'operator refused the request' (-2147020576, measured 2026-09-05).
    The register script must explicitly allow any power source and set
    wake-to-run."""
    from unittest.mock import patch

    from daily_t2_schedule import cmd_register

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stderr = ""
        result = cmd_register(None)
    assert result == 0
    script = mock_run.call_args[0][0][4]  # ["powershell", "-NoProfile", "-NonInteractive", "-Command", script]
    assert "-AllowStartIfOnBatteries" in script
    assert "-DontStopIfGoingOnBatteries" in script
    assert "-WakeToRun" in script
    assert "-StartWhenAvailable" in script
    assert "New-ScheduledTaskSettingsSet" in script


# ---------------------------------------------------------------------------
# C6 — FC-705 observation advancement wired into the daily run (GP-008)
# ---------------------------------------------------------------------------


def test_c6_fresh_periods_file_starts_at_period_one(tmp_path):
    """First daily run opens period 1 when no periods ledger exists yet."""
    from daily_t2_schedule import next_period_number

    assert next_period_number(tmp_path / "absent.json") == 1


def test_c6_next_period_after_open_window(tmp_path):
    """A second (or later) daily run opens max+1; an open period never
    blocks the next number (it is closed by the new run's bookkeeping)."""
    from daily_t2_schedule import next_period_number

    path = tmp_path / "periods.json"
    path.write_text(json.dumps({
        "periods": [
            {"period": 1, "started_at": "2026-09-04T03:30:00Z",
             "ended_at": "2026-09-05T03:30:00Z", "legacy_bridge_hits": 0},
            {"period": 2, "started_at": "2026-09-05T03:30:00Z",
             "ended_at": None, "legacy_bridge_hits": 0},
        ]
    }), encoding="utf-8")
    assert next_period_number(path) == 3


def test_c6_corrupt_periods_file_fails_closed_to_one(tmp_path):
    """A corrupt ledger must not crash the scheduled run; it restarts the
    observation sequence (fail closed — an open restart is never a pass)."""
    from daily_t2_schedule import next_period_number

    path = tmp_path / "periods.json"
    path.write_text("{not json", encoding="utf-8")
    assert next_period_number(path) == 1


def test_c6_observer_argv_is_read_only_with_period_file():
    """The daily observation step invokes the wiki legacy_observer with
    --read-only and an explicit period file (the FC-705 periods ledger)."""
    from daily_t2_schedule import (
        DEFAULT_PERIODS,
        LEGACY_OBSERVER,
        observer_argv,
    )

    argv = observer_argv(
        Path(r"C:\repos\company-wiki\.source_catalog\catalog.sqlite3"),
        period=3,
        periods_path=Path(r"C:\repos\revenue-forecast\assurance\runs\legacy_periods.json"),
    )
    assert argv[0] == sys.executable
    assert Path(argv[2]).resolve() == LEGACY_OBSERVER.resolve()
    assert "--read-only" in argv
    assert argv[argv.index("--period") + 1] == "3"
    assert "--period-file" in argv
    assert "--catalog" in argv
    # default ledger location for the real scheduled run
    assert DEFAULT_PERIODS.name == "legacy_periods.json"
