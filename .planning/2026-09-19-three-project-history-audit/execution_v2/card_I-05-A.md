本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-05-A — 默认产物与验证器共用契约，sections 不能绕过资格

parent：I-05；status：planned；owner：wiki producer 实施者；RF reviewer 独立验收。

依赖：I-02-E。设计前置：D-W05。证据目录：`execution_runs/I-05-A/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/src/company_wiki/source_catalog/artifact_handle.py:78](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/artifact_handle.py:78>) `validate_artifact`：现有 completed/schema/source/hash/registry/date/path 门；保留已通过约束。 SHA256 `3cc8fbf4f65380d17e2f0140390ef346f7cc17504854ff04b3ddf46498317b99`。
- [company-wiki/src/company_wiki/source_catalog/source_bundle.py:99](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/source_bundle.py:99>) `build_source_bundle`：默认 registry 及 newest VALID 选择已存在。 SHA256 `fe64912172d3004b137ebf415a01b8b3e75eb41ea785edf254644258f0c2261c`。
- [company-wiki/src/company_wiki/source_catalog/normalizer.py:1962](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/normalizer.py:1962>) `normalize_catalog artifact INSERT`：当前已写 schema=1.0/source_sha/created_at，旧失败不等于当前 producer 仍缺字段。 SHA256 `772075ed0d1c540aeb2a0feea17d7735a28c0aba981edfbdefa7297a57a06cff`。
- [company-wiki/src/company_wiki/source_catalog/llm_summarizer.py:514](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/llm_summarizer.py:514>) `summarize_catalog_with_llm artifact INSERT`：当前已写同类字段；不改旧结果冒充新产物。 SHA256 `a930a42e04d52a47e8469be346c92eb58dfe604332d6a7708edaf94ad9fa4ade`。
- [company-wiki/src/company_wiki/source_catalog/section_extractor.py:283](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/section_extractor.py:283>) `extract_sections_catalog`：现有 sec.artifact_id IS NULL 不区分 failed/stale。 SHA256 `b59ce324d3481e790acd92d96b2b662d94d5ab7ddf60e896658dfa8bb055406b`。
- [company-wiki/src/company_wiki/source_catalog/section_query.py:90](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/section_query.py:90>) `SectionQueryService.list_sections`：目前仅 role/generator/document 查询再返回 metadata，无完整资格校验。 SHA256 `a40d54a36fe14fd0e76b322477885777ad2b3fa8b5263a2d8e726a2c63214f49`。

**必读原证据**

- [audit_review/2026-09-18_real_company_skill_audit/runs/03_zijin_fetch_reuse/stdout.txt](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/03_zijin_fetch_reuse/stdout.txt>)： 旧真实 bundle normalized/summary 无效的原原因
- [.planning/2026-09-19-three-project-history-audit/reviews/wiki_legacy/section_probe.py](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/wiki_legacy/section_probe.py>)： 纯 scratch 反例构造与硬编码路径/输出位置，禁止原地运行
- [.planning/2026-09-19-three-project-history-audit/reviews/wiki_legacy/section_probe.json](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/wiki_legacy/section_probe.json>)： failed/missing/wrong hash/nonexistent span 返回普通结果
- [../company-wiki/src/company_wiki/source_catalog/artifact_handle.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/artifact_handle.py>)： 字段/拒绝原因实际权威
- [../company-wiki/tests/contract/test_source_catalog_artifact_handle.py](<C:/Users/郑曾波/Projects/company-wiki/tests/contract/test_source_catalog_artifact_handle.py>)： 现有隔离 validator 回归，不等于 default producer 证据

**只允许修改**

- CW:src/company_wiki/source_catalog/section_query.py
- CW:src/company_wiki/source_catalog/section_extractor.py
- CW:src/company_wiki/source_catalog/source_bundle.py
- CW:src/company_wiki/source_catalog/artifact_handle.py
- CW:src/company_wiki/source_catalog/normalizer.py、llm_summarizer.py（仅复验证实仍有的 metadata/契约问题）
- 对应隔离默认 producer/consumer contract tests；不重建旧研究 writer 或 markdown producer

**固定样本**

- 一份小型已核验 annual 文本，含释义、主营业务和经营讨论三个明确区块；由真实 normalize/section producer 产出，不直接 INSERT 绿色 artifact 充当正例。
- 篡改用副本：status=failed/partial、缺文件、旧 schema/version、source_sha 不符、future created_at、不存在 span、多个同 role 版本。
- 旧紫金无效工件只作为历史副本迁移/失效输入，current producer 另用新样本证明。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W05A-P1 / positive**：默认 normalize→sections/适用 summary→默认 bundle 路径。
  预期：所需角色自产生后被同一 validator 接受；DB 字段与文件 hash/source 实际一致；不依赖 test-only registry。
- **W05A-N1 / negative**：上述无效字段逐项独立变异，特别 failed sections + 不存在文件/span。
  预期：sections 查询不能返回普通 usable 内容；保留拒绝原因及补产需求。
- **W05A-N2 / negative**：旧 failed/stale sections 行已存在，输入 normalized 合格。
  预期：不能只因 artifact_id 非空跳过；重算完成前旧行仍不可用。
- **W05A-N3 / negative**：同 role 新旧行混合，旧失败先插入，新合格后插入。
  预期：选择确定且依据有效版本/来源；不能靠 SQLite 未排序 first row。
- **W05A-P2 / positive**：raw-only 需求或 summary 对该文档不适用。
  预期：不为了 bundle 齐全强制 LLM/虚造 summary；状态区分 not_applicable 与 missing/failed。

**按序执行**

1. 冻结 D-W05 的字段与角色适用性；对当前新产物先复验，已有正确行为只补证，不重复修。
2. 把历史 section_probe 复制到本次 attempt 并显式重绑源码/输出；不覆写旧 JSON。
3. 接通 section 查询与默认 bundle 的同一资格门；校验 index 文件、内容、源/span 绑定和状态。
4. 修正 stale/failed 的重算选择；保存 producer 实际调用、文件及 artifact 行，重复请求验证复用。

**失败停止与恢复界限**

- 没有 source/span 来源证明的旧工件只能保持 invalid/重新生成，不得批量填 source_sha 使绿。
- normalizer 若较本卡 hash 已变化（已有并发修复先例），先归因版本再处理；禁止回滚他人修复。

入口：`CMD-W06`、`CMD-W07`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`default-producer-artifacts.json`、`artifact-mutation-matrix.json`、`section-index-span-checks.json`。

**退出判据**：适用的真实默认产物可消费，无效 section 无旁路；局部 helper/fixture 通过不能替代默认产物链。
