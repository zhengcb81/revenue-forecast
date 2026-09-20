# I-04-D 实现者自述（**不构成验收**）

卡：`I-04-D`（实施原子 lease 更新并验证进程交错）。attempt：`a20260919-01`。
本文件由**实现者**撰写，`status = review_pending`。**实现者不自签 accepted**；§9 的判决栏留空，只允许独立 reviewer 填写。
本文件的数字全部来自本 attempt 的盘上证据与 `scratch/FACTS.md`（唯一数字来源）；凡 FACTS 没有记录的，本文件标为"未采集 / 无证据"，不做推断。

> **落盘时点说明（诚实登记）**：本文件由实现者撰写时，`commands.json`、`changes.diff` 与 `oracle.md` 的追加区 R1 **尚未落盘**（并行工作的其他 agent 在同一 attempt 内写入）。实现者在它们落盘后**逐项复核并把差异写入本文件**：§2 的证据索引、§3 的口径、§4 的证据状态、§5 的 (h)(i)(m) 与 §6 都已按盘上现状更新。因此**请以盘上文件为准**；本文件仍不构成任何验收。

---

## §1 本卡做了什么

本卡把 I-04-C 已签的 pause/lease 协议（ADR-1…ADR-12、R1–R5 分支表、`lock_budget_for(x)=min(x,60)`）**移植进隔离副本** `iso/filing-fetch/scripts/fetch_filing.py`，而不是移植进生产仓：生产 `filing-fetch/scripts/fetch_filing.py` 在交付时仍是 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`，本卡一个字节都没有写它。移植是**确定性**的：`scratch/patch_i04d.py --apply` 从 I-04-B 的已验收输出（基线 sha256 `dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c`，56405 bytes）生成输出（sha256 `a72546c50401a4b1876288bea6b6d7e4a72db9c39fd028c7bfb75a6f929ad198`，126274 bytes），并且**基线 hash 不匹配就拒跑**。验证方式不是单进程 mock：三个真实 OS 子进程角色 + 文件栅栏（gate）编排出 19 例交错场景，每例留下 `summary.json`、每参与者 report、fake worker journal（含每次调用的真实 `pid`/`ppid`）与终态快照。写盘范围只在本 attempt（外加 harness 路径长度所需的短路径 case 根，见 §5 与 `recovery/README.md`）。

`iso/` 内文件及其角色（按 FACTS §1）：

- `iso/filing-fetch/scripts/fetch_filing.py` — **被测源码**（唯一的协议实现落点；输出 sha256 `a72546c5…a436`，126274 bytes）。
- `iso/filing-fetch/scripts/i04d_fake_worker.py` — **假 worker 命令进程**（sha256 `5f16f0fe…a902`）：只改一个 JSON 状态文件并 append 一行 journal；**不是**真实 worker，**不**接触真实 catalog。
- `iso/filing-fetch/scripts/i04d_participant.py` — **参与者进程**（sha256 `eabd3961…e889`）：真实独立子进程，直接使用被测的 `PausedWorkerScope`（不复制实现），写自己的 report JSON（pid / boot_uuid / lease_id / action / stats / 快照 hash）。
- `iso/filing-fetch/scripts/i04d_schedule.py` — **调度器**（sha256 `f2edc307…e766`）：起真实子进程、按文件栅栏放行、采集终态与 `summary.json`。
- `iso/filing-fetch/tests/test_fetch_filing_lease.py` — **18 项 pytest 断言套件**（sha256 `27f492b1…127b`）。
- `scratch/patch_i04d.py` — 确定性补丁生成器（sha256 `a730362c…99ce`，幂等、基线 hash 校验）。
- 未在本 attempt 产出：`decision.md`、`changes.diff`、`commands.json`（见 §5 与 §8；`binding.json.new_files` 还列了 `iso/filing-fetch/scripts/i04d_mutants.py`，变异证明未跑，故其存在与否未作为本卡主张）。

---

## §2 证据索引（reviewer 请**按序**读实际内容，不要只看文件名/hash）

1. `oracle.md` — 运行前冻结的期望集合（P1–P5、N1–N13、退出码固定表、崩溃注入点位表、M1–M11 变异队列、carry 落点表）。先读它，才能判断后面一切是"符合期望"还是"事后合理化"。
2. `evidence/oracle-freeze.txt` — 冻结时点记录：oracle.md 写在 iso 源码被修改**之前**，冻结时 iso 基线 = `dc593a75…af1c` / 56405 bytes。
3. `before/i04d-red.txt` — 修改前原始 pytest 日志（rc=1，`17 failed, 2 passed, 2 skipped in 14.59s`）。
4. `after/i04d-green.txt` — 修改后原始 pytest 日志（**rc=1，`18 passed, 3 failed`**；GREEN 那次调用的 basetemp 是 `after/lease-basetemp`，见 `commands.json` 的 `I04D-06-t-filing-green`）。
5. `evidence/hashes.txt` — 本 attempt 的 hash 清单（binding.json / oracle.md / 四个 iso 文件 / patch 脚本 / RED 与 GREEN 日志 / 三个 before 捕获）。
6. `evidence/run/<case>/summary.json` — **19 例调度器主证据**（`I04D-CASE-F-L5`、`F-L6`、`F-L6b`、`F-L7`、`F-L7b`、`F-L7c`、`F-L8a-W1`、`F-L8a-W1b`、`F-L8b-W2`、`F-L8c-W4`、`F-L8d`、`F-L8g-UNKNOWN`、`F-L8h-WRITEFAIL`、`F-L9a`、`F-L9c`、`F-LK-TIMEOUT`、`F-LK-TIMEOUT-ZERO`、`F-LK-HOLDER-CRASH`、`F-LK-NEVER-UNLINK`）；同目录还有 `report.<tag>.json`、`worker.jsonl`、`worker_state.json`，两个有诊断的案例另有 `hook-probe.log`，以及每例 wiki 树。
7. `oracle.md` 的**追加区 `# 追加 R1`**（第 294–367 行；冻结正文第 1–290 行未改）—— 实施逼出的两处"设计沉默处"显式化：**R1-3**（R4 接管必须同时要求"同一进程世系"与该世系可证死亡）与 **R1-4**（存活的第三方 owner 归 ADR-9b"加入"，不归 R5"拒绝"）、R1-5（崩溃用例实测表）、R1-6（变异未做）、R1-7（套件 18/3 的诚实状态）。这两条正是 §5(c) 与 §5(d) 的攻击点，**必须先读**。当前 `oracle.md` 367 行，sha256 `e50380d6e99f80c1567af5d0e2191dddc2d1f42b69f7d2d8a0a38c39c4a87a20`（注意 `evidence/hashes.txt` 里记的是追加前的 `e2b9029f…b690`，两个都对，只是时点不同）。
8. `commands.json` — 本 attempt 的命令登记表：8 条已跑命令的 argv/cwd/`expected_returncode`/`raw_returncode`/产物，另有 `not_run` 里的变异证明（未跑）。已核对：7 条 raw==expected，唯一不一致的是 `I04D-06-t-filing-green`（expected 0 / raw 1）。
9. `changes.diff` — iso/ 相对 I-04-B 基线的完整 delta（180917 bytes；added=4 removed=0 modified=1；路径为 attempt 根的 POSIX 相对路径，**不含任何生产仓文件**）。生成命令 `I04D-07-changes-diff`（`scratch/make_diff.py`，rc=0）。
10. `handoff.json` — 九步、命令与原始/期望退出码、`measured_results`、`carries_disposition`、`not_granted`。
11. `recovery/README.md` — 回滚/恢复配方（含 scratch-only 变异配方与 pid 处置规则）。
12. `scratch/REPORT.md` — 同级实现者摘要（说明 `decision.md` 应由并行 agent 产出；见 §5(m)）。

