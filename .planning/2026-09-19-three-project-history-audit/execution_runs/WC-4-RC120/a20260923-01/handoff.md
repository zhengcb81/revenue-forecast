# handoff.md — WC-4 = F12-RC120 → **review_pending**

- **状态**：`review_pending`（九步已跑完、证据齐、**未复审**）
- **签字**：**unsigned** —— 本卡无任何 reviewer/owner 签字；`oracle.md` 仅由本实现者冻结（sha 见 `oracle.sha256`）
- **交付形态**：RF 生产零写；产物 = `changes.diff`（2 文件）+ 本卡 8 件套（oracle / binding / commands / decision / changes.diff / handoff / evidence / recovery）
- **绑定**：`binding.json` sha `caca43e80e0692216a146fb3d4f2a81ff4904954aebf8c71233285f43c8220db`（19 pins；逐行原文 `evidence\pins_freeze.txt`）；`oracle.md` sha `7fecfaea02f62b3740122a2c79ff5f7194bdd29505696cb0e8c38cdce1cb8be8`（收尾复算同值）；`changes.diff` sha `f0a01489a01b72005ccc112acb4dc4d0812e675490a6a184257ac2186c02b187`（8306 B）；八件套+证据清单总账=`DELIVERABLES.sha256`（证据 57 项另见 `evidence\MANIFEST.sha256`）

## 1. 处置状态（映射）

| 项 | 本卡处置 | 依据 |
|---|---|---|
| **F12 产品半**（断管/flush 失败退出归一化） | **FIXED-pending-review**（修已交付、待复审；非 CLOSED、非 REM-79） | `changes.diff` + decision §2/§4；REGISTRY §八十四 F12 行 `:1701`、§八十七 `:1748` |
| **F12 数值域半**（{0,2} vs 120 的勘误与否） | **NO-CHANGE（owner 已裁：维持 {0,2}，不修 oracle）** | `OWNER_DECISIONS.md:484`（§23，原话「2，记为待修」）；I-09-A `decision.md:412-425` |
| **SA-DEFECT 机制措辞** | **CORRECTED（本卡承载）**：「断言在返回后开火」→「解释器 finalization 段 stdio flush 失败（Errno 22）自报 rc=120」 | `report_SA-DEFECT.md:165` 被更正；oracle §5 冻结；decision §1 展开 |
| **`probe_f12.py:65`（C.stderr 误标）** | **CORRECTION DELIVERED, SEALED BYTES UNTOUCHED** | `evidence\probe_f12_line65_fix.diff`（`err`→`p.stderr`）；I-09-C 封存件不回改，见 decision §6.4 |
| **REM-79**（REM79 差集常设工具） | **NOT THIS CARD**（=WC-5，另卡） | REGISTRY-CLOSURE `decision.md:96-97`；register `:1705`（D1 注记） |
| **REM-24**（M14 OQ-03 D/E 层追认） | **owner 追认已落地=CLOSED(owner-ratified)**；**与本卡触碰面无关**（本卡只改 CLI 与新增测试，不触 M14/OQ-03/signed 约定面），按卡面要求**在此备录** | `OWNER_DECISIONS.md:483`（§23.1「1，追认」）；register `:1747`（§八十七） |

**owner 票面引用（完整）**：§22「守卫收窄」（`OWNER_DECISIONS.md:473-477`，single_owner 守卫按自身语义收窄——**与本卡无关的同文件上下文**，仅按卡面要求引注）；§23 F12「记为待修」（`:481-486`，本卡授权依据）；REGISTRY-CLOSURE §八十四 F12 rows（register `:1701` + REGISTRY-CLOSURE `decision.md:64,93-94,104`）；owner-vote register note（register `:1741` 待票登记 + `:1745-1749` 双票落地）。

## 2. 交付文件（待复审逐件核）

1. `changes.diff` —— 恰 2 文件：
   - `scripts/revenue_forecast.py`：`2a2dfede7941b0fa…` → `4e6b64a789b97f30…`（+1591 B；新增 `_neutralize_broken_stream` + `_finalize_exit_status`，入口包一层；复杂度 max 18==frozen 18 未变）
   - `tests/test_stdout_flush_exit_domain.py`（**新增**，6192 B，sha `5b8e8a3fc1ebf5fb…`）：**8 用例** = 3 端到端（断管 rc=2+文本保留+无 `Exception ignored`；reader 基线 rc=0；usage 仍 rc=2）+ 5 in-process 单元守卫（成功直通 0/2、失败归一化 2 且**换流**、既有错误码 2 保持、stderr 也坏时仍 2、devnull 不可用时回退 `_NullStream`）
   - `harness\verify_diff.py` 已做 **apply-check**：重算 unified diff 与盘上 `changes.diff` 逐字节同（`VERIFY_DIFF_OK`，无 git）
