"""Reviewed explanations follow native evidence scope and scenario; no model inference."""
from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from research.authoring_projection import reconcile_authoring_explanations


def neutral_document(role="history_base"):
    return {
        "company_name": "Neutral services",
        "evidence_claims": [{"claim_id": "context", "evidence_role": role}],
        "parameters": [
            {"parameter_id": f"parent_{scenario}", "scenario": scenario,
             "period": "FY2031", "unit": "GBP million", "value": value}
            for scenario, value in (("low", 120), ("base", 150), ("high", 210))
        ] + [
            {"parameter_id": f"activity_{scenario}", "scenario": scenario,
             "period": "FY2031", "unit": "ratio", "value": value,
             "rationale": "Copied first-scenario operating requirement."}
            for scenario, value in (("low", 1.1), ("base", 1.4), ("high", 1.8))
        ],
        "growth_driver_tree": {"drivers": [{
            "driver_id": "legacy", "title": "Disclosed ramp",
            "thesis": "Disclosed projects support future operating growth.",
            "causal_chain": ["new projects", "recognized sales"],
            "leading_indicators": ["new projects"], "falsifiers": ["ramp fails"],
            "persistence_rationale": "A disclosed multi-year mechanism.",
            "segment_attribution": [{"segment_name": "Legacy support", "weight": 1}],
            "evidence_nodes": [{"evidence_id": "historical", "claim_ids": ["context"],
                "evidence_type": "issuer_current_operating_update", "inference_distance": "one_step",
                "conclusion": "Current workload establishes an operating direction."}],
        }]},
        "operating_research": {"calibrations": [
            {"scope": "Legacy support", "limitations": ["Foreign product cohort."],
             "status": "unverified", "observed_range": None},
            {"scope": "Subscriptions", "limitations": ["Foreign product cohort."],
             "status": "unverified", "observed_range": None},
            {"scope": "Unrelated", "limitations": ["Its own unknown."],
             "status": "unverified", "observed_range": None},
        ]},
    }


def neutral_plan():
    return {
        "historical_driver_contexts": {"legacy": {
            "historical_context": "Only a historical decline is disclosed.",
            "forward_condition": "Revenue is a conditional runoff estimate.",
            "leading_indicators": ["a newly disclosed continuing contract"],
            "falsifiers": ["new continuing revenue changes the perimeter"],
        }},
        "calibration_limitations": {
            "Legacy support": ["No disclosed renewal/runoff cohort."],
            "Subscriptions": ["No observed subscription-retention distribution."],
        },
        "scenario_bridges": [{
            "explanation_parameter_id": f"activity_{scenario}",
            "parent_parameter_id": f"parent_{scenario}",
            "scenario": scenario, "period": "FY2031", "period_label": "Q3 FY2031",
            "scope": "Subscriptions", "component_name": "Recurring subscription",
            "residual_amount": "30", "prior_component_amount": "100",
            "unit": "GBP million", "condition": "services stays at the comparable level",
        } for scenario in ("low", "base", "high")],
    }


def test_historical_role_updates_all_driver_explanations_without_touching_amounts():
    source = neutral_document()
    result = reconcile_authoring_explanations(source, neutral_plan())
    driver = result["growth_driver_tree"]["drivers"][0]
    assert "historical" in driver["thesis"].lower()
    assert "no disclosed forward mechanism" in driver["thesis"].lower()
    assert driver["evidence_nodes"][0]["evidence_type"] == "issuer_historical_context"
    assert driver["evidence_nodes"][0]["inference_distance"] == "direct"
    assert "historical" in driver["evidence_nodes"][0]["conclusion"].lower()
    assert driver["causal_chain"] != source["growth_driver_tree"]["drivers"][0]["causal_chain"]
    assert driver["leading_indicators"] == ["a newly disclosed continuing contract"]
    assert driver["falsifiers"] == ["new continuing revenue changes the perimeter"]
    assert [p["value"] for p in result["parameters"]] == [p["value"] for p in source["parameters"]]


def test_genuine_mechanism_is_not_downgraded_by_a_history_plan_entry():
    source = neutral_document("mechanism_direction")
    result = reconcile_authoring_explanations(source, neutral_plan())
    assert result["growth_driver_tree"] == source["growth_driver_tree"]


def test_mixed_evidence_does_not_erase_a_real_forward_mechanism():
    source = neutral_document()
    source["evidence_claims"].append({"claim_id": "actual_mechanism", "evidence_role": "mechanism_direction"})
    source["growth_driver_tree"]["drivers"][0]["evidence_nodes"][0]["claim_ids"].append("actual_mechanism")
    result = reconcile_authoring_explanations(source, neutral_plan())
    assert result["growth_driver_tree"] == source["growth_driver_tree"]


def test_scope_specific_calibration_notes_do_not_cross_businesses():
    source = neutral_document()
    result = reconcile_authoring_explanations(source, neutral_plan())
    notes = {row["scope"]: row["limitations"] for row in result["operating_research"]["calibrations"]}
    assert notes["Legacy support"] == ["No disclosed renewal/runoff cohort."]
    assert notes["Subscriptions"] == ["No observed subscription-retention distribution."]
    assert notes["Unrelated"] == ["Its own unknown."]
    assert all(row["status"] == "unverified" and row["observed_range"] is None
               for row in result["operating_research"]["calibrations"])


@pytest.mark.parametrize("scenario,expected", [("low", "-10.00%"), ("base", "20.00%"), ("high", "80.00%")])
def test_each_scenario_uses_its_own_parent_amount_and_named_condition(scenario, expected):
    result = reconcile_authoring_explanations(neutral_document(), neutral_plan())
    parameter = next(p for p in result["parameters"] if p["parameter_id"] == f"activity_{scenario}")
    text = parameter["rationale"]
    assert expected in text
    assert scenario in text and "Q3 FY2031" in text
    assert "services stays at the comparable level" in text
    assert "GBP million" in text
    assert "not an observed rate" in text


def test_zero_comparable_component_stays_unknown_instead_of_inventing_a_rate():
    plan = neutral_plan()
    plan["scenario_bridges"][0]["prior_component_amount"] = "0"
    result = reconcile_authoring_explanations(neutral_document(), plan)
    text = next(p for p in result["parameters"] if p["parameter_id"] == "activity_low")["rationale"]
    assert "not defined" in text
    assert "0.00%" not in text


def test_input_claims_structure_and_external_plan_are_immutable():
    document, plan = neutral_document(), neutral_plan()
    old_document, old_plan = deepcopy(document), deepcopy(plan)
    result = reconcile_authoring_explanations(document, plan)
    assert document == old_document and plan == old_plan
    assert result["evidence_claims"] == document["evidence_claims"]
    assert set(result) == set(document)
    assert reconcile_authoring_explanations(result, plan) == result


def test_currency_or_scenario_mismatch_is_a_data_error_not_a_conversion_guess():
    plan = neutral_plan()
    plan["scenario_bridges"][0]["unit"] = "EUR million"
    with pytest.raises(ValueError, match="unit"):
        reconcile_authoring_explanations(neutral_document(), plan)
    plan = neutral_plan()
    plan["scenario_bridges"][0]["scenario"] = "high"
    with pytest.raises(ValueError, match="scenario"):
        reconcile_authoring_explanations(neutral_document(), plan)