**`decision.md` 在本次交付时仍不存在**（全 attempt 递归搜索无该文件）。FACTS §6 的 carry 2 与 carry 6、`scratch/REPORT.md` §8、`oracle.md` R1-3/R1-4 都声称"已登记在 decision.md 第 2b/第 6 节"，但盘上没有。reviewer **不得**按"已存在"处理；这条已登记为 §5(m)。

---

## §3 RED → GREEN 的原始结论

- RED：从 `iso/filing-fetch` 跑同一套断言，`rc = 1`，结果 **`17 failed, 2 passed, 2 skipped in 14.59s`**（`before/i04d-red.txt`）。冻结时期 iso 基线 = `dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c`。2 个 pass 是 legacy 代码也满足的两个 `F-LK-*`（持锁不可再获取；legacy 没有锁文件可 unlink）；2 个 skip 是依赖 lease journal 的检查（legacy 不写 journal）。
- GREEN：同一 argv、自己的 basetemp，`rc = 1`，结果 **`18 passed, 3 failed`**（`after/i04d-green.txt`）。
- **必须说明白**：GREEN 套件**不是全绿**，就是 **18 passed / 3 failed**。3 个失败是 `test_f_l5_two_processes_one_pause_one_resume`、`test_f_l6b_exactly_one_resume_when_a_leaves_while_b_holds`、`test_l8a_w1_no_owner_marker_is_not_a_user_pause`。原因：这三个断言读的是**调度器在 gate 放行之后**取的快照，而被 park 的参与者可能已经被放行，所以断言对 harness 的 park 竞态**顺序敏感**，而不是对协议敏感；同样三个案例在调度器层是通过的（§4 的 pause/resume/lock_acq 与终态就是它们），且底层不变量确有断言覆盖（两条 lease 共存、peer 存活期间不 resume、崩溃不被读成用户暂停）。这正是 §5(a) 要 reviewer 攻击的第一点。
- **主证据是调度器 run 树**，不是 pytest 汇总行：`evidence/run/<case>/summary.json` + `report.<tag>.json` + `worker.jsonl` + `worker_state.json` + 每例 wiki 树。19 例逐例 GREEN（例名清单见 §2 第 6 项）。每例都带真实 `participants.<tag>.pid`、`started_monotonic`/`finished_monotonic`/`elapsed_seconds`、`exit_code`；"谁真的发了 pause/resume"由 fake worker journal 里每次调用的 `pid`/`ppid` 判定，不由被测返回值自报。崩溃注入用的是冻结退出码：W1 → 90、W2 → 91、W4 → 92。

---

## §4 负例清单与结果

编号按 **oracle.md §4 的 N1–N13**。但**oracle 编号与调度器案例名不是一一对应**，先把对应关系钉死（这是本节的第一个事实）：

