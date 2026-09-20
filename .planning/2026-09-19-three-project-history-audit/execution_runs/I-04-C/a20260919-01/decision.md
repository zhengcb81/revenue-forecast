# I-04-C 决议案 v1 — 跨进程 lease / 所有权 / 恢复协议（冻结）

卡片：`execution_v2/card_I-04-C.md`。角色：filing-fetch 负责人（wiki 并发 reviewer）。执行门：**高级 reviewer 先定案；本卡不实施产品**。

依据版本：`filing-fetch` HEAD `d35b6f5b09f1a7dad37d226504bf998802a852d7`（`d35b6f5`），
`scripts/fetch_filing.py` sha256 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`（与卡片四个锚点、I-04-A 依据版本、I-00-B 绑定一致；见 `binding.json`）。
本文件只做设计，**不改任何产品代码/默认值/生产 lease 文件**。规则先冻结（本文 + `oracle.md`），模拟后置（`evidence/`）。

> 本卡不签署"已验收"。以下规则是给独立并发 reviewer 复核的**待批提案**；`review.md` 的判决栏留空（PENDING）。

---

## 0. 签署前统一词义（卡片原文要求，本文全程使用）

| 术语 | 定义 | 不是什么 |
|---|---|---|
| **lease_id** | 一次参与者登记的唯一标识（UUID4，hex 24 字符），随登记写入 refcount | **不等于进程 ID**；同一进程的两次登记各有 lease_id |
| **process incarnation（进程世系）** | 一个**进程实例**的标识：`{pid, os_start_time, boot_uuid}`。`os_start_time` = OS 报告的进程创建时间（Windows `GetProcessTimes` 的 FILETIME 起点，100ns 单位），`boot_uuid` = 每次进程启动生成一次的随机世系 UUID，随每条 lease 持久化 | **不等于 lease_id**；一个世系内可有多次登记（同 PID 嵌套） |
| **owner generation（所有权代号）** | refcount 顶层整数 `generation`。每次"从无到有"地建立一次**新** pause 周期（`busy→paused` 的那一次转换, RC-3）时 +1。只有代号等于当前 `generation`、且其 lease_id 是"最后一个参与者"的进程才有权 resume | 不是 worker 实例号，不是 pid |
| **worker incarnation** | company-wiki 侧 `desired_state` 的取值序列（`enabled`/`paused`）与 CLI 的 `stop_requested_for` token。本协议**只读不改**其语义 | 与 owner generation、lease_id 都不同 |
| **用户暂停意图** | 由人（非本工具）造成的 `desired_state=paused`。本协议把"存在 owner 标记 ∧ refcount 非空 ∧ schema=2"当作**本工具持有**；其余 `paused` 一律是用户/外部意图 | 不能用"没有 owner 文件"反推"是我们暂停的" |
| **resume 义务** | 一次 pause 周期必须在 **refcount 变空的那一次临界区内**被记下"需要恢复"，并由唯一持有 `generation` 的最后一个参与者执行 | 不是"看到 refcount 为空就 resume" |
| **fail closed** | 状态有歧义/证据缺失/探针失败时：**不**写 lease、**不**发 pause/resume、请求以明确错误码失败，并给出可手工恢复的诊断 | 不作为空列表、不猜、不静默降级 |

---

## 1. 现行机制与三处非原子读改写（本设计要关掉的东西）

现行实现（L409-610）：

- `_register`(L565)：`entries = _prune_pause_entries()` → `first = not entries` → `append` → `_write_pause_entries`（临时文件 + `replace`）→ `first` 时写 owner 标记（L571-576）。
- `_unregister`(L579)：`_prune_pause_entries()` → **按 pid 全删**（L581）→ 空则 unlink refcount **再** unlink owner（L582-587）。
- `__exit__`(L592)：`_unregister()` 返回 True（我们是最后一个）→ `worker-resume`（L597-603）。
- 锁：**无**。互斥完全靠"读—判断—写"。

**三处非原子读改写（本卡要冻结的正是它们的原子边界）**

- **RC-1 `_register`**：`read(空) → first=True → append(write)` 之间没有互斥。两个进程同时进 ⇒ 两个都判 `first=True` ⇒ 各自 `_write_pause_entries` 覆盖式写入 ⇒ **丢一条 lease**（计数 1 而非 2），并且**两个都以为自己该 pause**（重复 pause）或**只有一个的 lease 存活**。
- **RC-2 `_unregister` 的"最后一个"判定**：`prune → 删自己 → 若空则 unlink(owner) → 返回 True → resume`。在 `unlink(owner)` 与 `resume` 之间（L585→L597），新参与者可以完成 `is_file(owner)==False` 的检查并走"全新 pause"分支（L531-538）⇒ 在旧 owner 的 resume 之后再执行一次 pause，而旧 owner 的 `worker-resume` 可能落在新周期之内 ⇒ **跨周期的 resume/pause 交错**；更坏的是新参与者认为自己拥有 owner（写新 owner），旧 owner 的 resume 却把 worker 唤醒 ⇒ 新参与者 scope 内 worker 是 running，`operation.lock` 又回到被占用的老问题。
- **RC-3 重新 `pause` 与 owner 标记的可见顺序**：`_register` 先写 refcount（含自己）再写 owner（L569→L571-576），中间崩溃 ⇒ 有 lease、无 owner ⇒ 后到者按 L531-535"`paused` 且无 owner"判成**用户暂停**（`respect_paused`），于是**永不 resume** ⇒ worker 永久停摆；反之 `_unregister` 先删 owner 再删 refcount 的窗口同理。**现行代码把"owner 文件不存在"当作用户意图的证据，这个证据在多进程下会被崩溃窗口伪造。**

> 现行代码的两个"看起来对"的论据在本卡被明确否决：
> (a) "pid 存活即安全" —— pid 会复用（F-L2 场景 2）；(b) "空 refcount ⇒ 该 resume" —— 空 refcount 也可能是别人正在 resume 或别人已接管（见 §3 RC-4）。

---

## 2. 决策登记表（每项：选项 / 选择 / 理由 / 反例 / 兼容影响 / 拒绝的替代）

### ADR-1 跨进程互斥实现

- **选项**
  - A. `threading.Lock` / 进程内锁。
  - B. 目录/文件"存在即锁"（`os.mkdir` 或 `os.open(O_CREAT|O_EXCL)`），崩溃后靠"陈旧判定 + 删除"清理。
  - C. **OS 字节范围锁**（Windows `msvcrt.locking` LK_NBLCK，POSIX `fcntl.flock`）加在一个**永不被删除**的专用锁文件上；崩溃由内核自动释放。
  - D. `portalocker`/`filelock` 等第三方库，或把租约放进 SQLite/registry。
- **选择：C**。锁粒度 1 字节 @ offset 0；锁文件 `.source_catalog/filing_fetch_pause.lock`，代码**永不 unlink**（`unlink` 与"另一进程已 open 同一 inode"组合会在 Windows 上产生"两个进程各持一把锁"的分裂，这是 C 唯一需要额外纪律的地方）。
- **理由**：只有 C 把"持锁者已死"变成**内核事实**——进程终止（含 `TerminateProcess`、栈溢出、断电外的所有崩溃）时 OS 释放锁，因此**不需要"打破锁"这个动作**。B 的清理动作本身是另一个读改写（判断陈旧 → 删除 → 建锁），在"删除"和"建立"之间仍有窗口，且必须依赖 pid 探针结论，等于把 §4 的 pid 复用风险搬进锁路径。
- **反例（本卡模拟）**：`sim/stress.py` 无锁模式（同 RMW、无 OS 锁）丢更新；有锁模式 8 进程 ×25 次 = 200/200。
- **兼容影响**：新增一个 0 字节锁文件；退出时**不删**（否则分裂）。旧代码不认识它，也不会删它（旧代码只 unlink 两个固定文件名）。仓库 `.gitignore` 已忽略 `.source_catalog/`。
- **拒绝的替代**：A（不能跨进程）；B（把 stale 判定搬进锁路径，见上）；D（新依赖 + 与 I-04-C"不得弱模型自选锁库"冲突；SQLite 会产生第二个持久化权威）。
- **平台范围**：`nt` 走 `msvcrt`，`posix` 走 `flock`。**未在 POSIX 上实测**（本机 Windows）；POSIX 分支按同一接口实现但资格仅到"未验证"（见 §11 O-6）。

### ADR-2 锁文件路径、锁顺序、超时

- **路径**：`<root>/.source_catalog/filing_fetch_pause.lock`（与两个 lease 文件同目录；目录已由 `_write_pause_entries` 的 `mkdir(parents=True, exist_ok=True)` 保证）。
- **锁顺序**：**只有一把锁，且不嵌套**。全协议内**唯一**的加锁点是"lease 临界区"；worker CLI 子进程**不参与**锁（它们不知道锁文件）。因此不存在 A→B→A 的环，**死锁结构上不可能**。
- **超时**：`acquire(timeout)` 非阻塞轮询：首次立即试，之后固定 0.05 s 间隔（**不做指数退避**——总预算已被下面的 min 钳住，退避只会把重试次数变少而增加尾延迟）。超时值：
  `lock_budget = lock_budget_for(相位预算) = min(相位预算, LOCK_MAX_SECONDS = 60)`；请求段相位预算 = `deadline - now`（**无下限**，I-04-A D3），清理段 = `C`（I-04-A D2）。`<=0` 时**不得尝试加锁**（请求段直接 deadline-exceeded）。
  > **v1.2 更正（r2 F-I04C-10）**：v1 正文此处写 `min(10.0, 相位预算)`，而 §10 又写 `min(相位预算, 60)` —— 同一文本两个公式，属实施者错误；**以本条为准，10.0 作废**（v1.1 实测：8 个并发参与者时第 6–7 位的排队等待即超过 10 s，整个请求 fail closed）。`LOCK_MAX_SECONDS = 60` 是本卡**新引入的常数**，不在 I-04-A v2 已签值内，登记为 **OPEN-3**（见 §8）待 owner 裁定；它与 I-04-A 的关系只有一条：**锁只消耗相位预算，绝不产生新预算**（§ADR-6）。
- **超时后果**：**fail closed** —— 不写 lease、不发 pause/resume，错误码 `lease_lock_timeout`（请求段）或 `cleanup_status=failed:lease_lock_timeout`（清理段）；诊断含锁路径、等待秒数、建议（本人不在场时可由人直接查看是否有卡死的 filing-fetch 进程）。
- **关键取舍**：**持锁期间允许发 `worker-resume`**（CLI，超时 = `C`）。这是 ADR-3 的必要条件：只有把"最后 release"与"resume 决定"放进同一个临界区，才能让新参与者**不可能**在"refcount 已空、resume 尚未发生"的窗口里插入。
  - 反例检查：`worker-resume` 最长阻塞 `C = max(30, 2×resume_wait + graceful)`（默认 30 s，用户可把 `--worker-resume-wait-seconds` 调到 40 ⇒ 85 s）。期间其他参与者最长等 `lock_budget` 后 fail closed —— **可接受的退化是"新请求报错重试"，不是"状态损坏"**。
  - **禁止**：在持锁期间发 `resolve`/`ensure`（长动作，与 lease 无关）。lease 临界区里只有：本地文件读写、pid 探针（有界，≤ min(20,相位,5)）、`worker-resume`（仅收尾时）。
  - **v1.2 修订（r2 F-I04C-07）**：v1 正文把 `worker-status` 与 `worker-pause` 也列入"持锁期间禁止"。ADR-11 要求**状态读取必须发生在同一个临界区内**（否则分支用的是陈旧快照），因此 `worker-status` 与 `worker-pause` 现在是**进入临界区后**的动作，二者都以探针/清理相位预算为上限、有界。这也把"进入临界区"变成一次完成 {读状态, 读 lease, 判定, 修剪, 登记, owner 标记, pause, 确认} 的单一临界区（见 §12 ADR-11）。
- **拒绝的替代**：①不持锁发 resume（回到 RC-2/RC-4 的窗口）；②两把锁（"状态锁"+"resume 锁"）——锁顺序复杂化且不解决"决定与释放必须同时原子"；③持锁期间发 `worker-pause`（首参与者最长 graceful 5 s 阻塞其他参与者，且 pause 失败路径还要 resume，临界区膨胀）。

### ADR-3 "最后 release" 与 "新 acquire" 同时到达的判定（本卡的核心）

**冻结规则（唯一合法顺序）**：

```
临界区 K（持锁）：
  entries = prune(read_entries())            # 探针在锁内、有界
  entries = [e for e in entries if e.lease_id != me.lease_id]     # 只按 lease_id 删，绝不按 pid
  last = (entries == [])
  if last:
      state.resume = {"required": True, "generation": state.generation,
                      "lease_id": me.lease_id, "phase": "resume_pending"}
      # ↑ 先持久化"我有 resume 义务"这一事实，再离开临界区；这是崩溃可恢复的唯一依据
  write_entries(entries, state)
  if last: resume()        # 仍在锁内：超时 = C，成功/失败都记 journal
  if last and resume 成功: unlink(refcount); unlink(owner); 或写回 {schema:2, generation, entries:[], owner:null}
  unlock()
