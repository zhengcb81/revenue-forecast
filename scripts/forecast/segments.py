"""Extracted from revenue_core.py during the R9 split (behavior-locked by tests/test_golden_behavior_lock.py)."""

from __future__ import annotations

import math
import re
from typing import Any, Iterable, Mapping, Sequence

import copy

from contracts.constants import (
    ADJUSTMENT_CATEGORIES,
    PRESENTATIONS,
    RECOGNITION_MODES,
    RECOGNITION_TIMING,
    SCENARIOS,
)
from contracts.document import validate_document, validate_scenario_probabilities
from contracts.evidence import (
    ForecastInputError,
    canonical_sha256,
    period_year,
    require,
    text_sha256,
    validate_claim_ids,
)
from forecast.calc import (
    _optional_series,
    calculate_cagr,
    parameter_values,
    resolve_driver_series,
)
from model_registry import MODEL_SPECS, ModelRegistryError, calculate_registered_model
from revenue_constraints import RevenueConstraintError, apply_revenue_constraints


def calculate_model_path(
    model: str,
    base_revenue: float,
    driver_ids: dict[str, Any],
    parameter_index: dict[str, dict[str, Any]],
    years: list[int],
    scenario: str,
) -> dict[str, Any]:
    """Calculate one segment/scenario path from registered parameter IDs."""
    require(model in MODEL_SPECS, f"unsupported revenue model: {model}")
    require(scenario in SCENARIOS, f"unsupported scenario: {scenario}")
    require(
        isinstance(driver_ids, dict),
        f"driver_parameter_ids must be an object for {model}",
    )
    spec = MODEL_SPECS[model]
    allowed = set(spec["required"]) | set(spec["optional"])
    missing = [driver for driver in spec["required"] if driver not in driver_ids]
    require(not missing, f"missing drivers for {model}: {', '.join(missing)}")
    extra = sorted(set(driver_ids) - allowed)
    require(not extra, f"unsupported drivers for {model}: {', '.join(extra)}")
    if model == "retail_franchise":
        pair = {"franchise_system_sales", "recognized_fee_rate"}
        require(
            not (set(driver_ids) & pair) or pair <= set(driver_ids),
            "retail_franchise requires franchise_system_sales and recognized_fee_rate together",
        )

    drivers: dict[str, list[float]] = {}
    for driver in spec["required"]:
        drivers[driver] = resolve_driver_series(
            parameter_index, driver_ids[driver], years, driver, scenario, model
        )
    for driver in spec["optional"]:
        drivers[driver] = _optional_series(
            driver_ids,
            driver,
            parameter_index,
            years,
            scenario,
            model,
            float(spec.get("defaults", {}).get(driver, 0.0)),
        )

    try:
        revenue = calculate_registered_model(model, base_revenue, drivers, years)
    except ModelRegistryError as exc:
        raise ForecastInputError(str(exc)) from exc
    for year, value in zip(years, revenue):
        require(
            value >= 0 and math.isfinite(value),
            f"calculated revenue must be finite and non-negative for {model}/{year}",
        )

    return {
        "model": model,
        "formula": spec["formula"],
        "annual_revenue": dict(zip(map(str, years), revenue)),
        "driver_values": {
            name: dict(zip(map(str, years), values)) for name, values in drivers.items()
        },
        "driver_parameter_ids": copy.deepcopy(driver_ids),
    }


