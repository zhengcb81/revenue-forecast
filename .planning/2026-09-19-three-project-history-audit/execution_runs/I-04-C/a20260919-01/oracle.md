# I-04-C oracle v1（运行前冻结；签署后不得为实现结果改写）

规则来源：`decision.md`（本卡 v1 / v1.1）。本文件只写**期望**，不写实现细节。
任何数字都由 `decision.md` 的状态机/计数口径手工推导，或来自现行源码（`fetch_filing.py` L409-610）的直读；
**没有**调用被测实现来生成 expected（模拟内核 `sim/kernel.py` 在期望冻结之后才写）。

> **v1.1 修订记录（在 §10 之前不动上面的语义）**：运行后 `decision.md` §10 修订了五处**实现级**规则
> （守卫顺序 ADR-9/9b、交接链 ADR-10、临界区内重读 status ADR-11、锁预算公式 ADR-2）。
> 本文件的 F-L1…F-W5 **语义期望未变**（谁该 resume、什么必须 fail closed、空 refcount 不授权 resume），
> 但 `action` **名字**有变化：`joined`（新增/明确）、`takeover_resumed`、`released_joined`、
> `released_took_ownership`（取代 v1 的"released_last 兜底"）、`released_with_pending_resume`、
> `fresh_cycle_recovering`（取代 `fresh_after_stale`）。逐条实测结果见 `evidence/failures.txt`。


## 0. 计数与判定口径（全程固定）

- `lease_set`：任一步骤后，refcount 中 lease 的**有序集合**（按 `lease_id` 排序）；`[]` 表示空。
- `owner`：`{generation, owner_lease, pid, boot_uuid, os_start_time}`（v1.3 更正：字段在 r2 扩展）；`generation` 是**每文件**计数器，每次"从无到有"的新周期 +1，文件被收尾删除后下一周期从 1 重新开始（**不是**全局单调；见 decision.md ADR-12 与 §R2-1、证据 `evidence/run/F-GEN/`）。
- `action`：`disabled | no_status | worker_stopped | respect_paused | joined | paused_by_us | takeover_resumed | released_joined | released_last | released_owner_changed | pause_failed | lease_fail_closed*`。
- **`pause_calls` / `resume_calls`：真实跨进程调用次数**（由 worker stub 侧的 journal 统计，不由被测返回值自报）。
- 每个"subprocess 退出码"与"业务判定"分开记录（START_HERE 要求）。
- 所有注入都是"调度脚本控时序"：等待点（gate）用文件栅栏，**不用 sleep 猜时序**（仅超时上限用秒）。

## 1. F-L1 — 两参与者基本序列（卡片表 F-L1）

初始：worker `running/enabled`；refcount/owner 不存在。A、B 为**两个真实子进程**（不同 pid）。

| 步骤 | 操作 | 冻结期望 |
|---|---|---|
| 1 | A enter（带栅栏：A 卡在 lease 临界区内） | `lease_set={A}`；`owner={gen:1, A}`；`pause_calls=1`；A.action=`paused_by_us` |
| 2 | B enter（B 也卡在临界区入口）→ 放开 A | A 完成；`lease_set={A,B}`；`gen=1`；`pause_calls` 仍 **1**（B 不 pause） |
| 3 | B 完成 enter | B.action=`joined`；`lease_set={A,B}` |
| 4 | A exit（栅栏放开） | A.action=`released_joined`；`lease_set={B}`；`resume_calls=0` |
| 5 | B exit | B.action=`released_last`；`resume_calls=1`；refcount 与 owner 文件**都不存在** |
| 合计 | — | 有效 lease 计数 1→2→1→0；pause 动作 **1**；A 退出 resume **0**；B 最后退出 resume **1** |

**对照（无锁，同 RMW，确定性注入）**：`racestop` 栅栏精确落在**现行代码的 prune→write 之间**（L566→L569）：
A 读到空列表、停在栅栏；B 完整跑完 enter（写 `[B]`、pause）；再放开 A ⇒ A 用自己读到的陈旧快照覆盖写 `[A]`。
**冻结期望**：终态 `lease_set={A}`（**B 的 lease 被丢更新**）、`pause_calls=2`（首参与者判定分裂）、
B 退出时 `empty=True` ⇒ `resume_calls` 最终 **2**（多一次 resume）；这些数字**与有锁版本逐个不同**。
这条是本设计存在的理由，也把"逻辑 RMW 反例"变成可复算的实测。

