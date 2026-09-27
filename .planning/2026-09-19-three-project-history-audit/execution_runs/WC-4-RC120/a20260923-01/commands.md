# commands.md — WC-4 = F12-RC120（**无 git**；RF 生产零写；全部在 iso + 本 attempt 内）

**两段式绑定**（与 I-09-A `commands.json` 同口径）：**P0 = 冻结前登记的命令与期望**（写于 oracle 冻结同批，未跑）；**P1 = 实际执行回填**（每条带真实 argv / cwd / 解释器 / raw rc）。失败或被取代的尝试**如实入册、不当证据**。

- 解释器：`C:\Miniconda\python.exe`（3.13.9），子进程一律加 `-B`（不落 pyc）
- 根：`RF = C:\Users\郑曾波\Projects\revenue-forecast`（只读）；`ISO = <attempt>\iso\rf`；`A = <attempt>`（= `.planning\2026-09-19-three-project-history-audit\execution_runs\WC-4-RC120\a20260923-01`）
- 临时：`%TEMP%`（仅 runner 自身临时目录）；证据目录 `$A\evidence\...`（attempt 内，可弃可重建）

## P0 — 预登记（purpose → expected）

| # | 阶段 | 命令（真实 argv 形态，cwd） | expected |
|---|---|---|---|
| C1 | phase0 地面真相（**oracle 冻结前**，如实披露） | `python -B $A\harness\mech_case.py`（cwd=RF） | M0/M1 pipe_noreader=**120**、reader/file=0/2；M2/M3=**2**；M4 pipe_noreader=**120**（catch 不够、必须中和流）——**先于 oracle 冻结跑**，属「复核地面真相」非 RGM |
| C2 | RED | `python -B $A\harness\probe_wc4.py --stage red`（cwd=RF） | F12 臂 **120**（域外，红成立）+ 基线 A/C=0 + 正常矩阵全等于期望 |
| C3 | RED（产品测试） | `python -m pytest $ISO\tests\test_stdout_flush_exit_domain.py -q -p no:cacheprovider`（cwd=$ISO） | **1 failed**（观察 120 vs 期望 2）+ 2 passed ⇒ 真红 |
| C4 | REGRESSION before | `python -m pytest <8 个家族文件> -q -p no:cacheprovider`（cwd=$ISO，**未修**） | 记录 before 基线（passed/failed/skip/xfail 计数） |
| C5 | GREEN | 同 C2 `--stage green` | F12 臂 **2**、stderr 含产品错误文本、无 `Exception ignored`、基线/正常矩阵不变 |
| C6 | GREEN（产品测试） | 同 C3 | **全 passed** |
| C7 | REGRESSION after | 同 C4（**已修**） | after == before 逐文件全等，无 skip/xfail |
| C8 | MUTATION-1（整体回退） | 撤归一化 → 同 C2 `--stage mut1` + 同 C3 | F12=**120** 复现 + 产品测试 **failed** ⇒ 变异被抓 |
| C9 | MUTATION-2（半回退：留 catch、去流中和） | 改 iso 源 → 同 C2 `--stage mut2` + 同 C3 | F12 仍 **120** + 测试 failed ⇒ 两半都承重 |
| C10 | 终态复原 | 恢复 iso 修复态 → 同 C6 | 全 passed（iso 终态=交付态） |
| C11 | 交付 diff | `python -B $A\harness\make_diff.py`（比对 RF 生产原字节 vs 修复后字节） | `changes.diff` 恰 1 产品文件（+1 新测试文件），生产树 sha 前后不变 |
| C12 | 生产零写复核 | 复算 `RF\scripts\revenue_forecast.py` 等 pin 的 sha256 | 与 binding `prod_cli_before` 完全相同 |

**家族（grep 依据，见 decision §5）**：`tests/test_industry_end_to_end.py`、`tests/test_publication_pipeline.py`、`tests/test_verbose_validation.py`、`tests/test_zr701_f1_draft_formal.py`、`tests/test_zr704_validate_only_gate.py`、`tests/test_zr710_publication_txn.py`、`tests/test_zr803_chaos_recovery.py`、`tests/test_zr804_platform_shape.py`

## P1 — 实际执行回填（append-only）

> 状态记法：✅=按期望达成；❌=失败尝试（**如实入册、不作证据**）；⤴=被后继取代。
> 家族日志由 PowerShell `*>` 重定向写出（UTF-16），由 `harness\compare_family.py` 解码比对。

### phase0 — 地面真相复核（**oracle 冻结之前**，如实披露）

| # | 命令（真实 argv，cwd=RF 除非注明） | raw rc | 结果 / 证据 |
|---|---|---|---|
| C1 | `python -B <A>\harness\mech_case.py` | 0 | M0(无 RF 代码) pipe_noreader=**120** / reader=0 / file=0；M1(`exit(2)` 请求) pipe_noreader=**120**；M2/M3(修复形态) =**2** 且带错误文本、无 `Exception ignored`；M4(只 catch 不中和流)=**120** ⇒ 形态判据先于冻结拿到。`evidence\mech\mech_cases.json`（sha `919a3448…`） |
| C1b | 内联 pwsh：`Select-String scripts\*.py -Pattern '120'` + 线性搜索 `python313.dll` 中字面量 `Exception ignored on flushing sys.stdout` | 0 | 产品源 120 全部是 FC-120x 需求号、**退出码形 0 命中**；该报错串在 `python313.dll` byte offset **5921656** 命中（dll sha `d97a9810…`）⇒ **解释器自报**。`evidence\mech\grep_120_and_emitter.txt` |
| C2-build | `robocopy RF <A>\iso\rf /MIR /XD .git .planning <caches>` | 1（=成功） | iso 镜像 26.29 MB；iso CLI sha `2a2dfede7941…` == 生产 pin |

