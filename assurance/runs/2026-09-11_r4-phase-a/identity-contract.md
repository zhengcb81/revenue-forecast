# A04 identity-contract —— 对外引用与版本身份（v0.1 草案）

> 阶段 A · 步骤 A04 · 只读产出 · 状态：**草案，待 A.DR**。
> 本轮**未访问 catalog 数据库**（保持 A01 声明的"无数据读取"边界）；DB 结构级事实列为 **TO-VERIFY**，附 VR 应执行的**只读**命令。

## 1. 设计契约（对外引用 = 三元组）

```
对外引用 ::= document_id + version/source_hash + locator
```

| 成分 | 语义 | 明确不属于身份的部分 |
|---|---|---|
| `document_id` | 平台内**逻辑文档**的稳定标识（一份报送/年报/研报） | 文件名、标题字符串、绝对路径 |
| `version` / `source_hash` | **内容版本**：源字节 hash（+ 规范化后 hash）；同一逻辑文档的不同修订是不同的 version | 目录层级、root、抓取时间 |
| `locator` | **定位**：`root_id` + 相对路径（+ 页码/表格锚点，用于证据） | locator **不是**身份：换 root/换副本不改变 document identity |

**契约规则 R4**：**路径诊断信息不得进入业务身份**。即在比较、去重、复用、对外引用时，只能使用 `document_id` + `version/source_hash`；`root_id`/相对路径只用于**定位**与诊断，不得作为"是否同一文档"的判据。

## 2. 同字节副本 vs 真实修订（必须区分）

| 情形 | 判定 | 依据 |
|---|---|---|
| 同一 `document_id`，**字节完全相同**（`source_hash` 相同）出现在多个 root/路径 | **同字节副本（exact copy）**——不是新版本 | 现有 `duplicates` / `duplicate-preview` / `duplicate-recycle` 一族与 `is_canonical` 选择逻辑（`resolver.py:915/1157`） |
| 同一 `document_id`，**字节不同**（hash 不同） | **真实修订/不同版本**——必须并存，不得覆盖 | 版本轴即 `source_hash`；A06 基线用例按版本分别冻结 |
| 不同 `document_id`，字节相同 | 保留为**不同文档**，除非有**凭据**证明是同一逻辑文档 | 契约规则 R5 |

**契约规则 R5（不得强行合并）**：**无凭据证明是同一逻辑文档时，禁止合并**。合并只允许在具备来源证据（同一 provider 文档号 / 同一原始 URL / 同一申报期同一实体）并记录证据 hash 的情况下进行。

**契约规则 R6（alias 迁移不删旧引用）**：身份别名（公司别名、证券代码、历史命名）迁移时，**旧引用必须保留可解析**（或保留映射表），不得因为"改名"而删除或失效既有引用。

## 3. 当前代码事实（已核实，带位置）

| 事实 | 位置 |
|---|---|
| 采集侧显式携带 `provider_document_id`、`fiscal_year`、`content_sha256`（小写 SHA-256 强校验） | `acquisition.py:78/85/155/158/187` |
| 采集日志/服务侧有 `content_sha256`、去重结果 `deduplicated_after_download` / `DEDUPLICATED` | `acquisition_journal.py:56-87`、`acquisition_service.py:29/179` |
| 采集回执校验：重算摘要必须等于 `receipt.content_sha256` | `acquisition.py:554` |
| 副本/规范位：`is_canonical` 参与选择 | `resolver.py:915/1157` |
| 文档/来源/产物分层：`documents` / `sources` / `artifacts` 三表，artifact 绑定 `source_sha256`（A-2 fail-closed 门） | 本会话既有 A-2 修复记录（`summarizer.py`/`section_extractor.py` 空 `source_sha` 修复） |
| 身份解析入口 | `identify`（`cli.py:306`、`identity_cli.py:24`）：name/alias/ticker → **one verified listed security** |

## 4. TO-VERIFY（VR 必须用**只读**命令核实，未测即 blocked）

| # | 待核实 | 建议只读命令（走批准后的 command-manifest） |
|---|---|---|
| V1 | `documents` 表的主键/唯一约束、是否含 `document_id`；`sources`/`artifacts` 的外键与 hash 列 | `sqlite3 <catalog> ".schema documents"` / `".schema sources"` / `".schema artifacts"`（只读，不查行） |
| V2 | 同 `document_id` 多版本是否**并存**（是否存在覆盖式写入） | 只读聚合计数（不导出正文） |
| V3 | `is_canonical` 的选择键（是否只用路径/优先级——即是否存在"路径参与身份"的残留） | `resolver.py:900-960` / `1150-1170` 代码复核 + 只读查询 |
| V4 | 同字节副本跨 root 的实际分布（exact copy 判定是否只看 `content_sha256`） | `duplicates` 命令（只读）在隔离副本上运行 |
| V5 | alias/旧引用：是否存在"改名即失效"的路径 | `identify` 只读调用 + 别名表结构复核 |

## 5. 交给 A.DR 的问题

1. `locator` 里是否允许携带**页码/表格锚点**（证据级定位）而不污染身份？本草案认为允许，但要明确"锚点属于证据，不属于身份"。
2. 契约 R5 的"凭据"清单是否要收敛为闭集（provider 文档号 / 原始 URL / 申报期+实体三者之一）？
3. `duplicate-preview` 的 confirmation token 是否应写入"副本处置"审计（与 A03 §4.1 同一问题）？
4. 同一 `document_id` 的**字节完全相同**的两份，是否允许**都**作为 locator 保留（当前 `is_canonical` 选一处，其余为副本）？

## 6. 边界

- 本文件为设计草案：未访问 DB、未运行 CLI、未改产品代码/配置；§3 之外的 schema 细节一律标 TO-VERIFY，不写成已通过。
