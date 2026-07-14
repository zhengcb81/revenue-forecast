from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ForecastInputError, canonical_sha256, run_forecast  # noqa: E402
from revenue_report import render_markdown, validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


class OutputReportTests(unittest.TestCase):
    def test_valid_output_and_markdown(self) -> None:
        result = run_forecast(forecast_document())
        validate_forecast_output(result)
        markdown = render_markdown(result)
        self.assertIn("## 核心营收结论", markdown)
        self.assertIn("## 未来收入主要驱动力", markdown)
        self.assertIn("## 收入增长驱动树", markdown)
        self.assertIn("## 九维研究覆盖", markdown)
        self.assertIn("## 三情景经营驱动", markdown)
        self.assertIn("## 分部驱动与收入确认", markdown)
        self.assertIn("## 参数—证据claim映射", markdown)
        self.assertIn("## 参数来源", markdown)

    def test_tampered_research_coverage_counts_are_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["research_coverage"]["counts"]["modeled_driver"] += 1
        with self.assertRaisesRegex(ForecastInputError, "counts mismatch"):
            validate_forecast_output(result)

    def test_tampered_cagr_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["consolidated_forecast"]["base"]["cagr"] = 0.99
        with self.assertRaisesRegex(ForecastInputError, "CAGR mismatch"):
            validate_forecast_output(result)

    def test_tampered_bridge_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["consolidated_forecast"]["base"]["annual_revenue"]["2026"] += 1
        with self.assertRaisesRegex(ForecastInputError, "mismatch"):
            validate_forecast_output(result)

    def test_prohibited_non_revenue_key_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["valuation"] = {"multiple": 10}
        with self.assertRaisesRegex(ForecastInputError, "prohibited"):
            validate_forecast_output(result)

    def test_probability_tampering_is_rejected(self) -> None:
        data = forecast_document()
        data["scenario_probabilities"] = {"low": 0.25, "base": 0.5, "high": 0.25}
        data["probability_rationale"] = "test"
        result = run_forecast(data)
        tampered = copy.deepcopy(result)
        tampered["probability_weighted_forecast"]["annual_revenue"]["2026"] += 1
        with self.assertRaisesRegex(ForecastInputError, "probability-weighted"):
            validate_forecast_output(tampered)

    def test_parameter_trace_custom_key_is_not_prohibited(self) -> None:
        result = run_forecast(forecast_document())
        result["parameter_trace"][0]["profit"] = "source vocabulary only"
        result["result_sha256"] = canonical_sha256({key: value for key, value in result.items() if key != "result_sha256"})
        validate_forecast_output(result)

    def test_tampered_segment_recognition_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["segments"][0]["scenarios"]["base"]["recognized_revenue"]["2026"] = 9999
        result["result_sha256"] = canonical_sha256({key: value for key, value in result.items() if key != "result_sha256"})
        with self.assertRaisesRegex(ForecastInputError, "recognized revenue mismatch"):
            validate_forecast_output(result)

    def test_tampered_annual_growth_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        result["consolidated_forecast"]["base"]["annual_growth"]["2026"] = 123
        result["result_sha256"] = canonical_sha256({key: value for key, value in result.items() if key != "result_sha256"})
        with self.assertRaisesRegex(ForecastInputError, "annual growth mismatch"):
            validate_forecast_output(result)

    def test_tampered_growth_driver_impact_is_rejected_even_after_rehash(self) -> None:
        result = run_forecast(forecast_document())
        result["growth_driver_analysis"]["drivers"][0]["estimated_base_terminal_increment"] += 1
        result["result_sha256"] = canonical_sha256({key: value for key, value in result.items() if key != "result_sha256"})
        with self.assertRaisesRegex(ForecastInputError, "growth driver analysis recomputation mismatch"):
            validate_forecast_output(result)

    def test_missing_workflow_receipt_is_rejected(self) -> None:
        result = run_forecast(forecast_document())
        del result["workflow_compliance_receipt"]
        result["result_sha256"] = canonical_sha256({key: value for key, value in result.items() if key != "result_sha256"})
        with self.assertRaisesRegex(ForecastInputError, "workflow_compliance_receipt"):
            validate_forecast_output(result)

    def test_tampered_workflow_receipt_is_rejected_even_after_rehash(self) -> None:
        result = run_forecast(forecast_document())
        result["workflow_compliance_receipt"]["freeform_formal_output_allowed"] = True
        result["workflow_compliance_receipt"]["receipt_sha256"] = canonical_sha256({
            key: value for key, value in result["workflow_compliance_receipt"].items()
            if key != "receipt_sha256"
        })
        result["result_sha256"] = canonical_sha256({key: value for key, value in result.items() if key != "result_sha256"})
        with self.assertRaisesRegex(ForecastInputError, "workflow compliance receipt mismatch"):
            validate_forecast_output(result)


if __name__ == "__main__":
    unittest.main()
