# I-14-B review.md — 实现者自述与待 reviewer 攻击点（**未自签**）

- card：I-14-B（parent I-14）
- attempt：`execution_runs/I-14-B/a20260919-01`
- 实现者：本 attempt 的实现模型
- 独立 reviewer：**未指定、未审阅**
- **本文件的结论仅为 `review_pending` 的自述，不含 accepted 字样，也不代表任何资格授予。**

---

## 1. 范围与产出（做了什么）

在本 attempt 目录内新建了一个**候选计时/证据分类器**与配套证据，**未触碰任何生产文件**：

| 文件 | 作用 |
|---|---|
| `oracle.md` | 运行前冻结：字段分列、14 条判据、20 个 case 的手算期望、容差预注册、日历规则、退出码契约（含 §8-errata 与 §8-errata-2） |
| `harness/cases.json` | 20 个冻结输入（W1–W7 计时、C1–C7 日历、L1/L2/L2b/L3/L4/L5 登录锚点） |
| `harness/frozen_expectations.json` | 运行前**手写**的逐 case 期望（verdict / refusals / 关键派生量） |
| `harness/run_cases.py` | 独立预期侧的反作弊门（rc 0 仅当 20/20 匹配） |
| `harness/tests/test_i14b_natural_window.py` | 手写断言的验收套件（29 vs 37、并集 vs 求和等） |
| `harness/mutate.py` | 15 个变异，逐条回退单一判据 |
| `harness/tolerance_sweep.py` | 容差作为**输入参数**的扫描（不是真实试验） |
| `harness/probe_ui_capture.py` | UI 捕获能力探测（只读） |
| `harness/calendar_map.py` | 需求ID→I-17 日历映射 + 只读普查（锚点由脚本搜索得到，不手抄） |
| `harness/reproduce_ca206_acceptance.py` | 只读导入**生产** CA-206 纯函数，复现历史攻击 |
| `harness/capture_baseline.py` / `make_diff.py` | 只读不变量快照 / 确定性生成 diff |
| `iso/natural_window.py` | 被测件（BEFORE→AFTER 两次修订；diff 见 `changes.diff`） |

## 2. 实测结果（raw rc 与业务判定分开）

| 命令 | raw rc | 期望 rc | 业务结果 |
|---|---:|---:|---|
| `CMD-I14B-CASES-before` | 1 | 1 | mismatch 213，**12 个不合规主张被 accept** |
| `CMD-I14B-SUITE-before` | 1 | 1 | 30 failed / 2 passed |
| `CMD-I14B-CA206REPRO` | 0 | 0 | **生产** CA-206 函数把攻击账本判为 `complete`（daily 7） |
| `CMD-I14B-CASES-after` | 0 | 0 | mismatch 0，accepted_ineligible 0（20/20 匹配） |
| `CMD-I14B-SUITE-after` | 0 | 0 | 32 passed |
| `CMD-I14B-REPEAT-1..3` | 0,0,0 | 0 | 三次一致，SUT hash 相同 |
| `CMD-I14B-MUTATE` | 0 | 0 | 15/15 变异重新变红，且预期反例都在红名单内 |
| `CMD-I14B-TOLERANCE-SWEEP` | 0 | 0 | L2 在 tol 87 s 才翻转；L2b/L3/L4/L5 全程拒绝 |
| `CMD-I14B-UI-CAPABILITY` | 0 | 0 | 捕获能力未建立（见 §5） |
| `CMD-I14B-CALENDAR-MAP` | 0 | 0 | 17 行、0 锚点缺失、全部 pending |
| `CMD-I14B-CLI-CONTRACT` | 2 | 2 | 畸形输入 fail-closed |

## 3. 核心判据与反例（卡 #1）

**分列**：`scheduled_at` / `started_at` / `first_sampled_at` / `last_sampled_at` / `observation_finished_at` / `quick_check_seconds` / `command_total_seconds` / `schedule_lag_seconds` 全部单独输出；形状缺失即判不匹配（`run_cases.py` 的 `REQUIRED_KEYS`）。

**重叠不相加**：W4（窗 A 00:00–00:29、窗 B 00:20–00:40）主张 Σ=2940 s → `R-SUM-OVERLAP`；手算并集 2400 s、重叠 540 s。W5 同输入主张并集 2400 s → accept，且输出里 `sum_seconds=2940` 只作 `forbidden_sum_seconds` 语义（`sum_used_for_natural_duration=false`）。**能证伪它的反例**：MUT-1 把并集换成求和后 W4 与 W5 同时重新变红（mismatch 8）。

