"""Confidence score units are origins/roles, not quote multiplicity."""
from copy import deepcopy
from datetime import date
from pathlib import Path
import math
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "tests")]
from analysis import confidence as model  # noqa: E402
from contracts.document import validate_sources  # noqa: E402
from contracts.evidence import ForecastInputError  # noqa: E402


def scoring_case(roles=("exact_value", "rationale_support")):
    data = {"forecast_years": [2027], "segments": [{"name": "Neutral", "recognition": {},
        "scenarios": {"base": {"model": "unit_sales", "driver_parameter_ids": {"units": ["p"]}}}}]}
    claims = {key: {"claim_id": key, "source_id": key, "support_type": role,
        "excerpt": "Independent observation " + key, "verified_date": "2026-10-01"}
        for key, role in zip(("a", "b"), roles)}
    sources = {key: {"source_id": key, "published_date": published,
        "capture": {"snapshot_sha256": key * 64}}
        for key, published in (("a", "2026-01-01"), ("b", "2026-10-01"))}
    valid = {"parameter_index": {"p": {"claim_ids": ["a", "b"]}}, "claim_index": claims,
        "source_index": sources, "as_of_date": date(2026, 10, 30),
        "research_coverage": {"counts": {"data_gap": 0}}}
    result = {"segments": [{"name": "Neutral", "scenarios": {"base": {
        "model": "unit_sales", "recognized_revenue": {"2027": 100.0}}}}],
        "consolidated_forecast": {"base": {"adjustment_bridge": []}}}
    return data, valid, result, []


def added(case, base="a", *, source=None, role=None):
    case = deepcopy(case)
    valid = case[1]
    claim = dict(valid["claim_index"][base], claim_id="added", excerpt="Another measurement")
    if source is not None:
        valid["source_index"][source["source_id"]] = source
        claim["source_id"] = source["source_id"]
    if role is not None:
        claim["support_type"] = role
    valid["claim_index"]["added"] = claim
    valid["parameter_index"]["p"]["claim_ids"].append("added")
    return case


@pytest.mark.parametrize("base", ["a", "b"])
def test_more_quotes_or_measurements_same_origin_role_do_not_change_score(base):
    before = scoring_case()
    after = added(before, base)
    frozen = deepcopy(after)
    assert model.calculate_confidence(*before) == model.calculate_confidence(*after)
    assert after == frozen  # score reduction must never delete source measurements
    assert len(after[1]["claim_index"]) == 3


def test_same_sha_alias_same_role_adds_no_vote():
    before = scoring_case()
    alias = dict(before[1]["source_index"]["a"], source_id="alias")
    assert model.calculate_confidence(*before) == model.calculate_confidence(*added(before, source=alias))


def test_genuine_new_capture_has_a_freshness_and_quality_vote():
    before = scoring_case()
    new = {"source_id": "independent", "published_date": "2026-10-01",
        "capture": {"snapshot_sha256": "c" * 64}}
    a = model.calculate_confidence(*before)["components"]
    b = model.calculate_confidence(*added(before, source=new))["components"]
    assert a["source_freshness"] < b["source_freshness"]
    assert a["verified_claim_quality"] < b["verified_claim_quality"]


def test_new_role_same_capture_changes_quality_only():
    before = scoring_case()
    a = model.calculate_confidence(*before)["components"]
    after = added(before, "a", role="rationale_support")
    b = model.calculate_confidence(*after)["components"]
    assert b["verified_claim_quality"] < a["verified_claim_quality"]
    assert b["source_freshness"] == a["source_freshness"]
    assert model.calculate_confidence(*added(after, "added")) == model.calculate_confidence(*after)


@pytest.mark.parametrize("alias_date", ["2026-10-01", None])
def test_alias_newer_or_unknown_date_never_erases_old_known_date(alias_date):
    before = scoring_case()
    alias = dict(before[1]["source_index"]["a"], source_id="alias", published_date=alias_date)
    a = model.calculate_confidence(*before)
    b = model.calculate_confidence(*added(before, source=alias))
    assert b["components"] == a["components"]
    if alias_date is not None:
        assert any("conflicting publication" in item for item in b["limitations"])


def test_alias_conflict_uses_earliest_publication_in_any_order():
    before = scoring_case()
    alias = dict(before[1]["source_index"]["b"], source_id="alias", published_date="2023-01-01")
    after = added(before, "b", source=alias)
    score = model.calculate_confidence(*after)
    assert score["components"]["source_freshness"] == 5.0  # (.8 + .2) / 2 * 10
    after[1]["parameter_index"]["p"]["claim_ids"].reverse()
    assert model.calculate_confidence(*after) == score


