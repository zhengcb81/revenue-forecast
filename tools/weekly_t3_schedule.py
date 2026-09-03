"""ZR-903: weekly / pre-release T3 scheduling — <=7d freshness, blocked alerts.

Wraps the filing-fetch T3 real-download suite (``tests/test_e2e_download.py``,
opt-in via ``FILING_FETCH_E2E_DOWNLOAD=1``, temp wiki only) into a weekly
scheduled assurance loop, reusing the ZR-902 ledger machinery:

  run-weekly   run the T3 suite, write the weekly ledger
               (``assurance/runs/weekly_manifest.json``), judge freshness
               (<= 7d and ok -> fresh; older -> stale; absent -> missing),
               append an alert journal entry when not fresh, and record a
               BLOCKED status (never a pass) when the suite was entirely
               skipped (missing credentials/network — CA-203 RED).
  register     register a Windows Task Scheduler weekly task (deployment
               action; requires elevation) that invokes ``run-weekly``.
  query        read-only status of the scheduled task (exists / last run).
  unregister   remove the scheduled task (deployment action).
  verify       combined status: schedule + last run — AUD2-01/02/03 oracle.

The release gate is the ZR-902 pure function over the ledger: fresh + ok ->
ready; stale / missing / not-ok / all-skipped -> blocked.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from daily_t2_schedule import (
    append_alert,
    freshness_status,
    read_ledger,
    release_gate,
    write_ledger,
    _head,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FILING_ROOT = PROJECT_ROOT.parent / "filing-fetch"
T3_SUITE = FILING_ROOT / "tests" / "test_e2e_download.py"
WEEKLY_LEDGER = PROJECT_ROOT / "assurance" / "runs" / "weekly_manifest.json"
WEEKLY_ALERTS = PROJECT_ROOT / "assurance" / "runs" / "weekly_alert.jsonl"
WEEKLY_TASK = "revenue_weekly_t3"
MAX_AGE_DAYS = 7


def _run_t3_suite(timeout: int = 3600) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["FILING_FETCH_E2E_DOWNLOAD"] = "1"
    return subprocess.run(
        [sys.executable, "-B", "-m", "pytest", str(T3_SUITE), "-q", "--tb=short"],
        capture_output=True, text=True, errors="replace", timeout=timeout,
        env=env,
    )


def _suite_outcome(proc: subprocess.CompletedProcess) -> tuple[bool, str, str]:
    """(ok, status, detail) — an all-skipped suite is BLOCKED, never a pass."""
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return False, "not-ok", f"T3 suite exit {proc.returncode}"
    if "skipped" in out and "passed" not in out:
        return False, "blocked", "T3 suite fully skipped (credentials/network missing)"
    return True, "ok", "T3 suite passed"


def run_weekly(ledger_path: Path, alert_path: Path) -> int:
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    proc = _run_t3_suite()
    started = datetime.now(UTC).isoformat()
    ok, status, detail = _suite_outcome(proc)
    triplet = {"revenue": _head(PROJECT_ROOT),
               "filing": _head(FILING_ROOT),
               "wiki": _head(PROJECT_ROOT.parent / "company-wiki")}
    write_ledger(ledger_path, run_id, started, triplet, ok,
                 f"weekly-run-{run_id}")
    if status != "ok":
        append_alert(alert_path, {
            "at_utc": started, "run_id": run_id, "status": status,
            "reason": detail, "exit_code": proc.returncode,
        })
    print(f"run_id={run_id} ok={ok} status={status} detail={detail}")
    return proc.returncode


def cmd_register_weekly(_args: argparse.Namespace) -> int:
    """Register via PowerShell Register-ScheduledTask (no password prompt)."""
    script = (
        "$action = New-ScheduledTaskAction -Execute "
        f"'{sys.executable}' -Argument '\"{Path(__file__).resolve()}\" run-weekly'; "
        "$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 04:30; "
        "$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' "
        "-LogonType ServiceAccount -RunLevel Highest; "
        f"Register-ScheduledTask -TaskName '{WEEKLY_TASK}' "
        "-Action $action -Trigger $trigger -Principal $principal -Force | Out-Null"
    )
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, errors="replace", timeout=60,
    )
    if proc.returncode != 0:
        print((proc.stderr or "register failed").strip(), file=sys.stderr)
        return proc.returncode or 1
    print(f"registered weekly task {WEEKLY_TASK}")
    return 0


def cmd_query_weekly(_args: argparse.Namespace) -> int:
    proc = subprocess.run(
        ["schtasks", "/query", "/tn", WEEKLY_TASK, "/fo", "csv", "/v"],
        capture_output=True, text=True, errors="replace", timeout=60,
    )
    found = proc.returncode == 0
    print(f"task={WEEKLY_TASK} status={'registered' if found else 'missing'}")
    return 0 if found else 1


def cmd_unregister_weekly(_args: argparse.Namespace) -> int:
    proc = subprocess.run(
        ["schtasks", "/delete", "/tn", WEEKLY_TASK, "/f"],
        capture_output=True, text=True, errors="replace", timeout=60,
    )
    if proc.returncode != 0:
        print((proc.stderr or "unregister failed").strip(), file=sys.stderr)
        return proc.returncode or 1
    print(f"unregistered {WEEKLY_TASK}")
    return 0


def cmd_verify_weekly(args: argparse.Namespace) -> int:
    ledger = read_ledger(Path(args.ledger))
    run_status, run_detail = freshness_status(ledger, max_age_hours=MAX_AGE_DAYS * 24)
    ready, gate = release_gate(Path(args.ledger), max_age_hours=MAX_AGE_DAYS * 24)
    print(f"last_run={run_status} ({run_detail})")
    print(f"release_gate={ready} ({gate})")
    return 0 if run_status == "fresh" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Weekly T3 scheduling (ZR-903)")
    parser.add_argument("--ledger", type=Path, default=WEEKLY_LEDGER)
    parser.add_argument("--alerts", type=Path, default=WEEKLY_ALERTS)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run-weekly", "register", "unregister", "query", "verify"):
        sub.add_parser(name)
    args = parser.parse_args()
    if args.command == "run-weekly":
        return run_weekly(Path(args.ledger), Path(args.alerts))
    if args.command == "register":
        return cmd_register_weekly(args)
    if args.command == "unregister":
        return cmd_unregister_weekly(args)
    if args.command == "query":
        return cmd_query_weekly(args)
    return cmd_verify_weekly(args)


if __name__ == "__main__":
    raise SystemExit(main())
