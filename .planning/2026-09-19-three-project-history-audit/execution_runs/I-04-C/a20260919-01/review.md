# I-04-C 独立复审记录（v1 changes_required → v1.2 处置 → 第二轮 accepted_scoped → r3 处置）

> **状态：PENDING（r3 修订已提交，等待复核确认 3 项 still-required 的处置）。**
> 本文件由实施者起草并维护"处置栏"；**实施者不写自己的判决**。
> reviewer 的结论见 ▶「复审结论」区（由 reviewer 填写/保留）。

## 0. 复审结论（reviewer 填写区，实施者不得改动）

- 第一轮结论：**changes_required** → r2 修订（见 §1）。
- **第二轮结论：`accepted_scoped`** —— 设计被接受；ADR-1..12 的模拟资格与全套 case 授予；
  F-I04C-04（计数）与 F-I04C-07（ADR-11）已闭合；`hashes.txt` 31/31 自洽；F-L4a 真实产出 + LIMITATION；
  F-W1/W2/W4b 断言改正；**V4-a/V4-e/V4-f 与新案例 V4-g1/g2/h/j 全部命中**。
- **附 3 项 still-required**（r3 逐条处置见 §6）：
  ① **错误码与超时 case（I-04-D 落地前必须改掉）**；② **排队跨预算边界验收 + 记录排队消耗下载预算**；
  ③ **正文旧值与 F-LK2 数字统一（卫生）**。
- 不授予：生产实现、真实 provider/worker/wiki 并发、DECLARED 判活与真实探针的等价性、POSIX/SMB 锁语义、
  真实 PID 复用检测、同进程多线程 scope。

## 6. r3 处置（第二轮 3 项 still-required 逐条）

| 项 | 处置 | 锚点 | 证据 |
|---|---|---|---|
| **必修 1**：错误码与实现不一致（实现抛通用 `lock_timeout`，文本冻的是 `lease_lock_timeout`），且没有任何真超时 case | **改实现对齐冻结文本**：`FileLock` 增加 `code` 参数，`lease_lock()` 传 `code="lease_lock_timeout"`（journal 锁与 `stress.py` 的独立锁保持通用码）。新增 4 个真超时/边界 case：F-T1（请求段真占锁 + 预算 0.05 s）、F-T2（预算 0 ⇒ 不尝试加锁）、F-T3（清理段 ⇒ `failed:lease_lock_timeout`）、F-T4（排队跨预算） | `sim/kernel.py`：`FileLock.__init__` 的 `code` 参数、`acquire()` 抛 `self.code`、`lease_lock()`、`run_legacy` 的锁、`Client.worker_pause` 的 `pause_hold_seconds`；`sim/cases_timeout.py`；`sim/hold_lock.py` | `evidence/run/F-T1/`（`code=lease_lock_timeout`、`action=lease_lock_timeout`、`writes=0`、状态字节不变）；F-T2/F-T3/F-T4 同目录 |
| **必修 2**：排队跨预算没有边界验收；排队消耗下载预算未记录 | 新增 **F-T4**：6 个 enter-only 参与者 × 注入临界区保持 H=0.4 s、锁预算 1.0 s ⇒ 4 人 `lease_lock_timeout` 零写、成功者集合恰为 refcount 集合、超时者绝不入表、收尾无悬挂。**把 (N−1)·H 模型与"排队吃掉下载预算"写进 ADR-2 正文、§5 码表与 §14 F-I04C-12**；F-T4 报告 `budget_consumed_by_queueing` | `decision.md` §14 F-I04C-12；`oracle.md` R3-2；`sim/cases_timeout.py::case_f_t4` | `evidence/run/F-T4/`；`evidence/phase-wall.txt`（F-L2d 8 并发最大等待 9.87 s、相位墙 13.2 s） |
| **必修 3**：正文旧值与 F-LK2 数字（三处三组）不一致 | ① `decision.md` §ADR-6 表与 §6 摘要第 1 条 → `lock_budget_for(x)=min(x,60)` + v1.3 更正注记；② §10 的 ADR-10 行标注**已被 §12 R1–R5 取代**（`released_took_ownership` 在 r2 已删除）；③ §10 末段追认"任何情况下都不留下 paused 且无人有义务"**已正式放弃**（R5 允许该终态）；④ `oracle.md` §0 → **每文件计数器、收尾后从 1 重来**（非单调）+ owner 记录字段扩展；⑤ `oracle.md` §7 → `min(相位预算,60)`；⑥ **F-LK2 统一为实测组** finals `[16,35,10,56,18]` ⇒ lost `[184,165,190,144,182]`（来源 `evidence/lock-and-legacy.txt` 的 F-LK2 记录，与 finals 相容；复审复跑 34 与更早一轮 261/200 作为调度依赖的旁证保留） | `sim/patch_r3_docs.py`（可复算的替换脚本，全部替换都成功） | 三处文本对齐后重跑全部证据（见下方计数） |
| **OPEN-3**（复核建议，已采纳） | **保留 60，重命名为"本卡新增的等待上限常数"**：请求段默认 900 s 下不构成额外约束；真实作用是给**清理段（C≤85 s）与短 deadline** 封顶，属防病态等待而非新预算，`≤0` 时拒绝等待（F-T2 已证）；与 I-04-A v2 三条已签值无冲突。**并把"是否允许 `worker-pause` 在锁内"一并列为 owner 待裁** | `decision.md` §14（OPEN-3 段）+ §8 O-3；`oracle.md` R3-3；`handoff.json.next_action` | F-T2 + F-T4 + F-L2d 的 `max_lock_wait` |

