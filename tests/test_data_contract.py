from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import ENGINE_VERSION, FORECAST_SCHEMA_VERSION, ForecastInputError, MONETARY_DIMENSIONS, SKILL_VERSION, text_sha256, validate_document  # noqa: E402


RESEARCH_DIMENSIONS = (
    "company_foundation",
    "growth_curve",
    "industry_market",
    "competition",
    "capacity",
    "technology",
    "policy",
    "customers",
    "demand",
)


def apply_parameter_contract(data: dict, parameter: dict, dimension: str | None = None) -> None:
    if dimension is None:
        dimension = "ratio" if "growth" in parameter["parameter_id"] else "revenue"
    parameter["dimension"] = dimension
    parameter["time_basis"] = "annual"
    if dimension in MONETARY_DIMENSIONS:
        parameter["currency"] = data["currency"]
        parameter["scale"] = data["unit"]
    else:
        parameter.pop("currency", None)
        parameter.pop("scale", None)


def _claim(claim_id: str, source_id: str, target_type: str, target_id: str, support_type: str, excerpt: str, verified_date: str, **extra: object) -> dict:
    return {
        "claim_id": claim_id,
        "source_id": source_id,
        "target_type": target_type,
        "target_id": target_id,
        "support_type": support_type,
        "locator": "Revenue note",
        "excerpt": excerpt,
        "excerpt_sha256": text_sha256(excerpt),
        "content_sha256": "a" * 64,
        "verification_status": "opened_and_checked",
        "verified_by": "test-research-agent",
        "verified_date": verified_date,
        **extra,
    }


def finalize_contract(data: dict) -> dict:
    data["schema_version"] = "3.0"
    claims: list[dict] = []
    for parameter in data["parameters"]:
        if "dimension" not in parameter:
            apply_parameter_contract(data, parameter)
        parameter_claims: list[str] = []
        if parameter.get("source_ids"):
            claim_id = f"claim_parameter_{parameter['parameter_id']}"
            support_type = "exact_value" if parameter["kind"] in {"reported_fact", "management_guidance"} else "rationale_support"
            extra = {}
            if support_type == "exact_value":
                extra = {"extracted_value": parameter["value"], "unit": parameter["unit"], "period": parameter["period"]}
            claims.append(_claim(claim_id, parameter["source_ids"][0], "parameter", parameter["parameter_id"], support_type, f"Evidence supporting parameter {parameter['parameter_id']} value and definition.", data["as_of_date"], **extra))
            parameter_claims.append(claim_id)
        parameter["claim_ids"] = parameter_claims
    for record in data["historical_revenue"]:
        claim_id = f"claim_history_{record['year']}"
        claims.append(_claim(claim_id, record["source_ids"][0], "historical_revenue", f"historical_revenue:{record['year']}", "exact_value", f"Reported company revenue for fiscal year {record['year']} is disclosed here.", data["as_of_date"], extracted_value=record["value"], unit=f"{data['currency']} {data['unit']}", period=f"FY{record['year']}"))
        record["claim_ids"] = [claim_id]
    for segment in data.get("segments", []):
        recognition = segment.get("recognition")
        if not isinstance(recognition, dict):
            continue
        recognition["modeled_presentation"] = recognition["presentation"]
        claim_id = f"claim_recognition_{segment['name'].replace(' ', '_')}"
        claims.append(_claim(claim_id, "filing", "recognition_policy", f"recognition:{segment['name']}", "policy_support", f"Revenue recognition policy for {segment['name']} is disclosed in the filing.", data["as_of_date"]))
        recognition["basis_claim_ids"] = [claim_id]
    probability_claim_id = "claim_scenario_probability"
    claims.append(_claim(probability_claim_id, "filing", "scenario_probability", "scenario_probability", "rationale_support", "Scenario probability calibration uses the disclosed operating evidence.", data["as_of_date"]))
    data["probability_claim_ids"] = [probability_claim_id]
    data["evidence_claims"] = claims
    return data


def update_parameter_value_and_claim(data: dict, parameter_id: str, value: float) -> None:
    parameter = next(item for item in data["parameters"] if item["parameter_id"] == parameter_id)
    parameter["value"] = value
    for claim_id in parameter.get("claim_ids", []):
        claim = next(item for item in data["evidence_claims"] if item["claim_id"] == claim_id)
        if claim["support_type"] == "exact_value":
            claim["extracted_value"] = value