- N1 → 案例 `F-L8a-W1`；N2 → `F-L8a-W1b`；N3 → `F-L8b-W2`；N4 → `F-L8c-W4`；
- N5/N6/N7 → **没有任何调度器案例**，只有 pytest 断言（`F-L8d-corrupt` / `F-L8e-legacy` / `F-L8f-element-corrupt`）；
- N8 → `F-L8g-UNKNOWN`；N9 → `F-L8h-WRITEFAIL`；N10 → `F-LK-TIMEOUT`；N11 → `F-LK-TIMEOUT-ZERO`；N12 → `F-LK-HOLDER-CRASH`；N13 → `F-LK-NEVER-UNLINK`。
- oracle §7 的 M9 另引用一个 **N14（两进程同时持久化）**，该案例在冻结 §4 里并不存在（见 §6）。

**总负例数 = 13。** 证据状态分三档：**6 条有调度器实测值**（N1、N2、N3、N4、N8、N13）；**4 条只有部分实测 + 缺判据字段**（N9、N10、N11、N12）；**3 条在已跑的任一证据树里没有任何原始记录**（N5、N6、N7；它们目前只有 pytest 断言，而 pytest 汇总行是 `18 passed, 3 failed`，FACTS 未提供逐例结果）。**本文件不声称 13 条全部变绿。**

| # | 场景（注入点） | 冻结期望（oracle.md §4） | 实测（FACTS §4 的 scheduler 值；FACTS 无记录者写"未采集/无证据"） |
|---|---|---|---|
| N1 | `F-L8a-W1`：首参与者在 `after-refcount-before-owner` 硬退出（rc 90） | 判 A 死 ⇒ 回收；`pause_calls=1`（只 B 自己 pause）；B 不把"无 owner"读成用户暂停；A rc=90、B rc=0；终态清空 | pause 1 / resume 1 / lock_acq 3；终态 ledger **absent**、worker **running** ⇒ 与"1 次 pause、终态清空"一致。oracle 追加区 R1-5 记该例 B 为 `released_last`。**B.action 的原始字段值**须从 `report.B.json` 直读（FACTS 只给计数与终态）。 |
| N2 | `F-L8a-W1b`：同 N1 但 A 随后正常退出 | A 走 `released_noop`、A 不发 resume、A 不得删 B 的 lease；`resume_calls` 仅由 B 的最后 release 产生 = 1 | pause **2** / resume **2** / lock_acq 5；终态 **absent**、worker **running**。注意各 2 与冻结文本的"resume_calls=1"**不是同一口径**（该例是完整多周期）；**A.action 与"谁发的"未在 FACTS 记录**，须从 `report.*.json` 与 `worker.jsonl` 的 `ppid` 直读。 |
| N3 | `F-L8b-W2`：首参与者在 `after-pause-confirm` 硬退出（rc 91） | W2 阶段 resume=1；B 随后 `paused_by_us`；总 `pause_calls=2`；终态清空 | pause **2** / resume **1** / lock_acq 3；终态 **absent**、worker **running** ⇒ 与 `pause_calls=2` 吻合。**oracle 追加区 R1-5 明确记了一条与冻结文本的偏差**：B 实测是**开了自己的新周期**（`pause=2 resume=1`），**不是**接管（`takeover_resumed`），因为崩溃点落在确认之前还是之后取决于调度时序；R1-5 主张"绝不读成用户暂停 + 终态清空"仍成立。请 reviewer 判定这是否可接受。 |
| N4 | `F-L8c-W4`：最后参与者在 `after-release-persist-before-resume` 硬退出（rc 92） | B 接管：resume=1（补上），然后 B 自己 pause（总 2）；**必须有 1 次 resume 发生在 B 的 pause 之前**；`resume.required` 不得被静默丢弃 | pause **2** / resume **2** / lock_acq 4；终态 **absent**、worker **running**。**oracle 追加区 R1-5 补记**：崩溃后状态与冻结期望"完全一致"（`entries=[]`、`resume.required=True`、owner=已死 A）。**事件先后（resume 早于 pause）仍未在 FACTS 记录**，须从 `worker.jsonl` 的 `monotonic` 直读 —— 这是 N4 最关键的判据，FACTS 没有替它背书。 |
| N5 | `F-L8d-corrupt`：人工写入截断 JSON | enter 与 exit 都 `lease_state_corrupt`；pause=0/resume=0；**损坏文件字节不变**；不 unlink、不重建；rc=2 | **无调度器记录**；只有 pytest 断言，而 FACTS 未给逐例结果。**无证据**（oracle §6 第 7 项要求的前后 sha256 相同，本次无落盘证据）。 |
| N6 | `F-L8e-legacy`：人工写入旧格式 list | `lease_state_legacy`；零写零 CLI；字节不变 | **无调度器记录**，同上。**无证据。** |
| N7 | `F-L8f-element-corrupt`：`schema=2`、entry 缺 `lease_id` | `lease_state_corrupt`（条目级）；零写零 CLI；字节不变 | **无调度器记录**，同上。**无证据。** |
| N8 | `F-L8g-UNKNOWN`：活 pid + 空 `os_start_time` + 不同 boot_uuid | 判 **unknown** ⇒ `lease_conflict_unknown`；零写零 CLI；refcount 字节不变；rc=2 | pause **0** / resume **0** / lock_acq 1；终态 **ledger sha256 unchanged**、worker **running** ⇒ "零 CLI + 字节不变"有实测。**`error_code=lease_conflict_unknown` 与 rc=2、以及该 verdict 是走注入还是走真实 API 失败均未在 FACTS 记录**（见 §5(e)）。 |
| N9 | `F-L8h-WRITEFAIL`：`before-ledger-persisted:0` + refcount 路径预建为目录 | 致命 `lease_state_write_failed`；不得报"持有首租约"；pause=0；无孤儿 lease；rc=2 | pause **0** / resume **0** / **lock_acq 0**；终态 **refcount path still a directory**、worker **running** ⇒ "pause=0 + 从未成功写入"有实测。**`error_code` 与 rc=2 未在 FACTS 记录。** |
| N10 | `F-LK-TIMEOUT`：外部进程真持锁 + `--request-budget 0.2` | `lease_lock_timeout`（**不是**通用 `lock_timeout`）；零写零 CLI；两文件都不存在；等待受预算钳制（wall < 0.2 + 1.5 s 容差） | pause 0 / resume 0 / **lock_acq 0**；终态 **absent**、worker **running** ⇒ "零写、文件不存在、未取得锁"有实测。**`error_code`、rc=2、等待墙钟是否受钳制未在 FACTS 记录。**（`scratch/REPORT.md` §3 另记 "wall 0.20s under a 0.2s budget"，该数字不在 FACTS 内，本文件不据它下结论。） |
| N11 | `F-LK-TIMEOUT-ZERO`：同上但 `--request-budget 0` | 同上，且**根本不尝试加锁**：不产生 lock 文件、`lock_attempted=false` | pause 0 / resume 0 / **lock_acq 1**；终态 **absent**、worker **running**。**这是 §5 的攻击点**：`lock_acq=1` 与"根本不尝试加锁"表面冲突（`lock_acquisitions` 是成功获取计数，与 `lock_attempted` 不同口径，且预算为 0 时按 oracle §3.3 不应创建锁文件）。FACTS 没有记录该例的 `lock_attempted`、`error_code` 或锁文件是否存在 —— 必须从 `report.A.json` 与 `summary.json.final_lease.lock_exists` 直读判定。（`scratch/REPORT.md` §3 记为 "deadline_exhausted"，该值不在 FACTS 内，本文件不据它下结论。） |
| N12 | `F-LK-HOLDER-CRASH`：子进程持锁 2 s 后 `os._exit(90)` | 父进程 **≤0.5 s** 内取得锁，无需清理、无需删锁文件；锁文件事后仍在且 0 字节 | pause 0 / resume 0 / **lock_acq 0**；终态 **absent**、worker **running**。**"≤0.5 s 取得锁"与"锁文件存在且 0 字节"未在 FACTS 记录**；且 FACTS 表里该例 `lock_acq=0` 与"父进程取得锁"需要 reviewer 用 report 对齐口径。（`scratch/REPORT.md` §6 另记 "reacquire 0.000x s"、"holder rc=90"，同样不在 FACTS 内。） |
| N13 | `F-LK-NEVER-UNLINK`：P1 跑完后 | 锁文件仍存在（0 字节）且可再次加锁 | pause 2 / resume 2 / lock_acq 4；终态 **absent, lock file present 0 bytes**、worker **running** ⇒ "锁文件存在且 0 字节"有实测；"可再次加锁"由 lock_acq=4 间接支持。 |

