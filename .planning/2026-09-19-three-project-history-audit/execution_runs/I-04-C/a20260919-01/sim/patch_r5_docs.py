"""Round-5 closeout corrections: erratum E1 in three documents + the reviewer's
verdict pasted verbatim into review.md section 5.

Append-only rules of this attempt:
  * no existing line is rewritten or deleted; every correction is a NEW block next
    to the text it corrects and the stale value stays visible as history;
  * idempotent (unique marker per block), anchored (unique line prefix, single hit
    or the file is left untouched and the run fails);
  * line endings preserved (decision.md / review.md / oracle.md are CRLF).

The verdict block is NOT transcribed by hand: it is read out of
evidence/r5-reviewer-closeout-report.md (the reviewer's report, copied byte-for-byte
from %TEMP%\\closeout-review-20260920-035508\\REPORT.md), between the fence that
follows the heading '### > 可原样粘贴进 `review.md §5` 的裁决正文'.

Run:  & $PY -B sim/patch_r5_docs.py
"""

from __future__ import annotations

import hashlib
import io
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRLF = "\r\n"
REPORT_COPY = os.path.join(ATTEMPT, "evidence", "r5-reviewer-closeout-report.md")
VERDICT_HEADING = "可原样粘贴进 `review.md §5` 的裁决正文"
VERDICT_MARKER = "## 5. reviewer 结论（独立 reviewer session，2026-09-20）"
# Only the appended verdict carries this line (VERDICT_MARKER also appears inside
# BLOCK_R5's pointer text, so it cannot be used as the appendix's own marker).
APPENDIX_MARKER = "- reviewer：独立 reviewer session（本次收尾复核），2026-09-20。"

MARK_R1 = "E1 更正（收尾复核；2026-09-20 追加，原行一字未删）"
MARK_D1 = "E1 更正（收尾复核；2026-09-20 追加，上行原文保留）"
MARK_O1 = "E1 更正，收尾复核 2026-09-20 追加"
MARK_R5 = "本节已填写（2026-09-20）"

BLOCK_R1 = [
    "> **" + MARK_R1 + "**：上表\"必修 2\"行的证据栏写 \u201c`evidence/phase-wall.txt`（F-L2d 8 并发最大等待",
    "> 9.87 s、相位墙 13.2 s）\u201d，与该文件的实际内容不符：`evidence/phase-wall.txt` 的 F-L2d 记录是",
    "> `max_lock_wait_seconds = 9.782719`、`phase_wall_seconds = 13.386`，即 **9.78 s / 13.4 s**",
    "> （9.87 是把 9.782719 末两位换位的转录错误）。该数字的权威来源只有 `evidence/phase-wall.txt`",
    "> 一处一行一条记录；本行原文保留，取值以更正块为准。",
    "> 同一过时数字还出现在 `decision.md` §14 F-I04C-12 段与 `oracle.md` R3-2 段（两处均已追加同一更正），",
    "> 以及 `handoff.json.results.queue_cost`（已就地追加 erratum 标注）。**设计结论不变**：",
    "> \"8 并发的锁等待接近 10 s、相位墙约 13 s、排队会吃掉下载预算\"的量级结论与 ADR-2 的取舍都不受影响。",
]

BLOCK_D1 = [
    "> **" + MARK_D1 + "**：上行的 \"9.87 s / 13.2 s\" 是转录错误；`evidence/phase-wall.txt` 的 F-L2d 记录为",
    "> `max_lock_wait_seconds = 9.782719`、`phase_wall_seconds = 13.386` ⇒ **9.78 s / 13.4 s**。",
    "> 同一更正在 `oracle.md` R3-2、`review.md` §6 与 `handoff.json.results.queue_cost` 同步。",
    "> 量级结论（等待接近 10 s、相位墙约 13 s、排队消耗下载预算）与 ADR-2 的取舍**不变**；",
    "> 本卡不改任何期望值或断言强度。",
]

BLOCK_O1 = [
    "  （**" + MARK_O1 + "**：上面这条 bullet 里的 \"9.87 s / 13.2 s\" 是转录错误；`evidence/phase-wall.txt` 的",
    "  F-L2d 记录为 `max_lock_wait_seconds = 9.782719`、`phase_wall_seconds = 13.386` ⇒ 9.78 s / 13.4 s。",
    "  只更正数字，R3-2 的模型与结论不变；同一更正同步到 `decision.md` §14 F-I04C-12、`review.md` §6",
    "  与 `handoff.json.results.queue_cost`。本注记插在该 bullet 结束之后，不改动上面的任何一行。）",
]

