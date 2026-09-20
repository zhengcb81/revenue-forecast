# I-04-D decision.md — 实施记录与冲突/未决登记

范围：`<A>` = `execution_runs\I-04-D\a20260919-01`。上游设计 = `execution_runs\I-04-C\a20260919-01\decision.md` v1.3（`accepted_scoped`，ADR-1…ADR-12 + §12 的 R1–R5 分支表 + `lock_budget_for(x)=min(x,60)`）。本卡冻结期望 = `<A>\oracle.md`。本文件的事实来源 = `<A>\scratch\FACTS.md`（引用处写作 FACTS §n）。

---

## 0. 本卡性质与边界

- **本卡是实施卡（IMPLEMENTATION card），不是设计卡。** 上游设计 I-04-C v1.3（状态 `accepted_scoped`）在本卡**不被重开**：ADR-1…ADR-12、R1–R5、`lock_budget_for(x)=min(x,60)` 一律按原文执行；本卡只把它们落成代码，并把实施中暴露的缺口登记在此（§2、§6）。
- **改动范围仅限隔离副本 `iso/`。** 唯一的实现产物是 `<A>\iso\filing-fetch\scripts\fetch_filing.py`，由 `<A>\scratch\patch_i04d.py --apply` 确定性生成（幂等；基线 hash 不匹配则拒绝打补丁）；新增辅助文件 `scripts\i04d_fake_worker.py`、`scripts\i04d_participant.py`、`scripts\i04d_schedule.py`、`tests\test_fetch_filing_lease.py`（FACTS §1）。
- 基线（输入）= I-04-B `accepted` 产物，sha256 `dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c`；输出 sha256 `a72546c50401a4b1876288bea6b6d7e4a72db9c39fd028c7bfb75a6f929ad198`（126274 字节）（FACTS §1）。
- **生产仓库字节未动**：`filing-fetch\scripts\fetch_filing.py` 仍为 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`；company-wiki `catalog.sqlite3` 仍为 49,677,344,768 字节 @ `2026-09-19T06:31:35Z`、`-wal` 0 字节（FACTS §8）。
- **状态 `review_pending`；实施者不签署任何资格**（FACTS 头部）。本文件不主张验收。
- 证据状态（如实）：末次 pytest 运行为 `18 passed, 3 failed`（RED 时为 `17 failed, 2 passed, 2 skipped`）；**3 个失败登记为 harness 时序债务（§6e），本文件不声称该项全绿**。19 个 scheduler case 全部 GREEN，其原始 `summary.json` 位于 `<A>\evidence\run\<case>\`，是**主要证据**（FACTS §2、§4、§5）。
- **未运行变异证明**；oracle §7 的 M1–M11 全部未执行（FACTS §8，`review.md` 的命令清单与未决原因）。

---

## 1. 实现映射（设计 -> 代码）

全部锚点都在 `<A>\iso\filing-fetch\scripts\fetch_filing.py`（FACTS §1 的实现映射，行号为输出文件行号）。

| ADR | 冻结要点 | iso 中的实现锚点 |
|---|---|---|
| **ADR-1** OS 字节锁 | 1 字节 @ offset 0，加在永不 unlink 的专用锁文件上，崩溃由内核释放 | `_try_lock_byte` / `_unlock_byte`（`msvcrt.locking` `LK_NBLCK` / `LK_UNLCK`；POSIX `fcntl.flock` 分支已写但**从未执行**）、`_LeaseLocked`（进程内按深度可重入 = 唯一临界区入口）、`_lease_lock_path`；`_LeaseLocked` 的 docstring 明示"由 `__exit__` 复用 `__enter__` 已持有的锁"（见 §2d） |
| **ADR-2** 锁预算 | `lock_budget_for(x)=min(x,60)`，0.05 s 固定轮询（不退避），`x<=0` 不得尝试加锁 | `LOCK_MAX_SECONDS = 60.0`、`_lock_budget`、`_acquire_lock`（`budget <= 0` 直接抛 `lease_lock_timeout`，不创建锁文件、不产生 `lock_acq`） |
| **ADR-3** "最后 release" 判定 | 删除自己 lease → 判 last → 先持久化义务 → 再动作，全在同一临界区 | `__exit__` → `_release_locked` → `_release_common_locked`（实现为**单段**临界区，见 §2d） |
| **ADR-4** lease 身份与 stale 判定 | `lease_id` = uuid4 hex 24；只按 `lease_id` 删；五条探针规则；OS 探针失败即 unknown | `_new_lease_id`、`_boot_uuid`、`_probe_entry_verdict`（verdict `self` / `alive` / `dead` / `reused` / `unknown`）、`_pid_is_alive_with_start_time`、`_process_exists` / `_process_start_time_raw` / `_windows_process_start_time`、`_pid_is_alive`（`tasklist` 降级）、`_probe_injection`（仅测试用 `I04D_PROBE_INJECT`） |
| **ADR-5** W1–W8 崩溃窗口 | 每个窗口的 fail-closed 处置 | W1 → `_dispatch_locked`：`state.owner is None` ⇒ `_join_cycle_locked`（**owner 文件不是权威**）；W2 → `_withdraw_orphan_pause_locked` + `_fresh_cycle_locked(resume_required=False)`；W3/W4 → `_takeover_cycle_locked`（入口判据 `state.resume_required`，在 `_dispatch_locked` 的 `not live` 分支）；W5 → `_release_common_locked` 的 resume 失败路径：保留 `owner` / `resume.required`，`cleanup_status=failed:resume_timeout` 或 `failed:<code>`；W6 → `_read_pause_state`（`lease_state_corrupt`，不改名/不删除/不重建）；W7 → `_probe_owner_death` 把 `owner_record_missing` 定为**非**死亡证据 + R5 分支；W8 → `_release_common_locked` 的 `is_owner` / `resume_required` 双判据（owner 证据变化 ⇒ 不 resume） |
| **ADR-6** 预算归属 | 锁只消耗相位预算、不产生；探针 `min(20, 相位, 5)`；pause 记请求段；resume 记清理段 | `_request_remaining` / `_cleanup_timeout` / `_cleanup_remaining` / `_lock_budget`；`_worker_pause(min(remaining, _WORKER_STATUS_TIMEOUT))`；`_worker_resume(self._cleanup_remaining())` |
| **ADR-7** schema=2 / owner 标记 / 迁移 / journal | 不迁移生产文件；旧 list 默认 fail closed；journal 非权威、失败不致命 | `_read_pause_state`（fail-closed 读取器）、`_write_pause_state`、`_write_owner_marker` / `_write_owner_marker_locked`、`_migrate_legacy_payload`（仅 `_MIGRATE_ENV=1` 时）、`_lease_journal`（append-only，从不作权威判据）、`_clear_pause_lease`、`_PAUSE_LEASE_SCHEMA` / `_PAUSE_LOCK_NAME` / `_PAUSE_JOURNAL_NAME` |
| **ADR-8** 用户暂停优先 | `paused` 且非本工具持有 ⇒ 零写、零 pause、零 resume | `_respect_user_pause_locked`（判据 `not state.entries and not state.owner`）+ `_dispatch_locked` 中 paused 分支的**第一格**（见 §2c） |
| **ADR-9 / 9b / 9c** 守卫顺序与加入 | paused-or-leased 先于 `runtime_state`；有 lease 即 join/takeover；孤儿 pause 撤回 | `_enter_locked`（`if desired == "paused" or state.entries:` 先判，`elif runtime != "running"` 后判）、`_dispatch_locked`（`_is_our_owner` ⇒ join；`_withdraw_orphan_pause_locked` ⇒ 撤回后开新周期；`_owner_lease_live` ⇒ journal `joined_live_holder` + join）、`_join_cycle_locked` |
| **ADR-10 R1–R5** | 释放分支表 | `_release_common_locked`：R1 `if remaining:`；R2 `is_owner` ⇒ `resume_reason=owner_is_me`；R3 `state.resume_required` ⇒ `inherited_obligation`；R4 `_probe_owner_death` 为真且 `_owner_is_our_lineage`（见 §2a）；R5 其余 ⇒ `released_owner_changed` + `cleanup_status=failed:owner_evidence_changed[:<why>[:foreign_lineage]]` |
| **ADR-10e** owner 移交 | 离开者即 owner 时移交给存活 lease（连同 `pid` / `boot_uuid` / `os_start_time`） | `_release_common_locked` R1 内的移交块：`heir = min(remaining, key=lease_id)`，写 `state.owner`（含 `pid`/`boot_uuid`/`os_start_time`），journal `ownership_transferred`（`dead_able=bool(os_start_time)`），并落到 `lease_owner_transferred_to` |
| **ADR-11** 整条 acquire 一个临界区 | 无锁外读；status/lease 都在锁内重读 | `__enter__`（`with self._lock as locked: locked._scope._enter_locked()`）→ `_enter_locked`（锁内：`_worker_status` → `_read_pause_state` → `_classify_locked` → `_dispatch_locked`；`_confirm_pause_locked` 亦在锁内） |
| **ADR-12** generation 每文件计数器 | 新周期 `generation+1`；接管沿用；文件收尾删除后下一周期从 1 重来 | `_fresh_cycle_locked`（`state.generation + 1`）、`_takeover_cycle_locked`（**不**自增，沿用被接管的 generation）、`_release_common_locked` 成功收尾（`entries=[]` / `owner=None` / `resume_required=False` + `_clear_pause_lease`） |
| O-5（ADR-7 附属） | 唯一 `.tmp` 名，避免两进程互撞 | `_unique_tmp_path`（`name.<pid>.<boot_uuid>.<uuid8>.tmp`）+ `_atomic_write_json` |

---

## 2. 实施中发现的设计缺口与本卡的处置（关键章节）

### 2.0 由失败用例逼出来的 9 个实现缺陷（FACTS §3，逐条均已修复）

| # | 症状 | 被哪个用例抓到 | 性质 | 与本节的关系 |
|---|---|---|---|---|
| 1 | `_lease_entry(state, state, ...)` 把 `_LeaseState` 当 scope 传入 ⇒ `AttributeError: '_LeaseState' object has no attribute 'lease_id'` | W4 takeover | 纯实现 bug | — |
| 2 | `_is_our_owner` 以 `owner.lease_id == 我的 lease_id` 判同源 ⇒ 同 PID 嵌套被误判为外来持有者 | F-L7 | 实现 bug（改用世系身份：`boot_uuid` + `pid` + owner lease 仍存活） | 与 §2a 同一族判据 |
| 3 | `_probe_owner_death` 把 `owner_record_missing` 当作"不安全原因"返回，释放路径据此视为"可继续" | 释放路径 | 实现 bug（改为 R5 fail closed，`owner_record_missing` **不是**死亡证据） | §2a |
| 4 | R4 缺 lineage 限定 ⇒ 外来记录只要指向已死 pid 就授权 resume | F-L8d | **设计缺口** | **§2a** |
| 5 | 存活的外来 holder 被判为冲突而不是加入 ⇒ 同一工具的两个真实参与者互相 fail closed | F-L5 | **设计缺口（解释分歧）** | **§2b** |
| 6 | "paused + 空账本"缺 ADR-8 守卫 ⇒ 把用户的暂停认成自己的周期，对已停的 worker 再 pause 再 resume | F-L9a | **设计缺口** | **§2c** |
| 7 | 钩子栅栏过滤器把每个 gate 施加给每个参与者 ⇒ B 被只有 A 能到达的 gate 死锁 | 用例编排 | harness 缺陷（改为按 tag 门控 `I04D_HOOK_TAG`） | §6e |
| 8 | 探针的"无法回答"与"已死"被合并（`_windows_process_start_time` 对缺失 pid 与 API 失败都返回 `None`） | 探针用例 | **设计缺口** | **§2e** |
| 9 | 探针用缓存句柄路径，对**已退出**的 pid 报 alive | 探针用例 | 实现 bug（每次判定都重新查询） | **§2e** |

### 2.a R4 的"可证死亡"缺少 lineage 限定 —— 实现级澄清（收紧 fail-closed 方向）

- **冻结文本**：I-04-C §12 ADR-10 的 R4 只要求 `∅ ∧ owner 可证死亡`（owner lease 在被修剪集合里 verdict ∈ {dead, pid_reuse}，或 owner 记录带 pid 而探针判死）⇒ `released_last` 并 resume。
- **代码必须做什么**：resume 会解除一次 pause。若"可证死亡"单独成立即可授权，则**任何**第三方记录（例如用户手工 `worker-pause` 后残留、或另一个工具写的记录）只要恰好指向一个已退出的 pid，就能让本工具 resume 一个**本工具从未创建**的暂停——最坏情况是用户的暂停。
- **本卡选择**：R4 增加两道门槛，二者取"或"：
  (i) owner 记录属于**本进程世系**（`_owner_is_our_lineage`：同 `boot_uuid` + 同 `pid`）；或
  (ii) 该 owner 的 lease 仍在本次 prune 的**原始账本**中（即它是本工具账本里的成员，被本次 prune 回收；`_probe_owner_death` 以 `owner_lease_still_live` 返回"非外来记录"，随后末位参与者按 R4 收尾）。
  外来世系记录且**可证死亡** ⇒ 落 R5：`released_owner_changed`，`cleanup_status=failed:owner_evidence_changed:<why>:foreign_lineage`，owner 记录**逐字节不变**、`resume_calls=0`。
- **实测**：F-L8d（调度者写入 `owner={"lease_id":"third-party-owner","pid":999999,...}`）⇒ `pause=1 / resume=0 / entries=[] / owner 字节不变`（FACTS §4 行 F-L8d）。
- **判定**：**不是设计冲突**，是**实现级澄清**——它只收紧 fail-closed 方向（把原本会 resume 的一格改成不 resume），不放松任何已签判据，也不改变 R1/R2/R3 与 R5 的既有格子。**待办**：是否回写进 I-04-C 正文见 §6b。

### 2.b ADR-9b 与 R5 的边界 —— 需要 reviewer 确认的解释（本卡唯一的可观察行为差异）

- **冻结文本冲突**：一个**存活**的第三方 owner 持有周期时，ADR-9b（I-04-C §10 修订行）说 "live leases route to the same branch"（进入 join/takeover 分支，即加入），而 R5（§12 ADR-10 末格）说"owner 为第三方且不可证死亡 ⇒ fail closed"。两条文字指向相反动作。
- **代码必须做什么**：enter 时遇到"`paused` ∧ 账本里有存活 lease ∧ owner 记录指向一个存活但非本世系的参与者"，必须二选一：加入（`joined`）或 fail closed（`lease_conflict_unknown`）。选错任一侧都不是崩溃，而是可用性/安全性的取舍。
- **本卡选择：加入**。理由：一次 pause 只对应一个周期，加入只**追加**自己的一条 lease，**不**发 pause、**不**写 resume 义务、**不**代第三方 resume；而 fail closed 会让同一台机器上两个真实参与者互相拒绝（F-L5 实测的正是这一格）。实现锚点：`_dispatch_locked` 的 `_owner_lease_live` 分支 → journal `joined_live_holder` → `_join_cycle_locked`。
- **与简报表述的一处偏差（如实登记）**：`_join_cycle_locked` 会把 owner 记录指向**加入者**（`state.owner = self._owner_record(state)`），因此"加入不改动 owner 记录"这一说法**不成立**；实际行为是"只追加自己的 lease、不发 pause、不建义务、不代第三方 resume，owner 记录落到加入者（存活参与者）身上"。这与 ADR-10e"owner 必须落在存活 lease 上"的方向一致，且可由 F-L5 的 journal 逐条复核：`joined_live_holder`（pid 4816 加入，owner 仍为 `95b0bae2ed79400ea993a038`）→ 加入者 release 时 `ownership_transferred` → `to: 95b0bae2ed79400ea993a038`（`dead_able: true`）→ 该存活者 `released_last` / `reason: owner_is_me`（`evidence\run\I04D-CASE-F-L5\summary.json` 的 `protocol_journal`）。
- **判定**：**需要 reviewer 确认的解释**（本卡唯一相对逐字读法改变可观察行为的一项）。**待办**：§6a。

### 2.c ADR-8 的守卫缺一格 —— 实现级澄清

- **冻结文本**：ADR-8 只写了"`desired_state == paused` ∧ 非本工具持有 ⇒ `respect_paused`"，并给出"本工具持有 = `schema=2 ∧ entries 非空`"。它**没有**明确"账本为空（或文件不存在）且无 `resume` 义务"时该在哪一格判定。
- **代码必须做什么**：`paused` ∧ `entries == []` ∧ `resume.required == False` ∧ 无 owner 记录时，必须判"这是**用户/外部**暂停"并零写退出。
- **本卡选择**：把该守卫放在 `_dispatch_locked` 的 paused 分支**最前面**（`_respect_user_pause_locked`，判据 `not state.entries and not state.owner`），优先级 = **用户意图 > 周期回收 > join/takeover**。没有它时代码会把用户的暂停当成自己的周期：对**已经停掉**的 worker 再 pause 一次、随后又 resume——本卡 F-L9a 用例抓到了这个回归（FACTS §3 第 6 条）。
- **实测**：F-L9a `pause=0 / resume=0 / lock_acq=1`，账本与 owner 标记全程不存在，worker 保持 `paused (untouched)`；子案 F-L9c 为 `pause=1 / resume=0`、终态 `entries=[] / owner=null`（FACTS §4）。
- **判定**：**实现级澄清**（只补上 fail-closed 一侧的判定入口，不改 ADR-8 的任何判据）。

### 2.d 释放段的"两段锁" vs "单段锁" —— 等价实现登记

- **冻结文本**：`oracle.md` §3.1 在实现级冻结约定里写了**两段锁**（段 A 持久化后**放锁**，段 B 重新取锁再 resume），并自注"崩溃窗口多一个（§5 W4'）"；I-04-C 的 kernel 则是**整段持锁**。
- **代码必须做什么**：`__exit__` 必须在同一个 ADR-3 语义下完成 {读状态 → prune → 删自己 → R1–R5 判定 → 持久化义务 → resume → 清账}。
- **本卡选择：单段**（enter 与 release 共用一个临界区；`_LeaseLocked` 按深度可重入，故 `__exit__` 复用 `__enter__` 路径已持有的锁）。**没有采用两段**的原因：两段会在"段 A 已持久化义务、段 B 尚未复查"之间新增一个崩溃/插入窗口（oracle §3.1 自己标注的 W4'），而 ADR-3 的全部内容恰恰是"发出的 resume 与周期结束的记账同处一个临界区"；单段把这个窗口消掉，代价只是临界区保持时间 H 略长（H 的排队代价已在 I-04-C §14 F-I04C-12 登记为设计上可接受的退化）。
- **ADR-3 的两个段落在同一临界区内**：段 A 的 `_persist_locked(state, resume_required=True)`（LP-3）与段 B 的 `_worker_resume(...)` 之间不释放锁，任何并发参与者在拿到锁后读到的都是"已清空 ∧ 有义务/有 owner"，不存在"空且无义务"的中间可见态。
- **判定**：**等价实现**（未改动 R1–R5 任何期望值；F-L6 / F-L6b / F-L5 在 scheduler 层全绿）。**待办**：reviewer 确认该等价性，并注意它偏离的是 `oracle.md` §3.1 的实现级约定，而不是 I-04-C 的正文；与 §6e 的三个时序敏感断言相互独立。

### 2.e 探针的"无法回答"与"已死"必须分开 —— 实现级澄清

- **冻结文本**：ADR-4 规则 5 要求"探针异常/超时/未知 ⇒ `unknown` ⇒ 不回收、直接 fail closed（`lease_conflict_unknown`）"，但冻结文本没有规定**底层的返回值形状**如何区分二者。
- **代码必须做什么**：Windows 探针有两条返回空的路径——"pid 不存在"与"OS API 失败"；若两者都返回空，调用方无法区分"已死（可回收）"与"问不出来（必须 fail closed）"；实测到的最坏表现是"**已退出的 pid 被判 alive**"（FACTS §3 第 8、9 条）。
- **本卡选择**：探针改**三态** `_process_exists` 返回 `True` / `False` / `None`，与 `_process_start_time_raw` 分离；只有显式 `False`（pid 不存在）或 start_time 不匹配（pid 复用）才是回收证据，`None` 一律 `unknown`。判定入口 `_probe_entry_verdict` 输出 `self | alive | dead | reused | unknown`，`unknown` 在 `_classify_locked` 里直接抛 `lease_conflict_unknown`（零写零 CLI）。
- **实测**：F-L8g-UNKNOWN ⇒ `pause=0 / resume=0 / lock_acq=1`、账本 sha256 前后不变、worker 保持 running（FACTS §4）。
- **判定**：**实现级澄清**（把"未知 ≠ 死"落成可执行的返回形状；不新增/不放松任何预算上限）。

### 2.f 附加观察：释放路径中 `owner_probe:alive` 一格（未经用例覆盖，提请 reviewer）

- 现象（**代码阅读所得，本卡未改动、无任何 case 覆盖、也无实测数字**）：`_release_common_locked` 的 R4/R5 判定中，`_probe_owner_death` 返回"非可证死亡"时的兜底格是 `else: reason = why`（随后 `resume_required=True` 并 resume）。该格除覆盖本世系的 `owner_is_this_incarnation` 与"本次 prune 回收的 owner"外，也会覆盖 `owner_probe:alive` / `owner_probe_timeout` / `owner_probe_error:*`。
- 与逐字读法的张力：R5 的原文是"owner 为第三方且**不可证死亡**／owner 记录缺失／探针 unknown ⇒ `released_owner_changed`，不 resume"。一个**存活**的第三方 owner 记录（且其 lease 不在账本里）按该读法应落 R5，而当前实现会 resume。
- 本卡处置：**不改代码、不新增断言**（无覆盖用例时改行为属越权）；仅登记，交 reviewer 判定是否收紧为 R5，并建议补一个"第三方 owner 记录指向**存活** pid"的用例（与 F-L8d 配对，F-L8d 用的是已死 pid 999999）。见 §6f。

---

## 3. R5 终态的人工解除指引（carry 2 / O-1）

代码里 `cleanup_status` 以 `failed:` 开头时，`__exit__` 会调用 `_print_release_guidance()`，把**原始记录**与下列步骤打到 stderr。运维步骤（与代码打印逐条一致）：

1. 确认**没有** filing-fetch 下载在运行（工具打印的命令：`tasklist /FI "IMAGENAME eq python.exe"`）。
2. 若 worker **应当**继续运行：执行 `python -m company_wiki.source_catalog.cli worker-resume`。
3. **只有**当第 2 步报告它**已经在运行**时，才删除 refcount 与 owner 两个文件（路径见下）。
4. **绝不**删除一条你**没有完整读过**其 owner 记录的 lease（读不懂就保留现场，交下一个 acquire 或人工处置）。

工具实际打印的原始记录（`_print_release_guidance` 的输出，逐项）：

| 打印项 | 内容 |
|---|---|
| 首行 | `[filing-fetch] worker lease NOT released: <cleanup_status>` |
| refcount 路径 | `[filing-fetch]   refcount : <_pause_state_path(root)>` |
| owner 路径与存在性 | `[filing-fetch]   owner    : <_pause_owner_path(root)> (exists=<True/False>)` |
| **原始账本文本** | `[filing-fetch]   raw state: <账本文件原文>`；文件不存在或不可读时为 `<refcount file is absent or unreadable>` |
| 步骤 | `to release by hand:` + 上述 1)–4) 四条 |

补充口径：该指引是 carry 2 / O-1 的落点（FACTS §6 第 2 条）：R5 允许"paused 且无可归因义务"作为**故意的 fail-closed 终态**，恢复**只**由下一个 acquire 或人的手工动作发生；本卡**不**新增后台自愈进程/定时器（I-04-C §8 O-1）。

---

## 4. 与 I-04-A / I-04-B 的数值关系（carry 9）

- **没有就地改动任何 I-04-A 数值**（FACTS §6 第 9 条；本卡只登记，不改写）。
- `C = max(30, 2*resume_wait + graceful)`：恒等，用于**清理段**相位预算（`_cleanup_timeout`），与 deadline 无关；`_cleanup_remaining` 只在清理相位内递减，绝不为一个临界区新造一个 C。
- 探针预算 ≤ `min(20, 相位预算, 5)`（`_PID_PROBE_MAX_SECONDS` / `_PROBE_SOFT_CAP_SECONDS`；I-04-B 的"探针 ≤ min(20, 相位)"再收紧，不放松）。
- **请求段相位预算无下限**（`deadline - now`，I-04-A D3）：`<= 0` 时 `_enter_locked` 直接 `deadline_exhausted`、`_acquire_lock` 直接 `lease_lock_timeout` 且**不尝试加锁**。
- **清理段预算独立**：不继承请求段的剩余（清理段的锁等待受 `lock_budget_for(C)` 约束，超时落 `cleanup_status=failed:lease_lock_timeout`）。
- `LOCK_MAX_SECONDS = 60.0` 来自 **I-04-C**（`lock_budget_for(x)=min(x,60)`；OPEN-3 / owner 门 C2），本卡**逐字使用**、不加解释地按 60 执行（裁定前一律 60，见 §6c）。
- 如果上述任何一条需要改动，本卡会停下并退回 I-04-A 重新签值——**没有发生**。

---

## 5. I-04-E 需要的信封字段（carry 6，只登记需求）

以下字段名来自 FACTS §6 第 6 条。本卡**只登记需求**，"值今天已存在于哪里"一栏是现状定位，**不构成 I-04-E 的任何结论**（本卡不声称字段口径、命名或验收标准已经定稿）。

| 字段 | 必须承载什么 | 值今天已存在于哪里 |
|---|---|---|
| `lease_lock_waits` | 进入加锁循环的次数（含最终失败的等待） | `stats["lease_lock_waits"]`（`_acquire_lock` 内自增；`_normalize_stats` 给默认 0） |
| `lease_lock_acquisitions` | 真实成功获取 OS 字节锁的次数 | `stats["lease_lock_acquisitions"]`（`_acquire_lock` 自增，`__exit__` 再落一次）+ journal `lease_lock_acquired`（含 `budget` / `wait_seconds` / `pid`） |
| `lease_lock_max_wait_seconds` | 单次等待的最长值（诊断用，非验收上限） | `self._max_lock_wait` → `stats["lease_lock_max_wait_seconds"]` + journal `release.max_lock_wait_seconds` |
| `lease_ledger_writes` | 账本持久化写次数（含失败的写尝试，供"是否发生过失败写"判定） | `self._ledger_writes` → `stats["lease_ledger_writes"]` |
| `lease_resume_reason` | 该次 resume 的授权依据（`owner_is_me` / `inherited_obligation` / `owner_probe:*` / `owner_pruned:*`） | `self._resume_reason` → `stats["lease_resume_reason"]` + journal `released_last.reason` |
| `lease_owner_transferred_to` | ADR-10e 移交的继承人 lease_id（无移交则为空） | `self._transfer_to` → `stats["lease_owner_transferred_to"]` + journal `ownership_transferred.to` / `released_joined.transferred_to` |
| `cleanup_status` | 清理段结论：`not_needed` 或 `failed:<reason>`（绝不被 cleanup 失败改写 `pause_action`） | `stats["cleanup_status"]`（`_normalize_stats` 默认 `not_needed`）+ journal `release.cleanup_status` |
| `cleanup_elapsed_seconds` | 清理段自身的墙钟（与请求段计时分开） | `stats["cleanup_elapsed_seconds"]`（`__exit__` 计算） |
| `pause_action` | 请求段结论（`paused_by_us` / `joined` / `respect_paused` / `takeover_resumed` / `released_*` / 各 `lease_*` 失败族），**绝不**被清理失败改写 | `stats["pause_action"]` + journal `release.action` |
| `liveness_calls` | 判活探针调用次数（I-04-A R-P 行口径） | `stats["liveness_calls"]`（`_prune_locked` 每次条目判定自增）+ 响应体 `liveness_calls` |
| `liveness_probe_failed` | 判活探针失败次数（失败 ⇒ 相关判定为 `unknown`） | `stats["liveness_probe_failed"]` + 响应体（成功与错误响应两处都带） |
| 相位墙钟 `phase_wall_seconds` | 该相位的墙钟，**只报告、不设验收上限**（I-04-B carry 3） | journal `release.phase_wall_seconds` 与每个 case 的 `summary.json.phase_wall_seconds`（如 F-L5 = `1.0637`） |

口径提示（现状，不是结论）：上列字段中 `stats[...]` 属**返回体**（权威方向），journal 行按 ADR-7 **不是权威**（缺权限时静默跳过、守卫判据不得依赖它）。

---

## 6. 未决 / 需 owner 或 reviewer 拍板

| # | 问题 | 现状与影响面 |
|---|---|---|
| **a** | **ADR-9b 与 R5 的边界**：一个**存活**的第三方 owner 持有时，应当是"加入"（本卡选择）还是"fail closed"（R5 逐字读法）？另外，加入时把 owner 记录指向加入者（`_join_cycle_locked`）是否符合设计意图——I-04-C 文本并未规定 join 是否顺手接管 owner 记录？ | §2b；唯一相对逐字读法改变可观察行为的一项；证据 `evidence\run\I04D-CASE-F-L5\summary.json` 的 `protocol_journal`（`joined_live_holder` → `ownership_transferred` → `released_last`） |
| **b** | **R4 的 lineage 限定是否回写进 I-04-C 正文？** 该限定目前**只存在于本卡的实现**（`_owner_is_our_lineage` + "本次 prune 回收的 owner"两条门槛），I-04-C §12 R4 的原文仍只要求"owner 可证死亡" | §2a；回写属 I-04-C 的文本维护，本卡只登记（不回写上游冻结文本） |
| **c** | **OPEN-3 / C2（I-04-C 已携带的 owner 裁定项）**：(1) 等待上限常数 `LOCK_MAX_SECONDS = 60` 的命名与边界验收；(2) `worker-pause` 是否允许留在锁内。**本卡维持 `worker-pause` 在锁内**（`_worker_pause` 在 `_fresh_cycle_locked` 内、临界区中调用），与 I-04-C §8 O-3 / §14 F-I04C-12 末段一致；裁定前一律按 60 执行 | I-04-C §8 O-3、§12「ADR-2 锁预算（v1.2 定稿）与 OPEN-3」、§14；本卡不改该值、不改文本 |
| **d** | **O-2 `pause_origin` 跨仓依赖**：用户在本工具 scope 内按下的暂停，只有在 company-wiki 侧提供"暂停来源"信号后才可能被保护；company-wiki `control.py` 现值**没有** origin 信号（只读检视，未做任何变更）。是否由 owner 立项推动 wiki 侧接口？ | FACTS §6 第 4 条；本卡**未实现**该依赖，也不臆造 wiki 变更（oracle §2 P4 已登记的已签限制） |
| **e** | **harness 债务**：`tests/test_fetch_filing_lease.py` 的三个断言 `test_f_l5_two_processes_one_pause_one_resume`、`test_f_l6b_exactly_one_resume_when_a_leaves_while_b_holds`、`test_l8a_w1_no_owner_marker_is_not_a_user_pause` 是**顺序敏感**的（断言取的是调度者在一个 park 竞态之后拍的快照，而非协议事实）；同名的 scheduler case 在 `evidence\run\` 层全绿，且被断言的不变量确已被覆盖（两条 lease 共存 / 同伴存活期间不 resume / 崩溃不被读成用户暂停）。正确修法是让调度者在 gate 握手**之内**拍快照 | FACTS §5；末次 pytest = `18 passed, 3 failed`（本文件不声称该项全绿） |
| **f** | **（本卡附加登记，未经用例覆盖）** 释放路径的兜底格 `else: reason = why` 也覆盖 `owner_probe:alive` / `owner_probe_timeout` / `owner_probe_error:*`：一个**存活**的第三方 owner 记录（其 lease 不在账本里）会被 resume，而 R5 的逐字读法要求 `released_owner_changed`、不 resume。是否收紧为 R5，并补一个"第三方 owner 指向**存活** pid"的用例（与 F-L8d 配对）？ | §2f；纯代码阅读所得，**无实测数字、无覆盖用例**，本卡未据此改动任何代码 |

---

## 7. 本卡不授予的资格

以下为 FACTS §8 的"未做/未授予"内容，逐条以**明确的非授予**表述（另附 oracle §9 的同向非授予）：

1. **未运行变异证明**：oracle §7 的 M1–M11 一条都没有执行（命令清单与未决原因见 `review.md`）；因此**不授予**"每条判据都已被变异反证"的资格。
2. **POSIX 分支未验证**：`fcntl.flock` 分支已实现但**从未被实际执行**；**不授予** POSIX 平台资格（亦**不授予** SMB/NFS 等非本机盘的锁资格，oracle §9）。
3. **无真实下游**：没有真实 company-wiki worker、没有真实 catalog、没有 provider、没有网络；**不授予**真实并发/真实下载资格（stub worker 只改一个 JSON 状态文件，oracle §0/§9）。
4. **生产仓库未改动**：`filing-fetch\scripts\fetch_filing.py` 仍为 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`；company-wiki `catalog.sqlite3` 仍为 49,677,344,768 字节 @ `2026-09-19T06:31:35Z`、`-wal` 0 字节。**不授予**生产实现资格（`iso/` 是隔离副本）。
5. **不授予 I-04-E 的任何结论**：本卡只按 carry 6 列出它需要的字段名与现状来源（§5）。
6. **不授予**"用户在本工具 scope 内按下的暂停已被保护"的资格（`pause_origin` 缺失，见 §6d）。
7. **不授予**验收/签署资格：状态为 `review_pending`，实施者不签署（FACTS 头部）；末次 pytest 仍有 3 个失败（§6e）。

