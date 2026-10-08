"""Already recognized aggregate accounting must remain truthful and unchanged."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from revenue_core import ForecastInputError, run_forecast
from test_recognition_bridge import forecast_document
from test_data_contract import finalize_contract


def mixed_document():
    data = forecast_document()
    data["segments"][0]["recognition"].update({
        "timing": "mixed", "presentation": "mixed",
        "modeled_presentation": "mixed",
        "aggregation_boundary": (
            "Annual recognized revenue includes deliveries and services; "
            "policy components cannot be split from published segment totals."
        ),
    })
    return finalize_contract(data)


def test_mixed_recognized_aggregate_preserves_exact_revenue_and_output_contract():
    baseline = run_forecast(forecast_document(), mode="draft")
    result = run_forecast(mixed_document(), mode="draft")
    assert result["consolidated_forecast"] == baseline["consolidated_forecast"]
    for scenario in ("low", "base", "high"):
        path = result["segments"][0]["scenarios"][scenario]
        assert path["recognized_revenue"] == path["modeled_activity"]
        assert path["progress_values"] is None
        assert path["unrecognized_tail_activity"] == []
    assert result["segments"][0]["recognition"]["timing"] == "mixed"
    assert result["segments"][0]["recognition"]["presentation"] == "mixed"


@pytest.mark.parametrize("field", ["timing", "presentation"])
def test_mixed_requires_explicit_aggregate_boundary(field):
    data = mixed_document()
    data["segments"][0]["recognition"].pop("aggregation_boundary")
    if field == "timing":
        data["segments"][0]["recognition"].update(presentation="gross", modeled_presentation="gross")
    else:
        data["segments"][0]["recognition"]["timing"] = "point_in_time"
    with pytest.raises(ForecastInputError, match="aggregation_boundary"):
        run_forecast(data, mode="draft")


def test_mixed_rejects_lagged_activity():
    data = mixed_document()
    data["segments"][0]["recognition"]["mode"] = "lagged_activity"
    with pytest.raises(ForecastInputError, match="already recognized"):
        run_forecast(data, mode="draft")


def test_mixed_rejects_activity_model():
    data = mixed_document()
    for scenario in data["segments"][0]["scenarios"].values():
        scenario["model"] = "unit_sales"
    # Validate the accounting boundary before trying incompatible driver IDs.
    from forecast.segments import validate_recognition_metadata
    with pytest.raises(ForecastInputError, match="direct_growth/direct_revenue"):
        validate_recognition_metadata(data["segments"][0],
            {s["source_id"]: s for s in data["sources"]},
            {})


@pytest.mark.parametrize("field,value", [
    ("progress_parameter_ids", {"low": [], "base": [], "high": []}),
    ("progress_measure", "fake progress=1"),
    ("lag_years", 1),
    ("carry_in_parameter_ids", {"low": [], "base": [], "high": []}),
])
def test_mixed_cannot_hide_extra_recognition_transforms(field, value):
    data = mixed_document()
    data["segments"][0]["recognition"][field] = value
    with pytest.raises(ForecastInputError, match="recognition transform"):
        run_forecast(data, mode="draft")