## 4. 合成时间用例（卡 #2）

W1：观测 00:00–00:29（30 个 60 s 样本）+ 结束后 quick_check 00:29–00:37 ⇒ **观测 1740 s（29 min）**、quick_check 480 s（8 min）、命令总耗时 2220 s（37 min）。测得的正是 1740，不是 2220。W2/W3 把 37 min 当观测或用 29+8 冒充观测，均被拒（`R-TOTAL-AS-OBS` / `R-QC-IN-OBS`）。**该用例只验证计时算法，不构成真实观察资格**（已写进 oracle.md §3 与 `harness/cases.json` 的 note）。

## 5. 30/60/120 秒检查（卡 #3）

- **容差未冻结**：`oracle.md` §6.1 的预注册块中 `frozen_by` / `frozen_at_utc` / `frozen_tolerance_seconds` 仍为 `null`，实现者提议 5 s 但**不自签**。
- **真实检查 blocked**：9/9 捕获模块不可导入；4,002 个扫描文件中 0 个"预布置记录器"候选；本 attempt 未启动 worker/浏览器。**边界如实声明**：PATH 上存在 `ffmpeg.EXE` 与 `playwright.EXE`（未运行），`SESSIONNAME=Console`，所以不能声称"物理上不可能"，只能说"本 attempt 未建立该能力且前置条件缺失"。
- **算法级验证（合成输入，不是试验）**：历史缺陷模式（标签 30/60/120 实际为累计等待 29/88/207 秒）在 tol ≤ 86 s 一律被拒，tol = 87 s 起才通过——证明该判据是真阈值而非"一律拒绝"，也指明了自选容差的危险。

## 6. 自然日历（卡 #4）

`evidence/calendar_mapping.json`：17 行，全部 `started_at=null / due_at=null / status=pending / measured_here=false`；锚点由脚本在源文件中搜索字面量得到（行号、原文、文件 sha256 一并落盘），不手抄。已存在的真实产物（daily/weekly/monthly/legacy_periods/daily_alert）只做**只读普查**，且登记 `latest daily manifest ok=false`（`20260919T210001Z`）。**本卡不裁资格**：那是 I-17-A 的 reviewer 职责。

## 7. 生产零改动（分范围陈述）

- 写入**仅**发生在 attempt 目录内；RF porcelain 中本 attempt 的唯一足迹是 `?? .planning/…/execution_runs/I-14-B/`。
- 产品文件 porcelain 集合 before/after **完全相同**（45 条）；company-wiki 仍只有 ` M CLAUDE.md`、` M README.md`；filing-fetch 空。
- 引用锚点全部逐字节不变：`test_ca206_soak_window.py b8169d64…`、aug09 `task_plan.md 6214a36b…`、四个 `assurance/runs/*.json`、`catalog.sqlite3 69f498a2…`。
- 不变量：catalog 49,677,344,768 B / mtime `2026-09-19T06:31:35Z` / `-wal` 0 B；`.planning/reviews` mtime **before = after = `2026-09-19T08:14:20.083527Z`**。
- `worker_control.json` sha256 `9fcbe233…`（`desired_state=paused`）与 `runtime_policy.json a0ce50c9…` 均未变。
- **必须披露的并发事实**：RF HEAD 在本 attempt 期间由 `1ac01f02…` 变为 `e9544495…`，原因是**审计 owner 自己**在 `2026-09-20T03:54:00+01:00` 提交（`git log -1` 显示 author `zhengcb81`，题"审计实施段：交付留档 M05-M08/M13-M28 + I-07-A/I-14-A/I-09-A"）。本 attempt 未执行任何 `git add/commit/restore/stash`，只用 `--no-optional-locks` 的只读命令。
- **与用户给定 mtime 值的差异声明**：任务书写 `.planning\reviews` mtime 应保持 `2026-09-19 10:05`，而绑定时刻实测（本地时区 GMT+1）为 `2026-09-19 09:14:20`（UTC `08:14:20Z`）。本 attempt **不修改**该值，只保证"与绑定时刻一致"；没有 10:05 这个观测值可供比对，故不声称与它相符。

## 8. 变异证明（15/15）

`evidence/mutations.json`：每条判据被单独回退到 scratch 副本后，运行**同一** runner：

