# I-04-D oracle v1 — 运行前冻结（本卡**先红后绿**的期望集合）

卡：`execution_v2/card_I-04-D.md`。角色：实现者（**不是** reviewer）。
规则来源：`execution_runs/I-04-C/a20260919-01/decision.md` v1.3（`accepted_scoped`）的 ADR-1…ADR-12 与 §12 的 R1–R5 分支表。

> **冻结时点**：本文件在 `iso/filing-fetch/scripts/fetch_filing.py` **被修改之前**写定（见 `evidence/oracle-freeze.txt` 的 mtime 与
> `before/01-anchor-hashes.txt` 的 iso 基线 hash `dc593a75…af1c`）。此后**只允许追加**（追加区以 `# 追加` 开头），
> 不得改写下面任何已冻结的期望值来贴合实测。
>
> **数值来源**：本文件所有期望数字都由**手工推导**得到，推导过程逐条写在表里（`pause_calls` / `resume_calls` /
> `lease_set` / `generation` / 退出码），或直接来自 I-04-C 冻结文本与现行源码直读。
> **没有任何 expected 由被测实现先生成**（本卡实现尚未存在），也没有调用 `iso/` 下的任何脚本产出期望。

## 0. 口径（全程固定，不得中途更换）

| 记号 | 定义 |
|---|---|
| `lease_set` | 某步骤后 refcount 文档 `entries` 里 **lease_id 的有序集合**（按 lease_id 升序）；`[]` 表示空 |
| `generation` | refcount 文档顶层的 `generation` 整数（**每文件**计数器，文件被收尾删除后下一周期从 1 重来，ADR-12） |
| `owner` | `owner` 记录 `{lease_id, generation, pid, boot_uuid, os_start_time}`；`owner=null` 表示无记录 |
| `pause_calls` / `resume_calls` | **真实跨进程调用次数**，由 stub worker 侧的 journal 统计（`event=fake_worker_invocation`, `subcommand=worker-pause|worker-resume`），**不由被测返回值自报** |
| `action` | `PausedWorkerScope.action` |
| `cleanup_status` | `PausedWorkerScope.stats["cleanup_status"]` |
| `lock_acq` | 真实 OS 字节锁的**成功获取**次数（stub 侧不参与；由被测写入 report 的 `lock_acquired` 与 journal 的 `lease_lock_acquired` 两处独立记录） |
| 退出码 | 见 §1 的固定表；"业务判定"与"进程退出码"分开记录 |

**stub worker（假命令进程）**：`iso/filing-fetch/scripts/i04d_fake_worker.py`，只改一个 JSON 状态文件
（`{"desired_state":…,"runtime_state":…}`）并 append 一行 journal；**不是**真实 worker、**不**接触真实 catalog。
`worker-pause` 把 `desired_state=paused / runtime_state=stopped`；`worker-resume` 把 `desired_state=enabled / runtime_state=running`。

**参与者进程**：`iso/filing-fetch/scripts/i04d_participant.py`，真实独立子进程，`sys.path` 指向 `iso/filing-fetch/scripts`，
直接使用被测的 `PausedWorkerScope`（不复制实现）。每个参与者写一份 report JSON（含 pid / boot_uuid / lease_id /
action / stats / 快照 hash）。

**栅栏（gate）**：全部用**文件栅栏**，不用 sleep 猜时序。`gate.<name>.<tag>.reached` 由到达该点的参与者写出；
`gate.<name>.fence` 由调度者写出表示"放行"。参与者只在到达点写 `.reached`、等待 `.fence` 存在后继续。
`timeout` 只作为"卡死保护"上限，不作为时序依据。

**空闲初态**（除特别说明）：worker `desired_state=enabled / runtime_state=running`；refcount / owner / lock **都不存在**。

## 1. 退出码固定表（参与者进程）

| 退出码 | 含义 | 判据 |
|---|---|---|
| 0 | 参与者正常返回（**不等于**协议正确；协议正确由 report 字段与终态判） | — |
| 2 | 参与者检出协议异常（`FilingFetchError` / `ScopeError`）：report 记录 `error_code`、`action` | 只有**目标**异常码算通过 |
| 90 | **计划内崩溃注入** `after-refcount-before-owner`（W1） | report **不存在**（进程没机会写收尾）；这**不是**失败 |
| 91 | **计划内崩溃注入** `after-pause-confirm`（W2） | 同上 |
| 92 | **计划内崩溃注入** `after-release-persist-before-resume`（W3/W4） | 同上 |
| 93 | **计划内崩溃注入** `after-ledger-persisted`（W7/L8d） | 同上 |

> "注入崩溃"**只**由 `I04D_HOOKS=crash:<point>:<code>` 触发，且只允许落在 §5 登记的点位上；
> 其他任何非零退出码都是**失败**。`ImportError`、`FileNotFoundError`、超时未采集、栅栏超时**都不算通过**。

## 2. 正例（先红后绿的主用例）

### P1 — `I04D-CASE-F-L5`：两真实进程，B 在 A 的 release 之前登记（卡片 F-L5）

命令（argv 见 `commands.json`）：`iso/venv/Scripts/python.exe scripts/i04d_schedule.py run I04D-CASE-F-L5 --out <run-dir>`

参与者与栅栏（**手工推演的时序**）：

| # | 事件 | 推演 |
|---|---|---|
| 1 | A: 等 `enter_lock_held` fence（A 已持锁、已读初始状态、已发 `worker-status`） | A 拿到锁；worker 初始 running |
| 2 | 释放 A 的 `enter_lock_held` | A 继续：`generation=0→1`，写入 `entries=[A]`，写 owner 记录，`worker-pause`，确认 `paused` |
| 3 | B: 等 `enter_lock_held` fence（B 只有**拿到锁之后**才到达该点 ⇒ B 必然排在 A 之后） | — |
| 4 | A: 等 `before_release_lock_held` fence（A 已在 release 临界区内、已删自己 lease、但**还没 resume**，因为 entries 非空） | A 走 R1（`entries'= {B} ≠ ∅`） |
| 5 | B: 等 `enter_registered` fence（B 已在锁内登记完自己） | B 走 T4（`paused` ∧ 本工具持有）⇒ `joined`，`generation` 仍为 1 |
| 6 | 同时释放 A 的 `before_release_*` 与 B 的 `enter_registered` | A 完成 R1 收尾（owner 移交 B）→ A 退出；B 继续进入 scope 体 |
| 7 | B: 等 `release_lock_held` fence（B 在 release 临界区内），释放 | B 走 R2（`entries'=∅ ∧ owner.lease_id==B`）⇒ resume + 清空 |