def research_coverage(company_parameter_ids: list[str], growth_parameter_ids: list[str] | None = None) -> list[dict]:
    records: list[dict] = []
    for dimension in RESEARCH_DIMENSIONS:
        if dimension == "company_foundation":
            records.append({
                "dimension": dimension,
                "status": "modeled_driver",
                "conclusion": "Reported revenue perimeter and segment base are reconciled",
                "revenue_mechanism": "reported total equals segment external revenue plus adjustments",
                "parameter_ids": company_parameter_ids,
                "source_ids": ["filing"],
            })
        elif dimension == "growth_curve" and growth_parameter_ids:
            records.append({
                "dimension": dimension,
                "status": "modeled_driver",
                "conclusion": "Forecast growth is generated by registered operating drivers",
                "revenue_mechanism": "scenario drivers calculate annual recognized revenue",
                "parameter_ids": growth_parameter_ids,
                "source_ids": ["filing"],
            })
        elif dimension == "growth_curve":
            records.append({
                "dimension": dimension,
                "status": "data_gap",
                "conclusion": "Forecast driver mapping is not yet available",
                "revenue_mechanism": "missing operating drivers prevent a complete growth bridge",
                "parameter_ids": [],
                "source_ids": [],
                "rationale": "This base-contract fixture intentionally stops before scenario construction",
            })
        else:
            records.append({
                "dimension": dimension,
                "status": "immaterial",
                "conclusion": f"{dimension} is not material to this synthetic test horizon",
                "revenue_mechanism": "no incremental revenue effect is modeled in this fixture",
                "parameter_ids": [],
                "source_ids": [],
                "rationale": "Synthetic contract test isolates the base and forecast calculation path",
            })
    return records


def valid_document() -> dict:
    data = {
        "company_name": "Test Co",
        "as_of_date": "2026-07-12",
        "currency": "USD",
        "unit": "million",
        "fiscal_year_end": "12-31",
        "base_year": 2025,
        "forecast_years": [2026, 2027],
        "sources": [
            {
                "source_id": "filing",
                "source_type": "exchange_filing",
                "title": "FY2025 filing",
                "publisher": "Test Exchange",
                "url": "https://www.sec.gov/Archives/edgar/data/1/test.htm",
                "published_date": "2026-03-01",
                "accessed_date": "2026-07-01",
                "page_or_section": "Revenue note",
            }
        ],
        "parameters": [
            {
                "parameter_id": "reported_total",
                "kind": "reported_fact",
                "value": 150,
                "unit": "USD million",
                "period": "FY2025",
                "definition": "reported total revenue",
                "source_ids": ["filing"],
            },
            {
                "parameter_id": "segment_a_base",
                "kind": "reported_fact",
                "value": 100,
                "unit": "USD million",
                "period": "FY2025",
                "definition": "segment A external revenue",
                "source_ids": ["filing"],
            },
            {
                "parameter_id": "segment_b_base",
                "kind": "reported_fact",
                "value": 50,
                "unit": "USD million",
                "period": "FY2025",
                "definition": "segment B external revenue",
                "source_ids": ["filing"],
            },
            {
                "parameter_id": "a_growth_2026_base",
                "kind": "analyst_assumption",
                "value": 0.1,
                "unit": "ratio",
                "period": "FY2026",
                "definition": "segment A growth rate base",
                "scenario": "base",
                "rationale": "Driver-based test assumption",
                "source_ids": ["filing"],
            },
        ],
        "segments": [
            {"name": "Segment A", "base_revenue_parameter_id": "segment_a_base"},
            {"name": "Segment B", "base_revenue_parameter_id": "segment_b_base"},
        ],
        "reported_total_revenue_parameter_id": "reported_total",
        "base_adjustment_parameter_ids": [],
        "historical_revenue": [
            {"year": 2024, "value": 140, "source_ids": ["filing"]},
            {"year": 2025, "value": 150, "source_ids": ["filing"]},
        ],
        "research_coverage": research_coverage(["reported_total", "segment_a_base", "segment_b_base"]),
    }
    apply_parameter_contract(data, data["parameters"][0], "revenue")
    apply_parameter_contract(data, data["parameters"][1], "revenue")
    apply_parameter_contract(data, data["parameters"][2], "revenue")
    apply_parameter_contract(data, data["parameters"][3], "ratio")
    return finalize_contract(data)


