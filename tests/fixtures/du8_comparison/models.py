"""Synthetic complete models for the DU8 comparison round trip.

Every model here is built from the repository's own synthetic test documents
(``test_recognition_bridge.forecast_document`` and
``test_management_targets.add_target``). Nothing in this module is evidence
about a real company, and none of these inputs were produced by a supplier or
a network call.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

_SKILL_ROOT = Path(__file__).resolve().parents[3]
_TEST_ROOT = _SKILL_ROOT / "tests"
for _path in (str(_TEST_ROOT), str(_SKILL_ROOT / "scripts")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from test_management_targets import add_target  # noqa: E402
from test_recognition_bridge import add_parameter, forecast_document  # noqa: E402
from test_data_contract import finalize_contract  # noqa: E402

TYPED_SCHEMA = "management-target-comparison/1"


def _scale_high_scenario(data: dict, factor: float) -> None:
    """Scale every year of segment A's high scenario by ``factor``."""
    index = {p["parameter_id"]: p for p in data["parameters"]}
    ids = data["segments"][0]["scenarios"]["high"]["driver_parameter_ids"]["revenue"]
    for pid in ids:
        index[pid]["value"] = index[pid]["value"] * factor


def legacy_annual_model() -> dict:
    """A legacy (non-typed) annual ``at_least`` revenue-level target."""
    data = add_target(forecast_document(), target_value=144.0)
    target = data["management_targets"][0]
    target.update(
        comparison="at_least",
        comparison_tolerance=0.01,
        mapped_scenarios=["high"],
        statement="Reach at least USD 144 million of annual segment revenue.",
    )
    return data


def legacy_approximately_model() -> dict:
    """A legacy ``approximately`` target reached through the public entry."""
    data = add_target(forecast_document(), target_value=0.5)
    target = data["management_targets"][0]
    target.update(
        comparison="approximately",
        comparison_tolerance=0.01,
        comparison_value=0.5,
        mapped_scenarios=["high"],
        statement="Segment revenue of approximately USD 0.5 million.",
    )
    claim = next(
        c for c in data["evidence_claims"] if c["claim_id"] in target["claim_ids"]
    )
    claim["extracted_value"] = 0.5
    index = {p["parameter_id"]: p for p in data["parameters"]}
    for scenario, offset in (("low", 0.94), ("base", 0.97), ("high", 1.0)):
        ids = data["segments"][0]["scenarios"][scenario]["driver_parameter_ids"]["revenue"]
        seed = 0.5 * 0.981 * offset
        index[ids[0]]["value"] = seed
        index[ids[1]]["value"] = seed
    return data


def legacy_cumulative_model() -> dict:
    """A legacy cumulative-periods target over two fiscal years."""
    data = add_target(
        forecast_document(),
        target_value=260.0,
        period="FY2026-FY2027",
        measurement_basis="cumulative_periods",
        measurement_periods=["FY2026", "FY2027"],
    )
    target = data["management_targets"][0]
    target.update(comparison="at_least", comparison_tolerance=0.01,
                  mapped_scenarios=["high"])
    return data


def typed_level_model() -> dict:
    """A typed annual revenue-level independent benchmark."""
    data = add_target(forecast_document(), target_value=1000.0,
                      treatment="independent_benchmark")
    target = data["management_targets"][0]
    target.update(
        mapped_scenarios=["low", "base", "high"],
        mapped_parameter_ids=[
            data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
        ],
        benchmark_rationale="A level benchmark kept independent of the scenario paths.",
        benchmark_claim_ids=["benchmark_evidence"],
        comparison="at_least",
        comparison_tolerance=0.01,
        comparison_value=1000.0,
        normalization_rationale="Source and model use the same currency, unit and revenue definition.",
        statement="Reach at least USD 1000 million of annual segment revenue.",
        comparison_basis={
            "schema_version": TYPED_SCHEMA,
            "metric_kind": "annual_revenue_level",
            "period": "FY2027",
        },
    )
    claim = copy.deepcopy(data["evidence_claims"][-1])
    claim.update({"claim_id": "benchmark_evidence", "support_type": "rationale_support"})
    data["evidence_claims"].append(claim)
    return data


def growth_model() -> dict:
    """A typed year-over-year growth target (signed ratio)."""
    data = add_target(forecast_document(), target_value=1000.0,
                      treatment="independent_benchmark")
    target = data["management_targets"][0]
    target.update(
        statement="Management guides FY2027 year over year revenue growth of 10 percent.",
        metric_name="revenue growth",
        metric_definition="year over year growth of recognized segment revenue",
        raw_unit="percent",
        raw_currency="dimensionless",
        raw_scale="percent",
        raw_value_kind="numeric",
        raw_target_value=10.0,
        comparison="approximately",
        comparison_tolerance=0.01,
        comparison_value=0.10,
        mapped_scenarios=["low", "base", "high"],
        mapped_parameter_ids=[
            data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
        ],
        comparison_basis={
            "schema_version": TYPED_SCHEMA,
            "metric_kind": "year_over_year_growth",
            "period": "FY2027",
            "base_period": "FY2026",
            "raw_ratio_basis": "percent",
        },
        benchmark_rationale="The stated growth rate is a benchmark, not an attained path.",
        benchmark_claim_ids=["benchmark_evidence"],
    )
    claim = next(c for c in data["evidence_claims"] if c["claim_id"] in target["claim_ids"])
    claim.update(unit="percent", period="FY2027", extracted_value=10.0)
    other = copy.deepcopy(claim)
    other.update(claim_id="benchmark_evidence", support_type="rationale_support")
    data["evidence_claims"].append(other)
    return data