> **E1 更正（收尾复核；2026-09-20 追加，原行一字未删）**：上表"必修 2"行的证据栏写 “`evidence/phase-wall.txt`（F-L2d 8 并发最大等待
> 9.87 s、相位墙 13.2 s）”，与该文件的实际内容不符：`evidence/phase-wall.txt` 的 F-L2d 记录是
> `max_lock_wait_seconds = 9.782719`、`phase_wall_seconds = 13.386`，即 **9.78 s / 13.4 s**
> （9.87 是把 9.782719 末两位换位的转录错误）。该数字的权威来源只有 `evidence/phase-wall.txt`
> 一处一行一条记录；本行原文保留，取值以更正块为准。
> 同一过时数字还出现在 `decision.md` §14 F-I04C-12 段与 `oracle.md` R3-2 段（两处均已追加同一更正），
> 以及 `handoff.json.results.queue_cost`（已就地追加 erratum 标注）。**设计结论不变**：
> "8 并发的锁等待接近 10 s、相位墙约 13 s、排队会吃掉下载预算"的量级结论与 ADR-2 的取舍都不受影响。

### r3 的真实计数（重跑后）

- 协议套件（含 F-T1..F-T4）：`cases_in_log=28 pass=28 fail=0 harness_error=0 failing_checks=0`
- 锁与 legacy 反例：`cases_in_log=7 pass=7 fail=0 failing_checks=0`
- `sim/static_check.py`：S1–S4 全 PASS

## 1. 逐条处置（r2；每条给 文件:行 与可复现证据）

