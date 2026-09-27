# reviewer_report.md — WC-4 = F12-RC120 独立复审（复审工位）

- 卡：WC-4 = F12-RC120 ｜ attempt：`.planning\2026-09-19-three-project-history-audit\execution_runs\WC-4-RC120\a20260923-01`
- 复审人：独立复审工位（非本卡实现者）｜复审日期：2026-09-24
- 本文只写复审结论与证据，不写卡状态、不改写任何既有交付字节、不创建 `handoff.json`。

## 1. 复审范围与方法

**读取顺序**（按卡面要求）：登记册 §一一〇（`REMEDIATION_REGISTER.md` L2063 附近 WC-4 行）→ `handoff.md` → `decision.md` → `oracle.md` → `commands.md` → `DELIVERABLES.sha256` → `evidence/`（含 `evidence/MANIFEST.sha256`、`evidence/rgm/**`、`evidence/mech/**`）→ `binding.json` + `evidence/pins_freeze.txt` → `harness/*`（`probe_wc4.py`、`apply_fix.py`、`verify_diff.py`、`check_ratchet_own_file.py`）。

**方法**（期望值一律来自本复审的独立复算/独立重跑，不照抄实现者叙述）：

1. **哈希独立复算**：`DELIVERABLES.sha256` 9 条、`evidence/MANIFEST.sha256` 57 条、`binding.json` 19 pins 全量重算；`pins_freeze.txt` 逐行原文在现盘文件中定位核对。
2. **机制独立复算**：生产 `scripts/*.py` 中 `120` 字面量与退出码形 0 命中；`Exception ignored on flushing sys.stdout` 是否存在于生产源；`python313.dll` 内该字面量的 byte offset 与 dll sha256 独立重算；**自建最小反证**（M0/M1/M4，脚本写在会话 `%TEMP%`，不落 `evidence/`）。
3. **红绿变异独立重跑**：因 `harness/probe_wc4.py` 会写 `evidence/rgm/<stage>/`（本复审不得改写 evidence 既有字节），改用**复审方自建等价 probe**（`%TEMP%\wc4_rev_probe.py`，故障构造逐字复刻 `run_sink("pipe_noreader")`：`os.pipe()` → `Popen(stdout=w_fd)` → 关 `w_fd` 与 `r_fd`，仅读 `Popen.returncode`），输出全部落 `%TEMP%`；iso 状态切换用卡面 `harness/apply_fix.py`（revert / apply / mutate2），终态复原。
4. **产品测试独立重跑**：`pytest` 在本会话沙箱内无法创建/使用其 tmp basetemp（见 §4），改用**复审方自建 runner**直接驱动 `tests/test_stdout_flush_exit_domain.py` 的 8 个测试函数（`monkeypatch` 最小替身；`conftest` 的会话夹具以 `REVENUE_PUBLICATION_REGISTRY → %TEMP%` 等价替代）。
5. **不变量**：棘轮脚本重跑、ruff 重跑、家族日志字节级复核、覆盖率静态面+算术面独立复算、双 probe 同 sha 独立复算。
6. **边界**：`git diff HEAD --name-only` / `git status --porcelain` 只读取证；不执行任何 git 写命令；不联网。

## 2. 逐项验证结果

### 2.1 机制归因（rc=120 来自 CPython finalization 段 flush 的 Errno22）—— **证据支持**

