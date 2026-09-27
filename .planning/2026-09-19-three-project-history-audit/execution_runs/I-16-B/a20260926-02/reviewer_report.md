# I-16-B / a20260926-02 独立复审报告（部署窗口验收 · A 级全量档）

- 复审角色：`reviewer_i16b`（独立复审工位，部署验收者）；复审时刻 **2026-09-27 07:35–08:05 本地（UTC+1，下文 UTC 另标）**
- 被审 **8 件**：`oracle.md` · `deployment_record.md` · `verification.json` · `handoff.json` · `result_R4_gate2.json` · `r5_fullpath_result.json` · `r6_backup/catalog_backup.json` · `combo_manifest.json`（+ **脚本 4 件** `_bind_combo.py` / `_verify_combo.py` / `_recovery_drill.py` / `_probe_newprocess.py`，附 `probe_live.json` · `impact_scope.json` · `recovery_drill.json` · `snapshot_manifest.json` · `result_R4_gate.json`）
- 判据（只读）：`OWNER_DECISIONS §三十九`（L908–L935，R1–R8 逐字已取）· `I-16-A/a20260926-01/deployment_proposal.md`（`accepted_scoped`，含「复跑仍红 ⇒ 不得开部署窗口」）+ `impact_scope.json`（`production_change_executed=false` 冻结件）· `execution_v2/card_I-16-B.md`（13 行）
- 上一 attempt：`I-16-B/a20260926-01/`（`blocked` 载体 + 复审报告 `ACCEPT(P2×2/P3×5)`，`sha b0bc2ec5…` 之上我再自算 `13879cf6…`）
- **写入面 = 本目录 2 个新文件**（`reviewer_report.md` + `reviewer_report.sha256`）；R4 复跑产物落 `%TEMP%\i16b_review_r4_rerun.json`（避免污染被审目录）；被审/判据只读、收尾复哈希；三仓只读（仅 `git diff HEAD/--cached --name-only`、`ls-files --others`、`rev-parse/log`，**未跑 `git status`**）；**零 git 写 · 零联网**（复用探测为本地查询，跑后目录 mtime 复核零写）；不写卡状态。

---

## 1. 裁决行 + 发现清单

### VERDICT：`ACCEPT`（`P2×2` + `P3×7`；**无 P1**）

> **P1 七项触发逐条排除**：
> ① **部署越权 / `git` 写 / 参数放行 / worker 被动 = 全否**：窗口扫描（本地 06:13–07:40 = 执行窗口）内 `C:\Miniconda\Lib\site-packages` **0 件**、`C:\Miniconda\Scripts` **0 件**、`RF/config` **0 件**、`CW/config` **0 件**；三仓 `staged=0`、`HEAD` 均未变（`RF b7a6a116` / `CW dbe47450` / `DAYU 2115c86d`）；`worker_control.json` mtime 仍 `2026-08-20 22:43:32`、`config/.source_catalog/worker_*` 仍 `2026-08-08` ⇒ 未启停未 resume；生产写入仅 `.source_catalog` 5 件（`catalog.sqlite3`/`-wal`/`acquisition_attempts.jsonl`/`paused_acquisition.log`/`staging/**`）+ raw 2 件（MSFT `__095935f968b5.htm`+sidecar）——**逐件落在 `§三十九 R1` 授权面内**。
> ② **R6 备份不一致 = 否**：备份自算 `sha 63c359aa…` = `r6_backup/catalog_backup.json` 记录值 = `I-16-A/recovery_drill.json` **执行前锚点** `sha256_at_bind`；备份 `size 3055796224` = 锚点 `bytes` = `combo_manifest.data_layer.catalog.bytes`（三项独立互证）。
> ③ **回归排除证据成立**（见 §4，三条各有一手证据，其中 ② 为**同文档同日失败**的决定性证据）⇒ 不升 P1。
> ④ **封盘被动 = 否**：`f2178768…`(51697 B) 与 `b2063ac8…`(61231 B) 我方收尾自算**零字节一致**，mtime 分别停在 `2026-09-20 15:48:19` / `2026-09-26 01:10:16`（窗口内未触碰）。

