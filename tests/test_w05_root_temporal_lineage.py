"""ROOT business regressions for temporal meaning through the actual RF DAG.

All amounts are synthetic test fixtures. Tests use native input/forecast readers.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from revenue_core import ForecastInputError, run_forecast
from test_w05_dated_contribution_contract import add_window_parameter, parameter, schema_3_10_document
from test_w05_dated_contribution_output import add_acquisition_adjustment


def acquisition_document():
    data = schema_3_10_document()
    add_acquisition_adjustment(data)
    return data


def test_partial_flow_cannot_become_full_year_by_derived_annual_alias():
    data = acquisition_document()
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(time_basis="annual", formula="x0", input_parameter_ids=["cmp_post_2026"], value=1.29190208)
        for field in ("period_start", "period_end", "rationale"):
            target.pop(field)
    with pytest.raises(ForecastInputError, match="composition"):
        run_forecast(data)


def test_rationale_cannot_relabel_existing_2026_amount_as_2027_flow():
    data = acquisition_document()
    data.pop("forecast_adjustments")
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(period="FY2027", period_start="2027-01-01", period_end="2027-12-31", rationale="explicit composition")
    with pytest.raises(ForecastInputError, match="composition"):
        run_forecast(data)


def test_same_perimeter_h1_and_its_q2_cannot_be_added_despite_rationale():
    data = acquisition_document()
    definition = "Segment A recognized revenue"
    add_window_parameter(data, "same_h1", 55.0, "2026-01-01", "2026-06-30", 2026, definition=definition)
    add_window_parameter(data, "same_q2", 30.0, "2026-04-01", "2026-06-30", 2026, definition=definition)
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(formula="x0+x1", input_parameter_ids=["same_h1", "same_q2"], value=85.0,
                      definition=definition, rationale="Q2 is a subset of H1; intentional overlap")
    with pytest.raises(ForecastInputError, match="composition"):
        run_forecast(data)


def test_zero_weight_full_year_input_does_not_fill_missing_flow_coverage():
    data = acquisition_document()
    add_window_parameter(data, "unused_full_year", 42.0, "2026-01-01", "2026-12-31", 2026)
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(formula="x0+0*x1", input_parameter_ids=["cmp_post_2026", "unused_full_year"], value=1.29190208)
        target.pop("rationale")
    with pytest.raises(ForecastInputError, match="composition"):
        run_forecast(data)


@pytest.mark.parametrize("target_definition", ["Segment A recognized revenue", "A completely renamed output"])
def test_derived_aliases_cannot_launder_same_scope_overlap(target_definition):
    data = schema_3_10_document()
    add_window_parameter(data, "actual_h1", 55.0, "2026-01-01", "2026-06-30", 2026,
                         definition="Segment A recognized revenue")
    add_window_parameter(data, "actual_q2", 30.0, "2026-04-01", "2026-06-30", 2026,
                         definition="Segment A recognized revenue")
    for name, source, value, start in (("alias_h1", "actual_h1", 55.0, "2026-01-01"),
                                      ("alias_q2", "actual_q2", 30.0, "2026-04-01")):
        add_window_parameter(data, name, value, start, "2026-06-30", 2026, kind="derived_fact", claim=False,
                             formula="x0", input_parameter_ids=[source], definition=f"Renamed {name}")
    add_window_parameter(data, "alias_sum", 85.0, "2026-01-01", "2026-06-30", 2026,
                         kind="derived_fact", claim=False, formula="x0+x1", input_parameter_ids=["alias_h1", "alias_q2"],
                         definition=target_definition, rationale="Two relabeled operands")
    with pytest.raises(ForecastInputError, match="double counts"):
        run_forecast(data)


def test_same_original_flow_cannot_be_reused_via_distinct_derived_aliases():
    data = schema_3_10_document()
    add_window_parameter(data, "original", 20.0, "2026-06-01", "2026-06-10", 2026)
    for name in ("alias_left", "alias_right"):
        add_window_parameter(data, name, 20.0, "2026-06-01", "2026-06-10", 2026,
                             kind="derived_fact", claim=False, formula="x0", input_parameter_ids=["original"],
                             definition=f"Distinct alias {name}")
    add_window_parameter(data, "double_alias", 40.0, "2026-06-01", "2026-06-10", 2026,
                         kind="derived_fact", claim=False, formula="x0+x1", input_parameter_ids=["alias_left", "alias_right"],
                         rationale="These labels are different")
    with pytest.raises(ForecastInputError, match="double counts"):
        run_forecast(data)


def test_disjoint_business_scopes_may_compose_the_same_dates_with_explanation():
    data = schema_3_10_document()
    add_window_parameter(data, "entity_a", 20.0, "2026-06-01", "2026-06-10", 2026, definition="Entity A standalone revenue")
    add_window_parameter(data, "entity_b", 15.0, "2026-06-01", "2026-06-10", 2026, definition="Entity B standalone revenue")
    add_window_parameter(data, "combined_entities", 35.0, "2026-06-01", "2026-06-10", 2026,
                         kind="derived_fact", claim=False, formula="x0+x1", input_parameter_ids=["entity_a", "entity_b"],
                         rationale="A and B are disjoint standalone businesses; no group/subsidiary duplication")
    run_forecast(data)


def test_point_stock_alone_cannot_be_retyped_as_dated_recognized_revenue():
    data = schema_3_10_document()
    add_window_parameter(data, "closing_stock", 20.0, None, None, 2026,
                         time_basis="point_in_time", definition="Closing receivable balance")
    parameter(data, "closing_stock")["dimension"] = "monetary_balance"
    add_window_parameter(data, "fake_flow_from_stock", 20.0, "2026-01-01", "2026-12-31", 2026,
                         kind="derived_fact", claim=False, formula="x0", input_parameter_ids=["closing_stock"],
                         rationale="The balance is relabeled as recognized flow")
    with pytest.raises(ForecastInputError, match="flow-bearing"):
        run_forecast(data)


def typed_assumption(data, parameter_id, value, dimension, basis="annual"):
    from test_data_contract import apply_parameter_contract
    item = {"parameter_id": parameter_id, "kind": "analyst_assumption", "value": value,
            "unit": {"ratio": "ratio", "quantity": "units", "revenue_per_unit": "USD million per unit"}.get(dimension, "USD million"),
            "period": "FY2026", "definition": f"Typed synthetic {parameter_id}",
            "scenario": None, "source_ids": [], "rationale": "Synthetic typed test assumption"}
    apply_parameter_contract(data, item, dimension)
    item["time_basis"] = basis
    data["parameters"].append(item)
    return item


@pytest.mark.parametrize("dimension,basis,formula,value", [
    ("monetary_balance", "point_in_time", "x0", 20.0),
    ("monetary_balance", "annual", "x0", 20.0),
    ("quantity", "point_in_time", "x0", 20.0),
    ("ratio", "annual", "x0", 0.2),
    ("ratio", "annual", "100*x0", 20.0),
    ("ratio", "annual", "20", 20.0),
    ("revenue", "annual", "0*x0+20", 20.0),
])
def test_nonflow_aliases_cannot_become_annual_revenue(dimension, basis, formula, value):
    data = acquisition_document()
    source_value = 0.2 if dimension == "ratio" else 20.0
    typed_assumption(data, "typed_origin", source_value, dimension, basis)
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(time_basis="annual", formula=formula, input_parameter_ids=["typed_origin"], value=value,
                      rationale="Relabeling with an explanation must not change a type")
        target.pop("period_start")
        target.pop("period_end")
    with pytest.raises(ForecastInputError, match="typed flow"):
        run_forecast(data)


def test_nested_annual_aliases_do_not_erase_original_stock_type():
    data = acquisition_document()
    typed_assumption(data, "typed_balance", 20.0, "monetary_balance", "point_in_time")
    add_window_parameter(data, "renamed_balance", 20.0, None, None, 2026, time_basis="annual",
                         kind="derived_fact", claim=False, formula="x0", input_parameter_ids=["typed_balance"],
                         definition="Intermediate revenue renamed from receivables")
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(time_basis="annual", formula="x0", input_parameter_ids=["renamed_balance"], value=20.0)
        target.pop("period_start")
        target.pop("period_end")
    with pytest.raises(ForecastInputError, match="typed flow"):
        run_forecast(data)


def test_annual_derived_revenue_cannot_be_a_ratio_of_two_revenues():
    data = acquisition_document()
    typed_assumption(data, "annual_left", 20.0, "revenue")
    typed_assumption(data, "annual_right", 10.0, "revenue")
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(time_basis="annual", formula="x0/x1", input_parameter_ids=["annual_left", "annual_right"], value=2.0)
        target.pop("period_start")
        target.pop("period_end")
    with pytest.raises(ForecastInputError, match="typed flow"):
        run_forecast(data)


def test_point_quantity_times_annual_arpu_is_a_valid_typed_annual_revenue():
    data = acquisition_document()
    typed_assumption(data, "average_customers", 10.0, "quantity", "point_in_time")
    typed_assumption(data, "annual_arpu", 2.0, "revenue_per_unit")
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(time_basis="annual", formula="x0*x1", input_parameter_ids=["average_customers", "annual_arpu"], value=20.0)
        target.pop("period_start")
        target.pop("period_end")
    run_forecast(data)


@pytest.mark.parametrize("model,stocks", [
    ("subscription", {"average_customers"}),
    ("asset_management", {"average_aum"}),
    ("bank_revenue", {"average_earning_assets", "average_interest_bearing_liabilities"}),
])
def test_native_stock_price_and_fee_models_keep_explicit_business_roles(model, stocks):
    import copy
    from test_industry_end_to_end import model_document
    data = model_document(model)
    expected = run_forecast(copy.deepcopy(data))
    data["schema_version"] = "3.10"
    for scenario in data["segments"][0]["scenarios"].values():
        for driver in stocks:
            for identifier in scenario["driver_parameter_ids"][driver]:
                parameter(data, identifier)["time_basis"] = "point_in_time"
    result = run_forecast(data)
    assert result["consolidated_forecast"] == expected["consolidated_forecast"]


def test_standalone_annual_consumer_checks_derived_type_before_annual_label():
    from contracts.annual_consumption import validate_annual_consumption
    origin = {"parameter_id": "stock", "dimension": "monetary_balance", "time_basis": "point_in_time",
              "period": "FY2026", "kind": "reported_fact", "value": 20.0}
    alias = {"parameter_id": "alias", "dimension": "revenue", "time_basis": "annual", "period": "FY2026",
             "kind": "derived_fact", "value": 20.0, "formula": "x0", "input_parameter_ids": ["stock"]}
    data = {"schema_version": "3.10", "fiscal_year_end": "12-31", "segments": [],
            "forecast_adjustments": [{"scenario_parameter_ids": {"low": ["alias"]}}]}
    with pytest.raises(ForecastInputError, match="typed flow"):
        validate_annual_consumption(data, {"stock": origin, "alias": alias})


def rebind_annual_adjustment(data, formula, inputs, value):
    for scenario in ("low", "base", "high"):
        target = parameter(data, f"cmp_fy2026_{scenario}")
        target.update(time_basis="annual", formula=formula, input_parameter_ids=inputs, value=value)
        target.pop("period_start")
        target.pop("period_end")


@pytest.mark.parametrize("flow_value", [0.0, 10.0])
def test_money_stock_cannot_join_recognized_flow_even_with_real_annual_anchor(flow_value):
    data = acquisition_document()
    typed_assumption(data, "receivable_stock", 20.0, "monetary_balance", "point_in_time")
    typed_assumption(data, "annual_anchor", flow_value, "revenue")
    rebind_annual_adjustment(data, "x0+x1", ["receivable_stock", "annual_anchor"], 20.0 + flow_value)
    with pytest.raises(ForecastInputError, match="typed flow"):
        run_forecast(data)


def test_stock_divided_by_flow_then_multiplied_by_that_flow_stays_stock():
    data = acquisition_document()
    typed_assumption(data, "receivable_stock", 20.0, "monetary_balance", "point_in_time")
    typed_assumption(data, "annual_anchor", 10.0, "revenue")
    ratio = typed_assumption(data, "stock_to_flow", 2.0, "ratio")
    ratio.update(kind="derived_fact", formula="x0/x1", input_parameter_ids=["receivable_stock", "annual_anchor"])
    rebind_annual_adjustment(data, "x0*x1", ["annual_anchor", "stock_to_flow"], 20.0)
    with pytest.raises(ForecastInputError, match="typed flow"):
        run_forecast(data)


def test_actual_annual_turnover_ratio_can_convert_a_money_stock_with_its_flow_ancestry():
    data = acquisition_document()
    typed_assumption(data, "asset_stock", 20.0, "monetary_balance", "point_in_time")
    typed_assumption(data, "annual_anchor", 10.0, "revenue")
    ratio = typed_assumption(data, "annual_turnover", 0.5, "ratio")
    ratio.update(kind="derived_fact", formula="x0/x1", input_parameter_ids=["annual_anchor", "asset_stock"])
    rebind_annual_adjustment(data, "x0*x1", ["asset_stock", "annual_turnover"], 10.0)
    run_forecast(data)


@pytest.mark.parametrize("origin_dimension,origin_basis,expected", [
    ("revenue", "annual", "accept"),
    ("monetary_balance", "point_in_time", "reject"),
])
def test_derived_annual_price_keeps_its_actual_income_or_stock_origin(origin_dimension, origin_basis, expected):
    data = acquisition_document()
    typed_assumption(data, "original_money", 20.0, origin_dimension, origin_basis)
    typed_assumption(data, "operating_customers", 10.0, "quantity", "point_in_time")
    price = typed_assumption(data, "derived_annual_price", 2.0, "revenue_per_unit")
    price.update(kind="derived_fact", formula="x0/x1", input_parameter_ids=["original_money", "operating_customers"])
    rebind_annual_adjustment(data, "x0*x1", ["operating_customers", "derived_annual_price"], 20.0)
    if expected == "reject":
        with pytest.raises(ForecastInputError, match="typed flow"):
            run_forecast(data)
    else:
        run_forecast(data)


@pytest.mark.parametrize("variant", ["inline", "derived_ratio", "distinct_prices", "nested_alias", "equivalent_expression", "scaled_cancel"])
@pytest.mark.parametrize("origin_dimension,origin_basis,expected", [
    ("monetary_balance", "point_in_time", "reject"),
    ("revenue", "annual", "accept"),
])
def test_price_cancellation_cannot_change_original_stock_or_flow_time(variant, origin_dimension, origin_basis, expected):
    """Business identity: multiplying by a price ratio cannot create duration."""
    data = acquisition_document()
    typed_assumption(data, "original_amount", 20.0, origin_dimension, origin_basis)
    typed_assumption(data, "annual_price", 2.0, "revenue_per_unit")
    if variant == "inline":
        formula, inputs, value = "x0*(x1/x1)", ["original_amount", "annual_price"], 20.0
    elif variant == "scaled_cancel":
        formula, inputs, value = "x0*((2*x1)/(4*x1))", ["original_amount", "annual_price"], 10.0
    else:
        if variant == "distinct_prices":
            typed_assumption(data, "other_annual_price", 4.0, "revenue_per_unit")
            ids, ratio_formula, ratio_value = ["annual_price", "other_annual_price"], "x0/x1", 0.5
        elif variant in {"nested_alias", "equivalent_expression"}:
            alias = typed_assumption(data, "price_alias", 2.0, "revenue_per_unit")
            alias.update(kind="derived_fact", formula="x0" if variant == "nested_alias" else "(3*x0+x0)/4",
                         input_parameter_ids=["annual_price"])
            ids, ratio_formula, ratio_value = ["annual_price", "price_alias"], "x0/x1", 1.0
        else:
            ids, ratio_formula, ratio_value = ["annual_price"], "x0/x0", 1.0
        ratio = typed_assumption(data, "cancelled_price_ratio", ratio_value, "ratio")
        ratio.update(kind="derived_fact", formula=ratio_formula, input_parameter_ids=ids)
        formula, inputs, value = "x0*x1", ["original_amount", "cancelled_price_ratio"], 20.0 * ratio_value
    rebind_annual_adjustment(data, formula, inputs, value)
    if expected == "reject":
        with pytest.raises(ForecastInputError, match="typed flow"):
            run_forecast(data)
    else:
        result = run_forecast(data)
        assert result["consolidated_forecast"]["low"]["annual_revenue"]["2026"] == 150.0 + value


def test_annual_operating_flow_times_transaction_price_preserves_flow():
    data = acquisition_document()
    typed_assumption(data, "annual_units", 10.0, "quantity")
    typed_assumption(data, "transaction_price", 2.0, "revenue_per_unit")
    rebind_annual_adjustment(data, "x0*x1", ["annual_units", "transaction_price"], 20.0)
    run_forecast(data)



def test_actual_dated_quantity_times_transaction_price_keeps_real_window():
    data = schema_3_10_document()
    add_window_parameter(data, "units_sold", 10.0, "2026-06-01", "2026-06-10", 2026, unit="units")
    from test_data_contract import apply_parameter_contract
    apply_parameter_contract(data, parameter(data, "units_sold"), "quantity")
    parameter(data, "units_sold")["time_basis"] = "period_flow"
    typed_assumption(data, "sale_price", 2.0, "revenue_per_unit")
    add_window_parameter(data, "sales_income", 20.0, "2026-06-01", "2026-06-10", 2026,
                         kind="derived_fact", claim=False, formula="x0*x1", input_parameter_ids=["units_sold", "sale_price"])
    run_forecast(data)
