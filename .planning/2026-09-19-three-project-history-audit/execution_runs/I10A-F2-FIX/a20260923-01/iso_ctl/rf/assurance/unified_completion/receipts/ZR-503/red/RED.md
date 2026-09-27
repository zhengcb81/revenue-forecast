# ZR-503 RED 探针证据（2026-08-19）

探针：构造长江式多实体比较报告（首页文本含「紫金矿业集团股份有限公司VS陕西煤业股份有限公司」+ broker_research 元数据），走 `_frontmatter` 产 normalized frontmatter。

命令（company-wiki, wiki HEAD 19c3b73）：
```
@'<python probe>'@ | .venv\Scripts\python.exe -
```

输出：
```
frontmatter keys: ['artifact_role', 'document_id', 'document_kind', 'homepage_identity', 'normalization_status', 'page_count', 'parser_name', 'parser_version', 'published_date', 'quality_flags', 'schema_version', 'source_id', 'source_sha256', 'title']
has detected_entities: False
quality_flags: ['homepage_identity_contradiction']
has multi_entity flag: False
```

结论（G1 坐实）：
- **G1 多实体零检测**：双实体正文（紫金 + 陕西煤业）normalize 产物无任何多实体信号——无 `detected_entities` 键、无 `multi_entity_attribution_needed` flag。下游按单实体（sidecar canonical_entity_id）消费时，陕西煤业内容被静默归入紫金（错归污染，BR-06/07 要求错归=0）。
- **G2 无检测机制**：不存在公司名短语提取 + 声明比对的纯函数。
- **G3 无防污染门**：无 fail-closed 标记拒绝静默单实体归属。
- 注：`homepage_identity_contradiction` 为该构造（title 与首页文本字面不一致）的 ZR-502 既有行为，与本卡 RED 无关；真实 sidecar title 与首页一致时 ZR-502 判 consistent。
- 锚点：golden corpus `zijin_broker_20240304_changjiang`（dropbox anchor，sha256 273d450887eff7c079b28f394c4831092fa3abbb81db86f2544cab425c2719d7，entities=[紫金矿业集团股份有限公司, 陕西煤业股份有限公司]）——本卡只读引用 hash，不拉原文。

RED 探针脚本与输出已记录；实现后同探针须输出 `detected_entities` 存在且 verdict=multi_entity（GREEN 对照）。

## GREEN 对照（实现后，wiki HEAD 含 ZR-503 变更）

同构造探针输出：
```
has detected_entities: True
verdict: multi_entity
phrases: [<紫金全称>, <陕西全称>]
flags: ['homepage_identity_contradiction', 'multi_entity_attribution_needed']
```
G1/G2/G3 闭环：`detected_entities` 键 + `multi_entity_attribution_needed` flag 落 frontmatter；13 tests 全绿（C1 纯函数 7 + C2 接线 4 + C3 锚定 2）。