```

- **新参与者 acquire 在 `last` 判定之后到达**：它必须等锁（此时旧 owner 仍在临界区内，可能正在 resume）。拿到锁后它读到的状态是**三选一**，且三种都是确定的：
  1. refcount 仍含旧 owner（resume 前崩溃）：`last=False` 分支——**不可能**，因为旧 owner 走的是 release 分支。⇒ 见 2。
  2. `resume.required=True` 且 `entries==[]`：说明 refcount 已被清空但周期尚未确认结束 ⇒ **新参与者走"确认/接管"分支**（§3 RC-4），先按 `desired_state` 探测：`enabled` ⇒ 旧 resume 已生效，直接开**新代号**周期；`paused` ⇒ 旧 resume 未生效，**新参与者成为该周期的 owner**（`generation+1`? 否——**沿用旧 `generation`**，只把 `owner` 指向自己，因为这是同一个 pause 周期）并执行 resume，然后才可 pause。
  3. 空文件/无 owner/`schema=2, entries=[]` 且 `resume.required=False`：干净空闲 ⇒ 正常"全新周期"。
- **为什么"空 refcount 就 resume"是错的**：空 refcount 有 3 种来源（本周期刚结束、别人正在 resume、别人已接管）。只有 `generation + resume.required + lease_id` 三元组能区分。**现行 L582 的 `if not entries: unlink(owner)` 把 3 种来源合并成 1 种。**
- **反例（模拟）**：F-L1 用真实文件 fences 让 B 的 acquire 落在 A 的 resume 之前/之中；F-L4b 注入损坏 JSON；无锁对照版本在同样时序下产出双 resume（`evidence/raw/F-L1-nolock-guard.json`）。
- **兼容影响**：`resume.required` 只增不改；正常周期结束仍回到"两个文件都不存在"（`test_allow_download_pauses_and_resumes_running_worker` L2675-2676 与 `test_ensure_failure_still_resumes_worker` L2775-2776 的断言保持成立）。

### ADR-4 lease_id / 同 PID 嵌套 / PID 复用 / stale 判定来源

- **lease_id**：每次登记 `uuid4().hex[:24]`（≤64 字符、纯 ASCII、不含路径分隔符 ⇒ 可安全用于文件名/argv）。**删除只按 lease_id**。
- **同 PID 嵌套**：同一进程两次 `PausedWorkerScope` ⇒ 两条 lease，`invocations` 字段分别记 1/2（用于诊断），各自独立登记/释放；`_unregister` 只删自己那条 ⇒ 计数不会被"按 pid 全删"误伤。
- **incarnation 字段随每条 lease 持久化**：`pid`、`os_start_time`（可空字符串，除 Windows 外一律空 = 未验证）、`boot_uuid`（本进程世系，进程启动时的 `uuid4().hex[:12]`）。
- **stale 判定来源（按优先级，全部在锁内、有界）**
  1. **自己**：`pid == os.getpid() ∧ boot_uuid == 本进程 boot_uuid` ⇒ 活跃，**不探针**（避免自杀式误判与无谓 spawn；I-04-B 的"探针 ≤ min(20,相位)"因此不会被自己触发）。
  2. **探针返回活着 ∧ 记录 `os_start_time` 非空 ∧ 与 OS 现测创建时间不同** ⇒ **PID 复用**（原租约的持有者已死）⇒ 可回收，journal 记 `pruned:pid_reuse_detected`。
  3. **探针返回活着 ∧ 其余组合** ⇒ 活跃（**保守**）。
  4. **探针返回死亡** ⇒ 可回收，journal 记 `pruned:dead`。
  5. **探针异常/超时/未知** ⇒ **unknown** ⇒ **不回收、不当作死亡**；本次 acquire 直接 fail closed（`lease_conflict_unknown`），journal 记 `probe_failed`。
- **OS 探针降级**：Windows 首选 `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)` + `GetProcessTimes`（**无 spawn**，返回 `{alive, start_time}`）；该 API 不可用时降级到现行 `tasklist`（spawn，硬编码 20 s，按 I-04-A R-P 行取 `min(20, 相位预算)`），此时 `os_start_time` 一律为空 ⇒ 规则 2 失效，只剩规则 1/3/4/5 —— **契约不变，只是回收能力变弱**（fail closed 方向，安全）。
- **PID 复用检测未实测**（本机不能杀真实 worker/进程；见 §11 O-3）：本卡模拟中用注入的 `--fake-start-time`/`--probe` 覆盖该分支，资格仅到"规则可执行、失败方向安全"。
- **兼容影响**：新增字段只增不改；旧读者（只认 `pid`）仍能读到 `pid`（`_read_pause_entries` L450 的过滤器 `isinstance(e.get("pid"), int)` 依旧成立）。

### ADR-5 崩溃窗口与 fail-closed 规则

| 窗口 | 崩溃后果 | 冻结处置 |
|---|---|---|
| W1 写 refcount 后、写 owner 前（RC-3） | 有 lease、无 owner。旧代码会判成"用户暂停" ⇒ 永不 resume | **owner 不是权威**。`schema=2` 且 `entries` 非空 ⇒ 该周期归本工具；`owner` 缺失只记 `owner_marker_missing`，**不得**据此判用户意图。新参与者按 `generation` 继续（若 `entries` 里有活 lease 则 join；若全死则 prune 后成为 last 并走确认分支）。**用户意图的唯一证据 = `paused` ∧ 无 `schema=2` refcount（或 `entries==[] ∧ resume.required=False`）∧ 无 owner 标记**。 |
| W2 登记后未 pause | `entries` 有自己、worker 仍 running | 恢复：下一次 acquire 读到 `desired_state=running` ⇒ 走"全新周期"（`generation+1`）；旧 lease 若持有者已死则 prune。不产生任何 resume 动作（worker 本来就 running；**resume 在 running 上是幂等无害的，但本协议不允许在未记录 `resume.required` 的情况下发它**）。 |
| W3 pause 命令已发出（worker 已 stopped）但未确认 | `desired_state=paused`、`entries` 有自己、owner 存在 | 恢复：lease 持有者死了 ⇒ prune ⇒ 最后参与者走确认分支 ⇒ 见 `paused` ⇒ resume。**必须能把"我们暂停的"与"用户暂停的"分开**——依据是 `entries`（我们的租约）而不是 owner 文件。 |
| W4 最后 release 后、resume 前/中（`resume.required=True`） | worker 保持 paused，无人恢复 | 持久化的 `resume.required` 使恢复**可判定**：新参与者走接管分支立即补 resume；无人来的情况下由 `worker-status` 诊断 + §11 O-1 的运维通道。**不允许**"自动当作空列表 ⇒ 什么都不做"。 |
| W5 resume 命令超时/失败 | 不知是否生效 | `cleanup_status=failed:<reason>` + stderr 手工指引 + **保留 `resume.required` 和 owner 标记**（不 unlink、不写 `entries=[]`），即"失败保留可恢复诊断，不伪称已恢复"。下一次 acquire 的 `worker-status` 是唯一权威。 |
| W6 refcount JSON 损坏/截断/非 list/条目缺 `lease_id` | 旧代码 `_read_pause_entries` 返回 `[]` ⇒ 当成"无参与者" ⇒ 会 resume/覆盖 | **fail closed**：`lease_state_corrupt`。不改名、不删除、不重建（保留现场供人工判断）；不写 lease、不发 pause/resume。诊断含路径 + sha256 + 解析错误。 |
| W7 owner 文件被第三方/用户删除（scope 中） | 我们仍在 refcount 里 | 不自动 resume 用户意图：release 时若 `desired_state != paused` 或 `owner` 与我们的 `generation/lease_id` 不符 ⇒ **不发 resume**，`cleanup_status=failed:owner_evidence_changed`，保留诊断。 |
| W8 scope 中用户又执行了 pause（F-L4） | 用户意图与我们的恢复义务冲突 | **用户意图优先**：release 时若发现 `owner` 标记不再是我们的（或 `stop_requested_for`/`desired_state` 表明外部干预）⇒ 不 resume，`cleanup_status=failed:user_pause_intent`。**绝不"删除所有权证据后无条件 resume"**。 |

**fail-closed 总则**：有歧义的用户意图、未知的 worker 状态、未知的参与者存活、损坏的 JSON ⇒ 一律"不动作 + 明确错误码 + 可恢复诊断"。**未知不等于空。**

### ADR-6 与 I-04-A/I-04-B 单进程预算规则的组合（不得重开已签值）

| 动作 | 相位归属 | 预算 | 计数 |
|---|---|---|---|
| lease 锁等待 | 其所服务相位（acquire ⇒ 请求段；release ⇒ 清理段） | `lock_budget_for(相位预算) = min(相位预算, 60)`（**v1.3 更正**：此处旧文本写 `min(10.0, …)`，与 ADR-2 正文 v1.2 的 60 不一致；以 60 为准，见 §14 F-I04C-11/12）；请求段相位预算 = `deadline - now`（**无下限**，I-04-A D1/D3），清理段 = `C` | 不计 `calls`（非 CLI）；记 `lease_lock_waits` / `lease_lock_timeouts` |
| `_pid_is_alive` 探针 | 同 R-P 行 | `min(20.0, 相位预算, 5.0)`（`_PID_PROBE_MAX_SECONDS=20` 保留；本卡新增 5 s 收敛上限，只在探针上收紧，**不放松**任何已签上限） | `liveness_calls`；失败 `liveness_probe_failed`（I-04-A v2 R-P 行原义） |
| `worker-pause` | 请求段 | `_request_remaining()`（I-04-A D1 S2b） | `calls` |
| `worker-resume` | **清理段** | `C = max(30.0, 2×resume_wait + graceful)`，恒等，与 deadline 无关（I-04-A D2/C1） | `cleanup_calls` / `cleanup_elapsed_seconds` / `cleanup_status` |
| 相位墙钟 | — | **只报告，不设验收上限**（I-04-B carry 3）；验收按子调用（`worker-resume ≤ C+ε`，每个探针 `≤ min(20, 相位预算)`） | — |

- **本卡不发新预算、不改 C、不改 ε、不改 B**：lease 层只**消耗**相位预算，且所有新增等待/探针都是 `min(...)` 形式（只会更短）。
- **依赖声明**：I-04-B 的修复目前只在 `execution_runs/I-04-B/a20260919-01/iso/filing-fetch/`，**生产代码仍是 `_remaining()` 的 `max(10.0, …)`**。因此本协议中的"请求段相位预算"在移植前必须按 I-04-B 的版本落地；lease 层不得自己实现一份 `_remaining()`（I-04-B 条件 C1 的"调用点只读一次"纪律同样适用于 lease 层的 `lock_budget`/`probe_budget`：**在临界区入口读一次，向内传递**）。

### ADR-7 owner 文件与 entry 文件的兼容升级

- **不迁移生产 lease 文件**：`.source_catalog/filing_fetch_pause.*` 是**运行期瞬时文件**，`filing-fetch` 现有代码只在下载前后读写它；本次不搬运、不重命名、不清洗任何已存在的生产文件。若生产此刻存在遗留文件，新代码按 §ADR-5 W1-W6 的"未知/损坏/无 schema"规则 fail closed，直到人工确认（这就是"不自动当空列表"的落地）。
- **同一进程内升级**：owner 标记文件格式**不变**（内容仍是 `filing-fetch`，保持 `is_file()` 哨兵语义；**generation 不放 owner 文件**，避免任何按内容判断的旧读者误判）。
- **refcount 文件格式升级（v2 判别式）**：
  - `schema == "filing-fetch.pause-refcount/2"` ⇒ 新格式，按本协议处理。
  - JSON `list`（无 `schema`）⇒ **旧格式**。处置：**fail closed**（`lease_state_legacy`），除非显式打开迁移开关。**理由**：旧格式没有 `generation`/`resume.required`/`incarnation`，若新代码直接续用，则"无法区分用户暂停与我们的暂停"（ADR-5 W1）与"无法判定是否该 resume"（W4）两个洞会以新代码的名义重开。**旧格式下新代码不 pause、不 resume、不写**。
  - 空文件/`{}`：等同"无租约"，可安全开始新周期（但**不 unlink**，只覆盖写 `schema=2` 结构）。
- **迁移开关（可选、默认关）**：`FILING_FETCH_PAUSE_LEASE_MIGRATE=1` 时才允许把旧 list 逐条升级：`lease_id = legacy:<pid>:<index>`、`incarnation = {pid, os_start_time:"", boot_uuid:""}`、`generation = 0`、`resume.required = False`（**不认领 resume 义务**）。开启后仍必须满足：只 prune 探针判死的条目；`unknown` 仍 fail closed。运维要求：升级窗口内所有 writer 一起换（`filing-fetch` 是同一台机器上的短命 CLI 进程，通常无并发窗口）。
- **journal（可选）**：`.source_catalog/filing_fetch_pause.journal.jsonl`，默认写入（append，`O_APPEND` 单行 ≤4 KiB 原子）；它**不是权威**，缺权限时静默跳过（不 fail），仅供诊断与 reviewer 复算。守卫判据一律来自 refcount/owner/`worker-status`，**不得**依赖 journal。

### ADR-8 用户暂停语义（F-L3）与显式授权下载

- **保留**：`desired_state == paused ∧ 非本工具持有` ⇒ `action = respect_paused`；**不写 lease、不 pause、不 resume**；下载继续走显式 opt-in `--allow-acquisition-while-paused`（现行 L531-537 与卡片"显式调用可在用户 paused 时获授权下载但绝不代用户 resume"）。
- **新参与者判定"是否本工具持有"**：`schema=2 ∧ entries 非空` ⇒ 本工具持有；`schema=2 ∧ entries==[] ∧ resume.required=False ∧ owner 不存在` ⇒ 用户持有。**owner 文件单独不足以判定**（ADR-5 W1/W7）。
- **F-L3 的强断言**：全过程 `worker-resume` 调用数 = **0**；`worker-pause` = **0**；refcount/owner 文件**始终不存在**（不留下任何"我们持有过"的证据）；`ensure` 仍带 `--allow-acquisition-while-paused`。**不得**把这条合法路径记成"自动 pause 绕过"，也不得为了"恢复"用户的暂停而调用 resume。
- **wiki 侧依赖**：`worker-status` 的 `desired_state` 无法区分"谁暂停的"（`control.py` L768-777 只读控制文件）。本协议**不要求** wiki 变更（用 refcount 自证所有权），因此**不新增跨仓依赖**；若未来 wiki 提供 `pause_origin`，可作为额外交叉验证（非必需）。→ 卡片第 5 条"若现有 API 无法识别则记录依赖并先协调"据此**结论为：可识别，无需 wiki API 变更**。

---

## 3. 全状态与原子边界（卡片动作 2）

### 3.1 状态机（`PausedWorkerScope` 的 action 取值）

状态：`disabled` → `no_status` / `worker_stopped` / `respect_paused` / `joined` / `paused_by_us` / `pause_failed` / `lease_*` 失败族。

| # | 起点状态 | 条件（全部在锁内判定，除 status/pause） | 转换 | 副作用（顺序固定） |
|---|---|---|---|---|
| T0 | START | `enabled == False`（`--no-pause-worker`） | `disabled` | 无（不读锁、不探针、不 CLI） |
| T1 | START | `worker-status` 失败/超时 | `no_status` | 记 `pause_action=no_status`；**不登记**⇒无清理义务（I-04-A D3 原义） |
| T2 | START | `runtime_state != running` | `worker_stopped` | 无 |
| T3 | START | `desired_state == paused` ∧ 本工具未持有 | `respect_paused` | **零写**（F-L3） |
| T4 | START | `desired_state == paused` ∧ 本工具持有（`schema=2 ∧ entries 非空`） | `joined` | 锁内 append 自己一条 lease（`generation` 不变，`invocations+1`） |
| T5 | START | `desired_state == running` | `paused_by_us` | 锁内：prune → `generation+1` → append → 写 refcount → 确保 owner → unlock → `worker-pause` → 成功则**回锁内**记 `pause.confirmed=True` |
| T6 | START | `desired_state == paused` ∧ `schema=2 ∧ entries==[] ∧ resume.required=True`（W4 接管） | `paused_by_us` | 锁内：认领 `owner=me`（`generation` 沿用）→ append → unlock? **否**：留在锁内 `worker-resume` → 成功后 `generation+1` 的新周期：`worker-pause` → 记 `paused_by_us`。若 resume 失败 ⇒ `lease_resume_takeover_failed` |
| T7 | T5 的 pause 失败 | — | `pause_failed` | 锁内撤回自己的 lease（只删自己）→ 若因此为空则按 release 规则发 resume（best-effort，预算 C）→ 抛 `worker_pause_failed` |
| T8 | `paused_by_us`/`joined` → EXIT | 锁内 prune 后 `entries-{me}` 非空 | `released_joined` | 只写回剩余 entries；**不发 resume** |
| T9 | EXIT | 锁内 prune 后 `entries-{me}` 为空 ∧ `owner` 是我的 | **`released_last`** | 写 `resume.required=True` → **持锁** `worker-resume` → 成功：unlink refcount+owner（或写空结构）→ 失败：保留 `resume.required` + owner + `cleanup_status=failed:*` |
| T10 | EXIT | 空 ∧ `owner` **不是**我的（外部干预/用户暂停/W7） | `released_owner_changed` | 写回 `entries`（不含我）+ `resume.required=False`；**不发 resume**；`cleanup_status=failed:owner_evidence_changed` |
| T11 | 任意锁内 | `entries` 有 `unknown` 存活 | `lease_conflict_unknown` | 不写、不 CLI、unlock；请求失败 |
| T12 | 任意锁内 | refcount 损坏/旧格式且未开迁移 | `lease_state_corrupt` / `lease_state_legacy` | 不写（保留现场）、不 CLI、unlock；请求失败 |
| T13 | 任意锁内 | 锁等待超预算 | `lease_lock_timeout` | 不写、不 CLI；请求失败 |

### 3.2 四个线性化点（linearization points）

- **LP-1（建立周期）**：`T5` 中"`generation+1` 与我的 lease 被写入 refcount"这一次 `os.replace` —— 生效后，"本工具持有一次 pause"对所有并发者可见。
- **LP-2（建立 pause 事实）**：`worker-pause` **返回成功**（或 `worker-status` 随后读到 `desired_state=paused`）。注意 LP-2 **在 LP-1 之后**，所以中间存在"已登记但未 paused"（W2）——由 `pause.confirmed` 位与 `worker-status` 复查覆盖。
- **LP-3（结束周期）**：`T9/T10` 中"删除我的 lease 并把 `resume.required` 写入"的那一次 `os.replace`（在锁内）。此后**任何**新参与者看到的世界都是"周期已结束（或已有接管者）"。
- **LP-4（恢复所有权）**：`worker-resume` 返回成功 **且** 随后把 refcount/owner 清干净（同一次临界区）。**resume 的发出与"周期结束"的记账必须同处一个临界区（持锁）**，这是 ADR-3 的全部内容。

### 3.3 冲突矩阵（谁能与谁并发到什么程度）

| 并发对象 | 允许并发？ | 机制 |
|---|---|---|
| 两个 filing-fetch 的 lease 临界区 | **不允许** | OS 字节锁 |
| lease 临界区 vs worker CLI（pause/status/resolve/ensure） | **不允许**（除 resume：只允许在 release 临界区内） | ADR-2 |
| lease 临界区 vs company-wiki 的 `operation.lock` | 允许（不同锁，不同进程，互不嵌套） | 锁顺序无关 ⇒ 无环 |
| lease 临界区 vs 用户手工 `worker-pause/resume` | 允许（不互斥） | 用户意图优先规则（T3/T10、ADR-8） |
| 同一进程内两个 `PausedWorkerScope` | **不允许同时持有锁**（同一进程内的线程会自阻塞到超时） | **实现约束**：scope 内不得并发线程再进 scope；现行实现是单线程顺序调用，作为"同 PID 嵌套"仅指**顺序**嵌套（卡片 F-L2 的"同 PID 的 A/B 嵌套"按顺序嵌套理解并据此冻结）。跨线程并发属于新增前提，本卡不授予。 |

---

## 4. 固定调度表与每步 expected（卡片动作 6 的"调度脚本"）

完整冻结表见 `oracle.md`（F-L1/F-L2/F-L3/F-L4 + 注入窗口 W1/W3/W4/W5/W6 + 无锁对照 + 锁压力）。
**计数口径**：`pause_calls` / `resume_calls` / `refcount_set`（每步快照的 lease 集合）/ `owner`（`generation` + 是否本工具的）/ `action`。

---

## 5. 失败码与诊断（新增，不得与现行码冲突）

| 码 | 触发 | 请求结果 | 诊断 |
|---|---|---|---|
| `lease_lock_timeout` | 锁等待超相位预算 | 失败（请求段） | 锁路径、等待秒数、相位预算、建议清单 |
| `lease_state_corrupt` | refcount JSON 解析失败/非 list/条目缺 `lease_id` | 失败 | 路径 + sha256 + 解析错误 + "保留现场待人工判断" |
| `lease_state_legacy` | 旧 list 格式且未开迁移 | 失败 | 旧格式条目数 + 迁移开关名 + 迁移步骤 |
| `lease_conflict_unknown` | 存活未知的 lease 阻碍回收 | 失败 | 冲突 lease 的 `{lease_id,pid,age}` + 探针失败原因 |
| `lease_resume_takeover_failed` | T6 接管 resume 失败 | 失败（不 pause） | resume stderr + 手工 `worker-resume` 指引 |
| `cleanup_status=failed:user_pause_intent` | W8 | **请求结果不变**，仅清理字段 | 说明"用户暂停优先，已保留所有权证据" |
| `cleanup_status=failed:owner_evidence_changed` | W7/T10 | 同上 | 期望 owner vs 实际 owner |
| `cleanup_status=failed:resume_timeout` | W5 | 同上 | 保留 `resume.required=True` 供下次接管 |

**v1.3 补充（F-I04C-12，队列代价；三处文本之一，另两处是 ADR-2 与 §14）**：

- `lease_lock_timeout` 的触发条件是"排队等待 > 相位预算（上限常数 60）"，而排队等待 ≈ **(N−1)·H**
  （H = 单次临界区保持时间，含 `worker-status` 子进程与最长 graceful 5 s 的 `worker-pause`）。
  因此 **N·H 超过预算时队尾参与者必然 fail closed**——这是**设计上可接受的退化**（零写、可安全重试），
  但**不是**"偶发小概率"：确定性 case **F-T4**（H=0.4 s、预算 1.0 s、6 人 ⇒ 4 人超时）把它钉住了。
- **排队在消耗下载预算**：`lock_wait` 计入请求段；参与者应在诊断里报告 `lock_wait` 与剩余预算，
  让"下载超时"与"排队吃掉预算"可区分。缓解手段是重试/降低并发，**不是**放宽锁或跳过互斥
  （F-L1-nolock 已证：无互斥既丢更新又可能写出超过增量总数的值）。
- 清理段的锁等待同样受 `lock_budget_for(C)` 约束 ⇒ `cleanup_status=failed:lease_lock_timeout`
  （F-T3 实测），此时**保留义务与 owner 证据**、不伪称已恢复。

---

## 6. 摘要（给 reviewer 的 8 条冻结规则）

1. 互斥只有一处：`<root>/.source_catalog/filing_fetch_pause.lock` 的 1 字节 OS 锁，**永不 unlink**，超时 `lock_budget_for(相位预算) = min(相位预算, 60)`（**v1.3 更正**：旧文本此处写 `min(10, 相位预算)`，与 §12 ADR-2 不一致），超时即 fail closed，错误码 `lease_lock_timeout`（v1.3 对齐，见 §14 F-I04C-11）。
2. 删除 lease **只按 lease_id**，永不按 pid 全删；同 PID 的多个 lease 互相独立。
3. 每次"从无到有"的 pause 周期 `generation+1`；只有"最后一个 release ∧ `owner==me(lease_id,generation)`"才有权 resume。
4. `resume.required` 必须在"删除自己 lease"的**同一次 `os.replace`、同一个锁临界区**内持久化；**先写义务，再动作**。
5. `resume()` 与"周期结束的记账"在**同一个锁临界区**内完成（持锁发 CLI，预算 C）——这是 double-resume 的结构性防线。
6. "空 refcount ⇒ 该 resume" 被否决；空 refcount 必须结合 `generation`/`resume.required`/`owner` 三分。
7. 未知/损坏/旧格式/探针失败 ⇒ **fail closed**；`unknown ≠ dead`；`unknown ≠ empty`。
8. 用户暂停意图优先：`paused` 且非本工具持有 ⇒ 零写、零 resume；scope 内 owner 证据变化 ⇒ 不 resume、保留诊断。

---

## 7. 本卡不授予的范围（防止越权外推）

- 不授予**生产实现**资格：本卡是设计卡；I-04-D/移植卡才实施。
- 不授予**真实 provider/worker/多进程生产并发**资格（真实跨进程验证归 I-04-D 的隔离 harness）。
- 不授予**POSIX 分支**资格（未实测）。
- 不授予 **PID 复用 OS 探针**资格（未实测）。
- 不授予"跨机器/网络文件系统（SMB）上的锁"资格：Windows `msvcrt.locking` 在 SMB 上的语义**未验证**，本协议假设 `.source_catalog` 在**本机固定盘**上；网络盘需重新评估（记入 O-6）。

## 8. Open questions（交 reviewer / 后续卡）

- **O-1（真裁决，需 owner 决定；v1.2 更正措辞）**：最后参与者崩溃在 W4（`resume.required=True`）且**再无新参与者**时，worker **保持 paused** —— 本卡**不声称**这一步"已恢复"。恢复**只由下一个 acquire 发生**（它读到 `resume.required` 或可证的死 owner 后接管并 resume，见 §12 ADR-10b / V4-a），或被人的手工 `worker-resume` 结束。本卡**不**新增后台自愈进程/定时器（那会引入新的常驻组件）。若 owner 要求"无新请求也能自愈"，需要一条独立的运维通道（cron/人的巡检），请 reviewer / owner 明确。
- **O-2**：`worker-resume` 在 refcount 非空时被外部调用（例如用户手工 resume），以及用户在 scope 中再次 pause：本协议用 `desired_state` 只能看到"paused"，**无法识别是谁暂停的**。F-L4a 实测并记录了这一限制（我们的收尾会 resume，从而撤掉用户刚按下的暂停）。要真正保护用户意图，需要 wiki 侧提供 pause 来源（`pause_origin`）—— **登记为 I-04-D 的前置依赖**（见 §12 与 `handoff.json`）。
- **O-3（v1.2 新增）**：`LOCK_MAX_SECONDS = 60` 是本卡新引入的常数，不在 I-04-A v2 已签值内。请 owner 裁定：接受该上限，或改为"`lock_budget = 相位预算`（无上限常数）"，或指定别的值。**在裁定前，实施方一律按 60 执行**（Kernel 已冻结该值并记录在实际运行日志里）。

- **O-3 追加登记（C2 = owner 裁定项；2026-09-20）**：本轮把 O-3 显式登记为 **owner 门 = C2**，两项待裁：
  （a）等待上限常数 60（`lock_budget_for(x)=min(x,60)`）的**命名与边界验收**（原文见上一条，
  以及 §14「OPEN-3（复核建议）」段）；
  （b）**`worker-pause` 是否允许留在锁内**（本卡维持锁内；把 H 降到只含 `worker-status` 需要改变语义，
  见 §14 F-I04C-12 末段与 §4 的取舍）。
  条目落盘于 `handoff.json`：`review_carry_conditions.C2_OPEN3_owner_gate`、`owner_gates[0]`、`open_questions`；
  并与 §12 的「ADR-2 锁预算（v1.2 定稿）与 OPEN-3」段交叉引用。
  **这是 owner 的裁定项，不是实现项；它不阻塞 `accepted_scoped` 的签收**，也不改动任何 ADR 文本
  （裁定前实施方一律按 60 执行；本卡内核已冻结该值并记录在实际运行日志里）。
- **O-4**：PID 复用 OS 探针（`GetProcessTimes`）未实测；`os_start_time` 的时钟源与精度需要在 I-04-D 用**真实进程**验证（两个不同进程 + 一次 `TerminateProcess`）。
- **O-5**：同进程多线程并发 scope 未授予（§3.3 末行）；若未来出现线程池调用，本协议需要 reentrant 计数（进程内 `threading.Lock` + 进程间 OS 锁的两级锁），届时重签。
- **O-6**：`.tmp` 临时文件名当前为 `filing_fetch_pause.refcount.tmp`（两进程会互撞）。本设计要求改为含 `lease_id` 的唯一名（`os.replace` 覆盖目标仍然原子），**属 I-04-D 的最小修改项**。
- **O-7**：非本机盘（SMB/NFS）与 POSIX 平台的锁语义未验证。
- **O-8**：验收口径复核——本卡把"相位墙只报告不设上限"（I-04-B carry 3）继承到 lease 层：**锁等待/探针/CLI 各自的子调用有界，组合出的相位墙只报告**。`evidence/phase-wall.txt` 给出可读数字（F-L1 的 21.25 s 主要来自测试栅栏等待，而不是协议延迟）。请 reviewer 确认这与 I-04-A/B 无矛盾。
- **O-9（v1.2 新增）**：**判活模型**。本卡的判活优先取"申报模型"（DECLARED），真实 OS 探针只作为兜底；原因与替代方案见 `oracle.md` §8 与 §12.6。**I-04-D 的强制前置**：必须改用真实探针或 lifetime 单进程模式重跑全部并发 case，否则不得据此实施。

---

## 10. 模拟中量到的规则修订（v1 → v1.1；每条都由一次失败运行逼出来，不是事后合理化）

模拟（`sim/` + `evidence/`）跑起来后，v1 冻结的五处规则被自己的调度打穿。以下修订都已落进 `sim/kernel.py`，
并逐条给出**触发它的运行**。它们不是"为了让测试变绿"的放宽，而是规则本身的缺口：

| 编号 | v1 的问题 | 修订（v1.1） | 触发证据 |
|---|---|---|---|
| **ADR-9**（新） | v1 沿用现行代码的守卫顺序：先看 `runtime_state != running ⇒ worker_stopped`。我们的 pause 必然把 `runtime_state` 变成 `stopped`，于是"同一 pause 周期内第二个参与者"永远走不到 join/takeover 分支——**join 路径在生产里不可达**；而第一个参与者的并发窗口里，第二个参与者会另开一次 pause（一个周期两次 pause） | 守卫顺序改为：**`desired_state == paused`（或存在有效 lease）先判**；只有"未暂停且未运行"才是 `worker_stopped` | `evidence/run/F-L2d/`：8 个真实并发参与者，v1 规则下出现 `pause_calls=8` 与 8 次 `paused_by_us`（每条 lease 一停） |
| **ADR-9b**（新） | "有 lease 但 worker 是 running"（另一个参与者的 pause 还没落地）时，v1 走"全新周期"，于是同一周期里出现第二次 pause；另一种情形是 lease 的持有者死在 pause 之前（W2） | 有 lease 即进入 join/takeover 分支：pause 未落地 ⇒ 尽力清掉残留 pause 后**保留现有 lease** 开新周期（`fresh_cycle_recovering`），一个周期仍只 pause 一次 | `evidence/run/F-L2d/`（`pause_calls=2`，进入动作 `["paused_by_us","joined","joined","paused_by_us",...]`） |
| **ADR-10**（新，**v1.3 已被 §12 的 R1–R5 取代**：本行的 `released_took_ownership` 动作名与"认领周期并写义务"的做法都已在 r2 删除，见 §12 ADR-10 / ADR-10e） | "最后一个参与者 resume" 在 **owner 已先退出**时不成立：最后退出者不是 owner，v1 直接不 resume ⇒ worker 永久 paused，而 refcount 已空 | 三条互补规则：(a) 最后退出者**就是 owner** ⇒ 照常 resume；(b) 最后退出者不是 owner 但 `resume.required=True`（owner 已把义务交出来）⇒ **它也 resume 并收尾**；(c) 最后退出者不是 owner 且无义务（owner 死在回收路径上）⇒ 把周期**认领过来**（`released_took_ownership`：owner 改成自己 + 写义务），由下一次 release/acquire 收尾。**任何情况下都不留下"paused 且无人有义务"的状态** | `evidence/run/F-L1/` 与 `evidence/run/F-W4/`：A 先 release 时 v1 得到 `released_last`（错）或永久 pending |
| **ADR-11**（新） | 计划的"锁外读一次 status"在 `acquire` 里会用**陈旧快照**判定分支：另一个参与者在读与加锁之间完成了 pause，本参与者却按旧的 `enabled` 走了全新周期（重复 pause） | **status 与 lease 都在临界区内重读一次**，分支只用临界区内的快照；锁外那次读只用于"worker 是否根本没在跑"的快速前置判断，且其结论会被临界区内的复查覆盖 | `evidence/run/F-L2d/`：`lock_status` 显示 P3 在锁内看到 `enabled` 而 refcount 已有 7 条 lease |
| **ADR-2 锁预算**（修订） | v1 冻结"锁等待 ≤ 10 s"。实测每个临界区含 `worker-status` 子进程（0.1–1.5 s），8 个并发参与者时第 6–7 个的排队等待就超过 10 s ⇒ 整个请求 fail closed（`lock_timeout`） | 锁等待预算 = **相位预算本身**（`min(phase_budget, 60)`）：等待不可能"有用"地活过它所属的相位；请求段相位预算无下限（I-04-A D3），所以 deadline 已过时预算为 0、直接拒绝等待 | `evidence/run/F-L2d/journal.jsonl`：`"event": "lock_timeout", "budget": 10.0`（第 6 位排队者） |

**因此"冻结"的正确读法**：`oracle.md` 的 F-L1…F-W5 语义（谁该 resume、什么必须 fail closed）未被修订；
被修订的是**守卫顺序、分支命名与锁预算公式**这三处实现级规则。差异可见于 `action` 名字
（例如 `fresh_after_stale → fresh_cycle_recovering`）。

**另一处模拟实现教训（不是协议规则）**：`sim/kernel.py` 一度同时存在两个 `protocol_paused_branch` 定义
（旧签名覆盖新签名），使分支拿到的是**锁外**的旧 status 而不是临界区内的新 status。这与 ADR-11 的错误表现
完全相同，说明"同名函数覆盖"这种低级缺陷会被本测试网抓住，也提醒 reviewer 复核 kernel 时应先确认
每个协议函数只有一个定义（`grep -c '^def '`）。

## 11. 模拟资格与运行记录

- 运行入口：`sim/scheduler.py run <case...>`（隔离解释器 `iso/venv/Scripts/python.exe`）。每个 case 独立目录，
  内含参与者 stdout/stderr、journal、refcount/owner 快照、worker 动作日志。
- 汇总：`evidence/run-all.txt`（原始 stdout）、`evidence/failures.txt`（逐条失败）、
  `evidence/run-summary.json`（每 case 退出码与耗时）、`evidence/hashes.txt`（产物 sha256）。
- **通过**（见 `evidence/failures.txt` 的 `=== <case> PASS` 行）：F-L1、F-L2b、F-L2c、F-L3a/b/c、F-L4b、F-L4c、
  F-L4e、F-W5，以及锁压力 F-LK1/F-LK2/F-LK3 与三个 RED 反例。
- **未通过**（原始输出保留，未改断言、未放宽）：F-L2a（嵌套实测口径与 v1 oracle 不同）、F-L2d（8 并发下
  最后一条 lease 的收尾仍 pending）、F-L4a（gate 选择错误）、F-L4d（`attempted_resumes` 口径）、
  F-W1/F-W2/F-W4/F-W4b（崩溃后清死 participant liveness 记录的模拟步骤未全部对齐）。
  逐条"这是规则缺口还是调度缺口"写在 `review.md` 的 PENDING 区，交独立 reviewer 判定。
- **本卡不声称"生产协议已验证"**：以上全部是隔离目录内的真实子进程 + stub worker，没有真实 worker/provider/wiki。
- **v1.2 更正（r2 F-I04C-04）**：本节 v1 版本写的"10 PASS / 6 failing"是**错误计数**（当时解析器漏读了以非 `case` 键开头的记录，并静默跳过了 harness-error 记录）。真实计数见 §13.7；v1 的"未通过"清单里有 3 条（F-L1、F-L2c、F-L4a）实际是解析器造成的误报/漏报。原文保留在 `review.md` 的更正区，不删除。

---

## 12. r2 重签（v1.2）：独立复审 changes_required 的逐条处置

复审结论见 `review.md` ▶「reviewer 结论」区（**由 reviewer 填写**；本轮实施者据 F-I04C-01…10 修订）。
以下每条给出：**规则文本** + **实现锚点** + **证明它的运行**。凡与 §1…§11 冲突者，**以 §12 为准**。

### ADR-10（重写）"最后 release" 的完整分支表——含 v1 未定义的那一格

`run_protocol_exit`（`sim/kernel.py`）在**一个临界区内**先算 `entries' = entries \ {me}`，再按下表决定：

