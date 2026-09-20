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

---

# §5 独立 reviewer 裁决（独立 reviewer session）

> 本节由**独立 reviewer session**（DSH agent session `session-b0e4a430ca7d`，由父 session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 委派；
> 审阅时刻 `2026-09-20T03:15Z` 前后）在尝试封存后追加。本节的插入不改动本文 §1–§11 任何一字
> （写入前副本 `review.md` sha256 = `5f6e5887…`，追加后见 `handoff.json` 之外的 reviewer 记录）。
> 完整武器化证据、命令与原始输出见 reviewer 报告 `REPORT.md`（sha256 `fdb93aa2f7706b46b104192b094458d220d0b528ea6ca67e87de7c0416a517eb`）。

## 结论：`changes_required`

**授予（仅记录性，不构成 accepted 资格）：** 计时/时间字段**分列口径**与"重叠取并集、不相加"的算法，
在冻结的 W1–W7 上正确且可独立复现；合成输入 1740/480/2220（29≠37）的算术与判定正确；
`R-SUM-OVERLAP` / `R-NO-SAMPLES` / `R-SAMPLE-OUTSIDE`（含 ±1 s 严格边界）行为正确；
容差在 tol ∈ [1 s, 86 s] 稳定区间内行为正确；日历 17 行映射与全部 pending 正确；
生产零改动、冻结时序、变异 15/15 单行回退、CA-206 生产侧外锚点均经独立复核成立；
实现者自述与弱项披露**诚实**（`handoff.json` 仍 `review_pending`、未自签、FIXCYCLE 覆盖事件已如实登记）。

**不授予：** ①计时/分类器在冻结输入**之外**的正确性（下述 P1/P2 反例已实测被 accept）；
②任何真实自然观察资格；③真实 UI 即时性资格；④formula / disclosure_adaptation / accuracy；⑤产物进入生产树。

## 阻断项（must fix）

**P1（严重）`claim.basis` 未做枚举校验 ⇒ 计时判据整体可被绕过。**
`iso/natural_window.py:157-178` 的 `if/elif` 链没有 `else`，当 `basis` 取未知值 / `""` / `null` / 缺失时 `allowed` 保持 `None`，
第 177 行的 J11 一并失效。独立实测（我在 attempt 之外自造 case，不在冻结 20 内）：
`B1 basis='wall_clock' claim=2220 → accept_claim（refusals=[]）`；
`B2 basis='' claim=99999 → accept_claim`；`B3 basis 缺失 claim=99999 → accept_claim`；`B4 basis=None claim=2220 → accept_claim`；
负对照 `B5 basis='command_total' → reject（R-TOTAL-AS-OBS）`（证明不是 SUT 整体失效，而是取值域未校验）。
**修法：** 显式校验 `basis ∈ {sample_span, command_total, observation_plus_quick_check, sum_of_windows, union_of_windows}`，
未知/缺失即拒（建议新增 `R-BASIS-UNKNOWN`）；并在 `harness/cases.json` 增 2 条反例。

**P2（严重）`union_of_windows` / `sum_of_windows` 把 quick_check 计入自然观察时长。**
`iso/natural_window.py:137-147`：无显式 `windows[]` 时 `intervals = [观察窗] + [quick_check 窗]`，
`union = _measure_union(intervals)`；而 J3 只在 `basis == "observation_plus_quick_check"` 时触发 ⇒ 换 basis 名即可绕过。独立实测：
`P1（无 windows[]，主张 2220 union_of_windows）→ accept`；
`P2（同事实、诚实主张 1740）→ reject（R-CLAIM-EXCEEDS）`（**方向反了：诚实值被判不合规**）；
`P4/P5（把 quick_check 时段改名为第二个观察窗）→ accept`；`P6（同事实、basis=sample_span）→ reject`（负对照）。
再以 attempt 自带 runner + reviewer 自写期望跑 8 条新 case：
`{"ok": false, "case_count": 8, "mismatch_count": 2, "accepted_ineligible_count": 1, "sut_raw_returncode": 0, "sut_sha256": "495a4411…"}`，
命中 `X6: expected=reject_claim got=accept_claim`。
**此漏洞已烧进冻结期望：** W1 冻结的 `union_seconds = 2220` 与 J3 的严格读法冲突（严格读法下应为 1740），
故修 P2 必须**同时改 oracle 期望**，不能只改实现。
**修法（二选一，须显式选定并写入 oracle）：** 甲）并集只由观察区间构成，W1 的 `union_seconds` 期望改 1740；
乙）保留机械并集，但新增"并集不得覆盖任何 quick_check 区间"的判据（触发 `R-QC-IN-OBS`）并加 2 条反例。

