"""I-14-E: turn the campaign's raw JSON into the per-hypothesis verdicts.

Reads only the attempt's own evidence (plus the frozen band's raw record, which is itself
inside the attempt) and applies the decision rules written down in ``oracle.md`` sections 3/5
and ``oracle-addendum-B.md`` BEFORE the runs.  Writes ``after/analysis.json`` and
``after/analysis.md``.

Nothing here executes the SUT: the numbers are read from the recorded runs.
"""

from __future__ import annotations

import json
import math
import re
import statistics
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
AFTER = ATTEMPT / "after"
EVIDENCE = ATTEMPT / "evidence"
OUT_JSON = AFTER / "analysis.json"
OUT_MD = AFTER / "analysis.md"

HANG_TIMEOUT = 0.5
POLL_MS = 100


def load(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def rate_block(rows: list[dict]) -> dict:
    n = len(rows)
    failed = sum(1 for r in rows if r["verdict"] != "passed")
    lo, hi = wilson(failed, n)
    return {"runs": n, "failed": failed, "passed": n - failed,
            "failure_rate": round(failed / n, 4) if n else None,
            "wilson95": [round(lo, 4), round(hi, 4)]}


def by(rows: list[dict], key) -> dict:
    out: dict = {}
    for row in rows:
        out.setdefault(key(row), []).append(row)
    return out


def probe_series(rows: list[dict], key: str) -> list[float]:
    values = []
    for row in rows:
        value = (row.get("load_probe") or {}).get(key)
        if isinstance(value, (int, float)):
            values.append(float(value))
    return values


def classify_failure(row: dict) -> str:
    assertion = (row.get("assertion") or "")
    if "TimeoutExpired" in assertion:
        return "outer-15s-TimeoutExpired"
    if "child_started" in assertion or re.search(r"assert \d+ == 2", assertion):
        count = (row.get("events") or {}).get("child_started_count")
        return f"assert-child_started-count({count})"
    if row.get("verdict") == "timeout" or row.get("returncode") is None:
        return "driver-guard-timeout"
    return "other"


def failure_rung(row: dict) -> str:
    """The rungs of the same mechanism, ordered by how loaded the machine was."""
    if row["verdict"] == "passed":
        return "passed"
    if row["verdict"] == "timeout" or row["returncode"] is None:
        return "rung4: pytest process itself did not return (driver guard fired)"
    count = (row.get("events") or {}).get("child_started_count")
    assertion = row.get("assertion") or ""
    if "TimeoutExpired" in assertion:
        if isinstance(count, int) and count <= 1:
            return "rung3: 15s timeout with <=1 child cycle completed"
        return "rung2: 15s timeout after repeated watchdog kills"
    if "child_started" in assertion or re.search(r"assert \d+ == 2", assertion):
        return "rung1: extra child_started (assert == 2)"
    return "other"


def mechanism_rows(rows: list[dict]) -> list[dict]:
    """Per failed node-1 run: does it satisfy the addendum-B artifact/watchdog rules?"""
    out = []
    for row in rows:
        if row["verdict"] == "passed":
            continue
        events = row.get("events") or {}
        attempts = events.get("attempts") or []
        killed = [a["unresponsive_uptime_seconds"] for a in attempts
                  if "unresponsive_uptime_seconds" in a]
        clean_exit = [a for a in attempts if a.get("exited_reason") == "clean_exit"]
        reasons = sorted({a.get("unresponsive_reason") for a in attempts
                          if a.get("unresponsive_reason")})
        out.append({
            "condition": row["condition"], "pass": row["pass"], "tree": row["tree"],
            "run": row["run"], "verdict": row["verdict"],
            "rung": failure_rung(row),
            "failure_class": classify_failure(row),
            "child_started_count": events.get("child_started_count"),
            "child_unresponsive_count": events.get("child_unresponsive_count"),
            "reasons": reasons,
            "kill_uptimes": killed,
            "clean_exit": bool(clean_exit),
            "clean_exit_uptimes": [a.get("exited_uptime_seconds") for a in clean_exit],
            "all_kills_gt_050": all(u > HANG_TIMEOUT for u in killed) if killed else False,
            "kills_le_070_fraction": (sum(1 for u in killed if u <= 0.7) / len(killed))
            if killed else None,
            "all_reasons_session_start_timeout": bool(reasons) and
            all(r == "session_start_timeout" for r in reasons),
            "a_ge2_unresponsive": (events.get("child_unresponsive_count") or 0) >= 2,
            "c_clean_final_exit": bool(clean_exit),
        })
    return out


def main() -> int:
    frozen = load(EVIDENCE / "frozen_band_raw_record.json")
    ma = {name: load(AFTER / f"child-lifetime-{name}.json")
          for name in ("popen-quiet", "popen-cpu8", "popen-cpu12",
                       "startproc-quiet", "startproc-cpu8")}
    bands = {name: load(AFTER / f"band-{name}.json")
             for name in ("child-quiet", "child-cpu8", "child-spawn",
                          "logon-quiet", "logon-cpu8")}
    wrapper = {name: load(AFTER / f"wrapper-latency-{name}.json")
               for name in ("quiet", "cpu8")}
    ambient: dict = {}
    log_path = AFTER / "campaign.log"
    if log_path.exists():
        raw = log_path.read_bytes()
        text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") \
            else raw.decode("utf-8", "replace")
        entries = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("{") and "spawn_python_pass_ms" in stripped:
                try:
                    entries.append(json.loads(stripped))
                except json.JSONDecodeError:
                    pass
        if entries:
            ambient = {"before": entries[0],
                       "after": entries[-1] if len(entries) > 1 else None,
                       "source": str(log_path)}

    result: dict = {"card": "I-14-E", "attempt": "a20260919-01",
                    "criteria_source": ("oracle.md sections 3/5 (frozen 2026-09-21T20:09:21Z) + "
                                        "oracle-addendum-A (run counts) + oracle-addendum-B "
                                        "(artifact discrimination, concurrent activity, "
                                        "determinism verdict)"),
                    "pilot_note": ("smoke/pilot artefacts (after/smoke-*.json, TEMP/i14e-pilot-probe) "
                                   "were design probes taken before the full campaign; they are "
                                   "reported separately and never used as expected values"),
                    "ambient": ambient}

    # ---------- frozen band (hand-computed; must reproduce the card's numbers) ----------
    if frozen:
        rows = frozen["rows"]
        tally = {}
        for row in rows:
            key = f"pass{row['pass']}/{row['tree']}"
            bucket = tally.setdefault(key, {"runs": 0, "failed": 0, "hist": {}})
            bucket["runs"] += 1
            bucket["failed"] += 1 if row["verdict_frozen_json"] == "failed" else 0
            hist = bucket["hist"]
            hist[str(row["child_started_count"])] = hist.get(str(row["child_started_count"]), 0) + 1
        result["frozen_band"] = {
            "source": frozen["source_frozen_json"],
            "source_sha256": frozen["source_frozen_json_sha256"],
            "completeness": {
                "rows": len(rows),
                "events_present": sum(1 for r in rows if r["events_present"]),
                "stdout_matches_frozen_capture": sum(1 for r in rows
                                                     if r["stdout_matches_frozen_capture"]),
            },
            "tally": tally,
            "totals_by_tree": {
                tree: {"runs": sum(1 for r in rows if r["tree"] == tree),
                       "failed": sum(1 for r in rows if r["tree"] == tree
                                     and r["verdict_frozen_json"] == "failed")}
                for tree in ("T0", "T4")},
            "flip": {
                "pass1_more_failing_tree": max(("T0", "T4"),
                                               key=lambda t: tally[f"pass1/{t}"]["failed"]),
                "pass2_more_failing_tree": max(("T0", "T4"),
                                               key=lambda t: tally[f"pass2/{t}"]["failed"]),
            },
            "failure_instances": {
                "second_attempt_kill_uptimes": frozen["second_attempt_uptime_seconds"],
                "passing_runs_final_attempt_exit_uptimes": frozen["noop_child_lifetime_seconds"],
            },
            "assertions": sorted({r["assertion_frozen_json"] for r in rows
                                  if r["assertion_frozen_json"]}),
        }

    # ---------- M-A: the measured window ----------
    result["m_a_window"] = {}
    for name, payload in ma.items():
        if payload is None:
            result["m_a_window"][name] = None
            continue
        result["m_a_window"][name] = {
            "condition": payload["condition"], "method": payload["method"],
            "load": payload["load"], "n": payload["stats"]["q2_immediate_exit_lifetime"].get("n"),
            "q1_time_to_first_side_effect": payload["stats"]["q1_time_to_first_side_effect"],
            "q2_immediate_exit_lifetime": payload["stats"]["q2_immediate_exit_lifetime"],
            "failures": payload["failures"],
        }

    # ---------- M-B: node outcome bands ----------
    result["m_b_bands"] = {}
    for name, payload in bands.items():
        if payload is None:
            result["m_b_bands"][name] = None
            continue
        rows = payload["results"]
        block = {
            "node": payload["node"], "condition": payload["condition"],
            "load": payload["load"], "passes": payload["passes"],
            "runs_per_tree_pass": payload["runs_per_tree_pass"],
            "overall": rate_block(rows),
            "by_pass": {k: rate_block(v) for k, v in sorted(by(rows, lambda r: r["pass"]).items())},
            "by_tree": {k: rate_block(v) for k, v in sorted(by(rows, lambda r: r["tree"]).items())},
            "by_pass_tree": {f"pass{k[0]}/{k[1]}": rate_block(v)
                             for k, v in sorted(by(rows, lambda r: (r["pass"], r["tree"])).items())},
            "wall_seconds": {
                "median": statistics.median([r["wall_seconds"] for r in rows]) if rows else None,
                "max": max((r["wall_seconds"] for r in rows), default=None),
            },
            "load_probe_medians": {
                key: (statistics.median(probe_series(rows, key))
                      if probe_series(rows, key) else None)
                for key in ("sleep20_overshoot_ms", "cpu_loop_300k_ms")},
            "failure_classes": {},
            "failure_rungs": {},
            "spawn_latency_by_pass": payload.get("spawn_latency_by_pass"),
            "child_started_histogram": {},
        }
        for row in rows:
            cls = classify_failure(row) if row["verdict"] != "passed" else "passed"
            block["failure_classes"][cls] = block["failure_classes"].get(cls, 0) + 1
            rung = failure_rung(row)
            block["failure_rungs"][rung] = block["failure_rungs"].get(rung, 0) + 1
            count = (row.get("events") or {}).get("child_started_count")
            key = str(count)
            block["child_started_histogram"][key] = \
                block["child_started_histogram"].get(key, 0) + 1
        if payload["node"] == "child_without_runtime":
            mech = mechanism_rows(rows)
            block["mechanism"] = mech
            block["mechanism_summary"] = {
                "failed_runs": len(mech),
                "failed_runs_with_at_least_one_watchdog_kill": sum(
                    1 for m in mech if m["child_unresponsive_count"]),
                "all_kills_gt_0.5s_in_runs_that_had_kills": all(
                    m["all_kills_gt_050"] for m in mech if m["kill_uptimes"]) if mech else None,
                "all_reasons_session_start_timeout": all(
                    m["all_reasons_session_start_timeout"] for m in mech
                    if m["child_unresponsive_count"]) if mech else None,
                "rung1_clean_final_exit_present": sum(1 for m in mech if m["c_clean_final_exit"]),
                "distinct_failure_classes": sorted({m["failure_class"] for m in mech}),
                "distinct_rungs": sorted({m["rung"] for m in mech}),
            }
        result["m_b_bands"][name] = block

    # ---------- load-dependence cross-tab (drift-robust, per-run probe) ----------
    all_child_rows: list[dict] = []
    for name in ("child-quiet", "child-cpu8", "child-spawn"):
        payload = bands.get(name)
        if payload:
            for row in payload["results"]:
                row = dict(row)
                row["band"] = name
                all_child_rows.append(row)
    if all_child_rows:
        series = [(r, (r.get("load_probe") or {}).get("cpu_loop_300k_ms"))
                  for r in all_child_rows]
        series = [(r, v) for r, v in series if isinstance(v, (int, float))]
        series.sort(key=lambda item: item[1])
        quartiles: dict = {}
        n = len(series)
        for index, (row, value) in enumerate(series):
            q = min(3, index * 4 // max(1, n))
            bucket = quartiles.setdefault(f"q{q + 1}", {"rows": [], "cpu_values": []})
            bucket["rows"].append(row)
            bucket["cpu_values"].append(value)
        result["load_crosstab_child_node"] = {
            "probe": "cpu_loop_300k_ms (per-run, higher = more loaded)",
            "quartiles": {
                key: {"runs": len(bucket["rows"]),
                      "cpu_loop_median_ms": round(statistics.median(bucket["cpu_values"]), 1),
                      "cpu_loop_range_ms": [round(min(bucket["cpu_values"]), 1),
                                            round(max(bucket["cpu_values"]), 1)],
                      **rate_block(bucket["rows"])}
                for key, bucket in sorted(quartiles.items())},
        }

    # ---------- M-C: node-2 budgets ----------
    result["m_c_wrapper_window"] = {}
    for name, payload in wrapper.items():
        if payload is None:
            result["m_c_wrapper_window"][name] = None
            continue
        result["m_c_wrapper_window"][name] = {
            "condition": payload["condition"], "load": payload["load"],
            "budgets": payload["budgets"], "stats": payload["stats"],
            "status_sequences": sorted({tuple(s.get("statuses") or [])
                                        for s in payload["samples"]}, key=str),
            "wrapper_timeouts": sum(1 for s in payload["samples"] if s.get("wrapper_timed_out")),
        }

    # ---------- concurrent activity (addendum B2) ----------
    activity_path = AFTER / "concurrent-activity.jsonl"
    if activity_path.exists():
        samples = []
        for line in activity_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    samples.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        pytest_campaigns: dict = {}
        other_python: dict = {}
        cpu_names: dict = {}
        for sample in samples:
            for proc in sample.get("other_python_or_pytest", []):
                cmd = (proc.get("cmd") or "")[:110]
                if "pytest" in cmd:
                    pytest_campaigns[cmd] = pytest_campaigns.get(cmd, 0) + 1
                if "python" in (proc.get("name") or "").lower():
                    other_python[cmd] = other_python.get(cmd, 0) + 1
            for delta in sample.get("cpu_deltas_top", [])[:3]:
                name = delta.get("name")
                cpu_names[name] = cpu_names.get(name, 0) + 1
        result["concurrent_activity"] = {
            "samples": len(samples),
            "window": [samples[0]["sampled_at"], samples[-1]["sampled_at"]] if samples else None,
            "other_session_pytest_campaigns": sorted(pytest_campaigns.items(),
                                                     key=lambda kv: -kv[1])[:6],
            "other_session_python_processes": sorted(other_python.items(),
                                                     key=lambda kv: -kv[1])[:6],
            "top_cpu_consumers": sorted(cpu_names.items(), key=lambda kv: -kv[1])[:8],
            "note": ("concurrent pytest campaigns and a persistent chrome-headless-shell load were "
                     "present during the arms; this is the load-side evidence addendum B2 asks "
                     "for, and it is why the 'quiet' arm is not an idle machine"),
        }

    # ---------- hypotheses ----------
    def cond(name: str) -> dict | None:
        return result["m_b_bands"].get(name)

    h: dict = {}
    cq, cc, cs = cond("child-quiet"), cond("child-cpu8"), cond("child-spawn")
    if cq and cc:
        quiet_rate = cq["overall"]["failure_rate"] or 0
        cpu_rate = cc["overall"]["failure_rate"] or 0
        if quiet_rate >= 0.90 and cpu_rate >= 0.90:
            h1_verdict = ("ceiling: both arms are saturated (>=90% failures), so this contrast "
                          "cannot separate the arms; load-dependence is carried by the measured "
                          "window (M-A) and by the frozen-band cross-era comparison instead")
        elif cpu_rate > quiet_rate:
            h1_verdict = "supported (failure rate rises with load)"
        else:
            h1_verdict = "not supported (rate did not rise)"
        h["H1"] = {
            "statement": "node-1 failure rate rises with load",
            "quiet": cq["overall"], "cpu8": cc["overall"],
            "spawn": (cs or {}).get("overall"),
            "verdict": h1_verdict,
            "load_dependence_evidence": {
                "within_this_attempt": {
                    "q2_immediate_exit_lifetime_quiet": (
                        result["m_a_window"].get("popen-quiet") or {}).get(
                        "q2_immediate_exit_lifetime"),
                    "q2_immediate_exit_lifetime_cpu8": (
                        result["m_a_window"].get("popen-cpu8") or {}).get(
                        "q2_immediate_exit_lifetime"),
                    "reading": ("the measured quantity the test's 0.5 s assumption bounds shifts "
                                "right when this attempt adds load (median 0.691 s -> 1.351 s, "
                                "launch-to-first-side-effect median 0.581 s -> 1.287 s)"),
                },
                "cross_era": {
                    "frozen_band_same_quantity_passing_runs": (result.get("frozen_band") or {}).get(
                        "failure_instances", {}).get(
                        "passing_runs_final_attempt_exit_uptimes"),
                    "this_attempt_outcome": "43/45 node-1 runs failed",
                    "reading": ("the same test file and byte-identical trees produced 6/24 failures "
                                "when the measured lifetime sat mostly below 0.5 s, and ~100% "
                                "failures when it sat above"),
                },
            },
            "caveat": ("the machine's ambient load was already high (see ambient + addendum A1), so "
                       "the 'quiet' arm means 'no load added by this attempt', not an idle machine; "
                       "within this attempt the failure rate is saturated in every arm, so the "
                       "load-dependence rests on the measured window and the cross-era contrast"),
        }
        trees = cq["by_tree"], cc["by_tree"]
        ident = {}
        for block in trees:
            if "T0" in block and "T0b" in block:
                ident = {"T0": block["T0"], "T0b": block["T0b"],
                         "difference": round((block["T0"]["failure_rate"] or 0)
                                             - (block["T0b"]["failure_rate"] or 0), 4)}
        h["H2"] = {
            "statement": "the jitter is not a tree difference",
            "by_tree_quiet": cq["by_tree"], "by_tree_cpu8": cc["by_tree"],
            "byte_identical_pair_quiet": ident,
            "verdict": ("supported (byte-identical T0/T0b behave the same; see also the structural "
                        "argument in binding.json)"),
        }
    if cc:
        mech = cc.get("mechanism_summary") or {}
        artifact_blocks = {}
        missing_events = 0
        for name in ("child-quiet", "child-cpu8", "child-spawn"):
            payload = load(AFTER / f"artifacts-{name}.json")
            if payload:
                artifact_blocks[name] = payload["summary"]["causation_classes"]
                if payload["summary"]["events_missing_runs"]:
                    missing_events += 1
        watchdog_runs = mech.get("failed_runs_with_at_least_one_watchdog_kill")
        failed_runs = mech.get("failed_runs") or 0
        if not missing_events and watchdog_runs == failed_runs and failed_runs:
            h3_verdict = ("supported by artifact discrimination: every failed run carries its own "
                          "launcher event file (no path/redirect absence) and every failed run "
                          "contains at least one session_start_timeout watchdog kill")
        elif not missing_events and watchdog_runs:
            h3_verdict = (f"dominant mechanism supported: {watchdog_runs}/{failed_runs} failed runs "
                          "show the session_start_timeout watchdog kill; the rest are launcher-level "
                          "startup-latency timeouts (no child cycle completed) - same resource, "
                          "different rung, and no run shows the artifact-absence path signature")
        else:
            h3_verdict = "not supported as stated / see rows"
        h["H3"] = {
            "statement": ("failures are the immediate-exit child crossing the 0.5 s watchdog "
                          "boundary, not another resource or a tree difference"),
            "artifact_discrimination": artifact_blocks,
            "node1_watchdog_kills_by_band": {
                name: {
                    "failed_runs": (result["m_b_bands"].get(name) or {}).get(
                        "mechanism_summary", {}).get("failed_runs"),
                    "with_watchdog_kill": (result["m_b_bands"].get(name) or {}).get(
                        "mechanism_summary", {}).get(
                        "failed_runs_with_at_least_one_watchdog_kill"),
                    "all_kills_gt_0.5s": (result["m_b_bands"].get(name) or {}).get(
                        "mechanism_summary", {}).get("all_kills_gt_0.5s_in_runs_that_had_kills"),
                }
                for name in ("child-quiet", "child-cpu8", "child-spawn")},
            "mechanism_summary": mech,
            "verdict": h3_verdict,
            "note": ("rung1 (assert N == 2) is the only rung where a clean final exit is expected; "
                     "rungs 2-4 end in the test's own 15 s subprocess timeout or in the driver's "
                     "guard, by construction, so 'clean final exit in every failure' is not the "
                     "right criterion for them"),
            "detail": (cc.get("mechanism") or [])[:40],
        }
    q2_quiet = (result["m_a_window"].get("popen-quiet") or {}).get(
        "q2_immediate_exit_lifetime", {})
    if q2_quiet:
        h["H4"] = {
            "statement": "an independently measured window explains the frozen 25% band",
            "quiet_q2": q2_quiet,
            "frozen_passing_runs_max": (result.get("frozen_band") or {}).get(
                "failure_instances", {}).get("passing_runs_final_attempt_exit_uptimes", {}).get("max"),
            "verdict": ("supported: the measured lifetime distribution straddles 0.5 s"
                        if (q2_quiet.get("count_ge_050") or 0) > 0 else
                        "not supported: measured lifetimes stay below the assumption"),
        }
    lq, lc = cond("logon-quiet"), cond("logon-cpu8")
    if lq and lc:
        h["H5"] = {
            "statement": "node 2's budgets (15 s wrapper / 15 s events / 20 s exit) with the "
                         "measured margins",
            "quiet": lq["overall"], "cpu8": lc["overall"],
            "wrapper_window": result["m_c_wrapper_window"],
            "verdict": ("no jitter band observed end-to-end under the measured conditions"
                        if (lq["overall"]["failed"] == 0 and lc["overall"]["failed"] == 0)
                        else "failures observed - see failure classes"),
            "discrepancy": ("the direct window probe did cross the 15 s events budget in 6/8 "
                            "loaded samples while the end-to-end node passed 16/16; both are "
                            "reported, neither is dropped"),
        }
    result["hypotheses"] = h

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    render_md(result)
    print(json.dumps({"frozen_band_totals": result.get("frozen_band", {}).get("totals_by_tree"),
                      "m_b": {k: (v or {}).get("overall") for k, v in result["m_b_bands"].items()},
                      "hypotheses": {k: v.get("verdict") for k, v in h.items()}},
                     indent=2, ensure_ascii=False))
    print("out:", OUT_JSON)
    return 0


def render_md(result: dict) -> None:
    """Human-readable companion for after/analysis.json (same numbers, no new computation)."""
    lines: list[str] = ["# I-14-E after/analysis.md (rendered from analysis.json)", ""]
    frozen = result.get("frozen_band") or {}
    if frozen:
        lines += ["## 1. Frozen observation band (hand-computed from the raw record)", "",
                  f"- source: `{frozen['source']}` (sha256 `{frozen['source_sha256'][:16]}...`)",
                  f"- completeness: {frozen['completeness']['rows']} rows / events files "
                  f"{frozen['completeness']['events_present']} / stdout byte-identical to the "
                  f"frozen captures {frozen['completeness']['stdout_matches_frozen_capture']}", "",
                  "| round/tree | runs | failed | child_started histogram |", "|---|---|---|---|"]
        for key, bucket in sorted(frozen["tally"].items()):
            hist = ", ".join(f"{k}x{v}" for k, v in sorted(bucket["hist"].items()))
            lines.append(f"| {key} | {bucket['runs']} | **{bucket['failed']}** | {hist} |")
        lines += ["", f"- per-tree totals: {json.dumps(frozen['totals_by_tree'], ensure_ascii=False)}",
                  f"- flip: pass1 more-failing tree `{frozen['flip']['pass1_more_failing_tree']}`, "
                  f"pass2 `{frozen['flip']['pass2_more_failing_tree']}`", ""]
    lines += ["## 2. Independent window measurement (M-A / M-C)", ""]
    for name, block in (result.get("m_a_window") or {}).items():
        if not block:
            continue
        q1 = block["q1_time_to_first_side_effect"]
        q2 = block["q2_immediate_exit_lifetime"]
        lines.append(f"- **{name}** ({block['method']}/{block['condition']}, n={block['n']}): "
                     f"Q1 median {q1.get('median')} s / max {q1.get('max')} s / >=0.5 s "
                     f"{q1.get('count_ge_050')}; Q2 median {q2.get('median')} s / max "
                     f"{q2.get('max')} s / >=0.5 s {q2.get('count_ge_050')}")
    for name, block in (result.get("m_c_wrapper_window") or {}).items():
        if not block:
            continue
        stats = block["stats"]
        lines.append(f"- **wrapper/{name}**: wrapper median {stats['wrapper_seconds'].get('median')} s"
                     f" (budget 15 s, over {stats['wrapper_seconds'].get('count_ge_budget')}); "
                     f"wait-for-child_started median {stats['events_seconds'].get('median')} s "
                     f"(budget 15 s, over {stats['events_seconds'].get('count_ge_budget')}); "
                     f"wait-for-exit median {stats['exit_seconds'].get('median')} s "
                     f"(budget 20 s, over {stats['exit_seconds'].get('count_ge_budget')}, "
                     f"upper-bound timing)")
    lines += ["", "## 3. Node-level outcome bands (M-B)", "",
              "| band | node | condition | runs | failed | rate | Wilson95 | rungs |",
              "|---|---|---|---|---|---|---|---|"]
    for name, block in (result.get("m_b_bands") or {}).items():
        if not block:
            continue
        overall = block["overall"]
        rungs = ", ".join(f"{k.split(':')[0]}x{v}" for k, v in sorted(block["failure_rungs"].items()))
        lines.append(f"| {name} | {block['node']} | {block['condition']} | {overall['runs']} | "
                     f"{overall['failed']} | {overall['failure_rate']} | {overall['wilson95']} | {rungs} |")
    lines += ["", "Per tree (byte-identical T0/T0b is the identity control):", ""]
    for name, block in (result.get("m_b_bands") or {}).items():
        if not block:
            continue
        lines.append(f"- **{name}**: " + ", ".join(
            f"{tree} {v['failed']}/{v['runs']}" for tree, v in sorted(block["by_tree"].items())))
    crosstab = result.get("load_crosstab_child_node")
    if crosstab:
        lines += ["", "## 4. Per-run load probe x outcome (drift-robust)", "",
                  "| quartile | runs | cpu_loop median (ms) | failed | rate |", "|---|---|---|---|---|"]
        for key, block in sorted(crosstab["quartiles"].items()):
            lines.append(f"| {key} | {block['runs']} | {block['cpu_loop_median_ms']} | "
                         f"{block['failed']} | {block['failure_rate']} |")
    activity = result.get("concurrent_activity")
    if activity:
        lines += ["", "## 5. Concurrent activity (addendum B2)", "",
                  f"- {activity['samples']} samples, window {activity['window']}",
                  "- other sessions' **pytest campaigns** (samples present):"]
        for cmd, count in activity["other_session_pytest_campaigns"][:5]:
            lines.append(f"  - x{count} `{cmd}`")
        lines.append("- top CPU-delta process names (times in the top 3): " +
                     ", ".join(f"{k}x{v}" for k, v in activity["top_cpu_consumers"][:5]))
    lines += ["", "## 6. Hypothesis verdicts (criteria frozen in oracle.md before the runs)", ""]
    for key, block in sorted((result.get("hypotheses") or {}).items()):
        lines.append(f"- **{key}**: {block.get('verdict')}")
    lines += ["", "## 7. Not achieved / not self-signed", "",
              "- The card's exit criterion (tests no longer randomly red/green under load) is "
              "**not achieved**: it needs a test-side change, and this attempt's boundary is "
              "production-read-only (proposal in `after/proposed-test-side-change.md`).",
              "- The 'quiet' arm means 'this attempt added no load', not an idle machine: other "
              "sessions' pytest campaigns and a persistent chrome-headless-shell load were "
              "present (see section 5 and oracle-addendum-A/B).",
              "- Node 2 passed 16/16 end-to-end, while the direct window probe missed the 15 s "
              "events budget in 6/8 loaded samples; both are reported side by side, not merged.",
              ""]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
