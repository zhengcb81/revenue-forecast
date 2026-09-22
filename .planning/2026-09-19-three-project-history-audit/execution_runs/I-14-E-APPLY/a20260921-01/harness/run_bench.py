"""I-14-E-APPLY: per-run bench driver for one isolated test tree.

Shape follows I-14-E's ``harness/run_band.py`` (same stripped env, same
``-p no:cacheprovider``, same fresh basetemp per run, same interleaving) so that the
pre-fix baseline in ``I-14-E/a20260919-01/after/band-child-*.json`` and this attempt's
arms are comparable.  The differences are the ones this card needs:

  * ``--suite``  the test file path differs per arm (fixed tree vs mutant tree)
  * ``--node-name``  the node id differs (the non-vacuity node lives in the fixed tree)
  * every run records the hang timeout the launcher ACTUALLY used, read from that run's
    own ``worker_launcher_events.jsonl``, plus the watchdog-kill uptimes and counts

  python run_bench.py --python <iso venv python> --suite <abs test file> \
      --node child_without_runtime --condition quiet \
      --trees T0=<..>/iso/T0,T0b=<..>/iso/T0b \
      --runs 4 --passes 2 --root %TEMP%/i14eapply-quiet --evidence <dir> --out <json>
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

NODES = {
    "child_without_runtime": "test_child_without_runtime_session_is_terminated_and_restarted",
    "non_vacuity": "test_derived_hang_timeout_still_terminates_a_genuinely_hung_child",
}


def parse_trees(spec: str) -> dict[str, Path]:
    trees: dict[str, Path] = {}
    for part in spec.split(","):
        name, _, path = part.strip().partition("=")
        if not name or not path:
            raise SystemExit(f"bad --trees entry: {part!r}")
        trees[name] = Path(path).resolve()
    return trees


def load_probe() -> dict:
    """Cheap per-run proxy for machine load (perturbation ~30 ms), same as I-14-E."""
    t0 = time.perf_counter()
    time.sleep(0.02)
    overshoot_ms = (time.perf_counter() - t0 - 0.02) * 1000.0
    t1 = time.perf_counter()
    total = 0
    for i in range(300_000):
        total += i
    return {"sleep20_overshoot_ms": round(overshoot_ms, 3),
            "cpu_loop_300k_ms": round((time.perf_counter() - t1) * 1000.0, 3),
            "blackhole": total}


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
                           text=True)
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


def collect_events(run_dir: Path) -> dict:
    """Timeline of the ASSERTED project only.

    The measured-throughput derivation drives the launcher twice more inside the same
    pytest tmp dir, so a run directory can hold several timelines; the one that matters
    is the project the node asserts on, which is always ``fake-project``.
    """
    candidates = sorted(run_dir.rglob("worker_launcher_events.jsonl"))
    chosen = None
    for path in candidates:
        if path.parent.parent.name == "fake-project":
            chosen = path
            break
    if chosen is None:
        return {"events_present": False, "events_paths": [str(p) for p in candidates]}
    events = []
    for line in chosen.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    attempts: list[dict] = []
    for event in events:
        if event.get("status") == "child_started":
            attempts.append({"attempt": event.get("attempt"), "child_pid": event.get("child_pid"),
                             "recorded_at": event.get("recorded_at")})
        elif attempts and event.get("status") == "child_unresponsive":
            attempts[-1]["unresponsive_uptime_seconds"] = event.get("uptime_seconds")
            attempts[-1]["unresponsive_reason"] = event.get("reason")
        elif attempts and event.get("status") == "exited":
            attempts[-1]["exited_uptime_seconds"] = event.get("uptime_seconds")
            attempts[-1]["exited_reason"] = event.get("reason")
            attempts[-1]["exit_code"] = event.get("exit_code")
    unresponsive = [e for e in events if e.get("status") == "child_unresponsive"]
    return {
        "events_present": True,
        "events_path": str(chosen),
        "all_timelines_in_run": [str(p) for p in candidates],
        "statuses": [e.get("status") for e in events],
        "child_started_count": sum(1 for e in events if e.get("status") == "child_started"),
        "child_unresponsive_count": len(unresponsive),
        "restarting_count": sum(1 for e in events if e.get("status") == "restarting"),
        "watchdog_kill_uptimes": [e.get("uptime_seconds") for e in unresponsive],
        "watchdog_kill_reasons": sorted({e.get("reason") for e in unresponsive}),
        "attempts": attempts,
        "launcher_pid": events[0].get("launcher_pid") if events else None,
        # THE key observability requirement: what timeout the launcher actually used
        "hang_timeout_seconds_actually_used": (
            events[0].get("worker_hang_timeout_seconds") if events else None),
        "child_poll_ms_actually_used": (
            events[0].get("child_poll_milliseconds") if events else None),
    }


def measured_derivation(run_dir: Path) -> dict:
    """Read back what the in-test derivation measured, from the warm-up project.

    The report is written by the test itself using lenient probes; a missing file is
    recorded as such rather than silently dropped.
    """
    reports = sorted(run_dir.rglob("hang_timeout_derivation.json"))
    if not reports:
        return {"report_present": False}
    try:
        return {"report_present": True, "report_path": str(reports[-1]),
                **json.loads(reports[-1].read_text(encoding="utf-8-sig"))}
    except (OSError, ValueError) as exc:
        return {"report_present": False, "report_error": f"{type(exc).__name__}: {exc}"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--node", required=True, choices=sorted(NODES))
    parser.add_argument("--condition", required=True, choices=["quiet", "cpu", "spawn"])
    parser.add_argument("--burners", type=int, default=8)
    parser.add_argument("--trees", required=True)
    parser.add_argument("--runs", type=int, default=4)
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--longest-ok-seconds", type=float, default=45.0,
                        help="a PASS longer than this is flagged as suspicious")
    args = parser.parse_args(argv)

    suite_path = Path(args.suite).resolve()
    node_name = NODES[args.node]
    trees = parse_trees(args.trees)
    root = Path(os.path.expandvars(args.root))
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    evidence = Path(args.evidence)
    evidence.mkdir(parents=True, exist_ok=True)

    env_base = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
    }
    suite_sha = hashlib.sha256(suite_path.read_bytes()).hexdigest()
    tree_shas = {label: hashlib.sha256(
        (src / "tests" / "contract" / suite_path.name).read_bytes()).hexdigest()
        for label, src in trees.items()}

    per_run_guess = 12.0 if args.node == "non_vacuity" else 10.0
    est_seconds = per_run_guess * args.runs * args.passes * len(trees) + 60
    load = Load(args.condition, args.burners, est_seconds)
    rows: list[dict] = []
    spawn_by_pass: dict[int, dict] = {}
    swept = sweep_leftovers(root)
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    load.start()
    try:
        for pass_index in range(1, args.passes + 1):
            spawn_by_pass[pass_index] = spawn_latency_probe(args.python)
            for run in range(1, args.runs + 1):
                for label, src in trees.items():
                    run_dir = root / f"{args.condition}-p{pass_index}-{label}-{args.node}-{run}"
                    run_dir.mkdir(parents=True, exist_ok=True)
                    probe = load_probe()
                    env = dict(env_base)
                    env["PYTHONPATH"] = str(src / "tests" / "contract")
                    argv_pytest = [args.python, "-X", "utf8", "-B", "-m", "pytest",
                                   "-p", "no:cacheprovider",
                                   "--basetemp", str(run_dir / "pytest"),
                                   "-q", f"{suite_path}::{node_name}"]
                    t0 = time.perf_counter()
                    timed_out = False
                    try:
                        proc = subprocess.run(argv_pytest, cwd=str(run_dir), env=env,
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
                    capture = evidence / (f"{args.condition}-p{pass_index}-{label}-"
                                          f"{args.node}-{run}.txt")
                    capture.write_text(text, encoding="utf-8")
                    verdict = ("passed" if "1 passed" in text
                               else "failed" if "1 failed" in text
                               else "timeout" if timed_out
                               else "error" if rc not in (0, 1)
                               else "unknown")
                    assertion = ""
                    for line in text.splitlines():
                        if line.startswith("E   ") and not assertion:
                            assertion = line.strip()[:220]
                    events = collect_events(run_dir)
                    derivation = measured_derivation(run_dir)
                    reaped = reap([events.get("launcher_pid")] +
                                  [a.get("child_pid") for a in events.get("attempts", [])])
                    if reaped:
                        events["reaped_pids"] = reaped
                    if events.get("events_present"):
                        shutil.copyfile(events["events_path"],
                                        evidence / (f"{args.condition}-p{pass_index}-{label}-"
                                                    f"{args.node}-{run}-launcher-events.jsonl"))
                    if derivation.get("report_present"):
                        shutil.copyfile(derivation["report_path"],
                                        evidence / (f"{args.condition}-p{pass_index}-{label}-"
                                                    f"{args.node}-{run}-derivation.json"))
                    rows.append({
                        "condition": args.condition, "pass": pass_index, "tree": label,
                        "node": args.node, "run": run, "wall_seconds": round(wall, 3),
                        "returncode": rc, "verdict": verdict, "assertion": assertion,
                        "load_probe": probe, "capture": str(capture),
                        "argv": argv_pytest, "cwd": str(run_dir), "tree_root": str(src),
                        "events": events, "derivation": derivation,
                        "pass_but_slow": (verdict == "passed"
                                          and wall > args.longest_ok_seconds),
                    })
                    print(f"{args.condition} p{pass_index} {label} run{run} rc={rc} {verdict} "
                          f"wall={wall:5.2f}s starts={events.get('child_started_count')} "
                          f"hang={events.get('hang_timeout_seconds_actually_used')} "
                          f"kills={events.get('child_unresponsive_count')} {assertion}",
                          flush=True)
    finally:
        load.stop()

    def tally(sel: list[dict]) -> dict:
        return {"runs": len(sel),
                "passed": sum(1 for r in sel if r["verdict"] == "passed"),
                "failed": sum(1 for r in sel if r["verdict"] == "failed"),
                "timeout": sum(1 for r in sel if r["verdict"] == "timeout"),
                "error": sum(1 for r in sel if r["verdict"] == "error"),
                "unknown": sum(1 for r in sel if r["verdict"] == "unknown"),
                "pass_but_slow": sum(1 for r in sel if r.get("pass_but_slow"))}

    payload = {
        "script": "harness/run_bench.py",
        "card": "I-14-E-APPLY", "attempt": "a20260921-01",
        "node": args.node, "node_name": node_name,
        "condition": args.condition, "load": load.describe(),
        "started_utc": started_utc,
        "python": args.python, "suite": str(suite_path), "suite_sha256": suite_sha,
        "tree_suite_sha256": tree_shas,
        "trees": {k: str(v) for k, v in trees.items()},
        "runs_per_tree_pass": args.runs, "passes": args.passes,
        "interleaved": True,
        "spawn_latency_by_pass": spawn_by_pass,
        "leftovers_swept_at_start": swept,
        "results": rows,
        "tally_by_condition": tally(rows),
        "tally_by_pass": {f"pass{p}": tally([r for r in rows if r["pass"] == p])
                          for p in range(1, args.passes + 1)},
        "tally_by_tree": {t: tally([r for r in rows if r["tree"] == t]) for t in trees},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("tally:", json.dumps(payload["tally_by_condition"]))
    print("hang timeouts actually used:",
          sorted({r["events"].get("hang_timeout_seconds_actually_used") for r in rows
                  if r["events"].get("events_present")}))
    print("out:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