### 冻结（跑 RGM 之前）

- `oracle.md` sha256 = `7fecfaea02f62b3740122a2c79ff5f7194bdd29505696cb0e8c38cdce1cb8be8`（收尾复算**同值**）
- `binding.json` sha256 = `caca43e80e0692216a146fb3d4f2a81ff4904954aebf8c71233285f43c8220db`（19 pins，逐行原文在 `evidence\pins_freeze.txt` sha `522cd765…`）

### RGM

| # | 命令 | raw rc | 结果 / 证据 |
|---|---|---|---|
| ❌C2-try1 | `python -B <A>\harness\probe_wc4.py --stage red` | 1 | **harness 缺陷**（`NameError: base`，判据段引用了不存在的变量）——量已采但未落判；修 harness 后重跑；**不作证据** |
| ✅C2 | 同上（harness 修复后） | **0** | verdict `RED_REPRODUCED_OUT_OF_DOMAIN_120`：F12 臂 **rc=120**（∉{0,2}）、`Exception ignored on flushing sys.stdout` 在、基线 A/C=0/0、正常矩阵全对。`evidence\rgm\red\probe.json` + `red_probe_console.txt` |
| ✅C3 | `python -m pytest <A>\iso\rf\tests\test_stdout_flush_exit_domain.py -q -p no:cacheprovider`（cwd=RF） | **1** | **1 failed, 2 passed**（失败断言原文 `got 120`）⇒ 真红。`evidence\rgm\red_pytest_newtest.txt` |
| ⤴C4-try1 | `python -m pytest <8 家族文件> -q -p no:cacheprovider`（iso 无 sibling，未修） | 1 | 2 failed / 62 passed：`test_zr803…test_lock_held_write_transaction_does_not_block_read_journey` 与 `test_zr804…test_case_swapped_project_dir_runs_identical_journey`，断言原文均为 **filing-fetch script not found … `iso\filing-fetch\scripts\fetch_filing.py`（rc3 vs 0）** = **iso 缺同级 sibling 技能检出**的环境红，与本卡无关。**原日志被 try2 同名覆盖（披露）**，失败摘要以本行为准（取自该次控制台尾部） |
| ✅C4 | `robocopy Projects\filing-fetch <A>\iso\filing-fetch /MIR …`（code 1）→ 同上 pytest（iso 未修） | **0** | **64 passed, 48 subtests passed**（199.76s；0 skip/xfail）= before 基线。`evidence\rgm\family_before_raw.txt` |
| ✅C5 | `python -B <A>\harness\apply_fix.py apply` → `probe_wc4.py --stage green` | 0 / **0** | iso CLI `2a2dfede…→4e6b64a7…`(state=fixed)；verdict `GREEN_IN_DOMAIN_2_WITH_ERROR_TEXT`：F12=**2**、产品错误文本在、`Exception ignored` **消失**、基线/矩阵不变。`evidence\rgm\green\probe_run1_after_fix.json` + `green_probe_console.txt` |
| ✅C6 | 同 C3 | **0** | **3 passed**（4.95s）。`evidence\rgm\green_pytest_newtest.txt` |
| ✅C7 | 同 C4（已修） | **0** | **64 passed, 48 subtests passed**（184.42s）；`compare_family` 逐行 diff = **仅 wall-clock 两行不同**，计数/集合全等、0 skip/xfail。`evidence\rgm\family_after_raw.txt` + `family_compare.txt` |
| ✅C8 | `apply_fix.py revert`（sha 回 `2a2dfede…`）→ `probe_wc4.py --stage mut1` → 同 C3 | 0 / **0** / **1** | **MUTATION-1 捕获**：F12=**120** 复现、产品测试 1 failed/2 passed。`evidence\rgm\mut1\probe.json`、`mut1_probe_console.txt`、`mut1_pytest_newtest.txt` |
| ✅C9 | `apply_fix.py apply` → `apply_fix.py mutate2`（sha `347400d6…`）→ `probe_wc4.py --stage mut2` → 同 C3 | 0 / **0** / **1** | **MUTATION-2 捕获**：产品错误文本**在**、但 rc 仍 **120** ⇒ catch 半与中和半**都承重**；测试 1 failed。`evidence\rgm\mut2\…` |
| ❌C10-try1 | `apply_fix.py apply`（从 mutate2 态回 fixed）→ `probe --stage green` → 同 C3 | **1 / 1** | **回退未落地**：字符串手术锚失败（stderr `mutate2 -> fixed patch anchor failed`），实跑仍是对变异体 ⇒ 判 `GREEN_NOT_MET`（F12=120）。**不作证据**，产物改名归档 `*_failed_mutant_leftover*`；harness 改为「从 pristine 快照重建」 |
| ✅C10 | `apply_fix.py apply`（修后）→ `status` → `probe --stage green` → 同 C3 | 0 / **0** / **0** | iso 终态=fixed（sha `4e6b64a7…`）；终版 GREEN：F12=**2**、文本在、无 `Exception ignored`、基线 0/0、矩阵全对；产品测试 **3 passed**。`evidence\rgm\green\probe.json`、`green_probe_final_console.txt`、`green_pytest_final.txt` |
| ✅C11 | `python -B <A>\harness\make_diff.py` → `python -B <A>\harness\verify_diff.py` | 0 / **0** | `changes.diff` 5015 B（sha `c7353fd4…`）= 恰 2 文件；`VERIFY_DIFF_OK`（重算 unified diff 逐字节命中）。生产 CLI sha 复算 `2a2dfede…`（== pin） |
| ✅C12 | `production_zero_write_before.txt` vs `production_zero_write_after.txt` | — | `scripts` 树 sha `d29e761d…`、`tests` 树 sha `a0d7667c…` **前后相同**；新测试**不在**生产树 ⇒ **生产零写** |
| ✅Q1 | `ruff check <iso fixed cli> <iso new test>`（ruff 0.15.18=CI 钉版） | **0** | `All checks passed!`。`evidence\rgm\ruff_fixed_files.txt` |

