"""Phase 19.3 guard — the engine-enum quick-reference in
``references/input-construction.md`` must stay aligned with the constants in
``scripts/revenue_core.py`` (findings G8).

The Alphabet build took 8 validation rounds largely because the engine's enums
are scattered across source and undocumented. The quick-reference exists so a
new company's input validates in <=2 rounds; this test prevents the doc from
silently drifting from the source.

It is hermetic: it reads the markdown and imports ``revenue_core`` only.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]

import sys  # noqa: E402

sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import revenue_core  # noqa: E402


_DOC = (SKILL_ROOT / "references" / "input-construction.md").read_text(encoding="utf-8")

# Capture the quick-reference section (up to the next ## heading or EOF).
_SECTION_RE = re.compile(r"## Engine enum quick-reference.*?(?=\n## |\Z)", re.S)
# A documented enum bullet: "- `UPPER_NAME`: `a`, `b`, ...". The name must start
# uppercase so the prose bullets in the same section (e.g. "- Currency/scale:")
# are not mistaken for enum declarations.
_BULLET_RE = re.compile(r"^-\s*`([A-Z][A-Z0-9_]*)`:\s*(.+)$", re.M)
_TOKEN_RE = re.compile(r"`([^`]+)`")


def _documented_enums() -> dict[str, set[str]]:
    section = _SECTION_RE.search(_DOC)
    assert section is not None, "input-construction.md is missing the '## Engine enum quick-reference' section"
    documented: dict[str, set[str]] = {}
    for name, rest in _BULLET_RE.findall(section.group(0)):
        documented[name] = set(_TOKEN_RE.findall(rest))
    return documented


class InputConstructionEnumConsistencyTests(unittest.TestCase):
    """Documented engine enums must equal the source constants."""

    def test_quick_reference_documents_the_core_enums(self) -> None:
        # Guard: fail loudly if the section is removed or the regex no longer
        # matches, instead of passing vacuously.
        documented = _documented_enums()
        for required in (
            "TIME_BASES",
            "PARAMETER_DIMENSIONS",
            "MONETARY_DIMENSIONS",
            "GROWTH_DRIVER_PERSISTENCE",
            "GROWTH_DRIVER_INFERENCE_DISTANCES",
            "GROWTH_DRIVER_COUNTEREVIDENCE_STATUSES",
        ):
            self.assertIn(required, documented, f"{required} not documented in quick-reference")

    def test_documented_enums_match_revenue_core_constants(self) -> None:
        documented = _documented_enums()
        for name, doc_values in documented.items():
            with self.subTest(enum=name):
                self.assertTrue(
                    hasattr(revenue_core, name),
                    f"input-construction.md documents {name} but revenue_core has no such constant",
                )
                source = getattr(revenue_core, name)
                if isinstance(source, (set, frozenset)):
                    self.assertEqual(doc_values, set(source), f"{name}: doc != revenue_core")
                elif isinstance(source, (tuple, list)):
                    self.assertEqual(
                        sorted(doc_values),
                        sorted(source),
                        f"{name}: doc != revenue_core",
                    )
                else:  # pragma: no cover - defensive
                    self.fail(f"{name} has unexpected constant type {type(source)!r}")


if __name__ == "__main__":
    unittest.main()
