# WC-6-ADAPTER-DISPATCH 独立复审报告（reviewer）

- 卡：WC-6 = REM-95-ADAPTER-DISPATCH（REMEDIATION_REGISTER §75 / §84 E 组 :1709,:1718 / §86 派发 :1739）
- attempt：`execution_runs/WC-6-ADAPTER-DISPATCH/a20260923-01`（handoff.status = `review_pending`，实现者未自签）
- 复审人：独立复审工位（与实现者非同一人）；只写本文件与其旁路钉 `reviewer_report.sha256`，**不改 handoff/decision/oracle/binding/commands/evidence 任何既有字节，不落定卡状态**
- 复审方式：**全部结论来自我自己的重跑 / 复算 / 逐跳实测**；缺证据处写「未证实」；无绿色样例制造
- 复审时间：2026-09-24 21:xx（本地）

---

## 0. 复审执行环境与自证（硬性纪律）

1. **生产树只读**：live company-wiki（`C:\Users\郑曾波\Projects\company-wiki`）与 revenue-forecast 生产树全程只读；唯一读取 live 的写动作是 `shutil.copy2/copytree` 进隔离副本。
2. **写入范围**：本 attempt 目录内仅新增两个文件（`reviewer_report.md` + `reviewer_report.sha256`）。自证：attempt 目录内最新既有文件 mtime = **2026/9/24 06:18:32（handoff.json，实现者）**，复审发生在 21:xx，**无既有字节被改写**。
3. **重跑在隔离副本**：为避免重跑命令写 `evidence/`，我把整个 attempt `robocopy /E` 到 `%TEMP%\wc6rev_a20260923\attempt`（关键文件 sha256 与源一致，见 §1.0），所有 harness 重跑在该副本内执行；探针 cell 在 `%TEMP%\wc6rev_a20260923\temp\wc6\cells\probes`（隔离）。
4. **git 自证**：`git diff HEAD --name-only -- . ":(exclude).planning"` → **输出为空，count = 0**（rc=0）；即**非 `.planning` 改动数 = 0**。复审全程未执行 add/commit/checkout/stash/restore/reset，未联网。
5. **环境偏差披露（重要）**：本会话文件沙箱下，pytest 以 `mode=0o700` 创建的目录**立即对创建者自身不可访问**（实测：`Path.mkdir(mode=0o700)` 成功 → `os.listdir()` 即 `PermissionError [WinError 5]`；默认 mode 则正常）。因此家族（family）重跑**前两次失败**（`fam_rerun`、`fam_rerun2`：338/474 ERROR at setup，全部 `PermissionError: ...pytest-of-郑曾波`），我在 scratch 加了一个仅作用于 `pytest-of-*` 路径的 `sitecustomize.py` mkdir-mode 垫片（PYTHONPATH 注入，**不改产品、不改测试树**）后才得以完成家族重跑，见 §1.5。该偏差双向对称（我的 pre/post 两侧同一环境），故不破坏「前==后」这一卡契约的可比性。

---

## 1. 步骤一：逐条复验（我自己重跑，原始 rc 逐项记录）

### 1.0 字节复核（先于任何重跑）

| 对象 | 我实测 sha256 / 字节 | 与 binding/handoff 期望 | 结果 |
|---|---|---|---|
| `changes.diff` | `ad88feed773a312ecfa3229144fbdad397e5055d490956fdff16c18e277eb44f` / 2604 B | 同 | ✅ |
| changes.diff 行统计 | +18 / −1、2 文件、3 hunk（`+` 18 行、`-` 1 行、`+++` 2 行） | +18/−1、2 files | ✅ |
| `oracle.md` | `f59aa27dc880cbb7b4adce62ca50f85421fbc38d367c60495997118e0cdfccc4` / 13183 B | 同（冻结后未改） | ✅ |
| iso 修复件 `adapter_dispatch.py`（`iso/cw/src` 与 `iso/fixed/` 各一份） | `0c5ac1a2c2a4bd53dc10f954bd4d429b2d5511dcc8610b3b901ea11c10754769` | 同 | ✅ |
| iso 修复件 `scanner.py`（两处） | `85d96757b627a45e3487197d164eb611a19aa54bcfbfc4eb62ad223bd02a47a9` | 同 | ✅ |
| live pre-image（我现场哈希 live CW） | `adapter_dispatch=6a72e7c5…bdbe`（3799 B）、`scanner=f039d5f8…45e`（88112 B） | 同，且**至今未变**（生产仍未修） | ✅ |
| `inputs/probe_fixture.json` | `1836b8b7ef26e1cb82caf5977d0b9b7a55a80d086412658a7017e0e9f206ec9c` | 同 | ✅ |
| harness 10 个脚本（binding `harness` 最终值） | compare_family `de8c6179…`、compare_runs `61097837…`、make_changes_diff `89141e5d…`、pin_sources `00b4cd3c…`、prepare `6496abd4…`、reason_chain `ab95253c…`、run_family `ba44edbc…`、run_stage `69b81b31…`、select_family `5a8c821d…`、wc6_common `2ddabd45…` | **10/10 逐个相等** | ✅ |
| I-07-C 载体 5 件 | decision `0fc21ff0…`、review `c5021799…`、reviewer_report `d5e3e661…`、oracle `b051135a…`、handoff `550b489d…` | 5/5 相等（他卡冻结件未被本卡触碰） | ✅ |
| `REMEDIATION_REGISTER.md` | 现值 `33c7505e88322ddadc173901ebb124b995ad505547e6109fecfbefe2cdb80fee` / 270337 B | binding 钉 `f8cd3ac4…` / 223551 B | ⚠ 不等，见 §5 边界（登记册被计划层后续追加：§1502/§1709/§1718/§1739 行号与 REM-95 文本逐行未变，仅其后新增小节；**非本卡改动，亦无法再复现钉时字节**） |
| attempt 根文件集合 | 恰 `binding.json, changes.diff, commands.json, decision.md, handoff.json, oracle.md` | decision §7 item6 声明的「无游离副本」 | ✅ |

