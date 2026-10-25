"""W16-RF-BASIS: the single owner of historical revenue basis metadata.

An annual revenue forecast anchors on a reported total and a history of
observations. Two observations with the same unit are still not the same
measurement: a continuing-operations figure is not the consolidated total,
an as-reported figure is not its restatement, and a quarterly or year-to-
date figure is not a fiscal year. When an author explicitly supplies that
structure, the forecast must keep it and use it instead of silently
mixing the numbers into one "comparable growth" series.

This module is the one place those rules live (B08). The input contract
(``contracts/document.py``), the report (``revenue_report.py``) and the
linter (``lint_input.py``) call it; none of them keeps a second copy. It
reuses the existing responsibility layers instead of building parallels:
claim alignment follows ``contracts.evidence.validate_claim_ids``, money
unit resolution follows DU5 ``research.input_quantities`` (there is no
second currency table), and the component recompute uses ``Decimal`` with
the document's own reconciliation tolerance.

Records without ``revenue_basis`` keep the exact pre-W16 behavior; a
missing declaration is reported as ``not_declared`` and never as
"verified comparable" (B02/B03).
"""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from typing import Any

from contracts.evidence import (
    finite_number,
    require,
    validate_claim_ids,
)
from research.input_quantities import (
    money_currency,
    money_scale_factor,
    money_unit_currency,
    money_unit_scale_factor,
    validate_input_quantity_record,
)

REVENUE_BASIS_SCHEMA_VERSION = "rf-revenue-basis/1"

OPERATIONS = ("total", "continuing", "discontinued")
STATEMENT_STATUSES = ("as_reported", "restated")
PERIOD_KINDS = (
    "fiscal_year",
    "half_year",
    "quarter",
    "ytd",
    "trailing_twelve_months",
)
ANNUAL_PERIOD_KIND = "fiscal_year"

_BASIS_KEYS = {
    "schema_version",
    "operations",
    "statement_status",
    "period_kind",
    "input_quantity",
    "components",
    "source_ids",
    "business_boundary_id",
    "comparison_group_id",
    "basis_claim_ids",
}
_COMPONENT_OPERATIONS = ("continuing", "discontinued")

# Human labels for the report; unknown declarations never reach rendering
# because the contract layer rejected them first.
OPERATIONS_LABELS = {
    "total": "总额",
    "continuing": "持续经营",
    "discontinued": "终止经营",
}
STATEMENT_LABELS = {
    "as_reported": "原表",
    "restated": "重述",
}
PERIOD_KIND_LABELS = {
    "fiscal_year": "财年",
    "half_year": "半年度",
    "quarter": "季度",
    "ytd": "年累计",
    "trailing_twelve_months": "滚动十二月",
}


def parse_revenue_basis(record: Any) -> dict[str, Any] | None:
    """Return the validated ``revenue_basis`` of a historical record.

    ``None`` means the record declares nothing (the legacy input shape);
    every declaration error is a ``ForecastInputError`` naming the field.
    """
    require(isinstance(record, dict), "historical revenue record must be an object")
    if "revenue_basis" not in record:
        return None
    year = record.get("year")
    basis = record["revenue_basis"]
    field = f"historical_revenue[{year}].revenue_basis"
    require(isinstance(basis, dict), f"{field} must be an object")
    unknown = sorted(set(basis) - _BASIS_KEYS)
    require(
        not unknown,
        f"{field} has unsupported keys: {', '.join(unknown)}",
    )
    require(
        basis.get("schema_version") == REVENUE_BASIS_SCHEMA_VERSION,
        f"{field}.schema_version must be {REVENUE_BASIS_SCHEMA_VERSION}",
    )
    require(
        basis.get("operations") in OPERATIONS,
        f"{field}.operations must be one of {', '.join(OPERATIONS)}",
    )
    require(
        basis.get("statement_status") in STATEMENT_STATUSES,
        f"{field}.statement_status must be one of {', '.join(STATEMENT_STATUSES)}",
    )
    if "period_kind" in basis:
        require(
            basis["period_kind"] in PERIOD_KINDS,
            f"{field}.period_kind must be one of {', '.join(PERIOD_KINDS)}",
        )
    if "source_ids" in basis:
        source_ids = basis["source_ids"]
        require(
            isinstance(source_ids, list)
            and source_ids
            and all(isinstance(item, str) and item.strip() for item in source_ids),
            f"{field}.source_ids must be a non-empty list of source ids",
        )
        require(
            len(source_ids) == len(set(source_ids)),
            f"{field}.source_ids must not contain duplicates",
        )
    for key in ("business_boundary_id", "comparison_group_id"):
        if key in basis:
            require(
                isinstance(basis[key], str) and basis[key].strip(),
                f"{field}.{key} must be nonempty text",
            )
    if "basis_claim_ids" in basis:
        ids = basis["basis_claim_ids"]
        require(
            isinstance(ids, list)
            and ids
            and all(isinstance(i, str) and i.strip() for i in ids),
            f"{field}.basis_claim_ids must be nonempty claim ids",
        )
    if "components" in basis:
        _parse_components(basis["components"], field)
    return basis


