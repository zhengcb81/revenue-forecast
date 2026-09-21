"""Reviewer re-derivation of the 347-case claim + M05-M08 rename blast radius."""
import glob
import json
import os
import re

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
total = 0
compound = []
missing = []
nonstring = []
declared = {}
per_card = {}
for card_dir in sorted(glob.glob(os.path.join(PLAN, "execution_runs", "M*"))):
    card = os.path.basename(card_dir)
    if not re.fullmatch(r"M\d\d", card):
        continue
    hits = glob.glob(os.path.join(card_dir, "*", "evidence", card, "cases.json"))
    for h in hits:
        d = json.load(open(h, encoding="utf-8"))
        cases = d.get("cases", [])
        per_card[card] = len(cases)
        for c in cases:
            total += 1
            v = c.get("expected")
            if not isinstance(v, str):
                nonstring.append((card, c.get("id"), v))
            elif not v.strip():
                missing.append((card, c.get("id")))
            elif "/" in v or "," in v or "|" in v:
                compound.append((card, c.get("id"), v))
            else:
                declared[v] = declared.get(v, 0) + 1
print("total cases across the 31 frozen cases.json:", total)
print("distinct declared `expected` values:", declared)
print("compound values:", compound)
print("missing/blank:", missing)
print("non-string:", nonstring)
print("per-card counts:", json.dumps(per_card, sort_keys=True))
print()
print("M05-M08 rename blast radius: does the historical M05-M08 runner emit expectation_consistency?")
for card in ("M05", "M06", "M07", "M08"):
    p = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card,
                     "run_result.json")
    d = json.load(open(p, encoding="utf-8"))
    facts = (d.get("expectation_consistency") or {}).get("facts")
    print("  %s expectation_consistency.facts = %s" % (card, facts))