class DataContractTests(unittest.TestCase):
    def test_release_and_schema_versions_are_explicit(self) -> None:
        self.assertEqual(SKILL_VERSION, "3.0.0")
        self.assertEqual(ENGINE_VERSION, SKILL_VERSION)
        self.assertEqual(FORECAST_SCHEMA_VERSION, "3.0")

    def test_valid_document(self) -> None:
        validated = validate_document(valid_document())
        self.assertEqual(validated["years"], [2026, 2027])
        self.assertEqual(validated["source_index"]["filing"]["source_rank"], 1)

    def test_rejects_placeholder_url(self) -> None:
        data = valid_document()
        data["sources"][0]["url"] = "https://example.com/fake"
        with self.assertRaisesRegex(ForecastInputError, "placeholder"):
            validate_document(data)

    def test_rejects_search_page(self) -> None:
        data = valid_document()
        data["sources"][0]["url"] = "https://www.google.com/search?q=revenue"
        with self.assertRaisesRegex(ForecastInputError, "search-page"):
            validate_document(data)

    def test_rejects_future_information(self) -> None:
        data = valid_document()
        data["sources"][0]["published_date"] = "2026-07-13"
        with self.assertRaisesRegex(ForecastInputError, "future information leak"):
            validate_document(data)

    def test_fact_requires_source(self) -> None:
        data = valid_document()
        data["parameters"][0]["source_ids"] = []
        with self.assertRaisesRegex(ForecastInputError, "requires at least one source"):
            validate_document(data)

    def test_assumption_requires_rationale(self) -> None:
        data = valid_document()
        del data["parameters"][3]["rationale"]
        with self.assertRaisesRegex(ForecastInputError, "requires rationale"):
            validate_document(data)

    def test_derived_fact_requires_formula_and_inputs(self) -> None:
        data = valid_document()
        data["parameters"].append(
            {
                "parameter_id": "derived",
                "kind": "derived_fact",
                "value": 1,
                "unit": "ratio",
                "period": "FY2025",
                "definition": "derived test",
                "source_ids": [],
                "claim_ids": [],
                "dimension": "ratio",
                "time_basis": "annual",
            }
        )
        with self.assertRaisesRegex(ForecastInputError, "requires formula"):
            validate_document(data)

    def test_unknown_source_reference(self) -> None:
        data = valid_document()
        data["parameters"][0]["source_ids"] = ["missing"]
        with self.assertRaisesRegex(ForecastInputError, "unknown source_id"):
            validate_document(data)

    def test_base_reconciliation_is_hard_gate(self) -> None:
        data = valid_document()
        update_parameter_value_and_claim(data, "segment_b_base", 49)
        with self.assertRaisesRegex(ForecastInputError, "does not reconcile"):
            validate_document(data)

    def test_conflicting_fact_parameters_are_rejected(self) -> None:
        data = valid_document()
        duplicate = copy.deepcopy(data["parameters"][1])
        duplicate["parameter_id"] = "segment_a_conflict"
        duplicate["value"] = 99
        data["parameters"].append(duplicate)
        with self.assertRaisesRegex(ForecastInputError, "unresolved conflicting"):
            validate_document(data)

    def test_requires_two_historical_observations(self) -> None:
        data = valid_document()
        data["historical_revenue"] = data["historical_revenue"][-1:]
        with self.assertRaisesRegex(ForecastInputError, "at least two"):
            validate_document(data)

    def test_historical_base_must_match_reported_total(self) -> None:
        data = valid_document()
        data["historical_revenue"][-1]["value"] = 149
        claim = next(item for item in data["evidence_claims"] if item["claim_id"] == "claim_history_2025")
        claim["extracted_value"] = 149
        with self.assertRaisesRegex(ForecastInputError, "does not match"):
            validate_document(data)

    def test_research_coverage_requires_all_nine_dimensions(self) -> None:
        data = valid_document()
        data["research_coverage"].pop()
        with self.assertRaisesRegex(ForecastInputError, "exactly nine"):
            validate_document(data)

    def test_research_modeled_driver_must_be_used(self) -> None:
        data = valid_document()
        record = next(item for item in data["research_coverage"] if item["dimension"] == "industry_market")
        record.update({
            "status": "modeled_driver",
            "parameter_ids": ["a_growth_2026_base"],
            "source_ids": ["filing"],
        })
        with self.assertRaisesRegex(ForecastInputError, "not used by the revenue model"):
            validate_document(data)

    def test_research_immaterial_dimension_cannot_map_parameters(self) -> None:
        data = valid_document()
        record = next(item for item in data["research_coverage"] if item["dimension"] == "capacity")
        record["parameter_ids"] = ["reported_total"]
        with self.assertRaisesRegex(ForecastInputError, "immaterial cannot map"):
            validate_document(data)

    def test_research_data_gap_requires_rationale(self) -> None:
        data = valid_document()
        record = next(item for item in data["research_coverage"] if item["dimension"] == "growth_curve")
        del record["rationale"]
        with self.assertRaisesRegex(ForecastInputError, "data_gap requires rationale"):
            validate_document(data)

    def test_research_mapping_rejects_unknown_parameter(self) -> None:
        data = valid_document()
        record = next(item for item in data["research_coverage"] if item["dimension"] == "company_foundation")
        record["parameter_ids"] = ["missing_parameter"]
        with self.assertRaisesRegex(ForecastInputError, "unknown research parameter_id"):
            validate_document(data)

    def test_derived_fact_value_is_recomputed(self) -> None:
        data = valid_document()
        data["parameters"].append({
            "parameter_id": "derived_bad", "kind": "derived_fact", "value": 999,
            "unit": "ratio", "period": "FY2025", "definition": "derived mismatch",
            "source_ids": [], "claim_ids": [], "dimension": "ratio", "time_basis": "annual",
            "formula": "x0 + 1", "input_parameter_ids": ["segment_a_base"],
        })
        with self.assertRaisesRegex(ForecastInputError, "derived_fact value mismatch"):
            validate_document(data)

    def test_parameter_period_is_strict(self) -> None:
        data = valid_document()
        data["parameters"][3]["period"] = "not-2026-a-period"
        with self.assertRaisesRegex(ForecastInputError, "strict FYyyyy"):
            validate_document(data)

    def test_reported_revenue_dimension_is_enforced(self) -> None:
        data = valid_document()
        data["parameters"][0]["dimension"] = "quantity"
        data["parameters"][0].pop("currency")
        data["parameters"][0].pop("scale")
        with self.assertRaisesRegex(ForecastInputError, "reported total revenue must use revenue dimension"):
            validate_document(data)

    def test_pre_revenue_company_can_have_no_history(self) -> None:
        data = valid_document()
        data["pre_revenue"] = True
        data["historical_revenue"] = []
        update_parameter_value_and_claim(data, "reported_total", 0)
        update_parameter_value_and_claim(data, "segment_a_base", 0)
        update_parameter_value_and_claim(data, "segment_b_base", 0)
        finalize_contract(data)
        validate_document(data)

    def test_claim_excerpt_hash_is_enforced(self) -> None:
        data = valid_document()
        data["evidence_claims"][0]["excerpt"] = "Tampered excerpt with a different meaning."
        with self.assertRaisesRegex(ForecastInputError, "excerpt hash mismatch"):
            validate_document(data)

    def test_claim_extracted_value_must_match_parameter(self) -> None:
        data = valid_document()
        claim = next(item for item in data["evidence_claims"] if item["target_id"] == "reported_total")
        claim["extracted_value"] = 999
        with self.assertRaisesRegex(ForecastInputError, "claim value mismatch"):
            validate_document(data)

    def test_future_year_cannot_be_labeled_historical(self) -> None:
        data = valid_document()
        data["historical_revenue"].append({"year": 2026, "value": 160, "source_ids": ["filing"], "claim_ids": ["claim_history_2025"]})
        with self.assertRaisesRegex(ForecastInputError, "cannot exceed base_year"):
            validate_document(data)


if __name__ == "__main__":
    unittest.main()
