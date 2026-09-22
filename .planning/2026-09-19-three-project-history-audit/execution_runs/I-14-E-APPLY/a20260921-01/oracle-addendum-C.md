# I-14-E-APPLY oracle.md — Addendum C（campaign v2：**范围收缩为 4 臂 + 逐次落盘**，运行前冻结）

**记录时刻：2026-09-22T07:31:56Z（UTC）／本地 2026-09-22 08:31:56**，写于本 addendum 之后**任何一次**
v2 pytest 运行之前（`after/campaign_v2.jsonl` 的第一行时间戳晚于本文件的 mtime，可核）。

**编号说明**：本文件是 I-14-E-APPLY attempt 的第一份 addendum；字母 **C** 延续其来源卡
`execution_runs/I-14-E/a20260919-01/oracle-addendum-A.md` / `-B.md` 的编号——A/B 已按父指示在
本卡开跑前通读（A = 运行 count 收缩的先例；B = CF-I14F-X1 的工件判别前置），本文件与它们同属
一条 oracle 血统。A/B 原件不在本 attempt 内，不移动、不复制、不改写。

---

## C0. 授权与触发（先于一切运行登记）

- **Owner 裁定（`OWNER_DECISIONS.md` §16「已裁定·第七批」原话逐字）**：
  「A-1: b（允许修 prune 代码，不授权执行 prune） A-2: 批准 B: a（提高门超时到 1200，立卡红绿）
   C: 先推已收口的 4 张，B1/B3/I-14-D 攒第二批 D-G1: a D-G2: 留置/（或给取舍） E-1: 150/60
   **E-2: 重跑** E-3: 立卡 E-4: 维持暂不签」
  §16 执行栏对 E-2 的记载：「**E-2 = 重跑** | I-14-E-APPLY 重跑 | 与建议一致（**收缩为 4 臂 + 逐次落盘**）|
  派 re-run 卡」。⇒ 本文件即那张 re-run 卡的运行前冻结件。
- **触发事实（v1 战役的死因，如实登记）**：`oracle.md` §4 冻结的 6 臂战役（B1–B5 + B4，
  约 76 次运行，逐臂批量落盘）在一次外部终止下整体丢失进度：
  - `after/bench.log` 止于 `[23:38:02] ARM B4-nonvacuity-quiet START`，**没有**对应的
    `EXIT=` 行，也没有 `ALL ARMS DONE`；
  - `after/arm-logs/B4-nonvacuity-quiet.log` 为 **0 字节**（臂启动即被终止，未写出任何一行）；
  - `after/arm-logs/B5-clockmut-cpu8.log` 记录 `ARM B5-clockmut-cpu8 EXIT=3221225786`
    —— 0xC000013A = **`STATUS_CONTROL_C_EXIT`**；
  - 逐臂结果只以臂结束时的一次性 `after/bench-*.json` 落盘 ⇒ **任何在臂中途的终止都会清零该臂**。
- **v1 已完成部分是披露历史，不是可重写的草稿**：`after/bench.log`、`after/arm-logs/B1..B5.log`、
  `after/bench-B1-fixed-quiet.json`、`after/bench-B2-fixed-cpu8.json`、`after/bench-B3-mutant0.5-cpu8.json`
  以及它们的 `after/bench-captures-*` **原样保留，本卡不删除、不覆盖、不改写**（v2 全部落到
  `campaign_v2.*` 新文件，连 `bench.log` 都不追加）。

## C1. 为什么收缩（判据的实质不变，只减 N）

一次终止吃掉整场 ⇒ v2 只保留**能证明这张卡**的部分，并把落盘粒度降到"**每运行一次**"：