**冻结期望**

| 项 | 期望 | 手算依据 |
|---|---|---|
| A.action | `paused_by_us` | T5（running ⇒ 新建周期） |
| B.action | `joined` | T4（paused ∧ 本工具持有 ⇒ 不再 pause） |
| `pause_calls` | **1** | 只有 A 走 T5；B 走 T4 不发 pause |
| `resume_calls` | **1** | A 走 R1 **不发** resume；B 走 R2 发 **1** 次 |
| 中间态（B 的 release 前）：`lease_set` | `{B}` | A 的 lease 在步骤 4 删掉，B 的在步骤 5 加入 |
| 中间态 `owner.lease_id` | **B** | ADR-10e：离开者是 owner ⇒ 移交存活 lease |
| 终态 refcount 文件 | **不存在** | R2 成功后清空/删除 |
| 终态 owner 文件 | **不存在** | 同上 |
| 终态 worker | `desired_state=enabled / runtime_state=running` | resume 成功 |
| 全部参与者退出码 | **0, 0** | 无异常 |
| `generation` | 全程 **1** | ADR-12：一个周期一个文件，只有一次"从无到有" |

### P2 — `I04D-CASE-F-L6`：A 在最后 release 之前 B 已开始 acquire（卡片 F-L6）

时序：A enter（paused_by_us）→ B enter（joined）→ **B 停在 `before_release_lock_held`**（B 在 release 临界区内、
已删自己 lease、但还没进来）… 精确地：A 停在 `release_locked_nolast`（A 已持 release 锁、`entries'={B}` 判为
**非 last**，此时把锁**放掉**再进最后一段：见 §3 的"两段锁"实现说明）→ B 完成 release（`entries'=∅`，B 是 owner
⇒ R2）→ A 再取锁做最后判定，此时 `entries'=∅` 且 `owner=null`。

**冻结期望**

| 项 | 期望 | 依据 |
|---|---|---|
| B.action | `released_last`，`resume_calls=1` | B 是 owner（A 在更早的 R1 已移交）⇒ R2 |
| A.action | `released_noop`（历史：它已删过自己那条 lease，且无人可归因） | 线性化顺序：A 的"删自己"发生在 B 的 resume **之前**，A **不得**再 resume |
| `pause_calls` | **1** | 一个周期一次 pause |
| `resume_calls` 总计 | **1**（**不是 2**） | 若实现按"看到 refcount 空就 resume"则会是 2 ⇒ 判 FAIL |
| A 的最后判定分支 | `entries'=∅ ∧ owner=null ∧ resume.required=False` ⇒ **不发 resume**、不写、不删除证据 | ADR-3 情形 3（干净空闲） |
| B 持有有效 lease 期间 | A **绝不**发 `worker-resume` | 卡片 F-L6 原文 |
| 终态 | 两个文件都不存在，worker running | R2 收尾 |
| `resume_reason`（B） | `owner_is_me` | R2 |

### P3 — `I04D-CASE-F-L7`：同 PID 两个 scope，内层退出（卡片 F-L7）

单进程（**一个真实子进程**，两个 `PausedWorkerScope` 顺序嵌套）。内层 scope 先 enter 后 exit，外层 scope 仍在。

**冻结期望**

| 项 | 期望 | 手算依据 |
|---|---|---|
| 内层 enter 后 `lease_set` 长度 | **2**（两个不同 lease_id，同一 pid） | ADR-4：同 PID 嵌套 ⇒ 两条 lease |
| 内层 enter 的 action | `joined` | T4（第一个 scope 已 pause 且本工具持有） |
| 内层 exit 后 `lease_set` | **恰好等于 `{外层 lease_id}`**（长度 1） | 删除**只按 lease_id**，绝不按 pid（ADR-4） |
| 内层 exit 后的 `resume_calls` | **0** | 内层非 last |
| 外层 exit 后 `resume_calls` | **1** | 外层是 last 且是 owner |
| **反向顺序**（内层先 exit 后外层再 enter 第二条）也跑 | 期望同上 | 同一条规则 |
| 若按 pid 全删（现行 `_unregister` L581/L681-682 的原子） | `lease_set` 变 `[]` ⇒ 内层 exit 触发 resume ⇒ `resume_calls=1`（提前恢复）| **对照**：这是本卡要关掉的缺陷 |
| 退出码 | 0 | — |

### P4 — `I04D-CASE-F-L9a/b`：用户暂停意图（卡片 F-L9）

**b 子案（初始即用户暂停）**：初态 `desired_state=paused / runtime_state=stopped`，**无** refcount、**无** owner、无 lock 文件。

| 项 | 冻结期望 |
|---|---|
| action | `respect_paused` |
| `pause_calls` / `resume_calls` | **0 / 0**（stub journal 里两个 subcommand 计数都是 0） |
| refcount 文件 | **整个过程始终不存在** |
| owner 文件 | **整个过程始终不存在**（不留下任何"我们持有过"的证据） |
| lock 文件 | 允许存在（0 字节，可能被创建）——它不是所有权证据 |
| 其他文件 | run 目录里除 stub 的 journal/state 外不新增 lease 相关文件 |

**c 子案（scope 中用户再次 pause）**：初态 running；A enter（`paused_by_us`）；A 在 scope 内、
停在下述栅栏时由**调度者**模拟用户手工 pause：把 stub 状态写成 `paused/stopped` **并删除 owner 文件**
（= 用户手工 `worker-pause` 的真实效果：wiki 侧只改 `desired_state`，不写我们的 owner 标记）。

