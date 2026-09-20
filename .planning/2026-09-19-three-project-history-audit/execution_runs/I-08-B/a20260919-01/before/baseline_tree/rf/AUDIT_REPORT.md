# Revenue Forecast 技能全面审计报告

审计日期：2026-07-26  
审计对象：`revenue-forecast` v3.10.0 / forecast schema 3.4，以及其与 `filing-fetch`、`invest-core`、`invest-framework` 和八个 leaf `invest-*` 技能的接口  
审计方式：契约逐条核对、实现调用链审查、静态检查、正常路径测试、跨技能测试和定向对抗性复现

## 一、结论摘要

总体结论：这是一个**业务建模能力强、正常路径测试充分、下游依赖边界较成熟，但形式化可信链仍存在关键语义缺口**的技能。

六个问题的直接答案如下：

| 问题 | 结论 | 评价 |
|---|---|---|
| 1. 是否足够模块化 | **逻辑模块化较好，物理模块化不足** | 模型注册、约束、报告、回测、CLI 已分离；但 `revenue_core.py` 约 2324 行、`filing_acquisition.py` 约 2080 行，职责过度集中 |
| 2. 模块是否足够泛化 | **业务层泛化强，部署层泛化中等** | 23 个模型按经济驱动而非公司分派；正式核心无公司分支。公司硬编码只出现在 Tencent/Microsoft 示例脚本；dayu 的 Windows 虚拟环境路径和相邻仓库拓扑仍偏硬 |
| 3. 步骤是否真正强制 | **结构性门禁强，程序性与语义性门禁不充分** | CLI 对输入、识别、三情景、bridge、capture 等有硬门；但若干步骤可用 `data_gap`/自报结果降级，且最终 output validator 存在已复现的概率、目标和敏感性伪造绕过 |
| 4. 是否优先复用本地文档 | **是，但当前复用的是文件树/sidecar，不是真正的 company-wiki 索引接口** | manager 顺序严格为 identity → local resolve → 缺口 → 授权 → 下载；能复用 canonical raw/sidecar，但可能漏掉只被 catalog 索引、未符合 sidecar 布局的资料 |
| 5. 是否复用下载工具并规范落库 | **功能上是，架构上存在双重实现** | CN 调 StockInfoDLSimple，HK/US 调 dayu；下载经 staging、hash、size、去重后写入 `companies/{entity}/raw/...`。但它与独立 `filing-fetch`/company-wiki catalog 重复实现同一能力 |
| 6. 与 invest-* 协同和重复情况 | **业务所有权和单向依赖良好；基础契约和文件获取重复** | `revenue → invest-core → leaf → framework` 落实较好，leaf 未重建收入；但 evidence/capture/hash 契约重复，filing acquisition 有两套 owner，上游 validator 缺口会被可信 reference 放大到 valuation/SOTP |

综合评分建议：

- 业务模型泛化与可扩展性：8.5/10
- 正常路径工程质量：8/10
- 强制工作流与抗绕过性：6/10
- 文档治理与可复用性：7/10
- invest-* 协同：8/10
- 当前作为“不可伪造正式预测工件”的可信度：5.5/10

在修复 Critical 项目前，不应把 `workflow_compliance_receipt.status="pass"` 理解为完整的、不可绕过的正式发布证明。

## 二、设计与架构审查

### 2.1 做得好的部分

1. `scripts/revenue_forecast.py` 是薄 CLI：读取输入、运行核心、调用独立 output validator、写 JSON/只读 Markdown renderer。
2. `scripts/model_registry.py` 以 frozen `ModelSpec`、`MappingProxyType` 和 immutable registry 管理模型；模型按 volume、capacity、subscriber、platform、bank、insurance、backlog、resource depletion 等经济机制选择，而不是按公司名选择。
3. 计算顺序明确并在实现中落实：modeled activity → revenue recognition → cross-segment constraints → company aggregation。
4. low/base/high 使用同一 segment 模型；识别时点、gross/net presentation、lag、carry-in、over-time progress 均有结构化约束。
5. 历史数据、base reconciliation、claim/capture、参数维度、derived fact、target ledger、driver tree 和 company bridge 不是纯提示词，而是实际 schema/validator。
6. `revenue_constraints.py`、`revenue_report.py`、`revenue_backtest.py` 和 `model_registry.py` 已形成清晰子域。
7. `invest-core` 的 revenue adapter 只复制 consolidated 或 segment `effective_revenue`，不重建收入公式；`invest-framework` 强制 identity、scenario、segment、constraint、financial、valuation、SOTP 全覆盖。

