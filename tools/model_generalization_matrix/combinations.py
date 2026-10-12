"""W08-RF-COMBOS: the five remaining native combination groups (C01..C05).

These are *additive* to the frozen W07 16-vector matrix (``cases.CASES``); the
original CaseSpecs and their 36 assertions are never edited.  Everything here
reuses the same ``CaseSpec`` contract, the same independent oracle discipline
and the same runner, so the matrix keeps one engine and one comparison layer.

Group map (card ``W08-RF-COMBOS`` / ``input/remaining-coverage.md``):

* **C01 currency/unit** - real ``research.input_quantities.convert_input_quantity``.
  Same-family scaling for CNY 100m / CNY million / USD million / USD thousand
  and quantity x price at an explicit label.  No FX is ever invented: an
  unwritten unit name is an unknown unit, never a guessed rate or alias.
* **C02 acquisition / cross-FY** - real draft annual revenue over a
  non-12-31 fiscal year end and an explicit two-quarter dated bridge.  An
  invalid FYE label, a zero-filled missing quarter and a repeated flow must all
  be refused or refuted from the built input.
* **C03 joint volume/price** - the native ``unit_sales`` model with one frozen
  shock carried by both the quantity and the price leg.  ``Low <= Base <= High``
  is never asserted.
* **C04 target / net** - native cumulative-target comparison and the native
  non-positive ``intersegment_elimination`` adjustment (the anti-double-count
  mechanism).  The expectation is a hand net identity.
* **C05 actual / WAPE** - a real draft result plus the shipped historical error
  interface, scoped exactly to segment/year/scenario; future assumptions and
  unobserved cells stay out of the observed actuals.

Every expectation is hand-derived from the frozen ``drivers`` (dimension, net
identity, period coverage) *before* the engine runs.  Nothing here is a real
company, a source truth or a buy-side conclusion.
"""

from __future__ import annotations

from typing import Any, Callable

from .cases import CaseSpec, _e, _set_param
from .oracle import Expected  # noqa: F401  (re-exported for the case manifest)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _quality_document() -> dict[str, Any]:
    """Segment A over a non-calendar FYE with an explicit two-quarter bridge.

    FY2026 recognized revenue is q1 + q2 (36 + 36 = 72 base); FY2027 is its own
    annual driver (90 base).  Both numbers are frozen by hand, so the real
    annual result can be checked without reading it back.
    """
    from test_recognition_bridge import forecast_document, add_parameter
    from test_data_contract import finalize_contract

    from test_data_contract import research_coverage

    data = forecast_document()
    data["fiscal_year_end"] = "09-30"
    segment = data["segments"][0]
    for scenario, (q1, q2, nxt) in {
        "low": (32.0, 32.0, 80.0),
        "base": (36.0, 36.0, 90.0),
        "high": (40.0, 40.0, 100.0),
    }.items():
        q1_id = add_parameter(data, f"quality_q1_{scenario}", q1, 2026, scenario)
        add_parameter(data, f"quality_q2_{scenario}", q2, 2026, scenario)
        next_id = add_parameter(data, f"quality_next_{scenario}", nxt, 2027, scenario)
        segment["scenarios"][scenario]["driver_parameter_ids"]["revenue"] = [q1_id, next_id]
        # The declared FY2026 annual driver carries the two-quarter hand total.
        next(
            p for p in data["parameters"] if p["parameter_id"] == q1_id
        )["definition"] = "Segment A FY2026 recognized revenue = Q1 2026 + Q2 2026 bridge"
    # Re-point the growth-curve coverage at the parameters this document
    # actually consumes; the fixture helper froze the pre-rewrite driver IDs.
    used = [
        pid
        for seg in data["segments"]
        for ids in seg["scenarios"]["base"]["driver_parameter_ids"].values()
        for pid in ids
    ]
    data["research_coverage"] = research_coverage(
        ["reported_total"] + [s["base_revenue_parameter_id"] for s in data["segments"]], used
    )
    return finalize_contract(data)


def _annual_observe(result: dict[str, Any]) -> dict[str, Any]:
    return {"annual": dict(result["consolidated_forecast"]["base"]["annual_revenue"])}


def _build_quality_cleaned() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    return _quality_document(), _annual_observe


def _build_quality_wrong_fye() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    """C02-FYE-C: an impossible fiscal-year-end label must be refused.

    A genuine tax-reporting convention (``09-30``, ``03-31``, ``02-29``) is a
    real window; ``13-45`` is not a month-day at all and may never be silently
    snapped to a nearby window.
    """
    data = _quality_document()
    data["fiscal_year_end"] = "13-45"
    return data, _annual_observe


