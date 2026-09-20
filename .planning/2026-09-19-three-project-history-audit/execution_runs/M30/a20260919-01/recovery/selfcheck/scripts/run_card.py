"""Card-agnostic, verdict-carrying product runner for the I-10 model-card formula oracles.

Isolation contract
------------------
* The product code comes from --code-root, which MUST be the attempt-local isolated
  snapshot whose sha256 is recorded in evidence/<CARD>/source_manifest.json.
* The only product entry point invoked is ``calculate_registered_model(**spec)``.
* Expected values come exclusively from evidence/<CARD>/oracle.json, produced by
  scripts/oracle_<CARD>.py (stdlib only; it never imports the product).
* Every negative case gets a NEW deepcopy of the frozen base input, built in memory
  (never round-tripped through a JSON parser), so a JSON-parser rejection cannot
  masquerade as a model rejection.

Exit codes (verdict-carrying; a bookkeeping-only rc=0 is not allowed)
--------------------------------------------------------------------
  0 = pass            positive within the frozen tolerance AND output fidelity ok
                      AND the continuity positive matched AND every negative case
                      was rejected with model_registry.ModelRegistryError
  1 = harness error   the runner itself could not produce a verdict (missing or
                      unreadable evidence file, product import failure, unexpected
                      exception outside the case loops)
  2 = no verdict      the frozen expectation is missing, or the observed output
                      cannot be faithfully compared with the frozen shape
                      (length != len(years), length != len(expected), element that
                      is not a plain finite number, non-sequence container)
  3 = negative verdict the comparison was possible and did not hold: the positive
                      path raised or fell outside tolerance, the continuity
                      positive did not match, or at least one negative case was NOT
                      rejected as expected

Precedence when several conditions hold at once: 1 > 2 > 3 > 0 (a harness failure
dominates; "no verdict could be issued" dominates "the verdict is negative").

Difference from the M05-M08 runner of this same audit, recorded rather than hidden:
that runner used 2 = harness/bookkeeping failure and 3 = negative verdict for
positive mismatch, continuity failure and unrejected negatives alike.  This batch
keeps 3 as the negative verdict, moves the harness failure to 1 and reserves 2 for
"no verdict could be issued" (missing expectation / fidelity mismatch).  The delta
is documented in the attempt's oracle.md, review.md and evidence/<CARD>/exit_code.json.

Printed output contract
-----------------------
Every value printed to stdout is also stored in the result document under
``printed_summary.lines`` and the file is re-read before printing, so the printed
values and the evidence file cannot disagree (see F-M05-01/-02 lineage: an earlier
batch printed a value that did not match its evidence file).
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
import traceback

EXIT_PASS = 0
EXIT_HARNESS = 1
EXIT_NO_VERDICT = 2
EXIT_NEGATIVE = 3


class HarnessError(RuntimeError):
    """Raised when the runner cannot even set up a comparison."""


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:  # noqa: BLE001
        raise HarnessError("cannot read %s: %s: %s" % (path, type(exc).__name__, exc)) from exc


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
        raise HarnessError("unknown mutation kind: " + repr(kind))
    return base


def call_product(model_registry, spec):
    return model_registry.calculate_registered_model(
        model_id=spec["model_id"], base_revenue=spec["base_revenue"],
        drivers=spec["drivers"], years=spec["years"])


def within(values, expected):
    if len(values) != len(expected):
        return False
    return all(abs(a - e) <= 1e-9 * max(1.0, abs(e)) for a, e in zip(values, expected))


def describe_output(value):
    """Structure/length/field-set description of a produced revenue path.

    The product returns a bare list of numbers, so year LABELS are not observable;
    the only year-linked property that can be observed is length == len(years).
    That limitation is recorded explicitly instead of being papered over.
    """
    is_seq = isinstance(value, (list, tuple))
    elements = list(value) if is_seq else []
    return {
        "python_type": type(value).__name__,
        "is_flat_sequence": is_seq,
        "length": len(elements) if is_seq else None,
        "element_types": [type(v).__name__ for v in elements] if is_seq else None,
        "all_elements_plain_number": bool(is_seq) and all(
            isinstance(v, (int, float)) and not isinstance(v, bool) for v in elements),
        "all_elements_finite": bool(is_seq) and all(
            isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
            for v in elements),
        "container_has_extra_fields": False if is_seq else None,
        "year_labels_observable": False,
        "year_linked_observable": "length only: len(output) must equal len(years)",
    }


def fidelity_block(value, expected, years):
    described = describe_output(value)
    length = described["length"]
    expectations_present = (isinstance(expected, list) and len(expected) > 0
                            and isinstance(years, list) and len(years) > 0)
    described["expected_length"] = len(expected) if isinstance(expected, list) else None
    described["years_length"] = len(years) if isinstance(years, list) else None
    described["length_equals_years"] = (length is not None and isinstance(years, list)
                                        and length == len(years))
    described["length_equals_expected"] = (length is not None and isinstance(expected, list)
                                           and length == len(expected))
    described["expectations_present"] = bool(expectations_present)
    structure_ok = bool(described["is_flat_sequence"] and described["all_elements_plain_number"]
                        and described["all_elements_finite"])
    described["structure_ok"] = structure_ok
    described["fidelity_ok"] = bool(structure_ok
                                    and described["length_equals_years"]
                                    and described["length_equals_expected"])
    return described


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-result-out", default=None)
    parser.add_argument("--negative-out", default=None)
    args = parser.parse_args()

    lines = []

    def emit(text):
        lines.append(text)

    result = {
        "card_id": args.card,
        "attempt_root": args.attempt,
        "code_root": args.code_root,
        "product_entry_point": "model_registry.calculate_registered_model(**input)",
        "only_product_function_called": "calculate_registered_model",
        "registry_metadata": {},
        "positive": {},
        "continuity_positive": {},
        "defaults": {},
        "observations": [],
        "negatives": [],
        "fidelity": {},
        "tolerances_ok": None,
        "defaults_ok": None,
        "exit_code_semantics": {
            "0": "pass",
            "1": "harness error",
            "2": "no verdict (missing expectation or fidelity mismatch)",
            "3": "negative verdict (mismatch or unrejected negative)",
            "precedence": "1 > 2 > 3 > 0",
            "delta_vs_M05_M08_runner": ("M05-M08 used 2=harness failure and 3=negative verdict; "
                                        "this runner moves harness failure to 1 and reserves 2 "
                                        "for 'no verdict could be issued'"),
        },
    }

    try:
        evidence = os.path.join(args.attempt, "evidence", args.card)
        input_doc = load_json(os.path.join(evidence, "input.json"))
        oracle_doc = load_json(os.path.join(evidence, "oracle.json"))
        cases_doc = load_json(os.path.join(evidence, "cases.json"))

        result["model_id"] = oracle_doc["model_id"]
        result["input_hashes_source"] = {
            "evidence/%s/input.json" % args.card: _sha256(os.path.join(evidence, "input.json")),
            "evidence/%s/oracle.json" % args.card: _sha256(os.path.join(evidence, "oracle.json")),
            "evidence/%s/cases.json" % args.card: _sha256(os.path.join(evidence, "cases.json")),
        }

        sys.path.insert(0, args.code_root)
        try:
            import model_registry  # noqa: E402
        except Exception as exc:  # noqa: BLE001
            raise HarnessError("cannot import model_registry from %s: %s: %s"
                               % (args.code_root, type(exc).__name__, exc)) from exc
        result["model_registry_file"] = model_registry.__file__
    except HarnessError as exc:
        result["harness_error"] = str(exc)
        result["verdict"] = "harness_error"
        result["exit_code"] = EXIT_HARNESS
        emit("HARNESS ERROR: " + str(exc))
        emit("verdict: harness_error exit_code: %d" % EXIT_HARNESS)
        result["printed_summary"] = {"lines": lines, "note": "printed lines are byte-identical to stdout.txt"}
        _dump(args.out, result)
        if args.run_result_out:
            _dump(args.run_result_out, result)
        for line in lines:
            print(line)
        return EXIT_HARNESS

    try:
        spec = model_registry.MODEL_REGISTRY[oracle_doc["model_id"]]
        result["registry_metadata"] = {
            "model_id": spec.model_id,
            "required": list(spec.required),
            "optional": list(spec.optional),
            "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
            "dimensions": dict(spec.dimensions),
            "ratio_drivers": sorted(spec.ratio_drivers),
            "declared_driver_bounds": {k: [None if b[0] is None else b[0],
                                           None if b[1] is None else b[1]]
                                       for k, b in dict(spec.driver_bounds).items()},
            "formula": spec.formula,
        }
        result["registry_metadata"]["effective_bounds"] = {}
        for driver in list(spec.required) + list(spec.optional):
            lower, upper = model_registry.driver_value_bounds(spec.model_id, driver)
            result["registry_metadata"]["effective_bounds"][driver] = [
                "-inf" if lower == -math.inf else lower,
                "inf" if upper == math.inf else upper,
            ]
    except Exception as exc:  # noqa: BLE001
        result["registry_metadata"] = {"error": type(exc).__name__ + ": " + str(exc)}

    # ---------------- positive ----------------
    spec_in = copy.deepcopy(input_doc["positive"])
    try:
        actual = call_product(model_registry, spec_in)
        result["positive"] = {"raised": None, "actual": [float(v) for v in actual],
                              "actual_repr": [repr(float(v)) for v in actual],
                              "length": len(actual)}
    except Exception as exc:  # noqa: BLE001
        result["positive"] = {"raised": type(exc).__name__, "message": str(exc),
                              "traceback": traceback.format_exc()}

    exp = oracle_doc.get("positive", {}).get("expected_float")
    tol = oracle_doc.get("positive", {}).get("tolerances")
    years = oracle_doc.get("positive", {}).get("years")
    expectations_present = (isinstance(exp, list) and len(exp) > 0
                            and isinstance(tol, list) and len(tol) == len(exp)
                            and isinstance(years, list) and len(years) > 0)
    result["expectations_present"] = bool(expectations_present)
    result["fidelity"] = {"missing_expectation_reason": None if expectations_present else
                          "evidence/%s/oracle.json positive.expected_float / tolerances / years "
                          "absent or not the same length" % args.card}

    if result["positive"].get("raised") is None and expectations_present:
        result["fidelity"] = fidelity_block(actual, exp, years)
        act = result["positive"]["actual"]
        checks = []
        if result["fidelity"]["length_equals_expected"]:
            for i, (a, e, t) in enumerate(zip(act, exp, tol)):
                checks.append({"index": i, "year": years[i], "actual": a, "expected": e,
                               "tolerance": t, "abs_diff": abs(a - e), "ok": abs(a - e) <= t})
        result["per_value_checks"] = checks
        result["tolerances_ok"] = bool(checks) and all(c["ok"] for c in checks)
    elif result["positive"].get("raised") is not None:
        result["tolerances_ok"] = False
        result["fidelity"] = {"fidelity_ok": False,
                              "reason": "the positive path raised, so no output could be compared"}

    # ---------------- continuity positive ----------------
    cspec = copy.deepcopy(input_doc["continuity_positive"])
    cexp = oracle_doc.get("continuity_positive", {}).get("expected_float")
    try:
        cactual = call_product(model_registry, cspec)
        cwithin = bool(isinstance(cexp, list) and len(cexp) > 0
                       and within([float(v) for v in cactual], cexp))
        result["continuity_positive"] = {
            "raised": None, "actual": [float(v) for v in cactual],
            "actual_repr": [repr(float(v)) for v in cactual], "expected": cexp,
            "expectation_present": isinstance(cexp, list) and len(cexp) > 0,
            "ok": cwithin,
        }
    except Exception as exc:  # noqa: BLE001
        result["continuity_positive"] = {"raised": type(exc).__name__, "message": str(exc),
                                         "traceback": traceback.format_exc(), "ok": False,
                                         "expectation_present": isinstance(cexp, list)}

    # ---------------- defaults case (recorded, NOT gating) ----------------
    dspec = copy.deepcopy(input_doc["defaults"])
    dexp = oracle_doc.get("defaults_expected_float")
    try:
        dactual = call_product(model_registry, dspec)
        result["defaults"] = {
            "raised": None, "actual": [float(v) for v in dactual], "expected": dexp,
            "ok": bool(isinstance(dexp, list) and within([float(v) for v in dactual], dexp)),
        }
    except Exception as exc:  # noqa: BLE001
        result["defaults"] = {"raised": type(exc).__name__, "message": str(exc),
                              "traceback": traceback.format_exc(), "ok": False}
    result["defaults_ok"] = bool(result["defaults"].get("ok"))
    result["defaults_gating"] = False

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
        entry = {"id": case["id"], "kind": case["kind"], "why": case["why"],
                 "expected": case["expected"], "base_input": base_key}
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = (repr(mutated["drivers"])[:400]
                                           + " years=" + repr(mutated["years"])
                                           + " base=" + repr(mutated["base_revenue"]))
            call_product(model_registry, mutated)
            entry["raised"] = None
            entry["verdict"] = "FAIL_not_rejected"
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
            is_target = isinstance(exc, model_registry.ModelRegistryError)
            is_import_or_file = isinstance(exc, (ImportError, ModuleNotFoundError, FileNotFoundError))
            entry["is_target_type"] = is_target
            entry["is_import_or_file_error"] = is_import_or_file
            entry["verdict"] = ("PASS_rejected" if is_target
                                else ("FAIL_wrong_exception_type" if not is_import_or_file
                                      else "FAIL_import_or_file_error"))
        result["negatives"].append(entry)

    result["negative_summary"] = {
        "total": len(result["negatives"]),
        "passed": sum(1 for e in result["negatives"] if e["verdict"] == "PASS_rejected"),
        "failed": [e["id"] for e in result["negatives"] if e["verdict"] != "PASS_rejected"],
        "target_exception": "model_registry.ModelRegistryError",
        "import_or_file_errors_never_pass": True,
    }
    result["negative_counts"] = {
        "total": len(result["negatives"]),
        "rejected_with_ModelRegistryError": sum(
            1 for e in result["negatives"] if e.get("is_target_type")),
        "not_rejected": sum(1 for e in result["negatives"] if e["raised"] is None),
        "wrong_exception_type": sum(1 for e in result["negatives"]
                                    if e.get("raised") is not None and not e.get("is_target_type")
                                    and not e.get("is_import_or_file_error")),
        "import_or_file_error": sum(1 for e in result["negatives"] if e.get("is_import_or_file_error")),
    }

    # ---------------- verdict ----------------
    positive_raised = result["positive"].get("raised") is not None
    fidelity_ok = bool(result["fidelity"].get("fidelity_ok"))
    tolerances_ok = bool(result.get("tolerances_ok"))
    continuity_ok = bool(result["continuity_positive"].get("ok"))
    negatives_ok = result["negative_summary"]["passed"] == result["negative_summary"]["total"]

    reasons = []
    if positive_raised:
        reasons.append("positive_raised:%s" % result["positive"].get("raised"))
    if not expectations_present:
        reasons.append("frozen_expectation_missing")
    if expectations_present and not positive_raised and not fidelity_ok:
        reasons.append("output_fidelity_mismatch")
    if expectations_present and not positive_raised and fidelity_ok and not tolerances_ok:
        reasons.append("positive_out_of_tolerance")
    if not continuity_ok:
        reasons.append("continuity_positive_not_matched")
    if not negatives_ok:
        reasons.append("negatives_not_rejected:" + ",".join(result["negative_summary"]["failed"]))

    if not expectations_present or (expectations_present and not positive_raised and not fidelity_ok):
        exit_code = EXIT_NO_VERDICT
        verdict = "no_verdict"
    elif reasons:
        exit_code = EXIT_NEGATIVE
        verdict = "fail"
    else:
        exit_code = EXIT_PASS
        verdict = "pass"

    result["verdict"] = verdict
    result["exit_code"] = exit_code
    result["verdict_reasons"] = reasons
    result["exit_code_semantics"].update({
        "positive_raised": positive_raised,
        "expectations_present": expectations_present,
        "fidelity_ok": fidelity_ok,
        "positive_ok": bool(tolerances_ok and fidelity_ok and not positive_raised),
        "continuity_ok": continuity_ok,
        "negatives_ok": negatives_ok,
        "defaults_ok_not_gating": result.get("defaults_ok"),
        "verdict": verdict,
        "exit_code": exit_code,
    })

    # ---------------- negative_results.json (written by the run itself) ----------------
    if args.negative_out:
        neg_doc = {
            "card_id": args.card,
            "model_id": result.get("model_id"),
            "attempt_root": args.attempt,
            "code_root": args.code_root,
            "target_exception": "model_registry.ModelRegistryError",
            "independence": ("each case is built from a NEW deepcopy of the frozen base input, in "
                             "memory; no case is round-tripped through a JSON parser"),
            "first_required_driver": cases_doc.get("first_required_driver"),
            "frozen_expectation": "ModelRegistryError for every case",
            "continuity_first_positive": cases_doc.get("continuity_first_positive"),
            "summary": {"total": result["negative_summary"]["total"],
                        "passed": result["negative_summary"]["passed"],
                        "failed": result["negative_summary"]["failed"]},
            "counts": result["negative_counts"],
            "cases": result["negatives"],
        }
        _dump(args.negative_out, neg_doc)

    # ---------------- printed output == evidence file ----------------
    emit("card: %s model_id: %s" % (args.card, result.get("model_id")))
    emit("code_root: %s" % result["code_root"])
    emit("model_registry_file: %s" % result.get("model_registry_file"))
    emit("registry formula: %s" % result["registry_metadata"].get("formula"))
    emit("registry required: %s" % result["registry_metadata"].get("required"))
    emit("registry optional: %s" % result["registry_metadata"].get("optional"))
    emit("registry defaults: %s" % result["registry_metadata"].get("defaults"))
    emit("registry declared_driver_bounds: %s"
         % result["registry_metadata"].get("declared_driver_bounds"))
    emit("registry effective_bounds: %s" % result["registry_metadata"].get("effective_bounds"))
    emit("positive raised: %s" % result["positive"].get("raised"))
    emit("positive actual: %s" % result["positive"].get("actual"))
    emit("positive expected: %s" % exp)
    emit("positive tolerances: %s" % tol)
    emit("positive fidelity: %s" % result["fidelity"])
    emit("per_value_checks: %s" % result.get("per_value_checks"))
    emit("tolerances_ok: %s" % result.get("tolerances_ok"))
    emit("continuity_positive raised: %s actual: %s expected: %s ok: %s"
         % (result["continuity_positive"].get("raised"), result["continuity_positive"].get("actual"),
            result["continuity_positive"].get("expected"), result["continuity_positive"].get("ok")))
    emit("defaults (not gating) ok: %s actual: %s expected: %s"
         % (result.get("defaults_ok"), result["defaults"].get("actual"), result["defaults"].get("expected")))
    for obs in result["observations"]:
        emit("observation: %s raised=%s actual=%s matches_compared=%s expect_equal=%s "
             "matches_expected_relation=%s matches_expected=%s"
             % (obs["id"], obs.get("raised"), obs.get("actual"), obs.get("matches_compared"),
                obs.get("expect_equal"), obs.get("matches_expected_relation"),
                obs.get("matches_expected")))
    for entry in result["negatives"]:
        emit("negative: %s %s %s - %s" % (entry["id"], entry["verdict"], entry.get("raised"),
                                          entry.get("message", "")))
    emit("negative summary: %s" % result["negative_summary"])
    emit("verdict: %s exit_code: %d" % (verdict, exit_code))

    summary_keys = ("positive", "continuity_positive", "defaults", "negative_summary",
                    "tolerances_ok", "defaults_ok", "verdict", "exit_code", "fidelity")
    partial = {k: result.get(k) for k in summary_keys}
    result["printed_summary"] = {"lines": lines, "note": "printed lines are byte-identical to stdout.txt"}
    _dump(args.out, result)
    if args.run_result_out:
        _dump(args.run_result_out, result)

    re_read = load_json(args.out)
    checks = [
        re_read.get("positive", {}).get("actual") == result["positive"].get("actual"),
        re_read.get("continuity_positive", {}).get("actual")
        == result["continuity_positive"].get("actual"),
        re_read.get("negative_summary") == result["negative_summary"],
        re_read.get("tolerances_ok") == result.get("tolerances_ok"),
        re_read.get("verdict") == verdict,
        re_read.get("exit_code") == exit_code,
        all(re_read.get(k) == partial[k] for k in summary_keys),
    ]
    consistency_ok = all(checks)
    consistency_line = ("printed_matches_evidence_file: %s (re-read %s and compared "
                        "positive/continuity/negative_summary/tolerances_ok/verdict/exit_code)"
                        % (consistency_ok, os.path.basename(args.out)))
    result["printed_values_match_evidence_file"] = consistency_ok
    emit(consistency_line)
    result["printed_summary"]["lines"] = lines
    _dump(args.out, result)
    if args.run_result_out:
        _dump(args.run_result_out, result)

    for line in lines:
        print(line)
    if not consistency_ok:
        return EXIT_HARNESS
    return exit_code


def _sha256(path):
    import hashlib
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _dump(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001
        print("HARNESS ERROR (uncaught): %s: %s" % (type(exc).__name__, exc))
        traceback.print_exc()
        raise SystemExit(EXIT_HARNESS)
