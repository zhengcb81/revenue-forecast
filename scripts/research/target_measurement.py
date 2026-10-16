"""Typed management comparisons over existing RF paths and quarter bridges.

Money scaling resolves through the one DU5 Currency x Scale description
(``research.input_quantities``); this module keeps no scale list of its own.
The comparison contract below is sign-safe: a target's negative sign never
reverses which side counts as a shortfall, strict comparisons stay strict, and
a two-ended range keeps both ends instead of becoming a midpoint.
"""
from __future__ import annotations

from copy import deepcopy
import math
import re

from contracts.constants import SCENARIOS
from contracts.evidence import finite_number, require, validate_claim_ids
from research.input_quantities import money_scale_factor, same_money_currency
from research.native_dependencies import scope_components

SCHEMA = "management-target-comparison/1"
METRICS = {"annual_revenue_level", "quarterly_revenue_level", "year_over_year_growth"}
# Named diagnostics: a comparison word whose economic meaning cannot be pinned
# down without guessing is refused by name instead of being silently resolved.
OPERATOR_RANGE_INCOMPATIBLE = "typed_comparison_operator_range_incompatible"
ATTAINMENT_RATIO_WITHHELD = "attainment_ratio_withheld_nonpositive_target"


def is_typed_target(target: dict) -> bool:
    return isinstance(target.get("comparison_basis"), dict)


def normalize_target_bounds(target: dict, data: dict) -> tuple[float, float]:
    """Convert stated units only; never synthesize a manager dollar target.

    Money amounts resolve through the shared DU5 Currency x Scale description,
    so CNY and RMB are one currency, ``万``/``万元``/``10k`` are one scale, and
    HKD/USD/RMB still never mix without an FX basis. A growth target is a
    signed ratio: it keeps its sign (a decline is never rewritten as growth)
    and never licenses a negative revenue amount.
    """
    spec = target["comparison_basis"]
    raw = target.get("raw_target_value")
    low = target.get("raw_target_value_low") if raw is None else raw
    high = target.get("raw_target_value_high") if raw is None else raw
    low = finite_number(low, "target lower bound")
    high = finite_number(high, "target upper bound")
    if spec["metric_kind"] == "year_over_year_growth":
        basis = spec.get("raw_ratio_basis")
        require(basis in {"percent", "fraction", "level_multiple"}, "growth target requires explicit raw_ratio_basis")
        if basis == "percent":
            low, high = low / 100, high / 100
        elif basis == "level_multiple":
            low, high = low - 1, high - 1
    else:
        require(target["raw_unit"] == f"{target['raw_currency']} {target['raw_scale']}",
                "typed target raw unit must match currency/scale used for normalization")
        require(same_money_currency(target["raw_currency"], data["currency"]),
                "typed target currency mismatch; reconcile first")
        raw_factor = money_scale_factor(target["raw_scale"])
        model_factor = money_scale_factor(data["unit"])
        require(raw_factor is not None and model_factor is not None, "typed target scale is unsupported")
        low, high = low * raw_factor / model_factor, high * raw_factor / model_factor
    require(low <= high, "typed target range is inverted")
    return low, high


def range_comparison_is_defined(comparison: str) -> bool:
    """Only ``approximately`` has an unambiguous two-ended range meaning.

    ``at_least``/``at_most``/``greater_than``/``less_than`` each name one
    threshold, and a range names two: whether the floor is the low end or the
    high end cannot be settled without guessing management's intent. Those
    combinations carry the named ``OPERATOR_RANGE_INCOMPATIBLE`` diagnostic.
    """
    return comparison == "approximately"


def acceptance_bound(value: float, tolerance: float, *, lower: bool) -> float:
    """Tolerance band edge for ``at_least`` (lower) / ``at_most`` (upper).

    A non-negative target keeps the frozen ``value * (1 +/- tolerance)``
    expression bit for bit. A negative target widens away from zero, so the
    target's sign never reverses which side counts as a shortfall.
    """
    if value >= 0:
        return value * (1 - tolerance) if lower else value * (1 + tolerance)
    return value - tolerance * abs(value) if lower else value + tolerance * abs(value)


def meets_target(observed: float, low: float, high: float, comparison: str, tolerance: float) -> bool:
    if low != high:
        require(
            range_comparison_is_defined(comparison),
            f"{OPERATOR_RANGE_INCOMPATIBLE}: comparison {comparison} names one threshold "
            f"but the target range names two; use approximately or a point target",
        )
        return low <= observed <= high
    if comparison == "greater_than":
        return observed > low
    if comparison == "less_than":
        return observed < low
    if comparison == "at_least":
        return observed >= acceptance_bound(low, tolerance, lower=True)
    if comparison == "at_most":
        return observed <= acceptance_bound(low, tolerance, lower=False)
    return math.isclose(observed, low, rel_tol=tolerance, abs_tol=max(abs(low), 1e-12) * tolerance)