## 2. F-L2 — 同 PID 嵌套 / PID 复用 / 锁竞争

| 子案 | 注入 | 冻结期望 |
|---|---|---|
| **F-L2a** 同 pid 顺序嵌套 | 同一真实进程内两次 scope（`--two-scopes`），第二次在第一次 release 之前 | 两个不同 `lease_id` 同时在位（`lease_set` 长度 2）；第一次 exit 只删自己 ⇒ `lease_set` 长度 1、**该 lease 仍属于本进程**；第二次 exit 才 resume（`resume_calls=1`） |
| **F-L2b** 同 pid 不同世系（未验证 pid 复用） | 两条 lease 同为 pid 9001、`os_start_time` 不同（1000 vs 2000）；探针回 `alive=True, start_time=2000` | **规则 2**：记录 `1000` ≠ 现测 `2000` ⇒ 判 `pid_reuse` ⇒ 可回收（`pruned=[第一条]`），不阻塞 |
| **F-L2c** 同 pid 无世系证据 | 两条 lease 同为 pid 9002、`os_start_time` 都为空；探针 `alive=True`、无 start_time | **fail closed**：`lease_conflict_unknown`；**不写**、**不发** pause/resume；`lease_set` 保持两条不变 |
| **F-L2d** 锁竞争 | 8 个真实进程各 enter+exit；加一个"持锁 0.6 s"的第三方进程 | 全部 8 个退出码 0、无 `lease_lock_timeout`；`pause_calls=1`、`resume_calls=1`；最终 owner/refcount 清空 |
| **对照** legacy 同 pid 嵌套（F-L2a 同形） | 现行 `_unregister` 按 pid 全删（L581） | 期望**缺陷**：第一位 exit 后 `lease_set` 变 `[]`（第二位被误删）⇒ 第二位 exit 时 `empty=True` ⇒ **`resume_calls` 预期 1 实测 2**，且第二位 scope 内 worker 已被唤醒 |

## 3. F-L3 — 用户已暂停、且非本工具持有（卡片表 F-L3）

初始：`desired_state=paused`、`runtime_state=stopped`；**无** owner 标记、**无** refcount。执行一次显式授权下载。

| 项 | 冻结期望 |
|---|---|
| action | `respect_paused` |
| `pause_calls` | **0** |
| `resume_calls` | **0** |
| refcount / owner 文件 | 整个过程**始终不存在**（不留下任何"我们持有过"的证据） |
| 下载路径 | 仍带显式 opt-in（本卡只证 lease 层零动作，不重证 CLI 参数） |
| 误报禁止 | 该路径**不得**被记成"自动 pause 绕过"，也不得为了让 worker"恢复"而 resume |

## 4. F-L4 — scope 中用户意图变化 / 损坏 JSON / resume 失败（卡片表 F-L4）

| 子案 | 注入 | 冻结期望 |
|---|---|---|
| **F-L4a** scope 中 owner 证据变化 | exit 临界区内把 refcount 的 `owner` 改成第三方 lease | action=`released_owner_changed`；`resume_calls=0`；`cleanup_status=failed:owner_evidence_changed`；refcount **不被删除**（保留现场） |
| **F-L4b** refcount JSON 损坏 | 写 `{"schema": "…/2", "entries": [`（截断） | enter：action=`lease_state_corrupt`；`pause_calls=0`；**不覆盖损坏文件**（字节不变）；exit：`release_fail_closed`、`resume_calls=0` |
| **F-L4c** 旧格式 list | 写 `[{"pid":9003,"joined":false}]` | 同上但码为 `lease_state_legacy`；不写、不 CLI |
| **F-L4d** resume 失败（worker 拒绝） | stub：`desired_state` 被外部改成 paused ⇒ resume 被拒 | action=`released_last_resume_failed`；`cleanup_status=failed:resume_refused`；**保留** `resume.required=True` 与 owner 标记（不 unlink）；随后第三方 takeover ⇒ `resume_calls` 总计 2、`cleanup_status=restored`、文件清空 |
| **F-L4e** 元素级损坏 | refcount 合法 JSON 但 entry 缺 `lease_id`（如 `{"pid":1}`） | `lease_state_corrupt`（条目级校验），fail closed |