### 2.2 模块化不足

`revenue_core.py` 同时拥有：

- 顶层输入契约；
- sources、captures、claims、parameters；
- history/base reconciliation；
- segment 模型路径、识别、聚合；
- sensitivity、theme analysis、confidence；
- research coverage、growth-driver tree、management targets；
- workflow receipt。

这属于“函数层面模块化、文件和所有权层面未拆分”。建议拆成：

1. `contracts/evidence.py`
2. `contracts/document.py`
3. `forecast/segments.py`
4. `forecast/recognition.py`
5. `forecast/aggregation.py`
6. `research/coverage.py`
7. `research/drivers.py`
8. `research/targets.py`
9. `analysis/sensitivity.py`
10. `analysis/confidence.py`
11. `publication/finalizer.py`

`filing_acquisition.py` 也应拆为 config、identity、resolver、adapters、writer、manager；更优方案是删除其独立 owner 身份，改为调用统一的 `filing-fetch`/company-wiki catalog API。

### 2.3 泛化性

正式核心没有 Tencent、Microsoft 或其他公司的条件分支。唯一公司硬编码集中在 `scripts/run_forecasts.py`，它包含完整 Tencent/Microsoft 输入、claims、研究文字和输出名，且是唯一 Ruff 不洁净文件。它不被正式 workflow 引用，但放在 `scripts/` 容易被误认成生产入口，应移动到 `examples/` 或 fixtures。

正式核心只有一个模型特例：`retail_franchise` 的 `franchise_system_sales` 与 `recognized_fee_rate` 必须成对出现。该规则是跨字段 schema 约束，不是公司特例；不过最好由 registry spec 声明，而不是留在 core 条件分支。

部署泛化仍有两个问题：

- dayu command 写死 `.venv/Scripts/python.exe`，偏 Windows；
- 默认配置假设 company-wiki、dayu-agent、StockInfoDLSimple 是相邻项目目录。

## 三、强制性和检查点审查

### 3.1 强制性矩阵

| 步骤 | 当前强制程度 | 主要缺口 |
|---|---|---|
| 0 九维研究覆盖 | 结构硬门 | 九维可全部声明为 `data_gap`/`immaterial`；custom dimension 的 input/output 契约不一致 |
| 1 信息集冻结 | 强 | capture/hash/date 强；真实工具调用和资料完整性仍依赖 host |
| 1A 管理层沟通/目标 | 中强 | 六类别结构强；`not_available`/`not_applicable` 可自报，target mapping 与 scope/scenario 绑定弱 |
| 2 历史/base | 强 | 未知 base adjustment 可能抛 `KeyError`；重复 adjustment ID 未显式禁止 |
| 3 来源/参数/claim | 强结构、弱真实性 | self-reported `tool_call_id`/`manual_open` 无法证明工具调用；source-linked assumption 未强制 rationale-support |
| 4 收入曲线拆分 | 中 | segment/model schema 强；经济上是否拆得足够细无法自动证明 |
| 5 收入确认 | 强 | policy claim、timing、trigger、presentation、progress、lag 都有硬门 |
| 6 三情景 | 强结构 | 同模型、driver、rationale、顺序强；经济合理性不能机器验证 |
| 6A 因果驱动树 | 可降级 | 整棵树可设为 `data_gap` 后继续正式出数 |
| 7 聚合/bridge | 强 | model → recognition → constraints → company、bridge 和增量均重算 |
| 8 敏感性/theme | 弱至中 | sensitivity 可为空；遗漏 progress、constraint 和 derived-chain；output 不重跑 shock |
| 9 置信度 | 强计算 | 权重是启发式，且遗漏 constraint 参数 |
| 10 验证/交付 | CLI 强、函数路径可绕 | `run_forecast` 在 output validation 前签发 pass receipt |
| 11 冻结/回测 | 可选且有缺陷 | auto-name snapshot 自失效；同 schema 旧 engine 不兼容；actuals evidence 较弱 |

### 3.2 无法仅靠 schema 解决的边界

技能能够证明“用户提交了形状正确、哈希自洽的数据”，但无法仅凭用户提供的 JSON 证明：

