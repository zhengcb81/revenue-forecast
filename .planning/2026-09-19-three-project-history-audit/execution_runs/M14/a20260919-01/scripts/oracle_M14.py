"""Independent oracle generator for card M14 (retail_franchise) - standard library only.

Hard independence rule: this file NEVER imports model_registry, model_extensions or any other
product module. Every number below is plain decimal arithmetic derived from the card text (see
oracle.md sections 1-5), never from the product.

Writes into <out-root>/evidence/M14:
  input.json             frozen positive / continuity_positive / defaults inputs
  cases.json             negative cases (card-specific + N01-N05 + continuity break)
                         plus the non-gating extra observations
  oracle.json            frozen expected values, tolerances, expected output shape
  oracle_selfcheck.json  proof that this generator does not import the product, plus the
                         freeze-time sha256 of the three frozen files

Run (attempt-local isolated interpreter, ASCII-only console output):
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B <attempt>/scripts/oracle_M14.py ^
      --out-root <attempt>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from decimal import Decimal, getcontext

getcontext().prec = 50

CARD = "M14"
MODEL_ID = "retail_franchise"
FIRST_REQUIRED_DRIVER = "average_owned_stores"
TOL = Decimal("1e-9")
PRODUCT_MODULE_TOKENS = ("model_registry", "model_extensions", "revenue_core", "revenue_forecast")


def tol_for(expected):
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


# Frozen refusal rationale. Sources: card_M14.md, common_model_cards.md L26-30 and this card's
# oracle.md sections 5 and 8.
WHY = {
    "NEG-CARD": "card-specific negative (card_M14.md L41): the recognised franchise fee rate leaves the ratio domain",
    "N01a": "common negative N01a: bool is not a numeric driver value",
    "N01b": "common negative N01b: non-finite value nan",
    "N01c": "common negative N01c: non-finite value inf",
    "N01d": "common negative N01d: non-finite value -inf",
    "N02": "common negative N02: first required driver array is empty, so its length != len(years)",
    "N03": "common negative N03: first required driver deleted (missing required field)",
    "N04": "common negative N04: unknown_driver added (unsupported driver)",
    "N05a": "common negative N05a: years = [] (fiscal-year domain)",
    "N05b": "common negative N05b: first year replaced by True (True is not a fiscal year)",
    "CONT-BREAK": "continuity break for this card: non-consecutive fiscal years (oracle.md section 4)",
}


def build():
    # revenue = average_owned_stores * revenue_per_owned_store
    #         + franchise_system_sales * recognized_fee_rate + supply_revenue
    def revenue(stores, per_store, system_sales, fee_rate, supply):
        total = (Decimal(stores) * Decimal(per_store)
                 + Decimal(system_sales) * Decimal(fee_rate) + Decimal(supply))
        return total, "%s x %s + %s x %s + %s" % (stores, per_store, system_sales, fee_rate, supply)

    p1 = revenue(10, 5, 200, "0.04", 7)
    c1 = revenue(10, 5, 200, "0.04", 7)
    c2 = revenue(12, "5.5", 240, "0.045", 8)
    d1 = revenue(10, 5, 0, 0, 0)
    o_incl = revenue(10, 5, 200, "1", 7)

    positive = {
        "model_id": MODEL_ID,
        "base_revenue": 0,
        "drivers": {"average_owned_stores": [10], "revenue_per_owned_store": [5],
                    "franchise_system_sales": [200], "recognized_fee_rate": [0.04],
                    "supply_revenue": [7]},
        "years": [2027],
    }
    continuity_positive = {
        "model_id": MODEL_ID,
        "base_revenue": 0,
        "drivers": {"average_owned_stores": [10, 12], "revenue_per_owned_store": [5, 5.5],
                    "franchise_system_sales": [200, 240], "recognized_fee_rate": [0.04, 0.045],
                    "supply_revenue": [7, 8]},
        "years": [2027, 2028],
    }
    defaults = {
        "model_id": MODEL_ID,
        "base_revenue": 0,
        "drivers": {"average_owned_stores": [10], "revenue_per_owned_store": [5]},
        "years": [2027],
    }

    cases = [
        {"id": "NEG-CARD", "kind": "set_driver_element", "base_input": "positive",
         "driver": "recognized_fee_rate", "index": 0, "value": {"__float__": 1.1},
         "expected": "ModelRegistryError", "why": WHY["NEG-CARD"]},
        {"id": "N01a", "kind": "set_driver_element", "base_input": "positive",
         "driver": FIRST_REQUIRED_DRIVER, "index": 0, "value": {"__bool__": True},
         "expected": "ModelRegistryError", "why": WHY["N01a"]},
        {"id": "N01b", "kind": "set_driver_element", "base_input": "positive",
         "driver": FIRST_REQUIRED_DRIVER, "index": 0, "value": {"__float__": "nan"},
         "expected": "ModelRegistryError", "why": WHY["N01b"]},
        {"id": "N01c", "kind": "set_driver_element", "base_input": "positive",
         "driver": FIRST_REQUIRED_DRIVER, "index": 0, "value": {"__float__": "inf"},
         "expected": "ModelRegistryError", "why": WHY["N01c"]},
        {"id": "N01d", "kind": "set_driver_element", "base_input": "positive",
         "driver": FIRST_REQUIRED_DRIVER, "index": 0, "value": {"__float__": "-inf"},
         "expected": "ModelRegistryError", "why": WHY["N01d"]},
        {"id": "N02", "kind": "set_driver", "base_input": "positive",
         "driver": FIRST_REQUIRED_DRIVER, "value": [],
         "expected": "ModelRegistryError", "why": WHY["N02"]},
        {"id": "N03", "kind": "delete_driver", "base_input": "positive",
         "driver": FIRST_REQUIRED_DRIVER,
         "expected": "ModelRegistryError", "why": WHY["N03"]},
        {"id": "N04", "kind": "add_driver", "base_input": "positive",
         "driver": "unknown_driver", "value": [1],
         "expected": "ModelRegistryError", "why": WHY["N04"]},
        {"id": "N05a", "kind": "set_years", "base_input": "positive", "value": [],
         "expected": "ModelRegistryError", "why": WHY["N05a"]},
        {"id": "N05b", "kind": "set_years", "base_input": "positive",
         "value": {"__bool__first__": True},
         "expected": "ModelRegistryError", "why": WHY["N05b"]},
        {"id": "CONT-BREAK", "kind": "set_years", "base_input": "continuity_positive",
         "value": [2027, 2029],
         "expected": "ModelRegistryError",
         "why": "continuity break for this card: FY2028 is missing, so the years are not "
                "consecutive (the two-year positive is run first)"},
    ]

    observations = [
        {"id": "OBS-BASE-IGNORED", "kind": "set_base_revenue", "value": 999,
         "base_input": "positive", "compare_to": "positive", "expect_equal": True,
         "why": "the rowwise calculator discards base_revenue; design observation only, "
                "not a pass condition"},
        {"id": "OBS-BOUND-INCLUSIVE", "kind": "set_driver_element", "driver": "recognized_fee_rate",
         "index": 0, "value": {"__float__": 1.0}, "base_input": "positive",
         "why": "the ratio domain is INCLUSIVE at the upper edge: 1.0 is accepted while "
                "NEG-CARD's 1.1 is refused; records the edge, does not gate"},
        {"id": "OBS-SUPPLY-BOUND", "kind": "set_driver_element", "driver": "supply_revenue",
         "index": 0, "value": {"__float__": -1}, "base_input": "positive",
         "why": "supply_revenue is NOT a signed driver in this registry, so a negative supply "
                "sale is refused by the driver bound (lower bound 0.0) rather than by the "
                "non-negative-revenue check; records the contract boundary, does not gate"},
    ]

    return {
        "positive": positive,
        "continuity_positive": continuity_positive,
        "defaults": defaults,
        "positive_expected": expected_block([2027], [p1[0]], [p1[1]]),
        "continuity_expected": expected_block([2027, 2028], [c1[0], c2[0]], [c1[1], c2[1]]),
        "defaults_expected": expected_block([2027], [d1[0]], [d1[1]]),
        "observation_expected": {
            "OBS-BOUND-INCLUSIVE": expected_block([2027], [o_incl[0]], [o_incl[1]]),
        },
        "cases": cases,
        "observations": observations,
        "expected_output_shape": {
            "positive": {"container": "list", "length": 1, "element_type": "float",
                         "all_finite": True, "years": [2027]},
            "continuity_positive": {"container": "list", "length": 2, "element_type": "float",
                                    "all_finite": True, "years": [2027, 2028]},
            "defaults": {"container": "list", "length": 1, "element_type": "float",
                         "all_finite": True, "years": [2027]},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True)
    args = parser.parse_args()

    data = build()
    target = os.path.join(args.out_root, "evidence", CARD)
    os.makedirs(target, exist_ok=True)

    input_doc = {"card_id": CARD,
                 "positive": data["positive"],
                 "continuity_positive": data["continuity_positive"],
                 "defaults": data["defaults"]}
    cases_doc = {"card_id": CARD,
                 "first_required_driver": FIRST_REQUIRED_DRIVER,
                 "independent_deepcopy_per_case": True,
                 "continuity_first_positive": "continuity_positive",
                 "cases": data["cases"],
                 "extra_observations": data["observations"]}
    oracle_doc = {
        "card_id": CARD,
        "model_id": MODEL_ID,
        "generated_by": "scripts/oracle_%s.py (standard library only, no product import)" % CARD,
        "positive": data["positive_expected"],
        "continuity_positive": data["continuity_expected"],
        "defaults": data["defaults_expected"],
        "defaults_expected_float": data["defaults_expected"]["expected_float"],
        "observation_expected": data["observation_expected"],
        "negative_count": len(data["cases"]),
        "negative_ids": [case["id"] for case in data["cases"]],
        "expected_output_shape": data["expected_output_shape"],
        "tolerance_rule": "abs(actual-expected) <= 1e-9 * max(1, abs(expected))",
        "fidelity_rule": "container=list, length=len(years)=frozen length, element_type=float, "
                         "all elements finite, years equal to the frozen years",
    }

    def dump(name, doc):
        path = os.path.join(target, name)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(doc, handle, ensure_ascii=True, indent=1)
            handle.write("\n")
        return path

    dump("input.json", input_doc)
    dump("cases.json", cases_doc)
    dump("oracle.json", oracle_doc)

    with open(__file__, "rb") as handle:
        payload = handle.read()
    script_sha = hashlib.sha256(payload).hexdigest()
    import_lines = [line.strip() for line in payload.decode("utf-8").splitlines()
                    if line.startswith("import ") or line.startswith("from ")]
    frozen = {}
    for name in ("input.json", "cases.json", "oracle.json"):
        with open(os.path.join(target, name), "rb") as handle:
            frozen["evidence/%s/%s" % (CARD, name)] = hashlib.sha256(handle.read()).hexdigest()
    selfcheck = {
        "card_id": CARD,
        "script": os.path.abspath(__file__),
        "script_sha256": script_sha,
        "rule": "the oracle generator must not import the product under test",
        "forbidden_tokens": list(PRODUCT_MODULE_TOKENS),
        "import_lines": import_lines,
        "product_import_present": any(token in line for token in PRODUCT_MODULE_TOKENS
                                      for line in import_lines),
        "expected_values_origin": "hand decimal arithmetic written into this file from the card "
                                 "text; no product call is made anywhere in this generator",
        "frozen_file_sha256_at_freeze_time": frozen,
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    dump("oracle_selfcheck.json", selfcheck)

    print("card %s model %s" % (CARD, MODEL_ID))
    print("positive expected %s tolerances %s"
          % (data["positive_expected"]["expected"], data["positive_expected"]["tolerances"]))
    print("continuity expected %s" % data["continuity_expected"]["expected"])
    print("defaults expected %s" % data["defaults_expected"]["expected"])
    print("observation expected %s"
          % {k: v["expected"] for k, v in data["observation_expected"].items()})
    print("negative cases %d %s" % (len(data["cases"]), [c["id"] for c in data["cases"]]))
    print("frozen_file_sha256 %s" % frozen)
    print("oracle_selfcheck product_import_present = %s" % selfcheck["product_import_present"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
