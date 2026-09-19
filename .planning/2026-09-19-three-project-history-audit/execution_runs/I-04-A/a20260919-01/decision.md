# I-04-A 决议案 v2（修订版；处置独立复审 F-BA2A-01…08 后重签）

依据版本：`fetch_filing.py` sha256 `046cc7dc…`（filing-fetch `d35b6f5`，与卡片锚点和 I-00-B 绑定一致）。
本文件只做设计，不改任何产品代码/默认值。v1→v2 的每处变更由复审发现号标注（F-BA2A-xx）。

## D0. 现行缺陷清单（本设计要关掉的三件事）

1. **过期预算**：`_remaining() = max(10.0, min(deadline - now, 60))`（L509-513）在 deadline 已过时
   仍给请求/清理子调用发 10 秒 ⇒ F-D2。
2. **陈旧剩余**：retry 循环的 `remaining` 在子调用**之前**算（L304），except 分支里
   `wait = min(jittered, remaining)`（L326）用的是**过期值** ⇒ 子调用吃到 t=9 后 wait=min(5,10)=5、
   t=14 > deadline 10 —— 历史事故本体（`reviews/filing/tests/pure_probes.json`：budget=10,
   elapsed=14 实证）⇒ F-D1。父项 I-04 第 1 条原文即要求"**每次子调用返回后、退避 sleep 前重算剩余预算**"。
3. **清理与请求不分账**：worker-resume 的耗时混在请求 elapsed 里、清理失败被降级成裸 warning ⇒ F-D3。

## D1. 阶段预算表（动作 1；v2 增补 pid 探测行，F-BA2A-03）

一个请求只有一个 deadline：`resolve_filing` 入口 `deadline = time.monotonic() + timeout_seconds`
（L679；`--timeout-seconds` 默认 900，L1055）。**所有请求阶段共用它，任何阶段不得独立重置或获得新预算。**

| # | 阶段 | 代码锚点 | 预算来源 | 计入同一 deadline？ | 说明 |
|---|---|---|---|---|---|
| S1 | `identify` | L694-704 | retry 循环；子调用 `timeout=当时剩余`（L304/316，**按 D3-修复改为返回后重算**） | 是 | 每个请求必经 |
| S2a | `worker-status`（`__enter__`） | L520 | **改为 `_request_remaining()`（无下限；≤0 不得发起）** | 是 | 请求阶段；现 `max(10,…)` 即 F-D2 缺陷 |
| S2b | `worker-pause`（`__enter__`） | L541-546 | 同 S2a | 是 | 请求阶段 |
| S3 | `resolve` / `ensure` | L751-765 | 同 S1 | 是 | 主体动作 |
| S4 | `close-gap`（含自己的 PausedWorkerScope） | L990-1006 | 同 S1 | 是 | 仅 actionable gap + allow_download + authorization |
| R-P | **pid 存活探测**（`tasklist` 子进程，硬编码 timeout=20，L418-432；经 `_prune_pause_entries` L462 被 `_register` L534/566 与 `_unregister` L580 调用） | **v2 新增（F-BA2A-03）**：请求段（register）`timeout = min(20, 当时请求剩余)`；清理段（unregister）`timeout = min(20, C)` | 请求段计入 deadline；清理段计入 C | **不得再是"无预算来源"**：计入新计数器 `stats["liveness_calls"]`（不复用 `calls`），探测超时/异常按 L419-431"视为存活"处理但**必须记 `liveness_probe_failed`**。I-04-B 应优先改用无 spawn 的存活 API（OpenProcess）消除 20 s 尾巴——预算与记录规则无论如何都生效 |
| C1 | `__exit__` 的 `worker-resume`（**cleanup 义务 = action∈{paused_by_us, joined} 且 `_unregister()` 返回 True（我们是最后参与者）**；L593-596） | L595-610 | **`_cleanup_timeout() = C`（常数，v2 明确定义，F-BA2A-04）** | **否** | 所有权恢复 |
| C2 | `__enter__` pause 失败路径的 best-effort `worker-resume` | L550-558 | 同 C1 | **否** | 恢复所有权 |
| C3 | pause/owner 文件 unlink（本地，无子进程） | L584-585 | 无需预算 | 否 | 本地文件操作 |

**判定规则**：凡为"完成用户请求"而发起的 CLI 子调用（identify / worker-status / worker-pause /
resolve / ensure / close-gap）都是**请求阶段**；凡只为"恢复我们改变的外部状态"（worker-resume、
unlink）都是**清理阶段**；`tasklist` 存活探测按**其所服务阶段**归类（R-P 行）。同一 CLI 按用途归类，
不得因名字相同共享预算。

## D2. 清理预算 C（动作 2；v2 采纳公式，F-BA2A-08；修正 joined 措辞，F-BA2A-05）

- **C = max(30.0, 2 × worker_resume_wait_seconds + worker_graceful_timeout_seconds)**。
  默认输入（resume_wait=5、graceful=5）⇒ C = max(30, 15) = **30.0 s**；用户把 `--worker-resume-wait-seconds`
  调到 40 ⇒ C = 85。**公式的意义**：不为 CLI 已允许的输入冻结一个已知会被击穿的常数（那正是
  "签后再放宽"的温床）——O-2 据此**关闭**（不再移交给 I-04-B）。
- `_cleanup_timeout()` **恒等于 C**（无第二操作数；不对请求剩余取 min——清理与 deadline 无关，F-D3）。
- **何时可用**：仅 C1 / C2（且满足上面的 cleanup 义务判定）。deadline 是否已过**不影响** C 的可用性。
- **报告**：清理耗时**不得**计入请求 elapsed。新增独立字段：`cleanup_calls`、
  `cleanup_elapsed_seconds`、`cleanup_status`（`restored` / `failed:<reason>` / `not_needed`）。
  清理失败 = stderr 警告（保留手动 resume 指引，L606-608）+ 结构化字段；**不得改写请求自身的
  退出码/业务结果**。请求与清理 elapsed 分别报告（`request_elapsed` / `cleanup_elapsed_seconds`），
  禁止合并成一个 wall 数字。

