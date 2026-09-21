"""I-14-E: node-2 window probe — how long the logon wrapper takes, and how long the
supervisor it detaches takes to finish, under a declared load condition.

Node ``test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths`` has three
timing budgets: ``subprocess.run(..., timeout=15)`` around the wrapper, a 15 s wait for
the detached supervisor to appear in the launcher events, and a 20 s wait for it to
exit.  This script measures the two quantities those budgets must cover:

  wrapper_seconds  powershell -File source_catalog_worker_at_logon.ps1 ... (must be < 15 s)
  events_seconds   wrapper exit -> launcher events file present with a child_started
  exit_seconds     child_started -> supervisor and child gone (the test's 20 s budget)

It uses a fake project built by the product test's own helper, copies the two ps1 files
from the read-only product tree exactly as the test does, and records both load probes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load import Load  # noqa: E402
from run_band import load_probe  # noqa: E402

DEFAULT_REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
SUITE = "tests/contract/test_source_catalog_worker_bootstrap.py"
WRAPPER_TIMEOUT = 15.0
EVENTS_BUDGET = 15.0
EXIT_BUDGET = 20.0


def build_fixture(repo: Path):
    spec = importlib.util.spec_from_file_location("cw_bootstrap_test", repo / SUITE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def pid_alive(pid: int) -> bool:
    proc = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                           f"if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) "
                           f"{{ exit 0 }} else {{ exit 1 }}"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--repo", default=str(DEFAULT_REPO))
    parser.add_argument("--condition", required=True, choices=["quiet", "cpu", "spawn"])
    parser.add_argument("--burners", type=int, default=8)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    module = build_fixture(repo)
    scripts_src = repo / "scripts"
    root = Path(os.path.expandvars(args.root))
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    load = Load(args.condition, args.burners, args.samples * 20.0 + 60)
    samples: list[dict] = []
    load.start()
    try:
        for index in range(1, args.samples + 1):
            project_root = root / f"sample-{index:03d}"
            project_root.mkdir(parents=True, exist_ok=True)
            project = module._prepare_fake_launcher_project(
                project_root / "project path with spaces",
                [{"sleep_seconds": 10, "exit_code": 0}])
            scripts = project / "scripts"
            scripts.mkdir()
            for name in ("source_catalog_worker.ps1", "source_catalog_worker_at_logon.ps1"):
                shutil.copyfile(scripts_src / name, scripts / name)
            wrapper = scripts / "source_catalog_worker_at_logon.ps1"
            probe = load_probe()
            row: dict = {"sample": index, "condition": args.condition,
                         "load_probe": probe}
            t0 = time.perf_counter()
            try:
                completed = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
                     "Bypass", "-File", str(wrapper), "-PythonExe", args.python,
                     "-ProjectRoot", str(project)],
                    cwd=str(project), capture_output=True, text=True, encoding="utf-8",
                    errors="replace", timeout=WRAPPER_TIMEOUT, check=False)
                row["wrapper_seconds"] = round(time.perf_counter() - t0, 3)
                row["wrapper_rc"] = completed.returncode
                row["wrapper_timed_out"] = False
                row["wrapper_stderr_tail"] = (completed.stderr or "")[-300:]
            except subprocess.TimeoutExpired:
                row["wrapper_seconds"] = None
                row["wrapper_timed_out"] = True
            # wait for the detached supervisor's first child, within the test's 15 s budget
            events_path = project / ".source_catalog" / "worker_launcher_events.jsonl"
            child_pid = supervisor_pid = None
            t1 = time.perf_counter()
            while time.perf_counter() - t1 < EVENTS_BUDGET:
                if events_path.exists():
                    try:
                        events = [json.loads(line) for line in
                                  events_path.read_text(encoding="utf-8-sig").splitlines()
                                  if line.strip()]
                    except json.JSONDecodeError:
                        events = []
                    starts = [e for e in events if e.get("status") == "child_started"]
                    if starts:
                        child_pid = int(starts[-1]["child_pid"])
                        supervisor_pid = int(starts[-1]["launcher_pid"])
                        break
                time.sleep(0.05)
            row["events_seconds"] = round(time.perf_counter() - t1, 3)
            row["child_started_seen"] = child_pid is not None
            # how long until supervisor and child are gone (test budget: 20 s)
            t2 = time.perf_counter()
            if child_pid is not None and supervisor_pid is not None:
                while time.perf_counter() - t2 < EXIT_BUDGET:
                    if not pid_alive(supervisor_pid) and not pid_alive(child_pid):
                        break
                    time.sleep(0.1)
                row["exit_seconds"] = round(time.perf_counter() - t2, 3)
                row["supervisor_gone"] = not pid_alive(supervisor_pid)
                row["child_gone"] = not pid_alive(child_pid)
                for pid in (child_pid, supervisor_pid):
                    subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive",
                                    "-Command",
                                    f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            row["statuses"] = None
            if events_path.exists():
                try:
                    row["statuses"] = [json.loads(line).get("status") for line in
                                       events_path.read_text(encoding="utf-8-sig").splitlines()
                                       if line.strip()]
                except json.JSONDecodeError:
                    pass
            samples.append(row)
            print(f"  node2/{args.condition} {index}/{args.samples} "
                  f"wrapper={row.get('wrapper_seconds')} events={row.get('events_seconds')} "
                  f"exit={row.get('exit_seconds')} starts={row.get('child_started_seen')} "
                  f"statuses={row.get('statuses')}", flush=True)
    finally:
        load.stop()

    def stats(key: str) -> dict:
        values = sorted(v for v in (s.get(key) for s in samples) if v is not None)
        if not values:
            return {"n": 0}
        return {"n": len(values), "min": values[0], "median": statistics.median(values),
                "max": values[-1],
                "count_ge_budget": sum(1 for v in values
                                       if v >= {"wrapper_seconds": WRAPPER_TIMEOUT,
                                                "events_seconds": EVENTS_BUDGET,
                                                "exit_seconds": EXIT_BUDGET}[key])}

    payload = {
        "script": "harness/measure_wrapper_latency.py",
        "card": "I-14-E", "attempt": "a20260919-01",
        "node": "logon_wrapper_quoted", "condition": args.condition,
        "load": load.describe(), "python": args.python,
        "test_file_sha256": hashlib.sha256((repo / SUITE).read_bytes()).hexdigest(),
        "budgets": {"wrapper_timeout_seconds": WRAPPER_TIMEOUT,
                    "events_budget_seconds": EVENTS_BUDGET,
                    "exit_budget_seconds": EXIT_BUDGET},
        "samples": samples,
        "stats": {k: stats(k) for k in
                  ("wrapper_seconds", "events_seconds", "exit_seconds")},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload["stats"], indent=2))
    print("out:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
