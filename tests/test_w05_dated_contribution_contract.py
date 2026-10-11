"""W05-RF-FLOW contract tests: arbitrary real dated windows (schema 3.10 opt-in).

Root cause (sealed PROCESS-006): an acquisition post-control contribution dated
2026-05-31..2026-06-30 (purchase date 2026-05-31, purchase-to-end revenue
1,291,902.08 CNY = 1.29190208 CNY million) had to be written as 2026-01-01..2026-06-30
because the 3.9 validator only allows 3/6/12 whole calendar months — a real
window that cannot pretend to be H1 or a full year. Schema 3.10 is additive:

* ``time_basis=period_flow`` accepts any real finite inclusive window
  (``period_start <= period_end``, same-day flows included) inside the
  fiscal-year window implied by ``fiscal_year_end`` and the ``FYyyyy`` label;
* amounts belong only to the written window — no implicit x2/x12/day
  annualization, no date-clipping of cross-FY amounts (they must be split);
* 3.9 keeps ``period_start < period_end`` and the 3/6/12 rule verbatim; 3.7/3.8
  keep failing closed on the dated fields.

Fixture amounts are synthetic except the sealed control-window fact above.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from contracts.evidence import ForecastInputError  # noqa: E402
from contracts.period_flow import (  # noqa: E402
    period_flow_months,
    validate_period_flow_fields,
)
from revenue_core import text_sha256, validate_document  # noqa: E402
from test_data_contract import apply_parameter_contract  # noqa: E402
from test_m3_period_flow_contract import add_flow_parameter  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

# Literal on purpose: the suite must exercise the schema by name, not by an
# implementation constant that could drift.
DATED_SCHEMA = "3.10"


def schema_3_10_document() -> dict:
    data = forecast_document()
    data["schema_version"] = DATED_SCHEMA
    return data


def add_window_parameter(
    data: dict,
    parameter_id: str,
    value: float,
    start: str | None,
    end: str | None,
    year: int,
    *,
    kind: str = "reported_fact",
    unit: str = "USD million",
    definition: str | None = None,
    rationale: str | None = None,
    formula: str | None = None,
    input_parameter_ids: list[str] | None = None,
    time_basis: str = "period_flow",
    claim: bool = True,
) -> str:
    """Append a dated parameter on the fixture document (synthetic amounts)."""
    parameter = {
        "parameter_id": parameter_id,
        "kind": kind,
        "value": value,
        "unit": unit,
        "period": f"FY{year}",
        "definition": definition or f"{parameter_id} recognized flow",
        "scenario": None,
        "source_ids": ["filing"] if claim and kind == "reported_fact" else [],
    }
    if kind in {"analyst_assumption", "scenario_stress"}:
        parameter["rationale"] = rationale or "synthetic dated fixture assumption"
    if kind == "derived_fact":
        parameter["formula"] = formula or "x0+x1"
        parameter["input_parameter_ids"] = input_parameter_ids or []
        if rationale is not None:
            parameter["rationale"] = rationale
    apply_parameter_contract(data, parameter, "revenue")
    parameter["time_basis"] = time_basis
    if start is not None:
        parameter["period_start"] = start
    if end is not None:
        parameter["period_end"] = end
    if claim and kind == "reported_fact":
        excerpt = f"Checked excerpt supporting {parameter_id}."
        data["evidence_claims"].append(
            {
                "claim_id": f"claim_parameter_{parameter_id}",
                "source_id": "filing",
                "target_type": "parameter",
                "target_id": parameter_id,
                "support_type": "exact_value",
                "locator": "Revenue note",
                "excerpt": excerpt,
                "excerpt_sha256": text_sha256(excerpt),
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


def parameter(data: dict, parameter_id: str) -> dict:
    return next(p for p in data["parameters"] if p["parameter_id"] == parameter_id)


class DatedWindowContractTests(unittest.TestCase):
    def test_real_control_window_validates_on_3_10(self) -> None:
        # Sealed counterexample: purchase date 2026-05-31, purchase-to-end
        # revenue 1,291,902.08 CNY (1.29190208 CNY million).
        data = schema_3_10_document()
        add_window_parameter(
            data,
            "cmp_post_2026",
            1.29190208,
            "2026-05-31",
            "2026-06-30",
            2026,
            definition="acquired entity revenue from control date 2026-05-31 to period end",
        )
        validated = validate_document(data)
        entry = validated["parameter_index"]["cmp_post_2026"]
        self.assertEqual(entry["period_start"], "2026-05-31")
        self.assertEqual(entry["period_end"], "2026-06-30")
        self.assertEqual(entry["value"], 1.29190208)

    def test_ten_day_and_same_day_windows_validate_on_3_10(self) -> None:
        for start, end in (
            ("2026-06-01", "2026-06-10"),
            ("2026-06-30", "2026-06-30"),
        ):
            with self.subTest(start=start, end=end):
                data = schema_3_10_document()
                add_window_parameter(data, "short_flow", 3.0, start, end, 2026)
                validated = validate_document(data)
                self.assertIn("short_flow", validated["parameter_index"])

    def test_leap_day_windows_validate_on_3_10(self) -> None:
        for start, end, year in (
            ("2024-02-29", "2024-02-29", 2024),
            ("2024-02-01", "2024-02-29", 2024),
            ("2024-01-01", "2024-03-31", 2024),
        ):
            with self.subTest(start=start, end=end):
                data = schema_3_10_document()
                add_window_parameter(data, "leap_flow", 2.0, start, end, year)
                validate_document(data)

    def test_non_calendar_fiscal_year_short_flow_validates_on_3_10(self) -> None:
        data = schema_3_10_document()
        data["fiscal_year_end"] = "06-30"
        # FY2026 = 2025-07-01..2026-06-30 for a 06-30 fiscal year end.
        add_window_parameter(data, "off_fy_short", 1.5, "2026-06-01", "2026-06-10", 2026)
        validate_document(data)

    def test_window_outside_labeled_fiscal_year_rejected_on_3_10(self) -> None:
        cases = (
            ("2026-05-31", "2026-06-30", 2025, "12-31"),
            ("2025-12-15", "2027-01-15", 2026, "12-31"),  # cross-FY amount unsplit
            ("2025-07-01", "2026-06-30", 2026, "12-31"),
        )
        for start, end, year, fiscal_year_end in cases:
            with self.subTest(start=start, end=end, year=year):
                data = schema_3_10_document()
                data["fiscal_year_end"] = fiscal_year_end
                add_window_parameter(data, "wrong_window", 5.0, start, end, year)
                with self.assertRaisesRegex(ForecastInputError, "fiscal"):
                    validate_document(data)

    def test_reversed_missing_or_invalid_dates_rejected_on_3_10(self) -> None:
        cases = (
            ("2026-06-30", "2026-05-31"),
            ("2026-06-30", None),
            (None, "2026-06-30"),
            ("2026-6-1", "2026-06-30"),
        )
        for start, end in cases:
            with self.subTest(start=start, end=end):
                data = schema_3_10_document()
                add_window_parameter(data, "bad_window", 5.0, start, end, 2026)
                with self.assertRaises(ForecastInputError):
                    validate_document(data)

    def test_period_fields_still_rejected_on_non_flow_parameters(self) -> None:
        for version in ("3.7", "3.8", "3.9", DATED_SCHEMA):
            with self.subTest(version=version):
                data = forecast_document()
                data["schema_version"] = version
                add_window_parameter(
                    data, "misdated", 5.0, "2026-01-01", "2026-06-30", 2026,
                    time_basis="annual",
                )
                with self.assertRaisesRegex(ForecastInputError, "period_start"):
                    validate_document(data)

    def test_old_schemas_still_reject_the_dated_basis(self) -> None:
        for version in ("3.7", "3.8"):
            with self.subTest(version=version):
                data = forecast_document()
                data["schema_version"] = version
                add_window_parameter(data, "dated", 5.0, "2026-05-31", "2026-06-30", 2026)
                with self.assertRaisesRegex(ForecastInputError, "time_basis"):
                    validate_document(data)

    def test_3_9_keeps_strict_order_and_3_6_12_month_rule(self) -> None:
        data = forecast_document()
        data["schema_version"] = "3.9"
        add_flow_parameter(data, "short_3_9", 5.0, "2026-05-31", "2026-06-30", 2026)
        with self.assertRaisesRegex(ForecastInputError, "month"):
            validate_document(data)
        data = forecast_document()
        data["schema_version"] = "3.9"
        add_flow_parameter(data, "same_day_3_9", 5.0, "2026-06-30", "2026-06-30", 2026)
        with self.assertRaisesRegex(ForecastInputError, "strictly"):
            validate_document(data)
        data = forecast_document()
        data["schema_version"] = "3.9"
        add_flow_parameter(data, "h1_3_9", 55.0, "2026-01-01", "2026-06-30", 2026)
        validate_document(data)
        # The pure month counter itself is unchanged (3.9 semantics).
        self.assertEqual(period_flow_months(date(2026, 1, 1), date(2026, 6, 30)), 6)
        with self.assertRaises(ForecastInputError):
            period_flow_months(date(2026, 5, 31), date(2026, 6, 30))

    def test_pure_field_validator_defaults_to_3_9_and_takes_schema_explicitly(self) -> None:
        short = {
            "time_basis": "period_flow",
            "period": "FY2026",
            "period_start": "2026-05-31",
            "period_end": "2026-06-30",
        }
        # Old pure-helper call shape keeps the 3.9 meaning (fail closed).
        with self.assertRaisesRegex(ForecastInputError, "month"):
            validate_period_flow_fields("p1", short, "12-31")
        normalized = validate_period_flow_fields(
            "p1", short, "12-31", schema_version=DATED_SCHEMA
        )
        self.assertEqual(
            normalized,
            {"period_start": date(2026, 5, 31), "period_end": date(2026, 6, 30)},
        )
        with self.assertRaises(ForecastInputError):
            validate_period_flow_fields("p1", short, "12-31", schema_version="2.0")

    def test_same_day_flow_passes_through_unscaled(self) -> None:
        data = schema_3_10_document()
        add_window_parameter(data, "one_day", 0.5, "2026-06-30", "2026-06-30", 2026)
        validated = validate_document(data)
        self.assertEqual(validated["parameter_index"]["one_day"]["value"], 0.5)


if __name__ == "__main__":
    unittest.main()
