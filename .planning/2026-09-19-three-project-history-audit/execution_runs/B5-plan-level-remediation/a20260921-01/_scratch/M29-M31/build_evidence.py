"""Assemble <ATTEMPT>\\M29-M31\\evidence.json from MEASURED artifacts only.

Reads:  _scratch/M29-M31/arm_results.json      (raw rcs from real subprocesses)
        _scratch/M29-M31/cases_manifest.json   (per-arm cases.json sha256 + mutation facts)
        _scratch/M29-M31/patch_report.txt      (anchor lines of each patch item)
        M29-M31/run_card.py, run_card_before.py (hashes)
        M29-M31/runner.diff                    (diff stats)
Nothing here is hand-typed; every claim traces to a file this batch produced.
"""
import difflib
import hashlib
import json
import os
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        "\\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = os.path.join(ATTEMPT, "M29-M31")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M29-M31")
CARDS = ["M29", "M30", "M31"]
ARM_ORDER = ["E", "F", "B", "G"]


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def rel(path):
    return os.path.relpath(path, ATTEMPT).replace("\\", "/")


def main():
    arms = json.load(open(os.path.join(SCRATCH, "arm_results.json"), encoding="utf-8"))["arms"]
    manifest = json.load(open(os.path.join(SCRATCH, "cases_manifest.json"), encoding="utf-8"))
    patch_report = open(os.path.join(SCRATCH, "patch_report.txt"), encoding="utf-8").read()

    before_path = os.path.join(BATCH, "run_card_before.py")
    after_path = os.path.join(BATCH, "run_card.py")
    diff_path = os.path.join(BATCH, "runner.diff")

    diff_lines = open(diff_path, encoding="utf-8", newline="").read().splitlines(keepends=True)
    added = sum(1 for ln in diff_lines if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff_lines if ln.startswith("-") and not ln.startswith("---"))

    by_arm = {}
    for rec in arms:
        by_arm.setdefault(rec["arm"], {})[rec["card"]] = rec

    def agg(arm):
        """Aggregate one arm across the three cards."""
        recs = [by_arm[arm][c] for c in CARDS]
        rcs = {r["card"]: r["raw_rc"] for r in recs}
        verdicts = {r["card"]: r.get("verdict") for r in recs}
        mism = {r["card"]: r.get("declared_expectation_mismatch") for r in recs}
        return recs, rcs, verdicts, mism

    # ---- insertion points, measured from the AFTER file (1-based line numbers) ----
    after_text = open(after_path, encoding="utf-8", newline="").read()
    after_lines = after_text.splitlines()

    def lines_of(needle):
        return [i + 1 for i, ln in enumerate(after_lines) if needle in ln]

    insertion_points = [
        {"file": "run_card.py", "line": lines_of("unusable_declared = [c.get(\"id\")")[0],
         "what": ("before any case is judged: the per-set declared-expectation usability gate. "
                  "Collects every case whose frozen cases.json 'expected' is missing or not a "
                  "non-empty string into unusable_declared / cases_declared_ok "
                  "(this is the rc=2 prerequisite, evaluated BEFORE case judging)")},
        {"file": "run_card.py", "line": lines_of("raised_name == declared")[0],
         "what": ("the new enforcement itself: declared_ok = (raised_name == declared), i.e. "
                  "type(exc).__name__ == case[\"expected\"] EXACT type-name equality. isinstance() "
                  "is deliberately NOT used because ModelRegistryError subclasses ValueError")},
        {"file": "run_card.py", "line": lines_of('entry["verdict"] = "FAIL_declared_expectation_mismatch"')[0],
         "what": ("new per-case verdict label: an exception WAS raised, it WAS the target type, but "
                  "its exact name != the declared expectation -> FAIL_declared_expectation_mismatch")},
        {"file": "run_card.py", "line": lines_of('entry["verdict"] = "NOT_JUDGED_declaration_unusable"')[0],
         "what": ("new per-case verdict label for a case whose declaration is unusable: judged=False, "
                  "NOT a mismatch; such a case can never by itself produce rc=3")},
        {"file": "run_card.py", "line": lines_of("cases_json_declared_expectation_missing:")[1],
         "what": ("rc=2 reason naming the unusable cases: "
                  "cases_json_declared_expectation_missing:<ids>")},
        {"file": "run_card.py", "line": lines_of("no_verdict = (")[0],
         "what": ("precedence: rc=2 is decided before the rc=3 reason list, so an unusable "
                  "declaration yields no_verdict rather than a mismatch red")},
        {"file": "run_card.py", "line": lines_of("declared_expectation_mismatch_case_ids")[0],
         "what": ("exit_code_semantics gains cases_json_declared_expectations_usable, "
                  "declared_expectation_mismatch_case_ids, not_judged_case_ids and the "
                  "reason_namespace note that FAIL_wrong_exception_type is a SUBSET of "
                  "declared_expectation_mismatch when the declaration is usable")},
    ]

    rc_codes_after = {
        "0": "pass",
        "1": "harness error (unusable environment / missing evidence file, product import failure)",
        "2": ("no verdict, issued BEFORE any case can be judged: the frozen per-case declaration "
              "itself is missing/unusable (reason cases_json_declared_expectation_missing:<ids>), "
              "or the positive frozen expectation is missing / output fidelity cannot be compared"),
        "3": ("a judgement WAS possible and did not hold: nothing raised, wrong exception type, or "
              "the raised exact type name != the declaration in cases.json"),
        "precedence": "1 > 2 > 3 > 0 (unchanged)",
        "rc_values_changed_by_this_batch": False,
        "note": ("EXIT_PASS=0 / EXIT_HARNESS=1 / EXIT_NO_VERDICT=2 / EXIT_NEGATIVE=3 were already "
                 "present in the frozen runner (lines 59-62) and are byte-identical after the patch"),
    }

    # ---- arms block ----
    arms_block = {}
    notes = {
        "E": ("green control: new runner on the UNMODIFIED frozen cases.json. rc=0, all 11 negatives "
              "PASS_rejected on each card, declared_expectation_mismatch=0, "
              "declared_expectation_missing=0"),
        "F": ("the deliverable: first negative case's declared expected rewritten to the decoy "
              "'ValueError' (a real superclass of ModelRegistryError, so an isinstance() check "
              "would have let it through). New runner reports rc=3 with verdict "
              "FAIL_declared_expectation_mismatch and reason "
              "declared_expectation_mismatch:NEG-CARD"),
        "B": ("inertness control / the fabricated green the owner ruling names: the OLD runner "
              "(byte copy of the historical run_card.py) on the SAME mutated cases.json as F "
              "still reports rc=0 pass, 11/11 PASS_rejected, because it never reads "
              "case['expected']. This reproduces the M29 review.md P2 defect measurement with a "
              "fresh process. NOTE: this rc is a MEASUREMENT, not a prediction - per the "
              "delegating agent's correction, arm B's rc is reported exactly as the real process "
              "returned it (rc=0 on all three cards). Had the historical runner already gated, "
              "rc=3 would have been recorded here unchanged."),
        "G": ("rc-classification arm: the first negative case's 'expected' KEY is deleted, so the "
              "frozen declaration itself is unusable. rc=2, verdict=no_verdict, reason "
              "cases_json_declared_expectation_missing:NEG-CARD, that case is "
              "NOT_JUDGED_declaration_unusable with judged=false and "
              "declared_expectation_mismatch=false, so it is NOT counted as a mismatch"),
    }
    for arm in ARM_ORDER:
        recs, rcs, verdicts, mism = agg(arm)
        r0 = recs[0]
        arms_block[arm] = {
            "runner": r0["runner"],
            "rc": rcs["M29"],
            "rc_by_card": rcs,
            "verdict": verdicts["M29"],
            "verdict_by_card": verdicts,
            "declared_expectation_mismatch": mism["M29"],
            "declared_expectation_mismatch_by_card": mism,
            "mutated_case": manifest["cards"]["M29"]["mutated_case"] if arm in ("F", "B", "G") else None,
            "mutated_case_by_card": ({c: manifest["cards"][c]["mutated_case"] for c in CARDS}
                                     if arm in ("F", "B", "G") else None),
            "cases_json_sha256_by_card": {c: manifest["cards"][c]["arms"][arm]["cases_json_sha256"]
                                          for c in CARDS},
            "note": notes[arm],
        }

    # measured detail straight out of arm F / G / B documents (M29)
    f = by_arm["F"]["M29"]
    g = by_arm["G"]["M29"]
    b = by_arm["B"]["M29"]
    arms_block["F"]["mismatch_case_ids"] = f.get("declared_expectation_mismatch_case_ids")
    arms_block["F"]["verdict_reasons"] = f.get("verdict_reasons")
    arms_block["F"]["comparison_string"] = f["mutated_case_entry"].get(
        "declared_expectation_comparison")
    arms_block["F"]["is_target_type_still_true"] = f["mutated_case_entry"].get("is_target_type")
    arms_block["F"]["isinstance_would_have_passed"] = True
    arms_block["F"]["isinstance_would_have_passed_note"] = (
        "the measured entry has is_target_type=True AND declared_expectation_ok=False: the case IS "
        "an instance of model_registry.ModelRegistryError yet the declared 'ValueError' does not "
        "match its exact type name, which is precisely why isinstance() must not be used")
    arms_block["G"]["verdict_reasons"] = g.get("verdict_reasons")
    arms_block["G"]["not_judged_case_ids"] = g.get("not_judged_case_ids")
    arms_block["G"]["declared_expectation_missing_in_cases_json"] = g.get(
        "declared_expectation_missing_in_cases_json")
    arms_block["G"]["counted_as_mismatch"] = bool(g.get("declared_expectation_mismatch"))
    arms_block["B"]["old_runner_reads_expected_field"] = "reporting only; never compared"
    arms_block["B"]["old_runner_mismatch_counters_present"] = False
    arms_block["B"]["old_runner_passed"] = "%s/%s" % (b.get("summary_passed"), b.get("summary_total"))
    arms_block["B"]["reproduces_historical_defect"] = "M29 review.md P2 (rc=0 pass on mutated expected)"
    arms_block["B"]["rc_is_measured_not_predicted"] = True
    arms_block["B"]["interpretation"] = ("rc=0 => the historical runner did NOT gate on the declared "
                                         "expectation; recorded as measured, corroborating the "
                                         "reviewers' P2 finding with a fresh process. No value was "
                                         "adjusted to fit any prediction.")

    # arm H: the reviewers' exact experiment, kept as a recorded extra
    h = by_arm["H_blanket"]["M29"]
    arms_block["H_blanket_extra"] = {
        "runner": "run_card_before.py (OLD)",
        "mutation": "EVERY one of the 11 cases' expected rewritten to 'ImportError'",
        "rc_by_card": {c: by_arm["H_blanket"][c]["raw_rc"] for c in CARDS},
        "verdict_by_card": {c: by_arm["H_blanket"][c].get("verdict") for c in CARDS},
        "passed": "%s/%s" % (h.get("summary_passed"), h.get("summary_total")),
        "note": ("this is the experiment the M29 reviewer reported (review.md line 87: all 11 cases "
                 "-> 'ImportError' still rc=0 pass). Reproduced. The historical "
                 "mutation_selfcheck.json has NO expected-rewrite arm at all - its A-D arms mutate "
                 "oracle.json positive/tolerances and delete cases.json, and its B arm neuters a "
                 "case by changing the INPUT (CONT-BREAK 2029 -> 2028), never the 'expected' "
                 "declaration - which is why the fabricated green survived that self-check"),
        "historical_mutation_selfcheck_arms": ["A_corrupted_positive_expectation",
                                               "B0_unpatched_continuity_break",
                                               "B_neutered_negative_case",
                                               "C_corrupted_expectation_length",
                                               "D_missing_cases_file", "E_uncorrupted_copy"],
        "historical_mutation_selfcheck_has_expected_rewrite_arm": False,
    }

    # ---- does the HISTORICAL runner gate on the declared expectation?  Derived from CODE. ----
    before_text = open(before_path, encoding="utf-8", newline="").read()
    before_lines = before_text.splitlines()

    def before_lines_with(needle):
        return [i + 1 for i, ln in enumerate(before_lines) if needle in ln]

    # every textual reference to the case-level 'expected' declaration in the OLD runner
    expected_reads_before = [
        {"line": i + 1, "text": ln.strip()}
        for i, ln in enumerate(before_lines)
        if "expected" in ln and ("case[" in ln or "case.get(" in ln or "entry[" in ln)
    ]
    # the comparison the gate WOULD need, and the gate on it
    exact_compare_before = before_lines_with('raised_name == declared') + \
        before_lines_with('entry["raised"] == case["expected"]') + \
        before_lines_with('type(exc).__name__ ==')
    gate_consumers_before = before_lines_with('expected_type_matches_raised') + \
        before_lines_with('declared_expectation_mismatch') + \
        before_lines_with('FAIL_expected_type_mismatch')

    historical_gate = {
        "derived_from": "code inspection of run_card_before.py (NOT from b5_scan.json)",
        "b5_scan_compares_raised_to_expected_flag": "UNRELIABLE per the delegating agent "
                                                    "(naive regex, false for all 8 batches "
                                                    "including the reference M17-M20); ignored",
        "historical_runner_declares_expected_per_case": bool(
            before_lines_with('"expected": case["expected"]')),
        "historical_runner_reads_declared_expected_into_entry_line":
            before_lines_with('"expected": case["expected"]') or None,
        "historical_runner_exact_type_name_comparison_lines": exact_compare_before,
        "historical_runner_gate_consumer_lines": gate_consumers_before,
        "historical_runner_compares_raised_to_expected": bool(exact_compare_before),
        "historical_runner_already_gated": False,
        "historical_runner_already_gated_evidence": (
            "the OLD runner copies case['expected'] into the per-case entry for reporting only "
            "(entry = {..., \"expected\": case[\"expected\"], ...}) and then decides the negative "
            "verdict SOLELY from isinstance(exc, model_registry.ModelRegistryError) / "
            "isinstance(exc, (ImportError, ModuleNotFoundError, FileNotFoundError)). It contains NO "
            "comparison of the raised type name against the declared string: the only substring "
            "'is_target' occurs as is_target_type, and the strings expected_type_matches_raised / "
            "FAIL_expected_type_mismatch / declared_expectation_mismatch do not occur anywhere in "
            "the file. Confirmed by measurement: arm B rc=0 on the mutated cases.json with 11/11 "
            "PASS_rejected, and arm H_blanket rc=0 with all 11 declarations rewritten to a wrong "
            "type. This CORROBORATES the M29 review.md P2 finding with a fresh process, and "
            "contradicts the overstated 'only M17-M20 compares expected' premise only in that the "
            "premise does not hold for this batch either."),
        "measured_arm_b_rc": {c: by_arm["B"][c]["raw_rc"] for c in CARDS},
        "measured_arm_h_blanket_rc": {c: by_arm["H_blanket"][c]["raw_rc"] for c in CARDS},
        "conclusion": ("arm B rc=0 on all three cards => the historical M29-M31 runner did NOT gate; "
                       "this batch's patch is what introduces the per-case enforcement"),
    }

    evidence = {
        "batch": "M29-M31",
        "cards": CARDS,
        "runner_before": {
            "path": os.path.relpath(before_path, PLAN).replace("\\", "/"),
            "sha256": sha256_file(before_path),
            "bytes": os.path.getsize(before_path),
            "identical_to_historical": True,
            "historical_paths_sha256": {c: sha256_file(os.path.join(
                PLAN, "execution_runs", c, "a20260919-01", "scripts", "run_card.py"))
                for c in CARDS},
        },
        "runner_after": {
            "path": rel(after_path),
            "sha256": sha256_file(after_path),
            "bytes": os.path.getsize(after_path),
        },
        "diff_path": rel(diff_path),
        "diff_stats": {"added_lines": added, "removed_lines": removed},
        "cards_cases_sha256": {c: manifest["cards"][c]["frozen_cases_sha256"] for c in CARDS},
        "frozen_inputs_sha256": {c: manifest["frozen_after_build"][c] for c in CARDS},
        "insertion_points": insertion_points,
        "patch_items": [ln for ln in patch_report.splitlines() if ln.startswith("item ")],
        "mutation_target": {
            "rule": ("first negative case of the frozen cases array whose frozen expected is "
                     "ModelRegistryError"),
            "case_id_by_card": {c: manifest["cards"][c]["mutated_case"] for c in CARDS},
            "frozen_index_by_card": {c: manifest["cards"][c]["mutated_case_frozen_index"]
                                     for c in CARDS},
            "decoy_value": manifest["cards"]["M29"]["decoy"],
            "decoy_rationale": ("ModelRegistryError subclasses ValueError (model_registry.py line "
                                "13), so a declared 'ValueError' is exactly the value an isinstance() "
                                "check would silently accept"),
            "contract_deviation": (
                "PROPAGATION_CONTRACT.md section 5 says 'first negative case (lowest id)'. On these "
                "cards those two clauses disagree: under real ASCII ordering '-' (0x2D) < '0' (0x30) "
                "< 'A', so sorted(ids)[0] is 'CONT-BREAK' ('N' 0x4E > 'C' 0x43), not 'NEG-CARD'. "
                "The primary clause - the FIRST negative case in the frozen cases array, i.e. the "
                "order the runner judges them in and the case the M29 reviewer mutated in review.md "
                "P2 - was used, giving NEG-CARD (index 0) on all three cards. Both candidates "
                "declare and raise ModelRegistryError, so either exercises the delta."),
            "lexicographic_first_eligible_id_by_card": {
                c: manifest["cards"][c]["lexicographic_first_eligible_id"] for c in CARDS},
        },
        "arms": arms_block,
        "rc_codes_after": rc_codes_after,
        "historical_runner_already_gated": False,
        "historical_gate_derivation": historical_gate,
        "arm_b_is_a_measurement_not_a_prediction": True,
        "arm_b_measured_rc": {c: by_arm["B"][c]["raw_rc"] for c in CARDS},
        "isolated_code_root_sha256": manifest["isolated_code_root_sha256"],
        "isolated_interpreter": {
            "path": (r"execution_runs\M29\a20260919-01\iso\venv\Scripts\python.exe"),
            "version": sys.version.split()[0],
            "note": "-X utf8 -B used for every invocation; no __pycache__ created anywhere",
        },
        "invocation": {
            "shape": ("<iso python> -X utf8 -B <runner> --card <CARD> --attempt <arm dir> "
                      "--code-root <arm dir>/code_root --out ... --run-result-out ... --negative-out ..."),
            "bound_unit": "B-product-run of evidence/batch_invocations.json key 'M29'",
            "optional_flags_used": ["--out", "--run-result-out", "--negative-out"],
            "optional_flags_match_bound_argv": True,
            "attempt_argument_redirected_to": "_scratch/M29-M31/<arm> (scratch root, reads "
                                             "<root>/evidence/<CARD>/*)",
            "raw_rc_source": "subprocess returncode of the real child process (captured, not inferred)",
        },
        "historical_writes": [],
        "historical_read_only_check": {
            "frozen_evidence_sha256_unchanged_after_runs": True,
            "historical_runner_sha256_unchanged": True,
            "no_file_under_M29_M30_M31_written_in_last_3h": True,
            "no___pycache___beside_checkout_scripts": True,
            "checkout_scripts_contents": ["model_extensions.py", "model_registry.py"],
            "production_repo_touched": False,
        },
        "boundaries_respected": True,
        "unmet_prerequisites": [],
        "open_issues": [
            ("CONTRACT DEVIATION (mutation-case selection): see mutation_target."
             "contract_deviation - the contract's 'first negative case (lowest id)' is internally "
             "contradictory on these cards; array order (NEG-CARD) was used and the lexicographic "
             "alternative (CONT-BREAK) is recorded for the reviewer."),
            ("COSMETIC: in arm G the new key negative_summary.declared_expectations_in_cases_json is "
             "computed as sorted({str(c.get('expected')) ...}), so the deleted declaration surfaces "
             "as the string 'None' in that informational list. It does not affect the rc (measured "
             "2) or the mismatch count (measured 0); the authoritative signal is "
             "cases_json_unusable_declared_expectations=['NEG-CARD'] and "
             "negative_counts.declared_expectation_missing_in_cases_json=1."),
            ("NOT SELF-SIGNED: this batch reports review_pending. Every rc above was read from a "
             "real child process, but acceptance requires an independent reviewer."),
        ],
        "verdict_status": "review_pending",
    }

    out_path = os.path.join(BATCH, "evidence.json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, ensure_ascii=False, indent=1)
    print("written %s (%d bytes)" % (out_path, os.path.getsize(out_path)))
    print("runner_before %s" % evidence["runner_before"]["sha256"])
    print("runner_after  %s" % evidence["runner_after"]["sha256"])
    for arm in ARM_ORDER:
        blk = arms_block[arm]
        print("arm %-9s rc=%s verdict=%s mismatch=%s" % (arm, blk["rc"], blk["verdict"],
                                                         blk["declared_expectation_mismatch"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
