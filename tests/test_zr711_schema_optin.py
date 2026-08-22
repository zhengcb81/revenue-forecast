"""ZR-711 acceptance tests: additive schema 3.8 opt-in and 3.7 compatibility.

  C1  3.7 zero regression: existing 3.7 documents validate identically;
      FORECAST_SCHEMA_VERSION stays "3.7"; SUPPORTED set contains both
      versions; SCHEMA_EMIT_ENGINES for "3.8" points to current engine.
  C2  3.8 opt-in: schema_version "3.8" passes validate_document; additive
      operating_units key (list of MineYearOperations) validated when
      present; each entry must be a complete seven-field operation (fail-
      closed on gaps); absent key passes (additive, 3.7 unaffected).
  C3  converter: convert_3_7_to_3_8 bumps version and adds operating_units
      as empty list (honest gap — never guesses); convert_3_8_to_3_7 strips
      additive keys and restores 3.7; round-trip 3.7→3.8→3.7 is canonically
      equal to the original document.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from contracts.constants import (  # noqa: E402
    FORECAST_SCHEMA_VERSION,
    OPT_IN_SCHEMA_VERSION,
    SUPPORTED_FORECAST_SCHEMA_VERSIONS,
)
from contracts.document import (  # noqa: E402
    validate_document,
    validate_operating_units,
)
from contracts.evidence import ForecastInputError  # noqa: E402
from schema_compatibility import SCHEMA_EMIT_ENGINES  # noqa: E402
from schema_optin import (  # noqa: E402
    convert_3_7_to_3_8,
    convert_3_8_to_3_7,
)
from test_data_contract import finalize_contract, valid_document  # noqa: E402

VALID_OP = {
    "volume": 1000.0,
    "grade": 0.5,
    "recovery": 0.90,
    "payable": 0.95,
    "product": "copper concentrate",
    "period": "FY2026",
    "scenario": "base",
}


# ---------------------------------------------------------------------------
# C1 — 3.7 zero regression
# ---------------------------------------------------------------------------


def test_c1_forecast_schema_version_still_37():
    assert FORECAST_SCHEMA_VERSION == "3.7"


def test_c1_38_in_supported_and_emit():
    assert "3.8" in SUPPORTED_FORECAST_SCHEMA_VERSIONS
    assert "3.8" in SCHEMA_EMIT_ENGINES
    assert OPT_IN_SCHEMA_VERSION == "3.8"
    # SUPPORTED ⊆ EMIT (ZR-703 invariant)
    assert SUPPORTED_FORECAST_SCHEMA_VERSIONS <= set(SCHEMA_EMIT_ENGINES)


def test_c1_37_document_validates_unchanged():
    # full valid_document() through validate_document — 3.7 path untouched
    data = finalize_contract(valid_document())
    validated = validate_document(data)
    assert validated is not None
    assert data["schema_version"] == "3.7"


def test_c1_37_rejected_when_wrong_version():
    data = finalize_contract(valid_document())
    data["schema_version"] = "3.6"
    with pytest.raises(ForecastInputError, match="schema_version must be"):
        validate_document(data)


# ---------------------------------------------------------------------------
# C2 — 3.8 opt-in
# ---------------------------------------------------------------------------


def test_c2_38_document_validates():
    data = finalize_contract(valid_document())
    data["schema_version"] = "3.8"
    # operating_units absent — additive, passes
    validated = validate_document(data)
    assert validated is not None


def test_c2_operating_units_present_and_valid():
    data = finalize_contract(valid_document())
    data["schema_version"] = "3.8"
    data["operating_units"] = [VALID_OP]
    validated = validate_document(data)
    assert validated is not None


def test_c2_operating_units_gap_closed():
    bad = dict(VALID_OP)
    bad.pop("grade")
    data = finalize_contract(valid_document())
    data["schema_version"] = "3.8"
    data["operating_units"] = [bad]
    with pytest.raises(ForecastInputError, match="grade is required"):
        validate_document(data)


def test_c2_operating_units_must_be_list():
    data = finalize_contract(valid_document())
    data["schema_version"] = "3.8"
    data["operating_units"] = "not-a-list"
    with pytest.raises(ForecastInputError, match="operating_units must be"):
        validate_document(data)


def test_c2_validate_operating_units_standalone():
    # absent key returns empty
    assert validate_operating_units({}) == []
    # valid entry returns normalized list
    result = validate_operating_units({"operating_units": [VALID_OP]})
    assert len(result) == 1
    assert result[0]["volume"] == 1000.0
    # gap fails closed
    bad = dict(VALID_OP)
    bad["recovery"] = -1.0
    with pytest.raises(ForecastInputError):
        validate_operating_units({"operating_units": [bad]})


def test_c2_38_with_empty_operating_units():
    data = finalize_contract(valid_document())
    data["schema_version"] = "3.8"
    data["operating_units"] = []
    validated = validate_document(data)
    assert validated is not None  # empty list = explicit gap, not a failure


# ---------------------------------------------------------------------------
# C3 — converter (gap-only, reversible)
# ---------------------------------------------------------------------------


def test_c3_convert_37_to_38():
    doc = finalize_contract(valid_document())
    converted = convert_3_7_to_3_8(doc)
    assert converted["schema_version"] == "3.8"
    assert converted["operating_units"] == []  # honest gap, never guessed
    # original unchanged (deepcopy)
    assert doc["schema_version"] == "3.7"


def test_c3_convert_38_to_37():
    doc38 = finalize_contract(valid_document())
    doc38["schema_version"] = "3.8"
    doc38["operating_units"] = [VALID_OP]
    reverted = convert_3_8_to_3_7(doc38)
    assert reverted["schema_version"] == "3.7"
    assert "operating_units" not in reverted  # additive key stripped


def test_c3_round_trip_canonical_equality():
    original = finalize_contract(valid_document())
    round_trip = convert_3_8_to_3_7(convert_3_7_to_3_8(original))
    assert round_trip == original


def test_c3_converter_never_guesses_values():
    doc = finalize_contract(valid_document())
    converted = convert_3_7_to_3_8(doc)
    assert converted["operating_units"] == []  # empty = gap, not fabricated data


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