**另有 2 条 frozen 判据在 FACTS 中无记录**：N4 的"resume 早于 pause"事件先后、N12 的"≤0.5 s"。oracle §6 的 10 项"交付前必须逐条复算"里，第 4 项（N1：B.action ≠ `respect_paused`）、第 6 项（N4 事件先后）、第 7 项（N5/N6/N7/N8 的 sha256 前后相同，其中 N5–N7 无证据）、第 9 项（N12 ≤0.5 s）、第 10 项（N13 可再加锁）在本 attempt **没有可直读的复算产物**。**本文件不声称 13 条负例全部为 green。**

---

## §5 待 reviewer 攻击的点

1. **(a) 三个顺序敏感断言 + harness debt 的说法本身要被打。** GREEN 的 rc 是 **1**（`18 passed, 3 failed`），不是 0。实现者主张 `test_f_l5_*`、`test_f_l6b_*`、`test_l8a_w1_*` 的失败源于"快照取在 gate 放行之后"，而不是协议缺陷。可falsify的检验：从 `after/i04d-green.txt` 找到三条失败的实际断言文本，再到 `evidence/run/I04D-CASE-F-L5`/`F-L6b`/`F-L8a-W1` 的 `report.*.json` 里找**同一字段**的取值——若同名字段在 report 里是期望值而只在 pytest 里错，则 harness debt 成立；若 report 里也错，则这是协议缺陷被调度器层"通过"掩盖。修法（把快照取进 gate handshake 内部）会改动 harness，属不属于本卡 allowlist，由 reviewer 裁定。
2. **(b) 调度器的 gate 握手能否静默掩盖协议 bug。** 例：某个参与者从未被放行（或放行前就退出），案例仍可能"通过"，因为 `pause_calls`/`resume_calls` 变少也符合"没有多暂停"的直觉。逐例可查项：`summary.json.participants.<tag>.elapsed_seconds` 与 `finished_monotonic` 是否都非空、`harness_error` 是否为空串、`report.<tag>.json.hold_released` 是否为 true；任何 `harness_error` 非空或参与者无 report 的案例都必须重跑，不能算 GREEN。**并请特别看 `F-L8b-W2`（resume 总数 1）与 `F-L8c-W4`（resume 总数 2）的事件先后**：总数正确不代表"接管 resume 发生在自己 pause 之前"。
3. **(c) ADR-9b 与 R5 的解读：活的外来持有者是被 join，而不是被拒。** 这一条**已被写进 oracle 的追加区 R1-4**（不再是"只在 review 里补充的解释"）：实现选择了 ADR-9b 的"加入"（§7 缺陷 5，由 F-L5 发现），但 R5 又允许"paused 且无可归因义务"作为 fail-closed 终态；两条在"存活的第三方 owner"这一格上重叠。R1-4 记录的理由是："拒绝"会让同一工具的两个**真实**参与者互相 fail closed；实现选择**加入**：只追加自己一条 lease、不动 owner 记录、不发 pause，一个周期仍只有一次 pause。请判定：(i) 这个理由是否足以覆盖一条冻结文本的重叠格；(ii) join 的适用边界是否只是"本工具世系"——`F-L5` 的实测（pause 1 / resume 1 / lock_acq 4、终态两文件不存在、worker running）只覆盖**同工具**两参与者共存的场景，**没有**覆盖"世系不同但存活"的第三方 owner 被 join 还是被拒；`F-L8d`（R5，resume **0**、owner 记录**逐字节不变**）覆盖的是**不可归因**的第三方 owner。中间那一格（外来但可归因、且存活）本 attempt **没有案例**。
4. **(d) R4 的 lineage 限制不在上游文本里 —— 这是本卡唯一改变可观察行为的解释。** §7 缺陷 4 记录：R4（可证死亡后接管）原实现没有世系校验，本卡加了 "same `boot_uuid` + same `pid`，或该记录是在本轮被 prune 掉的"。oracle 追加区 **R1-3** 把它写成显式期望，并自己声明这是"本卡唯一一处相对字面读法改变了可观察行为的解释"：据 R1-3，实施初版照字面实现后，**F-L8d 变成了一次 resume**（第三方 `pid=999999` 确实可证死亡 ⇒ 最后的释放者接管并 resume，那可能是**用户**的暂停）；加世系要求后 F-L8d 变成 resume=0、owner 记录写回后与改写值逐字节相同、`cleanup_status=failed:owner_evidence_changed:owner_probe:dead:foreign_lineage`。请判定这是"修复原文本的洞"（应接受并把 R1-3 视为期望的显式化）还是"超范围改设计"（应回 I-04-C 登记为 owner ruling）。**这是本次验收最实质的一个决定**，也是唯一一处"如果 reviewer 不同意，实现就必须改"的地方。
5. **(e) 探针三态设计与 `unknown` 在生产是否可达。** 接口是 `self | alive | dead | reused | unknown`（`_probe_entry_verdict`）。关键问题：`unknown` 在真实 Windows 生产路径上**是否可达**，还是被 `_process_exists`/`_process_start_time_raw` 的取值域排除了？如果 `unknown` 只在 `_probe_injection`（test-only `I04D_PROBE_INJECT`）下出现，则 N8 的"unknown ⇒ fail closed"只是一条**测试专用路径**，生产上等价于"永不触发"。可查：`_process_exists` 返回 `True/False/None` 的三态在 `OpenProcess` 权限失败（如受限进程）时的实际返回，以及 `F-L8g-UNKNOWN` 案例到底是走注入还是走真实 API 失败（`hook-probe.log` 与 `report.A.json.probe_last_verdict`）。**FACTS 只记了该例的 ledger sha256 未变与零 CLI，没有记 verdict 来源。**
6. **(f) journal 是否真的非权威（有没有任何 guard 读它）。** 主张是"`_lease_journal` 只 append、永不被读、永不影响判定（ADR-7）"。可查方式：在 `iso/filing-fetch/scripts/fetch_filing.py` 里对 `_lease_journal` / `_PAUSE_JOURNAL_NAME` / journal 路径做**全局引用搜索**，确认除写入点外没有读取点、没有 `if journal...` 型分支；再确认 `report/journal` 里的字段（`pause_action`、`lease_resume_reason` 等）来自内存 stats 而不是重新解析 journal。若存在任何"journal 缺行 ⇒ 判定变化"的路径，则"非权威"不成立。
7. **(g) `_is_our_owner` 的化身判定能否被 pid + boot_uuid 碰撞骗过。** 判定用 `boot_uuid` + `pid` + owner lease 仍存活（§7 缺陷 2 的修法）。攻击面：`boot_uuid` 的实现若只是"启动时刻派生的短串"（实测样本形如 `b60e06df5017`，12 个十六进制字符 = 48 bit），在 pid 复用 + 机器重启后碰撞的概率虽低但非零；更重要的是**同一台机器同一 pid 在同一 boot 内被复用**时，`boot_uuid + pid` 无法区分"我"与"前一个同 pid 进程"。请判定是否需要把 `os_start_time` 纳入 `_is_our_owner`（它目前只在 owner 记录与 R4 世系里被使用），以及 48 bit 是否够。
8. **(h) 变异证明（§6）根本没有跑。** 本卡**没有**任何变异证据：oracle.md §7 的 M1–M11 全部为 open。也就是说"每条断言真的能红"这一层**未经验证**——现有 GREEN 只能证明"实现没让这些断言红"，不能证明"断言在实现退化时会红"。请把 (h) 当作本卡最强的未满足项来裁定。
9. **(i) 缺失的 `decision.md`（本次交付时仍不存在）。** 全 attempt 递归搜索找不到该文件，但 `scratch/REPORT.md` §8 与 `oracle.md` R1-3/R1-4 都声称"已登记在 decision.md 第 2b/第 6 节"。后果：(a) R4 世系收紧与 ADR-9b 解读这两项**没有正式登记位**，只有 oracle 追加区里的说明；(b) carry 2（R5 手工释放指引）与 carry 6（I-04-E 必需字段清单）在文档层没有落点——虽然**代码**侧的 `_print_release_guidance()`（打印 refcount 路径、owner 路径、原始 ledger 文本与 4 步指引）与每例 `summary.json` 里的字段（`lease_lock_waits`/`lease_lock_acquisitions`/`lease_lock_max_wait_seconds`/`lease_ledger_writes`/`lease_resume_reason`/`lease_owner_transferred_to`/`cleanup_status`/`cleanup_elapsed_seconds`/`pause_action`/`liveness_calls`/`liveness_probe_failed`/相位墙钟）都在。请判定是必须补交（`changes_required`）还是在 closeout 记为文档缺口。注意 START_HERE 第 6 步与"必须交专业审查"清单都要求：**跨进程锁与崩溃恢复机制必须先写 `decision.md`**——本卡的机制改动（R4 世系）恰好落在这个清单里。
10. **(j) oracle 的 N 编号与调度器案例名不对应，且冻结文本内部有悬空引用。** (1) N1–N4 拆成 4 个独立案例、N5–N7 **没有**任何调度器案例、N9 的案例名是 `F-L8h-WRITEFAIL`（冻结写 `F-L8h-write-fail`）；(2) oracle §7 的 **M9 引用 N14（两进程同时持久化），而 N14 在冻结 §4 里并不存在**；(3) M4/M7/M11 点名 "P2/P1/N13" 而 P1/P2/P3 在冻结 §2 里是 F-L5/F-L6/F-L7 的编号，M2 却直接点名 "P3"、M4 点名 "P2" —— 这些引用当前**无法唯一解析到案例**。§4 与本文件的映射是**实现者的解析**，请 reviewer 裁定是否接受该映射，还是要求把 oracle §7 的引用改成明确的 `I04D-CASE-*` 名（这只应该是追加，不改冻结语义）。
11. **(k) 三个失败断言的具体节点名与复现口径。(a) 里说的三条失败断言，`-k` 复现时只能用 basetemp 目录名的前 30 字符**（`test_f_l5_two_processes_one_pa0`、`test_f_l6b_exactly_one_resume_0`、`test_l8a_w1_no_owner_marker_is0`）。请 reviewer 确认这三条与 `after/i04d-green.txt` 里失败的三条是同一批；若能从日志里读到**完整** nodeid（含 `[param]` 或类名），应以日志为准，并以日志里的完整 nodeid 作为"保留案例"登记。
12. **(l) `F-L9a` 的期望值改过口径。** oracle 追加区 **R1-1/R1-2** 记录：冻结 §2 P4b 写 `action = respect_paused`，实施中实测先出现 `worker_stopped`（"没有可暂停的东西可加入"守卫先行），补上 ADR-8 守卫 `_respect_user_pause_locked` 后回到 `respect_paused`，且实测 pause/resume 一度是 1/1（期望 0/0）。FACTS §4 记 `F-L9a` 终态为 pause 0 / resume 0 / lock_acq 1、ledger absent、marker absent、worker **paused (untouched)**。请确认 R1-2 的"实施缺陷已修"是真修（case 实测回到 0/0），而不是把期望改小。
13. **(m) `scratch/REPORT.md` 与 `oracle.md` R1 的"全绿"口径不能替代逐条证据。** `scratch/REPORT.md` §3 写 "Zero failed at the scheduler level"、并给出若干**不在 FACTS 内**的数字（N10 "wall 0.20s under a 0.2s budget"、N11 "deadline_exhausted"、N12 "reacquire 0.000x s"）。本文件**不引用**这些数字（它们没有落在本卡的可直读证据树上）。请 reviewer 要么从 `report.*.json` 与 `worker.jsonl` 里把它们复算出来，要么把它们记为未验证 —— 不要让摘要行充当证据。
14. **(n) case 根落在 attempt 目录之外。** `execution_runs/I-04-D/runs<pid>`（FACTS §7：Windows 路径长度所致）。这既影响 "changed_paths 全在 attempt 内" 的表述，也是清理边界问题；`recovery/README.md` §6 已写明归属与删除规则，请确认是否接受。
15. **(o) I-04-B 依赖是"iso 产物"而不是生产代码。** 基线用的是 I-04-B 的 **accepted_scoped iso 输出**（`execution_runs/I-04-B/…/iso/filing-fetch/scripts/fetch_filing.py`），因为生产仍是 `max(10.0, …)`（binding.json 的 ADR-6 依赖声明）。这意味着本卡验证的语义**与生产现状不同源**；请确认这条依赖链是否被正确登记，以及"孤儿 pause 可由人类手工解除"的指引在实际生产路径上是否仍然可用。
16. **(p) 摘要行与证据行的口径差。** `evidence/hashes.txt` 里 `oracle.md` 记的是 `e2b9029f…b690`（追加 R1 之前），盘上当前是 `e50380d6…b68b`（367 行）；`after/` 下同时存在 `lease-pytest-green/`（4:01）与 `lease-basetemp/`（4:47）两个 basetemp，而 GREEN 日志对应的是后者（见 `commands.json`）。请 reviewer 以日志与文件内容为准，不要把目录名当成运行时序。**本 attempt 的文档是多个 agent 并行写入的**（handoff.json / review.md / recovery/README.md 由实现者写；commands.json / changes.diff / oracle.md 追加区由其他 agent 写），措辞之间可能仍有未对齐处。