2. `oracle.md` + `oracle.sha256`（冻结在跑 RGM 之前；收尾复算同值）
3. `binding.json`（19 pins）+ `evidence\pins_freeze.txt`（pin 行逐字原文）
4. `commands.md`（P0 预登记 + P1 全回填，含 3 次失败尝试披露）
5. `decision.md`（机制追踪 line-cited、形态取舍、正常路径不变证明、SA-DEFECT 更正）
6. `evidence\`（RED / GREEN / MUTATION-1 / MUTATION-2 / 家族 before+after+compare / mech / 零写 / lint）
7. `recovery.md`（重建与撤销路径）

## 3. 未映射 / 未证（unmapped · unproven，如实携带）

1. **平台未证**：全部实测在 Windows + CPython 3.13.9；Linux/macOS 的断管码值（EPIPE 形态）**未测**（语义同为 OSError ⇒ 预期同修，但不宣称已证）。
2. **stderr 汇本身断管**：未构造（oracle §6 明确非目标；实现已 best-effort 守卫，但无实测）。
3. **argparse/`SystemExit` 从 `main()` 内部抛出且 stdout 已缓冲**的组合：未构造（该路径 stdout 为空、无待 flush 内容——**推理而非实测**）。
4. **家族面=8 个 grep 命中文件**（卡面口径），**未跑全量测试套件**；全量回归由合并批/CI 承担。
5. **家族环境补丁**：iso 镜像缺同级 `filing-fetch` 检出导致 2 个环境红（try1），以复制 `Projects\filing-fetch`（306 文件/37.4 MB，`/MIR`、不含 `.git`）入 `iso\` 解决；**生产 sibling 未被本卡写入**。try1 原始日志被 try2 同名覆盖（披露，摘要入 commands.md P1）。
6. **`probe_f12.py:65` 未落封存件**：修正以 diff 交付；若父裁定要随修本体，需另开 supersession 载体（封存 sha 已 pin）。
7. **120 的 C 源码行不可引**：本机仅有 `python313.dll`（无 CPython 源码 checkout），机制以 ① dll 内字面量命中 ② 无 RF 代码的最小复现 ③ 五阶段实测 三重钉住，但**没有解释器源码行号**（如实披露）。
8. **家族日志编码**：PowerShell `*>` 重定向产出 UTF-16，已由 `harness\compare_family.py` 解码并留 `family_compare.txt`。
9. **`tools/tests/test_complexity_ratchet.py` 既有红**：iso 与生产**逐条同红**（`analysis/confidence.py 32>23`、`model_extensions.py 27>10`）——非本卡引入；本卡文件的棘轮值经同算法单测=18==frozen（`check_ratchet_own_file.py`，rc 0）。**该既有红是否要另立修卡=父裁**（超出本卡面）。
10. **覆盖门只跑了子集**：`run_coverage_gates.py` 全量（`pytest tests`）未跑——全量含可能触网的 e2e，受本卡 **no network** 约束；已用 CLI 触碰子集给 `revenue_forecast.py` 下界 **73% ≥ 60** 且**新语句 0 miss**（缺行全为 `main()` 既有行）；全量只会更高（覆盖单调）。本机 **coverage 子进程钩子实测未生效**（子进程 0 数据）→ 已用 in-process 单元守卫兜底，见 decision §3。

## 4. 复审入口（建议顺序）

`oracle.sha256` 复算 → `binding.json` + `pins_freeze.txt` 抽 3 pin → `decision.md §1` 机制 10 行逐行复核（重点：⑤⑥ 是否真支撑「非源码、非断言」）→ `evidence\rgm\{red,green,mut1,mut2}\probe.json` 四份判据 → `family_compare.txt` → `changes.diff` apply-check → `production_zero_write_after.txt` → 回 `handoff §3` 逐条认领 unproven。

---

## review_round_2

- **status**：`review_pending`（r2 修复轮已交付、**待复审**）
- **implementer_signed**：`false` —— 本轮**不自签 ACCEPT**；无任何 reviewer/owner 签字；`oracle.md` 一字未改（收尾复算 `7fecfaea02f62b3740122a2c79ff5f7194bdd29505696cb0e8c38cdce1cb8be8` == `oracle.sha256` == `binding.json.oracle_sha256`）
- **裁决来源**：本 attempt `reviewer_report.md`（26073 B，sha `9941660588641a31a22449365982392a28f4fc5b2451a69ca8587f38ad3074e8`，VERDICT: changes_required）—— 本轮**只读**，字节复算一致
- **前缀自证**：本节之前 `handoff.md` = **7077 B**、sha256=`14dc9b6272f839ec9ad415ed44709398bfb064efa8087642436b4c4ec7f40f4d`（r1 `DELIVERABLES.sha256` 行）；追加后前 7077 B 逐字节重算同值 ⇒ `prefix_bytes_preserved=true`（`harness\prefix_selfcheck_r2.py` → `evidence\rgm2\prefix_selfcheck_r2.json`）。r1 既有字节面（`decision.md` / `commands.md` / `binding.json` / `DELIVERABLES.sha256` / `evidence/**`）**全部只追加或零改**，逐项复核见该产物。
- **交付形态（r2）**：RF 生产零写（`git diff HEAD --name-only` 非 `.planning` **=0**）；`changes.diff` 重生成 = **10114 B**、sha **`d1a79376c518eab300400c54badf91e141ed4b50ae0623a6fefe52900ad2856d`**、恰 2 文件、**r1/r2 各一 hunk**；iso CLI `4e6b64a7…` → **`405fec6d7ea23324bd671e144caa994889e076104d67560bc3b1d0f830599bda`**；产品测试 8 → **9** 条

### F-01（P1）关闭证据

| 面 | 修前（iso `4e6b64a7`） | 修后（iso `405fec6d…`） | 证据 |
|---|---|---|---|
| `--help` × 断读端 raw rc | **120** | **2** | `evidence\rgm2\red\probe.json` / `evidence\rgm2\green\probe.json` |
| `-h` × 断读端 raw rc | **120** | **2** | 同上 |
| stderr 关键行 | `Exception ignored on flushing sys.stdout:` + `OSError: [Errno 22] Invalid argument`（**无产品文本** ⇒ 包装未执行） | `error: stdout flush failed: [Errno 22] Invalid argument`，且 **`Exception ignored` 0 命中** | 同上 |
| 新产品测试 `test_help_with_broken_stdout_exits_2_with_preserved_error_text` | **1 failed, 8 passed**（`assert 120 == 2`） | **9 passed**（r1 的 8 条 = **8/0**） | `evidence\rgm2\pytest_r2\red_newtest_r1_state.txt` / `green_r2_state.txt` / `green_final_r2_state.txt` |
| 其它 F12 臂（validate/version/usage × 断读端） | 2 / 2 / 2（r1 已修，未被 r2 破坏） | 2 / 2 / 2 | 各 `probe.json` |
| 正常矩阵（5 读端臂 + usage） | 0/0/0/0/2、stdout 形状全对 | **逐值相同** | 同上 |
| 变异 | MUT-A 回退包装 → **120**（探针红、测试 1F/8P）；MUT-B 只 catch 不换流 → **120**（测试 3F/6P）；MUT-C 只中和不 catch → **0 且无产品文本**（测试 4F/5P） | 终态 `restore` 复探 **GREEN** + **9 passed** | `evidence\rgm2\{mut1_revertwrap,mut2_nocatch,mut3_neutralonly}\` |
| ruff / 棘轮 | — | `All checks passed!`（rc 0）／`max=18 == frozen 18`（rc 0） | `evidence\rgm2\ruff_r2.txt`、`ratchet_r2.txt` |
| 生产 pristine（只读对照） | `--help` × 断读端仍 **120**（**非本卡回归，待合并 `changes.diff` 后修复**） | — | commands R2-C3 |

**处置路线**：复审建议第 **1** 条路（扩包装覆盖 `main()` 内 `SystemExit` + 补 1 条 `--help`×断管 产品测试）；第 2 条路（owner 出 oracle 范围豁免）**未走、未申请**——本卡**不改冻结 oracle、不改冻结期望**，也不代 owner 裁。

### F-02 … F-08 处置表

| 编号 | 级别 | 处置（结论） | 证据 |
|---|---|---|---|
| **F-02** | P3 | **已处置（erratum，未改证据字节）**：Q3 的 rc=0 属 `coverage run -m pytest`（测试执行）；证据末行 `fail-under=84` 属 `coverage report` 步，本轮实测该步 **rc=2**（`--fail-under=0` 对照 **rc=0**）。适用域：`fail_under=84` 是仓库**全局门**，与本卡 `run_coverage_gates.py` **单模块 ≥60% 门**不同口径 | `evidence\rgm2\coverage_rc_probe_r2.txt`；commands R2-步骤6 |
| **F-03** | P3 | **已登记 `pin_drift`，不回写 pin 表**：19 pins 复算 **10 MATCH / 9 DRIFT**（与复审同一分割）；register×5 `227689/2e9f3a40…`→**`314823/e3b24ef1…`**（复审时点 `270337/33c7505e…`，活文档继续外部追加），**全部钉行逐字仍在**、非空行现 **+3**；closure decision×3 `23413/a68ed77f…`→**`26557/5e275968…`**，L64/93/94/104 **原行号原字**；`iso_cli_before` `2a2dfede…`→**`405fec6d…`**（=r2 交付态，pin 语义为「修前」，**预期内**） | `evidence\rgm2\pins_r2.json` |
| **F-04** | P3 | **已追加时序更正**：C1b 产物 `grep_120_and_emitter.txt` mtime **00:04:17** 晚于 `oracle.sha256` **23:50:41** ⇒ 该行「冻结之前」标注**与 mtime 不符**；按 mtime 登记为**冻结后产物**；「冻结前已跑」**不可证、不作断言**（C1 `mech_cases.json` 23:40:19 确在冻结前） | commands R2-步骤6 F-04 行 |
| **F-05** | P3 | **已核实并更正表述**：`report_SA-DEFECT.md` **字节从未改动**（sha `374a57700884a6ee4…` 26047 B == pin，L165 原文仍是「断言在返回后开火」）；r1 handoff §1「被更正」措辞不实 → 更正为「**以本卡 oracle §5 / decision §1 承载更正；封存件字节不动**」（与登记册口径一致） | 本节 + commands R2-步骤6 F-05 行 |
| **F-06** | P3 | **已补列**：`decision.md §5` 家族 grep 行号清单补 **`test_publication_pipeline.py:315`**（注释行）；87/332/360 不变，**文件集合仍恰 8 个**，G-4 不受影响 | 生产 `tests\` 同正则复测 15 行/8 文件（commands R2-步骤6 F-06 行） |
| **F-07** | P3 | **已追加披露**：r1 首轮 RED probe 字节被末轮同名覆盖未留存（`probe_run1_after_fix.json` 00:14:27 早于 `red\probe.json` 00:32:41）；**r2 起规则 = 同名覆盖前先改名归档**（本轮 try1 已按此归档） | commands R2-步骤6 F-07 行、`evidence\rgm2\failed_try1_expect_table\` |
| **F-08** | P3 | **已补臂**：新增 MUT-C「只中和不 catch」→ `--help/-h/validate/version` 断管 **rc=0、无产品文本**（∈{0,2} 但违反 G-2），产品测试 **4F/5P** 打红；**冻结 M-1/M-2 与 `oracle.md §4` 一字未改**，catch 半非空转证据 = 产品测试 **+** 该臂 | `evidence\rgm2\mut3_neutralonly\`、decision §7.3 |

### blocked_by / unverified

- **`blocked_by` = `[]`**（无阻断项；本轮 P1 已修并三证、P3 七条全部处置完毕）
- **unverified（如实携带）**：
  1. 家族 8 文件回归 **r2 未重跑**（`tempfile`/`tmp_path` 在本会话沙箱被拒，与复审 §4.1 同源）；r1 的 64/48 字节级证据照录，另加本轮静态不相交论证（家族 0 命中 `--help`/`-h`）。
  2. 单模块覆盖门 **≥60% r2 未复测**（直调 `main()` 的测试本会话不可运行）；r1 的 73% 既未推翻也未复证；本轮子集观测 96/60/38%（默认配置、子集不同）**与 73% 不可比、不作门结论**；算术上界估计≈69%（**估计非实测**）。
  3. Linux/macOS 断管码值未测；`--help`/`-h` 之外的 `SystemExit`-in-`main` 组合未穷举；stderr 汇断管未构造（oracle §6 非目标）。
  4. `probe_f12.py:65` 是否随修本体 = 父裁（r1 carried 项，本轮不裁定）。
- **本轮未做**：未改 `oracle.md`/`oracle.sha256`；未改 r1 复审报告两件；未回写 `binding.json`/`pins_freeze.txt`/`evidence\rgm\**`；未写登记册/`progress.md`/`findings.md`/`task_plan.md`；未把 status 改成 accepted、未代签、未晋升；未执行任何 git 写命令；未联网。
