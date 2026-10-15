"""R6-RF-INPUT I1: explicit human-unit conversion for input quantities.

The cross-market US failure built a 5-percentage-point shock as
``shock_value=5.0`` on a ratio parameter. The engine's arithmetic on that
input is self-consistent, so the fix belongs to the construction half: an
explicit, auditable conversion from the unit a human source uses to the
engine's contract unit. This module is that shared responsibility layer; the
engine re-derives and enforces every stored record (see
``analysis/sensitivity.py``), so a forged conversion cannot pass validation.

DU5: every money unit is derived from one finite Currency x Scale
description (USD, RMB with CNY as a same-currency alias, HKD; at the
yuan/thousand/wan/million/yi/billion scales). There is no second hand list of
currency spellings. Unknown currencies and spellings stay unknown: a bare
``wan_yuan``/``万元`` is never guessed as RMB, and multi-currency expressions
never resolve. ``validate_input_quantity_for_parameter`` is the single helper
the sensitivity consumer calls to check a stored record against the
parameter's real currency/scale/dimension and shock semantics.
"""

from __future__ import annotations

import math
import re
from typing import Any

from contracts.constants import MONETARY_DIMENSIONS
from contracts.evidence import finite_number, require


INPUT_QUANTITY_SCHEMA_VERSION = "rf-input-quantity/1"

# Share-of-total units (dimensionless fractions and their point spellings).
_SHARE_UNITS = {"pp", "percent", "ratio", "basis_point"}
# Aliases authors actually type; normalized before lookup.
_SHARE_ALIASES = {
    "pp": "pp",
    "percentage_point": "pp",
    "percentage_points": "pp",
    "pct": "percent",
    "percent": "percent",
    "%": "percent",
    "ratio": "ratio",
    "fraction": "ratio",
    "bp": "basis_point",
    "basis_point": "basis_point",
    "basis_points": "basis_point",
}

# Money units: one finite Currency x Scale description. The canonical name is
# ``{currency}_{scale}`` and every accepted spelling is the product of a
# currency alias and a scale alias, so there is no parallel hand-written
# alias/family/scale list to drift. ``cny`` normalizes to the existing ``rmb``
# units; historical records are never rewritten.
_MONEY_CURRENCY_ALIASES = {"usd": "usd", "rmb": "rmb", "cny": "rmb", "hkd": "hkd"}
_MONEY_SCALE_ALIASES = {
    "unit": "unit",
    "元": "unit",
    "thousand": "thousand",
    "千": "thousand",
    "10k": "10k",
    "wan": "10k",
    "万": "10k",
    "million": "million",
    "百万": "million",
    "100m": "100m",
    "yi": "100m",
    "亿": "100m",
    "billion": "billion",
    "十亿": "billion",
}
# Scale factors in the currency's base unit (one yuan / one dollar / one HKD).
_MONEY_SCALE_FACTORS = {
    "unit": 1.0,
    "thousand": 1_000.0,
    "10k": 10_000.0,
    "million": 1_000_000.0,
    "100m": 100_000_000.0,
    "billion": 1_000_000_000.0,
}

# Count scales (existing vocabulary, unchanged).
_COUNT_ALIASES = {
    "units": "units",
    "thousand_units": "thousand_units",
    "million_units": "million_units",
}
_COUNT_SCALES = {
    "units": 1.0,
    "thousand_units": 1_000.0,
    "million_units": 1_000_000.0,
}


def _build_unit_tables() -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    aliases: dict[str, str] = {}
    descriptions: dict[str, dict[str, Any]] = {}

    def register(alias: str, canonical: str, description: dict[str, Any]) -> None:
        existing = aliases.get(alias)
        require(existing is None or existing == canonical, f"unit alias collision: {alias}")
        aliases[alias] = canonical
        descriptions[canonical] = description

    for alias, canonical in _SHARE_ALIASES.items():
        register(
            alias, canonical,
            {"family": "share", "currency": None, "scale": None, "factor": None},
        )
    for currency_alias, currency in _MONEY_CURRENCY_ALIASES.items():
        for scale_alias, scale in _MONEY_SCALE_ALIASES.items():
            register(
                f"{currency_alias}_{scale_alias}",
                f"{currency}_{scale}",
                {
                    "family": "money",
                    "currency": currency,
                    "scale": scale,
                    "factor": _MONEY_SCALE_FACTORS[scale],
                },
            )
    for alias, canonical in _COUNT_ALIASES.items():
        register(
            alias, canonical,
            {
                "family": "count",
                "currency": None,
                "scale": canonical,
                "factor": _COUNT_SCALES[canonical],
            },
        )
    return aliases, descriptions


