"""Transcribe the independent reviewer's r2 verdict into a review.md / batch_handoff.md VERBATIM.

The reviewer wrote the verdict in zero-write mode and authorised transcription on the condition that
the text is not rewritten, shortened or summarised.  This script therefore copies the exact bytes of a
fenced markdown block out of the reviewer's report and appends them unchanged; it then proves equality
by re-reading the target file, locating the copied region and comparing sha256 both ways.

Only AFTER the verbatim block does it append an explicitly labelled "实现者附注" paragraph, so the
reviewer's words and the implementer's words cannot be confused.

Usage:
  python -X utf8 -B transcribe_review_verdict.py --card M17 --report <REPORT_r2.md> \
      --block-index 0 --target <attempt>/review.md --note-mode card --runner-sha256 <sha>
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os

NOTE_CARD = """

### 实现者附注（非 reviewer 文字，另起一段以便区分）

本段由 M17-M20 attempt 的实现 session 追加，**不是** reviewer 的原文。要点：
①上方法庭级判定与"必须修改（P2）"三项、随附 P3-1…P3-6 已逐条处置，处置证据见本卡
`review.md` 的 r2 处置节、`evidence/{card}/oq_rulings.json`、`evidence/{card}/revision_r2.json`、
`process_history.json`、`after/final_deliverable_hashes.json`（含 `drift_count`/`verified_utc`）与
`evidence/{card}/hash_table_selfcheck.json`；
②实现者**未**自签 accepted：`formula` 仍为 `review_pending`，等 reviewer 点审；
③§5.6 的 r1 正文写"2 趟"是 r1 当时的口径，与 `process_history.json` 的"声明 3 趟测量执行"并存，
两者口径已在 r2 节与 `process_history.json.forensic_explanation` 中显式说明（**交叉引用，不改写 r1 正文**）；
④`disclosure_adaptation = unmapped`（零产出）；`accuracy = unproven`。
"""

NOTE_BATCH = """

### 实现者附注（非 reviewer 文字，另起一段以便区分）

本段由 M17-M20 attempt 的实现 session 追加，**不是** reviewer 的原文。第 8 节的 rc 命名空间规则继续
有效；`rc_namespace.json` 已修为**合法 JSON**（由 `scripts/batch_tools.py write-rc-namespace` 生成，
并对批次目录 + 四卡 attempt 的全部 `.json` 做解析回读自检，实测失败数见
`batch_json_validation.json`）。`after/final_deliverable_hashes.json` 与
`evidence/<CARD>/evidence_hashes.json` 现均带 `drift_count`/`verified_utc`，并由收尾后的
`V-verify-hash-tables` 单元再测一次；修好之前的"产物复算 0 drift"主张**已撤回**（见各卡 review.md 的
r2 处置节）。
"""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _atomic_dump(path: str, doc) -> None:
    """Write JSON via a temp file + os.replace so an interrupted write cannot truncate it."""
    tmp = path + ".tmp-atomic"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def extract_blocks(report_bytes: bytes):
    """Return the byte-exact contents of every ```markdown fenced block, in order."""
    blocks = []
    marker = b"```markdown\n"
    position = 0
    while True:
        start = report_bytes.find(marker, position)
        if start < 0:
            break
        body_start = start + len(marker)
        end = report_bytes.find(b"\n```", body_start)
        if end < 0:
            break
        blocks.append(report_bytes[body_start:end + 1])  # keep the trailing newline
        position = end + 4
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--block-index", type=int, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--note-mode", choices=("card", "batch"), required=True)
    parser.add_argument("--runner-sha256", default=None)
    parser.add_argument("--proof-out", default=None)
    args = parser.parse_args()

    with open(args.report, "rb") as handle:
        report = handle.read()
    blocks = extract_blocks(report)
    if args.block_index >= len(blocks):
        print("REFUSED: report has only %d markdown blocks" % len(blocks))
        return 3
    block = blocks[args.block_index]

    with open(args.target, "rb") as handle:
        before = handle.read()
    if block in before:
        # Idempotent re-run: the reviewer's text is already there.  Never append twice; verify that
        # the copy in the file is byte-identical to the block and report success.
        start = before.find(block)
        copied = before[start:start + len(block)]
        proof = {
            "card_id": args.card,
            "target": os.path.abspath(args.target),
            "report": os.path.abspath(args.report),
            "block_index": args.block_index,
            "verbatim": True,
            "transcription_skipped_already_present": True,
            "source_block_sha256": sha256_bytes(block),
            "copied_region_sha256": sha256_bytes(copied),
            "byte_equal": sha256_bytes(block) == sha256_bytes(copied),
            "source_block_bytes": len(block),
            "copied_region_bytes": len(copied),
            "target_bytes_now": len(before),
            "appended_bytes": 0,
            "runner_sha256": args.runner_sha256,
            "executed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        print("verdict block already present in", proof["target"],
              "- re-verified, not appended again")
        print("source_block_sha256:", proof["source_block_sha256"])
        print("copied_region_sha256:", proof["copied_region_sha256"])
        print("byte_equal:", proof["byte_equal"])
        if args.proof_out:
            _atomic_dump(args.proof_out, proof)
            print("proof ->", args.proof_out)
        return 0 if proof["byte_equal"] else 3

    note = (NOTE_CARD.format(card=args.card) if args.note_mode == "card" else NOTE_BATCH)
    if args.note_mode == "card":
        note = note.replace("{card}", args.card)
    separator = ("\n---\n\n").encode("utf-8")
    payload = before + separator + block + note.encode("utf-8")
    tmp = args.target + ".tmp-atomic"
    with open(tmp, "wb") as handle:
        handle.write(payload)
    os.replace(tmp, args.target)

    with open(args.target, "rb") as handle:
        after = handle.read()
    start = after.find(block)
    copied = after[start:start + len(block)]
    proof = {
        "card_id": args.card,
        "target": os.path.abspath(args.target),
        "report": os.path.abspath(args.report),
        "block_index": args.block_index,
        "verbatim": True,
        "source_block_sha256": sha256_bytes(block),
        "copied_region_sha256": sha256_bytes(copied),
        "byte_equal": sha256_bytes(block) == sha256_bytes(copied),
        "source_block_bytes": len(block),
        "copied_region_bytes": len(copied),
        "target_bytes_before": len(before),
        "target_bytes_after": len(after),
        "appended_bytes": len(after) - len(before),
        "note_appended_after_the_verbatim_block": True,
        "note_label": "实现者附注（非 reviewer 文字，另起一段以便区分）",
        "runner_sha256": args.runner_sha256,
        "executed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    print("verbatim transcription appended to", proof["target"])
    print("source_block_sha256:", proof["source_block_sha256"])
    print("copied_region_sha256:", proof["copied_region_sha256"])
    print("byte_equal:", proof["byte_equal"])
    print("appended_bytes:", proof["appended_bytes"])
    if args.proof_out:
        with open(args.proof_out, "w", encoding="utf-8") as handle:
            json.dump(proof, handle, ensure_ascii=False, indent=1)
        print("proof ->", args.proof_out)
    return 0 if proof["byte_equal"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