| 检查 | 卡面主张 | 本复审实测 | 结论 |
|---|---|---|---|
| G1 源内 `120` | 7 处全是 `FC-120x` 需求号 | 独立 grep 生产 `scripts/*.py`：**命中 7 处**，与卡面逐行相同（`filing_fetch_client.py:57,107`、`revenue_report.py:70,243,271,328`、`source_preparation.py:90`） | 一致 |
| G2 退出码形 | 0 命中 | 正则 `exit(120)/return 120/= 120/EXIT_120` → **0** | 一致 |
| G3 报错串归属 | `python313.dll` byte offset **5921656**、dll sha `d97a9810…` | 独立线性搜索：`C:\Miniconda\python313.dll` size=7,116,616，offset=**5921656**（精确相同），sha256=**d97a98104f8bba00acc6d91c9b1db9ce0e917257da80ec923000f7e9be9d77f4**；该字面量在生产任何 `.py` 中 **0 命中** | 一致（独立复算命中同一 offset） |
| M0 最小反证（无 RF 代码） | pipe_noreader=120 / reader=0 / file=0 | 自建脚本：**120 / 0 / 0**，stderr 逐字 `Exception ignored on flushing sys.stdout:\r\nOSError: [Errno 22] Invalid argument\r\n` | 一致 |
| **M1（`SystemExit(2)` 仍 120）** | 120 / reader=2 / file=2 → 「只归一化无效」 | 自建脚本：**120 / 2 / 2** | 一致；证明「把 main 返回值归一化成 2」在该故障下仍被 finalization 覆写，**归一化单半无效** |
| **M4（只 catch 不换流仍 120）** | pipe_noreader=120 → 「两半皆承重」 | 自建脚本（先缓冲写入再 `try: flush()` → catch → 写 stderr → `raise SystemExit(2)`，**不换流**）：**120**，stderr 同时含我方 `error: stdout flush failed: OSError(22, ...)` 与 CPython `Exception ignored …`；reader/file=0 | 一致；证明**流中和是必要半** |
| 与域内 catch 半合看 | 两半皆承重 | M1+M4 已证「仅 rc 归一化不够」「仅 catch 不够」；catch 半本身由产品测试 `test_finalize_exit_status_normalizes_flush_failure_to_2`（返回值必须=2）钉住 | 支持（缺一个「只中和不 catch」的变异臂，见 F-08） |
| 历史归因链 | I-09-C A=0/B=120/C=0 | `pipe_controls.json` 等 4 个 pin 全 MATCH，`handoff.json:54`/`reviewer_report.md:46` 原文在盘逐字 | 一致 |

**结论**：机制归因被证据支持——rc=120 不在产品源码、报错串由 `python313.dll` 发出（offset 5921656 独立复算命中）、无 RF 代码的最小片段同样 120，且 M1/M4 独立复现。SA-DEFECT 旧措辞「断言在返回后开火」确实与上述证据矛盾（`report_SA-DEFECT.md:165` pin MATCH，原文仍在，见 F-05 措辞问题）。

### 2.2 修复边界与生产零写 —— **通过**

- `changes.diff`（8306 B，sha `f0a01489a01b7200…` = DELIVERABLES 复算一致）**恰 2 文件**：`scripts/revenue_forecast.py`（单 hunk `@@ -123,5 +123,49 @@`，模块尾）+ `tests/test_stdout_flush_exit_domain.py`（新增 175 行、6192 B、sha `5b8e8a3fc1ebf5fb…` 与 handoff 一致、**8 个 `def test_`**）。
- 独立 `harness\verify_diff.py` → **`VERIFY_DIFF_OK`，rc=0**（重算 unified diff 与盘上逐字节同；`old_sha=2a2dfede… / new_sha=4e6b64a7…`；新测试 `NEW FILE (production absent as expected)`）。
- `_finalize_exit_status` **只在败路变**：成功路径 `sys.stdout.flush()` 成功即 `return rc`（原样透传）；只有 `except (OSError, ValueError)` 分支才 `print(error)`+换流+`return 2`。实测正常矩阵在 pristine/fixed 两态逐值相同（§2.3）。
- **只改 iso 隔离副本**：本复审的 revert/apply/mutate2 全部作用于 `iso\rf\scripts\revenue_forecast.py`；attempt 目录内当日 21:00 后唯一被改写的文件就是该 iso CLI（内容已复原为交付态 `4e6b64a789b97f30daf5def474bcd5a1d19cbc45b555e554b23fb8ecafe9e977`，mtime 变化、字节不变）。
- **生产树零改动（git 取证）**：`git diff HEAD --name-only` → `TOTAL=3821，NON_PLANNING=0`；生产 CLI sha=**`2a2dfede7941b0fac972d802d25eb71f798c1ebdb83226bbf8528481b9669e36` == pin `prod_cli_before`**；`tests/test_stdout_flush_exit_domain.py` 在生产树 **不存在**（`Test-Path=False`）。
- `production_zero_write_before.txt` / `_after.txt`：`scripts` 树 `d29e761d…`、`tests` 树 `a0d7667c…` 前后相同（字节级核验，算法未复刻，见 §4）。
- `git status --porcelain` 非 `.planning` 条目 **2 条**，均为会话前既有未跟踪件（`.tmp-r41-mutation/` 创建于 2026-09-20 18:31、`assurance/unified_completion/manifests/plan_inputs.json.bak` 创建于 2026-09-21 07:09），**非本复审产生**。