## 5. 崩溃窗口（decision.md ADR-5）

| 子案 | 崩溃点 | 冻结期望（崩溃后 + 下一参与者） |
|---|---|---|
| **F-W1** W1：写 refcount 后、写 owner 前 | 首参与者在 `after-refcount-before-owner` 硬退出（`os._exit(90)`） | 崩溃后：`lease_set={A}`、owner 文件**不存在**、worker 仍 running。下一参与者 B（探针 A=dead）：进入后 prune 掉 A、`gen=2`、`pause_calls=1`（B 自己 pause）；**B 不得**因"无 owner"判成 `respect_paused`（这是现行缺陷 W1 的正面反例） |
| **F-W2** W3：pause 后未确认 | 在 `after-pause-before-confirm` 硬退出 | 崩溃后：worker `desired_state=paused`、`lease_set={A}`、owner 存在。下一参与者 B（探针 A=dead）：`desired_state=paused` 且 entries 里 A 死 ⇒ prune 后为空 ⇒ 走 takeover：`resume_calls=1` 恢复，且 **B 不 pause**（B 只是确认/接管）；最终 `resume_calls=1`、文件清空 |
| **F-W3** W4：最后 release 后、resume 前 | 在 `wm-release-before-resume` 硬退出（已持久化 `resume.required=True`） | 崩溃后：worker 仍 `paused`、`lease_set=[]`、`resume.required=True`、owner 是我们（已死）。下一参与者 B：`paused` + `resume.required` ⇒ `takeover_resumed`、`resume_calls` 总计 **1**、之后 B 自己 pause（`pause_calls=1`），最终 B exit ⇒ `resume_calls` 总计 **2** |
| **F-W4** W4 双 resume 防线 | 最后参与者停在 release 临界区内、resume 之前（栅栏）；第二个参与者在门外等待 | 第二参与者在第一个的 `resume_required` 写入与 resume **之间**拿不到锁；第一个 resume 后第二个才进入；第二个看到 `desired_state=enabled` ⇒ 开**新代**周期（`gen+1`），**不**再补一次 resume。冻结：`resume_calls=1`（若实现按"看到 refcount 空就 resume"则有 2 次 ⇒ 判 FAIL） |
| **F-W5** W5：resume 超时 | 最后参与者 resume 延迟 0.3 s、预算 0.05 s | `cleanup_status=failed:resume_timeout`；**保留** `resume.required=True`；请求结果（enter 的 action）**不被改写** |

## 6. 锁与原子更新（ADR-1/ADR-2 的证据）

| 子案 | 注入 | 冻结期望 |
|---|---|---|
| **F-LK1** 有锁计数 | 8 进程 × 25 次 RMW（真实 OS 锁） | 末值 **=200**；无丢更新；journal 里 `lock_acq` 计数 = 200 |
| **F-LK2** 无锁计数（对照） | 同代码、`--no-lock` | 末值 **<200**（丢更新至少 1 次）；这是"读改写必须有互斥"的实测反例 |
| **F-LK3** 持锁者崩溃释放 | 子进程持锁 2 s 后 `os._exit(90)`；父进程等待后加锁 | 父进程在 **≤0.5 s** 内获得锁（无需清理动作、无需删除锁文件）⇒ 证明"内核释放"是本协议不需要打破锁的原因 |
| **F-LK4** 锁文件不被 unlink | F-L1 结束后 | 锁文件**仍然存在**（0 字节）且可再次加锁 |

## 7. 与 I-04-A/B 预算的组合（不得放宽已签值）

| 项 | 冻结期望 |
|---|---|
| 探针上限 | 每个探针预算 `min(20, 5, 相位预算)` ⇒ **≤20**（I-04-B F-B4B-01 的 `_PID_PROBE_MAX_SECONDS=20` 不被放松）；本卡只在探针上再收紧到 5 |
| 锁等待 | `lock_budget_for(相位预算) = min(相位预算, 60)`（v1.3 更正：旧文本写 `min(10, …)`；上限常数 60 = OPEN-3，见 decision.md §8 O-3 与 §14）；请求段相位预算无下限（I-04-A D3/F-D2），`≤0` 时不得加锁（模拟中 `request_budget=0` ⇒ `lease_lock_timeout`） |
| 清理预算 | resume 用 `C = max(30, 2×resume_wait + graceful)`；`cleanup_budget=30` 时 resume 延迟 0.3 s 应成功，`resume_budget=0.05` 才超时 |
| 相位墙 | **只报告**（记录 journal 首末 monotonic），**不设**验收上限（I-04-B carry 3） |
| 计数分账 | lease 动作不计入 `calls`（非 CLI）；探针计 `liveness_calls`、resume 计 `cleanup_calls`（本卡只做模拟层分账声明，产品字段归 I-04-E） |