def lagged_recognition_model() -> dict:
    """A segment whose recognized path differs from its adjusted path.

    ``lagged_activity`` recognition defers revenue by one year, so
    ``recognized_revenue`` and ``effective_revenue`` are genuinely different
    series. This is the fixture that makes the owner's choice between the two
    paths observable instead of coincidental (they coincide only when every
    period recognizes 100 percent).
    """
    data = forecast_document()
    segment = data["segments"][0]
    carry = {}
    for scenario, value in (("low", 90), ("base", 95), ("high", 100)):
        carry[scenario] = [
            add_parameter(data, f"carry_{scenario}", value, 2026, scenario)
        ]
    segment["recognition"] = {
        "mode": "lagged_activity",
        "timing": "point_in_time",
        "trigger": "customer acceptance after installation",
        "presentation": "gross",
        "lag_years": 1,
        "carry_in_parameter_ids": carry,
    }
    finalize_contract(data)
    data = add_target(data, target_value=144.0)
    target = data["management_targets"][0]
    target.update(
        comparison="approximately",
        comparison_tolerance=0.25,
        mapped_scenarios=["high"],
        statement="Reach approximately USD 144 million of annual segment revenue.",
    )
    return data


def constrained_model() -> dict:
    """A model whose revenue constraint makes effective differ from recognized.

    ``sum_cap`` re-allocates segment revenue, so ``effective_revenue`` is no
    longer equal to ``recognized_revenue``. This makes the owner's choice
    between the two paths observable rather than coincidental.
    """
    data = forecast_document()
    constraints = {"low": [140, 145], "base": [150, 170], "high": [160, 190]}
    cap_ids = {}
    for scenario, values in constraints.items():
        cap_ids[scenario] = [
            add_parameter(data, f"shared_cap_{scenario}_{year}", value, year, scenario)
            for year, value in zip(data["forecast_years"], values)
        ]
    data["revenue_constraints"] = [
        {
            "constraint_id": "shared_capacity_cap",
            "type": "sum_cap",
            "segments": ["Segment A", "Segment B"],
            "allocation": "proportional",
            "scenario_parameter_ids": cap_ids,
            "rationale": "Both segments consume the same constrained external capacity.",
        }
    ]
    finalize_contract(data)
    data = add_target(data, target_value=144.0)
    target = data["management_targets"][0]
    target.update(
        comparison="approximately",
        comparison_tolerance=0.25,
        mapped_scenarios=["base"],
        statement="Reach approximately USD 144 million of annual segment revenue.",
    )
    return data


def broken_model() -> dict:
    """A model the engine must refuse: the mapped scenario misses the target."""
    data = add_target(forecast_document(), target_value=1000.0)
    target = data["management_targets"][0]
    target.update(comparison="at_least", mapped_scenarios=["high"])
    return data


def typed_quarterly_model() -> dict:
    """A typed native-quarter bridge: the quarter is summed, never times four."""
    data = forecast_document()
    segment = data["segments"][0]
    quarter_ids = {}
    for scenario, value in (("low", 105840), ("base", 108000), ("high", 110160)):
        pid = add_parameter(data, "quarter_" + scenario, value, 2026, scenario)
        next(p for p in data["parameters"] if p["parameter_id"] == pid)[
            "measurement_period"
        ] = "FY2026Q3"
        quarter_ids[scenario] = [pid]
        annual_id = segment["scenarios"][scenario]["driver_parameter_ids"]["revenue"][0]
        annual = next(p for p in data["parameters"] if p["parameter_id"] == annual_id)
        annual.update(
            kind="derived_fact",
            value=value + 300000,
            formula="x0 + 300000",
            input_parameter_ids=[pid],
        )
    finalize_contract(data)
    add_target(data, period="FY2026", target_value=108, treatment="independent_benchmark",
               measurement_basis="quarterly_period", measurement_periods=[])
    target = data["management_targets"][0]
    target.update(
        target_quarter="Q3",
        raw_target_value=None,
        raw_value_kind="numeric_range",
        raw_target_value_low=105.84,
        raw_target_value_high=110.16,
        raw_unit="USD billion",
        raw_currency="USD",
        raw_scale="billion",
        comparison_value=None,
        comparison="approximately",
        mapped_scenarios=["low", "base", "high"],
        mapped_parameter_ids=quarter_ids["base"],
        benchmark_rationale="Quarter inputs enter the explicit annual bridge.",
        benchmark_claim_ids=["quarter_benchmark"],
        comparison_basis={
            "schema_version": TYPED_SCHEMA,
            "metric_kind": "quarterly_revenue_level",
            "period": "FY2026Q3",
            "scenario_parameter_ids": quarter_ids,
        },
    )
    claim = next(c for c in data["evidence_claims"] if c["claim_id"] in target["claim_ids"])
    claim.pop("extracted_value", None)
    claim["unit"] = "USD billion"
    other = copy.deepcopy(claim)
    other.update(claim_id="quarter_benchmark", support_type="rationale_support")
    data["evidence_claims"].append(other)
    return data
