"""Card-agnostic, verdict-carrying product runner for the M-card formula oracles.

Isolation contract
------------------
* The product scripts directory comes from --code-root, which MUST be the
  attempt-local isolated snapshot whose sha256 is recorded in source_manifest.json.
* The only product entry point invoked is ``calculate_registered_model(**spec)``.
* Expected values come exclusively from evidence/<CARD>/oracle.json, produced by
  scripts/oracle_M25_M28.py (stdlib only, which never imports the product).
* Every negative case gets a NEW deepcopy of the frozen base input, built in
  memory (never round-tripped through a JSON parser).

Exit codes (verdict-carrying; a bookkeeping-only rc=0 is not allowed)
--------------------------------------------------------------------
  0 = the positive path matched the independent oracle within tolerance AND the
      continuity positive passed AND every negative case was rejected with
      ModelRegistryError
  1 = an unguarded harness defect raised (fail loud; the only non-verdict code)
  2 = harness/bookkeeping could not produce a verdict (e.g. the positive path
      raised, so there is nothing to compare)
  3 = the verdict is negative (positive mismatch, continuity failure, or an
      unrejected negative)

The observation block (extra_observations) is deliberately NOT part of the exit
code: those entries are design observations whose expected value is sometimes
"no expectation asserted" (M26 new_store_productivity above one, M27 negative
merchant price), which exist to record which convention the implementation uses
rather than to pass or fail it.
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


def declared_defaults_of(model_registry, model_id):
    """Bookkeeping only: what the registry DECLARES as an optional default."""
    try:
        spec = model_registry.MODEL_REGISTRY[model_id]
        return {k: (None if v is None else float(v)) for k, v in dict(spec.defaults).items()}
    except Exception:  # noqa: BLE001
        return {}


def mechanism_prefix(text):
    """Extract the message prefix a declared mechanism claims, delimited by backticks.

    The frozen declaration reads e.g. "closing_stores=[24] makes the store-count bridge fail:
    ... so `opening_stores stock-flow balance failed: FY2027` is raised"; the backticked
    fragment is the product message we require to appear. Returns None if the declaration does
    not carry exactly one backticked fragment.
    """
    if not text:
        return None
    parts = text.split("`")
    if len(parts) != 3 or not parts[1].strip():
        return None
    return parts[1].strip()


def run(args) -> int:
    attempt_dir = args.attempt_dir or args.attempt
    evidence = os.path.join(attempt_dir, "evidence", args.card)
    input_doc = load_json(os.path.join(evidence, "input.json"))
    oracle_doc = load_json(os.path.join(evidence, "oracle.json"))
    cases_doc = load_json(os.path.join(evidence, "cases.json"))
    # Mutation self-check hook (scratch only): patch a COPY of a negative case in
    # memory so the frozen cases.json stays byte-unchanged. Used by the G self-check
    # to prove that an unrejected negative really turns the verdict red.
    if args.case_override:
        for override in load_json(args.case_override):
            for case in cases_doc["cases"]:
                if case["id"] == override["id"]:
                    case.update(copy.deepcopy(override["set"]))

    # ---------------- frozen case-contract gate (review finding P3-2) ----------------
    # Before this gate the runner ignored cases.json[].expected and the case COUNT, so
    # rewriting a declaration or deleting a whole negative still produced rc=0. A harness
    # whose bookkeeping cannot notice a missing case is not verdict-carrying, so a violated
    # contract is a harness defect: fail loud with rc=1 instead of issuing a verdict.
    contract = cases_doc.get("case_contract") or {}
    contract_problems = []
    if not contract:
        contract_problems.append("cases.json has no case_contract block")
    else:
        declared = contract.get("declared_expected_exception")
        wrong_declaration = [case["id"] for case in cases_doc["cases"]
                             if case.get("expected") != declared]
        if wrong_declaration:
            contract_problems.append(
                "cases whose `expected` is not %r: %s" % (declared, wrong_declaration))
        ids = [case["id"] for case in cases_doc["cases"]]
        if len(ids) != contract.get("expected_count"):
            contract_problems.append("case count %d != declared %s"
                                     % (len(ids), contract.get("expected_count")))
        if ids != list(contract.get("expected_ids") or []):
            contract_problems.append("case id list %s != declared %s"
                                     % (ids, contract.get("expected_ids")))
        unknown = [i for i in ids if i not in ("NEG-CARD", "N01a", "N01b", "N01c", "N01d",
                                               "N02", "N03", "N04", "N05a", "N05b",
                                               "CONT-BREAK")]
        if unknown:
            contract_problems.append("unexpected negative ids: %s" % unknown)
    if contract_problems:
        sys.stderr.write("HARNESS ERROR (rc=1): frozen case contract violated:\n")
        for problem in contract_problems:
            sys.stderr.write("  - " + problem + "\n")
        sys.stderr.flush()
        return 1

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
        "defaults_declared_check": {},
        "observations": [],
        "negatives": [],
        "tolerances_ok": None,
        "defaults_ok": None,
        "harness_incomplete": None,
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

    checks = []
    if result["positive"].get("raised") is None:
        exp = oracle_doc["positive"]["expected_float"]
        tol = oracle_doc["positive"]["tolerances"]
        act = result["positive"]["actual"]
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
            "length_ok": len(cactual) == len(cexp),
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

    # ---------------- declared-default bookkeeping (NOT part of the exit code) -------------
    decl = oracle_doc.get("defaults_declared_expectation") or {}
    declared = declared_defaults_of(model_registry, oracle_doc["model_id"])
    driver = decl.get("driver")
    if driver:
        present = driver in declared
        matches = present == bool(decl.get("declared_default_present"))
    else:
        present = None
        matches = None
    result["defaults_declared_check"] = {
        "driver": driver,
        "registry_declared_defaults": declared,
        "declared_default_present": present,
        "declared_default_value": declared.get(driver) if driver else None,
        "expected_declared_default_present": decl.get("declared_default_present"),
        "matches_expected": matches,
        "why": decl.get("why"),
        "gating": False,
    }

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
    }

    # ---------------- NEG-CARD mechanism check (review finding P2-1) ----------------
    # Being rejected is not enough: a negative that is refused by an UNRELATED generic guard
    # (here the length/type guard) does not exercise the card-specific rule the oracle claims.
    # The frozen contract declares the mechanism; we only assert the declared MESSAGE PREFIX
    # appears, which is stable and does not compare against a product-generated expectation.
    neg_card_mechanism = contract.get("neg_card_declared_mechanism")
    neg_card = next((e for e in result["negatives"] if e["id"] == "NEG-CARD"), None)
    prefix = mechanism_prefix(neg_card_mechanism)
    message = (neg_card or {}).get("message") or ""
    mechanism_ok = bool(prefix) and prefix in message
    result["neg_card_mechanism_check"] = {
        "declared": neg_card_mechanism,
        "observed_message": (neg_card or {}).get("message"),
        "expected_substring": prefix,
        "matched": mechanism_ok,
        "gating": True,
        "why": ("the card-specific negative must be refused by the CARD-SPECIFIC guard, not by "
                "the generic per-year length/type guard; otherwise the oracle.md coverage claim "
                "is unsupported. A declaration without exactly one backticked message fragment is "
                "itself a contract violation."),
    }

    def dump(path):
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
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
    print("defaults declared check:", result["defaults_declared_check"].get("driver"),
          "declared=", result["defaults_declared_check"].get("declared_default_present"),
          "expected=", result["defaults_declared_check"].get("expected_declared_default_present"),
          "matches=", result["defaults_declared_check"].get("matches_expected"),
          "registry_defaults=", result["defaults_declared_check"].get("registry_declared_defaults"))
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
    print("neg_card_mechanism matched:", result["neg_card_mechanism_check"]["matched"],
          "expected_substring=", result["neg_card_mechanism_check"]["expected_substring"],
          "observed=", result["neg_card_mechanism_check"]["observed_message"])

    harness_incomplete = result["positive"].get("raised") is not None
    negatives_ok = result["negative_summary"]["passed"] == result["negative_summary"]["total"]
    positive_ok = bool(result.get("tolerances_ok"))
    continuity_ok = bool(result["continuity_positive"].get("ok"))
    mechanism_ok = bool(result["neg_card_mechanism_check"]["matched"])
    verdict = "pass" if (positive_ok and negatives_ok and continuity_ok and mechanism_ok
                         and not harness_incomplete) else "fail"
    if harness_incomplete:
        exit_code = 2
    elif verdict == "pass":
        exit_code = 0
    else:
        exit_code = 3
    result["harness_incomplete"] = harness_incomplete
    result["exit_code_semantics"] = {
        "harness_incomplete": harness_incomplete,
        "positive_ok": positive_ok,
        "continuity_ok": continuity_ok,
        "negatives_ok": negatives_ok,
        "neg_card_mechanism_ok": mechanism_ok,
        "defaults_ok_not_gating": result.get("defaults_ok"),
        "defaults_declared_check_not_gating": result["defaults_declared_check"].get("matches_expected"),
        "verdict": verdict,
        "exit_code": exit_code,
    }
    dump(args.out)
    if args.run_result_out:
        dump(args.run_result_out)
    print("verdict:", verdict, "exit_code:", exit_code)
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-result-out", default=None)
    parser.add_argument("--case-override", default=None,
                       help="scratch-only: JSON list of {id, set} patches applied to an in-memory "
                            "copy of cases.json so a corrupted negative assertion can be shown to fail")
    parser.add_argument("--attempt-dir", default=None,
                       help="scratch-only: read evidence/<card>/{input,oracle,cases}.json from this "
                            "directory instead of --attempt, so a scratch run reads exactly one "
                            "mutated file and nothing else")
    args = parser.parse_args()
    try:
        return run(args)
    except SystemExit:
        raise
    except BaseException:  # noqa: BLE001 - unguarded harness defect: fail loud with rc=1
        sys.stderr.write("HARNESS ERROR (rc=1):\n")
        sys.stderr.write(traceback.format_exc())
        sys.stderr.flush()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
