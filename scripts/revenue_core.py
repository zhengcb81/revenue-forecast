"""Core validation and calculation primitives for revenue-only forecasts."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
import re
from collections import defaultdict
from datetime import date
from typing import Any, Iterable
from urllib.parse import urlparse

from model_registry import (
    MODEL_DRIVER_DIMENSIONS as REGISTERED_MODEL_DRIVER_DIMENSIONS,
    MODEL_RATIO_DRIVERS as REGISTERED_MODEL_RATIO_DRIVERS,
    MODEL_SPECS as REGISTERED_MODEL_SPECS,
    ModelRegistryError,
    calculate_registered_model,
)
from revenue_constraints import (
    RevenueConstraintError,
    apply_revenue_constraints,
    constraint_parameter_ids,
    validate_revenue_constraints,
)


SCENARIOS = ("low", "base", "high")
SKILL_VERSION = "3.4.0"
# Compatibility name retained in serialized forecasts and snapshots.
ENGINE_VERSION = SKILL_VERSION
FORECAST_SCHEMA_VERSION = "3.3"
SUPPORTED_FORECAST_SCHEMA_VERSIONS = {"3.0", "3.1", "3.2", FORECAST_SCHEMA_VERSION}
PARAMETER_KINDS = {
    "reported_fact",
    "derived_fact",
    "management_guidance",
    "analyst_assumption",
    "scenario_stress",
}
SOURCE_RANKS = {
    "audited_filing": 1,
    "exchange_filing": 1,
    "regulatory_filing": 1,
    "official_statistics": 1,
    "company_release": 2,
    "investor_presentation": 2,
    "earnings_transcript": 2,
    "official_operating_data": 2,
    "contract_award": 3,
    "customer_filing": 3,
    "tender_document": 3,
    "sector_regulator": 3,
    "industry_association": 4,
    "primary_market_dataset": 4,
    "specialist_research": 5,
    "reputable_news": 5,
}
BLOCKED_HOSTS = {
    "example.com",
    "www.example.com",
    "localhost",
    "127.0.0.1",
    "google.com",
    "www.google.com",
    "bing.com",
    "www.bing.com",
    "baidu.com",
    "www.baidu.com",
}

MODEL_SPECS = REGISTERED_MODEL_SPECS
MODEL_RATIO_DRIVERS = REGISTERED_MODEL_RATIO_DRIVERS
MODEL_DRIVER_DIMENSIONS = REGISTERED_MODEL_DRIVER_DIMENSIONS
PARAMETER_DIMENSIONS = {
    "revenue", "quantity", "ratio", "revenue_per_unit", "activity",
    "revenue_per_activity", "monetary_balance", "area", "revenue_per_area",
    "backlog", "coverage_units",
}
MONETARY_DIMENSIONS = {"revenue", "revenue_per_unit", "revenue_per_activity", "monetary_balance", "revenue_per_area", "backlog"}
TIME_BASES = {"annual", "point_in_time"}

RECOGNITION_MODES = {"modeled_as_recognized", "lagged_activity"}
RECOGNITION_TIMING = {"point_in_time", "over_time"}
PRESENTATIONS = {"gross", "net"}
ADJUSTMENT_CATEGORIES = {
    "intersegment_elimination",
    "acquisition_contribution",
    "disposal_contribution",
    "foreign_exchange",
    "reclassification",
    "other",
}
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
RESEARCH_COVERAGE_STATUSES = {"modeled_driver", "data_gap", "immaterial"}
MANAGEMENT_COMMUNICATION_CATEGORIES = (
    "latest_annual_filing",
    "latest_results_release",
    "latest_earnings_call",
    "latest_investor_presentation",
    "latest_strategy_communication",
    "material_announcements_since_last_filing",
)
MANAGEMENT_COMMUNICATION_STATUSES = {"checked", "not_available", "not_applicable"}
MANAGEMENT_TARGET_TREATMENTS = {
    "modeled_scenario",
    "scenario_boundary",
    "sensitivity_only",
    "unmodeled_data_gap",
    "out_of_horizon",
}
MANAGEMENT_TARGET_PERIMETERS = {"matched", "reconciled", "mismatch"}
MANAGEMENT_TARGET_COMPARISONS = {"at_least", "at_most", "approximately"}
MANAGEMENT_TARGET_MEASUREMENT_BASES = {
    "annual_period",
    "run_rate_at_period_end",
    "cumulative_periods",
    "ambiguous",
}
GROWTH_DRIVER_TREE_STATUSES = {"modeled", "data_gap"}
GROWTH_DRIVER_PERSISTENCE = {"multi_year_structural", "cyclical", "temporary", "uncertain"}
GROWTH_DRIVER_INFERENCE_DISTANCES = {"direct", "one_step", "analogical", "contrary"}
GROWTH_DRIVER_COUNTEREVIDENCE_STATUSES = {"found", "searched_none_found", "data_gap"}


class ForecastInputError(ValueError):
    """Raised when an input violates the auditable revenue contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ForecastInputError(message)


