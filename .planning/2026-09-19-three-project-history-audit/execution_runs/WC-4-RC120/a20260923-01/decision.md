# decision.md — WC-4 = F12-RC120（机制追踪 · 形态取舍 · 正常路径不变证明 · SA-DEFECT 措辞更正）

## 1. 机制追踪（report opener：120 从哪来，逐行钉）

**结论先说：rc=120 不是任何断言、也不是 revenue-forecast 源码里的任何字面量——它是 CPython 解释器在 finalization（解释器关闭）段 flush `sys.stdout` 失败后自报的进程退出码，会覆盖程序自己设置的 0/2。**

| 环节 | 位置（line-cited） | 事实 |
|---|---|---|
| ① 程序把输出**缓冲**进 stdout | `scripts/revenue_forecast.py:111`（`print("valid")`，validate-only 臂）、`:117`（`print(rendered, end="")`，JSON 臂） | 小写入留在 `sys.stdout` 缓冲区，**不立刻触碰管道** |
| ② 程序设定自己的退出码 | `:120-122`（错误类：`except (OSError, json.JSONDecodeError, ForecastInputError)` → stderr → `return 2`）、`:123`（`return 0`） | 域内码只有 0 与 2 |
| ③ 进程退出入口 | `:126-127`（`if __name__ == "__main__": raise SystemExit(main())`） | 此处生效的是 0/2 |
| ④ **finalization flush（缺陷发生点，**非**RF 源码）** | CPython 解释器关闭段：flush 缓冲中的 `sys.stdout` → 管道无读者 → `OSError: [Errno 22] Invalid argument` → **解释器把进程退出码改写为 120** | stderr 指纹逐字：`Exception ignored on flushing sys.stdout:\r\nOSError: [Errno 22] Invalid argument` |
| ⑤ 「120 在源码里吗？」 | `grep 120 scripts\*.py` → 7 处全是 `FC-120x` 需求号；**退出码形 0 命中**（`exit(120)/return 120/= 120/rc=120/EXIT_120` 全 0） | `evidence\mech\grep_120_and_emitter.txt` |
| ⑥ 「那串报错是谁的？」 | 字面量 `Exception ignored on flushing sys.stdout` 在 **`python313.dll` byte offset 5921656** 命中（dll sha `d97a9810…`；python 3.13.9） | 报错文本**由解释器发出**，RF 源码无此串 |
| ⑦ 最小反证（无 RF 代码） | `mech_case.py` M0：`sys.stdout.write('valid\n'); raise SystemExit(0)` + 断读端管道 → **120**；reader/file 臂 0 | `evidence\mech\mech_cases.json` |
| ⑧ 「改退出码也没用」 | M1：同一最小片段 `raise SystemExit(2)` + 断读端 → **仍 120** | 证明必须**中和 finalization 的 flush**，光归一化 main 的返回值不够 |
| ⑨ 「只 catch 不够」 | M4：显式 `flush()` 捕获、写 stderr、`rc=2`，但**不替换坏流** → **仍 120** | 证明「域内捕捉」与「流中和」两半都承重（正是 MUTATION-2 的依据） |
| ⑩ 历史归因链（冻结在案） | I-09-C `probe_f12.py` A=0 / B=120 / C=0（单变量=仅 stdout 汇）；`pipe_controls.json:22`；`handoff.json:54`；`reviewer_report.md:46` | 本卡复测同构同值（本卡 probe A/C=0/0、B=120→修后 2） |

**SA-DEFECT 机制措辞更正（本卡的 erratum 承载）**：`AUDIT-GOAL\evidence\report_SA-DEFECT.md:165` 把 F12 机制写成 **「断言在返回后开火」** ——**错**。F12 全程没有任何断言参与；正确机制=上表 ④：**CLI 的解释器 finalization 段 stdio flush 失败（Errno 22），由 CPython 自报 rc=120**。REGISTRY §八十四 F12 行（`:1701`）与 §八十七（`:1748`）已按此口径登记；本卡 oracle §5 把该更正冻结。