---

## §6 变异证明状态

**明确陈述：变异证明没有跑。** 本 attempt 不存在任何 M1–M11 的结果；`evidence/` 下没有变异日志，也没有 `scratch/mutants/` 目录。`commands.json` 的 `not_run` 区块与本条的记录一致（`I04D-09-mutation-proof`，`binding_status=unbound`）；`oracle.md` 追加区 **R1-6** 同样写明"未做，不主张任何结果"。任何人**不得**把 §4 的 GREEN 读成"断言已被证明会红"。以下 M1–M11 是**下一 attempt 的确切队列**（原文来自 oracle.md §7）：

| 变异 | 回退的判据 | oracle.md 期望重新变红的案例 |
|---|---|---|
| M1 `no-lock` | `lease_lock()` 改为不调用 OS 锁（同 RMW） | P1（`pause_calls` 变 2 或丢更新、`lease_set` 少一条） |
| M2 `by-pid-removal` | 删除条件改回 `entry["pid"] != os.getpid()` | P3 / `F-L7`（内层 exit 后 `lease_set` 空、`resume_calls` 提前变 1） |
| M3 `no-obligation` | release 段 A 不再写 `resume.required` | N4（B 读到空且无义务 ⇒ 不 resume ⇒ 终态仍 paused） |
| M4 `resume-on-empty` | release 段 B 的复查去掉"义务/所有权可归因" | P2 / `F-L6`（`resume_calls=2`） |
| M5 `owner-not-transferred` | 删掉 ADR-10e 的 owner 移交 | P1 / `F-L5`（B 走 R5 ⇒ 终态仍 paused、owner 指向已死的 A） |
| M6 `no-generation` | R5 的"可证死亡"去掉 incarnation（pid 活即认活） | N1 / `F-L8a-W1`（A 的 lease 不可回收 ⇒ 冲突/永久 paused） |
| M7 `unlink-lock-file` | release 结束时 unlink 锁文件 | N13 / `F-LK-NEVER-UNLINK`（锁文件不存在） |
| M8 `legacy-as-empty` | `_read_pause_state` 把旧 list / 损坏 JSON 当空 | N5/N6（会 resume/覆盖 ⇒ 字节被改） |
| M9 `unique-tmp-regression` | `.tmp` 名改回固定 `...refcount.tmp` | oracle.md 引用 **N14（两进程同时持久化）—— 该案例目前不存在，需先补** |
| M10 `user-pause-overridden` | T3/T4 去掉"本工具持有"判据 | P4b / `F-L9a`（pause/resume ≠ 0，或 refcount 文件被创建） |
| M11 `probe-unknown-as-dead` | unknown 判为 dead | N8 / `F-L8g-UNKNOWN`（不再 `lease_conflict_unknown`，而是回收并继续） |