## 记录项（不阻断）

- **P3-a** `R-SAME-INSTANT`(J10a) 对"同一 UTC 日、不同 run_id、不同瞬时"静默断链：实测 11:00 与 12:00 两条
  → `daily_count=1`、**无拒绝码**。不会误拒，但会把真实同日两次运行降级计数。**保守失败，非阻断**；
  建议在链规则补诊断字段使其可见。
- **P3-b** weekly / monthly"全过期"无独立反例（实现者自报准确）。reviewer 补跑 Q3（weekly 最新 6.9 天前）/ Q4（monthly 40 天前）
  证明**代码路径存在且行为符合 oracle**，但冻结集缺反例；建议补 2 条**带 `status="complete"` 主张**的 case，
  否则只能证明"不崩"而非"会拒"。
- **P3-c** `R-CLAIM-EXCEEDS` 跨 timer / calendar 复用：oracle §2 已预登记，`handoff.json:126` 主动请打，**不判缺陷**；建议后续拆码。
- **P3-d** `after/cmd-CASES` 目录 mtime `03:05:02Z` 高于内部报告内嵌 `generated_at_utc 03:00:12Z`，
  系事后写 `FIXCYCLE.md` 抬高目录 mtime；在 FIXCYCLE 成因链下时间线自洽。
- **P3-e** 口径澄清：`PLAN\reviews` **目录** mtime = `2026-09-19T08:14:20.0835265Z`（本地 09:14:20），
  目录内**最新文件** `second_wave\final_review_checks.json` = `2026-09-19T09:05:32Z`（本地 10:05:32）。两个值都对，是不同对象。
- **P3-f** RF HEAD 在审阅期间由 `e9544495…` 推进到 `ddc81ab6…`（owner `2026-09-20T04:09:31+01:00` 提交，含 120 个 I-14-B attempt 路径）。
  复核 attempt 内 8 个关键文件哈希**逐字节未变**，该 commit 只作留档。**副作用**：attempt 目录的 `??` porcelain 足迹已被该 commit 吸收，
  现在查该路径 porcelain 为空 —— 后人不得据此推断"没有足迹"。

## D-1 —— **已由本 reviewer 填写：`frozen_tolerance_seconds = 5`**

按"合法下界 / 危险上界"两处独立约束定值，而非照抄实现者提议：
L1（诚实锚点，捕获延迟 1 s）实测 `tol=0.9 拒 / tol=1.0 起通过` ⇒ 容差 <1 s 会误杀**合法**即时截图（下界 1 s）；
L2（历史累计等待 29/88/207，手算 max error 87 落在标签 120）实测 `tol ≤ 86 拒 / tol = 87 起通过`
⇒ tol ≥ 87 s 会让**已复现的历史缺陷**通过（上界 86 s）。**合法区间 [1 s, 86 s]，取 5 s。**
`capture_latency_tolerance_seconds` 同为 5。判据为 `max_error > tol`（严格），tol=5 放行误差 ≤5 s，与整数秒标签语义一致。

填写行：`oracle.md` L128–L131（`frozen_by` / `frozen_at_utc = 2026-09-20T03:15:44Z` / `frozen_tolerance_seconds = 5` / `reviewer_signature_line`）。
改动脉络：`oracle.md` sha256 `093899bc…` → `f8082205…`，18794 → 18858 字节，**行数 209 → 209**，
逐行比对 `identical = 205`、`differing = [128,129,130,131]`（恰好 4 行）；`proposed` 两行（L126/L127）保留原文未动。
填前副本留档于 reviewer 报告目录（sha256 = 原 `093899bc…`）。

