# B 阶段文件范围（file-scope v0.1.1）—— 待 owner 批准的 DEV 工作包附件

> 依据 handbook **§1 第 5 项**（"首次实施前用户须批准 DEV 精确工作包及文件范围"）与 **§3**（run 目录结构 / card 字段）；B.DR-18 指出 v0.1 把两处误写为"§2.5"，已改。
> 本页给出 **B 阶段候选改动文件的精确定位 + 冻结哈希**（实测 2026-09-12，wiki 产品树 = A01 冻结的 `7d4852f`，`git diff 7d4852f 032da52 -- src config` 为空，B.DR 已复核）。
> **本页只是提案**：owner 批准前**没有任何文件会被修改**。

## 1. 允许修改（proposed allowed_files）

| # | 绝对路径 | 符号 / 区域（实测） | sha256(16) | 步骤 | 改动性质 | 是否 A01 冻结项 |
|---|---|---|---|---|---|---|
| F1 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/service.py` | `_annotate_locations` `:621-663`；locations 取值 SQL `:329`/`:527`/`:772` | `6412b19e8e9a3073` | B02/B04 | 候选集合与排序分离 + 完整候选清单 | ✅ 是 |
| F2 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/resolver.py` | **`_handle` `:1142-1224`（`:1153-1165` 二次 canonical 过滤、`:1166 is_file()` —— v0.1.1 补，B-DR-04）**；复用判定 `:782-786`/`:933-940`；canonical 过滤 `:912-921`；rationale `:528-533`；`SourceRequest` `:144-161` | `6962b258ce198f19` | B02/B04/B07 | 资格≠排序；`false` 生效（与 F9 收敛）；切换逻辑在合格清单上 | ✅ 是 |
| F3 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/scanner.py` | metadata 合并 `:1007-1081`（开关 `:1038`；**整条 UPDATE `:1078-1081`**）；root 选择 `_select_roots:753`；candidate admission `:872`/`:993` | `c2ada3e26a53b535` | B05 | provenance + 冲突保留；priority 退出真伪判定（**覆盖表全部列**） | ✅ 是 |
| F4 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/reader.py` | `CatalogReader` `:47`；`ReadOnlyCatalogReader` `:144`；`mode=ro`+`query_only` `:16`/`:181` | `ad8cb9147d4f2f51` | B03/B07 | 稳定字节底座（只读，不新增写路径） | ❌ **新增**（A01 未冻结此文件——v0.1.1 更正，B-DR-09） |
| F5 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/models.py` | `RootSpec` `:86-109`；`ROOT_KINDS` `:39`；`CATALOG_SCHEMA_VERSION` `:11` | `fc6cc009fb22f6d6` | B01/B07 | 字段 owner 与合同版本（schema 变更须单列迁移） | ✅ 是 |
| F6 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/config.py` | 字段准入 `:70-118`；未知字段拒绝 `:82-84`；`read_only` 默认 `:106`；`privacy_class` 默认 `:144` | `e96cea75cb27bcf6` | B01 | 唯一准入；`privacy_class` 缺省语义（owner R-4） | ✅ 是 |
| F7 | `C:/Users/郑曾波/Projects/company-wiki/config/source_catalog.yaml` | 四 root 声明（1712 B） | `f9eb72a6c37c2dfe` | B01（**仅在裁定后**） | 仅在需要显式声明时改；**改动即 A01 冻结哈希失效**，须重跑 A01 §0 | ✅ 是 |
| F8 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/policy.py` | `_effective_reusable` `:67-72`（**在产第二实现**）；`export_policy` 哈希 `:56-64`；文件共 **86 行**（v0.1.1 更正，B-DR-10：v0.1 误把 3384 B 当行号） | `78320c429e4b7bc9` | B01/B07 | R-2 收敛点之一；**其输出是跨仓 policy_hash，改动须同步迁移** | ✅ 是 |
| F9 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/llm_summarizer.py` | 白名单 `:333-341`；发送 `:443-449`；常量 `:45` | 见文件哈希 | B01（只读范围声明） | **只登记不改**（属 owner R-4 整改范围，不在 B 实施面） | ❌ 新增 |

> **F9 说明**：`llm_summarizer.py` 与 `legacy_research_ingest.py` 属 **owner R-4 的整改范围**，但那属"外发门"工作，**不属于 B 的读取面**；v0.1.1 把它们**列入 forbidden**（见 §2），避免 B 顺手改安全门。

## 2. 明确禁止（prohibited，除非另行单独批准）

