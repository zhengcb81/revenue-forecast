"""Construct an illustrative dated delay using the existing native formula DAG.

No engine model or capacity policy is added. Quarter amounts and cancellation
fractions are explicit caller assumptions, not inferred from annual totals.
"""
from __future__ import annotations
from copy import deepcopy
import math
import re
from contracts.constants import SCENARIOS
from contracts.evidence import finite_number, require
from forecast.calc import evaluate_derived_formula
from model_registry import driver_value_bounds
from research.recognition_exposure import prove_pending_exposure


def build_quarter_delay_bridge(data, *, segment_name, from_period, to_period,
                               deferred_parameter_ids, catch_up_parameter_ids,
                               prefix, rationale):
    match_from = re.fullmatch(r"FY([0-9]{4})Q([1-4])", from_period)
    match_to = re.fullmatch(r"FY([0-9]{4})Q([1-4])", to_period)
    require(match_from is not None and match_to is not None, "delay periods must be fiscal quarters")
    first_year, first_quarter = map(int, match_from.groups())
    next_year, next_quarter = map(int, match_to.groups())
    require(first_quarter == 4 and next_quarter == 1 and next_year == first_year + 1,
            "annual delay bridge requires a one-quarter Q4 to next-Q1 shift")
    require(isinstance(rationale, str) and bool(rationale.strip()), "delay rationale required")
    require(isinstance(prefix, str) and bool(re.fullmatch(r"[A-Za-z0-9_.-]+", prefix)), "delay prefix invalid")
    require(set(deferred_parameter_ids) == set(catch_up_parameter_ids) == set(SCENARIOS), "delay needs all scenarios")
    out = deepcopy(data)
    years = out["forecast_years"]
    require(first_year in years and next_year in years, "delay needs both annual periods in horizon")
    index = {p["parameter_id"]: p for p in out["parameters"]}
    segment = next((s for s in out["segments"] if s["name"] == segment_name), None)
    require(segment is not None, "delay segment unknown")
    changes = {}
    for scenario in SCENARIOS:
        spec = segment["scenarios"][scenario]
        require(spec["model"] == "direct_revenue" and segment["recognition"]["mode"] == "modeled_as_recognized",
                "this aggregate bridge requires direct recognized revenue; choose an activity-specific bridge otherwise")
        require(deferred_parameter_ids[scenario] in index and catch_up_parameter_ids[scenario] in index, "delay parameter missing")
        deferred = index[deferred_parameter_ids[scenario]]
        fraction = index[catch_up_parameter_ids[scenario]]
        require(deferred["dimension"] == "revenue" and deferred.get("measurement_period") == from_period and deferred["period"] == f"FY{first_year}", "deferred amount must be explicit revenue for the source quarter")
        require(fraction["dimension"] == "ratio" and fraction["period"] == f"FY{next_year}", "catch-up fraction period/dimension mismatch")
        for p in (deferred, fraction):
            require(p.get("scenario") in (None, "all", scenario), "delay scenario mismatch")
        delay_amount = finite_number(deferred["value"], "deferred value")
        catch_up = finite_number(fraction["value"], "catch-up fraction")
        require(delay_amount >= 0 and 0 <= catch_up <= 1, "delay/cancellation bounds invalid")
        emitted = []
        for year, formula, extra_ids in ((first_year, "x0-x1", [deferred["parameter_id"]]),
                                         (next_year, "x0+x1*x2", [deferred["parameter_id"], fraction["parameter_id"]])):
            offset = years.index(year)
            old_id = spec["driver_parameter_ids"]["revenue"][offset]
            old = index[old_id]
            require(old["unit"] == deferred["unit"] and old.get("currency") == deferred.get("currency") and old.get("scale") == deferred.get("scale"), "delay unit/currency/scale mismatch")
            if year == first_year:
                require(delay_amount <= float(old["value"]), "delay cannot exceed current recognized amount")
            pid = f"{prefix}_{scenario}_{year}"
            require(pid not in index, "delay output parameter already exists")
            p = deepcopy(old)
            inputs = [old_id, *extra_ids]
            p.update(parameter_id=pid, kind="derived_fact", formula=formula, input_parameter_ids=inputs,
                     value=evaluate_derived_formula(formula, [float(index[i]["value"]) for i in inputs]),
                     definition=f"{segment_name} dated delay bridge {scenario} FY{year}",
                     rationale=rationale, claim_ids=[], source_ids=sorted({sid for i in inputs for sid in index[i].get("source_ids", [])}))
            p.pop("measurement_period", None)
            out["parameters"].append(p)
            index[pid] = p
            spec["driver_parameter_ids"]["revenue"][offset] = pid
            emitted.append({"parameter_id": pid, "formula": formula, "input_parameter_ids": inputs,
                            "value": p["value"], "unit": p["unit"]})
        changes[scenario] = {"deferred": delay_amount, "catch_up": delay_amount * catch_up,
                             "canceled": delay_amount * (1 - catch_up), "emitted": emitted}
    return out, {"schema_version": "dated-delay-bridge/1", "status": "illustrative_stress",
                 "segment_name": segment_name, "from_period": from_period, "to_period": to_period,
                 "delay_quarters": 1, "rationale": rationale, "scenarios": changes,
                 "limitations": ["Not a calibrated Low; existing scenario order and shared constraints still apply.",
                                 "Annual model cannot resolve an in-year quarterly delay; no x4 or annual sorting."]}


