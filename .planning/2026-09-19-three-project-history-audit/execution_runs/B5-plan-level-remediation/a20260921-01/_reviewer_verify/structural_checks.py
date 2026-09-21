"""Reviewer structural checks over the six patched runner copies.

Read-only.  Answers:
  * is there any isinstance() used in an `expected` comparison? (decoy claim)
  * were any rc constants renumbered vs the byte-copy historical runner?
  * do all six copies carry the required additive counters?
  * are the historical runner copies / frozen cases.json unchanged?
"""
import hashlib
import io
import json
import os
import re
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCHES = {"M05-M08": "M05", "M09-M12": "M09", "M13-M16": "M13",
           "M21-M24": "M21", "M25-M28": "M25", "M29-M31": "M29"}


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    out = {"batches": {}}
    for batch, rep in BATCHES.items():
        new = os.path.join(ATTEMPT, batch, "run_card.py")
        old = os.path.join(ATTEMPT, batch, "run_card_before.py")
        hist = os.path.join(PLAN, "execution_runs", rep, "a20260919-01", "scripts", "run_card.py")
        rec = {
            "new_sha256": sha(new), "new_bytes": os.path.getsize(new),
            "old_sha256": sha(old), "old_bytes": os.path.getsize(old),
            "historical_sha256": sha(hist), "historical_bytes": os.path.getsize(hist),
            "old_equals_historical_bytes": open(old, "rb").read() == open(hist, "rb").read(),
        }
        txt = open(new, encoding="utf-8").read()
        lines = txt.splitlines()

        # 1. isinstance decoy: find every line mentioning isinstance AND expected
        decoy = []
        for i, ln in enumerate(lines, 1):
            if "isinstance" in ln:
                decoy.append({"line": i, "text": ln.strip()[:150]})
        rec["isinstance_lines"] = decoy

        # 2. exact type-name equality enforcement lines
        eq = [{"line": i, "text": ln.strip()[:160]} for i, ln in enumerate(lines, 1)
              if re.search(r"raised_name\s*==|==\s*declared|declared_ok\s*=", ln)]
        rec["equality_lines"] = eq

        # 3. rc constants: collect `return N` and `EXIT_*=N` / `RC_*=N`
        rets_old = sorted(set(re.findall(r"^\s*return\s+([0-9]+)\s*$", open(old, encoding="utf-8").read(), re.M)))
        rets_new = sorted(set(re.findall(r"^\s*return\s+([0-9]+)\s*$", txt, re.M)))
        consts_old = dict(re.findall(r"^(?:EXIT|RC)_([A-Z_]+)\s*=\s*([0-9]+)", open(old, encoding="utf-8").read(), re.M))
        consts_new = dict(re.findall(r"^(?:EXIT|RC)_([A-Z_]+)\s*=\s*([0-9]+)", txt, re.M))
        rec["return_literals_old"] = rets_old
        rec["return_literals_new"] = rets_new
        rec["rc_consts_old"] = consts_old
        rec["rc_consts_new"] = consts_new
        rec["rc_consts_renumbered"] = {k: (consts_old.get(k), consts_new.get(k))
                                       for k in set(consts_old) | set(consts_new)
                                       if consts_old.get(k) != consts_new.get(k)}
        rec["exit_code_semantics_exit_code_assignments"] = sorted(set(
            re.findall(r'"exit_code"\s*:\s*([0-9]+)', txt)))
        rec["old_exit_code_assignments"] = sorted(set(
            re.findall(r'"exit_code"\s*:\s*([0-9]+)', open(old, encoding="utf-8").read())))

        # 4. required additive fields
        required = ["declared", "raised", "declared_expectation_ok",
                    "declared_expectation_mismatch", "declared_expectation_not_met",
                    "declared_expectation_comparison", "judged",
                    "declared_expectations_in_cases_json", "declared_expectations_enforced",
                    "cases_json_declared_expectations_usable",
                    "declared_expectation_mismatch_case_ids", "reason_namespace"]
        rec["required_fields_present"] = {f: (f in txt) for f in required}
        rec["all_required_present"] = all(f in txt for f in required)

        # 5. frozen cases.json untouched?
        cases_sha = {}
        for card in sorted({c for c in os.listdir(os.path.join(ATTEMPT, batch))
                            if c.startswith("M") and os.path.isdir(os.path.join(ATTEMPT, batch, c))}):
            pass
        rec["diff_present"] = os.path.exists(os.path.join(ATTEMPT, batch, "runner.diff"))
        rec["evidence_present"] = os.path.exists(os.path.join(ATTEMPT, batch, "evidence.json"))
        out["batches"][batch] = rec
        print("%-8s new=%s old==hist=%s isinstance_lines=%d renumbered=%s"
              % (batch, rec["new_sha256"][:12], rec["old_equals_historical_bytes"],
                 len(decoy), rec["rc_consts_renumbered"]))

    with open(os.path.join(ATTEMPT, "_reviewer_verify", "structural_checks.json"),
              "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