| # | 发现 | 级别 |
|---|---|---|
| 1 | **R4 门复跑 `rc=3`（非 `rc=0`）**：`violations=[J1_repo_source, J6_recovery]`；且 **`§三十九 R4` 硬前置「静默后转绿才开窗」在开窗时点未维持**——绿灯 `gate2=2026-09-27T01:55:56Z`，开窗（R6 备份）`05:13:45Z`，**间隔 3h18m 内 CW 已有 8 件外部写入**，窗口内再 5 件；被审 `oracle S1` 只写「J1–J8 rc=0 全绿」，**未披露绿灯已过期** | **P2-1** |
| 2 | **R5「修复」未持久化**：`I-16-B/_recovery_drill.py` 与 `I-16-A` **字节完全相同**（`sha 5898d162…`、9526 B），**`L42` 仍为 `Path(row["source_path"]).name`（basename 落盘）**；全路径重跑的实现**不在写入面 4 件脚本内**，只有产物树 + 结果 JSON 落盘 ⇒ 修复**不可复算、不可重跑**；且本 attempt 自身 `snapshot_manifest` 为 **159 行 / 154 个 `repo+basename` 目的地**，今日若按现脚本跑仍会产生 **5 件同名覆盖** | **P2-2** |
| 3 | `oracle` 为**事后补记**（`handoff.oracle_frozen_before_execution=false` 如实登记；执行依据 `§三十九` + `I-16-A` 提案确在执行前冻结） | **P3-1**（已知必判） |
| 4 | `oracle findings ②` 称占用文件「mtime 早于本会话 **5 天**」，实测 **2026-09-19 05:52:59（本地）→ 2026-09-27 = 8 天**；结论方向（早于本会话）不受影响 | **P3-2** |
| 5 | R6 记录 `sha 63c359aa 与源一致` **未标时点**：复审时点源已变为 `3055800320 B / 30794a01…`（**+4096 B**，授权摄取写入所致，J6 因此红）⇒ 该句仅在「备份时刻」成立，须补时点限定 | **P3-3** |
| 6 | `handoff.written_files` 列入的 `recovery_drill.json`（`7130a6e0…`）与 `impact_scope.json`（`e0959fb9…`）**是 I-16-A 的副本**（内容 `card_id=I-16-A`、`run_at=2026-09-26T21:30:59Z`、`production_change_executed=false`），未标注「上游副本」，与 `handoff.production_change_executed=true` 并存易误读 | **P3-4** |
| 7 | `result_R4_gate2.json` 头部 `card_id/attempt_id = I-16-A / a20260926-01`（脚本硬编码）而非 `I-16-B / a20260926-02` ⇒ 产出物身份与所在 attempt 不符 | **P3-5** |
| 8 | **①CN 数据可得性的正向归因未证**：`SA2025` 实录 `adapter_discovery_returned_no_candidate`（`05:48:09Z`）；「`AR2024/AR2025` 可得 ⇒ 非路由故障」是**不完全归纳**，且禁网无法核 cninfo 是否有紫金 2025 半年报（catalog 内紫金 `semi_annual_report = 0`）；**但「非本会话引起」已证**（见 §4） | **P3-6** |
| 9 | 窗口内 `CW/.source_catalog/paused_acquisition.log`（`2233 B`，`06:27:34Z`）被写，**未列入** `oracle` 步骤表与 `handoff.production_change_summary` 的写入面清单 | **P3-7** |

---

## 2. ⭐ R4 门复跑（任务书指定命令）

```
python -X utf8 -B _verify_combo.py --probe probe_live.json --manifest combo_manifest.json --out %TEMP%\i16b_review_r4_rerun.json
→ mode=live  rc=3  violations=['J1_repo_source','J6_recovery']   （本地 2026-09-27 07:35:28 = 06:35:28Z）
```

**`rc=3 ≠ 0`**，逐条归因（我方独立取证）：

