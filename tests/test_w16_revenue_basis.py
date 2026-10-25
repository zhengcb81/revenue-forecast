"""W16-RF-BASIS: historical revenue basis metadata (continuing/discontinued,
as-reported/restated, period kind, unit conversion, component bridge).

These tests freeze the B02-B05 contract before implementation (RED first).
The single shared owner is ``research/revenue_basis.py``; the contract,
report and linter layers call it instead of keeping a second copy of the
rules (B08).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import (  # noqa: E402
    ForecastInputError,
    canonical_sha256,
    run_forecast,
    validate_document,
)
from revenue_report import render_markdown  # noqa: E402
from research.input_quantities import convert_input_quantity  # noqa: E402
from research.revenue_basis import (  # noqa: E402
    ANNUAL_PERIOD_KIND,
    REVENUE_BASIS_SCHEMA_VERSION,
    basis_comparable,
    decimal_sum_matches,
    historical_basis_view,
    parse_revenue_basis,
    year_over_year,
)
from test_data_contract import _claim  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def _record_for_year(data: dict, year: int) -> dict:
    return next(item for item in data["historical_revenue"] if item["year"] == year)


def _add_component_claims(data: dict, year: int, parts: list[dict]) -> None:
    """Attach exact_value claims to component parts of one historical record."""
    source = data["sources"][0]
    for index, part in enumerate(parts):
        claim_id = f"claim_basis_component_{year}_{part['operations']}"
        claim = _claim(
            claim_id,
            source["source_id"],
            "historical_revenue",
            f"historical_revenue:{year}",
            "exact_value",
            f"Disclosed {part['operations']} operations revenue for FY{year}.",
            data["as_of_date"],
            extracted_value=part["value"],
            unit=f"{data['currency']} {data['unit']}",
            period=f"FY{year}",
        )
        claim["capture_receipt_sha256"] = source["capture"]["receipt_sha256"]
        data["evidence_claims"].append(claim)
        part["claim_ids"] = [claim_id]


def _basis(
    *,
    operations: str = "total",
    statement_status: str = "as_reported",
    period_kind: str | None = None,
    input_quantity: dict | None = None,
    components: list[dict] | None = None,
    source_ids: list[str] | None = None,
) -> dict:
    basis: dict = {
        "schema_version": REVENUE_BASIS_SCHEMA_VERSION,
        "operations": operations,
        "statement_status": statement_status,
    }
    if period_kind is not None:
        basis["period_kind"] = period_kind
    if input_quantity is not None:
        basis["input_quantity"] = input_quantity
    if components is not None:
        basis["components"] = components
    if source_ids is not None:
        basis["source_ids"] = source_ids
    return basis


class OwnerTests(unittest.TestCase):
    def test_schema_version_is_explicit(self) -> None:
        self.assertEqual(REVENUE_BASIS_SCHEMA_VERSION, "rf-revenue-basis/1")
        self.assertEqual(ANNUAL_PERIOD_KIND, "fiscal_year")

    def test_parse_returns_none_for_legacy_records(self) -> None:
        self.assertIsNone(parse_revenue_basis({"year": 2025, "value": 150.0}))

    def test_parse_rejects_unknown_operations_and_statement_status(self) -> None:
        with self.assertRaisesRegex(ForecastInputError, "operations"):
            parse_revenue_basis(
                {"revenue_basis": _basis(operations="continuing_ops")}
            )
        with self.assertRaisesRegex(ForecastInputError, "statement_status"):
            parse_revenue_basis(
                {"revenue_basis": _basis(statement_status="amended")}
            )

    def test_parse_rejects_unknown_keys(self) -> None:
        basis = _basis()
        basis["unexpected"] = True
        with self.assertRaisesRegex(ForecastInputError, "unexpected"):
            parse_revenue_basis({"revenue_basis": basis})

    def test_comparable_matrix(self) -> None:
        total = _basis()
        same = _basis()
        continuing = _basis(operations="continuing")
        restated = _basis(statement_status="restated")

        status, _ = basis_comparable(total, same)
        self.assertEqual(status, "comparable")

        status, reason = basis_comparable(total, continuing)
        self.assertEqual(status, "not_comparable")
        self.assertIn("operations", reason)

        status, reason = basis_comparable(total, restated)
        self.assertEqual(status, "not_comparable")
        self.assertIn("statement_status", reason)

        status, reason = basis_comparable(total, None)
        self.assertEqual(status, "not_declared")
        self.assertIn("not declared", reason)

    def test_year_over_year_guards_zero_base(self) -> None:
        growth, reason = year_over_year(150.0, 165.0)
        self.assertAlmostEqual(growth, 0.1)
        self.assertEqual(reason, "")
        growth, reason = year_over_year(0.0, 10.0)
        self.assertIsNone(growth)
        self.assertIn("zero", reason)

    def test_decimal_sum_matches_uses_tolerance(self) -> None:
        self.assertTrue(decimal_sum_matches(150.0, [100.0, 50.0], tolerance=1e-6))
        self.assertTrue(
            decimal_sum_matches(1_000_000.0, [600_000.0, 400_000.0000001], tolerance=1e-9)
        )
        self.assertFalse(decimal_sum_matches(150.0, [100.0, 40.0], tolerance=1e-6))


class ContractTests(unittest.TestCase):
    def test_legacy_history_is_unchanged(self) -> None:
        data = forecast_document()
        validated = validate_document(data)
        self.assertEqual(validated["years"], [2026, 2027])
        result = run_forecast(data, mode="draft")
        self.assertEqual(result["historical_revenue"], data["historical_revenue"])

    def test_declared_total_as_reported_basis_passes(self) -> None:
        data = forecast_document()
        for record in data["historical_revenue"]:
            record["revenue_basis"] = _basis()
        validate_document(data)
        result = run_forecast(data, mode="draft")
        self.assertEqual(
            result["historical_revenue"], data["historical_revenue"]
        )

    def test_base_year_continuing_operations_is_rejected(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            operations="continuing"
        )
        with self.assertRaisesRegex(
            ForecastInputError, r"continuing.*total|total.*continuing"
        ):
            validate_document(data)

    def test_sub_annual_period_kind_is_rejected(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2024)["revenue_basis"] = _basis(
            period_kind="quarter"
        )
        with self.assertRaisesRegex(ForecastInputError, "quarter"):
            validate_document(data)
        data = forecast_document()
        _record_for_year(data, 2024)["revenue_basis"] = _basis(
            period_kind="ytd"
        )
        with self.assertRaisesRegex(ForecastInputError, "ytd"):
            validate_document(data)

    def test_fiscal_year_period_kind_is_accepted(self) -> None:
        data = forecast_document()
        for record in data["historical_revenue"]:
            record["revenue_basis"] = _basis(period_kind="fiscal_year")
        validate_document(data)

    def test_input_quantity_conversion_passes_and_is_preserved(self) -> None:
        data = forecast_document()
        record = _record_for_year(data, 2025)
        record["revenue_basis"] = _basis(
            input_quantity={
                "schema_version": "rf-input-quantity/1",
                "value": 0.15,
                "input_unit": "USD billion",
                "engine_unit": "USD million",
                "engine_value": 150.0,
                "conversion": "0.15 usd_billion x 1000 = 150 usd_million",
            }
        )
        validate_document(data)
        result = run_forecast(data, mode="draft")
        self.assertEqual(
            result["historical_revenue"][1]["revenue_basis"]["input_quantity"][
                "engine_value"
            ],
            150.0,
        )

    def test_input_quantity_engine_value_mismatch_is_rejected(self) -> None:
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
        with self.assertRaisesRegex(ForecastInputError, "input_quantity"):
            validate_document(data)

    def test_input_quantity_cross_currency_is_rejected(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            input_quantity={
                "schema_version": "rf-input-quantity/1",
                "value": 150.0,
                "input_unit": "RMB million",
                "engine_unit": "USD million",
                "engine_value": 150.0,
                "conversion": "bogus",
            }
        )
        # DU5 owns cross-currency conversion: it rejects the record before the
        # W16 document checks run; either way no mixed-currency basis passes.
        with self.assertRaisesRegex(
            ForecastInputError, "currency|incompatible unit conversion"
        ):
            validate_document(data)

    def test_components_bridge_reconciles(self) -> None:
        data = forecast_document()
        parts = [
            {"operations": "continuing", "value": 100.0, "source_ids": ["filing"]},
            {"operations": "discontinued", "value": 50.0, "source_ids": ["filing"]},
        ]
        _add_component_claims(data, 2025, parts)
        _record_for_year(data, 2025)["revenue_basis"] = _basis(components=parts)
        validate_document(data)
        result = run_forecast(data, mode="draft")
        basis = result["historical_revenue"][1]["revenue_basis"]
        self.assertEqual(len(basis["components"]), 2)

    def test_components_sum_mismatch_is_rejected(self) -> None:
        data = forecast_document()
        parts = [
            {"operations": "continuing", "value": 100.0, "source_ids": ["filing"]},
            {"operations": "discontinued", "value": 40.0, "source_ids": ["filing"]},
        ]
        _add_component_claims(data, 2025, parts)
        _record_for_year(data, 2025)["revenue_basis"] = _basis(components=parts)
        with self.assertRaisesRegex(ForecastInputError, "components"):
            validate_document(data)

    def test_components_require_both_sides(self) -> None:
        data = forecast_document()
        parts = [
            {"operations": "continuing", "value": 150.0, "source_ids": ["filing"]},
        ]
        _add_component_claims(data, 2025, parts)
        _record_for_year(data, 2025)["revenue_basis"] = _basis(components=parts)
        with self.assertRaisesRegex(ForecastInputError, "continuing and discontinued"):
            validate_document(data)

    def test_component_claim_value_must_align(self) -> None:
        data = forecast_document()
        parts = [
            {"operations": "continuing", "value": 100.0, "source_ids": ["filing"]},
            {"operations": "discontinued", "value": 50.0, "source_ids": ["filing"]},
        ]
        _add_component_claims(data, 2025, parts)
        parts[0]["claim_ids"] = parts[1]["claim_ids"]  # claim says 50, part says 100
        _record_for_year(data, 2025)["revenue_basis"] = _basis(components=parts)
        with self.assertRaisesRegex(ForecastInputError, "claim value mismatch"):
            validate_document(data)

    def test_components_only_on_total_operations(self) -> None:
        data = forecast_document()
        parts = [
            {"operations": "continuing", "value": 150.0, "source_ids": ["filing"]},
        ]
        _add_component_claims(data, 2025, parts)
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            operations="continuing", components=parts
        )
        with self.assertRaisesRegex(ForecastInputError, "total"):
            validate_document(data)

    def test_negative_component_value_is_rejected(self) -> None:
        data = forecast_document()
        parts = [
            {"operations": "continuing", "value": 160.0, "source_ids": ["filing"]},
            {"operations": "discontinued", "value": -10.0, "source_ids": ["filing"]},
        ]
        _add_component_claims(data, 2025, parts)
        _record_for_year(data, 2025)["revenue_basis"] = _basis(components=parts)
        with self.assertRaisesRegex(ForecastInputError, "cannot be negative"):
            validate_document(data)

    def test_input_quantity_accepts_du5_alias_engine_unit(self) -> None:
        # S5 review: a DU5 alias spelling (usd_百万, not the canonical
        # usd_million) must resolve through the shared registry, not be
        # misrejected as "not a money unit". Same scale as the document unit.
        record = convert_input_quantity(
            150.0, input_unit="USD 百万", engine_unit="usd_百万"
        )
        data = forecast_document()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            input_quantity=record
        )
        validate_document(data)

    def test_input_quantity_scale_mismatch_is_rejected(self) -> None:
        # engine_value must be in the document unit; a different-scale
        # engine_unit whose value coincidentally equals the record value is
        # not a conversion into the document unit.
        quantity = convert_input_quantity(
            150.0, input_unit="usd_yi", engine_unit="usd_yi"
        )
        data = forecast_document()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            input_quantity=quantity
        )
        with self.assertRaisesRegex(ForecastInputError, "scale"):
            validate_document(data)

    def test_non_numeric_extracted_value_does_not_crash(self) -> None:
        data = forecast_document()
        claim = next(
            claim
            for claim in data["evidence_claims"]
            if claim["claim_id"] == "claim_history_2025"
        )
        claim["extracted_value"] = "not-a-number"
        with self.assertRaisesRegex(ForecastInputError, "claim value mismatch"):
            validate_document(data)

    def test_basis_source_ids_must_be_known(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            source_ids=["nonexistent"]
        )
        with self.assertRaisesRegex(ForecastInputError, "source"):
            validate_document(data)

    def test_mixed_statement_status_is_not_an_input_error(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2024)["revenue_basis"] = _basis()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            statement_status="restated"
        )
        result = run_forecast(data, mode="draft")
        self.assertEqual(len(result["historical_revenue"]), 2)


class OutputValidationTests(unittest.TestCase):
    def test_output_rejects_tampered_basis(self) -> None:
        data = forecast_document()
        for record in data["historical_revenue"]:
            record["revenue_basis"] = _basis()
        result = run_forecast(data)
        result["historical_revenue"][1]["revenue_basis"]["operations"] = "continuing"
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        with self.assertRaisesRegex(ForecastInputError, "historical"):
            render_markdown(result)


class ReportTests(unittest.TestCase):
    def _rendered(self, data: dict) -> str:
        result = run_forecast(data)
        return render_markdown(result)

    def test_legacy_render_marks_basis_undeclared(self) -> None:
        rendered = self._rendered(forecast_document())
        self.assertIn("历史营收", rendered)
        self.assertIn("未声明", rendered)
        self.assertNotIn("已核实可比", rendered)

    def test_render_includes_basis_columns_and_adoption(self) -> None:
        data = forecast_document()
        for record in data["historical_revenue"]:
            record["revenue_basis"] = _basis()
        rendered = self._rendered(data)
        self.assertIn("总额", rendered)
        self.assertIn("原表", rendered)
        self.assertIn("口径可比性", rendered)
        self.assertIn("基数采用", rendered)
        self.assertIn("可比", rendered)

    def test_render_flags_non_comparable_pair_with_reason(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2024)["revenue_basis"] = _basis()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            statement_status="restated"
        )
        rendered = self._rendered(data)
        self.assertIn("不可比", rendered)
        self.assertIn("statement_status", rendered)
        self.assertIn("重述", rendered)

    def test_render_shows_conversion_expression(self) -> None:
        data = forecast_document()
        _record_for_year(data, 2025)["revenue_basis"] = _basis(
            input_quantity={
                "schema_version": "rf-input-quantity/1",
                "value": 0.15,
                "input_unit": "USD billion",
                "engine_unit": "USD million",
                "engine_value": 150.0,
                "conversion": "0.15 usd_billion x 1000 = 150 usd_million",
            }
        )
        rendered = self._rendered(data)
        self.assertIn("usd_billion", rendered)

    def test_view_reports_base_adoption(self) -> None:
        data = forecast_document()
        for record in data["historical_revenue"]:
            record["revenue_basis"] = _basis()
        view = historical_basis_view(
            data["historical_revenue"],
            base_year=data["base_year"],
            reported_total_revenue_parameter_id=data[
                "reported_total_revenue_parameter_id"
            ],
            reported_total_value=150.0,
            reconciliation_tolerance=1e-6,
        )
        adoption = view["base_adoption"]
        self.assertEqual(adoption["year"], 2025)
        self.assertEqual(adoption["operations"], "total")
        self.assertEqual(adoption["statement_status"], "as_reported")
        self.assertTrue(adoption["matches_reported_total"])
        self.assertEqual(view["comparability"][0]["status"], "comparable")


if __name__ == "__main__":
    unittest.main()
