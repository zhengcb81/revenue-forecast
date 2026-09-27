# I-16-A / a20260926-01 独立复审报告（部署验收工位）

- 复审角色：`reviewer_i16a`（独立复审工位，部署验收者）；A 级全量档
- 复审时刻：2026-09-26 21:41–21:5x UTC（本地 22:41–22:5x，UTC+1）
- 被审：`execution_runs/I-16-A/a20260926-01/` 顶层 **16 件产出**（`oracle.md` · `deployment_proposal.md` · `verification.json` · `handoff.json` · `combo_manifest.json` · `snapshot_manifest.json` · `recovery_drill.json` · `impact_scope.json` · `probe_bind.json` · `gate0_raw.txt` · `_bind_combo.py` · `_build_outputs.py` · `_probe_newprocess.py` · `_recovery_drill.py` · `_run_mutations.py` · `_verify_combo.py`）
- **写入面**：仅本报告 2 文件（`reviewer_report.md` + `reviewer_report.sha256`）；被审与上游只读；产品三仓只读（未跑 `git status`、零 git 写、零联网）；**本报告不写卡状态**（`status` 仍 `review_pending`，落定走父直写）

---

## VERDICT：`ACCEPT`（附 `P2×2` + `P3×5`；无 P1）

> 判级依据：`恢复可证（未触发 blocked）` · `无未授权影响被自行执行` · `OPEN-2 红线未破` · `封盘零字节` · `三仓未被本卡写入` ⇒ 不落入 P1 五项，故为 ACCEPT。
> **资格口径（卡文 L13）**：仅「可进入具体部署窗口」，**尚非已部署**；本卡未执行任何生产变更 —— 不因未部署判 P1。

---

## 0. 回源（只读，sha 复算）

### 0.1 判据权威

| 文件 | 自算 sha256 | 对照 `verification.input_hashes` |
|---|---|---|
| `execution_v2/card_I-16-A.md`（13 行） | `fa2884fa30678085ccb8a4c9f08035817b45a9200de02b6a5ebf3d71852f535c` | ✅ 一致 |
| `execution_v2/common_root_cards.md` | `f8127541c763859761eb6affdd9f3c898766e249205436ff164b73c2621cd260` | ✅ 一致 |
| `execution_v2/START_HERE.md` | `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318` | ✅ 一致 |
| `OWNER_DECISIONS.md` | `c905ea515d4b5da1192e411fbb6b5d4fbb720cb5b9b20485b34fc402bd3e11e9` | ✅ 一致 |

**`OWNER_DECISIONS.md §三十八 裁定一`（L879–L886）逐字回源**：与 `oracle.md §1`、`handoff.authorized_by.verbatim` 逐字比对 **完全一致**（含「授权开工（建议）」、5 条开工判据、`I-08-A` 按清单 `[x]`、`I-14-E` 环境阻断以 `unverified` 登记不作开工阻断、动作 3 fail-closed **不放宽**、动作 4 未授权影响上报维持、5 项不授予）；`§三十七` 关键句（沙箱常设授权 + `commit/push` 仍须 owner 另批）亦逐字一致。

### 0.2 上游 5 卡（仅 sha / 状态，复审自算）

| 卡 | attempt | 自算 handoff sha256 | status | 实现者登记 |
|---|---|---|---|---|
| I-07-D | a20260923-01 | `82bb03aca1756d0cec155d039150e930d7b2a885659ad73d5a94e1c032d09e13` | `accepted_scoped` | ✅ 一致 |
| I-07-E | a20260926-01 | `8cfce3671e29d69eac5d49af114d522d5ba4ae3681b3e70c2f688b45786ecc04` | `accepted_scoped` | ✅ 一致 |
| I-13-A | a20260926-01 | `0b466621ff964c8e3347cc96033bf7abd1f800eaf9eda75c3555209ac60a2f97` | `accepted_scoped` | ✅ 一致 |
| I-13-BC | a20260926-01 | `2dfa7a0918a75c862fdf5b378bb50523cf94ff56a48e3b31353d5f0b724f8dfa` | `accepted_scoped` | ✅ 一致 |
| **I-15-A** | a20260919-01 | **`a93494f266e9a5359283d0acb41894510cdcd602d9720e1c3b4340a098274b29`** | `accepted_scoped` | ⚠ **未登记**（见 P3-1） |

