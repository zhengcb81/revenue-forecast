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

_TEST_ROOT = Path(__file__).resolve().parents[1]
if str(_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT))
if str(_TEST_ROOT.parent / "scripts") not in sys.path:
    sys.path.insert(0, str(_TEST_ROOT.parent / "scripts"))

from test_management_targets import add_target  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

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
        statement="Reach at least USD 1000 million of annual segment revenue.",
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


def broken_model() -> dict:
    """A model the engine must refuse: the mapped scenario misses the target."""
    data = add_target(forecast_document(), target_value=1000.0)
    target = data["management_targets"][0]
    target.update(comparison="at_least", mapped_scenarios=["high"])
    return data