### 产品测试扩充（v2）与重跑（append-only 续）

> **动机（如实）**：本机 coverage 的 **subprocess 钩子未生效**（子进程 CLI 未产出 coverage 数据——subset 实测 `main()` 体 0 覆盖），若新增 14 条语句只靠子进程覆盖，`tools/run_coverage_gates.py` 的 `scripts/revenue_forecast.py ≥60%` 门有环境依赖风险。故把产品测试**加层为 in-process 单元守卫**（直接驱动 `_finalize_exit_status`/`_neutralize_broken_stream`），使新代码覆盖**不依赖**钩子。原 v1（仅 3 个子进程测试）的证据文件已改名保留 `*_v1_subprocess_only.txt`。

| # | 命令 | raw rc | 结果 / 证据 |
|---|---|---|---|
| ✅C3b | 同 C3（**v2 测试**，iso 未修） | **1** | **6 failed, 2 passed**——1 个端到端（`got 120`）+ 5 个 in-process（helper 不存在）；通过的 2 个=基线送达与 usage 路径。`evidence\rgm\red_pytest_newtest.txt` |
| ✅C6b | 同 C3（v2，iso 已修） | **0** | **8 passed**（run1 与终版各一次）。`green_pytest_newtest.txt`、`green_pytest_final.txt` |
| ✅C8b | 同 C8（v2：revert → probe mut1 → pytest） | 0 / **0** / **1** | probe F12=**120**；测试 **6 failed, 2 passed**（与 C3b 同构=字节同 pristine ⇒ RED 与 MUT-1 同态，如实注明）。`mut1_probe_console.txt`、`mut1_pytest_newtest.txt` |
| ✅C9b | 同 C9（v2：apply→mutate2→probe→pytest） | 0 / **0** / **1** | probe：文本**在**、F12 仍 **120**；测试 **2 failed, 6 passed**——失败的恰是两条「半承重」断言（端到端 120、`assert sys.stdout is not broken`）。`mut2_probe_console.txt`、`mut2_pytest_newtest.txt` |
| ✅C10b | 终版：`apply_fix.py apply` → `status` → `probe --stage green` → 同 C3 | 0 / **0** / **0** | iso 终态 `4e6b64a7…`=fixed；F12=**2**、文本在、无 `Exception ignored`、基线 0/0、矩阵全对；**8 passed** |
| ✅C11b | `make_diff.py` → `verify_diff.py` | 0 / **0** | `changes.diff` **8306 B**（sha `f0a01489a01b7200…`）；`VERIFY_DIFF_OK`；新测试 sha `5b8e8a3fc1ebf5fb…`（6192 B） |
| ✅C12b | 终版零写复算（含全量 `scripts`/`tests` 树 sha） | — | `scripts` 树 `d29e761d…`、`tests` 树 `a0d7667c…` **与开工时相同**；生产无新测试文件。`production_zero_write_after.txt` |
| ✅Q2a | `python -m pytest <iso>\tools\tests\test_complexity_ratchet.py -q -p no:cacheprovider` | **1** | **2 failed，但 iso 与生产逐条同红**（`analysis/confidence.py max 32>23`、`model_extensions.py max 27>10`）⇒ **仓库既有红**（与本卡无关，且循环先在 confidence.py 断言、根本走不到本卡文件）。原失败取证 `ratchet_iso_failure.txt` |
| ✅Q2b | `python -B <A>\harness\check_ratchet_own_file.py`（与门**同算法**逐文件测） | **0** | `revenue_forecast.py max=18（worst=main:18）== frozen 18`——iso fixed / iso pristine / 生产**三者同值** ⇒ 本卡**未加重**复杂度棘轮（`OWN_FILE_RATCHET_OK`） |
| ✅Q3 | coverage subset（`COVERAGE_PROCESS_START` + `coverage run -m pytest` 5 个 CLI 触碰测试 + 新测试，cwd=iso） | 0 | `scripts/revenue_forecast.py` **90 stmts / 20 miss / 73% ≥ 门 60%**；缺行全在 `main()`（73-100,102,106,117-122，均为既有行），**本卡新增语句 0 miss** ⇒ 子集即达门、全量套件只会更高（覆盖单调）。`coverage_subset_fixed.txt` |
| ✅C7b | 同 C4（**终版 iso 树**，含 v2 新测试文件在盘、cli=4e6b64a7…） | **0** | **64 passed, 48 subtests passed**（180.48s）；`compare_family family_before vs family_final` = **仅 wall-clock 两行不同**。`family_final_raw.txt`、`family_compare.txt`（旧对比留档 `family_compare_v1testfile.txt`） |

**最终 iso 终态**：`state=fixed`、`cli_sha256=4e6b64a789b97f30daf5def474bcd5a1d19cbc45b555e554b23fb8ecafe9e977`；**oracle 收尾复算**=`7fecfaea02f62b3740122a2c79ff5f7194bdd29505696cb0e8c38cdce1cb8be8`（与冻结一致）。


