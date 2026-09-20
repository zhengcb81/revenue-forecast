"""Append the r3 bookkeeping addendum to decision.md, and register the two summary entries
(one M-card attempt). Append-only: no existing byte of decision.md is rewritten.

Requested by the orchestration layer after its independent re-verification of the M13-M16
transcription pass:

  1. decision.md said nothing about the qualification state while handoff.json and
     qualification.json now say ``accepted_scoped``. This script APPENDS one section
     (``## r3 bookkeeping addendum (appended, not rewritten)``) that records the reviewer's
     verdict, its carriers, the historical-value declaration, the unchanged scope and the
     non-signature statement. It never edits, reflows or deletes existing bytes; the proof is
     ``sha256(new_bytes[:len(old_bytes)]) == sha256(old_bytes)``.
  2. ``evidence/<CARD>/doc_pointer_audit.json`` is pre-r3 and is NOT to be re-run (that would
     rewrite an evidence file and is outside the authorised write set). The limitation is
     registered in ``recovery/bookkeeping_r3/summary.json`` under ``limits`` instead.
  3. Two practices worth reusing are recorded under ``notes``: the idempotent re-run and the
     timezone self-correction.

Factual note recorded in the addendum: M13-M16 decision.md never contained the literal token
``review_pending`` (that wording lives in the M17-M20 decision records); the historical-value
declaration is therefore made for disambiguation, and the addendum says so.

Run without --apply for a dry run (nothing is written).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

SCRIPT = os.path.abspath(__file__)
ATTEMPT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT)))
CARD = os.path.basename(os.path.dirname(ATTEMPT))
BK = os.path.join(ATTEMPT, "recovery", "bookkeeping_r3")
HEADING = "## r3 bookkeeping addendum (appended, not rewritten)"
PROOF_REL = "recovery/bookkeeping_r3/decision_addendum_r3.json"


def sha256b(data):
    return hashlib.sha256(data).hexdigest()


def rb(path):
    with open(path, "rb") as handle:
        return handle.read()


def wb(path, data):
    with open(path, "wb") as handle:
        handle.write(data)


def jdump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def addendum_text(review_lines, addendum_lines, source_sha, source_bytes):
    return """%(heading)s

> 本节由 r3 记账/转录执行者于 2026-09-20 **追加**（append-only）：上文既有字节未被改写；`decision.md` 的
> 前像字节经 `sha256(new[:len(old)]) == sha256(old)` 逐字节校验。本节**不是自签**，验收文字由独立复核者写出。

1. **r3 独立复核判定**：本卡 `formula` 资格 = `accepted_scoped`，**范围仅限 `formula`**；`disclosure_adaptation`
   与 `accuracy` 不在本次裁定内。
2. **载体**：`review.md` 中的复核者裁决原文（**`review.md` 第 %(rls)d–%(rle)d 行**）；其**逐字节**转录证明见
   `evidence/%(card)s/verdict_transcription_r3.json`（旧字节是新字节的前缀、追加区 sha256 = reviewer 源文件
   sha256 = `%(ssha)s`、源文件 %(sbytes)d B、`byte_identical: true`）。同一裁定已记入
   `handoff.json.status` 与 `evidence/%(card)s/qualification.json` 的 `formula.state`，两处旧值
   `review_pending` 均保留在 `*_before_bookkeeping_fix` 键下。（本节自身位于本文件第 %(als)d–%(ale)d 行。）
3. **历史值声明**：本文件此前若出现任何"待复核 / 未签收 / pending"口径的表述，一律视为**历史值**，以本节为准。
   事实核对（记账执行者）：本卡 `decision.md` 原文并未出现 `review_pending` 字样（该字样出现在 M17–M20 的
   decision 记录中），故此声明用于**消除口径歧义**，而非订正某一行原文。
4. **范围未扩大**：`disclosure_adaptation` 仍为 `unmapped`，`accuracy` 仍为 `unproven`；D（披露映射）、
   E（历史映射探针）、F（准确性）三阶段**未执行**，不在本裁定覆盖范围内。
5. **非自签声明**：`implementer_signed: false`；`implementer_never_signs_acceptance: true`；
   authority = "acceptance was written by an independent reviewer, not by the implementer"。

