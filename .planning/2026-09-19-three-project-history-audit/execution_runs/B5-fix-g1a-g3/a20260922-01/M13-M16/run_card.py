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
      oracle within ``1e-9 * max(1, |expected|)`` AND the frozen negative-case set is
      internally consistent AND every negative case was rejected with the target exception
      type (``ModelRegistryError``)
  1 = harness error: the runner could not even set up the observation (missing or
      unreadable evidence file, product import failure, unexpected internal exception).
      A harness error is NEVER reported as a pass and never as a case failure.
  2 = no verdict (expectation missing / not faithful / expectation declaration inconsistent):
      an expectation is missing from the frozen oracle (``positive.expected_float``,
      ``expected_output_shape``, tolerances, ``negative_count``, ``negative_ids``), or the
      observed output is not faithful to it - wrong container, wrong length, wrong element
      type, non-finite element, year mismatch, or a value outside tolerance - or the frozen
      case set contradicts its own declared expectations (a case whose ``expected`` is
      missing or is not a non-empty string, a case count or id set that disagrees with the
      oracle, a duplicate case id, an unknown case kind, or a ``base_input`` that does not
      exist).
  3 = verdict is negative on the refusal side: at least one negative case was NOT
      rejected with the target exception type, or a case WAS rejected with an exception
      whose exact type name does not equal that case's declared ``expected``.

Precedence when several conditions hold: 1 > 2 > 3. Every triggered condition is listed
verbatim in ``exit_code_semantics.triggered``, so an rc=2 never hides an rc=3 condition.

Why the expectation-consistency block exists (independent review finding F-01, 2026-09-20):
revision r1 of this runner decided a negative case purely by ``isinstance(exc,
ModelRegistryError)`` and never read ``case["expected"]``, so ``cases.json``'s ``expected``
field was decorative metadata: renaming it to a different type, or deleting a whole negative
case, still produced rc=0. Both are now expectation gaps that yield rc=2, and the case count
and id set are cross-checked against ``oracle.json``.

Per-case declared-expectation enforcement (REM-21 / B5, propagated from M17-M20, 2026-09-21)
------------------------------------------------------------------------------------------
What follows closes the remaining half of F-01. Revision r2 of this runner still only ran a
SET-LEVEL check: ``expectation_gaps`` compared ``case["expected"]`` against the single type
the runner happens to apply (``TARGET_EXCEPTION``), so it judged the whole frozen set and never
verified - per case - that the exception actually RAISED by that case carries the declared
exact type name. A declaration naming a different (but still usable) type therefore produced
rc=2 without the case ever concluding.

This runner now enforces ``type(exc).__name__ == case["expected"]`` per case: EXACT TYPE-NAME
EQUALITY, never ``isinstance()``. ``ModelRegistryError`` is a subclass of ``ValueError``, so a
declared ``"ValueError"`` would silently pass under ``isinstance()``. A judged case whose raised
type name differs from its declaration gets the verdict ``FAIL_declared_expectation_mismatch``
and drives rc=3. Precedence is preserved: a declaration that is missing or not a non-empty
string is unusable, is reported as ``NOT_JUDGED_declaration_unusable``, is never counted as a
mismatch, and yields rc=2 BEFORE any case is judged. The SET-LEVEL check is retained for what
it alone can do - count/id/kind/``base_input`` consistency and the unusable-declaration gap -
and the declared-name decision has moved to the per-case comparison, which is strictly
stronger than the old "is it equal to TARGET_EXCEPTION" set-level proxy.

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
KNOWN_CASE_KINDS = ("set_driver_element", "set_driver", "set_driver_multi", "delete_driver",
                    "add_driver", "set_years", "set_base_revenue")


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