### 1.2 四臂 + compare + repeat + mutation + 幂等双臂 + CFG-01（我重跑，原始 rc）

以下 rc 均为我本次执行的原始返回码；`harness rc` 遵 commands.json 图例，`product rc` 原样记录。

| # | 我执行的命令（scratch 副本内） | harness rc | 关键实测 |
|---|---|---|---|
| R1 | `pin_sources.py after` | **0** | `live_file_count=503`、`manifest_sha256=41c2271dbaf26bcf2f564d48eb0705e467bbf7b2dc05f85f914fdcced047d739`、`live_key_sources_drifted_vs_before=[]`、`iso_equals_live=false`（mismatched 恰为两个修复文件） |
| R2 | `prepare.py green_r` | **0** | `tree_sha256=37be0c5a607cf7c4619b6381bb2eae808966e8152f875c56e9024f7ad615ad58`、probes=7 |
| R3 | `run_stage.py green_r {scan,rescan,resolve,cfg01}` | **0×4** | product rc = **0 / 0 / 0 / 1**；耗时 0.97–1.40s |
| R4 | `reason_chain.py chain_r`（在 green cell 上） | **0** | `all_hops_match=true`，4 探针 × 4 跳全等 oracle §1.1 字面（见 §3 逐跳表） |
| R5 | `prepare.py repeat_r` + 4 阶段 | **0×5** | product rc 0/0/0/1；tree_sha 同 `37be0c5a…` |
| R6 | `compare_runs.py green_r repeat_r` | **0** | `outcome_bytes_identical_overall=true`、四阶段 `diagnostic_changed_paths=[]`、fixture 同 |
| R7 | 突变注入：字节级替换 `error=item.evidence.get("remediation"),` → `error=None,  # MUTATION …`，**occurrences=1**，sha `0c5ac1a2… → ec8d22be48c45b0c5db48615bb883b2a9675951f161ac8e89db5646a6b4294bb` | — | 突变确实落盘（我自己施加） |
| R8 | `prepare.py mut_r` + 4 阶段 | **0×5** | product rc 0/0/0/1；**`locations.error` = NULL ×4** |
| R9 | `compare_runs.py green_r mut_r` | **0** | overall=true；四阶段 changed 恰 = 3 探针；green 诊断=3 串+clean NULL，mut 诊断=全 NULL → **非空转** |
| R10 | 恢复 `iso/fixed/adapter_dispatch.py` → sha 回 `0c5ac1a2…` | — | ✅ 恢复字节等同 |
| R11 | 装入 live pre-image（两文件）→ `6a72e7c5…` / `f039d5f8…` | — | 与 step-2 pin 逐字节相同（RED 臂代码态为真 pre-fix） |
| R12 | `prepare.py red_r` + 4 阶段 | **0×5** | product rc 0/0/0/1；**`locations.error` = NULL ×4**（缺陷复现，非继承） |
| R13 | `compare_runs.py red_r green_r` | **0** | overall=true、fixture 同；四阶段 changed 恰 = `broken_sidecar_probe.txt / mismatch_probe.txt / no_sidecar_probe.txt`；cfg01 product rc **1** 两侧同；stderr 字节同 |
| R14 | 恢复两修复文件 → `0c5ac1a2…` / `85d96757…` | — | ✅ |
| R15 | `compare_runs.py green_r mut_r` 幂等段 + `red_r` 幂等段 | （含于 R9/R13） | 双臂 `diagnostic_identical_across_rescan=true`、`error_counters_unchanged=true`，首/二扫 `errors=0, new_errors=0, error_details=[]`（`known_quarantined` 见 P2-1） |

