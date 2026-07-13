"""Immutable registry of pure segment revenue model calculators."""

from __future__ import annotations

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Iterable, Mapping, Sequence


class ModelRegistryError(ValueError):
    """Raised when model registration or pure calculation is invalid."""


Calculator = Callable[[float, Mapping[str, list[float]], Sequence[int]], list[float]]


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    required: tuple[str, ...]
    optional: tuple[str, ...]
    defaults: Mapping[str, float]
    dimensions: Mapping[str, str]
    ratio_drivers: frozenset[str]
    formula: str
    calculator: Calculator

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ModelRegistryError("revenue model_id is required")
        drivers = self.required + self.optional
        if len(drivers) != len(set(drivers)):
            raise ModelRegistryError(f"duplicate driver in revenue model: {self.model_id}")
        if set(self.dimensions) != set(drivers):
            raise ModelRegistryError(f"driver dimension coverage mismatch: {self.model_id}")
        if not set(self.defaults) <= set(self.optional):
            raise ModelRegistryError(f"defaults must reference optional drivers: {self.model_id}")
        if not self.ratio_drivers <= set(drivers):
            raise ModelRegistryError(f"ratio driver is not registered: {self.model_id}")
        if not self.formula.strip() or not callable(self.calculator):
            raise ModelRegistryError(f"formula and calculator are required: {self.model_id}")
        object.__setattr__(self, "defaults", MappingProxyType(dict(self.defaults)))
        object.__setattr__(self, "dimensions", MappingProxyType(dict(self.dimensions)))


def build_registry(specs: Iterable[ModelSpec]) -> Mapping[str, ModelSpec]:
    registry: dict[str, ModelSpec] = {}
    for spec in specs:
        if spec.model_id in registry:
            raise ModelRegistryError(f"duplicate revenue model: {spec.model_id}")
        registry[spec.model_id] = spec
    if not registry:
        raise ModelRegistryError("revenue model registry cannot be empty")
    return MappingProxyType(registry)


def _rowwise(formula: Callable[[Mapping[str, float]], float]) -> Calculator:
    def calculate(base_revenue: float, drivers: Mapping[str, list[float]], years: Sequence[int]) -> list[float]:
        del base_revenue
        return [formula({name: values[index] for name, values in drivers.items()}) for index in range(len(years))]

    return calculate


def _direct_growth(base_revenue: float, drivers: Mapping[str, list[float]], years: Sequence[int]) -> list[float]:
    del years
    result: list[float] = []
    current = base_revenue
    for growth_rate in drivers["growth_rate"]:
        current *= 1 + growth_rate
        result.append(current)
    return result


def _direct_revenue(base_revenue: float, drivers: Mapping[str, list[float]], years: Sequence[int]) -> list[float]:
    del base_revenue, years
    return list(drivers["revenue"])


def _project_backlog(base_revenue: float, drivers: Mapping[str, list[float]], years: Sequence[int]) -> list[float]:
    del base_revenue
    result: list[float] = []
    for index, year in enumerate(years):
        opening = drivers["opening_backlog"][index]
        if index > 0 and not math.isclose(opening, drivers["closing_backlog"][index - 1], rel_tol=1e-9, abs_tol=1e-9):
            raise ModelRegistryError(f"project backlog continuity failed: FY{year}")
        result.append(
            opening
            + drivers["bookings"][index]
            - drivers["cancellations"][index]
            + drivers["contract_changes"][index]
            - drivers["closing_backlog"][index]
        )
    return result


def _cohort_subscription(base_revenue: float, drivers: Mapping[str, list[float]], years: Sequence[int]) -> list[float]:
    del base_revenue
    result: list[float] = []
    for index, year in enumerate(years):
        opening = drivers["opening_customers"][index]
        ending = drivers["ending_customers"][index]
        expected_ending = opening + drivers["new_customers"][index] - drivers["churned_customers"][index]
        if not math.isclose(ending, expected_ending, rel_tol=1e-9, abs_tol=1e-9):
            raise ModelRegistryError(f"cohort customer bridge failed: FY{year}")
        if index > 0 and not math.isclose(opening, drivers["ending_customers"][index - 1], rel_tol=1e-9, abs_tol=1e-9):
            raise ModelRegistryError(f"cohort customer continuity failed: FY{year}")
        result.append(
            (opening + ending) / 2
            * drivers["revenue_per_customer"][index]
            * drivers["timing_factor"][index]
            + drivers["usage_revenue"][index]
        )
    return result


