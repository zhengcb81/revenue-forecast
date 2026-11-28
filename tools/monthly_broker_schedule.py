"""Inspect or remove the legacy GP-009 monthly broker task and its history.

  run-monthly   report the retirement without refreshing prior results
  register      report the retirement without registering a new task
  unregister    remove the existing scheduled task
  query         read-only registration status
  verify        historical ledger freshness
"""

from __future__ import annotations

if __package__:
    from .rf_owner_runtime import DiagnosticParser, Invocation, exit_cli, observed_entry
else:
    from rf_owner_runtime import DiagnosticParser, Invocation, exit_cli, observed_entry

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
from monthly_broker_runner import DEFAULT_ALERT, DEFAULT_LEDGER, report_retired

MONTHLY_TASK = "revenue_monthly_broker"
MAX_AGE_DAYS = 35


def cmd_register(_args: argparse.Namespace) -> int:
    return report_retired()


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


@observed_entry
def main(*, runtime: Invocation) -> int:
    parser = DiagnosticParser(
        description="Legacy monthly broker task and history (GP-009 / CA-206 C3)"
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--alerts", type=Path, default=DEFAULT_ALERT)
    parser.add_argument("--catalog", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("run-monthly", "register", "unregister", "query", "verify"):
        sub.add_parser(name)
    args = parser.parse_args()
    if args.command == "run-monthly":
        return report_retired()
    if args.command == "register":
        return cmd_register(args)
    if args.command == "unregister":
        return cmd_unregister(args)
    if args.command == "query":
        return cmd_query(args)
    return cmd_verify(args)


if __name__ == "__main__":
    raise SystemExit(exit_cli(main))
