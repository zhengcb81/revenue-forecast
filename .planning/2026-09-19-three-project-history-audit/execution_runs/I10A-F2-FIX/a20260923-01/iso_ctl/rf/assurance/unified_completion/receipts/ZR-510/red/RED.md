# ZR-510 RED 探针证据（2026-08-19）

探针（company-wiki, wiki HEAD ea9c49b）：
```
grep chunk_attribution src/company_wiki → 0 命中
grep "def attribute_document" src/company_wiki → 0 命中
```
现状：ZR-503 提供 multi_entity_attribution_needed flag（检测+拒绝静默污染），ZR-506 提供 chunk_spans（section 行区间），但**无 chunk 级实体归属**——多实体文档消费方不知道哪个 chunk 属于哪个实体。

结论（G1~G3 坐实）：
- **G1 无逐 chunk 归属**：仅 flag 无归属。
- **G2 错归无证明**：无测试证明长江形状文档 chunk 归属错归=0。
- **G3 无诚实 unattributed**：无实体短语的 chunk 无归属信号。

GREEN 对照（实现后）：attribute_document 每 chunk 归属（entity/mixed/unattributed）；长江形状文档错归=0 断言；multi_entity 文档 frontmatter chunk_attribution 键；确定性 + 零硬编码。
