#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-D red-arm runner: copy attempt -> _mut/<id>, apply ONE mutation, run verifier,
record raw rc + output. Originals never modified."""
import csv
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


def p1_tamper_oracle(dst):
    p = os.path.join(dst, "evidence", "I-12-D", "metric_oracle_result.json")

    def op(o):
        o["computed"]["WAPE"]["numerator"] = 41
        o["computed"]["WAPE"]["string"] = "41/300"
    _json(p, op)


def p2_epsilon_on_zero_denominator(dst):
    p = os.path.join(dst, "evidence", "I-12-D", "metric_negative_results.json")

    def op(o):
        for c in o["cases"]:
            if c["case"] == "N1_zero_denominator":
                c["observed"]["WAPE"] = {"defined": True, "value": 0.0, "string": "0/1",
                                         "note": "epsilon 代入"}
                c["checks"]["WAPE_undefined"] = False
                c["checks"]["no_epsilon_used"] = False
                c["pass"] = False
    _json(p, op)


def p3_fabricated_detail_row(dst):
    p = os.path.join(dst, "evidence", "I-12-D", "sample_errors.csv")
    with open(p, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    rows.append(["SMP-FABRICATED", "FAKE", "FAKE", "2026-01-01", "FY2027", "mv-x",
                 "1", "2", "1", "1", "1", "0", "true", ""])
    with open(p, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def p4_unsigned_ci_claim(dst):
    p = os.path.join(dst, "evidence", "I-12-D", "interval_diagnostics.json")

    def op(o):
        o["confidence_intervals"]["computed"] = True
        o["confidence_intervals"]["level"] = 0.95
        o["confidence_intervals"]["pending_items"] = []
    _json(p, op)


def p5_significance_claim(dst):
    p = os.path.join(dst, "evidence", "I-12-D", "metrics_by_stratum.json")

    def op(o):
        o["significance_claimed"] = True
        o["state"] = "significant_improvement"
    _json(p, op)


MUTATIONS = [
    ("P1", "oracle metric value tampered (WAPE numerator 40->41)", 3, p1_tamper_oracle),
    ("P2", "zero denominator answered with epsilon instead of undefined", 3, p2_epsilon_on_zero_denominator),
    ("P3", "fabricated per-sample row in sample_errors.csv", 3, p3_fabricated_detail_row),
    ("P4", "95% CI claimed while thresholds unsigned", 3, p4_unsigned_ci_claim),
    ("P5", "significance claimed with 0 scorable samples", 3, p5_significance_claim),
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