def _parse_components(components: Any, field: str) -> None:
    require(
        isinstance(components, list) and components,
        f"{field}.components must be a non-empty list",
    )
    seen: set[str] = set()
    for position, component in enumerate(components):
        component_field = f"{field}.components[{position}]"
        require(
            isinstance(component, dict),
            f"{component_field} must be an object",
        )
        require(
            component.get("operations") in _COMPONENT_OPERATIONS,
            f"{component_field}.operations must be one of "
            f"{', '.join(_COMPONENT_OPERATIONS)}",
        )
        operations = component["operations"]
        require(
            operations not in seen,
            f"{field}.components declares {operations} twice",
        )
        seen.add(operations)
        component_value = finite_number(
            component.get("value"), f"{component_field}.value"
        )
        require(
            component_value >= 0,
            f"{component_field}.value cannot be negative: revenue components "
            "are disclosed revenue amounts",
        )
        require(
            isinstance(component.get("source_ids"), list) and component["source_ids"],
            f"{component_field}.source_ids is required",
        )
        require(
            isinstance(component.get("claim_ids"), list) and component["claim_ids"],
            f"{component_field}.claim_ids is required",
        )


def validate_basis_against_document(
    basis: dict[str, Any],
    *,
    record: dict[str, Any],
    data: dict[str, Any],
    source_index: dict[str, dict[str, Any]],
    claim_index: dict[str, dict[str, Any]],
    target_type: str = "historical_revenue",
    target_id: str | None = None,
) -> None:
    """Enforce every rule that needs the surrounding document.

    Called by ``validate_historical_revenue`` after the record's own value,
    source and claim checks have passed. Raises ``ForecastInputError`` with
    a field-specific message; it never rewrites the observation.
    """
    year = record["year"]
    value = finite_number(record.get("value"), f"historical_revenue[{year}].value")
    field = f"historical_revenue[{year}].revenue_basis"

    period_kind = basis.get("period_kind")
    require(
        period_kind in (None, ANNUAL_PERIOD_KIND),
        f"{field}.period_kind {period_kind} cannot serve as the annual "
        f"historical basis: the engine compares full fiscal years only "
        f"({PERIOD_KIND_LABELS.get(period_kind, period_kind)} figures belong "
        "to their own observation series, not to this one)",
    )

    for source_id in basis.get("source_ids", []):
        require(
            source_id in source_index,
            f"{field} references unknown source_id: {source_id}",
        )

    if "input_quantity" in basis:
        _validate_history_input_quantity(
            basis["input_quantity"], record=record, data=data, field=field
        )

    if any(
        key in basis
        for key in ("business_boundary_id", "comparison_group_id", "basis_claim_ids")
    ):
        require(
            all(
                basis.get(key)
                for key in (
                    "business_boundary_id",
                    "comparison_group_id",
                    "basis_claim_ids",
                )
            ),
            f"{field} comparison declaration requires business_boundary_id, comparison_group_id and basis_claim_ids",
        )
        policy_claims = validate_claim_ids(
            basis.get("basis_claim_ids"),
            claim_index,
            target_type,
            target_id or f"historical_revenue:{year}",
            field,
            "policy_support",
        )
        allowed_sources = set(basis.get("source_ids") or record.get("source_ids", []))
        require(
            all(claim["source_id"] in allowed_sources for claim in policy_claims),
            f"{field}.basis_claim_ids source must belong to the observation",
        )

    components = basis.get("components")
    if components is not None:
        require(
            basis["operations"] == "total",
            f"{field}.components decompose the consolidated total; records "
            f"with operations={basis['operations']} cannot carry them",
        )
        declared = {component["operations"] for component in components}
        require(
            declared == set(_COMPONENT_OPERATIONS),
            f"{field}.components must declare both continuing and discontinued "
            "operations before the total is recomputed",
        )
        for position, component in enumerate(components):
            component_field = f"{field}.components[{position}]"
            allowed_keys = {
                "operations",
                "value",
                "source_ids",
                "claim_ids",
                "statement_status",
                "business_boundary_id",
                "comparison_group_id",
                "period_kind",
            }
            require(
                not (set(component) - allowed_keys),
                f"{component_field} has unsupported keys",
            )
            for key in (
                "statement_status",
                "business_boundary_id",
                "comparison_group_id",
                "period_kind",
            ):
                if key in component:
                    require(
                        component[key] == basis.get(key),
                        f"{component_field}.{key} conflicts with total basis",
                    )
            for source_id in component["source_ids"]:
                require(
                    source_id in source_index,
                    f"{component_field} references unknown source_id: {source_id}",
                )
            claims = validate_claim_ids(
                component["claim_ids"],
                claim_index,
                "historical_revenue",
                f"historical_revenue:{year}",
                component_field,
                "exact_value",
            )
            require(
                all(claim["source_id"] in component["source_ids"] for claim in claims),
                f"{component_field}.claim_ids source must belong to the component",
            )
            component_value = finite_number(
                component["value"], f"{component_field}.value"
            )
            validate_historical_claim_alignment(
                claims,
                value=component_value,
                year=year,
                currency_unit=f"{data['currency']} {data['unit']}",
                label=f"historical revenue component {component['operations']} ",
            )
        tolerance = finite_number(
            data.get("reconciliation_tolerance", 1e-6),
            "reconciliation_tolerance",
        )
        parts = [
            finite_number(component["value"], f"{field}.components[{index}].value")
            for index, component in enumerate(components)
        ]
        require(
            decimal_sum_matches(value, parts, tolerance=tolerance),
            f"{field}.components do not reconcile: "
            f"{value} is not the sum of continuing and discontinued "
            f"({' + '.join(_plain(part) for part in parts)}) within tolerance",
        )