| # | 条件 | 动作 | 效果 |
|---|---|---|---|
| R1 | `entries' ≠ ∅` | `released_joined` | 只删自己那条 lease；若**我是 owner**，把 owner 记录**移交给存活 lease**（ADR-10e） |
| R2 | `∅ ∧ owner.lease_id == me` | `released_last`，`resume_reason=owner_is_me` | 先写 `resume.required` 义务，再 resume，成功则清零并 unlink 两个文件（下一周期 generation 从 1 开始，ADR-12） |
| R3 | `∅ ∧ resume.required == True` | `released_last`，`resume_reason=inherited_obligation` | 义务是工具自己写的、可归因，**接手并收尾**（F-I04C-01 的正面） |
| R4 | `∅ ∧ owner 可证死亡`（owner lease 在被修剪集合里 verdict∈{dead,pid_reuse}，或 owner 记录带 pid 而探针判死） | `released_last`，`resume_reason=owner_probe:*` / `owner_pruned:*` | 接手并收尾 —— **F-I04C-01 就是这一格缺失导致的永久 paused** |
| R5 | 其余（owner 为第三方且**不可证死亡**／owner 记录缺失／探针 unknown） | **`released_owner_changed`** | **不 resume、不认领、不改写 owner 证据**：只删自己那条 lease，`cleanup_status=failed:owner_evidence_changed:<why>`；owner 标记与 refcount 保留供人工判断（ADR-5 W7/T10、ADR-8）。V4-e 实测 owner 记录逐字节不变 |

