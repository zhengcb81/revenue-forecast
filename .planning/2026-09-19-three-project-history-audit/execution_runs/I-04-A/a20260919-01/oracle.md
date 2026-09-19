# I-04-A oracle v2（运行前冻结；签署后不得为实现结果改写）

预期来源（v2 更正标注，F-BA2A-01）：
- F-D1 的 wait=1.0 / end=10.0 来自**卡片的独立数学预期 + decision.md v2 的 D3 修复规则
  （每次子调用返回后、退避 sleep 前重算剩余预算）**——它**不是**现行代码行为
  （现行 L304/L326 用调用前过期剩余 ⇒ wait=min(5,10)=5、t=14；`pure_probes.json`
  budget=10 / elapsed=14 即该缺陷的实证）。
- F-D2 / F-D3 同样是**修复后语义**的冻结；数字全部可手工复算
  （`design_measurements/math_oracle.json`，纯算术，未 import 被测代码）。

## 冻结的独立数学预期（卡片原文的展开）

- t0=0，deadline=10，首次子调用返回 t=9（catalog_busy）⇒ **返回后重算剩余 = 1**；
- 下一退避 = min(5, 1) = 1（jitter=0）；
- t ≥ 10 不可新发请求。

## F-D1 — 退避不得越界，截止后零子调用

| 项 | 冻结预期 |
|---|---|
| 注入 | 虚拟钟 0→9；identify 消耗 9 后抛 catalog_busy；deadline=10；jitter=0；backoff=5 |
| 退避消耗 | **恰 1.0**（返回后剩余 1；min(5,1)）；事件表 start=9.0 → end=10.0 |
| 退避后再调用数 | **0** |
| 请求结束时间 | **=10.0 ≤ 10**（终态 `upstream_error`） |
| 禁止 | 14.0 那种"9+5"越界（= 现行缺陷行为）；任何 >10 的请求侧结束点 |

## F-D2 — 截止后不得给请求阶段重新发预算

| 项 | 冻结预期 |
|---|---|
| 注入 | now=100，deadline=90（已超），本 scope 需要发 `worker-status`（请求阶段） |
| 请求阶段调用数 | **0** |
| 预算 | **不得出现 10.0 秒请求预算**（现 `_remaining()` 的 `max(10.0,…)`，L509-513，即缺陷本体） |
| 结果 | 请求以 deadline-exceeded 语义失败；"proceed-without-pause"兜底不得在截止后触发（它本身是请求侧动作） |

## F-D3 — 截止耗尽仍须恢复所有权（独立清理预算）

| 项 | 冻结预期 |
|---|---|
| 前置 | 本 scope 已登记（paused_by_us 或 joined 且为最后参与者）；请求在 deadline 耗尽处失败 |
| 清理 | `worker-resume` 仍**必须被尝试**，timeout **= C**（常数，v2 定义），独立标签 `cleanup:worker-resume`，与请求 deadline 无关 |
| 记账 | `cleanup_elapsed_seconds` 单列（模拟值 5.5 = resume_wait 5 + 0.5 子进程开销 ≤ C）；**不得**计入请求 elapsed |
| 失败 | `cleanup_status=failed:<reason>` + stderr 警告（含手动 resume 指引）；请求自己的退出码/业务结果不被清理失败改写 |

## 复审预注册变化案例（F-BA2A 复审给出；冻结规则逐数值复现 ✓）

deadline=30，t0=0，jitter=0，identify 连续三次 catalog_busy/超时：
call1 授予 30、返回 t=2 → 返回后剩余 28 → wait=min(5,28)=5 → 睡至 7；
call2 授予 23、返回 t=10 → 剩余 20、backoff 升 10 → wait=min(10,20)=10 → 睡至 20；
call3 授予 10、t=30 TimeoutExpired → **终态 upstream_error**（v2：TimeoutExpired 不重试）。
合计：子调用 3、退避消耗 15、请求结束 = 30.0 ≤ deadline、无第 4 次调用。

## v2 新增冻结项

- **TimeoutExpired = 终态**（不进重试集；模拟中走"剩余≤0 终态"同分支；机制归属见 decision.md D3）。
- **pid 探测（tasklist，现硬编码 20 s）**：请求段 `min(20, 当时请求剩余)`、清理段 `min(20, C)`；
  计 `liveness_calls`；探测失败记 `liveness_probe_failed`（保守视为存活的现行语义保留）。
- **C = max(30, 2×resume_wait + graceful)**（默认 30）；`_cleanup_timeout() = C` 恒定。
- **ε = 0.4 s（临时签署）**：仅适用请求/退避钳制路径与本机短 spawn 的 elapsed 验收；I-04-B/E
  使用真实进程 oracle 验收前必须按 decision.md D4 的**预先承诺程序**重测（真实 import 链 +
  并发负载 + kill/reap 延迟；n≥50/案、≥2 会话；2×max(p95)、上限 2 s）——该重签触发是预先承诺
  的测量程序本身，不是某次测试失败。
- **B = 20 s 只约束请求段**；清理段单列、按 C（±ε）验收。
- 真实进程侧：每子调用 timeout = 当时剩余（请求）或 = C（清理）；记录原始 monotonic 起止；
  新 stats 字段：`request_deadline` / `request_elapsed` / `cleanup_calls` /
  `cleanup_elapsed_seconds` / `cleanup_status` / `pause_action` / `liveness_calls` /
  `liveness_probe_failed`。

## 模拟资格声明

F-D1—D3 与复审变化案例全部可在**无服务环境**用虚拟 monotonic 钟模拟；真实 provider/worker
归 I-04-B/I-07，本卡不运行。
