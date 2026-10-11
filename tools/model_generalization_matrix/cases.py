"""Frozen CaseSpec for the model generalization matrix (node A).

Each case declares, BEFORE any implementation runs:

* ``drivers``  — the literal input drivers (frozen source of truth);
* ``build()``  — a builder producing the native input via the *legal* engine
  constructions (``model_document``/``calibrated_document``/``add_target``/...),
  deep-copied per case so no helper mutation leaks between cases;
* ``observe()``— how to read the relevant numbers back out of a result;
* ``expected`` — the independent oracle (``oracle.py``) computed from ``drivers``
  alone, never from any engine output.

A case also carries a ``verify_input`` step: after ``build()`` we re-read the
base-scenario driver values out of the built input and require them to equal the
frozen ``drivers``.  A mismatch means the builder is contaminated and the case is
invalid — this is the anti-contamination guarantee the test-suite exercises.

Only the 8 combination classes are covered, each with one legal vector and one
counter/unknown vector (16 cases).  This is a finite, repeatable engineering
matrix — not a second forecast engine and not a buy-side accuracy claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from . import oracle as O
from .oracle import Expected

# Frozen forecast horizon shared by the model_document constructions.
YEARS = [2026, 2027]


# --- input construction helpers ------------------------------------------

def _param_value(data: dict[str, Any], pid: str) -> float:
    for p in data["parameters"]:
        if p["parameter_id"] == pid:
            return float(p["value"])
    raise KeyError(f"missing parameter: {pid}")


def _set_param(data: dict[str, Any], pid: str, value: float) -> None:
    """Set a parameter value AND its evidence-claim value consistently.

    ``finalize_contract`` bakes ``extracted_value`` into each claim; mutating only
    the parameter would trigger a claim-value mismatch inside the engine.  This
    helper keeps both in sync so a mutated case stays a *legal* construction.
    """
    for p in data["parameters"]:
        if p["parameter_id"] == pid:
            p["value"] = value
            for cid in p.get("claim_ids", []):
                for c in data.get("evidence_claims", []):
                    if c.get("claim_id") == cid and "extracted_value" in c:
                        c["extracted_value"] = value
    else:
        pass


def _base_drivers(data: dict[str, Any]) -> dict[str, list[float]]:
    """Read the base-scenario driver values back out of a built input."""
    seg = data["segments"][0]
    ids = seg["scenarios"]["base"]["driver_parameter_ids"]
    return {
        driver: [_param_value(data, p) for p in pids]
        for driver, pids in ids.items()
    }


def _base_revenue_params(data: dict[str, Any]) -> list[float]:
    seg = data["segments"][0]
    ids = seg["scenarios"]["base"]["driver_parameter_ids"]["revenue"]
    return [_param_value(data, p) for p in ids]


# --- builders (each deep-copies and returns a fresh input) ----------------

def _build_unit_sales() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_industry_end_to_end import model_document

    data = model_document("unit_sales")

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        base = result["segments"][0]["scenarios"]["base"]
        return {"revenue": dict(base["recognized_revenue"])}

    return data, observe


def _build_arr_bridge() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_industry_end_to_end import model_document

    data = model_document("subscription_arr_bridge")

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        base = result["segments"][0]["scenarios"]["base"]
        return {"revenue": dict(base["recognized_revenue"])}

    return data, observe


def _build_arr_bridge_missing() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_industry_end_to_end import model_document

    data = model_document("subscription_arr_bridge")
    # Counter: drop the required new_arr driver.  A legal engine must refuse the
    # input outright rather than silently zero-fill the missing data.
    for seg in data["segments"]:
        for sc in seg["scenarios"].values():
            sc["driver_parameter_ids"].pop("new_arr", None)

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        return {"revenue": dict(result["segments"][0]["scenarios"]["base"]["recognized_revenue"])}

    return data, observe


def _build_launch_capacity() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_industry_end_to_end import model_document

    data = model_document("commercial_launch")

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        base = result["segments"][0]["scenarios"]["base"]
        return {"revenue": dict(base["recognized_revenue"])}

    return data, observe


def _build_launch_zero_cap() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_industry_end_to_end import model_document

    data = model_document("commercial_launch")
    for sc in ("low", "base", "high"):
        for yr in (2026, 2027):
            _set_param(data, f"commercial_launch_annual_supply_capacity_{yr}_{sc}", 0.0)

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        base = result["segments"][0]["scenarios"]["base"]
        return {"revenue": dict(base["recognized_revenue"])}

    return data, observe


def _build_zero_base_launch() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_industry_end_to_end import model_document

    data = model_document("commercial_launch")
    # Zero the base so CAGR is structurally undefined (base = 0).
    _set_param(data, "reported_total", 0.0)
    _set_param(data, "segment_base", 0.0)
    for rec in data["historical_revenue"]:
        rec["value"] = 0.0
    for c in data.get("evidence_claims", []):
        if c.get("target_id") == "historical_revenue:2024":
            c["extracted_value"] = 0.0
        if c.get("target_id") == "historical_revenue:2025":
            c["extracted_value"] = 0.0

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        base = result["consolidated_forecast"]["base"]
        return {
            "cagr": base.get("cagr"),
            "terminal": base.get("terminal_revenue"),
            "annual": dict(base.get("annual_revenue", {})),
        }

    return data, observe


def _build_period_flow_cross_fy() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_m3_period_flow_contract import schema_3_9_document, add_flow_parameter

    data = schema_3_9_document()
    # A six-month flow that crosses calendar years but sits inside the FY window.
    add_flow_parameter(data, "seg_h1_2026", 55.0, "2026-01-01", "2026-06-30", 2026)

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        return {"annual": dict(result["consolidated_forecast"]["base"]["annual_revenue"])}

    return data, observe


def _build_period_flow_out_of_window() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_m3_period_flow_contract import schema_3_9_document, add_flow_parameter

    data = schema_3_9_document()
    # Counter: FY2026 label with calendar-2025 dates — outside the declared window.
    # A missing/misaligned quarter must not be treated as 0; it must be refused.
    add_flow_parameter(data, "seg_bad", 10.0, "2025-01-01", "2025-06-30", 2026)

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        return {"annual": dict(result["consolidated_forecast"]["base"]["annual_revenue"])}

    return data, observe


def _build_quarter_delay_shock() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_recognition_bridge import forecast_document, add_parameter
    from test_data_contract import finalize_contract
    from research.timing_bridge import build_quarter_delay_bridge

    data = forecast_document()
    deferred = {s: add_parameter(data, f"q4_deferred_{s}", 20.0, 2026, s) for s in ("low", "base", "high")}
    catch_up = {
        s: add_parameter(data, f"catch_up_{s}", 0.75, 2027, s, dimension="ratio")
        for s in ("low", "base", "high")
    }
    for p in data["parameters"]:
        if p["parameter_id"] in deferred.values():
            p["measurement_period"] = "FY2026Q4"
        if p["parameter_id"] in catch_up.values():
            p["unit"] = "ratio"
    stressed, _receipt = build_quarter_delay_bridge(
        data,
        segment_name="Segment A",
        from_period="FY2026Q4",
        to_period="FY2027Q1",
        deferred_parameter_ids=deferred,
        catch_up_parameter_ids=catch_up,
        prefix="joint_delay",
        rationale="One shared financing/delivery delay stress applied exactly once.",
    )
    finalize_contract(stressed)

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        return {"annual": dict(result["consolidated_forecast"]["base"]["annual_revenue"])}

    return stressed, observe


def _build_shock_baseline() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_recognition_bridge import forecast_document

    data = forecast_document()

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        return {"annual": dict(result["consolidated_forecast"]["base"]["annual_revenue"])}

    return data, observe


def _build_conversion_mixed_units() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    # No forecast input: this case drives the unit/currency conversion entry
    # directly (the runner handles kind="conversion").  Cross-family and
    # cross-currency conversions must raise, never silently re-label.
    return {"conversion": True}, (lambda _r: {})


def _build_shared_cap_constraint() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_recognition_bridge import forecast_document, add_parameter
    from test_data_contract import finalize_contract
    from research.timing_bridge import build_quarter_delay_bridge

    data = forecast_document()
    # First apply the shared joint delay stress (so segment shares move), then
    # impose one fixed shared cap across every scenario.  Because the cap is
    # identical for low/base/high it can change segment shares and cross coherent
    # scenario paths; a legal engine must refuse to force Low<=Base<=High rather
    # than silently re-ordering the scenarios.
    deferred = {s: add_parameter(data, f"q4_def_{s}", 20.0, 2026, s) for s in ("low", "base", "high")}
    catch_up = {
        s: add_parameter(data, f"catch_{s}", 0.75, 2027, s, dimension="ratio")
        for s in ("low", "base", "high")
    }
    for p in data["parameters"]:
        if p["parameter_id"] in deferred.values():
            p["measurement_period"] = "FY2026Q4"
        if p["parameter_id"] in catch_up.values():
            p["unit"] = "ratio"
    stressed, _ = build_quarter_delay_bridge(
        data,
        segment_name="Segment A",
        from_period="FY2026Q4",
        to_period="FY2027Q1",
        deferred_parameter_ids=deferred,
        catch_up_parameter_ids=catch_up,
        prefix="shared_cap_jd",
        rationale="Shared joint stress to move segment shares before the shared cap.",
    )
    caps: dict[str, list[str]] = {}
    for s in ("low", "base", "high"):
        caps[s] = [
            add_parameter(stressed, f"shared_capacity_{s}_{yr}", value, yr, s, dimension="revenue")
            for yr, value in zip(stressed["forecast_years"], [140.0, 160.0])
        ]
    stressed["revenue_constraints"] = [
        {
            "constraint_id": "shared",
            "type": "sum_cap",
            "segments": ["Segment A", "Segment B"],
            "allocation": "proportional",
            "scenario_parameter_ids": caps,
            "rationale": "Synthetic shared delivery cap; no separate capacity double count.",
        }
    ]
    finalize_contract(stressed)

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        return {"annual": dict(result["consolidated_forecast"]["base"]["annual_revenue"])}

    return stressed, observe


def _build_target_annual() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_recognition_bridge import forecast_document
    from test_management_targets import add_target

    data = add_target(forecast_document(), target_value=144.0, measurement_basis="annual_period")

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        t = result["management_target_coverage"]["targets"][0]
        return {
            "comparison_value": t.get("comparison_value"),
            "measurement_basis": t.get("measurement_basis"),
        }

    return data, observe


def _build_target_runrate() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_recognition_bridge import forecast_document
    from test_management_targets import add_target

    # Counter: a run-rate/period-end target must not masquerade as the current
    # annual figure without an explicit conversion.  Either the engine refuses
    # it or it leaves a gap (comparison_value null) — never an invented annual.
    data = add_target(
        forecast_document(),
        target_value=200.0,
        measurement_basis="run_rate_at_period_end",
    )

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        t = result["management_target_coverage"]["targets"][0]
        return {
            "comparison_value": t.get("comparison_value"),
            "measurement_basis": t.get("measurement_basis"),
        }

    return data, observe


def _build_support_calibrated() -> tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]:
    from test_research_evidence_roles import calibrated_document

    data = calibrated_document()

    def observe(result: dict[str, Any]) -> dict[str, Any]:
        cells: dict[str, str] = {}
        for seg in result["segments"]:
            for e in seg["entries"]:
                cells[f"{seg['segment']}|{e['scenario']}|{e['year']}"] = e["status"]
        return {"cells": cells, "economic_truth_inferred": result["economic_truth_inferred"]}

    return data, observe


# --- CaseSpec ------------------------------------------------------------

@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    cls: str
    vector: str  # "legal" | "counter" | "unknown"
    boundary: str
    kind: str  # "forecast" | "conversion" | "support" | "shock_pair"
    drivers: dict[str, Any]
    build: Callable[[], tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]]
    expected: Expected
    # For "shock_pair" the case runs baseline then stressed and observes the delta.
    build_baseline: Callable[
        [], tuple[dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]]
    ] | None = None
    expected_input_drivers: dict[str, list[float]] | None = None
    # Legal same-family conversions asserted natively: (value, in_unit, eng_unit, expected_engine_value).
    extra_conversions: tuple[tuple[float, str, str, float], ...] = ()


def _e(values: dict[str, Any], **kw: Any) -> Expected:
    return Expected(values=values, **kw)


CASES: list[CaseSpec] = [
    # ---- M01 quantity x price x currency/unit ----
    CaseSpec(
        case_id="M01-L",
        cls="M01",
        vector="legal",
        boundary="quantity x price computes revenue at an explicit currency/unit label",
        kind="forecast",
        drivers={
            "model": "unit_sales",
            "units": [10.0, 12.0],
            "unit_revenue": [5.0, 5.0],
            "timing_factor": [1.0, 1.0],
        },
        build=_build_unit_sales,
        expected=_e(
            {
                "revenue": {
                    "2026": O.unit_sales_revenue([10.0, 12.0], [5.0, 5.0], [1.0, 1.0])[0],
                    "2027": O.unit_sales_revenue([10.0, 12.0], [5.0, 5.0], [1.0, 1.0])[1],
                }
            },
            conservation={"units_times_price": "revenue == units*unit_revenue*timing"},
        ),
        expected_input_drivers={"units": [10.0, 12.0], "unit_revenue": [5.0, 5.0]},
        # Same-dimension scaling keeps the economic amount: 5 usd_million is the
        # same money as 5000 usd_thousand (x1000), never an FX move.
        extra_conversions=((5.0, "usd_million", "usd_thousand", 5000.0),),
    ),
    CaseSpec(
        case_id="M01-C",
        cls="M01",
        vector="counter",
        boundary="mixed currency/units are refused or explicitly converted, never auto-FX",
        kind="conversion",
        drivers={
            "value": 5.0,
            "cross_currency": ["usd_million", "rmb_million"],
            "cross_family": ["percent", "usd_million"],
        },
        build=_build_conversion_mixed_units,
        expected=_e({}, reject=True, reject_reason="incompatible unit conversion"),
    ),
    # ---- M02 ARR stock -> recognition + late contract/churn ----
    CaseSpec(
        case_id="M02-L",
        cls="M02",
        vector="legal",
        boundary="closing ARR is not full-year revenue; revenue follows the committed bridge",
        kind="forecast",
        drivers={
            "model": "subscription_arr_bridge",
            "opening_arr": [100.0, 125.0],
            "gross_retention_rate": [0.9, 0.9],
            "expansion_arr": [15.0, 20.0],
            "new_arr": [20.0, 30.0],
            "lost_arr_revenue_fraction": [0.75, 0.5],
            "expansion_revenue_fraction": [0.5, 0.5],
            "new_arr_revenue_fraction": [0.25, 0.25],
            "closing_arr": [125.0, 162.5],
        },
        build=_build_arr_bridge,
        expected=_e(
            {
                "revenue": {
                    "2026": O.arr_bridge_revenue(
                        [100.0, 125.0], [0.9, 0.9], [15.0, 20.0], [20.0, 30.0],
                        [0.75, 0.5], [0.5, 0.5], [0.25, 0.25],
                    )[0],
                    "2027": O.arr_bridge_revenue(
                        [100.0, 125.0], [0.9, 0.9], [15.0, 20.0], [20.0, 30.0],
                        [0.75, 0.5], [0.5, 0.5], [0.25, 0.25],
                    )[1],
                }
            },
            conservation={"closing_arr_is_not_revenue": "closing ARR stock != recognized revenue"},
        ),
        expected_input_drivers={"opening_arr": [100.0, 125.0], "new_arr": [20.0, 30.0]},
    ),
    CaseSpec(
        case_id="M02-C",
        cls="M02",
        vector="counter",
        boundary="a missing ARR driver is refused, never zero-filled",
        kind="forecast",
        drivers={"model": "subscription_arr_bridge", "missing": "new_arr"},
        build=_build_arr_bridge_missing,
        # Hand-derived: missing data must not be zero-filled, so the entry must
        # refuse.  The exact contract wording is engine implementation detail;
        # assert a genuine ForecastInputError carrying a non-empty reason.
        expected=_e({}, reject=True, reject_reason=None),
    ),
    # ---- M03 capacity/demand/launch fraction ----
    CaseSpec(
        case_id="M03-L",
        cls="M03",
        vector="legal",
        boundary="demand is capped by capacity; the launch fraction is applied exactly once",
        kind="forecast",
        drivers={
            "model": "commercial_launch",
            "eligible_units": [1000.0, 1200.0],
            "adoption_rate": [0.1, 0.2],
            "annual_supply_capacity": [80.0, 300.0],
            "commercial_year_fraction": [0.5, 1.0],
            "net_revenue_per_unit": [2.0, 2.0],
        },
        build=_build_launch_capacity,
        expected=_e(
            {
                "revenue": {
                    "2026": O.commercial_launch_revenue(
                        [1000.0, 1200.0], [0.1, 0.2], [80.0, 300.0], [0.5, 1.0], [2.0, 2.0]
                    )[0],
                    "2027": O.commercial_launch_revenue(
                        [1000.0, 1200.0], [0.1, 0.2], [80.0, 300.0], [0.5, 1.0], [2.0, 2.0]
                    )[1],
                }
            },
            conservation={
                "launch_fraction_once": "revenue uses min(demand,capacity)*fraction*price (fraction once)",
            },
        ),
        expected_input_drivers={
            "eligible_units": [1000.0, 1200.0],
            "annual_supply_capacity": [80.0, 300.0],
        },
    ),
    CaseSpec(
        case_id="M03-C",
        cls="M03",
        vector="counter",
        boundary="zero capacity yields finite zero revenue, never unbounded growth",
        kind="forecast",
        drivers={
            "model": "commercial_launch",
            "eligible_units": [1000.0, 1200.0],
            "adoption_rate": [0.1, 0.2],
            "annual_supply_capacity": [0.0, 0.0],
            "commercial_year_fraction": [0.5, 1.0],
            "net_revenue_per_unit": [2.0, 2.0],
        },
        build=_build_launch_zero_cap,
        expected=_e(
            {
                "revenue": {
                    "2026": O.commercial_launch_revenue(
                        [1000.0, 1200.0], [0.1, 0.2], [0.0, 0.0], [0.5, 1.0], [2.0, 2.0]
                    )[0],
                    "2027": O.commercial_launch_revenue(
                        [1000.0, 1200.0], [0.1, 0.2], [0.0, 0.0], [0.5, 1.0], [2.0, 2.0]
                    )[1],
                }
            },
            conservation={"finite_zero": "0 capacity -> revenue 0 (finite, not unbounded)"},
        ),
        expected_input_drivers={"annual_supply_capacity": [0.0, 0.0]},
    ),
    # ---- M04 dated acquisition/control + cross-FY partial windows ----
    CaseSpec(
        case_id="M04-L",
        cls="M04",
        vector="legal",
        boundary="a cross-calendar partial window inside the FY is accepted at its real coverage",
        kind="period_flow",
        drivers={
            "flow": {"start": "2026-01-01", "end": "2026-06-30", "year": 2026, "value": 55.0},
            "months": 6,
        },
        build=_build_period_flow_cross_fy,
        expected=_e({"months": 6.0}),
        expected_input_drivers=None,
    ),
    CaseSpec(
        case_id="M04-C",
        cls="M04",
        vector="counter",
        boundary="a dated flow outside its declared FY window is refused, not zero-filled",
        kind="period_flow",
        drivers={
            "flow": {"start": "2025-01-01", "end": "2025-06-30", "year": 2026, "value": 10.0},
        },
        build=_build_period_flow_out_of_window,
        expected=_e({}, reject=True, reject_reason="must lie within the FY2026 window"),
    ),
    # ---- M05 zero-base commercial launch + CAGR ----
    CaseSpec(
        case_id="M05-L",
        cls="M05",
        vector="legal",
        boundary="zero-base launch revenue is computable",
        kind="forecast",
        drivers={
            "model": "commercial_launch",
            "base_revenue": 0.0,
            "eligible_units": [1000.0, 1200.0],
            "adoption_rate": [0.1, 0.2],
            "annual_supply_capacity": [80.0, 300.0],
            "commercial_year_fraction": [0.5, 1.0],
            "net_revenue_per_unit": [2.0, 2.0],
        },
        build=_build_zero_base_launch,
        expected=_e(
            {
                "cagr": O.cagr(0.0, 480.0, len(YEARS)),
                "terminal": 480.0,
                "annual": {
                    "2026": O.commercial_launch_revenue(
                        [1000.0, 1200.0], [0.1, 0.2], [80.0, 300.0], [0.5, 1.0], [2.0, 2.0]
                    )[0],
                    "2027": O.commercial_launch_revenue(
                        [1000.0, 1200.0], [0.1, 0.2], [80.0, 300.0], [0.5, 1.0], [2.0, 2.0]
                    )[1],
                },
            },
            unknown_fields=("cagr",),
        ),
    ),
    CaseSpec(
        case_id="M05-C",
        cls="M05",
        vector="unknown",
        boundary="CAGR from a zero base is undefined=null, not 0 growth nor a bad forecast",
        kind="forecast",
        drivers={"base_revenue": 0.0, "expected_cagr": None},
        build=_build_zero_base_launch,
        expected=_e({"cagr": None}, unknown_fields=("cagr",)),
    ),
    # ---- M06 shared shock + joint scenarios ----
    CaseSpec(
        case_id="M06-L",
        cls="M06",
        vector="legal",
        boundary="a shared shock propagates once; the joint volume/price path conserves the delta",
        kind="shock_pair",
        drivers={
            "deferred": 20.0,
            "catch_up_fraction": 0.75,
            "delta_2026": -20.0,
            "delta_2027": 15.0,
            "delta_sum": -5.0,
        },
        build=_build_quarter_delay_shock,
        build_baseline=_build_shock_baseline,
        expected=_e(
            {
                "delta_2026": -20.0,
                "delta_2027": 15.0,
                "delta_sum": -5.0,
            },
            conservation={"shock_applied_once": "the deferred drop appears once (not double)"},
        ),
    ),
    CaseSpec(
        case_id="M06-C",
        cls="M06",
        vector="counter",
        boundary="a fixed shared cap that would force Low<=Base<=High is refused, not reordered",
        kind="forecast",
        drivers={"shared_cap": [140.0, 160.0], "scenarios": ["low", "base", "high"]},
        build=_build_shared_cap_constraint,
        expected=_e({}, reject=True, reject_reason="scenario ordering"),
    ),
    # ---- M07 management target + gross/net/cannibalization ----
    CaseSpec(
        case_id="M07-L",
        cls="M07",
        vector="legal",
        boundary="a comparable annual target keeps its own value and basis",
        kind="forecast",
        drivers={"target_value": 144.0, "measurement_basis": "annual_period"},
        build=_build_target_annual,
        expected=_e(
            {
                "comparison_value": O.annual_target_comparison(144.0, "annual_period"),
                "measurement_basis": "annual_period",
            },
            conservation={"annual_target_keeps_value": "comparable annual target maps to its value"},
        ),
    ),
    CaseSpec(
        case_id="M07-C",
        cls="M07",
        vector="counter",
        boundary="a run-rate/period-end target is not re-labelled as the current annual figure",
        kind="forecast",
        drivers={"target_value": 200.0, "measurement_basis": "run_rate_at_period_end"},
        build=_build_target_runrate,
        expected=_e(
            {},
            reject=True,
            reject_reason="requires explicit annual recognized revenue conversion",
        ),
    ),
    # ---- M08 optional operating support + segment/year/scenario + future actual ----
    CaseSpec(
        case_id="M08-L",
        cls="M08",
        vector="legal",
        boundary="support is scoped per segment/year/scenario; one calibrated cell never presumes another",
        kind="support",
        drivers={
            "calibrated_cell": "Segment A|base|2026",
            "uncalibrated_cell": "Segment A|base|2027",
            "other_segment": "Segment B|base|2026",
        },
        build=_build_support_calibrated,
        expected=_e(
            {
                "cells": {
                    "Segment A|low|2026": "supported",
                    "Segment A|base|2026": "supported",
                    "Segment A|high|2026": "supported",
                    "Segment A|base|2027": "unsupported",
                    "Segment B|base|2026": "unsupported",
                },
                "economic_truth_inferred": False,
            },
            conservation={
                "no_presumed_support": "calibrated cell A/2026 does not extend to A/2027 or B/2026",
            },
        ),
    ),
    CaseSpec(
        case_id="M08-C",
        cls="M08",
        vector="unknown",
        boundary="an unknown observed range/actual stays null, never coerced to 0",
        kind="support",
        drivers={"observed_range": None},
        build=_build_support_calibrated,
        expected=_e({"unknown_stays_null": True}, unknown_fields=("observed_range",)),
    ),
]


def case_index() -> dict[str, CaseSpec]:
    return {c.case_id: c for c in CASES}
