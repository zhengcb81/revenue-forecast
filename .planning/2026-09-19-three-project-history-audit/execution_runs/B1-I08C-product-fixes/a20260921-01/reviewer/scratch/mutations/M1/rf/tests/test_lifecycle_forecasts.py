"""Synthetic lifecycle cases through formal forecast and strong validation.

These fixtures exercise economic shapes, not real companies or source accuracy.
The session fixture in conftest.py isolates the publication registry; no large
JSON artifacts or additional registry are written by these tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from model_extensions import EXTENSION_OPENING_BALANCES  # noqa: E402
from revenue_core import MODEL_DRIVER_DIMENSIONS, ForecastInputError, run_forecast  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_data_contract import apply_parameter_contract, finalize_contract, research_coverage  # noqa: E402
from test_industry_end_to_end import model_document  # noqa: E402


def _add_parameter(data, parameter_id, value, dimension, year, scenario, kind="analyst_assumption"):
    parameter = {
        "parameter_id": parameter_id, "value": value, "kind": kind,
        "period": f"FY{year}", "scenario": scenario,
        "unit": "synthetic compatible model units", "definition": f"SYNTHETIC {parameter_id}",
        "rationale": "Synthetic lifecycle test only; not a real investment assumption.",
        "source_ids": ["filing"],
    }
    apply_parameter_contract(data, parameter, dimension)
    data["parameters"].append(parameter)


def _document(name, model, base_revenue, definitions):
    data = model_document(model)
    data.update(company_name=f"SYNTHETIC lifecycle - {name}", forecast_version="synthetic-lifecycle-v1")
    data["sources"][0].update(title="SYNTHETIC lifecycle fixture; no real company filing",
                               publisher="Synthetic test fixture")
    data["parameters"] = []
    data["segments"] = []
    data["historical_revenue"] = (
        [{"year": 2024, "value": base_revenue * 0.8, "source_ids": ["filing"]},
         {"year": 2025, "value": base_revenue, "source_ids": ["filing"]}]
        if base_revenue else []
    )
    data["pre_revenue"] = base_revenue == 0
    _add_parameter(data, "reported_total", base_revenue, "revenue", 2025, "all", "reported_fact")
    for index, (name, model, segment_base, scenarios) in enumerate(definitions):
        prefix = f"s{index}"
        base_id = f"{prefix}_base"
        _add_parameter(data, base_id, segment_base, "revenue", 2025, "all", "reported_fact")
        segment = {
            "name": name, "base_revenue_parameter_id": base_id,
            "recognition": {"mode": "modeled_as_recognized", "timing": "point_in_time",
                            "trigger": "Synthetic delivery with customer acceptance", "presentation": "gross"},
            "scenarios": {},
        }
        for scenario, drivers in scenarios.items():
            ids = {}
            for driver, values in drivers.items():
                ids[driver] = []
                for year, value in zip(data["forecast_years"], values):
                    parameter_id = f"{prefix}_{driver}_{year}_{scenario}"
                    _add_parameter(data, parameter_id, value, MODEL_DRIVER_DIMENSIONS[model][driver], year, scenario)
                    ids[driver].append(parameter_id)
            segment["scenarios"][scenario] = {
                "model": model, "driver_parameter_ids": ids,
                "rationale": f"Synthetic {scenario} economic conditions; no real-world forecast asserted.",
            }
        if model in EXTENSION_OPENING_BALANCES:
            field, opening_driver, dimension = EXTENSION_OPENING_BALANCES[model]
            anchor_id = f"{prefix}_opening_anchor"
            _add_parameter(data, anchor_id, scenarios["base"][opening_driver][0], dimension, 2025, "all", "reported_fact")
            segment[field] = anchor_id
        data["segments"].append(segment)
    base_driver_ids = [parameter_id for segment in data["segments"]
                       for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values()
                       for parameter_id in ids]
    data["research_coverage"] = research_coverage(
        ["reported_total"] + [s["base_revenue_parameter_id"] for s in data["segments"]], base_driver_ids
    )
    return data


def _saas_document():
    scenarios = {}
    for scenario, loss_timing in (("low", [1, 1]), ("base", [0.5, 0.9]), ("high", [0, 0.8])):
        scenarios[scenario] = {
            "opening_arr": [120, 200], "gross_retention_rate": [110 / 120, 0.5],
            "expansion_arr": [20, 0], "new_arr": [70, 20], "closing_arr": [200, 120],
            "lost_arr_revenue_fraction": loss_timing, "expansion_revenue_fraction": [0.5, 0],
            "new_arr_revenue_fraction": [0, 0],
        }
    data = _document("SaaS expansion then contraction", "subscription_arr_bridge", 100,
                     [("Subscription", "subscription_arr_bridge", 100, scenarios)])
    recognition = data["segments"][0]["recognition"]
    recognition.update(timing="over_time", trigger="Synthetic annual service delivered",
                       progress_measure="ARR cohort exposure already measures annual earned revenue; no second time discount",
                       progress_parameter_ids={})
    for scenario in scenarios:
        ids = []
        for year in data["forecast_years"]:
            parameter_id = f"saas_progress_{year}_{scenario}"
            _add_parameter(data, parameter_id, 1, "ratio", year, scenario)
            ids.append(parameter_id)
        recognition["progress_parameter_ids"][scenario] = ids
    return finalize_contract(data)


def _drug_document():
    scenarios = {}
    for scenario, fractions in (("low", [0, 0]), ("base", [0, 0.25]), ("high", [0.5, 1])):
        scenarios[scenario] = {
            "eligible_units": [1000, 2000], "adoption_rate": [0.4, 0.5],
            "annual_supply_capacity": [100, 300], "commercial_year_fraction": fractions,
            "net_revenue_per_unit": [0.02, 0.02],
        }
    return finalize_contract(_document("Drug failure delay and supply bottleneck", "commercial_launch", 0,
                              [("Commercial product", "commercial_launch", 0, scenarios)]))


def _stores_document():
    legacy, new_format = {}, {}
    for scenario, loss_timing, opening_timing in (
        ("low", [0.75, 0.75], [0, 0.25]),
        ("base", [0.5, 0.5], [0.25, 0.75]),
        ("high", [0.25, 0.25], [0.75, 1]),
    ):
        legacy[scenario] = {
            "opening_stores": [20, 12], "new_stores": [0, 0], "closed_stores": [8, 4],
            "closing_stores": [12, 8], "new_store_revenue_fraction": [0, 0],
            "closure_lost_fraction": loss_timing, "new_store_productivity": [1, 1],
            "annual_revenue_per_mature_store": [5, 5],
        }
        new_format[scenario] = {
            "opening_stores": [0, 5], "new_stores": [5, 5], "closed_stores": [0, 0],
            "closing_stores": [5, 10], "new_store_revenue_fraction": opening_timing,
            "closure_lost_fraction": [0, 0], "new_store_productivity": [0.6, 0.8],
            "annual_revenue_per_mature_store": [8, 8],
        }
    return finalize_contract(_document("Legacy closures and new store format", "store_cohorts", 100, [
        ("Legacy format", "store_cohorts", 100, legacy), ("New format", "store_cohorts", 0, new_format),
    ]))


def _formal_result(data):
    result = run_forecast(data, mode="formal")
    validate_published_forecast(result, data)
    return result


def _parameter(data, parameter_id):
    return next(p for p in data["parameters"] if p["parameter_id"] == parameter_id)


def test_synthetic_saas_year_end_arr_additions_do_not_prevent_revenue_contraction():
    result = _formal_result(_saas_document())
    company = result["consolidated_forecast"]["base"]
    subscription = result["segments"][0]["scenarios"]["base"]
    assert company["annual_revenue"] == {"2026": 125.0, "2027": 110.0}
    assert company["annual_growth"]["2027"] == pytest.approx(-0.12)
    assert subscription["driver_values"]["closing_arr"] == {"2026": 200.0, "2027": 120.0}
    assert subscription["driver_values"]["new_arr_revenue_fraction"] == {"2026": 0.0, "2027": 0.0}
    assert subscription["modeled_activity"] == subscription["recognized_revenue"]


def test_synthetic_pre_revenue_drug_failure_delay_and_supply_cap():
    result = _formal_result(_drug_document())
    company = result["consolidated_forecast"]
    assert company["low"]["annual_revenue"] == {"2026": 0.0, "2027": 0.0}
    assert company["base"]["annual_revenue"] == {"2026": 0.0, "2027": 1.5}
    assert company["high"]["annual_revenue"] == {"2026": 1.0, "2027": 6.0}
    assert all(company[scenario]["cagr"] is None for scenario in ("low", "base", "high"))
    assert result["scenario_probabilities"] is None
    assert result["probability_weighted_forecast"] is None


def test_synthetic_store_transition_keeps_decline_and_opening_timing_separate():
    result = _formal_result(_stores_document())
    company = result["consolidated_forecast"]
    assert company["low"]["annual_revenue"] == {"2026": 70.0, "2027": 93.0}
    assert company["base"]["annual_revenue"] == {"2026": 86.0, "2027": 114.0}
    assert company["high"]["annual_revenue"] == {"2026": 108.0, "2027": 127.0}
    assert company["base"]["incremental_contribution"]["segments"] == [
        {"name": "Legacy format", "terminal_incremental_revenue": -50.0},
        {"name": "New format", "terminal_incremental_revenue": 64.0},
    ]
    new_format = next(s for s in result["segments"] if s["name"] == "New format")
    assert new_format["scenarios"]["low"]["recognized_revenue"]["2026"] == 0.0


def test_synthetic_saas_rejects_inconsistent_arr_bridge():
    data = _saas_document()
    _parameter(data, "s0_closing_arr_2027_base")["value"] = 121
    with pytest.raises(ForecastInputError, match="stock-flow balance"):
        run_forecast(finalize_contract(data), mode="formal")


def test_synthetic_launch_rejects_additional_success_probability_driver():
    data = _drug_document()
    for scenario in ("low", "base", "high"):
        drivers = data["segments"][0]["scenarios"][scenario]["driver_parameter_ids"]
        drivers["success_probability"] = drivers["adoption_rate"].copy()
    with pytest.raises(ForecastInputError, match="unsupported drivers.*success_probability"):
        run_forecast(finalize_contract(data), mode="formal")


def test_synthetic_store_transition_rejects_unanchored_opening_balance():
    data = _stores_document()
    _parameter(data, "s0_opening_stores_2026_base")["value"] = 21
    with pytest.raises(ForecastInputError, match="first opening does not reconcile"):
        run_forecast(finalize_contract(data), mode="formal")
