"""GP-009 / CA-206 C3: monthly broker-cohort scheduling.

Mirrors the daily/weekly schedulers so the monthly soak window can actually
accumulate: ``run-monthly`` audits the frozen broker cohort read-only
(``monthly_broker_runner``), the registered SYSTEM task fires it on day 1 at
05:00, and ``verify`` fails closed when the ledger is missing, stale (>35d) or
not-ok.

  run-monthly   run the audit now (writes monthly_manifest.json + alerts)
  register      register the Windows Task Scheduler task (needs elevation)
  unregister    remove the scheduled task
  query         read-only registration status
  verify        registration + ledger freshness
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from daily_t2_schedule import freshness_status, read_ledger, release_gate
from monthly_broker_runner import DEFAULT_ALERT, DEFAULT_LEDGER, run as run_audit

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONTHLY_TASK = "revenue_monthly_broker"
MAX_AGE_DAYS = 35


def cmd_register(_args: argparse.Namespace) -> int:
    """Register via Register-ScheduledTask (SYSTEM, no password prompt)."""
    script = (
        "$action = New-ScheduledTaskAction -Execute "
        f"'{sys.executable}' -Argument '\"{Path(__file__).resolve()}\" run-monthly'; "
        "$trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 05:00; "
        "$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' "
        "-LogonType ServiceAccount -RunLevel Highest; "
        "$settings = New-ScheduledTaskSettingsSet "
        "-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun "
        "-StartWhenAvailable; "
        f"Register-ScheduledTask -TaskName '{MONTHLY_TASK}' "
        "-Action $action -Trigger $trigger -Principal $principal "
        "-Settings $settings -Force | Out-Null"
    )
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, errors="replace", timeout=60,
    )
    if proc.returncode != 0:
        print((proc.stderr or "register failed").strip(), file=sys.stderr)
        return proc.returncode or 1
    print(f"registered monthly task {MONTHLY_TASK}")
    return 0


def cmd_unregister(_args: argparse.Namespace) -> int:
    proc = subprocess.run(
        ["schtasks", "/delete", "/tn", MONTHLY_TASK, "/f"],
        capture_output=True, text=True, errors="replace", timeout=60,
    )
    if proc.returncode != 0:
        print((proc.stderr or "unregister failed").strip(), file=sys.stderr)
        return proc.returncode or 1
    print(f"unregistered {MONTHLY_TASK}")
    return 0


def cmd_query(_args: argparse.Namespace) -> int:
    proc = subprocess.run(
        ["schtasks", "/query", "/tn", MONTHLY_TASK, "/fo", "csv", "/v"],
        capture_output=True, text=True, errors="replace", timeout=60,
    )
    found = proc.returncode == 0
    print(f"task={MONTHLY_TASK} status={'registered' if found else 'missing'}")
    return 0 if found else 1


def cmd_verify(args: argparse.Namespace) -> int:
    ledger = read_ledger(Path(args.ledger))
    run_status, run_detail = freshness_status(
        ledger, max_age_hours=MAX_AGE_DAYS * 24
    )
    ready, gate = release_gate(Path(args.ledger), max_age_hours=MAX_AGE_DAYS * 24)
    print(f"last_run={run_status} ({run_detail})")
    print(f"release_gate={ready} ({gate})")
    return 0 if run_status == "fresh" else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Monthly broker-cohort scheduling (GP-009 / CA-206 C3)"
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--alerts", type=Path, default=DEFAULT_ALERT)
    parser.add_argument("--catalog", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run-monthly", "register", "unregister", "query", "verify"):
        sub.add_parser(name)
    args = parser.parse_args()
    if args.command == "run-monthly":
        catalog = args.catalog
        if catalog is None:
            from monthly_broker_runner import DEFAULT_CATALOG

            catalog = DEFAULT_CATALOG
        return run_audit(catalog, Path(args.ledger), Path(args.alerts))
    if args.command == "register":
        return cmd_register(args)
    if args.command == "unregister":
        return cmd_unregister(args)
    if args.command == "query":
        return cmd_query(args)
    return cmd_verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
