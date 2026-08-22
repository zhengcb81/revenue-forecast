"""ZR-707 acceptance tests: mixed recognition/gross-net and multi-commodity.

  C1  Mixed recognition: same company different segments can use different
      recognition modes (modeled_as_recognized / lagged_activity); validate_
      document accepts mixed-mode documents; each segment validates
      independently.
  C2  Multi-commodity product matrix: a single mine can have multiple
      commodity segments (copper + gold); each commodity has its own model;
      no duplicate segment names.
  C3  Presentation consistency: each segment declares gross/net; trading/other
      activities use correct presentation (not approximated); segment bridge
      with mixed presentations validates correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.evidence import ForecastInputError  # noqa: E402
from mixed_recognition import (  # noqa: E402
    validate_commodity_matrix,
    validate_mixed_recognition,
    validate_presentation_consistency,
)
from contracts.constants import PRESENTATIONS, RECOGNITION_MODES  # noqa: E402

VALID_RECOGNITION = {
    "mode": "modeled_as_recognized",
    "timing": "point_in_time",
    "trigger": "customer acceptance",
    "presentation": "gross",
    "modeled_presentation": "gross",
    "basis_claim_ids": [],
    "basis_source_ids": ["filing"],
}


# ---------------------------------------------------------------------------
# C1 — mixed recognition
# ---------------------------------------------------------------------------


def test_c1_mixed_recognition_modes_accepted():
    segments = [
        {"name": "copper", "recognition": {**VALID_RECOGNITION, "mode": "modeled_as_recognized"}},
        {"name": "gold", "recognition": {**VALID_RECOGNITION, "mode": "lagged_activity"}},
    ]
    validate_mixed_recognition(segments)  # must not raise


def test_c1_single_mode_accepted():
    segments = [
        {"name": "copper", "recognition": {**VALID_RECOGNITION, "mode": "modeled_as_recognized"}},
    ]
    validate_mixed_recognition(segments)


def test_c1_invalid_mode_rejected():
    segments = [
        {"name": "copper", "recognition": {**VALID_RECOGNITION, "mode": "invalid_mode"}},
    ]
    with pytest.raises(ForecastInputError, match="unsupported recognition mode"):
        validate_mixed_recognition(segments)


def test_c1_no_segments_passes():
    validate_mixed_recognition([])


def test_c1_vocabulary_exact():
    assert RECOGNITION_MODES == {"modeled_as_recognized", "lagged_activity"}


# ---------------------------------------------------------------------------
# C2 — multi-commodity product matrix
# ---------------------------------------------------------------------------


def test_c2_multi_commodity_segments_accepted():
    segments = [
        {"name": "mine_a_copper", "recognition": {**VALID_RECOGNITION, "presentation": "gross"}},
        {"name": "mine_a_gold", "recognition": {**VALID_RECOGNITION, "presentation": "gross"}},
    ]
    validate_commodity_matrix(segments)  # must not raise


def test_c2_duplicate_segment_names_rejected():
    segments = [
        {"name": "mine_a_copper", "recognition": {**VALID_RECOGNITION}},
        {"name": "mine_a_copper", "recognition": {**VALID_RECOGNITION}},
    ]
    with pytest.raises(ForecastInputError, match="duplicate segment name"):
        validate_commodity_matrix(segments)


def test_c2_empty_segments_passes():
    validate_commodity_matrix([])


# ---------------------------------------------------------------------------
# C3 — presentation consistency
# ---------------------------------------------------------------------------


def test_c3_gross_presentation_accepted():
    segments = [{"name": "mining", "recognition": {**VALID_RECOGNITION, "presentation": "gross"}}]
    validate_presentation_consistency(segments)


def test_c3_net_presentation_accepted():
    segments = [{"name": "trading", "recognition": {**VALID_RECOGNITION, "presentation": "net"}}]
    validate_presentation_consistency(segments)


def test_c3_mixed_presentations_accepted():
    segments = [
        {"name": "mining", "recognition": {**VALID_RECOGNITION, "presentation": "gross"}},
        {"name": "trading", "recognition": {**VALID_RECOGNITION, "presentation": "net"}},
    ]
    validate_presentation_consistency(segments)


def test_c3_invalid_presentation_rejected():
    segments = [{"name": "mining", "recognition": {**VALID_RECOGNITION, "presentation": "invalid"}}]
    with pytest.raises(ForecastInputError, match="unsupported presentation"):
        validate_presentation_consistency(segments)


def test_c3_presentations_exact():
    assert PRESENTATIONS == {"gross", "net"}


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