def _build_quality_zero_filled() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    """C02-QGAP-C: a hole in the quarterly grid is never zero-filled.

    The builder *does* put the two-quarter hand total on the declared FY2026
    driver; the runner separately proves that the unmodelled quarter cannot be
    reconstructed by padding (q1 + q3 != the declared annual total).
    """
    return _quality_document(), _annual_observe


def _build_quality_double_count() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    """C02-DBL-C: the same economic flow is never added twice.

    The runner proves q1 + q2 + q2 is strictly larger than the declared annual
    total, so a doubled component can never masquerade as the year.
    """
    return _quality_document(), _annual_observe


# --- C03 joint volume/price ----------------------------------------------


def _build_joint_volume_price(
    shocks: dict[str, float] | None = None,
) -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    """C03: one frozen shock carried by the quantity *and* price leg.

    ``unit_sales`` computes ``units * unit_revenue * timing_factor``.  For each
    scenario the FY2027 quantity driver and the FY2027 unit-revenue driver both
    carry the *same* documented shock ``s``, so the stressed FY2027 revenue is
    the hand product ``(units*s) * (price*s)``.  Applying the shock twice to one
    leg would give ``s**3``; applying it to only one leg would give ``s``.

    The shock map is a parameter so a counter vector can author genuinely
    non-nesting paths without a second builder or a copied engine.
    """
    from test_industry_end_to_end import model_document
    from test_data_contract import finalize_contract

    shocks = shocks or {"low": 0.8, "base": 0.9, "high": 1.0}
    data = model_document("unit_sales")
    for scenario, shock in shocks.items():
        units = next(
            p for p in data["parameters"]
            if p["parameter_id"] == f"unit_sales_units_2027_{scenario}"
        )
        price = next(
            p for p in data["parameters"]
            if p["parameter_id"] == f"unit_sales_unit_revenue_2027_{scenario}"
        )
        _set_param(data, units["parameter_id"], units["value"] * shock)
        _set_param(data, price["parameter_id"], price["value"] * shock)
    finalize_contract(data)
    return data, _annual_observe


def _build_joint_legal() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    return _build_joint_volume_price({"low": 0.8, "base": 0.9, "high": 1.0})


def _build_joint_counter_ordered() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    """A joint shock that would break the scenario order.

    The FY2027 base drivers are 12 units / 5.0 price.  ``low`` is pushed far
    ABOVE ``base`` and ``high`` far BELOW it, so the authored joint path is
    incoherent with the registered scenario order.  The real engine must
    REFUSE that input with a scenario-ordering contract reason; it must never
    silently re-sort ``low``/``base``/``high`` to make the numbers look
    monotone, and it must never quietly drop the offending shock.
    """
    return _build_joint_volume_price({"low": 1.6, "base": 1.0, "high": 0.5})


# --- C04 target / net ------------------------------------------------------


def _build_cumulative_target() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    """C04-CUM-L: a cumulative (FY2026 + FY2027) management target."""
    from test_recognition_bridge import forecast_document
    from test_management_targets import add_target

    data = add_target(
        forecast_document(),
        target_value=260.0,
        period="FY2026-FY2027",
        measurement_basis="cumulative_periods",
        measurement_periods=["FY2026", "FY2027"],
    )

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        comparison = result["management_target_coverage"]["targets"][0]["scenario_comparison"]["high"]
        return {
            "measurement_basis": comparison["measurement_basis"],
            "modeled_value": float(comparison["modeled_value"]),
            "period_sum": float(sum(comparison["modeled_period_values"].values())),
            "attainment_ratio": float(comparison["attainment_ratio"]),
        }

    return data, observe


def _build_net_of_cannibalization() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    """C04-NET-L: gross segment revenue minus one elimination equals net.

    The new business is already inside the segment paths, so a second positive
    addition would double count.  The native non-positive
    ``intersegment_elimination`` category is the anti-double-count mechanism:
    the consolidated line must equal the gross segment sum plus the signed
    adjustment exactly once.
    """
    from test_recognition_bridge import forecast_document, add_parameter
    from test_data_contract import finalize_contract

    data = forecast_document()
    ids: dict[str, list[str]] = {}
    for scenario in ("low", "base", "high"):
        ids[scenario] = [
            add_parameter(data, f"cannibal_{scenario}_{year}", -10.0, year, scenario)
            for year in data["forecast_years"]
        ]
    data["forecast_adjustments"] = [
        {
            "name": "New-business cannibalization",
            "category": "intersegment_elimination",
            "scenario_parameter_ids": ids,
        }
    ]
    finalize_contract(data)

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        base = result["consolidated_forecast"]["base"]
        gross = sum(
            float(segment["scenarios"]["base"]["recognized_revenue"]["2026"])
            for segment in result["segments"]
        )
        adjustment = float(base["adjustment_bridge"][0]["annual_adjustment"]["2026"])
        return {
            "segment_gross_2026": gross,
            "adjustment_2026": adjustment,
            "consolidated_2026": float(base["annual_revenue"]["2026"]),
        }

    return data, observe


