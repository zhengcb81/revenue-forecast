"""B5 / REM-21 batch M25-M28 - build the patched runner from the historical runner.

Reads  : <PLAN>/execution_runs/M25/a20260919-01/scripts/run_card.py   (READ-ONLY, never written)
Writes : <ATTEMPT>/M25-M28/run_card_before.py   (byte copy of the historical runner)
         <ATTEMPT>/M25-M28/run_card.py          (the deliverable: per-case enforcement added)
         <ATTEMPT>/M25-M28/runner.diff          (unified diff before -> after)

Every source substitute is exact and unique; the script fails loudly rather than
producing a partial patch.
"""
import hashlib
import os
import subprocess
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
OUTDIR = os.path.join(ATTEMPT, "M25-M28")
HISTORICAL = os.path.join(PLAN, "execution_runs", "M25", "a20260919-01", "scripts", "run_card.py")
EXPECTED_SHA = "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6"
EXPECTED_BYTES = 22720
GIT = r"C:\Program Files\Git\cmd\git.exe"


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sub_once(hay, needle, repl, tag):
    n = hay.count(needle)
    if n != 1:
        sys.exit("FATAL: anchor %r occurs %d times (must be exactly 1)" % (tag, n))
    return hay.replace(needle, repl)


# --------------------------------------------------------------------------- anchors
OLD_DOC = """  1 = an unguarded harness defect raised (fail loud; the only non-verdict code)
  2 = harness/bookkeeping could not produce a verdict (e.g. the positive path
      raised, so there is nothing to compare)
  3 = the verdict is negative (positive mismatch, continuity failure, or an
      unrejected negative)
"""

NEW_DOC = """  1 = an unguarded harness defect raised (fail loud; the only non-verdict code)
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
preempted the per-case judgement entirely. That gate is still EVALUATED and
reported verbatim (``case_contract_check`` / ``case_contract_problems``), but a
per-case ``expected`` value that differs from the set-level declaration is now a
JUDGED negative outcome (rc=3), not a harness defect (rc=1). The structural
contract checks (missing case_contract, case count, id list, unknown ids) still
fail loud with rc=1, so the interlocked cases.json <-> runner pair is unchanged.
"""

OLD_PRE = """                    case.update(copy.deepcopy(override["set"]))

    # ---------------- frozen case-contract gate (review finding P3-2) ----------------
"""

NEW_PRE = """                    case.update(copy.deepcopy(override["set"]))

    # ---- frozen per-case declaration (REM-21 / B5 / T1-8), decided BEFORE judging ----
    # `expected` MUST be a bare exception type name (e.g. "ModelRegistryError").
    # Comparison is EXACT TYPE-NAME EQUALITY. isinstance() must NOT be used:
    # ModelRegistryError is a subclass of ValueError, so a declared "ValueError"
    # would silently pass under isinstance().
    unusable_declared = [c.get("id") for c in cases_doc["cases"]
                         if not (isinstance(c.get("expected"), str) and c["expected"].strip())]
    cases_declared_ok = not unusable_declared

    # ---------------- frozen case-contract gate (review finding P3-2) ----------------
"""

OLD_GATE = """    contract = cases_doc.get("case_contract") or {}
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
        sys.stderr.write("HARNESS ERROR (rc=1): frozen case contract violated:\\n")
        for problem in contract_problems:
            sys.stderr.write("  - " + problem + "\\n")
        sys.stderr.flush()
        return 1
"""

NEW_GATE = """    contract = cases_doc.get("case_contract") or {}
    contract_problems = []
    # REM-21/B5 split, deliberately kept in ONE list for backward compatibility:
    #   * `structural_problems`             -> the interlocked cases.json <-> runner pair is broken
    #                                          (no case_contract, wrong case count/id list, unknown
    #                                          ids): a harness defect, still failing with rc=1.
    #   * `set_level_declaration_violations` -> a per-case `expected` differing from the whole-set
    #                                          declaration. This is now a JUDGED outcome driven by
    #                                          per-case enforcement (rc=3), NOT a harness defect, so
    #                                          it never enters the rc=1 gate.
    # `contract_problems` stays the union of both, so the existing key keeps its meaning.
    structural_problems = []
    set_level_declaration_violations = []
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
                "REM-21/B5 non-gating: cases whose `expected` is not %r: %s"
                % (declared, wrong_declaration))
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
        # ONLY a structural contract violation is a harness defect. A per-case `expected` that
        # differs from the whole-set declaration is judged per case instead (rc=2/rc=3).
        sys.stderr.write("HARNESS ERROR (rc=1): frozen case contract violated:\\n")
        for problem in structural_problems:
            sys.stderr.write("  - " + problem + "\\n")
        sys.stderr.flush()
        return 1
"""

OLD_RESULT = """        "negatives": [],
        "tolerances_ok": None,
        "defaults_ok": None,
        "harness_incomplete": None,
    }
"""

