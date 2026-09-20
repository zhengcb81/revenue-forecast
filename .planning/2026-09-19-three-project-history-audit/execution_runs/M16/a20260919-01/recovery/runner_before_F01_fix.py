"""Card-agnostic, verdict-carrying product runner for the M13-M16 formula oracles.

Isolation contract
------------------
* ``--code-root`` MUST be the attempt-local isolated snapshot (``iso/checkout_scripts``)
  whose sha256 is recorded in ``evidence/<CARD>/source_manifest.json``.
* the only product entry point invoked is ``model_registry.calculate_registered_model``.
* expected values come exclusively from ``evidence/<CARD>/oracle.json``, written by
  ``scripts/oracle_<CARD>.py`` (standard library only; it never imports the product).
* every negative case is built in memory from a NEW ``deepcopy`` of the frozen base
  input - never round-tripped through a JSON parser - so a JSON-parser rejection can
  never masquerade as a model rejection.

Exit codes (verdict-carrying; a bookkeeping-only rc=0 is not allowed)
--------------------------------------------------------------------
  0 = pass: the positive path and the continuity positive are faithful to the frozen
      oracle within ``1e-9 * max(1, |expected|)`` AND every negative case was rejected
      with the target exception type (``ModelRegistryError``)
  1 = harness error: the runner could not even set up the observation (missing or
      unreadable evidence file, product import failure, unexpected internal exception).
      A harness error is NEVER reported as a pass and never as a case failure.
  2 = no verdict (期望缺失 / 保真不符): an expectation is missing from the frozen oracle
      (``positive.expected_float``, ``expected_output_shape``, tolerances), or the
      observed output is not faithful to it - wrong container, wrong length, wrong
      element type, non-finite element, year mismatch, or a value outside tolerance.
  3 = verdict is negative on the refusal side: at least one negative case was NOT
      rejected with the target exception type.

Precedence when several conditions hold: 1 > 2 > 3. Every triggered condition is listed
verbatim in ``exit_code_semantics.triggered``, so an rc=2 never hides an rc=3 condition.

The ``observations`` block is deliberately NOT part of the exit code: those entries are
design observations whose expectation is sometimes "no expectation asserted" (the
inclusive-bound probes), so they can neither pass nor fail the card.
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

TARGET_EXCEPTION = "ModelRegistryError"
RC_PASS = 0
RC_HARNESS = 1
RC_NO_VERDICT = 2
RC_NEGATIVES = 3


class HarnessError(Exception):
    """Condition that makes a verdict impossible to compute."""


def ascii_text(value):
    """ASCII-only rendering: the GBK console must never see a non-ASCII byte."""
    return str(value).encode("ascii", "backslashreplace").decode("ascii")


def sha256_file(path):
    try:
        with open(path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return None


def load_json(path):
    if not os.path.isfile(path):
        raise HarnessError("missing evidence file: " + path)
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:  # noqa: BLE001
        raise HarnessError("unreadable evidence file %s (%s: %s)"
                           % (path, type(exc).__name__, exc))


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
        raise HarnessError("unknown mutation kind: " + str(kind))
    return base


def call_product(model_registry, spec):
    return model_registry.calculate_registered_model(
        model_id=spec["model_id"], base_revenue=spec["base_revenue"],
        drivers=spec["drivers"], years=spec["years"])


def within(values, expected):
    if len(values) != len(expected):
        return False
    return all(abs(a - e) <= 1e-9 * max(1.0, abs(e)) for a, e in zip(values, expected))


def fidelity(value, years, shape):
    """Structure / length / element-type / finiteness fidelity against the frozen shape.

    Returns (ok, problems, facts). ``shape`` is ``oracle.json``'s
    ``expected_output_shape``; a missing shape is itself an expectation gap.
    """
    problems = []
    facts = {"container": type(value).__name__, "length": None, "element_types": []}
    if not isinstance(value, list):
        problems.append("container is %s, expected list" % type(value).__name__)
    else:
        facts["length"] = len(value)
        if len(value) != len(years):
            problems.append("length %d != len(years) %d" % (len(value), len(years)))
        for index, item in enumerate(value):
            kind = type(item).__name__
            facts["element_types"].append(kind)
            if isinstance(item, bool) or not isinstance(item, float):
                problems.append("element %d has type %s, expected float" % (index, kind))
            elif not math.isfinite(item):
                problems.append("element %d is not finite" % index)
    if not isinstance(shape, dict):
        problems.append("frozen oracle carries no expected_output_shape (expectation missing)")
    else:
        if shape.get("container") != facts["container"]:
            problems.append("container %s != frozen %r" % (facts["container"], shape.get("container")))
        if shape.get("length") != facts["length"]:
            problems.append("length %r != frozen %r" % (facts["length"], shape.get("length")))
        frozen_type = shape.get("element_type")
        wrong = sorted(set(k for k in facts["element_types"] if k != frozen_type))
        if wrong:
            problems.append("element types %s != frozen %r" % (wrong, frozen_type))
        if shape.get("all_finite") and any(k != "float" for k in facts["element_types"]):
            problems.append("frozen oracle requires finite floats")
    return (not problems), problems, facts


def value_checks(actual, oracle_block, label):
    """Per-value comparison plus the expectation-present check."""
    result = {"label": label, "ok": False, "expectation_present": False,
              "length_ok": None, "per_value": [], "problems": []}
    if oracle_block is None:
        result["problems"].append("frozen oracle carries no %s block" % label)
        return result
    expected = oracle_block.get("expected_float")
    tolerances = oracle_block.get("tolerances")
    if expected is None or tolerances is None:
        result["problems"].append("frozen oracle carries no %s.expected_float/tolerances" % label)
        return result
    result["expectation_present"] = True
    if len(actual) != len(expected):
        result["length_ok"] = False
        result["problems"].append("length %d != expected length %d" % (len(actual), len(expected)))
        return result
    result["length_ok"] = True
    for index, (got, want, tol) in enumerate(zip(actual, expected, tolerances)):
        ok = abs(got - want) <= tol
        result["per_value"].append({"index": index, "actual": got, "expected": want,
                                    "tolerance": tol, "abs_diff": abs(got - want), "ok": ok})
        if not ok:
            result["problems"].append("value %d: |%r - %r| > %r" % (index, got, want, tol))
    result["ok"] = result["length_ok"] and all(item["ok"] for item in result["per_value"])
    return result


def run_all(args, result, emit):
    evidence = os.path.join(args.attempt, "evidence", args.card)
    input_doc = load_json(os.path.join(evidence, "input.json"))
    oracle_doc = load_json(os.path.join(evidence, "oracle.json"))
    cases_doc = load_json(os.path.join(evidence, "cases.json"))
    result["evidence_dir"] = evidence
    result["frozen_input_sha256"] = {
        "input.json": sha256_file(os.path.join(evidence, "input.json")),
        "oracle.json": sha256_file(os.path.join(evidence, "oracle.json")),
        "cases.json": sha256_file(os.path.join(evidence, "cases.json")),
    }
    for required in ("positive", "continuity_positive", "defaults"):
        if required not in input_doc:
            raise HarnessError("input.json has no %r block" % required)
    for required in ("positive", "continuity_positive", "defaults_expected_float"):
        if required not in oracle_doc:
            raise HarnessError("oracle.json has no %r block" % required)
    result["model_id"] = oracle_doc["model_id"]

    if not os.path.isdir(args.code_root):
        raise HarnessError("--code-root is not a directory: " + args.code_root)
    sys.path.insert(0, args.code_root)
    try:
        import model_registry  # noqa: E402
    except Exception as exc:  # noqa: BLE001
        raise HarnessError("product import failed from %s (%s: %s)"
                           % (args.code_root, type(exc).__name__, exc))
    result["model_registry_file"] = model_registry.__file__
    result["imported_module_sha256"] = {
        "model_registry.py": sha256_file(model_registry.__file__),
        "model_extensions.py": sha256_file(
            os.path.join(os.path.dirname(model_registry.__file__), "model_extensions.py")),
    }
    result["code_root_on_sys_path"] = args.code_root in sys.path
    if not hasattr(model_registry, TARGET_EXCEPTION):
        raise HarnessError("product module exposes no " + TARGET_EXCEPTION)
    if oracle_doc["model_id"] not in model_registry.MODEL_REGISTRY:
        raise HarnessError("model_id not registered: " + str(oracle_doc["model_id"]))

    spec = model_registry.MODEL_REGISTRY[oracle_doc["model_id"]]
    result["registry_metadata"] = {
        "model_id": spec.model_id,
        "required": list(spec.required),
        "optional": list(spec.optional),
        "defaults": {k: float(v) for k, v in dict(spec.defaults).items()},
        "dimensions": dict(spec.dimensions),
        "ratio_drivers": sorted(spec.ratio_drivers),
        "driver_bounds": {k: [None if b[0] is None else b[0], None if b[1] is None else b[1]]
                          for k, b in dict(spec.driver_bounds).items()},
        "formula": spec.formula,
    }

    # ---------------- positives ----------------
    shapes = oracle_doc.get("expected_output_shape") or {}
    for block in ("positive", "continuity_positive"):
        spec_in = copy.deepcopy(input_doc[block])
        entry = {"block": block, "years": list(spec_in["years"]), "raised": None,
                 "actual": None, "actual_repr": None, "fidelity": None,
                 "value_checks": None, "years_match_frozen": None}
        try:
            actual = call_product(model_registry, spec_in)
            entry["actual"] = [float(v) for v in actual] if isinstance(actual, list) else None
            entry["actual_repr"] = repr(actual)
            ok, problems, facts = fidelity(actual, spec_in["years"], shapes.get(block))
            entry["fidelity"] = {"ok": ok, "problems": problems, "facts": facts}
            if isinstance(actual, list) and all(
                    isinstance(v, float) and not isinstance(v, bool) for v in actual):
                entry["value_checks"] = value_checks(entry["actual"], oracle_doc.get(block), block)
            else:
                entry["value_checks"] = {"label": block, "ok": False, "expectation_present": None,
                                         "problems": ["actual is not a list of floats; "
                                                      "value comparison not attempted"]}
            frozen_years = oracle_doc.get(block, {}).get("years")
            entry["years_match_frozen"] = (list(spec_in["years"]) == frozen_years)
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = ascii_text(exc)
            entry["traceback"] = ascii_text(traceback.format_exc())
        entry["ok"] = bool(entry["raised"] is None
                           and entry["fidelity"] and entry["fidelity"]["ok"]
                           and entry["value_checks"] and entry["value_checks"]["ok"]
                           and entry["years_match_frozen"])
        result[block] = entry

    # ---------------- defaults case (NOT gating) ----------------
    dspec = copy.deepcopy(input_doc["defaults"])
    dactual = None
    try:
        dactual = call_product(model_registry, dspec)
        result["defaults"] = {
            "raised": None,
            "actual": [float(v) for v in dactual] if isinstance(dactual, list) else None,
            "expected": oracle_doc["defaults_expected_float"],
            "ok": within([float(v) for v in dactual], oracle_doc["defaults_expected_float"])
                  if isinstance(dactual, list) else False,
            "gating": False,
            "why": "documents the documented zero default for the optional drivers; non-gating",
        }
    except Exception as exc:  # noqa: BLE001
        result["defaults"] = {"raised": type(exc).__name__, "message": ascii_text(exc),
                              "expected": oracle_doc["defaults_expected_float"], "ok": False,
                              "gating": False,
                              "why": "documents the documented zero default for the optional drivers; non-gating"}

    # ---------------- observations (NOT part of the exit code) ----------------
    obs_expected = oracle_doc.get("observation_expected") or {}
    for obs in cases_doc.get("extra_observations", []):
        entry = {"id": obs["id"], "expectation": obs.get("expectation"),
                 "kind": obs.get("kind", "input_replay"), "why": obs.get("why", ""),
                 "gating": False}
        try:
            if obs.get("kind") == "input_replay":
                mutated = copy.deepcopy(input_doc[obs["input"]])
            else:
                mutated = apply_case(copy.deepcopy(input_doc[obs.get("base_input", "positive")]), obs)
                for driver, value in (obs.get("also_set_driver") or {}).items():
                    mutated["drivers"][driver] = copy.deepcopy(value)
            value = call_product(model_registry, mutated)
            entry["raised"] = None
            entry["actual"] = [float(v) for v in value] if isinstance(value, list) else None
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
                entry["matches_expected"] = within(entry["actual"] or [], obs_expected[obs["id"]]["expected_float"])
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = ascii_text(exc)
            entry["traceback"] = ascii_text(traceback.format_exc())
        result["observations"].append(entry)

    # ---------------- negatives ----------------
    for case in cases_doc["cases"]:
        base_key = case.get("base_input", "positive")
        base = copy.deepcopy(input_doc[base_key])
        entry = {"id": case["id"], "kind": case["kind"], "why": case["why"],
                 "expected": case["expected"], "base_input": base_key}
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = ascii_text(
                repr(mutated["drivers"])[:400] + " years=" + repr(mutated["years"])
                + " base=" + repr(mutated["base_revenue"]))
            call_product(model_registry, mutated)
            entry["raised"] = None
            entry["verdict"] = "FAIL_not_rejected"
        except Exception as exc:  # noqa: BLE001
            entry["raised"] = type(exc).__name__
            entry["message"] = ascii_text(exc)
            entry["traceback"] = ascii_text(traceback.format_exc())
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
        "target_exception": TARGET_EXCEPTION,
        "counting_rule": "only isinstance(exc, ModelRegistryError) counts as PASS; "
                         "ImportError/ModuleNotFoundError/FileNotFoundError are recorded as FAIL",
    }


def decide(result):
    triggered = []
    positive = result.get("positive") or {}
    continuity = result.get("continuity_positive") or {}
    negatives = result.get("negative_summary") or {}

    missing = []
    for block, entry in (("positive", positive), ("continuity_positive", continuity)):
        checks = entry.get("value_checks") or {}
        if entry.get("raised") is not None:
            missing.append("%s raised %s instead of producing a value" % (block, entry["raised"]))
        if not checks.get("expectation_present"):
            missing.append("%s expectation missing from the frozen oracle" % block)
        if entry.get("years_match_frozen") is False:
            missing.append("%s years differ from the frozen oracle" % block)
    fidelity_problems = []
    for block, entry in (("positive", positive), ("continuity_positive", continuity)):
        fid = entry.get("fidelity") or {}
        for problem in (fid.get("problems") or []):
            fidelity_problems.append("%s: %s" % (block, problem))
    value_problems = []
    for block, entry in (("positive", positive), ("continuity_positive", continuity)):
        checks = entry.get("value_checks") or {}
        for problem in (checks.get("problems") or []):
            value_problems.append("%s: %s" % (block, problem))

    if result.get("harness_error"):
        triggered.append("harness_error")
    if missing:
        triggered.append("expectation_missing")
    if fidelity_problems:
        triggered.append("fidelity_mismatch")
    if value_problems:
        triggered.append("value_out_of_tolerance")
    if negatives.get("failed"):
        triggered.append("negative_case_not_rejected")

    if "harness_error" in triggered:
        verdict, rc = "harness_error", RC_HARNESS
    elif triggered:
        verdict, rc = "fail", (RC_NEGATIVES if triggered == ["negative_case_not_rejected"]
                               else RC_NO_VERDICT)
    else:
        verdict, rc = "pass", RC_PASS

    result["verdict"] = {"verdict": verdict, "exit_code": rc}
    result["exit_code"] = rc
    result["exit_code_semantics"] = {
        "0": "pass: faithful positive + continuity and every negative rejected with the target exception",
        "1": "harness error: no observation could be set up; never a pass",
        "2": "no verdict: expectation missing or the output is not faithful to the frozen oracle",
        "3": "verdict negative: at least one negative case was not rejected with the target exception",
        "precedence": "1 > 2 > 3",
        "triggered": triggered,
        "expectation_missing": missing,
        "fidelity_problems": fidelity_problems,
        "value_problems": value_problems,
        "negative_failures": negatives.get("failed", []),
    }
    return result


def emit_result_lines(result, emit):
    meta = result.get("registry_metadata") or {}
    emit("card_id: %s" % result.get("card_id"))
    emit("model_id: %s" % result.get("model_id"))
    emit("code_root: %s" % ascii_text(result.get("code_root")))
    emit("model_registry_file: %s" % ascii_text(result.get("model_registry_file")))
    emit("imported_module_sha256: %s" % ascii_text(result.get("imported_module_sha256")))
    emit("frozen_input_sha256: %s" % ascii_text(result.get("frozen_input_sha256")))
    emit("registry formula: %s" % meta.get("formula"))
    emit("registry required: %s" % meta.get("required"))
    emit("registry optional: %s" % meta.get("optional"))
    emit("registry defaults: %s" % meta.get("defaults"))
    emit("registry ratio_drivers: %s" % meta.get("ratio_drivers"))
    emit("registry driver_bounds: %s" % meta.get("driver_bounds"))
    for block in ("positive", "continuity_positive"):
        entry = result.get(block) or {}
        checks = entry.get("value_checks") or {}
        emit("%s raised: %s" % (block, entry.get("raised")))
        emit("%s actual: %s" % (block, entry.get("actual")))
        emit("%s expected: %s" % (block, [c["expected"] for c in checks.get("per_value", [])]))
        emit("%s tolerances: %s" % (block, [c["tolerance"] for c in checks.get("per_value", [])]))
        emit("%s value_ok: %s" % (block, checks.get("ok")))
        emit("%s fidelity_ok: %s" % (block, (entry.get("fidelity") or {}).get("ok")))
        emit("%s fidelity_problems: %s" % (block, (entry.get("fidelity") or {}).get("problems")))
        emit("%s years_match_frozen: %s" % (block, entry.get("years_match_frozen")))
    defaults = result.get("defaults") or {}
    emit("defaults actual: %s" % defaults.get("actual"))
    emit("defaults expected: %s" % defaults.get("expected"))
    emit("defaults ok (not gating): %s" % defaults.get("ok"))
    for obs in result.get("observations", []):
        emit("observation: %s raised=%s actual=%s matches_compared=%s expect_equal=%s "
             "matches_expected_relation=%s matches_expected=%s %s"
             % (obs.get("id"), obs.get("raised"), obs.get("actual"), obs.get("matches_compared"),
                obs.get("expect_equal"), obs.get("matches_expected_relation"),
                obs.get("matches_expected"), obs.get("message", "")))
    for entry in result.get("negatives", []):
        emit("negative: %s %s %s - %s" % (entry["id"], entry["verdict"], entry.get("raised"),
                                          entry.get("message", "")))
    summary = result.get("negative_summary") or {}
    emit("negative summary: total=%s passed=%s failed=%s"
         % (summary.get("total"), summary.get("passed"), summary.get("failed")))
    semantics = result.get("exit_code_semantics") or {}
    emit("exit_code triggered: %s" % semantics.get("triggered"))
    emit("verdict: %s exit_code: %s" % ((result.get("verdict") or {}).get("verdict"),
                                        result.get("exit_code")))


def finalize(result, args, printed):
    result["printed_lines"] = list(printed)
    result["printed_sha256"] = hashlib.sha256(
        ("\n".join(printed) + "\n").encode("utf-8")).hexdigest()
    result["print_vs_file_rule"] = (
        "stdout.txt is the raw OS-level capture of this process's stdout; "
        "scripts/verify_card.py re-reads this file and asserts that its lines equal "
        "printed_lines and that printed_sha256 matches, so a printed number can never "
        "disagree with the recorded evidence.")
    payload = json.dumps(result, ensure_ascii=True, indent=1, sort_keys=False)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload + "\n")
    if args.run_result_out:
        with open(args.run_result_out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--code-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--run-result-out", default=None)
    args = parser.parse_args(argv)

    printed = []

    def emit(line):
        text = ascii_text(line)
        printed.append(text)
        sys.stdout.write(text + "\n")
        sys.stdout.flush()

    result = {
        "card_id": args.card,
        "model_id": None,
        "code_root": args.code_root,
        "entry_point": "model_registry.calculate_registered_model(model_id, base_revenue, drivers, years)",
        "attempt": args.attempt,
        "python_version": sys.version.split()[0],
        "python_executable": ascii_text(sys.executable),
        "registry_metadata": {},
        "positive": {},
        "continuity_positive": {},
        "defaults": {},
        "observations": [],
        "negatives": [],
        "harness_error": None,
    }
    try:
        run_all(args, result, emit)
    except BaseException as exc:  # noqa: BLE001 - any failure here is a harness failure
        result["harness_error"] = {"type": type(exc).__name__, "message": ascii_text(exc),
                                   "traceback": ascii_text(traceback.format_exc())}
        emit("harness_error: %s: %s" % (type(exc).__name__, ascii_text(exc)))
    decide(result)
    emit_result_lines(result, emit)
    finalize(result, args, printed)
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