def require_total_operations_for_base(
    basis: dict[str, Any] | None,
    *,
    year: int,
    reported_basis: dict[str, Any] | None = None,
) -> None:
    """Align the adopted observation with the actual reported parameter.

    A legacy parameter means consolidated total. An explicitly continuing
    reported parameter can anchor continuing revenue; no numeric equality
    silently changes its business or statement basis.
    """
    if basis is None and reported_basis is None:
        return
    if reported_basis is None:
        require(
            basis is not None and basis["operations"] == "total",
            f"historical revenue base-year FY{year} operations={basis.get('operations') if basis else None}; undeclared reported parameter requires operations=total",
        )
        return
    require(
        basis is not None,
        f"historical revenue base-year FY{year} must declare the reported parameter basis",
    )
    for key in (
        "operations",
        "statement_status",
        "business_boundary_id",
        "comparison_group_id",
    ):
        require(
            basis.get(key) == reported_basis.get(key),
            f"historical revenue base-year FY{year} {key} differs from reported parameter basis",
        )


def _extract_matches(claim: dict[str, Any], value: float) -> bool:
    """True when the claim's extracted_value numerically equals the record.

    A non-numeric extracted_value (or a numeric string) never crashes the
    comparison; it simply does not support the value.
    """
    extracted = claim.get("extracted_value")
    if not isinstance(extracted, (int, float, str)):
        return False
    try:
        return math.isclose(float(extracted), value, rel_tol=0, abs_tol=1e-9)
    except (TypeError, ValueError):
        return False


def validate_historical_claim_alignment(
    claims: list[dict[str, Any]],
    *,
    value: float,
    year: int,
    currency_unit: str,
    label: str = "historical revenue ",
) -> None:
    """Exact-value claims must carry this value, period and unit.

    Extracted from ``validate_historical_revenue`` so record-level and
    component-level checks are one rule with identical messages (the label
    keeps the historical record messages byte-compatible).
    """
    require(
        any(_extract_matches(claim, value) for claim in claims),
        f"{label}claim value mismatch: {year}",
    )
    require(
        all(claim.get("period") == f"FY{year}" for claim in claims),
        f"{label}claim period mismatch: {year}",
    )
    require(
        all(claim.get("unit") == currency_unit for claim in claims),
        f"{label}claim unit mismatch: {year}",
    )