### 2.3 红绿链（**本复审亲自重跑**，raw rc 如下）

解释器：`C:\Miniconda\python.exe` 3.13.9，子进程一律 `-B`；cwd=`iso\rf`；故障构造=写端打开、读端已关的管道。

| 阶段 | iso CLI sha | F12 臂 raw rc | stderr 关键指纹 | 基线 A/C | 正常矩阵 N1..N5 | probe 自身 rc |
|---|---|---|---|---|---|---|
| **GREEN（重跑 1，交付态）** | `4e6b64a7…` | **2** | `error: stdout flush failed: [Errno 22] Invalid argument`，**无** `Exception ignored` | 0 / 0 | 0 / 2 / 2 / 0 / 0，N5 两产物落盘 | **0**（`GREEN_IN_DOMAIN_2_WITH_ERROR_TEXT`） |
| **RED（revert→pristine 后重跑）** | `2a2dfede…` | **120** | `Exception ignored on flushing sys.stdout:` + `OSError: [Errno 22] Invalid argument` | 0 / 0 | 0 / 2 / 2 / 0 / 0 | **0**（`RED_REPRODUCED_OUT_OF_DOMAIN_120`，120 ∉ {0,2}） |
| **MUT2（apply→mutate2 后重跑）** | `347400d6…` | **120** | **两者都在**：`error: stdout flush failed: …` **且** `Exception ignored …` | 0 / 0 | 0 / 2 / 2 / 0 / 0 | **0**（`MUTATION_DETECTED_mut2`） |
| **GREEN（复原后终跑）** | `4e6b64a7…` | **2** | 同上（产品文本在、无 `Exception ignored`） | 0 / 0 | 0 / 2 / 2 / 0 / 0 | **0** |

**产品测试（8 用例）独立重跑**（复审方 runner，见 §4 关于 pytest 的说明）：

| 状态 | 结果 | runner rc | 卡面记录 | 是否相符 |
|---|---|---|---|---|
| GREEN（fixed `4e6b64a7`） | **8 passed / 0 failed**（跑两次，均 8/0） | 0 | C6b/C10b「8 passed」 | 相符 |
| RED（pristine `2a2dfede`） | **6 failed / 2 passed**；端到端失败原文 `… got 120 …`，其余 5 条 `AttributeError: module 'revenue_forecast' has no attribute '_finalize_exit_status'/'_neutralize_broken_stream'` | 1 | C3b「6 failed, 2 passed」 | 相符 |
| MUT1（= pristine，字节同 `2a2dfede`） | 与 RED 同态（同一字节状态，卡面亦自述「RED 与 MUT-1 同态」） | 1 | C8b「6 failed, 2 passed」 | 相符 |
| MUT2（`347400d6`） | **2 failed / 6 passed**；失败恰为①端到端 `got 120` ②`assert sys.stdout is not broken` | 1 | C9b「2 failed, 6 passed——失败的恰是两条半承重断言」 | 相符 |

