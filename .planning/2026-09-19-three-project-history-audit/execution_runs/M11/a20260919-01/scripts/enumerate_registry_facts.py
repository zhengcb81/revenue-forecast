"""Read-only registry enumeration used as the SOURCE OF COUNT for oq_rulings.json.

This script performs a CONTRACT READ of the registry metadata of the isolated product
copy: it reads ``MODEL_REGISTRY`` / ``ModelSpec`` attributes and calls
``driver_value_bounds``. It NEVER calls ``calculate_registered_model`` and it never
produces an expected revenue value. Counts in evidence/<CARD>/oq_rulings.json come from
this script's output, not from prose.

Run (from an attempt root):
  python -X utf8 -B scripts/enumerate_registry_facts.py --card M09 \
      --code-root <attempt>/iso/checkout_scripts --out <attempt>/evidence/M09/registry_enumeration.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

BATCH_CARDS = {
    "M09": "resource",
    "M10": "reserve_depletion",
    "M11": "infrastructure",
    "M12": "bank_revenue",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(BATCH_CARDS))
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    sys.path.insert(0, args.code_root)
    import model_registry  # noqa: E402  (contract read only)

    registry = model_registry.MODEL_REGISTRY

    def driver_facts(model_id, driver, spec):
        dimension = spec.dimensions[driver]
        if driver in spec.driver_bounds:
            lower, upper = spec.driver_bounds[driver]
            lower = float("-inf") if lower is None else float(lower)
            upper = float("inf") if upper is None else float(upper)
            bound_source = "explicit driver_bounds"
        else:
            lower, upper = model_registry.driver_value_bounds(model_id, driver)
            bound_source = ("implicit: growth_rate rule" if driver == "growth_rate"
                            else "implicit: signed driver list" if driver in model_registry._SIGNED_DRIVERS
                            else "implicit: dimension default")
        return {
            "driver": driver,
            "dimension": dimension,
            "role": "required" if driver in spec.required else "optional",
            "declared_default": (float(spec.defaults[driver]) if driver in spec.defaults else None),
            "declared_default_present": driver in spec.defaults,
            "ratio_driver": driver in spec.ratio_drivers,
            "effective_lower_bound": ("-inf" if lower == float("-inf") else float(lower)),
            "effective_upper_bound": ("inf" if upper == float("inf") else float(upper)),
            "bound_source": bound_source,
        }

    target = BATCH_CARDS[args.card]
    spec = registry[target]

    per_card = {}
    for card, model_id in sorted(BATCH_CARDS.items()):
        s = registry[model_id]
        drivers = [driver_facts(model_id, d, s) for d in list(s.required) + list(s.optional)]
        per_card[card] = {
            "model_id": model_id,
            "formula": s.formula,
            "required": list(s.required),
            "optional": list(s.optional),
            "declared_defaults": {k: float(v) for k, v in dict(s.defaults).items()},
            "ratio_drivers": sorted(s.ratio_drivers),
            "explicit_driver_bounds": {
                k: [None if b[0] is None else float(b[0]), None if b[1] is None else float(b[1])]
                for k, b in dict(s.driver_bounds).items()},
            "drivers": drivers,
            "optional_drivers_without_declared_default": [
                d for d in s.optional if d not in s.defaults],
        }

    # ---- registry-wide facts (batch scope + full registry scope) ----
    all_models = sorted(registry)
    ratio_non_default = []
    per_unit_like_default_bounds = set()
    per_unit_like_drivers = []
    per_unit_like_negative_capable = []
    reserve_volume_drivers = []
    silent_zero_fill = []
    for model_id in all_models:
        s = registry[model_id]
        for d in list(s.required) + list(s.optional):
            if d in s.ratio_drivers or s.dimensions[d] == "ratio":
                lower, upper = model_registry.driver_value_bounds(model_id, d)
                if not (lower == 0.0 and upper == 1.0):
                    ratio_non_default.append({"driver": "%s.%s" % (model_id, d),
                                              "bounds": [lower, upper],
                                              "bound_source": ("explicit driver_bounds"
                                                               if d in s.driver_bounds
                                                               else "implicit")})
            if s.dimensions[d] in ("revenue_per_unit", "revenue_per_activity"):
                lower, upper = model_registry.driver_value_bounds(model_id, d)
                per_unit_like_default_bounds.add((lower, upper))
                per_unit_like_drivers.append("%s.%s" % (model_id, d))
                if lower < 0:
                    per_unit_like_negative_capable.append("%s.%s" % (model_id, d))
            if s.dimensions[d] == "reserve_volume":
                lower, upper = model_registry.driver_value_bounds(model_id, d)
                reserve_volume_drivers.append({"driver": "%s.%s" % (model_id, d),
                                               "bounds": [lower, upper],
                                               "bound_source": ("explicit driver_bounds"
                                                                if d in s.driver_bounds
                                                                else "implicit")})
            if d in s.optional and d not in s.defaults:
                silent_zero_fill.append("%s.%s" % (model_id, d))

    batch_silent = {card: per_card[card]["optional_drivers_without_declared_default"]
                    for card in sorted(BATCH_CARDS)}
    batch_silent_total = sum(len(v) for v in batch_silent.values())
    batch_optional_total = sum(len(per_card[c]["optional"]) for c in BATCH_CARDS)

    doc = {
        "card_id": args.card,
        "target_model_id": target,
        "code_root": args.code_root,
        "model_registry_file": model_registry.__file__,
        "read_kind": "contract read only (MODEL_REGISTRY metadata + driver_value_bounds); "
                     "calculate_registered_model was NOT called by this script",
        "per_card": per_card,
        "batch_scope": ["M09", "M10", "M11", "M12"],
        "facts": {
            "batch_optional_driver_count": batch_optional_total,
            "batch_optional_drivers_without_declared_default": batch_silent,
            "batch_optional_drivers_without_declared_default_total": batch_silent_total,
            "registry_model_count": len(all_models),
            "registry_optional_drivers_without_declared_default_total": len(silent_zero_fill),
            "registry_optional_drivers_without_declared_default_sample": sorted(silent_zero_fill)[:40],
            "ratio_drivers_whose_effective_bounds_are_not_0_1": ratio_non_default,
            "ratio_drivers_whose_effective_bounds_are_not_0_1_count": len(ratio_non_default),
            "revenue_per_unit_and_revenue_per_activity_default_bounds_observed": sorted(
                [list(b) for b in per_unit_like_default_bounds]),
            "revenue_per_unit_and_revenue_per_activity_driver_count": len(per_unit_like_drivers),
            "revenue_per_unit_and_revenue_per_activity_drivers": sorted(per_unit_like_drivers),
            "revenue_per_unit_and_revenue_per_activity_drivers_that_admit_negative_values": sorted(
                per_unit_like_negative_capable),
            "revenue_per_unit_and_revenue_per_activity_drivers_that_admit_negative_values_count":
                len(per_unit_like_negative_capable),
            "reserve_volume_drivers": sorted(reserve_volume_drivers, key=lambda r: r["driver"]),
            "reserve_volume_drivers_non_negative_count":
                len([r for r in reserve_volume_drivers if r["bounds"][0] == 0.0]),
            "reserve_volume_drivers_signed_count":
                len([r for r in reserve_volume_drivers if r["bounds"][0] == float("-inf")]),
        },
    }
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
        handle.write("\n")

    with open(model_registry.__file__, "rb") as handle:
        registry_sha = hashlib.sha256(handle.read()).hexdigest()

    print("card", args.card, "target model", target)
    print("registry file", model_registry.__file__)
    print("registry file sha256", registry_sha)
    print("registry model count", len(all_models))
    for card in sorted(BATCH_CARDS):
        pc = per_card[card]
        print("%s %s required=%s optional=%s declared_defaults=%s"
              % (card, pc["model_id"], pc["required"], pc["optional"], pc["declared_defaults"]))
        print("%s optional_drivers_without_declared_default=%s"
              % (card, pc["optional_drivers_without_declared_default"]))
        for d in pc["drivers"]:
            print("   %s dimension=%s role=%s default=%s bounds=[%s, %s] source=%s"
                  % (d["driver"], d["dimension"], d["role"], d["declared_default"],
                     d["effective_lower_bound"], d["effective_upper_bound"], d["bound_source"]))
    print("batch optional driver count", batch_optional_total)
    print("batch optional drivers without a declared default", batch_silent)
    print("batch optional drivers without a declared default total", batch_silent_total)
    print("registry optional drivers without a declared default total", len(silent_zero_fill))
    print("ratio drivers whose effective bounds are not [0,1] count", len(ratio_non_default))
    for row in ratio_non_default:
        print("   ratio_non_default", row["driver"], row["bounds"], row["bound_source"])
    print("revenue_per_unit / revenue_per_activity observed default bounds",
          sorted([list(b) for b in per_unit_like_default_bounds]))
    print("revenue_per_unit / revenue_per_activity driver count", len(per_unit_like_drivers))
    print("revenue_per_unit / revenue_per_activity negative-capable drivers",
          sorted(per_unit_like_negative_capable))
    print("reserve_volume drivers", len(reserve_volume_drivers),
          "non_negative", len([r for r in reserve_volume_drivers if r["bounds"][0] == 0.0]),
          "signed", len([r for r in reserve_volume_drivers if r["bounds"][0] == float("-inf")]))
    for row in sorted(reserve_volume_drivers, key=lambda r: r["driver"]):
        print("   reserve_volume", row["driver"], row["bounds"], row["bound_source"])
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