| 违例 | 具体 | 归因（是否本部署会话） |
|---|---|---|
| `J1` | `RF: diff non_planning 2 != 0` → `assurance/runs/weekly_alert.jsonl`、`weekly_manifest.json`；`RF: untracked set changed` → `+1 = assurance/runs/weekly-run-20260927T033001Z.log` | **独立周调度**：`weekly_t3_schedule.py run-weekly`（脚本自述 “scheduled assurance loop … Windows Task Scheduler weekly task”），日志 `run_id=20260927T033001Z`、`started_at=03:31:35Z`，`weekly_alert.jsonl` 另有 `09-06/09-13/09-20` 三次历史行；**落在 01:55Z 绑定之后、05:13Z 开窗之前，非部署会话** |
| `J1` | `CW: untracked set changed`（**+4 / −0**：`src/company_wiki/source_catalog/narrative_retrieval.py`、`tests/unit/test_narrative_retrieval.py`、`tests/e2e/test_narrative_g1_pipeline.py`、`docs/…/provider_cost_and_capability_2026-09-27.md`）+ **13 件 dirty content 变更** | **外部并发工位**（narrative-evidence-pilot 专题）：`CW/docs/…/progress.md` 三个新 Session 段自述其写入面「本轮只改本计划目录中的文档…未写 RF 仓库」，并记录 `I-16-B 卡仍 planned、01:55Z 快照对 91 个计划文件中 11 个 SHA 已变`；与上一 attempt P3-5 `u-I16A-0` 漂移同源；**非部署会话**（部署写入面=raw+catalog，见 §6） |
| `J6` | `production_catalog: size/exists changed`（我方自算 `3055800320` vs 锚点 `3055796224`，sha `30794a01…`） | **本部署的授权摄取写入**（R6 先备份后开库的必然结果）；本身**不构成越权**，但使「开窗前置=绿」在复审时点不成立 |

**重绑内容是否如实（任务书点名的 `CW:dbe4745/dirty=109`）—— 如实**：

- `CW HEAD = dbe474504a6187e22c37918743d17fe59c85a0a8`（我方 `git log -1` 自算）= `combo_manifest.repos.CW.head` ✅
- `dirty_content_count = 109` ✅（8 件 tracked 修改 + 101 件 untracked，我方独立枚举 `diff HEAD --name-only` = 8、`ls-files --others` = 101（绑定时点））
- **逐文件内容复核**：我方对 `CW.dirty_content` 109 条逐条重算 sha → **96 一致 / 13 已变**；13 件全部 = 上表外部并发的 narrative-evidence 文件 ⇒ **manifest 记录真实，漂移是记录之后发生的**。
- `RF b7a6a116 / dirty=48` ✅（HEAD 自算一致；`untracked(non-planning)` 48 → **49**，唯一新增即周调度日志）、`DAYU 2115c86 / dirty=2` ✅（`sec_downloader.py` 我方自算 `sha 4684933e…` 与绑定值**逐字相同**、mtime `2026-09-26 01:07` 早于窗口）。
- 另两道绿门（J2 安装副本 / J3 加载路径 / J4 解释器 / J5 config-policy-flags-schema / J7 影响范围 / J8 封盘）在我复跑中**仍全绿**。

**⇒ 记录的 `gate2 rc=0 @01:55:56Z` 是真的，但它不是「开窗时刻的绿」。**

---

## 3. ⭐ R5 修复核

**原缺陷（读代码）**：`I-16-A/a20260926-01/_recovery_drill.py L42` 逐字
`dst = out_root / row["repo"] / Path(row["source_path"]).name` ⇒ 按 **basename** 落盘 → 实测 **109 行 → 104 个 `repo+basename` 目的地 = 5 件同名覆盖**（我方自算 `distinct_basename=103`、`distinct(repo+basename)=104`，与上一 attempt「109→104、5 件覆盖」口径一致）。**原缺陷成立。**