**产品 rc 汇总（我的重跑）**：`scan=0`、`rescan=0`、`resolve=0`、`cfg01=1` —— 四臂（red/green/mut/repeat）全同；CFG-01 拒绝行（stderr 内）：

```
company_wiki.source_catalog.config.CatalogConfigError: roots[0] adapter_id 'unknown_layout_v9' not registered (CFG-01)
```

**CFG-01 quote-preserve 的字节实测**：
- 既有证据侧：`evidence/red_prefix/cfg01/stderr.txt` 与 `evidence/green/cfg01/stderr.txt` **sha 同 = `9ac24cebe8fa2d264d803ba2ae579b2135f0a663f4ee89061bdaf098814992cc`（均 1191 B）** ✅（登记册「stderr sha 同 rc1」成立）
- 我的重跑侧：red_r / green_r / mut_r / repeat_r 四份 stderr **sha 同 = `bef4ca3829b32d2aa8d7fd7d6681e8d39b102e5e4d83e744d2aaa599956b2d40`（均 981 B）**，且 CFG-01 拒绝行与既有证据 **逐字符相同**（整文件 sha 不同仅因 traceback 内嵌的绝对路径不同：scratch 路径比 `.planning` 路径短 210 字节）。

**我的诊断值 vs 既有证据交叉核对**：`green_r/scan/normalized.json > diagnostic` 与既有 `green/scan/normalized.json > diagnostic` **逐字节相等**；`red_r` 与 `red_prefix` 同 **相等**（即我复现出的 RED/GREEN 诊断与实现者所报完全一致）。

**我复算的结论**：登记册「一一五」的四阶段 compare rc0 overall=true、唯 3 诊断格变、repeat 确定性同、mutation NULL×4 非空转、幂等双臂 report 同（errors0/new_errors0）、CFG-01 rc1+stderr 同 —— **逐条在我的重跑中原样复现**。

### 1.3 既有 compare/chain/family 证据的字节核验（我解析原文件）

- `compare_red_prefix_vs_green.json`：overall=true，stages=[scan,rescan,resolve,cfg01]，每阶段 outcome/rc/stdout(去 volatile)/stderr 全等，changed 恰 3 路径。
- `compare_green_vs_mutation.json`：overall=true，changed 恰 3 路径（突变侧回 NULL）。
- `compare_green_vs_repeat_postfix.json`：overall=true，changed=[]。
- `reason_chain.json`：all_hops_match=true，fix_files = `0c5ac1a2…`/`85d96757…`。
- `compare_family_fam_before_vs_fam_after.json`：474=474、443P/8S/23F 两侧同、`status_changed=[]`、`only_in_a/b=[]`、raw rc 1/1。
- `source_pins_before.json`：503/503、`iso_equals_live=true`（修前 iso==live）、manifest `41c2271d…`；`source_pins_after.json`：manifest 同、drift=[]。
- `changes_diff_manifest.json`：`ok=true`、`changed_files` 恰 2、`unexpected_changes=[]`、`missing_in_iso=[]`、`iso_only_files=[]`。
- `complexity_before_after.json`：`frozen_max` 4/140、`live_max` 4/140、`iso_after_max` 4/140 —— 但 **`iso_after_per` 两处皆 `{}`**（见 P3-1）。

### 1.4 独立复算（不依赖其 harness）

**(a) 逐函数 McCabe 复杂度**（我按 `test_fc1204_complexity_ratchet._mccabe` 同式自算，live vs iso-fixed）：

| 文件 | live max | iso max | 函数数 | 逐函数差异 |
|---|---|---|---|---|
| `adapter_dispatch.py` | **4**（adapter_for 4 / `_to_scanner_candidate` 3 / scan_root_via_adapter 3） | **4**（同值） | 3 vs 3 | **无差异** |
| `scanner.py` | **140** | **140** | 35 vs 35 | **无差异** |

⇒ 登记册「棘轮 4==frozen4 / 140==frozen140 逐函数同」**我独立复算成立**（注意：卡自己的 `complexity_before_after.json` 并未承载 iso 侧逐函数值，见 P3-1）。

**(b) 扫描报告全键审计（关键，见 P2-1）**：我从四臂 `catalog_dump.json > scan_runs.report_json` 取原始报告并跑卡自己的 `strip_volatile`：

- 报告键全集 = `dry_run, error_details, errors, files_excluded, files_hashed, files_reused, files_seen, known_quarantined, locations_active, locations_missing, new_errors, policy_excluded, run_id, strategy`
- **被 `strip_volatile` 静默剔除的键 = `['known_quarantined', 'run_id']`**（`known_quarantined` 含子串 `now`，命中 `VOLATILE_MARKERS` 的 `"now"`）
- 我的独立比对（原始报告剔除纯时间/id 键后整体 canonical 比较）：**red_prefix / green / mutation / repeat_postfix 四臂首扫报告全等**；四臂 `known_quarantined` 皆 **0**；`errors=0,new_errors=0,error_details=[]` 皆同。
- 其余 outcome 键（counts 表名、roots/locations/sources/documents allowlist、`errors/new_errors/error_details/strategy/...`）经我逐一过筛，**无一命中 volatile 标记** ⇒ 唯一未声明的剔除就是 `known_quarantined`。

