"""Append the round-5 recovery section to recovery/README.md.

Kept in recovery/ (not part of the hashes.txt manifest) for the same reason as the
round-4 appender: the file it edits is itself hashed by sim/freeze_evidence.py.
Line endings are preserved (this file is LF).  Idempotent.

Run:  & $PY -B recovery/round5-append-readme.py
"""

from __future__ import annotations

import io
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ATTEMPT, "recovery", "README.md")
MARKER = "## 6. 第 5 轮（2026-09-20）"

SECTION = """
## 6. 第 5 轮（2026-09-20）：收尾复核的两条 erratum + 证据缺口登记 + reviewer 裁决入卷

### 6.1 改了什么、为什么

收尾复核 verdict = **`accepted_scoped`（限本 attempt 的设计文本与模拟结果）**，C1 关闭、C2 仍为 owner 门且不阻塞签收、
三项 still-required 逐条关闭。复核人另提 **两条文字/断言层更正（E1、E2）**（"不改变裁决，请做掉"）与两条证据缺口。
本轮**只做**这四件事，未改任何数值结论、未改任何期望值、生产三仓零写入、无 commit。

### 6.2 E1（P3 文字性 erratum）：F-L2d 的相位墙数字

- **缺陷**：`review.md` §6"必修 2"行证据栏写 "F-L2d 8 并发最大等待 9.87 s、相位墙 13.2 s"。
- **权威值**：`evidence/phase-wall.txt` **第 9 行** F-L2d 记录 = `max_lock_wait_seconds: 9.782719`、
  `phase_wall_seconds: 13.386` ⇒ **9.78 s / 13.4 s**（9.87 是把 9.782719 末两位换位的转录错误）。
- **更正位置**（全部追加式，原行一字未删）：`review.md` §6 表后更正块；`decision.md` §14 F-I04C-12 段后更正块；
  `oracle.md` R3-2（追加节内）更正注；`handoff.json.results.queue_cost` 就地追加 erratum 标注。
- **不变的**：量级结论（8 并发锁等待接近 10 s、相位墙约 13 s、排队吃掉下载预算）与 ADR-2 的取舍。

### 6.3 E2（P3 断言强度）：F-T4 的两处"永不失败"子句

- **缺陷**（复核人给出最小复现）：`sim/cases_timeout.py` 的 refcount 检查里
  `not any(lease in successful_ids is False for lease in view["entries"])` 是 Python **链式比较**，
  等价 `(lease in successful_ids) and (successful_ids is False)` ⇒ **恒为 False**，于是 `not any(...)` **恒真**、
  该子句永不失败；`:213-216` 的"queue wait is reported"断言传的是字面 `True`（只是记录装置，不是断言）。
- **改法**（`sim/cases_timeout.py`，检查名与条数不变，F-T4 仍是 8 条）：
  ① 显式量词 `all(lease in successful_ids …) and all(lease not in timed_out_ids …) and view["entries"] != []`；
  ② 队列等待改为真实比较：每个成功参与者必须**真的报告了** `lock_wait`，且 `0.0 <= wait <= budget + 0.001`
  （1 ms = 上报分辨率）；
  ③ winners/joiners 由"只比长度"改成**集合相等 + 互斥**。
- **变异证据**：`sim/verify_r5_assertions.py` ⇒ `evidence/r5-assertion-mutation.txt`（**16/16 期望成立**）。
  它**不重打**表达式，而是从 `sim/cases_timeout.py` 现场抽取当前表达式再求值：
  历史子句在 4/4 恶意视图（含超时 lease、空视图、垃圾 id、全员入表）下**全为 True**（证明其恒真）；
  历史整条在"succeeded/timed_out 重叠"时仍为绿而新子句转红（盲区被补上）；
  缺 `lock_wait`、等待超预算、动作重复计数三种注入都会让**现行**子句转红。
- **加强后重跑**：`& $PY -B "$A\\sim\\scheduler.py" run F-T1 F-T2 F-T3 F-T4 --root "$A\\evidence\\recheck\\run"
  --log "$A\\evidence\\r5-timeout-suite-recheck.txt"` ⇒ 退出码 **0**，F-T1/T2/T3/T4 = **7/3/6/8 条检查全 PASS**，
  raw log 落盘（本次调度结果是 P0/P2/P3/P4 超时、P1/P5 成功，等待 0.0 s / 0.676 s）。
  **冻结证据 `evidence/run/F-T4/` 未被覆盖**（换了 `--root`），`evidence/failures.txt`、`run-all.txt` 未改。

### 6.4 证据缺口登记：`CMD-I04C-08` 没有原始日志（未重测）

- **声明**：`commands.json:233` 与 `handoff.json` 写 "pytest -k 'pause or resume' on the byte-identical iso source:
  8 passed / 109 deselected"。
- **缺口（已自查证实）**：在 attempt 内（排除 `iso/`）检索 `deselected`，**只命中 `commands.json` 与 `handoff.json`**
  两个"声明文件"——没有 raw log。
- **复核人的独立复现**：他从 `%TEMP%` 的 iso 副本重跑，得到 `8 passed, 109 deselected in 0.32s`（退出码 0）
  ⇒ **声明为真，但实现者未留证**（本轮不补测，只登记）。
- **今后的规矩（本轮起生效）**：任何"结果被写进交付物"的命令，必须把 raw log 落盘到 `evidence/`
  （本轮新增的三条命令都已照此办理：`r5-timeout-suite-recheck.txt`、`r5-assertion-mutation.txt`、
  `r5-appendonly-proof.txt`）。

### 6.5 reviewer 裁决入卷（`review.md` §5）

`review.md` §5 现已**逐字粘贴**复核人报告里"可原样粘贴进 `review.md §5` 的裁决正文"（52 行）。
粘贴**不是手工转录**：`sim/patch_r5_docs.py` 从 `evidence/r5-reviewer-closeout-report.md`
（复核人报告 `%TEMP%\\closeout-review-20260920-035508\\REPORT.md` 的逐字节副本，
sha256 `9dafd6cf566418cf4b5e1e9c21cb9147902fbe83dccd47147a5d66c20ef678d0`）的代码块中读出后写入。
原 §5"留空 —— 由独立 reviewer 填写"抬头与五行模板**作为历史保留**（其上方已插入指向文末裁决的说明）。
`handoff.json.reviewer_status` 指向该 §5。**`status` 仍为 `review_pending`**：签收不是实施者的事。

### 6.6 改前 hash → 改后 hash（sha256，本轮）

| 文件 | 改前（= 第 4 轮末） | 改后 |
|---|---|---|
| `review.md` | `d416b73a662c8c4e5f168b0c94bb34f7e0e48e1f31e4fc921f3da5e36988d2be` | `910be66954f6250dee6bd8c7f181caa116a64cb52b8286490560f348bc56dde2` |
| `decision.md` | `f1a2396c13bfe30ca71fc4d2b7178f8807f91cd230c5260251ee64bcea7f8622` | `309ba3042073b4826569579d262f9c8e08c0aee045b552bfce21d7ef3dee6461` |
| `oracle.md` | `3594f4d6cbf9b9b20b00c317451a8f8ad2cffe5df4d58664c782a840610a4390` | `c3cb8fb494d957f20b11084c8655947fbab737ca7c6289f8f8b9b14e0e367aa5` |
| `handoff.json` | `ac418ac661e278ff014af7c80d951d7db106bb091e839a01353f3fcfea7aa378` | `291fb1677740f54e19408c344d08f40f5226170f3c97efa28c096e3286fc0014` |
| `sim/cases_timeout.py` | `cc07aa36e623481ccb9ed6a7346f2c18c27e66653e57a8a347d0bcf1172a44de` | `bfca707a8c692f83fb6a09ab4ea386388c6f212bd41fdec9d0bcf1e28df205ca` |
| `evidence/hashes.txt` | `698d6f716fad9e83939045d2b3c9fdf62e615557b7210f7668e9dbeea0cf442e` | 见 `recovery/round5-post-hashes.txt`（自指不可能，口径同 P3-3） |
| `recovery/README.md`（本文件） | `7ad7d2a0dcfff4b5ed5267fcac786f61fac949a0216418ccb1300416cc317c91` | 见 `recovery/round5-post-hashes.txt` 与 `evidence/hashes.txt` |

本轮新增（改后 sha256）：`evidence/r5-reviewer-closeout-report.md` `9dafd6cf566418cf…ef678d0`、
`evidence/r5-assertion-mutation.txt` `c39e8093e83c4f3d…7a52bb08`、
`evidence/r5-timeout-suite-recheck.txt` `900677f666c71502…f17f5712`、
`evidence/r5-appendonly-proof.txt` `6531f05ad9a5a0df…f34f74a4`、
`sim/verify_r5_assertions.py`、`sim/verify_r5_appendonly.py`、`sim/patch_r5_docs.py`、`sim/patch_r5_handoff.py`、
`recovery/round5-pre-hashes.txt`、`recovery/round5-post-hashes.txt`、`recovery/round5-append-readme.py`
（前四个 sim 脚本与四个 evidence 文件都在 `evidence/hashes.txt` 里；`recovery/` 下除 `README.md` 外不入账）。

### 6.7 如何复核这一轮

```powershell
# 1) E2 变异证据（16/16；历史子句恒真、现行子句对每种注入转红）
& $PY -B "$A\\sim\\verify_r5_assertions.py"

# 2) 加强后重跑超时套件（隔离 root，不动冻结证据）
& $PY -B "$A\\sim\\scheduler.py" run F-T1 F-T2 F-T3 F-T4 --root "$A\\evidence\\recheck\\run" `
    --log "$A\\evidence\\r5-timeout-suite-recheck.txt"

# 3) 第 4+5 轮"只增不改"链式证明（最终都回到复核过的原始字节）
& $PY -B "$A\\sim\\verify_r5_appendonly.py"

# 4) 冻结哈希账
& $PY -B "$A\\sim\\freeze_evidence.py"
```

预期：1) `VERDICT: OK (16/16)`；2) 退出码 0 且 F-T1..F-T4 = 7/3/6/8 全 PASS；3) `APPEND-ONLY CONFIRMED FOR
ROUNDS 4 AND 5`；4) 退出码 0 且 `PRODUCTION_UNCHANGED=true`。

**注意（脚本被取代）**：`sim/verify_r4_appendonly.py` 只在"第 4 轮结束时的文本"上成立，本轮之后请改用
`sim/verify_r5_appendonly.py`（它的第 2 段就是第 4 轮展开，等价且更强）。两个脚本都保留，作为各轮的现场记录。

### 6.8 本轮**未**做（明确留给 reviewer / owner / 后续卡）

- `handoff.json.status` 仍为 `review_pending`；`review.md` §0 的"第二轮结论"原文与 §5 旧模板均保留，实施者不写判决。
- **C2（OPEN-3）不实现**：等 owner 裁定；裁定前实现按 60。
- `CMD-I04C-08` 的 raw log **不补测**（按复核人要求只登记；其结论已由复核人在 TEMP 副本复现）。
- 复核人列出的未验证项（生产 attempt 内未重跑、ADR 全文未逐条复核、`hashes.txt` 只做代表性校验、
  F-L4a LIMITATION 与 ADR-10e 并发转让不变式仍未证、真实并发/探针等价性/POSIX-SMB/PID 复用/多线程 scope 未复现）
  **原样承接**在 `review.md` 末段（reviewer 原文）。
- `sim/patch_r3_handoff.py` 里仍写着旧的 `9.87 s / 13.2 s` 字面量（它是第 3 轮的历史脚本，未改；**不要重跑它**，
  否则会把已更正的 `handoff.json` 覆盖回旧值）。
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
    print("appended recovery section 6 (%d chars)" % len(SECTION))
    return 0


if __name__ == "__main__":
    sys.exit(main())
