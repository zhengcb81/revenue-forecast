"""Single-owner structural guards (R3, roadmap RC-3 / N-03).

Filing acquisition has exactly one canonical owner: ``filing_fetch_client.py``
(which routes to filing-fetch). These checks cover that operation boundary
without prescribing which other RF components may start a process.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path, PureWindowsPath


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
SKILL_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CLIENT = "filing_fetch_client.py"
FILING_ENTRY_NAMES = {"fetch_filing.py", "fetch_statements.py"}
FORBIDDEN_SYMBOLS = {"resolve_filing", "AcquisitionManager", "AdapterRegistry"}
DOC_SOURCES = (
    [SKILL_ROOT / "SKILL.md"]
    + sorted((SKILL_ROOT / "references").glob("*.md"))
)


def _python_files() -> list[Path]:
    return sorted(path for path in SCRIPTS.rglob("*.py") if path.name != "__init__.py")


def _filing_entries(tree: ast.AST) -> set[str]:
    return {
        name
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        if (name := node.value.replace("\\", "/").rsplit("/", 1)[-1]) in FILING_ENTRY_NAMES
    }


class SingleOwnerGuardTests(unittest.TestCase):
    def test_filing_cli_entries_are_owned_by_the_canonical_client(self) -> None:
        for path in _python_files():
            with self.subTest(path=path.relative_to(SCRIPTS).as_posix()):
                actual = _filing_entries(ast.parse(path.read_text(encoding="utf-8")))
                expected = FILING_ENTRY_NAMES if path == SCRIPTS / CANONICAL_CLIENT else set()
                self.assertEqual(actual, expected)

    def test_filing_entry_detection_is_not_a_subprocess_import_allowlist(self) -> None:
        native_scripts = PureWindowsPath(SKILL_ROOT / "scripts")
        for prefix in ("scripts/", "scripts\\", f"{native_scripts}\\"):
            for entry in sorted(FILING_ENTRY_NAMES):
                with self.subTest(prefix=prefix, entry=entry):
                    transport = ast.parse(f"run([interpreter, {prefix + entry!r}])")
                    self.assertEqual(_filing_entries(transport), {entry})
        local_job = ast.parse('import subprocess\nsubprocess.run(["render-report", "fetch_filing.py.backup"])')
        self.assertEqual(_filing_entries(local_job), set())

    def test_no_second_resolve_filing_symbol(self) -> None:
        for path in _python_files():
            if path == SCRIPTS / CANONICAL_CLIENT:
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
