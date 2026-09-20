"""Append the round-4 recovery section to recovery/README.md.

Kept in recovery/ (which is not part of the hashes.txt manifest) on purpose: the
section documents how this round was produced, and the file it edits is itself
hashed by sim/freeze_evidence.py.  Line endings are preserved (this file is LF).

Idempotent: stops if the section marker is already present.
Run:  & $PY -B recovery/round4-append-readme.py
"""

from __future__ import annotations

import io
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ATTEMPT, "recovery", "README.md")
MARKER = "## 5. 第 4 轮（2026-09-20）"

SECTION = """
## 5. 第 4 轮（2026-09-20）：C1 追加式更正 + C2 登记（本轮只动文本/证据账）

### 5.1 改了什么、为什么

上一轮复核 verdict = `accepted_scoped`，携带两个条件：**C1（必须关闭）** —— `decision.md` §13.5 与 `review.md` §1 的
P3-4 行仍印着**过时的 F-LK2 数值**；**C2（只登记）** —— OPEN-3 = 60 s 等待上限常数（`lock_budget_for(x)=min(x,60)`）
的命名/边界验收，以及 `worker-pause` 是否留在锁内，属 **owner 裁定项**。

本轮只做数值与登记层面的**追加式**更正：**不改任何设计结论、不放宽任何断言、不改冻结 oracle 的期望值**；
`PLAN\\reviews\\` 一个字节未动，三个生产仓库只读（无 `git add`、无 commit）。

### 5.2 C1 的真值（自己从证据复算，不采信正文）

- **权威记录**：`evidence/lock-and-legacy.txt` **第 6 行**的 F-LK2 记录（含 `finals`/`lost_updates`/
  `lost_updates_range`/`determinism`）。
- **独立复核源**（不是同一份记录的转抄）：`evidence/run/F-LK2-r{1..5}/` 的 `counter.txt`、
  `payload.{0..7}.json`、`counter.journal.jsonl`。
- **真值**：finals `[16, 35, 10, 56, 18]` ⇒ lost_updates `[184, 165, 190, 144, 182]`，
  `lost_updates_range = [144, 190]`，`expected = 200`（8 进程 × 25 轮），五轮 `lock_acquisitions` 全为 0、
  `use_lock=false`。**与卡片给的数字一致，无冲突。**
- **过时组**（`decision.md` §13.5 第 5 条与 `review.md` §1 P3-4 行的原文，现作为历史保留）：
  finals `[12, 19, 7, 26, 43]` ⇒ lost `[197, 185, 191, 198, 14]`；该组**自身不相容**
  （`200 - [12,19,7,26,43] = [188,181,193,174,157]` ≠ 同处给出的 lost）。

```powershell
# 1) 复算 F-LK2 真值（读原始 run 目录 + 记录；输出 evidence/flk2-recompute.txt）
& $PY -B "$A\\sim\\verify_flk2.py"            # 13/13 PASS，退出码 0

# 2) 追加式更正两份文本（幂等：第二次运行全部 SKIP）
& $PY -B "$A\\sim\\patch_r4_docs.py"

# 3) handoff.json：C1 -> closed、C2 -> owner gate
& $PY -B "$A\\sim\\patch_r4_handoff.py"

# 4) 证明"只增不改"：删掉插入块后重建的 sha256 == 改前 sha256
& $PY -B "$A\\sim\\verify_r4_appendonly.py"    # APPEND-ONLY CONFIRMED，退出码 0

# 5) 冻结哈希账（排除自身与 run-summary.json，按本目录既有口径）
& $PY -B "$A\\sim\\freeze_evidence.py"
```

### 5.3 更正落在哪（追加式，原文一字未删、未静默改写）

| 位置 | 追加内容 |
|---|---|
| `decision.md` §13.5 第 5 条之后 | 更正块：过时值点名 + 真值 + 复算命令 + 证据文件行号 + "结论不变" |
| `decision.md` §8 O-3 之后 | "O-3 追加登记（C2 = owner 裁定项）"，含"**不阻塞 `accepted_scoped` 的签收**" |
| `decision.md` §12「ADR-2 锁预算（v1.2 定稿）与 OPEN-3」段之后 | OPEN-3/C2 交叉引用（指向 §8 O-3、§14 与 `handoff.json`） |
| `decision.md` §14 F-I04C-13 表之后 | C1 关闭说明：r3 的 `patch_r3_docs.py` 只落到 `oracle.md` §7，§13.5/`review.md` 当时未触及 |
| `review.md` §1 表之后 | P3-4 行的更正块（该行原文保留；"261/200"与过时组作为历史保留） |
| `handoff.json` | 新增 `review_carry_conditions`（C1 `closed` + C2 `open_owner_ruling`）与 `owner_gates[0]`；`open_questions` 追加一条 C2 登记；`revision`/`next_action`/`reviewer_status` 各追加一句；`commands_executed`/`expected_exit_codes`/`raw_exit_codes` 各加一项（9/9/9 保持平行） |
| `recovery/README.md` | 本节（§5） |
| 新增文件 | `sim/verify_flk2.py`、`sim/verify_r4_appendonly.py`、`sim/patch_r4_docs.py`、`sim/patch_r4_handoff.py`、`evidence/flk2-recompute.txt`、`recovery/round4-pre-hashes.txt`、`recovery/round4-append-readme.py`、`recovery/round4-post-hashes.txt` |

### 5.4 改前 hash → 改后 hash（sha256）

| 文件 | 改前 | 改后 |
|---|---|---|
| `decision.md` | `bb9bb0f401e573409842afd7bfc7a17eb3d5dd52b79e134f41417f1aa0a6f479` | `f1a2396c13bfe30ca71fc4d2b7178f8807f91cd230c5260251ee64bcea7f8622` |
| `review.md` | `8cc116bced471b721bf28f1a15f9daf3e875e720ad9cb3e7eb0ebd3966289a57` | `d416b73a662c8c4e5f168b0c94bb34f7e0e48e1f31e4fc921f3da5e36988d2be` |
| `handoff.json` | `397eaa07749c4dfe57cb3da2473d4a5937dc9359a29ce2e84e3035c4a5364b28` | `ac418ac661e278ff014af7c80d951d7db106bb091e839a01353f3fcfea7aa378` |
| `evidence/hashes.txt` | `6b61e8da55cbdf2590c55007c0617fa2b9d0de68b914f8c4a73c169013f520d1` | 见 `recovery/round4-post-hashes.txt`（**自指不可能**：`hashes.txt` 由 `sim/freeze_evidence.py` 写，按 P3-3 的既有口径排除自身与 `run-summary.json`） |
| `recovery/README.md`（本文件） | `804b2dc938f866d8355d920a7ef3e2fd15850e9c104ca248123a79c462aa1930` | 见 `recovery/round4-post-hashes.txt` 与 `evidence/hashes.txt`（本文件不能自指） |

`recovery/round4-pre-hashes.txt` 是**改前**快照（含 `PLAN\\reviews\\` 的 mtime 普查指纹
`6152372047dcbe9e363182240c03a9845c9213bd72fb85bf2468c4632b27672d`，285 个文件）；
`recovery/round4-post-hashes.txt` 在最后一次冻结之后捕获，两者对照即可看出本轮到底动了哪些字节。

### 5.5 如何复核这一轮

1. **复算**：`verify_flk2.py` 必须 13/13 PASS、退出码 0，且 `evidence/flk2-recompute.txt` 与哈希账一致。
2. **只增不改**：`verify_r4_appendonly.py` 必须打印 `APPEND-ONLY CONFIRMED`（它删掉插入块后重建的 sha256
   与 §5.4 的"改前"列逐字相等）。
3. **幂等**：重跑 `patch_r4_docs.py` / `patch_r4_handoff.py` 必须全部 SKIP，且四个被改文件哈希不变。
4. **哈希账**：`freeze_evidence.py` 退出码 0，`evidence/hashes.txt` 末行 `PRODUCTION_UNCHANGED=true`。
5. **边界**：本轮**不得**改动任何 ADR 文本、`oracle.md` 的期望值、`PLAN\\reviews\\**`、三个生产仓库
   （`recovery/round4-p*-hashes.txt` 的对照与 `PRODUCTION_UNCHANGED=true` 是这条的证据）。

### 5.6 本轮**未**做（留给 reviewer / owner / 后续卡）

- `handoff.json.status` 仍为 `review_pending`：是否改判/签收由 reviewer/owner 决定，实施者不改。
- **C2（OPEN-3）不实现**：等 owner 裁定；裁定前实现一律按 60（内核已冻结该值）。
- `review.md` §0/§5 的 reviewer 区未动（实施者不得代填判决）。
- PLAN 根级 `progress.md`/`task_plan.md` 里"I-04-C 返工中 / changes_required"的旧计数**不在本卡写入范围**
  （只允许写 attempt 目录），未改 —— 需要 PLAN 级同步时由父代理处理。
"""


def main():
    with io.open(README, "r", encoding="utf-8", newline="") as handle:
        text = handle.read()
    if MARKER in text:
        print("SKIP already applied")
        return 0
    if not text.endswith("\n"):
        text += "\n"
    with io.open(README, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + SECTION)
    print("appended recovery section 5 (%d chars)" % len(SECTION))
    return 0


if __name__ == "__main__":
    sys.exit(main())
