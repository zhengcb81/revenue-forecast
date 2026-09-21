"""G4 evidence: is rc=2 ever emitted BECAUSE a negative was correctly rejected?

Scans every frozen historical run_result.json / formula_result.json for all 31 cards and
records (rc, verdict, positive raised, all negatives PASS_rejected).
"""
import glob
import json
import os
import re

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
rows = []
for card_dir in sorted(glob.glob(os.path.join(PLAN, "execution_runs", "M*"))):
    card = os.path.basename(card_dir)
    if not re.fullmatch(r"M\d\d", card):
        continue
    for pat in ("evidence/*/run_result.json", "evidence/*/formula_result.json"):
        for p in glob.glob(os.path.join(card_dir, "*", pat)):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            ecs = d.get("exit_code_semantics") or {}
            rc = ecs.get("exit_code", d.get("exit_code"))
            if rc is None:
                continue
            ns = d.get("negative_summary") or {}
            total, passed = ns.get("total"), ns.get("passed")
            pos = d.get("positive") or {}
            rows.append({"card": card, "file": os.path.relpath(p, PLAN),
                         "rc": rc, "verdict": d.get("verdict"),
                         "neg_total": total, "neg_passed": passed,
                         "positive_raised": pos.get("raised")})

# dedupe by (card, rc, verdict, neg_total, neg_passed, positive_raised)
uniq = []
seen = set()
for r in rows:
    k = (r["card"], r["rc"], str(r["verdict"]), r["neg_total"], r["neg_passed"],
         str(r["positive_raised"]))
    if k in seen:
        continue
    seen.add(k)
    uniq.append(r)

print("%-5s %-4s %-14s %-8s %-8s %s" % ("card", "rc", "verdict", "neg_tot", "neg_pass", "pos_raised"))
for r in uniq:
    print("%-5s %-4s %-14s %-8s %-8s %s" % (r["card"], r["rc"], str(r["verdict"])[:14],
                                            r["neg_total"], r["neg_passed"],
                                            str(r["positive_raised"])[:30]))
print()
print("distinct rc values observed across the 31 frozen cards:", sorted({r["rc"] for r in uniq}))
print()
print("rc==2 AND all negatives present and all PASS_rejected:")
hit = [r for r in uniq if r["rc"] == 2 and r["neg_total"] and r["neg_passed"] == r["neg_total"]]
for r in hit:
    print("   ", r)
print("   count =", len(hit))
print()
print("rc==0 AND all negatives PASS_rejected (the reference shape):")
hit0 = [r for r in uniq if r["rc"] == 0 and r["neg_total"] and r["neg_passed"] == r["neg_total"]]
for r in hit0[:12]:
    print("   ", r)
print("   count =", len(hit0))
