"""I-14-E: assemble after/fail-able-cases.json (card item 4) + the determinism verdict (B3).

One fail-able case per restart node, each carrying:
  * the product test nodeid and the exact timing assumption it rests on
  * the measured window for that assumption (this attempt's own numbers)
  * the reproductions observed in this attempt (which runs, what signature)
  * the artifact-level proof of the cause (from collect_artifacts.py output)
  * the minimal command that reproduces it
and, at the top level, the determinism verdict the parent's CF-I14F-X1 / addendum B3 asks for.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
AFTER = ATTEMPT / "after"
EVIDENCE = ATTEMPT / "evidence"
OUT = AFTER / "fail-able-cases.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def main() -> int:
    frozen = load(EVIDENCE / "frozen_band_raw_record.json")
    ma = {name: load(AFTER / f"child-lifetime-{name}.json")
          for name in ("popen-quiet", "popen-cpu8", "popen-cpu12",
                       "startproc-quiet", "startproc-cpu8")}
    bands = {name: load(AFTER / f"band-{name}.json")
             for name in ("child-quiet", "child-cpu8", "child-spawn",
                          "logon-quiet", "logon-cpu8")}
    artifacts = {name: load(AFTER / f"artifacts-{name}.json")
                 for name in ("child-quiet", "child-cpu8", "child-spawn",
                              "logon-quiet", "logon-cpu8")}
    wrapper = {name: load(AFTER / f"wrapper-latency-{name}.json")
               for name in ("quiet", "cpu8")}

    def failures(band_name: str) -> list[dict]:
        payload = bands.get(band_name)
        if not payload:
            return []
        return [r for r in payload["results"] if r["verdict"] != "passed"]

    def signature(row: dict) -> str:
        assertion = row.get("assertion") or ""
        if "TimeoutExpired" in assertion:
            return "launcher-subprocess-TimeoutExpired(15s)"
        if "child_started" in assertion:
            return f"assert-child_started==2(failed with {assertion.split('==')[-1].strip()})"
        return assertion[:80] or "other"

    cases: list[dict] = []

    # ---------------- node 1 ----------------
    node1_repro = []
    for band_name in ("child-quiet", "child-cpu8", "child-spawn"):
        payload = bands.get(band_name)
        if not payload:
            continue
        for row in failures(band_name):
            node1_repro.append({
                "band": band_name, "pass": row["pass"], "tree": row["tree"], "run": row["run"],
                "verdict": row["verdict"], "signature": signature(row),
                "child_started_count": (row.get("events") or {}).get("child_started_count"),
                "wall_seconds": row["wall_seconds"],
                "kill_uptimes": [a.get("unresponsive_uptime_seconds")
                                 for a in (row.get("events") or {}).get("attempts", [])
                                 if a.get("unresponsive_uptime_seconds") is not None],
            })
    q2 = (ma.get("popen-quiet") or {}).get("stats", {}).get("q2_immediate_exit_lifetime", {})
    q2_cpu = (ma.get("popen-cpu8") or {}).get("stats", {}).get("q2_immediate_exit_lifetime", {})
    cases.append({
        "case_id": "I-14-E-FC-1",
        "node": "child_without_runtime",
        "nodeid": ("tests/contract/test_source_catalog_worker_bootstrap.py::"
                   "test_child_without_runtime_session_is_terminated_and_restarted"),
        "timing_assumption": ("-WorkerHangTimeoutSeconds 0.5 with -ChildPollMilliseconds 100: a child "
                              "with no matching runtime session that is still alive at a poll "
                              "boundary after 0.5 s of uptime is killed as session_start_timeout"),
        "measured_window": {
            "quiet": q2, "cpu8": q2_cpu,
            "startproc_quiet": (ma.get("startproc-quiet") or {}).get(
                "stats", {}).get("q2_immediate_exit_lifetime", {}),
            "frozen_band_same_quantity": (frozen or {}).get(
                "noop_child_lifetime_seconds"),
        },
        "reproductions_this_attempt": node1_repro,
        "reproduction_count": len(node1_repro),
        "minimal_command": (
            "iso/venv/Scripts/python.exe -X utf8 harness/run_band.py --python "
            "iso/venv/Scripts/python.exe --repo <CW> --node child_without_runtime "
            "--condition quiet --trees T0=iso/T0/src --runs 1 --passes 1 "
            "--root %TEMP%/i14e-repro-child --evidence after/repro --out after/repro.json"),
        "artifact_proof": {name: (artifacts.get(name) or {}).get("summary")
                           for name in ("child-quiet", "child-cpu8", "child-spawn")},
        "diagnosis": ("the test's 0.5 s hang timeout is compared against a quantity "
                      "(fake child launch -> exit, and launch -> first side effect) whose measured "
                      "distribution straddles that value: 24/30 quiet samples >= 0.5 s and 25/25 "
                      "under +8 burners, with a measured upper tail of 1.7-2.5 s.  Every extra "
                      "watchdog kill adds a child_started, so `assert ... == 2` fails; under "
                      "heavier load the restarts continue until the test's own 15 s subprocess "
                      "timeout fires"),
        "green_would_require": ("a test-side change (the card forbids it here): derive the hang "
                                "timeout from an in-test measurement of the child's launch latency "
                                "with margin - see after/proposed-test-side-change.md"),
    })

    # ---------------- node 2 ----------------
    node2_repro = []
    for band_name in ("logon-quiet", "logon-cpu8"):
        payload = bands.get(band_name)
        if not payload:
            continue
        for row in failures(band_name):
            node2_repro.append({
                "band": band_name, "pass": row["pass"], "tree": row["tree"], "run": row["run"],
                "verdict": row["verdict"], "signature": signature(row),
                "wall_seconds": row["wall_seconds"],
                "statuses": (row.get("events") or {}).get("statuses"),
            })
    probe_repro = []
    for name, payload in wrapper.items():
        if not payload:
            continue
        for sample in payload["samples"]:
            if not sample.get("child_started_seen"):
                probe_repro.append({
                    "probe": f"wrapper-latency-{name}", "sample": sample["sample"],
                    "wrapper_seconds": sample.get("wrapper_seconds"),
                    "events_seconds": sample.get("events_seconds"),
                    "statuses": sample.get("statuses"),
                    "budget_seconds": payload["budgets"]["events_budget_seconds"],
                })
    cases.append({
        "case_id": "I-14-E-FC-2",
        "node": "logon_wrapper_quoted",
        "nodeid": ("tests/contract/test_source_catalog_worker_bootstrap.py::"
                   "test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths"),
        "timing_assumption": ("subprocess.run(wrapper, timeout=15) + a 15 s wait for the detached "
                              "supervisor's first child_started + a 20 s wait for supervisor and "
                              "child to disappear, against a fake child that sleeps 10 s"),
        "measured_window": {name: (payload or {}).get("stats")
                            for name, payload in wrapper.items()},
        "measured_budgets": (wrapper.get("quiet") or {}).get("budgets"),
        "reproductions_this_attempt": node2_repro,
        "reproduction_count": len(node2_repro),
        "probe_level_reproductions": probe_repro,
        "probe_level_reproduction_count": len(probe_repro),
        "end_to_end_status": ("the node itself passed 16/16 (8 quiet + 8 with +8 burners), so at "
                              "the node level this attempt found NO fail-able case; the direct "
                              "window probe did cross the 15 s events budget in 6/8 loaded "
                              "samples.  The two disagree and are reported side by side rather "
                              "than merged into one claim"),
        "minimal_command": (
            "iso/venv/Scripts/python.exe -X utf8 harness/measure_wrapper_latency.py --python "
            "iso/venv/Scripts/python.exe --condition cpu --burners 8 --samples 8 "
            "--root %TEMP%/i14e-repro-logon --out after/repro-logon.json"),
        "artifact_proof": {name: (artifacts.get(name) or {}).get("summary")
                           for name in ("logon-quiet", "logon-cpu8")},
        "diagnosis": ("the wrapper itself keeps a 1.4x margin even under +8 burners, but the "
                      "detached supervisor's first child_started did not appear inside the 15 s "
                      "budget in 6/8 loaded probe samples (only `starting` was written), and the "
                      "20 s exit budget was crossed in 4/8 quiet samples by this probe's own "
                      "upper-bound timing (the probe spends up to two PowerShell spawns per poll, "
                      "so treat the exit numbers as upper bounds)"),
        "green_would_require": ("derive all three budgets from a measured wrapper/supervisor "
                                "latency instead of the fixed 15/15/20 s - see "
                                "after/proposed-test-side-change.md"),
    })

    # ---------------- determinism verdict (addendum B3) ----------------
    frozen_kill = (frozen or {}).get("second_attempt_uptime_seconds", {})
    frozen_pass = (frozen or {}).get("noop_child_lifetime_seconds", {}).get("passed_runs", {})
    determinism = {
        "question": ("can the jitter band be characterised deterministically, or is it a "
                     "load-dependent distribution?"),
        "verdict": "distributional",
        "why": [
            ("the discriminating quantity is a latency (fake child launch -> exit), and its "
             "measured distribution moves with machine load: quiet median %.3f s vs +8 burners "
             "median %.3f s (popen), with maxima 1.72 s / 2.30 s"
             % ((q2 or {}).get("median", float("nan")), (q2_cpu or {}).get("median", float("nan")))),
            ("the product test does not compare against the latency directly: it compares against "
             "'still alive at a poll boundary after 0.5 s', so the effective boundary carries a "
             "~100 ms ambiguity window from the poll cadence - the frozen band itself contains a "
             "run that exited cleanly at uptime %.3f s and runs killed at %.3f s"
             % (frozen_pass.get("max", float("nan")), frozen_kill.get("min", float("nan")))),
            ("therefore no single threshold constant is stable across loads: a value that makes "
             "the node green on an idle machine still fails on a loaded one (this attempt: "
             "near-100%% failures with the same test file and byte-identical trees)"),
        ],
        "what_is_deterministic": [
            "the mechanism (watchdog verdict on a child that is alive at a poll boundary after "
            "0.5 s of uptime, counted through the number of child_started events)",
            "the direction of the load response (more load -> higher latency -> more watchdog "
            "kills -> more restarts)",
            "the failure signature ladder: assert 3 == 2 / 4 == 2 at moderate load, then "
            "launcher-subprocess-TimeoutExpired(15 s) at heavy load",
        ],
        "what_is_not_deterministic": [
            "the pass/fail outcome of any single run, which depends on where the child's exit "
            "lands relative to the poll cadence",
            "any fixed timeout constant chosen without measuring the latency distribution on the "
            "target machine",
        ],
    }

    payload = {
        "card": "I-14-E", "attempt": "a20260919-01",
        "status": "review_pending (implementer does not self-sign)",
        "scope_note": ("fail-able cases are reproductions of the product test's own timing "
                       "assumption failing under measured load.  No product code and no product "
                       "test was changed; the GREEN path is proposed, not applied."),
        "cases": cases,
        "determinism_verdict": determinism,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"cases": [{"id": c["case_id"], "reproductions": c["reproduction_count"]}
                                for c in cases],
                      "determinism": determinism["verdict"]}, indent=2, ensure_ascii=False))
    print("out:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