def _validate_history_input_quantity(
    quantity: Any, *, record: dict[str, Any], data: dict[str, Any], field: str
) -> None:
    """Normalize the raw value/unit through DU5; never a second currency table."""
    year = record["year"]
    value = finite_number(record.get("value"), f"historical_revenue[{year}].value")
    quantity_field = f"{field}.input_quantity"
    expected = validate_input_quantity_record(quantity, field=quantity_field)
    engine_unit = quantity["engine_unit"]
    resolved_currency = money_unit_currency(engine_unit)
    require(
        resolved_currency is not None,
        f"{quantity_field}.engine_unit {engine_unit} is not a money unit; "
        "historical revenue values are money amounts",
    )
    document_currency = money_currency(data["currency"])
    require(
        document_currency is not None and resolved_currency == document_currency,
        f"{quantity_field} is denominated in {engine_unit} but the document "
        f"currency is {data['currency']}; cross-currency amounts never mix "
        "without an FX basis",
    )
    engine_scale = money_unit_scale_factor(engine_unit)
    document_scale = money_scale_factor(data["unit"])
    require(
        engine_scale is not None
        and document_scale is not None
        and math.isclose(engine_scale, document_scale, rel_tol=0, abs_tol=0),
        f"{quantity_field}.engine_unit {engine_unit} scale does not match the "
        f"document unit {data['unit']}; engine_value must be expressed in the "
        "document unit, so convert the scale at construction",
    )
    require(
        math.isclose(expected["engine_value"], value, rel_tol=1e-9, abs_tol=1e-9),
        f"{quantity_field}.engine_value {expected['engine_value']} does not "
        f"match historical_revenue[{year}].value {value}; convert to the "
        "document unit at construction",
    )


def basis_comparable(
    left: dict[str, Any] | None, right: dict[str, Any] | None
) -> tuple[str, str]:
    """Same unit is not the same basis (B03).

    Returns ``(status, reason)`` with status ``comparable`` (both declared,
    same operations, statement status, source-linked comparison group and business boundary), ``not_comparable`` (both
    declared, different basis — the reason names the differing field) or
    ``not_declared`` (at least one side carries no declaration; the numeric
    legacy comparison stays available but is never reported as verified).
    """
    if left is None or right is None:
        missing = "left" if left is None else "right"
        return (
            "not_declared",
            f"basis not declared on the {missing} observation",
        )
    if left["operations"] != right["operations"]:
        return (
            "not_comparable",
            f"operations differ ({left['operations']} vs {right['operations']})",
        )
    if left["statement_status"] != right["statement_status"]:
        return (
            "not_comparable",
            "statement_status differs "
            f"({left['statement_status']} vs {right['statement_status']}); "
            "without an explicit restatement bridge the figures are not "
            "silently comparable",
        )
    for key in ("business_boundary_id", "comparison_group_id"):
        if left.get(key) and right.get(key) and left[key] != right[key]:
            return ("not_comparable", f"{key} differs ({left[key]} vs {right[key]})")
    if not all(
        item.get(key)
        for item in (left, right)
        for key in ("business_boundary_id", "comparison_group_id", "basis_claim_ids")
    ):
        return (
            "not_declared",
            "shared business boundary/comparison group with source-linked policy claims not declared",
        )
    return (
        "comparable",
        "source-linked comparison declaration; not an independent semantic approval",
    )


def history_basis_status(history: list[dict[str, Any]]) -> tuple[str, list[str]]:
    """Legacy numerics remain available; explicit uncertain bases never seed benchmarks."""
    if not any("revenue_basis" in row for row in history):
        return "legacy_numeric_only", [
            "basis not declared; legacy numeric benchmark, not verified comparable"
        ]
    pairs = [
        basis_comparable(a.get("revenue_basis"), b.get("revenue_basis"))
        for a, b in zip(history, history[1:])
    ]
    if any(status == "not_comparable" for status, _ in pairs):
        return "not_comparable", [
            reason for status, reason in pairs if status != "comparable"
        ]
    if not pairs or any(status != "comparable" for status, _ in pairs):
        return "not_declared", [
            reason for status, reason in pairs if status != "comparable"
        ]
    return "comparable", []


