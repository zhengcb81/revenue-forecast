# B10 侦察记录（单读取链的**机器导出**基线）

> 状态：**侦察完成，实施未开始**（前序门已开，见 [b10-plan.md](b10-plan.md)）。
> 工具：[evidence/b10_read_chain_inventory.py](../evidence/b10_read_chain_inventory.py) → [evidence/b10-read-chain-inventory.json](../evidence/b10-read-chain-inventory.json)（**只读**，AST 扫描，不改任何代码）。

## 1. 事实：共享列 `documents.metadata_json` 现在有**几条读取链**

| 项 | 数量 | 说明 |
|---|---|---|
| 解析点总数 | **21** | AST 扫 `src/company_wiki/source_catalog/**.py` |
| **单一链调用**（`store.metadata_object`） | **2** | `backfill_v2.py` / `migration_ledger.py` —— 已是链 |
| **确认的直接读取者**（参数里就写着 `metadata_json`） | **10** | 见下表；这是**收敛基线** |
| 启发式候选（只有所在符号提到该列） | 9 | 含重命名取值的真读取者，也含**假阳性** |
| 涉及模块 | 12 | |

**确认的直接读取者（10 个，分布在 9 个模块）**：

| 模块 | 符号 | 行 |
|---|---|---|
| `artifact_backfill.py` | `_classify` | 175 |
| `artifact_read_model.py` | `_artifact_row` | 105 |
| `normalizer.py` | `_frontmatter` / `normalize_catalog` ×2 | 1441 / 1633 / 1684 |
| `resolver.py` | `_metadata_conflict_reason` | 816 |
| `scanner.py` | `_merge_document_row` | 1697 |
| `section_query.py` | `SectionQueryService` | 109 |
| `service.py` | `SourceCatalog` | 432 |
| `source_lifecycle.py` | `_safety_receipt` | 151 |

（另：`service._read_shared_metadata`（`service.py:93`）是**第二份实现**——它与 `store.metadata_object` 语义等价，属"实现级重复"，见 [b10-plan.md](b10-plan.md) §1。）

## 2. 两处只有做了才会发现的东西（都已登记）

1. **启发式第一版漏了一整类读取者**：只看"参数里有没有写 `metadata_json`"时，`json.loads(row[0] or "{}")` 这种**重命名取值**的读取点（`prompt_injection.py:108/151`、`prompt_injection_guard.py:118`、`extraction_quality.py:195`）**全部看不见**。改成"所在符号提到该列也算"后，总量从 **12 → 21**。
2. **加宽后出现假阳性**：`store.read_pipeline_status`（`store.py:566`）解析的是 `report_json`，只是**同一个符号里**也提到了 `metadata_json`。⇒ 门**不能**把启发式集合当作强制基线，否则会去"要求收敛"一个根本不相干的读取点。

**因此门的基线规则**（B10-1 的实施内容）：
- **强制棘轮**只看 **`confirmed`（10 个）**：新增一个"参数里写着该列"的直接读取者 ⇒ 门**红**；
- 基线**只能降**：清单里已消失的站点若仍留在基线里 ⇒ 门**红**（否则基线会腐烂成橡皮图章）；
- `heuristic` 集合**只报告**（供人分类），**不**参与判定——假阳性已经在上面证明了。

## 3. 下一步（B10 实施顺序，来自 [b10-plan.md](b10-plan.md) §3）

| 步 | 内容 | 验收 |
|---|---|---|
| B10-1 | 新增 `read_chain.py`：链版本常量 + **旧入口注册表**（版本/语义/移除条件）+ 上表的 **confirmed 基线** | 注册表与本次机器导出**逐条一致**；新增未登记入口 ⇒ 红 |
| B10-2 | `service._read_shared_metadata` 改为**委托** `store.metadata_object`（本名保留为显式 adapter 别名） | 行为等价用例 + 收敛门；把委托改回第二份实现 ⇒ **门红**（变异） |
| B10-3 | 10 个 confirmed 读取点**分批**切到单一链（先固定当前行为，再切） | 每批定点用例 + 契约套件；**任何行为变化即停并上呈** |
| B10-4 | `reader.resolve_handle` / `reader.bundle` 就地标注为**显式 v1 adapter**（claim-level，从不读字节） | 门要求：凡返回"可用句柄"的入口必须在注册表声明**是否字节级**；未声明 ⇒ 红 |
| B10-5 | 记录**可回退版本**与**移除条件** | 文档与注册表一致 + 独立复审确认 |

**边界不变**：不写任何 catalog 数据、不改消费者仓、不动冻结常量（`schema_version`/taxonomy 版本）。
