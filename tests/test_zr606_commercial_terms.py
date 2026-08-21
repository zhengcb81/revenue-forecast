"""ZR-606 acceptance tests: commercial terms layer.

  C1  provenance: every commercial variable is {value, source, assumption,
      period} — value finite (never inf/NaN — ZR-605 REV-001 fix), text
      fields non-empty; price required, others optional.
  C2  no double counting: net = (gross − TC − RC + premium +
      byproduct_credit − royalty_rate×gross) × FX; byproduct_credit is an
      independent addition (never part of volume × price).
  C3  sensitivity recompute: pure function — deterministic, idempotent,
      price/FX changes recompute correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from commercial_terms import (  # noqa: E402
    CommercialTerm,
    CommercialTerms,
    calculate_net_revenue,
    validate_commercial_terms,
)
from contracts.evidence import ForecastInputError  # noqa: E402

BASE_TERMS = {
    "price": {"value": 5.0, "source": "LME index", "assumption": "analyst", "period": "FY2026"},
    "payability": {"value": 0.95, "source": "smelter contract", "assumption": "contract", "period": "FY2026"},
    "tc": {"value": 0.2, "source": "TC contract", "assumption": "contract", "period": "FY2026"},
    "rc": {"value": 0.1, "source": "RC contract", "assumption": "contract", "period": "FY2026"},
    "premium": {"value": 0.05, "source": "premium schedule", "assumption": "analyst", "period": "FY2026"},
    "byproduct_credit": {"value": 2.0, "source": "gold byproduct", "assumption": "analyst", "period": "FY2026"},
    "fx_rate": {"value": 7.2, "source": "PBOC", "assumption": "spot", "period": "FY2026"},
    "royalty_rate": {"value": 0.03, "source": "royalty agreement", "assumption": "contract", "period": "FY2026"},
}


# ---------------------------------------------------------------------------
# C1 — provenance
# ---------------------------------------------------------------------------


def test_c1_valid_terms_passes():
    terms = validate_commercial_terms(BASE_TERMS)
    assert isinstance(terms, CommercialTerms)
    assert isinstance(terms.price, CommercialTerm)
    assert terms.price.value == 5.0
    assert terms.fx_rate is not None


def test_c1_price_required():
    bad = {k: v for k, v in BASE_TERMS.items() if k != "price"}
    with pytest.raises(ForecastInputError, match="price is required"):
        validate_commercial_terms(bad)


@pytest.mark.parametrize("field", ["payability", "tc", "rc",
                                   "premium", "byproduct_credit", "fx_rate",
                                   "royalty_rate"])
def test_c1_optional_terms_may_be_absent(field):
    terms = validate_commercial_terms(
        {k: v for k, v in BASE_TERMS.items() if k != field}
    )
    assert getattr(terms, field) is None


@pytest.mark.parametrize("bad_value", ["abc", True, None, float("inf"), float("-inf")])
def test_c1_non_finite_values_rejected(bad_value):
    # ZR-605 REV-001 fix: inf/-inf rejected via finite_number (NaN also)
    for field in ("price", "fx_rate", "royalty_rate"):
        bad = dict(BASE_TERMS)
        bad[field] = {**bad[field], "value": bad_value}
        with pytest.raises(ForecastInputError, match="finite|numeric"):
            validate_commercial_terms(bad)


@pytest.mark.parametrize("text_field", ["source", "assumption", "period"])
def test_c1_empty_text_fields_rejected(text_field):
    bad = dict(BASE_TERMS)
    bad["price"] = {**bad["price"], text_field: "  "}
    with pytest.raises(ForecastInputError, match="non-empty string"):
        validate_commercial_terms(bad)


def test_c1_frozen_dataclasses():
    terms = validate_commercial_terms(BASE_TERMS)
    with pytest.raises(AttributeError):
        terms.price = CommercialTerm(1.0, "x", "y", "FY2026")  # type: ignore[misc]


# ---------------------------------------------------------------------------
# C2 — no double counting
# ---------------------------------------------------------------------------


def test_c2_net_revenue_hand_check():
    terms = validate_commercial_terms(BASE_TERMS)
    result = calculate_net_revenue(100.0, terms)
    # gross = 100 × 5.0 = 500
    # deductions = 0.2 + 0.1 + 0.03×500 = 15.3
    # additions = 0.05 + 2.0 = 2.05
    # net_before_fx = 500 − 15.3 + 2.05 = 486.75
    # net = 486.75 × 7.2 = 3504.6
    assert result["gross"] == pytest.approx(500.0)
    assert result["deductions"] == pytest.approx(15.3)
    assert result["additions"] == pytest.approx(2.05)
    assert result["net"] == pytest.approx(3504.6)


def test_c2_minimal_terms_no_double_counting():
    # price only: net == gross (no hidden deductions/additions)
    terms = validate_commercial_terms({"price": BASE_TERMS["price"]})
    result = calculate_net_revenue(100.0, terms)
    assert result["gross"] == pytest.approx(500.0)
    assert result["deductions"] == pytest.approx(0.0)
    assert result["additions"] == pytest.approx(0.0)
    assert result["net"] == pytest.approx(500.0)


def test_c2_byproduct_is_independent_addition():
    # byproduct credit adds once — never multiplied by volume
    terms = validate_commercial_terms(BASE_TERMS)
    result_small = calculate_net_revenue(1.0, terms)
    result_large = calculate_net_revenue(1000.0, terms)
    # additions identical regardless of volume (per-unit premium scales,
    # but byproduct_credit is fixed)
    assert result_small["additions"] == result_large["additions"] == pytest.approx(2.05)


# ---------------------------------------------------------------------------
# C3 — sensitivity recompute
# ---------------------------------------------------------------------------


def test_c3_deterministic_idempotent():
    terms = validate_commercial_terms(BASE_TERMS)
    first = calculate_net_revenue(100.0, terms)
    second = calculate_net_revenue(100.0, terms)
    assert first == second  # pure function


def test_c3_price_sensitivity_recompute():
    base_terms = validate_commercial_terms(BASE_TERMS)
    raised = validate_commercial_terms({
        **BASE_TERMS,
        "price": {**BASE_TERMS["price"], "value": 6.0},
    })
    base_net = calculate_net_revenue(100.0, base_terms)["net"]
    raised_net = calculate_net_revenue(100.0, raised)["net"]
    # Δnet = Δgross × (1 − royalty_rate) × fx = 100 × 1.0 × 0.97 × 7.2 = 698.4
    assert raised_net - base_net == pytest.approx(698.4)


def test_c3_fx_sensitivity_recompute():
    base_terms = validate_commercial_terms(BASE_TERMS)
    no_fx = validate_commercial_terms(
        {k: v for k, v in BASE_TERMS.items() if k != "fx_rate"}
    )
    base_net = calculate_net_revenue(100.0, base_terms)["net"]
    no_fx_net = calculate_net_revenue(100.0, no_fx)["net"]
    assert no_fx_net == pytest.approx(486.75)  # fx=1.0
    assert base_net == pytest.approx(no_fx_net * 7.2)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
