# I-04-A 独立复审记录（两轮）

- reviewer：独立只读子代理 `e136877d-1b5f-4e71-841c-0491393a1117`（两轮同一会话；两轮均零写入，产物只在 %TEMP%）。
- 对象：本 attempt 的 decision.md / oracle.md / binding.json / commands.json / 两份设计测量。
- 结果：**第 1 轮 `changes_required`（1×P1 / 2×P2 / 5×P3）→ 作者修订 decision.md v2 + oracle.md v2 → 第 2 轮 `accepted_scoped`**（1 条 P3 措辞接缝随签携带，作为 I-04-B 冻结真实进程 oracle 时的强制口径条件）。
- 范围声明（复审原文）：仅接受设计文本；**不授予任何产品实施权**；I-04-B 开工前须重验 `fetch_filing.py` sha256 = `046cc7dc…088`。

## 第 1 轮发现与处置

| id | 严重度 | 发现（摘） | 处置（v2 位置） |
|---|---|---|---|
| F-BA2A-01 | P1 | 未落实父项第 1 条"每次子调用返回后、退避 sleep 前重算剩余"；现行 L304/L326 用过期剩余 ⇒ wait=5、t=14（pure_probes budget=10/elapsed=14 实证）；D3 却写"保持现行钳制"；oracle.md 推导来源标注错误 | decision.md 新增 D0-2 机制陈述；D3 行 2 明确"返回后、wait 前重算 remaining_fresh"并标注**是对现行行为的修正**；oracle.md 头部更正 F-D1 来源 |
| F-BA2A-02 | P2 | TimeoutExpired 被误标 retryable：现码映射 upstream_error（L226-231）、不在重试集（L57）、L321-322 立即重抛；"remaining>0 才重试"恒假 | D3 行 1 改**终态**；否决改重试集（整请求级超时不应自动重试）；L227-228 注释不符移交 I-04-B 只改注释；复审变化案例覆盖该分支 |
| F-BA2A-03 | P2 | 阶段表漏 `_pid_is_alive` tasklist 探测（硬编码 20 s，L418-432；经 L462←L534/566/580 横跨请求/清理段），不受 deadline 约束、不计 stats | D1 增 R-P 行：请求段 `min(20,当时请求剩余)`、清理段 `min(20,C)`；新计数 `liveness_calls`；失败记 `liveness_probe_failed`；建议 I-04-B 改无 spawn API |
| F-BA2A-04 | P3 | `_cleanup_timeout()` 的 min 第二操作数未定义 | D2：`_cleanup_timeout() = C`（常数，不与请求剩余取 min） |
| F-BA2A-05 | P3 | "joined 时不负责 resume"不准确（L593 纳入 joined；L595-596 仅在仍有其他参与者时早退） | C1 行与 F-D3 前置改为"action∈{paused_by_us, joined} 且 `_unregister()`=True（最后参与者）" |
| F-BA2A-06 | P3 | ε 方法论薄弱（n=30 单会话；复审 15 分钟后复测 0.19 vs 0.40；未测真实 import 链/负载/kill-reap；2× 无论证） | ε=0.4 改**临时签署**+范围限定；I-04-B/E 验收前按**预先承诺程序**重测（真实 import 链+并发负载+kill/reap；n≥50/案、≥2 会话；2×max(p95) 上限 2 s）——触发是程序本身，不是测试失败 |
| F-BA2A-07 | P3 | B=20 未定义是否含清理（含则与 C=30 矛盾） | B 只约束请求段；清理单列按 C |
| F-BA2A-08 | P3 | C=30 对 CLI 已允许输入不充分（resume_wait 可为任意 float）；O-2 后移=签后放宽温床 | 采纳公式 **C = max(30, 2×resume_wait + graceful)**（默认 30；40/5 ⇒ 85）；O-2 关闭 |

## 第 2 轮（重签）

- 逐条核对 01…08 全部真实处置、无 P1/P2 级新矛盾；修订完整性核过（仅 decision.md/oracle.md 变更，其余文件字节未动；FF 树未动；allowlist 干净）。
- 预注册变化案例被 v2 冻结规则逐数值复现（deadline=30 三连争用：授予 30/23/10、wait 5/10、t=30 TimeoutExpired 终态、3 次调用、退避消耗 15、end=30 ≤ deadline）。
- **随签携带的强制口径（归 I-04-B）**：`F-BA2A-R2-residual | P3` —— 清理段验收必须按**子调用**（resume ≤ C+ε；每个 pid 探测各 ≤ min(20,·)），相位总墙钟单列报告、不设验收上限（否则过期 pid 场景会判假 RED）；D4 B 行与 D5.2 的措辞以本条为准统一。

## 复审通过项（severity none，摘要）

锚点 sha256/48392 字节/HEAD `d35b6f5` 一致；全部行号锚点属实；F-D2 机制主张正确（`max(10,min(-10,60))=10`，pure_probes `worker_remaining_after_deadline=10.0` 实证）；数学 oracle 三案例手算复现、脚本不 import 被测码；D2/D3 其余语义行与代码一致；范围无遗漏（父项 1→A+B、2→C+D、3-5→E）；allowlist 干净；O-1 是真裁决。

## not_verified（复审声明，照录）

I-00-A 基线收据内容；RF 22:10 批量 mtime 是否使 I-00-B 的 RF hash 过期（建议下游 RF 卡重验）；负载/真实链路/kill 延迟的 ε 补测（超出只读 brief，已转为 I-04-B 前置条件）；`FilingFetchError.attempts` 默认值。