| | v1（oracle §4，已中断） | **v2（本 addendum，冻结）** |
|---|---|---|
| 臂数 | 6（B1/B2/B3/B5/B4-quiet/B4-cpu8） | **4**（A1/A2/A3/A4） |
| 运行数 | ≈ 76 | **22**（6+6+4+6） |
| 落盘粒度 | 每**臂**结束写一次 `bench-*.json` | 每**运行**一行 `campaign_v2.jsonl` + 每次追加后重写索引 |
| B5（clock-mutant） | 8 次 | **删除**：它回答的是"测量是否 load-bearing"的**第二**证明，R4（A4）已足够 |
| 双树 T0/T0b | 计划 2× | 保留但按 N 折半（见 C2） |
| R1/R2 判据 | 8/8 | **6/6**（如实登记为 N 缩减；**不再声称 8/8**） |
| R3（反空转） | 24 次 | **4 次**（quiet 2 + load 2） |
| R4（突变） | ≥ 8 红 / 16 次 | **6/6 红**（比例更严，绝对数更少） |

**判据实质未动**：`oracle.md` §2 的施加形态、§2.3 的"不改清单"（`child_started == 2` 一字不改、
`timeout=15`、`child_poll_milliseconds=100`、生产只读、不采用建议 2/3）、§2.4 的语义窗口
（`hang ∈ ceil(clamp(4·t0, 2.0, 4.0))`）、§3 四条判据的**定义与反面**、§5 反空转节点的形态与
"**B4/A3 任何 RED ⇒ 本卡报 blocked，不得报 review_pending 通过**"——**全部原样继承**。
本 addendum 只改：臂数、每臂 N、落盘方式、工件保留方式、负载生命周期。**不放宽任何断言，
不放宽任何期望，不把"够不到 8/8"折算成"6/6 即等于原判据"**：报告里 R1/R2 必须写
"6/6（v1 判据 8/8 的缩减版，8/8 未被 v2 检验）"。

## C2. v2 臂表（**冻结；运行前写定，不得中途扩臂**）

坐标：`ATT = <本 attempt>`，`PY = ATT/iso/venv/Scripts/python.exe`（3.13.9 / pytest 9.1.1）。
`N` = **pytest 节点调用次数**（不是"臂×轮×树"的乘积展开）；每臂的树序在运行前写死如下。

| 臂 | SUT（suite 所在树） | 节点 | 条件 | 树序（按 run 1..N） | N | 期望 | 判据 |
|---|---|---|---|---|---|---|---|
| **A1-fixed-quiet** | `iso/T0`、`iso/T0b`（sha256 `2719b835…`，字节相同） | 节点① | quiet（本卡不加负载） | T0, T0b, T0, T0b, T0, T0b | **6** | 全 PASS | R2′ = 6/6 |
| **A2-fixed-cpu8** | 同上 | 节点① | **cpu8**（8 忙循环） | T0, T0b, T0, T0b, T0, T0b | **6** | 全 PASS | **R1′ = 6/6（本卡的全部目的）** |
| **A3-nonvacuity** | 同上 | 反空转节点（§5） | run1–2 quiet；run3–4 **cpu8** | T0, T0b, T0, T0b | **4**（2+2） | 全 PASS = **挂死子派生被抓住** | R3′ = 4/4 caught |
| **A4-mutant05-cpu8** | `iso/mutant-derivation-0.5`（sha256 `76699401…`，派生退回写死 0.5 s） | 节点① | **cpu8** | M05 ×6 | **6** | **全 RED（测试失败）** | R4′ = 6/6 RED |

- **v1-era 对照（本卡要打掉的东西）**：冻结带 12/12 红、I-14-E cpu8 近 100% 红；
  v1 自己的 B2（fixed + cpu8）是 **15/16**——1 次 `subprocess.TimeoutExpired`（测试自身
  `timeout=15` 撞上外部启动延迟，`starts=1`，**不是** `assert … == 2`）。⇒ **A2 若复现该形态，
  如实登记为"该修法在本机本时段不足"，不调判据、不加重试、不扩臂**（v1 该次运行的原始记录
  在 `after/bench-B2-fixed-cpu8.json`，已披露）。
