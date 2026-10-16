"""ROOT unit contracts: stored numeric units must match the actual consumer."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest


@pytest.fixture
def runtime(monkeypatch, tmp_path):
    # Set IO ownership before importing any RF runtime (including test helpers).
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(tmp_path / "registry.jsonl"))
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "scripts"))
    monkeypatch.syspath_prepend(str(root / "tests"))
    from revenue_core import ForecastInputError, run_forecast
    from research.input_quantities import build_sensitivity_test, convert_input_quantity
    from test_golden_behavior_lock import model_document
    from test_recognition_bridge import forecast_document
    yield {
        "error": ForecastInputError, "run": run_forecast, "build": build_sensitivity_test,
        "convert": convert_input_quantity, "model": model_document,
        "forecast": forecast_document,
    }
    assert not (tmp_path / "registry.jsonl").exists(), "draft must not publish"


@pytest.mark.parametrize("source,target,shock_type", [
    ("pp", "ratio", "basis_point"),
    ("bp", "basis_point", "percentage_point"),
    ("bp", "basis_point", "percent"),
    ("percent", "percent", "percent"),
])
def test_share_record_numeric_unit_must_match_real_shock_type(runtime, source, target, shock_type):
    data = runtime["model"]("capacity")
    record = runtime["convert"](5, input_unit=source, engine_unit=target)
    data["sensitivity_tests"] = [{
        "name": "wrong_contract_unit", "parameter_id": "capacity_utilization_base_2026",
        "shock_type": shock_type, "shock_value": record["engine_value"],
        "input_quantity": record,
    }]
    with pytest.raises(runtime["error"], match="engine.*unit|contract.*unit"):
        runtime["run"](data, mode="draft")


@pytest.mark.parametrize("source,target,semantics,shock_type,down,up", [
    ("pp", None, "additive", "percentage_point", 0.75, 0.85),
    ("bp", None, "additive", "basis_point", 0.7995, 0.8005),
    ("pp", "basis_point", "additive", "basis_point", 0.75, 0.85),
    ("bp", "ratio", "additive", "percentage_point", 0.7995, 0.8005),
    ("percent", None, "multiplicative", "percent", 0.76, 0.84),
])
def test_share_correct_numeric_contracts_remain_valid(runtime, source, target, semantics, shock_type, down, up):
    data = runtime["model"]("capacity")
    test = runtime["build"](parameter_id="capacity_utilization_base_2026", value=5,
                            input_unit=source, engine_unit=target, shock_semantics=semantics)
    data["sensitivity_tests"] = [test]
    actual = runtime["run"](data, mode="draft")["sensitivities"][0]
    assert actual["shock_type"] == shock_type
    assert actual["requested_values"]["down"] == pytest.approx(down)
    assert actual["requested_values"]["up"] == pytest.approx(up)


def count_document(runtime, unit):
    data = runtime["model"]("volume")
    ids = set()
    for parameter in data["parameters"]:
        if parameter["dimension"] == "quantity":
            parameter["unit"] = unit
            ids.add(parameter["parameter_id"])
    for claim in data["evidence_claims"]:
        if claim.get("target_id") in ids and "unit" in claim:
            claim["unit"] = unit
    return data


@pytest.mark.parametrize("parameter_unit,record_unit", [
    ("units", "million_units"), ("million units", "units"),
    ("thousand units", "million_units"), ("units", "thousand_units"),
])
def test_count_record_scale_must_match_actual_parameter(runtime, parameter_unit, record_unit):
    data = count_document(runtime, parameter_unit)
    data["sensitivity_tests"] = [runtime["build"](
        parameter_id="volume_saleable_volume_base_2027", value=5,
        input_unit=record_unit, shock_semantics="absolute",
    )]
    with pytest.raises(runtime["error"], match="unit|scale"):
        runtime["run"](data, mode="draft")


@pytest.mark.parametrize("parameter_unit,source,target,expected", [
    ("units", "units", None, 5),
    ("million units", "million_units", None, 5),
    ("thousand units", "thousand_units", None, 5),
    ("units", "million_units", "units", 5_000_000),
    ("million units", "units", "million_units", 0.000005),
])
def test_count_real_conversion_enters_native_revenue(runtime, parameter_unit, source, target, expected):
    data = count_document(runtime, parameter_unit)
    data["sensitivity_tests"] = [runtime["build"](
        parameter_id="volume_saleable_volume_base_2027", value=5, input_unit=source,
        engine_unit=target, shock_semantics="absolute",
    )]
    output = runtime["run"](data, mode="draft")
    actual = output["sensitivities"][0]
    assert actual["shock_value"] == pytest.approx(expected)
    assert actual["requested_values"]["up"] == pytest.approx(100 + expected)
    assert actual["up_terminal_revenue"] == pytest.approx(200 + 2 * expected)


@pytest.mark.parametrize("parameter_unit", ["tonnes", "transactions per day", "USD million"])
def test_count_unknown_or_composite_parameter_unit_is_diagnostic(runtime, parameter_unit):
    data = count_document(runtime, parameter_unit)
    data["sensitivity_tests"] = [runtime["build"](
        parameter_id="volume_saleable_volume_base_2027", value=5,
        input_unit="units", shock_semantics="absolute",
    )]
    with pytest.raises(runtime["error"], match="safely interpreted|count unit"):
        runtime["run"](data, mode="draft")


def test_no_record_legacy_model_is_not_reinterpreted(runtime):
    data = runtime["model"]("volume")
    before = copy.deepcopy(data)
    result = runtime["run"](data, mode="draft")
    assert result["consolidated_forecast"]["base"]["terminal_revenue"] == pytest.approx(200)
    assert data == before