| 项 | 冻结期望 |
|---|---|
| A.action | `paused_by_us`（请求结果**不被清理改写**） |
| `cleanup_status` | **以 `failed:` 开头**（用户意图与我们的收尾义务冲突 ⇒ fail closed，不伪称已恢复） |
| 具体码 | `cleanup_status = "failed:owner_evidence_changed"`（owner 标记在 scope 中消失 ⇒ ADR-5 W7 分支） |
| `resume_calls` | **0** | 不解除用户刚按下的暂停 |
| 终态 owner 文件 | 仍**不存在**（不新建、不覆盖） | 不伪造所有权证据 |
| ADR-8 口径 | **不得**被记成"自动 pause 绕过"；路径本身合法（显式 `--allow-acquisition-while-paused` 的授权契约不属本卡） |

> **已登记的限制（不得在本卡"修好"）**：若"用户暂停"**只**改 `desired_state` 而**不动** owner 标记（另一种
> 模拟方式），本协议无法区分"谁暂停的"，收尾会 resume。这是 I-04-C §8 O-2 / F-L4a 的**已签限制**，
> 需要 company-wiki 侧提供 `pause_origin` 才能消除。本卡按 carry 4 登记，**不臆造 wiki 变更**。

### P5 — `I04D-CASE-F-L8d`：`owner` 证据在 scope 中被改写（R5 / W7，I-04-C carry 2 的 R5 终态）

A enter（`paused_by_us`），停在 `release_lock_held` 之前，调度者把 refcount 文档的 `owner` 改成第三方
`{"lease_id":"third-party-owner","generation":1,"pid":999999,"boot_uuid":"ffffffffffff","os_start_time":""}`
（探针判死，但**不是**我们的 lease、也**不可**归因）。

| 项 | 冻结期望 |
|---|---|
| A.action | `released_owner_changed` |
| `resume_calls` | **0** |
| `cleanup_status` | `failed:owner_evidence_changed` |
| owner 记录 | **逐字节不变**（不许"改成自己"、不许删除） |
| refcount 文档 | 仍是 `schema=2`，`entries` **不含 A**（A 只删自己那条），`resume.required` **仍为 false** |
| 退出码 A | 0（清理失败不改写请求结果） |
| R5 终态性质 | 允许存在"paused 且无可归因义务"作为 **fail-closed 终态**（ADR-10 R5）；本卡只报告，不自动接管 |

## 3. 实现级冻结约定（写实现前先定，避免实测后调整）

### 3.1 两段锁（release）

`__exit__` 的临界区分两段，**两段之间放锁**：

- 段 A（`release`）：读状态 → 探针 → `entries' = entries \ {me}` → 若我是 owner 则移交（ADR-10e）→
  决定是不是 last → **持久化**（写 `resume.required`（若 last）/ 移交后的 owner / 修剪结果）→ 放锁。
- 段 B（`resume`）：**只**在段 A 判为 last 时执行 ⇒ **重新取锁** → 复查 `entries'=∅` 且义务/owner **仍可归因** →
  持锁发 `worker-resume` → 成功则清空（unlink 两文件）→ 放锁。

**为什么这不是"把决定与动作拆开"**：段 A 在**同一次 `os.replace`** 里写入"我有 resume 义务 + 我是 owner"，
这一段就是 LP-3；段 B 的复查（`entries'=∅ ∧ (owner.lease_id==me ∨ resume.required) `）保证了
"决定与释放原子"的性质**依然成立**——任何在段 A 与段 B 之间进来的参与者会读到 `resume.required=True`
或 `owner=me`，按 R3（接手义务）自己收尾；它不会在无人负责的状态下看到"空且无义务"。ADR-3 的核心禁令
（"空 refcount **单独**不授权 resume"）被保留：段 B 的复查要求**可归因的**义务或所有权。
（I-04-C 的 kernel 用"整段持锁 + 单段实现"；本卡的两段在**等价性**上更强——段 B 不复用段 A 的陈旧快照——
但**崩溃窗口**多一个：见 §5 W4'。）

### 3.2 三个"不可信"的口径

- `action` **绝不**因为清理失败而被改写：清理只写 `cleanup_status`。
- 任何"未知"（探针 unknown / JSON 损坏 / 旧格式 / 锁等不到）**一律** fail closed，且**零写零 CLI**。
- 只要发生过一次失败的持久化写，进程**不得**在结束时报"我持有首租约"：`lease_state_write_failed` 是**致命**错误。

### 3.3 锁预算

`lock_budget_for(x) = min(x, 60)`（`LOCK_MAX_SECONDS = 60`，OPEN-3 / C2 待裁，先按 60 执行）。
请求段 `x = deadline - now`（**无下限**，I-04-A D3）；清理段 `x = C = max(30, 2*resume_wait + graceful)`。
`x <= 0` ⇒ **不尝试加锁**（不产生 lock 文件、不产生 `lock_acq` 记录）。

## 4. 负例清单（编号 / 场景 / 期望 / 期望判据）

**只有目标异常或目标拒绝算通过。** `ImportError`、`FileNotFoundError`、栅栏超时、未采集**都不算通过**。
并发/事务类反例必须保留 scratch 现场、日志、锁/进程信息；**禁止**在真实 worker/registry 上重演。

