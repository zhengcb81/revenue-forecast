"""ZR-903: consume existing FF T3 assurance and keep RF's weekly gate readable."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if __package__:
    from .daily_t2_schedule import (
        append_alert,
        freshness_status,
        query_task_status,
        read_ledger,
        release_gate,
        write_ledger,
    )
    from .weekly_t3_assurance import FILING_ROOT, MAX_AGE_DAYS, add_owner_options, read_weekly_t3, receipt_label
else:
    from daily_t2_schedule import (
        append_alert,
        freshness_status,
        query_task_status,
        read_ledger,
        release_gate,
        write_ledger,
    )
    from weekly_t3_assurance import FILING_ROOT, MAX_AGE_DAYS, add_owner_options, read_weekly_t3, receipt_label

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from rf_assurance_history import AssuranceRun, get_run, path_reference, show_run, write_json  # noqa: E402

WEEKLY_LEDGER = PROJECT_ROOT / "assurance" / "runs" / "weekly_manifest.json"
WEEKLY_ALERTS = PROJECT_ROOT / "assurance" / "runs" / "weekly_alert.jsonl"
WEEKLY_TASK = "revenue_weekly_t3"


def _write_report(ledger_path: Path, run_id: str, body: dict) -> str:
    target = ledger_path.parent / f"weekly-run-{run_id}.log"
    try:
        write_json(target, body)
    except OSError as exc:
        print(f"warning: could not persist the weekly receipt report: {type(exc).__name__}",
              file=sys.stderr)
        return f"{target.name} (NOT WRITTEN: {type(exc).__name__})"
    return target.name


def run_weekly(
    ledger_path: Path,
    alert_path: Path,
    *,
    filing_fetch_root: Path = FILING_ROOT,
    receipts_dir: Path | None = None,
    owner_run_id: str | None = None,
) -> int:
    entered = Path(__file__)
    attempt = AssuranceRun(
        ledger_path, "weekly", sources=(entered, entered.with_name("weekly_t3_assurance.py")),
        request={"filing_fetch_root_ref": path_reference(filing_fetch_root),
                 "receipts_dir_ref": path_reference(receipts_dir) if receipts_dir else None,
                 "owner_run_id": receipt_label(owner_run_id)},
    )
    run_id = attempt.run_id
    result = read_weekly_t3(filing_fetch_root, receipts_dir=receipts_dir, owner_run_id=owner_run_id)
    exit_code = 124 if result.detail == "owner_lookup_timeout" else result.exit_code
    attempt.finish(exit_code=exit_code, outcome=result.status,
                   diagnostic={"reason": result.detail, "owner_exit_code": result.owner_exit_code,
                               "owner_run_id": (result.receipt or {}).get("run_id"),
                               "cause_chain": list(result.cause_chain)})
    report = _write_report(ledger_path, run_id, result.report(run_id))
    filing_revision = (result.receipt or {}).get("owner_revision")
    triplet = {"filing": filing_revision} if filing_revision is not None else {}
    try:
        write_ledger(ledger_path, run_id, result.ledger_time, triplet, result.ok, report)
    except OSError as exc:
        print(f"warning: could not refresh weekly ledger {run_id} ({type(exc).__name__})", file=sys.stderr)
    if not result.ok:
        try:
            append_alert(alert_path, {
                "at_utc": result.observed_at,
                "run_id": run_id,
                "status": result.status,
                "reason": result.detail,
                "exit_code": exit_code,
                "owner_run_id": (result.receipt or {}).get("run_id"),
            })
        except OSError as exc:
            print(f"warning: could not record weekly alert {run_id} ({type(exc).__name__})", file=sys.stderr)
    print(f"run_id={run_id} ok={result.ok} status={result.status} detail={result.detail}")
    return exit_code


def cmd_register_weekly(_args: argparse.Namespace) -> int:
    """Register via PowerShell Register-ScheduledTask (no password prompt).

    Power/wake fix (0x800710E0, diagnosed 2026-09-05): explicit settings
    allow any power source, wake the computer to run on schedule, and
    StartWhenAvailable catches up a missed Sunday run on the next boot.
    """
    script = (
        "$action = New-ScheduledTaskAction -Execute "
        f"'{sys.executable}' -Argument '\"{Path(__file__).resolve()}\" run-weekly'; "
        "$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 04:30; "
        "$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' "
        "-LogonType ServiceAccount -RunLevel Highest; "
        "$settings = New-ScheduledTaskSettingsSet "
        "-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun "
        "-StartWhenAvailable; "
        f"Register-ScheduledTask -TaskName '{WEEKLY_TASK}' "
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
    print(f"registered weekly task {WEEKLY_TASK}")
    return 0


def cmd_query_weekly(_args: argparse.Namespace) -> int:
    status, detail = query_task_status(WEEKLY_TASK)
    print(f"task={WEEKLY_TASK} status={status} detail={detail}")
    return 0 if status == "registered" else 1


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
    attempt = get_run(Path(args.ledger), "weekly")
    if attempt is not None and attempt["state"] == "started":
        print(f"latest_attempt={attempt['run_id']} completion=unconfirmed")
    # release_gate comes from the shared ZR-902 machinery and words itself for the
    # DAILY T2 loop (B-VR903-08); say which gate this is.
    print(f"release_gate={ready} ({gate.replace('daily T2', 'weekly T3')})")
    return 0 if run_status == "fresh" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Weekly T3 scheduling (ZR-903)")
    parser.add_argument("--ledger", type=Path, default=WEEKLY_LEDGER)
    parser.add_argument("--alerts", type=Path, default=WEEKLY_ALERTS)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run-weekly")
    add_owner_options(run)
    sub.add_parser("get-run", help="read from the RF assurance history").add_argument("--run-id")
    for name in ("register", "unregister", "query", "verify"):
        sub.add_parser(name)
    args = parser.parse_args()
    if args.command == "run-weekly":
        return run_weekly(
            args.ledger, args.alerts, filing_fetch_root=args.filing_fetch_root,
            receipts_dir=args.receipts_dir, owner_run_id=args.owner_run_id,
        )
    if args.command == "get-run":
        return show_run(args.ledger, "weekly", args.run_id)
    if args.command == "register":
        return cmd_register_weekly(args)
    if args.command == "unregister":
        return cmd_unregister_weekly(args)
    if args.command == "query":
        return cmd_query_weekly(args)
    return cmd_verify_weekly(args)


if __name__ == "__main__":
    raise SystemExit(main())
