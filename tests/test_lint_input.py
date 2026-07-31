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

from test_recognition_bridge import forecast_document  # noqa: E402
import lint_input  # noqa: E402


class LintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()

    def test_clean_doc_has_zero_findings(self) -> None:
        self.assertEqual(lint_input.lint(self.base), [])

    def test_detects_capture_field_shape(self) -> None:
        data = copy.deepcopy(self.base)
        data["sources"][0]["capture"]["bogus_key"] = "x"
        findings = lint_input.lint(data)
        self.assertTrue(any(f["category"] == "capture_shape" for f in findings), findings)

    def test_detects_missing_capture_key(self) -> None:
        data = copy.deepcopy(self.base)
        del data["sources"][0]["capture"]["captured_date"]
        findings = lint_input.lint(data)
        self.assertTrue(any(f["category"] == "capture_shape" for f in findings), findings)

    def test_detects_ghost_source_id(self) -> None:
        data = copy.deepcopy(self.base)
        data["parameters"][0]["source_ids"] = ["ghost_source"]
        findings = lint_input.lint(data)
        self.assertTrue(any("ghost_source" in f["message"] for f in findings), findings)

    def test_detects_claim_target_mismatch(self) -> None:
        data = copy.deepcopy(self.base)
        claim = next(c for c in data["evidence_claims"] if c["target_type"] == "parameter")
        claim["target_id"] = "segment_b_base"
        findings = lint_input.lint(data)
        self.assertTrue(
            any(f["category"] == "reference" and "does not support" in f["message"] for f in findings),
            findings,
        )

    def test_detects_stale_receipt_and_excerpt_hashes(self) -> None:
        data = copy.deepcopy(self.base)
        data["sources"][0]["capture"]["receipt_sha256"] = "0" * 64
        data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64
        findings = lint_input.lint(data)
        self.assertGreaterEqual([f["category"] for f in findings].count("hash"), 2, findings)

    def test_detects_attribution_weight_not_one(self) -> None:
        data = copy.deepcopy(self.base)
        data["growth_driver_tree"]["drivers"][0]["segment_attribution"][0]["weight"] = 0.8
        findings = lint_input.lint(data)
        self.assertTrue(
            any(f["category"] == "aggregate" and "weight" in f["message"] for f in findings),
            findings,
        )

    def test_collect_all_reports_independent_violations(self) -> None:
        data = copy.deepcopy(self.base)
        data["parameters"][0]["source_ids"] = ["ghost_source"]
        data["evidence_claims"][0]["excerpt_sha256"] = "0" * 64
        data["growth_driver_tree"]["drivers"][0]["segment_attribution"][0]["weight"] = 0.8
        findings = lint_input.lint(data)
        categories = {f["category"] for f in findings}
        self.assertIn("reference", categories)
        self.assertIn("hash", categories)
        self.assertIn("aggregate", categories)
        self.assertGreaterEqual(len(findings), 3)


class LintCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()
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
        cmd = [sys.executable, str(root / "scripts" / "lint_input.py"), *args]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_clean_doc_exit_0(self) -> None:
        result = self._run(self._write(copy.deepcopy(self.base)))
        self.assertEqual(result.returncode, 0)

    def test_findings_exit_2(self) -> None:
        data = copy.deepcopy(self.base)
        data["parameters"][0]["source_ids"] = ["ghost_source"]
        result = self._run(self._write(data))
        self.assertEqual(result.returncode, 2)
        self.assertIn("ghost_source", result.stdout + result.stderr)


class MainInProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = forecast_document()
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _path(self, data: dict) -> str:
        path = os.path.join(self.dir, "i.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False)
        return path

    def test_main_clean_returns_0(self) -> None:
        self.assertEqual(lint_input.main([self._path(copy.deepcopy(self.base))]), 0)

    def test_main_findings_return_2(self) -> None:
        data = copy.deepcopy(self.base)
        data["parameters"][0]["source_ids"] = ["ghost_source"]
        self.assertEqual(lint_input.main([self._path(data)]), 2)

    def test_main_bad_json_returns_2(self) -> None:
        path = os.path.join(self.dir, "bad.json")
        Path(path).write_text("{x", encoding="utf-8")
        self.assertEqual(lint_input.main([path]), 2)

    def test_main_non_object_input_returns_2(self) -> None:
        path = os.path.join(self.dir, "arr.json")
        Path(path).write_text("[1, 2, 3]", encoding="utf-8")
        self.assertEqual(lint_input.main([path]), 2)


if __name__ == "__main__":
    unittest.main()
