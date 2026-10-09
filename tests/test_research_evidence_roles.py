"""Explicit role/period/calibration counterexamples; no English plausibility judge."""
from __future__ import annotations
from copy import deepcopy
import importlib
import json
from pathlib import Path
import pytest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from revenue_core import ForecastInputError, run_forecast, validate_document, text_sha256
from revenue_report import validate_published_forecast, render_markdown
from test_recognition_bridge import forecast_document, add_parameter


def module():
    try:
        return importlib.import_module("research.evidence_roles")
    except ModuleNotFoundError:
        pytest.fail("typed operating inventory and calibration projection missing")


def research_document():
    d=forecast_document()
    pid=d["segments"][0]["scenarios"]["base"]["driver_parameter_ids"]["revenue"][0]
    c=next(c for c in d["evidence_claims"] if c["target_id"]==pid)
    c["evidence_role"]="mechanism_direction"
    d["operating_research"]={"schema_version":"operating-research/1",
        "inventory":[{"item_id":"ramp", "topic":"new_product_ramp", "disposition":"modeled",
            "rationale":"Synthetic operating mechanism, not a real calibrated forecast.",
            "claim_ids":[c["claim_id"]],"parameter_ids":[pid],"driver_ids":[],
            "recognition_note":"Customer acceptance in FY2026", "included_in":None}],
        "observations":[{"claim_id":c["claim_id"],"observation_kind":"operating_mechanism",
            "scope":"Segment A","period":"FY2026","parameter_ids":[pid],"driver_ids":[],
            "rationale":"Mechanism direction only; range is unknown."}], "calibrations":[]}
    return d,pid,c


@pytest.mark.parametrize("fixture",["aster-en","hengwei-zh"])
def test_declared_history_header_and_pc_weakness_cannot_be_positive_mechanism(fixture):
    facts=json.loads((Path(__file__).parent/"fixtures/research_evidence_roles"/(fixture+".json")).read_text(encoding="utf-8"))
    d,pid,c=research_document()
    c["excerpt"]=facts["history_excerpt"]
    c["excerpt_sha256"]=text_sha256(c["excerpt"])
    o=d["operating_research"]["observations"][0]
    o["observation_kind"]="historical_revenue_table"
    with pytest.raises(ForecastInputError,match="observation.*role"):
        module().analyze_operating_research(d,validate_document(d))
    c["excerpt"]=facts["weakness_excerpt"]
    c["excerpt_sha256"]=text_sha256(c["excerpt"])
    o["observation_kind"]="weak_demand"
    with pytest.raises(ForecastInputError,match="observation.*role"):
        module().analyze_operating_research(d,validate_document(d))
    c["evidence_role"]="counterevidence"
    # Counterevidence is a related research observation, never a positive numeric support link.
    p=next(p for p in d["parameters"] if p["parameter_id"]==pid)
    p["claim_ids"].remove(c["claim_id"])
    p["source_ids"]=[]
    c["target_type"]="growth_driver"
    c["target_id"]="ramp_risk"
    diag=module().analyze_operating_research(d,validate_document(d))
    assert diag["evidence_roles"][0]["role"]=="counterevidence"
    assert diag["mechanism_adequacy"]["supported_parameter_ids"]==[]


def test_optional_diagnostic_separates_documentary_presence_and_unknown_magnitude():
    d,pid,c=research_document()
    module()
    result=run_forecast(d)
    diag=result["confidence"]["research_adequacy"]
    assert diag["documentary_presence"]["checked_claim_count"]>0
    assert diag["mechanism_adequacy"]["supported_parameter_ids"]==[pid]
    assert diag["magnitude_adequacy"]["supported_parameter_ids"]==[]
    assert pid in diag["magnitude_adequacy"]["unverified_parameter_ids"]
    old=deepcopy(d)
    del old["operating_research"]
    old_result=run_forecast(old)
    assert result["confidence"]["score"]==old_result["confidence"]["score"]
    assert result["confidence"]["components"]==old_result["confidence"]["components"]
    assert result["confidence"]["calculation_version"]=="stable-fsum/1"
    validate_published_forecast(result,d)
    report=render_markdown(result)
    assert "量级" in report and "new_product_ramp" in report and "unknown" in report
    result["confidence"]["research_adequacy"]["magnitude_adequacy"]["supported_parameter_ids"]=[pid]
    with pytest.raises(ForecastInputError,match="research adequacy"):
        validate_published_forecast(result,d)


