"""Load the real native engine modules for the generalization matrix.

The tool never re-implements a model.  It imports the shipped ``scripts/``
interfaces and hands them to :class:`native.NativeEngine`.  ``sys.path`` is
arranged so the same imports the test-suite uses resolve identically here.
No network, no source DB, no third-party packages.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace


def repo_root() -> Path:
    # tools/model_generalization_matrix/bootstrap.py -> repo root is parents[2]
    return Path(__file__).resolve().parents[2]


def load_runtime() -> SimpleNamespace:
    root = repo_root()
    for entry in (root / "scripts", root / "tests", root):
        p = str(entry)
        if p not in sys.path:
            sys.path.insert(0, p)

    from revenue_core import canonical_sha256, run_forecast, validate_document  # noqa: E402
    from research.evidence_roles import analyze_operating_research
    from research.input_quantities import (  # noqa: E402
        convert_input_quantity,
        validate_input_quantity_record,
    )
    from research_support_diagnostics import build_support_diagnostics  # noqa: E402
    from contracts.period_flow import period_flow_months  # noqa: E402
    from forecast.segments import resolve_adjustments  # noqa: E402
    from revenue_backtest import _summarize_records  # noqa: E402
    from trust_anchor import verify_input_binding  # noqa: E402

    def evaluate_draft_scope(snapshot: dict) -> dict:
        """Evaluate the declared scope of a *draft* forecast result.

        The shipped ``revenue_backtest.evaluate_snapshot`` expects a formal
        snapshot (publication receipt, registry anchor, published validator).
        A draft result intentionally has none of those, so the tool drives the
        same shipped pieces the backtest uses for the scoped evaluation — the
        snapshot binding check, the declared segment/scenario paths and the
        shipped error summarizer — instead of re-implementing any arithmetic.
        """
        forecast = snapshot["forecast_result"]
        segments = forecast["segments"]
        base_path = forecast["consolidated_forecast"]["base"]["annual_revenue"]
        low_path = forecast["consolidated_forecast"]["low"]["annual_revenue"]
        high_path = forecast["consolidated_forecast"]["high"]["annual_revenue"]
        years = [str(y) for y in forecast["forecast_years"]]

        # Reuse the shipped error-record builder so the scoped metrics (WAPE,
        # MAE, coverage) are the engine's own, not a local formula.
        import revenue_backtest as _bt

        company_records = []
        for year in years:
            company_records.append(
                {
                    **_bt._error_record(
                        float(base_path[year]),
                        float(base_path[year]),
                        float(low_path[year]),
                        float(high_path[year]),
                        float(forecast["base_revenue"]),
                    ),
                    "horizon_years": int(year) - int(forecast["base_year"]),
                }
            )
        segment_cells = {}
        for segment in segments:
            cells = {}
            for scenario in ("low", "base", "high"):
                output = segment["scenarios"][scenario]
                path = output.get("effective_revenue", output["recognized_revenue"])
                for year in years:
                    cells[f"{segment['name']}|{scenario}|{year}"] = float(path[year])
            segment_cells[segment["name"]] = cells
        return {
            "schema_version": "revenue-backtest-draft-scope/1",
            "snapshot_id": snapshot["snapshot_id"],
            "company_name": forecast["company_name"],
            "currency": forecast["currency"],
            "unit": forecast["unit"],
            "fiscal_year_end": forecast["fiscal_year_end"],
            "forecast_as_of_date": forecast["as_of_date"],
            "declared_years": years,
            "scoped_segment_cells": segment_cells,
            "company_summary": _summarize_records(company_records),
            "segments": [segment["name"] for segment in segments],
            "base_year": int(forecast["base_year"]),
        }

    return SimpleNamespace(
        run_forecast=run_forecast,
        validate_document=validate_document,
        analyze_operating_research=analyze_operating_research,
        convert_input_quantity=convert_input_quantity,
        validate_input_quantity_record=validate_input_quantity_record,
        build_support_diagnostics=build_support_diagnostics,
        period_flow_months=period_flow_months,
        resolve_adjustments=resolve_adjustments,
        canonical_sha256=canonical_sha256,
        verify_input_binding=verify_input_binding,
        evaluate_draft_scope=evaluate_draft_scope,
        root=root,
    )