BLOCK_R5 = [
    "> **" + MARK_R5 + "**：独立 reviewer 的裁决正文在本文件**末尾逐字粘贴**",
    "> （标题为 `" + VERDICT_MARKER + "`）。上面的 \"留空 —— 由独立 reviewer 填写\" 是 r3 的状态说明，",
    "> 下面五行是当时的模板：作为历史保留，不要当作已填写的版本。",
]


def load(path):
    with io.open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def save(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def insert(text, prefix, block, marker, eol, before=False):
    if marker in text:
        print("  SKIP  already applied (%s)" % marker.encode("ascii", "backslashreplace").decode("ascii"))
        return text, True
    lines = text.split(eol)
    hits = [i for i, line in enumerate(lines) if line.strip().startswith(prefix)]
    if len(hits) != 1:
        print("  FAIL  anchor found %d times: %s"
              % (len(hits), prefix.encode("ascii", "backslashreplace").decode("ascii")))
        return text, False
    index = hits[0] if before else hits[0] + 1
    lines[index:index] = (block + [""]) if before else ([""] + block)
    return eol.join(lines), True


def read_verdict_block():
    """Read the reviewer's paste-ready verdict verbatim out of the report copy."""
    text = io.open(REPORT_COPY, encoding="utf-8").read()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    lines = text.split("\n")
    heading = None
    for index, line in enumerate(lines):
        if VERDICT_HEADING in line and line.lstrip().startswith("#"):
            heading = index
            break
    if heading is None:
        raise SystemExit("paste heading not found in " + REPORT_COPY)
    fence = None
    for index in range(heading + 1, len(lines)):
        if lines[index].strip() == "```":
            fence = index
            break
    if fence is None:
        raise SystemExit("opening fence not found after the paste heading")
    block = []
    for line in lines[fence + 1:]:
        if line.strip() == "```":
            break
        block.append(line)
    else:
        raise SystemExit("closing fence not found")
    if not block or block[0].strip() != VERDICT_MARKER:
        raise SystemExit("verdict block does not start with the expected heading")
    if "reviewer：独立 reviewer session" not in block[-1]:
        raise SystemExit("verdict block does not end with the reviewer signature line")
    return block, digest, len(lines)


def build_appendix(verdict, digest):
    provenance = (
        "> **本节已由独立 reviewer 填写（2026-09-20）；上面的 \"留空\" 抬头与五行模板是 r3 状态，作为历史保留。**\n"
        "> 下面是 reviewer 报告里\"可原样粘贴进 `review.md §5`\"的裁决正文，由 `sim/patch_r5_docs.py` "
        "从 `evidence/r5-reviewer-closeout-report.md` 的代码块中**逐字读出并粘贴，实施者未改一字**\n"
        "> （源文件 sha256 `%s`，副本来自 reviewer 的 `%%TEMP%%\\closeout-review-20260920-035508\\REPORT.md`）。"
        % digest)
    body = provenance + "\n\n" + "\n".join(verdict) + "\n"
    return body.replace("\n", CRLF)


def main():
    ok = True
    verdict, digest, report_lines = read_verdict_block()
    print("verdict block read from evidence/r5-reviewer-closeout-report.md: %d lines, sha256 %s"
          % (len(verdict), digest[:16]))

    path = os.path.join(ATTEMPT, "review.md")
    text = load(path)
    print("review.md")
    text, a = insert(text, "| **OPEN-3**（复核建议，已采纳）", BLOCK_R1, MARK_R1, CRLF)
    text, b = insert(text, "## 5. reviewer 结论（**留空", BLOCK_R5, MARK_R5, CRLF)
    if APPENDIX_MARKER in text:
        print("  SKIP  verdict appendix already pasted")
        c = True
    else:
        if not text.endswith(CRLF):
            text += CRLF
        text = text + CRLF + build_appendix(verdict, digest)
        print("  appended the reviewer verdict verbatim (%d lines)" % len(verdict))
        c = True
    ok &= a and b and c
    if a or b or c:
        save(path, text)
        print("  wrote review.md")

    path = os.path.join(ATTEMPT, "decision.md")
    text = load(path)
    print("decision.md")
    text, d = insert(text, "高并发时下载预算会被排队吃掉", BLOCK_D1, MARK_D1, CRLF)
    ok &= d
    if d:
        save(path, text)
        print("  wrote decision.md")

    path = os.path.join(ATTEMPT, "oracle.md")
    text = load(path)
    print("oracle.md")
    # Anchor = the LAST line of the R3-2 bullet (the first version of this patch
    # anchored on the line that contains the stale numbers, which sits in the
    # middle of the bullet and split it; see recovery/round5-relocate-oracle-note.py).
    text, e = insert(text, "**不得**通过放宽锁或跳过互斥来规避", BLOCK_O1, MARK_O1, CRLF)
    ok &= e
    if e:
        save(path, text)
        print("  wrote oracle.md")

    print("all_ok =", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
