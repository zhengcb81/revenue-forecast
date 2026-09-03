"""ZR-902: daily Windows T2 scheduling — schedule/runner/freshness/release gate.

Wraps the existing FC-1102 ``tools/daily_t2_runner.py`` into a fully
scheduled daily assurance loop:

  run-daily    run the T2 runner, write the run ledger
               (``assurance/runs/daily_manifest.json``), judge freshness
               (<= 24h and ok -> fresh; older -> stale; absent -> missing)
               and append an alert journal entry when not fresh.
  register     register a Windows Task Scheduler daily task (deployment
               action; requires elevation) that invokes ``run-daily``.
  query        read-only status of the scheduled task (exists / last run).
  unregister   remove the scheduled task (deployment action).
  verify       combined status: schedule (registered/missing) + last run
               (fresh/stale/missing) — the AUD2-01/02/03 oracle.

The release gate (``release_gate``) is a pure function over the ledger:
fresh + ok -> ready; stale / missing / not-ok -> blocked.  Scripts existing
without a schedule, a stopped job, or an old green report never pass.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / "tools" / "daily_t2_runner.py"
DEFAULT_LEDGER = PROJECT_ROOT / "assurance" / "runs" / "daily_manifest.json"
DEFAULT_ALERTS = PROJECT_ROOT / "assurance" / "runs" / "daily_alert.jsonl"
TASK_NAME = "revenue_daily_t2"
MAX_AGE_HOURS = 24


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _iso_to_utc(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(UTC)


def write_ledger(path: Path, run_id: str, started_at: str, triplet: dict,
                 ok: bool, report_path: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "latest_run_id": run_id,
        "started_at": started_at,
        "triplet": triplet,
        "ok": ok,
        "report_path": report_path,
    }
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


def run_daily(catalog: Path, manifest: Path, report_root: Path,
              ledger_path: Path, alert_path: Path) -> int:
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_dir = report_root / run_id
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER),
         "--catalog", str(catalog), "--manifest", str(manifest),
         "--report-root", str(report_root), "--run-id", run_id],
        capture_output=True, text=True, errors="replace", timeout=600,
    )
    started = _now_iso()
    ok = proc.returncode == 0
    triplet = {"revenue": _head(PROJECT_ROOT),
               "filing": _head(PROJECT_ROOT.parent / "filing-fetch"),
               "wiki": _head(PROJECT_ROOT.parent / "company-wiki")}
    write_ledger(ledger_path, run_id, started, triplet, ok,
                 str(report_dir / "report.json"))
    status, detail = freshness_status(read_ledger(ledger_path), now=started)
    if status != "fresh":
        append_alert(alert_path, {
            "at_utc": started, "run_id": run_id, "status": status,
            "reason": detail, "exit_code": proc.returncode,
        })
    print(f"run_id={run_id} ok={ok} status={status} detail={detail}")
    return proc.returncode


def _head(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def _schtasks(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["schtasks", *args], capture_output=True,
                          text=True, errors="replace", timeout=60)


def task_status() -> tuple[str, str]:
    proc = _schtasks(["/query", "/tn", TASK_NAME, "/fo", "csv", "/v"])
    if proc.returncode != 0:
        return "missing", "no scheduled task registered"
    out = proc.stdout or ""
    # TaskName appears in CSV as "revenue_daily_t2" or "\revenue_daily_t2"
    # (folder prefix); plain substring search is robust to column layout,
    # BOM, and locale-specific headers.
    if TASK_NAME in out:
        return "registered", "task found in query output"
    return "missing", "task not found in query output"


def cmd_register(_args: argparse.Namespace) -> int:
    """Register via PowerShell Register-ScheduledTask (no password prompt).

    ``schtasks /create /ru SYSTEM`` without ``/rp`` pops a credential dialog
    on some Windows builds and hangs the subprocess; Register-ScheduledTask
    with ``-LogonType ServiceAccount`` registers SYSTEM tasks without any
    password.
    """
    script = (
        "$action = New-ScheduledTaskAction -Execute "
        f"'{sys.executable}' -Argument '\"{Path(__file__).resolve()}\" --run-daily'; "
        "$trigger = New-ScheduledTaskTrigger -Daily -At 03:30; "
        "$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' "
        "-LogonType ServiceAccount -RunLevel Highest; "
        f"Register-ScheduledTask -TaskName '{TASK_NAME}' "
        "-Action $action -Trigger $trigger -Principal $principal -Force | Out-Null"
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Daily Windows T2 scheduling (ZR-902)")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--alerts", type=Path, default=DEFAULT_ALERTS)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run-daily")
    run.add_argument("--catalog", type=Path, required=True)
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--report-root", type=Path, required=True)
    for name in ("register", "unregister", "query", "verify"):
        sub.add_parser(name)
    args = parser.parse_args()
    if args.command == "run-daily":
        return run_daily(args.catalog, args.manifest, args.report_root,
                         Path(args.ledger), Path(args.alerts))
    if args.command == "register":
        return cmd_register(args)
    if args.command == "unregister":
        return cmd_unregister(args)
    if args.command == "query":
        return cmd_query(args)
    return cmd_verify(args)


if __name__ == "__main__":
    raise SystemExit(main())
