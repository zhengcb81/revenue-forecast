"""Independent oracle generator for cards M05-M08 (stdlib only).

Writes, for one card:
  <card>/input.json            frozen positive / continuity_positive / defaults inputs
  <card>/cases.json            negative cases (card-specific + N01-N05 + continuity break)
  <card>/oracle.json           frozen expected values + tolerances + observation expectations
  <card>/oracle_selfcheck.json proof that this file does not import the product

Hard independence rule: this file must NEVER import model_registry,
model_extensions or any product module. Every number below is plain arithmetic
derived from the card text (see oracle.md), never from the product.

Run:
  python -X utf8 -B scripts/oracle_M05.py --card M05 --out-root <attempt_root>
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


# Frozen refusal rationale. Sources: card_Mxx.md, common_model_cards.md L26-30,
# and this card's oracle.md section 8.
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
# M05 subscription
# --------------------------------------------------------------------------
def m05():
    def sub(customers, arpu, timing, usage):
        return (
            Decimal(customers) * Decimal(arpu) * Decimal(timing) + Decimal(usage),
            "%s x %s x %s + %s" % (customers, arpu, timing, usage),
        )

    v, f = zip(*[sub(200, 3, 1, 20)])
    c1 = sub(180, 3, 1, 10)
    c2 = sub(220, 4, 1, 0)
    d1 = sub(200, 3, 1, 0)
    return {
        "model_id": "subscription",
        "first_required_driver": "average_customers",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "subscription",
                "base_revenue": 0,
                "drivers": {"average_customers": [200], "revenue_per_customer": [3],
                            "timing_factor": [1], "usage_revenue": [20]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "subscription",
                "base_revenue": 0,
                "drivers": {"average_customers": [180, 220], "revenue_per_customer": [3, 4],
                            "timing_factor": [1, 1], "usage_revenue": [10, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "subscription",
                "base_revenue": 0,
                "drivers": {"average_customers": [200], "revenue_per_customer": [3]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "average_customers",
            ("set_driver", "positive", "timing_factor", None, {"__float__": 1.5}),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "rowwise calculator discards base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-ALT-CONV", "kind": "input_replay", "input": "positive",
             "compare_to": "positive", "expect_equal": True,
             "why": "replays the frozen card input so the runner's own reading is reproducible"},
        ],
    }


# --------------------------------------------------------------------------
# M06 usage_platform
# --------------------------------------------------------------------------
def m06():
    def up(activity, rate, fixed):
        return (
            Decimal(activity) * Decimal(rate) + Decimal(fixed),
            "%s x %s + %s" % (activity, rate, fixed),
        )

    v, f = zip(*[up(500, "0.04", 3)])
    c1 = up(500, "0.04", 3)
    c2 = up(800, "0.05", 4)
    d1 = up(500, "0.04", 0)
    return {
        "model_id": "usage_platform",
        "first_required_driver": "eligible_activity",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "usage_platform",
                "base_revenue": 0,
                "drivers": {"eligible_activity": [500], "monetization_rate": [0.04],
                            "fixed_revenue": [3]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "usage_platform",
                "base_revenue": 0,
                "drivers": {"eligible_activity": [500, 800], "monetization_rate": [0.04, 0.05],
                            "fixed_revenue": [3, 4]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "usage_platform",
                "base_revenue": 0,
                "drivers": {"eligible_activity": [500], "monetization_rate": [0.04]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "eligible_activity",
            ("set_driver_element", "positive", "eligible_activity", 0, {"__float__": -1}),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "rowwise calculator discards base_revenue; design observation only"},
            {"id": "OBS-RATE-GT1", "kind": "set_driver_element", "driver": "monetization_rate",
             "index": 0, "value": {"__float__": 1.5}, "base_input": "positive",
             "expect_equal": None,
             "why": "records empirically whether the implementation treats monetization_rate as a [0,1] probability; NO expectation and NO verdict is asserted"},
        ],
    }


# --------------------------------------------------------------------------
# M07 services
# --------------------------------------------------------------------------
def m07():
    def sv(cap, util, rate, timing, other):
        return (
            Decimal(cap) * Decimal(util) * Decimal(rate) * Decimal(timing) + Decimal(other),
            "%s x %s x %s x %s + %s" % (cap, util, rate, timing, other),
        )

    v, f = zip(*[sv(10000, "0.6", "0.02", 1, 2)])
    c1 = sv(10000, "0.6", "0.02", 1, 2)
    c2 = sv(12000, "0.55", "0.025", 1, 0)
    d1 = sv(10000, "0.6", "0.02", 1, 0)
    return {
        "model_id": "services",
        "first_required_driver": "billable_capacity",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "services",
                "base_revenue": 0,
                "drivers": {"billable_capacity": [10000], "utilization": [0.6],
                            "billing_rate": [0.02], "timing_factor": [1], "other_revenue": [2]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "services",
                "base_revenue": 0,
                "drivers": {"billable_capacity": [10000, 12000], "utilization": [0.6, 0.55],
                            "billing_rate": [0.02, 0.025], "timing_factor": [1, 1],
                            "other_revenue": [2, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "services",
                "base_revenue": 0,
                "drivers": {"billable_capacity": [10000], "utilization": [0.6],
                            "billing_rate": [0.02]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "billable_capacity",
            ("set_driver_element", "positive", "utilization", 0, {"__float__": 1.01}),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "rowwise calculator discards base_revenue; design observation only"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver", "driver": "timing_factor",
             "value": [1], "base_input": "defaults", "compare_to": "defaults",
             "expect_equal": True, "also_set_driver": {"other_revenue": [0]},
             "why": "explicit 1/0 equals the omitted default; makes the documented default falsifiable"},
        ],
    }


# --------------------------------------------------------------------------
# M08 project_backlog
# --------------------------------------------------------------------------
def m08():
    """Three distinguishable readings of the M08 revenue line.

    reading_a_card_arithmetic : the card's printed line "100+40-5-10-15-60=50":
        the magnitude 10 of contract_changes is subtracted, and backlog_remeasurements
        is subtracted. This is the ONLY reading that reproduces 50.
    reading_b_card_formula_string : the card's printed SYMBOLS
        "opening + bookings - cancellations - contract_changes + remeasurements - closing"
        with the frozen sign convention (a negative contract change INCREASES the backlog).
    reading_c_upstream_and_implementation : docs/buy_side_model_audit_2026-09-18.md:42 and
        scripts/model_registry.py:228 use "+ contract_changes" over signed amounts,
        which is what model_registry._project_backlog computes with math.fsum.
    """

    def pb(opening, bookings, cancellations, changes, remeasure, closing, mode):
        o, b, c, ch, rm, cl = (Decimal(opening), Decimal(bookings), Decimal(cancellations),
                               Decimal(changes), Decimal(remeasure), Decimal(closing))
        if mode == "a":
            change_term = -abs(ch)
            change_symbol, change_shown = "-", abs(ch)
        elif mode == "b":
            change_term = -ch
            change_symbol, change_shown = "-", ch
        elif mode == "c":
            change_term = ch
            change_symbol, change_shown = "+", ch
        else:
            raise ValueError(mode)
        total = o + b - c + change_term + rm - cl
        formula = ("%s + %s - %s %s %s + %s - %s" %
                   (opening, bookings, cancellations, change_symbol, change_shown,
                    remeasure, closing))
        return total, formula

    a1, f_a1 = pb(100, 40, 5, -10, -15, 60, "a")
    b1, f_b1 = pb(100, 40, 5, -10, -15, 60, "b")
    c1, f_c1 = pb(100, 40, 5, -10, -15, 60, "c")
    a2, _ = pb(60, 0, 0, 0, 0, 60, "a")
    b2, _ = pb(60, 0, 0, 0, 0, 60, "b")
    c2, _ = pb(60, 0, 0, 0, 0, 60, "c")
    da, f_da = pb(100, 40, 5, -10, 0, 60, "a")   # defaults: backlog_remeasurements omitted
    db, _ = pb(100, 40, 5, -10, 0, 60, "b")
    dc, _ = pb(100, 40, 5, -10, 0, 60, "c")
    sa, _ = pb(100, 40, 5, 10, 0, 60, "a")       # sign probe +10, reading a
    sb, _ = pb(100, 40, 5, 10, 0, 60, "b")       # sign probe +10, reading b
    sc, _ = pb(100, 40, 5, 10, 0, 60, "c")       # sign probe +10, reading c
    ta, _ = pb(100, 40, 5, -20, 0, 60, "a")      # sign probe -20, reading a
    tb, _ = pb(100, 40, 5, -20, 0, 60, "b")      # sign probe -20, reading b
    tc, _ = pb(100, 40, 5, -20, 0, 60, "c")      # sign probe -20, reading c
    return {
        "model_id": "project_backlog",
        "first_required_driver": "opening_backlog",
        "reading_A_card_arithmetic": {
            "desc": "card line 42 arithmetic: subtract the magnitude 10 and subtract the -15",
            "source": "card_M08.md L42",
            "positive_expected": str(a1),
        },
        "reading_B_card_formula_string": {
            "desc": "card line 42 symbols (- contract_changes) over the frozen signed convention",
            "source": "card_M08.md L8 and L42",
            "positive_expected": str(b1),
        },
        "reading_C_upstream_and_implementation": {
            "desc": "+ contract_changes over signed amounts",
            "source": "docs/buy_side_model_audit_2026-09-18.md:42 and scripts/model_registry.py:228",
            "positive_expected": str(c1),
        },
        "positive": expected_block([2027], [a1], [f_a1]),
        "continuity_positive": expected_block(
            [2027, 2028], [a1, a2], [f_a1, "60 + 0 - 0 - 0 + 0 - 60"]),
        "defaults": expected_block([2027], [da], [f_da]),
        "input": {
            "positive": {
                "model_id": "project_backlog",
                "base_revenue": 0,
                "drivers": {"opening_backlog": [100], "bookings": [40], "cancellations": [5],
                            "contract_changes": [-10], "backlog_remeasurements": [-15],
                            "closing_backlog": [60]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "project_backlog",
                "base_revenue": 0,
                "drivers": {"opening_backlog": [100, 60], "bookings": [40, 0],
                            "cancellations": [5, 0], "contract_changes": [-10, 0],
                            "backlog_remeasurements": [-15, 0], "closing_backlog": [60, 60]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "project_backlog",
                "base_revenue": 0,
                "drivers": {"opening_backlog": [100], "bookings": [40], "cancellations": [5],
                            "contract_changes": [-10], "closing_backlog": [60]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "opening_backlog",
            ("set_driver_element", "positive", "closing_backlog", 0, {"__float__": 500}),
            ("set_driver_multi", None, None,
             {"opening_backlog": [100, 61], "closing_backlog": [60, 61]}),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the backlog bridge ignores base_revenue at this entry point; design observation only"},
            {"id": "OBS-SIGN-B", "kind": "set_driver_element", "driver": "contract_changes",
             "index": 0, "value": {"__float__": 10}, "base_input": "defaults",
             "compare_to": None, "expect_equal": None,
             "why": "sign probe with contract_changes = +10: reading A gives %s, reading B gives %s, reading C gives %s; NO expectation and NO verdict is asserted" % (sa, sb, sc)},
            {"id": "OBS-SIGN-NEG", "kind": "set_driver_element", "driver": "contract_changes",
             "index": 0, "value": {"__float__": -20}, "base_input": "defaults",
             "compare_to": None, "expect_equal": None,
             "why": "second sign probe with contract_changes = -20: reading A gives %s, reading B gives %s, reading C gives %s - this probe separates reading B from A/C; NO expectation and NO verdict is asserted" % (ta, tb, tc)},
            {"id": "OBS-REMEASURE-USED", "kind": "input_replay", "input": "defaults",
             "compare_to": "positive", "expect_equal": False,
             "why": "omitting backlog_remeasurements changes the result, so the remeasurement term is really used"},
        ],
        "secondary_readings": {
            "reading_B_positive": str(b1),
            "reading_C_positive": str(c1),
            "reading_C_formula_string": f_c1,
            "reading_B_continuity": [str(b1), str(b2)],
            "reading_C_continuity": [str(c1), str(c2)],
            "reading_B_defaults": str(db),
            "reading_C_defaults": str(dc),
            "sign_probe_reading_A": str(sa),
            "sign_probe_reading_B": str(sb),
            "sign_probe_reading_C": str(sc),
            "sign_probe_neg_reading_A": str(ta),
            "sign_probe_neg_reading_B": str(tb),
            "sign_probe_neg_reading_C": str(tc),
        },
    }


BUILDERS = {"M05": m05, "M06": m06, "M07": m07, "M08": m08}


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
        "generated_by": "scripts/oracle_%s.py (stdlib only, no product import)" % card,
        "positive": data["positive"],
        "continuity_positive": data["continuity_positive"],
        "defaults": data["defaults"],
        "defaults_expected_float": data["defaults"]["expected_float"],
        "observation_expected": {},
        "negative_count": len(cases),
        "negative_ids": [c["id"] for c in cases],
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
    }
    if card == "M08":
        oracle["reading_A_card_arithmetic"] = data["reading_A_card_arithmetic"]
        oracle["reading_B_card_formula_string"] = data["reading_B_card_formula_string"]
        oracle["reading_C_upstream_and_implementation"] = data["reading_C_upstream_and_implementation"]
        oracle["secondary_readings"] = data["secondary_readings"]
    if card == "M07":
        oracle["observation_expected"]["OBS-DEFAULT-EQUIV"] = data["defaults"]

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
    if card == "M08":
        print("reading A (card arithmetic)   ", data["reading_A_card_arithmetic"]["positive_expected"])
        print("reading B (card formula text) ", data["reading_B_card_formula_string"]["positive_expected"])
        print("reading C (upstream/implement)", data["reading_C_upstream_and_implementation"]["positive_expected"])
        print("secondary readings", data["secondary_readings"])
    print("negative cases", len(cases), [c["id"] for c in cases])
    print("oracle_selfcheck product_import_present =", selfcheck["product_import_present"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
