"""Independent oracle generator for the I-10 model cards M29, M30 and M31.

Writes, for one card, into <out-root>/evidence/<card>/:
  input.json             frozen positive / continuity_positive / defaults inputs
  cases.json             negative cases (card-specific + N01-N05 + stock-flow continuity break)
  oracle.json            frozen expected values + tolerances + hand-work records
  oracle_selfcheck.json  proof that this file does not import the product

Hard independence rule: this file must NEVER import the product under test (neither the
registry module nor the extension module).  Every number below is plain arithmetic derived
by hand from the card text (see the attempt's oracle.md), never from the product.

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


# Frozen refusal rationale.  Sources: card_M29/M30/M31.md, common_model_cards.md L24-30
# (the common negatives N01-N05), and each card's oracle.md section 5.
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
    "CONT-BREAK": "stock-flow continuity break for this card (oracle.md section 4)",
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
# card arithmetic (hand work, transcribed from the card text)
# --------------------------------------------------------------------------
def m29_positive():
    """card_M29.md L39: demand = 1000 x 0.2 = 200; min(200, 150) = 150; 150 x 0.5 x 4 = 300."""
    units = min(Decimal(1000) * Decimal("0.2"), Decimal(150))
    value = units * Decimal("0.5") * Decimal(4)
    formula = "min(1000 x 0.2, 150) x 0.5 x 4"
    return value, formula, units


def m29_year2():
    """oracle.md section 3: demand = 2000 x 0.1 = 200; min(200, 400) = 200; 200 x 1.0 x 5 = 1000."""
    units = min(Decimal(2000) * Decimal("0.1"), Decimal(400))
    value = units * Decimal("1.0") * Decimal(5)
    return value, "min(2000 x 0.1, 400) x 1.0 x 5"


def m30_positive():
    """card_M30.md L42: 500+100-50-200 = 350; 200 x 3 = 600."""
    balance = Decimal(500) + Decimal(100) - Decimal(50) - Decimal(200)
    assert balance == Decimal(350), "the frozen M30 input does not balance"
    value = Decimal(200) * Decimal(3)
    return balance, value, "500 + 100 - 50 - 200 = 350; 200 x 3"


def m30_year2():
    """card_M30.md L93: no flow in year 2 and opening = prior closing, so 0 x 3 = 0."""
    balance = Decimal(350) + Decimal(0) - Decimal(0) - Decimal(0)
    assert balance == Decimal(350), "the frozen M30 second year does not balance"
    return Decimal(0) * Decimal(3), "350 + 0 - 0 - 0 = 350; 0 x 3"


def m31_positive():
    """card_M31.md L45: 100+60+10-5-80 = 85; 80 x 2 = 160."""
    balance = (Decimal(100) + Decimal(60) + Decimal(10) - Decimal(5) - Decimal(80))
    assert balance == Decimal(85), "the frozen M31 input does not balance"
    value = Decimal(80) * Decimal(2)
    return balance, value, "100 + 60 + 10 - 5 - 80 = 85; 80 x 2"


def m31_year2():
    """card_M31.md L100: no flow in year 2 and opening = prior closing, so 0 x 2 = 0."""
    balance = (Decimal(85) + Decimal(0) + Decimal(0) - Decimal(0) - Decimal(0))
    assert balance == Decimal(85), "the frozen M31 second year does not balance"
    return Decimal(0) * Decimal(2), "85 + 0 + 0 - 0 - 0 = 85; 0 x 2"


# --------------------------------------------------------------------------
# M29 commercial_launch : min(demand, capacity) x year fraction x net price
# --------------------------------------------------------------------------
def m29():
    v, f, demand_units = m29_positive()
    v2, f2 = m29_year2()
    below_supply = (min(Decimal(50) * Decimal("0.2"), Decimal(150)) * Decimal("0.5") * Decimal(4))
    full_year = (min(Decimal(1000) * Decimal("0.2"), Decimal(150)) * Decimal("1.0") * Decimal(4))
    base_ignored = (min(Decimal(1000) * Decimal("0.2"), Decimal(150)) * Decimal("0.5") * Decimal(4))
    return {
        "model_id": "commercial_launch",
        "first_required_driver": "eligible_units",
        "positive": expected_block([2027], [v], [f]),
        "continuity_positive": expected_block([2027, 2028], [v, v2], [f, f2]),
        "defaults": expected_block([2027], [v], [f]),
        "observation_expected": {
            "OBS-MIN-DEMAND-BINDS": expected_block([2027], [below_supply],
                                                   ["min(50 x 0.2, 150) x 0.5 x 4"]),
            "OBS-FULL-YEAR-FRACTION": expected_block([2027], [full_year],
                                                     ["min(1000 x 0.2, 150) x 1.0 x 4"]),
            "OBS-BASE-IGNORED": expected_block([2027], [base_ignored], [f]),
        },
        "continuity_case_source": None,
        "input": {
            "positive": {
                "model_id": "commercial_launch",
                "base_revenue": 0,
                "drivers": {"eligible_units": [1000], "adoption_rate": [0.2],
                            "annual_supply_capacity": [150], "commercial_year_fraction": [0.5],
                            "net_revenue_per_unit": [4]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "commercial_launch",
                "base_revenue": 0,
                "drivers": {"eligible_units": [1000, 2000], "adoption_rate": [0.2, 0.1],
                            "annual_supply_capacity": [150, 400], "commercial_year_fraction": [0.5, 1.0],
                            "net_revenue_per_unit": [4, 5]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "commercial_launch",
                "base_revenue": 0,
                "drivers": {"eligible_units": [1000], "adoption_rate": [0.2],
                            "annual_supply_capacity": [150], "commercial_year_fraction": [0.5],
                            "net_revenue_per_unit": [4]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "eligible_units",
            ("set_driver_element", "positive", "adoption_rate", 0, {"__float__": 1.1}),
            ("set_years", None, None, [2027, 2029]),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": ("the rowwise calculator deletes base_revenue; design observation only, not a "
                     "pass condition")},
            {"id": "OBS-MIN-DEMAND-BINDS", "kind": "set_driver", "driver": "eligible_units",
             "value": [50], "base_input": "positive",
             "expectation": ("with demand below supply the min() must pick the demand side: "
                             "50 x 0.2 = 10 eligible, 10 x 0.5 x 4 = 20"),
             "why": ("the card fixes min(demand, capacity); this probe makes the min() falsifiable in "
                     "the DEMAND-binding direction (recorded under observation_expected)")},
            {"id": "OBS-FULL-YEAR-FRACTION", "kind": "set_driver", "driver":
             "commercial_year_fraction", "value": [1.0], "base_input": "positive",
             "expectation": ("commercial_year_fraction = 1.0 is the inclusive upper edge of the ratio "
                             "domain and must be accepted: 150 x 1.0 x 4 = 600"),
             "why": ("probes the upper edge of the ratio domain, which is where the card-specific "
                     "negative (1.1) is refused")},
        ],
    }


# --------------------------------------------------------------------------
# M30 finite_adoption : adopted_units x net price on a balanced unserved-market bridge
# --------------------------------------------------------------------------
def m30():
    _balance, v, f = m30_positive()
    v2, f2 = m30_year2()
    rate_one = Decimal(200) * Decimal(3)
    tolerance_case = Decimal(200) * Decimal(3)
    return {
        "model_id": "finite_adoption",
        "first_required_driver": "opening_unserved_market",
        "positive": expected_block([2027], [v], [f]),
        "continuity_positive": expected_block([2027, 2028], [v, v2], [f, f2]),
        "defaults": expected_block([2027], [v], [f]),
        "observation_expected": {
            "OBS-RATE-ONE": expected_block([2027], [rate_one],
                                           ["200 x 3 (adopted_units unchanged; adoption_rate is not "
                                            "a driver of this model)"]),
            "OBS-BASE-IGNORED": expected_block([2027], [Decimal(200) * Decimal(3)], [f]),
        },
        "continuity_case_source": {
            "card": "card_M30.md L52-106 (two-year continuity case, printed in the card itself)",
            "hand_work_second_year": ("year 2 has no new / removed / adopted flow and opening = prior "
                                      "closing (350), so the bridge balances at 350 and revenue is "
                                      "0 x 3 = 0"),
            "expected_negative": ("ModelRegistryError/continuity; each year balances on its own, but "
                                  "year 2 opening is 1 higher than year 1 closing"),
            "frozen_continuity_expected": [str(v), str(v2)],
        },
        "input": {
            "positive": {
                "model_id": "finite_adoption",
                "base_revenue": 0,
                "drivers": {"opening_unserved_market": [500], "new_eligible_units": [100],
                            "removed_eligible_units": [50], "adopted_units": [200],
                            "closing_unserved_market": [350], "net_revenue_per_unit": [3]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "finite_adoption",
                "base_revenue": 0,
                "drivers": {"opening_unserved_market": [500, 350], "new_eligible_units": [100, 0],
                            "removed_eligible_units": [50, 0], "adopted_units": [200, 0],
                            "closing_unserved_market": [350, 350], "net_revenue_per_unit": [3, 3]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "finite_adoption",
                "base_revenue": 0,
                "drivers": {"opening_unserved_market": [500], "new_eligible_units": [100],
                            "removed_eligible_units": [50], "adopted_units": [200],
                            "closing_unserved_market": [350], "net_revenue_per_unit": [3]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "opening_unserved_market",
            ("set_driver_element", "positive", "closing_unserved_market", 0, {"__float__": 351}),
            ("set_driver_multi", None, None,
             {"opening_unserved_market": [500, 351], "closing_unserved_market": [350, 351]}),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": ("the bridge calculator deletes base_revenue; design observation only, not a pass "
                     "condition")},
            {"id": "OBS-RATE-ONE", "kind": "input_replay", "input": "positive",
             "compare_to": "positive", "expect_equal": True,
             "expectation": ("replays the frozen card input so the runner's own reading is "
                             "reproducible: 200 x 3 = 600"),
             "why": ("finite_adoption has no adoption_rate driver at all (the card's own negative "
                     "edits closing_unserved_market); this replay re-reads the frozen input instead of "
                     "inventing a driver")},
            {"id": "OBS-TOLERANCE-2Y", "kind": "set_driver", "driver": "opening_unserved_market",
             "value": [500, 350.0000000001], "base_input": "continuity_positive",
             "also_set_driver": {"closing_unserved_market": [350, 350.0000000001]},
             "expectation": ("the continuity check uses math.isclose(rel_tol=1e-9, abs_tol=1e-9), so a "
                             "1e-10 imbalance in a balancing year must be accepted: revenue stays "
                             "[600, 0]"),
             "why": ("probes the tolerant side of the continuity rule whose strict side is CONT-BREAK")},
        ],
        "frozen_continuity_tolerance_case": tolerance_case,
    }


# --------------------------------------------------------------------------
# M31 inventory_sellthrough : sold_units x net price on a balanced inventory bridge
# --------------------------------------------------------------------------
def m31():
    _balance, v, f = m31_positive()
    v2, f2 = m31_year2()
    zero_sold = Decimal(0) * Decimal(2)
    hundred_sold = Decimal(100) * Decimal(2)
    return {
        "model_id": "inventory_sellthrough",
        "first_required_driver": "opening_inventory",
        "positive": expected_block([2027], [v], [f]),
        "continuity_positive": expected_block([2027, 2028], [v, v2], [f, f2]),
        "defaults": expected_block([2027], [v], [f]),
        "observation_expected": {
            "OBS-SCRAP-NOT-REVENUE": expected_block([2027], [zero_sold],
                                                    ["0 x 2 (sold_units = 0; scrapped 100 is not "
                                                     "revenue)"]),
            "OBS-SOLD-ONLY": expected_block([2027], [hundred_sold], ["100 x 2"]),
            "OBS-BASE-IGNORED": expected_block([2027], [Decimal(80) * Decimal(2)], [f]),
        },
        "continuity_case_source": {
            "card": "card_M31.md L55-113 (two-year continuity case, printed in the card itself)",
            "hand_work_second_year": ("year 2 has no production / purchase / scrap / sale flow and "
                                      "opening = prior closing (85), so the bridge balances at 85 and "
                                      "revenue is 0 x 2 = 0"),
            "expected_negative": ("ModelRegistryError/continuity; each year balances on its own, but "
                                  "year 2 opening is 1 higher than year 1 closing"),
            "frozen_continuity_expected": [str(v), str(v2)],
        },
        "input": {
            "positive": {
                "model_id": "inventory_sellthrough",
                "base_revenue": 0,
                "drivers": {"opening_inventory": [100], "saleable_production": [60],
                            "purchased_units": [10], "scrapped_units": [5], "sold_units": [80],
                            "closing_inventory": [85], "net_revenue_per_unit": [2]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "inventory_sellthrough",
                "base_revenue": 0,
                "drivers": {"opening_inventory": [100, 85], "saleable_production": [60, 0],
                            "purchased_units": [10, 0], "scrapped_units": [5, 0], "sold_units": [80, 0],
                            "closing_inventory": [85, 85], "net_revenue_per_unit": [2, 2]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "inventory_sellthrough",
                "base_revenue": 0,
                "drivers": {"opening_inventory": [100], "saleable_production": [60],
                            "purchased_units": [10], "scrapped_units": [5], "sold_units": [80],
                            "closing_inventory": [85], "net_revenue_per_unit": [2]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "opening_inventory",
            ("set_driver_element", "positive", "closing_inventory", 0, {"__float__": 86}),
            ("set_driver_multi", None, None,
             {"opening_inventory": [100, 86], "closing_inventory": [85, 86]}),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": ("the bridge calculator deletes base_revenue; design observation only, not a pass "
                     "condition")},
            {"id": "OBS-SCRAP-NOT-REVENUE", "kind": "set_driver_multi", "base_input": "positive",
             "value": {"scrapped_units": [85], "sold_units": [0], "saleable_production": [0],
                       "purchased_units": [0],
                       "closing_inventory": [15]},
             "expectation": ("revenue follows sold_units only, and scrapped units are not negative "
                             "revenue: 0 x 2 = 0 while the bridge balances at "
                             "100 + 0 + 0 - 85 - 0 = 15"),
             "why": ("the card states that scrapping is not negative revenue; this probe makes that "
                     "statement falsifiable with a balancing input (recorded under "
                     "observation_expected)")},
            {"id": "OBS-SOLD-ONLY", "kind": "set_driver", "driver": "sold_units", "value": [100],
             "base_input": "positive", "also_set_driver": {"closing_inventory": [65]},
             "expectation": ("revenue is sold_units x net price with the bridge rebalanced: "
                             "100 x 2 = 200"),
             "why": "probes the revenue line at a different sold quantity with a balancing bridge"},
        ],
    }


BUILDERS = {"M29": m29, "M30": m30, "M31": m31}

MODEL_IDS = {"M29": "commercial_launch", "M30": "finite_adoption",
             "M31": "inventory_sellthrough"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", choices=sorted(BUILDERS),
                        help="required unless --emit-script is used alone")
    parser.add_argument("--out-root", default=None,
                        help="attempt root; required unless --emit-script is used alone")
    parser.add_argument("--emit-script", default=None,
                        help="write a byte-identical copy of this generator to this path")
    args = parser.parse_args()

    if args.emit_script:
        with open(__file__, "rb") as handle:
            payload = handle.read()
        os.makedirs(os.path.dirname(os.path.abspath(args.emit_script)), exist_ok=True)
        with open(args.emit_script, "wb") as handle:
            handle.write(payload)
        print("emitted oracle script copy ->", args.emit_script,
              "sha256", hashlib.sha256(payload).hexdigest())
        if not args.card or not args.out_root:
            return 0   # emit-only mode: generation is a separate, later invocation (see oracle.md 9)

    if not args.card or not args.out_root:
        parser.error("--card and --out-root are required for oracle generation")

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
        "fidelity_rule": ("len(output) must equal len(years) and len(expected); every element must be "
                          "a plain finite number; year labels are not observable from the returned "
                          "list, so length is the only year-linked observable"),
        "model_has_no_optional_drivers": True,
    }
    if data.get("continuity_case_source"):
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

    print("card", card, "model", data["model_id"], "expected_model", MODEL_IDS[card])
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