def _projected_amount(growth_count: int) -> str:
    return "x0" + "".join(f"*(1+x{offset})" for offset in range(1, growth_count + 1))


def _stress_ratio(index, param_id, period):
    rate = index.get(param_id, {})
    require(rate.get("dimension") == "ratio" and rate.get("period") == period
            and rate.get("scenario") in (None, "all"),
            f"{param_id}: shared stress needs a ratio for {period} across scenarios")
    value = finite_number(rate.get("value"), param_id)
    require(0 <= value <= 1, f"{param_id}: stress fraction must be between zero and one")


def _put_derived_ratio(out, index, *, param_id, definition, period, scenario, formula, inputs, rationale):
    require(param_id not in index, f"stress parameter already exists: {param_id}")
    value = evaluate_derived_formula(formula, [index[dep]["value"] for dep in inputs])
    row = {"parameter_id": param_id, "kind": "derived_fact", "definition": definition,
           "value": value, "dimension": "ratio", "unit": "ratio", "time_basis": "annual",
           "period": period, "scenario": scenario, "formula": formula, "input_parameter_ids": inputs,
           "rationale": rationale, "source_ids": [], "claim_ids": []}
    out["parameters"].append(row)
    index[param_id] = row


def _stress_growth_formula(baseline_ids, offset, first, exposure_id, delay_id, loss_id):
    # Keep the relative ratios coherent when the temporary shock rolls off.
    # Do not retime a dated recognized-flow fact or feed the loss into the next
    # year's unshocked growth base. Each formula consumes only its own inputs.
    inputs = baseline_ids[:offset + 2]
    exposure = f"x{len(inputs)}"
    inputs.append(exposure_id)
    deltas = {}
    if offset <= first + 1:
        deltas[first] = f"-{exposure}*x{len(inputs)}"
        inputs.append(loss_id)
    if offset > first:
        deltas[first + 1] = f"+{exposure}*x{len(inputs)}"
        inputs.append(delay_id)
    numerator = _projected_amount(offset + 1) + deltas.get(offset, "")
    denominator = _projected_amount(offset) + deltas.get(offset - 1, "")
    return f"({numerator})/({denominator})-1", inputs


