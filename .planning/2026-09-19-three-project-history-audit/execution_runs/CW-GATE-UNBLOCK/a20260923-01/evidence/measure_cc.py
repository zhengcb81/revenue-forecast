"""measure_cc.py - per-function McCabe using the EXACT counting logic of
tests/contract/test_fc1204_complexity_ratchet.py (_mccabe / _max_complexity).

Usage: python measure_cc.py <path-to-py-file>
Prints per-top-level-function CC and FILE-MAX (excluding test_* functions).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


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


def main() -> int:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    top = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            cc = 1 + _mccabe(ast.parse(seg))
            top = max(top, cc)
            print(f"{cc:3d}  {node.name}")
    print(f"FILE-MAX {top}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
