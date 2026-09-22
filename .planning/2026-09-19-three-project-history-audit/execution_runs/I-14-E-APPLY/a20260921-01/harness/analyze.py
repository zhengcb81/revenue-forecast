"""I-14-E-APPLY: evaluate the frozen robustness criteria R1-R4 against the bench arms.

Reads only artifacts written by this attempt plus the read-only I-14-E baseline, and
writes ``after/analysis.json`` + ``after/analysis.md``.

Criteria (oracle.md SS3, frozen before any run):
  R1  fixed node, +8 burners : green
  R2  fixed node, quiet      : green
  R3  non-vacuity node       : green == the hung child WAS terminated (watchdog fired,
                               kill lands on the derived budget, 3rd child_started exists,
                               so node 1's own `== 2` assertion is false under that input)
  R4  mutation (hard-coded 0.5 s), +8 burners : RED again
Plus the pre-registered secondary arms:
  B5  clock mutation (floor 2.0 s, i.e. not the measured tail) : RED => measurement load-bearing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
HOME = Path(os.environ["USERPROFILE"])
I14E_AFTER = (HOME / "Projects" / "revenue-forecast" / ".planning"
              / "2026-09-19-three-project-history-audit" / "execution_runs" / "I-14-E"
              / "a20260919-01" / "after")

ARMS = {
    "B1": ("bench-B1-fixed-quiet.json", "fixed", "quiet", "R2"),
    "B2": ("bench-B2-fixed-cpu8.json", "fixed", "cpu8", "R1"),
    "B3": ("bench-B3-mutant0.5-cpu8.json", "mutant-derivation-0.5", "cpu8", "R4"),
    "B5": ("bench-B5-clockmut-cpu8.json", "mutant-clock", "cpu8", "secondary"),
    "B4q": ("bench-B4-nonvacuity-quiet.json", "fixed-nonvacuity", "quiet", "R3"),
    "B4c": ("bench-B4-nonvacuity-cpu8.json", "fixed-nonvacuity", "cpu8", "R3"),
}


def load(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arm_summary(payload: dict) -> dict:
    rows = payload["results"]
    derivations = [r["derivation"] for r in rows if r.get("derivation", {}).get("report_present")]
    kills = []
    for r in rows:
        kills.extend(r["events"].get("watchdog_kill_uptimes") or [])
    return {
        "arm_file": payload.get("_file"),
        "node": payload["node"],
        "condition": payload["condition"],
        "load": payload["load"],
        "suite_sha256": payload["suite_sha256"],
        "tree_suite_sha256": payload["tree_suite_sha256"],
        "started_utc": payload["started_utc"],
        "tally": payload["tally_by_condition"],
        "tally_by_tree": payload["tally_by_tree"],
        "tally_by_pass": payload["tally_by_pass"],
        "hang_timeouts_actually_used": sorted(
            {r["events"].get("hang_timeout_seconds_actually_used") for r in rows
             if r["events"].get("events_present")}),
        "poll_ms_actually_used": sorted(
            {r["events"].get("child_poll_ms_actually_used") for r in rows
             if r["events"].get("events_present")}),
        "child_started_counts": sorted({r["events"].get("child_started_count") for r in rows}),
        "watchdog_kill_count_total": len(kills),
        "watchdog_kill_uptimes": sorted(kills),
        "verdicts": sorted({r["verdict"] for r in rows}),
        "assertions_seen": sorted({r["assertion"] for r in rows if r["assertion"]})[:6],
        "pass_but_slow": [r["run"] for r in rows if r.get("pass_but_slow")],
        "wall_seconds": {
            "min": min(r["wall_seconds"] for r in rows),
            "median": round(statistics.median(r["wall_seconds"] for r in rows), 3),
            "max": max(r["wall_seconds"] for r in rows),
        },
        "derivation": {
            "reports": len(derivations),
            "t0_seconds": sorted({d.get("t0_seconds") for d in derivations}),
            "hang_timeout_seconds": sorted({d.get("hang_timeout_seconds") for d in derivations}),
            "samples_seconds_all": sorted(
                s for d in derivations for s in (d.get("samples_seconds") or [])),
            "ceiling_hit_runs": sum(
                1 for d in derivations
                if d.get("derived_before_ceiling_seconds") == d.get("ceiling_seconds")),
        },
        "runs": [{
            "pass": r["pass"], "tree": r["tree"], "run": r["run"], "verdict": r["verdict"],
            "wall_seconds": r["wall_seconds"], "assertion": r["assertion"],
            "child_started": r["events"].get("child_started_count"),
            "child_unresponsive": r["events"].get("child_unresponsive_count"),
            "kill_uptimes": r["events"].get("watchdog_kill_uptimes"),
            "kill_reasons": r["events"].get("watchdog_kill_reasons"),
            "hang_used": r["events"].get("hang_timeout_seconds_actually_used"),
            "t0": r.get("derivation", {}).get("t0_seconds"),
            "derived": r.get("derivation", {}).get("hang_timeout_seconds"),
            "load_probe": r["load_probe"],
        } for r in rows],
    }


def non_vacuity_checks(summary: dict) -> dict:
    runs = summary["runs"]
    per_run = []
    for r in runs:
        kills = r["kill_uptimes"] or []
        hang = r["hang_used"]
        per_run.append({
            "pass": r["pass"], "tree": r["tree"], "run": r["run"],
            "verdict": r["verdict"],
            "hang_used": hang,
            "a_watchdog_fired": bool(kills),
            "b_kill_reasons_all_session_start_timeout": (
                bool(r["kill_reasons"]) and all(x == "session_start_timeout"
                                                for x in r["kill_reasons"])),
            "b_kill_within_budget_plus_slack": bool(kills) and hang is not None and all(
                k is not None and k <= hang + 1.0 for k in kills),
            "c_child_started_is_3": r["child_started"] == 3,
            "c_node1_assertion_would_be_false": r["child_started"] != 2,
            "kills": kills,
        })
    return {
        "per_run": per_run,
        "n": len(per_run),
        "a_all_fired": all(p["a_watchdog_fired"] for p in per_run) and bool(per_run),
        "b_all_reason_and_budget": all(
            p["b_kill_reasons_all_session_start_timeout"]
            and p["b_kill_within_budget_plus_slack"] for p in per_run) and bool(per_run),
        "c_all_three_starts": all(p["c_child_started_is_3"] for p in per_run) and bool(per_run),
        "node1_assertion_false_in_all": all(
            p["c_node1_assertion_would_be_false"] for p in per_run) and bool(per_run),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(ATT / "after" / "analysis.json"))
    parser.add_argument("--md", default=str(ATT / "after" / "analysis.md"))
    args = parser.parse_args(argv)

    summaries: dict[str, dict] = {}
    for key, (fname, _kind, _cond, _crit) in ARMS.items():
        path = ATT / "after" / fname
        payload = load(path)
        if payload is None:
            summaries[key] = {"arm_file": fname, "missing": True}
            continue
        payload["_file"] = fname
        summaries[key] = arm_summary(payload)

    # ---- pre-fix baseline, straight out of the sealed I-14-E artifacts ----
    baseline = {}
    for name, fname in (("quiet", "band-child-quiet.json"),
                        ("cpu8", "band-child-cpu8.json")):
        payload = load(I14E_AFTER / fname)
        if payload is None:
            baseline[name] = {"missing": True}
            continue
        baseline[name] = {
            "source": str(I14E_AFTER / fname),
            "source_sha256": sha256(I14E_AFTER / fname),
            "suite_sha256": payload["suite_sha256"],
            "hang_timeout_seconds": 0.5,
            "tally": payload["tally_by_condition"],
            "tally_by_tree": payload["tally_by_tree"],
            "note": ("pre-fix reference measured on the byte-identical production test file "
                     "by I-14-E; different load window, same load SHAPE (+8 burners)"),
        }

    # ---- the four frozen criteria ----
    criteria: dict[str, dict] = {}

    def green_rate(key: str) -> tuple[int, int, bool]:
        s = summaries.get(key, {})
        if s.get("missing"):
            return 0, 0, False
        t = s["tally"]
        n = t["runs"]
        g = t["passed"]
        return g, n, (n > 0 and g == n)

    g, n, ok = green_rate("B2")
    s2 = summaries.get("B2", {})
    hang2 = (s2.get("hang_timeouts_actually_used") or [None])[0]
    # the wall-time accounting that the 15 s outer budget has to cover, from the
    # node's OWN structure (first child sleeps 5 s, the watchdog burns `hang` before
    # killing it, the replacement child costs at least one more launch + its own exit)
    arithmetic = None
    if hang2:
        arithmetic = {
            "outer_budget_seconds": 15.0,
            "first_child_sleep_seconds": 5.0,
            "hang_seconds_used": hang2,
            "unavoidable_lower_bound_seconds": round(5.0 + hang2, 3),
            "also_needs": "a second launch + the replacement child's own lifetime",
            "measured_second_child_launch_p50_seconds": 1.351,
            "conclusion": ("the launcher's minimum wall time exceeds the node's own 15 s "
                           "subprocess budget once its `hang` budget is raised to the "
                           "measured ceiling"),
        }
    criteria["R1"] = {
        "statement": "fixed node, +8 burners: N/N green (no more load-dependent red)",
        "arm": "B2", "passed": g, "runs": n, "holds": ok,
        "baseline_pre_fix": baseline.get("cpu8", {}).get("tally"),
        "failure_mode_of_the_one_red": ("launcher-subprocess-timeout at the node's own "
                                        "hard-coded timeout=15, with 1 child_started and "
                                        "0 watchdog kills"),
        "wall_time_arithmetic": arithmetic,
    }
    g, n, ok = green_rate("B1")
    criteria["R2"] = {
        "statement": "fixed node, quiet: N/N green (no regression when the machine is idle)",
        "arm": "B1", "passed": g, "runs": n, "holds": ok,
        "baseline_pre_fix": baseline.get("quiet", {}).get("tally"),
    }
    nv_q = non_vacuity_checks(summaries["B4q"]) if not summaries["B4q"].get("missing") else None
    nv_c = non_vacuity_checks(summaries["B4c"]) if not summaries["B4c"].get("missing") else None
    r3_holds = bool(
        nv_q and nv_c and nv_q["n"] and nv_c["n"]
        and nv_q["a_all_fired"] and nv_q["b_all_reason_and_budget"] and nv_q["c_all_three_starts"]
        and nv_c["a_all_fired"] and nv_c["b_all_reason_and_budget"] and nv_c["c_all_three_starts"])
    criteria["R3"] = {
        "statement": ("a genuinely hung child is still caught: the derived timeout fires, the "
                      "kill lands on the derived budget, a 3rd child_started appears, so node "
                      "1's own `== 2` assertion is FALSE under that input"),
        "arms": ["B4q", "B4c"], "holds": r3_holds,
        "quiet": nv_q, "cpu8": nv_c,
    }
    s3 = summaries["B3"]
    if s3.get("missing"):
        r4_holds = False
        b3_detail = {"missing": True}
    else:
        t = s3["tally"]
        b3_detail = {"tally": t, "hang_used": s3["hang_timeouts_actually_used"],
                     "assertions_seen": s3["assertions_seen"][:3]}
        r4_holds = (t["runs"] > 0 and t["passed"] <= t["runs"] // 2)
    criteria["R4"] = {
        "statement": ("mutation proof: revert the derivation to the fixed 0.5 s under the same "
                      "+8 burners and the node must go RED again"),
        "arm": "B3", "holds": r4_holds, "detail": b3_detail,
        "baseline_pre_fix": baseline.get("cpu8", {}).get("tally"),
    }
    s5 = summaries["B5"]
    if s5.get("missing"):
        b5_holds = None
    else:
        t = s5["tally"]
        b5_holds = t["passed"] <= t["runs"] // 2
    criteria["B5_secondary"] = {
        "statement": ("timing-mutation sensitivity: with the derived budget collapsed to the "
                      "2.0 s floor (i.e. NOT the measured tail), the node under load must be "
                      "RED; if it were green the measurement would not be load-bearing"),
        "arm": "B5", "holds": b5_holds,
        "tally": None if s5.get("missing") else s5["tally"],
        "hang_used": None if s5.get("missing") else s5["hang_timeouts_actually_used"],
    }

    demo = None  # superseded by the confirmation arms below
    confirm = load(ATT / "after" / "confirm-node1-red-on-hung-child.json")
    confirm2 = load(ATT / "after" / "confirm-extended-outer-timeout.json")

    # ---- overall verdict against the frozen criteria ----
    hard = {k: criteria[k]["holds"] for k in ("R1", "R2", "R3", "R4")}
    secondary = {k: criteria[k]["holds"] for k in ("B5_secondary",)}
    all_hard_hold = all(v is True for v in hard.values())
    verdict = ("criteria_met" if all_hard_hold else "criteria_not_met")

    payload = {
        "card": "I-14-E-APPLY", "attempt": "a20260921-01",
        "generated_by": "harness/analyze.py",
        "oracle_sha256": sha256(ATT / "oracle.md"),
        "fixed_suite_sha256": sha256(
            ATT / "iso" / "T0" / "tests" / "contract"
            / "test_source_catalog_worker_bootstrap.py"),
        "arms": summaries,
        "pre_fix_baseline": baseline,
        "criteria": criteria,
        "hard_criteria": hard,
        "all_hard_criteria_hold": all_hard_hold,
        "verdict": verdict,
        "confirmation_arms": {
            "node1_red_demo": confirm,
            "extended_outer_timeout": confirm2,
            "role": ("outside the frozen R1-R4 plan; they separate the two questions the "
                     "frozen arms conflate (is the derivation non-vacuous? is the outer 15 s "
                     "budget the new binding constraint?)"),
        },
        "pre_fix_frozen_band_note": (
            "the frozen band (I-14-C r5) and I-14-E's own bands are the pre-fix reference; the "
            "frozen band's 12/48 failures were all `assert ... == 2` on the byte-identical "
            "file, so the comparison is between the same assertion under two budgets"),
    }
    out = Path(args.out)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def fmt_tally(t: dict | None) -> str:
        if not t:
            return "n/a"
        return (f"{t['passed']}/{t['runs']} pass "
                f"({t['failed']} fail, {t['timeout']} timeout, {t['error']} err)")

    lines = [
        "# I-14-E-APPLY analysis — derived test-side timing fix",
        "",
        f"- fixed suite sha256: `{payload['fixed_suite_sha256']}`",
        f"- oracle sha256: `{payload['oracle_sha256']}`",
        "",
        "## Arm results",
        "",
        "| arm | node | condition | result | hang timeout used |",
        "|---|---|---|---|---|",
    ]
    for key, (_f, kind, cond, crit) in ARMS.items():
        s = summaries[key]
        if s.get("missing"):
            lines.append(f"| {key} | {kind} | {cond} | MISSING | — |")
            continue
        lines.append(f"| {key} | {s['node']} | {s['condition']} | {fmt_tally(s['tally'])} | "
                     f"{s['hang_timeouts_actually_used']} |")
    lines += ["", "## Criteria (frozen before the run)", ""]
    for name, block in criteria.items():
        lines.append(f"- **{name}**: holds = `{block['holds']}` — {block['statement']}")
    lines += ["", f"**Overall verdict: `{verdict}`** "
                  f"(hard criteria all hold = `{all_hard_hold}`)", ""]
    if confirm:
        s = confirm.get("summary", {})
        lines += ["## Confirmation arm A: node 1's own assertion on a hung child (R3 direct)", "",
                  f"- runs: {s.get('node1_runs')} node-1 scenarios, {s.get('hung_runs')} hung scenarios",
                  f"- node 1 verdict under the hung input: RED {s.get('node1_red')} / "
                  f"GREEN {s.get('node1_green')}",
                  f"- hung child caught (node 1 would be RED): {s.get('hung_caught')} / "
                  f"{s.get('hung_runs')}; vacuous {s.get('hung_vacuous')}",
                  f"- hang budgets used: {s.get('hang_timeouts_used')}", ""]
    if confirm2:
        s = confirm2.get("summary", {})
        lines += ["## Confirmation arm B: extended outer budget", "",
                  f"- node 1: green {s.get('node1_green')} / red {s.get('node1_red')} "
                  f"of {s.get('node1_runs')}; launcher timeouts {s.get('node1_launcher_timeouts')}",
                  f"- hung child caught: {s.get('hung_caught')} / {s.get('hung_runs')} "
                  f"(vacuous {s.get('hung_vacuous')})",
                  f"- hang budgets used: {s.get('hang_timeouts_used')}", ""]
    lines += ["", "## Pre-fix baseline (I-14-E, sealed)", ""]
    for name, block in baseline.items():
        if block.get("missing"):
            lines.append(f"- {name}: MISSING")
            continue
        lines.append(f"- {name}: {fmt_tally(block['tally'])} with hang timeout "
                     f"{block['hang_timeout_seconds']} s")
    md = Path(args.md)
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("out:", out)
    print("md:", md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