- **树的语义修正（相对 v1 驱动，运行前声明）**：v1 的 `run_all_arms.py` 把 `--suite` 固定为
  `iso/T0` 的文件、只让 PYTHONPATH 随树变，因此 v1 的"T0b 运行"实际执行的是 T0 的字节。
  v2 每次运行执行**该树自己的 suite**（`iso/<tree>/tests/contract/…`），并把 suite sha256 与
  launcher sha256 逐运行记入 JSONL——T0/T0b 字节相同由 `before/binding_hashes.json` +
  逐运行哈希双重可核；A4 的 M05 只有一棵树，故 6 次全在 M05。
- **A3 的期望方向（澄清，与 §5 一致）**：反空转节点的 pytest verdict 期望 **PASS**——
  它断言的是"挂死子进程**被抓住**"（`child_unresponsive` 非空、reason=`session_start_timeout`、
  被杀 uptime ≤ 派生预算 + 1.0 s、`child_started == 3`）。抓住即绿；看门狗若永不
  开火（派生值空转）⇒ 该节点 RED ⇒ 按 §5 报 **blocked**。同时 JSONL 逐次记录
  `watchdog_kill_uptimes` 与 `hang_timeout_seconds_actually_used`，让"抓住"可被 reviewer
  脱离日志复核。

## C3. 逐次落盘（interruption-safe 的精确定义）

1. `after/campaign_v2.jsonl`：**每运行一行**，在该运行结束、basetemp 保留打包之后**立即**追加
   （`flush + fsync`）。字段至少含：`arm`、`run`（臂内序号 1..N）、`outcome`、`returncode`、
   `wall_seconds`、`guard_seconds`、`started_utc`/`ended_utc`、`condition`、`tree`、`suite`、
   `suite_sha256`、`node`、`basetemp_path`（实际执行路径）、`basetemp_archive`（ZIP 保留副本）、
   `basetemp_artifacts_dir`（扁平工件副本目录）、`basetemp_archived`、
   保留统计（文件数/字节/最长路径字符数/zip 条目数）+ **逐文件清单**
   （rel、执行绝对路径与字符数、bytes、sha256）、events 摘要（`child_started_count`、
   `child_unresponsive_count`、`watchdog_kill_uptimes`、`hang_timeout_seconds_actually_used`）、
   derivation 摘要（`t0_seconds`、`hang_timeout_seconds`）、负载探针、`as_expected`。
2. `after/campaign_v2-index.json`：**每次追加后**原子重写（临时文件 + `os.replace`），
   内容 = 由 JSONL 重建的逐臂累计（planned/recorded/passed/failed/timeout/error/as_expected）、
   总数、最后一行摘要、JSONL 行数与字节数。驱动启动时也先由 JSONL 重建一次索引，
   因此**索引永远不领先于 JSONL**，撕裂行会计入 `torn_lines` 而不是被静默丢弃。
3. **丢失上界 = 一次运行**：进程若在"运行结束 → 保留打包 → 追加 → 索引"链条中间被杀，
   最多丢那一次运行（其 capture 与 `%TEMP%` 原件仍在，可人工核）；重跑由"JSONL 里已有
   (arm, run) 即跳过"实现**续跑**，已落盘的行永不重写。
4. 顺序（写死）：`运行 → 采集 events/derivation → reap 已知 pid → 保留打包
   （清单 → 扁平副本 → ZIP）→ 追加 JSONL → 重写索引`。
   保留失败也**必须**追加该行（`archived=false` + 错误文本），绝不因保留失败而吞掉运行结果。
5. v2 的驱动日志是 `after/campaign_v2.log`（新文件）；**不打开 v1 的 `bench.log`**。

## C4. basetemp 工件保留（CF-I14F-X1 前置，B1 的延续）

I-14-F reviewer（`I-14-F/a20260919-01/reviewer_report.md` §7(ii)）判词：
"`timeout15s-band` is not by itself proof of load causation (§3), so the I-14-E work should
**retain basetemp artifacts** when it tackles the band — **the current cleanup design destroys
exactly the evidence it will need**"。本卡据此前置：

