"""I-14-E-TESTSIDE: red / green / mutation band driver for node ①.

Runs ONE restart node exactly the way the source card's ``harness/run_band.py``
ran it — same suite path, same stripped env, same per-run fresh basetemp, same
load generator — under a declared load condition, and records per run:

  rc / verdict / assertion, node wall time, the launcher-event timeline derived
  from that run's own ``worker_launcher_events.jsonl`` (statuses, attempts,
  uptimes, the ``worker_hang_timeout_seconds`` the launcher was actually given),
  the product's ``CW-BASETEMP-DECISION`` line, the test-side trace
  (``t0`` + exported ``H`` written by the test itself), and two cheap per-run
  load probes — so "load" and "fix" are numbers, not adjectives.

The driver is an evidence collector: it never asserts a business verdict and it
never modifies the product test or the product source.

  python run_band.py --python <venv python> --repo <iso> --tree <iso/src> \
      --arm red --tag r --condition cpu --burners 8 --runs 6 \
      --out .../red/band-red.json --evidence .../red
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load import Load  # noqa: E402

SUITE = "tests/contract/test_source_catalog_worker_bootstrap.py"
NODE = "test_child_without_runtime_session_is_terminated_and_restarted"


def load_probe() -> dict:
    """Cheap per-run proxies for machine load (perturbation ~30 ms)."""
    t0 = time.perf_counter()
    time.sleep(0.02)
    overshoot_ms = (time.perf_counter() - t0 - 0.02) * 1000.0
    t1 = time.perf_counter()
    total = 0
    for i in range(300_000):
        total += i
    cpu_loop_ms = (time.perf_counter() - t1) * 1000.0
    return {"sleep20_overshoot_ms": round(overshoot_ms, 3),
            "cpu_loop_300k_ms": round(cpu_loop_ms, 3),
            "blackhole": total}


def ambient_sample(seconds: float = 3.0) -> dict:
    """Independent machine-load measurement: process CPU-time delta / wall.

    busy_cores = total CPU-seconds consumed by ALL processes during the window,
    divided by the window length (12 logical cores on this box).  Same shape of
    probe the source card used in oracle-addendum-A A1 (implemented with
    Get-Process TotalProcessorTime deltas, which needs no extra package).
    """
    script = (
        "$a=@{}; "
        "Get-Process | ForEach-Object { $a[$_.Id]=$_.TotalProcessorTime.TotalMilliseconds }; "
        "$t=[Diagnostics.Stopwatch]::StartNew(); Start-Sleep -Seconds @SECONDS@; $t.Stop(); "
        "$total=0.0; $top=@(); "
        "Get-Process | ForEach-Object { $p=$a[$_.Id]; if ($null -ne $p) { "
        "$d=$_.TotalProcessorTime.TotalMilliseconds-$p; if ($d -gt 0) { $total+=$d; "
        "if ($d -gt 200) { $top += ($_.Name + ':' + [int]$d) } } } }; "
        "$busy = $total / $t.ElapsedMilliseconds; "
        "$o = New-Object System.Collections.Specialized.OrderedDictionary; "
        "$o['window_ms'] = [int64]$t.ElapsedMilliseconds; "
        "$o['total_cpu_ms'] = [math]::Round($total,1); "
        "$o['busy_cores'] = [math]::Round($busy,3); "
        "$o['logical_cores'] = @CORES@; "
        "$o['top'] = @($top | Select-Object -First 6); "
        "Write-Output ($o | ConvertTo-Json -Compress)"
    ).replace("@SECONDS@", str(int(seconds))).replace("@CORES@", str(os.cpu_count() or 0))
    try:
        out = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace")
        payload = json.loads(out.stdout.strip().splitlines()[-1])
    except Exception as exc:  # pragma: no cover
        payload = {"error": f"{type(exc).__name__}: {exc}"}
    payload["probe"] = "process CPU-time delta over N-second window"
    payload["window_seconds_requested"] = seconds
    return payload


def spawn_latency_probe(python: str) -> dict:
    samples = []
    for _ in range(3):
        t0 = time.perf_counter()
        subprocess.run([python, "-c", "pass"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        samples.append(round((time.perf_counter() - t0) * 1000.0, 1))
    return {"spawn_python_pass_ms": samples,
            "spawn_python_pass_ms_median": sorted(samples)[1]}


def sweep_leftovers(root: Path) -> list[int]:
    """Kill launcher/child processes left by an earlier attempt *of this driver only*."""
    root_text = str(root)
    killed: list[int] = []
    query = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "
             f"'*{root_text}*' -and ($_.CommandLine -like '*-File*source_catalog_worker.ps1*' "
             "-or $_.CommandLine -like '*-m company_wiki.source_catalog.cli*') } | "
             "Select-Object -ExpandProperty ProcessId")
    probe = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                            query], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, encoding="utf-8", errors="replace")
    for line in probe.stdout.split():
        if line.strip().isdigit():
            pid = int(line)
            if pid == os.getpid():
                continue
            subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                            f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            killed.append(pid)
    return killed


def reap(pids: list[int]) -> list[int]:
    reaped = []
    for pid in pids:
        if not pid or pid == os.getpid():
            continue
        probe = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                                f"if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) "
                                f"{{ exit 0 }} else {{ exit 1 }}"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if probe.returncode == 0:
            reaped.append(pid)
            subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                            f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return reaped


def collect_events(run_root: Path) -> dict:
    events_path = next(run_root.rglob("worker_launcher_events.jsonl"), None)
    if events_path is None:
        return {"events_present": False}
    events = []
    for line in events_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    attempts: list[dict] = []
    for event in events:
        if event.get("status") == "child_started":
            attempts.append({"attempt": event.get("attempt"), "child_pid": event.get("child_pid")})
        elif attempts and event.get("status") == "child_unresponsive":
            attempts[-1]["unresponsive_uptime_seconds"] = event.get("uptime_seconds")
            attempts[-1]["unresponsive_reason"] = event.get("reason")
        elif attempts and event.get("status") == "exited":
            attempts[-1]["exited_uptime_seconds"] = event.get("uptime_seconds")
            attempts[-1]["exited_reason"] = event.get("reason")
            attempts[-1]["exit_code"] = event.get("exit_code")
    return {
        "events_present": True,
        "events_path": str(events_path),
        "statuses": [e.get("status") for e in events],
        "child_started_count": sum(1 for e in events if e.get("status") == "child_started"),
        "child_unresponsive_count": sum(1 for e in events
                                        if e.get("status") == "child_unresponsive"),
        "restarting_count": sum(1 for e in events if e.get("status") == "restarting"),
        "attempts": attempts,
        "launcher_pid": events[0].get("launcher_pid") if events else None,
        "hang_timeout_seconds": events[0].get("worker_hang_timeout_seconds") if events else None,
        "child_poll_ms": events[0].get("child_poll_milliseconds") if events else None,
    }


def read_tail(path: Path, offset: int) -> tuple[list[str], int]:
    if not path.exists():
        return [], offset
    data = path.read_text(encoding="utf-8", errors="replace")
    new = data[offset:].splitlines()
    return [ln for ln in new if ln.strip()], len(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--repo", required=True, help="iso root (suite lives below it)")
    parser.add_argument("--tree", required=True, help="product src tree put on PYTHONPATH")
    parser.add_argument("--arm", required=True, choices=["red", "green", "mut"])
    parser.add_argument("--tag", required=True, help="basetemp tag prefix, 1-2 chars (r/g/m)")
    parser.add_argument("--condition", required=True, choices=["quiet", "cpu", "spawn"])
    parser.add_argument("--burners", type=int, default=8)
    parser.add_argument("--runs", type=int, default=6)
    parser.add_argument("--passes", type=int, default=1)
    parser.add_argument("--out", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    tree = Path(args.tree).resolve()
    temp = Path(os.environ.get("TEMP", os.environ.get("TMP", ".")))
    # NOTE: a FRESH work root on purpose.  The first (discarded) red attempt ran
    # before the dir-mode shim existed and left basetemps whose ACL nobody can
    # read or delete any more (see oracle-addendum-B.md): they are undeletable,
    # so later arms use ``i14ets-b`` rather than re-touching them.
    # R3 note: this attempt uses its own fresh root ``i14ets-r3`` (oracle.md
    # section 4.4) so no earlier attempt's scratch is ever touched.
    work = temp / "i14ets-r3"     # pytest cwd + basetemp parent (oracle-addendum-A)
    work.mkdir(parents=True, exist_ok=True)
    evidence = Path(args.evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    capture_dir = evidence / "captures"
    capture_dir.mkdir(parents=True, exist_ok=True)
    decision_file = evidence / "basetemp-decisions.jsonl"
    trace_file = evidence / "tside-trace.jsonl"
    report_file = evidence / "reports.jsonl"
    for path in (decision_file, trace_file, report_file):
        if path.exists():
            path.unlink()
    harness_dir = Path(__file__).resolve().parent

    env_base = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": str(temp),
        "TMP": str(temp),
        "PYTHONPATH": str(tree) + os.pathsep + str(harness_dir),
        # product's own short-basetemp convention: basetemp <= 60 chars stays
        # within-budget (no relocation, no %TEMP%/cw-pytest-basetemp creation)
        "CW_BASETEMP_DECISION_FILE": str(decision_file),
        # optional test-side trace sink (the fix works without it too)
        "CW_TSIDE_TRACE_FILE": str(trace_file),
        # harness-side report sink (survives a crashing pytest_sessionfinish)
        "CW_REPORT_FILE": str(report_file),
    }
    suite_path = repo / SUITE
    suite_sha = hashlib.sha256(suite_path.read_bytes()).hexdigest()

    per_run_guess = 12.0
    est_seconds = per_run_guess * args.runs * args.passes + 60
    load = Load(args.condition, args.burners, est_seconds)
    rows: list[dict] = []
    spawn_by_pass: dict[int, dict] = {}
    ambient = {"before": None, "with_load": None, "after": None}
    swept = sweep_leftovers(work)
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ambient["before"] = ambient_sample(3.0)
    load.start()
    ambient["with_load"] = ambient_sample(3.0)
    try:
        for pass_index in range(1, args.passes + 1):
            spawn_by_pass[pass_index] = spawn_latency_probe(args.python)
            for run in range(1, args.runs + 1):
                basetemp = work / f"{args.tag}{pass_index}{run}"
                if basetemp.exists():
                    shutil.rmtree(basetemp, ignore_errors=True)
                probe = load_probe()
                trace_offset = trace_file.stat().st_size if trace_file.exists() else 0
                report_offset = report_file.stat().st_size if report_file.exists() else 0
                argv_pytest = [args.python, "-X", "utf8", "-B", "-m", "pytest",
                               "-p", "no:cacheprovider",
                               "-p", "tside_probe",
                               "--basetemp", str(basetemp),
                               "-q", f"{suite_path}::{NODE}"]
                t0 = time.perf_counter()
                timed_out = False
                try:
                    proc = subprocess.run(argv_pytest, cwd=str(work), env=env_base,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          timeout=args.timeout)
                    rc = proc.returncode
                    text = proc.stdout.decode("utf-8", "replace")
                except subprocess.TimeoutExpired as exc:
                    timed_out = True
                    rc = None
                    text = (exc.stdout or b"").decode("utf-8", "replace")
                wall = time.perf_counter() - t0
                capture = capture_dir / f"{args.arm}-p{pass_index}-r{run}.txt"
                capture.write_text(text, encoding="utf-8")
                new_reports, _ = read_tail(report_file, report_offset)
                reports = [json.loads(ln) for ln in new_reports if ln.startswith("{")]
                report_failed = any(r.get("outcome") == "failed" for r in reports)
                report_call_ok = any(r.get("outcome") == "passed" and r.get("when") == "call"
                                     for r in reports)
                if timed_out:
                    verdict = "timeout"
                elif "1 passed" in text or (report_call_ok and not report_failed):
                    verdict = "passed"
                elif "1 failed" in text or report_failed:
                    verdict = "failed"
                else:
                    verdict = "unknown"
                assertion = ""
                for line in text.splitlines():
                    if line.startswith("E   ") and not assertion:
                        assertion = line.strip()[:200]
                if not assertion:
                    for rec in reports:
                        for line in str(rec.get("longrepr", "")).splitlines():
                            stripped = line.strip()
                            if stripped.startswith("E ") or stripped.startswith("E   "):
                                assertion = stripped[:200]
                                break
                        if assertion:
                            break
                decision_lines, _ = read_tail(decision_file, 0)
                trace_lines, _ = read_tail(trace_file, trace_offset)
                events = collect_events(basetemp)
                reaped = reap([events.get("launcher_pid")] +
                              [a.get("child_pid") for a in events.get("attempts", [])])
                if reaped:
                    events["reaped_pids"] = reaped
                if events.get("events_present"):
                    shutil.copyfile(events["events_path"],
                                    capture_dir / f"{args.arm}-p{pass_index}-r{run}-events.jsonl")
                row = {
                    "arm": args.arm, "pass": pass_index, "run": run,
                    "basetemp": str(basetemp), "basetemp_len": len(str(basetemp)),
                    "wall_seconds": round(wall, 3),
                    "returncode": rc, "verdict": verdict, "assertion": assertion,
                    "load_probe": probe, "capture": str(capture),
                    "basetemp_decision_lines": decision_lines[-2 * args.runs:],
                    "tside_trace": [json.loads(ln) for ln in trace_lines
                                    if ln.startswith("{")],
                    "reports": reports,
                    "argv": argv_pytest, "cwd": str(work), "tree_src": str(tree),
                    "events": events,
                }
                rows.append(row)
                extra = ""
                if events.get("attempts"):
                    extra = "/".join(
                        str(a.get("unresponsive_uptime_seconds",
                                  a.get("exited_uptime_seconds")))
                        for a in events["attempts"])
                trace_txt = ""
                if row["tside_trace"]:
                    last = row["tside_trace"][-1]
                    trace_txt = (f" t0={last.get('t0_seconds')} "
                                 f"H={last.get('hang_timeout_seconds')}")
                print(f"{args.arm} p{pass_index} r{run} rc={rc} {verdict} "
                      f"wall={wall:5.2f}s starts={events.get('child_started_count')} "
                      f"H={events.get('hang_timeout_seconds')} uptimes={extra}"
                      f"{trace_txt} {assertion}", flush=True)
    finally:
        ambient["after"] = ambient_sample(3.0)
        load.stop()

    def tally(sel: list[dict]) -> dict:
        return {"runs": len(sel),
                "passed": sum(1 for r in sel if r["verdict"] == "passed"),
                "failed": sum(1 for r in sel if r["verdict"] == "failed"),
                "timeout": sum(1 for r in sel if r["verdict"] == "timeout"),
                "unknown": sum(1 for r in sel if r["verdict"] == "unknown")}

    payload = {
        "script": "harness/run_band.py",
        "card": "I-14-E-TESTSIDE-R3", "attempt": "a20260926-01",
        "arm": args.arm, "node": "child_without_runtime", "node_name": NODE,
        "condition": args.condition, "burners": args.burners,
        "load": load.describe(),
        "started_utc": started_utc,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": args.python, "repo": str(repo), "suite": str(suite_path),
        "suite_sha256": suite_sha, "tree_src": str(tree),
        "runs": args.runs, "passes": args.passes,
        "driver_timeout_seconds": args.timeout,
        "ambient_sample": ambient,
        "spawn_latency_by_pass": spawn_by_pass,
        "leftovers_swept_at_start": swept,
        "work_root": str(work),
        "decision_file": str(decision_file),
        "trace_file": str(trace_file),
        "results": rows,
        "tally": tally(rows),
        "mean_wall_seconds": round(sum(r["wall_seconds"] for r in rows) / max(1, len(rows)), 3),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("tally:", json.dumps(payload["tally"]))
    print("ambient:", json.dumps(ambient))
    print("out:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