**可运行配方（逐条相同，只在第 2 步的回退点不同）**：

1. 复制主副本到 scratch 副本：`robocopy <A>\iso\filing-fetch <A>\scratch\mutants\<Mn>\filing-fetch /E /XD __pycache__`（argv 风格；copy 与 robocopy 皆可，但**必须**在 `iso/` 之外）。
2. 在该副本里做**单点回退**（M1–M11 各一条判据，见上表的"回退的判据"列）——只改这一处，改完把副本的 `scripts/fetch_filing.py` sha256 记下来，作为该变异体的身份。
3. 用同一解释器跑**该变异点名的那一个案例**（argv 形状与主副本一致，cwd 与 `--out` 指向变异体目录）：
   `<A>\iso\venv\Scripts\python.exe -X utf8 <副本>\scripts\i04d_schedule.py run <case> --out <A>\scratch\mutants\<Mn>\run`
   若点名的案例是 pytest 案例（P1/P2/P3/P4b），则用：
   `<副本>\..\venv\Scripts\python.exe -X utf8 -B -m pytest tests/test_fetch_filing_lease.py -q -p no:cacheprovider --basetemp=<A>\scratch\mutants\<Mn>\basetemp -k <test-name>`
4. 记录：变异体 `fetch_filing.py` 的 sha256、该案例的 **raw rc**、以及"是否按期望变红"的字段级证据；全部写进 `scratch/mutants/<Mn>/`，并追加一行到下一 attempt 的 `evidence/mutation-<Mn>.txt`。
5. 收尾证明：重算 `<A>\iso\filing-fetch\scripts\fetch_filing.py` 的 sha256，必须仍为 `a72546c50401a4b1876288bea6b6d7e4a72db9c39fd028c7bfb75a6f929ad198`（证明变异没有污染主副本）。
6. 前置缺口：M9 需要先补出 N14（两进程同时持久化）案例；M3/M4/M5/M7/M8/M10/M11 在 oracle.md 里只给了"期望变红"，没有给出可运行 argv——接手者必须先补齐 argv 与期望 rc，或把这些条目记为 blocked，**不得**用"看起来会红"充当结果。

