"""Compare requested top-level metrics from two exact frozen reports.

This module is a read-only owner adapter over ``ReportCatalog``'s public exact
report/run readers. It never enumerates artifact directories or invokes the
forecast engine. A comparison delta is emitted only when the full public metric
semantics (and canonical company scope) align.
"""
from __future__ import annotations

import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from typing import Any

from report_catalog import CatalogError, ReportCatalog

SCHEMA_VERSION = "rf-report-comparison/1"
MAX_DECIMAL_CHARS = 4096
MAX_DECIMAL_PRECISION = 8192
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,191}$")
_SUPPORTED_METRICS = frozenset({"revenue"})
_PERIOD_KINDS = frozenset({"FY", "H1", "Q", "TTM", "instant"})
_PERIOD_FIELDS = ("fiscal_year", "period_kind", "period_start", "period_end")
_REQUIRED_DIMENSIONS = (
    "unit", "currency", "scale", "fiscal_year", "period_kind",
    "period_start", "period_end", "basis", "scenario", "actual_or_forecast",
    "analysis_subject_id",
)


class CompareError(RuntimeError):
    """Pathless error safe for the public comparison CLI."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise CompareError(code, message)


def _known_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _known_token(value: Any) -> bool:
    """Known, non-empty and not the contract's literal unknown marker."""
    return _known_string(value) and value.strip().lower() != "unknown"


def validate_request(value: Any) -> dict[str, Any]:
    """Validate the bounded public request without accepting extension fields."""
    _require(isinstance(value, dict), "invalid_request", "request must be an object")
    _require(set(value) == {"left_report_id", "right_report_id", "scenario", "metric_ids"},
             "invalid_request", "request fields do not match CompareRequest")
    for key in ("left_report_id", "right_report_id"):
        _require(isinstance(value[key], str) and _ID.fullmatch(value[key]) is not None,
                 "invalid_request", f"{key} must be an opaque ID")
    _require(isinstance(value["scenario"], str) and
             re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", value["scenario"]) is not None,
             "invalid_request", "scenario must be a bounded opaque identifier")
    metric_ids = value["metric_ids"]
    _require(isinstance(metric_ids, list) and len(metric_ids) >= 1,
             "invalid_request", "metric_ids must contain at least one entry")
    _require(all(isinstance(item, str) and
                 re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", item) is not None
                 for item in metric_ids),
             "invalid_request", "metric_ids must be bounded opaque identifiers")
    _require(len(metric_ids) == len(set(metric_ids)), "invalid_request",
             "metric_ids must not contain duplicates")
    unknown = sorted(set(metric_ids) - _SUPPORTED_METRICS)
    _require(not unknown, "unknown_metric", "one or more requested metric IDs are unsupported")
    return value


def _owner_error(exc: BaseException) -> CompareError:
    if isinstance(exc, CatalogError):
        code = exc.code
        if code == "not_found":
            return CompareError("not_found", "an exact requested report was not found")
        if code in {"catalog_unavailable", "artifact_unavailable"}:
            return CompareError("unavailable", "an exact catalog or report artifact is unavailable")
        return CompareError("incompatible", "the exact catalog or report failed owner validation")
    if isinstance(exc, OSError):
        return CompareError("unavailable", "an exact catalog or report artifact is unavailable")
    return CompareError("incompatible", "the exact catalog or report failed owner validation")