## 8. 模拟资格声明（不夸大）

- 真实：跨进程 OS 文件锁（Windows `msvcrt.locking`）、真实子进程、`os.replace` 原子替换、真实退出码、
  真实并发队列（`evidence/run/F-L2d/journal.jsonl` 的 `lock_acq.waited` 逐条可复算）。
- **模拟**：
  - worker CLI：`sim/stub_worker.py` 只改一个 JSON 状态文件并写 journal；**不是真实 worker**。
  - **pid 存活探针：DECLARED（申报）模型**。每个参与者进程在启动时写
    `alive.<pid>.<holder>.<tag>.json`、正常返回时删除；崩溃（`os._exit`）会留下该文件。
    判活顺序：① 本进程自己的世系 ⇒ alive；② payload 里 scripted 的答案（合成 pid）⇒ 按答案；
    ③ 申报模型（存在该 pid 的申报文件且其中至少一条标 alive，且 OS 也认为该 pid 存在）；
    ④ 否则真实 OS 探针（Windows `tasklist`）；⑤ `unknown` ⇒ fail closed。
    **这条模型是必要的**，因为本测试里"参与者已经跑完 enter、由调度者稍后运行它的 release"是刻意安排的
    时序；真实 OS 探针会把这种进程报成 dead，从而误判 lease 过期。该模型的替代品不是"真实探针"，
    而是"一次调用内跑完 enter+release"（`lifetime` 模式，见下），本卡两种模式都用过。
  - 崩溃：进程以退出码 90 硬退出（`os._exit`），A 的 liveness 申报文件由**调度者**在崩溃后清除
    （`Harness.kill_declared`），以模拟"进程确实死了"。
  - 时钟：无虚拟钟；所有时序由文件栅栏（gate/fence）控制，不靠 sleep 猜。
  - 损坏输入：人工写入截断 JSON / 旧格式 list / 缺 `lease_id` 的条目。
- **不覆盖**：真实 wiki/provider/worker、真实 PID 复用（`GetProcessTimes` 探针未实测）、SMB/POSIX 锁、
  同进程多线程并发 scope、生产移植后的集成（I-04-D）。
- 结论只能支持"规则在调度表下的行为与冻结预期一致"，**不能**支持"真实并发概率已量化"。

---

# oracle r2 追加（v1.2；**只追加，不改上面任何冻结正文**）

复审 changes_required 要求的新增/更正期望。上面 §1–§8 的**语义**继续有效（谁该 resume、什么必须 fail closed、
空 refcount 不授权 resume）；下面记录 r2 新冻结的**动作名、分支与新增 case**。

## R2-1 动作名与分支（替代 §1–§5 里的旧名）

| 旧（v1/v1.1） | 新（v1.2） | 含义 |
|---|---|---|
| `released_took_ownership` + `deferred:ownership_transfer` | **不存在**；改为 `released_joined` + `ownership_transferred_to=<lease>`（ADR-10e）或 R5 的 `released_owner_changed` | 离开者若是 owner 则**移交**给存活 lease，不再"认领周期" |
| `released_with_pending_resume` | `released_last` + `resume_reason=inherited_obligation` | 接手别人写下的义务（R3） |
| `fresh_after_stale` | `fresh_cycle_recovering` | 有 lease 但 worker 在跑 ⇒ 保留 lease 开新周期（ADR-9b） |
| （无） | `resume_skipped_worker_running` | 接管时 worker 根本没暂停 ⇒ 不发多余的 resume（ADR-10d） |
| （无） | `owner_evidence_foreign` | owner 不可归因 ⇒ fail closed，不写不发（ADR-10 R5 / V4-f） |
| （无） | `released_owner_changed` | 收尾时 owner 不是自己且不可证死亡 ⇒ 不 resume、不改写证据（R5 / V4-e / F-W7） |
| `resume_reason` | 新字段：`owner_is_me` / `inherited_obligation` / `owner_probe:*` / `owner_pruned:*` | 收尾理由可审计 |

