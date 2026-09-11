# A04 identity-contract —— 对外引用与版本身份（v0.2 草案，已按 A.DR 更正）

> 🔴 **v0.2 更正（2026-09-11，回应 A.DR rejected）**：
> 1. **R4 不是现状，而是目标**（A-DR-07）：现行代码里 **`priority`/`root_id`/`relative_path` 确实参与"哪个位置代表该文档"的判定** —— `service.py:621-663` 的 `_annotate_locations` 按 `source_id` 分组后以 `(root_priority, root_id, relative_path, location_id)` 排序，取 `ordered[0]` 标 `is_canonical=True`；排序 SQL 亦为 `ORDER BY l.document_id, r.priority, l.root_id, l.relative_path`（`service.py:329`、`:527`）；`resolver.py:912-921` 还按**路径内容**过滤（排除含 `.rejections` 的 `original_primary`），`:528-533` 的 rationale 亦自述 `lowest_priority_active_original_primary_then_tiebreak`。→ R4 重述为**目标**并点名残留。
> 2. **V3 的静态一半已答**（A-DR-07）：选择键**确实是** `(priority, root_id, relative_path, location_id)`——**路径参与身份投影**；只剩"DB 内实际分布/是否存在覆盖式写入"属数据侧，留给 VR。
> 3. **R6 补 owner / 机制 / 存储 / 负例**（A-DR-13）：v0.1 的 R6 是纯规范句，无可检测性；且其 V5 用 `identify` 作验证命令，而 `identify --refresh` 是网络+写路径（A-DR-04）。
> 4. **V5 命令收紧**：只允许**无 `--refresh`** 的 `identify`（`cli.py:1080-1087` 已证 `--refresh` 会触网+写）。
>
> 阶段 A · 步骤 A04 · 只读产出 · 状态：**草案 v0.2，待 A.DR 复审**。
> 本轮**未访问 catalog 数据库**（保持 A01 声明的"无数据读取"边界）；DB 结构级事实列为 **TO-VERIFY**，附 VR 应执行的**只读**命令。
> ⚠️ **边界更正如实披露**（A-DR-08）：本 run 期间生产 catalog 的 `catalog.sqlite3-shm` 被观测到有写入（21:18:15），**归属未明**；"未访问 DB"仅是作者对**本会话未执行 CLI/未打开 DB** 的声明，**不构成"无第三方连接"的证明**。详见 [boundary-audit.md](boundary-audit.md)。

## 1. 设计契约（对外引用 = 三元组）

```
对外引用 ::= document_id + version/source_hash + locator
```

| 成分 | 语义 | 明确不属于身份的部分 |
|---|---|---|
| `document_id` | 平台内**逻辑文档**的稳定标识（一份报送/年报/研报） | 文件名、标题字符串、绝对路径 |
| `version` / `source_hash` | **内容版本**：源字节 hash（+ 规范化后 hash）；同一逻辑文档的不同修订是不同的 version | 目录层级、root、抓取时间 |
| `locator` | **定位**：`root_id` + 相对路径（+ 页码/表格锚点，用于证据） | locator **不是**身份：换 root/换副本不改变 document identity |

**契约规则 R4（目标，非现状 —— v0.2 更正）**：**路径诊断信息不得进入业务身份**。即在比较、去重、复用、对外引用时，只能使用 `document_id` + `version/source_hash`；`root_id`/相对路径只用于**定位**与诊断，不得作为"是否同一文档"的判据。

> **残留（已核实的反面事实，A-DR-07）**：该目标**当前未达成**，三处代码把路径/优先级放进了"代表该文档的位置"这一**身份投影**：
> 1. `service.py:643-653`：`sorted(group, key=(root_priority, root_id, relative_path, location_id))` → `ordered[0]` 即 `is_canonical`。**优先级与路径决定"规范位"**。
> 2. `service.py:329` / `:527`：locations 读取的 `ORDER BY l.document_id, r.priority, l.root_id, l.relative_path`。
> 3. `resolver.py:912-921`：canonical 候选**按路径字符串内容**过滤（`.rejections` 排除）；`:528-533` rationale 自述 `lowest_priority_active_original_primary_then_tiebreak`。
> **注意边界**：这三处影响的是"**哪个位置代表文档**"（locator/规范位选择），**不是** `document_id` 本身的生成；因此 R4 的严格读法是"**身份投影**中不得含路径"，而当前实现是"身份稳定、**位置代表权**由路径与优先级决定"。是否把后者也算违例，请 A.DR/owner 裁定（§5 问题 1）。
>
> **与 A02 的交叉**：`priority` 正是 A02 §2 表中 `dropbox_stock`(30)/`future_lake`(40) 等 root 的字段——即**同一字段**既服务于"复用能力"（A02 C4，实际不读它）又服务于"代表位选择"（此处读它）。A02 R8 的收敛必须同时覆盖这两条用途。

