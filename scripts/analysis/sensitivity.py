"""Extracted from revenue_core.py during the R9 split (behavior-locked by tests/test_golden_behavior_lock.py)."""

from __future__ import annotations

import math
import re
from typing import Any, Iterable, Mapping, Sequence

import copy

from contracts.constants import SCENARIOS
from contracts.evidence import (
    ForecastInputError,
    canonical_sha256,
    finite_number,
    period_year,
    require,
    text_sha256,
)
from forecast.calc import parameter_driver_roles, referenced_parameter_ids
from forecast.segments import _run_forecast_core


def _sensitivity_bounds(
    parameter: dict[str, Any], roles: set[tuple[str, str]]
) -> tuple[float, float]:
    if any(driver == "growth_rate" for _, driver in roles):
        return (-0.999999999, math.inf)
    if parameter["dimension"] == "ratio":
        return (0.0, 1.0)
    if parameter["dimension"] in {
        "quantity",
        "activity",
        "monetary_balance",
        "area",
        "backlog",
        "coverage_units",
        "revenue_per_unit",
        "revenue_per_activity",
        "revenue_per_area",
    }:
        return (0.0, math.inf)
    if parameter["dimension"] == "revenue" and roles:
        return (0.0, math.inf)
    return (-math.inf, math.inf)


def _requested_sensitivity_values(
    test: dict[str, Any], original: float, name: str, dimension: str
) -> tuple[float, float, float | None]:
    shock_type = test.get("shock_type")
    require(
        shock_type
        in {
            "percent",
            "percentage_point",
            "basis_point",
            "absolute",
            "range",
            "discrete",
        },
        f"unsupported sensitivity shock_type for {name}: {shock_type}",
    )
    if shock_type in {"range", "discrete"}:
        down = finite_number(test.get("down_value"), f"{name}.down_value")
        up = finite_number(test.get("up_value"), f"{name}.up_value")
        require(down <= up, f"{name} requires down_value <= up_value")
        return down, up, None
    shock = finite_number(test.get("shock_value"), f"{name}.shock_value")
    require(shock > 0, f"{name}.shock_value must be positive")
    if shock_type == "percent":
        require(
            original != 0,
            f"percent sensitivity cannot be applied to zero parameter: {test.get('parameter_id')}",
        )
        return original * (1 - shock), original * (1 + shock), shock
    if shock_type == "percentage_point":
        require(
            dimension == "ratio",
            f"percentage_point sensitivity requires ratio dimension: {test.get('parameter_id')}",
        )
        return original - shock, original + shock, shock
    if shock_type == "basis_point":
        require(
            dimension == "ratio",
            f"basis_point sensitivity requires ratio dimension: {test.get('parameter_id')}",
        )
        delta = shock / 10000
        return original - delta, original + delta, shock
    return original - shock, original + shock, shock


def calculate_sensitivities(
    data: dict[str, Any], result: dict[str, Any]
) -> list[dict[str, Any]]:
    tests = copy.deepcopy(data.get("sensitivity_tests", data.get("sensitivities", [])))
    require(isinstance(tests, list), "sensitivity_tests must be a list")
    for _test in tests:
        if isinstance(_test, dict) and "name" not in _test and "parameter_id" in _test:
            _test["name"] = _test["parameter_id"]
    if not tests:
        return []
    base_refs = referenced_parameter_ids(data, "base")
    baseline_terminal = result["consolidated_forecast"]["base"]["terminal_revenue"]
    parameter_positions = {
        parameter["parameter_id"]: index
        for index, parameter in enumerate(data["parameters"])
    }
    outputs: list[dict[str, Any]] = []
    names: set[str] = set()
    tested_parameters: set[str] = set()
    roles = parameter_driver_roles(data, "base")
    for test in tests:
        require(isinstance(test, dict), "every sensitivity test must be an object")
        name = test.get("name")
        parameter_id = test.get("parameter_id")
        require(
            isinstance(name, str) and name.strip(), "sensitivity test name is required"
        )
        require(name not in names, f"duplicate sensitivity test name: {name}")
        names.add(name)
        require(
            parameter_id not in tested_parameters,
            f"duplicate sensitivity parameter_id: {parameter_id}",
        )
        tested_parameters.add(parameter_id)
        require(
            parameter_id in base_refs,
            f"sensitivity parameter is not referenced by the base scenario: {parameter_id}",
        )
        require(
            parameter_id in parameter_positions,
            f"unknown sensitivity parameter_id: {parameter_id}",
        )
        parameter = data["parameters"][parameter_positions[parameter_id]]
        require(
            parameter["kind"] in {"analyst_assumption", "scenario_stress"},
            f"sensitivity parameter must be an assumption or stress: {parameter_id}",
        )
        original = float(parameter["value"])
        requested_down, requested_up, shock = _requested_sensitivity_values(
            test, original, name, parameter["dimension"]
        )
        lower, upper = _sensitivity_bounds(parameter, roles.get(parameter_id, set()))
        effective_down = min(max(requested_down, lower), upper)
        effective_up = min(max(requested_up, lower), upper)
        terminals: dict[str, float] = {}
        for direction, shocked_value in (
            ("down", effective_down),
            ("up", effective_up),
        ):
            shocked = copy.deepcopy(data)
            shocked["parameters"][parameter_positions[parameter_id]]["value"] = (
                shocked_value
            )
            shocked.pop("sensitivity_tests", None)
            shocked_result = _run_forecast_core(shocked)
            terminals[direction] = shocked_result["consolidated_forecast"]["base"][
                "terminal_revenue"
            ]
        impact = max(
            abs(terminals["down"] - baseline_terminal),
            abs(terminals["up"] - baseline_terminal),
        )
        outputs.append(
            {
                "name": name,
                "parameter_id": parameter_id,
                "shock_type": test["shock_type"],
                "shock_value": shock,
                "requested_values": {"down": requested_down, "up": requested_up},
                "effective_values": {"down": effective_down, "up": effective_up},
                "clamped": {
                    "down": not math.isclose(requested_down, effective_down),
                    "up": not math.isclose(requested_up, effective_up),
                },
                "baseline_terminal_revenue": baseline_terminal,
                "down_terminal_revenue": terminals["down"],
                "up_terminal_revenue": terminals["up"],
                "max_absolute_terminal_impact": impact,
                "max_relative_terminal_impact": None
                if baseline_terminal == 0
                else impact / baseline_terminal,
            }
        )
    return outputs


