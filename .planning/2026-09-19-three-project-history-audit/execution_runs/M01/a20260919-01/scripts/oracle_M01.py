"""M01 independent oracle + negative-case spec (NO product import).

This script is deliberately standalone: it imports only the Python standard
library. It NEVER imports scripts/model_registry.py or any other product
module, and therefore cannot generate the expected values from the code under
test.

It writes three artefacts into the attempt evidence directory:
  input.json    - the frozen positive-case input (as the JSON-shaped oracle)
  oracle.json   - hand-computed / independently computed expected values
  cases.json    - the negative-case mutation plan consumed by run_M01.py

ASCII-only stdout (GBK console safe).
"""

from __future__ import annotations

import json
import os
import sys
from decimal import Decimal, getcontext

getcontext().prec = 50

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ATTEMPT, "evidence", "M01")

# --------------------------------------------------------------------------
# 1. Frozen positive case (verbatim from card_M01.md lines 12-29)
# --------------------------------------------------------------------------
POSITIVE_INPUT = {
    "model_id": "direct_growth",
    "base_revenue": 200,
    "drivers": {"growth_rate": [0.1, -0.5, -1]},
    "years": [2027, 2028, 2029],
}


def direct_growth_oracle(base_revenue, growth_rates):
    """R[t] = R[t-1] * (1 + g[t]); exact decimal arithmetic."""
    current = Decimal(str(base_revenue))
    out = []
    for g in growth_rates:
        current = current * (Decimal(1) + Decimal(str(g)))
        out.append(current)
    return out


# --------------------------------------------------------------------------
# 2. Continuity case (growth-semantics continuity, see oracle.md section 5)
# --------------------------------------------------------------------------
CONTINUITY_POSITIVE_INPUT = {
    "model_id": "direct_growth",
    "base_revenue": 100,
    "drivers": {"growth_rate": [0.1, 0.05]},
    "years": [2027, 2028],
}

# --------------------------------------------------------------------------
# 3. Disclosure-mapping arithmetic (real disclosed figures, ZJ FY2024/FY2025)
#    Figures were read from the frozen raw PDFs and are recorded with page
#    numbers and sha256 in evidence/M01/disclosure_mapping.json.
# --------------------------------------------------------------------------
ZJ_FY2024_REVENUE = Decimal("303639957153")
ZJ_FY2025_REVENUE = Decimal("349079082852")
ZJ_DISCLOSED_YOY_PCT = Decimal("14.96")


def disclosure_arithmetic():
    recomputed_growth = (ZJ_FY2025_REVENUE / ZJ_FY2024_REVENUE - Decimal(1)) * Decimal(100)
    predicted_fy2025 = ZJ_FY2024_REVENUE * (Decimal(1) + ZJ_DISCLOSED_YOY_PCT / Decimal(100))
    residual = ZJ_FY2025_REVENUE - predicted_fy2025
    return {
        "entity": "紫金矿业集团股份有限公司",
        "market": "CN",
        "segment": "group_total_operating_revenue",
        "base_year": 2024,
        "base_revenue_cny": str(ZJ_FY2024_REVENUE),
        "target_year": 2025,
        "target_revenue_cny_disclosed": str(ZJ_FY2025_REVENUE),
        "recomputed_yoy_pct": str(recomputed_growth.quantize(Decimal("0.0001"))),
        "disclosed_yoy_pct": str(ZJ_DISCLOSED_YOY_PCT),
        "formula_prediction_from_disclosed_rate_cny": str(predicted_fy2025),
        "residual_cny": str(residual),
        "residual_pct_of_disclosed": str(
            (residual / ZJ_FY2025_REVENUE * Decimal(100)).quantize(Decimal("0.000001"))
        ),
        "residual_sign_convention": "disclosed_minus_formula_prediction (positive = formula under-predicted)",
        "residual_note": (
            "The FY2025 report prints the growth column rounded to 2 decimals (14.96%); the exact "
            "ratio of the two disclosed figures is 14.9648%. The residual reported here uses the "
            "printed 14.96% so that the number is reproducible from the document alone."
        ),
        "scope_note": (
            "historical_mapping_probe only: a closed period, already-disclosed fact. "
            "NOT a three-scenario forecast and NOT accuracy evidence."
        ),
    }


