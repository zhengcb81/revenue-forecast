"""M02 independent oracle + negative-case spec (NO product import).

Stdlib only: this script cannot generate the expected values from the code
under test. See oracle_M01.py for the shared conventions.

ASCII-only stdout (GBK console safe).
"""

from __future__ import annotations

import json
import os
from decimal import Decimal, getcontext

getcontext().prec = 50

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ATTEMPT, "evidence", "M02")

POSITIVE_INPUT = {
    "model_id": "direct_revenue",
    "base_revenue": 0,
    "drivers": {"revenue": [80, 0, 120]},
    "years": [2027, 2028, 2029],
}

CONTINUITY_POSITIVE_INPUT = {
    "model_id": "direct_revenue",
    "base_revenue": 0,
    "drivers": {"revenue": [50, 60]},
    "years": [2027, 2028],
}

BASE_INDEPENDENCE_INPUT = {
    "model_id": "direct_revenue",
    "base_revenue": 999,
    "drivers": {"revenue": [80, 0, 120]},
    "years": [2027, 2028, 2029],
}

# Real disclosed figures (read-only) used for the disclosure mapping.
ZJ_FY2025_REVENUE = Decimal("349079082852")


def direct_revenue_oracle(values):
    """R[t] = revenue[t], exactly."""
    return [Decimal(str(v)) for v in values]


def main() -> int:
    os.makedirs(EVIDENCE, exist_ok=True)

    expected = direct_revenue_oracle(POSITIVE_INPUT["drivers"]["revenue"])
    continuity_expected = direct_revenue_oracle(CONTINUITY_POSITIVE_INPUT["drivers"]["revenue"])

    float_exactness = {
        "value": str(ZJ_FY2025_REVENUE),
        "float_roundtrip_exact": float(ZJ_FY2025_REVENUE) == int(ZJ_FY2025_REVENUE),
        "note": "349,079,082,852 < 2**53 so IEEE754 double represents it exactly; no rounding is introduced by using float inputs",
    }

    input_doc = {
        "card_id": "M02",
        "oracle_source": "scripts/oracle_M02.py (stdlib only; no product import)",
        "positive": POSITIVE_INPUT,
        "continuity_positive": CONTINUITY_POSITIVE_INPUT,
        "base_independence": BASE_INDEPENDENCE_INPUT,
    }
    oracle_doc = {
        "card_id": "M02",
        "model_id": "direct_revenue",
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
        "positive": {
            "expected": [str(v) for v in expected],
            "expected_float": [float(v) for v in expected],
            "length": len(expected),
            "years": POSITIVE_INPUT["years"],
            "tolerances": [float(Decimal("1e-9") * max(Decimal(1), abs(v))) for v in expected],
            "hand_arithmetic": ["copy 80", "copy 0 (must stay 0, not defaulted)", "copy 120"],
        },
        "continuity_positive": {
            "expected": [str(v) for v in continuity_expected],
            "expected_float": [float(v) for v in continuity_expected],
            "years": CONTINUITY_POSITIVE_INPUT["years"],
        },
        "base_independence": {
            "expected_same_as_positive": True,
            "expected_float": [float(v) for v in expected],
            "why": "card_M02.md line 8: R[t] = direct_revenue[t]; base_revenue is not a term",
        },
        "disclosure_arithmetic": {
            "entity": "紫金矿业集团股份有限公司",
            "reconciliation_is_constructive": True,
            "note": (
                "Filling the disclosed FY2025 revenue into the revenue driver reproduces it exactly, so the "
                "residual is trivially zero. This proves only that the copy step is right; it proves nothing "
                "about the source, period, gross/net basis or forecast usefulness of the revenue figure."
            ),
            "input_revenue_cny": str(ZJ_FY2025_REVENUE),
            "float_exactness": float_exactness,
        },
        "not_from_product_code": True,
    }
    cases_doc = {
        "card_id": "M02",
        "first_required_driver": "revenue",
        "independent_deepcopy_per_case": True,
        "continuity_first_positive": "continuity_positive",
        "extra_observations": [
            {"id": "BASE-INDEPENDENCE", "input": "base_independence",
             "expectation": "output identical to positive; NOT a rejection case"},
            {"id": "OBS-NEG-BASE", "kind": "set_base_revenue", "value": -5,
             "expectation": "observed and recorded as a design observation only; NOT counted as pass/fail "
                             "because direct_revenue never uses base_revenue"},
        ],
        "cases": [
            {"id": "NEG-CARD", "kind": "set_driver_element", "driver": "revenue", "index": 1,
             "value": {"__float__": -1}, "expected": "ModelRegistryError",
             "why": "negative recognised revenue is outside the [0, inf) revenue domain (card line 33)"},
            {"id": "N01a", "kind": "set_driver_element", "driver": "revenue", "index": 0,
             "value": {"__bool__": True}, "expected": "ModelRegistryError", "why": "bool is not numeric"},
            {"id": "N01b", "kind": "set_driver_element", "driver": "revenue", "index": 0,
             "value": {"__float__": "nan"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N01c", "kind": "set_driver_element", "driver": "revenue", "index": 0,
             "value": {"__float__": "inf"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N01d", "kind": "set_driver_element", "driver": "revenue", "index": 0,
             "value": {"__float__": "-inf"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N02", "kind": "set_driver", "driver": "revenue", "value": [],
             "expected": "ModelRegistryError", "why": "path length 0 != len(years)=3"},
            {"id": "N03", "kind": "delete_driver", "driver": "revenue",
             "expected": "ModelRegistryError", "why": "required driver missing"},
            {"id": "N04", "kind": "add_driver", "driver": "unknown_driver", "value": [1, 1, 1],
             "expected": "ModelRegistryError", "why": "unknown driver"},
            {"id": "N05a", "kind": "set_years", "value": [], "expected": "ModelRegistryError",
             "why": "empty fiscal-year list"},
            {"id": "N05b", "kind": "set_years", "value": {"__bool__first__": True},
             "expected": "ModelRegistryError", "why": "True is not a fiscal year"},
            {"id": "CONT-BREAK", "kind": "set_years", "value": [2027, 2029],
             "base_input": "continuity_positive", "expected": "ModelRegistryError",
             "why": "fiscal years must be consecutive"},
        ],
    }

    for name, doc in (("input.json", input_doc), ("oracle.json", oracle_doc), ("cases.json", cases_doc)):
        path = os.path.join(EVIDENCE, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, ensure_ascii=False, indent=1)
        print("wrote", path)

    print("positive expected:", [str(v) for v in expected])
    print("continuity expected:", [str(v) for v in continuity_expected])
    print("negative case count:", len(cases_doc["cases"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