**签字不等于可以开真实窗口。** D-1 恢复规则三条件中：(a) reviewer 冻结容差 ✅ 本次已签；
(b) 预布置记录器就位并产出带 hash 的登录锚点事件 ❌（探测 0/4002 候选）；
(c) owner 显式授权在该窗口启动 worker/UI ❌。另加两条 reviewer 前置：**先修 P1**；
真实窗口须**另开 attempt + 另开 binding**，**不得**改写本 attempt 的 blocked 记录。
⇒ **真实 30/60/120 格维持 `blocked`；签字只把它从"blocked"变为"可开卡"，不等于已运行。**

## 其余 decision 项处置

- **D-2**：**维持 blocked，不授权**。独立确认 `ffmpeg.exe`（`C:\Users\郑曾波\ffmpeg\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe`）
  与 `playwright.exe`（`C:\Miniconda\Scripts\playwright.exe`）存在，而隔离解释器内 `playwright` **不可导入**
  （该 exe 是 Miniconda 的 CLI，缺对应 Python 包）。用它们建捕获路径属 owner 的专业决定 + 新卡。
- **D-3**：**不裁**，归 I-17-A 的 reviewer。17 行全 pending 是正确处置；`latest daily manifest ok=false` 未被计入。
- **D-4**：**复核通过，维持**。BEFORE 版本 `sut_raw_returncode = 0` 却接受 12 个不合规主张，自指契约的论证成立。
- **D-5**：**复核通过，维持**。实测单样本 + 主张 0 s → `R-NO-SAMPLES`。
- **D-6**：**复核通过，维持**。`RF/tools/` 下只有 `slo_probe.py`（mtime 2026-08-13，早于本 attempt）；
  `slo_probe_patched.py` 仅存在于 I-14-A attempt 的两个目录内，**未提升**。

## 待 owner / 其他 reviewer

1. **owner**：D-2 是否投入建设 UI 捕获路径（含显式授权启动 worker/UI 窗口）。
2. **本卡实现者**：修 **P1**（必做）、**P2**（必做，且需同步改 W1 的 `union_seconds` 期望或新增 J3 判据）。
3. **I-17-A reviewer**：D-3，哪些原自然窗口保留；`assurance/runs/*` 现存产物不得当周期完成。
4. **owner / 后续卡**：P3-a/b/c 记录项；`RF/tests/test_ca206_soak_window.py` 的可攻击性已复现但**未修**（属 I-17-A 范围）。

## reviewer 未能验证

物理机真实截图能力（未运行 ffmpeg/playwright、非交互会话）；`catalog.sqlite3` 完整 sha256
（46.3 GB 超出 `Get-FileHash` 时限，仅核尺寸 `49,677,344,768 B` / mtime `2026-09-19T06:31:35Z` / `-wal` 0 B）；
被覆盖的第一次 AFTER 报告原文（已不存在，故无法逐字节复核 `mismatch_count = 3`）；
`oracle.md` 之前那次写入是否"只追加"（无改动前副本，仅能证 mtime 时序自洽）；
runner 两版之间除 `REQUIRED_KEYS` 外是否还有差异（无旧版源码；但可逻辑证明新增检查只会变严或不变）。

---

# 12. r2 实现者回应：`changes_required` 的修复记录（**追加节，未自签**）

本节在 reviewer 裁决节之后**追加**。§1–§11 与 reviewer 节**一字未改**（可核验：原 230 行逐行 identical）。本节不含 accepted 字样；第三轮复核仍由独立 reviewer 给出。

## 12.1 两个阻断项的修复与红→绿证据

**P1（`claim.basis` 无枚举校验）** → 新增 **J16**：`basis` 必须属于封闭枚举 `{sample_span, command_total, observation_plus_quick_check, sum_of_windows, union_of_windows}`；未登记/空串/`null`/缺键 → **`R-BASIS-UNKNOWN`**。

