"""Per-function CC using the SAME measurement code as tools/tests/test_complexity_ratchet.py.

Imports the test module and reuses its _mccabe / _max_complexity verbatim.
Usage: python -B measure_cc.py <file> [<file> ...]
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
TEST = RF / "tools" / "tests" / "test_complexity_ratchet.py"

spec = importlib.util.spec_from_file_location("tcr", TEST)
tcr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tcr)


def per_function(text: str):
    tree = ast.parse(text)
    rows = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            cc = 1 + tcr._mccabe(ast.parse(seg))
            rows.append((node.name, node.lineno, cc))
    return rows


def main() -> None:
    files = sys.argv[1:]
    if not files:
        files = [
            str(RF / "scripts" / "analysis" / "confidence.py"),
            str(RF / "scripts" / "model_extensions.py"),
        ]
    for f in files:
        text = Path(f).read_text(encoding="utf-8")
        print(f"== {f}")
        for name, ln, cc in sorted(per_function(text), key=lambda r: (-r[2], r[1])):
            print(f"  {name:45s} L{ln:<5d} CC={cc}")
        print(f"  FILE_MAX={tcr._max_complexity(text)}")


if __name__ == "__main__":
    main()
