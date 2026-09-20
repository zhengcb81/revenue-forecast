"""M01 product runner: calls only calculate_registered_model(**oracle.input).

Isolation contract
------------------
* The product scripts directory is taken from --code-root (the I-00-B bound
  isolated checkout; this attempt only has iso/override module copies, so the
  bound source root is used read-only and its hashes are recorded).
* The only product entry point invoked is
  ``calculate_registered_model(**input_spec)``, exactly as card_M01.md step B
  requires. No other product function is called.
* Expected values come exclusively from evidence/M01/oracle.json, which was
  produced by scripts/oracle_M01.py (stdlib only). The runner never derives an
  expectation from the product.
* Every negative case gets a NEW deepcopy of the frozen positive input, built
  in memory (never round-tripped through a JSON parser, so JSON rejections
  cannot masquerade as model rejections).

Raw exit code of this process is reported by the caller; this script always
exits 0 when it completed its own bookkeeping, and records per-case raw
outcomes in formula_result.json / negative_results.json.
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
        if "__bool__" in spec:
            return True
        if "__bool__first__" in spec:
            return True
    return spec


def apply_case(base, case):
    """Return a fresh mutated input; base is already a deepcopy."""
    kind = case["kind"]
    if kind == "set_driver_element":
        base["drivers"][case["driver"]][case["index"]] = build_mutation_value(case["value"])
    elif kind == "set_driver":
        base["drivers"][case["driver"]] = copy.deepcopy(case["value"])
    elif kind == "delete_driver":
        del base["drivers"][case["driver"]]
    elif kind == "add_driver":
        base["drivers"][case["driver"]] = copy.deepcopy(case["value"])
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    evidence = os.path.join(args.attempt, "evidence", "M01")
    input_doc = load_json(os.path.join(evidence, "input.json"))
    oracle_doc = load_json(os.path.join(evidence, "oracle.json"))
    cases_doc = load_json(os.path.join(evidence, "cases.json"))

    sys.path.insert(0, args.code_root)
    import model_registry  # noqa: E402  (only allowed product import)

    result = {
        "card_id": "M01",
        "code_root": args.code_root,
        "model_registry_file": model_registry.__file__,
        "entry_point": "model_registry.calculate_registered_model(**input)",
        "positive": {},
        "continuity_positive": {},
        "negatives": [],
        "tolerances_ok": None,
    }

    # ---------------- positive ----------------
    spec = copy.deepcopy(input_doc["positive"])
    try:
        actual = model_registry.calculate_registered_model(
            model_id=spec["model_id"],
            base_revenue=spec["base_revenue"],
            drivers=spec["drivers"],
            years=spec["years"],
        )
        result["positive"] = {"raised": None, "actual": [float(v) for v in actual],
                             "actual_repr": [repr(float(v)) for v in actual],
                             "length": len(actual)}
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
        cactual = model_registry.calculate_registered_model(
            model_id=cspec["model_id"], base_revenue=cspec["base_revenue"],
            drivers=cspec["drivers"], years=cspec["years"])
        cexp = oracle_doc["continuity_positive"]["expected_float"]
        result["continuity_positive"] = {
            "raised": None, "actual": [float(v) for v in cactual], "expected": cexp,
            "ok": len(cactual) == len(cexp) and all(
                abs(a - e) <= 1e-9 * max(1.0, abs(e)) for a, e in zip(cactual, cexp)),
        }
    except Exception as exc:  # noqa: BLE001
        result["continuity_positive"] = {"raised": type(exc).__name__, "message": str(exc),
                                         "traceback": traceback.format_exc(), "ok": False}

    # ---------------- negatives ----------------
    for case in cases_doc["cases"]:
        base_key = case.get("base_input", "positive")
        base = copy.deepcopy(input_doc[base_key])
        entry = {"id": case["id"], "kind": case["kind"], "why": case["why"],
                 "expected": case["expected"], "base_input": base_key}
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = repr(mutated["drivers"])[:400] + " years=" + repr(mutated["years"])
            model_registry.calculate_registered_model(
                model_id=mutated["model_id"], base_revenue=mutated["base_revenue"],
                drivers=mutated["drivers"], years=mutated["years"])
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

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=1)

    print("positive raised:", result["positive"].get("raised"))
    print("positive actual:", result["positive"].get("actual"))
    print("tolerances_ok:", result.get("tolerances_ok"))
    print("continuity_positive ok:", result["continuity_positive"].get("ok"))
    print("negative summary:", result["negative_summary"])

    # F-M01-02 (revision r2): mirror run_card.py's verdict-carrying exit code so
    # that this earlier card-specific runner cannot report success silently.
    # NOTE: this runner is historical; the evidence of record is produced by
    # run_card.py (both produced identical results, see review.md section 2).
    harness_incomplete = result["positive"].get("raised") is not None
    negatives_ok = result["negative_summary"]["passed"] == result["negative_summary"]["total"]
    positive_ok = bool(result.get("tolerances_ok"))
    continuity_ok = bool(result["continuity_positive"].get("ok"))
    verdict = "pass" if (positive_ok and negatives_ok and continuity_ok and not harness_incomplete) else "fail"
    exit_code = 2 if harness_incomplete else (0 if verdict == "pass" else 3)
    result["exit_code_semantics"] = {
        "harness_incomplete": harness_incomplete,
        "positive_ok": positive_ok,
        "continuity_ok": continuity_ok,
        "negatives_ok": negatives_ok,
        "verdict": verdict,
        "exit_code": exit_code,
    }
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=1)
    print("verdict:", verdict, "exit_code:", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
