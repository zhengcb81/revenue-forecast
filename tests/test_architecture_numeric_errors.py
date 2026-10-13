"""Malformed real arithmetic returns the RF error contract without numeric repair."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from contracts.evidence import ForecastInputError, finite_number
from forecast.calc import evaluate_derived_formula


def test_integer_overflow_is_reported_as_nonfinite_input():
    with pytest.raises(ForecastInputError, match="finite"):
        finite_number(10 ** 10000, "reported revenue")


@pytest.mark.parametrize(("formula", "inputs"), [
    ("x0**x1", [-1, 0.5]), ("x0**x1", [0, -1]),
    ("x0*x0", [1e308]), ("x0**10", [1e308]),
])
def test_invalid_real_formula_arithmetic_has_a_named_contract_error(formula, inputs):
    with pytest.raises(ForecastInputError):
        evaluate_derived_formula(formula, inputs)


@pytest.mark.parametrize(("formula", "inputs", "expected"), [
    ("x0**x1", [-2, 3], -8), ("x0**x1", [-2, 2], 4),
    ("x0*x1", [1e150, 1e150], 1e150 * 1e150), ("-x0+x1", [5, 2], -3),
])
def test_valid_signed_and_large_real_arithmetic_is_preserved(formula, inputs, expected):
    assert evaluate_derived_formula(formula, inputs) == expected


def test_scenario_order_accepts_only_machine_roundoff_without_changing_values():
    import math
    from contracts.evidence import scenario_ordered
    base = 103.125
    low = math.nextafter(base, math.inf)
    assert scenario_ordered(low, base, base)
    assert low != base
    far = base
    for _ in range(5):
        far = math.nextafter(far, math.inf)
    assert not scenario_ordered(far, base, base)
    assert not scenario_ordered(104, base, 105)
