"""Independent hand anchors for the DU8 comparison owner.

Every value here was computed with :mod:`decimal` from the contract text in
``references/management-targets.md`` and
``references/target-measurement-comparison.md``. This module imports NO
production comparison code, so it cannot inherit the owner's arithmetic: it is
the anchor the owner is checked against, not a second copy of it.

The two bands are deliberately recorded side by side, because DU8 froze them
as two compatibility paths instead of unifying them:

* legacy ``abs_tol``  = ``max(1.0, |v|) * t``     (fixed one-unit floor)
* typed  ``abs_tol``  = ``max(|v|, 1e-12) * t``   (the target's own magnitude)

They agree only at ``|v| >= 1``. Below that the legacy floor is the wider band.
"""

from __future__ import annotations

from decimal import Decimal

TOLERANCE = Decimal("0.01")

# name -> (expression description, expected Decimal)
LEGACY_ANCHORS: dict[str, tuple[str, Decimal]] = {
    # references/management-targets.md: abs_tol = max(1.0, |v|) * t
    "legacy_approximately_abs_tol_small_target": (
        "max(1, 0.5) * 0.01",
        Decimal("0.01"),
    ),
    "legacy_approximately_abs_tol_at_one": (
        "max(1, 1) * 0.01",
        Decimal("0.01"),
    ),
    "legacy_approximately_abs_tol_large_target": (
        "max(1, 144) * 0.01",
        Decimal("1.44"),
    ),
    # references/management-targets.md legacy at_least/at_most: v * (1 -/+ t)
    "legacy_at_least_bound_144": (
        "144 * (1 - 0.01)",
        Decimal("142.56"),
    ),
    "legacy_at_most_bound_144": (
        "144 * (1 + 0.01)",
        Decimal("145.44"),
    ),
    "legacy_at_least_bound_one": (
        "1 * (1 - 0.01)",
        Decimal("0.99"),
    ),
    # revenue_report.py legacy ratio rule: None if v == 0 else observed / v
    "legacy_attainment_ratio_4905_over_500": (
        "0.4905 / 0.5",
        Decimal("0.981"),
    ),
}

TYPED_ANCHORS: dict[str, tuple[str, Decimal]] = {
    # references/management-targets.md DU6 table: abs_tol = max(|v|, 1e-12) * t
    "typed_approximately_abs_tol_half": (
        "max(0.5, 1e-12) * 0.01",
        Decimal("0.005"),
    ),
    "typed_approximately_abs_tol_large": (
        "max(144, 1e-12) * 0.01",
        Decimal("1.44"),
    ),
    # DU6 acceptance_bound for a negative point target widens away from zero.
    "typed_at_least_negative_widens_down": (
        "-0.10 - 0.01 * |{-0.10}|",
        Decimal("-0.101"),
    ),
    "typed_at_most_negative_widens_up": (
        "-0.10 + 0.01 * |{-0.10}|",
        Decimal("-0.099"),
    ),
}

# The reachable divergence frozen as the A-node RED: a 0.5 target observed at
# 0.4905 is inside the legacy band [0.490, 0.510] but outside the typed band.
DIVERGENCE_CASE = {
    "target_value": Decimal("0.5"),
    "observed": Decimal("0.4905"),
    "legacy_accepted": True,
    "typed_accepted": False,
}
