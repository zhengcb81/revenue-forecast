"""F-M08-07 evidence: re-enumerate the registry instead of trusting the counts.

Facts re-derived from the code, per card, from that attempt's own isolated copy:
  * every registered driver and its dimension (declared vs effective bounds)
  * the number of drivers whose dimension is "ratio"
  * which ratio drivers do NOT carry the inclusive [0,1] domain, and why
  * the revenue_per_activity / revenue_per_unit family and its exceptions

Effective bounds come from the product's own accessor
`model_registry.driver_value_bounds(model_id, driver)` so the enumeration cannot
disagree with runtime behaviour.

Writes evidence/<card>/oq_rulings_enumeration.json for every card and prints the
raw ASCII report.

Usage: <iso venv python> -X utf8 -B f07_enumerate.py > f07_enumerate.out.txt
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")
RATIO = "ratio"
MONEY_PER_ACTIVITY = ("revenue_per_activity", "revenue_per_unit")


def inf_marker(x: float) -> float | None:
    """JSON cannot carry Infinity portably; None means unbounded."""
    if x == math.inf or x == -math.inf:
        return None
    return x


def canon(bounds: tuple[float, float]) -> list:
    return [inf_marker(bounds[0]), inf_marker(bounds[1])]


def enumerate_registry(code_root: str) -> dict:
    if code_root not in sys.path:
        sys.path.insert(0, code_root)
    import model_registry as mr  # noqa: E402  (import path set at runtime)

    registry = mr.MODEL_REGISTRY
    ratio_drivers: list[dict] = []
    per_activity: list[dict] = []
    all_drivers = 0
    for model_id in sorted(registry):
        spec = registry[model_id]
        for driver in sorted(spec.dimensions):
            all_drivers += 1
            dim = spec.dimensions[driver]
            eff = mr.driver_value_bounds(model_id, driver)
            row = {
                "model_id": model_id,
                "driver": driver,
                "dimension": dim,
                "effective_bounds": canon(eff),
                "declared_bounds": (
                    [inf_marker(v) for v in spec.driver_bounds[driver]]
                    if driver in spec.driver_bounds
                    else None
                ),
                "in_0_1": eff[0] == 0.0 and eff[1] == 1.0,
            }
            if dim == RATIO:
                ratio_drivers.append(row)
            if dim in MONEY_PER_ACTIVITY:
                per_activity.append(row)

    outside = [r for r in ratio_drivers if not r["in_0_1"]]
    # why each one is outside: declared metadata vs the growth_rate special case
    for row in outside:
        if row["declared_bounds"] is not None:
            row["outside_reason"] = (
                "explicit spec.driver_bounds entry takes precedence over the "
                "conservative [0,1] ratio default"
            )
        elif row["driver"] == "growth_rate":
            row["outside_reason"] = (
                "hard-coded domain (-1, inf) in driver_value_bounds because a "
                "growth rate can legitimately be a contraction"
            )
        elif eff_is_signed(row):
            row["outside_reason"] = "listed in _SIGNED_DRIVERS"
        else:
            row["outside_reason"] = "unknown - needs investigation"

    registry_file = os.path.join(code_root, "model_registry.py")
    bounds_index = {}
    explicit_bounds_models = []
    for model_id in sorted(registry):
        spec = registry[model_id]
        for driver in sorted(spec.dimensions):
            bounds_index[f"{model_id}.{driver}"] = canon(
                mr.driver_value_bounds(model_id, driver)
            )
        if spec.driver_bounds:
            explicit_bounds_models.append(model_id)
    return {
        "code_root": code_root.replace("\\", "/"),
        "model_registry_file": registry_file.replace("\\", "/"),
        "model_registry_sha256": hashlib.sha256(open(registry_file, "rb").read()).hexdigest(),
        "models_total": len(registry),
        "drivers_total": all_drivers,
        "ratio_drivers_total": len(ratio_drivers),
        "ratio_drivers_not_in_0_1_total": len(outside),
        "ratio_drivers_not_in_0_1": outside,
        "ratio_drivers_in_0_1_total": len(ratio_drivers) - len(outside),
        "revenue_per_activity_or_per_unit_total": len(per_activity),
        "revenue_per_activity_or_per_unit_outside_0_inf": [
            r for r in per_activity if r["effective_bounds"] != [0.0, None]
        ],
        "ratio_driver_names": [f"{r['model_id']}.{r['driver']}" for r in ratio_drivers],
        "effective_bounds_index": bounds_index,
        "models_with_explicit_driver_bounds": explicit_bounds_models,
        "growth_rate_entry": next(
            (r for r in ratio_drivers if r["driver"] == "growth_rate"), None
        ),
    }


def eff_is_signed(row: dict) -> bool:
    b = row["effective_bounds"]
    return b[0] is None and b[1] is None


def main() -> int:
    print("== F-M08-07: independent re-enumeration of the model registry ==")
    print("effective bounds are read from the product accessor driver_value_bounds()")
    summary: dict[str, object] = {}
    for card in CARDS:
        code_root = os.path.join(BASE, card, "a20260919-01", "iso", "checkout_scripts")
        data = enumerate_registry(code_root)
        print("")
        print(f"-- {card} --")
        print(f"   code_root={data['code_root']}")
        print(f"   model_registry_sha256={data['model_registry_sha256']}")
        print(f"   models_total={data['models_total']} drivers_total={data['drivers_total']}")
        print(f"   ratio_drivers_total={data['ratio_drivers_total']} "
              f"(in_[0,1]={data['ratio_drivers_in_0_1_total']}, "
              f"NOT_in_[0,1]={data['ratio_drivers_not_in_0_1_total']})")
        for row in data["ratio_drivers_not_in_0_1"]:
            print(f"      ratio outside [0,1]: {row['model_id']}.{row['driver']} "
                  f"bounds={row['effective_bounds']} declared={row['declared_bounds']}")
            print(f"          reason: {row['outside_reason']}")
        print(f"   revenue_per_activity_or_per_unit_total="
              f"{data['revenue_per_activity_or_per_unit_total']}")
        for row in data["revenue_per_activity_or_per_unit_outside_0_inf"]:
            print(f"      priced-volume exception: {row['model_id']}.{row['driver']} "
                  f"bounds={row['effective_bounds']}")
        gr = data["growth_rate_entry"]
        print(f"   direct_growth.growth_rate: dimension={gr['dimension']} "
              f"effective_bounds={gr['effective_bounds']} declared={gr['declared_bounds']}")
        # write the per-card evidence file
        out = os.path.join(
            BASE, card, "a20260919-01", "evidence", card, "oq_rulings_enumeration.json"
        )
        payload = {"card_id": card, "enumerated_by": "implementer (this attempt)",
                   "enumeration": data}
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        summary[card] = {
            "ratio_drivers_total": data["ratio_drivers_total"],
            "ratio_drivers_not_in_0_1_total": data["ratio_drivers_not_in_0_1_total"],
            "ratio_drivers_not_in_0_1": [
                f"{r['model_id']}.{r['driver']}" for r in data["ratio_drivers_not_in_0_1"]
            ],
            "evidence_file": f"evidence/{card}/oq_rulings_enumeration.json",
            "evidence_sha256": hashlib.sha256(open(out, "rb").read()).hexdigest(),
        }
        print(f"   wrote evidence/{card}/oq_rulings_enumeration.json "
              f"sha256={summary[card]['evidence_sha256']}")

    with open(os.path.join(HERE, "f07_enumerate.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("")
    print("wrote f07_enumerate.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
