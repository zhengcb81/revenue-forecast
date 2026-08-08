"""Extracted from revenue_core.py during the R9 split (behavior-locked by tests/test_golden_behavior_lock.py)."""

from __future__ import annotations

import math
from typing import Any

from collections import defaultdict

from contracts.constants import FORECAST_SCHEMA_VERSION
from contracts.evidence import (
    parse_iso_date,
)
from contracts.document import validate_historical_accuracy_records


def parameter_revenue_weights(
    data: dict[str, Any], result: dict[str, Any]
) -> dict[str, float]:
    weights: dict[str, float] = defaultdict(float)
    segment_inputs = {segment["name"]: segment for segment in data["segments"]}
    for segment_result in result["segments"]:
        segment = segment_inputs[segment_result["name"]]
        base_output = segment_result["scenarios"]["base"]
        terminal = abs(
            float(
                list(
                    base_output.get(
                        "effective_revenue", base_output["recognized_revenue"]
                    ).values()
                )[-1]
            )
        )
        refs: set[str] = set()
        for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values():
            refs.update(ids)
        recognition = segment["recognition"]
        for container in ("carry_in_parameter_ids", "progress_parameter_ids"):
            values = recognition.get(container, {})
            if isinstance(values, dict):
                refs.update(values.get("base", []))
        if refs:
            for parameter_id in refs:
                weights[parameter_id] += terminal / len(refs)
    for adjustment, bridge in zip(
        data.get("forecast_adjustments", []),
        result["consolidated_forecast"]["base"]["adjustment_bridge"],
    ):
        refs = adjustment["scenario_parameter_ids"]["base"]
        impact = abs(float(list(bridge["annual_adjustment"].values())[-1]))
        if refs:
            for parameter_id in refs:
                weights[parameter_id] += impact / len(refs)
    # Constraint parameters drive effective revenue when constraints are present;
    # include their absolute revenue impact so confidence weights stay aligned
    # with the growth-driver helper.
    for entry in result.get("constraint_audit", []):
        impact = sum(abs(change["adjustment"]) for change in entry.get("changes", []))
        param_ids = entry.get("parameter_ids", [])
        if param_ids and impact > 0:
            for parameter_id in param_ids:
                weights[parameter_id] += impact / len(param_ids)
    return dict(weights)


