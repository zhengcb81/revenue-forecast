"""M3-FLOW contract tests: explicit dated period flows (schema 3.9 opt-in).

Root cause R20: TIME_BASES only had annual/point_in_time, so at least 18 real
half-year revenue flows (HK 10 H1 + 5 H2, CN 3 H1) were labeled ``annual``.
The new contract is additive and versioned:

* ``time_basis=period_flow`` with ``period_start``/``period_end`` is accepted
  ONLY on schema 3.9; 3.7/3.8 keep rejecting it (no silent widening).
* The dates must be valid ISO days, strictly ordered, inside the fiscal-year
  window implied by ``fiscal_year_end`` (this covers cross-calendar-year and
  non-calendar fiscal years), and the covered length must be 3, 6 or 12
  calendar months. Amounts belong to the covered period — no implicit
  annualization (x2) anywhere.
* ``period_start``/``period_end`` on any non-period_flow parameter are
  rejected in every schema; point-in-time stocks keep their old semantics.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from contracts.constants import (  # noqa: E402
    OPT_IN_SCHEMA_VERSION,
    SKILL_VERSION,
)
from contracts.evidence import ForecastInputError  # noqa: E402
from contracts.period_flow import (  # noqa: E402
    fiscal_year_window,
    period_flow_months,
    validate_period_flow_fields,
)
from revenue_core import (  # noqa: E402
    run_forecast,
    text_sha256,
    validate_document,
)
from revenue_report import render_markdown, validate_published_forecast  # noqa: E402
from test_data_contract import apply_parameter_contract, finalize_contract  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

PERIOD_EVIDENCE_SCHEMA_VERSION = "3.9"


def schema_3_9_document() -> dict:
    data = forecast_document()
    data["schema_version"] = PERIOD_EVIDENCE_SCHEMA_VERSION
    return data


def add_flow_parameter(
    data: dict,
    parameter_id: str,
    value: float,
    start: str,
    end: str,
    year: int,
    *,
    kind: str = "reported_fact",
    definition: str | None = None,
    time_basis: str = "period_flow",
) -> str:
    parameter = {
        "parameter_id": parameter_id,
        "kind": kind,
        "value": value,
        "unit": "USD million",
        "period": f"FY{year}",
        "definition": definition
        or f"{parameter_id} recognized flow over {start}..{end}",
        "scenario": None,
        "source_ids": ["filing"],
    }
    if kind == "analyst_assumption":
        parameter["rationale"] = "synthetic flow fixture"
    apply_parameter_contract(data, parameter, "revenue")
    # apply_parameter_contract forces time_basis="annual"; the typed flow
    # basis and its dates are set after the monetary contract fields.
    parameter["time_basis"] = time_basis
    parameter["period_start"] = start
    parameter["period_end"] = end
    if kind == "reported_fact":
        data["evidence_claims"].append(
            {
                "claim_id": f"claim_parameter_{parameter_id}",
                "source_id": "filing",
                "target_type": "parameter",
                "target_id": parameter_id,
                "support_type": "exact_value",
                "locator": "Revenue note",
                "excerpt": f"Checked excerpt supporting {parameter_id}.",
                "excerpt_sha256": text_sha256(f"Checked excerpt supporting {parameter_id}."),
                "content_sha256": "a" * 64,
                "verification_status": "opened_and_checked",
                "verified_by": "test-research-agent",
                "verified_date": data["as_of_date"],
                "extracted_value": value,
                "unit": parameter["unit"],
                "period": parameter["period"],
                "capture_receipt_sha256": data["sources"][0]["capture"]["receipt_sha256"],
            }
        )
        parameter["claim_ids"] = [f"claim_parameter_{parameter_id}"]
    data["parameters"].append(parameter)
    return parameter_id


class PeriodFlowConstantTests(unittest.TestCase):
    def test_engine_and_schema_versions_are_registered(self) -> None:
        self.assertEqual(SKILL_VERSION, "4.2.0")
        self.assertEqual(PERIOD_EVIDENCE_SCHEMA_VERSION, "3.9")

    def test_fiscal_year_window_resolves_calendar_and_offset_year_ends(self) -> None:
        self.assertEqual(
            fiscal_year_window("12-31", 2025), (date(2025, 1, 1), date(2025, 12, 31))
        )
        self.assertEqual(
            fiscal_year_window("06-30", 2025), (date(2024, 7, 1), date(2025, 6, 30))
        )
        # Leap-day fiscal year end is a legal window boundary.
        self.assertEqual(
            fiscal_year_window("02-28", 2026), (date(2025, 3, 1), date(2026, 2, 28))
        )

    def test_period_flow_months_counts_3_6_12_including_cross_calendar(self) -> None:
        self.assertEqual(period_flow_months(date(2025, 1, 1), date(2025, 3, 31)), 3)
        self.assertEqual(period_flow_months(date(2025, 1, 1), date(2025, 6, 30)), 6)
        self.assertEqual(period_flow_months(date(2025, 1, 1), date(2025, 12, 31)), 12)
        # A six-month flow crossing calendar years (FYE 03-31 fiscal 2026 H1).
        self.assertEqual(period_flow_months(date(2025, 10, 1), date(2026, 3, 31)), 6)


class PeriodFlowContractUnitTests(unittest.TestCase):
    def test_legal_period_flow_validates_in_schema_3_9(self) -> None:
        data = schema_3_9_document()
        add_flow_parameter(data, "segment_a_h1_2026", 55.0, "2026-01-01", "2026-06-30", 2026)
        add_flow_parameter(
            data, "segment_a_q1_2026", 25.0, "2026-01-01", "2026-03-31", 2026
        )
        validated = validate_document(data)
        self.assertIn("segment_a_h1_2026", validated["parameter_index"])

    def test_old_schemas_reject_period_flow_time_basis(self) -> None:
        for version in ("3.7", OPT_IN_SCHEMA_VERSION):
            data = forecast_document()
            data["schema_version"] = version
            add_flow_parameter(data, "segment_a_h1_2026", 55.0, "2026-01-01", "2026-06-30", 2026)
            with self.assertRaisesRegex(ForecastInputError, "time_basis"):
                validate_document(data)

    def test_period_fields_on_non_flow_parameters_rejected_in_every_schema(self) -> None:
        for version in ("3.7", OPT_IN_SCHEMA_VERSION, PERIOD_EVIDENCE_SCHEMA_VERSION):
            data = forecast_document()
            data["schema_version"] = version
            add_flow_parameter(
                data,
                "misplaced_period_field",
                55.0,
                "2026-01-01",
                "2026-06-30",
                2026,
                time_basis="annual",
            )
            with self.assertRaisesRegex(ForecastInputError, "period_start"):
                validate_document(data)

    def test_invalid_or_reversed_dates_rejected(self) -> None:
        cases = [
            ("2026-1-1", "2026-06-30"),  # not strict ISO
            ("2026-01-01", None),  # missing end
            ("2026-06-30", "2026-01-01"),  # reversed period
            ("2026-01-01", "2026-01-01"),  # zero-length period
        ]
        for start, end in cases:
            data = schema_3_9_document()
            parameter = {
                "parameter_id": "bad_flow",
                "kind": "reported_fact",
                "value": 1.0,
                "unit": "USD million",
                "period": "FY2026",
                "definition": "bad flow",
                "time_basis": "period_flow",
                "source_ids": ["filing"],
            }
            parameter["period_start"] = start
            if end is not None:
                parameter["period_end"] = end
            apply_parameter_contract(data, parameter, "revenue")
            parameter["time_basis"] = "period_flow"
            data["parameters"].append(parameter)
            with self.assertRaises(ForecastInputError):
                validate_document(data)

    def test_flow_outside_declared_fiscal_year_window_rejected(self) -> None:
        data = schema_3_9_document()
        # FY2026 label with calendar-2025 dates violates the FYE 12-31 window.
        add_flow_parameter(data, "wrong_year", 55.0, "2025-01-01", "2025-06-30", 2026)
        with self.assertRaisesRegex(ForecastInputError, "fiscal"):
            validate_document(data)

    def test_cross_calendar_fiscal_year_flow_validates(self) -> None:
        data = schema_3_9_document()
        data["fiscal_year_end"] = "03-31"
        # FY2026 = 2025-04-01..2026-03-31; its first half crosses calendar years.
        add_flow_parameter(
            data, "offset_h1_fy2026", 55.0, "2025-04-01", "2025-09-30", 2026
        )
        validate_document(data)

    def test_unsupported_flow_lengths_rejected(self) -> None:
        for start, end in (("2026-01-01", "2026-01-31"), ("2026-01-01", "2026-05-31")):
            data = schema_3_9_document()
            add_flow_parameter(data, "odd_flow", 55.0, start, end, 2026)
            with self.assertRaisesRegex(ForecastInputError, "month"):
                validate_document(data)

    def test_pure_field_validator_contract(self) -> None:
        parameter = {
            "time_basis": "period_flow",
            "period": "FY2026",
            "period_start": "2026-01-01",
            "period_end": "2026-06-30",
        }
        normalized = validate_period_flow_fields("p1", parameter, "12-31")
        self.assertEqual(
            normalized, {"period_start": date(2026, 1, 1), "period_end": date(2026, 6, 30)}
        )
        bad = dict(parameter, period_start="2026-07-01", period_end="2026-12-31", period="FY2025")
        with self.assertRaisesRegex(ForecastInputError, "fiscal"):
            validate_period_flow_fields("p1", bad, "12-31")


class PeriodFlowIntegrationTests(unittest.TestCase):
    def test_h1_plus_h2_compose_annual_with_unchanged_units(self) -> None:
        data = schema_3_9_document()
        add_flow_parameter(data, "half_h1", 100.0, "2026-01-01", "2026-06-30", 2026)
        add_flow_parameter(data, "half_h2", 60.0, "2026-07-01", "2026-12-31", 2026)
        composed = {
            "parameter_id": "half_annual",
            "kind": "derived_fact",
            "value": 160.0,
            "unit": "USD million",
            "period": "FY2026",
            "definition": "annual flow composed from both halves",
            "time_basis": "period_flow",
            "period_start": "2026-01-01",
            "period_end": "2026-12-31",
            "source_ids": [],
            "formula": "x0+x1",
            "input_parameter_ids": ["half_h1", "half_h2"],
            "scenario": None,
        }
        apply_parameter_contract(data, composed, "revenue")
        composed["time_basis"] = "period_flow"
        data["parameters"].append(composed)
        validate_document(data)
        # A wrong composition still fails the derived tolerance gate.
        composed["value"] = 170.0
        with self.assertRaisesRegex(ForecastInputError, "derived_fact"):
            validate_document(data)

    def test_forecast_math_and_point_stocks_unchanged_between_3_7_and_3_9(self) -> None:
        legacy = forecast_document()
        modern = schema_3_9_document()
        # A point-in-time stock keeps its basis and carries no period fields.
        stock = {
            "parameter_id": "point_stock",
            "kind": "reported_fact",
            "value": 30.0,
            "unit": "USD million",
            "period": "FY2025",
            "definition": "point-in-time stock",
            "time_basis": "point_in_time",
            "source_ids": ["filing"],
            "scenario": None,
        }
        for data in (legacy, modern):
            apply_parameter_contract(data, stock, "monetary_balance")
            stock["time_basis"] = "point_in_time"  # apply forces annual; restore
            data["parameters"].append(dict(stock))
            data["evidence_claims"].append(
                {
                    "claim_id": "claim_parameter_point_stock",
                    "source_id": "filing",
                    "target_type": "parameter",
                    "target_id": "point_stock",
                    "support_type": "exact_value",
                    "locator": "Balance note",
                    "excerpt": "Checked excerpt supporting the point-in-time stock.",
                    "excerpt_sha256": text_sha256(
                        "Checked excerpt supporting the point-in-time stock."
                    ),
                    "content_sha256": "a" * 64,
                    "verification_status": "opened_and_checked",
                    "verified_by": "test-research-agent",
                    "verified_date": data["as_of_date"],
                    "extracted_value": 30.0,
                    "unit": stock["unit"],
                    "period": stock["period"],
                    "capture_receipt_sha256": data["sources"][0]["capture"][
                        "receipt_sha256"
                    ],
                }
            )
            data["parameters"][-1]["claim_ids"] = ["claim_parameter_point_stock"]
        legacy_result = run_forecast(legacy)
        modern_result = run_forecast(modern)
        self.assertEqual(
            legacy_result["consolidated_forecast"], modern_result["consolidated_forecast"]
        )
        self.assertEqual(modern_result["schema_version"], PERIOD_EVIDENCE_SCHEMA_VERSION)
        self.assertEqual(modern_result["engine_version"], "4.2.0")
        # The stock value passes through exactly — never doubled.
        self.assertEqual(
            modern_result["parameter_trace"][-1]["value"], 30.0
        )

    def test_different_flow_scopes_cannot_silently_mix(self) -> None:
        data = schema_3_9_document()
        shared = {
            "kind": "reported_fact",
            "unit": "USD million",
            "definition": "Segment A recognized flow",
            "scenario": None,
            "source_ids": ["filing"],
            "time_basis": "period_flow",
            "dimension": "revenue",
            "currency": data["currency"],
            "scale": data["unit"],
        }
        data["parameters"].append(
            {
                "parameter_id": "scope_q2",
                "value": 30.0,
                "period": "FY2026",
                "period_start": "2026-04-01",
                "period_end": "2026-06-30",
                **shared,
            }
        )
        data["parameters"].append(
            {
                "parameter_id": "scope_h1",
                "value": 55.0,
                "period": "FY2026",
                "period_start": "2026-01-01",
                "period_end": "2026-06-30",
                **shared,
            }
        )
        finalize_contract(data)
        data["schema_version"] = PERIOD_EVIDENCE_SCHEMA_VERSION
        with self.assertRaisesRegex(ForecastInputError, "conflict|resolution"):
            validate_document(data)

    def test_published_3_9_result_strong_validates_and_renders(self) -> None:
        data = schema_3_9_document()
        add_flow_parameter(data, "half_h1", 100.0, "2026-01-01", "2026-06-30", 2026)
        result = run_forecast(data)
        context = validate_published_forecast(result, data)
        self.assertIsNotNone(context)
        report = render_markdown(result)
        self.assertIn("Test Co", report)

    def test_real_half_year_flow_shapes_map_to_legal_windows(self) -> None:
        # Hermetic echo of the 18 real mislabeled flows (HK 10 H1 + 5 H2 from
        # native-reviewable-input-v2.json, CN h124/h125/h126 from
        # native-input-v6.json): all filers use a 12-31 fiscal year end, so
        # each H1/H2 label maps to explicit calendar windows.
        real_shapes = [
            (2025, "H1", 1, 6), (2026, "H1", 1, 6),  # HK games/social/... x5 segments
            (2025, "H2", 7, 12),                      # HK derived H2 x5 segments
            (2024, "H1", 1, 6), (2025, "H1", 1, 6), (2026, "H1", 1, 6),  # CN h124/125/126
        ]
        for year, _label, start_month, end_month in real_shapes:
            start = date(year, start_month, 1)
            end = date(year, end_month, 1)
            from calendar import monthrange

            end = end.replace(day=monthrange(end.year, end.month)[1])
            window_start, window_end = fiscal_year_window("12-31", year)
            self.assertGreaterEqual(start, window_start)
            self.assertLessEqual(end, window_end)
            self.assertEqual(period_flow_months(start, end), 6)
            normalized = validate_period_flow_fields(
                "real_flow",
                {
                    "time_basis": "period_flow",
                    "period": f"FY{year}",
                    "period_start": start.isoformat(),
                    "period_end": end.isoformat(),
                },
                "12-31",
            )
            self.assertEqual(normalized["period_start"], start)


if __name__ == "__main__":
    unittest.main()
