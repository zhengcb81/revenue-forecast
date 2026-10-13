"""Independent ROOT checks: real dated ancestry and independent actuals."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model_generalization_matrix.bootstrap import load_runtime
from model_generalization_matrix.native import NativeEngine
from model_generalization_matrix.combinations import combination_case_index
from model_generalization_matrix.runner import run_case


@pytest.fixture
def engine(tmp_path, monkeypatch):
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(tmp_path / "registry"))
    return NativeEngine(load_runtime())


def test_dated_legal_uses_actual_window_ancestry(engine):
    spec = combination_case_index()["C02-FY-L"]
    data, _ = spec.build()
    assert data["schema_version"] == "3.10"
    assert data["fiscal_year_end"] == "09-30"
    assert data["forecast_adjustments"][0]["category"] == "acquisition_contribution"
    out = run_case(spec, engine)
    assert out.status == "PASS", out.diagnostics
    assert out.observed["annual"] == pytest.approx({"2026": 127, "2027": 210.5})
    assert out.observed["dated_windows"]
    assert out.observed["contribution"]["2026"] == 36


@pytest.mark.parametrize("key", ["C02-QGAP-C", "C02-DBL-C"])
def test_dated_missing_and_duplicate_rejected_by_real_engine(key, engine):
    spec = combination_case_index()[key]
    assert spec.expected.reject
    out = run_case(spec, engine)
    assert out.status == "REJECT_OK", (out.diagnostics, out.observed)
    assert out.native_refs[-1]["exception_type"] in {
        "ForecastInputError",
        "MultiValidationError",
    }
    assert (
        "composition" in out.observed["exception"]
        or "double counts" in out.observed["exception"]
    )


def test_backtest_calls_public_interface_with_independent_actuals(engine, monkeypatch):
    calls = []
    native = engine._rt.evaluate_snapshot

    def observed(snapshot, actuals):
        calls.append(actuals)
        return native(snapshot, actuals)

    monkeypatch.setattr(engine._rt, "evaluate_snapshot", observed)
    out = run_case(combination_case_index()["C05-ACT-L"], engine)
    assert out.status == "PASS", out.diagnostics
    assert calls[0]["actual_company_revenue"]["2026"]["value"] == 160
    assert out.observed["wape"] == pytest.approx(0.05)
    assert out.observed["segment_cells"] == ["Segment A|2026", "Segment A|2027"]
    assert out.observed["declared_years"] == ["2026", "2027"]
    ref = next(
        r for r in out.native_refs if r["entry"] == "revenue_backtest.evaluate_snapshot"
    )
    assert ref["request"]["actuals"]["actual_company_revenue"]["2027"]["value"] == 170


def test_wrong_actual_metric_fails_independent_oracle(engine, monkeypatch):
    native = engine._rt.evaluate_snapshot

    def wrong(snapshot, actuals):
        result = native(snapshot, actuals)
        result["summary"]["wape"] = 0
        return result

    monkeypatch.setattr(engine._rt, "evaluate_snapshot", wrong)
    out = run_case(combination_case_index()["C05-ACT-L"], engine)
    assert out.status == "FAIL"


def test_missing_actual_cells_stay_absent_and_foreign_wape_null(engine):
    out = run_case(combination_case_index()["C05-COV-C"], engine)
    assert out.status == "PASS", out.diagnostics
    assert out.observed["actual_company_years"] == ["2026"]
    assert out.observed["actual_segment_cells"] == ["Segment A|2026"]
    assert out.observed["unobserved_wape"] is None
    assert out.observed["foreign_scope_observations"] == 0
    assert "predates fiscal year end" in out.observed["future_actual_rejection"]


def test_backtest_infrastructure_error_cannot_be_dressed_as_rejection(
    engine, monkeypatch
):
    def broken(*args, **kwargs):
        raise RuntimeError("native failure")

    monkeypatch.setattr(engine._rt, "evaluate_snapshot", broken)
    out = run_case(combination_case_index()["C05-COV-C"], engine)
    assert out.status == "ERROR", out.observed
    assert "RuntimeError" in out.diagnostics["error"]
