from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import generate_input_template as gen  # noqa: E402
import lint_input  # noqa: E402
from lint_input import CAPTURE_REQUIRED, TOP_LEVEL_REQUIRED  # noqa: E402

HEX64 = re.compile(r"[0-9a-f]{64}")
STRUCTURAL = {"top_level_shape", "capture_shape", "claim_shape", "parameter_shape", "reference"}


class TemplateTests(unittest.TestCase):
    def _skeleton(self) -> dict:
        return gen.build_template(
            name="Smoke Co", base_year=2025, forecast_years=[2026, 2027],
            currency="USD", unit="million", segment_names=["Core"],
        )

    def test_has_required_top_level_keys(self) -> None:
        skeleton = self._skeleton()
        for key in TOP_LEVEL_REQUIRED:
            self.assertIn(key, skeleton, key)

    def test_capture_has_exactly_nine_keys(self) -> None:
        capture = self._skeleton()["sources"][0]["capture"]
        self.assertEqual(set(capture), set(CAPTURE_REQUIRED))

    def test_sha256_placeholders_are_hex64(self) -> None:
        skeleton = self._skeleton()
        capture = skeleton["sources"][0]["capture"]
        self.assertTrue(HEX64.fullmatch(capture["receipt_sha256"]))
        self.assertTrue(HEX64.fullmatch(capture["snapshot_sha256"]))
        for claim in skeleton["evidence_claims"]:
            self.assertTrue(HEX64.fullmatch(claim["excerpt_sha256"]), claim["claim_id"])

    def test_segments_and_years_are_parameterized(self) -> None:
        skeleton = gen.build_template(
            name="X", base_year=2024, forecast_years=[2025, 2026, 2027],
            currency="CNY", unit="wan", segment_names=["A", "B"],
        )
        self.assertEqual([segment["name"] for segment in skeleton["segments"]], ["A", "B"])
        self.assertEqual(skeleton["base_year"], 2024)
        self.assertEqual(skeleton["forecast_years"], [2025, 2026, 2027])

    def test_skeleton_is_lint_clean_structurally(self) -> None:
        skeleton = self._skeleton()
        findings = [f for f in lint_input.lint(skeleton) if f["category"] in STRUCTURAL]
        self.assertEqual(findings, [], findings)

    def test_skeleton_has_nine_research_dims_and_six_comm_categories(self) -> None:
        skeleton = self._skeleton()
        self.assertEqual(len(skeleton["research_coverage"]), 9)
        self.assertEqual(len(skeleton["management_communication_coverage"]), 6)


class TemplateCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_cli_writes_valid_skeleton(self) -> None:
        root = Path(__file__).resolve().parents[1]
        out = os.path.join(self.dir, "skeleton.json")
        cmd = [
            sys.executable, str(root / "scripts" / "generate_input_template.py"),
            "--name", "Smoke Co", "--base-year", "2025",
            "--forecast-years", "2026", "2027",
            "--currency", "USD", "--unit", "million",
            "--segments", "Core", "--output", out,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(out, encoding="utf-8") as handle:
            skeleton = json.load(handle)
        self.assertEqual(set(skeleton["sources"][0]["capture"]), set(CAPTURE_REQUIRED))
        self.assertIn("schema_version", skeleton)


class MainInProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_main_writes_output_file(self) -> None:
        out = os.path.join(self.dir, "skeleton.json")
        rc = gen.main([
            "--name", "X", "--base-year", "2025", "--forecast-years", "2026", "2027",
            "--segments", "Core", "--output", out,
        ])
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(out))

    def test_main_writes_to_stdout(self) -> None:
        import io
        buffer = io.StringIO()
        original = sys.stdout
        sys.stdout = buffer
        try:
            rc = gen.main([
                "--name", "Stdout Co", "--base-year", "2025",
                "--forecast-years", "2026", "--segments", "A",
            ])
        finally:
            sys.stdout = original
        self.assertEqual(rc, 0)
        self.assertIn("Stdout Co", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
