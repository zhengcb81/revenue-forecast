"""RF-RATCHET-REST-A oracle: full-row scan of the complexity ratchet.

Numbers come from the ratchet test's OWN _max_complexity (imported live from
tools/tests/test_complexity_ratchet.py).  An independently written twin
(_twin_max_complexity: ast.walk-based, separate traversal) must agree on every
scanned file or the script aborts (two-implementation agreement).

Usage:  python scan_ratchet.py <root> [--per-function] [--json out.json]
  <root>  repo root that contains scripts/ and tools/tests/test_complexity_ratchet.py
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

BRANCH_NODES = (ast.If, ast.For, ast.While, ast.And, ast.Or,
                ast.ExceptHandler, ast.comprehension, ast.Assert, ast.With)


def load_ratchet(root: Path):
    path = root / "tools" / "tests" / "test_complexity_ratchet.py"
    spec = importlib.util.spec_from_file_location("ratchet_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, path


def twin_max_complexity(text: str) -> int:
    """Independent re-derivation of the ratchet's per-file max complexity.

    Different traversal (ast.walk over each top-level def's segment) from the
    test's recursive _mccabe; same branch-node semantics, same 1 + count, same
    test_-prefix exclusion, same SyntaxError -> 0.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return 0
    best = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            parsed = ast.parse(seg)
            count = 1
            for sub in ast.walk(parsed):
                if isinstance(sub, BRANCH_NODES):
                    count += 1
                if isinstance(sub, ast.BoolOp):
                    count += len(sub.values) - 1
            best = max(best, count)
    return best


def per_function(mod, text: str):
    """[{name, start, cc}] for every top-level def the ratchet measures."""
    out = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            cc = 1 + mod._mccabe(ast.parse(seg))
            out.append({"name": node.name, "start": node.lineno,
                        "end": node.end_lineno, "cc": cc})
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--per-function", action="store_true")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    root = args.root.resolve()
    mod, ratchet_path = load_ratchet(root)
    src = root / "scripts"

    print(f"root            : {root}")
    print(f"ratchet test    : {ratchet_path}")
    print(f"ratchet sha256  : {sha256(ratchet_path)}")
    print(f"SRC resolved    : {mod.SRC} (exists={mod.SRC.is_dir()})")
    print()

    failures = []
    agreement_checked = 0

    def measure(rel: str, frozen: int, bucket: str):
        nonlocal agreement_checked
        path = src / rel
        text = path.read_text(encoding="utf-8")
        theirs = mod._max_complexity(text)
        mine = twin_max_complexity(text)
        agreement_checked += 1
        if theirs != mine:
            print(f"!! IMPLEMENTATION DISAGREE {rel}: test={theirs} twin={mine}")
            return 2
        ok = theirs <= frozen
        status = "PASS" if ok else "FAIL"
        print(f"{status}  {rel:<34} actual={theirs:<4} frozen={frozen:<4} "
              f"(headroom {frozen - theirs:+d})")
        if not ok:
            failures.append({"rel": rel, "actual": theirs, "frozen": frozen,
                             "bucket": bucket})
        if args.per_function and rel in MY_ROWS:
            print(f"      per-function (top-level, ratchet semantics):")
            for f in sorted(per_function(mod, text), key=lambda x: -x["cc"]):
                mark = " <-- drives file max" if f["cc"] == theirs else ""
                print(f"        cc={f['cc']:<4} L{f['start']}-{f['end']:<5} {f['name']}{mark}")
        return 0

    MY_ROWS = {"forecast/calc.py", "generate_input_template.py",
               "research/targets.py"}

    print("=== FROZEN ROWS (test_frozen_files_do_not_worsen, sorted order = abort order) ===")
    rc = 0
    for rel, frozen in sorted(mod.FROZEN_MAX.items()):
        rc = max(rc, measure(rel, frozen, "frozen"))
    print()
    print("=== NEW-FILE ROWS (test_new_files_stay_simple, NEW_FILE_MAX) ===")
    for path in sorted(src.rglob("*.py")):
        rel = str(path.relative_to(src)).replace("\\", "/")
        if rel in mod.FROZEN_MAX:
            continue
        rc = max(rc, measure(rel, mod.NEW_FILE_MAX, "new"))
    print()
    print(f"files cross-checked by two implementations: {agreement_checked}")
    print(f"FAILING ROWS: {len(failures)}")
    for f in failures:
        print(f"  - {f['rel']} {f['actual']} > {f['frozen']} [{f['bucket']}]")

    my_fail = [f for f in failures if f["rel"] in MY_ROWS]
    other_fail = [f for f in failures if f["rel"] not in MY_ROWS]
    print(f"MY 3 ROWS failing: {len(my_fail)} -> {[f['rel'] for f in my_fail]}")
    print(f"OTHER rows failing: {len(other_fail)} -> {[f['rel'] for f in other_fail]}")

    if args.json:
        args.json.write_text(json.dumps(
            {"root": str(root), "ratchet_sha256": sha256(ratchet_path),
             "failures": failures, "agreement_checked": agreement_checked},
            indent=2), encoding="utf-8")
        print(f"json -> {args.json}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