def attainment_ratio(observed: float | None, low: float, high: float) -> float | None:
    """Attainment of a point target, withheld where the ratio would mislead.

    ``observed / low`` flips better and worse when ``low`` is negative, and a
    zero target has no ratio at all. A two-ended range has no single target to
    divide by (no midpoint is invented). The comparable observed value,
    ``meets_target`` and the signed difference are never suppressed here.
    """
    if observed is None or low != high or low <= 0:
        return None
    return observed / low


def validate_typed_target(target, data, parameters, claims, sources, used):
    spec = target["comparison_basis"]
    require(spec.get("schema_version") == SCHEMA, "unsupported typed management comparison")
    metric = spec.get("metric_kind")
    require(metric in METRICS, "unsupported management comparison metric_kind")
    period = spec.get("period")
    pattern = r"FY\d{4}(?:Q[1-4]|H[12])" if metric == "quarterly_revenue_level" else r"FY\d{4}"
    require(isinstance(period, str) and re.fullmatch(pattern, period) is not None, "typed comparison period is invalid")
    year = int(period[2:6])
    treatment = target["treatment"]
    modeled = treatment in {"modeled_scenario", "scenario_boundary", "independent_benchmark"}
    require(target["target_period"] == f"FY{year}", "typed comparison target period mismatch")
    require(bool(target.get("normalization_rationale")), "typed comparison requires normalization rationale")
    if metric != "quarterly_revenue_level":
        require(target["measurement_periods"] == [period], "typed comparison measurement periods mismatch")
    allowed = {"schema_version", "metric_kind", "period"}
    if metric == "year_over_year_growth":
        allowed |= {"base_period", "raw_ratio_basis"}
        base = spec.get("base_period")
        require(base is None or (isinstance(base, str) and re.fullmatch(r"FY\d{4}", base) is not None), "typed growth base_period is invalid")
        require(base is None or int(base[2:]) == year - 1, "year-over-year growth requires the previous fiscal period")
        require(target["measurement_basis"] == "annual_period", "growth measurement basis must be annual_period")
    elif metric == "quarterly_revenue_level":
        allowed.add("scenario_parameter_ids")
        require(target["measurement_basis"] == "quarterly_period" and target.get("target_quarter") == period[6:], "typed quarterly period mismatch")
        mapping = spec.get("scenario_parameter_ids")
        require(mapping is None and not modeled or isinstance(mapping, dict) and set(mapping) == set(SCENARIOS), "quarter bridge requires all scenario parameter paths")
        for scenario, ids in (mapping or {}).items():
            require(isinstance(ids, list) and bool(ids) and len(ids) == len(set(ids)), "quarter bridge parameter IDs must be unique")
            for pid in ids:
                require(pid in parameters and pid in used, "quarter bridge requires a used forecast parameter")
                p = parameters[pid]
                require(p["dimension"] == "revenue" and p.get("measurement_period") == period and p["period"] == f"FY{year}" and p.get("scenario") in {scenario, "all", "shared", None}, "quarter bridge parameter period/scenario/dimension mismatch")
                require(p["currency"] == data["currency"] and p["scale"] == data["unit"], "quarter bridge currency/scale mismatch")
                require(bool(p.get("claim_ids")), "quarter bridge requires checked input claims")
            components = scope_components(data, parameters, target["scope"], scenario, year)
            members = set().union(*components.values()) if components else set()
            require(set(ids) <= members and all(set(ids) & refs for refs in components.values()),
                    "quarter bridge target scope must match its native component ancestry")
    else:
        require(target["measurement_basis"] == "annual_period", "annual comparison measurement basis mismatch")
    require(set(spec) == allowed, "typed comparison fields are not exact")
    raw_point = target.get("raw_target_value")
    two_ended = raw_point is None and (
        target.get("raw_target_value_low") is not None
        or target.get("raw_target_value_high") is not None
    )
    if two_ended and not range_comparison_is_defined(target["comparison"]):
        require(
            not modeled,
            f"{OPERATOR_RANGE_INCOMPATIBLE}: comparison {target['comparison']} names one "
            f"threshold but the typed target range names two; use approximately or a point target",
        )
    low, high = normalize_target_bounds(target, data) if modeled else (None, None)
    if modeled and low == high:
        require(target.get("comparison_value") is not None and math.isclose(finite_number(target["comparison_value"], "comparison_value"), low, rel_tol=1e-9, abs_tol=1e-9), "typed comparison normalization mismatch")
    else:
        require(target.get("comparison_value") is None, "range comparison cannot carry a synthetic point target")
    require(treatment in {"modeled_scenario", "scenario_boundary", "independent_benchmark", "unmodeled_data_gap", "out_of_horizon"}, "unsupported typed target treatment")
    if not modeled:
        require(not target["mapped_scenarios"], "unmodeled typed target cannot claim mapped scenarios")
    if modeled:
        require(year in data["forecast_years"], "typed benchmark must be inside forecast horizon")
        require(target["perimeter_status"] in {"matched", "reconciled"} and target["scope"]["type"] in {"company", "segment"}, "typed comparison perimeter remains unresolved")
        require(bool(target["mapped_parameter_ids"]) and bool(target["mapped_scenarios"]), "typed comparison requires mapped parameters/scenarios")
    source_ids = [claims[cid]["source_id"] for cid in target["claim_ids"]]
    if treatment == "independent_benchmark":
        require(set(target["mapped_scenarios"]) == set(SCENARIOS), "independent comparison requires all scenarios")
        require(bool(target.get("benchmark_rationale")), "independent comparison requires benchmark rationale")
        checked = validate_claim_ids(target.get("benchmark_claim_ids"), claims, "management_target", target["target_id"], target["target_id"], "rationale_support")
        source_ids.extend(c["source_id"] for c in checked)
    normalized = deepcopy(target)
    if metric == "year_over_year_growth" and spec.get("base_period") is None:
        normalized["comparison_status"] = "not_comparable"
        normalized["comparison_reason"] = "base_period_unknown"
    elif two_ended and not range_comparison_is_defined(target["comparison"]):
        normalized["comparison_status"] = "not_comparable"
        normalized["comparison_reason"] = "operator_range_incompatible"
    normalized["source_ids"] = list(dict.fromkeys(source_ids))
    normalized["source_publication_dates"] = {sid: sources[sid]["published_date"] for sid in normalized["source_ids"]}
    return normalized