| 禁止项 | 原因 |
|---|---|
| **`policy_2x.py` 的 `export_policy_2x` 路径**（`cli.py:835-857 _policy_export_payload` 及其调用点 `:811`/`:831`/`:1182`） | **在产**且是 filing-fetch FC-501 containment / ZR-405 policy_hash 的**唯一来源**（`filing_contracts.py:450/461-497`）。**v0.1.1 更正（B-DR-01/A-AR-05/A-VR-05 共同 P0）**：v0.1 把它列为"可停用"是**事实错误**；B 的任何改动都必须**保持该 payload 字节/hash 不变** |
| `policy_2x.py` / `policy_3x.py` 的 **loader**（`load_root_policy_2x`/`load_root_policy_3x`） | owner R-3 范围（准入收敛）；**先停用、不就地改**（改它=维护第二套准入）。注意：仅限 loader，不含上面的 export |
| `llm_summarizer.py`、`legacy_research_ingest.py` | owner R-4 的外发门整改范围，**不属于 B**（避免 B 顺手改安全门） |
| `adapters/*`、`adapter_dispatch.py`、`adapter_process.py`、`dayu_cli_adapter.py` | provider 获取面（N/X），非读取面 |
| `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/{store.py, canonical_writer.py, normalizer.py, duplicate_cleanup.py}` | 写/加工面；**B05 的持久化若需要它们，则本步升级为独立工作包**（B-DR-12） |
| `company-wiki/.source_catalog/**`（catalog.sqlite3、-wal、-shm、legacy_periods.json） | 生产状态；行为验证一律用隔离副本 |
| `company-wiki/config/source_catalog_worker.yaml`、worker 控制/启动/任务相关文件 | D.SAFE 范围 |
| `company-wiki/scripts/legacy_observer.py` 及任何写 `legacy_periods.json` 的路径 | FC-705 门与 R9 的权威账本 |
| `company-wiki/artifacts/**`、`raw/**`、`companies/**` | 原始数据与受控证据，只读 |
| `filing-fetch/**`、`revenue-forecast/**`（本 run 目录除外） | B 主责任在 wiki；消费者瘦身属 C（B07 的消费者侧实现见 [b-design.md](b-design.md) §B07 的范围表） |
| 任何 `*.ps1` 自启动脚本、计划任务、`install-startup` 路径 | S 类系统动作 |
| prune / duplicate-recycle / archive-retired-evidence 相关路径 | 删除类（D + H01） |

## 3. owner R-6 的 9 处同型排序：**分类（v0.1.1 补，B-DR-13）**

| 位置 | 处置 |
|---|---|
| `service.py:329`/`:527`/`:643-653`/`:772`、`canonical_writer.py:287` | 前三个在 **F1**（allowed）；`canonical_writer.py:287` 在 **forbidden**（写面）→ R-6 整改须单列工作包 |
| `duplicate_cleanup.py:210`/`:486`、`normalizer.py:1600`/`:1892`、`llm_summarizer.py:371`、`evidence_query.py:269` | 全部 **forbidden**（写/加工/外发/查询只读层）→ 登记为 **C/D 或独立工作包**，B 不改 |

> 结论：**B 只改 `service.py` 与 `resolver.py` 内的排序语义**；其余 6 处是"登记 + 归属”，避免 B 越界。

## 4. 变更规模与回退

- 预计改动集中在 **F1/F2/F3**（候选选择、切换、metadata 合并）+ **F8**（R-2 收敛点之一）；F4–F6 为配套；**F7 默认不改**。
- 回退：每步独立 commit；回退 = revert 单个 commit，**不回滚原始数据与历史来源证据**（handbook §5）。
- **跨仓约束**：任何影响 `export_policy` 输出的改动都会改变 **policy_hash**，必须与 filing-fetch 的 FC-501 期望值同步迁移（`filing_contracts.py:450/461-497`）——**无同步迁移则不得合入**。

## 5. 与阶段 A 冻结哈希的关系（v0.1.1 更正，B-DR-09）

- F1/F2/F3/F5/F6/F7/F8 = **A01 §0 的冻结项**，哈希逐一相符（`6412b19e…`/`6962b258…`/`c2ada3e2…`/`fc6cc009…`/`e96cea75…`/`f9eb72a6…`/`78320c42…`）。
- **F4 `reader.py` 不是 A01 冻结项**（A01 §0 只冻结了 12 个候选定位文件）→ v0.1 写"F1–F8 逐一等于 A01 §0"**不成立**，现按本表逐行标注。
- 一旦 B 开工，A01 §0 的"产品输入哈希"即视为**已消费**，后续阶段必须重跑输入冻结（handbook §2.3）。