---

## 1. 动作 1 —— 三仓 commit + dirty 内容 hash · 安装副本 · 解释器/依赖 · config/policy/flags/schema · 真实加载模块

### 1.1 三仓源（抽 2 仓 + 全 3 仓自己复算 `commit`/`dirty` digest）

复算算法（自 `_bind_combo.bind_repo` 读出后独立重写）：`git diff HEAD --name-only` 与 `ls-files --others --exclude-standard`（均 `-c core.quotepath=false`，剔 `.planning`）→ 逐文件 sha256 → `state|path|sha256` 按 path 排序 → 整体 sha256。

| 仓 | 自算 HEAD | 自算 diff total / non-planning | 自算 untracked(np) | 自算 dirty 条数 | 自算 digest | 对照 manifest | 结论 |
|---|---|---|---|---|---|---|---|
| **RF**（抽样①） | `b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb` | 3830 / **0** | 48 | 48 | `f41d1a3f0046dd89246fb16447ab85c8e617825406713b23a23d281608bdda8d` | `f41d1a3f…` | ✅ **逐字节一致** |
| **DAYU**（抽样②） | `2115c86d5a9027bb51cbbc8a4d0175080732e4e6` | 1 / 1 | 1 | 2 | `8d2b7c1da188f3b8799d72af1ca05544cd49937d1d94f19376e5b1a498d748e6` | `8d2b7c1d…` | ✅ **逐字节一致** |
| CW（附带） | `dbe474504a6187e22c37918743d17fe59c85a0a8` | 8 / 8 | **55**（绑定 51） | **63**（绑定 59） | **`13b19d65c3b9fc914882a4cc353226db958b8a0c00340f95c9c72ab77b1ba645`** ≠ `3630bfae…` | ❌ 现红 | 见 **P2-1** |

- 结尾只读计数（`git diff HEAD --name-only`）：RF `3830/non_planning=0`、CW `8/8`、DAYU `1/1` —— 与 `verification.three_repo_sha_consistency.final_recheck` **完全一致**；三仓 HEAD 与绑定值一致。
- **CW 漂移归因**：4 个新增 untracked + 5 个 sha 变化**全部**落在并发工位 `docs/plans/narrative-evidence-pilot-2026-09-26/**`、`scripts/narrative_summary_review_pilot.py`、`tests/unit/test_narrative_summary_review_pilot.py`（mtime 22:32:16 → 22:44:13，其中 22:41/22:44 **发生在本复审进行中**）；RF、DAYU 在 22:00 后 **0 个** dirty 文件被触碰。⇒ 并发外部写入方仍在活动，非本卡所为。
- **git 写归因（只读探明）**：`.git` 元数据 —— RF `index` mtime `2026-09-23 19:51:01`、`HEAD` `2026-09-20 15:23`（**本卡窗口未动**）；CW `refs/heads/fcap` + `index` = `2026-09-26 22:10:38`（门0 之后、绑定之前，与实现者登记的 `HEAD bf0c8b27 → dbe47450` 外部提交吻合）；DAYU `index` 同秒 `22:10:38`。**本卡在 RF 上跑了最多的只读 git 命令而 RF index 未被刷新 ⇒ 本卡的 git 调用不写索引**，CW/DAYU 索引刷新归外部工位。

### 1.2 安装副本（editable 三处同源）

自算：`company_wiki-0.1.0.direct_url.json` `9c21606a…` ✅ == manifest；`__editable__.company_wiki-0.1.0.pth` `29cc4b82…`（46 B，内容 `<CW>\src`）✅ == manifest == M5 `artifact_sha_before`；三处 `direct_url` 均 `dir_info.editable=true`（Miniconda CW/DAYU + DAYU `.venv`），editable 目标 = 源仓路径；finder `MAPPING {'dayu': '<DAYU>\dayu'}`；`top_level` 包名 `dayu`（非 `dayu_agent`）。`J2` 成立。

### 1.3 解释器 / 依赖（新进程外自算）

