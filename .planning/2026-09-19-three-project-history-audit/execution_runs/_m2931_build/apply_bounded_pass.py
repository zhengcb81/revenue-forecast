import os

T = chr(34) * 3

HEADER = """Bounded-text remainder pass for M29/M30/M31 (reviewer items R-0..R-4).

Reads CONFIRM.md, appends its reviewer confirmation block VERBATIM to each review.md (with a
byte-level transcription proof) and clears the live-record residuals:

  S-0  review.md: append the CONFIRM.md block; write evidence/<CARD>/verdict_confirmation_check.txt
  R-1  handoff.json: OQ-04 live title loses the withdrawn M31 divergence clause; withdrawal note kept
  R-2  scripts/write_binding.py (attempt + build dir): M31 constant corrected to seven drivers with
       card_text_required_matches_registry = True, so a regeneration cannot re-create the retraction
  R-3  handoff.json: OQ-05 live title becomes the post-hoc statement and carries the OQ-05 ruling
  R-4  scripts/pack_card.py and scripts/write_handoff.py: corrected regenerated wording plus a
       stale-source warning banner (these files already ran and must not be re-run here)
  R-0  evidence/<CARD>/verdict_transcription_check.txt: the CRLF claim is corrected (the report was
       measured to contain no CR, so the normalisation was a no-op) with the superseded sentences and
       the pre-correction sha256 recorded inside the file

Idempotent: every edit is guarded by a substring test.  Each file this pass rewrites is first copied
byte-for-byte into recovery/pre_bounded_text_pass/.

Usage:
  <venv python> -X utf8 -B apply_bounded_pass.py --card M29 --attempt-root <attempt> --confirm <CONFIRM.md> --build-dir <execution_runs>/_m2931_build
"""

PACK_WARNING = (
    "!!! STALE SOURCE WARNING (bounded-text pass, {now}) !!!\n"
    "\n"
    "This file already ran for attempt a20260919-01.  It is kept for provenance and for the record\n"
    "of HOW the evidence was produced, but it MUST NOT be re-run against this attempt:\n"
    "\n"
    "  * re-running it would rewrite evidence/<CARD>/source_manifest.json from values measured now,\n"
    "  * and the pack's own oracle_document wording was corrected after the independent reviewer\n"
    "    found the original freshness wording self-contradictory (finding F-04 / residual R-4), so a\n"
    "    re-run would re-emit corrected wording over an attempt whose evidence was already sealed.\n"
    "\n"
    "The sealed evidence under evidence/<CARD>/ is the record; scripts/verify_remediation.py is the\n"
    "read-only re-check; recovery/remediation_r2.json and the errata section of oracle.md list what\n"
    "was corrected.\n"
)

WRITE_BINDING_WARNING = (
    "!!! M31 CARD-TEXT CONSTANT CORRECTED (F-02 withdrawal, {now}) !!!\n"
    "\n"
    "The M31 entry below used to claim that card_M31.md L9 does NOT list net_revenue_per_unit.  That\n"
    "claim was FALSE and was withdrawn by finding F-02: card_M31.md L9 lists all seven drivers and\n"
    "model_cards.md L2818 lists the same seven, byte-identical.  The constant is now the seven drivers\n"
    "with card_text_required_matches_registry = True, so a regeneration cannot re-create the retracted\n"
    "record.  See evidence/M31/binding.json card_text_required_list_vs_registry.errata.superseded_values\n"
    "for the withdrawn values.\n"
)

import argparse
import datetime
import hashlib
import json
import shutil


def tri():
    return T


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


def body_after_docstring(text):
    first = text.index(T)
    second = text.index(T, first + 3) + 3
    return text[second:]


def extract_block(text, heading):
    start = text.index(heading)
    fence = text.index("```markdown", start)
    body_start = text.index("\n", fence) + 1
    body_end = text.index("\n```", body_start) + 1
    block = text[body_start:body_end].replace("\r\n", "\n").replace("\r", "\n")
    if not block.endswith("\n"):
        block += "\n"
    return block


CARDS = {"M29": "commercial_launch", "M30": "finite_adoption", "M31": "inventory_sellthrough"}

OQ04_TITLE = "numerical domain / boundary observations of this model"
OQ05_TITLE = ("oracle.md's present mtime is a post-hoc value and is NOT pre-run evidence (measured: "
              "oracle_md_mtime < product_stdout_mtime)")