def _delivery_pipeline(base_revenue: float, drivers: Mapping[str, list[float]], years: Sequence[int]) -> list[float]:
    del base_revenue
    result: list[float] = []
    for index, year in enumerate(years):
        opening = drivers["opening_orders"][index]
        ending = drivers["ending_orders"][index]
        expected_ending = opening + drivers["new_orders"][index] - drivers["cancellations"][index] - drivers["deliveries"][index]
        if not math.isclose(ending, expected_ending, rel_tol=1e-9, abs_tol=1e-9):
            raise ModelRegistryError(f"delivery order bridge failed: FY{year}")
        if index > 0 and not math.isclose(opening, drivers["ending_orders"][index - 1], rel_tol=1e-9, abs_tol=1e-9):
            raise ModelRegistryError(f"delivery order continuity failed: FY{year}")
        result.append(
            drivers["deliveries"][index]
            * drivers["unit_revenue"][index]
            * drivers["timing_factor"][index]
            + drivers["other_revenue"][index]
        )
    return result


def _spec(
    model_id: str,
    required: tuple[str, ...],
    optional: tuple[str, ...],
    dimensions: Mapping[str, str],
    formula: str,
    calculator: Calculator,
    *,
    defaults: Mapping[str, float] | None = None,
    ratio_drivers: Iterable[str] = (),
) -> ModelSpec:
    return ModelSpec(
        model_id=model_id,
        required=required,
        optional=optional,
        defaults=defaults or {},
        dimensions=dimensions,
        ratio_drivers=frozenset(ratio_drivers),
        formula=formula,
        calculator=calculator,
    )