**本节不主张任何变异结果。**

---

## §7 实现者自查出的缺陷（10 项）

> 第 10 项（释放路径 R5 兜底格把**存活的第三方 owner** 当成可 resume）由决定文档作者读码
> 发现，见 `oracle.md` R1-9；其余 9 项由失败用例发现。

全部由**失败的案例**发现，不是靠阅读发现的。每项都已在 iso 副本内修掉（修法列见下）。

| 编号 | 症状 | 触发它的用例 | 修法 |
|---|---|---|---|
| 1 | `_lease_entry(state, state, ...)` 把 `_LeaseState` 传进了需要 `PausedWorkerScope` 的位置 → `AttributeError: '_LeaseState' object has no attribute 'lease_id'` | W4 takeover | 传入正确的 scope 对象 |
| 2 | `_is_our_owner` 比较 `owner.lease_id == 我的 lease_id`，同 pid 的**嵌套**被当成外来持有者拒掉 | `F-L7` | 改为世系身份（`boot_uuid` + `pid` + owner lease 仍存活） |
| 3 | `_probe_owner_death` 把 `owner_record_missing` 当作 UNSAFE 理由，使 release 路径把"记录缺失"读成"可以继续" | release 路径（R5） | R5 fail-closed |
| 4 | R4（可证死亡后接管）**没有世系校验**，外来记录只要指向一个死 pid 就能授权 resume | `F-L8d` | 要求 same `boot_uuid` + same `pid`，或该记录是在本轮被 prune 掉的 |
| 5 | dispatch 把外来的**活**持有者当冲突而不是加入，使同一工具的两个真实参与者互相 fail closed | `F-L5` | 改为 ADR-9b 的 join the live cycle |
| 6 | 缺少 ADR-8 用户暂停守卫（paused + 空 ledger）：采纳用户暂停、停掉已停的 worker，然后又把它 RESUME | `F-L9a` | `_respect_user_pause_locked` |
| 7 | hook gate 过滤器把每个配置的 gate 施加到每个参与者 | 构建案例时（harness 缺陷） | 按 tag 过滤（`I04D_HOOK_TAG`） |
| 8 | 探针把"无法回答"与"已死"混为一谈：`_windows_process_start_time` 对缺失 pid 与 API 失败都返回 `None` | 构建案例时（harness 缺陷） | 拆成 `_process_exists`(True/False/None) + `_process_start_time_raw`，无法回答一律 `unknown` |
| 9 | 探针用缓存句柄路径且不复查，对已退出的 pid 仍答 `alive` | `F-L8g-UNKNOWN` 相关诊断 | 每次判定都重新发起查询 |

