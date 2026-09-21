"""REM-21 M29-M31 patch builder.

Derives <ATTEMPT>\\M29-M31\\run_card.py from the byte-identical frozen copy
run_card_before.py (sha256 9ea69c72dced...).  Every replacement is anchored on a
verbatim excerpt of the BEFORE file, applied at most once, in order; the script
fails loudly if an anchor is missing or ambiguous.  Run with the batch's own
isolated interpreter and -B (no __pycache__ anywhere).
"""
import hashlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.abspath(os.path.join(HERE, "..", "..", "M29-M31"))

BEFORE = os.path.join(BATCH, "run_card_before.py")
AFTER = os.path.join(BATCH, "run_card.py")
REPORT = os.path.join(HERE, "patch_report.txt")

BEFORE_SHA = "9ea69c72dced41580aaf8c06481d766cd80dcc4b9fccac78b843d7d6095f42dd"

# ---------------------------------------------------------------- item 1
OLD_DOC = """  3 = negative verdict the comparison was possible and did not hold: the positive
                      path raised or fell outside tolerance, the continuity
                      positive did not match, or at least one negative case was NOT
                      rejected as expected
"""
NEW_DOC = """  3 = negative verdict the comparison was possible and did not hold: the positive
                      path raised or fell outside tolerance, the continuity
                      positive did not match, at least one negative case was NOT
                      rejected as expected, or a rejected case's exception type did
                      not match the per-case expectation DECLARED in cases.json

Additional per-case enforcement (REM-21 / B5 F-01)
--------------------------------------------------
cases.json carries a frozen per-case ``expected`` field naming the exception type
the case must raise.  This runner ENFORCES that declaration by comparing it with
the raised exception's EXACT type name (``type(exc).__name__ == case["expected"]``).
isinstance() must NOT be used for this comparison: ModelRegistryError is a subclass
of ValueError, so a declared "ValueError" would silently pass under isinstance().
An unusable declaration (missing, or not a non-empty string) is not a judgement at
all: it makes the declared-expectation set unusable and the run reports NO VERDICT
(rc=2) under reason ``cases_json_declared_expectation_missing:<ids>``, evaluated
BEFORE any case is judged.  rc=3 is used only when a judgement was possible and did
not hold.
"""

# ---------------------------------------------------------------- item 2
OLD_LOOP = """    # ---------------- negatives ----------------
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
"""
NEW_LOOP = """    # ---------------- negatives ----------------
    # REM-21 / B5 F-01: each case DECLARES its expected exception type in the frozen
    # cases.json (written by the independent oracle script).  The runner must enforce that
    # declaration, not merely "some ModelRegistryError was raised": the declared name is
    # compared against the exception's EXACT type name.  isinstance() must NOT be used for
    # this comparison, because ModelRegistryError is a subclass of ValueError and a
    # declared expectation of "ValueError" would then silently pass.
    #
    # Classification is MUTUALLY EXCLUSIVE:
    #   * not_rejected                  -> the call returned a value, so nothing was raised
    #                                      at all; this is NOT a declared-expectation mismatch.
    #   * declared_expectation_mismatch -> an exception WAS raised, but its exact type name
    #                                      is not the declared one.
    # A declaration that is missing/not a non-empty string is not a verdict at all: the
    # declared-expectation set is unusable and the run reports NO VERDICT (rc=2) before any
    # case is judged.
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
                 "expected": declared, "base_input": base_key}
        entry["declared"] = declared
        entry["declared_expectation_comparison"] = (
            "raised exact type name %r vs declared %r (exact-name comparison, not isinstance)"
            % (None, declared))
        try:
            mutated = apply_case(base, case)
            entry["mutated_input_repr"] = (repr(mutated["drivers"])[:400]
                                           + " years=" + repr(mutated["years"])
                                           + " base=" + repr(mutated["base_revenue"]))
            call_product(model_registry, mutated)
            entry["raised"] = None
            entry["declared_expectation_ok"] = False
            entry["declared_expectation_mismatch"] = False
            entry["declared_expectation_not_met"] = True
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
                "raised exact type name %r vs declared %r (exact-name comparison, not isinstance)"
                % (raised_name, declared))
            if not declared_usable:
                # The frozen declaration is unusable, so this case is NOT JUDGED: it is neither
                # a mismatch nor a rejection failure.
                entry["declared_expectation_ok"] = None
                entry["declared_expectation_mismatch"] = False
                entry["declared_expectation_not_met"] = None
                entry["judged"] = False
                entry["expectation_not_met_reason"] = (
                    "declared expectation is unusable (missing or not a non-empty string), so the "
                    "case cannot be judged against it")
                entry["verdict"] = "NOT_JUDGED_declaration_unusable"
            else:
                declared_ok = (raised_name == declared)  # EXACT type-name equality, never isinstance
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
"""

