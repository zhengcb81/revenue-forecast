"""Reusable test-only mining forecast fixture from the ZR-709 journey."""

from __future__ import annotations

from commercial_terms import calculate_net_revenue, validate_commercial_terms
from mine_year_operation import derive_saleable_volume, validate_mine_year_operation
from test_data_contract import apply_parameter_contract, finalize_contract, research_coverage


YEARS = [2026, 2027, 2028, 2029, 2030]
PRICE_MULT = {"low": 0.85, "base": 1.0, "high": 1.2}
VOLUME_MULT = {"low": 0.9, "base": 1.0, "high": 1.08}
RAMP = [1.00, 1.05, 1.10, 1.12, 1.15]  # ramp-up across the five years

# Synthetic Zijin-shaped structure (test-only names; zero product hardcoding)
KAMOA_CHAIN = [
    [{"effective_date": "2015-05-01", "ownership_fraction": 0.6}],
    [{"effective_date": "2015-05-01", "ownership_fraction": 0.66}],
]  # effective group share 0.6 × 0.66 = 0.396
KAMOA_SHARE = 0.396
JULONG_SHARE = 1.0
ZIJINSHAN_SHARE = 1.0
BYPRODUCT_CREDIT = 350.0


def _operation(mine: str, scenario: str, year: int) -> dict:
    index = YEARS.index(year)
    shapes = {
        # mine: (volume, grade, recovery, payable, product)
        "kamoa_copper": (450.0, 2.8, 0.86, 0.965, "copper concentrate"),
        "julong_copper": (200.0, 0.55, 0.84, 0.95, "copper concentrate"),
        "zijinshan_gold": (8000.0, 0.9, 0.78, 0.99, "gold doré"),
    }
    volume, grade, recovery, payable, product = shapes[mine]
    return {
        "volume": volume * VOLUME_MULT[scenario] * RAMP[index],
        "grade": grade,
        "recovery": recovery,
        "payable": payable,
        "product": product,
        "period": f"FY{year}",
        "scenario": scenario,
    }


def _terms(mine: str, scenario: str, year: int) -> dict:
    prices = {
        "kamoa_copper": (9800.0, 0.035),
        "julong_copper": (71000.0, 0.03),
        "zijinshan_gold": (620.0, 0.02),
    }
    price, royalty = prices[mine]
    terms = {
        "price": {
            "value": price * PRICE_MULT[scenario],
            "source": "fixture price curve",
            "assumption": "analyst",
            "period": f"FY{year}",
        },
        "royalty_rate": {
            "value": royalty,
            "source": "fixture mining code",
            "assumption": "contract",
            "period": f"FY{year}",
        },
    }
    if mine == "zijinshan_gold":
        terms["byproduct_credit"] = {
            "value": BYPRODUCT_CREDIT,
            "source": "fixture silver credit",
            "assumption": "analyst",
            "period": f"FY{year}",
        }
    return terms


def _mine_contribution(
    mine: str, share: float, scenario: str, year: int
) -> tuple[float, float]:
    """(ownership-weighted saleable volume, weighted net revenue)."""
    operation = validate_mine_year_operation(_operation(mine, scenario, year))
    saleable = derive_saleable_volume(operation)
    net = calculate_net_revenue(
        saleable, validate_commercial_terms(_terms(mine, scenario, year))
    )
    return saleable * share, net["net"] * share


SEGMENT_MINES = {
    "copper": (("kamoa_copper", KAMOA_SHARE), ("julong_copper", JULONG_SHARE)),
    "gold": (("zijinshan_gold", ZIJINSHAN_SHARE),),
}


def _segment_volume_and_net(
    segment: str, scenario: str, year: int
) -> tuple[float, float]:
    volumes = []
    nets = []
    for mine, share in SEGMENT_MINES[segment]:
        saleable, net = _mine_contribution(mine, share, scenario, year)
        volumes.append(saleable)
        nets.append(net)
    return sum(volumes), sum(nets)


def _trading_value(scenario: str, year: int) -> float:
    base = {"low": 18.0, "base": 20.0, "high": 23.0}[scenario]
    growth = {"low": 1.04, "base": 1.06, "high": 1.09}[scenario]
    return base * growth ** (year - 2025)


def _add_driver(
    data: dict,
    parameter_id: str,
    value: float,
    dimension: str,
    scenario: str,
    year: int,
    definition: str,
) -> None:
    parameter = {
        "parameter_id": parameter_id,
        "kind": "analyst_assumption",
        "value": value,
        "unit": dimension,
        "period": f"FY{year}",
        "definition": definition,
        "scenario": scenario,
        "rationale": "Derived from validated operating units and commercial terms",
        "source_ids": ["filing"],
    }
    data["parameters"].append(parameter)
    apply_parameter_contract(data, parameter, dimension)