---

## P1-R2 — 修复轮 r2（针对 r1 复审 `reviewer_report.md`，append-only 续）

**前缀自证**：本节之前的 `commands.md` 共 **13251 B**、sha256=`bde20daace862f4f080793cb44697a23ce230086cce5464ed65d6b5de4aa7eae`（= r1 `DELIVERABLES.sha256` 行）；追加后文件的**前 13251 B 逐字节重算 sha 同值** ⇒ `prefix_bytes_preserved=true`（复算脚本 `harness\prefix_selfcheck_r2.py`，产物 `evidence\rgm2\prefix_selfcheck_r2.json`）。r1 复审报告 `reviewer_report.md`（26073 B，sha `9941660588641a31a22449365982392a28f4fc5b2451a69ca8587f38ad3074e8`）与 `reviewer_report.sha256` 本轮**只读未改**（sha 复算见同产物）。

**r2 唯一裁决来源**：`reviewer_report.md`（VERDICT: changes_required；F-01 = P1、F-02…F-08 = P3）。**oracle 一字未改**：`oracle.md` 收尾复算仍 `7fecfaea…`（== `oracle.sha256` == `binding.json.oracle_sha256`），F-01 按复审建议第 1 条路「把修复做到满足 O-1」处置，**不改冻结期望**；第 2 条路（owner 出 oracle 范围豁免）**本卡不走**（owner 未裁）。

