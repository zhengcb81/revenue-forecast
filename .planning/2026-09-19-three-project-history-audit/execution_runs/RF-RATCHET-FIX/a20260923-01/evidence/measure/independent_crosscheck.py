"""Independent cross-check: replicate _mccabe/_max_complexity INLINED from the test source
(no import of the test module) and evaluate every frozen row + every new file.
Prints only violations. Used to confirm the import-based scan.
"""
from __future__ import annotations

import ast
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
SRC = RF / "scripts"
TEST = RF / "tools" / "tests" / "test_complexity_ratchet.py"

# --- inlined verbatim from tools/tests/test_complexity_ratchet.py ---


def _mccabe(node: ast.AST) -> int:
    if not isinstance(node, ast.AST):
        return 0
    total = 0
    for child in ast.iter_child_nodes(node):
        total += _mccabe(child)
    if isinstance(node, (ast.If, ast.For, ast.While, ast.And, ast.Or,
                         ast.ExceptHandler, ast.comprehension, ast.Assert,
                         ast.With)):
        total += 1
    if isinstance(node, ast.BoolOp):
        total += len(node.values) - 1
    return total


def _max_complexity(text: str) -> int:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return 0
    top = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            top = max(top, 1 + _mccabe(ast.parse(seg)))
    return top


# --- extract FROZEN_MAX from the test source without importing it ---
ns: dict = {}
tree = ast.parse(TEST.read_text(encoding="utf-8"))
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == "FROZEN_MAX" for t in node.targets
    ):
        ns["FROZEN_MAX"] = ast.literal_eval(node.value)
    if isinstance(node, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == "NEW_FILE_MAX" for t in node.targets
    ):
        ns["NEW_FILE_MAX"] = ast.literal_eval(node.value)
FROZEN_MAX: dict = ns["FROZEN_MAX"]
NEW_FILE_MAX: int = ns["NEW_FILE_MAX"]

print("INLINED CROSS-CHECK (no import of test module)")
print("\n-- frozen violations --")
n = 0
for rel, frozen in sorted(FROZEN_MAX.items()):
    p = SRC / rel
    actual = _max_complexity(p.read_text(encoding="utf-8"))
    if actual > frozen:
        n += 1
        print(f"  FAIL {rel:35s} actual={actual} frozen={frozen}")
print(f"  frozen violations = {n}")

print("\n-- new-file violations --")
m = 0
for p in sorted(SRC.rglob("*.py")):
    rel = str(p.relative_to(SRC)).replace("\\", "/")
    if rel in FROZEN_MAX:
        continue
    actual = _max_complexity(p.read_text(encoding="utf-8"))
    if actual > NEW_FILE_MAX:
        m += 1
        print(f"  FAIL {rel:35s} actual={actual} cap={NEW_FILE_MAX}")
print(f"  new-file violations = {m}")