def test_inventory_included_items_do_not_become_additional_revenue():
    d,pid,c=research_document()
    item=deepcopy(d["operating_research"]["inventory"][0])
    item.update(item_id="processor", disposition="included", included_in="ramp")
    d["operating_research"]["inventory"].append(item)
    diag=module().analyze_operating_research(d,validate_document(d))
    assert diag["inventory"][1]["included_in"]=="ramp"
    before=run_forecast(forecast_document())
    after=run_forecast(d)
    assert after["consolidated_forecast"]==before["consolidated_forecast"]
    item["included_in"]="processor"
    with pytest.raises(ForecastInputError,match="inclusion"):
        module().analyze_operating_research(d,validate_document(d))


def test_template_does_not_default_future_evidence_to_mechanism():
    import generate_input_template as gen
    d=gen.build_template("X",2025,[2026,2027],"USD","million",["Core"])
    pids={p["parameter_id"] for p in d["parameters"] if p["kind"]=="analyst_assumption"}
    claims=[c for c in d["evidence_claims"] if c["target_id"] in pids]
    assert claims and all(c.get("evidence_role") is None for c in claims)
    assert all(c.get("research_role_status")=="unclassified" for c in claims)
    assert all(c.get("evidence_role")=="history_base" for c in d["evidence_claims"] if c["target_type"]=="historical_revenue")


def calibrated_document():
    from test_data_contract import finalize_contract
    d=forecast_document()
    lower=add_parameter(d,"reference_lower",100,2025,"all")
    upper=add_parameter(d,"reference_upper",120,2025,"all")
    for p in d["parameters"]:
        if p["parameter_id"] in (lower,upper):
            p["kind"]="reported_fact"
    inputs={}
    outputs={}
    factor_ids=[]
    for scenario,factor in (("low",1.0),("base",1.1),("high",1.2)):
        fid=add_parameter(d,"conversion_"+scenario,factor,2026,scenario,dimension="ratio")
        factor_ids.append(fid)
        next(p for p in d["parameters"] if p["parameter_id"]==fid)["unit"]="ratio"
        pid=d["segments"][0]["scenarios"][scenario]["driver_parameter_ids"]["revenue"][0]
        p=next(p for p in d["parameters"] if p["parameter_id"]==pid)
        p.update(kind="derived_fact",formula="x0*x1",input_parameter_ids=[lower,fid])
        inputs[scenario]=[lower,fid]
        outputs[scenario]=pid
    finalize_contract(d)
    observations=[]
    for p in d["parameters"]:
        if p["parameter_id"] in [lower,upper]+factor_ids:
            c=next(c for c in d["evidence_claims"] if c["target_id"]==p["parameter_id"])
            c["evidence_role"]="value_range" if p["parameter_id"] in (lower,upper) else "conversion_assumption"
            observations.append({"claim_id":c["claim_id"],"observation_kind":"quantitative_reference" if p["parameter_id"] in (lower,upper) else "conversion",
                "scope":"Segment A","period":p["period"],"parameter_ids":[p["parameter_id"]],"driver_ids":[],"rationale":"Synthetic scoped range/conversion."})
    d["operating_research"]={"schema_version":"operating-research/1","inventory":[],"observations":observations,
        "calibrations":[{"calibration_id":"reference_bridge","status":"calibrated","scope":"Segment A","observed_period":"FY2025",
            "source_claim_ids":["claim_parameter_"+lower,"claim_parameter_"+upper],"counterevidence_claim_ids":[],
            "observed_range":{"lower":100,"upper":120,"unit":"USD million"},"conversion_formula":"x0*x1","output_unit":"USD million",
            "scenario_input_parameter_ids":inputs,"scenario_output_parameter_ids":outputs,
            "rationale":"Observed comparable range then disclosed conversion, not management promise.","limitations":["Engineering fixture only; no empirical probability calibration."]}]}
    return d