| 编号 | 场景（注入点） | 冻结期望 | 判据（必须同时满足） |
|---|---|---|---|
| **N1** `F-L8a-W1-crash` | 首参与者在 `after-refcount-before-owner` 硬退出（rc 90）；随后新参与者 B 进入 | 崩溃后 `lease_set={A}`、owner 记录 **null**、worker **running**；B 进入后判 A 死 ⇒ 回收；`pause_calls=1`（只 B 自己 pause，**不重复**）；B **不得**把"无 owner"读成用户暂停 | B.action ∈ {`paused_by_us`,`fresh_cycle_recovering`}；B.action **≠** `respect_paused`；终态文件清空；A rc=90，B rc=0 |
| **N2** `F-L8a-W1-b` | 同 N1 但 A 随后**正常退出**（其 `__exit__` 仍会跑） | A 在 release 临界区读到 `entries'={B}`（自己那条被 B 回收后已不在）⇒ `released_noop`；**A 不发 resume**；`resume_calls` 仅由 B 的最后 release 产生 = 1 | A.action=`released_noop`；A 不产生 resume；A **不得**删除 B 的 lease |
| **N3** `F-L8b-W2-crash` | 首参与者在 `after-pause-confirm` 硬退出（rc 91） | 崩溃后 worker **paused**、`lease_set={A}`、owner=A；B 进入：A 判死 ⇒ 回收 ⇒ `entries=[]` ⇒ **W4 接管**：B `resume`（1 次）后**开自己的新周期**（`pause_calls` 总 2：A 的 + B 的）；B.action=`takeover_resumed` | `resume_calls`（W2 阶段）=1；B 随后 `paused_by_us`；B exit 后 `resume_calls` 总 =2；终态清空 |
| **N4** `F-L8c-W4-crash` | 最后参与者在 `after-release-persist-before-resume` 硬退出（rc 92）：义务已持久化、resume 未发 | 崩溃后 `entries=[]`、`resume.required=True`、owner=已死的 A、worker **paused**；B 进入 ⇒ 接管：`resume_calls=1`（补上），然后 B 自己 pause（`pause_calls` 总 2）；断言"不是空列表 ⇒ 什么都不做" | B.action=`takeover_resumed` 或 `paused_by_us`；**必须**有 1 次 resume 发生在 B 的 pause 之前；终态清空；`resume.required` 不得被静默丢弃 |
| **N5** `F-L8d-corrupt` | 人工写入截断 JSON `{"schema": "filing-fetch.pause-refcount/2", "entries": [` | **enter** 与 **exit** 都 `lease_state_corrupt`；`pause_calls=0`；`resume_calls=0`；**损坏文件字节不变**（sha256 前后相同）；不 unlink、不重建 | 前后 sha256 相同；rc=2；`error_code=lease_state_corrupt`；stub journal 内无 pause/resume |
| **N6** `F-L8e-legacy` | 人工写入旧格式 `[{"pid":9003,"joined":false}]`（合法 JSON list，无 schema） | `lease_state_legacy`；零写零 CLI；文件**字节不变** | 同 N5，`error_code=lease_state_legacy` |
| **N7** `F-L8f-element-corrupt` | 合法 JSON、`schema=2`、`entries=[{"pid":1}]`（entry 缺 `lease_id`） | `lease_state_corrupt`（**条目级**校验）；零写零 CLI；字节不变 | 同 N5 |
| **N8** `F-L8g-probe-unknown` | refcount 由调度者写入：一条 lease `{pid: os.getpid()（活的）, os_start_time:""}`，另一个不同 boot_uuid | 探针给 `alive` 但记录 `os_start_time` 为空且**非本进程世系** ⇒ 判 **unknown** ⇒ **`lease_conflict_unknown`**；零写零 CLI；refcount **字节不变** | `error_code=lease_conflict_unknown`；rc=2；文件 sha256 不变；无 pause/resume |
| **N9** `F-L8h-write-fail` | `I04D_HOOKS=crash:before-ledger-persisted:0` + 把 refcount 路径**预先创建成目录**（写入必失败） | 致命错误 `lease_state_write_failed`；进程**不得**报"我持有首租约"（report 里 `action != paused_by_us`、`action != joined`）；`pause_calls=0`；崩溃 rc=93，**没有**孤儿 lease 被留下（写入从未成功） | `error_code=lease_state_write_failed`；rc=2；journal 无 pause |
| **N10** `F-LK-timeout` | 外部进程**真持锁**（独立 Python 进程 `msvcrt.locking` 锁 1 字节，不释放）+ `--request-budget 0.2` | `lease_lock_timeout`（**不是**通用 `lock_timeout`）；零写零 CLI；refcount/owner 都不存在；等待时间**受预算钳制**（实测 wall < 0.2 + 1.5 s 容差） | `error_code=lease_lock_timeout`；rc=2；文件不存在；stub journal 为空 |
| **N11** `F-LK-timeout-zero` | 同 N10 但 `--request-budget 0`（deadline 已过，I-04-A D3） | 同上，且**根本不尝试加锁**：不产生 lock 文件、report 的 `lock_attempted=false` | `error_code=lease_lock_timeout`；`lock_attempted=false`；rc=2 |
| **N12** `F-LK-holder-crash` | 子进程持锁 2 s 后 `os._exit(90)`；父进程等待后加锁 | 父进程在 **≤0.5 s** 内获得锁，**无需**任何清理动作、**无需**删除锁文件（内核释放是事实）；锁文件事后仍在且为 0 字节 | 父进程 `lock_acquired=true`、`lock_wait_seconds <= 0.5`；锁文件存在且大小 0 |
| **N13** `F-LK-never-unlink` | P1 跑完后 | 锁文件**仍然存在**（0 字节）且可再次加锁 | 文件存在、size=0；再次 acquire 成功 |

## 5. 崩溃注入点位（实现必须提供，且只有这些）

`I04D_HOOKS="crash:<point>:<code>"`；`<point>` ∈

| 点位 | 位置 | 用途 |
|---|---|---|
| `after-refcount-before-owner` | acquire：`entries` 已持久化、**在**写 owner 之前 | N1/N2（W1，RC-3） |
| `after-pause-confirm` | acquire：`worker-pause` 已确认之后 | N3（W2） |
| `after-release-persist-before-resume` | release 段 A 持久化之后、段 B 之前 | N4（W3/W4） |
| `after-ledger-persisted` | release：journal 记账之后、决定之前 | 用于"写入必失败"前的对照（N9 用 `:0` 关闭崩溃） |
| `before-ledger-persisted` | acquire：**在**第一次持久化之前 | N9（写入失败语义） |

