"""Schedule RF's read-only daily health check and retain its local results.

The scheduled task delegates only to the RF runner. The optional exact source
pins use the CWP public verifier. Existing daily ledgers still load normally.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

if __package__:
    from .daily_t2_runner import DEFAULT_CONFIG, DEFAULT_REPORT_ROOT
else:
    from daily_t2_runner import DEFAULT_CONFIG, DEFAULT_REPORT_ROOT

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / "tools" / "daily_t2_runner.py"
DEFAULT_LEDGER = PROJECT_ROOT / "assurance" / "runs" / "daily_manifest.json"
DEFAULT_ALERTS = PROJECT_ROOT / "assurance" / "runs" / "daily_alert.jsonl"
TASK_NAME = "revenue_daily_t2"
MAX_AGE_HOURS = 24

# Outcome vocabulary shared with the weekly T3 loop (owner decision 2026-09-13: the
# daily run gets the SAME split).  ``not-ok`` is a statement about the product;
# ``blocked`` says the run could not be evaluated here.  The two tuples are mirrored
# in tools/weekly_t3_schedule.py on purpose (that module imports this one, so a shared
# constant here would invert the dependency); tests/test_zr902b_run_outcome.py pins
# that the two vocabularies are IDENTICAL, so a change in one place cannot drift.
ENVIRONMENT_SENTINEL = "T2-RUN-COULD-NOT-RUN"
ENVIRONMENT_MARKERS = (
    "not found",
    "no such file",
    "filenotfounderror",
    "winerror 2",
    "errno 2",
    "timeoutexpired",
    "connectionerror",
    "connection",
    "timed out",
    "network",
    "sslerror",
    "socket.gaierror",
    "urlerror",
    "httperror",
    "credentials",
    "unauthorized",
    "permission denied",
    "permissionerror",
    "not installed",
)

def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _iso_to_utc(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)


def write_ledger(path: Path, run_id: str, started_at: str, triplet: dict,
                 ok: bool, report_path: str,
                 observation_period: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "latest_run_id": run_id,
        "started_at": started_at,
        "triplet": triplet,
        "ok": ok,
        "report_path": report_path,
    }
    if observation_period is not None:
        payload["observation_period"] = observation_period
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_ledger(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def freshness_status(ledger: dict | None, *, now: str | None = None,
                     max_age_hours: int = MAX_AGE_HOURS) -> tuple[str, str]:
    """fresh / stale / missing — an old green report is never fresh."""
    if ledger is None:
        return "missing", "no daily run ledger (schedule never ran)"
    try:
        started = _iso_to_utc(str(ledger.get("started_at", "")))
    except (ValueError, TypeError):
        return "stale", "ledger started_at unparseable (corrupt ledger)"
    now_dt = _iso_to_utc(now) if now else datetime.now(UTC)
    if not ledger.get("ok"):
        return "stale", "latest daily run reported not-ok"
    age = now_dt - started
    if age > timedelta(hours=max_age_hours):
        return "stale", f"latest run {int(age.total_seconds() // 3600)}h old (> {max_age_hours}h)"
    return "fresh", f"latest run ok, {int(age.total_seconds() // 60)}m old"


def append_alert(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def release_gate(ledger_path: Path, *, now: str | None = None,
                 max_age_hours: int = MAX_AGE_HOURS) -> tuple[bool, str]:
    """Release consumption gate: fresh + ok -> ready, else blocked."""
    status, detail = freshness_status(read_ledger(ledger_path), now=now,
                                      max_age_hours=max_age_hours)
    if status == "fresh":
        return True, "daily T2 gate ready"
    return False, f"daily T2 gate blocked: {detail}"


def _read_runner_report(report_path: Path) -> dict | None:
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def run_outcome(
    proc: subprocess.CompletedProcess, report: dict | None,
) -> tuple[bool, str, str]:
    """Read today's native result, with legacy subprocess failure attribution."""
    if report is not None:
        problems = report.get("problems") or []
        if proc.returncode == 0 and report.get("ok") is True and not problems:
            return True, "ok", "Daily source assurance passed"
        detail = "; ".join(str(item) for item in problems) or "runner reported failure"
        if report.get("outcome") == "blocked":
            return False, "blocked", detail
        return False, "not-ok", f"T2 runner produced a verdict: {detail}"

    output = ((proc.stdout or "") + (proc.stderr or "")).lower()
    if ENVIRONMENT_SENTINEL.lower() in output:
        return False, "blocked", f"runner reported sentinel {ENVIRONMENT_SENTINEL}; exit {proc.returncode}"
    markers = [marker for marker in ENVIRONMENT_MARKERS if marker in output]
    if markers:
        return False, "blocked", (
            f"no verdict was produced (runner exit {proc.returncode}; "
            f"matched: {', '.join(markers)}) - heuristic"
        )
    return False, "not-ok", f"T2 runner failed without a report (exit {proc.returncode})"