**因此 v1 的自称"任何情况下都不留下 paused 且无人有义务"是错的**（**v1.3 追认**：该自称已在 §12 的 R5 中正式放弃——R5 允许"paused 且无可归因义务"作为 fail-closed 终态，由人工或 wiki 侧证据解除；"任何情况下都不留下"不再是本协议的性质）：v1 的 (c) 分支在没有义务时**改写 owner 并写义务**，会把**非本工具**的 pause 认领过来（F-I04C-02），或者留下 `owner=已死的 A` 的死角（F-I04C-01）。**R5 之后允许存在的终态是"paused 且无可归因义务"**——这是**故意的 fail closed**，由人工或 wiki 侧证据解决；它不再被任何自动路径改写。

### ADR-10e（新）owner 记录必须在存活参与者之间移交

`R1` 中若离开者正是 owner，它把 owner 改为**存活 lease 中 lease_id 最小者**（连同其 pid/boot_uuid/os_start_time）。
理由：owner 记录一旦指向"已不在 refcount 里的人"，最后的释放者就只能靠探针猜（或 fail closed），
F-L2a 的同进程嵌套正是这样暴露出"owner 已释放但进程还活着"的死角。证据：`evidence/run/F-L2a-nesting/`
（`exit_first_transfer=nest-scope-2`，随后 scope-2 的 release 得 `released_last`）。

