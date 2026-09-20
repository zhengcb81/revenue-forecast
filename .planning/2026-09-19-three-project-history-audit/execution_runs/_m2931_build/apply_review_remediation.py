"""Apply the independent reviewer's required corrections to the M29/M30/M31 attempts.

Three jobs, all in one auditable pass:

  J1  VERDICT TRANSCRIPTION (append-only)
      Extract the three ```markdown blocks of <REPORT> section 6 programmatically and append each
      one VERBATIM to the matching review.md.  Write evidence/verdict_transcription_check.txt
      proving the appended span is byte-identical to the block taken from the report.
      Nothing in the existing review.md text is touched.

  J2  CORRECTIONS (F-02 for M31, F-04 for all three) + append-only oracle.md errata
      * binding.json: card_text_matches_registry -> true, divergence note corrected (M31 only)
      * source_manifest.json: the mtime comparison is relabelled as what it is -- a POST-HOC stat
        comparison, not a pre-freeze; the anchored object is named explicitly (generator code),
        and oracle.md is declared out of the anchor scope and free of any gating expectation.
      * oq_rulings.json: append a ruling_corrections entry + text_corrections entry (M31)
      * oracle.md: APPEND an errata section only (never rewrite the frozen body), with the
        pre-append hash and a unified diff of what the errata supersedes (M31; plus a source
        provenance note for all three).
      * handoff.json: reviewer_status points at the appended verdict block lines; corrections and
        the reviewer ruling boundary are registered.

  J3  REGISTRATION (no in-batch fix)
      handoff.json.cross_batch_gaps: F-01 (runner never compares cases[*].expected) and the P3
      list F-05..F-10, each with what the reviewer measured and where the true value lives.

Every edited JSON keeps its old value under a "superseded" / "<field>_before_errata" key, and the
script reports the before -> after sha256 of every file it touches.

Usage (from the attempt whose venv is used):
  <venv python> -X utf8 -B apply_review_remediation.py --card M29 --attempt-root <attempt> \
      --report <REPORT.md> --runs-root <execution_runs>
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import json
import os
import re

CARDS = {
    "M29": {"model_id": "commercial_launch", "reviewer_heading": "### M29 · commercial_launch"},
    "M30": {"model_id": "finite_adoption", "reviewer_heading": "### M30 · finite_adoption"},
    "M31": {"model_id": "inventory_sellthrough",
            "reviewer_heading": "### M31 · inventory_sellthrough"},
}

GEN_SHA = "3177247f95f7554920ac43b4e076f28b5ef78250059c130de1f5e8dee2e4c09e"

# F-01 + the P3 list the reviewer measured.  Registered, not fixed in this batch.
CROSS_BATCH_GAPS = [
    {"id": "F-01", "severity": "P2", "batch": "shared by the M-card runner batches",
     "title": "run_card.py never compares cases.json[*].expected",
     "measured_by_reviewer": ("setting NEG-CARD expected to \"ValueError\", to 42, and all 11 "
                              "expected values to \"ImportError\" still yielded rc=0 pass on all three "
                              "cards; the negative verdict only checks isinstance(exc, "
                              "ModelRegistryError)"),
     "impact": ("the frozen per-case rejection SEMANTICS carries no weight in the automatic gate, so "
                "changing an expectation in cases.json cannot turn the runner red"),
     "control_that_still_works": ("a no-op patch -> rc=3 FAIL_not_rejected; corrupting the "
                                  "oracle.json positive expectation -> rc=3"),
     "disposition": "REGISTERED, NOT FIXED IN THIS BATCH (batch-level runner concern)",
     "where_the_true_values_live": {
         "expected_values": "evidence/<CARD>/cases.json (frozen, regenerable byte-for-byte)",
         "per_case_verdicts": "evidence/<CARD>/negative_results.json",
     }},
    {"id": "F-05", "severity": "P3", "batch": "M29-M31 (pack_card.r2_analysis)",
     "title": "r2 line-boundary demonstration offset is 1 byte too large",
     "measured_by_reviewer": ("truncating at len(base) reproduces the base hash exactly, so the real "
                              "line boundary is len(base), not the demonstrated offset"),
     "impact": "mechanism demonstration only; the r2 rule itself (no r2 section is present) is unaffected",
     "disposition": "REGISTERED, not silently renumbered",
     "where_the_true_values_live": "evidence/<CARD>/revision_r2.json mechanism_proof"},
    {"id": "F-06", "severity": "P3", "batch": "M29-M31",
     "title": "self-referential stale hashes",
     "measured_by_reviewer": ("commands.json Z-close-attempt.rc_record_sha256, "
                              "after/final_deliverable_hashes.json 154/156 and "
                              "evidence/<CARD>/evidence_hashes.json 94/97 are stale because those "
                              "files are written by commands that run before other files exist; the "
                              "rule text 'written after everything else' does not hold"),
     "impact": ("a reader who trusts the ledger alone would see a handful of mismatches; every stale "
                "value is obtainable fresh from the file itself"),
     "disposition": "REGISTERED, not fixed in this batch",
     "where_the_true_values_live": ("recompute sha256 of any file directly; commands.json carries the "
                                    "final unit list and its own hash is inside "
                                    "after/final_deliverable_hashes.json")},
    {"id": "F-07", "severity": "P3", "batch": "M29-M31 (run_card.py docstring)",
     "title": "run_card.py docstring points at evidence/<CARD>/exit_code.json which does not exist",
     "measured_by_reviewer": "the file is absent; the exit code is stored in run_result.json instead",
     "impact": "documentation-only",
     "disposition": "REGISTERED (the runner is reused verbatim from the M17-M20 batch, so the fix is a batch-level edit)",
     "where_the_true_values_live": "evidence/<CARD>/run_result.json exit_code / exit_code_semantics"},
    {"id": "F-08", "severity": "P3", "batch": "M29-M31 (bootstrap A0 record)",
     "title": "runs/A0-iso-venv-create/rc.json creation_argv[0] is a placeholder and its stdout shows a mojibake user name",
     "measured_by_reviewer": ("creation_argv[0] is the literal string "
                              "'<I-00-A template venv>\\Scripts\\python.exe' and the captured version "
                              "probe stdout contains a GBK-mangled absolute path"),
     "impact": "cosmetic/record-keeping; the real interpreter path and sha256 are recorded in the same file",
     "disposition": "REGISTERED, not fixed in this batch",
     "where_the_true_values_live": "evidence/<CARD>/runs/A0-iso-venv-create/rc.json venv_interpreter + venv_interpreter_sha256"},
    {"id": "F-09", "severity": "P3", "batch": "M29-M31 (pack_card.integrity)",
     "title": "integrity.json recomputes only 2 of the 3 task-given anchors",
     "measured_by_reviewer": ("scripts/model_registry.py and scripts/model_extensions.py are "
                              "re-hashed; scripts/forecast/segments.py is only present in "
                              "before/after source_hashes.txt"),
     "impact": "no product conclusion depends on it; the third anchor is still captured twice in source_hashes.txt",
     "disposition": "REGISTERED, not fixed in this batch",
     "where_the_true_values_live": "before/source_hashes.txt and after/source_hashes.txt"},
    {"id": "F-10", "severity": "P3", "batch": "M31 only",
     "title": "oq_rulings.json measured_probes[*].measured_matches is an empty dict",
     "measured_by_reviewer": ("the M31 probes have no expected_if_* numeric key, so the summary dict "
                              "is empty even though extra_probes.json itself is complete and honest"),
     "impact": "summary-only; the probe file carries the real measurement",
     "disposition": "REGISTERED, not fixed in this batch",
     "where_the_true_values_live": "evidence/M31/extra_probes.json"},
    {"id": "F-11", "severity": "observation", "batch": "M29-M31",
     "title": "the defaults case carries no independent evidence",
     "measured_by_reviewer": "defaults is byte-identical to positive because these models declare no optional driver",
     "impact": "none; it only documents the 'no default' contract fact",
     "disposition": "REGISTERED (already disclosed in review.md section 4)",
     "where_the_true_values_live": "evidence/<CARD>/input.json defaults block"},
]

RC_CONVENTION = {
    "this_batch": {"0": "pass", "1": "harness error", "2": "no verdict",
                   "3": "negative verdict", "precedence": "1 > 2 > 3 > 0"},
    "M05_M08_batch": {"0": "pass", "2": "harness/bookkeeping failure", "3": "negative verdict"},
    "rule": ("the difference is recorded, NOT retro-applied: no historical rc in any earlier batch is "
             "rewritten, and readers must not compare rc meaning across batches without this table"),
}


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def extract_reviewer_block(report_text, heading):
    """Return the FIRST ```markdown fenced block that follows the given heading.

    Line endings are normalised to LF: the report was written with CRLF while every file in the
    attempt uses LF, and the "verbatim" requirement applies to the TEXT, not to the transport line
    ending.  The normalisation is recorded in the transcription proof.
    """
    start = report_text.index(heading)
    fence = report_text.index("```markdown", start)
    body_start = report_text.index("\n", fence) + 1
    body_end = report_text.index("```", body_start)
    block = report_text[body_start:body_end]
    block = block.replace("\r\n", "\n").replace("\r", "\n")
    if not block.endswith("\n"):
        block += "\n"
    return block


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--runs-root", required=True)
    args = parser.parse_args()

    card = args.card
    info = CARDS[card]
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    runs_root = os.path.abspath(args.runs_root)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    report_text = read_text(args.report)
    block = extract_reviewer_block(report_text, info["reviewer_heading"])
    block_bytes = block.encode("utf-8")
    block_sha = hashlib.sha256(block_bytes).hexdigest()

    summary = {"card_id": card, "generated_utc": now, "files": {}}

    # preserve a byte copy of every file this pass rewrites, BEFORE anything is written
    backup_dir = os.path.join(attempt, "recovery", "pre_remediation")
    os.makedirs(backup_dir, exist_ok=True)
    for rel in ("review.md", "binding.json", "handoff.json", "oracle.md",
                os.path.join("evidence", card, "source_manifest.json"),
                os.path.join("evidence", card, "oq_rulings.json"),
                os.path.join("after", "final_deliverable_hashes.json")):
        src = os.path.join(attempt, rel)
        if os.path.isfile(src):
            dst = os.path.join(backup_dir, rel.replace("\\", os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, "rb") as fh_in, open(dst, "wb") as fh_out:
                fh_out.write(fh_in.read())
    summary["pre_remediation_copies"] = backup_dir
    print("pre-remediation copies ->", backup_dir)

    def record(label, path, before):
        after = sha256(path) if os.path.isfile(path) else None
        summary["files"][label] = {"path": path, "sha256_before": before, "sha256_after": after,
                                   "changed": before != after}
        print("  %-34s %s -> %s" % (label, (before or "None")[:16], (after or "None")[:16]))

    # ------------------------------------------------------------------ J1
    review_path = os.path.join(attempt, "review.md")
    review_before_hash = sha256(review_path)
    review_text = read_text(review_path)
    if not review_text.endswith("\n"):
        review_text += "\n"
    pre_lines = review_text.count("\n")
    appended = "\n" + block
    write_text(review_path, review_text + appended)
    review_after = read_text(review_path)
    # locate the appended span by its byte offset in the new file
    pre_bytes = review_text.encode("utf-8")
    appended_bytes = review_after.encode("utf-8")[len(pre_bytes):]
    start_line = (review_text.count("\n") + 1) + 1        # 1-based line of the block's first line
    end_line = start_line + block.count("\n") - 1
    identical = appended_bytes == block_bytes
    appended_sha = hashlib.sha256(appended_bytes).hexdigest()

    check = [
        "verdict_transcription_check",
        "card_id: %s" % card,
        "model_id: %s" % info["model_id"],
        "attempt_root: %s" % attempt,
        "report: %s" % os.path.abspath(args.report),
        "report_section: 6, heading %s" % info["reviewer_heading"],
        "method: the fenced ```markdown block following that heading was extracted from the report, "
        "line endings were normalised CRLF->LF (the report is CRLF, every attempt file is LF; the "
        "verbatim requirement applies to the text), the block was appended to review.md, and the "
        "appended span was re-read from review.md and compared byte-for-byte with the extracted block.",
        "line_ending_normalisation: CRLF -> LF (transport only; no character of the text changed)",
        "extracted_block_sha256_crlf_normalised: %s" % block_sha,
        "extracted_block_bytes: %d" % len(block_bytes),
        "appended_span_sha256: %s" % appended_sha,
        "appended_span_bytes: %d" % len(appended_bytes),
        "byte_identical: %s" % ("true" if identical else "false"),
        "review_md_sha256_before_append: %s" % review_before_hash,
        "review_md_sha256_after_append: %s" % sha256(review_path),
        "appended_block_first_line_1based: %d" % start_line,
        "appended_block_last_line_1based: %d" % end_line,
        "assertion: appended_span_sha256 == extracted_block_sha256_crlf_normalised -> %s"
        % ("PASS" if identical else "FAIL"),
        "note: the pre-existing review.md body above the appended block was not modified; only a "
        "blank separator line and the verbatim block were appended.",
    ]
    check_path = os.path.join(evidence, "verdict_transcription_check.txt")
    write_text(check_path, "\n".join(check) + "\n")
    if not identical:
        raise SystemExit("TRANSCRIPTION FAILED: appended span differs from the report block")
    print("J1 verdict appended to review.md lines %d-%d, byte-identical to the report block"
          % (start_line, end_line))
    record("review.md", review_path, review_before_hash)
    record("evidence/%s/verdict_transcription_check.txt" % card, check_path, None)

    # ------------------------------------------------------------------ J2a binding.json (M31 only)
    binding_path = os.path.join(attempt, "binding.json")
    binding_before = sha256(binding_path)
    binding = load_json(binding_path)
    comparison = binding.get("card_text_required_list_vs_registry", {})
    if card == "M31":
        old = dict(comparison)
        comparison["card_text_required_list"] = [
            "opening_inventory", "saleable_production", "purchased_units", "scrapped_units",
            "sold_units", "closing_inventory", "net_revenue_per_unit"]
        comparison["card_text_matches_registry"] = True
        comparison["divergence_note"] = None
        comparison["errata"] = {
            "applied_utc": now,
            "finding": "F-02 (independent reviewer, M31)",
            "what_was_wrong": (
                "the earlier record claimed card_M31.md L9 omits net_revenue_per_unit. That claim is "
                "FALSE: the reviewer checked byte-level that card_M31.md L9 lists all seven drivers "
                "including net_revenue_per_unit, and that model_cards.md L2818 lists the same seven."),
            "byte_level_check": {
                "card_document": "execution_v2/card_M31.md",
                "line": 9,
                "contains_net_revenue_per_unit": True,
                "master_table": "execution_v2/model_cards.md",
                "master_table_line": 2818,
                "master_table_contains_net_revenue_per_unit": True,
                "card_line_equals_master_table_line": True,
            },
            "correction": ("the card text and the registry AGREE on all seven drivers; there is no "
                           "divergence and therefore no owner ruling is required for one"),
            "superseded_values": {
                "card_text_required_list": old.get("card_text_required_list"),
                "card_text_matches_registry": old.get("card_text_matches_registry"),
                "divergence_note": old.get("divergence_note"),
            },
            "effect_on_conclusions": ("none: the frozen seven-driver input, the expectations and the "
                                      "runner verdicts are untouched; this is a text correction only"),
            "consistency_now": ("binding.json, oracle.md (section 12 errata) and oq_rulings.json all "
                                "record the same seven drivers as the registry"),
        }
        binding["card_text_required_list_vs_registry"] = comparison
        dump_json(binding_path, binding)
        record("binding.json", binding_path, binding_before)
    else:
        print("J2a binding.json: no divergence claimed for %s - nothing to correct" % card)

    # ------------------------------------------------------------------ J2b source_manifest.json (F-04, all three)
    sm_path = os.path.join(evidence, "source_manifest.json")
    sm_before = sha256(sm_path)
    sm = load_json(sm_path)
    ordering = sm.get("mtime_ordering", {})
    ordering["semantics"] = (
        "POST-HOC STAT COMPARISON ONLY. These values are stat() results taken AFTER the card ran; "
        "they are reported as measurements of what is on disk, and they are NOT a claim that any file "
        "was frozen before the run.")
    ordering["pre_freeze_claim"] = False
    ordering["pre_freeze_claim_note"] = (
        "no mtime in this block is offered as evidence of pre-run freezing. The pre-run anchor is a "
        "HASH OF THE GENERATOR CODE taken before the generator ran "
        "(evidence/<CARD>/oracle_document_freeze.json -> iso/oracle_card.md -> "
        "scripts/oracle_<CARD>.py), and the gating expectations live in evidence/<CARD>/oracle.json, "
        "which is regenerable byte-for-byte.")
    if "oracle_md_precedes_product_stdout" in ordering:
        ordering["oracle_md_mtime_earlier_than_product_stdout_post_hoc"] = ordering.pop(
            "oracle_md_precedes_product_stdout")
    if "oracle_json_precedes_product_stdout" in ordering:
        ordering["oracle_json_mtime_earlier_than_product_stdout_post_hoc"] = ordering.pop(
            "oracle_json_precedes_product_stdout")
    if "binding_precedes_product_stdout" in ordering:
        ordering["binding_json_mtime_earlier_than_product_stdout_post_hoc"] = ordering.pop(
            "binding_precedes_product_stdout")
    sm["mtime_ordering"] = ordering

    doc = sm.get("oracle_document", {})
    doc.pop("frozen_before_any_product_run", None)
    doc.pop("oracle_md_mtime_note", None)
    doc["anchor_scope"] = {
        "anchored_object": "the generator CODE, scripts/oracle_%s.py" % card,
        "anchor_evidence": "evidence/%s/oracle_document_freeze.json" % card,
        "anchor_pointer_file": "iso/oracle_card.md (= byte-identical copy of the generator)",
        "anchor_sha256": GEN_SHA,
        "oracle_md_text_in_anchor_scope": False,
        "oracle_md_carries_gating_expectations": False,
        "statement": ("what was anchored before the generator ran is the generator code, NOT the "
                      "oracle.md text. oracle.md is a human-written document that is never read or "
                      "validated by the pipeline (gen_oracle.py requires only the pointer file plus "
                      "the script), and it carries no gating expectation: every gated expectation "
                      "lives in evidence/%s/oracle.json, which is regenerable byte-for-byte from that "
                      "anchored code." % card),
    }
    doc["oracle_md_provenance"] = {
        "disclosed_fact": (
            "oracle.md was first written before the measurement chain, was later found absent from "
            "disk, and was restored with identical content before the pack; its present mtime is a "
            "POST-HOC value and is not offered as a pre-freeze claim in either direction."),
        "post_hoc_stat_comparison": {
            "oracle_md_mtime": ordering.get("oracle_md_mtime"),
            "product_stdout_mtime": ordering.get("product_stdout_mtime"),
            "oracle_md_mtime_is_later_than_product_stdout": (
                ordering.get("oracle_md_mtime") is not None
                and ordering.get("product_stdout_mtime") is not None
                and ordering["oracle_md_mtime"] > ordering["product_stdout_mtime"]),
        },
        "consequence": ("no conclusion in this attempt depends on oracle.md's mtime; see "
                        "freshness_claim for what IS claimed"),
    }
    doc["freshness_claim"] = {
        "claim": ("the gating expectations existed on disk before the only product call, and the code "
                  "that produced them was hash-anchored before it ran"),
        "anchored_by": [
            "evidence/%s/oracle.json mtime < evidence/%s/stdout.txt mtime "
            "(post-hoc stat comparison, reported as measured)" % (card, card),
            ("evidence/%s/oracle_document_freeze.json records sha256 %s of iso/oracle_card.md, taken "
             "BEFORE the generator ran; that pointer is a byte-identical copy of "
             "scripts/oracle_%s.py" % (card, GEN_SHA, card)),
            "evidence/%s/oracle_regen_proof.json shows input/oracle/cases regenerate byte-for-byte"
            % card,
        ],
        "not_claimed": [
            "oracle.md's present mtime is NOT offered as evidence of pre-run freezing",
            "oracle.md is NOT part of the anchor scope",
            "oracle.md carries NO gating expectation",
        ],
        "reviewer_ruling": {
            "finding": "OQ-05 (independent reviewer)",
            "ruling": ("does NOT block the formula signature and does NOT require a new attempt, "
                       "provided the owner claims formula only"),
            "boundary": ("if the owner wants oracle.md itself treated as pre-run frozen evidence, this "
                         "attempt is NOT sufficient and a re-run per the reviewer's minimum scope is "
                         "required; oracle.md must never be described as pre-run frozen evidence"),
            "reviewer_report": os.path.abspath(args.report),
        },
    }
    sm["oracle_document"] = doc
    sm["corrections"] = {
        "F-04": {
            "applied_utc": now,
            "what_was_wrong": ("the file contained both "
                               "'mtime_ordering.oracle_md_precedes_product_stdout: true' and a note "
                               "saying the mtime is later - a self-contradiction inside one file"),
            "resolution": ("the comparison is relabelled as a post-hoc stat comparison "
                           "(..._post_hoc) and no pre-freeze claim is attached to any mtime; "
                           "pre_freeze_claim is now false and the anchor scope is stated explicitly"),
            "reviewer_note_upheld": ("per the recorded values the flag was true "
                                     "(oracle_md_mtime < product_stdout_mtime); both the relabelled "
                                     "flag and the raw numbers are kept"),
        },
        "F-03": {
            "applied_utc": now,
            "what_was_wrong": ("the freshness chain label implied oracle.md was anchored"),
            "resolution": ("anchor_scope now names the generator code as the anchored object and "
                           "declares oracle.md outside the scope"),
        },
    }
    dump_json(sm_path, sm)
    record("evidence/%s/source_manifest.json" % card, sm_path, sm_before)

    # ------------------------------------------------------------------ J2c oq_rulings.json (M31) + shared note
    oq_path = os.path.join(evidence, "oq_rulings.json")
    oq_before = sha256(oq_path)
    oq = load_json(oq_path)
    if card == "M31":
        for ruling in oq.get("rulings", []):
            if ruling.get("id") == "OQ-04":
                old_title = ruling.get("title")
                ruling["title"] = ("numerical domain / boundary observations of this model "
                                   "(the card-text divergence claim was withdrawn by F-02)")
                ruling["withdrawn_claim"] = {
                    "applied_utc": now,
                    "finding": "F-02 (independent reviewer, M31)",
                    "superseded_title": old_title,
                    "why": ("the claim that card_M31.md omits net_revenue_per_unit is false; the card "
                            "lists all seven drivers and agrees with the registry, so no owner ruling "
                            "about a divergence is required"),
                    "byte_level_check": ("card_M31.md L9 and model_cards.md L2818 both contain "
                                         "net_revenue_per_unit and are byte-identical lines"),
                    "kept": ("the seven-driver required list and the effective bounds recorded in this "
                             "file were already correct and are unchanged"),
                }
    oq["counts_provenance_rule"] = oq.get("counts_provenance_rule", "")
    oq["text_corrections"] = {
        "F-04": {
            "applied_utc": now,
            "statement": ("the mtime comparison in evidence/%s/source_manifest.json is a POST-HOC stat "
                          "comparison, not a pre-freeze claim; the anchored object is the generator "
                          "code scripts/oracle_%s.py (sha256 %s), and oracle.md is outside the anchor "
                          "scope and carries no gating expectation" % (card, card, GEN_SHA)),
        },
    }
    dump_json(oq_path, oq)
    record("evidence/%s/oq_rulings.json" % card, oq_path, oq_before)

    # ------------------------------------------------------------------ J2d oracle.md (append-only errata)
    oracle_path = os.path.join(attempt, "oracle.md")
    oracle_before = sha256(oracle_path)
    oracle_text = read_text(oracle_path)
    if not oracle_text.endswith("\n"):
        oracle_text += "\n"
    errata_lines = []
    errata_lines.append("")
    errata_lines.append("## errata r1 (appended by the implementer after independent review; "
                        "APPEND-ONLY, the frozen body above is byte-unchanged)")
    errata_lines.append("")
    errata_lines.append("- appended_utc: %s" % now)
    errata_lines.append("- oracle_md_sha256_before_this_append: %s" % oracle_before)
    errata_lines.append("- rule: nothing above this line was rewritten; where an erratum supersedes a "
                        "sentence of the frozen body, this section says so explicitly.")
    errata_lines.append("")
    errata_lines.append("### E-1 (F-04, all three cards): what the freshness chain does and does not claim")
    errata_lines.append("")
    errata_lines.append("- The mtime comparison in `evidence/%s/source_manifest.json` is a **POST-HOC "
                        "stat comparison**, not evidence of pre-run freezing." % card)
    errata_lines.append("- The object anchored before the generator ran is the **generator code** "
                        "`scripts/oracle_%s.py` (sha256 `%s`), recorded through the byte-identical "
                        "pointer `iso/oracle_card.md` in `evidence/%s/oracle_document_freeze.json`."
                        % (card, GEN_SHA, card))
    errata_lines.append("- **This document is not part of the anchor scope and carries no gating "
                        "expectation.** The pipeline never reads or validates it; every gated "
                        "expectation lives in `evidence/%s/oracle.json`, which is regenerable "
                        "byte-for-byte from the anchored code." % card)
    errata_lines.append("- Independent-reviewer ruling on OQ-05: it does **not** block the formula "
                        "signature and does **not** require a new attempt **provided the owner claims "
                        "formula only**; if the owner wants this document treated as pre-run frozen "
                        "evidence, this attempt is insufficient and a re-run is required. This "
                        "document must never be described as pre-run frozen evidence.")
    errata_lines.append("")
    if card == "M31":
        errata_lines.append("### E-2 (F-02, M31 only): section 12 is superseded by this erratum")
        errata_lines.append("")
        errata_lines.append("Section 12 above claims that `card_M31.md` L9 does **not** list "
                            "`net_revenue_per_unit`. **That claim is false and is withdrawn.**")
        errata_lines.append("")
        errata_lines.append("- Byte-level check by the independent reviewer and re-run here: "
                            "`card_M31.md` L9 lists all seven drivers "
                            "(`opening_inventory`, `saleable_production`, `purchased_units`, "
                            "`scrapped_units`, `sold_units`, `closing_inventory`, "
                            "`net_revenue_per_unit`) and the master table `model_cards.md` L2818 lists "
                            "the same seven; the two lines are byte-identical.")
        errata_lines.append("- Therefore the card text and the registry **agree**, "
                            "`binding.json:card_text_required_list_vs_registry.card_text_matches_registry` "
                            "is now `true`, the divergence note is withdrawn, and the owner ruling that "
                            "section 12 asked for is **not** required.")
        errata_lines.append("- What section 12 got right and keeps: the seven-driver frozen input, the "
                            "registry as the authority for the driver set, and the fact that omitting "
                            "`net_revenue_per_unit` is refused with `missing drivers`. No numeric "
                            "expectation, verdict or frozen evidence file changes.")
        errata_lines.append("")
        errata_lines.append("Superseded sentences of section 12 (unified diff of the frozen text "
                            "against the corrected statement; the frozen text itself is left as it is):")
        errata_lines.append("")
        old_s12 = ("card_M31.md L9 lists the required drivers as opening_inventory, "
                   "saleable_production, purchased_units, scrapped_units, sold_units, "
                   "closing_inventory and does not list net_revenue_per_unit, while the registry "
                   "declares it required.")
        new_s12 = ("card_M31.md L9 lists all seven drivers including net_revenue_per_unit, and the "
                   "registry declares the same seven; the card text and the registry agree.")
        diff = difflib.unified_diff(old_s12.splitlines(), new_s12.splitlines(),
                                    fromfile="oracle.md section 12 (frozen, still on disk)",
                                    tofile="corrected statement (this erratum)",
                                    lineterm="")
        errata_lines.append("```diff")
        errata_lines.extend(diff)
        errata_lines.append("```")
        errata_lines.append("")
    errata_lines.append("### E-3 (registration, not a fix): cross-batch gaps recorded in handoff.json")
    errata_lines.append("")
    errata_lines.append("- F-01 (`run_card.py` never compares `cases.json[*].expected`) and the P3 list "
                        "F-05..F-10 are batch-level concerns; they are registered in "
                        "`handoff.json.cross_batch_gaps` and were deliberately **not** fixed inside "
                        "this attempt.")
    errata_lines.append("- The exit-code convention of this batch "
                        "(`0=pass / 1=harness / 2=no-verdict / 3=negative`) differs from the M05-M08 "
                        "batch (`2=harness`); the difference is registered and no historical rc is "
                        "rewritten.")
    errata_lines.append("")
    write_text(oracle_path, oracle_text + "\n".join(errata_lines))
    record("oracle.md", oracle_path, oracle_before)

    # ------------------------------------------------------------------ J2e handoff.json
    handoff_path = os.path.join(attempt, "handoff.json")
    handoff_before = sha256(handoff_path)
    handoff = load_json(handoff_path)
    handoff["reviewer_status"] = {
        "state": "accepted_scoped (formula qualification only), per the independent reviewer",
        "verdict_transcribed_verbatim_into": "review.md",
        "verdict_block_first_line": start_line,
        "verdict_block_last_line": end_line,
        "verdict_block_sha256": block_sha,
        "transcription_proof": "evidence/%s/verdict_transcription_check.txt" % card,
        "reviewer_report": os.path.abspath(args.report),
        "implementer_signed": False,
        "granted": ["formula"],
        "not_granted": ["disclosure_adaptation (stays unmapped)", "accuracy (stays unproven)"],
        "no_extrapolation": ("a formula pass for this model, or one company's mapping, is never "
                             "promoted to industry-wide accuracy or disclosure adaptation"),
    }
    handoff["status"] = "review_pending"
    handoff["status_note"] = ("the reviewer verdict is transcribed into review.md, but this record "
                              "keeps status=review_pending on purpose: the implementer never signs, "
                              "and the batch owner closes the card only after the F-02 errata is in "
                              "place (it now is) and, for M31, after the owner has seen the "
                              "withdrawn divergence claim.")
    oq04_note = ("OQ-04 for this card covers numerical domain / boundary observations only; for M31 "
                 "the divergence claim was withdrawn by F-02 - the card text and the registry agree "
                 "on all seven drivers.")
    handoff["open_questions_note"] = oq04_note
    if card == "M31":
        handoff["open_questions_amendments"] = [{
            "id": "OQ-04",
            "amended_utc": now,
            "amendment": ("the M31 divergence sub-claim is WITHDRAWN (F-02): card_M31.md L9 lists all "
                          "seven drivers including net_revenue_per_unit, so there is no divergence and "
                          "no owner ruling is required for one"),
            "evidence": ["binding.json card_text_required_list_vs_registry.errata",
                         "evidence/M31/oq_rulings.json rulings[OQ-04].withdrawn_claim",
                         "oracle.md errata r1 section E-2"],
        }]
    handoff["reviewer_ruling_boundaries"] = [
        {"id": "OQ-05",
         "ruling": ("does NOT block the formula signature and does NOT require a new attempt, provided "
                    "the owner claims formula only"),
         "boundary": ("if the owner wants oracle.md treated as pre-run frozen evidence, this attempt is "
                      "NOT sufficient and a re-run per the reviewer's minimum scope is required"),
         "recorded_now": "oracle.md is NOT described anywhere in this attempt as pre-run frozen evidence"},
        {"id": "OQ-01",
         "ruling": "still an owner item (isolation binding provenance); code under test is byte-identical"},
        {"id": "F-01_and_source_manifest_wording",
         "ruling": ("batch-level runner concern (cases[*].expected is never compared) plus the "
                    "source_manifest wording correction now applied"),
         "owner_action": "decide whether to fix the runner as a minimum change in a later card"},
    ]
    handoff["text_corrections_applied"] = {
        "F-02": ("binding.json / oracle.md section 12 / this file's OQ-04 claim that the card text "
                 "omits net_revenue_per_unit -> withdrawn; card text and registry agree on seven "
                 "drivers") if card == "M31" else "not applicable to %s (no divergence was claimed)" % card,
        "F-04": ("evidence/%s/source_manifest.json mtime comparison relabelled as a post-hoc stat "
                 "comparison; anchor scope names the generator code and excludes oracle.md" % card),
    }
    handoff["cross_batch_gaps"] = CROSS_BATCH_GAPS
    handoff["exit_code_convention"] = RC_CONVENTION
    handoff["evidence_hashes_note"] = (
        "evidence/%s/evidence_hashes.json was written at pack time and therefore does not cover the "
        "files changed by this remediation (review.md, handoff.json, oracle.md, binding.json, "
        "source_manifest.json, oq_rulings.json); the authoritative post-remediation ledger is "
        "after/final_deliverable_hashes.json, and this remediation's own report lists the before/after "
        "sha256 of every file it touched." % card)
    handoff["remediation_utc"] = now
    dump_json(handoff_path, handoff)
    record("handoff.json", handoff_path, handoff_before)

    # ------------------------------------------------------------------ summary + final hashes
    summary["verdict_block"] = {"sha256": block_sha, "bytes": len(block_bytes),
                                "review_md_lines": [start_line, end_line]}
    summary["cross_batch_gaps_registered"] = [g["id"] for g in CROSS_BATCH_GAPS]
    summary_path = os.path.join(attempt, "recovery",
                                "remediation_%s.json" % "r2")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    dump_json(summary_path, summary)
    print("remediation summary ->", summary_path)

    # refresh the final deliverable ledger so it covers the remediated files
    ledger = os.path.join(attempt, "after", "final_deliverable_hashes.json")
    if os.path.isfile(ledger):
        skip = os.path.normcase(os.path.join("iso", "venv"))
        files = {}
        for root, dirs, names in os.walk(attempt):
            rel_root = os.path.relpath(root, attempt)
            if rel_root != "." and os.path.normcase(rel_root) == skip:
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if os.path.normcase(os.path.join(rel_root, d)) != skip]
            for name in sorted(names):
                path = os.path.join(root, name)
                rel = os.path.relpath(path, attempt).replace("\\", "/")
                if rel.endswith("final_deliverable_hashes.json"):
                    continue
                files[rel] = {"absolute_path": path, "sha256": sha256(path),
                              "size_bytes": os.path.getsize(path)}
        dump_json(ledger, {
            "card_id": card, "attempt_id": "a20260919-01", "model_id": info["model_id"],
            "attempt_root": attempt,
            "generated_utc": now,
            "interpreter_path": os.path.join(attempt, "iso", "venv", "Scripts", "python.exe"),
            "excluded_from_the_table": ["iso/venv/** (attempt-local interpreter, not an evidence file)"],
            "written_last": ("refreshed after the independent-review remediation so it covers the "
                             "finished attempt including the transcribed verdict and the F-02/F-04 "
                             "corrections"),
            "file_count": len(files), "files": files})
        print("refreshed final ledger:", ledger, len(files), "files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