- `C:\Miniconda\python.exe` → **3.13.9**；`company-wiki 0.1.0` `editable=true`、`dayu-agent 0.1.4` `editable=true`、`PyYAML 6.0.3`、`requests 2.34.2`、`httpx 0.28.1`、`pydantic 2.13.4` —— **全部与冻结 P3 一致**。
- DAYU `.venv\Scripts\python.exe` → **3.14.2**，`dayu-agent 0.1.4`、`requests 2.34.2`、`httpx 0.28.1`、`PyYAML 6.0.3` —— **一致**；双解释器同源 editable（M4 臂亦证 3.14.2 会被判 rc=3）。

### 1.4 config / policy / flags / schema（逐项自算）

`company_wiki.json=2.0` · `filing_fetch.json=1.0` · `source_catalog.yaml=1.0` · `source_catalog_worker.yaml=1.3` · `FORECAST_SCHEMA_VERSION="3.7"` · `OPT_IN_SCHEMA_VERSION="3.8"` · `CONFIDENCE_POLICY_VERSION="1.0"` · `migrations.SCHEMA_VERSION=1` · `SOURCE_CONTRACT_COMPATIBILITY_POLICY_VERSION="1.0.0"` —— **9/9 与 `combo_manifest.config_policy_flags_schema` 一致**。

### 1.5 真实加载模块（新进程 + 抽样自算）

`probe_bind.json` 8 个模块的 `origin` 均落 editable 目标 / `RF\scripts\contracts\constants.py`；复审自算 6 个 origin 文件 sha（`constants.py 278e3e02…`、`confidence_policy.py a2444c1e…`、`company_wiki/__init__.py 39921253…`、`evidence_query.py 15fd3969…`、`dayu/__init__.py 7e3854e8…`、`dayu/cli/__init__.py 31504ff2…`）**全部 == probe 记录值 == manifest 值** ⇒ 加载路径 = 安装副本 = 源仓 = 预期组合，`J3` 成立。

---

## 2. 动作 2 —— 新进程加载路径验证 + 旧加载模块负例

- **正例**：`_probe_newprocess.py` 以独立解释器进程运行（`python -X utf8 -B`），`_live/result_final.json` `rc=0`，`J1..J8` 全 `ok=true`（21:31:21Z）。
- **负例 M1（旧加载模块）复审自算**：隔离 site 内 `evidence_query.py` = **git HEAD blob** `a60a9249257a79d7500b2aa7bc7875cd7f77fa9ecea43126eaddbf1f403f1493`（15,259 B，`git cat-file -p HEAD:…` 直接复算一致）≠ 工作树 `15fd3969…`（17,234 B）；`_mut/M1/probe_output.txt` 显示 `--site` 注入 → 新进程真实加载旧字节 → `verifier_output.txt`：`mode=dir rc=3 violations=['J3_new_process_load_path']`。⇒ **负例证据在案，且确实能发现版本错配**。
- 其余四臂 `result.json` 自读：M2 `rc=3/J5`、M3 `rc=3/J3+J5`（probe 常量=3.6）、M4 `rc=3/J4(+J3,J5)`（probe 解释器 `.venv` 3.14.2）、M5 `rc=3/J2`；G/G2 `rc=0`；`mutation_summary.json`：`all_rc_match=true`、`all_expected_violations_present=true`、`original_artifacts_untouched=true`（before/after 两表自比 **完全相等**）。红臂 5 ≥3，符合冻结 oracle §4b。

---

## 3. 动作 3 —— 上个可恢复组合 / 迁移可逆 / 兼容边界（**核实是否 fail-closed**）