def run_daily(
    catalog_config: Path, report_root: Path, ledger_path: Path, alert_path: Path,
    *, source_ref_files: tuple[Path, ...] = (),
) -> int:
    started = _now_iso()
    run_id = datetime.fromisoformat(started).strftime("%Y%m%dT%H%M%S%fZ")
    report_path = report_root / run_id / "report.json"
    argv = [
        sys.executable, "-B", str(RUNNER), "--config", str(catalog_config),
        "--report-root", str(report_root), "--run-id", run_id,
    ]
    for path in source_ref_files:
        argv.extend(("--source-ref", str(path)))
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, errors="replace", timeout=600)
    except (OSError, subprocess.TimeoutExpired) as error:
        proc = subprocess.CompletedProcess(
            argv, 2, "", f"{ENVIRONMENT_SENTINEL}: {type(error).__name__}",
        )
    report = _read_runner_report(report_path)
    ok, outcome, detail = run_outcome(proc, report)
    if report is None:
        report = {"run_id": run_id, "ok": ok, "outcome": outcome, "checks": {},
                  "problems": [detail], "triplet": {}}
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False) + "\n", encoding="utf-8")
    write_ledger(ledger_path, run_id, started, report.get("triplet", {}), ok, str(report_path))
    status, freshness = freshness_status(read_ledger(ledger_path), now=started)
    if not ok:
        append_alert(alert_path, {
            "at_utc": started, "run_id": run_id, "status": status,
            "outcome": outcome, "reason": f"{detail} (ledger: {freshness})",
            "exit_code": proc.returncode or 1,
        })
    print(f"run_id={run_id} ok={ok} outcome={outcome} status={status} detail={detail}")
    return 0 if ok else proc.returncode or 1


def _head(repo: Path) -> str:
    # safe.directory=* is required in the SYSTEM scheduled-task context: git
    # refuses "dubious ownership" there and would return an empty HEAD, so the
    # ledger recorded a green run with an empty triplet (2026-09-08, same class
    # as the 56ba0eb manifest cat-file fix).
    return subprocess.run(["git", "-c", "safe.directory=*", "-C", str(repo),
                           "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def _schtasks(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["schtasks", *args], capture_output=True,
                          text=True, errors="replace", timeout=60)


def query_task_status(task_name: str) -> tuple[str, str]:
    """registered / missing / unknown — never claim "missing" when unreadable.

    A SYSTEM task is not queryable from a non-elevated session (`Access is
    denied`), so a failed query is UNKNOWN, not missing: reporting a
    successfully registered task as missing is a false signal (observed
    2026-09-08 right after the monthly task was registered).
    """
    proc = _schtasks(["/query", "/tn", task_name, "/fo", "csv", "/v"])
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        first = detail[0] if detail else "schtasks query failed"
        return "unknown", f"cannot read task (run elevated): {first}"
    out = proc.stdout or ""
    # TaskName appears in CSV as "name" or "\name" (folder prefix); plain
    # substring search is robust to column layout, BOM, locale headers.
    if task_name in out:
        return "registered", "task found in query output"
    return "missing", "task not found in query output"


def task_status() -> tuple[str, str]:
    return query_task_status(TASK_NAME)


def cmd_register(_args: argparse.Namespace) -> int:
    """Register via PowerShell Register-ScheduledTask (no password prompt).

    ``schtasks /create /ru SYSTEM`` without ``/rp`` pops a credential dialog
    on some Windows builds and hangs the subprocess; Register-ScheduledTask
    with ``-LogonType ServiceAccount`` registers SYSTEM tasks without any
    password.

    Power/wake fix (0x800710E0, diagnosed 2026-09-05): the DEFAULT settings
    refuse to start on battery power and never wake the machine — when the
    computer sleeps through the 22:00 trigger, the late catch-up run fails
    with "operator refused the request" (-2147020576).  Explicit settings
    allow any power source, wake the computer to run on schedule, and
    StartWhenAvailable catches up a missed run on the next boot (the owner
    powers the machine off overnight — StartWhenAvailable fires the missed
    daily run once when the machine is next turned on, without the
    multiple-runs-per-day risk of a bare boot trigger).
    """
    script = (
        "$action = New-ScheduledTaskAction -Execute "
        f"'{sys.executable}' -Argument '\"{Path(__file__).resolve()}\" run-daily'; "
        "$trigger = New-ScheduledTaskTrigger -Daily -At 22:00; "
        "$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' "
        "-LogonType ServiceAccount -RunLevel Highest; "
        "$settings = New-ScheduledTaskSettingsSet "
        "-AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun "
        "-StartWhenAvailable; "
        f"Register-ScheduledTask -TaskName '{TASK_NAME}' "
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
    print(f"registered daily task {TASK_NAME}")
    return 0


def cmd_unregister(_args: argparse.Namespace) -> int:
    proc = _schtasks(["/delete", "/tn", TASK_NAME, "/f"])
    if proc.returncode != 0:
        print((proc.stderr or "unregister failed").strip(), file=sys.stderr)
        return proc.returncode or 1
    print(f"unregistered {TASK_NAME}")
    return 0


def cmd_query(_args: argparse.Namespace) -> int:
    status, detail = task_status()
    print(f"task={TASK_NAME} status={status} detail={detail}")
    return 0 if status == "registered" else 1


def cmd_verify(args: argparse.Namespace) -> int:
    status, detail = task_status()
    ledger = read_ledger(Path(args.ledger))
    run_status, run_detail = freshness_status(ledger)
    ready, gate = release_gate(Path(args.ledger))
    print(f"schedule={status} ({detail})")
    print(f"last_run={run_status} ({run_detail})")
    print(f"release_gate={ready} ({gate})")
    return 0 if (status == "registered" and run_status == "fresh") else 1


def build_parser() -> argparse.ArgumentParser:
    """Parser factory (testable without executing commands)."""
    parser = argparse.ArgumentParser(description="Daily Windows T2 scheduling (ZR-902)")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--alerts", type=Path, default=DEFAULT_ALERTS)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run-daily")
    run.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    run.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    run.add_argument("--source-ref", action="append", type=Path, default=[])
    for name in ("register", "unregister", "query", "verify"):
        sub.add_parser(name)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "run-daily":
        return run_daily(
            args.config, args.report_root, args.ledger, args.alerts,
            source_ref_files=tuple(args.source_ref),
        )
    if args.command == "register":
        return cmd_register(args)
    if args.command == "unregister":
        return cmd_unregister(args)
    if args.command == "query":
        return cmd_query(args)
    return cmd_verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
