"""F-M08-08 evidence: what exactly changed in the r2 repack, and is it comments only?

The baseline is the reviewer's own r1 snapshot (copy/<card>/...), which this script
first *verifies* really is the r1 state (its oracle.md must hash to the authoritative
v1 claim that oracle.md itself records).

Then, for every file present in both trees, it reports unchanged / changed, and for
every changed JSON file it walks both objects and lists the exact differing paths
with the old and the new value, classifying each difference as:
   ANNOTATION  the leaf is a string and only the text differs
   VALUE       a number / bool / null / structure changed
A file is "annotation only" iff every difference is an ANNOTATION and no key was
added or removed.

Usage: <iso venv python> -X utf8 -B f08_repack_diff.py > f08_repack_diff.out.txt
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
COPY = (
    "C:/Users/\u90d1\u66fe\u6ce2/AppData/Local/Temp/"
    "m05m08-review-20260920-025942/copy"
)
CARDS = ("M05", "M06", "M07", "M08")
V1_CLAIMS = {
    "M05": "ae1986f61c03daa6ac633ffcc9eaf36060de08f1f39bf8f8c90e5315fe4e943a",
    "M06": "d335f5ec2a699bef008686249d77f2f9af6e2b6306510e57a83446f92df7e3eb",
    "M07": "1eeb6806b82cb7fc70265fac512d263693e041076d195f4a0720dcbc3c9a3591",
    "M08": "47481cab511f2bdf655ffbe3ff1f2d0b0d21c1f8c599cbb101c98124b2d57011",
}


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def walk(root: str) -> dict[str, str]:
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("venv", "__pycache__")]
        for name in filenames:
            full = os.path.join(dirpath, name)
            out[os.path.relpath(full, root).replace("\\", "/")] = full
    return out


def diff_json(a, b, path: str, out: list) -> None:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a:
                out.append((f"{path}.{key}", "ADDED_KEY", None, b[key]))
            elif key not in b:
                out.append((f"{path}.{key}", "REMOVED_KEY", a[key], None))
            else:
                diff_json(a[key], b[key], f"{path}.{key}", out)
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path + ".length", "VALUE", len(a), len(b)))
        for i in range(min(len(a), len(b))):
            diff_json(a[i], b[i], f"{path}[{i}]", out)
        return
    if a == b:
        return
    if isinstance(a, str) and isinstance(b, str):
        out.append((path, "ANNOTATION", a, b))
    else:
        out.append((path, "VALUE", a, b))


print("== baseline check: is the reviewer's copy/ tree really the r1 state? ==")
copy_ok = True
for card in CARDS:
    p = os.path.join(COPY, card, "a20260919-01", "oracle.md")
    got = sha_file(p)
    ok = got == V1_CLAIMS[card]
    copy_ok = copy_ok and ok
    print(f"   {card}: copy/oracle.md sha256={got}")
    print(f"        == authoritative v1 claim {V1_CLAIMS[card]} -> {ok}")
print(f"   ALL_CARDS_BASELINE_IS_R1={copy_ok}")

report: dict[str, object] = {}
print("")
print("== full tree comparison: r1 snapshot vs current attempt ==")
for card in CARDS:
    cur_root = os.path.join(BASE, card, "a20260919-01")
    cp_root = os.path.join(COPY, card, "a20260919-01")
    cur, cp = walk(cur_root), walk(cp_root)
    changed, unchanged, only_cur, only_cp = [], [], [], []
    for rel in sorted(set(cur) & set(cp)):
        if sha_file(cur[rel]) == sha_file(cp[rel]):
            unchanged.append(rel)
        else:
            changed.append(rel)
    for rel in sorted(set(cur) - set(cp)):
        only_cur.append(rel)
    for rel in sorted(set(cp) - set(cur)):
        only_cp.append(rel)
    print("")
    print(f"-- {card} --")
    print(f"   common={len(set(cur) & set(cp))} unchanged={len(unchanged)} "
          f"changed={len(changed)}")
    print(f"   only_in_current={len(only_cur)} only_in_r1_snapshot={len(only_cp)}")
    for rel in changed:
        print(f"      CHANGED {rel}  r1={sha_file(cp[rel])[:16]} now={sha_file(cur[rel])[:16]}"
              f"  bytes {os.path.getsize(cp[rel])} -> {os.path.getsize(cur[rel])}")
    for rel in only_cur:
        print(f"      ONLY_NOW {rel}")
    for rel in only_cp:
        print(f"      ONLY_R1  {rel}")

    print("   -- per-changed-JSON structural diff --")
    per_file = {}
    for rel in changed:
        if not rel.endswith(".json"):
            print(f"      {rel}: not JSON, byte diff only")
            per_file[rel] = {"kind": "non-json"}
            continue
        try:
            a = json.load(open(cp[rel], encoding="utf-8"))
            b = json.load(open(cur[rel], encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"      {rel}: cannot parse both sides ({exc})")
            per_file[rel] = {"kind": "unparsable"}
            continue
        d: list = []
        diff_json(a, b, "$", d)
        kinds = sorted({k for _, k, _, _ in d})
        annotation_only = kinds == ["ANNOTATION"]
        print(f"      {rel}: diffs={len(d)} kinds={kinds} "
              f"annotation_only={annotation_only}")
        for path, kind, old, new in d:
            if kind == "ANNOTATION":
                print(f"          {kind} {path}")
                print(f"              r1 = {old!r}")
                print(f"              now= {new!r}")
            else:
                print(f"          {kind} {path}: r1={old!r} now={new!r}")
        per_file[rel] = {
            "sha256_r1": sha_file(cp[rel]),
            "sha256_now": sha_file(cur[rel]),
            "bytes_r1": os.path.getsize(cp[rel]),
            "bytes_now": os.path.getsize(cur[rel]),
            "diffs": len(d),
            "kinds": kinds,
            "annotation_only": annotation_only,
            "diff_detail": [
                {"path": p, "kind": k, "r1": o, "now": n} for p, k, o, n in d
            ],
        }
    report[card] = {
        "baseline_copy_is_r1": copy_ok,
        "unchanged": unchanged,
        "changed": changed,
        "only_in_current": only_cur,
        "only_in_r1_snapshot": only_cp,
        "per_changed_file": per_file,
    }

with open(os.path.join(HERE, "f08_repack_diff.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("")
print("wrote f08_repack_diff.json")
sys.exit(0)