**与盘上既有证据对照**：`evidence/rgm/{red,green,mut1,mut2}/probe.json` 的 `iso_cli_sha256` / `f12_arm.raw_returncode` / verdict 分别为 `2a2dfede`+120+`RED_REPRODUCED_OUT_OF_DOMAIN_120`、`4e6b64a7`+2+`GREEN_IN_DOMAIN_2_WITH_ERROR_TEXT`、`2a2dfede`+120+`MUTATION_DETECTED_120_RETURNED_mut1`、`347400d6`+120+`MUTATION_DETECTED_120_RETURNED_mut2`，`harness_rewrites_child_rc=false` —— **与本复审重跑的 rc、iso sha 逐项相同**。

### 2.4 变异证明 —— **通过**

- **MUT1（整体回退）**：`apply_fix.py revert` 后 iso sha = **`2a2dfede…`** == `evidence/rgm/cli_original.py` == 生产 pin ⇒ 变异体即 pristine 字节（最小回退）；probe **rc=120**、测试 **6F/2P** ⇒ 被判据打红。
- **MUT2（半回退）**：实测 sha **`347400d6059e661e0fe3328bc4ef902c0a7c3b1c8a1bc62b42dedee1c0cc0507`**；复审独立按 `fixed_text.replace('        _neutralize_broken_stream("stdout")\n        return 2', '        return 2')` 重建，得 **sha 完全相同** ⇒ **变异体与 fixed 逐行 diff 恰好只有 1 行被删**（`@@ -165 +164,0 @@ -        _neutralize_broken_stream("stdout")`）。probe **rc=120**（产品文本在）、测试 **2F/6P** ⇒ 被打红且非空转。
- 两个变异臂均只动 iso，未触碰 `evidence/*` 与生产树。

### 2.5 不变量 —— 逐个复算/重跑

| 不变量 | 卡面数字 | 本复审核验 | 结论 |
|---|---|---|---|
| 家族 8 文件（grep 依据） | 8 文件 | 独立 grep `revenue_forecast\.py\|scripts[/\\]+revenue_forecast` → **恰 8 文件**，文件集合与卡面完全相同 | ✅（行号清单有 1 处漏列，见 F-06） |
| 家族结果 before==after | 64 passed / 48 subtests 恒 | **未能重跑**（pytest 环境限制，§4）→ 字节级核验：`family_before_raw.txt`/`family_after_raw.txt`/`family_final_raw.txt`（各 334 B，UTF-16）三份 summary 均为 **`64 passed, 48 subtests passed`**，仅计时行 199.76s / 184.42s / 180.48s 不同；`family_compare.txt` 的 unified diff 除计时行外为空；三文件哈希均在 MANIFEST 57/57 内命中；无 skip/xfail 字样 | ⚠️ 重跑未果，字节级一致 |
| 棘轮 18==frozen | 18 | **重跑** `check_ratchet_own_file.py` → `iso_fixed=18 (worst=main:18)`、`iso_pristine=18`、`production=18`、`frozen_max=18`、`OWN_FILE_RATCHET_OK`，**rc=0** | ✅ |
| 覆盖 73% ≥ 60、新 0 miss | 90 stmts / 20 miss / 18 branch / 5 BrPart / 73% | **静态面独立复算**：以项目 `.coveragerc`（`branch=True`、`exclude_lines=if __name__ == .__main__.`）计量修复后 iso 文件 → **Stmts 90、Branch 18**，与卡面完全一致；**算术面**：coverage 公式 (90−20 + 分支覆盖 9)/108 = 73.1% → **73%**，与 90/20/18/5 自洽且 **73 ≥ 60**；**新 0 miss 独立证实**：复审方自跑 coverage（仅新测试子集）得 `90 / 55 miss / 18 / 0 BrPart / 32%`，missing = `27-35, 47-52, 56-123`，**全部 < 126**（修复插入点 `@@ -123,5 +123,49 @@` 之后的新语句一行不缺）；卡面 missing `73-100,102,106,117,118->123,120-122` 亦全部 ≤123 | ✅ 形态/算术/新语句 0 miss 均复算通过；**20 miss 的原始 subset 数字未独立复现**（§4） |
| 双 probe 同 sha | `52807297…` | 独立复算 `green/probe.json` 与 `green/probe_run1_after_fix.json` → 均为 **`528072976cab4b60e10893a627ce339b33cab78f24ad65720d8778f12feb5fb2`**，`EQUAL=True` | ✅ |
| 产零写 | 前后树 sha 相同 | §2.2 git 取证 + 生产 pin 复算 + 新测试不在生产 | ✅ |
| ruff（CI 钉 0.15.18） | `All checks passed!` | **重跑** `ruff 0.15.18 check <iso cli> <iso new test>` → `All checks passed!`，**rc=0** | ✅ |