def parse_iso_date(value: Any, field: str) -> date:
    require(isinstance(value, str) and bool(value.strip()), f"{field} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ForecastInputError(f"{field} must use YYYY-MM-DD") from exc


def finite_number(value: Any, field: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{field} must be numeric")
    number = float(value)
    require(math.isfinite(number), f"{field} must be finite")
    return number


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()


def period_year(value: Any, field: str) -> int:
    require(isinstance(value, str) and re.fullmatch(r"FY\d{4}", value) is not None, f"{field} must use strict FYyyyy format")
    return int(value[2:])


def _evaluate_formula_node(node: ast.AST, variables: dict[str, float]) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate_formula_node(node.body, variables)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.Name):
        require(node.id in variables, f"unsupported derived formula variable: {node.id}")
        return variables[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate_formula_node(node.operand, variables)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
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
        return left ** right
    raise ForecastInputError(f"unsupported derived formula node: {type(node).__name__}")


def evaluate_derived_formula(formula: str, inputs: list[float]) -> float:
    require(len(formula) <= 500, "derived formula is too long")
    try:
        parsed = ast.parse(formula, mode="eval")
    except SyntaxError as exc:
        raise ForecastInputError("derived formula is not valid arithmetic") from exc
    value = _evaluate_formula_node(parsed, {f"x{index}": number for index, number in enumerate(inputs)})
    require(math.isfinite(value), "derived formula result must be finite")
    return value


def valid_source_url(url: Any) -> bool:
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        return False
    if host in BLOCKED_HOSTS or host.endswith(".example"):
        return False
    return "." in host


def validate_top_level(data: dict[str, Any]) -> tuple[list[int], date]:
    required = (
        "schema_version",
        "company_name",
        "as_of_date",
        "currency",
        "unit",
        "fiscal_year_end",
        "base_year",
        "forecast_years",
        "historical_revenue",
        "sources",
        "parameters",
        "segments",
        "reported_total_revenue_parameter_id",
        "research_coverage",
        "growth_driver_tree",
        "management_communication_coverage",
        "management_targets",
        "evidence_claims",
    )
    for key in required:
        require(key in data, f"missing required field: {key}")

    require(data["schema_version"] == FORECAST_SCHEMA_VERSION, f"schema_version must be {FORECAST_SCHEMA_VERSION}")

    require(isinstance(data["company_name"], str) and data["company_name"].strip(), "company_name is required")
    as_of = parse_iso_date(data["as_of_date"], "as_of_date")
    require(isinstance(data["currency"], str) and data["currency"].strip(), "currency is required")
    require(isinstance(data["unit"], str) and data["unit"].strip(), "unit is required")
    require(isinstance(data["fiscal_year_end"], str) and re.fullmatch(r"\d{2}-\d{2}", data["fiscal_year_end"]), "fiscal_year_end must use MM-DD")
    try:
        date(2000, int(data["fiscal_year_end"][:2]), int(data["fiscal_year_end"][3:]))
    except ValueError as exc:
        raise ForecastInputError("fiscal_year_end is not a valid month-day") from exc
    require(isinstance(data["base_year"], int), "base_year must be an integer")

    years = data["forecast_years"]
    require(isinstance(years, list) and years, "forecast_years must be a non-empty list")
    require(all(isinstance(year, int) for year in years), "forecast_years must contain integers")
    require(years == sorted(years) and len(years) == len(set(years)), "forecast_years must be unique and increasing")
    require(years[0] == data["base_year"] + 1, "forecast_years must start after base_year")
    require(all(right - left == 1 for left, right in zip(years, years[1:])), "forecast_years must be consecutive")
    for field in ("data_gaps", "disconfirming_indicators"):
        if field in data:
            values = data[field]
            require(isinstance(values, list), f"{field} must be a list of strings")
            require(all(isinstance(value, str) and value.strip() for value in values), f"{field} must contain non-empty strings")
            require(len(values) == len(set(values)), f"{field} must not contain duplicates")
    return years, as_of


def validate_historical_revenue(
    data: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
    parameter_index: dict[str, dict[str, Any]],
    claim_index: dict[str, dict[str, Any]],
) -> None:
    history = data["historical_revenue"]
    require(isinstance(history, list), "historical_revenue must be a list")
    pre_revenue = bool(data.get("pre_revenue", False))
    require(pre_revenue or len(history) >= 2, "historical_revenue requires at least two observations unless pre_revenue=true")
    years: set[int] = set()
    normalized: list[tuple[int, float]] = []
    for position, record in enumerate(history):
        require(isinstance(record, dict), f"historical_revenue[{position}] must be an object")
        year = record.get("year")
        require(isinstance(year, int), f"historical_revenue[{position}].year must be an integer")
        require(year <= data["base_year"], f"historical revenue year cannot exceed base_year: {year}")
        require(year not in years, f"duplicate historical revenue year: {year}")
        years.add(year)
        value = finite_number(record.get("value"), f"historical_revenue[{position}].value")
        require(value >= 0, f"historical revenue cannot be negative: {year}")
        source_ids = record.get("source_ids")
        require(isinstance(source_ids, list) and source_ids, f"historical_revenue[{position}].source_ids is required")
        for source_id in source_ids:
            require(source_id in source_index, f"unknown historical revenue source_id: {source_id}")
        claims = validate_claim_ids(
            record.get("claim_ids"), claim_index, "historical_revenue", f"historical_revenue:{year}",
            f"historical_revenue[{position}]", "exact_value",
        )
        require(any(math.isclose(float(claim.get("extracted_value")), value, rel_tol=0, abs_tol=1e-9) for claim in claims), f"historical revenue claim value mismatch: {year}")
        require(all(claim.get("period") == f"FY{year}" for claim in claims), f"historical revenue claim period mismatch: {year}")
        require(all(claim.get("unit") == f"{data['currency']} {data['unit']}" for claim in claims), f"historical revenue claim unit mismatch: {year}")
        normalized.append((year, value))
    require(normalized == sorted(normalized), "historical_revenue must be ordered by year")
    require(all(right[0] - left[0] == 1 for left, right in zip(normalized, normalized[1:])), "historical_revenue years must be consecutive")
    total = float(parameter_index[data["reported_total_revenue_parameter_id"]]["value"])
    base_records = [value for year, value in normalized if year == data["base_year"]]
    if pre_revenue and not normalized:
        require(math.isclose(total, 0.0), "pre-revenue company without history must use zero reported base revenue")
        return
    require(len(base_records) == 1, "historical_revenue must contain exactly one base_year observation")
    tolerance = max(1.0, abs(total)) * float(data.get("reconciliation_tolerance", 1e-6))
    require(abs(base_records[0] - total) <= tolerance, "historical base-year revenue does not match reported total revenue")


def validate_sources(data: dict[str, Any], as_of: date) -> dict[str, dict[str, Any]]:
    sources = data["sources"]
    require(isinstance(sources, list) and sources, "sources must be a non-empty list")
    index: dict[str, dict[str, Any]] = {}
    for position, source in enumerate(sources):
        prefix = f"sources[{position}]"
        require(isinstance(source, dict), f"{prefix} must be an object")
        source_id = source.get("source_id")
        require(isinstance(source_id, str) and source_id.strip(), f"{prefix}.source_id is required")
        require(source_id not in index, f"duplicate source_id: {source_id}")
        source_type = source.get("source_type")
        require(source_type in SOURCE_RANKS, f"unsupported source_type for {source_id}: {source_type}")
        require(valid_source_url(source.get("url")), f"invalid, search-page, or placeholder URL for {source_id}")
        for field in ("title", "publisher", "page_or_section"):
            require(isinstance(source.get(field), str) and source[field].strip(), f"{source_id}.{field} is required")
        published = parse_iso_date(source.get("published_date"), f"{source_id}.published_date")
        require(published <= as_of, f"future information leak: {source_id} was published after as_of_date")
        if source.get("accessed_date") is not None:
            parse_iso_date(source["accessed_date"], f"{source_id}.accessed_date")
        enriched = dict(source)
        enriched["source_rank"] = SOURCE_RANKS[source_type]
        index[source_id] = enriched
    return index


def validate_parameters(
    data: dict[str, Any], source_index: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    parameters = data["parameters"]
    require(isinstance(parameters, list) and parameters, "parameters must be a non-empty list")
    index: dict[str, dict[str, Any]] = {}
    semantic_groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)

    for position, parameter in enumerate(parameters):
        prefix = f"parameters[{position}]"
        require(isinstance(parameter, dict), f"{prefix} must be an object")
        parameter_id = parameter.get("parameter_id")
        require(isinstance(parameter_id, str) and parameter_id.strip(), f"{prefix}.parameter_id is required")
        require(parameter_id not in index, f"duplicate parameter_id: {parameter_id}")
        kind = parameter.get("kind")
        require(kind in PARAMETER_KINDS, f"unsupported parameter kind for {parameter_id}: {kind}")
        value = finite_number(parameter.get("value"), f"{parameter_id}.value")
        for field in ("unit", "period", "definition"):
            require(isinstance(parameter.get(field), str) and parameter[field].strip(), f"{parameter_id}.{field} is required")
        period_year(parameter["period"], f"{parameter_id}.period")
        dimension = parameter.get("dimension")
        require(dimension in PARAMETER_DIMENSIONS, f"unsupported dimension for {parameter_id}: {dimension}")
        time_basis = parameter.get("time_basis")
        require(time_basis in TIME_BASES, f"unsupported time_basis for {parameter_id}: {time_basis}")
        if dimension in MONETARY_DIMENSIONS:
            require(parameter.get("currency") == data["currency"], f"currency mismatch for {parameter_id}")
            require(parameter.get("scale") == data["unit"], f"scale mismatch for {parameter_id}")
        else:
            require(parameter.get("currency") in (None, ""), f"non-monetary parameter {parameter_id} cannot carry currency")

        source_ids = parameter.get("source_ids", [])
        require(isinstance(source_ids, list), f"{parameter_id}.source_ids must be a list")
        require(len(source_ids) == len(set(source_ids)), f"duplicate source reference in {parameter_id}")
        for source_id in source_ids:
            require(source_id in source_index, f"unknown source_id {source_id} referenced by {parameter_id}")

        if kind in {"reported_fact", "management_guidance"}:
            require(bool(source_ids), f"{kind} {parameter_id} requires at least one source")
        if kind in {"analyst_assumption", "scenario_stress"}:
            require(isinstance(parameter.get("rationale"), str) and parameter["rationale"].strip(), f"{kind} {parameter_id} requires rationale")
        if kind == "derived_fact":
            require(isinstance(parameter.get("formula"), str) and parameter["formula"].strip(), f"derived_fact {parameter_id} requires formula")
            inputs = parameter.get("input_parameter_ids")
            require(isinstance(inputs, list) and inputs, f"derived_fact {parameter_id} requires input_parameter_ids")

        normalized = dict(parameter)
        normalized["value"] = value
        index[parameter_id] = normalized
        scenario = str(parameter.get("scenario", "none"))
        key = (parameter["definition"].strip().lower(), parameter["period"], parameter["unit"], scenario)
        semantic_groups[key].append(normalized)

    for parameter_id, parameter in index.items():
        if parameter["kind"] == "derived_fact":
            for input_id in parameter["input_parameter_ids"]:
                require(input_id in index, f"unknown input_parameter_id {input_id} referenced by {parameter_id}")
                require(input_id != parameter_id, f"derived parameter {parameter_id} cannot reference itself")

    resolved: dict[str, float] = {}

    def resolve_value(parameter_id: str, stack: set[str]) -> float:
        require(parameter_id not in stack, f"derived parameter cycle detected at {parameter_id}")
        if parameter_id in resolved:
            return resolved[parameter_id]
        parameter = index[parameter_id]
        if parameter["kind"] != "derived_fact":
            resolved[parameter_id] = float(parameter["value"])
            return resolved[parameter_id]
        inputs = [resolve_value(input_id, stack | {parameter_id}) for input_id in parameter["input_parameter_ids"]]
        calculated = evaluate_derived_formula(parameter["formula"], inputs)
        tolerance = max(1.0, abs(calculated)) * float(data.get("reconciliation_tolerance", 1e-6))
        require(math.isclose(float(parameter["value"]), calculated, rel_tol=0, abs_tol=tolerance), f"derived_fact value mismatch for {parameter_id}")
        resolved[parameter_id] = calculated
        return calculated

    for parameter_id in index:
        resolve_value(parameter_id, set())

    for key, group in semantic_groups.items():
        if len(group) <= 1:
            continue
        values = {item["value"] for item in group}
        if len(values) > 1:
            ids = ", ".join(item["parameter_id"] for item in group)
            raise ForecastInputError(f"unresolved conflicting parameters for {key}: {ids}")
    return index


def validate_evidence_claims(
    data: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
    parameter_index: dict[str, dict[str, Any]],
    as_of: date,
) -> dict[str, dict[str, Any]]:
    claims = data.get("evidence_claims")
    require(isinstance(claims, list) and claims, "evidence_claims must be a non-empty list")
    index: dict[str, dict[str, Any]] = {}
    allowed_target_types = {
        "parameter", "historical_revenue", "recognition_policy", "scenario_probability",
        "management_target", "growth_driver",
    }
    allowed_support_types = {"exact_value", "rationale_support", "policy_support"}
    for position, claim in enumerate(claims):
        prefix = f"evidence_claims[{position}]"
        require(isinstance(claim, dict), f"{prefix} must be an object")
        claim_id = claim.get("claim_id")
        require(isinstance(claim_id, str) and claim_id.strip(), f"{prefix}.claim_id is required")
        require(claim_id not in index, f"duplicate claim_id: {claim_id}")
        source_id = claim.get("source_id")
        require(source_id in source_index, f"unknown claim source_id: {source_id}")
        target_type = claim.get("target_type")
        support_type = claim.get("support_type")
        require(target_type in allowed_target_types, f"unsupported claim target_type for {claim_id}: {target_type}")
        require(support_type in allowed_support_types, f"unsupported claim support_type for {claim_id}: {support_type}")
        target_id = claim.get("target_id")
        require(isinstance(target_id, str) and target_id.strip(), f"{claim_id}.target_id is required")
        for field in ("locator", "excerpt", "verified_by"):
            require(isinstance(claim.get(field), str) and claim[field].strip(), f"{claim_id}.{field} is required")
        excerpt = claim["excerpt"].strip()
        require(10 <= len(excerpt) <= 500, f"{claim_id}.excerpt must contain 10-500 characters")
        require(claim.get("excerpt_sha256") == text_sha256(excerpt), f"claim excerpt hash mismatch: {claim_id}")
        require(isinstance(claim.get("content_sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", claim["content_sha256"]), f"{claim_id}.content_sha256 must be lowercase SHA-256")
        require(claim.get("verification_status") == "opened_and_checked", f"claim {claim_id} must be opened_and_checked")
        verified_date = parse_iso_date(claim.get("verified_date"), f"{claim_id}.verified_date")
        published_date = parse_iso_date(source_index[source_id]["published_date"], f"{source_id}.published_date")
        require(published_date <= verified_date <= as_of, f"claim verification date is outside the allowed information set: {claim_id}")

        if target_type == "parameter":
            require(target_id in parameter_index, f"unknown claim parameter target: {target_id}")
            parameter = parameter_index[target_id]
            require(source_id in parameter.get("source_ids", []), f"claim source {source_id} is not registered on parameter {target_id}")
            if support_type == "exact_value":
                extracted = finite_number(claim.get("extracted_value"), f"{claim_id}.extracted_value")
                require(math.isclose(extracted, float(parameter["value"]), rel_tol=0, abs_tol=1e-9), f"claim value mismatch for parameter {target_id}")
                require(claim.get("unit") == parameter["unit"], f"claim unit mismatch for parameter {target_id}")
                require(claim.get("period") == parameter["period"], f"claim period mismatch for parameter {target_id}")
        index[claim_id] = dict(claim)

    for parameter_id, parameter in parameter_index.items():
        claim_ids = parameter.get("claim_ids", [])
        require(isinstance(claim_ids, list), f"{parameter_id}.claim_ids must be a list")
        require(len(claim_ids) == len(set(claim_ids)), f"duplicate claim reference in {parameter_id}")
        linked: list[dict[str, Any]] = []
        for claim_id in claim_ids:
            require(claim_id in index, f"unknown claim_id {claim_id} referenced by {parameter_id}")
            claim = index[claim_id]
            require(claim["target_type"] == "parameter" and claim["target_id"] == parameter_id, f"claim {claim_id} does not support parameter {parameter_id}")
            linked.append(claim)
        if parameter["kind"] in {"reported_fact", "management_guidance"}:
            require(any(claim["support_type"] == "exact_value" for claim in linked), f"{parameter['kind']} {parameter_id} requires an exact-value claim")
        if parameter["kind"] in {"analyst_assumption", "scenario_stress"} and parameter.get("source_ids"):
            require(bool(linked), f"source-linked assumption {parameter_id} requires a rationale-support claim")
    return index


def validate_claim_ids(
    claim_ids: Any,
    claim_index: dict[str, dict[str, Any]],
    target_type: str,
    target_id: str,
    field: str,
    support_type: str | None = None,
) -> list[dict[str, Any]]:
    require(isinstance(claim_ids, list) and claim_ids, f"{field} requires claim_ids")
    require(len(claim_ids) == len(set(claim_ids)), f"{field} contains duplicate claim_ids")
    claims: list[dict[str, Any]] = []
    for claim_id in claim_ids:
        require(claim_id in claim_index, f"unknown claim_id {claim_id} in {field}")
        claim = claim_index[claim_id]
        require(claim["target_type"] == target_type and claim["target_id"] == target_id, f"claim {claim_id} does not support {target_type}:{target_id}")
        if support_type is not None:
            require(claim["support_type"] == support_type, f"claim {claim_id} must use {support_type}")
        claims.append(claim)
    return claims


def parameter_values(parameter_index: dict[str, dict[str, Any]], parameter_ids: Iterable[str]) -> list[float]:
    values: list[float] = []
    for parameter_id in parameter_ids:
        require(parameter_id in parameter_index, f"unknown parameter_id: {parameter_id}")
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
    require(isinstance(parameter_ids, list), f"driver {driver} must be a list of parameter_ids")
    require(len(parameter_ids) == len(years), f"driver {driver} must contain one parameter_id per forecast year")
    values: list[float] = []
    for year, parameter_id in zip(years, parameter_ids):
        require(parameter_id in parameter_index, f"unknown parameter_id {parameter_id} for driver {driver}")
        parameter = parameter_index[parameter_id]
        parameter_scenario = parameter.get("scenario")
        require(parameter_scenario in (None, "all", scenario), f"scenario mismatch: {parameter_id} cannot be used in {scenario}")
        require(period_year(parameter["period"], f"{parameter_id}.period") == year, f"period mismatch: {parameter_id} does not map to {year}")
        expected_dimension = MODEL_DRIVER_DIMENSIONS[model][driver]
        require(parameter["dimension"] == expected_dimension, f"dimension mismatch: {parameter_id} must be {expected_dimension} for {model}.{driver}")
        value = float(parameter["value"])
        if parameter["dimension"] == "ratio" and driver != "growth_rate":
            require(0 <= value <= 1, f"ratio driver {driver} must be between 0 and 1: {parameter_id}")
        elif driver not in {"growth_rate", "contract_changes", "other_revenue", "fixed_revenue", "ancillary_revenue", "milestone_revenue", "royalty_revenue", "service_revenue", "performance_fee_revenue", "fee_revenue"}:
            require(value >= 0, f"driver {driver} cannot be negative: {parameter_id}")
        if driver == "growth_rate":
            require(value > -1, f"growth_rate must be greater than -1: {parameter_id}")
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
    return resolve_driver_series(parameter_index, driver_ids[driver], years, driver, scenario, model)


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
    require(isinstance(driver_ids, dict), f"driver_parameter_ids must be an object for {model}")
    spec = MODEL_SPECS[model]
    allowed = set(spec["required"]) | set(spec["optional"])
    missing = [driver for driver in spec["required"] if driver not in driver_ids]
    require(not missing, f"missing drivers for {model}: {', '.join(missing)}")
    extra = sorted(set(driver_ids) - allowed)
    require(not extra, f"unsupported drivers for {model}: {', '.join(extra)}")
    if model == "retail_franchise":
        pair = {"franchise_system_sales", "recognized_fee_rate"}
        require(not (set(driver_ids) & pair) or pair <= set(driver_ids), "retail_franchise requires franchise_system_sales and recognized_fee_rate together")

    drivers: dict[str, list[float]] = {}
    for driver in spec["required"]:
        drivers[driver] = resolve_driver_series(parameter_index, driver_ids[driver], years, driver, scenario, model)
    for driver in spec["optional"]:
        drivers[driver] = _optional_series(driver_ids, driver, parameter_index, years, scenario, model, float(spec.get("defaults", {}).get(driver, 0.0)))

    try:
        revenue = calculate_registered_model(model, base_revenue, drivers, years)
    except ModelRegistryError as exc:
        raise ForecastInputError(str(exc)) from exc
    for year, value in zip(years, revenue):
        require(value >= 0 and math.isfinite(value), f"calculated revenue must be finite and non-negative for {model}/{year}")

    return {
        "model": model,
        "formula": spec["formula"],
        "annual_revenue": dict(zip(map(str, years), revenue)),
        "driver_values": {name: dict(zip(map(str, years), values)) for name, values in drivers.items()},
        "driver_parameter_ids": copy.deepcopy(driver_ids),
    }


def calculate_segment_forecasts(data: dict[str, Any], validated: dict[str, Any]) -> list[dict[str, Any]]:
    years = validated["years"]
    parameter_index = validated["parameter_index"]
    results: list[dict[str, Any]] = []
    for segment in data["segments"]:
        name = segment["name"]
        base = float(parameter_index[segment["base_revenue_parameter_id"]]["value"])
        scenarios = segment.get("scenarios")
        require(isinstance(scenarios, dict) and set(scenarios) == set(SCENARIOS), f"{name} must contain low/base/high scenarios")
        models = {scenarios[scenario].get("model") for scenario in SCENARIOS}
        require(len(models) == 1, f"{name} must use the same model across scenarios")
        model = next(iter(models))
        opening_checks = {
            "project_backlog": ("base_backlog_parameter_id", "opening_backlog", "backlog"),
            "delivery_pipeline": ("base_orders_parameter_id", "opening_orders", "quantity"),
        }
        if model in opening_checks:
            base_field, opening_driver, expected_dimension = opening_checks[model]
            opening_base_id = segment.get(base_field)
            require(opening_base_id in parameter_index, f"{name}/{model} requires valid {base_field}")
            opening_base = parameter_index[opening_base_id]
            require(opening_base["dimension"] == expected_dimension, f"{name}/{base_field} has wrong dimension")
            require(period_year(opening_base["period"], f"{opening_base_id}.period") == data["base_year"], f"{name}/{base_field} must use base year")
            for scenario in SCENARIOS:
                opening_ids = scenarios[scenario].get("driver_parameter_ids", {}).get(opening_driver, [])
                require(bool(opening_ids), f"{name}/{scenario} requires {opening_driver}")
                require(math.isclose(float(parameter_index[opening_ids[0]]["value"]), float(opening_base["value"]), rel_tol=1e-9, abs_tol=1e-9), f"{name}/{scenario} first opening does not reconcile to {base_field}")
        scenario_results: dict[str, Any] = {}
        for scenario in SCENARIOS:
            scenario_input = scenarios[scenario]
            require(isinstance(scenario_input.get("rationale"), str) and scenario_input["rationale"].strip(), f"{name}/{scenario} requires rationale")
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
        results.append({
            "name": name,
            "base_revenue": base,
            "base_revenue_parameter_id": segment["base_revenue_parameter_id"],
            "scenarios": scenario_results,
        })
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
    require(mode in RECOGNITION_MODES, f"unsupported recognition mode for {name}: {mode}")
    require(timing in RECOGNITION_TIMING, f"unsupported recognition timing for {name}: {timing}")
    require(presentation in PRESENTATIONS, f"unsupported presentation for {name}: {presentation}")
    require(recognition.get("modeled_presentation") == presentation, f"{name} modeled_presentation must match accounting presentation")
    require(isinstance(recognition.get("trigger"), str) and recognition["trigger"].strip(), f"{name} requires a revenue-recognition trigger")
    if timing == "over_time":
        require(isinstance(recognition.get("progress_measure"), str) and recognition["progress_measure"].strip(), f"{name} over-time recognition requires progress_measure")
        require(mode != "lagged_activity", f"{name} cannot combine over_time with lagged_activity")
        progress = recognition.get("progress_parameter_ids")
        require(isinstance(progress, dict) and set(progress) == set(SCENARIOS), f"{name} over-time recognition requires low/base/high progress_parameter_ids")
    basis_claims = validate_claim_ids(recognition.get("basis_claim_ids"), claim_index, "recognition_policy", f"recognition:{name}", f"{name}.recognition", "policy_support")
    basis_source_ids = sorted({claim["source_id"] for claim in basis_claims})
    require(bool(basis_source_ids), f"{name} recognition requires policy evidence")
    recognition = dict(recognition)
    recognition["basis_source_ids"] = basis_source_ids
    if mode == "lagged_activity":
        lag_years = recognition.get("lag_years")
        require(isinstance(lag_years, int) and lag_years > 0, f"{name} lagged_activity requires positive integer lag_years")
        carry_in = recognition.get("carry_in_parameter_ids")
        require(isinstance(carry_in, dict) and set(carry_in) == set(SCENARIOS), f"{name} lagged_activity requires low/base/high carry_in_parameter_ids")
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
                require(isinstance(progress_ids, list) and len(progress_ids) == len(years), f"{result['name']}/{scenario} progress_parameter_ids must contain one parameter per year")
                for year, parameter_id in zip(years, progress_ids):
                    require(parameter_id in parameter_index, f"unknown progress parameter_id: {parameter_id}")
                    parameter = parameter_index[parameter_id]
                    require(parameter["dimension"] == "ratio", f"progress parameter must use ratio dimension: {parameter_id}")
                    require(period_year(parameter["period"], f"{parameter_id}.period") == year, f"progress period mismatch: {parameter_id}")
                    require(parameter.get("scenario") in (None, "all", scenario), f"progress scenario mismatch: {parameter_id}")
                    progress_values.append(float(parameter["value"]))
                require(all(0 <= value <= 1 for value in progress_values), f"{result['name']}/{scenario} progress must be between 0 and 1")
                recognized = [value * progress for value, progress in zip(modeled, progress_values)]
                tail = [value - recognized_value for value, recognized_value in zip(modeled, recognized)]
                carry_in_values = []
            elif recognition["mode"] == "modeled_as_recognized":
                recognized = modeled
                tail: list[float] = []
                carry_in_values: list[float] = []
            else:
                lag = recognition["lag_years"]
                require(lag <= len(years), f"{result['name']} lag_years exceeds forecast horizon")
                carry_ids = recognition["carry_in_parameter_ids"][scenario]
                require(isinstance(carry_ids, list) and len(carry_ids) == lag, f"{result['name']}/{scenario} carry-in count must equal lag_years")
                carry_in_values = parameter_values(parameter_index, carry_ids)
                for offset, parameter_id in enumerate(carry_ids):
                    parameter = parameter_index[parameter_id]
                    require(period_year(parameter["period"], f"{parameter_id}.period") == years[offset], f"carry-in period mismatch: {parameter_id}")
                    require(parameter["dimension"] == "revenue", f"carry-in must use revenue dimension: {parameter_id}")
                    require(parameter.get("scenario") in (None, "all", scenario), f"carry-in scenario mismatch: {parameter_id}")
                    require(parameter["value"] >= 0, f"carry-in revenue cannot be negative: {parameter_id}")
                recognized = carry_in_values + modeled[:-lag]
                tail = modeled[-lag:]
            scenario_output = dict(result["scenarios"][scenario])
            scenario_output["modeled_activity"] = scenario_output.pop("annual_revenue")
            scenario_output["recognized_revenue"] = dict(zip(map(str, years), recognized))
            scenario_output["carry_in_revenue"] = carry_in_values
            scenario_output["unrecognized_tail_activity"] = tail
            scenario_output["progress_values"] = dict(zip(map(str, years), progress_values)) if progress_values else None
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
        require(isinstance(adjustment, dict), "every forecast adjustment must be an object")
        name = adjustment.get("name")
        category = adjustment.get("category")
        require(isinstance(name, str) and name.strip(), "forecast adjustment name is required")
        require(name not in names, f"duplicate forecast adjustment name: {name}")
        names.add(name)
        require(category in ADJUSTMENT_CATEGORIES, f"unsupported forecast adjustment category: {category}")
        scenario_ids = adjustment.get("scenario_parameter_ids")
        require(isinstance(scenario_ids, dict) and set(scenario_ids) == set(SCENARIOS), f"{name} must contain low/base/high parameter IDs")
        for scenario in SCENARIOS:
            ids = scenario_ids[scenario]
            require(isinstance(ids, list) and len(ids) == len(years), f"{name}/{scenario} must contain one parameter ID per year")
            values: list[float] = []
            for year, parameter_id in zip(years, ids):
                require(parameter_id in parameter_index, f"unknown adjustment parameter_id: {parameter_id}")
                parameter = parameter_index[parameter_id]
                require(period_year(parameter["period"], f"{parameter_id}.period") == year, f"adjustment period mismatch: {parameter_id}")
                require(parameter["dimension"] == "revenue", f"adjustment must use revenue dimension: {parameter_id}")
                require(parameter.get("scenario") in (None, "all", scenario), f"adjustment scenario mismatch: {parameter_id}")
                values.append(float(parameter["value"]))
            if category in {"intersegment_elimination", "disposal_contribution"}:
                require(all(value <= 0 for value in values), f"{category} must use non-positive signed values: {name}/{scenario}")
            if category == "acquisition_contribution":
                require(all(value >= 0 for value in values), f"acquisition_contribution must use non-negative values: {name}/{scenario}")
            result[scenario].append({
                "name": name,
                "category": category,
                "annual_adjustment": dict(zip(map(str, years), values)),
                "parameter_ids": ids,
            })
    return result


def calculate_cagr(base: float, terminal: float, years: int) -> float | None:
    if base <= 0 or terminal < 0 or years <= 0:
        return None
    return (terminal / base) ** (1 / years) - 1


def calculate_company_forecast(
    data: dict[str, Any],
    validated: dict[str, Any],
    recognized_segments: list[dict[str, Any]],
) -> dict[str, Any]:
    years = validated["years"]
    parameter_index = validated["parameter_index"]
    reported_base = float(parameter_index[data["reported_total_revenue_parameter_id"]]["value"])
    adjustments = resolve_adjustments(data, validated)
    consolidated: dict[str, Any] = {}
    for scenario in SCENARIOS:
        segment_totals = [0.0] * len(years)
        segment_bridge: list[dict[str, Any]] = []
        for segment in recognized_segments:
            scenario_output = segment["scenarios"][scenario]
            values = list(scenario_output.get("effective_revenue", scenario_output["recognized_revenue"]).values())
            segment_totals = [left + right for left, right in zip(segment_totals, values)]
            segment_bridge.append({"name": segment["name"], "annual_revenue": dict(zip(map(str, years), values))})
        adjustment_totals = [0.0] * len(years)
        for adjustment in adjustments[scenario]:
            values = list(adjustment["annual_adjustment"].values())
            adjustment_totals = [left + right for left, right in zip(adjustment_totals, values)]
        company_values = [segment + adjustment for segment, adjustment in zip(segment_totals, adjustment_totals)]
        require(all(value >= 0 and math.isfinite(value) for value in company_values), f"company revenue must be finite and non-negative in {scenario}")
        annual_growth: dict[str, float | None] = {}
        previous = reported_base
        for year, value in zip(years, company_values):
            annual_growth[str(year)] = None if previous == 0 else value / previous - 1
            previous = value
        base_adjustment_total = sum(parameter_values(parameter_index, data.get("base_adjustment_parameter_ids", [])))
        segment_contributions = [
            {
                "name": segment["name"],
                "terminal_incremental_revenue": list(
                    segment["scenarios"][scenario].get(
                        "effective_revenue", segment["scenarios"][scenario]["recognized_revenue"]
                    ).values()
                )[-1] - segment["base_revenue"],
            }
            for segment in recognized_segments
        ]
        adjustment_increment = adjustment_totals[-1] - base_adjustment_total
        contribution_sum = sum(item["terminal_incremental_revenue"] for item in segment_contributions) + adjustment_increment
        company_increment = company_values[-1] - reported_base
        require(math.isclose(contribution_sum, company_increment, rel_tol=1e-9, abs_tol=1e-9), f"incremental revenue attribution does not reconcile in {scenario}")
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


def validate_scenario_probabilities(data: dict[str, Any], validated: dict[str, Any]) -> dict[str, float] | None:
    probabilities = data.get("scenario_probabilities")
    if probabilities is None:
        return None
    require(isinstance(probabilities, dict) and set(probabilities) == set(SCENARIOS), "scenario_probabilities must contain low/base/high")
    normalized: dict[str, float] = {}
    for scenario in SCENARIOS:
        value = finite_number(probabilities[scenario], f"scenario_probabilities.{scenario}")
        require(value >= 0, "scenario probabilities must be non-negative")
        normalized[scenario] = value
    require(math.isclose(sum(normalized.values()), 1.0, rel_tol=0, abs_tol=1e-9), "scenario probabilities must sum to 1")
    require(isinstance(data.get("probability_rationale"), str) and data["probability_rationale"].strip(), "scenario probabilities require probability_rationale")
    claims = validate_claim_ids(data.get("probability_claim_ids"), validated["claim_index"], "scenario_probability", "scenario_probability", "scenario probabilities", "rationale_support")
    data["probability_source_ids"] = sorted({claim["source_id"] for claim in claims})
    return normalized


def add_scenario_analysis(data: dict[str, Any], validated: dict[str, Any], result: dict[str, Any]) -> None:
    years = validated["years"]
    consolidated = result["consolidated_forecast"]
    for segment in result["segments"]:
        for year in map(str, years):
            low = segment["scenarios"]["low"].get("effective_revenue", segment["scenarios"]["low"]["recognized_revenue"])[year]
            base = segment["scenarios"]["base"].get("effective_revenue", segment["scenarios"]["base"]["recognized_revenue"])[year]
            high = segment["scenarios"]["high"].get("effective_revenue", segment["scenarios"]["high"]["recognized_revenue"])[year]
            require(low <= base <= high, f"segment scenario ordering failed for {segment['name']}/{year}")
    for year in map(str, years):
        low = consolidated["low"]["annual_revenue"][year]
        base = consolidated["base"]["annual_revenue"][year]
        high = consolidated["high"]["annual_revenue"][year]
        require(low <= base <= high, f"scenario ordering failed in {year}: low <= base <= high is required")
    probabilities = validate_scenario_probabilities(data, validated)
    result["scenario_probabilities"] = probabilities
    result["probability_weighted_forecast"] = None
    if probabilities is None:
        return
    values = [
        sum(probabilities[scenario] * consolidated[scenario]["annual_revenue"][str(year)] for scenario in SCENARIOS)
        for year in years
    ]
    result["probability_weighted_forecast"] = {
        "annual_revenue": dict(zip(map(str, years), values)),
        "terminal_revenue": values[-1],
        "expected_terminal_implied_cagr": calculate_cagr(result["base_revenue"], values[-1], len(years)),
        "incremental_revenue": values[-1] - result["base_revenue"],
        "probability_rationale": data["probability_rationale"],
        "probability_source_ids": data["probability_source_ids"],
    }


def referenced_parameter_ids(data: dict[str, Any], scenario: str) -> set[str]:
    referenced: set[str] = set()
    for segment in data["segments"]:
        scenario_input = segment["scenarios"][scenario]
        for ids in scenario_input["driver_parameter_ids"].values():
            referenced.update(ids)
        recognition = segment["recognition"]
        if recognition.get("mode") == "lagged_activity":
            referenced.update(recognition["carry_in_parameter_ids"][scenario])
    for adjustment in data.get("forecast_adjustments", []):
        referenced.update(adjustment["scenario_parameter_ids"][scenario])
    return referenced


def parameter_driver_roles(data: dict[str, Any], scenario: str) -> dict[str, set[tuple[str, str]]]:
    roles: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for segment in data["segments"]:
        scenario_input = segment["scenarios"][scenario]
        model = scenario_input["model"]
        for driver, ids in scenario_input["driver_parameter_ids"].items():
            for parameter_id in ids:
                roles[parameter_id].add((model, driver))
    return roles


def _sensitivity_bounds(parameter: dict[str, Any], roles: set[tuple[str, str]]) -> tuple[float, float]:
    if any(driver == "growth_rate" for _, driver in roles):
        return (-0.999999999, math.inf)
    if parameter["dimension"] == "ratio":
        return (0.0, 1.0)
    if parameter["dimension"] in {"quantity", "activity", "monetary_balance", "area", "backlog", "coverage_units", "revenue_per_unit", "revenue_per_activity", "revenue_per_area"}:
        return (0.0, math.inf)
    if parameter["dimension"] == "revenue" and roles:
        return (0.0, math.inf)
    return (-math.inf, math.inf)


def _requested_sensitivity_values(test: dict[str, Any], original: float, name: str, dimension: str) -> tuple[float, float, float | None]:
    shock_type = test.get("shock_type")
    require(shock_type in {"percent", "percentage_point", "basis_point", "absolute", "range", "discrete"}, f"unsupported sensitivity shock_type for {name}: {shock_type}")
    if shock_type in {"range", "discrete"}:
        down = finite_number(test.get("down_value"), f"{name}.down_value")
        up = finite_number(test.get("up_value"), f"{name}.up_value")
        require(down <= up, f"{name} requires down_value <= up_value")
        return down, up, None
    shock = finite_number(test.get("shock_value"), f"{name}.shock_value")
    require(shock > 0, f"{name}.shock_value must be positive")
    if shock_type == "percent":
        require(original != 0, f"percent sensitivity cannot be applied to zero parameter: {test.get('parameter_id')}")
        return original * (1 - shock), original * (1 + shock), shock
    if shock_type == "percentage_point":
        require(dimension == "ratio", f"percentage_point sensitivity requires ratio dimension: {test.get('parameter_id')}")
        return original - shock, original + shock, shock
    if shock_type == "basis_point":
        require(dimension == "ratio", f"basis_point sensitivity requires ratio dimension: {test.get('parameter_id')}")
        delta = shock / 10000
        return original - delta, original + delta, shock
    return original - shock, original + shock, shock


def calculate_sensitivities(data: dict[str, Any], result: dict[str, Any]) -> list[dict[str, Any]]:
    tests = data.get("sensitivity_tests", [])
    require(isinstance(tests, list), "sensitivity_tests must be a list")
    if not tests:
        return []
    base_refs = referenced_parameter_ids(data, "base")
    baseline_terminal = result["consolidated_forecast"]["base"]["terminal_revenue"]
    parameter_positions = {parameter["parameter_id"]: index for index, parameter in enumerate(data["parameters"])}
    outputs: list[dict[str, Any]] = []
    names: set[str] = set()
    tested_parameters: set[str] = set()
    roles = parameter_driver_roles(data, "base")
    for test in tests:
        require(isinstance(test, dict), "every sensitivity test must be an object")
        name = test.get("name")
        parameter_id = test.get("parameter_id")
        require(isinstance(name, str) and name.strip(), "sensitivity test name is required")
        require(name not in names, f"duplicate sensitivity test name: {name}")
        names.add(name)
        require(parameter_id not in tested_parameters, f"duplicate sensitivity parameter_id: {parameter_id}")
        tested_parameters.add(parameter_id)
        require(parameter_id in base_refs, f"sensitivity parameter is not referenced by the base scenario: {parameter_id}")
        require(parameter_id in parameter_positions, f"unknown sensitivity parameter_id: {parameter_id}")
        parameter = data["parameters"][parameter_positions[parameter_id]]
        require(parameter["kind"] in {"analyst_assumption", "scenario_stress"}, f"sensitivity parameter must be an assumption or stress: {parameter_id}")
        original = float(parameter["value"])
        requested_down, requested_up, shock = _requested_sensitivity_values(test, original, name, parameter["dimension"])
        lower, upper = _sensitivity_bounds(parameter, roles.get(parameter_id, set()))
        effective_down = min(max(requested_down, lower), upper)
        effective_up = min(max(requested_up, lower), upper)
        terminals: dict[str, float] = {}
        for direction, shocked_value in (("down", effective_down), ("up", effective_up)):
            shocked = copy.deepcopy(data)
            shocked["parameters"][parameter_positions[parameter_id]]["value"] = shocked_value
            shocked.pop("sensitivity_tests", None)
            shocked_result = _run_forecast_core(shocked)
            terminals[direction] = shocked_result["consolidated_forecast"]["base"]["terminal_revenue"]
        impact = max(abs(terminals["down"] - baseline_terminal), abs(terminals["up"] - baseline_terminal))
        outputs.append({
            "name": name,
            "parameter_id": parameter_id,
            "shock_type": test["shock_type"],
            "shock_value": shock,
            "requested_values": {"down": requested_down, "up": requested_up},
            "effective_values": {"down": effective_down, "up": effective_up},
            "clamped": {"down": not math.isclose(requested_down, effective_down), "up": not math.isclose(requested_up, effective_up)},
            "baseline_terminal_revenue": baseline_terminal,
            "down_terminal_revenue": terminals["down"],
            "up_terminal_revenue": terminals["up"],
            "max_absolute_terminal_impact": impact,
            "max_relative_terminal_impact": None if baseline_terminal == 0 else impact / baseline_terminal,
        })
    return outputs


def calculate_theme_analysis(data: dict[str, Any], validated: dict[str, Any], result: dict[str, Any]) -> dict[str, Any] | None:
    theme = data.get("theme_analysis")
    if theme is None:
        return None
    require(isinstance(theme, dict), "theme_analysis must be an object")
    require(isinstance(theme.get("name"), str) and theme["name"].strip(), "theme_analysis.name is required")
    segment_names = theme.get("segment_names")
    require(isinstance(segment_names, list) and segment_names, "theme_analysis.segment_names is required")
    available = {segment["name"] for segment in result["segments"]}
    require(set(segment_names) <= available, "theme_analysis contains an unknown segment")
    counterfactual_ids = theme.get("counterfactual_terminal_parameter_ids")
    require(isinstance(counterfactual_ids, dict) and set(counterfactual_ids) == set(SCENARIOS), "theme counterfactual requires low/base/high parameter IDs")
    output = {"name": theme["name"], "segment_names": segment_names, "scenarios": {}}
    parameter_index = validated["parameter_index"]
    for scenario in SCENARIOS:
        parameter_id = counterfactual_ids[scenario]
        require(parameter_id in parameter_index, f"unknown theme counterfactual parameter_id: {parameter_id}")
        parameter = parameter_index[parameter_id]
        require(parameter.get("scenario") in (None, "all", scenario), f"theme counterfactual scenario mismatch: {parameter_id}")
        require(parameter["kind"] in {"analyst_assumption", "scenario_stress"}, f"theme counterfactual must be an explicit assumption: {parameter_id}")
        require(parameter["dimension"] == "revenue", f"theme counterfactual must use revenue dimension: {parameter_id}")
        require(period_year(parameter["period"], f"{parameter_id}.period") == validated["years"][-1], f"theme counterfactual must use terminal forecast year: {parameter_id}")
        require(float(parameter["value"]) >= 0, f"theme counterfactual cannot be negative: {parameter_id}")
        theme_revenue = sum(
            list(segment["scenarios"][scenario].get(
                "effective_revenue", segment["scenarios"][scenario]["recognized_revenue"]
            ).values())[-1]
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
            "theme_elasticity_to_company_base": None if result["base_revenue"] == 0 else increment / result["base_revenue"],
            "theme_share_of_company_terminal": None if company_terminal == 0 else theme_revenue / company_terminal,
            "counterfactual_parameter_id": parameter_id,
        }
    return output


def validate_historical_accuracy_records(data: dict[str, Any]) -> tuple[float | None, int]:
    records = data.get("historical_accuracy_records", [])
    require(isinstance(records, list), "historical_accuracy_records must be a list")
    weighted_error = 0.0
    observations = 0
    ids: set[str] = set()
    for record in records:
        require(isinstance(record, dict), "historical accuracy record must be an object")
        require(record.get("record_schema_version") == "1.0", "unsupported historical accuracy record schema")
        backtest_id = record.get("backtest_id")
        require(isinstance(backtest_id, str) and backtest_id and backtest_id not in ids, "historical accuracy backtest_id must be unique")
        ids.add(backtest_id)
        provided_hash = record.get("record_sha256")
        payload = {key: value for key, value in record.items() if key != "record_sha256"}
        require(provided_hash == canonical_sha256(payload), f"historical accuracy record hash mismatch: {backtest_id}")
        count = record.get("observations")
        require(isinstance(count, int) and count > 0, f"historical accuracy observations must be positive: {backtest_id}")
        wape = record.get("wape")
        if wape is not None:
            value = finite_number(wape, f"historical accuracy WAPE {backtest_id}")
            require(value >= 0, f"historical accuracy WAPE cannot be negative: {backtest_id}")
            weighted_error += value * count
            observations += count
    return (None if observations == 0 else weighted_error / observations, observations)


def parameter_revenue_weights(data: dict[str, Any], result: dict[str, Any]) -> dict[str, float]:
    weights: dict[str, float] = defaultdict(float)
    segment_inputs = {segment["name"]: segment for segment in data["segments"]}
    for segment_result in result["segments"]:
        segment = segment_inputs[segment_result["name"]]
        base_output = segment_result["scenarios"]["base"]
        terminal = abs(float(list(base_output.get("effective_revenue", base_output["recognized_revenue"]).values())[-1]))
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
    for adjustment, bridge in zip(data.get("forecast_adjustments", []), result["consolidated_forecast"]["base"]["adjustment_bridge"]):
        refs = adjustment["scenario_parameter_ids"]["base"]
        impact = abs(float(list(bridge["annual_adjustment"].values())[-1]))
        if refs:
            for parameter_id in refs:
                weights[parameter_id] += impact / len(refs)
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
    covered_weight = sum(weight for parameter_id, weight in weights.items() if parameters[parameter_id].get("claim_ids"))
    driver_coverage = 0 if total_weight == 0 else covered_weight / total_weight
    quality_numerator = 0.0
    freshness_numerator = 0.0
    as_of = validated["as_of_date"]
    for parameter_id, weight in weights.items():
        claim_ids = parameters[parameter_id].get("claim_ids", [])
        if not claim_ids:
            continue
        parameter_claims = [claims[claim_id] for claim_id in claim_ids]
        quality = sum(1.0 if claim["support_type"] == "exact_value" else 0.8 if claim["support_type"] == "policy_support" else 0.7 for claim in parameter_claims) / len(parameter_claims)
        ages = [(as_of - parse_iso_date(validated["source_index"][claim["source_id"]]["published_date"], "published_date")).days for claim in parameter_claims]
        freshness = sum(1.0 if age <= 180 else 0.8 if age <= 365 else 0.5 if age <= 730 else 0.2 for age in ages) / len(ages)
        quality_numerator += weight * quality
        freshness_numerator += weight * freshness
    source_quality = 0 if covered_weight == 0 else quality_numerator / covered_weight
    freshness = 0 if covered_weight == 0 else freshness_numerator / covered_weight

    segment_total = sum(abs(float(list(segment["scenarios"]["base"].get(
        "effective_revenue", segment["scenarios"]["base"]["recognized_revenue"]
    ).values())[-1])) for segment in result["segments"])
    explicit_total = sum(
        abs(float(list(segment["scenarios"]["base"].get(
            "effective_revenue", segment["scenarios"]["base"]["recognized_revenue"]
        ).values())[-1]))
        for segment in result["segments"]
        if segment["scenarios"]["base"]["model"] not in {"direct_growth", "direct_revenue"}
    )
    explicit_model_share = 0 if segment_total == 0 else explicit_total / segment_total

    historical_wape, historical_observations = validate_historical_accuracy_records(data)
    history_score = 0.0 if historical_wape is None else 15 if historical_wape <= 0.05 else 12 if historical_wape <= 0.10 else 8 if historical_wape <= 0.20 else 4 if historical_wape <= 0.30 else 0

    sensitivity_coverage = 0.0
    concentration = None
    if sensitivities:
        impacts = [item["max_absolute_terminal_impact"] for item in sensitivities]
        total_impact = sum(impacts)
        concentration = 0 if total_impact == 0 else max(impacts) / total_impact
        tested = {item["parameter_id"] for item in sensitivities}
        sensitivity_coverage = 0 if total_weight == 0 else sum(weight for parameter_id, weight in weights.items() if parameter_id in tested) / total_weight

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
            (covered_weight == 0, "No verified claims for revenue-weighted base drivers"),
            (historical_wape is None, "No immutable historical backtest record"),
            (not sensitivities, "No deterministic sensitivity tests"),
            (explicit_model_share < 1, "One or more segments use a direct fallback model"),
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
        float(growth_analysis.get("unattributed_company_adjustments", 0)), 0.0,
        rel_tol=0, abs_tol=1e-9,
    ):
        limitations.append("Company-level forecast adjustments are disclosed separately from operating growth-driver ranking")
    return {
        "score": score,
        "rating": rating,
        "components": components,
        "driver_evidence_coverage": driver_coverage,
        "sensitivity_concentration": concentration,
        "historical_accuracy": {"wape": historical_wape, "observations": historical_observations},
        "quality_gates": quality_gates,
        "limitations": limitations,
    }


def run_forecast(data: dict[str, Any]) -> dict[str, Any]:
    """Run the complete revenue forecast without any investment outputs."""
    validated = validate_document(data)
    result = _run_forecast_core(data)
    result["schema_version"] = data["schema_version"]
    result["engine_version"] = ENGINE_VERSION
    result["input_sha256"] = canonical_sha256(data)
    result["research_coverage"] = {
        "dimensions": validated["research_coverage"]["records"],
        "counts": validated["research_coverage"]["counts"],
    }
    result["management_target_coverage"] = add_management_target_analysis(validated, result)
    add_scenario_analysis(data, validated, result)
    result["growth_driver_analysis"] = calculate_growth_driver_analysis(validated, result)
    sensitivities = calculate_sensitivities(data, result)
    result["sensitivities"] = sensitivities
    result["theme_analysis"] = calculate_theme_analysis(data, validated, result)
    result["confidence"] = calculate_confidence(data, validated, result, sensitivities)
    result["forecast_version"] = data.get("forecast_version", f"{data['as_of_date']}-v1")
    result["data_gaps"] = list(dict.fromkeys([
        *data.get("data_gaps", []),
        *validated["research_coverage"]["gap_messages"],
        *validated["growth_driver_tree"]["gap_messages"],
        *validated["management_target_coverage"]["gap_messages"],
    ]))
    result["disconfirming_indicators"] = list(data.get("disconfirming_indicators", []))
    result["parameter_trace"] = data["parameters"]
    result["sources"] = list(validated["source_index"].values())
    result["evidence_claims"] = list(validated["claim_index"].values())
    result["historical_accuracy_records"] = copy.deepcopy(data.get("historical_accuracy_records", []))
    result["result_sha256"] = canonical_sha256(result)
    return result


def validate_base_reconciliation(data: dict[str, Any], parameter_index: dict[str, dict[str, Any]]) -> None:
    total_id = data["reported_total_revenue_parameter_id"]
    require(total_id in parameter_index, f"unknown reported_total_revenue_parameter_id: {total_id}")
    total_parameter = parameter_index[total_id]
    require(total_parameter["kind"] in {"reported_fact", "derived_fact"}, "reported total revenue must be a fact")
    require(total_parameter["dimension"] == "revenue", "reported total revenue must use revenue dimension")
    require(period_year(total_parameter["period"], f"{total_id}.period") == data["base_year"], "reported total revenue must use base year")
    total = float(total_parameter["value"])

    segments = data["segments"]
    require(isinstance(segments, list) and segments, "segments must be a non-empty list")
    names: set[str] = set()
    segment_total = 0.0
    for position, segment in enumerate(segments):
        require(isinstance(segment, dict), f"segments[{position}] must be an object")
        name = segment.get("name")
        require(isinstance(name, str) and name.strip(), f"segments[{position}].name is required")
        require(name not in names, f"duplicate segment name: {name}")
        names.add(name)
        base_id = segment.get("base_revenue_parameter_id")
        require(base_id in parameter_index, f"unknown base_revenue_parameter_id for {name}: {base_id}")
        base_parameter = parameter_index[base_id]
        require(base_parameter["dimension"] == "revenue", f"base revenue must use revenue dimension for {name}")
        require(period_year(base_parameter["period"], f"{base_id}.period") == data["base_year"], f"base revenue must use base year for {name}")
        require(base_parameter["value"] >= 0, f"base revenue cannot be negative for {name}")
        segment_total += float(base_parameter["value"])

    adjustment_ids = data.get("base_adjustment_parameter_ids", [])
    require(isinstance(adjustment_ids, list), "base_adjustment_parameter_ids must be a list")
    for parameter_id in adjustment_ids:
        require(parameter_index[parameter_id]["dimension"] == "revenue", f"base adjustment must use revenue dimension: {parameter_id}")
    adjustment_total = sum(parameter_values(parameter_index, adjustment_ids))
    tolerance = finite_number(data.get("reconciliation_tolerance", 1e-6), "reconciliation_tolerance")
    require(tolerance >= 0, "reconciliation_tolerance cannot be negative")
    difference = segment_total + adjustment_total - total
    allowed = max(1.0, abs(total)) * tolerance
    require(abs(difference) <= allowed, f"base revenue does not reconcile: segments+adjustments={segment_total + adjustment_total}, reported={total}")


def _listed_parameter_ids(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _expand_derived_inputs(parameter_ids: set[str], parameter_index: dict[str, dict[str, Any]]) -> set[str]:
    expanded = set(parameter_ids)
    pending = list(parameter_ids)
    while pending:
        parameter_id = pending.pop()
        parameter = parameter_index.get(parameter_id)
        if not parameter or parameter.get("kind") != "derived_fact":
            continue
        for input_id in parameter.get("input_parameter_ids", []):
            if input_id not in expanded:
                expanded.add(input_id)
                pending.append(input_id)
    return expanded


def collect_parameter_roles(
    data: dict[str, Any], parameter_index: dict[str, dict[str, Any]]
) -> dict[str, set[str]]:
    """Collect parameters that actually enter the base or forecast calculation graph."""
    foundation: set[str] = set()
    forecast: set[str] = set()

    total_id = data.get("reported_total_revenue_parameter_id")
    if isinstance(total_id, str):
        foundation.add(total_id)
    foundation.update(_listed_parameter_ids(data.get("base_adjustment_parameter_ids", [])))

    for segment in data.get("segments", []):
        if not isinstance(segment, dict):
            continue
        base_id = segment.get("base_revenue_parameter_id")
        if isinstance(base_id, str):
            foundation.add(base_id)
        for base_field in ("base_backlog_parameter_id", "base_orders_parameter_id"):
            if isinstance(segment.get(base_field), str):
                foundation.add(segment[base_field])
        scenarios = segment.get("scenarios", {})
        if isinstance(scenarios, dict):
            for scenario in scenarios.values():
                if not isinstance(scenario, dict):
                    continue
                driver_map = scenario.get("driver_parameter_ids", {})
                if isinstance(driver_map, dict):
                    for ids in driver_map.values():
                        forecast.update(_listed_parameter_ids(ids))
        recognition = segment.get("recognition", {})
        if isinstance(recognition, dict):
            carry_in = recognition.get("carry_in_parameter_ids", {})
            if isinstance(carry_in, dict):
                for ids in carry_in.values():
                    forecast.update(_listed_parameter_ids(ids))
            progress = recognition.get("progress_parameter_ids", {})
            if isinstance(progress, dict):
                for ids in progress.values():
                    forecast.update(_listed_parameter_ids(ids))

    for adjustment in data.get("forecast_adjustments", []):
        if not isinstance(adjustment, dict):
            continue
        scenario_ids = adjustment.get("scenario_parameter_ids", {})
        if isinstance(scenario_ids, dict):
            for ids in scenario_ids.values():
                forecast.update(_listed_parameter_ids(ids))

    forecast.update(constraint_parameter_ids(data.get("revenue_constraints", [])))

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
    parameter_ids: set[str] = set()
    for segment in data.get("segments", []):
        if not isinstance(segment, dict):
            continue
        base_scenario = segment.get("scenarios", {}).get("base", {})
        if isinstance(base_scenario, dict):
            driver_map = base_scenario.get("driver_parameter_ids", {})
            if isinstance(driver_map, dict):
                for ids in driver_map.values():
                    parameter_ids.update(_listed_parameter_ids(ids))
        recognition = segment.get("recognition", {})
        if isinstance(recognition, dict):
            for container in ("carry_in_parameter_ids", "progress_parameter_ids"):
                scenario_map = recognition.get(container, {})
                if isinstance(scenario_map, dict):
                    parameter_ids.update(_listed_parameter_ids(scenario_map.get("base", [])))
    for adjustment in data.get("forecast_adjustments", []):
        if not isinstance(adjustment, dict):
            continue
        scenario_map = adjustment.get("scenario_parameter_ids", {})
        if isinstance(scenario_map, dict):
            parameter_ids.update(_listed_parameter_ids(scenario_map.get("base", [])))
    parameter_ids.update(constraint_parameter_ids(data.get("revenue_constraints", [])))
    return _expand_derived_inputs(parameter_ids, parameter_index)


def base_segment_parameter_ids(
    data: dict[str, Any], parameter_index: dict[str, dict[str, Any]]
) -> dict[str, set[str]]:
    """Map Base-path parameters to the segment revenue paths they can affect."""
    segment_parameters: dict[str, set[str]] = {}
    for segment in data.get("segments", []):
        if not isinstance(segment, dict) or not isinstance(segment.get("name"), str):
            continue
        parameter_ids: set[str] = set()
        base_scenario = segment.get("scenarios", {}).get("base", {})
        if isinstance(base_scenario, dict):
            driver_map = base_scenario.get("driver_parameter_ids", {})
            if isinstance(driver_map, dict):
                for ids in driver_map.values():
                    parameter_ids.update(_listed_parameter_ids(ids))
        recognition = segment.get("recognition", {})
        if isinstance(recognition, dict):
            for container in ("carry_in_parameter_ids", "progress_parameter_ids"):
                scenario_map = recognition.get(container, {})
                if isinstance(scenario_map, dict):
                    parameter_ids.update(_listed_parameter_ids(scenario_map.get("base", [])))
        segment_parameters[segment["name"]] = _expand_derived_inputs(parameter_ids, parameter_index)

    for constraint in data.get("revenue_constraints", []):
        if not isinstance(constraint, dict):
            continue
        affected_segments: set[str] = set()
        if constraint.get("type") == "sum_cap":
            affected_segments.update(constraint.get("segments", []))
        elif constraint.get("type") == "linked_ratio":
            affected_segments.add(constraint.get("target_segment"))
        elif constraint.get("type") == "elimination":
            affected_segments.update(constraint.get("segment_adjustment_parameter_ids", {}))
        linked_parameters = _expand_derived_inputs(
            constraint_parameter_ids([constraint]), parameter_index
        )
        for segment_name in affected_segments:
            if segment_name in segment_parameters:
                segment_parameters[segment_name].update(linked_parameters)
    return segment_parameters


def _string_list(value: Any, field: str, minimum: int = 1, maximum: int = 10) -> list[str]:
    require(isinstance(value, list), f"{field} must be a list")
    require(minimum <= len(value) <= maximum, f"{field} must contain {minimum}-{maximum} items")
    require(all(isinstance(item, str) and item.strip() for item in value), f"{field} must contain non-empty strings")
    normalized = [item.strip() for item in value]
    require(len(normalized) == len(set(normalized)), f"{field} must not contain duplicates")
    return normalized


def _validate_growth_driver_attribution(
    driver_id: str,
    attribution: Any,
    available_segments: set[str],
    attribution_totals: dict[str, float],
) -> tuple[set[str], list[dict[str, Any]]]:
    require(isinstance(attribution, list) and attribution, f"{driver_id}.segment_attribution must be a non-empty list")
    seen_segments: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for position, item in enumerate(attribution):
        require(isinstance(item, dict), f"{driver_id}.segment_attribution[{position}] must be an object")
        segment_name = item.get("segment_name")
        require(segment_name in available_segments, f"unknown growth driver segment: {segment_name}")
        require(segment_name not in seen_segments, f"duplicate segment attribution in {driver_id}: {segment_name}")
        seen_segments.add(segment_name)
        weight = finite_number(item.get("weight"), f"{driver_id}.segment_attribution[{position}].weight")
        require(0 < weight <= 1, f"growth driver attribution weight must be in (0, 1]: {driver_id}/{segment_name}")
        attribution_totals[segment_name] += weight
        normalized.append({"segment_name": segment_name, "weight": weight})
    return seen_segments, normalized


def _validate_growth_driver_parameters(
    driver_id: str,
    parameter_ids: Any,
    parameter_index: dict[str, dict[str, Any]],
    base_parameter_ids: set[str],
    parameters_by_segment: dict[str, set[str]],
    attributed_segments: set[str],
) -> list[str]:
    require(isinstance(parameter_ids, list) and parameter_ids, f"{driver_id}.parameter_ids must be a non-empty list")
    require(len(parameter_ids) == len(set(parameter_ids)), f"{driver_id}.parameter_ids contains duplicates")
    for parameter_id in parameter_ids:
        require(parameter_id in parameter_index, f"unknown growth driver parameter_id: {parameter_id}")
        require(parameter_id in base_parameter_ids, f"growth driver parameter_id is not used by the base forecast: {parameter_id}")
        require(parameter_index[parameter_id].get("scenario") in (None, "all", "base"), f"growth driver parameter is not a base/shared assumption: {parameter_id}")
        require(
            any(parameter_id in parameters_by_segment[segment_name] for segment_name in attributed_segments),
            f"growth driver parameter does not affect an attributed segment: {driver_id}/{parameter_id}",
        )
    return list(parameter_ids)


def _validate_growth_driver_evidence(
    driver_id: str,
    evidence_nodes: Any,
    counterevidence_status: str,
    evidence_ids: set[str],
    source_index: dict[str, dict[str, Any]],
    claim_index: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str], list[str], str]:
    require(isinstance(evidence_nodes, list) and evidence_nodes, f"{driver_id}.evidence_nodes must be a non-empty list")
    require(len(evidence_nodes) <= 10, f"{driver_id}.evidence_nodes cannot exceed 10 items")
    normalized_nodes: list[dict[str, Any]] = []
    for position, node in enumerate(evidence_nodes):
        require(isinstance(node, dict), f"{driver_id}.evidence_nodes[{position}] must be an object")
        evidence_id = node.get("evidence_id")
        require(isinstance(evidence_id, str) and re.fullmatch(r"[A-Za-z0-9_.-]+", evidence_id), f"{driver_id}.evidence_id must be a stable identifier")
        require(evidence_id not in evidence_ids, f"duplicate growth driver evidence_id: {evidence_id}")
        evidence_ids.add(evidence_id)
        evidence_type = node.get("evidence_type")
        require(isinstance(evidence_type, str) and evidence_type.strip(), f"{evidence_id}.evidence_type is required")
        inference_distance = node.get("inference_distance")
        require(inference_distance in GROWTH_DRIVER_INFERENCE_DISTANCES, f"unsupported inference_distance for {evidence_id}: {inference_distance}")
        conclusion = node.get("conclusion")
        require(isinstance(conclusion, str) and conclusion.strip(), f"{evidence_id}.conclusion is required")
        claims = validate_claim_ids(
            node.get("claim_ids"), claim_index, "growth_driver", evidence_id,
            f"{driver_id}.evidence_nodes[{position}]", "rationale_support",
        )
        node_source_ids = list(dict.fromkeys(claim["source_id"] for claim in claims))
        require(set(node_source_ids) <= set(source_index), f"unknown source in growth driver evidence: {evidence_id}")
        normalized_nodes.append({
            "evidence_id": evidence_id,
            "evidence_type": evidence_type.strip(),
            "inference_distance": inference_distance,
            "conclusion": conclusion.strip(),
            "claim_ids": list(node["claim_ids"]),
            "source_ids": node_source_ids,
        })
    supporting_nodes = [node for node in normalized_nodes if node["inference_distance"] != "contrary"]
    require(supporting_nodes, f"{driver_id} requires at least one non-contrary evidence node")
    if counterevidence_status == "found":
        require(any(node["inference_distance"] == "contrary" for node in normalized_nodes), f"{driver_id} found counterevidence requires a contrary evidence node")
    evidence_types = list(dict.fromkeys(node["evidence_type"] for node in supporting_nodes))
    evidence_source_ids = list(dict.fromkeys(source_id for node in supporting_nodes for source_id in node["source_ids"]))
    evidence_status = "triangulated" if len(evidence_types) >= 2 and len(evidence_source_ids) >= 2 else "limited"
    return normalized_nodes, evidence_types, evidence_source_ids, evidence_status


def _validate_growth_driver_record(
    driver: Any,
    position: int,
    data: dict[str, Any],
    parameter_index: dict[str, dict[str, Any]],
    source_index: dict[str, dict[str, Any]],
    claim_index: dict[str, dict[str, Any]],
    context: dict[str, Any],
) -> dict[str, Any]:
    prefix = f"growth_driver_tree.drivers[{position}]"
    require(isinstance(driver, dict), f"{prefix} must be an object")
    driver_id = driver.get("driver_id")
    require(isinstance(driver_id, str) and re.fullmatch(r"[A-Za-z0-9_.-]+", driver_id), f"{prefix}.driver_id must be a stable identifier")
    require(driver_id not in context["driver_ids"], f"duplicate growth driver_id: {driver_id}")
    context["driver_ids"].add(driver_id)
    for field in ("title", "thesis", "persistence_rationale", "counterevidence_rationale"):
        require(isinstance(driver.get(field), str) and driver[field].strip(), f"{driver_id}.{field} is required")
    causal_chain = _string_list(driver.get("causal_chain"), f"{driver_id}.causal_chain", 2, 8)
    leading_indicators = _string_list(driver.get("leading_indicators"), f"{driver_id}.leading_indicators", 1, 8)
    falsifiers = _string_list(driver.get("falsifiers"), f"{driver_id}.falsifiers", 1, 8)
    attributed_segments, normalized_attribution = _validate_growth_driver_attribution(
        driver_id, driver.get("segment_attribution"), context["available_segments"], context["attribution_totals"]
    )
    parameter_ids = _validate_growth_driver_parameters(
        driver_id, driver.get("parameter_ids"), parameter_index, context["base_parameter_ids"],
        context["parameters_by_segment"], attributed_segments,
    )
    horizon = driver.get("horizon")
    require(isinstance(horizon, dict), f"{driver_id}.horizon must be an object")
    start_year, end_year = horizon.get("start_year"), horizon.get("end_year")
    require(isinstance(start_year, int) and isinstance(end_year, int), f"{driver_id}.horizon years must be integers")
    require(data["forecast_years"][0] <= start_year <= end_year <= data["forecast_years"][-1], f"{driver_id}.horizon must fall inside forecast_years")
    persistence = driver.get("persistence")
    require(persistence in GROWTH_DRIVER_PERSISTENCE, f"unsupported persistence for {driver_id}: {persistence}")
    counterevidence_status = driver.get("counterevidence_status")
    require(counterevidence_status in GROWTH_DRIVER_COUNTEREVIDENCE_STATUSES, f"unsupported counterevidence_status for {driver_id}: {counterevidence_status}")
    normalized_nodes, evidence_types, evidence_source_ids, evidence_status = _validate_growth_driver_evidence(
        driver_id, driver.get("evidence_nodes"), counterevidence_status, context["evidence_ids"],
        source_index, claim_index,
    )
    if counterevidence_status == "data_gap":
        context["gap_messages"].append(f"growth_driver:{driver_id}: counterevidence search is incomplete")
    if evidence_status == "limited":
        context["limitations"].append(f"Growth driver {driver_id} is not triangulated across two evidence types and sources")
    return {
        "driver_id": driver_id,
        "title": driver["title"].strip(),
        "thesis": driver["thesis"].strip(),
        "causal_chain": causal_chain,
        "parameter_ids": parameter_ids,
        "segment_attribution": normalized_attribution,
        "horizon": {"start_year": start_year, "end_year": end_year},
        "persistence": persistence,
        "persistence_rationale": driver["persistence_rationale"].strip(),
        "evidence_nodes": normalized_nodes,
        "evidence_types": evidence_types,
        "evidence_source_ids": evidence_source_ids,
        "evidence_status": evidence_status,
        "leading_indicators": leading_indicators,
        "falsifiers": falsifiers,
        "counterevidence_status": counterevidence_status,
        "counterevidence_rationale": driver["counterevidence_rationale"].strip(),
    }


def validate_growth_driver_tree(
    data: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
    parameter_index: dict[str, dict[str, Any]],
    claim_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Validate a generic causal tree that explains the modeled base-case revenue path."""
    tree = data.get("growth_driver_tree")
    require(isinstance(tree, dict), "growth_driver_tree must be an object")
    status = tree.get("status")
    require(status in GROWTH_DRIVER_TREE_STATUSES, f"unsupported growth_driver_tree status: {status}")
    drivers = tree.get("drivers")
    require(isinstance(drivers, list), "growth_driver_tree.drivers must be a list")
    if status == "data_gap":
        require(not drivers, "growth_driver_tree data_gap cannot contain drivers")
        rationale = tree.get("rationale")
        require(isinstance(rationale, str) and rationale.strip(), "growth_driver_tree data_gap requires rationale")
        return {
            "status": status,
            "rationale": rationale.strip(),
            "drivers": [],
            "gap_messages": [f"growth_driver_tree: {rationale.strip()}"],
            "limitations": ["No auditable revenue growth-driver tree is available"],
        }

    require(1 <= len(drivers) <= 10, "growth_driver_tree modeled status requires 1-10 drivers")
    segment_names = [segment.get("name") for segment in data.get("segments", []) if isinstance(segment, dict)]
    require(all(isinstance(name, str) and name.strip() for name in segment_names), "growth_driver_tree requires valid segment names")
    available_segments = set(segment_names)
    base_parameter_ids = base_forecast_parameter_ids(data, parameter_index)
    parameters_by_segment = base_segment_parameter_ids(data, parameter_index)
    require(base_parameter_ids, "growth_driver_tree modeled status requires a base forecast path")
    context: dict[str, Any] = {
        "available_segments": available_segments,
        "base_parameter_ids": base_parameter_ids,
        "parameters_by_segment": parameters_by_segment,
        "attribution_totals": {name: 0.0 for name in segment_names},
        "driver_ids": set(),
        "evidence_ids": set(),
        "limitations": [],
        "gap_messages": [],
    }
    normalized_drivers = [
        _validate_growth_driver_record(
            driver, position, data, parameter_index, source_index, claim_index, context
        )
        for position, driver in enumerate(drivers)
    ]
    for segment_name, total in context["attribution_totals"].items():
        require(math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-9), f"growth driver attribution weights must sum to 1 for segment {segment_name}; got {total}")
    return {
        "status": status,
        "drivers": normalized_drivers,
        "gap_messages": context["gap_messages"],
        "limitations": context["limitations"],
    }


def calculate_growth_driver_analysis(validated: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Rank causal revenue drivers by reconciled base-case terminal revenue increment."""
    tree = validated["growth_driver_tree"]
    base_contribution = result["consolidated_forecast"]["base"]["incremental_contribution"]
    segment_increments = {
        item["name"]: float(item["terminal_incremental_revenue"])
        for item in base_contribution["segments"]
    }
    if tree["status"] == "data_gap":
        return {
            "status": "data_gap",
            "rationale": tree["rationale"],
            "top_drivers": [],
            "headwinds": [],
            "drivers": [],
            "unattributed_company_adjustments": float(base_contribution["adjustments"]),
            "reconciliation": {
                "driver_attributed_segment_increment": 0.0,
                "segment_increment_total": sum(segment_increments.values()),
                "unattributed_company_adjustments": float(base_contribution["adjustments"]),
                "company_increment_total": float(base_contribution["total"]),
                "difference": float(base_contribution["adjustments"]) - float(base_contribution["total"]),
            },
        }

    output_drivers: list[dict[str, Any]] = []
    for driver in tree["drivers"]:
        by_segment = [
            {
                "segment_name": item["segment_name"],
                "weight": item["weight"],
                "terminal_incremental_revenue": segment_increments[item["segment_name"]] * item["weight"],
            }
            for item in driver["segment_attribution"]
        ]
        impact = sum(item["terminal_incremental_revenue"] for item in by_segment)
        output = copy.deepcopy(driver)
        output["terminal_increment_by_segment"] = by_segment
        output["estimated_base_terminal_increment"] = impact
        output_drivers.append(output)

    positive_total = sum(max(0.0, driver["estimated_base_terminal_increment"]) for driver in output_drivers)
    for driver in output_drivers:
        driver["share_of_positive_driver_increment"] = (
            None if positive_total == 0
            else max(0.0, driver["estimated_base_terminal_increment"]) / positive_total
        )

    def summary(driver: dict[str, Any]) -> dict[str, Any]:
        return {
            "driver_id": driver["driver_id"],
            "title": driver["title"],
            "thesis": driver["thesis"],
            "estimated_base_terminal_increment": driver["estimated_base_terminal_increment"],
            "share_of_positive_driver_increment": driver["share_of_positive_driver_increment"],
            "segment_names": [item["segment_name"] for item in driver["segment_attribution"]],
            "causal_chain": list(driver["causal_chain"]),
            "evidence_status": driver["evidence_status"],
            "leading_indicators": list(driver["leading_indicators"]),
            "falsifiers": list(driver["falsifiers"]),
        }

    positive = sorted(
        (driver for driver in output_drivers if driver["estimated_base_terminal_increment"] > 0),
        key=lambda driver: (-driver["estimated_base_terminal_increment"], driver["driver_id"]),
    )
    negative = sorted(
        (driver for driver in output_drivers if driver["estimated_base_terminal_increment"] < 0),
        key=lambda driver: (driver["estimated_base_terminal_increment"], driver["driver_id"]),
    )
    top_drivers = [dict(summary(driver), rank=rank) for rank, driver in enumerate(positive[:5], start=1)]
    headwinds = [dict(summary(driver), rank=rank) for rank, driver in enumerate(negative[:5], start=1)]
    attributed = sum(driver["estimated_base_terminal_increment"] for driver in output_drivers)
    segment_total = sum(segment_increments.values())
    require(math.isclose(attributed, segment_total, rel_tol=1e-9, abs_tol=1e-9), "growth driver attribution does not reconcile to segment increment")
    adjustments = float(base_contribution["adjustments"])
    company_total = float(base_contribution["total"])
    return {
        "status": "modeled",
        "top_drivers": top_drivers,
        "headwinds": headwinds,
        "drivers": output_drivers,
        "unattributed_company_adjustments": adjustments,
        "reconciliation": {
            "driver_attributed_segment_increment": attributed,
            "segment_increment_total": segment_total,
            "unattributed_company_adjustments": adjustments,
            "company_increment_total": company_total,
            "difference": attributed + adjustments - company_total,
        },
    }


def validate_research_coverage(
    data: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
    parameter_index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Validate the nine-dimension research gate without turning it into a score."""
    coverage = data.get("research_coverage")
    require(isinstance(coverage, list), "research_coverage must be a list")
    require(len(coverage) == len(RESEARCH_DIMENSIONS), "research_coverage must contain exactly nine dimensions")
    roles = collect_parameter_roles(data, parameter_index)
    normalized: dict[str, dict[str, Any]] = {}

    for position, record in enumerate(coverage):
        prefix = f"research_coverage[{position}]"
        require(isinstance(record, dict), f"{prefix} must be an object")
        dimension = record.get("dimension")
        require(dimension in RESEARCH_DIMENSIONS, f"unsupported research dimension: {dimension}")
        require(dimension not in normalized, f"duplicate research dimension: {dimension}")
        status = record.get("status")
        require(status in RESEARCH_COVERAGE_STATUSES, f"unsupported research coverage status for {dimension}: {status}")
        for field in ("conclusion", "revenue_mechanism"):
            require(isinstance(record.get(field), str) and record[field].strip(), f"{dimension}.{field} is required")

        parameter_ids = record.get("parameter_ids", [])
        source_ids = record.get("source_ids", [])
        require(isinstance(parameter_ids, list), f"{dimension}.parameter_ids must be a list")
        require(isinstance(source_ids, list), f"{dimension}.source_ids must be a list")
        require(len(parameter_ids) == len(set(parameter_ids)), f"{dimension}.parameter_ids contains duplicates")
        require(len(source_ids) == len(set(source_ids)), f"{dimension}.source_ids contains duplicates")
        for parameter_id in parameter_ids:
            require(parameter_id in parameter_index, f"unknown research parameter_id {parameter_id} for {dimension}")
            require(parameter_id in roles["used"], f"research parameter_id {parameter_id} for {dimension} is not used by the revenue model")
        for source_id in source_ids:
            require(source_id in source_index, f"unknown research source_id {source_id} for {dimension}")

        rationale = record.get("rationale")
        if status == "modeled_driver":
            require(bool(parameter_ids), f"{dimension} modeled_driver requires parameter_ids")
            require(bool(source_ids), f"{dimension} modeled_driver requires source_ids")
            if dimension == "company_foundation":
                require(bool(set(parameter_ids) & roles["foundation"]), "company_foundation must map to a base or reported revenue parameter")
            if dimension == "growth_curve":
                require(bool(set(parameter_ids) & roles["forecast"]), "growth_curve must map to a forecast driver, carry-in, or adjustment parameter")
        elif status == "data_gap":
            require(isinstance(rationale, str) and rationale.strip(), f"{dimension} data_gap requires rationale")
        else:
            require(not parameter_ids, f"{dimension} immaterial cannot map to model parameters")
            require(isinstance(rationale, str) and rationale.strip(), f"{dimension} immaterial requires rationale")

        item = {
            "dimension": dimension,
            "status": status,
            "conclusion": record["conclusion"].strip(),
            "revenue_mechanism": record["revenue_mechanism"].strip(),
            "parameter_ids": list(parameter_ids),
            "source_ids": list(source_ids),
        }
        if isinstance(rationale, str) and rationale.strip():
            item["rationale"] = rationale.strip()
        normalized[dimension] = item

    require(set(normalized) == set(RESEARCH_DIMENSIONS), "research_coverage must include every required dimension exactly once")
    records = [normalized[dimension] for dimension in RESEARCH_DIMENSIONS]
    return {
        "records": records,
        "counts": {
            status: sum(record["status"] == status for record in records)
            for status in sorted(RESEARCH_COVERAGE_STATUSES)
        },
        "gap_messages": [
            f"{record['dimension']}: {record['conclusion']}"
            for record in records
            if record["status"] == "data_gap"
        ],
        "parameter_roles": roles,
    }


def validate_management_target_coverage(
    data: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
    parameter_index: dict[str, dict[str, Any]],
    claim_index: dict[str, dict[str, Any]],
    as_of: date,
) -> dict[str, Any]:
    """Validate official communication coverage and every material forward revenue target."""
    coverage = data.get("management_communication_coverage")
    require(isinstance(coverage, list), "management_communication_coverage must be a list")
    require(
        len(coverage) == len(MANAGEMENT_COMMUNICATION_CATEGORIES),
        "management_communication_coverage must contain every required category",
    )
    normalized_coverage: dict[str, dict[str, Any]] = {}
    referenced_target_ids: set[str] = set()
    for position, record in enumerate(coverage):
        prefix = f"management_communication_coverage[{position}]"
        require(isinstance(record, dict), f"{prefix} must be an object")
        category = record.get("category")
        require(category in MANAGEMENT_COMMUNICATION_CATEGORIES, f"unsupported management communication category: {category}")
        require(category not in normalized_coverage, f"duplicate management communication category: {category}")
        status = record.get("status")
        require(status in MANAGEMENT_COMMUNICATION_STATUSES, f"unsupported management communication status: {category}/{status}")
        conclusion = record.get("conclusion")
        require(isinstance(conclusion, str) and conclusion.strip(), f"{category}.conclusion is required")
        source_ids = record.get("source_ids", [])
        target_ids = record.get("material_revenue_target_ids", [])
        require(isinstance(source_ids, list) and len(source_ids) == len(set(source_ids)), f"{category}.source_ids must be unique")
        require(isinstance(target_ids, list) and len(target_ids) == len(set(target_ids)), f"{category}.material_revenue_target_ids must be unique")
        require(all(isinstance(item, str) and item.strip() for item in target_ids), f"{category}.material_revenue_target_ids contains invalid IDs")
        for source_id in source_ids:
            require(source_id in source_index, f"unknown management communication source_id: {source_id}")
        checked_date = parse_iso_date(record.get("checked_date"), f"{category}.checked_date")
        require(checked_date <= as_of, f"management communication checked after as_of_date: {category}")
        rationale = record.get("rationale")
        if status == "checked":
            require(bool(source_ids), f"checked management communication requires source_ids: {category}")
        else:
            require(not source_ids, f"{status} management communication cannot contain source_ids: {category}")
            require(not target_ids, f"{status} management communication cannot contain target_ids: {category}")
            require(isinstance(rationale, str) and rationale.strip(), f"{status} management communication requires rationale: {category}")
            if status == "not_available":
                require(isinstance(record.get("search_description"), str) and record["search_description"].strip(), f"not_available communication requires search_description: {category}")
        referenced_target_ids.update(target_ids)
        normalized = {
            "category": category,
            "status": status,
            "source_ids": list(source_ids),
            "checked_date": checked_date.isoformat(),
            "conclusion": conclusion.strip(),
            "material_revenue_target_ids": list(target_ids),
        }
        for optional in ("rationale", "search_description"):
            if isinstance(record.get(optional), str) and record[optional].strip():
                normalized[optional] = record[optional].strip()
        normalized_coverage[category] = normalized

    targets = data.get("management_targets")
    require(isinstance(targets, list), "management_targets must be a list")
    roles = collect_parameter_roles(data, parameter_index)
    segment_names = {segment.get("name") for segment in data.get("segments", []) if isinstance(segment, dict)}
    normalized_targets: dict[str, dict[str, Any]] = {}
    gap_messages: list[str] = []
    for position, target in enumerate(targets):
        prefix = f"management_targets[{position}]"
        require(isinstance(target, dict), f"{prefix} must be an object")
        target_id = target.get("target_id")
        require(isinstance(target_id, str) and target_id.strip(), f"{prefix}.target_id is required")
        require(target_id not in normalized_targets, f"duplicate management target: {target_id}")
        for field in ("statement", "metric_name", "metric_definition", "target_period", "raw_unit", "raw_currency", "raw_scale", "measurement_rationale", "perimeter_notes", "rationale"):
            require(isinstance(target.get(field), str) and target[field].strip(), f"{target_id}.{field} is required")
        raw_value = finite_number(target.get("raw_target_value"), f"{target_id}.raw_target_value")
        require(raw_value >= 0, f"management target cannot be negative: {target_id}")
        measurement_basis = target.get("measurement_basis")
        require(measurement_basis in MANAGEMENT_TARGET_MEASUREMENT_BASES, f"invalid management target measurement basis: {target_id}")
        measurement_periods = target.get("measurement_periods")
        require(isinstance(measurement_periods, list) and len(measurement_periods) == len(set(measurement_periods)), f"invalid management target measurement periods: {target_id}")
        measurement_years = [period_year(period, f"{target_id}.measurement_periods") for period in measurement_periods]
        require(measurement_years == sorted(measurement_years), f"management target measurement periods must be ordered: {target_id}")
        if measurement_basis in {"annual_period", "run_rate_at_period_end"}:
            require(len(measurement_years) == 1, f"single-period management target requires exactly one measurement period: {target_id}")
        elif measurement_basis == "cumulative_periods":
            require(len(measurement_years) >= 2, f"cumulative management target requires at least two measurement periods: {target_id}")
            require(measurement_years == list(range(measurement_years[0], measurement_years[-1] + 1)), f"cumulative management target periods must be contiguous: {target_id}")
        else:
            require(not measurement_years, f"ambiguous management target cannot claim measurement periods: {target_id}")
        materiality = target.get("materiality")
        require(materiality in {"material", "contextual"}, f"invalid management target materiality: {target_id}")
        commitment_strength = target.get("commitment_strength")
        require(commitment_strength in {"guidance", "goal", "aspiration", "capacity_plan"}, f"invalid management target commitment strength: {target_id}")
        perimeter_status = target.get("perimeter_status")
        require(perimeter_status in MANAGEMENT_TARGET_PERIMETERS, f"invalid management target perimeter: {target_id}")
        treatment = target.get("treatment")
        require(treatment in MANAGEMENT_TARGET_TREATMENTS, f"invalid management target treatment: {target_id}")
        comparison = target.get("comparison")
        require(comparison in MANAGEMENT_TARGET_COMPARISONS, f"invalid management target comparison: {target_id}")
        scope = target.get("scope")
        require(isinstance(scope, dict) and scope.get("type") in {"company", "segment", "custom"}, f"invalid management target scope: {target_id}")
        scope_name = scope.get("name")
        require(isinstance(scope_name, str) and scope_name.strip(), f"management target scope name is required: {target_id}")
        if scope["type"] == "segment":
            require(scope_name in segment_names, f"unknown management target segment: {target_id}/{scope_name}")

        claim_ids = target.get("claim_ids")
        linked_claims = validate_claim_ids(claim_ids, claim_index, "management_target", target_id, target_id, "exact_value")
        source_ids = []
        for linked in linked_claims:
            extracted = finite_number(linked.get("extracted_value"), f"{linked['claim_id']}.extracted_value")
            require(math.isclose(extracted, raw_value, rel_tol=0, abs_tol=1e-9), f"management target claim value mismatch: {target_id}")
            require(linked.get("unit") == target["raw_unit"], f"management target claim unit mismatch: {target_id}")
            require(linked.get("period") == target["target_period"], f"management target claim period mismatch: {target_id}")
            source_ids.append(linked["source_id"])

        mapped_ids = target.get("mapped_parameter_ids", [])
        mapped_scenarios = target.get("mapped_scenarios", [])
        require(isinstance(mapped_ids, list) and len(mapped_ids) == len(set(mapped_ids)), f"invalid mapped_parameter_ids: {target_id}")
        require(isinstance(mapped_scenarios, list) and len(mapped_scenarios) == len(set(mapped_scenarios)), f"invalid mapped_scenarios: {target_id}")
        require(set(mapped_scenarios) <= set(SCENARIOS), f"invalid mapped scenario: {target_id}")
        for parameter_id in mapped_ids:
            require(parameter_id in parameter_index, f"unknown management target parameter: {target_id}/{parameter_id}")
            require(parameter_id in roles["forecast"], f"management target parameter is not used by the forecast: {target_id}/{parameter_id}")

        within_horizon = bool(measurement_years) and set(measurement_years) <= set(data["forecast_years"])
        comparable = (
            measurement_basis != "ambiguous"
            and perimeter_status in {"matched", "reconciled"}
            and scope["type"] in {"company", "segment"}
        )
        comparison_value = target.get("comparison_value")
        if comparable:
            comparison_value = finite_number(comparison_value, f"{target_id}.comparison_value")
            require(comparison_value >= 0, f"management target comparison value cannot be negative: {target_id}")
            require(target.get("comparison_currency") == data["currency"], f"management target comparison currency mismatch: {target_id}")
            require(target.get("comparison_scale") == data["unit"], f"management target comparison scale mismatch: {target_id}")
            require(isinstance(target.get("normalization_rationale"), str) and target["normalization_rationale"].strip(), f"management target normalization rationale is required: {target_id}")
        else:
            require(comparison_value is None, f"non-comparable management target cannot contain comparison_value: {target_id}")

        if measurement_basis == "ambiguous":
            require(treatment == "unmodeled_data_gap", f"measurement-ambiguous target must remain an unmodeled data gap: {target_id}")
            require(not mapped_ids and not mapped_scenarios, f"measurement-ambiguous target cannot claim scenario mapping: {target_id}")

        if treatment in {"modeled_scenario", "scenario_boundary"}:
            require(within_horizon, f"modeled management target must be inside forecast horizon: {target_id}")
            require(comparable, f"modeled management target requires matched or reconciled perimeter: {target_id}")
            require(bool(mapped_ids) and bool(mapped_scenarios), f"modeled management target requires mapped parameters and scenarios: {target_id}")
        elif treatment == "out_of_horizon":
            require(bool(measurement_years) and max(measurement_years) > max(data["forecast_years"]), f"out_of_horizon target must extend after forecast horizon: {target_id}")
            require(not mapped_ids and not mapped_scenarios, f"out_of_horizon target cannot claim scenario mapping: {target_id}")
            gap_messages.append(f"management_target:{target_id}: target period {target['target_period']} is outside the forecast horizon")
        else:
            require(not mapped_scenarios, f"unmodeled management target cannot claim mapped scenarios: {target_id}")
            gap_messages.append(f"management_target:{target_id}: {treatment}")

        if materiality == "material" and within_horizon and comparable:
            require(treatment in {"modeled_scenario", "scenario_boundary"}, f"material in-horizon comparable target must enter a scenario: {target_id}")
        if perimeter_status == "mismatch":
            require(treatment in {"unmodeled_data_gap", "out_of_horizon"}, f"perimeter-mismatched target cannot be modeled directly: {target_id}")

        normalized = copy.deepcopy(target)
        normalized["raw_target_value"] = raw_value
        normalized["measurement_periods"] = list(measurement_periods)
        normalized["source_ids"] = list(dict.fromkeys(source_ids))
        if comparable:
            normalized["comparison_value"] = float(comparison_value)
        normalized_targets[target_id] = normalized

    require(referenced_target_ids == set(normalized_targets), "management communication target IDs must match management_targets exactly")
    records = [normalized_coverage[category] for category in MANAGEMENT_COMMUNICATION_CATEGORIES]
    target_records = [normalized_targets[target["target_id"]] for target in targets]
    return {
        "communications": records,
        "targets": target_records,
        "counts": {
            "communications_checked": sum(record["status"] == "checked" for record in records),
            "targets_total": len(target_records),
            "targets_modeled": sum(record["treatment"] in {"modeled_scenario", "scenario_boundary"} for record in target_records),
            "targets_unmodeled": sum(record["treatment"] not in {"modeled_scenario", "scenario_boundary"} for record in target_records),
        },
        "gap_messages": gap_messages,
    }


def add_management_target_analysis(
    validated: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    """Attach scenario attainment to the already validated target ledger."""
    output_targets = []
    segment_index = {segment["name"]: segment for segment in result["segments"]}
    for target in validated["management_target_coverage"]["targets"]:
        item = copy.deepcopy(target)
        comparisons: dict[str, Any] = {}
        if target["treatment"] in {"modeled_scenario", "scenario_boundary"}:
            measurement_periods = list(target["measurement_periods"])
            target_value = float(target["comparison_value"])
            tolerance = finite_number(target.get("comparison_tolerance", 0.01), f"{target['target_id']}.comparison_tolerance")
            require(0 <= tolerance <= 0.25, f"management target comparison_tolerance outside 0..0.25: {target['target_id']}")
            for scenario in target["mapped_scenarios"]:
                if target["scope"]["type"] == "company":
                    revenue_path = result["consolidated_forecast"][scenario]["annual_revenue"]
                else:
                    scenario_output = segment_index[target["scope"]["name"]]["scenarios"][scenario]
                    revenue_path = scenario_output.get("effective_revenue", scenario_output["recognized_revenue"])
                period_values = {period: float(revenue_path[period[2:]]) for period in measurement_periods}
                if target["measurement_basis"] == "cumulative_periods":
                    observed = sum(period_values.values())
                else:
                    observed = period_values[measurement_periods[0]]
                if target["comparison"] == "at_least":
                    meets = observed >= target_value * (1 - tolerance)
                elif target["comparison"] == "at_most":
                    meets = observed <= target_value * (1 + tolerance)
                else:
                    meets = math.isclose(observed, target_value, rel_tol=tolerance, abs_tol=max(1.0, abs(target_value)) * tolerance)
                require(meets, f"mapped scenario does not satisfy management target: {target['target_id']}/{scenario}")
                comparisons[scenario] = {
                    "measurement_basis": target["measurement_basis"],
                    "measurement_periods": measurement_periods,
                    "modeled_period_values": period_values,
                    "modeled_value": observed,
                    "target_value": target_value,
                    "attainment_ratio": None if target_value == 0 else observed / target_value,
                    "meets_target": meets,
                }
        item["scenario_comparison"] = comparisons
        output_targets.append(item)
    return {
        "communications": copy.deepcopy(validated["management_target_coverage"]["communications"]),
        "targets": output_targets,
        "counts": copy.deepcopy(validated["management_target_coverage"]["counts"]),
    }


def validate_document(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and return indexes used by the forecast engine."""
    years, as_of = validate_top_level(data)
    source_index = validate_sources(data, as_of)
    parameter_index = validate_parameters(data, source_index)
    claim_index = validate_evidence_claims(data, source_index, parameter_index, as_of)
    validate_historical_revenue(data, source_index, parameter_index, claim_index)
    validate_base_reconciliation(data, parameter_index)
    try:
        revenue_constraints = validate_revenue_constraints(
            data.get("revenue_constraints", []),
            [segment.get("name") for segment in data.get("segments", []) if isinstance(segment, dict)],
            parameter_index,
            years,
        )
    except RevenueConstraintError as exc:
        raise ForecastInputError(str(exc)) from exc
    research_coverage = validate_research_coverage(data, source_index, parameter_index)
    growth_driver_tree = validate_growth_driver_tree(
        data, source_index, parameter_index, claim_index
    )
    management_target_coverage = validate_management_target_coverage(
        data, source_index, parameter_index, claim_index, as_of
    )
    return {
        "years": years,
        "as_of_date": as_of,
        "source_index": source_index,
        "parameter_index": parameter_index,
        "claim_index": claim_index,
        "revenue_constraints": revenue_constraints,
        "research_coverage": research_coverage,
        "growth_driver_tree": growth_driver_tree,
        "management_target_coverage": management_target_coverage,
    }
