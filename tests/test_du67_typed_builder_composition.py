"""ROOT: builders and native typed validation must consume one contract."""

from copy import deepcopy
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests")]
from research.input_targets import build_management_target  # noqa: E402
from research.target_measurement import meets_target, normalize_target_bounds  # noqa: E402
from revenue_core import run_forecast  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_target_measurement_comparison import quarter_document  # noqa: E402
from test_du6_target_measurement_boundaries import (  # noqa: E402
    growth_document,
    money_target_document,
)
from test_recognition_bridge import add_parameter  # noqa: E402
from test_data_contract import finalize_contract  # noqa: E402


def rebuild_target(data, *, treatment=None):
    old = data["management_targets"][0]
    claim = next(
        c for c in data["evidence_claims"] if c["claim_id"] in old["claim_ids"]
    )
    capture = next(
        s["capture"] for s in data["sources"] if s["source_id"] == claim["source_id"]
    )
    keys = [
        "target_id",
        "metric_name",
        "metric_definition",
        "raw_unit",
        "raw_currency",
        "raw_scale",
        "measurement_basis",
        "measurement_periods",
        "target_period",
        "target_quarter",
        "commitment_strength",
        "materiality",
        "perimeter_status",
        "comparison",
        "rationale",
        "measurement_rationale",
        "perimeter_notes",
        "mapped_parameter_ids",
        "mapped_scenarios",
        "presentation_basis",
        "currency_basis",
        "comparison_tolerance",
        "normalization_rationale",
    ]
    kwargs = {k: deepcopy(old[k]) for k in keys if k in old}
    kwargs.update(
        source_id=claim["source_id"],
        locator=claim["locator"],
        excerpt=claim["excerpt"],
        verified_by="root-independent-review",
        verified_date=data["as_of_date"],
        period_label=old.get("period_label", old["target_period"]),
        comparison_spec=deepcopy(old["comparison_basis"]),
        source_capture=capture,
        raw_value=old.get("raw_target_value"),
        raw_value_low=old.get("raw_target_value_low"),
        raw_value_high=old.get("raw_target_value_high"),
    )
    if treatment is not None:
        kwargs["treatment"] = treatment
    if old["comparison_basis"]["metric_kind"] != "year_over_year_growth":
        kwargs.update(
            comparison_currency=data["currency"], comparison_scale=data["unit"]
        )
    built = build_management_target(old["statement"], **kwargs)
    data["evidence_claims"] = [
        c for c in data["evidence_claims"] if c["claim_id"] not in old["claim_ids"]
    ]
    data["evidence_claims"].extend(built["claims"])
    data["management_targets"] = [built["target"]]
    return built


def company_quarter_document():
    data = quarter_document()
    old_claims = deepcopy(data["evidence_claims"])
    target = data["management_targets"][0]
    target.update(
        scope={"type": "company", "name": "company"},
        raw_unit="USD million",
        raw_scale="million",
        raw_target_value_low=107240,
        raw_target_value_high=111960,
    )
    segment = data["segments"][1]
    for scenario, value in [("low", 1400), ("base", 1600), ("high", 1800)]:
        pid = add_parameter(
            data, "company_second_quarter_" + scenario, value, 2026, scenario
        )
        next(p for p in data["parameters"] if p["parameter_id"] == pid)[
            "measurement_period"
        ] = "FY2026Q3"
        annual_id = segment["scenarios"][scenario]["driver_parameter_ids"]["revenue"][0]
        annual = next(p for p in data["parameters"] if p["parameter_id"] == annual_id)
        annual.update(
            kind="derived_fact",
            value=value + 300000,
            formula="x0 + 300000",
            input_parameter_ids=[pid],
        )
        target["comparison_basis"]["scenario_parameter_ids"][scenario].append(pid)
    target["mapped_parameter_ids"] = list(
        target["comparison_basis"]["scenario_parameter_ids"]["base"]
    )
    finalize_contract(data)
    generated_ids = {c["claim_id"] for c in data["evidence_claims"]}
    data["evidence_claims"].extend(
        c for c in old_claims if c["claim_id"] not in generated_ids
    )
    return data


def test_native_quarter_builder_uses_real_quarter_bridge_without_annual_conversion():
    data = company_quarter_document()
    built = rebuild_target(data, treatment="modeled_scenario")
    assert "normalization_formula" not in built["target"]
    assert built["notes"]["comparable"] is True
    result = run_forecast(data)
    validate_published_forecast(result, data)
    for scenario, amount in [("low", 107240), ("base", 109600), ("high", 111960)]:
        row = result["management_target_coverage"]["targets"][0]["scenario_comparison"][
            scenario
        ]
        assert row["modeled_value"] == amount
        assert row["period"] == "FY2026Q3"
        assert row["meets_target"] is True


@pytest.mark.parametrize("treatment", [None, "unmodeled_data_gap", "out_of_horizon"])
def test_unmodeled_typed_growth_builder_roundtrips_without_fabricated_comparison(
    treatment,
):
    actual = treatment or "unmodeled_data_gap"
    data = growth_document(
        raw_value=-12.5,
        comparison_value=None,
        treatment=actual,
        comparison="approximately",
        growth_by_scenario={"low": -0.25, "base": -0.125, "high": 0.125},
    )
    built = rebuild_target(data, treatment=treatment)
    assert built["target"]["comparison_value"] is None
    assert built["notes"]["comparable"] is False
    result = run_forecast(data)
    validate_published_forecast(result, data)
    target = result["management_target_coverage"]["targets"][0]
    assert target["raw_target_value"] == -12.5
    assert target["scenario_comparison"] == {}
    assert any(actual in gap for gap in result["data_gaps"])


def test_positive_money_normalization_preserves_historical_factor_expression():
    target = {
        "comparison_basis": {
            "schema_version": "management-target-comparison/1",
            "metric_kind": "annual_revenue_level",
            "period": "FY2027",
        },
        "raw_target_value": 1.1,
        "raw_unit": "USD million",
        "raw_currency": "USD",
        "raw_scale": "million",
    }
    old = 1.1 * (1e6 / 1e8)
    normalized = normalize_target_bounds(target, {"currency": "USD", "unit": "亿元"})[0]
    assert normalized == old
    assert meets_target(old, normalized, normalized, "greater_than", 0.0) is False


def test_unmodeled_foreign_amount_is_preserved_without_inventing_fx():
    data = money_target_document(
        raw_value=125,
        comparison_value=None,
        raw_currency="HKD",
        raw_scale="million",
        model_currency="USD",
        model_unit="million",
        treatment="unmodeled_data_gap",
    )
    # The unsupported currency basis is retained as an explicit gap. The typed
    # validator already leaves such a target unnormalized; the builder must too.
    data["management_targets"][0]["mapped_parameter_ids"] = []
    data["management_targets"][0]["mapped_scenarios"] = []
    built = rebuild_target(data, treatment="unmodeled_data_gap")
    assert built["target"]["comparison_value"] is None
    assert built["notes"]["comparable"] is False
    result = run_forecast(data)
    validate_published_forecast(result, data)
    target = result["management_target_coverage"]["targets"][0]
    assert target["raw_target_value"] == 125
    assert target["raw_currency"] == "HKD"
    assert target["scenario_comparison"] == {}