_UNIT_ALIASES, _UNIT_DESCRIPTIONS = _build_unit_tables()

# Parameter dimensions a plain count unit can shock. Monetary dimensions are
# owned by contracts.constants; the per-unit split below is this layer's
# interpretation of them (see validate_input_quantity_for_parameter).
_COUNT_SHOCKABLE_DIMENSIONS = {"quantity", "activity", "coverage_units"}
_MONETARY_PER_UNIT_DIMENSIONS = {
    "revenue_per_unit",
    "revenue_per_activity",
    "revenue_per_area",
}


def _normalize_unit(unit: Any, field: str) -> str:
    require(
        isinstance(unit, str) and bool(unit.strip()),
        f"{field} must be a non-empty unit string",
    )
    normalized = re.sub(r"[-\s]+", "_", unit.strip().lower())
    canonical = _UNIT_ALIASES.get(normalized)
    require(canonical is not None, f"unknown {field}: {unit}")
    assert canonical is not None  # narrow for type checking; require() already enforced
    return canonical


def _parameter_money_currency(currency: Any) -> str | None:
    if not isinstance(currency, str) or not currency.strip():
        return None
    return _MONEY_CURRENCY_ALIASES.get(currency.strip().lower())


def _parameter_money_scale(scale: Any) -> str | None:
    if not isinstance(scale, str) or not scale.strip():
        return None
    return _MONEY_SCALE_ALIASES.get(scale.strip().lower())


def _units_are_convertible(source: str, target: str) -> bool:
    left, right = _UNIT_DESCRIPTIONS[source], _UNIT_DESCRIPTIONS[target]
    if left["family"] != right["family"]:
        return False
    if left["family"] == "money":
        # Same-currency scale conversion only; USD/HKD/RMB never convert.
        return left["currency"] == right["currency"]
    return True


def convert_input_quantity(
    value: Any, *, input_unit: str, engine_unit: str
) -> dict[str, Any]:
    """Convert *value* from an explicit human unit to an engine contract unit.

    Returns an audit record preserving the original value/unit and the applied
    conversion; it never silently reinterprets semantics (``ratio`` stays a
    factor, not a percent) and never converts across incompatible unit
    families (a share cannot become money, USD cannot become RMB).
    """
    number = finite_number(value, "value")
    source = _normalize_unit(input_unit, "input_unit")
    target = _normalize_unit(engine_unit, "engine_unit")
    if source != target:
        require(
            _units_are_convertible(source, target),
            f"incompatible unit conversion: {input_unit} -> {engine_unit}",
        )
    family = _UNIT_DESCRIPTIONS[source]["family"]
    if source == target:
        engine_value = number
        expression = (
            f"{_plain(number)} {source} is already the engine unit {target} (identity)"
        )
    elif family == "share":
        engine_value = _convert_share(number, source, target)
        expression = (
            f"{_plain(number)} {source} = {_format_share(target, engine_value)} "
            f"({_describe_share(source, target)})"
        )
    else:
        factor = (
            _UNIT_DESCRIPTIONS[source]["factor"] / _UNIT_DESCRIPTIONS[target]["factor"]
        )
        engine_value = number * factor
        expression = (
            f"{_plain(number)} {source} x {factor:g} = {_plain(engine_value)} {target}"
        )
    require(math.isfinite(engine_value), "converted value must be finite")
    return {
        "schema_version": INPUT_QUANTITY_SCHEMA_VERSION,
        "value": number,
        "input_unit": str(input_unit).strip(),
        "engine_unit": str(engine_unit).strip(),
        "engine_value": engine_value,
        "conversion": expression,
    }


def _plain(number: float) -> str:
    if float(number).is_integer():
        return str(int(number))
    return f"{number:g}"


def _describe_share(source: str, target: str) -> str:
    pair = {
        ("pp", "ratio"): "1 pp = 0.01 ratio fraction",
        ("percent", "ratio"): "1 percent = 0.01 ratio fraction",
        ("basis_point", "ratio"): "1 bp = 0.0001 ratio fraction",
        ("pp", "basis_point"): "1 pp = 100 bp",
        ("ratio", "percent"): "ratio x 100 = percent",
        ("pp", "percent"): "1 pp = 1 percent",
        ("percent", "pp"): "1 percent = 1 pp",
        ("basis_point", "pp"): "100 bp = 1 pp",
        ("ratio", "basis_point"): "ratio x 10000 = bp",
    }
    return pair.get((source, target), f"{source} -> {target}")


def _format_share(unit: str, value: float) -> str:
    plain = _plain(value)
    if unit == "ratio":
        return plain
    return f"{plain} {unit}"


