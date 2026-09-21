"""I-14-E: independent measurement of the quantities the node-1 timing assumption bounds.

Node ``test_child_without_runtime_session_is_terminated_and_restarted`` drives the REAL
supervisor (``CW/scripts/source_catalog_worker.ps1``) with ``-WorkerHangTimeoutSeconds 0.5
-ChildPollMilliseconds 100`` against a fake project whose behaviours are
``[{sleep 5}, {exit 0}]``.  Two distinct load-sensitive quantities decide the outcome:

  Q1 ``time_to_first_side_effect``  launch -> the fake child's first side effect
     (it increments ``fake_worker_count.txt``, which selects the behaviour).  If child #1
     is killed before that write, child #2 receives the *sleep 5* behaviour instead of the
     immediate exit, and the test needs a third start -> ``assert 3 == 2``.
  Q2 ``immediate_exit_lifetime``   launch -> exit for a child that already sees
     behaviour #2 (immediate exit).  If it is still alive at a poll boundary after 0.5 s of
     uptime, the supervisor kills it as ``session_start_timeout`` -> extra start -> failure.

Both are measured here without pytest and without the watchdog, using the product test's own
``_prepare_fake_launcher_project`` (imported read-only), under a declared load condition:

  --method popen      Popen(python -m company_wiki.source_catalog.cli ... worker) with the
                      child's stdout/stderr redirected to files, cwd = project
  --method startproc  the same launch through PowerShell ``Start-Process`` (the supervisor's
                      own uptime definition, including Start-Process overhead)
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
PROBE_PS1 = Path(__file__).resolve().parent / "child_uptime_probe.ps1"
BEHAVIORS = [{"sleep_seconds": 5, "exit_code": 0}, {"exit_code": 0}]


def build_fixture(repo: Path):
    spec = importlib.util.spec_from_file_location("cw_bootstrap_test", repo / SUITE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def child_env(tree_src: Path) -> dict:
    return {
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
        "PYTHONPATH": str(tree_src),
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": os.environ.get("TEMP", ""), "TMP": os.environ.get("TMP", ""),
    }


def child_argv(python: str, project: Path) -> list[str]:
    return [python, "-m", "company_wiki.source_catalog.cli",
            "--config", str(project / "config" / "source_catalog.yaml"),
            "worker", "--worker-config",
            str(project / "config" / "source_catalog_worker.yaml")]


def sample(repo_module, python: str, tree_src: Path, project_root: Path,
           method: str, timeout: float) -> dict:
    project = repo_module._prepare_fake_launcher_project(project_root, BEHAVIORS)
    catalog = project / ".source_catalog"
    count_path = catalog / "fake_worker_count.txt"
    argv = child_argv(python, project)
    env = child_env(tree_src)

    # ---- child #1: the 5 s sleeper.  Measures Q1 (launch -> first side effect) and is
    # killed at the watchdog's own schedule (0.5 s) if the write has not happened yet.
    probe = load_probe()
    started = time.perf_counter()
    warm = subprocess.Popen(argv, cwd=str(project), env=env, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    q1 = None
    kill_at = 0.5
    while True:
        elapsed = time.perf_counter() - started
        if count_path.exists():
            q1 = elapsed
            break
        if warm.poll() is not None or elapsed >= 3.0:
            break
        time.sleep(0.005)
    warm.kill()
    warm.wait()
    kill_time = time.perf_counter() - started

    # ---- child #2: with the count file present it selects behaviour #2 (immediate exit).
    # Measures Q2 with the same launch mechanism as the supervisor.
    q2 = None
    q2_extra = {}
    if count_path.exists():
        try:
            if method == "popen":
                out = open(catalog / "probe_out.log", "wb")
                err = open(catalog / "probe_err.log", "wb")
                t0 = time.perf_counter()
                proc = subprocess.Popen(argv, cwd=str(project), env=env, stdout=out,
                                        stderr=err, stdin=subprocess.DEVNULL)
                try:
                    proc.wait(timeout=timeout)
                    rc = proc.returncode
                    timed_out = False
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                    rc = None
                    timed_out = True
                q2 = time.perf_counter() - t0
                out.close()
                err.close()
                q2_extra = {"exit_code": rc, "timed_out": timed_out}
            else:
                result_path = project_root / "uptime_probe.json"
                if result_path.exists():
                    result_path.unlink()
                penv = dict(os.environ)
                penv.update({"PYTHONPATH": str(tree_src),
                             "PYTHONDONTWRITEBYTECODE": "1"})
                t0 = time.perf_counter()
                proc = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
                     "Bypass", "-File", str(PROBE_PS1), "-PythonExe", python,
                     "-ProjectRoot", str(project), "-OutPath", str(result_path)],
                    cwd=str(project), env=penv, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, timeout=timeout)
                wall = time.perf_counter() - t0
                payload = (json.loads(result_path.read_text(encoding="utf-8-sig"))
                           if result_path.exists() else {})
                q2 = payload.get("uptime_seconds", wall)
                q2_extra = {"exit_code": payload.get("exit_code"),
                            "probe_rc": proc.returncode,
                            "probe_wall_seconds": round(wall, 3)}
        except Exception as exc:  # noqa: BLE001 - recorded, not swallowed
            q2_extra = {"error": f"{type(exc).__name__}: {exc}"}
    return {
        "time_to_first_side_effect_seconds": None if q1 is None else round(q1, 3),
        "warm_child_kill_seconds": round(kill_time, 3),
        "count_file_after_warmup": count_path.read_text().strip() if count_path.exists() else None,
        "immediate_exit_lifetime_seconds": None if q2 is None else round(q2, 3),
        "q2_detail": q2_extra,
        "load_probe": probe,
    }


def stats(values: list[float]) -> dict:
    values = sorted(v for v in values if v is not None)
    if not values:
        return {"n": 0}

    def q(p: float) -> float:
        return values[min(len(values) - 1, max(0, int(round(p * (len(values) - 1)))))]

    return {"n": len(values), "min": values[0], "p25": q(0.25),
            "median": statistics.median(values), "p75": q(0.75), "p90": q(0.90),
            "p95": q(0.95), "p99": q(0.99), "max": values[-1],
            "count_ge_050": sum(1 for v in values if v >= 0.5),
            "count_ge_060": sum(1 for v in values if v >= 0.6),
            "count_ge_080": sum(1 for v in values if v >= 0.8)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--repo", default=str(DEFAULT_REPO))
    parser.add_argument("--tree", required=True)
    parser.add_argument("--method", choices=["popen", "startproc"], default="popen")
    parser.add_argument("--condition", required=True, choices=["quiet", "cpu", "spawn"])
    parser.add_argument("--burners", type=int, default=8)
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    tree_src = Path(args.tree).resolve()
    module = build_fixture(repo)
    test_file = repo / SUITE
    root = Path(os.path.expandvars(args.root))
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    load = Load(args.condition, args.burners, args.samples * 4.0 + 60)
    samples: list[dict] = []
    failures: list[str] = []
    load.start()
    try:
        for index in range(1, args.samples + 1):
            project_root = root / f"sample-{index:03d}"
            project_root.mkdir(parents=True, exist_ok=True)
            try:
                row = sample(module, args.python, tree_src, project_root, args.method,
                             args.timeout)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"sample-{index:03d}: {type(exc).__name__}: {exc}")
                continue
            row.update({"sample": index, "condition": args.condition,
                        "method": args.method, "project": str(project_root / "fake-project"),
                        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
            samples.append(row)
            if index % 5 == 0:
                print(f"  {args.method}/{args.condition} {index}/{args.samples} "
                      f"q1={row['time_to_first_side_effect_seconds']} "
                      f"q2={row['immediate_exit_lifetime_seconds']}", flush=True)
    finally:
        load.stop()

    payload = {
        "script": "harness/measure_child_lifetime.py",
        "card": "I-14-E", "attempt": "a20260919-01",
        "method": args.method, "condition": args.condition, "load": load.describe(),
        "python": args.python, "tree_src": str(tree_src),
        "fixture_builder": f"{test_file}::_prepare_fake_launcher_project",
        "test_file_sha256": hashlib.sha256(test_file.read_bytes()).hexdigest(),
        "behaviors": BEHAVIORS,
        "hang_timeout_seconds": 0.5, "child_poll_milliseconds": 100,
        "note": ("Q1 = launch -> fake child's first side effect (behaviour selector); Q2 = "
                 "launch -> exit for a child already selecting the immediate-exit behaviour. "
                 "'popen' excludes, 'startproc' includes the PowerShell Start-Process overhead "
                 "the supervisor itself pays.  No supervisor and no watchdog are involved."),
        "samples": samples,
        "failures": failures,
        "stats": {
            "q1_time_to_first_side_effect": stats(
                [s["time_to_first_side_effect_seconds"] for s in samples]),
            "q2_immediate_exit_lifetime": stats(
                [s["immediate_exit_lifetime_seconds"] for s in samples]),
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload["stats"], indent=2))
    print("failures:", failures[:5], "total", len(failures))
    print("out:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
