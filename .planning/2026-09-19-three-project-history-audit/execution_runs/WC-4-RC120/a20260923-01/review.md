# WC-4-RC120 复审裁决落定（review.md）

> **本文件由 carrier-landing 簿记 pass 创建，创建前本 attempt 无 `review.md`。**
> 创建前本 attempt 根仅含：`binding.json` / `changes.diff` / `commands.md` / `decision.md` / `DELIVERABLES.sha256` / `handoff.json` / `handoff.md` / `oracle.md` / `oracle.sha256` / `recovery.md` / `reviewer_report.md` / `reviewer_report.sha256` / `reviewer_report_r2.md` / `reviewer_report_r2.sha256`，以及 `evidence/` `harness/` `iso/` 三个目录（`iso\rf\audit_review\2026-09-18_real_company_skill_audit\independent\review.md` 是隔离副本里**另一仓**的文件，与本卡无关）。
> **本文件只转录，不产生新裁决、不自签**：`implementer_signed = false`、`verdict_is_transcribed_not_authored = true`。
> 转录者 = carrier-landing 簿记执行者（与实现者、复审者均非同一人）；本 pass 未重跑任何命令、未联网、未跑测试、未做任何 git 写操作、未使用 `git status`。

---

## 0. 裁决来源（唯一权威）

| 项 | 值 |
|---|---|
| **当前裁决 carrier（唯一权威）** | `reviewer_report_r2.md`（本 attempt 内，全程只读） |
| 字节 | **28878 B** |
| sha256 | **`ddbd536c47b54822e1ff2af79f02d48632907b54cc057dcda1f43f6cf80ca001`** |
| 侧车 | `reviewer_report_r2.sha256`（**88 B**，内容 `ddbd536c47b54822e1ff2af79f02d48632907b54cc057dcda1f43f6cf80ca001  reviewer_report_r2.md` + LF；侧车自身 sha `cfed6122474bba684638a4f8e26f70052c589f6a791dbe55bda9069f59fb959c`；本 pass 只读，0 字节写入） |
| 总行数 | **232 行**（LF-only、0 CR、末行带 LF） |
| 裁决行 | 第 **232** 行；字节区 **[28862, 28877]**（0-based、含行尾 LF，**16 B**）；该行 sha256 `ffd796ea6572fdaf4dce6d9984e6e9294cf8c0c564ce345d73132bf29aa1b3b4` |
| **裁决行文本** | **`VERDICT: ACCEPT`** |
| 计数 | **P1 = 0 / P2 = 1（N-01）/ P3 = 1（N-02）**（报告 §12 末行「级别统计：P1 = 0，P2 = 1（N-01），P3 = 1（N-02）。」） |

| 项 | 值 |
|---|---|
| **历史裁决 carrier（只读保留，不覆盖）** | `reviewer_report.md`（r1） |
| 字节 / sha256 | **26073 B** / **`9941660588641a31a22449365982392a28f4fc5b2451a69ca8587f38ad3074e8`** |
| 侧车 | `reviewer_report.sha256`（85 B，内容 `99416605…  reviewer_report.md` + LF；侧车自身 sha `381efe271046e67f75a7cac31b0b019a99b8117f2d27ff75ddc57351e2efc490`） |
| 总行数 | **161 行**（LF-only、0 CR、末行带 LF） |
| 裁决行 | 第 **161** 行；字节区 **[26047, 26072]**（含行尾 LF，**26 B**）；该行 sha256 `501cc91c3dc9566eeb7032d7c8aa2faccb5b68a41bf1582d848c4193f32d9488` |
| 裁决行文本 | `VERDICT: changes_required` |
| 计数 | **P1 = 1（F-01）/ P2 = 0 / P3 = 7（F-02…F-08）**（r1 报告 §3 末行） |

字节区定义（与本计划既往落定一致）：0-based 字节偏移，按文件处于上述 sha256 状态时计算；**单行区含行尾 LF**；**多行区含内部 LF、不含末尾 LF**。

本 pass 复算的其余区段（供父/后续复算）——

- **r2 `reviewer_report_r2.md`**：§2 F-01 关闭 [2324,5633] / 3310 B / `78a89734…`、§4 三变异臂 [6331,7969] / 1639 B / `276b6728…`、§5 产品测试 [7973,9775] / 1803 B / `e1d4342e…`、§6 棘轮与 lint [9779,10699] / 921 B / `8b0baaf6…`、§7 changes.diff [10703,12615] / 1913 B / `d8d73c98…`、§8 F-02…F-08 [12619,17632] / 5014 B / `0ec482ae…`、§9 两起簿记事故 [17636,19761] / 2126 B / `45d04a96…`、§10 前缀台账 [19765,21242] / 1478 B / `b3c7a092…`、§11 边界 [21246,21932] / 687 B / `a233a6bc…`、§12 发现表 [21936,24496] / 2561 B / `70fb50f3…`（其中 N-01 行 [22050,22996] / 947 B / `046e8eb9…`、N-02 行 [22998,23872] / 875 B / `d967832d…`）、§13 unverified [24500,26589] / 2090 B / `783962e2…`、§14 没有做 [26593,27716] / 1124 B / `1fa5e886…`、§15 结论含裁决行 [27720,28875] / 1156 B / `1118b4a9…`。
- **r1 `reviewer_report.md`**：§3 发现表 [16518,21713] / 5196 B / `abf2dea2…`、§4 unverified [21717,24046] / 2330 B / `147a86a1…`、§5 边界 [24050,25578] / 1529 B / `ae6341ba…`、§6 结论含裁决行 [25582,26070] / 489 B / `5afd4f5c…`。

