"""Write the r3 hash ledgers: after/rerun_sha256.json, source_manifest.json,
evidence_hashes.json, and the new evidence/<card>/docfix_r3.json.

Write order is forced by the references (no circularity):
  1. docfix_r3.json          records the after-hashes of rerun_sha256/source_manifest
                             (computed in memory) and intentionally NOT of
                             evidence_hashes.json, which is written after it
  2. after/rerun_sha256.json all 32 entries refreshed from disk so that the ledger's
                             own "== disk" property (the F-M08-01 fix) still holds;
                             every value that changed r2->r3 is listed with its r2 value
  3. source_manifest.json    oracle_document.sha256_now -> r3 whole-file hash, with the
                             r2 value kept and the v1 frozen-body hash restated
  4. evidence_hashes.json    written last; revision r3; hashes refreshed and the two new
                             files added so the reviewer's own self-consistency check covers them

Usage: <iso venv python> -X utf8 -B f08_ledger.py [--apply] > f08_ledger.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
REVIEW = "C:/Users/\u90d1\u66fe\u6ce2/AppData/Local/Temp/m05m08-review-20260920-025942"
CARDS = ("M05", "M06", "M07", "M08")
APPLY = "--apply" in sys.argv

dedupe = json.load(open(os.path.join(HERE, "f06_dedupe.json"), encoding="utf-8"))
verify = json.load(open(os.path.join(HERE, "f06_verify.json"), encoding="utf-8"))
oqs = json.load(open(os.path.join(HERE, "f07_fix_oq.json"), encoding="utf-8"))
named = json.load(open(os.path.join(HERE, "f08_named_files.json"), encoding="utf-8"))
docs = json.load(open(os.path.join(HERE, "f089_patch_docs.json"), encoding="utf-8"))
repack = json.load(open(os.path.join(HERE, "f08_repack_diff.json"), encoding="utf-8"))
fold = json.load(open(os.path.join(HERE, "f13_fold_wording.json"), encoding="utf-8"))


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def dump(obj) -> bytes:
    return (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    print("== r3 hash ledgers ==")
    print(f"apply={APPLY}")
    out_ledger: dict[str, object] = {}
    for card in CARDS:
        at = os.path.join(BASE, card, "a20260919-01")
        ev = os.path.join(at, "evidence", card)
        rerun_p = os.path.join(at, "after", "rerun_sha256.json")
        sm_p = os.path.join(ev, "source_manifest.json")
        eh_p = os.path.join(ev, "evidence_hashes.json")
        dr_p = os.path.join(ev, "docfix_r3.json")
        enum_rel = f"evidence/{card}/oq_rulings_enumeration.json"

        print("")
        print(f"-- {card} --")
        r2dir = os.path.join(REVIEW, "copy_r2", card, "a20260919-01")

        # ---------- 2) after/rerun_sha256.json ----------
        # the r2 baseline is read from the verified r2 snapshot, never from the file
        # being rewritten, so this script is idempotent and always reports the true
        # r2 -> r3 delta even when it is run twice
        rerun = json.load(open(rerun_p, encoding="utf-8"))
        old_files = json.load(open(os.path.join(r2dir, "after", "rerun_sha256.json"),
                                   encoding="utf-8"))["files"]
        refreshed, changed_entries = {}, []
        for rel in sorted(old_files):
            p = os.path.join(at, rel.replace("/", os.sep))
            now = sha_file(p)
            refreshed[rel] = now
            if now != old_files[rel]:
                changed_entries.append({"path": rel, "sha256_r2": old_files[rel],
                                        "sha256_r3": now})
        missing = [rel for rel in old_files
                   if not os.path.exists(os.path.join(at, rel.replace("/", os.sep)))]
        rerun["files"] = refreshed
        rerun["revision"] = "r3"
        rerun["generated_after"] = (
            "every r2 edit including oracle.md and review.md appends, plus the r3 "
            "document/evidence consistency pass (oracle.md r2-section dedup, oq_rulings "
            "counts, qualified repack ledger, DEC-M08-1 correction)"
        )
        rerun["oracle_md_ledger"] = {
            "v1_frozen_body_sha256": dedupe[card]["authoritative_v1_claim"],
            "v1_frozen_body_prefix_bytes": dedupe[card]["authoritative_v1_cut"]["payload_bytes"],
            "whole_file_sha256_v1": sha_file(
                os.path.join(REVIEW, "copy", card, "a20260919-01", "oracle.md")),
            "whole_file_sha256_r2": dedupe[card]["oracle_md_sha256_before"],
            "whole_file_sha256_r3": dedupe[card]["oracle_md_sha256_after"],
            "note": "the files['oracle.md'] entry below tracks the CURRENT whole file; the "
                    "v1 frozen body hash it also records is still reproducible as "
                    "sha256(oracle.md[:prefix_bytes]) because the merge kept that prefix "
                    "byte-identical",
        }
        rerun["docfix_r3_note"] = (
            "entries refreshed in r3 so that this manifest keeps its own property of "
            "equalling the bytes on disk (the F-M08-01 fix). Entries whose value changed "
            "r2->r3 are listed in docfix_r3_changed_entries; the r2 values are preserved "
            "there rather than overwritten silently."
        )
        rerun["docfix_r3_changed_entries"] = changed_entries
        rerun_bytes = dump(rerun)
        print(f"   after/rerun_sha256.json entries={len(refreshed)} "
              f"changed_r2_to_r3={len(changed_entries)} missing={missing}")
        for row in changed_entries:
            print(f"      {row['path']}: {row['sha256_r2'][:16]} -> {row['sha256_r3'][:16]}")

        # ---------- 3) source_manifest.json ----------
        sm = json.load(open(sm_p, encoding="utf-8"))
        od = sm["oracle_document"]
        sm_before = sha_file(os.path.join(r2dir, "evidence", card, "source_manifest.json"))
        sm["oracle_document"] = {
            "path": od["path"],
            "sha256_now": dedupe[card]["oracle_md_sha256_after"],
            "sha256_now_note": (
                "whole-file hash AFTER the r3 merge; this is the value that tracks the "
                "file on disk"
            ),
            "sha256_before_r3_dedup": dedupe[card]["oracle_md_sha256_before"],
            "sha256_at_oracle_generation": od.get("sha256_at_oracle_generation"),
            "v1_frozen_body_sha256": dedupe[card]["authoritative_v1_claim"],
            "v1_frozen_body_prefix_bytes": dedupe[card]["authoritative_v1_cut"]["payload_bytes"],
            "v1_frozen_body_still_reproducible":
                verify[card]["P5_v1_claim_reproduces"],
            "honest_gap": od["honest_gap"],
            "honest_gap_r3_dedup_addendum": (
                "Revision r3 FOLDED the two duplicated 'revision r2' sections into ONE and "
                "INSERTED a provenance-gap note at the folded duplicate's former position "
                "(finding F-M08-06; wording corrected under F-R3-01). The fold removed only "
                "the byte-identical duplicate section and the note went in at that position, "
                "so live = pre[:kept_prefix_bytes] + note: the kept prefix is byte-for-byte "
                "unchanged (proved in recovery/docfix-r3/f06_verify.out.txt), and therefore "
                "the v1 frozen body and every frozen expectation are still byte-identical to "
                "what the product ran against."
            ),
            "mtime_ordering": od["mtime_ordering"],
            "oracle_script_selfcheck": od["oracle_script_selfcheck"],
            "docfix_r3_ledger": f"evidence/{card}/docfix_r3.json",
        }
        sm["oracle_document"]["mtime_ordering"] = dict(
            od["mtime_ordering"],
            note=("mtime ordering is unchanged in substance; the r2/r3 appends are after the "
                  "run by construction, which is why oracle.md's own mtime is later than the "
                  "product stdout"),
        )
        sm_bytes = dump(sm)
        sm_rel = f"evidence/{card}/source_manifest.json"
        sm_hash = hashlib.sha256(sm_bytes).hexdigest()
        # the refresh loops above read from disk BEFORE this file is rewritten, so the
        # new value has to be injected explicitly here (this is the whole point of
        # writing the ledgers in a forced order)
        if sm_rel in refreshed and refreshed[sm_rel] != sm_hash:
            changed_entries.append({"path": sm_rel, "sha256_r2": refreshed[sm_rel],
                                    "sha256_r3": sm_hash})
            refreshed[sm_rel] = sm_hash
            rerun["files"] = refreshed
            rerun["docfix_r3_changed_entries"] = changed_entries
            rerun_bytes = dump(rerun)
        print(f"   source_manifest.json {sm_before[:16]} -> "
              f"{hashlib.sha256(sm_bytes).hexdigest()[:16]} "
              f"(sha256_now {od['sha256_now'][:16]} -> "
              f"{dedupe[card]['oracle_md_sha256_after'][:16]})")

        # ---------- 1) evidence/<card>/docfix_r3.json ----------
        named_rows = []
        for key, info in named.items():
            c, rel = key.split("/", 1)
            if c == card:
                named_rows.append({
                    "path": rel,
                    "sha256_r1": info["sha256_r1"],
                    "sha256_r3": info["sha256_now"],
                    "changed_r1_to_r3": info["changed"],
                    "annotation_only": info.get(
                        "annotation_only_proof_deep_equal_after_stripping_added_keys"),
                    "added_keys": info.get("added_keys", []),
                    "removed_keys": info.get("removed_keys", []),
                    "pre_existing_leaf_values_compared": info.get("pre_existing_leaves"),
                    "pre_existing_leaf_values_changed": len(
                        info.get("changed_pre_existing_leaves", {})),
                })
        ledger = {
            "card_id": card,
            "pass": "r3 document/evidence consistency revision",
            "findings_addressed": ["F-M08-06", "F-M08-07", "F-M08-08", "F-M08-09"],
            "no_frozen_value_changed": (
                "no pre-registered expectation, tolerance, rejection condition, negative case "
                "or disclosure figure was changed; no product file was touched"
            ),
            "findings": {
                "F-M08-06": {
                    "what": "oracle.md carried two duplicated 'revision r2' sections and two "
                            "mutually exclusive pre-append hashes in the same ledger",
                    "action": "FOLDED the two r2 sections into one and INSERTED a "
                              "provenance-gap note at the folded duplicate's former position. "
                              "The insert point coincides with EOF of the new file, but the "
                              "mechanism is an INSERTION into the pre image's content, not a "
                              "trailing append: live = pre[:kept_prefix_bytes] + note, so "
                              "live[:kept_prefix_bytes] == pre[:kept_prefix_bytes] byte for "
                              "byte (equivalently, live carries pre's complete r2 body as a "
                              "prefix). F-R3-01: the earlier 'deleted + appended' phrasing was "
                              "correct arithmetic but the wrong mental model, and is replaced "
                              "here. The reproducible v1 hash is kept; the unreproducible value "
                              "is kept verbatim, labelled a provenance gap and barred from use "
                              "as a baseline",
                    "byte_account": (
                        f"{dedupe[card]['oracle_md_bytes_before']} (pre whole file) - "
                        f"{verify[card]['P2_deleted_bytes']} (folded duplicate = pre[K:]) + "
                        f"{verify[card]['P2_inserted_bytes']} (inserted r3 note) = "
                        f"{verify[card]['oracle_md_bytes_after']} (live whole file)"
                    ),
                    "kept_prefix_taken_from_the_preserved_pre_image": True,
                    "only_the_r3_block_changed_in_F_R3_01":
                        fold[card]["only_r3_block_changed"],
                    "r3_block_versions": {
                        "v1_original": {
                            "block_bytes": fold[card]["r3_block_bytes_before"],
                            "block_sha256": fold[card]["r3_block_sha256_before"],
                            "whole_file_sha256":
                                fold[card]["oracle_md_sha256_before_wording_fix"],
                            "note": "the reviewer's verified arithmetic "
                                    "(12592-1900+3711=14403 / 10912-1706+3709=12915 / "
                                    "11469-1903+3709=13275 / 19745-3585+3714=19874) refers "
                                    "to this version",
                        },
                        "v2_after_F_R3_01": {
                            "block_bytes": fold[card]["r3_block_bytes_after"],
                            "block_sha256": fold[card]["r3_block_sha256_after"],
                            "whole_file_sha256":
                                fold[card]["oracle_md_sha256_after_wording_fix"],
                            "note": "same kept prefix, same frozen text; only the block's prose "
                                    "and its self-consistent byte account changed",
                        },
                    },
                    "oracle_md_sha256_before": dedupe[card]["oracle_md_sha256_before"],
                    "oracle_md_bytes_before": dedupe[card]["oracle_md_bytes_before"],
                    "oracle_md_sha256_after": dedupe[card]["oracle_md_sha256_after"],
                    "oracle_md_bytes_after": dedupe[card]["oracle_md_bytes_after"],
                    "removed_duplicate_bytes": verify[card]["P2_deleted_bytes"],
                    "removed_duplicate_sha256": verify[card]["P2_deleted_sha256"],
                    "added_r3_note_bytes": verify[card]["P2_inserted_bytes"],
                    "added_r3_note_sha256": verify[card]["P2_inserted_sha256"],
                    "kept_prefix_bytes": verify[card]["P1_kept_region_bytes"],
                    "kept_prefix_sha256_before": verify[card]["P1_kept_region_sha256_before"],
                    "kept_prefix_sha256_after": verify[card]["P1_kept_region_sha256_after"],
                    "kept_prefix_byte_identical": verify[card]["P1_kept_region_byte_identical"],
                    "sections_byte_unequal": verify[card]["P3_sections_byte_unequal"],
                    "r2_section_occurrences_after": verify[card][
                        "P3_r2_section_occurrences_after"],
                    "authoritative_v1_claim": dedupe[card]["authoritative_v1_claim"],
                    "authoritative_v1_cut": dedupe[card]["authoritative_v1_cut"],
                    "provenance_gap_claim": dedupe[card]["provenance_gap_claim"],
                    "provenance_gap_cut": dedupe[card]["provenance_gap_cut"],
                    "provenance_gap_total_matches_over_all_byte_cuts":
                        dedupe[card]["provenance_gap_total_matches"],
                    "provenance_gap_meaning": (
                        "the value reproduces ONLY as the sha256 of the intermediate write "
                        "buffer 'v1 frozen body + first r2 section body' (a byte prefix of the "
                        "file, not any document state before an append). It therefore cannot "
                        "serve as a hash-ledger baseline; the reviewer's statement that no "
                        "line-boundary cut reproduces it is upheld (the usual line-boundary "
                        "scan uses rstrip, which eats the CR of this file's CRLF append "
                        "region), and this pass adds the byte-exact provenance."
                    ),
                    "reproduce": (
                        "<iso venv python> -X utf8 -B recovery/docfix-r3/f06_brute.py > "
                        "recovery/docfix-r3/f06_brute.out.txt ; "
                        "<iso venv python> -X utf8 -B recovery/docfix-r3/f06_classify.py > "
                        "recovery/docfix-r3/f06_classify.out.txt"
                    ),
                    "proof": (
                        "<iso venv python> -X utf8 -B recovery/docfix-r3/f06_verify.py > "
                        "recovery/docfix-r3/f06_verify.out.txt"
                    ),
                    "pre_image": f"recovery/docfix-r3/oracle_pre_{card}.md",
                    "merged_image": f"recovery/docfix-r3/oracle_merged_{card}.md",
                },
                "F-M08-07": {
                    "what": "oq_rulings.json miscounted the enumeration and credited the "
                            "enumeration to the reviewer in the first person",
                    "action": "re-enumerated from the code; counts corrected; attribution "
                              "rewritten in the third person with the originals preserved",
                    "sha256_before": oqs[card]["sha256_before"],
                    "sha256_after": oqs[card]["sha256_after"],
                    "ratio_drivers_total_was": oqs[card]["ratio_drivers_total_was"],
                    "ratio_drivers_total_now": oqs[card]["ratio_drivers_total_now"],
                    "ratio_drivers_not_in_0_1_was": oqs[card]["ratio_drivers_not_in_0_1_was"],
                    "ratio_drivers_not_in_0_1_now": oqs[card]["ratio_drivers_not_in_0_1_now"],
                    "missing_driver_added": "direct_growth.growth_rate, domain (-1, inf)",
                    "enumeration_evidence": enum_rel,
                    "enumeration_evidence_sha256": oqs[card]["enumeration_evidence_sha256"],
                    "reproduce": (
                        "<iso venv python> -X utf8 -B recovery/docfix-r3/f07_enumerate.py > "
                        "recovery/docfix-r3/f07_enumerate.out.txt ; "
                        "<iso venv python> -X utf8 -B recovery/docfix-r3/f07_fix_oq.py > "
                        "recovery/docfix-r3/f07_fix_oq.out.txt"
                    ),
                },
                "F-M08-08": {
                    "what": "'the frozen artefacts were not changed' needed qualification "
                            "because the r2 annotation repack changed bytes",
                    "action": "declared the repack scope with old/new hashes and proved the "
                              "difference is annotation-only",
                    "qualified_statement": (
                        "the oracle.md v1 frozen body and every frozen expectation are "
                        "byte-unchanged and no product file was touched; oracle.md as a whole "
                        "and the files listed in repack_scope changed for documentation "
                        "reasons only"
                    ),
                    "r1_r2_r3_reference_states": {
                        "r1": "reviewer snapshot copy/ (verified: copy/oracle.md == the "
                              "authoritative v1 claim for every card)",
                        "r2": "reviewer snapshot copy_r2/ (verified: copy_r2/oracle.md == the "
                              "pre-r3 whole-file hash for every card)",
                        "r3": "attempt tree on disk after this pass",
                    },
                    "named_by_F_M08_08": named_rows,
                    "measured_correction": (
                        "MEASURED, and it refines the finding: against the verified r1 "
                        "snapshot only THREE of the five named files actually changed "
                        "(M08 cases.json, M08 run_result.json, M08 negative_results.json). "
                        "M07 run_result.json, M07 negative_results.json and M06 "
                        "negative_results.json are BYTE-IDENTICAL to the r1 snapshot, so they "
                        "need no qualification. The three that did change carry only added "
                        "annotation keys: stripping them makes the document deep-equal to r1, "
                        "and 0 of 117 / 0 of 220 / 0 of 189 pre-existing leaf values changed."
                    ),
                    "repack_scope_r1_to_r2_from_binding_and_handoff": (
                        "see binding.json / handoff.json -> docfix_r3_hash_ledger."
                        "repack_scope_r1_to_r2"
                    ),
                    "reproduce": (
                        "<iso venv python> -X utf8 -B recovery/docfix-r3/f08_named_files.py > "
                        "recovery/docfix-r3/f08_named_files.out.txt ; "
                        "<iso venv python> -X utf8 -B recovery/docfix-r3/f08_repack_diff.py > "
                        "recovery/docfix-r3/f08_repack_diff.out.txt"
                    ),
                },
                "F-M08-09": {
                    "what": "M08 decision.md DEC-M08-1 still carried the r1 wording and did "
                            "not point at the handoff's three owner steps",
                    "action": "appended a superseding DEC-M08-1 section that points explicitly "
                              "at handoff.json.owner_action_required (all three steps, "
                              "including the explicit prohibition on re-picking the example); "
                              "the r1 wording is preserved verbatim above it",
                    "decision_md_sha256_before": docs[card]["decision.md"]["sha256_before"],
                    "decision_md_sha256_after": docs[card]["decision.md"]["sha256_after"],
                    "points_at": "handoff.json.owner_action_required (id F-M08-02-remediation)",
                    "forbidden_constraint_restated":
                        "re-picking the example so that only the convenient reading passes",
                    "m08_only": card == "M08",
                },
            },
            "r3_changed_files_in_this_attempt": {
                "oracle.md": {"sha256_before": dedupe[card]["oracle_md_sha256_before"],
                              "sha256_after": dedupe[card]["oracle_md_sha256_after"]},
                "evidence/": {
                    f"evidence/{card}/oq_rulings.json":
                        {"sha256_before": oqs[card]["sha256_before"],
                         "sha256_after": oqs[card]["sha256_after"]},
                    f"evidence/{card}/source_manifest.json":
                        {"sha256_before": sm_before,
                         "sha256_after": hashlib.sha256(sm_bytes).hexdigest()},
                },
                "binding.json": docs[card]["binding.json"],
                "handoff.json": docs[card]["handoff.json"],
                "decision.md": docs[card]["decision.md"],
                "after/rerun_sha256.json": {
                    "sha256_before": sha_file(os.path.join(r2dir, "after",
                                                           "rerun_sha256.json")),
                    "sha256_after": hashlib.sha256(rerun_bytes).hexdigest()},
                "new_files": [
                    f"evidence/{card}/oq_rulings_enumeration.json",
                    f"evidence/{card}/docfix_r3.json",
                ],
                "evidence_hashes.json": {
                    "note": "written last; its own hash after this pass is discoverable from "
                            "the file itself and from recovery/docfix-r3/tree_post.txt"
                },
            },
            "downstream_ledgers_updated": {
                "evidence/<card>/source_manifest.json": "oracle_document.sha256_now -> r3, "
                    "with the r2 value preserved as sha256_before_r3_dedup",
                "after/rerun_sha256.json": "all entries refreshed from disk so the manifest "
                    "still equals the bytes on disk (F-M08-01 property); r2 values of changed "
                    "entries preserved in docfix_r3_changed_entries",
                "evidence/<card>/evidence_hashes.json": "revision r3, hashes refreshed, "
                    "docfix_r3.json and oq_rulings_enumeration.json added",
            },
            "product_repos": {
                "revenue-forecast": "read-only; no write",
                "company-wiki": "read-only; no write",
                "filing-fetch": "read-only; no write",
            },
        }
        dr_bytes = dump(ledger)

        print(f"   docfix_r3.json bytes={len(dr_bytes)} "
              f"sha256={hashlib.sha256(dr_bytes).hexdigest()[:16]}")

        # ---------- 4) evidence_hashes.json ----------
        eh = json.load(open(eh_p, encoding="utf-8"))
        eh_base = json.load(open(os.path.join(r2dir, "evidence", card,
                                              "evidence_hashes.json"),
                                 encoding="utf-8"))["files"]
        refreshed_eh, changed_eh = {}, []
        for rel in sorted(eh_base):
            p = os.path.join(at, rel.replace("/", os.sep))
            now = sha_file(p)
            refreshed_eh[rel] = now
            if now != eh_base[rel]:
                changed_eh.append({"path": rel, "sha256_before": eh_base[rel],
                                   "sha256_after": now})
        refreshed_eh[f"evidence/{card}/docfix_r3.json"] = hashlib.sha256(dr_bytes).hexdigest()
        refreshed_eh[enum_rel] = sha_file(os.path.join(ev, "oq_rulings_enumeration.json"))
        for rel in (f"evidence/{card}/docfix_r3.json", enum_rel):
            changed_eh.append({"path": rel, "sha256_before": None,
                               "sha256_after": refreshed_eh[rel],
                               "change": "added in r3"})
        if sm_rel in refreshed_eh and refreshed_eh[sm_rel] != sm_hash:
            changed_eh = [row for row in changed_eh if row["path"] != sm_rel]
            changed_eh.append({"path": sm_rel, "sha256_before": refreshed_eh[sm_rel],
                               "sha256_after": sm_hash})
            refreshed_eh[sm_rel] = sm_hash
        eh_out = {
            "card_id": eh["card_id"],
            "revision": "r3",
            "files": dict(sorted(refreshed_eh.items())),
            "docfix_r3_note": (
                "revision r3 = document/evidence consistency pass. Hash entries refreshed and "
                "two files added (docfix_r3.json, oq_rulings_enumeration.json). Entries whose "
                "value changed are listed in docfix_r3_changed_entries with their previous "
                "value; no entry was removed."
            ),
            "docfix_r3_changed_entries": changed_eh,
        }
        eh_bytes = dump(eh_out)
        print(f"   evidence_hashes.json entries={len(refreshed_eh)} "
              f"changed={len(changed_eh)} "
              f"sha256={hashlib.sha256(eh_bytes).hexdigest()[:16]}")
        for row in changed_eh:
            before_short = (row["sha256_before"][:16] if row["sha256_before"] else "NEW")
            print(f"      {row['path']}: {before_short} -> "
                  f"{row['sha256_after'][:16]}")

        if APPLY:
            open(dr_p, "wb").write(dr_bytes)
            open(rerun_p, "wb").write(rerun_bytes)
            open(sm_p, "wb").write(sm_bytes)
            open(eh_p, "wb").write(eh_bytes)
            for p, blob in ((dr_p, dr_bytes), (rerun_p, rerun_bytes),
                            (sm_p, sm_bytes), (eh_p, eh_bytes)):
                assert sha_file(p) == hashlib.sha256(blob).hexdigest(), p
            print("   APPLIED")

        out_ledger[card] = {
            "docfix_r3.json": hashlib.sha256(dr_bytes).hexdigest(),
            "after/rerun_sha256.json": hashlib.sha256(rerun_bytes).hexdigest(),
            "evidence_hashes.json": hashlib.sha256(eh_bytes).hexdigest(),
            "source_manifest.json_before": sm_before,
            "source_manifest.json_after": hashlib.sha256(sm_bytes).hexdigest(),
            "rerun_entries": len(refreshed),
            "rerun_entries_changed": len(changed_entries),
            "evidence_hashes_entries": len(refreshed_eh),
        }

    with open(os.path.join(HERE, "f08_ledger.json"), "w", encoding="utf-8") as fh:
        json.dump(out_ledger, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("")
    print("wrote f08_ledger.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
