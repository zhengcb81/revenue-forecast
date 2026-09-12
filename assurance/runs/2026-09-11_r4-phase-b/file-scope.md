# B 阶段文件范围（file-scope）—— 待 owner 批准的 DEV 工作包附件

> 依据 handbook §2.5：「首次实施前用户须批准 DEV 精确工作包及文件范围」；card 字段要求 `allowed_files` 绝对解析到获批隔离根，`forbidden_paths` 明确列出。
> 本页给出 **B 阶段候选改动文件的精确定位 + 冻结哈希**（实测于 2026-09-11 23:3x，wiki HEAD `032da52` 的父级产品树 = `7d4852f` 冻结的产品输入，产品代码自 A01 冻结后未变）。
> **本页只是提案**：在 owner 批准前，**没有任何文件会被修改**。

## 1. 允许修改（proposed allowed_files，全部位于 company-wiki 产品源）

| # | 绝对路径 | 符号 / 区域（实测行号） | sha256(16) | 对应步骤 | 改动性质 |
|---|---|---|---|---|---|
| F1 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/service.py` | `_annotate_locations` `:621-663`；locations 取值 SQL `:329`/`:527`/`:772` | `6412b19e8e9a3073` | B02/B04 | 候选集合与排序分离；保留完整候选清单 |
| F2 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/resolver.py` | 复用判定 `:782-786`/`:933-940`；canonical 过滤 `:912-921`；rationale `:528-533` | `6962b258ce198f19` | B02/B04 | 资格与排序分离；`reusable_for_filing:false` 生效（owner R-2） |
| F3 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/scanner.py` | metadata 合并 `:1007-1081`（`:1038` priority 比较）；root 准入 `:872`/`:993`；`_select_roots` `:753` | `c2ada3e26a53b535` | B05 | provenance + 冲突保留，priority 退出"真伪"判定 |
| F4 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/reader.py` | `CatalogReader` `:47`；`ReadOnlyCatalogReader` `:144`；`mode=ro`+`query_only` `:16`/`:181` | `ad8cb9147d4f2f51` | B03/B07 | 稳定字节提供的只读底座（不新增写路径） |
| F5 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/models.py` | `RootSpec` `:86-109`；`ROOT_KINDS` `:39`；`CATALOG_SCHEMA_VERSION` `:11` | `fc6cc009fb22f6d6` | B01/B07 | 字段 owner 收敛与合同版本（如需 schema 变更须单列迁移） |
| F6 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/config.py` | 字段准入 `:70-118`；未知字段拒绝 `:82-84` | `e96cea75cb27bcf6` | B01 | 唯一准入实现（owner R-3）；`privacy_class` 缺省语义（owner R-4） |
| F7 | `C:/Users/郑曾波/Projects/company-wiki/config/source_catalog.yaml` | 四 root 声明（1712 B） | `f9eb72a6c37c2dfe` | B01（**仅在裁定后**） | 只在需要显式声明时改；**任何改动都会使 A01 冻结哈希失效**，须重跑 A01 §0 |
| F8 | `C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/policy.py` | `:1-3384` 导出策略 | `78320c429e4b7bc9` | B06/B07 | 资格标签与读取合同版本（如出口在此） |

**测试文件（同样需要批准，属新增）**：`company-wiki/tests/contract/` 下与 L01–L12 对应的新测例（命名沿用现有 `test_<id>_<slug>.py` 约定）；**仅新增**，不修改既有断言。

## 2. 明确禁止（prohibited，除非另行单独批准）

| 禁止项 | 原因 |
|---|---|
| `company-wiki/src/company_wiki/source_catalog/policy_2x.py`、`policy_3x.py` | owner R-3 判定为"无生产调用者"的那套；**先停用，不就地改**（改它等于维护第二套准入） |
| `company-wiki/.source_catalog/**`（含 catalog.sqlite3、-wal、-shm、legacy_periods.json） | 生产状态；行为验证一律用隔离副本 |
| `company-wiki/config/source_catalog_worker.yaml`、worker 控制/启动/任务相关文件 | 属 D.SAFE 范围，B 不碰 |
| `company-wiki/scripts/legacy_observer.py` 与任何写 `legacy_periods.json` 的路径 | FC-705 门与 R9 的权威账本 |
| `company-wiki/artifacts/**`、`company-wiki/raw/**`、`companies/**` | 原始数据与受控证据；只读，不写不改 |
| `filing-fetch/**`、`revenue-forecast/**`（除本 run 目录） | B 的主责任在 wiki；消费者瘦身属 C |
| 任何 `*.ps1` 自启动脚本、Windows 计划任务、`install-startup` 路径 | S 类系统动作，B 不碰 |
| `prune`/`duplicate-recycle`/`archive-retired-evidence` 相关路径 | 删除类，属 D + H01 |

## 3. 变更规模与回退

- 预计改动集中在 **F1–F3**（候选选择、复用判定、metadata 合并）与 **F8**（合同出口）；F4–F6 为配套；**F7 默认为不改**。
- 回退：B10 要求记录**可回退版本**；设计上每个步骤独立 commit，回退=revert 单个 commit，**不回滚原始数据与历史来源证据**（handbook §5 硬停止）。

## 4. 与阶段 A 冻结哈希的关系

- 上表 F1–F8 的 sha256(16) **与 A01 §0 冻结值逐一相同**（`service.py 6412b19e…`、`resolver.py 6962b258…`、`scanner.py c2ada3e2…`、`config.py e96cea75…`、`models.py fc6cc009…`、`policy.py 78320c42…`、`source_catalog.yaml f9eb72a6…`）——即 B 的改动面**可从 A 的冻结基线精确 diff**。
- 一旦 B 开工，A01 §0 的"产品输入哈希"即视为**已消费**，任何后续阶段都必须重跑输入冻结（handbook §2.3）。