| 变异 | 回退判据 | runner rc | 重新变红的 case |
|---|---|---:|---|
| MUT-1 | 重叠求和 | 1 | W4, W5 |
| MUT-2 | 命令总耗时当观测 | 1 | W2 |
| MUT-3 | quick_check 计入 | 1 | W3 |
| MUT-4 | 未测量按 0 | 1 | W6 |
| MUT-5 | 越界样本 | 1 | W7 |
| MUT-6 | 未来时钟 | 1 | C1 |
| MUT-7 | 模拟时钟 | 1 | C5 |
| MUT-8 | 空 hash | 1 | C1, C7 |
| MUT-9 | 重复 run_id | 1 | C6 |
| MUT-10a | 同一瞬时当连续 | 1 | C1 |
| MUT-10b | 登录同一瞬时 | 1 | L4 |
| MUT-11 | 主张超过事实 | 1 | C1, C4, C6, C7 |
| MUT-12 | 标签偏移 | 1 | L2, L2b, L4 |
| MUT-13 | 共享锚点 | 1 | L5 |
| MUT-14 | 事后捕获 | 1 | L2b, L3 |

## 9. 未做项（不得被读成已完成）

1. **真实 30/60/120 秒观察**：未做 → blocked（D-1/D-2）。
2. **真实自然日/周/月窗口**：未做 → 全部 pending（D-3）。本卡**不授予**任何自然观察资格。
3. **补丁提升**：`iso/slo_probe_patched.py` 未复制进 `RF/tools/`（I-14-A D1/D2/D3 未签）。
4. **生产验收件修复**：`RF/tests/test_ca206_soak_window.py` 的可攻击性已复现，但**未修**（属 I-17-A 范围）。
5. **未跑**：任何 worker/scheduler/后台常驻进程、任何网络命令、任何生产库写入。
6. 中间一次 AFTER 运行的 3 处不匹配已由**改实现**解决（不是改期望），原始文件被同目录重跑覆盖，声明见 `after/cmd-CASES/FIXCYCLE.md`。

## 10. 待 reviewer 攻击点（请优先打这些）

1. **oracle 是否真的先冻结**：`oracle.md` sha256 `093899bc…`；`harness/cases.json` `5d8c4592…`；`harness/frozen_expectations.json` `3ba2bb17…`。请核对 §8-errata / §8-errata-2 的时序声明是否可信（r0 探索性 RED 与形状检查的关系）。**若认为"先跑 r0 再加形状检查"已经污染冻结，请直接判 changes_required。**
2. **手算期望是否独立**：请复算 1740/480/2220、2400/2940/540、29/88/207 → max error 87、以及 C3 的 weekly 新鲜度（`2026-09-13T04:30Z` 距 `2026-09-20T02:56:38Z` 是否 ≤ 7 d）。
3. **C1 的攻击是否被如实建模**：`before/cmd-CA206REPRO/ca206_repro.json` 用的是生产函数本体；请核对输入确实与 `reviews/revenue/review.md:13` 描述一致（7 个不同 ID、同一未来时间、空 hash），以及该复现是否只读。
4. **拒绝码语义**：`R-CLAIM-EXCEEDS` 同时用于计时（数值与其自身 basis 不符）与日历（主张 complete 而计算 pending）；请判断这种复用是否是隐藏的语义混淆。
5. **`R-SAME-INSTANT` 的适用面**：日历按 `started_at`、登录按 `sampled_at`。请检查是否存在合法场景（例如同一日两个不同窗口）会被误拒。
6. **容差扫描是否等价于"事后挑容差"**：本卡的辩护是"报告整条曲线 + 翻转点，并把 proposed 值与结论分离"。请判断该辩护是否成立。
7. **blocked 与 pending 的边界**：CAL-13 同时出现在日历（pending）与 §5（blocked）。请判断是否应只保留一种状态。
8. **零改动声明**：请独立核对 before/after 快照与 `git log`，特别是 RF HEAD 变化是否真的与本 attempt 无关。
9. **未证伪项**：周/月窗口规则（35 d、7 d 新鲜度）只有 C2/C3/C4 覆盖，没有"weekly 全部过期"或"monthly 过期"的独立反例；如果认为需要，请列为 changes_required 或后续卡。
10. **不可外部锚定**：本 attempt 的全部证据都是它自己产出的；生产侧唯一的外部锚点是只读文件 hash 与 CA-206 复现。

## 11. 状态

`review_pending`。未自签 accepted；未授予 formula / disclosure_adaptation / accuracy 之外的任何额外资格，且本卡本身**不授予**真实自然观察资格。