**P2（quick_check 计入自然观察时长）** → 采**甲**：自然观察区间只由观察阶段构成（无 `windows[]` 时 `intervals=[(started_at, observation_finished_at)]`），quick_check 永不进入并集；并另加 **J15**：任何已声明的观察窗若覆盖 quick_check 区间（reviewer 的"改名"变体）→ `R-QC-IN-OBS`。**选甲而非乙的理由**：乙式判据虽能拒 37 min，但诚实主张 1740 s 仍会被误拒（reviewer 实测的方向倒置不会消失）。

| 行为 | 修复前（reviewer 复核过的 r1 修订 `495a4411…`） | 修复后（r2 `7fff6f0c…`） |
|---|---|---|
| X1 `basis="wall_clock"` 2220 s | **accept**（refusals=[]） | reject `/ R-BASIS-UNKNOWN` |
| X2 `basis=""` 99999 s | **accept** | reject `/ R-BASIS-UNKNOWN` |
| X3 `basis` 缺键 99999 s | **accept** | reject `/ R-BASIS-UNKNOWN` |
| X4 `basis=null` 2220 s | **accept** | reject `/ R-BASIS-UNKNOWN` |
| X5 诚实 1740 s `union_of_windows` | **reject** `/ R-CLAIM-EXCEEDS`（方向反了） | **accept** |
| X6 2220 s `union_of_windows`（reviewer X6） | **accept** | reject `/ R-CLAIM-EXCEEDS` |
| X7 2220 s `sum_of_windows` | **accept** | reject `/ R-CLAIM-EXCEEDS` |
| X8 窗口 B 复制 quick_check 时段 | **accept** | reject `/ R-QC-IN-OBS`（重叠 480 s） |
| X10/X11 无任何观察区间却主张 0 s | X10 reject(错码) / X11 **accept** | 均 reject `/ R-NO-INTERVAL` |

同一条冻结命令的前后 rc（命令与原始输出全部落盘）：

| 命令 | rc | 业务结果 | 证据 |
|---|---:|---|---|
| `run_cases.py --sut <r1 修订> --cases cases.r2.json --expectations frozen_expectations.r2.json` | **1** | mismatch 49、**accepted_ineligible 8**（X1,X2,X3,X4,X6,X7,X8,X11） | `before/cmd-CASES-r2-r1sut/cases_report.json` |
| `run_cases.py --sut <原始 AFTER> …`（同一 r2 材料） | **1** | mismatch 452、accepted_ineligible 20 | `before/cmd-CASES-r2-baseline/cases_report.json` |
| `run_cases.py --sut iso/natural_window.py …`（**同一命令**，修后） | **0** | mismatch 0、accepted_ineligible 0、34/34 | `after/cmd-CASES-r2/cases_report.json` |
| `pytest harness/tests/test_i14b_natural_window_r2.py`（对 r1 修订） | **1** | **14 failed / 4 passed** | `before/cmd-SUITE-r2-r1sut/stdout.txt` |
| 同上（对 r2 修订） | **0** | **18 passed** | `after/cmd-SUITE-r2/stdout.txt` |
| `pytest harness/tests/test_i14b_natural_window.py`（r1 套件**未改一字**，对 r2 修订） | **0** | **32 passed** | `after/cmd-SUITE-r1suite-vs-r2sut/stdout.txt` |
| `run_cases.py`（r2 材料）重复 3 次 | 0,0,0 | 三次一致 | `evidence/repeat-r2-1..3/cases_report.json` |
| `mutate.r2.py` | 0 | **20/20 变异重新变红**，预期反例均在红名单 | `evidence/mutations.r2.json` |

**红→绿变异证据路径**：`evidence/mutations-r2/MUT-15-J16-basis-enumeration/` → 红 X1,X2,X3,X4；`evidence/mutations-r2/MUT-16-P2-quick-check-in-union/` → 红 W1,X1,X5,X6,X7；`evidence/mutations-r2/MUT-17-J15-window-covers-quick-check/` → 红 X8,X9；`evidence/mutations-r2/MUT-18-J4b-absent-observation-interval/` → 红 X10,X11；`evidence/mutations-r2/MUT-19-J10c-same-utc-day-second-run/` → 红 X14。每条变异均是对 scratch 副本的**字面单行回退**（断言恰好命中 1 次），正式被测件未被改动。

