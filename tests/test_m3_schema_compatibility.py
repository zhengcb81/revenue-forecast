"""M3-FLOW compatibility matrix tests: schema 3.9 is a new explicit row.

Rules under test (per the strict registry semantics):

* schema 3.9 (period_flow + role-aware triangulation) is emitted only by the
  new engine 4.2.0 — engines 4.1.0/4.1.1 never emitted it and must fail closed;
* the 3.7/3.8 emit history is preserved verbatim ({4.1.0, 4.1.1}) and the
  current engine is always a legal emitter for the schemas it can produce;
* ``formal`` mode accepts only the current engine for every schema;
* the registry mirrors the supported schema-version constants, so old frozen
  artifacts pinned to their declared emitting engine keep validating while
  unknown engines keep failing.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from contracts.constants import (  # noqa: E402
    FORECAST_SCHEMA_VERSION,
    OPT_IN_SCHEMA_VERSION,
    SUPPORTED_FORECAST_SCHEMA_VERSIONS,
)
from revenue_core import ENGINE_VERSION  # noqa: E402
from schema_compatibility import (  # noqa: E402
    SCHEMA_EMIT_ENGINES,
    require_validating_engine,
    supported_schema_versions,
    validating_engine_allowed,
)

PERIOD_EVIDENCE_SCHEMA_VERSION = "3.9"


class PeriodEvidenceSchemaCompatibilityTests(unittest.TestCase):
    def test_new_schema_row_requires_new_engine(self) -> None:
        self.assertEqual(ENGINE_VERSION, "4.2.0")
        self.assertIn(PERIOD_EVIDENCE_SCHEMA_VERSION, SCHEMA_EMIT_ENGINES)
        # 4.1.x never emitted schema 3.9 — fail closed in read modes.
        self.assertFalse(
            validating_engine_allowed(PERIOD_EVIDENCE_SCHEMA_VERSION, "4.1.0", "output")
        )
        self.assertFalse(
            validating_engine_allowed(PERIOD_EVIDENCE_SCHEMA_VERSION, "4.1.1", "snapshot")
        )
        self.assertTrue(
            validating_engine_allowed(PERIOD_EVIDENCE_SCHEMA_VERSION, ENGINE_VERSION, "formal")
        )
        self.assertTrue(
            validating_engine_allowed(PERIOD_EVIDENCE_SCHEMA_VERSION, ENGINE_VERSION, "output")
        )

    def test_3_7_3_8_emit_history_is_preserved(self) -> None:
        for schema in (FORECAST_SCHEMA_VERSION, OPT_IN_SCHEMA_VERSION):
            for engine in ("4.1.0", "4.1.1", ENGINE_VERSION):
                self.assertTrue(
                    validating_engine_allowed(schema, engine, "output"),
                    f"{schema}/{engine} lost documented emit history",
                )
            self.assertFalse(validating_engine_allowed(schema, "9.9.9", "output"))

    def test_formal_mode_accepts_only_current_engine(self) -> None:
        for schema in (
            FORECAST_SCHEMA_VERSION,
            OPT_IN_SCHEMA_VERSION,
            PERIOD_EVIDENCE_SCHEMA_VERSION,
        ):
            self.assertTrue(validating_engine_allowed(schema, ENGINE_VERSION, "formal"))
            self.assertFalse(validating_engine_allowed(schema, "4.1.1", "formal"))
            self.assertFalse(validating_engine_allowed(schema, "9.9.9", "formal"))

    def test_registry_mirrors_supported_schema_constants(self) -> None:
        self.assertEqual(supported_schema_versions(), frozenset(SUPPORTED_FORECAST_SCHEMA_VERSIONS))
        self.assertIn(PERIOD_EVIDENCE_SCHEMA_VERSION, SUPPORTED_FORECAST_SCHEMA_VERSIONS)

    def test_declared_old_engine_still_validates_old_artifacts(self) -> None:
        # An old artifact pinned to its declared emitter keeps validating...
        require_validating_engine("3.7", "4.1.1", "output")
        require_validating_engine("3.8", "4.1.0", "snapshot")
        # ...and an undeclared engine for the same artifact fails closed.
        with self.assertRaises(Exception):
            require_validating_engine("3.7", "4.2.9", "output")


if __name__ == "__main__":
    unittest.main()
