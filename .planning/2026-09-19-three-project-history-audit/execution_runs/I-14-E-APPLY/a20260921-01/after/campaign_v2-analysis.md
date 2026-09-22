# I-14-E-APPLY — campaign v2 结果分析（重跑卡，`status=review_pending`，实现者不自签）

- **卡 / attempt**：`I-14-E-APPLY` / `execution_runs/I-14-E-APPLY/a20260921-01`
- **授权**：`OWNER_DECISIONS.md` §16（第七批）原话「… **E-2: 重跑** …」；执行栏
  「E-2 = 重跑 | I-14-E-APPLY 重跑 | 与建议一致（**收缩为 4 臂 + 逐次落盘**）| 派 re-run 卡」
- **运行前冻结**：`oracle-addendum-C.md`（2026-09-22T07:31:56Z，**早于第一跑**
  `2026-09-22T07:55:53Z`；sha256 `6321ae1d110ab0ea8f2a6e917f9bde370f815a2c0c5dadf8a204a17663b564e5`）
- **战役窗口**：`2026-09-22T07:55:53Z` → `2026-09-22T08:19:57Z`（24 min；22 次运行墙钟合计 1096 s）
- **总量**：计划 22 / 落盘 22（14 passed, 7 failed, 1 timeout），逐跑期望命中 **19/22**
- **机器**：12 逻辑核；外部 `chrome-headless-shell` 负载全程在场（10 个进程），
  运行前实测 `LoadPercentage` 82–100 % ⇒ "quiet" 一律按 I-14-E addendum A1 的口径读作
  "**本卡不额外加负载**"，不是"机器空闲"。

---

## 1. 逐臂结果（期望 vs 实测）

| 臂 | SUT | 节点 | 条件 | N | 期望 | **实测** | 判定 |
|---|---|---|---|---|---|---|---|
| **A1-fixed-quiet** | iso/T0+T0b（sha `2719b835…`） | 节点① | quiet | 6 | 6/6 PASS | **6/6 PASS** | ✅ R2′=6/6 |
| **A2-fixed-cpu8** | iso/T0+T0b | 节点① | +8 忙循环 | 6 | 6/6 PASS | **6/6 PASS** | ✅ **R1′=6/6（本卡的目的）** |
| **A3-nonvacuity** | iso/T0+T0b | 反空转节点 | quiet 2 + cpu8 2 | 4 | 4/4 PASS（=挂死被抓住） | **quiet 2/2 PASS；cpu8 2/2 RED** | ⚠️ **见 §2：事件级 4/4 抓住；pytest 级 2 RED ⇒ §5 字面触发，交 reviewer 裁** |
| **A4-mutant05-cpu8** | iso/mutant-derivation-0.5（sha `76699401…`） | 节点① | +8 忙循环 | 6 | 6/6 RED | **5 RED + 1 guard-timeout；0 PASS** | ✅/⚠️ R4′：5/6 按期望 RED，1 次撞 180 s guard（按 guardrail 记为运行结果继续，未重试） |

**A2 逐跑（卡片全部意义所在——v1 时代该带在载荷下红）**：

| run | 树 | 结果 | 实测 t0（导出输入） | 实际 hang | starts / 被杀 | 被杀 uptime | 载荷% | 墙钟 |
|---|---|---|---|---|---|---|---|---|
| 1 | T0 | PASS | 1.895 s | **4** | 2 / 1 | 4.088 | 100 | 57.2 s |
| 2 | T0b | PASS | 1.009 s | **4** | 2 / 1 | 4.046 | 82 | 51.6 s |
| 3 | T0 | PASS | 0.951 s | **4** | 2 / 1 | 4.058 | 100 | 49.5 s |
| 4 | T0b | PASS | 1.175 s | **4** | 2 / 1 | 4.053 | 91 | 52.0 s |
| 5 | T0 | PASS | 1.154 s | **4** | 2 / 1 | 4.107 | 97 | 54.1 s |
| 6 | T0b | PASS | 0.881 s | **4** | 2 / 1 | 4.003 | 91 | 44.7 s |

- 每跑都走**测试内实测导出**（`max(2.0, 4·t0)` 再被 4.0 s 语义上限截断、向上取整）：
  t0 0.88–1.90 s ⇒ 4·t0 = 3.5–7.6 s ⇒ 实际施加 **4 s**（逐跑从该次运行自己的
  `worker_launcher_events.jsonl` 的 `worker_hang_timeout_seconds` 读出，不靠日志转述）。
- 产品语义保持：每跑 `child_started == 2`、恰好 1 次 `child_unresponsive`
  （reason `session_start_timeout`，uptime 4.00–4.11 s 落在 `[4−0.1, 4+1.0]` 窗内）、
  最终 rc=0 ⇒ **看门狗仍在杀，断言未放宽**。
