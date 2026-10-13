"""Extracted from revenue_core.py during the R9 split (behavior-locked by tests/test_golden_behavior_lock.py)."""

from __future__ import annotations

import ast
import math
from collections import defaultdict
from typing import Any, Iterable

from contracts.evidence import (
    ForecastInputError,
    finite_number,
    period_year,
    require,
)
from model_registry import MODEL_DRIVER_DIMENSIONS, driver_value_bounds
from model_extensions import EXTENSION_OPENING_BALANCES
from forecast.dependencies import effective_segment_dependencies, expand_derived_inputs, parameter_uses


def _evaluate_formula_node(node: ast.AST, variables: dict[str, float]) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate_formula_node(node.body, variables)
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, (int, float))
        and not isinstance(node.value, bool)
    ):
        return float(node.value)
    if isinstance(node, ast.Name):
        require(
            node.id in variables, f"unsupported derived formula variable: {node.id}"
        )
        return variables[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate_formula_node(node.operand, variables)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and isinstance(
        node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
    ):
        left = _evaluate_formula_node(node.left, variables)
        right = _evaluate_formula_node(node.right, variables)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            require(not math.isclose(right, 0.0), "derived formula division by zero")
            return left / right
        require(abs(right) <= 10, "derived formula exponent is outside safe range")
        return left**right
    raise ForecastInputError(f"unsupported derived formula node: {type(node).__name__}")


def evaluate_derived_formula(formula: str, inputs: list[float]) -> float:
    require(len(formula) <= 500, "derived formula is too long")
    try:
        parsed = ast.parse(formula, mode="eval")
    except SyntaxError as exc:
        raise ForecastInputError("derived formula is not valid arithmetic") from exc
    try:
        value = _evaluate_formula_node(
            parsed, {f"x{index}": number for index, number in enumerate(inputs)}
        )
    except ArithmeticError as exc:
        raise ForecastInputError("derived formula arithmetic is invalid") from exc
    return finite_number(value, "derived formula result")


def parameter_values(
    parameter_index: dict[str, dict[str, Any]], parameter_ids: Iterable[str]
) -> list[float]:
    values: list[float] = []
    for parameter_id in parameter_ids:
        require(
            parameter_id in parameter_index, f"unknown parameter_id: {parameter_id}"
        )
        values.append(float(parameter_index[parameter_id]["value"]))
    return values


def resolve_driver_series(
    parameter_index: dict[str, dict[str, Any]],
    parameter_ids: Any,
    years: list[int],
    driver: str,
    scenario: str,
    model: str,
) -> list[float]:
    require(
        isinstance(parameter_ids, list),
        f"driver {driver} must be a list of parameter_ids",
    )
    require(
        len(parameter_ids) == len(years),
        f"driver {driver} must contain one parameter_id per forecast year",
    )
    values: list[float] = []
    for year, parameter_id in zip(years, parameter_ids):
        require(
            parameter_id in parameter_index,
            f"unknown parameter_id {parameter_id} for driver {driver}",
        )
        parameter = parameter_index[parameter_id]
        parameter_scenario = parameter.get("scenario")
        require(
            parameter_scenario in (None, "all", scenario),
            f"scenario mismatch: {parameter_id} cannot be used in {scenario}",
        )
        require(
            period_year(parameter["period"], f"{parameter_id}.period") == year,
            f"period mismatch: {parameter_id} does not map to {year}",
        )
        expected_dimension = MODEL_DRIVER_DIMENSIONS[model][driver]
        require(
            parameter["dimension"] == expected_dimension,
            f"dimension mismatch: {parameter_id} must be {expected_dimension} for {model}.{driver}",
        )
        value = float(parameter["value"])
        lower, upper = driver_value_bounds(model, driver)
        require(lower <= value <= upper,
                f"driver {driver} outside permitted bounds "
                f"[{lower}, {upper}]: {parameter_id}")
        values.append(value)
    return values


def _optional_series(
    driver_ids: dict[str, Any],
    driver: str,
    parameter_index: dict[str, dict[str, Any]],
    years: list[int],
    scenario: str,
    model: str,
    default: float = 0.0,
) -> list[float]:
    if driver not in driver_ids:
        return [default] * len(years)
    return resolve_driver_series(
        parameter_index, driver_ids[driver], years, driver, scenario, model
    )


def calculate_cagr(base: float, terminal: float, years: int) -> float | None:
    if base <= 0 or terminal < 0 or years <= 0:
        return None
    return (terminal / base) ** (1 / years) - 1


def referenced_parameter_ids(data: dict[str, Any], scenario: str) -> set[str]:
    return {use.parameter_id for use in parameter_uses(data, scenario)
            if use.kind != "constraint"}


def scenario_forecast_parameter_ids(
    data: dict[str, Any], scenario: str, parameter_index: dict[str, dict[str, Any]]
) -> set[str]:
    """Follow native inputs in one scenario without mixing constraint scenarios."""
    roots = {use.parameter_id for use in parameter_uses(data, scenario)}
    return _expand_derived_inputs(roots & parameter_index.keys(), parameter_index)


def sensitivity_domain_bounds(parameter: dict[str, Any]) -> tuple[float, float] | None:
    """Validate an optional authored domain without guessing a ratio's meaning."""
    if "sensitivity_domain" not in parameter:
        return None
    domain = parameter["sensitivity_domain"]
    field = f"{parameter.get('parameter_id')}.sensitivity_domain"
    require(isinstance(domain, dict) and set(domain) == {"lower", "upper", "basis"},
            f"{field} requires lower, upper and basis")
    require(isinstance(domain["basis"], str) and domain["basis"].strip(),
            f"{field}.basis must be non-empty")
    lower = -math.inf if domain["lower"] is None else finite_number(domain["lower"], f"{field}.lower")
    upper = math.inf if domain["upper"] is None else finite_number(domain["upper"], f"{field}.upper")
    require(lower <= upper, f"{field} requires lower <= upper")
    require(lower <= float(parameter["value"]) <= upper,
            f"{field} must include the original parameter value")
    return lower, upper


def refresh_derived_descendants(
    parameter_index: dict[str, dict[str, Any]], changed_id: str
) -> list[str]:
    """Refresh only descendants in the copied native DAG, in dependency order."""
    children: dict[str, set[str]] = defaultdict(set)
    for parameter_id, parameter in parameter_index.items():
        if parameter.get("kind") == "derived_fact":
            for input_id in parameter["input_parameter_ids"]:
                children[input_id].add(parameter_id)
    affected: set[str] = set()
    pending = [changed_id]
    while pending:
        for child in children[pending.pop()]:
            if child not in affected:
                affected.add(child)
                pending.append(child)
    resolved: set[str] = set()

    def resolve(parameter_id: str, visiting: set[str]) -> float:
        require(parameter_id in parameter_index, f"unknown derived input: {parameter_id}")
        parameter = parameter_index[parameter_id]
        if parameter_id not in affected or parameter_id in resolved:
            return float(parameter["value"])
        require(parameter_id not in visiting, f"derived_fact dependency cycle: {parameter_id}")
        inputs = [resolve(input_id, visiting | {parameter_id})
                  for input_id in parameter["input_parameter_ids"]]
        parameter["value"] = evaluate_derived_formula(parameter["formula"], inputs)
        resolved.add(parameter_id)
        return float(parameter["value"])

    for parameter_id in sorted(affected):
        resolve(parameter_id, set())
    return sorted(affected)


def opening_base_bridge(
    data: dict[str, Any], parameter_index: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Describe the signed opening reconciliation; it never changes forecast revenue."""
    total_id = data["reported_total_revenue_parameter_id"]
    adjustment_ids = data.get("base_adjustment_parameter_ids", [])
    reported = float(parameter_index[total_id]["value"])
    segment_total = sum(float(parameter_index[s["base_revenue_parameter_id"]]["value"])
                        for s in data["segments"])
    adjustment_total = sum(parameter_values(parameter_index, adjustment_ids))
    tolerance = finite_number(data.get("reconciliation_tolerance", 1e-6), "reconciliation_tolerance")
    difference = segment_total + adjustment_total - reported
    require(tolerance >= 0 and abs(difference) <= max(1.0, abs(reported)) * tolerance,
            "opening base bridge does not reconcile within input tolerance")
    return {"reported_total_revenue_parameter_id": total_id,
            "base_adjustment_parameter_ids": list(adjustment_ids),
            "segment_base_total": segment_total, "base_adjustment_total": adjustment_total,
            "reported_base_revenue": reported, "reconciliation_tolerance": tolerance,
            "reconciliation_difference": difference}


def parameter_driver_roles(
    data: dict[str, Any], scenario: str
) -> dict[str, set[tuple[str, str]]]:
    roles: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for segment in data["segments"]:
        scenario_input = segment["scenarios"][scenario]
        model = scenario_input["model"]
        for driver, ids in scenario_input["driver_parameter_ids"].items():
            for parameter_id in ids:
                roles[parameter_id].add((model, driver))
    return roles


def _parse_fiscal_year(value: str) -> int | None:
    """Parse 'FYyyyy' or 'yyyy' to integer year, or return None."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    if value.startswith("FY") and len(value) == 6:
        try:
            return int(value[2:])
        except ValueError:
            return None
    if value.isdigit() and len(value) == 4:
        return int(value)
    return None


def _string_list(
    value: Any, field: str, minimum: int = 1, maximum: int = 10
) -> list[str]:
    require(isinstance(value, list), f"{field} must be a list")
    require(
        minimum <= len(value) <= maximum,
        f"{field} must contain {minimum}-{maximum} items",
    )
    require(
        all(isinstance(item, str) and item.strip() for item in value),
        f"{field} must contain non-empty strings",
    )
    normalized = [item.strip() for item in value]
    require(
        len(normalized) == len(set(normalized)), f"{field} must not contain duplicates"
    )
    return normalized


def _listed_parameter_ids(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _expand_derived_inputs(
    parameter_ids: set[str], parameter_index: dict[str, dict[str, Any]]
) -> set[str]:
    """Compatibility alias for the shared iterative native ancestry visitor."""
    return expand_derived_inputs(parameter_ids, parameter_index)


def _collect_segment_foundation(
    segment: dict[str, Any], foundation: set[str],
) -> None:
    base_id = segment.get("base_revenue_parameter_id")
    if isinstance(base_id, str):
        foundation.add(base_id)
    fields = (
        "base_backlog_parameter_id", "base_orders_parameter_id",
        *(entry[0] for entry in EXTENSION_OPENING_BALANCES.values()),
    )
    for field in fields:
        value = segment.get(field)
        if isinstance(value, str):
            foundation.add(value)


def collect_parameter_roles(
    data: dict[str, Any], parameter_index: dict[str, dict[str, Any]]
) -> dict[str, set[str]]:
    """Collect parameters that actually enter the base or forecast calculation graph."""
    foundation: set[str] = set()
    forecast: set[str] = set()

    total_id = data.get("reported_total_revenue_parameter_id")
    if isinstance(total_id, str):
        foundation.add(total_id)
    foundation.update(
        _listed_parameter_ids(data.get("base_adjustment_parameter_ids", []))
    )
    for segment in data.get("segments", []):
        if isinstance(segment, dict):
            _collect_segment_foundation(segment, foundation)
    forecast.update(use.parameter_id for use in parameter_uses(data))
    foundation = _expand_derived_inputs(foundation, parameter_index)
    forecast = _expand_derived_inputs(forecast, parameter_index)
    return {
        "foundation": foundation,
        "forecast": forecast,
        "used": foundation | forecast,
    }


def base_forecast_parameter_ids(
    data: dict[str, Any], parameter_index: dict[str, dict[str, Any]]
) -> set[str]:
    """Return the expanded parameter set that actually enters the base forecast path."""
    return scenario_forecast_parameter_ids(data, "base", parameter_index)


def base_segment_parameter_ids(
    data: dict[str, Any], parameter_index: dict[str, dict[str, Any]]
) -> dict[str, set[str]]:
    """Map final Base-path value dependencies to affected segment outputs."""
    roots = {name: set().union(*(cell.value_parameter_ids for cell in cells.values()))
             if cells else set()
             for name, cells in effective_segment_dependencies(data, "base").items()}
    return {name: _expand_derived_inputs(ids, parameter_index) for name, ids in roots.items()}