def build_shared_recognition_stress(
    data, *, exposure_parameter_ids, from_year, delay_rate_parameter_id,
    cancellation_rate_parameter_id, prefix, rationale,
):
    """Author a native, illustrative stress for one event across businesses.

    Each exposure is an explicit dated forecast component of the business's
    recognized direct-growth path. The delayed fraction moves once to the next
    fiscal year. The cancellation fraction affects only the undelayed portion.
    A later year returns to the no-event path when it is in the horizon.
    """
    require(isinstance(rationale, str) and bool(rationale.strip()), "stress rationale required")
    require(isinstance(prefix, str) and bool(re.fullmatch(r"[A-Za-z0-9_.-]+", prefix)), "stress prefix invalid")
    years = data["forecast_years"]
    require(from_year in years and from_year + 1 in years, "stress needs two consecutive forecast years")
    identified = {segment["name"]: i for i, segment in enumerate(data["segments"])}
    require(bool(exposure_parameter_ids) and set(exposure_parameter_ids) <= identified.keys(),
            "stress needs explicit exposures in known businesses")

    out = deepcopy(data)
    index = {p["parameter_id"]: p for p in out["parameters"]}
    period = f"FY{from_year}"
    first = years.index(from_year)
    _stress_ratio(index, delay_rate_parameter_id, period)
    _stress_ratio(index, cancellation_rate_parameter_id, period)
    loss_rate = f"{prefix}_current_year_loss_fraction"
    _put_derived_ratio(out, index, param_id=loss_rate, definition=f"{prefix} delayed plus canceled fraction",
                       period=period, scenario="all", formula="x0+(1-x0)*x1",
                       inputs=[delay_rate_parameter_id, cancellation_rate_parameter_id], rationale=rationale)
    lower, upper = driver_value_bounds("direct_growth", "growth_rate")
    original_domain = {"lower": lower if math.isfinite(lower) else None,
                       "upper": upper if math.isfinite(upper) else None,
                       "basis": "Original direct_growth.growth_rate bounds for continued native sensitivity."}
    sensitivity_ids = {test["parameter_id"] for test in out.get("sensitivity_tests", [])}
    stressed = {}
    used = {scenario: set() for scenario in SCENARIOS}
    for name, exposures in exposure_parameter_ids.items():
        require(set(exposures) == set(SCENARIOS), f"{name}: stress needs low/base/high exposures")
        ordinal = identified[name]
        segment = out["segments"][ordinal]
        require(segment["recognition"]["mode"] == "modeled_as_recognized",
                f"{name}: this stress applies to a recognized revenue path")
        stressed[name] = {}
        for scenario in SCENARIOS:
            spec = segment["scenarios"][scenario]
            require(spec["model"] == "direct_growth", f"{name}: this stress requires direct_growth")
            drivers = spec["driver_parameter_ids"]["growth_rate"]
            baseline_ids = [segment["base_revenue_parameter_id"], *drivers]
            exposure_id = exposures[scenario]
            binding = prove_pending_exposure(data, index, baseline_ids[:first + 2], exposure_id, scenario, from_year)
            pending_origins = set(binding["pending_origin_ids"])
            require(used[scenario].isdisjoint(pending_origins),
                    f"{exposure_id}: the same pending flow cannot be shocked twice")
            used[scenario].update(pending_origins)
            value = finite_number(index[exposure_id]["value"], exposure_id)
            current_amount = evaluate_derived_formula(_projected_amount(first + 1),
                                                      [index[pid]["value"] for pid in baseline_ids[:first + 2]])
            require(0 <= value <= current_amount, f"{exposure_id}: stress exposure exceeds the forecast path")
            emitted = []
            if value and index[loss_rate]["value"]:
                for offset in range(first, min(first + 3, len(years))):
                    original = drivers[offset]
                    if original in sensitivity_ids:
                        index[original].setdefault("sensitivity_domain", dict(original_domain))
                    year = years[offset]
                    param_id = f"{prefix}_{ordinal}_{scenario}_{year}"
                    formula, inputs = _stress_growth_formula(baseline_ids, offset, first, exposure_id,
                                                             delay_rate_parameter_id, loss_rate)
                    _put_derived_ratio(out, index, param_id=param_id,
                                       definition=f"{name} {prefix} conditional growth {scenario} FY{year}",
                                       period=f"FY{year}", scenario=scenario, formula=formula, inputs=inputs,
                                       rationale=rationale)
                    drivers[offset] = param_id
                    emitted.append(param_id)
            stressed[name][scenario] = {
                "exposure_parameter_id": exposure_id, "growth_parameter_ids": emitted,
                "recognized_addend": binding,
            }
    return out, {"schema_version": "shared-recognition-stress/1", "status": "illustrative_stress",
                 "from_year": from_year, "catch_up_year": from_year + 1, "rationale": rationale,
                 "delay_rate_parameter_id": delay_rate_parameter_id,
                 "cancellation_rate_parameter_id": cancellation_rate_parameter_id,
                 "loss_rate_parameter_id": loss_rate, "exposures": stressed}
