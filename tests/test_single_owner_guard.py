"""Single-owner structural guards (R3, roadmap RC-3 / N-03).

Filing acquisition has exactly one canonical owner: ``filing_fetch_client.py``
(which routes to filing-fetch).  These AST-level guards fail the build if a
second owner ever grows back in ``scripts/`` or if the docs re-reference the
removed legacy module.
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SKILL_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CLIENT = "filing_fetch_client.py"
FORBIDDEN_SYMBOLS = {"resolve_filing", "AcquisitionManager", "AdapterRegistry"}
DOC_SOURCES = (
    [SKILL_ROOT / "SKILL.md"]
    + sorted((SKILL_ROOT / "references").glob("*.md"))
)


def _python_files() -> list[Path]:
    return sorted(path for path in SCRIPTS.glob("*.py") if path.name != "__init__.py")


class SingleOwnerGuardTests(unittest.TestCase):
    def test_only_canonical_client_may_use_subprocess_download_adapters(self) -> None:
        for path in _python_files():
            if path.name == CANONICAL_CLIENT:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertNotIn(
                        "subprocess",
                        {alias.name.split(".")[0] for alias in node.names},
                        f"{path.name} imports subprocess (second download owner)",
                    )
                if isinstance(node, ast.ImportFrom):
                    self.assertNotEqual(
                        node.module,
                        "subprocess",
                        f"{path.name} imports subprocess (second download owner)",
                    )

    def test_no_second_resolve_filing_symbol(self) -> None:
        for path in _python_files():
            if path.name == CANONICAL_CLIENT:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            defined = {
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))
            }
            self.assertFalse(
                FORBIDDEN_SYMBOLS & defined,
                f"{path.name} defines a second filing-owner symbol: "
                f"{sorted(FORBIDDEN_SYMBOLS & defined)}",
            )

    def test_docs_never_reference_the_removed_legacy_owner(self) -> None:
        for path in DOC_SOURCES:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(
                "filing_acquisition",
                text,
                f"{path} still references the removed legacy filing owner",
            )


if __name__ == "__main__":
    unittest.main()