**修复声称核（`r5_fullpath_result.json`：`rows=109 / distinct_destinations=109 / collisions=[] / pre_write_mismatch=[] / post_write_recheck_mismatch=[] / files_on_disk=109 / ok=true`）——数值全部自证通过，但载体有缺口**：

1. 我方独立复算 `drill_restore_fullpath/` = **109 文件（RF 48 + CW 59 + DAYU 2）**，与 `I-16-A/snapshot_manifest.json` 的 **109 行**一一对应（RF 48 / CW 59 / DAYU 2）；
2. 逐文件 `Get-FileHash` 对比其快照：**`BYTE_OK=109 / MISMATCH=0 / MISSING=0`**（写后复核通过）；该 manifest 自身 `all_match=true` 且 `source_sha256 == snapshot_sha256` **109/109**（写前复核通过）⇒ `pre/post_write_mismatch=[]` 属实；
3. 全路径口径下 **109 个唯一目的地、0 碰撞**属实（basename 口径则为 104 目的地 / 5 覆盖）。
4. **缺口**：`_recovery_drill.py` **未被修改**（与上游字节相同，`L42` 仍 basename）；全路径实现不在 4 件脚本内 ⇒ **结论：R5 的「结果」成立，「修复（改代码）」的声称不成立**，降级为 **P2-2**（非 P1：R5 属演练层，产物已可复核，且未动生产）。

> 附：`snapshot` 层行数口径差异已澄清 —— 本 attempt `snapshot_manifest = 159 行`（RF48+CW109+DAYU2，`created 01:55:35Z`），R5 复跑针对的是**有碰撞的 109 行集**（I-16-A manifest，`created 09-26T21:30:57Z`），两者不冲突但被审件未写明。

---

## 4. ⭐ 三项功能验证（卡文 L9）

### 4.1 已有复用 —— **我方自跑 1 次（只读）✅**

```
python -X utf8 -B scripts/fetch_filing.py --request-file .planning\_pwf_tmp\req_zijin_ar2025.json     # 不带 --allow-download
→ rc=0  status=capture_ready  outcome=reused_existing  downloads=0  calls=2
   byte_size=79925886  content_sha256=01819e1c…  collector=stockinfo-cninfo
   location=urn:company-wiki:location:sha256:22e19944…  document=urn:company-wiki:document:sha256:01819e1c…
```

- 与 `verification.reuse_tests[ZIJIN AR2025]` 的 `bytes=79925886 / collector=stockinfo-cninfo / capture_ready` **逐字段一致**；文件本体 `companies\紫金矿业\raw\financial_reports\annual\2026-03-20_cninfo_1225023658_…2025年年度报告.pdf = 79925886 B` 自核一致。
- **只读性自证**：探测后 `acquisition_attempts.jsonl`(07:27:34Z) / `catalog.sqlite3`(07:23:51Z) / `paused_acquisition.log` mtime **全部未变**（探测发生于 07:47Z 之后）⇒ 我方未产生生产写、未联网下载。
- 另 2 项（`ZIJIN AR2024` 32100114 B、`MSFT FY2025` 8158067 B）**未重复自跑**，以被审记录 + 目录内文件字节数自核（32100114 / 8158067 均与记录相同）作为旁证。

### 4.2 新文件摄取 3 失败 —— **回归排除证据逐条核（成立）**

