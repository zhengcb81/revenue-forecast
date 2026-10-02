"""Dual metric harness for RATCHET-FIX-A.

A (authoritative) = tests/contract/test_fc1204_complexity_ratchet.py::_max_complexity
B (dispatch "actual" numbers) = standard McCabe:
   1 + decisions where decisions = If/For/While/ExceptHandler/comprehension/Assert/With
   + BoolOp(len(values)-1)  [each boolean expression counted once, n-1]
   + IfExp                  [ternary counted]
   i.e. B = A - (#ast.And/#ast.Or operator nodes) + (#ast.IfExp)
   Reproduces dispatch 14/17/16/32 exactly.
"""
import ast
import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
SPEC = importlib.util.spec_from_file_location(
    "rat", REPO / "tests" / "contract" / "test_fc1204_complexity_ratchet.py")
RAT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RAT)

FROZEN = {
    "adapters/parity.py": 13,
    "lock.py": 15,
    "prompt_injection.py": 15,
    "store.py": 30,
}


def _mccabe_b(node) -> int:
    """Standard McCabe decision points (B metric)."""
    if not isinstance(node, ast.AST):
        return 0
    total = 0
    for child in ast.iter_child_nodes(node):
        total += _mccabe_b(child)
    if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                         ast.comprehension, ast.Assert, ast.With)):
        total += 1
    if isinstance(node, ast.IfExp):
        total += 1
    if isinstance(node, ast.BoolOp):
        total += len(node.values) - 1
    return total


def func_metrics(text: str):
    """-> list of (name, lineno, A, B) for top-level non-test functions."""
    tree = ast.parse(text)
    out = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            a = RAT._max_complexity(seg)
            b = 1 + _mccabe_b(ast.parse(seg))
            out.append((node.name, node.lineno, a, b))
    return out


def file_metrics(rel: str):
    text = (REPO / "src" / "company_wiki" / "source_catalog" / rel).read_text(encoding="utf-8")
    rows = func_metrics(text)
    a = max((r[2] for r in rows), default=0)
    b = max((r[3] for r in rows), default=0)
    return a, b, rows


def report():
    ok = True
    for rel, frozen in FROZEN.items():
        a, b, rows = file_metrics(rel)
        worst_a = max(rows, key=lambda r: r[2])
        worst_b = max(rows, key=lambda r: r[3])
        pa = "OK" if a <= frozen else "FAIL"
        pb = "OK" if b <= frozen else "FAIL"
        if a > frozen or b > frozen:
            ok = False
        print(f"{rel}: A={a}({worst_a[0]}) {pa} | B={b}({worst_b[0]}) {pb} | frozen={frozen}")
        for name, lineno, x, y in sorted(rows, key=lambda r: -(r[2] + r[3]))[:4]:
            print(f"    {name}:{lineno}  A={x}  B={y}")
    print("ALL OK" if ok else "SOME FAIL")
    return ok


if __name__ == "__main__":
    sys.exit(0 if report() else 1)