### 1.5 家族（60 文件）重跑 —— 我复现了「前==后」本体

| 轮次 | 代码态 | pytest 原始 rc | 结果 | 说明 |
|---|---|---|---|---|
| `fam_rerun`（attempt 1） | 修复态 | — | **118P/338E/12F/6S，作废** | 沙箱致 tmp_path 全线 PermissionError（§0.5） |
| `fam_rerun2`（attempt 2） | 修复态 | — | 同上，**作废** | 同上 |
| `fam_rerun3`（加 mkdir-mode 垫片） | 修复态 | **1** | **427P / 39F / 8S，474 outcomes** | harness rc **0** |
| `fam_rerun_pre`（我把 iso 装回 live pre-image，sha 已核 `6a72e7c5…`/`f039d5f8…`） | pre-fix | **1** | **427P / 39F / 8S，474 outcomes** | harness rc **0** |
| `compare_family fam_rerun_pre fam_rerun3` | — | — | **rc 0**：`per_test_outcomes_identical=true`、`status_changed=[]`、`only_in_a=[]`、`only_in_b=[]` | **我独立复现「前==后逐测试全同」** |
| `compare_family fam_before fam_rerun3` / `fam_after fam_rerun3` | 跨会话 | — | **rc 3**：18 条状态不同（17 passed→failed、1 failed→passed） | 跨环境差异，见下 |
| 既有 `compare_family fam_before fam_after`（字节核验） | — | — | rc 0、443/8/23 双侧同、changed=[] | ✅ |

要点：
1. **卡的契约是「同树前==后」，我在自己环境里用同树前后各跑一次并逐测试比对 → 全同（rc 0）**，因此「0 新增 skip/xfail、0 状态漂移」成立：两侧 skipped 都是同样 8 条（`dbx05_symlink_escape_rejected`、coverage ratchet ×2、r9 gate ×4、pdf page-aware），failed 集合也完全相同。
2. **绝对计数跨会话不可复现**（实现者 443P/23F vs 我 427P/39F）：18 条差异全部集中在 `cw_228_backfill`/`fbar_b10r2_normalize_guards`/`close_gap`/`fc906c`/`focus_admission`/`writer_lock`/`zr409` 这类环境敏感测试（我的失败文本：27 个 AssertionError(回填 completed=0)、11 个 PermissionError、3 个 FileNotFoundError、1 个 ModuleNotFoundError），**没有一条落在 adapter_dispatch / `_Candidate` / sidecar / scanner 诊断面**；实现者披露的 23 条既有失败（18=iso 缺 `scripts/`、5=既有）在 recovery/README §7 有原始文本，我按 id 核对：23=8 snapshot_catalog + 9 cold_start + duplicate_cleanup 1 + focus_admission 2 + pipeline 1 + zr409 1 + complexity ratchet 1，与「18 iso-scope（snapshot_catalog 8 + cold_start 9 + control 1）+ 5 其余」的算术自洽。
3. 我两侧的 `test_fc1204_complexity_ratchet::test_complexity_ratchet_frozen_files_do_not_worsen` 都失败于 **`archive_retired_evidence.py max complexity 19 exceeds frozen 7`**（登记册所注 CW-GATE-2 域既有失败），与本卡无关且两侧同；修复涉及的两个文件没有出现在该断言中。
4. 家族文件数：`family_files.json > file_count = 60` ✅；`changes.diff` 触测试文件 = **0**、`skip|xfail` 命中 = **0** ✅。

---

## 2. 步骤二：两非目标裁

### 裁① `documents.metadata_json.acquisition` 缺 `remediation` 键 —— **不属本卡（WC-6/REM-95）范围**

**我自己的实测**：在 RED 臂与 GREEN 臂的 `documents` outcome 中，`mismatch_probe` 的 `acquisition` 对象含 30+ 字段但**无 `remediation` 键**；`no_sidecar`/`broken_sidecar` 两文档 `acquisition = null`；红绿两侧 `documents.metadata_json` **字节相同**（即本卡确实完全没动文档元数据）。

