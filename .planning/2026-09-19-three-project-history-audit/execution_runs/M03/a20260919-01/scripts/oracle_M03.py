"""M03 independent oracle + negative-case spec (NO product import).

Stdlib only. See oracle_M01.py for the shared conventions.
Disclosed figures come from BYD's FY2024 annual report (read-only PDF), pages
3/14/23/24/25; the values below were transcribed by hand from the extracted
page text stored in before/probe01_byd.json and before/probe02_byd.json.

ASCII-only stdout (GBK console safe).
"""

from __future__ import annotations

import json
import os
from decimal import Decimal, getcontext

getcontext().prec = 50

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE = os.path.join(ATTEMPT, "evidence", "M03")

POSITIVE_INPUT = {
    "model_id": "unit_sales",
    "base_revenue": 0,
    "drivers": {"units": [120], "unit_revenue": [2.5], "timing_factor": [1], "other_revenue": [5]},
    "years": [2027],
}

CONTINUITY_POSITIVE_INPUT = {
    "model_id": "unit_sales",
    "base_revenue": 0,
    "drivers": {"units": [100, 110], "unit_revenue": [2, 2], "timing_factor": [1, 1],
                "other_revenue": [0, 0]},
    "years": [2027, 2028],
}

DEFAULTS_INPUT = {
    "model_id": "unit_sales",
    "base_revenue": 0,
    "drivers": {"units": [10], "unit_revenue": [3]},
    "years": [2027],
}

ZERO_UNITS_WITH_OTHER_INPUT = {
    "model_id": "unit_sales",
    "base_revenue": 0,
    "drivers": {"units": [0], "unit_revenue": [2.5], "timing_factor": [1], "other_revenue": [5]},
    "years": [2027],
}

# ---------------- BYD FY2024 disclosed figures (page 23 and 24/25) ----------------
BYD_PV_UNITS = Decimal("4250370")            # 乘用车 快报销量 (辆), p23
BYD_PV_REVENUE = Decimal("525989680000.00")  # 乘用车 销售收入（元）, p23
BYD_CV_UNITS = Decimal("21775")              # 商用车 快报销量 (辆), p23
BYD_CV_REVENUE = Decimal("7340435000.00")    # 商用车 销售收入（元）, p23
BYD_VEHICLE_UNITS_TOTAL = Decimal("4272145")  # 整车合计 快报销量 (辆), p23
BYD_AUTO_SEGMENT_REVENUE = Decimal("617381935000.00")  # 交通运输设备及电气制造业, p24/p25
BYD_PV_UNITS_2023 = Decimal("3024417")       # 乘用车 快报销量 2023 (辆), p23
BYD_AUTO_SEGMENT_REVENUE_2023 = Decimal("483453318000.00")  # p24


def unit_sales_oracle(units, unit_revenue, timing_factor, other_revenue):
    out = []
    for u, r, t, o in zip(units, unit_revenue, timing_factor, other_revenue):
        out.append(Decimal(str(u)) * Decimal(str(r)) * Decimal(str(t)) + Decimal(str(o)))
    return out


