# B2-EXHIBIT-GATE-8K · a20260926-01 —— 独立复审报告（reviewer）

VERDICT: ACCEPT

- **卡**：`B2-EXHIBIT-GATE-8K` ｜ **attempt**：`a20260926-01` ｜ **角色**：`reviewer`（独立复审工位，与实现者非同一人）
- **复审对象**：实现者交付的 iso 改动 + `changes.diff`（`status=review_pending`）
- **授权回源**：`OWNER_DECISIONS.md §三十`（「授权扩闸到 8-K（建议）」，执行映射 1 点名 `sec_downloader.py` 的 `include_exhibits` 分支 L1112/L1124 与 `company-wiki/.../dayu_cli_adapter.py` 的资产复制；执行纪律：iso → changes.diff → 独立复审 → 晋升授权、不授权谎报 `kind`）、`§三十一`（落点 `raw/other/`，诚实 kind `current_report`）、`execution_v2/common_filing_cards.md L17`（跨项目公共 schema / canonical writer / registry / worker API 只有指定 owner 写，scope 外只记录不扩面）
- **本报告只写复审结论，不写卡状态**（`handoff.json` / `oracle.md` / `changes.diff` 等一切既有字节零改动）
- **复跑环境**：`%TEMP%\b2rev8k`（harness + iso + 冻结件的隔离副本）；产品仓全程只读；网络 0；未执行 `git status`、未做任何 git 写

---

## 1. 六项独立复核（全部为我本人实测，非转述）

| # | 复核项 | 我的实测 | 卡面声称 | 判定 |
|---|---|---|---|---|
| 1 | **红**：改动前取不到 8-K exhibit | M0（两 iso 文件还原为产品前像 + **最终版 harness**）：**dayu rc=1**，failed=`[G1_8k_exhibit_in_filenames]`（4/5 绿）；**adapter rc=3**，failed=`[A1, A2, A6]`（4/7 绿）。另：pre-change stdout（mtime 夹定 `2026-09-25T23:50:32Z` / `23:55:24Z`）同为 `passed 4/failed 1`、`passed 4/failed 3` | `raw_rc` dayu=1、adapter=3 | ✅ 一致 |
| 2 | **绿** | **dayu 5/5 rc=0**；**adapter 7/7 rc=0**（含 `A7 landing=other`）；**static 8/8 rc=0** | 5/5、7/7、8/8 | ✅ 一致 |
| 3 | **变异 6 条** | M0`[1,3]`→G1 / A1,A2,A6；M1`[1]`→G1；M2`[2]`→G3,G4；M3`[1]`→A4；M4`[1]`→A1；M5`[5]`→A1,A2,A4,A5,A6；**mismatch=0**；每次还原后 sha = `4684933e…`(dayu) / `32ef1165…`(cw)，与改动后 sha **逐字节相同** | 同上，`mismatch=0` | ✅ 逐条命中冻结预期 |
| 4 | **⭐ 6-K 逐字节不变** | dayu 6-K 全字段 JSON **`649d906c3bc03bccd19c51849e78363646f36c7636ce8753173a884086def2bd` = 前 = 后，3318 B**；adapter 6-K 结果对象 **`0c9000a11443dba1a505534d80dfb3f2d8717bcef705734a494d02e89ef41b7c` 前后相同**；10-K **`7507acadb06e691ba923ce1d9acb689d9df122ebff491af5fa009696ca9f3109` 前后相同**；**回归表会咬**：M2→dayu rc=2（G3,G4）、M3→adapter rc=1（A4） | 同一組 sha | ✅ 第一不变量成立 |
| 5 | **changes.diff 判定** | **11379 B / sha256 `731bbeeb77d31eec8c2b57ef8eb65418f403480273b25d4638029ca5da8e803e` / 恰 2 文件**；我用 `git diff --no-index`（产品前像 vs iso 后像）在 %TEMP% **独立重算 → 与交付件字节完全相同**；+6/−3 与 +121/−7；前像 sha `543d005c…`/`bcbbbfd9…`、后像 `4684933e…`/`32ef1165…` 全部对上 | 同 | ✅ |
| 6 | **L1105 自曝判断** | 打开产品文件实测：L1105 = `filenames: list[str] = [primary_document]`，**对所有 form 无条件执行、位于闸门之前** ⇒ 判断**成立**（详见 §2） | 「是 primary 种子不是闸门 ⇒ 未改」 | ✅ 成立 |

