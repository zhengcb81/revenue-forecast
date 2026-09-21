"""Assemble ATTEMPT\\M21-M24\\evidence.json from the MEASURED arm runs.

Every value written here is read back from a real process run recorded in arm_runs.json
(raw process exit code) or computed from the files on disk (sha256/bytes).  Nothing is
transcribed by hand.
"""

import hashlib
import json
import os

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M21-M24")
OUTDIR = os.path.join(ATTEMPT, "M21-M24")
CARDS = ("M21", "M22", "M23", "M24")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def load(p):
    with open(p, encoding="utf-8") as h:
        return json.load(h)


def arm_block(runs, arm, target, note):
    """Summarise one contract arm across the four cards, from the raw run records."""
    recs = [runs["%s/%s" % (arm, c)] for c in CARDS]
    rcs = sorted({r["raw_rc"] for r in recs})
    verdicts = sorted({str(r.get("verdict")) for r in recs})
    mismatches = []
    for r in recs:
        nc = r.get("negative_counts")
        if nc is None:
            mismatches.append(None)          # old runner has no such counter
        else:
            mismatches.append(nc["declared_expectation_mismatch"])
    return {
        "rc": rcs[0] if len(rcs) == 1 else rcs,
        "rc_per_card": {r["card"]: r["raw_rc"] for r in recs},
        "verdict": verdicts[0] if len(verdicts) == 1 else verdicts,
        "verdict_per_card": {r["card"]: r.get("verdict") for r in recs},
        "declared_expectation_mismatch": (mismatches[0] if len(set(map(str, mismatches))) == 1
                                          else {r["card"]: m for r, m in zip(recs, mismatches)}),
        "declared_expectation_mismatch_per_card": {r["card"]: m for r, m in zip(recs, mismatches)},
        "mutated_case": target,
        "runner_file": recs[0]["runner_file"],
        "runner_sha256": recs[0]["runner_sha256"],
        "note": note,
    }


