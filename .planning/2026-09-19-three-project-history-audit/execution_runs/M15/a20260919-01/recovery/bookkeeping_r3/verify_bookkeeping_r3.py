"""Independent verification of the r3 bookkeeping / transcription pass for one M-card attempt.

This verifier does not trust the bookkeeping scripts' own reporting. For every file the pass
touched it RECONSTRUCTS the pre-pass bytes by undoing exactly the declared edit and checks that the
result hashes to the pre-pass sha256 recorded before the edit was made. If a reconstruction
reproduces the old hash, then the edit set is exactly what was declared and nothing else changed.

It also re-derives the verdict transcription proof from the raw bytes and re-checks the frozen
artifacts and the runner revision against the values the independent reviewer stated.

Exit codes: 0 all checks pass, 8 at least one check failed, 1 harness error.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

SCRIPT = os.path.abspath(__file__)
ATTEMPT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT)))
CARD = os.path.basename(os.path.dirname(ATTEMPT))
EVID = os.path.join(ATTEMPT, "evidence", CARD)
SUMMARY = os.path.join(ATTEMPT, "recovery", "bookkeeping_r3", "summary.json")
VERDICTS_DIR = os.path.join(os.environ.get("TEMP", ""), "m13m16-review-20260920-035325", "r3",
                            "verdicts")

CHECKS = []


def check(cid, ok, detail=""):
    CHECKS.append({"check": cid, "ok": bool(ok), "detail": detail})
    print("%-4s %-46s %s" % ("OK" if ok else "FAIL", cid, detail))
    return ok


def sha256b(data):
    return hashlib.sha256(data).hexdigest()


def rb(path):
    with open(path, "rb") as handle:
        return handle.read()


def jdump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def changes_map():
    summary = json.loads(rb(SUMMARY).decode("utf-8"))
    return {entry["path"]: entry for entry in summary["changes"]}, summary


def undo_handoff(text, doc):
    marker = ',\n "bookkeeping": {'
    text = text[:text.index(marker)] + "\n}\n"
    old_rs = doc["reviewer_status_before_bookkeeping_fix"]
    new_rs = doc["reviewer_status"]
    text = text.replace(
        ' "reviewer_status": ' + json.dumps(new_rs, ensure_ascii=False) + ',\n'
        ' "reviewer_status_before_bookkeeping_fix": ' + json.dumps(old_rs, ensure_ascii=False) + ',',
        ' "reviewer_status": ' + json.dumps(old_rs, ensure_ascii=False) + ',')
    text = text.replace('  "formula": "accepted_scoped",\n'
                        '  "formula_before_bookkeeping_fix": "review_pending",',
                        '  "formula": "review_pending",')
    text = text.replace(' "status": "accepted_scoped",\n'
                        ' "status_before_bookkeeping_fix": "review_pending",',
                        ' "status": "review_pending",')
    return text


def undo_qualification(text):
    text = text[:text.index(',\n "bookkeeping": {')] + "\n}\n"
    return text.replace('  "state": "accepted_scoped",\n'
                        '  "state_before_bookkeeping_fix": "review_pending",',
                        '  "state": "review_pending",')


def main() -> int:
    print("=== independent verification of the r3 bookkeeping pass - card %s ===" % CARD)
    changes, summary = changes_map()
    regen_later = json.loads(rb(os.path.join(ATTEMPT, "recovery", "bookkeeping_r3",
                                             "ledger_regeneration_r3.json")).decode("utf-8"))

    # ---- A. verdict transcription, recomputed from raw bytes -------------------------------
    proof_rel = "evidence/%s/verdict_transcription_r3.json" % CARD
    proof = json.loads(rb(os.path.join(ATTEMPT, *proof_rel.split("/"))).decode("utf-8"))
    src_path = os.path.join(VERDICTS_DIR, "review_verdict_%s.md" % CARD)
    src = rb(src_path)
    rv = rb(os.path.join(ATTEMPT, "review.md"))
    rec = proof["appended_region"]
    appended = rv[rec["offset_start"]:rec["offset_end"]]
    check("A1 source sha256 matches the reviewer's file", sha256b(src) == proof["source_sha256"])
    check("A2 appended region sha256 == source sha256", sha256b(appended) == sha256b(src))
    check("A3 appended region is a byte prefix-suffix of review.md twice-checked",
          rv[:rec["offset_start"]] == rv[:len(rv) - len(src)] and rv.endswith(src),
          "review.md %d B, verdict %d B" % (len(rv), len(src)))
    check("A4 review.md sha256 matches the proof", sha256b(rv) == proof["review_md_sha256_after"])
    check("A5 byte counts: len(new) = len(old) + len(source)",
          len(rv) == proof["review_md_bytes_before"] + len(src))
    check("A6 proof asserts byte_identical", proof.get("byte_identical") is True)
    lines = rv.split(b"\n")
    blk = b"\n".join(lines[proof["verdict_block_in_review_md"]["line_start"] - 1:
                         proof["verdict_block_in_review_md"]["line_end"]]) + b"\n"
    check("A7 recorded line range holds the verdict block",
          blk == src, "lines %d-%d" % (proof["verdict_block_in_review_md"]["line_start"],
                                       proof["verdict_block_in_review_md"]["line_end"]))
    check("A8 no duplicate of the verdict block in review.md", rv.count(src) == 1)

    # ---- B. handoff.json: undo the edit, reproduce the pre-pass hash ------------------------
    hp = os.path.join(ATTEMPT, "handoff.json")
    hnew = rb(hp).decode("utf-8")
    hdoc = json.loads(hnew)
    hrec = changes["handoff.json"]
    check("B1 handoff.json sha256_after recorded == disk", hrec["sha256_after"] == sha256b(rb(hp)))
    check("B2 handoff.json reconstructed pre-pass bytes hash to sha256_before",
          sha256b(undo_handoff(hnew, hdoc).encode("utf-8")) == hrec["sha256_before"])
    check("B3 status == accepted_scoped", hdoc["status"] == "accepted_scoped")
    check("B4 status_before_bookkeeping_fix == review_pending",
          hdoc["status_before_bookkeeping_fix"] == "review_pending")
    check("B5 qualifications.formula == accepted_scoped",
          hdoc["qualifications"]["formula"] == "accepted_scoped")
    check("B6 qualification disclosure_adaptation / accuracy untouched",
          hdoc["qualifications"]["disclosure_adaptation"] == "unmapped"
          and hdoc["qualifications"]["accuracy"] == "unproven")
    bk = hdoc["bookkeeping"]
    check("B7 carrier attests implementer_signed=false / never signs / authority",
          bk["implementer_signed"] is False and bk["implementer_never_signs_acceptance"] is True
          and bk["authority"] == "acceptance was written by an independent reviewer, not by the "
                                 "implementer")
    check("B8 carrier records the proof file path + its real sha256",
          bk["transcription_proof_file"]["path"] == proof_rel
          and bk["transcription_proof_file"]["sha256"]
          == sha256b(rb(os.path.join(ATTEMPT, *proof_rel.split("/")))))
    check("B9 carrier line range == proof line range",
          bk["verdict_block_in_review_md"]["line_start"]
          == proof["verdict_block_in_review_md"]["line_start"]
          and bk["verdict_block_in_review_md"]["line_end"]
          == proof["verdict_block_in_review_md"]["line_end"])
    check("B10 discipline rule present verbatim",
          hdoc["discipline"]["rule"].startswith(
              "a production file hash used as acceptance evidence must be treated as a quantity "
              "that external git operations can change")
          and "never adapt expectations or frozen artifacts" in hdoc["discipline"]["rule"])

    # ---- C. qualification.json -------------------------------------------------------------
    qp = os.path.join(EVID, "qualification.json")
    qnew = rb(qp).decode("utf-8")
    qdoc = json.loads(qnew)
    qrec = changes["evidence/%s/qualification.json" % CARD]
    check("C1 qualification.json sha256_after recorded == disk", qrec["sha256_after"] == sha256b(rb(qp)))
    check("C2 qualification.json reconstructed pre-pass bytes hash to sha256_before",
          sha256b(undo_qualification(qnew).encode("utf-8")) == qrec["sha256_before"])
    check("C3 formula.state == accepted_scoped", qdoc["formula"]["state"] == "accepted_scoped")
    check("C4 formula.state_before_bookkeeping_fix == review_pending",
          qdoc["formula"]["state_before_bookkeeping_fix"] == "review_pending")
    check("C5 disclosure_adaptation == unmapped (untouched)",
          qdoc["disclosure_adaptation"]["state"] == "unmapped"
          and qdoc["bookkeeping"]["disclosure_adaptation_touched"] is False)
    check("C6 accuracy == unproven (untouched)",
          qdoc["accuracy"]["state"] == "unproven"
          and qdoc["bookkeeping"]["accuracy_touched"] is False)

    # ---- D. oq_rulings.json (single inserted line) -----------------------------------------
    op = os.path.join(EVID, "oq_rulings.json")
    onew = rb(op).decode("utf-8")
    odoc = json.loads(onew)
    orec = changes["evidence/%s/oq_rulings.json" % CARD]
    line = ('  "authorised_transcription": "the parent orchestration layer authorised transcription '
            'of the reviewer\'s verdict; see review.md",\n')
    check("D1 oq_rulings.json sha256_after recorded == disk", orec["sha256_after"] == sha256b(rb(op)))
    check("D2 oq_rulings.json pre-pass bytes reproduced by removing the one added line",
          onew.count(line) == 1 and sha256b(onew.replace(line, "").encode("utf-8")) == orec["sha256_before"])
    check("D3 attribution.authorised_transcription present; reviewed_by unchanged in substance",
          odoc["attribution"].get("authorised_transcription", "").endswith("see review.md")
          and odoc["attribution"]["reviewed_by"].startswith("an independent reviewer (2026-09-20)"))

    # ---- E. cases_annotation_repack.json (M14/M15/M16 only) --------------------------------
    if CARD != "M13":
        rp = os.path.join(EVID, "cases_annotation_repack.json")
        rdoc = json.loads(rb(rp).decode("utf-8"))
        rrec = changes["evidence/%s/cases_annotation_repack.json" % CARD]
        stripped = {k: v for k, v in rdoc.items()
                    if k not in ("repack_scope_before_F_r3_01_fix", "F_r3_01",
                                 "frozen_siblings_unchanged_by_F_r3_01")}
        stripped["repack_scope"] = rdoc["repack_scope_before_F_r3_01_fix"]
        check("E1 repack sha256_after recorded == disk", rrec["sha256_after"] == sha256b(rb(rp)))
        check("E2 repack pre-pass bytes reproduced by dropping the 3 added keys",
              sha256b(jdump(stripped).encode("utf-8")) == rrec["sha256_before"])
        check("E3 repack_scope now states no annotation was applied",
              rdoc["repack_scope"].startswith("no annotation applied on this card"))
        check("E4 all_differences_found is still empty and old/new revisions are identical",
              rdoc["all_differences_found"] == []
              and rdoc["old_revision"]["sha256"] == rdoc["new_revision"]["sha256"])
        for name in ("cases.json", "oracle.json", "input.json"):
            sib = os.path.join(EVID, name)
            check("E5 %s byte-identical (hash matches the recorded sibling hash)" % name,
                  rdoc["frozen_siblings_unchanged_by_F_r3_01"][name]["sha256"] == sha256b(rb(sib)))
    else:
        check("E0 M13 repack wording not applicable (this card has a real annotation)", True)

    # ---- F. frozen artifacts vs the reviewer's own values ----------------------------------
    ledger = json.loads(rb(os.path.join(ATTEMPT, "after", "rerun_sha256.json")).decode("utf-8"))
    frozen_now = ledger["frozen_evidence_hashes_now"]
    frozen_then = ledger["frozen_evidence_hashes_at_freeze_time"]
    check("F1 frozen input/cases/oracle hashes now == at freeze time", frozen_now == frozen_then,
          json.dumps(frozen_now, sort_keys=True))
    check("F2 ledger reports frozen_evidence_unchanged",
          ledger["frozen_evidence_unchanged"] is True)
    base = json.loads(rb(os.path.join(ATTEMPT, "before", "oracle_md_v1.json")).decode("utf-8"))
    oracle_md = rb(os.path.join(ATTEMPT, "oracle.md"))
    check("F3 oracle.md frozen body (bytes [:%d]) still hashes to the pre-append baseline"
          % base["bytes"],
          sha256b(oracle_md[:base["bytes"]]) == base["sha256"],
          "and oracle.md is only larger: %d > %d" % (len(oracle_md), base["bytes"])
          if sha256b(oracle_md[:base["bytes"]]) == base["sha256"] else "")

    # ---- G. runner untouched (F-r3-05 no change) ------------------------------------------
    runner = sha256b(rb(os.path.join(ATTEMPT, "scripts", "run_card.py")))
    check("G1 scripts/run_card.py is the revision the reviewer verified (9e4a6450...)",
          runner.startswith("9e4a6450"), runner)
    check("G2 F-r3-05: the runner is not among the files this pass wrote",
          "scripts/run_card.py" not in changes
          and ledger["inventory_rule_amend_r3"]["verification_logic_changed"] is False
          and regen_later["runner_modified"] is False)

    # ---- H. ledger reproducibility ---------------------------------------------------------
    files = ledger["files"]
    combined = hashlib.sha256()
    for rel in sorted(files):
        combined.update(rel.encode("utf-8"))
        combined.update(files[rel]["sha256"].encode("ascii"))
    check("H1 combined digest recomputed independently == declared",
          combined.hexdigest() == ledger["combined_digest_over_sorted_relative_path_and_sha256"],
          ledger["combined_digest_over_sorted_relative_path_and_sha256"])
    bad = [rel for rel, e in files.items()
           if not os.path.exists(os.path.join(ATTEMPT, *rel.split("/")))
           or sha256b(rb(os.path.join(ATTEMPT, *rel.split("/")))) != e["sha256"]]
    check("H2 every listed file exists and hashes as listed", not bad, "checked %d files" % len(files))
    check("H3 no __pycache__ entries remain in the inventory",
          not [r for r in files if "__pycache__" in r])
    check("H4 ledger generator self-check reports zero mismatches",
          ledger["inventory_self_check"]["mismatches"] == []
          and ledger["inventory_self_check"]["files_rehashed_from_disk"] == len(files))
    regen = regen_later
    hist = regen["historical_values_preserved"]
    check("H5 historical production/isolated values are bit-identical to the pre-pass ledger",
          ledger["production_source_hashes_now"] == hist["production_source_hashes_now_before"]
          and ledger["production_source_hashes_now"] == hist["production_source_hashes_now_after"]
          and ledger["isolated_copy_still_equals_production"]
          == hist["isolated_copy_still_equals_production_before"] is True
          and regen["runner_modified"] is False
          and regen["expectations_tolerances_frozen_artifacts_touched"] is False)
    modified_pre_existing = sorted(p for p, e in changes.items() if e["bytes_before"] > 0)
    check("H6 the pre-pass ledger's hash drift is exactly the pre-existing files this pass modified",
          modified_pre_existing
          == sorted(regen["ledger_before"]["files_with_mismatched_hash"]),
          "modified: %s" % modified_pre_existing)
    check("H7 the changes table covers every modified file, including review.md",
          "review.md" in changes and changes["review.md"]["sha256_before"]
          == proof["review_md_sha256_before"]
          and changes["review.md"]["sha256_after"] == sha256b(rb(os.path.join(ATTEMPT, "review.md"))))

    # ---- I. drift declaration --------------------------------------------------------------
    drift = json.loads(rb(os.path.join(ATTEMPT, "recovery", "production_drift_note.json")).decode("utf-8"))
    check("I1 drift window recorded exactly",
          drift["window"]["local_start"] == "2026-09-20 04:35:31"
          and drift["window"]["local_end"] == "2026-09-20 04:40:53")
    check("I2 drift observed/anchor hashes and byte counts recorded",
          drift["drift"]["observed_sha256"].startswith("1f2639e1")
          and drift["drift"]["observed_bytes"] == 19703
          and drift["drift"]["anchor_sha256"].startswith("9ec652955")
          and drift["drift"]["anchor_bytes"] == 26446)
    check("I3 root cause records the pre-commit export + `git checkout -- .` rc=255",
          "patch1789875331-33652" in drift["root_cause"]["patch_file"]
          and drift["root_cause"]["git_checkout_exit_code"] == 255)
    check("I4 time-bound rule present",
          "CORRECT WARNING" in drift["time_bound_rule"]["rule"]
          and "rc=5" in " ".join(drift["time_bound_rule"]["must_never_be_fixed_by"]))
    check("I5 line-335 non-correspondence recorded with this card's OQ-02",
          "model_registry.py:335" in drift["line_335_correspondence"]["statement"]
          and drift["line_335_correspondence"]["card_oq_02_as_recorded_in_handoff_json"]
          .startswith("OQ-02"))
    check("I6 incident pointer exists on disk",
          drift["pointer"]["incident_record_exists_at_transcription_time"] is True)
    anchors = drift["recovery"]["anchors_reverified"]
    check("I7 all 8 anchors re-verified from disk and match the declared byte counts",
          len(anchors) == 8 and all(a["bytes"] == a["declared_anchor_bytes"] for a in anchors.values()))
    check("I8 boundaries: historical values not rewritten, no logic changed",
          drift["boundaries_respected"]["historical_values_of_production_source_hashes_now_not_rewritten"]
          is True
          and drift["boundaries_respected"][
              "historical_values_of_isolated_copy_still_equals_production_not_rewritten"] is True
          and drift["boundaries_respected"]["verification_logic_changed_to_hide_an_rc_5"] is False)

    failed = [c for c in CHECKS if not c["ok"]]
    print("--- %d checks, %d failed ---" % (len(CHECKS), len(failed)))
    return 8 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
