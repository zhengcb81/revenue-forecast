# I-04-C 独立复审记录

> **状态：PENDING —— 独立 reviewer 尚未给出结论。**
> 本文件由实施者起草，只提供"读什么、验什么、已知哪里会翻车"的索引；
> **实施者不写自己的判决**，也不得在此写 accepted / changes_required。
> 复审请把结论填在文末的「reviewer 结论」栏（含签名与范围限定）。

## 0. 复审对象与最小读法

| 文件 | 作用 |
|---|---|
| `decision.md` | **冻结的协议**（ADR-1…ADR-11、状态机、线性化点、崩溃窗口、兼容升级、与 I-04-A/B 预算的组合、§10 运行后的实测修订） |
| `oracle.md` | 运行前冻结的期望（F-L1…F-W5 + 锁压力），以及 §8 模拟资格声明（含 DECLARED 判活模型） |
| `commands.json` | 每条命令的 cwd/argv/预期/实际退出码与原始日志路径 |
| `evidence/run-all.txt` + `evidence/failures.txt` | 协议套件的原始 stdout 与逐 case 失败明细 |
| `evidence/lock-and-legacy.txt` | 锁原子性（F-LK1/2/3）与三个 RED 反例的原始输出 |
| `evidence/run/<case>/**` | 每 case 的参与者 stdout/stderr、journal、refcount/owner 快照、worker 动作日志 |
| `sim/kernel.py` | 协议实现（**只有实现者写的模拟内核；不是产品代码**） |
| `evidence/hashes.txt` | 全部产物 sha256 + 生产 `fetch_filing.py` 复核 |

**建议的复算顺序**（reviewer 固定操作第 4 条：至少独立复算一个卡片专属 oracle）：

1. **复算 F-LK1/F-LK2**：`evidence/lock-and-legacy.txt` 里 `final=200 / lost_updates=0`（有锁）与
   `final=10 / lost_updates=190`（无锁）——重跑 `sim/scheduler.py run F-LK1 F-LK2` 即可重现，
   不需要读任何实现代码就能判断"读改写必须有互斥"。
2. **复算 F-LK3**：`parent_wait_seconds = 0.0004`、`holder_exit_code = 90`、`cleanup_action_required = false`
   ——对应 ADR-1"内核释放，不需要打破锁"。
3. **复算 F-L1-nolock**：`evidence/run/F-L1-nolock/` 里 refcount 只剩一条 `pid`，
   而两个进程都记录 `legacy_register first=true` ——对应 ADR-1 的反例。
4. **复算 F-L1 的租赁时间线**：`evidence/run/F-L1/` 的四个快照（1→2→1→0）与
   `journal.jsonl` 的 `worker_pause`/`worker_resume` 各一次。

## 1. 实施者自报的通过 / 未通过（供 reviewer 核对，不构成结论）

**通过**（`evidence/failures.txt` 的 `=== <case> PASS` 行）：
F-L1、F-L2b、F-L2c、F-L3a、F-L3b、F-L3c、F-L4b、F-L4c、F-L4e、F-W4、F-W5；
锁压力 F-LK1、F-LK2、F-LK3；RED 反例 F-L1-nolock、F-L1-nolock-guard。
（另：iso 未改动源码的既有契约测试 `-k "pause or resume"` = **8 passed / 109 deselected**，
见 `commands.json` 的 I04C-06，证明本设计卡没有改动任何既有行为。）

**未通过**（原始输出保留；实施者**没有**改断言、没有放宽期望、没有换样本）：

| case | 失败的检查 | 实施者的初判（**请 reviewer 裁定**） |
|---|---|---|
| F-L2a | `one lease outlives the other's release`；`a new participant joins the existing pause cycle`；`joining does not pause again` | **混合**：嵌套实测显示"同进程第二个 scope 会 join 并向 refcount 追加第二条 lease"，这是 v1 oracle 没预设的口径；但同进程 join 的第三条检查同时暴露 ADR-9b 的 `fresh_cycle_recovering` 与 join 的选择依赖锁内 status |
| F-L2d | `exactly one resume, from the last releaser`；`exactly one release is the resuming one`；`state cleaned up` | **规则缺口（已部分修）**：8 个真实并发参与者时，收尾仍是 `released_took_ownership` 而非 resume，留下 `resume_required=True`。ADR-10(c) 把义务交给"下一次"；请判定"下一次"是否必须包含同一批次的最后一个 release |
| F-L4d | `the resume attempt is still recorded`（`attempted_resumes` 口径） | **模拟口径**：注入的 resume 失败发生在 CLI 之前，`attempted_resumes=1` 但 worker 动作日志为 0；oracle 想让两者都可读 |
| F-W1 | `B's release closes the cycle with one resume`；`state cleaned` | **规则/调度混合**：B 在 join 后与 A 的剩余 lease 交织，收尾义务落在谁身上需 reviewer 裁定 |
| F-W2 | `the orphaned pause was resumed exactly once`；`B's own cycle closes with the second resume`；`state cleaned` | **同上**：孤儿 pause 被 B 接管后，B 自己的 release 是否必须立刻收尾 |
| F-W4b | `B saw a clean empty state ... opened a NEW cycle`（B 观察到的状态与 oracle 设想的"干净空闲"不同） | **时序**：A 的 release 与 B 的 acquire 之间的可见状态需按 ADR-3 的"三选一"重新表述 |