# --------------------------------------------------------------------------
# 4. Negative-case plan. Each entry is an independent deep-copied input with a
#    single documented mutation; the harness applies it in memory (never via a
#    JSON parser, so parser rejections cannot masquerade as model rejections).
# --------------------------------------------------------------------------
def negative_cases():
    return [
        {"id": "NEG-CARD", "kind": "set_driver_element",
         "driver": "growth_rate", "index": 0, "value": {"__float__": -1.01},
         "expected": "ModelRegistryError",
         "why": "growth_rate below -1 leaves the documented [-1, inf) domain (card line 33/37)"},
        {"id": "N01a", "kind": "set_driver_element",
         "driver": "growth_rate", "index": 0, "value": {"__bool__": True},
         "expected": "ModelRegistryError",
         "why": "bool is not a numeric ratio"},
        {"id": "N01b", "kind": "set_driver_element",
         "driver": "growth_rate", "index": 0, "value": {"__float__": "nan"},
         "expected": "ModelRegistryError", "why": "non-finite value"},
        {"id": "N01c", "kind": "set_driver_element",
         "driver": "growth_rate", "index": 0, "value": {"__float__": "inf"},
         "expected": "ModelRegistryError", "why": "non-finite value"},
        {"id": "N01d", "kind": "set_driver_element",
         "driver": "growth_rate", "index": 0, "value": {"__float__": "-inf"},
         "expected": "ModelRegistryError", "why": "non-finite value"},
        {"id": "N02", "kind": "set_driver",
         "driver": "growth_rate", "value": [],
         "expected": "ModelRegistryError",
         "why": "path length 0 != len(years)=3"},
        {"id": "N03", "kind": "delete_driver",
         "driver": "growth_rate", "expected": "ModelRegistryError",
         "why": "required driver missing"},
        {"id": "N04", "kind": "add_driver",
         "driver": "unknown_driver", "value": [1, 1, 1],
         "expected": "ModelRegistryError", "why": "unknown driver"},
        {"id": "N05a", "kind": "set_years", "value": [],
         "expected": "ModelRegistryError", "why": "empty fiscal-year list"},
        {"id": "N05b", "kind": "set_years", "value": {"__bool__first__": True},
         "expected": "ModelRegistryError", "why": "True is not a fiscal year"},
        {"id": "CONT-BREAK", "kind": "set_years", "value": [2027, 2029],
         "base_input": "continuity_positive", "expected": "ModelRegistryError",
         "why": "fiscal years must be consecutive; growth compounding cannot bridge a gap year"},
    ]


def main() -> int:
    os.makedirs(EVIDENCE, exist_ok=True)

    expected = direct_growth_oracle(
        POSITIVE_INPUT["base_revenue"], POSITIVE_INPUT["drivers"]["growth_rate"]
    )
    continuity_expected = direct_growth_oracle(
        CONTINUITY_POSITIVE_INPUT["base_revenue"],
        CONTINUITY_POSITIVE_INPUT["drivers"]["growth_rate"],
    )

    input_doc = {
        "card_id": "M01",
        "oracle_source": "scripts/oracle_M01.py (stdlib only; no product import)",
        "positive": POSITIVE_INPUT,
        "continuity_positive": CONTINUITY_POSITIVE_INPUT,
    }
    oracle_doc = {
        "card_id": "M01",
        "model_id": "direct_growth",
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
        "positive": {
            "expected": [str(v) for v in expected],
            "expected_float": [float(v) for v in expected],
            "length": len(expected),
            "years": POSITIVE_INPUT["years"],
            "tolerances": [
                float(Decimal("1e-9") * max(Decimal(1), abs(v))) for v in expected
            ],
            "hand_arithmetic": [
                "200 * 1.1 = 220",
                "220 * 0.5 = 110",
                "110 * 0 = 0",
            ],
        },
        "continuity_positive": {
            "expected": [str(v) for v in continuity_expected],
            "expected_float": [float(v) for v in continuity_expected],
            "years": CONTINUITY_POSITIVE_INPUT["years"],
        },
        "disclosure_arithmetic": disclosure_arithmetic(),
        "not_from_product_code": True,
    }
    cases_doc = {
        "card_id": "M01",
        "first_required_driver": "growth_rate",
        "independent_deepcopy_per_case": True,
        "continuity_first_positive": "continuity_positive",
        "cases": negative_cases(),
    }

    for name, doc in (("input.json", input_doc), ("oracle.json", oracle_doc), ("cases.json", cases_doc)):
        path = os.path.join(EVIDENCE, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, ensure_ascii=False, indent=1)
        print("wrote", path)

    print("positive expected:", [str(v) for v in expected])
    print("continuity expected:", [str(v) for v in continuity_expected])
    d = oracle_doc["disclosure_arithmetic"]
    print("ZJ recomputed yoy pct:", d["recomputed_yoy_pct"], "disclosed:", d["disclosed_yoy_pct"])
    print("ZJ residual cny:", d["residual_cny"], "pct:", d["residual_pct_of_disclosed"])
    print("negative case count:", len(cases_doc["cases"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