| 发现 | 严重度 | 处置 | 锚点（v1.2 代码） | 证据 |
|---|---|---|---|---|
| **F-I04C-01** 最后一格未定义（最后退出者非 owner 且 `resume.required=False`）⇒ 永久 paused | P1 阻塞 | **重写 ADR-10 为 R1–R5 五分支**（`decision.md` §12 ADR-10）。R3 接手"已记录义务"，R4 在 owner **可证死亡**时接手并收尾，R5 其余一律 fail closed 且**不改写 owner 证据**。新增 **V4-a** case | `sim/kernel.py::run_protocol_exit`（R1–R5）；`sim/cases_review.py::case_v4a` | `evidence/run/V4-a/`；`evidence/failures.txt` 的 `=== V4-a PASS (9 checks)` |
| **F-I04C-02** ADR-10(c) 覆盖 W7/T10，把第三方 owner 改写为自己并 resume | P1 | **新增 `owner_resumable()`**：只有 `owner_is_me` / `owner_alive_in_cycle` / `owner_pruned:{dead,pid_reuse}` / `owner_probe:{dead,pid_reuse}` 才可 resume；其余 ⇒ 收尾时 `released_owner_changed`、进入时 `owner_evidence_foreign`。W7/T10 与之统一 | `sim/kernel.py::owner_resumable`、`classify_pid`、`run_protocol_exit` R5、`protocol_paused_branch` | `evidence/run/V4-e/`、`evidence/run/V4-f/`、`evidence/run/F-W7/`（owner 记录不变；`resume_calls=0`） |
| **F-I04C-03** generation 非单调（unlink 后归零） | P2 | **写入冻结文本并改掉"单调不减"**：新增 **ADR-12**（每文件计数器，收尾 unlink ⇒ 下周期从 1 开始），权威判据改为 owner/义务/判活三者。新增 **F-GEN** case | `decision.md` §12 ADR-12；`sim/cases_review.py::case_generation` | `evidence/run/F-GEN/`、`evidence/run/F-W4b/` |
| **F-I04C-04** 证据与报告矛盾（SUMMARY 9/16 失败 vs 报告"10 PASS/6 failing"） | P2（诚实性） | **修 `parse_run.py`**：按行解析所有记录（旧版只找 `{"case":` 字面量，漏读以 `{"A_lease_id"` 开头的记录），**计入 harness-error**，输出 `cases_in_log/pass/fail/harness_error/failing_checks`；scheduler 增 `--log`（UTF-8、不折行）消除 PowerShell 折行截断。**所有计数改回真实值** | `sim/parse_run.py`；`sim/scheduler.py`(`Tee`) | `evidence/failures.txt`、`evidence/lock-and-legacy-failures.txt` 首行；`evidence/run-all.txt`（scheduler 退出码 0） |
| **F-I04C-05** F-L4a 无结果（victim payload 缺 `phase="exit"`） | P2 | **修 harness/调度**：F-L4a 改为"scope 中用户再次 pause"的真实场景；第三方 owner 变体交给 F-W7/V4-e/V4-f；F-L4a 现在真正产出并记录 **LIMITATION** | `sim/cases_ownership.py::case_f_l4a` | `evidence/run/F-L4a/`；`=== F-L4a PASS (6 checks)` |
| **F-I04C-06** F-L2c 实为失败 2 条却报通过（死 lease+无 marker 判成用户暂停） | P2 | 判据改为"**曾经有 entries 即工具证据**"：修剪后为空但曾有 lease ⇒ 不是用户暂停，走接管（`owner_pruned:dead`）。新增 **F-L2c-dead**；F-L2c（unknown）保持 fail closed | `sim/kernel.py::protocol_paused_branch`（`had_entries`/`marker`）；`sim/cases_review.py::case_l2c_dead` | `evidence/run/F-L2c-dead/`、`evidence/run/F-L2c/` |
| **F-I04C-07** ADR-11 未落实（锁外 `state` 被锁内当判据） | P2 | **整条 acquire 路径合并为一个临界区**（读状态+读 lease+判定+写全部在内）；四个子函数**不再加锁**（前置：调用者持锁）。新增静态证明 + 行为对照 | `sim/kernel.py::run_protocol`；`sim/static_check.py`（S1–S4）；`sim/cases_review.py`（F-L2e-*） | `evidence/static-adr11.txt`；`evidence/run/F-L2e-stale/`（pause×2）、`evidence/run/F-L2e-fixed/`（pause×1，join） |
| **F-I04C-08** "规则缺口 vs 调度缺口"初判不成立 | P2 | **逐条重归类**：F-W1=用了已删除的注入点（证据缺陷）；F-W2=规则正确、断言写错（B 必须再 pause，`pause_calls=2`）；F-W4b=断言与 ADR-12 不符（新周期 gen=1）。三条已按规则改正 | `decision.md` §12「ADR-5 W1/W2/W3 的表述更正」；`sim/cases_ownership.py` | `evidence/run/F-W1/`、`evidence/run/F-W2/`、`evidence/run/F-W4b/` |
| **P3-1** O-1 不得写成"W4 已恢复" | P3 | 改写 O-1：**无新参与者 ⇒ worker 保持 paused**；恢复只由下一个 acquire（或人工）发生；本卡不提供后台自愈 | `decision.md` §8 O-1 | V4-a 的 mid-state 实测即该窗口（`evidence/run/V4-a/`） |
| **P3-2** DECLARED 判活与 lifetime/真实探针重跑 | P3 | 写入"不授予范围" + **I-04-D 强制前置** | `decision.md` §12（判活模型）+ §8 O-9；`oracle.md` R2-3；`handoff.json.not_granted` | F-L1/F-L2d/F-L2e-*/F-W7/V4-a 已用 `lifetime` 单进程模式 |
| **P3-3** `hashes.txt` 自哈希不自洽 | P3 | `freeze_evidence.py` 排除自身与 `run-summary.json`，并在清单里注明排除项 | `sim/freeze_evidence.py` | `evidence/hashes.txt` |
| **P3-4** F-LK2 数值不可复现（10 vs 34） | P3 | `stress.py` 支持 `repeat`；F-LK2 连跑 5 次并输出 `finals`/`lost_updates`/`lost_updates_range`/`determinism` | `sim/stress.py`；`sim/scheduler.py` | `evidence/lock-and-legacy.txt` 的 F-LK2 记录（最终轮 finals `[12,19,7,26,43]`；更早一轮曾出现 261/200 的撕裂写） |
| **P3-5** 相位墙给可读数字 | P3 | 新增 `sim/phase_wall.py`（`phase_wall_seconds` + `max_lock_wait_seconds`，标注只报告） | `sim/phase_wall.py` | `evidence/phase-wall.txt` |
| **F-I04C-10 / ADR-2** `min(相位预算,60)` 与文中 `min(10,…)` 并存、与 I-04-A 关系未确认 | 不授予项 | **统一为一个公式** `lock_budget_for(x)=min(x,60)`（正文删掉 10.0 并加更正注记），明确"只消耗相位预算、不产生新预算"；新常数 60 登记 **OPEN-3 待裁** | `decision.md` ADR-2 正文更正 + §12 + §8 O-3 | 本轮 `max_lock_wait_seconds` 全部 < 9.2 s，未触发 `lease_lock_timeout` |

