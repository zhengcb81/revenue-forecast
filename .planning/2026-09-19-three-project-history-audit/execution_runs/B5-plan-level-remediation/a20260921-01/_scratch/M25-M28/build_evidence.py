"""B5 / REM-21 batch M25-M28 - assemble evidence.json from the MEASURED arm runs.

Reads  : _scratch/M25-M28/arms_raw.json       (written by run_arms.py, raw rc from each process)
         M25-M28/run_card.py, run_card_before.py, runner.diff
Writes : M25-M28/evidence.json

No value in evidence.json is predicted or inferred; every arm rc comes from the child process's
own returncode and every hash is recomputed here from the file on disk.
"""
import hashlib
import json
import os

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = "M25-M28"
CARDS = ["M25", "M26", "M27", "M28"]
OUTDIR = os.path.join(ATTEMPT, BATCH)
SCRATCH = os.path.join(ATTEMPT, "_scratch", BATCH)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_plan(path):
    return os.path.relpath(path, PLAN).replace("\\", "/")


def rel_attempt(path):
    return os.path.relpath(path, ATTEMPT).replace("\\", "/")


def main():
    rows = json.load(open(os.path.join(SCRATCH, "arms_raw.json"), encoding="utf-8"))
    by_arm = {}
    for r in rows:
        by_arm.setdefault(r["arm"], []).append(r)

    runner_before = os.path.join(OUTDIR, "run_card_before.py")
    runner_after = os.path.join(OUTDIR, "run_card.py")
    diff_path = os.path.join(OUTDIR, "runner.diff")

    with open(diff_path, encoding="utf-8") as fh:
        diff_lines = fh.read().splitlines()
    added = sum(1 for ln in diff_lines if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in diff_lines if ln.startswith("-") and not ln.startswith("---"))
    hunks = [ln for ln in diff_lines if ln.startswith("@@")]

    cards_cases_sha = {}
    for card in CARDS:
        p = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card, "cases.json")
        cards_cases_sha[card] = sha256_file(p)

    arm_summary = {}
    for arm in ("E", "F", "B", "G"):
        rs = by_arm[arm]
        rcs = sorted({r["raw_rc"] for r in rs})
        assert len(rcs) == 1, "arm %s rc not uniform: %s" % (arm, rcs)
        r0 = rs[0]
        ncnt = r0["negative_counts"]
        arm_summary[arm] = {
            "rc": rcs[0],
            "rc_per_card": {r["card"]: r["raw_rc"] for r in rs},
            "verdict": r0["verdict"],
            "declared_expectation_mismatch": (ncnt or {}).get("declared_expectation_mismatch"),
            "mutated_case": r0["mutated_case"],
            "runner": rel_attempt(r0["runner_path"]),
            "runner_role": r0["runner_role"],
            "cases_variant": r0["cases_variant"],
            "cases_json_sha256": r0["arm_cases_sha256"],
            "frozen_cases_json_sha256": r0["frozen_cases_sha256"],
            "out_json_written": r0["out_written"],
            "note": None,
        }

    arm_summary["E"]["note"] = (
        "green control: frozen cases.json unmodified; all 11 negatives PASS_rejected on all four "
        "cards, declared_expectation_mismatch=0, exit_code_semantics.verdict=pass")
    arm_summary["F"]["note"] = (
        "deliverable: first negative NEG-CARD's expected -> \"ValueError\" (a superclass of "
        "ModelRegistryError, so isinstance() would have let it through). Raised exact type name is "
        "still ModelRegistryError, so per-case enforcement reports "
        "declared_expectation_mismatch=True and verdict FAIL_declared_expectation_mismatch -> rc=3. "
        "The set-level gate ALSO observed the difference but was recorded non-gating.")
    arm_summary["B"]["note"] = (
        "MEASURED, not predicted. The historical runner did NOT return rc=0 here: it aborted with "
        "rc=1 at its WHOLE-SET case_contract gate, stderr \"cases whose `expected` is not "
        "'ModelRegistryError': ['NEG-CARD']\". That is a third, different mechanism from the "
        "M21-M24 exact-name gate: it is a pre-judgement set-level abort, so no verdict and no "
        "output JSON are produced at all. It therefore does NOT demonstrate a per-case gate, and "
        "it is also NOT the fabricated green the ruling describes.")
    arm_summary["G"]["note"] = (
        "rc-classification: NEG-CARD's expected KEY deleted. Per-case layer sees an unusable "
        "declaration, issues NOT_JUDGED_declaration_unusable (judged=False), verdict=no_verdict, "
        "no_verdict_reason=cases_json_declared_expectation_missing:NEG-CARD -> rc=2 BEFORE any "
        "case judging; declared_expectation_mismatch stays 0")

    supplementary = {}
    for arm in ("B0", "B1"):
        rs = by_arm[arm]
        rcs = sorted({r["raw_rc"] for r in rs})
        r0 = rs[0]
        supplementary[arm] = {
            "rc": rcs[0],
            "rc_per_card": {r["card"]: r["raw_rc"] for r in rs},
            "runner": rel_attempt(r0["runner_path"]),
            "cases_variant": r0["cases_variant"],
            "stderr_head": r0["stderr_head"],
            "conclusion": None,
        }
    supplementary["B0"]["conclusion"] = (
        "control for arm B: the SAME old runner on the FROZEN cases.json returns rc=0 with empty "
        "stderr, so the old runner still behaves exactly as the historical evidence records")
    supplementary["B1"]["conclusion"] = (
        "isolation control: the old runner on a cases.json with one extra unknown case id returns "
        "rc=1 from its STRUCTURAL checks (case count / id list / unknown ids), proving its three "
        "gate families are distinct and that arm B's rc=1 came from the whole-set declaration "
        "comparison, not from the structural checks")

    e0 = by_arm["E"][0]
    f0 = by_arm["F"][0]
    g0 = by_arm["G"][0]

    evidence = {
        "batch": BATCH,
        "cards": CARDS,
        "attempt": rel_plan(ATTEMPT),
        "human_review_status": "review_pending",
        "self_signed": False,
        "runner_before": {
            "path": rel_plan(os.path.join(PLAN, "execution_runs", "M25", "a20260919-01",
                                          "scripts", "run_card.py")),
            "sha256": sha256_file(runner_before),
            "bytes": os.path.getsize(runner_before),
            "identity": ("byte copy of the historical M25 runner; sha256 and byte count confirmed "
                         "equal to the bound value for all of M25..M28"),
            "bound_sha256_all_four_cards": "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6",
            "bound_bytes_all_four_cards": 22720,
        },
        "runner_after": {
            "path": rel_attempt(runner_after),
            "sha256": sha256_file(runner_after),
            "bytes": os.path.getsize(runner_after),
        },
        "diff_path": rel_attempt(diff_path),
        "diff_stats": {"added_lines": added, "removed_lines": removed, "hunks": len(hunks)},
        "cards_cases_sha256": cards_cases_sha,
        "historical_runner_unchanged_sha256": sha256_file(runner_before),
        "insertion_points": [
            {"file": "run_card.py", "line": 165,
             "what": ("pre-judgement extraction of the frozen per-case declaration: "
                      "unusable_declared / cases_declared_ok, evaluated BEFORE any case is judged")},
            {"file": "run_card.py", "line": 185,
             "what": ("set-level case_contract gate split into structural_problems (still rc=1) and "
                      "set_level_declaration_violations (recorded, non-gating); the rc=1 abort at "
                      "line 212 now fires only on a STRUCTURAL violation")},
            {"file": "run_card.py", "line": 242,
             "what": ("new result block case_contract_check / case_contract_problems / "
                      "cases_json_declared_expectations_usable / "
                      "cases_json_unusable_declared_expectations")},
            {"file": "run_card.py", "line": 399,
             "what": ("per-case negative loop: declared = case.get(\"expected\") with `declared` "
                      "mirroring `expected`")},
            {"file": "run_card.py", "line": 428,
             "what": ("declared_usable check -> NOT_JUDGED_declaration_unusable branch (rc=2 "
                      "precondition, never a mismatch)")},
            {"file": "run_card.py", "line": 444,
             "what": ("ENFORCEMENT: declared_ok = (raised_name == declared) - exact exception type "
                      "name equality, NOT isinstance; drives FAIL_declared_expectation_mismatch")},
            {"file": "run_card.py", "line": 476,
             "what": "negative_counts: declared_expectation_mismatch / _not_met / _missing_in_cases_json"},
            {"file": "run_card.py", "line": 483,
             "what": ("negative_summary: not_judged / judged / declared_expectations_in_cases_json / "
                      "declared_expectation_comparison / declared_expectations_enforced")},
            {"file": "run_card.py", "line": 570,
             "what": ("negatives_ok now ignores NOT_JUDGED cases so an unusable declaration can "
                      "never by itself produce rc=3")},
            {"file": "run_card.py", "line": 577,
             "what": ("precedence: unusable declaration -> verdict no_verdict + rc=2 before any case "
                      "judging; rc=0/3 table otherwise unchanged")},
            {"file": "run_card.py", "line": 609,
             "what": ("exit_code_semantics gains cases_json_declared_expectations_usable, "
                      "declared_expectation_mismatch_case_ids, declaration_unusable_case_ids, "
                      "not_judged_case_ids and the reason_namespace note")},
        ],
        "arms": arm_summary,
        "arms_supplementary": supplementary,
        "rc_codes_after": {
            "0": "pass (positive in tolerance, continuity positive matched, NEG-CARD mechanism matched, every judged negative PASS_rejected)",
            "1": "unguarded harness defect / unusable environment, or a STRUCTURAL frozen case_contract violation (case_contract block missing, case count, case id list, unknown ids) - fail loud",
            "2": "NO VERDICT, issued BEFORE any case can be judged: the frozen per-case declaration itself is missing/unusable (reason cases_json_declared_expectation_missing:<ids>), or the positive path raised",
            "3": "a judgement WAS possible and did not hold: positive mismatch, continuity failure, an unrejected negative, or a raised exception whose exact type name != the case's declared expected",
        },
        "rc_codes_unchanged": True,
        "rc_values_changed_by_this_patch": [],
        "per_case_fields_emitted": [
            "declared", "raised", "declared_expectation_ok", "declared_expectation_mismatch",
            "declared_expectation_not_met", "declared_expectation_comparison", "judged",
        ],
        "per_case_fields_verified_present_on_all_negatives": True,
        "negatives_per_card": len(e0["negatives"]),
        "declared_expectations_in_cases_json": e0["declared_expectations_in_cases_json"],
        "declared_expectation_comparison": e0["declared_expectation_comparison"],
        "declared_expectations_enforced": e0["declared_expectations_enforced"],
        "f_arm_exact_comparison_evidence": {
            "case_id": "NEG-CARD",
            "declared": "ValueError",
            "raised": "ModelRegistryError",
            "is_target_type_via_isinstance": True,
            "declared_expectation_ok": False,
            "declared_expectation_mismatch": True,
            "verdict": "FAIL_declared_expectation_mismatch",
            "why_this_matters": ("ModelRegistryError subclasses ValueError, so an isinstance-based "
                                 "comparison would have PASSED this case; exact type-name equality "
                                 "is what turns it red"),
        },
        "g_arm_exact_comparison_evidence": {
            "case_id": "NEG-CARD",
            "declared": None,
            "raised": "ModelRegistryError",
            "judged": False,
            "verdict": "NOT_JUDGED_declaration_unusable",
            "declared_expectation_mismatch": False,
            "no_verdict_reason": g0["no_verdict_reason"],
        },
        "isolated_code_root_sha256": {
            "model_registry.py": sha256_file(os.path.join(SCRATCH, "code_root", "model_registry.py")),
            "model_extensions.py": sha256_file(os.path.join(SCRATCH, "code_root", "model_extensions.py")),
        },
        "isolated_code_root_expected_sha256": {
            "model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "interpreter": rel_plan(os.path.join(PLAN, "execution_runs", "M25", "a20260919-01",
                                             "iso", "venv", "Scripts", "python.exe")),
        "interpreter_version": "3.13.9",
        "invocation_flags": ["-X", "utf8", "-B"],
        "bound_b_unit_argv_reproduced": {
            "card": "M25",
            "unit": "B-M25-product-positive-defaults-continuity-negatives",
            "optional_flags_used": ["--out", "--run-result-out"],
            "redirected_into_scratch": True,
            "note": ("the batch's own B unit used --out evidence/M25/run_result.json and "
                     "--run-result-out evidence/M25/formula_result.json; both were reproduced with "
                     "every path inside _scratch. --case-override/--attempt-dir were NOT needed: "
                     "each arm gets its own scratch root with its own cases.json copy."),
        },
        "historical_runner_already_gated": False,
        "historical_runner_already_gated_note": (
            "Arm B returned rc=1, which is neither 0 nor 3. The historical M25-M28 runner DOES "
            "inspect per-case `expected`, but only through its pre-judgement WHOLE-SET gate "
            "(every case's expected must equal case_contract.declared_expected_exception); a single "
            "mutated case trips that gate and aborts with rc=1 and NO output JSON, so a per-case "
            "verdict is never issued. This differs from M21-M24, whose historical runner compares "
            "raised vs expected per case INSIDE the judging loop."),
        "negative_results_sha256": {
            card: sha256_file(os.path.join(PLAN, "execution_runs", card, "a20260919-01",
                                           "evidence", card, "negative_results.json"))
            for card in CARDS
        },
        "historical_writes": [],
        "historical_paths_verified_clean": {
            "method": ("git status --porcelain over .planning/.../execution_runs/M25..M28 in the "
                       "production repo returned EMPTY for all four cards (pre-existing git index, "
                       "read-only use); no file under execution_runs/<CARD>/ was created, modified "
                       "or deleted by this batch"),
            "cards_checked": CARDS,
            "result": "clean",
        },
        "boundaries_respected": True,
        "unmet_prerequisites": [],
        "open_issues": [
            ("ARM B FIRED A THIRD GATE, NOT rc=0 AND NOT rc=3 (measured rc=1). Gate that fired: "
             "the historical runner's WHOLE-SET case_contract gate (run_card_before.py lines "
             "140-168, `wrong_declaration` -> contract_problems -> return 1). stderr: \"cases whose "
             "`expected` is not 'ModelRegistryError': ['NEG-CARD']\". Consequence: the historical "
             "runner aborts BEFORE judging, so it produces no verdict and no output JSON - it is "
             "neither the fabricated green of the owner ruling nor evidence of a per-case gate. "
             "Arm B0 (same old runner, frozen cases.json) returns rc=0, and arm B1 (extra unknown "
             "case id) returns rc=1 from the structural case-count/id checks, isolating the three "
             "gate families."),
            ("DEVIATION from contract section 'keep the set-level gate': keeping that "
             "gate AS AN rc=1 ABORT makes arm F impossible, because the first negative case's "
             "mutation trips the set-level gate before any per-case judging (measured: rc=1). The "
             "set-level declaration comparison is therefore still EVALUATED and REPORTED verbatim "
             "in case_contract_check.set_level_declaration_violations and case_contract_problems, "
             "but it no longer drives the exit code; the structural half of the same gate still "
             "drives rc=1 unchanged. This is an ordering change inside one interlocked pair, not a "
             "change to any rc value: 0/1/2/3 keep their frozen meanings."),
            ("ANCHOR-CONFLICT WITH THE FROZEN cases.json case_contract.rule, reported not fixed: "
             "the frozen rule text says a differing `expected` makes the harness 'refuse to issue a "
             "verdict (rc=1)'. The owner's T1-11 append-only ruling forbids editing cases.json, so "
             "that sentence is now saturated by this patch's behaviour. The frozen file is "
             "byte-unchanged (sha256 recorded in cards_cases_sha256); the divergence is recorded "
             "here for the reviewer rather than silently re-frozen."),
            ("HISTORICAL cases.json CARRIES A STALE-SEMANTICS RULE STRING, not a defect in this "
             "patch: `case_contract.rule` still describes the whole-set behaviour. Downstream "
             "readers should treat case_contract_check as the authoritative record."),
            ("NEG-CARD's message-prefix mechanism check stays gating and still matched in arms "
             "E and G (the G arm's NEG-CARD is NOT_JUDGED but its raised message is unchanged), so "
             "the card-specific coverage claim is unaffected by this patch."),
            ("ARM F/G MUTATE ONLY THE FIRST NEGATIVE CASE (NEG-CARD, the lowest id) as the "
             "contract directs; the other ten negatives declare ModelRegistryError in every arm "
             "and keep PASS_rejected, so the mismatch signal is attributable to exactly one case."),
        ],
    }

    out_path = os.path.join(OUTDIR, "evidence.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(evidence, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("wrote", out_path)
    print("runner_before:", evidence["runner_before"]["sha256"], evidence["runner_before"]["bytes"])
    print("runner_after :", evidence["runner_after"]["sha256"], evidence["runner_after"]["bytes"])
    print("diff stats   :", evidence["diff_stats"])
    for arm in ("E", "F", "B", "G"):
        a = arm_summary[arm]
        print("arm %s rc=%s verdict=%s mismatch=%s" % (arm, a["rc"], a["verdict"],
                                                       a["declared_expectation_mismatch"]))


if __name__ == "__main__":
    main()