## 2. 形态取舍（evidence-first → freeze）

**可选项**（卡面给的两案）：
- **(i) flush 失败 → rc=2（既有错误类）+ 错误文本保留在 stderr**（fail-closed、informative）；
- (ii) 进程仍须带语义码退出时，把 flush 失败路径**归一化**为 2 + 错误文本。

**实测证据先于冻结**（oracle 冻结前的 phase0，commands.md C1）：

| 形态 | 断读端管道实测 | 判定 |
|---|---|---|
| 不做任何事（现状） | **120**（M0/M1） | 域外 ⇒ 缺陷 |
| 只把 `main()` 的返回值归一化 | **120**（M1：`exit(2)` 也被改写） | 无效 |
| 显式 `flush()` + catch + 写 stderr + `rc=2`，**不换流** | **120**（M4） | 无效（finalization 再次 flush 同一坏流） |
| 显式 `flush()` + catch + 写 stderr + `rc=2` + **把坏流换成 devnull/空流** | **2**，且 stderr 带 `stdout flush failed: OSError(22, 'Invalid argument')`、**无** `Exception ignored`（M2/M3） | **采用** |

**裁定：(i)∩(ii) 的同一点**——在**域内**（`__main__` 边界）先 flush，失败即 `return 2`（案 i 的错误类），同时中和坏流使 finalization 无法改写（案 ii 的「进程最终退出码=2」）。**选型理由**：
1. 失败时**没有任何输出送达**（管道已死）——保留 0 会谎报成功；2 是既有错误类（`:120-122`），且 ∈ 冻结域 {0,2}，**不需要动 oracle**（与 owner §23 第一选项一致）。
2. M1 证明「带语义码退出」在该故障下**不可保**（任何码都会被 120 覆盖），故 (ii) 单独不可实现；必须先中和流，中和后 rc 可自由落在域内 ⇒ 取 2。
3. 错误文本既保留我们自己的 `error: stdout flush failed: [Errno 22] Invalid argument`，又不再需要 CPython 的 `Exception ignored` 兜底 ⇒ **fail-closed 且 informative**（oracle G-2）。
4. **改动面最小**：仅在 `raise SystemExit(...)` 一处包一层 `_finalize_exit_status(main())`；`main()` 内部、`revenue_core`、发布注册表、晋升面**零字节变化**（changes.diff=2 文件，均在 CLI 边界/新增测试）。

**实现位置**：`scripts/revenue_forecast.py` 尾部新增 `_neutralize_broken_stream()` 与 `_finalize_exit_status`，入口改为 `raise SystemExit(_finalize_exit_status(main()))`（详见 changes.diff）。**行为变化仅在 flush 失败路径**；成功路径只是把 flush 提前到入口处执行（同一批字节、同一 rc、同一文本），由 §3 逐例证明。

## 3. 正常路径不变证明（before == after）

