# I10A-F2-FIX / a20260923-01 — review.md（carrier-landing 簿记转录）

> **创建声明**：本文件**由 carrier-landing 簿记 pass 创建**；**创建前本 attempt 无 `review.md`**
> （attempt 根当时只有 12 个目录 `after/ before/ command_runs/ evidence/ harness/ iso/ iso_ctl/ oracle/ recovery/ scratch/ scripts/ _scratch_i10b/ _scratch_import/`
> 与 6 个文件 `changes.diff`、`frozen_regression_rerun.json`、`handoff.json`、`oracle.md`、`reviewer_report.md`、`reviewer_report.sha256`）。
>
> **本文件只做簿记转录，不产生新裁决、不自签。** 裁决唯一权威 = `reviewer_report.md`（独立复审工位亲笔，其 §0 明写「只写本报告，不写卡状态、不替实现者落定、不处置 D-1」）；
> 本文件、`handoff.json` 的 status 面、`evidence/I10A-F2-FIX/qualification.json` 只转录该裁决，
> **`verdict_is_transcribed_not_authored = true`**、**`implementer_signed = false`**、**不代签**。

---

## 0. 裁决转录（唯一权威 = `reviewer_report.md`）

```text
VERDICT: ACCEPT
```

**P1 = 0 / P2 = 0 / P3 = 4**，另有 **7 项 unverified** 如实随卡（report §10）。P1=0 ⇒ 判 ACCEPT 而非 changes_required；**scoped，不 clean**。

