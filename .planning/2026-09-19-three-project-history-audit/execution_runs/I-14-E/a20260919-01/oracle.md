# I-14-E oracle.md — 重启节点的时序抖动（负载相关，非树差异）

attempt：`execution_runs/I-14-E/a20260919-01`。**冻结时刻：2026-09-21T20:09:21Z（UTC）**，
先于本 attempt 的任何一次测量运行（`evidence/freeze_instant.json`）。

本卡是**测量卡**：只识别、不定性、不改产品、不改产品测试的时序假设。
`status=review_pending`，实现者不自签。

---

## 1. SUT 身份与绑定

| 项 | 值 |
|---|---|
| 产品测试（真正的 SUT） | `CW/tests/contract/test_source_catalog_worker_bootstrap.py`，sha256 `32515aa6…c005c1`（= I-14-C binding、I-14-F handoff 同值） |
| 节点① `child_without_runtime` | `test_child_without_runtime_session_is_terminated_and_restarted`（该文件 893–917 行） |
| 节点② `logon_wrapper_quoted` | `test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths`（1039–1119 行） |
| 真实启动器 | `CW/scripts/source_catalog_worker.ps1` sha256 `5c12cd74…bc311`（= 冻结带事件里 `launcher_source_hashes.supervisor_ps1`） |
| 登录包装器 | `CW/scripts/source_catalog_worker_at_logon.ps1` sha256 `70b4d7d7…be5a1c`（= 冻结带 `logon_ps1`） |
| CW HEAD | `f39bd5a64224cd0c7aa098f23f64bf3811fa8939`（branch fcap，与 I-14-C/I-14-F 同） |
| 运行解释器 | `iso/venv/Scripts/python.exe`（3.13.9；= I-14-F venv 的字节副本，包集合与 I-14-C 运行器 venv 完全相同） |
| 两棵树 | `iso/T0/src`（= I-14-C `iso/product/src`，manifest `dca36d3b…`）；`iso/T4/src`（= I-14-C `iso/product_fixed/src`，manifest `808a0dfa…`）；`iso/T0b/src` = T0 的**字节相同**第二副本（身份对照） |
| T0 vs T4 差异 | 仅 `company_wiki/source_catalog/{cli.py,observability.py,worker.py}`（I-14-C 的脱敏修复） |
| 事实来源 | `evidence/binding_hashes.json`（逐文件清单 + 相等性证明 + 锚点 hash） |

**运行前就记录的结构性前提（可证伪，见 §4 H2）**：两个节点的结果**在构造上**不可能依赖树变体——
节点①的测试体不 import 任何 `company_wiki.*`；被启动的子进程是测试自己写进 tmp 项目的假
`cli.py`（由 cwd 解析），启动器是两棵树共用的同一个 `.ps1`；节点②只用
`company_wiki.source_catalog.control` 的 `process_identity/terminate_matching_process`，而
`control.py` 在 T0/T4 中**逐字节相同**。`sys.executable`（子解释器）两棵树相同。

环境：12 逻辑核 / 15.8 GB；机器与他人会话共享，因此每次运行都记录负载探针（§5），
并如实报告环境混淆，而非把环境噪声记成树差异。

---

## 2. 冻结观测带（原始记录，expected 由该记录**手算**）

### 2.1 原始记录的来源与完整性

- 冻结带 = I-14-C r5 `r5/flake-evidence/frequency-child_without_runtime.json`
  （sha256 `68d4e63e64744f099504ee4fa02cb299caa9c404978275ea8f884fbb92763e42`）：节点①，
  12 次 × 2 轮 × 2 树 = 48 行，**交错**执行（每轮内 T0/T4 交替），短 `%TEMP%` basetemp。
- 该脚本当时只把 stdout 写回 attempt；**每次运行的 `worker_launcher_events.jsonl` 仍留在 scratch**
  `%TEMP%/i14c-flake-freq`。本 attempt 只读地把它捞回：
  `evidence/frozen_band_raw_record.json`（`harness/extract_frozen_band.py`）。