## 12.2 oracle 期望更正的追加式 provenance 落点

- **文件 + 键**：`harness/frozen_expectations.r2.json` → `expected.W1.computed.union_seconds`，旧值 **2220** → 新值 **1740**（并新增 `sum_seconds=1740`、`observation_interval_count=1`、`quick_check_overlap_seconds=0`、`quick_check_in_observation_intervals=false` 作为锚定断言）。
- **旧值保留处**：同文件 `expected_superseded["W1"]["computed.union_seconds"]`，字段含 `old=2220`、`new=1740`、`pre_image_sha256=3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b`、`changed_at_utc`、`reason`。
- **机械 diff**：同文件 `errata[0].diff_from_r1_expected_map`（r1→r2 期望映射的 unified diff，182 行）。
- **前像文件**：`harness/archive/frozen_expectations.r1.json`（sha256 `3ba2bb1799ae30b9…`）、`harness/archive/cases.r1.json`（`5d8c459277da88b8…`），另有 17 个 r1 文件 byte-identical 归档于 `harness/archive/MANIFEST.json`。
- **重新冻结**：`harness/cases.r2.json`（34 case，`c00a3a00ffe8b883…`）＋ `harness/frozen_expectations.r2.json`（`6f814d0af6a8ffd0…`）；r1 两份**未被覆盖**。r2 报告的 `expectations_sha256` 一律为 `6f814d0a…`（可核验冻结时点）。
- **oracle.md 追加节**：`## 11. r2 勘误与新增判据`（L210 起）；§1–§10 与 reviewer 冻结四行 L128–131 **逐行 identical**（`identical prefix lines = 209/209`，`differing=[]`）。`oracle.md` 新 sha256 `bdd0407ab577ed4564b8e948d8e3954b663c795dbcd7a3035485424ae753baf3`。
- **如实声明的次序偏差**：本次**先改实现、后冻结 r2 期望**；理由是修复目标已由 reviewer 报告逐条给定，且期望值系从 reviewer 报告的原始 probe 输出与 oracle 字段定义手算。第三条支撑证据：r1 修订在 r2 oracle 下的越权行为（accepted_ineligible 8）由独立运行复现——期望不是"照着修好的实现写的"。

## 12.3 改前→改后 sha256 表