- 对照：v1 的 B2（同为 fixed+cpu8）是 **15/16**（1 次测试自身 `timeout=15` 撞
  `subprocess.TimeoutExpired`，`after/bench-B2-fixed-cpu8.json`）；v2 A2 在更高外部负载下
  **6/6**。addendum C2/C7 预先登记过"若复现该形态即如实登记不足"——**本次未复现**。

**A4（突变体）逐跑**：hang 全程 **0.5 s**（突变生效）；starts/kills = 8/8、10/10、3/2、9/9、9/9、11/11
——退化回"重启风暴"，即 v1 时代红的形态；run6 直接以 `AssertionError`（节点①自身断言）红。
run1 撞 180 s guard（墙钟 190.97 s，pytest 被 guard 终止），按 guardrail **记为 `outcome=timeout`
并继续**，不重试不扩臂。⇒ **突变下 0/6 通过**，派生确实是 load-bearing。

## 2. 非空转（non-vacuity）证明 —— 挂死子进程在派生 timeout 下**被抓住**

反空转节点（oracle §5 形态）4 次全部给出同一组事件；判定三条（a/b/c）**逐跑核对**
（数据在 `after/campaign_v2.jsonl` 该臂 4 行的 `events` 段，可脱离本文件复核）：

| run | 条件 | pytest 结果 | (a) 看门狗开火 | reason | (b) 被杀 uptime vs 派生 4 s（窗 [3.9, 5.0]） | (c) `child_started` |
|---|---|---|---|---|---|---|
| 1 | quiet | **PASS** | 2 次 | 全 `session_start_timeout` | 4.097 / 4.042 ⇒ 2/2 在窗内 | **3** ✅ |
| 2 | quiet | **PASS** | 2 次 | 全 `session_start_timeout` | 4.029 / 4.088 ⇒ 2/2 在窗内 | **3** ✅ |
| 3 | **cpu8** | **RED**（`subprocess.TimeoutExpired`@节点自身 `timeout=15`） | 2 次 | 全 `session_start_timeout` | 4.109 / 4.038 ⇒ 2/2 在窗内 | **3** ✅ |
| 4 | **cpu8** | **RED**（同上） | 2 次 | 全 `session_start_timeout` | 4.028 / 4.016 ⇒ 2/2 在窗内 | **3** ✅ |

**读法（两种 RED 形态的区分，正是 addendum C7.2 要求出示的证据）**：

- **(a)(b)(c) 在 4/4 运行都成立** ⇒ 派生 timeout **没有空转**：挂死子进程在预算内被杀、
  重启到第 3 次启动，"一个派生得过大的 timeout 永不开火"这条失败模式**被数据否掉**。
- **2 次 cpu8 RED 的失败点不是断言**：测试在**自己的外层 `timeout=15` 预算**上抛
  `subprocess.TimeoutExpired`（节点①/反空转节点冻结的 `timeout=15` 不许改，oracle §2.3）。
  派生 4 s × 2 次看门狗击杀 + 每次启动的载荷下延迟 ≈ 正好压线 15 s，quiet 赶得上、+8 载荷赶不上。
- 但 **oracle.md §5 的字面规则是"若 B4/A3 出现任何 RED，本卡必须报 blocked，不得报
  review_pending 通过"**。⇒ 此处**不作自我豁免**：本报告把该触发**显式登记**，
  R3′ 只报 **"quiet 2/2 通过 + 事件级 4/4 抓住 + cpu8 2/2 外层预算 RED"**，
  **不宣称 R3′ 全绿**，交由 reviewer/owner 按 §5 字面与上述证据裁定。
  可选处置（**均未执行，须另行授权**）：(i) 提高该节点外层预算（属又一次测试侧时序修改，
  超出本卡冻结范围）；(ii) 以 quiet-only 判 R3；(iii) 判 blocked 并立后继卡。

## 3. 逐次落盘（persistence）证明

- `after/campaign_v2.jsonl`：**22 行 = 22 次运行**，0 撕裂行，466 021 字节，
  sha256 `8c227233a1a4e6c504eb704929242a20f53270cc230ac7c6a11baf6ea8677ee4`；
  每行含 arm / run / outcome / returncode / wall / guard / 时间戳 / basetemp 路径 /
  保留统计+逐文件清单 / events 摘要 / derivation / 负载探针 / `as_expected`。
- `after/campaign_v2-index.json`：**每次追加后原子重写**；当前 `recorded_total = 22`
  与 JSONL **一致（synced）**，`jsonl_lines_torn = 0`，sha256
  `f8969098ebe3a12aaca862d7e12dd6b72c13cc83656e393c7eb2a22b3d6ed0fb`。