def year_over_year(left_value: float, right_value: float) -> tuple[float | None, str]:
    """YoY growth, or ``None`` with a reason when the base cannot carry it."""
    if left_value <= 0:
        return (
            None,
            f"comparison base is {'zero' if left_value == 0 else 'negative'} "
            f"({left_value}); year-over-year growth is undefined",
        )
    return (right_value / left_value - 1, "")


def decimal_sum_matches(total: float, parts: list[float], *, tolerance: float) -> bool:
    """``total`` equals ``sum(parts)`` under Decimal arithmetic and tolerance.

    The tolerance follows the document's reconciliation convention
    (``max(1, |total|) * tolerance``); no float re-summation is trusted.
    """
    try:
        total_decimal = Decimal(str(total))
        parts_decimal = [Decimal(str(part)) for part in parts]
        window = Decimal(str(max(1.0, abs(total)))) * Decimal(str(tolerance))
        return abs(total_decimal - sum(parts_decimal)) <= window
    except (InvalidOperation, ValueError):
        return False


def historical_basis_view(
    history: list[dict[str, Any]],
    *,
    base_year: int,
    reported_total_revenue_parameter_id: str,
    reported_total_value: float,
    reconciliation_tolerance: float = 1e-6,
) -> dict[str, Any]:
    """Additive diagnostic view: declarations, comparability, base adoption.

    Pure reporting over already-validated records (B05): which observation
    the forecast actually adopted as its base, its conversion/basis status,
    and why any adjacent pair cannot be compared. It never mutates the
    history and never promotes an undeclared basis to verified.
    """
    rows: list[dict[str, Any]] = []
    for record in history:
        basis = record.get("revenue_basis")
        if basis is None:
            rows.append(
                {
                    "year": record.get("year"),
                    "value": record.get("value"),
                    "operations": None,
                    "statement_status": None,
                    "period_kind": None,
                    "conversion": None,
                    "declared": False,
                }
            )
            continue
        quantity = basis.get("input_quantity")
        rows.append(
            {
                "year": record.get("year"),
                "value": record.get("value"),
                "operations": basis["operations"],
                "statement_status": basis["statement_status"],
                "period_kind": basis.get("period_kind"),
                "conversion": None
                if quantity is None
                else {
                    "value": quantity.get("value"),
                    "input_unit": quantity.get("input_unit"),
                    "engine_unit": quantity.get("engine_unit"),
                    "engine_value": quantity.get("engine_value"),
                    "conversion": quantity.get("conversion"),
                },
                "declared": True,
            }
        )

    comparability: list[dict[str, Any]] = []
    for left, right in zip(history, history[1:]):
        status, reason = basis_comparable(
            left.get("revenue_basis"), right.get("revenue_basis")
        )
        growth, growth_reason = year_over_year(
            float(left.get("value", 0.0)), float(right.get("value", 0.0))
        )
        comparability.append(
            {
                "left_year": left.get("year"),
                "right_year": right.get("year"),
                "status": status,
                "reason": reason,
                "year_over_year_growth": growth,
                "year_over_year_reason": growth_reason,
            }
        )

    base_record = next(
        (record for record in history if record.get("year") == base_year), None
    )
    if base_record is None:
        adoption = {
            "year": base_year,
            "adopted": False,
            "reason": "no observation for the base year",
            "reported_total_revenue_parameter_id": (
                reported_total_revenue_parameter_id
            ),
        }
    else:
        basis = base_record.get("revenue_basis")
        value = float(base_record.get("value", 0.0))
        difference = value - float(reported_total_value)
        tolerance = max(1.0, abs(float(reported_total_value))) * float(
            reconciliation_tolerance
        )
        adoption = {
            "year": base_year,
            "adopted": True,
            "value": value,
            "source_ids": list(base_record.get("source_ids", [])),
            "operations": None if basis is None else basis["operations"],
            "statement_status": (None if basis is None else basis["statement_status"]),
            "period_kind": basis.get("period_kind") if basis else None,
            "conversion_applied": "input_quantity" in (basis or {}),
            "reported_total_revenue_parameter_id": (
                reported_total_revenue_parameter_id
            ),
            "reported_total_value": float(reported_total_value),
            "difference": difference,
            "reconciliation_tolerance": float(reconciliation_tolerance),
            "matches_reported_total": abs(difference) <= tolerance,
            "basis_declared": basis is not None,
        }
    return {"records": rows, "comparability": comparability, "base_adoption": adoption}


def _plain(number: float) -> str:
    if float(number).is_integer():
        return str(int(number))
    return f"{number:g}"
