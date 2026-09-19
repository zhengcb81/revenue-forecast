本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-05-C — 按需求执行最小补产并如实计调用次数

parent：I-05；status：planned；owner：wiki producer 单一 owner + RF consumer_analysis owner。

依赖：I-05-B、I-06-B。设计前置：D-W05。证据目录：`execution_runs/I-05-C/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [company-wiki/src/company_wiki/source_catalog/artifact_dag.py:10](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/artifact_dag.py:10>) `ROLE_DEPENDENCIES`：当前 summary→markdown→normalized 与冗余 markdown producer 退役冲突；必须先冻结活动 DAG 兼容。 SHA256 `13e02211ca9f6eef251acd33c1be75db3112d1e4a7acf0b3739b23c955fbf505`。
- [revenue-forecast/scripts/company_wiki_source.py:147](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/company_wiki_source.py:147>) `select_artifact_roles`：当前 missing 的下游闭包可能含消费者未请求角色；计划不是已调用。 SHA256 `aeeb7b2a63047c73eac3a9806ac0c426e645e9aa87da85606cab78770b039ff0`。
- [company-wiki/src/company_wiki/source_catalog/normalizer.py:1646](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/normalizer.py:1646>) `normalize_catalog`：现有 producer，不新增重复 parser。 SHA256 `772075ed0d1c540aeb2a0feea17d7735a28c0aba981edfbdefa7297a57a06cff`。
- [company-wiki/src/company_wiki/source_catalog/section_extractor.py:283](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/section_extractor.py:283>) `extract_sections_catalog`：补产必须处理已存在失败状态。 SHA256 `b59ce324d3481e790acd92d96b2b662d94d5ab7ddf60e896658dfa8bb055406b`。
- [company-wiki/src/company_wiki/source_catalog/llm_summarizer.py:514](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/llm_summarizer.py:514>) `LLM summary artifact INSERT`：产物行只证明产物，不包括失败尝试/重试调用次数。 SHA256 `a930a42e04d52a47e8469be346c92eb58dfe604332d6a7708edaf94ad9fa4ade`。

**必读原证据**

- [../company-wiki/src/company_wiki/source_catalog/artifact_dag.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/artifact_dag.py>)： 旧图与 invalidation/current schema
- [scripts/company_wiki_source.py](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/company_wiki_source.py>)： closure 与 ancestors 的实际用法
- [.planning/2026-09-19-three-project-history-audit/reviews/wiki/review.md](<C:/Users/郑曾波/Projects/revenue-forecast/.planning/2026-09-19-three-project-history-audit/reviews/wiki/review.md>)： producer 冗余退役与工程上下文边界
- [../company-wiki/src/company_wiki/source_catalog/service.py](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/service.py>)： 实际 normalize/summarize/extract_sections 入口；逐项验证存在

**只允许修改**

- CW:src/company_wiki/source_catalog/artifact_dag.py
- CW:src/company_wiki/source_catalog/service.py（按需求调用现有 producer）
- CW:src/company_wiki/source_catalog/processing_demand.py
- RF:scripts/company_wiki_source.py
- RF:scripts/source_preparation.py
- D-W05 指定的现有 producer 调用边界/事件文件；RF consumer_analysis 对应 owner 文件须先列精确路径
- 对应隔离调用计数及 DAG tests

**固定样本**

- 已冻结新活动 DAG：normalized→summary、normalized→sections、summary→consumer_analysis；历史 markdown 只兼容而不补产。
- 分别请求 normalized-only、sections-only、summary-only、consumer_analysis；每组单独变更 source/producer 版本或缺适用 role。
- 受控 LLM 假服务用于故障/计数（明确 test double），默认真实 provider 能力另验；没有模型能力则真实 summary case blocked，不假称已验证。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W05C-P1 / positive**：sections-only 且 normalized 合格、sections 缺失。
  预期：只调用 sections producer 1 次、parser=0/LLM=0；读到新 sections；第二次 producer=0。
- **W05C-P2 / positive**：summary-only，source/normalized 合格但 summary 失效。
  预期：不重解析 raw、不产 markdown/sections/consumer_analysis；summary 按适用已批准方法产生并被实际读。
- **W05C-N1 / negative**：原件 hash 改变。
  预期：全部旧绑定失效，但只重建本请求必需祖先/角色；不复用旧安全审核。
- **W05C-N2 / negative**：LLM 第一次失败第二次成功，或 parser 失败未产 artifact。
  预期：真实调用 attempts=2 或失败 parser=1，不以 artifacts INSERT 数=1/0 充当调用次数。
- **W05C-N3 / negative**：无适用 producer/无 credentials/unsupported 文档。
  预期：返回明确 missing/unsupported/not_applicable 区分；不插 completed 占位、不调用退役 writer。
- **W05C-N4 / negative**：summary 变化但 normalized/sections 输入未变。
  预期：已有 normalized/sections 仍有效；consumer_analysis 失效只在其被请求时补产。

**按序执行**

1. D-W05 先定活动 DAG 和版本迁移，移除对退役 markdown producer 的隐式需求，不能另建一套 RF 图。
2. 计算所需角色及必要祖先，失效闭包与本请求需生成集合分开；不盲补所有下游。
3. 用 I-06 的批准消费路径调用现有 producer；在实际调用边界记录成功/失败/重试事件，不从结果表倒推。
4. 读取新产物走 I-05-B，原 request 再跑证明复用零补产；独立核对调用 trace。

**失败停止与恢复界限**

- 缺 consumer_analysis 真实 owner 入口或 LLM 能力就阻断对应角色；不造绿色样例补全。
- 产物半完成保留 failed/partial，并按 DAG 重算受影响部分；不把 failure 全库 force 重跑。

入口：`CMD-W06`、`CMD-W09`、`CMD-W05`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`requested-role-dag-matrix.json`、`producer-invocations.json`、`retry-count-vs-artifact-count.json`、`second-reuse.json`。

**退出判据**：需求、实际补产、实际读取和独立计数闭合；hermetic 假服务不等于真实 LLM/投资研究质量已通过。
