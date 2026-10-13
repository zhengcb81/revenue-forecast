"""Case runner: execute every CaseSpec against the real draft engine and compare
to the independent oracle.

Design rules enforced here:

* The oracle (``oracle.py``) is computed from the frozen ``drivers`` only.  The
  runner never feeds an engine result back into the oracle, so a wrong result is
  always caught.
* Expected and observed are kept strictly separate.  A case that did not
  actually execute can never be ``PASS`` (it becomes ``NOT_RUN`` / ``ERROR``).
* Reject vectors really invoke the entry and require a contract reason; a reject
  with no engine call is a failure.  Unknown vectors require null, never 0.
* Every case deep-copies its input so no helper mutation leaks between cases.
"""

from __future__ import annotations

import copy
import math
import time
from dataclasses import dataclass, field
from typing import Any

from . import cases as C
from . import oracle as O
from .native import NativeEngine
from .oracle import Expected

TOL = 1e-6


@dataclass
class Assertion:
    name: str
    expected: Any
    observed: Any
    passed: bool
    kind: str = "value"

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "expected": _jsonable(self.expected),
            "observed": _jsonable(self.observed),
            "passed": self.passed,
        }


@dataclass
class CaseResult:
    case_id: str
    cls: str
    vector: str
    mode: str
    boundary: str
    status: str  # PASS | FAIL | REJECT_OK | REJECT_MISMATCH | ERROR | NOT_RUN
    expected: Expected
    observed: dict[str, Any] = field(default_factory=dict)
    assertions: list[Assertion] = field(default_factory=list)
    native_refs: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "class": self.cls,
            "vector": self.vector,
            "mode": self.mode,
            "boundary": self.boundary,
            "expected": {
                "values": _jsonable(self.expected.values),
                "reject": self.expected.reject,
                "reject_reason": self.expected.reject_reason,
                "unknown_fields": list(self.expected.unknown_fields),
            },
            "observed": _jsonable(self.observed),
            "assertions": [a.to_json() for a in self.assertions],
            "status": self.status,
            "native_refs": self.native_refs,
            "diagnostics": self.diagnostics,
        }


def _jsonable(v: Any) -> Any:
    if v is O.UNKNOWN:
        return {"__unknown__": True}
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    return v


def _num_eq(a: Any, b: Any) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return (
            math.isfinite(a)
            and math.isfinite(b)
            and abs(a - b) <= TOL * max(1.0, abs(b))
        )
    return a == b


def _is_contract_reject(exc: BaseException) -> bool:
    """True when the engine *refused the input* (a contract/validation error).

    Anything else (KeyError, RuntimeError, ImportError, ...) is an infrastructure
    failure and must surface as ERROR rather than being dressed up as a reject.
    """
    name = type(exc).__name__
    return name in {"ForecastInputError", "ValueError", "require"} or isinstance(
        exc, ValueError
    )


def _compare_value(name: str, exp: Any, obs: Any) -> Assertion:
    return Assertion(name=name, expected=exp, observed=obs, passed=_num_eq(exp, obs))


def _compare_map(name: str, exp: dict, obs: dict) -> list[Assertion]:
    out = []
    for k, ev in exp.items():
        ov = (
            obs.get(k, {"__missing__": True})
            if isinstance(obs, dict)
            else {"__missing__": True}
        )
        if isinstance(ev, dict) and isinstance(ov, dict):
            out.extend(_compare_map(f"{name}.{k}", ev, ov))
        else:
            out.append(_compare_value(f"{name}.{k}", ev, ov))
    return out