## R2-2 新增 case（复审要求，全部已跑通）

| case | 期望（冻结） | 对应发现 |
|---|---|---|
| **V4-a** | owner 死在义务写入临界区（`entries=[]`, `resume.required=true`, owner=已死 A）：终态**可以被下一个参与者关掉**——它 `takeover_resumed` 后拥有自己的新周期；`pause_calls=2`（A 的 + B 的）、最终 `resume_calls=2`、状态清空 | F-I04C-01 |
| **V4-e** | 我的 lease + 第三方 owner：`released_owner_changed`、`resume_calls=0`、**owner 记录逐字段不变**、不写义务 | F-I04C-02 |
| **V4-f** | 下游新参与者遇第三方 owner：`owner_evidence_foreign`、零写零 CLI、owner 标记保留 | F-I04C-02 |
| **F-W7** | 收尾临界区内 owner 被外部改写：`released_owner_changed`、不 resume、证据保留（ADR-5 W7/T10） | F-I04C-02 |
| **F-L2c-dead** | "死 lease + 无 marker + 非空 entries" **不是**用户暂停：接管并 resume 一次，之后自建周期 | F-I04C-06 |
| **F-L2e-stale** | v1 形状（锁外读状态）在既定交错下 **pause 两次**（RED 确认） | F-I04C-07 |
| **F-L2e-fixed** | 冻结形状同交错：B **join**、`pause_calls=1`、`resume_calls=1`、无 gate 超时 | F-I04C-07 |
| **F-GEN** | 两个连续周期的 generation **各自为 1**（跨文件不单调） | F-I04C-03 |
| **F-L4a** | scope 中用户再次 pause：API 无来源信息 ⇒ 我们的收尾会 resume（**记录为限制**，写入 `LIMITATION` 与 I-04-D 依赖） | 卡片第 5 条 |
| **F-L2a-legacy** | 现行机制：公开入口在 paused worker 上返回 `worker_stopped`（refcount 路径在生产不可达）；其 unregister 原子按 pid 删掉两条同 pid lease 并 unlink owner 标记 | ADR-1/ADR-4 反例 |
| **F-Lgw1** | 现行 register 原子：死 pid 列表被当作"无人"⇒ 再 pause 一次，并**静默丢弃**死条目（v1 说"prune 不落盘"是错的，已更正） | ADR-4 反例 |

## R2-3 判活模型（更正与范围，r2 P3-2）

- 判活优先级：① 本进程世系；② payload 注入答案（合成 pid）；③ **DECLARED 申报模型**：参与者启动写
  `alive.<pid>.<holder>.<tag>.json`、正常返回删除、崩溃留下，且 **OS 也必须认为该 pid 存在**；
  ④ 真实 OS 探针；⑤ `unknown` ⇒ fail closed。
- **不授予**"DECLARED 与真实探针等价"。**I-04-D 强制前置**：用真实探针或以 `lifetime` 单进程模式重跑
  全部并发 case（本轮 F-L1/F-L2d/F-L2e-*/F-W7/V4-a 已用 lifetime 模式；仍属模拟，不构成生产资格）。

## R2-4 计数口径（r2 F-I04C-04）

- 判定与计数一律以 `sim/parse_run.py` 的输出为准：它输出 `cases_in_log / pass / fail / harness_error / failing_checks`，
  并把每条 `{"case": …}` 与 `{"case": …, "error": …}` 都计入；以 `{"case","exit","seconds"}` 开头的
  scheduler SUMMARY 行**不算** case 记录。
- v1 的"10 PASS / 6 failing"作废（解析器漏读以非 `case` 键开头的记录并跳过 harness-error）。
  真实计数见 `decision.md` §13.7。
- **无锁对照 F-LK2 的数字是定性的**：同一配置连续 5 次 finals `[16, 35, 10, 56, 18]`（⇒ lost `[184, 165, 190, 144, 182]`，与 finals 相容；来源 `evidence/lock-and-legacy.txt` 的 F-LK2 记录），复审独立复跑得 34
  ⇒ 只有"无锁必然丢更新"可作断言，任何单一数字不得写成结论。

