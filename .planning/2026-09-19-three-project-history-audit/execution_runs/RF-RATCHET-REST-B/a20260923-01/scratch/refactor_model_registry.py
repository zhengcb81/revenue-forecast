"""File 1/3: refactor calculate_registered_model (CC 28) into top-level helpers (cap 9).

Splices everything from 'def calculate_registered_model(' to EOF with the helper-split
version. Statements/conditions/error messages are moved VERBATIM (transcribed from the
promotion payload bytes pinned in binding_before.json); every helper is a TOP-LEVEL
module function so the ratchet measures each separately. Target: all helpers + main <= 9.
"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(sys.argv[1])
text = TARGET.read_text(encoding="utf-8")
anchor = "def calculate_registered_model("
idx = text.index(anchor)
head = text[:idx]

NEW = '''def _resolve_model_spec(model_id: str) -> ModelSpec:
    """Registered spec lookup, with the frozen unsupported-model error."""
    try:
        spec = MODEL_REGISTRY[model_id]
    except KeyError as exc:
        raise ModelRegistryError(f"unsupported revenue model: {model_id}") from exc
    return spec


def _validated_base_revenue(model_id: str, base_revenue: float) -> float:
    """Finite non-negative base revenue, with the frozen error messages."""
    base = _finite_model_number(base_revenue, f"{model_id}.base_revenue")
    if base < 0:
        raise ModelRegistryError(f"{model_id}.base_revenue cannot be negative")
    return base


def _validated_years(model_id: str, years: Sequence[int]) -> None:
    """Fiscal-year values must be present, bool-free ints in 1..9999, ordered."""
    if not years or any(isinstance(year, bool) or not isinstance(year, int) or not 1 <= year <= 9999 for year in years):
        raise ModelRegistryError(f"{model_id}.years must contain fiscal years")
    _validated_year_order(model_id, years)


def _validated_year_order(model_id: str, years: Sequence[int]) -> None:
    """Years must be consecutive and strictly increasing."""
    if any(later != earlier + 1 for earlier, later in zip(years, years[1:])):
        raise ModelRegistryError(f"{model_id}.years must be consecutive and increasing")


def _validate_driver_sets(
    model_id: str,
    spec: ModelSpec,
    drivers: Mapping[str, list[float]],
) -> None:
    """Exact driver-key contract: no missing required, no unsupported extras."""
    missing = set(spec.required) - set(drivers)
    if missing:
        raise ModelRegistryError(f"missing drivers for {model_id}: {', '.join(sorted(missing))}")
    extra = set(drivers) - set(spec.required) - set(spec.optional)
    if extra:
        raise ModelRegistryError(f"unsupported drivers for {model_id}: {', '.join(sorted(extra))}")


def _driver_series(
    model_id: str,
    spec: ModelSpec,
    driver: str,
    drivers: Mapping[str, list[float]],
    years: Sequence[int],
) -> object:
    # --- I-10-B defect 1 fix (T1-22) ------------------------------------
    # Previously: drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))
    # That silently filled any optional driver lacking an explicit default
    # with 0.0, encoding "absent" and "not found" as the SAME input.
    # Now: an omitted driver is legal ONLY when spec.defaults carries an
    # explicit value for it.  Note we deliberately do NOT substitute an
    # explicit 0.0 — that would still fail to distinguish "not found".
    if driver not in drivers:
        if driver not in spec.defaults:
            raise ModelRegistryError(
                f"missing driver for {model_id}: {driver} has no explicit default"
            )
        values: object = [spec.defaults[driver]] * len(years)
    else:
        values = drivers[driver]
    if not isinstance(values, (list, tuple)) or len(values) != len(years):
        raise ModelRegistryError(f"driver {model_id}.{driver} must contain one value per forecast year")
    return values


def _normalized_driver(
    model_id: str,
    driver: str,
    years: Sequence[int],
    values: object,
    lower: float,
    upper: float,
) -> list[float]:
    """One driver's per-year finite values, bounds-checked in year order."""
    numbers: list[float] = []
    for year, value in zip(years, values):
        number = _finite_model_number(value, f"{model_id}.{driver}.FY{year}")
        if not lower <= number <= upper:
            raise ModelRegistryError(f"driver {model_id}.{driver} must be between {lower} and {upper}: FY{year}")
        numbers.append(number)
    return numbers


def _normalized_drivers(
    model_id: str,
    spec: ModelSpec,
    drivers: Mapping[str, list[float]],
    years: Sequence[int],
) -> dict[str, list[float]]:
    """Materialize every declared driver in (required + optional) order."""
    normalized: dict[str, list[float]] = {}
    for driver in spec.required + spec.optional:
        values = _driver_series(model_id, spec, driver, drivers, years)
        lower, upper = driver_value_bounds(model_id, driver)
        normalized[driver] = _normalized_driver(model_id, driver, years, values, lower, upper)
    return normalized


def _checked_model_path(
    model_id: str,
    spec: ModelSpec,
    base: float,
    normalized: dict[str, list[float]],
    years: Sequence[int],
) -> list[float]:
    """Run the calculator and validate path length, finiteness and sign."""
    try:
        result = spec.calculator(base, normalized, years)
    except ArithmeticError as exc:
        raise ModelRegistryError(f"invalid arithmetic in revenue model: {model_id}") from exc
    if len(result) != len(years):
        raise ModelRegistryError(f"calculator returned wrong path length: {model_id}")
    checked = [_finite_model_number(value, f"{model_id}.revenue.FY{year}") for year, value in zip(years, result)]
    if any(value < 0 for value in checked):
        raise ModelRegistryError(f"calculated revenue cannot be negative: {model_id}")
    return checked


def calculate_registered_model(
    model_id: str,
    base_revenue: float,
    drivers: Mapping[str, list[float]],
    years: Sequence[int],
) -> list[float]:
    """Pure registered-model calculation: validate, normalize, run, check.

    Ratchet refactor (RF-RATCHET-REST-B): the validation stages live in the
    top-level helpers above; behavior — evaluation order, error types, error
    message strings and returned values — is byte-identical to the promotion
    payload this file was promoted as (62f864b9...).
    """
    spec = _resolve_model_spec(model_id)
    base = _validated_base_revenue(model_id, base_revenue)
    _validated_years(model_id, years)
    if not isinstance(drivers, Mapping):
        raise ModelRegistryError(f"{model_id}.drivers must be a mapping")
    _validate_driver_sets(model_id, spec, drivers)
    normalized = _normalized_drivers(model_id, spec, drivers, years)
    return _checked_model_path(model_id, spec, base, normalized, years)
'''

TARGET.write_text(head + NEW, encoding="utf-8", newline="\n")
print(f"spliced at char {idx}; new size {TARGET.stat().st_size} B")