相关记录：`recovery/production_drift_note.json`（F-r3-02 时间窗内的生产漂移声明）、
`evidence/%(card)s/cases_annotation_repack.json`（F-r3-01 口径更正）、`recovery/bookkeeping_r3/summary.json`
（本次记账的改前→改后 sha256 台账）。
""" % {"heading": HEADING, "rls": review_lines[0], "rle": review_lines[1],
       "als": addendum_lines[0], "ale": addendum_lines[1], "card": CARD, "ssha": source_sha,
       "sbytes": source_bytes}


def update_summary(note_text):
    path = os.path.join(BK, "summary.json")
    raw = rb(path)
    summary = json.loads(raw.decode("utf-8"))
    summary.setdefault("limits", {})[
        "doc_pointer_audit_is_pre_r3_and_does_not_cover_the_appended_verdict_text_or_the_new_"
        "recovery_files"] = (
        "evidence/%s/doc_pointer_audit.json was produced by the r3 pipeline BEFORE this bookkeeping "
        "pass appended the reviewer's verdict to review.md and before recovery/production_drift_note"
        ".json and recovery/bookkeeping_r3/** existed, so it does not cover them. It was deliberately "
        "NOT re-run: re-running it would rewrite an evidence file and is outside this pass's "
        "authorised write set - re-running requires separate authorisation. Every pointer it does "
        "contain still resolves; no dangling pointer was introduced." % CARD)
    notes = summary.setdefault("notes", {})
    notes["idempotent_re_run"] = (
        "re-running recovery/bookkeeping_r3/transcribe_r3_verdict.py is safe and is the recommended "
        "template for later bookkeeping executors: it detects that the verdict bytes are already in "
        "review.md and reports 'already_present_verified_not_duplicated' (rc=0, zero writes) instead "
        "of duplicating the block, and every carrier edit is guarded the same way (status/formula "
        "edits are skipped once the '_before_bookkeeping_fix' keys exist, the repack wording and the "
        "oq_rulings provenance line are likewise one-shot). Verified after the fact on all four cards.")
    notes["timezone_self_correction"] = (
        "the first revision of recovery/production_drift_note.json described the drift window's "
        "timezone as 'Asia/Shanghai'. A clock check (Get-Date local vs UTC, "
        "[System.TimeZoneInfo]::Local.Id = GMT Standard Time, offset +01:00) showed the machine is on "
        "GMT Standard Time, so the declared window 2026-09-20 04:35:31-04:40:53 local is "
        "2026-09-20 03:35:31-03:40:53 UTC. The correction was applied to all four notes AND to the "
        "source templates (fix_drift_note_timezone_r3.py), and the bookkeeping table was updated so "
        "no row went stale. Template lesson: state a timezone only after measuring it, and correct "
        "the generator, not just the generated file.")
    summary["notes"]["decision_addendum"] = note_text
    data = jdump(summary).encode("utf-8")
    wb(path, data)
    return {"path": "recovery/bookkeeping_r3/summary.json", "sha256_before": sha256b(raw),
            "sha256_after": sha256b(data), "bytes_before": len(raw), "bytes_after": len(data)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--redo", action="store_true",
                        help="if an earlier append is present, restore the hash-verified pre-pass "
                             "bytes recorded in the existing proof and append the corrected block "
                             "again; no pre-existing byte is ever altered")
    args = parser.parse_args()

    dm = os.path.join(ATTEMPT, "decision.md")
    proof_path = os.path.join(ATTEMPT, *PROOF_REL.split("/"))
    before = rb(dm)
    text = before.decode("utf-8")
    proof = json.loads(rb(os.path.join(ATTEMPT, "evidence", CARD,
                                       "verdict_transcription_r3.json")).decode("utf-8"))
    review_lines = (proof["verdict_block_in_review_md"]["line_start"],
                    proof["verdict_block_in_review_md"]["line_end"])

    revision_note = None
    print("=== decision.md r3 addendum - card %s ===" % CARD)
    if HEADING in text:
        if not (args.redo and os.path.exists(proof_path)):
            existing = json.loads(rb(proof_path).decode("utf-8"))
            print("  addendum already present (decision.md lines %d-%d); nothing to do"
                  % (existing["addendum_block"]["line_start"], existing["addendum_block"]["line_end"]))
            print("  decision.md sha256 = %s" % sha256b(before))
            return 0
        old = json.loads(rb(proof_path).decode("utf-8"))
        truncated = before[:old["bytes_before"]]
        if sha256b(truncated) != old["sha256_before"]:
            raise AssertionError("cannot restore the pre-pass bytes; refusing to touch decision.md")
        revision_note = ("the first append (decision.md %d->%d B, %s->%s) quoted the addendum's own "
                         "line range where the review.md verdict-block range belonged; the file was "
                         "restored to its hash-verified pre-pass bytes (%d B, %s) and the corrected "
                         "block appended. No pre-existing byte was altered at any point."
                         % (old["bytes_before"], old["bytes_after"], old["sha256_before"],
                            old["sha256_after"], old["bytes_before"], old["sha256_before"]))
        before = truncated
        text = before.decode("utf-8")
        print("  --redo: restored the pre-pass bytes (%d B, %s verified)"
              % (len(before), sha256b(before)[:16]))

    sep = b"" if before.endswith(b"\n\n") else (b"\n" if before.endswith(b"\n") else b"\n\n")
    if not before.endswith(b"\n"):
        print("  note: decision.md did not end with a newline; %d separator byte(s) appended"
              % len(sep))
    start_offset = len(before) + len(sep)
    line_start = before.count(b"\n") + sep.count(b"\n") + 1
    # The addendum quotes its own line range, so iterate to a fixed point: the line count depends
    # only on the digit width of the two numbers.
    line_end = line_start
    for _ in range(6):
        body = addendum_text(review_lines, (line_start, line_end), proof["source_sha256"],
                             proof["source_bytes"])
        candidate = line_start + body.count("\n") - (1 if body.endswith("\n") else 0)
        if candidate == line_end:
            break
        line_end = candidate
    body = addendum_text(review_lines, (line_start, line_end), proof["source_sha256"],
                         proof["source_bytes"])
    addendum = body.encode("utf-8")
    after = before + sep + addendum

    if not after.startswith(before) or sha256b(after[:len(before)]) != sha256b(before):
        raise AssertionError("append-only property violated")

    record = {
        "card_id": CARD,
        "kind": "decision.md r3 bookkeeping addendum proof (append-only)",
        "recorded_by": "the r3 bookkeeping/transcription executor session, 2026-09-20",
        "why": "the orchestration layer's independent re-verification asked for decision.md to carry "
               "the r3 qualification state so that one attempt does not read two ways; only an "
               "append was authorised",
        "path": "decision.md",
        "revision_note": revision_note,
        "sha256_before": sha256b(before),
        "bytes_before": len(before),
        "sha256_after": sha256b(after),
        "bytes_after": len(after),
        "prefix_check": {
            "method": "sha256(new_bytes[:len(old_bytes)]) == sha256(old_bytes) and "
                      "new_bytes.startswith(old_bytes)",
            "existing_bytes_untouched": sha256b(after[:len(before)]) == sha256b(before),
            "startswith": after.startswith(before),
        },
        "separator_bytes_added": len(sep),
        "addendum": {
            "heading": HEADING,
            "sha256": sha256b(addendum),
            "bytes": len(addendum),
            "offset_start": start_offset,
            "offset_end": start_offset + len(addendum),
        },
        "addendum_block": {
            "line_start": line_start,
            "line_end": line_end,
            "lines": line_end - line_start + 1,
            "line_numbering": "1-based, inclusive, counted over the final decision.md bytes",
        },
        "carrier_reference": {
            "review_md_verdict_block": proof["verdict_block_in_review_md"],
            "verdict_transcription_proof": "evidence/%s/verdict_transcription_r3.json" % CARD,
            "verdict_transcription_proof_sha256": sha256b(
                rb(os.path.join(ATTEMPT, "evidence", CARD, "verdict_transcription_r3.json"))),
        },
        "declares_prior_pending_wording_historical": True,
        "factual_note": "M13-M16 decision.md never contained the literal token 'review_pending' "
                        "(that wording appears in the M17-M20 decision records); the declaration in "
                        "item 3 removes ambiguity rather than correcting a line of this file",
        "scope_unchanged": {"disclosure_adaptation": "unmapped", "accuracy": "unproven",
                            "D_E_F": "not performed"},
        "implementer_signed": False,
        "implementer_never_signs_acceptance": True,
        "authority": "acceptance was written by an independent reviewer, not by the implementer",
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    print("  decision.md %d -> %d B; %s -> %s" % (len(before), len(after),
                                                  sha256b(before)[:16], sha256b(after)[:16]))
    print("  separator bytes = %d; addendum lines %d-%d (%d lines, %d B)"
          % (len(sep), line_start, line_end, line_end - line_start + 1, len(addendum)))
    if args.apply:
        wb(dm, after)
        wb(proof_path, jdump(record).encode("utf-8"))
        entry = update_summary("an r3 addendum was appended to decision.md at lines %d-%d; proof: %s"
                               % (line_start, line_end, PROOF_REL))
        print("  summary.json %d -> %d B (%s -> %s)" % (entry["bytes_before"], entry["bytes_after"],
                                                        entry["sha256_before"][:12],
                                                        entry["sha256_after"][:12]))
        print("  registered summary limits/notes keys")
    else:
        print("  dry run: nothing written")
    print("=== done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
