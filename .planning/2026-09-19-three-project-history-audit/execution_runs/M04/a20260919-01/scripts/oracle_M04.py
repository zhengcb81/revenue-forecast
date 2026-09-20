"""M04 independent oracle + negative-case spec (NO product import).

Stdlib only. See oracle_M01.py for the shared conventions.
Disclosed figures come from SMIC's FY2024 annual report (read-only PDF),
pages 6 / 8 / 84; the values below were transcribed by hand from the extracted
page text stored in before/probe01_smic.json and before/probe02_smic.json.

ASCII-only stdout (GBK console safe).
"""

from __future__ import annotations

import json
import os
from decimal import Decimal, getcontext

getcontext().prec = 50

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ATTEMPT, "evidence", "M04")

POSITIVE_INPUT = {
    "model_id": "capacity_utilization",
    "base_revenue": 0,
    "drivers": {"capacity": [1000], "utilization": [0.8], "yield": [0.9], "unit_revenue": [2],
                "timing_factor": [0.5], "other_revenue": [10]},
    "years": [2027],
}

CONTINUITY_POSITIVE_INPUT = {
    "model_id": "capacity_utilization",
    "base_revenue": 0,
    "drivers": {"capacity": [100, 120], "utilization": [0.8, 0.8], "yield": [0.9, 0.9],
                "unit_revenue": [2, 2], "timing_factor": [1, 1], "other_revenue": [0, 0]},
    "years": [2027, 2028],
}

DEFAULTS_INPUT = {
    "model_id": "capacity_utilization",
    "base_revenue": 0,
    "drivers": {"capacity": [1000], "utilization": [0.8], "yield": [0.9], "unit_revenue": [2]},
    "years": [2027],
}

# ---------------- SMIC FY2024 disclosed figures ----------------
SMIC_MONTHLY_CAPACITY_WAFERS = Decimal("948000")    # p6/p84: 94.8万片/月 折合8英寸标准逻辑 (year-end)
SMIC_UTILIZATION = Decimal("0.856")                 # p6: 产能利用率 85.6%
SMIC_WAFERS_SOLD = Decimal("8021000")               # p84: 销售晶圆 802.1万片 折合8英寸
SMIC_REVENUE_2024_CNY = Decimal("57795570000")      # p8: 57,795,570 千元
SMIC_REVENUE_2023_CNY = Decimal("45250425000")      # p8: 45,250,425 千元
MONTHS_PER_YEAR = Decimal("12")


def capacity_oracle(capacity, utilization, yield_, unit_revenue, timing_factor, other_revenue):
    out = []
    for c, u, y, r, t, o in zip(capacity, utilization, yield_, unit_revenue, timing_factor, other_revenue):
        out.append(Decimal(str(c)) * Decimal(str(u)) * Decimal(str(y)) * Decimal(str(r))
                   * Decimal(str(t)) + Decimal(str(o)))
    return out