### 2.6 冻结序（oracle/期望是否先于首次运行写盘）

mtime 实测（attempt 内）：

```
23:50:38  oracle.md          23:50:41  oracle.sha256        23:51:50  binding.json / pins_freeze.txt
23:40:19  evidence/mech/mech_cases.json            ← 冻结前（C1 phase0，已如实披露）
00:04:17  evidence/mech/grep_120_and_emitter.txt   ← 冻结后（但 commands.md 把它列在「冻结之前」，见 F-04）
00:04:59 family_before → 00:09:39 family_after → 00:43:36 family_final
00:32:41 red/probe.json → 00:33:00 red_pytest → 00:33:12 mut1 → 00:33:52 mut2 → 00:34:53 green/probe.json
00:14:27 green/probe_run1_after_fix.json（首轮 GREEN，早于末轮 RED，见 F-07）
```

- `oracle.md` mtime **早于** `oracle.sha256`；收尾复算 `oracle.md` sha = **`7fecfaea02f62b3740122a2c79ff5f7194bdd29505696cb0e8c38cdce1cb8be8`** 与 `oracle.sha256`、`binding.json.oracle_sha256`、`DELIVERABLES.sha256` 四处全同 ⇒ **oracle 冻结后无编辑**，不存在事后改写。
- 末轮 RGM 产物时序 red(00:32:41) < red_pytest(00:33:00) < mut1(00:33:12) < mut2(00:33:52) < green(00:34:53) ⇒ **先红后绿**在末轮内成立。
- `commands.md`/`decision.md`/`handoff.md` 的 mtime（00:38–00:44）晚于 RGM，属**回填式追加**，其内容已被 `DELIVERABLES.sha256` 钉住（9/9 复算一致），旧值无从比对（这些文件没有更早版本留存）→ 记为不可证的簿记面（§4）。

### 2.7 交付完整性 —— **通过**

- `DELIVERABLES.sha256` **9/9 全部复算一致**：`oracle.md 7fecfaea…`、`oracle.sha256 a6995bba…`、`binding.json caca43e8…`、`commands.md bde20daa…`、`decision.md fad182c0…`、`changes.diff f0a01489…`、`handoff.md 14dc9b62…`、`recovery.md 1c58a8ef…`、`evidence/MANIFEST.sha256 29efb109…`。
- `evidence/MANIFEST.sha256` **57/57 全部复算一致**（唯一未列入者为 MANIFEST 自身，正常）。
- `binding.json` 19 pins：**10 MATCH / 9 DRIFT**（明细见 F-03）；`pins_freeze.txt` 50 条行级原文中 **38 条原行号原字**、**12 条（全在 REMEDIATION_REGISTER.md）整体 +1 行漂移但逐字未改**，其余文件（I-09-A decision、OWNER_DECISIONS、SA-DEFECT、I-09-C 四件、REGISTRY-CLOSURE decision L64/93/94/104）均原行号原字。

### 2.8 额外全域性检查（oracle O-1 是否在**所有**可达 F12 路径成立）—— **不成立**

复审在通过 2.1–2.7 后追加了对 oracle `O-1`（「产品 CLI 在 F12 故障下退出码 ∈ {0,2}」，无路径豁免）的全域抽测，结果：

