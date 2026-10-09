"""F1-F4 acceptance regressions over actual native ancestry and measurements."""
from copy import deepcopy
from pathlib import Path
import sys
import pytest
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/"scripts"),str(Path(__file__).resolve().parent)]
from revenue_core import ForecastInputError,run_forecast  # noqa: E402
from revenue_report import validate_published_forecast  # noqa: E402
from test_target_measurement_comparison import quarter_document,yoy_document  # noqa: E402
from test_research_evidence_roles import research_document  # noqa: E402
from test_recognition_bridge import add_parameter  # noqa: E402


def checked(data):
    result=run_forecast(data)
    validate_published_forecast(result,data)
    return result


def test_quarter_cannot_take_another_segments_native_bridge():
    data=quarter_document()
    data["management_targets"][0]["scope"]["name"]="Segment B"
    with pytest.raises(ForecastInputError,match="quarter.*scope"):
        checked(data)


def test_quarter_scope_accepts_same_segment_actual_derived_ancestry():
    result=checked(quarter_document())
    assert result["management_target_coverage"]["targets"][0]["scenario_comparison"]["base"]["modeled_value"]==108000


def company_quarters():
    d=quarter_document()
    target=deepcopy(d["management_targets"][0])
    saved=[deepcopy(c) for c in d["evidence_claims"] if c["claim_id"] in target["claim_ids"]+target["benchmark_claim_ids"]]
    for scenario,value in (("low",10),("base",11),("high",12)):
        pid=add_parameter(d,"b_quarter_"+scenario,value,2026,scenario)
        next(p for p in d["parameters"] if p["parameter_id"]==pid)["measurement_period"]="FY2026Q3"
        annual_id=d["segments"][1]["scenarios"][scenario]["driver_parameter_ids"]["revenue"][0]
        annual=next(p for p in d["parameters"] if p["parameter_id"]==annual_id)
        annual.update(kind="derived_fact",formula="x0+40",input_parameter_ids=[pid],value=value+40)
        target["comparison_basis"]["scenario_parameter_ids"][scenario].append(pid)
    d["management_targets"]=[target]
    d["evidence_claims"].extend(saved)
    target["scope"]={"type":"company","name":d["company_name"]}
    return d


def test_company_quarter_has_actual_native_composition():
    d=company_quarters()
    result=checked(d)
    assert result["management_target_coverage"]["targets"][0]["scenario_comparison"]["base"]["modeled_value"]==108011
    d["management_targets"][0]["comparison_basis"]["scenario_parameter_ids"]["base"].pop()
    with pytest.raises(ForecastInputError,match="quarter.*scope"):
        checked(d)


def test_mechanism_cannot_retarget_an_unbound_business_high_parameter():
    d,_,_=research_document()
    pid=d["segments"][1]["scenarios"]["high"]["driver_parameter_ids"]["revenue"][1]
    d["operating_research"]["observations"][0].update(parameter_ids=[pid],scope="Segment B",period="FY2027")
    with pytest.raises(ForecastInputError,match="observation.*binding"):
        checked(d)