---

## 8. 与上游文本的冲突登记（结论）

- **结论：没有发现任何使设计无法实施的冲突。** I-04-C v1.3 的 ADR-1…ADR-12、R1–R5 与 `lock_budget_for(x)=min(x,60)` 全部被落地；本卡没有一处因为"设计不可实施"而停下或改设计。
- §2 的四项（2a、2c、2d、2e）是**澄清 / 等价实现**：2a 只收紧 fail-closed 方向；2c 只补上判定入口；2d 是等价实现（不释放锁的更强形状）；2e 把"未知 ≠ 死"落成返回形状。四项都不改动任何已签数值或期望值。
- §2b 是**唯一**相对逐字读法改变可观察行为的一项（存活第三方 owner ⇒ 加入而非 fail closed；其中 owner 记录接管入加入者一节见 §2b/§6a），已登记为**需要 reviewer 确认的解释**。
- §2f 是本卡在阅读实现时发现的**未测观察**（无覆盖用例、无实测数字、本卡未据此改代码）；它**不是**设计冲突，也**不是**已确立的行为差异，交由 reviewer 判定是否收紧为 R5。
- **本文件不重开 I-04-A / I-04-B / I-04-C 的任何数值**：`C = max(30, 2*resume_wait + graceful)`、探针 `min(20, 相位预算, 5)`、请求段无下限、清理段独立、`LOCK_MAX_SECONDS = 60`（I-04-C 的 OPEN-3 / C2，逐字使用）均按上游执行（§4）。