NEW_RESULT = """        "negatives": [],
        "tolerances_ok": None,
        "defaults_ok": None,
        "harness_incomplete": None,
        # REM-21/B5: the whole-set declaration gate is still evaluated and reported, but a
        # differing per-case `expected` is no longer a harness defect (see the module docstring).
        "case_contract_check": {
            "declared_expected_exception": contract.get("declared_expected_exception"),
            "expected_count": contract.get("expected_count"),
            "expected_ids": contract.get("expected_ids"),
            "cases_whose_expected_differs_from_declaration": wrong_declaration,
            "set_level_declaration_violations": set_level_declaration_violations,
            "structural_problems": structural_problems,
            "structural_gate_gating": True,
            "set_level_declaration_gating": False,
            "note": ("whole-set gate retained for fidelity with the frozen cases.json "
                     "case_contract; per-case enforcement (exact type-name equality) is the "
                     "authority that drives rc=3"),
        },
        "case_contract_problems": contract_problems,
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "cases_json_unusable_declared_expectations": unusable_declared,
    }
"""

OLD_NEG_LOOP = """    for case in cases_doc["cases"]:
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
"""

NEW_NEG_LOOP = """    # ---------------- negatives (PER-CASE `expected` ENFORCEMENT) ----------------
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
"""

OLD_TAIL = """    harness_incomplete = result["positive"].get("raised") is not None
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
"""

NEW_TAIL = """    harness_incomplete = result["positive"].get("raised") is not None
    # A NOT_JUDGED case (unusable declaration) is not a case judgement, so it must never, by
    # itself, be able to produce rc=3.
    negatives_ok = all(e["verdict"] == "PASS_rejected"
                       for e in result["negatives"] if e.get("judged"))
    positive_ok = bool(result.get("tolerances_ok"))
    continuity_ok = bool(result["continuity_positive"].get("ok"))
    mechanism_ok = bool(result["neg_card_mechanism_check"]["matched"])
    no_verdict_reason = ("cases_json_declared_expectation_missing:" + ",".join(unusable_declared)
                         if not cases_declared_ok else None)
    if harness_incomplete or not cases_declared_ok:
        # Precedence: an unusable frozen declaration (or an unusable environment) means no verdict
        # was possible, so rc=2 is issued BEFORE any case can be judged.
        verdict = "no_verdict"
        exit_code = 2
    elif positive_ok and negatives_ok and continuity_ok and mechanism_ok:
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
"""

OLD_PRINT = """    print("neg_card_mechanism matched:", result["neg_card_mechanism_check"]["matched"],
          "expected_substring=", result["neg_card_mechanism_check"]["expected_substring"],
          "observed=", result["neg_card_mechanism_check"]["observed_message"])
"""
NEW_PRINT = OLD_PRINT + """    print("negative counts:", result["negative_counts"])
    print("declared expectations enforced:",
          result["negative_summary"]["declared_expectations_enforced"],
          "cases_json_declared_expectations_usable:", cases_declared_ok)
    print("set-level case_contract declaration violations (non-gating):",
          result["case_contract_check"]["set_level_declaration_violations"])
"""

OLD_FINAL_DUMP = """    dump(args.out)
    if args.run_result_out:
        dump(args.run_result_out)
    print("verdict:", verdict, "exit_code:", exit_code)
    return exit_code
"""

NEW_FINAL_DUMP = """    dump(args.out)
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
"""


def main():
    with open(HISTORICAL, "rb") as fh:
        before = fh.read()
    got = sha256_bytes(before)
    if got != EXPECTED_SHA or len(before) != EXPECTED_BYTES:
        sys.exit("FATAL: historical runner mismatch: sha256=%s bytes=%d" % (got, len(before)))

    text = before.decode("utf-8")
    text = sub_once(text, OLD_DOC, NEW_DOC, "docstring")
    text = sub_once(text, OLD_PRE, NEW_PRE, "pre-gate")
    text = sub_once(text, OLD_GATE, NEW_GATE, "case-contract gate")
    text = sub_once(text, OLD_RESULT, NEW_RESULT, "result init")
    text = sub_once(text, OLD_NEG_LOOP, NEW_NEG_LOOP, "negative loop")
    text = sub_once(text, OLD_TAIL, NEW_TAIL, "verdict tail")
    text = sub_once(text, OLD_PRINT, NEW_PRINT, "print block")
    text = sub_once(text, OLD_FINAL_DUMP, NEW_FINAL_DUMP, "final dump block")

    after = text.encode("utf-8")

    os.makedirs(OUTDIR, exist_ok=True)
    before_path = os.path.join(OUTDIR, "run_card_before.py")
    after_path = os.path.join(OUTDIR, "run_card.py")
    with open(before_path, "wb") as fh:
        fh.write(before)
    with open(after_path, "wb") as fh:
        fh.write(after)

    # syntax gate: compile it before anyone runs it
    compile(text, after_path, "exec")

    diff_path = os.path.join(OUTDIR, "runner.diff")
    proc = subprocess.run(
        [GIT, "-c", "core.autocrlf=false", "-c", "core.safecrlf=false",
         "diff", "--no-index", "--no-color", "run_card_before.py", "run_card.py"],
        cwd=OUTDIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    diff = proc.stdout
    with open(diff_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(diff)

    added = sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff.splitlines() if ln.startswith("-") and not ln.startswith("---"))
    print("historical sha256 :", got, len(before))
    print("patched  sha256   :", sha256_bytes(after), len(after))
    print("diff added/removed:", added, removed, "->", diff_path)
    print("compile           : OK")


if __name__ == "__main__":
    main()
