# oracle.md — WC-4 = F12-RC120（finalization flush rc=120 → rc=2）

- **卡**：WC-4（代号 F12-RC120）｜**attempt**：`execution_runs\WC-4-RC120\a20260923-01`
- **冻结时点**：2026-09-23（本文件写入并出 `oracle.sha256` **之后**才允许跑 RED/GREEN/MUTATION/REGRESSION）
- **生产写**：RF 生产树 **零写**；一切测量在 `iso\rf\`（生产镜像）与本 attempt 目录内
- **域来源（frozen，不改）**：I-09-A `decision.md` §7 故障点表（sha `94a27b8ae31cb746…`，L412–L425）——`F12 | stdout 输送失败（管道关闭/终端退出） | … | rc（A）= **0 或 2** | …`；owner 裁决见 binding。

---

## 1. 域不变式（O-series，frozen）

- **O-1（数值域不变式）**：产品 CLI `scripts/revenue_forecast.py` 在 **F12 故障**（stdout 输送失败：写端打开而读端关闭的管道 / 终端退出）下的**进程退出码 ∈ {0, 2}**。
  **不修 oracle、不修冻结数值域**（owner 原话 §23「2，记为待修」= 第一选项口径：{0,2} 维持、rc=120 记为待修产品缺陷）。
- **O-2（正常路径不变式）**：非故障路径退出码与生产**逐例相同**（成功 0、错误类 2、argparse usage 2、`--version` 0）；stdout/stderr 文本与生产逐字节等同；既存产品测试家族**结果 before == after**（无 skip、无 xfail、无新失败）。
- **O-3（零产写）**：RF 生产树（`scripts/` `tests/` 等）在本卡全程无字节变化；交付只经 `changes.diff`。

## 2. RED 期望（fix 前必须实测到，先红）

- **R-1**：iso（=生产镜像，未修）运行 `scripts/revenue_forecast.py <input> --validate-only`，stdout = **写端管道、读端已关**（同一故障构造，复刻 I-09-C `probe_f12.py` B 臂）→ **raw 子进程 rc = 120**，且 120 ∉ {0,2} ⇒ **RED（缺陷复现）**。
- **R-2**：同一次运行 stderr 含 CPython finalization 自报文本 `Exception ignored on flushing sys.stdout` 与 `OSError: [Errno 22] Invalid argument`（机制指纹）。
- **R-3**：对照臂 A（管道有读者）= 0、C（stdout=普通文件）= 0 ⇒ 单变量仅 stdout 汇不同（与 I-09-C A/B/C 归因链一致）。
- **R-4**：新增产品测试 `tests/test_stdout_flush_exit_domain.py`（RED 阶段以未修源跑）**必须 FAIL**（观察值 120 vs 期望 2）——保证红是真红、非空转。

## 3. GREEN 期望（fix 后）

- **G-1**：同一 F12 构造 → **raw rc = 2 ∈ {0,2}**。
- **G-2（错误文本保留，fail-closed 且 informative）**：同一次运行 stderr 含产品侧错误文本（子串 `stdout flush failed` 且含底层错误详情 `Errno 22`/`Invalid argument`）；**无**未捕获 traceback；**无** CPython `Exception ignored on flushing sys.stdout`（finalization 不再失败）。
- **G-3（O-2 逐例）**：A/C 对照臂与正常 CLI 矩阵（validate-only 成功=0、invalid JSON=2、missing arg=2、`--version`=0、formal `--output/--markdown`=0）与生产**逐值相同**。
- **G-4（家族）**：grep 命中的 8 个产品测试文件（见 commands/REGRESSION 节）before == after 全等，`no skip/xfail`。
- **G-5**：`tests/test_stdout_flush_exit_domain.py` **PASS**。

## 4. MUTATION 期望（非空转证明）

- **M-1（整体回退）**：把归一化撤掉（恢复 `raise SystemExit(main())` 原样）→ F12 构造 **rc=120 复现**、新测试再次 FAIL ⇒ 变异被抓。
- **M-2（半回退：只留 catch、不留流替换）**：`flush()` 异常被吞但不中和 `sys.stdout` → **仍 120**（机制实验 M4 已预言）⇒ 两半（域内捕捉 + finalization 中和）都承重，缺一不可。

## 5. 机制勘误（mechanism erratum，随本卡更正，frozen）

- **错描述（被更正对象）**：`AUDIT-GOAL\evidence\report_SA-DEFECT.md:165` 对 F12 的机制列 = **「断言在返回后开火」**。
- **正描述（以此为准）**：F12 的 rc=120 **不是任何断言**；是**产品 CLI 解释器 finalization 段 stdio flush 失败**（`sys.stdout` 缓冲内容在解释器关闭时 flush 到无读者的管道 → `OSError: [Errno 22] Invalid argument`）→ **CPython 自报进程退出码 120**，覆盖程序原本设置的 0/2。
- **证据**：①不含任何 RF 代码的最小片段同样得 120（`evidence\mech\mech_cases.json` M0/M1，pipe_reader/file 臂 0/2 正常）；②RF 源码 grep `120` = 0 命中（源内无该字面量）；③I-09-C `handoff.json:54` 与 `pipe_controls.json:22` 原文同一机制；④I-09-C `reviewer_report.md:46` 同。

## 6. 非目标（non-goals）

1. **不改冻结数值域**、不修 I-09-A oracle、不把冻结 F12 案例「重跑到绿」（I-09-C 封存件一字不动）。
2. **不改 stderr 汇**（F12 = stdout 输送失败）；stderr 汇失败不在本卡构造面。
3. 不动 `revenue_core` / 发布注册表 / 晋升面字节；**仅** `scripts/revenue_forecast.py`（+ 新增产品测试文件）入 `changes.diff`。
4. I-09-C 封存 harness `probe_f12.py:65`（C.stderr 误标）**不改封存字节**——修正以本卡 `evidence\probe_f12_line65_fix.diff` 交付并在 decision 记载（见 handoff carried）。