- **可核的时间序**：`started_utc` 全程单调不减（07:55:53Z 起逐跑递进）——
  一行一跑、跑完即落盘的顺序可由每行时间戳独立复核；丢失上界 = 1 跑
  （顺序：运行 → 采集 → reap → 保留打包 → 追加(flush+fsync) → 重写索引）。
- **续跑语义已实现但本次未用到**（22/22 一次跑完，无重启、无重跑、无补跑）。

## 4. basetemp 工件保留证明（CF-I14F-X1）

| 检查项 | 结果 |
|---|---|
| 执行 basetemp 路径 | `%TEMP%\i14eapply-v2\<arm>-rNN\pytest`，**69–72 字符**；实际最长执行路径 **197–215 字符**（< I-14-F 的 240/241 起病点，<< 260）⇒ **无路径致因污染** |
| driver 是否删除 basetemp | **否**：v2 driver **没有任何 rmtree**；每次运行独立目录，pytest 只在该跑开始时清它自己的目录；`basetemp_executed_tree_deleted = false` ×22；`%TEMP%` 执行原件 22/22 仍在 |
| ZIP 保留件 | `after/campaign_v2-basetemps/<arm>-rNN.zip` **22/22 存在**，254 094 B；**每一跑 `zip_entries == files_total`（591/591 文件）**，归档错误 0 |
| 扁平可读副本 | `after/campaign_v2-artifacts/<arm>-rNN/` **22 个目录，591 个文件**（`<idx>.<basename>`，idx→rel 映射在 JSONL 清单里） |
| 逐文件清单 | 每跑 JSONL 行内 `artifacts.manifest[]`：rel、**执行绝对路径+字符数**、bytes、sha256 |
| **工件判别（B1 规则）** | `worker_launcher_events.jsonl`、`worker_stdout-*`、`worker_stderr-*` **22/22 全在** ⇒ **0 次 `artifact-absence`**，本战役**没有**任何一次失败可以归因于路径/重定向致因 |
| 逐跑 stdout / events / derivation 捕获 | `after/campaign_v2-captures/` 60 个文件 |
| **v1 遗产抢救** | `after/v1-basetemps/*.zip` **6 个**（B1/B2/B3/B5 + smoke + iso，共 129 个源文件 / 1.45 MB，0 错误）+ `v1-basetemp-manifest.json`（760 KB，逐文件 rel/path/chars/bytes/sha256）；**%TEMP% 原件未动** |
| **为什么是 ZIP+清单而不是树拷贝** | 运行前实测：attempt 内 `after/` 前缀已 134 字符 + 最深工件 suffix ≈131 ⇒ 树拷贝目标 **274–308 字符 > MAX_PATH(260)**，首次 PowerShell 树拷贝逐文件报 `Could not find a part of the path`（这本身就是 I-14-F 那族路径失败的活演示）⇒ 按 addendum C4 改为"清单 + 扁平副本 + ZIP"，并把该失败登记在册、清理我方半成品（**v1 原件一字节未动**） |
| 今日清理状态 | v1 的 `after/arm-logs/*`（含 **B4 = 0 字节**）与 `after/bench.log` **mtime 仍为 2026-09-21 23:07–23:38**，今日**未被打开写入**；v2 一律写 `campaign_v2.*` 新文件 |

## 5. 生产只读（`harness/final_hashes.py --verify` → `after/final_hashes.json`）

- **company-wiki（本卡 SUT 所在生产仓）：逐字节未变** —— HEAD 仍 `f39bd5a6…`、
  `status --porcelain` 仍恰为 3 条既有修改（`CLAUDE.md`、`README.md`、
  `src/company_wiki/source_catalog/artifact_dag.py`），`tests/contract` + `scripts` 扫描内容
  哈希未变；daily-news 亦未变。**本卡对生产仓零写入成立。**
- **诚实披露（verify 返回 2 的原因）**：扫描器同时盯 3 个仓，其中
  **revenue-forecast（本工作区仓）的 git 状态在冻结快照（09-21 22:48 之后）至今移动了**：
  HEAD `8431ba78 → 1d2288c0`、porcelain 157→99 行 —— 由**其它轮次的规划提交**造成
  （rounds 67–76，作者 zhengcb81，09-22 00:03–07:17，含 I-14-D 各轮），**与本卡无关**：
  本卡未执行任何 git 写操作，本卡的全部写入都在本 attempt 目录内。
  ⇒ 三仓级断言 `production_readonly_holds = false`，**卡级断言（生产 SUT 仓只读）成立**；
  该差异在此显式披露，不做任何粉饰。

## 6. v1 中断史（披露，未改写）