**已知会误导 reviewer 的三处（实施者主动披露）**：

1. `decision.md` §10 记录了**运行后才修订的五处实现级规则**（ADR-9、9b、10、11、ADR-2 锁预算）。
   这些修订由失败运行逼出，已落进 `sim/kernel.py`；oracle 的**语义**未变，但 `action` 名字变了。
   请判定"这是设计缺口被测试逼出来"还是"实现者事后放宽"。
2. 模拟内核 `sim/kernel.py` 一度同时存在**两个 `protocol_paused_branch` 定义**（旧签名覆盖新签名），
   表现为与 ADR-11 相同的症状。修好后 F-L2d 的 pause 计数从 8 降到 1。请复核当前文件里
   每个协议函数只有一份定义。
3. 判活模型是 **DECLARED（申报）** 而非真实 OS 探针（`oracle.md` §8 有完整说明与理由）。
   真实探针会把"enter 已完成、release 由调度者稍后运行"的参与者判成 dead，
   从而误判 lease 过期。请判定该模型是否可接受，或要求改用 `lifetime` 模式（一次进程内跑完 enter+release，
   `sim/participant.py` 的 `run_lifetime`）重做全部 case。

## 2. 请 reviewer 优先攻击的点（实施者的建议顺序）

1. **ADR-3 + ADR-10 的交接链**：构造"最后 release 与新 acquire 同时到达"的第三种时序
   （新参与者在 owner 释放临界区**之前**到达、在**之中**到达、在 resume 已发出但未确认时到达），
   核对是否仍满足"同一次 pause 周期只 resume 一次、永不留下 paused 且无人有义务"。
   `sim/kernel.py` 的 `run_protocol_exit` + `protocol_paused_branch` 是全部判定点。
2. **`resume.required` 的持久化点**：是否真的在"删除自己 lease"的**同一次 `os.replace`**里
   （ADR-3/ADR-5 W4）；用 `evidence/run/F-W4/` 的 `wm-release-before-resume` 崩溃点核对。
3. **`classify()` 的五种判定**：特别是"记录 `os_start_time` 但探针给不出创建时间 ⇒ UNKNOWN ⇒ fail closed"
   这条会不会在**真实**环境（Windows `GetProcessTimes` 不可用）把正常并发全部 fail closed。
4. **ADR-9b 与 join 的选择**：有 lease 但 worker 未暂停时，"接管并保留下属 lease"是否可能
   让一个已经放弃的参与者继续持有 lease（僵尸 lease）。
5. **锁预算公式（ADR-2 修订）**：`min(phase_budget, 60)` 是否与 I-04-A D3"截止后不得发起"一致；
   把 `request_budget` 压到 <1 s 时是否仍有确定的 fail-closed 语义。
6. **兼容升级（ADR-7）**：旧格式 list 一律 fail closed 是否会在生产升级窗口里把正常请求全部拒绝；
   `FILING_FETCH_PAUSE_LEASE_MIGRATE=1` 的迁移条件是否足以避免"用户暂停被当成我们的暂停"。

## 3. 本轮明确未验证（照录，不得外推）

- 真实 company-wiki worker / provider / wiki 根：本卡一律未接触（stub 只改一个 JSON 文件）。
- 真实 PID 复用：`GetProcessTimes` 探针未实测，`os_start_time` 语义在真实进程上未验证。
- POSIX 分支（`fcntl.flock`）与网络盘（SMB/NFS）上的锁语义。
- 同进程多线程并发 scope（ADR-4 末行，需要两级锁，未授予）。
- 生产移植：`decision.md` §ADR-6 明确指出 I-04-B 的修复目前只在
  `execution_runs/I-04-B/a20260919-01/iso/`，生产代码仍是 `_remaining()` 的 `max(10.0, …)`；
  lease 层不得自行实现一份 `_remaining()`。

## 4. reviewer 结论（**留空 —— 由独立 reviewer 填写**）

- 结论：`<accepted_scoped | changes_required | blocked | not_applicable_with_reason>`
- 复算过的 oracle：
- 未复现/未验证项：
- 授予的资格与明确不授予的资格：
- reviewer（agent id / 时间）：
