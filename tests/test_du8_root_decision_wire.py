"""ROOT: preserve the JSON bool/null decision contract across both owners."""
from __future__ import annotations

import copy

import pytest

from test_du8_target_report_roundtrip import MODELS
from models import constrained_model, growth_model
from revenue_core import ForecastInputError, canonical_sha256, run_forecast
from revenue_publication import _payload_sha256, _receipt_sha256
from revenue_report import validate_forecast_output

FACTORIES = {**MODELS, "constrained": constrained_model}


def reseal(result):
    out = copy.deepcopy(result)
    receipt = out.get("publication_receipt")
    if isinstance(receipt, dict):
        receipt.pop("receipt_sha256", None)
        receipt.pop("validated_payload_sha256", None)
        receipt["validated_payload_sha256"] = _payload_sha256(out)
        receipt["receipt_sha256"] = _receipt_sha256(receipt)
    out["result_sha256"] = canonical_sha256(
        {key: value for key, value in out.items() if key != "result_sha256"}
    )
    return out


@pytest.mark.parametrize("name", sorted(FACTORIES))
@pytest.mark.parametrize("replacement_kind", ["integer", "float", "string", "null"])
@pytest.mark.parametrize("input_bound", [False, True])
def test_decision_cannot_be_replaced_by_equal_or_truthy_json_value(
    tmp_path, monkeypatch, name, replacement_kind, input_bound,
):
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(tmp_path / "registry.jsonl"))
    data = FACTORIES[name]()
    result = run_forecast(data)
    validate_forecast_output(result, data if input_bound else None)
    row = next(iter(result["management_target_coverage"]["targets"][0]["scenario_comparison"].values()))
    assert type(row["meets_target"]) is bool
    original = row["meets_target"]
    row["meets_target"] = {
        "integer": int(original), "float": float(original),
        "string": "true" if original else "", "null": None,
    }[replacement_kind]
    with pytest.raises(ForecastInputError):
        validate_forecast_output(reseal(result), data if input_bound else None)


def test_typed_unknown_growth_remains_null_and_is_not_false(tmp_path, monkeypatch):
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(tmp_path / "registry.jsonl"))
    data = growth_model()
    data["management_targets"][0]["comparison_basis"]["base_period"] = None
    result = run_forecast(data)
    rows = result["management_target_coverage"]["targets"][0]["scenario_comparison"]
    assert rows
    assert all(row["meets_target"] is None for row in rows.values())
    assert all(row["comparison_status"] == "not_comparable" for row in rows.values())
    validate_forecast_output(result, data)
    next(iter(rows.values()))["meets_target"] = False
    with pytest.raises(ForecastInputError):
        validate_forecast_output(reseal(result), data)