## 2. 同字节副本 vs 真实修订（必须区分）

| 情形 | 判定 | 依据 |
|---|---|---|
| 同一 `document_id`，**字节完全相同**（`source_hash` 相同）出现在多个 root/路径 | **同字节副本（exact copy）**——不是新版本 | 现有 `duplicates` / `duplicate-preview` / `duplicate-recycle` 一族与 `is_canonical` 选择逻辑（`resolver.py:915/1157`） |
| 同一 `document_id`，**字节不同**（hash 不同） | **真实修订/不同版本**——必须并存，不得覆盖 | 版本轴即 `source_hash`；A06 基线用例按版本分别冻结 |
| 不同 `document_id`，字节相同 | 保留为**不同文档**，除非有**凭据**证明是同一逻辑文档 | 契约规则 R5 |

**契约规则 R5（不得强行合并）**：**无凭据证明是同一逻辑文档时，禁止合并**。合并只允许在具备来源证据（同一 provider 文档号 / 同一原始 URL / 同一申报期同一实体）并记录证据 hash 的情况下进行。

**契约规则 R6（alias 迁移不删旧引用 —— v0.2 补齐可检测要素，A-DR-13）**：身份别名（公司别名、证券代码、历史命名）迁移时，**旧引用必须保留可解析**（或保留映射表），不得因为"改名"而删除或失效既有引用。

| 要素 | 内容 |
|---|---|
| **owner** | 身份别名/证券主数据的写入方（`identity-enrichment verify` 路径 + `security_identity` 主数据刷新）；**本阶段无 owner 指派**，需 owner 裁定（§5 问题 2） |
| **机制** | 别名→证券的解析必须**追加式**：新增映射而不覆盖；历史映射以**生效区间**（或版本号）标记，而非原地改写 |
| **存储位置** | **TO-VERIFY（数据侧）**：别名/证券主数据的表名与列 **未核实**（本轮未开 DB）。静态可知的入口：`identity_enrichment` 断言（`identity-enrichment preview/verify/reject`）、`security_identity.py` 的 identity master/cache、`--identity-cache-dir` |
| **负例（可检测）** | 1) 对同一实体做两次别名迁移后，**第一次的别名仍能解析**到同一 `security_id`；2) 迁移后**旧引用不出现"未找到"**；3) 断言被 `reject` 后其**历史已验证映射不被删除**（`activation rollback` 可回退） |
| **验证方式** | VR 在**隔离副本**上：先 `identify`（**必须不带 `--refresh`**）解析旧别名，再复核别名表结构（V5） |

## 3. 当前代码事实（已核实，带位置）

| 事实 | 位置 |
|---|---|
| 采集侧显式携带 `provider_document_id`、`fiscal_year`、`content_sha256`（小写 SHA-256 强校验） | `acquisition.py:78/85/155/158/187` |
| 采集日志/服务侧有 `content_sha256`、去重结果 `deduplicated_after_download` / `DEDUPLICATED` | `acquisition_journal.py:56-87`、`acquisition_service.py:29/179` |
| 采集回执校验：重算摘要必须等于 `receipt.content_sha256` | `acquisition.py:554` |
| 副本/规范位：`is_canonical` 参与选择 | `resolver.py:915/1157` |
| **规范位选择键 = `(root_priority, root_id, relative_path, location_id)`**（按 `source_id` 分组，取最小者） | **`service.py:643-653`**（`_annotate_locations`，`:621-663`）；取值 SQL 排序 `service.py:329` / `:527` |
| **canonical 候选按路径内容过滤**（排除含 `.rejections` 的 `original_primary`，并单独出 `rejections_path` trace） | `resolver.py:912-931` |
| **canonical rationale 自述"按优先级择低再 tiebreak"** | `resolver.py:528-533`（字符串字面量，非分支） |
| 规范位选择**发生在 service 的 `source_id` 分组上**（即 exact-copy 组以 `source_id` 为键，而非直接以 content hash 为键） | `service.py:634-641`；`source_id`↔`content_sha256` 的对应关系属数据侧 **TO-VERIFY（V4 邻接）** |
| 文档/来源/产物分层：`documents` / `sources` / `artifacts` 三表，artifact 绑定 `source_sha256`（A-2 fail-closed 门） | 本会话既有 A-2 修复记录（`summarizer.py`/`section_extractor.py` 空 `source_sha` 修复） |
| 身份解析入口 | `identify`（`cli.py:306`、`identity_cli.py:24`）：name/alias/ticker → **one verified listed security** |