- **家族（grep 依据见 §5）**：8 个触碰该 CLI/finalizer 的产品测试文件，未修 iso = **64 passed / 48 subtests / 0 failed / 0 skip / 0 xfail**（rc 0）；已修 iso（同一环境，含 sibling `filing-fetch` 检出）= **64 passed / 48 subtests / 0 failed**（rc 0）。逐行 diff = **仅两行 wall-clock 不同**（`evidence\rgm\family_compare.txt`，`diff` 段除时间外为空）。
- **正常 CLI 矩阵（probe，每阶段都跑）**：A（管道有读者）=0、C（stdout=文件）=0、N1 validate-only=0 且 stdout 逐字 `valid`、N2 非法 JSON=2、N3 usage=2、N4 `--version`=0、N5 formal `--output/--markdown`=0 且两产物落盘——**red / green(×2) / mut1 / mut2 五阶段全部相同**（各阶段 `probe.json` 的 `checks.normal_ok`、`baselines_ok` 均 true）。
- **ruff 0.15.18（CI 钉版）**：两文件 `All checks passed!`（rc 0）。
- **复杂度棘轮（`tools/tests/test_complexity_ratchet.py`）**：门测试在 iso 与生产**逐条同红**（`analysis/confidence.py 32>23`、`model_extensions.py 27>10` = **仓库既有红**，循环先断在 confidence.py、走不到本卡文件）；用**同算法**单测本文件（`harness\check_ratchet_own_file.py`）：`revenue_forecast.py max=18（worst=main:18）== frozen 18`，**iso fixed / iso pristine / 生产三者同值** ⇒ 本卡未加重棘轮（`OWN_FILE_RATCHET_OK`，rc 0）。
- **per-module 覆盖门（`tools/run_coverage_gates.py` 的 `revenue_forecast.py ≥60%`）**：5 个 CLI 触碰测试子集实测 **73%**，缺行全在 `main()` 既有行（73-100/102/106/117-122），**本卡新增语句 0 miss**（子集即达门、全量单调更高）；为此产品测试**加层 in-process 单元守卫**（本机 coverage 的子进程钩子实测未生效，见 commands P1 动机段），使新代码覆盖不依赖钩子。`evidence\rgm\coverage_subset_fixed.txt`。
- **生产零写**：`scripts` 树 sha `d29e761d…`、`tests` 树 sha `a0d7667c…` 开工与收尾**相同**；新测试未出现在生产树（`evidence\production_zero_write_before.txt` / `_after.txt`）。
- **无 skip/xfail**：家族两跑的 summary 均无 s/x 计数（`family_compare.txt` 计 0）。

## 4. 红绿变异（rgm 计数）

| 环节 | 观测 | 判据（oracle） | 结果 |
|---|---|---|---|
| RED（probe） | F12=**120**、`Exception ignored` 在、基线 0/0、矩阵全对 | §2 R-1..R-3 | ✅ |
| RED（产品测试） | v1: **1 failed, 2 passed**（断言原文 `got 120`）；**v2 加层后: 6 failed, 2 passed**（1 端到端 + 5 in-process helper 缺失；通过的 2 个=基线/usage） | §2 R-4 | ✅ 真红 |
| GREEN（probe） | F12=**2**、`error: stdout flush failed: [Errno 22] Invalid argument`、无 `Exception ignored`、基线/矩阵不变 | §3 G-1..G-3 | ✅（run1 与终版两次独立跑 `probe.json` **逐字节同 sha** `52807297…`） |
| GREEN（产品测试） | v1: **3 passed**；**v2: 8 passed**（run1 与终版各一次） | §3 G-5 | ✅ |
| REGRESSION 家族 | 64/48 == 64/48、0 skip | §3 G-4 | ✅ |
| MUTATION-1（整体回退） | F12=**120** 复现 + 测试 v2 **6 failed, 2 passed**（字节=pristine，与 RED 同态，如实注明） | §4 M-1 | ✅ 捕获 |
| MUTATION-2（只留 catch） | 文本在、F12 仍 **120** + 测试 v2 **2 failed, 6 passed**——失败的恰是两条半承重断言（端到端 120、`assert sys.stdout is not broken`） | §4 M-2 | ✅ 捕获 ⇒ 非空转 |

**rgm 计数**：RED 2 项 / GREEN 2 项 / MUTATION 2 项（均捕获）/ 家族 8 文件×2 跑全等 / 产品测试 v2 8 用例（RED 6 红→GREEN 8 绿→MUT1 6 红→MUT2 2 红→终版 8 绿）；失败尝试 3 次（harness NameError、家族缺 sibling、mutate2 回退锚失败）全部如实入 commands.md P1、不作证据。

## 5. 家族 grep 依据（谁触碰这个 CLI/finalizer）

