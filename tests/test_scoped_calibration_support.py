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


def synchronized_conversion_period(document, period):
    """Change the parameter applicability and its declared links together."""
    ids = {o["parameter_ids"][0] for o in conversion_observations(document)}
    for parameter in document["parameters"]:
        if parameter["parameter_id"] in ids:
            parameter["period"] = period
    for claim in document["evidence_claims"]:
        if claim["target_id"] in ids:
            claim["period"] = period
    for observation in conversion_observations(document):
        observation["period"] = period


@pytest.mark.parametrize("period", ["FY2027", "FY2031"])
def test_synchronized_conversion_period_does_not_calibrate_fy2026(period):
    d = calibrated_document()
    synchronized_conversion_period(d, period)
    diag = analyze(d)
    # Each observation is internally bound; applicability to its real output
    # must still be checked independently, without rejecting the document.
    assert all(o["binding_status"] == "bound" for o in diag["evidence_roles"]
               if o["observation_kind"] == "conversion")
    cal = diag["calibrations"][0]
    assert cal["adequacy_status"] == "unverified"
    for scenario in ("low", "base", "high"):
        assert (f"conversion_output_period_mismatch:conversion_{scenario}:{period}:"
                f"0_{scenario}_2026:FY2026:claim_parameter_conversion_{scenario}") in cal["reasons"]
    assert diag["magnitude_adequacy"]["supported_parameter_ids"] == []


def test_output_period_must_match_its_actual_direct_revenue_cell():
    d = calibrated_document()
    synchronized_conversion_period(d, "FY2031")
    outputs = set(d["operating_research"]["calibrations"][0]["scenario_output_parameter_ids"].values())
    for parameter in d["parameters"]:
        if parameter["parameter_id"] in outputs:
            parameter["period"] = "FY2031"
    for claim in d["evidence_claims"]:
        if claim["target_id"] in outputs:
            claim["period"] = "FY2031"
    cal = analyze(d)["calibrations"][0]
    assert cal["adequacy_status"] == "unverified"
    for scenario in ("low", "base", "high"):
        assert (f"calibration_output_consumption_period_mismatch:0_{scenario}_2026:"
                f"FY2031:Segment A:{scenario}:FY2026") in cal["reasons"]


def test_old_claim_disclosure_period_is_not_a_conversion_applicability_gate():
    d = calibrated_document()
    for claim in d["evidence_claims"]:
        if claim["target_id"].startswith("conversion_"):
            claim["period"] = "FY2025"
    cal = analyze(d)["calibrations"][0]
    assert cal["adequacy_status"] == "referenced_range"
    assert cal["reasons"] == []


def target_period_bridge_document():
    """Reuse a historical assumption through an explicit target-period DAG node.

    The old claim retains FY2025; its observation names a real downstream
    derived conversion for FY2026, rather than rewriting source provenance.
    """
    from copy import deepcopy
    d = calibrated_document()
    synchronized_conversion_period(d, "FY2025")
    parameters = {p["parameter_id"]: p for p in d["parameters"]}
    calibration = d["operating_research"]["calibrations"][0]
    for observation in conversion_observations(d):
        source_id = observation["parameter_ids"][0]
        scenario = parameters[source_id]["scenario"]
        target_id = source_id + "_for_2026"
        target = deepcopy(parameters[source_id])
        target.update(parameter_id=target_id, kind="derived_fact", period="FY2026",
                      definition="Explicit FY2026 bridge: " + source_id,
                      formula="x0", input_parameter_ids=[source_id],
                      source_ids=[], claim_ids=[])
        d["parameters"].append(target)
        calibration["scenario_input_parameter_ids"][scenario][1] = target_id
        output_id = calibration["scenario_output_parameter_ids"][scenario]
        parameters[output_id]["input_parameter_ids"][1] = target_id
        observation.update(parameter_ids=[target_id], period="FY2026")
    return d


def test_explicit_native_target_period_bridge_keeps_historical_provenance():
    from revenue_core import run_forecast
    d = target_period_bridge_document()
    diag = analyze(d)
    cal = diag["calibrations"][0]
    assert cal["adequacy_status"] == "referenced_range"
    assert cal["reasons"] == []
    for scenario in ("low", "base", "high"):
        assert cal["scenario_conversion"][scenario]["input_parameter_ids"][1] == f"conversion_{scenario}_for_2026"
        claim = next(c for c in d["evidence_claims"] if c["target_id"] == f"conversion_{scenario}")
        assert claim["period"] == "FY2025"
    assert run_forecast(d)["consolidated_forecast"] == run_forecast(calibrated_document())["consolidated_forecast"]


def test_applicability_diagnostic_does_not_change_arithmetic_or_legacy_optional_behavior():
    from revenue_core import run_forecast
    valid = calibrated_document()
    bad = calibrated_document()
    synchronized_conversion_period(bad, "FY2031")
    original = run_forecast(valid)
    updated = run_forecast(bad)
    assert updated["confidence"]["research_adequacy"]["calibrations"][0]["adequacy_status"] == "unverified"
    assert updated["consolidated_forecast"] == original["consolidated_forecast"]
    assert updated["confidence"]["score"] == original["confidence"]["score"]
    assert updated["confidence"]["components"] == original["confidence"]["components"]
    valid.pop("operating_research")
    assert analyze(valid) is None
