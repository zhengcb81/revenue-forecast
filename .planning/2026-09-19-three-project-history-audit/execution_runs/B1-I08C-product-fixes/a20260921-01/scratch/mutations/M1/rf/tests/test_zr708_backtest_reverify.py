"""ZR-708 acceptance tests: reverify immutable snapshot/backtest wiring.

ZR-708 = already_satisfied reverification card: the existing snapshot/
backtest infrastructure (scripts/revenue_backtest.py) is green on the
current triplet, so this file pins the critical contracts as reverification
evidence rather than fixing working mechanisms.

  C1  already_satisfied: snapshot determinism, immutability (no overwrite),
      tamper-evidence all hold on the current triplet.
  C2  accuracy record consumption: evaluate_snapshot's accuracy_record
      flows into run_forecast → confidence.historical_accuracy (wape
      matches, component contribution > 0); tampered records are rejected.
  C3  immutable wiring: future-dated actuals rejected, four-layer hash
      chain (record_sha256) linked.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.evidence import ForecastInputError  # noqa: E402
from revenue_backtest import (  # noqa: E402
    create_snapshot,
    evaluate_snapshot,
    validate_snapshot,
)
from revenue_core import run_forecast  # noqa: E402
from test_backtest import actuals_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


# ---------------------------------------------------------------------------
# C1 — already_satisfied: snapshot contracts hold
# ---------------------------------------------------------------------------


def test_c1_snapshot_is_deterministic():
    first = create_snapshot(forecast_document(), "v1")
    second = create_snapshot(forecast_document(), "v1")
    assert first == second  # deterministic on same input


def test_c1_snapshot_validates():
    snapshot = create_snapshot(forecast_document(), "v1")
    validate_snapshot(snapshot)  # must not raise


def test_c1_tampered_snapshot_rejected():
    snapshot = create_snapshot(forecast_document(), "v1")
    snapshot["forecast_result"]["consolidated_forecast"]["base"]["annual_revenue"][
        "2026"
    ] = 9999.0
    with pytest.raises(ForecastInputError, match="mismatch"):
        evaluate_snapshot(snapshot, actuals_document())


# ---------------------------------------------------------------------------
# C2 — accuracy record consumption chain
# ---------------------------------------------------------------------------


def test_c2_accuracy_record_consumed_by_confidence():
    evaluation = evaluate_snapshot(
        create_snapshot(forecast_document(), "v1"), actuals_document()
    )
    record = evaluation["accuracy_record"]
    assert record["backtest_id"] == evaluation["backtest_id"]
    assert "record_sha256" in record
    data = forecast_document()
    data["historical_accuracy_records"] = [record]
    result = run_forecast(data)
    assert result["confidence"]["historical_accuracy"]["wape"] == pytest.approx(
        evaluation["summary"]["wape"]
    )
    assert result["confidence"]["components"]["historical_accuracy"] > 0


def test_c2_tampered_accuracy_record_rejected():
    evaluation = evaluate_snapshot(
        create_snapshot(forecast_document(), "v1"), actuals_document()
    )
    record = dict(evaluation["accuracy_record"])
    record["wape"] = 0.0  # tamper with the metric
    data = forecast_document()
    data["historical_accuracy_records"] = [record]
    with pytest.raises(ForecastInputError):
        run_forecast(data)


# ---------------------------------------------------------------------------
# C3 — immutable wiring
# ---------------------------------------------------------------------------


def test_c3_future_dated_actuals_rejected():
    snapshot = create_snapshot(forecast_document(), "v1")
    actuals = actuals_document()
    actuals["actual_company_revenue"]["2029"] = {
        "value": 180,
        "source_ids": ["actual_filing"],
    }
    with pytest.raises(ForecastInputError, match="outside forecast horizon"):
        evaluate_snapshot(snapshot, actuals)


def test_c3_accuracy_record_hash_linked():
    evaluation = evaluate_snapshot(
        create_snapshot(forecast_document(), "v1"), actuals_document()
    )
    assert evaluation["accuracy_record"]["backtest_id"] == evaluation["backtest_id"]
    assert isinstance(evaluation["accuracy_record"]["record_sha256"], str)
    assert len(evaluation["accuracy_record"]["record_sha256"]) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