`grep 'revenue_forecast\.py|scripts[/\\]+revenue_forecast' tests\*.py` → 8 文件（每个都以 `subprocess` 起真进程，故必然穿过 `__main__`/finalization 边界）：`test_industry_end_to_end.py:237`、`test_publication_pipeline.py:87,332,360`、`test_verbose_validation.py:83`、`test_zr701_f1_draft_formal.py:68`、`test_zr704_validate_only_gate.py:37`、`test_zr710_publication_txn.py:105,141`、`test_zr803_chaos_recovery.py:198,218`、`test_zr804_platform_shape.py:49,177,184`。

## 6. 决定与依据（绑定）

1. **冻结数值域 {0,2} 不动**：owner §23（`OWNER_DECISIONS.md:484`，原话「2，记为待修」）+ I-09-A `decision.md:412-425`（rc(A)=0 或 2）。本卡**只修产品**。
2. **产品修形态**：本案 §2 裁定（flush 失败 → rc=2 + stderr 文本 + 流中和）。
3. **机制措辞更正**：`report_SA-DEFECT.md:165`「断言在返回后开火」→「解释器 finalization 段 stdio flush 失败（Errno 22）自报 rc=120」（本卡 oracle §5 冻结，本文件 §1 展开）。
4. **`probe_f12.py:65` 随修**：I-09-C attempt 为封存件（binding sha 已 pin），**不改封存字节**；一行修正以 `evidence\probe_f12_line65_fix.diff` 交付（`err` → `p.stderr`），效果=仅 C 臂 stderr 标签改真，A/B/C rc 与归因不变。
5. **交付面**：`changes.diff` 恰 2 文件——`scripts/revenue_forecast.py`（修）+ `tests/test_stdout_flush_exit_domain.py`（新，8 用例=3 端到端 + 5 in-process 单元守卫）。第 2 个文件的正当性：①把「域内 rc=2 + 文本保留 + 无 CPython 兜底报错」钉进产品测试族（MUTATION 在产品侧就红，不只靠 harness）；②in-process 层使新增语句覆盖**不依赖 coverage 子进程钩子**，保住 `run_coverage_gates.py` 的 per-module ≥60% 门（实测子集 73%、新语句 0 miss）。

---

## 7. review_round_2 —— r1 复审（P1=F-01）的修复轮裁定（append-only 续）

> 前缀自证：本节之前 `decision.md` = **11542 B**、sha256=`fad182c0ec7391de922750184c8b1b4434841643ba90e783e39e1e62e102ffe2`（r1 `DELIVERABLES.sha256` 行）；追加后前 11542 B 逐字节重算同值 ⇒ `prefix_bytes_preserved=true`（`harness\prefix_selfcheck_r2.py` → `evidence\rgm2\prefix_selfcheck_r2.json`）。r1 复审报告只读未改。

### 7.1 F-01（P1）根因与修法：**把修复做到满足 oracle，不改 oracle**

