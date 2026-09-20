"""Independent oracle generator for cards M09-M12 (Python standard library only).

Writes, for one card, into <out-root>/evidence/<CARD>/:
  input.json           frozen positive / continuity_positive / defaults inputs
  cases.json           negative cases (card-specific + N01-N05 + continuity break)
  oracle.json          frozen expected values, tolerances, contract checks
  oracle_selfcheck.json proof that this file does not import the product

HARD INDEPENDENCE RULE
----------------------
This file must NEVER import model_registry, model_extensions or any product module.
Every number below is plain arithmetic derived from the card text and the frozen
oracle.md (see the ``hand_work`` strings), never from the product.

The script is deterministic: re-running it reproduces input.json, cases.json and
oracle.json byte for byte (see evidence/<CARD>/regeneration_check.json).

Run (from an attempt root):
  python -X utf8 -B scripts/oracle_cards_M09_M12.py --card M09 --out-root <attempt_root>
Optional:
  --emit-script <path>   write a byte-identical copy of this generator to <path>
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
        "hand_work": list(formulas),
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
    "NEG-CARD": "card-specific negative named in the card body",
    "CONT-BREAK": "continuity break for this card (oracle.md section 4)",
}


def common_cases(first_required_driver, card_negative, continuity_break):
    """Build the frozen NEG-CARD + N01-N05 + CONT-BREAK list (11 cases)."""
    card = dict(card_negative)
    cont = dict(continuity_break)
    return [
        dict(card, id="NEG-CARD", expected="ModelRegistryError",
             base_input=card.get("base_input", "positive"), why=WHY["NEG-CARD"]),
        _case("N01a", "set_driver_element", "positive", first_required_driver, 0,
              {"__bool__": True}),
        _case("N01b", "set_driver_element", "positive", first_required_driver, 0,
              {"__float__": "nan"}),
        _case("N01c", "set_driver_element", "positive", first_required_driver, 0,
              {"__float__": "inf"}),
        _case("N01d", "set_driver_element", "positive", first_required_driver, 0,
              {"__float__": "-inf"}),
        _case("N02", "set_driver", "positive", first_required_driver, None, []),
        _case("N03", "delete_driver", "positive", first_required_driver),
        _case("N04", "add_driver", "positive", "unknown_driver", None, [1]),
        _case("N05a", "set_years", "positive", None, None, []),
        _case("N05b", "set_years", "positive", None, None, {"__bool__first__": True}),
        dict(cont, id="CONT-BREAK", expected="ModelRegistryError",
             base_input=cont.get("base_input", "continuity_positive"), why=WHY["CONT-BREAK"]),
    ]


def _case(case_id, kind, base_input, driver=None, index=None, value=None, guard_hint=""):
    case = {"id": case_id, "kind": kind, "driver": driver,
            "expected": "ModelRegistryError", "base_input": base_input,
            "why": WHY[case_id], "guard_hint": guard_hint}
    if kind == "set_driver_element":
        case["index"] = index
        case["value"] = value
    elif kind in ("set_driver", "add_driver", "set_years", "set_driver_multi", "set_base_revenue"):
        case["value"] = value
    return case


def contract_block(formula, required, optional, dimensions, effective_defaults):
    return {
        "formula": formula,
        "required": sorted(required),
        "optional": sorted(optional),
        "dimensions": dict(dimensions),
        "effective_defaults_expected": dict(effective_defaults),
        "declared_defaults_expected": {},
        "declared_defaults_note": (
            "the card states the optional default, but the registry declares no default for these "
            "drivers; the stated behaviour is realised by the implicit zero-fill at "
            "scripts/model_registry.py:335. The gating check is the behavioural defaults case, "
            "not the declared defaults mapping (oracle.md section 7; OQ-1)."),
        "output_container": "list",
        "output_element_types": ["float"],
    }


# --------------------------------------------------------------------------
# M09 resource
# --------------------------------------------------------------------------
def m09():
    def res(volume, price, other):
        return (Decimal(volume) * Decimal(price) + Decimal(other),
                "%s x %s + %s" % (volume, price, other))

    v, f = zip(*[res(30, 4, 2)])
    c1 = res(30, 4, 2)
    c2 = res(45, 5, 0)
    d1 = res(30, 4, 0)
    return {
        "model_id": "resource",
        "first_required_driver": "saleable_volume",
        "contract": contract_block(
            "revenue = saleable_volume * realized_price + other_revenue",
            ("saleable_volume", "realized_price"), ("other_revenue",),
            {"saleable_volume": "quantity", "realized_price": "revenue_per_unit",
             "other_revenue": "revenue"},
            {"other_revenue": 0.0}),
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "resource", "base_revenue": 0,
                "drivers": {"saleable_volume": [30], "realized_price": [4],
                            "other_revenue": [2]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "resource", "base_revenue": 0,
                "drivers": {"saleable_volume": [30, 45], "realized_price": [4, 5],
                            "other_revenue": [2, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "resource", "base_revenue": 0,
                "drivers": {"saleable_volume": [30], "realized_price": [4]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "saleable_volume",
            _case("NEG-CARD", "set_driver_element", "positive", "saleable_volume", 0,
                  {"__float__": "-1"},
                  guard_hint="driver value-domain guard: quantity default bound [0, inf)"),
            _case("CONT-BREAK", "set_years", "continuity_positive", None, None,
                  [2027, 2029],
                  guard_hint="fiscal-year consecutiveness guard"),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the rowwise calculator discards base_revenue; design observation only, "
                    "not a pass condition"},
            {"id": "OBS-PRICE-NEG", "kind": "set_driver", "driver": "realized_price",
             "value": [-1], "base_input": "positive",
             "why": "records whether a negative realized price is expressible; the driver-domain "
                    "guard runs before the calculator, so the recorded message shows which guard "
                    "fires first (a negative total would also be refused)"},
        ],
        "observation_expected": {
            "OBS-BASE-IGNORED": {"expected_float": [float(v[0])]},
            "OBS-PRICE-NEG": {"expected_raised": "ModelRegistryError"},
        },
    }


# --------------------------------------------------------------------------
# M10 reserve_depletion
# --------------------------------------------------------------------------
def m10():
    def rd(opening, additions, revisions, depletion, recovery, price, other):
        balance = (Decimal(opening) + Decimal(additions) + Decimal(revisions)
                   - Decimal(depletion))
        revenue = Decimal(depletion) * Decimal(recovery) * Decimal(price) + Decimal(other)
        return revenue, ("balance %s+%s+%s-%s=%s ; revenue %s x %s x %s + %s"
                         % (opening, additions, revisions, depletion, balance,
                            depletion, recovery, price, other))

    v, f = zip(*[rd(1000, 100, -50, 200, "0.8", 3, 10)])
    c1 = rd(1000, 100, -50, 200, "0.8", 3, 10)
    c2 = rd(850, 0, 0, 0, "0.8", 3, 0)
    d1 = rd(1000, 100, 0, 250, "0.8", 3, 0)
    r_pos = rd(1000, 100, 50, 200, "0.8", 3, 10)
    return {
        "model_id": "reserve_depletion",
        "first_required_driver": "opening_reserves",
        "contract": contract_block(
            "revenue = depletion * recovery_rate * realized_price + other_revenue",
            ("opening_reserves", "additions", "depletion", "closing_reserves",
             "recovery_rate", "realized_price"),
            ("other_revenue", "reserve_revisions"),
            {"opening_reserves": "reserve_volume", "additions": "reserve_volume",
             "depletion": "reserve_volume", "closing_reserves": "reserve_volume",
             "reserve_revisions": "reserve_volume", "recovery_rate": "ratio",
             "realized_price": "revenue_per_unit", "other_revenue": "revenue"},
            {"other_revenue": 0.0, "reserve_revisions": 0.0}),
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "reserve_depletion", "base_revenue": 0,
                "drivers": {"opening_reserves": [1000], "additions": [100],
                            "reserve_revisions": [-50], "depletion": [200],
                            "closing_reserves": [850], "recovery_rate": [0.8],
                            "realized_price": [3], "other_revenue": [10]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "reserve_depletion", "base_revenue": 0,
                "years": [2027, 2028],
                "drivers": {"opening_reserves": [1000, 850], "additions": [100, 0],
                            "reserve_revisions": [-50, 0], "depletion": [200, 0],
                            "closing_reserves": [850, 850], "recovery_rate": [0.8, 0.8],
                            "realized_price": [3, 3], "other_revenue": [10, 0]},
            },
            "defaults": {
                "model_id": "reserve_depletion", "base_revenue": 0,
                "drivers": {"opening_reserves": [1000], "additions": [100],
                            "depletion": [250], "closing_reserves": [850],
                            "recovery_rate": [0.8], "realized_price": [3]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "opening_reserves",
            _case("NEG-CARD", "set_driver", "positive", "closing_reserves", None, [851],
                  guard_hint="stock-flow balance guard: 1000+100-50-200 = 850 != 851"),
            dict(_case("CONT-BREAK", "set_driver_multi", "continuity_positive", None, None,
                       {"opening_reserves": [1000, 851], "closing_reserves": [850, 851]},
                       guard_hint="cross-year continuity guard: opening[2028]=851 != "
                                  "closing[2027]=850; each year balances on its own"),
                 ),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the reserve bridge discards base_revenue; design observation only"},
            {"id": "OBS-DEFAULT-EQUIV", "kind": "set_driver_multi", "base_input": "defaults",
             "value": {"other_revenue": [0], "reserve_revisions": [0]},
             "compare_to": "defaults", "expect_equal": True,
             "why": "explicit 0/0 equals the omitted optional drivers; makes the documented "
                    "default falsifiable"},
            {"id": "OBS-REVISION-POS", "kind": "set_driver_multi", "base_input": "positive",
             "value": {"reserve_revisions": [50], "closing_reserves": [950]},
             "why": "a positive revision keeps the balance (1000+100+50-200=950) and must not "
                    "change revenue: revisions enter the stock bridge only"},
            {"id": "OBS-RECOVERY-GT1", "kind": "set_driver", "driver": "recovery_rate",
             "value": [1.5], "base_input": "positive",
             "why": "records that recovery_rate keeps the ratio default bound [0, 1] "
                    "(it has no explicit driver_bounds entry)"},
        ],
        "observation_expected": {
            "OBS-BASE-IGNORED": {"expected_float": [float(v[0])]},
            "OBS-DEFAULT-EQUIV": {"expected_float": [float(d1[0])]},
            "OBS-REVISION-POS": {"expected_float": [float(r_pos[0])]},
            "OBS-RECOVERY-GT1": {"expected_raised": "ModelRegistryError"},
        },
    }


# --------------------------------------------------------------------------
# M11 infrastructure
# --------------------------------------------------------------------------
def m11():
    def infra(volume, tariff, other):
        return (Decimal(volume) * Decimal(tariff) + Decimal(other),
                "%s x %s + %s" % (volume, tariff, other))

    v, f = zip(*[infra(400, "0.5", 10)])
    c1 = infra(400, "0.5", 10)
    c2 = infra(500, "0.6", 0)
    d1 = infra(400, "0.5", 0)
    return {
        "model_id": "infrastructure",
        "first_required_driver": "billable_volume",
        "contract": contract_block(
            "revenue = billable_volume * tariff + other_revenue",
            ("billable_volume", "tariff"), ("other_revenue",),
            {"billable_volume": "activity", "tariff": "revenue_per_activity",
             "other_revenue": "revenue"},
            {"other_revenue": 0.0}),
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "infrastructure", "base_revenue": 0,
                "drivers": {"billable_volume": [400], "tariff": [0.5],
                            "other_revenue": [10]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "infrastructure", "base_revenue": 0,
                "drivers": {"billable_volume": [400, 500], "tariff": [0.5, 0.6],
                            "other_revenue": [10, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "infrastructure", "base_revenue": 0,
                "drivers": {"billable_volume": [400], "tariff": [0.5]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "billable_volume",
            _case("NEG-CARD", "set_driver_element", "positive", "billable_volume", 0,
                  {"__float__": "-1"},
                  guard_hint="driver value-domain guard: activity default bound [0, inf)"),
            _case("CONT-BREAK", "set_years", "continuity_positive", None, None,
                  [2027, 2029],
                  guard_hint="fiscal-year consecutiveness guard"),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the rowwise calculator discards base_revenue; design observation only"},
            {"id": "OBS-TARIFF-NEG", "kind": "set_driver", "driver": "tariff",
             "value": [-1], "base_input": "positive",
             "why": "records whether a negative tariff is expressible; the driver-domain guard "
                    "runs before the calculator, so the recorded message shows which guard fires "
                    "first (a negative total would also be refused)"},
        ],
        "observation_expected": {
            "OBS-BASE-IGNORED": {"expected_float": [float(v[0])]},
            "OBS-TARIFF-NEG": {"expected_raised": "ModelRegistryError"},
        },
    }


# --------------------------------------------------------------------------
# M12 bank_revenue
# --------------------------------------------------------------------------
def m12():
    def bank(aea, ay, aibl, fc, fee, other):
        gross = Decimal(aea) * Decimal(ay)
        cost = Decimal(aibl) * Decimal(fc)
        return (gross - cost + Decimal(fee) + Decimal(other),
                "%s x %s - %s x %s + %s + %s" % (aea, ay, aibl, fc, fee, other))

    v, f = zip(*[bank(1000, "0.04", 800, "0.02", 8, 2)])
    c1 = bank(1000, "0.04", 800, "0.02", 8, 2)
    c2 = bank(1200, "0.045", 1000, "0.025", 9, 0)
    d1 = bank(1000, "0.04", 800, "0.02", 8, 0)
    neg_rate_ok = bank(1000, "-0.01", 0, 0, 8, 2)
    fee_signed = bank(1000, "0.04", 800, "0.02", -5, 2)
    rate_gt1 = bank(1000, "0.5", 800, "0.02", 8, 2)
    return {
        "model_id": "bank_revenue",
        "first_required_driver": "average_earning_assets",
        "contract": contract_block(
            "revenue = average_earning_assets * asset_yield - "
            "average_interest_bearing_liabilities * funding_cost + fee_revenue + other_revenue",
            ("average_earning_assets", "asset_yield",
             "average_interest_bearing_liabilities", "funding_cost", "fee_revenue"),
            ("other_revenue",),
            {"average_earning_assets": "monetary_balance", "asset_yield": "ratio",
             "average_interest_bearing_liabilities": "monetary_balance",
             "funding_cost": "ratio", "fee_revenue": "revenue",
             "other_revenue": "revenue"},
            {"other_revenue": 0.0}),
        "positive": expected_block([2027], list(v), list(f)),
        "continuity_positive": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults": expected_block([2027], [d1[0]], [d1[1]]),
        "input": {
            "positive": {
                "model_id": "bank_revenue", "base_revenue": 0,
                "drivers": {"average_earning_assets": [1000], "asset_yield": [0.04],
                            "average_interest_bearing_liabilities": [800],
                            "funding_cost": [0.02], "fee_revenue": [8],
                            "other_revenue": [2]},
                "years": [2027],
            },
            "continuity_positive": {
                "model_id": "bank_revenue", "base_revenue": 0,
                "drivers": {"average_earning_assets": [1000, 1200],
                            "asset_yield": [0.04, 0.045],
                            "average_interest_bearing_liabilities": [800, 1000],
                            "funding_cost": [0.02, 0.025], "fee_revenue": [8, 9],
                            "other_revenue": [2, 0]},
                "years": [2027, 2028],
            },
            "defaults": {
                "model_id": "bank_revenue", "base_revenue": 0,
                "drivers": {"average_earning_assets": [1000], "asset_yield": [0.04],
                            "average_interest_bearing_liabilities": [800],
                            "funding_cost": [0.02], "fee_revenue": [8]},
                "years": [2027],
            },
        },
        "cases": common_cases(
            "average_earning_assets",
            _case("NEG-CARD", "set_driver_multi", "positive", None, None,
                  {"asset_yield": [0], "funding_cost": [0.1], "fee_revenue": [0],
                   "other_revenue": [0]},
                  guard_hint="totals guard: 0 - 80 + 0 + 0 = -80 < 0 (NOT a rate-domain refusal)"),
            _case("CONT-BREAK", "set_years", "continuity_positive", None, None,
                  [2027, 2029],
                  guard_hint="fiscal-year consecutiveness guard"),
        ),
        "observations": [
            {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
             "base_input": "positive", "compare_to": "positive", "expect_equal": True,
             "why": "the rowwise calculator discards base_revenue; design observation only"},
            {"id": "OBS-NEG-RATE-ACCEPTED", "kind": "set_driver_multi", "base_input": "positive",
             "value": {"asset_yield": [-0.01],
                       "average_interest_bearing_liabilities": [0], "funding_cost": [0]},
             "why": "negative interest rates must be ACCEPTED (card L48); the total is exactly "
                    "0 here, which is not negative, so nothing else binds"},
            {"id": "OBS-NEG-RATE-TOTAL-NEG", "kind": "set_driver", "driver": "asset_yield",
             "value": [-0.01], "base_input": "positive",
             "why": "same negative rate but the total is -16: proves the binding guard is the "
                    "revenue-total guard, not a 0-1 rate restriction"},
            {"id": "OBS-FEE-SIGNED", "kind": "set_driver", "driver": "fee_revenue",
             "value": [-5], "base_input": "positive",
             "why": "fee_revenue is a signed driver, so a negative net fee can be expressed"},
            {"id": "OBS-RATE-GT1", "kind": "set_driver", "driver": "asset_yield",
             "value": [0.5], "base_input": "positive",
             "why": "the ratio dimension default bound [0, 1] does NOT apply to asset_yield; "
                    "a yield above 1 must be accepted"},
        ],
        "observation_expected": {
            "OBS-BASE-IGNORED": {"expected_float": [float(v[0])]},
            "OBS-NEG-RATE-ACCEPTED": {"expected_float": [float(neg_rate_ok[0])]},
            "OBS-NEG-RATE-TOTAL-NEG": {"expected_raised": "ModelRegistryError"},
            "OBS-FEE-SIGNED": {"expected_float": [float(fee_signed[0])]},
            "OBS-RATE-GT1": {"expected_float": [float(rate_gt1[0])]},
        },
    }


BUILDERS = {"M09": m09, "M10": m10, "M11": m11, "M12": m12}


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

    cases = data["cases"]

    input_doc = dict(data["input"])
    input_doc["card_id"] = card
    input_doc["model_id"] = data["model_id"]

    cases_doc = {
        "card_id": card,
        "model_id": data["model_id"],
        "first_required_driver": data["first_required_driver"],
        "independent_deepcopy_per_case": True,
        "continuity_first_positive": "continuity_positive",
        "continuity_then_break_order": [
            "run continuity_positive and check it against oracle.continuity_positive",
            "only then apply the CONT-BREAK patch to a fresh deepcopy of continuity_positive",
        ],
        "cases": cases,
        "extra_observations": data["observations"],
    }

    oracle = {
        "card_id": card,
        "model_id": data["model_id"],
        "generated_by": "scripts/oracle_cards_M09_M12.py --card %s (stdlib only, no product import)" % card,
        "contract": data["contract"],
        "positive": data["positive"],
        "continuity_positive": data["continuity_positive"],
        "defaults": data["defaults"],
        "defaults_expected_float": data["defaults"]["expected_float"],
        "observation_expected": data["observation_expected"],
        "negative_count": len(cases),
        "negative_ids": [c["id"] for c in cases],
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
        "structure_rule": (
            "positive output must be a builtin list whose length equals len(years), whose elements "
            "are all float instances and all finite, and the registry contract (formula string, "
            "required set, optional set, dimensions) must equal oracle.contract"),
    }

    def dump(name, doc):
        path = os.path.join(target, name)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(doc, handle, ensure_ascii=False, indent=1)
            handle.write("\n")
        return path

    dump("input.json", input_doc)
    dump("cases.json", cases_doc)
    dump("oracle.json", oracle)
    dump("observation_expected.json", {"card_id": card,
                                      "observation_expected": data["observation_expected"]})

    with open(__file__, "rb") as handle:
        script_bytes = handle.read()
    script_sha = hashlib.sha256(script_bytes).hexdigest()
    import_lines = [line.strip() for line in script_bytes.decode("utf-8").splitlines()
                    if line.startswith("import ") or line.startswith("from ")]
    selfcheck = {
        "card_id": card,
        "script": "scripts/oracle_cards_M09_M12.py",
        "script_path_relative_to": "attempt root (this file is a byte-identical copy of that generator)",
        "script_sha256": script_sha,
        "rule": "the oracle generator must not import the product under test",
        "forbidden_tokens": list(PRODUCT_MODULE_TOKENS),
        "import_lines": import_lines,
        "product_import_present": any(
            token in line for token in PRODUCT_MODULE_TOKENS for line in import_lines),
        "expected_values_source": "hand arithmetic transcribed in oracle.md (see oracle.<block>.hand_work)",
        "product_entry_point_not_used": "calculate_registered_model was NOT called to produce any expectation",
    }
    dump("oracle_selfcheck.json", selfcheck)

    print("card", card, "model", data["model_id"])
    print("positive expected", data["positive"]["expected"],
          "tolerances", data["positive"]["tolerances"])
    print("continuity expected", data["continuity_positive"]["expected"])
    print("defaults expected", data["defaults"]["expected"])
    print("contract formula", data["contract"]["formula"])
    print("contract required", data["contract"]["required"])
    print("contract optional", data["contract"]["optional"])
    print("negative cases", len(cases), [c["id"] for c in cases])
    print("observation_expected", sorted(data["observation_expected"]))
    print("oracle_selfcheck product_import_present =", selfcheck["product_import_present"])
    for name in ("input.json", "oracle.json", "cases.json", "observation_expected.json",
                 "oracle_selfcheck.json"):
        with open(os.path.join(target, name), "rb") as handle:
            print("wrote", name, "sha256", hashlib.sha256(handle.read()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
