"""Extra boundary probes for cards M29/M30/M31: measured, NON-GATING observations.

These probes are deliberately NOT part of the frozen oracle and NOT part of the runner's
exit code.  They exist because the enumeration (scripts/enumerate_registry.py) reports the
effective bounds, and a bound is only a claim until a value at or beyond it is actually fed
to the calculator.

Each probe states its expectation BEFORE the call, computed by plain arithmetic in this
file (never by the product), and records whether the measured value matched.

Writes <attempt>/evidence/<CARD>/extra_probes.json.  The frozen evidence is read only.

Usage:
  python -X utf8 -B probe_extra.py --card M29 --attempt-root <attempt> --code-root <iso>
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import traceback

# expectation_source documents WHERE the pre-registered expectation comes from.
PROBES = {
    "M29": [
        {"id": "PROBE-RATIO-EDGE-ONE",
         "why": ("adoption_rate carries the ratio domain [0,1]; the card-specific negative uses 1.1, so "
                 "this probe measures the inclusive upper edge. Demand 1000 x 1.0 = 1000, min(1000,150) "
                 "= 150, 150 x 0.5 x 4 = 300"),
         "patch": {"adoption_rate": [1.0]},
         "expectation_source": "inclusive upper edge of the ratio domain",
         "expected_if_inclusive": 300.0,
         "expected_if_exclusive": "ModelRegistryError"},
        {"id": "PROBE-QUANTITY-EDGE-ZERO",
         "why": ("the quantity domain starts at 0; expected min(0 x 0.2, 150) x 0.5 x 4 = 0"),
         "patch": {"eligible_units": [0]},
         "expectation_source": "inclusive lower edge of the quantity domain",
         "expected_if_inclusive": 0.0,
         "expected_if_exclusive": "ModelRegistryError"},
        {"id": "PROBE-CAPACITY-EDGE-ZERO",
         "why": ("annual_supply_capacity = 0 is the lower edge of the quantity domain and the min() "
                 "must then bind on the supply side: min(200, 0) x 0.5 x 4 = 0"),
         "patch": {"annual_supply_capacity": [0.0]},
         "expectation_source": "inclusive lower edge of the quantity domain",
         "expected_if_inclusive": 0.0,
         "expected_if_exclusive": "ModelRegistryError"},
        {"id": "PROBE-NET-PRICE-EDGE-ZERO",
         "why": ("net_revenue_per_unit = 0 is the lower edge of the revenue_per_unit domain; expected "
                 "min(200, 150) x 0.5 x 0 = 0"),
         "patch": {"net_revenue_per_unit": [0.0]},
         "expectation_source": "inclusive lower edge of the revenue_per_unit domain",
         "expected_if_inclusive": 0.0,
         "expected_if_exclusive": "ModelRegistryError"},
    ],
    "M30": [
        {"id": "PROBE-OPENING-EDGE-ZERO",
         "why": ("the unserved-market quantity domain starts at 0 and the bridge must still balance; "
                 "expected the same revenue line 200 x 3 = 600 with closing = 0"),
         "patch": {"opening_unserved_market": [0], "closing_unserved_market": [0]},
         "expectation_source": "inclusive lower edge of the quantity domain",
         "expected_if_inclusive": 600.0,
         "expected_if_exclusive": "ModelRegistryError"},
        {"id": "PROBE-CONTINUITY-TOLERANCE",
         "why": ("the cross-year continuity check uses math.isclose(rel_tol=1e-9, abs_tol=1e-9), so a "
                 "1e-10 imbalance in a balancing year must be tolerated while the 1.0 imbalance of "
                 "CONT-BREAK is rejected; this probe measures the tolerant side"),
         "base_input": "continuity_positive",
         "patch": {"opening_unserved_market": [500, 350.0000000001],
                   "closing_unserved_market": [350, 350.0000000001]},
         "expectation_source": "math.isclose(rel_tol=1e-9, abs_tol=1e-9)",
         "expected_if_tolerant": "accepted",
         "expected_if_exact": "ModelRegistryError"},
    ],
    "M31": [
        {"id": "PROBE-SCRAP-EXCEEDS-OPENING",
         "why": ("scrapped_units has no cross-driver guard of its own; this probe measures whether a "
                 "scrap larger than the opening inventory is accepted as long as the closing balance "
                 "is stated consistently (domain check only)"),
         "patch": {"scrapped_units": [200.0], "closing_inventory": [-30.0]},
         "expectation_source": ("no cross-driver guard is declared, but closing_inventory is a "
                                "quantity with lower bound 0, so a negative closing balance must be "
                                "refused by the domain check"),
         "expected_if_domain_only": "ModelRegistryError",
         "expected_if_scrap_guard": "ModelRegistryError"},
        {"id": "PROBE-SOLD-EXCEEDS-OPENING",
         "why": ("sold_units = 200 exceeds opening 100 while the bridge still balances "
                 "(100 + 0 + 0 - 0 - 200 = -100), which would require a negative closing balance; the "
                 "closing_inventory domain must refuse it"),
         "patch": {"sold_units": [200.0], "saleable_production": [0.0], "purchased_units": [0.0],
                   "scrapped_units": [0.0], "closing_inventory": [-100.0]},
         "expectation_source": "quantity domain lower bound 0 on closing_inventory",
         "expected_if_domain_only": "ModelRegistryError",
         "expected_if_sold_guard": "ModelRegistryError"},
        {"id": "PROBE-CONTINUITY-TOLERANCE",
         "why": ("the cross-year continuity check uses math.isclose(rel_tol=1e-9, abs_tol=1e-9), so a "
                 "1e-10 imbalance in a balancing year must be tolerated while the 1.0 imbalance of "
                 "CONT-BREAK is rejected; this probe measures the tolerant side"),
         "base_input": "continuity_positive",
         "patch": {"opening_inventory": [100, 85.0000000001],
                   "closing_inventory": [85, 85.0000000001]},
         "expectation_source": "math.isclose(rel_tol=1e-9, abs_tol=1e-9)",
         "expected_if_tolerant": "accepted",
         "expected_if_exact": "ModelRegistryError"},
    ],
}

CARDS = {
    "M29": "commercial_launch",
    "M30": "finite_adoption",
    "M31": "inventory_sellthrough",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--code-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    with open(os.path.join(evidence, "input.json"), "r", encoding="utf-8") as handle:
        input_doc = json.load(handle)

    sys.path.insert(0, os.path.abspath(args.code_root))
    import model_registry  # noqa: E402

    results = []
    for probe in PROBES[card]:
        spec = copy.deepcopy(input_doc[probe.get("base_input", "positive")])
        for driver, values in probe["patch"].items():
            spec["drivers"][driver] = copy.deepcopy(values)
        entry = {k: v for k, v in probe.items() if k not in ("patch", "base_input")}
        entry["base_input"] = probe.get("base_input", "positive")
        entry["patch"] = probe["patch"]
        entry["mutated_input_repr"] = (repr(spec["drivers"])[:400] + " years=" + repr(spec["years"]))
        try:
            value = model_registry.calculate_registered_model(
                model_id=spec["model_id"], base_revenue=spec["base_revenue"],
                drivers=spec["drivers"], years=spec["years"])
            entry["raised"] = None
            entry["actual"] = [float(v) for v in value]
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
        if entry["raised"] is None:
            for key, expected in probe.items():
                if key.startswith("expected_if_") and isinstance(expected, (int, float)):
                    entry["matches_" + key] = (
                        len(entry["actual"]) == 1 and abs(entry["actual"][0] - expected) <= 1e-9)
        results.append(entry)

    doc = {
        "card_id": card,
        "model_id": CARDS[card],
        "gating": False,
        "purpose": ("measured boundary observations of the documented domains; they are NOT part of "
                    "the frozen oracle and NOT part of the runner's exit code"),
        "expectation_rule": ("each expectation is computed by plain arithmetic in this file before the "
                             "call and never taken from the product"),
        "code_root": os.path.abspath(args.code_root),
        "probes": results,
    }
    out = os.path.join(evidence, "extra_probes.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    for entry in results:
        print("probe", entry["id"], "raised=", entry["raised"], "actual=", entry.get("actual"),
              {k: v for k, v in entry.items() if k.startswith("matches_")})
    print("written", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