## 4. TO-VERIFY（VR 必须用**只读**命令核实，未测即 blocked）

| # | 待核实 | 建议只读命令（走批准后的 command-manifest） |
|---|---|---|
| V1 | `documents` 表的主键/唯一约束、是否含 `document_id`；`sources`/`artifacts` 的外键与 hash 列 | `sqlite3 <catalog> ".schema documents"` / `".schema sources"` / `".schema artifacts"`（只读，不查行） |
| V2 | 同 `document_id` 多版本是否**并存**（是否存在覆盖式写入） | 只读聚合计数（不导出正文） |
| V3 | `is_canonical` 的选择键 | ✅ **静态一半已答（v0.2）**：选择键 = `(root_priority, root_id, relative_path, location_id)`，**路径与优先级确实参与**（`service.py:621-663`）。**残留**：仍待 VR 的是数据侧——实际分布是否出现"同 `document_id` 同 `source_id` 但规范位落在非预期 root"、以及是否存在覆盖式写入（并入 V2） |
| V4 | 同字节副本跨 root 的实际分布（exact copy 判定是否只看 `content_sha256`） | `duplicates` 命令（只读）在隔离副本上运行；**另需核** `source_id` 与 `sources.content_sha256` 是否一一对应（`service.py:634-641` 以 `source_id` 分组） |
| V5 | alias/旧引用：是否存在"改名即失效"的路径 | `identify --query <旧别名>`（**严禁 `--refresh`**，见 §2 R6 表）+ 别名表结构复核 |

## 5. 交给 A.DR 的问题（v0.2）

1. **R4 的严格读法**（A-DR-07 引出）：现行 `is_canonical`/规范位选择把 `priority`/`root_id`/`relative_path` 纳入排序。这影响的是**位置代表权**而非 `document_id` 生成。是否把"位置代表权由路径决定"也算违反 R4？若算，R4 需在 B/C 阶段登记为整改项。
2. **R6 的 owner**：别名迁移目前**无 owner 指派**（§2 R6 表）。请裁定 owner（建议：`identity-enrichment` 断言路径 + `security_identity` 主数据刷新共同负责），否则 R6 仍不可检测。
3. `locator` 里是否允许携带**页码/表格锚点**（证据级定位）而不污染身份？本草案认为允许，但要明确"锚点属于证据，不属于身份"。
4. 契约 R5 的"凭据"清单是否要收敛为闭集（provider 文档号 / 原始 URL / 申报期+实体三者之一）？
5. `duplicate-preview` 的 confirmation token 是否应写入"副本处置"审计（与 A03 §4 同一问题）？
6. 同一 `document_id` 的**字节完全相同**的两份，是否允许**都**作为 locator 保留（当前 `is_canonical` 选一处，其余为 `duplicate_relation=exact_copy`，`service.py:659-662`）？
7. **V1/V2/V4 的数据读取权限**：本轮在"无 DB 读取"边界下完成；是否同意在 A06 的**隔离副本**上执行（而非生产 catalog，其体积 **49,677,344,768 B**）？

## 6. 边界

- 本文件为设计草案：未访问 DB、未运行 CLI、未改产品代码/配置；§3 之外的 schema 细节一律标 TO-VERIFY，不写成已通过。
- **"未访问 DB"的范围如实限定**：指**本作者会话未打开 catalog 数据库、未执行任何 CLI 数据命令**；**不**声称同期不存在任何进程连接（见 A-DR-08 与 [boundary-audit.md](boundary-audit.md) 的 shm 观测）。