def calculate_theme_analysis(
    data: dict[str, Any], validated: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any] | None:
    theme = data.get("theme_analysis")
    if theme is None:
        return None
    require(isinstance(theme, dict), "theme_analysis must be an object")
    require(
        isinstance(theme.get("name"), str) and theme["name"].strip(),
        "theme_analysis.name is required",
    )
    segment_names = theme.get("segment_names")
    require(
        isinstance(segment_names, list) and segment_names,
        "theme_analysis.segment_names is required",
    )
    available = {segment["name"] for segment in result["segments"]}
    require(
        set(segment_names) <= available, "theme_analysis contains an unknown segment"
    )
    counterfactual_ids = theme.get("counterfactual_terminal_parameter_ids")
    require(
        isinstance(counterfactual_ids, dict)
        and set(counterfactual_ids) == set(SCENARIOS),
        "theme counterfactual requires low/base/high parameter IDs",
    )
    output = {"name": theme["name"], "segment_names": segment_names, "scenarios": {}}
    parameter_index = validated["parameter_index"]
    for scenario in SCENARIOS:
        parameter_id = counterfactual_ids[scenario]
        require(
            parameter_id in parameter_index,
            f"unknown theme counterfactual parameter_id: {parameter_id}",
        )
        parameter = parameter_index[parameter_id]
        require(
            parameter.get("scenario") in (None, "all", scenario),
            f"theme counterfactual scenario mismatch: {parameter_id}",
        )
        require(
            parameter["kind"] in {"analyst_assumption", "scenario_stress"},
            f"theme counterfactual must be an explicit assumption: {parameter_id}",
        )
        require(
            parameter["dimension"] == "revenue",
            f"theme counterfactual must use revenue dimension: {parameter_id}",
        )
        require(
            period_year(parameter["period"], f"{parameter_id}.period")
            == validated["years"][-1],
            f"theme counterfactual must use terminal forecast year: {parameter_id}",
        )
        require(
            float(parameter["value"]) >= 0,
            f"theme counterfactual cannot be negative: {parameter_id}",
        )
        theme_revenue = sum(
            list(
                segment["scenarios"][scenario]
                .get(
                    "effective_revenue",
                    segment["scenarios"][scenario]["recognized_revenue"],
                )
                .values()
            )[-1]
            for segment in result["segments"]
            if segment["name"] in segment_names
        )
        counterfactual = float(parameter["value"])
        increment = theme_revenue - counterfactual
        company_terminal = result["consolidated_forecast"][scenario]["terminal_revenue"]
        output["scenarios"][scenario] = {
            "theme_terminal_revenue": theme_revenue,
            "counterfactual_terminal_revenue": counterfactual,
            "theme_incremental_revenue": increment,
            "theme_elasticity_to_company_base": None
            if result["base_revenue"] == 0
            else increment / result["base_revenue"],
            "theme_share_of_company_terminal": None
            if company_terminal == 0
            else theme_revenue / company_terminal,
            "counterfactual_parameter_id": parameter_id,
        }
    return output