- 完整性核对：**48/48** 次运行的 scratch `stdout.txt` 与冻结 capture **逐字节相同**
  （sha256 相等，非"内容相似"）；**48/48** 存在 launcher 事件文件。⇒ 这份原始记录就是冻结带本身的
  产物，**不是重跑**。
- 缺口（如实登记）：I-14-C 的 48 行原始记录**没有负载快照**；这正是本卡要补的一列。

### 2.2 手算表（由 2.1 的原始记录直接数出来；不调用任何被测函数、不重跑）

| 轮/树 | 运行数 | 失败（`child_started != 2`） | child_started 直方图 |
|---|---|---|---|
| pass1 / T0 | 12 | **3** | 2×9, 3×3 |
| pass1 / T4 | 12 | **2** | 2×10, 3×2 |
| pass2 / T0 | 12 | **3** | 2×9, 3×3 |
| pass2 / T4 | 12 | **4** | 2×8, 3×2, 4×2 |
| 合计 | 48 | **12** | 2×36, 3×10, 4×2 |

- 每树 24 次：T0 **6/24**、T4 **6/24** ⇒ 与卡片正文"6/24"一致。
- **关键事实（手算）**：pass1 失败更多的是 **T0**（3 > 2），pass2 失败更多的是 **T4**（4 > 3）
  ⇒ "失败更多的那棵树"在两轮之间**翻转**。
- 全部 12 次失败都是**同一条断言**：`assert len([... "child_started"]) == 2`
  （12 次中 10 次得 3、2 次得 4）；冻结带内**没有**超时、没有 `launcher_exception`、
  没有其他失败形态。
- 失败实例中"第 2 次 child 被看门狗杀掉时的 uptime"：n=12，min **0.507**，median **0.537**，
  max **0.588** s。
- 通过实例中"最后一次 child 自行退出的 uptime"（= 立即退出型假子进程的真实寿命）：n=36，
  min 0.113，median 0.2245，**max 0.622** s。

### 2.3 机制（从原始事件时间线读出，不是推测）

失败例 `p2-T4-child_without_runtime-1`（12 事件）：

| t+ | 事件 | 关键字段 |
|---|---|---|
| 0.000 | `starting` | hang_timeout=0.5, poll=100ms |
| 0.101 | `child_started` | attempt=1（行为①：sleep 5，不写 runtime） |
| 0.650 | `child_unresponsive` | attempt=1, uptime=0.566, reason=`session_start_timeout` |
| 0.673 | `restarting` | attempt=1, rc=-1, delay=0 |
| 0.682 | `child_started` | attempt=2（行为②：**立即 exit 0**） |
| 1.221 | `child_unresponsive` | attempt=2, **uptime=0.515** ⇒ 被误判为"没有 runtime 会话" |
| 1.230 | `restarting` | attempt=2, rc=-1 |
| 1.250 | `child_started` | attempt=3 |
| 1.766 | `child_unresponsive` | attempt=3, uptime=0.520 |
| 1.777 | `restarting` | attempt=3 |
| 1.805 | `child_started` | attempt=4 |
| 1.933 | `exited` | attempt=4, uptime=0.132, rc=0, reason=`clean_exit` ⇒ 测试看到 4 次 start |

对照：通过例 `p2-T0-child_without_runtime-2`（6 事件）里 attempt=2 **uptime=0.603 也通过**
（`WaitForExit` 先返回，循环不再做 uptime 检查）；`p1-T0-child_without_runtime-3` 的
attempt=2 在 **0.435 s** 自行退出。⇒ 判据不是干净的"0.5 s 阈值"，而是
**"轮询边界的对齐"**：`source_catalog_worker.ps1:351-373` 先 `WaitForExit(poll)`，
返回 false 才检查 uptime；于是"在 0.5 s 之后的某个轮询点仍存活"才会被杀，
而刚好在两次检查之间退出的子进程即使超过 0.5 s 也算干净退出。模糊窗宽度 ≈ 一个轮询间隔
（100 ms，受压时会拉长）。

---

