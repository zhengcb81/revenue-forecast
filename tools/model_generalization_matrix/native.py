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
    def period_flow_months(self, start: Any, end: Any) -> int:
        ref = NativeRef(entry="contracts.period_flow.period_flow_months",
                        request_sha256=_sha({"start": str(start), "end": str(end)}),
                        request={"start": str(start), "end": str(end)})
        self.refs.append(ref)
        val = self._rt.period_flow_months(start, end)
        ref.result_sha256 = _sha(val)
        ref.result = val
        ref.json_pointers = {"/months": val}
        return val