| 文件 | r1（reviewer 已复核） | r2（本次修复后） | 说明 |
|---|---|---|---|
| `iso/natural_window.py` | `495a44111a854bd5b76d39aeae91d11ab789fe48bb8bcbc9ae3af4b87d8c5b95` | `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` | P1/P2/J15/J4b/J10c；r1 归档于 `harness/archive/natural_window.after-r1.py` |
| `oracle.md` | `f8082205f17d3afa5eaa3a976f87b61259f92f7679584ead88f95482a0cb01b5` | `bdd0407ab577ed4564b8e948d8e3954b663c795dbcd7a3035485424ae753baf3` | 209 → 273 行；前缀 209 行 identical |
| `review.md` | `5d99f4dc04866da2027883b102f0f0777790af3a5e060299edcdc2c1aeac8fe3` | 见 `evidence/file_manifest.json`（本节追加后自失效，故不在此处引用自身哈希） | 230 行 → 追加本节 |
| `harness/cases.json`（r1） | `5d8c459277da88b8361b520bee1424f079dc1d9c08744433cae0d30cdbb67d64` | 未改（新文件 `cases.r2.json` = `c00a3a00ffe8b883…`） | 旧文件不覆盖 |
| `harness/frozen_expectations.json`（r1） | `3ba2bb1799ae30b9acac064ab7a7a57338fcd3dfab3aa27052e02f8ffdac806b` | 未改（新文件 `frozen_expectations.r2.json` = `6f814d0af6a8ffd0…`） | 旧文件不覆盖，勘误另存 |
| `harness/run_cases.py` | `f2a07d0b85c5dcb3a233d9010ad9deead70b22535ab82a61414d2ef7f54f7c23` | **未改**（r2 通过 `--cases/--expectations` 指向 r2 材料） | reviewer 关心的两版差异问题不再增加新版本 |
| `harness/mutate.py` | `ff4ec9d9f07319b7f6a94a11bbbd2dd9db9f39b55aace4a29e3a9db2b1c03a36` | 未改（新增 `harness/mutate.r2.py`） | 旧文件不覆盖 |
| `harness/tests/test_i14b_natural_window.py` | `413ff05c52e07acacf0491a0ec3f2cd1c426011995b45d7ad3edaab65a38ad4e` | **未改**，且对 r2 修订仍 32 passed | — |
| `harness/tests/test_i14b_natural_window_r2.py` | —（新增） | 见 `evidence/file_manifest.json` | 18 tests |
| `harness/calendar_map.py` | `4789cc9360aea4e4b1c4bbebb2412ddaf48883dbd14a32c99d1606e83e7b86fe` | 见 manifest（增加 CAL-13 `blocked_reason`） | reviewer P3⑦ 建议 |
| `evidence/calendar_mapping.json` | `6f3ebd998a0cbcc7460d501befbbde5aeff055f90382817b7b3155e1d00aea8e` | `e3a734b3253716cb68e18483fba5fe3df8eb857ee7ad76e2961ca48ae487bf02` | r1 归档于 `harness/archive/calendar_mapping.r1.json` |
| `evidence/mutations.json` | `61a5fe1426da03e0c0ae2234b5034f94f1ae9cf2d7d648d41db241fce2fba6f7` | 未改（新增 `evidence/mutations.r2.json`） | 旧文件不覆盖 |
| `changes.diff` | `89556ac05de87ebe37962f6ecb3861a63261b98f778c9beb49604417e26dcaf1` | 未改（新增 `changes.r2.diff` = `660bc943187db1c083ef8f04b3c642f3917a3040a5eae376c4fcbbb7ef2c2104`，+71 −13） | r1→r2 修复 diff |

## 12.4 仍存在的缺口（不掩盖）

1. **真实 30/60/120 秒观察仍 blocked**：容差已被 reviewer 冻结（5 s），但 (b) 预布置记录器 0/4002 候选、(c) owner 未授权启动 worker/UI，且 reviewer 另加"先修 P1"（已完成）与"真实窗口须另开 attempt + 另开 binding"两条前置。本 attempt **不得**改写 blocked 记录。
2. **真实自然日/周/月窗口仍全部 pending**（17/17）。本卡不授予自然观察资格。
3. **P3 记录项**：`R-CLAIM-EXCEEDS` 跨 timer/calendar 复用未拆码（`R-NUMERIC-BASIS-MISMATCH` 留给后续卡）；weekly/monthly 的"全过期"反例已按 reviewer 建议补为 X12/X13，但**周/月边界的 ±1 天行为**仍只有 C2/C3/C4/X12/X13 覆盖。
4. **J10c 的语义选择**：同一 UTC 日第二条 daily 条目现在"忽略且计数"（X14 → daily_count 6、dropped 1）。这是**行为变更**（r1 为静默重置链 → count 4），依据是"7 consecutive Daily runs on consecutive dates"的原文语义；reviewer 可要求改回"重置"或另定，届时按追加勘误处理。
5. **不可外部锚定**：除生产 CA-206 纯函数复现（`before/cmd-CA206REPRO`）与只读文件哈希外，本 attempt 证据仍为自产。
6. **本次仍未验证**：物理机真实截图能力；`catalog.sqlite3` 完整 sha256（46.3 GB 超时限，仅尺寸/mtime/`-wal`）；被覆盖的第一次 AFTER 报告原文（已不存在）。
7. **时序偏差**：先改实现、后冻结 r2 期望（§12.2 已如实声明并给出三条可核查支撑）。

## 12.5 状态

仍为 **`review_pending`**；请独立 reviewer 做**第三轮复核**（重点：X1–X14 的期望是否独立于实现、J15/J4b/J10c 是否越权、W1 期望更正的前像链是否完整、`changes.r2.diff` 是否只含 P1/P2 相关改动）。实现者未自签。