def disclosure_arithmetic():
    annualized_capacity = SMIC_MONTHLY_CAPACITY_WAFERS * MONTHS_PER_YEAR
    good_output_year_end_basis = annualized_capacity * SMIC_UTILIZATION
    unit_revenue_derived = SMIC_REVENUE_2024_CNY / good_output_year_end_basis
    rebuild = good_output_year_end_basis * unit_revenue_derived
    gap_units = good_output_year_end_basis - SMIC_WAFERS_SOLD
    gap_pct = gap_units / SMIC_WAFERS_SOLD * Decimal(100)
    implied_available_capacity = SMIC_WAFERS_SOLD / SMIC_UTILIZATION
    implied_monthly = implied_available_capacity / MONTHS_PER_YEAR
    ratio_to_year_end = implied_available_capacity / annualized_capacity * Decimal(100)
    return {
        "source": "SMIC FY2024 annual report, pages 6 / 8 / 84",
        "capacity_annualized_from_year_end_monthly": str(annualized_capacity),
        "utilization": str(SMIC_UTILIZATION),
        "yield_used": "1 (SMIC discloses no numeric yield; the disclosed utilisation is an "
                      "effective-output/available-capacity ratio, so yield must not be applied twice)",
        "timing_factor": "1 (capacity is a full-year figure)",
        "good_output_year_end_basis": str(good_output_year_end_basis),
        "unit_revenue_cny_per_wafer_derived": str(unit_revenue_derived.quantize(Decimal("0.000001"))),
        "rebuild_cny": str(rebuild),
        "disclosed_revenue_2024_cny": str(SMIC_REVENUE_2024_CNY),
        "residual_cny": str(SMIC_REVENUE_2024_CNY - rebuild),
        "constructive_note": ("unit_revenue is derived from the same disclosed revenue divided by the model's "
                              "own output, so the zero residual is an identity. The informative check is the "
                              "wafer-count reconciliation below."),
        "wafer_count_reconciliation": {
            "model_output_wafers_year_end_basis": str(good_output_year_end_basis),
            "disclosed_wafers_sold": str(SMIC_WAFERS_SOLD),
            "gap_wafers": str(gap_units),
            "gap_pct_of_disclosed": str(gap_pct.quantize(Decimal("0.0001"))),
            "frozen_tolerance_pct": "0.5",
            "verdict": "FAILS the frozen 0.5% tolerance by a wide margin",
            "diagnosis": ("year-end monthly capacity annualised is not the year-average available capacity; "
                          "SMIC was expanding all year, so year-end capacity exceeds the full-year average"),
            "implied_available_capacity_diagnostic_only": str(implied_available_capacity.quantize(Decimal("0.01"))),
            "implied_monthly_capacity_diagnostic_only": str(implied_monthly.quantize(Decimal("0.01"))),
            "implied_share_of_year_end_annualised_pct": str(ratio_to_year_end.quantize(Decimal("0.0001"))),
            "warning": ("the implied figures are back-solved from disclosed volume and must NOT be presented "
                        "as disclosed parameters"),
        },
        "revenue_yoy_check": {
            "revenue_2024_cny": str(SMIC_REVENUE_2024_CNY),
            "revenue_2023_cny": str(SMIC_REVENUE_2023_CNY),
            "recomputed_pct": str(((SMIC_REVENUE_2024_CNY / SMIC_REVENUE_2023_CNY - Decimal(1)) * Decimal(100))
                                  .quantize(Decimal("0.0001"))),
            "disclosed_pct": "27.7",
        },
        "yield_disclosure_probe": "full-text search for 良率 returned 2 hits (pages 13 and 34), both qualitative",
        "not_a_forecast": "FY2024 is closed and already disclosed; this is a historical mapping probe only",
    }