MODEL_REGISTRY = build_registry([
    _spec("direct_growth", ("growth_rate",), (), {"growth_rate": "ratio"}, "revenue[t] = revenue[t-1] * (1 + growth_rate[t])", _direct_growth),
    _spec("direct_revenue", ("revenue",), (), {"revenue": "revenue"}, "revenue[t] = direct_revenue[t]", _direct_revenue),
    _spec("unit_sales", ("units", "unit_revenue"), ("timing_factor", "other_revenue"), {"units": "quantity", "unit_revenue": "revenue_per_unit", "timing_factor": "ratio", "other_revenue": "revenue"}, "revenue = units * unit_revenue * timing_factor + other_revenue", _rowwise(lambda d: d["units"] * d["unit_revenue"] * d["timing_factor"] + d["other_revenue"]), defaults={"timing_factor": 1.0}, ratio_drivers=("timing_factor",)),
    _spec("capacity_utilization", ("capacity", "utilization", "yield", "unit_revenue"), ("timing_factor", "other_revenue"), {"capacity": "quantity", "utilization": "ratio", "yield": "ratio", "unit_revenue": "revenue_per_unit", "timing_factor": "ratio", "other_revenue": "revenue"}, "revenue = capacity * utilization * yield * unit_revenue * timing_factor + other_revenue", _rowwise(lambda d: d["capacity"] * d["utilization"] * d["yield"] * d["unit_revenue"] * d["timing_factor"] + d["other_revenue"]), defaults={"timing_factor": 1.0}, ratio_drivers=("utilization", "yield", "timing_factor")),
    _spec("subscription", ("average_customers", "revenue_per_customer"), ("timing_factor", "usage_revenue"), {"average_customers": "quantity", "revenue_per_customer": "revenue_per_unit", "timing_factor": "ratio", "usage_revenue": "revenue"}, "revenue = average_customers * revenue_per_customer * timing_factor + usage_revenue", _rowwise(lambda d: d["average_customers"] * d["revenue_per_customer"] * d["timing_factor"] + d["usage_revenue"]), defaults={"timing_factor": 1.0}, ratio_drivers=("timing_factor",)),
    _spec("usage_platform", ("eligible_activity", "monetization_rate"), ("fixed_revenue",), {"eligible_activity": "activity", "monetization_rate": "revenue_per_activity", "fixed_revenue": "revenue"}, "revenue = eligible_activity * monetization_rate + fixed_revenue", _rowwise(lambda d: d["eligible_activity"] * d["monetization_rate"] + d["fixed_revenue"])),
    _spec("services", ("billable_capacity", "utilization", "billing_rate"), ("timing_factor", "other_revenue"), {"billable_capacity": "activity", "utilization": "ratio", "billing_rate": "revenue_per_activity", "timing_factor": "ratio", "other_revenue": "revenue"}, "revenue = billable_capacity * utilization * billing_rate * timing_factor + other_revenue", _rowwise(lambda d: d["billable_capacity"] * d["utilization"] * d["billing_rate"] * d["timing_factor"] + d["other_revenue"]), defaults={"timing_factor": 1.0}, ratio_drivers=("utilization", "timing_factor")),
    _spec("project_backlog", ("opening_backlog", "bookings", "cancellations", "contract_changes", "closing_backlog"), (), {"opening_backlog": "backlog", "bookings": "backlog", "cancellations": "backlog", "contract_changes": "backlog", "closing_backlog": "backlog"}, "revenue = opening_backlog + bookings - cancellations + contract_changes - closing_backlog", _project_backlog),
    _spec("resource", ("saleable_volume", "realized_price"), ("other_revenue",), {"saleable_volume": "quantity", "realized_price": "revenue_per_unit", "other_revenue": "revenue"}, "revenue = saleable_volume * realized_price + other_revenue", _rowwise(lambda d: d["saleable_volume"] * d["realized_price"] + d["other_revenue"])),
    _spec("infrastructure", ("billable_volume", "tariff"), ("other_revenue",), {"billable_volume": "activity", "tariff": "revenue_per_activity", "other_revenue": "revenue"}, "revenue = billable_volume * tariff + other_revenue", _rowwise(lambda d: d["billable_volume"] * d["tariff"] + d["other_revenue"])),
    _spec("bank_revenue", ("average_earning_assets", "asset_yield", "average_interest_bearing_liabilities", "funding_cost", "fee_revenue"), ("other_revenue",), {"average_earning_assets": "monetary_balance", "asset_yield": "ratio", "average_interest_bearing_liabilities": "monetary_balance", "funding_cost": "ratio", "fee_revenue": "revenue", "other_revenue": "revenue"}, "revenue = average_earning_assets * asset_yield - average_interest_bearing_liabilities * funding_cost + fee_revenue + other_revenue", _rowwise(lambda d: d["average_earning_assets"] * d["asset_yield"] - d["average_interest_bearing_liabilities"] * d["funding_cost"] + d["fee_revenue"] + d["other_revenue"]), ratio_drivers=("asset_yield", "funding_cost")),
    _spec("asset_management", ("average_aum", "management_fee_rate"), ("performance_fee_revenue", "other_revenue"), {"average_aum": "monetary_balance", "management_fee_rate": "ratio", "performance_fee_revenue": "revenue", "other_revenue": "revenue"}, "revenue = average_aum * management_fee_rate + performance_fee_revenue + other_revenue", _rowwise(lambda d: d["average_aum"] * d["management_fee_rate"] + d["performance_fee_revenue"] + d["other_revenue"]), ratio_drivers=("management_fee_rate",)),
    _spec("retail_franchise", ("average_owned_stores", "revenue_per_owned_store"), ("franchise_system_sales", "recognized_fee_rate", "supply_revenue"), {"average_owned_stores": "quantity", "revenue_per_owned_store": "revenue_per_unit", "franchise_system_sales": "revenue", "recognized_fee_rate": "ratio", "supply_revenue": "revenue"}, "revenue = average_owned_stores * revenue_per_owned_store + franchise_system_sales * recognized_fee_rate + supply_revenue", _rowwise(lambda d: d["average_owned_stores"] * d["revenue_per_owned_store"] + d["franchise_system_sales"] * d["recognized_fee_rate"] + d["supply_revenue"]), ratio_drivers=("recognized_fee_rate",)),
    _spec("transport", ("capacity", "utilization", "yield"), ("ancillary_revenue",), {"capacity": "quantity", "utilization": "ratio", "yield": "revenue_per_unit", "ancillary_revenue": "revenue"}, "revenue = capacity * utilization * yield + ancillary_revenue", _rowwise(lambda d: d["capacity"] * d["utilization"] * d["yield"] + d["ancillary_revenue"]), ratio_drivers=("utilization",)),
    _spec("real_estate_rental", ("average_occupied_area", "rent_per_area"), ("other_revenue",), {"average_occupied_area": "area", "rent_per_area": "revenue_per_area", "other_revenue": "revenue"}, "revenue = average_occupied_area * rent_per_area + other_revenue", _rowwise(lambda d: d["average_occupied_area"] * d["rent_per_area"] + d["other_revenue"])),
    _spec("licensing_commercial", ("treated_units", "net_revenue_per_unit"), ("milestone_revenue", "royalty_revenue", "service_revenue"), {"treated_units": "quantity", "net_revenue_per_unit": "revenue_per_unit", "milestone_revenue": "revenue", "royalty_revenue": "revenue", "service_revenue": "revenue"}, "revenue = treated_units * net_revenue_per_unit + milestone_revenue + royalty_revenue + service_revenue", _rowwise(lambda d: d["treated_units"] * d["net_revenue_per_unit"] + d["milestone_revenue"] + d["royalty_revenue"] + d["service_revenue"])),
    _spec("advertising", ("eligible_impressions", "fill_rate", "revenue_per_thousand_impressions"), ("other_revenue",), {"eligible_impressions": "activity", "fill_rate": "ratio", "revenue_per_thousand_impressions": "revenue_per_activity", "other_revenue": "revenue"}, "revenue = eligible_impressions / 1000 * fill_rate * revenue_per_thousand_impressions + other_revenue", _rowwise(lambda d: d["eligible_impressions"] / 1000 * d["fill_rate"] * d["revenue_per_thousand_impressions"] + d["other_revenue"]), ratio_drivers=("fill_rate",)),
    _spec("gaming", ("active_users", "payer_conversion", "revenue_per_payer"), ("other_revenue",), {"active_users": "quantity", "payer_conversion": "ratio", "revenue_per_payer": "revenue_per_unit", "other_revenue": "revenue"}, "revenue = active_users * payer_conversion * revenue_per_payer + other_revenue", _rowwise(lambda d: d["active_users"] * d["payer_conversion"] * d["revenue_per_payer"] + d["other_revenue"]), ratio_drivers=("payer_conversion",)),
    _spec("cohort_subscription", ("opening_customers", "new_customers", "churned_customers", "ending_customers", "revenue_per_customer"), ("timing_factor", "usage_revenue"), {"opening_customers": "quantity", "new_customers": "quantity", "churned_customers": "quantity", "ending_customers": "quantity", "revenue_per_customer": "revenue_per_unit", "timing_factor": "ratio", "usage_revenue": "revenue"}, "revenue = average(opening_customers, ending_customers) * revenue_per_customer * timing_factor + usage_revenue", _cohort_subscription, defaults={"timing_factor": 1.0}, ratio_drivers=("timing_factor",)),
    _spec("delivery_pipeline", ("opening_orders", "new_orders", "cancellations", "deliveries", "ending_orders", "unit_revenue"), ("timing_factor", "other_revenue"), {"opening_orders": "quantity", "new_orders": "quantity", "cancellations": "quantity", "deliveries": "quantity", "ending_orders": "quantity", "unit_revenue": "revenue_per_unit", "timing_factor": "ratio", "other_revenue": "revenue"}, "revenue = deliveries * unit_revenue * timing_factor + other_revenue", _delivery_pipeline, defaults={"timing_factor": 1.0}, ratio_drivers=("timing_factor",)),
    _spec("milestone_royalty", ("eligible_sales", "royalty_rate"), ("milestone_revenue", "service_revenue"), {"eligible_sales": "revenue", "royalty_rate": "ratio", "milestone_revenue": "revenue", "service_revenue": "revenue"}, "revenue = eligible_sales * royalty_rate + milestone_revenue + service_revenue", _rowwise(lambda d: d["eligible_sales"] * d["royalty_rate"] + d["milestone_revenue"] + d["service_revenue"]), ratio_drivers=("royalty_rate",)),
    _spec("insurance_service", ("coverage_units", "revenue_per_coverage_unit"), ("timing_factor", "other_revenue"), {"coverage_units": "coverage_units", "revenue_per_coverage_unit": "revenue_per_unit", "timing_factor": "ratio", "other_revenue": "revenue"}, "revenue = coverage_units * revenue_per_coverage_unit * timing_factor + other_revenue", _rowwise(lambda d: d["coverage_units"] * d["revenue_per_coverage_unit"] * d["timing_factor"] + d["other_revenue"]), defaults={"timing_factor": 1.0}, ratio_drivers=("timing_factor",)),
])