| # | 失败（`acquisition_attempts.jsonl` 一手记录） | 我方证据 | 结论 |
|---|---|---|---|
| ① `ZIJIN SA2025` | `05:48:09Z` `adapter_discovery_returned_no_candidate` / `stockinfo-cninfo` / `outcome=missing`（`verification` 记 calls=3 downloads=0） | **同类失败早于本会话**：同一 reason 在 `2026-07-23T20:57Z`（stockinfo）、`2026-07-24T20:10Z`（stockinfo）、`2026-07-20/07-23`（dayu）各出现过，全库该 reason 共 **5 条**；**本会话未改任何相关代码/配置**（J2/J3/J4/J5 复跑绿、`RF/config` 与 `CW/config` 窗口内 **0 写**、`sec_form_utils.py`/`acquisition_service.py`/`close_gap.py` 与 HEAD 无 diff）；catalog 内紫金 `semi_annual_report = 0`（`annual_report` 有 2 件）；**旁证**：同日本会话外的周调度 e2e `DownloadE2E.test_download_cn_annual_report` 亦红（`upstream_unavailable`，历史 09-13/09-20 同红） | **非回归成立**；但正向因由「数据可得性」**未证**（禁网）→ **P3-6** |
| ② `MSFT 10-K FY2026` | `06:16:35Z` `canonical_import_failed` / `CanonicalImportError` / `content_sha 095935f9…` | **决定性**：同一 `provider_document_id = sec:0001193125-26-323660` 在 **`2026-09-19T04:53:00Z`** 已以同一 reason 失败过一次（`content_sha e3de0053…`）；占位文件 `…10-K 2026-06-30.htm` **mtime 自算 = `2026-09-19 05:52:59`**（早于本会话 **8 天**，被审写「5 天」→ P3-2）；失败产物 `…__095935f968b5.htm`(8585621 B)+sidecar mtime `2026-09-27 07:16:27` = 窗口内；`acquisition_service.py`(mtime 08-08)/`close_gap.py`(mtime 09-16) **与 HEAD 无 diff** | **非回归 —— 决定性成立** |
| ③ `MSFT 10-Q FY2026` | `06:23:58Z` `DayuCliAdapterError: 不支持的 form_type: ['10-Q/A']` | `dayu/fins/pipelines/sec_form_utils.py` **L107 逐字** `raise ValueError(f"不支持的 form_type: {unsupported}")`；我方自算 **`mtime 2026-05-30 22:42:42`、`sha256 431ea8560fc71d7c6f57921ee9cc339aa33ac9a964117ff9a24a0c423ccd3fd3`**（4 个月未动、非 B2 晋升件、DAYU `git diff` 不含此文件）；同 reason `adapter_or_staging_failed` 全库 **15 条**、最早 `2026-07-20` | **非回归成立** |

**⇒ 回归排除证据成立（不升 P1）。**

### 4.3 工件失效最小重算 —— **`unverified` 维持（机制自核通过）**

我方只读 sqlite（`file:…?mode=ro`，`rc=0`）：表 **18 张**（= `combo_manifest.data_layer.table_count`）；`artifacts = 8191` 行（与 `verification.artifact_invalidation` 声称值**自算一致**）；`producer_events = 473` 行、`activation_journal = 1` 行**均存在**；`sources 43112 / documents 23530 / locations 46606`。
**无实况失效事件、无安全触发方式、不伪造** ⇒ **`unverified` 判定正确**，机制在位已证。

---

## 5. ⭐ R6 备份（我方自算）

| 项 | 我方自算 | 对照 | 结论 |
|---|---|---|---|
| 备份文件 sha256 | `63c359aa4b09545a540a05f8d32d66ac3c9dbd4ccf696470d55cb38a31f6dcfc` | `r6_backup/catalog_backup.json.sha256` = 同值 | ✅ 记录真实 |
| 备份 `size` | `3055796224` | = `I-16-A/recovery_drill.production_catalog_anchor.bytes` = `combo_manifest.data_layer.catalog.bytes` = 被审 `impact_scope` 所载 `3,055,796,224 B` | ✅ 与**执行前冻结锚点**一致 |
| 「与源一致」 | **执行前锚点** `sha256_at_bind = 63c359aa…`（I-16-A，`09-26T21:30:57Z`）+ 备份 `mtime` 保留为 `2026-09-26T17:48:22.684241Z` = 锚点 `mtime_utc` | 三重互证 ⇒ 备份内容 = 执行前源 | ✅ **备份有效性成立** |
| **当前源** | `3055800320 B / 30794a01e04a9e77ec13cd7b27a3f24bf9861bda9fc7c3c50a2b362830fbc823`（**+4096 B**） | = 备份之后的授权摄取写入（`catalog.sqlite3` mtime `2026-09-27 07:23:51` 在窗口内） | ⚠ 记录须补时点限定 → **P3-3**；J6 因此复跑红 → 归入 **P2-1** |