### 1.1 第 1 项明细（红）

- 我在 %TEMP% 副本执行 `harness/run_mutations.py` 的 **M0**：把 `iso/` 两个文件替换为**产品仓只读前像**，用最终版 harness 跑 `check`。
  - dayu：`{"mode":"check","passed":4,"failed":1,"failed_names":["G1_8k_exhibit_in_filenames"]}` → **rc=1**
  - adapter：`{"passed":4,"failed":3,"failed_names":["A1_8k_stages_primary_and_exhibit_only","A2_8k_exhibit_bytes_match_meta_sha","A6_include_exhibits_flag_gates_8k"]}` → **rc=3**
- M0 下 **G3（6-K 字节）与 A4/A5 仍绿** ⇒ `results/6k_frozen_before.json`、`adapter_frozen_before.json` 确实是**改动前**行为，冻结件可信。
- 时间线独立佐证（本地时区 `GMT Standard Time`，显示值 −1h = UTC）：
  `6k_frozen_before.json` 23:50:27Z、`dayu_check_red` 23:50:32Z、`adapter_frozen_before` 23:55:13Z、`adapter_check_red` 23:55:24Z（均 = `rc_log.txt` 原值）⇒ 首次 iso 编辑窗口 **23:55:24Z–23:58:51Z**；`oracle.md` 最后写入 00:05:32Z（v3 记 00:06:02Z）；`mutations.json` 00:07:03Z、`static_checks` 00:07:46Z。
- 行为侧旁证：pre-change dayu 输出**只有 6-K** 的「读取主文档补链失败」警告；post-change **多出 8-K primary 补链**警告 ⇒ 闸门确实由关到开（不是断言写死）。
- 机制侧回源 `OPEN3-E1-ORIGIN-BYTES/a20260925-01/mechanism_scan.json`：449 个 meta 实测含 exhibit 者 23 例、全部 `6-K`，`8-K` 0 例；`code_evidence.line_1105/1112/1124` 与产品现行字节一致。

### 1.2 第 2 项明细（绿）与附带的**额外独立测试**

- `dayu_gate_harness.py check` → 5/5；`adapter_copy_harness.py check` → 7/7（`landing_current_report=other`）；`static_checks.py` → 8/8（iso 两棵树各只变 1 文件、产品前像 sha 一致、两文件可编译、`dayu_cli_adapter` 复杂度 **10 ≤ 46**）。
- **超出卡面证据的补充（我在 %TEMP% 复制产品测试树后跑的）**：
  - dayu `tests/fins/test_sec_downloader.py` 对 **iso 改后代码**：**41 passed / 0 failed**（含 `test_list_filing_files_includes_xbrl_and_exhibits`、`..._primary_linked_html_exhibits` 两个逐名单断言）。
  - company-wiki `test_source_catalog_dayu_cli_adapter.py` + `test_dayu_adapter.py` + `test_dayu_adapter_fc602.py` 对 iso 改后代码：**14 passed / 0 failed**。
  - company-wiki `test_fc1204_complexity_ratchet.py` 对 iso 副本（= 产品字节）：**1 failed / 1 passed**，见发现 P3-2。

### 1.3 第 3 项明细（变异，逐条对照冻结预期）

| ID | 我实测 rc | 我实测 failed_names | 冻结预期（oracle §2） | 命中 | 还原 sha 回到改动后 |
|---|---|---|---|---|---|
| M0 | 1 / 3 | G1 ｜ A1,A2,A6 | G1 红 + A1 红，G3/A4 仍绿 | ✅ | ✅ `4684933e…` / `32ef1165…` |
| M1 | 1 | G1 | G1 红，G3 仍绿 | ✅ | ✅ |
| M2 | 2 | G3,G4 | V1/V2 红（6-K 清单字节变化） | ✅ | ✅ |
| M3 | 1 | A4 | V3/A4 红（6-K 行为被改） | ✅ | ✅ |
| M4 | 1 | A1 | **v3**：仅 A1 红（A5 不红） | ✅ | ✅ |
| M5 | 5 | A1,A2,A4,A5,A6 | G3/A1 + G4/A6 红 | ✅（含预测集合；A4/A5 见 P3-1） | ✅ |