## 3. 本卡要检验的假设（运行前冻结，含证伪条件）

- **H1（负载相关）**：节点①的失败率随机器负载上升。
  - 判据：在**人为负载**条件下（§5 的 `cpu` 条件）48 次运行的失败率 > 安静条件下的失败率。
  - 证伪：负载条件下失败率 ≤ 安静条件（或两者都为 0）。
- **H2（非树差异）**：抖动与"哪棵树"无关。
  - 判据 A（结构）：§1 的前提成立，且实测中失败形态**只**由 `child_started` 计数决定。
  - 判据 B（身份对照）：`T0` 与 `T0b`（字节相同）在同一负载条件下的失败率差
    ≤ 二项抽样噪声（本判据把"位置/顺序效应"也算进去，若 T0 与 T0b 出现系统性差异，
    则必须表述为**位置/环境效应**，绝不能读成树差异）。
  - 证伪：两棵**字节相同**的树在交错运行下出现稳定的、方向一致的大幅差异
    （此时"树身份"不足以解释，但"顺序/位置"仍是更可能的解释——须如实记录，不得改口成树差异）。
- **H3（机制归因）**：失败的直接原因是"**立即退出型假子进程的启动寿命跨过 0.5 s 轮询边界**"，
  而不是另一个资源（锁、句柄、CPU 饥饿、超时）。
  - 判据：每一次失败运行都必须同时满足 (a) 存在 ≥2 条 `child_unresponsive`，reason 全为
    `session_start_timeout`；(b) 第 2 次（及第 3 次）被杀的 uptime 落在 **(0.5, 0.7] s**
    ——即刚好越过看门狗而非"子进程根本没起来"；(c) 最后一次 attempt 以 rc=0 干净退出。
  - 证伪：出现 `launcher_exception` / 超时 / 非零退出 / uptime ≫ 0.7 s 的失败形态。
- **H4（窗口可测）**：独立测量（不经 pytest、不经看门狗）得到的"立即退出型假子进程寿命"
  分布，其**安静条件下的上尾**应能解释冻结带的 25% 失败率量级；负载条件下分布整体右移。
  - 判据：安静条件 n≥40 的样本里出现 ≥0.5 s 的样本（冻结带 36 个通过样本的 max=0.622 已经
    暗示上尾确实穿过 0.5 s）；负载条件下 median 或 p90 显著大于安静条件。
  - 证伪：安静条件分布**完全**落在 0.5 s 以下（上限远低于 0.5 s），此时冻结带的 25% 必须另找原因，
    本卡不得硬套 H3。
- **H5（节点②）**：`logon_wrapper_quoted` 的时序假设是另一族（PowerShell 包装器 15 s 硬超时、
  15 s 事件等待、20 s 监督者退出等待、假子进程 sleep 10 s）。判据：在负载条件下测出
  包装器时长/事件等待余量的分布；若实测余量充足则不宣称它有抖动带（**不得**为了对称而虚构）。

**诚实条款**：若抖动窗口无法被判据确定地刻画（例如失败边界落在与环境无关的随机区间），
本卡如实写"未定位到单一根因/边界不可确定"，不强行给出结论（卡片第 5 条）。

---

## 4. 测量计划（冻结；运行 count 与负载等级在运行前写定）

**M-A（独立带宽，不经 pytest/看门狗）** `harness/measure_child_lifetime.py`
- 用产品测试**自己的** `_prepare_fake_launcher_project` 造样例（只读 import），行为表
  `[{sleep 5},{exit 0}]`，先做一次不计量的"第 1 次启动"（0.5 s 后杀掉，模拟看门狗），
  再计量第 2 次启动的 **launch→exit** 时长；子进程 argv/环境/cwd 与启动器一致。
- 两种方法：`popen`（不含 Start-Process 开销）与 `startproc`（PowerShell `Start-Process`，
  含启动器自己付的开销，见 `harness/child_uptime_probe.ps1`）。
- 负载等级：`quiet`（无外加负载）、`cpu8`（8 个忙循环进程）、`cpu12`（12 个）。
- 样本数：`popen` 每等级 40；`startproc` 在 quiet/cpu8 各 12。