⇒ **R6 不构成 P1**（「先备份再开库」`fail-closed` 纪律被遵守：备份 06:13:45Z 在首笔生产写 06:16:27Z **之前**）。

---

## 6. 边界（任务书第 6 项）

| 项 | 我方只读实测 | 结论 |
|---|---|---|
| **`dayu-agent` 未改未提交** | `git diff HEAD --name-only` = **1**（`dayu/fins/downloaders/sec_downloader.py`），`--cached` = **0**，`ls-files --others` = **1**（`docs/architecture_report.html`）；`HEAD = 2115c86d…` 未变；`sec_downloader.py` 我方自算 `sha 4684933e076e759c8ebc8acc494c0611f763e95364bc4a9d0a9a16165e1e4e1b` = 绑定值、mtime `2026-09-26 01:07:03` 早于窗口 | ✅ 源零改零提交（**披露**：窗口内 `dayu/**/__pycache__/*.pyc` 18 件被写 = 入口复验的字节码缓存，已 gitignore，`ls-files --others` 不含） |
| **`rf` 非 `.planning` = 0** | 实测 **= 2**（`assurance/runs/weekly_alert.jsonl`、`weekly_manifest.json`）；`untracked(non-planning)` **49**（绑定 48，+1 为 `weekly-run-20260927T033001Z.log`）；`staged = 0`；`HEAD = b7a6a116` 未变 | ❌ **不为 0**，但归因于**独立 Windows 周调度**（脚本 + 4 次历史 run 记录），**非部署会话**；`handoff.git_diff_non_planning=0` / `oracle 边界自证 非.planning 0` 为**绑定时点口径**，复审时点已过期 → 并入 **P2-1** |
| **封盘 `f2178768…`** | `I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` = `51697 B` / `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | ✅ 零字节一致（mtime `2026-09-20 15:48:19` 未动） |
| **store `b2063ac8…`** | `OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json` = `61231 B` / `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` | ✅ 零字节一致（mtime `2026-09-26 01:10:16` 未动） |
| **`params_released=false`** | `handoff.params_released=false`、`verification.releases_nothing=true`；实测 `RF/config` 与 `CW/config` 窗口内 **0 件写入**；RF 非 `.planning` 差异仅上列 2 件（无参数载体）；`threshold_review_status` 未动 | ✅ 未放行参数 |
| **worker `paused` 维持** | `CW/.source_catalog/worker_control.json` 逐字 `{"desired_state":"paused", …}`、`178 B`、mtime **`2026-08-20 22:43:32`（窗口内未变）**；`config/.source_catalog/{worker_state,worker_runtime,worker_runs}.json` 全部停在 `2026-08-08`；`worker_control.json`（config 目录）ABSENT；`handoff.worker_processes_touched=0` | ✅ 状态文件层维持 `paused` 且未被改写；**进程级无审计可回放** → `unverified` |

---

## 7. P 清单与 `unverified`

### P2（须在结卡/下个 attempt 前处置）

- **P2-1｜R4 复跑 `rc=3` + 硬前置在开窗时点未维持**：`§三十九 R4` 逐字「✅ 批（**硬前置**：`CW untracked(np)` 实测 67 仍在漂，须静默后转绿才开窗）」、`I-16-A/deployment_proposal` 逐字「若复跑仍红 ⇒ 组合不稳定，**不得开部署窗口**」。实况：绿灯 `01:55:56Z` → 开窗 `05:13:45Z`，**期间 CW 8 件外部写入**（`02:03/03:12/03:14/04:51/05:08/05:09/05:09/05:11Z`）、窗口内再 5 件；复跑 `J1` 红（RF 周调度 2+1、CW 漂移 13+4）、`J6` 红（catalog +4096）。**三类漂移均已归因到非本部署会话/授权写入 ⇒ 不升 P1**，但被审件「S1 J1–J8 rc=0 全绿」缺时点披露，且 owner 的开窗条件未真正满足。**要求**：结卡时把「绿灯时点 / 开窗时点 / 期间漂移」三元组写明；下个窗口须**先静默、再复跑、绿后立即开窗**，并把 `RF assurance/runs/` 周调度纳入静默清单。
- **P2-2｜R5「修复」未落到可复算载体**：`_recovery_drill.py` 与上游字节相同（`5898d162…`）、`L42` 仍 `basename`；全路径重跑实现不在写入面 4 件内；本 attempt manifest 159 行按现脚本仍会 5 件覆盖。**要求**：把全路径实现作为持久化脚本纳入写入面（或把声明收窄为「对 109 行集的一次性全路径复原，已复核」），并对 159 行集补一次全路径复原。

### P3（记录，不阻断）

- **P3-1**｜`oracle` 事后补记（`handoff.oracle_frozen_before_execution=false` 如实登记；执行依据 `§三十九`+`I-16-A` 提案执行前已冻结）——**已知必判，判 P3 非 P1**。
- **P3-2**｜`findings ②`「早于本会话 5 天」实为 **8 天**（`2026-09-19 05:52:59` → `2026-09-27`）。
- **P3-3**｜R6「sha 与源一致」未标时点；复审时点源 `+4096 B`（`30794a01…`），须写成「与**执行前锚点**一致」。
- **P3-4**｜`handoff.written_files` 内 `recovery_drill.json`/`impact_scope.json` 为 I-16-A 副本未标注，且 `production_change_executed=false` 与 `handoff=true` 并存易误读。
- **P3-5**｜`result_R4_gate*.json` 的 `card_id/attempt_id = I-16-A/a20260926-01`，产出物身份与所在 attempt 不符。
- **P3-6**｜①CN 归因「数据可得性」未证（禁网；`AR 可得 ≠ SA 可得`；catalog 紫金 `semi_annual=0` 只说明**索引内**没有，不说明 cninfo 没有）。
- **P3-7**｜`paused_acquisition.log`（窗口内 `06:27:34Z`，`2233 B`）未入写入面清单。

### `unverified`（保持未解除）

1. **工件失效最小重算 = `unverified`**（无实况失效事件；机制已自核：`artifacts=8191`、`producer_events=473`、`activation_journal=1`、表 18 张）。
2. `I-14` 测量器测量（失败率/时延/内存）**未执行** —— `I-14-E` `OpenProcess DENIED` 阻断未解，**不代其出结论**（卡文 L10 因此未完成）。
3. CN `ZIJIN SA2025` 在 cninfo 的**真实数据可得性**（禁联网，无法核）。
4. **进程级「零启停/零 resume」**无审计日志可回放，仅状态文件 mtime 旁证。
5. skill 安装副本（`~\.claude\skills\revenue-forecast` Junction 目标）读/列被拒 —— 沿用上游 `u-I16A-skillcopy`。
6. 入口 shim ×4 `--help rc=0` 与 `dayu-cli sessions` 环境限制结论 **未由我复跑**（会再写 `__pycache__`，与写入面纪律冲突），按被审记录采信。
7. `CW` 外部并发漂移**仍在进行**（复审期间 `findings.md`/`task_plan.md` mtime 仍在推进）⇒ 组合稳定性问题未闭合。

---

## 8. 收尾复哈希（写本报告前自算）

| 被审件 | bytes | 自算 sha256 |
|---|---|---|
| `oracle.md` | 3400 | `16e52618f5b5c338692902f684d6aa609c240d59c5a98a206330bf8dd547d695` |
| `deployment_record.md` | 1219 | `1a53be9f66cc59628fd34cea114a633dfb8f1ee9c2aa75893b69c15ae4c84b18` |
| `verification.json` | 2084 | `9259b4895b1faef49297be7f7997a764628729d2f7a9658e5f75a1e9da4ec895` |
| `handoff.json` | 1686 | `adc3d9c54f1951a5a6f54abb9044dc7c6125ddfc89ca27c061f4fdd8f27a87a5` |
| `result_R4_gate2.json` | 1832 | `29f8c45655727082f22aa8e767ff106c7efa9de9a04f4aaf496a5349f414dea3` |
| `r5_fullpath_result.json` | 270 | `d2f680275381bb8d999cdb61ceb1738d87a850b030eed9125f45e6bd0f7520fb` |
| `r6_backup/catalog_backup.json` | 315 | `1f73e7144656aac89265da84945ad991222ea673c59581e4ee6ac2f539f1007b` |
| `combo_manifest.json` | 80773 | `3c45bc004ca9d4adf1ee11f71b1cc8b017e963eae0f38c972a0669d34577b86b` |
| `_bind_combo.py` | 19404 | `2f7df8ee8e0596afa8a881f22df98231712d10dbb09b4fc6bfd7bb12d239189c` |
| `_verify_combo.py` | 12976 | `29a2e8ab90c740226a2e7f78f33d282f5d598902abd58e96a531a153d79e9134` |
| `_recovery_drill.py` | 9526 | `5898d162b053ff63b0e8da656ec42e215d40dbf079011dcefa04e77cd61b1efd`（= I-16-A 同名件，字节相同） |
| `_probe_newprocess.py` | 6966 | `f55e39b8964ef1edf3723c7c306dd43b7b9e219f2d47b9fbe2891055982e9f2d` |
| `probe_live.json` | 4064 | `31f049874d144e5f5823fbaf65357c2f86a05143ccf284d9bb892cc26beefd1b` |
| `impact_scope.json` | 6439 | `e0959fb90afc68b793fa3260bb553a2d1aa029dba0baf4c1b221be05603ac71f`（= I-16-A 副本） |
| `recovery_drill.json` | 4606 | `7130a6e09a246abf7c685373d7401a1a57f4592e079e9c6f9c4eca38b30780fd`（= I-16-A 副本） |
| `snapshot_manifest.json` | 80666 | `0f532319ad1879eba8e181baf7c7f5c30a9fc5a5179c980cbe3c16919926222f` |
| `result_R4_gate.json` | 1878 | `bdb157641a3f4e45b2ab82506028773cac1cf75de0915602f38edb4f0f75345d` |
| 判据 `OWNER_DECISIONS.md` | — | `§三十九` L908–L935 逐字取自原文（R1–R8 全批，含 R3 `paused` 更正、R4 硬前置、R5 全路径、R6 先备份、R7 执行=父会话、R8 测量器绑定、纪律边界「不放行参数/三仓 git 零写/交 I-17-A」） |

---

## 9. 没做的事（明确边界）

1. **不写卡状态**：`handoff.status` 维持 `review_pending`；本报告不产生 `accepted/changes_required` 落定，落定走父直写。
2. **未跑 `git status`**、**零 git 写**、**零联网**（复用探测为本地查询，跑后 mtime 复核零写）；未改任何被审件/判据件/产品仓文件（收尾复哈希 17 件见 §8）。
3. **R4 复跑输出未落被审目录**（写 `%TEMP%`），以守住「写入面 = 2 新文件」；如需入档请父工位另行落盘。
4. **未复跑 `_recovery_drill.py` / `_bind_combo.py` / `_probe_newprocess.py`**（会写 `drill_restore*` / 绑定件，与写入面冲突）⇒ R5 改为**产物树 + manifest 的只读等价复核**（§3，逐文件 sha）。
5. **未复跑入口 shim ×4 `--help` 与 `dayu-cli sessions`**（会写 `__pycache__`/触碰 `~/.edgar`），按被审记录采信。
6. 未执行 `I-14` 测量器测量、未代 `I-14-E` 出结论、未派 `I-17-A`、未放行任何参数、未解 `TESTSIDE`、未宣布持续服务通过。
7. 未解 skill 安装副本 Junction ACL、未复核 CN 侧线上数据可得性（禁网）。