## D3. 错误语义表（动作 3；v2 修 F-BA2A-01/02）

| 情形 | 语义 | 处置 |
|---|---|---|
| 请求子调用 **TimeoutExpired** | **终态**（v2 更正，F-BA2A-02）：现码映射 `upstream_error`（L226-231），不在重试集 `{catalog_locked, catalog_busy, db_timeout}`（L57），L321-322 立即原样重抛。**设计维持终态**，否决"改重试集"的替代（整请求级超时不应自动重试烧预算）。附带：L227-228 的注释写 "(retryable)" 与行为不符，I-04-B 顺手改注释（不改行为） | 直接失败该阶段；记录该次调用 |
| **退避等待（重试集三码）** | **v2 修复（F-BA2A-01）**：每次子调用**返回后**、计算 wait **之前**，`remaining = deadline - time.monotonic()` **重算**；`wait = min(jittered, remaining_fresh)`；睡醒后循环顶重查 `remaining<=0` ⇒ `upstream_error("overall deadline exceeded …")`。**这是对现行 L304/L326 行为的修正**（现行用调用前过期值 ⇒ wait=5、t=14，即历史事故；F-D1 的 wait=1.0 正是本规则的产物），不是"保持现行" | 退避常数 5→10→…→60、jitter ±20% 不变（L49-52） |
| 截止后到达的请求阶段（含 worker-status/pause） | **不得发起**；请求以 deadline-exceeded 失败 | 删除 `max(10.0,…)` 下限（F-D2）；不得借任何下限给请求重发预算 |
| 请求被取消 / KeyboardInterrupt | 原样向外传播 | `__exit__` 仍执行 C1（独立预算 C），不改写退出码 |
| worker 状态未知（worker-status 失败） | proceed-without-pause（L521-527） | 记 `pause_action=no_status`；**不产生清理义务**（未登记）；该判定消耗请求预算，截止后同样不得发起 |
| 清理子调用失败/超时 | `cleanup_status=failed:<reason>` + stderr 警告 | 请求结果不被改写 |
| **pid 探测超时/异常**（v2 新增） | 按 L419-431"视为存活"（保守） | 记 `liveness_probe_failed`；预算按 R-P 行 |

## D4. B / C / ε 冻结值（动作 4；v2 修 F-BA2A-06/07/08）

| 量 | 冻结值 | 依据与边界 |
|---|---|---|
| **C** | **max(30.0, 2×resume_wait + graceful)**（默认 ⇒ 30.0） | 见 D2；公式随用户输入缩放，杜绝签后放宽 |
| **ε** | **0.4 s（临时签署值，范围受限）** | 本机实测 `2×max(p95)`：启动 0.105 / sleep(0.25) 越界 0.202（n=30）。**适用范围（v2 明示，F-BA2A-06）**：仅请求/退避钳制路径与本机短 spawn 的 elapsed 验收比较。**重签前置条件**：I-04-B/E 使用真实进程 oracle 验收前，必须按预先承诺的程序重测 ε——(a) 真实 CLI import 链、(b) 一个刻意并发负载场景、(c) 含 TimeoutExpired kill/reap 延迟；n≥50/案、≥2 个时间上分离的会话；ε := 2×max(p95)，上限 2 s。重签触发是**本次预先承诺的测量程序**，不是"某次测试失败"；此后不得再放宽。复审独立复测 0.19（2.2× 摆动）恰证明单会话 n=30 不足 |
| **B** | **20 s，只约束每个真实时延案例的请求段**（v2 明示，F-BA2A-07）；清理段单列、按 C（±ε）验收 | 案例用受控真实 sleep（0.5–10 s）+ 结构化 elapsed 与原始 monotonic 时间戳双验收；不重演"模拟钟 9s+旧退避 5s=14"的不可归因数字 |

## D5. 两套 oracle（动作 5）

1. **模型时钟 oracle**（`design_measurements/math_oracle.json`，纯算术，**不 import fetch_filing**）：
   F-D1/F-D2/F-D3 原始 monotonic 时间戳表；断言已跑（ALL PASS）。**F-D1 的 wait=1.0 是 D3-修复
   规则（返回后重算剩余）的产物**——现行代码给 5.0/14.0，这正是要修的缺陷（复审 F-BA2A-01 确认）。
2. **真实进程 oracle**（I-04-B 实施）：每子调用 `timeout = 当时剩余`（请求阶段）或 `= C`（清理）；
   每案记录原始 `time.monotonic()` 起止；请求结束 ≤ deadline + ε（请求段）；清理 ≤ C + ε、独立
   action 标签（`cleanup:worker-resume`）；pid 探测按 R-P 行记 `liveness_calls`。
3. 信封/stats 新字段：`request_deadline`、`request_elapsed`、`cleanup_calls`、
   `cleanup_elapsed_seconds`、`cleanup_status`、`pause_action`、`liveness_calls`（v2 新增）、
   `liveness_probe_failed`（v2 新增）。

## Open questions

- O-1（保留，真裁决）：截止后 `worker-status` 被跳过 ⇒ 请求以 deadline-exceeded 失败、worker 保持
  running——**不设"纯状态查询豁免"**（豁免即重开洞）。I-04-B 如发现修复成本冲突，回本卡重议。
- ~~O-2~~ **已关闭（v2，F-BA2A-08）**：C 采纳随输入缩放的公式（见 D2），不再移交。
