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

from daily_t2_schedule import (
    freshness_status,
    query_task_status,
    read_ledger,
    release_gate,
)
from monthly_broker_runner import DEFAULT_ALERT, DEFAULT_LEDGER, run as run_audit

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONTHLY_TASK = "revenue_monthly_broker"
MAX_AGE_DAYS = 35


def cmd_register(_args: argparse.Namespace) -> int:
    """Register a true calendar-monthly SYSTEM task (day 1, 05:00).

    ``New-ScheduledTaskTrigger`` has NO ``-Monthly`` parameter (its parameter
    sets are Once/Daily/Weekly/Startup/Logon), so the trigger is created with
    ``schtasks /sc MONTHLY`` and the power/wake settings are then applied with
    ``Set-ScheduledTask``.  The function self-verifies by querying the task
    afterwards, so a silently-unregistered task cannot look like success.
    """
    action = (
        f'"{sys.executable}" "{Path(__file__).resolve()}" run-monthly'
    )
    script = (
        f"schtasks /create /tn '{MONTHLY_TASK}' /tr '{action}' "
        "/sc MONTHLY /d 1 /st 05:00 /ru SYSTEM /rl HIGHEST /f | Out-Null; "
        "if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; "
        "$settings = New-ScheduledTaskSettingsSet "
        "-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun "
        "-StartWhenAvailable; "
        f"Set-ScheduledTask -TaskName '{MONTHLY_TASK}' "
        "-Settings $settings | Out-Null"
    )
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, errors="replace", timeout=60,
    )
    if proc.returncode != 0:
        print((proc.stderr or "register failed").strip(), file=sys.stderr)
        return proc.returncode or 1
    check = subprocess.run(
        ["schtasks", "/query", "/tn", MONTHLY_TASK],
        capture_output=True, text=True, errors="replace", timeout=60,
    )
    if check.returncode != 0:
        print(
            f"register reported success but task {MONTHLY_TASK} is not "
            "queryable — treating as failure",
            file=sys.stderr,
        )
        return 1
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
    status, detail = query_task_status(MONTHLY_TASK)
    print(f"task={MONTHLY_TASK} status={status} detail={detail}")
    return 0 if status == "registered" else 1


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
