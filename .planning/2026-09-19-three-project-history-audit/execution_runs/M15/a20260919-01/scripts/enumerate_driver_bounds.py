"""Enumerate the live driver-bounds contract of the isolated product copy (raw evidence).

This is NOT part of the formula oracle and does NOT produce any expected value. It is a
read-only metadata enumeration whose raw output backs the counts quoted in
``evidence/<CARD>/oq_rulings.json``; the rulings file is built from THIS file by
``scripts/build_oq_rulings.py`` so that no count in the narrative is hand-typed.

Declared product calls (read-only metadata, no calculation):
  MODEL_REGISTRY, ModelSpec.driver_bounds / defaults / dimensions / ratio_drivers,
  model_registry.driver_value_bounds(model_id, driver), model_registry._SIGNED_DRIVERS

Writes ``evidence/<CARD>/oq_enumeration.json``. Standard library + the isolated product copy.
Prints ASCII only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def jsonable(value):
    """JSON has no infinity literal; write non-finite floats as the strings inf/-inf/nan.

    A strict JSON parser (jq, PowerShell ConvertFrom-Json, a reviewer's own reader) rejects
    Python's non-standard ``Infinity`` token, so this file must not contain one.
    """
    if isinstance(value, float):
        if value == float("inf"):
            return "inf"
        if value == float("-inf"):
            return "-inf"
        if value != value:
            return "nan"
        return value
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--code-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", card)
    os.makedirs(evidence, exist_ok=True)

    sys.path.insert(0, args.code_root)
    import model_registry  # noqa: E402

    oracle = json.load(open(os.path.join(evidence, "oracle.json"), "r", encoding="utf-8"))
    model_id = oracle["model_id"]
    spec = model_registry.MODEL_REGISTRY[model_id]
    signed = sorted(getattr(model_registry, "_SIGNED_DRIVERS", frozenset()))

    registry_totals = {"models": len(model_registry.MODEL_REGISTRY), "drivers": 0,
                       "ratio_drivers": 0}
    ratio_not_in_0_1 = []
    for other_id, other in sorted(model_registry.MODEL_REGISTRY.items()):
        drivers = list(other.required) + list(other.optional)
        registry_totals["drivers"] += len(drivers)
        for driver in drivers:
            if driver not in other.ratio_drivers:
                continue
            registry_totals["ratio_drivers"] += 1
            lower, upper = model_registry.driver_value_bounds(other_id, driver)
            if not (lower == 0.0 and upper == 1.0):
                ratio_not_in_0_1.append({"driver": "%s.%s" % (other_id, driver),
                                         "bounds": [lower, upper],
                                         "explicit_bound_tuple": list(other.driver_bounds[driver])
                                         if driver in other.driver_bounds else None})

    drivers = list(spec.required) + list(spec.optional)
    effective_bounds = {}
    for driver in drivers:
        lower, upper = model_registry.driver_value_bounds(model_id, driver)
        effective_bounds[driver] = [lower, upper]

    optional_without_default = [d for d in spec.optional if d not in spec.defaults]
    optional_with_explicit_default = {d: float(spec.defaults[d]) for d in spec.optional
                                      if d in spec.defaults}
    signed_drivers_of_this_model = [d for d in drivers if d in signed]
    unbounded_drivers = [d for d in drivers
                         if effective_bounds[d][0] == float("-inf")
                         and effective_bounds[d][1] == float("inf")]
    zero_lower_bound_drivers = [d for d in drivers if effective_bounds[d][0] == 0.0]
    inclusive_upper_one_drivers = [d for d in drivers if effective_bounds[d][1] == 1.0]

    doc = {
        "card_id": card,
        "model_id": model_id,
        "purpose": "raw enumeration backing the counts quoted in oq_rulings.json; read-only "
                   "product metadata, no calculation, no expected value",
        "code_root": args.code_root,
        "model_registry_sha256": sha256_file(os.path.join(args.code_root, "model_registry.py")),
        "model_extensions_sha256": sha256_file(os.path.join(args.code_root, "model_extensions.py")),
        "registry_totals": {
            "models": registry_totals["models"],
            "drivers": registry_totals["drivers"],
            "ratio_drivers": registry_totals["ratio_drivers"],
            "ratio_drivers_whose_bounds_are_not_0_1": len(ratio_not_in_0_1),
        },
        "ratio_drivers_whose_bounds_are_not_0_1": ratio_not_in_0_1,
        "signed_driver_names_in_the_module": signed,
        "card_model": {
            "required": list(spec.required),
            "optional": list(spec.optional),
            "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
            "explicit_driver_bounds": {k: [None if b[0] is None else b[0],
                                           None if b[1] is None else b[1]]
                                       for k, b in dict(spec.driver_bounds).items()},
            "ratio_drivers": sorted(spec.ratio_drivers),
            "dimensions": dict(spec.dimensions),
            "effective_bounds": effective_bounds,
            "formula": spec.formula,
        },
        "counts": {
            "card_required_drivers": len(spec.required),
            "card_optional_drivers": len(spec.optional),
            "card_optional_drivers_without_an_explicit_default": len(optional_without_default),
            "card_optional_drivers_without_an_explicit_default_names": optional_without_default,
            "card_optional_drivers_with_an_explicit_default": optional_with_explicit_default,
            "card_drivers_signed_and_unbounded": len(unbounded_drivers),
            "card_drivers_signed_and_unbounded_names": unbounded_drivers,
            "card_drivers_in_the_module_signed_set": len(signed_drivers_of_this_model),
            "card_drivers_in_the_module_signed_set_names": signed_drivers_of_this_model,
            "card_drivers_with_lower_bound_exactly_zero": len(zero_lower_bound_drivers),
            "card_drivers_with_lower_bound_exactly_zero_names": zero_lower_bound_drivers,
            "card_drivers_with_inclusive_upper_bound_one": len(inclusive_upper_one_drivers),
            "card_drivers_with_inclusive_upper_bound_one_names": inclusive_upper_one_drivers,
        },
        "fill_mechanism_line": "scripts/model_registry.py:335 "
                               "drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))",
        "generated_at_unix": time.time(),
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(evidence, "oq_enumeration.json")
    doc = jsonable(doc)
    doc["number_format_note"] = ("non-finite bounds are written as the strings 'inf'/'-inf' "
                                 "because JSON has no infinity literal; finite bounds stay "
                                 "numbers")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=True, indent=1)
        handle.write("\n")

    print("card %s model %s" % (card, model_id))
    print("registry totals %s" % json.dumps(doc["registry_totals"], sort_keys=True))
    print("card counts %s" % json.dumps(doc["counts"], sort_keys=True))
    print("wrote %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