**r2 新增 harness（全部新建，不改 r1 harness 语义）**：`probe_help_r2.py`（F-01 探针，输出只落 `evidence\rgm2\`）、`run_pytest_r2.py`、`capture_checks_r2.py`、`apply_fix_r2.py`、`verify_pins_r2.py`、`coverage_rc_probe_r2.py`、`coverage_subset_r2.py`、`prefix_selfcheck_r2.py`。

### R2-步骤1 · 复审发现清单（逐条抄入工作清单）

| 编号 | 级别 | 一句话 | 本轮处置（详 §R2-P3） |
|---|---|---|---|
| **F-01** | **P1** | iso `4e6b64a7` 下 `--help`/`-h` × 断读端管道 **raw rc=120**、stderr 仅 CPython `Exception ignored on flushing sys.stdout`、**无产品文本** ⇒ `_finalize_exit_status` 未执行；根因=argparse 在 **`main()` 内部** `raise SystemExit(0)`，入口包装够不到；r1 handoff §3.3「该路径 stdout 为空」为推理且**被证伪** | **修**（扩包装）+ 补 1 条产品测试 + 红/绿/三变异全证 |
| **F-02** | P3 | commands Q3 覆盖 rc 记 0，证据末行 `Coverage failure: total of 73 is less than fail-under=84` | 本轮实测各步 rc、写口径与适用域 erratum（**不改证据字节**） |
| **F-03** | P3 | binding 19 pins 中 9 DRIFT；register 12 钉行整体漂移、逐字未改 | 复算 19 pins + 逐行定位，登记 `pin_drift`（**不回写 pin 表**） |
| **F-04** | P3 | C1b 被列「冻结之前」，但 `grep_120_and_emitter.txt` mtime `00:04:17` 晚于 `oracle.sha256` `23:50:41` | 追加时序更正声明 |
| **F-05** | P3 | handoff「`report_SA-DEFECT.md:165` 被更正」与 pin MATCH 矛盾 | 核实真相（文件字节未动），更正表述 |
| **F-06** | P3 | decision §5 家族 grep 漏列 `test_publication_pipeline.py:315`（文件集合仍恰 8） | 追加补列 |
| **F-07** | P3 | 首轮 RED probe 字节被末轮同名覆盖、未单独披露 | 追加披露（r2 起同名覆盖一律先改名归档） |
| **F-08** | P3 | 变异矩阵缺「只中和不 catch」臂 | **本轮补该臂**（M-1/M-2 冻结判据不动） |

### R2-步骤2 · 补红（F-01 修前实测）

| # | 命令（cwd=ISO 除注明） | raw rc | 结果 / 证据 |
|---|---|---|---|
| ✅R2-C1 | `python -B <A>\harness\probe_help_r2.py --stage red`（iso=r1 交付态 `4e6b64a7`） | 探针 **0** | verdict `RED_F01_HELP_STILL_RAW_120_NO_PRODUCT_TEXT`：`--help` **120**、`-h` **120**；stderr 逐字两行 `Exception ignored on flushing sys.stdout:` / `OSError: [Errno 22] Invalid argument`，**无** `stdout flush failed`；r1 已修的返回值臂 validate=2、version=2、usage=2；正常臂 0/0/0/0/2 全对。`evidence\rgm2\red\probe.json` |
| ❌R2-C1-try1 | 同上（探针期望表写错：把 r1 已修的返回值臂也期望成 120） | 1 | 判 `RED_NOT_REPRODUCED`（**harness 缺陷，量对判错**）；产物**改名归档** `evidence\rgm2\failed_try1_expect_table\probe.json`，**不作证据**（吸取 F-07 教训：不覆盖、先归档） |
| ✅R2-C2 | `python -B <A>\harness\run_pytest_r2.py --name red_newtest_r1_state -- tests\test_stdout_flush_exit_domain.py`（**新测试先落、代码未修**） | **1** | **1 failed, 8 passed**，失败原文 `assert 120 == 2`（`test_help_with_broken_stdout_exits_2_with_preserved_error_text`）⇒ 新判据真红。`evidence\rgm2\pytest_r2\red_newtest_r1_state.txt` |
| ✅R2-C3 | 生产 pristine `python -B <prod>\scripts\revenue_forecast.py --help`（stdout=断读端管道，**只读执行**） | **120** | stderr 同样只有 `Exception ignored…`/`OSError: [Errno 22]` ⇒ **非本卡回归，且待 `changes.diff` 合并后才修**（生产树本轮零写，见 R2-C12） |

### R2-步骤3-4 · 修 + 绿

| # | 命令 | raw rc | 结果 / 证据 |
|---|---|---|---|
| ✅R2-C4 | 手术式编辑**仅** `iso\rf\scripts\revenue_forecast.py` 尾部 `if __name__ == "__main__":` 块（`try: _exit_code = main()` / `except SystemExit as _system_exit:` 取码（int→原值、None→0、其余→2）/ `raise SystemExit(_finalize_exit_status(_exit_code))`） | — | iso sha `4e6b64a789b97f30…` → **`405fec6d7ea23324bd671e144caa994889e076104d67560bc3b1d0f830599bda`**（快照 `evidence\rgm2\cli_r2_state.py`）；r1 交付态快照 `evidence\rgm2\cli_r1_state.py`（`4e6b64a7…`） |
| ✅R2-C5 | `probe_help_r2.py --stage green` | **0** | verdict `GREEN_F01_HELP_IN_DOMAIN_2_WITH_ERROR_TEXT`：`--help` **2**、`-h` **2**；stderr 逐字 `error: stdout flush failed: [Errno 22] Invalid argument`；**无** `Exception ignored`；validate=2、version=2、usage=2；正常臂 0/0/0/0/2、stdout 形状全对。`evidence\rgm2\green\probe.json`（首轮=`green\probe_run1.json`，变异往返后复跑=终版，两次 iso sha 同 `405fec6d…`） |
| ✅R2-C6 | `run_pytest_r2.py --name green_r2_state` / `--name green_final_r2_state`（同 r1 的 8 条 + 新增 1 条） | **0 / 0** | **9 passed**（其中 **r1 的 8 条 = 8 passed / 0 failed**，新条 1/1）。`evidence\rgm2\pytest_r2\green_r2_state.txt`、`green_final_r2_state.txt` |
| ✅R2-C7 | `capture_checks_r2.py`（`ruff 0.15.18 check` 两交付文件） | **0** | `All checks passed!`。`evidence\rgm2\ruff_r2.txt` |
| ✅R2-C8 | 同脚本 `check_ratchet_own_file.py`（与门同算法） | **0** | iso fixed / iso pristine / 生产 **三者 max=18（worst=main:18）== frozen 18**，`OWN_FILE_RATCHET_OK` ⇒ r2 未加重棘轮（`if __name__` 块为模块级语句，非 `FunctionDef`，不入该棘轮面）。`evidence\rgm2\ratchet_r2.txt` |

**G-2 关键行（F-01 修后）**：`error: stdout flush failed: [Errno 22] Invalid argument`；`Exception ignored on flushing sys.stdout` **0 命中**。

### R2-步骤5 · 变异（三个臂，逐臂 raw rc + 产品测试）

| 臂 | 切换命令（`apply_fix_r2.py`） | iso sha | 探针（`--stage`） | 关键 raw rc | 产品测试 | 判定 |
|---|---|---|---|---|---|---|
| **MUT-A（复审建议变异①：回退包装，仍只包 `main()` 外）** | `revert_wrap`（回退后**与 r1 快照逐字节相等**，harness 内置断言） | `4e6b64a7…`（=r1 交付态） | `mut1_revertwrap` | **`--help`=120**、`-h`=120、validate=2、version=2、usage=2；正常臂全对 | **1 failed, 8 passed**（新判据红，`assert 120 == 2`） | **红 ⇒ 新判据承重** |
| **MUT-B（复审建议变异②：只 catch 不换流 = r1 oracle M-2，在 r2 包装上重跑）** | `mut2` | `99fc716ad9ef6ce80f5e2e50062027f2e2e0354a432774034ad8c8a6d6891153` | `mut2_nocatch` | **`--help`=120**（**产品文本在** + **`Exception ignored` 也在**）、`-h`=120、validate=**120**、version=**120**、usage=2 | **3 failed, 6 passed**（端到端 120、`assert sys.stdout is not broken`、新 `--help` 条） | **红 ⇒ 中和半承重** |
| **MUT-C（F-08 补臂：只中和不 catch）** | `mut3` | `4f9d78034b46e8054ef9807dafc38f9728737269f2be5c6eeca505012ddbd95b` | `mut3_neutralonly` | **`--help`=0、`-h`=0、validate=0、version=0**（仍 ∈{0,2}）、usage=2；**无产品文本**、无 `Exception ignored` ⇒ **违反 G-2 fail-closed/informative** | **4 failed, 5 passed**（端到端 rc≠2+无文本、`normalizes_flush_failure_to_2`、`survives_broken_stderr`、新 `--help` 条） | **红 ⇒ catch 半非空转**（F-08 关闭） |
| 终态复原 | `restore` → `status` | **`405fec6d…` state=r2** | `green`（复跑） | `--help`=2、文本在、无 `Exception ignored`、矩阵全对 | **9 passed** | 交付态复证 |

变异证据：`evidence\rgm2\{mut1_revertwrap,mut2_nocatch,mut3_neutralonly}\probe.json`、`evidence\rgm2\pytest_r2\{mut1_revertwrap,mut2_nocatch,mut3_neutralonly}.txt`。**三臂均只动 iso**（`apply_fix_r2.py` 只写 iso CLI），r1 `evidence\rgm/**` 与生产树零改。

### R2-步骤7 · `changes.diff` 重生成

| # | 命令 | raw rc | 结果 / 证据 |
|---|---|---|---|
| ✅R2-C9 | `python -B <A>\harness\make_diff.py` → `verify_diff.py` | 0 / **0** | `changes.diff` **10114 B**、sha256 **`d1a79376c518eab300400c54badf91e141ed4b50ae0623a6fefe52900ad2856d`**；`VERIFY_DIFF_OK`（重算与盘上逐字节同）。**恰 2 文件**：`scripts/revenue_forecast.py` `2a2dfede…`→`405fec6d…`（5333→7647 B）+ `tests/test_stdout_flush_exit_domain.py` 新增（7270 B、195 行、9 个 `def test_`、sha `083b92a535bf43f0…`） |
| ✅R2-C10 | 比对 hunks | — | **CLI 恰 2 hunk**：`@@ -125,0 +126,44 @@`（**r1 修复**：`_neutralize_broken_stream` + `_finalize_exit_status`）与 `@@ -127 +171,15 @@`（**r2 修复**：入口扩到 `main()` 内 `SystemExit`）；新测试 `@@ -0,0 +1,195 @@` ⇒ **r1/r2 各一 hunk、r2 增量可辨** |
| ✅R2-C10b | 格式变更如实登记 | — | r1 的 diff 用 `difflib.unified_diff(..., n=3)`（`@@ -123,5 +123,49 @@`）；本轮改 **`n=0`**——否则 r1/r2 两处改动只隔 1 行未变行（`if __name__ == "__main__":`），`n=3` 上下文会把两块**并成一个 hunk**，无法「各一 hunk」。r1 旧 diff（8306 B，sha `f0a01489a01b7200…`）**预像归档** `evidence\rgm2\changes_r1_preimage.diff` |
| ✅R2-C11 | 生产零写复核 | — | `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` **= 0**（见 §R2-边界）；生产 CLI sha 仍 `2a2dfede…`== pin `prod_cli_before`；新测试在生产树 `Test-Path=False` |

### R2-步骤6 · P3 逐条处置（F-02…F-08）

| # | 处置（全部**只追加、不改既有证据字节**） | 实测/证据 |
|---|---|---|
| **F-02** | **登记口径冲突与适用域（erratum，不改 Q3 行、不改 `coverage_subset_fixed.txt`）**：Q3 的 `rc=0` 属 **`coverage run -m pytest`（测试执行步）**；证据末行 `Coverage failure: total of 73 is less than fail-under=84` 属随后的 **`coverage report` 步**，该步**本轮实测 raw rc=2**。适用域：`.coveragerc [report] fail_under=84` 是**仓库全局门**（全量套件面），与本卡判据 **`tools/run_coverage_gates.py` 的 `scripts/revenue_forecast.py ≥60%` 单模块门**不是同一口径；单模块门由子集 73% 打下界 | `evidence\rgm2\coverage_rc_probe_r2.txt`：`coverage run`=**0**、`coverage report`(fail_under=84)=**2**、`coverage report --fail-under=0`=**0**；`.coveragerc` 现盘 `fail_under = 84` 只读复核 |
| **F-03** | **登记 `pin_drift`（旧/新/成因/逐字未改），不回写 pin 表**：19 pins 复算 = **10 MATCH / 9 DRIFT**，与复审**同一分割**。① `REMEDIATION_REGISTER.md`×5：`227689 B/2e9f3a40…` → **`314823 B/e3b24ef156b18514…`**（复审时点为 `270337 B/33c7505e…`，**活文档在复审后又外部追加**）——5 个 pin 的**全部钉行逐字仍在盘**（`verbatim_all_found=true`），非空钉行现盘行号较冻结 **+3**（复审时点为 +1；空行不计位移）；② `REGISTRY-CLOSURE/…/decision.md`×3：`23413 B/a68ed77f…` → **`26557 B/5e275968…`**，L64/93/94/104 **原行号原字**（delta=0）；③ `iso_cli_before`×1：`2a2dfede…` → **`405fec6d…`**（=本轮交付态；复审时点为 `4e6b64a7…`）——pin 语义是「修前」，修后必漂，属**预期内**。成因均为**外部活文档追加 / 本卡 iso 状态推进**，**非本卡改写封存件** | `evidence\rgm2\pins_r2.json`（19 pins 逐条 sha/bytes + 钉行逐行定位） |
| **F-04** | **追加更正时序声明**：`commands.md` P1「phase0 —（oracle 冻结之前）」表中 **C1b 行的阶段标注与产物 mtime 不符**——`evidence\mech\grep_120_and_emitter.txt` mtime = **2026-09-24 00:04:17**，晚于 `oracle.sha256`（2026-09-23 23:50:41）约 14 分钟。**如实更正**：C1b 产物按 mtime 属**冻结后写盘**；「冻结前已执行、冻结后重跑留证」这一说法**本卡无独立证据支持，不作断言**（不可证），以 mtime 为准登记为冻结后产物；同表 C1（`mech_cases.json`，23:40:19）确在冻结前 | mtime 复测：`oracle.md 23:50:38` / `oracle.sha256 23:50:41` / `mech_cases.json 23:40:19` / `grep_120_and_emitter.txt 00:04:17` |
| **F-05** | **核实并更正表述**：`handoff.md §1` 表「`report_SA-DEFECT.md:165` 被更正」**措辞不实**——pin `sa_defect_wrong_mechanism` **MATCH**（`26047 B` / `374a57700884a6ee4…` 与冻结同值），L165 原文**至今仍是**「断言在返回后开火」⇒ **封存件字节从未改动**；更正实际只落在**本卡 `oracle.md §5` / `decision.md §1`**（与登记册「封存件不动、oracle §5 冻结」口径一致）。已在 `handoff.md` `## review_round_2` 更正为「以本卡 oracle §5/decision §1 承载更正；封存件字节不动」 | L165 以 UTF-8 逐行读回：`\| F12（断管归一化） \| 断言在返回后开火 \| REG:592 \| …`；sha 复算 `374a5770…` |
| **F-06** | **补列**：decision §5 家族 grep 清单补 `test_publication_pipeline.py:315`（注释行 `# (the subprocess-only pattern left revenue_forecast.py at ~0%).`，含 `revenue_forecast.py` 故被同一正则命中）；decision 已列 87/332/360 不变，**文件集合仍恰 8 个**、G-4 不受影响 | 生产 `tests\` 同正则复测：15 行命中、8 文件；`test_publication_pipeline.py` 命中行 = **87, 315, 332, 360** |
| **F-07** | **追加披露**：r1 首轮 GREEN 的 `evidence\rgm\green\probe_run1_after_fix.json`（mtime **00:14:27**）早于现存 `evidence\rgm\red\probe.json`（**00:32:41**）⇒ **首轮 RED 的 probe 输出被末轮同名覆盖、未单独留存**（`commands.md` 此前只对 C4 明确披露同名覆盖）。本行为正式披露，与 C4/C4-try1 同口径；末轮内部 red<mut1<mut2<green 时序仍自洽、判据内容不受影响。**r2 起规则**：任何同名覆盖前先改名归档（本轮 try1 即按此执行） | mtime 复测：`probe_run1_after_fix.json 00:14:27` < `red\probe.json 00:32:41` |
| **F-08** | **本轮补「只中和不 catch」臂（MUT-C）**：`_finalize_exit_status` 改为「flush 失败→只换流、不报文本、不改 rc」→ 实测 `--help/-h/validate/version` 断管 **raw rc=0**、**无产品文本**、无 `Exception ignored`（仍 ∈{0,2} 但**违反 G-2 fail-closed/informative**），产品测试 **4 failed/5 passed** 抓红。**冻结判据 M-1/M-2 与 `oracle.md §4` 一字未动**；catch 半的非空转证据现在**同时**来自产品测试 `test_finalize_exit_status_normalizes_flush_failure_to_2` 与该变异臂 | `evidence\rgm2\mut3_neutralonly\probe.json`、`evidence\rgm2\pytest_r2\mut3_neutralonly.txt` |

### R2-环境限制（如实携带，与复审 §4 同源）

1. **`tempfile`/`tmp_path` 在本会话沙箱被拒**：`tempfile.mkdtemp()` 后向其中写文件 → `PermissionError(13)`（**纯 python 进程同样复现**，非 pytest 特有）；pytest 的 `--basetemp`/`pytest-of-<user>` 目录同样建得进、进不去。⇒ **家族 8 文件回归本轮无法重跑**（r1 的 64 passed/48 subtests 字节级证据与复审 §4.1 结论照录，本轮未刷新）；`test_publication_pipeline`（3 failed）、`test_verbose_validation`（2 failed）在本会话**不可运行**（均为该 PermissionError，非产品失败）。
2. **产品测试可用跑法**：`run_pytest_r2.py` = `pytest --noconftest` + 显式 `REVENUE_PUBLICATION_REGISTRY`（iso `tests\conftest.py` 唯一会话夹具就是设该环境变量，等价替代；`--noconftest` 只为绕开它对 `tmp_path_factory.mktemp` 的依赖）⇒ 9/9 可跑、判据值与 r1 相同。
3. **单模块覆盖门（≥60%）本轮未复测**：r1 的 73% 依赖 `main()` 体的进程内覆盖（`test_publication_pipeline` 直调 `main()`），该文件在本会话不可运行 ⇒ **登记 unverified**。本轮可运行子集实测（**默认配置，iso 内无 `.coveragerc`**）= `96 stmts / 60 miss / 38%`，missing `27-35,47-52,56-123,177-185`（`177-185` = r2 新增的 `if __name__` 模块级块，仅以脚本方式执行时才可达）——**与 r1 的 73% 不可比**（子集与配置都不同），**不作门结论**；算术上界估计：即使 6 条新语句全 miss，`(79)/(96+18)≈69% ≥ 60`（**估计，非实测**）。`evidence\rgm2\coverage_subset_r2.txt`
4. **家族静态面**：8 个家族文件对 `--help`/`-h` **0 命中**（本轮 grep），而 r2 的行为增量**只在「`SystemExit` 于 `main()` 内抛出」这一条路径上**；正常矩阵（5 个正常臂 + 5 个读端臂）与 r1 逐值相同 ⇒ O-2 的**动态面由矩阵复证**，家族面由 r1 证据 + 该静态不相交论证携带（**未重跑**）。

### R2-边界声明

- **零生产写**：`git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` 条目 **= 0**（开工 3821 / 收尾 3824，**两头非 `.planning` 都是 0**，详见下方 R2-收尾复核）；`git status --porcelain` 非 `.planning` 仅 r1 前既有 2 个未跟踪件（`.tmp-r41-mutation/`、`assurance/…/plan_inputs.json.bak`），**非本轮产生**。生产 CLI sha 复算 `2a2dfede…` == pin。
- **零 git 写**：本轮只执行 `git -c core.quotepath=false diff HEAD --name-only` / `git status --porcelain` 等只读命令；**未执行** `add/commit/checkout/stash/restore/reset` 任一种。
- **零网络**：未发起任何 HTTP/网络请求。
- **oracle 零改**：`oracle.md`/`oracle.sha256` 字节未动（sha 复算 `7fecfaea…`/`a6995bba…` 与冻结一致）；`binding.json`、`evidence\pins_freeze.txt`、`evidence\rgm\**`、`recovery.md` **一字未改**；r1 复审报告两件**只读**。
- **只动 iso + 本 attempt**：r2 的代码改动只落在 `iso\rf\scripts\revenue_forecast.py` 与 `iso\rf\tests\test_stdout_flush_exit_domain.py`；其余全部为本 attempt 目录内的**新建/追加**文件。

### R2-收尾复核（本轮最后一次写文档前的实测）

| 项 | 开工时 | 收尾时 | 结论 |
|---|---|---|---|
| `git -c core.quotepath=false diff HEAD --name-only` **非 `.planning` 计数** | **0**（总 3821） | **0**（总 3824） | **=0，纪律达成**；总数 +3 来自**其他会话并发写 `.planning` 内活文档**（`REMEDIATION_REGISTER.md` mtime 本轮内由 21:32:31 变到 21:59:07），与本卡无关；本 attempt 目录在 git 中**未被 HEAD 跟踪**（`git show HEAD:…commands.md` 报 `exists on disk, but not in 'HEAD'`），故对 attempt 的写入不进该 diff |
| `git status --porcelain` 非 `.planning` | 2 条 | **同 2 条** | `.tmp-r41-mutation/`、`assurance/unified_completion/manifests/plan_inputs.json.bak`——均既有未跟踪件，**非本轮产生** |
| 生产 `scripts/revenue_forecast.py` | `2a2dfede…` | **`2a2dfede7941b0fac972d802d25eb71f798c1ebdb83226bbf8528481b9669e36`** | == pin `prod_cli_before`，**零写** |
| 生产 `tests/test_stdout_flush_exit_domain.py` | 不存在 | **不存在**（`Test-Path=False`） | 新测试只在 iso，交付经 `changes.diff` |
| iso CLI | `4e6b64a7…` | **`405fec6d7ea23324bd671e144caa994889e076104d67560bc3b1d0f830599bda`** | `apply_fix_r2.py status` = `state=r2` |
| iso 新测试 | 6192 B / 175 行 / 8 测试 | **7270 B / 195 行 / 9 测试**，sha `083b92a535bf43f0ea0863a979579c2e6f55c4eb1e63abbefa7a7b35e1d533aa` | r1 的 175 行**逐字前缀未改**（尾部追加 1 条） |
| `changes.diff` | 8306 B / `f0a01489…`（r1） | **10114 B / `d1a79376c518eab300400c54badf91e141ed4b50ae0623a6fefe52900ad2856d`** | `VERIFY_DIFF_OK`；r1 预像归档 `evidence\rgm2\changes_r1_preimage.diff` |
| `oracle.md` / `oracle.sha256` | `7fecfaea…` / `a6995bba…` | **同值** | **冻结 oracle 一字未改** |
| `reviewer_report.md` | `99416605…` / 26073 B | **同值 / 26073 B** | **复审报告只读未改** |
| r1 证据 `evidence/MANIFEST.sha256` | 57 条 | **57/57 复算一致**（该 ledger 本身字节未改） | r1 `evidence/rgm/**` 零改写 |
| 前缀自证 | — | **`PREFIX_SELFCHECK_OK`**：append-only 9/9 `prefix_bytes_preserved=true`、byte-identical 面全等、DELIVERABLES r1 9/9 复算、reviewer report 只读 | `evidence\rgm2\prefix_selfcheck_r2.json` |

**r2 台账（append-only 规则）**

- `DELIVERABLES.sha256`：**r1 前 9 行一字未动**（r1 预像 725 B、sha `c7d8c583eeea3a754ae8272d54e36757896a93c71a977447370c53c5b4cb5ce8`，前 725 B 复算同值）；其后**追加** `# ---- review_round_2 (r2) append-only additions ----` 块，登记 r2 态 sha（`commands.md` / `decision.md` / `handoff.md` / `changes.diff` / `handoff.json` / `evidence/rgm2/MANIFEST_r2.sha256`），由 `harness\finalize_ledgers_r2.py` **幂等**生成。
- `evidence/MANIFEST.sha256`（r1，57 条）**不改**；r2 证据改由**新文件** `evidence/rgm2/MANIFEST_r2.sha256` 登记（不列自身，沿用 r1「MANIFEST 不列自身」口径）。
- `binding.json` / `evidence/pins_freeze.txt` / `recovery.md` / `oracle.*` / r1 `evidence/**`：**零改写**（复算见证）。

**r2 簿记事故与修复（如实披露）**：向 `commands.md` 追加 r2 节时，编辑器**丢掉了原文件末尾的 1 个换行字节**（r1 = 13251 B，追加后前缀复算 `bde20daa…` 不中），被 `harness\prefix_selfcheck_r2.py` **当场抓出**；已按「原文件 = 当前前 13250 B + `\\n`」逐字节还原，还原后前缀 sha 复算 = `bde20daace862f4f080793cb44697a23ce230086cce5464ed65d6b5de4aa7eae` ✓。首次失败的自检产物**改名归档** `evidence\rgm2\prefix_selfcheck_r2_failed1.json`（**不作证据**）；同轮还归档了探针期望表写错的 try1（`evidence\rgm2\failed_try1_expect_table\`）。**r1 证据字节零覆盖**。