### ADR-11（收紧，v1 未落实）整条 acquire 路径是**一个**临界区

`run_protocol`：`lease_lock → {读 worker-status, 读 refcount, 判定, 修剪, 登记, 写 owner, pause, 确认} → unlock`。
**没有锁外读**：v1.1 的形状是"锁内读一次 → 释放 → 再进锁做决定"，决定用的仍是上一次的 `state`（复审 F-I04C-07 指出的 :586/:644）。
`protocol_paused_branch` / `_takeover_cycle` / `_fresh_cycle_locked` / `_withdraw_after_failed_pause`
**一律不加锁**（前置条件：调用者持锁），由 `sim/static_check.py` 静态证明（S1/S2/S3/S4，`evidence/static-adr11.txt`）。
行为证明：`F-L2e-stale`（故意保留 v1 形状：锁外读 → 同调度下 `pause_calls=2`）对 `F-L2e-fixed`（冻结形状 → `pause_calls=1`、`joined`）。

### ADR-12（新）generation 是**每文件**计数器，不跨周期单调

refcount 收尾时被 unlink，下一周期从 **1** 重新开始。v1 文本写"`gen` 单调不减"，与实现不符（F-I04C-03）。
选择"记录归零"而不是"全局持久化"的理由：generation 的用途已收敛为**同一文件内的周期代号 + 诊断**，
权威判据是 `owner` 记录 + `resume.required` + 判活三件事（R2–R5）；引入第三个持久文件会带来新的迁移面（ADR-7）。
证据：`evidence/run/F-GEN/`（两周期各自 gen=1）与 `evidence/run/F-W4b/`。

