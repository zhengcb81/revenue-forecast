"""Independent oracle generator for the M21-M24 card batch (stdlib only).

Writes, into <out-root>/evidence/<card>/ :
  input.json              frozen positive / continuity_positive / defaults inputs
  cases.json              negative cases (card-specific + N01-N05 + continuity break)
  oracle.json             frozen expected values + tolerances + observation expectations
  oracle_selfcheck.json   proof that this file does not import the product

Hard independence rule: this file must NEVER import model_registry, model_extensions
or any other product module. Every number below is plain arithmetic derived from the
card text (see oracle.md), never from the product under test.

The card is selected with --card; the same byte-identical generator serves all four
attempts and is copied into each attempt's scripts/ directory.

Run (attempt-local interpreter):
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/oracle_M21.py \
      --card M21 --out-root <attempt>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal, getcontext

getcontext().prec = 50

TOL = Decimal("1e-9")
PRODUCT_MODULE_TOKENS = ("model_registry", "model_extensions", "revenue_core", "revenue_forecast")


def tol_for(expected: Decimal) -> Decimal:
    return TOL * max(Decimal(1), abs(expected))


def expected_block(years, values, formulas):
    assert len(years) == len(values) == len(formulas), "length mismatch"
    return {
        "years": list(years),
        "expected": [str(v) for v in values],
        "expected_float": [float(v) for v in values],
        "tolerances": [float(tol_for(v)) for v in values],
        "hand_work": formulas,
    }


WHY = {
    "NEG-CARD": "card-specific negative (oracle.md section 5)",
    "N01a": "common negative N01a: bool is not a numeric driver value",
    "N01b": "common negative N01b: non-finite value nan",
    "N01c": "common negative N01c: non-finite value inf",
    "N01d": "common negative N01d: non-finite value -inf",
    "N02": "common negative N02: first required driver array is empty, so its length != len(years)",
    "N03": "common negative N03: first required driver deleted (missing required field)",
    "N04": "common negative N04: unknown_driver added (unsupported driver)",
    "N05a": "common negative N05a: years = [] (fiscal-year domain)",
    "N05b": "common negative N05b: first year replaced by True (True is not a fiscal year)",
    "CONT-BREAK": "continuity break for this card (oracle.md section 4)",
    "CONT-BREAK-CROSSYEAR": "cross-year anchoring break added at the request of the "
                            "independent review: only the FY2028 opening/closing ARR move, "
                            "so FY2027 still balances and the continuity guard must fire",
    "CARD-NEG-GAP": "card-listed second negative kept as a NON-GATING observation so that NEG-CARD "
                    "exercises the value-domain guard on a 2-year path (oracle.md section 6)",
}

# Frozen MESSAGE requirement per case id, when a type-only assertion would be too weak.
# The runner fails a case whose ModelRegistryError message does not contain this substring.
# Deliberately MINIMAL, so that the frozen oracle body changes as little as possible:
#   * M22 / M23 NEG-CARD - required by review item P2-2: the card's literal 1-element-list
#     replacement must reach the VALUE-domain guard, not the length guard.
#   * M24 NEG-CARD       - the value/bridge guard, not the length guard.
#   * M24 CONT-BREAK-CROSSYEAR - required by review item P2-3: the CROSS-YEAR anchoring
#     guard, not the FY2027 balance guard.
# Not used for CONT-BREAK on M21 / M22 / M23 / M24, because for M22/M23 no guard
# substitution is possible (only the fiscal-year guard can raise there), on M21 the
# continuity guard is the only reachable refusal on a 2-year path, and on M24 the
# cross-year requirement is already frozen on the dedicated CROSSYEAR case.
EXPECT_MESSAGE_CONTAINS = {
    "NEG-CARD": {
        "M22": "must be between 0.0 and 1.0: FY2027",
        "M23": "must be between 0.0 and 1.0: FY2027",
        "M24": "stock-flow balance failed: FY2027",
    },
    "CONT-BREAK-CROSSYEAR": {
        "M24": "continuity failed: FY2028",
    },
}


def case_tuple(case_id, kind, base_input, driver=None, index=None, value=None):
    return (case_id, kind, driver, index, value, base_input)


def common_cases(first_required_driver, card_negative, continuity_break):
    """Build the frozen NEG-CARD + N01-N05 + CONT-BREAK list."""
    card_kind, card_base, card_driver, card_index, card_value = card_negative
    cont_kind, cont_driver, cont_index, cont_value = continuity_break
    return [
        case_tuple("NEG-CARD", card_kind, card_base, card_driver, card_index, card_value),
        case_tuple("N01a", "set_driver_element", "positive", first_required_driver, 0,
                   {"__bool__": True}),
        case_tuple("N01b", "set_driver_element", "positive", first_required_driver, 0,
                   {"__float__": "nan"}),
        case_tuple("N01c", "set_driver_element", "positive", first_required_driver, 0,
                   {"__float__": "inf"}),
        case_tuple("N01d", "set_driver_element", "positive", first_required_driver, 0,
                   {"__float__": "-inf"}),
        case_tuple("N02", "set_driver", "positive", first_required_driver, None, []),
        case_tuple("N03", "delete_driver", "positive", first_required_driver),
        case_tuple("N04", "add_driver", "positive", "unknown_driver", None, [1]),
        case_tuple("N05a", "set_years", "positive", None, None, []),
        case_tuple("N05b", "set_years", "positive", None, None, {"__bool__first__": True}),
        case_tuple("CONT-BREAK", cont_kind, "continuity_positive", cont_driver, cont_index,
                   cont_value),
    ]


# --------------------------------------------------------------------------
# M21 delivery_pipeline
# --------------------------------------------------------------------------
def m21():
    def dp(deliveries, unit_revenue, timing, other, opening, new, canc, closing):
        revenue = (Decimal(deliveries) * Decimal(unit_revenue) * Decimal(timing)
                   + Decimal(other))
        bridge = (Decimal(opening) + Decimal(new) - Decimal(canc) - Decimal(deliveries))
        return revenue, ("%s x %s x %s + %s" % (deliveries, unit_revenue, timing, other)), bridge

    r1, f1, b1 = dp(40, 3, 1, 2, 50, 30, 5, 35)
    assert b1 == Decimal(35), "hand bridge must close at 35"
    c1 = dp(40, 3, 1, 2, 50, 30, 5, 35)
    c2 = dp(0, 3, 1, 0, 35, 0, 0, 35)
    d1 = dp(40, 3, 1, 0, 50, 30, 5, 35)
    obs_timing = dp(40, 3, "1.5", 2, 50, 30, 5, 35)
    return {
        "model_id": "delivery_pipeline",
        "first_required_driver": "opening_orders",
        "positive": expected_block([2027], [r1], [f1]),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "delivery_pipeline",
                "base_revenue": 0,
                "drivers": {"opening_orders": [50], "new_orders": [30], "cancellations": [5],
                            "deliveries": [40], "ending_orders": [35], "unit_revenue": [3],
                            "timing_factor": [1], "other_revenue": [2]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "delivery_pipeline",
                "base_revenue": 0,
                "drivers": {"opening_orders": [50, 35], "new_orders": [30, 0],
                            "cancellations": [5, 0], "deliveries": [40, 0],
                            "ending_orders": [35, 35], "unit_revenue": [3, 3],
                            "timing_factor": [1, 1], "other_revenue": [2, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "delivery_pipeline",
                "base_revenue": 0,
                "drivers": {"opening_orders": [50], "new_orders": [30], "cancellations": [5],
                            "deliveries": [40], "ending_orders": [35], "unit_revenue": [3]},
                "years": [2027],
            },
            # Dedicated 2-year base for NEG-CARD so that index 1 exists and the
            # ratio-domain guard (not a length guard) is the reason for rejection.
            "card_neg": {
                "model_id": "delivery_pipeline",
                "base_revenue": 0,
                "drivers": {"opening_orders": [50, 35], "new_orders": [30, 0],
                            "cancellations": [5, 0], "deliveries": [40, 0],
                            "ending_orders": [35, 35], "unit_revenue": [3, 3],
                            "timing_factor": [1, 1], "other_revenue": [2, 0]},
                "years": [2027, 2028],
            },
        },
        "cases": common_cases(
            "opening_orders",
            ("set_driver_element", "card_neg", "timing_factor", 1, {"__float__": 1.5}),
            ("set_driver_multi", None, None,
             {"opening_orders": [50, 36], "ending_orders": [35, 36]}),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the delivery bridge ignores base_revenue at this entry point; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver_multi",
             "value": {"timing_factor": [1], "other_revenue": [0]}, "base_input": "defaults",
             "compare_to": "defaults", "expect_equal": True,
             "why": "explicit 1/0 equals the omitted default; makes the documented default falsifiable"},
            {"id": "OBS-CARD-NEG-ENDING", "kind": "set_driver",
             "driver": "ending_orders", "value": [36], "base_input": "positive",
             "expect_equal": None,
             "why": "card-listed negative, kept as a NON-GATING observation on the 1-year path; the frozen gating cases are NEG-CARD (value domain) and CONT-BREAK (bridge/continuity)"},
        ],
        "hand_notes": {
            "positive": "50 + 30 - 5 - 40 = 35 (bridge closes); revenue 40 x 3 x 1 + 2 = 122",
            "continuity_fy2028": "opening 35 = FY2027 closing; 35 + 0 - 0 - 0 = 35 closes; revenue 0 x 3 x 1 + 0 = 0",
            "defaults": "timing_factor omitted -> 1; other_revenue omitted -> 0; 40 x 3 x 1 + 0 = 120",
        },
        "probe_expected": {"OBS-CARD-NEG-ENDING": "ModelRegistryError (bridge: 35 + 30 - 5 - 40 != 36)"},
    }


# --------------------------------------------------------------------------
# M22 milestone_royalty
# --------------------------------------------------------------------------
def m22():
    def mr(sales, rate, milestone, service):
        return (Decimal(sales) * Decimal(rate) + Decimal(milestone) + Decimal(service),
                "%s x %s + %s + %s" % (sales, rate, milestone, service))

    r1 = mr(500, "0.08", 12, 3)
    c1 = mr(500, "0.08", 12, 3)
    c2 = mr(0, "0.08", 4, 0)
    d1 = mr(500, "0.08", 0, 0)
    return {
        "model_id": "milestone_royalty",
        "first_required_driver": "eligible_sales",
        "positive": expected_block([2027], [r1[0]], [r1[1]]),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "milestone_royalty",
                "base_revenue": 0,
                "drivers": {"eligible_sales": [500], "royalty_rate": [0.08],
                            "milestone_revenue": [12], "service_revenue": [3]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "milestone_royalty",
                "base_revenue": 0,
                "drivers": {"eligible_sales": [500, 0], "royalty_rate": [0.08, 0.08],
                            "milestone_revenue": [12, 4], "service_revenue": [3, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "milestone_royalty",
                "base_revenue": 0,
                "drivers": {"eligible_sales": [500], "royalty_rate": [0.08]},
                "years": [2027],
            },
        },
        # NEG-CARD is the CARD'S LITERAL negative: replace the whole `royalty_rate`
        # driver by the 1-element list [1.01] (card_M22.md L38). The list form is what
        # reaches the VALUE-domain guard; a scalar would be refused earlier by the
        # length guard. Frozen requirement: the refusal MESSAGE must contain
        # "must be between 0.0 and 1.0: FY2027" (see cases.json expect_message_contains).
        "cases": common_cases(
            "eligible_sales",
            ("set_driver", "positive", "royalty_rate", None, [1.01]),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the royalty calculation ignores base_revenue at this entry point; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver_multi",
             "value": {"milestone_revenue": [0], "service_revenue": [0]},
             "base_input": "defaults", "compare_to": "defaults", "expect_equal": True,
             "why": "explicit 0/0 equals the omitted default; makes the documented default falsifiable"},
        ],
        "hand_notes": {
            "positive": "500 x 0.08 = 40; 40 + 12 + 3 = 55",
            "continuity_fy2028": "0 x 0.08 + 4 + 0 = 4 (no eligible sales, milestone only)",
            "defaults": "milestone_revenue omitted -> 0; service_revenue omitted -> 0; 500 x 0.08 = 40",
        },
        "probe_expected": {},
    }


# --------------------------------------------------------------------------
# M23 insurance_service
# --------------------------------------------------------------------------
def m23():
    def ins(units, per_unit, timing, other):
        return (Decimal(units) * Decimal(per_unit) * Decimal(timing) + Decimal(other),
                "%s x %s x %s + %s" % (units, per_unit, timing, other))

    r1 = ins(100, 2, "0.5", 10)
    c1 = ins(100, 2, "0.5", 10)
    c2 = ins(120, "2.5", 1, 0)
    d1 = ins(100, 2, 1, 0)
    return {
        "model_id": "insurance_service",
        "first_required_driver": "coverage_units",
        "positive": expected_block([2027], [r1[0]], [r1[1]]),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "insurance_service",
                "base_revenue": 0,
                "drivers": {"coverage_units": [100], "revenue_per_coverage_unit": [2],
                            "timing_factor": [0.5], "other_revenue": [10]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "insurance_service",
                "base_revenue": 0,
                "drivers": {"coverage_units": [100, 120], "revenue_per_coverage_unit": [2, 2.5],
                            "timing_factor": [0.5, 1], "other_revenue": [10, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "insurance_service",
                "base_revenue": 0,
                "drivers": {"coverage_units": [100], "revenue_per_coverage_unit": [2]},
                "years": [2027],
            },
        },
        # NEG-CARD is the CARD'S LITERAL negative: replace the whole `timing_factor`
        # driver by the 1-element list [1.1] (card_M23.md L38). The list form is what
        # reaches the VALUE-domain guard; a scalar would be refused earlier by the
        # length guard. Frozen requirement: the refusal MESSAGE must contain
        # "must be between 0.0 and 1.0: FY2027" (see cases.json expect_message_contains).
        "cases": common_cases(
            "coverage_units",
            ("set_driver", "positive", "timing_factor", None, [1.1]),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the coverage-unit calculation ignores base_revenue at this entry point; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver_multi",
             "value": {"timing_factor": [1], "other_revenue": [0]}, "base_input": "defaults",
             "compare_to": "defaults", "expect_equal": True,
             "why": "explicit 1/0 equals the omitted default; makes the documented default falsifiable"},
            {"id": "OBS-TIMING-BOUND-11", "kind": "set_driver", "driver": "timing_factor",
             "value": [1.1, 0.5], "base_input": "continuity_positive", "expect_equal": None,
             "why": "records whether timing_factor = 1.1 on a 2-year path is refused by the VALUE-domain guard rather than by a length guard; the frozen gating case NEG-CARD is on the 1-year card input where no index 1 exists; NO expectation and NO verdict is asserted"},
        ],
        "hand_notes": {
            "positive": "100 x 2 = 200; 200 x 0.5 = 100; 100 + 10 = 110",
            "continuity_fy2028": "120 x 2.5 = 300; 300 x 1 = 300; 300 + 0 = 300",
            "defaults": "timing_factor omitted -> 1; other_revenue omitted -> 0; 100 x 2 x 1 = 200",
        },
        "probe_expected": {},
    }


# --------------------------------------------------------------------------
# M24 subscription_arr_bridge
# --------------------------------------------------------------------------
def m24():
    def arr(opening, grr, expansion, new_arr, closing, lost_frac, exp_frac, new_frac, usage):
        opening, grr = Decimal(opening), Decimal(grr)
        lost = opening * (Decimal(1) - grr)
        expected_closing = opening - lost + Decimal(expansion) + Decimal(new_arr)
        revenue = (opening
                   - lost * Decimal(lost_frac)
                   + Decimal(expansion) * Decimal(exp_frac)
                   + Decimal(new_arr) * Decimal(new_frac)
                   + Decimal(usage))
        formula = ("%s - %s*(1-%s)*%s + %s*%s + %s*%s + %s"
                   % (opening, opening, grr, lost_frac, expansion, exp_frac, new_arr, new_frac, usage))
        return revenue, formula, lost, expected_closing

    r1 = arr(200, "0.9", 30, 40, 250, "0.75", "0.5", "0.25", 5)
    assert r1[3] == Decimal(250), "hand bridge must close at 250"
    c1 = arr(200, "0.9", 30, 40, 250, "0.75", "0.5", "0.25", 5)
    c2 = arr(250, 1, 0, 0, 250, "0.75", "0.5", "0.25", 0)
    d1 = arr(200, "0.9", 30, 40, 250, "0.75", "0.5", "0.25", 0)
    return {
        "model_id": "subscription_arr_bridge",
        "first_required_driver": "opening_arr",
        "positive": expected_block([2027], [r1[0]], [r1[1]]),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "subscription_arr_bridge",
                "base_revenue": 0,
                "drivers": {"opening_arr": [200], "gross_retention_rate": [0.9],
                            "expansion_arr": [30], "new_arr": [40], "closing_arr": [250],
                            "lost_arr_revenue_fraction": [0.75],
                            "expansion_revenue_fraction": [0.5],
                            "new_arr_revenue_fraction": [0.25], "usage_revenue": [5]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "subscription_arr_bridge",
                "base_revenue": 0,
                "drivers": {"opening_arr": [200, 250], "gross_retention_rate": [0.9, 1],
                            "expansion_arr": [30, 0], "new_arr": [40, 0],
                            "closing_arr": [250, 250],
                            "lost_arr_revenue_fraction": [0.75, 0.75],
                            "expansion_revenue_fraction": [0.5, 0.5],
                            "new_arr_revenue_fraction": [0.25, 0.25],
                            "usage_revenue": [5, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "subscription_arr_bridge",
                "base_revenue": 0,
                "drivers": {"opening_arr": [200], "gross_retention_rate": [0.9],
                            "expansion_arr": [30], "new_arr": [40], "closing_arr": [250],
                            "lost_arr_revenue_fraction": [0.75],
                            "expansion_revenue_fraction": [0.5],
                            "new_arr_revenue_fraction": [0.25]},
                "years": [2027],
            },
        },
        # CONT-BREAK is the CARD'S LITERAL patch (card_M24.md L115-124) and, as the card
        # itself notes, its numbers also move FY2027's closing, so the FY2027 stock-flow
        # BALANCE guard fires first. CONT-BREAK-CROSSYEAR is the additional case the
        # independent review required: ONLY year-2 opening/closing move (251), so FY2027
        # still balances on its own and the CROSS-YEAR ANCHORING guard is the one that
        # must fire. Frozen requirement for that case: the refusal MESSAGE must contain
        # "continuity failed: FY2028".
        "cases": common_cases(
            "opening_arr",
            ("set_driver", "positive", "closing_arr", None, [251]),
            ("set_driver_multi", None, None,
             {"opening_arr": [200, 251], "closing_arr": [250, 251]}),
        ) + [case_tuple("CONT-BREAK-CROSSYEAR", "set_driver_multi", "continuity_positive",
                        None, None,
                        {"opening_arr": [200, 251], "closing_arr": [250, 251]})],
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the ARR bridge ignores base_revenue at this entry point; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver", "driver": "usage_revenue",
             "value": [0], "base_input": "defaults", "compare_to": "defaults",
             "expect_equal": True,
             "why": "explicit 0 equals the omitted optional usage_revenue; makes the documented default falsifiable"},
            {"id": "OBS-GRR-ONE-SECOND-YEAR", "kind": "input_replay", "input": "continuity_positive",
             "compare_to": "continuity_positive", "expect_equal": True,
             "why": "records whether gross_retention_rate = 1 on the FY2028 slot is accepted (the retained-ARR guard: opening_arr * grr == 0 and expansion_arr > 0); NO expectation and NO verdict is asserted"},
            {"id": "OBS-BRIDGE-TOL-1E-7", "kind": "set_driver_element", "driver": "closing_arr",
             "index": 0, "value": {"__float__": 250.0000001}, "base_input": "positive",
             "expect_equal": None,
             "why": "effective-resolution probe required by the review (P3-2): the bridge compares with math.isclose(rel_tol=1e-9, abs_tol=1e-9), whose effective absolute tolerance at |closing_arr| = 250 is about 2.5e-7, so +1e-7 is expected to be INSIDE tolerance and the call to return a value; NO verdict is asserted, the observed outcome is recorded"},
            {"id": "OBS-BRIDGE-TOL-1E-6", "kind": "set_driver_element", "driver": "closing_arr",
             "index": 0, "value": {"__float__": 250.000001}, "base_input": "positive",
             "expect_equal": None,
             "why": "second effective-resolution probe (P3-2): +1e-6 is expected to be OUTSIDE the ~2.5e-7 effective tolerance and be refused with a stock-flow balance ModelRegistryError; NO verdict is asserted, the observed outcome is recorded"},
        ],
        "hand_notes": {
            "positive": "lost = 200 x (1 - 0.9) = 20; closing = 200 - 20 + 30 + 40 = 250 (bridge closes); revenue = 200 - 20 x 0.75 + 30 x 0.5 + 40 x 0.25 + 5 = 200 - 15 + 15 + 10 + 5 = 215",
            "continuity_fy2028": "grr = 1 -> lost = 0; closing = 250 + 0 + 0 = 250; revenue = 250 - 0 + 0 + 0 + 0 = 250",
            "defaults": "usage_revenue omitted -> 0; 200 - 15 + 15 + 10 + 0 = 210",
            "continuity_negative_note": "the card's CONT patch also moves FY2027 closing_arr to 251, so the FY2027 balance check fires before the FY2028 continuity check; both are ModelRegistryError, the frozen requirement is the exception TYPE",
        },
        "probe_expected": {},
    }


BUILDERS = {"M21": m21, "M22": m22, "M23": m23, "M24": m24}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(BUILDERS))
    parser.add_argument("--out-root", required=True)
    args = parser.parse_args()

    card = args.card
    data = BUILDERS[card]()
    target = os.path.join(args.out_root, "evidence", card)
    os.makedirs(target, exist_ok=True)

    cases = []
    for entry in data["cases"]:
        if len(entry) != 6:
            raise ValueError("case tuples must have 6 elements: " + repr(entry))
        case_id, kind, driver, index, value, base_input = entry
        case = {"id": case_id, "kind": kind, "expected": "ModelRegistryError",
                "base_input": base_input, "why": WHY[case_id], "driver": driver}
        if case_id in EXPECT_MESSAGE_CONTAINS:
            requirement = EXPECT_MESSAGE_CONTAINS[case_id].get(card)
            if requirement:
                case["expect_message_contains"] = requirement
                case["expect_message_basis"] = (
                    "the type-only assertion is too weak for this case: a length/lookup guard "
                    "could raise the same exception class for the wrong reason, so the refusal "
                    "MESSAGE is frozen too and the runner fails the case if the message does "
                    "not contain this substring")
        if kind == "set_driver_element":
            case["index"] = index
            case["value"] = value
        elif kind in ("set_driver", "add_driver", "set_years", "set_driver_multi"):
            case["value"] = value
        elif kind == "delete_driver":
            pass
        else:
            raise ValueError("unknown case kind: " + kind)
        cases.append(case)

    input_doc = dict(data["input"])
    input_doc["card_id"] = card

    cases_doc = {
        "card_id": card,
        "first_required_driver": data["first_required_driver"],
        "independent_deepcopy_per_case": True,
        "continuity_first_positive": "continuity_positive",
        "cases": cases,
        "extra_observations": data["observations"],
        "probe_expected": data.get("probe_expected", {}),
    }

    oracle = {
        "card_id": card,
        "model_id": data["model_id"],
        "generated_by": "scripts/oracle_%s.py (stdlib only, no product import)" % card,
        "positive": data["positive"],
        "continuity_positive": data["continuity_positive"],
        "defaults": data["defaults"],
        "defaults_expected_float": data["defaults"]["expected_float"],
        "observation_expected": {},
        "hand_notes": data.get("hand_notes", {}),
        "negative_count": len(cases),
        "negative_ids": [c["id"] for c in cases],
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
    }

    def dump(name, doc):
        path = os.path.join(target, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, ensure_ascii=False, indent=1)
        return path

    dump("input.json", input_doc)
    dump("cases.json", cases_doc)
    dump("oracle.json", oracle)

    with open(__file__, "rb") as handle:
        script_sha = hashlib.sha256(handle.read()).hexdigest()
    with open(__file__, "r", encoding="utf-8") as handle:
        own_text = handle.read()
    import_lines = [line.strip() for line in own_text.splitlines()
                    if line.startswith("import ") or line.startswith("from ")]
    selfcheck = {
        "script": os.path.abspath(__file__),
        "script_sha256": script_sha,
        "rule": "the oracle generator must not import the product under test",
        "forbidden_tokens": list(PRODUCT_MODULE_TOKENS),
        "import_lines": import_lines,
        "product_import_present": any(
            token in line for token in PRODUCT_MODULE_TOKENS for line in import_lines),
    }
    dump("oracle_selfcheck.json", selfcheck)

    print("card", card, "model", data["model_id"])
    print("positive expected", data["positive"]["expected"],
          "tolerances", data["positive"]["tolerances"])
    print("continuity expected", data["continuity_positive"]["expected"])
    print("defaults expected", data["defaults"]["expected"])
    print("negative cases", len(cases), [c["id"] for c in cases])
    print("oracle_selfcheck product_import_present =", selfcheck["product_import_present"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