先记**执行侧**——**执行路径短、保留路径不受长度约束**：每次运行的 `--basetemp` 是
   `%TEMP%\i14eapply-v2\<arm>-r<NN>\pytest`（≈70 字符；I-14-F 实测该节点最长生成路径
   suffix = **125** 字符、退化起点 **240/241** ⇒ 总长 ≈195 < 240，路径致因被排除在带外）。
   保留件（清单/扁平副本/ZIP）不参与执行，因此其路径深度不会引入 WinError 206——
   这正是"重定向而不是删除"的做法。
1. **每个 (arm, run) 一个独立 basetemp 目录**：pytest 的显式 `--basetemp` 只在**该次运行开始时**
   清空它自己的目录；本 driver **没有任何 rmtree**（v1 `run_bench.py` 的"臂开始时
   rmtree 整个 root"已废除——那就是会删掉判别证据的 cleanup）。
2. **每次运行后的保留（三重 + 原件，写于任何 v2 运行之前）**：
   - **逐文件清单**（相对路径、**实际执行的绝对路径 + 字符数**、字节数、≤1 MiB 文件的 sha256）
     直接写进该次运行的 JSONL 行——这是 CF-I14F-X1 工件判别（存在/缺失 + 路径长度）的载体；
   - **扁平副本**：≤128 KiB 的每个文件复制为
     `after/campaign_v2-artifacts/<arm>-r<NN>/<idx>.<basename>`（扁平、短路径、任何工具可读；
     `idx → 相对路径` 映射在清单里）；
   - **整树 ZIP**：`after/campaign_v2-basetemps/<arm>-r<NN>.zip`（逐字节、保留目录结构，
     `zip_entries == files_total` 记入 JSONL）；
   - `%TEMP%` 下的**执行原件同时保留**（`executed_tree_deleted: false`）。
   JSONL 记录保留是否成功（`basetemp_archived` / `basetemp_archive_error`）。
3. **v1 的 `%TEMP%` basetemp 一并抢救**（它们还在 `%TEMP%\i14eapply-B1/B2/B3/B5-*`，
   属披露历史且随时可能被系统/下次同名臂清掉）→ 以同样方式存为
   `after/v1-basetemps/<arm>.zip` + `after/v1-basetemps/v1-basetemp-manifest.json`；
   原件同时保留；只复制，不移动，不改名原有臂日志。smoke/setup 的
   `%TEMP%\i14eapply-smoke`、`i14eapply-iso` 也一并入册（**超集于原计划、零运行、只增保留**，
   此处显式披露）。
4. **运行前实测到的硬约束（诚实登记；它本身就是路径致因的活演示）**：首次尝试用
   PowerShell `Copy-Item -Recurse` 把 v1 的 B1 root 拷进 `after/v1-basetemps/…`，最深目标
   路径实测 **≈274–308 字符 > MAX_PATH(260)**，逐文件报
   `Could not find a part of the path`（浅于 260 的兄弟文件同样失败——父目录没建成）。
   这正是 I-14-F 判定"路径致因 ≠ 负载致因"的那族失败形态。⇒ 结论（运行前定死）：
   **attempt 内部放不下深树**（`after/` 前缀已 134 字符 + 最深工件 suffix ≈131 ⇒ 308 > 260），
   所以执行走 `%TEMP%` 短路径（≈196 < 240 起病点），保留走"清单 + 扁平副本 + ZIP"。
   该次失败生成的**半成品目录在我方重做前清除**（那是我方刚生成的残件，不是 v1 历史；
   v1 的 `%TEMP%` 原件一个字节都没动）。
5. 复核点（报告必含）：ZIP 存在且 `zip_entries == files_total`、扁平副本文件数、
   逐臂清单条目数、最长执行路径字符数、`worker_launcher_events.jsonl` /
   `worker_stdout-*` / `worker_stderr-*` 在清单中的**存在/缺失**——**工件判别**（B1 规则）
   由此可执行：事件文件缺失且 `.source_catalog` 存在 ⇒ `artifact-absence`（路径致因），
   不得算负载致因。

