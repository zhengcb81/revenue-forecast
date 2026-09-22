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
      raised, so there is nothing to compare, or cases.json's frozen per-case
      ``expected`` declaration is itself missing/unusable - decided BEFORE any
      case is judged, so the run issues verdict "no_verdict")
  3 = the verdict is negative (positive mismatch, continuity failure, an
      unrejected negative, or a raised exception whose exact type name does not
      equal the case's declared ``expected``)

Per-case ``expected`` enforcement (REM-21 / B5 / T1-8; propagated from M17-M20)
-----------------------------------------------------------------------------
``cases.json`` declares, per negative case, the bare exception type name the
product must raise (``"expected"``). The runner ENFORCES that declaration per
case: the raised exception's EXACT type name must equal the declared string.
``isinstance()`` must NOT be used, because ``ModelRegistryError`` is a subclass
of ``ValueError``, so a declared ``"ValueError"`` would silently pass under
``isinstance``. Precedence: a missing/unusable declaration is decided BEFORE any
case is judged and yields rc=2 (no verdict); such a case is reported as
``NOT_JUDGED_declaration_unusable`` and is never counted as a mismatch.

Before REM-21 this runner had a WHOLE-SET declaration gate only (every case's
``expected`` had to equal ``case_contract.declared_expected_exception``), which
is not per-case enforcement: it cannot name the offending case, it collapses the
"declaration mismatch" and "declaration unusable" outcomes into one rc, and it
preempted the per-case judgement entirely. Under the owner's G1-a execution
ruling (2026-09-22) that gate is no longer left non-gating: it is EXPLICITLY
ROUTED, and the routing is load-bearing on the exit code:

  * structural problems (missing case_contract, case count, id list, unknown
    ids) -> rc=1, UNCHANGED (harness/fixture/file fault);
  * a declaration that is unusable (missing / malformed / non-string
    ``expected``) -> rc=2 + ``no_verdict``, evaluated BEFORE any case is
    judged (frozen rc table, START_HERE L90-115);
  * a usable but different per-case ``expected`` -> rc=3, through the per-case
    exact type-name judgement AND asserted directly by the set-level route
    (the owner-mandated arm that was previously unreachable while the
    set-level gate aborted at rc=1);
  * a VALUE difference NEVER aborts at rc=1, and the gate is NEVER silent:
    ``case_contract_check.set_level_declaration_routing`` records the route.

The frozen ``cases.json`` ``case_contract.rule`` text still says a differing
``expected`` means "the harness refuses to issue a verdict (rc=1)". That frozen
text stays byte-unchanged (T1-11) and is registered as a KNOWN CONFLICT whose
owner ruling is 留置 (permanently registered on the books): the owner declined
to declare any precedence between the two frozen artifacts, and none is
asserted here. This runner implements the independent G1-a execution ruling.

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

    # ---- frozen per-case declaration (REM-21 / B5 / T1-8), decided BEFORE judging ----
    # `expected` MUST be a bare exception type name (e.g. "ModelRegistryError").
    # Comparison is EXACT TYPE-NAME EQUALITY. isinstance() must NOT be used:
    # ModelRegistryError is a subclass of ValueError, so a declared "ValueError"
    # would silently pass under isinstance().
    unusable_declared = [c.get("id") for c in cases_doc["cases"]
                         if not (isinstance(c.get("expected"), str) and c["expected"].strip())]
    cases_declared_ok = not unusable_declared

    # ---------------- frozen case-contract gate (review finding P3-2) ----------------
    # Before this gate the runner ignored cases.json[].expected and the case COUNT, so
    # rewriting a declaration or deleting a whole negative still produced rc=0. A harness
    # whose bookkeeping cannot notice a missing case is not verdict-carrying, so a violated
    # contract is a harness defect: fail loud with rc=1 instead of issuing a verdict.
    contract = cases_doc.get("case_contract") or {}
    contract_problems = []
    # REM-21/B5 split, deliberately kept in ONE list for backward compatibility:
    #   * `structural_problems`             -> the interlocked cases.json <-> runner pair is broken
    #                                          (no case_contract, wrong case count/id list, unknown
    #                                          ids): a harness defect, still failing with rc=1.
    #   * `set_level_declaration_violations` -> a per-case `expected` differing from the whole-set
    #                                          declaration: EXPLICITLY ROUTED under the owner's
    #                                          G1-a execution ruling (2026-09-22) - unusable value
    #                                          -> rc=2 + no_verdict before any case is judged;
    #                                          usable but different value -> rc=3 per case. It never
    #                                          enters the rc=1 gate AND is never left non-gating.
    # `contract_problems` stays the union of both, so the existing key keeps its meaning.
    structural_problems = []
    set_level_declaration_violations = []
    set_level_route_rc = None
    set_level_unusable_ids = []
    set_level_usable_diff_ids = []
    if not contract:
        structural_problems.append("cases.json has no case_contract block")
    else:
        declared = contract.get("declared_expected_exception")
        wrong_declaration = [case["id"] for case in cases_doc["cases"]
                             if case.get("expected") != declared]
        if wrong_declaration:
            set_level_declaration_violations.append(
                "cases whose `expected` is not %r: %s" % (declared, wrong_declaration))
            contract_problems.append(
                "G1-a routed (was: REM-21/B5 non-gating): cases whose `expected` is not %r: %s"
                % (declared, wrong_declaration))
            # ---- G1-a explicit routing of this gate (owner ruling 2026-09-22) ----
            #   * unusable value (missing / malformed / non-string) -> rc=2 + no_verdict,
            #     evaluated BEFORE any case is judged (frozen rc table START_HERE L90-115);
            #   * usable but different value -> rc=3, via the per-case exact type-name judge-
            #     ment (asserted directly in the exit-code decision below);
            #   * NEVER rc=1 for a value difference (rc=1 is structural only) and the gate is
            #     never left non-gating: its route participates in the final rc.
            set_level_unusable_ids = [c["id"] for c in cases_doc["cases"]
                                      if c.get("expected") != declared
                                      and not (isinstance(c.get("expected"), str)
                                               and c["expected"].strip())]
            set_level_usable_diff_ids = [c["id"] for c in cases_doc["cases"]
                                         if c.get("expected") != declared
                                         and isinstance(c.get("expected"), str)
                                         and c["expected"].strip()]
            if set_level_unusable_ids:
                set_level_route_rc = 2
            else:
                set_level_route_rc = 3  # wrong_declaration is non-empty here; values are usable
        ids = [case["id"] for case in cases_doc["cases"]]
        if len(ids) != contract.get("expected_count"):
            structural_problems.append("case count %d != declared %s"
                                       % (len(ids), contract.get("expected_count")))
        if ids != list(contract.get("expected_ids") or []):
            structural_problems.append("case id list %s != declared %s"
                                       % (ids, contract.get("expected_ids")))
        unknown = [i for i in ids if i not in ("NEG-CARD", "N01a", "N01b", "N01c", "N01d",
                                               "N02", "N03", "N04", "N05a", "N05b",
                                               "CONT-BREAK")]
        if unknown:
            structural_problems.append("unexpected negative ids: %s" % unknown)
    contract_problems.extend(structural_problems)
    if structural_problems:
        # G1-a: ONLY a structural contract violation (harness/fixture/file fault) is a harness
        # defect aborting at rc=1. A VALUE difference in `expected` never reaches this abort -
        # it is routed to rc=2 (unusable, before judging) or rc=3 (usable, per case) above.
        sys.stderr.write("HARNESS ERROR (rc=1): frozen case contract violated:\n")
        for problem in structural_problems:
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
        # REM-21/B5: the whole-set declaration gate is still evaluated and reported, and under
        # the owner's G1-a ruling (2026-09-22) it is now EXPLICITLY ROUTED (see the module
        # docstring): structural -> rc=1, unusable -> rc=2 + no_verdict before judging,
        # usable-but-different -> rc=3 per case; never non-gating, never rc=1 for a value
        # difference, and no precedence between the frozen rule text and the frozen rc table
        # is asserted (owner ruling on that conflict: 留置 / permanently registered).
        "case_contract_check": {
            "declared_expected_exception": contract.get("declared_expected_exception"),
            "expected_count": contract.get("expected_count"),
            "expected_ids": contract.get("expected_ids"),
            "cases_whose_expected_differs_from_declaration": wrong_declaration,
            "set_level_declaration_violations": set_level_declaration_violations,
            "structural_problems": structural_problems,
            "structural_gate_gating": True,
            "set_level_declaration_gating": True,
            "set_level_declaration_route_rc": set_level_route_rc,
            "set_level_unusable_case_ids": list(set_level_unusable_ids),
            "set_level_usable_diff_case_ids": list(set_level_usable_diff_ids),
            "set_level_declaration_routing": {
                "authority": "owner G1-a execution ruling (2026-09-22), implementing REM-21/T1-8",
                "structural_problems": "rc=1 unchanged (harness/fixture/file fault)",
                "declaration_unusable": "rc=2 + no_verdict, evaluated BEFORE any case is judged",
                "declaration_usable_but_different": "rc=3 via per-case exact type-name judgement",
                "value_difference_never_rc1": True,
                "never_left_nongating": True,
                "load_bearing": ("set_level_route_rc participates in the final exit-code "
                                 "decision below"),
            },
            "frozen_rule_text_conflict": {
                "status": "known conflict - owner ruling 留置 (permanently registered)",
                "frozen_rule_text": ("M25-M28 frozen cases.json case_contract.rule: a differing "
                                     "'expected' => the harness refuses to issue a verdict "
                                     "(rc=1)"),
                "frozen_rc_table": ("START_HERE.md L90-115 (T1-19): structural rc=1 / "
                                    "declaration unusable rc=2+no_verdict / mismatch rc=3"),
                "precedence_between_frozen_artifacts": "NOT asserted - owner declined to rule",
                "implementation_basis": "independent G1-a execution ruling",
                "frozen_artifacts_edited_by_this_card": False,
            },
            "note": ("whole-set gate retained for fidelity with the frozen cases.json "
                     "case_contract and EXPLICITLY ROUTED (G1-a); per-case enforcement "
                     "(exact type-name equality) drives rc=3, and the set-level route is "
                     "asserted in the exit-code decision"),
        },
        "case_contract_problems": contract_problems,
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "cases_json_unusable_declared_expectations": unusable_declared,
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
    # ---------------- negatives (PER-CASE `expected` ENFORCEMENT) ----------------
    # Each case carries a DECLARED expectation in the frozen cases.json. The runner must enforce
    # that declaration per case, not merely "some ModelRegistryError was raised": the declared
    # name is compared against the raised exception's EXACT type name.
    #   * not_rejected                  -> the call returned a value; nothing was raised, so this
    #                                      is NOT a declared-expectation mismatch.
    #   * declared_expectation_mismatch -> an exception WAS raised, but its exact type name is not
    #                                      the declared one.
    # A declaration that is missing/not a non-empty string is not a verdict at all: it is an
    # unusable frozen declaration, reported as NOT_JUDGED_declaration_unusable and decided as
    # "no verdict" (rc=2) BEFORE any case is judged.
    for case in cases_doc["cases"]:
        base_key = case.get("base_input", "positive")
        base = copy.deepcopy(input_doc[base_key])
        declared = case.get("expected")  # raw declaration; may be missing/None
        entry = {"id": case["id"], "kind": case["kind"], "why": case["why"],
                 "expected": declared, "declared": declared, "base_input": base_key}
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = (repr(mutated["drivers"])[:400]
                                           + " years=" + repr(mutated["years"])
                                           + " base=" + repr(mutated["base_revenue"]))
            call_product(model_registry, mutated)
            entry["raised"] = None
            # Nothing was raised: the declared expectation was certainly not met, but this is a
            # not_rejected failure, NOT a declaration MISMATCH (the two are exclusive).
            entry["declared_expectation_ok"] = False
            entry["declared_expectation_mismatch"] = False
            entry["declared_expectation_not_met"] = True
            entry["declared_expectation_comparison"] = (
                "nothing raised; cases.json declared " + repr(declared))
            entry["judged"] = True
            entry["expectation_not_met_reason"] = "no exception was raised"
            entry["verdict"] = "FAIL_not_rejected"
        except Exception as exc:  # noqa: BLE001
            raised_name = type(exc).__name__
            entry["raised"] = raised_name
            entry["message"] = str(exc)
            entry["traceback"] = traceback.format_exc()
            is_target = isinstance(exc, model_registry.ModelRegistryError)
            is_import_or_file = isinstance(exc, (ImportError, ModuleNotFoundError, FileNotFoundError))
            entry["is_target_type"] = is_target
            entry["is_import_or_file_error"] = is_import_or_file
            declared_usable = isinstance(declared, str) and bool(declared.strip())
            entry["declared_expectation_comparison"] = (
                "raised exact type name %r vs declared %r (exact-name comparison, NOT isinstance)"
                % (raised_name, declared))
            if not declared_usable:
                # The frozen declaration is unusable, so this case is NOT JUDGED: it is neither a
                # mismatch nor a rejection failure (the taxonomy is exclusive).
                entry["declared_expectation_ok"] = None
                entry["declared_expectation_mismatch"] = False
                entry["declared_expectation_not_met"] = None
                entry["judged"] = False
                entry["expectation_not_met_reason"] = (
                    "declared expectation is unusable (missing or not a non-empty string), so the "
                    "case cannot be judged against it")
                entry["verdict"] = "NOT_JUDGED_declaration_unusable"
            else:
                declared_ok = (raised_name == declared)  # exact type-name equality
                entry["declared_expectation_ok"] = declared_ok
                entry["declared_expectation_mismatch"] = not declared_ok
                entry["declared_expectation_not_met"] = not declared_ok
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
    mismatch_ids = [e["id"] for e in result["negatives"]
                    if e.get("declared_expectation_mismatch") is True]
    not_rejected_ids = [e["id"] for e in result["negatives"] if e["raised"] is None]
    result["negative_summary"] = {
        "total": len(result["negatives"]),
        "passed": sum(1 for e in result["negatives"] if e["verdict"] == "PASS_rejected"),
        # `failed` keeps its historical meaning verbatim (every non-PASS verdict), so downstream
        # evidence files generated from the field keep their meaning.
        "failed": [e["id"] for e in result["negatives"] if e["verdict"] != "PASS_rejected"],
        "failed_judged": [e["id"] for e in result["negatives"]
                          if e["verdict"] not in ("PASS_rejected",
                                                  "NOT_JUDGED_declaration_unusable")],
    }
    result["negative_counts"] = {
        "declared_expectation_mismatch": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_mismatch") is True),
        "declared_expectation_not_met": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_not_met") is True),
        "declared_expectation_missing_in_cases_json": len(unusable_declared),
    }
    result["negative_summary"].update({
        "not_judged": not_judged_ids,
        "judged": sum(1 for e in result["negatives"] if e.get("judged")),
        "declared_expectations_in_cases_json": sorted(
            {c["expected"] for c in cases_doc["cases"]
             if isinstance(c.get("expected"), str) and c["expected"].strip()}),
        "declared_expectation_comparison": ("exact exception type name == cases.json's per-case "
                                            "'expected' string (NOT isinstance)"),
        "declared_expectations_enforced": True,
        "declared_expectations_usable": cases_declared_ok,
        "classification_is_mutually_exclusive": True,
        "import_or_file_errors_never_pass": True,
        "target_exception": "model_registry.ModelRegistryError",
    })

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
    print("negative counts:", result["negative_counts"])
    print("declared expectations enforced:",
          result["negative_summary"]["declared_expectations_enforced"],
          "cases_json_declared_expectations_usable:", cases_declared_ok)
    print("set-level case_contract declaration violations (G1-a routed, route_rc=%s):"
          % set_level_route_rc,
          result["case_contract_check"]["set_level_declaration_violations"])

    harness_incomplete = result["positive"].get("raised") is not None
    # A NOT_JUDGED case (unusable declaration) is not a case judgement, so it must never, by
    # itself, be able to produce rc=3.
    negatives_ok = all(e["verdict"] == "PASS_rejected"
                       for e in result["negatives"] if e.get("judged"))
    positive_ok = bool(result.get("tolerances_ok"))
    continuity_ok = bool(result["continuity_positive"].get("ok"))
    mechanism_ok = bool(result["neg_card_mechanism_check"]["matched"])
    no_verdict_reason = ("cases_json_declared_expectation_missing:" + ",".join(unusable_declared)
                         if not cases_declared_ok else None)
    # ---- G1-a exit-code routing (owner ruling 2026-09-22); the whole-set gate is load-bearing
    # here - never non-gating, and a value difference never maps to rc=1:
    #   1. structural problems already returned rc=1 above (harness/fixture/file fault);
    #   2. an unusable declaration (missing / malformed / non-string `expected`) -> rc=2 +
    #      no_verdict. `unusable_declared` / `set_level_route_rc == 2` are evaluated BEFORE the
    #      case loop above, and this branch wins over every judgement below;
    #   3. a usable but different declaration -> rc=3: driven by the per-case exact type-name
    #      judgement AND asserted directly via `set_level_route_rc` so the set-level gate can
    #      never silently fall back to non-gating.
    set_level_forces_fail = (set_level_route_rc == 3)
    if harness_incomplete or not cases_declared_ok or set_level_route_rc == 2:
        # Precedence: an unusable frozen declaration (or an unusable environment) means no verdict
        # was possible, so rc=2 is issued BEFORE any case can be judged.
        verdict = "no_verdict"
        exit_code = 2
    elif (positive_ok and negatives_ok and continuity_ok and mechanism_ok
          and not set_level_forces_fail):
        verdict = "pass"
        exit_code = 0
    else:
        verdict = "fail"
        exit_code = 3
    result["harness_incomplete"] = harness_incomplete
    result["verdict"] = verdict
    result["no_verdict_reason"] = no_verdict_reason
    verdict_reasons = []
    if harness_incomplete:
        verdict_reasons.append("positive_raised:" + str(result["positive"].get("raised")))
    if not cases_declared_ok:
        verdict_reasons.append(no_verdict_reason)
    if not positive_ok:
        verdict_reasons.append("positive_out_of_tolerance")
    if not continuity_ok:
        verdict_reasons.append("continuity_positive_not_matched")
    if not mechanism_ok:
        verdict_reasons.append("neg_card_declared_mechanism_not_matched")
    if not_rejected_ids:
        verdict_reasons.append("negatives_not_rejected:" + ",".join(not_rejected_ids))
    if mismatch_ids:
        verdict_reasons.append("declared_expectation_mismatch:" + ",".join(mismatch_ids))
    if set_level_route_rc == 3 and not mismatch_ids:
        # Corner case where the per-case judgement somehow agrees but the set-level gate still
        # sees a usable-but-different declaration: the G1-a route itself forces rc=3.
        verdict_reasons.append("set_level_declaration_mismatch:" + ",".join(set_level_usable_diff_ids))
    result["verdict_reasons"] = verdict_reasons
    result["exit_code_semantics"] = {
        "harness_incomplete": harness_incomplete,
        "positive_ok": positive_ok,
        "continuity_ok": continuity_ok,
        "negatives_ok": negatives_ok,
        "neg_card_mechanism_ok": mechanism_ok,
        "defaults_ok_not_gating": result.get("defaults_ok"),
        "defaults_declared_check_not_gating": result["defaults_declared_check"].get("matches_expected"),
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "declaration_unusable_case_ids": list(unusable_declared),
        "declared_expectation_mismatch_case_ids": list(mismatch_ids),
        "declared_expectation_mismatch_ids": list(mismatch_ids),
        "declared_expectation_not_met_case_ids": [
            e["id"] for e in result["negatives"]
            if e.get("declared_expectation_not_met") is True],
        "not_judged_case_ids": list(not_judged_ids),
        "set_level_declaration_route": set_level_route_rc,
        "set_level_unusable_case_ids": list(set_level_unusable_ids),
        "set_level_usable_diff_case_ids": list(set_level_usable_diff_ids),
        "declaration_usability_decided_before_case_judgment": True,
        "value_difference_never_maps_to_rc1": True,
        "g1a_authority": "owner G1-a execution ruling 2026-09-22 (frozen rule-text conflict: 留置)",
        "reason_namespace": (
            "PASS_rejected | FAIL_not_rejected (nothing raised) | FAIL_wrong_exception_type | "
            "FAIL_import_or_file_error | FAIL_declared_expectation_mismatch | "
            "NOT_JUDGED_declaration_unusable. FAIL_wrong_exception_type is a SUBSET of "
            "declared_expectation_mismatch when the declaration is usable; "
            "NOT_JUDGED_declaration_unusable is an unusable-declaration outcome (rc=2, no "
            "verdict) and is NOT a mismatch and NOT part of "
            "declared_expectation_mismatch_case_ids."),
        "verdict_reasons": verdict_reasons,
        "no_verdict_reason": no_verdict_reason,
        "verdict": verdict,
        "exit_code": exit_code,
    }
    dump(args.out)
    if args.run_result_out:
        dump(args.run_result_out)
    print("verdict:", verdict, "exit_code:", exit_code)
    print("declared expectation enforcement: usable=%s mismatch_ids=%s not_judged_ids=%s "
          "mismatch_count=%s"
          % (cases_declared_ok, mismatch_ids, not_judged_ids,
             result["negative_counts"]["declared_expectation_mismatch"]))
    if no_verdict_reason:
        print("no_verdict reason:", no_verdict_reason)
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
