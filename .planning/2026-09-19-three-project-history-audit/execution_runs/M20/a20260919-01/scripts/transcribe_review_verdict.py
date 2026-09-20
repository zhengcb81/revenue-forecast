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

NOTE_CARD_R3 = """

### 实现者附注（非 reviewer 文字，另起一段以便区分）

本段由 M17-M20 attempt 的实现 session 追加，**不是** reviewer 的原文。

**世代边界（重要）**：上方法庭级判定由独立 reviewer 针对**冻结世代
`2026-09-20T03:44:34Z–03:44:43Z`**（四卡最后一次收尾 + V 单元）作出，只对该世代有效。本转录以及
r3 遗留项 P3-A…P3-D 的处置都发生在该世代**之后**，故本卡目录此后存在更新的记录；判定所依据的世代值
已用**只读快照**保存于 `evidence/{card}/generation_20260920T034434Z/`（含当时的
`evidence_hashes.json`、`after/final_deliverable_hashes.json`、`after/hash_table_verification.json`、
`handoff.json`、`commands.json`、`process_history.json`、`qualification.json`、`revision_r2.json`、
`source_manifest.json` 及各自 sha256），可据此逐条比对"哪些文件在判定世代之后被改写"。

**流程要求（reviewer 明示并登记为约束）**：宣布本卡完成后**不得再写入 attempt 目录**；任何后续写入都会
使本判定失效、必须重新点审。若确需写入，应先保存世代快照，写入后重跑 `run_closing.py`
（其内含 V 单元）并重新登记世代。

**r3 遗留项处置（只涉及脚本与记录文件；`oracle.md` 未再改动）**：P3-A 已让 `run_closing.py` 在收尾单元
之后**同一命令内**执行 `verifier_units()`（含 `V-verify-hash-tables`），并在 `recovery/closing_run.json`
记录两阶段单元清单与 raw rc；P3-B 已把无追加节分支的演示截断点改到 **base 长度**处（并加 `applicable`
标记）；P3-C/P3-D 以**文档**形式落在 `rc_namespace.json` 与批次交接（**不改 `run_card.py` 一个字节**，
以保持 reviewer 已验证的 runner sha `94619a98…` 不变）；P3-E 的世代覆盖事实登记在批次交接与
`generation_manifest.json`。`disclosure_adaptation` 与 `accuracy` **未动**。
"""

