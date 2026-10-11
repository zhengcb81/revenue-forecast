"""W05-RF-FLOW output-side tests: DAG entry, report, tamper resistance, registry.

A real dated contribution must travel the whole chain — input -> validate ->
formula DAG -> forecast (low/base/high) -> report -> published output/snapshot
readers — and a forged artifact must not pass just because it was rehashed:

* the contribution enters the forecast DAG through the explicit
  ``acquisition_contribution`` scope-change adjustment (group perimeter change
  is named, never silently merged);
* the report shows the real window dates, amount and sources — it never
  relabels a partial contribution as a full year;
* output tampering of dates, currency or scope against a frozen bound input is
  rejected even after recomputing ``result_sha256``;
* schema 3.10 is emitted only by the new engine 4.3.0 while 4.2.1 keeps its
  documented emit history for 3.7/3.8/3.9, and the 3.10 role-aware mechanism
  triangulation inherits the 3.9 rule without touching 3.7/3.8.

Fixture amounts are synthetic except the sealed control-window fact.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from contracts.evidence import ForecastInputError  # noqa: E402
from revenue_core import (  # noqa: E402
    ENGINE_VERSION,
    SKILL_VERSION,
    canonical_sha256,
    run_forecast,
    validate_document,
)
from revenue_report import (  # noqa: E402
    render_markdown,
    validate_forecast_output,
    validate_published_forecast,
)
from schema_compatibility import (  # noqa: E402
    SCHEMA_EMIT_ENGINES,
    require_validating_engine,
    validating_engine_allowed,
)
from test_m3_evidence_roles import role_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402
from test_w05_dated_contribution_contract import (  # noqa: E402
    DATED_SCHEMA,
    add_window_parameter,
    parameter,
    schema_3_10_document,
)

SCOPE_RATIONALE = (
    "pre-control window 2026-01-01..2026-05-30 is outside the group "
    "consolidation perimeter from control date 2026-05-31 (out-of-scope, not "
    "missing data, never zero-filled)"
)


def add_acquisition_adjustment(data: dict) -> dict[str, float]:
    """C1 as an explicit low/base/high DAG contribution per forecast year."""
    add_window_parameter(
        data, "cmp_post_2026", 1.29190208, "2026-05-31", "2026-06-30", 2026,
        definition="acquired entity revenue from control date to period end (purchase-to-end)",
    )
    expected: dict[str, float] = {}
    scenario_ids: dict[str, list[str]] = {"low": [], "base": [], "high": []}
    h2_values = {"low": 30.0, "base": 40.0, "high": 50.0}
    y2_values = {"low": 200.0, "base": 300.0, "high": 400.0}
    for scenario in ("low", "base", "high"):
        h2_id = f"cmp_h2_2026_{scenario}"
        add_window_parameter(
            data, h2_id, h2_values[scenario], "2026-07-01", "2026-12-31", 2026,
            kind="scenario_stress", claim=False,
            definition=f"H2 2026 contribution ({scenario}) under continued control",
            rationale="synthetic scenario stress; fixture amount, not a reported figure",
        )
        parameter(data, h2_id)["scenario"] = scenario
        fy_id = f"cmp_fy2026_{scenario}"
        add_window_parameter(
            data, fy_id, 1.29190208 + h2_values[scenario], "2026-01-01", "2026-12-31", 2026,
            kind="derived_fact", claim=False, formula="x0+x1",
            input_parameter_ids=["cmp_post_2026", h2_id],
            definition="full-year 2026 group contribution of the acquired entity",
            rationale=SCOPE_RATIONALE,
        )
        parameter(data, fy_id)["scenario"] = scenario
        y2_id = f"cmp_fy2027_{scenario}"
        add_window_parameter(
            data, y2_id, y2_values[scenario], "2027-01-01", "2027-12-31", 2027,
            kind="scenario_stress", claim=False,
            definition="full-year 2027 contribution under continued control",
            rationale="synthetic scenario stress; fixture amount, not a reported figure",
        )
        parameter(data, y2_id)["scenario"] = scenario
        scenario_ids[scenario] = [fy_id, y2_id]
        expected[scenario] = 1.29190208 + h2_values[scenario]
    data.setdefault("forecast_adjustments", []).append(
        {
            "name": "acq_scope_change",
            "category": "acquisition_contribution",
            "scenario_parameter_ids": scenario_ids,
        }
    )
    return expected


def rehashed(result: dict) -> dict:
    result["result_sha256"] = canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    )
    return result


class DatedContributionForecastTests(unittest.TestCase):
    def test_contribution_enters_low_base_high_dag_with_explicit_scope_change(self) -> None:
        data = schema_3_10_document()
        expected = add_acquisition_adjustment(data)
        reference = run_forecast(schema_3_10_document())
        result = run_forecast(data)
        validate_published_forecast(result, data)
        for scenario in ("low", "base", "high"):
            for year_index, year in enumerate((2026, 2027)):
                got = result["consolidated_forecast"][scenario]["annual_revenue"][str(year)]
                base = reference["consolidated_forecast"][scenario]["annual_revenue"][str(year)]
                wanted = expected[scenario] if year_index == 0 else {"low": 200.0, "base": 300.0, "high": 400.0}[scenario]
                # Hand check: the dated contribution adds exactly its own
                # window amount to the year — nothing is annualized or doubled.
                self.assertAlmostEqual(got - base, wanted, places=9)

    def test_same_window_contribution_value_passes_through_unscaled(self) -> None:
        data = schema_3_10_document()
        add_window_parameter(
            data, "cmp_post_2026", 1.29190208, "2026-05-31", "2026-06-30", 2026,
        )
        result = run_forecast(data)
        traced = next(
            item for item in result["parameter_trace"] if item["parameter_id"] == "cmp_post_2026"
        )
        self.assertEqual(traced["value"], 1.29190208)
        self.assertEqual(traced["period_start"], "2026-05-31")
        self.assertEqual(traced["period_end"], "2026-06-30")

    def test_report_shows_real_window_dates_amount_and_sources(self) -> None:
        data = schema_3_10_document()
        add_window_parameter(
            data, "cmp_post_2026", 1.29190208, "2026-05-31", "2026-06-30", 2026,
            definition="acquired entity revenue from control date to period end",
        )
        result = run_forecast(data)
        report = render_markdown(result)
        row = next(line for line in report.splitlines() if "cmp_post_2026" in line)
        self.assertIn("period_flow", row)
        self.assertIn("2026-05-31", row)
        self.assertIn("2026-06-30", row)
        self.assertIn("filing", row)
        # Never relabeled as an annual/full-year observation.
        self.assertNotIn("annual", row)
        self.assertIn("USD million", report)

    def test_output_tamper_dates_currency_and_scope_rejected_even_rehashed(self) -> None:
        data = schema_3_10_document()
        add_acquisition_adjustment(data)
        result = run_forecast(data)
        validate_published_forecast(result, data)

        dated = copy.deepcopy(result)
        target = next(
            item for item in dated["parameter_trace"] if item["parameter_id"] == "cmp_post_2026"
        )
        target["period_start"] = "2026-01-01"
        rehashed(dated)
        with self.assertRaises(ForecastInputError):
            validate_published_forecast(dated, data)

        currency = copy.deepcopy(result)
        currency["currency"] = "CNY"
        rehashed(currency)
        with self.assertRaises(ForecastInputError):
            validate_published_forecast(currency, data)

        scope = copy.deepcopy(result)
        scope["input_document"]["parameters"] = copy.deepcopy(data["parameters"])
        edited = next(
            item for item in scope["input_document"]["parameters"]
            if item["parameter_id"] == "cmp_post_2026"
        )
        edited["period_end"] = "2026-12-31"
        scope["input_sha256"] = canonical_sha256(scope["input_document"])
        rehashed(scope)
        with self.assertRaises(ForecastInputError):
            validate_published_forecast(scope, data)

    def test_bound_input_reader_still_consumes_3_10(self) -> None:
        data = schema_3_10_document()
        add_window_parameter(
            data, "cmp_post_2026", 1.29190208, "2026-05-31", "2026-06-30", 2026,
        )
        result = run_forecast(data)
        validate_forecast_output(result)  # embedded input_document reader
        self.assertEqual(result["schema_version"], DATED_SCHEMA)
        self.assertEqual(result["engine_version"], SKILL_VERSION)

    def test_snapshot_reader_roundtrip_and_tamper_rejection(self) -> None:
        import os
        import tempfile

        from revenue_backtest import create_snapshot, validate_snapshot

        data = schema_3_10_document()
        add_window_parameter(
            data, "cmp_post_2026", 1.29190208, "2026-05-31", "2026-06-30", 2026,
        )
        with tempfile.TemporaryDirectory() as scratch:
            previous = os.environ.get("REVENUE_PUBLICATION_REGISTRY")
            os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(
                Path(scratch) / "registry.jsonl"
            )
            try:
                snapshot = create_snapshot(data, "w05-fixture-v1")
                validate_snapshot(snapshot)
                forged = copy.deepcopy(snapshot)
                target = next(
                    item for item in forged["input_document"]["parameters"]
                    if item["parameter_id"] == "cmp_post_2026"
                )
                target["period_end"] = "2026-12-31"
                forged["input_sha256"] = canonical_sha256(forged["input_document"])
                with self.assertRaises(ForecastInputError):
                    validate_snapshot(forged)
            finally:
                if previous is None:
                    os.environ.pop("REVENUE_PUBLICATION_REGISTRY", None)
                else:
                    os.environ["REVENUE_PUBLICATION_REGISTRY"] = previous


class DatedContributionCompatibilityTests(unittest.TestCase):
    def test_engine_version_is_the_dated_contribution_release(self) -> None:
        self.assertEqual(SKILL_VERSION, "4.3.0")
        self.assertEqual(ENGINE_VERSION, SKILL_VERSION)
        self.assertEqual(SCHEMA_EMIT_ENGINES[DATED_SCHEMA], frozenset({ENGINE_VERSION}))

    def test_4_2_1_emit_history_is_preserved_after_the_bump(self) -> None:
        for schema in ("3.7", "3.8", "3.9"):
            for mode in ("output", "snapshot"):
                self.assertTrue(
                    validating_engine_allowed(schema, "4.2.1", mode),
                    f"{schema}/4.2.1 lost documented emit history",
                )
        self.assertTrue(validating_engine_allowed("3.9", "4.2.0", "output"))

    def test_3_10_requires_the_new_engine_and_cannot_be_issued_by_4_2_x(self) -> None:
        for engine in ("4.1.0", "4.1.1", "4.2.0", "4.2.1"):
            for mode in ("formal", "output", "snapshot"):
                self.assertFalse(
                    validating_engine_allowed(DATED_SCHEMA, engine, mode),
                    f"3.10 must not be issued by engine {engine} in {mode}",
                )
        for mode in ("formal", "output", "snapshot"):
            self.assertTrue(validating_engine_allowed(DATED_SCHEMA, ENGINE_VERSION, mode))
        with self.assertRaises(ForecastInputError):
            require_validating_engine(DATED_SCHEMA, "4.2.1", "output")

    def test_old_schema_artifacts_still_validate_unchanged(self) -> None:
        for version in ("3.7", "3.8", "3.9"):
            with self.subTest(version=version):
                data = forecast_document()
                data["schema_version"] = version
                result = run_forecast(data)
                validate_published_forecast(result, data)


class DatedContributionRoleTests(unittest.TestCase):
    def test_history_background_does_not_triangulate_on_3_10(self) -> None:
        data = role_document(
            DATED_SCHEMA,
            [
                {"roles": ["history_base"], "source_id": "filing", "evidence_type": "company_execution"},
                {"roles": ["history_base"], "source_id": "transcript", "evidence_type": "operating_metrics"},
            ],
        )
        validated = validate_document(data)
        driver = validated["growth_driver_tree"]["drivers"][0]
        self.assertEqual(driver["evidence_status"], "limited")

    def test_true_mechanism_support_triangulates_on_3_10(self) -> None:
        data = role_document(
            DATED_SCHEMA,
            [
                {"roles": ["mechanism_direction"], "source_id": "filing", "evidence_type": "company_execution"},
                {"roles": ["mechanism_direction"], "source_id": "transcript", "evidence_type": "operating_metrics"},
            ],
        )
        validated = validate_document(data)
        driver = validated["growth_driver_tree"]["drivers"][0]
        self.assertEqual(driver["evidence_status"], "triangulated")

    def test_legacy_3_7_semantics_are_not_silently_changed(self) -> None:
        data = role_document(
            "3.7",
            [
                {"roles": ["history_base"], "source_id": "filing", "evidence_type": "company_execution"},
                {"roles": ["history_base"], "source_id": "transcript", "evidence_type": "operating_metrics"},
            ],
        )
        validated = validate_document(data)
        driver = validated["growth_driver_tree"]["drivers"][0]
        self.assertEqual(driver["evidence_status"], "triangulated")


if __name__ == "__main__":
    unittest.main()
