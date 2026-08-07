"""Repeatable, self-validating revenue-forecast engine E2E harness.

Runs the engine end-to-end on a frozen input fixture, strong-validates the
output, checks the calculation at every step, verifies deterministic
double-run reproducibility, creates the backtest snapshot, and compares
everything against a golden expected result keyed on the input's canonical
semantic sha256 (the engine's own input_sha256).

Usage:
    python e2e/run_revenue_forecast_e2e.py [--input PATH] [--update-golden] [--keep-runs]

Exit codes:
    0 = all green
    1 = a step assertion failed (regression or environment)
    2 = input/contract error (missing file, invalid input, missing golden key)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_INPUT = HERE / "fixtures" / "biren_input.json"
EXPECTED_DIR = HERE / "expected"
RUNS_DIR = HERE / ".runs"
REVENUE_FORECAST_HEAD = None


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _report(msg: str) -> None:
    print(f"[e2e] {msg}", flush=True)


class StepCollector:
    def __init__(self) -> None:
        self.failures: list[str] = []

    def check(self, step: str, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(f"STEP {step}: {message}")
            _report(f"  FAIL {step}: {message}")
        else:
            _report(f"  ok   {step}")


def run_engine(input_path: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)  # the engine CLI does not create parents
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "revenue_forecast.py"),
         str(input_path), "--output", str(out_dir / "forecast.json"),
         "--markdown", str(out_dir / "forecast.md")],
        cwd=str(REPO), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=600,
    )
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--update-golden", action="store_true")
    parser.add_argument("--keep-runs", action="store_true")
    args = parser.parse_args()

    input_path = args.input.resolve()
    if not input_path.is_file():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 2
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "3.6":
        print("ERROR: input is not schema 3.6", file=sys.stderr)
        return 2
    semantic_sha = canonical_sha256(data)
    golden_path = EXPECTED_DIR / f"expected-{semantic_sha[:12]}.json"

    # ---- STEP 1: input contract ----
    c = StepCollector()
    required = ("company_name", "as_of_date", "currency", "unit", "fiscal_year_end",
                "base_year", "forecast_years", "segments", "sources", "parameters",
                "evidence_claims", "historical_revenue", "research_coverage",
                "management_communication_coverage", "growth_driver_tree")
    c.check("1a", all(k in data for k in required), f"input missing top-level fields: {sorted(set(required)-set(data))}")
    c.check("1b", all(s["scenarios"].get("base") and s["scenarios"]["base"].get("model")
                      for s in data["segments"]), "segment scenarios incomplete")
    if c.failures:
        print("ERROR: " + "; ".join(c.failures), file=sys.stderr)
        return 2

    # ---- run engine twice (determinism) + backtest snapshot ----
    run_root = RUNS_DIR / semantic_sha[:12]
    run_root.mkdir(parents=True, exist_ok=True)
    existing = [int(p.name.split("-")[1]) for p in run_root.iterdir()
                if p.is_dir() and p.name.startswith("run-")]
    seq = max(existing, default=0)
    results: list[dict] = []
    for attempt in (1, 2):
        out_dir = run_root / f"run-{seq + attempt}"
        rc = run_engine(input_path, out_dir)
        if rc != 0:
            print(f"ERROR: STEP 2/9 FAILED: engine exited {rc} (run {attempt})", file=sys.stderr)
            return 1
        r = json.loads((out_dir / "forecast.json").read_text(encoding="utf-8"))
        results.append(r)
        _report(f"  run {attempt} ok: result={r['result_sha256'][:16]}")

    _report("STEP 9: deterministic double-run")
    if results[0]["result_sha256"] != results[1]["result_sha256"]:
        print("ERROR: STEP 9 FAILED: two identical inputs produced different outputs", file=sys.stderr)
        return 1
    _report("  ok   STEP 9: result_sha256 identical across two runs")

    r = results[0]
    out_dir = run_root / f"run-{seq + 1}"

    # ---- STEP 3: output is a strong-validated formal artifact ----
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        from revenue_report import validate_published_forecast  # noqa: E402
        validate_published_forecast(r, data)
        _report("  ok   STEP 3: output strong-validated (publication receipt recomputed)")
    except Exception as exc:
        print(f"ERROR: STEP 3 FAILED: strong validation rejected output: {exc}", file=sys.stderr)
        return 1

    # ---- STEPS 4-8 + golden ----
    cf = r["consolidated_forecast"]
    seg = r["segments"][0]
    actual = {
        "input_canonical_sha256": semantic_sha,
        "result_sha256": r["result_sha256"],
        "input_sha256": r["input_sha256"],
        "formal_output_mode": r.get("publication_receipt", {}).get("formal_output_mode"),
        "workflow_receipt": bool(r.get("workflow_compliance_receipt")),
        "terminals": {s: cf[s]["terminal_revenue"] for s in ("low", "base", "high")},
        "cagr": {s: cf[s]["cagr"] for s in ("low", "base", "high")},
        "segment_effective_terminal": {
            s: seg["scenarios"][s]["effective_revenue"]["2030"] for s in ("low", "base", "high")},
        "evidence_claim_count": len(r.get("evidence_claims", [])),
        "sensitivity_count": len(r.get("sensitivities", [])),
    }
    try:
        actual["repo_head"] = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
    except Exception:
        actual["repo_head"] = None

    c = StepCollector()
    c.check("4a", r["input_sha256"] == semantic_sha,
            f"output input_sha256 {r['input_sha256']} != canonical input {semantic_sha}")
    c.check("4b", r.get("publication_receipt", {}).get("formal_output_mode") == "formal",
            "formal_output_mode != formal")
    c.check("4c", bool(r.get("workflow_compliance_receipt")), "workflow receipt missing")
    # result_sha256 = canonical_sha256(result) computed BEFORE the field is
    # attached, so recompute on the output minus the self field.
    r_no_self = {k: v for k, v in r.items() if k != "result_sha256"}
    c.check("4d", canonical_sha256(r_no_self) == r.get("result_sha256"),
            "canonical recomputation (minus self field) must equal result_sha256")
    c.check("4e", len(r.get("evidence_claims", [])) > 0, "no evidence claims in output")
    c.check("4f", len(r.get("sensitivities", [])) > 0, "no sensitivities in output")

    if not golden_path.is_file() and not args.update_golden:
        print(f"ERROR: no golden for input {semantic_sha[:12]} "
              f"(input changed? run --update-golden after reviewing)", file=sys.stderr)
        return 2

    if args.update_golden:
        EXPECTED_DIR.mkdir(parents=True, exist_ok=True)
        golden_path.write_text(json.dumps(actual, ensure_ascii=False, indent=2), encoding="utf-8")
        _report(f"golden updated: {golden_path.name}")
    else:
        golden = json.loads(golden_path.read_text(encoding="utf-8"))
        diffs = []
        for key in ("result_sha256", "input_sha256", "formal_output_mode", "workflow_receipt",
                    "evidence_claim_count", "sensitivity_count"):
            if actual.get(key) != golden.get(key):
                diffs.append(f"{key}: expected {golden.get(key)} got {actual.get(key)}")
        for key in ("terminals", "cagr", "segment_effective_terminal"):
            for scen in ("low", "base", "high"):
                a = (actual.get(key) or {}).get(scen)
                g = (golden.get(key) or {}).get(scen)
                if not (isinstance(a, (int, float)) and isinstance(g, (int, float))
                        and math.isclose(a, g, rel_tol=1e-9, abs_tol=1e-6)):
                    diffs.append(f"{key}[{scen}]: expected {g} got {a}")
        if diffs:
            print("ERROR: STEP 10 FAILED — golden mismatch:", file=sys.stderr)
            for d in diffs:
                print(f"  {d}", file=sys.stderr)
            return 1
        _report("  ok   STEP 10: golden comparison identical")

    # ---- STEP 8: backtest snapshot create ----
    snap_dir = run_root / f"run-{seq + 2}"
    snap_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "revenue_backtest.py"), "create",
         str(input_path), "--version", "e2e-" + semantic_sha[:8],
         "--output", str(snap_dir / "snapshot.json")],
        cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600,
    )
    if proc.returncode != 0:
        print(f"ERROR: STEP 8 FAILED: backtest create exited {proc.returncode}: {proc.stderr[-800:]}",
              file=sys.stderr)
        return 1
    snap = json.loads((snap_dir / "snapshot.json").read_text(encoding="utf-8"))
    c.check("8a", snap.get("input_sha256") == snap.get("forecast_result", {}).get("input_sha256"),
            "snapshot input binding broken")
    c.check("8b", bool(snap.get("snapshot_id")), "snapshot_id missing")

    if c.failures:
        print("ERROR: " + "; ".join(c.failures), file=sys.stderr)
        return 1
    _report(f"E2E PASS: input={semantic_sha[:12]} result={r['result_sha256'][:12]} repo_head={(actual.get('repo_head') or '?')[:8]}")
    if not args.keep_runs:
        runs = sorted(run_root.glob("run-*"))
        for old in runs[:-3]:
            try:
                for f in old.iterdir():
                    f.unlink()
                old.rmdir()
            except OSError:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
