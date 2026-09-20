"""Final hash inventory for one M-card attempt (standard library only).

Writes, at the very end of the attempt:
  after/rerun_sha256.json    sha256 + size + mtime of every attempt file except iso/venv,
                             plus the re-checked production/isolated hashes, the frozen
                             evidence hashes, the PLAN/reviews mtime and the whole-attempt
                             digest
  after/source_hashes.txt    the four product-source hashes in plain text
  after/git_status_<repo>.txt  post-run dirty state of the three production repos (the
                             pre-existing dirt is captured in before/ as well)

Everything under recovery/selfcheck/ is included on purpose: it is the scratch tree used by
the mutation self-check, so a reviewer can confirm nothing frozen was touched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time

SKIP_DIRS = (os.path.join("iso", "venv"),)


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    plan = os.path.dirname(os.path.dirname(os.path.dirname(attempt)))
    prod = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
    evidence = os.path.join(attempt, "evidence", card)
    skip = tuple(os.path.join(attempt, part) for part in SKIP_DIRS)
    self_rel = "after/rerun_sha256.json"

    prod_hashes = {"scripts/" + name: sha256_file(os.path.join(prod, "scripts", name))
                   for name in ("model_registry.py", "model_extensions.py")}
    iso_hashes = {"iso/checkout_scripts/" + name: sha256_file(
        os.path.join(attempt, "iso", "checkout_scripts", name))
        for name in ("model_registry.py", "model_extensions.py")}

    # F-04 (independent review 2026-09-20): write this script's OWN by-products BEFORE walking the
    # tree, so the inventory describes their final bytes instead of their pre-write state. The one
    # file that still cannot describe itself - this manifest - is excluded and declared below.
    lines = ["%s  %s" % (name, value) for name, value in sorted(prod_hashes.items())]
    lines += ["%s  %s" % (name, value) for name, value in sorted(iso_hashes.items())]
    with open(os.path.join(attempt, "after", "source_hashes.txt"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    for name in ("revenue-forecast", "company-wiki", "filing-fetch"):
        repo = os.path.join(os.environ["USERPROFILE"], "Projects", name)
        if not os.path.isdir(repo):
            continue
        target = os.path.join(attempt, "after", "git_status_%s.txt" % name)
        err = os.path.join(attempt, "after", "git_status_%s.stderr.txt" % name)
        with open(target, "wb") as out_handle, open(err, "wb") as err_handle:
            subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=out_handle,
                           stderr=err_handle)

    inventory = {}
    excluded = []
    for root, dirs, files in os.walk(attempt):
        if root.startswith(skip):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not os.path.join(root, d).startswith(skip)]
        # F-r3-04 (independent review 2026-09-20): byte-code caches are by-products that
        # appear and disappear with tool runs; listing them produced inventory entries for
        # files that no longer existed on disk.
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            path = os.path.join(root, name)
            rel = os.path.relpath(path, attempt).replace("\\", "/")
            if rel == self_rel:
                excluded.append(rel)
                continue
            entry = {"sha256": sha256_file(path), "bytes": os.path.getsize(path),
                     "mtime_unix": os.path.getmtime(path)}
            if rel.startswith("after/git_status_"):
                entry["concurrently_mutable"] = True
                entry["concurrently_mutable_reason"] = (
                    "the content is a snapshot of the three production repos' dirty state, which "
                    "other sessions can change; the FILE is stable once written, but regenerating "
                    "it later can legitimately produce different bytes")
            inventory[rel] = entry

    inventory_self_check = {
        "rule": "every file listed in `files` was re-opened and re-hashed from disk after the "
                "walk; a non-empty `mismatches` list means the inventory is not reproducible",
        "files_rehashed_from_disk": 0,
        "mismatches": [],
    }
    for rel, entry in inventory.items():
        path = os.path.join(attempt, *rel.split("/"))
        try:
            digest_now = sha256_file(path)
            size_now = os.path.getsize(path)
        except OSError as exc:
            inventory_self_check["mismatches"].append({"path": rel, "error": str(exc)})
            continue
        inventory_self_check["files_rehashed_from_disk"] += 1
        if digest_now != entry["sha256"] or size_now != entry["bytes"]:
            inventory_self_check["mismatches"].append(
                {"path": rel, "sha256_listed": entry["sha256"], "sha256_now": digest_now})

    frozen = {"evidence/%s/%s" % (card, name): sha256_file(os.path.join(evidence, name))
              for name in ("input.json", "cases.json", "oracle.json")}
    freeze_time = json.load(open(os.path.join(evidence, "oracle_selfcheck.json"),
                                 "r", encoding="utf-8"))["frozen_file_sha256_at_freeze_time"]
    reviews_dir = os.path.join(plan, "reviews")

    combined = hashlib.sha256()
    for rel in sorted(inventory):
        combined.update(rel.encode("utf-8"))
        combined.update(inventory[rel]["sha256"].encode("ascii"))

    doc = {
        "card_id": card,
        "attempt": attempt,
        "inventory_rule": "all files under the attempt except iso/venv/** (the virtual "
                          "environment is a tool, not evidence); recovery/selfcheck/** IS "
                          "included so the scratch state of the mutation proof is fixed; "
                          "__pycache__/** is EXCLUDED as of the r3 bookkeeping pass "
                          "(carried finding F-r3-04): a byte-code cache appears and "
                          "disappears with tool runs, so it can neither be pinned nor stay "
                          "listed once it is cleared",
        "inventory_rule_amend_r3": {
            "finding": "F-r3-04 (P3, inventory scope), independent review of 2026-09-20",
            "change": "__pycache__/** excluded from `files` and therefore from the combined "
                      "digest",
            "why_exclusion_and_not_a_concurrently_mutable_mark": "the finding allowed either "
                      "fix; exclusion is the stronger one because the previous revision "
                      "listed entries for files that no longer exist on disk",
            "frozen_artifacts_affected": False,
            "verification_logic_changed": False,
        },
        "ledger_refresh_r3": {
            "reason": "the r3 bookkeeping/transcription pass changed review.md, handoff.json, "
                      "evidence/<card>/qualification.json, evidence/<card>/oq_rulings.json, "
                      "evidence/<card>/cases_annotation_repack.json (M14/M15/M16) and added "
                      "evidence/<card>/verdict_transcription_r3.json, "
                      "recovery/production_drift_note.json and recovery/bookkeeping_r3/**; "
                      "the inventory is regenerated by RUNNING this script so the ledger does "
                      "not go stale",
            "historical_values_preserved": {
                "production_source_hashes_now": "NOT rewritten: production was restored to the "
                                                "anchored revision before this pass, so the "
                                                "regenerated value equals the "
                                                "2026-09-20T03:28-03:30Z value",
                "isolated_copy_still_equals_production": "NOT rewritten for the same reason",
            },
            "production_drift_pointer": 'C:\\Users\\郑曾波\\Projects\\revenue-forecast\\.planning\\2026-09-19-three-project-history-audit\\execution_runs\\_isolation_incidents\\20260920-precommit-stash-production-rollback\\INCIDENT.md',
            "production_source_hashes_during_the_drift_window_20260920_043531_044053": {
                "scripts/model_registry.py": "1f2639e1d44df6794a1478e7c3ed3400b5cf9d70cc994d3804e933bd6b020a86",
                "bytes": 19703,
                "anchor_sha256": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
                "anchor_bytes": 26446,
            },
            "declared_in": "recovery/production_drift_note.json",
        },
        "inventory_self_check": inventory_self_check,
        "files": inventory,
        "file_count": len(inventory),
        "combined_digest_over_sorted_relative_path_and_sha256": combined.hexdigest(),
        "combined_digest_scope": "exactly the `files` map listed above (sorted relative path + "
                                 "sha256); reproducible by re-walking the attempt with the same "
                                 "exclusions. It must NOT be used as a frozen checksum of the "
                                 "attempt, because after/git_status_*.txt are snapshots of a "
                                 "concurrently changing working tree.",
        "self_reference_note": "this manifest is written AFTER the inventory is computed, so it "
                               "cannot describe its own final bytes; it is excluded from `files` "
                               "and from the combined digest (see `excluded_from_inventory`). The "
                               "review finding F-04 of 2026-09-20 was that the previous revision "
                               "listed itself and its own git_status by-products with pre-write "
                               "hashes, which made the manifest - and the combined digest - "
                               "impossible to reproduce.",
        "excluded_from_inventory": excluded,
        "self_by_products_written_before_the_inventory": [
            "after/source_hashes.txt", "after/git_status_revenue-forecast.txt",
            "after/git_status_revenue-forecast.stderr.txt",
            "after/git_status_company-wiki.txt", "after/git_status_company-wiki.stderr.txt",
            "after/git_status_filing-fetch.txt", "after/git_status_filing-fetch.stderr.txt",
        ],
        "production_source_hashes_now": prod_hashes,
        "isolated_copy_hashes_now": iso_hashes,
        "isolated_copy_still_equals_production": (
            prod_hashes["scripts/model_registry.py"]
            == iso_hashes["iso/checkout_scripts/model_registry.py"]
            and prod_hashes["scripts/model_extensions.py"]
            == iso_hashes["iso/checkout_scripts/model_extensions.py"]),
        "frozen_evidence_hashes_now": frozen,
        "frozen_evidence_hashes_at_freeze_time": freeze_time,
        "frozen_evidence_unchanged": frozen == freeze_time,
        "plan_reviews_mtime_unix_now": os.path.getmtime(reviews_dir)
        if os.path.isdir(reviews_dir) else None,
        "plan_reviews_written_by_this_attempt": False,
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = os.path.join(attempt, "after", "rerun_sha256.json")
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=True, indent=1)
        handle.write("\n")

    print("inventory files: %d (iso/venv excluded, %s excluded as the manifest itself)"
          % (doc["file_count"], self_rel))
    print("combined digest: %s" % doc["combined_digest_over_sorted_relative_path_and_sha256"])
    print("isolated copy still equals production: %s"
          % doc["isolated_copy_still_equals_production"])
    print("frozen evidence unchanged: %s" % doc["frozen_evidence_unchanged"])
    print("wrote after/rerun_sha256.json, after/source_hashes.txt, after/git_status_*.txt")
    return 0 if (doc["isolated_copy_still_equals_production"] and doc["frozen_evidence_unchanged"]) else 11


if __name__ == "__main__":
    raise SystemExit(main())
