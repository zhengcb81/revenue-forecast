"""Relationships over the existing native parameter/segment/driver DAG.

This module preserves scope, scenario and period when following IDs. It does
not revalidate sources, infer business semantics or create another registry.
"""
from __future__ import annotations
from typing import Any
from forecast.dependencies import effective_segment_dependencies, expand_derived_inputs, segment_parameter_uses, series_parameter_ids


def ancestry(parameter_ids, parameters):
    return expand_derived_inputs(parameter_ids, parameters)


def _period_ids(mapping, scenario, year, years):
    return series_parameter_ids(mapping, scenario, year, years)


def segment_roots(data, segment, scenario, year):
    """Direct INPUT-clock roots (activity or recognition inputs), not final cells."""
    return [use.parameter_id for use in segment_parameter_uses(data, segment, scenario)
            if use.year == year]


def direct_parameter_cells(
    data: dict[str, Any], parameter_id: str, *, scope: str, scenario: str
) -> list[tuple[str, str, str]]:
    """Actual direct native INPUT-clock consumers, without flattening a bridge.

    A downstream derived FY2027 node may legitimately consume an FY2026
    intermediate. Only a direct root claims to describe that cell itself;
    preserve explicit cross-period ancestry rather than equating all dates.
    """
    cells = []
    for segment in data.get("segments", []):
        if scope not in {data.get("company_name"), segment["name"]}:
            continue
        used_years = {u.input_year for u in segment_parameter_uses(data, segment, scenario)
                      if u.parameter_id == parameter_id}
        cells.extend((segment["name"], scenario, f"FY{year}")
                     for year in data["forecast_years"] if year in used_years)
    return cells


def segment_ancestry(data, parameters, segment, scenario, year):
    cells = effective_segment_dependencies(data, scenario).get(segment["name"], {})
    roots = cells[year].value_parameter_ids if year in cells else set()
    return ancestry(roots, parameters)


def scope_components(data, parameters, scope, scenario, year):
    segments = [s for s in data.get("segments", [])
                if scope["type"] == "company" or s["name"] == scope["name"]]
    graph = effective_segment_dependencies(data, scenario)
    components = {s["name"]: ancestry(graph[s["name"]][year].value_parameter_ids, parameters)
                  for s in segments if year in graph[s["name"]]}
    if scope["type"] == "company":
        for adjustment in data.get("forecast_adjustments", []):
            roots = _period_ids(adjustment.get("scenario_parameter_ids", {}), scenario, year, data["forecast_years"])
            if roots:
                components["adjustment:" + adjustment["name"]] = ancestry(roots, parameters)
    return components


def parameter_scopes(data, parameters, pid):
    scopes = set()
    scenarios = {scenario for segment in data.get("segments", [])
                 for scenario in segment.get("scenarios", {})}
    for scenario in scenarios:
        graph = effective_segment_dependencies(data, scenario)
        for name, cells in graph.items():
            if any(pid in ancestry(cell.value_parameter_ids, parameters)
                   for cell in cells.values()):
                scopes.add(name)
    return scopes


def claim_parameter_anchors(claim, parameters, drivers):
    if claim["target_type"] == "parameter":
        pid = claim["target_id"]
        if pid in parameters and claim["claim_id"] in parameters[pid].get("claim_ids", []):
            return {pid}
    elif claim["target_type"] == "growth_driver":
        roots = set()
        for driver in drivers.values():
            if any(n.get("evidence_id") == claim["target_id"]
                   and claim["claim_id"] in n.get("claim_ids", [])
                   for n in driver.get("evidence_nodes", [])):
                roots.update(driver.get("parameter_ids", []))
        return ancestry(roots, parameters)
    return set()


def observation_binding(row, claim, data, parameters, drivers):
    role = claim["evidence_role"]
    if role in {"counterevidence", "counter_comparison", "peer_analogy"}:
        return "related_not_positive_support"
    anchors = claim_parameter_anchors(claim, parameters, drivers)
    if not anchors and claim["target_type"] == "historical_revenue" and role == "history_base":
        return "historical_context"
    if not anchors:
        return "unverified_claim_binding"
    from contracts.evidence import require
    for pid in row["parameter_ids"]:
        require(bool(anchors & ancestry([pid], parameters)), "operating observation parameter binding mismatch")
    for driver_id in row["driver_ids"]:
        require(bool(anchors & ancestry(drivers[driver_id].get("parameter_ids", []), parameters)),
                "operating observation driver binding mismatch")
    status = "bound"
    for pid in row["parameter_ids"]:
        parameter = parameters[pid]
        if row["period"] != parameter.get("measurement_period", parameter["period"]):
            require(role != "mechanism_direction", "operating observation period binding mismatch")
            status = "unverified_period"
        scopes = parameter_scopes(data, parameters, pid)
        if row["scope"] not in {data.get("company_name"), *scopes}:
            if row["scope"] in {s["name"] for s in data.get("segments", [])} and scopes:
                require(role != "mechanism_direction", "operating observation scope binding mismatch")
            status = "unverified_scope"
    return status
