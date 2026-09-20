"""Verify the independent-review remediation of one M29/M30/M31 attempt, then print a fact sheet.

Read-only.  Every assertion below is recomputed from the files on disk:

  V1 the appended verdict block in review.md is byte-identical to the block extracted from the report
  V2 handoff.json points at exactly that line range
  V3 (M31) binding.json now records seven card-text drivers and card_text_matches_registry = true,
     with the withdrawn values preserved
  V4 source_manifest.json carries the post-hoc semantics and the explicit anchor scope
  V5 oracle.md's errata section records the pre-append hash it was appended to
  V6 the cross-batch gap table is present with F-01 and F-05..F-11

Usage:
  python -X utf8 -B verify_remediation.py --card M29 --attempt-root <attempt> --report <REPORT.md>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

CARDS = {"M29": ("commercial_launch", "### M29 · commercial_launch"),
         "M30": ("finite_adoption", "### M30 · finite_adoption"),
         "M31": ("inventory_sellthrough", "### M31 · inventory_sellthrough")}


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    card = args.card
    model_id, heading = CARDS[card]
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    failures = []

    def check(name, condition, detail):
        print("%-6s %s -- %s" % ("PASS" if condition else "FAIL", name, detail))
        if not condition:
            failures.append(name)

    # -- V1
    report = open(args.report, "r", encoding="utf-8", newline="").read()
    start = report.index(heading)
    fence = report.index("```markdown", start)
    body_start = report.index("\n", fence) + 1
    body_end = report.index("```", body_start)
    block = report[body_start:body_end].replace("\r\n", "\n").replace("\r", "\n")
    if not block.endswith("\n"):
        block += "\n"
    check_file = os.path.join(evidence, "verdict_transcription_check.txt")
    fields = {}
    for line in open(check_file, "r", encoding="utf-8").read().splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            fields[key.strip()] = value.strip()
    first = int(fields["appended_block_first_line_1based"])
    last = int(fields["appended_block_last_line_1based"])
    review_lines = open(os.path.join(attempt, "review.md"), "r", encoding="utf-8").read().splitlines()
    span = "\n".join(review_lines[first - 1:last]) + "\n"
    check("V1", span == block,
          "review.md lines %d-%d == report block (sha %s)"
          % (first, last, hashlib.sha256(span.encode("utf-8")).hexdigest()[:16]))
    check("V1b", fields.get("assertion", "").endswith("PASS"),
          "transcription check file self-assertion: %s" % fields.get("assertion"))

    # -- V2
    handoff = json.load(open(os.path.join(attempt, "handoff.json"), "r", encoding="utf-8"))
    status = handoff.get("reviewer_status", {})
    check("V2", status.get("verdict_block_first_line") == first
          and status.get("verdict_block_last_line") == last,
          "handoff.reviewer_status lines %s-%s, state=%s"
          % (status.get("verdict_block_first_line"), status.get("verdict_block_last_line"),
             status.get("state")))
    check("V2b", handoff.get("status") == "review_pending" and status.get("implementer_signed") is False,
          "status=%s implementer_signed=%s" % (handoff.get("status"),
                                               status.get("implementer_signed")))

    # -- V3 (M31)
    binding = json.load(open(os.path.join(attempt, "binding.json"), "r", encoding="utf-8"))
    comparison = binding.get("card_text_required_list_vs_registry", {})
    if card == "M31":
        check("V3", comparison.get("card_text_matches_registry") is True
              and comparison.get("divergence_note") is None
              and len(comparison.get("card_text_required_list", [])) == 7,
              "card_text_matches_registry=%s drivers=%d divergence_note=%r"
              % (comparison.get("card_text_matches_registry"),
                 len(comparison.get("card_text_required_list", [])),
                 comparison.get("divergence_note")))
        errata = comparison.get("errata", {})
        check("V3b", errata.get("byte_level_check", {}).get("contains_net_revenue_per_unit") is True
              and "superseded_values" in errata,
              "byte-level check recorded + superseded values preserved")
    else:
        check("V3", comparison.get("card_text_matches_registry") is True,
              "card text agrees with the registry (nothing to correct)")

    # -- V4
    sm = json.load(open(os.path.join(evidence, "source_manifest.json"), "r", encoding="utf-8"))
    ordering = sm["mtime_ordering"]
    scope = sm["oracle_document"]["anchor_scope"]
    check("V4", ordering.get("pre_freeze_claim") is False
          and "oracle_md_precedes_product_stdout" not in ordering
          and "oracle_md_mtime_earlier_than_product_stdout_post_hoc" in ordering
          and scope.get("oracle_md_text_in_anchor_scope") is False
          and scope.get("oracle_md_carries_gating_expectations") is False,
          "post-hoc semantics: pre_freeze_claim=%s, labels=%s"
          % (ordering.get("pre_freeze_claim"),
             [k for k in ordering if "post_hoc" in k]))
    check("V4b", scope.get("anchored_object", "").endswith("oracle_%s.py" % card)
          and scope.get("anchor_sha256") ==
          "3177247f95f7554920ac43b4e076f28b5ef78250059c130de1f5e8dee2e4c09e",
          "anchored object = %s" % scope.get("anchored_object"))

    # -- V5
    oracle_text = open(os.path.join(attempt, "oracle.md"), "r", encoding="utf-8").read()
    marker = "- oracle_md_sha256_before_this_append: "
    recorded = oracle_text.split(marker, 1)[1].splitlines()[0].strip()
    backup = os.path.join(attempt, "recovery", "pre_remediation", "oracle.md")
    backup_hash = sha256(backup) if os.path.isfile(backup) else None
    # the errata section was appended to the frozen body that the pack had already read, so the
    # frozen body (everything before the blank line that introduces '## errata r1') must hash back
    # to the recorded pre-append value.
    body = oracle_text.split("\n## errata r1", 1)[0]
    if not body.endswith("\n"):
        body += "\n"
    body_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    body_matches_backup = False
    if backup_hash:
        body_matches_backup = body.encode("utf-8") == open(backup, "rb").read()
    check("V5", recorded == body_hash,
          "errata pre-append hash %s == frozen body sha %s" % (recorded[:16], body_hash[:16]))
    check("V5b", body_matches_backup,
          "frozen body above the errata is byte-identical to recovery/pre_remediation/oracle.md")
    headings = [line.strip() for line in oracle_text.splitlines() if line.startswith("## ")]
    errata_headings = [h for h in headings if h.startswith("## errata")]
    r2_headings = [h for h in headings if "revision r2" in h]
    check("V5c", len(errata_headings) == 1 and not r2_headings,
          "exactly one errata heading %r and no r2 heading (the string '## revision r2' does appear "
          "inside the frozen rule prose of section 10, which is not a heading)" % errata_headings)

    # -- V6
    gaps = [g["id"] for g in handoff.get("cross_batch_gaps", [])]
    check("V6", "F-01" in gaps and all(g in gaps for g in
                                       ("F-05", "F-06", "F-07", "F-08", "F-09", "F-10", "F-11")),
          "cross-batch gaps registered: %s" % gaps)
    ec = handoff.get("exit_code_convention", {})
    check("V6b", ec.get("this_batch", {}).get("2") == "no verdict"
          and ec.get("M05_M08_batch", {}).get("2") == "harness/bookkeeping failure",
          "exit-code convention difference registered (this batch 2=no-verdict, M05-M08 2=harness)")

    print()
    print("card %s remediation verification: %s (%d failures)"
          % (card, "ALL PASS" if not failures else "FAILURES: " + ",".join(failures), len(failures)))
    return 0 if not failures else 3


if __name__ == "__main__":
    raise SystemExit(main())
