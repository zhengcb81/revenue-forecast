"""Scratch-only helper that materialises the mutated copies used by the exit-code
self-check (the "mutation proof").  It NEVER writes to the frozen evidence tree.

For each card it builds, under recovery/selfcheck/cases/<CASE>/evidence/<CARD>/:
  input.json, cases.json, oracle.json
where exactly ONE thing is mutated per case:

  A  oracle.json positive.expected_float -> [999.0]
     (a corrupted expectation must not hide behind rc=0)
  B  oracle.json positive.expected_float -> my own NAIVE arithmetic
     (a wrong hand computation must not hide behind rc=0 either)
  C  nothing mutated (the green control)
  D  frozen files + case_D_override.json: NEG-CARD's mutation is replaced by the
     identity value, so the model must ACCEPT it and the verdict must go red
  E  oracle.json positive.expected_float -> the MIS-SIGNED variant from
     naive_oracle.py --sign -1 (M28 only; for M25/M26/M27 the same mechanism is
     exercised with a deliberately wrong magnitude)

Run:
  python -X utf8 -B recovery/selfcheck/make_mutations.py --card M25 --attempt <attempt_root>
"""

from __future__ import annotations

import argparse
import copy
import json
import os

# The naive/mis-signed expectations planted by cases B and E.  They are MY arithmetic
# (never the product's output) and are deliberately different from the frozen values.
# Hand work for the planted variants:
#   M25: sign slip - adding the retirement term instead of subtracting it gives
#        (200 + 40*0.25 + 20*0.5) * 0.5 * 3 = (200 + 10 + 10) * 1.5 = 330.0
#   M26: sign slip - dropping the closure loss gives (20 - 2 + 1.5) * 10 = 195.0
#   M27: double count - adding other_revenue twice gives 262800 + 1200 + 1200 = 265200.0
#   M28: sign slip - treating the printed -50 as a magnitude to subtract gives
#        1050*0.01 + 2 = 12.5
NAIVE = {
    "M25": 330.0,
    "M26": 195.0,
    "M27": 265200.0,
    "M28": 12.5,
}


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    frozen = os.path.join(args.attempt, "evidence", args.card)
    scratch = os.path.join(args.attempt, "recovery", "selfcheck")
    input_doc = load(os.path.join(frozen, "input.json"))
    oracle_doc = load(os.path.join(frozen, "oracle.json"))
    cases_doc = load(os.path.join(frozen, "cases.json"))
    frozen_positive = list(oracle_doc["positive"]["expected_float"])
    naive = NAIVE[args.card]

    def plant(value):
        doc = copy.deepcopy(oracle_doc)
        doc["positive"]["expected"] = [str(value)]
        doc["positive"]["expected_float"] = [float(value)]
        doc["positive"]["tolerances"] = [1e-9 * max(1.0, abs(float(value)))]
        return doc

    variants = {
        "A": plant(999.0),
        "B": plant(naive),
        "C": copy.deepcopy(oracle_doc),
        "D": copy.deepcopy(oracle_doc),
        "E": plant(naive),
    }
    # Case F (review finding P3-2): two corruptions of cases.json that a verdict-carrying
    # runner must notice - a rewritten `expected` declaration and a DELETED negative case.
    f1 = copy.deepcopy(cases_doc)
    for case in f1["cases"]:
        if case["id"] == "NEG-CARD":
            case["expected"] = "ValueError"
    f2 = copy.deepcopy(cases_doc)
    f2["cases"] = [c for c in f2["cases"] if c["id"] != "N04"]
    fmut = {"F1": f1, "F2": f2}

    for name, doc in variants.items():
        base = os.path.join(scratch, "cases", name, "evidence", args.card)
        dump(os.path.join(base, "input.json"), copy.deepcopy(input_doc))
        dump(os.path.join(base, "cases.json"), copy.deepcopy(cases_doc))
        dump(os.path.join(base, "oracle.json"), doc)
    for name, doc in fmut.items():
        base = os.path.join(scratch, "cases", name, "evidence", args.card)
        dump(os.path.join(base, "input.json"), copy.deepcopy(input_doc))
        dump(os.path.join(base, "cases.json"), doc)
        dump(os.path.join(base, "oracle.json"), copy.deepcopy(oracle_doc))

    first = cases_doc["first_required_driver"]
    identity = input_doc["positive"]["drivers"][first][0]
    d_override = [{"id": "NEG-CARD",
                   "set": {"kind": "set_driver_element", "driver": first, "index": 0,
                           "value": identity}}]
    dump(os.path.join(scratch, "case_D_override.json"), d_override)

    print("card", args.card)
    print("frozen positive expected_float:", frozen_positive)
    print("case A planted: [999.0]")
    print("case B/E planted naive value:", [naive])
    print("case D override (identity, must be accepted):", json.dumps(d_override))
    print("case F1: NEG-CARD expected declaration rewritten to 'ValueError'")
    print("case F2: the N04 negative case deleted (10 cases left)")
    print("scratch case trees under:", os.path.join(scratch, "cases"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