def _zijin_document() -> dict:
    """Five-year mining forecast document derived from the F2 contracts."""
    data = {
        "company_name": "Synthetic Zijin-Shaped Copper-Gold Group",
        "as_of_date": "2026-07-12",
        "currency": "USD",
        "unit": "million",
        "fiscal_year_end": "12-31",
        "base_year": 2025,
        "forecast_years": YEARS,
        "sources": [
            {
                "source_id": "filing",
                "source_type": "exchange_filing",
                "title": "FY2025 annual report",
                "publisher": "Test Exchange",
                "url": "https://www.example-filing.com/acme/2025",
                "published_date": "2026-03-01",
                "accessed_date": "2026-07-01",
                "page_or_section": "Revenue note",
            },
            {
                "source_id": "research",
                "source_type": "company_release",
                "title": "Q2 operations research communication",
                "publisher": "Company IR",
                "url": "https://www.example-filing.com/acme/q2-research",
                "published_date": "2026-06-15",
                "accessed_date": "2026-07-01",
                "page_or_section": "Operating outlook",
            },
        ],
        "parameters": [
            {
                "parameter_id": "reported_total",
                "kind": "reported_fact",
                "value": 320,
                "unit": "USD million",
                "period": "FY2025",
                "definition": "reported total revenue",
                "source_ids": ["filing"],
            },
            {
                "parameter_id": "copper_base",
                "kind": "reported_fact",
                "value": 210,
                "unit": "USD million",
                "period": "FY2025",
                "definition": "copper segment external revenue",
                "source_ids": ["filing"],
            },
            {
                "parameter_id": "gold_base",
                "kind": "reported_fact",
                "value": 90,
                "unit": "USD million",
                "period": "FY2025",
                "definition": "gold segment external revenue",
                "source_ids": ["filing"],
            },
            {
                "parameter_id": "trading_base",
                "kind": "reported_fact",
                "value": 20,
                "unit": "USD million",
                "period": "FY2025",
                "definition": "trading and other external revenue",
                "source_ids": ["filing"],
            },
        ],
        "segments": [
            {"name": "copper", "base_revenue_parameter_id": "copper_base"},
            {"name": "gold", "base_revenue_parameter_id": "gold_base"},
            {"name": "trading_and_other", "base_revenue_parameter_id": "trading_base"},
        ],
        "reported_total_revenue_parameter_id": "reported_total",
        "base_adjustment_parameter_ids": [],
        "historical_revenue": [
            {"year": 2024, "value": 300, "source_ids": ["filing"]},
            {"year": 2025, "value": 320, "source_ids": ["filing"]},
        ],
        "research_coverage": research_coverage(
            ["reported_total", "copper_base", "gold_base", "trading_base"]
        ),
    }
    for parameter in data["parameters"]:
        apply_parameter_contract(data, parameter, "revenue")

    driver_ids: dict[str, dict[str, list[str]]] = {}
    for segment in ("copper", "gold"):
        driver_ids[segment] = {}
        for scenario in ("low", "base", "high"):
            volume_ids = []
            price_ids = []
            for year in YEARS:
                seg_volume, seg_net = _segment_volume_and_net(segment, scenario, year)
                other = BYPRODUCT_CREDIT if segment == "gold" else 0.0
                realized_price = (seg_net - other) / seg_volume
                volume_id = f"{segment}_{scenario}_{year}_saleable"
                price_id = f"{segment}_{scenario}_{year}_price"
                _add_driver(
                    data,
                    volume_id,
                    seg_volume,
                    "quantity",
                    scenario,
                    year,
                    f"{segment} ownership-weighted saleable volume",
                )
                _add_driver(
                    data,
                    price_id,
                    realized_price,
                    "revenue_per_unit",
                    scenario,
                    year,
                    f"{segment} blended realized net price per unit",
                )
                volume_ids.append(volume_id)
                price_ids.append(price_id)
            drivers = {
                "saleable_volume": volume_ids,
                "realized_price": price_ids,
            }
            if segment == "gold":
                other_ids = []
                for year in YEARS:
                    other_id = f"gold_{scenario}_{year}_byproduct"
                    _add_driver(
                        data,
                        other_id,
                        BYPRODUCT_CREDIT,
                        "revenue",
                        scenario,
                        year,
                        "silver byproduct credit (flat, never double counted)",
                    )
                    other_ids.append(other_id)
                drivers["other_revenue"] = other_ids
            driver_ids[segment][scenario] = drivers

    trading_ids: dict[str, list[str]] = {}
    for scenario in ("low", "base", "high"):
        ids = []
        for year in YEARS:
            parameter_id = f"trading_{scenario}_{year}_rev"
            _add_driver(
                data,
                parameter_id,
                _trading_value(scenario, year),
                "revenue",
                scenario,
                year,
                "trading and other modeled revenue",
            )
            ids.append(parameter_id)
        trading_ids[scenario] = ids

    for segment in data["segments"]:
        segment["recognition"] = {
            "mode": "modeled_as_recognized",
            "timing": "point_in_time",
            "trigger": "shipment/delivery",
            "presentation": "gross",
        }
        segment["scenarios"] = {}
        for scenario in ("low", "base", "high"):
            if segment["name"] == "trading_and_other":
                model = "direct_revenue"
                drivers = {"revenue": trading_ids[scenario]}
            else:
                model = "resource"
                drivers = driver_ids[segment["name"]][scenario]
            segment["scenarios"][scenario] = {
                "model": model,
                "driver_parameter_ids": drivers,
                "rationale": f"{scenario} mining resource path from F2 contracts",
            }

    base_driver_ids = [
        parameter_id
        for segment in data["segments"]
        for ids in segment["scenarios"]["base"]["driver_parameter_ids"].values()
        for parameter_id in ids
    ]
    growth_record = next(
        item
        for item in data["research_coverage"]
        if item["dimension"] == "growth_curve"
    )
    growth_record.update(
        {
            "status": "modeled_driver",
            "conclusion": "Resource-model paths generate the five-year synthetic forecast",
            "revenue_mechanism": "operating units × commercial terms aggregate by segment",
            "parameter_ids": base_driver_ids,
            "source_ids": ["filing", "research"],
        }
    )
    growth_record.pop("rationale", None)
    return finalize_contract(data)