（缺陷 7、8 是 harness 自身的缺陷，不是协议缺陷；FACTS §7 记它们为"构建案例时发现并修好的两个真实 harness 缺陷"。）

---

## §8 本卡不声称的资格

- **不授予生产实现资格**：`iso/` 是隔离副本；生产 `filing-fetch/scripts/fetch_filing.py` 仍是 `046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088`。company-wiki `catalog.sqlite3` 仍为 49,677,344,768 bytes、mtime `2026-09-19T06:31:35Z`、`-wal` 0 bytes。
- **不授予 mutation proof 资格**：本卡没跑（§6；`commands.json.not_run` 与 `oracle.md` R1-6 一致登记）。
- **不授予 POSIX（`fcntl.flock`）资格**：该分支实现了但从未被执行；SMB/NFS 锁语义同样未实测。
- **不授予真实 provider / 真实 company-wiki worker / 真实 catalog / 网络资格**：fake worker 只改一个 JSON 文件。
- **不授予"用户在我们 scope 中按下暂停会被保护"的资格**：`pause_origin` 缺失（carry 4，跨仓依赖，company-wiki `control.py` 无来源信号，只做只读检查）。
- **不授予 I-04-E 的任何结论**：本卡只登记它需要的字段名。
- **不授予 `decision.md` 所述内容与 `changes.diff` 的资格**：`decision.md` 在本 attempt 未产出（§5(i)），其对 R4/ADR-9b 的"正式登记"缺失；`changes.diff` 已产出（180917 bytes，added=4 removed=0 modified=1，只覆盖 iso/），但**未经 reviewer 复算**，其"仅 allowlist 内改动"的结论仍待直读确认。
- **不授予 13 条负例全部通过的资格**：§4 已逐条标注证据状态（6 条实测、4 条部分、3 条无原始记录）。
- **不授予生产路径语义同源资格**：iso 基线是 I-04-B 的 iso 产物，生产仍是 `max(10.0, …)`（binding.json ADR-6 依赖声明）。

---

## §9 判决栏（留空，**只允许 reviewer 填写**）

> 本栏由实现者保持为空。实现者不自签 `accepted`；`status` 维持 `review_pending`。
> 只有独立 reviewer（或 owner 指定的验收方）可以在此写入 `accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`，并列出本卡获得的资格与未获资格、保留案例与恢复规则。

```
verdict:                      (empty — reviewer only)
reviewer:                     (empty)
date:                         (empty)
scope_of_acceptance:          (empty)
still_required:               (empty)
reserved_cases:               (empty)
```

实现者未在本文件内主张任何通过结论；§3 的 RED→GREEN 是过程描述，§4 的"green"仅指 `evidence/run/` 里案例的运行结果，均不构成验收。
