"""R6-RF-INPUT I2: management target construction semantics.

Quarterly CC guidance, qualitative ranges (mid-single-digit / high-teens),
undated capacity goals and half-year constant-currency figures must enter the
ledger verbatim without being silently annualized. A quarter is not four
quarters; a qualitative label has no midpoint; a capacity plan is not a
revenue promise. Only an explicit, evidence-backed conversion may produce an
annual comparison value, and the original statement is never overwritten.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from revenue_core import ForecastInputError, run_forecast, text_sha256  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def _capture_of(data: dict) -> dict:
    return data["sources"][0]["capture"]


def _attach(data: dict, built: dict) -> dict:
    data["evidence_claims"].extend(built["claims"])
    data["management_targets"].append(built["target"])
    for index, record in enumerate(data["management_communication_coverage"]):
        if index == 0:
            record["material_revenue_target_ids"] = [built["target"]["target_id"]]
    return data


class BuildManagementTargetTests(unittest.TestCase):
    def setUp(self) -> None:
        from research.input_targets import build_management_target

        self.build = build_management_target
        self.data = forecast_document()
        self.capture = _capture_of(self.data)

    def _base_kwargs(self, **overrides) -> dict:
        kwargs = dict(
            target_id="t_quarterly",
            metric_name="revenue",
            metric_definition="recognized revenue",
            source_id="filing",
            locator="Results release, Q2 section",
            excerpt="Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
            raw_unit="USD million",
            raw_currency="USD",
            raw_scale="million",
            period_label="Q2 FY2026",
            measurement_basis="quarterly_period",
            target_quarter="Q2",
            commitment_strength="guidance",
            rationale="Quarterly actual disclosed in the results release.",
            measurement_rationale="Source states a single quarter; no annual basis is disclosed.",
            perimeter_notes="Company recognized revenue; quarterly basis.",
            statement="Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
            raw_value=40.0,
            source_capture=self.capture,
        )
        kwargs.update(overrides)
        return kwargs

    def test_quarterly_target_is_preserved_without_annual_comparison(self) -> None:
        built = self.build(self._base_kwargs()["statement"], **{
            k: v for k, v in self._base_kwargs().items() if k != "statement"
        })
        target = built["target"]
        # Verbatim preservation: the statement is never replaced by a conversion.
        self.assertEqual(target["statement"], self._base_kwargs()["statement"])
        self.assertEqual(target["measurement_basis"], "quarterly_period")
        self.assertEqual(target["target_quarter"], "Q2")
        self.assertEqual(target["measurement_periods"], [])
        self.assertIsNone(target.get("comparison_value"))
        self.assertEqual(target["treatment"], "unmodeled_data_gap")
        self.assertFalse(built["notes"]["comparable"])
        self.assertTrue(built["notes"]["reason_code"])

    def test_quarterly_target_never_produces_annual_comparison_in_engine(self) -> None:
        built = self.build(**self._base_kwargs())
        data = _attach(self.data, built)
        result = run_forecast(data)
        record = next(
            t for t in result["management_target_coverage"]["targets"]
            if t["target_id"] == "t_quarterly"
        )
        self.assertEqual(record["measurement_basis"], "quarterly_period")
        self.assertIsNone(record.get("comparison_value"))
        self.assertEqual(record["scenario_comparison"], {})
        self.assertIn(
            "management_target:t_quarterly",
            " ".join(result.get("data_gaps", [])) or " ".join(
                result["confidence"]["limitations"]
            ),
        )

    def test_quarterly_annualization_requires_evidence_backed_conversion(self) -> None:
        """A supported conversion (evidence-backed factor parameter) may produce a
        comparison value; a bare x0*4-style literal formula must be rejected."""
        built = self.build(**self._base_kwargs(
            measurement_periods=["FY2026"],
            conversion={
                "comparison_basis": "annual_recognized_revenue",
                "formula": "x0*4",
                "parameter_ids": [],
                "rationale": "Quarters are a quarter of the year.",
            },
        ))
        self.assertEqual(
            built["notes"].get("reject_reason"),
            "conversion_requires_evidence_backed_inputs",
        )

    def test_quarterly_with_supported_conversion_is_comparable(self) -> None:
        data = forecast_document()
        # A real, evidence-backed seasonality/currency exposure parameter.
        data["parameters"].append({
            "parameter_id": "q2_annual_exposure",
            "kind": "analyst_assumption",
            "value": 4.0,
            "unit": "ratio",
            "period": "FY2026",
            "definition": "evidence-backed annual exposure of Q2 disclosures",
            "scenario": "shared",
            "rationale": "Disclosed intra-year trajectory supports the exposure factor.",
            "source_ids": ["filing"],
        })
        data["parameters"][-1]["dimension"] = "ratio"
        from test_data_contract import apply_parameter_contract
        apply_parameter_contract(data, data["parameters"][-1], "ratio")
        exposure_claim = {
            "claim_id": "claim_q2_exposure",
            "source_id": "filing",
            "target_type": "parameter",
            "target_id": "q2_annual_exposure",
            "support_type": "rationale_support",
            "locator": "Results release, seasonality note",
            "excerpt": "Disclosed intra-year trajectory supports the annual exposure of Q2 disclosures.",
            "excerpt_sha256": text_sha256("Disclosed intra-year trajectory supports the annual exposure of Q2 disclosures."),
            "content_sha256": data["sources"][0]["capture"]["snapshot_sha256"],
            "capture_receipt_sha256": data["sources"][0]["capture"]["receipt_sha256"],
            "verification_status": "opened_and_checked",
            "verified_by": "input-semantics-test",
            "verified_date": data["as_of_date"],
        }
        data["evidence_claims"].append(exposure_claim)
        data["parameters"][-1]["claim_ids"] = ["claim_q2_exposure"]
        capture = _capture_of(data)
        built = self.build(
            "Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
            target_id="t_quarterly_conv",
            metric_name="revenue",
            metric_definition="recognized revenue",
            source_id="filing",
            locator="Results release, Q2 section",
            excerpt="Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
            verified_by="input-semantics-test",
            verified_date=data["as_of_date"],
            raw_unit="USD million",
            raw_currency="USD",
            raw_scale="million",
            period_label="Q2 FY2026",
            measurement_basis="quarterly_period",
            target_quarter="Q2",
            measurement_periods=["FY2026"],
            commitment_strength="guidance",
            rationale="Quarterly actual disclosed in the results release.",
            measurement_rationale="Conversion uses the disclosed annual exposure factor.",
            perimeter_notes="Company recognized revenue; quarterly basis.",
            raw_value=40.0,
            treatment="modeled_scenario",
            mapped_parameter_ids=["0_base_2026"],
            mapped_scenarios=["base"],
            conversion={
                "comparison_basis": "annual_recognized_revenue",
                "formula": "x0*x1",
                "parameter_ids": ["q2_annual_exposure"],
                "parameter_values": [4.0],
                "rationale": "Exposure factor converts the disclosed quarter to annual recognized revenue.",
            },
            source_capture=capture,
            comparison_currency="USD",
            comparison_scale="million",
        )
        self.assertTrue(built["notes"]["comparable"])
        self.assertAlmostEqual(built["target"]["comparison_value"], 160.0, places=9)
        # The raw statement and quarter label survive the conversion.
        self.assertEqual(built["target"]["target_quarter"], "Q2")
        self.assertEqual(
            built["target"]["statement"],
            "Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
        )
        _attach(data, built)
        result = run_forecast(data)
        record = next(
            t for t in result["management_target_coverage"]["targets"]
            if t["target_id"] == "t_quarterly_conv"
        )
        self.assertAlmostEqual(record["comparison_value"], 160.0, places=9)
        self.assertIn("base", record["scenario_comparison"])

    def test_qualitative_label_is_kept_verbatim_without_a_midpoint(self) -> None:
        built = self.build(
            "Management expects mid-single-digit revenue growth for FY2026.",
            target_id="t_qualitative",
            metric_name="revenue",
            metric_definition="recognized revenue growth",
            source_id="filing",
            locator="Earnings call, outlook",
            excerpt="Management expects mid-single-digit revenue growth for FY2026.",
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
            raw_unit="percent",
            raw_currency="USD",
            raw_scale="million",
            period_label="FY2026",
            measurement_basis="annual_period",
            measurement_periods=["FY2026"],
            target_period="FY2026",
            commitment_strength="guidance",
            rationale="Qualitative direction only.",
            measurement_rationale="Single annual period named by management.",
            perimeter_notes="Company revenue growth.",
            raw_label="mid-single-digit",
        )
        target = built["target"]
        self.assertEqual(target["raw_value_kind"], "qualitative_range")
        self.assertEqual(target["raw_label"], "mid-single-digit")
        self.assertIsNone(target.get("raw_target_value"))
        self.assertIsNone(target.get("comparison_value"))
        self.assertEqual(target["treatment"], "unmodeled_data_gap")
        self.assertTrue(target.get("unmodeled_reason"))

    def test_high_teens_label_and_numeric_range_have_no_invented_point(self) -> None:
        built = self.build(
            "Management targets high-teens segment revenue growth.",
            target_id="t_range",
            metric_name="revenue",
            metric_definition="segment revenue growth",
            source_id="filing",
            locator="Investor presentation, growth slide",
            excerpt="Management targets high-teens segment revenue growth.",
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
            raw_unit="percent",
            raw_currency="USD",
            raw_scale="million",
            period_label="FY2026-FY2028",
            measurement_basis="annual_period",
            measurement_periods=["FY2026"],
            target_period="FY2026",
            commitment_strength="goal",
            rationale="Range guidance without disclosed endpoints.",
            measurement_rationale="First in-horizon year named by the source.",
            perimeter_notes="Segment growth; perimeter reconciled separately.",
            raw_label="high-teens",
        )
        self.assertEqual(built["target"]["raw_value_kind"], "qualitative_range")
        self.assertIsNone(built["target"].get("comparison_value"))

        built2 = self.build(
            "Management expects revenue of USD 38 to 42 million in FY2026.",
            target_id="t_numeric_range",
            metric_name="revenue",
            metric_definition="recognized revenue",
            source_id="filing",
            locator="Results release, outlook table",
            excerpt="Management expects revenue of USD 38 to 42 million in FY2026.",
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
            raw_unit="USD million",
            raw_currency="USD",
            raw_scale="million",
            period_label="FY2026",
            measurement_basis="annual_period",
            measurement_periods=["FY2026"],
            target_period="FY2026",
            commitment_strength="guidance",
            rationale="Range guidance; no single point disclosed.",
            measurement_rationale="Single annual period named by management.",
            perimeter_notes="Company recognized revenue.",
            raw_value_low=38.0,
            raw_value_high=42.0,
        )
        target2 = built2["target"]
        self.assertEqual(target2["raw_value_kind"], "numeric_range")
        self.assertAlmostEqual(target2["raw_target_value_low"], 38.0, places=9)
        self.assertAlmostEqual(target2["raw_target_value_high"], 42.0, places=9)
        self.assertIsNone(target2.get("comparison_value"))
        self.assertEqual(target2["treatment"], "unmodeled_data_gap")

    def test_undated_capacity_goal_is_not_a_revenue_promise(self) -> None:
        built = self.build(
            "The plant will reach full capacity of 200 thousand units when commissioned.",
            target_id="t_capacity",
            metric_name="capacity",
            metric_definition="production capacity at full ramp",
            source_id="filing",
            locator="Annual report, capacity section",
            excerpt="The plant will reach full capacity of 200 thousand units when commissioned.",
            verified_by="input-semantics-test",
            verified_date=self.data["as_of_date"],
            raw_unit="thousand units",
            raw_currency="USD",
            raw_scale="million",
            period_label="when commissioned",
            measurement_basis="ambiguous",
            commitment_strength="capacity_plan",
            rationale="No calendar year is disclosed; capacity is not revenue.",
            measurement_rationale="Source names no determinate period; basis unresolved.",
            perimeter_notes="Operating capacity, not recognized revenue.",
            raw_value=200.0,
        )
        target = built["target"]
        self.assertEqual(target["commitment_strength"], "capacity_plan")
        self.assertEqual(target["measurement_basis"], "ambiguous")
        self.assertEqual(target["treatment"], "unmodeled_data_gap")
        self.assertEqual(target["measurement_periods"], [])

    def test_capacity_plan_cannot_be_forced_into_a_modeled_scenario(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "capacity_plan|aspiration"):
            self.build(
                **self._base_kwargs(
                    target_id="t_capacity_modeled",
                    commitment_strength="capacity_plan",
                    measurement_basis="annual_period",
                    measurement_periods=["FY2026"],
                    target_period="FY2026",
                    treatment="modeled_scenario",
                )
            )
        with self.assertRaisesRegex(ForecastInputError, "capacity_plan|aspiration"):
            self.build(
                **self._base_kwargs(
                    target_id="t_aspiration_modeled",
                    commitment_strength="aspiration",
                    measurement_basis="annual_period",
                    measurement_periods=["FY2026"],
                    target_period="FY2026",
                    treatment="scenario_boundary",
                )
            )

    def test_gross_net_and_currency_basis_are_recorded(self) -> None:
        built = self.build(**self._base_kwargs(
            target_id="t_gross_net",
            presentation_basis="gross",
            currency_basis="constant_currency",
        ))
        self.assertEqual(built["target"]["presentation_basis"], "gross")
        self.assertEqual(built["target"]["currency_basis"], "constant_currency")
        with self.assertRaises(ForecastInputError):
            self.build(**self._base_kwargs(presentation_basis="sometimes_gross"))
        with self.assertRaises(ForecastInputError):
            self.build(**self._base_kwargs(currency_basis="whatever_fx"))

    def test_run_rate_target_without_conversion_stays_unmodeled(self) -> None:
        built = self.build(**self._base_kwargs(
            target_id="t_runrate",
            statement="Management said current ARR run-rate is USD 120 million.",
            excerpt="Management said current ARR run-rate is USD 120 million.",
            period_label="as of Q2 FY2026",
            measurement_basis="run_rate_at_period_end",
            raw_value=120.0,
        ))
        self.assertEqual(built["target"]["treatment"], "unmodeled_data_gap")
        self.assertIsNone(built["target"].get("comparison_value"))

    def test_claims_preserve_statement_and_bind_source(self) -> None:
        built = self.build(**self._base_kwargs())
        self.assertTrue(built["claims"])
        claim = built["claims"][0]
        self.assertEqual(claim["target_type"], "management_target")
        self.assertEqual(claim["target_id"], "t_quarterly")
        self.assertEqual(
            claim["excerpt"], "Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year."
        )
        self.assertEqual(claim["source_id"], "filing")
        self.assertEqual(
            claim["capture_receipt_sha256"], self.capture["receipt_sha256"]
        )
        self.assertEqual(claim["content_sha256"], self.capture["snapshot_sha256"])

    def test_invalid_enum_inputs_fail_closed(self) -> None:
        with self.assertRaises(ForecastInputError):
            self.build(**self._base_kwargs(measurement_basis="fortnightly"))
        with self.assertRaises(ForecastInputError):
            self.build(**self._base_kwargs(target_quarter="Q5"))
        with self.assertRaises(ForecastInputError):
            self.build(**self._base_kwargs(commitment_strength="wish"))
        with self.assertRaises(ForecastInputError):
            self.build(**self._base_kwargs(raw_value=-40.0))
        with self.assertRaises(ForecastInputError):
            self.build(**self._base_kwargs(
                raw_value_low=42.0, raw_value_high=38.0,
                target_id="t_inverted", statement="inverted range",
            ))


class QuarterlyLedgerEngineTests(unittest.TestCase):
    def test_ledger_with_quarterly_target_counts_it_unmodeled(self) -> None:
        from research.input_targets import build_management_target

        data = forecast_document()
        built = build_management_target(
            "Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
            target_id="t_quarterly",
            metric_name="revenue",
            metric_definition="recognized revenue",
            source_id="filing",
            locator="Results release, Q2 section",
            excerpt="Management stated Q2 FY2026 revenue reached USD 40 million, up 12 percent year over year.",
            verified_by="input-semantics-test",
            verified_date=data["as_of_date"],
            raw_unit="USD million",
            raw_currency="USD",
            raw_scale="million",
            period_label="Q2 FY2026",
            measurement_basis="quarterly_period",
            target_quarter="Q2",
            commitment_strength="guidance",
            rationale="Quarterly actual disclosed in the results release.",
            measurement_rationale="Source states a single quarter; no annual basis is disclosed.",
            perimeter_notes="Company recognized revenue; quarterly basis.",
            raw_value=40.0,
            source_capture=data["sources"][0]["capture"],
        )
        data["evidence_claims"].extend(built["claims"])
        data["management_targets"].append(built["target"])
        data["management_communication_coverage"][0]["material_revenue_target_ids"] = [
            "t_quarterly"
        ]
        result = run_forecast(data)
        counts = result["management_target_coverage"]["counts"]
        self.assertEqual(counts["targets_unmodeled"], 1)


if __name__ == "__main__":
    unittest.main()