def calculate_segment_forecasts(
    data: dict[str, Any], validated: dict[str, Any]
) -> list[dict[str, Any]]:
    years = validated["years"]
    parameter_index = validated["parameter_index"]
    results: list[dict[str, Any]] = []
    for segment in data["segments"]:
        name = segment["name"]
        base = float(parameter_index[segment["base_revenue_parameter_id"]]["value"])
        scenarios = segment.get("scenarios")
        require(
            isinstance(scenarios, dict) and set(scenarios) == set(SCENARIOS),
            f"{name} must contain low/base/high scenarios",
        )
        models = {scenarios[scenario].get("model") for scenario in SCENARIOS}
        require(len(models) == 1, f"{name} must use the same model across scenarios")
        model = next(iter(models))
        opening_checks = {
            "project_backlog": (
                "base_backlog_parameter_id",
                "opening_backlog",
                "backlog",
            ),
            "delivery_pipeline": (
                "base_orders_parameter_id",
                "opening_orders",
                "quantity",
            ),
        }
        if model in opening_checks:
            base_field, opening_driver, expected_dimension = opening_checks[model]
            opening_base_id = segment.get(base_field)
            require(
                opening_base_id in parameter_index,
                f"{name}/{model} requires valid {base_field}",
            )
            opening_base = parameter_index[opening_base_id]
            require(
                opening_base["dimension"] == expected_dimension,
                f"{name}/{base_field} has wrong dimension",
            )
            require(
                period_year(opening_base["period"], f"{opening_base_id}.period")
                == data["base_year"],
                f"{name}/{base_field} must use base year",
            )
            for scenario in SCENARIOS:
                opening_ids = (
                    scenarios[scenario]
                    .get("driver_parameter_ids", {})
                    .get(opening_driver, [])
                )
                require(
                    bool(opening_ids), f"{name}/{scenario} requires {opening_driver}"
                )
                require(
                    math.isclose(
                        float(parameter_index[opening_ids[0]]["value"]),
                        float(opening_base["value"]),
                        rel_tol=1e-9,
                        abs_tol=1e-9,
                    ),
                    f"{name}/{scenario} first opening does not reconcile to {base_field}",
                )
        scenario_results: dict[str, Any] = {}
        for scenario in SCENARIOS:
            scenario_input = scenarios[scenario]
            require(
                isinstance(scenario_input.get("rationale"), str)
                and scenario_input["rationale"].strip(),
                f"{name}/{scenario} requires rationale",
            )
            path = calculate_model_path(
                scenario_input["model"],
                base,
                scenario_input.get("driver_parameter_ids", {}),
                parameter_index,
                years,
                scenario,
            )
            path["rationale"] = scenario_input["rationale"]
            scenario_results[scenario] = path
        results.append(
            {
                "name": name,
                "base_revenue": base,
                "base_revenue_parameter_id": segment["base_revenue_parameter_id"],
                "scenarios": scenario_results,
            }
        )
    return results


