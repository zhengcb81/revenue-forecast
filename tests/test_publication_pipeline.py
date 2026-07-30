"""Adversarial tests for the formal publication pipeline (Phase 1, task_plan.md).

These tests pin the boundary between an executed forecast and a *published*
forecast:

* ``run_forecast`` must not hand back a receipt that certifies the
  ``output_recomputation`` gate before that gate has actually run.
* The CLI must not persist a JSON artifact when publication validation fails.
* The Markdown renderer must refuse any result that has not passed output
  validation.

The first test is a deliberate RED: it exposes that ``run_forecast`` signs a
``status="pass"`` receipt citing ``output_recomputation`` even though
``validate_forecast_output`` is never called inside ``run_forecast``. The other
two are guard rails that pin the CLI/renderer behavior the publication pipeline
must preserve once Phase 2 splits execution from publication receipts.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import (  # noqa: E402
    ForecastInputError,
    _build_forecast_draft,
    canonical_sha256,
    run_forecast,
)
from revenue_report import render_markdown, validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


SKILL_ROOT = Path(__file__).resolve().parents[1]


class PublicationPipelineTests(unittest.TestCase):
    def test_public_api_never_returns_pass_receipt_before_output_validation(self) -> None:
        # RED: run_forecast must not sign a receipt that certifies the
        # output_recomputation gate as passed, because validate_forecast_output
        # is never called inside run_forecast. Today the returned receipt carries
        # status="pass" and lists "output_recomputation" in gate_ids.
        result = run_forecast(forecast_document())
        receipt = result["workflow_compliance_receipt"]
        self.assertFalse(
            receipt.get("status") == "pass"
            and "output_recomputation" in receipt.get("gate_ids", []),
            "run_forecast signed a 'pass' receipt citing output_recomputation before output validation ran",
        )

    def test_cli_does_not_write_json_when_publication_validation_fails(self) -> None:
        # Guard rail: the input contract admits appended custom research
        # dimensions (>= 9 required) while the output contract requires exactly
        # nine, so run_forecast admits this input but validate_forecast_output
        # rejects it. The CLI must exit non-zero and leave no output JSON behind.
        data = forecast_document()
        data["research_coverage"].append({
            "dimension": "",
            "status": "immaterial",
            "conclusion": "Not material to near-term revenue.",
            "revenue_mechanism": "no revenue mechanism",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "Out of scope for this revenue forecast.",
        })
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.json"
            output_path = root / "forecast.json"
            input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SKILL_ROOT / "scripts" / "revenue_forecast.py"),
                 str(input_path), "--output", str(output_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("non-empty string", completed.stderr)
            self.assertFalse(output_path.exists())

    def test_markdown_is_only_rendered_from_published_json(self) -> None:
        # Guard rail: render_markdown must refuse any result that has not passed
        # output validation, so a tampered-and-rehashed artifact cannot be
        # rendered into a human-facing report.
        result = run_forecast(forecast_document())
        result["consolidated_forecast"]["base"]["cagr"] = 0.99
        result["result_sha256"] = canonical_sha256({key: value for key, value in result.items() if key != "result_sha256"})
        with self.assertRaisesRegex(ForecastInputError, "CAGR mismatch"):
            render_markdown(result)

    def test_draft_carries_no_publication_receipt(self) -> None:
        # The private draft carries the execution receipt only: no publication
        # receipt and no result hash. Publication is run_forecast's job.
        draft = _build_forecast_draft(forecast_document())
        self.assertNotIn("publication_receipt", draft)
        self.assertNotIn("result_sha256", draft)
        self.assertNotIn("output_recomputation", draft["workflow_compliance_receipt"]["gate_ids"])

    def test_run_forecast_result_carries_valid_publication_receipt(self) -> None:
        # Every normal run_forecast return is a published result: it carries a
        # formal publication receipt whose output gate is honestly claimed.
        result = run_forecast(forecast_document())
        receipt = result["publication_receipt"]
        self.assertEqual(receipt["formal_output_mode"], "formal")
        self.assertFalse(receipt["freeform_override_allowed"])
        self.assertIn("output_recomputation", receipt["gate_ids"])
        validate_forecast_output(result)

    def test_publication_receipt_tampering_is_rejected(self) -> None:
        # Flipping freeform_override_allowed and recomputing every hash must
        # still be rejected: the receipt's own field contract is enforced.
        result = run_forecast(forecast_document())
        receipt = result["publication_receipt"]
        receipt["freeform_override_allowed"] = True
        receipt["receipt_sha256"] = canonical_sha256(
            {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        )
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaisesRegex(ForecastInputError, "publication_receipt freeform_override_allowed"):
            validate_forecast_output(result)

    def test_publication_receipt_is_deterministic(self) -> None:
        # The same input must yield byte-identical publication receipts and
        # result hashes across independent runs.
        first = run_forecast(forecast_document())
        second = run_forecast(forecast_document())
        self.assertEqual(first["publication_receipt"], second["publication_receipt"])
        self.assertEqual(first["result_sha256"], second["result_sha256"])

    def test_run_forecast_rejects_unpublishable_result(self) -> None:
        # run_forecast publishes only after output validation; an input whose
        # result fails the output validator (custom research dimension, which the
        # input contract admits but the output contract rejects) must raise.
        data = forecast_document()
        data["research_coverage"].append({
            "dimension": "",
            "status": "immaterial",
            "conclusion": "Not material to near-term revenue.",
            "revenue_mechanism": "no revenue mechanism",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "Out of scope for this revenue forecast.",
        })
        with self.assertRaisesRegex(ForecastInputError, "non-empty string"):
            run_forecast(data)

    def test_custom_research_dimension_is_accepted(self) -> None:
        # A valid custom dimension (non-empty, unique, appended after the nine
        # core dimensions) must pass output validation.
        data = forecast_document()
        data["research_coverage"].append({
            "dimension": "esg_capital_allocation",
            "status": "immaterial",
            "conclusion": "Not material to near-term revenue.",
            "revenue_mechanism": "no revenue mechanism",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "Out of scope for this revenue forecast.",
        })
        result = run_forecast(data)
        self.assertEqual(len(result["research_coverage"]["dimensions"]), 10)
        validate_forecast_output(result)

    def test_null_research_dimension_is_rejected(self) -> None:
        # A custom dimension whose name is not a string must be rejected.
        data = forecast_document()
        data["research_coverage"].append({
            "dimension": None,
            "status": "immaterial",
            "conclusion": "Not material.",
            "revenue_mechanism": "none",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "out of scope",
        })
        with self.assertRaisesRegex(ForecastInputError, "non-empty string"):
            run_forecast(data)

    def test_duplicate_core_research_dimension_is_rejected(self) -> None:
        # A custom dimension that reuses a core dimension name must be rejected.
        data = forecast_document()
        data["research_coverage"].append({
            "dimension": "growth_curve",
            "status": "immaterial",
            "conclusion": "Duplicate.",
            "revenue_mechanism": "none",
            "parameter_ids": [],
            "source_ids": [],
            "rationale": "duplicate",
        })
        with self.assertRaisesRegex(ForecastInputError, "duplicate"):
            run_forecast(data)

    def test_source_horizon_gap_is_rejected(self) -> None:
        # A source whose coverage horizon ends before a forecast year that
        # references it must be rejected at input validation.
        data = forecast_document()
        data["sources"][0]["covers_until"] = "FY2025"
        with self.assertRaisesRegex(ForecastInputError, "covers only until"):
            run_forecast(data)

    def test_assumption_requires_rationale_support(self) -> None:
        # A source-linked assumption/stress parameter must have at least one
        # rationale-support claim; an exact_value claim alone is not sufficient.
        data = forecast_document()
        for param in data["parameters"]:
            if param["kind"] == "analyst_assumption" and param.get("source_ids"):
                param["claim_ids"] = []
                break
        with self.assertRaisesRegex(ForecastInputError, "rationale-support"):
            run_forecast(data)

    def test_unknown_base_adjustment_is_rejected(self) -> None:
        # A base_adjustment_parameter_id that does not exist in the parameter
        # index must raise a controlled ForecastInputError, not a KeyError.
        data = forecast_document()
        data["base_adjustment_parameter_ids"] = ["nonexistent_adjustment"]
        with self.assertRaisesRegex(ForecastInputError, "unknown base_adjustment_parameter_id"):
            run_forecast(data)

    def test_sensitivity_completeness_rejects_uncovered_parameter(self) -> None:
        # When completeness is required, an eligible base parameter that is
        # neither sensitivity-tested nor excluded must be rejected.
        data = forecast_document()
        tested_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
        data["sensitivity_tests"] = [{"name": "Core terminal", "parameter_id": tested_id, "shock_type": "percent", "shock_value": 0.1}]
        data["require_sensitivity_completeness"] = True
        with self.assertRaisesRegex(ForecastInputError, "completeness required"):
            run_forecast(data)

    def test_sensitivity_completeness_accepts_excluded_parameter(self) -> None:
        # A structured exclusion (reason + rationale) satisfies the completeness
        # gate for parameters that are not sensitivity-tested.
        data = forecast_document()
        tested_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
        data["sensitivity_tests"] = [{"name": "Core terminal", "parameter_id": tested_id, "shock_type": "percent", "shock_value": 0.1}]
        data["require_sensitivity_completeness"] = True
        all_base_ids = [
            pid
            for segment in data["segments"]
            for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values()
            for pid in ids
        ]
        data["sensitivity_exclusions"] = [
            {"parameter_id": pid, "reason": "immaterial", "rationale": "Not a primary terminal driver."}
            for pid in all_base_ids if pid != tested_id
        ]
        result = run_forecast(data)
        validate_forecast_output(result)


if __name__ == "__main__":
    unittest.main()