def calculate_confidence(
    data: dict[str, Any],
    validated: dict[str, Any],
    result: dict[str, Any],
    sensitivities: list[dict[str, Any]],
) -> dict[str, Any]:
    parameters = validated["parameter_index"]
    claims = validated["claim_index"]
    weights = parameter_revenue_weights(data, result)
    total_weight = sum(weights.values())
    covered_weight = sum(
        weight
        for parameter_id, weight in weights.items()
        if parameters[parameter_id].get("claim_ids")
    )
    driver_coverage = 0 if total_weight == 0 else covered_weight / total_weight
    quality_numerator = 0.0
    freshness_numerator = 0.0
    as_of = validated["as_of_date"]
    for parameter_id, weight in weights.items():
        claim_ids = parameters[parameter_id].get("claim_ids", [])
        if not claim_ids:
            continue
        parameter_claims = [claims[claim_id] for claim_id in claim_ids]
        quality = sum(
            1.0
            if claim["support_type"] == "exact_value"
            else 0.8
            if claim["support_type"] == "policy_support"
            else 0.7
            for claim in parameter_claims
        ) / len(parameter_claims)
        ages = [
            (
                as_of
                - parse_iso_date(
                    validated["source_index"][claim["source_id"]]["published_date"],
                    "published_date",
                )
            ).days
            for claim in parameter_claims
        ]
        freshness = sum(
            1.0 if age <= 180 else 0.8 if age <= 365 else 0.5 if age <= 730 else 0.2
            for age in ages
        ) / len(ages)
        quality_numerator += weight * quality
        freshness_numerator += weight * freshness
    source_quality = 0 if covered_weight == 0 else quality_numerator / covered_weight
    freshness = 0 if covered_weight == 0 else freshness_numerator / covered_weight

    segment_total = sum(
        abs(
            float(
                list(
                    segment["scenarios"]["base"]
                    .get(
                        "effective_revenue",
                        segment["scenarios"]["base"]["recognized_revenue"],
                    )
                    .values()
                )[-1]
            )
        )
        for segment in result["segments"]
    )
    explicit_total = sum(
        abs(
            float(
                list(
                    segment["scenarios"]["base"]
                    .get(
                        "effective_revenue",
                        segment["scenarios"]["base"]["recognized_revenue"],
                    )
                    .values()
                )[-1]
            )
        )
        for segment in result["segments"]
        if segment["scenarios"]["base"]["model"]
        not in {"direct_growth", "direct_revenue"}
    )
    explicit_model_share = 0 if segment_total == 0 else explicit_total / segment_total

    historical_wape, historical_observations = validate_historical_accuracy_records(
        data
    )
    history_score = (
        0.0
        if historical_wape is None
        else 15
        if historical_wape <= 0.05
        else 12
        if historical_wape <= 0.10
        else 8
        if historical_wape <= 0.20
        else 4
        if historical_wape <= 0.30
        else 0
    )

    sensitivity_coverage = 0.0
    concentration = None
    if sensitivities:
        impacts = [item["max_absolute_terminal_impact"] for item in sensitivities]
        total_impact = sum(impacts)
        concentration = 0 if total_impact == 0 else max(impacts) / total_impact
        tested = {item["parameter_id"] for item in sensitivities}
        sensitivity_coverage = (
            0
            if total_weight == 0
            else sum(
                weight
                for parameter_id, weight in weights.items()
                if parameter_id in tested
            )
            / total_weight
        )

    components = {
        "verified_claim_quality": 20 * source_quality,
        "verified_claim_coverage": 25 * driver_coverage,
        "source_freshness": 10 * freshness,
        "revenue_weighted_explicit_models": 15 * explicit_model_share,
        "historical_accuracy": history_score,
        "revenue_weighted_sensitivity_coverage": 15 * sensitivity_coverage,
    }
    score = sum(components.values())
    rating = "high" if score >= 80 else "medium" if score >= 55 else "low"
    quality_gates = {
        "base_reconciliation": True,
        "recognition_contract": True,
        "scenario_consistency": True,
        "research_coverage": True,
    }
    if data.get("schema_version") in {"3.1", "3.2", FORECAST_SCHEMA_VERSION}:
        quality_gates["management_target_coverage"] = True
    if data.get("schema_version") == FORECAST_SCHEMA_VERSION:
        quality_gates["growth_driver_tree"] = True
    limitations = [
        item
        for condition, item in (
            (
                covered_weight == 0,
                "No verified claims for revenue-weighted base drivers",
            ),
            (historical_wape is None, "No immutable historical backtest record"),
            (not sensitivities, "No deterministic sensitivity tests"),
            (
                explicit_model_share < 1,
                "One or more segments use a direct fallback model",
            ),
            (
                validated["research_coverage"]["counts"]["data_gap"] > 0,
                f"Research coverage contains {validated['research_coverage']['counts']['data_gap']} material data gap(s)",
            ),
        )
        if condition
    ]
    target_coverage = validated.get("management_target_coverage")
    if target_coverage and target_coverage["counts"]["targets_unmodeled"] > 0:
        limitations.append(
            f"Management target coverage contains {target_coverage['counts']['targets_unmodeled']} unmodeled material/contextual target(s)"
        )
    limitations.extend(validated.get("growth_driver_tree", {}).get("limitations", []))
    growth_analysis = result.get("growth_driver_analysis")
    if growth_analysis and not math.isclose(
        float(growth_analysis.get("unattributed_company_adjustments", 0)),
        0.0,
        rel_tol=0,
        abs_tol=1e-9,
    ):
        limitations.append(
            "Company-level forecast adjustments are disclosed separately from operating growth-driver ranking"
        )
    return {
        "score": score,
        "rating": rating,
        "components": components,
        "driver_evidence_coverage": driver_coverage,
        "sensitivity_concentration": concentration,
        "historical_accuracy": {
            "wape": historical_wape,
            "observations": historical_observations,
        },
        "quality_gates": quality_gates,
        "limitations": limitations,
    }
