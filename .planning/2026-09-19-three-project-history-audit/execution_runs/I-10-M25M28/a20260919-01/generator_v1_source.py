"""Independent frozen-evidence generator for cards M25, M26, M27, M28 (stdlib only).

Writes, for one card, into <out-root>/evidence/<card>/:
  input.json             frozen positive / continuity_positive / defaults inputs
  cases.json             negative cases (NEG-CARD + N01a-d + N02..N05b + CONT-BREAK)
  oracle.json            frozen expected values + tolerances + observation expectations
  oracle_selfcheck.json  proof that this file does not import the product under test

Hard independence rule
----------------------
This file must NEVER import model_registry, model_extensions or any product module.
Every expected number is plain arithmetic derived from the card text and from the
registry formula STRING quoted in card_Mxx.md (see oracle.md), never from a call to
the product.  The registry metadata string is transcribed from the card; the runner
separately prints the registry's own formula string so a mismatch is visible rather
than hidden.

Run:
  python -X utf8 -B scripts/oracle_M25_M28.py --card M25 --out-root <attempt_root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from decimal import Decimal, getcontext

getcontext().prec = 50

TOL = Decimal("1e-9")
PRODUCT_MODULE_TOKENS = ("model_registry", "model_extensions", "revenue_core", "revenue_forecast")

# Frozen refusal rationale. Sources: card_Mxx.md, common_model_cards.md L24-30,
# and this card's oracle.md section 5.
WHY = {
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
    "NEG-CARD": "card-specific negative (oracle.md sections 5 and 8)",
}


def tol_for(expected: Decimal) -> Decimal:
    return TOL * max(Decimal(1), abs(expected))


def expected_block(years, values, formulas):
    assert len(years) == len(values) == len(formulas), "length mismatch"
    return {
        "years": list(years),
        "expected": [q(v) for v in values],
        "expected_float": [float(v) for v in values],
        "tolerances": [float(tol_for(v)) for v in values],
        "hand_work": formulas,
    }


def d(value) -> Decimal:
    return Decimal(str(value))


def q(value: Decimal) -> str:
    """Present a hand-computed Decimal without trailing zeros (exact, no rounding)."""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if text not in ("", "-") else "0"


def case_tuple(case_id, kind, base_input, driver=None, index=None, value=None):
    return (case_id, kind, driver, index, value, base_input)


def common_cases(first_required_driver, card_negative, continuity_break):
    """Build the frozen NEG-CARD + N01-N05 + CONT-BREAK list (11 cases)."""
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
# M25 installed_base_aftermarket
# --------------------------------------------------------------------------
def m25():
    def inst(opening, new, retired, new_frac, ret_lost, attach, per_unit):
        exposure = (d(opening) + d(new) * d(new_frac) - d(retired) * d(ret_lost))
        return (
            exposure * d(attach) * d(per_unit),
            "(%s + %s*%s - %s*%s) * %s * %s" % (opening, new, new_frac, retired, ret_lost,
                                                attach, per_unit),
        )

    v, f = zip(*[inst(200, 40, 20, "0.25", "0.5", "0.5", 3)])
    c1 = inst(200, 40, 20, "0.25", "0.5", "0.5", 3)
    c2 = inst(220, 0, 0, "0.25", "0.5", "0.5", 3)
    # defaults case: M25 has optional = () and defaults = {}, so no optional driver can be
    # omitted. The runnable zero-identity case records that the rowwise calculator starts from
    # zero for every year and that "zero" is an explicit input, not a library-supplied default.
    d1 = inst(0, 0, 0, 0, 0, 0, 0)
    return {
        "model_id": "installed_base_aftermarket",
        "first_required_driver": "opening_installed_units",
        "continuity_case": True,
        "continuity_note": "two-year continuity example taken verbatim from card_M25.md; the negative_patch "
                           "keeps both years individually balanced (220+0-0=220 and 221+0-0=221) and breaks "
                           "only the year-over-year opening=prior closing identity.",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "installed_base_aftermarket",
                "base_revenue": 0,
                "drivers": {"opening_installed_units": [200], "new_installed_units": [40],
                            "retired_units": [20], "closing_installed_units": [220],
                            "new_unit_revenue_fraction": [0.25],
                            "retirement_lost_fraction": [0.5], "attach_rate": [0.5],
                            "annual_revenue_per_attached_unit": [3]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "installed_base_aftermarket",
                "base_revenue": 0,
                "drivers": {"opening_installed_units": [200, 220], "new_installed_units": [40, 0],
                            "retired_units": [20, 0], "closing_installed_units": [220, 220],
                            "new_unit_revenue_fraction": [0.25, 0.25],
                            "retirement_lost_fraction": [0.5, 0.5], "attach_rate": [0.5, 0.5],
                            "annual_revenue_per_attached_unit": [3, 3]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "installed_base_aftermarket",
                "base_revenue": 0,
                "drivers": {"opening_installed_units": [0], "new_installed_units": [0],
                            "retired_units": [0], "closing_installed_units": [0],
                            "new_unit_revenue_fraction": [0], "retirement_lost_fraction": [0],
                            "attach_rate": [0], "annual_revenue_per_attached_unit": [0]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "opening_installed_units",
            ("set_driver_multi", "positive", None, None,
             {"retired_units": [201], "closing_installed_units": [39]}),
            ("set_driver_multi", None, None,
             {"opening_installed_units": [200, 221], "closing_installed_units": [220, 221]}),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "rowwise calculator discards base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-ZERO", "kind": "input_replay", "input": "defaults",
             "compare_to": None, "expect_equal": None,
             "why": "all eight required drivers explicitly zero, no optional driver exists; the mechanism is the rowwise calculator, which starts from zero for every year"},
        ],
        "defaults_declared_expectation": {
            "driver": None,
            "declared_default_present": None,
            "why": "M25 has optional = () and defaults = {}, so there is no declared optional default to check"},
    }


# --------------------------------------------------------------------------
# M26 store_cohorts
# --------------------------------------------------------------------------
def m26():
    def st(opening, new, closed, new_frac, close_lost, productivity, per_mature):
        mature = d(opening) - d(closed) * d(close_lost)
        newxp = d(new) * d(new_frac) * d(productivity)
        return (
            (mature + newxp) * d(per_mature),
            "(%s - %s*%s + %s*%s*%s) * %s" % (opening, closed, close_lost, new, new_frac,
                                              productivity, per_mature),
        )

    v, f = zip(*[st(20, 5, 2, "0.4", "0.5", "0.75", 10)])
    c1 = st(20, 5, 2, "0.4", "0.5", "0.75", 10)
    c2 = st(23, 0, 0, "0.4", "0.5", "0.75", 10)
    # defaults case: optional = () and defaults = {} -> the zero-identity case.
    d1 = st(0, 0, 0, 0, 0, 0, 0)
    return {
        "model_id": "store_cohorts",
        "first_required_driver": "opening_stores",
        "continuity_case": True,
        "continuity_note": "two-year continuity example taken verbatim from card_M26.md; the negative_patch "
                           "keeps both years individually balanced (20+5-2=23 and 24+0-0=24) and breaks only "
                           "the year-over-year opening=prior closing identity.",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "store_cohorts",
                "base_revenue": 0,
                "drivers": {"opening_stores": [20], "new_stores": [5], "closed_stores": [2],
                            "closing_stores": [23], "new_store_revenue_fraction": [0.4],
                            "closure_lost_fraction": [0.5], "new_store_productivity": [0.75],
                            "annual_revenue_per_mature_store": [10]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "store_cohorts",
                "base_revenue": 0,
                "drivers": {"opening_stores": [20, 23], "new_stores": [5, 0],
                            "closed_stores": [2, 0], "closing_stores": [23, 23],
                            "new_store_revenue_fraction": [0.4, 0.4],
                            "closure_lost_fraction": [0.5, 0.5],
                            "new_store_productivity": [0.75, 0.75],
                            "annual_revenue_per_mature_store": [10, 10]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "store_cohorts",
                "base_revenue": 0,
                "drivers": {"opening_stores": [0], "new_stores": [0], "closed_stores": [0],
                            "closing_stores": [0], "new_store_revenue_fraction": [0],
                            "closure_lost_fraction": [0], "new_store_productivity": [0],
                            "annual_revenue_per_mature_store": [0]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "opening_stores",
            ("set_driver", "positive", "closing_stores", None, {"__float__": 24}),
            ("set_driver_multi", None, None,
             {"opening_stores": [20, 24], "closing_stores": [23, 24]}),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "rowwise calculator discards base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-PRODUCTIVITY-BOUND", "kind": "set_driver_element",
             "driver": "new_store_productivity", "index": 0, "value": {"__float__": 1.5},
             "base_input": "positive", "expect_equal": None,
             "why": "card_M26.md L8 says new-store productivity may exceed one; the registry declares "
                    "store_cohorts.new_store_productivity = (0.0, inf) while this driver's dimension is "
                    "ratio. The probe records black-box behaviour with NO expectation and NO verdict asserted."},
        ],
        "defaults_declared_expectation": {
            "driver": None,
            "declared_default_present": None,
            "why": "M26 has optional = () and defaults = {}, so there is no declared optional default to check"},
    }


# --------------------------------------------------------------------------
# M27 renewable_generation
# --------------------------------------------------------------------------
def m27():
    def rg(mw, hours, cf, curtail, contracted, contract_price, merchant_price, other):
        delivered = d(mw) * d(hours) * d(cf) * (d(1) - d(curtail))
        blended = d(contracted) * d(contract_price) + (d(1) - d(contracted)) * d(merchant_price)
        return (
            delivered * blended + d(other),
            "(%s*%s*%s*(1-%s)) * (%s*%s + (1-%s)*%s) + %s" % (mw, hours, cf, curtail, contracted,
                                                              contract_price, contracted,
                                                              merchant_price, other),
        )

    v, f = zip(*[rg(2, 8760, "0.5", 0, "0.5", 40, 20, 1200)])
    c1 = rg(2, 8760, "0.5", 0, "0.5", 40, 20, 1200)
    c2 = rg(5, 8760, "0.45", "0.1", "0.4", 42, 25, 0)
    # defaults case: other_revenue omitted -> the library fills 0.0 although the card
    # declares other_revenue default 0 (card_M27.md L9). Recorded as a design artefact.
    d1 = rg(2, 8760, "0.5", 0, "0.5", 40, 20, 0)
    e1 = rg(2, 8760, "0.5", 0, "0.5", 40, 20, 1200)
    return {
        "model_id": "renewable_generation",
        "first_required_driver": "average_commissioned_mw",
        "continuity_case": False,
        "continuity_note": "card_M27.md gives no two-year continuity example, and renewable_generation is "
                           "a per-year flow model with no opening/closing stock to bridge (no "
                           "EXTENSION_OPENING_BALANCES entry), so the applicable continuity check is the "
                           "cross-year fiscal-year continuity used for M05: a gap in years must be refused.",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "renewable_generation",
                "base_revenue": 0,
                "drivers": {"average_commissioned_mw": [2], "period_hours": [8760],
                            "pre_curtailment_capacity_factor": [0.5], "curtailment_rate": [0],
                            "contracted_share": [0.5], "contract_price_per_mwh": [40],
                            "merchant_price_per_mwh": [20], "other_revenue": [1200]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "renewable_generation",
                "base_revenue": 0,
                "drivers": {"average_commissioned_mw": [2, 5], "period_hours": [8760, 8760],
                            "pre_curtailment_capacity_factor": [0.5, 0.45],
                            "curtailment_rate": [0, 0.1], "contracted_share": [0.5, 0.4],
                            "contract_price_per_mwh": [40, 42],
                            "merchant_price_per_mwh": [20, 25], "other_revenue": [1200, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "renewable_generation",
                "base_revenue": 0,
                "drivers": {"average_commissioned_mw": [2], "period_hours": [8760],
                            "pre_curtailment_capacity_factor": [0.5], "curtailment_rate": [0],
                            "contracted_share": [0.5], "contract_price_per_mwh": [40],
                            "merchant_price_per_mwh": [20]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "average_commissioned_mw",
            ("set_driver", "positive", "period_hours", None, {"__float__": 0}),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "rowwise calculator discards base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-NEG-PRICE", "kind": "set_driver_element",
             "driver": "merchant_price_per_mwh", "index": 0, "value": {"__float__": -20},
             "base_input": "positive", "expect_equal": None,
             "why": "card_M27.md L54 says a negative power price may be entered; the registry declares "
                    "merchant_price_per_mwh = (None, None). The probe records whether the blended price "
                    "path accepts it, with NO expectation and NO verdict asserted on the price."},
        ],
        "defaults_declared_expectation": {
            "driver": "other_revenue",
            "declared_default_present": False,
            "why": "card_M27.md L9 declares other_revenue default 0, but the registry implementation "
                   "declares defaults = {} while keeping other_revenue optional; the library therefore "
                   "zero-fills it silently. This is the same silent-zero-fill class recorded as OQ-04 in "
                   "the accepted M05-M08 attempts, and it is checked here to keep the omission visible."},
        "extra_expected": {
            "OBS-EQUIV-DEFAULT": float(e1[0]),
        },
    }


# --------------------------------------------------------------------------
# M28 aum_fee_bridge
# --------------------------------------------------------------------------
def m28():
    def aum(opening, inflows, outflows, market, inflow_frac, outflow_lost, market_frac,
            fee_rate, perf):
        average = (d(opening) + d(inflows) * d(inflow_frac) - d(outflows) * d(outflow_lost)
                   + d(market) * d(market_frac))
        return (
            average * d(fee_rate) + d(perf),
            "(%s + %s*%s - %s*%s + %s*%s) * %s + %s" % (opening, inflows, inflow_frac, outflows,
                                                        outflow_lost, market, market_frac,
                                                        fee_rate, perf),
        )

    v, f = zip(*[aum(1000, 200, 100, -50, "0.25", "0.75", "0.5", "0.01", 2)])
    c1 = aum(1000, 200, 100, -50, "0.25", "0.75", "0.5", "0.01", 2)
    c2 = aum(1050, 0, 0, 0, "0.25", "0.75", "0.5", "0.01", 0)
    d1 = aum(1000, 200, 100, -50, "0.25", "0.75", "0.5", "0.01", 0)
    return {
        "model_id": "aum_fee_bridge",
        "first_required_driver": "opening_aum",
        "continuity_case": True,
        "continuity_note": "two-year continuity example taken verbatim from card_M28.md; the negative_patch "
                           "keeps both years individually balanced (1000+200-100-50=1050 and 1051+0-0+0=1051) "
                           "and breaks only the year-over-year opening=prior closing identity.",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "aum_fee_bridge",
                "base_revenue": 0,
                "drivers": {"opening_aum": [1000], "inflows": [200], "outflows": [100],
                            "market_change": [-50], "closing_aum": [1050],
                            "inflow_revenue_fraction": [0.25], "outflow_lost_fraction": [0.75],
                            "market_change_revenue_fraction": [0.5], "management_fee_rate": [0.01],
                            "recognized_performance_fees": [2]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "aum_fee_bridge",
                "base_revenue": 0,
                "drivers": {"opening_aum": [1000, 1050], "inflows": [200, 0], "outflows": [100, 0],
                            "market_change": [-50, 0], "closing_aum": [1050, 1050],
                            "inflow_revenue_fraction": [0.25, 0.25],
                            "outflow_lost_fraction": [0.75, 0.75],
                            "market_change_revenue_fraction": [0.5, 0.5],
                            "management_fee_rate": [0.01, 0.01],
                            "recognized_performance_fees": [2, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "aum_fee_bridge",
                "base_revenue": 0,
                "drivers": {"opening_aum": [1000], "inflows": [200], "outflows": [100],
                            "market_change": [-50], "closing_aum": [1050],
                            "inflow_revenue_fraction": [0.25], "outflow_lost_fraction": [0.75],
                            "market_change_revenue_fraction": [0.5], "management_fee_rate": [0.01]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "opening_aum",
            ("set_driver", "positive", "closing_aum", None, {"__float__": 1051}),
            ("set_driver_multi", None, None,
             {"opening_aum": [1000, 1051], "closing_aum": [1050, 1051]}),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "rowwise calculator discards base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-PERF-OMITTED", "kind": "input_replay", "input": "defaults",
             "compare_to": "positive", "expect_equal": False,
             "why": "omitting recognized_performance_fees changes the result, so the recognised performance "
                    "fee term is really used and its omission is not free"},
        ],
        "defaults_declared_expectation": {
            "driver": "recognized_performance_fees",
            "declared_default_present": False,
            "why": "card_M28.md L9 declares recognized_performance_fees default 0; the registry keeps the "
                   "driver optional with defaults = {}, so the library zero-fills it. Recorded to keep the "
                   "omission visible; the probe is non-gating."},
    }


BUILDERS = {"M25": m25, "M26": m26, "M27": m27, "M28": m28}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(BUILDERS))
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--emit-script", default=None,
                        help="write a byte-identical copy of this generator to this path")
    args = parser.parse_args()

    card = args.card
    if args.emit_script:
        with open(__file__, "rb") as handle:
            payload = handle.read()
        os.makedirs(os.path.dirname(os.path.abspath(args.emit_script)), exist_ok=True)
        with open(args.emit_script, "wb") as handle:
            handle.write(payload)
        print("emitted oracle script copy ->", args.emit_script,
              "sha256", hashlib.sha256(payload).hexdigest())

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
    }

    oracle = {
        "card_id": card,
        "model_id": data["model_id"],
        "generated_by": "scripts/oracle_M25_M28.py --card %s (stdlib only, no product import)" % card,
        "continuity_case": data.get("continuity_case", False),
        "continuity_note": data.get("continuity_note"),
        "positive": data["positive"],
        "continuity_positive": data["continuity_positive"],
        "defaults": data["defaults"],
        "defaults_expected_float": data["defaults"]["expected_float"],
        "defaults_declared_expectation": data.get("defaults_declared_expectation"),
        "observation_expected": {},
        "negative_count": len(cases),
        "negative_ids": [c["id"] for c in cases],
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
    }
    if card == "M27":
        oracle["extra_expected"] = data["extra_expected"]
        oracle["observation_expected"]["OBS-EQUIV-DEFAULT"] = data["defaults"]

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
    import_lines = [line.strip() for line in open(__file__, "r", encoding="utf-8").read().splitlines()
                    if line.startswith("import ") or line.startswith("from ")]
    selfcheck = {
        "script": os.path.abspath(__file__),
        "script_name": os.path.basename(__file__),
        "script_sha256": script_sha,
        "rule": "the oracle generator must not import the product under test",
        "forbidden_tokens": list(PRODUCT_MODULE_TOKENS),
        "import_lines": import_lines,
        "product_import_present": any(
            token in line for token in PRODUCT_MODULE_TOKENS for line in import_lines),
        "generated_evidence": {
            "evidence/%s/input.json" % card: hashlib.sha256(
                open(os.path.join(target, "input.json"), "rb").read()).hexdigest(),
            "evidence/%s/cases.json" % card: hashlib.sha256(
                open(os.path.join(target, "cases.json"), "rb").read()).hexdigest(),
            "evidence/%s/oracle.json" % card: hashlib.sha256(
                open(os.path.join(target, "oracle.json"), "rb").read()).hexdigest(),
        },
    }
    dump("oracle_selfcheck.json", selfcheck)

    print("card", card, "model", data["model_id"])
    print("positive expected", data["positive"]["expected"],
          "tolerances", data["positive"]["tolerances"])
    print("continuity expected", data["continuity_positive"]["expected"])
    print("defaults expected", data["defaults"]["expected"])
    print("negative cases", len(cases), [c["id"] for c in cases])
    print("oracle_selfcheck product_import_present =", selfcheck["product_import_present"])
    print("script_sha256 =", script_sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
