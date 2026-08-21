"""ZR-603 acceptance tests: asset ownership/consolidation timeline +
geography hierarchy contract.

  C1  timeline: effective-dated fractions (unique ISO dates, fraction in
      (0,1]); lookup = latest effective_date <= on_date, fail-closed
      before the first entry (no implicit backwards inheritance);
      acquisition effective date changes the fraction; mid-period change
      is fail-closed by default, explicit allow_pro_rata resolves with a
      day-weighted average.
  C2  no double equity multiplication: chain product applied once
      (group 60% * intermediate 70% == 0.42); apply_ownership_share on
      one_hundred_percent basis multiplies exactly once; equity_share
      basis is rejected (already applied — the Kamoa/Porgera guard);
      consolidated basis is not equity-discounted at this layer.
  C3  geography: additive {country, region?} validation (None passes);
      searchable country -> (region|None) -> names index; segment-level
      additive keys validated inside validate_document.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from asset_ownership import (  # noqa: E402
    apply_ownership_share,
    effective_group_share,
    fraction_for_period,
    geography_index,
    ownership_fraction_on,
    validate_geography,
    validate_ownership_timeline,
)
from contracts.constants import ASSET_FACT_OWNERSHIP_BASES  # noqa: E402
from contracts.document import validate_document  # noqa: E402
from contracts.evidence import ForecastInputError  # noqa: E402
from test_data_contract import finalize_contract, valid_document  # noqa: E402

TIMELINE = [
    {"effective_date": "2015-05-01", "ownership_fraction": 0.45},
    {"effective_date": "2026-07-01", "ownership_fraction": 0.60},
]
CHAIN = [
    [{"effective_date": "2015-05-01", "ownership_fraction": 0.6}],
    [{"effective_date": "2015-05-01", "ownership_fraction": 0.7}],
]

# ---------------------------------------------------------------------------
# C1 — ownership timeline
# ---------------------------------------------------------------------------


def test_c1_valid_timeline_passes():
    validate_ownership_timeline(TIMELINE)


def test_c1_empty_timeline_rejected():
    for bad in ([], "not-a-list", None):
        with pytest.raises(ForecastInputError, match="non-empty list"):
            validate_ownership_timeline(bad)


def test_c1_duplicate_effective_date_rejected():
    timeline = [
        {"effective_date": "2015-05-01", "ownership_fraction": 0.45},
        {"effective_date": "2015-05-01", "ownership_fraction": 0.60},
    ]
    with pytest.raises(ForecastInputError, match="duplicate effective_date"):
        validate_ownership_timeline(timeline)


@pytest.mark.parametrize("fraction", [0, 0.0, 1.5, -0.1, "0.5"])
def test_c1_fraction_bounds_rejected(fraction):
    timeline = [{"effective_date": "2015-05-01", "ownership_fraction": fraction}]
    with pytest.raises(ForecastInputError, match=r"numeric|in \(0, 1\]"):
        validate_ownership_timeline(timeline)


def test_c1_non_iso_date_rejected():
    timeline = [{"effective_date": "2015/05/01", "ownership_fraction": 0.45}]
    with pytest.raises(ForecastInputError, match="YYYY-MM-DD"):
        validate_ownership_timeline(timeline)


def test_c1_before_first_entry_fail_closed():
    with pytest.raises(ForecastInputError, match="does not cover"):
        ownership_fraction_on(TIMELINE, "2015-04-30")


def test_c1_acquisition_effective_date_changes_fraction():
    assert ownership_fraction_on(TIMELINE, "2026-06-30") == 0.45
    assert ownership_fraction_on(TIMELINE, "2026-07-01") == 0.60
    assert ownership_fraction_on(TIMELINE, "2026-12-31") == 0.60


def test_c1_mid_period_change_fail_closed_then_pro_rata():
    with pytest.raises(ForecastInputError, match="allow_pro_rata"):
        fraction_for_period(TIMELINE, "2026-01-01", "2026-12-31")
    # explicit day-weighted: 181 days at 0.45 + 184 days at 0.60 over 365
    weighted = fraction_for_period(
        TIMELINE, "2026-01-01", "2026-12-31", allow_pro_rata=True
    )
    assert weighted == pytest.approx((181 * 0.45 + 184 * 0.60) / 365)


def test_c1_stable_period_returns_fraction_directly():
    assert fraction_for_period(TIMELINE, "2016-01-01", "2016-12-31") == 0.45


# ---------------------------------------------------------------------------
# C2 — no double equity multiplication
# ---------------------------------------------------------------------------


def test_c2_chain_product_applied_once():
    assert effective_group_share(CHAIN, "2026-12-31") == pytest.approx(0.42)


def test_c2_single_level_share():
    assert effective_group_share(CHAIN[:1], "2026-12-31") == pytest.approx(0.6)


def test_c2_apply_share_on_hundred_percent_basis_once():
    attributed = apply_ownership_share(
        {"FY2026": 100.0, "FY2027": 200.0},
        "one_hundred_percent",
        CHAIN,
        {"FY2026": ("2026-01-01", "2026-12-31"),
         "FY2027": ("2027-01-01", "2027-12-31")},
    )
    assert attributed == {"FY2026": pytest.approx(42.0),
                          "FY2027": pytest.approx(84.0)}


def test_c2_equity_share_double_multiplication_rejected():
    with pytest.raises(ForecastInputError, match="already applied"):
        apply_ownership_share(
            {"FY2026": 42.0}, "equity_share", CHAIN,
            {"FY2026": ("2026-01-01", "2026-12-31")},
        )


def test_c2_consolidated_basis_not_discounted():
    with pytest.raises(ForecastInputError, match="not equity-discounted"):
        apply_ownership_share(
            {"FY2026": 100.0}, "consolidated", CHAIN,
            {"FY2026": ("2026-01-01", "2026-12-31")},
        )


def test_c2_unsupported_basis_rejected():
    with pytest.raises(ForecastInputError, match="unsupported ownership basis"):
        apply_ownership_share(
            {"FY2026": 100.0}, "two_thirds", CHAIN,
            {"FY2026": ("2026-01-01", "2026-12-31")},
        )
    # basis vocabulary is exactly the ZR-602 enum
    assert ASSET_FACT_OWNERSHIP_BASES == {
        "one_hundred_percent", "equity_share", "consolidated",
    }


# ---------------------------------------------------------------------------
# C3 — geography hierarchy
# ---------------------------------------------------------------------------


def test_c3_geography_validation_contract():
    validate_geography({"country": "DR Congo", "region": "Lualaba"})
    validate_geography({"country": "DR Congo"})
    validate_geography(None)  # additive — absent geography passes
    for bad in ({}, {"country": "  "}, {"country": 7},
                {"country": "X", "region": " "}, ["country"]):
        with pytest.raises(ForecastInputError):
            validate_geography(bad)


def test_c3_geography_index_searchable():
    assets = [
        {"name": "mine_a", "geography": {"country": "DR Congo", "region": "Lualaba"}},
        {"name": "mine_b", "geography": {"country": "DR Congo"}},
        {"name": "plant_c", "geography": {"country": "Serbia", "region": "Bor"}},
    ]
    index = geography_index(assets)
    assert index["DR Congo"]["Lualaba"] == ["mine_a"]
    assert index["DR Congo"][None] == ["mine_b"]
    assert index["Serbia"]["Bor"] == ["plant_c"]
    # assets without geography are not silently omitted
    with pytest.raises(ForecastInputError, match="no geography"):
        geography_index([{"name": "mine_x"}])


def test_c3_document_level_segment_keys_additive():
    data = valid_document()
    segment = data["segments"][0]
    segment["geography"] = {"country": "DR Congo", "region": "Lualaba"}
    segment["ownership"] = CHAIN
    validate_document(finalize_contract(data))  # valid keys pass end-to-end
    # invalid ownership fraction on a segment fails closed at document level
    bad = valid_document()
    bad["segments"][0]["ownership"] = [
        [{"effective_date": "2015-05-01", "ownership_fraction": 1.4}],
    ]
    with pytest.raises(ForecastInputError, match="ownership_fraction"):
        validate_document(finalize_contract(bad))
    # blank country on a segment fails closed at document level
    ugly = valid_document()
    ugly["segments"][0]["geography"] = {"country": " "}
    with pytest.raises(ForecastInputError, match="geography"):
        validate_document(finalize_contract(ugly))
    # legacy segments without the keys are unaffected
    validate_document(finalize_contract(valid_document()))


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