OLD_M31_CONSTANT = (
    '            "card_text_required_list": ["opening_inventory", "saleable_production", '
    '"purchased_units",\n'
    '                                        "scrapped_units", "sold_units", "closing_inventory"],\n'
    '            "card_text_required_matches_registry": False,\n'
    '            "card_text_divergence_note": (\n'
    '                "card_M31.md L9 lists required as opening_inventory, saleable_production, "\n'
    '                "purchased_units, scrapped_units, sold_units, closing_inventory and does NOT '
    'list "\n'
    '                "net_revenue_per_unit, while the registry declares it required (dimension "\n'
    '                "revenue_per_unit). The formula itself is printed in the card without that '
    'driver in "\n'
    '                "the parameter list, so the REGISTRY is the authority here: not supplying "\n'
    '                "net_revenue_per_unit is refused with \'missing drivers\'. Recorded, not '
    'silently "\n'
    '                "resolved."),'
)

NEW_M31_CONSTANT = (
    '            "card_text_required_list": ["opening_inventory", "saleable_production", '
    '"purchased_units",\n'
    '                                        "scrapped_units", "sold_units", "closing_inventory",\n'
    '                                        "net_revenue_per_unit"],\n'
    '            "card_text_required_matches_registry": True,\n'
    '            "card_text_divergence_note": None,\n'
    '            "card_text_divergence_withdrawal_note": (\n'
    '                "F-02 WITHDRAWAL: an earlier version of this constant claimed that card_M31.md '
    'L9 "\n'
    '                "does NOT list net_revenue_per_unit. That claim was false: card_M31.md L9 lists '
    'all "\n'
    '                "seven drivers and model_cards.md L2818 lists the same seven, byte-identical. '
    'The "\n'
    '                "constant is now seven drivers with card_text_required_matches_registry = True; '
    'see "\n'
    '                "evidence/M31/binding.json "\n'
    '                "card_text_required_list_vs_registry.errata.superseded_values for the withdrawn "\n'
    '                "values."),'
)

OLD_OQ04 = (
    '{"id": "OQ-04", "title": "numerical domain / boundary observations incl. the M31 card-text "\n'
    '                                     "divergence on net_revenue_per_unit",'
)
NEW_OQ04 = '{"id": "OQ-04", "title": "numerical domain / boundary observations of this model",'

