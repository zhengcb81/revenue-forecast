# B2 · EXHIBIT 闸门扩到 8-K —— oracle（**冻结版**）

- **card**: `B2-EXHIBIT-GATE-8K` ｜ **attempt**: `a20260926-01` ｜ **role**: `implementer`（实现工位，产出 `changes.diff`，交独立复审）
- **授权（逐字回源）**: `OWNER_DECISIONS.md` **§三十**「**授权扩闸到 8-K（建议）**」——执行映射 1：「把 filing-fetch/dayu 的 exhibit 闸门扩到 `8-K` —— 触及 `sec_downloader.py` 的 `include_exhibits` 分支（L1112/L1124）与 `company-wiki/.../dayu_cli_adapter.py` 的资产复制（现只复制 `primary_document`）」；执行纪律：「本裁定 = 一个授权（改闸门），不是一个结论：**不解除 `BLOCKED-NEEDS-ORIGIN-BYTES`、不解除 `OPEN-3`、不产生 ACCEPT、不判 E1/E2 等级**」「**不授权谎报 `kind`**」「产品改动须走既有流程：iso → `changes.diff` → 独立复审 → 晋升授权，**不得直接写产品仓**」。
- **落点（§三十一 逐字）**: 「**8-K 按诚实 kind `current_report` 落 `company-wiki/companies/{entity}/raw/other/` —— 不改 `canonical_writer` 映射、不谎报 `quarterly_report`**」。
- **边界来源**: `execution_v2/common_filing_cards.md` **L17**「凡跨项目公共 schema、canonical writer、registry 或 worker API，**只有指定 owner 写**；发现 scope 外必要改动先记录阻断并交 owner 补卡，不能为绿灯建立平行框架」⇒ 本卡 `changes.diff` **只允许 2 个文件**；scope 外缺口只记录，不扩文件面。
- **基线证据**: `OPEN3-E1-ORIGIN-BYTES/a20260925-01/mechanism_scan.json`（B2 机制缺口：`L1105/L1112/L1124`、`L389/L474-490/L245-298`、449 个 meta 实测 6-K 23 例 / 8-K 0 例）。

### 冻结记录（修订史）

| 版本 | sha256 | 冻结 UTC | 说明 |
|---|---|---|---|
| v1 | `9467739c7507be037641196355a38b3da040337af55ae9a023db7f7a87bc331c` | 2026-09-25T23:47:30Z | 首次冻结 |
| v2 | `2ff11de822cc73b185c85b6317ace011540c51720e72befb0001bc7178692ac6` | 2026-09-25T23:48:42Z | **iso 代码仍未动**时的修正：`adapter_payload_json` 的 `exhibit_filenames` 由「非授权 form 记 `[]`」改为「**仅在登记到 exhibit 时加键**」——否则 6-K 的 candidate payload 会多一个键，违反 V3 的逐字节不变 |
| v3（现行） | 见 `results/oracle_freeze.json` | 2026-09-26T00:05Z | **事后披露修订（M4 已跑完之后）**：① 修正 M4 的**预期红集合**（见 §2）；② 补判据 ID ↔ harness check 名的**映射表**（见 §1.1）；③ 补列 **M0**（前像撤回）变异行。**未改动任何 R/G/V 判据、未放宽任何要求**；M4 仍然必须红（`A1`），v2→v3 只是把「预测错的那一半」改对 |

> v1→v2 发生在**任何 iso 代码编辑之前**；v2→v3 是唯一一次事后修订，性质 = **披露式勘误**（把一个过宽的变异预测改成实测结果），**不涉及任何红/绿/回归判据**，故不构成「改判据迁就结果」。原始 v2 文本的 M4 行保留在 `mutations/M4_adapter.json` 与 `mutations/M4_adapter.stdout.txt` 中可对照。

#### 1.1 判据 ID ↔ harness check 名映射（v3 补）

| oracle 判据 | harness check 名 | 层 |
|---|---|---|
| G1 | `G1_8k_exhibit_in_filenames` | dayu |
| G2 | `G2_8k_exhibit_absent_without_flag` | dayu |
| G3 | `A1_8k_stages_primary_and_exhibit_only`（+ `A2` 哈希、`A3` receipt） | adapter |
| G4 | `A6_include_exhibits_flag_gates_8k` | adapter |
| G5 | `G5_10k_exhibit_not_ingested`（dayu）+ `A5_10k_result_byte_identical_to_before`（adapter） | 两层 |
| G6 | `A7_landing_current_report_is_other` | 只读直调 |
| V1/V2 | `G3_6k_list_byte_identical` / `G4_6k_expected_names_present` | dayu |
| V3 | `A4_6k_result_byte_identical_to_before` | adapter |
| V4 | `A5_10k_result_byte_identical_to_before` | adapter |


