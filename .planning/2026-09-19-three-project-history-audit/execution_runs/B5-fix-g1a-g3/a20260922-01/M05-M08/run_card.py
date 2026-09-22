"""Card-agnostic, verdict-carrying product runner for the M-card formula oracles.

Isolation contract
------------------
* The product scripts directory comes from --code-root, which MUST be the
  attempt-local isolated snapshot whose sha256 is recorded in source_manifest.json.
* The only product entry point invoked is ``calculate_registered_model(**spec)``.
* Expected values come exclusively from evidence/<CARD>/oracle.json, produced by
  scripts/oracle_<CARD>.py (stdlib only, which never imports the product).
* Every negative case gets a NEW deepcopy of the frozen base input, built in
  memory (never round-tripped through a JSON parser).

Exit codes (verdict-carrying; a bookkeeping-only rc=0 is not allowed)
--------------------------------------------------------------------
  0 = the positive path matched the independent oracle within tolerance AND the
      continuity positive passed AND every negative case was rejected with
      ModelRegistryError
  2 = harness/bookkeeping could not produce a verdict (e.g. the positive path
      raised, so there is nothing to compare, or cases.json's frozen per-case
      ``expected`` declaration is itself missing/unusable, which is decided
      BEFORE any case is judged and issues verdict "no_verdict")
  3 = the verdict is negative (positive mismatch, continuity failure, an
      unrejected negative, or a raised exception whose exact type name does not
      equal the case's declared ``expected``)

Per-case ``expected`` enforcement (REM-21 / B5, propagated from M17-M20)
-----------------------------------------------------------------------
``cases.json`` declares, per negative case, the bare exception type name the
product must raise (``"expected"``). The comparison is EXACT TYPE-NAME
EQUALITY, never ``isinstance()``: ``ModelRegistryError`` is a subclass of
``ValueError``, so a declared ``"ValueError"`` would silently pass an
``isinstance`` check. Precedence: a missing/unusable declaration is decided
BEFORE any case is judged and yields rc=2 (no verdict); such a case is
reported as ``NOT_JUDGED_declaration_unusable`` and is never counted as a
declaration mismatch.

The observation block (extra_observations) is deliberately NOT part of the exit
code: those entries are design observations whose expected value is sometimes
"no expectation asserted" (e.g. the M08 sign probes, which exist to record which
formula convention the implementation uses, not to pass or fail it).
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import traceback


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_mutation_value(spec):
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
        base["drivers"][case["driver"]] = copy.deepcopy(case["value"])
    elif kind == "delete_driver":
        del base["drivers"][case["driver"]]
    elif kind == "add_driver":
        base["drivers"][case["driver"]] = copy.deepcopy(case["value"])
    elif kind == "set_driver_multi":
        for driver, value in case["value"].items():
            base["drivers"][driver] = copy.deepcopy(value)
    elif kind == "set_base_revenue":
        base["base_revenue"] = copy.deepcopy(case["value"])
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


def within(values, expected):
    if len(values) != len(expected):
        return False
    return all(abs(a - e) <= 1e-9 * max(1.0, abs(e)) for a, e in zip(values, expected))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-result-out", default=None)
    args = parser.parse_args()

    evidence = os.path.join(args.attempt, "evidence", args.card)
    input_doc = load_json(os.path.join(evidence, "input.json"))
    oracle_doc = load_json(os.path.join(evidence, "oracle.json"))
    cases_doc = load_json(os.path.join(evidence, "cases.json"))

    # ---- frozen declaration precondition (REM-21 / B5), decided BEFORE judging ----
    # `expected` MUST be a bare exception type name (e.g. "ModelRegistryError").
    # Comparison is EXACT TYPE-NAME EQUALITY. isinstance() must NOT be used:
    # ModelRegistryError is a subclass of ValueError, so a declared "ValueError"
    # would silently pass under isinstance().
    unusable_declared = [c.get("id") for c in cases_doc["cases"]
                         if not (isinstance(c.get("expected"), str) and c["expected"].strip())]
    cases_declared_ok = not unusable_declared
    no_verdict_reason = ("cases_json_declared_expectation_missing:"
                         + ",".join(str(i) for i in unusable_declared)
                         if not cases_declared_ok else None)
    declared_expectations_cases_json = sorted(
        {c["expected"] for c in cases_doc["cases"]
         if isinstance(c.get("expected"), str) and c["expected"].strip()})

    sys.path.insert(0, args.code_root)
    import model_registry  # noqa: E402

    result = {
        "card_id": args.card,
        "model_id": oracle_doc["model_id"],
        "code_root": args.code_root,
        "model_registry_file": model_registry.__file__,
        "entry_point": "model_registry.calculate_registered_model(**input)",
        "registry_metadata": {},
        "positive": {},
        "continuity_positive": {},
        "defaults": {},
        "observations": [],
        "negatives": [],
        "tolerances_ok": None,
        "defaults_ok": None,
    }

    try:
        spec = model_registry.MODEL_REGISTRY[oracle_doc["model_id"]]
        result["registry_metadata"] = {
            "model_id": spec.model_id,
            "required": list(spec.required),
            "optional": list(spec.optional),
            "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
            "dimensions": dict(spec.dimensions),
            "ratio_drivers": sorted(spec.ratio_drivers),
            "driver_bounds": {k: [None if b[0] is None else b[0],
                                  None if b[1] is None else b[1]]
                              for k, b in dict(spec.driver_bounds).items()},
            "formula": spec.formula,
        }
    except Exception as exc:  # noqa: BLE001
        result["registry_metadata"] = {"error": type(exc).__name__ + ": " + str(exc)}

    # ---------------- positive ----------------
    spec_in = copy.deepcopy(input_doc["positive"])
    try:
        actual = call_product(model_registry, spec_in)
        result["positive"] = {"raised": None, "actual": [float(v) for v in actual],
                              "actual_repr": [repr(float(v)) for v in actual], "length": len(actual)}
    except Exception as exc:  # noqa: BLE001
        result["positive"] = {"raised": type(exc).__name__, "message": str(exc),
                              "traceback": traceback.format_exc()}

    if result["positive"].get("raised") is None:
        exp = oracle_doc["positive"]["expected_float"]
        tol = oracle_doc["positive"]["tolerances"]
        act = result["positive"]["actual"]
        checks = []
        if len(act) == len(exp):
            for i, (a, e, t) in enumerate(zip(act, exp, tol)):
                checks.append({"index": i, "year": oracle_doc["positive"]["years"][i],
                               "actual": a, "expected": e, "tolerance": t,
                               "abs_diff": abs(a - e), "ok": abs(a - e) <= t})
            result["length_ok"] = True
        else:
            result["length_ok"] = False
        result["per_value_checks"] = checks
        result["tolerances_ok"] = bool(checks) and all(c["ok"] for c in checks) and result["length_ok"]

    # ---------------- continuity positive ----------------
    cspec = copy.deepcopy(input_doc["continuity_positive"])
    try:
        cactual = call_product(model_registry, cspec)
        cexp = oracle_doc["continuity_positive"]["expected_float"]
        result["continuity_positive"] = {
            "raised": None, "actual": [float(v) for v in cactual], "expected": cexp,
            "ok": within([float(v) for v in cactual], cexp),
        }
    except Exception as exc:  # noqa: BLE001
        result["continuity_positive"] = {"raised": type(exc).__name__, "message": str(exc),
                                         "traceback": traceback.format_exc(), "ok": False}

    # ---------------- defaults case ----------------
    dspec = copy.deepcopy(input_doc["defaults"])
    try:
        dactual = call_product(model_registry, dspec)
        dexp = oracle_doc["defaults_expected_float"]
        result["defaults"] = {
            "raised": None, "actual": [float(v) for v in dactual], "expected": dexp,
            "ok": within([float(v) for v in dactual], dexp),
        }
    except Exception as exc:  # noqa: BLE001
        result["defaults"] = {"raised": type(exc).__name__, "message": str(exc),
                              "traceback": traceback.format_exc(), "ok": False}
    result["defaults_ok"] = bool(result["defaults"].get("ok"))

    # ---------------- observations (NOT part of the exit code) ----------------
    obs_expected = oracle_doc.get("observation_expected") or {}
    for obs in cases_doc.get("extra_observations", []):
        entry = {"id": obs["id"], "expectation": obs.get("expectation"),
                 "kind": obs.get("kind", "input_replay"), "why": obs.get("why", "")}
        try:
            if obs.get("kind") == "input_replay":
                mutated = copy.deepcopy(input_doc[obs["input"]])
            else:
                mutated = apply_case(copy.deepcopy(input_doc[obs.get("base_input", "positive")]), obs)
                for driver, value in (obs.get("also_set_driver") or {}).items():
                    mutated["drivers"][driver] = copy.deepcopy(value)
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
            if obs["id"] in obs_expected:
                entry["expected"] = obs_expected[obs["id"]]["expected_float"]
                entry["matches_expected"] = within(entry["actual"], entry["expected"])
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
        result["observations"].append(entry)

    # ---------------- negatives ----------------
    for case in cases_doc["cases"]:
        base_key = case.get("base_input", "positive")
        base = copy.deepcopy(input_doc[base_key])
        declared = case.get("expected")  # raw declaration, may be missing/None
        entry = {"id": case["id"], "kind": case["kind"], "why": case["why"],
                 "expected": declared, "declared": declared, "base_input": base_key}
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = (repr(mutated["drivers"])[:400]
                                           + " years=" + repr(mutated["years"])
                                           + " base=" + repr(mutated["base_revenue"]))
            call_product(model_registry, mutated)
            entry["raised"] = None
            entry["declared_expectation_ok"] = None
            entry["declared_expectation_mismatch"] = False
            entry["declared_expectation_not_met"] = None
            entry["declared_expectation_comparison"] = (
                "nothing raised; cases.json declared " + repr(declared))
            entry["judged"] = True
            entry["verdict"] = "FAIL_not_rejected"
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
            is_target = isinstance(exc, model_registry.ModelRegistryError)
            is_import_or_file = isinstance(exc, (ImportError, ModuleNotFoundError, FileNotFoundError))
            entry["is_target_type"] = is_target
            entry["is_import_or_file_error"] = is_import_or_file
            declared_usable = isinstance(declared, str) and bool(declared.strip())
            if not declared_usable:
                # No verdict possible for this case: the DECLARATION is unusable,
                # so there is nothing to compare against. NOT a mismatch.
                entry["declared_expectation_ok"] = None
                entry["declared_expectation_mismatch"] = False
                entry["declared_expectation_not_met"] = None
                entry["declared_expectation_comparison"] = (
                    "declaration unusable (cases.json 'expected'=" + repr(declared)
                    + "); raised=" + entry["raised"] + " - not compared")
                entry["judged"] = False
                entry["verdict"] = "NOT_JUDGED_declaration_unusable"
            else:
                declared_ok = (entry["raised"] == declared)  # exact type-name equality
                entry["declared_expectation_ok"] = declared_ok
                entry["declared_expectation_mismatch"] = not declared_ok
                entry["declared_expectation_not_met"] = not is_target
                entry["declared_expectation_comparison"] = (
                    "raised=" + entry["raised"] + " vs declared=" + repr(declared)
                    + " (exact type name; NOT isinstance)")
                entry["judged"] = True
                if not is_target:
                    entry["verdict"] = "FAIL_wrong_exception_type"
                elif not declared_ok:
                    entry["verdict"] = "FAIL_declared_expectation_mismatch"
                else:
                    entry["verdict"] = "PASS_rejected"
        result["negatives"].append(entry)

    result["negative_counts"] = {
        "declared_expectation_mismatch": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_mismatch") is True),
        "declared_expectation_not_met": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_not_met") is True),
        "declared_expectation_missing_in_cases_json": len(unusable_declared),
    }
    result["negative_summary"] = {
        "total": len(result["negatives"]),
        "passed": sum(1 for e in result["negatives"] if e["verdict"] == "PASS_rejected"),
        "failed": [e["id"] for e in result["negatives"] if e["verdict"] != "PASS_rejected"],
        "declared_expectations_in_cases_json": declared_expectations_cases_json,
        "declared_expectation_comparison": (
            "exact exception type name == cases.json's per-case 'expected' string "
            "(NOT isinstance)"),
        "declared_expectations_enforced": True,
        "not_judged": [e["id"] for e in result["negatives"] if not e.get("judged")],
        "judged": sum(1 for e in result["negatives"] if e.get("judged")),
    }

    def dump(path):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=1)

    dump(args.out)

    print("code_root:", result["code_root"])
    print("model_registry_file:", result["model_registry_file"])
    print("registry formula:", result["registry_metadata"].get("formula"))
    print("registry required:", result["registry_metadata"].get("required"))
    print("registry optional:", result["registry_metadata"].get("optional"))
    print("registry defaults:", result["registry_metadata"].get("defaults"))
    print("registry driver_bounds:", result["registry_metadata"].get("driver_bounds"))
    print("positive raised:", result["positive"].get("raised"))
    print("positive actual:", result["positive"].get("actual"))
    print("positive expected:", oracle_doc["positive"]["expected_float"])
    print("tolerances_ok:", result.get("tolerances_ok"))
    print("continuity_positive ok:", result["continuity_positive"].get("ok"))
    print("defaults ok:", result.get("defaults_ok"), "actual:", result["defaults"].get("actual"),
          "expected:", result["defaults"].get("expected"))
    for obs in result["observations"]:
        print("observation:", obs["id"], "raised=", obs.get("raised"),
              "actual=", obs.get("actual"),
              "matches_compared=", obs.get("matches_compared"),
              "expect_equal=", obs.get("expect_equal"),
              "matches_expected_relation=", obs.get("matches_expected_relation"),
              "matches_expected=", obs.get("matches_expected"),
              obs.get("message", ""))
    for entry in result["negatives"]:
        print("negative:", entry["id"], entry["verdict"], entry.get("raised"),
              "-", entry.get("message", ""))
    print("negative summary:", result["negative_summary"])
    print("negative counts:", result["negative_counts"])
    print("declared expectations enforced:", result["negative_summary"]["declared_expectations_enforced"],
          "cases_json_declared_expectations_usable:", cases_declared_ok)
    if no_verdict_reason:
        print("no_verdict reason:", no_verdict_reason)

    # Precedence: an unusable frozen declaration is decided BEFORE any case judging.
    harness_incomplete = result["positive"].get("raised") is not None
    # A NOT_JUDGED case (unusable declaration) is not a case judgement, so it must
    # never, by itself, be able to produce rc=3.
    negatives_ok = all(e["verdict"] == "PASS_rejected"
                       for e in result["negatives"] if e.get("judged"))
    positive_ok = bool(result.get("tolerances_ok"))
    continuity_ok = bool(result["continuity_positive"].get("ok"))
    if not cases_declared_ok or harness_incomplete:
        verdict = "no_verdict"
        exit_code = 2
    elif positive_ok and negatives_ok and continuity_ok:
        verdict = "pass"
        exit_code = 0
    else:
        verdict = "fail"
        exit_code = 3
    result["no_verdict_reason"] = no_verdict_reason
    result["exit_code_semantics"] = {
        "harness_incomplete": harness_incomplete,
        "positive_ok": positive_ok,
        "continuity_ok": continuity_ok,
        "negatives_ok": negatives_ok,
        "defaults_ok_not_gating": result.get("defaults_ok"),
        "verdict": verdict,
        "exit_code": exit_code,
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "declared_expectation_mismatch_case_ids": [
            e["id"] for e in result["negatives"]
            if e.get("declared_expectation_mismatch") is True],
        "declared_expectation_not_met_case_ids": [
            e["id"] for e in result["negatives"]
            if e.get("declared_expectation_not_met") is True],
        "declaration_unusable_case_ids": list(unusable_declared),
        "reason_namespace": (
            "FAIL_wrong_exception_type is a SUBSET of declared_expectation_mismatch "
            "when the declaration is usable; NOT_JUDGED_declaration_unusable is an "
            "unusable-declaration outcome (rc=2, no verdict) and is NOT a mismatch "
            "and NOT part of declared_expectation_mismatch_case_ids."),
    }
    dump(args.out)
    if args.run_result_out:
        dump(args.run_result_out)
    print("verdict:", verdict, "exit_code:", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