## C5. 负载与 guard（每次运行独立、可被任何中断安全放弃）

- **负载**：`condition=cpu` 的运行启动 **8 个忙循环**（与 I-14-E / v1 同形：`x=(x+1)%1000003`），
  预热 1.5 s 后才开始计时；`quiet` 不加负载（含义仍是"**本卡不额外加负载**"，机器本身有
  外部 `chrome-headless-shell` 负载——I-14-E addendum A1 已登记同一口径，本次运行前实测
  `Win32_Processor.LoadPercentage` 亦逐运行记入 JSONL）。
- **burner 自带到期**：v2 的 burner 源码内嵌 `end = time.time() + guard + 120`（= 300 s），
  **即使驱动被硬杀、finally 没跑，孤儿 burner 最多再活 300 s 自行退出**——这是对 v1"B5 中断可能留下
  8 个忙循环"缺陷的修复，写在 `harness/load_v2.py`（不改 v1 的 `harness/load.py`）。
- **guard**：单次 pytest 运行 **180 s**（v1 同值）。超时 ⇒ `outcome=timeout` 照常落盘，
  reap/sweep 该 run root 下的启动器与子进程，**继续下一 run**；不重试、不扩臂、不改判据。
- 每次运行前清扫**本卡自己的** `%TEMP%\i14eapply-v2` 根下遗留启动器/子进程
  （命令行匹配该根，不碰其他会话，与 v1 同规则）。

## C6. 不做什么（继承 oracle §4 并按 v2 复述）

1. 不改生产仓（就地只读；运行后 `harness/final_hashes.py --verify` 出示逐字节证明）；
2. 不放宽任何断言（含 `== 2`、`timeout=15`、`poll=100`；**断言松解（建议 3）明确不采用**——
   与 `I-14-E/after/proposed-test-side-change.md` 建议 1（推荐）一致：hang timeout 由
   **测试内实测启动延迟**导出，`max(2.0, 4·t0)` 再被 §2.4 的 4.0 s 语义上限截断）；
3. 不用"载荷大到必红/小到必绿"凑判据；不把本机本时段结果升格为规范常量；
4. **不删不改 v1 的中断日志与结果文件**；不中途加臂、不加次数、不加确认臂
   （v1 的 `confirm_arms.py` 属于 v1 计划之外的确认工具，v2 不调用）。

## C7. 运行前自愿登记的残余风险（不作为事后辩解）

1. **A2 的 6/6 不保证**：v1 已见 1/16 的 `TimeoutExpired`（`timeout=15` 被外部启动延迟打穿，
   形态是 `starts=1`）。若 v2 复现 ⇒ 如实登记"该修法在本机本时段不足"，不调判据。
2. **A3 的 `timeout=15` 更紧**：该节点要在 15 s 内完成 2 次看门狗击杀（各 ≈ 派生 4 s）+
   3 次启动，cpu8 下余量小；若 RED ⇒ 按 §5 报 **blocked**（不得以"其实是超时不是空转"
   自行豁免——但必须同时出示 events：`child_unresponsive` 是否开火、uptime 落点，供
   reviewer 区分"看门狗没开火（真空转）"与"外层 15 s 预算不够"两种 RED 形态）。
3. **外部负载不可控**：同机 `chrome-headless-shell`（PIDs 672/36184 等，I-14-E A1 已登记
   ≈8.8/12 核）仍在；"quiet" 只能读作"本卡不加负载"。负载探针逐次入册，
   臂间并发差异必须在结论里写明，不得算成臂间差异（I-14-E B2 同规则）。
4. **6/6 检验不了 8/8**：R1/R2 的原判据在 v2 下**不被满足检验**，只能报 R1′/R2′=6/6 并注明
   这是 owner 裁定（E-2 收缩）下的缩减检验。