`mismatch=0`；我复跑得到的 `mutations.json` 与交付件在 rc / failed_names / restored_sha256 上**完全一致**。

### 1.4 第 4 项明细（6-K 第一不变量）

- dayu 层：`G3_6k_list_byte_identical` 的 `before_sha256 == after_sha256 == 649d906c…`，`before_bytes == after_bytes == 3318`；6-K 名单 True/False 两组与冻结件逐项相同。
- adapter 层：`A4` `0c9000a1…` 前后相同（staged 仍 = `[tm2412704d1_6k.htm]`、`adapter_payload_json` 无 `exhibit_filenames` 键、receipt sha `edddeada…` 相同）；`A5`（10-K）`7507acad…` 前后相同。
- 冻结件本身：`6k_frozen_before.json` 3415 B / `aa79e08f…`、`adapter_frozen_before.json` 2220 B / `782ba66a…`，与 `handoff.deliverables` 一致。
- **咬合性**：M2（删共享分支一行）→ dayu rc=2（G3+G4）；M3（adapter 闸门放宽含 6-K）→ adapter rc=1（A4）⇒ 这张回归表**真的会咬**。

### 1.5 第 5 项明细（changes.diff 内容核）

- 独立重算：`git -c core.quotepath=false diff --no-index --no-color <产品前像> <iso后像>` 两对文件并重写头部 → **11379 B、sha `731bbeeb…`、file_count=2、+6/−3 与 +121/−7**，与交付件**逐字节相同**。
- **删除行全集（我逐行读过）**：dayu 3 行 = 文档串「（6-K）→（6-K、8-K）」+ 两处 `if include_exhibits and form_type == "6-K":`；adapter 7 行 = 旧的 `adapter_payload_json=canonical_json({...})` 字面量块。**没有一行**是测试、断言、`canonical_writer`、`acquisition`、`resolver`、`__init__`、registry 或任何既有判据。
- **`src/` 口径**：diff 中唯一位于 `src/` 前缀下的路径是 `company-wiki/src/company_wiki/source_catalog/dayu_cli_adapter.py`，正是 §三十 执行映射 1 **点名授权**的文件；`tests/` **0 触碰**；`revenue-forecast` 仓非 `.planning` **0 内容写入**（今日 mtime 扫描：dayu `dayu/`+`tests/` = 0，company-wiki `src/`+`tests/` = 0，revenue-forecast 非 `.planning` 仅 `.codegraph/codegraph.db-shm` 这个 SQLite 共享内存段 mtime 变化——gitignored、`codegraph.db` 本体仍为 2026-09-19、无数据写入，非本卡文件）。
- 收尾核对：`git -c core.quotepath=false diff HEAD --name-only` → 总 3834 行，**非 `.planning` = 0**（卡面记录 3827 行，+7 全在 `.planning` 其他文件，非本 attempt）。
- 本 attempt 交付完整性：`handoff.deliverables` **45 项逐项 bytes+sha256 全部一致（mismatch 0）** ⇒ 我复审期间未改动任何既有字节。

---

## 2. 第 6 项：`L1105` 自曝裁定 —— **判断成立**