- 指定工具真的被调用；
- 搜索已经穷尽；
- 页面内容没有在进入 hash 前被伪造；
- `not_available` 不是为了跳过研究；
- claim 在经济上真的支持参数。

若目标是防止调用工具的 agent 偷工减料，应把关键研究和下载步骤置于受控 orchestrator 中，并由 host 生成不可由模型填写的 tool-event receipt；正式 finalizer 只接受受信任执行环境签发的 receipt，而不是接受输入 JSON 中自报的 `tool_call_id`。

## 四、关键缺陷

### Critical-1：output validator 不是完整的独立语义重算器

已通过最小变异测试复现以下结果；每次都同步重算了 `result_sha256`：

1. 把概率改为 `{low: 2, base: 0, high: 0}`，并同步 weighted path，validator 通过。
2. 把管理目标值从 144 改为 1000、强制 `meets_target=true`，同步 ratio 后 validator 通过。
3. 把 sensitivity 的 down/up terminal 改为 1/999，同步 impact 后 validator 通过。
4. 在 `parameter_trace[0]` 嵌入结构化 `valuation=123`，validator 通过。

原因：

- output 侧只验证概率加权算术，没有重新执行输入概率契约；
- target 只验证存储值之间的算术，不重新执行 comparison/tolerance；
- sensitivity 只重算 impact，不重新运行 shock；
- prohibited investment-field scan 不是全树扫描，也没有区分“来源文本词汇”和“正式结构化投资结论”。

影响：`invest-core` 在建立 revenue reference 前信任此 validator，SOTP 又消费 `meets_target` 布尔值，因此伪造结果可以向 valuation/framework 传播。

### Critical-2：workflow pass receipt 签发过早

`run_forecast` 在 `validate_forecast_output` 之前就构造：

- `status="pass"`
- gate `output_recomputation`

正式 CLI 的下一步确实会调用 output validator，但 Python 调用者可以获得一个带 pass receipt 的、随后无法通过 output validation 的结果。custom-dimension 复现已经证明“receipt pass，正式 validator fail”可以同时发生。

建议拆成：

- execution receipt：输入契约和计算完成；
- publication receipt：独立 output validation 成功后，由 finalizer 最后签发。

只有 publication receipt 可以进入 invest-*。

### High-1：research custom dimension 契约自相矛盾

input validator 允许核心九维之外的 custom dimension，甚至当前允许 `dimension=null`；output validator 却要求列表长度必须等于九并严格按核心九维排列。

结果：输入可以被 `run_forecast` 接受，但正式 CLI 必然在 output validator 失败。此行为也与 changelog 对 custom dimension 的支持声明不一致。

### High-2：同一 schema 的历史 artifact 被 engine 精确版本锁死

当前 schema 3.4 output 必须 `engine_version == 3.10.0`。然而 v3.5–v3.10 均使用 schema 3.4；因此一个重新验哈无误的 3.9.0/schema-3.4 artifact 会被拒绝。snapshot validator 同样要求当前 engine。

这破坏 immutable forecast 和长期 backtest 的基本使用场景。兼容性应由 schema/contract capability 决定，而不是由当前技能 patch/minor 版本决定。

### High-3：sensitivity auto-name 会修改原始输入并使 snapshot 自失效

`calculate_sensitivities` 会原地给缺少 `name` 的测试字典补名；`run_forecast` 在此之前计算 input hash，`create_snapshot` 在运行后又对已变异输入计算 hash。

已复现：`create_snapshot` 成功返回，但紧接着 `validate_snapshot` 报 `forecast result input fingerprint mismatch`。

### High-4：存在检查器但未接入正式流程

`validate_source_coverage` 能识别 `covers_until` 早于预测参数期间，但它没有被 `validate_document`、`run_forecast` 或 confidence 消费。

已复现：把所有来源设为只覆盖 FY2025，FY2026–FY2027 正式预测仍通过。

另外，source-linked `analyst_assumption`/`scenario_stress` 只要求存在任意 linked claim，没有强制 `support_type="rationale_support"`；用 exact-value claim 替代也可通过。

### High-5：回测证据和口径不足

- actuals 的 source validation 未强制 capture receipt；
- actual claim 只有 content hash，未绑定 immutable capture/snapshot；
- segment evaluation 使用 `recognized_revenue`，而正式 company path 使用 constraints 后的 `effective_revenue`；
- accuracy record 可影响未来 confidence，因此证据弱点会进入未来正式输出。

### Medium-1：敏感性和置信度遗漏关键参数