# ---------------------------------------------------------------- item 3
OLD_SUMMARY = """    result["negative_summary"] = {
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
"""
NEW_SUMMARY = """    not_judged_ids = [e["id"] for e in result["negatives"]
                      if e["verdict"] == "NOT_JUDGED_declaration_unusable"]
    judged_failed = [e["id"] for e in result["negatives"]
                     if e["verdict"] not in ("PASS_rejected", "NOT_JUDGED_declaration_unusable")]
    result["negative_summary"] = {
        "total": len(result["negatives"]),
        "passed": sum(1 for e in result["negatives"] if e["verdict"] == "PASS_rejected"),
        "not_judged": not_judged_ids,
        "failed": judged_failed,
        "verdicts_are_mutually_exclusive": True,
        "target_exception": "model_registry.ModelRegistryError",
        "declared_expectations_in_cases_json": sorted(
            {str(c.get("expected")) for c in cases_doc["cases"]}),
        "declared_expectation_comparison": ("exact exception type name == cases.json's per-case "
                                            "'expected' string (NOT isinstance)"),
        "declared_expectations_enforced": True,
        "declared_expectations_usable": cases_declared_ok,
        "classification_is_mutually_exclusive": True,
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
        "declared_expectation_mismatch": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_mismatch")),
        "declared_expectation_not_met": sum(
            1 for e in result["negatives"] if e.get("declared_expectation_not_met")),
        "declared_expectation_missing_in_cases_json": len(unusable_declared),
    }
"""

# ---------------------------------------------------------------- item 4
OLD_VERDICT = """    reasons = []
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
"""
NEW_VERDICT = """    not_rejected_ids = [e["id"] for e in result["negatives"] if e["raised"] is None]
    mismatch_ids = [e["id"] for e in result["negatives"] if e.get("declared_expectation_mismatch")]
    reasons = []
    if positive_raised:
        reasons.append("positive_raised:%s" % result["positive"].get("raised"))
    if not expectations_present:
        reasons.append("frozen_expectation_missing")
    if not cases_declared_ok:
        reasons.append("cases_json_declared_expectation_missing:" + ",".join(unusable_declared))
    if expectations_present and not positive_raised and not fidelity_ok:
        reasons.append("output_fidelity_mismatch")
    if expectations_present and not positive_raised and fidelity_ok and not tolerances_ok:
        reasons.append("positive_out_of_tolerance")
    if not continuity_ok:
        reasons.append("continuity_positive_not_matched")
    if not_rejected_ids:
        reasons.append("negatives_not_rejected:" + ",".join(not_rejected_ids))
    if mismatch_ids:
        reasons.append("declared_expectation_mismatch:" + ",".join(mismatch_ids))

    # rc=2 (no verdict) before any case can be judged when the frozen declaration itself is
    # missing or unusable; rc=3 only when a judgement was possible and did not hold.
    no_verdict = (not expectations_present or not cases_declared_ok
                  or (expectations_present and not positive_raised and not fidelity_ok))
    if no_verdict:
        exit_code = EXIT_NO_VERDICT
        verdict = "no_verdict"
    elif reasons:
        exit_code = EXIT_NEGATIVE
        verdict = "fail"
    else:
        exit_code = EXIT_PASS
        verdict = "pass"
"""

