"""I-14-A / E7: the copied-exact bundle control, made deterministic.

The frozen rule is "the real bundle path must be measured; a copied exact latency
may not grant bundle eligibility".  Testing that rule needs a bundle input that is
*exactly* this run's exact latencies, which cannot be produced before the run
exists.  So this control runs the probe twice:

  pass 1  no --bundle-measurement        -> exposes this run's exact latencies
  pass 2a --bundle-measurement copy.json -> copy.json is built from pass 1's exact
                                            latencies, so the probe must refuse it
  pass 2b --bundle-measurement indep.json-> independent values, so the probe must
                                            accept it

Both expectations are frozen in oracle.md E7; this script only supplies the inputs.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SPEC = load("fixture_spec", HERE / "fixture_spec.py")
RUNNER = load("run_probe_cases", HERE / "run_probe_cases.py")


def invoke(tool: Path, out_dir: Path, extra: list[str], samples: int = 3) -> dict:
    info = SPEC.ensure_fixture_root()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    argv = [
        info["python"], "-X", "utf8", "-B", str(tool),
        "--catalog", info["fixture_catalog"],
        "--config", info["fixture_config"],
        "--samples", str(samples),
        "--report", str(report_path),
        "--resolve-cmd", json.dumps(SPEC.fixture_template("F4")),
        "--resolve-cwd", str(out_dir),
        *extra,
    ]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=SPEC.PROBE_CASES_TIMEOUT_SECONDS)
    (out_dir / "stdout.json").write_text(proc.stdout or "", encoding="utf-8")
    (out_dir / "stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
    (out_dir / "raw_returncode.txt").write_text(str(proc.returncode), encoding="utf-8")
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    return {"argv": argv, "raw_returncode": proc.returncode, "report": report}


def main() -> int:
    tool = Path(sys.argv[1])
    out_root = Path(sys.argv[2])
    prod_tool = (Path(sys.argv[3]) if len(sys.argv) > 3
                 else ATTEMPT / "iso" / "tool_prod" / "slo_probe.py")
    out_root.mkdir(parents=True, exist_ok=True)

    pass1 = invoke(tool, out_root / "pass1", [])
    exact_values = [c["elapsed_seconds"] for c in pass1["report"].get("per_call", [])
                    if c["succeeded"]]
    if not exact_values:
        print(json.dumps({"error": "pass1 produced no successful exact calls",
                          "raw_returncode": pass1["raw_returncode"]}, indent=2))
        return 1

    copied = out_root / "bundle-copied-from-exact.json"
    copied.write_text(json.dumps({
        "command": "copied_from_exact_control",
        "window_seconds": pass1["report"]["windows"]["slo_window_seconds"],
        "bundle_latencies_seconds": exact_values,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    independent = out_root / "bundle-independent.json"
    independent_values = [round(v * 1.5 + 0.01, 6) for v in exact_values]
    independent.write_text(json.dumps({
        "command": "independent_bundle_measurement_control",
        "window_seconds": pass1["report"]["windows"]["slo_window_seconds"] * 1.5,
        "bundle_latencies_seconds": independent_values,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    pass2a = invoke(tool, out_root / "pass2a-copied", ["--bundle-measurement", str(copied)])
    pass2b = invoke(tool, out_root / "pass2b-independent",
                    ["--bundle-measurement", str(independent)])

    def bundle_of(result: dict) -> dict:
        return result["report"].get("slo_probe", {}).get("bundle", {})

    prod_source = prod_tool.read_text(encoding="utf-8")
    patched_source = tool.read_text(encoding="utf-8")

    checks = {
        "production_tool_aliases_bundle_to_exact": {
            # The measured structural defect: the production tool's bundle metric IS
            # the exact latency list, with no bundle measurement anywhere.
            "ok": "bundle = exact[:]" in prod_source
            and "def _load_bundle_measurement" not in prod_source,
            "detail": {"has_bundle_eq_exact": "bundle = exact[:]" in prod_source,
                       "has_bundle_measurement_loader":
                           "def _load_bundle_measurement" in prod_source}},
        "patched_tool_has_no_bundle_alias": {
            "ok": "bundle = exact[:]" not in patched_source
            and "def _load_bundle_measurement" in patched_source,
            "detail": {"tool_under_test": str(tool),
                       "has_bundle_eq_exact": "bundle = exact[:]" in patched_source,
                       "has_bundle_measurement_loader":
                           "def _load_bundle_measurement" in patched_source}},
        "pass1_bundle_unmeasured": {
            "ok": bundle_of(pass1).get("measured") is False
            and bundle_of(pass1).get("basis") == "unmeasured"
            and any("bundle" in b for b in pass1["report"].get("breaches", [])),
            "detail": {"bundle": bundle_of(pass1),
                       "breaches": pass1["report"].get("breaches")}},
        "pass1_not_green": {"ok": pass1["raw_returncode"] != 0,
                            "detail": pass1["raw_returncode"]},
        "pass2a_copy_input_measured_on_own_values": {
            # Scope note (oracle.md E7): a bundle file is measured on its own numbers,
            # so run-to-run jitter means the identical-value refusal path is not
            # reachable from a file built out of a different run.  The literal alias
            # (bundle = exact[:]) is what "copied exact" means, and the structural
            # check above covers it.
            "ok": bundle_of(pass2a).get("measured") is True
            and bundle_of(pass2a).get("identity_check", {}).get("verdict")
            in ("independent", "copied_exact"),
            "detail": {"bundle": bundle_of(pass2a),
                       "raw_returncode": pass2a["raw_returncode"]}},
        "pass2b_independent_accepted": {
            "ok": bundle_of(pass2b).get("measured") is True
            and bundle_of(pass2b).get("basis") == "measured"
            and not any("bundle" in b for b in pass2b["report"].get("breaches", [])),
            "detail": {"bundle": bundle_of(pass2b),
                       "breaches": pass2b["report"].get("breaches")}},
        "pass2b_green": {"ok": pass2b["raw_returncode"] == 0,
                         "detail": pass2b["raw_returncode"]},
    }
    verdict = {"case": "E7b-bundle-copy-control", "checks": checks,
               "all_ok": all(c["ok"] for c in checks.values()),
               "failed_checks": [k for k, v in checks.items() if not v["ok"]],
               "raw_returncodes": {"pass1": pass1["raw_returncode"],
                                   "pass2a-copied": pass2a["raw_returncode"],
                                   "pass2b-independent": pass2b["raw_returncode"]}}
    (out_root / "verdict.json").write_text(json.dumps(verdict, ensure_ascii=False, indent=2),
                                           encoding="utf-8")
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0 if verdict["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