---

## 1. 两轮裁决链（两条都要在载体里可见）

```
r1  reviewer_report.md:161   VERDICT: changes_required   P1=1(F-01) / P2=0 / P3=7(F-02…F-08)
                                    │  （r1 的 changes_required 是历史，字节只读保留、不覆盖）
                                    ▼
r2  reviewer_report_r2.md:232 VERDICT: ACCEPT             P1=0 / P2=1(N-01) / P3=1(N-02)
                                    │  （r2 的 ACCEPT 是最新裁决 = 当前唯一权威）
                                    ▼
    carrier-landing 簿记转录 → review.md + handoff.json(status) + evidence/WC-4-RC120/qualification.json
    （纯转录，不产生新裁决、不自签）
```

| 轮次 | carrier | 行号 | 字节区 | sha256 | 裁决 | 计数 |
|---|---|---|---|---|---|---|
| **r1** | `reviewer_report.md`（26073 B） | **L161** | **[26047, 26072]**（26 B，含 LF） | `9941660588641a31a22449365982392a28f4fc5b2451a69ca8587f38ad3074e8`（整文件）／裁决行 `501cc91c3dc9566eeb7032d7c8aa2faccb5b68a41bf1582d848c4193f32d9488` | `changes_required` | P1=1 / P2=0 / P3=7 |
| **r2** | `reviewer_report_r2.md`（28878 B） | **L232** | **[28862, 28877]**（16 B，含 LF） | `ddbd536c47b54822e1ff2af79f02d48632907b54cc057dcda1f43f6cf80ca001`（整文件）／裁决行 `ffd796ea6572fdaf4dce6d9984e6e9294cf8c0c564ce345d73132bf29aa1b3b4` | **`ACCEPT`** | **P1=0 / P2=1 / P3=1** |

- **r1 的唯一 P1 = F-01（`--help` × 断读端 raw rc=120）在 r2 已关闭**（详见 §2）；r1 的 7 条 P3 **7/7 有处置**，其中 **F-06 的处置位置记录不实 → r2 记 N-02（P3）**（详见 §8、§9）。
- **r2 P1 = 0 ⇒ 裁决是 `ACCEPT` 而非 `changes_required`**（报告 §15 末三行：「**P1 = 0** ⇒ 按裁决规则：/ VERDICT: ACCEPT」）。
- r1 `reviewer_report.md` 与 r2 `reviewer_report_r2.md` **两份都只读、都在本 attempt 内保留**，本 pass 对两份报告 + 两个 sha 侧车的写入字节数 = **0**。

---

## 2. F-01 关闭证据（复审者在 %TEMP% 隔离副本亲测，逐字抄 rc 与 stderr）

