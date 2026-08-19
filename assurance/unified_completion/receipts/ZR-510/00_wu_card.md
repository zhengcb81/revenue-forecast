# ZR-510 工作单元卡（preflight）— 阶段 E 收尾：多实体 chunk attribution（错归=0）

- 领取时间：2026-08-19T20:45Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-510`，ZR-509 accepted + closure→ZR-510；锁 ZR-510（owner=zr510-implementer）。
- 依赖：ZR-503（✅ entity 检测）、ZR-504（✅ 页码 locator）、ZR-505（✅ table cell locator）、ZR-506（✅ section/chunk/fact）。Registry 依赖列=ZR-501。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 E 第十卡（收尾）：**多实体 chunk attribution，错归=0**（traceability BR-06/07：长江紫金/陕西煤业 section/table/row attribution 准确，错归=0；golden corpus：长江比较报告双实体负例"供 ZR-503/510 错归测试"）。ZR-503 已钉"检测 + 拒绝静默单实体污染"（multi_entity_attribution_needed flag）；本卡交付**逐 chunk 归属**——多实体文档的每个 chunk（section 区间）归属到其文本实际提到的实体，未提实体的 chunk 诚实标 unattributed（不猜、不伪造）。
2. **production entrypoint 是什么？** 新 `src/company_wiki/source_catalog/attribution.py` 纯函数：`attribute_document(text, chunks, declared_entities)` → 每 chunk [{chunk_index, start, end, entities, attribution}]——复用 entity_detection 的短语提取；normalizer 接线：frontmatter 加 `chunk_attribution` 键（仅当 detected_entities 为 multi_entity 时输出，single 文档保持简洁）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 无逐 chunk 归属**：多实体文档仅 flag（ZR-503）无 chunk 级归属——消费方无法知道哪个 chunk 属于哪个实体。
   - **G2 错归无证明**：无测试证明"长江形状文档的 chunk 归属不含跨实体错归"（错归=0）。
   - **G3 无诚实 unattributed**：无实体短语的 chunk（如"本报告仅供内部参考"）无归属信号。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/attribution.py` + normalizer.py（frontmatter `chunk_attribution` 键）+ 新测试 `tests/contract/test_zr510_attribution.py`；revenue receipts/ZR-510/**。禁止：真实 catalog 写、下载、LLM、改 admission/schema、实体名硬编码。
5. **下一单元解锁条件？本单元不解决什么？** 本卡为阶段 E 收尾；解锁 ZR-304~306 存量迁移部分（阶段 E 尾部）或阶段 F。本卡不做：attribution 落库/持久化（后续卡）、真实文档全链处理（阶段 G）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-509 accepted（closure.next=ZR-510）。
- [x] triplet 冻结：revenue（ZR-509 closure 提交后）、wiki `ea9c49b…`、filing `5a1c18f…`。
- [x] 现状事实：entity_detection 短语提取可复用（ZR-503）；chunk_spans 提供 section 行区间（ZR-506）；multi_entity flag 已有；无 chunk 级归属。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（attribution.py + normalizer 接线 + 测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 逐 chunk 归属（杀 G1）**：`attribute_document(text, chunks, declared_entities)` 纯函数（hermetic 零硬编码）——每 chunk 提取实体短语（复用 ZR-503 模式）→ attribution ∈ {entity_name, mixed, unattributed}；chunk 只提一个实体 → 该实体；多个 → mixed；无 → unattributed（诚实）。
  - **C2 错归=0（杀 G2）**：长江形状文档（section A=紫金内容、section B=陕西内容、section C=无实体）→ 紫金 chunk 归属紫金、陕西 chunk 归属陕西、C unattributed——任何 chunk 的 attribution 不含非本 chunk 实体（错归=0 断言）。
  - **C3 normalizer 接线（杀 G3 端）**：multi_entity 文档 frontmatter 加 `chunk_attribution` 键（[{chunk_index, start, end, entities, attribution}]）；single 文档无该键（保持简洁）；与 ZR-501~509 字段共存。
  - **C4 确定性 + 零硬编码**：同输入同输出；产品模块无实体名硬编码。
  - 质量门：wiki unit 787 + 受影响 contract 无回归；ruff clean；复杂度 ratchet 不超（新文件 max≤10）；独立 reviewer 复放。
- **Stop conditions / handoff**：真实 catalog 写、下载、LLM、改 admission/schema、attribution 落库/持久化 → 立即停止。

## Annex：chunk attribution 判定矩阵

| chunk 文本 | attribution |
|---|---|
| 只含"紫金矿业集团…" | 紫金矿业集团股份有限公司（declared 匹配名） |
| 只含"陕西煤业股份有限公司…" | 陕西煤业股份有限公司 |
| 含两个实体名 | mixed |
| 无实体短语 | unattributed |
| declared 简称（紫金矿业）与全称 containment | 归一化匹配 → 归属 declared 全称 |
