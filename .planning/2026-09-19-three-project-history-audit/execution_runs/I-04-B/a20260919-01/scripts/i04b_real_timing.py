"""I-04-B epsilon re-measurement (revision 2) + real request/cleanup trajectories.

Review findings addressed:
  F-B4B-07  the sessions must be genuinely time-separated and the p95 definition explicit
  F-B4B-08  RAW samples must be retained so a reviewer can recompute p95 independently

Usage (two INVOCATIONS, separated in time, then merge):
  python i04b_real_timing.py --session quiet   --out after/epsilon_session1.json
  python i04b_real_timing.py --session load    --out after/epsilon_session2.json
  python i04b_real_timing.py --merge after/epsilon_session1.json after/epsilon_session2.json \
         --out after/i04b_real_timing.json

p95 definition (stated explicitly, no interpolation): the value at index
int(0.95 * (n - 1)) of the ASCENDING sorted sample - the nearest-rank-below convention
used by I-04-A, so both cards' numbers are computed the same way.
epsilon := 2 * max(p95 over every case and session), capped at 2.0 s.
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "filing-fetch"
N = 50
PYTHON = sys.executable
sys.path.insert(0, str(ISO / "scripts"))
CASES = ("startup_s", "cli_import_s", "sleep_overshoot_s", "kill_reap_overshoot_s")


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[int(0.95 * (len(ordered) - 1))]


def _spawn(code: str, timeout: float | None = None) -> tuple[float, str]:
    start = time.monotonic()
    try:
        proc = subprocess.run([PYTHON, "-X", "utf8", "-B", "-c", code],
                              capture_output=True, text=True, timeout=timeout)
        return time.monotonic() - start, ("ok" if proc.returncode == 0
                                          else f"rc={proc.returncode}")
    except subprocess.TimeoutExpired:
        return time.monotonic() - start, "timeout"


def run_session(load: bool) -> dict:
    load_procs = []
    if load:
        for _ in range(4):
            load_procs.append(subprocess.Popen(
                [PYTHON, "-X", "utf8", "-B", "-c", "sum(range(8_000_000))"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    try:
        samples: dict[str, list[float]] = {case: [] for case in CASES}
        for _ in range(N):
            samples["startup_s"].append(_spawn("pass")[0])
        for _ in range(N):
            samples["cli_import_s"].append(_spawn(
                f"import sys; sys.path.insert(0, {str(ISO / 'scripts')!r}; "
                "import fetch_filing")[0])
        for _ in range(N):
            elapsed, _status = _spawn("import time; time.sleep(0.25)")
            samples["sleep_overshoot_s"].append(elapsed - 0.25)
        for _ in range(N):
            elapsed, status = _spawn("import time; time.sleep(3.0)", timeout=0.3)
            if status != "timeout":
                raise SystemExit(f"kill/reap probe did not time out: {status}")
            samples["kill_reap_overshoot_s"].append(elapsed - 0.3)
    finally:
        for proc in load_procs:
            proc.kill()
        for proc in load_procs:
            proc.wait()
    return samples


def summarise(samples: dict[str, list[float]]) -> dict:
    return {
        case: {
            "n": len(values),
            "min": round(min(values), 4),
            "median": round(statistics.median(values), 4),
            "p95": round(p95(values), 4),
            "max": round(max(values), 4),
            "raw": [round(value, 6) for value in values],
        }
        for case, values in samples.items()
    }


def trajectory(base: Path) -> dict:
    """F-B4c: request segment vs cleanup segment of real processes, with phase wall."""
    from fetch_filing import PausedWorkerScope, _normalize_stats

    root = base / "company-wiki"
    (root / "config").mkdir(parents=True)
    (root / "config" / "source_catalog.yaml").write_text("schema_version: '1.0'\n",
                                                        encoding="utf-8")
    slow = base / "slow_status.py"
    slow.write_text("import json, time\ntime.sleep(3.0)\n"
                    "print(json.dumps({'runtime_state': 'running'}))\n", encoding="utf-8")
    resume = base / "resume_stub.py"
    resume.write_text("import json, sys, time\ntime.sleep(0.30)\n"
                      "print(json.dumps({'status': 'running'}))\nsys.exit(0)\n",
                      encoding="utf-8")

    budget = 0.6
    stats = _normalize_stats({})
    scope = PausedWorkerScope(
        root=root, command_prefix=[PYTHON, "-X", "utf8", "-B", str(slow)],
        enabled=True, graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
        deadline=time.monotonic() + budget, stats=stats,
    )
    request_start = time.monotonic()
    scope.__enter__()
    request_end = time.monotonic()

    cleanup_scope = PausedWorkerScope(
        root=root, command_prefix=[PYTHON, "-X", "utf8", "-B", str(resume)],
        enabled=True, graceful_timeout_seconds=5.0, resume_wait_seconds=5.0,
        deadline=time.monotonic() + 30.0, stats=stats,
    )
    cleanup_scope._register(joined=False)
    cleanup_scope.action = "paused_by_us"
    cleanup_start = time.monotonic()
    cleanup_scope.__exit__(None, None, None)
    cleanup_end = time.monotonic()

    return {
        "request_segment": {
            "budget_s": budget,
            "start_monotonic": round(request_start, 6),
            "end_monotonic": round(request_end, 6),
            "observed_s": round(request_end - request_start, 4),
            "action": scope.action,
        },
        "cleanup_subcall": {
            "cleanup_elapsed_seconds": stats.get("cleanup_elapsed_seconds"),
            "cleanup_calls": stats.get("cleanup_calls"),
            "cleanup_status": stats.get("cleanup_status"),
            "pause_action": stats.get("pause_action"),
        },
        "cleanup_phase_wall": {
            "start_monotonic": round(cleanup_start, 6),
            "end_monotonic": round(cleanup_end, 6),
            "observed_s": round(cleanup_end - cleanup_start, 4),
            "note": ("the phase wall also contains one tasklist liveness probe per "
                     "refcount entry; it is REPORTED and never bounded by an acceptance "
                     "cap (I-04-A re-sign carry)"),
        },
        "separation": {
            "cleanup_elapsed_key_present": "cleanup_elapsed_seconds" in stats,
            "request_elapsed_key_present": "request_elapsed" in stats,
            "note": ("the unit path has no main(); the envelope-level proof of two "
                     "independent keys is test_i04b_f_b4c_envelope_reports_request_and_"
                     "cleanup_separately"),
        },
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--session", choices=("quiet", "load"))
    parser.add_argument("--merge", nargs="*", type=Path, default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.session:
        samples = run_session(load=args.session == "load")
        record = {
            "artifact": "I-04-B epsilon re-measurement (single session)",
            "session": args.session,
            "session_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_started_monotonic": round(time.monotonic(), 3),
            "n_per_case": N,
            "p95_definition": "sorted ascending, index int(0.95*(n-1)); no interpolation",
            "cases": summarise(samples),
        }
        args.out.write_text(json.dumps(record, ensure_ascii=True, indent=2) + "\n",
                            encoding="utf-8")
        print(json.dumps({case: record["cases"][case]["p95"] for case in CASES},
                         ensure_ascii=True, indent=2))
        return 0

    if args.merge:
        sessions = [json.loads(path.read_text(encoding="utf-8")) for path in args.merge]
        pooled = {case: [] for case in CASES}
        for session in sessions:
            for case in CASES:
                pooled[case].extend(session["cases"][case]["raw"])
        worst = max(p95(values) for values in pooled.values())
        with tempfile.TemporaryDirectory() as temporary:
            traj = trajectory(Path(temporary))
        record = {
            "artifact": "I-04-B real-process timing + epsilon re-measurement (merged)",
            "interpreter": PYTHON,
            "sessions": [
                {"session": session["session"],
                 "started_utc": session["session_started_utc"],
                 "started_monotonic": session["session_started_monotonic"],
                 "n_per_case": session["n_per_case"]}
                for session in sessions
            ],
            "p95_definition": "sorted ascending, index int(0.95*(n-1)); no interpolation",
            "pooled": {case: {"n": len(values), "p95": round(p95(values), 4)}
                       for case, values in pooled.items()},
            "worst_p95_s": round(worst, 4),
            "epsilon_re_measured_s": round(min(2.0, 2.0 * worst), 2),
            "epsilon_rule": ("epsilon := 2*max(p95 over every case and session), capped at "
                             "2 s; the re-signing trigger is this pre-committed program, "
                             "never a failed test, and no further loosening is allowed"),
            "trajectory": traj,
            "ran_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        args.out.write_text(json.dumps(record, ensure_ascii=True, indent=2) + "\n",
                            encoding="utf-8")
        print(json.dumps({"epsilon_re_measured_s": record["epsilon_re_measured_s"],
                          "worst_p95_s": record["worst_p95_s"],
                          "sessions": [s["session"] for s in record["sessions"]],
                          "trajectory": traj}, ensure_ascii=True, indent=2))
        return 0

    parser.error("either --session or --merge is required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