> **更正（C1 关闭；2026-09-20 追加，上表 P3-4 行原文保留）**：该行"证据"栏写的最终轮 finals `[12,19,7,26,43]` 是**过时值**，
> 且自身不相容（`200 - [12,19,7,26,43] = [188,181,193,174,157]` ≠ 同处给出的 lost `[197,185,191,198,14]`）。
> **最终证据轮的实测真值**（实施者独立复算，不采信正文）：finals `[16, 35, 10, 56, 18]` ⇒ lost_updates
> `[184, 165, 190, 144, 182]`，`lost_updates_range = [144, 190]`，`expected = 200`（8 进程 × 25 轮，
> 五轮 `lock_acquisitions` 全为 0）。依据：`& $PY -B sim/verify_flk2.py` ⇒ `evidence/flk2-recompute.txt`
> （13/13 PASS；A1–A8 逐轮从 `evidence/run/F-LK2-r{1..5}/` 的 `counter.txt`、`payload.*.json`、
> `counter.journal.jsonl` 复算，B1–B4 复核记录内部算术，C1 证明过时组不可复现）；
> 权威记录为 `evidence/lock-and-legacy.txt` **第 6 行**的 F-LK2 记录。
> P3-4 的**处置结论不变**（`stress.py` 支持 `repeat`、连跑 5 次、只作定性断言、输出 `determinism` 字段）：
> 本条只更正数字。"更早一轮 261/200 的撕裂写"与该过时组作为**历史**保留（261/200 不在最终证据轮内），
> 不删除、不改写，也不放宽断言。

## 2. v1 报告中的错误表述 —— 原文保留 + 更正说明（不删除）