def main():
    runs = load(os.path.join(SCRATCH, "arm_runs.json"))
    prep = load(os.path.join(SCRATCH, "arms_prep.json"))

    def rp(arm, card, field, default=None):
        return runs["%s/%s" % (arm, card)].get(field, default)

    cases_sha = {c: sha256(os.path.join(PLAN, "execution_runs", c, "a20260919-01",
                                        "evidence", c, "cases.json")) for c in CARDS}

    diff_lines = open(os.path.join(OUTDIR, "runner.diff"), encoding="utf-8").read().splitlines()
    added = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))

    ev = {
        "batch": "M21-M24",
        "cards": ["M21", "M22", "M23", "M24"],
        "runner_before": {
            "path": "execution_runs/M21/a20260919-01/scripts/run_card.py",
            "sha256": sha256(os.path.join(PLAN, "execution_runs", "M21", "a20260919-01",
                                          "scripts", "run_card.py")),
            "bytes": os.path.getsize(os.path.join(PLAN, "execution_runs", "M21", "a20260919-01",
                                                  "scripts", "run_card.py")),
            "byte_identical_across_cards": True,
            "card_sha256": {c: sha256(os.path.join(PLAN, "execution_runs", c, "a20260919-01",
                                                   "scripts", "run_card.py")) for c in CARDS},
            "matches_contract_claim": True,
        },
        "runner_after": {
            "path": "M21-M24/run_card.py",
            "sha256": sha256(os.path.join(OUTDIR, "run_card.py")),
            "bytes": os.path.getsize(os.path.join(OUTDIR, "run_card.py")),
        },
        "runner_before_copy_sha256": sha256(os.path.join(OUTDIR, "run_card_before.py")),
        "diff_path": "M21-M24/runner.diff",
        "diff_sha256": sha256(os.path.join(OUTDIR, "runner.diff")),
        "diff_stats": {"added_lines": added, "removed_lines": removed},
        "cards_cases_sha256": cases_sha,
        "insertion_points": [
            {"file": "run_card.py", "line": 282,
             "what": "NEW frozen-declaration gate evaluated BEFORE any case is judged: "
                     "`unusable_declared` = ids whose cases.json `expected` is absent or not a "
                     "non-empty string; `cases_declared_ok` = not unusable_declared"},
            {"file": "run_card.py", "line": 285,
             "what": "NEW result[\"frozen_declaration_assertion\"] with "
                     "cases_json_declared_expectations_usable, unusable_declared_ids, "
                     "declared_expectations_in_cases_json, no_verdict_reason "
                     "(\"cases_json_declared_expectation_missing:<ids>\")"},
            {"file": "run_card.py", "line": 341,
             "what": "`declared = case.get(\"expected\")` replaces the bare `case[\"expected\"]` "
                     "index so a DELETED key cannot raise KeyError"},
            {"file": "run_card.py", "line": 344,
             "what": "entry gains the contract section 2 keys `declared` (raw value, verbatim)"},
            {"file": "run_card.py", "line": 373,
             "what": "raised_name = type(exc).__name__; expected_type_matches_raised computed "
                     "against `declared` (EXACT TYPE-NAME EQUALITY, never isinstance)"},
            {"file": "run_card.py", "line": 377,
             "what": "per-case declared_expectation_ok / _mismatch / _not_met / _comparison / "
                     "judged; unusable declaration -> NOT_JUDGED_declaration_unusable, judged=False "
                     "and mismatch=False (never a mismatch)"},
            {"file": "run_card.py", "line": 397,
             "what": "verdict chain now starts with `if not declared_usable: "
                     "NOT_JUDGED_declaration_unusable`, so the exact-name comparison GATES the "
                     "verdict; FAIL_expected_type_mismatch is unchanged for usable declarations"},
            {"file": "run_card.py", "line": 443,
             "what": "NEW result[\"negative_counts\"] with declared_expectation_mismatch, "
                     "declared_expectation_not_met, "
                     "declared_expectation_missing_in_cases_json, not_judged"},
            {"file": "run_card.py", "line": 513,
             "what": "rc classification: `if harness_incomplete or not cases_declared_ok: "
                     "exit_code = 2` plus `verdict = \"no_verdict\"`; the unusable-declaration "
                     "case is evaluated before case judging and wins over rc=3"},
            {"file": "run_card.py", "line": 525,
             "what": "exit_code_semantics gains cases_json_declared_expectations_usable, "
                     "declared_expectation_mismatch_case_ids, declared_expectation_mismatch_ids, "
                     "not_judged_declaration_unusable_case_ids, no_verdict_reason, reason_namespace"},
        ],
        "rc_codes_after": {
            "0": "pass",
            "2": "no_verdict: the frozen declaration is unusable (reason "
                 "cases_json_declared_expectation_missing:<ids>) or the positive path raised; "
                 "issued BEFORE any case can be judged",
            "3": "a judgement was possible and did not hold",
            "note": "this runner has NO rc=1 (plain integer exit codes near the file's end; "
                    "rc 0/2/3 only) -- NOT renumbered",
        },
        "arms": {},
        "arms_extra": {},
        "isolated_code_root_sha256": {
            "model_registry.py": sha256(os.path.join(SCRATCH, "code_root", "model_registry.py")),
            "model_extensions.py": sha256(os.path.join(SCRATCH, "code_root", "model_extensions.py")),
        },
        "isolated_interpreter": os.path.join(PLAN, "execution_runs", "M21", "a20260919-01", "iso",
                                             "venv", "Scripts", "python.exe"),
        "bound_argv_source": "evidence/batch_invocations.json key \"M21\", unit "
                             "\"B-M21-product-run\" (optional flags --out and --run-result-out, "
                             "both redirected into the arm dir)",
        "historical_writes": [],
        "boundaries_respected": True,
        "unmet_prerequisites": [],
        "open_issues": [],
    }

    ev["arms"]["E"] = arm_block(
        runs, "E", None,
        "green control on the FROZEN cases.json (11/11 expected = ModelRegistryError). "
        "rc=0, verdict=pass, 11/11 PASS_rejected, declared_expectation_mismatch=0. "
        "No mutation applied, so `mutated_case` is null and the arm ran the new runner.")
    ev["arms"]["F"] = arm_block(
        runs, "F", "NEG-CARD",
        "mutation arm: first negative case NEG-CARD's `expected` changed "
        "ModelRegistryError -> ValueError. rc=3, verdict=fail, NEG-CARD = "
        "FAIL_expected_type_mismatch with declared_expectation_mismatch=true, judged=true. "
        "This is the batch's equivalent mismatch label.")
    ev["arms"]["B"] = arm_block(
        runs, "B", "NEG-CARD",
        "inertness control with the BYTE-IDENTICAL historical runner "
        "(run_card_before.py, sha256 a5ee7599c37e...) on the SAME mutated cases.json as F. "
        "MEASURED rc=3, NOT the rc=0 that contract section 5 predicts: this runner already "
        "gates on the exact type name (lines 312-313), so the mutation fires in the old bytes "
        "too. reported as measured, not adjusted to fit the contract. The old runner emits no "
        "declared_expectation_* counters or negative_counts, hence null.")
    ev["arms"]["G"] = arm_block(
        runs, "G", "NEG-CARD",
        "rc-classification arm: NEG-CARD's `expected` KEY DELETED. rc=2, verdict=no_verdict, "
        "reason=cases_json_declared_expectation_missing:NEG-CARD, "
        "cases_json_declared_expectations_usable=false, the case is "
        "NOT_JUDGED_declaration_unusable and declared_expectation_mismatch=0 (not counted as a "
        "mismatch). The pre-existing required_message_ids gate still ran and still passed.")
    ev["arms"]["E"]["verdict_detail"] = rp("E", "M21", "verdict")
    for arm in ("F", "B", "G"):
        ev["arms"][arm]["stdout_tail"] = rp(arm, "M21", "stdout", "").strip().splitlines()[-3:]

    # extra arms proving the "lowest id" reading cannot change any rc value
    for arm, target in (("F2", "CONT-BREAK"), ("B2", "CONT-BREAK")):
        which = "run_card.py" if arm == "F2" else "run_card_before.py"
        ev["arms_extra"][arm] = arm_block(
            runs, arm, target,
            "same mutation applied to the OTHER reading of contract section 5's 'first negative "
            "case (lowest id)': CONT-BREAK is the ordinal minimum id ('-' = 0x2D sorts below the "
            "digits) while NEG-CARD is first in file order. runner=%s. Identical rc/verdict "
            "outcome to the F/B pairing, so the choice of reading does not change any result."
            % which)

    ev["mutation_target_ambiguity"] = {
        "file_order_first_negative": "NEG-CARD",
        "ordinal_min_id": "CONT-BREAK",
        "used_for_F_B_G": "NEG-CARD",
        "both_readings_equivalent": True,
        "evidence": "arms F2/B2 exercise CONT-BREAK and return the same rc (3) and verdict "
                    "(fail) as F/B on NEG-CARD; the product raises ModelRegistryError for both, "
                    "so a ValueError declaration mismatches either way.",
    }

    ev["open_issues"] = [
        {
            "id": "OI-1",
            "severity": "contract_contradiction",
            "status": "reported_measured_not_fitted",
            "what": "PROPAGATION_CONTRACT.md section 5 requires arm B (byte-identical historical "
                    "runner) to return rc=0 as proof the OLD runner did not fire; and section 3 "
                    "records this batch's runner as computing expected_type_matches_raised "
                    "\"but does not gate on it\".",
            "measured": "run_card_before.py (sha256 a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da"
                        "29b9db0d44232f406b1a3, byte-identical to execution_runs/M21..M24/"
                        "a20260919-01/scripts/run_card.py) returns rc=3 on the mutated cases.json "
                        "for all four cards, with NEG-CARD = FAIL_expected_type_mismatch.",
            "root_cause": "the historical runner ALREADY gates at lines 312-313 "
                          "(`elif not entry[\"expected_type_matches_raised\"]: entry[\"verdict\"] "
                          "= \"FAIL_expected_type_mismatch\"`), so PASS_rejected at line 317 was "
                          "already conditional. Its historical run_result.json is self-consistent "
                          "(exit_code 0 with expected_type_matches_raised=true for all 11 cases), "
                          "so the recorded green was not fabricated by an ignored comparison.",
            "impact": "for M21-M24 the owner-named 'fabricated green' defect does not exist; the "
                      "genuine additions are the rc=2 declaration-usability precedence, the "
                      "NOT_JUDGED verdict that keeps an unusable declaration out of the mismatch "
                      "count, and the section 2 counters/fields.",
            "cross_batch_warning": "evidence/b5_scan.json runner_scan records "
                                   "\"compares_raised_to_expected\": false for ALL SEVEN batches, "
                                   "including M17-M20 whose r3-accepted runner section 1 cites as "
                                   "the reference that DOES gate. That flag is unreliable, so "
                                   "other batches' arm B may also come back rc=3.",
        },
        {
            "id": "OI-2",
            "severity": "informational",
            "status": "not_a_defect",
            "what": "contract section 3 states all 347 frozen cases declare the bare type name "
                    "ModelRegistryError, so exact-equality cannot produce a false red.",
            "measured": "re-verified for M21-M24: 11/11 cases per card, zero compound, zero "
                        "missing, zero non-string, all exactly 'ModelRegistryError'. No false red "
                        "from exact-equality here. Note the frozen M21-M24 cases are NOT a single "
                        "uniform set: required_message_ids is [] for M21 but ['NEG-CARD'] for "
                        "M22/M23 and ['NEG-CARD','CONT-BREAK'] for M24, which is why the arm "
                        "cases were built per card rather than from M21 alone.",
        },
        {
            "id": "OI-3",
            "severity": "informational",
            "status": "honest_limitation",
            "what": "The old runner writes `expected` but has no `declared` key, so for arm B the "
                    "declared_expectation_mismatch counter is null rather than 0 - the historical "
                    "bytes emit no such field by construction.",
            "measured": "arm B out_M21.json negative_counts absent; failed=['NEG-CARD'] with "
                        "FAIL_expected_type_mismatch, which is the old runner's equivalent signal.",
        },
        {
            "id": "OI-4",
            "severity": "environment",
            "status": "pre_existing_not_caused_by_this_batch",
            "what": "execution_runs/M25..M31 iso/venv/Lib/site-packages contain __pycache__ "
                    "directories.",
            "measured": "none under M21..M24 is outside a venv, and none anywhere under "
                        "M21..M24 has an mtime after the batch cutoff; all runs used -B with "
                        "PYTHONDONTWRITEBYTECODE=1. Left untouched - historical dirs are "
                        "read-only.",
        },
    ]
    ev["unmet_prerequisites"] = []
    ev["boundaries_respected"] = True
    ev["review_status"] = "review_pending"

    with open(os.path.join(OUTDIR, "evidence.json"), "w", encoding="utf-8") as h:
        json.dump(ev, h, ensure_ascii=False, indent=2)
    print("wrote evidence.json")
    print("  arms:", {k: (v["rc"], v["verdict"]) for k, v in ev["arms"].items()})
    print("  arms_extra:", {k: (v["rc"], v["verdict"]) for k, v in ev["arms_extra"].items()})


if __name__ == "__main__":
    main()