NOTE_BATCH_R3 = """

### 实现者附注（非 reviewer 文字，另起一段以便区分）

本段由 M17-M20 attempt 的实现 session 追加，**不是** reviewer 的原文。

**世代边界**：第 9 节的终判针对冻结世代 **`2026-09-20T03:44:34Z–03:44:43Z`**，只对该世代有效；
本次转录与 r3 遗留项处置在其后发生。各卡目录内已保存只读世代快照
`evidence/<CARD>/generation_20260920T034434Z/`，批次层面另见 `generation_manifest.json`。

**流程要求（登记为约束）**：宣布完成后**不再写入 attempt 目录**；再写入即判定失效、需重新点审。

**r3 遗留项 P3-A…P3-E 的落点**：P3-A `scripts/run_closing.py`（收尾后同一命令内跑 V，`recovery/closing_run.json`
记录两阶段 rc）；P3-B `scripts/pack_card.py` 的无追加节演示分支（截断点改到 base 长度 + `applicable`）；
P3-C/P3-D `rc_namespace.json` 的 `cases_json_schema_constraint` 与 `counting_semantics`（**未改
`run_card.py`**，以保持 reviewer 已验证的 runner sha `94619a98…` 逐字节不变）；P3-E 见本节与
`generation_manifest.json` 的"世代覆盖"记录。**`oracle.md` 未再改动**。

**本批最后一次写入之后的纪律**：生产 hash 是可被外部 git 操作改变的量（见 §9.2 与
`_isolation_incidents/20260920-precommit-stash-production-rollback/INCIDENT.md`）：时点限定、发现不一致
先记录并上报、**永不**改期望或冻结件适配、引用时写明被测副本 hash。
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


def extract_by_lines(report_bytes: bytes, first_line: int, last_line: int) -> bytes:
    """Byte-exact slice of whole lines [first_line, last_line] (1-based, inclusive).

    Used for the r3 report, whose verdict text itself mentions a ```markdown fence, so naive fence
    scanning would cut the block short.  Explicit line numbers are also what the reviewer asked to be
    recorded as the transcription landing point.
    """
    lines = report_bytes.splitlines(keepends=True)
    if not (1 <= first_line <= last_line <= len(lines)):
        raise SystemExit("REFUSED: line range %d:%d outside the report (%d lines)"
                         % (first_line, last_line, len(lines)))
    return b"".join(lines[first_line - 1:last_line])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--block-index", type=int, default=None)
    parser.add_argument("--block-lines", default=None,
                        help="explicit source line range FIRST:LAST (1-based, inclusive)")
    parser.add_argument("--target", required=True)
    parser.add_argument("--note-mode", choices=("card", "batch", "r3-card", "r3-batch"), required=True)
    parser.add_argument("--runner-sha256", default=None)
    parser.add_argument("--generation-boundary", default=None)
    parser.add_argument("--proof-out", default=None)
    args = parser.parse_args()

    if (args.block_index is None) == (args.block_lines is None):
        print("REFUSED: give exactly one of --block-index or --block-lines")
        return 3

    with open(args.report, "rb") as handle:
        report = handle.read()
    if args.block_lines:
        first_line, last_line = (int(x) for x in args.block_lines.split(":"))
        block = extract_by_lines(report, first_line, last_line)
        source_range = {"first_line": first_line, "last_line": last_line}
    else:
        blocks = extract_blocks(report)
        if args.block_index >= len(blocks):
            print("REFUSED: report has only %d markdown blocks" % len(blocks))
            return 3
        block = blocks[args.block_index]
        source_range = {"fenced_block_index": args.block_index}

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
            "source_range": source_range,
            "generation_boundary": args.generation_boundary,
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

    note = {"card": NOTE_CARD, "batch": NOTE_BATCH,
            "r3-card": NOTE_CARD_R3, "r3-batch": NOTE_BATCH_R3}[args.note_mode]
    if args.note_mode in ("card", "r3-card"):
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
    block_first_line = after[:start].count(b"\n") + 1
    block_last_line = block_first_line + block.count(b"\n") - 1
    proof = {
        "card_id": args.card,
        "target": os.path.abspath(args.target),
        "report": os.path.abspath(args.report),
        "source_range": source_range,
        "generation_boundary": args.generation_boundary,
        "verbatim": True,
        "source_block_sha256": sha256_bytes(block),
        "copied_region_sha256": sha256_bytes(copied),
        "byte_equal": sha256_bytes(block) == sha256_bytes(copied),
        "source_block_bytes": len(block),
        "copied_region_bytes": len(copied),
        "target_bytes_before": len(before),
        "target_bytes_after": len(after),
        "appended_bytes": len(after) - len(before),
        "landing_point": {
            "target_byte_offset_start": start,
            "target_byte_offset_end": start + len(block),
            "target_first_line": block_first_line,
            "target_last_line": block_last_line,
            "target_total_lines": after.count(b"\n") + 1,
        },
        "note_appended_after_the_verbatim_block": True,
        "note_label": "实现者附注（非 reviewer 文字，另起一段以便区分）",
        "runner_sha256": args.runner_sha256,
        "executed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    print("verbatim transcription appended to", proof["target"])
    print("source_range:", source_range)
    print("source_block_sha256:", proof["source_block_sha256"])
    print("copied_region_sha256:", proof["copied_region_sha256"])
    print("byte_equal:", proof["byte_equal"])
    print("landing_point:", proof["landing_point"])
    print("appended_bytes:", proof["appended_bytes"])
    if args.proof_out:
        _atomic_dump(args.proof_out, proof)
        print("proof ->", args.proof_out)
    return 0 if proof["byte_equal"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
