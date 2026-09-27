"""Measure the frozen max-cyclomatic-complexity for ONE file using exactly the
gate's algorithm (tools/tests/test_complexity_ratchet.py), so we can prove the
WC-4 edit keeps scripts/revenue_forecast.py <= its frozen max (18) even when the
gate's own loop aborts earlier on unrelated pre-existing failures.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
FROZEN_MAX = {"revenue_forecast.py": 18}


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
    tree = ast.parse(text)
    top = 0
    worst = ("<none>", 0)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            value = 1 + _mccabe(ast.parse(seg))
            if value > top:
                top = value
            if value > worst[1]:
                worst = (node.name, value)
    return top, worst


def main() -> int:
    targets = {
        "iso_fixed": ATTEMPT / "iso" / "rf" / "scripts" / "revenue_forecast.py",
        "iso_pristine": ATTEMPT / "evidence" / "rgm" / "cli_original.py",
        "production": Path(r"C:\Users\郑曾波\Projects\revenue-forecast\scripts\revenue_forecast.py"),
    }
    ok = True
    for label, path in targets.items():
        value, worst = _max_complexity(path.read_text(encoding="utf-8"))
        frozen = FROZEN_MAX["revenue_forecast.py"]
        passed = value <= frozen
        ok = ok and passed
        print(f"{label}: max_complexity={value} (worst func={worst[0]}:{worst[1]}) "
              f"frozen_max={frozen} pass={passed} file={path}")
    print("OWN_FILE_RATCHET_OK" if ok else "OWN_FILE_RATCHET_FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