**判为非目标的理由**：
1. **权威规格文本只写列**：REMEDIATION_REGISTER :1718「**WC-6｜REM-95：补救原因持久化至 `locations.error`**」；:1709 REM-95 定义「adapter_dispatch 丢补救原因→locations.error=NULL」。两处均未把 `documents.metadata_json` 列入修法。
2. **卡内冻结契约禁止它**：oracle §3 G-2 冻结「整个 dump 唯一允许的字节变化是 P2/P3/P4 的 `locations.error`」；若把 remediation 写进 `acquisition`，`documents.metadata_json`（outcome allowlist 字段）必然变化 ⇒ 与本卡自己的 RED/GREEN 字节证**自相矛盾**，只能另卡。
3. **修改面显著更宽**：`group_metadata → collector_name/version/retrieved_at + manifest + documents.metadata_json`（scanner.py:699-708 路径）是载荷/身份面改动；且 `no_sidecar`/`broken_sidecar` 两文档的 `acquisition` 整体为 `null`，要加 `remediation` 就得**凭空造出一个 acquisition 对象**，属 schema/行为变更，远超「诊断列」。
4. **可观测性已达成**：修复后读者经 `service.query() → document.locations[].error` 已能看到原因（我 R4 实测 H4 命中），`acquisition` 键不是达成 REM-95 目标的必要条件。

**反例（何时它才算本卡内）**：若 REM-95 规格原文写成「持久化至 `locations.error` **与** `documents.metadata_json.acquisition`」，或 oracle 冻结时把 documents 面列为允许变化项，则它属本卡——**两者都不成立**。

**结论与必办路由**：属 **C1 观察的第二表面，非 REM-95 规格面**。I-07-C 复审原文（reviewer_report:83）本就把它归为「NOT this card's fix surface → route to the REMEDIATION ledger」。**要求**：登记册在处置 REM-95 时**必须显式记下该未覆盖面**（另立一行或在 REM-95 行加注「C1 第二表面未修，另派」），否则违反 owner 原话「发现的缺陷都要全部修复」（§76）而无账可查。若关闭 REM-95 时未记录 → 该条升级为 **P2**。**本卡本身已如实披露**（decision §9、handoff `open_questions` 第 1 条），不计为本卡缺陷。

### 裁② 四桩披露（post-freeze rescan 臂 / 比较器剔 volatile 清单 / mutation1 宿主败 / 同哈希副本删）+ binding harness 哈希并列重录 —— **基本充分，一处实质缺口（P2-1）**

| 披露 | 我的核验 | 充分性 |
|---|---|---|
| post-freeze 新增 `rescan` 臂 | decision §7 item9 + handoff `disclosures.rescan_arm_added_after_oracle_freeze`（oracle sha 仍 `f59aa27d…`）+ 四臂 `rescan/` 证据文件俱在 + 我重跑复现 | ✅ 充分（但见 P3-3：该臂的命令 id 不在 commands.json 冻结清单里） |
| 比较器剔 volatile 清单 | decision §7 item4 列了实测 volatile 键（scan `run_id`、resolve `retrieved_at`、`observed_at`、`*_at/mtime/…`）+ `wc6_common.VOLATILE_MARKERS` 源码 + oracle §4 声明 | ⚠ **不完整**：清单未包含 `"now"` 子串导致的 `known_quarantined` 剔除 ⇒ **P2-1** |
| mutation1（utf8NoBOM 宿主失败、突变未落盘） | 目录 `evidence/mutation_attempt1_mutation_not_applied/` 存在且各阶段齐全；其 `scan/normalized.json` 诊断与 `green` **逐字节相等**（即「跑的是修复码」这一披露为真） | ✅ 充分（原样保留、未覆盖） |
| 同哈希副本删除记账 | decision §7 item6 记 sha `0c5ac1a2…`、已删；attempt 根现存恰 6 个声明文件、无游离件 | ✅ 一致（被删文件本体不可再验 → 该单点**未证实**，但与根目录现状不矛盾） |
| binding harness 哈希并列重录 | 我逐个比 10/10 相等（§1.0）；binding 注记保留了首冻值 `wc6_common 2513fda2…/prepare a6da5275…/run_stage 7bf5fdc7…/compare_runs f1d362b0…` | ✅ 充分 |
| （附）`no_live_family_run` | handoff `disclosures.no_live_family_run=true` + decision §7 item8 给出理由（他 agent 并发跑 live 套件） | ✅ 披露在，但命令表账不平 → P3-2 |

---

## 3. 步骤三：REM-95 关闭裁（丢弃缝是否真关闭，逐跳实测）

**代码态（我读源码，行号为 iso-fixed 现值）**