**(a) 计数口径（v1 原文）**
> "协议套件：16 selected, 10 PASS / 6 with failing checks (raw: evidence/run-all.txt, parsed: evidence/failures.txt)"

**更正**：错误。同期 `evidence/run-all.txt` 的 SUMMARY 是 **9/16 例失败**（含 F-L1、F-L2c、F-L4a），
而 `failures.txt` 把真正失败的 F-L1、F-L2c 写成 PASS、F-L4a 静默跳过。根因是 `sim/parse_run.py`
用字面量 `{"case":` 搜索记录（漏读以其他键开头的记录）并跳过无 `checks` 的 harness-error 记录。
v1.2 真实计数：**协议套件 24 PASS / 0 FAIL / 0 harness-error / 0 failing checks**；
锁与 legacy 反例 **7 PASS / 0 FAIL**。

**(b) F-Lgw1 的机制（v1 原文）**
> "...but the dead entry is STILL on disk after the write (the prune is never persisted)"

**更正**：**"prune 不落盘"是错的** —— 现行 `_register` 把 `prune()+self` 一起写回，死条目**不会**留在文件里。
实测缺陷是：死 pid 列表被读成"无人"（`first=True`）⇒ 对已暂停的 worker 再 pause 一次，并**静默丢弃**该死参与者
（无任何诊断）。case 已按实测改写，并带 `v1_claim_corrected` 字段。

**(c) "规则缺口 vs 调度缺口"初判（v1 原文）**
> "F-W1/F-W2/F-W4b（崩溃后清死 participant liveness 记录的模拟步骤未全部对齐）" —— 归类为调度问题

**更正**：不成立。F-W1=**证据缺陷**（注入点 `after-pause-before-confirm` 已不存在，崩溃没发生、exit=0）；
F-W2=**断言写错**（ADR-10d 要求关掉孤儿周期后再开自己的周期 ⇒ `pause_calls=2`）；
F-W4b=**断言与 ADR-12 不符**（收尾 unlink ⇒ 新周期 gen=1）。

## 3. 实施者主动披露的其它更正

1. `sim/kernel.py` 一度同时存在两个 `protocol_paused_branch` 定义（旧签名覆盖新签名），表现为与 ADR-11
   相同的症状；现已合并，并由 `static_check.py` 的 **S4**（无重复模块级函数）静态守住。
2. v1.1 的 `ADR-10(c)`（认领周期 + 写义务）被 **ADR-10e**（owner 移交给存活 lease）取代；
   `released_took_ownership` / `released_with_pending_resume` 两个动作名在 v1.2 **不再存在**。
3. `F-L4a-foreign` 与 `F-W7` 场景重复，已删除，只保留 F-W7（并新增 V4-e/V4-f）。
4. 相位墙数字含测试栅栏等待（如 F-L1 的 21.25 s），**不是协议延迟**；协议侧可归因指标是 `max_lock_wait_seconds`。
5. F-L2a 的"同进程嵌套"现在由 `sim/nesting_probe.py` 真正跑出（一个进程两条 lease，独立释放，
   `exit_first_transfer=nest-scope-2`），并新增"prewritten 同 pid 对"的确定性对照。

## 4. 请 reviewer 优先攻击的点（v1.2）

1. **R3/R4/R5 的边界**：构造"owner 记录缺 pid + 无义务 + 我非 owner"（应落 R5）与
   "owner 有 pid 但探针 unknown"（应落 R5，不得当死亡）——核对 `owner_resumable` 的四种肯定判据。
2. **ADR-10e 的移交**：并发释放时 owner 移交是否可能指向"刚释放完、即将退出"的 lease（僵尸 owner）；
   R4 的探针是否足以兜住。
3. **单临界区的代价**：`worker-status`/`worker-pause` 现在都在锁内，F-L2d 实测 `max_lock_wait` 已达 9.16 s（8 并发）；
   请判定"锁预算 = 相位预算（上限 60）"是否把队列长度风险转成了延迟风险，并给 OPEN-3 的裁决意见。