环境：解释器 `C:\Miniconda\python.exe` 3.13.9；cwd = `%TEMP%\wc4r2rev\rf`（`iso\rf` 1976 文件 / 28 MB 整树副本）；故障臂 = `os.pipe()` → `Popen(stdout=w_fd)` → 关 `w_fd` 与 `r_fd`，只读 `Popen.returncode`；复审**未运行卡面 `probe_help_r2.py`**（它会写 `evidence\rgm2\`），改用自建 `%TEMP%\wc4r2rev\rev_probe.py`。

### 2.1 修前态（r1 交付 `4e6b64a789b97f30daf5def474bcd5a1d19cbc45b555e554b23fb8ecafe9e977`，由 r2 快照独立反推、sha 命中）

| 臂 | 断读端 raw rc | stderr 关键行 | 产品文本 | `Exception ignored` |
|---|---|---|---|---|
| `--help` | **120** | `Exception ignored on flushing sys.stdout:` / `OSError: [Errno 22] Invalid argument` | **无** | **在** |
| `-h` | **120** | 同上（逐字两行） | **无** | **在** |
| `<input> --validate-only` | 2 | `error: stdout flush failed: [Errno 22] Invalid argument` | 在 | 无 |
| `--version` | 2 | `error: stdout flush failed: [Errno 22] Invalid argument` | 在 | 无 |
| 无参数 usage | 2 | `usage: …` + `error: the following arguments are required: input` | 无（不适用） | 无 |
| 读端正常 5 臂 | **0 / 0 / 0 / 0 / 2** | — | — | — |

⇒ r1 的 P1 现象原样复现：`--help`/`-h` raw rc=**120**、stderr **只有 CPython 两行**、**无产品错误文本** ⇒ `_finalize_exit_status` 未被执行。

### 2.2 修后态（r2 交付 `405fec6d7ea23324bd671e144caa994889e076104d67560bc3b1d0f830599bda` = 当前 iso 字节，`iso_now == cli_r2_state` 实测 `true`）

| 臂 | 断读端 raw rc | stderr 关键行 | 产品文本 | `Exception ignored` |
|---|---|---|---|---|
| `--help` | **2** | **`error: stdout flush failed: [Errno 22] Invalid argument`** | **在** | **0 命中** |
| `-h` | **2** | 同上 | **在** | **0 命中** |
| `<input> --validate-only` | **2** | 同上 | 在 | 0 命中 |
| `--version` | **2** | 同上 | 在 | 0 命中 |
| 无参数 usage | **2** | usage 文本（stderr-only，产品 flush 文本不出现属正常） | — | 0 命中 |
| 读端正常 5 臂 | **0 / 0 / 0 / 0 / 2** | — | — | — |

- 读端 stdout 形状逐臂断言 **5/5 全对**：`--help`→以 `usage:` 开头；`-h`→以 `usage:` 开头；`--validate-only`→逐字 `valid`；`--version`→以 `revenue-forecast ` 开头；usage→stderr 含 `usage:`。
- 读端 `--help` 的 stdout **1612 B，与生产 pristine 逐字节同 sha** ⇒ 正常路径输出形状/字节未变。
- 冻结不变式 O-1（rc ∈ {0,2}）在 `--help`/`-h`/`validate`/`version`/`usage` × 断读端 5 条路径上全部成立（2/2/2/2/2）。
- **对照：生产 pristine `2a2dfede7941b0fac972d802d25eb71f798c1ebdb83226bbf8528481b9669e36`（5333 B，== pin `prod_cli_before`）**：`--help`=**120**、`-h`=**120**、`validate`=**120**、`version`=**120**、`usage`=**2** —— 与卡面「非本卡回归、待合并 `changes.diff` 后修复」一致（本复审只读执行）。

**⇒ r2 结论：F-01 关闭。** 另有 §2.3 独立证明「只动 `__main__` 块」：按 `if __name__ == "__main__":` 截断重建的 r1 文本与 `cli_r1_state.py` 快照逐字节相等（`derived_r1_equals_snapshot_r1 = true`）⇒ r2 相对 r1 的字节增量只有 `__main__` 块，`_finalize_exit_status` / `_neutralize_broken_stream` 一字未改。

---

## 3. 三变异臂全打红（各记 raw rc；sha 由复审独立重建并复算）

| 臂 | 复审重建的 iso sha | `--help` | `-h` | validate | version | usage | stderr 关键行 | 产品测试（raw） |
|---|---|---|---|---|---|---|---|---|
| **变异①回退包装**（回 r1 态） | `4e6b64a789b97f30daf5def474bcd5a1d19cbc45b555e554b23fb8ecafe9e977`（由 r2 文本反推，与 r1 快照逐字节相等；与卡面自述相同） | **120** | 120 | 2 | 2 | 2 | 仅 CPython 两行、**无产品文本** | **1 failed, 8 passed**（`assert 120 == 2`） |
| **变异②只 catch 不换流**（= 冻结 M-2） | `99fc716ad9ef6ce80f5e2e50062027f2e2e0354a432774034ad8c8a6d6891153` | **120** | 120 | **120** | **120** | 2 | **产品文本与 `Exception ignored` 并存**（逐字两段都在） | **3 failed, 6 passed** |
| **变异③只中和不 catch**（F-08 补臂） | `4f9d78034b46e8054ef9807dafc38f9728737269f2be5c6eeca505012ddbd95b` | **0** | 0 | 0 | 0 | 2 | **无产品文本、无 `Exception ignored`（stderr 空）** | **4 failed, 5 passed** |

- 三臂读端正常矩阵均 **0/0/0/0/2**、形状全对。
- **三个臂都打红**：① 新判据 `--help` 条红；② 端到端 120 + `assert sys.stdout is not broken` 类断言红；③ 端到端 rc≠2 + 无文本 + `normalizes_flush_failure_to_2` + `survives_broken_stderr` + 新 `--help` 条红。
- **变异③ rc=0 ∈ {0,2} 但无产品文本、fail-closed/informative 被破坏 ⇒ 违反 G-2**；该臂正是 r1 P3 **F-08** 要求补的臂，本轮已补并打红。
- 所有状态切换只发生在 %TEMP% 副本；**卡面 iso 终态仍为 `405fec6d…`**（复审未改 attempt 任何字节）。

---

## 4. 产品测试 9 条

| 状态 | 结果 | pytest rc | 卡面自述 | 相符 |
|---|---|---|---|---|
| **修前**（r1 代码 `4e6b64a7` + 新 9 条测试文件） | **1 failed, 8 passed** | 1 | 1 failed, 8 passed | ✔ |
| **修后**（r2 `405fec6d` + 9 条） | **9 passed** | **0** | 9 passed（r1 8 条 = 8/0） | ✔ |
| 变异① `4e6b64a7` | 1 failed, 8 passed | 1 | 1F/8P | ✔ |
| 变异② `99fc716a` | 3 failed, 6 passed | 1 | 3F/6P | ✔ |
| 变异③ `4f9d7803` | 4 failed, 5 passed | 1 | 4F/5P | ✔ |
| 生产 pristine（参考） | 7 failed, 2 passed | 1 | （r1 8 条时为 6F/2P，+1 新条 ⇒ 7F/2P 自洽） | ✔ |

- **修前失败原文（逐字）**：`AssertionError: --help with a broken stdout pipe must land in the frozen domain {0,2} as rc=2, got 120; stderr='Exception ignored on flushing sys.stdout:\r\nOSError: [Errno 22] Invalid argument\r\n'`
- **绕行只改运行方式、不改判据**：`--noconftest` 只是绕开会话夹具 `_isolate_publication_registry`（`tmp_path_factory.mktemp` 在本沙箱确实被拒——**复审独立复现：`tempfile.mkdtemp()` 建得出目录、向其中 `open(...,'w')` 报 `PermissionError: [Errno 13]`**，纯 python 进程同样复现）；该夹具的唯一作用就是设 `REVENUE_PUBLICATION_REGISTRY`，复审显式指向 `%TEMP%` 等价替代。**判据断言本身（rc、`stdout flush failed` 文本、`Errno`、`Exception ignored` 缺席、`sys.stdout is not broken`、`_NullStream` 回退、正常臂 0/2）逐条未改**——复审读了测试源码并逐条复跑。⇒ **只改运行方式，未改判据值。**
- 测试文件：**7270 B / 195 行 / 9 个 `def test_` / sha `083b92a535bf43f0ea0863a979579c2e6f55c4eb1e63abbefa7a7b35e1d533aa`**（与卡面一致）。
- 命令形态：`python -B -m pytest tests\test_stdout_flush_exit_domain.py -q -p no:cacheprovider --noconftest`，cwd=%TEMP% 副本，`REVENUE_PUBLICATION_REGISTRY` 显式指向 %TEMP%。

---

## 5. 棘轮 / lint

**棘轮**（复审先自写 `_mccabe`/`_max_complexity` 逐行对齐 `tools/tests/test_complexity_ratchet.py` 独立复算，再跑卡面 `harness\check_ratchet_own_file.py`（纯读）交叉验证；frozen `revenue_forecast.py` = 18）：

| 目标 | 复算 max | worst | 结果 |
|---|---|---|---|
| iso r2（`405fec6d`） | **18** | `main:18` | ≤18 ✅ |
| iso pristine（`evidence/rgm/cli_original.py` = `2a2dfede`） | **18** | `main:18` | ✅ |
| 生产（`2a2dfede`） | **18** | `main:18` | ✅ |
| r1 态（`4e6b64a7`，附加参考） | **18** | `main:18` | ✅ |

**⇒ iso r2 / pristine / 生产 / r1 四者均 18（`main:18`）== frozen 18**；卡面 `check_ratchet_own_file.py` 重跑 `iso_fixed=18 / iso_pristine=18 / production=18 / frozen_max=18`、`OWN_FILE_RATCHET_OK`、**raw rc=0**，与复算逐值相同。

**lint**：`python -m ruff --version` → **ruff 0.15.18**；`ruff check` 两个交付文件（iso CLI + iso 新测试）→ **`All checks passed!`，raw rc=0**。

---

## 6. `changes.diff`

| 项 | 卡面自述 | 复审实测 |
|---|---|---|
| 大小 / sha | 10114 B / `d1a79376c518eab300400c54badf91e141ed4b50ae0623a6fefe52900ad2856d` | **完全相同** |
| 文件数 | 恰 2 | **恰 2**：`scripts/revenue_forecast.py` + `tests/test_stdout_flush_exit_domain.py` |
| CLI 前后 | `2a2dfede…`（5333 B）→ `405fec6d…`（7647 B） | 完全相同 |
| 新测试 | 7270 B / 195 行 / 9 个 `def test_` | 完全相同 |
| **hunks** | **恰为 `@@ -125,0 +126,44 @@` + `@@ -127 +171,15 @@` + `@@ -0,0 +1,195 @@`** | **完全相同** ⇒ **r1/r2 各一 hunk、增量可辨**（前两条 = CLI 上 r1 一 hunk、r2 一 hunk；第三条 = 新测试文件整体） |
| **独立重建** | — | 复审用 `difflib.unified_diff(..., n=0)` 独立重算 → **与盘上逐字节相同**（`byte_identical=True`，双 sha 同 `d1a79376…`） |
| `git apply --check` | 未跑（卡面 `verify_diff.py` 是字节重建、**从未用 git**） | **raw rc=1（失败）** ⇒ 记 **N-01（P2）**，见 §9 逐字条 |
| `git apply --check --unidiff-zero` | — | **raw rc=0**；实打后 LF 归一产物恰为 `405fec6d…` / `083b92a5…` |
| r1 旧 diff（`evidence/rgm2/changes_r1_preimage.diff`，`f0a01489…`，n=3） | 归档 | plain `git apply --check` **rc=0** |

---

## 7. 两起簿记事故的独立复算结果（逐字抄）

### ① `commands.md` 丢尾换行

| 检查 | 结果 |
|---|---|
| 当前 `commands.md` **前 13251 B** sha256 | **`bde20daace862f4f080793cb44697a23ce230086cce5464ed65d6b5de4aa7eae`** == r1 `DELIVERABLES.sha256` 行 ⇒ **还原成功** |
| 前 13250 B sha256 | `9da00721b1ea5d122e0b821b59d0b7715b1d788f1324f6627804cc78a4b66982` ≠ 钉值 ⇒ 末字节 **`byte[13250] = 0x0a`**（尾换行确属**还原**而非巧合） |
| 追加起点 | `byte[13251..] = "---\n\n## P…"` ⇒ r2 内容从 13251 起，**r1 前缀完整** |

### ② `DELIVERABLES.sha256` CRLF→LF

| 检查 | 结果 |
|---|---|
| 当前 `DELIVERABLES.sha256` **前 725 B** sha256 | **`c7d8c583eeea3a754ae8272d54e36757896a93c71a977447370c53c5b4cb5ce8`** == r1 钉值 ⇒ **重建成功** |
| 前 725 B 行尾 | **9 个 CRLF / 9 个 LF** ⇒ 9 行全 CRLF，与 r1 **逐字节同**（逐字节复原） |
| 全文件 | 1632 B；总 CR=9、LF=22 ⇒ r1 九行保持 CRLF，r2 追加块用 LF（r1 面不受影响） |
| r1 九行 vs 现盘文件 | 逐条复算全部命中：`oracle.md 7fecfaea…`、`oracle.sha256 a6995bba…`、`binding.json caca43e8…`、`commands.md bde20daa…`、`decision.md fad182c0…`、`changes.diff`（r1 值 `f0a01489…`）、`handoff.md 14dc9b62…`、`recovery.md 1c58a8ef…`、`evidence/MANIFEST.sha256 29efb109…` |
| r2 追加六行 | `commands a64eac68…`、`decision d9e85550…`、`handoff 30bfe950…`、`changes d1a79376…`、`handoff.json 19a2969e…`、`evidence/rgm2/MANIFEST_r2.sha256 6f565c28…` —— **6/6 复算命中** |

**两次失败产物已改名归档、`commands.md` 明写不作证据**：`evidence\rgm2\prefix_selfcheck_r2_failed1.json`（7787 B）与 `evidence\rgm2\failed_try1_expect_table\probe.json`（5453 B），均为**改名独立路径**。备注（非发现）：这两件同时被 `evidence\rgm2\MANIFEST_r2.sha256` 收录为字节留痕条目（24/24 复算命中）——**收录本身只保证字节不丢，不改变其「不作证据」的定位**。

**⇒ 复审结论：两起簿记事故的自述与现盘字节完全相符。**

---

## 8. r1 的 F-02…F-08 逐条终态（r1 报告 + r2 复算合并转录）

| 编号 | r1 原要求（r1 报告 §3） | 卡面处置 | **r2 独立核验后的终态** |
|---|---|---|---|
| **F-02** | P3：`commands.md` P1 表 Q3 行 raw rc 记 0，而 `coverage_subset_fixed.txt` 末行 `Coverage failure: total of 73 is less than fail-under=84` ⇒ report 步 rc≠0；要求更正 rc 记录或写明 0 属哪一步，不改证据字节，以 erratum 记载 | erratum：`coverage run`=0、`coverage report --fail-under=84`=2、`--fail-under=0`=0；不改 Q3 行 / 不改原证据字节 | ✅ **已处置**：①新证据 `evidence\rgm2\coverage_rc_probe_r2.txt`（848 B，sha 在 `MANIFEST_r2` 内命中）三行 rc = **0 / 2 / 0**，末行 `Coverage failure: … less than fail-under=84`；②**复审用 coverage 7.12.0 在 %TEMP% 独立复现同一 rc 三元组**；③现盘 `.coveragerc [report] fail_under = 84` 只读复核为真；④**Q3 所在的 r1 段字节未动**（`commands.md` 前 13251 B sha 仍 `bde20daa…`）、`evidence/rgm/coverage_subset_fixed.txt` 在 r1 `MANIFEST` 57/57 内 |
| **F-03** | P3：`binding.json` 19 pins 全量重算 9 DRIFT / 10 MATCH + 行级漂移；要求按他卡惯例记 erratum、封件不回改 | 19 pins = **10 MATCH / 9 DRIFT**（与 r1 同分割），不回写 pin 表 | ✅ **已处置**：①按 r2 归档 `evidence\rgm2\pins_r2.json` = `sha_match_now=10 / sha_drift_now=9`，`drift_ids` = register×5 + closure decision×3 + `iso_cli_before`×1 ⇒ **与 r1 分割完全相同**；②**复审 22:38 现盘读数 = 8 MATCH / 11 DRIFT**（多出 `owner_decisions_sec22/sec23`，见 §9 第三条）；③**50 条钉行逐字全部仍在现盘**；④`binding.json` 字节未改（`caca43e8…` == r1 DELIVERABLES 行）。**⇒ 读数必须标时点** |
| **F-04** | P3：C1b 产物 mtime 00:04:17 晚于 `oracle.sha256` 23:50:41，却列在「冻结之前」表 | 时序更正追加：登记为冻结后产物，「冻结前已跑」不作断言 | ✅ **已处置**：mtime 复测 `oracle.md 2026-09-23 23:50:38`、`oracle.sha256 23:50:41`、`evidence\mech\mech_cases.json 23:40:19`（冻结前）、`evidence\mech\grep_120_and_emitter.txt 2026-09-24 00:04:17`（冻结后）⇒ 与卡面一致；`commands.md` R2-步骤6 F-04 行原文在盘 |
| **F-05** | P3：handoff §1 表称 `report_SA-DEFECT.md:165` 被更正，但 pin MATCH、字节未动 | 措辞更正为「以本卡 oracle §5 / decision §1 承载更正；封存件字节不动」 | ✅ **已处置**：复算 `AUDIT-GOAL\a20260923-01\evidence\report_SA-DEFECT.md` = **26047 B / `374a57700884a6ee427286a2e27c544746dfe004dd260739dcabdceba74d37df`** == pin；**L165 原文仍是**「`\| F12（断管归一化） \| 断言在返回后开火 \| REG:592 \| …`」；`handoff.md` `## review_round_2` F-05 行已写入更正措辞 |
| **F-06** | P3：`decision.md §5` 家族 grep 行号清单漏 `test_publication_pipeline.py:315`；**补列 315 或注明已排除注释行** | 「已补列：`decision.md §5` 补 `test_publication_pipeline.py:315`；87/332/360 不变；文件集合仍恰 8」 | ⚠️ **处置位置记录不实 ⇒ N-02（P3）**：①实体事实复测**为真**（同正则生产 `tests\` 恰 **8 文件 / 15 行**，`test_publication_pipeline.py` = **87, 315, 332, 360**）；②但 `decision.md` §5（**L71**）逐字仍只列 `87,332,360`，全文唯一 `315` 在 **L124（§7.5 摘要）**；③§5 位于 append-only r1 前缀内（前 11542 B = `fad182c0…` 已复算）**结构上不可能改**；r1 的「补列**或**注明」实际只在 §7.5/commands/handoff 三处落地 ⇒ 见 §9 第二条 |
| **F-07** | P3：首轮 GREEN probe 被末轮同名覆盖未单独留存；要求 commands 补一行同等披露 | 披露 r1 首轮 RED probe 被同名覆盖 + r2 新规则「覆盖前先改名归档」 | ✅ **已处置**：mtime 复测 `evidence\rgm\green\probe_run1_after_fix.json = 00:14:27` < `evidence\rgm\red\probe.json = 00:32:41` ⇒ 覆盖事实成立；`commands.md` R2-步骤6 F-07 行原文在盘；r2 归档实物 `evidence\rgm2\failed_try1_expect_table\probe.json`（5453 B）与 `evidence\rgm2\prefix_selfcheck_r2_failed1.json`（7787 B）均为改名独立路径，commands 明写「**不作证据**」 |
| **F-08** | P3：冻结判据只有 M-1/M-2，缺「只中和不 catch」臂；要求保持冻结、在 decision 增补说明 catch 半非空转证据来自产品测试 | 补「只中和不 catch」臂；冻结 M-1/M-2 与 `oracle §4` 一字未改 | ✅ **已处置**：补臂已跑（§3 变异③：4 臂 help/h/validate/version 全 **0**、无产品文本、无 `Exception ignored`、**4F/5P 打红**）；`oracle.md` sha 仍 `7fecfaea…` ⇒ §4 一字未改；`decision.md` §4 属 r1 前缀（`fad182c0…` 前缀复算通过）⇒ 一字未改；§7.3 关闭语句在盘 |

**r1 七条 P3：7/7 处置；其中 F-02/F-03/F-04/F-05/F-07/F-08 经 r2 独立复算为真，F-06 的处置位置记录不实（→ N-02）。**

---

## 9. 必须随卡携带的三条（逐字，不得弱化）

### 9.1 N-01（P2）—— `changes.diff` 是 0-context，plain `git apply --check` 不通过

> r2 把 `changes.diff` 改成 `difflib n=0`（0-context）后，**plain `git apply --check` = rc=1**（`error: patch failed: scripts/revenue_forecast.py:127` / `patch does not apply`；隔离副本与本仓各跑一次相同；`core.autocrlf=false/true` 结果相同）；须 **`git apply --check --unidiff-zero`** 才 rc=0（实打后 LF 归一产物恰为 `405fec6d…`/`083b92a5…`）。**对照：r1 旧 diff `f0a01489…`（n=3）plain check rc=0。** 卡面 R2-C10b 只披露了 n=0 的「hunk 分离」动机，**未披露对 plain git apply 的影响**；卡面自身的 `verify_diff` 是字节重建、**从未用 git**。⇒ **若合并批本就用 `--unidiff-zero` 或非 git 工具，可降 P3** —— 此处置权归父/合并批，**你不裁**。

（位置：`reviewer_report_r2.md:195`，字节区 [22050,22996] / 947 B / `046e8eb9d3874d2d9e4421046b2c94f8b217d39057cecc111220dfd1c561296c`；本 pass **不裁其降级**。）

### 9.2 N-02（P3）—— F-06 处置位置记录不实

> F-06 处置**位置记录不实** —— `handoff.md:85`、`handoff.json` findings[F-06]、`commands.md` R2-步骤6 三处都写「`decision.md` **§5** 补列 `test_publication_pipeline.py:315`」，但 §5（L71）逐字仍只列 `87,332,360`，全文唯一 `315` 在 **L124（§7.5 摘要）**；§5 在 append-only r1 前缀内（前 11542 B = `fad182c0…` 已复算）**结构上不可能改**。**实体事实复测为真**：生产 `tests/` 同正则**恰 8 文件 / 15 行**，`test_publication_pipeline.py` = 87,315,332,360。

（位置：`reviewer_report_r2.md:196`，字节区 [22998,23872] / 875 B / `d967832dcc5e2d76ae5f20c6a0fe393ac7a373e26af5c34b7f9e993d8bd698d9`。）

### 9.3 pin 读数必须标时点

> **pin 读数必须标时点**：r2 的 10 MATCH/9 DRIFT 是 **22:03 前后**读数（`pins_r2.json` 存档，drift_ids 与 r1 **完全同分割**）；复审 **22:38** 现盘读数 = **8 MATCH / 11 DRIFT**，多出 2 条是 `OWNER_DECISIONS.md`（22:15:34 外部追加）与登记册（22:13:25 再追加），**均晚于 r2 复算**；**50 条钉行逐字全部仍在现盘**（register delta=+3、closure delta=0、OWNER_DECISIONS delta=0）。

（位置：`reviewer_report_r2.md:197`（§12 第三行，标注「信息，**非本卡缺陷**」）；**不需本卡处置**，但任何后续引用 pin 数字**必须标时点**。）

---

## 10. r2 发现表（转录）

| 编号 | 级别 | 位置 | 建议处置 | 本 pass 处置 |
|---|---|---|---|---|
| **N-01** | **P2** | `changes.diff`（r2 重生成，`difflib n=0`）；`commands.md` R2-C10b；`handoff.json.checks.changes_diff` | 追加一行「本 diff 为 0-context（U0），`git apply` 需 `--unidiff-zero`」，或由合并批确认应用方式；**若合并批本就使用 `--unidiff-zero`/非 git 工具，可降为 P3** | **随卡携带，不裁**（降级处置权归父/合并批） |
| **N-02** | **P3** | `handoff.md` L85、`handoff.json.findings[F-06].disposition`、`commands.md` R2-步骤6 F-06 行、`decision.md` L124 | 把三处措辞改为「在 §7.5/本表补列」或「§5 位于 r1 冻结前缀不可改，改于 §7.5 补列」，与 F-05 的诚实口径一致 | **随卡携带**（`handoff.md` / `commands.md` / `decision.md` 为既有 carrier，**本 pass 只读不改**；措辞修正归父） |
| —（信息，非本卡缺陷） | — | `binding.json` 19 pins 读数时点 | 任何后续复审引用 pin 数字**必须标时点** | 已随卡携带（§9.3） |

**级别统计：P1 = 0，P2 = 1（N-01），P3 = 1（N-02）。**

---

## 11. unverified / 本复审未验证清单（r2 报告 §13，9 条逐条照录）

1. **家族 8 文件 64 passed/48 subtests 本轮（r2）与本复审均未重跑**：复审独立复现根因——`tempfile.mkdtemp()` 建得进、**向其写文件即 `PermissionError: [Errno 13]`**，纯 python 进程同样复现；`tests/conftest.py` 的 `_isolate_publication_registry` 即 `tmp_path_factory.mktemp`。⇒ 只能字节级核验 r1 的 5 件 `family_*`（`before/after/final_raw.txt`、`compare.txt`、`compare_v1testfile.txt`，**全部在 r1 `MANIFEST` 57/57 内命中**）+ 静态不相交（grep 8 个家族文件，`--help`/`-h` **0 命中**）。**未证的是「本次会话重跑得到 64/48」。**
2. **单模块覆盖门 `revenue_forecast.py ≥60%` 未复测**（r1 的 73% 依赖直调 `main()` 的进程内覆盖，本会话不可运行）。只独立验证了 F-02 的 **rc 语义**（0/2/0），**未重跑 r1 的 73% 子集，也未采用 r2 的 38% 子集作门结论**（卡面已明示「不可比、不作门结论」，其 `coverage combine` rc=1 失败也如实留档）。
3. **Linux/macOS 断管码值未测**（卡面已披露，复审照录）。
4. **`--help`/`-h` 之外的 `SystemExit`-in-`main` 组合未穷举**（如 `parser.exit(status)` 非 0/2 码）；映射规则 `int→原值 / None→0 / 其余→2` 读了源码但只有 argparse 实际产生的 0/2 被实测。
5. **stderr 汇本身断管未构造**（oracle §6 明列非目标）。
6. **真仓库内的 `git apply` 实施**未执行（只执行 `--check`，`--unidiff-zero` 的实际 apply 在隔离副本执行）。
7. **r2 归档读数（`pins_r2.json` 的 10/9）无法在复审时点原样复现**——只能以该存档 + mtimes 认定其为当时真值。
8. 复审**未**复刻 `production_zero_write_*.txt` 的树 sha 算法（卡面未给清单）；以 `git diff HEAD --name-only` 非 `.planning`=0 + 生产 CLI sha==pin + 新测试不在生产树替代。
9. 复审**未使用 `git status`**（卡面纪律禁用），因此未复核卡面提到的「2 条既有未跟踪件」。

---

## 12. 边界声明

**（a）复审者自己的边界（r2 报告 §11/§14，转录）**

- `git -c core.quotepath=false diff HEAD --name-only` → **TOTAL=3826，非 `.planning` = 0** ✅（**未使用 `git status`**）。
- 生产 `scripts/revenue_forecast.py` = **`2a2dfede7941b0fac972d802d25eb71f798c1ebdb83226bbf8528481b9669e36`**（5333 B）== pin `prod_cli_before` ✅；生产树 `tests/test_stdout_flush_exit_domain.py` **不存在** ✅。
- 全部测试/探针只在 `%TEMP%\wc4r2rev\`；`evidence\rgm\**`、`evidence\rgm2\**` 与 attempt 既有字节**零写入**（由 57/57 + 24/24 复算反证）。
- **没有**修改两份复审报告、**没有**覆盖 r1 的 `reviewer_report.md`/`reviewer_report.sha256`、**没有**创建或修改 `handoff.json`、**没有**改任何 status、**没有**替实现者落定或代签、**没有**执行任何 git 写命令、**没有**联网、**没有**运行卡面会写 `evidence\` 的 harness、**没有**在仓库内创建临时文件、**没有**把任何未验证项写成已验证。

**（b）本 carrier-landing pass 自身的边界**

- **写入面 = 本 attempt 目录，恰 3 个文件**：`review.md`（新建）、`handoff.json`（仅 status 面转录）、`evidence/WC-4-RC120/qualification.json`（新建，目录新建）。
- **未写**五份计划文件（父折入）；**未改 `.planning` 之外任何文件**；**无 git 写操作**；**本仓未执行 `git status`**；**未联网**；**未跑测试**。
- **两轮复审报告都只读、都保留**：`reviewer_report.md` 26073 B / `99416605…`（`changes_required`）、`reviewer_report_r2.md` 28878 B / `ddbd536c…`（`ACCEPT`）、`reviewer_report_r2.sha256` 88 B —— 本 pass 写入字节 = **0**。
- **既有 carrier 只读**：`oracle.md`（`7fecfaea…` 四处同值）、`changes.diff`（10114 B / `d1a79376c518eab3…`）、`decision.md`、`handoff.md`、`commands.md`、`DELIVERABLES.sha256`、`evidence/MANIFEST.sha256`、`evidence/**`、r1 `evidence/rgm/**` —— 除 `handoff.json` 状态转录与新建文件外 **0 字节改动**。
- **不自签**：`implementer_signed = false`、`verdict_is_transcribed_not_authored = true`。
- **不裁**：不裁 N-01 的降级；不晋升；不改两份复审报告；不碰其他卡。

---

## 13. 落定清单

| 文件 | 状态 |
|---|---|
| `review.md` | **本文件，新建**（创建前本 attempt 无 `review.md`） |
| `handoff.json` | `status: review_pending → accepted_scoped`；新增 `status_before` / `status_authority`（carrier = `reviewer_report_r2.md` + 行号/字节区/sha 全值 + `verdict_line_text`）/ `status_history`（**两条：r1 `changes_required` + r2 `ACCEPT`**）/ `reviewer_status` / `carried_findings`（N-01 P2 + N-02 P3 + r1 F-02…F-08 逐条）/ `unverified`（r2 §13 的 9 条逐条）/ `verdict_is_transcribed_not_authored = true`；前像 sha `19a2969e…`（6575 B）已记，写后重解析 |
| `evidence/WC-4-RC120/qualification.json` | **新建**：`formula = not_applicable_with_reason`、`disclosure_adaptation = unmapped`、`accuracy = unproven`、`granted_scope`（rc 终态处理域的**证据与判据**，**不含晋升**）、`not_granted`（生产闭环、晋升、家族 64/48、单模块覆盖门 ≥60%、Linux/macOS 断管码值）、`verdict_is_transcribed_not_authored = true`、`status_authority` 镜像、`carried_findings` 镜像 |

**当前状态**：`accepted_scoped`（scoped：N-01 P2 随卡移交父/合并批、N-02 P3 随卡移交；**非 clean**）；**不晋升**、**不自签**、**不裁 N-01 降级**。
