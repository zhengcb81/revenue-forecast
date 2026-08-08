from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ENGINE_VERSION, FORECAST_SCHEMA_VERSION  # noqa: E402
from schema_compatibility import (  # noqa: E402
    require_validating_engine,
    supported_schema_versions,
    validating_engine_allowed,
)


class SchemaCompatibilityRegistryTests(unittest.TestCase):
    def test_current_schema_accepts_only_current_engine(self) -> None:
        self.assertTrue(
            validating_engine_allowed(FORECAST_SCHEMA_VERSION, ENGINE_VERSION, "output")
        )
        self.assertFalse(
            validating_engine_allowed(FORECAST_SCHEMA_VERSION, "9.9.9", "output")
        )

    def test_legacy_schema_accepts_documented_emit_engines(self) -> None:
        # CHANGELOG: schema 3.4 was emitted by engines 3.5.0..3.10.0.
        for engine in ("3.5.0", "3.6.0", "3.7.0", "3.8.0", "3.9.0", "3.10.0"):
            self.assertTrue(
                validating_engine_allowed("3.4", engine, "output"),
                f"schema 3.4 should accept engine {engine}",
            )
        self.assertFalse(validating_engine_allowed("3.4", "3.4.0", "output"))
        self.assertFalse(validating_engine_allowed("3.4", "9.9.9", "output"))

    def test_formal_mode_accepts_only_current_engine(self) -> None:
        for schema in (
            "3.0",
            "3.1",
            "3.2",
            "3.3",
            "3.4",
            "3.5",
            FORECAST_SCHEMA_VERSION,
        ):
            self.assertFalse(
                validating_engine_allowed(schema, "9.9.9", "formal"),
                f"formal mode must reject unknown engine for {schema}",
            )
        self.assertTrue(
            validating_engine_allowed(FORECAST_SCHEMA_VERSION, ENGINE_VERSION, "formal")
        )

    def test_unknown_schema_fails_closed(self) -> None:
        self.assertFalse(validating_engine_allowed("2.0", ENGINE_VERSION, "output"))
        self.assertFalse(validating_engine_allowed("3.8", ENGINE_VERSION, "snapshot"))

    def test_non_string_engine_fails_closed(self) -> None:
        self.assertFalse(validating_engine_allowed("3.4", 3.10, "output"))
        self.assertFalse(validating_engine_allowed("3.4", None, "output"))

    def test_registry_matches_supported_schema_set(self) -> None:
        self.assertEqual(
            supported_schema_versions(),
            {"3.0", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", FORECAST_SCHEMA_VERSION},
        )

    def test_require_validating_engine_raises_on_unknown(self) -> None:
        with self.assertRaises(Exception):
            require_validating_engine("3.4", "9.9.9", "snapshot")


if __name__ == "__main__":
    unittest.main()