def _load_exact(catalog: ReportCatalog, report_id: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Read one exact public report and its exact run identity through owner APIs."""
    try:
        response = catalog.get_report(report_id)
    except CatalogError as exc:
        raise _owner_error(exc) from exc
    except OSError as exc:
        raise CompareError("unavailable", "an exact catalog or report artifact is unavailable") from exc
    _require(isinstance(response, dict) and response.get("schema_version") == "rf-report-catalog/1",
             "incompatible", "owner report response schema is unsupported")
    revision = response.get("catalog_revision")
    view = response.get("view")
    _require(_known_string(revision) and isinstance(view, dict), "incompatible",
             "owner exact report response is incomplete")
    report = view.get("report")
    metrics = view.get("metrics")
    _require(isinstance(report, dict) and report.get("report_id") == report_id and
             isinstance(report.get("run_id"), str), "incompatible",
             "owner exact report reference does not match the request")
    _require(isinstance(metrics, list) and all(isinstance(row, dict) for row in metrics),
             "incompatible", "owner report metrics are malformed")
    try:
        run_response = catalog.get_run(report["run_id"])
    except CatalogError as exc:
        # A report whose exact run is absent is corrupt/incompatible, never a
        # request-level not_found for a different report ID.
        if exc.code == "catalog_unavailable":
            raise CompareError("unavailable", "an exact catalog or report artifact is unavailable") from exc
        raise CompareError("incompatible", "the exact report run is missing or invalid") from exc
    except OSError as exc:
        raise CompareError("unavailable", "an exact catalog or report artifact is unavailable") from exc
    _require(isinstance(run_response, dict) and
             run_response.get("schema_version") == "rf-report-catalog/1" and
             isinstance(run_response.get("run"), dict), "incompatible",
             "owner exact run response schema is unsupported")
    run = run_response["run"]
    report_company = report.get("company")
    _require(run.get("run_id") == report["run_id"] and isinstance(run.get("company"), dict) and
             isinstance(report_company, dict) and run["company"] == report_company and
             run["company"].get("resolution_status") == "resolved",
             "incompatible", "owner exact report and run identity do not agree")
    return {"report": report, "metrics": metrics, "company": run["company"]}, view, revision


def _period_key(number: dict[str, Any]) -> tuple[Any, ...] | None:
    """A full explicit period key; null means the owner did not identify one."""
    if not isinstance(number, dict):
        return None
    fiscal_year = number.get("fiscal_year")
    period_kind = number.get("period_kind")
    period_start = number.get("period_start")
    period_end = number.get("period_end")
    if fiscal_year is not None and type(fiscal_year) is not int:
        raise CompareError("incompatible", "owner metric fiscal year is malformed")
    for value in (period_kind, period_start, period_end):
        if value is not None and not isinstance(value, str):
            raise CompareError("incompatible", "owner metric period dimension is malformed")
    if period_kind is not None and period_kind not in _PERIOD_KINDS:
        raise CompareError("incompatible", "owner metric period kind is not in the contract enum")
    values = (fiscal_year, period_kind, period_start, period_end)
    if all(value is None for value in values):
        return None
    return values


def _period_sort_key(key: tuple[Any, ...] | None) -> str:
    return json.dumps(key, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _selected_rows(side: dict[str, Any], metric_id: str, scenario: str) -> dict[tuple[Any, ...] | None, dict[str, Any]]:
    if side["report"].get("status") == "legacy":
        # Legacy exact reports stay legacy even if a malformed artifact carries
        # metric rows; never emit a delta from legacy model output.
        return {}
    selected: dict[tuple[Any, ...] | None, dict[str, Any]] = {}
    for row in side["metrics"]:
        number = row.get("number")
        if row.get("segment_id") is not None or row.get("metric_id") != metric_id:
            continue
        if not isinstance(number, dict) or number.get("scenario") != scenario:
            continue
        key = _period_key(number)
        if key in selected:
            raise CompareError("ambiguous_metric", "a requested report has duplicate candidates for one metric period")
        provenance = row.get("provenance")
        if (not isinstance(provenance, dict) or
                provenance.get("artifact_id") != side["report"]["report_id"] or
                provenance.get("run_id") != side["report"].get("run_id")):
            raise CompareError("incompatible", "owner metric provenance is not bound to its exact report and run")
        if number.get("analysis_subject_id") != side["company"].get("analysis_subject_id"):
            raise CompareError("incompatible", "owner metric subject does not match its exact run company")
        selected[key] = row
    return selected


def _identity_reasons(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    left_company, right_company = left["company"], right["company"]
    left_entity, right_entity = left_company.get("entity_id"), right_company.get("entity_id")
    reasons: list[str] = []
    if not _known_token(left_entity) or not _known_token(right_entity):
        reasons.append("canonical_entity_unknown")
    elif left_entity != right_entity:
        reasons.append("canonical_entity_mismatch")
    for field, reason in (("listing_id", "canonical_listing"),
                          ("analysis_subject_id", "canonical_subject")):
        left_value, right_value = left_company.get(field), right_company.get(field)
        # A missing or literal-unknown canonical listing/subject is unknown,
        # not proof that both reports refer to the same scope.
        if left_value is None or right_value is None:
            reasons.append(f"{reason}_unknown")
        elif not _known_token(left_value) or not _known_token(right_value):
            reasons.append(f"{reason}_unknown")
        elif left_value != right_value:
            reasons.append(f"{reason}_mismatch")
    return reasons


def _valid_period_date(value: Any) -> bool:
    if not _known_token(value):
        return False
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return True


def _dimension_reasons(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    left_number, right_number = left.get("number"), right.get("number")
    if not isinstance(left_number, dict) or not isinstance(right_number, dict):
        return ["number_unavailable"]
    reasons: list[str] = []
    if left_number.get("value") is None:
        reasons.append("left_value_unavailable")
    if right_number.get("value") is None:
        reasons.append("right_value_unavailable")
    left_definition, right_definition = left.get("definition_version"), right.get("definition_version")
    if left_definition != right_definition:
        reasons.append("definition_version_mismatch")
    elif not _known_token(left_definition):
        reasons.append("definition_version_unknown")
    for field in _REQUIRED_DIMENSIONS:
        a, b = left_number.get(field), right_number.get(field)
        if a != b:
            reasons.append(f"{field}_mismatch")
            continue
        if field == "scale":
            if type(a) is not int:
                reasons.append("scale_unknown")
        elif field in {"period_start", "period_end"}:
            # Null dates on a known FY row are explicit FY granularity, not a
            # substitution; otherwise the date must be known and a real ISO date.
            if a is None:
                if left_number.get("period_kind") == "FY" and type(left_number.get("fiscal_year")) is int:
                    continue
                reasons.append(f"{field}_unknown")
            elif not _known_token(a):
                reasons.append(f"{field}_unknown")
            elif not _valid_period_date(a):
                reasons.append(f"{field}_invalid")
        elif field == "currency":
            # Null currency is only a non-applicable dimension for non-currency units.
            if a is None:
                if left_number.get("unit") != "currency":
                    continue
                reasons.append("currency_unknown")
            elif not _known_token(a):
                reasons.append("currency_unknown")
        elif field == "fiscal_year":
            if type(a) is not int:
                reasons.append("fiscal_year_unknown")
        elif field == "actual_or_forecast":
            if a not in {"actual", "forecast"}:
                reasons.append("actual_or_forecast_unknown")
        elif not _known_token(a):
            reasons.append(f"{field}_unknown")
    for side_name, number in (("left", left_number), ("right", right_number)):
        # This public comparator is deliberately limited to the owner's
        # top-level consolidated rows; a non-consolidated basis is out of scope.
        if number.get("basis") != "consolidated":
            reasons.append(f"{side_name}_basis_not_consolidated")
    return reasons


def _decimal_value(value: Any, side: str) -> Decimal:
    _require(isinstance(value, str) and 0 < len(value) <= MAX_DECIMAL_CHARS,
             "decimal_invalid", f"{side} metric value is not a bounded decimal string")
    # The contract allows fixed-point decimal strings only; explicitly reject
    # exponent syntax, whitespace and non-finite values before Decimal parsing.
    _require(re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", value) is not None,
             "decimal_invalid", f"{side} metric value is not fixed-point decimal")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise CompareError("decimal_invalid", f"{side} metric value is not decimal") from exc
    _require(number.is_finite(), "decimal_invalid", f"{side} metric value must be finite")
    return number


def _exact_delta(left_value: Any, right_value: Any) -> str:
    left_number = _decimal_value(left_value, "left")
    right_number = _decimal_value(right_value, "right")
    left_exponent = left_number.as_tuple().exponent
    right_exponent = right_number.as_tuple().exponent
    _require(type(left_exponent) is int and type(right_exponent) is int,
             "decimal_invalid", "metric value has no finite decimal exponent")
    assert isinstance(left_exponent, int) and isinstance(right_exponent, int)
    exponent_floor = min(left_exponent, right_exponent)
    adjusted_ceiling = max(left_number.adjusted(), right_number.adjusted())
    precision = max(1, adjusted_ceiling - exponent_floor + 3)
    _require(precision <= MAX_DECIMAL_PRECISION, "decimal_precision_exceeded",
             "exact decimal delta exceeds the comparison precision bound")
    try:
        with localcontext() as context:
            context.prec = precision
            delta = right_number - left_number
    except (InvalidOperation, ArithmeticError) as exc:
        raise CompareError("decimal_precision_exceeded", "exact decimal delta could not be represented") from exc
    _require(delta.is_finite(), "decimal_precision_exceeded", "exact decimal delta is not finite")
    # Preserve the exact Decimal result, including signed zero and the natural
    # fixed-point exponent; never normalize -0.0 into +0.0.
    return format(delta, "f")


def _compare_pair(metric_id: str, left: dict[str, Any] | None, right: dict[str, Any] | None,
                  *, identity_reasons: list[str], side_states: dict[str, str],
                  side_information: dict[str, str | None]) -> dict[str, Any]:
    reasons = list(identity_reasons)
    if left is None:
        reasons.append("left_metric_missing_for_period")
        if side_states["left"] == "legacy":
            reasons.append("left_legacy_metrics_unavailable")
    if right is None:
        reasons.append("right_metric_missing_for_period")
        if side_states["right"] == "legacy":
            reasons.append("right_legacy_metrics_unavailable")
    if left is not None and right is not None:
        reasons.extend(_dimension_reasons(left, right))
    for side_name, row in (("left", left), ("right", right)):
        if row is None:
            continue
        provenance = row.get("provenance")
        expected_info = side_information[side_name]
        if (not isinstance(provenance, dict) or
                provenance.get("source_as_of") != expected_info):
            reasons.append(f"{side_name}_provenance_information_as_of_mismatch")
    reasons = sorted(set(reasons))
    comparable = left is not None and right is not None and not reasons
    delta = None
    if comparable:
        assert left is not None and right is not None
        left_number, right_number = left.get("number"), right.get("number")
        assert isinstance(left_number, dict) and isinstance(right_number, dict)
        delta = {**right_number, "value": _exact_delta(left_number.get("value"), right_number.get("value"))}
    return {"metric_id": metric_id, "left": left, "right": right, "delta": delta,
            "comparable": comparable, "reasons": reasons}


def compare_reports(request: Any, *, catalog: ReportCatalog | None = None) -> dict[str, Any]:
    """Return the public comparison and exact catalog revisions observed per side."""
    request = validate_request(request)
    catalog = catalog or ReportCatalog()
    left, _, left_revision = _load_exact(catalog, request["left_report_id"])
    right, _, right_revision = _load_exact(catalog, request["right_report_id"])
    identity_reasons = _identity_reasons(left, right)

    left_info = left["report"].get("information_as_of")
    right_info = right["report"].get("information_as_of")
    for value in (left_info, right_info):
        _require(value is None or isinstance(value, str), "incompatible",
                 "owner information_as_of precision is invalid")
    side_states = {"left": str(left["report"].get("status")),
                   "right": str(right["report"].get("status"))}
    output_metrics: list[dict[str, Any]] = []
    for metric_id in sorted(request["metric_ids"]):
        left_rows = _selected_rows(left, metric_id, request["scenario"])
        right_rows = _selected_rows(right, metric_id, request["scenario"])
        if not left_rows and not right_rows:
            any_metric = any(
                row.get("segment_id") is None and row.get("metric_id") == metric_id
                for item, state in ((left, side_states["left"]), (right, side_states["right"]))
                if state != "legacy" for row in item["metrics"])
            if any_metric:
                # The metric exists, but not for the requested scenario. This is
                # an unknown scenario, never a successful empty comparison.
                raise CompareError("unknown_scenario", "requested scenario is absent from both exact reports")
            if "legacy" not in side_states.values():
                raise CompareError("metric_unavailable", "requested metric is absent from both exact reports")
            # A legacy exact report may legitimately have no metrics/model data;
            # retain one explicit unknown row instead of returning a false empty success.
            output_metrics.append(_compare_pair(metric_id, None, None,
                identity_reasons=identity_reasons,
                side_states={"left": "legacy" if side_states["left"] == "legacy" else "missing",
                             "right": "legacy" if side_states["right"] == "legacy" else "missing"},
                side_information={"left": left_info, "right": right_info}))
            continue
        keys = set(left_rows) | set(right_rows)
        for key in sorted(keys, key=_period_sort_key):
            output_metrics.append(_compare_pair(metric_id, left_rows.get(key), right_rows.get(key),
                                                identity_reasons=identity_reasons,
                                                side_states=side_states,
                                                side_information={"left": left_info,
                                                                  "right": right_info}))
    comparison = {
        "left_report_id": request["left_report_id"],
        "right_report_id": request["right_report_id"],
        "left_information_as_of": left_info,
        "right_information_as_of": right_info,
        "metrics": output_metrics,
        "explained_changes": [],
        "unproven_changes": ["numeric_deltas_do_not_establish_cause_or_management_intent"],
    }
    return {"comparison": comparison,
            "catalog_revisions": {"left": left_revision, "right": right_revision}}