| 调用 | sink | iso 修复态 `4e6b64a7` raw rc | 生产 pristine `2a2dfede` raw rc |
|---|---|---|---|
| `--version` | 断读端管道 | **2**（`error: stdout flush failed: …`） | 120 |
| 无参数（usage） | 断读端管道 | **2**（usage 文本在 stderr） | 2 |
| **`--help` / `-h`** | 断读端管道 | **120**，stderr 仅 `Exception ignored on flushing sys.stdout:` | 120 |
| `--version` / usage / `--help` | 正常读端 | 0 / 2 / 0 | 0 / 2 / 0 |

**`--help` + 断读端 stdout 在修复态仍为 raw rc=120**，且 stderr **没有** `error: stdout flush failed` ⇒ `_finalize_exit_status` 未被执行。根因：argparse 把 help 文本写入 stdout 缓冲后在 **`main()` 内部** `raise SystemExit(0)`，`raise SystemExit(_finalize_exit_status(main()))` 的包装函数根本没被调用。这正是 F-01。

## 3. 发现表

| 编号 | 级别 | 位置 | 证据（复审实测） | 建议处置 |
|---|---|---|---|---|
| **F-01** | **P1（阻断）** | `oracle.md` L12（O-1 无豁免）；`scripts/revenue_forecast.py` 入口 `raise SystemExit(_finalize_exit_status(main()))`；`handoff.md` L38 §3.3 | iso `4e6b64a7`：`python -B revenue_forecast.py --help`（stdout=写端开、读端关的管道）→ **raw rc=120**、stderr 仅 `Exception ignored on flushing sys.stdout: OSError: [Errno 22] Invalid argument`（无产品错误文本 ⇒ 包装未执行）；`-h` 同；正常读端臂=0。生产 pristine 同为 120（非回归，但**未修**）。该构造完全落在 oracle 对 F12 的定义（stdout 输送失败：管道关闭）内，而 O-1 明文要求 ∈ {0,2}。卡面唯一相关披露 `handoff.md §3.3` 的理由「该路径 stdout 为空、无待 flush 内容——推理而非实测」被本实测**证伪**（help 文本正是被缓冲的内容） | 把包装从 `_finalize_exit_status(main())` 扩到能覆盖 `main()` 内抛出的 `SystemExit`（如 `try: rc = main() except SystemExit as e: rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 2)` 后再 `_finalize_exit_status(rc)`），并补 1 条产品测试（`--help` × 断读端 → 2 + 产品文本 + 无 `Exception ignored`）；若 owner 认为 `--help` 不属 F12 范围，则须由 owner 出具明确的 oracle 范围豁免（oracle 已冻结，实现者不得自行改） |
| **F-02** | P3 | `commands.md` P1 表 Q3 行（raw rc 记 0） | `evidence/rgm/coverage_subset_fixed.txt` 末行原文 `Coverage failure: total of 73 is less than fail-under=84`；复审实测 `.coveragerc [report] fail_under=84`，带 fail-under 的 `coverage report` 未达标时 **rc=2**（不带则 rc=0）⇒ 产出该证据的 report 步骤 rc≠0 | 更正 Q3 的 rc 记录，或写明 0 属于哪一步（`coverage run`/`pytest`）而 report 步 rc=2；不改动证据字节，以 erratum 记载 |
| **F-03** | P3 | `binding.json` 19 pins | 复审全量重算：**9 DRIFT** = `REMEDIATION_REGISTER.md` ×5（227689 B/`2e9f3a40` → 270337 B/`33c7505e`）、`REGISTRY-CLOSURE/…/decision.md` ×3（23413 B/`a68ed77f` → 26557 B/`5e275968`）、`iso_cli_before` ×1（`2a2dfede` → `4e6b64a7`＝交付态，预期内）；**10 MATCH**。行级：12 条 register 行整体 **+1 行漂移**（1655→1656、1701→1702、1716→1717、1741→1742、1745→1746、1747→1748、1748→1749、1749→1750），**逐字未改**；closure decision L64/93/94/104 原行号原字 | 漂移属活文档外部追加（非本卡造成），按本计划他卡惯例以 erratum 记录真值与「行号 +1、内容逐字」的核验结论，封件不回改 |
| **F-04** | P3 | `commands.md` P1「phase0 — 地面真相复核（oracle 冻结之前）」表中的 C1b 行 | `evidence/mech/grep_120_and_emitter.txt` mtime = **2026-09-24 00:04:17**，晚于 `oracle.sha256`（2026-09-23 23:50:41）约 14 分钟；同表 C1 的 `mech_cases.json` mtime 23:40:19 确在冻结前 | 更正该行的阶段标注（或补记「冻结前已跑、冻结后重跑留证」），避免「先于冻结」的表述与产物 mtime 不符 |
| **F-05** | P3 | `handoff.md` §1 表「`report_SA-DEFECT.md:165` 被更正」 | pin `sa_defect_wrong_mechanism` **MATCH**（sha `374a5770…`、26047 B），L165 原文仍为「断言在返回后开火」⇒ 该文件字节**未被改动**；更正实际只落在本卡 `oracle.md §5` / `decision.md §1`（登记册 §一一〇 已写明「封存件不动、oracle §5 冻结」） | 把 handoff 表述改为「以本卡 oracle §5/decision §1 承载更正；封存件字节不动」，与登记册口径一致 |
| **F-06** | P3 | `decision.md` §5 家族 grep 行号清单 | 复审用卡面自述的同一正则 grep：`tests/test_publication_pipeline.py:315` 亦命中（注释行 `# (the subprocess-only pattern left revenue_forecast.py at ~0%).`），decision 只列了 87/332/360；**文件集合仍恰 8 个**，不影响 G-4 | 补列 315 或注明已排除注释行 |
| **F-07** | P3 | `evidence/rgm/red/probe.json` 等 | 首轮 GREEN `probe_run1_after_fix.json` mtime **00:14:27** 早于现存 RED `probe.json` mtime **00:32:41** ⇒ 首轮 RED 的探针字节被末轮同名覆盖、未单独留存（`commands.md` 仅对 C4 明确披露了同名覆盖）。末轮内部时序 red<mut1<mut2<green 自洽，判据内容不受影响 | 在 commands.md P1 补一行「C2 首轮 probe 输出被 v2 末轮同名覆盖」，保持与 C4 同等的披露口径 |
| **F-08** | P3 | `oracle.md §4` / `decision.md §4` 变异矩阵 | 冻结判据只有 M-1（整退）与 M-2（留 catch 去中和），**没有**「只中和不 catch」臂（该臂会 rc=0 且无错误文本，仍 ∈{0,2} 但违反 G-2 的 fail-closed/informative）。卡面「两半皆承重」中 catch 半目前仅由产品测试 `test_finalize_exit_status_normalizes_flush_failure_to_2` 承担，无变异臂打红 | 保持（判据冻结、测试已钉）；在 decision 增补一句说明 catch 半的非空转证据来自产品测试而非 MUT 臂 |

