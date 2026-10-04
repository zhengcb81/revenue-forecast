# Dual-metric measurement: the test's own metric (authoritative gate) + metric "M"
# (BoolOp counted as n-1 only, IfExp counted) — used to reconcile the dispatch's
# stated numbers (20~27 / 25 / 13).
import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
spec = importlib.util.spec_from_file_location(
    "rat", str(REPO / "tests" / "contract" / "test_fc1204_complexity_ratchet.py")
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def mccabe_m(node, count_ifexp=True, boolop_as_n_minus_1=True):
    if not isinstance(node, ast.AST):
        return 0
    total = 0
    for child in ast.iter_child_nodes(node):
        total += mccabe_m(child, count_ifexp, boolop_as_n_minus_1)
    if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                         ast.comprehension, ast.Assert, ast.With)):
        total += 1
    if count_ifexp and isinstance(node, ast.IfExp):
        total += 1
    if isinstance(node, ast.BoolOp):
        total += len(node.values) - 1
        if not boolop_as_n_minus_1:
            total += 1  # the test metric also counts the And/Or op node itself
    return total


def max_m(text, **kw):
    tree = ast.parse(text)
    top = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            top = max(top, 1 + mccabe_m(ast.parse(seg), **kw))
    return top


def per_func(text, fn):
    out = []
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            out.append((fn(seg), node.name, node.lineno))
    return sorted(out, reverse=True)


FILES = ["src/company_wiki/source_catalog/observability.py",
         "src/company_wiki/source_catalog/prune_retired_evidence.py",
         "src/company_wiki/source_catalog/adapters/conformance.py"]

print("=== CURRENT working tree ===")
for rel in FILES:
    t = (REPO / rel).read_text(encoding="utf-8")
    print(f"{rel}: TEST={m._max_complexity(t)} M={max_m(t, count_ifexp=True, boolop_as_n_minus_1=True)}")

print("=== HEAD (committed) ===")
for rel in FILES:
    t = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
                       capture_output=True).stdout.decode("utf-8")
    test_max = m._max_complexity(t)
    m_max = max_m(t, count_ifexp=True, boolop_as_n_minus_1=True)
    print(f"{rel}: TEST={test_max} M={m_max}")
    if rel.endswith("observability.py") or rel.endswith("conformance.py"):
        for c, name, ln in per_func(t, lambda s: 1 + mccabe_m(ast.parse(s))):
            pass
        # show the two metrics per function for the interesting ones
        rows_test = {name: c for c, name, _ in per_func(t, lambda s: 1 + m._mccabe(ast.parse(s)))}
        rows_m = {name: c for c, name, _ in per_func(t, lambda s: 1 + mccabe_m(ast.parse(s)))}
        for name in rows_test:
            if rows_test[name] > 8 or rows_m[name] > 8:
                print(f"    {name}: TEST={rows_test[name]} M={rows_m[name]}")
