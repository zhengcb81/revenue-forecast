"""Claim 5 — row-by-row: the r3+r4 rows must be unchanged on the r5 tree."""
import json, os, sys

S = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_review_i14d_r5_20260922\scratch"

def load(p):
    return json.load(open(os.path.join(S, p), encoding="utf-8"))

def rows_of(d):
    for k in ("rows", "cases", "results", "entries_detail"):
        if k in d and isinstance(d[k], list):
            return d[k]
    return None

pairs = [
    ("r4 oracle  (r3+r4 rows)", "r4oracle_on_product_narrow_r4.json", "r4oracle_on_product_narrow_r5.json"),
    ("r4 rule    (r3+r4 rows)", "r4rule_on_product_narrow_r4.json",   "r4rule_on_product_narrow_r5.json"),
    ("r3 oracle  (r3 rows)",    "r3oracle_on_product_narrow_r3.json", "r3oracle_on_product_narrow_r5.json"),
    ("r3 rule    (r3 rows)",    "r3rule_on_product_narrow_r3.json",   "r3rule_on_product_narrow_r5.json"),
    ("r5 oracle  (r4 rows only)","r5oracle_on_product_narrow_r4.json","r5oracle_on_product_narrow_r5.json"),
    ("r5 rule    (r4 rows only)","r5rule_on_product_narrow_r4.json",  "r5rule_on_product_narrow_r5.json"),
]
for label, pa, pb in pairs:
    a = load(pa); b = load(pb)
    ra = rows_of(a); rb = rows_of(b)
    if ra is None or rb is None:
        print(f"{label}: no row list found; keys a={list(a.keys())} keys b={list(b.keys())}")
        continue
    ia = [r.get("id") for r in ra]; ib = [r.get("id") for r in rb]
    common = [i for i in ia if i in set(ib)]
    diff = []
    for r in ra:
        if r.get("id") in set(ib):
            r2 = next(x for x in rb if x.get("id") == r["id"])
            if r != r2:
                diff.append((r["id"], r, r2))
    print(f"{label}: rows r4tree={len(ra)} r5tree={len(rb)}  common={len(common)}  differing={len(diff)}"
          f"  order_preserved={ia == [i for i in ib if i in set(ia)]}")
    for d in diff[:10]:
        print("   DIFF", d[0])
        print("      on r4 tree:", json.dumps(d[1], ensure_ascii=False)[:300])
        print("      on r5 tree:", json.dumps(d[2], ensure_ascii=False)[:300])
    onlyb = [i for i in ib if i not in set(ia)]
    if onlyb:
        print("   rows present only on the r5 tree (the new r5 rows):", onlyb)