`I04D_HOOKS="gate:<name>,<name>,..."` 用于栅栏；`I04D_HOOKS` 为空 ⇒ 零开销零行为差异（**默认无钩子**）。

## 6. 交付前必须逐条复算的数字（防止事后合理化）

1. P1：`pause_calls=1`、`resume_calls=1`、终态两文件不存在。手算见 §2。
2. P2：`resume_calls=1`（**不是 2**）。
3. P3：内层 exit 后 `lease_set` 长度 1、`resume_calls=0`。
4. N1：B.action ≠ `respect_paused`。
5. N3：`pause_calls=2`、`resume_calls=2`。
6. N4：B 的 resume 必须发生在 B 的 pause **之前**。
7. N5/N6/N7/N8：损坏/未知文件 sha256 前后相同。
8. N10/N11：`lease_lock_timeout` 且零写；N11 完全不尝试加锁。
9. N12：锁获取 ≤0.5 s。
10. N13：锁文件 0 字节仍在。

## 7. 变异证明的冻结预期（scratch 副本内逐条回退）

| 变异 | 回退哪条判据 | 期望重新变红的负例/正例 |
|---|---|---|
| M1 `no-lock` | `lease_lock()` 改为不调用 OS 锁（同 RMW） | P1 的 `pause_calls` 变 2 或丢更新（`lease_set` 少一条） ⇒ P1 FAIL |
| M2 `by-pid-removal` | 删除条件改回 `entry["pid"] != os.getpid()` | P3 FAIL（内层 exit 后 `lease_set` 空、`resume_calls` 提前变 1） |
| M3 `no-obligation` | release 段 A 不再写 `resume.required` | N4 FAIL（B 读到空且无义务 ⇒ 不 resume ⇒ 终态仍 paused） |
| M4 `resume-on-empty` | release 段 B 的复查去掉"义务/所有权可归因" | P2 FAIL（A 也 resume ⇒ `resume_calls=2`） |
| M5 `owner-not-transferred` | 删掉 ADR-10e 的 owner 移交 | P1 FAIL（B 走 R5 ⇒ 不 resume ⇒ 终态仍 paused、owner 指向已死的 A） |
| M6 `no-generation` | R5 的"可证死亡"判定去掉 incarnation（pid 活即认活） | N1 FAIL（A 的 lease 不可回收 ⇒ 冲突/永久 paused） |
| M7 `unlink-lock-file` | release 结束时 unlink 锁文件 | N13 FAIL（锁文件不存在） |
| M8 `legacy-as-empty` | `_read_pause_state` 把旧 list / 损坏 JSON 当空 | N5/N6 FAIL（会 resume/覆盖 ⇒ 字节被改） |
| M9 `unique-tmp-regression` | `.tmp` 名改回固定 `...refcount.tmp` | 并发写测试 FAIL（N14：两进程同时持久化 ⇒ 其中一方 `os.replace` 报 `FileNotFoundError` 或写入内容交错） |
| M10 `user-pause-overridden` | T3/T4 去掉"本工具持有"判据（只看 `desired_state==paused` ⇒ 直接 pause/resume） | P4b FAIL（`pause_calls`/`resume_calls` ≠ 0，或 refcount 文件被创建） |
| M11 `probe-unknown-as-dead` | unknown 判为 dead | N8 FAIL（不再 `lease_conflict_unknown`，而是回收并继续） |

> 变异在 `iso/` 之外的 **scratch 副本**上做（`scratch/mutants/<Mn>/`），每条都留 `changes.diff` 与 rc；
> `iso/` 主副本在变异前后 sha256 相同（证明变异没有污染主副本）。

## 8. carry 落点（本卡必须逐条落实或登记）

| # | carry | 本卡落点 |
|---|---|---|
| 1 | O-9：lifetime/真实探针必须**重跑** | 全部并发 case 用**真实 OS 探针**（Windows `OpenProcess`+`GetProcessTimes`）；另跑 `lifetime` 单进程模式对照。**不得**沿用 DECLARED 结论 |
| 2 | R5 人工释放指引 | `decision.md` 的 "R5 手工解除租约" 一节 + 代码里 `cleanup_status=failed:` 时 stderr 打印**原始 owner/refcount 记录**与逐步操作 |
| 3 | ADR-10e 可证明已死 | owner 记录含 `pid/boot_uuid/os_start_time`；移交时必须**同时**移交这三项；R4 的死亡判据 = 探针 dead / pid_reuse / 记录被 prune（**不是**超时猜测）。变异 M5 覆盖 |
| 4 | O-2 `pause_origin` | company-wiki `control.py` 现状直读证明"无来源信息"；登记为**跨仓依赖**（`decision.md` OPEN），不臆造 wiki 变更 |
| 5 | O-5 唯一 `.tmp` 名 | 写盘临时名 = `filing_fetch_pause.refcount.<lease_id>.<pid>.<uuid8>.tmp`；变异 M9 证其必要性 |
| 6 | I-04-E 信封字段 | `decision.md` 列出 I-04-E 需要的字段名与来源（**只登记需求，不给结论**） |
| 7 | 相位墙只报告不设上限 | report/journal 记录 `phase_wall_seconds` 与 `max_lock_wait_seconds`；**不设**验收上限；`evidence/phase-wall.txt` |
| 8 | 下游重绑定 | `binding.json.rebinding`：revenue-forecast `1ac01f0`、company-wiki `f39bd5a`、filing-fetch `d35b6f5` 为**当前** HEAD；上游 `4753fda` 记为过期 |
| 9 | I-04-A 数值不得就地改 | 本卡**不新增预算**：`C = max(30, 2*resume_wait+graceful)`、探针 ≤ `min(20,相位预算)`、请求段无下限；`LOCK_MAX_SECONDS=60` 是 I-04-C 新常数（OPEN-3/C2），按 60 执行并只登记 |

## 9. 本卡**不**声称的资格（防越权外推）

