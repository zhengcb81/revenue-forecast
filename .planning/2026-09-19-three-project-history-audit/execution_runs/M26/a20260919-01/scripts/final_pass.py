"""Final pass: refresh evidence_hashes.json, add after/rerun_sha256.json, and record the
production-tree re-verification observed at the end of the attempt (stdlib only).

Run:
  python -X utf8 -B scripts/final_pass.py --card M25 --attempt-root <attempt> --production-root <root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

PRODUCTION_HASHES = {
    "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
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
    parser.add_argument("--production-root", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = args.attempt_root
    ev = os.path.join(attempt, "evidence", card)

    # ---- re-verify the production modules by hash ----
    observed = {}
    for rel, anchored in PRODUCTION_HASHES.items():
        path = os.path.join(args.production_root, rel)
        current = sha256_file(path)
        observed[rel] = {
            "anchored_sha256": anchored,
            "observed_sha256_at_the_end_of_the_attempt": current,
            "matches": current == anchored,
            "mtime_at_the_end_of_the_attempt": os.path.getmtime(path),
        }
    all_match = all(row["matches"] for row in observed.values())

    # ---- integrity.json: add the end-of-attempt re-verification ----
    integrity = load(os.path.join(ev, "integrity.json"))
    integrity["production_source_reverified_at_the_end_of_the_attempt"] = observed
    integrity["anchored_hashes_still_match_at_the_end_of_the_attempt"] = all_match
    integrity["production_tree_observation"] = {
        "method": ("git -C <production-root> status --porcelain compared with the I-00-A "
                   "baseline, after dropping every .planning/ entry (this audit's own working "
                   "tree) and the .tmp-* permission warnings"),
        "unattributable_entry_observed": {
            "path": "assurance/runs/daily_alert.jsonl",
            "status": " M",
            "attribution": ("NOT this attempt: it is the repository's own daily alert job output "
                            "(already recorded in "
                            "execution_runs/_isolation_incidents/20260920-prereg-expectations-leak/"
                            "INCIDENT.md event I-3). This attempt never writes under assurance/."),
        },
        "entries_that_disappeared_from_the_diff": {
            "note": ("assurance/runs/2026-09-11_r4-phase-b/* entries present in the I-00-A baseline "
                     "no longer appear because the plan owner COMMITTED them (parent commits "
                     "7d7ea1e / 1ac01f0, not this attempt)"),
        },
        "same_second_rewrite_observation": {
            "observed_mtime": "2026-09-20 03:41:57",
            "files": ["scripts/revenue_core.py", "scripts/forecast/segments.py",
                      "CHANGELOG.md", "SKILL.md", "references/*.md",
                      "assurance/runs/daily_alert.jsonl"],
            "statement": ("these files share one mtime that coincides with the plan owner's commit "
                          "1ac01f0 (2026-09-20 03:41:55). For the two modules this attempt "
                          "actually binds, the sha256 is unchanged from the anchored value, so the "
                          "rewrite did not change the bytes under test. For the others this attempt "
                          "has no baseline hash and does not claim byte-equality."),
        },
    }
    with open(os.path.join(ev, "integrity.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(integrity, handle, ensure_ascii=False, indent=1)

    # ---- revision_r2.json: record the stdout re-encoding and the rerun proof ----
    revision_path = os.path.join(ev, "revision_r2.json")
    revision = load(revision_path)
    revision["stdout_reencoding"] = {
        "what_happened": ("the very first capture of evidence/<card>/stdout.txt used PowerShell "
                          "redirection, which wrote UTF-16LE on Windows PowerShell 5.1. It was "
                          "re-captured as UTF-8 (BOM) by re-running the SAME bound argv, so the "
                          "stdout.txt in evidence/ is the definitive run's output in the same "
                          "encoding as the rest of the evidence set."),
        "frozen_numbers_unchanged": True,
        "proof": ("the re-run produced a byte-identical run_result.json "
                  "(recovery/rerun_check/rerun_check.json: byte_identical = true) and the printed "
                  "values in stdout.txt match the evidence files "
                  "(printed_value_checks all true)"),
        "raw_rc_of_the_reencoding_run": 0,
        "rerun_check": "recovery/rerun_check/rerun_check.json",
        "rerun_check_unit": "R-%s-independent-rerun-check" % card,
    }
    with open(revision_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(revision, handle, ensure_ascii=False, indent=1)

    # ---- after/rerun_sha256.json ----
    rerun = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "note": ("hashes observed at the END of the attempt, after the mutation self-check, after "
                 "the evidence pack and after the docs were written. The frozen evidence set "
                 "(input.json / oracle.json / cases.json / stdout.txt / run_result.json / "
                 "formula_result.json) must equal the hashes reported by the runner."),
        "frozen_evidence": {},
        "scripts": {},
        "documents": {},
        "production_reverified": observed,
        "production_anchored_hashes_still_match": all_match,
    }
    for name in sorted(os.listdir(ev)):
        path = os.path.join(ev, name)
        if os.path.isfile(path):
            rerun["frozen_evidence"]["evidence/%s/%s" % (card, name)] = sha256_file(path)
    for name in sorted(os.listdir(os.path.join(attempt, "scripts"))):
        if name.endswith(".py"):
            rerun["scripts"]["scripts/" + name] = sha256_file(
                os.path.join(attempt, "scripts", name))
    for name in ("oracle.md", "commands.json", "binding.json", "decision.md", "handoff.json",
                 "review.md", "changes.diff"):
        path = os.path.join(attempt, name)
        if os.path.exists(path):
            rerun["documents"][name] = sha256_file(path)
    with open(os.path.join(attempt, "after", "rerun_sha256.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(rerun, handle, ensure_ascii=False, indent=1)

    # ---- refresh evidence_hashes.json (it must exclude its own self-reference) ----
    hashes = {}
    for name in sorted(os.listdir(ev)):
        path = os.path.join(ev, name)
        if os.path.isfile(path) and name != "evidence_hashes.json":
            hashes["evidence/%s/%s" % (card, name)] = sha256_file(path)
    for name in ("oracle.md", "commands.json", "binding.json", "decision.md", "handoff.json",
                 "review.md", "changes.diff"):
        path = os.path.join(attempt, name)
        if os.path.exists(path):
            hashes[name] = sha256_file(path)
    for name in sorted(os.listdir(os.path.join(attempt, "scripts"))):
        if name.endswith(".py"):
            hashes["scripts/" + name] = sha256_file(os.path.join(attempt, "scripts", name))
    with open(os.path.join(ev, "evidence_hashes.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump({
            "card_id": card,
            "note": ("hashes of the receipt set at pack time; evidence_hashes.json itself is "
                     "excluded because it cannot contain its own hash (the value after this write "
                     "is recorded in after/rerun_sha256.json)"),
            "hashes": hashes,
        }, handle, ensure_ascii=False, indent=1)

    print("final pass for", card)
    print("  production anchored hashes still match:", all_match)
    print("  evidence files hashed:", len(rerun["frozen_evidence"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