- **实测**：产品 `dayu-agent/dayu-agent/dayu/fins/downloaders/sec_downloader.py` **L1105 = `filenames: list[str] = [primary_document]`**，在 `if include_xbrl or include_exhibits:`（L1108）与两处 `if include_exhibits and form_type == "6-K":`（L1112/L1124）**之前无条件执行**，对任何 form 都只播种 primary。
- **为什么它是种子不是闸门**：
  1. 它不带任何 `form_type` / `include_exhibits` 条件 ⇒ 改它既不会让 8-K 拿到 exhibit，也不构成排除 exhibit 的条件；
  2. **反证**：我保持 L1105 原样，仅按 diff 开闸，G1 即绿（8-K filenames 含 `d291965dex991.htm`）⇒ L1105 不阻碍 exhibit；
  3. 真正的排除条件是 L1112/L1124 的 `form_type == "6-K"`；且 §三十 **执行映射 1 原文只写**「`include_exhibits` 分支（L1112/L1124）」，L1105 只出现在**提问背景的机制描述**里（`mechanism_scan.json` 的 `line_1105` 同为证据引用，其 `meaning` 是「远端文件清单 = 主文档 + XBRL」）；
  4. 若改 L1105（例如置空种子），primary 会对**所有** form 消失，连 6-K/10-K 都会破坏 —— 与本卡第一不变量冲突。
- **结论**：实现者「父派转述的这一行按实测修正、不改 L1105」的处理**正确**，且**收窄到授权范围**（不扩大改动面）。我据此不记任何发现。

---

## 3. 两处主动披露的性质裁定

### ① `oracle v3` 是「事后披露式勘误」还是「事后改期望」？ —— **裁定：合法的追加式勘误，非事后改期望**

逐条对照先例 `T1-F3-FIX / ERRATUM-1` 的三条理由：

| 先例理由 | 本卡实况 | 结论 |
|---|---|---|
| **(1) 可由冻结输入独立算出** | 我**不看实测结果**、只读冻结后的改动代码即可推导：`_US_EXHIBIT_FORMS = frozenset({"8-K"})` 在调用 `_us_exhibit_assets` 之前就把 10-K 挡住 ⇒ M4 把 exhibit 判定改成恒真时 **10-K 不可能红（A5 绿）**；8-K 会把 XBRL `d291965d8k_htm.xml` 当 exhibit 复制 ⇒ **A1 红**。与 v3 写的「仅 A1 为预期红」**完全吻合** | ✅ 成立 |
| **(2) 冻结体仍是旧值（v2 正文可对照）** | **不成立/不可核验**：v1/v2 只留 `sha256 + frozen_utc`（`results/oracle_freeze.json`、`handoff.oracle.versions`），`oracle.md` 是**覆盖写**，attempt 内与 `git HEAD`（该路径 `exists on disk, but not in HEAD`）均无 v2 正文；实现者所指的「M4 行保留在 `mutations/M4_adapter.*`」保存的是**实测结果**，不是 v2 的**预测文本** | ❌ 缺 |
| **(3) 前缀不变（改动面可界定）** | 仅能凭 v3 自述（v3 增补了 §1.1 映射表与 M0 行，属**加法**），因 v2 正文缺失，**无法字节级验证**「除这三处外未动」 | ⚠️ 仅自述 |

**时序（可独立核）**：v1 `23:47:30Z`、v2 `23:48:42Z` 均**早于**首次 iso 编辑窗口 `23:55:24Z–23:58:51Z`（由 pre-change 两份 stdout 的 mtime 与 `rc_log.txt` 双向夹定），也早于 M4 首跑（M4 属 `00:00–00:07Z` 的变异批次）⇒ **不存在「跑完 M4 才回改 v2」**；v3 `00:06:02Z` 落在 M4 之后、且**文件内自曝为事后修订**（不是偷偷改）。

**实质核（最关键）**：现行 v3 的 **R1–R3 / G1–G6 / V1–V4 一条不少、一条不松**，且我全部独立复跑通过（红真的红、绿真的绿、6-K 逐字节不变、6 条变异命中）；M4 行**仍然要求 M4 必须红（A1）**且实测确实红。即：**没有任何一条判据因这次勘误而迁就结果**。

> **裁定：合法追加式勘误（非事后改期望）。** 但记 **P2-1**：v1/v2 正文未随卡留存，先例理由 (2) 在本卡**不可核验**，只能靠 (1)+(时序)+(实质核) 三条旁证。建议后续所有「冻结」必须同时留 `oracle.v2.md` 之类的版本正文（或把每版正文存进 `results/`），否则先例第三条永远缺角。

### ② `U1` 未证实 —— **裁定：记 P2，不升 P1**

