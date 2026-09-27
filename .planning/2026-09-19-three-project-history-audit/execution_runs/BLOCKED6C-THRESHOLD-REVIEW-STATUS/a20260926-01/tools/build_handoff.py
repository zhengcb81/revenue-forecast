"""BLOCKED6C handoff.json builder (oracle.md section 9 items 6-7).

Reads the phase reports this attempt produced, recomputes every sha256/byte
count from the files themselves, and writes handoff.json (UTF-8, no BOM, LF).
Process exit codes are constants here because rc lives in the shell log, not in
the JSON reports; each constant is labelled with the command that produced it.

Usage:
  python -X utf8 -B tools/build_handoff.py --out <handoff.json>
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANNING = os.path.abspath(os.path.join(RUN, os.pardir, os.pardir, os.pardir))

# ---- raw rc values observed in THIS session (documented with their command) ---
# python -X utf8 -B iso/tools/validate_hypotheses.py iso red/baseline_recheck_report.json red/baseline_recheck.log
RC_RED_BASELINE = 0
# python -X utf8 -B tools/run_cases.py --validator iso/tools/... --phase red-j1
RC_RED_J1 = 1
# python -X utf8 -B tools/run_cases.py --validator iso_patched/tools/... --phase green
RC_GREEN_CASES = 0
# python -X utf8 -B iso_patched/tools/validate_hypotheses.py iso_patched green/validation_report.json green/validation_run.log
RC_GREEN_MAIN = 0
# python -X utf8 -B tools/run_cases.py --validator mut/M*/... (one run per mutant)
RC_MUTANTS = {"M1": 1, "M2": 1, "M3": 1, "M4": 1, "M5": 1}
# python -X utf8 -B tools/l271_monitor.py --planning-root ... --out l271/l271_report.json
RC_L271 = 0
# python -X utf8 -B tools/make_mutants.py ; tools/make_diff.py
RC_MAKE_MUTANTS = 0
RC_MAKE_DIFF = 0

SEALED = [
    ("execution_runs/I11A-OPEN-ACCT/a20260924-01/ruling.md",
     "f3040df0081f6653c0d18ac334890bf0aff12175aeacbdc8e31485972bb329c2", 37355),
    ("execution_runs/I-11-A/a20260919-01/decision.md",
     "e9c96f02118514b8596620b3c0e235a797747fcd3bcf59d1a0fd20aa70166951", 29756),
    ("execution_runs/I-11-A/a20260919-01/oracle.md",
     "83dca500732f9365bbca865b4098729657d994af6ad40b282c26237c9906a890", 22418),
    ("execution_runs/I-11-A/a20260919-01/tools/validate_hypotheses.py",
     "cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac", 28549),
    ("execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json",
     "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28", 51697),
    ("execution_runs/I-11-A/a20260919-01/evidence/I-11-A/source_map.json",
     "3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf", 13863),
    ("execution_runs/I-11-A/a20260919-01/evidence/I-11-A/validation_report.json",
     "dc014e7e7a5699f5692d60d3e7cf76b782d1c64ef7668d5104e077290cb7c9b8", 5341),
    ("execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json",
     "b7314a22ebae453d4df6e6a93df62b993e0b179140feb67dafa0ec52b18b5878", 21808),
    ("execution_runs/I11A-HYP-APPROVE/a20260925-01/hypotheses_v2.json",
     "32c22208573a71d53033c4535e8d0cb598c61710e06174196033d996999d7859", 55213),
    ("execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json",
     "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff", 61231),
    ("execution_runs/HYPOTHESES-V4-MERGE/a20260926-01/hypotheses_v4.json",
     "ebf6fa4e2f708c397165127926475d5426afbdef0d93864a795a8640029c4654", 68565),
    ("execution_runs/OPEN6-TOLERANCE-TABLE/a20260925-01/tolerance_table.json",
     "1da977bfe05e23545363f123bb1f00e1b21e153849173e5ec9ed9bd8ec315573", 37631),
    ("execution_runs/OPEN6B-TOLERANCE-RULING/a20260926-01/tolerance_signed.json",
     "3ad403ba75cf545721b0ba4fa32345d5ecae00c1802e4ca39feb5f19d5f747e8", 18082),
]

DELIVERABLES = [
    "oracle.md",
    "changes.diff",
    "iso/tools/validate_hypotheses.py",
    "iso_patched/tools/validate_hypotheses.py",
    "tools/run_cases.py",
    "tools/make_mutants.py",
    "tools/l271_monitor.py",
    "tools/make_diff.py",
    "tools/build_handoff.py",
    "red/baseline_run.log",
    "red/baseline_validation_report.json",
    "red/baseline_recheck_report.json",
    "red/baseline_recheck.log",
    "red/ce_run.log",
    "red/ce22_ce25_report.json",
    "green/cases_run.log",
    "green/cases_report.json",
    "green/validation_report.json",
    "green/validation_run.log",
    "l271/l271_report.json",
    "l271/l271_run.log",
] + ["mut/M%d/%s" % (i, n) for i in range(1, 6)
     for n in ("validate_hypotheses.py", "cases_report.json", "cases_run.log")]


def sha_bytes(path):
    raw = open(path, "rb").read()
    return hashlib.sha256(raw).hexdigest(), len(raw)


def load(rel):
    with open(os.path.join(RUN, rel), encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    red_j1 = load("red/ce22_ce25_report.json")
    green = load("green/cases_report.json")
    green_main = load("green/validation_report.json")
    l271 = load("l271/l271_report.json")

    muts = {}
    for i in range(1, 6):
        name = "M%d" % i
        r = load("mut/%s/cases_report.json" % name)
        ce_acc = [c["case_id"] for c in r["card_counterexamples_ce22_ce25"]
                  if not c["rejected"]]
        orig_acc = [c["case_id"] for c in r["all_cases"]
                    if not c["rejected"]]
        muts[name] = {
            "rc": RC_MUTANTS[name],
            "mutation": {
                "M1": "DEFAULT_THRESHOLD_REVIEW_STATUS = \"reviewed\" (default flipped)",
                "M2": "whole <B6C-G3> not_reviewed fail-closed block deleted",
                "M3": "pre-existing E_THRESHOLD_BASIS_UNKNOWN closed-set check deleted",
                "M4": "B6C-G1 status closed-set judgement deleted (shared tuple "
                      "assignment kept so G2/G3 stay executable)",
                "M5": "B6C-G2 A-6.3 seal judgement deleted",
            }[name],
            "positive_case": r["positive_case"]["verdict"],
            "expected_flip_ce": {
                "M1": ["CE-24"], "M2": ["CE-24", "CE-25"], "M3": [],
                "M4": ["CE-22"], "M5": ["CE-23"],
            }[name],
            "expected_flip_own_suite": {
                "M1": ["OWN-24"], "M2": ["OWN-24", "OWN-25"], "M3": ["OWN-21"],
                "M4": ["OWN-22"], "M5": ["OWN-23"],
            }[name],
            "actually_flipped_ce": sorted(
                c for c in ce_acc if c.startswith("CE")),
            "actually_flipped_own_suite": sorted(
                c for c in orig_acc if c.startswith("OWN")),
            "expected_codes_present": sorted({
                c["expected_code"] for c in r["card_counterexamples_ce22_ce25"]
                if c["rejected"]}),
            "original_21_rejected": r["target_suite"]["original_21_rejected"],
            "new_b6c_rejected": r["target_suite"]["new_b6c_rejected"],
            "accepted_by_mistake": r["target_suite"]["accepted_by_mistake"],
            "matches_oracle_S5_expectation": (
                r["positive_case"]["verdict"] == "pass"
                and sorted(c for c in ce_acc if c.startswith("CE"))
                == sorted({"M1": ["CE-24"], "M2": ["CE-24", "CE-25"],
                           "M3": [], "M4": ["CE-22"], "M5": ["CE-23"]}[name])
                and sorted(c for c in orig_acc if c.startswith("OWN"))
                == sorted({"M1": ["OWN-24"], "M2": ["OWN-24", "OWN-25"],
                           "M3": ["OWN-21"], "M4": ["OWN-22"],
                           "M5": ["OWN-23"]}[name])),
            "report": "mut/%s/cases_report.json" % name,
            "log": "mut/%s/cases_run.log" % name,
        }

    # changes.diff stats
    diff_path = os.path.join(RUN, "changes.diff")
    diff_sha, diff_len = sha_bytes(diff_path)
    diff_lines = open(diff_path, encoding="utf-8").read().split("\n")
    body = diff_lines[diff_lines.index("---") + 1:]
    additions = sum(1 for l in body if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in body if l.startswith("-") and not l.startswith("---"))
    hunks = sum(1 for l in body if l.startswith("@@"))
    diff_files = [l[6:] if l.startswith("+++ b/") else l[4:]
                  for l in body if l.startswith("+++ ") or l.startswith("+++ b/")]

    deliverables = []
    for rel in DELIVERABLES:
        p = os.path.join(RUN, rel)
        sha, ln = sha_bytes(p)
        deliverables.append({"path": rel, "bytes": ln, "sha256": sha})

    sealed = []
    for rel, want, want_len in SEALED:
        p = os.path.join(PLANNING, rel)
        sha, ln = sha_bytes(p)
        sealed.append({"path": rel, "sha256": sha, "sha256_expected": want,
                       "bytes": ln, "bytes_expected": want_len,
                       "match": sha == want and ln == want_len})

    ts = green["target_suite"]
    steps = [
        {"step": 1, "name": "inventory of the on-disk progress",
         "status": "already_complete_before_continuation",
         "detail": "139 files / 2.38 MB present; oracle.md frozen (27,126 B), "
                   "iso/ pre-image copy, red/baseline_run.log + "
                   "red/baseline_validation_report.json, iso_patched patch "
                   "(G1-G3), tools/run_cases.py all already on disk",
         "rc": None, "artifacts": ["oracle.md", "iso/", "red/baseline_run.log",
                                   "red/baseline_validation_report.json",
                                   "iso_patched/tools/validate_hypotheses.py",
                                   "tools/run_cases.py"]},
        {"step": 2, "name": "freeze oracle.md before the first validator run",
         "status": "already_complete_before_continuation",
         "detail": "frozen 2026-09-26 by the previous worker; body NOT modified "
                   "by this continuation (sha256 still 27126 B / matches oracle "
                   "section 1 self-reference; no erratum needed because every "
                   "measured number matched the frozen hand calculation)",
         "rc": None, "artifacts": ["oracle.md"]},
        {"step": 3, "name": "RED baseline: positive case + frozen 21 examples "
                            "on the unpatched validator",
         "status": "already_complete_before_continuation (rc re-recorded here)",
         "detail": "previous worker left red/baseline_run.log + "
                   "red/baseline_validation_report.json (positive pass, "
                   "21/21 rejected, accepted_by_mistake=0) but did not record the "
                   "raw rc; this continuation re-ran the same command into new "
                   "files red/baseline_recheck_* (byte-identical report, "
                   "sha adcade2f...) and recorded rc=0. The previous worker's two "
                   "files were NOT modified.",
         "rc": RC_RED_BASELINE,
         "artifacts": ["red/baseline_run.log", "red/baseline_validation_report.json",
                       "red/baseline_recheck_report.json", "red/baseline_recheck.log"]},
        {"step": 4, "name": "RED J1: CE-22..CE-25 accepted by the unpatched validator",
         "status": "completed_by_this_continuation",
         "detail": "4/4 accepted (rejected=False, observed=-) => J1 red holds; "
                   "positive case still pass; original 21 still 21/21 rejected",
         "rc": RC_RED_J1,
         "artifacts": ["red/ce_run.log", "red/ce22_ce25_report.json"]},
        {"step": 5, "name": "GREEN: patched validator, positive + 25 examples",
         "status": "completed_by_this_continuation",
         "detail": "positive_case errors=0 verdict=pass; CE-22..CE-25 all rejected "
                   "with their expected codes; target suite 25/25 "
                   "(original_21_rejected=21, new_b6c_rejected=4, "
                   "accepted_by_mistake=0); DEC-14 re-count recorded in "
                   "green/validation_report.json counterexample_summary",
         "rc": RC_GREEN_CASES, "rc_validator_main": RC_GREEN_MAIN,
         "artifacts": ["green/cases_run.log", "green/cases_report.json",
                       "green/validation_report.json", "green/validation_run.log"]},
        {"step": 6, "name": "mutations M1..M5 (J2 discriminating power)",
         "status": "completed_by_this_continuation",
         "detail": "all five mutants red with exactly the pre-registered flip and "
                   "positive case still pass; M3's OWN-21 flip is the pre-registered "
                   "mutation red, NOT a J3 regression",
         "rc": RC_MAKE_MUTANTS, "rc_per_mutant": RC_MUTANTS,
         "artifacts": ["tools/make_mutants.py"] +
                      ["mut/M%d/" % i for i in range(1, 6)]},
        {"step": 7, "name": "L271 counterexample quantification (J4)",
         "status": "completed_by_this_continuation",
         "detail": "6 corpus files, sha256 all match oracle section 1; "
                   "record N=40 U=14 (35.0%); distinct N=8 U=4 (50.0%); "
                   "T1/T2/T3 all miss under U-PRIMARY => L271_trigger_fired=false; "
                   "under the U-LITERAL A-6.1 reading all three hit => "
                   "literal flag true",
         "rc": RC_L271, "artifacts": ["tools/l271_monitor.py",
                                      "l271/l271_report.json",
                                      "l271/l271_run.log"]},
        {"step": 8, "name": "changes.diff (per-file disclosure)",
         "status": "completed_by_this_continuation",
         "detail": "1 touched file, %d additions / %d deletions / %d hunks; "
                   "pre-image byte-identical to the sealed original"
                   % (additions, deletions, hunks),
         "rc": RC_MAKE_DIFF, "artifacts": ["changes.diff", "tools/make_diff.py"]},
        {"step": 9, "name": "handoff.json + integrity re-verification",
         "status": "completed_by_this_continuation",
         "detail": "handoff.json written; sealed inputs re-hashed; "
                   "git diff HEAD --name-only non-.planning = 0; all JSON "
                   "re-parsed by final_verification.json",
         "rc": 0, "artifacts": ["handoff.json", "final_verification.json"]},
    ]

    doc = {
        "schema": "blocked6c_handoff_v1",
        "card_id": "BLOCKED6C-THRESHOLD-REVIEW-STATUS",
        "attempt_id": "a20260926-01",
        "attempt_dir": ".planning/2026-09-19-three-project-history-audit/"
                       "execution_runs/BLOCKED6C-THRESHOLD-REVIEW-STATUS/a20260926-01",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
                                  .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "role": "I-11-A implementer-side / orchestration schema-side executor "
                "(dispatch 17c710a9, REMEDIATION_REGISTER.md section 143 B.4; "
                "requirement text = I11A-OPEN-ACCT ruling.md L298/L324)",
        "status": "review_pending",
        "implementer_signed": False,
        "signature": {
            "signed": False,
            "signer": None,
            "note": "no one signed for this card; independent review must exercise "
                    "the L17 scope judgement (oracle section 0.1) and the "
                    "U-PRIMARY vs U-LITERAL reading split (oracle section 3.3)",
        },
        "continuation": {
            "previous_worker_interrupted_by": "system event (dispatch states the "
                                              "progress on disk is valid)",
            "on_disk_before_this_continuation": [
                "oracle.md (frozen, 27126 B)",
                "iso/ full copy incl. tools/validate_hypotheses.py pre-image "
                "(28549 B, sha cb49360d...)",
                "iso_patched/tools/validate_hypotheses.py with B6C-SCHEMA/"
                "B6C-HELPERS/B6C-G1/G2/G3 (36030 B as listed by the dispatch)",
                "tools/run_cases.py (9041 B)",
                "red/baseline_run.log, red/baseline_validation_report.json "
                "(red phase complete)",
            ],
            "completed_by_this_continuation": [
                "B6C-G4 report block added to the patch (counts."
                "threshold_review_statuses, threshold_reviewability, "
                "threshold_review_status_schema with DEC-14 limitations) - the "
                "on-disk patch had G1..G3 only and would have missed oracle 3.2 G4",
                "red J1 (CE-22..CE-25 on the unpatched validator)",
                "green (positive + 25-case suite + DEC-14 report)",
                "mutations M1..M5",
                "L271 quantification",
                "changes.diff",
                "handoff.json + final verification",
            ],
            "previous_patch_sha_not_recoverable": (
                "the 36030 B intermediate version of iso_patched/tools/"
                "validate_hypotheses.py listed by the dispatch has no sha on disk "
                "and is not tracked by git, so its sha256 cannot be back-filled; "
                "the post-image of THIS attempt is recorded instead"),
        },
        "nine_steps": steps,
        "red_green_mutations": {
            "red_baseline": {
                "rc": RC_RED_BASELINE,
                "positive_verdict": "pass",
                "counterexample_summary": {"cases": 21, "rejected_as_expected": 21,
                                           "accepted_by_mistake": 0},
                "raw_rc_note": "rc re-recorded by this continuation; the report is "
                               "byte-identical to the previous worker's file",
                "artifacts": ["red/baseline_validation_report.json",
                              "red/baseline_recheck_report.json"],
            },
            "red_j1_ce22_ce25": {
                "rc": RC_RED_J1,
                "positive_verdict": red_j1["positive_case"]["verdict"],
                "ce_summary": red_j1["ce_summary"],
                "per_case": [{"case_id": c["case_id"],
                              "expected_code": c["expected_code"],
                              "observed_codes": c["observed_codes"],
                              "rejected": c["rejected"]}
                             for c in red_j1["card_counterexamples_ce22_ce25"]],
                "original_21_rejected": red_j1["target_suite"]["original_21_rejected"],
                "verdict": "J1 RED holds: 4/4 pre-registered counterexamples were "
                           "ACCEPTED by the unpatched validator",
            },
            "green": {
                "rc_cases_runner": RC_GREEN_CASES,
                "rc_validator_main": RC_GREEN_MAIN,
                "positive_verdict": green["positive_case"]["verdict"],
                "positive_errors": len(green["positive_case"]["errors"]),
                "ce_summary": green["ce_summary"],
                "target_suite": {
                    "cases": ts["cases"],
                    "original_21_total": ts["original_21_total"],
                    "original_21_rejected": ts["original_21_rejected"],
                    "original_21_accepted_ids": ts["original_21_accepted_ids"],
                    "new_b6c_total": ts["new_b6c_total"],
                    "new_b6c_rejected": ts["new_b6c_rejected"],
                    "rejected_as_expected": ts["rejected_as_expected"],
                    "accepted_by_mistake": ts["accepted_by_mistake"],
                },
                "dec14_report": {
                    "counterexample_summary":
                        green_main["counterexample_summary"],
                    "counts_threshold_review_statuses":
                        green_main["counts"]["threshold_review_statuses"],
                    "counts_threshold_review_status_defaulted":
                        green_main["counts"]["threshold_review_status_defaulted"],
                    "counts_threshold_reviewability_unusable":
                        green_main["counts"]["threshold_reviewability_unusable"],
                    "threshold_reviewability_summary":
                        green_main["threshold_reviewability"]["summary"],
                    "threshold_review_status_schema_limitations_present":
                        bool(green_main.get("threshold_review_status_schema", {})
                                        .get("limitations")),
                },
            },
            "mutations": muts,
            "mutation_verdict": "5/5 mutants red exactly as pre-registered in "
                                "oracle.md section 5; J2 holds",
        },
        "counterexample_regression_21": {
            "requirement": "DEC-14 (decision.md L345-369) / oracle J3: the "
                           "original 21 counterexamples must still be rejected on "
                           "the UNMUTATED patched validator",
            "original_21_rejected": ts["original_21_rejected"],
            "original_21_total": ts["original_21_total"],
            "accepted_ids": ts["original_21_accepted_ids"],
            "passed": ts["original_21_rejected"] == 21 and
                      not ts["original_21_accepted_ids"],
            "note": "M3 flips OWN-21 back to accepted; that is the pre-registered "
                    "mutation red and is explicitly NOT counted against J3 "
                    "(oracle section 5)",
        },
        "L271": {
            "quote": l271["l271_quote"],
            "trigger_fired": l271["L271_trigger_fired"],
            "trigger_fired_literal_A61_reading":
                l271["L271_trigger_fired_literal_A61_reading"],
            "quantification": {
                "corpus_files": len(l271["corpus"]),
                "corpus_sha256_all_match": l271["corpus_sha256_all_match"],
                "record_level": {
                    "N": l271["record_level"]["N"],
                    "U": l271["record_level"]["U_primary"],
                    "U_pct": l271["record_level"]["U_primary_pct"],
                    "usable": l271["record_level"]["usable_primary"],
                    "U_reasons": l271["record_level"]["U_primary_reasons"],
                    "A62_usable": l271["record_level"]["A62_usable_records"],
                    "U_newly": l271["record_level"]["U_newly"],
                    "U_newly_ids": l271["record_level"]["U_newly_ids"],
                    "U_literal": l271["record_level"]["U_literal"],
                    "U_literal_pct": l271["record_level"]["U_literal_pct"],
                    "U_newly_literal": l271["record_level"]["U_newly_literal"],
                },
                "distinct_level": {
                    "N": l271["distinct_underlying_level"]["N"],
                    "U": l271["distinct_underlying_level"]["U_primary"],
                    "U_pct": l271["distinct_underlying_level"]["U_primary_pct"],
                    "usable": l271["distinct_underlying_level"]["usable_primary"],
                    "U_reasons":
                        l271["distinct_underlying_level"]["U_primary_reasons"],
                    "A62_usable":
                        l271["distinct_underlying_level"]["A62_usable_records"],
                    "U_newly": l271["distinct_underlying_level"]["U_newly"],
                    "U_newly_ids":
                        l271["distinct_underlying_level"]["U_newly_ids"],
                    "U_literal": l271["distinct_underlying_level"]["U_literal"],
                    "U_newly_literal":
                        l271["distinct_underlying_level"]["U_newly_literal"],
                },
                "triggers": l271["triggers"],
            },
            "matches_oracle_frozen_hand_calculation": (
                l271["record_level"]["U_primary"] == 14 and
                l271["record_level"]["N"] == 40 and
                l271["record_level"]["U_newly"] == 2 and
                l271["record_level"]["A62_usable_records"] == 28 and
                l271["distinct_underlying_level"]["U_primary"] == 4 and
                l271["distinct_underlying_level"]["N"] == 8 and
                l271["distinct_underlying_level"]["U_newly"] == 1 and
                l271["distinct_underlying_level"]["A62_usable_records"] == 5 and
                l271["record_level"]["U_literal"] == 40 and
                l271["distinct_underlying_level"]["U_literal"] == 8),
            "report": "l271/l271_report.json",
            "log": "l271/l271_run.log",
        },
        "fail_closed": {
            "rule_1": {"condition": "any L271 trigger line hit under U-PRIMARY",
                       "fired": l271["L271_trigger_fired"],
                       "consequence_if_fired": "blocked"},
            "rule_2": {"condition": "any of the original 21 counterexamples "
                                    "regresses on the unmutated patched validator",
                       "fired": not (ts["original_21_rejected"] == 21 and
                                     not ts["original_21_accepted_ids"]),
                       "consequence_if_fired": "blocked"},
            "blocked": bool(l271["L271_trigger_fired"]) or not (
                ts["original_21_rejected"] == 21 and
                not ts["original_21_accepted_ids"]),
            "outcome": "neither fail-closed rule fired => this card is NOT blocked; "
                       "it is handed off for independent review "
                       "(status=review_pending)",
        },
        "changes_diff": {
            "path": "changes.diff",
            "bytes": diff_len,
            "sha256": diff_sha,
            "files": diff_files,
            "touched_files": len(diff_files),
            "additions": additions,
            "deletions": deletions,
            "hunks": hunks,
            "hypotheses_json_in_diff": any("hypotheses.json" in f
                                           for f in diff_files),
        },
        "deliverables": deliverables,
        "sealed_inputs_reverified": sealed,
        "sealed_inputs_all_match": all(s["match"] for s in sealed),
        "git": {
            "command": "git -c core.quotepath=false diff HEAD --name-only",
            "measured_local": "2026-09-26 09:40:26",
            "diff_HEAD_name_only_total": 3830,
            "git_diff_non_planning": 0,
            "untracked_command": "git -c core.quotepath=false ls-files --others "
                                 "--exclude-standard",
            "untracked_total": 9061,
            "untracked_non_planning_total": 48,
            "untracked_non_planning_created_by_this_attempt": 0,
            "untracked_non_planning_note": "all 48 are pre-existing leftovers "
                "(.tmp-r41-mutation/*, assurance/.../plan_inputs.json.bak, "
                "h2.log, h2.log.err) with mtimes 2026-09-20..2026-09-25, i.e. "
                "before this attempt; 101 untracked files belong to this card and "
                "all of them are under .planning/",
            "git_status_used": False,
            "git_write_used": False,
            "concurrency_note": "other cards are writing to .planning in the same "
                                "checkout, so the TOTAL counts drift between "
                                "measurements (3829 -> 3830 during this attempt); "
                                "the criterion is the NON-.planning count, which "
                                "stayed 0 in every measurement",
        },
        "releases_nothing": True,
        "does_not_claim_I11A_acceptance": True,
        "does_not_unblock_BLOCKED_6b": True,
        "does_not_unblock_OPEN_6": True,
        "does_not_release_any_parameter": True,
        "low_base_high_still_null": True,
        "threshold_basis_unchanged": True,
        "ruling_and_halves_unchanged": True,
        "produces_no_accept_for_I11B_or_I11C": True,
        "writes_no_plan_files": True,
        "writes_product_repos": False,
        "network_used": False,
        "unverified": [
            "No independent review has happened; implementer_signed=false and "
            "this card does not sign for anyone.",
            "The U-PRIMARY vs U-LITERAL reading split is NOT settled by this card: "
            "under the A-6.1 item-1 literal reading every one of the 40 records is "
            "unusable and all three trigger lines fire, which would make this card "
            "blocked. Oracle 3.3 pre-registers that the split is for the reviewer "
            "to rule on; both numbers are disclosed here.",
            "Mutations M4/M5 delete the judgement `if` block but keep the shared "
            "`_trs_*` tuple assignment; deleting the whole marker block would "
            "raise NameError instead of flipping the judgement, so that is not a "
            "faithful mutation. Disclosed in tools/make_mutants.py.",
            "The previous worker's red baseline rc was never recorded on disk; "
            "rc=0 comes from this continuation's re-run "
            "(red/baseline_recheck_report.json, byte-identical to the previous "
            "worker's report).",
            "L271 was quantified on the 6 corpus files frozen in oracle section 6 "
            "(sha256 all re-verified); the 21908-file sweep done while freezing "
            "was not repeated.",
            "T1 is a usable-threshold probe, not an actual I-11-C boot: whether "
            "the real I-11-C code starts was not tested (out of scope).",
            "The B6C-G4 report block was added by THIS continuation; the "
            "intermediate 36030 B patch state left by the previous worker has no "
            "recorded sha256 and is not recoverable.",
            "red/ logs and reports carry CRLF line endings (Windows console / "
            "validator writer); green/validation_report.json and "
            "green/validation_run.log were normalised to LF after writing, "
            "content unchanged. changes.diff and handoff.json are LF, UTF-8, "
            "no BOM.",
            "Only this card's own validator copy was exercised; no product-repo "
            "test suite, CI or lint was run (out of scope).",
        ],
        "did_not_do": [
            "did not unblock BLOCKED-6b (its still_blocked status is not mine)",
            "did not unblock OPEN-6",
            "did not release any parameter or threshold (low/base/high remain null)",
            "did not change threshold_basis or any threshold value",
            "did not touch the sealed I-11-A/a20260919-01 attempt or either "
            "half-territory ruling / tolerance ruling byte",
            "did not produce any ACCEPT for I-11-B or I-11-C",
            "did not sign on anyone's behalf",
            "did not write the five plan files",
            "did not use git write commands and did not run git status",
            "did not use the network",
            "did not modify any corpus file used by the L271 monitor",
        ],
        "next_owner": "independent reviewer (non-implementer) to rule on the L17 "
                      "scope judgement, the U-PRIMARY/U-LITERAL split, and the "
                      "3-signature acceptance path",
    }

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    raw = open(out, "rb").read()
    json.loads(raw.decode("utf-8"))  # immediate re-parse proof
    print("handoff.json bytes=%d sha256=%s" %
          (len(raw), hashlib.sha256(raw).hexdigest()))
    print("status=%s implementer_signed=%s L271_fired=%s blocked=%s" %
          (doc["status"], doc["implementer_signed"],
           doc["L271"]["trigger_fired"], doc["fail_closed"]["blocked"]))
    print("changes.diff files=%d +%d -%d hunks=%d" %
          (len(diff_files), additions, deletions, hunks))
    print("sealed_all_match=%s" % doc["sealed_inputs_all_match"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
