#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I-12-B red-arm runner: copy the attempt into _mut/<id>, apply ONE mutation,
run the read-only verifier against the copy, record raw rc + output.
Originals are never modified (byte-identical before/after is asserted by _check_originals.py).
"""
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


def m1_duplicate_sample_id(dst):
    p = os.path.join(dst, "evidence", "I-12-B", "sample_manifest.jsonl")
    rows = load_jsonl(p)
    rows.append(dict(rows[0]))          # duplicate sample_id
    save_jsonl(p, rows)


def m2_future_leakage(dst):
    p = os.path.join(dst, "evidence", "I-12-B", "sample_manifest.jsonl")
    rows = load_jsonl(p)
    rows[0]["available_at"] = "2026-03-21"      # > origin 2026-03-20
    rows[0]["available_at_le_origin"] = False
    save_jsonl(p, rows)


def m3_drop_exclusion(dst):
    p = os.path.join(dst, "evidence", "I-12-B", "exclusions.jsonl")
    rows = load_jsonl(p)
    rows = [r for r in rows if r.get("exclusion_id") != "EX-002"]
    save_jsonl(p, rows)


def m4_open2_consumed(dst):
    p = os.path.join(dst, "evidence", "I-12-B", "actuals_policy_application.json")
    with open(p, "r", encoding="utf-8") as f:
        obj = json.load(f)
    obj["redline_probe_mutation"] = {"value": "124248.63", "state": "consumed"}
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def m5_params_released(dst):
    p = os.path.join(dst, "handoff.json")
    with open(p, "r", encoding="utf-8") as f:
        obj = json.load(f)
    obj["params_released"] = True
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


MUTATIONS = [
    ("M1", "duplicate sample_id appended", 3, m1_duplicate_sample_id),
    ("M2", "available_at>origin / leakage flag", 3, m2_future_leakage),
    ("M3", "row-level exclusion dropped (conservation broken)", 3, m3_drop_exclusion),
    ("M4", "OPEN-2 redline literal consumed in evidence", 3, m4_open2_consumed),
    ("M5", "handoff.params_released=true", 3, m5_params_released),
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
        json.dump({"results": results,
                   "all_pass": all(r["pass"] for r in results),
                   "legend": "0=all invariants OK, 1=harness failure, 2=no verdict, 3=named invariant violation"},
                  f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0 if all(r["pass"] for r in results) else 3


if __name__ == "__main__":
    sys.exit(main())
