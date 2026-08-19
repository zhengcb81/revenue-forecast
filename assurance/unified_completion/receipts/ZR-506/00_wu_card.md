# ZR-506 工作单元卡（preflight）— section/chunk/tag/fact assertion

- 领取时间：2026-08-19T20:14Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-506`，ZR-505 accepted + closure→ZR-506；锁 ZR-506（owner=zr506-implementer，nonce 19e3dc06…）。
- 依赖：ZR-501（✅）、ZR-502（✅）、ZR-503（✅，entity tag 复用）、ZR-504（✅，页码 locator）、ZR-505（✅，table cell locator）。Registry 依赖列=ZR-501。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第六卡：**section/chunk/tag/fact assertion**（authoritative_execution_plan 阶段 E）。normalized 产物只有扁平 locator 流（page/paragraph/table）——没有章节层级（section 边界与标题）、没有 chunk 分组（section 内段落/表格序列）、没有结构化事实断言（"营业收入：3036亿元" 只是普通文本）。下游（revenue 模型输入、ZR-510 完整 attribution）需要 section 定位、chunk 引用与 fact 断言。
2. **production entrypoint 是什么？** normalizer `_pdf_markdown`/`_render_page_aware_markdown`（body 文本 + locator 流）→ 新纯函数 `section_chunk_fact.py`（section 检测 / chunk 分组 / fact 提取）→ `_frontmatter` 加 `document_structure` 键。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 无 section 层级**：章节标题（"一、经营概况"/"第X章"/"1.1"）在 normalized body 中只是普通段落，无 section 边界/标题识别。
   - **G2 无 chunk 分组**：无 section→段落/表格的 chunk 归属断言。
   - **G3 无 fact 断言**："指标名：数字+单位" 模式（营业收入：3036亿元/单位成本 2.1 万元）无结构化提取。
   - 既有已钉死（不重复）：页码 locator（ZR-504）、table cell locator（ZR-505）、entity tag（ZR-503 detected_entities）。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/section_chunk_fact.py`（纯函数，hermetic 零硬编码）+ normalizer.py（frontmatter `document_structure` 键）+ 新测试 `tests/contract/test_zr506_section_chunk_fact.py`；revenue receipts/ZR-506/**。禁止：真实 catalog 写、下载、LLM、改 admission/schema、IPC envelope 契约、指标名/实体名硬编码。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-507（ProcessingDemand API）。本卡不做：ProcessingDemand（ZR-507）、scheduler 公平性（ZR-508）、HTML capture（ZR-509）、完整逐 section attribution 落库（ZR-510）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-505 accepted（closure.next=ZR-506）。
- [x] triplet 冻结：revenue（ZR-505 closure 提交后）、wiki `7c44904…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：body 有 "## Page N" + locator 注释 + 段落文本；无 section 标记/chunk 分组/fact 断言（has section markers=False 于正文、chunk=False、fact=False）。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（section_chunk_fact 纯函数 + normalizer 接线 + 测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 section 检测（杀 G1）**：`detect_sections(text)` 纯函数（hermetic 零硬编码）识别章节标题行——CJK 序号（`[一二三四五六七八九十百]+、` 行首）、"第X章/第X节"、数字标题（`^\d+(\.\d+)*`）；返回 [{index, title, line_offset}]；无标题 → []；正文含"一、"但非行首不误报。
  - **C2 chunk 分组（杀 G2）**：`chunk_spans(spans, sections)` 将段落/表格 span 归入 section 区间（section 间段落序列 = 该 section 的 chunk）；跨页连续；无 section 时全部归入单个隐式 chunk。
  - **C3 fact 提取（杀 G3）**：`extract_facts(text)` 模式 `指标名：数字+单位`（`[\u4e00-\u9fffA-Za-z0-9]{2,12}[:：]\s*[+-]?\d+(\.\d+)?\s*[单位]?`）→ [{metric, value, unit}]；负数/小数/百分比/无单位均正确；无匹配 → []（不伪造）。
  - **C4 normalizer 接线**：frontmatter `document_structure` 键（sections + chunk_count + facts）；与 ZR-501~505 字段（page_count/homepage_identity/detected_entities）共存。
  - **C5 零硬编码**：产品模块无实体名/指标名硬编码（grep 验证）；"营业收入"等指标名不得写死在产品代码。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超（新文件 max≤10）；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema、IPC envelope 契约变更 → 立即停止。

## Annex：section/chunk/fact 判定矩阵

| 输入 | 期望 |
|---|---|
| "一、经营概况\n\n正文段落" | section [{0, "一、经营概况"}]；chunk 含其下段落 |
| "第一章 总则" / "1.1 背景" | 均识别为 section 标题 |
| 正文含"一、"非行首（"所述一、二点"） | 不误报 section |
| 无标题纯文本 | sections=[]；chunk 单组 |
| "营业收入：3036亿元" | fact {metric: 营业收入, value: 3036, unit: 亿元} |
| "亏损-2.1亿元" / "增长12.5%" / "值 42" | 负数/百分比/无单位均正确 |
| 无模式文本 | facts=[]（不伪造） |
