"""Golden behavior lock (R9 step 1) — R1-R8 outputs must stay byte-identical.

Five model families (volume / capacity / subscriber / backlog / bank) each
get a full run through ``run_forecast``; the canonical hash of the entire
result is pinned here.  The R9 split must not change any of these hashes
(except version fields) — a change means the split altered behavior.

To refresh the baseline after a *deliberate, versioned* change:
    python -m pytest tests/test_golden_behavior_lock.py --update-golden
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_core import canonical_sha256, run_forecast  # noqa: E402
from test_data_contract import (  # noqa: E402
    apply_parameter_contract,
    finalize_contract,
    research_coverage,
)
from test_recognition_bridge import add_parameter, forecast_document  # noqa: E402

GOLDEN_PATH = Path(__file__).resolve().parent / "golden_behavior_hashes.json"

MODEL_SPECS = {
    # (model, {driver: (dimension, base_value)})
    "volume": ("resource", {"saleable_volume": ("quantity", 100.0), "realized_price": ("revenue_per_unit", 2.0)}),
    "capacity": ("capacity_utilization", {"capacity": ("quantity", 100.0), "utilization": ("ratio", 0.8), "yield": ("ratio", 0.9), "unit_revenue": ("revenue_per_unit", 2.0)}),
    "subscriber": ("subscription", {"average_customers": ("quantity", 30.0), "revenue_per_customer": ("revenue_per_unit", 2.0)}),
    "backlog": ("project_backlog", {"opening_backlog": ("backlog", 50.0), "bookings": ("backlog", 20.0), "cancellations": ("backlog", 5.0), "contract_changes": ("backlog", 2.0), "closing_backlog": ("backlog", 45.0)}),

    "bank": ("reserve_depletion", {"opening_reserves": ("reserve_volume", 100.0), "additions": ("reserve_volume", 10.0), "depletion": ("reserve_volume", 20.0), "closing_reserves": ("reserve_volume", 90.0), "recovery_rate": ("ratio", 0.9), "realized_price": ("revenue_per_unit", 2.0)}),
}


def model_document(family: str) -> dict:
    model, drivers = MODEL_SPECS[family]
    data = forecast_document()
    segment = {
        "name": family.title(),
        "base_revenue_parameter_id": family + "_base",
        "recognition": {
            "mode": "modeled_as_recognized",
            "timing": "point_in_time",
            "trigger": "customer acceptance",
            "presentation": "gross",
        },
        "scenarios": {},
    }
    if family == "backlog":
        # project_backlog requires an opening-backlog base parameter and
        # year-over-year continuity: opening[t+1] == closing[t].
        opening_param = {
            "parameter_id": "backlog_opening_base",
            "kind": "reported_fact",
            "value": 50.0,
            "unit": "quantity",
            "period": f"FY{data['base_year']}",
            "definition": "backlog opening base",
            "source_ids": ["filing"],
            "scenario": "shared",
            "rationale": "Golden backlog opening base.",
        }
        apply_parameter_contract(data, opening_param, "backlog")
        data["parameters"].append(opening_param)
        segment["base_backlog_parameter_id"] = "backlog_opening_base"
    base_param = {
        "parameter_id": family + "_base",
        "kind": "reported_fact",
        # Must reconcile with valid_document()'s reported total (150.0).
        "value": 150.0,
        "unit": data["currency"] + " " + data["unit"],
        "period": "FY" + str(data["base_year"]),
        "definition": family + " base revenue",
        "source_ids": ["filing"],
        "scenario": "shared",
        "rationale": "Golden behavior-lock base revenue.",
    }
    apply_parameter_contract(data, base_param, "revenue")
    data["parameters"].append(base_param)
    for scenario, multiplier in (("low", 0.85), ("base", 1.0), ("high", 1.15)):
        driver_ids = {}
        for position, (driver, (dimension, base_value)) in enumerate(drivers.items()):
            scale = multiplier if position == 0 else 1.0
            if family == "backlog" and driver == "opening_backlog":
                scale = 1.0  # opening must reconcile to base_backlog_parameter_id
            if family == "bank":
                scale = 1.0  # stock-flow balance must hold per scenario
            value = base_value * scale
            per_year = []
            for offset, year in enumerate(data["forecast_years"]):
                # Continuity: opening[t+1] == closing[t] (backlog & reserves).
                if family == "backlog" and driver == "opening_backlog" and offset > 0:
                    value = 45.0
                elif family == "backlog" and driver == "closing_backlog" and offset == 0:
                    value = 45.0
                elif family == "backlog" and driver == "closing_backlog" and offset > 0:
                    value = 40.0
                elif family == "bank" and driver == "opening_reserves" and offset > 0:
                    value = 90.0
                elif family == "bank" and driver == "closing_reserves" and offset == 0:
                    value = 90.0
                elif family == "bank" and driver == "closing_reserves" and offset > 0:
                    value = 80.0
                per_year.append(value)
            driver_ids[driver] = [
                add_parameter(
                    data,
                    f"{family}_{driver}_{scenario}_{year}",
                    per_year[index],
                    year,
                    scenario,
                    dimension=dimension,
                )
                for index, year in enumerate(data["forecast_years"])
            ]
        segment["scenarios"][scenario] = {
            "model": model,
            "driver_parameter_ids": driver_ids,
            "rationale": scenario + " golden " + family + " test",
        }
    data["segments"] = [segment]
    # research_coverage must reference parameters the model actually uses.
    base_year_driver_ids = [
        f"{family}_{driver}_base_{year}" for driver in drivers for year in data["forecast_years"][:1]
    ]
    data["research_coverage"] = research_coverage(
        [family + "_base"], growth_parameter_ids=base_year_driver_ids
    )
    finalize_contract(data)
    return data


def run_family(family: str) -> dict:
    return run_forecast(model_document(family))


class GoldenBehaviorLockTests(unittest.TestCase):
    def test_all_model_family_outputs_are_pinned(self) -> None:
        expected = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(expected), set(MODEL_SPECS), "golden file model drift")
        for family in MODEL_SPECS:
            result = run_family(family)
            actual = canonical_sha256(result)
            self.assertEqual(
                actual,
                expected[family],
                f"{family} output hash changed — R9 split must be "
                "behavior-locked (byte-identical outputs)",
            )


if __name__ == "__main__":
    if "--update-golden" in sys.argv:
        hashes = {family: canonical_sha256(run_family(family)) for family in MODEL_SPECS}
        GOLDEN_PATH.write_text(
            json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"golden updated: {GOLDEN_PATH}")
    else:
        unittest.main()