def disclosure_arithmetic():
    pv_unit_revenue = BYD_PV_REVENUE / BYD_PV_UNITS
    pv_rebuild = BYD_PV_UNITS * pv_unit_revenue
    cv_unit_revenue = BYD_CV_REVENUE / BYD_CV_UNITS
    cv_rebuild = BYD_CV_UNITS * cv_unit_revenue
    total_rebuild = BYD_VEHICLE_UNITS_TOTAL * pv_unit_revenue
    gap_vs_segment = BYD_AUTO_SEGMENT_REVENUE - total_rebuild
    other_auto_revenue = BYD_AUTO_SEGMENT_REVENUE - BYD_PV_REVENUE - BYD_CV_REVENUE
    return {
        "source": "BYD FY2024 annual report (cninfo:1222881496), pages 23/24/25",
        "mapping_1_same_table": {
            "units_pv": str(BYD_PV_UNITS),
            "revenue_pv_cny": str(BYD_PV_REVENUE),
            "unit_revenue_pv_cny_derived": str(pv_unit_revenue.quantize(Decimal("0.000001"))),
            "timing_factor": "1 (already full-year exposed volume; must not be scaled again)",
            "other_revenue": "0 (not disclosed in that table; not assumed)",
            "rebuild_cny": str(pv_rebuild),
            "disclosed_cny": str(BYD_PV_REVENUE),
            "residual_cny": str(BYD_PV_REVENUE - pv_rebuild),
            "residual_pct": "0.000000",
            "constructive_note": (
                "unit_revenue is derived by dividing the SAME disclosed revenue cell by the SAME "
                "disclosed volume cell, so the zero residual is an identity, not evidence. It proves "
                "dimensional wiring only."
            ),
        },
        "mapping_1b_commercial_vehicle": {
            "units_cv": str(BYD_CV_UNITS),
            "revenue_cv_cny": str(BYD_CV_REVENUE),
            "unit_revenue_cv_cny_derived": str(cv_unit_revenue.quantize(Decimal("0.000001"))),
            "rebuild_cny": str(cv_rebuild),
            "residual_cny": str(BYD_CV_REVENUE - cv_rebuild),
        },
        "mapping_2_scope_residual": {
            "auto_segment_revenue_cny": str(BYD_AUTO_SEGMENT_REVENUE),
            "vehicle_units_total": str(BYD_VEHICLE_UNITS_TOTAL),
            "rebuild_using_vehicle_total_at_pv_unit_price_cny": str(total_rebuild.quantize(Decimal("0.01"))),
            "gap_cny": str(gap_vs_segment.quantize(Decimal("0.01"))),
            "gap_pct_of_segment": str((gap_vs_segment / BYD_AUTO_SEGMENT_REVENUE * Decimal(100))
                                      .quantize(Decimal("0.0001"))),
            "other_auto_revenue_not_in_the_vehicle_production_sales_table_cny":
                str(other_auto_revenue.quantize(Decimal("0.01"))),
            "why": (
                "The automobile segment revenue line also contains secondary rechargeable batteries, "
                "vehicle parts and other products, which unit_sales cannot identify. The gap must NOT be "
                "silently treated as residual revenue."
            ),
        },
        "mapping_3_mix": {
            "pv_units_2023": str(BYD_PV_UNITS_2023),
            "auto_segment_revenue_2023_cny": str(BYD_AUTO_SEGMENT_REVENUE_2023),
            "implied_pv_unit_price_2023_cny": str((BYD_AUTO_SEGMENT_REVENUE_2023 / BYD_PV_UNITS_2023)
                                                  .quantize(Decimal("0.000001"))),
            "note": "single unit price hides the sedan/SUV/MPV mix (p23 lines: 2,370,709 / 1,805,441 / 104,934)",
        },
        "not_a_forecast": "FY2024 is a closed, already-disclosed period; this is a historical mapping probe only",
    }