- **盘面复算（R2/R3/R4 sha 与记录一一对应）**：`drill_db/v0_empty.sqlite3` = `drill_db/v0_empty.sqlite3.pre_migrate.bak` = **`c563fb43…`** = 记录 `sha_before`/`sha_after_restore` ✅（迁移后 `5673c251…` 未留存=已从备份还原）；`newer.sqlite3` = `9f641d5d…` = 记录 `sha_before == sha_after`（R3 fail-closed 后字节不变）✅；`drift.sqlite3` = `f3157fff…` = 记录 `sha_before == sha_after`（R4 `SchemaDriftError` 只读）✅。
- **快照层自算**：`snapshot/` **109/109** 文件 sha == `snapshot_manifest.source_sha256 == snapshot_sha256`；对 live 源复算 **102 仍同 / 7 已变（全为 CW 外部漂移）/ 0 丢失**。
- **R1 缺陷（P2-2）**：`drill_snapshot` 的目的地用 `Path(source_path).name`（仅 basename）→ 实际 `drill_restore/**` 只有 **104** 个文件，5 件同名互相覆盖（`RF/__init__.py ×4`、`RF/test_model_extensions_anchor.py ×2`、`CW/README.md ×2`）；`restored=109, mismatch=[]` 按行统计，**不证明目的地完整**。
- **结论**：恢复目标 **C0**（本卡绑定组合）与可逆性**可证**：文件层字节由快照全量校验、DB 层 backup→migrate→restore 字节相等（盘面复算一致）、前向 `UnsupportedSchemaVersionError` 与 `SchemaDriftError` 均 **fail-closed 且文件不变**、registry 前向无守卫的边界风险已如实登记（`R5`：`user_version=9` 静默接受）。**未出现「关闭严格门回滚」**，实现者据此 `recovery_provable=true` 未判 `blocked` —— 复审**核可该判断**（R1 目的地缺陷列为 P2，不构成"恢复证不了"）。
- 生产 catalog 锚点**全量重算**（7.8 s，只读）：`3,055,796,224 B` / `mtime_utc 2026-09-26 17:48:22.684241` / `sha256 63c359aa4b09545a540a05f8d32d66ac3c9dbd4ccf696470d55cb38a31f6dcfc` / `user_version=0` —— **与锚点逐字段一致**（生产库未被改动）。

---

## 4. 动作 4 —— 影响范围 · 写入 / 停重启 / 恢复步骤 · 未授权影响

- `impact_scope.json` 三段齐备（`writes`：本卡已写 3 类 + 部署窗口将写 7 项逐项可逆方式；`stop_restart`：现状只读观测 + 6 步窗口计划 + 「不因工具退出无条件 resume」；`recovery_steps` 7 步含「恢复不可证 ⇒ STOP 判 blocked」）；`J7` 所需 `writes/stop_restart/recovery_steps` 全在。
- `production_change_executed=false`、`unauthorized_impact=false`、`escalation_to_user.triggered=false`。复审**未发现**任何自行执行的未授权影响：无 git 写（RF/DAYU `.git` 索引与 HEAD 在本卡窗口未动）、无联网调用（6 个脚本 grep 无 `urllib/requests/httpx/socket` 网络调用）、未停他人进程、未写 `raw/`/registry 生产数据、未放行参数（store `low/base/high` 仍全 `null`，sha 未变）。**§三十八 动作 4 红线维持**：真正未授权影响才停下上报 —— 本卡未遭遇，故未上报属正确。

---

## 5. 附加核验

| 项 | 结果 |
|---|---|
| **`I-14-E` 环境阻断登记** | `handoff.i14e_env_blocked_registered=true` **属实**；detail 为「`OpenProcess` DENIED ⇒ `TESTSIDE` 三臂不可证 ⇒ `unverified`，不作开工阻断（§三十八 逐字）」；`oracle §5.6/§7`、`proposal §4.2/未满足项`、`verification.open_findings` 一致；**只登记未解除**（无任何「已验证/已解除/代其出结论」表述），`TESTSIDE` 未放行 ✅ |
| **`OPEN-2` 红线** | `124,248.63`（真值 `38,175.95`）在全部产出中仅出现于**红线登记**语境（oracle §5.1、handoff `open2_ban_detail`、proposal 未满足项表），**未作为任何部署输入被消费** ✅ |
| **封盘 `f2178768…`** | `I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` = `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`，**51,697 B，零字节变化** ✅；store `b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff` **61,231 B 零字节变化** ✅ |
| **三仓工作区未被本卡写入** | 结尾 `git diff HEAD --name-only` 只读计数 RF `3830/0`、CW `8/8`、DAYU `1/1` == `final_recheck`；RF/DAYU 22:00 后 0 文件被碰；RF `.git/index` 未刷新 ⇒ 本卡 git 只读；CW 变更全部归并发 `narrative-evidence-pilot` 工位（已由实现者登记 `u-I16A-0`）✅ **归因本卡的产品仓写 = 0** |
| 五份计划文件 | `task_plan/progress/findings/PLANNING_STATUS/IMPLEMENTATION_PLAN.md` mtime 均 `2026-09-20`，本卡窗口未动 ✅ |
| 不自签 / 不放行 / 不派 I-16-B | `status=review_pending`、`implementer_signed=false`、`params_released=false`、`i16b_dispatched=false` ✅ |

