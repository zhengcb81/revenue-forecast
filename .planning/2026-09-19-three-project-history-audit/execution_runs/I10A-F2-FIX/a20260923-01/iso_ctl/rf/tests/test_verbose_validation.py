from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import (  # noqa: E402
    Collector,
    ForecastInputError,
    MultiValidationError,
    validate_document,
)
from test_recognition_bridge import forecast_document  # noqa: E402


class VerboseValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()

    def test_default_path_still_fails_fast_with_single_error(self) -> None:
        data = copy.deepcopy(self.base)
        data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64
        data["evidence_claims"][1]["excerpt_sha256"] = "0" * 64
        with self.assertRaises(ForecastInputError) as ctx:
            validate_document(data)
        self.assertNotIsInstance(ctx.exception, MultiValidationError)
        self.assertNotIn("validation problem(s) found", str(ctx.exception))

    def test_collector_gathers_multiple_within_gate(self) -> None:
        data = copy.deepcopy(self.base)
        data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64
        data["evidence_claims"][1]["excerpt_sha256"] = "0" * 64
        with self.assertRaises(MultiValidationError) as ctx:
            validate_document(data, collector=Collector())
        excerpt_errors = [m for _, m in ctx.exception.errors if "excerpt" in m]
        self.assertGreaterEqual(len(excerpt_errors), 2, ctx.exception.errors)

    def test_collector_gathers_across_gates(self) -> None:
        data = copy.deepcopy(self.base)
        data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64
        data["growth_driver_tree"]["drivers"][0]["segment_attribution"][0]["weight"] = 0.8
        with self.assertRaises(MultiValidationError) as ctx:
            validate_document(data, collector=Collector())
        gates = {gate for gate, _ in ctx.exception.errors}
        self.assertIn("evidence_claims", gates)
        self.assertIn("growth_driver_tree", gates)

    def test_collector_survives_gate_crash_without_propagating(self) -> None:
        data = copy.deepcopy(self.base)
        del data["base_year"]
        with self.assertRaises(MultiValidationError):
            validate_document(data, collector=Collector())

    def test_clean_doc_with_collector_returns_indexes(self) -> None:
        result = validate_document(copy.deepcopy(self.base), collector=Collector())
        self.assertIn("years", result)
        self.assertIn("parameter_index", result)


class VerboseCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write(self, data: dict) -> str:
        path = os.path.join(self.dir, "input.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        return path

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        root = Path(__file__).resolve().parents[1]
        cmd = [sys.executable, str(root / "scripts" / "revenue_forecast.py"), *args]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_verbose_reports_all_and_writes_nothing(self) -> None:
        data = forecast_document()
        data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64
        data["growth_driver_tree"]["drivers"][0]["segment_attribution"][0]["weight"] = 0.8
        out = os.path.join(self.dir, "out.json")
        result = self._run(self._write(data), "--validate-only", "--verbose", "--output", out)
        self.assertEqual(result.returncode, 2)
        self.assertIn("validation problem(s) found", result.stderr)
        self.assertFalse(os.path.exists(out))

    def test_verbose_clean_doc_is_valid(self) -> None:
        result = self._run(self._write(forecast_document()), "--validate-only", "--verbose")
        self.assertEqual(result.returncode, 0)
        self.assertIn("valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