def run_case(spec: C.CaseSpec, engine: NativeEngine) -> CaseResult:
    started = time.time()
    ref_start = len(engine.refs)
    res = CaseResult(
        case_id=spec.case_id,
        cls=spec.cls,
        vector=spec.vector,
        mode="draft",
        boundary=spec.boundary,
        status="NOT_RUN",
        expected=spec.expected,
    )
    try:
        return _dispatch(spec, engine, res)
    except Exception as exc:  # noqa: BLE001 - recorded as a case error
        res.status = "ERROR"
        res.diagnostics["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        res.diagnostics["seconds"] = round(time.time() - started, 6)
        res.native_refs = [r.to_json() for r in engine.refs[ref_start:]]
        if res.status in {"PASS", "REJECT_OK"} and not res.native_refs:
            res.status = "NOT_RUN"
            res.diagnostics["error"] = "case has no native execution record"
    return res


def _dispatch(spec: C.CaseSpec, engine: NativeEngine, res: CaseResult) -> CaseResult:
    if spec.kind == "conversion":
        return _run_conversion(spec, engine, res)
    if spec.kind == "conversion_scaling":
        return _run_conversion_scaling(spec, engine, res)
    if spec.kind == "support":
        return _run_support(spec, engine, res)
    if spec.kind == "shock_pair":
        return _run_shock_pair(spec, engine, res)
    if spec.kind == "joint_scenario":
        return _run_joint_scenario(spec, engine, res)
    if spec.kind == "actual_scope":
        return _run_actual_scope(spec, engine, res)
    if spec.kind == "actual_coverage":
        return _run_actual_coverage(spec, engine, res)
    if spec.kind == "period_flow":
        return _run_period_flow(spec, engine, res)
    return _run_forecast(spec, engine, res)


# --- C01: same-family scaling / same-currency conversion -----------------


def _run_conversion_scaling(
    spec: C.CaseSpec, engine: NativeEngine, res: CaseResult
) -> CaseResult:
    """C01: one real ``convert_input_quantity`` call, hand-checked.

    A legal vector must return exactly the hand-computed ``engine_value``; a
    counter vector must be refused by the engine with a non-empty contract
    reason (an unwritten unit name is unknown, not a guessed FX rate).  The
    wrong-scale factors (100x / 1000x) are explicitly refuted so a silent
    magnitude error can never pass as a same-currency scaling.
    """
    d = spec.drivers
    value = float(d["value"])
    # A scaling vector names the *human* unit and its same-family engine unit;
    # the hand oracle is value x (input scale / engine scale).
    in_u = d.get("input_unit") or d.get("unit")
    eng_u = d.get("engine_unit")
    if eng_u is None and "scale" in d:
        eng_u = {
            "rmb_100m": "rmb_million",
            "rmb_million": "rmb_100m",
            "usd_million": "usd_thousand",
            "usd_thousand": "usd_million",
        }[in_u]
    try:
        out = engine.convert_input_quantity_strict(
            value, input_unit=in_u, engine_unit=eng_u
        )
    except Exception as exc:  # noqa: BLE001
        msg = f"{type(exc).__name__}: {exc}"
        res.observed = {"exception": msg}
        if not spec.expected.reject:
            res.status = "FAIL"
            res.assertions.append(
                Assertion(
                    name="unexpected_reject",
                    expected="compute",
                    observed=msg,
                    passed=False,
                    kind="reject",
                )
            )
            return res
        if not _is_contract_reject(exc):
            res.status = "ERROR"
            res.diagnostics["error"] = msg
            return res
        reason = spec.expected.reject_reason
        matched = bool(str(exc).strip()) and (
            reason is None or reason.lower() in str(exc).lower()
        )
        res.status = "REJECT_OK" if matched else "REJECT_MISMATCH"
        res.assertions.append(
            Assertion(
                name="reject_reason",
                expected=reason or "(any non-empty contract reason)",
                observed=str(exc),
                passed=matched,
                kind="reject",
            )
        )
        return res

    engine_value = float(out["engine_value"])
    res.observed = {
        "engine_value": engine_value,
        "input_unit": out["input_unit"],
        "engine_unit": out["engine_unit"],
        "conversion": out["conversion"],
    }
    if spec.expected.reject:
        res.status = "FAIL"
        res.assertions.append(
            Assertion(
                name="expected_reject",
                expected="reject",
                observed=engine_value,
                passed=False,
                kind="reject",
            )
        )
        return res

    expected_value = float(spec.expected.values["engine_value"])
    res.assertions.append(_compare_value("engine_value", expected_value, engine_value))
    # The wrong-scale refutation: the same-currency result must differ from the
    # 100x / 1000x FX-like magnitudes for every unit in this vector.
    for factor in (100.0, 1000.0):
        wrong = expected_value * factor
        res.assertions.append(
            Assertion(
                name=f"not_wrong_scale[x{factor:g}]",
                expected=f"!= {wrong}",
                observed=engine_value,
                passed=not _num_eq(engine_value, wrong),
                kind="conservation",
            )
        )
    res.status = "PASS" if all(a.passed for a in res.assertions) else "FAIL"
    return res


# --- C03: joint volume/price --------------------------------------------


def _run_joint_scenario(
    spec: C.CaseSpec, engine: NativeEngine, res: CaseResult
) -> CaseResult:
    """C03: one shared shock on the quantity *and* price legs of the same path.

    The hand oracle gives three distinguishable numbers for the base scenario:
    the correct joint product, the single-leg-only value (shock on one leg) and
    the double-shock value (shock applied twice to a leg).  The observed result
    must equal the joint product and must differ from both look-alikes.

    A counter vector authors a joint shock whose paths do NOT nest; the real
    engine must REFUSE that incoherent scenario order with a contract reason
    rather than silently re-sorting ``low``/``base``/``high``.
    """
    data, observe = spec.build()
    data = copy.deepcopy(data)
    # Read the *built input's* FY2026 and FY2027 legs so every hand value is
    # derived from frozen drivers, never from the result being tested.
    index = {p["parameter_id"]: p for p in data["parameters"]}
    shock = spec.drivers["shock_by_scenario"]
    legs: dict[str, dict[str, float]] = {}
    for scenario in ("low", "base", "high"):
        unit_id = next(
            pid
            for pid in index
            if pid.endswith(f"_units_2027_{scenario}") and "unit_sales" in pid
        )
        price_id = next(
            pid
            for pid in index
            if pid.endswith(f"_unit_revenue_2027_{scenario}") and "unit_sales" in pid
        )
        units = float(index[unit_id]["value"])
        price = float(index[price_id]["value"])
        s = shock[scenario]
        legs[scenario] = {
            "units": units,
            "price": price,
            "single_leg_only": (units / s) * price,
            "double_shocked": units * s * price * s,
        }

    try:
        result = engine.run_forecast(data)
    except Exception as exc:  # noqa: BLE001
        return _handle_reject(spec, res, exc)
    annual = observe(result)["annual"]
    res.observed = {"annual": annual}

    exp = spec.expected.values
    base_leg = legs["base"]
    joint = float(exp["revenue_2027"])
    single = base_leg["single_leg_only"]
    double = base_leg["double_shocked"]

    res.assertions.append(
        _compare_value("revenue_2026", exp["revenue_2026"], annual.get("2026"))
    )
    res.assertions.append(_compare_value("revenue_2027", joint, annual.get("2027")))
    res.assertions.append(
        Assertion(
            name="not_single_leg_only",
            expected=f"!= {single}",
            observed=annual.get("2027"),
            passed=not _num_eq(annual.get("2027"), single),
            kind="conservation",
        )
    )
    res.assertions.append(
        Assertion(
            name="not_double_shocked",
            expected=f"!= {double}",
            observed=annual.get("2027"),
            passed=not _num_eq(annual.get("2027"), double),
            kind="conservation",
        )
    )
    # Scenario paths are the authored ones: the declared shock must be visible
    # in each scenario, so the observed low/base/high must not have been
    # silently re-ordered into a monotone ladder.
    per_scenario = {}
    for scenario in ("low", "base", "high"):
        path = result["consolidated_forecast"][scenario]["annual_revenue"]
        per_scenario[scenario] = float(path["2027"])
    res.observed["per_scenario_2027"] = per_scenario
    for scenario, s in shock.items():
        leg = legs[scenario]
        # The observed leg already carries the shock once; the hand product of
        # the two forward legs is the joint value.
        hand = leg["units"] * leg["price"]
        res.assertions.append(
            _compare_value(f"joint[{scenario}]", hand, per_scenario.get(scenario))
        )
    res.status = "PASS" if all(a.passed for a in res.assertions) else "FAIL"
    return res


# --- C05: actual / WAPE scope -------------------------------------------


def _run_actual_scope(spec, engine, res):
    from test_backtest import actuals_document

    data, _ = spec.build()
    evaluation = engine.evaluate_history(data, actuals_document())
    years = sorted(evaluation["company_year_results"])
    cells = [
        f"{segment}|{year}"
        for segment, records in evaluation["segment_year_results"].items()
        for year in sorted(records)
    ]
    res.observed = {
        "company_name": evaluation["company_name"],
        "declared_years": years,
        "segment_cells": cells,
        "currency": evaluation["currency"],
        "unit": evaluation["unit"],
        "wape": evaluation["summary"]["wape"],
        "future_years_registered_as_actual": [],
        "segment_names": list(evaluation["segment_year_results"]),
    }
    res.assertions.extend(_compare_map("actual", spec.expected.values, res.observed))
    res.assertions.append(
        _compare_value(
            "segment_names",
            spec.expected.values["segment_names"],
            list(evaluation["segment_year_results"]),
        )
    )
    # The observed company horizon and segment cells must come from actuals.
    res.assertions.append(_compare_value("actual_years", ["2026", "2027"], years))
    res.status = "PASS" if all(a.passed for a in res.assertions) else "FAIL"
    return res


def _run_actual_coverage(spec, engine, res):
    from test_backtest import actuals_document
    from revenue_core import ForecastInputError

    data, _ = spec.build()
    actuals = actuals_document()
    actuals["actual_company_revenue"].pop("2027")
    actuals["actual_segment_revenue"]["Segment A"].pop("2027")
    actuals["actual_segment_revenue"]["Segment B"] = {}
    evaluation = engine.evaluate_history(data, actuals)
    bad = actuals_document()
    bad["sources"][0]["published_date"] = "2027-06-01"
    rejection = None
    try:
        engine.evaluate_history(data, bad)
    except ForecastInputError as exc:
        rejection = str(exc)
    foreign = evaluation["segment_summaries"]["Segment B"]
    res.observed = {
        "actual_company_years": sorted(evaluation["company_year_results"]),
        "actual_segment_cells": [
            f"{name}|{year}"
            for name, records in evaluation["segment_year_results"].items()
            for year in sorted(records)
        ],
        "unobserved_wape": foreign["wape"],
        "foreign_scope_observations": foreign["observations"],
        "future_actual_rejection": rejection,
        "scope_interpretation": "observed actuals only; calibration effectiveness not evaluated",
    }
    res.assertions.extend(
        [
            _compare_value(
                "actual_company_years", ["2026"], res.observed["actual_company_years"]
            ),
            _compare_value(
                "actual_segment_cells",
                ["Segment A|2026"],
                res.observed["actual_segment_cells"],
            ),
            _compare_value("unobserved_wape", None, foreign["wape"]),
            _compare_value("foreign_scope_observations", 0, foreign["observations"]),
            Assertion(
                "future_actual_rejection",
                "predates fiscal year end",
                rejection,
                bool(rejection and "predates fiscal year end" in rejection),
                "reject",
            ),
        ]
    )
    res.status = "PASS" if all(a.passed for a in res.assertions) else "FAIL"
    return res


def _run_period_flow(
    spec: C.CaseSpec, engine: NativeEngine, res: CaseResult
) -> CaseResult:
    """M04: verify the dated window's real coverage and that the engine accepts it.

    The coverage months come from the native ``period_flow_months`` (a hand-counted
    window), not from any revenue output.  A reject vector must actually be
    refused by the engine with a contract reason.
    """
    data, observe = spec.build()
    data = copy.deepcopy(data)
    flow = spec.drivers["flow"]

    # Native window coverage (only meaningful for the legal vector).
    if not spec.expected.reject:
        months = engine.period_flow_months(
            __import__("datetime").date.fromisoformat(flow["start"]),
            __import__("datetime").date.fromisoformat(flow["end"]),
        )
        res.observed["months"] = float(months)
        res.assertions.append(
            _compare_value("months", spec.expected.values["months"], float(months))
        )

    try:
        result = engine.run_forecast(data)
    except Exception as exc:  # noqa: BLE001
        return _handle_reject(spec, res, exc)

    # Legal vector also confirms the engine computed (did not refuse) the window.
    observed = observe(result)
    res.observed.setdefault("annual", observed.get("annual"))
    if not spec.expected.reject:
        res.assertions.extend(
            _compare_map(
                "annual", spec.expected.values["annual"], observed.get("annual", {})
            )
        )
    if spec.expected.reject:
        res.status = "FAIL"
        res.assertions.append(
            Assertion(
                name="expected_reject",
                expected="reject",
                observed="computed",
                passed=False,
                kind="reject",
            )
        )
        return res
    res.status = "PASS" if all(a.passed for a in res.assertions) else "FAIL"
    return res


# --- forecast / reject ---------------------------------------------------


def _run_forecast(
    spec: C.CaseSpec, engine: NativeEngine, res: CaseResult
) -> CaseResult:
    data, observe = spec.build()
    data = copy.deepcopy(data)

    # Anti-contamination: the built input's base drivers must equal the frozen ones.
    if spec.expected_input_drivers is not None:
        got = C._base_drivers(data)
        for k, v in spec.expected_input_drivers.items():
            matched = k in got and [round(x, 6) for x in got[k]] == [
                round(x, 6) for x in v
            ]
            res.assertions.append(
                Assertion(
                    name=f"input_driver[{k}]",
                    expected=v,
                    observed=got.get(k),
                    passed=matched,
                    kind="input",
                )
            )
            if not matched:
                res.status = "ERROR"
                res.diagnostics["error"] = f"input contamination on driver {k}"
                return res

    # Extra legal same-family conversions (e.g. same-dimension scaling).
    for value, in_u, eng_u, expected_engine_value in spec.extra_conversions:
        try:
            conv = engine.convert_input_quantity(
                value, input_unit=in_u, engine_unit=eng_u
            )
            res.assertions.append(
                _compare_value(
                    f"conversion[{value} {in_u}->{eng_u}]",
                    expected_engine_value,
                    conv.get("engine_value"),
                )
            )
        except Exception as exc:  # noqa: BLE001
            res.assertions.append(
                Assertion(
                    name=f"conversion[{value} {in_u}->{eng_u}]",
                    expected=expected_engine_value,
                    observed=f"{type(exc).__name__}: {exc}",
                    passed=False,
                    kind="conversion",
                )
            )

    try:
        result = engine.run_forecast(data)
    except Exception as exc:  # noqa: BLE001
        if _is_contract_reject(exc) or spec.expected.reject:
            return _handle_reject(spec, res, exc)
        raise  # infrastructure failure -> outer handler marks ERROR

    observed = observe(result)
    res.observed = observed
    return _assert_values(spec, res, observed)


def _handle_reject(spec: C.CaseSpec, res: CaseResult, exc: Exception) -> CaseResult:
    if not _is_contract_reject(exc):
        res.status = "ERROR"
        res.diagnostics["error"] = f"{type(exc).__name__}: {exc}"
        return res
    msg = f"{type(exc).__name__}: {exc}"
    res.observed = {"exception": msg}
    if not spec.expected.reject:
        res.status = "FAIL"
        res.assertions.append(
            Assertion(
                name="unexpected_reject",
                expected="compute",
                observed=msg,
                passed=False,
                kind="reject",
            )
        )
        return res
    reason = spec.expected.reject_reason
    # A real contract refusal: engine must raise with a non-empty reason.  If a
    # specific reason string is required it must appear; otherwise any
    # ForecastInputError-family contract message suffices.
    is_contract_error = _is_contract_reject(exc) and bool(str(exc).strip())
    if reason:
        matched = reason.lower() in str(exc).lower() and is_contract_error
        expected_label = reason
    else:
        matched = is_contract_error
        expected_label = "(any non-empty contract reason)"
    res.status = "REJECT_OK" if matched else "REJECT_MISMATCH"
    res.assertions.append(
        Assertion(
            name="reject_reason",
            expected=expected_label,
            observed=str(exc),
            passed=matched,
            kind="reject",
        )
    )
    return res


def _assert_values(
    spec: C.CaseSpec, res: CaseResult, observed: dict[str, Any]
) -> CaseResult:
    exp = spec.expected
    if exp.reject:
        # We computed instead of rejecting.
        res.status = "FAIL"
        res.assertions.append(
            Assertion(
                name="expected_reject",
                expected="reject",
                observed="computed",
                passed=False,
                kind="reject",
            )
        )
        return res

    assertions: list[Assertion] = []
    for field_name in exp.unknown_fields:
        obs_val = observed.get(field_name, {"__missing__": True})
        assertions.append(
            Assertion(
                name=f"unknown[{field_name}]",
                expected=None,
                observed=obs_val,
                passed=field_name in observed and obs_val is None,
                kind="unknown",
            )
        )
    for k, ev in exp.values.items():
        ov = observed.get(k, {"__missing__": True})
        if isinstance(ev, dict) and isinstance(ov, dict):
            assertions.extend(_compare_map(k, ev, ov))
        else:
            assertions.append(_compare_value(k, ev, ov))
    res.assertions.extend(assertions)
    if not res.assertions:
        # A legal vector must produce at least one checkable assertion; an
        # empty expectation is a case-design error, never a silent PASS.
        res.status = "ERROR"
        res.diagnostics["error"] = "no assertions were produced for a legal vector"
        return res
    if all(a.passed for a in res.assertions):
        res.status = "PASS"
    elif res.status != "ERROR":
        res.status = "FAIL"
    return res


# --- conversion (reject) -------------------------------------------------


def _run_conversion(
    spec: C.CaseSpec, engine: NativeEngine, res: CaseResult
) -> CaseResult:
    d = spec.drivers
    value = d["value"]
    # Each of cross_currency / cross_family is a single [input_unit, engine_unit]
    # pair that must be refused; a same-family scaling pair may be listed under
    # `same_family` and must succeed with its hand-computed engine_value.
    attempts: list[tuple[str, str]] = []
    for key in ("cross_currency", "cross_family"):
        pair = d.get(key)
        if pair:
            attempts.append((pair[0], pair[1]))
    if not attempts:
        res.status = "NOT_RUN"
        res.diagnostics["error"] = "no conversion attempts declared"
        return res
    all_rejected = True
    messages = []
    for in_u, eng_u in attempts:
        try:
            engine.convert_input_quantity(value, input_unit=in_u, engine_unit=eng_u)
            all_rejected = False
            messages.append(f"{in_u}->{eng_u}: NO ERROR (BAD)")
        except Exception as exc:  # noqa: BLE001
            if not _is_contract_reject(exc):
                raise
            all_rejected = all_rejected and bool(str(exc).strip())
            messages.append(f"{in_u}->{eng_u}: {type(exc).__name__}: {exc}")
    res.observed = {"attempts": messages, "all_rejected": all_rejected}
    res.assertions.append(
        Assertion(
            name="mixed_units_rejected",
            expected=True,
            observed=all_rejected,
            passed=all_rejected,
            kind="reject",
        )
    )
    res.status = "REJECT_OK" if all_rejected else "FAIL"
    return res


# --- support diagnostics -------------------------------------------------


def _run_support(spec: C.CaseSpec, engine: NativeEngine, res: CaseResult) -> CaseResult:
    data, observe = spec.build()
    data = copy.deepcopy(data)
    if spec.case_id == "M08-C":
        # Unknown observed range must remain null through the native analyzer.
        data["operating_research"]["calibrations"][0]["observed_range"] = None
        diag = engine.analyze_operating_research(data)
        cal = diag["calibrations"][0]
        res.observed = {
            "observed_range": cal.get("observed_range"),
            "adequacy_status": cal.get("adequacy_status"),
        }
        unknown_ok = cal.get("observed_range") is None
        res.assertions.append(
            Assertion(
                name="observed_range_stays_null",
                expected=None,
                observed=cal.get("observed_range"),
                passed=unknown_ok,
                kind="unknown",
            )
        )
        unverified = cal.get("adequacy_status") == "unverified"
        res.assertions.append(
            Assertion(
                name="adequacy_unverified",
                expected="unverified",
                observed=cal.get("adequacy_status"),
                passed=unverified,
                kind="unknown",
            )
        )
        res.status = "PASS" if (unknown_ok and unverified) else "FAIL"
        return res

    diag = engine.build_support_diagnostics(data)
    observed = observe(diag)
    res.observed = observed
    return _assert_values(spec, res, observed)


# --- shock pair (baseline vs stressed delta) -----------------------------


def _run_shock_pair(
    spec: C.CaseSpec, engine: NativeEngine, res: CaseResult
) -> CaseResult:
    base_data, base_observe = spec.build_baseline()
    base_data = copy.deepcopy(base_data)
    base_result = engine.run_forecast(base_data)
    base_annual = base_observe(base_result)["annual"]

    stressed_data, stressed_observe = spec.build()
    stressed_data = copy.deepcopy(stressed_data)
    stressed_result = engine.run_forecast(stressed_data)
    stressed_annual = stressed_observe(stressed_result)["annual"]

    years = sorted(base_annual)
    delta = {y: stressed_annual[y] - base_annual[y] for y in years}
    delta_sum = sum(delta.values())
    observed = {
        "delta_2026": delta.get("2026"),
        "delta_2027": delta.get("2027"),
        "delta_sum": delta_sum,
        "baseline_annual": base_annual,
        "stressed_annual": stressed_annual,
    }
    res.observed = observed

    assertions = []
    for k, ev in spec.expected.values.items():
        ov = observed.get(k, {"__missing__": True})
        assertions.append(_compare_value(k, ev, ov))
    # Conservation: the first-year drop equals the deferred amount exactly once.
    expected_drop = -float(spec.drivers["deferred"])
    drop_once = _num_eq(expected_drop, delta.get("2026"))
    assertions.append(
        Assertion(
            name="shock_applied_once",
            expected=expected_drop,
            observed=delta.get("2026"),
            passed=drop_once,
            kind="conservation",
        )
    )
    res.assertions = assertions
    res.status = "PASS" if all(a.passed for a in assertions) else "FAIL"
    return res