sensitivity 的 referenced parameter 集合遗漏：

- over-time progress 参数；
- cross-segment constraint/cap/weight 参数；
- derived-chain 中的源 assumption。

confidence 的 revenue weights 同样遗漏 constraints，和 growth-driver helper 的覆盖口径不一致。

### Medium-2：本地文件获取有两个 owner

独立 `filing-fetch` 是 company-wiki `source_catalog identify/resolve/ensure` 的薄客户端；revenue v3.10 又内置约 2080 行自包含实现。

两边都处理 identity、reuse、authorization、market routing、dedup、provenance 和 canonical storage，而且技能说明对谁是首选 owner 存在冲突。这会导致 bug 修复、catalog 规则和 adapter 接口漂移。

### Medium-3：invest runtime 可能导入错误版本

`invest-core.revenue_runtime()` 把选定 skill 的 scripts 路径插入 `sys.path` 后执行 `import_module("revenue_core")`，但没有验证已加载 module 的 `__file__`。

若同一进程已经加载另一份同名模块，`sys.modules` 会静默复用错误版本。应使用显式 file spec/唯一模块名，或至少断言 resolved `__file__` 属于选定 skill。

### Low/工程质量

- 主测试运行时，dayu discovery success path 出现 2 个未关闭 stdout/stderr pipe 的 `ResourceWarning`。
- `validate_base_reconciliation` 对未知 adjustment ID 可能抛 `KeyError`，而非受控 `ForecastInputError`。
- `.agents` 安装副本与 canonical 38 个文件完全一致；技能目录中另一条 `.codex` locator 实际不存在，属于本机 catalog/安装状态漂移，不是本仓库代码缺陷。

## 五、公司文档复用与下载链路

### 5.1 当前实际顺序

`FilingAcquisitionManager` 实现的顺序正确：

1. 解析/确认公司身份；
2. 在 `${company_wiki_root}/companies/{entity}/**/*.source.json` 和 alias sidecar 中查找；
3. 校验 canonical path 在 root 内、文件存在、hash 和 size 一致；
4. 命中则直接复用；
5. 未命中且未授权下载则 hard fail；
6. 只有显式 `allow_download` 才调用 market adapter；
7. staging 后验证 hash/size；
8. exact-hash 去重；
9. 原子写入 `companies/{safe_entity}/raw/<kind>/...` 和 immutable `.source.json`。

### 5.2 市场路由

- CN：通过 StockInfoDLSimple 的 versioned structured JSON CLI，`shell=False`；
- HK/US：通过 dayu CLI；
- 不从搜索结果页直接伪造 filing URL；
- 下载先进入临时 workspace，不直接写 canonical raw。

### 5.3 需要调整的地方

严格回答“是否优先查找本地公司文档索引”：当前答案是**文件系统复用优先，但不是真正 catalog/index 优先**。

建议只保留一个 acquisition owner：

1. company-wiki `source_catalog` 负责 identity、resolve、ensure 和 canonical write；
2. `filing-fetch` 作为跨技能薄客户端；
3. revenue 和所有 invest-* 只调用 filing-fetch；
4. 若需要 revenue 专用输出，保留 adapter，不复制 acquisition 实现。

## 六、与 invest-* 的协同性

### 6.1 良好部分

依赖方向清晰且实现基本一致：

```text
revenue-forecast
  → invest-core immutable revenue reference
  → invest-financials / moat / management / distribution
  → invest-valuation
  → invest-sotp / invest-compare
  → invest-framework orchestration
```

- financials 消费收入，不创建第二套收入预测；
- moat 引用 driver，不重排收入；
- management 不重复资本分配计算；
- distribution 不做估值；
- valuation 不重建 revenue/profit；
- SOTP 只聚合已验证 segment valuation；
- compare 只对齐并比较已验证 artifact；
- psychology 在基本面 DAG 之外。

framework 还强制：

- identity 与 frozen forecast 完全一致；
- required constraint IDs 与 revenue constraints 一致；
- segments 必须逐一且只覆盖一次；
- low/base/high scenario manifest 唯一；
- 每个 segment 必须有 financial + valuation；
- SOTP selection/ownership 覆盖全部 segment；
- bundle 的 revenue reference 精确等于 frozen forecast reference。

### 6.2 重复和接口缺口

没有发现 leaf 技能重建第二套收入公式。重复主要在基础设施：