def test_calibration_recomputes_existing_formula_units_and_keeps_unknown_null():
    d=calibrated_document()
    result=run_forecast(d)
    diag=result["confidence"]["research_adequacy"]
    c=diag["calibrations"][0]
    assert c["adequacy_status"]=="referenced_range"
    assert [c["scenario_conversion"][s]["formula_value"] for s in ("low","base","high")]==pytest.approx([100,110,120])
    validate_published_forecast(result,d)
    d["operating_research"]["calibrations"][0]["observed_range"]=None
    unknown=module().analyze_operating_research(d,validate_document(d))["calibrations"][0]
    assert unknown["observed_range"] is None and unknown["adequacy_status"]=="unverified"
    assert "observed_range_unknown" in unknown["reasons"]


def test_calibration_does_not_substitute_current_year_for_observed_reference_period():
    d=calibrated_document()
    next(p for p in d["parameters"] if p["parameter_id"]=="reference_lower")["period"]="FY2026"
    next(c for c in d["evidence_claims"] if c["target_id"]=="reference_lower")["period"]="FY2026"
    diag=module().analyze_operating_research(d,validate_document(d))["calibrations"][0]
    assert diag["adequacy_status"]=="unverified"
    assert "observed_input_period_mismatch" in diag["reasons"]


@pytest.mark.parametrize("entity",["Aster","恒微"])
def test_dated_quarter_delay_reuses_native_formula_and_shared_constraint(entity):
    from research.timing_bridge import build_quarter_delay_bridge
    from test_data_contract import finalize_contract
    from test_revenue_constraints import _series
    d=forecast_document()
    d["company_name"]=entity
    # Apply one common joint financing/delivery stress. Amounts are explicit fixtures,
    # never claimed to be a calibrated Low or a real company capacity limit.
    original=run_forecast(d)
    deferred={s:add_parameter(d,"q4_deferred_"+s,20,2026,s) for s in ("low","base","high")}
    catch_up={s:add_parameter(d,"catch_up_"+s,0.75,2027,s,dimension="ratio") for s in ("low","base","high")}
    for p in d["parameters"]:
        if p["parameter_id"] in deferred.values():
            p["measurement_period"]="FY2026Q4"
        if p["parameter_id"] in catch_up.values():
            p["unit"]="ratio"
    stressed,receipt=build_quarter_delay_bridge(d,segment_name="Segment A",from_period="FY2026Q4",to_period="FY2027Q1",
        deferred_parameter_ids=deferred,catch_up_parameter_ids=catch_up,prefix="joint_delay",rationale="Illustrative one-quarter financing and delivery delay, 25% canceled.")
    finalize_contract(stressed)
    result=run_forecast(stressed)
    for s in ("low","base","high"):
        before=original["consolidated_forecast"][s]["annual_revenue"]
        after=result["consolidated_forecast"][s]["annual_revenue"]
        assert after["2026"]==pytest.approx(before["2026"]-20)
        assert after["2027"]==pytest.approx(before["2027"]+15)
        assert sum(after.values())==pytest.approx(sum(before.values())-5)
    assert receipt["status"]=="illustrative_stress" and receipt["delay_quarters"]==1
    caps=_series(stressed,"shared_capacity",{s:[140,160] for s in ("low","base","high")},"revenue")
    stressed["revenue_constraints"]=[{"constraint_id":"shared", "type":"sum_cap","segments":["Segment A","Segment B"],
        "allocation":"proportional","scenario_parameter_ids":caps,"rationale":"Synthetic shared delivery cap; no CPU/GPU separate capacity double count."}]
    with pytest.raises(ForecastInputError,match="scenario ordering"):
        run_forecast(stressed)
    # A fixed cap can change segment shares and cross coherent scenarios. Preserve
    # that rejection; a separate, explicitly conditional cap case has ordered paths.
    cap_index={p["parameter_id"]:p for p in stressed["parameters"]}
    for scenario,values in (("low",[140,160]),("base",[150,170]),("high",[160,180])):
        for pid,value in zip(caps[scenario],values):
            cap_index[pid]["value"]=value
    finalize_contract(stressed)
    constrained=run_forecast(stressed)
    assert constrained["consolidated_forecast"]["high"]["annual_revenue"]==pytest.approx({"2026":160,"2027":180})
    assert constrained["constraint_audit"]
    validate_published_forecast(constrained,stressed)