---

## 0. 改动面（先自行打开文件核对行号，父派转述已按实测修正）

### 0.1 `dayu-agent/dayu-agent/dayu/fins/downloaders/sec_downloader.py`（前像 sha256 `543d005c25fabea3431704293e05e79ebfa76de71f031bf6dc6106113e7a5da0`，74,235 B）

| 位置（前像行号） | 现状 | 计划改动 |
|---|---|---|
| L1094 | `include_exhibits: 是否包含 exhibit 文件（6-K）。` | 改为「（6-K、8-K）」——文档串同步 |
| L1105 | `filenames: list[str] = [primary_document]` | **不改**（它是 primary 种子，6-K/8-K 共用；实测确认非闸门行） |
| L1112 | `if include_exhibits and form_type == "6-K":` | `if include_exhibits and form_type in EXHIBIT_GATED_FORM_TYPES:` |
| L1124 | `if include_exhibits and form_type == "6-K":` | 同上 |
| 常量区（L86 后） | 无 | 新增 `EXHIBIT_GATED_FORM_TYPES: frozenset[str] = frozenset({"6-K", "8-K"})` + 注释 |

- 分支体（L1113–L1136：index-header 拉取、`pick_form_document_files`、`pick_exhibit_files`、primary 补链）**逐字不动**；`unique_filenames = sorted(set(filenames))`（L1138）**不动** ⇒ 对 `form_type == "6-K"`，改动前后**执行路径完全等价**。
- `8-K/A` **不在**闸门内（§三十 授权原文 = 「扩到 `8-K`」；`8-K/A` 属 scope 外，记录不扩）。

### 0.2 `company-wiki/src/company_wiki/source_catalog/dayu_cli_adapter.py`（前像 sha256 `bcbbbfd955306c3ed7ca4febff03813ea7dfafeb068c114873bfbfd3456eab5a`，19,775 B）

| 位置（前像行号） | 现状 | 计划改动 |
|---|---|---|
| L389 | `file_entry = self._us_primary_entry(value)` | **不改**（primary 取值逻辑正确）；在其后的 US 路径上**新增** exhibit 资产登记 |
| L474–L490 | `_us_primary_entry` 只取 primary | **不改**；**新增**同级静态方法 `_us_exhibit_entries`（与 dayu `pick_exhibit_files` 同构） |
| L245–L298 `fetch()` | 只复制 primary 一个资产 | 在同一 `try` 内、primary 落盘后**追加复制已登记的 exhibit 资产**（同 sha 校验、同 temp+`os.replace`、同 staging 目录） |
| L150 `__init__` / L300 `close()` | 只有 `_assets` | 新增 `_exhibit_assets` 注册表并在 `close()` 清空 |
| L435–L441 `adapter_payload_json` | `{dayu_document_id, primary_filename, content_sha256}` | **仅当本次登记到 exhibit 资产时**新增 `"exhibit_filenames": [...]`（有序）；**非授权 form / 无 exhibit 时 payload 字节与改动前完全相同（不出现该键）** ⇒ 6-K、10-K 的 candidate/provenance payload 逐字节不变 |

**复制闸门（本卡设计，冻结于此）**：

```
include_exhibits（模块级常量 _INCLUDE_EXHIBITS，默认 True，对应 dayu list_filing_files 的同名参数默认值）
  AND form_type in _US_EXHIBIT_FORMS == {"8-K"}        ← §三十 授权的新 form
  AND meta.files[] 中存在 exhibit 资产（≠ primary_document，.htm/.html，name 含 "dex99"/"ex99" —— 与 dayu pick_exhibit_files 同构）
```

- **为什么不把 `6-K` 放进本适配器的复制闸门**：改动前 `dayu_cli_adapter` 对**任何** form 都只复制 primary ⇒ 把 6-K 放进来会**改变 6-K 的既有行为**，直接违反本卡第一不变量（「6-K 行为必须不变」）与执行映射「6-K 原行为不变」。§三十 授权原文是「**扩到 8-K**」，不是「补 6-K 的复制缺口」。⇒ 变异 **M3** 专门验证：把 6-K 放进新复制逻辑 ⇒ 6-K 回归必须红。若 owner 要 6-K 也复制，属 scope 外新卡（L17）。
- **HK 路径**：exhibit 收集仅在 `market == "US"` 分支触发，HK 行为零变化。

---

## 1. 判据（fail-closed；每条都是可执行断言，harness 见 `harness/`）

### 红（改动前必须实测为红）