1. revenue 与 invest-core 各自实现 canonical hash、restricted formula、URL/source/claim/parameter 验证；
2. revenue filing acquisition 与 filing-fetch/company-wiki catalog 双实现；
3. scenario manifest 只保证 low/base/high 名称和文本定义一致，没有机器映射 revenue 内具体假设；
4. invest-core 只复制 target/driver summary，不能弥补 revenue validator 的语义缺陷。

建议把 evidence/capture/hash/formula contract 下沉为一个真正共享、版本化的包；revenue 和 invest-* 只通过 immutable adapter 使用。

## 七、测试与质量基线

实际运行结果：

| 范围 | 结果 |
|---|---:|
| revenue 主测试 | 158/158 通过 |
| revenue 安装/同步工具测试 | 4/4 通过 |
| invest-core | 29/29 通过 |
| invest-framework | 22/22 通过 |
| 8 个 leaf invest-* | 55/55 通过 |
| 合计 | **268/268 通过** |

其他检查：

- `python -m compileall -q scripts tests tools`：通过；
- 正式核心 Ruff：通过；
- 全量 Ruff：只有 `scripts/run_forecasts.py` 4 个示例脚本问题；
- revenue 主 suite statement coverage：84%；
- `revenue_core.py` 96%、constraints 96%、registry 89%、backtest 88%、report 85%、filing acquisition 77%。

重要判断：高 statement coverage 没有发现本次 mutation/adversarial 测试复现的语义绕过。下一阶段应优先增加对抗性契约测试，而不是只追求更高行覆盖率。

## 八、修复优先级与验收检查点

### P0：正式工件可信链

1. 把 publication receipt 移到 output validation 之后签发。
2. output validator 从 frozen input/parameter trace 独立重建：
   - scenario probability 契约与 weighted path；
   - target comparison/tolerance/meets_target；
   - 每个 sensitivity shock；
   - prohibited structured field 的全树策略。
3. invest-core 只接受 publication receipt。

验收：对概率、目标、敏感性、嵌套 valuation 的四类 mutation 全部 hard fail。

### P1：契约一致性和可追溯性

1. 统一 custom research dimension 的 input/output schema，并拒绝非字符串 dimension。
2. 以 schema/capability matrix 管理历史 artifact，而不是要求当前 engine 精确相等。
3. sensitivity 只操作 deepcopy，修复 snapshot 自失效。
4. 把 source horizon checker 接入 formal validation。
5. source-linked assumption 强制 rationale-support。
6. actuals 强制 immutable capture，并以 `effective_revenue` 作为受约束 segment 回测口径。

验收：本报告中的 custom dimension、source horizon、exact-value assumption、old-engine、auto-name snapshot 复现全部转为预期行为。

### P2：所有权和模块化

1. 统一 filing owner 到 company-wiki catalog/filing-fetch。
2. 拆分两个超大模块。
3. 共享 evidence/capture/hash/formula contract。
4. 修复 invest-core 安全导入。
5. 把 Tencent/Microsoft 示例移到 `examples/`。
6. 关闭 dayu subprocess pipes，并为 timeout、cleanup、partial write 增加测试。

### P3：防止研究流程偷步

1. 对 driver tree 的 `data_gap` 降级设置正式发布阈值或显式 exception approval。
2. 对 management communication 的 `not_available` 保存机器生成的查询日志。
3. 敏感性至少覆盖所有 material Base 参数，或由批准的 exclusion ledger 解释。
4. tool-event receipt 由 host 签发，禁止模型自填。

## 九、最终判断

`revenue-forecast` 已经不是一个松散提示词技能，而是一个相当完整的、跨行业的收入预测运行时。它最强的部分是模型注册、收入确认、情景一致性、约束后聚合以及与 invest-* 的单向职责边界。

它当前最大的风险不是“没有检查”，而是**若干检查只验证结果内部自洽，没有重新验证结果与冻结输入之间的真实语义关系**；与此同时，pass receipt 又在最终验证之前签发。这两个问题叠加，使正式工件的可信声明强于实际保证。

因此建议结论为：

- 可以继续作为研究和建模主干使用；
- 在 P0/P1 修复前，不应把 receipt 当作防篡改、不可绕过的发布证明；
- 文档获取功能正确但应尽快收敛到唯一 filing owner；
- invest-* 业务边界无需重构，重点应放在共享基础契约、版本兼容和上游 validator 加固。
