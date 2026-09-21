#!/usr/bin/env python3
"""I-10-B — frozen-expectation impact scan.

Question the card text asks, verbatim: for every bound change, WHICH M-card
case, if any, is affected?

Method: walk every M-card artefact tree under the history audit, load every
JSON file, and look for any occurrence of a changed (model, driver) pair in a
position that could carry an input value or a frozen expectation. Classify each
hit:
  * CASE_TARGET   the changed driver is the `driver` of a negative/mutation case
                  -> widening the lower bound could flip a PASS_rejected
  * VALUE_BEARING the changed driver carries a numeric array somewhere
                  -> if that array holds a negative number, its expected result
                     could move
  * REFERENCE_ONLY the name appears without a numeric payload (prose, hash table,
                  enumeration list) -> no behavioural coupling
Anything that is neither CASE_TARGET nor VALUE_BEARING-with-negatives is
provably unaffected, because the bound only gates values it never sees.
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent
ROOT = RUN.parent.parent  # execution_runs/

CHANGED = [
    ("cohort_subscription", "usage_revenue"),
    ("retail_franchise", "franchise_system_sales"),
    ("retail_franchise", "supply_revenue"),
    ("subscription", "usage_revenue"),
    ("subscription_arr_bridge", "usage_revenue"),
]
CHANGED_DRIVERS = sorted({d for _, d in CHANGED})
DRIVER_OF_MODEL = defaultdict(set)
for mdl, drv in CHANGED:
    DRIVER_OF_MODEL[mdl].add(drv)

NEG = re.compile(r'"value"\s*:\s*(-\d|\[\s*-)|__float__"\s*:\s*"-')

report = {
    "run": "I-10-B",
    "attempt": "a20260919-01",
    "changed_cells": [{"model": a, "driver": b} for a, b in CHANGED],
    "changed_drivers": CHANGED_DRIVERS,
}

case_targets = []
value_bearing = []
reference_only = []

scanned = 0
for mdir in sorted(ROOT.iterdir()):
    if not mdir.is_dir() or not re.fullmatch(r"M\d\d", mdir.name):
        continue
    for f in sorted(mdir.rglob("*.json")):
        try:
            txt = f.read_text(encoding="utf-8")
        except Exception:
            continue
        scanned += 1
        hits = [d for d in CHANGED_DRIVERS if d in txt]
        if not hits:
            continue
        rel = str(f.relative_to(ROOT))
        try:
            data = json.loads(txt)
        except Exception:
            reference_only.append({"file": rel, "reason": "unparseable"})
            continue

        # walk every dict; look for {'driver': <changed>, ...}
        found = {"case": False, "value": False, "neg": False}

        def walk(node):
            if isinstance(node, dict):
                drv = node.get("driver")
                if drv in CHANGED_DRIVERS:
                    found["case"] = True
                    v = node.get("value")
                    s = json.dumps(v, ensure_ascii=False) if v is not None else ""
                    if NEG.search('"value": ' + s):
                        found["neg"] = True
                for k, v in node.items():
                    if k in CHANGED_DRIVERS:
                        found["value"] = True
                        if isinstance(v, list) and any(
                            isinstance(x, (int, float)) and x < 0 for x in v
                        ):
                            found["neg"] = True
                        if isinstance(v, (int, float)) and v < 0:
                            found["neg"] = True
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(data)

        if found["case"]:
            case_targets.append({"file": rel, "drivers": hits, "negative_value": found["neg"]})
        elif found["value"]:
            value_bearing.append({"file": rel, "drivers": hits, "negative_value": found["neg"]})
        else:
            reference_only.append({"file": rel, "drivers": hits})

report["files_scanned"] = scanned
report["CASE_TARGET"] = case_targets
report["VALUE_BEARING"] = value_bearing
report["REFERENCE_ONLY_count"] = len(reference_only)
report["REFERENCE_ONLY"] = reference_only

report["verdict"] = {
    "case_targets": len(case_targets),
    "value_bearing_with_negative": sum(1 for v in value_bearing if v["negative_value"]),
    "any_frozen_expectation_affected": bool(
        case_targets or any(v["negative_value"] for v in value_bearing)
    ),
}

(RUN / "frozen_impact_scan.json").write_text(
    json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
)

print("files scanned:", scanned)
print("CASE_TARGET:", len(case_targets))
for c in case_targets:
    print("   ", c)
print("VALUE_BEARING:", len(value_bearing))
for v in value_bearing:
    print("   ", v)
print("REFERENCE_ONLY:", len(reference_only))
print()
print("VERDICT:", json.dumps(report["verdict"], ensure_ascii=False))