# Compatibility views retained for existing callers and fixtures.
MODEL_SPECS: Mapping[str, Mapping[str, object]] = MappingProxyType({
    model_id: MappingProxyType({
        "required": spec.required,
        "optional": spec.optional,
        "defaults": spec.defaults,
        "formula": spec.formula,
    })
    for model_id, spec in MODEL_REGISTRY.items()
})
MODEL_DRIVER_DIMENSIONS: Mapping[str, Mapping[str, str]] = MappingProxyType({
    model_id: spec.dimensions for model_id, spec in MODEL_REGISTRY.items()
})
MODEL_RATIO_DRIVERS: Mapping[str, frozenset[str]] = MappingProxyType({
    model_id: spec.ratio_drivers for model_id, spec in MODEL_REGISTRY.items() if spec.ratio_drivers
})


def calculate_registered_model(
    model_id: str,
    base_revenue: float,
    drivers: Mapping[str, list[float]],
    years: Sequence[int],
) -> list[float]:
    try:
        spec = MODEL_REGISTRY[model_id]
    except KeyError as exc:
        raise ModelRegistryError(f"unsupported revenue model: {model_id}") from exc
    result = spec.calculator(base_revenue, drivers, years)
    if len(result) != len(years):
        raise ModelRegistryError(f"calculator returned wrong path length: {model_id}")
    return [float(value) for value in result]