def test_no_capture_legacy_sources_remain_distinct_by_source_id():
    before = scoring_case()
    for source in before[1]["source_index"].values():
        source.pop("capture")
    assert model.calculate_confidence(*before)["components"]["source_freshness"] == 9.0
    assert model.calculate_confidence(*before) == model.calculate_confidence(*added(before))


def test_legal_m1_unknown_publication_is_zero_not_availability_freshness():
    from test_source_provenance import AS_OF, local_record
    source = local_record(unknown=True)
    frozen = deepcopy(source)
    source_index = validate_sources({"sources": [source]}, AS_OF, require_capture=True)
    case = scoring_case()
    valid = case[1]
    valid["source_index"] = source_index
    valid["as_of_date"] = AS_OF
    valid["claim_index"] = {"n": {"source_id": source["source_id"], "support_type": "rationale_support"}}
    valid["parameter_index"]["p"]["claim_ids"] = ["n"]
    score = model.calculate_confidence(*case)
    assert score["components"]["source_freshness"] == 0
    assert any("unknown publication" in item for item in score["limitations"])
    assert source == frozen and source["published_date"] is None


def test_checked_date_does_not_change_publication_score():
    before = scoring_case()
    after = deepcopy(before)
    for claim in after[1]["claim_index"].values():
        claim["verified_date"] = "2026-10-29"
    assert model.calculate_confidence(*before) == model.calculate_confidence(*after)


def test_new_revision_and_old_exact_algorithm_coexist():
    before = scoring_case()
    after = added(before)
    assert model.calculate_confidence(*before)["calculation_version"] == "source-evidence/2"
    old = model.calculate_confidence(*before, calculation_version="stable-fsum/1")
    old_dup = model.calculate_confidence(*after, calculation_version="stable-fsum/1")
    assert old["components"]["verified_claim_quality"] == 17
    assert old_dup["components"]["verified_claim_quality"] == 18
    assert old_dup["components"]["source_freshness"] == 8.666666666666668
    model.validate_confidence_recomputation(old, old)
    legacy = deepcopy(old)
    legacy.pop("calculation_version")
    model.validate_confidence_recomputation(old, legacy)
    with pytest.raises(ForecastInputError, match="calculation version"):
        model.validate_confidence_recomputation(model.calculate_confidence(*before), legacy)


@pytest.mark.parametrize("version", [None, "", "future/3", [], {}])
def test_invalid_revision_is_not_default_or_legacy(version):
    with pytest.raises(ForecastInputError, match="calculation version"):
        model.calculate_confidence(*scoring_case(), calculation_version=version)


@pytest.mark.parametrize("marked", [False, True])
def test_formal_strong_replay_dispatches_old_revision_and_rejects_tamper(marked, monkeypatch):
    import revenue_core
    from revenue_core import run_forecast
    from revenue_report import validate_published_forecast
    from test_recognition_bridge import forecast_document
    data = forecast_document()
    def historical_calculation(*args):
        value = model.calculate_confidence(*args, calculation_version="stable-fsum/1")
        if not marked:
            value.pop("calculation_version")
        return value
    # Historical emitter computes the old revision BEFORE its native receipt.
    # Do not forge a refreshed hash for a changed published payload.
    monkeypatch.setattr(revenue_core, "calculate_confidence", historical_calculation)
    result = run_forecast(data)
    validate_published_forecast(result, data)
    result["confidence"]["components"]["source_freshness"] += .001
    result["confidence"]["score"] = math.fsum(result["confidence"]["components"].values())
    with pytest.raises(ForecastInputError, match="components recomputation mismatch"):
        validate_published_forecast(result, data)


@pytest.mark.parametrize("version", [None, "invented", [], {}])
def test_formal_strong_replay_rejects_invalid_revision(version):
    from revenue_core import run_forecast
    from revenue_report import validate_published_forecast
    from test_recognition_bridge import forecast_document
    data = forecast_document()
    result = run_forecast(data)
    result["confidence"]["calculation_version"] = version
    with pytest.raises(ForecastInputError, match="calculation version"):
        validate_published_forecast(result, data)


@pytest.mark.parametrize("version", ["stable-fsum/1", "source-evidence/2"])
def test_each_marked_revision_rejects_even_one_ulp_of_tampering(version):
    value = model.calculate_confidence(*scoring_case(), calculation_version=version)
    altered = deepcopy(value)
    key = "verified_claim_quality"
    altered["components"][key] = math.nextafter(altered["components"][key], math.inf)
    with pytest.raises(ForecastInputError, match="components recomputation mismatch"):
        model.validate_confidence_recomputation(value, altered)
