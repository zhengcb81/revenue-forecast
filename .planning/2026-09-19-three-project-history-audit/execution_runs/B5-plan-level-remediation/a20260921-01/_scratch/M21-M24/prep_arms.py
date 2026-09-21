"""Rebuild the four contract arms deterministically from the FROZEN evidence.

Single source of truth so the arms cannot drift. Every arm gets a fresh copy of the frozen
input.json / cases.json / oracle.json / negative_results.json; only then is the mutation applied.

Mutation target (contract section 5): "the FIRST negative case (lowest id) whose frozen
`expected` is `ModelRegistryError`". Two readings of "lowest id" are possible for these cards:

  * file order  -> 'NEG-CARD'   (the card-specific negative, and the id named in probe_expected)
  * ordinal min -> 'CONT-BREAK' ('-' is 0x2D, below the digits, so it sorts first)

Both readings are exercised: NEG-CARD in arms F/B/G, CONT-BREAK in the extra arms F2/B2.
"""

import collections
import json
import os
import shutil

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M21-M24")
CARDS = ("M21", "M22", "M23", "M24")
FILES = ("input.json", "cases.json", "oracle.json", "negative_results.json")

# arm -> (target case id, mutation kind)
ARMS = {
    "E": (None, "frozen"),
    "F": ("NEG-CARD", "mutate"),
    "B": ("NEG-CARD", "mutate"),
    "G": ("NEG-CARD", "delete"),
    "F2": ("CONT-BREAK", "mutate"),
    "B2": ("CONT-BREAK", "mutate"),
}


def frozen_dir(card):
    return os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card)


def main():
    report = {}
    for arm, (target, kind) in ARMS.items():
        for card in CARDS:
            dst = os.path.join(SCRATCH, arm, "evidence", card)
            os.makedirs(dst, exist_ok=True)
            for f in FILES:
                shutil.copy2(os.path.join(frozen_dir(card), f), os.path.join(dst, f))
            if target is None:
                report["%s/%s" % (arm, card)] = None
                continue
            p = os.path.join(dst, "cases.json")
            with open(p, encoding="utf-8") as h:
                d = json.load(h, object_pairs_hook=collections.OrderedDict)
            cases = {c["id"]: c for c in d["cases"]}
            c = cases[target]
            assert c.get("expected") == "ModelRegistryError", (arm, card, target, c.get("expected"))
            if kind == "mutate":
                c["expected"] = "ValueError"
            elif kind == "delete":
                del c["expected"]
            with open(p, "w", encoding="utf-8") as h:
                json.dump(d, h, ensure_ascii=False, indent=1)
            report["%s/%s" % (arm, card)] = target
            print("rebuilt %-3s %s  target=%s kind=%s" % (arm, card, target, kind))
    with open(os.path.join(SCRATCH, "arms_prep.json"), "w", encoding="utf-8") as h:
        json.dump(report, h, ensure_ascii=False, indent=1)
    print("wrote", os.path.join(SCRATCH, "arms_prep.json"))


if __name__ == "__main__":
    main()