**级别统计：P1 = 1（F-01），P2 = 0，P3 = 7（F-02…F-08）。**

## 4. unverified / 未能重跑清单（如实携带）

1. **家族 64/48 未能重跑**：`pytest` 在本会话沙箱中无法创建/使用其 tmp basetemp，报 `PermissionError: [WinError 5] ... \Temp\dsh-RI6nNv\pytest-of-郑曾波`（会话夹具 `_isolate_publication_registry` 即 `tmp_path_factory.mktemp` 处炸）。已试 4 种绕行均失败：①默认 TEMP ②重定向 `TEMP/TMP/TMPDIR` ③`--basetemp` 新路径 ④`--basetemp` 预建路径（均同一 PermissionError，最小无夹具用例可通过 ⇒ 环境限制而非卡面问题）。⇒ 改用**字节级核验**：三份家族 raw 日志 summary 全同（64/48）、compare 仅计时差、MANIFEST 57/57 哈希命中。**未证的是「本次会话内重跑得到 64/48」**。
2. **产品测试未以 pytest 重跑**（同一环境限制）；以复审方 runner 直接驱动 8 个测试函数替代，得到 GREEN 8/0、RED 6F/2P、MUT2 2F/6P。差异面：不经过 pytest 的会话夹具（已用 `REVENUE_PUBLICATION_REGISTRY` 等价替代）与 pytest 断言格式化，判据值（rc、文本、`sys.stdout is not broken`）逐条相同。
3. **覆盖率 73% 的原始 subset 数字未独立复现**（需 pytest 跑「5 个 CLI 触碰测试 + 新测试」）。已独立复算：静态面 90/18 与卡面完全一致、73% 的算术自洽、**新语句 0 miss 独立证实**、missing 行全 ≤123。
4. **生产树 tree-sha（`d29e761d…`/`a0d7667c…`）算法未复刻**（卡面未给出算法/清单）⇒ 以 `git diff HEAD --name-only` NON_PLANNING=0 + 生产 CLI sha==pin + 新测试不在生产树替代证明（三者均通过）。
5. **`--help` 之外的 `SystemExit`-in-`main` 组合**未穷举（仅测 `--help`/`-h`/usage）；Linux/macOS 断管码值、stderr 汇断管、CPython 源码行号 —— 卡面已披露为未测/不可引，本复审照录（dll 字面量 offset 已独立复算命中）。
6. **`probe_f12.py:65` 修正**仅以 `evidence/probe_f12_line65_fix.diff` 交付、封存件字节未动（pin `i09c_probe_f12_line65` MATCH）—— 是否随修本体需父裁，本复审不裁定。
7. **`commands.md`/`decision.md`/`handoff.md` 的「冻结前写盘」无法由 mtime 独证**（均在 RGM 之后回填，无更早版本留存）；能证的是 `oracle.md`+`oracle.sha256` 的冻结序与四点同 sha。

