"""Claim 5/6/4: row-by-row comparison across trees and against recorded runs."""
import json
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
S = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_review_i14d_r4_20260922")
MEAS = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_r4_measure_20260922")


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def rows_by_id(d):
    return {r["id"]: r for r in d["rows"]}


print("=" * 78)
print("CLAIM 5a: the 28 r3 ORACLE rows, unchanged on the r4 tree?")
print("=" * 78)
a = load(S / "r3oracle_on_r3.json")
b = load(S / "r3oracle_on_r4.json")
print(f"r3 tree rows={len(a['rows'])}  r4 tree rows={len(b['rows'])}")
ra, rb = rows_by_id(a), rows_by_id(b)
print(f"same id set: {set(ra) == set(rb)}   same order: {[r['id'] for r in a['rows']] == [r['id'] for r in b['rows']]}")
diff = []
for k in ra:
    if ra[k] != rb[k]:
        diff.append(k)
        print(f"  DIFFERS {k}")
        for f in sorted(set(ra[k]) | set(rb[k])):
            if ra[k].get(f) != rb[k].get(f):
                print(f"     {f}: r3={ra[k].get(f)!r}  r4={rb[k].get(f)!r}")
print(f"rows with any field difference: {len(diff)}  -> {diff}")

print()
print("=" * 78)
print("CLAIM 5b: the 79 r3 RULE-TABLE rows, unchanged on the r4 tree?")
print("=" * 78)
a = load(S / "r3rule_on_r3.json")
b = load(S / "r3rule_on_r4.json")
print(f"r3 tree rows={len(a['rows'])}  r4 tree rows={len(b['rows'])}")
ra, rb = rows_by_id(a), rows_by_id(b)
print(f"same id set: {set(ra) == set(rb)}   same order: {[r['id'] for r in a['rows']] == [r['id'] for r in b['rows']]}")
diff = [k for k in ra if ra[k] != rb[k]]
print(f"rows with any field difference: {len(diff)}  -> {diff}")
for k in diff:
    for f in sorted(set(ra[k]) | set(rb[k])):
        if ra[k].get(f) != rb[k].get(f):
            print(f"   {k}.{f}: r3={ra[k].get(f)!r}  r4={rb[k].get(f)!r}")

print()
print("=" * 78)
print("Recorded r3 runs (scratch/) vs my re-run on the r3 tree")
print("=" * 78)
for rec, mine in (("scratch/oracle_r3.json", "r3oracle_on_r3.json"),
                  ("scratch/rule_r3.json", "r3rule_on_r3.json")):
    p = ATT / rec
    if not p.exists():
        print(f"  {rec}: MISSING")
        continue
    d1, d2 = load(p), load(S / mine)
    r1, r2 = rows_by_id(d1), rows_by_id(d2)
    d = [k for k in r1 if r1.get(k) != r2.get(k)]
    print(f"  {rec}: rows={len(r1)} vs {len(r2)}; ids equal={set(r1)==set(r2)}; differing rows={len(d)}")

print()
print("=" * 78)
print("Recorded r4 harness runs vs my re-run on the r4 tree")
print("=" * 78)
for rec, mine in (("oracle_r4_harness.json", "oracle_r4_on_r4.json"),
                  ("rule_r4_harness.json", None)):
    p = MEAS / rec
    if mine is None:
        print(f"  {rec}: (my run below)")
        continue
    d1, d2 = load(p), load(S / mine)
    r1, r2 = rows_by_id(d1), rows_by_id(d2)
    d = [k for k in r1 if r1.get(k) != r2.get(k)]
    print(f"  {rec}: rows={len(r1)} vs {len(r2)}; ids equal={set(r1)==set(r2)}; differing rows={len(d)}")

print()
print("=" * 78)
print("CLAIM 6: over-redaction family")
print("=" * 78)
for name, p in (("r3 rule on r3 tree", S / "r3rule_on_r3.json"),
                ("r3 rule on r4 tree", S / "r3rule_on_r4.json")):
    d = load(p)
    print(f"  {name}: over_redaction_rows={len(d['over_redaction_rows'])} "
          f"touched={len(d['over_redaction_touched'])}")
    print(f"     {d['over_redaction_rows']}")

d = load(MEAS / "rule_r4_harness.json")
print(f"  recorded r4 rule harness (83 rows): over_redaction_rows={len(d['over_redaction_rows'])}")
print(f"     {d['over_redaction_rows']}")

print()
print("=" * 78)
print("CLAIM 4: row counts and new-row ids")
print("=" * 78)
d = load(MEAS / "oracle_r4_harness.json")
ids = [r["id"] for r in d["rows"]]
print(f"  r4 oracle rows = {len(ids)}")
print(f"  new ids present: {[i for i in ids if i.startswith('N5l') or i.startswith('N5m') or i.startswith('N5n') or i.startswith('N5o')]}")
d = load(MEAS / "rule_r4_harness.json")
ids = [r["id"] for r in d["rows"]]
print(f"  r4 rule rows = {len(ids)}")
print(f"  new ids present: {[i for i in ids if 'question-mark' in i or 'nonletter' in i]}")
