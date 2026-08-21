"""ZR-607 acceptance tests: internal-flow / consolidation accounting bridge.

  C1  traceability: InternalFlow = {flow_id, source, destination, product,
      volume, transfer_price, period, scenario} — text fields non-empty,
      volume/transfer_price finite > 0 (finite_number); any gap fails
      closed (never default 0).
  C2  elimination: internal_revenue = volume × transfer_price;
      eliminate_internal_revenue → {gross, internal_total, net} with
      net = external (internal sales never double counted); period/
      scenario filters.
  C3  composition: elimination composes with ZR-606 commercial terms
      (terms applied to flows before elimination) and the gross/net bridge
      is exact.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from contracts.evidence import ForecastInputError  # noqa: E402
from internal_flow import (  # noqa: E402
    InternalFlow,
    eliminate_internal_revenue,
    internal_revenue,
    validate_internal_flow,
)

VALID_FLOW = {
    "flow_id": "flow-001",
    "source": "mine_a",
    "destination": "smelter_internal",
    "product": "copper concentrate",
    "volume": 100.0,
    "transfer_price": 50.0,
    "period": "FY2026",
    "scenario": "base",
}


# ---------------------------------------------------------------------------
# C1 — traceability
# ---------------------------------------------------------------------------


def test_c1_valid_flow_passes():
    flow = validate_internal_flow(VALID_FLOW)
    assert isinstance(flow, InternalFlow)
    assert flow.flow_id == "flow-001"
    assert flow.volume == 100.0


@pytest.mark.parametrize("field", [
    "flow_id", "source", "destination", "product", "volume",
    "transfer_price", "period", "scenario",
])
def test_c1_missing_field_creates_gap(field):
    bad = dict(VALID_FLOW)
    bad.pop(field)
    with pytest.raises(ForecastInputError, match=f"{field} is required"):
        validate_internal_flow(bad)


@pytest.mark.parametrize("field,bad", [
    ("flow_id", "  "), ("source", "  "), ("destination", ""),
    ("product", "  "), ("period", "  "),
])
def test_c1_empty_text_fields_rejected(field, bad):
    bad_flow = dict(VALID_FLOW, **{field: bad})
    with pytest.raises(ForecastInputError, match="non-empty string"):
        validate_internal_flow(bad_flow)


@pytest.mark.parametrize("bad_value", [
    float("inf"), float("-inf"), float("nan"), "abc", True, None,
])
def test_c1_non_finite_values_rejected(bad_value):
    for field in ("volume", "transfer_price"):
        bad = dict(VALID_FLOW, **{field: bad_value})
        with pytest.raises(ForecastInputError, match="finite|numeric"):
            validate_internal_flow(bad)


def test_c1_non_positive_volume_and_price_rejected():
    for field in ("volume", "transfer_price"):
        bad = dict(VALID_FLOW, **{field: 0.0})
        with pytest.raises(ForecastInputError, match="positive"):
            validate_internal_flow(bad)


def test_c1_invalid_scenario_rejected():
    bad = dict(VALID_FLOW, scenario="extreme")
    with pytest.raises(ForecastInputError, match="scenario"):
        validate_internal_flow(bad)


def test_c1_frozen_dataclass():
    flow = validate_internal_flow(VALID_FLOW)
    with pytest.raises(AttributeError):
        flow.volume = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# C2 — elimination (no double counting)
# ---------------------------------------------------------------------------


def test_c2_internal_revenue_hand_check():
    flow = validate_internal_flow(VALID_FLOW)
    assert internal_revenue(flow) == pytest.approx(5000.0)  # 100 × 50


def test_c2_elimination_no_double_counting():
    flows = [
        validate_internal_flow(VALID_FLOW),
        validate_internal_flow({**VALID_FLOW, "flow_id": "flow-002",
                                "volume": 200.0, "transfer_price": 40.0}),
    ]
    result = eliminate_internal_revenue(10000.0, flows)
    # internal_total = 5000 + 8000 = 13000; net = external = 10000
    assert result["gross"] == pytest.approx(23000.0)
    assert result["internal_total"] == pytest.approx(13000.0)
    assert result["net"] == pytest.approx(10000.0)
    # net NEVER includes internal sales — no double counting


def test_c2_period_scenario_filters():
    flows = [
        validate_internal_flow(VALID_FLOW),  # FY2026/base
        validate_internal_flow({**VALID_FLOW, "flow_id": "flow-2027",
                                "period": "FY2027", "volume": 50.0}),
        validate_internal_flow({**VALID_FLOW, "flow_id": "flow-low",
                                "scenario": "low", "volume": 30.0}),
    ]
    result = eliminate_internal_revenue(9000.0, flows, period="FY2026")
    # FY2026 flows: flow-001 (base, 5000) + flow-low (low, 1500) = 6500
    assert result["internal_total"] == pytest.approx(6500.0)
    assert result["net"] == pytest.approx(9000.0)
    result_scenario = eliminate_internal_revenue(9000.0, flows, scenario="base")
    # FY2026/base + FY2027/base = 5000 + 2500
    assert result_scenario["internal_total"] == pytest.approx(7500.0)


def test_c2_empty_flows_no_elimination():
    result = eliminate_internal_revenue(10000.0, [])
    assert result["gross"] == result["net"] == pytest.approx(10000.0)
    assert result["internal_total"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# C3 — composition
# ---------------------------------------------------------------------------


def test_c3_composes_with_commercial_terms():
    # internal flow priced via ZR-606 commercial terms (net of TC/RC)
    from commercial_terms import calculate_net_revenue, validate_commercial_terms

    terms = validate_commercial_terms({
        "price": {"value": 50.0, "source": "LME", "assumption": "a", "period": "FY2026"},
        "tc": {"value": 2.0, "source": "TC", "assumption": "a", "period": "FY2026"},
        "rc": {"value": 1.0, "source": "RC", "assumption": "a", "period": "FY2026"},
    })
    flow = validate_internal_flow(VALID_FLOW)
    priced = calculate_net_revenue(flow.volume, terms)
    # gross = 100 × 50 = 5000; deductions = 3.0; net = 4997.0
    assert priced["gross"] == pytest.approx(5000.0)
    assert priced["net"] == pytest.approx(4997.0)
    # elimination uses transfer value, never double counts
    result = eliminate_internal_revenue(50000.0, [flow])
    assert result["net"] == pytest.approx(50000.0)


def test_c3_gross_net_bridge_exact():
    flows = [validate_internal_flow(VALID_FLOW)]
    result = eliminate_internal_revenue(10000.0, flows)
    assert result["net"] == result["gross"] - result["internal_total"]
    assert result["net"] < result["gross"]  # internal eliminated


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