- **被证伪的前提**：r1 `handoff.md §3.3` 写「`main()` 内 `SystemExit` 且 stdout 已缓冲的组合未构造，该路径 stdout 为空、无待 flush 内容——**推理而非实测**」。本轮实测（iso `4e6b64a7`，`--help`/`-h` × 断读端管道）：**raw rc=120**，stderr 逐字 `Exception ignored on flushing sys.stdout:` + `OSError: [Errno 22] Invalid argument`，**无** `error: stdout flush failed` ⇒ **help 文本正是被缓冲的内容，该前提为假**。
- **根因**：`argparse` 的 `--help`/`-h` 动作**先 `print_help()` 把文本写进 stdout 缓冲，再在 `parse_args()`（位于 `main()` 内部）`raise SystemExit(0)`**；r1 的 `raise SystemExit(_finalize_exit_status(main()))` 只包住 `main()` 的**返回值**，`SystemExit` 直接穿透到解释器 → `_finalize_exit_status` 未执行 → finalization 段 flush 失败 → CPython 自报 120（机制与 §1 ④ 完全相同，只是入口未达）。
- **修法（复审建议第 1 条路，父已裁定）**：`if __name__ == "__main__":` 块内 **`try: _exit_code = main()` / `except SystemExit as _system_exit:` 取码（`int`→原值、`None`→0、其余→2）/ `raise SystemExit(_finalize_exit_status(_exit_code))`**——**同一终态处理**覆盖「返回值」与「`main()` 内 `SystemExit`」两条路径。
- **为什么不改 oracle**：O-1 是**冻结不变式**（`oracle.md L12`，无路径豁免），P1 说「修复没满足 O-1」⇒ 正确处置是**改修复**。复审给出的第 2 条路（owner 出 oracle 范围豁免）**需要 owner 裁定，本卡不走、也不代裁**；本轮**未登记任何 oracle 待裁项**（实现者不认为 oracle 有误）。
- **闭合证据**（全部新产物，r1 证据零改写）：修前 `evidence\rgm2\red\probe.json`（help/h=**120**，无产品文本）→ 修后 `evidence\rgm2\green\probe.json`（help/h=**2**、`error: stdout flush failed: [Errno 22] Invalid argument` 在、`Exception ignored` 消失）；新判据产品测试 `test_help_with_broken_stdout_exits_2_with_preserved_error_text`（`--help` 与 `-h` 两旗）修前 **1 failed, 8 passed**（`assert 120 == 2`）→ 修后 **9 passed**；三变异臂全部打红（见 7.3）。
- **O-1 现覆盖的路径**（本轮实测）：`--help`、`-h`、`--version`、`--validate-only`、usage（无参数）× 断读端 = **2/2/2/2/2**；读端正常臂 = **0/0/0/0/2**。生产 pristine 仍 120（**非回归、待合并 `changes.diff` 后修复**，本轮只读实测）。

### 7.2 O-2（正常路径不变）在 r2 的复证

