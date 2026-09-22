"""F-3/F-1 proof: run M14's consolidated_report.py:75 READER EXPRESSION against this
card's patched M13-M16 outputs.

Method (self-evidently the real reader):
  1. Read the HISTORICAL bytes of execution_runs/M14/a20260919-01/recovery/consolidated_report.py
     and extract, from those bytes, the exact subscript expression(s) on line ~75 that index
     expectation_consistency.facts (the reader the reviewer proved breaks on a rename).
  2. eval() that extracted expression against:
       a) the FROZEN historical run_result.json            -> baseline: must work;
       b) B5's patched-runner output (B5 attempt, read-only) -> must KeyError (the F-1 break);
       c) THIS card's patched-runner outputs, arms E/F/B/G x M13..M16 -> must all work,
          and both keys must be present with identical values.
  3. Write evidence/g3_reader_proof.json.

Nothing outside this attempt is written; B5's attempt and the historical cards are read-only.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-fix-g1a-g3", "a20260922-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch")
B5 = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
READER = os.path.join(PLAN, "execution_runs", "M14", "a20260919-01", "recovery",
                      "consolidated_report.py")
CARDS = ("M13", "M14", "M15", "M16")
ARMS = ("E", "F", "B", "G")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def extract_reader_expressions(src_text):
    """Pull the literal reader subscripts out of consolidated_report.py's print block."""
    exprs = re.findall(r'run\["expectation_consistency"\]\["facts"\]\["[a-z_]+"\]', src_text)
    # preserve order, drop duplicates
    seen, ordered = set(), []
    for e in exprs:
        if e not in seen:
            seen.add(e)
            ordered.append(e)
    return ordered


def try_eval(expr, doc):
    try:
        return {"ok": True, "value": eval(expr, {"run": doc})}  # noqa: S307 - exact historical expr
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, exc)}