| pin | value |
|---|---|
| 载体（carrier，唯一裁决来源） | `reviewer_report.md`（本 attempt 根，只读） |
| 字节 | **27699 B** |
| sha256（本 pass 只读重算，与派发钉一致） | `667694e9e2c566df3b7a33f7e9e49692c639264083c4be05ed63552f8b47353f` |
| sidecar | `reviewer_report.sha256` = **85 B**（其自身 sha256 `c92acefd22ac7c987290ddde7794715e9c7c96fb214787c5b42fd9e33e17f621`），内容 `667694e9e2c566df3b7a33f7e9e49692c639264083c4be05ed63552f8b47353f  reviewer_report.md\n` —— 与只读重算 **MATCH** |
| 全文行数 / 编码 | 314 行；UTF-8，LF-only（CR=0），末行带 LF |
| **裁决行** | **第 9 行**（1-based，位于 ``` 围栏内）；0-based 字节区 **[415, 430]**（含行尾 LF，长度 16）；行 sha256 `ffd796ea6572fdaf4dce6d9984e6e9294cf8c0c564ce345d73132bf29aa1b3b4`；原文 `VERDICT: ACCEPT` |
| 分节字节区（0-based，含行内 LF、不含该节末行 LF） | 见下表 |

| 节 | 行号 | start | end_inclusive | length | sha256 |
|---|---|---|---|---|---|
| §0 方法与边界 | 16–22 | 622 | 1469 | 848 | `4f33be478d9d8d8a9cb03c7af1b1660181531be8cba3e68ab05eb28a5d62889b` |
| §1 逐项核验表 | 24–34 | 1472 | 2377 | 906 | `383226d290fa5ddce68ee41b4ed57d3a861842afa5519ecf91adeb74d97a6a07` |
| §2 三臂 | 37–66 | 2384 | 5207 | 2824 | `b98f733a5e03b79b341eb67970d3857f5e332dfee0323614b76c00ebae1c2cdb` |
| §3 家族 | 69–114 | 5214 | 8873 | 3660 | `c3e5320f99e4f5d461a551f7427ccdef46ba097966d82b156c489b7b3868c8f4` |
| §4 changes.diff | 117–129 | 8880 | 10490 | 1611 | `c1242d59dc35d875a92483d815b1f20584916bbb88da9c2f098103ffe712df8c` |
| §5 D-5 夹具 | 132–156 | 10497 | 12880 | 2384 | `1260db761f111ae5a7138efc032f3a17bdad1b3beb254625f5aab0f89fca83a1` |
| §6 D-1 一致性 | 159–181 | 12887 | 15411 | 2525 | `571d7672b67242d48ad00e0bb9eab4d102bb35ab5c1f10044e7f05bb65a9d3cf` |
| §7 B-1 | 184–196 | 15418 | 16858 | 1441 | `bf0d38dfce75ac657e2e79c4fc573a11d5b73b63327bcd16f54ec722cf8bce89` |
| §8 自曝三处 + 瑕疵两处 | 199–227 | 16865 | 20400 | 3536 | `5f4ced407ca0a1a59f491bd70897fa113f3da43c32897716db04c99e82fbb7ae` |
| §9 发现分级（P3 四条） | 230–250 | 20407 | 22582 | 2176 | `dcf5e58aa9d2f460dcca176edd3c1e2b4d1dc7e57d268d63d10b38d5f18fbcc4` |
| §10 Unverified（7 项） | 253–262 | 22589 | 23885 | 1297 | `7995e3df4ab06b9a5e4035f6f22a04c5d6347e8e66c5b64960ffd67b92a6a995` |
| §11 边界 + 副作用自报 | 265–281 | 23892 | 25945 | 2054 | `0edc52a86751a2834a69cf38de4f618ced7e99ace6ee0c492361689344323be3` |
| §12 rc/sha 速查 | 284–314 | 25952 | 27697 | 1746 | `6bc87f92f26426074664bce664218092e9f7205a14916d90e8b0433f7ed0062c` |

**实现者未自签**：`handoff.json` 前像 = 51834 B / `00ae453b05a78435127dc0d39ee15f084b707a47b62d65812381e8a04b70d404`，`status="review_pending"`、`implementer_signed=false`、`reviewer_signed=false` —— 在本 pass 任何写入之前只读量取。**本 pass 不签任何字。**

---

## 1. 【三臂实测，逐字抄】复审独立自跑结果（report §2）

复审把 `iso_ctl/rf/scripts`（原像）与 `iso/rf/scripts`（修复后）分别拷进 `%TEMP%`，用**原样拷贝的 I-10-A harness**（`harness/run_mapping_probe.py`，未改一行）+ 同一 `oracle_expected.json` 自跑 4 案 × 5 臂，**20/20 次 `process_rc == harness raw_rc`，无一例外**。

| 臂 | 树 | normal | red_conv | mut_swap_ids | mut_swap | **mut_omit_optional** |
|---|---|---|---|---|---|---|
| **RED** | `iso_ctl/rf`（原像，**复审自拷原像树自跑**） | 0,0,0,0 | 2,2,2,2 | 2,2,2,2 | 3,3,3,3 | **3,3,3,2** |
| **GREEN** | `iso/rf`（修复后） | 0,0,0,0 | 2,2,2,2 | 2,2,2,2 | 3,3,3,3 | **2,2,2,2** |
| **MUT** | 修复后 + **复审亲手**打上变异 | — | — | — | — | **3,3,3,2** |
| **RESTORED** | 变异撤回后 | 0,0,0,0 | 2,2,2,2 | 2,2,2,2 | 3,3,3,3 | **2,2,2,2** |

案序固定为 ZJ-MIN-M09 / ZJ-SMT-M09 / XM-PHONE-M03 / XM-EV-M03。

**变异与归位（复审自己的 sha）**

- 打变异前 `iso/rf/scripts/forecast/calc.py` = **15969 B / `9eecf260bfb22f1a5b3114a956cdf633328d620e1957a58de6806ab0214dcca9`**（与实现者自述逐字节相同）。
- 打变异后 = **`a80776421360bec31c0839ac4a60e961b197edc93e5c1d444bdff358c85a3e07`**（15875 B）—— 与 `evidence/mut_arm.json` 的 `sha_after` **完全相同**（变异打在同一处、同一字节）。
- 撤回后 = `9eecf260bfb22f1a…14dcca9`，与打变异前**逐字节相同**（sha256 比对，非"看起来一样"）；CRLF=0、LF=390（真·LF，无漂移残留）。

**`field_class_check`：true → false → true（变异真打红）**

- 变异态：`all_pass=false`，**FC1/FC2 变 `outcome=ok, pass=false`**（RAISE 类被 0 填吃掉），FC3/FC4/FC5 仍 true ⇒ **变异真的把判定打红了，不是空转**；进程 rc=1。
- 归位后：`all_pass=true`，FC1/FC2 恢复 `ForecastInputError` + 冻结报文 `missing driver for unit_sales|resource: other_revenue has no explicit default`，FC4 显式 0.0 仍得 `[50.0, 55.0]` ⇒ 进程 rc=0。

**字节级重建（不自跑的部分）**：对盘上 `evidence/probe_before|probe_after|probe_after2|probe_mut|probe_mut2|probe_mutrestored|probe_mutrestored2` 共 7 组 probe_result 逐个解析 `raw_rc`，得到与上表完全一致的 3,3,3,2 / 2,2,2,2 / 3,3,3,2 / 2,2,2,2。

实现者"RED 未重跑、从冻结 payload 抽取"的披露属实（`evidence/rc_red.json` note 与 `run_log` `CMD-I10A2F2-RED-EXTRACT`）——但复审**没有依赖该披露**：它在自己的原像副本上真跑了 RED，结果相同。

---

## 2. 【家族面，逐字抄】（report §3）

**复审用 ElementTree 重算 junit（非读 handoff）**：

- `family_before_junit.xml` = **1169 passed / 59 failed / 4 error / 11 skipped**（合计 1243）
- `family_after_junit.xml` = **1164 passed / 64 failed / 4 error / 11 skipped**（合计 1243）
- 逐 id 分类：**`regressed=5`、`fixed=0`、`other=0`、`added=0`、`removed=0`、`same=1238`** —— 与 `family_diff.json` 逐项一致
- `family_ctl_subset_junit.xml` = 5 tests / 5 failures；`regressed` = 5 条，`regressed_in_control` = **同一 5 条**，`passed_in_control=[]`、`ids_not_run_in_control=[]` ⇒ 集合相等，对照臂恰好覆盖 regressed 全集

**复审在字节级原像树独立重跑 5 个 id = 5/5 全失败（606.91s，rc=1）**：

```
FAILED tests/test_fc1004_platform.py::test_install_sync_gate_detects_drift
FAILED tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity[install_root0]
FAILED tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity[install_root1]
FAILED tests/test_zr907_drift_patrol.py::test_c3_cli_reports_all_checks
FAILED tests/test_zr907_drift_patrol.py::test_c3_patrol_core_gates_green
6 failed, 2 passed in 606.91s   (rc=1)
```

其 junit 中 traceback 与 subprocess 实参**同指它自己的 `ctltree`**（无实现者那份的路径矛盾）；同法在 `isotree`（AFTER 树）跑 fc1004 + zr907×2 = **3/3 失败**。

**同一短临时根 `dsh-5SPejJ`（`iso_ctl` 相关三份 junit 同根）**：junit 内 `Temp\dsh-5SPejJ\p\pytest-of-…` —— `family_after_junit` = `dsh-5SPejJ`、`family_ctl_subset_junit` = `dsh-5SPejJ`、`envfix_check_junit` = `dsh-5SPejJ`；`family_before_junit` = **无**（不同 session、默认临时根，与 handoff 自述一致）。

同 session 佐证：ctl junit `timestamp=2026-09-24T22:02:11+01:00`、`family_diff_control.generated_at_local=22:12:32`；跑在 iso_ctl 的实参 = `…\a20260923-01\iso_ctl\rf\tools\sync_installations.py`（4 处，但见 P3-1）。

树身份核验：`iso_ctl/rf/{scripts,tests,tools}` vs 生产 = **0 差异**（43/131/32 文件）；`iso/rf` vs 生产 = **恰 8 个文件差异**（= changes.diff 的 8 个）。

---

## 3. 【`changes.diff`，逐字抄】（report §4）

- **14366 B**、**LF only（CRLF=0）**、**无 BOM**、sha256 = `bcd44c249da249b283cc06088e5da8e3aa8d092ecae28cae506be631503f6db8`
- **8 对 `---/+++`**（`--- a/` 8 条、`+++ b/` 8 条），两侧集合相同：
  `scripts/forecast/calc.py`、`scripts/forecast/segments.py`、`tests/golden_behavior_hashes.json`、`tests/test_golden_behavior_lock.py`、`tests/test_industry_end_to_end.py`、`tests/test_lifecycle_forecasts.py`、`tests/test_models.py`、`tests/test_zr709_zijin_journey.py`
- **产品面恰 2 个**：`calc.py 14978 → 15969`（`bc4f33d9…` → `9eecf260…`）、`segments.py 27697 → 27966`（`95555509…` → `cd6edee6…`）—— 与复审实测两棵树字节数/sha 完全一致
- **`git apply --check`（对生产树）rc=0**，8 个 patch 全部 "Checking patch …" 无报错
- **最强一步**：复审**用自己写的 unified-diff 应用器，把「生产树原文 + changes.diff」应用后与 `iso/rf` 对应文件逐字节比对 → 8/8 MATCH（ALL_MATCH=True）** ⇒ **`unexpected=0 / missing=0` 是可证的，不是自述**
- 改动只在 iso、生产树零写：`git diff HEAD --name-only`（`core.quotepath=false`）两次 **total=3826、非 `.planning` = 0**；`iso_ctl/…` vs 生产 0 差异；`iso/rf` vs 生产恰 8 文件
- handoff **147 条 deliverable sha/bytes 复算 0 mismatch**（开工、收尾各一次）

---

## 4. 【夹具未弱化（D-5），逐字抄】（report §5）

做法：6 个夹具文件的**生产前像** vs **iso 后像**全文比对，抽取所有断言行（`assert*` / `assertRaises*` / `pytest.raises` / `self.assert*` / `assert re.`）做**多重集比对**，并单独 grep `skip|xfail`。

| 文件 | 断言行 before | after | 删/改 | 增/改 | skip/xfail 新增 |
|---|---|---|---|---|---|
| tests/golden_behavior_hashes.json | 0 | 0 | — | — | 0 |
| tests/test_golden_behavior_lock.py | 2 | 2 | **0** | **0** | 0 |
| tests/test_industry_end_to_end.py | 15 | 15 | **0** | **0** | 0 |
| tests/test_lifecycle_forecasts.py | 19 | 19 | **0** | **0** | 0 |
| tests/test_models.py | 10 | 10 | **0** | **0** | 0 |
| tests/test_zr709_zijin_journey.py | 41 | 41 | **0** | **0** | 0 |

- **`test_retail_franchise_optional_pair_is_enforced`**：前后两个函数体整段打印比对，断言行
  `with self.assertRaisesRegex(ForecastInputError, "requires franchise_system_sales and recognized_fee_rate together"): run_forecast(data)`
  **逐字节未变**；新增的只有一行
  `data["segments"][0]["scenarios"]["low"]["driver_parameter_ids"].pop("recognized_fee_rate", None)`（前置条件显式化）。
  关键点：该断言带**具体报文正则**，若现在是被 F-I10A-2 的 `missing driver …` 异常触发，`assertRaisesRegex` 会不匹配而失败；
  **`fixture_fix_check_junit` = 114 tests / 0 failures / 0 errors** ⇒ **仍然是那条 pair 规则在报文**，测试没有被绕开。
- `test_lifecycle_forecasts._document` 改动只有 ① import 行多引入 `MODEL_SPECS`；② 新增一段给 optional 驱动显式补 0.0 的循环 —— **无任何断言被删/被改**。
- 旁证：`family_diff_preedit.json` 记录 D-5 编辑**之前**的 60 个翻转，编辑后收敛为 5；`golden_after_update_junit.xml` = 1 test / 0 failure；`test_zr709` 41 条断言 0 删 0 增。
- **判定（复审）：夹具改动没有弱化任何测试**；实现者"断言一字未改"逐字核实为真。

---

## 5. 【D-1 一致性 —— 父处置记录，逐字转录】（report §6；只核不处置）

**实现者披露（5 条记录、`20:02:50.848–20:02:51.036Z` 190 ms 内、65→60 行、50229→46369 B、`18310fae…` → `bc3256bb…`、`tracked_file_written=false`、ReadOnly `attempted=true, succeeded=false` 自判 BLOCKED、未清保护位）与父 `REMEDIATION_RECORD` 完全一致。**

父方 `REMEDIATION_RECORD.md` 原文（逐字）：

```text
# D-1 remediation record (owner-authorized truncation)

