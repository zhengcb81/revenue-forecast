"""One read-only visitor over RF's native parameter uses and derived ancestry.

Visitors describe inputs that the existing calculators consume. Validation and
arithmetic remain with their owners; this module never flattens different
scenarios, guesses a stock is revenue, or creates another computation engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Iterator

from contracts.constants import SCENARIOS
from model_registry import MODEL_REGISTRY


@dataclass(frozen=True)
class ParameterUse:
    parameter_id: str
    segment: str
    scenario: str
    input_year: int | None
    model: str
    driver: str
    output: str
    kind: str
    recognized_year: int | None = None

    @property
    def year(self) -> int | None:
        """Compatibility view of the explicitly INPUT clock, never an output cell."""
        return self.input_year

    def formula_ref(self) -> dict[str, str]:
        result = {"segment": self.segment, "scenario": self.scenario, "model": self.model,
                  "driver": self.driver, "output": self.output}
        if self.input_year is not None and self.recognized_year != self.input_year:
            result["input_period"] = f"FY{self.input_year}"
            result["recognized_period"] = f"FY{self.recognized_year}"
        return result


def expand_derived_inputs(parameter_ids: Iterable[str], parameters: dict[str, dict[str, Any]]) -> set[str]:
    """Follow only actual derived-fact inputs; iterative and cycle-bounded."""
    expanded = set(parameter_ids)
    pending = list(expanded)
    while pending:
        parameter = parameters.get(pending.pop())
        if not parameter or parameter.get("kind") != "derived_fact":
            continue
        for input_id in parameter.get("input_parameter_ids", []):
            if input_id not in expanded:
                expanded.add(input_id)
                pending.append(input_id)
    return expanded


def _series(ids: Any, years: list[int], *, count: int | None = None) -> Iterator[tuple[int | None, str]]:
    # A staged input may bind source claims before its fiscal schedule is built.
    # Preserve structural uses without inventing a fiscal cell. Formal input
    # validation still requires and checks the complete schedule.
    if not years and isinstance(ids, list):
        for pid in ids:
            if isinstance(pid, str):
                yield None, pid
        return
    expected = len(years) if count is None else count
    if not isinstance(ids, list) or len(ids) != expected or expected > len(years):
        return
    for year, pid in zip(years, ids):
        if isinstance(pid, str):
            yield year, pid


def series_parameter_ids(mapping: Any, scenario: str, year: int, years: list[int]) -> list[str]:
    ids = mapping.get(scenario, []) if isinstance(mapping, dict) else []
    return [pid for observed_year, pid in _series(ids, years) if observed_year == year]


def segment_parameter_uses(data: dict[str, Any], segment: dict[str, Any], scenario: str) -> Iterator[ParameterUse]:
    """Direct native input uses with separate input and recognized clocks."""
    years = data.get("forecast_years", [])
    config = segment.get("scenarios", {}).get(scenario, {})
    name, model = segment.get("name", ""), config.get("model", "")
    recognition = segment.get("recognition", {})
    lag = recognition.get("lag_years", 0) if isinstance(recognition, dict) and recognition.get("mode") == "lagged_activity" else 0
    lag = lag if type(lag) is int and lag > 0 else 0
    drivers = config.get("driver_parameter_ids", {})
    if isinstance(drivers, dict):
        for driver, ids in drivers.items():
            for year, pid in _series(ids, years):
                recognized_year = year + lag if year is not None else None
                output = "modeled_activity" if lag else "recognized_revenue"
                if years and recognized_year is not None and recognized_year > years[-1]:
                    output = "unrecognized_tail_activity"
                yield ParameterUse(pid, name, scenario, year, model, driver,
                                   output, "model_driver", recognized_year)
    recognition = segment.get("recognition", {})
    if not isinstance(recognition, dict):
        return
    if recognition.get("timing") == "over_time":
        fields = [("progress_parameter_ids", "progress", None)]
    elif recognition.get("mode") == "lagged_activity":
        lag = recognition.get("lag_years")
        if type(lag) is not int or lag < 1:
            return
        fields = [("carry_in_parameter_ids", "carry_in", lag)]
    else:
        return
    for field, driver, count in fields:
        mapping = recognition.get(field, {})
        ids = mapping.get(scenario, []) if isinstance(mapping, dict) else []
        for year, pid in _series(ids, years, count=count):
            yield ParameterUse(pid, name, scenario, year, model, driver,
                               "recognized_revenue", "recognition", year)


def _constraint_uses(data: dict[str, Any], constraint: dict[str, Any], scenario: str) -> Iterator[ParameterUse]:
    years = data.get("forecast_years", [])
    kind, identifier = constraint.get("type"), constraint.get("constraint_id", "")
    groups = []
    if kind == "sum_cap":
        for segment in constraint.get("segments", []):
            groups.append((segment, constraint.get("scenario_parameter_ids", {}), "cap"))
            if constraint.get("allocation") == "fixed_weights":
                groups.append((segment, constraint.get("weight_parameter_ids", {}).get(segment, {}), "weight"))
    elif kind == "linked_ratio":
        groups.append((constraint.get("target_segment", ""), constraint.get("scenario_parameter_ids", {}), "ratio"))
    elif kind == "elimination":
        groups.extend((segment, mapping, "elimination") for segment, mapping in
                      constraint.get("segment_adjustment_parameter_ids", {}).items())
    for segment, mapping, role in groups:
        if not isinstance(mapping, dict):
            continue
        for year, pid in _series(mapping.get(scenario, []), years):
            yield ParameterUse(pid, segment, scenario, year, "revenue_constraint",
                               f"{identifier}:{role}", "effective_revenue", "constraint", year)


def parameter_uses(data: dict[str, Any], scenario: str | None = None) -> Iterator[ParameterUse]:
    scenarios = (scenario,) if scenario is not None else SCENARIOS
    years = data.get("forecast_years", [])
    for selected in scenarios:
        for segment in data.get("segments", []):
            if isinstance(segment, dict):
                yield from segment_parameter_uses(data, segment, selected)
        for adjustment in data.get("forecast_adjustments", []):
            if not isinstance(adjustment, dict):
                continue
            mapping = adjustment.get("scenario_parameter_ids", {})
            if not isinstance(mapping, dict):
                continue
            for year, pid in _series(mapping.get(selected, []), years):
                yield ParameterUse(pid, data.get("company_name", ""), selected, year,
                    "forecast_adjustment", adjustment.get("name", ""),
                    "consolidated_revenue", "forecast_adjustment", year)
        for constraint in data.get("revenue_constraints", []):
            if isinstance(constraint, dict):
                yield from _constraint_uses(data, constraint, selected)


def parameter_formula_refs(data: dict[str, Any], parameter_id: str,
                           parameters: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    """Trace a true ancestry use once; metadata references never enter this visitor."""
    refs = []
    seen = set()
    ancestors: dict[str, set[str]] = {}
    for use in parameter_uses(data):
        if use.parameter_id not in ancestors:
            ancestors[use.parameter_id] = expand_derived_inputs([use.parameter_id], parameters)
        if parameter_id not in ancestors[use.parameter_id]:
            continue
        ref = use.formula_ref()
        key = tuple(ref.items())
        if key not in seen:
            seen.add(key)
            refs.append(ref)
    direct_scopes = {(ref["segment"], ref["scenario"]) for ref in refs}
    for scenario in SCENARIOS:
        for segment, cells in effective_segment_dependencies(data, scenario).items():
            if (segment, scenario) in direct_scopes:
                continue
            if any(parameter_id in expand_derived_inputs(e.value_parameter_ids, parameters)
                   for e in cells.values()):
                refs.append({"segment": segment, "scenario": scenario, "model": "native_effect",
                             "driver": "effective_revenue_path", "output": "effective_revenue"})
    return refs


@dataclass(frozen=True)
class SegmentDependency:
    """Current output-cell value and branch-control roots remain distinct."""
    value_parameter_ids: frozenset[str]
    control_parameter_ids: frozenset[str] = frozenset()


def _segment_recognized_dependencies(data: dict[str, Any], segment: dict[str, Any],
                                    scenario: str) -> dict[int, SegmentDependency]:
    years = data.get("forecast_years", [])
    uses = list(segment_parameter_uses(data, segment, scenario))
    spec = MODEL_REGISTRY.get(segment.get("scenarios", {}).get(scenario, {}).get("model"))
    modeled = {}
    for year in years:
        roots = {u.parameter_id for u in uses if u.kind == "model_driver" and u.input_year == year}
        if spec is not None:
            roots.update(u.parameter_id for u in uses if u.kind == "model_driver"
                         and u.driver in spec.cumulative_drivers and u.input_year is not None
                         and u.input_year <= year)
            if spec.consumes_base_revenue and isinstance(segment.get("base_revenue_parameter_id"), str):
                roots.add(segment["base_revenue_parameter_id"])
        modeled[year] = roots
    recognition = segment.get("recognition", {})
    lag = recognition.get("lag_years", 0) if recognition.get("mode") == "lagged_activity" else 0
    lag = lag if type(lag) is int and lag > 0 else 0
    result = {}
    for offset, year in enumerate(years):
        if lag:
            roots = modeled[years[offset - lag]] if offset >= lag else set()
        else:
            roots = modeled[year]
        roots = roots | {u.parameter_id for u in uses if u.kind == "recognition" and u.input_year == year}
        result[year] = SegmentDependency(frozenset(roots))
    return result


def _constraint_effects(data: dict[str, Any], dependencies: dict[str, dict[int, SegmentDependency]],
                        constraint: dict[str, Any], scenario: str) -> None:
    """Propagate the real constraint topology in declaration/application order."""
    years = data.get("forecast_years", [])
    kind = constraint.get("type")
    for year in years:
        if kind == "sum_cap":
            names = constraint.get("segments", [])
            before = {name: dependencies[name][year] for name in names if name in dependencies}
            if len(before) != len(names):
                continue
            value_roots = set().union(*(e.value_parameter_ids for e in before.values()))
            controls = set().union(*(e.control_parameter_ids for e in before.values()))
            cap = set(series_parameter_ids(constraint.get("scenario_parameter_ids"), scenario, year, years))
            for name in names:
                if constraint.get("allocation") == "fixed_weights":
                    weights = set(series_parameter_ids(constraint.get("weight_parameter_ids", {}).get(name), scenario, year, years))
                    # Own unbound revenue or own fixed allocation amount; peer
                    # revenue influences the activation condition, not this amount.
                    values = set(before[name].value_parameter_ids) | cap | weights
                    control = controls | value_roots | cap
                else:
                    # Proportional allocation genuinely uses every participating
                    # segment amount in the shared denominator; no foreign segment.
                    values = value_roots | cap
                    control = controls
                dependencies[name][year] = SegmentDependency(frozenset(values), frozenset(control))
        elif kind == "linked_ratio":
            source, target = constraint.get("source_segment"), constraint.get("target_segment")
            if source not in dependencies or target not in dependencies:
                continue
            a, b = dependencies[source][year], dependencies[target][year]
            values = set(a.value_parameter_ids) | set(series_parameter_ids(
                constraint.get("scenario_parameter_ids"), scenario, year, years))
            controls = set(a.control_parameter_ids)
            if constraint.get("relation") == "maximum":
                values |= b.value_parameter_ids
                controls |= b.control_parameter_ids
            dependencies[target][year] = SegmentDependency(frozenset(values), frozenset(controls))
        elif kind == "elimination":
            for name, mapping in constraint.get("segment_adjustment_parameter_ids", {}).items():
                if name in dependencies:
                    old = dependencies[name][year]
                    ids = set(series_parameter_ids(mapping, scenario, year, years))
                    dependencies[name][year] = SegmentDependency(old.value_parameter_ids | ids,
                                                                  old.control_parameter_ids)


def effective_segment_dependencies(data: dict[str, Any], scenario: str) -> dict[str, dict[int, SegmentDependency]]:
    """ID topology of recognized/effective cells, not a second amount calculator.

    max/cap branches retain possible value operands; fixed-allocation activation
    inputs are separate control dependencies. No number, source or scenario is
    inferred, and original engine arithmetic remains the sole amount authority.
    """
    result = {s["name"]: _segment_recognized_dependencies(data, s, scenario)
              for s in data.get("segments", []) if isinstance(s, dict) and isinstance(s.get("name"), str)}
    for constraint in data.get("revenue_constraints", []):
        if isinstance(constraint, dict):
            _constraint_effects(data, result, constraint, scenario)
    return result