## 5. 边界声明

- **零生产写**：`git diff HEAD --name-only` → `TOTAL=3821`、**`NON_PLANNING=0`**（复审结束前复测同值口径）；生产 `scripts/revenue_forecast.py` sha 仍为 pin `2a2dfede…`；新测试不在生产树。
- **零 git 写**：全程只执行 `git diff HEAD --name-only` / `git status --porcelain` / `git -c core.quotepath=false …` 等只读命令；**未执行** `add/commit/checkout/stash/restore/reset` 任何一种。
- **零网络**：未发起任何 HTTP/网络请求。
- **写入面**：仅本 attempt 目录内**新建** `reviewer_report.md` 与其侧钉 `reviewer_report.sha256`；`handoff/decision/oracle/binding/commands/evidence` 既有字节**零改动**（复审结束前 DELIVERABLES 9/9、MANIFEST 57/57 再次复算全中为证）；**未创建/改写 `handoff.json`**；未在任何载体写入自拟 status。
- **重跑期间的受控改动**：按复审要求「在本 attempt 隔离副本内按 commands.md 重跑」，用卡面 `harness/apply_fix.py` 切换 `iso\rf\scripts\revenue_forecast.py`（revert→apply→mutate2→apply），**终态已复原为交付态 `4e6b64a789b97f30…`**；attempt 内当日 21:00 后唯一被改 mtime 的文件即该 iso CLI（字节不变）。
- **临时文件**：全部落在会话 `%TEMP%`（`...\AppData\Local\Temp\dsh-RI6nNv\`，即 `commands.md`/`binding.json` 声明的 runner temp），仓库其他位置未创建文件；`evidence/rgm/**` 未被本复审写入（故弃用 `probe_wc4.py` 而用等价自建 probe）。

## 6. 结论

2.1–2.7 的卡面主张全部经独立复算/重跑成立（机制归因、修复边界、红绿链 rc、双变异打红、棘轮/覆盖形态/双 probe 同 sha/交付哈希/冻结序均通过，家族项以字节级核验替代重跑）。但 2.8 的独立全域抽测发现 oracle 冻结不变式 **O-1 在可达的 F12 路径上被证伪**（`--help` × 断读端 → raw rc=120），且卡面唯一相关披露的前提为假，属阻断级。

VERDICT: changes_required