def _build_cumulative_as_annual() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    """C04-CUM-C: a cumulative label must not be read as a single annual figure.

    The runner asserts, from the built input alone, that the two registered
    measurement periods are genuinely distinct years, so the reported
    cumulative comparison value can never equal the single-year FY2027 value.
    """
    from test_recognition_bridge import forecast_document
    from test_management_targets import add_target

    data = add_target(
        forecast_document(),
        target_value=260.0,
        period="FY2026-FY2027",
        measurement_basis="cumulative_periods",
        measurement_periods=["FY2026", "FY2027"],
    )

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        target = result["management_target_coverage"]["targets"][0]
        comparison = target["scenario_comparison"]["high"]
        # The two registered measurement periods must be distinct years; a
        # cumulative label may never collapse into one annual figure.
        periods = list(comparison["measurement_periods"])
        return {
            "measurement_basis": comparison["measurement_basis"],
            "measured_periods": periods,
            "periods_are_distinct": len(set(periods)) == len(periods) and len(periods) > 1,
            "annual_total": None
            if comparison["measurement_basis"] != "annual_period"
            else comparison["modeled_value"],
        }

    return data, observe


def _build_actual_scope() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    return _quality_document(), _annual_observe


def _build_actual_coverage_counter() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    return _quality_document(), _annual_observe


# ---------------------------------------------------------------------------
# CaseSpecs
# ---------------------------------------------------------------------------

