"""RF-RATCHET-REST-A differential probe: original vs refactored behavior.

Run:  python diff_probe.py <scripts_root>
Prints ONE json object: {probe_name: {"ok": <json-string>} | {"err": [ExcType, str]}}.

Both sides run identical probe code; equality of the two dumps is the
zero-behavior-change claim (outputs incl. key/list order, exception type+message).
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))

RESULTS: dict[str, dict] = {}


def probe(name):
    def wrap(fn):
        try:
            RESULTS[name] = {"ok": fn()}
        except BaseException as exc:  # noqa: BLE001 - identity compare, not handling
            RESULTS[name] = {"err": [type(exc).__name__, str(exc)]}
        return fn
    return wrap


# --------------------------------------------------------------------------
# forecast.calc
# --------------------------------------------------------------------------
from forecast.calc import (  # noqa: E402
    base_forecast_parameter_ids,
    base_segment_parameter_ids,
    collect_parameter_roles,
    evaluate_derived_formula,
)


@probe("calc.recognition.variants")
def _():
    # recognition scan lives inline in ORIG and in a helper in NEW; probe it
    # only through the public collect_parameter_roles (must exist on both).
    cases = [
        {"carry_in_parameter_ids": {"low": ["c1"], "base": ["c2", 5, None]},
         "progress_parameter_ids": {"high": ["g1", "g1"]}},
        {"carry_in_parameter_ids": "not-a-dict", "progress_parameter_ids": ["x"]},
        {"carry_in_parameter_ids": {"base": "notlist"}},
        {"progress_parameter_ids": {"base": {"a": "b"}}},
        {},
        ["not", "a", "dict"],
        "string",
        {"carry_in_parameter_ids": {}, "progress_parameter_ids": {}},
        {"unknown_key": 1},
        None,
    ]
    outs = []
    index = {"c1": {"value": 3.0}, "c2": {"value": 4.0}, "g1": {"value": 5.0}}
    for case in cases:
        data = {"segments": [{"name": "S", "recognition": case}]}
        try:
            res = collect_parameter_roles(data, index)
            outs.append([repr(case), "ok",
                         json.dumps({k: sorted(v) for k, v in res.items()})])
        except BaseException as exc:  # noqa: BLE001
            outs.append([repr(case), type(exc).__name__, str(exc)])
    return json.dumps(outs)


_RICH = {
    "reported_total_revenue_parameter_id": "tot",
    "base_adjustment_parameter_ids": ["adj1", "adj2", 7, "adj1"],
    "segments": [
        {"name": "A",
         "base_revenue_parameter_id": "a_base",
         "base_backlog_parameter_id": "a_bl",
         "base_orders_parameter_id": "a_bo",
         "scenarios": {
             "base": {"model": "direct_revenue",
                      "driver_parameter_ids": {"revenue": ["p1", "p2"], "growth_rate": ["p3"]}},
             "low": "not-a-dict",
             "high": {"driver_parameter_ids": "not-a-dict"},
         },
         "recognition": {"mode": "lagged_activity",
                         "carry_in_parameter_ids": {"low": ["c1"], "base": ["c2", 5]},
                         "progress_parameter_ids": {"high": ["g1"]}}},
        "not-a-dict",
        {"name": "B", "scenarios": "not-a-dict",
         "recognition": ["x"], "base_revenue_parameter_id": 7,
         "project_backlog": "pb1"},
        {"name": "C", "recognition": {}},
    ],
    "forecast_adjustments": [
        {"scenario_parameter_ids": {"base": ["f1", "f2"], "low": "notlist"}},
        "junk",
        {"scenario_parameter_ids": {}},
    ],
    "revenue_constraints": [
        {"type": "sum_cap", "segments": ["A"], "parameter_ids": ["k1"],
         "scenario_parameter_ids": {"base": "k1"}},
    ],
}
_PARAM_INDEX = {
    "tot": {"value": 100.0, "kind": "reported_fact", "period": "FY2025"},
    "p1": {"value": 1.0}, "p2": {"value": 2.0}, "p3": {"value": 0.1},
    "c1": {"value": 3.0}, "c2": {"value": 4.0}, "g1": {"value": 5.0},
    "f1": {"value": 6.0}, "f2": {"value": 7.0},
    "adj1": {"value": 8.0}, "adj2": {"value": 9.0},
    "a_base": {"value": 10.0}, "a_bl": {"value": 11.0}, "a_bo": {"value": 12.0},
    "pb1": {"value": 13.0},
    "d1": {"kind": "derived_fact", "input_parameter_ids": ["p1", "d2", "missing"]},
    "d2": {"kind": "derived_fact", "input_parameter_ids": ["p2", "d1"]},
    "k1": {"value": 14.0},
}


@probe("calc.collect.rich")
def _():
    out = collect_parameter_roles(_RICH, _PARAM_INDEX)
    return json.dumps({k: sorted(v) for k, v in out.items()})


@probe("calc.collect.with_derived")
def _():
    data = dict(_RICH, base_adjustment_parameter_ids=["d1", "tot"])
    out = collect_parameter_roles(data, _PARAM_INDEX)
    return json.dumps({k: sorted(v) for k, v in out.items()})


@probe("calc.collect.empty")
def _():
    out = collect_parameter_roles({}, {})
    return json.dumps({k: sorted(v) for k, v in out.items()})


@probe("calc.collect.no_segments_key")
def _():
    out = collect_parameter_roles({"segments": None}, _PARAM_INDEX)
    return json.dumps({k: sorted(v) for k, v in out.items()})


@probe("calc.base_forecast_ids.rich")
def _():
    return json.dumps(sorted(base_forecast_parameter_ids(_RICH, _PARAM_INDEX)))


@probe("calc.base_segment_ids.rich")
def _():
    out = base_segment_parameter_ids(_RICH, _PARAM_INDEX)
    return json.dumps({k: sorted(v) for k, v in sorted(out.items())})


@probe("calc.derived_formula.grid")
def _():
    outs = []
    for formula, inputs in [
        ("x0+x1", [1.0, 2.0]), ("x0*x1-x0", [3.0, 4.0]), ("x0/x1", [1.0, 4.0]),
        ("x0**2", [3.0, 0.0]), ("-x0", [2.5, 0.0]), ("x0/x1", [1.0, 0.0]),
        ("x0**x1", [2.0, 99]), ("x0**x1", [2.0, 5.0]), ("bad name", [1.0]),
        ("x0+", [1.0]), ("x9", [1.0]), ("", []), ("x0" * 501, [1.0]),
        ("x0 // x1", [5.0, 2.0]),
    ]:
        try:
            outs.append([formula, "ok", evaluate_derived_formula(formula, inputs)])
        except BaseException as exc:  # noqa: BLE001
            outs.append([formula, type(exc).__name__, str(exc)])
    return json.dumps(outs)


# --------------------------------------------------------------------------
# generate_input_template
# --------------------------------------------------------------------------
import generate_input_template as gen  # noqa: E402
from model_registry import MODEL_REGISTRY  # noqa: E402
from model_extensions import EXTENSION_OPENING_BALANCES  # noqa: E402


def _bt(**kw):
    args = dict(name="Acme", base_year=2025, forecast_years=[2026, 2027],
                currency="USD", unit="million", segment_names=["Alpha", "Beta"],
                segment_models=None)
    args.update(kw)
    return gen.build_template(**args)


@probe("template.default")
def _():
    return json.dumps(_bt(), ensure_ascii=False)


@probe("template.every_registered_model")
def _():
    outs = []
    for model in sorted(MODEL_REGISTRY):
        for seg in (["Alpha"], ["Alpha", "Beta"]):
            try:
                t = _bt(segment_names=seg, segment_models={s: model for s in seg})
                outs.append([model, len(seg), "ok", json.dumps(t, ensure_ascii=False)])
            except BaseException as exc:  # noqa: BLE001
                outs.append([model, len(seg), type(exc).__name__, str(exc)])
    return json.dumps(outs)


@probe("template.extension_models_opening_balances")
def _():
    outs = []
    for model in sorted(EXTENSION_OPENING_BALANCES):
        t = _bt(segment_names=["Alpha"], segment_models={"Alpha": model})
        seg = t["segments"][0]
        outs.append([model, sorted(k for k in seg if k.startswith("base_")),
                     json.dumps(t, ensure_ascii=False)])
    return json.dumps(outs)


@probe("template.error_unknown_segment")
def _():
    try:
        _bt(segment_models={"Ghost": "direct_revenue"})
    except BaseException as exc:  # noqa: BLE001
        return [type(exc).__name__, str(exc)]
    raise AssertionError("expected ValueError")


@probe("template.error_unknown_model")
def _():
    try:
        _bt(segment_models={"Alpha": "not_a_model"})
    except BaseException as exc:  # noqa: BLE001
        return [type(exc).__name__, str(exc)]
    raise AssertionError("expected ValueError")


@probe("template.edge_inputs")
def _():
    outs = []
    for kw in [dict(base_year=2000, forecast_years=[2001], segment_names=["Only One"]),
               dict(currency="CNY", unit="thousand", forecast_years=[2026, 2027, 2028],
                    segment_names=["A B", "c-d"])]:
        outs.append(json.dumps(_bt(**kw), ensure_ascii=False))
    return json.dumps(outs)


@probe("template.cli_matrix")
def _():
    outs = []
    script = ROOT / "generate_input_template.py"
    cli_cases = [
        ["--name", "Acme", "--base-year", "2025", "--forecast-years", "2026",
         "--segments", "Alpha", "Beta"],
        ["--name", "Acme", "--base-year", "2025", "--forecast-years", "2026", "2027",
         "--segments", "Alpha", "--segment-model", "Alpha=direct_revenue"],
        ["--name", "Acme", "--base-year", "2025", "--forecast-years", "2026",
         "--segments", "Alpha", "--segment-model", "Ghost=direct_revenue"],
        ["--name", "Acme", "--base-year", "2025", "--forecast-years", "2026",
         "--segments", "Alpha", "--segment-model", "Alpha=nope"],
        ["--name", "Acme", "--base-year", "2025", "--forecast-years", "2026",
         "--segments", "Alpha", "--segment-model", "Alpha=direct_revenue",
         "--segment-model", "Alpha=direct_revenue"],
        ["--name", "Acme", "--base-year", "2025", "--forecast-years", "2026",
         "--segments", "Alpha"],
    ]
    for case in cli_cases:
        proc = subprocess.run(
            [sys.executable, "-B", str(script), *case],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        outs.append([case[case.index("--segment-model") + 1] if "--segment-model" in case else "plain",
                     proc.returncode,
                     json.dumps(json.loads(proc.stdout)) if proc.returncode == 0 else proc.stderr])
    return json.dumps(outs)


# --------------------------------------------------------------------------
# research.targets
# --------------------------------------------------------------------------
from research.targets import (  # noqa: E402
    add_management_target_analysis,
    validate_management_target_coverage,
)
from contracts.constants import (  # noqa: E402
    MANAGEMENT_COMMUNICATION_CATEGORIES,
    MANAGEMENT_COMMUNICATION_STATUSES,
    SCENARIOS,
)

AS_OF = date(2026, 9, 23)
SOURCE_INDEX = {"s1": {"source_id": "s1"}}
CLAIM_INDEX = {
    "c1": {"claim_id": "c1", "source_id": "s1", "target_type": "management_target",
           "target_id": "t_mod", "support_type": "exact_value",
           "extracted_value": 50.0, "unit": "USD million", "period": "FY2026"},
    "c_bench": {"claim_id": "c_bench", "source_id": "s1",
                "target_type": "management_target", "target_id": "t_bench",
                "support_type": "rationale_support"},
}
PARAM_INDEX = {
    "m1": {"value": 0.0, "claim_ids": ["c1"], "source_ids": ["s1"]},
    "n1": {"value": 0.1, "claim_ids": ["c1"], "source_ids": ["s1"]},
}


def _coverage_record(category, status="checked", **extra):
    rec = {"category": category, "status": status, "source_ids": [],
           "checked_date": "2026-09-01",
           "conclusion": f"conclusion for {category}",
           "material_revenue_target_ids": []}
    if status == "checked":
        rec["source_ids"] = ["s1"]
    else:
        rec["rationale"] = f"rationale for {status}"
    if status == "not_available":
        rec["search_description"] = "searched filings"
        rec["search_event"] = {"query_scope": "company", "query_time": "2026-09-01T00:00:00Z",
                               "event_ids": ["e1"], "generated_by": "tool",
                               "event_sha256": "ab"}
    if status == "not_applicable":
        rec["reason_code"] = "no_guidance"
    rec.update(extra)
    return rec


def _full_coverage(**overrides_per_category):
    recs = []
    statuses = ["checked", "not_available", "not_applicable"]
    for i, category in enumerate(MANAGEMENT_COMMUNICATION_CATEGORIES):
        recs.append(_coverage_record(category, statuses[i % len(statuses)],
                                     **overrides_per_category.get(category, {})))
    return recs


def _base_data(**kw):
    data = {
        "currency": "USD", "unit": "million",
        "forecast_years": [2026, 2027],
        "segments": [{"name": "Seg1",
                      "scenarios": {"base": {"model": "direct_revenue",
                                             "driver_parameter_ids": {"revenue": ["m1"]}},
                                    "low": {"model": "direct_revenue",
                                            "driver_parameter_ids": {"revenue": ["m1"]}},
                                    "high": {"model": "direct_revenue",
                                             "driver_parameter_ids": {"revenue": ["m1"]}}}}],
        "management_communication_coverage": _full_coverage(),
        "management_targets": [],
    }
    data.update(kw)
    return data


def _target(tid, **kw):
    tgt = {
        "target_id": tid, "statement": f"{tid} statement", "metric_name": "revenue",
        "metric_definition": "total revenue", "target_period": "FY2026",
        "raw_unit": "USD million", "raw_currency": "USD", "raw_scale": "million",
        "measurement_rationale": "how measured", "perimeter_notes": "notes",
        "rationale": "why it matters",
        "raw_target_value": 50.0, "measurement_basis": "annual_period",
        "measurement_periods": ["FY2026"],
        "materiality": "contextual", "commitment_strength": "guidance",
        "perimeter_status": "matched", "treatment": "unmodeled_data_gap",
        "comparison": "at_least", "scope": {"type": "company", "name": "Acme"},
        "claim_ids": [], "mapped_parameter_ids": [], "mapped_scenarios": [],
        "comparison_value": None,
    }
    claim_ids = kw.pop("claim_ids", None)
    tgt.update(kw)
    if claim_ids is None:
        # validate_claim_ids requires at least one claim: auto-register an
        # exact-value claim matching this target so late validation branches
        # are actually exercised (identically on both sides).
        cid = f"c_{tid}"
        claim_ids = [cid]
        _CLAIMS_BAG[cid] = {"claim_id": cid, "source_id": "s1",
                            "target_type": "management_target", "target_id": tid,
                            "support_type": "exact_value",
                            "extracted_value": tgt["raw_target_value"],
                            "unit": tgt["raw_unit"], "period": tgt["target_period"]}
    tgt["claim_ids"] = claim_ids
    return tgt


_CLAIMS_BAG: dict[str, dict] = {}


def _run(data, claim_index=None, param_index=None):
    out = validate_management_target_coverage(
        data, SOURCE_INDEX, param_index if param_index is not None else PARAM_INDEX,
        claim_index if claim_index is not None else {**CLAIM_INDEX, **_CLAIMS_BAG}, AS_OF)
    return json.dumps(out, sort_keys=True)


@probe("targets.valid_empty_targets_mixed_statuses")
def _():
    return _run(_base_data())


@probe("targets.valid_coverage_all_statuses")
def _():
    # sorted(): MANAGEMENT_COMMUNICATION_STATUSES is a set -> list() order is
    # hash-randomized per process; sorted() makes the probe deterministic.
    statuses = sorted(MANAGEMENT_COMMUNICATION_STATUSES)
    recs = [_coverage_record(c, statuses[i % len(statuses)])
            for i, c in enumerate(MANAGEMENT_COMMUNICATION_CATEGORIES)]
    return _run(_base_data(management_communication_coverage=recs))


@probe("targets.valid_out_of_horizon_target")
def _():
    tgt = _target("t_ool", measurement_periods=["FY2030"], treatment="out_of_horizon",
                  perimeter_status="mismatch")
    data = _base_data(management_targets=[tgt])
    data["management_communication_coverage"] = _full_coverage(
        **{MANAGEMENT_COMMUNICATION_CATEGORIES[0]: {"material_revenue_target_ids": ["t_ool"]}})
    return _run(data)


@probe("targets.valid_modeled_target")
def _():
    tgt = _target("t_mod", materiality="material", treatment="modeled_scenario",
                  mapped_parameter_ids=["m1"], mapped_scenarios=list(SCENARIOS),
                  comparison_value=40.0, comparison_currency="USD",
                  comparison_scale="million", normalization_rationale="norm")
    data = _base_data(management_targets=[tgt])
    data["management_communication_coverage"] = _full_coverage(
        **{MANAGEMENT_COMMUNICATION_CATEGORIES[3]: {"material_revenue_target_ids": ["t_mod"]}})
    out = _run(data)
    result = json.loads(out)
    result["targets"][0]["scenario_comparison"] = "OMITTED"  # exercised in probe below
    return json.dumps(result, sort_keys=True)


@probe("targets.valid_modeled_analysis")
def _():
    tgt = _target("t_mod", materiality="material", treatment="modeled_scenario",
                  mapped_parameter_ids=["m1"], mapped_scenarios=list(SCENARIOS),
                  comparison_value=40.0, comparison_currency="USD",
                  comparison_scale="million", normalization_rationale="norm")
    data = _base_data(management_targets=[tgt])
    data["management_communication_coverage"] = _full_coverage(
        **{MANAGEMENT_COMMUNICATION_CATEGORIES[3]: {"material_revenue_target_ids": ["t_mod"]}})
    validated = {"management_target_coverage": json.loads(_run(data))}
    result = {
        "consolidated_forecast": {s: {"annual_revenue": {"2026": 45.0, "2027": 60.0}}
                                  for s in SCENARIOS},
        "segments": [{"name": "Seg1",
                      "scenarios": {s: {"recognized_revenue": {"2026": 45.0, "2027": 60.0}}
                                    for s in SCENARIOS}}],
    }
    return json.dumps(add_management_target_analysis(validated, result), sort_keys=True)


@probe("targets.valid_run_rate_target")
def _():
    tgt = _target("t_rr", treatment="modeled_scenario", materiality="material",
                  measurement_basis="run_rate_at_period_end",
                  comparison_basis="annual_recognized_revenue",
                  normalization_parameter_ids=["n1"], normalization_formula="x0*(1+x1)",
                  mapped_parameter_ids=["m1"], mapped_scenarios=list(SCENARIOS),
                  comparison_value=55.0, comparison_currency="USD",
                  comparison_scale="million", normalization_rationale="annualize")
    data = _base_data(management_targets=[tgt])
    data["management_communication_coverage"] = _full_coverage(
        **{MANAGEMENT_COMMUNICATION_CATEGORIES[0]: {"material_revenue_target_ids": ["t_rr"]}})
    return _run(data)


@probe("targets.valid_independent_benchmark")
def _():
    tgt = _target("t_bench", treatment="independent_benchmark",
                  materiality="contextual",
                  mapped_parameter_ids=["m1"], mapped_scenarios=list(SCENARIOS),
                  benchmark_rationale="analyst view",
                  benchmark_claim_ids=["c_bench"],
                  comparison_value=48.0, comparison_currency="USD",
                  comparison_scale="million", normalization_rationale="norm")
    data = _base_data(management_targets=[tgt])
    data["management_communication_coverage"] = _full_coverage(
        **{MANAGEMENT_COMMUNICATION_CATEGORIES[3]: {"material_revenue_target_ids": ["t_bench"]}})
    return _run(data)


@probe("targets.valid_cumulative_target")
def _():
    tgt = _target("t_cum", measurement_basis="cumulative_periods",
                  measurement_periods=["FY2027", "FY2028"],
                  comparison_value=90.0, comparison_currency="USD",
                  comparison_scale="million", normalization_rationale="sum",
                  treatment="out_of_horizon", raw_target_value=1000.0)
    data = _base_data(management_targets=[tgt])
    data["management_communication_coverage"] = _full_coverage(
        **{MANAGEMENT_COMMUNICATION_CATEGORIES[0]: {"material_revenue_target_ids": ["t_cum"]}})
    return _run(data)


@probe("targets.error_matrix")
def _():
    outs = []

    def case(name, fn):
        try:
            outs.append([name, "ok", fn()])
        except BaseException as exc:  # noqa: BLE001
            outs.append([name, type(exc).__name__, str(exc)])

    case("coverage_not_list", lambda: _run(_base_data(management_communication_coverage="x")))
    case("coverage_too_short", lambda: _run(_base_data(
        management_communication_coverage=[_full_coverage()[0]])))
    case("bad_category", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record("not_a_category")] + _full_coverage()[1:])))
    case("dup_category", lambda: _run(_base_data(management_communication_coverage=[
        _full_coverage()[0], _full_coverage()[0]] + _full_coverage()[2:])))
    case("bad_status", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], "weird")])))
    case("empty_conclusion", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], conclusion="  ")])))
    case("checked_no_sources", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], "checked", source_ids=[])])))
    case("unchecked_with_sources", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], "not_checked",
                         source_ids=["s1"])])))
    case("unknown_source", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], "checked",
                         source_ids=["ghost"])])))
    case("checked_after_as_of", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], checked_date="2027-01-01")])))
    case("na_no_reason", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], "not_available",
                         search_event=None, reason_code=None)])))
    case("na_bad_event", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], "not_available",
                         search_event={"query_scope": "", "query_time": "",
                                       "event_ids": [], "generated_by": "",
                                       "event_sha256": ""})])))
    case("no_search_description", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], "not_available",
                         search_description=None)])))
    case("nap_no_reason", lambda: _run(_base_data(management_communication_coverage=[
        _coverage_record(MANAGEMENT_COMMUNICATION_CATEGORIES[0], "not_applicable",
                         reason_code="  ")])))
    case("targets_not_list", lambda: _run(_base_data(management_targets="x")))
    case("target_not_dict", lambda: _run(_base_data(management_targets=["nope"])))
    case("target_no_id", lambda: _run(_base_data(management_targets=[_target("t1", target_id=None)])))
    case("dup_target_id", lambda: _run(_base_data(
        management_targets=[_target("t1"), _target("t1")])))
    case("target_missing_field", lambda: _run(_base_data(
        management_targets=[_target("t1", statement="  ")])))
    case("target_negative", lambda: _run(_base_data(
        management_targets=[_target("t1", raw_target_value=-1.0)])))
    case("bad_basis", lambda: _run(_base_data(
        management_targets=[_target("t1", measurement_basis="wishful")])))
    case("periods_unsorted", lambda: _run(_base_data(
        management_targets=[_target("t1", measurement_basis="cumulative_periods",
                                    measurement_periods=["FY2027", "FY2026"])])))
    case("annual_two_periods", lambda: _run(_base_data(
        management_targets=[_target("t1", measurement_periods=["FY2026", "FY2027"])])))
    case("cum_single", lambda: _run(_base_data(
        management_targets=[_target("t1", measurement_basis="cumulative_periods",
                                    measurement_periods=["FY2026"])])))
    case("cum_noncontiguous", lambda: _run(_base_data(
        management_targets=[_target("t1", measurement_basis="cumulative_periods",
                                    measurement_periods=["FY2026", "FY2028"])])))
    case("ambiguous_with_periods", lambda: _run(_base_data(
        management_targets=[_target("t1", measurement_basis="ambiguous",
                                    measurement_periods=["FY2026"])])))
    case("ambiguous_not_gap", lambda: _run(_base_data(
        management_targets=[_target("t1", measurement_basis="ambiguous",
                                    treatment="modeled_scenario")])))
    case("bad_materiality", lambda: _run(_base_data(
        management_targets=[_target("t1", materiality="materialish")])))
    case("bad_commitment", lambda: _run(_base_data(
        management_targets=[_target("t1", commitment_strength="vibe")])))
    case("bad_perimeter", lambda: _run(_base_data(
        management_targets=[_target("t1", perimeter_status="ishy")])))
    case("bad_treatment", lambda: _run(_base_data(
        management_targets=[_target("t1", treatment="handwavy")])))
    case("bad_comparison", lambda: _run(_base_data(
        management_targets=[_target("t1", comparison="roughly")])))
    case("bad_scope", lambda: _run(_base_data(
        management_targets=[_target("t1", scope={"type": "galaxy", "name": "G"})])))
    case("scope_no_name", lambda: _run(_base_data(
        management_targets=[_target("t1", scope={"type": "company", "name": " "})])))
    case("scope_unknown_segment", lambda: _run(_base_data(
        management_targets=[_target("t1", scope={"type": "segment", "name": "Nope"})])))
    case("claim_mismatch_value", lambda: _run(_base_data(management_targets=[
        _target("t_mod", claim_ids=["c1"], comparison_value=None)]),
        claim_index={**CLAIM_INDEX, "c1": {**CLAIM_INDEX["c1"], "extracted_value": 9.0}}))
    case("claim_wrong_unit", lambda: _run(_base_data(management_targets=[
        _target("t_mod", claim_ids=["c1"])]),
        claim_index={**CLAIM_INDEX, "c1": {**CLAIM_INDEX["c1"], "unit": "EUR"}}))
    case("mapped_unknown_param", lambda: _run(_base_data(
        management_targets=[_target("t1", mapped_parameter_ids=["ghost"])])))
    case("mapped_param_unused", lambda: _run(_base_data(
        management_targets=[_target("t1", mapped_parameter_ids=["n1"],
                                    mapped_scenarios=list(SCENARIOS))])))
    case("mapped_bad_scenario", lambda: _run(_base_data(
        management_targets=[_target("t1", mapped_scenarios=["sideways"])])))
    case("ambiguous_gap_mapping", lambda: _run(_base_data(management_targets=[
        _target("t1", measurement_basis="ambiguous", treatment="unmodeled_data_gap",
                mapped_scenarios=list(SCENARIOS))])))
    case("modeled_no_horizon", lambda: _run(_base_data(management_targets=[
        _target("t1", measurement_periods=["FY2030"], treatment="modeled_scenario",
                materiality="material", mapped_parameter_ids=["m1"],
                mapped_scenarios=list(SCENARIOS),
                comparison_value=1.0, comparison_currency="USD",
                comparison_scale="million", normalization_rationale="n")])))
    case("modeled_uncomparable", lambda: _run(_base_data(management_targets=[
        _target("t1", treatment="modeled_scenario", materiality="material",
                perimeter_status="mismatch", mapped_parameter_ids=["m1"],
                mapped_scenarios=list(SCENARIOS))])))
    case("material_not_in_scenario", lambda: _run(_base_data(management_targets=[
        _target("t1", materiality="material", treatment="unmodeled_data_gap")])))
    case("mismatch_modeled", lambda: _run(_base_data(management_targets=[
        _target("t1", perimeter_status="mismatch", treatment="modeled_scenario",
                materiality="material", mapped_parameter_ids=["m1"],
                mapped_scenarios=list(SCENARIOS),
                comparison_value=1.0, comparison_currency="USD",
                comparison_scale="million", normalization_rationale="n")])))
    case("bench_no_rationale", lambda: _run(_base_data(management_targets=[
        _target("t1", treatment="independent_benchmark",
                mapped_parameter_ids=["m1"], mapped_scenarios=list(SCENARIOS),
                comparison_value=1.0, comparison_currency="USD",
                comparison_scale="million", normalization_rationale="n")])))
    case("runrate_no_conversion", lambda: _run(_base_data(management_targets=[
        _target("t1", treatment="modeled_scenario", materiality="material",
                measurement_basis="run_rate_at_period_end",
                mapped_parameter_ids=["m1"], mapped_scenarios=list(SCENARIOS),
                comparison_value=1.0, comparison_currency="USD",
                comparison_scale="million", normalization_rationale="n")])))
    case("runrate_unmapped_no_conv", lambda: _run(_base_data(management_targets=[
        _target("t1", measurement_basis="run_rate_at_period_end")])))
    case("runrate_bad_formula_vars", lambda: _run(_base_data(management_targets=[
        _target("t1", treatment="modeled_scenario", materiality="material",
                measurement_basis="run_rate_at_period_end",
                comparison_basis="annual_recognized_revenue",
                normalization_parameter_ids=["n1"], normalization_formula="x0+x5",
                mapped_parameter_ids=["m1"], mapped_scenarios=list(SCENARIOS),
                comparison_value=1.0, comparison_currency="USD",
                comparison_scale="million", normalization_rationale="n")])))
    case("runrate_value_mismatch", lambda: _run(_base_data(management_targets=[
        _target("t1", treatment="modeled_scenario", materiality="material",
                measurement_basis="run_rate_at_period_end",
                comparison_basis="annual_recognized_revenue",
                normalization_parameter_ids=["n1"], normalization_formula="x0*(1+x1)",
                mapped_parameter_ids=["m1"], mapped_scenarios=list(SCENARIOS),
                comparison_value=999.0, comparison_currency="USD",
                comparison_scale="million", normalization_rationale="n")])))
    case("comparison_currency_mismatch", lambda: _run(_base_data(management_targets=[
        _target("t1", comparison_value=5.0, comparison_currency="EUR")])))
    case("comparison_scale_mismatch", lambda: _run(_base_data(
        management_targets=[_target("t1", comparison_value=5.0,
                                    comparison_currency="USD",
                                    comparison_scale="billion")])))
    case("no_normalization_rationale", lambda: _run(_base_data(
        management_targets=[_target("t1", comparison_value=5.0,
                                    comparison_currency="USD",
                                    comparison_scale="million")])))
    case("comparable_but_none", lambda: _run(_base_data(
        management_targets=[_target("t1", comparison_value=5.0)])))
    case("uncomparable_with_value", lambda: _run(_base_data(management_targets=[
        _target("t1", treatment="out_of_horizon",
                measurement_periods=["FY2030"], comparison_value=5.0)])))
    case("bench_only_partial_scenarios", lambda: _run(_base_data(management_targets=[
        _target("t1", treatment="independent_benchmark", materiality="material",
                mapped_parameter_ids=["m1"], mapped_scenarios=["base"],
                benchmark_rationale="b", benchmark_claim_ids=["c_bench"],
                comparison_value=1.0, comparison_currency="USD",
                comparison_scale="million", normalization_rationale="n")])))
    case("coverage_target_id_unknown", lambda: _run(_base_data(
        management_communication_coverage=_full_coverage(
            **{MANAGEMENT_COMMUNICATION_CATEGORIES[0]:
               {"material_revenue_target_ids": ["ghost_target"]}}))))
    case("gap_unmodeled", lambda: _run(_base_data(management_targets=[
        _target("t1", treatment="unmodeled_data_gap")])))
    case("empty_data", lambda: _run({}))
    return json.dumps(outs)


@probe("targets.add_analysis_edge_cases")
def _():
    validated = {"management_target_coverage": {"communications": [], "targets": [], "counts": {}}}
    result = {"segments": [], "consolidated_forecast": {}}
    return json.dumps(add_management_target_analysis(validated, result), sort_keys=True)


print(json.dumps(RESULTS, sort_keys=True))
