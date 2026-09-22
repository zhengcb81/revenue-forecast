"""I-14-E-APPLY: R3 demonstration runner.

Two jobs, both against the FIXED iso tree, both leaving the test file byte-identical:

1. ``--demo`` reproduces the hung-child scenario and evaluates **node 1's own final
   assertion** (``len(child_started) == 2``) against the resulting real timeline, so
   the RED that criterion R3 claims is observed rather than argued.

2. ``--outer-timeout <s>`` / ``--criterion-timeout`` re-run node 1 and/or the
   non-vacuity node with an EXTENDED outer subprocess budget, to separate two
   different questions that the fixed 15 s budget conflates:
     * does the launcher ever finish at all under load (outer budget too small?), and
     * does the derived watchdog budget still catch the hung child once it does?
   This is a CONFIRMATION arm outside the frozen R1-R4 plan; the frozen arms are
   reported exactly as measured.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from load import Load  # noqa: E402

NODE1_BEHAVIORS = [{"sleep_seconds": 5, "exit_code": 0}, {"exit_code": 0}]
HUNG_BEHAVIORS = [{"sleep_seconds": 5, "exit_code": 0},
                  {"sleep_seconds": 30, "exit_code": 0},
                  {"exit_code": 0}]
NODE1_ASSERTION = 'assert len([event for event in events if event["status"] == "child_started"]) == 2'


def build_fixture(path: Path):
    spec = importlib.util.spec_from_file_location("iso_bootstrap_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def observe(module, tmp_path: Path, behaviors, outer_timeout: float,
            extend_inner: bool) -> dict:
    """Run one scenario with the REAL helpers from the fixed test file."""
    hang = module._derive_worker_hang_timeout_seconds(tmp_path)
    project = module._prepare_fake_launcher_project(tmp_path, behaviors)
    kwargs = {"timeout": outer_timeout,
              "worker_hang_timeout_seconds": hang,
              "child_poll_milliseconds": 100}
    if extend_inner:  # the confirmed complete fix also derives the outer budget
        kwargs["timeout"] = max(outer_timeout, 4.0 * hang + 9.0)
    started = time.perf_counter()
    timed_out = False
    try:
        completed = module._run_real_worker_launcher(project, **kwargs)
        rc = completed.returncode
        stderr_tail = (completed.stderr or "")[-400:]
    except Exception as exc:  # noqa: BLE001 - a timeout is a datum here
        timed_out = True
        rc = None
        stderr_tail = f"{type(exc).__name__}: {exc}"[:400]
    wall = time.perf_counter() - started
    events = module._launcher_events(project) if (
        project / ".source_catalog" / "worker_launcher_events.jsonl").exists() else []
    unresponsive = [e for e in events if e.get("status") == "child_unresponsive"]
    starts = [e for e in events if e.get("status") == "child_started"]
    return {
        "hang_timeout_seconds": hang,
        "outer_timeout_seconds": kwargs["timeout"],
        "launcher_returncode": rc,
        "launcher_timed_out": timed_out,
        "launcher_wall_seconds": round(wall, 3),
        "stderr_tail": stderr_tail,
        "statuses": [e.get("status") for e in events],
        "child_started_count": len(starts),
        "watchdog_kill_count": len(unresponsive),
        "watchdog_kill_reasons": sorted({e.get("reason") for e in unresponsive}),
        "watchdog_kill_uptimes": [e.get("uptime_seconds") for e in unresponsive],
        "node1_assertion": NODE1_ASSERTION,
        "node1_assertion_holds": len(starts) == 2,
        "node1_verdict_under_this_input": "GREEN" if len(starts) == 2 else "RED",
        "vacuous": len(unresponsive) == 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--condition", required=True, choices=["quiet", "cpu", "spawn"])
    parser.add_argument("--burners", type=int, default=8)
    parser.add_argument("--runs", type=int, default=4)
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mode", required=True,
                        choices=["node1-red-demo", "extended-outer"])
    parser.add_argument("--outer-timeout", type=float, default=15.0)
    parser.add_argument("--extend-inner", action="store_true")
    args = parser.parse_args(argv)

    suite = Path(args.suite).resolve()
    module = build_fixture(suite)
    root = Path(os.path.expandvars(args.root))
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    load = Load(args.condition, args.burners, args.runs * 60.0 + 60)
    rows: list[dict] = []
    load.start()
    try:
        for index in range(1, args.runs + 1):
            for scenario, behaviors, extend in (
                ("node1", NODE1_BEHAVIORS, False),
                ("hung_child", HUNG_BEHAVIORS, False),
            ):
                tmp_path = root / f"run-{index:02d}-{scenario}"
                tmp_path.mkdir(parents=True, exist_ok=True)
                row: dict = {"run": index, "scenario": scenario, "condition": args.condition,
                             "mode": args.mode}
                try:
                    row.update(observe(module, tmp_path, behaviors,
                                       args.outer_timeout, args.extend_inner))
                except Exception as exc:  # noqa: BLE001
                    row["error"] = f"{type(exc).__name__}: {exc}"
                rows.append(row)
                print(f"run{index} {scenario:11s} hang={row.get('hang_timeout_seconds')} "
                      f"outer={row.get('outer_timeout_seconds')} "
                      f"rc={row.get('launcher_returncode')} "
                      f"to={row.get('launcher_timed_out')} "
                      f"starts={row.get('child_started_count')} "
                      f"kills={row.get('watchdog_kill_count')} "
                      f"node1={row.get('node1_verdict_under_this_input')} "
                      f"wall={row.get('launcher_wall_seconds')} {row.get('error','')}",
                      flush=True)
    finally:
        load.stop()

    node1 = [r for r in rows if r["scenario"] == "node1"]
    hung = [r for r in rows if r["scenario"] == "hung_child"]
    payload = {
        "script": "harness/confirm_arms.py",
        "card": "I-14-E-APPLY", "attempt": "a20260921-01",
        "mode": args.mode, "condition": args.condition, "load": load.describe(),
        "suite": str(suite),
        "suite_sha256": __import__("hashlib").sha256(suite.read_bytes()).hexdigest(),
        "outer_timeout_seconds": args.outer_timeout,
        "extend_inner": args.extend_inner,
        "note": ("confirmation arm outside the frozen R1-R4 plan; the frozen arms are "
                 "reported as measured.  The test file is byte-identical to the fixed tree."),
        "runs": rows,
        "summary": {
            "node1_runs": len(node1), "hung_runs": len(hung),
            "node1_green": sum(1 for r in node1
                               if r.get("node1_verdict_under_this_input") == "GREEN"),
            "node1_red": sum(1 for r in node1
                             if r.get("node1_verdict_under_this_input") == "RED"),
            "node1_launcher_timeouts": sum(1 for r in node1 if r.get("launcher_timed_out")),
            "hung_caught": sum(1 for r in hung
                               if r.get("node1_verdict_under_this_input") == "RED"),
            "hung_vacuous": sum(1 for r in hung if r.get("vacuous")),
            "hung_launcher_timeouts": sum(1 for r in hung if r.get("launcher_timed_out")),
            "hang_timeouts_used": sorted({r.get("hang_timeout_seconds") for r in rows}),
            "node1_wall_median": (round(statistics.median(
                [r["launcher_wall_seconds"] for r in node1 if "launcher_wall_seconds" in r]), 3)
                if node1 else None),
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("summary:", json.dumps(payload["summary"]))
    print("out:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
