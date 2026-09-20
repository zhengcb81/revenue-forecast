"""Round-4 append-only corrections (carry condition C1) + the C2 cross-references.

Rules enforced by this script:
  * APPEND ONLY: no existing line is ever rewritten or deleted; every correction is
    a new block inserted next to the text it corrects, and the stale value stays
    visible as history.
  * IDEMPOTENT: each block carries a unique marker; a second run reports SKIP
    instead of inserting twice.
  * ANCHORED: each insertion point is located by a unique line prefix; if the
    anchor is missing or ambiguous the file is left untouched and the run fails.
  * BYTE DISCIPLINE: line endings are preserved (decision.md/review.md are CRLF).

Truth used by every block (recomputed, not copied from prose):
  evidence/lock-and-legacy.txt line 6 (F-LK2 record) == raw runs in
  evidence/run/F-LK2-r{1..5}/  =>  finals [16, 35, 10, 56, 18] =>
  lost_updates [184, 165, 190, 144, 182], range [144, 190], expected 200.
  See sim/verify_flk2.py and evidence/flk2-recompute.txt (13/13 PASS).
"""

from __future__ import annotations

import io
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRLF = "\r\n"

MARK_A = "更正（C1 关闭；2026-09-20 追加，原文一字未删）"
MARK_B = "O-3 追加登记（C2 = owner 裁定项"
MARK_C = "OPEN-3 交叉引用（C2 登记；2026-09-20 追加）"
MARK_D = "C1 关闭（2026-09-20 追加）**：上表最后一行的"
MARK_E = "更正（C1 关闭；2026-09-20 追加，上表 P3-4 行原文保留）"

BLOCK_A = [
    "> **" + MARK_A + "**：上面第 5 条引用的 finals `[12, 19, 7, 26, 43]` ⇒ lost_updates",
    "> `[197, 185, 191, 198, 14]` 是**过时值**，不是最终证据轮的实测值；该组自身也不相容",
    "> （`expected - finals = [188, 181, 193, 174, 157]`，与它同处给出的 `[197, 185, 191, 198, 14]` 不等）。",
    "> **最终证据轮的实测真值**（权威记录：`evidence/lock-and-legacy.txt` **第 6 行**的 F-LK2 记录；并与原始运行目录",
    "> `evidence/run/F-LK2-r{1..5}/counter.txt` 逐轮一致）：finals `[16, 35, 10, 56, 18]` ⇒ lost_updates",
    "> `[184, 165, 190, 144, 182]`，`lost_updates_range = [144, 190]`，`expected = 200`（8 进程 × 25 轮），",
    "> 五轮的 `lock_acquisitions` 全为 0 且 `use_lock=false`。",
    "> **复算命令与原始输出**：`& $PY -B sim/verify_flk2.py` ⇒ `evidence/flk2-recompute.txt`（13/13 检查通过：",
    "> A1–A8 逐轮从原始运行目录复算并与记录字段比对，B1–B4 复核记录内部算术，C1 证明上面那组过时数字",
    "> 不可能来自 `expected=200` 的任何一轮）。",
    "> 第 5 条的**结论不变**（\"只能定性\"、只断言 `final != expected`）；本条只更正数字，",
    "> 不放宽任何断言、不改冻结 oracle 的期望值。上表 §14 F-I04C-13 行与本条引文中的 `[12,19,7,26,43]`、",
    "> 以及\"更早一轮 261/200 的撕裂写\"均作为**历史**保留（261/200 不在最终证据轮内），不删除、不改写。",
]

BLOCK_B = [
    "- **" + MARK_B + "；2026-09-20）**：本轮把 O-3 显式登记为 **owner 门 = C2**，两项待裁：",
    "  （a）等待上限常数 60（`lock_budget_for(x)=min(x,60)`）的**命名与边界验收**（原文见上一条，",
    "  以及 §14「OPEN-3（复核建议）」段）；",
    "  （b）**`worker-pause` 是否允许留在锁内**（本卡维持锁内；把 H 降到只含 `worker-status` 需要改变语义，",
    "  见 §14 F-I04C-12 末段与 §4 的取舍）。",
    "  条目落盘于 `handoff.json`：`review_carry_conditions.C2_OPEN3_owner_gate`、`owner_gates[0]`、`open_questions`；",
    "  并与 §12 的「ADR-2 锁预算（v1.2 定稿）与 OPEN-3」段交叉引用。",
    "  **这是 owner 的裁定项，不是实现项；它不阻塞 `accepted_scoped` 的签收**，也不改动任何 ADR 文本",
    "  （裁定前实施方一律按 60 执行；本卡内核已冻结该值并记录在实际运行日志里）。",
]

