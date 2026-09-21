"""Card-agnostic, verdict-carrying product runner for the M-card formula oracles.

Isolation contract
-----------------
* The product scripts directory comes from --code-root, which MUST be the
  attempt-local isolated snapshot whose sha256 is recorded in source_manifest.json.
* The only product entry point invoked is ``calculate_registered_model(**spec)``.
* Expected values come exclusively from evidence/<CARD>/oracle.json and
  evidence/<CARD>/cases.json, produced by scripts/oracle_<CARD>.py (stdlib only,
  which never imports the product).
* Every negative case gets a NEW deepcopy of the frozen base input, built in
  memory (never round-tripped through a JSON parser).

Frozen-assertion contract for negatives (revision r2, review item P2-1)
----------------------------------------------------------------------
A negative case is a PASS only when ALL of the following hold:

  1. an instance of ``ModelRegistryError`` was raised (an ImportError or a file
     error is a FAIL, never a pass);
  2. the raised type's NAME equals the case's frozen ``expected`` field, i.e. the
     runner actually CHECKS that field instead of only copying it into the result.
     A case whose ``expected`` was edited to e.g. "ValueError" therefore FAILS with
     FAIL_expected_type_mismatch, which makes the assertion falsifiable by mutation
     (probe F of scripts/selfcheck_mutations.py);
  3. when the case carries ``expect_message_contains``, the refusal MESSAGE must
     contain that substring, so a length or lookup guard cannot stand in for the
     value-domain or bridge guard that the case is meant to exercise.

Frozen-declaration contract for negatives (revision r3, batch M21-M24)
----------------------------------------------------------------------
The comparison in (2) is EXACT TYPE-NAME EQUALITY between the raised exception's
``type(exc).__name__`` and the case's frozen ``expected`` string. ``isinstance()``
must NOT be used: ``ModelRegistryError`` subclasses ``ValueError``, so a case whose
``expected`` was edited to ``"ValueError"`` would silently pass under isinstance().
That exact-name comparison now GATES the verdict and the exit code instead of being
recorded and ignored:

* the comparison is evaluated across the WHOLE frozen case list BEFORE any case is
  judged. If any case's ``expected`` is absent or not a non-empty string, the run
  cannot be judged at all: exit code 2, ``verdict = "no_verdict"`` and reason
  ``cases_json_declared_expectation_missing:<ids>``, where ``<ids>`` is the
  comma-joined list of unusable case ids. Such a case is NOT counted as a mismatch.
* otherwise a case whose raised type NAME differs from its frozen ``expected`` is
  judged and FAILS with ``FAIL_expected_type_mismatch`` / ``judged = True``, which
  is what makes the leftover rc=0 "fabricated green" impossible.
* precedence: the unusable-declaration check (exit 2) is evaluated BEFORE case
  judging and therefore wins over a mismatch (exit 3).

Exit codes (verdict-carrying; a bookkeeping-only rc=0 is not allowed)
--------------------------------------------------------------------
  0 = the positive path matched the independent oracle within tolerance AND the
      continuity positive passed AND every negative case satisfied 1-3 above
  2 = NO VERDICT, issued BEFORE any case can be judged: the frozen declaration
      itself is missing/unusable (reason
      "cases_json_declared_expectation_missing:<ids>", verdict "no_verdict"), or
      the positive path raised so there is nothing to compare
  3 = a judgement WAS possible and did not hold (positive mismatch, continuity
      failure, an unrejected negative, a declared-expectation mismatch, or a
      message mismatch)

Reason namespace: ``FAIL_expected_type_mismatch`` is a SUBSET of
``declared_expectation_mismatch`` when the frozen declaration is usable;
``FAIL_wrong_exception_type`` and ``FAIL_import_or_file_error`` are also counted as
declared-expectation mismatches. A case with an unusable declaration is
``NOT_JUDGED_declaration_unusable`` and is never a mismatch.

The observation block (extra_observations) is deliberately NOT part of the exit
code: those entries are design observations whose expected value is sometimes
"no expectation asserted".
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
    parser.add_argument("--cases", default=None,
                        help="override the cases.json path (used by the mutation probe)")
    args = parser.parse_args()

    evidence = os.path.join(args.attempt, "evidence", args.card)
    input_doc = load_json(os.path.join(evidence, "input.json"))
    oracle_doc = load_json(os.path.join(evidence, "oracle.json"))
    cases_path = args.cases or os.path.join(evidence, "cases.json")
    cases_doc = load_json(cases_path)

    sys.path.insert(0, args.code_root)
    import model_registry  # noqa: E402

    result = {
        "card_id": args.card,
        "model_id": oracle_doc["model_id"],
        "code_root": args.code_root,
        "model_registry_file": model_registry.__file__,
        "cases_path": cases_path,
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
    # Frozen-declaration gate, evaluated BEFORE any case is judged (revision r3, batch M21-M24).
    # A case's `expected` MUST be a bare exception type name (e.g. "ModelRegistryError"). If any
    # case's declaration is missing or unusable the run can produce NO VERDICT at all: exit code 2
    # with reason "cases_json_declared_expectation_missing:<ids>". Such a case is reported as
    # NOT_JUDGED_declaration_unusable and is deliberately NOT counted as a mismatch, because no
    # comparison against a usable declaration ever happened for it.
    unusable_declared = [c.get("id") for c in cases_doc["cases"]
                         if not (isinstance(c.get("expected"), str) and c["expected"].strip())]
    cases_declared_ok = not unusable_declared
    result["frozen_declaration_assertion"] = {
        "rule": "every case's frozen `expected` must be a non-empty STRING naming the exception "
                "type that must be raised; the comparison is EXACT TYPE-NAME EQUALITY between "
                "type(exc).__name__ and that string (isinstance() is NOT used, because "
                "ModelRegistryError subclasses ValueError)",
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "unusable_declared_ids": unusable_declared,
        "declared_expectations_in_cases_json": sorted(
            {c["expected"] for c in cases_doc["cases"]
             if isinstance(c.get("expected"), str) and c["expected"].strip()}),
        "no_verdict_reason": (
            None if cases_declared_ok
            else "cases_json_declared_expectation_missing:"
                 + ",".join(str(i) for i in unusable_declared)),
        "declared_expectations_enforced": True,
    }

    # Gate BEFORE the loop: every id in the frozen `required_message_ids` must exist and must
    # carry a non-empty `expect_message_contains`. Without this gate, DELETING a message
    # requirement would silently disable the check (independent review round 2, item 3), so
    # mutation probe R4 in scripts/selfcheck_mutations.py must go red when the field is
    # removed. This evaluation is deliberately OUT OF BAND: it is not a case `kind`, so it
    # does not add a verdict to the negative summary - it fails the whole run instead.
    required_ids = cases_doc.get("required_message_ids")
    gate_problems = []
    if required_ids is None:
        gate_problems.append("cases.json has no frozen `required_message_ids` field")
    elif not isinstance(required_ids, list):
        gate_problems.append("`required_message_ids` is not a list: %r" % (required_ids,))
    else:
        by_id = {c["id"]: c for c in cases_doc["cases"]}
        for required_id in required_ids:
            case = by_id.get(required_id)
            if case is None:
                gate_problems.append("required message id %r is absent from `cases`"
                                     % required_id)
            elif not (case.get("expect_message_contains") or "").strip():
                gate_problems.append(
                    "required message id %r has an empty or absent `expect_message_contains`"
                    % required_id)
    for obs in cases_doc.get("extra_observations", []):
        if obs.get("expect_message_contains"):
            gate_problems.append("observation %r carries a message requirement, which this "
                                 "runner never evaluates" % obs["id"])
    result["required_message_ids_assertion"] = {
        "required_ids": required_ids,
        "rule": cases_doc.get("required_message_ids_rule"),
        "problems": gate_problems,
        "ok": not gate_problems,
    }

    for case in cases_doc["cases"]:
        base_key = case.get("base_input", "positive")
        base = copy.deepcopy(input_doc[base_key])
        # the raw frozen declaration, copied verbatim; `case["expected"]` may be ABSENT, so this
        # is a .get() rather than an index and must never raise for a missing declaration.
        declared = case.get("expected")
        entry = {"id": case["id"], "kind": case["kind"], "why": case["why"],
                 "expected": declared, "declared": declared, "base_input": base_key,
                 "expect_message_contains": case.get("expect_message_contains")}
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = (repr(mutated["drivers"])[:400]
                                           + " years=" + repr(mutated["years"])
                                           + " base=" + repr(mutated["base_revenue"]))
            call_product(model_registry, mutated)
            entry["raised"] = None
            entry["declared_usable"] = isinstance(declared, str) and bool(declared.strip())
            entry["judged"] = bool(entry["declared_usable"])
            entry["declared_expectation_ok"] = None
            entry["declared_expectation_mismatch"] = False
            entry["declared_expectation_not_met"] = True
            entry["declared_expectation_comparison"] = (
                "no exception raised; declared %r" % (declared,))
            if not entry["declared_usable"]:
                # precedence: an unusable declaration means the case CANNOT be judged, so it must
                # never be reported as a rejection failure or as a mismatch
                entry["verdict"] = "NOT_JUDGED_declaration_unusable"
            else:
                entry["verdict"] = "FAIL_not_rejected"
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
            is_target = isinstance(exc, model_registry.ModelRegistryError)
            is_import_or_file = isinstance(exc, (ImportError, ModuleNotFoundError, FileNotFoundError))
            entry["is_target_type"] = is_target
            entry["is_import_or_file_error"] = is_import_or_file
            # (2) the frozen `expected` field must actually be CHECKED, not merely copied.
            # EXACT TYPE-NAME EQUALITY; isinstance() must never be used here because
            # ModelRegistryError is a subclass of ValueError.
            raised_name = type(exc).__name__
            entry["expected_type_matches_raised"] = (raised_name == declared)
            declared_usable = isinstance(declared, str) and bool(declared.strip())
            entry["declared_usable"] = declared_usable
            if declared_usable:
                declared_ok = (raised_name == declared)
                entry["declared_expectation_ok"] = declared_ok
                entry["declared_expectation_mismatch"] = not declared_ok
                entry["declared_expectation_not_met"] = not declared_ok
                entry["declared_expectation_comparison"] = (
                    "raised %r == declared %r -> %s (exact exception type name)"
                    % (raised_name, declared, declared_ok))
                entry["judged"] = True
            else:
                entry["declared_expectation_ok"] = None
                entry["declared_expectation_mismatch"] = False
                entry["declared_expectation_not_met"] = None
                entry["declared_expectation_comparison"] = (
                    "NOT JUDGED: frozen `expected` is missing or unusable (got %r); "
                    "raised %r was never compared to a usable declaration"
                    % (declared, raised_name))
                entry["judged"] = False
            # (3) the frozen message requirement, when the case carries one
            requirement = case.get("expect_message_contains")
            entry["message_requirement_met"] = (
                None if requirement is None else bool(requirement in (entry.get("message") or "")))
            if not declared_usable:
                entry["verdict"] = "NOT_JUDGED_declaration_unusable"
            elif not is_target:
                entry["verdict"] = ("FAIL_import_or_file_error" if is_import_or_file
                                    else "FAIL_wrong_exception_type")
            elif not entry["expected_type_matches_raised"]:
                entry["verdict"] = "FAIL_expected_type_mismatch"
            elif entry["message_requirement_met"] is False:
                entry["verdict"] = "FAIL_message_mismatch"
            else:
                entry["verdict"] = "PASS_rejected"
        result["negatives"].append(entry)

    result["negative_summary"] = {
        "total": len(result["negatives"]),
        "passed": sum(1 for e in result["negatives"] if e["verdict"] == "PASS_rejected"),
        "failed": [e["id"] for e in result["negatives"] if e["verdict"] != "PASS_rejected"],
        "expected_type_mismatch_cases": [e["id"] for e in result["negatives"]
                                         if e["verdict"] == "FAIL_expected_type_mismatch"],
        "message_mismatch_cases": [e["id"] for e in result["negatives"]
                                   if e["verdict"] == "FAIL_message_mismatch"],
        "message_requirements_checked": sorted(
            e["id"] for e in result["negatives"] if e.get("expect_message_contains")),
        "required_message_ids_ok": bool(result["required_message_ids_assertion"]["ok"]),
        "judged": sum(1 for e in result["negatives"] if e.get("judged")),
        "not_judged_declaration_unusable_cases": [
            e["id"] for e in result["negatives"]
            if e["verdict"] == "NOT_JUDGED_declaration_unusable"],
        "declared_expectations_in_cases_json": sorted(
            {e["declared"] for e in result["negatives"]
             if isinstance(e.get("declared"), str) and e["declared"].strip()}),
        "declared_expectation_comparison": (
            "exact exception type name == cases.json's per-case 'expected' string (NOT isinstance)"),
        "declared_expectations_enforced": True,
        "verdict_rule": "PASS_rejected requires isinstance(ModelRegistryError) AND the raised "
                        "type name EQUAL to cases.json `expected` AND, when present, "
                        "expect_message_contains to be a substring of the message. "
                        "Additionally the whole run fails if the frozen `required_message_ids` "
                        "gate does not hold, and produces NO VERDICT (exit 2) if any case's "
                        "frozen `expected` declaration is missing or unusable.",
    }
    result["negative_counts"] = {
        "total": result["negative_summary"]["total"],
        "passed": result["negative_summary"]["passed"],
        "failed": len([e for e in result["negatives"] if e["verdict"] != "PASS_rejected"]),
        "declared_expectation_mismatch": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_mismatch")),
        "declared_expectation_not_met": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_not_met") is True),
        "declared_expectation_missing_in_cases_json": len(unusable_declared),
        "not_judged": sum(1 for e in result["negatives"] if not e.get("judged")),
    }

    def dump(path):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=1)

    dump(args.out)

    print("code_root:", result["code_root"])
    print("model_registry_file:", result["model_registry_file"])
    print("cases_path:", result["cases_path"])
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
              "expected_type_checked=", entry.get("expected_type_matches_raised"),
              "declared=", repr(entry.get("declared")),
              "declared_expectation_mismatch=", entry.get("declared_expectation_mismatch"),
              "judged=", entry.get("judged"),
              "comparison=", entry.get("declared_expectation_comparison"),
              "message_requirement_met=", entry.get("message_requirement_met"),
              "-", entry.get("message", ""))
    print("negative summary:", result["negative_summary"])
    print("negative counts:", result["negative_counts"])
    print("required_message_ids:", result["required_message_ids_assertion"]["required_ids"],
          "ok=", result["required_message_ids_assertion"]["ok"],
          "problems=", result["required_message_ids_assertion"]["problems"])
    print("frozen_declaration_assertion:",
          "usable=", result["frozen_declaration_assertion"]["cases_json_declared_expectations_usable"],
          "declared=", result["frozen_declaration_assertion"]["declared_expectations_in_cases_json"],
          "unusable_ids=", result["frozen_declaration_assertion"]["unusable_declared_ids"],
          "no_verdict_reason=", result["frozen_declaration_assertion"]["no_verdict_reason"])

    harness_incomplete = result["positive"].get("raised") is not None
    gate_ok = bool(result["required_message_ids_assertion"]["ok"])
    negatives_ok = (result["negative_summary"]["passed"] == result["negative_summary"]["total"]
                    and gate_ok)
    positive_ok = bool(result.get("tolerances_ok"))
    continuity_ok = bool(result["continuity_positive"].get("ok"))
    verdict = "pass" if (positive_ok and negatives_ok and continuity_ok and not harness_incomplete) else "fail"
    # Precedence: an unusable frozen declaration yields NO VERDICT (rc=2) BEFORE any case can be
    # judged, so it can never be reported as a mismatch (rc=3).
    if harness_incomplete or not cases_declared_ok:
        exit_code = 2
        if not cases_declared_ok:
            verdict = "no_verdict"
    elif verdict == "pass":
        exit_code = 0
    else:
        exit_code = 3
    no_verdict_reason = result["frozen_declaration_assertion"]["no_verdict_reason"]
    if harness_incomplete:
        no_verdict_reason = "positive_path_raised_no_comparison_possible"
    result["exit_code_semantics"] = {
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "declared_expectation_mismatch_case_ids": [
            e["id"] for e in result["negatives"] if e.get("declared_expectation_mismatch")],
        "declared_expectation_mismatch_ids": [
            e["id"] for e in result["negatives"] if e.get("declared_expectation_mismatch")],
        "not_judged_declaration_unusable_case_ids": [
            e["id"] for e in result["negatives"]
            if e["verdict"] == "NOT_JUDGED_declaration_unusable"],
        "no_verdict_reason": no_verdict_reason,
        "reason_namespace": "FAIL_expected_type_mismatch is a SUBSET of "
                            "declared_expectation_mismatch when the frozen declaration is usable; "
                            "FAIL_wrong_exception_type and FAIL_import_or_file_error also count as "
                            "declared_expectation_mismatch. A case with an unusable declaration is "
                            "NOT_JUDGED_declaration_unusable and is never a mismatch.",
        "harness_incomplete": harness_incomplete,
        "positive_ok": positive_ok,
        "continuity_ok": continuity_ok,
        "negatives_ok": negatives_ok,
        "required_message_ids_ok": gate_ok,
        "defaults_ok_not_gating": result.get("defaults_ok"),
        "verdict": verdict,
        "exit_code": exit_code,
    }
    dump(args.out)
    if args.run_result_out:
        dump(args.run_result_out)
    print("verdict:", verdict, "exit_code:", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
