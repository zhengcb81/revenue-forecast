"""W16-RF-BASIS B06: the public CLI end to end on the frozen behavior matrix.

Every case runs the real ``scripts/revenue_forecast.py`` in its own exclusive
temporary directory (one of them contains Chinese characters and a space);
assertions check the concrete diagnostics and result content, never the
exit code alone. Case inputs are synthetic but complete RF documents built
by the shared test builders.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from test_recognition_bridge import forecast_document  # noqa: E402
from test_w16_revenue_basis import (  # noqa: E402
    _add_component_claims,
    _basis,
    _record_for_year,
)


def _claim_for(data: dict, year: int) -> dict:
    claim_id = f"claim_history_{year}"
    return next(
        claim
        for claim in data["evidence_claims"]
        if claim["claim_id"] == claim_id
    )


class CliCaseRunner(unittest.TestCase):
    """Shared runner: one exclusive directory per case, real CLI subprocess."""

    def setUp(self) -> None:
        self._root = Path(
            tempfile.mkdtemp(prefix="w16_cli_", dir=tempfile.gettempdir())
        )

    def tearDown(self) -> None:
        # Cleanup only this run's exclusive root, verified to live in the
        # system temp directory before any removal (COMMON §5).
        resolved = str(self._root.resolve())
        assert resolved.startswith(
            str(Path(tempfile.gettempdir()).resolve())
        ), f"refusing to clean non-temp path: {resolved}"
        shutil.rmtree(self._root, ignore_errors=True)

    def _run(
        self,
        data: dict,
        *,
        case_dir: str,
        expect_success: bool,
    ) -> subprocess.CompletedProcess[str]:
        directory = self._root / case_dir
        directory.mkdir()
        environment = dict(os.environ)
        environment["REVENUE_PUBLICATION_REGISTRY"] = str(directory / "registry")
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        input_path = directory / "input.json"
        output_path = directory / "forecast.json"
        markdown_path = directory / "forecast.md"
        input_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "revenue_forecast.py"),
                str(input_path),
                "--output",
                str(output_path),
                "--markdown",
                str(markdown_path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
            check=False,
        )
        if expect_success:
            self.assertEqual(
                completed.returncode,
                0,
                f"CLI failed unexpectedly: {completed.stderr}",
            )
            self.assertTrue(output_path.exists())
            self.assertTrue(markdown_path.exists())
        else:
            self.assertEqual(completed.returncode, 2)
            self.assertFalse(output_path.exists())
        return completed

    def _output(self, case_dir: str) -> dict:
        return json.loads(
            (self._root / case_dir / "forecast.json").read_text(encoding="utf-8")
        )

    def _markdown(self, case_dir: str) -> str:
        return (self._root / case_dir / "forecast.md").read_text(encoding="utf-8")


class SameBasisSuite(CliCaseRunner):
    """同口径正常 + 明确有桥 + 币种尺度转换：成功且结果携带口径。"""

    def test_same_basis_with_bridge_and_conversion_succeeds(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2024)["revenue_basis"] = _basis()
        parts = [
            {"operations": "continuing", "value": 100.0, "source_ids": ["filing"]},
            {"operations": "discontinued", "value": 50.0, "source_ids": ["filing"]},
        ]
        _add_component_claims(data, 2025, parts)
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            input_quantity={
                "schema_version": "rf-input-quantity/1",
                "value": 0.15,
                "input_unit": "USD billion",
                "engine_unit": "USD million",
                "engine_value": 150.0,
                "conversion": "0.15 usd_billion x 1000 = 150 usd_million",
            },
            components=parts,
        )
        completed = self._run(
            data, case_dir="基期 口格 same basis", expect_success=True
        )
        self.assertEqual(completed.stderr, "")
        output = self._output("基期 口格 same basis")
        basis_records = [
            record.get("revenue_basis") for record in output["historical_revenue"]
        ]
        self.assertEqual(basis_records[0]["operations"], "total")
        self.assertEqual(basis_records[1]["operations"], "total")
        self.assertEqual(
            basis_records[1]["input_quantity"]["engine_value"], 150.0
        )
        markdown = self._markdown("基期 口格 same basis")
        self.assertIn("总额/原表", markdown)
        self.assertIn("口径可比性", markdown)
        self.assertIn("同口径可比", markdown)
        self.assertIn("基数采用", markdown)
        self.assertIn("usd_billion", markdown)
        self.assertIn("与报告总额参数一致", markdown)


class ErrorSuite(CliCaseRunner):
    """具体错误：断言 stderr 消息，不只退出码。"""

    def test_continuing_operations_as_base_is_rejected(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            operations="continuing"
        )
        completed = self._run(
            data, case_dir="err_continuing", expect_success=False
        )
        self.assertIn("continuing", completed.stderr)
        self.assertIn("total", completed.stderr)

    def test_quarter_period_kind_is_rejected(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2024)["revenue_basis"] = _basis(
            period_kind="quarter"
        )
        completed = self._run(
            data, case_dir="err_quarter", expect_success=False
        )
        self.assertIn("quarter", completed.stderr)
        self.assertIn("fiscal", completed.stderr)

    def test_conversion_mismatch_is_rejected(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            input_quantity={
                "schema_version": "rf-input-quantity/1",
                "value": 0.15,
                "input_unit": "USD billion",
                "engine_unit": "USD million",
                "engine_value": 999.0,
                "conversion": "0.15 usd_billion x 1000 = 999 usd_million",
            }
        )
        completed = self._run(
            data, case_dir="err_conversion", expect_success=False
        )
        self.assertIn("input_quantity", completed.stderr)
        self.assertIn("999", completed.stderr)


class DiagnosticsSuite(CliCaseRunner):
    """成功但诊断必须如实：无桥不可比、有桥可比、零基数、legacy。"""

    def test_restated_without_bridge_is_flagged_not_comparable(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2024)["revenue_basis"] = _basis()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            statement_status="restated"
        )
        self._run(data, case_dir="diag_no_bridge", expect_success=True)
        markdown = self._markdown("diag_no_bridge")
        self.assertIn("不可比", markdown)
        self.assertIn("statement_status", markdown)
        self.assertIn("重述", markdown)
        output = self._output("diag_no_bridge")
        # 观测值保留，不因口径不可比被丢弃或改写。
        self.assertEqual(
            [record["value"] for record in output["historical_revenue"]],
            [140, 150],
        )

    def test_matching_restatements_are_comparable(self) -> None:
        data = forecast_document()
        for record in data["historical_revenue"]:
            record["revenue_basis"] = _basis(statement_status="restated")
        self._run(data, case_dir="diag_bridged", expect_success=True)
        markdown = self._markdown("diag_bridged")
        self.assertIn("同口径可比", markdown)
        self.assertIn("重述", markdown)

    def test_zero_comparison_base_reports_undefined_growth(self) -> None:
        data = forecast_document()
        record = _record_for_year(data, 2024)
        record["value"] = 0.0
        _claim_for(data, 2024)["extracted_value"] = 0.0
        record["revenue_basis"] = _basis()
        _record_for_year(data, 2025)["revenue_basis"] = _basis()
        self._run(data, case_dir="diag_zero_base", expect_success=True)
        markdown = self._markdown("diag_zero_base")
        self.assertIn("同比未定义", markdown)
        self.assertIn("zero", markdown)

    def test_legacy_without_metadata_keeps_engine_behavior(self) -> None:
        data = forecast_document()
        self._run(data, case_dir="diag_legacy", expect_success=True)
        output = self._output("diag_legacy")
        self.assertIn("historical_revenue", output)
        self.assertEqual(
            [record["value"] for record in output["historical_revenue"]],
            [140, 150],
        )
        self.assertNotIn("revenue_basis", output["historical_revenue"][0])
        markdown = self._markdown("diag_legacy")
        self.assertIn("未声明", markdown)
        self.assertNotIn("已核实可比", markdown)


if __name__ == "__main__":
    unittest.main()
