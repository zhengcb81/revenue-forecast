"""Enumerate the WHOLE revenue-model registry from the isolated snapshot.

Purpose: every count that appears in evidence/<card>/oq_rulings.json must come from
this script and its raw output file, not from prose.  The script reads the isolated
copy of the product (read-only) and reports:

  * model / required / optional / ratio-driver totals
  * every ratio driver whose EFFECTIVE bound is not [0,1], with the mechanism
  * every revenue_per_activity / revenue_per_unit driver, its default bound and its exceptions
  * every optional driver that is NOT listed in the model's declared defaults
    (those are the ones the calculator silently fills with 0.0)
  * a per-card focus block for the card under test

Usage:
  python -X utf8 -B enumerate_registry.py --code-root <iso/checkout_scripts> \
      --card M17 --out <evidence/M17/registry_enumeration.json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def bound_pair(lower, upper):
    return ["-inf" if lower == -math.inf else lower, "inf" if upper == math.inf else upper]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--card", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    sys.path.insert(0, args.code_root)
    import model_registry  # noqa: E402  (isolated snapshot only)

    registry = model_registry.MODEL_REGISTRY
    signed = sorted(getattr(model_registry, "_SIGNED_DRIVERS", frozenset()))

    per_model = []
    ratio_drivers_total = 0
    ratio_not_ratio_bound = []
    per_activity_drivers_total = 0
    per_activity_exceptions = []
    silently_zero_filled = []
    explicit_bound_sets = []
    required_total = 0
    optional_total = 0

    for model_id in sorted(registry):
        spec = registry[model_id]
        required_total += len(spec.required)
        optional_total += len(spec.optional)
        if spec.driver_bounds:
            explicit_bound_sets.append(model_id)
        drivers = {}
        for driver in list(spec.required) + list(spec.optional):
            dimension = spec.dimensions[driver]
            lower, upper = model_registry.driver_value_bounds(model_id, driver)
            declared = spec.driver_bounds.get(driver)
            entry = {
                "dimension": dimension,
                "declared_bounds": (bound_pair(*declared) if declared is not None else None),
                "effective_bounds": bound_pair(lower, upper),
                "in_declared_defaults": driver in spec.defaults,
                "declared_default": (float(spec.defaults[driver]) if driver in spec.defaults else None),
            }
            drivers[driver] = entry
            if dimension == "ratio":
                ratio_drivers_total += 1
                if not (lower == 0.0 and upper == 1.0):
                    ratio_not_ratio_bound.append({
                        "driver": "%s.%s" % (model_id, driver),
                        "effective_bounds": bound_pair(lower, upper),
                        "declared_bounds": entry["declared_bounds"],
                        "signed_driver": driver in signed,
                        "mechanism": ("explicit declared bounds" if declared is not None
                                      else ("signed-driver allowlist" if driver in signed
                                            else "other")),
                    })
            if dimension in ("revenue_per_activity", "revenue_per_unit"):
                per_activity_drivers_total += 1
                if not (lower == 0.0 and upper == math.inf):
                    per_activity_exceptions.append({
                        "driver": "%s.%s" % (model_id, driver),
                        "dimension": dimension,
                        "effective_bounds": bound_pair(lower, upper),
                        "declared_bounds": entry["declared_bounds"],
                    })
            if driver in spec.optional and driver not in spec.defaults:
                silently_zero_filled.append({
                    "driver": "%s.%s" % (model_id, driver),
                    "dimension": dimension,
                    "effective_bounds": bound_pair(lower, upper),
                    "mechanism": ("drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years)) "
                                  "in calculate_registered_model -> an omitted value becomes 0.0, and "
                                  "'no such item' becomes indistinguishable from 'item not found'"),
                })
        per_model.append({
            "model_id": model_id,
            "required": list(spec.required),
            "optional": list(spec.optional),
            "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
            "ratio_drivers": sorted(spec.ratio_drivers),
            "formula": spec.formula,
            "drivers": drivers,
        })

    focus_model = None
    by_id = {m["model_id"]: m for m in per_model}
    card_model = None
    for candidate in ("licensing_commercial", "advertising", "gaming", "cohort_subscription"):
        if candidate in by_id:
            if args.card == "M17" and candidate == "licensing_commercial":
                card_model = candidate
            elif args.card == "M18" and candidate == "advertising":
                card_model = candidate
            elif args.card == "M19" and candidate == "gaming":
                card_model = candidate
            elif args.card == "M20" and candidate == "cohort_subscription":
                card_model = candidate
    if card_model:
        focus_model = {"model_id": card_model, **{k: v for k, v in by_id[card_model].items()
                                                 if k != "model_id"}}

    doc = {
        "card_id": args.card,
        "enumerated_by": "scripts/enumerate_registry.py",
        "enumeration_rule": ("counts below are produced by this script from the isolated snapshot; "
                             "no count is copied from prose"),
        "code_root": os.path.abspath(args.code_root),
        "registry_module_file": model_registry.__file__,
        "source_hashes": {
            "iso/checkout_scripts/model_registry.py": sha256(
                os.path.join(args.code_root, "model_registry.py")),
            "iso/checkout_scripts/model_extensions.py": sha256(
                os.path.join(args.code_root, "model_extensions.py")),
        },
        "totals": {
            "models": len(per_model),
            "required_drivers": required_total,
            "optional_drivers": optional_total,
            "ratio_drivers": ratio_drivers_total,
            "revenue_per_activity_and_per_unit_drivers": per_activity_drivers_total,
            "optional_drivers_absent_from_declared_defaults": len(silently_zero_filled),
        },
        "signed_drivers": signed,
        "models_with_explicit_driver_bounds": explicit_bound_sets,
        "ratio_drivers_whose_effective_bound_is_not_0_1": ratio_not_ratio_bound,
        "revenue_per_activity_and_per_unit_default_bound": [0.0, "inf"],
        "revenue_per_activity_and_per_unit_exceptions": per_activity_exceptions,
        "optional_drivers_silently_defaulted_to_zero": silently_zero_filled,
        "card_focus": focus_model,
        "per_model": per_model,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)

    print("card", args.card, "registry models", len(per_model))
    print("ratio_drivers", ratio_drivers_total,
          "ratio_drivers_not_in_0_1", len(ratio_not_ratio_bound))
    print("revenue_per_activity_and_per_unit_drivers", per_activity_drivers_total,
          "exceptions", len(per_activity_exceptions))
    print("optional_drivers_silently_defaulted_to_zero", len(silently_zero_filled))
    print("models_with_explicit_driver_bounds", explicit_bound_sets)
    if focus_model:
        print("card_focus model", focus_model["model_id"])
        print("card_focus required", focus_model["required"])
        print("card_focus optional", focus_model["optional"])
        print("card_focus defaults", focus_model["defaults"])
        for driver, entry in focus_model["drivers"].items():
            print("  driver", driver, entry["dimension"], "effective", entry["effective_bounds"],
                  "in_defaults", entry["in_declared_defaults"])
    print("written", os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