def expectation_gaps(cases_doc, oracle_doc, input_doc):
    """Consistency of the frozen case set with its own declared expectations.

    Independent review finding F-01: the runner used to decide a negative case purely by
    ``isinstance(exc, ModelRegistryError)`` and never read ``case["expected"]``, and it never
    checked the case count or the id set. Renaming a case's ``expected`` to another type, or
    deleting a whole negative case, therefore still produced rc=0. Every such inconsistency is
    an expectation gap and yields rc=2 (no verdict) instead of a silent pass.

    Returns (gaps, facts) where gaps is a list of human-readable strings.
    """
    gaps = []
    cases = cases_doc.get("cases")
    if not isinstance(cases, list) or not cases:
        gaps.append("cases.json carries no negative case list")
        return gaps, {"case_count": 0}

    ids = [case.get("id") for case in cases]
    duplicated = sorted(set(i for i in ids if ids.count(i) > 1))
    if duplicated:
        gaps.append("duplicate case ids in cases.json: %s" % duplicated)

    declared_count = oracle_doc.get("negative_count")
    if declared_count is None:
        gaps.append("oracle.json carries no negative_count (expectation missing)")
    elif declared_count != len(cases):
        gaps.append("cases.json has %d cases but oracle.json.negative_count is %r"
                    % (len(cases), declared_count))

    declared_ids = oracle_doc.get("negative_ids")
    if declared_ids is None:
        gaps.append("oracle.json carries no negative_ids (expectation missing)")
    else:
        missing = sorted(set(declared_ids) - set(ids))
        extra = sorted(set(ids) - set(declared_ids))
        if missing:
            gaps.append("cases.json is MISSING cases that oracle.json declares: %s" % missing)
        if extra:
            gaps.append("cases.json carries cases that oracle.json does not declare: %s" % extra)

    for case in cases:
        case_id = case.get("id")
        declared = case.get("expected")
        # SET-LEVEL check, narrowed by REM-21 / B5. It used to be
        # ``declared != TARGET_EXCEPTION``, i.e. it flagged ANY name other than the one type this
        # runner applies and answered "no verdict" (rc=2) for the whole frozen set. That proxy
        # could not distinguish "the declaration is unusable" from "the declaration is usable but
        # the case raised something else", and the latter is exactly what the per-case
        # enforcement below now decides with rc=3. So this check keeps only the part only it can
        # answer - a declaration that is not a non-empty string is a structural gap - and a
        # usable declaration that disagrees with the raised exact type name is reported per case
        # as FAIL_declared_expectation_mismatch (rc=3). No key is removed: this still feeds
        # ``expectation_consistency.gaps`` exactly as before for unusable declarations, which is
        # what the deletion arm of the B5 propagation exercises.
        if not (isinstance(declared, str) and declared.strip()):
            gaps.append("case %s declares an unusable expected=%r (expected a non-empty "
                        "exception type name)" % (case_id, declared))
        kind = case.get("kind")
        if kind not in KNOWN_CASE_KINDS:
            gaps.append("case %s uses unknown mutation kind %r" % (case_id, kind))
        base_key = case.get("base_input", "positive")
        if base_key not in input_doc:
            gaps.append("case %s references base_input %r which input.json does not contain"
                        % (case_id, base_key))

    # B5-fix G3 / F-1 (fix card B5-fix-g1a-g3, owner ruling "D, G1-a" 2026-09-22): the
    # contract's §2 key list is ADDITIVE and the contract forbids renaming existing fields
    # ("downstream evidence files were generated from them"). The historical key
    # ``declared_expectations`` has a real downstream reader:
    # execution_runs/M14/a20260919-01/recovery/consolidated_report.py:75 indexes
    # ``run["expectation_consistency"]["facts"]["declared_expectations"]`` and would KeyError
    # on a rename. So BOTH keys are emitted here, with the SAME value computed once: the
    # original key keeps its name and meaning; the contract-required name
    # ``declared_expectations_in_cases_json`` is ADDED, not substituted.
    declared_in_cases = sorted(set(str(case.get("expected")) for case in cases))
    facts = {
        "case_count": len(cases),
        "case_ids": ids,
        "oracle_negative_count": declared_count,
        "oracle_negative_ids": declared_ids,
        "declared_expectations": declared_in_cases,
        "declared_expectations_in_cases_json": declared_in_cases,
        "target_exception": TARGET_EXCEPTION,
    }
    return gaps, facts


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

    # ---------------- expectation consistency of the frozen case set (F-01) ----------------
    gaps, gap_facts = expectation_gaps(cases_doc, oracle_doc, input_doc)
    result["expectation_consistency"] = {
        "ok": not gaps,
        "gaps": gaps,
        "facts": gap_facts,
        "rule": "a case whose declared expected is missing or is not a non-empty string, or a "
                "case count / id set that disagrees with oracle.json, is an expectation gap and "
                "yields rc=2 - never a silent pass. A usable declaration that does not equal the "
                "exact type name of the exception that case raised is decided PER CASE as "
                "FAIL_declared_expectation_mismatch (rc=3), which is strictly stronger than the "
                "former set-level 'declared != target exception' proxy",
    }

    # ---------------- negatives ----------------
    # Frozen-declaration precondition (REM-21 / B5). ``expected`` MUST be a bare exception type
    # name (e.g. "ModelRegistryError"). The comparison further down is EXACT TYPE-NAME EQUALITY;
    # isinstance() must NOT be used, because ModelRegistryError is a subclass of ValueError and a
    # declared "ValueError" would then silently pass. A declaration that is missing or not a
    # non-empty string is unusable: it is a "no verdict" condition (rc=2) decided BEFORE any case
    # is judged, and such a case is never counted as a declaration mismatch.
    unusable_declared = [c.get("id") for c in cases_doc["cases"]
                         if not (isinstance(c.get("expected"), str) and c["expected"].strip())]
    cases_declared_ok = not unusable_declared
    result["cases_json_declared_expectations_usable"] = cases_declared_ok
    result["cases_json_unusable_declared_expectations"] = unusable_declared

    for case in cases_doc["cases"]:
        base_key = case.get("base_input", "positive")
        base = copy.deepcopy(input_doc[base_key])
        declared = case.get("expected")
        entry = {"id": case["id"], "kind": case["kind"], "why": case["why"],
                 "expected": declared, "declared": declared, "base_input": base_key,
                 "declared_expected": case.get("expected")}
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = ascii_text(
                repr(mutated["drivers"])[:400] + " years=" + repr(mutated["years"])
                + " base=" + repr(mutated["base_revenue"]))
            call_product(model_registry, mutated)
            entry["raised"] = None
            # Nothing was raised at all. The declaration is still readable, so the case IS judged:
            # it failed the refusal it declared, but this is NOT a declaration mismatch (the two
            # failure modes are mutually exclusive).
            declared_usable = isinstance(declared, str) and bool(declared.strip())
            entry["declared_expectation_ok"] = (False if declared_usable else None)
            entry["declared_expectation_mismatch"] = False
            entry["declared_expectation_not_met"] = (True if declared_usable else None)
            entry["judged"] = declared_usable
            entry["declared_expectation_comparison"] = (
                "nothing raised; cases.json declared %r" % (declared,))
            entry["verdict"] = ("FAIL_not_rejected" if declared_usable
                                else "NOT_JUDGED_declaration_unusable")
        except Exception as exc:  # noqa: BLE001
            raised_name = type(exc).__name__
            entry["raised"] = raised_name
            entry["message"] = ascii_text(exc)
            entry["traceback"] = ascii_text(traceback.format_exc())
            is_target = isinstance(exc, model_registry.ModelRegistryError)
            is_import_or_file = isinstance(exc, (ImportError, ModuleNotFoundError, FileNotFoundError))
            entry["is_target_type"] = is_target
            entry["is_import_or_file_error"] = is_import_or_file
            declared_usable = isinstance(declared, str) and bool(declared.strip())
            entry["declared_expectation_comparison"] = (
                "raised exact type name %r vs declared %r (exact-name equality, NOT isinstance)"
                % (raised_name, declared))
            if not declared_usable:
                # The frozen declaration is unusable, so this case is NOT JUDGED: it is neither a
                # mismatch nor a rejection failure. The declaration gap itself yields rc=2.
                entry["declared_expectation_ok"] = None
                entry["declared_expectation_mismatch"] = False
                entry["declared_expectation_not_met"] = None
                entry["judged"] = False
                entry["expectation_not_met_reason"] = (
                    "declared expectation is unusable (missing or not a non-empty string), so "
                    "the case cannot be judged against it")
                entry["verdict"] = "NOT_JUDGED_declaration_unusable"
            else:
                # THE delta (REM-21 / B5): exact type-name equality per case.
                declared_ok = (raised_name == declared)
                entry["declared_expectation_ok"] = declared_ok
                entry["declared_expectation_mismatch"] = not declared_ok
                # `declared_expectation_not_met` keeps its original meaning: the case did not
                # produce the declared refusal. `declared_expectation_mismatch` is the narrower
                # "an exception WAS raised, but its exact type name is not the declared one".
                entry["declared_expectation_not_met"] = not is_target
                entry["judged"] = True
                if not declared_ok:
                    entry["expectation_not_met_reason"] = (
                        "raised exact type name %r != declared %r" % (raised_name, declared))
                if not is_target:
                    entry["verdict"] = ("FAIL_wrong_exception_type" if not is_import_or_file
                                        else "FAIL_import_or_file_error")
                elif not declared_ok:
                    entry["verdict"] = "FAIL_declared_expectation_mismatch"
                else:
                    entry["verdict"] = "PASS_rejected"
        result["negatives"].append(entry)

    not_judged_ids = [e["id"] for e in result["negatives"]
                      if e["verdict"] == "NOT_JUDGED_declaration_unusable"]
    judged_failed = [e["id"] for e in result["negatives"]
                     if e["verdict"] not in ("PASS_rejected", "NOT_JUDGED_declaration_unusable")]
    mismatch_ids = [e["id"] for e in result["negatives"]
                    if e.get("declared_expectation_mismatch") is True]

    result["negative_counts"] = {
        "total": len(result["negatives"]),
        "passed": sum(1 for e in result["negatives"] if e["verdict"] == "PASS_rejected"),
        "not_rejected": sum(1 for e in result["negatives"] if e["raised"] is None),
        "wrong_exception_type": sum(1 for e in result["negatives"]
                                    if e.get("raised") is not None
                                    and e.get("is_target_type") is False
                                    and e.get("is_import_or_file_error") is False),
        "import_or_file_error": sum(1 for e in result["negatives"]
                                    if e.get("is_import_or_file_error") is True),
        "declared_expectation_mismatch": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_mismatch") is True),
        "declared_expectation_not_met": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_not_met") is True),
        "declared_expectation_missing_in_cases_json": len(unusable_declared),
    }

    result["negative_summary"] = {
        "total": len(result["negatives"]),
        "passed": sum(1 for e in result["negatives"] if e["verdict"] == "PASS_rejected"),
        "failed": judged_failed,
        "target_exception": TARGET_EXCEPTION,
        "counting_rule": "only isinstance(exc, ModelRegistryError) counts as PASS; "
                         "ImportError/ModuleNotFoundError/FileNotFoundError are recorded as FAIL",
        "expectation_consistency_ok": not gaps,
        "expectation_gaps": gaps,
        "not_judged": not_judged_ids,
        "declared_expectations_in_cases_json": sorted(
            {str(case.get("expected")) for case in cases_doc["cases"]}),
        "declared_expectation_comparison": ("exact exception type name == cases.json's per-case "
                                            "'expected' string (NOT isinstance)"),
        "declared_expectations_enforced": True,
        "declared_expectations_usable": cases_declared_ok,
        "verdicts_are_mutually_exclusive": True,
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
    cases_declared_ok = result.get("cases_json_declared_expectations_usable", True)
    unusable_declared = result.get("cases_json_unusable_declared_expectations") or []
    mismatch_ids = [e["id"] for e in result.get("negatives", [])
                    if e.get("declared_expectation_mismatch") is True]
    consistency = result.get("expectation_consistency") or {}
    if consistency and not consistency.get("ok", True):
        triggered.append("expectation_declaration_inconsistent")
    if not cases_declared_ok:
        triggered.append("cases_json_declared_expectation_missing:"
                         + ",".join(str(i) for i in unusable_declared))
    if missing:
        triggered.append("expectation_missing")
    if fidelity_problems:
        triggered.append("fidelity_mismatch")
    if value_problems:
        triggered.append("value_out_of_tolerance")
    if negatives.get("failed"):
        triggered.append("negative_case_not_rejected")
    if mismatch_ids:
        triggered.append("declared_expectation_mismatch:" + ",".join(mismatch_ids))

    if "harness_error" in triggered:
        verdict, rc = "harness_error", RC_HARNESS
    elif not cases_declared_ok or (consistency and not consistency.get("ok", True)) or missing \
            or fidelity_problems or value_problems:
        # rc=2 (NO VERDICT) is decided BEFORE any case can be judged: the frozen declaration
        # itself is missing/unusable, or an oracle expectation is absent/not faithful. A case
        # reported as NOT_JUDGED_declaration_unusable can therefore never, by itself, produce
        # rc=3.
        verdict, rc = "no_verdict", RC_NO_VERDICT
    elif triggered:
        verdict, rc = "fail", RC_NEGATIVES
    else:
        verdict, rc = "pass", RC_PASS

    result["verdict"] = {"verdict": verdict, "exit_code": rc}
    result["exit_code"] = rc
    mismatch_case_ids = [e["id"] for e in result.get("negatives", [])
                         if e.get("declared_expectation_mismatch") is True]
    not_judged_case_ids = [e["id"] for e in result.get("negatives", [])
                           if e.get("judged") is False
                           or e.get("verdict") == "NOT_JUDGED_declaration_unusable"]
    not_met_case_ids = [e["id"] for e in result.get("negatives", [])
                        if e.get("declared_expectation_not_met") is True]
    result["exit_code_semantics"] = {
        "0": "pass: faithful positive + continuity and every negative rejected with the target exception",
        "1": "harness error: no observation could be set up; never a pass",
        "2": "no verdict: an oracle expectation is missing or the output is not faithful to the "
             "frozen oracle, or the frozen per-case `expected` declaration is itself "
             "missing/unusable (decided BEFORE any case is judged)",
        "3": "verdict negative: at least one negative case was not rejected with the target "
             "exception, or was rejected with an exception whose exact type name does not equal "
             "that case's declared `expected`",
        "precedence": "1 > 2 > 3",
        "triggered": triggered,
        "expectation_missing": missing,
        "expectation_declaration_gaps": consistency.get("gaps", []),
        "fidelity_problems": fidelity_problems,
        "value_problems": value_problems,
        "negative_failures": negatives.get("failed", []),
        # ---- REM-21 / B5 per-case declared-expectation enforcement ----
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "declared_expectation_mismatch_case_ids": mismatch_case_ids,
        "declared_expectation_not_met_case_ids": not_met_case_ids,
        "not_judged_case_ids": not_judged_case_ids,
        "declaration_unusable_case_ids": [str(i) for i in unusable_declared],
        # NOTE: this runner's rc table (0/1/2/3) is already the frozen table, so NO rc value was
        # changed by REM-21 / B5 and the RC_* names are unchanged. Only the CLASSIFICATION inside
        # this table was made finer: rc=2 is now decided before any case is judged and never
        # hides an rc=3 condition (they are listed together in `triggered`).
        "rc_table_unchanged_by_rem21": True,
        "reason_namespace": (
            "FAIL_wrong_exception_type is a SUBSET of declared_expectation_mismatch WHEN THE "
            "DECLARATION IS USABLE; declared_expectation_mismatch is the narrower 'an exception "
            "WAS raised, but its exact type name != cases.json's declared expected' and is "
            "mutually exclusive with FAIL_not_rejected (nothing raised). "
            "NOT_JUDGED_declaration_unusable is an unusable-declaration outcome (rc=2, "
            "no_verdict): such a case is NOT a mismatch and never appears in "
            "declared_expectation_mismatch_case_ids."),
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
    consistency = result.get("expectation_consistency") or {}
    emit("expectation_consistency: ok=%s gap_count=%d facts=%s"
         % (consistency.get("ok"), len(consistency.get("gaps") or []),
            ascii_text(consistency.get("facts"))))
    for gap in consistency.get("gaps") or []:
        emit("expectation_gap: %s" % ascii_text(gap))
    for entry in result.get("negatives", []):
        emit("negative: %s declared_expected=%s verdict=%s raised=%s - %s"
             % (entry["id"], entry.get("declared_expected"), entry["verdict"],
                entry.get("raised"), entry.get("message", "")))
        emit("negative-declared-expectation: %s judged=%s declared=%s raised=%s "
             "declared_expectation_ok=%s declared_expectation_mismatch=%s comparison=%s"
             % (entry["id"], entry.get("judged"), entry.get("declared"), entry.get("raised"),
                entry.get("declared_expectation_ok"), entry.get("declared_expectation_mismatch"),
                entry.get("declared_expectation_comparison")))
    summary = result.get("negative_summary") or {}
    counts = result.get("negative_counts") or {}
    emit("negative summary: total=%s passed=%s failed=%s"
         % (summary.get("total"), summary.get("passed"), summary.get("failed")))
    emit("negative declared-expectation counts: mismatch=%s not_met=%s "
         "missing_in_cases_json=%s not_judged=%s declared_expectations=%s enforced=%s comparison=%s"
         % (counts.get("declared_expectation_mismatch"), counts.get("declared_expectation_not_met"),
            counts.get("declared_expectation_missing_in_cases_json"), summary.get("not_judged"),
            summary.get("declared_expectations_in_cases_json"),
            summary.get("declared_expectations_enforced"),
            summary.get("declared_expectation_comparison")))
    semantics = result.get("exit_code_semantics") or {}
    emit("exit_code triggered: %s" % semantics.get("triggered"))
    emit("cases_json_declared_expectations_usable: %s unusable=%s"
         % (semantics.get("cases_json_declared_expectations_usable"),
            semantics.get("declaration_unusable_case_ids")))
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