- **我独立确认 U1 属实（只读代码级）**：`canonical_writer.py L136 import_staged(request, candidate, receipt)` 是**单 receipt 契约**，唯一调用方 `acquisition_service.py:159`、`portfolio_promoter.py:221` 各传**一个** receipt；`import_staged` 只按该 receipt 的 `staged_path` 校验/搬移（`_validate_staged`）。⇒ 已复制进 staging 的 **exhibit 没有 receipt 就不会被 canonical 导入**，`exhibit 是否最终落 raw/other/` **确实未证实**。落点映射本身我复核 = `_destination_subdirectory("current_report") -> Path("other")`（`canonical_writer.py L90-101`，该文件**不在 diff 内**）。
- **定级 P2 理由**：端到端业务结果（filing-fetch 最终取回 8-K exhibit 原始字节）**本卡尚未闭环**，读者若只看「闸门已开」容易高估；后续**必须**有第 3 个文件（`acquisition` / `canonical_writer` 侧多 receipt 或二次导入）才能打通。
- **不升 P1 的理由**：① 卡面**如实登记未造绿样**（`oracle §4 U1`、`handoff.unverified U1`、`self_attest §6` 三处一致）；② 修复**必然越出本卡 2 文件面**，按 `common_filing_cards.md L17` **只能 owner 补卡**，让本卡改第 3 个文件反而是**违规**；③ §三十 授权对象是「闸门」本身，diff 与授权严格对齐，**交付物无缺陷**；④ 落点口径（§三十一）已由只读直调验证，不涉谎报 `kind`。
- **附带**：staging 中的 exhibit 目前是**孤儿**（既无 receipt 也不会被 `_remove_staged` 按 receipt 清理），属打通卡要一并处理的细节，随 U1 走 owner 补卡。

---

## 4. 发现分级

| 级别 | 编号 | 发现 | 处置建议 |
|---|---|---|---|
| **P1** | — | **无** | — |
| **P2** | P2-1 | oracle v1/v2 **正文未留存**（只留 sha），先例理由 (2)「冻结体仍是旧值」不可核验 | 后续卡冻结必须留版本正文；本卡不因此回退（实质核已过） |
| **P2** | P2-2 | **U1 端到端未闭环**：exhibit 停在 staging，canonical 单 receipt 契约不在 2 文件面内 | **owner 按 L17 补第 3 个文件的卡**；在 B3/C3 结论里显式标注「闸门已开 ≠ 已落 `raw/other/`」 |
| **P3** | P3-1 | M5 实测多红 A4/A5，根因是 harness 把 `include_exhibits_flag` **记进被比对对象**（`_run_scenario` 字段），6-K/10-K 的 staged/payload/receipt 实际**仍逐字节等于冻结件**；oracle/handoff 未解释这一点 | harness 把该元数据移出 blob，或 oracle M5 行注明「A4/A5 属预期元数据红」 |
| **P3** | P3-2 | 产品 company-wiki `test_fc1204_complexity_ratchet::frozen_files_do_not_worsen` **既有红**：`archive_retired_evidence 19>7`、`observability 27>6`、`prompt_injection 17>15`、`prune_retired_evidence 27>12`（iso 与产品字节逐个相同、B2 未碰这些文件）⇒ U4「不跑真套件」的理由**不只是写权限**，替代证据只对**本卡改动文件**成立 | 属既有状态/他卡范围；请父登记并交对应 owner，B2 不背 |
| **P3** | P3-3 | `_us_exhibit_assets` 在 meta 缺 `sha256` 时回退为「发现时计算源哈希」，此时校验锚点从 meta 退化为磁盘（只能发现 discover→fetch 之间的改动） | 打通卡里可改 fail-closed；本卡不影响任何判据 |

**P1 = 0 ⇒ `VERDICT: ACCEPT`（带 2×P2 + 3×P3）。**

---

## 5. Unverified（我未验证的，如实登记）

