"""Registry driver-domain enumeration for the M21-M24 batch (read-only).

This is the raw evidence behind evidence/<card>/oq_rulings.json. It reads the
ISOLATED snapshot of the product registry (--code-root) and prints, for every
registered model, the effective driver domain returned by the product's own
driver_value_bounds(model_id, driver), plus the exceptions.

It classifies nothing by hand: the counts below are produced by the loops.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/enumerate_oq_rulings.py \
      --code-root <attempt>/iso/checkout_scripts --card M21 --out <json>
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--card", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    sys.path.insert(0, args.code_root)
    import model_registry as mr  # noqa: E402  (isolated snapshot)

    report = {
        "card_id": args.card,
        "code_root": args.code_root,
        "model_registry_file": mr.__file__,
        "question": "does a ratio-dimension driver outside [0,1] (and an optional driver "
                    "with no explicit default) represent a contract gap?",
        "registered_model_count": len(mr.MODEL_REGISTRY),
        "total_driver_slots": 0,
        "by_dimension": {},
        "ratio_drivers_total": 0,
        "ratio_drivers_effective_domain_0_1": 0,
        "ratio_drivers_outside_0_1": [],
        "non_ratio_drivers_total": 0,
        "non_ratio_drivers_with_finite_upper_bound": [],
        "optional_drivers_without_explicit_default": [],
        "silent_zero_fill_mechanism": "scripts/model_registry.py:335 "
                                      "drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))",
        "per_model": {},
    }

    for model_id, spec in sorted(mr.MODEL_REGISTRY.items()):
        row = {"required": list(spec.required), "optional": list(spec.optional),
               "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
               "explicit_driver_bounds": {k: [None if b[0] is None else float(b[0]),
                                              None if b[1] is None else float(b[1])]
                                          for k, b in dict(spec.driver_bounds).items()},
               "drivers": {}}
        for driver in list(spec.required) + list(spec.optional):
            lower, upper = mr.driver_value_bounds(model_id, driver)
            dimension = spec.dimensions[driver]
            report["total_driver_slots"] += 1
            report["by_dimension"][dimension] = report["by_dimension"].get(dimension, 0) + 1
            domain = [None if math.isinf(lower) and lower < 0 else lower,
                      None if math.isinf(upper) and upper > 0 else upper]
            entry = {"dimension": dimension,
                     "in_required": driver in spec.required,
                     "in_optional": driver in spec.optional,
                     "has_explicit_default": driver in spec.defaults,
                     "explicit_bounds": driver in spec.driver_bounds,
                     "effective_domain": domain,
                     "signed_driver_exception": driver in mr._SIGNED_DRIVERS}
            row["drivers"][driver] = entry
            if dimension == "ratio":
                report["ratio_drivers_total"] += 1
                if domain == [0.0, 1.0]:
                    report["ratio_drivers_effective_domain_0_1"] += 1
                else:
                    report["ratio_drivers_outside_0_1"].append(
                        {"model_id": model_id, "driver": driver, "effective_domain": domain,
                         "explicit_bounds": entry["explicit_bounds"],
                         "signed_driver_exception": entry["signed_driver_exception"]})
            else:
                report["non_ratio_drivers_total"] += 1
                if domain[1] is not None:
                    report["non_ratio_drivers_with_finite_upper_bound"].append(
                        {"model_id": model_id, "driver": driver, "effective_domain": domain})
            if driver in spec.optional and driver not in spec.defaults:
                report["optional_drivers_without_explicit_default"].append(
                    {"model_id": model_id, "driver": driver, "dimension": dimension,
                     "effective_domain": domain})
        report["per_model"][model_id] = row

    report["card_model_ids"] = {}
    for model_id in ("delivery_pipeline", "milestone_royalty", "insurance_service",
                     "subscription_arr_bridge"):
        spec = mr.MODEL_REGISTRY[model_id]
        report["card_model_ids"][model_id] = {
            "required": list(spec.required),
            "optional": list(spec.optional),
            "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
            "effective_domains": {d: [None if math.isinf(mr.driver_value_bounds(model_id, d)[0])
                                      and mr.driver_value_bounds(model_id, d)[0] < 0
                                      else mr.driver_value_bounds(model_id, d)[0],
                                      None if math.isinf(mr.driver_value_bounds(model_id, d)[1])
                                      and mr.driver_value_bounds(model_id, d)[1] > 0
                                      else mr.driver_value_bounds(model_id, d)[1]]
                                      for d in list(spec.required) + list(spec.optional)},
            "silent_zero_fill_applies_to": [d for d in spec.optional if d not in spec.defaults],
        }

    report["counts"] = {
        "registered_model_count": report["registered_model_count"],
        "total_driver_slots": report["total_driver_slots"],
        "ratio_drivers_total": report["ratio_drivers_total"],
        "ratio_drivers_effective_domain_0_1": report["ratio_drivers_effective_domain_0_1"],
        "ratio_drivers_outside_0_1": len(report["ratio_drivers_outside_0_1"]),
        "non_ratio_drivers_total": report["non_ratio_drivers_total"],
        "non_ratio_drivers_with_finite_upper_bound":
            len(report["non_ratio_drivers_with_finite_upper_bound"]),
        "optional_drivers_without_explicit_default":
            len(report["optional_drivers_without_explicit_default"]),
    }

    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
    print("registered_model_count", report["registered_model_count"])
    print("total_driver_slots", report["total_driver_slots"])
    print("by_dimension", json.dumps(report["by_dimension"], sort_keys=True))
    print("ratio_drivers_total", report["ratio_drivers_total"])
    print("ratio_drivers_effective_domain_0_1", report["ratio_drivers_effective_domain_0_1"])
    print("ratio_drivers_outside_0_1", json.dumps(report["ratio_drivers_outside_0_1"],
                                                  ensure_ascii=False, sort_keys=True))
    print("non_ratio_drivers_total", report["non_ratio_drivers_total"])
    print("non_ratio_drivers_with_finite_upper_bound",
          json.dumps(report["non_ratio_drivers_with_finite_upper_bound"], ensure_ascii=False))
    print("optional_drivers_without_explicit_default",
          json.dumps(report["optional_drivers_without_explicit_default"],
                     ensure_ascii=False, sort_keys=True))
    print("card_model_ids", json.dumps(report["card_model_ids"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