def main():
    src_bytes = open(READER, "rb").read()
    src_text = src_bytes.decode("utf-8")
    line75 = src_text.splitlines()[74]  # 1-based line 75, verbatim
    exprs = extract_reader_expressions(src_text)
    declared_expr = [e for e in exprs if e.endswith('["declared_expectations"]')]
    assert declared_expr, "reader expression not found in historical bytes"
    declared_expr = declared_expr[0]

    proof = {
        "reader_file": os.path.relpath(READER, PLAN).replace("\\", "/"),
        "reader_file_sha256": hashlib.sha256(src_bytes).hexdigest(),
        "reader_line_75_verbatim": line75,
        "reader_expressions_extracted": exprs,
        "load_bearing_expression": declared_expr,
        "baseline_frozen_run_result": {},
        "b5_patched_output_reproduces_break": {},
        "this_card_outputs": {},
    }

    # (a) baseline: the frozen historical run_result.json the reader was written against
    frozen = load(os.path.join(PLAN, "execution_runs", "M14", "a20260919-01", "evidence",
                               "M14", "run_result.json"))
    for expr in exprs:
        proof["baseline_frozen_run_result"][expr] = try_eval(expr, frozen)

    # (b) B5's patched output (read-only): must KeyError on the declared_expectations expr
    b5_candidates = sorted(glob.glob(os.path.join(B5, "_scratch", "M13-M16", "*",
                                                  "out_M14.json")))
    b5_candidates += sorted(glob.glob(os.path.join(B5, "_scratch", "M13-M16", "*",
                                                   "M14", "run_result.json")))
    b5_docs = []
    for path in b5_candidates:
        try:
            b5_docs.append((path, load(path)))
        except Exception:  # noqa: BLE001
            continue
    seen_hashes = set()
    for path, doc in b5_docs:
        facts = ((doc.get("expectation_consistency") or {}).get("facts") or {})
        key = json.dumps(sorted(facts.keys()), ensure_ascii=False)
        if key in seen_hashes:
            continue
        seen_hashes.add(key)
        proof["b5_patched_output_reproduces_break"][path] = {
            "facts_keys": sorted(facts.keys()),
            "expr_results": {e: try_eval(e, doc) for e in exprs},
        }

    # (c) this card's outputs: all four arms x four cards.
    # Scope note: BOTH keys are required from the PATCHED runner's outputs (arms E/F/G).
    # Arm B runs the byte-identical HISTORICAL runner, whose output must keep its historical
    # shape (old key only) — that is asserted separately, never counted as a both-keys failure.
    all_ok = True
    both_keys_new_runner_ok = True
    arm_b_historical_shape_ok = True
    for arm in ARMS:
        for card in CARDS:
            path = os.path.join(SCRATCH, "M13-M16", arm, "out_%s.json" % card)
            entry = {"path": os.path.relpath(path, ATTEMPT).replace("\\", "/"),
                     "runner_role": "old (historical, byte-identical)" if arm == "B"
                     else "new (this card's patched copy)"}
            if not os.path.exists(path):
                entry["missing"] = True
                all_ok = False
                both_keys_new_runner_ok = False
            else:
                doc = load(path)
                facts = ((doc.get("expectation_consistency") or {}).get("facts") or {})
                entry["facts_keys"] = sorted(facts.keys())
                entry["expr_results"] = {e: try_eval(e, doc) for e in exprs}
                entry["both_keys_present"] = ("declared_expectations" in facts
                                              and "declared_expectations_in_cases_json" in facts)
                entry["both_keys_equal"] = (entry["both_keys_present"]
                                            and facts["declared_expectations"]
                                            == facts["declared_expectations_in_cases_json"])
                entry["values"] = {"declared_expectations": facts.get("declared_expectations"),
                                   "declared_expectations_in_cases_json":
                                       facts.get("declared_expectations_in_cases_json")}
                entry["all_reader_expressions_ok"] = all(
                    r.get("ok") for r in entry["expr_results"].values())
                all_ok = all_ok and entry["all_reader_expressions_ok"]
                if arm == "B":
                    # historical runner output: old key present (readable), new key absent
                    entry["historical_shape_as_expected"] = (
                        "declared_expectations" in facts
                        and "declared_expectations_in_cases_json" not in facts)
                    arm_b_historical_shape_ok = (arm_b_historical_shape_ok
                                                 and entry["historical_shape_as_expected"])
                else:
                    both_keys_new_runner_ok = (both_keys_new_runner_ok
                                               and entry["both_keys_present"]
                                               and entry["both_keys_equal"])
            proof["this_card_outputs"]["%s/%s" % (arm, card)] = entry

    proof["b5_break_reproduced"] = any(
        (r.get("ok") is False)
        for v in proof["b5_patched_output_reproduces_break"].values()
        for r in v["expr_results"].values())
    proof["baseline_ok"] = all(r.get("ok") for r in proof["baseline_frozen_run_result"].values())
    proof["all_this_card_outputs_readable"] = all(
        v.get("all_reader_expressions_ok") for v in proof["this_card_outputs"].values())
    proof["both_keys_on_patched_runner_outputs"] = both_keys_new_runner_ok
    proof["arm_b_historical_shape_unchanged"] = arm_b_historical_shape_ok
    proof["PASS"] = (proof["baseline_ok"] and proof["b5_break_reproduced"]
                     and proof["all_this_card_outputs_readable"]
                     and both_keys_new_runner_ok and arm_b_historical_shape_ok)

    dest = os.path.join(ATTEMPT, "evidence", "g3_reader_proof.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(proof, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("reader line 75:", line75.strip())
    print("expression:", declared_expr)
    print("baseline_ok:", proof["baseline_ok"])
    print("b5_break_reproduced:", proof["b5_break_reproduced"])
    print("all_this_card_outputs_readable:", proof["all_this_card_outputs_readable"])
    print("both_keys_on_patched_runner_outputs:", proof["both_keys_on_patched_runner_outputs"])
    print("arm_b_historical_shape_unchanged:", proof["arm_b_historical_shape_unchanged"])
    print("PASS =", proof["PASS"])
    print("wrote", dest)
    return 0 if proof["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