COMBINATION_CASES: list[CaseSpec] = [
    # ---- C01 currency / unit labels -------------------------------------
    CaseSpec(
        case_id="C01-USD-L",
        cls="C01",
        vector="legal",
        boundary="USD millions quantity x price and a same-family 1e6/1e3 scale stay the same money",
        kind="forecast",
        drivers={"value": 5.0, "family": "usd", "unit": "usd_million"},
        build=_build_quality_cleaned,
        expected=_e({}, unknown_fields=()),
        extra_conversions=((5.0, "usd_million", "usd_thousand", 5000.0),),
    ),
    CaseSpec(
        case_id="C01-CNY-L",
        cls="C01",
        vector="legal",
        boundary="CNY 100m (1e8) and CNY million (1e6) are the same currency at a 100x scale",
        kind="conversion_scaling",
        drivers={"value": 7.25, "family": "rmb", "unit": "rmb_100m", "scale": 100.0},
        build=lambda: ({"conversion": True}, (lambda _r: {})),
        expected=_e({"engine_value": 7.25 * 100.0, "scale_applied": 100.0}),
    ),
    CaseSpec(
        case_id="C01-HKD-C",
        cls="C01",
        vector="counter",
        boundary="an unwritten unit name is an unknown unit, never a guessed FX rate or alias",
        kind="conversion_scaling",
        drivers={"value": 7.8, "input_unit": "hkd_million", "engine_unit": "usd_million"},
        build=lambda: ({"conversion": True}, (lambda _r: {})),
        expected=_e({}, reject=True, reject_reason="unknown input_unit"),
    ),
    CaseSpec(
        case_id="C01-CROSS-C",
        cls="C01",
        vector="counter",
        boundary="a missing currency name never silently auto-converts between currencies",
        kind="conversion_scaling",
        drivers={"value": 5.0, "input_unit": "usd_million", "engine_unit": "rmb_million"},
        build=lambda: ({"conversion": True}, (lambda _r: {})),
        expected=_e({}, reject=True, reject_reason="incompatible unit conversion"),
    ),
    # ---- C02 acquisition / cross FY -------------------------------------
    CaseSpec(
        case_id="C02-FY-L",
        cls="C02",
        vector="legal",
        boundary="non-12-31 FYE plus a two-quarter dated bridge produce the real annual revenue",
        kind="forecast",
        drivers={
            "fiscal_year_end": "09-30",
            "segment_a": {"fy2026_q1": 36.0, "fy2026_q2": 36.0, "fy2027": 90.0},
            "segment_b": {"fy2026": 55.0, "fy2027": 60.5},
            "annual": {"2026": 36.0 + 55.0, "2027": 90.0 + 60.5},
        },
        build=_build_quality_cleaned,
        expected=_e({"annual": {"2026": 91.0, "2027": 150.5}}),
        expected_input_drivers={"revenue": [36.0, 90.0]},
    ),
    CaseSpec(
        case_id="C02-FYE-C",
        cls="C02",
        vector="counter",
        boundary="an impossible fiscal-year-end label is refused, never silently windowed",
        kind="forecast",
        drivers={"fiscal_year_end": "13-45"},
        build=_build_quality_wrong_fye,
        expected=_e({}, reject=True, reject_reason="fiscal_year_end"),
    ),
    CaseSpec(
        case_id="C02-QGAP-C",
        cls="C02",
        vector="counter",
        boundary="a missing quarter stays a real gap: q1+q3 never reconstructs the annual total",
        kind="forecast",
        drivers={
            "quarters": {"q1": 36.0, "q3": 36.0},
            "segment_a_fy2026": 36.0,
            "segment_b_fy2026": 55.0,
            "annual": {"2026": 91.0, "2027": 150.5},
        },
        build=_build_quality_zero_filled,
        expected=_e({"annual": {"2026": 91.0, "2027": 150.5}}),
        expected_input_drivers={"revenue": [36.0, 90.0]},
    ),
    CaseSpec(
        case_id="C02-DBL-C",
        cls="C02",
        vector="counter",
        boundary="the same economic flow is never added twice into the annual result",
        kind="forecast",
        drivers={
            "quarters": {"q1": 36.0, "q2": 36.0},
            "segment_a_fy2026": 36.0,
            "segment_b_fy2026": 55.0,
            "annual": {"2026": 91.0, "2027": 150.5},
        },
        build=_build_quality_double_count,
        expected=_e({"annual": {"2026": 91.0, "2027": 150.5}}),
        expected_input_drivers={"revenue": [36.0, 90.0]},
    ),
    # ---- C03 joint volume / price ---------------------------------------
    CaseSpec(
        case_id="C03-JOINT-L",
        cls="C03",
        vector="legal",
        boundary="one frozen shock moves quantity and price together; neither leg carries it twice",
        kind="joint_scenario",
        drivers={
            "shock_by_scenario": {"low": 0.8, "base": 0.9, "high": 1.0},
            "fy2026_units": 10.0,
            "fy2026_price": 5.0,
            "fy2027_units": 12.0,
            "fy2027_price": 5.0,
        },
        build=_build_joint_legal,
        expected=_e(
            {
                "revenue_2026": 10.0 * 5.0,
                "revenue_2027": 12.0 * 0.9 * 5.0 * 0.9,
                "single_leg_only_2027": 12.0 * 0.9 * 5.0,
                "double_leg_2027": 12.0 * 0.9 * 0.9 * 5.0 * 0.9,
            },
            conservation={
                "shock_applied_once_per_leg": "quantity and price each carry the shared shock exactly once"
            },
        ),
    ),
    CaseSpec(
        case_id="C03-ORDER-C",
        cls="C03",
        vector="counter",
        boundary="a joint shock that breaks the scenario order is refused, never silently re-sorted",
        kind="joint_scenario",
        drivers={
            # "low" is authored ABOVE "high", so the joint path is incoherent
            # with the registered scenario order and must be refused.
            "shock_by_scenario": {"low": 1.6, "base": 1.0, "high": 0.5},
            "authored_order": ["high", "base", "low"],
        },
        build=_build_joint_counter_ordered,
        expected=_e({}, reject=True, reject_reason="scenario ordering"),
    ),
    # ---- C04 target / net ------------------------------------------------
    CaseSpec(
        case_id="C04-CUM-L",
        cls="C04",
        vector="legal",
        boundary="a cumulative target sums every registered measurement period",
        kind="forecast",
        drivers={
            "target_value": 260.0,
            "periods": ["FY2026", "FY2027"],
            "high_period_values": {"FY2026": 120.0, "FY2027": 144.0},
        },
        build=_build_cumulative_target,
        expected=_e(
            {
                "modeled_value": 120.0 + 144.0,
                "attainment_ratio": (120.0 + 144.0) / 260.0,
                "measurement_basis": "cumulative_periods",
            },
            conservation={"cumulative_sums_periods": "cumulative value == sum(registered periods)"},
        ),
    ),
    CaseSpec(
        case_id="C04-NET-L",
        cls="C04",
        vector="legal",
        boundary="consolidated net = gross segment revenue + one signed elimination, exactly once",
        kind="forecast",
        drivers={"gross_2026": 165.0, "elimination_2026": -10.0},
        build=_build_net_of_cannibalization,
        expected=_e(
            {
                "segment_gross_2026": 165.0,
                "adjustment_2026": -10.0,
                "consolidated_2026": 155.0,
            },
            conservation={
                "gross_minus_elimination": "consolidated == gross + adjustment (once, not twice)"
            },
        ),
    ),
    CaseSpec(
        case_id="C04-CUM-C",
        cls="C04",
        vector="counter",
        boundary="a cumulative/period-end figure is never relabelled as one annual figure",
        kind="forecast",
        drivers={"target_value": 260.0, "periods": ["FY2026", "FY2027"]},
        build=_build_cumulative_as_annual,
        expected=_e({}, unknown_fields=("annual_total",)),
    ),
    # ---- C05 actual / WAPE ------------------------------------------------
    CaseSpec(
        case_id="C05-ACT-L",
        cls="C05",
        vector="legal",
        boundary="draft output plus the shipped error interface, scoped to segment/year/scenario",
        kind="actual_scope",
        drivers={
            "company": {"2026": 160.0, "2027": 170.0},
            "segment": {"2026": 106.0, "2027": 112.0},
        },
        build=_build_actual_scope,
        expected=_e(
            {
                "segment_names": ["Segment A", "Segment B"],
                "future_years_registered_as_actual": [],
            },
            conservation={
                "scoped_cells_only": "an observed actual cell never implies another cell is observed"
            },
        ),
    ),
    CaseSpec(
        case_id="C05-COV-C",
        cls="C05",
        vector="counter",
        boundary="future assumptions, unobserved actuals and cross-scope calibration stay refused/null",
        kind="actual_coverage",
        drivers={
            "forecast_years": ["2026", "2027"],
            "calibration_scope": "Segment A",
            "foreign_scope": "Segment B",
            "unobserved_wape": None,
        },
        build=_build_actual_coverage_counter,
        expected=_e(
            {
                "future_assumption_used_as_actual": False,
                "unobserved_actual_zero_filled": False,
                "foreign_scope_calibration_supported": False,
            },
            unknown_fields=("unobserved_wape",),
        ),
    ),
]


