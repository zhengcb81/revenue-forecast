# I10A-F2-FIX — 独立复审报告（independent reviewer station）

- 卡 / attempt: `I10A-F2-FIX` / `a20260923-01`
- 复审角色: 独立复审工位（与实现者非同一人）；**只写本报告，不写卡状态、不替实现者落定、不处置 D-1**
- 复审时间: 2026-09-24/25（本 session）
- 写入面: 仅本 attempt 内两个新建文件 `reviewer_report.md` + `reviewer_report.sha256`

```
VERDICT: ACCEPT
```

结论依据: 六项必核全部由**我自己的独立复算/重跑**得出；未发现 P1。发现 4 条 P3（证据质量/留痕类），另有若干 unverified 如实列出。

---

## 0. 复审方法与边界（先说"我怎么核的"）

1. **只读生产树**：全程未改 `.planning` 之外任何文件；未改本 attempt 任何既有字节（结束前用实现者自己的 147 条 deliverable sha 逐条复算，0 mismatch）。禁用 `git status`，只用了 `git diff HEAD --name-only`、`git ls-files --error-unmatch`、`git check-ignore -v`、`git apply --check`（纯校验，不写 index/worktree）。未联网。
2. **测试只在 `%TEMP%` 隔离副本内跑**：`%TEMP%\revf2\` 下自建 `harness/`（原样拷贝）+ `iso/rf/scripts`（AFTER 原像）+ `isoctl/rf/scripts`（PRE-IMAGE 原像）+ `ctltree/`、`isotree/`（两棵整树副本）。所有 probe / pytest / fieldclass 输出只写进 `%TEMP%`。
3. **复算脚本**全部落在 `%TEMP%`（`rev_*.py`），未在 attempt 内新增任何脚本。

---

## 1. 逐项核验表

| # | 必核项 | 我的独立实测 | 判定 |
|---|---|---|---|
| 1 | 三臂 raw rc + 变异打红 + restore 逐字节归位 | 自跑复现（见 §2） | **通过** |
| 2 | "5 个家族翻转全环境"主张 | 对照臂设计核验 + **我在字节级原像树上独立重跑 5 个 id 全部失败**（见 §3） | **通过**（证据留痕有 P3-1） |
| 3 | `changes.diff` 14366 B / 8 文件 / unexpected=0 missing=0 | 字节级重建 + `git apply --check` rc=0（见 §4） | **通过** |
| 4 | 夹具改动是否弱化测试（D-5 自曝） | 断言行逐字比对 0 删 0 增（见 §5） | **未弱化** |
| 5 | D-1 披露 vs 父复原记录一致性（只核不处置） | 三处 sha/行数/时间全对齐 + 现盘 60 行（见 §6） | **一致** |
| 6 | B-1 blocked 成立性 | 生产侧 rc=1/198 我自跑复现 + 原像树 5/5 失败（见 §3、§7） | **成立** |

---

## 2. 【第 1 项】三臂 — 我的独立自跑结果

我把 `iso_ctl/rf/scripts`（原像）和 `iso/rf/scripts`（修复后）分别拷进 `%TEMP%`，用**原样拷贝的 I-10-A harness**（`harness/run_mapping_probe.py`，未改一行）+ 同一 `oracle_expected.json` 自跑 4 案 × 5 臂。**20/20 次 `process_rc == harness raw_rc`，无一例外。**

| 臂 | 树 | normal | red_conv | mut_swap_ids | mut_swap | **mut_omit_optional** |
|---|---|---|---|---|---|---|
| **RED** | `iso_ctl/rf`（原像，我自己拷的） | 0,0,0,0 | 2,2,2,2 | 2,2,2,2 | 3,3,3,3 | **3,3,3,2** |
| **GREEN** | `iso/rf`（修复后） | 0,0,0,0 | 2,2,2,2 | 2,2,2,2 | 3,3,3,3 | **2,2,2,2** |
| **MUT** | 修复后 + 我亲手打上变异 | — | — | — | — | **3,3,3,2** |
| **RESTORED** | 变异撤回后 | 0,0,0,0 | 2,2,2,2 | 2,2,2,2 | 3,3,3,3 | **2,2,2,2** |

（案序固定为 ZJ-MIN-M09 / ZJ-SMT-M09 / XM-PHONE-M03 / XM-EV-M03。）

变异与归位（**我自己的 sha**）：

- 打变异前 `iso/rf/scripts/forecast/calc.py` = **15969 B / `9eecf260bfb22f1a5b3114a956cdf633328d620e1957a58de6806ab0214dcca9`**（与实现者自述逐字节相同）。
- 打变异后 = **`a80776421360bec31c0839ac4a60e961b197edc93e5c1d444bdff358c85a3e07`** —— 与 `evidence/mut_arm.json` 的 `sha_after` **完全相同**（说明变异打在同一处、同一字节）。
- 撤回后 = **`9eecf260bfb22f1a…14dcca9`**，与打变异前**逐字节相同**（我用 sha256 比对，非"看起来一样"）。

`field_class_check`（同一份 `scripts/fieldclass_check.py`，拷到我的临时树、只写我的 `evidence/`）：

- 变异态: `all_pass=false`，**FC1/FC2 变 `outcome=ok, pass=false`**（RAISE 类被 0 填吃掉），FC3/FC4/FC5 仍 true → **变异真的把判定打红了，不是空转**；进程 rc=1。
- 归位后: `all_pass=true`，FC1/FC2 恢复 `ForecastInputError` + 冻结报文 `missing driver for unit_sales|resource: other_revenue has no explicit default`，FC4 显式 0.0 仍得 `[50.0, 55.0]` → 进程 rc=0。

**字节级重建（不自跑的部分）**：对盘上 `evidence/probe_before|probe_after|probe_after2|probe_mut|probe_mut2|probe_mutrestored|probe_mutrestored2` 共 7 组 probe_result 逐个解析 `raw_rc`，得到与上表**完全一致**的 3,3,3,2 / 2,2,2,2 / 3,3,3,2 / 2,2,2,2。

**实现者"RED 未重跑、从冻结 payload 抽取"的披露属实**（`evidence/rc_red.json` 的 note 与 `run_log` CMD-I10A-F2-RED-EXTRACT 都这么写）——我**没有**依赖这个披露：我在自己的原像副本上真跑了 RED，结果相同。

I-1（registry/extensions 字节不变）：`model_registry.py` = `62f864b9ab3f144e…`（30116 B）、`model_extensions.py` = `9939480b717d5a49…`（14475 B），**生产树与 iso 树两边逐字节相同**（我自己算的 sha）。

---

## 3. 【第 2 项】"5 个翻转全环境"是否成立

### 3.1 对照臂设计核验

| 维度 | 证据 | 结论 |
|---|---|---|
| 树是否真为原像 | 逐字节比对：`iso_ctl/rf/{scripts,tests,tools}` vs 生产树 = **0 差异**（43/131/32 文件）；`iso/rf` vs 生产 = **恰 8 个文件差异**（= changes.diff 的 8 个） | ✅ 对照树确为原像 |
| 同一短临时根 | junit 内 `Temp\dsh-5SPejJ\p\pytest-of-…`：`family_after_junit` = `dsh-5SPejJ`、`family_ctl_subset_junit` = `dsh-5SPejJ`、`envfix_check_junit` = `dsh-5SPejJ`；`family_before_junit` = **无**（不同 session，默认根，与 handoff 自述一致） | ✅ AFTER 与 CONTROL 同根 |
| 同 session | ctl junit `timestamp=2026-09-24T22:02:11+01:00`、`family_diff_control.generated_at_local=22:12:32`，均落在本 attempt 时间窗内 | ✅ |
| 跑在 iso_ctl | ctl junit 中 zr804 的 subprocess 实参 = `…\a20260923-01\iso_ctl\rf\tools\sync_installations.py`（4 处） | ✅（但见 P3-1 的路径矛盾） |
| 同 shim | 无直接留痕（见 §8 unverified）；间接：AFTER/CTL 仅 4 个 error，若无 shim 会全线 PermissionError | ⚠️ 未直接证实 |
| 5 个 id 与 `regressed` 集**完全一致** | 我从 junit 重算：`regressed` = 5 条；`regressed_in_control` = **同一 5 条**；`passed_in_control=[]`、`ids_not_run_in_control=[]` → **集合相等，且对照臂恰好覆盖 regressed 全集** | ✅ |

家族计数（我用 ElementTree 重算 junit，非读 handoff）：

- `family_before_junit.xml` = **1169 passed / 59 failed / 4 error / 11 skipped**（合计 1243）
- `family_after_junit.xml` = **1164 passed / 64 failed / 4 error / 11 skipped**（合计 1243）
- 逐 id 分类：`regressed=5`、`fixed=0`、`other=0`、`added=0`、`removed=0`、`same=1238` —— 与 `family_diff.json` **逐项一致**
- `family_ctl_subset_junit.xml` = 5 tests / 5 failures

### 3.2 我自己的独立对照重跑（决定性）

把 `iso_ctl/rf` 整树拷进 `%TEMP%\revf2\ctltree`（拷贝后与源树哈希一致），带 `-p i10a_dir_mode_shim` + 短 basetemp，在我自己的 session 跑这 5 个 id：

```
FAILED tests/test_fc1004_platform.py::test_install_sync_gate_detects_drift
FAILED tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity[install_root0]
FAILED tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity[install_root1]
FAILED tests/test_zr907_drift_patrol.py::test_c3_cli_reports_all_checks
FAILED tests/test_zr907_drift_patrol.py::test_c3_patrol_core_gates_green
6 failed, 2 passed in 606.91s   (rc=1)
```

**5/5 全部失败，且我这份 junit 里 traceback 与 subprocess 实参都指向我自己的 `ctltree`**（无实现者那份的路径矛盾）。→ "**原像树在本 session 也过不了这 5 个**"由我独立证实。

同法在 `isotree`（AFTER 树）上跑 fc1004 + zr907×2：**3/3 失败**（与家族结果一致）。

### 3.3 `sync_installations` 生产侧 rc=1 / 198 DIFF

- 盘上证据：`evidence/production_install_check.txt`（`production_rc=1`、`iso_rc=1`、每目标 `198 files`）。
- **我自跑**（只读 hash check，不带 `--apply`）：`python -B tools\sync_installations.py` → **rc=1**，`DIFF …\.agents\skills: 198 files`、`DIFF …\.codex\skills: 198 files`。与在盘证据一致。

### 3.4 结论

**"environment=5、fix_attributable=0" 成立。** 该主张免于 P1 的关键在于它不是自我循环——我用字节级原像树独立复现了 5/5 失败，且生产侧安装漂移独立复现。残留一条 P3 留痕问题（P3-1）与一条根因未诊断（见 unverified）。

---

## 4. 【第 3 项】`changes.diff`

- **14366 B**、**LF only（CRLF=0）**、**无 BOM**、sha256 = `bcd44c249da249b283cc06088e5da8e3aa8d092ecae28cae506be631503f6db8`（我自算）。
- `--- a/` / `+++ b/` 各 **8** 条，两侧集合相同：
  `scripts/forecast/calc.py`、`scripts/forecast/segments.py`、`tests/golden_behavior_hashes.json`、`tests/test_golden_behavior_lock.py`、`tests/test_industry_end_to_end.py`、`tests/test_lifecycle_forecasts.py`、`tests/test_models.py`、`tests/test_zr709_zijin_journey.py`。
- **产品面恰 2 个**：`calc.py 14978 → 15969`（`bc4f33d9…` → `9eecf260…`）、`segments.py 27697 → 27966`（`95555509…` → `cd6edee6…`）—— 与我实测的两棵树字节数/sha **完全一致**。
- **`git apply --check`（对生产树）rc=0**，8 个 patch 全部 "Checking patch …" 无报错。
- **最强一步**：我用自己写的 unified-diff 应用器，把 `生产树原文 + changes.diff` 应用后与 `iso/rf` 对应文件逐字节比对 → **8/8 MATCH（ALL_MATCH=True）**。即 `changes.diff` **既不缺也不多**，`unexpected=0 / missing=0` 是可证的，不是自述。
- **改动只在 iso、生产树零写**：
  - `git diff HEAD --name-only` 我跑了两次（`core.quotepath=false`），**total=3826，非 `.planning` = 0**（实现者自述 3824，差 2 个都在 `.planning` 内，非本卡面）。
  - `iso_ctl/rf/{scripts,tests,tools}` vs 生产 = 0 差异；`iso/rf` vs 生产 = 恰 8 文件（即上面 8 个）。
  - 我复算 handoff 的 **147 条 deliverable sha/bytes：0 mismatch**（开工、收尾各一次）。

---

## 5. 【第 4 项】夹具改动是否弱化测试（D-5）

做法：把 6 个夹具文件的**生产前像**与 **iso 后像**全文比对，抽取所有断言行（`assert*` / `assertRaises*` / `pytest.raises` / `self.assert*` / `assert re.`）做多重集比对，并单独 grep `skip|xfail`。

| 文件 | 断言行 before | after | 删/改 | 增/改 | skip/xfail 新增 |
|---|---|---|---|---|---|
| tests/golden_behavior_hashes.json | 0 | 0 | — | — | 0 |
| tests/test_golden_behavior_lock.py | 2 | 2 | **0** | **0** | 0 |
| tests/test_industry_end_to_end.py | 15 | 15 | **0** | **0** | 0 |
| tests/test_lifecycle_forecasts.py | 19 | 19 | **0** | **0** | 0 |
| tests/test_models.py | 10 | 10 | **0** | **0** | 0 |
| tests/test_zr709_zijin_journey.py | 41 | 41 | **0** | **0** | 0 |

两处自曝逐字核对：

1. **`test_lifecycle_forecasts._document`**：改动只有 ① import 行多引入 `MODEL_SPECS`；② 新增一段 `for _opt in MODEL_SPECS[model]["optional"] … ids[_opt] = [0.0 …]` 的**补参**循环。**无任何断言被删/被改**，只是把"被产品拒绝的隐式省缺"改成"显式给 0.0"。→ **没有变松**。
2. **`test_retail_franchise_optional_pair_is_enforced`**：我把前后两个函数体整段打印比对 —— 断言行
   `with self.assertRaisesRegex(ForecastInputError, "requires franchise_system_sales and recognized_fee_rate together"): run_forecast(data)`
   **逐字节未变**；新增的只有一行
   `data["segments"][0]["scenarios"]["low"]["driver_parameter_ids"].pop("recognized_fee_rate", None)`（前置条件显式化）。
   关键点：该断言带**具体报文正则**，若现在是被 F-I10A-2 的 `missing driver …` 异常触发，`assertRaisesRegex` 会**不匹配而失败**；`fixture_fix_check_junit.xml` = **114 tests / 0 failures / 0 errors**，说明**仍然是那条 pair 规则在报文**，测试没有被绕开。→ **没有变松，前置条件反而更显式**。
3. 旁证：`family_diff_preedit.json` 记录了 D-5 两处编辑**之前**的 60 个翻转（全部是"缺显式 0.0 可选驱动"导致），D-5 编辑后收敛为 5；`golden_after_update_junit.xml` = 1 test / 0 failure（golden 刷新后真的绿）；`test_zr709` 的 41 条断言也 0 删 0 增。

**判定：夹具改动没有弱化任何测试。** 实现者"断言一字未改"的说法**逐字核实为真**。

---

## 6. 【第 5 项】D-1 披露 vs 父方复原记录（**只核，不处置**）

### 6.1 三份记录对照

| 项 | 实现者 `handoff.D-1` + `evidence/production_runtime_log_restore.json` | 父方 `REMEDIATION_RECORD.md` / `INCIDENT.md` | 一致？ |
|---|---|---|---|
| 触发动作 | 对生产树跑 `golden_value_identity.py`，`run_forecast` 追加 5 条 | 同 | ✅ |
| 时间窗 | `registered_at 2026-09-24T20:02:50Z–20:02:51Z` | `20:02:50.848835 → 20:02:51.036956`（190 ms 内） | ✅ |
| 前像 | 65 行 / 50229 B / `18310faea83bad23e68f6713b2c5cce2ad6a3d89f6d8a6b8a02419659335ad55` | PRE **65 行 / 50229 B / 同 sha** | ✅ |
| 目标后像 | 预测截断到 60 行 → `bc3256bb…` | POST **60 行 / 46369 B / `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`** | ✅ |
| 被跟踪文件 | `tracked_file_written=false`；`git diff HEAD 非 .planning = 0` | `git ls-files --error-unmatch rc=1`（未跟踪）、`git check-ignore -v rc=0 → .gitignore:16 artifacts/` | ✅（我亦独立复测：rc=1 / rc=0 同结论） |
| ReadOnly | `attempted=true, succeeded=false`，**自判 BLOCKED、未清保护位** | `readonly_before=True → readonly_after=False`（复原时由父清除） | ✅ 无矛盾 |
| 时序 | 实现者证据 `at=2026-09-24T21:55:33`（本地，=20:55:33Z），handoff `generated_at=22:19:49`（本地） | `executed_at_utc=2026-09-24T21:41:35Z`（=22:41:35 本地） | ✅ 顺序：工位取证 → 交卡 → owner 裁 (a) → 父执行 |

### 6.2 我对现盘的只读复测

- `artifacts/registry/publications.jsonl` = **60 行 / 46369 B / `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`**、属性 `Archive`（**ReadOnly 已清**）→ 与父方 POST **完全一致**。
- 事故目录在盘：`execution_runs/_isolation_incidents/20260924-i10a-f2-baseline-wrote-production-registry/` 含 `INCIDENT.md`(5966 B)、`REMEDIATION_RECORD.md`(992 B)、`publications.jsonl.pre_truncation_20260924`。
- `publications.jsonl.pre_truncation_20260924` = **50229 B / 65 行 / `18310faea83bad23e68f6713b2c5cce2ad6a3d89f6d8a6b8a02419659335ad55`**（我自算），与前像一致。
- `INCIDENT.md` 中 `status: **RESOLVED**`（原 `OPEN` 行已划除），`detected_by: 修卡工位自报`、`verified_by: 父独立取证`。

**结论：实现者的 D-1 披露与父方复原记录在时间、行数、字节、sha、ReadOnly 状态上完全一致，无矛盾。** 我**未**重做截断、**未**改该文件、**未**清属性、**未**改 handoff。

---

## 7. 【第 6 项】B-1 blocked 是否成立

| 支撑点 | 盘上证据 | 我的独立复测 |
|---|---|---|
| 生产侧只读 hash check 就是红的 | `evidence/production_install_check.txt`（production_rc=1 / iso_rc=1 / 每目标 198 DIFF） | **我自跑 rc=1，`.agents` 与 `.codex` 均 198 files DIFF** |
| 原像树同样过不了这 5 个 | `evidence/family_ctl_subset_junit.xml`（5/5 failed）、`family_diff_control.json` | **我在字节级原像副本上重跑，5/5 failed，606.91s** |
| 5 个 id 就是 regressed 全集 | `family_diff.json` / `family_diff_control.json` | 我重算 junit：集合**完全相等**，`passed_in_control=[]`、`ids_not_run_in_control=[]` |
| 未新增 skip/xfail 掩盖 | handoff `no_new_skip_or_xfail=true` | 我对 6 个夹具文件 grep：**0 新增** |

**B-1 成立**：这 5 个安装/平台门在本 session 的失败**与本卡修复无关**（原像树同样失败、生产侧安装漂移独立复现），属于环境性。B-1 声称的"environment, not the fix"得到独立证据支撑。

**残留（不推翻 B-1，但要说清）**：`test_fc1004_platform::test_install_sync_gate_detects_drift` 用的是 `--destination tmp_path/installed` 一次性目标、`returncode=1` 且 **stdout 为空**（= 子进程崩了，而非 diff 报告），其**根因未诊断**；它在原像树上同样失败，因此只到"非本卡回归"这一层，**未到"已知为何必失败"**。

---

## 8. 另核三处自曝 + 两处过程瑕疵

### D-2 环境 shim — **只改权限，不改断言/夹具/SUT** ✅

- `scripts/i10a_dir_mode_shim.py`（1584 B，sha `68a3a29677d28e28…` 与 handoff 一致）全文只做一件事：`os.mkdir = _mkdir`，把 `mode` 参数丢掉、按默认 `0o777` 创建；**不 import 产品、不碰 conftest/夹具/断言、不筛选用例**。
- `scripts/_modeprobe.py`（588 B）在盘，`attempt/scratch/m700`、`scratch/pathlib700` 等探针目录在盘（我在 attempt 树里看到它们）。
- 我额外 grep 了 6 个夹具文件 + 全 tests 树的 `0o700|0o600|chmod|st_mode`：唯一命中是 `test_publication_registry.py:70 path.chmod(S_IWRITE|S_IREAD)`，**与 mkdir mode 无关** → 没有任何断言会因 shim 而被掩盖。
- 限制：AFTER 与 CONTROL 都带 shim、**BEFORE 不带**（跨 session），handoff 已如实注明。

### D-3 生产面副作用 — **披露完整** ✅

- 披露内容与我读到的源码一致：`test_zr804_platform_shape._sync_installations()` 执行 `tools/sync_installations.py --apply`（**无 `--destination`** → 走 `DEFAULT_DESTINATIONS` = `Path.home()/.{agents,claude,codex}/skills`），即 `.planning` 之外。
- 证据在盘：`evidence/family_after_stdout.txt` 内 `sync_installations` 7 处、`--apply` 3 处、`TimeoutExpired` 6 处。
- "基线跑也这么干过"：`family_before_junit.xml` 里 zr804 两条 `installed_copy…` 为 **passed** → 它当时**必然**执行过同一条 `--apply`。✅ 成立。
- `tools/sync_installations.py` 默认模式（不带 `--apply`）是**只读 hash check**（`main()` 只有 `--apply`/`--print-manifest`/`--import-from` 才会写），我只用了默认模式。

### 过程瑕疵 ①（mut_guard CRLF 漂移）— 归位为真、旧记录在盘且标废 ✅

- `evidence/mut_arm_superseded_r1.json`（1276 B）在盘，含 `superseded` 字段明写"text-mode … sha256 over in-memory (LF) … 已归位 … `evidence/mut_arm.json` is the authoritative record"。
- 时间线自洽：r1 `apply/restore` = `21:12:16/21:12:26` → 标废 `superseded_at=21:15:18` → 正式 `mut_arm.json` `apply/restore` = `21:15:18/21:15:24` → `rc_mut_arms.started_at=21:15:22`、`rc_mut_restored.started_at=21:15:30`，**整臂确在字节模式归位之后重跑**。
- 归位实证：我现在算 `iso/rf/scripts/forecast/calc.py` = **15969 B / `9eecf260…`**，且 **CRLF=0、LF=390**（真·LF，无漂移残留）。
- 小瑕疵：`mut_arm_superseded_r1.json` 同时出现在 handoff 的 `evidence_paths` 里（它是 147 条 hash 清单的一员），但**没有任何 run_log 记录把它当证据引用**，run_log 第 5 条只引 `evidence/mut_arm.json` → 视为"留档且未用作证据"。

### 过程瑕疵 ②（validator verbatim 拷贝 rc=3）— 披露在盘 ✅，但原始输出未留 ❌→unverified

- `run_log.jsonl` 第 9 条完整披露：verbatim 拷贝跑 rc=3 的原因是 `validate_adaptation` 按自身位置解析 ATT、我方 attempt 无 `evidence/I-10-A/source_extracts`（63 个 R3 quote-not-found），属误用；改用 I-10-A 原脚本。
- 正确产物在盘：`command_runs/CMD-I10A2F2-VALIDATE-GREEN/validate_result.json`（181 B）= `verdict:"pass", violations: [], raw_rc:0`。
- **但披露明写"its output was overwritten by the correct run"** → 首次 rc=3 的输出**已不在盘**，我**无法独立验证那次 rc=3**（也无法验证"原脚本"这一说法——`validate_result.json` 不含脚本路径/sha）。列为 unverified。

---

## 9. 发现分级

### P1
无。

### P2
无。

### P3（证据质量 / 留痕，不推翻结论）

- **P3-1 `family_ctl_subset_junit.xml` 内部路径自相矛盾。**
  同一份文件里，zr804 的 subprocess 实参是 `…\iso_ctl\rf\tools\sync_installations.py`（4 处，JSON 转义 `\\`），而 traceback 的源文件路径是 `..\..\iso\rf\tests\test_zr804_platform_shape.py:161/176`（7 处，**指向 AFTER 树**）——两者由同一模块的 `__file__`/`co_filename` 推出，**不可能同时为真**（`iso/rf` 与 `iso_ctl/rf` 的 `tests/` 是两个内容不同的真实目录，已哈希验证）。
  同时，**对照臂的 pytest 实际命令行 / cwd / rootdir 没有落在盘上任何地方**（`run_log.jsonl` 只有叙述，`family_ctl_subset_stdout.txt` 无 session 头、无 `rootdir:` 行）。
  影响：对照臂的"树=iso_ctl"只有 zr804 的实参这一条硬证据，fc1004/zr907 三条的树归属在他们的产物里**是含糊的**。
  为何不升级：结论已被**我的独立原像树重跑（5/5 failed）**替代证明；且我那份对照 junit 中 traceback 与实参**同指一棵树**，可作正确留痕的样板。
- **P3-2 首次 validator rc=3 的输出被覆盖，未留档。** 披露本身在 `run_log`，但原始产物不可复核（见 §8 末）。
- **P3-3 BEFORE 家族跑的命令行/stdout 未留盘。** 只有 `family_before_junit.xml`（+`family_before.json` 纯状态表），"上一 session、默认临时根、无 shim"是 handoff 的**自述**；我只能从 junit 里 `Temp\...` 匹配为空**间接印证**"不是本 session 的短根"。
- **P3-4 `evidence/family_measure_junit.xml`（1169/59/4/11，与 family_before 同计数）未在 handoff 中说明其用途/来源**，仅作为 hash 清单成员列出；不构成矛盾，但读者无法定位它与 `family_before_junit.xml` 的关系。

（观察项，非发现：生产树存在未跟踪根 `.tmp-r41-mutation`（创建于 2026-09-20，**早于本 attempt**）与 `assurance/`（D-4 已披露的调度器产物）；两者均在 handoff `production_readonly_self_check.untracked_non_planning_roots` 中列出，非本卡写入。）

---

## 10. Unverified（缺证据，如实记，不造绿）

1. **新拒绝的 CLI rc=2 端到端路径**未跑通（实现者自曝，probe 直接调 `calculate_model_path`）；我亦未补跑 → **未证实**。
2. **最终 `family_after` / `family_ctl` 两次 pytest 是否真的 `-p i10a_dir_mode_shim`**：盘上无命令行留痕，`plugins:` 行只列 entry-point 插件（不列 `-p` 模块），只能间接推断（若无 shim 会全线 PermissionError，而两次都只有 4 error）→ **未证实**。
3. **`test_fc1004` 在一次性 destination 上 `rc=1`+空 stdout 的根因**未诊断 → 只能说"原像树同样失败=非本卡回归"，不能说"已知为何必失败"。
4. **"5 个安装门在干净环境下会绿"** 未验证（也不在 B-1 要求内）。
5. **validator rc=0 来自 I-10-A 原脚本** 的出处（脚本路径/sha 未记录在 `validate_result.json`）→ 未证实。
6. **D-3 的完整性**：我只核了已披露的 `sync_installations --apply` 机制，**没有穷举 1243 个用例里所有写 `.planning` 之外的路径** → 未穷尽。
7. handoff 记 `git_diff_HEAD_name_only_total=3824`，我两次实测 **3826**；差 2 全在 `.planning` 内，非本卡面，**未追查具体两条**（非 `.planning` 均为 0，此点两版一致）。

---

## 11. 我没有做的事（边界声明）

- **没有**创建/修改 `handoff.json`，**没有**改任何 status，**没有**替实现者落定，**没有**处置 D-1。
- **没有**重做 `publications.jsonl` 截断、**没有**动该文件、**没有**清任何保护属性、**没有**改 `REMEDIATION_RECORD.md`/`INCIDENT.md`。
- **没有**改本 attempt 任何既有字节（收尾用 147 条 deliverable sha + 4 个根文件 sha 复算，0 mismatch；`iso/rf/scripts/forecast/calc.py` 仍为 `9eecf260…`/15969 B）。
- **没有**执行 `git status`、**没有**任何 git 写操作（`git apply` 只加 `--check` / 在 `%TEMP%` 内 `--no-index`）、**没有**联网。
- **没有**在生产树或 attempt 树内跑任何测试；测试只在 `%TEMP%` 副本。
- 结束前复核：`git diff HEAD --name-only` **非 `.planning` = 0**。

### ⚠️ 必须自报的一处副作用（deviation）

我的独立对照重跑选了整个 `tests/test_zr804_platform_shape.py`，其中 `test_installed_copy_executes_with_canonical_identity` 会执行 `tools/sync_installations.py --apply` → 目标是 **`Path.home()/.agents/skills` 与 `Path.home()/.codex/skills`（`.planning` 之外）**，即 D-3 所披露的同一机制。该调用在 **300 s 超时被杀**，我**随后用只读 hash check 复测**：两目标仍各为 **`198 files DIFF`**（与我跑之前的生产侧读数相同），即**未观察到安装副本状态变化**；`git diff HEAD --name-only` 非 `.planning` 仍 = 0。这条副作用是我引入的、非实现者问题，按纪律如实留档（复跑 5 个 id 本可用 deselect 规避 zr804，我事先未预见到）。

### 复审过程中的自身操作瑕疵（留档，不掩饰）

首次重建 `changes.diff` 时，我的临时补丁文件用系统区域编码（GBK）写出，导致 `git apply` 结果被非 UTF-8 字节污染；**这是我的工具错误，不是被审产物的问题**。改用显式 `encoding="utf-8"` 后：`git apply --check` rc=0、我的 unified-diff 应用器 8/8 逐字节 MATCH。

---

## 12. 我实测的 rc / sha 速查

```
产物:  handoff.json            51834 B  00ae453b05a78435…
       changes.diff            14366 B  bcd44c249da249b2…   (LF only, no BOM, 8 文件)
       oracle.md               14872 B  6d6cf38463d9d822…
       frozen_regression_rerun 4580 B   1ceb9e430ef02a468…
       handoff 147 条 deliverable sha/bytes: 0 mismatch（开工+收尾各一次）

