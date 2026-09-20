"""Write the batch generation manifest: judgement generation vs post-review-fix generation.

Judgement generation = 2026-09-20T03:44:34Z-03:44:43Z (independent reviewer r3), whose values were
copied read-only into evidence/<CARD>/generation_20260920T034434Z/ BEFORE any post-verdict write.
This manifest records the post-fix values, and measures which files changed between the two
generations (measurement artifacts must be byte-identical).

Usage:
  python -X utf8 -B write_generation_manifest.py --batch-root <batch> --runs-root <execution_runs>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os

CARDS = ("M17", "M18", "M19", "M20")
GEN_DIR = "generation_20260920T034434Z"
MEASUREMENT_MARKERS = ("/run_result.json", "/formula_result.json", "/negative_results.json",
                       "/mutation_selfcheck.json", "/extra_probes.json",
                       "/registry_enumeration.json", "/input.json", "/oracle.json", "/cases.json",
                       "/oracle_regen_proof.json", "/oracle_document_freeze.json")
BATCH_FILES = ("batch_handoff.md", "rc_namespace.json", "batch_json_validation.json",
               "transcription_proof_batch_r3.json", "final_validation_after_incident.txt")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-root", required=True)
    parser.add_argument("--runs-root", required=True)
    args = parser.parse_args()
    B = os.path.abspath(args.batch_root)
    R = os.path.abspath(args.runs_root)

    per_card = {}
    for card in CARDS:
        a = os.path.join(R, card, "a20260919-01")
        ev = os.path.join(a, "evidence", card)
        snap_dir = os.path.join(ev, GEN_DIR)
        snapshot = load(os.path.join(snap_dir, "SNAPSHOT.json"))
        old = {name: entry["sha256"] for name, entry in snapshot["copies"].items()}
        old_table = load(os.path.join(snap_dir, "final_deliverable_hashes.json"))
        new_table = load(os.path.join(a, "after", "final_deliverable_hashes.json"))
        measurement = sorted(k for k in old_table["files"]
                             if any(m in k for m in MEASUREMENT_MARKERS)
                             or k.endswith("/stdout.txt") and k.count("/") == 2)
        unchanged = [k for k in measurement
                     if k in new_table["files"]
                     and new_table["files"][k]["sha256"] == old_table["files"][k]["sha256"]]
        changed = [k for k in measurement if k not in unchanged]

        post = {
            "evidence_hashes.json": sha256(os.path.join(ev, "evidence_hashes.json")),
            "final_deliverable_hashes.json": sha256(
                os.path.join(a, "after", "final_deliverable_hashes.json")),
            "hash_table_verification.json": sha256(
                os.path.join(a, "after", "hash_table_verification.json")),
            "review.md": sha256(os.path.join(a, "review.md")),
            "handoff.json": sha256(os.path.join(a, "handoff.json")),
            "commands.json": sha256(os.path.join(a, "commands.json")),
            "process_history.json": sha256(os.path.join(a, "process_history.json")),
            "qualification.json": sha256(os.path.join(ev, "qualification.json")),
            "revision_r2.json": sha256(os.path.join(ev, "revision_r2.json")),
            "source_manifest.json": sha256(os.path.join(ev, "source_manifest.json")),
            "review_decision.json": sha256(os.path.join(ev, "review_decision.json")),
            "transcription_proof_r3.json": sha256(os.path.join(ev, "transcription_proof_r3.json")),
        }
        hand = load(os.path.join(a, "handoff.json"))
        qual = load(os.path.join(ev, "qualification.json"))
        rev = load(os.path.join(ev, "revision_r2.json"))
        proof = load(os.path.join(ev, "transcription_proof_r3.json"))
        per_card[card] = {
            "judgement_generation_values": old,
            "post_review_fix_values": post,
            "status": hand["status"],
            "formula_state": qual["formula"]["state"],
            "disclosure_adaptation": qual["disclosure_adaptation"]["state"],
            "accuracy": qual["accuracy"]["state"],
            "reviewer_verdict_block": {
                "landing_lines_in_review_md": [proof["landing_point"]["target_first_line"],
                                               proof["landing_point"]["target_last_line"]],
                "sha256": proof["copied_region_sha256"],
                "bytes": proof["source_block_bytes"],
                "byte_equal": proof["byte_equal"],
                "source_report_lines": "%s:%s" % (proof["source_range"]["first_line"],
                                                  proof["source_range"]["last_line"]),
            },
            "measurement_artifacts_unchanged": {
                "checked": len(measurement), "identical": len(unchanged), "changed": changed,
                "rule": ("the product measurement artifacts must be byte-identical across the two "
                         "generations; only records/status/transcription files may differ"),
            },
            "p3_b_demo_flag": {
                "applicable": rev["mechanism_proof"].get("applicable"),
                "prefix_hash_equals_base_hash": rev["mechanism_proof"].get(
                    "prefix_hash_equals_base_hash"),
            },
            "oracle_md": rev["oracle_md_sha256_now"],
            "r2_sections_in_oracle_md": rev["r2_sections_in_oracle_md"],
        }

    batch_files = {}
    for name in BATCH_FILES:
        path = os.path.join(B, name)
        if os.path.isfile(path):
            batch_files[name] = sha256(path)
    doc = {
        "batch_id": "M17-M20",
        "attempt_id": "a20260919-01",
        "judgement_generation": {
            "frozen_at_utc": "2026-09-20T03:44:34Z-03:44:43Z",
            "basis": ("four cards' last closing pass + V unit; stability evidenced by two identical "
                      "mtime samples at 03:45:31Z and 03:46:46Z"),
            "verdict": "accepted_scoped (formula qualification only), P1=0, P2=0",
            "snapshots": "evidence/<CARD>/%s/SNAPSHOT.json" % GEN_DIR,
        },
        "post_review_fix_generation": {
            "purpose": ("r3 leftovers P3-A..P3-D, the authorised accepted_scoped status, and the "
                        "byte-exact transcription of the r3 verdict"),
            "measurement_artifacts_unchanged": all(
                not c["measurement_artifacts_unchanged"]["changed"] for c in per_card.values()),
            "changed_after_the_judgement_generation": [
                "review.md (appended transcriptions + implementer notes)",
                "handoff.json / qualification.json (authorised accepted_scoped carrier)",
                "commands.json / process_history.json (regenerated records)",
                "evidence/<CARD>/{evidence_hashes,hash_table_selfcheck,source_manifest,oq_rulings,"
                "integrity,revision_r2}.json and after/{final_deliverable_hashes,"
                "hash_table_verification}.json (regenerated records)",
                "scripts/{run_closing,pack_card,transcribe_review_verdict,apply_review_decision,"
                "write_handoff,card_units}.py (P3-A/P3-B/P3-C documentation only for run_card.py: "
                "NOT touched)",
                "plus the unit capture records of the units re-executed in this generation",
            ],
        },
        "per_card": per_card,
        "batch_files": batch_files,
        "process_requirement": ("once completion is declared, the attempt directories must NOT be "
                                "written to again; any further write invalidates the r3 judgement and "
                                "requires re-review"),
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    out = os.path.join(B, "generation_manifest.json")
    tmp = out + ".tmp-atomic"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, out)
    print("generation manifest ->", out)
    print("measurement artifacts unchanged for all cards:",
          doc["post_review_fix_generation"]["measurement_artifacts_unchanged"])
    for card, c in per_card.items():
        m = c["measurement_artifacts_unchanged"]
        print("  %s status=%s formula=%s | measurement %d/%d identical | oracle.md %s r2=%s"
              % (card, c["status"], c["formula_state"], m["identical"], m["checked"],
                 c["oracle_md"][:16], c["r2_sections_in_oracle_md"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