def test_mechanism_allows_actual_cross_year_derivation_not_an_arbitrary_period():
    d,original,_=research_document()
    pid=d["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][1]
    p=next(p for p in d["parameters"] if p["parameter_id"]==pid)
    p.update(kind="derived_fact",formula="x0*1.1",input_parameter_ids=[original])
    d["operating_research"]["observations"][0].update(parameter_ids=[pid],period="FY2027")
    result=checked(d)
    assert result["confidence"]["research_adequacy"]["mechanism_adequacy"]["supported_parameter_ids"]==[pid]
    d["operating_research"]["observations"][0]["period"]="FY2028"
    with pytest.raises(ForecastInputError,match="observation.*period"):
        checked(d)


def test_unknown_product_scope_cannot_be_promoted_to_structural_mechanism_support():
    d,_,_=research_document()
    d["operating_research"]["observations"][0]["scope"]="unmodeled product perimeter"
    result=checked(d)
    observation=result["confidence"]["research_adequacy"]["evidence_roles"][0]
    assert result["confidence"]["research_adequacy"]["mechanism_adequacy"]["supported_parameter_ids"]==[]
    assert observation["binding_status"]=="unverified_scope"


@pytest.mark.parametrize(("field","value"),[("unit","EUR billion"),("period","FY2030"),("currency","EUR"),("scale","million"),("measurement_period","FY2026Q4")])
def test_numeric_range_keeps_source_measurement_binding(field,value):
    d=quarter_document()
    t=d["management_targets"][0]
    next(c for c in d["evidence_claims"] if c["claim_id"] in t["claim_ids"])[field]=value
    with pytest.raises(ForecastInputError,match="target claim.*mismatch"):
        checked(d)


def test_numeric_range_true_raw_to_comparison_units_remain_legal():
    result=checked(quarter_document())
    row=result["management_target_coverage"]["targets"][0]["scenario_comparison"]["base"]
    assert row["unit"]=="USD million"
    assert row["target_low"]==pytest.approx(105840) and row["target_high"]==pytest.approx(110160)


@pytest.mark.parametrize("metric",["year_over_year_growth","annual_revenue_level"])
def test_typed_and_legacy_annual_measurement_periods_cannot_disagree(metric):
    d=yoy_document()
    t=d["management_targets"][0]
    if metric=="annual_revenue_level":
        t.update(raw_target_value=70,raw_unit="USD million",raw_currency="USD",raw_scale="million",comparison_value=70)
        t["comparison_basis"]={"schema_version":"management-target-comparison/1","metric_kind":metric,"period":"FY2027"}
        next(c for c in d["evidence_claims"] if c["claim_id"] in t["claim_ids"]).update(unit="USD million")
    checked(d)
    t["measurement_periods"]=["FY2026"]
    with pytest.raises(ForecastInputError,match="typed.*measurement period"):
        checked(d)


def test_growth_driver_mechanism_uses_its_actual_evidence_node_binding():
    from test_recognition_bridge import forecast_document
    d=forecast_document()
    driver=d["growth_driver_tree"]["drivers"][0]
    node=driver["evidence_nodes"][0]
    claim=next(c for c in d["evidence_claims"] if c["claim_id"] in node["claim_ids"])
    claim["evidence_role"]="mechanism_direction"
    pid=d["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][-1]
    d["operating_research"]={"schema_version":"operating-research/1","inventory":[],"calibrations":[],
        "observations":[{"claim_id":claim["claim_id"],"observation_kind":"operating_mechanism","scope":"Segment A","period":"FY2027",
            "parameter_ids":[pid],"driver_ids":[driver["driver_id"]],"rationale":"The checked node belongs to the existing actual causal driver."}]}
    result=checked(d)
    assert result["confidence"]["research_adequacy"]["mechanism_adequacy"]["supported_parameter_ids"]==[pid]


def test_numeric_range_with_unknown_source_unit_or_period_stays_explicit_gap():
    d=quarter_document()
    t=d["management_targets"][0]
    t.update(treatment="unmodeled_data_gap",mapped_parameter_ids=[],mapped_scenarios=[])
    t["comparison_basis"]["scenario_parameter_ids"]=None
    claim=next(c for c in d["evidence_claims"] if c["claim_id"] in t["claim_ids"])
    claim.pop("unit")
    claim.pop("period")
    result=checked(d)
    assert result["management_target_coverage"]["targets"][0]["scenario_comparison"]=={}
    assert any("unmodeled_data_gap" in gap for gap in result["data_gaps"])


def test_range_raw_unit_cannot_contradict_currency_scale_used_for_conversion():
    d=quarter_document()
    t=d["management_targets"][0]
    t["raw_unit"]="EUR billion"
    next(c for c in d["evidence_claims"] if c["claim_id"] in t["claim_ids"])["unit"]="EUR billion"
    with pytest.raises(ForecastInputError,match="typed target raw unit"):
        checked(d)
