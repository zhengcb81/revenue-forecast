"""Card-agnostic, verdict-carrying product runner for the M-card formula oracles.

Isolation contract
------------------
* The product scripts directory comes from --code-root, which MUST be the
  attempt-local isolated snapshot whose sha256 is recorded in source_manifest.json.
* The ONLY product entry point invoked is ``calculate_registered_model(**spec)``.
* Expected values come exclusively from evidence/<CARD>/oracle.json, produced by
  scripts/oracle_cards_M09_M12.py (standard library only; it never imports the product).
* Every negative case and every observation gets a NEW deepcopy of the frozen base
  input, built in memory (never round-tripped through a JSON parser).

Exit codes (verdict-carrying; a bookkeeping-only rc=0 is not allowed)
--------------------------------------------------------------------
  0 = pass            : the positive path matched the frozen oracle in structure, length
                        and value, the continuity positive passed, the defaults case
                        passed, and every negative case was rejected with the exception
                        type named in cases.json (ModelRegistryError).
  2 = no-verdict      : the expectation is missing from the frozen oracle, or the observed
                        output does not match the frozen expectation (structure / length /
                        field set / value / defaults / continuity). "保真不符".
  3 = negative failed : the positive side was fine, but at least one negative case was NOT
                        rejected as the frozen case expects (accepted, or rejected with a
                        different exception type).
  1 = harness error   : the comparison could not be attempted at all - product import
                        failure, missing/unparseable evidence file, an I/O error inside a
                        product call, or any unexpected harness exception.

Precedence: 1 (harness) > 2 (no-verdict / fidelity) > 3 (negative) > 0 (pass).

Declared expectations (REM-21 / T1-8; propagated from the M17-M20 reference runner)
-----------------------------------------------------------------------------------
The per-case ``expected`` string in cases.json IS the frozen declaration, and it is ENFORCED by
EXACT exception type-name equality (``type(exc).__name__ == declared``).  isinstance() must never
be used for that comparison: ModelRegistryError subclasses ValueError, so a declared "ValueError"
would silently pass under isinstance().

* a declaration that is missing, or is not a non-empty string, is an UNUSABLE frozen expectation:
  it yields rc=2 (no verdict) BEFORE any case can be judged, and that case is recorded as
  NOT_JUDGED_declaration_unusable - it is never counted as a mismatch;
* a USABLE declaration that does not hold yields rc=3: FAIL_declared_expectation_mismatch when the
  raised type is the target type, FAIL_wrong_exception_type when it is not;
* nothing raised at all is FAIL_not_rejected (a judged failure, rc=3) - not a declaration mismatch.

Observations (cases.json -> extra_observations) are measured and compared against
oracle.json -> observation_expected, and are printed, but they do NOT change the exit
code: they are design probes whose purpose is to record which contract convention the
implementation uses. Their comparison results are part of the evidence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys
import traceback

EXIT_PASS = 0
EXIT_HARNESS = 1
EXIT_NO_VERDICT = 2
EXIT_NEGATIVE = 3

TARGET_EXCEPTION = "ModelRegistryError"


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_mutation_value(spec):
    """Decode the frozen mutation encodings used by cases.json.

    ``{"__float__": "nan"}`` -> float('nan');  ``{"__bool__": true}`` -> True.
    Anything else is returned unchanged, so a real list stays a real list.
    """
    if isinstance(spec, dict):
        if "__float__" in spec:
            return float(spec["__float__"])
        if "__bool__" in spec or "__bool__first__" in spec:
            return True
    return spec


def apply_case(base, case):
    kind = case["kind"]
    if kind == "set_driver_element":
        base["drivers"][case["driver"]][case["index"]] = build_mutation_value(case["value"])
    elif kind == "set_driver":
        base["drivers"][case["driver"]] = build_mutation_value(case["value"])
    elif kind == "delete_driver":
        del base["drivers"][case["driver"]]
    elif kind == "add_driver":
        base["drivers"][case["driver"]] = build_mutation_value(case["value"])
    elif kind == "set_driver_multi":
        for driver, value in case["value"].items():
            base["drivers"][driver] = build_mutation_value(value)
    elif kind == "set_base_revenue":
        base["base_revenue"] = build_mutation_value(case["value"])
    elif kind == "set_years":
        value = case["value"]
        if isinstance(value, dict) and "__bool__first__" in value:
            new_years = list(base["years"])
            new_years[0] = True
            base["years"] = new_years
        else:
            base["years"] = copy.deepcopy(value)
    else:
        raise ValueError("unknown mutation kind: " + kind)
    return base


def call_product(model_registry, spec):
    return model_registry.calculate_registered_model(
        model_id=spec["model_id"], base_revenue=spec["base_revenue"],
        drivers=spec["drivers"], years=spec["years"])


def value_within(actual, expected, tolerance):
    try:
        return math.isfinite(actual) and abs(actual - expected) <= tolerance
    except TypeError:
        return False


def structure_report(value, years):
    """Structural fidelity of the returned path (not a numeric comparison)."""
    report = {
        "container_type": type(value).__name__,
        "is_builtin_list": isinstance(value, list),
        "length": len(value) if isinstance(value, (list, tuple)) else None,
        "years_length": len(years),
        "length_equals_years": (isinstance(value, (list, tuple)) and len(value) == len(years)),
        "element_types": sorted({type(v).__name__ for v in value}) if isinstance(value, (list, tuple)) else None,
        "element_type_set": sorted({type(v).__name__ for v in value}) if isinstance(value, (list, tuple)) else None,
        "all_elements_float": (isinstance(value, (list, tuple))
                               and all(isinstance(v, float) for v in value)),
        "all_elements_finite": (isinstance(value, (list, tuple))
                                and all(isinstance(v, float) and math.isfinite(v) for v in value)),
        "year_field_echo": False,
        "note": ("the product contract returns a bare list[float] positionally aligned with "
                 "years; there are no named output fields, so the 'field set' check is the "
                 "element type set {float} plus the container type plus the length/order check"),
    }
    report["ok"] = bool(report["is_builtin_list"] and report["length_equals_years"]
                        and report["all_elements_float"] and report["all_elements_finite"])
    return report


def contract_report(observed, expected):
    checks = {}
    for key in ("formula", "required", "optional", "dimensions"):
        obs = observed.get(key)
        exp = expected.get(key)
        checks[key] = {"observed": obs, "expected": exp, "ok": obs == exp}
    checks["ok"] = all(v["ok"] for v in checks.values() if isinstance(v, dict))
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--out", required=True, help="run_result.json path")
    parser.add_argument("--formula-out", default=None, help="formula_result.json path")
    parser.add_argument("--negative-out", default=None, help="negative_results.json path")
    parser.add_argument("--stdout-out", default=None)
    parser.add_argument("--stderr-out", default=None)
    args = parser.parse_args()

    lines: list[str] = []
    result: dict = {"card_id": args.card, "code_root": args.code_root, "harness_errors": [],
                    "observations": [], "negatives": [], "positive": {},
                    "continuity_positive": {}, "defaults": {}, "registry_metadata": {}}

    def emit(line=""):
        lines.append(line)

    try:
        evidence = os.path.join(args.attempt, "evidence", args.card)
        input_doc = load_json(os.path.join(evidence, "input.json"))
        oracle_doc = load_json(os.path.join(evidence, "oracle.json"))
        cases_doc = load_json(os.path.join(evidence, "cases.json"))
    except Exception as exc:  # noqa: BLE001
        emit("HARNESS ERROR while loading frozen evidence: %s: %s" % (type(exc).__name__, exc))
        result["harness_errors"].append({"stage": "load_evidence",
                                        "error": type(exc).__name__, "message": str(exc),
                                        "traceback": traceback.format_exc()})
        result["exit_code_semantics"] = {
            "verdict": "harness_error", "exit_code": EXIT_HARNESS,
            "fidelity_ok": False, "negative_ok": False,
            "reason": "frozen evidence could not be read",
        }
        _finish(args, result, lines, EXIT_HARNESS)
        return EXIT_HARNESS

    result["model_id"] = oracle_doc.get("model_id")
    result["entry_point"] = "model_registry.calculate_registered_model(**input)"
    result["frozen_input_hashes"] = {}
    for name in ("input.json", "oracle.json", "cases.json"):
        with open(os.path.join(evidence, name), "rb") as handle:
            result["frozen_input_hashes"]["evidence/%s/%s" % (args.card, name)] = \
                hashlib.sha256(handle.read()).hexdigest()

    sys.path.insert(0, args.code_root)
    try:
        import model_registry  # noqa: E402
    except Exception as exc:  # noqa: BLE001
        emit("HARNESS ERROR while importing the product from --code-root: %s: %s"
             % (type(exc).__name__, exc))
        result["harness_errors"].append({"stage": "import_product",
                                        "error": type(exc).__name__, "message": str(exc),
                                        "traceback": traceback.format_exc()})
        result["exit_code_semantics"] = {
            "verdict": "harness_error", "exit_code": EXIT_HARNESS,
            "fidelity_ok": False, "negative_ok": False,
            "reason": "product import failed",
        }
        _finish(args, result, lines, EXIT_HARNESS)
        return EXIT_HARNESS

    result["model_registry_file"] = model_registry.__file__
    result["target_exception"] = TARGET_EXCEPTION

    # ---------------- registry contract ----------------
    observed_contract = {}
    try:
        spec = model_registry.MODEL_REGISTRY[oracle_doc["model_id"]]
        observed_contract = {
            "formula": spec.formula,
            "required": sorted(spec.required),
            "optional": sorted(spec.optional),
            "dimensions": dict(spec.dimensions),
        }
        result["registry_metadata"] = {
            "model_id": spec.model_id,
            "required": list(spec.required),
            "optional": list(spec.optional),
            "declared_defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
            "dimensions": dict(spec.dimensions),
            "ratio_drivers": sorted(spec.ratio_drivers),
            "explicit_driver_bounds": {
                k: [None if b[0] is None else float(b[0]),
                    None if b[1] is None else float(b[1])]
                for k, b in dict(spec.driver_bounds).items()},
            "formula": spec.formula,
        }
    except Exception as exc:  # noqa: BLE001
        result["registry_metadata"] = {"error": type(exc).__name__ + ": " + str(exc)}

    frozen_contract = oracle_doc.get("contract") or {}
    if not frozen_contract:
        result["harness_errors"].append({"stage": "contract", "error": "MissingExpectation",
                                        "message": "oracle.json has no frozen contract block"})
    contract_check = contract_report(observed_contract, frozen_contract)
    result["contract_check"] = contract_check

    # ---------------- positive ----------------
    positive_expected = (oracle_doc.get("positive") or {}).get("expected_float")
    positive_tol = (oracle_doc.get("positive") or {}).get("tolerances")
    positive_years = (oracle_doc.get("positive") or {}).get("years")
    input_years = input_doc["positive"]["years"]
    missing_positive = positive_expected is None or positive_tol is None or positive_years is None

    spec_in = copy.deepcopy(input_doc["positive"])
    try:
        actual = call_product(model_registry, spec_in)
        result["positive"] = {"raised": None, "actual": [float(v) for v in actual],
                              "actual_repr": [repr(float(v)) for v in actual],
                              "length": len(actual),
                              "structure": structure_report(actual, input_years)}
    except Exception as exc:  # noqa: BLE001
        result["positive"] = {"raised": type(exc).__name__, "message": str(exc),
                              "traceback": traceback.format_exc()}

    positive_ok = False
    per_value_checks = []
    if missing_positive:
        result["positive"]["expected_missing"] = True
    elif result["positive"].get("raised") is None:
        act = result["positive"]["actual"]
        if len(act) == len(positive_expected):
            for i, (a, e, t) in enumerate(zip(act, positive_expected, positive_tol)):
                per_value_checks.append({"index": i, "year": positive_years[i], "actual": a,
                                         "expected": e, "tolerance": t,
                                         "abs_diff": abs(a - e),
                                         "ok": value_within(a, e, t)})
        result["per_value_checks"] = per_value_checks
        positive_ok = (result["positive"]["structure"]["ok"]
                       and len(act) == len(positive_expected)
                       and bool(per_value_checks)
                       and all(c["ok"] for c in per_value_checks))
    result["length_and_year_check"] = {
        "oracle_years": positive_years,
        "input_years": input_years,
        "years_match": positive_years == input_years,
        "oracle_length": None if positive_expected is None else len(positive_expected),
        "input_years_length": len(input_years),
        "lengths_match": (positive_expected is not None
                          and len(positive_expected) == len(input_years)),
    }
    result["fidelity_checks"] = {
        "missing_expected": missing_positive,
        "positive_structure_ok": bool(result["positive"].get("structure", {}).get("ok")),
        "positive_values_ok": positive_ok,
        "contract_ok": bool(contract_check.get("ok")),
        "years_match": result["length_and_year_check"]["years_match"],
        "lengths_match": result["length_and_year_check"]["lengths_match"],
    }

    # ---------------- continuity positive (runs BEFORE the break patch) ----------------
    cspec = copy.deepcopy(input_doc["continuity_positive"])
    cexp = (oracle_doc.get("continuity_positive") or {}).get("expected_float")
    ctol = (oracle_doc.get("continuity_positive") or {}).get("tolerances")
    missing_continuity = cexp is None or ctol is None
    try:
        cactual = call_product(model_registry, cspec)
        cactual_f = [float(v) for v in cactual]
        cchecks = []
        if not missing_continuity and len(cactual_f) == len(cexp):
            cchecks = [{"index": i, "actual": cactual_f[i], "expected": cexp[i],
                        "tolerance": ctol[i], "abs_diff": abs(cactual_f[i] - cexp[i]),
                        "ok": value_within(cactual_f[i], cexp[i], ctol[i])}
                       for i in range(len(cexp))]
        result["continuity_positive"] = {
            "raised": None, "actual": cactual_f, "expected": cexp,
            "per_value_checks": cchecks,
            "structure": structure_report(cactual, input_doc["continuity_positive"]["years"]),
            "ok": (bool(cchecks) and all(c["ok"] for c in cchecks)
                   and len(cactual_f) == len(cexp or [])),
            "ran_before_negative_patch": True,
        }
    except Exception as exc:  # noqa: BLE001
        result["continuity_positive"] = {"raised": type(exc).__name__, "message": str(exc),
                                         "traceback": traceback.format_exc(), "ok": False,
                                         "ran_before_negative_patch": True}
    if missing_continuity:
        result["continuity_positive"]["expected_missing"] = True

    # ---------------- defaults case ----------------
    dexp = oracle_doc.get("defaults_expected_float")
    dtol = (oracle_doc.get("defaults") or {}).get("tolerances")
    missing_defaults = dexp is None or dtol is None
    dspec = copy.deepcopy(input_doc["defaults"])
    try:
        dactual = call_product(model_registry, dspec)
        dactual_f = [float(v) for v in dactual]
        dchecks = []
        if not missing_defaults and len(dactual_f) == len(dexp):
            dchecks = [{"index": i, "actual": dactual_f[i], "expected": dexp[i],
                        "tolerance": dtol[i], "abs_diff": abs(dactual_f[i] - dexp[i]),
                        "ok": value_within(dactual_f[i], dexp[i], dtol[i])}
                       for i in range(len(dexp))]
        result["defaults"] = {
            "raised": None, "actual": dactual_f, "expected": dexp,
            "per_value_checks": dchecks,
            "structure": structure_report(dactual, input_doc["defaults"]["years"]),
            "ok": bool(dchecks) and all(c["ok"] for c in dchecks),
        }
    except Exception as exc:  # noqa: BLE001
        result["defaults"] = {"raised": type(exc).__name__, "message": str(exc),
                              "traceback": traceback.format_exc(), "ok": False}
    if missing_defaults:
        result["defaults"]["expected_missing"] = True
    result["defaults_ok"] = bool(result["defaults"].get("ok"))

    # ---------------- observations (measured; NOT part of the exit code) ----------------
    obs_expected = oracle_doc.get("observation_expected") or {}
    for obs in cases_doc.get("extra_observations", []):
        entry = {"id": obs["id"], "kind": obs.get("kind", "input_replay"),
                 "driver": obs.get("driver"), "base_input": obs.get("base_input"),
                 "why": obs.get("why", ""), "gating": False}
        try:
            if obs.get("kind") == "input_replay":
                mutated = copy.deepcopy(input_doc[obs["input"]])
            else:
                mutated = apply_case(copy.deepcopy(input_doc[obs.get("base_input", "positive")]), obs)
                for driver, value in (obs.get("also_set_driver") or {}).items():
                    mutated["drivers"][driver] = copy.deepcopy(value)
            entry["mutated_drivers_repr"] = (repr(mutated["drivers"])[:400]
                                             + " years=" + repr(mutated["years"])
                                             + " base=" + repr(mutated["base_revenue"]))
            value = call_product(model_registry, mutated)
            entry["raised"] = None
            entry["actual"] = [float(v) for v in value]
            if obs.get("compare_to"):
                entry["compared_to"] = obs["compare_to"]
                entry["compared_actual"] = result[obs["compare_to"]].get("actual")
                entry["matches_compared"] = entry["actual"] == entry["compared_actual"]
                if obs.get("expect_equal") is not None:
                    entry["expected_equal"] = obs["expect_equal"]
                    entry["matches_expected_relation"] = (
                        entry["matches_compared"] == bool(obs["expect_equal"]))
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
        exp = obs_expected.get(obs["id"])
        entry["expectation_recorded"] = exp
        if exp:
            if "expected_float" in exp:
                entry["matches_expected"] = (
                    entry.get("raised") is None
                    and len(entry.get("actual", [])) == len(exp["expected_float"])
                    and all(value_within(a, e, 1e-9 * max(1.0, abs(e)))
                            for a, e in zip(entry["actual"], exp["expected_float"])))
            elif "expected_raised" in exp:
                entry["matches_expected"] = entry.get("raised") == exp["expected_raised"]
        result["observations"].append(entry)

    # ---------------- negatives ----------------
    # Each case carries a DECLARED expectation in the frozen cases.json.  The runner must ENFORCE
    # that declaration, not merely "some ModelRegistryError was raised": the declared value is
    # compared against the exception's EXACT type name.  isinstance() must NOT be used for that
    # comparison, because ModelRegistryError subclasses ValueError, so a declared "ValueError"
    # would silently pass under isinstance().
    #
    # Precedence (REM-21 / T1-8, propagated from the M17-M20 reference runner): a declaration that
    # is missing or is not a non-empty string is an UNUSABLE frozen expectation => rc=2 (no
    # verdict), decided BEFORE any case is judged; that case is NOT_JUDGED (neither a mismatch nor
    # a rejection failure).  Only a USABLE declaration that does not hold can produce rc=3.
    unusable_declared = [c.get("id") for c in cases_doc["cases"]
                         if not (isinstance(c.get("expected"), str) and c["expected"].strip())]
    cases_declared_ok = not unusable_declared
    result["cases_json_declared_expectations_usable"] = cases_declared_ok
    result["cases_json_unusable_declared_expectations"] = unusable_declared

    for case in cases_doc["cases"]:
        base_key = case.get("base_input", "positive")
        base = copy.deepcopy(input_doc[base_key])
        # `declared` is the raw frozen declaration; the pre-existing "expected" key is kept as-is
        # for every downstream evidence reader, and "declared" is written alongside it.
        declared = case.get("expected")
        declared_usable = isinstance(declared, str) and bool(declared.strip())
        entry = {"id": case["id"], "kind": case["kind"], "why": case["why"],
                 "expected": declared, "declared": declared, "base_input": base_key,
                 "guard_hint": case.get("guard_hint", ""),
                 "fresh_deepcopy": True}
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = (repr(mutated["drivers"])[:400]
                                           + " years=" + repr(mutated["years"])
                                           + " base=" + repr(mutated["base_revenue"]))
            call_product(model_registry, mutated)
            entry["raised"] = None
            entry["declared_expectation_comparison"] = (
                "no exception was raised; declared %r (exact exception type name comparison, "
                "NOT isinstance)" % (declared,))
            if not declared_usable:
                # Unusable declaration: no verdict can be issued for this case (rc=2), and it is
                # explicitly NOT a declared-expectation mismatch.
                entry["declared_expectation_ok"] = None
                entry["declared_expectation_mismatch"] = False
                entry["declared_expectation_not_met"] = None
                entry["judged"] = False
                entry["expectation_not_met_reason"] = (
                    "declared expectation is unusable (missing or not a non-empty string), so the "
                    "case cannot be judged against it")
                entry["verdict"] = "NOT_JUDGED_declaration_unusable"
            else:
                entry["declared_expectation_ok"] = False
                entry["declared_expectation_mismatch"] = False
                entry["declared_expectation_not_met"] = True
                entry["judged"] = True
                entry["expectation_not_met_reason"] = "no exception was raised"
                entry["verdict"] = "FAIL_not_rejected"
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
            is_target = isinstance(exc, model_registry.ModelRegistryError)
            is_import_or_file = isinstance(exc, (ImportError, ModuleNotFoundError,
                                                 FileNotFoundError, OSError))
            entry["is_target_type"] = is_target
            entry["is_import_or_file_error"] = is_import_or_file
            # The pre-existing comparison field is REUSED as the declaration comparison; it is
            # never recomputed a second time.
            entry["raised_matches_expected_name"] = (entry["raised"] == declared)
            entry["declared_expectation_comparison"] = (
                "raised exact type name %r vs declared %r (exact-name comparison, not isinstance)"
                % (entry["raised"], declared))
            if not declared_usable:
                # Unusable declaration: this case is NOT JUDGED - it is neither a mismatch nor a
                # rejection failure (the taxonomy stays mutually exclusive; rc=2, not rc=3).
                entry["declared_expectation_ok"] = None
                entry["declared_expectation_mismatch"] = False
                entry["declared_expectation_not_met"] = None
                entry["judged"] = False
                entry["expectation_not_met_reason"] = (
                    "declared expectation is unusable (missing or not a non-empty string), so the "
                    "case cannot be judged against it")
                entry["verdict"] = "NOT_JUDGED_declaration_unusable"
            else:
                declared_ok = entry["raised_matches_expected_name"]
                entry["declared_expectation_ok"] = declared_ok
                entry["declared_expectation_mismatch"] = not declared_ok
                entry["declared_expectation_not_met"] = not declared_ok
                entry["judged"] = True
                if not declared_ok:
                    entry["expectation_not_met_reason"] = (
                        "raised exact type name %r != declared %r"
                        % (entry["raised"], declared))
                if not is_target:
                    entry["verdict"] = ("FAIL_import_or_file_error" if is_import_or_file
                                        else "FAIL_wrong_exception_type")
                elif not declared_ok:
                    entry["verdict"] = "FAIL_declared_expectation_mismatch"
                else:
                    entry["verdict"] = "PASS_rejected"
        result["negatives"].append(entry)

    not_judged_ids = [e["id"] for e in result["negatives"]
                      if e["verdict"] == "NOT_JUDGED_declaration_unusable"]
    judged_failed = [e["id"] for e in result["negatives"]
                     if e["verdict"] not in ("PASS_rejected", "NOT_JUDGED_declaration_unusable")]
    mismatch_ids = [e["id"] for e in result["negatives"] if e.get("declared_expectation_mismatch")]
    not_rejected_ids = [e["id"] for e in result["negatives"] if e["raised"] is None]
    result["negative_summary"] = {
        "total": len(result["negatives"]),
        "passed": sum(1 for e in result["negatives"] if e["verdict"] == "PASS_rejected"),
        "failed": judged_failed,
        "not_judged": not_judged_ids,
        "import_or_file_errors": [e["id"] for e in result["negatives"]
                                  if e.get("is_import_or_file_error")],
        "target_exception": "model_registry.ModelRegistryError",
        "declared_expectations_in_cases_json": sorted(
            {str(c.get("expected")) for c in cases_doc["cases"]}),
        "declared_expectation_comparison": ("exact exception type name == cases.json's per-case "
                                            "'expected' string (NOT isinstance)"),
        "declared_expectations_enforced": True,
        "declared_expectations_usable": cases_declared_ok,
        "verdicts_are_mutually_exclusive": True,
        "classification_is_mutually_exclusive": True,
        "import_or_file_errors_never_pass": True,
    }
    result["negative_counts"] = {
        "total": len(result["negatives"]),
        "rejected_with_ModelRegistryError": sum(
            1 for e in result["negatives"] if e.get("is_target_type")),
        "not_rejected": sum(1 for e in result["negatives"] if e["raised"] is None),
        "wrong_exception_type": sum(1 for e in result["negatives"]
                                    if e.get("raised") is not None
                                    and not e.get("is_target_type")
                                    and not e.get("is_import_or_file_error")),
        "import_or_file_error": sum(1 for e in result["negatives"]
                                    if e.get("is_import_or_file_error")),
        "declared_expectation_mismatch": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_mismatch")),
        "declared_expectation_not_met": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_not_met")),
        "declared_expectation_missing_in_cases_json": len(unusable_declared),
    }

    # ---------------- verdict ----------------
    harness_error = bool(result["harness_errors"]) or any(
        e.get("is_import_or_file_error") for e in result["negatives"])
    negatives_ok = result["negative_summary"]["passed"] == result["negative_summary"]["total"]
    fidelity_ok = (positive_ok and bool(contract_check.get("ok"))
                   and result["length_and_year_check"]["years_match"]
                   and result["length_and_year_check"]["lengths_match"]
                   and bool(result["continuity_positive"].get("ok"))
                   and bool(result["defaults"].get("ok")))
    if missing_positive or missing_continuity or missing_defaults:
        fidelity_ok = False

    verdict_reasons = []
    if not cases_declared_ok:
        verdict_reasons.append("cases_json_declared_expectation_missing:"
                               + ",".join(unusable_declared))
    if not fidelity_ok:
        verdict_reasons.append("output_fidelity_mismatch")
    if not_rejected_ids:
        verdict_reasons.append("negatives_not_rejected:" + ",".join(not_rejected_ids))
    if mismatch_ids:
        verdict_reasons.append("declared_expectation_mismatch:" + ",".join(mismatch_ids))
    if not_judged_ids:
        verdict_reasons.append("declaration_unusable_not_judged:" + ",".join(not_judged_ids))

    # rc=2 (no verdict) is evaluated BEFORE case judging when the frozen declaration itself is
    # missing/unusable (T1-8 prereq 3); rc=3 is issued only when a judgement WAS possible and did
    # not hold.  A NOT_JUDGED_declaration_unusable case can therefore never produce rc=3 by itself.
    if harness_error:
        exit_code, verdict = EXIT_HARNESS, "harness_error"
    elif not cases_declared_ok or not fidelity_ok:
        exit_code, verdict = EXIT_NO_VERDICT, "no_verdict"
    elif not negatives_ok:
        exit_code, verdict = EXIT_NEGATIVE, "negative_failed"
    else:
        exit_code, verdict = EXIT_PASS, "pass"

    result["verdict"] = verdict
    result["exit_code"] = exit_code
    result["verdict_reasons"] = verdict_reasons

    result["exit_code_semantics"] = {
        "verdict": verdict,
        "exit_code": exit_code,
        "positive_ok": positive_ok,
        "contract_ok": bool(contract_check.get("ok")),
        "continuity_ok": bool(result["continuity_positive"].get("ok")),
        "defaults_ok": bool(result["defaults"].get("ok")),
        "fidelity_ok": fidelity_ok,
        "negatives_ok": negatives_ok,
        "harness_error": harness_error,
        "missing_expectations": {"positive": missing_positive,
                                 "continuity_positive": missing_continuity,
                                 "defaults": missing_defaults},
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "cases_json_unusable_declared_expectations": unusable_declared,
        "declared_expectation_mismatch_case_ids": mismatch_ids,
        "declared_expectation_not_met_case_ids": [e["id"] for e in result["negatives"]
                                                  if e.get("declared_expectation_not_met")],
        "not_rejected_case_ids": not_rejected_ids,
        "not_judged_case_ids": not_judged_ids,
        "verdict_reasons": verdict_reasons,
        "reason": (";".join(verdict_reasons) if verdict_reasons
                   else "every declaration was usable and held; all checks passed"),
        "reason_namespace": ("exclusive taxonomy: PASS_rejected | FAIL_not_rejected (nothing "
                             "raised) | FAIL_wrong_exception_type | FAIL_import_or_file_error | "
                             "FAIL_declared_expectation_mismatch | "
                             "NOT_JUDGED_declaration_unusable. FAIL_wrong_exception_type is a "
                             "SUBSET of declared_expectation_mismatch when the declaration is "
                             "usable; a NOT_JUDGED_declaration_unusable case is never a mismatch"),
        "precedence": "1 harness > 2 no-verdict/fidelity > 3 negative > 0 pass",
    }

    emit("card_id: %s" % args.card)
    emit("model_id: %s" % result.get("model_id"))
    emit("code_root: %s" % args.code_root)
    emit("model_registry_file: %s" % result.get("model_registry_file"))
    emit("registry formula: %s" % result.get("registry_metadata", {}).get("formula"))
    emit("registry required: %s" % result.get("registry_metadata", {}).get("required"))
    emit("registry optional: %s" % result.get("registry_metadata", {}).get("optional"))
    emit("registry declared_defaults: %s" % result.get("registry_metadata", {}).get("declared_defaults"))
    emit("registry ratio_drivers: %s" % result.get("registry_metadata", {}).get("ratio_drivers"))
    emit("registry explicit_driver_bounds: %s"
         % result.get("registry_metadata", {}).get("explicit_driver_bounds"))
    emit("contract_check ok: %s" % contract_check.get("ok"))
    for key in ("formula", "required", "optional", "dimensions"):
        sub = contract_check.get(key, {})
        emit("contract_check %s ok=%s observed=%s" % (key, sub.get("ok"), sub.get("observed")))
    emit("positive raised: %s" % result["positive"].get("raised"))
    emit("positive actual: %s" % result["positive"].get("actual"))
    emit("positive actual_repr: %s" % result["positive"].get("actual_repr"))
    emit("positive expected: %s" % positive_expected)
    emit("positive tolerance: %s" % positive_tol)
    emit("positive length: %s (years length %s, year direction %s)"
         % (result["positive"].get("length"), len(input_years), input_years))
    emit("positive structure: %s" % json.dumps(result["positive"].get("structure"), ensure_ascii=True))
    emit("per_value_checks: %s" % json.dumps(per_value_checks, ensure_ascii=True))
    emit("positive_ok: %s" % positive_ok)
    emit("continuity_positive raised: %s" % result["continuity_positive"].get("raised"))
    emit("continuity_positive actual: %s" % result["continuity_positive"].get("actual"))
    emit("continuity_positive expected: %s" % cexp)
    emit("continuity_positive ok: %s" % result["continuity_positive"].get("ok"))
    emit("defaults raised: %s" % result["defaults"].get("raised"))
    emit("defaults actual: %s" % result["defaults"].get("actual"))
    emit("defaults expected: %s" % dexp)
    emit("defaults ok: %s" % result["defaults"].get("ok"))
    for obs in result["observations"]:
        emit("observation: %s gating=%s raised=%s actual=%s expectation=%s matches_expected=%s "
             "matches_compared=%s expect_equal=%s matches_expected_relation=%s %s"
             % (obs["id"], obs["gating"], obs.get("raised"), obs.get("actual"),
                json.dumps(obs.get("expectation_recorded"), ensure_ascii=True),
                obs.get("matches_expected"), obs.get("matches_compared"),
                obs.get("expect_equal"), obs.get("matches_expected_relation"),
                obs.get("message", "")))
    for entry in result["negatives"]:
        emit("negative: %s verdict=%s raised=%s expected=%s - %s"
             % (entry["id"], entry["verdict"], entry.get("raised"), entry["expected"],
                entry.get("message", "")))
        emit("negative_declaration: %s declared=%s raised_matches_declared=%s judged=%s "
             "declared_expectation_ok=%s declared_expectation_mismatch=%s "
             "declared_expectation_not_met=%s comparison=%s"
             % (entry["id"], entry.get("declared"),
                entry.get("raised_matches_expected_name"), entry.get("judged"),
                entry.get("declared_expectation_ok"),
                entry.get("declared_expectation_mismatch"),
                entry.get("declared_expectation_not_met"),
                entry.get("declared_expectation_comparison")))
    emit("negative_summary: %s" % json.dumps(result["negative_summary"], ensure_ascii=True))
    emit("negative_counts: %s" % json.dumps(result["negative_counts"], ensure_ascii=True))
    emit("cases_json_declared_expectations_usable: %s" % cases_declared_ok)
    emit("fidelity_checks: %s" % json.dumps(result["fidelity_checks"], ensure_ascii=True))
    emit("verdict_reasons: %s" % json.dumps(verdict_reasons, ensure_ascii=True))
    emit("verdict: %s exit_code: %s" % (verdict, exit_code))

    _finish(args, result, lines, exit_code)
    return exit_code


def _finish(args, result, lines, exit_code):
    text = "\n".join(lines) + "\n"
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=1)
    if args.formula_out:
        formula = {k: result.get(k) for k in
                   ("card_id", "model_id", "code_root", "model_registry_file", "entry_point",
                    "target_exception", "registry_metadata", "contract_check", "positive",
                    "per_value_checks", "length_and_year_check", "fidelity_checks",
                    "continuity_positive", "defaults", "defaults_ok",
                    "exit_code_semantics", "harness_errors")}
        with open(args.formula_out, "w", encoding="utf-8") as handle:
            json.dump(formula, handle, ensure_ascii=False, indent=1)
    if args.negative_out:
        negatives = {k: result.get(k) for k in
                     ("card_id", "model_id", "entry_point", "target_exception",
                      "negatives", "negative_summary", "negative_counts", "observations",
                      "exit_code_semantics", "verdict", "exit_code", "verdict_reasons",
                      "cases_json_declared_expectations_usable",
                      "cases_json_unusable_declared_expectations", "harness_errors")}
        with open(args.negative_out, "w", encoding="utf-8") as handle:
            json.dump(negatives, handle, ensure_ascii=False, indent=1)
    if args.stdout_out:
        with open(args.stdout_out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    if args.stderr_out:
        with open(args.stderr_out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("")
    sys.stdout.write(text)
    sys.stdout.flush()


if __name__ == "__main__":
    raise SystemExit(main())