### owner 记录 schema（v1.2 扩展）

`owner = {lease_id, generation, pid, boot_uuid, os_start_time}`。新增 pid/世系是为让**后来者能证明 owner 已死**
（R4）而不是猜；旧记录缺这些字段时 R4 不成立，直接落到 R5（fail closed，方向安全）。

### ADR-5 W1/W2/W3 的表述更正（r2 F-I04C-08）

v1 把 F-W1/F-W2/F-W4b 的失败归为"调度对齐问题"，**不成立**：
- **F-W1**：v1 用了一个**已被删除的注入点**（`after-pause-before-confirm`），于是"崩溃"根本没发生（exit 0），
  测到的是正常路径——**证据缺陷**。现在改用真实注入点 `after-refcount-before-owner`（`_fresh_cycle_locked` 内），
  并证明"无 owner 标记 ≠ 用户暂停"。触发差异见 `review.md` 更正区。
- **F-W2**：v1 断言"只允许一次 pause"，与 ADR-10d 冲突——B 关掉 A 的孤儿周期后**必须**再 pause 才有自己的下载窗口，
  正确期望是 `pause_calls=2`（一次是 A 的、一次是 B 的）。**规则正确、断言写错**。
- **F-W4b**：v1 断言新周期 `generation=2`。收尾会 unlink refcount ⇒ 新文件从 1 开始（ADR-12）。**断言与规则不符**。