### 3 处 spot-check（全部自算）

1. `mod_rf_forecast_constants` → `RF/scripts/contracts/constants.py` = `278e3e02df15e556f4851b46711a2f36aac5b7e6a9820c27e0ca31b02858d0ae` = manifest = probe（**同一次计算三处对照**）✅
2. `inst_cw_pth` → `C:\Miniconda\Lib\site-packages\__editable__.company_wiki-0.1.0.pth` = `29cc4b82addb59ab3aa45a35ba9ae402e9328f1c3a5e9ac7b857542150adae0a`（46 B）= manifest = M5 `artifact_sha_before` ✅
3. `mod_cw_evidence_query` → `CW/src/.../evidence_query.py` = `15fd39696398d7cf05ade62868d13eeffd23cf22dfa7827101b491c584cf298d` = manifest = probe = M1 `current_module_sha256` ✅
   （追加：`mod_cw_migrations 1f6dcb6b…`、`cfg_rf_company_wiki_json 7a65a00e…`、`inst_cw_direct_url 9c21606a…`、`worker_runtime_json adf5de4d…` 亦全 match）

---

## 6. P 清单与 `unverified`

### P2（须在部署窗口前处置）

- **P2-1｜`J1` 复审复跑现红（组合仍在被外部改写）**：CW dirty digest `3630bfae… → 13b19d65…`、untracked 51→55、5 个 sha 变化，且复审期间（22:41:06 / 22:44:13）仍在写入。按实现者 `u-I16A-0`（high）与 owner 规则 —— **「安静时刻复跑 J1，仍红则不得开部署窗口」**：**本次复跑即为红 ⇒ 当前不得开窗**。非本卡过错（实现者已如实登记并留作开窗前置），但**该前置条件目前未达成**，须在并发工位静默后重跑 `J1` 至绿方可开窗。
- **P2-2｜R1 恢复演练目的地命名碰撞**：`drill_restore` 按 basename 落盘 → 109 行仅 104 目的地，5 件同名覆盖；`restored=109, mismatch=[]` 的声明**强于实证范围**。建议：以相对路径补跑一次 R1，或将声明收窄为「快照层字节完整性 + 逐行拷贝字节相等」。

### P3（记录，不阻断）

- **P3-1｜上游 `I-15-A` 未入回源表**：`oracle §3`、`verification.upstream_inputs` 只列 4 份 handoff；复审自算 `I-15-A/a20260919-01 = a93494f2… / accepted_scoped`，与 §三十八「已 accepted」一致，**结论无影响**。
- **P3-2｜哈希台账缺口**：`_build_outputs.py`（20,911 B）与 `handoff.json` 自身未被任何 `written_files` 台账覆盖（其余 16 项 sha/bytes **全部复算一致，mismatches=0**）。
- **P3-3｜handoff 字段不全**：缺 `review_and_handoff.md L37` 要求的 `input_hashes / current_source_hashes / changed_paths / commands_executed / raw_exit_codes / expected_exit_codes / reviewer_status`（信息散落于 `verification.json`、`oracle §4c`、证据路径，**可寻但不合最小字段集**）。
- **P3-4｜parent id 不一致**：`oracle §0` 写 `session-19074bf0-0205-4150-…` 并注「见 handoff.parent_agent_id」，实际 `handoff.parent_agent_id = session-19074bf0-0205-4315-af73-9db57597275a`（冻结件内自指不一致）。
- **P3-5｜`u-I16A-1` 历史运行态不可重建**：2026-08-08 worker 组合 4 模块字节在 git 历史+磁盘均未命中 ⇒ 已正确**禁止**作恢复目标；是否另立补救卡交 owner/编排层。

### `unverified`（保持未解除）

