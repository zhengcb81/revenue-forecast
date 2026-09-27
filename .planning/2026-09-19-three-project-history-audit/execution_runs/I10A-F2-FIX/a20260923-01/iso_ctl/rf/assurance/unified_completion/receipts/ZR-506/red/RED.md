# ZR-506 RED 探针证据（2026-08-19）

探针（company-wiki, wiki HEAD 7c44904）：合成 2 页文档（含"一、经营概况"/"二、成本分析"章节 + "营业收入：3036亿元"事实文本）走 `adapt_pdf_pages` + `_render_page_aware_markdown`。

输出（body 结构）：
```
## Page 1
<!-- locator: loc:v1/page:1/paragraph:0/chars:0-6 -->
一、经营概况
<!-- locator: loc:v1/page:1/paragraph:1/chars:8-32 -->
紫金矿业集团股份有限公司2025年经营情况良好。
<!-- locator: loc:v1/page:1/paragraph:2/chars:34-45 -->
营业收入：3036亿元
## Page 2
<!-- locator: loc:v1/page:2/paragraph:0/chars:47-53 -->
二、成本分析
...
```
信号检测：
```
has section markers: False（正文无 section 标记；'## Page N' 是页标题非章节）
has chunk grouping: False
has fact assertions: False
```

结论（G1~G3 坐实）：
- **G1 无 section 层级**：章节标题（"一、经营概况"）是普通段落，无 section 边界/标题识别。
- **G2 无 chunk 分组**：无 section→段落/表格的 chunk 归属。
- **G3 无 fact 断言**："营业收入：3036亿元" 无结构化提取（metric/value/unit）。

GREEN 对照（实现后）：detect_sections 识别 2 个 section；chunk 分组 2 组；extract_facts 提取 {metric: 营业收入, value: 3036, unit: 亿元}；frontmatter document_structure 键存在。