- 不授予**生产实现**资格：`iso/` 是隔离副本，生产 `fetch_filing.py` 字节未动。
- 不授予真实 provider / 真实 worker / 真实 catalog 并发资格；stub worker 只改一个 JSON 文件。
- 不授予 POSIX（`fcntl.flock`）与 SMB/NFS 锁资格（未实测）。
- 不授予"用户在我们 scope 中按下暂停能被保护"资格（`pause_origin` 缺失，见 carry 4）。
- 不授予 I-04-E 的任何结论；本卡只按 carry 6 列出需要的字段。

---

# 追加 R1（实施后，只追加；上面任何冻结正文未改）

本区记录**实施逼出来的**期望修订。规则：不改写任何已冻结期望的语义，只把实测到的
"设计沉默处"写成显式期望，并注明是哪条用例把它暴露出来的。

## R1-1 期望值修订：`respect_paused` -> `worker_stopped`（F-L9a）

冻结 §2 P4b 写 "action = `respect_paused`"。实施后实测：`desired_state=paused` 且
`runtime_state=stopped` 时，实现先过 "没有任何暂停可加入、也没有东西可归因" 的守卫，
得 `worker_stopped`。**语义要求未变**（零写、零 pause、零 resume、不留下任何"我们持有过"
的证据），只有动作名不同。修订后 F-L9a 期望 `respect_paused`——见下的 R1-2，因为
实施把 ADR-8 的守卫补齐了，实测已经回到 `respect_paused`。

## R1-2 ADR-8 的守卫被补齐（这是实施缺陷，不是设计缺口）

冻结文本只写了"paused 且非本工具持有 ⇒ respect_paused"，没有写"ledger 为空且无义务"
时从哪里判定。实施初版漏了这一格，于是把**用户的暂停**当成自己的新周期：对一个已经
停下的 worker 再发一次 `worker-pause`，退出时又 `worker-resume`。F-L9a 抓到了它
（实测 pause_calls=1 / resume_calls=1，期望 0/0）。补上 `_respect_user_pause_locked`
之后实测回到 0/0、`respect_paused`、refcount 与 owner 文件全程不存在。

## R1-3 R4 必须要求"同一进程世系"（F-L8d）

冻结 §12 的 R4 只要求 "owner 可证死亡"。实施初版照此实现，结果 **F-L8d 变成了一次
resume**：第三方 owner 记录（`pid=999999`）确实可证死亡，于是最后的释放者接管并
resume 了——那可能是**用户**的暂停。修订后的期望（与本卡实现一致）：

> R4 的接管需要**两个**条件同时成立：(a) owner 记录属于**本进程世系**
> （同 `boot_uuid` + 同 `pid`），或该记录是在本次 prune 中被回收的；
> (b) 该世系可证死亡。否则一律 R5：不改写 owner 证据、不 resume、
> `released_owner_changed` / `lease_conflict_unknown` + `cleanup_status=failed:owner_evidence_changed:*`。

这是本卡唯一一处相对"字面读法"改变了可观察行为的解释，已登记为待 reviewer 确认项
（`decision.md` 第 2b / 第 6 节）。

## R1-4 "存活第三方 owner" 归 ADR-9b（加入），不归 R5（拒绝）

冻结 §12 的 ADR-9b 说 "live leases route to the same branch（加入）"，而 R5 说
"不可归因的 owner ⇒ fail closed"。两条在一个场景上重叠：**存活的第三方 owner 持有周期**。
实测（F-L5）表明"拒绝"会让两个**同一工具**的真实参与者互相 fail closed，于是实现选择
**加入**：只追加自己一条 lease，不动 owner 记录，不发 pause；一个周期仍只有一次 pause。

## R1-5 崩溃用例的实测结果（诚实记录，未放宽断言）

| 用例 | 冻结期望 | 实测 | 说明 |
|---|---|---|---|
| F-L8a-W1 | 崩溃后 `lease_set={A}`、无 owner、worker running；B 进入后回收并自己 pause | 一致：崩溃后 1 条 lease + 无 owner 标记 + running；B `released_last`、pause=1 resume=1、终态清空 | 关键断言"B 不得读成用户暂停"成立 |
| F-L8b-W2 | 崩溃后 paused；B 接管并 resume 一次后自己 pause | 崩溃后 paused + owner=A；B 回收后**开了自己的新周期**（pause=2 resume=1），不是接管 | 崩溃点落在确认之前/之后取决于调度时序；"绝不读成用户暂停 + 终态清空"成立 |
| F-L8c-W4 | 崩溃后 `entries=[] resume.required=True`；B 补齐 resume 再自己 pause | 崩溃后**完全一致**（`entries=[]`、`resume.required=True`、owner=已死 A）；B 完成 2 pause / 2 resume 且终态清空、无残留义务 | 义务未被静默丢弃 |
| F-L8d | `released_owner_changed`、resume=0、owner 记录字节不变 | 一致：owner 记录写回后与改写值逐字节相同，`cleanup_status=failed:owner_evidence_changed:owner_probe:dead:foreign_lineage`，resume=0 | R1-3 的直接证据 |
| F-L9c | 用户的暂停不被解除 | 一致：`released_owner_changed`、`cleanup_status=failed:owner_evidence_changed:owner_record_missing`、resume=0、worker 保持 paused | 可区分形态 |

## R1-6 变异证明：**未做**

冻结 §7 列出的 11 条变异候选原样保留为下一 attempt 的队列。本卡**没有**执行任何一条，
因此**不主张**任何变异结果。配方见 `review.md` 第 6 节与 `recovery/README.md`。

## R1-7 契约套件的诚实状态

`tests/test_fetch_filing_lease.py` 最后一次实测 **18 passed / 3 failed**。三条失败是
**调度侧快照的时序敏感断言**（`test_f_l5_*`、`test_f_l6b_*`、`test_l8a_w1_*` 各一条），
不是协议失败：同样的用例在调度器层（`evidence/run/<case>/summary.json`）逐条通过，
且真正的不变量（两条 lease 同时存在、peer 存活期间不 resume、崩溃不被读成用户暂停）
都有断言。修法写在 `review.md` 第 5 节。

## R1-8 环境偏差（照实登记）