4. **R5 的终态**：`paused` + 无可归因义务是**允许的终态**（fail closed）。请判定它与卡片第 5 条是否一致，
   以及 F-L4a 记录的 LIMITATION 是否可接受。
5. **判活模型**：DECLARED 的适用范围与 I-04-D 强制前置是否写够。
6. **计数口径**：复算 `evidence/failures.txt` 与 `run-all.txt` SUMMARY 是否一致（v1.2 应完全一致）。

## 5. reviewer 结论（**留空 —— 由独立 reviewer 填写，实施者不得代填**）

> **本节已填写（2026-09-20）**：独立 reviewer 的裁决正文在本文件**末尾逐字粘贴**
> （标题为 `## 5. reviewer 结论（独立 reviewer session，2026-09-20）`）。上面的 "留空 —— 由独立 reviewer 填写" 是 r3 的状态说明，
> 下面五行是当时的模板：作为历史保留，不要当作已填写的版本。

- 第二轮结论：`<accepted_scoped | changes_required | blocked | not_applicable_with_reason>`
- 复算过的 oracle：
- 未复现/未验证项：
- 授予的资格与明确不授予的资格：
- reviewer（agent id / 时间）：

> **本节已由独立 reviewer 填写（2026-09-20）；上面的 "留空" 抬头与五行模板是 r3 状态，作为历史保留。**
> 下面是 reviewer 报告里"可原样粘贴进 `review.md §5`"的裁决正文，由 `sim/patch_r5_docs.py` 从 `evidence/r5-reviewer-closeout-report.md` 的代码块中**逐字读出并粘贴，实施者未改一字**
> （源文件 sha256 `9dafd6cf566418cf4b5e1e9c21cb9147902fbe83dccd47147a5d66c20ef678d0`，副本来自 reviewer 的 `%TEMP%\closeout-review-20260920-035508\REPORT.md`）。

## 5. reviewer 结论（独立 reviewer session，2026-09-20）

- 第二轮结论：`accepted_scoped`（**限定：仅本 attempt 的设计文本与模拟结果**；不含任何产品实现/部署资格）
- 复算过的 oracle：
  ① 我在隔离副本（%TEMP%，不写生产仓）重跑协议套件：`cases_in_log=28 pass=28 fail=0 harness_error=0
     failing_checks=0`，其中 F-T1/F-T2/F-T3/F-T4 = 7/3/6/8 checks 全 PASS；`sim/static_check.py` S1–S4
     全 PASS；锁与 legacy 套件 `7 pass / 0 fail`。
  ② F-LK2：我复算 `200 − finals == lost_updates` 恒成立；`evidence/flk2-recompute.txt` 的真值组
     `[16,35,10,56,18] ⇒ [184,165,190,144,182]`（range [144,190]，expected 200）逐项自洽；旧组
     `[12,19,7,26,43] ⇒ [197,185,191,198,14]` 与之矛盾（C1 证伪）。我这一轮的实测组为
     `[16,6,25,115,8] ⇒ [184,194,175,85,192]`，与记录组不同但同守 `lost = 200 − finals`，且
     `determinism = NOT deterministic` ⇒ 该量只能定性断言，卡片口径正确。
  ③ 追加性：我亲自运行 `sim/verify_r4_appendonly.py` ⇒ `APPEND-ONLY CONFIRMED`（decision.md 重建
     sha256 `bb9bb0f4…`、review.md `8cc116bc…` 与改前快照逐字相等）；旧文本 `[12,19,7,26,43]`、
     `min(10.0, 相位预算)` 在 `decision.md:69/245/410` 与 `review.md:49` 均**原样保留**，更正在其后追加。
