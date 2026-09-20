"""Independent oracle generator for the I-10 model cards M17-M20 (standard library only).

Writes, for one card, into <out-root>/evidence/<card>/:
  input.json             frozen positive / continuity_positive / defaults inputs
  cases.json             negative cases (card-specific + N01-N05 + continuity break)
  oracle.json            frozen expected values + tolerances + hand-work records
  oracle_selfcheck.json  proof that this file does not import the product

Hard independence rule: this file must NEVER import the product under test
(the registry module or the extension module).  Every number below is plain
arithmetic derived by hand from the card text (see the attempt's oracle.md),
never from the product.

Run:
  python -X utf8 -B scripts/oracle_<CARD>.py --card <CARD> --out-root <attempt_root>
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
# and each card's oracle.md section 5.
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
# M17 licensing_commercial
# --------------------------------------------------------------------------
def m17():
    def lc(units, net_price, milestone, royalty, service):
        return (
            Decimal(units) * Decimal(net_price) + Decimal(milestone) + Decimal(royalty)
            + Decimal(service),
            "%s x %s + %s + %s + %s" % (units, net_price, milestone, royalty, service),
        )

    v, f = zip(*[lc(40, 2, 15, 5, 10)])
    c1 = lc(40, 2, 15, 5, 10)
    c2 = lc(55, 3, 0, 4, 0)
    d1 = lc(40, 2, 0, 0, 0)
    return {
        "model_id": "licensing_commercial",
        "first_required_driver": "treated_units",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "licensing_commercial",
                "base_revenue": 0,
                "drivers": {"treated_units": [40], "net_revenue_per_unit": [2],
                            "milestone_revenue": [15], "royalty_revenue": [5],
                            "service_revenue": [10]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "licensing_commercial",
                "base_revenue": 0,
                "drivers": {"treated_units": [40, 55], "net_revenue_per_unit": [2, 3],
                            "milestone_revenue": [15, 0], "royalty_revenue": [5, 4],
                            "service_revenue": [10, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "licensing_commercial",
                "base_revenue": 0,
                "drivers": {"treated_units": [40], "net_revenue_per_unit": [2]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "treated_units",
            ("set_driver_element", "positive", "treated_units", 0, {"__float__": -1}),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the rowwise calculator discards base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver_multi", "base_input": "defaults",
             "value": {"milestone_revenue": [0], "royalty_revenue": [0], "service_revenue": [0]},
             "compare_to": "defaults", "expect_equal": True,
             "why": "writing the three omitted optional drivers explicitly as 0 reproduces the omitted-input result, so the documented default of 0 is falsifiable"},
        ],
        "observation_expected": {},
    }


# --------------------------------------------------------------------------
# M18 advertising
# --------------------------------------------------------------------------
def m18():
    def ad(impressions, fill, rpm, other):
        return (
            Decimal(impressions) / Decimal(1000) * Decimal(fill) * Decimal(rpm) + Decimal(other),
            "%s / 1000 x %s x %s + %s" % (impressions, fill, rpm, other),
        )

    v, f = zip(*[ad(1000000, "0.8", 10, 100)])
    c1 = ad(1000000, "0.8", 10, 100)
    c2 = ad(1500000, "0.75", 12, 0)
    d1 = ad(1000000, "0.8", 10, 0)
    t1 = ad(2000000, "0.8", 10, 100)
    return {
        "model_id": "advertising",
        "first_required_driver": "eligible_impressions",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "observation_expected": {"OBS-THOUSAND-ONCE": expected_block([2027], [t1[0]], [t1[1]])},
        "input": {
            "positive": {
                "model_id": "advertising",
                "base_revenue": 0,
                "drivers": {"eligible_impressions": [1000000], "fill_rate": [0.8],
                            "revenue_per_thousand_impressions": [10], "other_revenue": [100]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "advertising",
                "base_revenue": 0,
                "drivers": {"eligible_impressions": [1000000, 1500000],
                            "fill_rate": [0.8, 0.75],
                            "revenue_per_thousand_impressions": [10, 12],
                            "other_revenue": [100, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "advertising",
                "base_revenue": 0,
                "drivers": {"eligible_impressions": [1000000], "fill_rate": [0.8],
                            "revenue_per_thousand_impressions": [10]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "eligible_impressions",
            ("set_driver_element", "positive", "fill_rate", 0, {"__float__": 1.2}),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the rowwise calculator discards base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver", "driver": "other_revenue",
             "value": [0], "base_input": "defaults", "compare_to": "defaults", "expect_equal": True,
             "why": "writing the omitted optional driver explicitly as 0 reproduces the omitted-input result"},
            {"id": "OBS-THOUSAND-ONCE", "kind": "set_driver", "driver": "eligible_impressions",
             "value": [2000000], "base_input": "positive",
             "expectation": "doubling eligible_impressions adds exactly one more 8000 block (16100); a second division by 1000 would give 16.1",
             "why": "the card fixes 'thousand-impression conversion happens exactly once'; this probe is a numeric fidelity probe of that statement (recorded under observation_expected)"},
        ],
    }


# --------------------------------------------------------------------------
# M19 gaming
# --------------------------------------------------------------------------
def m19():
    def gm(users, conversion, per_payer, other):
        return (
            Decimal(users) * Decimal(conversion) * Decimal(per_payer) + Decimal(other),
            "%s x %s x %s + %s" % (users, conversion, per_payer, other),
        )

    v, f = zip(*[gm(1000, "0.05", 20, 10)])
    c1 = gm(1000, "0.05", 20, 10)
    c2 = gm(1200, "0.06", 22, 0)
    d1 = gm(1000, "0.05", 20, 0)
    b1 = gm(1000, "1.0", 20, 10)
    return {
        "model_id": "gaming",
        "first_required_driver": "active_users",
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "observation_expected": {"OBS-PAYER-BOUNDARY": expected_block([2027], [b1[0]], [b1[1]])},
        "input": {
            "positive": {
                "model_id": "gaming",
                "base_revenue": 0,
                "drivers": {"active_users": [1000], "payer_conversion": [0.05],
                            "revenue_per_payer": [20], "other_revenue": [10]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "gaming",
                "base_revenue": 0,
                "drivers": {"active_users": [1000, 1200], "payer_conversion": [0.05, 0.06],
                            "revenue_per_payer": [20, 22], "other_revenue": [10, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "gaming",
                "base_revenue": 0,
                "drivers": {"active_users": [1000], "payer_conversion": [0.05],
                            "revenue_per_payer": [20]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "active_users",
            ("set_driver_element", "positive", "payer_conversion", 0, {"__float__": 1.1}),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the rowwise calculator discards base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver", "driver": "other_revenue",
             "value": [0], "base_input": "defaults", "compare_to": "defaults", "expect_equal": True,
             "why": "writing the omitted optional driver explicitly as 0 reproduces the omitted-input result"},
            {"id": "OBS-PAYER-BOUNDARY", "kind": "set_driver_element", "driver": "payer_conversion",
             "index": 0, "value": {"__float__": 1.0}, "base_input": "positive",
             "expectation": "payer_conversion = 1.0 is inside the frozen [0,1] ratio domain, so it must be accepted: 1000 x 1.0 x 20 + 10 = 20010",
             "why": "probes whether the ratio bound is inclusive at its upper edge (recorded under observation_expected)"},
        ],
    }


# --------------------------------------------------------------------------
# M20 cohort_subscription
# --------------------------------------------------------------------------
def m20():
    def cs(opening, new, churned, ending, rpc, new_frac, lost_frac, timing, usage):
        opening, new, churned, ending = (Decimal(opening), Decimal(new), Decimal(churned),
                                        Decimal(ending))
        rpc, new_frac, lost_frac = Decimal(rpc), Decimal(new_frac), Decimal(lost_frac)
        timing, usage = Decimal(timing), Decimal(usage)
        expected_ending = opening + new - churned
        balance_ok = expected_ending == ending
        exposure = opening + new * new_frac - churned * lost_frac
        total = exposure * rpc * timing + usage
        formula = ("((%s + %s x %s - %s x %s)) x %s x %s + %s"
                   % (opening, new, new_frac, churned, lost_frac, rpc, timing, usage))
        return total, formula, exposure, balance_ok

    v, f, e1, b1 = cs(100, 40, 20, 120, 2, "0.25", "0.75", 1, 5)
    c1 = cs(100, 40, 20, 120, 2, "0.25", "0.75", 1, 5)
    c2 = cs(120, 0, 0, 120, 2, "0.25", "0.75", 1, 0)
    d1 = cs(100, 40, 20, 120, 2, "0.5", "0.5", 1, 0)
    z1 = cs(0, 0, 0, 0, 2, "0.5", "0.5", 1, 7)
    assert b1 and c1[3] and c2[3] and d1[3] and z1[3], "a frozen input violates the customer bridge"
    return {
        "model_id": "cohort_subscription",
        "first_required_driver": "opening_customers",
        "positive": expected_block([2027], [v], [f]),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "observation_expected": {"OBS-ZERO-CUSTOMERS": expected_block([2027], [z1[0]], [z1[1]])},
        "continuity_case_source": {
            "card": "card_M20.md L59-125 (two-year continuity case, printed in the card itself)",
            "hand_work_second_year": ("year 2 has no new/churned/usage flow, opening = prior closing; "
                                      "exposure 120 x 2 x 1 + 0 = 240"),
            "expected_negative": ("ModelRegistryError/continuity; each year balances on its own, but "
                                  "year 2 opening is 1 higher than year 1 closing"),
            "frozen_continuity_expected": [str(c1[0]), str(c2[0])],
        },
        "input": {
            "positive": {
                "model_id": "cohort_subscription",
                "base_revenue": 0,
                "drivers": {"opening_customers": [100], "new_customers": [40],
                            "churned_customers": [20], "ending_customers": [120],
                            "revenue_per_customer": [2],
                            "new_customer_revenue_fraction": [0.25],
                            "churned_customer_lost_fraction": [0.75],
                            "timing_factor": [1], "usage_revenue": [5]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "cohort_subscription",
                "base_revenue": 0,
                "drivers": {"opening_customers": [100, 120], "new_customers": [40, 0],
                            "churned_customers": [20, 0], "ending_customers": [120, 120],
                            "revenue_per_customer": [2, 2],
                            "new_customer_revenue_fraction": [0.25, 0.25],
                            "churned_customer_lost_fraction": [0.75, 0.75],
                            "timing_factor": [1, 1], "usage_revenue": [5, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "cohort_subscription",
                "base_revenue": 0,
                "drivers": {"opening_customers": [100], "new_customers": [40],
                            "churned_customers": [20], "ending_customers": [120],
                            "revenue_per_customer": [2]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "opening_customers",
            ("set_driver_element", "positive", "ending_customers", 0, {"__float__": 121}),
            ("set_driver_multi", None, None,
             {"opening_customers": [100, 121], "ending_customers": [120, 121]}),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the cohort calculator deletes base_revenue; design observation only, not a pass condition"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver_multi", "base_input": "defaults",
             "value": {"timing_factor": [1], "usage_revenue": [0],
                       "new_customer_revenue_fraction": [0.5],
                       "churned_customer_lost_fraction": [0.5]},
             "compare_to": "defaults", "expect_equal": True,
             "why": "writing the four optional drivers explicitly at their documented defaults reproduces the omitted-input result, so the defaults are falsifiable"},
            {"id": "OBS-ZERO-CUSTOMERS", "kind": "set_driver_multi", "base_input": "positive",
             "value": {"opening_customers": [0], "new_customers": [0], "churned_customers": [0],
                       "ending_customers": [0], "revenue_per_customer": [2],
                       "new_customer_revenue_fraction": [0.5],
                       "churned_customer_lost_fraction": [0.5], "timing_factor": [1],
                       "usage_revenue": [7]},
             "expectation": "an all-zero customer bridge with zero exposure is accepted (the guard is exposure < 0): 0 x 2 x 1 + 7 = 7",
             "why": "probes the lower edge of the 'cohort customer time exposure cannot be negative' guard (recorded under observation_expected)"},
        ],
    }


BUILDERS = {"M17": m17, "M18": m18, "M19": m19, "M20": m20}


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
        "model_id": data["model_id"],
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
        "observation_expected": data.get("observation_expected", {}),
        "negative_count": len(cases),
        "negative_ids": [c["id"] for c in cases],
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
        "fidelity_rule": ("len(output) must equal len(years) and len(expected); every element must "
                          "be a plain finite number; year labels are not observable from the "
                          "returned list, so length is the only year-linked observable"),
    }
    if card == "M20":
        oracle["continuity_case_source"] = data["continuity_case_source"]

    def dump(name, doc):
        path = os.path.join(target, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(doc, handle, ensure_ascii=False, indent=1)
        return path

    written = {}
    written["input.json"] = dump("input.json", input_doc)
    written["cases.json"] = dump("cases.json", cases_doc)
    written["oracle.json"] = dump("oracle.json", oracle)

    with open(__file__, "rb") as handle:
        script_sha = hashlib.sha256(handle.read()).hexdigest()
    source_text = open(__file__, "r", encoding="utf-8").read()
    import_lines = [line.strip() for line in source_text.splitlines()
                    if line.startswith("import ") or line.startswith("from ")]
    selfcheck = {
        "script": os.path.abspath(__file__),
        "script_sha256": script_sha,
        "rule": "the oracle generator must not import the product under test",
        "forbidden_tokens": list(PRODUCT_MODULE_TOKENS),
        "import_lines": import_lines,
        "product_import_present": any(
            token in line for token in PRODUCT_MODULE_TOKENS for line in import_lines),
        "written_hashes": {name: hashlib.sha256(open(path, "rb").read()).hexdigest()
                           for name, path in written.items()},
    }
    dump("oracle_selfcheck.json", selfcheck)

    print("card", card, "model", data["model_id"])
    print("positive expected", data["positive"]["expected"],
          "tolerances", data["positive"]["tolerances"])
    print("positive hand_work", data["positive"]["hand_work"])
    print("continuity expected", data["continuity_positive"]["expected"])
    print("continuity hand_work", data["continuity_positive"]["hand_work"])
    print("defaults expected", data["defaults"]["expected"])
    print("observation_expected keys", sorted(oracle["observation_expected"]))
    print("negative cases", len(cases), [c["id"] for c in cases])
    print("oracle_selfcheck product_import_present =", selfcheck["product_import_present"])
    print("written hashes", selfcheck["written_hashes"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