def _convert_share(number: float, source: str, target: str) -> float:
    # Everything funnels through the fraction representation.
    as_ratio = {
        "pp": lambda v: v / 100.0,
        "percent": lambda v: v / 100.0,
        "ratio": lambda v: v,
        "basis_point": lambda v: v / 10_000.0,
    }
    from_ratio = {
        "pp": lambda v: v * 100.0,
        "percent": lambda v: v * 100.0,
        "ratio": lambda v: v,
        "basis_point": lambda v: v * 10_000.0,
    }
    return from_ratio[target](as_ratio[source](number))


def validate_input_quantity_record(record: Any, *, field: str) -> dict[str, Any]:
    """Re-derive a stored ``input_quantity`` record; any drift fails closed.

    Used by the engine and the linter so the stored conversion lineage is
    machine-checked rather than decorative. The conversion expression carries
    the applied factor, so its text is re-derived and compared exactly: a
    tampered factor line is drift like any other.
    """
    require(isinstance(record, dict), f"{field} must be an object")
    require(
        set(record)
        >= {
            "schema_version", "value", "input_unit", "engine_unit",
            "engine_value", "conversion",
        },
        f"{field} is missing required keys",
    )
    require(
        record.get("schema_version") == INPUT_QUANTITY_SCHEMA_VERSION,
        f"unsupported {field}.schema_version",
    )
    expected = convert_input_quantity(
        record["value"], input_unit=record["input_unit"], engine_unit=record["engine_unit"]
    )
    require(
        math.isclose(
            finite_number(record.get("engine_value"), f"{field}.engine_value"),
            expected["engine_value"],
            rel_tol=0,
            abs_tol=1e-12,
        ),
        f"{field}.engine_value does not match the recorded units: "
        f"{record.get('engine_value')} != {expected['engine_value']}",
    )
    require(
        isinstance(record.get("conversion"), str) and record["conversion"].strip(),
        f"{field}.conversion is required",
    )
    require(
        record["conversion"] == expected["conversion"],
        f"{field}.conversion does not match the recorded units: "
        f"{record.get('conversion')!r} != {expected['conversion']!r}",
    )
    return expected


def validate_input_quantity_for_parameter(
    record: Any, *, parameter: Any, shock_type: Any, field: str
) -> dict[str, Any]:
    """Re-derive *record* and check it against the parameter's real unit.

    This is the single helper the sensitivity consumer calls. It re-runs the
    stored conversion, then checks the shock semantics (relative share shocks
    and absolute money/count shocks never mix), the parameter dimension, the
    currency family and the scale against the parameter's declared
    currency/scale (already bound to the document by the contracts). A
    self-consistent record that contradicts the parameter it shocks is
    rejected; a parameter unit that cannot be safely interpreted gets a clear
    diagnostic instead of a guess. Monetary-per-unit dimensions are never
    shocked by a plain money amount — the denominator is not dropped.
    """
    expected = validate_input_quantity_record(record, field=field)
    engine_unit = record["engine_unit"]
    description = _UNIT_DESCRIPTIONS[_normalize_unit(engine_unit, f"{field}.engine_unit")]
    family = description["family"]
    require(isinstance(parameter, dict), "sensitivity parameter must be an object")
    parameter_id = parameter.get("parameter_id")
    dimension = parameter.get("dimension")
    if shock_type in {"percent", "percentage_point", "basis_point"}:
        require(
            family == "share",
            f"{field}: {shock_type} shock requires a share-of-total unit "
            f"(pp/percent/bp/ratio), got {engine_unit}",
        )
    elif shock_type == "absolute":
        require(
            family in {"money", "count"},
            f"{field}: absolute shock requires a money or count unit, got "
            f"{engine_unit}; relative and absolute shocks never mix",
        )
    else:
        require(
            False,
            f"{field}: shock_type {shock_type} cannot carry an input_quantity record",
        )
    if family == "money":
        require(
            dimension in MONETARY_DIMENSIONS,
            f"{field}: money unit {engine_unit} cannot shock parameter "
            f"{parameter_id} (dimension {dimension})",
        )
        require(
            dimension not in _MONETARY_PER_UNIT_DIMENSIONS,
            f"{field}: parameter {parameter_id} dimension {dimension} is "
            f"monetary-per-unit; an absolute money unit {engine_unit} would "
            f"drop the per-unit denominator and cannot be safely interpreted",
        )
        currency = _parameter_money_currency(parameter.get("currency"))
        require(
            currency is not None,
            f"{field}: parameter {parameter_id} currency "
            f"{parameter.get('currency')!r} cannot be safely interpreted as a "
            f"registered money currency",
        )
        require(
            description["currency"] == currency,
            f"{field}: record unit {engine_unit} is denominated in "
            f"{description['currency'].upper()} but parameter {parameter_id} is "
            f"{str(parameter.get('currency')).strip()}; cross-currency amounts "
            f"never mix without an FX basis",
        )
        scale = _parameter_money_scale(parameter.get("scale"))
        require(
            scale is not None,
            f"{field}: parameter {parameter_id} scale "
            f"{parameter.get('scale')!r} cannot be safely interpreted as a "
            f"registered money scale",
        )
        require(
            description["scale"] == scale,
            f"{field}: record unit {engine_unit} scale does not match parameter "
            f"{parameter_id} scale {parameter.get('scale')!r}; convert to the "
            f"parameter scale at construction",
        )
    elif family == "count":
        require(
            dimension in _COUNT_SHOCKABLE_DIMENSIONS,
            f"{field}: count unit {engine_unit} cannot shock parameter "
            f"{parameter_id} (dimension {dimension})",
        )
    return expected


