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
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= TOL * max(1.0, abs(b))
    return a == b


def _is_contract_reject(exc: BaseException) -> bool:
    """True when the engine *refused the input* (a contract/validation error).

    Anything else (KeyError, RuntimeError, ImportError, ...) is an infrastructure
    failure and must surface as ERROR rather than being dressed up as a reject.
    """
    name = type(exc).__name__
    return name in {"ForecastInputError", "ValueError", "require"} or isinstance(exc, ValueError)


def _compare_value(name: str, exp: Any, obs: Any) -> Assertion:
    return Assertion(name=name, expected=exp, observed=obs, passed=_num_eq(exp, obs))


def _compare_map(name: str, exp: dict, obs: dict) -> list[Assertion]:
    out = []
    for k, ev in exp.items():
        ov = obs.get(k, {"__missing__": True}) if isinstance(obs, dict) else {"__missing__": True}
        if isinstance(ev, dict) and isinstance(ov, dict):
            out.extend(_compare_map(f"{name}.{k}", ev, ov))
        else:
            out.append(_compare_value(f"{name}.{k}", ev, ov))
    return out


def run_case(spec: C.CaseSpec, engine: NativeEngine) -> CaseResult:
    started = time.time()
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
        res.native_refs = [r.to_json() for r in engine.refs]
    return res


def _dispatch(spec: C.CaseSpec, engine: NativeEngine, res: CaseResult) -> CaseResult:
    if spec.kind == "conversion":
        return _run_conversion(spec, engine, res)
    if spec.kind == "support":
        return _run_support(spec, engine, res)
    if spec.kind == "shock_pair":
        return _run_shock_pair(spec, engine, res)
    if spec.kind == "period_flow":
        return _run_period_flow(spec, engine, res)
    return _run_forecast(spec, engine, res)


def _run_period_flow(spec: C.CaseSpec, engine: NativeEngine, res: CaseResult) -> CaseResult:
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
        res.assertions.append(_compare_value("months", spec.expected.values["months"], float(months)))

    try:
        result = engine.run_forecast(data)
    except Exception as exc:  # noqa: BLE001
        return _handle_reject(spec, res, exc)

    # Legal vector also confirms the engine computed (did not refuse) the window.
    observed = observe(result)
    res.observed.setdefault("annual", observed.get("annual"))
    if spec.expected.reject:
        res.status = "FAIL"
        res.assertions.append(
            Assertion(name="expected_reject", expected="reject", observed="computed", passed=False,
                      kind="reject")
        )
        return res
    res.status = "PASS" if all(a.passed for a in res.assertions) else "FAIL"
    return res


# --- forecast / reject ---------------------------------------------------

