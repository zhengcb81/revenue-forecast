"""Extracted from revenue_core.py during the R9 split (behavior-locked by tests/test_golden_behavior_lock.py)."""

from __future__ import annotations

import math
import re
from typing import Any, Iterable, Mapping, Sequence

import copy
from datetime import date

from contracts.constants import (
    MANAGEMENT_COMMUNICATION_CATEGORIES,
    MANAGEMENT_COMMUNICATION_STATUSES,
    MANAGEMENT_TARGET_COMPARISONS,
    MANAGEMENT_TARGET_MEASUREMENT_BASES,
    MANAGEMENT_TARGET_PERIMETERS,
    MANAGEMENT_TARGET_TREATMENTS,
    SCENARIOS,
)
from contracts.evidence import (
    ForecastInputError,
    canonical_sha256,
    finite_number,
    parse_iso_date,
    period_year,
    require,
    text_sha256,
    validate_claim_ids,
)
from forecast.calc import collect_parameter_roles


def validate_management_target_coverage(
    data: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
    parameter_index: dict[str, dict[str, Any]],
    claim_index: dict[str, dict[str, Any]],
    as_of: date,
) -> dict[str, Any]:
    """Validate official communication coverage and every material forward revenue target."""
    coverage = data.get("management_communication_coverage")
    require(
        isinstance(coverage, list), "management_communication_coverage must be a list"
    )
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
        require(
            category in MANAGEMENT_COMMUNICATION_CATEGORIES,
            f"unsupported management communication category: {category}",
        )
        require(
            category not in normalized_coverage,
            f"duplicate management communication category: {category}",
        )
        status = record.get("status")
        require(
            status in MANAGEMENT_COMMUNICATION_STATUSES,
            f"unsupported management communication status: {category}/{status}",
        )
        conclusion = record.get("conclusion")
        require(
            isinstance(conclusion, str) and conclusion.strip(),
            f"{category}.conclusion is required",
        )
        source_ids = record.get("source_ids", [])
        target_ids = record.get("material_revenue_target_ids", [])
        require(
            isinstance(source_ids, list) and len(source_ids) == len(set(source_ids)),
            f"{category}.source_ids must be unique",
        )
        require(
            isinstance(target_ids, list) and len(target_ids) == len(set(target_ids)),
            f"{category}.material_revenue_target_ids must be unique",
        )
        require(
            all(isinstance(item, str) and item.strip() for item in target_ids),
            f"{category}.material_revenue_target_ids contains invalid IDs",
        )
        for source_id in source_ids:
            require(
                source_id in source_index,
                f"unknown management communication source_id: {source_id}",
            )
        checked_date = parse_iso_date(
            record.get("checked_date"), f"{category}.checked_date"
        )
        require(
            checked_date <= as_of,
            f"management communication checked after as_of_date: {category}",
        )
        rationale = record.get("rationale")
        if status == "checked":
            require(
                bool(source_ids),
                f"checked management communication requires source_ids: {category}",
            )
        else:
            require(
                not source_ids,
                f"{status} management communication cannot contain source_ids: {category}",
            )
            require(
                not target_ids,
                f"{status} management communication cannot contain target_ids: {category}",
            )
            require(
                isinstance(rationale, str) and rationale.strip(),
                f"{status} management communication requires rationale: {category}",
            )
            if status == "not_available":
                require(
                    isinstance(record.get("search_description"), str)
                    and record["search_description"].strip(),
                    f"not_available communication requires search_description: {category}",
                )
                search_event = record.get("search_event")
                require(
                    isinstance(search_event, dict),
                    f"not_available communication requires a machine-generated search_event: {category}",
                )
                require(
                    isinstance(search_event.get("query_scope"), str)
                    and search_event["query_scope"].strip(),
                    f"search_event.query_scope is required: {category}",
                )
                require(
                    isinstance(search_event.get("query_time"), str)
                    and search_event["query_time"].strip(),
                    f"search_event.query_time is required: {category}",
                )
                require(
                    isinstance(search_event.get("event_ids"), list)
                    and bool(search_event["event_ids"]),
                    f"search_event.event_ids must be non-empty: {category}",
                )
                require(
                    isinstance(search_event.get("generated_by"), str)
                    and search_event["generated_by"].strip(),
                    f"search_event.generated_by is required: {category}",
                )
                require(
                    isinstance(search_event.get("event_sha256"), str)
                    and search_event["event_sha256"].strip(),
                    f"search_event.event_sha256 is required: {category}",
                )
            if status == "not_applicable":
                require(
                    isinstance(record.get("reason_code"), str)
                    and record["reason_code"].strip(),
                    f"not_applicable communication requires reason_code: {category}",
                )
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
    segment_names = {
        segment.get("name")
        for segment in data.get("segments", [])
        if isinstance(segment, dict)
    }
    normalized_targets: dict[str, dict[str, Any]] = {}
    gap_messages: list[str] = []
    for position, target in enumerate(targets):
        prefix = f"management_targets[{position}]"
        require(isinstance(target, dict), f"{prefix} must be an object")
        target_id = target.get("target_id")
        require(
            isinstance(target_id, str) and target_id.strip(),
            f"{prefix}.target_id is required",
        )
        require(
            target_id not in normalized_targets,
            f"duplicate management target: {target_id}",
        )
        for field in (
            "statement",
            "metric_name",
            "metric_definition",
            "target_period",
            "raw_unit",
            "raw_currency",
            "raw_scale",
            "measurement_rationale",
            "perimeter_notes",
            "rationale",
        ):
            require(
                isinstance(target.get(field), str) and target[field].strip(),
                f"{target_id}.{field} is required",
            )
        raw_value = finite_number(
            target.get("raw_target_value"), f"{target_id}.raw_target_value"
        )
        require(raw_value >= 0, f"management target cannot be negative: {target_id}")
        measurement_basis = target.get("measurement_basis")
        require(
            measurement_basis in MANAGEMENT_TARGET_MEASUREMENT_BASES,
            f"invalid management target measurement basis: {target_id}",
        )
        measurement_periods = target.get("measurement_periods")
        require(
            isinstance(measurement_periods, list)
            and len(measurement_periods) == len(set(measurement_periods)),
            f"invalid management target measurement periods: {target_id}",
        )
        measurement_years = [
            period_year(period, f"{target_id}.measurement_periods")
            for period in measurement_periods
        ]
        require(
            measurement_years == sorted(measurement_years),
            f"management target measurement periods must be ordered: {target_id}",
        )
        if measurement_basis in {"annual_period", "run_rate_at_period_end"}:
            require(
                len(measurement_years) == 1,
                f"single-period management target requires exactly one measurement period: {target_id}",
            )
        elif measurement_basis == "cumulative_periods":
            require(
                len(measurement_years) >= 2,
                f"cumulative management target requires at least two measurement periods: {target_id}",
            )
            require(
                measurement_years
                == list(range(measurement_years[0], measurement_years[-1] + 1)),
                f"cumulative management target periods must be contiguous: {target_id}",
            )
        else:
            require(
                not measurement_years,
                f"ambiguous management target cannot claim measurement periods: {target_id}",
            )
        materiality = target.get("materiality")
        require(
            materiality in {"material", "contextual"},
            f"invalid management target materiality: {target_id}",
        )
        commitment_strength = target.get("commitment_strength")
        require(
            commitment_strength in {"guidance", "goal", "aspiration", "capacity_plan"},
            f"invalid management target commitment strength: {target_id}",
        )
        perimeter_status = target.get("perimeter_status")
        require(
            perimeter_status in MANAGEMENT_TARGET_PERIMETERS,
            f"invalid management target perimeter: {target_id}",
        )
        treatment = target.get("treatment")
        require(
            treatment in MANAGEMENT_TARGET_TREATMENTS,
            f"invalid management target treatment: {target_id}",
        )
        comparison = target.get("comparison")
        require(
            comparison in MANAGEMENT_TARGET_COMPARISONS,
            f"invalid management target comparison: {target_id}",
        )
        scope = target.get("scope")
        require(
            isinstance(scope, dict)
            and scope.get("type") in {"company", "segment", "custom"},
            f"invalid management target scope: {target_id}",
        )
        scope_name = scope.get("name")
        require(
            isinstance(scope_name, str) and scope_name.strip(),
            f"management target scope name is required: {target_id}",
        )
        if scope["type"] == "segment":
            require(
                scope_name in segment_names,
                f"unknown management target segment: {target_id}/{scope_name}",
            )

        claim_ids = target.get("claim_ids")
        linked_claims = validate_claim_ids(
            claim_ids,
            claim_index,
            "management_target",
            target_id,
            target_id,
            "exact_value",
        )
        source_ids = []
        for linked in linked_claims:
            extracted = finite_number(
                linked.get("extracted_value"), f"{linked['claim_id']}.extracted_value"
            )
            require(
                math.isclose(extracted, raw_value, rel_tol=0, abs_tol=1e-9),
                f"management target claim value mismatch: {target_id}",
            )
            require(
                linked.get("unit") == target["raw_unit"],
                f"management target claim unit mismatch: {target_id}",
            )
            require(
                linked.get("period") == target["target_period"],
                f"management target claim period mismatch: {target_id}",
            )
            source_ids.append(linked["source_id"])

        mapped_ids = target.get("mapped_parameter_ids", [])
        mapped_scenarios = target.get("mapped_scenarios", [])
        require(
            isinstance(mapped_ids, list) and len(mapped_ids) == len(set(mapped_ids)),
            f"invalid mapped_parameter_ids: {target_id}",
        )
        require(
            isinstance(mapped_scenarios, list)
            and len(mapped_scenarios) == len(set(mapped_scenarios)),
            f"invalid mapped_scenarios: {target_id}",
        )
        require(
            set(mapped_scenarios) <= set(SCENARIOS),
            f"invalid mapped scenario: {target_id}",
        )
        for parameter_id in mapped_ids:
            require(
                parameter_id in parameter_index,
                f"unknown management target parameter: {target_id}/{parameter_id}",
            )
            require(
                parameter_id in roles["forecast"],
                f"management target parameter is not used by the forecast: {target_id}/{parameter_id}",
            )

        within_horizon = bool(measurement_years) and set(measurement_years) <= set(
            data["forecast_years"]
        )
        comparable = (
            measurement_basis != "ambiguous"
            and perimeter_status in {"matched", "reconciled"}
            and scope["type"] in {"company", "segment"}
        )
        comparison_value = target.get("comparison_value")
        if comparable:
            comparison_value = finite_number(
                comparison_value, f"{target_id}.comparison_value"
            )
            require(
                comparison_value >= 0,
                f"management target comparison value cannot be negative: {target_id}",
            )
            require(
                target.get("comparison_currency") == data["currency"],
                f"management target comparison currency mismatch: {target_id}",
            )
            require(
                target.get("comparison_scale") == data["unit"],
                f"management target comparison scale mismatch: {target_id}",
            )
            require(
                isinstance(target.get("normalization_rationale"), str)
                and target["normalization_rationale"].strip(),
                f"management target normalization rationale is required: {target_id}",
            )
        else:
            require(
                comparison_value is None,
                f"non-comparable management target cannot contain comparison_value: {target_id}",
            )

        if measurement_basis == "ambiguous":
            require(
                treatment == "unmodeled_data_gap",
                f"measurement-ambiguous target must remain an unmodeled data gap: {target_id}",
            )
            require(
                not mapped_ids and not mapped_scenarios,
                f"measurement-ambiguous target cannot claim scenario mapping: {target_id}",
            )

        if treatment in {"modeled_scenario", "scenario_boundary"}:
            require(
                within_horizon,
                f"modeled management target must be inside forecast horizon: {target_id}",
            )
            require(
                comparable,
                f"modeled management target requires matched or reconciled perimeter: {target_id}",
            )
            require(
                bool(mapped_ids) and bool(mapped_scenarios),
                f"modeled management target requires mapped parameters and scenarios: {target_id}",
            )
        elif treatment == "out_of_horizon":
            require(
                bool(measurement_years)
                and max(measurement_years) > max(data["forecast_years"]),
                f"out_of_horizon target must extend after forecast horizon: {target_id}",
            )
            require(
                not mapped_ids and not mapped_scenarios,
                f"out_of_horizon target cannot claim scenario mapping: {target_id}",
            )
            gap_messages.append(
                f"management_target:{target_id}: target period {target['target_period']} is outside the forecast horizon"
            )
        else:
            require(
                not mapped_scenarios,
                f"unmodeled management target cannot claim mapped scenarios: {target_id}",
            )
            gap_messages.append(f"management_target:{target_id}: {treatment}")

        if materiality == "material" and within_horizon and comparable:
            require(
                treatment in {"modeled_scenario", "scenario_boundary"},
                f"material in-horizon comparable target must enter a scenario: {target_id}",
            )
        if perimeter_status == "mismatch":
            require(
                treatment in {"unmodeled_data_gap", "out_of_horizon"},
                f"perimeter-mismatched target cannot be modeled directly: {target_id}",
            )

        normalized = copy.deepcopy(target)
        normalized["raw_target_value"] = raw_value
        normalized["measurement_periods"] = list(measurement_periods)
        normalized["source_ids"] = list(dict.fromkeys(source_ids))
        if comparable:
            normalized["comparison_value"] = float(comparison_value)
        normalized_targets[target_id] = normalized

    require(
        referenced_target_ids == set(normalized_targets),
        "management communication target IDs must match management_targets exactly",
    )
    records = [
        normalized_coverage[category]
        for category in MANAGEMENT_COMMUNICATION_CATEGORIES
    ]
    target_records = [normalized_targets[target["target_id"]] for target in targets]
    return {
        "communications": records,
        "targets": target_records,
        "counts": {
            "communications_checked": sum(
                record["status"] == "checked" for record in records
            ),
            "targets_total": len(target_records),
            "targets_modeled": sum(
                record["treatment"] in {"modeled_scenario", "scenario_boundary"}
                for record in target_records
            ),
            "targets_unmodeled": sum(
                record["treatment"] not in {"modeled_scenario", "scenario_boundary"}
                for record in target_records
            ),
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
            tolerance = finite_number(
                target.get("comparison_tolerance", 0.01),
                f"{target['target_id']}.comparison_tolerance",
            )
            require(
                0 <= tolerance <= 0.25,
                f"management target comparison_tolerance outside 0..0.25: {target['target_id']}",
            )
            for scenario in target["mapped_scenarios"]:
                if target["scope"]["type"] == "company":
                    revenue_path = result["consolidated_forecast"][scenario][
                        "annual_revenue"
                    ]
                else:
                    scenario_output = segment_index[target["scope"]["name"]][
                        "scenarios"
                    ][scenario]
                    revenue_path = scenario_output.get(
                        "effective_revenue", scenario_output["recognized_revenue"]
                    )
                period_values = {
                    period: float(revenue_path[period[2:]])
                    for period in measurement_periods
                }
                if target["measurement_basis"] == "cumulative_periods":
                    observed = sum(period_values.values())
                else:
                    observed = period_values[measurement_periods[0]]
                if target["comparison"] == "at_least":
                    meets = observed >= target_value * (1 - tolerance)
                elif target["comparison"] == "at_most":
                    meets = observed <= target_value * (1 + tolerance)
                else:
                    meets = math.isclose(
                        observed,
                        target_value,
                        rel_tol=tolerance,
                        abs_tol=max(1.0, abs(target_value)) * tolerance,
                    )
                require(
                    meets,
                    f"mapped scenario does not satisfy management target: {target['target_id']}/{scenario}",
                )
                comparisons[scenario] = {
                    "measurement_basis": target["measurement_basis"],
                    "measurement_periods": measurement_periods,
                    "modeled_period_values": period_values,
                    "modeled_value": observed,
                    "target_value": target_value,
                    "attainment_ratio": None
                    if target_value == 0
                    else observed / target_value,
                    "meets_target": meets,
                }
        item["scenario_comparison"] = comparisons
        output_targets.append(item)
    return {
        "communications": copy.deepcopy(
            validated["management_target_coverage"]["communications"]
        ),
        "targets": output_targets,
        "counts": copy.deepcopy(validated["management_target_coverage"]["counts"]),
    }