| ID | 层 | 断言（改动前 = FAIL） |
|---|---|---|
| **R1** | dayu `G1_8k_exhibit_in_filenames` | `list_filing_files(form_type="8-K", include_exhibits=True)` 的 `filenames` **不含** `d291965dex991.htm`（mechanism_scan B2 的机制事实） |
| **R2** | adapter `A1_8k_stages_primary_and_exhibit_only` | 8-K filing `fetch()` 后 staging 目录文件集合 = `{d291965d8k.htm}`（**只有 primary**） |
| **R3** | adapter `A2_8k_exhibit_bytes_match_meta_sha` | staging 中**没有** sha 与 meta 里 exhibit 条目一致的文件 |

### 绿（改动后必须全绿，rc=0）

| ID | 断言 |
|---|---|
| **G1** | 8-K + `include_exhibits=True` ⇒ filenames **含** `d291965dex991.htm`（且 `source_url = https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm`） |
| **G2** | 8-K + `include_exhibits=False` ⇒ filenames **不含** exhibit（闸门开关真实生效） |
| **G3** | adapter：8-K staging 文件集合 = **恰** `{d291965d8k.htm, d291965dex991.htm}`，exhibit 的 sha256 == meta 条目 sha256；receipt 仍指向 primary 且 `sha(staged)==receipt.content_sha256` |
| **G4** | adapter：`_INCLUDE_EXHIBITS=False` ⇒ 8-K staging 只有 primary |
| **G5** | 非授权 form 不泄漏：dayu 10-K（index 内含 exhibit 文件）filenames **不含** exhibit；adapter 10-K staging **只有** primary |
| **G6** | 落点声明（§三十一，只读直调）：`canonical_writer._destination_subdirectory("current_report") == Path("other")` ⇒ `raw/other/`；`canonical_writer.py` 字节零改动 |

### 回归（6-K 不变量 —— 本卡最重要）

| ID | 断言（**逐字节**） |
|---|---|
| **V1** | dayu `list_filing_files(form_type="6-K", include_exhibits=True/False)` 的 descriptors 全字段 JSON：改动前冻结件（`results/6k_frozen_before.json`）与改动后件 **sha256 相同** |
| **V2** | dayu 6-K 期望文件名清单不变：`{sample-6k.htm, sample-6k_htm.xml, sample-6k.xsd, d123dex991.htm, form6kcover.htm, q12025pressrelease.htm}` |
| **V3** | adapter 6-K filing `fetch()` 的**完整结果对象**（candidates/receipt/staged_files/staged_hashes）：冻结件（`results/adapter_frozen_before.json`）与改动后件 **sha256 相同**（staged 集合仍 = `{tm2412704d1_6k.htm}`） |
| **V4** | adapter 10-K 同法冻结对比 sha256 相同 |

**证明方式**：`freeze` 模式在**改动前**的 iso 上运行并落盘冻结件；`check` 模式在改动后重跑并做 SHA-256 对比（输出在 `results/*.json` 的 `before_sha256/after_sha256` 字段）。

---

## 2. 变异清单（每条：改 iso → 重跑 → 必须红 → 还原）

| ID | 变异 | 必须红的判据 | 反例（会出什么问题） |
|---|---|---|---|
| **M0**（v3 补列） | 把两个 iso 文件**还原为产品前像**（= 完整撤回本卡改动），用**最终版 harness** 重跑 | **G1 红**（dayu rc≠0）+ **G3/A1 红**（adapter rc≠0）；**V1/G3 与 V3/A4 仍绿** | 这就是改动前的原始红：证明绿完全依赖本卡 diff，也补上「harness 在红→绿之间修过两处环境 bug」的对照证据 |
| **M1** | dayu 闸门改回 `EXHIBIT_GATED_FORM_TYPES = {"6-K"}`（= 把 8-K 分支改回去） | **G1 红**；G3/V1 仍绿 | 8-K 的 `d291965dex991.htm` 再次不可达 ⇒ B2 未修 |
| **M2** | 删掉共享 exhibit 分支中的 `filenames.extend(pick_form_document_files(index_header_documents, form_type))`（6-K 走到被改动的共享分支） | **V1/V2 红**（6-K 清单字节变化） | 6-K 丢 `form6kcover.htm` ⇒ 证明 6-K 字节回归断言真的会咬；任何共享分支改动都逃不掉 |
| **M3** | adapter 闸门 `_US_EXHIBIT_FORMS = {"6-K","8-K"}`（让 6-K 也走新复制逻辑） | **V3/A4 红** | 6-K staging 从 `{primary}` 变 `{primary, exhibit}` ⇒ **6-K 行为被改变**，违反第一不变量 |
| **M4** | adapter exhibit 判定**恒真**（任意 files[] 条目都算 exhibit） | **G3/A1 红**（v3 勘误：仅此一条为预期红；原 v2 同时预测 `G5/A5` 红，**实测 A5 不红**——`_US_EXHIBIT_FORMS={"8-K"}` 是**独立的第二道闸**，10-K 在到达 exhibit 判定之前就被挡住，故 10-K 不泄漏） | 反例（v2/v3 一致）：8-K 的 XBRL `d291965d8k_htm.xml` 被当作 exhibit 复制进 staging ⇒ 非 exhibit 资产泄漏 |
| **M5** | adapter `_INCLUDE_EXHIBITS = False` | **G3/A1 红** + G4/A6 红 | 证明 `include_exhibits` 开关真实生效（不是装饰性参数） |