BLOCK_C = [
    "**" + MARK_C + "**：上文的 `lock_budget_for(x)=min(x,60)` 与上限常数 60 登记为 **OPEN-3 = owner 门（C2）**。",
    "条目在 `handoff.json.review_carry_conditions.C2_OPEN3_owner_gate` 与 `handoff.json.owner_gates`；",
    "正文见 §8 O-3（含紧随其后的\"追加登记\"条）与 §14「OPEN-3（复核建议）」段。两项待裁：",
    "（a）60 的命名与边界验收；（b）`worker-pause` 是否留在锁内（本卡维持锁内）。",
    "**不阻塞 `accepted_scoped` 的签收**（属 owner 裁定项，不是实现项）；裁定前实现一律按 60，",
    "任何 ADR 文本与断言强度均不因本条改变。",
]

BLOCK_D = [
    "> **" + MARK_D + "\"已改\"在 r3 只落到 `oracle.md` §7（`sim/patch_r3_docs.py` 的 O3 替换）；",
    "> `decision.md` §13.5 与 `review.md` §1 的 P3-4 行当时**未**被该脚本触及，仍印着过时组 `[12,19,7,26,43]`",
    "> （该值在此只作历史引用保留，不删除）。本轮已在 §13.5（本节上方追加的更正块）与 `review.md` §1",
    "> （该表下方追加的更正块）补齐；两处更正的依据都是自己复算的 `sim/verify_flk2.py` ⇒",
    "> `evidence/flk2-recompute.txt`（13/13 PASS）与 `evidence/lock-and-legacy.txt` 第 6 行的 F-LK2 记录，",
    "> 真值 finals `[16,35,10,56,18]` ⇒ lost `[184,165,190,144,182]`。",
    "> **设计结论、断言强度与冻结 oracle 的期望值均未改动**（本轮只做数值与登记层面的追加式更正）。",
]

BLOCK_E = [
    "> **" + MARK_E + "**：该行\"证据\"栏写的最终轮 finals `[12,19,7,26,43]` 是**过时值**，",
    "> 且自身不相容（`200 - [12,19,7,26,43] = [188,181,193,174,157]` ≠ 同处给出的 lost `[197,185,191,198,14]`）。",
    "> **最终证据轮的实测真值**（实施者独立复算，不采信正文）：finals `[16, 35, 10, 56, 18]` ⇒ lost_updates",
    "> `[184, 165, 190, 144, 182]`，`lost_updates_range = [144, 190]`，`expected = 200`（8 进程 × 25 轮，",
    "> 五轮 `lock_acquisitions` 全为 0）。依据：`& $PY -B sim/verify_flk2.py` ⇒ `evidence/flk2-recompute.txt`",
    "> （13/13 PASS；A1–A8 逐轮从 `evidence/run/F-LK2-r{1..5}/` 的 `counter.txt`、`payload.*.json`、",
    "> `counter.journal.jsonl` 复算，B1–B4 复核记录内部算术，C1 证明过时组不可复现）；",
    "> 权威记录为 `evidence/lock-and-legacy.txt` **第 6 行**的 F-LK2 记录。",
    "> P3-4 的**处置结论不变**（`stress.py` 支持 `repeat`、连跑 5 次、只作定性断言、输出 `determinism` 字段）：",
    "> 本条只更正数字。\"更早一轮 261/200 的撕裂写\"与该过时组作为**历史**保留（261/200 不在最终证据轮内），",
    "> 不删除、不改写，也不放宽断言。",
]


def load(path):
    with io.open(path, "r", encoding="utf-8", newline="") as handle:
        return handle.read()


def save(path, text):
    with io.open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def insert(text, prefix, block, marker, eol, before=False):
    """Insert `block` after (or before) the single line starting with `prefix`."""
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


def main():
    ok = True

    path = os.path.join(ATTEMPT, "decision.md")
    text = load(path)
    print("decision.md")
    text, a = insert(text, "**结论只能是定性的", BLOCK_A, MARK_A, CRLF)
    text, b = insert(text, "- **O-3（v1.2 新增）**", BLOCK_B, MARK_B, CRLF)
    text, c = insert(text, "探针 ≤ min(20,相位预算)", BLOCK_C, MARK_C, CRLF)
    text, d = insert(text, "| F-LK2 数字（三处三组） |", BLOCK_D, MARK_D, CRLF)
    ok &= a and b and c and d
    if a or b or c or d:
        save(path, text)
        print("  wrote decision.md (append-only blocks: 4)")

    path = os.path.join(ATTEMPT, "review.md")
    text = load(path)
    print("review.md")
    text, e = insert(text, "## 2. v1 报告中的错误表述", BLOCK_E, MARK_E, CRLF, before=True)
    ok &= e
    if e:
        save(path, text)
        print("  wrote review.md (append-only blocks: 1)")

    print("all_ok =", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