def test_actual_case_assembly_cli_then_native_validate_compute_snapshot(tmp_path):
    import subprocess
    from company_wiki_source_v2 import build_revenue_source_record_from_verified_read
    from test_company_wiki_source_reader_v2 import BODY, _ref, _receipt
    d=calibrated_document()
    raw_receipt=_receipt()
    manifest=raw_receipt.pop("manifest")
    candidate={"status":"source_candidate","source_ref":_ref(),"byte_verification":"pending_verified_open",
        "document_kind":manifest["document_kind"],"fiscal_year":manifest["fiscal_year"],"fiscal_period":manifest["fiscal_period"],
        "resolution_outcome":"reused_existing","download_events":0}
    source=build_revenue_source_record_from_verified_read(source_ref=_ref(),read_receipt=raw_receipt,
        source_bytes=BODY,source_manifest=manifest,source_candidate=candidate,as_of_date=d["as_of_date"],
        source_type="regulatory_filing",publisher="synthetic producer fixture",page_or_section="1")
    sid=source["source_id"]
    def rekey(value):
        if isinstance(value,dict):
            return {key:rekey(v) for key,v in value.items()}
        if isinstance(value,list):
            return [rekey(v) for v in value]
        return sid if value=="filing" else value
    d=rekey(d)
    d["sources"][0]=source
    for c in d["evidence_claims"]:
        if c["source_id"]==sid:
            c["content_sha256"]=source["capture"]["snapshot_sha256"]
            c["capture_receipt_sha256"]=source["capture"]["receipt_sha256"]
    prep={"schema_version":"source-preparation-result/1","source":source,"filing_fetch":None,"narrative":None}
    research=d.pop("operating_research")
    for name,value in (("input",d),("research",research),("preparation",prep),("discovery",{"schema_version":"synthetic-discovery-receipt/1","items":[],"coverage_complete":False})):
        (tmp_path/(name+".json")).write_text(json.dumps(value,ensure_ascii=False),encoding="utf-8")
    root=Path(__file__).resolve().parents[1]
    assembled=tmp_path/"assembled"
    command=[sys.executable,"-X","utf8","-B",str(root/"tools/build_auditable_case.py"),"--company","synthetic",
        "--input",str(tmp_path/"input.json"),"--research",str(tmp_path/"research.json"),"--preparation",str(tmp_path/"preparation.json"),
        "--discovery",str(tmp_path/"discovery.json"),"--as-of",d["as_of_date"],"--output-root",str(assembled)]
    run=subprocess.run(command,capture_output=True,text=True,encoding="utf-8",timeout=30)
    assert run.returncode==0,run.stderr
    receipt=json.loads((assembled/"assembly.json").read_text(encoding="utf-8"))
    assert receipt["narrative_status"]=="not_consumed"
    assert receipt["source_bindings"][0]["source_ref"]==_ref()
    assert receipt["new_supplier_calls"]==0 and receipt["new_model_calls"]==0
    native=tmp_path/"native"
    run=subprocess.run([sys.executable,"-X","utf8","-B",str(root/"tools/run_target_measurement_e2e.py"),
        "--input",str(assembled/"linked-input.json"),"--output-root",str(native)],capture_output=True,text=True,encoding="utf-8",timeout=30)
    assert run.returncode==0,run.stderr
    assert (native/"snapshot.json").exists()
    result=json.loads((native/"forecast.json").read_text(encoding="utf-8"))
    assert result["confidence"]["research_adequacy"]["calibrations"][0]["adequacy_status"]=="referenced_range"


def test_numeric_historical_baseline_keeps_history_role_without_future_support():
    d=forecast_document()
    for c in d["evidence_claims"]:
        if c["target_type"]=="historical_revenue":
            c["evidence_role"]="history_base"
    # A measured historical number is still a historical base, not a mechanism.
    result=run_forecast(d)
    assert result["base_revenue"]==150