def main() -> int:
    os.makedirs(EVIDENCE, exist_ok=True)

    expected = capacity_oracle(POSITIVE_INPUT["drivers"]["capacity"], POSITIVE_INPUT["drivers"]["utilization"],
                               POSITIVE_INPUT["drivers"]["yield"], POSITIVE_INPUT["drivers"]["unit_revenue"],
                               POSITIVE_INPUT["drivers"]["timing_factor"],
                               POSITIVE_INPUT["drivers"]["other_revenue"])
    continuity_expected = capacity_oracle(
        CONTINUITY_POSITIVE_INPUT["drivers"]["capacity"], CONTINUITY_POSITIVE_INPUT["drivers"]["utilization"],
        CONTINUITY_POSITIVE_INPUT["drivers"]["yield"], CONTINUITY_POSITIVE_INPUT["drivers"]["unit_revenue"],
        CONTINUITY_POSITIVE_INPUT["drivers"]["timing_factor"],
        CONTINUITY_POSITIVE_INPUT["drivers"]["other_revenue"])
    defaults_expected = [Decimal("1440")]

    input_doc = {
        "card_id": "M04",
        "oracle_source": "scripts/oracle_M04.py (stdlib only; no product import)",
        "positive": POSITIVE_INPUT,
        "continuity_positive": CONTINUITY_POSITIVE_INPUT,
        "defaults_case": DEFAULTS_INPUT,
    }
    oracle_doc = {
        "card_id": "M04",
        "model_id": "capacity_utilization",
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
        "positive": {
            "expected": [str(v) for v in expected],
            "expected_float": [float(v) for v in expected],
            "length": len(expected),
            "years": POSITIVE_INPUT["years"],
            "tolerances": [float(Decimal("1e-9") * max(Decimal(1), abs(v))) for v in expected],
            "hand_arithmetic": ["1000 * 0.8 = 800", "800 * 0.9 = 720", "720 * 2 = 1440",
                                "1440 * 0.5 = 720", "720 + 10 = 730"],
        },
        "continuity_positive": {
            "expected": [str(v) for v in continuity_expected],
            "expected_float": [float(v) for v in continuity_expected],
            "years": CONTINUITY_POSITIVE_INPUT["years"],
        },
        "defaults_case": {
            "expected": [str(v) for v in defaults_expected],
            "expected_float": [float(v) for v in defaults_expected],
            "why": "timing_factor defaults to 1.0 and other_revenue to 0.0; the default is NOT an "
                   "authorisation to fill 1/0 when the disclosure is missing",
        },
        "disclosure_arithmetic": disclosure_arithmetic(),
        "observation_expected": {
            "DEFAULTS-CASE": {"expected_float": [float(v) for v in defaults_expected]},
        },
        "not_from_product_code": True,
    }
    cases_doc = {
        "card_id": "M04",
        "first_required_driver": "capacity",
        "independent_deepcopy_per_case": True,
        "continuity_first_positive": "continuity_positive",
        "extra_observations": [
            {"id": "DEFAULTS-CASE", "input": "defaults_case",
             "expectation": "output [1440] proving the documented optional defaults"},
        ],
        "cases": [
            {"id": "NEG-CARD", "kind": "set_driver", "driver": "utilization", "value": [1.1],
             "expected": "ModelRegistryError", "why": "utilisation is a ratio in [0,1] (card line 44)"},
            {"id": "N01a", "kind": "set_driver_element", "driver": "capacity", "index": 0,
             "value": {"__bool__": True}, "expected": "ModelRegistryError", "why": "bool is not numeric"},
            {"id": "N01b", "kind": "set_driver_element", "driver": "capacity", "index": 0,
             "value": {"__float__": "nan"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N01c", "kind": "set_driver_element", "driver": "capacity", "index": 0,
             "value": {"__float__": "inf"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N01d", "kind": "set_driver_element", "driver": "capacity", "index": 0,
             "value": {"__float__": "-inf"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N02", "kind": "set_driver", "driver": "capacity", "value": [],
             "expected": "ModelRegistryError", "why": "path length 0 != len(years)=1"},
            {"id": "N03", "kind": "delete_driver", "driver": "capacity",
             "expected": "ModelRegistryError", "why": "required driver missing"},
            {"id": "N04", "kind": "add_driver", "driver": "unknown_driver", "value": [1],
             "expected": "ModelRegistryError", "why": "unknown driver"},
            {"id": "N05a", "kind": "set_years", "value": [], "expected": "ModelRegistryError",
             "why": "empty fiscal-year list"},
            {"id": "N05b", "kind": "set_years", "value": {"__bool__first__": True},
             "expected": "ModelRegistryError", "why": "True is not a fiscal year"},
            {"id": "R2-YIELD", "kind": "set_driver", "driver": "yield", "value": [1.2],
             "expected": "ModelRegistryError", "why": "yield is a ratio in [0,1]"},
            {"id": "R3-CAPACITY-NEG", "kind": "set_driver", "driver": "capacity", "value": [-1],
             "expected": "ModelRegistryError", "why": "negative capacity"},
            {"id": "R3-UNIT-REV-NEG", "kind": "set_driver", "driver": "unit_revenue", "value": [-2],
             "expected": "ModelRegistryError", "why": "negative revenue per good unit"},
            {"id": "R8-NET-NEG", "kind": "set_driver", "driver": "other_revenue", "value": [-2000],
             "expected": "ModelRegistryError",
             "why": "signed other_revenue may be negative but the resulting revenue cannot be negative"},
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

    d = oracle_doc["disclosure_arithmetic"]
    print("positive expected:", [str(v) for v in expected])
    print("continuity expected:", [str(v) for v in continuity_expected])
    print("SMIC model output (year-end basis):", d["good_output_year_end_basis"],
          "disclosed wafers:", d["wafer_count_reconciliation"]["disclosed_wafers_sold"],
          "gap:", d["wafer_count_reconciliation"]["gap_wafers"],
          "gap_pct:", d["wafer_count_reconciliation"]["gap_pct_of_disclosed"])
    print("SMIC implied available capacity:", d["wafer_count_reconciliation"]["implied_available_capacity_diagnostic_only"],
          "=", d["wafer_count_reconciliation"]["implied_share_of_year_end_annualised_pct"], "% of year-end annualised")
    print("negative case count:", len(cases_doc["cases"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