| 跳 | 位置 | 我实测 |
|---|---|---|
| H0 承诺 | live `adapters/sidecar.py:5-7` docstring「exact remediation reason」 | 读到 |
| H1 计算 | live `sidecar.py:60` `evidence={"remediation": "missing_sidecar"}`；`:74` `evidence={"remediation": ";".join(problems)} if problems else {}`；词表 `_validate_sidecar :90-119`（`sidecar_parse_failed/:94`、`unknown_schema_version/:96`、`missing_identity:/:99`、`missing:/:102`、`missing_provenance:/:105`、`content_hash_mismatch/:111`、`path_escape:/:118`） | 逐行读到 |
| H1→H2 丢弃缝（本卡修复点） | iso `adapter_dispatch.py:81` `error=item.evidence.get("remediation"),`（在 `_to_scanner_candidate :57-82` 内，仅注释+该表达式，无控制流节点） | 读到；mutation 臂移除后诊断回 NULL ⇒ **该缝即因果来源** |
| H2 载体 | iso `scanner.py:44-61` `_Candidate` 新增 `error: str | None = None`（默认值 ⇒ 既有构造点全兼容）；`_ObservedFile.error`（:74）与之并存 | 读到 |
| H3 持久化 | iso `scanner.py:1096` 全仓唯一 `INSERT INTO locations`；末位元素 `:1125` `item.error if item.error is not None else candidate.error`（观察错误优先，保 `known_error` 等式闸门 `:740-746` `existing["error"] == error` 不被改写） | 读到 + 红绿两侧 `locations.error` 实测 |
| H3′ 计数不受污染 | iso `scanner.py:989-1000`：`if item.error:` 才 `errors+=1 / new_errors+=1 / error_details.append`；`known_error` 只在异常分支 `:738-746` 计算 —— **`candidate.error` 不进入任何计数路径** | 读到 + 报告计数四臂同 |
| H4 读者面 | iso `service.py:653-660` `SELECT … l.error …` → `:683` `_annotate_locations` → `document.locations[].error` | 读到 + R4 实测 H4 |

**运行时逐跳（我的 `reason_chain.py chain_r` 重跑，rc=0，`all_hops_match=true`）**

| 探针 | oracle 期望 | H1 adapter evidence | H2 `_Candidate.error` | H3 `locations.error` | H4 `query().locations[].error` | H4 命中视图 |
|---|---|---|---|---|---|---|
| `clean_probe.txt` | NULL | NULL | NULL | NULL | NULL | default_active_only |
| `no_sidecar_probe.txt` | `missing_sidecar` | 同 | 同 | 同 | 同 | default_active_only |
| `broken_sidecar_probe.txt` | `sidecar_parse_failed` | 同 | 同 | 同 | 同 | explicit_source_status_incomplete |
| `mismatch_probe.txt` | `missing_identity:canonical_entity_id;content_hash_mismatch;path_escape:canonical_path` | 同 | 同 | 同 | 同 | explicit_source_status_incomplete |

**关闭裁**：REM-95 的丢弃缝（`sidecar → evidence → _Candidate.error → locations.error → service.query`）**已确实关闭**，四跳在我自己的执行中逐跳命中 oracle 冻结字面，且 outcome 面逐字节不变（§1.2 R13）。

**但「关闭登记行」的措辞有前置条件**：
1. 依 REMEDIATION_REGISTER 第 4 行纪律「每项修复走九步协议（隔离副本+冻结 oracle+独立复核+**零生产合并**）；生产晋升仍是独立 owner 决定」，本卡已满足卡片级修复与独立复核，**但 live CW 仍为 pre-image（我现场哈希 `6a72e7c5…`/`f039d5f8…` 未变）⇒ 生产缺陷仍在**。
2. 因此我的建议处置：REM-95 = **「已修待晋升（FIXED-verified / 复审通过，pending promotion）」**，**不可**记为生产面 CLOSED；晋升 `changes.diff` 到 live CW 是 owner 独立决定（另卡/另授权）。
3. 关闭文案必须带上裁①的未覆盖面（C1 第二表面）。

---

## 4. 步骤四：幂等证永拒裁 —— `_ObservedFile.error` 方案能否「永久拒绝」

**判断：足以拒绝（针对该方案本身），但「永久」有边界。**

**支持拒绝的三条独立证据（我实测/实读）**
1. **静态路径穷尽**：全仓唯一 `INSERT INTO locations` 在 `scanner.py:1096`；计数只在 `:989-1000`（`item.error` 真值时 `errors+1`、`known_error` 假则 `new_errors+1`、append `error_details`），而 `known_error` **只**在异常分支 `:738-746` 计算 ⇒ 若把补救原因放进 `_ObservedFile.error`，则每次扫描 `errors/new_errors/error_details` 都非零，且成功路径永远 `known_error=False` ⇒ **每次 rescan 都把同一条补救记成 NEW error**（计数永不收敛）。这是代码结构上的必然，不是抽样推断。
2. **正向幂等实证（我重跑）**：本方案下红/绿双臂首扫与二扫 `diagnostic_identical_across_rescan=true`、`errors=0/new_errors=0/error_details=[]` 完全相同，诊断不抖动。
3. **家族旁证**：我两侧 `test_repeated_empty_source_is_a_known_quarantine_and_recovers`、`test_scan_is_idempotent_and_tombstones_missing_locations…`、`test_scan_deduplicates…` 等 quarantine/幂等用例 **pre/post 同为 passed** ⇒ 观察错误的等式闸门与既有隔离语义未被本修复触碰。

