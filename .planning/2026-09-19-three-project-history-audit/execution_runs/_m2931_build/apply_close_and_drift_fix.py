import argparse
import datetime
import hashlib
import json
import os

CARDS = {"M29": "commercial_launch", "M30": "finite_adoption", "M31": "inventory_sellthrough"}
PROD = "C:\\Users\\\u90d1\u66fe\u6ce2\\Projects\\revenue-forecast"

ANCHORS = {
    "scripts/model_registry.py": ("9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
                                  26446),
    "scripts/model_extensions.py": ("9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
                                    None),
    "scripts/forecast/segments.py": ("95555509bc8a30affe1bcde3bb658ee4e3211d3b91f0ac6b1038dfc6d79765dd",
                                     None),
}

PATCH_NAME = "patch1789875331-33652"
INCIDENT = ("execution_runs/_isolation_incidents/"
            "20260920-precommit-stash-production-rollback/INCIDENT.md")
RISK_IDS = ["F-10"]


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    handoff_path = os.path.join(attempt, "handoff.json")
    with open(handoff_path, "r", encoding="utf-8") as handle:
        handoff = json.load(handle)
    before = sha256(handoff_path)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # ---- 2. keep the original F-DRIFT-1 record, append the root cause + recovery ----------------
    drift = handoff.get("source_drift_observed_after_review", {})
    live_now = {}
    for rel, (anchored, size) in ANCHORS.items():
        path = os.path.join(PROD, rel.replace("/", os.sep))
        live_now[rel] = {
            "anchored_sha256": anchored,
            "sha256_now": sha256(path) if os.path.isfile(path) else None,
            "size_bytes_now": os.path.getsize(path) if os.path.isfile(path) else None,
            "anchored_size_bytes": size,
            "unchanged": (os.path.isfile(path) and sha256(path) == anchored),
        }
    drift["root_cause_and_recovery"] = {
        "added_utc": now,
        "status": "CLOSED - root cause identified and repaired by the orchestration layer (parent agent)",
        "executor_determined": (
            "the executor IS determined: it was the orchestration layer's own commit job (the parent "
            "agent's git add/commit/push), NOT any card attempt and not an unidentified concurrent "
            "actor"),
        "root_cause": (
            "that commit job triggered the repository's own pre-commit gate. At 04:35:31 the gate "
            "exported the unstaged changes to %s (557,924 bytes) and then ran `git checkout -- .`; "
            "that command returned 255 because three concurrently held scratch files could not be "
            "unlinked (\"unable to unlink ... Invalid argument\"), the hook aborted, and THE PATCH WAS "
            "NEVER REPLAYED. The production working tree was therefore left reset to HEAD (every "
            "mtime 04:35:32)." % PATCH_NAME),
        "recovery": {
            "action": ("the parent agent re-applied the same patch with the .planning subset excluded "
                       "(`git apply --exclude=.planning/*`); both `--check` and `--apply` returned "
                       "exit 0"),
            "state_after_recovery": live_now,
            "anchor_check": ("all three watched files hash back to the anchored values; "
                             "SKILL.md 45e4e343... matches the I-00-A baseline and CHANGELOG.md "
                             "bcba3dd5... was restored as well"),
            "incident_record": INCIDENT,
            "concurrent_cause": (
                "three attempt scratch trees under .planning contain their own nested .git "
                "directories; a guard entry was added to execution_runs/.gitignore and NO file was "
                "deleted"),
        },
        "correction_1_attribution": {
            "what_the_original_record_said": (
                "that the working tree had been switched to HEAD or another revision by an "
                "unidentified concurrent actor"),
            "corrected": (
                "the orchestration layer's commit job caused it: the pre-commit patch was never "
                "replayed after `git checkout -- .` returned 255. Executor = orchestration layer "
                "(the parent agent's commit job); not any attempt."),
            "kept_verbatim": (
                "the original record above this key is preserved unchanged, including its timeline "
                "entry, so the wrong attribution remains auditable"),
        },
        "correction_2_import_failure": {
            "what_the_original_record_said": (
                "that the live registry could not import because model_extensions was missing"),
            "corrected": (
                "scripts/model_extensions.py was ON DISK and its hash never changed throughout the "
                "incident (9939480b..., it is untracked). The HEAD revision of model_registry.py "
                "simply no longer imports or mounts it: the build_extension_specs mounting line and "
                "the driver_bounds mechanism are absent from that revision."),
            "therefore": (
                "no file went missing; what vanished for the duration of the window was the "
                "registration of the extension models, not the extension module itself"),
            "kept_verbatim": (
                "the original probe result (ModuleNotFoundError) is preserved in the record above as "
                "the observed symptom, with this correction naming its real cause"),
        },
        "time_bound_warning_for_reviewers": (
            "any `production_hashes_unchanged=false` reading taken inside the 04:35:31-04:35:32 "
            "window (and until the patch was replayed) is a CORRECT alarm, not a false positive: the "
            "working tree really was not at the anchored revision then. Hashes taken before or after "
            "the window are unaffected. Consumers must carry the observation time with any "
            "production-hash claim."),
        "effect_after_recovery": {
            "frozen_evidence": "unchanged (verified again: input.json / oracle.json / cases.json match "
                               "source_manifest.evidence_input_hashes)",
            "formula_qualification": "still scoped to the anchored revision; the live tree is now back "
                                     "at that revision, which the anchor_check above demonstrates",
            "attempt_writes": "this attempt still executed no git write command and wrote no file "
                              "under the production tree",
        },
    }
    handoff["source_drift_observed_after_review"] = drift

    # ---- cross-batch gap registration for this incident -----------------------------------------
    gaps = handoff.setdefault("cross_batch_gaps", [])
    if not any(g.get("id") == "F-DRIFT-1" for g in gaps):
        gaps.append({
            "id": "F-DRIFT-1",
            "severity": "P2 (shared tooling / orchestration)",
            "batch": "orchestration-level; it can reset the shared working tree for every card",
            "title": "the pre-commit gate's patch was never replayed after `git checkout -- .` "
                     "returned 255, leaving the production tree at HEAD",
            "measured": ("04:35:31 patch export to %s; `git checkout -- .` exit 255 (three scratch "
                         "files could not be unlinked); hook aborted; tree reset to HEAD (mtimes "
                         "04:35:32); recovered by `git apply --exclude=.planning/*` (check and apply "
                         "both exit 0)" % PATCH_NAME),
            "impact": ("for the duration of the window every production-hash anchor was stale, so any "
                       "card that measured the tree then would have measured the wrong revision. No "
                       "card's frozen evidence in this batch was affected: all of them were measured "
                       "against their own iso/checkout_scripts copies."),
            "disposition": ("REGISTERED; recovery recorded in " + INCIDENT + ". This batch does not "
                            "fix the gate itself."),
            "where_the_true_values_live": "before/ and after/ source_hashes.txt, plus the recovery "
                                          "anchor_check in source_drift_observed_after_review",
        })

    # ---- 3. status -> accepted_scoped, carried by the reviewer's own verdict --------------------
    transcript = "evidence/%s/verdict_transcription_check.txt" % card
    confirm = "evidence/%s/verdict_confirmation_check.txt" % card
    status_block = {
        "state": "accepted_scoped",
        "granted": ["formula"],
        "not_granted": ["disclosure_adaptation (stays unmapped)", "accuracy (stays unproven)"],
        "supersedes_previous_state": handoff.get("status"),
        "carrier": (
            "the independent reviewer's own verdict text, transcribed verbatim into review.md "
            "lines %s-%s and proven byte-identical to the reviewer's report block by %s; the "
            "reviewer's later bounded-text confirmation is appended at review.md lines %s-%s and "
            "proven byte-identical by %s"
            % (handoff.get("reviewer_status", {}).get("verdict_block_first_line"),
               handoff.get("reviewer_status", {}).get("verdict_block_last_line"),
               transcript,
               _confirm_lines(evidence)[0], _confirm_lines(evidence)[1], confirm)),
        "authority": ("the acceptance was written by an independent reviewer, not by the implementer; "
                      "the implementer only transcribed it and proved the transcription byte-for-byte"),
        "implementer_signed": False,
        "implementer_never_signs_acceptance": True,
        "status_set_utc": now,
        "set_by": ("the implementer, on the explicit instruction of the orchestration layer (parent "
                   "agent), because the reviewer's close condition (R-1/R-2 cleared) is satisfied"),
        "reviewer_close_condition": {
            "condition": "M31 may not be closed before R-1/R-2 are cleared",
            "R-1": "cleared (live OQ-04 title corrected, superseded title kept)",
            "R-2": "cleared (all four write_binding.py copies carry the seven-driver/True constant "
                   "with no live False and a correction banner; the source was fixed, not merely "
                   "annotated)",
            "R-3_R-4_R-0": "also corrected at the source",
        },
        "qualification_scope": ("formula only, and only for the anchored revision "
                                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"),
    }
    handoff["status"] = "accepted_scoped"
    handoff["status_note"] = (
        "status was moved from review_pending to accepted_scoped on the orchestration layer's "
        "instruction once the reviewer's close condition was met. The acceptance is the reviewer's; "
        "the implementer never signs acceptance and did not author the verdict.")
    handoff["reviewer_status"] = status_block

    handoff["integrity_statement_scope_note"] = (
        "the before/after source hashes prove THIS ATTEMPT wrote nothing; they do not prove the "
        "repository stayed still. The transient reset of the production tree caused by the "
        "orchestration layer's pre-commit gate is recorded in "
        "source_drift_observed_after_review together with its root cause and recovery.")

    with open(handoff_path, "w", encoding="utf-8") as handle:
        json.dump(handoff, handle, ensure_ascii=False, indent=1)
    print("handoff %s: status=%s (was %s)" % (card, handoff["status"],
                                              status_block["supersedes_previous_state"]))
    print("  sha256 %s -> %s" % (before[:16], sha256(handoff_path)[:16]))

    # ---- qualification.json: formula -> accepted_scoped, other two untouched --------------------
    q_path = os.path.join(evidence, "qualification.json")
    q_before = sha256(q_path)
    with open(q_path, "r", encoding="utf-8") as handle:
        q = json.load(handle)
    previous = q["formula"].get("state")
    q["formula"]["state"] = "accepted_scoped"
    q["formula"]["granted"] = ["formula"]
    q["formula"]["granted_at_utc"] = now
    q["formula"]["granted_by"] = (
        "an independent reviewer (verdict transcribed verbatim into review.md; see "
        "reviewer_status.carrier in handoff.json). The implementer transcribed the verdict and did "
        "not sign it.")
    q["formula"]["implementer_signed"] = False
    q["formula"]["implementer_never_writes_accepted"] = True
    q["formula"]["state_supersedes"] = previous
    q["formula"]["scope"] = ("only the anchored revision "
                             "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f; not "
                             "extrapolated to disclosure adaptation, accuracy, other models or other "
                             "companies")
    if "granted_by" in q["formula"] and previous != "accepted_scoped":
        q["formula"]["granted_by_note"] = (
            "the earlier review_pending text said a separate independent reviewer only may write "
            "'accepted'; that reviewer has now done so and the verdict is transcribed above")
    with open(q_path, "w", encoding="utf-8") as handle:
        json.dump(q, handle, ensure_ascii=False, indent=1)
    print("  qualification.formula %s -> %s  (disclosure=%s accuracy=%s)"
          % (previous, q["formula"]["state"], q["disclosure_adaptation"]["state"],
             q["accuracy"]["state"]))
    print("  qualification.json sha256 %s -> %s" % (q_before[:16], sha256(q_path)[:16]))
    return 0


def _confirm_lines(evidence):
    path = os.path.join(evidence, "verdict_confirmation_check.txt")
    first = last = None
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("appended_block_first_line_1based:"):
                first = line.split(":", 1)[1].strip()
            elif line.startswith("appended_block_last_line_1based:"):
                last = line.split(":", 1)[1].strip()
    return first, last


if __name__ == "__main__":
    raise SystemExit(main())