> 变异全部只作用于 iso；每次变异后**还原**再进入下一步（还原后 sha 必须等于改动后 sha，记录在 `mutations/`）。

---

## 3. 执行纪律与行不交界

1. **产品仓只读**：`dayu-agent/`、`company-wiki/`、`revenue-forecast/`（`.planning` 之外）**零写入**；一切代码改动只落 `iso/`。
2. **禁 `git status`**、**禁 git 写**；收尾只跑只读 `git -c core.quotepath=false diff HEAD --name-only`。
3. **禁联网**：dayu harness 对 `_http_get_bytes` / `_http_get_json` 打 kill-switch（抛 `RuntimeError`，由 `_try_*` 兜底为 `[]`），`_http_head` 用本地桩；adapter harness 的 dayu CLI 是本地假脚本。网络请求预期 = **0**。
4. **不执行实际下载**（B1 仍阻断）；不改 `canonical_writer` 映射、不改任何 `kind`、不谎报；不解除 `OPEN-3`/`BLOCKED-NEEDS-ORIGIN-BYTES`；不判等级；不产生 ACCEPT；不代签；不写五份计划文件。
5. **不改的行**：dayu L1105、L1119–L1138 分支体、L1138 排序去重；adapter `_us_primary_entry`、`acquisition.py`、`canonical_writer.py`、`resolver.py`、`source_catalog/__init__.py` 均**逐字节不动**。
6. **交付面**：`changes.diff` **只含 2 个被改文件**；harness/结果/报告全落本 attempt 目录（`.planning` 内）。

---

## 4. 未证实 / scope 外（如实登记，不造绿样）

- **U1**：exhibit 资产被复制到 **staging** 后，`acquisition`/`canonical_writer` 的 **单 receipt** 契约（`import_staged(request, candidate, receipt)` 一次一个文件）**不在本卡 2 文件改动面内** ⇒ **exhibit 最终是否落 `raw/other/` = 未证实**（落点本身按 §三十一 声明并以 `G6` 只读直调验证映射）。
- **U2**：**B1 未解**（本会话 company-wiki 全域不可写、审批禁用、子代理不可提权）⇒ 未执行任何真实 filing-fetch ensure / 下载；真实 SEC 上 `0001193125-26-380280` 的行为 = 未实测。
- **U3**：`8-K/A` 未纳入闸门（授权原文只写 8-K）；`pick_exhibit_files` 同构的 name-pattern 判定意味着**非 ex99 命名的 primary-linked HTML** 不在 adapter 复制面内 —— 与 dayu 侧可下载、adapter 侧未复制的差 = **已知边界**。
- **U4**：company-wiki 自身契约测试（`test_fc1204_complexity_ratchet` ≤46、`test_fc1204_coverage_ratchet` 71、全量 suite）**未在 iso 内运行**：覆盖率测试要求读取产品仓根目录的 `coverage.json`（运行它会**写产品仓**，被纪律 #1 禁止）⇒ **未证实**；替代证据 = 本卡用同一 AST 规则本地复算 `dayu_cli_adapter.py` 的 max-complexity 仍 ≤46（结果见 `results/static_checks.json`）。
- **U5**：dayu 侧改动**未运行**产品仓 `tests/fins/test_sec_pipeline_download*.py` 等 suite（会写产品仓 `.pytest_cache`/workspace）⇒ **未证实**；替代证据 = 本卡自建 harness 覆盖 6-K/8-K/10-K 三形态 + 字节回归。
- **U6**：`handoff.json` `status=review_pending`、`implementer_signed=false` —— **不代签、不产生 ACCEPT**。

---

## 5. iso 可行性判据

- iso 内可完成：import 两个被改模块、跑 8-K/6-K/10-K 全部红绿与变异、跑 6-K 字节回归、跑 `G6` 只读落点调用 ⇒ **iso 可行**。
- 若出现「必须在产品仓原路径才能跑通」的依赖（例如必须读产品仓 `.source_catalog/catalog.db` 才能完成的路径）⇒ 判 **`blocked`** 并写明卡点，**不为跑通而写产品仓**。