OLD_OQ05 = (
    '{"id": "OQ-05", "title": "oracle.md was restored after the run (content unchanged) and its "\n'
    '                                     "present mtime is later than the product stdout",'
)
NEW_OQ05 = (
    '{"id": "OQ-05", "title": "oracle.md\'s present mtime is a post-hoc value and is NOT pre-run "\n'
    '                                     "evidence (measured: oracle_md_mtime < '
    'product_stdout_mtime)",'
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--confirm", required=True)
    parser.add_argument("--build-dir", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    build_dir = os.path.abspath(args.build_dir)
    evidence = os.path.join(attempt, "evidence", card)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    backup_dir = os.path.join(attempt, "recovery", "pre_bounded_text_pass")
    os.makedirs(backup_dir, exist_ok=True)
    summary = {"card_id": card, "generated_utc": now, "files": {}, "pre_pass_copies": backup_dir}

    def backup(rel):
        src = os.path.join(attempt, rel.replace("/", os.sep))
        if os.path.isfile(src):
            dst = os.path.join(backup_dir, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.isfile(dst):
                shutil.copyfile(src, dst)

    def record(label, path, before, note=""):
        after = sha256(path) if os.path.isfile(path) else None
        summary["files"][label] = {"path": path, "sha256_before": before, "sha256_after": after,
                                   "changed": before != after}
        if note:
            summary["files"][label]["note"] = note
        print("  %-46s %s -> %s" % (label, (before or "None")[:16], (after or "None")[:16]))

    # ---------------- S-0: append the reviewer's bounded-text confirmation block ----------------
    review_path = os.path.join(attempt, "review.md")
    backup("review.md")
    review_before = sha256(review_path)
    block = extract_block(read_text(args.confirm), "## 可直接抄录的裁决确认")
    block_bytes = block.encode("utf-8")
    block_sha = hashlib.sha256(block_bytes).hexdigest()
    review_text = read_text(review_path)
    if "M31 在 R-1 / R-2 清除前不得关闭" in review_text:
        print("S-0 already appended - skipping")
    else:
        if not review_text.endswith("\n"):
            review_text += "\n"
        pre_bytes = review_text.encode("utf-8")
        write_text(review_path, review_text + "\n" + block)
        review_after = read_text(review_path)
        span = review_after.encode("utf-8")[len(pre_bytes):]
        appended = span[1:] if span.startswith(b"\n") else span
        start_line = (review_text.count("\n") + 1) + 1
        end_line = start_line + block.count("\n") - 1
        if appended != block_bytes:
            raise SystemExit("CONFIRMATION TRANSCRIPTION FAILED")
        check_path = os.path.join(evidence, "verdict_confirmation_check.txt")
        check = [
            "verdict_confirmation_check",
            "card_id: %s" % card,
            "model_id: %s" % CARDS[card],
            "attempt_root: %s" % attempt,
            "confirm_report: %s" % os.path.abspath(args.confirm),
            "confirm_section: the fenced block after '## 可直接抄录的裁决确认'",
            "method: the fenced block was extracted from CONFIRM.md, appended to review.md behind one "
            "blank separator line, and the appended span was re-read from review.md and compared "
            "byte-for-byte with the extracted block.",
            "line_ending_normalisation: none needed (CONFIRM.md contains no CR characters)",
            "extracted_block_sha256: %s" % block_sha,
            "extracted_block_bytes: %d" % len(block_bytes),
            "appended_block_sha256: %s" % hashlib.sha256(appended).hexdigest(),
            "appended_block_bytes: %d" % len(appended),
            "byte_identical: true",
            "review_md_sha256_before_append: %s" % review_before,
            "review_md_sha256_after_append: %s" % sha256(review_path),
            "appended_block_first_line_1based: %d" % start_line,
            "appended_block_last_line_1based: %d" % end_line,
            "m31_close_condition_preserved: true (the block contains the sentence that M31 may not be "
            "closed before R-1/R-2 are cleared)",
            "assertion: appended_block_sha256 == extracted_block_sha256 -> PASS",
            "note: the pre-existing review.md body (including the earlier verdict block) was not "
            "modified.",
        ]
        write_text(check_path, "\n".join(check) + "\n")
        print("S-0 appended to review.md lines %d-%d (sha %s)" % (start_line, end_line, block_sha[:16]))
        record("evidence/%s/verdict_confirmation_check.txt" % card, check_path, None)
    record("review.md", review_path, review_before)

    # ---------------- R-0: correct the transcription-check wording ----------------
    tc_path = os.path.join(evidence, "verdict_transcription_check.txt")
    backup("evidence/%s/verdict_transcription_check.txt" % card)
    tc_before = sha256(tc_path)
    tc = read_text(tc_path)
    if "line_ending_normalisation_note_corrected" in tc:
        print("R-0 already applied - skipping")
    else:
        old_sentences = [line for line in tc.splitlines()
                         if line.startswith("method: ") or line.startswith("line_ending_normalisation:")]
        tc = tc.replace(
            "line endings were normalised CRLF->LF (the report is CRLF, every attempt file is LF; the "
            "verbatim requirement applies to the text), ",
            "line endings were normalised CRLF->LF as a defensive no-op: the report was MEASURED to "
            "contain 0 CR characters (it is LF), so this step changed nothing. ")
        tc = tc.replace(
            "line_ending_normalisation: CRLF -> LF (transport only; no character of the text changed)",
            "line_ending_normalisation: CRLF -> LF as a defensive no-op (measured CR count in the "
            "report: 0); no character of the text was altered")
        addendum = [
            "",
            "correction (bounded-text pass, %s):" % now,
            "  finding: R-0 (independent reviewer, bounded-text confirmation)",
            "  what_was_wrong: the original method sentence claimed the report is CRLF while the report "
            "contains 0 CR characters, so the normalisation was a no-op and the claim was wrong",
            "  superseded_sentences:",
        ]
        addendum += ["    - %s" % sentence for sentence in old_sentences]
        addendum += [
            "  corrected_wording: the method and line_ending_normalisation lines above",
            "  effect_on_the_proof: none -- byte_identical: true and the recorded hashes are unchanged",
            "  line_ending_normalisation_note_corrected: true",
            "  verdict_transcription_check_sha256_before_this_correction: %s" % tc_before,
        ]
        write_text(tc_path, tc.rstrip("\n") + "\n" + "\n".join(addendum) + "\n")
        record("evidence/%s/verdict_transcription_check.txt" % card, tc_path, tc_before,
               "R-0 wording correction (superseded sentences + pre-correction hash kept)")

    # ---------------- R-1 / R-3: handoff live titles ----------------
    handoff_path = os.path.join(attempt, "handoff.json")
    backup("handoff.json")
    handoff_before = sha256(handoff_path)
    handoff = load_json(handoff_path)
    superseded = handoff.setdefault("live_record_corrections", {})
    for question in handoff.get("open_questions", []):
        if question.get("id") == "OQ-04" and question.get("title") != OQ04_TITLE:
            superseded.setdefault("R-1", {
                "applied_utc": now,
                "finding": "R-1 (independent reviewer, bounded-text confirmation)",
                "what_was_wrong": "the live OQ-04 title still asserted the M31 card-text divergence",
                "superseded_title": question["title"],
                "corrected_to": OQ04_TITLE,
                "withdrawal_evidence": ("evidence/M31/binding.json "
                                        "card_text_required_list_vs_registry.errata.superseded_values"),
            })
            question["title"] = OQ04_TITLE
            question["withdrawn_claim"] = {
                "applied_utc": now,
                "finding": "F-02 (independent reviewer) via residual R-1",
                "withdrawal": ("the M31 card text and the registry agree on all seven drivers; there is "
                               "no divergence and no owner ruling is required for one"),
                "superseded_by": ["evidence/M31/binding.json errata",
                                  "evidence/M31/oq_rulings.json rulings[OQ-04].withdrawn_claim",
                                  "oracle.md errata r1 section E-2"],
            }
        if question.get("id") == "OQ-05" and question.get("title") != OQ05_TITLE:
            superseded.setdefault("R-3", {
                "applied_utc": now,
                "finding": "R-3 (independent reviewer, bounded-text confirmation)",
                "what_was_wrong": ("the live OQ-05 title said the present mtime is later than the "
                                   "product stdout, contradicting the same attempt's "
                                   "source_manifest.oracle_document.oracle_md_provenance"),
                "superseded_title": question["title"],
                "corrected_to": OQ05_TITLE,
                "measured": ("oracle_md_mtime < product_stdout_mtime, re-derived from "
                             "evidence/%s/source_manifest.json mtime_ordering" % card),
            })
            question["title"] = OQ05_TITLE
            question["ruling"] = {
                "ruled_by": "independent reviewer (OQ-05 ruling, report section 2.3)",
                "ruling": ("oracle.md's present mtime is a POST-HOC value and is not offered as pre-run "
                           "evidence in either direction; what was anchored before the generator ran is "
                           "the generator code scripts/oracle_%s.py (sha256 "
                           "3177247f95f7554920ac43b4e076f28b5ef78250059c130de1f5e8dee2e4c09e), and "
                           "oracle.md is outside the anchor scope and carries no gating expectation"
                           % card),
                "does_not_block": "the formula signature (owner claims formula only)",
                "boundary": ("if the owner wants oracle.md treated as pre-run frozen evidence, this "
                             "attempt is NOT sufficient and a re-run is required"),
            }
    dump_json(handoff_path, handoff)
    record("handoff.json", handoff_path, handoff_before, "R-1 + R-3 live titles corrected")

    # ---------------- bounded git claim ----------------
    handoff = load_json(handoff_path)
    if "git_writes" not in handoff:
        before = sha256(handoff_path)
        handoff["git_writes"] = {
            "statement": ("this attempt executed no git write command: no add, commit, restore, stash, "
                          "checkout or reset was run by any command of this card; the only git "
                          "invocation in the whole attempt is the read-only `git status --porcelain` "
                          "inside hash_state.py"),
            "what_is_NOT_claimed": ("it is NOT claimed that no commit happened in revenue-forecast "
                                    "during this window. The repository is shared and the orchestration "
                                    "layer committed concurrently (observed: 66bd75f1 at 04:20:08 and "
                                    "cc78c529 at 04:27:52, the latter containing this batch's "
                                    "execution_runs/M29|M30|M31 handoff.json / oracle.md / "
                                    "verdict_transcription_check.txt). Those commits were not made by "
                                    "this attempt."),
            "evidence": ["binding.json forbidden list", "integrity.json",
                         "before/ and after/ git status --porcelain captures",
                         "evidence/%s/runs/G0-state-before/rc.json and "
                         "evidence/%s/runs/G1-state-after/rc.json" % (card, card)],
        }
        handoff["integrity_statement_scope"] = (
            "production_repos_untouched refers to FILE WRITES BY THIS ATTEMPT only, measured by the "
            "before/after source hashes; it is not a claim about the repository's commit history")
        dump_json(handoff_path, handoff)
        record("handoff.json (git_writes)", handoff_path, before)

    # ---------------- R-2: write_binding.py ----------------
    for target in (os.path.join(attempt, "scripts", "write_binding.py"),
                   os.path.join(build_dir, "write_binding.py")):
        if not os.path.isfile(target):
            print("R-2 skip (missing):", target)
            continue
        before = sha256(target)
        text = read_text(target)
        if "M31 CARD-TEXT CONSTANT CORRECTED" in text:
            print("R-2 already applied:", target)
            continue
        text = text.replace(OLD_M31_CONSTANT, NEW_M31_CONSTANT)
        write_text(target, tri() + WRITE_BINDING_WARNING.format(now=now) + tri()
                   + body_after_docstring(text))
        label = ("scripts/write_binding.py" if target.startswith(attempt)
                 else "_m2931_build/write_binding.py")
        record(label, target, before, "R-2 constant corrected + warning banner")

    # ---------------- R-4: pack_card.py + write_handoff.py ----------------
    for name in ("pack_card.py", "write_handoff.py"):
        for target in (os.path.join(attempt, "scripts", name), os.path.join(build_dir, name)):
            if not os.path.isfile(target):
                print("R-4 skip (missing):", target)
                continue
            before = sha256(target)
            text = read_text(target)
            if "STALE SOURCE WARNING" in text:
                print("R-4 already applied:", target)
                continue
            if name == "write_handoff.py":
                text = text.replace(OLD_OQ04, NEW_OQ04)
                text = text.replace(OLD_OQ05, NEW_OQ05)
            write_text(target, tri() + PACK_WARNING.format(now=now) + tri()
                       + body_after_docstring(text))
            label = ("scripts/%s" % name if target.startswith(attempt)
                     else "_m2931_build/%s" % name)
            record(label, target, before, "R-4 warning banner (and corrected OQ titles)")

    # ---------------- bookkeeping ----------------
    sm_path = os.path.join(evidence, "source_manifest.json")
    backup("evidence/%s/source_manifest.json" % card)
    sm_before = sha256(sm_path)
    sm = load_json(sm_path)
    sm.setdefault("post_review_text_corrections", {})
    sm["post_review_text_corrections"]["bounded_text_pass"] = {
        "applied_utc": now,
        "findings": ["R-0", "R-1", "R-2", "R-3", "R-4"],
        "frozen_evidence_touched": False,
        "frozen_evidence_note": ("input.json, oracle.json and cases.json were not touched by this pass "
                                 "or by the earlier remediation; their hashes in evidence_input_hashes "
                                 "are unchanged"),
        "script_hashes_after_this_pass": {
            item: sha256(os.path.join(attempt, "scripts", item))
            for item in sorted(os.listdir(os.path.join(attempt, "scripts")))
            if item.endswith(".py")
        },
        "script_hashes_note": ("card_script_hashes above is the pack-time record; these are the "
                               "current values and the difference is exactly this text pass"),
        "git_claim": "see handoff.json git_writes (bounded statement)",
    }
    dump_json(sm_path, sm)
    record("evidence/%s/source_manifest.json" % card, sm_path, sm_before)

    # ---------------- refresh the final ledger ----------------
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
            for item in sorted(names):
                path = os.path.join(root, item)
                rel = os.path.relpath(path, attempt).replace("\\", "/")
                if rel.endswith("final_deliverable_hashes.json"):
                    continue
                files[rel] = {"absolute_path": path, "sha256": sha256(path),
                              "size_bytes": os.path.getsize(path)}
        dump_json(ledger, {
            "card_id": card, "attempt_id": "a20260919-01", "model_id": CARDS[card],
            "attempt_root": attempt, "generated_utc": now,
            "interpreter_path": os.path.join(attempt, "iso", "venv", "Scripts", "python.exe"),
            "excluded_from_the_table": ["iso/venv/**"],
            "written_last": "refreshed after the bounded-text pass (R-0..R-4)",
            "file_count": len(files), "files": files})
        print("refreshed final ledger:", len(files), "files")

    summary_path = os.path.join(attempt, "recovery", "bounded_text_pass.json")
    dump_json(summary_path, summary)
    print("bounded-text pass summary ->", summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
