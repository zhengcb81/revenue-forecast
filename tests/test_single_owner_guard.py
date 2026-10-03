"""Single-owner structural guards (R3, roadmap RC-3 / N-03).

Filing acquisition has exactly one canonical owner: ``filing_fetch_client.py``
(which routes to filing-fetch). These AST-level guards reject a second owner or
legacy resolver. Several other modules use subprocess for non-download work
(source reads, orchestration, attestation), so their process boundary is
checked as a closed allowlist rather than banned wholesale.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SKILL_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CLIENT = "filing_fetch_client.py"
# Exact subprocess boundary. Each non-acquisition use has its own contract:
# source preparation delegates to the canonical client; SourceRef reads use
# company-wiki's source_reader_cli; revenue_core calls the attestation provider.
# A new process caller must add a focused contract test before entering here.
SUBPROCESS_CLIENTS = {
    "filing_fetch_client.py",
    "company_wiki_source_reader_v2.py",
    "company_wiki_narrative_process.py",
    "source_preparation.py",
    "revenue_core.py",
}
FORBIDDEN_SYMBOLS = {"resolve_filing", "AcquisitionManager", "AdapterRegistry"}
DOC_SOURCES = (
    [SKILL_ROOT / "SKILL.md"]
    + sorted((SKILL_ROOT / "references").glob("*.md"))
)


def _python_files() -> list[Path]:
    return sorted(path for path in SCRIPTS.glob("*.py") if path.name != "__init__.py")


class SingleOwnerGuardTests(unittest.TestCase):
    def test_subprocess_use_is_limited_to_contract_clients(self) -> None:
        observed: set[str] = set()
        for path in _python_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports_subprocess = False
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports_subprocess |= any(
                        alias.name.split(".")[0] == "subprocess"
                        for alias in node.names
                    )
                if isinstance(node, ast.ImportFrom):
                    imports_subprocess |= node.module == "subprocess"
            if imports_subprocess:
                observed.add(path.name)
        self.assertEqual(observed, SUBPROCESS_CLIENTS)

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
