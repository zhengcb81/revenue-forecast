"""FC-1204-b gate: per-file max-cyclomatic-complexity ratchet (revenue).

Frozen from the measured 2026-08-12 baseline (findings 60).  A file in the
table must not exceed its frozen max (ratchet moves DOWN only); a file not
in the table (new file) must not exceed 10.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "scripts"

FROZEN_MAX = {
    "analysis/confidence.py": 23,
    "analysis/sensitivity.py": 12,
    "company_wiki_source.py": 18,
    "contracts/document.py": 32,
    "contracts/evidence.py": 10,
    "filing_fetch_client.py": 23,
    "fix_hashes.py": 12,
    "forecast/calc.py": 21,
    "forecast/segments.py": 15,
    "generate_input_template.py": 9,
    "lint_input.py": 25,
    "model_registry.py": 9,
    "processed_artifact_canary.py": 5,
    "publication_registry.py": 16,
    "research/coverage.py": 26,
    "research/drivers.py": 19,
    "research/targets.py": 88,
    "revenue_backtest.py": 18,
    "revenue_constraints.py": 29,
    "revenue_core.py": 6,
    "revenue_forecast.py": 18,
    "revenue_publication.py": 10,
    "revenue_report.py": 150,  # FC-1204-b: 174 -> 150 via block extraction
    "schema_compatibility.py": 6,
    "source_preparation.py": 17,
    "trust_anchor.py": 8
}

NEW_FILE_MAX = 10


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


class ComplexityRatchetTests(unittest.TestCase):
    def test_frozen_files_do_not_worsen(self):
        for rel, frozen in sorted(FROZEN_MAX.items()):
            path = SRC / rel
            self.assertTrue(path.is_file(), f"ratchet file missing: {rel}")
            actual = _max_complexity(path.read_text(encoding="utf-8"))
            self.assertLessEqual(actual, frozen, f"{rel} max {actual} > {frozen}")

    def test_new_files_stay_simple(self):
        for path in sorted(SRC.rglob("*.py")):
            rel = str(path.relative_to(SRC)).replace("\\", "/")
            if rel in FROZEN_MAX:
                continue
            actual = _max_complexity(path.read_text(encoding="utf-8"))
            self.assertLessEqual(actual, NEW_FILE_MAX, f"{rel} max {actual} > {NEW_FILE_MAX}")


if __name__ == "__main__":
    unittest.main()
