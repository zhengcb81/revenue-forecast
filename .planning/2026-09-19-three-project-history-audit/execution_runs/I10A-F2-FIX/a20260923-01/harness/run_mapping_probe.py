#!/usr/bin/env python
"""I-10-A harness: historical_mapping_probe runner (card action 4).

Calls the REAL production forecast entry — iso/rf/scripts/forecast/segments.py
calculate_model_path(model, base_revenue, driver_ids, parameter_index, years,
scenario) — with FY2025 disclosed historical parameters held IDENTICAL on
low/base/high, to verify the field->parameter->model->output wiring. Every result
is labelled `historical_mapping_probe` and is NEVER a three-scenario forecast or
accuracy evidence (STOP_QUALIFICATION_SCOPE).

Variants implement the frozen red/mutation arms (oracle §3):
  normal            positive: outputs must equal the frozen hand-computed values
  red_conv          mis-wired conversion (quantity x10) -> must NOT validate (rc 2)
  mut_swap          swap quantity/price parameter values -> dimension mismatch,
                    product must raise -> correctly refused (rc 2)
  mut_omit_optional drop explicit other_revenue -> registry must raise (省缺即抛,
                    post-I-10-B contract) -> correctly refused (rc 2)
An unrefused variant is rc 3 (应红未红) and a recorded mutation gap.

rc legend (this batch, frozen): 0=pass 1=harness failure 2=correctly-rejected
negative / no verdict 3=not as expected.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ATT / "iso" / "rf" / "scripts"))

import cases_data  # noqa: E402

SCENARIOS = ("low", "base", "high")
TOL = 1e-9


def close(a: float, b: float) -> bool:
    return abs(a - b) <= TOL * max(1.0, abs(b))


def build_params(case: dict, inst: dict, variant: str):
    """Build (parameter_index, driver_ids) for one instance under one variant."""
    model = case["model_id"]
    spec = cases_data.driver_spec(model)
    qty_used = inst["qty_raw"] * inst["qty_factor"]
    price = inst["price"]
    if variant == "red_conv":
        qty_used = qty_used * 10.0  # deliberately wrong conversion (mis-wired field->unit)
    if variant == "mut_swap":
        qty_used, price = price, qty_used  # dimension mismatch injection

    pid_prefix = f"P-{case['company_id'][:2]}-{inst['instance'].upper()}"
    parameter_index: dict = {}
    driver_ids: dict = {}

    def add(driver: str, value: float, unit: str, pid: str):
        dim = spec["required"].get(driver) or spec["optional"].get(driver)
        parameter_index[pid] = {
            "value": float(value),
            "unit": unit,
            "dimension": dim,
            "period": "FY2025" if case["period"] == "FY2025" else "FY2026",
            "scenario": "all",
        }
        driver_ids[driver] = [pid]

    if model == "resource":
        add("saleable_volume", qty_used, inst["qty_unit"], f"{pid_prefix}-QTY")
        add("realized_price", price, inst["price_unit"], f"{pid_prefix}-PRICE")
        if variant != "mut_omit_optional":
            add("other_revenue", inst["other_revenue"], "元", f"{pid_prefix}-OTHER")
    elif model == "unit_sales":
        add("units", qty_used, inst["qty_unit"], f"{pid_prefix}-QTY")
        add("unit_revenue", price, inst["price_unit"], f"{pid_prefix}-PRICE")
        add("timing_factor", inst.get("timing_factor", 1.0), "ratio", f"{pid_prefix}-T")
        if variant != "mut_omit_optional":
            add("other_revenue", inst["other_revenue"], "元", f"{pid_prefix}-OTHER")
    else:
        raise SystemExit(f"probe not designed for model {model}")
    if variant == "mut_swap_ids":
        # swap the parameter-ID REFERENCES across the quantity/price drivers so the
        # product's own dimension check must fire (frozen oracle §3 expectation)
        names = list(driver_ids)
        if len(names) >= 2:
            driver_ids[names[0]], driver_ids[names[1]] = driver_ids[names[1]], driver_ids[names[0]]
    return parameter_index, driver_ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--variant", default="normal")
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect-file", required=True)
    args = ap.parse_args()
    started = time.strftime("%Y-%m-%dT%H:%M:%S")

    case = cases_data.CASES[args.case]
    expected_doc = json.loads(Path(args.expect_file).read_text(encoding="utf-8"))
    expected = expected_doc["cases"][args.case]

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    import forecast.segments as seg  # the REAL product entry (iso copy)
    import model_registry

    counts = {"calculate_registered_model_calls": 0, "calculate_model_path_calls": 0}
    call_log: list = []
    orig_calc = seg.calculate_registered_model

    def counting_calc(*a, **kw):
        counts["calculate_registered_model_calls"] += 1
        call_log.append({"fn": "calculate_registered_model", "seq": counts["calculate_registered_model_calls"]})
        return orig_calc(*a, **kw)

    seg.calculate_registered_model = counting_calc  # count-on-entry spy (wired at import namespace)

    instances_out = []
    product_errors = []
    mismatch = []
    refusals = []
    for inst in case["instances"]:
        parameter_index, driver_ids = build_params(case, inst, args.variant)
        per_scenario = {}
        for scen in SCENARIOS:
            try:
                result = seg.calculate_model_path(
                    case["model_id"], case["base_revenue"], driver_ids, parameter_index,
                    case["years"], scen,
                )
                counts["calculate_model_path_calls"] += 1
                value = float(result["annual_revenue"][str(case["years"][0])])
                per_scenario[scen] = {"ok": True, "annual_revenue": value, "driver_values": result["driver_values"]}
            except Exception as exc:  # product refusal (negative arm) — recorded verbatim
                per_scenario[scen] = {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}
                product_errors.append({"instance": inst["instance"], "scenario": scen,
                                       "error_type": type(exc).__name__, "error": str(exc)})
                refusals.append(f"{inst['instance']}/{scen}:{type(exc).__name__}")
        exp = next((e for e in expected["instances"] if e["instance"] == inst["instance"]), None)
        exp_val = exp["expected_revenue"] if exp else None
        vals = [per_scenario[s]["annual_revenue"] for s in SCENARIOS if per_scenario[s]["ok"]]
        identical = len(vals) == 3 and all(close(vals[0], v) for v in vals)
        matches_expected = exp_val is not None and len(vals) == 3 and all(close(v, exp_val) for v in vals)
        if not matches_expected and exp_val is not None:
            mismatch.append({"instance": inst["instance"], "expected": exp_val,
                             "measured": vals, "variant": args.variant})
        instances_out.append({
            "instance": inst["instance"],
            "cn": inst["cn"],
            "parameter_index": parameter_index,
            "driver_parameter_ids": driver_ids,
            "per_scenario": {s: {k: v for k, v in per_scenario[s].items() if k != "driver_values"} for s in SCENARIOS},
            "driver_values_sample": per_scenario["base"].get("driver_values"),
            "low_base_high_identical": identical,
            "frozen_expected_revenue": exp_val,
            "matches_frozen_expected": matches_expected,
        })

    counts_ok = (
        counts["calculate_registered_model_calls"] == expected["expected_probe_counts"]["calculate_registered_model_calls"]
    )
    label_ok = args.variant == "normal"  # label applies to the recorded artifact, asserted by validator R5

    # business verdict per variant
    if args.variant == "normal":
        business_pass = (not mismatch) and counts_ok and all(i["low_base_high_identical"] for i in instances_out)
        verdict = "pass" if business_pass else "not_as_expected"
        rc = 0 if business_pass else 3
    else:
        # negative arm: must be refused (product error) or must mismatch
        detected = bool(refusals) or bool(mismatch)
        verdict = "correctly_rejected" if detected else "NOT_REFUSED_MUTANT_SURVIVED"
        rc = 2 if detected else 3

    payload = {
        "artifact": "historical_mapping_probe_result",
        "historical_mapping_probe": True,
        "label": "historical_mapping_probe",
        "NOT_a_three_scenario_forecast": True,
        "accuracy_evidence": False,
        "case_id": args.case,
        "variant": args.variant,
        "started_at_local": started,
        "finished_at_local": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "product_entry": "iso/rf/scripts/forecast/segments.py calculate_model_path",
        "model_id": case["model_id"],
        "period": case["period"],
        "scenarios_run": list(SCENARIOS),
        "scenario_values_identical_by_design": "historical_mapping_probe: disclosed historical parameters at identical values on low/base/high (card action 4); mapping verification ONLY",
        "counts_measured": counts,
        "counts_expected": expected["expected_probe_counts"],
        "counts_ok": counts_ok,
        "call_log": call_log,
        "instances": instances_out,
        "product_errors": product_errors,
        "refusals": refusals,
        "mismatches": mismatch,
        "business_verdict": verdict,
        "expected_business_result": expected_doc["negative_arm_expectations"].get(args.variant, "positive: outputs equal frozen hand values and low/base/high identical"),
        "raw_rc": rc,
    }
    (out_dir / "probe_result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps({"case": args.case, "variant": args.variant, "verdict": verdict, "rc": rc,
                      "counts": counts}, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())