**边界（「永久」的适用范围）**
- **被拒的是「把补救原因写进 `_ObservedFile.error`」这一具体方案**，在当前 `scanner.py` 结构下（计数路径与 `known_error` 计算位置不变）。它**不排斥**未来能保持 fail-closed 计数不变的设计（独立诊断列/表；或让 `_observe_file` 在成功路径也做等式读回的 remediation-aware 闸门）——那些必须**重跑本套幂等+fail-closed 组合证**再谈。
- **实证覆盖的缺口**：四臂探针里**没有任何一个带观察错误**（四臂 `errors` 全 0），所以三元表达式「观察错误优先」那一支（`item.error is not None`）**未被本卡探针直接触发**；它只由家族里 quarantine 用例与代码阅读支撑。这是该永拒结论的证据边界，须如实记账。
- 幂等双臂证据本身受 P2-1 影响：`known_quarantined` 未被比较器比较；我用**原始 report_json** 独立补上了这一格（四臂皆 0、原始报告除时间/id 外全等），故结论不依赖被污染的那一格。

**结论**：可以据此外加代码结构论证，**在本卡语境下永久拒绝 `_ObservedFile.error` 方案**；拒绝理由应记为「(i) 计数/闸门结构必然性 + (ii) 本方案幂等双臂实证 + (iii) 家族幂等用例两侧同」，并注明上面两条边界。

---

## 5. 步骤五：边界核验

| 边界 | 我的实测 | 结论 |
|---|---|---|
| live CW 503 件 manifest 前后同（`41c2271d…`） | 既有 before/after 证据均 `41c2271dbaf26bcf2f564d48eb0705e467bbf7b2dc05f85f914fdcced047d739`、`live_key_sources_drifted_vs_before=[]`；**我自己又跑了一次 `pin_sources.py after`（rc 0）得到同一 manifest 与空漂移**（时间点比实现者更晚） | ✅ 零产写 |
| 生产树零写 | `git diff HEAD --name-only -- . ":(exclude).planning"` = **0 行（count=0，rc 0）**；attempt 内既有文件 mtime 全部早于复审时刻 | ✅ |
| 60 文件家族面 0 新增 skip/xfail | `family_files.json file_count=60`；我的前后两侧 skipped 均为同一 8 条 id；`changes.diff` 中 `skip|xfail` 命中 0、测试文件命中 0 | ✅ |
| family「同树前==后」 | `compare_family fam_rerun_pre fam_rerun3` **rc 0、status_changed=[]**（我自跑两侧） | ✅（跨会话绝对计数不可复现，见 §1.5） |
| 既有证据链未被我改动 | attempt 最新 mtime = 06:18:32（handoff）；我只新增 2 个文件 | ✅ |
| 登记册钉哈希 | 现值 `33c7505e…` ≠ binding 钉 `f8cd3ac4…`（270337 vs 223551 B）；REM-95 相关行 :1502/:1709/:1718/:1739 文本与行号未变 | ⚠ 计划层并发追加，**钉时字节不可复现**（环境事实，非本卡改动；本报告对规格的引用以现行行文本为准） |
| 无 git 变更操作 / 无网络 | 仅 `git diff HEAD --name-only`（只读）；未联网 | ✅ |

---

## 6. 发现（P1 / P2 / P3）

**P1：0 条。**

### P2（2 条）

- **P2-1 比较器把 `known_quarantined` 从所有字节比对里静默剔除，oracle §4 明文冻结的不变量实际上没被比较。**
  - 证据：`wc6_common.strip_volatile` 的 `VOLATILE_MARKERS` 含子串 `"now"`，而 `known_quarantined` 含子串 `now`（k-n-**o-w-n**…）⇒ 我实测被剔键 = `['known_quarantined','run_id']`；oracle §4 要求 `errors/new_errors/known_quarantined/error_details` **全部字节相同**，decision §7 item4 的「实测 volatile 键」披露**未列**这一项。
  - 影响：`compare_*.json > idempotency` 中 `known_quarantined` 恒为 `null`（`.get()` 落空），读者会误以为「已比较相等」；登记册「known_error 闸门与计数不变」的**证据链在该键上是空的**。
  - 我的独立补证（说明**结论本身为真**）：四臂原始 `report_json` 中 `known_quarantined=0`，剔除纯时间/id 键后四臂报告全等；计数路径代码读证 `candidate.error` 不进计数（§3 H3′）。
  - 建议（低成本）：`strip_volatile` 改为整键精确匹配/白名单（或对 `scan_runs.report_json` 单独按 oracle §4 键表比对），并在 decision §7 item4/oracle §4 披露里补上 `known_quarantined` 这一格；登记册该句补一句「known_quarantined 由复审以原始 report_json 独立证等」。

- **P2-2（路由性要求，owner=登记册/父代理，非实现者）：REM-95 关闭文案必须同时记下 C1 第二表面未修。**
  - 依据 §2 裁①。若关闭时未记录 → 该未覆盖面将无账可查，违反 owner「发现的缺陷都要全部修复」。本卡已披露，故计为**处置前置条件**而非实现者过失。

