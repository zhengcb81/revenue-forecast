#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-E red-arm runner: copy attempt -> _mut/<id>, apply ONE mutation, run verifier,
record raw rc + output. Originals never modified."""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MUT = os.path.join(HERE, "_mut")
EXCLUDE = {"_mut", "__pycache__", "_gate0_probe.txt"}


def copy_tree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for dirpath, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        rel = os.path.relpath(dirpath, src)
        out = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(out, exist_ok=True)
        for fn in files:
            shutil.copy2(os.path.join(dirpath, fn), os.path.join(out, fn))


def _json(p, op):
    with open(p, "r", encoding="utf-8") as f:
        obj = json.load(f)
    op(obj)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def q1_verdict_supported(dst):
    p = os.path.join(dst, "evidence", "I-12-E", "accuracy_qualification.json")

    def op(o):
        o["comparisons"][1]["verdict"] = "supported"
        o["comparisons"][1]["threshold_state"] = "signed"
        o["comparison_counts"]["supported"] = 1
        o["comparison_counts"]["inconclusive"] = len(o["comparisons"]) - 1
    _json(p, op)


def q2_cross_column_pass(dst):
    p = os.path.join(dst, "evidence", "I-12-E", "accuracy_qualification.json")

    def op(o):
        o["three_column"]["no_cross_column_pass_override"] = False
        o["three_column"]["accuracy"]["state"] = "pass"
        o["three_column"]["accuracy"]["column_state"] = "pass"
    _json(p, op)


def q3_accuracy_claim(dst):
    p = os.path.join(dst, "evidence", "I-12-E", "accuracy_qualification.json")

    def op(o):
        o["three_column"]["accuracy_improvement_claimed"] = True
        o["counts"]["accuracy_improvement_claimed"] = True
        o["stops"]["STOP_CLAIM"]["triggered"] = True
    _json(p, op)


def q4_open2_consumed(dst):
    p = os.path.join(dst, "evidence", "I-12-E", "error_taxonomy.json")

    def op(o):
        o["redline_mutation"] = {"value": "124248.63", "state": "consumed"}
    _json(p, op)


def q5_taxonomy_gutted(dst):
    p = os.path.join(dst, "evidence", "I-12-E", "error_taxonomy.json")

    def op(o):
        o["categories"].pop("random", None)
        o["follow_up_questions"] = []
    _json(p, op)


MUTATIONS = [
    ("Q1", "comparison judged supported while thresholds unsigned", 3, q1_verdict_supported),
    ("Q2", "one column PASS overriding another (accuracy->pass)", 3, q2_cross_column_pass),
    ("Q3", "accuracy improvement claimed (STOP_CLAIM form)", 3, q3_accuracy_claim),
    ("Q4", "OPEN-2 redline literal consumed in evidence", 3, q4_open2_consumed),
    ("Q5", "error taxonomy category dropped + follow-up questions emptied", 3, q5_taxonomy_gutted),
]


def main():
    results = []
    os.makedirs(MUT, exist_ok=True)
    for mid, desc, exp, fn in MUTATIONS:
        dst = os.path.join(MUT, mid)
        copy_tree(HERE, dst)
        fn(dst)
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "_verify.py"), "--root", dst],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = (proc.stdout or "") + (proc.stderr or "")
        with open(os.path.join(dst, "verifier_output.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write("arm=%s expected_rc=%d actual_rc=%d\n%s" % (mid, exp, proc.returncode, out))
        results.append({"arm": mid, "mutation": desc, "expected_rc": exp,
                        "actual_rc": proc.returncode, "pass": proc.returncode == exp})
        print("%s expected=%d actual=%d pass=%s" % (mid, exp, proc.returncode, proc.returncode == exp))
    with open(os.path.join(MUT, "mutation_results.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"results": results, "all_pass": all(r["pass"] for r in results),
                   "legend": "0=all invariants OK, 1=harness failure, 2=no verdict, 3=named invariant violation"},
                  f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0 if all(r["pass"] for r in results) else 3


if __name__ == "__main__":
    sys.exit(main())
