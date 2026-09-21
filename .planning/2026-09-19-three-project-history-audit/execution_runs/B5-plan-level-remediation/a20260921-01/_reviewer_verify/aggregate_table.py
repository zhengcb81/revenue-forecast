"""Reviewer aggregate table: per-batch arms (as recorded) + implementation status."""
import json
import os

ATTEMPT = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
           r"\2026-09-19-three-project-history-audit\execution_runs"
           r"\B5-plan-level-remediation\a20260921-01")
BATCHES = ["M05-M08", "M09-M12", "M13-M16", "M21-M24", "M25-M28", "M29-M31"]
intended = {"M05-M08": "no gate", "M09-M12": "already gates (exact name)",
            "M13-M16": "set-level gap check only", "M21-M24": "already gates (exact name)",
            "M25-M28": "whole-set case_contract gate only", "M29-M31": "no gate"}
print("%-9s %-30s %-4s %-4s %-5s %-4s %-14s %-12s" %
      ("batch", "contract-intended-state", "E", "F", "B", "G", "mutated", "B semantics"))
for b in BATCHES:
    ev = json.load(open(os.path.join(ATTEMPT, b, "evidence.json"), encoding="utf-8"))
    a = ev["arms"]
    print("%-9s %-30s %-4s %-4s %-5s %-4s %-14s %-12s" % (
        b, intended[b], a["E"].get("rc"), a["F"].get("rc"), a["B"].get("rc"),
        a["G"].get("rc"), a["F"].get("mutated_case"),
        {"M05-M08": "not gated", "M09-M12": "ALREADY GATED", "M21-M24": "ALREADY GATED",
         "M25-M28": "3rd gate: rc=1"}.get(b, "?")))
    for arm in ("E", "F", "B", "G"):
        rec = a[arm]
        per = rec.get("rc_per_card") or {}
        vals = sorted(set(per.values())) if per else [rec.get("rc")]
        if len(vals) > 1:
            print("    !! %s rc_per_card not uniform: %s" % (arm, per))
print()
print("Contract section 5 predictions: E=0, F=3, B=0(predicted), G=2")
print()
for b in BATCHES:
    ev = json.load(open(os.path.join(ATTEMPT, b, "evidence.json"), encoding="utf-8"))
    print("%-9s cards=%s" % (b, ",".join(ev["cards"])))
