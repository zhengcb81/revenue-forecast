# ZR-504 工作单元卡（preflight）— 页码保真：normalized Markdown 的逐页 locator golden

- 领取时间：2026-08-19T19:58Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-504`，ZR-503 accepted + closure→ZR-504；锁 ZR-504（owner=zr504-implementer）。
- 依赖：ZR-501（accepted ✅，page_count 契约）、ZR-502（accepted ✅，first_page_text）、ZR-503（accepted ✅，全文检测）。Registry 依赖列=ZR-501。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第四卡：**页码/阅读顺序保真**（authoritative_execution_plan 阶段 E：页码/阅读顺序、typed table、chunk/tag/fact）。normalized Markdown 每个 span 的 locator 页码必须与源 PDF 物理页序一致、阅读顺序=页序、跨页 char 偏移全局连续——下游（ZR-506 section/chunk/tag/fact、revenue 引用）依赖 locator 页码做逐页引用与勾稽。现状：`adapt_pdf_pages` 强制物理页序连续（`_validate_page` expected_page_number=index）、normalized_text 按页序拼接、locator 含 page/paragraph/chars——机制存在但**无 golden 测试钉死**，且 page_count（ZR-501）与 locator 页码集无交叉验证；golden corpus 七份研报（published_date=null）的逐份页码/日期验证待本卡（notes："catalog published_date=null（ZR-504/505 需重建）"）。
2. **production entrypoint 是什么？** pdf_page_aware parser（`adapt_pdf_pages`：pages 严格快照 → ParserResult with coordinates.page_number/paragraph_index/char 全局偏移）→ normalizer `_pdf_markdown`/`_render_page_aware_markdown`（locator 注释渲染）→ `normalize_catalog`（frontmatter page_count，ZR-501 契约）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 无逐页 locator golden**：无测试钉死多页文档的 locator 序列（page 序 1..N、页内 paragraph_index 从 0、char_start/end 全局连续、页间 "\n\n" 分隔的阅读顺序=物理页序）。
   - **G2 页错误路径无保真断言**：error 页（PARSER_ERROR span 带 page_number）不破坏后续页序号与 char 偏移；empty 页（EMPTY_OUTPUT）同。
   - **G3 交叉验证缺口**：frontmatter page_count（ZR-501）与 locator 页码集（max page == page_count、每页至少一个 span）无一致性测试。
   - 既有已钉死（不重复）：物理页序强制连续（_validate_page 内建）、page_count 过 IPC envelope（ZR-501）、normalized_text 拼接。
4. **允许改哪些文件？** company-wiki 新增 `tests/contract/test_zr504_page_fidelity.py`（合成 pages fixture 直喂 `adapt_pdf_pages`——无需真 PDF；含 C1 多页 locator 保真、C2 阅读顺序与 body 渲染、C3 page_count 交叉、C4 页错误路径、C5 golden 锚定）+ 若探针发现保真缺口则修 `pdf_page_aware.py`/`normalizer.py`；revenue receipts/ZR-504/**。禁止：真实 catalog 写、下载、LLM、改 admission/schema、改 IPC envelope 契约。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-505（typed table artifact）。本卡不做：table 结构化保真（ZR-505）、多实体 attribution（ZR-503 已闭）、published_date 逐份重建（登记为 ZR-504 外延/后续卡——本卡只钉页码契约，published_date 重建待七份 PDF golden 验证卡）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-503 accepted（closure.next=ZR-504）。
- [x] triplet 冻结：revenue（ZR-503 closure 提交后）、wiki `e8e2926…`、filing `5a1c18f…`。
- [x] 现状事实：`adapt_pdf_pages` pages 严格快照契约（`_PAGE_FIELDS` 精确字段集）；`_validate_page` 物理页序连续强制；normalized_text 页间 "\n\n"；locator = page/paragraph/chars；page_count=len(validated)（ZR-501）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（测试 golden + 探针驱动的 parser 保真修复）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 逐页 locator golden（杀 G1）**：合成 3 页 fixture（页1 两段、页2 一段+一表、页3 文本）喂 `adapt_pdf_pages` → parser_results locator 页序 1,1,2,2,3…（按物理页序）、页内 paragraph_index 从 0 连续、char_start/end 全局连续（跨页单调递增、页间 "\n\n" 偏移计入）、normalized_text 页序拼接。
  - **C2 阅读顺序与 body 渲染（杀 G1 端）**：`_render_page_aware_markdown` 渲染的 normalized body 中 locator 出现顺序 = 物理页序；`_pdf_markdown` 的 `_first_page_text`（ZR-502）与页1 span 一致。
  - **C3 page_count 交叉验证（杀 G3）**：result.page_count == 3 == locator 最大页码；每页至少一个 span（或 error span 保页码）；frontmatter page_count 与 parser page_count 一致（ZR-501 契约回连）。
  - **C4 页错误路径保真（杀 G2）**：error 页 → PARSER_ERROR span 带正确 page_number、后续页序号/char 偏移不破坏；empty 页（无文本无表）→ EMPTY_OUTPUT span 保页码。
  - **C5 golden 锚定**：七份研报样本（golden corpus）至少一份 hash 只读锚定 + published_date=null 现状登记（ZR-504/505 重建外延）。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema、IPC envelope 契约变更 → 立即停止。

## Annex：页码保真判定矩阵

| 场景 | 期望 |
|---|---|
| 3 页文档（文本页） | locator page 序 1..3；paragraph_index 页内 0..；char 全局连续 |
| 页间分隔 | normalized_text 页间 "\n\n"（char 偏移 +2 计入） |
| error 页（text/tables 全空 + error 非空） | PARSER_ERROR span（page_number 保留）；后续页不受影响 |
| empty 页（无文本无表无 error） | EMPTY_OUTPUT span（page_number 保留） |
| 页序不连续（page_number 缺页） | _validate_page 抛 PageAwarePDFAdapterError（既有强制，回连断言） |
| page_count vs locator 最大页码 | 相等（交叉验证） |