- authorized_by: OWNER answer 2026-09-24, option (a)「截断回 60 行」
- executed_at_utc: 2026-09-24T21:41:35.194073Z
- PRE : 50229 B / 65 lines / sha256 `18310faea83bad23e68f6713b2c5cce2ad6a3d89f6d8a6b8a02419659335ad55`
- POST: 46369 B / 60 lines / sha256 `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`
- readonly_before=True  readonly_after=False
```

逐项对照（复审 §6.1 六行全 ✅）：触发动作、时间窗、前像（65 行 / 50229 B / `18310fae…`）、目标后像（60 行 / 46369 B / `bc3256bb…`）、被跟踪文件（`tracked_file_written=false`；`git ls-files --error-unmatch rc=1` 未跟踪、`git check-ignore -v rc=0 → .gitignore:16 artifacts/`）、ReadOnly（实现者未清判 BLOCKED vs 父复原时 `readonly_before=True → readonly_after=False`，无矛盾）、时序（工位取证 21:55:33 本地 → 交卡 22:19:49 → owner 裁 (a) → 父执行 `executed_at_utc=2026-09-24T21:41:35Z`）。

**现盘复测（复审只读）**：

- `artifacts/registry/publications.jsonl` = **60 行 / 46369 B / `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`**、属性 **Archive（ReadOnly 已清）** ⇒ 与父方 POST 完全一致。
- 事故目录在盘：`execution_runs/_isolation_incidents/20260924-i10a-f2-baseline-wrote-production-registry/` 含 `INCIDENT.md`（5966 B，**`status: **RESOLVED**`**，原 `OPEN` 行已划除；`detected_by: 修卡工位自报`、`verified_by: 父独立取证`）、`REMEDIATION_RECORD.md`（992 B）、`publications.jsonl.pre_truncation_20260924`（**50229 B / 65 行 / `18310faea83bad23e68f6713b2c5cce2ad6a3d89f6d8a6b8a02419659335ad55`**，与前像一致）。

**结论：实现者的 D-1 披露与父方复原记录在时间、行数、字节、sha、ReadOnly 状态上完全一致，无矛盾。复审未重做截断、未动该文件、未清属性、未改 handoff。本 pass 同样不碰 `publications.jsonl`（不重做截断、不清属性），`handoff.d1_state` 记 `remediated_by_parent_see_isolation_incident`。**

---

## 6. 【B-1 成立，逐字抄】（report §7）

| 支撑点 | 复审独立复测 |
|---|---|
| 生产侧只读 hash check 就是红的 | **自跑 rc=1**，`DIFF …\.agents\skills: 198 files`、`DIFF …\.codex\skills: 198 files`（与盘上 `evidence/production_install_check.txt` 一致） |
| 原像树同样过不了这 5 个 | **在字节级原像副本上重跑，5/5 failed，606.91s** |
| 5 个 id 就是 regressed 全集 | 重算 junit：集合完全相等，`passed_in_control=[]`、`ids_not_run_in_control=[]` |
| 未新增 skip/xfail 掩盖 | 6 个夹具文件 grep **0 新增** |

⇒ **`environment=5 / fix_attributable=0` 成立**：这 5 个安装/平台门在本 session 的失败**与本卡修复无关**。

**残留（不推翻 B-1，但要说清）**：`test_fc1004_platform::test_install_sync_gate_detects_drift` 用的是 `--destination tmp_path/installed` 一次性目标、`returncode=1` 且 **stdout 为空**（= 子进程崩了，而非 diff 报告），其**根因未诊断**；它在原像树上同样失败，因此只到"非本卡回归"这一层，**未到"已知为何必失败"**。

---

## 7. 【I-1 / D-2 / D-3，逐字抄】（report §2、§8）

**I-1（字节不变）**：`model_registry.py` = **`62f864b9ab3f144e…`（30116 B）**、`model_extensions.py` = **`9939480b717d5a49…`（14475 B）**，**生产树与 iso 树两边逐字节相同**（复审自算 sha）。

**D-2 shim 核验（只改权限，不改断言/夹具/SUT）**：

- `scripts/i10a_dir_mode_shim.py` = **1584 B / `68a3a29677d28e28…`**（与 handoff 一致），全文只做一件事：`os.mkdir = _mkdir`，**把 mode 参数丢掉、按默认 `0o777` 创建**；**不 import 产品、不碰 conftest/夹具/断言、不筛选用例**。
- `tests` 树 grep `0o700|0o600|chmod|st_mode`：**唯一命中是 `test_publication_registry.py:70 path.chmod(S_IWRITE|S_IREAD)`，与 mkdir mode 无关** ⇒ 没有任何断言会因 shim 被掩盖。
- 限制：AFTER 与 CONTROL 都带 shim、**BEFORE 不带**（跨 session），handoff 已如实注明。

**D-3 披露完整**：

- `test_zr804_platform_shape._sync_installations()` 执行 `tools/sync_installations.py --apply`（**无 `--destination`** ⇒ 走 `DEFAULT_DESTINATIONS` = **`Path.home()/.{agents,claude,codex}/skills`**），即 `.planning` 之外 —— 与复审读到的源码一致。
- 证据在盘：`evidence/family_after_stdout.txt` 内 `sync_installations` 7 处、`--apply` 3 处、`TimeoutExpired` 6 处。
- **基线亦然**：`family_before_junit.xml` 里 zr804 两条 `installed_copy…` 为 **passed** ⇒ 它当时**必然**执行过同一条 `--apply`。
- `tools/sync_installations.py` 默认模式（不带 `--apply`）是**只读 hash check**（`main()` 只有 `--apply`/`--print-manifest`/`--import-from` 才会写），复审只用了默认模式。

**另两处过程瑕疵（复审核过，留档）**：① `mut_guard` CRLF 漂移 —— `evidence/mut_arm_superseded_r1.json`（1276 B）标废在盘、时间线自洽、归位实证 15969 B/`9eecf260…` CRLF=0，视为"留档且未用作证据"；② validator verbatim 拷贝 rc=3 —— `run_log.jsonl` 第 9 条完整披露（`validate_adaptation` 按自身位置解析 ATT、我方 attempt 无 `evidence/I-10-A/source_extracts`，63 个 R3 quote-not-found 属误用，改用 I-10-A 原脚本），正确产物 `command_runs/CMD-I10A2F2-VALIDATE-GREEN/validate_result.json`（181 B）= `verdict:"pass", violations:[], raw_rc:0`，但**首次 rc=3 输出已被覆盖** → P3-2 + unverified #5。

---

## 8. 【P3 四条，逐字，不得弱化】（report §9 原文）

> **P3-1 `family_ctl_subset_junit.xml` 内部路径自相矛盾。**
> 同一份文件里，zr804 的 subprocess 实参是 `…\iso_ctl\rf\tools\sync_installations.py`（4 处，JSON 转义 `\\`），而 traceback 的源文件路径是 `..\..\iso\rf\tests\test_zr804_platform_shape.py:161/176`（7 处，**指向 AFTER 树**）——两者由同一模块的 `__file__`/`co_filename` 推出，**不可能同时为真**（`iso/rf` 与 `iso_ctl/rf` 的 `tests/` 是两个内容不同的真实目录，已哈希验证）。
> 同时，**对照臂的 pytest 实际命令行 / cwd / rootdir 没有落在盘上任何地方**（`run_log.jsonl` 只有叙述，`family_ctl_subset_stdout.txt` 无 session 头、无 `rootdir:` 行）。
> 影响：对照臂的"树=iso_ctl"只有 zr804 的实参这一条硬证据，fc1004/zr907 三条的树归属在他们的产物里**是含糊的**。
> 为何不升级：结论已被**我的独立原像树重跑（5/5 failed）**替代证明；且我那份对照 junit 中 traceback 与实参**同指一棵树**，可作正确留痕的样板。

> **P3-2 首次 validator `rc=3` 的输出被覆盖，未留档。** 披露本身在 `run_log`，但原始产物不可复核（见 §8 末）。

> **P3-3 BEFORE 家族跑的命令行/stdout 未留盘。** 只有 `family_before_junit.xml`（+`family_before.json` 纯状态表），"上一 session、默认临时根、无 shim"是 handoff 的**自述**；我只能从 junit 里 `Temp\...` 匹配为空**间接印证**"不是本 session 的短根"。

> **P3-4 `evidence/family_measure_junit.xml`（1169/59/4/11，与 family_before 同计数）未在 handoff 中说明其用途/来源**，仅作为 hash 清单成员列出；不构成矛盾，但读者无法定位它与 `family_before_junit.xml` 的关系。

（观察项，非发现：生产树存在未跟踪根 `.tmp-r41-mutation`（创建于 2026-09-20，**早于本 attempt**）与 `assurance/`（D-4 已披露的调度器产物）；两者均在 handoff `production_readonly_self_check.untracked_non_planning_roots` 中列出，非本卡写入。）

---

## 9. 【Unverified 七项，逐字】（report §10 原文）

1. **新拒绝的 CLI rc=2 端到端路径**未跑通（实现者自曝，probe 直接调 `calculate_model_path`）；我亦未补跑 → **未证实**。
2. **最终 `family_after` / `family_ctl` 两次 pytest 是否真的 `-p i10a_dir_mode_shim`**：盘上无命令行留痕，`plugins:` 行只列 entry-point 插件（不列 `-p` 模块），只能间接推断（若无 shim 会全线 PermissionError，而两次都只有 4 error）→ **未证实**。
3. **`test_fc1004` 在一次性 destination 上 `rc=1`+空 stdout 的根因**未诊断 → 只能说"原像树同样失败=非本卡回归"，不能说"已知为何必失败"。
4. **"5 个安装门在干净环境下会绿"** 未验证（也不在 B-1 要求内）。
5. **validator rc=0 来自 I-10-A 原脚本** 的出处（脚本路径/sha 未记录在 `validate_result.json`）→ 未证实。
6. **D-3 的完整性**：我只核了已披露的 `sync_installations --apply` 机制，**没有穷举 1243 个用例里所有写 `.planning` 之外的路径** → 未穷尽。
7. handoff 记 `git_diff_HEAD_name_only_total=3824`，我两次实测 **3826**；差 2 全在 `.planning` 内，非本卡面，**未追查具体两条**（非 `.planning` 均为 0，此点两版一致）。

（实现侧原有 3 条 unverified 保留在 `handoff.unverified` 中**不删**，与以上 7 条并列，共 10 条。）

---

## 10. 【复审自报的两条副作用，如实携带】

**① 复审对照重跑触发 `sync_installations --apply` 写 `.planning` 之外（report §11「⚠️ 必须自报的一处副作用」）**
复审的独立对照重跑选了整个 `tests/test_zr804_platform_shape.py`，其中 `test_installed_copy_executes_with_canonical_identity` 会执行 `tools/sync_installations.py --apply` → 目标是 **`Path.home()/.agents/skills` 与 `Path.home()/.codex/skills`（`.planning` 之外）**，即 D-3 所披露的同一机制。该调用在 **300 s 超时被杀**，复审**随后用只读 hash check 复测**：两目标仍各为 **`198 files DIFF`**（与跑之前的生产侧读数相同），即**未观察到安装副本状态变化**；`git diff HEAD --name-only` 非 `.planning` 仍 = 0。**这条副作用是复审引入的、非实现者问题，按纪律如实留档**（复跑 5 个 id 本可用 deselect 规避 zr804，复审事先未预见到）。

**② 复审首次重建补丁时临时文件被 GBK 写出（report §11「复审过程中的自身操作瑕疵」）**
首次重建 `changes.diff` 时，复审的临时补丁文件用系统区域编码（GBK）写出，导致 `git apply` 结果被非 UTF-8 字节污染 —— **这是复审自身的工具错误，不是被审产物的问题**。改用显式 `encoding="utf-8"` 后：`git apply --check` rc=0、其自写 unified-diff 应用器 **8/8 逐字节 MATCH**。

---

## 11. 本 pass 的写入面与"没有做的事"

**本 pass（carrier-landing 簿记）写入 = 本 attempt 目录内恰好 3 件：**

1. `review.md`（本文件，新建 —— 创建前本 attempt 无此文件）
2. `handoff.json`（**仅 status 面转录**：`review_pending → accepted_scoped` + `status_before` / `status_authority` / `status_history` / `reviewer_status` / `carried_findings` / `unverified` 追加复审 7 项 / `d1_state` / `verdict_is_transcribed_not_authored`；改前前像 51834 B / `00ae453b05a78435…`，改后重解析）
3. `evidence/I10A-F2-FIX/qualification.json`（新建，目录 `evidence/I10A-F2-FIX/` 一并创建）

**没有做的事**：

- **没有**改 `reviewer_report.md`（27699 B / `667694e9…`）与 `reviewer_report.sha256`（85 B）任何字节；**没有**改 `oracle.md`（14872 B / `6d6cf38463d9d822…`）、`changes.diff`（14366 B / `bcd44c249da249b2…`）、`decision.md`、`evidence/**`（147 件）中任何既有字节（`handoff.json` 状态转录与两份新建文件除外）。
- **没有**写 `REMEDIATION_REGISTER.md` / `progress.md` / `findings.md` / `task_plan.md` / `OWNER_DECISIONS.md`（父折入）；**没有**改 `.planning` 之外任何文件。
- **没有**碰 `publications.jsonl`（D-1 已由父处置：**不重做截断、不清属性**）；**没有**碰其他卡。
- **没有**任何 git 写操作；**本仓禁用 `git status`**；只跑了只读的 `git -c core.quotepath=false diff HEAD --name-only`（非 `.planning` 数 = 0）。
- **没有**联网、**没有**跑任何测试、**没有**晋升、**没有**产生新裁决、**没有**自签（`implementer_signed=false`、`verdict_is_transcribed_not_authored=true`）。
