#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-C red-arm runner: copy attempt -> _mut/<id>, apply ONE mutation, run verifier,
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


def load_jsonl(p):
    with open(p, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def save_jsonl(p, rows):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _json(p, op):
    with open(p, "r", encoding="utf-8") as f:
        obj = json.load(f)
    op(obj)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def n1_forecast_value(dst):
    p = os.path.join(dst, "evidence", "I-12-C", "forecast_vintages.jsonl")
    rows = load_jsonl(p)
    rows[0]["forecast"]["base"] = 123456
    rows[0]["forecast_value_state"] = "produced"
    save_jsonl(p, rows)


def n2_baseline_tamper(dst):
    p = os.path.join(dst, "evidence", "I-12-C", "baseline_vintages.jsonl")
    rows = load_jsonl(p)
    for r in rows:
        if r.get("kind") == "primary_baseline" and r.get("sample_id") == "SMP-CN-ZIJIN_MINERAL_20260320_FY2027":
            r["value"] = r["value"] + 1
            break
    save_jsonl(p, rows)


def n3_self_unblind(dst):
    p = os.path.join(dst, "evidence", "I-12-C", "unblind_receipt.json")

    def op(o):
        o["issued"] = True
        o["issued_by"] = "implementer_i12c"
        o["state"] = "issued"
    _json(p, op)


def n4_freeze_after_read(dst):
    p = os.path.join(dst, "evidence", "I-12-C", "forecast_manifest.json")

    def op(o):
        o["freeze_before_unblind"] = False
        o["actuals_read_by_this_station"] = True
    _json(p, op)


def n5_open2_consumed(dst):
    p = os.path.join(dst, "evidence", "I-12-C", "unblind_receipt.json")

    def op(o):
        o["redline_mutation"] = {"value": "124248.63", "state": "consumed"}
    _json(p, op)


MUTATIONS = [
    ("N1", "forecast.base numeric value written while params_released=false", 3, n1_forecast_value),
    ("N2", "primary baseline value tampered (+1)", 3, n2_baseline_tamper),
    ("N3", "implementer self-issues unblind_receipt", 3, n3_self_unblind),
    ("N4", "freeze_before_unblind=false (freeze after reading actuals)", 3, n4_freeze_after_read),
    ("N5", "OPEN-2 redline literal consumed in evidence", 3, n5_open2_consumed),
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