- `after/bench.log` 仍止于 `[23:38:02] ARM B4-nonvacuity-quiet START`，**无** `EXIT=` 行、
  **无** `ALL ARMS DONE`；`after/arm-logs/B5-clockmut-cpu8.log` 记
  `ARM B5-clockmut-cpu8 EXIT=3221225786` = 0xC000013A **`STATUS_CONTROL_C_EXIT`**；
  `after/arm-logs/B4-nonvacuity-quiet.log` = **0 字节**。
- v1 已完成且**原样保留**的结果：B1 16/16 绿、B2 15/16（1× `TimeoutExpired`）、
  B3 突变 16/16 红（`after/bench-B*.json` + `bench-captures-*`）。
- 本卡对这些文件**只读**；v2 全部落在 `campaign_v2.*` 新文件（连 `bench.log` 都不追加）。

## 7. 与冻结判据的逐条对账 + 剩余缺口

| 判据 | v1 冻结（oracle §3） | v2（addendum C2 缩减） | 实测 | 结论 |
|---|---|---|---|---|
| R1 载荷下不随机红 | 8/8 @ cpu8 | **R1′ 6/6 @ cpu8** | **6/6** | ✅（按缩减口径；**8/8 未被 v2 检验**） |
| R2 安静下不回归 | 8/8 quiet | **R2′ 6/6 quiet** | **6/6** | ✅（同上） |
| R3 反空转 | 抓住且节点行为可判 | **R3′ 4/4** | quiet 2/2 PASS；cpu8 2/2 RED（外层 15 s 预算），事件级 (a)(b)(c) **4/4 成立** | ⚠️ **§5 字面触发（任何 RED ⇒ blocked）**，交 reviewer；**不自签** |
| R4 突变证明 | ≥8/8 红中 ≥6 | **R4′ 6/6 RED** | **5 RED + 1 guard-timeout，0 PASS** | ✅ 实质成立（1 跑为 guard-timeout 而非 pytest-RED，如实登记） |

**剩余缺口（如实登记，不在本卡内处理）**：

1. **A3 cpu8 的 2 次 RED**：反空转节点在 +8 载荷下无法在其冻结的 `timeout=15` 外层预算内跑完
   （派生 4 s × 2 次击杀 + 载荷下启动延迟压线）；事件级已证非空转，但 §5 字面要求 reviewer 裁定
   blocked 与否，以及是否授权一次"提高该节点外层预算"的后继测试侧修改。
2. **A4 run1 的 guard-timeout**：180 s guard 内 pytest 未自行结束（starts=8/kills=8，明显在突变
   失败形态内），但形式上不是 pytest-RED；R4′ 报 5/6 RED + 1 timeout，不四舍五入成 6/6。
3. **6/6 ≠ 8/8**：R1/R2 的原判据在 v2 下**未被检验**（owner 裁定收缩的后果，addendum C1/C7.4 预先登记）。
4. **三仓级 `production_readonly_holds=false`** 系工作区仓被其它轮次提交所致（§5 已披露），
   生产 SUT 仓只读成立。
5. 本战役只覆盖**节点① + 反空转节点**；节点②（logon wrapper）与 B5（clock-mutant）**不在 v2 范围**
   （B5 由 R4′ 的突变臂替代，addendum C1 明示删除）。
6. 本机本时段结果**不升格为规范常量**（4·t0 的系数、4 s 上界仍是本机测量的产物）。

## 8. 产物索引

| 路径 | 内容 |
|---|---|
| `oracle-addendum-C.md` | v2 范围收缩的运行前冻结件（含 C4 的 MAX_PATH 实测与保留设计） |
| `after/campaign_v2.jsonl` | 22 行逐跑记录（append-only，flush+fsync） |
| `after/campaign_v2-index.json` | 每次追加后原子重写的索引（现 22/22 synced） |
| `after/campaign_v2-analysis.json` / `.md` | 机器可读 / 本文件的分析与逐条对账 |
| `after/campaign_v2.log` | v2 驱动日志（v1 `bench.log` 未被打开） |
| `after/campaign_v2-captures/` | 60 个逐跑 stdout / events / derivation 捕获 |
| `after/campaign_v2-artifacts/<run>/` | 22 目录 591 文件扁平副本 |
| `after/campaign_v2-basetemps/*.zip` | 22 个整树 ZIP（覆盖 591/591 文件） |
| `after/v1-basetemps/` | 6 个 v1 root ZIP + `v1-basetemp-manifest.json` |
| `after/final_hashes.json` | 生产只读 verify（company-wiki 成立；工作区仓差异见 §5） |
| `harness/run_campaign_v2.py` / `load_v2.py` / `analyze_campaign_v2.py` / `archive_v1_basetemps.py` | v2 驱动、自到期负载、分析、v1 抢救 |
| `handoff.json` | `status=review_pending`，含 `campaign_v2` 块；**实现者不自签** |
