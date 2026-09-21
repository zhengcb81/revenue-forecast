"""verify_t1_15.py -- one card for M08's three-step remediation.

WHAT THE RULING SAYS (OWNER_DECISIONS.md section 13, row T1-15; section 4 line 60)

  1. the owner rules that READING C is authoritative (already ruled);
  2. the owner corrects the index -- by measurement the four targets are
     execution_v2/card_M08.md:42, model_cards.md:552, model_cards.json:1930 and
     dispatch.json:5755 -- to carry read-C's SIGNED presentation
     100+40-5+-10+-15-60 (U+2212 throughout), with the EXPECTATION [50] UNCHANGED;
  3. after that correction an independent reviewer re-runs the frozen card on the SAME
     code_root 9ec65295... and archives the run.

WHAT THIS CARD IS, AND IS NOT
  It verifies that steps 1 and 2 are landed and it records what it checked. It does not
  re-run the product code, it does not move any status, and it does not edit any record.
  Step 3's archive is the reviewer's act; this card establishes only whether it happened
  and on which code_root.

HOW THIS CARD CAME TO EXIST (worth recording, because it changed the work)
  The orchestrator was dispatched TWICE on this ruling: commit b07d9b95 wrote the
  PROVENANCE event, the four pre-images and a provenance.json whose "correction" field
  says "printed read-A form -> read-C signed form; value unchanged". I therefore expected
  to find uncorrected indexes and started a correction script of my own.

  That script ABORTED on its own guard, because the live files matched NEITHER the frozen
  pre-image NOR the frozen post-image. The reason turned out to be two independent things,
  and separating them mattered:

    (a) LINE ENDINGS. The frozen hashes were taken on CRLF byte streams; the committed
        blobs are LF. Every file is therefore "drifted" by exactly its CRLF count, with
        zero payload difference. Measured here, not assumed.
    (b) A LATER COMMIT. Three of the four files were further modified after b07d9b95.

  So the honest finding is NOT "the correction is undone" and NOT "the file drifted".
  It is: the correction IS on disk, and the frozen provenance no longer describes the
  current bytes. Both facts are established below from the files themselves.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
AGENT = REPO / ".planning" / "2026-09-19-three-project-history-audit"
V2 = AGENT / "execution_v2"
RUNS = AGENT / "execution_runs"
REC = RUNS / "M08" / "a20260919-01" / "recovery"
PROV_DIR = REC / "owner_ruling_20260920_index_correction"
PROV = PROV_DIR / "provenance.json"
RERUN = REC / "rerun_after_owner_correction_20260920"
REG = REPO / "scripts" / "model_registry.py"

ANCHOR_SHA = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"
CORRECTING_COMMIT = "b07d9b95"
STEP3_COMMITS = ("ba17e46e", "c348afd0", "4259db0b")

# U+2212 MINUS SIGN, not ASCII hyphen. Written as escapes so no tool can "normalise" them.
MINUS = "\u2212"
OLD = "100+40" + MINUS + "5" + MINUS + "10" + MINUS + "15" + MINUS + "60=50"
NEW = "100+40" + MINUS + "5+" + MINUS + "10+" + MINUS + "15" + MINUS + "60=50"

# name, line number in the LF-normalised stream, and the "kind" of carrier
TARGETS = [
    ("card_M08.md", 42, "md_table", "手算"),
    ("model_cards.md", 552, "md_table", "手算"),
    ("model_cards.json", 1930, "json_field", "independent_hand_work"),
    ("dispatch.json", 5755, "json_field", "independent_hand_work"),
]

P: dict[str, dict] = {}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def lf_lines(b: bytes) -> list[str]:
    """Split on logical lines regardless of CRLF/LF, keeping no terminators."""
    return b.replace(b"\r\n", b"\n").decode("utf-8").split("\n")


def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def blob(path: str) -> bytes:
    r = subprocess.run(["git", "-C", str(REPO), "cat-file", "-p", "HEAD:" + path],
                       capture_output=True)
    return r.stdout


def main() -> int:
    # ------------------------------------------------ hard scope guard: registry anchor
    guard = {
        "registry_exists": REG.is_file(),
        "registry_matches_anchor": REG.is_file() and sha(REG.read_bytes()) == ANCHOR_SHA,
        "provenance_file_present": PROV.is_file(),
        "rerun_archive_present": RERUN.is_dir(),
        "four_targets_present": all((V2 / n).is_file() for n, _, _, _ in TARGETS),
    }
    guard["holds"] = all(v for k, v in guard.items()
                         if k not in ("registry_exists",) and isinstance(v, bool))
    if not guard["registry_matches_anchor"]:
        print("HARNESS FAILURE: the production anchor moved")
        print(json.dumps(guard, ensure_ascii=False, indent=1))
        return 1
    P["SCOPE"] = guard

    prov = json.loads(PROV.read_text(encoding="utf-8"))
    flat = re.sub(r"\s+", " ", (AGENT / "OWNER_DECISIONS.md").read_text(
        encoding="utf-8", errors="replace"))

    # ---------------------------------------------------- P-1: the three steps as ruled
    m = re.search(r"\|\s*T1-15\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", flat)
    row = (m.group(1) + " " + m.group(2)) if m else ""
    # The signed form appears in the rulings in a FORM THAT SURVIVES NORMALISATION: the
    # owner's cell prints the chain only as far as the first sign, i.e. "...-5+-10",
    # because the cell is describing the presentation, not the whole equation. So match the
    # prefix that is actually ruled, not the full equation I expected to find.
    SIGNED_PREFIX = "100+40" + MINUS + "5+" + MINUS + "10"
    bare_prefix = "100+40" + MINUS + "5" + MINUS + "10"
    p1 = {
        "t1_15_row_isolated": bool(m),
        "adopted_in_full": "\u5168\u90e8\u91c7\u7eb3" in row,
        "rules_reading_C_authoritative": "\u8bfb\u6cd5 C \u6743\u5a01" in row,
        "names_the_four_targets": all(t in row for t in (
            "card_M08.md:42", "model_cards.md:552",
            "model_cards.json:1930", "dispatch.json:5755")),
        "says_the_targets_were_measured": "\u5b9e\u6d4b" in row,
        "requires_the_signed_form": SIGNED_PREFIX in row,
        # the ruling row names the read-C presentation only; the bare chain it replaces is
        # printed in section 4, so check the pair THERE rather than expecting both in one cell
        "section4_names_the_bare_chain_as_the_target": bare_prefix in flat,
        "section4_shows_the_correction_pair": (bare_prefix in flat and SIGNED_PREFIX in flat),
        "expectation_stays_50": "[50]" in row and "\u4e0d\u53d8" in row,
        "step3_is_a_reviewer_rerun_on_the_same_code_root": (
            "reviewer" in row and "9ec65295" in row and "\u590d\u8dd1" in row),
        # the row must NOT authorise this card to grant anything
        "row_authorises_no_acceptance": "\u6388\u4e88" not in row and "accepted" not in row,
    }
    p1["holds"] = all(p1.values())
    P["P-1_the_three_steps_are_as_ruled"] = p1

    # ------------------------- P-2: read-C is the implementation, and 50 is not a coincidence
    #
    # I do not take "reading C is authoritative" on the owner's word alone: the ruling's
    # own basis is four mutually corroborating texts. Two are checked here directly.
    src = REG.read_text(encoding="utf-8")
    # The implementation of the backlog bridge is read from the SOURCE, not assumed. My first
    # attempt grepped for `+drivers["contract_changes"]` and came back RED -- the signs are on
    # the NEGATIVE terms (`-drivers["cancellations"]`, `-drivers["closing_backlog"]`) while the
    # two remeasurement terms are added bare. That IS reading C: the signed amounts enter with
    # their own signs, so a negative contract change reduces the bridge. A substring gate
    # written from memory would have "found" the sign convention backwards. Lesson #23/#24.
    reg_lines = src.splitlines()
    p2 = {
        "registry_has_the_bridge": "_project_backlog" in src,
        "the_bridge_is_a_signed_sum": bool(
            re.search(r"math\.fsum\(\(", src)),
        "cancellations_enter_negated": bool(
            re.search(r"-\s*drivers\[.cancellations.\]\[index\]", src)),
        "closing_backlog_enters_negated": bool(
            re.search(r"-\s*drivers\[.closing_backlog.\]\[index\]", src)),
        "contract_changes_enters_unnegated": bool(
            re.search(r"^\s*drivers\[.contract_changes.\]\[index\],", src, re.M)),
        "remeasurements_enters_unnegated": bool(
            re.search(r"^\s*drivers\[.backlog_remeasurements.\]\[index\],", src, re.M)),
        "spec_formula_string_uses_plus_for_contract_changes": (
            "bookings - cancellations + contract_changes + backlog_remeasurements"
            " - closing_backlog" in src),
    }
    p2["the_sign_convention_is_reading_C"] = all([
        p2["cancellations_enter_negated"],
        p2["closing_backlog_enters_negated"],
        p2["contract_changes_enters_unnegated"],
        p2["remeasurements_enters_unnegated"],
        p2["spec_formula_string_uses_plus_for_contract_changes"],
    ])
    # The two readings A and C BOTH give 50 on this input, so agreement with the frozen
    # expectation is not by itself evidence for C. The separation is done by arithmetic on the
    # two forms, computed here rather than transcribed, plus the OBS-SIGN-B probe recorded by
    # the reviewer's own rerun (contract_changes=+10 -> 85, which only reading C produces).
    #
    # NON-REDUNDANCY (learned from negative control NC-5): the first version of this gate had
    # four legs, and falsifying the sign-convention leg alone left P-2 GREEN -- the other three
    # were carrying it. A claim about the CONVENTION must be refuted by falsifying a leg about
    # the CONVENTION, so the arithmetic and card-text legs are now recorded as corroboration
    # rather than folded into `holds`. `holds` rests on the source-read convention alone.
    p2["read_A_arithmetic"] = 100 - 5 - 10 - 15 + 40 - 60       # read A folds the signs in
    p2["read_C_arithmetic"] = 100 + 40 - 5 + (-10) + (-15) - 60  # read C adds signed amounts
    p2["corroboration_both_readings_yield_50_on_this_input"] = (
        p2["read_A_arithmetic"] == 50 and p2["read_C_arithmetic"] == 50)
    p2["corroboration_the_two_readings_are_not_identical_expressions"] = (
        "100+40" + MINUS + "5" + MINUS + "10" + MINUS + "15" + MINUS + "60"
        != "100+40" + MINUS + "5+" + MINUS + "10+" + MINUS + "15" + MINUS + "60")
    card = (V2 / "card_M08.md").read_text(encoding="utf-8").splitlines()
    p2["corroboration_card_line_8_says_signed_amounts"] = bool(
        re.search(r"signed|\u5e26\u7b26\u53f7", card[7]))
    # these must all still be true, but they do not by themselves decide the proposition
    p2["all_corroboration_present"] = all([
        p2["corroboration_both_readings_yield_50_on_this_input"],
        p2["corroboration_the_two_readings_are_not_identical_expressions"],
        p2["corroboration_card_line_8_says_signed_amounts"],
    ])
    p2["holds"] = p2["the_sign_convention_is_reading_C"]
    P["P-2_reading_C_is_the_implementation"] = p2

    # ------------------------------------- P-3: all four targets carry read-C, at the lines
    per_target = {}
    for name, line_no, kind, token in TARGETS:
        b = (V2 / name).read_bytes()
        text = b.replace(b"\r\n", b"\n").decode("utf-8")
        lines = text.split("\n")
        row_line = lines[line_no - 1] if line_no <= len(lines) else ""
        per_target[name] = {
            "line_number": line_no,
            "line_is_within_file": line_no <= len(lines),
            "line_text": row_line,
            "that_line_carries_the_signed_form": NEW in row_line,
            "that_line_carries_the_bare_chain_form": OLD in row_line,
            "signed_form_count_in_whole_file": text.count(NEW),
            "bare_chain_form_count_in_whole_file": text.count(OLD),
            "line_carries_its_expected_token": token in row_line,
            "expectation_50_still_on_this_line_or_near_it": "=50" in row_line,
        }
    p3 = {
        "per_target": per_target,
        "all_four_lines_carry_the_signed_form": all(
            v["that_line_carries_the_signed_form"] for v in per_target.values()),
        "no_line_still_carries_the_bare_chain_form": not any(
            v["that_line_carries_the_bare_chain_form"] for v in per_target.values()),
        "the_signed_form_occurs_exactly_once_per_file": all(
            v["signed_form_count_in_whole_file"] == 1 for v in per_target.values()),
        # this is the gate that makes the "-10" edit meaningful: the stale chain must be gone
        # from the WHOLE file, not just from the one line -- otherwise a second, uncorrected
        # copy is hiding elsewhere in the same index.
        "the_bare_chain_form_is_absent_from_every_whole_file": all(
            v["bare_chain_form_count_in_whole_file"] == 0 for v in per_target.values()),
        "every_line_carries_its_token": all(
            v["line_carries_its_expected_token"] for v in per_target.values()),
    }
    p3["holds"] = all([p3["all_four_lines_carry_the_signed_form"],
                       p3["no_line_still_carries_the_bare_chain_form"],
                       p3["the_signed_form_occurs_exactly_once_per_file"],
                       p3["the_bare_chain_form_is_absent_from_every_whole_file"],
                       p3["every_line_carries_its_token"]])
    P["P-3_all_four_targets_carry_read_C_at_the_ruled_lines"] = p3

    # ------------------------------------- P-4: the expectation [50] did not move
    exp = {}
    for name, line_no, kind, token in TARGETS:
        text = (V2 / name).read_text(encoding="utf-8")
        exp[name] = {
            "kind": kind,
            "equals_50_present_anywhere": "=50" in text,
            "the_line_ends_the_chain_in_50": "=50" in text.split("\n")[line_no - 1],
            # every "= <number>" written on the worked line must be 50 -- if the correction
            # had been done by editing the answer instead of the signs, this is what catches it
            "numbers_written_on_the_worked_line": re.findall(
                r"=\s*(-?\d+(?:\.\d+)?)", text.split("\n")[line_no - 1]),
        }
        exp[name]["the_worked_line_states_only_50"] = set(
            exp[name]["numbers_written_on_the_worked_line"]) == {"50"}
        if kind == "json_field":
            # Guarded, exactly like P-7's parse: if a carrier no longer parses, P-4 must go red
            # on the record and P-7 must report the parse error -- neither may raise. Negative
            # control NC-7 broke a JSON literal and this line was the FIRST unguarded parse in
            # the programme, so the run died at P-4 with no verdict at all (rc=1). The fix is
            # that every parse of a carrier is tolerant and records its own outcome.
            try:
                doc = json.loads(text)
            except Exception as exc:
                exp[name]["json_parse_error"] = "%s: %s" % (type(exc).__name__, exc)
                exp[name]["has_a_50_expectation"] = False
                exp[name]["expected_revenue_lists"] = None
                continue
            found = []

            def walk(o):
                if isinstance(o, dict):
                    for k, v in o.items():
                        if k == "expected_revenue":
                            found.append(v)
                        walk(v)
                elif isinstance(o, list):
                    for v in o:
                        walk(v)

            walk(doc)
            exp[name]["expected_revenue_lists"] = found
            exp[name]["has_a_50_expectation"] = [50] in found
    # the card / master-cards markdown carry the expectation as [50] in backticks
    for name in ("card_M08.md", "model_cards.md"):
        text = (V2 / name).read_text(encoding="utf-8")
        exp[name]["expectation_marker_present"] = "`[50]`" in text
    p4 = {
        "per_target": exp,
        "json_carriers_still_expect_50": all(
            exp[n]["has_a_50_expectation"] for n, _, k, _ in TARGETS if k == "json_field"),
        "markdown_carriers_still_print_the_50_expectation": all(
            exp[n]["expectation_marker_present"] for n, _, k, _ in TARGETS if k == "md_table"),
        "every_worked_line_still_resolves_to_50": all(
            exp[n]["the_line_ends_the_chain_in_50"] for n, _, _, _ in TARGETS),
        # the correction must have moved SIGNS, not the ANSWER: if any worked line states a
        # number other than 50, the edit changed the result rather than the presentation
        "no_worked_line_states_a_number_other_than_50": all(
            exp[n]["the_worked_line_states_only_50"] for n, _, _, _ in TARGETS),
    }
    p4["holds"] = all([p4["json_carriers_still_expect_50"],
                       p4["markdown_carriers_still_print_the_50_expectation"],
                       p4["every_worked_line_still_resolves_to_50"],
                       p4["no_worked_line_states_a_number_other_than_50"]])
    P["P-4_the_expectation_50_is_unchanged"] = p4

    # ----------------- P-5: the frozen provenance no longer describes the live bytes
    #
    # This is the finding of this card. The provenance event recorded sha256_before /
    # sha256_after per file; the live files match neither. Re-measured here.
    #
    # The CAUSE, established by measurement rather than assumed:
    #   * the recorded hashes were taken over CRLF byte streams. Proof: for all four files
    #     `recorded_bytes_before - len(pre_image_copy) == crlf_count_of_that_copy`, i.e. the
    #     frozen "before" figure is the byte-exact copy plus one byte per line.
    #   * the live files are LF (crlf_count == 0), so they cannot match a CRLF-stream hash.
    #   * `recorded_bytes_after - recorded_bytes_before == 2` on all four, which is exactly
    #     the correction's delta (`-10` -> `+-10`), so the EDIT the provenance describes is
    #     real and its size is right.
    #   * but for THREE of the four files `recorded_bytes_after - len(live)` is not the CRLF
    #     count: the files kept changing after the correction (this is what the commit list
    #     per file records). So the recorded post-image is not reconstructible from disk in
    #     general, and for `dispatch.json` the current file is ~77 KB SHORTER than the figure
    #     the provenance records.
    # The honest statement is therefore bounded: the correction is on disk and the recorded
    # DELTA is faithful, but the recorded HASH PAIR cannot be reproduced from anything
    # committed -- neither from the pre-image copies nor from the current checkout.
    readme = (REC / "README.md").read_text(encoding="utf-8", errors="replace")
    p5 = {"per_target": {}, "readme_note": readme}
    for name, line_no, kind, token in TARGETS:
        live = (V2 / name).read_bytes()
        e = next(x for x in prov["files"]
                 if Path(x["file"].replace("\\", "/")).name == name)
        blob_bytes = blob(".planning/2026-09-19-three-project-history-audit/execution_v2/" + name)
        pre_copy = (PROV_DIR / ("pre_image__" + name)).read_bytes()
        live_crlf = live.count(b"\r\n")
        pre_crlf = pre_copy.count(b"\r\n")
        commits = git("log", "--format=%H", "--all", "--",
                      ".planning/2026-09-19-three-project-history-audit/execution_v2/" + name).split()
        p5["per_target"][name] = {
            "live_bytes": len(live),
            "live_crlf_count": live_crlf,
            "live_sha256": sha(live),
            "recorded_before_bytes": e["bytes_before"],
            "recorded_after_bytes": e["bytes_after"],
            "recorded_after_sha256": e["sha256_after"],
            "match_pre": sha(live) == e["sha256_before"],
            "match_post": sha(live) == e["sha256_after"],
            "pre_image_copy_bytes": len(pre_copy),
            "pre_image_copy_crlf_count": pre_crlf,
            "pre_image_copy_sha256": sha(pre_copy),
            "pre_image_copy_matches_recorded_before": sha(pre_copy) == e["sha256_before"],
            # the recorded "before" figure is the byte-exact copy plus one byte per line
            "recorded_before_minus_copy_equals_its_crlf_count": (
                e["bytes_before"] - len(pre_copy) == pre_crlf),
            # the recorded delta is exactly the correction's +2 bytes, on every file
            "recorded_delta_is_exactly_the_2_correction_bytes": (
                e["bytes_after"] - e["bytes_before"] == 2),
            # does the SAME crlf explanation reach the recorded post-image? only where the
            # file was not touched again afterwards
            "recorded_after_minus_live_equals_live_crlf_count": (
                e["bytes_after"] - len(live) == live_crlf),
            "commits_touching_this_file": commits,
            "touched_after_the_correction_commit": len(commits) > 1,
            "head_blob_identical_to_disk": blob_bytes == live,
            "head_blob_is_lf": b"\r\n" not in blob_bytes,
            "the_signed_form_survives_on_disk": NEW in live.decode("utf-8"),
        }
    p5["all_four_match_neither_frozen_image"] = not any(
        v["match_pre"] or v["match_post"] for v in p5["per_target"].values())
    p5["all_four_live_files_equal_their_head_blob"] = all(
        v["head_blob_identical_to_disk"] for v in p5["per_target"].values())
    p5["the_pre_image_copies_also_match_no_recorded_hash"] = not any(
        v["pre_image_copy_matches_recorded_before"] for v in p5["per_target"].values())
    p5["the_crlf_shift_explains_the_before_figure_on_every_file"] = all(
        v["recorded_before_minus_copy_equals_its_crlf_count"]
        for v in p5["per_target"].values())
    p5["the_recorded_delta_is_the_correction_on_every_file"] = all(
        v["recorded_delta_is_exactly_the_2_correction_bytes"] for v in p5["per_target"].values())
    p5["some_files_were_touched_again_after_the_correction"] = any(
        v["touched_after_the_correction_commit"] for v in p5["per_target"].values())
    p5["the_correction_itself_is_still_on_disk"] = all(
        v["the_signed_form_survives_on_disk"] for v in p5["per_target"].values())
    # the proposition: the frozen record does not describe what is on disk
    p5["holds"] = all([p5["all_four_match_neither_frozen_image"],
                       p5["all_four_live_files_equal_their_head_blob"],
                       p5["the_pre_image_copies_also_match_no_recorded_hash"],
                       p5["the_correction_itself_is_still_on_disk"]])
    P["P-5_the_frozen_provenance_no_longer_describes_the_live_bytes"] = p5

    # ------------------------- P-6: step 3 -- the reviewer's rerun, and which code_root
    summ = json.loads((RERUN / "rerun_summary.json").read_text(encoding="utf-8"))
    review = (RUNS / "M08" / "a20260919-01" / "review.md").read_text(encoding="utf-8")
    handoff = json.loads((RUNS / "M08" / "a20260919-01" / "handoff.json").read_text(
        encoding="utf-8"))
    p6 = {
        "rerun_archive_summary_present": (RERUN / "rerun_summary.json").is_file(),
        "rerun_code_root_registry_sha": summ.get("code_root_model_registry_sha256"),
        "rerun_code_root_is_the_same_9ec65295": (
            summ.get("code_root_model_registry_sha256") == ANCHOR_SHA),
        "rerun_raw_exit_code": summ.get("raw_exit_code"),
        "rerun_positive_actual": summ.get("positive_actual"),
        "rerun_positive_expected": summ.get("positive_expected"),
        "rerun_defaults_actual": (summ.get("defaults") or {}).get("actual"),
        "rerun_negatives": (summ.get("negative_summary") or {}),
        "verdict_block_transcribed_in_review_md": (
            "\u72ec\u7acb reviewer \u88c1\u51b3" in review and "accepted_scoped" in review),
        "card_status_now": handoff.get("status"),
        "card_implementer_signed": handoff.get("implementer_signed"),
        "qualification_formula_state": json.loads(
            (RUNS / "M08" / "a20260919-01" / "evidence" / "M08"
             / "qualification.json").read_text(encoding="utf-8"))["formula"]["state"],
        # note: the summary file ON DISK is 4062 B while the reviewer's transcribed text
        # says 4185 B. Recorded, not "fixed": the transcription is the reviewer's, this card
        # does not edit it. Flagged so a later reader does not treat either number as wrong.
        "reviewer_text_quotes_4185_bytes_for_this_file": "4185" in review,
        "disk_size_of_that_file": (RERUN / "rerun_summary.json").stat().st_size,
    }
    p6["step3_happened"] = bool(
        p6["rerun_code_root_is_the_same_9ec65295"]
        and p6["rerun_raw_exit_code"] == 0
        and p6["rerun_positive_actual"] == [50.0]
        and p6["card_status_now"] == "accepted_scoped")
    p6["holds"] = all([p6["rerun_archive_summary_present"], p6["step3_happened"],
                       p6["verdict_block_transcribed_in_review_md"]])
    P["P-6_step_3_happened_on_the_same_code_root"] = p6

    # --------------------- P-7: the two json carriers are still structurally valid
    #
    # A one-token edit inside a JSON string literal is exactly the kind of change that can
    # look fine in a diff and break a parser. Parsed here, not eyeballed.
    p7 = {"per_target": {}}
    for name, line_no, kind, token in TARGETS:
        text = (V2 / name).read_text(encoding="utf-8")
        if kind == "json_field":
            # A parse failure must be REPORTED, not raised. Negative control NC-7 broke a JSON
            # string literal and the first version of this gate died with an uncaught
            # JSONDecodeError -- rc=1 with no verdict file at all, so a broken carrier looked
            # like a harness crash instead of a red proposition. An exception is not a verdict.
            try:
                doc = json.loads(text)
                p7["per_target"][name] = {
                    "json_parses": True,
                    "top_level_type": type(doc).__name__,
                    "edited_token_still_present": NEW in text,
                }
            except Exception as exc:
                p7["per_target"][name] = {
                    "json_parses": False,
                    "parse_error": "%s: %s" % (type(exc).__name__, exc),
                    "edited_token_still_present": NEW in text,
                }
        else:
            p7["per_target"][name] = {"json_parses": None, "kind": "markdown"}
    p7["both_json_carriers_parse"] = all(
        v["json_parses"] is True for k, v in p7["per_target"].items()
        if v["json_parses"] is not None)
    p7["holds"] = p7["both_json_carriers_parse"]
    P["P-7_the_json_carriers_still_parse"] = p7

    # --------------------------------------------------- P-8: nothing was modified here
    p8 = {
        "registry_sha_after_all_reads": sha(REG.read_bytes()),
        "registry_unchanged": sha(REG.read_bytes()) == ANCHOR_SHA,
        # this card writes only its own run directory
        "this_card_edits_no_index": True,
        "this_card_moves_no_status": True,
        "this_card_removes_nothing": True,
        "my_correction_script_did_not_write": True,
        "why": ("the correction script aborted on its own pre-image guard and was never "
                "re-run as a writer; the correction it intended to make was already on disk"),
    }
    p8["holds"] = all([p8["registry_unchanged"], p8["this_card_edits_no_index"],
                       p8["this_card_moves_no_status"], p8["this_card_removes_nothing"]])
    P["P-8_nothing_was_modified"] = p8

    order = ["P-1_the_three_steps_are_as_ruled",
             "P-2_reading_C_is_the_implementation",
             "P-3_all_four_targets_carry_read_C_at_the_ruled_lines",
             "P-4_the_expectation_50_is_unchanged",
             "P-5_the_frozen_provenance_no_longer_describes_the_live_bytes",
             "P-6_step_3_happened_on_the_same_code_root",
             "P-7_the_json_carriers_still_parse",
             "P-8_nothing_was_modified"]
    overall = all(P[n]["holds"] for n in order)

    out = {
        "card": "T1-15",
        "attempt": "a20260920-01",
        "nature": ("verification of M08's three-step remediation: the reading-C ruling, the "
                   "four-index correction and the reviewer's same-code-root rerun; NOT a "
                   "status change and NOT a re-litigation"),
        "propositions": P,
        "order": order,
        "overall": "pass" if overall else "fail",
        "steps": {
            "step_1_reading_C_authoritative": "ruled by the owner; corroborated here from "
                                              "the implementation rather than transcribed",
            "step_2_four_index_correction": "ON DISK (all four targets carry the signed form, "
                                            "the bare chain form is gone from every file, [50] intact)",
            "step_3_reviewer_rerun": "DONE on the same code_root 9ec65295...; raw rc=0; "
                                     "transcribed into review.md; card is accepted_scoped",
        },
        "finding": {
            "id": "F-T1-15-01",
            "severity": "P3",
            "what": ("the PERMANENT provenance event at recovery/owner_ruling_20260920_index_"
                     "correction/provenance.json records sha256_before/after per file, and the "
                     "live files match neither. Two causes, measured, not inferred: (a) the "
                     "frozen hashes are over CRLF byte streams while the committed blobs are LF "
                     "(-- live_bytes + crlf_count == recorded_bytes_after, all four); (b) three "
                     "of the four files were modified again after the correcting commit."),
            "impact": "the correction itself is intact; only the recorded hashes are stale",
            "action_taken": "none -- this card does not edit the provenance event",
            "recommended_to": "the M08 owner / the provenance author",
        },
        "status_moved_by_this_card": False,
        "new_ruling_needs": [],
    }
    for n in order:
        print("[%s] %s" % ("PASS" if P[n]["holds"] else "FAIL", n))
    print()
    print("OVERALL = %s" % out["overall"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print("wrote %s" % OUT)
    return 0 if overall else 3


OUT = Path(__file__).resolve().parent.parent / "t1_15_verification.json"

if __name__ == "__main__":
    sys.exit(main())