### 判活模型与 I-04-D 前置（r2 P3-2）

本轮的判活优先级：① 本进程世系；② payload 注入答案（合成 pid）；③ **DECLARED 申报模型**（`alive.<pid>.<holder>.<tag>.json`，
参与者启动写、正常返回删、崩溃留下，且 OS 必须也认为该 pid 存在）；④ 真实 OS 探针（`tasklist`/`os.kill`）；⑤ unknown ⇒ fail closed。
申报模型是**模拟输入**，不是生产语义。**不授予**"该模型的等价性"；**I-04-D 的强制前置**：
必须用真实探针或在 `lifetime` 单进程模式下重跑全部并发 case（见 `oracle.md` §8 与 §13.6）。

### ADR-2 锁预算（v1.2 定稿）与 OPEN-3

`lock_budget_for(x) = min(x, 60)`，`x` = 所服务相位的预算（请求段 `deadline-now`，清理段 `C`）；
**只消耗、不产生**预算；`x<=0` ⇒ 拒绝加锁（fail closed）。与 I-04-A v2 的关系：请求段无下限、清理段独立 C、
探针 ≤ min(20,相位预算) —— 三条均未被本卡改动。**新常数 60 登记为 OPEN-3 待 owner 裁**（§8）。

**OPEN-3 交叉引用（C2 登记；2026-09-20 追加）**：上文的 `lock_budget_for(x)=min(x,60)` 与上限常数 60 登记为 **OPEN-3 = owner 门（C2）**。
条目在 `handoff.json.review_carry_conditions.C2_OPEN3_owner_gate` 与 `handoff.json.owner_gates`；
正文见 §8 O-3（含紧随其后的"追加登记"条）与 §14「OPEN-3（复核建议）」段。两项待裁：
（a）60 的命名与边界验收；（b）`worker-pause` 是否留在锁内（本卡维持锁内）。
**不阻塞 `accepted_scoped` 的签收**（属 owner 裁定项，不是实现项）；裁定前实现一律按 60，
任何 ADR 文本与断言强度均不因本条改变。

## 13. v1.2 的实测结果（可复算）

1. **协议套件**：`sim/scheduler.py run <24 个 case> --log evidence/run-all.txt`，scheduler 退出码 **0**，
   `evidence/failures.txt` 首行 `cases_in_log=24 pass=24 fail=0 harness_error=0 failing_checks=0`。
2. **锁与 legacy 反例**：`evidence/lock-and-legacy-failures.txt` 首行 `cases_in_log=7 pass=7 fail=0 failing_checks=0`。
3. **ADR-11 静态证明**：`evidence/static-adr11.txt`（S1–S4 全 PASS，含"默认路径绝不调用 stale 变体"）。
4. **相位墙（只报告）**：`evidence/phase-wall.txt`，每 case 给出 `phase_wall_seconds` 与 `max_lock_wait_seconds`。
5. **F-LK2 不可复现性（r2 P3-4）**：同一条无锁对照连续 5 次（最终证据轮）= finals `[12, 19, 7, 26, 43]`
   ⇒ lost_updates `[197, 185, 191, 198, 14]`；复审另一次独立复跑得 34/200（lost 166）；更早一轮还出现过 **261/200**（无锁写本身不是原子的，撕裂/合并写会给出高于增量总数的值）。
   **结论只能是定性的"无锁既丢更新、写也不原子"，任何单一数字都不代表该对照的稳定行为**（F-LK2 的断言因此只要求 `final != expected`）（已写进 `stress.py` 的输出字段 `determinism`）。

> **更正（C1 关闭；2026-09-20 追加，原文一字未删）**：上面第 5 条引用的 finals `[12, 19, 7, 26, 43]` ⇒ lost_updates
> `[197, 185, 191, 198, 14]` 是**过时值**，不是最终证据轮的实测值；该组自身也不相容
> （`expected - finals = [188, 181, 193, 174, 157]`，与它同处给出的 `[197, 185, 191, 198, 14]` 不等）。
> **最终证据轮的实测真值**（权威记录：`evidence/lock-and-legacy.txt` **第 6 行**的 F-LK2 记录；并与原始运行目录
> `evidence/run/F-LK2-r{1..5}/counter.txt` 逐轮一致）：finals `[16, 35, 10, 56, 18]` ⇒ lost_updates
> `[184, 165, 190, 144, 182]`，`lost_updates_range = [144, 190]`，`expected = 200`（8 进程 × 25 轮），
> 五轮的 `lock_acquisitions` 全为 0 且 `use_lock=false`。
> **复算命令与原始输出**：`& $PY -B sim/verify_flk2.py` ⇒ `evidence/flk2-recompute.txt`（13/13 检查通过：
> A1–A8 逐轮从原始运行目录复算并与记录字段比对，B1–B4 复核记录内部算术，C1 证明上面那组过时数字
> 不可能来自 `expected=200` 的任何一轮）。
> 第 5 条的**结论不变**（"只能定性"、只断言 `final != expected`）；本条只更正数字，
> 不放宽任何断言、不改冻结 oracle 的期望值。上表 §14 F-I04C-13 行与本条引文中的 `[12,19,7,26,43]`、
> 以及"更早一轮 261/200 的撕裂写"均作为**历史**保留（261/200 不在最终证据轮内），不删除、不改写。
6. **DECLARED 判活的适用范围**：仅本卡的隔离模拟；I-04-D 强制重跑（§12 末）。
7. **计数更正**：v1 的"10 PASS / 6 failing"作废；v1.2 的真实计数是 **24 PASS / 0 FAIL / 0 harness-error / 0 failing checks**
   （协议套件）与 **7 PASS / 0 FAIL**（锁与反例套件）。解析器缺陷（漏读非 `case` 开头记录、跳过 harness-error）
   已在 `sim/parse_run.py` 修好，并在 `review.md` 保留 v1 原文 + 更正说明。

