"""Scoped calibration binding: independent range references stay legal, actual
conversions/outputs must bind to the real native business scope and period.

RED anchors for the reproduced false-green counterexamples; positive controls
freeze the untouched legal paths (upper endpoint outside the revenue DAG,
correct conversion/output still referenced_range)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_core import validate_document  # noqa: E402
from research.evidence_roles import analyze_operating_research  # noqa: E402
from test_research_evidence_roles import calibrated_document  # noqa: E402


def conversion_observations(document):
    return [o for o in document["operating_research"]["observations"]
            if o["observation_kind"] == "conversion"]


def analyze(document):
    return analyze_operating_research(document, validate_document(document))


def test_unrelated_conversion_scope_cannot_promote_referenced_range():
    d = calibrated_document()
    for o in conversion_observations(d):
        o["scope"] = "Unrelated Business Line"
    cal = analyze(d)["calibrations"][0]
    assert cal["adequacy_status"] == "unverified"
    assert "conversion_observation_unverified_scope:conversion_low:claim_parameter_conversion_low" in cal["reasons"]
    assert "conversion_observation_unverified_scope:conversion_base:claim_parameter_conversion_base" in cal["reasons"]
    assert "conversion_observation_unverified_scope:conversion_high:claim_parameter_conversion_high" in cal["reasons"]


def test_unrelated_conversion_period_cannot_promote_referenced_range():
    d = calibrated_document()
    for o in conversion_observations(d):
        o["period"] = "FY2031"
    cal = analyze(d)["calibrations"][0]
    assert cal["adequacy_status"] == "unverified"
    assert "conversion_observation_unverified_period:conversion_low:claim_parameter_conversion_low" in cal["reasons"]
    assert "conversion_observation_unverified_period:conversion_high:claim_parameter_conversion_high" in cal["reasons"]


def test_calibration_scope_must_name_native_business_and_output_segment():
    d = calibrated_document()
    for o in d["operating_research"]["observations"]:
        if o["observation_kind"] == "quantitative_reference":
            o["scope"] = "Unrelated Product X"
    d["operating_research"]["calibrations"][0]["scope"] = "Unrelated Product X"
    cal = analyze(d)["calibrations"][0]
    assert cal["adequacy_status"] == "unverified"
    assert "calibration_scope_not_native_business:Unrelated Product X" in cal["reasons"]


def test_business_cross_borrowing_output_segment_mismatch_rejected():
    d = calibrated_document()
    d["operating_research"]["calibrations"][0]["scope"] = "Segment B"
    cal = analyze(d)["calibrations"][0]
    assert cal["adequacy_status"] == "unverified"
    assert "calibration_output_scope_mismatch:0_low_2026:Segment B->Segment A" in cal["reasons"]
    assert "calibration_output_scope_mismatch:0_high_2026:Segment B->Segment A" in cal["reasons"]


def test_valid_fixture_keeps_referenced_range_and_upper_endpoint_legal():
    d = calibrated_document()
    diag = analyze(d)
    cal = diag["calibrations"][0]
    assert cal["adequacy_status"] == "referenced_range"
    assert cal["reasons"] == []
    bindings = {o["claim_id"].replace("claim_parameter_", ""): o["binding_status"]
                for o in diag["evidence_roles"]}
    # The unused upper endpoint stays an unverified-scope independent reference;
    # that must not demote the calibration (positive control from the card).
    assert bindings["reference_upper"] == "unverified_scope"
    assert bindings["reference_lower"] == "bound"
    assert bindings["conversion_low"] == "bound"
    assert diag["magnitude_adequacy"]["supported_parameter_ids"] == ["0_base_2026", "0_high_2026", "0_low_2026"]


def test_demoted_calibration_drops_magnitude_support_per_scenario_and_year():
    d = calibrated_document()
    for o in conversion_observations(d):
        o["scope"] = "Unrelated Business Line"
    diag = analyze(d)
    assert diag["calibrations"][0]["adequacy_status"] == "unverified"
    assert diag["magnitude_adequacy"]["supported_parameter_ids"] == []
    assert diag["magnitude_adequacy"]["unverified_parameter_ids"]
    # One supported driver-year never supports later years, other segments or
    # the whole company (frozen invariant from the card §3).
    d2 = analyze(calibrated_document())
    magnitude = set(d2["magnitude_adequacy"]["supported_parameter_ids"])
    assert magnitude == {"0_low_2026", "0_base_2026", "0_high_2026"}
    unverified = set(d2["magnitude_adequacy"]["unverified_parameter_ids"])
    assert {"0_low_2027", "0_base_2027", "0_high_2027"} <= unverified
    assert {"1_low_2026", "1_base_2026", "1_high_2026"} <= unverified


def test_stress_and_unverified_statuses_unchanged_by_binding_rules():
    d = calibrated_document()
    d["operating_research"]["calibrations"][0]["status"] = "stress"
    cal = analyze(d)["calibrations"][0]
    assert cal["adequacy_status"] == "stress"


def test_tampered_diagnostic_cannot_bypass_strong_recompute():
    from revenue_core import run_forecast, ForecastInputError
    from revenue_report import validate_published_forecast
    d = calibrated_document()
    for o in conversion_observations(d):
        o["scope"] = "Unrelated Business Line"
    result = run_forecast(d)
    calibration = result["confidence"]["research_adequacy"]["calibrations"][0]
    assert calibration["adequacy_status"] == "unverified"
    # Rewriting the emitted diagnostic alone cannot pass publication recompute.
    result["confidence"]["research_adequacy"]["calibrations"][0]["adequacy_status"] = "referenced_range"
    with pytest.raises(ForecastInputError, match="research adequacy"):
        validate_published_forecast(result, d)
