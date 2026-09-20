"""F-M08-08 evidence, part 1: per-file r1 vs current for the five files the finding names.

The r1 baseline is the reviewer's r1 snapshot copy/<card>/a20260919-01/. This script
first re-verifies that snapshot really is r1 (its oracle.md must hash to the
authoritative v1 claim that oracle.md itself records, for every card), then reports
for each named file: r1 sha256, current sha256, byte sizes, and whether it changed.

For every file that DID change it proves the change is annotation-only by *removing*
the added keys and requiring the remainder to be deep-equal to the r1 object
(stronger than eyeballing the diff), and separately by comparing every pre-existing
leaf value (numbers, bools, nulls, strings) one by one.

It also reports the frozen numeric surface (positive / continuity / defaults /
negatives / summary / tolerances) r1 vs current, which is the reviewer's own
"rc=0 and the positives, continuity, defaults and negatives are all equal" claim,
recomputed.

Usage: <iso venv python> -X utf8 -B f08_named_files.py > f08_named_files.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
COPY = ("C:/Users/\u90d1\u66fe\u6ce2/AppData/Local/Temp/"
        "m05m08-review-20260920-025942/copy")
COPY_R2 = ("C:/Users/\u90d1\u66fe\u6ce2/AppData/Local/Temp/"
           "m05m08-review-20260920-025942/copy_r2")
CARDS = ("M05", "M06", "M07", "M08")
V1_CLAIMS = {
    "M05": "ae1986f61c03daa6ac633ffcc9eaf36060de08f1f39bf8f8c90e5315fe4e943a",
    "M06": "d335f5ec2a699bef008686249d77f2f9af6e2b6306510e57a83446f92df7e3eb",
    "M07": "1eeb6806b82cb7fc70265fac512d263693e041076d195f4a0720dcbc3c9a3591",
    "M08": "47481cab511f2bdf655ffbe3ff1f2d0b0d21c1f8c599cbb101c98124b2d57011",
}
# the five files named by finding F-M08-08
NAMED = (
    ("M08", "evidence/M08/cases.json"),
    ("M08", "evidence/M08/run_result.json"),
    ("M08", "evidence/M08/negative_results.json"),
    ("M07", "evidence/M07/run_result.json"),
    ("M07", "evidence/M07/negative_results.json"),
    ("M06", "evidence/M06/negative_results.json"),
)
FROZEN_KEYS = (
    "positive", "continuity_positive", "defaults", "negatives", "negative_summary",
    "tolerances_ok", "defaults_ok", "exit_code_semantics", "observations",
    "observations_not_gating",
)


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def leaves(obj, path: str, out: dict) -> None:
    if isinstance(obj, dict):
        for k in obj:
            leaves(obj[k], f"{path}.{k}", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            leaves(v, f"{path}[{i}]", out)
    else:
        out[path] = obj


def added_key_paths(a, b, path: str, out: list) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for k in b:
            if k not in a:
                out.append(f"{path}.{k}")
            else:
                added_key_paths(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        for i in range(min(len(a), len(b))):
            added_key_paths(a[i], b[i], f"{path}[{i}]", out)


def strip_paths(obj, paths: set, path: str = "$"):
    if isinstance(obj, dict):
        return {
            k: strip_paths(v, paths, f"{path}.{k}")
            for k, v in obj.items()
            if f"{path}.{k}" not in paths
        }
    if isinstance(obj, list):
        return [
            strip_paths(v, paths, f"{path}[{i}]") for i, v in enumerate(obj)
        ]
    return obj


print("== baseline check: the r1 snapshot copy/ must hash to the authoritative v1 claim ==")
baseline_ok = True
for card in CARDS:
    got = sha_file(os.path.join(COPY, card, "a20260919-01", "oracle.md"))
    ok = got == V1_CLAIMS[card]
    baseline_ok = baseline_ok and ok
    print(f"   {card}: copy/oracle.md={got} == v1 claim -> {ok}")
print(f"   R1_BASELINE_VERIFIED={baseline_ok}")

print("")
print("== r2 snapshot copy_r2/ vs current attempt: was anything changed after r2? ==")
for card in CARDS:
    root_now = os.path.join(BASE, card, "a20260919-01")
    root_r2 = os.path.join(COPY_R2, card, "a20260919-01")
    diffs = []
    for dirpath, dirnames, filenames in os.walk(root_r2):
        dirnames[:] = [d for d in dirnames if d not in ("venv", "__pycache__")]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root_r2).replace("\\", "/")
            now = os.path.join(root_now, rel.replace("/", os.sep))
            if not os.path.exists(now):
                diffs.append((rel, "MISSING_NOW"))
            elif sha_file(full) != sha_file(now):
                diffs.append((rel, "CHANGED"))
    print(f"   {card}: r2_snapshot_vs_current_differences={len(diffs)}")
    for rel, kind in diffs[:12]:
        print(f"      {kind} {rel}")

report: dict[str, object] = {}
print("")
print("== the five files named by F-M08-08 ==")
for card, rel in NAMED:
    p_r1 = os.path.join(COPY, card, "a20260919-01", rel.replace("/", os.sep))
    p_now = os.path.join(BASE, card, "a20260919-01", rel.replace("/", os.sep))
    h1, h2 = sha_file(p_r1), sha_file(p_now)
    print("")
    print(f"-- {card} {rel} --")
    print(f"   r1  sha256={h1} bytes={os.path.getsize(p_r1)}")
    print(f"   now sha256={h2} bytes={os.path.getsize(p_now)}")
    print(f"   CHANGED={h1 != h2}")
    if h1 == h2:
        print("   -> byte-identical to the r1 snapshot; no repack qualification needed")
        report[f"{card}/{rel}"] = {
            "sha256_r1": h1, "sha256_now": h2, "changed": False,
            "note": "byte-identical to the verified r1 snapshot",
        }
        continue
    a = json.load(open(p_r1, encoding="utf-8"))
    b = json.load(open(p_now, encoding="utf-8"))
    added: list = []
    added_key_paths(a, b, "$", added)
    stripped = strip_paths(b, set(added))
    deep_equal = stripped == a
    la, lb = {}, {}
    leaves(a, "$", la)
    leaves(b, "$", lb)
    pre_existing = {k: v for k, v in lb.items() if k in la}
    changed_leaves = {k: (la[k], lb[k]) for k in pre_existing if la[k] != lb[k]}
    removed_leaves = [k for k in la if k not in lb]
    print(f"   added_keys={len(added)} removed_keys={len(removed_leaves)}")
    for k in added:
        print(f"      ADDED {k}")
    print(f"   pre_existing_leaves={len(pre_existing)} "
          f"changed_pre_existing_leaves={len(changed_leaves)}")
    for k, (o, n) in list(changed_leaves.items())[:10]:
        print(f"      CHANGED_LEAF {k}: r1={o!r} now={n!r}")
    for k in removed_leaves[:10]:
        print(f"      REMOVED_LEAF {k}")
    print(f"   ANNOTATION_ONLY_PROOF: strip the added keys -> deep_equal={deep_equal}")
    frozen = {}
    for k in FROZEN_KEYS:
        if k in a or k in b:
            same = a.get(k) == b.get(k)
            frozen[k] = {"present_r1": k in a, "present_now": k in b, "equal": same}
            print(f"      frozen surface {k}: equal={same}")
    report[f"{card}/{rel}"] = {
        "sha256_r1": h1, "sha256_now": h2, "changed": True,
        "added_keys": added,
        "removed_keys": removed_leaves,
        "pre_existing_leaves": len(pre_existing),
        "changed_pre_existing_leaves": {k: [str(o), str(n)]
                                        for k, (o, n) in changed_leaves.items()},
        "annotation_only_proof_deep_equal_after_stripping_added_keys": deep_equal,
        "frozen_surface": frozen,
    }

with open(os.path.join(HERE, "f08_named_files.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("")
print("wrote f08_named_files.json")
sys.exit(0)