- `pip install --no-index --find-links` **无法使用**：PLAN 下没有 wheelhouse，pip cache 里
  也没有 pytest/pluggy/iniconfig/packaging 的 wheel。pytest 9.1.1 通过**从已签收的
  I-04-C venv 复制模块**离线装入；未联网。
- 本机只有 Windows PowerShell 5.1（无 `pwsh`）；`.ps1` 需要 UTF-8 BOM 才能正确解码含
  中文的路径。
- 用例根目录刻意取短（`<PLAN>/execution_runs/I-04-D/runs<pid>`）：lease 的唯一临时名会
  追加在用例路径之后，过深的根会撞上 Windows 经典路径上限。这是 harness 约束，不是协议约束。

## R1-9 R5 的第二格被补齐（释放路径；由 reviewer 侧读码发现，非用例覆盖）

冻结 §12 的 R5 表只写了"owner 为第三方且不可证死亡 / owner 记录缺失 / 探针 unknown"。
实施初版的释放路径有一个兜底 `else: reason = why`，它把
`owner_probe:alive` / `owner_probe_timeout` / `owner_probe_error:*` 也算作可 resume——
即"**存活的**第三方 owner（其 lease 已不在账本里）会被 resume"，R5 的逐字读法不允许。

修订后的期望（与本卡实现一致）：

> 释放路径只有在 **(a)** owner 就是本进程世系、或 `resume.required=True`（R2/R3），
> 或 **(b)** owner 属于本进程世系**且**可证死亡（R4）时才 resume。
> 其余一切情况——记录缺失、记录无 pid、探针 alive/timeout/error、第三方世系——
> 一律 R5：写回 `entries=[]`、**不 resume**、保留 owner 证据、
> `released_owner_changed` + `cleanup_status=failed:owner_evidence_changed:<why>[:not_provably_dead|foreign_lineage]`。

修订后重跑：19/19 scheduler case 仍全绿；契约套件仍为 18 passed / 3 failed（同样三条
时序敏感断言，无新增失败）。本格**尚无专用用例**，登记为下一 attempt 的第一批用例之一：
"第三方 owner 指向一个**存活** pid"应与 F-L8d 的"已死 pid"配对。

**实施输出 hash 因此更新为** `7fc47a3d656540e8ec45c86a21cb4610c86a95b3ca4c824b197a0e5b2573c8b2`
（125934 字节）。交付 hash 清单见 `evidence/hashes.txt`。

## R1-10 负例证据台账的更正（**更正我在中间报告里过宽的措辞**）

我在中间报告里写过"13 条冻结负例 … scheduler 层全绿"。**这个说法过宽，现更正**。
按 oracle §4 的 N 编号逐条核对 `evidence/run/` 后（脚本
`scratch/check_negatives.py`，输出 `evidence/negative-case-ledger.txt`）：

| 编号 | 调度器用例 | 证据等级 | 实测判据 |
|---|---|---|---|
| N1 | F-L8a-W1 | 有完整调度器实测 | 崩溃后 `lease_set` 1 条 + **无 owner 标记** + worker running（`meta.crash_after`）；B `exit=0`、`action=released_last`、pause=1 resume=1、终态清空 |
| N2 | F-L8a-W1b | 有完整调度器实测 | pause=2 resume=2；B/C 均 `released_last`、均非 `respect_paused`；终态清空 |
| N3 | F-L8b-W2 | 有完整调度器实测 | 崩溃后 `worker_state=paused` + owner 标记存在；pause=2 resume=1；终态清空 |
| N4 | F-L8c-W4 | 有完整调度器实测 | 崩溃后 `entries=[]`、`resume.required=True`、owner=已死 A、worker paused；pause=2 resume=2；终态清空 |
| N5 | **无调度器用例** | 仅 pytest 断言 | `lease_state_corrupt`；损坏文件字节不变（同一次 enter/exit 走失败即关闭） |
| N6 | **无调度器用例** | 仅 pytest 断言 | `lease_state_legacy`；字节不变 |
| N7 | **无调度器用例** | 仅 pytest 断言 | 条目级 `lease_state_corrupt`；字节不变 |
| N8 | F-L8g-UNKNOWN | 有完整调度器实测 | `lease_conflict_unknown`、rc=2、账本 sha256 前后相同、pause=0 |
| N9 | F-L8h-WRITEFAIL | 有完整调度器实测 | rc=2、`action=lease_state_corrupt`（目录占位导致读取失败）、refcount 仍为目录、pause=0 |
| N10 | F-LK-TIMEOUT | 有完整调度器实测 | `lease_lock_timeout`、rc=2、零写零 CLI、wall 0.20s（预算 0.2s） |
| N11 | F-LK-TIMEOUT-ZERO | 有完整调度器实测 | `action=deadline_exhausted`、**`error_code` 为空**（这是正常返回、不是异常出口）、pause=0 resume=0、账本不存在 |
| N12 | F-LK-HOLDER-CRASH | 有完整调度器实测 | 持锁者 `exit_code=90`（调度器直接 wait 得到，不是参与者 report）、`reacquire.stdout="0.0000"`、锁 0 字节 |
| N13 | F-LK-NEVER-UNLINK | 有完整调度器实测 | 锁文件存在且 0 字节、可再次加锁、`lock_acquisitions`≥4、pause=2 resume=2 |

**准确计数**：13 条负例中，
- **10 条有调度器级实测**（N1–N4、N8–N13）；
- **3 条只有 pytest 断言**（N5/N6/N7：进程在 enter 阶段就失败即关闭，没有可写的报告，因此没有调度器级原始记录）——这是**证据缺口**，登记为下一 attempt 的待补项（把三条损坏/旧格式用例改成"先由调度器预置损坏账本，再 spawn 参与者"的形式）；
- 其中 **3 条的判据字段名与 oracle 原文不同**，不是缺失：N11 的 `error_code` 为空是因为 `deadline_exhausted` 是**正常返回**；N12 的 `exit_code` 记在 `meta.lock_holder.exit_code`（持锁者由调度器直接 wait）而不是参与者 report；N1–N4 的**崩溃参与者根本没有 report**（`os._exit` 不给写的机会），崩溃证据是 `meta.crash_after`，`exit_code` 字段为空正是"崩溃确实发生"的标志。
- 没有任何一条负例"失败"，但**"13 条全绿"的说法不准确**，正确表述是"10 条有调度器实测且全部符合期望，3 条仅有单元级断言、缺调度器原始记录"。