- **行为增量只在「`SystemExit` 于 `main()` 内抛出」路径**：正常返回路径与 r1 **逐字节同逻辑**（`_finalize_exit_status` 未动）；`--help`/`-h` 的**成功路径**（读端正常）= 缓冲文本由入口处显式 flush 后以 rc=0 退出，**字节数与 rc 与生产一致**（矩阵实测 0，`usage:` 文本形状校验通过）；usage 错误路径仍 stderr-only、rc=2。
- **家族面（8 文件）**：本轮**未能重跑**（`tempfile`/`tmp_path` 在本会话沙箱被拒，见 commands R2-环境限制 1——复审 §4.1 同源）；静态面复证：8 个家族文件对 `--help`/`-h` **0 命中**（grep），即**家族不会走到 r2 新增的分支**；r1 的家族 64/48 字节级证据照录。⇒ O-2 **动态矩阵已复证、家族重跑 = unverified（环境）**。
- ruff `All checks passed!`（rc 0）、棘轮 `18==frozen 18`（`OWN_FILE_RATCHET_OK`，rc 0）——均见 `evidence\rgm2\`。

### 7.3 变异矩阵（r2）：**冻结 M-1/M-2 不动，补 F-08 臂**

| 臂 | 与冻结判据关系 | 实测 |
|---|---|---|
| MUT-A 回退包装（= 复审建议变异①） | r1 `handoff/decision` 未列此臂（r1 的 M-1 是**整退到 pristine**，本臂是**只退回 r1 包装**）——**r2 新增**，判据=「新 `--help` 条必须红」 | iso 回到 `4e6b64a7`（与 r1 快照逐字节相等），探针 `--help`=**120**，测试 **1F/8P** ⇒ 承重 |
| MUT-B 只 catch 不换流 | **= 冻结 M-2**（在 r2 包装上重跑） | `99fc716a…`，`--help`=**120**（文本在、`Exception ignored` 也在），validate/version=120，测试 **3F/6P** ⇒ 承重 |
| MUT-C 只中和不 catch | **F-08 指出的缺失臂，本轮补**；**不写入冻结 `oracle.md §4`** | `4f9d7803…`，`--help/-h/validate/version`=**0**、**无产品文本**（∈{0,2} 但**违反 G-2**），测试 **4F/5P** ⇒ 承重 |

**F-08 关闭语句**：`oracle.md §4` / `decision §4` 的 M-1、M-2 **判据与文字一字未改**；r2 以**卡面外新增臂**补足「只中和不 catch」的非空转证据，并保留「catch 半亦由产品测试 `test_finalize_exit_status_normalizes_flush_failure_to_2` 钉住」的既有说明。

### 7.4 交付形态变更（r2）

1. `changes.diff` **重生成**：`2a2dfede…` → `405fec6d…` + 新测试 195 行；**10114 B**、sha `d1a79376c518eab3…`；hunks = `@@ -125,0 +126,44 @@`（r1 修复）+ `@@ -127 +171,15 @@`（r2 修复）+ 新测试 `@@ -0,0 +1,195 @@` ⇒ **r1/r2 各一 hunk**。diff 生成参数由 `n=3` 改 `**n=0**`（理由见 commands R2-C10b；r1 旧 diff 预像归档 `evidence\rgm2\changes_r1_preimage.diff`）。
2. 新测试文件由 **8 → 9** 用例（追加 `test_help_with_broken_stdout_exits_2_with_preserved_error_text`，只在文件尾追加，r1 的 175 行前缀字节不变）。
3. iso CLI 由 `4e6b64a7…` → **`405fec6d7ea23324…`**；`_neutralize_broken_stream` / `_finalize_exit_status` **一字未改**（r2 只动 `__main__` 块）。

### 7.5 P3 处置摘要（详 commands R2-步骤6）

- **F-02** = 口径 erratum（rc=0 属 `coverage run`；`coverage report` 本轮实测 **rc=2**，因仓库全局 `fail_under=84`；与单模块 ≥60% 门不同域）——**不改证据字节**。
- **F-03** = `pin_drift` 登记（10 MATCH/9 DRIFT，与复审同分割；register 非空钉行现 **+3** 且**逐字全在**、closure decision **delta=0**、`iso_cli_before` 预期内漂）——**不回写 pin 表**。
- **F-04** = C1b 阶段标注更正（产物 mtime 00:04:17 > 冻结 23:50:41；「冻结前已跑」不可证、不作断言）。
- **F-05** = handoff §1 表述更正（封存件 `report_SA-DEFECT.md` **字节未动**，sha `374a5770…` == pin；更正由本卡 oracle §5 / decision §1 承载）。
- **F-06** = decision §5 家族 grep **补列 `test_publication_pipeline.py:315`**（文件集合仍恰 8）。
- **F-07** = 追加披露（r1 首轮 RED probe 被末轮同名覆盖；r2 起先归档再覆盖）。
- **F-08** = 见 7.3。

### 7.6 r2 unverified / 未证（如实携带）

1. **家族 64/48 本轮未重跑**（`tempfile`/`tmp_path` 沙箱拒绝）——r1 字节级证据 + 复审 §4.1 照录。
2. **单模块覆盖门 ≥60% 本轮未复测**（依赖直调 `main()` 的测试在本会话不可运行）；r1 的 73% 未被本轮推翻也**未被本轮复证** ⇒ unverified，交合并批/CI。本轮子集观测值见 commands R2-环境限制 3（**与 73% 不可比，不作门结论**）。
3. **Linux/macOS 断管码值**仍未测（r1 已披露，本轮沿用）。
4. **`--help` 之外的其它 `SystemExit`-in-`main` 组合**（如自定义 `parser.exit(status)` 非 0/2 码）**未穷举**；映射规则 `int→原值 / None→0 / 其余→2` 已实现并写入源注释，但只有 argparse 实际产生的 0/2 被实测。
5. **stderr 汇断管**仍为 oracle §6 非目标，本轮未构造。

### 7.7 签字与状态

- 本轮**不自签 ACCEPT**：`status=review_pending`、`implementer_signed=false`（见 `handoff.md ## review_round_2` 与 `handoff.json`）。
- `blocked_by = []`（无阻断项；上述 unverified 均为环境限制/非本卡面，不构成阻断）。
