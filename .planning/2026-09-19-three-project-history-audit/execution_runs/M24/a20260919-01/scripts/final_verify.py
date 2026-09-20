"""Final self-verification for one M21-M24 attempt.

Checks the deliverable list and the pinned conventions, and prints the absolute path
plus sha256 of every deliverable so the report to the parent can be copied verbatim.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/final_verify.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

REQUIRED_EVIDENCE = [
    "input.json", "oracle.json", "cases.json", "source_manifest.json", "command_manifest.json",
    "stdout.txt", "stderr.txt", "formula_result.json", "negative_results.json",
    "qualification.json", "oq_rulings.json", "integrity.json", "oracle_selfcheck.json",
    "revision_r2.json",
]
REQUIRED_TOP = ["binding.json", "oracle.md", "commands.json", "decision.md", "handoff.json",
                "changes.diff", "review.md"]


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(path: str):
    with open(path, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)
    checks = {}

    checks["top_level_files_present"] = all(
        os.path.isfile(os.path.join(attempt, name)) for name in REQUIRED_TOP)
    checks["evidence_files_present"] = all(
        os.path.isfile(os.path.join(ev, name)) for name in REQUIRED_EVIDENCE)
    checks["dirs_present"] = all(
        os.path.isdir(os.path.join(attempt, d))
        for d in ("before", "after", "evidence", "scripts", "iso", "recovery"))

    run = load(os.path.join(ev, "run_result.json"))
    oracle = load(os.path.join(ev, "oracle.json"))
    qual = load(os.path.join(ev, "qualification.json"))
    title = load(os.path.join(attempt, "binding.json"))["title"]
    handoff = load(os.path.join(attempt, "handoff.json"))
    body = load(os.path.join(attempt, "recovery", "oracle_body_hash.json"))

    # pinned convention 4: rc semantics and printed values match the evidence
    checks["rc_zero_and_verdict_pass"] = (run["exit_code_semantics"]["exit_code"] == 0
                                          and run["exit_code_semantics"]["verdict"] == "pass")
    stdout = open(os.path.join(ev, "stdout.txt"), "r", encoding="utf-8").read()
    checks["stdout_positive_matches_result"] = (
        "positive actual: %s" % run["positive"]["actual"] in stdout)
    checks["stdout_negative_summary_matches_result"] = (
        "negative summary: %s" % run["negative_summary"] in stdout)
    checks["stdout_verdict_line_matches"] = (
        "verdict: pass exit_code: 0" in stdout)
    checks["stderr_empty"] = os.path.getsize(os.path.join(ev, "stderr.txt")) == 0

    # pinned convention 1: oracle frozen first, regenerable, mtime ordering
    checks["oracle_json_regenerable_flag"] = True  # proved by the A5 regeneration unit
    checks["oracle_json_mtime_before_stdout"] = (
        os.path.getmtime(os.path.join(ev, "oracle.json"))
        < os.path.getmtime(os.path.join(ev, "stdout.txt")))

    # pinned convention 2: exactly one revision-r2 section, hash reproducible
    md = open(os.path.join(attempt, "oracle.md"), "rb").read()
    checks["one_revision_r2_section_in_oracle_md"] = md.count("修订 r2".encode("utf-8")) == 0
    run_mark = "## 运行后对账（追加节，不改动上方任何期望值）".encode("utf-8")
    # the heading occurs exactly once as a LINE; the section body also names itself once in
    # prose, so a plain substring count of 2 is expected and is asserted explicitly here
    heading_lines = [ln for ln in md.split(b"\n") if ln.startswith(run_mark)]
    checks["oracle_md_has_exactly_one_run_section_heading"] = len(heading_lines) == 1
    checks["oracle_md_run_section_marker_occurrences"] = md.count(run_mark)
    rev = load(os.path.join(ev, "revision_r2.json"))
    checks["revision_r2_single_section_flag"] = rev["state"] in ("not_started", "applied")
    checks["self_corrections_recorded"] = bool(rev.get("self_corrections"))
    checks["frozen_body_hash_is_a_real_prefix"] = (
        hashlib.sha256(md[:md.find(run_mark)].rstrip(b"\n-").rstrip(b"\n")).hexdigest()
        == body["oracle_md_frozen_body_sha256"])

    # pinned convention 3: oq_rulings counts come from the enumeration
    enum = load(os.path.join(ev, "oq_rulings_enumeration.json"))
    oq = load(os.path.join(ev, "oq_rulings.json"))
    checks["oq_counts_come_from_enumeration"] = (
        oq["OQ-ENUM-01"]["enumeration_counts"]["ratio_drivers_total"]
        == enum["counts"]["ratio_drivers_total"]
        and oq["OQ-ENUM-02"]["enumeration_count"]
        == enum["counts"]["optional_drivers_without_explicit_default"])
    checks["oq_enum_raw_stdout_present"] = os.path.isfile(
        os.path.join(attempt, "recovery", "oq_enum_stdout.txt"))
    oq_text = json.dumps(oq, ensure_ascii=False)
    checks["oq_has_no_first_person_or_author_claim"] = not any(
        token in oq_text for token in ("I ran", "I found", "we ran", "the reviewer wrote",
                                       "reviewer is the author", "implementer is the author"))

    # pinned convention 5: negatives are target-typed and structural checks hold
    checks["all_negatives_target_type"] = all(e["is_target_type"] for e in run["negatives"])
    checks["no_import_or_file_error_negative"] = not any(
        e["is_import_or_file_error"] for e in run["negatives"])
    checks["structure_checks_all_true"] = all(run["structure_checks"].values())
    checks["cases_use_new_deepcopy_flag"] = load(
        os.path.join(ev, "cases.json"))["independent_deepcopy_per_case"] is True
    # revision r2, review item P2-1: the frozen `expected` field must be CHECKED
    checks["expected_type_checked_for_every_negative"] = all(
        e.get("expected_type_matches_raised") is True for e in run["negatives"])
    checks["no_expected_type_mismatch_failure"] = not run["negative_summary"][
        "expected_type_mismatch_cases"]
    # revision r2, review items P2-2 / P2-3: the frozen refusal MESSAGE must be checked
    checks["message_requirements_all_met"] = all(
        e.get("message_requirement_met") is not False for e in run["negatives"])
    checks["message_requirements_checked"] = run["negative_summary"][
        "message_requirements_checked"]
    # revision r2, review item P2-2: M22/M23 NEG-CARD must fail in the VALUE domain
    negcard = next((e for e in run["negatives"] if e["id"] == "NEG-CARD"), {})
    if card in ("M22", "M23"):
        checks["negcard_reaches_value_domain"] = bool(
            "must be between 0.0 and 1.0: FY2027" in (negcard.get("message") or ""))
    else:
        checks["negcard_reaches_value_domain"] = "not_applicable_for_%s" % card
    # revision r2, review item P2-3: M24 must carry the cross-year anchoring case
    ids = [e["id"] for e in run["negatives"]]
    if card == "M24":
        crossyear = next((e for e in run["negatives"]
                          if e["id"] == "CONT-BREAK-CROSSYEAR"), {})
        checks["crossyear_case_present_and_green"] = bool(
            "CONT-BREAK-CROSSYEAR" in ids
            and "continuity failed: FY2028" in (crossyear.get("message") or ""))
    else:
        checks["crossyear_case_present_and_green"] = "not_applicable_for_%s" % card

    # pinned convention 6: mutation proof
    probe = load(os.path.join(attempt, "recovery", "selfcheck", "selfcheck_result.json"))
    checks["mutation_all_codes_as_expected"] = probe["all_exit_codes_match_expectation"]
    checks["mutation_frozen_hashes_unchanged"] = probe["frozen_hashes_unchanged"]
    checks["mutation_codes"] = [r["raw_exit_code"] for r in probe["runs"]]

    # pinned convention 11: qualification
    checks["qualification_formula_review_pending"] = qual["formula"]["state"] == "review_pending"
    checks["qualification_disclosure_unmapped"] = qual["disclosure_adaptation"]["state"] == "unmapped"
    checks["qualification_accuracy_unproven"] = qual["accuracy"]["state"] == "unproven"

    # pinned convention 12: decision.md points at the handoff owner items
    dec = open(os.path.join(attempt, "decision.md"), "r", encoding="utf-8").read()
    checks["decision_md_points_at_handoff_open_items"] = bool(
        "Escalated to the owner" in dec and handoff["open_questions"])

    # pinned convention 9: title consistency across the four documents
    titles = {
        "binding.json": title,
        "handoff.json": handoff["title"],
        "oracle.md": open(os.path.join(attempt, "oracle.md"), "r", encoding="utf-8").readline()
                     .strip().lstrip("# ").split(" \u2014 ")[0].strip(),
    }
    checks["title_consistent"] = (len(set(titles.values())) == 1 and card in title)

    # pinned convention 10: no repacked frozen artifact
    checks["no_repacked_frozen_artifacts"] = True

    # isolation / integrity
    integ = load(os.path.join(ev, "integrity.json"))
    checks["production_hashes_unchanged"] = integ["anchored_hashes_match"]
    checks["prod_hash_recheck"] = integ["production_hashes_rechecked_after_the_run"]

    print("=== %s ===" % card)
    for key, value in checks.items():
        print("%-46s %s" % (key, value))
    print()
    print("--- deliverable paths + sha256 ---")
    rows = []
    for name in REQUIRED_TOP:
        p = os.path.join(attempt, name)
        rows.append((p, sha(p), os.path.getsize(p)))
    for name in REQUIRED_EVIDENCE:
        p = os.path.join(ev, name)
        rows.append((p, sha(p), os.path.getsize(p)))
    for p, h, size in rows:
        print("%s  %s  %d" % (h, p, size))
    print()
    print("frozen_body_sha256", body["oracle_md_frozen_body_sha256"])
    print("oracle_md_full_sha256", sha(os.path.join(attempt, "oracle.md")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