- 三项 still-required 的逐条处置结论：
  ① 错误码/超时用例 —— **关闭**。请求段 `code/action = lease_lock_timeout` 且 `writes=0`（F-T1，预算
     0.05 s，真外部持锁）；预算 0 时不尝试加锁（F-T2，journal 无 `lock_acq`）；清理段
     `cleanup_status=failed:lease_lock_timeout` + `action=release_fail_closed`，义务与 owner 证据保留、
     worker 仍 paused（F-T3）。
  ② 队列跨预算边界 + 队列成本 —— **关闭**。F-T4（6 参与者 × H=0.4 s，锁预算 1.0 s）⇒ 4 人超时零写、
     成功者 {P0,P2}、超时者绝不入 refcount、收尾 entries=[] 且 resume_required=false；队列代价以
     `budget_consumed_by_queueing` 记录（本次 {P0:0.0,P2:0.593}，attempt 记录 0.572，属调度浮动）；
     `(N−1)·H` 模型与"排队消耗下载预算"已写入 ADR-2 正文/§5 码表/§14 F-I04C-12 与 oracle R3-2。
  ③ 陈旧文本与 F-LK2 数字 —— **关闭**。见上"追加性"与"F-LK2"两条；正文旧值保留、更正追加，未删改。
- C1（§13.5 与 review §1 的 F-LK2 过时值）：**关闭**（真值 `[16,35,10,56,18] ⇒
  [184,165,190,144,182]`；`verify_flk2.py` 13/13；追加性证明见上）。其中"父代理已复算"与本次独立复算
  结论一致。
- C2 = OPEN-3：**仍为 owner 裁定项，且不阻塞本次签收**。待裁两项：(a) 上限常数 60（
  `lock_budget_for(x)=min(x,60)`）的命名与边界验收；(b) `worker-pause` 是否允许留在锁内。三处登记一致
  （`decision.md:396` 及 §8 O-3、`handoff.json.owner_gates[0]`「OWNER RULING item…
  does_not_block: does not block the accepted_scoped sign-off」、本文件 §6 OPEN-3 行）；
  `handoff.json.blocked_by = []`。owner 未裁前实现继续使用冻结值 60。
- 生产仓零改动：**确认**。`filing-fetch` porcelain 为空；`iso/filing-fetch` 的 118 个文件与生产同路径文件
  SHA256 全部相同且无 iso 独有文件（生产多出的 270 个文件均为缓存/e2e/CI/规划文档，代码与内容目录下无
  生产独有文件）；生产 `scripts/fetch_filing.py` = `046cc7dc…`（与卡片锚点相同）；`company-wiki`
  porcelain 仅 ` M CLAUDE.md` / ` M README.md`（既有用户改动 + I-00-D，非本卡）。
- 未复现/未验证项：真实 provider/worker/wiki 并发；DECLARED 判活与真实探针的等价性（I-04-D 前置）；
  POSIX/SMB 锁语义；真实 PID 复用检测；同进程多线程 scope；`worker-pause` 锁内位置的取舍（=C2）；
  `I04C-08` 的原始日志缺失（该声明已由我在 TEMP 副本复现 `8 passed, 109 deselected`，但 attempt 内
  无 raw log）。
- 需实现者同轮做的文字性 erratum（**不改变本裁决**）：
  E1 `review.md:24` 的 "最大等待 9.87 s、相位墙 13.2 s" 与所引 `evidence/phase-wall.txt` 不符，该文件
     记录为 `max_lock_wait_seconds=9.782719`、`phase_wall_seconds=13.386`，应改为 9.78 s / 13.4 s；
  E2 `sim/cases_timeout.py:206-211` 的 `lease in successful_ids is False` 是链式比较、恒为 False，该子句
     永不失败；`:213-216` 的"queue wait is reported"断言传 `True`。建议加强（本轮不影响结论，因为
     F-T4 的实质合取项与我的复跑一致）。
- 授予的资格：本 attempt 的设计文本与模拟结果（ADR-1..12 + R1–R5 分支表 + 错误码/超时与队列边界口径 +
  F-T1..F-T4 与既有 28 例的模拟通过事实）。
- **明确不授予**：任何产品实现/合并/部署资格；真实并发、真实锁语义与真实判活的等价性；生产 pause
  refcount 的任何写入；I-04-D/E 及以后的实现资格。
- reviewer：独立 reviewer session（本次收尾复核），2026-09-20。
