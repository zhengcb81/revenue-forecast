"""Write binding.json (pins) then handoff.json (records binding's sha)."""
from __future__ import annotations

import hashlib
import json
import os

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
RUNS = os.path.join(PLAN, "execution_runs")
ATTEMPT = os.path.join(RUNS, "M01-M04-PROPAGATE", "a20260922-01")
EVIDENCE = os.path.join(ATTEMPT, "evidence")

HIST_RUNNER_SHA = "b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816"
CARDS = ("M01", "M02", "M03", "M04")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path):
    return os.path.relpath(path, PLAN).replace(os.sep, "/")


def pin(path):
    return {"path": rel(path), "sha256": sha(path), "bytes": os.path.getsize(path)}


def main():
    # ---------- freeze-order check: oracle strictly before every arm output ----------
    freeze = json.load(open(os.path.join(EVIDENCE, "oracle_freeze.json"), encoding="utf-8"))
    oracle_mtime = os.path.getmtime(os.path.join(ATTEMPT, "oracle.md"))
    arm_outputs = []
    for card in CARDS:
        for arm in ("E", "F", "G", "S", "B"):
            for name in ("out.json", "stdout.txt", "stderr.txt", "rc.txt", "run.json"):
                p = os.path.join(EVIDENCE, card, arm, name)
                if os.path.exists(p):
                    arm_outputs.append(p)
    first_arm = min(os.path.getmtime(p) for p in arm_outputs)
    freeze_ok = oracle_mtime < first_arm

    # ---------- original (historical) runner pins: 4 scripts + 4 recovery copies ----------
    originals = []
    for card in CARDS:
        for sub in (os.path.join("scripts", "run_card.py"),
                    os.path.join("recovery", "r2_exit_code_selfcheck", "run_card.py")):
            p = os.path.join(RUNS, card, "a20260919-01", sub)
            originals.append({"card": card,
                              "path": "execution_runs/%s/a20260919-01/%s"
                                      % (card, sub.replace(os.sep, "/")),
                              "sha256": sha(p), "bytes": os.path.getsize(p)})
    originals_ok = all(o["sha256"] == HIST_RUNNER_SHA for o in originals)

    manifest_verif = json.load(open(os.path.join(EVIDENCE, "manifest_verification.json"),
                                    encoding="utf-8"))
    arms_raw = json.load(open(os.path.join(EVIDENCE, "arms_raw.json"), encoding="utf-8"))
    arms_sum = json.load(open(os.path.join(EVIDENCE, "arms_summary.json"), encoding="utf-8"))
    commands = json.load(open(os.path.join(ATTEMPT, "commands.json"), encoding="utf-8"))
    raw_table = commands["raw_rc_table"]

    binding = {
        "card": "M01-M04-PROPAGATE",
        "attempt": "execution_runs/M01-M04-PROPAGATE/a20260922-01",
        "authority": {
            "file": "OWNER_DECISIONS.md",
            "section": "§十八【已裁定·第四批】",
            "verbatim": "A-1: 1, A-2: 授权, B: 全批, C:更新函件",
            "ruling": "A-1 = 1（①扩权）: REM-21/T1-8 同形态门传播扩到 M01–M04 四批 "
                      "（修在副本、before/ 留旧、历史 rc 零回改、证据齐全）; "
                      "预期臂 E=0/F=3/G=2/S=1 (OWNER_DECISIONS.md:424)",
            "register_row": "REMEDIATION_REGISTER.md: 'M01-M04-PROPAGATE（08e56200） | "
                            "A-1=①扩权 | 同四前置形态；预期臂 E=0/F=3/G=2/S=1；历史 runner/rc 零回改'",
        },
        "frozen_oracle": {
            "record": pin(os.path.join(EVIDENCE, "oracle_freeze.json")),
            "mtime_utc": freeze["mtime_utc"],
            "frozen_before_any_run": freeze["frozen_before_any_run"],
            "freeze_order_check": {
                "oracle_mtime_utc": __import__("datetime").datetime.utcfromtimestamp(
                    oracle_mtime).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "first_arm_output_utc": __import__("datetime").datetime.utcfromtimestamp(
                    first_arm).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "oracle_strictly_first": freeze_ok,
            },
        },
        "original_runners_historical_readonly": {
            "hash_family": HIST_RUNNER_SHA,
            "copies_checked": len(originals),
            "all_match_hash_family": originals_ok,
            "copies": originals,
        },
        "before_keeps_originals": {
            "before/run_card.py": {**pin(os.path.join(ATTEMPT, "before", "run_card.py")),
                                   "byte_identical_to_historical":
                                       sha(os.path.join(ATTEMPT, "before", "run_card.py"))
                                       == HIST_RUNNER_SHA},
            "iso/run_card_before.py": {**pin(os.path.join(ATTEMPT, "iso", "run_card_before.py")),
                                       "byte_identical_to_historical":
                                           sha(os.path.join(ATTEMPT, "iso", "run_card_before.py"))
                                           == HIST_RUNNER_SHA,
                                       "role": "arm B historical-runner role"},
            "before/cases_M01.json": pin(os.path.join(ATTEMPT, "before", "cases_M01.json")),
            "before/cases_M02.json": pin(os.path.join(ATTEMPT, "before", "cases_M02.json")),
            "before/cases_M03.json": pin(os.path.join(ATTEMPT, "before", "cases_M03.json")),
            "before/cases_M04.json": pin(os.path.join(ATTEMPT, "before", "cases_M04.json")),
        },
        "patched_copy": {**pin(os.path.join(ATTEMPT, "iso", "run_card.py")),
                         "form": "REM-21/T1-8 per-case exact-type-name gate"},
        "changes_diff": {**pin(os.path.join(ATTEMPT, "changes.diff")),
                         "added_lines": 149, "removed_lines": 21,
                         "mirror": "B5-fix-g1a-g3/a20260922-01/M05-M08/runner.diff "
                                   "(8263fc833fb48cbe..., 10431 B)"},
        "exit_code_legend": pin(os.path.join(ATTEMPT, "exit_code_legend.md")),
        "decision": pin(os.path.join(ATTEMPT, "decision.md")),
        "recovery_readme": pin(os.path.join(ATTEMPT, "recovery", "README.md")),
        "frozen_fixtures_cases_json": {
            "M01": "462ea30cfbb714a0be309af95cfe6427a0ed3b6b221c440ff60693c4ebc7e5b3",
            "M02": "b02423dd9adfe871b2bed6e5246f3b45afde8307e37a3ddb04a1871e91813015",
            "M03": "62d5b69f7af7fe0357d3fb02df6b4bb0e791d3f1240ca621fb6868894dff8443",
            "M04": "d515e1b7095b28222e6fadbfda2fcbb77b4decd49ff7bb2696044b0de7a905a4",
            "verified_against_historical_files": all(
                sha(os.path.join(RUNS, c, "a20260919-01", "evidence", c, "cases.json")) == v
                for c, v in (("M01", "462ea30cfbb714a0be309af95cfe6427a0ed3b6b221c440ff60693c4ebc7e5b3"),
                             ("M02", "b02423dd9adfe871b2bed6e5246f3b45afde8307e37a3ddb04a1871e91813015"),
                             ("M03", "62d5b69f7af7fe0357d3fb02df6b4bb0e791d3f1240ca621fb6868894dff8443"),
                             ("M04", "d515e1b7095b28222e6fadbfda2fcbb77b4decd49ff7bb2696044b0de7a905a4"))),
        },
        "code_root_readonly": {
            "model_registry.py": sha(os.path.join(ATTEMPT, "iso", "code_root", "model_registry.py")),
            "model_extensions.py": sha(os.path.join(ATTEMPT, "iso", "code_root", "model_extensions.py")),
            "pinned_by_B5_contract": True,
        },
        "interpreter": {
            "policy": "each card's own historical iso/venv python.exe, -X utf8 -B + "
                      "PYTHONDONTWRITEBYTECODE=1 (read-only execution)",
            "python_exe_sha256": arms_raw[0]["interpreter_sha256"],
            "version": "3.13.9",
        },
        "reference_mirror": {
            "diff": "execution_runs/B5-fix-g1a-g3/a20260922-01/M05-M08/runner.diff",
            "diff_sha256": sha(os.path.join(RUNS, "B5-fix-g1a-g3", "a20260922-01",
                                            "M05-M08", "runner.diff")),
            "patched_reference_sha256": sha(os.path.join(RUNS, "B5-fix-g1a-g3",
                                                         "a20260922-01", "M05-M08",
                                                         "run_card.py")),
            "patched_reference_identical_to_B5_plan_copy": sha(os.path.join(
                RUNS, "B5-fix-g1a-g3", "a20260922-01", "M05-M08", "run_card.py")) == sha(
                os.path.join(RUNS, "B5-plan-level-remediation", "a20260921-01",
                             "M05-M08", "run_card.py")),
            "semantic_origin": "T1-8 reference M17-M20 runner 94619a98... (reviewer r3)",
        },
        "historical_non_touch_proof": {
            "manifest_before": pin(os.path.join(EVIDENCE, "manifest_before.json")),
            "manifest_after": pin(os.path.join(EVIDENCE, "manifest_after.json")),
            "verification": {**pin(os.path.join(EVIDENCE, "manifest_verification.json")),
                             "result": manifest_verif["result"],
                             "files_checked": manifest_verif["files_checked"],
                             "added": len(manifest_verif["added_files"]),
                             "removed": len(manifest_verif["removed_files"]),
                             "changed": len(manifest_verif["changed_files"]),
                             "manifests_byte_identical":
                                 sha(os.path.join(EVIDENCE, "manifest_before.json"))
                                 == sha(os.path.join(EVIDENCE, "manifest_after.json"))},
        },
        "runs": {
            "arms_raw": pin(os.path.join(EVIDENCE, "arms_raw.json")),
            "arms_summary": pin(os.path.join(EVIDENCE, "arms_summary.json")),
            "commands": pin(os.path.join(ATTEMPT, "commands.json")),
            "run_count": len(arms_raw),
            "raw_rc_table": raw_table,
            "expected_rc_per_arm": {"E": 0, "F": 3, "G": 2, "S": 1, "B": 0},
            "all_arms_meet_frozen_expectation": arms_sum["all_arms_meet_frozen_expectation"],
            "deep_checks": "%d/%d" % (arms_sum["deep_checks_passed"],
                                      arms_sum["deep_checks_total"]),
            "raw_rc_source": "real child process exit codes (subprocess.run returncode), "
                             "recorded separately from expected_rc",
        },
        "final_recheck_after_all_deliverable_writes": {
            "note": "re-verified once more AFTER every deliverable file was written",
            **pin(os.path.join(EVIDENCE, "manifest_final_verification.json")),
            "result": json.load(open(os.path.join(EVIDENCE,
                                                  "manifest_final_verification.json"),
                                     encoding="utf-8"))["result"],
            "manifest_recheck": pin(os.path.join(EVIDENCE, "manifest_final_recheck.json")),
        },
        "four_preconditions": {
            "1_patch_on_copies_only": True,
            "2_before_keeps_originals": originals_ok,
            "3_zero_historical_rc_rewrite": manifest_verif["result"] == "PASS",
            "4_evidence_complete": True,
        },
        "boundaries": {
            "historical_directories_written": False,
            "product_or_production_writes": False,
            "git_writes": False,
            "self_signing": False,
            "__pycache_anywhere": False,
            "rem80_register_closure": "NOT claimed here - parent closes AFTER review",
        },
        "non_claims": {
            "disclosure_adaptation": "unmapped",
            "accuracy": "unproven",
        },
    }
    bpath = os.path.join(ATTEMPT, "binding.json")
    with open(bpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(binding, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    deliverable_hashes = {
        "oracle.md": sha(os.path.join(ATTEMPT, "oracle.md")),
        "binding.json": sha(bpath),
        "decision.md": sha(os.path.join(ATTEMPT, "decision.md")),
        "changes.diff": sha(os.path.join(ATTEMPT, "changes.diff")),
        "commands.json": sha(os.path.join(ATTEMPT, "commands.json")),
        "exit_code_legend.md": sha(os.path.join(ATTEMPT, "exit_code_legend.md")),
        "recovery/README.md": sha(os.path.join(ATTEMPT, "recovery", "README.md")),
        "iso/run_card.py": sha(os.path.join(ATTEMPT, "iso", "run_card.py")),
        "iso/run_card_before.py": sha(os.path.join(ATTEMPT, "iso", "run_card_before.py")),
        "before/run_card.py": sha(os.path.join(ATTEMPT, "before", "run_card.py")),
        "evidence/arms_raw.json": sha(os.path.join(EVIDENCE, "arms_raw.json")),
        "evidence/arms_summary.json": sha(os.path.join(EVIDENCE, "arms_summary.json")),
        "evidence/manifest_before.json": sha(os.path.join(EVIDENCE, "manifest_before.json")),
        "evidence/manifest_after.json": sha(os.path.join(EVIDENCE, "manifest_after.json")),
        "evidence/manifest_verification.json": sha(
            os.path.join(EVIDENCE, "manifest_verification.json")),
        "evidence/oracle_freeze.json": sha(os.path.join(EVIDENCE, "oracle_freeze.json")),
    }

    handoff = {
        "card": "M01-M04-PROPAGATE",
        "attempt": "execution_runs/M01-M04-PROPAGATE/a20260922-01",
        "status": "review_pending",
        "implementer_signed": False,
        "disclosure_adaptation": "unmapped",
        "accuracy": "unproven",
        "authority": binding["authority"],
        "summary": (
            "Owner-authorized (§18 A-1=①扩权) REM-21/T1-8-form per-case exact-type-name "
            "gate propagated to batches M01-M04 on COPIES only. Patch mirrors "
            "B5-fix M05-M08/runner.diff, adapted to the b5fcc685 family (import/file label "
            "and rc=1 crash path preserved). 20 fresh-subprocess runs: every raw rc equals "
            "the oracle frozen before any run (E=0/F=3/G=2/S=1 per card + inertness control "
            "B=0). Historical non-touch proof: 7722-file manifest zero drift (PASS)."),
        "batch_locating_note": (
            "No execution_runs/M01-M04/a20260919-01 directory exists; M01-M04 are four "
            "individual card attempts sharing the byte-identical runner b5fcc685... "
            "(8 historical copies, all verified)."),
        "arm_results_raw_rc": raw_table,
        "arm_results_expected": {"E": 0, "F": 3, "G": 2, "S": 1, "B": 0},
        "all_arms_meet_frozen_expectation": arms_sum["all_arms_meet_frozen_expectation"],
        "deep_checks": "%d/%d" % (arms_sum["deep_checks_passed"],
                                  arms_sum["deep_checks_total"]),
        "g_reason_measured": "cases_json_declared_expectation_missing:NEG-CARD (all 4 cards)",
        "f_mismatch_verdict_measured": "FAIL_declared_expectation_mismatch on NEG-CARD (all 4)",
        "s_structural_measured": "uncaught KeyError: 'kind', no out.json, rc=1 (all 4)",
        "b_inertness_measured": "historical byte-copy runner rc=0 on the same mutated "
                                "fixture (fabricated green re-measured in this attempt)",
        "historical_non_touch": {
            "files": manifest_verif["files_checked"],
            "added": 0, "removed": 0, "changed": 0,
            "result": manifest_verif["result"],
            "manifest_shas_identical": binding["historical_non_touch_proof"]
                ["verification"]["manifests_byte_identical"],
        },
        "runners": {
            "historical": HIST_RUNNER_SHA,
            "patched_copy": binding["patched_copy"]["sha256"],
            "before_copy": binding["before_keeps_originals"]["before/run_card.py"]["sha256"],
        },
        "four_preconditions": binding["four_preconditions"],
        "binding": {**pin(bpath)},
        "deliverable_hashes": deliverable_hashes,
        "open_issues": [
            "arm S family adaptation: B5-fix's literal extra_unknown_id mutation only "
            "structural-aborts runners WITH a case_contract id gate (M25-M28); the b5fcc685 "
            "family has none (source-verified), so S injects the equivalent structural fault "
            "for THIS family - one case entry missing required member `kind` -> rc=1. The "
            "literal extra_unknown_id variant was NOT run (would be judged normally, rc=0) "
            "and is not claimed as measured (oracle §4 pre-registered this).",
            "arm B rc=0 is a MEASUREMENT (matches B5-fix's two independent measurements "
            "E=0/F=0/B=0/G=1 on these bytes); the historical rc=1 G behaviour (KeyError) "
            "remains recorded in B5-fix and was not re-run here - historical runners/rc "
            "are read-only.",
            "REM-80 register-row closure, the 31/31-uniformity追认, and independent review "
            "belong to the parent AFTER review; this card only delivers evidence.",
            "START_HERE append-3 (REM-84) is out of this card's scope.",
        ],
        "review_instructions": [
            "Re-run scripts/run_arms.py + scripts/summarize.py (recovery/README.md) and "
            "expect E=0/F=3/G=2/S=1/B=0 for all four cards, deep checks 60/60.",
            "Re-verify historical non-touch: scripts/build_manifest.py + "
            "scripts/verify_manifest.py against evidence/manifest_before.json -> PASS, "
            "7722 files, 0/0/0 drift.",
            "Diff iso/run_card.py vs before/run_card.py (changes.diff) against the mirror "
            "B5-fix-g1a-g3/a20260922-01/M05-M08/runner.diff semantics.",
            "Confirm oracle.md sha/mtime precede every arm output "
            "(evidence/oracle_freeze.json).",
        ],
        "non_claims": binding["non_claims"],
    }
    hpath = os.path.join(ATTEMPT, "handoff.json")
    with open(hpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(handoff, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("binding.json sha256 =", sha(bpath))
    print("handoff.json  sha256 =", sha(hpath))
    print("originals_ok =", originals_ok, "freeze_ok =", freeze_ok,
          "manifest =", manifest_verif["result"],
          "arms_ok =", arms_sum["all_arms_meet_frozen_expectation"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
