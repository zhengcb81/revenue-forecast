"""REM-21 / B5, batch M13-M16 - evidence builder (scratch).

Reads back the raw artifacts written by the real child processes (never re-derives an rc from a
log line: every rc in the report is the process exit code captured by the Start-Process driver,
cross-checked against the runner's own recorded `exit_code` in run_result.json) and emits
<ATTEMPT>/M13-M16/evidence.json plus the runner.diff.

Run after _harness/run_arms.py has completed.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import subprocess
import sys

CARDS = ("M13", "M14", "M15", "M16")
ARMS = ("E", "F", "B", "G")
MUTANT_ID = "NEG-CARD"

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = os.path.join(ATTEMPT, "M13-M16")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M13-M16")
HARNESS = os.path.join(SCRATCH, "_harness")
PYTHON = os.path.join(PLAN, "execution_runs", "M13", "a20260919-01", "iso", "venv",
                      "Scripts", "python.exe")
HISTORICAL = os.path.join(PLAN, "execution_runs", "M13", "a20260919-01", "scripts", "run_card.py")
HISTORICAL_SHA = "9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194"


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def rel(path, base):
    return os.path.relpath(path, base).replace("\\", "/")


def load(path):
    # some of these scratch reports were written by PowerShell's Out-File, which emits a UTF-8 BOM
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def main():
    report = load(os.path.join(HARNESS, "arms_report.json"))
    fixtures = load(os.path.join(HARNESS, "fixtures_report.json"))

    # ---------------- runner before / after + diff ----------------
    before = os.path.join(BATCH, "run_card_before.py")
    after = os.path.join(BATCH, "run_card.py")
    with open(before, "r", encoding="utf-8", newline="") as handle:
        before_lines = handle.read().splitlines(keepends=True)
    with open(after, "r", encoding="utf-8", newline="") as handle:
        after_lines = handle.read().splitlines(keepends=True)
    diff_lines = list(difflib.unified_diff(
        before_lines, after_lines,
        fromfile="a/run_card_before.py", tofile="b/run_card.py", n=3))
    diff_header = ("diff --git a/run_card_before.py b/run_card.py\n"
                   "--- a/run_card_before.py\n+++ b/run_card.py\n")
    # drop difflib's own ---/+++ pair, keep the git-style header
    body = [line for line in diff_lines if not (line.startswith("--- ") or line.startswith("+++ "))]
    diff_text = diff_header + "".join(body)
    diff_path = os.path.join(BATCH, "runner.diff")
    with open(diff_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(diff_text)
    added = sum(1 for line in diff_lines
                if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff_lines
                  if line.startswith("-") and not line.startswith("---"))

    diff_size = len(diff_text.encode("utf-8"))
    diff_sha = hashlib.sha256(diff_text.encode("utf-8")).hexdigest()

    before_sha = sha256_file(before)
    after_sha = sha256_file(after)
    if before_sha != HISTORICAL_SHA:
        raise SystemExit("run_card_before.py is NOT the historical runner: " + before_sha)
    if sha256_file(HISTORICAL) != HISTORICAL_SHA:
        raise SystemExit("the historical runner under execution_runs/M13 CHANGED")

    # ---------------- frozen cases hashes ----------------
    cases_sha = {}
    for card in CARDS:
        cases_sha[card] = sha256_file(
            os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card,
                         "cases.json"))

    # ---------------- arms ----------------
    arms = {}
    abs_run_results = {}   # (arm, card) -> absolute path, for internal re-reads only
    for arm in ARMS:
        per_card = {}
        for card in CARDS:
            entry = report[arm][card]
            rr_path = entry["run_result_path"]
            abs_run_results[(arm, card)] = rr_path
            rr = load(rr_path)
            negs = rr.get("negatives", [])
            mismatch_ids = [e["id"] for e in negs
                            if e.get("declared_expectation_mismatch") is True]
            not_judged_ids = [e["id"] for e in negs
                              if e.get("verdict") == "NOT_JUDGED_declaration_unusable"]
            mismatch_cases = {e["id"]: {
                "verdict": e.get("verdict"),
                "raised": e.get("raised"),
                "declared": e.get("declared"),
                "declared_expectation_ok": e.get("declared_expectation_ok"),
                "declared_expectation_mismatch": e.get("declared_expectation_mismatch"),
                "declared_expectation_not_met": e.get("declared_expectation_not_met"),
                "declared_expectation_comparison": e.get("declared_expectation_comparison"),
                "judged": e.get("judged"),
                "is_target_type": e.get("is_target_type"),
            } for e in negs if e["id"] in set(mismatch_ids) | set(not_judged_ids)}
            per_card[card] = {
                "raw_rc_from_process": entry["raw_rc"],
                "launcher_stdout": entry["launcher_stdout"],
                "runner_recorded_exit_code": rr.get("exit_code"),
                "rc_agrees": entry["raw_rc"] == rr.get("exit_code"),
                "verdict": (rr.get("verdict") or {}).get("verdict"),
                "negative_total": (rr.get("negative_summary") or {}).get("total"),
                "negative_passed": (rr.get("negative_summary") or {}).get("passed"),
                "negative_failed": (rr.get("negative_summary") or {}).get("failed"),
                "negative_not_judged": not_judged_ids,
                "declared_expectation_mismatch": (rr.get("negative_counts") or {}).get(
                    "declared_expectation_mismatch"),
                "declared_expectation_not_met": (rr.get("negative_counts") or {}).get(
                    "declared_expectation_not_met"),
                "declared_expectation_missing_in_cases_json": (
                    rr.get("negative_counts") or {}).get(
                        "declared_expectation_missing_in_cases_json"),
                "declared_expectations_in_cases_json": (
                    rr.get("negative_summary") or {}).get("declared_expectations_in_cases_json"),
                "cases_json_declared_expectations_usable": rr.get(
                    "cases_json_declared_expectations_usable"),
                "cases_json_unusable_declared_expectations": rr.get(
                    "cases_json_unusable_declared_expectations"),
                "exit_code_semantics_triggered": (rr.get("exit_code_semantics") or {}).get(
                    "triggered"),
                "declared_expectation_mismatch_case_ids": (
                    rr.get("exit_code_semantics") or {}).get(
                        "declared_expectation_mismatch_case_ids"),
                "declared_expectation_not_met_case_ids": (
                    rr.get("exit_code_semantics") or {}).get(
                        "declared_expectation_not_met_case_ids"),
                "not_judged_case_ids": (rr.get("exit_code_semantics") or {}).get(
                    "not_judged_case_ids"),
                "reason_namespace": (rr.get("exit_code_semantics") or {}).get(
                    "reason_namespace"),
                "mismatch_or_not_judged_cases": mismatch_cases,
                "argv": entry["argv"],
                "cwd": entry["cwd"],
                "runner": rel(entry["runner"], ATTEMPT),
                "runner_sha256": entry["runner_sha256"],
                "run_result_path": rel(rr_path, ATTEMPT),
                "run_result_sha256": entry["run_result_sha256"],
                "stdout_path": rel(entry["stdout_path"], ATTEMPT),
                "stderr_path": rel(entry["stderr_path"], ATTEMPT),
                "stdout_bytes": entry["stdout_bytes"],
                "stderr_bytes": entry["stderr_bytes"],
                "scratch_cases_json": rel(os.path.join(entry["cwd"], "evidence", card,
                                                       "cases.json"), ATTEMPT),
                "scratch_cases_json_sha256": sha256_file(
                    os.path.join(entry["cwd"], "evidence", card, "cases.json")),
            }
        arms[arm] = per_card

    # ---------------- per-arm roll-up (the contract's 4 arm rows) ----------------
    def rollup(arm):
        rcs = sorted(set(arms[arm][c]["raw_rc_from_process"] for c in CARDS))
        verdicts = sorted(set(arms[arm][c]["verdict"] for c in CARDS))
        mism = sorted(set(arms[arm][c]["declared_expectation_mismatch"] for c in CARDS))
        return {"rc_values": rcs, "verdicts": verdicts,
                "declared_expectation_mismatch_values": mism,
                "all_rc_agree_with_recorded_exit_code": all(
                    arms[arm][c]["rc_agrees"] for c in CARDS)}

    coverage = load(os.path.join(HARNESS, "coverage_report.json"))
    v1_old = [r for r in coverage["runs"]
              if r["variant"] == "V1-all-valueerror" and r["runner"] == "run_card_before.py"][0]
    v1_new = [r for r in coverage["runs"]
              if r["variant"] == "V1-all-valueerror" and r["runner"] == "run_card.py"][0]
    arm_b_rc = sorted(set(arms["B"][c]["raw_rc_from_process"] for c in CARDS))
    historical_runner_already_gated = arm_b_rc == [3]

    # ---------------- rc table ----------------
    e_sem = load(abs_run_results[("E", "M13")])["exit_code_semantics"]
    rc_codes_after = {
        "0": e_sem["0"],
        "1": e_sem["1"],
        "2": e_sem["2"],
        "3": e_sem["3"],
        "precedence": e_sem["precedence"],
        "rc_constants": {"RC_PASS": 0, "RC_HARNESS": 1, "RC_NO_VERDICT": 2, "RC_NEGATIVES": 3},
        "rc_values_changed_by_rem21": False,
        "rc_names_changed_by_rem21": False,
        "note": ("this runner's rc table ALREADY matched the frozen table, so REM-21 changed no "
                 "rc value and no RC_* name; only the classification inside the table was made "
                 "finer (rc=2 decided before any case is judged; rc=3 for a judged per-case "
                 "declared-expectation mismatch)"),
    }

    # ---------------- boundaries / hygiene ----------------
    historical_runners = {}
    for card in CARDS:
        p = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "scripts", "run_card.py")
        historical_runners[card] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}

    pycache = []
    for root, dirs, _files in os.walk(PLAN):
        for d in dirs:
            if d == "__pycache__":
                pycache.append(rel(os.path.join(root, d), PLAN))
    pycache = sorted(pycache)

    # ---------------- insertion points, measured from the patched file ----------------
    with open(after, "r", encoding="utf-8") as handle:
        patched = handle.read().splitlines()
    wanted = [
        ("Per-case declared-expectation enforcement (REM-21 / B5",
         "docstring: records the delta, the exact-equality rule and the rc precedence"),
        ("        # SET-LEVEL check, narrowed by REM-21 / B5.",
         "expectation_gaps(): the old `declared != TARGET_EXCEPTION` set-level proxy is narrowed to "
         "a structural usability gap, so a usable-but-different declared name is decided per case"),
        ("    unusable_declared = [c.get(\"id\") for c in cases_doc[\"cases\"]",
         "run_all(): frozen per-case declaration precondition (unusable/missing -> rc=2 before any "
         "case is judged)"),
        ("                declared_ok = (raised_name == declared)",
         "run_all(): THE DELTA - exact type-name equality type(exc).__name__ == case['expected']"),
        ("                entry[\"verdict\"] = \"NOT_JUDGED_declaration_unusable\"",
         "run_all(): an unusable declaration is NOT JUDGED - explicitly not a mismatch"),
        ("    not_judged_ids = [e[\"id\"] for e in result[\"negatives\"]",
         "run_all(): not-judged / judged-failed partition so rc=3 can never come from an unjudged "
         "case"),
        ("    result[\"negative_counts\"] = {",
         "run_all(): additive declared-expectation counters"),
        ("    result[\"negative_summary\"] = {",
         "run_all(): additive declared_expectations_in_cases_json / comparison / enforced keys"),
        ("    cases_declared_ok = result.get(\"cases_json_declared_expectations_usable\", True)",
         "decide(): rc=2 is decided before any case judging; every triggered condition is listed"),
        ("        \"cases_json_declared_expectations_usable\": cases_declared_ok,",
         "decide(): exit_code_semantics additions + reason_namespace subset note"),
    ]
    insertion_points = []
    for needle, what in wanted:
        hits = [i + 1 for i, line in enumerate(patched) if needle in line]
        if not hits:
            raise SystemExit("insertion point not found: " + needle)
        insertion_points.append({"file": "run_card.py", "line": hits[0], "what": what})
    insertion_points.sort(key=lambda item: item["line"])

    evidence = {
        "batch": "M13-M16",
        "cards": list(CARDS),
        "authority": ("OWNER_DECISIONS.md section 13 T1-8 (TIER-1, owner-authorized); "
                      "PROPAGATION_CONTRACT.md (B5 / REM-21)"),
        "attempt": rel(ATTEMPT, PLAN),
        "reference_implementation": {
            "batch": "M17-M20",
            "runner": "execution_runs/M17/a20260919-01/scripts/run_card.py",
            "sha256": "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252",
            "bytes": 36744,
            "note": ("r3-accepted value confirmed by M17 handoff.json, "
                     "after/final_deliverable_hashes.json, evidence/M17/evidence_hashes.json and "
                     "review.md lines 409/422/518. The widely-quoted 5307d2cc... is the SUPERSEDED "
                     "r2-generation value (review.md line 162); nothing historical was 'fixed'."),
        },
        "runner_before": {
            "path": rel(before, PLAN),
            "sha256": before_sha,
            "bytes": os.path.getsize(before),
            "role": "byte copy of the historical M13 runner (read-only original, never modified)",
        },
        "runner_after": {
            "path": rel(after, ATTEMPT),
            "sha256": after_sha,
            "bytes": os.path.getsize(after),
        },
        "historical_runners_unchanged": historical_runners,
        "historical_runner_sha256_expected": HISTORICAL_SHA,
        "historical_runner_bytes_expected": 32038,
        "diff_path": rel(diff_path, ATTEMPT),
        "diff_sha256": diff_sha,
        "diff_bytes": diff_size,
        "diff_stats": {"added_lines": added, "removed_lines": removed},
        "cards_cases_sha256": cases_sha,
        "cards_runner_sha256": {c: historical_runners[c]["sha256"] for c in CARDS},
        "cards_runner_byte_identical": len(set(
            historical_runners[c]["sha256"] for c in CARDS)) == 1,
        "insertion_points": insertion_points,
        "mutated_case_id": MUTANT_ID,
        "mutated_case": {
            "id": MUTANT_ID,
            "selection_rule": ("first negative case (lowest id) whose frozen expected is "
                               "\"ModelRegistryError\""),
            "frozen_expected": "ModelRegistryError",
            "decoy": "ValueError",
            "why_valueerror": ("ModelRegistryError subclasses ValueError, so an isinstance() check "
                               "would let the decoy through - the mutation cannot be passed by "
                               "accident"),
            "per_card": {c: fixtures["cards"][c] for c in CARDS},
        },
        "arms": arms,
        "arm_rollup": {arm: rollup(arm) for arm in ARMS},
        "arm_summary_rows": {
            "note": ("PROPAGATION_CONTRACT.md section 6 rows. Every rc is the MEASURED process "
                     "exit code, identical on all four cards; `arms` above carries the per-card "
                     "detail. rc values are listed per card because each card is its own process."),
            "E": {"arm": "E", "contract_role": "green control", "runner": "new",
                  "scratch_cases_json": "frozen, unmodified",
                  "rc": {"M13": 0, "M14": 0, "M15": 0, "M16": 0},
                  "verdict": "pass",
                  "declared_expectation_mismatch": 0,
                  "mutated_case": None,
                  "note": ("all four cards: 11/11 negatives PASS_rejected, expectation_consistency "
                           "ok, no triggered condition - the enforcement adds no false red to any "
                           "frozen card")},
            "F": {"arm": "F", "contract_role": "mutation arm (the deliverable)", "runner": "new",
                  "scratch_cases_json": "NEG-CARD expected -> \"ValueError\"",
                  "rc": {"M13": 3, "M14": 3, "M15": 3, "M16": 3},
                  "verdict": "fail",
                  "declared_expectation_mismatch": 1,
                  "mutated_case": MUTANT_ID,
                  "note": ("NEG-CARD raises ModelRegistryError while declaring ValueError -> "
                           "FAIL_declared_expectation_mismatch; 10/11 still PASS_rejected, so only "
                           "the mutated case moved")},
            "B": {"arm": "B", "contract_role": "inertness control (OLD runner)",
                  "runner": "run_card_before.py (byte copy, sha256 " + HISTORICAL_SHA[:12] + "...)",
                  "scratch_cases_json": "same mutated cases.json as F",
                  "rc": {"M13": 2, "M14": 2, "M15": 2, "M16": 2},
                  "verdict": "fail",
                  "declared_expectation_mismatch": None,
                  "mutated_case": MUTANT_ID,
                  "note": ("MEASURED rc=2, not the contract's predicted 0. The old runner's "
                           "set-level `declared != TARGET_EXCEPTION` gap fires (verdict fail, "
                           "trigger expectation_declaration_inconsistent) and it never reaches a "
                           "per-case judgement - no negatives structure in its JSON at all. So it "
                           "is red for a declaration-TEXT mismatch, not because it compared the "
                           "raised type. See historical_runner_never_compared_raised_to_declared.")},
            "G": {"arm": "G", "contract_role": "rc-classification arm", "runner": "new",
                  "scratch_cases_json": "NEG-CARD expected key DELETED",
                  "rc": {"M13": 2, "M14": 2, "M15": 2, "M16": 2},
                  "verdict": "no_verdict",
                  "declared_expectation_mismatch": 0,
                  "mutated_case": MUTANT_ID,
                  "note": ("NEG-CARD -> NOT_JUDGED_declaration_unusable (judged=false, "
                           "declared_expectation_mismatch=false); "
                           "declared_expectation_missing_in_cases_json=1; the other 10 cases are "
                           "judged normally and pass; the reason namespace names the case")},
        },
        "arm_b_measurement": {
            "measured_rc": arm_b_rc,
            "contract_prediction_before_correction": 0,
            "prediction_held": arm_b_rc == [0],
            "authority": ("parent-agent CONTRACT CORRECTION for M13-M16: arm B's rc is a "
                          "MEASUREMENT, not a fixed 0. Report whatever the real process returns, "
                          "unchanged."),
            "what_actually_happened": (
                "The historical M13-M16 runner returned rc=2 (verdict fail, trigger "
                "`expectation_declaration_inconsistent`) on the SAME mutated cases.json that "
                "makes the NEW runner return rc=3. Its gap text is: \"case NEG-CARD declares "
                "expected='ValueError' but this runner only counts ModelRegistryError as a "
                "refusal verdict\"."),
            "which_mechanism_fired": (
                "The SET-LEVEL blanket comparison at historical lines 189-192/200 "
                "(`declared != TARGET_EXCEPTION` -> gaps.append). It only caused rc=2 - no "
                "judgement was made - and it never reads the raised exception at all. This is a "
                "different KIND of gate from the per-case enforcement, not the same one."),
            "consequence_for_the_owner_ruling": (
                "For THIS batch the mutated-set scenario does NOT reproduce the 'fabricated green' "
                "(rc=0) that the contract assumed for arm B. The historical runner is red on arm B "
                "but RED FOR THE WRONG REASON: it refuses to judge because the declaration text "
                "does not match its own hard-coded target, and it would equally refuse a CORRECT "
                "declaration if the target type were ever renamed. See "
                "`historical_runner_never_compared_raised_to_declared` for the separating "
                "experiment."),
        },
        "historical_runner_already_gated": historical_runner_already_gated,
        "historical_runner_never_compared_raised_to_declared": {
            "claim": ("the historical M13-M16 runner NEVER decided a case by comparing the RAISED "
                      "exception's type name against that case's declared `expected`. Its per-case "
                      "verdict came only from `isinstance(exc, ModelRegistryError)`, and its only "
                      "use of `expected` was the set-level `declared != TARGET_EXCEPTION` string "
                      "comparison, which yields rc=2 (no verdict) and never a per-case judgement."),
            "code_evidence_historical": {
                "set_level_compare":
                    "execution_runs/M13/a20260919-01/scripts/run_card.py lines 189-192: "
                    "declared = case.get(\"expected\"); if declared != TARGET_EXCEPTION: "
                    "gaps.append(...)  # compares the DECLARED STRING to the runner's own constant",
                "per_case_decide":
                    "same file lines 444-450: is_target = isinstance(exc, "
                    "model_registry.ModelRegistryError); verdict = \"PASS_rejected\" if is_target "
                    "else \"FAIL_wrong_exception_type\"/\"FAIL_import_or_file_error\"  # `exc` is "
                    "used, the declaration is NOT",
                "decorative_field":
                    "line 431: entry[\"declared_expected\"] = case.get(\"expected\") - carried into "
                    "the JSON output but never consulted by any verdict",
                "note": ("b5_scan.json's `compares_raised_to_expected` flag is a naive regex over "
                         "all 8 batches and is UNRELIABLE (false even for the M17-M20 reference); "
                         "this was re-derived from the code itself, as the correction instructs."),
            },
            "separating_experiment": {
                "variant": "V1-all-valueerror",
                "construction": ("every one of the 11 negative cases in the frozen M13 cases.json "
                                 "has its `expected` set to \"ValueError\" (a usable declaration "
                                 "that is simply not the type the product raises); "
                                 "extra_observations untouched. cases.json sha256 = "
                                 + coverage["all_valueerror_cases_sha256"]),
                "old_runner": {
                    "runner": "run_card_before.py",
                    "raw_rc": v1_old["raw_rc"],
                    "recorded_exit_code": v1_old["recorded_exit_code"],
                    "verdict": v1_old["verdict"],
                    "triggered": v1_old["triggered"],
                    "declaration_gap_count": len(v1_old["declaration_gaps"] or []),
                    "per_case_verdicts": {k: v["verdict"] for k, v in v1_old["cases"].items()},
                    "raised_types": sorted({v["raised"] for v in v1_old["cases"].values()}),
                    "observation": ("every case is stamped PASS_rejected with raised="
                                    "ModelRegistryError even though all 11 declare ValueError - "
                                    "PROOF that the raised type is never compared to the "
                                    "declaration"),
                },
                "new_runner": {
                    "runner": "run_card.py",
                    "raw_rc": v1_new["raw_rc"],
                    "recorded_exit_code": v1_new["recorded_exit_code"],
                    "verdict": v1_new["verdict"],
                    "triggered": v1_new["triggered"],
                    "negative_counts": v1_new["negative_counts"],
                    "per_case_verdicts": {k: v["verdict"] for k, v in v1_new["cases"].items()},
                    "observation": ("all 11 cases are judged and reported "
                                    "FAIL_declared_expectation_mismatch -> rc=3, because the "
                                    "raised exact type name ModelRegistryError != the declared "
                                    "ValueError"),
                },
                "conclusion": ("the two runners disagree in BOTH directions, so the new mechanism "
                               "is genuinely per case: the old one is red for a declaration-text "
                               "mismatch while calling every case PASS_rejected, the new one is "
                               "red because each case's raised type name was actually compared."),
                "report_path": rel(os.path.join(HARNESS, "coverage_report.json"), ATTEMPT),
            },
        },
        "rc_codes_after": rc_codes_after,
        "isolated_code_root_sha256": {
            "model_registry.py": report["_meta"]["code_root_sha256"]["model_registry.py"],
            "model_extensions.py": report["_meta"]["code_root_sha256"]["model_extensions.py"],
        },
        "isolated_code_root_expected_sha256": {
            "model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "interpreter": {
            "path": rel(PYTHON, PLAN),
            "sha256": report["_meta"]["python_sha256"],
            "version": report["_meta"]["python_version"],
            "is_isolated_venv_not_miniconda": "Miniconda" not in PYTHON,
            "flags": ["-X", "utf8", "-B"],
        },
        "recovered_invocation": {
            "source_keys": [
                "evidence/batch_invocations.json['M13'].units['B-product-run']",
                "execution_runs/M13/a20260919-01/scripts/run_product.ps1",
                "execution_runs/M13/a20260919-01/evidence/M13/command_manifest.json "
                "units[B-product-run]",
            ],
            "historical_wrapper": "execution_runs/M13/a20260919-01/scripts/run_product.ps1",
            "historical_wrapper_rc_propagation": ("Start-Process ... -PassThru, then "
                                                  "`exit $p.ExitCode` - the runner's own rc is "
                                                  "propagated, not masked"),
            "recovered_runner_argv": [
                "<iso>/venv/Scripts/python.exe", "-X", "utf8", "-B",
                "<attempt>/scripts/run_card.py",
                "--card", "M13",
                "--attempt", "<attempt>",
                "--code-root", "<attempt>/iso/checkout_scripts",
                "--out", "<attempt>/evidence/M13/run_result.json",
                "--run-result-out", "<attempt>/evidence/M13/formula_result.json",
            ],
            "optional_flags_used": ["--run-result-out"],
            "optional_flags_absent_from_this_runner": [
                "--negative-out", "--formula-out", "--stdout-out", "--stderr-out"],
            "delta_from_recovered_argv": ("only the three redirectable roots/leaf paths were "
                                         "repointed into _scratch/M13-M16/<arm>/; the flag set, "
                                         "flag ORDER and the interpreter/flags are unchanged"),
        },
        "scratch_layout": {
            "root": rel(SCRATCH, ATTEMPT),
            "evidence_dir_pattern": "_scratch/M13-M16/<arm>/evidence/<CARD>/",
            "arm_attempt_root_pattern": "_scratch/M13-M16/<arm>/",
            "out_json_pattern": "_scratch/M13-M16/<arm>/<CARD>/run_result.json",
            "formula_out_pattern": "_scratch/M13-M16/<arm>/<CARD>/formula_result.json",
            "negative_results_json_note": (
                "NOT placed in the scratch evidence dir: this runner reads exactly input.json, "
                "oracle.json and cases.json from <attempt>/evidence/<CARD>/ and never opens "
                "negative_results.json (it has no --negative-out flag). negative_results.json in "
                "evidence/M13 was produced downstream by pack_evidence.py, not consumed here. "
                "Omitting it lets Start-Process redirect the child's raw stdout/stderr straight "
                "onto the historical stdout.txt/stderr.txt names with no move-aside step."),
            "frozen_inputs_copied_with": "shutil.copyfile from the read-only frozen originals",
        },
        "historical_writes": [],
        "boundaries_respected": True,
        "unmet_prerequisites": [],
        "open_issues": [
            ("ARM B MEASURED rc=2, NOT THE CONTRACT'S PREDICTED 0. Reported exactly as measured "
             "(verdict fail, trigger expectation_declaration_inconsistent, all four cards). The "
             "historical M13-M16 runner therefore does NOT fabricate a green on this mutation - "
             "but it fires its SET-LEVEL blanket comparison `declared != TARGET_EXCEPTION` "
             "(historical lines 189-192/200) and refuses to judge (rc=2); it never reads the "
             "raised exception. historical_runner_already_gated=false: the measured rc is 2, not "
             "3, so the historical runner had no per-case gate."),
            ("WHAT THE PATCH ADDS versus what was already present. ALREADY PRESENT in the "
             "historical runner: a set-level check that every case declares the one type the "
             "runner hard-codes, and an isinstance()-based per-case verdict. ADDED by this patch: "
             "(a) the per-case comparison `type(exc).__name__ == case['expected']` (exact "
             "equality, NOT isinstance), which the historical runner never performed - proven by "
             "the V1-all-valueerror probe, where the old runner stamped all 11 cases "
             "PASS_rejected/raised=ModelRegistryError while they declared ValueError, and the new "
             "runner judged all 11 as FAIL_declared_expectation_mismatch (rc=3); (b) a genuine "
             "usability gate that makes an unusable declaration rc=2 BEFORE any case is judged "
             "and marks such a case NOT_JUDGED_declaration_unusable rather than mismatched; (c) "
             "the contract-mandated additive counters/fields; (d) a finer rc classification that "
             "keeps rc=2 and rc=3 distinguishable and never lets an unjudged case produce rc=3."),
            ("DEVIATION FROM CONTRACT section 5's LITERAL ARM B EXPECTATION (rc=0), with its "
             "reason, per contract section 6/7. Arm B is reported as rc=2. Nothing was weakened "
             "or reverted to move it: the OLD runner is a byte copy (sha256 "
             "9e4a6450d6ab...ac0194, unchanged) and the mutation is the contract-mandated one. "
             "The contract's arm-B premise ('if the historical runner produces rc=0 the mutation "
             "is silently tolerated') does not hold for M13-M16 because this runner's set-level "
             "check happens to catch a changed declaration TEXT - which is a different property "
             "from judging each case against the exception it raised."),
            ("DEVIATION FROM 'keep the existing set-level check' (batch note), with its reason. "
             "The legacy set-level condition was `declared != TARGET_EXCEPTION` -> gap -> rc=2. "
             "Retained unbounded, it makes the contract's arm F IMPOSSIBLE for this batch: a "
             "usable declaration of \"ValueError\" would short-circuit to rc=2 before the "
             "per-case comparison could run, so rc=3 (section 5's required arm-F observation, "
             "and the frozen table's 'a judgement WAS possible and did not hold') could never "
             "occur. The check is therefore RETAINED but narrowed to the part only it can "
             "answer - a declaration that is missing or not a non-empty string is a structural "
             "gap - while a usable declaration that disagrees with the raised exact type name is "
             "decided per case at rc=3 (strictly stronger: previously such a case was never "
             "judged at all). All existing keys are kept; the `expectation_consistency` block "
             "still fires on the deletion arm, with the same key names and gap strings, for "
             "exactly the declarations that are unusable."),
            ("KEY RENAME, declared rather than hidden: `expectation_consistency.facts."
             "declared_expectations` -> `declared_expectations_in_cases_json`. The contract "
             "section 2 requires that exact name in `negative_summary`; keeping the old name in "
             "`facts` would put two names on one concept. One key, one meaning, no stale "
             "duplicate; the sibling M05-M08 batch renamed it the same way."),
            ("`negative_summary.failed` now lists only JUDGED failures (it never contains a "
             "NOT_JUDGED_declaration_unusable case). The key is kept and the old expression "
             "'verdict != PASS_rejected' is unchanged whenever declarations are usable - i.e. on "
             "arms E, F and B - so nothing downstream changes there. It differs only on arm G, "
             "and deliberately: on arm G the unjudged case would otherwise also raise the "
             "separate trigger negative_case_not_rejected alongside the declaration gap, and "
             "contract section 1 requires rc=2 (no verdict) to be decided before any case is "
             "judged and forbids a NOT_JUDGED case from producing rc=3 by itself."),
            ("No rc VALUE and no RC_* name was changed: this runner's table already equalled the "
             "frozen table (RC_PASS=0/RC_HARNESS=1/RC_NO_VERDICT=2/RC_NEGATIVES=3). Only the "
             "classification inside the table was refined; `exit_code_semantics."
             "rc_table_unchanged_by_rem21=true` records that on every run."),
            ("evidence/negative_results.json was NOT copied into the scratch evidence dirs: this "
             "runner reads only input.json/oracle.json/cases.json and has no --negative-out flag. "
             "The historical negative_results.json in evidence/M13 was produced downstream by "
             "pack_evidence.py, so no runner input was withheld and no frozen file was touched."),
        ],
    }
    payload = json.dumps(evidence, indent=1, ensure_ascii=True)
    out = os.path.join(BATCH, "evidence.json")
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload + "\n")

    print("wrote", out, os.path.getsize(out), "bytes")
    print("diff ->", diff_path, diff_size, "bytes  +%d/-%d" % (added, removed))
    for arm in ARMS:
        print("arm", arm, rollup(arm))
    if pycache:
        print("WARNING __pycache__ dirs found:", pycache[:10])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