## R2-5 相位墙（r2 P3-5）

- 仍**只报告不设上限**；`evidence/phase-wall.txt` 给出每 case 的 `phase_wall_seconds` 与 `max_lock_wait_seconds`。
- 注意读法：F-L1 的 21.25 s、F-L2e-fixed 的约 1 s 等**包含测试栅栏（人为等待）时间**，不是协议延迟；
  协议侧的可归因指标是 `max_lock_wait_seconds`（本轮全部 < 9.2 s，且在相位预算内）。

---

# oracle r3 追加（v1.3；**只追加，不改上面任何已冻结正文**）

## R3-1 锁超时的冻结期望（对齐错误码；F-I04C-11）

- **错误码唯一**：锁等待超时一律是 **`lease_lock_timeout`**（**不是**通用 `lock_timeout`）。
  请求段 ⇒ `code=lease_lock_timeout` + `action=lease_lock_timeout`；
  清理段 ⇒ `action=release_fail_closed` + `cleanup_status=failed:lease_lock_timeout`。
- **零副作用**：超时**不写** refcount/owner、**不发**任何 CLI；lease 状态文件字节不变；等待受相位预算钳制；
  journal 记 `{"event":"lock_timeout","name":"lease","code":"lease_lock_timeout","budget":…}`。
- **预算 0**：`request_budget <= 0`（deadline 已过，I-04-A D3）⇒ **根本不尝试加锁**（journal 无 `lock_acq`）。
- 新增 case 与期望：
  | case | 冻结期望 | checks |
  |---|---|---|
  | **F-T1** | 外部进程真持锁 + `request_budget=0.05` ⇒ `lease_lock_timeout`、零写零 CLI、状态字节不变、等待有界 | 7 |
  | **F-T2** | 同上但 `request_budget=0` ⇒ 同上，且**未尝试加锁** | 3 |
  | **F-T3** | 请求已 `paused_by_us`；外部先占锁再放行清理段（`cleanup_budget=0.3`）⇒ 请求结果不变、`release_fail_closed`、`cleanup_status=failed:lease_lock_timeout`、义务与 owner 证据保留、worker 仍 paused | 6 |
  | **F-T4** | 6 个 enter-only 参与者、注入保持 H=0.4 s、锁预算 1.0 s ⇒ ≥1 个 `lease_lock_timeout` 且零写；成功者集合 = refcount 的 lease 集合；超时者绝不出现在 refcount；成功者释放后无悬挂 lease/义务 | 8 |
- 证据：`evidence/run/F-T1/` … `evidence/run/F-T4/`（每 case 含 journal、参与者 stdout/stderr、状态快照）。

## R3-2 排队代价（F-I04C-12）

- 排队等待 ≈ **(N−1)·H**（H = 单次临界区保持时间，含 `worker-status` 子进程与最长 graceful 5 s 的 `worker-pause`）。
- **N·H > 锁上限（`LOCK_MAX_SECONDS=60`，或更小的相位预算）⇒ 队尾参与者 fail closed**（`lease_lock_timeout`，
  零写、可安全重试）。F-T4 即该边界的确定性 case。
- **排队在消耗下载预算**：`lock_wait` 属于请求段；F-T4 报告 `budget_consumed_by_queueing`，
  F-L2d 的 8 并发实测最大等待 9.87 s、整相位墙 13.2 s。**这是协议的真实代价**，
  **不得**通过放宽锁或跳过互斥来规避（缓解手段是重试/降并发）。

## R3-3 OPEN-3 的读法（采纳复核建议，待 owner 确认）

`LOCK_MAX_SECONDS = 60` 是**本卡新增的等待上限常数**（防病态等待），**不是新预算**：
请求段相位预算（默认 900 s）通常远大于 60，故不构成额外约束；它实际封顶的是
**清理段（`C` 可达 85 s）与短 deadline**，且 `≤0` 时拒绝等待（F-T2 已证）。
与 I-04-A v2 三条已签值（探针 `min(20,相位,5)`、请求段无下限、清理段独立 `C`）无冲突。
**待裁**：① 命名与边界验收的确认；② 是否允许 `worker-pause` 留在锁内（本卡维持锁内，
否则两个参与者可能同时自认首参与者）。