### P3（4 条）

- **P3-1 引文与证据不匹配（claim 为真，证据文件缺半边）**：`evidence/complexity_before_after.json` 的 `iso_after_per` 两处皆 `{}`，但 `evidence/README.md`、decision §3、登记册「逐函数同」都以该文件为引文。我的 AST 独立复算证实 claim 成立（§1.4a）⇒ 仅证据完整性问题：应补录 iso 侧逐函数值。
- **P3-2 冻结命令表里有未执行的命令**：`commands.json` 声明 label `fam_live_before (--cwd live)` 与 compare 对 `["fam_before","fam_live_before"]`，但 evidence 中**无任何 live 家族文件**，`handoff.commands_executed` 也未列该条；仅以 `disclosures.no_live_family_run=true` + decision §7 item8（理由：他 agent 并发跑 live 套件）披露。披露在，账不平：应在 commands.json 侧标注 dropped（或在 commands_executed 记 `not_executed`）。
- **P3-3 handoff 里的命令 id 不在冻结清单**：`commands_executed` 含 `CMD-WC6-RESCAN-<label>`（三臂），而 `commands.json.commands[]` 无 RESCAN 条目（该臂系 oracle 冻结后新增，decision §7 item9 已披露）⇒ 归档不一致，建议补一行命令条目或注明其为 scan 的第二次调用。
- **P3-4 计数措辞**：登记册「一一五」写「披露**四桩**（post-freeze rescan 臂、比较器剔 volatile 清单、mutation1 宿主败原样留、同哈希副本删记账、binding harness 哈希并列重录）」——括号内实为**五项**；建议改为「五桩」或拆分。

（非缺陷的环境观察，供父代理知悉：① 登记册哈希自钉后漂移 `f8cd3ac4…→33c7505e…`；② 家族绝对计数跨会话不可复现（沙箱致 18 条环境敏感测试翻转，我的前后两侧对称）；③ 我的家族重跑依赖 scratch `sitecustomize.py` mkdir-mode 垫片，属会话沙箱限制，非产品/测试问题。）

---

## 7. 未能重跑 / 未证实项（诚实清单）

1. **`fam_live_before`（live CW 只读见证跑）——未重跑**：实现者亦未执行（P3-2）；我判断在本会话对 live CW 跑整套家族有让测试写生产树的风险（且沙箱会对 tmp_path 全线报错），故**只做字节核验**：`source_pins_before.json` 证明修前 iso==live（503 件全等），因此 pre-fix 的 iso 家族结果可代表 live 字节面；但「live 树上跑」这一命令本身**未证实**。
2. **mutation 臂实现者原突变文件字节（decision §5 所记 `b9460305…`）——未证实**：突变注入后已按恢复流程覆盖，其字节不可复现；我用自己的突变字节（`ec8d22be…`，occurrences=1）复现了**语义**（诊断回 NULL、outcome 不变）。
3. **「同哈希副本已删」的被删文件本体——未证实**（已删即不可再验）；仅能证实现根目录无游离件。
4. **登记册钉时字节 `f8cd3ac4…` ——不可复现**（登记册被计划层后续追加）；REM-95 规格行文本与行号未变，我按现行文本裁。
5. **绝对家族基线 443P/23F —— 跨会话未复现**（我的环境 427P/39F，18 条环境敏感差异）；**同树前==后等式已复现（rc 0）**，故卡契约成立，绝对计数只在各自会话内有意义。
6. 前两次家族重跑（`fam_rerun`/`fam_rerun2`）**作废**（环境 PermissionError 338/474），已如实记于 §1.5；其输出只存在于 scratch（临时目录），非本 attempt 证据。

---

## 8. 结论

- 逐条数字复验：**全部原样复现**（四臂 rc、compare rc0 overall=true、唯 3 诊断格、repeat 同、mutation NULL×4、幂等双臂 errors0/new_errors0、CFG-01 rc1+stderr 同、503 manifest 前后同、+18/−1 2 文件、棘轮 4/140 逐函数同、60 文件家族同树前==后 rc0）。
- 两非目标：①**非本卡**（含必办路由 P2-2）；②披露充分但 volatile 清单漏 `known_quarantined`（P2-1）。
- REM-95：**丢弃缝确已关闭**（四跳逐跳实测 + 代码路径穷尽），可从 `FIXED-pending-review` 进入 **「复审通过、待晋升（不可记生产 CLOSED）」**。
- 幂等永拒：**可拒绝 `_ObservedFile.error` 方案**（含结构论证 + 双臂实证 + 家族旁证），边界如实记账。
- 边界：生产零写（git 非 `.planning` 改动 = **0**）、家族 0 新 skip/xfail、503 manifest 前后同 —— 全部自证通过。
- 发现：**P1 = 0、P2 = 2、P3 = 4**。

VERDICT: ACCEPT