def validate_recognition_metadata(
    segment: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
    claim_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    name = segment["name"]
    recognition = segment.get("recognition")
    require(isinstance(recognition, dict), f"{name} requires recognition metadata")
    mode = recognition.get("mode")
    timing = recognition.get("timing")
    presentation = recognition.get("presentation")
    require(
        mode in RECOGNITION_MODES, f"unsupported recognition mode for {name}: {mode}"
    )
    require(
        timing in RECOGNITION_TIMING,
        f"unsupported recognition timing for {name}: {timing}",
    )
    require(
        presentation in PRESENTATIONS,
        f"unsupported presentation for {name}: {presentation}",
    )
    require(
        recognition.get("modeled_presentation") == presentation,
        f"{name} modeled_presentation must match accounting presentation",
    )
    require(
        isinstance(recognition.get("trigger"), str) and recognition["trigger"].strip(),
        f"{name} requires a revenue-recognition trigger",
    )
    if timing == "over_time":
        require(
            isinstance(recognition.get("progress_measure"), str)
            and recognition["progress_measure"].strip(),
            f"{name} over-time recognition requires progress_measure",
        )
        require(
            mode != "lagged_activity",
            f"{name} cannot combine over_time with lagged_activity",
        )
        progress = recognition.get("progress_parameter_ids")
        require(
            isinstance(progress, dict) and set(progress) == set(SCENARIOS),
            f"{name} over-time recognition requires low/base/high progress_parameter_ids",
        )
    basis_claims = validate_claim_ids(
        recognition.get("basis_claim_ids"),
        claim_index,
        "recognition_policy",
        f"recognition:{name}",
        f"{name}.recognition",
        "policy_support",
    )
    basis_source_ids = sorted({claim["source_id"] for claim in basis_claims})
    require(bool(basis_source_ids), f"{name} recognition requires policy evidence")
    recognition = dict(recognition)
    recognition["basis_source_ids"] = basis_source_ids
    if mode == "lagged_activity":
        lag_years = recognition.get("lag_years")
        require(
            isinstance(lag_years, int) and lag_years > 0,
            f"{name} lagged_activity requires positive integer lag_years",
        )
        carry_in = recognition.get("carry_in_parameter_ids")
        require(
            isinstance(carry_in, dict) and set(carry_in) == set(SCENARIOS),
            f"{name} lagged_activity requires low/base/high carry_in_parameter_ids",
        )
    return recognition


def apply_revenue_recognition(
    data: dict[str, Any],
    validated: dict[str, Any],
    segment_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    years = validated["years"]
    parameter_index = validated["parameter_index"]
    source_index = validated["source_index"]
    claim_index = validated["claim_index"]
    segment_inputs = {segment["name"]: segment for segment in data["segments"]}
    recognized_results: list[dict[str, Any]] = []
    for result in segment_results:
        segment = segment_inputs[result["name"]]
        recognition = validate_recognition_metadata(segment, source_index, claim_index)
        enriched = dict(result)
        enriched["recognition"] = copy.deepcopy(recognition)
        scenario_outputs: dict[str, Any] = {}
        for scenario in SCENARIOS:
            modeled = list(result["scenarios"][scenario]["annual_revenue"].values())
            progress_values: list[float] = []
            if recognition["timing"] == "over_time":
                progress_ids = recognition["progress_parameter_ids"][scenario]
                require(
                    isinstance(progress_ids, list) and len(progress_ids) == len(years),
                    f"{result['name']}/{scenario} progress_parameter_ids must contain one parameter per year",
                )
                for year, parameter_id in zip(years, progress_ids):
                    require(
                        parameter_id in parameter_index,
                        f"unknown progress parameter_id: {parameter_id}",
                    )
                    parameter = parameter_index[parameter_id]
                    require(
                        parameter["dimension"] == "ratio",
                        f"progress parameter must use ratio dimension: {parameter_id}",
                    )
                    require(
                        period_year(parameter["period"], f"{parameter_id}.period")
                        == year,
                        f"progress period mismatch: {parameter_id}",
                    )
                    require(
                        parameter.get("scenario") in (None, "all", scenario),
                        f"progress scenario mismatch: {parameter_id}",
                    )
                    progress_values.append(float(parameter["value"]))
                require(
                    all(0 <= value <= 1 for value in progress_values),
                    f"{result['name']}/{scenario} progress must be between 0 and 1",
                )
                recognized = [
                    value * progress
                    for value, progress in zip(modeled, progress_values)
                ]
                tail = [
                    value - recognized_value
                    for value, recognized_value in zip(modeled, recognized)
                ]
                carry_in_values = []
            elif recognition["mode"] == "modeled_as_recognized":
                recognized = modeled
                tail: list[float] = []
                carry_in_values: list[float] = []
            else:
                lag = recognition["lag_years"]
                require(
                    lag <= len(years),
                    f"{result['name']} lag_years exceeds forecast horizon",
                )
                carry_ids = recognition["carry_in_parameter_ids"][scenario]
                require(
                    isinstance(carry_ids, list) and len(carry_ids) == lag,
                    f"{result['name']}/{scenario} carry-in count must equal lag_years",
                )
                carry_in_values = parameter_values(parameter_index, carry_ids)
                for offset, parameter_id in enumerate(carry_ids):
                    parameter = parameter_index[parameter_id]
                    require(
                        period_year(parameter["period"], f"{parameter_id}.period")
                        == years[offset],
                        f"carry-in period mismatch: {parameter_id}",
                    )
                    require(
                        parameter["dimension"] == "revenue",
                        f"carry-in must use revenue dimension: {parameter_id}",
                    )
                    require(
                        parameter.get("scenario") in (None, "all", scenario),
                        f"carry-in scenario mismatch: {parameter_id}",
                    )
                    require(
                        parameter["value"] >= 0,
                        f"carry-in revenue cannot be negative: {parameter_id}",
                    )
                recognized = carry_in_values + modeled[:-lag]
                tail = modeled[-lag:]
            scenario_output = dict(result["scenarios"][scenario])
            scenario_output["modeled_activity"] = scenario_output.pop("annual_revenue")
            scenario_output["recognized_revenue"] = dict(
                zip(map(str, years), recognized)
            )
            scenario_output["carry_in_revenue"] = carry_in_values
            scenario_output["unrecognized_tail_activity"] = tail
            scenario_output["progress_values"] = (
                dict(zip(map(str, years), progress_values)) if progress_values else None
            )
            scenario_outputs[scenario] = scenario_output
        enriched["scenarios"] = scenario_outputs
        recognized_results.append(enriched)
    return recognized_results


def resolve_adjustments(
    data: dict[str, Any],
    validated: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    years = validated["years"]
    parameter_index = validated["parameter_index"]
    adjustments = data.get("forecast_adjustments", [])
    require(isinstance(adjustments, list), "forecast_adjustments must be a list")
    names: set[str] = set()
    result = {scenario: [] for scenario in SCENARIOS}
    for adjustment in adjustments:
        require(
            isinstance(adjustment, dict), "every forecast adjustment must be an object"
        )
        name = adjustment.get("name")
        category = adjustment.get("category")
        require(
            isinstance(name, str) and name.strip(),
            "forecast adjustment name is required",
        )
        require(name not in names, f"duplicate forecast adjustment name: {name}")
        names.add(name)
        require(
            category in ADJUSTMENT_CATEGORIES,
            f"unsupported forecast adjustment category: {category}",
        )
        scenario_ids = adjustment.get("scenario_parameter_ids")
        require(
            isinstance(scenario_ids, dict) and set(scenario_ids) == set(SCENARIOS),
            f"{name} must contain low/base/high parameter IDs",
        )
        for scenario in SCENARIOS:
            ids = scenario_ids[scenario]
            require(
                isinstance(ids, list) and len(ids) == len(years),
                f"{name}/{scenario} must contain one parameter ID per year",
            )
            values: list[float] = []
            for year, parameter_id in zip(years, ids):
                require(
                    parameter_id in parameter_index,
                    f"unknown adjustment parameter_id: {parameter_id}",
                )
                parameter = parameter_index[parameter_id]
                require(
                    period_year(parameter["period"], f"{parameter_id}.period") == year,
                    f"adjustment period mismatch: {parameter_id}",
                )
                require(
                    parameter["dimension"] == "revenue",
                    f"adjustment must use revenue dimension: {parameter_id}",
                )
                require(
                    parameter.get("scenario") in (None, "all", scenario),
                    f"adjustment scenario mismatch: {parameter_id}",
                )
                values.append(float(parameter["value"]))
            if category in {"intersegment_elimination", "disposal_contribution"}:
                require(
                    all(value <= 0 for value in values),
                    f"{category} must use non-positive signed values: {name}/{scenario}",
                )
            if category == "acquisition_contribution":
                require(
                    all(value >= 0 for value in values),
                    f"acquisition_contribution must use non-negative values: {name}/{scenario}",
                )
            result[scenario].append(
                {
                    "name": name,
                    "category": category,
                    "annual_adjustment": dict(zip(map(str, years), values)),
                    "parameter_ids": ids,
                }
            )
    return result


def calculate_company_forecast(
    data: dict[str, Any],
    validated: dict[str, Any],
    recognized_segments: list[dict[str, Any]],
) -> dict[str, Any]:
    years = validated["years"]
    parameter_index = validated["parameter_index"]
    reported_base = float(
        parameter_index[data["reported_total_revenue_parameter_id"]]["value"]
    )
    adjustments = resolve_adjustments(data, validated)
    consolidated: dict[str, Any] = {}
    for scenario in SCENARIOS:
        segment_totals = [0.0] * len(years)
        segment_bridge: list[dict[str, Any]] = []
        for segment in recognized_segments:
            scenario_output = segment["scenarios"][scenario]
            values = list(
                scenario_output.get(
                    "effective_revenue", scenario_output["recognized_revenue"]
                ).values()
            )
            segment_totals = [
                left + right for left, right in zip(segment_totals, values)
            ]
            segment_bridge.append(
                {
                    "name": segment["name"],
                    "annual_revenue": dict(zip(map(str, years), values)),
                }
            )
        adjustment_totals = [0.0] * len(years)
        for adjustment in adjustments[scenario]:
            values = list(adjustment["annual_adjustment"].values())
            adjustment_totals = [
                left + right for left, right in zip(adjustment_totals, values)
            ]
        company_values = [
            segment + adjustment
            for segment, adjustment in zip(segment_totals, adjustment_totals)
        ]
        require(
            all(value >= 0 and math.isfinite(value) for value in company_values),
            f"company revenue must be finite and non-negative in {scenario}",
        )
        annual_growth: dict[str, float | None] = {}
        previous = reported_base
        for year, value in zip(years, company_values):
            annual_growth[str(year)] = None if previous == 0 else value / previous - 1
            previous = value
        base_adjustment_total = sum(
            parameter_values(
                parameter_index, data.get("base_adjustment_parameter_ids", [])
            )
        )
        segment_contributions = [
            {
                "name": segment["name"],
                "terminal_incremental_revenue": list(
                    segment["scenarios"][scenario]
                    .get(
                        "effective_revenue",
                        segment["scenarios"][scenario]["recognized_revenue"],
                    )
                    .values()
                )[-1]
                - segment["base_revenue"],
            }
            for segment in recognized_segments
        ]
        adjustment_increment = adjustment_totals[-1] - base_adjustment_total
        contribution_sum = (
            sum(item["terminal_incremental_revenue"] for item in segment_contributions)
            + adjustment_increment
        )
        company_increment = company_values[-1] - reported_base
        require(
            math.isclose(
                contribution_sum, company_increment, rel_tol=1e-9, abs_tol=1e-9
            ),
            f"incremental revenue attribution does not reconcile in {scenario}",
        )
        consolidated[scenario] = {
            "segment_bridge": segment_bridge,
            "adjustment_bridge": adjustments[scenario],
            "segment_subtotal": dict(zip(map(str, years), segment_totals)),
            "adjustment_total": dict(zip(map(str, years), adjustment_totals)),
            "annual_revenue": dict(zip(map(str, years), company_values)),
            "annual_growth": annual_growth,
            "terminal_revenue": company_values[-1],
            "cagr": calculate_cagr(reported_base, company_values[-1], len(years)),
            "incremental_revenue": company_increment,
            "incremental_contribution": {
                "segments": segment_contributions,
                "adjustments": adjustment_increment,
                "total": contribution_sum,
            },
        }
    return {
        "base_revenue": reported_base,
        "segments": recognized_segments,
        "consolidated_forecast": consolidated,
    }


def _run_forecast_core(data: dict[str, Any]) -> dict[str, Any]:
    """Run validation, segment models, recognition, and company aggregation."""
    validated = validate_document(data)
    modeled_segments = calculate_segment_forecasts(data, validated)
    recognized_segments = apply_revenue_recognition(data, validated, modeled_segments)
    try:
        effective_segments, constraint_audit = apply_revenue_constraints(
            recognized_segments,
            data.get("revenue_constraints", []),
            validated["parameter_index"],
            validated["years"],
        )
    except RevenueConstraintError as exc:
        raise ForecastInputError(str(exc)) from exc
    company = calculate_company_forecast(data, validated, effective_segments)
    return {
        "company_name": data["company_name"],
        "as_of_date": data["as_of_date"],
        "currency": data["currency"],
        "unit": data["unit"],
        "fiscal_year_end": data["fiscal_year_end"],
        "base_year": data["base_year"],
        "forecast_years": validated["years"],
        "historical_revenue": data["historical_revenue"],
        "revenue_constraints": copy.deepcopy(data.get("revenue_constraints", [])),
        "constraint_audit": constraint_audit,
        **company,
    }


def add_scenario_analysis(
    data: dict[str, Any], validated: dict[str, Any], result: dict[str, Any]
) -> None:
    years = validated["years"]
    consolidated = result["consolidated_forecast"]
    for segment in result["segments"]:
        for year in map(str, years):
            low = segment["scenarios"]["low"].get(
                "effective_revenue", segment["scenarios"]["low"]["recognized_revenue"]
            )[year]
            base = segment["scenarios"]["base"].get(
                "effective_revenue", segment["scenarios"]["base"]["recognized_revenue"]
            )[year]
            high = segment["scenarios"]["high"].get(
                "effective_revenue", segment["scenarios"]["high"]["recognized_revenue"]
            )[year]
            require(
                low <= base <= high,
                f"segment scenario ordering failed for {segment['name']}/{year}",
            )
    for year in map(str, years):
        low = consolidated["low"]["annual_revenue"][year]
        base = consolidated["base"]["annual_revenue"][year]
        high = consolidated["high"]["annual_revenue"][year]
        require(
            low <= base <= high,
            f"scenario ordering failed in {year}: low <= base <= high is required",
        )
    probabilities = validate_scenario_probabilities(data, validated)
    result["scenario_probabilities"] = probabilities
    result["probability_weighted_forecast"] = None
    if probabilities is None:
        return
    values = [
        sum(
            probabilities[scenario]
            * consolidated[scenario]["annual_revenue"][str(year)]
            for scenario in SCENARIOS
        )
        for year in years
    ]
    result["probability_weighted_forecast"] = {
        "annual_revenue": dict(zip(map(str, years), values)),
        "terminal_revenue": values[-1],
        "expected_terminal_implied_cagr": calculate_cagr(
            result["base_revenue"], values[-1], len(years)
        ),
        "incremental_revenue": values[-1] - result["base_revenue"],
        "probability_rationale": data["probability_rationale"],
        "probability_source_ids": data["probability_source_ids"],
    }