1. **U1 承接**：exhibit 是否最终落 `raw/other/` **仍未证实**（我只做了单 receipt 契约的只读代码确认，未跑通导入链）。
2. **真实下载 / B1**：禁网、company-wiki 本会话不可写 ⇒ 未做任何真实 filing-fetch ensure；目标 accession `0001193125-26-380280` 在真实 SEC 上的行为未实测。
3. **company-wiki 全量 suite 与 `test_fc1204_coverage_ratchet`** 未跑（覆盖率测试要读写产品仓根 `coverage.json`，违反只读纪律）。
4. **dayu 其余 suite**（`test_sec_pipeline_download*.py` 等）未跑；我只补跑了 `tests/fins/test_sec_downloader.py`（41 passed）。
5. **oracle v1/v2 正文不可得** ⇒ 其差分面无法字节级复核（见 P2-1）。
6. 我第一次尝试跑 dayu 测试时被环境挡了两次（`conftest` symlink 探针与 pytest `tmp_path` 的 `0o700` 目录在本沙箱不可读，`WinError 5`）——属**环境 shim 问题**，我用 `%TEMP%` 副本 + `mkdtemp/mkdir` mode shim 解决，**未改任何产品代码**；这些失败尝试未被计入上面的通过数。
7. `handoff.git_boundary.diff_total_lines=3827` 与我收尾时的 3834 有 7 行差（全在 `.planning`、非本 attempt 文件），我**未追查**来源。

---

## 6. 我没有做的事（边界声明）

- **没有写本 attempt 任何既有字节**：`oracle.md`（三版记录）、`handoff.json`、`changes.diff`、`regression/`、`mutations/`、`results/`、`self_attest.md`、`iso/`、`harness/` 全部原样（45/45 deliverable sha 复核通过）。写入面 = **仅** `reviewer_report.md` + `reviewer_report.sha256`。
- **没有写产品仓**：`dayu-agent`、`company-wiki`、`revenue-forecast`(非 `.planning`) 今日 mtime 命中 = 0（唯一例外是 gitignored 的 `.codegraph/codegraph.db-shm` SQLite 共享内存段，`codegraph.db` 本体未变、无数据写入）。
- **没有用 `git status`、没有任何 git 写操作**；收尾只跑了只读 `git -c core.quotepath=false diff HEAD --name-only` → 非 `.planning` = 0。
- **没有联网**（harness 对 `_http_get_bytes`/`_http_get_json` 打 kill-switch；我没调用任何 web 工具）。
- **没有改 `kind` 映射 / 没有 `canonical_writer` 改动 / 没有谎报 kind**。
- **没有解除** `OPEN-3` / `BLOCKED-NEEDS-ORIGIN-BYTES` / `B1`；**没有判 E1/E2 等级**；**没有产生 ACCEPT / 没有代签 / 没有写卡状态**；**没有写五份计划文件**。
- **没有把「iso 改动只是 diff、未入库」当缺陷**（本卡形态本就如此），也**没有因为它只是 diff 就放松对 diff 内容的核**（逐行读 + 独立重算 + 独立跑测试）。
- **所有测试、变异、重算都在 `%TEMP%\b2rev8k` 隔离副本完成**；产品仓只读。

---

## 7. 证据索引

- 我的复跑目录：`%TEMP%\b2rev8k`（`harness/`、`iso/`、`results/` 冻结件副本、`mutations/` 复跑产物、`droot/`（dayu 测试副本）、`cwroot/`（company-wiki 测试副本））
- 卡面证据（只读核对）：`results/{dayu_gate_check,adapter_copy_check,static_checks}.json`、`results/rc_log.txt`、`results/oracle_freeze.json`、`results/6k_frozen_before.json`、`results/adapter_frozen_before.json`、`mutations/mutations.json`、`regression/6k_regression.md`、`self_attest.md`、`handoff.json`
- 授权回源：`OWNER_DECISIONS.md §三十/§三十一`、`execution_v2/common_filing_cards.md L17`、`execution_runs/OPEN3-E1-ORIGIN-BYTES/a20260925-01/mechanism_scan.json`
- 产品只读取证：`dayu/.../sec_downloader.py L1094/L1105/L1112/L1124`、`company-wiki/.../dayu_cli_adapter.py`、`canonical_writer.py L90-101/L136`、`acquisition.py L127-133`、`tests/contract/test_fc1204_complexity_ratchet.py`