def main() -> int:
    os.makedirs(EVIDENCE, exist_ok=True)

    expected = unit_sales_oracle(POSITIVE_INPUT["drivers"]["units"],
                                 POSITIVE_INPUT["drivers"]["unit_revenue"],
                                 POSITIVE_INPUT["drivers"]["timing_factor"],
                                 POSITIVE_INPUT["drivers"]["other_revenue"])
    continuity_expected = unit_sales_oracle(CONTINUITY_POSITIVE_INPUT["drivers"]["units"],
                                            CONTINUITY_POSITIVE_INPUT["drivers"]["unit_revenue"],
                                            CONTINUITY_POSITIVE_INPUT["drivers"]["timing_factor"],
                                            CONTINUITY_POSITIVE_INPUT["drivers"]["other_revenue"])
    defaults_expected = [Decimal("30")]
    zero_units_expected = [Decimal("5")]

    input_doc = {
        "card_id": "M03",
        "oracle_source": "scripts/oracle_M03.py (stdlib only; no product import)",
        "positive": POSITIVE_INPUT,
        "continuity_positive": CONTINUITY_POSITIVE_INPUT,
        "defaults_case": DEFAULTS_INPUT,
        "zero_units_with_other": ZERO_UNITS_WITH_OTHER_INPUT,
    }
    oracle_doc = {
        "card_id": "M03",
        "model_id": "unit_sales",
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
        "positive": {
            "expected": [str(v) for v in expected],
            "expected_float": [float(v) for v in expected],
            "length": len(expected),
            "years": POSITIVE_INPUT["years"],
            "tolerances": [float(Decimal("1e-9") * max(Decimal(1), abs(v))) for v in expected],
            "hand_arithmetic": ["120 * 2.5 = 300", "300 * 1 = 300", "300 + 5 = 305"],
        },
        "continuity_positive": {
            "expected": [str(v) for v in continuity_expected],
            "expected_float": [float(v) for v in continuity_expected],
            "years": CONTINUITY_POSITIVE_INPUT["years"],
        },
        "defaults_case": {
            "expected": [str(v) for v in defaults_expected],
            "expected_float": [float(v) for v in defaults_expected],
            "why": "optional timing_factor defaults to 1.0 and other_revenue to 0.0; the default is NOT an "
                   "authorisation to fill 1/0 when the disclosure is missing",
        },
        "zero_units_with_other": {
            "expected": [str(v) for v in zero_units_expected],
            "expected_float": [float(v) for v in zero_units_expected],
            "why": "zero confirmed volume must not be treated as 'missing'; other_revenue still applies",
        },
        "disclosure_arithmetic": disclosure_arithmetic(),
        "observation_expected": {
            "DEFAULTS-CASE": {"expected_float": [float(v) for v in defaults_expected]},
            "ZERO-UNITS": {"expected_float": [float(v) for v in zero_units_expected]},
        },
        "not_from_product_code": True,
    }
    cases_doc = {
        "card_id": "M03",
        "first_required_driver": "units",
        "independent_deepcopy_per_case": True,
        "continuity_first_positive": "continuity_positive",
        "extra_observations": [
            {"id": "DEFAULTS-CASE", "input": "defaults_case",
             "expectation": "output [30] proving the documented optional defaults"},
            {"id": "ZERO-UNITS", "input": "zero_units_with_other",
             "expectation": "output [5]; zero volume is data, not a missing field"},
            {"id": "OBS-NEG-OTHER", "kind": "set_driver", "driver": "other_revenue", "value": [-10],
             "expectation": "recorded as a design observation: other_revenue is a signed driver, but a "
                             "negative net revenue result must still be refused; NOT counted as pass/fail"},
        ],
        "cases": [
            {"id": "NEG-CARD", "kind": "set_driver", "driver": "units", "value": [-1],
             "expected": "ModelRegistryError",
             "why": "negative confirmed sales volume; returns must already be netted into units or unit_revenue"},
            {"id": "N01a", "kind": "set_driver_element", "driver": "units", "index": 0,
             "value": {"__bool__": True}, "expected": "ModelRegistryError", "why": "bool is not numeric"},
            {"id": "N01b", "kind": "set_driver_element", "driver": "units", "index": 0,
             "value": {"__float__": "nan"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N01c", "kind": "set_driver_element", "driver": "units", "index": 0,
             "value": {"__float__": "inf"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N01d", "kind": "set_driver_element", "driver": "units", "index": 0,
             "value": {"__float__": "-inf"}, "expected": "ModelRegistryError", "why": "non-finite"},
            {"id": "N02", "kind": "set_driver", "driver": "units", "value": [],
             "expected": "ModelRegistryError", "why": "path length 0 != len(years)=1"},
            {"id": "N03", "kind": "delete_driver", "driver": "units",
             "expected": "ModelRegistryError", "why": "required driver missing"},
            {"id": "N04", "kind": "add_driver", "driver": "unknown_driver", "value": [1],
             "expected": "ModelRegistryError", "why": "unknown driver"},
            {"id": "N05a", "kind": "set_years", "value": [], "expected": "ModelRegistryError",
             "why": "empty fiscal-year list"},
            {"id": "N05b", "kind": "set_years", "value": {"__bool__first__": True},
             "expected": "ModelRegistryError", "why": "True is not a fiscal year"},
            {"id": "R7-TIMING", "kind": "set_driver", "driver": "timing_factor", "value": [1.5],
             "expected": "ModelRegistryError", "why": "timing_factor is a ratio and must stay in [0,1]"},
            {"id": "R8-NET-NEG", "kind": "set_driver", "driver": "other_revenue", "value": [-400],
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
    print("defaults expected:", [str(v) for v in defaults_expected])
    print("BYD pv unit price:", d["mapping_1_same_table"]["unit_revenue_pv_cny_derived"],
          "residual:", d["mapping_1_same_table"]["residual_cny"])
    print("BYD scope gap cny:", d["mapping_2_scope_residual"]["gap_cny"],
          "pct:", d["mapping_2_scope_residual"]["gap_pct_of_segment"])
    print("negative case count:", len(cases_doc["cases"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
