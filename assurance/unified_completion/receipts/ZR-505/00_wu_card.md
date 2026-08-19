# ZR-505 工作单元卡（preflight）— typed table artifact：表格保真 golden

- 领取时间：2026-08-19T20:06Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-505`，ZR-504 accepted + closure→ZR-505；锁 ZR-505（owner=zr505-implementer）。
- 依赖：ZR-501（accepted ✅）、ZR-504（accepted ✅，页码保真）。Registry 依赖列=ZR-501。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第五卡：**typed table artifact（表格保真）**。券商研报核心数据在表格中（产量/成本/估值表）——每 cell 的 locator（page/table/row/column）、markdown 渲染、结构化值保真，是下游表格引用与勾稽（ZR-506 chunk/tag/fact、revenue 模型输入）的基础。golden corpus 七份研报含多表；authoritative_execution_plan 阶段 E：typed table。
2. **production entrypoint 是什么？** pdf_page_aware parser `_table_results`（table 快照契约 markdown/rows/cols/data → 每 cell ParserResult with coordinates page/table_index/row_index/column_index + structured_value kind=table_cell）→ `_render_page_aware_markdown`（Table cell [row, column] 渲染）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 无表格 golden**：无测试钉死表格 locator 流（page/table_index/row_index/column_index 三维保真）、markdown 渲染、structured_value 标量保真（str/int/float/bool/null 类型不变形）。
   - **G2 校验路径无测试**：非矩形 data、rows≠len(data)、非法 cell（dict/list/非 JSON 标量）、字段集不精确 → PageAwarePDFAdapterError 拒绝（机制存在，无断言）。
   - **G3 多表/跨页保真无测试**：同页多表 table_index 0,1…、跨页表格 table_index 每页从 0 重置、表格与段落 span 共存页的 locator 完整性。
   - 既有已钉死（不重复）：页码保真（ZR-504）、table 输入契约（_TABLE_FIELDS 精确校验内建）、矩形校验（_table_results 内建）。
4. **允许改哪些文件？** company-wiki 新增 `tests/contract/test_zr505_table_fidelity.py`（合成 pages fixture 直喂 adapt_pdf_pages：C1 表格 locator golden、C2 结构化值保真、C3 渲染、C4 校验拒绝路径、C5 多表/跨页 + golden 锚定）；若探针发现缺口则修 `pdf_page_aware.py`/`normalizer.py`；revenue receipts/ZR-505/**。禁止：真实 catalog 写、下载、LLM、改 admission/schema、改 IPC envelope 契约。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-506（section/chunk/tag/fact assertion）。本卡不做：section/chunk/tag/fact（ZR-506）、逐份 published_date 重建（ZR-504/505 外延登记）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-504 accepted（closure.next=ZR-505）。
- [x] triplet 冻结：revenue（ZR-504 closure 提交后）、wiki `2781df9…`、filing `5a1c18f…`。
- [x] 现状事实：`_table_results` 每 cell 一 ParserResult（page/table_index/row_index/column_index + structured_value kind=table_cell + raw_value/value）；table 输入契约 markdown/rows/cols/data；矩形 + 标量 + 字段集精确校验内建；渲染 `- Table cell [row, column]: value`。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（测试 golden + 探针驱动的保真修复）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3（预期 test-only 钉死，同 ZR-504 模式）。
- **Acceptance criteria**：
  - **C1 表格 locator golden（杀 G1）**：合成 pages fixture（页2 含 2×2 表）喂 `adapt_pdf_pages` → cell spans locator (page, table_index, row_index, column_index) 全序保真；`loc:v1/page:N/table:T/row:R/column:C/chars:…` 渲染含表维度。
  - **C2 结构化值保真（杀 G1 端）**：cell 类型 str/int/float/bool/null 输入 → structured_value.raw_value 类型不变形、value 文本化正确（str 原样、bool→true/false、int/float→str、null→None）；rectangular 数据全 cell 覆盖（rows×cols 个 span）。
  - **C3 渲染（杀 G1 端）**：`_render_page_aware_markdown` body 含 `- Table cell [r, c]: value` 行且顺序=row-major；与段落 span 共存页顺序正确（段落后表格）。
  - **C4 校验拒绝（杀 G2）**：非矩形（行长度不等）、rows≠len(data)、非法 cell（dict/list/NaN）、字段集多/缺 → PageAwarePDFAdapterError。
  - **C5 多表/跨页（杀 G3）**：同页两表 table_index 0,1；页2 表与页3 表各自从 0 重置；golden corpus 七份研报 ≥7 只读锚定（同 ZR-504 C5）。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema、IPC envelope 契约变更 → 立即停止。

## Annex：表格保真判定矩阵

| 场景 | 期望 |
|---|---|
| 2×2 表（str/int/bool/null） | 4 个 cell span；(page,0,0,0)…(page,1,1,1)；raw_value 类型不变；value 文本化正确 |
| 同页两表 | table_index 0,1（页内从 0） |
| 跨页两表 | 每页 table_index 从 0 重置 |
| 非矩形 data | PageAwarePDFAdapterError |
| rows≠len(data) | PageAwarePDFAdapterError |
| cell 为 dict/list/NaN | PageAwarePDFAdapterError |
| table 字段集不精确 | PageAwarePDFAdapterError |
| 段落后表格渲染 | body 段落 span 行在前、Table cell 行在后 |