# ---------------------------------------------------------------- item 5
OLD_SEM = """    result["exit_code_semantics"].update({
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
"""
NEW_SEM = """    result["exit_code_semantics"].update({
        "positive_raised": positive_raised,
        "expectations_present": expectations_present,
        "cases_json_declared_expectations_usable": cases_declared_ok,
        "fidelity_ok": fidelity_ok,
        "positive_ok": bool(tolerances_ok and fidelity_ok and not positive_raised),
        "continuity_ok": continuity_ok,
        "negatives_ok": negatives_ok,
        "defaults_ok_not_gating": result.get("defaults_ok"),
        "not_rejected_case_ids": not_rejected_ids,
        "declared_expectation_mismatch_case_ids": mismatch_ids,
        "not_judged_case_ids": not_judged_ids,
        "reason_namespace": ("exclusive taxonomy: PASS_rejected | FAIL_not_rejected (nothing raised) | "
                             "FAIL_wrong_exception_type | FAIL_import_or_file_error | "
                             "FAIL_declared_expectation_mismatch | NOT_JUDGED_declaration_unusable. "
                             "FAIL_wrong_exception_type is a SUBSET of declared_expectation_mismatch "
                             "when the declaration is usable"),
        "verdict": verdict,
        "exit_code": exit_code,
    })
"""

# ---------------------------------------------------------------- item 6
OLD_NEGDOC = """            "first_required_driver": cases_doc.get("first_required_driver"),
            "frozen_expectation": "ModelRegistryError for every case",
            "continuity_first_positive": cases_doc.get("continuity_first_positive"),"""
NEW_NEGDOC = """            "first_required_driver": cases_doc.get("first_required_driver"),
            "frozen_expectation": ("per-case declared expectation from the frozen cases.json: %s"
                                   % ", ".join(result["negative_summary"][
                                       "declared_expectations_in_cases_json"])),
            "declared_expectations_enforced": True,
            "declared_expectation_comparison": result["negative_summary"][
                "declared_expectation_comparison"],
            "continuity_first_positive": cases_doc.get("continuity_first_positive"),"""

# ---------------------------------------------------------------- item 7
OLD_EMIT = """    emit("negative summary: %s" % result["negative_summary"])
    emit("verdict: %s exit_code: %d" % (verdict, exit_code))"""
NEW_EMIT = """    emit("negative declared-expectation comparison: %s"
         % result["negative_summary"]["declared_expectation_comparison"])
    emit("negative declared-expectation mismatches: %d"
         % result["negative_counts"]["declared_expectation_mismatch"])
    emit("negative summary: %s" % result["negative_summary"])
    emit("verdict: %s exit_code: %d" % (verdict, exit_code))"""

ITEMS = [
    ("1_docstring", OLD_DOC, NEW_DOC),
    ("2_negative_loop", OLD_LOOP, NEW_LOOP),
    ("3_summary_and_counts", OLD_SUMMARY, NEW_SUMMARY),
    ("4_verdict_and_rc", OLD_VERDICT, NEW_VERDICT),
    ("5_exit_code_semantics", OLD_SEM, NEW_SEM),
    ("6_negative_results_doc", OLD_NEGDOC, NEW_NEGDOC),
    ("7_stdout_emit", OLD_EMIT, NEW_EMIT),
]


def main():
    with open(BEFORE, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    before_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if before_sha != BEFORE_SHA:
        raise SystemExit("FATAL: run_card_before.py sha256 %s != expected %s"
                         % (before_sha, BEFORE_SHA))

    report = []
    report.append("BEFORE sha256 %s bytes %d" % (before_sha, len(text.encode("utf-8"))))
    out = text
    for name, old, new in ITEMS:
        count = out.count(old)
        if count != 1:
            raise SystemExit("FATAL: anchor %s matched %d times (expected exactly 1)"
                             % (name, count))
        start_line = out[:out.index(old)].count("\n") + 1
        out = out.replace(old, new, 1)
        report.append("item %-24s anchor_line=%d old_lines=%d new_lines=%d"
                      % (name, start_line, old.count("\n"), new.count("\n")))

    with open(AFTER, "w", encoding="utf-8", newline="") as handle:
        handle.write(out)
    after_sha = hashlib.sha256(out.encode("utf-8")).hexdigest()
    report.append("AFTER  sha256 %s bytes %d" % (after_sha, len(out.encode("utf-8"))))
    report.append("rc constants unchanged: %s"
                  % [ln for ln in out.splitlines() if ln.startswith("EXIT_")])

    with open(REPORT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(report) + "\n")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
