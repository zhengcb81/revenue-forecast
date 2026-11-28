"""Per-callable decision complexity over the same owned source tree as S6."""

from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts"
BASELINE = ROOT / "tools" / "rf-runtime-baseline.json"
MAX_SIMPLE = 10
_SCOPES = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
_BRANCHES = (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler,
             ast.comprehension, ast.Assert, ast.With, ast.AsyncWith, ast.match_case)


def _decisions(node: ast.AST) -> int:
    """Count branches owned by a callable, excluding nested declarations."""
    if isinstance(node, _SCOPES):
        return 0
    local = len(node.values) - 1 if isinstance(node, ast.BoolOp) else int(isinstance(node, _BRANCHES))
    return local + sum(_decisions(child) for child in ast.iter_child_nodes(node))


def _measure(tree: ast.AST, prefix: str = "") -> dict[str, int]:
    results: dict[str, int] = {}
    for node in ast.iter_child_nodes(tree):
        nested = prefix
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nested += node.name + "."
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            results[nested[:-1]] = 1 + sum(_decisions(item) for item in node.body)
        for name, value in _measure(node, nested).items():
            results[name] = max(results.get(name, 0), value)
    return results


def measured_overages(source: Path) -> dict[str, dict[str, int]]:
    measured = {}
    for path in sorted(source.rglob("*.py")):
        relative = path.relative_to(source).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        existing = {name: score for name, score in _measure(tree).items() if score > MAX_SIMPLE}
        if existing:
            measured[relative] = existing
    return measured


def _growth(observed: dict[str, dict[str, int]], frozen: dict[str, dict[str, int]]) -> list[str]:
    return [
        f"{relative}:{name} {score} > {ceiling}"
        for relative, scores in sorted(observed.items())
        for name, score in sorted(scores.items())
        if score > (ceiling := frozen.get(relative, {}).get(name, MAX_SIMPLE))
    ]


class ComplexityRatchetTests(unittest.TestCase):
    def test_existing_and_new_callables_do_not_exceed_their_ceiling(self):
        frozen = json.loads(BASELINE.read_text(encoding="utf-8"))["callable_complexity"]
        self.assertEqual(frozen["new_callable_max"], MAX_SIMPLE)
        growth = _growth(measured_overages(SOURCE), frozen["observed"])
        self.assertEqual(growth, [], "\n".join(growth))

    def test_nested_async_functions_and_new_methods_cannot_hide_behind_a_module_max(self):
        tree = ast.parse("""
class Adapter:
    async def read(self):
        if online and authenticated:
            return result

def outer():
    def inner():
        if source:
            return source
    return inner
""")
        self.assertEqual(_measure(tree), {"Adapter.read": 3, "outer": 1, "outer.inner": 2})
        self.assertEqual(
            _growth({"adapter.py": {"known": 15, "new": 11}}, {"adapter.py": {"known": 15}}),
            ["adapter.py:new 11 > 10"],
        )
        self.assertEqual(
            _growth({"adapter.py": {"known": 16}}, {"adapter.py": {"known": 15}}),
            ["adapter.py:known 16 > 15"],
        )


if __name__ == "__main__":
    unittest.main()