树:    iso/rf/scripts/forecast/calc.py       15969 B  9eecf260bfb22f1a…  (归位后仍为此值)
       iso/rf/scripts/forecast/segments.py   27966 B  cd6edee661bf5042…
       生产 calc.py                          14978 B  bc4f33d92738029a…
       生产 segments.py                      27697 B  95555509bc8a30af…
       model_registry.py  两树同 30116 B  62f864b9ab3f144e…
       model_extensions.py 两树同 14475 B  9939480b717d5a49…
       变异态 calc.py  15875 B  a80776421360bec3…  (= mut_arm.json sha_after)

三臂:  RED    mut_omit 3,3,3,2   (我的原像副本自跑)
       GREEN  mut_omit 2,2,2,2   (我的修复副本自跑)
       MUT    mut_omit 3,3,3,2   field_class all_pass=false (FC1/FC2 红)
       REST.  mut_omit 2,2,2,2   field_class all_pass=true  rc=0；sha 归位 9eecf260…

家族:  before 1169/59/4/11  after 1164/64/4/11  (我用 junit 重算)
       regressed=5  fixed/other/added/removed=0  same=1238
       对照臂 5/5 failed（我的原像副本自跑，606.91s）

生产:  sync_installations 只读 check  rc=1  .agents=198 DIFF .codex=198 DIFF（我自跑）
       publications.jsonl  60 行 46369 B  bc3256bbc7abca8c0…  属性 Archive(ReadOnly 已清)
       事故前像 50229 B / 65 行 / 18310faea83bad23…
       git diff HEAD --name-only 非 .planning = 0（两次）
```
