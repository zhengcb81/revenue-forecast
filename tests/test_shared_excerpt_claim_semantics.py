"""A physical table excerpt can contain different facts and fiscal clocks."""
from copy import deepcopy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from revenue_core import ForecastInputError, run_forecast, text_sha256, validate_document  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def document(conclusions):
    data = forecast_document()
    excerpt = "H1 Service revenue 64,409 versus 64,847; Q2 Service revenue 32,463 versus 32,215."
    nodes = []
    for offset, (conclusion, distance) in enumerate(zip(conclusions, ("one_step", "contrary"))):
        claim_id, node_id = f"claim_signal_{offset}", f"signal_{offset}"
        data["evidence_claims"].append({"claim_id": claim_id, "source_id": "filing",
            "target_type": "growth_driver", "target_id": node_id, "support_type": "rationale_support",
            "locator": "Service segment revenue table", "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt),
            "content_sha256": data["sources"][0]["capture"]["snapshot_sha256"],
            "capture_receipt_sha256": data["sources"][0]["capture"]["receipt_sha256"],
            "verification_status": "opened_and_checked", "verified_by": "AQ fixture",
            "verified_date": data["as_of_date"]})
        nodes.append({"evidence_id": node_id, "evidence_type": "official_results_table",
            "inference_distance": distance, "conclusion": conclusion, "claim_ids": [claim_id]})
    ids = [pid for s in data["segments"] for series in
           s["scenarios"]["base"]["driver_parameter_ids"].values() for pid in series]
    data["growth_driver_tree"] = {"status": "modeled", "drivers": [{
        "driver_id": "stabilization", "title": "Recent stabilization after softness",
        "thesis": "Quarterly growth follows a weak half year; the future path remains an assumption.",
        "causal_chain": ["customer activity", "fulfilled paid service", "recognized revenue"],
        "parameter_ids": ids, "segment_attribution": [
            {"segment_name": s["name"], "weight": 1.0} for s in data["segments"]],
        "horizon": {"start_year": 2026, "end_year": 2027}, "persistence": "uncertain",
        "persistence_rationale": "Mixed historical signals do not prove future recovery.",
        "evidence_nodes": nodes, "leading_indicators": ["recognized service revenue"],
        "falsifiers": ["quarterly growth reverses"], "counterevidence_status": "found",
        "counterevidence_rationale": "The half year weakened despite quarterly improvement."}]}
    return data


def test_distinct_facts_from_shared_table_are_disclosed_not_falsely_rejected():
    data = document(["Q2 Service revenue recovered from 32,215 to 32,463.",
                     "H1 Service revenue declined from 64,847 to 64,409."])
    validated = validate_document(data)
    assert any("NOT_EVALUATED" in note for note in validated["growth_driver_tree"]["limitations"])
    result = run_forecast(deepcopy(data), mode="draft")
    assert result["growth_driver_analysis"]["drivers"][0]["evidence_status"] == "limited"
    baseline = run_forecast(forecast_document(), mode="draft")
    assert result["consolidated_forecast"] == baseline["consolidated_forecast"]


def test_same_proposition_cannot_be_relabelled_with_a_different_claim_id():
    data = document(["Q2 Service revenue recovered from 32,215 to 32,463.",
                     "  q2 Service revenue recovered from 32,215 to 32,463.  "])
    with pytest.raises(ForecastInputError, match="same excerpt"):
        validate_document(data)


def test_one_claim_cannot_be_both_evidence_nodes():
    data = document(["Q2 Service revenue recovered.", "H1 Service revenue weakened."])
    nodes = data["growth_driver_tree"]["drivers"][0]["evidence_nodes"]
    nodes[1]["claim_ids"] = nodes[0]["claim_ids"]
    with pytest.raises(ForecastInputError):
        validate_document(data)
