"""W05-RF-FLOW composition/scope/unit tests for dated consolidated contributions.

What a dated window may and may not do once schema 3.10 accepts it:

* a partial contribution may compose a full year only through an explicit
  derived sum — it can never pose as a complete FY base/total by itself;
* overlapping components (H1 + Q2, group total + acquired standalone over the
  same window) double count and need an explicit rationale (口径解释) — an
  unexplained full-year gap is never silently zero-filled (pre-acquisition
  out-of-scope is not "missing data");
* estimates keep the analyst_assumption/scenario_stress kinds; point-in-time
  stocks (net assets, customer counts, period-end equity) are never revenue;
* currency/scale (CNY 亿 / USD million / USD billion) stay document-consistent
  and conversions recompute; conflicting same-window facts keep failing.

Fixture amounts are synthetic except the sealed control-window fact
(2026-05-31..2026-06-30, 1,291,902.08 CNY).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from contracts.evidence import Collector, ForecastInputError, MultiValidationError  # noqa: E402
from revenue_core import validate_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402
from test_w05_dated_contribution_contract import (  # noqa: E402
    DATED_SCHEMA,
    add_window_parameter,
    parameter,
    schema_3_10_document,
)

SCOPE_RATIONALE = (
    "pre-control window 2026-01-01..2026-05-30 is outside the group "
    "consolidation perimeter from control date 2026-05-31 (out-of-scope, not "
    "missing data, never zero-filled); amounts are the sealed purchase-to-end "
    "flow plus an explicit H2 estimate"
)


def add_acquisition_composition(data: dict, *, rationale: str | None) -> str:
    """C1: FY2026 contribution = sealed post-control flow + explicit H2 estimate."""
    add_window_parameter(
        data, "cmp_post_2026", 1.29190208, "2026-05-31", "2026-06-30", 2026,
        definition="acquired entity revenue from control date to period end (purchase-to-end)",
    )
    add_window_parameter(
        data, "cmp_h2_2026", 40.0, "2026-07-01", "2026-12-31", 2026,
        kind="analyst_assumption", claim=False,
        definition="H2 2026 contribution estimate under continued control",
        rationale="synthetic H2 contribution estimate; fixture amount, not a reported figure",
    )
    add_window_parameter(
        data, "cmp_fy2026", 41.29190208, "2026-01-01", "2026-12-31", 2026,
        kind="derived_fact", claim=False, formula="x0+x1",
        input_parameter_ids=["cmp_post_2026", "cmp_h2_2026"],
        definition="full-year group contribution of the acquired entity",
        rationale=rationale,
    )
    return "cmp_fy2026"


class DatedCompositionTests(unittest.TestCase):
    def test_acquisition_contribution_composes_full_year_with_scope_explanation(self) -> None:
        data = schema_3_10_document()
        add_acquisition_composition(data, rationale=SCOPE_RATIONALE)
        validated = validate_document(data)
        composed = validated["parameter_index"]["cmp_fy2026"]
        # Hand check: 1.29190208 + 40.0 = 41.29190208 — no implicit x2/x12/day scaling.
        self.assertAlmostEqual(
            composed["value"],
            1.29190208 + 40.0,
            places=9,
        )
        self.assertEqual(composed["period_start"], "2026-01-01")
        self.assertEqual(composed["period_end"], "2026-12-31")

    def test_full_year_composition_without_explanation_rejected(self) -> None:
        # Missing full-year basis / unexplained gap: the pre-control window is
        # neither composed nor explained, so the full-year claim is dishonest.
        data = schema_3_10_document()
        add_acquisition_composition(data, rationale=None)
        with self.assertRaisesRegex(ForecastInputError, "composition"):
            validate_document(data)

    def test_gap_is_never_silently_zero_filled(self) -> None:
        # A one-component "full year" equals only the post-control window;
        # the missing months must not default to zero revenue.
        data = schema_3_10_document()
        add_window_parameter(
            data, "cmp_post_2026", 1.29190208, "2026-05-31", "2026-06-30", 2026,
        )
        add_window_parameter(
            data, "cmp_fy2026_silent", 1.29190208, "2026-01-01", "2026-12-31", 2026,
            kind="derived_fact", claim=False, formula="x0",
            input_parameter_ids=["cmp_post_2026"],
            definition="full-year contribution claimed from the control window alone",
        )
        with self.assertRaisesRegex(ForecastInputError, "composition"):
            validate_document(data)

    def test_overlapping_components_rejected_without_explanation(self) -> None:
        data = schema_3_10_document()
        add_window_parameter(data, "cmp_h1", 55.0, "2026-01-01", "2026-06-30", 2026)
        add_window_parameter(data, "cmp_q2", 30.0, "2026-04-01", "2026-06-30", 2026)
        add_window_parameter(
            data, "cmp_double", 85.0, "2026-01-01", "2026-06-30", 2026,
            kind="derived_fact", claim=False, formula="x0+x1",
            input_parameter_ids=["cmp_h1", "cmp_q2"],
            definition="H1 total merged with its own Q2 subset",
        )
        with self.assertRaisesRegex(ForecastInputError, "composition"):
            validate_document(data)

    def test_overlapping_components_allowed_with_explicit_rationale(self) -> None:
        data = schema_3_10_document()
        add_window_parameter(data, "cmp_h1", 55.0, "2026-01-01", "2026-06-30", 2026)
        add_window_parameter(data, "cmp_q2", 30.0, "2026-04-01", "2026-06-30", 2026)
        add_window_parameter(
            data, "cmp_overlap_explained", 85.0, "2026-01-01", "2026-06-30", 2026,
            kind="derived_fact", claim=False, formula="x0+x1",
            input_parameter_ids=["cmp_h1", "cmp_q2"],
            definition="disclosed overlapping composition",
            rationale="Q2 is a subset of H1; the overlap is intentional and disclosed here",
        )
        validate_document(data)

    def test_cross_entity_same_window_merge_rejected_without_explanation(self) -> None:
        # Group total and acquired-entity standalone revenue over the same
        # window cannot be silently merged into one "group" number.
        data = schema_3_10_document()
        add_window_parameter(
            data, "group_h1", 500.0, "2026-01-01", "2026-06-30", 2026,
            definition="group consolidated revenue H1",
        )
        add_window_parameter(
            data, "acq_standalone_h1", 20.0, "2026-01-01", "2026-06-30", 2026,
            definition="acquired entity standalone revenue H1",
        )
        add_window_parameter(
            data, "merged_h1", 520.0, "2026-01-01", "2026-06-30", 2026,
            kind="derived_fact", claim=False, formula="x0+x1",
            input_parameter_ids=["group_h1", "acq_standalone_h1"],
            definition="group plus acquired standalone merged as one scope",
        )
        with self.assertRaisesRegex(ForecastInputError, "composition"):
            validate_document(data)

    def test_residual_work_split_needs_explanation(self) -> None:
        # PROCESS-007 shape: core = group total - acquired contribution. The
        # inputs overlap in time, so the work split must be disclosed.
        data = schema_3_10_document()
        add_window_parameter(
            data, "group_h1", 500.0, "2026-01-01", "2026-06-30", 2026,
            definition="group consolidated revenue H1",
        )
        add_window_parameter(
            data, "acq_post", 1.29190208, "2026-05-31", "2026-06-30", 2026,
            definition="acquired entity revenue from control date to period end",
        )
        add_window_parameter(
            data, "core_h1_split", 498.70809792, "2026-01-01", "2026-06-30", 2026,
            kind="derived_fact", claim=False, formula="x0-x1",
            input_parameter_ids=["group_h1", "acq_post"],
            definition="core business H1 as a residual work split",
        )
        with self.assertRaisesRegex(ForecastInputError, "composition"):
            validate_document(data)
        parameter(data, "core_h1_split")["rationale"] = (
            "residual work split only: acquired contribution is not yet bridged "
            "for group internal eliminations; not a segment fact"
        )
        validate_document(data)

    def test_legal_explicit_sums_and_recognition_still_pass(self) -> None:
        data = schema_3_10_document()
        add_window_parameter(data, "split_h1", 60.0, "2026-01-01", "2026-06-30", 2026)
        add_window_parameter(data, "split_h2", 50.0, "2026-07-01", "2026-12-31", 2026)
        original = parameter(data, "0_base_2026")["value"]
        entry = parameter(data, "0_base_2026")
        entry.update(
            kind="derived_fact", formula="x0+x1",
            input_parameter_ids=["split_h1", "split_h2"],
            time_basis="period_flow", period_start="2026-01-01", period_end="2026-12-31",
        )
        validated = validate_document(data)
        self.assertEqual(validated["parameter_index"]["0_base_2026"]["value"], original)
        # The derived tolerance gate still rejects wrong compositions.
        entry["value"] = original + 10.0
        with self.assertRaisesRegex(ForecastInputError, "derived_fact"):
            validate_document(data)

    def test_partial_flow_cannot_be_annual_base_or_adjustment(self) -> None:
        for target, mutate in (
            ("segment base", lambda data: parameter(data, "segment_a_base").update(
                time_basis="period_flow", period_start="2025-01-01", period_end="2025-06-30",
                period="FY2025")),
            ("reported total", lambda data: parameter(data, "reported_total").update(
                time_basis="period_flow", period_start="2025-05-31", period_end="2025-06-30",
                period="FY2025")),
        ):
            with self.subTest(target=target):
                data = schema_3_10_document()
                mutate(data)
                with self.assertRaisesRegex(ForecastInputError, "annual"):
                    validate_document(data)

    def test_stock_and_net_asset_are_never_revenue(self) -> None:
        # Period-end equity/net-asset/customer counts are point-in-time stocks:
        # they cannot wear a period window and cannot be consumed as annual flow.
        data = schema_3_10_document()
        add_window_parameter(
            data, "closing_equity", 800.0, None, None, 2025,
            time_basis="point_in_time", claim=False,
            definition="period-end net assets stock",
        )
        parameter(data, "closing_equity")["dimension"] = "monetary_balance"
        with self.assertRaisesRegex(ForecastInputError, "period_start"):
            parameter(data, "closing_equity")["period_start"] = "2026-01-01"
            parameter(data, "closing_equity")["period_end"] = "2026-12-31"
            validate_document(data)
        from contracts.annual_consumption import validate_annual_consumption
        stock = {"parameter_id": "closing_stock", "time_basis": "point_in_time",
                 "period": "FY2026", "dimension": "monetary_balance", "value": 800.0}
        consumers = {"schema_version": DATED_SCHEMA, "fiscal_year_end": "12-31",
                     "segments": [{"base_revenue_parameter_id": "closing_stock"}]}
        with self.assertRaisesRegex(ForecastInputError, "annual"):
            validate_annual_consumption(consumers, {"closing_stock": stock})

    def test_currency_and_scale_must_match_the_document(self) -> None:
        data = schema_3_10_document()
        entry = {
            "parameter_id": "cny_flow", "kind": "reported_fact", "value": 1.29190208,
            "unit": "CNY million", "period": "FY2026",
            "definition": "CNY-denominated flow in a USD document",
            "scenario": None, "source_ids": ["filing"],
            "dimension": "revenue", "time_basis": "period_flow",
            "period_start": "2026-05-31", "period_end": "2026-06-30",
            "currency": "CNY", "scale": "million",
        }
        data["parameters"].append(entry)
        with self.assertRaisesRegex(ForecastInputError, "currency"):
            validate_document(data)
        entry.update(currency="USD", scale="billion", unit="USD billion")
        with self.assertRaisesRegex(ForecastInputError, "scale"):
            validate_document(data)

    def test_rmb_yi_and_usd_scale_denominations_recompute(self) -> None:
        # 1,291,902.08 CNY = 1.29190208 CNY million = 0.0129190208 CNY 亿, and
        # 1.29190208 USD million = 0.00129190208 USD billion. Each document
        # keeps one currency/scale and the conversion is recomputed here.
        self.assertAlmostEqual(1.29190208 / 100, 0.0129190208, places=12)
        self.assertAlmostEqual(0.0129190208 * 100 * 1_000_000, 1_291_902.08, places=6)
        self.assertAlmostEqual(1.29190208 / 1000, 0.00129190208, places=12)
        for currency, scale, factor in (
            ("CNY", "million", 1.0),
            ("CNY", "亿", 1.0 / 100),
            ("USD", "billion", 1.0 / 1000),
        ):
            with self.subTest(currency=currency, scale=scale):
                data = redenominated_document(currency, scale, factor)
                add_window_parameter(
                    data, "cmp_post_2026", 1.29190208 * factor, "2026-05-31", "2026-06-30", 2026,
                    unit=f"{currency} {scale}",
                    definition="acquired entity revenue from control date to period end",
                )
                validated = validate_document(data)
                written = validated["parameter_index"]["cmp_post_2026"]["value"]
                self.assertAlmostEqual(written * (100 if scale == "亿" else 1000 if scale == "billion" else 1), 1.29190208, places=9)

    def test_estimates_keep_assumption_kinds_and_reported_facts_need_evidence(self) -> None:
        data = schema_3_10_document()
        add_window_parameter(
            data, "estimate_window", 5.0, "2026-07-01", "2026-08-15", 2026,
            kind="scenario_stress", claim=False, rationale="stress case, synthetic",
        )
        validate_document(data)
        # A reported dated fact without any source/claim is not evidence-backed.
        data = schema_3_10_document()
        add_window_parameter(
            data, "unevidenced_window", 5.0, "2026-05-31", "2026-06-30", 2026,
            claim=False,
        )
        with self.assertRaises(ForecastInputError):
            validate_document(data)

    def test_same_window_fact_conflicts_still_fail_on_3_10(self) -> None:
        definition = "Segment A recognized revenue"
        data = schema_3_10_document()
        add_window_parameter(data, "window_first", 55.0, "2026-01-01", "2026-06-30", 2026, definition=definition)
        add_window_parameter(data, "window_second", 65.0, "2026-01-01", "2026-06-30", 2026, definition=definition)
        with self.assertRaisesRegex(ForecastInputError, "conflict|resolution"):
            validate_document(data)
        for pid in ("window_first", "window_second"):
            entry = parameter(data, pid)
            entry["assertion_status"] = "primary" if pid == "window_first" else "secondary"
            entry["resolution_status"] = "accepted" if pid == "window_first" else "rejected"
        validate_document(data)

    def test_collect_all_keeps_composition_violations_in_their_own_gate(self) -> None:
        data = schema_3_10_document()
        add_acquisition_composition(data, rationale=None)
        collector = Collector()
        with self.assertRaises(MultiValidationError):
            validate_document(data, collector=collector)
        self.assertTrue(any("composition" in message for _, message in collector.errors))


def redenominated_document(currency: str, scale: str, factor: float) -> dict:
    """Re-denominate the fixture into ``currency scale``, recomputing amounts."""
    data = forecast_document()
    data["schema_version"] = DATED_SCHEMA
    data["currency"] = currency
    data["unit"] = scale
    for entry in data["parameters"]:
        if "currency" in entry:
            entry["currency"] = currency
            entry["scale"] = scale
            entry["unit"] = f"{currency} {scale}"
            entry["value"] = entry["value"] * factor
    for record in data["historical_revenue"]:
        record["value"] = record["value"] * factor
    for claim in data["evidence_claims"]:
        unit = claim.get("unit")
        if isinstance(unit, str) and unit.startswith("USD "):
            claim["unit"] = f"{currency} {scale}"
            if "extracted_value" in claim:
                claim["extracted_value"] = claim["extracted_value"] * factor
    return data


if __name__ == "__main__":
    unittest.main()
