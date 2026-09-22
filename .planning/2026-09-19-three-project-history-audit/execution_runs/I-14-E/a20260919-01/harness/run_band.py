"""I-14-E: node-level band measurement (the card's step 4).

Runs ONE of the two restart nodes per invocation, exactly the way the frozen band
ran them (same suite path, same stripped env, same interleaving, same per-run
fresh basetemp), under a declared load condition, and records per run:

  rc / verdict / assertion, node wall time, the launcher-event timeline derived
  from the run's own worker_launcher_events.jsonl (statuses, attempts, uptimes),
  plus two cheap per-run load probes (scheduler overshoot and a fixed CPU loop).

The driver is an evidence collector: it never asserts a business verdict and it
never modifies the product test or the product source.

  python run_band.py --python <iso venv python> --repo <CW> --node child_without_runtime \
      --condition quiet --trees T0=<..>/iso/T0/src,T4=<..>/iso/T4/src,T0b=<..>/iso/T0b/src \
      --runs 12 --passes 2 --root %TEMP%/i14e-band-quiet --out .../after/band-quiet.json
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
NODES = {
    "child_without_runtime": "test_child_without_runtime_session_is_terminated_and_restarted",
    "logon_wrapper_quoted": "test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths",
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


def spawn_latency_probe(python: str) -> dict:
    """Process-creation latency series (the resource these nodes are actually sensitive to).

    Expensive relative to ``load_probe`` (~0.2-2 s), so it is sampled once per pass rather
    than once per run.
    """
    samples = []
    for _ in range(3):
        t0 = time.perf_counter()
        subprocess.run([python, "-c", "pass"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        samples.append(round((time.perf_counter() - t0) * 1000.0, 1))
    return {"spawn_python_pass_ms": samples,
            "spawn_python_pass_ms_median": sorted(samples)[1]}


def sweep_leftovers(root: Path) -> list[int]:
    """Kill launcher/child processes left by an earlier attempt *of this driver only*.

    The match is deliberately narrow: the launcher command line must contain the
    ``-ProjectRoot`` of a project under this driver's own scratch root, so no other
    session's SUT processes can be touched.
    """
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
    """Kill processes this run left behind (a timed-out pytest kills the supervisor via
    subprocess.run, but the fake children are only reaped by the product's job object).
    Returns the pids that were still alive when reaping started."""
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
    events_path = next(run_dir.rglob("worker_launcher_events.jsonl"), None)
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
            attempts.append({"attempt": event.get("attempt"), "child_pid": event.get("child_pid"),
                             "recorded_at": event.get("recorded_at")})
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--node", required=True, choices=sorted(NODES))
    parser.add_argument("--condition", required=True,
                        choices=["quiet", "cpu", "spawn"])
    parser.add_argument("--burners", type=int, default=8)
    parser.add_argument("--trees", required=True)
    parser.add_argument("--runs", type=int, default=12)
    parser.add_argument("--passes", type=int, default=2)
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
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
    suite_path = repo / SUITE
    suite_sha = hashlib.sha256(suite_path.read_bytes()).hexdigest()

    # rough wall estimate so the load generator lives exactly as long as the block
    per_run_guess = 12.0 if args.node == "logon_wrapper_quoted" else 3.5
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
                    env["PYTHONPATH"] = str(src)
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
                    capture = evidence / f"{args.condition}-p{pass_index}-{label}-{args.node}-{run}.txt"
                    capture.write_text(text, encoding="utf-8")
                    verdict = ("passed" if "1 passed" in text
                               else "failed" if "1 failed" in text
                               else "timeout" if timed_out
                               else "unknown")
                    assertion = ""
                    for line in text.splitlines():
                        if line.startswith("E   ") and not assertion:
                            assertion = line.strip()[:200]
                    events = collect_events(run_dir)
                    reaped = reap([events.get("launcher_pid")] +
                                  [a.get("child_pid") for a in events.get("attempts", [])])
                    if reaped:
                        events["reaped_pids"] = reaped
                    if events.get("events_present"):
                        shutil.copyfile(events["events_path"],
                                        evidence / f"{args.condition}-p{pass_index}-{label}-"
                                                   f"{args.node}-{run}-launcher-events.jsonl")
                    rows.append({
                        "condition": args.condition, "pass": pass_index, "tree": label,
                        "node": args.node, "run": run, "wall_seconds": round(wall, 3),
                        "returncode": rc, "verdict": verdict, "assertion": assertion,
                        "load_probe": probe, "capture": str(capture.relative_to(evidence.parent)),
                        "argv": argv_pytest, "cwd": str(run_dir), "tree_src": str(src),
                        "events": events,
                    })
                    extra = ""
                    if events.get("attempts"):
                        extra = "/".join(
                            f"{a.get('unresponsive_uptime_seconds', a.get('exited_uptime_seconds'))}"
                            for a in events["attempts"])
                    print(f"{args.condition} p{pass_index} {label} run{run} rc={rc} {verdict} "
                          f"wall={wall:5.2f}s starts={events.get('child_started_count')} "
                          f"uptimes={extra} {assertion}", flush=True)
    finally:
        load.stop()

    def tally(sel: list[dict]) -> dict:
        return {"runs": len(sel),
                "passed": sum(1 for r in sel if r["verdict"] == "passed"),
                "failed": sum(1 for r in sel if r["verdict"] == "failed"),
                "timeout": sum(1 for r in sel if r["verdict"] == "timeout"),
                "unknown": sum(1 for r in sel if r["verdict"] == "unknown")}

    payload = {
        "script": "harness/run_band.py",
        "card": "I-14-E", "attempt": "a20260919-01",
        "node": args.node, "node_name": node_name,
        "condition": args.condition, "load": load.describe(),
        "started_utc": started_utc,
        "python": args.python, "repo": str(repo), "suite": str(suite_path),
        "suite_sha256": suite_sha,
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
        "tally_by_pass_tree": {f"pass{p}/{t}": tally([r for r in rows
                                                     if r["pass"] == p and r["tree"] == t])
                               for p in range(1, args.passes + 1) for t in trees},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("tally:", json.dumps(payload["tally_by_condition"]))
    print("by tree:", json.dumps(payload["tally_by_tree"]))
    print("out:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
