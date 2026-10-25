"""ROOT acceptance: label equality is not comparable accounting history."""

import copy
import unittest
from test_w16_revenue_basis import _basis, _record_for_year, _add_component_claims
from test_recognition_bridge import forecast_document
from revenue_core import ForecastInputError, validate_document
from revenue_backtest import _benchmark_diagnostics
from research.revenue_basis import basis_comparable

from test_w16_revenue_basis import supported_basis


class RootBasisIntegrity(unittest.TestCase):
    def test_equal_restated_labels_do_not_prove_comparability(self):
        self.assertNotEqual(
            basis_comparable(
                _basis(statement_status="restated"), _basis(statement_status="restated")
            )[0],
            "comparable",
        )

    def test_equal_as_reported_labels_do_not_prove_business_boundary(self):
        self.assertNotEqual(basis_comparable(_basis(), _basis())[0], "comparable")

    def test_source_linked_comparison_group_and_boundary_allow_comparison(self):
        data = forecast_document()
        left, right = [supported_basis(data, row) for row in data["historical_revenue"]]
        validate_document(data)
        self.assertEqual(basis_comparable(left, right)[0], "comparable")

    def test_different_business_boundary_remains_incomparable(self):
        data = forecast_document()
        left, right = [supported_basis(data, row) for row in data["historical_revenue"]]
        right["business_boundary_id"] = "other-group"
        self.assertEqual(basis_comparable(left, right)[0], "not_comparable")

    def test_comparison_declaration_requires_real_policy_claim_not_numeric_claim(self):
        data = forecast_document()
        row = data["historical_revenue"][0]
        basis = supported_basis(data, row)
        basis["basis_claim_ids"] = row["claim_ids"]
        with self.assertRaisesRegex(ForecastInputError, "policy_support"):
            validate_document(data)

    def test_explicit_component_status_conflict_is_rejected(self):
        data = forecast_document()
        parts = [
            {
                "operations": "continuing",
                "value": 100,
                "source_ids": ["filing"],
                "statement_status": "restated",
            },
            {
                "operations": "discontinued",
                "value": 50,
                "source_ids": ["filing"],
                "statement_status": "as_reported",
            },
        ]
        _add_component_claims(data, 2025, parts)
        _record_for_year(data, 2025)["revenue_basis"] = _basis(components=parts)
        with self.assertRaisesRegex(ForecastInputError, "statement_status"):
            validate_document(data)

    def test_explicit_component_boundary_conflict_is_rejected(self):
        data = forecast_document()
        row = _record_for_year(data, 2025)
        basis = supported_basis(data, row, status="as_reported")
        parts = [
            {
                "operations": "continuing",
                "value": 100,
                "source_ids": ["filing"],
                "business_boundary_id": "other-group",
            },
            {"operations": "discontinued", "value": 50, "source_ids": ["filing"]},
        ]
        _add_component_claims(data, 2025, parts)
        basis["components"] = parts
        with self.assertRaisesRegex(ForecastInputError, "business_boundary_id"):
            validate_document(data)

    def test_continuing_base_can_match_reported_parameter_continuing_basis(self):
        data = forecast_document()
        row = _record_for_year(data, 2025)
        basis = supported_basis(data, row, operations="continuing")
        parameter = next(
            p
            for p in data["parameters"]
            if p["parameter_id"] == data["reported_total_revenue_parameter_id"]
        )
        parameter["revenue_basis"] = copy.deepcopy(basis)
        # Parameter basis policy must target this parameter, not a historical row.
        claim = copy.deepcopy(
            next(
                c
                for c in data["evidence_claims"]
                if c["claim_id"] == basis["basis_claim_ids"][0]
            )
        )
        claim.update(
            claim_id="parameter_basis",
            target_type="parameter",
            target_id=parameter["parameter_id"],
        )
        data["evidence_claims"].append(claim)
        parameter["revenue_basis"]["basis_claim_ids"] = [claim["claim_id"]]
        validate_document(data)

    def test_incomparable_history_cannot_feed_cagr_or_scaled_backtest(self):
        history = [
            {"year": 2024, "value": 140, "revenue_basis": _basis()},
            {
                "year": 2025,
                "value": 150,
                "revenue_basis": _basis(statement_status="restated"),
            },
        ]
        records = {
            "2026": {
                "absolute_error": 4,
                "squared_error": 16,
                "actual": 160,
                "horizon_years": 1,
            }
        }
        diagnostics = _benchmark_diagnostics(
            {"historical_revenue": history, "base_revenue": 150}, records
        )
        self.assertIsNone(diagnostics["mase"])
        self.assertIsNone(diagnostics["rmsse"])
        self.assertIsNone(diagnostics["historical_cagr_mae"])
        self.assertNotIn("historical_cagr_forecast", records["2026"])
        self.assertEqual(diagnostics["flat_base_mae"], 10)
        self.assertEqual(diagnostics["historical_basis_status"], "not_comparable")


if __name__ == "__main__":
    unittest.main()