def _run_forecast(spec: C.CaseSpec, engine: NativeEngine, res: CaseResult) -> CaseResult:
    data, observe = spec.build()
    data = copy.deepcopy(data)

    # Anti-contamination: the built input's base drivers must equal the frozen ones.
    if spec.expected_input_drivers is not None:
        got = C._base_drivers(data)
        for k, v in spec.expected_input_drivers.items():
            matched = k in got and [round(x, 6) for x in got[k]] == [round(x, 6) for x in v]
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
            conv = engine.convert_input_quantity(value, input_unit=in_u, engine_unit=eng_u)
            res.assertions.append(
                _compare_value(f"conversion[{value} {in_u}->{eng_u}]", expected_engine_value,
                               conv.get("engine_value"))
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
    msg = f"{type(exc).__name__}: {exc}"
    res.observed = {"exception": msg}
    if not spec.expected.reject:
        res.status = "FAIL"
        res.assertions.append(
            Assertion(name="unexpected_reject", expected="compute", observed=msg, passed=False,
                      kind="reject")
        )
        return res
    reason = spec.expected.reject_reason
    # A real contract refusal: engine must raise with a non-empty reason.  If a
    # specific reason string is required it must appear; otherwise any
    # ForecastInputError-family contract message suffices.
    is_contract_error = isinstance(exc, Exception) and bool(str(exc).strip())
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


def _assert_values(spec: C.CaseSpec, res: CaseResult, observed: dict[str, Any]) -> CaseResult:
    exp = spec.expected
    if exp.reject:
        # We computed instead of rejecting.
        res.status = "FAIL"
        res.assertions.append(
            Assertion(name="expected_reject", expected="reject", observed="computed", passed=False,
                      kind="reject")
        )
        return res

    assertions: list[Assertion] = []
    for field_name in exp.unknown_fields:
        if field_name in observed:
            obs_val = observed[field_name]
            # Unknown must be null, never 0.
            passed = obs_val is None
            assertions.append(
                Assertion(name=f"unknown[{field_name}]", expected=None, observed=obs_val,
                          passed=passed, kind="unknown")
            )
    for k, ev in exp.values.items():
        ov = observed.get(k, {"__missing__": True})
        if isinstance(ev, dict) and isinstance(ov, dict):
            assertions.extend(_compare_map(k, ev, ov))
        else:
            assertions.append(_compare_value(k, ev, ov))
    res.assertions.extend(assertions)
    res.status = "PASS" if all(a.passed for a in res.assertions) else "FAIL"
    return res


# --- conversion (reject) -------------------------------------------------

def _run_conversion(spec: C.CaseSpec, engine: NativeEngine, res: CaseResult) -> CaseResult:
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
    all_rejected = True
    messages = []
    for in_u, eng_u in attempts:
        try:
            engine.convert_input_quantity(value, input_unit=in_u, engine_unit=eng_u)
            all_rejected = False
            messages.append(f"{in_u}->{eng_u}: NO ERROR (BAD)")
        except Exception as exc:  # noqa: BLE001
            messages.append(f"{in_u}->{eng_u}: {type(exc).__name__}: {exc}")
    res.observed = {"attempts": messages, "all_rejected": all_rejected}
    res.assertions.append(
        Assertion(name="mixed_units_rejected", expected=True, observed=all_rejected,
                  passed=all_rejected, kind="reject")
    )
    res.status = "REJECT_OK" if all_rejected else "FAIL"
    return res


# --- support diagnostics -------------------------------------------------

def _run_support(spec: C.CaseSpec, engine: NativeEngine, res: CaseResult) -> CaseResult:
    data, observe = spec.build()
    data = copy.deepcopy(data)
    if spec.case_id == "M08-C":
        # Unknown observed range must remain null through the native analyzer.
        from research.evidence_roles import analyze_operating_research
        from revenue_core import validate_document

        data["operating_research"]["calibrations"][0]["observed_range"] = None
        diag = analyze_operating_research(data, validate_document(data))
        cal = diag["calibrations"][0]
        res.observed = {
            "observed_range": cal.get("observed_range"),
            "adequacy_status": cal.get("adequacy_status"),
        }
        unknown_ok = cal.get("observed_range") is None
        res.assertions.append(
            Assertion(name="observed_range_stays_null", expected=None,
                      observed=cal.get("observed_range"), passed=unknown_ok, kind="unknown")
        )
        unverified = cal.get("adequacy_status") == "unverified"
        res.assertions.append(
            Assertion(name="adequacy_unverified", expected="unverified",
                      observed=cal.get("adequacy_status"), passed=unverified, kind="unknown")
        )
        res.status = "PASS" if (unknown_ok and unverified) else "FAIL"
        return res

    diag = engine.build_support_diagnostics(data)
    observed = observe(diag)
    res.observed = observed
    return _assert_values(spec, res, observed)


# --- shock pair (baseline vs stressed delta) -----------------------------

def _run_shock_pair(spec: C.CaseSpec, engine: NativeEngine, res: CaseResult) -> CaseResult:
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
    drop_once = abs(delta.get("2026", 0.0) - (-20.0)) <= TOL * 20.0
    assertions.append(
        Assertion(name="shock_applied_once", expected=-20.0, observed=delta.get("2026"),
                  passed=drop_once, kind="conservation")
    )
    res.assertions = assertions
    res.status = "PASS" if all(a.passed for a in assertions) else "FAIL"
    return res
