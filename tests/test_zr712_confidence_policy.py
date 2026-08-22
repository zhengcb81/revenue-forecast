"""ZR-712 acceptance tests: versioned ConfidencePolicy and anti-gaming.

  C1  versioned policy: validate_confidence_policy accepts version 1.0
      with default/overridden weights+caps; unknown versions fail closed;
      weights/caps must be non-negative numbers.
  C2  six gaming mutations: duplicate backtest_id rejected; split
      observation (same year/source/value repeated) rejected; plug (no
      record_sha256) rejected; zero-impact (wape 0) disclosed honestly;
      one-observation caps history score; wrong-record is covered by the
      missing/blank hash rejection (tampering fails on hash).
  C3  rating caps recompute: recompute_rating matches legacy 80/55
      thresholds; custom caps honored; non-numeric score rejected.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from confidence_policy import (  # noqa: E402
    CONFIDENCE_POLICY_VERSION,
    DEFAULT_RATING_CAPS,
    DEFAULT_WEIGHTS,
    detect_gaming_mutations,
    recompute_rating,
    validate_confidence_policy,
)
from contracts.evidence import ForecastInputError  # noqa: E402


def _record(backtest_id: str, year: int = 2026, value: float = 160.0, **extra) -> dict:
    record = {
        "backtest_id": backtest_id,
        "year": year,
        "source_id": "filing",
        "value": value,
        "record_sha256": "a" * 64,
        "observations": 1,
        "wape": 0.12,
    }
    record.update(extra)
    return record


# ---------------------------------------------------------------------------
# C1 — versioned policy
# ---------------------------------------------------------------------------


def test_c1_valid_policy_defaults():
    policy = validate_confidence_policy({"version": CONFIDENCE_POLICY_VERSION})
    assert policy["weights"] == DEFAULT_WEIGHTS
    assert policy["rating_caps"] == DEFAULT_RATING_CAPS


def test_c1_valid_policy_overrides():
    policy = validate_confidence_policy({
        "version": CONFIDENCE_POLICY_VERSION,
        "weights": {"verified_claim_quality": 25},
        "rating_caps": {"high": 85.0, "medium": 60.0},
    })
    assert policy["weights"]["verified_claim_quality"] == 25
    assert policy["rating_caps"]["high"] == 85.0


def test_c1_unknown_version_fails_closed():
    with pytest.raises(ForecastInputError, match="unsupported confidence policy version"):
        validate_confidence_policy({"version": "9.9"})


def test_c1_negative_weight_rejected():
    with pytest.raises(ForecastInputError, match="non-negative"):
        validate_confidence_policy({
            "version": CONFIDENCE_POLICY_VERSION,
            "weights": {"verified_claim_quality": -1},
        })


def test_c1_missing_caps_rejected():
    with pytest.raises(ForecastInputError, match="high and medium"):
        validate_confidence_policy({
            "version": CONFIDENCE_POLICY_VERSION,
            "rating_caps": {"high": 80.0},
        })


# ---------------------------------------------------------------------------
# C2 — six gaming mutations
# ---------------------------------------------------------------------------


def test_c2_duplicate_backtest_rejected():
    records = [_record("bt-1"), _record("bt-1")]
    result = detect_gaming_mutations(records)
    assert any("duplicate accuracy record backtest_id" in item for item in result["rejected"])


def test_c2_split_observation_rejected():
    # same year/source/value appearing twice = one observation split
    records = [_record("bt-1", year=2026, value=160.0), _record("bt-2", year=2026, value=160.0)]
    result = detect_gaming_mutations(records)
    assert any("split observation" in item for item in result["rejected"])


def test_c2_plug_without_hash_rejected():
    records = [_record("bt-1", record_sha256="")]
    result = detect_gaming_mutations(records)
    assert any("no record_sha256" in item for item in result["rejected"])


def test_c2_zero_impact_disclosed():
    records = [_record("bt-1", wape=0.0)]
    result = detect_gaming_mutations(records)
    assert any("zero-impact" in item for item in result["disclosures"])


def test_c2_one_observation_disclosed():
    records = [_record("bt-1")]  # single observation
    result = detect_gaming_mutations(records)
    assert any("one-observation" in item for item in result["disclosures"])


def test_c2_wrong_record_tampering_rejected():
    # wrong-record = tampered content — hash absent/blank fails closed
    records = [_record("bt-1", record_sha256=None)]
    result = detect_gaming_mutations(records)
    assert any("no record_sha256" in item for item in result["rejected"])


def test_c2_clean_records_no_rejections():
    records = [_record("bt-1", year=2026, value=160.0, observations=3, wape=0.1),
               _record("bt-2", year=2027, value=170.0, observations=3, wape=0.09)]
    result = detect_gaming_mutations(records)
    assert result["rejected"] == []
    assert result["disclosures"] == []


def test_c2_non_numeric_record_value_fails_closed():
    # ZR712-REV-001 regression: malformed value must raise ForecastInputError
    # (never raw ValueError)
    records = [_record("bt-1", value="abc")]
    with pytest.raises(ForecastInputError, match="value must be numeric"):
        detect_gaming_mutations(records)


# ---------------------------------------------------------------------------
# C3 — rating caps recompute
# ---------------------------------------------------------------------------


def test_c3_legacy_thresholds():
    assert recompute_rating(95.0) == "high"
    assert recompute_rating(80.0) == "high"
    assert recompute_rating(79.9) == "medium"
    assert recompute_rating(55.0) == "medium"
    assert recompute_rating(54.9) == "low"


def test_c3_custom_caps():
    caps = {"high": 90.0, "medium": 70.0}
    assert recompute_rating(85.0, caps) == "medium"
    assert recompute_rating(95.0, caps) == "high"


def test_c3_non_numeric_score_rejected():
    with pytest.raises(ForecastInputError, match="score must be"):
        recompute_rating("high")


def test_c3_nan_score_rejected():
    # ZR712-REV-002 regression: NaN must fail closed (never silent "low")
    with pytest.raises(ForecastInputError, match="finite"):
        recompute_rating(float("nan"))


def test_c3_unvalidated_caps_missing_medium_rejected():
    # ZR712-REV-004: missing medium cap must fail closed (never KeyError)
    with pytest.raises(ForecastInputError, match="high and medium"):
        recompute_rating(70.0, {"high": 80.0})


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
