# I-14-E oracle.md — Addendum B（**测量前置**：由父 agent 转达的 CF-I14F-X1 强制要求）

本 addendum 追加于 2026-09-21T21:5xZ，**在 M-B 的 node1-quiet 臂进行中**（该臂 18 次里已完成
12 次）。如实登记时序：以下三条不是事后解释，而是**接下来的运行与全部分析**的前置；其中第 1 条
依赖的工件对**已经跑完的运行同样保留在盘上**，因此对已完成部分是**回溯可核**的（scratch 未删）。

## B1. 判据升级：致因必须用**工件存在/缺失**判别，不能只用"超时时长"

CF-I14F-X1 的证据：I-14-F 在 mutation-disabled 的深层运行里 child 表现为 **15 s launcher
超时**，但存活工件显示那是**路径致因**——`…\source_catalog`(247 字符) 与 `cli.py`(254)、
`worker_launcher.lock`(256) **存在**，而 `worker_launcher_events.jsonl`(264) 与
`worker_stdout-*` 日志(299) **不存在**（>260 不可达）。⇒ 单看"15 s 超时"会把路径致因误判成负载致因。

**本卡的对应前置**：

1. 本 attempt 的每次运行都保留完整 basetemp；不论运行通过与失败，都由
   `harness/collect_artifacts.py` 逐运行归档并登记：
   - `fake-project/` 与 `fake-project/.source_catalog/` 的**实际路径长度**；
   - 每个工件的**存在/缺失**：`worker_launcher_events.jsonl`、`worker_launcher.lock`、
     `worker_control.json`、`fake_worker_count.txt`、`worker_runtime.json`、
     `worker_stdout-<session>-attempt-NNNN.log`、`worker_stderr-…log`；
   - 每个存在的工件的字节数与 sha256，小文件复制进 `after/artifacts-<band>/`。
2. **失败归因规则（先写死）**：
   - 若一次失败运行的 `worker_launcher_events.jsonl` 缺失或为空、而 `.source_catalog` 存在
     ⇒ 归类为**路径/重定向致因**（`artifact-absence`），**不得**算作负载致因；
   - 若事件文件存在且含 `child_unresponsive`（reason=`session_start_timeout`）且被杀 uptime > 0.5 s
     ⇒ 归类为**负载致因**（`startup-latency`）；
   - 若事件文件存在但缺失 `child_started`（只有 `starting`）⇒ 归类为**外部启动延迟**
     （`supervisor-start-latency`，节点②的主要形态）；
   - 混合出现时**分别计数**，不合并成一句"负载导致"。
3. 本 attempt 的节点①②运行**不使用** I-14-F 的短 basetemp 约定（那是它 iso 树里的 conftest），
   因此**不存在**"按设计 rmtree 重定位工件"的机制；scratch 一律保留（见 `recovery/README.md`）。

## B2. 并发活动必须记录（负载侧的直接证据）

I-14-F 观测到本机存在来自**其它会话**的并发 pytest 战役。本卡前置：

1. 条件运行期间由 `harness/concurrent_activity.py` 每 20 s 采样一次进程清单，写入
   `after/concurrent-activity.jsonl`：非本 attempt 的 `python/pytest/powershell/node` 进程的
   PID、父 PID、命令行、启动时间；以及 `chrome-headless-shell` 等已知重负载进程的 CPU 增量。
2. 每个条件自己的负载探针（`sleep20_overshoot_ms`、`cpu_loop_300k_ms`、每 pass 的
   `spawn_python_pass_ms`）与之一并进入 `after/analysis.json` 的 load 段落。
3. 若某条臂的并发活动显著高于另一条，**必须**在结论里写明，不得把并发差异算成臂间差异。

## B3. 卡片归属：本卡要回答"该带能否被确定性刻画"

I-14-F reviewer 的 R-2：在 I-14-F 最终常量下，167/166 处 child **0/3 clean**（全部落进本卡的带内）
⇒ 本卡是"该带是否可确定性刻画"的**唯一归属卡**。因此本卡在 `after/analysis.json` 与
`after/fail-able-cases.json` 中必须给出**明确的确定性判定**，三选一：

- `deterministic-threshold`：存在一个与负载无关的固定阈值可刻画；
- `distributional`：**不存在**固定阈值；可确定刻画的是"启动延迟分布"与"0.5 s 假设在其中所处
  分位"，而单次结果的边界宽度 ≈ 一个轮询间隔（100 ms）；
- `unresolved`：连分布都不稳定（则如实写"未定位到单一根因"）。

先验预期（oracle §2.3 从冻结带原始记录读出的机制）指向 `distributional`：判据是
"在 0.5 s 之后的某个轮询点仍存活"，而 36 个通过样本里存在 uptime 0.622 s 仍干净退出的反例
⇒ 单点阈值不存在。此预期**不**作为结论，结论由 `after/analysis.json` 的实测分布与逐运行工件给出。

## B4. 与已冻结内容的关系

- `oracle.md` §3 的假设 H1–H5、§5 的判定规则**未改**；本 addendum 只**加强** H3 的取证要求
  （工件判别）并新增 B3 的确定性判定项。
- 冻结带（I-14-C r5）的 48 行原始记录已由本 attempt 捞回并逐字节核对（
  `evidence/frozen_band_raw_record.json`），其中的失败实例**同样**经得起 B1 的工件判别：
  48/48 存在 `worker_launcher_events.jsonl`，且每次命中 `child_unresponsive`
  (reason=`session_start_timeout`)，`fake_worker_count.txt` 全部为 `2`
  ⇒ 冻结带的 12 次失败**全部**属于 `startup-latency`，不含路径致因。