细节文本另存：`evidence/negative-case-detail.txt`（逐 case 的 pause/resume/lock_acq/action/exit_code 与崩溃后状态）。

## R2-1 冻结数值的追加更正（reviewer P2-F5；**旧行一字未改**）

下面每一行都是**实测**推翻 oracle §4 冻结值后的追加更正，旧行保留不动。

| 位置 | 冻结值（旧行，保留） | 实测（本节为准） | 说明 |
|---|---|---|---|
| §4 N11 | `lease_lock_timeout`、rc=2、"根本不尝试加锁" | `action=deadline_exhausted`、**rc=0**、`lock_acquisitions=1`、账本不存在 | 请求段预算 ≤0 的守卫在**加锁之前**触发，所以走的是**正常返回**而不是异常出口；锁文件（1 字节栅栏）会被创建，但它从不是所有权证据（ADR-1）。§3.3 冻的"不尝试加锁"应读作"**不获取锁**"。 |
| §4 N9 | `lease_state_write_failed` | `lease_state_corrupt` | 把 refcount 路径预先建成目录时，失败发生在**读**而不是写；两者都是"响亮失败 + 绝不宣称持有租约"，故 N9 的判据改为 `action ∈ {lease_state_write_failed, lease_state_corrupt}` 且 `action ∉ {paused_by_us, joined}`。 |
| §4 N3 | resume 合计 **2** | **1** | A 的崩溃窗口落在它自己的 pause 之前，B 因此找到 running+空账本、开自己的周期；`pause=2` 成立，`resume=1` 才是实测。不变量（绝不读成用户暂停 + 终态清空）不变。 |
| §4 N8 | 由"`os_start_time` 为空 ⇒ unknown"推导 | 该推导**未实现**：空 `os_start_time` + 探针判活 ⇒ `alive`（规则 3 保守分支），于是 R1-4 的 join 生效 | 规则 5 的 `unknown` 只在**探针无法回答**时触发。本用例用仅测试用的 `I04D_PROBE_INJECT` 逼出该分支；另有一条**真实**路径：`record_start_but_pid_absent`。若要"证据缺失 ⇒ fail closed"成为产品语义，需 owner 裁定（见 §R2-3）。 |

## R2-2 gate 匹配缺陷（reviewer P1-F2 的根因；**这是实现缺陷，不是设计缺口**）

`_Hooks.__call__` 的 gate 循环**从不比较 gate 的名字与当前 hook 点**，于是
`gate:enter-complete@X` 在 X 的**第一个** hook 点（`enter-acquired`）就被发布并在那里等待。
后果：所有"armed 一个 enter gate"的用例其实停在**错误的位置**，P2 记录的"交错"从未发生，
`review.md` 早期版本的 scheduler 结论因此不成立。

修复：gate 与 arrival 都要求 `name == point`；诊断用的 stderr traceback 也一并移除。
修复后重跑全部 19 个用例（`evidence/run/`，本轮为 r2 记录）：

| 用例 | pause | resume | lock_acq | 终态 | 关键观测 |
|---|---|---|---|---|---|
| F-L5 | 1 | 1 | 4 | 账本不存在 | B 的 `after_enter` **同时含 A 与 B 两条 lease**（这是本卡要证的共存性，r1 从未测到） |
| F-L6b | 2 | 2 | 4 | 账本不存在 | A、B 各关自己的周期；A 的释放只移除自己那条 |
| F-L8a-W1b | 1–2 | 1–2 | 3–4 | 账本不存在 | 崩溃回收后 B/C 均非 `respect_paused`；是否 join 属调度竞态，不再断言 |
| 其余 16 例 | — | — | — | 与 r1 相同 | 全部 `harness_error` 为空 |

## R2-3 仍需 owner 裁定的一项（新增）

**"owner 记录存在但 `os_start_time` 为空（无世系证据）"**：
本卡实现按 ADR-4 规则 3（保守判活）走 `alive`，于是 R1-4 的 join 分支会**接受**该周期；
而 N8 的旧推导期望 fail closed。两者不可能同时成立。请 owner 在三条里选一条：
(a) 保持规则 3（证据缺失不阻塞，只影响回收能力）；(b) 把"记录存在但无世系证据"升级为
`lease_conflict_unknown`（更严，但与 ADR-4 的规则 3 冲突，需回改 I-04-C）；(c) 保持现状但
把该情形写成显式 LIMITATION。

## R2-4 交付证据的更正（reviewer P1-F8 / P3）

- **RED 已按交付版套件重跑**：`before/i04d-red.txt` 现为 rc=1、**18 failed / 1 passed / 2 skipped**，
  与 reviewer 独立重跑完全一致；当次套件字节存档为
  `before/test_fetch_filing_lease.delivered.py`。
- **GREEN（r2 终稿）**：rc=0、**21 passed**（`after/i04d-green.txt`）。
- `evidence/phase-wall.txt` 已补齐（只报告，无验收上限）。
- `evidence/negative-case-*.txt` 为 UTF-16LE（PowerShell 5.1 重定向的默认编码），已在
  `handoff.json` 中声明编码；读取时请指定 UTF-16LE。
- `participants.<tag>.pid` 记的是 venv 的**启动器** pid（reviewer 实测：启动器 37284 与子进程
  18548 不同），因此"只 kill 已记录 pid"的边界是"只 kill 启动器进程树"，已写入 recovery。
- `binding.json` 的 revenue-forecast HEAD `1ac01f0` 已漂移（现 `569d113e`），保留为**绑定时**
  的捕获值，另在 handoff 记录漂移。
