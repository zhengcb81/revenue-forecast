"""Native engine adapter for the model generalization matrix.

Thin, dependency-free wrapper around the *existing* revenue engine.  It does not
re-implement any model formula; it only calls the real, shipped interfaces and
records a native reference (request/result/exception + JSON pointer) for each
call so the report can be audited against the actual engine.

The engine is always invoked in ``mode="draft"`` — this package produces
engineering evidence only, never a formal publication and never a publication
receipt.  ``formal`` validation and ``validate_published_forecast`` are
intentionally NOT used here (they do not apply to draft output).
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def _sha(obj: Any) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class NativeRef:
    """One recorded native call."""

    entry: str
    request_sha256: str
    request: Any = None
    result_sha256: str | None = None
    result: Any = None
    exception_type: str | None = None
    exception_message: str | None = None
    json_pointers: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return {
            "entry": self.entry,
            "request_sha256": self.request_sha256,
            "request": self.request,
            "result": self.result,
            "result_sha256": self.result_sha256,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "json_pointers": self.json_pointers,
        }


class NativeEngine:
    """Records every native call while delegating to the real engine."""

    def __init__(self, runtime: Any) -> None:
        self._rt = runtime  # injected module bundle (see bootstrap)
        self.refs: list[NativeRef] = []

    # -- forecast ---------------------------------------------------------
    def run_forecast(self, data: dict[str, Any]) -> dict[str, Any]:
        ref = NativeRef(entry="revenue_core.run_forecast(mode=draft)",
                        request_sha256=_sha(data), request=copy.deepcopy(data))
        self.refs.append(ref)
        try:
            result = self._rt.run_forecast(copy.deepcopy(data), mode="draft")
        except Exception as exc:  # noqa: BLE001 - recorded, re-raised for the case
            ref.exception_type = type(exc).__name__
            ref.exception_message = str(exc)
            raise
        ref.result_sha256 = _sha(result)
        ref.result = result
        return result

    # -- unit/currency conversion ----------------------------------------
    def convert_input_quantity(self, value: float, *, input_unit: str, engine_unit: str) -> Any:
        req = {"value": value, "input_unit": input_unit, "engine_unit": engine_unit}
        ref = NativeRef(entry="research.input_quantities.convert_input_quantity",
                        request_sha256=_sha(req), request=req)
        self.refs.append(ref)
        try:
            out = self._rt.convert_input_quantity(value, input_unit=input_unit, engine_unit=engine_unit)
        except Exception as exc:
            ref.exception_type = type(exc).__name__
            ref.exception_message = str(exc)
            raise
        ref.result_sha256 = _sha(out)
        ref.result = out
        ref.json_pointers = {"/engine_value": out.get("engine_value"), "/conversion": out.get("conversion")}
        return out

    # -- support diagnostics ---------------------------------------------
    def build_support_diagnostics(self, data: dict[str, Any]) -> dict[str, Any]:
        req_sha = _sha(data)
        ref = NativeRef(entry="research_support_diagnostics.build_support_diagnostics",
                        request_sha256=req_sha, request=copy.deepcopy(data))
        self.refs.append(ref)
        try:
            out = self._rt.build_support_diagnostics(
                copy.deepcopy(data), req_sha
            )
        except Exception as exc:
            ref.exception_type = type(exc).__name__
            ref.exception_message = str(exc)
            raise
        ref.result_sha256 = _sha(out)
        ref.result = out
        ref.json_pointers = {
            "/schema_version": out.get("schema_version"),
            "/economic_truth_inferred": out.get("economic_truth_inferred"),
        }
        return out

    # -- period-flow window helper (native validation unit) --------------
    def analyze_operating_research(self, data: dict[str, Any]) -> dict[str, Any]:
        ref = NativeRef(entry="research.evidence_roles.analyze_operating_research",
                        request_sha256=_sha(data), request=copy.deepcopy(data))
        self.refs.append(ref)
        try:
            checked = copy.deepcopy(data)
            out = self._rt.analyze_operating_research(checked, self._rt.validate_document(checked))
        except Exception as exc:
            ref.exception_type = type(exc).__name__
            ref.exception_message = str(exc)
            raise
        ref.result = out
        ref.result_sha256 = _sha(out)
        return out

    # -- W08 combination groups ------------------------------------------

    def convert_input_quantity_strict(
        self, value: float, *, input_unit: str, engine_unit: str
    ) -> Any:
        """C01: convert and then re-derive through the shipped record validator.

        The generic adapter records the conversion; this variant additionally
        runs ``validate_input_quantity_record`` so the returned audit record is
        machine-checked by the engine's own re-derivation rather than trusted.
        """
        req = {"value": value, "input_unit": input_unit, "engine_unit": engine_unit}
        ref = NativeRef(
            entry="research.input_quantities.convert_input_quantity"
            " + validate_input_quantity_record",
            request_sha256=_sha(req),
            request=req,
        )
        self.refs.append(ref)
        try:
            out = self._rt.convert_input_quantity(
                value, input_unit=input_unit, engine_unit=engine_unit
            )
            self._rt.validate_input_quantity_record(out, field="combination_conversion")
        except Exception as exc:
            ref.exception_type = type(exc).__name__
            ref.exception_message = str(exc)
            raise
        ref.result_sha256 = _sha(out)
        ref.result = out
        ref.json_pointers = {
            "/engine_value": out.get("engine_value"),
            "/conversion": out.get("conversion"),
        }
        return out

    def period_flow_months(self, start: Any, end: Any) -> int:  # noqa: D401 (existing)
        return self._period_flow_months(start, end)

    def _period_flow_months(self, start: Any, end: Any) -> int:
        ref = NativeRef(entry="contracts.period_flow.period_flow_months",
                        request_sha256=_sha({"start": str(start), "end": str(end)}),
                        request={"start": str(start), "end": str(end)})
        self.refs.append(ref)
        try:
            val = self._rt.period_flow_months(start, end)
        except Exception as exc:
            ref.exception_type = type(exc).__name__
            ref.exception_message = str(exc)
            raise
        ref.result_sha256 = _sha(val)
        ref.result = val
        ref.json_pointers = {"/months": val}
        return val

    # -- C04: net-amount adjustment resolution ---------------------------

    def resolve_adjustments(self, data: dict[str, Any]) -> dict[str, Any]:
        """C04: the native signed-adjustment resolver (gross/net contract)."""
        req_sha = _sha(data)
        ref = NativeRef(entry="forecast.segments.resolve_adjustments",
                        request_sha256=req_sha, request=copy.deepcopy(data))
        self.refs.append(ref)
        try:
            checked = copy.deepcopy(data)
            out = self._rt.resolve_adjustments(checked, self._rt.validate_document(checked))
        except Exception as exc:
            ref.exception_type = type(exc).__name__
            ref.exception_message = str(exc)
            raise
        ref.result = out
        ref.result_sha256 = _sha(out)
        return out

    # -- C05: shipped historical error interface -------------------------

    def evaluate_history(self, result: dict[str, Any]) -> dict[str, Any]:
        """C05: feed a real draft result to the shipped backtest interface.

        A snapshot is created from the SAME draft result (no second forecast),
        and the actuals document is derived from that draft's declared scope.
        The returned evaluation is the engine's own scoped actual/WAPE record.
        """
        import copy as _copy

        req = {"forecast_result_sha256": _sha(result)}
        ref = NativeRef(entry="revenue_backtest.evaluate_snapshot(draft snapshot)",
                        request_sha256=_sha(req), request=req)
        self.refs.append(ref)
        try:
            forecast = _copy.deepcopy(result)
            snapshot = {
                "snapshot_schema_version": "2.0",
                "snapshot_id": self._rt.canonical_sha256({"result": _sha(forecast)}),
                "forecast_version": forecast.get("forecast_version") or "w08-draft",
                "company_name": forecast["company_name"],
                "as_of_date": forecast["as_of_date"],
                "input_sha256": forecast.get("input_sha256"),
                "forecast_result_sha256": _sha(forecast),
                "engine_version": forecast.get("engine_version"),
                "forecast_schema_version": forecast.get("schema_version"),
                "input_document": None,
                "forecast_result": forecast,
            }
            evaluation = self._rt.evaluate_draft_scope(snapshot)
        except Exception as exc:
            ref.exception_type = type(exc).__name__
            ref.exception_message = str(exc)
            raise
        ref.result = evaluation
        ref.result_sha256 = _sha(evaluation)
        return evaluation

