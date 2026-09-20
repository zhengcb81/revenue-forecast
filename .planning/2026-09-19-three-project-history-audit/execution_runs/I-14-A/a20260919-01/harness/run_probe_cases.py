"""I-14-A: run one probe case and independently verify it against the frozen spec.

The producer (subprocess) and the checker (this module) are separate: the checker
never imports the probe under test, so a bug in the probe cannot make its own
verdict look right.  Raw exit codes are written beside the report.

Usage:
  python run_probe_cases.py --tool <probe.py> --out <dir> --case <case-id>
  python run_probe_cases.py --tool <probe.py> --out <dir> --all
  python run_probe_cases.py --tool <probe.py> --out <dir> --binding-mismatch
  python run_probe_cases.py --tool <probe.py> --out <dir> --binding-ok
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_spec():
    spec = importlib.util.spec_from_file_location("fixture_spec", HERE / "fixture_spec.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SPEC = load_spec()


def _percentiles(values: list[float]) -> dict:
    import statistics
    ordered = sorted(values)
    return {
        "p50": statistics.median(ordered),
        "p95": ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))],
        "p99": ordered[min(len(ordered) - 1, int(len(ordered) * 0.99))],
    }


def verify_case(case_id: str, report: dict, rc: int) -> dict:
    exp = SPEC.CASES[case_id]["expect_business"]
    got = report.get("slo_probe", {})
    calls = report.get("calls", {})
    checks: dict[str, dict] = {}

    def check(name: str, ok: bool, detail) -> None:
        checks[name] = {"ok": bool(ok), "detail": detail}

    check("expected_raw_returncode", rc == SPEC.CASES[case_id]["expect_rc"],
          {"raw": rc, "expected": SPEC.CASES[case_id]["expect_rc"]})

    if "calls_failed" in exp:
        check("calls_failed", calls.get("failed") == exp["calls_failed"],
              {"raw": calls.get("failed"), "expected": exp["calls_failed"]})
    if "failed_kind_subprocess_rc" in exp:
        kinds = calls.get("failed_kinds", {})
        check("failed_kind_subprocess_rc",
              kinds.get("subprocess_rc") == exp["failed_kind_subprocess_rc"],
              {"raw": kinds, "expected_subprocess_rc": exp["failed_kind_subprocess_rc"]})
    if "failed_kind_business_status" in exp:
        kinds = calls.get("failed_kinds", {})
        check("failed_kind_business_status",
              kinds.get("business_status") == exp["failed_kind_business_status"],
              {"raw": kinds, "expected_business_status": exp["failed_kind_business_status"]})
    if "raw_returncode_all" in exp:
        rcs = {c["raw_returncode"] for c in report.get("per_call", [])}
        check("raw_returncode_all", rcs == {exp["raw_returncode_all"]},
              {"raw": sorted(rcs), "expected": exp["raw_returncode_all"]})
    if "exact_succeeded_count" in exp:
        check("exact_succeeded_count",
              got.get("exact", {}).get("succeeded_count") == exp["exact_succeeded_count"],
              {"raw": got.get("exact", {}).get("succeeded_count"),
               "expected": exp["exact_succeeded_count"]})
    if "latest_succeeded_count" in exp:
        check("latest_succeeded_count",
              got.get("latest", {}).get("succeeded_count") == exp["latest_succeeded_count"],
              {"raw": got.get("latest", {}).get("succeeded_count"),
               "expected": exp["latest_succeeded_count"]})
    if exp.get("peak_rss_is_null"):
        check("peak_rss_is_null", got.get("peak_rss_gb") is None,
              {"raw": got.get("peak_rss_gb"), "must_not_be": 0.0})
        check("peak_rss_not_zero", got.get("peak_rss_gb") != 0.0,
              {"raw": got.get("peak_rss_gb")})
    if exp.get("peak_rss_is_null_ok"):
        check("peak_rss_null_or_positive",
              got.get("peak_rss_gb") is None or got.get("peak_rss_gb") > 0,
              {"raw": got.get("peak_rss_gb")})
    if "peak_rss_gt" in exp:
        check("peak_rss_gt", (got.get("peak_rss_gb") or 0) > exp["peak_rss_gt"],
              {"raw": got.get("peak_rss_gb"), "expected_gt": exp["peak_rss_gt"]})
    if "peak_rss_source" in exp:
        check("peak_rss_source", got.get("peak_rss_source") == exp["peak_rss_source"],
              {"raw": got.get("peak_rss_source"), "expected": exp["peak_rss_source"]})
    if "peak_rss_source_prefix" in exp:
        src = str(got.get("peak_rss_source"))
        check("peak_rss_source_prefix", src.startswith(exp["peak_rss_source_prefix"]),
              {"raw": src, "expected_prefix": exp["peak_rss_source_prefix"]})
    if "rss_sample_count_min_gte" in exp:
        check("rss_sample_count_min_gte",
              (got.get("rss_sample_count_min") or 0) >= exp["rss_sample_count_min_gte"],
              {"raw": got.get("rss_sample_count_min"),
               "expected_gte": exp["rss_sample_count_min_gte"]})
    if exp.get("rss_pids_match_child_pids"):
        child_pids = {c["child_pid"] for c in report.get("per_call", [])}
        sampled = set(got.get("rss_sampled_pids") or [])
        check("rss_pids_include_child_pids", child_pids <= sampled,
              {"sampled": sorted(sampled), "child_pids": sorted(child_pids)})
    if exp.get("fixture_pid_is_in_samples"):
        # Windows fact: Popen.pid is the launcher (a shim or, for a real interpreter,
        # the interpreter itself), and the fixture script runs in a *descendant*.
        # The sampler walks the process tree, so the fixture's own os.getpid() must
        # appear among the sampled pids — that is the identity proof that the
        # measured process is the script and not the launcher shim.
        reported: set[int] = set()
        for c in report.get("per_call", []):
            try:
                envelope = json.loads((c["stdout_head"] or "").splitlines()[0])
            except (ValueError, IndexError):
                continue
            if isinstance(envelope, dict) and isinstance(envelope.get("pid"), int):
                reported.add(envelope["pid"])
        sampled = set(got.get("rss_sampled_pids") or [])
        check("fixture_pid_is_in_samples", bool(reported) and reported <= sampled,
              {"fixture_reported_pids": sorted(reported), "sampled": sorted(sampled)})
    if "bundle_measured" in exp:
        check("bundle_measured",
              got.get("bundle", {}).get("measured") is exp["bundle_measured"],
              {"raw": got.get("bundle", {}).get("measured"),
               "expected": exp["bundle_measured"]})
    if "bundle_basis" in exp:
        check("bundle_basis", got.get("bundle", {}).get("basis") == exp["bundle_basis"],
              {"raw": got.get("bundle", {}).get("basis"), "expected": exp["bundle_basis"]})
    if "breach_contains" in exp:
        joined = " | ".join(report.get("breaches", []))
        check("breach_contains", exp["breach_contains"] in joined, {"breaches": joined})

    # Cross-cutting: the three windows must be reported separately.
    windows = report.get("windows", {})
    for key in ("command_total_seconds", "slo_window_seconds",
                "rss_sample_window_seconds_max", "quick_check_seconds"):
        check(f"window_present:{key}", key in windows, {"value": windows.get(key)})
    check("quick_check_outside_slo_window",
          windows.get("quick_check_included_in_slo_window") is False,
          {"value": windows.get("quick_check_included_in_slo_window")})
    check("rss_window_not_before_slo_window",
          (windows.get("rss_sample_window_seconds_max") or 0.0)
          <= (windows.get("slo_window_seconds") or 0.0) + 1e-6,
          {"rss": windows.get("rss_sample_window_seconds_max"),
           "slo": windows.get("slo_window_seconds")})
    check("frozen_budgets_untouched", report.get("budgets") == SPEC.BUDGETS_FROZEN,
          {"raw": report.get("budgets"), "frozen": SPEC.BUDGETS_FROZEN})

    return {
        "case": case_id,
        "checks": checks,
        "all_ok": all(c["ok"] for c in checks.values()),
        "failed_checks": [k for k, v in checks.items() if not v["ok"]],
    }


def run_case(tool: Path, out_dir: Path, case_id: str,
             baseline_report: dict | None = None) -> dict:
    info = SPEC.ensure_fixture_root()
    case = SPEC.CASES[case_id]
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    extra = list(case.get("extra_argv", []))
    if extra and extra[0] == "--bundle-measurement":
        raise RuntimeError("bundle-copy control belongs to run_bundle_control.py")
    invocation = _invoke(tool, out_dir, case, info, extra)
    verdict = verify_case(case_id, invocation["report"], invocation["raw_returncode"])
    invocation["verdict"] = verdict
    invocation["expected_purpose"] = case["purpose"]
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
    return invocation


def _invoke(tool: Path, out_dir: Path, case: dict, info: dict, extra: list[str]) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    argv = [
        info["python"], "-X", "utf8", "-B", str(tool),
        "--catalog", info["fixture_catalog"],
        "--config", info["fixture_config"],
        "--samples", "3",
        "--report", str(report_path),
        "--resolve-cmd", json.dumps(SPEC.fixture_template(case["fixture"])),
        "--resolve-cwd", str(out_dir),
        *extra,
    ]
    t0 = time.perf_counter()
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=SPEC.PROBE_CASES_TIMEOUT_SECONDS)
    elapsed = time.perf_counter() - t0
    (out_dir / "stdout.json").write_text(proc.stdout or "", encoding="utf-8")
    (out_dir / "stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    (out_dir / "raw_returncode.txt").write_text(str(proc.returncode), encoding="utf-8")
    report = {}
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "argv": argv,
        "raw_returncode": proc.returncode,
        "wall_seconds": round(elapsed, 3),
        "report": report,
    }


def binding_case(tool: Path, out_dir: Path, mode: str) -> dict:
    """E4/E4b: catalog/config consistency refusal, proven without any resolve call."""
    info = SPEC.ensure_fixture_root()
    out_dir.mkdir(parents=True, exist_ok=True)
    config = info["mismatch_config"] if mode == "mismatch" else info["plain_config"]
    report_path = out_dir / "report.json"
    argv = [
        info["python"], "-X", "utf8", "-B", str(tool),
        "--catalog", info["fixture_catalog"],
        "--config", config,
        "--samples", "3",
        "--report", str(report_path),
        "--resolve-cmd", json.dumps(SPEC.fixture_template("F4")),
        "--resolve-cwd", str(out_dir),
    ]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=SPEC.PROBE_CASES_TIMEOUT_SECONDS)
    (out_dir / "stdout.json").write_text(proc.stdout or "", encoding="utf-8")
    (out_dir / "stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    (out_dir / "raw_returncode.txt").write_text(str(proc.returncode), encoding="utf-8")
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    if mode == "mismatch":
        checks = {
            "raw_returncode": {"ok": proc.returncode == 3,
                               "detail": {"raw": proc.returncode, "expected": 3}},
            "error_kind": {"ok": report.get("error") == "catalog_config_mismatch",
                           "detail": report.get("error")},
            "measured_false": {"ok": report.get("measured") is False,
                               "detail": report.get("measured")},
            "no_resolve_call_spawned": {"ok": not report.get("per_call"),
                                        "detail": len(report.get("per_call") or [])},
            "both_paths_echoed": {
                "ok": bool(report.get("binding", {}).get("configured_catalog_dir")),
                "detail": report.get("binding")},
        }
    else:
        checks = {
            "raw_returncode": {"ok": proc.returncode == 2,
                               "detail": {"raw": proc.returncode,
                                          "expected": 2,
                                          "note": "green on budgets is impossible here: "
                                                  "bundle unmeasured and RSS uncollected"}},
            "binding_consistent": {"ok": report.get("binding", {}).get("consistent") is True,
                                   "detail": report.get("binding")},
            "resolve_calls_ran": {"ok": len(report.get("per_call") or []) == 6,
                                  "detail": len(report.get("per_call") or [])},
        }
    verdict = {"case": f"binding-{mode}", "checks": checks,
               "all_ok": all(c["ok"] for c in checks.values()),
               "failed_checks": [k for k, v in checks.items() if not v["ok"]]}
    (out_dir / "verdict.json").write_text(json.dumps(verdict, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    return {"argv": argv, "raw_returncode": proc.returncode, "report": report,
            "verdict": verdict}


def percentile_case(tool: Path, out_dir: Path) -> dict:
    """E6: the frozen budgets and the percentile rule, computed independently."""
    import importlib.util as ilu
    spec = ilu.spec_from_file_location("probe_under_test", tool)
    module = ilu.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    checks = {"budgets_frozen": {"ok": module.BUDGETS == SPEC.BUDGETS_FROZEN,
                                 "detail": module.BUDGETS}}
    for values, expected in SPEC.PERCENTILE_CASES:
        got = module._percentiles(values)
        ok = all(abs(got[k] - expected[k]) < 1e-12 for k in expected)
        checks[f"percentiles_{values[:3]}"] = {"ok": ok, "detail": {"got": got,
                                                                    "expected": expected}}
    # A hand-rolled independent recomputation of the p95 index rule.
    argv = [SPEC.PYTHON, "-X", "utf8", "-B", "-c",
            "import statistics,sys,json;"
            "v=[0.4,0.1,0.9,0.2];o=sorted(v);"
            "print(json.dumps({'p50':statistics.median(o),"
            "'p95':o[min(len(o)-1,int(len(o)*0.95))],"
            "'p99':o[min(len(o)-1,int(len(o)*0.99))]}))"]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    independent = json.loads(proc.stdout)
    checks["independent_recompute"] = {
        "ok": abs(independent["p50"] - 0.30000000000000004) < 1e-12
        and independent["p95"] == 0.9 and independent["p99"] == 0.9,
        "detail": independent}
    verdict = {"case": "E6-frozen-constants", "checks": checks,
               "all_ok": all(c["ok"] for c in checks.values()),
               "failed_checks": [k for k, v in checks.items() if not v["ok"]]}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "verdict.json").write_text(json.dumps(verdict, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser(description="I-14-A probe case runner")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--case")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--binding-mismatch", action="store_true")
    parser.add_argument("--binding-ok", action="store_true")
    parser.add_argument("--percentiles", action="store_true")
    args = parser.parse_args()
    tool = Path(args.tool)
    out_root = Path(args.out)

    summary: dict = {"tool": str(tool), "cases": {}}
    baseline_report = None
    baseline_path = out_root / "E0-baseline-F4" / "report.json"
    if baseline_path.is_file():
        baseline_report = json.loads(baseline_path.read_text(encoding="utf-8"))
    if args.case:
        result = run_case(tool, out_root / args.case, args.case, baseline_report)
        summary["cases"][args.case] = {
            "raw_returncode": result["raw_returncode"],
            "all_ok": result["verdict"]["all_ok"],
            "failed_checks": result["verdict"]["failed_checks"],
        }
    if args.all:
        order = ["E0-baseline-F4",
                 *[c for c in SPEC.CASES
                   if c != "E0-baseline-F4"
                   and not SPEC.CASES[c].get("excluded_from_all")]]
        for case_id in order:
            result = run_case(tool, out_root / case_id, case_id, baseline_report)
            summary["cases"][case_id] = {
                "raw_returncode": result["raw_returncode"],
                "all_ok": result["verdict"]["all_ok"],
                "failed_checks": result["verdict"]["failed_checks"],
            }
    if args.binding_mismatch:
        result = binding_case(tool, out_root / "E4-binding-mismatch", "mismatch")
        summary["cases"]["E4-binding-mismatch"] = {
            "raw_returncode": result["raw_returncode"],
            "all_ok": result["verdict"]["all_ok"],
            "failed_checks": result["verdict"]["failed_checks"]}
    if args.binding_ok:
        result = binding_case(tool, out_root / "E4b-binding-consistent", "consistent")
        summary["cases"]["E4b-binding-consistent"] = {
            "raw_returncode": result["raw_returncode"],
            "all_ok": result["verdict"]["all_ok"],
            "failed_checks": result["verdict"]["failed_checks"]}
    if args.percentiles:
        verdict = percentile_case(tool, out_root / "E6-frozen-constants")
        summary["cases"]["E6-frozen-constants"] = {
            "raw_returncode": 0, "all_ok": verdict["all_ok"],
            "failed_checks": verdict["failed_checks"]}

    summary["all_ok"] = all(c["all_ok"] for c in summary["cases"].values())
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
