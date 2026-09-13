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
               The suite's own output is persisted next to the ledger as
               ``weekly-run-<run_id>.log`` and that path is what the ledger's
               ``report_path`` names — before F-B01-10 it was a label with no
               file behind it, so a failed weekly run said only "exit 1" and
               could not be diagnosed.
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
    query_task_status,
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
# How much of the suite's output the persisted report keeps.  The tail is where
# pytest puts the failure summary; the full log can be megabytes.
REPORT_TAIL_CHARS = 20000


def _run_t3_suite(timeout: int = 3600) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["FILING_FETCH_E2E_DOWNLOAD"] = "1"
    # SYSTEM-context fix (GP-009, 2026-09-08): the isolated-wiki adapter config
    # resolves ${USERPROFILE}/Projects/... tokens and the download-tool gate
    # checks ~/Projects, but under the SYSTEM account Path.home() is the system
    # profile.  The suite therefore skipped every Sunday ("production download
    # tools not found") and the weekly window could never accumulate an ok run.
    # Derive the real profile from the repo location, exactly like the daily
    # runner derives the Dropbox root.
    profile = PROJECT_ROOT.parent.parent
    if profile.is_dir():
        env["USERPROFILE"] = str(profile)
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


def _write_suite_report(ledger_path: Path, run_id: str,
                        proc: subprocess.CompletedProcess, ok: bool,
                        status: str, detail: str) -> str:
    """Persist the suite's output beside the ledger; return the path recorded in it.

    F-B01-10 (2026-09-13): the weekly ledger recorded ``not-ok`` / ``exit 1`` while
    the subprocess output lived only in memory and ``report_path`` was a label with
    no file behind it, so that failure could not be diagnosed from the record at
    all.  The daily T2 runner already records a real report path; this makes the
    weekly loop do the same.
    """
    target = ledger_path.parent / f"weekly-run-{run_id}.log"
    output = (proc.stdout or "") + (proc.stderr or "")
    body = (
        f"run_id={run_id}\n"
        f"status={status} ok={ok} exit_code={proc.returncode}\n"
        f"detail={detail}\n"
        f"argv={sys.argv}\n"
        f"--- suite output, last {REPORT_TAIL_CHARS} chars ---\n"
        f"{output[-REPORT_TAIL_CHARS:]}\n"
    )
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    except OSError as exc:  # a diagnostic file must never break the assurance run
        print(f"warning: could not persist the suite report: {exc}", file=sys.stderr)
    return str(target)


def run_weekly(ledger_path: Path, alert_path: Path) -> int:
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    proc = _run_t3_suite()
    started = datetime.now(UTC).isoformat()
    ok, status, detail = _suite_outcome(proc)
    triplet = {"revenue": _head(PROJECT_ROOT),
               "filing": _head(FILING_ROOT),
               "wiki": _head(PROJECT_ROOT.parent / "company-wiki")}
    report = _write_suite_report(ledger_path, run_id, proc, ok, status, detail)
    write_ledger(ledger_path, run_id, started, triplet, ok, report)
    if status != "ok":
        append_alert(alert_path, {
            "at_utc": started, "run_id": run_id, "status": status,
            "reason": detail, "exit_code": proc.returncode,
        })
    print(f"run_id={run_id} ok={ok} status={status} detail={detail}")
    return proc.returncode


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