def _annual_value(result, target, scenario, period):
    if period is None:
        return None
    year = period[2:]
    if target["scope"]["type"] == "company":
        if int(year) == result["base_year"]:
            return result["base_revenue"]
        return result["consolidated_forecast"][scenario]["annual_revenue"].get(year)
    segment = next(item for item in result["segments"] if item["name"] == target["scope"]["name"])
    if int(year) == result["base_year"]:
        return segment["base_revenue"]
    output = segment["scenarios"][scenario]
    return output.get("effective_revenue", output["recognized_revenue"]).get(year)


def compare_target_measurement(target: dict, result: dict, parameters: dict | None = None) -> dict:
    spec = target["comparison_basis"]
    metric = spec["metric_kind"]
    index = parameters if parameters is not None else {p["parameter_id"]: p for p in result["parameter_trace"]}
    tolerance = finite_number(target.get("comparison_tolerance", 0.01), "comparison_tolerance")
    require(0 <= tolerance <= 0.25, "comparison tolerance outside 0..0.25")
    comparisons = {}
    if target["treatment"] not in {"modeled_scenario", "scenario_boundary", "independent_benchmark"}:
        return comparisons
    low, high = normalize_target_bounds(target, result)
    for scenario in target.get("mapped_scenarios", []):
        denominator = None
        numerator = None
        reason = None
        if metric == "quarterly_revenue_level":
            ids = spec["scenario_parameter_ids"][scenario]
            observed = math.fsum(float(index[pid]["value"]) for pid in ids)
        else:
            numerator = _annual_value(result, target, scenario, spec["period"])
            observed = numerator
            if numerator is None:
                reason = "missing_numerator_period"
        if metric == "year_over_year_growth":
            denominator = _annual_value(result, target, scenario, spec.get("base_period"))
            if numerator is None:
                reason = "missing_numerator_period"
            elif denominator is None:
                reason = "missing_base_period"
            elif denominator <= 0:
                reason = "nonpositive_base_revenue"
            observed = None if reason else numerator / denominator - 1
        row = {"metric_kind": metric, "period": spec["period"], "unit": "ratio" if metric == "year_over_year_growth" else f"{result['currency']} {result['unit']}",
               "modeled_value": observed, "target_value": low if low == high else None,
               "target_low": low, "target_high": high, "comparison": target["comparison"],
               "comparison_status": "not_comparable" if observed is None else "comparable", "reason": reason,
               "meets_target": None if observed is None else meets_target(observed, low, high, target["comparison"], tolerance),
               "attainment_ratio": attainment_ratio(observed, low, high)}
        if metric == "year_over_year_growth":
            row.update(base_value=denominator, base_period=spec.get("base_period"), numerator_value=numerator,
                       difference_percentage_points=None if observed is None or low != high else (observed - low) * 100)
            row["derived_revenue_benchmark"] = None if reason or denominator is None or low != high else {
                "origin": "analyst_derived", "value": denominator * (1 + low), "unit": f"{result['currency']} {result['unit']}",
                "formula": "scenario_base_revenue * (1 + normalized_growth_target)",
                "difference": None if numerator is None else numerator - denominator * (1 + low)}
        else:
            row["difference"] = None if observed is None or low != high else observed - low
        if row["attainment_ratio"] is None and observed is not None and low == high and low < 0:
            # A negative point target is genuinely comparable; only the ratio is
            # withheld because observed/low would flip better and worse. The
            # signed difference, the status and the verbatim statement carry it.
            row["reason"] = ATTAINMENT_RATIO_WITHHELD
        if target["treatment"] in {"modeled_scenario", "scenario_boundary"}:
            require(row["meets_target"] is True, "mapped scenario does not satisfy typed management target")
        comparisons[scenario] = row
    return comparisons
