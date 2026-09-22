# I-14-E review.md — 独立验收（由独立 reviewer 填写；实现者**未**自签）

本文件由实现者留出结构，**结论由 reviewer 写**。实现者身份：I-14-E implementer agent。
`handoff.json.status = review_pending`。

## 0. reviewer 应先读什么（不看实现者的通过摘要）

1. `oracle.md`（冻结于 2026-09-21T20:09:21Z）+ `oracle-addendum-A.md`（运行前追加，只改 N 与臂口径）
   —— 先确认判据是**运行前**写死的。
2. `binding.json` + `evidence/binding_hashes.json` —— 树/锚点/解释器 hash 与相等性。
3. `evidence/frozen_band_raw_record.json` —— 卡片引用的 24×2 观测带的**原始**事件记录。
4. `after/analysis.json` —— 逐假设判定与用到的数字。
5. `after/band-*.json` + `after/band-captures-*/` —— 每次运行的 stdout 与 launcher 事件。
6. `after/child-lifetime-*.json`、`after/wrapper-latency-*.json` —— 独立窗口测量。
7. `after/proposed-test-side-change.md` —— **未施加**的测试侧建议（本 attempt 未改产品测试）。

## 1. 建议 reviewer 复算/复验的项（卡片专属 oracle）

| # | 复验项 | 期望 |
|---|---|---|
| R1 | 从 `evidence/frozen_band_raw_record.json` **手数**：每树 24 次中失败数 | T0 6/24、T4 6/24，且 pass1 失败更多的是 T0、pass2 是 T4（翻转） |
| R2 | 同一记录的完整性 | 48/48 行有 launcher 事件、48/48 stdout 与冻结 capture 逐字节相同 |
| R3 | 两棵树的字节关系 | `iso/T0b/src` == `iso/T0/src`（字节相同）；`T0` vs `T4` 仅差 cli.py/observability.py/worker.py |
| R4 | 复算至少一个 M-A 统计量 | 任取 `after/child-lifetime-popen-quiet.json`，用其 `samples[].immediate_exit_lifetime_seconds` 手算 median 与 `count_ge_050`，与文件里的 `stats` 一致 |
| R5 | 复算一个 M-B 汇总 | 任取 `after/band-child-cpu8.json`，手数 `results[].verdict` 与 `tally_by_tree` 一致 |
| R6 | 机制核对 | 抽 `after/band-child-cpu8.json` 里任一失败运行，对照 `after/band-captures-child-cpu8/*-launcher-events.jsonl`：被杀 uptime 是否落在 (0.5, 0.7]，以及是否"最后一个 child 干净退出" |
| R7 | 边界检查 | 确认本 attempt **没有**改 `CW/tests/**`、`CW/scripts/**`、`CW/src/**`（见 `binding.json.forbidden` 与 `after/final_hashes.json`） |
| R8 | 独立反例/变体 | reviewer 自选一个未用于本 attempt 的变体（例如另一 basetemp 长度、另一负载等级、或把 `-WorkerHangTimeoutSeconds` 改成 2 的**只读**对照运行）先记录预期再看结果 |

## 2. 结论栏（reviewer 填写）

- 结论：`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`（四选一，未填即为未验收）
- 资格：本卡只给"测试时序抖动的测量与归因"，**不给**产品正确性、发布资格、`disclosure_adaptation`、`accuracy`。
- 保留案例（reviewer 预先保留、未用于实现者编写修复的变化案例）：
- 未获资格 / 未满足项：
- reviewer 签名与日期：

## 3. 实现者已如实登记的缺口（reviewer 需判断是否可接受）

1. `quiet` 臂的真实含义是"本 attempt 不额外加负载"：测量期间机器上另有两个与本卡无关的
   `chrome-headless-shell` 进程占用约 8.8/12 核（`oracle-addendum-A.md` A1）。
2. 节点②端到端运行数被削减（4×1×2 每条件）；其窗口主要由 M-C 直接测量而非端到端频率。
3. 本卡**没有**消除抖动：卡片退出判据"测试在负载波动下不再随机红/绿"需要**测试侧改动**，
   而"生产仓只读"的边界禁止本 attempt 施加该改动（建议见 `after/proposed-test-side-change.md`）。
4. 卡片正文说本卡"修产品测试的时序假设"，与本次任务书给出的边界（生产仓只读、不得改产品测试
   时序假设）存在口径冲突；实现者按**后者**执行并在此登记，需 owner 裁定后续是否另立施加卡。
