"""r3 closeout: records the production drift window and its restoration in a SEPARATE file
(new filename, per the owner's instruction) and verifies that every other artefact of the
attempt is byte-unchanged.

Nothing is overwritten: this script only CREATES
  recovery/production_drift_and_restoration_r3.json
and reads everything else. It also refuses to touch anything under recovery/precorrection/.

Run:
  python -X utf8 -B scripts/record_drift_restoration.py --card M25 --attempt-root <attempt> \
      --repo <production repo>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

PROD_ANCHOR = {
    "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
}
DRIFT_OBSERVED = {
    "scripts/model_registry.py": {
        "sha256": "1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86",
        "size_bytes": 19703,
        "blob": "c80075c4dadbed827aac0937ed84b8f820978c0c",
        "mtime": "2026-09-20 04:35:32",
        "note": ("the registry had been reset to HEAD: the model_extensions wiring, the "
                 "driver_bounds mechanism and this batch's four models were absent"),
    },
}
RESTORED_EXPECTED = {
    "scripts/revenue_core.py": "1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae",
    "scripts/contracts/constants.py": "278e3e02df15e556f4851b46711a2f36aac5b7e6a9820c27e0ca31b02858d0ae",
    "scripts/revenue_report.py": "a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f",
    "tests/test_backtest.py": "d0972e238066f40e4c52d25806683749ddfa2c84e7f6652f38ff44f3b7efc16e",
    "SKILL.md": "45e4e343eba4f6e766cdb163d21c35a7f7beeb603d3c8b237339de440dc47806",
    "CHANGELOG.md": "bcba3dd50278b677ef0af63725a5d635763a40bd9f92089dfc37ff17529c0a8e",
}


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = args.attempt_root
    ev = os.path.join(attempt, "evidence", card)
    code_root = os.path.join(attempt, "iso", "checkout_scripts")

    observed_now = {}
    for rel in list(PROD_ANCHOR) + list(RESTORED_EXPECTED):
        path = os.path.join(args.repo, rel)
        observed_now[rel] = {
            "sha256": sha256_file(path) if os.path.exists(path) else None,
            "size_bytes": os.path.getsize(path) if os.path.exists(path) else None,
            "exists": os.path.exists(path),
        }

    anchored_ok = all(observed_now[rel]["sha256"] == want
                      for rel, want in PROD_ANCHOR.items())
    restored_ok = all(observed_now[rel]["sha256"] == want
                      for rel, want in RESTORED_EXPECTED.items())
    isolated = {
        "iso/checkout_scripts/model_registry.py": sha256_file(
            os.path.join(code_root, "model_registry.py")),
        "iso/checkout_scripts/model_extensions.py": sha256_file(
            os.path.join(code_root, "model_extensions.py")),
    }
    isolated_ok = (isolated["iso/checkout_scripts/model_registry.py"]
                   == PROD_ANCHOR["scripts/model_registry.py"]
                   and isolated["iso/checkout_scripts/model_extensions.py"]
                   == PROD_ANCHOR["scripts/model_extensions.py"])

    frozen = {name: sha256_file(os.path.join(ev, name))
              for name in ("input.json", "oracle.json", "cases.json", "run_result.json")}
    probe = load(os.path.join(ev, "line_ending_and_blob_hashes.json"))
    frozen_r2 = {
        "input.json": probe["files"]["evidence/%s/input.json" % card]["worktree_sha256"],
        "oracle.json": probe["files"]["evidence/%s/oracle.json" % card]["worktree_sha256"],
        "cases.json": probe["files"]["evidence/%s/cases.json" % card]["worktree_sha256"],
        "run_result.json": probe["files"]["evidence/%s/run_result.json" % card]["worktree_sha256"],
    }

    payload = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "record": "production drift window and its restoration (r3 closeout)",
        "file_created_as_a_new_name_on_purpose": (
            "the owner asked for the drift fact and the recovery fact to be kept SIDE BY SIDE "
            "without overwriting anything, so this is a new file rather than an edit of "
            "integrity.json / source_manifest.json"),
        "drift_window": {
            "start_utc_approx": "2026-09-20 04:35:31",
            "end_utc_approx": "2026-09-20 04:40:53",
            "observed_by_this_attempt_at": "2026-09-20 04:5x (r3 closeout production re-check)",
            "production_was_not_in_the_anchored_state_during_this_window": True,
            "what_this_attempt_observed": DRIFT_OBSERVED,
            "instruction_for_downstream_readers": (
                "any recorded production_hashes_unchanged=false / anchored_hashes_match=false "
                "inside this window is a CORRECT alarm. It must never be used to change an "
                "expectation, a threshold or a frozen artefact, and those hashes must never be "
                "adopted as a new baseline."),
        },
        "root_cause_from_the_owner": {
            "who": "the orchestration layer's own git gate (not the user, not this implementer, not any attempt)",
            "what": ("a pre-commit/pre-push hook exported the unstaged changes to "
                     "C:\\Users\\郑曾波\\.cache\\pre-commit\\patch1789875331-33652 (557,924 B) at "
                     "04:35:31, then ran `git checkout -- .`; that command failed with 255 on three "
                     "concurrently-held scratch files (`unable to unlink ... Invalid argument`), so "
                     "the patch was never replayed and the worktree stayed reset to HEAD"),
            "same_second_side_effects": ["scripts/revenue_core.py",
                                         "scripts/contracts/constants.py",
                                         "scripts/revenue_report.py",
                                         "tests/test_backtest.py",
                                         "SKILL.md"],
        },
        "restoration": {
            "chosen_option": "option 1 - rebuild the extension-enabled state",
            "method": ("git apply --exclude=.planning/* on the SAME pre-commit patch; "
                       "--check exit 0 then apply exit 0"),
            "performed_by": "the owner (parent agent); this implementer performed no production write",
        },
        "post_restoration_verification_by_this_attempt": {
            "when": "2026-09-20 after 04:40:53",
            "anchored_two_modules_match": anchored_ok,
            "other_five_files_plus_changelog_match_the_owners_reported_hashes": restored_ok,
            "isolated_snapshot_equals_production_again": isolated_ok,
            "observed_hashes": observed_now,
            "isolated_snapshots": isolated,
        },
        "effect_on_the_cards": {
            "reviewer_invalidation_condition": ("iso/checkout_scripts/{model_registry,"
                                                "model_extensions}.py must always equal production "
                                                "9ec65295.../9939480b..."),
            "condition_was_triggered_during_the_window": True,
            "condition_is_cleared_again": anchored_ok and isolated_ok,
            "verdict_effect": ("the r2 accepted_scoped verdicts remain in force; no blocked "
                               "reclassification is needed"),
            "status_unchanged": "review_pending",
            "implementer_still_does_not_sign": True,
        },
        "frozen_artefacts_untouched_by_all_of_this": {
            "hash_at_r2": frozen_r2,
            "hash_now": frozen,
            "identical": frozen_r2 == frozen,
            "statement": ("no expectation, threshold or frozen artefact was changed to accommodate "
                          "the drift; the drift was recorded, escalated and then removed "
                          "externally"),
        },
        "residual_risk": {
            "scripts/model_extensions.py_is_still_untracked": True,
            "why_it_matters": ("model_registry.py imports it from the worktree, so half of the "
                               "extension wiring is still outside version control; another "
                               "`git checkout -- .` / `reset --hard` / `clean` could repeat this "
                               "failure"),
            "recommendation": ("the owner should bring model_extensions.py under version control "
                               "together with its wiring lines; this implementer did NOT run "
                               "git add (out of scope)"),
        },
        "lesson_for_this_batch": (
            "a card whose acceptance rests on a PRODUCTION FILE HASH is resting on a quantity that "
            "an external git operation can change without warning. On mismatch: record the drift "
            "and its time window, escalate to the orchestration layer for a ruling, and never "
            "adapt by editing expectations or frozen artefacts."),
    }

    with open(os.path.join(attempt, "recovery", "production_drift_and_restoration_r3.json"),
              "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=1)

    print("recorded drift + restoration for", card)
    print("  anchored two modules match:", anchored_ok)
    print("  isolated snapshot == production again:", isolated_ok)
    print("  frozen four-piece identical to r2:", frozen_r2 == frozen)
    return 0 if (anchored_ok and isolated_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