**M-B（节点级结果带）** `harness/run_band.py`
- 与冻结带同形：同一 suite 路径、同一 stripped env、逐轮**交错**树、每次运行**新建空**
  basetemp（short `%TEMP%/i14e-*`）、`-p no:cacheprovider`、`-B`。
- 节点①：`quiet` 与 `cpu8` 各 12 次 × 2 轮 × 3 树（T0/T4/T0b）= 72 次/条件；
  另加 `spawn` 条件（8 忙循环 + 持续拉起短命 python 进程，模拟"并发 pytest 战役"这一
  已登记混淆）12 次 × 1 轮 × 3 树 = 36 次。
- 节点②：`quiet` 与 `cpu8` 各 6 次 × 2 轮 × 2 树（T0/T4）= 24 次/条件；
  `spawn` 6 次 × 1 轮 × 2 树 = 12 次。
- 每次运行记录：rc / verdict / 断言原文、节点墙钟、该次运行自己的 launcher 事件时间线
  （状态序列、attempt、被杀 uptime、干净退出 uptime）、以及两个廉价负载探针
  （`sleep(20ms)` 超调、固定 30 万次循环耗时）——用来把"负载"变成可比的数量而不是形容词。
- 负载由 `harness/load.py` 生成并在条件结束时回收。

**不做什么**（写进 oracle，避免事后辩解）：
1. 不改产品测试的任何时序假设（`-WorkerHangTimeoutSeconds 0.5`、`timeout=15` 等一律原样）；
2. 不改任何产品源码/配置/启动器；
3. 不用测量运行去**生成** expected：§2 的 expected 全部来自原始记录；
4. 不把 `~25%` 升格为规范常量（卡片第 6 条）；它只是本机本时段的观测值。

---

## 5. 判定规则（先把话说死，再看数据）

| 假设 | 判定 |
|---|---|
| H1 | `cpu8` 条件节点①失败率 与 `quiet` 条件比较；报告点估计与二项 95% 区间，不做"显著/不显著"的口号式结论 |
| H2 | T0/T4/T0b 三者的失败率（同条件）+ T0 vs T0b 的差；另附 §1 的结构性论证 |
| H3 | 对**每一次**失败运行逐条核对 (a)(b)(c)；只要有一次失败形态不符，就如实登记为"存在第二种机制" |
| H4 | M-A 的分布统计（min/p25/median/p75/p90/p95/p99/max、≥0.50/0.55/0.60 计数）分条件对比 |
| H5 | 节点②按 15 s/15 s/20 s 三条等待的实测余量报告；余量充足则明确写"未观测到抖动带" |

**退出判据与本卡的关系（不得含糊）**：卡片退出判据是"测试在负载波动下不再随机红/绿，且无需改动
产品代码"。本 attempt 交付的是**识别 + 可失败用例 + 未施加的测试侧修改建议**；退出判据本身
**未自签**——它需要 reviewer 判定，且因"生产仓只读"的边界，测试侧改动**不在本 attempt 的允许范围**。
本卡**不**声称已消除抖动。

---

## 6. 预期产物

| 路径 | 内容 |
|---|---|
| `evidence/frozen_band_raw_record.json` | 冻结带 48 次运行的原始事件级记录（含完整性核对） |
| `evidence/binding_hashes.json` | 树/锚点/解释器 hash 与相等性证明 |
| `after/band-*.json` + `after/band-captures/` | M-B 每次运行的 stdout 与 launcher 事件 |
| `after/child-lifetime-*.json` | M-A 的原始样本 |
| `after/analysis.json` + `after/analysis.md` | 逐假设判定、机制归因、测得窗口 |
| `after/fail-able-cases.json` | 两种重启节点各自的**可失败用例**（当前条件下确实失败的复现） |
| `after/proposed-test-side-change.md` | **未施加**的测试侧修改建议（以实测带宽为据） |
| `handoff.json` / `review.md` | status=review_pending；reviewer 独立判定 |