# Engine contract-unit aliases accepted on sensitivity tests and parameters.
_ENGINE_UNIT_BY_SHOCK = {
    "percentage_point": "ratio",
    "basis_point": "basis_point",
    "percent": "ratio",
    "absolute": None,  # the parameter's own declared unit/scale
}
_SHOCK_SEMANTICS = {
    "additive": {"pp", "basis_point"},
    "multiplicative": {"percent"},
    "absolute": {
        name
        for name, description in _UNIT_DESCRIPTIONS.items()
        if description["family"] in {"money", "count"}
    },
}


def _shock_type_for_target(
    shock_semantics: str, target: str, engine_unit: Any
) -> str:
    """Map (semantics, engine contract unit) to the engine's shock_type."""
    if shock_semantics == "absolute":
        return "absolute"
    if shock_semantics == "additive":
        require(
            target in {"ratio", "basis_point"},
            f"engine_unit {engine_unit} cannot carry an additive share shock; "
            f"the engine contract unit is ratio or basis_point",
        )
        return "percentage_point" if target == "ratio" else "basis_point"
    require(
        target == "ratio",
        f"engine_unit {engine_unit} cannot carry a multiplicative shock; "
        f"the engine contract unit is the ratio factor",
    )
    return "percent"


def build_sensitivity_test(
    *,
    parameter_id: str,
    value: Any,
    input_unit: str,
    shock_semantics: str,
    name: str | None = None,
    engine_unit: str | None = None,
) -> dict[str, Any]:
    """Build a sensitivity test whose shock unit is explicit and auditable.

    ``shock_semantics`` states how the shock acts on the parameter
    (additive on a ratio, multiplicative, or an absolute amount in the
    parameter's own unit); it must be compatible with ``input_unit`` — the
    wrong pairing (5 percent treated as 5 percentage points) fails loudly
    instead of producing a self-consistent wrong number.

    ``engine_unit`` is optional. When omitted the historical behavior is kept
    exactly: share shocks land on the engine's contract unit and absolute
    shocks record an identity in the parameter's own unit. When given, the
    shock is really converted into that target unit (same-currency scale
    conversion only) so ``shock_value`` is the amount the engine applies — a
    relabeled number is never accepted as a converted one.
    """
    require(
        isinstance(parameter_id, str) and parameter_id.strip(),
        "parameter_id is required",
    )
    require(shock_semantics in _SHOCK_SEMANTICS, f"unsupported shock semantics: {shock_semantics}")
    unit = _normalize_unit(input_unit, "input_unit")
    require(
        unit in _SHOCK_SEMANTICS[shock_semantics],
        f"input_unit {input_unit} cannot act as a {shock_semantics} shock",
    )
    if engine_unit is None:
        resolved_shock_type = {
            ("additive", "pp"): "percentage_point",
            ("additive", "basis_point"): "basis_point",
            ("multiplicative", "percent"): "percent",
        }.get((shock_semantics, unit), "absolute")
        # An absolute shock is expressed in the parameter's own declared unit, so
        # the engine unit is the input unit itself (identity record, still audited).
        target = _ENGINE_UNIT_BY_SHOCK[resolved_shock_type] or str(input_unit).strip()
    else:
        target = str(engine_unit).strip()
        resolved_shock_type = _shock_type_for_target(
            shock_semantics, _normalize_unit(engine_unit, "engine_unit"), engine_unit
        )
    record = convert_input_quantity(value, input_unit=input_unit, engine_unit=target)
    require(record["engine_value"] > 0, "shock magnitude must be positive")
    return {
        "name": name or parameter_id,
        "parameter_id": parameter_id,
        "shock_type": resolved_shock_type,
        "shock_value": record["engine_value"],
        "input_quantity": record,
    }
