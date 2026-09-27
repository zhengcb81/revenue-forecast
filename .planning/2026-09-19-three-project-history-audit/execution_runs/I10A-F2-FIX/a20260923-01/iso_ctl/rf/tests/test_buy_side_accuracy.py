"""Economic accuracy checks: point-in-time reuse, pooling and benchmark skill."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from contracts.document import validate_historical_accuracy_records  # noqa: E402
from revenue_backtest import create_snapshot, evaluate_snapshot, _benchmark_diagnostics  # noqa: E402
from revenue_core import ForecastInputError, canonical_sha256, run_forecast  # noqa: E402
from test_backtest import actuals_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def rehash(record):
    record["record_sha256"] = canonical_sha256({k: v for k, v in record.items() if k != "record_sha256"})
    return record


def record_for(data, *, origin="2023-03-01", available="2024-03-01", error=20, actual=100, count=2):
    return rehash({
        "record_schema_version": "1.1", "backtest_id": canonical_sha256({"backtest": origin, "available": available}),
        "snapshot_id": canonical_sha256({"snapshot": origin}), "evaluation_sha256": canonical_sha256({"evaluation": origin}),
        **{key: data[key] for key in ("company_name", "currency", "unit", "fiscal_year_end")},
        "forecast_as_of_date": origin, "actuals_as_of_date": available,
        "observations": count, "sum_absolute_error": error, "sum_absolute_actual": actual,
        "wape": None if actual == 0 else error / actual, "mae": error / count, "mean_smape": 0.1,
    })


def test_future_evaluation_cannot_inflate_historical_confidence():
    data = forecast_document()
    evaluation = evaluate_snapshot(create_snapshot(data, "accuracy-review"), actuals_document())
    data["historical_accuracy_records"] = [evaluation["accuracy_record"]]
    with pytest.raises(ForecastInputError, match="future information leak"):
        run_forecast(data)


@pytest.mark.parametrize("field,value", [("company_name", "Other Co"), ("currency", "EUR"),
                                      ("unit", "billion"), ("fiscal_year_end", "06-30")])
def test_wrong_comparison_perimeter_rejected(field, value):
    data = forecast_document()
    record = record_for(data)
    record[field] = value
    data["historical_accuracy_records"] = [rehash(record)]
    with pytest.raises(ForecastInputError, match=f"{field} mismatch"):
        validate_historical_accuracy_records(data)


def test_wape_pools_error_totals_instead_of_averaging_ratios():
    data = forecast_document()
    data["historical_accuracy_records"] = [
        record_for(data, error=20, actual=100),
        record_for(data, origin="2024-03-01", available="2025-03-01", error=10, actual=1000),
    ]
    wape, count = validate_historical_accuracy_records(data)
    assert wape == pytest.approx(30 / 1100)
    assert count == 4


def test_zero_actual_cohort_errors_remain_in_pooled_wape_numerator():
    data = forecast_document()
    data["historical_accuracy_records"] = [
        record_for(data, error=20, actual=0),
        record_for(data, origin="2024-03-01", available="2025-03-01", error=10, actual=100),
    ]
    assert validate_historical_accuracy_records(data) == (0.3, 4)


def test_same_origin_cannot_be_counted_twice_via_new_version():
    data = forecast_document()
    one = record_for(data)
    two = copy.deepcopy(one)
    two["backtest_id"] = canonical_sha256({"backtest": "different-version"})
    two["snapshot_id"] = canonical_sha256({"snapshot": "different-version"})
    data["historical_accuracy_records"] = [one, rehash(two)]
    with pytest.raises(ForecastInputError, match="duplicate historical forecast origin"):
        validate_historical_accuracy_records(data)


@pytest.mark.parametrize("field", ["backtest_id", "snapshot_id", "evaluation_sha256"])
def test_accuracy_record_requires_artifact_identifiers(field):
    data = forecast_document()
    record = record_for(data)
    del record[field]
    data["historical_accuracy_records"] = [rehash(record)]
    with pytest.raises(ForecastInputError, match=field):
        validate_historical_accuracy_records(data)


@pytest.mark.parametrize("field", ["backtest_id", "snapshot_id", "evaluation_sha256"])
@pytest.mark.parametrize("value", ["not-a-hash", "g" * 64, "a" * 63, True])
def test_accuracy_artifact_identifiers_must_be_hex(field, value):
    data = forecast_document()
    record = record_for(data)
    record[field] = value
    data["historical_accuracy_records"] = [rehash(record)]
    with pytest.raises(ForecastInputError, match=field):
        validate_historical_accuracy_records(data)


def test_same_snapshot_cannot_be_counted_twice_with_changed_origin():
    data = forecast_document()
    one = record_for(data)
    two = record_for(data, origin="2024-03-01", available="2025-03-01")
    two["snapshot_id"] = one["snapshot_id"]
    data["historical_accuracy_records"] = [one, rehash(two)]
    with pytest.raises(ForecastInputError, match="duplicate historical forecast snapshot"):
        validate_historical_accuracy_records(data)


def test_scored_summary_discloses_provenance_audit_limit():
    data = forecast_document()
    data["historical_accuracy_records"] = [record_for(data)]
    result = run_forecast(data)
    assert any("not source provenance" in item and "artifacts require audit" in item
               for item in result["confidence"]["limitations"])


def test_legacy_record_readable_but_not_evidence_of_point_in_time_skill():
    data = forecast_document()
    data["historical_accuracy_records"] = [rehash({"record_schema_version": "1.0",
        "backtest_id": "old", "observations": 100, "wape": 0})]
    assert validate_historical_accuracy_records(data) == (None, 0)


def test_rehashed_inconsistent_totals_rejected():
    data = forecast_document()
    record = record_for(data)
    record["wape"] = 0
    data["historical_accuracy_records"] = [rehash(record)]
    with pytest.raises(ForecastInputError, match="WAPE totals mismatch"):
        validate_historical_accuracy_records(data)


def test_scaled_accuracy_uses_frozen_training_changes():
    data = forecast_document()
    result = evaluate_snapshot(create_snapshot(data, "benchmark-review"), actuals_document())
    diag = result["benchmark_diagnostics"]
    history = [row["value"] for row in data["historical_revenue"]]
    scale = sum(abs(b - a) for a, b in zip(history, history[1:])) / (len(history) - 1)
    assert diag["mase"] == pytest.approx((5 + 11.5) / 2 / scale)
    assert diag["flat_base_mae"] == pytest.approx(15)
    assert diag["mae_skill_vs_flat_base"] == pytest.approx(1 - 16.5 / 30)
    assert result["summary"]["bias_amount"] == pytest.approx(8.25)
    assert result["summary"]["rmse"] == pytest.approx(((25 + 132.25) / 2) ** 0.5)


def test_constant_or_zero_history_does_not_invent_scaled_accuracy():
    for history in ([], [{"year": 2024, "value": 0}, {"year": 2025, "value": 0}]):
        result = _benchmark_diagnostics({"historical_revenue": history, "base_revenue": 0},
            {"2026": {"actual": 0, "absolute_error": 5, "squared_error": 25, "horizon_years": 1}})
        assert result["mase"] is None
        assert result["rmsse"] is None
        assert result["mae_skill_vs_flat_base"] is None
        assert result["historical_cagr_mae"] is None