`I14-E-unverified`（`OpenProcess` DENIED → 进程命令行/TESTSIDE 三臂不可证）· `u-I16A-skillcopy`（`~\.claude\skills\revenue-forecast` Junction 目标读/列被拒 ⇒ skill 安装副本 hash 未核，部署窗口必检）· `u-I16A-0`（并发漂移，开窗前置复跑）。

---

## 7. 没做的事（明确边界）

1. **未复跑实现者脚本**（`_verify_combo.py` / `_run_mutations.py` / `_recovery_drill.py` 均会落盘，与「写入面 = 2 新文件」冲突）⇒ 改为**只读自算等价复核**（三仓 commit/digest、模块/安装/配置/依赖/锚点 sha、快照与演练盘面、负例字节）。
2. 未跑 `git status`、零 git 写、零联网、未动产品三仓、未改任何被审/上游文件、未解 skill 副本 ACL、未代 `I-14-E` 出结论、未放行任何参数、未派 `I-16-B`。
3. **未写卡状态**：`status` 保持 `review_pending`，本报告不产生 `accepted`/`blocked` 落定；落定走父直写。
4. 未按 `review_and_handoff.md §5` 追加「实现者未用的变化案例」额外变异（同因写入面限制）；未复核 `I-08/I-09/I-14` 依赖细项（§三十八 已授权免核）。

---

## 8. 收尾复哈希（被审 16 件，写本报告前复算）

| 文件 | sha256 | bytes |
|---|---|---|
| `_bind_combo.py` | `2f7df8ee8e0596afa8a881f22df98231712d10dbb09b4fc6bfd7bb12d239189c` | 19404 |
| `_build_outputs.py` | `919f3c634d5f19bd5c7657ed58862a9fe9cf554b68cc6ecc5d271d9bdd498407` | 20911 |
| `_probe_newprocess.py` | `f55e39b8964ef1edf3723c7c306dd43b7b9e219f2d47b9fbe2891055982e9f2d` | 6966 |
| `_recovery_drill.py` | `5898d162b053ff63b0e8da656ec42e215d40dbf079011dcefa04e77cd61b1efd` | 9526 |
| `_run_mutations.py` | `4bb36d38100f1db2c85d660501147c1875096d35e20b2af03eeb802e65e01950` | 11303 |
| `_verify_combo.py` | `29a2e8ab90c740226a2e7f78f33d282f5d598902abd58e96a531a153d79e9134` | 12976 |
| `combo_manifest.json` | `a2b9147ade7e6f35336816512c1bcb7a11fc4288f1f83d922d156143004b5fe6` | 64824 |
| `deployment_proposal.md` | `f6427b7173f5e63fa56e48090deb24b34339a91587ea49b5f1ec1f7b2dd3686b` | 19037 |
| `gate0_raw.txt` | `546b00e94ba5408e2ec5009d0d8ce0bea3fa3e072767752136c01fee6da8da8c` | 1268 |
| `handoff.json` | `05c45ce7fafcc03558ad91197558418d100c9d27940b2b8e2258cfbe447bc4b4` | 14050 |
| `impact_scope.json` | `e0959fb90afc68b793fa3260bb553a2d1aa029dba0baf4c1b221be05603ac71f` | 6439 |
| `oracle.md` | `435406389855ba60f12ad0b5522e92b1a2cd01577198ab6394bfd21ddc249938` | 18833 |
| `probe_bind.json` | `31f049874d144e5f5823fbaf65357c2f86a05143ccf284d9bb892cc26beefd1b` | 4064 |
| `recovery_drill.json` | `7130a6e09a246abf7c685373d7401a1a57f4592e079e9c6f9c4eca38b30780fd` | 4606 |
| `snapshot_manifest.json` | `dadb1db5195d8878db2123fffb902ac3e2806616d9083b91dd9cacb846fc7dfc` | 54024 |
| `verification.json` | `e8b537d331c62b8ffe9880ae0b04c4c95b92abfbc53b8e50c446709c93a24a13` | 16197 |

⇒ 与 `handoff.written_files` / `verification.written_files` 台账 **逐项一致（mismatches=0）**；台账未覆盖者仅 `_build_outputs.py` 与 `handoff.json` 自身（见 P3-2）。
