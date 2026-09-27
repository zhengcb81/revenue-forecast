# reviewer_report_r2.md — WC-4 = F12-RC120 **r2 修复轮**独立复审（复审工位）

- 卡：WC-4 = F12-RC120 ｜ attempt：`.planning\2026-09-19-three-project-history-audit\execution_runs\WC-4-RC120\a20260923-01`
- 复审人：独立复审工位（与实现者非同一人）｜复审日期：2026-09-24（读数时点以正文标注为准）
- 本文只写复审结论与证据，**不写卡状态、不改任何既有交付字节、不创建/修改 `handoff.json`、不替实现者落定**。
- 本轮写入面 = 本 attempt 内**仅两个新建文件**：`reviewer_report_r2.md` + `reviewer_report_r2.sha256`。

## 1. 复审范围与方法（全部为本复审的独立复算 / 独立重跑）

1. **只读**：r1 `reviewer_report.md`（裁决来源）、`oracle.md`/`oracle.sha256`、`binding.json`、`evidence/**`、r1 两份复审报告字节。
2. **独立重跑环境**：把 `iso\rf`（1976 文件 / 28 MB）整树复制到本会话 `%TEMP%\wc4r2rev\rf`，**所有探针与 pytest 只在该副本内跑**，attempt 目录与生产树零写。
3. **状态重建（不调用卡面 harness 写盘）**：用 `evidence\rgm2\cli_r1_state.py` / `cli_r2_state.py` 快照 + 我自己写的替换逻辑在 %TEMP% 内重建 5 个状态，并独立复算每个状态的 sha256。
4. **探针**：自建 `%TEMP%\wc4r2rev\rev_probe.py`（故障构造 = `os.pipe()` → `Popen(stdout=w_fd)` → 关 `w_fd` 与 `r_fd`，只读 `Popen.returncode`，与 r1/I-09-C 同构），**未运行卡面 `probe_help_r2.py`**（它写 `evidence\rgm2\`）。
5. **产品测试**：`python -B -m pytest tests\test_stdout_flush_exit_domain.py -q -p no:cacheprovider --noconftest`，cwd=%TEMP% 副本，`REVENUE_PUBLICATION_REGISTRY` 显式指向 %TEMP%；判据值与 r1 完全相同（rc、stderr 文本、`sys.stdout is not broken`）。
6. **哈希/前缀/清单**：全部由本复审用 `Get-FileHash` + 自写 SHA-256 前缀脚本重算。
7. **git**：只执行 `git -c core.quotepath=false diff HEAD --name-only`、`git apply --check`（只读）；**本仓未执行 `git status`**，未执行任何 git 写命令。
8. **棘轮**：先自写 `_mccabe`/`_max_complexity`（逐行对齐 `tools/tests/test_complexity_ratchet.py` 算法）独立复算，再跑卡面 `harness\check_ratchet_own_file.py`（纯读）交叉验证。

## 2. F-01（r1 P1）是否真的关了 —— **是（本复审亲测）**

解释器 `C:\Miniconda\python.exe` 3.13.9；cwd=%TEMP% 副本 `rf`；故障臂 = 写端开、读端已关的管道。

### 2.1 修前态（r1 交付 `4e6b64a789b97f30daf5def474bcd5a1d19cbc45b555e554b23fb8ecafe9e977`，由 r2 快照独立反推、sha 命中）

| 臂 | 断读端 raw rc | stderr 关键行 | 产品文本 | `Exception ignored` |
|---|---|---|---|---|
| `--help` | **120** | `Exception ignored on flushing sys.stdout:` / `OSError: [Errno 22] Invalid argument` | **无** | **在** |
| `-h` | **120** | 同上（逐字两行） | **无** | **在** |
| `<input> --validate-only` | 2 | `error: stdout flush failed: [Errno 22] Invalid argument` | 在 | 无 |
| `--version` | 2 | `error: stdout flush failed: [Errno 22] Invalid argument` | 在 | 无 |
| 无参数 usage | 2 | `usage: …` + `error: the following arguments are required: input` | 无（不适用） | 无 |
| 读端正常 5 臂 | **0 / 0 / 0 / 0 / 2** | — | — | — |

⇒ **r1 的 P1 现象在我这里原样复现**：`--help`/`-h` raw rc=120、stderr 只有 CPython 两行、**无产品错误文本** ⇒ `_finalize_exit_status` 未被执行（`raise SystemExit(_finalize_exit_status(main()))` 够不到 `main()` 内 argparse 的 `SystemExit`）。

### 2.2 修后态（r2 交付 `405fec6d7ea23324bd671e144caa994889e076104d67560bc3b1d0f830599bda` = 当前 iso 字节，`iso_now == cli_r2_state` 实测 `true`）

| 臂 | 断读端 raw rc | stderr 关键行 | 产品文本 | `Exception ignored` |
|---|---|---|---|---|
| `--help` | **2** | `error: stdout flush failed: [Errno 22] Invalid argument` | **在** | **0 命中** |
| `-h` | **2** | 同上 | **在** | **0 命中** |
| `<input> --validate-only` | **2** | 同上 | 在 | 0 命中 |
| `--version` | **2** | 同上 | 在 | 0 命中 |
| 无参数 usage | **2** | usage 文本（stderr-only，产品 flush 文本不出现属正常） | — | 0 命中 |
| 读端正常 5 臂 | **0 / 0 / 0 / 0 / 2** | — | — | — |

读端 stdout 形状（我逐臂断言）：`--help`→以 `usage:` 开头；`-h`→以 `usage:` 开头；`--validate-only`→逐字 `valid`；`--version`→以 `revenue-forecast ` 开头；usage→stderr 含 `usage:`。**5/5 全对**。

另测 O-2 加强项：读端 `--help` 的 stdout **1612 B，与生产 pristine 逐字节同 sha** ⇒ 正常路径输出形状/字节未变。

**结论：F-01 关闭。** 冻结不变式 O-1（rc ∈ {0,2}）在我实测的 `--help`/`-h`/`validate`/`version`/`usage` × 断读端 5 条路径上全部成立（2/2/2/2/2）。

**对照：生产 pristine `2a2dfede7941b0fac972d802d25eb71f798c1ebdb83226bbf8528481b9669e36`（5333 B，== pin `prod_cli_before`）**：`--help`=120、`-h`=120、`validate`=120、`version`=120、usage=2 —— 与卡面「非本卡回归、待合并 `changes.diff` 后修复」一致（本复审只读执行）。

### 2.3 「只动 iso、只动 `__main__` 块」的独立证明

我用 r2 文本按 `if __name__ == "__main__":` 截断并替换回 r1 入口行，**独立重建的 r1 文本与 `cli_r1_state.py` 快照逐字节相等**（`derived_r1_equals_snapshot_r1 = true`）⇒ **r2 相对 r1 的字节增量只有 `__main__` 块**，`_finalize_exit_status` / `_neutralize_broken_stream` **一字未改**。

## 3. oracle 未改 —— **通过**

| 来源 | 值 |
|---|---|
| 本复审复算 `oracle.md`（5166 B） | `7fecfaea02f62b3740122a2c79ff5f7194bdd29505696cb0e8c38cdce1cb8be8` |
| `oracle.sha256` 文件内容 | `7fecfaea…  oracle.md`（文件自身 sha `a6995bba…`，== r1 DELIVERABLES 行） |
| `binding.json.oracle_sha256` | `7fecfaea…` |
| r1 复审报告 §2.6 记录的钉值 | `7fecfaea…` |
| `handoff.json.oracle.changed_in_r2` | `false` |

**四处全同 + 与 r1 钉值相同 ⇒ oracle 冻结后无编辑。** 未走 owner 豁免、未登记任何 oracle 待裁项（`decision.md` §7.1 明写「第 2 条路不走、不代裁」；全文无「oracle 待裁」登记）。

## 4. 三个变异臂（**每个状态的 sha 我独立重建并复算**）

| 臂 | 我重建的 iso sha | 与卡面自述 | `--help` | `-h` | validate | version | usage | stderr 关键行 | 产品测试 |
|---|---|---|---|---|---|---|---|---|---|
| **变异①回退包装**（回 r1 态） | `4e6b64a789b97f30…`（**由 r2 文本反推，与 r1 快照逐字节相等**） | 相同 | **120** | 120 | 2 | 2 | 2 | 仅 CPython 两行、无产品文本 | **1 failed, 8 passed**（`assert 120 == 2`） |
| **变异②只 catch 不换流** | `99fc716ad9ef6ce80f5e2e50062027f2e2e0354a432774034ad8c8a6d6891153` | 相同 | **120** | 120 | **120** | **120** | 2 | **产品文本与 `Exception ignored` 并存**（逐字两段都在） | **3 failed, 6 passed** |
| **变异③只中和不 catch**（F-08 补臂） | `4f9d78034b46e8054ef9807dafc38f9728737269f2be5c6eeca505012ddbd95b` | 相同 | **0** | 0 | 0 | 0 | 2 | **无产品文本、无 `Exception ignored`**（stderr 空） | **4 failed, 5 passed** |

- 三臂读端正常矩阵均 **0/0/0/0/2**、形状全对。
- **三个臂都打红**：①新判据 `--help` 条红；②端到端 120 + `assert sys.stdout is not broken` 类断言红；③端到端 rc≠2 + 无文本 + `normalizes_flush_failure_to_2` + `survives_broken_stderr` + 新 `--help` 条红。
- 变异③ rc=0 ∈ {0,2} 但**无产品文本、fail-closed/informative 被破坏** ⇒ 正如卡面所述「违反 G-2」；该臂确为 r1 P3 F-08 要求补的臂，**本轮已补并打红**。
- 所有状态切换只发生在 %TEMP% 副本；**卡面 iso 终态仍为 `405fec6d…`**（本复审未改 attempt 任何字节）。

## 5. 产品测试 9 条（**我用 pytest 在 %TEMP% 副本亲自重跑**）

| 状态 | 结果 | pytest rc | 卡面自述 | 是否相符 |
|---|---|---|---|---|
| 修前（r1 代码 `4e6b64a7` + 新 9 条测试文件） | **1 failed, 8 passed**（失败原文 `AssertionError: --help with a broken stdout pipe must land in the frozen domain {0,2} as rc=2, got 120; stderr='Exception ignored on flushing sys.stdout:\r\nOSError: [Errno 22] Invalid argument\r\n'`） | 1 | 1 failed, 8 passed | ✔ |
| 修后（r2 `405fec6d` + 9 条） | **9 passed** | 0 | 9 passed（r1 8 条 = 8/0） | ✔ |
| 变异①（`4e6b64a7`） | 1 failed, 8 passed | 1 | 1F/8P | ✔ |
| 变异②（`99fc716a`） | 3 failed, 6 passed | 1 | 3F/6P | ✔ |
| 变异③（`4f9d7803`） | 4 failed, 5 passed | 1 | 4F/5P | ✔ |
| 生产 pristine（参考） | 7 failed, 2 passed | 1 | （r1 8 条时为 6F/2P，+1 新条 ⇒ 7F/2P 自洽） | ✔ |

**运行方式是否只改运行方式、不改判据值**：`--noconftest` 只是绕开会话夹具 `_isolate_publication_registry`（`tmp_path_factory.mktemp` 在本沙箱确实被拒——我独立复现：`tempfile.mkdtemp()` 建得出目录，**向其中 `open(...,'w')` 报 `PermissionError: [Errno 13]`**，纯 python 进程同样复现）；该夹具的唯一作用就是设 `REVENUE_PUBLICATION_REGISTRY`，我显式指向 %TEMP% 等价替代。**判据断言本身（rc、`stdout flush failed` 文本、`Errno`、`Exception ignored` 缺席、`sys.stdout is not broken`、`_NullStream` 回退、正常臂 0/2）逐条未改**——我读了测试源码并逐条复跑。⇒ **只改运行方式，未改判据值。**

测试文件本身：7270 B / 195 行 / 9 个 `def test_` / sha `083b92a535bf43f0ea0863a979579c2e6f55c4eb1e63abbefa7a7b35e1d533aa`（与卡面一致）。

## 6. 棘轮与 lint —— **我自己复算**

**棘轮**（算法逐行对齐 `tools/tests/test_complexity_ratchet.py` 的 `_mccabe`/`_max_complexity`，frozen `revenue_forecast.py`=18）：

| 目标 | 我复算 max | worst | 结果 |
|---|---|---|---|
| iso r2（`405fec6d`） | **18** | `main:18` | ≤18 ✅ |
| iso pristine（`evidence/rgm/cli_original.py` = `2a2dfede`） | **18** | `main:18` | ✅ |
| 生产（`2a2dfede`） | **18** | `main:18` | ✅ |
| r1 态（`4e6b64a7`，附加参考） | **18** | `main:18` | ✅ |

卡面 `harness\check_ratchet_own_file.py` 重跑：`iso_fixed=18 / iso_pristine=18 / production=18 / frozen_max=18`、`OWN_FILE_RATCHET_OK`、**raw rc=0** ⇒ 与我的复算逐值相同，**三者 max=18 == frozen 18**。

**lint**：`python -m ruff --version` → **ruff 0.15.18**；`ruff check` 两个交付文件（iso CLI + iso 新测试）→ **`All checks passed!`，raw rc=0**。

## 7. `changes.diff` —— **重建逐字节相同；但 plain `git apply --check` 不通过**

| 项 | 卡面自述 | 我的实测 |
|---|---|---|
| 大小 / sha | 10114 B / `d1a79376c518eab300400c54badf91e141ed4b50ae0623a6fefe52900ad2856d` | **完全相同**（10114 B / `d1a79376…`） |
| 文件数 | 恰 2 | **恰 2**：`scripts/revenue_forecast.py` + `tests/test_stdout_flush_exit_domain.py` |
| CLI 前后 | `2a2dfede…`（5333 B）→ `405fec6d…`（7647 B） | **完全相同** |
| 新测试 | 7270 B / 195 行 / 9 个 `def test_` | **完全相同** |
| hunks | `@@ -125,0 +126,44 @@` + `@@ -127 +171,15 @@` + `@@ -0,0 +1,195 @@` | **完全相同** ⇒ r1/r2 各一 hunk、增量可辨 |
| **独立重建** | — | 我用 `difflib.unified_diff(..., n=0)` 独立重算 → **与盘上逐字节相同**（`byte_identical=True`，双 sha 同 `d1a79376…`） |
| **`git apply --check`** | 未跑（卡面 `verify_diff.py` 是字节重建，非 git） | **raw rc=1（失败）**：`error: patch failed: scripts/revenue_forecast.py:127` / `error: scripts/revenue_forecast.py: patch does not apply`（隔离副本与**本仓内**各跑一次，结果相同；`autocrlf=false/true` 均同） |
| `git apply --check --unidiff-zero` | — | **raw rc=0（通过）** |
| 实际 apply（隔离副本） | — | `git apply --unidiff-zero` rc=0，产物 LF 归一后 **恰为 `405fec6d…` 与 `083b92a5…`** |
| r1 旧 diff（`changes_r1_preimage.diff`，`f0a01489…`） | 归档 | plain `git apply --check` **rc=0**（n=3 有上下文） |

**判定**：卡面 R2-C10b **如实披露**了 `n=3 → n=0` 的格式变更及其动机（否则 r1/r2 两个改动会被 `if __name__` 一行上下文并成一个 hunk），但**未披露该变更使 plain `git apply --check` 由 r1 的通过变为失败、必须加 `--unidiff-zero`**，卡面也从未用 git 做过 apply-check ⇒ 记为发现 **N-01（P2）**。

## 8. F-02 … F-08 逐条核（r1 的 7 条 P3）

| 编号 | 卡面处置 | 我的独立核验 | 结论 |
|---|---|---|---|
| **F-02** | erratum：`coverage run`=0、`coverage report --fail-under=84`=2、`--fail-under=0`=0；不改 Q3 行/不改原证据字节 | ①新证据 `evidence\rgm2\coverage_rc_probe_r2.txt`（848 B，sha 在 `MANIFEST_r2` 内命中）三行 rc = **0 / 2 / 0**，末行 `Coverage failure: … less than fail-under=84`；②**我用 coverage 7.12.0 在 %TEMP% 独立复现同一 rc 三元组**（`run`=0、`report`=2、`report --fail-under=0`=0）；③现盘 `.coveragerc [report] fail_under = 84` 只读复核为真；④**Q3 所在的 r1 段字节未动**（`commands.md` 前 13251 B sha 仍 `bde20daa…`）、`evidence/rgm/coverage_subset_fixed.txt` 在 r1 `MANIFEST` 57/57 内 | ✅ 已处置 |
| **F-03** | 19 pins = **10 MATCH / 9 DRIFT**（与 r1 同分割），不回写 pin 表 | **我复算 19 pins**：①按 r2 归档 `evidence\rgm2\pins_r2.json`（其记录时点）= `sha_match_now=10 / sha_drift_now=9`，`drift_ids` = register×5 + closure decision×3 + `iso_cli_before`×1 ⇒ **与 r1 分割完全相同**；②**本复审时点 2026-09-24 22:38 现盘读数 = 8 MATCH / 11 DRIFT**——多出的 2 条是 `owner_decisions_sec22/sec23`，因 `OWNER_DECISIONS.md` 于 **22:15:34** 被外部追加（`c13feca4…/64386` → `093cb686…/67435`），且 `REMEDIATION_REGISTER.md` 于 **22:13:25** 再被追加（r2 读数 `e3b24ef1…/314823` → 现 `937a0aec…/328271`）——**均发生在 r2 复算（`verify_pins_r2.py` mtime 22:03:05）之后**；③**50 条钉行逐字全部仍在现盘**（register 钉行 delta=+3、closure decision delta=0、`OWNER_DECISIONS` 钉行 delta=0、SA-DEFECT/I-09-C 各 delta=0）；④pin 表 `binding.json` 字节未改（`caca43e8…` == r1 DELIVERABLES 行） | ✅ 已处置；**读数必须注明时刻**（见上） |
| **F-04** | C1b 产物 mtime 00:04:17 晚于 `oracle.sha256` 23:50:41 ⇒ 登记为冻结后产物，「冻结前已跑」不作断言 | mtime 复测：`oracle.md 2026-09-23 23:50:38`、`oracle.sha256 23:50:41`、`evidence\mech\mech_cases.json 23:40:19`（冻结前）、`evidence\mech\grep_120_and_emitter.txt 2026-09-24 00:04:17`（冻结后）⇒ 与卡面一致；`commands.md` R2-步骤6 F-04 行原文在盘 | ✅ 已处置 |
| **F-05** | `report_SA-DEFECT.md` 字节从未改动，sha `374a5770…` / 26047 B == pin；handoff 措辞更正为「以本卡 oracle §5/decision §1 承载更正；封存件字节不动」 | 我复算：`AUDIT-GOAL\a20260923-01\evidence\report_SA-DEFECT.md` = **26047 B / `374a57700884a6ee427286a2e27c544746dfe004dd260739dcabdceba74d37df`** == pin（`sa_defect_wrong_mechanism` MATCH）；**L165 原文仍是**「`\| F12（断管归一化） \| 断言在返回后开火 \| REG:592 \| …`」；`handoff.md` `## review_round_2` F-05 行已写入更正措辞（r1 §1 表的旧措辞仍在前缀内，卡面已如实标注其「不实」） | ✅ 已处置 |
| **F-06** | 「**已补列**：`decision.md §5` 家族 grep 行号清单补 `test_publication_pipeline.py:315`；87/332/360 不变；文件集合仍恰 8」 | ①我用同一正则复测生产 `tests\`：**恰 8 文件 / 15 行**，`test_publication_pipeline.py` 命中 **87, 315, 332, 360** ⇒ 实体事实全部为真；②**但 `decision.md` §5（L71）逐字仍只列 `87,332,360`，没有 315**；全文唯一出现 315 的是 `decision.md` L124（§7.5 摘要行），且该行**声称**「decision §5 …补列 315」；`handoff.md` L85 与 `handoff.json` 同样声称「`decision.md §5` … 补 315」/「decision sec5 … now also lists …315」 ⇒ **§5 位于 append-only 的 r1 前缀内（前 11542 B 必须逐字节不变，我已复算 `fad182c0…`），不可能被补列**；r1 的 F-06 原要求是「补列 315 **或注明已排除注释行**」，实际只在 §7.5/commands/handoff 三处记录 | ⚠️ **处置记录与被指位置不符 ⇒ 发现 N-02（P3）** |
| **F-07** | r1 首轮 RED probe 被同名覆盖的披露 + r2 新规则「覆盖前先改名归档」 | mtime 复测：`evidence\rgm\green\probe_run1_after_fix.json = 00:14:27` < `evidence\rgm\red\probe.json = 00:32:41` ⇒ 覆盖事实成立；`commands.md` R2-步骤6 F-07 行原文在盘；r2 归档实物在盘：`evidence\rgm2\failed_try1_expect_table\probe.json`（5453 B）与 `evidence\rgm2\prefix_selfcheck_r2_failed1.json`（7787 B），均为**改名独立路径**，commands 明写「**不作证据**」 | ✅ 已处置 |
| **F-08** | 补「只中和不 catch」臂；冻结 M-1/M-2 与 `oracle §4` 一字未改 | 补臂已跑（§4 变异③：4 臂全 0、无产品文本、无 `Exception ignored`、4F/5P 打红）；`oracle.md` sha 仍 `7fecfaea…` ⇒ §4 一字未改；`decision.md` §4 属 r1 前缀（`fad182c0…` 前缀复算通过）⇒ 一字未改；§7.3 关闭语句在盘 | ✅ 已处置 |

**r1 七条 P3：7/7 处置；其中 F-06 的「处置位置」记录不实（N-02）。**

## 9. 两起簿记事故的独立复算

### ① `commands.md` 丢尾换行

| 检查 | 结果 |
|---|---|
| 当前 `commands.md` **前 13251 B** sha256 | **`bde20daace862f4f080793cb44697a23ce230086cce5464ed65d6b5de4aa7eae`** == r1 `DELIVERABLES.sha256` 行 ⇒ **还原成功** |
| 前 13250 B sha256 | `9da00721b1ea5d122e0b821b59d0b7715b1d788f1324f6627804cc78a4b66982` ≠ 钉值 ⇒ 末字节 `\n`（我读到 `byte[13250] = 0x0a`）确属还原而非巧合 |
| 追加起点 | `byte[13251..] = "---\n\n## P…"` ⇒ r2 内容从 13251 起，r1 前缀完整 |

### ② `DELIVERABLES.sha256` CRLF→LF

| 检查 | 结果 |
|---|---|
| 当前 `DELIVERABLES.sha256` **前 725 B** sha256 | **`c7d8c583eeea3a754ae8272d54e36757896a93c71a977447370c53c5b4cb5ce8`** == r1 钉值 ⇒ **重建成功** |
| 前 725 B 行尾 | **9 个 CRLF / 9 个 LF** ⇒ 9 行全 CRLF，与 r1 逐字节同 |
| 全文件 | 1632 B；总 CR=9、LF=22 ⇒ r1 九行保持 CRLF，r2 追加块用 LF（r1 面不受影响） |
| r1 九行 vs 现盘文件 | r1 九行逐条复算全部命中现盘文件（`oracle.md 7fecfaea…`、`oracle.sha256 a6995bba…`、`binding.json caca43e8…`、`commands.md bde20daa…`、`decision.md fad182c0…`、`changes.diff` r1 值 `f0a01489…`、`handoff.md 14dc9b62…`、`recovery.md 1c58a8ef…`、`evidence/MANIFEST.sha256 29efb109…`）——前三/后四为现盘实测，`changes.diff` 与 `commands/decision/handoff` 以其**前缀复算**命中 |
| r2 追加六行 | `commands a64eac68…`、`decision d9e85550…`、`handoff 30bfe950…`、`changes d1a79376…`、`handoff.json 19a2969e…`、`evidence/rgm2/MANIFEST_r2.sha256 6f565c28…` —— **6/6 复算命中** |

**两个失败产物均已改名归档、commands 明写不作证据**（`prefix_selfcheck_r2_failed1.json`、`failed_try1_expect_table\probe.json`）。备注（非发现）：这两件同时也被 `evidence\rgm2\MANIFEST_r2.sha256` 收录为字节留痕条目（24/24 复算命中），收录本身只保证字节不丢，不改变其「不作证据」的定位。

**结论：两起簿记事故的自述与现盘字节完全相符。**

## 10. 前缀 / 台账 / 证据清单

| 项 | 我的复算 |
|---|---|
| `commands.md` 前 13251 B | `bde20daa…` == r1 钉值 ✅ |
| `decision.md` 前 11542 B | `fad182c0ec7391de922750184c8b1b4434841643ba90e783e39e1e62e102ffe2` == r1 钉值 ✅ |
| `handoff.md` 前 7077 B | `14dc9b6272f839ec9ad415ed44709398bfb064efa8087642436b4c4ec7f40f4d` == r1 钉值 ✅ |
| r1 `evidence/MANIFEST.sha256` 本身 | 5838 B / **`29efb1094270d18fff8a1d3ed7c7cd12b1045c9aa7290bc4ef51a6224023c571`** == r1 DELIVERABLES 行 ⇒ **该台账字节未改** ✅ |
| r1 `MANIFEST` 57 条 | **57/57 全部复算一致**（0 missing / 0 mismatch）⇒ r1 `evidence/**` 零改写 ✅ |
| r2 `evidence\rgm2\MANIFEST_r2.sha256` | 2501 B / `6f565c28…` == DELIVERABLES 追加行；**24/24 复算一致**（新台账，不列自身） ✅ |
| r1 复审报告两件 | `reviewer_report.md` **26073 B / `9941660588641a31a22449365982392a28f4fc5b2451a69ca8587f38ad3074e8`**；`reviewer_report.sha256` 85 B，内容 `99416605…  reviewer_report.md` ⇒ **只读未改** ✅ |
| `binding.json` / `evidence\pins_freeze.txt` / `recovery.md` | `caca43e8…` / `522cd765…`（在 r1 MANIFEST 内）/ `1c58a8ef…` ⇒ **零改写** ✅ |
| `handoff.json`（r2 新建） | 6575 B / `19a2969e…` == DELIVERABLES 追加行；`status="review_pending"`、`implementer_signed=false`、`signed_by=null`、`blocked_by=[]`、`review_source.sha256=99416605…/bytes=26073/verdict=changes_required` ⇒ 与自述一致 ✅ |

## 11. 边界（收尾复测）

- `git -c core.quotepath=false diff HEAD --name-only` → **TOTAL=3826，非 `.planning` = 0** ✅（本仓**未使用 `git status`**）
- 生产 `scripts/revenue_forecast.py` = **`2a2dfede7941b0fac972d802d25eb71f798c1ebdb83226bbf8528481b9669e36`**（5333 B）== pin `prod_cli_before` ✅
- 生产树 `tests/test_stdout_flush_exit_domain.py` **不存在**（`Test-Path=False`）⇒ r2 只在 iso ✅
- 全部测试/探针只在 `%TEMP%\wc4r2rev\`；`evidence\rgm\**`、`evidence\rgm2\**` 与 attempt 既有字节**零写入**（由 57/57 + 24/24 复算反证）
- 未执行任何 git 写命令；未联网；未创建/修改 `handoff.json`；未写 status

## 12. 发现表

| 编号 | 级别 | 位置 | 证据（本复审实测） | 建议处置 |
|---|---|---|---|---|
| **N-01** | **P2** | `changes.diff`（r2 重生成，`difflib n=0`）；`commands.md` R2-C10b；`handoff.json.checks.changes_diff` | 本仓与隔离副本各跑一次：`git apply --check <changes.diff>` → **raw rc=1**，`error: patch failed: scripts/revenue_forecast.py:127` / `patch does not apply`（`core.autocrlf=false` 与 `true` 结果相同）；`git apply --check --unidiff-zero` → **rc=0**，且实打后 LF 归一产物恰为 `405fec6d…` / `083b92a5…`。对照：**r1 旧 diff（`f0a01489…`，n=3）plain `git apply --check` rc=0**。卡面已披露 n=3→n=0 的**动机**，但**未披露其对 plain `git apply` 的影响**，且卡面「apply-check」实为字节重建、从未用 git | 在 `commands.md`/`handoff.md` 追加一行「本 diff 为 0-context（U0），`git apply` 需 `--unidiff-zero`」，或由合并批确认其应用方式；**若合并批本就使用 `--unidiff-zero`/非 git 工具，可降为 P3** |
| **N-02** | **P3** | `handoff.md` L85、`handoff.json.findings[F-06].disposition`、`commands.md` R2-步骤6 F-06 行、`decision.md` L124 | 三处均写「`decision.md` **§5** …补 `test_publication_pipeline.py:315`」/「decision sec5 … now also lists …315」，但 `decision.md` §5（**L71**）逐字仍只列 `87,332,360`，**无 315**；全文唯一 315 在 L124（§7.5 摘要）。§5 位于 append-only r1 前缀（前 11542 B = `fad182c0…` 我已复算）内，**结构上不可能被补列**。r1 F-06 的原要求「补列 **或** 注明已排除注释行」实际只在 §7.5/commands/handoff 落地。实体事实（315 是注释行、8 文件/15 行、87/332/360 不变）我复测**全部为真** | 把三处措辞改为「在 §7.5/本表补列」或「§5 位于 r1 冻结前缀不可改，改于 §7.5 补列」，与 F-05 的诚实口径一致 |
| —（信息，**非本卡缺陷**） | — | `binding.json` 19 pins 读数时点 | r2 的 `10 MATCH / 9 DRIFT` 是 **2026-09-24 22:03 前后**的读数（`pins_r2.json` 存档为证，`drift_ids` 与 r1 完全同分割）；本复审 **22:38** 现盘读数为 **8 MATCH / 11 DRIFT**，多出的 2 条源于 `OWNER_DECISIONS.md`（22:15:34 外部追加）与 `REMEDIATION_REGISTER.md`（22:13:25 再追加）——**均晚于 r2 复算**。50 条钉行逐字全部仍在 | 任何后续复审引用 pin 数字**必须标时点**；**不需本卡处置** |

**级别统计：P1 = 0，P2 = 1（N-01），P3 = 1（N-02）。**

## 13. unverified / 本复审未验证清单（如实携带）

1. **家族 8 文件 64 passed/48 subtests 本轮（r2）与本复审均未重跑**：我独立复现了根因——`tempfile.mkdtemp()` 建得进、**向其写文件即 `PermissionError: [Errno 13]`**，纯 python 进程同样复现；`tests/conftest.py` 的 `_isolate_publication_registry` 即 `tmp_path_factory.mktemp`。⇒ 只能字节级核验 r1 的 5 件 `family_*`（`before/after/final_raw.txt`、`compare.txt`、`compare_v1testfile.txt`，**全部在 r1 `MANIFEST` 57/57 内命中**）+ 静态不相交（我 grep 8 个家族文件，`--help`/`-h` **0 命中**）。**未证的是「本次会话重跑得到 64/48」。**
2. **单模块覆盖门 `revenue_forecast.py ≥60%` 未复测**（r1 的 73% 依赖直调 `main()` 的进程内覆盖，本会话不可运行）。我只独立验证了 F-02 的 **rc 语义**（0/2/0），**未重跑 r1 的 73% 子集，也未采用 r2 的 38% 子集作门结论**（卡面已明示「不可比、不作门结论」，其 `coverage combine` rc=1 失败也如实留档）。
3. **Linux/macOS 断管码值未测**（卡面已披露，本复审照录）。
4. **`--help`/`-h` 之外的 `SystemExit`-in-`main` 组合未穷举**（如 `parser.exit(status)` 非 0/2 码）；映射规则 `int→原值 / None→0 / 其余→2` 我读了源码但只有 argparse 实际产生的 0/2 被实测。
5. **stderr 汇本身断管未构造**（oracle §6 明列非目标）。
6. **真仓库内的 `git apply` 实施**未执行（只执行 `--check`，`--unidiff-zero` 的实际 apply 在隔离副本执行）。
7. **r2 归档读数（`pins_r2.json` 的 10/9）无法在我时点原样复现**——只能以该存档 + mtimes 认定其为当时真值。
8. 本复审**未**复刻 `production_zero_write_*.txt` 的树 sha 算法（卡面未给清单）；以 `git diff HEAD --name-only` 非 `.planning`=0 + 生产 CLI sha==pin + 新测试不在生产树替代。
9. 本复审**未使用 `git status`**（卡面纪律禁用），因此未复核卡面提到的「2 条既有未跟踪件」。

## 14. 本复审**没有做**的事

- **没有**修改 `.planning\` 之外任何文件；**没有**改动本 attempt 内任何既有字节（r1 与 r2 的全部证据/交付/两份 r1 复审报告只读；由 57/57 + 24/24 + 前缀复算反证）。
- **没有**覆盖 r1 的 `reviewer_report.md` / `reviewer_report.sha256`。
- **没有**创建或修改 `handoff.json`；**没有**改任何 status；**没有**替实现者落定或代签。
- **没有**执行任何 git 写命令（add/commit/checkout/stash/restore/reset 一律未用）；**没有**执行 `git status`；只用了 `git diff HEAD --name-only` 与 `git apply --check`（只读）。
- **没有**联网。
- **没有**运行卡面会写 `evidence\` 的 harness（`probe_help_r2.py`、`run_pytest_r2.py`、`capture_checks_r2.py`、`apply_fix_r2.py`、`make_diff.py`、`verify_*.py`、`finalize_ledgers_r2.py` 一律未执行）；变异切换由我在 %TEMP% 副本内自写脚本完成。
- **没有**在仓库内创建任何临时文件（临时物全部在 `%TEMP%\wc4r2rev\`）。
- **没有**把任何未验证项写成已验证（§13 全条照录）。

## 15. 结论

- r1 的唯一 **P1 = F-01 已关闭**：修前态 `--help`/`-h` × 断读端在我这里原样复现 **raw rc=120、无产品文本**；修后态为 **raw rc=2、stderr 逐字 `error: stdout flush failed: [Errno 22] Invalid argument`、`Exception ignored` 0 命中**；读端正常臂 0/0/0/0/2 且 stdout 形状全对；产品测试由 **1 failed, 8 passed → 9 passed**；三个变异臂（`4e6b64a7`→120、`99fc716a`→120 且文本与 CPython 报错并存、`4f9d7803`→0 且无文本）**全部打红**；oracle 一字未改、未走 owner 豁免。
- r1 的 7 条 P3 **7/7 有处置**，其中 F-02/F-03/F-04/F-05/F-07/F-08 经我独立复算为真，**F-06 的处置位置记录不实**（N-02）。
- 棘轮（三者 18 == frozen 18）、ruff 0.15.18、`changes.diff` 字节重建、前缀与两起簿记事故还原、r1/r2 两份证据台账、生产零写边界——**全部复算通过**。
- 新发现 1 条 P2（`changes.diff` 为 0-context，plain `git apply --check` 失败、需 `--unidiff-zero`，卡面未披露）与 1 条 P3（F-06 补列位置记录不实）。
- **P1 = 0** ⇒ 按裁决规则：

VERDICT: ACCEPT