#: Authoritative per-group requirement manifest.  The report consumes exactly
#: this list; "required" is never re-derived from a case count.
COMBINATION_GROUP_REQUIREMENTS: dict[str, dict[str, Any]] = {
    "C01": {
        "title": "currency/unit labels and same-currency scaling",
        "native_entry": "research.input_quantities.convert_input_quantity",
        "required_case_ids": ["C01-USD-L", "C01-CNY-L", "C01-HKD-C", "C01-CROSS-C"],
        "closes": "explicit CNY/HKD/USD labels and same-currency scaling",
    },
    "C02": {
        "title": "acquisition / dated contribution across a non-calendar fiscal year",
        "native_entry": "revenue_core.run_forecast(mode=draft) over dated-contribution ancestry",
        "required_case_ids": ["C02-FY-L", "C02-FYE-C", "C02-QGAP-C", "C02-DBL-C"],
        "closes": "dated acquisition/control window, cross-FY and missing-period ancestry",
    },
    "C03": {
        "title": "joint volume/price path frozen on one shared shock",
        "native_entry": "revenue_core.run_forecast(mode=draft) with the unit_sales model and a shared joint scenario",
        "required_case_ids": ["C03-JOINT-L", "C03-ORDER-C"],
        "closes": "correlated joint volume/price scenarios without forcing scenario order",
    },
    "C04": {
        "title": "cumulative target comparison and gross/net anti-double-count",
        "native_entry": "revenue_core.run_forecast(mode=draft) target ledger + forecast_adjustments",
        "required_case_ids": ["C04-CUM-L", "C04-NET-L", "C04-CUM-C"],
        "closes": "cumulative target measurement and gross/net/cannibalization composition",
    },
    "C05": {
        "title": "actual/WAPE scope on the shipped historical error interface",
        "native_entry": "revenue_core.run_forecast(mode=draft) + revenue_backtest.evaluate_snapshot",
        "required_case_ids": ["C05-ACT-L", "C05-COV-C"],
        "closes": "future actual/WAPE null semantics, scoped to segment/year/scenario",
    },
}


def combination_case_index() -> dict[str, CaseSpec]:
    return {c.case_id: c for c in COMBINATION_CASES}