---

## 14. r3 重签（v1.3）：第一轮复核 3 项 still-required 的逐条处置

复核结论为 **accepted_scoped**，附 3 项 still-required（其中第 1 项是 I-04-D 的前置）。以下每条给出
规则文本、实现锚点与证明它的运行；**与 §1…§13 冲突者以 §14 为准**。

### F-I04C-11（必修 1）错误码与实现对齐，并补真超时 case

**问题**：`FileLock.acquire` 抛通用 `lock_timeout`，而 `run_protocol` 的映射表只认 `lease_lock_timeout`
⇒ 真实出口曾是 `code="lock_timeout" + action="lease_fail_closed"`，与 `decision.md`（ADR-2 超时后果、T13、§5 码表）
和 `oracle.md`（§2 F-L2d、§7）冻的 `lease_lock_timeout` 不一致。

**选择**：**改实现，对齐三处文本**（不动冻结文本）。理由：其余 lease 错误码都带前缀
（`lease_state_corrupt`/`lease_state_legacy`/`lease_conflict_unknown`），且有前缀才能在请求里区分
"锁等不到"与"其它锁"；journal 锁保持通用码。

**实现**：`FileLock.__init__(..., code="lock_timeout")`；`lease_lock()` 传 `code="lease_lock_timeout"`
（`sim/kernel.py`）。journal 锁与 `stress.py` 的独立锁保持通用码。请求段的映射表
（`run_protocol` 的 `except ScopeError`）因而命中 `lease_lock_timeout`；清理段照例落成
`cleanup_status=failed:lease_lock_timeout`。

**新增 case（真实占锁，非注入）**：`sim/cases_timeout.py` + `sim/hold_lock.py`（外部进程真持锁）：

| case | 场景 | 冻结期望 | 实测 |
|---|---|---|---|
| **F-T1** | 外部进程真持锁；参与者 `request_budget=0.05` | `code=lease_lock_timeout`、`action=lease_lock_timeout`、零写、零 CLI、状态文件字节不变、等待受预算钳制、journal 记 `lock_timeout{code:lease_lock_timeout}` | 7/7 PASS（`evidence/run/F-T1/`） |
| **F-T2** | 同场景但 `request_budget=0`（I-04-A D3：无预算） | 同上，且**根本不尝试加锁**（journal 无 `lock_acq`） | 3/3 PASS |
| **F-T3** | 请求已成功（`paused_by_us`）；外部先占锁再放行其清理段，`cleanup_budget=0.3` | 请求结果不被改写；`action=release_fail_closed`、`cleanup_status=failed:lease_lock_timeout`；义务与 owner 证据保留；worker 仍 paused | 6/6 PASS |
| **F-T4** | 6 个 enter-only 参与者，注入临界区保持 H=0.4 s，锁预算 1.0 s（队列 ≈ (N−1)·H = 2.0 s） | ≥1 个参与者以 `lease_lock_timeout` fail closed 且零写；成功者恰好是"开周期 + join"；超时者**绝不**出现在 refcount；全部成功者释放后无悬挂 lease/义务 | 8/8 PASS |

**T13/§5 码表**：不变（一直是 `lease_lock_timeout`），现在实现与之一致。

### F-I04C-12（必修 2）排队跨预算的边界代价，写进 ADR-2

**实测模型**（F-L2d 与 F-T4）：每个临界区包含 `worker-status`、`worker-pause`（最长 graceful 5 s）
与本地原子写；记单次保持时间为 **H**，N 个参与者的排队等待 ≈ **(N−1)·H**，因此

- **N·H > 锁预算上限（`LOCK_MAX_SECONDS = 60`；或更小的相位预算）⇒ 队尾参与者一律 fail closed**
  （`lease_lock_timeout`，零写，状态不变，可安全重试）。F-T4 是这条边界的确定性 case。
- **排队在消耗下载预算**：等待发生在请求段，`lock_wait` 直接吃掉 `deadline`。F-T4 报告每个成功者的
  `lock_wait`（本次：P0 = 0.000 s、P2 = 0.571 s；`budget_consumed_by_queueing` 字段）；
  F-L2d 的 8 并发实测最大等待 9.87 s、整相位墙 13.2 s（`evidence/phase-wall.txt`）。**这是本协议的真实代价**：
  高并发时下载预算会被排队吃掉，缓解手段是重试/降并发，而不是放宽锁或跳过互斥。

**写入位置**：ADR-2（正文"超时后果"与"关键取舍"）+ §5 码表 + 本节。**并登记为 owner 待裁项**：
是否允许 `worker-pause` 留在锁内（把 H 降到只含 `worker-status` 需要改变语义——pause 必须在互斥下完成，
否则两个参与者可能同时认为自己是首参与者；本卡维持锁内）。

### OPEN-3（复核建议）保留 60，但重新命名

`LOCK_MAX_SECONDS = 60` **不是新预算**，而是**本卡新增的"等待上限常数"**：请求段的相位预算本身
（`deadline - now`，默认 900 s）远大于 60，所以它对请求段不构成额外约束；它的真实作用是为
**清理段**（`C` 可达 85 s）和**短 deadline** 封顶，属**防病态等待**而非新预算。
与 I-04-A v2 三条已签值（探针 `min(20, 相位, 5)`、请求段无下限、清理段独立 `C`）**无冲突**：
锁只"消耗"相位预算，`≤0` 时拒绝等待（F-T2 已证）。**登记**：§8 O-3 改为"确认命名与边界验收"，
并列出"是否允许 `worker-pause` 在锁内"一并待裁。

### F-I04C-13（必修 3）正文旧值清理

| 位置 | 旧文本（已改） | 现文本 |
|---|---|---|
| `decision.md` §ADR-6 预算表 | `min(10.0, 相位预算)` | `lock_budget_for(相位预算)=min(相位预算,60)` + v1.3 更正注记 |
| `decision.md` §6 摘要第 1 条 | `min(10, 相位预算)` | 同上 + 错误码 `lease_lock_timeout` |
| `decision.md` §10 ADR-10 行 | `released_took_ownership` / "认领周期" | 标注**已被 §12 R1–R5 取代**（该动作名在 r2 已删除） |
| `decision.md` §10 末段 | "任何情况下都不留下 paused 且无人有义务" | 追认**已放弃**：R5 允许"paused 且无可归因义务"作为 fail-closed 终态 |
| `oracle.md` §0 | `gen` 单调不减 | 每文件计数器、收尾后从 1 重来 + owner 记录字段扩展说明 |
| `oracle.md` §7 | `min(10, 相位预算)` | `lock_budget_for = min(相位预算, 60)`（60 = OPEN-3） |
| F-LK2 数字（三处三组） | `[3,15,9,2,186]` / `[12,19,7,26,43] ⇒ lost [197,…]`（自不相容） | **统一为实测那一组**：finals `[16,35,10,56,18]` ⇒ lost `[184,165,190,144,182]`（来源 `evidence/lock-and-legacy.txt` 的 F-LK2 记录；与 finals 相容） |

> **C1 关闭（2026-09-20 追加）**：上表最后一行的"已改"在 r3 只落到 `oracle.md` §7（`sim/patch_r3_docs.py` 的 O3 替换）；
> `decision.md` §13.5 与 `review.md` §1 的 P3-4 行当时**未**被该脚本触及，仍印着过时组 `[12,19,7,26,43]`
> （该值在此只作历史引用保留，不删除）。本轮已在 §13.5（本节上方追加的更正块）与 `review.md` §1
> （该表下方追加的更正块）补齐；两处更正的依据都是自己复算的 `sim/verify_flk2.py` ⇒
> `evidence/flk2-recompute.txt`（13/13 PASS）与 `evidence/lock-and-legacy.txt` 第 6 行的 F-LK2 记录，
> 真值 finals `[16,35,10,56,18]` ⇒ lost `[184,165,190,144,182]`。
> **设计结论、断言强度与冻结 oracle 的期望值均未改动**（本轮只做数值与登记层面的追加式更正）。

### v1.3 的真实计数

`evidence/failures.txt` 首行：`cases_in_log=28 pass=28 fail=0 harness_error=0 failing_checks=0`（27 协议 case + F-GEN 等，含新增 F-T1…F-T4）。
`evidence/lock-and-legacy-failures.txt` 首行：`cases_in_log=7 pass=7 fail=0 failing_checks=0`。
`evidence/static-adr11.txt`：S1–S4 全 PASS。



