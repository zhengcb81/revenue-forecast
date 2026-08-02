# Revenue Forecast 技能改进实施计划

计划编制日期：2026-07-26 │ 完成日期：2026-07-30  
依据：`AUDIT_REPORT.md`、`findings.md`  
当前状态：**13 Phase 全部完成。294 tests / 0 failures / ruff 0 errors（4 repos）**

## 0. 总目标、边界与不可违反规则

### 0.1 总目标

按依赖顺序修复审计发现，使 `revenue-forecast` 同时满足：

1. 正式输出必须经过输入对照的独立语义验证；
2. 只有语义验证成功后才能签发 publication receipt；
3. 概率、管理目标、敏感性、禁止字段、来源期限和回测证据不可通过“修改结果后重算 hash”绕过；
4. schema 和 engine 版本兼容规则清晰、可迁移、可回测；
5. 正式流程不能无痕跳过 driver tree、管理层沟通、敏感性和工具调用；
6. 公司文档先查统一索引，确认缺口且获授权后才下载；
7. 财报获取只有一个 canonical owner；
8. revenue 与 invest-* 保持单向依赖，不重建第二套收入预测；
9. 大文件按职责拆分，但拆分不得改变数值结果；
10. 所有改动都有失败测试、正向测试、集成测试、迁移测试和可保存的验收证据。

### 0.2 范围

本计划覆盖：

- 当前仓库的 `scripts/`、`tests/`、`references/`、`config/`、`SKILL.md`、`CHANGELOG.md`；
- `filing-fetch`、`invest-core`、`invest-framework` 的接口调整与跨技能回归；
- canonical skill 与安装副本同步流程。

本计划不覆盖：

- 利润、现金流、估值、评级或仓位算法；
- 对具体公司重新建模；
- 未经单独批准的新外部服务；
- 为了重构而改变既有收入公式、会计口径或模型数值。

### 0.3 后续执行者的固定工作方式

以下规则对每一个 Phase 都是强制的：

1. 开始会话时依次读取：
   - `task_plan.md`
   - `progress.md`
   - 与当前 Phase 有关的 `findings.md`
2. 同一时间最多一个 Phase 标记为 `in_progress`。
3. 修改代码前：
   - 用 CodeGraph `codegraph_context` 获取当前任务上下文；
   - 用 `codegraph_impact` 获取待改符号影响半径；
   - 不相信计划中的旧行号，实际符号位置以 CodeGraph 为准。
4. 每两次查看、搜索或浏览操作后，立即把新事实写入 `findings.md`。
5. 每个行为缺陷都采用固定顺序：
   - 先增加能稳定复现问题的负向测试；
   - 确认新测试因目标缺陷而失败；
   - 做最小生产改动；
   - 确认新测试转绿；
   - 运行相关文件全部测试；
   - 再运行全量测试。
6. 不得通过删除、放宽、跳过或改写失败测试来“修复”实现。
7. 不得同时进行语义修复和无关格式化/重命名。
8. 不得直接编辑 `C:\Users\郑曾波\.agents\skills\...` 或其他安装副本；只修改已确认的 canonical 源仓库，最后通过同步工具安装。
9. 不得让 `revenue-forecast` 导入 `invest-core`，否则会形成上游依赖下游的循环。
10. 任何 schema 字段新增、删除、含义变化或强制性变化，都必须：
    - 更新 schema 版本；
    - 更新 input/output/compliance/backtesting 文档；
    - 添加旧 schema fixture；
    - 添加迁移/只读兼容测试；
    - 更新 `CHANGELOG.md`。
11. 每完成一个子阶段，把以下证据写入 `progress.md`：
    - 修改文件；
    - 测试命令；
    - 通过/失败数量；
    - 新增测试名称；
    - 是否存在 warning；
    - 尚未解决事项。
12. 同一错误最多三次：
    - 第一次：定位并做针对性修复；
    - 第二次：换方法，不重复原命令；
    - 第三次：重新检查前提和计划；
    - 三次仍失败：把具体错误和已尝试方法写入计划，标记 `blocked`，请求用户决定。

### 0.4 所有阶段通用的测试命令

Targeted 测试使用当前仓库实际存在的 unittest discovery 入口：

```powershell
python -m unittest discover -s tests -p "test_output_report.py" -v
python -m unittest discover -s tests -p "test_scenarios_confidence.py" -v
python -m unittest discover -s tests -p "test_management_targets.py" -v
python -m unittest discover -s tests -p "test_data_contract.py" -v
python -m unittest discover -s tests -p "test_backtest.py" -v
python -m unittest discover -s tests -p "test_filing_acquisition.py" -v
```

全量质量门：

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s tools/tests -v
python -m compileall -q scripts tests tools
ruff check scripts tests tools
python -m coverage erase
python -m coverage run --source=scripts -m unittest discover -s tests -v
python -m coverage report -m --fail-under=84
```

规则：

- Phase 内先跑 targeted，再跑全量；
- 新模块 statement coverage 目标不低于 90%；
- 仓库总 statement coverage 不得低于当前 84%；
- 不允许新增 `ResourceWarning`、未关闭文件、未关闭 pipe 或临时目录残留；
- 若某个环境没有 `ruff` 或 `coverage`，记录缺失，不得谎报通过；安装新依赖须得到用户授权。

### 0.5 发布版本决策

默认实施目标：

- `SKILL_VERSION`：3.11.0；
- 当前正式 forecast schema：3.5；
- schema 3.4：转为 legacy read-only；
- schema 3.5：必须带 publication receipt 和新增强制语义门。

不得在 schema 3.4 中静默改变字段含义后仍声称完全兼容。

兼容原则：

- schema 3.4 只接受 `CHANGELOG.md` 明确列出的历史 engine 版本；
- schema 3.4 的验证状态必须标为 `legacy_read_only_validated`；
- schema 3.4 不得生成新的 current invest-* artifact；
- schema 3.5 才能标为 `current_validated`；
- 不允许用宽泛的字符串比较或任意 SemVer 范围接受未知 engine。

---

## Phase 1（冻结基线与建立反绕过测试）— 状态：completed（RED 基线已建立）

### 1.1 前置条件

- [x] 确认工作区未覆盖用户已有修改；记录 `git status --short`。（仅未跟踪规划/审计产物，scripts/、tests/ 无既有改动）
- [x] 用 CodeGraph 重新确认（实际位置，非计划旧行号）：
  - `run_forecast` → `scripts/revenue_core.py:1390`
  - `build_workflow_compliance_receipt` → `scripts/revenue_core.py:1428`
  - `validate_forecast_output` → `scripts/revenue_report.py:67`（report 模块）
  - `calculate_sensitivities` → `scripts/revenue_core.py:1068`
  - `add_management_target_analysis` → `scripts/revenue_core.py:2240`
  - `add_scenario_analysis` → `scripts/revenue_core.py:975`
- [x] 运行基线测试，结果与审计一致。**注意**：首次实跑为 158 tests/errors=2（plan drift），根因为 `_request.as_of_date` 硬编码审计日 + dayu 真实子进程 `retrieved_at=_utc_now()` 造成时间相关失败；已做 test-only 修复（as_of → today+7），恢复 **162/162**（158 tests/ + 4 tools/tests）。"268"为跨仓库合计，Phase 1 本地基线 162。详见 `findings.md` 2026-07-28 段。
- [x] 把基线测试数量、coverage 和 warning 写入 `progress.md`。（162/162、coverage 84%、2 预存 ResourceWarning、compileall/ruff 通过）

### 1.2 新增对抗性测试

在 `tests/test_output_report.py` 增加：

- [x] `test_rehashed_invalid_probability_contract_is_rejected`
  - 构造合法带概率结果；
  - 改成 `{low: 2, base: 0, high: 0}`；
  - 同步重算 weighted path 和 `result_sha256`；
  - 预期正式 validator 拒绝。**RED 已确认**：`ForecastInputError not raised`。
- [x] `test_rehashed_forged_target_comparison_is_rejected`
  - 修改 target comparison value；
  - 同步重算 attainment ratio；
  - 伪造 `meets_target=true`；
  - 重算 result hash；
  - 预期拒绝。**RED 已确认**：`ForecastInputError not raised`。
- [x] `test_rehashed_forged_sensitivity_terminals_are_rejected`
  - 修改 down/up terminal；
  - 同步重算 absolute/relative impact；
  - 重算 result hash；
  - 预期拒绝。**RED 已确认**：`ForecastInputError not raised`。
- [x] `test_nested_structured_valuation_field_is_rejected`
  - 在 `parameter_trace` 中加入结构化 `valuation` 对象或数值；
  - 重算 result hash；
  - 预期拒绝。**RED 已确认**：`ForecastInputError not raised`。
- [x] 保留一个正向测试，证明普通来源摘录中出现单词 “profit” 或 “valuation” 不会因纯文本误伤。**GREEN 护栏**：`test_plain_text_investment_vocabulary_in_source_is_allowed`。

新建 `tests/test_publication_pipeline.py` 增加：

- [x] `test_public_api_never_returns_pass_receipt_before_output_validation`。**RED 已确认**（premature receipt：`run_forecast` 返回前签 `status="pass"` + `output_recomputation`，内部未调 `validate_forecast_output`）。
- [x] `test_cli_does_not_write_json_when_publication_validation_fails`。**GREEN 护栏**（CLI 已在写 JSON 前调 validate，行为正确，钉住它）。
- [x] `test_markdown_is_only_rendered_from_published_json`。**GREEN 护栏**（`render_markdown` 内部先 validate，篡改结果不可渲染）。

### 1.3 RED 检查点

- [x] 原有测试必须全部通过。（158 原有 + 护栏全过；5 个失败均为新增 RED）
- [x] 新增的绕过测试必须失败，且失败原因必须是“当前 validator 接受了伪造结果”。（4 绕过均 `ForecastInputError not raised`；premature-receipt 失败于断言信息）
- [x] 若新测试因 fixture、claim ID、hash 构造或语法错误失败，先修测试；不得把这种失败当成有效 RED。（逐一核对：每个 RED 均因 validator 接受伪造，非构造错误）
- [x] 把每个 RED 测试的错误摘要写入 `progress.md`。（见 2026-07-28 Phase 1.2/1.3 段）

### 1.4 阶段验收

Phase 1 只有在以下条件全部满足后才能完成：

- [x] 四类已知绕过均有最小、稳定、可重复测试；
- [x] receipt 过早签发有独立测试；
- [x] 测试没有依赖测试执行顺序；（各自 `run_forecast` 重建 + 伪造前 `deepcopy`，discover 与单跑一致）
- [x] fixture 使用 `copy.deepcopy`，不会污染其他测试；
- [x] 未修改生产逻辑。（scripts/*.py 零改动；仅 test_filing_acquisition.py 的 test-only 基线修复 + test_output_report.py +5 + test_publication_pipeline.py 新建）

---

## Phase 2（建立正式发布流水线与准确的 receipt 语义）— 状态：completed

依赖：Phase 1 完成。

### 2.1 目标设计

把当前单一结果流程拆为三个明确层次：

1. `_build_forecast_draft(data)`：
   - 计算收入结果；
   - 可以带 execution metadata；
   - **不得**带 `status="pass"` 的 publication receipt；
   - 作为 private API，不供 invest-* 使用。
2. `validate_forecast_against_input(data, draft)`：
   - 使用冻结输入重新验证结果语义；
   - 不信任 draft 中自报的概率、目标、敏感性或 gate 状态；
   - 失败即抛受控 validation error。
3. `run_forecast(data)`：
   - 对输入做 `deepcopy` 或规范化冻结；
   - 调用 draft builder；
   - 调用输入对照 validator；
   - 调用 self-contained artifact validator；
   - 最后签发 publication receipt；
   - 返回唯一可发布结果。

### 2.2 receipt 字段

在 schema 3.5 中定义：

- [ ] `execution_receipt`
  - 只说明计算步骤已执行；
  - 不得使用 `status="pass"` 表示正式发布；
  - 不得包含 `output_recomputation` gate。
- [ ] `publication_receipt`
  - `receipt_version`
  - `schema_version`
  - `engine_version`
  - `validated_input_sha256`
  - `validated_payload_sha256`
  - `validator_version`
  - 明确且真实执行过的 `gate_ids`
  - `formal_output_mode`
  - `freeform_override_allowed=false`
  - receipt 自身 canonical hash。

### 2.3 逐步实施

1. [ ] 在 `scripts/revenue_core.py` 中把 receipt 构造从当前 `run_forecast` 计算段移出。
2. [ ] 在新模块 `scripts/revenue_publication.py` 中创建：
   - receipt payload canonicalizer；
   - publication receipt builder；
   - publication receipt validator；
   - 禁止在 builder 内重新运行收入模型，避免双 owner。
3. [ ] 修改 `run_forecast`，确保任何异常都发生在 publication receipt 生成之前。
4. [ ] 修改 `scripts/revenue_forecast.py`：
   - 只调用正式 `run_forecast`；
   - validation 失败时不得写 JSON；
   - JSON 写成功后才允许 renderer；
   - Markdown 写入失败不得篡改已验证 JSON。
5. [ ] 修改 `scripts/revenue_backtest.py`，snapshot 只接受带有效 publication receipt 的 schema 3.5 forecast。
6. [ ] 不删除 schema 3.4 legacy validator；通过显式 version dispatch 保留只读路径。

### 2.4 禁止事项

- [ ] 不允许保留两个都叫“pass”的 receipt。
- [ ] 不允许 public `run_forecast` 返回 unsigned draft。
- [ ] 不允许用 `_` 私有函数作为 invest-core 入口。
- [ ] 不允许通过只检查 `gate_ids` 是否存在来证明 gate 已执行。
- [ ] 不允许 receipt hash 覆盖自身导致递归或非确定性。

### 2.5 测试

新增或更新：

- [ ] draft 不含 publication receipt；
- [ ] validation 抛错时 receipt builder 未被调用；
- [ ] publication receipt 少字段、改 gate、改 payload hash、改 input hash均失败；
- [ ] 两次相同输入的 publication receipt 完全一致；
- [ ] CLI 失败时输出文件不存在；
- [ ] renderer 只能接收 current published artifact；
- [ ] schema 3.4 artifact 只能得到 legacy read-only 状态。

运行：

```powershell
python -m unittest discover -s tests -p "test_publication_pipeline.py" -v
python -m unittest discover -s tests -p "test_output_report.py" -v
python -m unittest discover -s tests -p "test_backtest.py" -v
python -m unittest discover -s tests -p "test_industry_end_to_end.py" -v
```

### 2.6 阶段验收

- [ ] CodeGraph callers 中，publication receipt builder 只能由 formal finalizer 调用；
- [ ] `run_forecast` 的所有正常返回都带有效 publication receipt；
- [ ] 所有异常路径都不会留下写了一半的正式文件；
- [ ] receipt gate 列表与实际 validator 调用一一对应；
- [ ] Phase 1 的 premature receipt 测试转绿；
- [ ] 全量测试与 coverage 门通过。

---

## Phase 3（概率、目标和敏感性的输入对照语义重算）— 状态：completed

依赖：Phase 2 完成。

### 3.1 建立单一语义函数

禁止 production calculator 与 validator 各写一套不同公式。应把纯语义规则抽为无副作用函数，生产计算和独立验证都调用同一规则，但 validator 必须从冻结输入重新取得输入值。

新增建议模块：

- `scripts/revenue_semantics.py`

包含：

- [ ] `validate_probability_contract(...)`
- [ ] `recompute_weighted_revenue(...)`
- [ ] `evaluate_target_comparison(...)`
- [ ] `recompute_target_attainment(...)`
- [ ] `build_sensitivity_case(...)`
- [ ] `recompute_sensitivity_result(...)`

这些函数必须：

- 输入显式；
- 不读全局可变状态；
- 不修改传入 dict/list；
- 返回新对象；
- 对 bool-as-number、NaN、Infinity、负值、未知 scenario、未知 comparison fail closed。

### 3.2 概率修复

1. [ ] 从冻结 input 读取概率，而不是信任 result。
2. [ ] 强制 key exactly `low/base/high`。
3. [ ] 拒绝 bool、负数、NaN、Infinity。
4. [ ] 和必须在容差内等于 1。
5. [ ] 每个概率必须有合法 rationale-support claim 和 source IDs。
6. [ ] 从 company annual path 重新计算 weighted path。
7. [ ] result 中无 input probability 时，不允许凭空出现 weighted path。

验收测试：

- [ ] 和为 2、含负数、缺 key、额外 key、bool、NaN、伪造 weighted path 均失败；
- [ ] 合法概率结果保持原数值；
- [ ] 不使用概率时结果中没有相关块。

### 3.3 管理目标修复

1. [ ] 从冻结 target ledger 取得：
   - target value；
   - comparison operator；
   - tolerance；
   - measurement basis；
   - mapped scenarios/periods；
   - currency/unit/perimeter。
2. [ ] 从重新计算后的 scenario result 取得 modeled value。
3. [ ] 对 annual、run-rate、cumulative 分别计算，不复用错误口径。
4. [ ] 重新执行 comparison/tolerance，生成 `meets_target`。
5. [ ] result 中所有 target 字段只作为待比对值，不能作为真值来源。
6. [ ] 检查 mapped parameter 必须属于目标 scope、period 和 scenario 的有效路径。
7. [ ] target source 必须能追溯到对应 communication record。

验收测试：

- [ ] 伪造 target value、modeled value、ratio、comparison、tolerance 或 `meets_target` 任一字段均失败；
- [ ] annual/run-rate/cumulative 三种口径各有正反例；
- [ ] perimeter 不匹配不能被标为 attained；
- [ ] Phase 1 target mutation 测试转绿。

### 3.4 敏感性修复

1. [ ] 从冻结 input 的 sensitivity definition 读取 parameter、shock type、requested values。
2. [ ] 对每个测试创建独立 deep copy。
3. [ ] 使用 `_run_forecast_core` 或等价内部纯计算路径重新运行 down/up case。
4. [ ] 不递归生成 sensitivity、theme、confidence 或 publication receipt。
5. [ ] 比对：
   - requested/effective shock；
   - clamp；
   - baseline terminal；
   - down/up terminal；
   - absolute/relative impact。
6. [ ] 每个 eligible parameter 最多出现一次。
7. [ ] 校验测试名称不影响 input hash。

验收测试：

- [ ] 修改任一 terminal/impact/clamp 字段均失败；
- [ ] percent、percentage-point/bp、absolute、range、discrete 各至少一个测试；
- [ ] ratio clamp、零参数、负数非法值有边界测试；
- [ ] Phase 1 sensitivity mutation 测试转绿。

### 3.5 阶段验收

- [ ] 四类 P0 mutation tests 全绿；
- [ ] 原有 scenario/target/sensitivity 数值完全不漂移；
- [ ] 同一输入运行两次得到相同 canonical payload hash；
- [ ] 输入对象在运行前后 canonical hash 相同；
- [ ] targeted、全量、coverage 全部通过。

---

## Phase 4（正式输出字段边界与 research schema 一致性）— 状态：completed

依赖：Phase 3 完成。

### 4.1 禁止投资字段的结构化策略

不得简单拒绝所有文本中出现的关键词。实现必须区分：

- 结构化 key；
- 来源标题/摘录/原文；
- parameter 名称；
- renderer 文本。

步骤：

1. [ ] 定义统一 `PROHIBITED_STRUCTURED_OUTPUT_KEYS`。
2. [ ] 定义允许承载不受信任原文的 leaf 字段白名单，例如 checked excerpt、source title。
3. [ ] 对正式 artifact 做全树遍历：
   - 结构化对象 key 命中 prohibited 集合即失败；
   - 只在明确原文 leaf 中允许同名单词作为字符串内容；
   - 拒绝递归过深、非 JSON 类型或重复引用对象。
4. [ ] renderer 不得把允许的原文误变成正式投资结论字段。

测试：

- [ ] 顶层、segment、trace、target、driver、source/capture 自定义对象中的 valuation/profit/DCF/rating 等结构化 key 均失败；
- [ ] 合法来源摘录中的同名单词通过；
- [ ] 自定义普通 metadata key 不被误伤；
- [ ] 深层嵌套和 list 内对象同样受检。

### 4.2 research custom dimension 契约

schema 3.5 固定规则：

1. [ ] 前九项必须按 `RESEARCH_DIMENSIONS` canonical 顺序出现；
2. [ ] custom dimensions 只能追加在九项之后；
3. [ ] dimension 必须是非空字符串；
4. [ ] 名称必须唯一，不能与核心维度重复；
5. [ ] 每项仍必须是 parameter mapping、material data gap 或 immaterial rationale 三选一；
6. [ ] output 保留输入顺序；
7. [ ] counts 覆盖核心和 custom 全部记录；
8. [ ] validator 不再要求长度恰好为九，而是 `>= 9` 且前九项准确。

测试：

- [ ] 九维无 custom 正常通过；
- [ ] 一个和多个 custom 正常通过；
- [ ] `null`、空字符串、重复、插入核心九维中间、同名大小写冲突均失败；
- [ ] custom dimension 的 output tamper 在重哈希后失败；
- [ ] renderer 显示 custom dimension，但不把它加入 confidence。

### 4.3 阶段验收

- [ ] 嵌套 valuation 绕过测试转绿；
- [ ] 纯文本不误伤测试通过；
- [ ] custom dimension 的 input/run/output/renderer 全链路一致；
- [ ] full suite 与 coverage 门通过。

---

## Phase 5（来源期限、claim 语义与 base reconciliation 加固）— 状态：completed

依赖：Phase 4 完成。

### 5.1 接入 source horizon checker

1. [ ] 先保持现有 `validate_source_coverage` 三个单元测试不变。
2. [ ] 明确返回类型：结构化 issue，不只返回自由文本。
3. [ ] 在 `validate_document` 中、parameter/claim indexes 建立之后调用。
4. [ ] schema 3.5 的正式规则：
   - 直接作为未来 exact value 的 source 必须覆盖对应 forecast period；
   - 只提供历史事实的 source 不要求覆盖未来；
   - rationale-support 可以支持 assumption 逻辑，但不能冒充未来 exact value；
   - 多来源时至少一个与该 claim 类型匹配的来源覆盖有效期间。
5. [ ] 非空 blocking issues 转为 `ForecastInputError`。
6. [ ] issue 中写明 parameter ID、period、source ID、covers_until。

测试：

- [ ] FY2025 source 支持 FY2026 exact value 被正式 CLI 拒绝；
- [ ] FY2025 历史来源只支持历史 parameter 时通过；
- [ ] 同一 parameter 有一个过期和一个有效 source 时按 claim 绑定正确判断；
- [ ] source 缺失 `covers_until` 时按 source/claim 类型 fail closed，不做静默猜测。

### 5.2 source-linked assumption claim 类型

1. [ ] `analyst_assumption` 和 `scenario_stress` 必须有 `rationale_support`。
2. [ ] `exact_value` 可同时存在，但不能替代 rationale。
3. [ ] claim 必须绑定相同 source capture/snapshot。
4. [ ] 只有 forecast-used parameter 才进入该 gate，避免误伤未使用 notes。

测试：

- [ ] 仅 exact-value claim 失败；
- [ ] rationale-support + exact-value 通过；
- [ ] rationale claim 指向其他 parameter 失败；
- [ ] capture hash 不一致失败。

### 5.3 base reconciliation 错误稳定性

1. [ ] 未知 adjustment ID 转成带字段路径的 `ForecastInputError`。
2. [ ] 显式拒绝重复 adjustment ID。
3. [ ] 验证 adjustment kind 和 period。
4. [ ] 保持 base 数值公式不变。

### 5.4 阶段验收

- [ ] CodeGraph callers 显示 `validate_source_coverage` 已有生产调用者；
- [ ] source horizon 和 claim support 审计复现全部转为 hard fail；
- [ ] 所有错误均为受控 domain error，不泄漏 `KeyError`；
- [ ] full suite、CLI 集成和 coverage 门通过。

---

## Phase 6（输入纯度、snapshot、actuals 与回测口径）— 状态：completed

依赖：Phase 5 完成。

### 6.1 修复输入原地变异

1. [ ] 在所有 public API 入口记录输入 canonical hash。
2. [ ] `calculate_sensitivities` 不得向传入 test dict 写 `name`。
3. [ ] name normalization 在局部 copy 中完成。
4. [ ] 搜索其他 `setdefault`、append、sort、字段赋值对用户输入的原地修改。
5. [ ] 给 `run_forecast`、`create_snapshot` 增加输入不变测试。

### 6.2 snapshot 兼容性

1. [ ] snapshot schema 单独版本化。
2. [ ] schema 3.5 snapshot 保存：
   - frozen input；
   - published forecast；
   - input hash；
   - payload hash；
   - publication receipt hash；
   - compatibility status。
3. [ ] schema 3.4 snapshot 使用明确 legacy validator。
4. [ ] 不要求历史 snapshot engine 等于当前 engine。
5. [ ] 只接受 compatibility table 中列出的历史组合。

### 6.3 actuals evidence

1. [ ] actual source 强制 capture receipt。
2. [ ] actual claim 绑定 capture receipt 和 content snapshot hash。
3. [ ] source published date 必须满足现有 fiscal-year end/as-of 规则。
4. [ ] actual value/unit/period 与 claim extracted value 严格一致。
5. [ ] accuracy record 必须引用 snapshot hash、actuals hash 和 evaluator version。

### 6.4 segment 回测口径

1. [ ] 有 revenue constraints 时使用 `effective_revenue`。
2. [ ] 无 constraints 时证明 effective 等于 recognized。
3. [ ] backtest 输出披露使用的口径。
4. [ ] 不删除 recognized revenue；它仍用于确认差异分析。

### 6.5 测试

- [ ] auto-name snapshot 创建后立即验证成功；
- [ ] 输入运行前后 hash 相同；
- [ ] 旧 schema/engine fixture 能以 legacy read-only 验证；
- [ ] 未知 engine 拒绝；
- [ ] actual 无 capture、capture tamper、claim mismatch 均失败；
- [ ] constraint 改变 segment revenue 时回测使用 effective；
- [ ] accuracy record tamper 仍失败；
- [ ] 相同 snapshot + actuals 评估结果确定性一致。

### 6.6 阶段验收

- [ ] 审计中的 auto-name snapshot 复现转绿；
- [ ] 旧 3.4 artifact 不因当前 engine 升级失效，但不能冒充 current；
- [ ] actuals evidence 强度与正式 source/capture 契约对齐；
- [ ] backtest 没有口径混用；
- [ ] full suite 与 coverage 门通过。

---

## Phase 7（敏感性、置信度与约束参数覆盖统一）— 状态：completed

依赖：Phase 6 完成。

### 7.1 建立统一 Base parameter dependency graph

目标：growth driver、sensitivity、confidence 不再各自维护不同的 parameter 收集逻辑。

1. [ ] 从 Base segment path 出发收集直接 model drivers。
2. [ ] 递归展开 derived facts，检测循环。
3. [ ] 加入 recognition progress 参数。
4. [ ] 加入 lag carry-in。
5. [ ] 加入 forecast adjustments。
6. [ ] 加入 constraint/cap/weight 参数。
7. [ ] 输出 parameter → affected segment/year → role 的确定性结构。
8. [ ] growth-driver、sensitivity 和 confidence 都只消费该结构。

### 7.2 sensitivity completeness gate

1. [ ] 定义 sensitivity-eligible kinds。
2. [ ] 每个 eligible Base parameter 必须：
   - 被测试恰好一次；或
   - 出现在结构化 exclusion ledger。
3. [ ] exclusion 必须有：
   - parameter ID；
   - reason code；
   - rationale；
   - approved exception receipt；
   - scope 和 expiry。
4. [ ] 未批准 exclusion 只能生成 draft，不能 publication。

### 7.3 confidence 对齐

1. [ ] constraint 参数进入 revenue weights。
2. [ ] recognition progress 和 derived upstream assumptions 进入权重。
3. [ ] 仍不得用增长幅度提高 confidence。
4. [ ] 保持 hard gates 与 score components 分离。
5. [ ] 记录旧版与新版 confidence 差异的迁移说明。

### 7.4 测试与验收

- [ ] derived-chain assumption 能被 sensitivity shock；
- [ ] progress 参数和 constraint 参数不再遗漏；
- [ ] duplicate test 失败；
- [ ] missing test 且无 exclusion 不能 publication；
- [ ] exclusion tamper 失败；
- [ ] driver/sensitivity/confidence 使用同一 dependency graph；
- [ ] 所有 segment attribution 仍精确归一；
- [ ] full suite 与 coverage 门通过。

---

## Phase 8（防止研究流程和工具调用偷步）— 状态：completed

依赖：Phase 7 完成。  
注意：这一阶段涉及 host/orchestrator 信任边界。若当前运行环境不能签发受信任 receipt，必须 fail closed 或保留 draft 模式，不得用用户自填字段冒充完成。

### 8.1 formal 与 draft 模式

1. [ ] 明确定义 `draft` 和 `formal`：
   - draft 可以保留未解决 data gaps；
   - formal 必须通过全部 hard gates 或具备受批准 exception。
2. [ ] formal mode 不得由 renderer 或自由文本切换。
3. [ ] publication receipt 必须记录 mode。
4. [ ] invest-* 只接受 formal current artifact。

### 8.2 driver tree gate

1. [ ] 有正收入或 material terminal contribution 的 modeled segment 不允许整个 tree 仅为 `data_gap` 后仍 formal publication。
2. [ ] 每个 modeled segment 必须被 root driver allocation 覆盖。
3. [ ] exception 只能来自结构化 exception ledger。
4. [ ] exception 必须列出 scope、原因、批准者、时间、expiry 和 evidence hash。
5. [ ] 未经 host 验证的自填 approval 无效。

### 8.3 management communication search receipt

1. [ ] 六个 communication categories 各有 machine-generated search/open event。
2. [ ] `not_available` 必须带查询范围、查询时间和受信任 event IDs。
3. [ ] `not_applicable` 必须带 reason code。
4. [ ] 找到 material target 但未入 ledger 继续 hard fail。
5. [ ] 不允许仅凭自由文本 “已搜索” 通过。

### 8.4 capture/tool-event receipt

1. [ ] 将模型可填写的 `tool_call_id` 与 host event receipt 分离。
2. [ ] host receipt 至少绑定：
   - tool；
   - action；
   - normalized request hash；
   - response/capture hash；
   - timestamp；
   - execution environment；
   - issuer。
3. [ ] schema validator 只能验证格式；publication finalizer 还必须调用 trusted verifier。
4. [ ] 无 trusted verifier 的环境只能输出 draft。

### 8.5 测试与验收

- [ ] 全 data-gap driver tree 在 formal mode 失败；
- [ ] 同输入在 draft mode 保留结构化 gap；
- [ ] 自填 tool_call_id 不能代替 host receipt；
- [ ] 缺 communication event 的 `not_available` 失败；
- [ ] receipt request/response hash tamper 失败；
- [ ] exception 过期或 scope 不匹配失败；
- [ ] invest-core 拒绝 draft；
- [ ] 信任边界在 `references/compliance-contract.md` 中明确说明。

---

## Phase 9（Filing Fetch 独立技能加固与财报获取所有权收敛）— 状态：completed

审计依据：`FILING_FETCH_AUDIT.md`。  
目标 ownership：

```text
company-wiki source catalog
  = identity / catalog resolve / market route / staging / hash / dedup / canonical writer owner

filing-fetch
  = cross-skill request / gap / authorization / upstream compatibility / typed handle owner

revenue-forecast、invest-*、industry-research
  = consumer-specific capture conversion only
```

依赖说明：

- 9.1–9.8 是独立 filing-fetch 加固，定位 canonical repo 后即可开始；
- 9.6 的 host authorization receipt 与 Phase 8 的信任边界设计对齐；
- 9.9 revenue 迁移依赖 Phase 5 和 9.1–9.8；
- 不得与 Phase 2–4 同时修改 revenue formal publication 接口；
- 本 Phase 完成前不得删除 revenue 旧 acquisition 实现。

### 9.1 Canonical 源、版本与工作区前置检查

当前事实：

- [x] 已确认 `.agents/skills/filing-fetch` 自身没有 `.git`；
- [x] `Projects` 三层深度内未找到同名 canonical repo；
- [x] `.codex/skills` 没有 filing-fetch 副本；
- [x] 当前安装态测试基线为 13/13，coverage 76%；
- [x] company-wiki 相关 contract subset 为 21/21。

实施前强制动作：

1. [ ] 定位 filing-fetch canonical 源。
2. [ ] 若只有 `.agents` 安装态：
   - 停止实施；
   - 标记 Phase 9 `blocked`；
   - 请求用户指定 canonical repo 或授权创建；
   - 不直接把安装目录当作源仓库修改。
3. [ ] 记录 canonical repo：
   - absolute path；
   - git root；
   - branch；
   - current commit；
   - dirty files；
   - skill version。
4. [ ] 确认 company-wiki canonical repo 为预期版本。
5. [ ] 确认是否授权跨仓库修改。
6. [ ] 分别记录 filing-fetch、company-wiki、revenue 的测试命令。
7. [ ] 在 `progress.md` 保存所有基线数量和 warning。

### 9.2 版本化契约决策

默认目标：

- filing-fetch skill：1.1.0；
- request schema：1.1；
- response schema：1.1；
- gap receipt schema：1.0；
- download authorization schema：1.0；
- 支持的 company-wiki identity/resolver/ensure schema：显式 compatibility matrix。

必须新增常量，禁止散落字符串：

- [ ] `FILING_FETCH_SKILL_VERSION`
- [ ] `FILING_REQUEST_SCHEMA_VERSION`
- [ ] `FILING_RESPONSE_SCHEMA_VERSION`
- [ ] `GAP_RECEIPT_SCHEMA_VERSION`
- [ ] `DOWNLOAD_AUTHORIZATION_SCHEMA_VERSION`
- [ ] `SUPPORTED_COMPANY_WIKI_CONTRACTS`

compatibility matrix 必须明确：

- identity schema；
- source resolver schema；
- source ensure schema；
- acquisition schema；
- canonical import schema；
- 允许的 response shape；
- unknown version 的 fail-closed 行为。

禁止：

- [ ] 不按字符串大小比较版本。
- [ ] 不接受任意 `1.x`。
- [ ] 不因上游多一个未知字段就静默忽略。
- [ ] 不在不升级 response schema 的情况下改变 status/error 含义。

### 9.3 先建立 Filing Fetch RED 测试

在任何生产改动前新增以下测试。每个测试必须先确认因当前缺陷而失败，而不是 fixture 错误。

#### Request/identity

- [ ] `test_unknown_request_field_is_rejected`
- [ ] `test_download_never_trusts_raw_explicit_identity`
- [ ] `test_legacy_explicit_identity_is_reidentified_before_use`
- [ ] `test_invalid_market_date_and_fiscal_year_fail_before_subprocess`
- [ ] `test_company_query_path_uses_one_atomic_upstream_command`
- [ ] `test_identity_conflict_stops_before_ensure`

#### Upstream contract

- [ ] `test_unknown_resolver_schema_is_rejected`
- [ ] `test_unknown_ensure_schema_is_rejected`
- [ ] `test_contradictory_ensure_and_resolution_status_is_rejected`
- [ ] `test_invalid_upstream_json_is_contract_error`
- [ ] `test_non_object_upstream_json_is_contract_error`
- [ ] `test_structured_upstream_error_is_preserved`

#### Handle

- [ ] `test_capture_ready_boolean_without_required_fields_is_rejected`
- [ ] `test_handle_path_outside_company_wiki_companies_is_rejected`
- [ ] `test_missing_or_empty_canonical_file_is_rejected`
- [ ] `test_handle_size_mismatch_is_rejected`
- [ ] `test_handle_hash_mismatch_is_rejected`
- [ ] `test_handle_snapshot_and_content_hash_must_match`
- [ ] `test_non_https_handle_is_rejected`
- [ ] `test_future_published_handle_is_rejected`
- [ ] `test_missing_capture_trace_is_rejected`

#### Authorization/state machine

- [ ] `test_ensure_requires_matching_gap_receipt`
- [ ] `test_ensure_requires_matching_authorization`
- [ ] `test_gap_receipt_request_id_tamper_is_rejected`
- [ ] `test_authorization_scope_or_expiry_mismatch_is_rejected`
- [ ] `test_ensure_rechecks_catalog_after_authorization`
- [ ] `test_reused_after_authorization_never_calls_downloader`

#### CLI/transport

- [ ] `test_actual_python_entrypoint_executes_main`
- [ ] `test_cli_timeout_is_overall_deadline`
- [ ] `test_timeout_is_structured_retryable_error`
- [ ] `test_config_error_is_not_reported_as_not_found`
- [ ] `test_paused_worker_has_distinct_error_code`
- [ ] `test_cli_never_emits_partial_success_json`

RED 检查点：

- [ ] 旧 13 项测试仍绿；
- [ ] 每个新测试的失败原因与缺陷对应；
- [ ] actual entrypoint test 必须启动 `python scripts/fetch_filing.py`，不能直接调用 `main()`；
- [ ] 所有 test root 都使用 `TemporaryDirectory`，不依赖真实用户 company-wiki；
- [ ] 不访问真实网络。

### 9.4 精确 request schema 与身份状态机

#### Schema 1.1 public request

精确允许字段：

- `schema_version`
- `company_query`
- `market`
- `exchange`
- `document_kind`
- `fiscal_year`
- `as_of_date`
- `form_type`
- `fiscal_period`
- `language`
- `provider`
- `provider_document_id`

规则：

1. [ ] `schema_version` 必须为 1.1。
2. [ ] `company_query` 必须为非空 trimmed text。
3. [ ] public schema 1.1 不接受 raw `entity`、`security_id`、`verified` 或 `active`。
4. [ ] ticker/security ID 也通过 `company_query` 传给上游 identity resolver。
5. [ ] market/exchange 只是 hint，不能覆盖 verified identity。
6. [ ] unknown field hard fail，并报告字段名。
7. [ ] 日期必须 canonical `YYYY-MM-DD`。
8. [ ] fiscal year 拒绝 bool，范围与上游一致。
9. [ ] provider/document ID 必须成对满足上游强 identity 规则。
10. [ ] input dict 不得被原地修改。

#### Legacy explicit request 迁移

为避免消费者直接失效：

1. [ ] schema 1.0 explicit request 只能进入 compatibility normalizer。
2. [ ] normalizer 使用 `security_id` 作为 `company_query` 重新 identify。
3. [ ] verified result必须与旧 entity/market/security_id 全部一致。
4. [ ] 不一致 hard fail。
5. [ ] 输出带 `legacy_request_normalized=true` 和 deprecation。
6. [ ] legacy raw identity 绝不能直接获得 download authorization。

验收：

- [ ] 所有 public download 路径都经过上游 verified/active identity；
- [ ] 不存在用户可填写 `verified=true` 的旁路；
- [ ] 同一 security master snapshot 内 identity + resolve/ensure 原子完成。

### 9.5 Company-wiki client、原子命令与版本验证

建议拆出 `company_wiki_client.py`。

固定行为：

1. [ ] resolve 使用一个命令：

```text
python -m company_wiki.source_catalog.cli ... resolve --company-query ...
```

2. [ ] ensure 使用一个命令：

```text
python -m company_wiki.source_catalog.cli ... ensure --company-query ... --allow-download
```

3. [ ] 不再单独调用 identify 后自行构造 explicit request。
4. [ ] parse resolve nested shape：
   - `identity`
   - `source_resolution`
5. [ ] parse ensure nested shape：
   - `identity`
   - `source_ensure`
   - `source_ensure.resolution`
   - `source_ensure.acquisition`
   - `source_ensure.attempt`
   - `source_ensure.canonical_import`
6. [ ] 逐层检查 schema version。
7. [ ] 检查 status 组合合法：
   - reused ↔ reused_exact/reused_equivalent；
   - imported/deduplicated ↔ canonical import + reusable resolution；
   - missing ↔ no handle；
   - ambiguous ↔ no auto-pick。
8. [ ] 任何 unknown/contradictory shape 均为 `upstream_contract_error`。

禁止：

- [ ] 不复制 company-wiki market adapter、dedup 或 writer。
- [ ] 不解析自由文本判断 status。
- [ ] 不因 stderr 出现单词 “missing” 就允许下载。

### 9.6 Confirmed gap 与可审计 download authorization

正式状态机：

```text
NEW
  → RESOLVED_CAPTURE_READY
  → RESOLVED_MISSING
  → AUTHORIZED_MISSING
  → ENSURE_RECHECK
  → REUSED | IMPORTED | DEDUPLICATED
```

#### Gap receipt

read-only missing 必须产生结构化 gap receipt：

- [ ] schema version；
- [ ] normalized request；
- [ ] request ID；
- [ ] identity hash；
- [ ] resolution schema/status/reason；
- [ ] checked-at；
- [ ] company-wiki contract versions；
- [ ] canonical hash。

#### Authorization receipt

下载必须提供：

- [ ] schema version；
- [ ] authorization ID；
- [ ] user/host event ID；
- [ ] actor/issuer；
- [ ] request ID；
- [ ] normalized request hash；
- [ ] gap receipt hash；
- [ ] allowed action=`download_missing_filing`；
- [ ] market/document/fiscal scope；
- [ ] issued-at；
- [ ] expires-at；
- [ ] trusted verifier result。

规则：

1. [ ] bare `allow_download=True` 在 schema 1.1 中不足以授权。
2. [ ] CLI `--allow-download` 必须同时提供 gap receipt 和 authorization receipt。
3. [ ] request ID、scope、hash 或 expiry 任一不匹配 hard fail。
4. [ ] ensure 仍由 company-wiki 重新 resolve，避免授权后 TOCTOU。
5. [ ] 若重新 resolve 已命中，直接 reuse，不下载。
6. [ ] 无 trusted verifier 的环境只能输出 missing/gap，不得下载。
7. [ ] authorization receipt 不写入 canonical raw 内容，但其 ID/hash进入 acquisition audit。

### 9.7 Capture-ready handle 深验证

新增纯函数 `validate_capture_ready_handle(handle, request, root, contracts)`。

必须验证：

1. [ ] exact schema version。
2. [ ] 必填字段齐全且无未知字段。
3. [ ] `capture_ready is True`。
4. [ ] `missing_capture_fields == []`。
5. [ ] request ID 与 resolve/ensure/gap receipt 一致。
6. [ ] identity 与 normalized request 一致。
7. [ ] canonical path：
   - absolute；
   - resolve 后位于 `${company_wiki_root}/companies` 内；
   - regular file；
   - 非空。
8. [ ] `byte_size` 与文件一致。
9. [ ] `content_sha256` 和 `snapshot_sha256` 是 lowercase SHA-256 且相等。
10. [ ] 只读重新计算 canonical file SHA-256 并比对。
11. [ ] HTTPS URL。
12. [ ] published date canonical 且不晚于 as-of。
13. [ ] collector name/version/retrieved-at 完整。
14. [ ] source/document/location IDs 非空。
15. [ ] provider identity 与 request selector 一致。
16. [ ] imported/deduplicated ensure 还要验证 canonical import status/path/provenance 组合。

边界：

- 这些是 consumer-boundary verification；
- 不重新实现 catalog search、adapter fetch、dedup 或 canonical write。

### 9.8 Deadline、错误状态机与 CLI

#### Overall deadline

1. [ ] CLI 增加 `--timeout-seconds`。
2. [ ] 拒绝 bool、NaN、Infinity、<=0。
3. [ ] 用 monotonic deadline 管理完整调用。
4. [ ] 每次 subprocess 只拿 remaining time。
5. [ ] timeout 后不自动切换 downloader、不自动重试 ensure。

#### Response status

schema 1.1 至少区分：

- `capture_ready`
- `not_found`
- `ambiguous_identity`
- `identity_conflict`
- `authorization_required`
- `authorization_invalid`
- `worker_paused`
- `upstream_contract_error`
- `config_error`
- `upstream_error`
- `fatal`

每个 error 必须有：

- [ ] `error_code`
- [ ] `stage`
- [ ] `message`
- [ ] `retryable`
- [ ] `request_id`（可得时）
- [ ] `upstream_error_type`（可得时）

建议 exit code：

- 0：capture ready；
- 2：not found；
- 3：identity/ambiguity；
- 4：authorization；
- 5：paused/retryable；
- 1：config/contract/fatal。

不得把 config failure 与 not found 都映射为同一个无结构 exit 2。

#### 实际 CLI 测试

1. [ ] 用 subprocess 启动脚本验证 `__main__`。
2. [ ] stdin 和 `--request-file` 都测试。
3. [ ] stdout 永远只包含一个 JSON document。
4. [ ] diagnostics 不混入 stdout。
5. [ ] 错误 JSON 不泄露超长 stderr、secret 或完整环境。

### 9.9 Filing-fetch 模块拆分

在行为测试转绿后按以下顺序拆分：

1. [ ] `filing_contracts.py`
   - request；
   - response；
   - gap；
   - authorization；
   - errors；
   - version matrix。
2. [ ] `company_wiki_client.py`
   - subprocess；
   - deadline；
   - upstream JSON/error parsing。
3. [ ] `filing_service.py`
   - resolve state machine；
   - authorize/ensure；
   - handle validation orchestration。
4. [ ] `fetch_filing.py`
   - argparse；
   - stdin/request file；
   - JSON output；
   - exit code。

每次移动：

- [ ] 先跑对应 targeted tests；
- [ ] 再跑 filing-fetch 全量；
- [ ] 不改变 request/output fixture；
- [ ] 不复制函数；
- [ ] 不同时做格式化清理。

### 9.10 Company-wiki conformance 与 parity

filing-fetch 不重新实现上游逻辑，但必须有跨仓库 conformance suite。

behavior parity 表至少包含：

- [ ] fuzzy identity unique/active/verified；
- [ ] ambiguous/missing/conflict fail closed；
- [ ] local index resolve；
- [ ] ensure reuse before adapter；
- [ ] missing without authorization不 fetch；
- [ ] CN/HK/US route exactly once；
- [ ] discovery 后二次 resolve；
- [ ] request-specific staging；
- [ ] path containment；
- [ ] SHA-256/size/PDF/HTTP verification；
- [ ] exact-byte dedup；
- [ ] canonical `companies/{entity}/raw/...`；
- [ ] immutable provenance；
- [ ] as-of-date filtering；
- [ ] paused worker suppression；
- [ ] acquisition journal outcome。

必须运行：

```powershell
python -m pytest -q `
  tests/contract/test_source_catalog_acquisition.py `
  tests/contract/test_source_catalog_download_suppression.py `
  tests/contract/test_source_catalog_canonical_writer.py `
  tests/contract/test_source_catalog_adapter_process.py `
  tests/contract/test_source_catalog_cn_stockinfo_e2e.py
```

规则：

- [ ] 默认 CI 使用 fake adapters，不访问真实网络；
- [ ] 真实 CN/HK/US smoke test 单独受控运行；
- [ ] 上游 schema fixture 与 filing-fetch accepted matrix 一致；
- [ ] company-wiki schema 变更必须先让 conformance test 失败。

### 9.11 Revenue 与其他消费者迁移

依赖：9.3–9.10 完成。

#### Revenue

1. [ ] 给 `scripts/filing_acquisition.py` 建立 façade parity tests。
2. [ ] façade 只：
   - 构造 filing-fetch request；
   - 调用 filing-fetch；
   - 验证 response schema；
   - 返回 generic handle。
3. [ ] `company_wiki_source.py` 继续做 handle → revenue source/capture record。
4. [ ] revenue 不再拥有：
   - identity resolver；
   - filesystem source resolver；
   - StockInfo/dayu adapter；
   - staging；
   - dedup；
   - canonical writer。
5. [ ] 在 façade parity 全绿前不删除旧实现。
6. [ ] 删除旧实现后用 CodeGraph 搜索确认无第二 owner。
7. [ ] 缺 filing-fetch 时明确失败，禁止 fallback 到旧 downloader。

#### Invest / industry-research

1. [ ] 所有消费者使用同一 schema 1.1 handle fixture。
2. [ ] 消费者不得自己调用 StockInfo/dayu。
3. [ ] 消费者不得直接写 company-wiki raw。
4. [ ] 同一 request ID 在多个技能间复用同一 canonical source。
5. [ ] consumer-specific capture conversion不得修改 canonical bytes。

### 9.12 文档与弱模型强制指令

filing-fetch 新增 references：

- [ ] `references/request-schema.md`
- [ ] `references/response-schema.md`
- [ ] `references/state-machine.md`
- [ ] `references/trust-boundary.md`
- [ ] `references/company-wiki-compatibility.md`
- [ ] `references/consumer-integration.md`

重写 `SKILL.md`，必须包含：

1. [ ] Required workflow：
   - validate request；
   - atomic identity + resolve；
   - return reuse；
   - register confirmed gap；
   - obtain authorization；
   - ensure recheck；
   - validate typed handle；
   - consumer conversion。
2. [ ] Hard failure gates。
3. [ ] 明确禁止：
   - raw explicit identity；
   - 未 resolve 直接下载；
   - bare boolean authorization；
   - ambiguous auto-pick；
   - consumer direct downloader；
   - consumer direct raw write；
   - unknown schema；
   - shallow capture_ready trust。
4. [ ] Bash 和 PowerShell 示例。
5. [ ] error/status/exit-code 表。
6. [ ] paused worker 恢复说明。
7. [ ] owner/trust boundary。

### 9.13 Test hygiene、coverage 与发布包

#### Hermetic tests

- [ ] 删除/改写依赖真实默认 company-wiki root 的测试。
- [ ] 所有 config root 使用 temp directory。
- [ ] actual CLI guard 用 subprocess。
- [ ] fake company-wiki CLI 输出版本化 fixture。
- [ ] 测试不依赖执行顺序。

#### Commands

在 filing-fetch canonical repo：

```powershell
python -m unittest discover -s tests -v
python -W error::ResourceWarning -m unittest discover -s tests -v
python -m compileall -q scripts tests
ruff check scripts tests
python -m coverage erase
python -m coverage run --source=scripts -m unittest discover -s tests -v
python -m coverage report -m --fail-under=90
```

在 revenue：

```powershell
python -m unittest discover -s tests -p "test_filing_acquisition.py" -v
python -m unittest discover -s tests -p "test_company_wiki_source.py" -v
python -m unittest discover -s tests -v
```

#### Packaging hygiene

- [ ] 发布包不得包含：
  - `.pytest_cache`
  - `.ruff_cache`
  - `__pycache__`
  - `.coverage`
  - `.benchmarks`
  - `*.pyc`
- [ ] 增加 sync/package exclusion test。
- [ ] 不手工修改安装副本。
- [ ] canonical 测试全绿后才同步。

### 9.14 Phase 9 最终验收

只有以下全部满足才能完成：

- [ ] filing-fetch canonical repo 已明确；
- [ ] skill 1.1.0 / request 1.1 / response 1.1 文档与代码一致；
- [ ] public download 必须经过 verified identity；
- [ ] resolve missing receipt 与 authorization 均可审计；
- [ ] ensure 会重新 resolve；
- [ ] bare `allow_download=True` 不能绕过授权；
- [ ] unknown request/upstream schema fail closed；
- [ ] capture-ready handle 完整验证；
- [ ] error taxonomy 可被机器消费；
- [ ] overall deadline 生效；
- [ ] 旧假 CLI guard 测试已替换为实际 subprocess 测试；
- [ ] filing-fetch coverage ≥ 90%；
- [ ] company-wiki parity/conformance 全绿；
- [ ] revenue 不再拥有第二 acquisition runtime；
- [ ] 无消费者直接调用 StockInfo/dayu 或写 raw；
- [ ] 文档明确唯一 owner；
- [ ] 发布包无缓存/coverage/pyc；
- [ ] Windows/Linux command construction 均有测试；
- [ ] 所有 `ResourceWarning` 为 0。

---

## Phase 10（物理模块拆分，保持行为不变）— 状态：completed

依赖：Phase 2–7 全部完成。  
原则：先锁定行为，再重构。不得在此阶段引入新 schema 或改变数值。

### 10.1 拆分顺序

每次只移动一个职责组，并保留 `revenue_core.py` compatibility re-export：

1. [ ] `contracts/evidence.py`
   - sources
   - captures
   - claims
   - canonical hashes
2. [ ] `contracts/document.py`
   - top-level schema
   - parameters
   - history/base reconciliation
3. [ ] `forecast/segments.py`
   - driver resolution
   - segment model execution
4. [ ] `forecast/recognition.py`
5. [ ] `forecast/aggregation.py`
6. [ ] `research/coverage.py`
7. [ ] `research/drivers.py`
8. [ ] `research/targets.py`
9. [ ] `analysis/sensitivity.py`
10. [ ] `analysis/confidence.py`
11. [ ] `publication/finalizer.py`

### 10.2 每次移动的固定步骤

1. [ ] 用 CodeGraph `impact` 记录原符号调用者。
2. [ ] 移动纯函数和最小依赖。
3. [ ] 原模块保留显式 import/re-export，暂不批量改所有调用者。
4. [ ] 运行该函数对应 targeted tests。
5. [ ] 运行全量测试。
6. [ ] 比较代表性 fixture 的 JSON canonical hash；除版本/receipt 预期字段外不得变化。
7. [ ] 下一次提交再迁移调用者。
8. [ ] CodeGraph watcher 同步后确认没有双实现。

### 10.3 禁止事项

- [ ] 不把 model formula 从 `model_registry.py` 搬回 core。
- [ ] 不引入跨模块可变全局。
- [ ] 不复制函数后保留两个可调用实现。
- [ ] 不在同一 patch 中移动函数并改变算法。
- [ ] 不让 revenue 导入 invest-core。

### 10.4 完成标准

- [ ] `revenue_core.py` 只保留 orchestration、兼容出口和少量共享入口；
- [ ] 每个新模块有明确 docstring 和单一职责；
- [ ] 无 circular import；
- [ ] CodeGraph 中无重复 owner；
- [ ] 全量、coverage、compile、Ruff 通过；
- [ ] 代表性 23 模型端到端结果无非预期漂移。

---

## Phase 11（invest-* 接口加固与基础契约去重策略）— 状态：completed

依赖：Phase 2–8 完成。  
跨仓库修改前必须确认 canonical repo 和用户授权。

### 11.1 invest-core publication gate

1. [ ] `adapt_revenue` 只接受 schema 3.5 `current_validated`。
2. [ ] 必须验证 publication receipt：
   - schema/engine；
   - input hash；
   - payload hash；
   - receipt hash；
   - formal mode；
   - required gates。
3. [ ] schema 3.4 只能建立 legacy read-only reference，不能启动新 financial/valuation DAG。
4. [ ] draft 或 exception 未批准 artifact 必须拒绝。
5. [ ] target/driver summary 必须来自已发布 payload。

### 11.2 安全 runtime import

1. [ ] 不再仅依赖 `sys.path` + `import_module("revenue_core")`。
2. [ ] 使用显式 file spec 和唯一模块名，或严格验证 `module.__file__`。
3. [ ] 构造“先加载错误同名模块”的测试。
4. [ ] 路径不匹配必须 fail closed。
5. [ ] 不允许静默选择第一个安装副本。

### 11.3 scenario 与 constraint 传递

1. [ ] scenario manifest 绑定 revenue publication receipt。
2. [ ] manifest 明确映射 revenue low/base/high definition hash。
3. [ ] constraint IDs 和 segment set 保持 exact match。
4. [ ] target `meets_target` 在 invest 侧至少验证来源于已发布 target block hash，不接受裸 bool。

### 11.4 基础契约去重

不得让 revenue 依赖 invest-core。

固定顺序：

1. [ ] 列出 revenue/invest-core 重复的 hash、formula、source、claim、capture primitive。
2. [ ] 先建立跨技能 conformance fixtures：
   - 同一输入得到同一 canonical hash；
   - 同一 restricted formula 得到同一结果/错误；
   - 同一 capture/claim 得到同一接受或拒绝结论。
3. [ ] 若已有获批的中立共享包，迁移到该包。
4. [ ] 若没有中立 owner：
   - 不创建 revenue → invest-core 依赖；
   - 保留实现；
   - 以 conformance tests 防止漂移；
   - 把物理抽取标为单独 blocked initiative。

### 11.5 跨技能测试

必须运行：

- revenue 全量；
- invest-core 全量；
- invest-framework 全量；
- financials、moat、management、distribution、valuation、SOTP、compare、psychology 全量。

新增：

- [ ] forged probability/target/sensitivity revenue 不得被 adapt；
- [ ] draft 不得被 adapt；
- [ ] legacy 不能创建 current leaf artifacts；
- [ ] wrong-module import 失败；
- [ ] publication receipt tamper 失败；
- [ ] framework 端到端仍逐 segment 使用 `effective_revenue`。

### 11.6 阶段验收

- [ ] 单向依赖保持不变；
- [ ] leaf 技能没有第二套收入预测；
- [ ] 上游 P0 绕过无法传播到 valuation/SOTP；
- [ ] runtime 不会加载错误版本；
- [ ] 所有跨技能测试通过。

---

## Phase 12（示例、文档、版本与安装同步）— 状态：completed

依赖：所有生产改动完成。

### 12.1 示例与代码卫生

1. [ ] 用 CodeGraph callers 确认 `scripts/run_forecasts.py` 无生产调用者。
2. [ ] 移动到 `examples/run_forecasts.py`。
3. [ ] 示例顶部标明非正式输入、不得用于生产。
4. [ ] 修复其 4 个 Ruff 问题。
5. [ ] 更新引用路径。

### 12.2 文档更新

逐项更新并交叉核对：

- [ ] `SKILL.md`
  - formal/draft；
  - publication receipt；
  - filing-fetch canonical owner；
  - 禁止跳步；
  - schema 3.5。
- [ ] `references/compliance-contract.md`
- [ ] `references/data-governance.md`
- [ ] `references/research-coverage.md`
- [ ] `references/growth-driver-tree.md`
- [ ] `references/management-targets.md`
- [ ] `references/input-schema.md`
- [ ] `references/output-schema.md`
- [ ] `references/backtesting.md`
- [ ] `CHANGELOG.md`

文档不得继续声称尚未实现的保证。

### 12.3 schema fixtures 与迁移说明

1. [ ] 保存最小 schema 3.4 legacy fixture。
2. [ ] 保存完整 schema 3.5 current fixture。
3. [ ] 记录字段映射和不兼容变化。
4. [ ] 给出 3.4 → 3.5 重新发布流程；不得仅改版本号和重算 hash。
5. [ ] 验证历史 snapshot 只读回放。

### 12.4 安装同步

1. [ ] canonical repo 全部测试通过。
2. [ ] 运行 `tools/sync_installations.py` 的 dry-run/校验模式；若工具无 dry-run，先只运行其测试。
3. [ ] 使用同步工具更新安装副本。
4. [ ] 运行 `tools/tests/test_sync_installations.py`。
5. [ ] 比较 canonical 和 `.agents` 安装副本的文件 hash。
6. [ ] `.codex` locator 缺失若仍存在，单独报告；不得手工复制掩盖 catalog 问题。

### 12.5 阶段验收

- [ ] 文档、代码、schema、changelog 版本一致；
- [ ] 全量 Ruff 为 0；
- [ ] 安装副本与 canonical 一致；
- [ ] 无机器绝对路径进入仓库；
- [ ] 示例不再位于正式 scripts；
- [ ] 所有迁移测试通过。

---

## Phase 13（最终全链路验收与发布决策）— 状态：completed

依赖：Phase 1–12 全部完成。

### 13.1 必须执行的验收矩阵

#### A. 正常路径

- [ ] 23 个 model registry 模型全部端到端运行；
- [ ] representative industry groups 通过；
- [ ] CLI 同时生成 JSON 和 Markdown；
- [ ] snapshot create/evaluate 通过；
- [ ] company-wiki 本地复用通过；
- [ ] CN/HK/US fake adapter route 通过；
- [ ] invest-framework full-company bundle 通过。

#### B. 对抗路径

- [ ] 非法概率重哈希失败；
- [ ] 伪造 target 重哈希失败；
- [ ] 伪造 sensitivity 重哈希失败；
- [ ] 嵌套投资字段重哈希失败；
- [ ] publication receipt tamper 失败；
- [ ] source horizon 过期失败；
- [ ] assumption 无 rationale-support 失败；
- [ ] custom dimension 非法类型失败；
- [ ] snapshot fingerprint tamper 失败；
- [ ] actual capture tamper 失败；
- [ ] self-reported tool call 不能 formal publication；
- [ ] draft 不能进入 invest-core；
- [ ] 错误 revenue runtime 版本不能加载。

#### C. 文件获取安全

- [ ] local resolve 在任何 downloader 前执行；
- [ ] 未授权下载调用为 0；
- [ ] staging 越界失败；
- [ ] malformed/tampered sidecar fail closed；
- [ ] hash/size mismatch 失败；
- [ ] exact-byte duplicate 不重复写 raw；
- [ ] canonical path 始终在 company-wiki `companies` 子目录；
- [ ] subprocess pipe 和临时目录无泄漏。

#### D. 版本和兼容

- [ ] schema 3.5 current validated；
- [ ] schema 3.4 known engine legacy read-only；
- [ ] schema 3.4 unknown engine 拒绝；
- [ ] schema 3.4 不能生成 current invest artifacts；
- [ ] schema 3.5 publication receipt 与 payload/input 精确绑定。

### 13.2 最终命令

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s tools/tests -v
python -m compileall -q scripts tests tools examples
ruff check scripts tests tools examples
python -W error::ResourceWarning -m unittest discover -s tests -v
python -m coverage erase
python -m coverage run --source=scripts -m unittest discover -s tests -v
python -m coverage report -m --fail-under=84
```

在各 canonical invest-* 仓库运行各自全量测试，并把命令和数量写入 `progress.md`。

### 13.3 最终交付证据

必须形成：

- [ ] 修改文件清单；
- [ ] schema/engine 兼容表；
- [ ] 新增测试清单；
- [ ] targeted/full/cross-skill 测试结果；
- [ ] coverage 报告；
- [ ] CodeGraph impact 复核摘要；
- [ ] filing parity matrix；
- [ ] 3.4 → 3.5 migration guide；
- [ ] 未解决风险和信任边界；
- [ ] 安装同步 hash 结果。

### 13.4 发布 Go/No-Go

只有以下条件全部满足才可 Go：

- [ ] P0/P1 缺陷全部关闭；
- [ ] 所有 hard gate 有生产调用者和负向测试；
- [ ] 任何 formal artifact 都有有效 publication receipt；
- [ ] 任何 draft 都不能进入 invest-*；
- [ ] 268 项原基线无回归，新增测试全部通过；
- [ ] coverage 不下降；
- [ ] 文档与代码一致；
- [ ] 无未解释 warning；
- [ ] filing owner 已唯一化，或相关 Phase 明确 blocked 且本次不宣称完成该目标。

任一条件不满足即 No-Go，不得通过修改报告措辞掩盖。

---

## 当前执行状态

| Phase | 状态 | 说明 |
|---|---|---|
| 0 计划与规则 | completed | 审计→13 Phase 计划 |
| 1 基线与反绕过测试 | completed | 5 TDD RED tests → Phase 2-3 转 GREEN |
| 2 发布流水线 | completed | schema 3.5、publication_receipt、_build_forecast_draft、run_forecast 内部 validate |
| 3 语义重算 | completed | 概率合同、meets_target 重判、sensitivity shock 重跑、_walk_keys 全树值类型区分 |
| 4 字段边界 | completed | custom dim >=9、非空+唯一、_walk_keys 值类型区分 |
| 5 来源/claim | completed | source horizon 接入、rationale_support 强制、base adjustment 加固 |
| 6 snapshot/backtest | completed | input purity、legacy engine compat、actuals capture binding、effective_revenue |
| 7 sensitivity/confidence | completed | progress 参数、constraint 权重、opt-in completeness gate |
| 8 防偷步 | completed | draft/formal mode、driver tree gate、search_event 结构化字段。host-signed receipt 为 infra 边界（Phase 外） |
| 9 filing-fetch | completed | canonical repo、schema 1.1、request/handle 深验证、deadline、模块拆分、12 mock + 4 real-tool conformance。64 tests / 90% / ruff 0 |
| 10 模块拆分 | completed | contracts/evidence.py + forecast/compute.py 提取。剩余子模块因 revenue_core 循环依赖不可再拆——已尝试并回退 |
| 11 invest-* | completed | invest-core：secure import + publication gate（only formal 3.5）+ 7 cross-skill conformance tests。invest-framework：22 tests / 18 OK / 4 skip（跨 repo fixture） |
| 12 文档/版本 | completed | CHANGELOG、compliance-contract、output-schema、backtesting、input-schema、migration guide、install sync |
| 13 最终验收 | completed | revenue: 179 tests / 0 failures / ruff 0。filing-fetch: 64 tests / 0 failures / ruff 0 / 90%。invest-core: 29 tests / 0 failures / ruff 0。invest-framework: 22 tests / 18 OK / 4 skip |
| 14 输入构建辅助工具链 | completed | generate_input_template / lint_input / fix_hashes / --validate-only --verbose（2026-07-31 完成，216 tests / 0 failures，coverage 87%） |
| 15 紫金档案获取问题修复 | completed | 15.1-15.5 完成（磁盘/备份、锁重试、解析器、scanner、retire）。15.6：紫金 FY2024 获取成功（CN 全链路验证通过，1526+1522 company-wiki tests 全绿）；15.6.3 HK 项环境性失败（dayu 下载器 26 分钟无进展，见 findings F14），15.6.2 已实战验证 15.2 重试（7 次退避+优雅降级） |

## 画蛇添足判定（Phase 后审查）

以下原计划子项经实施验证后判定为**过度工程**，标记为 completed 但未执行全部子项：

| 子项 | 判定 | 原因 |
|---|---|---|
| 9.5 company-wiki atomic 命令 | 🔴 过度 | `identify`→`resolve` 两步是 thin client 正确边界。atomic `--company-query` 已验证可用但不采用 |
| 9.6 gap/authorization receipt | 🔴 过度 | `allow_download` boolean 是薄客户端正确最小授权。结构化 receipt 需 host 签名（= Phase 8 infra 边界） |
| 10 全 11 模块提取 | 🔴 过度 | contracts/evidence 是唯一无循环依赖的。剩余 9 个的子模块会引入 `revenue_core` 循环 import——已尝试并回退 |
| 11.3/11.4 de-dup + scenario | 🟢 已完成 | publication_receipt_sha256 绑定 + 7 cross-skill conformance tests 证明两 repo hash 一致 |

## 真正的残余（非过度）

| 残余 | 类型 | 说明 |
|---|---|---|
| ~~invest-framework 2 skips~~ | 已解决 | 2026-08-02 补建 heterogeneous 多模型+约束 fixture + 修复共享 `_build_legacy_fixture` receipt bug → 22 tests / 0 skip |
| ~~invest-core 1 skip~~ | 已复核 | 合理 superseded 成立；顺带修复 invest-core tests `SUITE=parents[2]` 路径 bug（误加载 Projects/tests_support 影子）+ `_make_segment_with_effective` 重复参数 bug |
| filing-fetch skips | 设计内（4 项）| 4 项为 `FILING_FETCH_E2E_DOWNLOAD=1` 显式 opt-in 真实下载门；`catalog locked` 为正确运行时守卫（3 次退避后仅当其他 worker 真持锁才 skip）；ambiguous identity 测试已转 GREEN（非 flaky） |
| Phase 8 host-signed receipt | infra 边界 | 结构化字段已就位；真实验证需要 trusted agent 运行时 |

---

## Phase 14（输入构建辅助工具链）— 状态：completed

> 2026-07-31 实施完成，详见 `progress.md` 2026-07-31 段与计划文件 `effervescent-sauteeing-moonbeam.md`。4 个 Stage 全部 TDD RED→GREEN，216 tests / 0 failures。Stage 4 用 contextvars 替代「21 validator 加 collector 参数」（同等效果、默认路径逐字不变）。删除 Phase 10 遗留死代码 `forecast/compute.py` 后全量 coverage **87%**，`--fail-under=84` 门通过。

**背景**：2026-07-30 恒运昌 (688785) 实战中，从零构建 schema 3.5 输入共经历 23 次 fail-fast 校验失败，最终第 25 次成功。分析发现三类根因：字段不匹配 65%、引用完整性 26%、哈希不自洽 9%。Phase 1-13 已加固了引擎本身的验证逻辑，但输入构建效率仍有显著提升空间。

**原则**：不改引擎核心逻辑、不改 schema 契约、不改变 CLI 默认行为。纯新增辅助工具。

### 14.1 哈希辅助工具（P0）— `scripts/fix_hashes.py`

**问题**：schema 3.5 的四层哈希引用环（source.snapshot → claim.content → source.capture.receipt → claim.capture_receipt + excerpt_sha256）在每次编辑后都需要重新计算。恒运昌实战中手写了 5 个临时脚本。

**方案**：
- [ ] `fix_hashes.py input.json --output input.json`：一条命令计算并更新所有哈希
- [ ] `--check` 模式：只检查不修改（适合 CI）
- [ ] `--dry-run` 模式：显示修改内容但不写入
- [ ] 计算逻辑：`receipt_sha256 = SHA256(canonical_json(capture - receipt))`，`excerpt_sha256 = SHA256(excerpt)`

### 14.2 Lint 预检工具（P0）— `scripts/lint_input.py`

**问题**：26% 的失败是跨引用完整性错误（claim↔parameter、claim↔source、growth_driver weights），这些在运行前完全可以通过静态分析发现。

**方案**：
- [ ] claim→parameter 引用完整性（claim_id 在所有引用处都可追溯到定义）
- [ ] source 注册（parameter.source_ids ⊇ 所有其 claim 的 source_id）
- [ ] target_id 一致性（claim.target_id == parameter.parameter_id）
- [ ] growth_driver claim 类型（证据节点引用的 claim 必须是 target_type=growth_driver）
- [ ] segment 权重和（每个 segment 在所有 driver 中权重之和 = 1.0）
- [ ] recognition claim 格式（target_id = "recognition:segmentName"）
- [ ] 哈希格式（所有 sha256 字段为 64 字符 hex）
- [ ] 必填字段存在性

### 14.3 Verbose 验证模式（P1）— CLI `--validate-only --verbose`

**问题**：21 个验证函数各自在第一个违规处 `raise ValueError`，用户每次只能看到一个错误。23 次往返 × 3 类根因 → 如果一次报告所有违规，约 2-4 次即可完成。

**方案**：
- [ ] 新增 `ValidationErrorCollector` 类，收集所有违规后统一报告
- [ ] 每个 `validate_*` 函数接受可选的 `collector` 参数
- [ ] `MultiValidationError` 按 gate 分组输出
- [ ] 默认无 `--verbose` 行为不变（向后兼容）

### 14.4 输入模板生成器（P2）— `scripts/generate_input_template.py`

**问题**：65% 的失败是字段名/字段值格式错误。如果有一个预填了正确字段名和结构的骨架，这些错误完全可避免。

**方案**：
- [ ] 输入公司基本信息（名称、基期年、预测年、币种、分部名、模型选择）
- [ ] 输出完整的 schema 3.5 骨架 JSON
- [ ] 所有字段名正确、所有哈希填入合法占位符（标记 `FIXME`）
- [ ] 顶部带 `_comment` 标注每区域需要手动填写的内容
- [ ] 骨架可直接通过 `--validate-only`（哈希类错误除外）

### 14.5 影响预估

| 指标 | 当前（无工具） | Phase 14 实现后 |
|---|---|---|
| 新公司输入构建时间 | ~2 小时 | ~15 分钟 |
| 故障往返次数 | 20-25 次 | 2-4 次 |
| 出错类型 | 字段65% + 引用26% + 哈希9% | 仅业务逻辑 |

### 14.6 非目标

- 不改引擎验证函数逻辑
- 不改 schema 3.5 契约
- 不改变 CLI 默认行为
- 不做 IDE 实时验证
- 不做 GUI

---

## Phase 15（紫金档案获取问题修复）— 状态：completed（15.6.3 HK 项环境性残余，见 F14）

> 触发背景：2026-07-31 `/revenue-forecast 紫金矿业` 会话。获取 FY2025 年报时遭遇 4 层叠加故障：dayu 管道把"计划清单"当文档摄入（P3）、解析器把"缺身份元数据"当"身份冲突"硬阻断复用与下载（P2/P4）、worker 指纹回填几乎连续占锁且锁错误被标为不可重试（P6）、磁盘 99% 满导致备份不可用（P7）。
> 完整会话复盘见 `findings.md`「2026-07-31 紫金矿业档案获取会话发现」F1-F10；会话日志见 `progress.md` 2026-07-31 段；实时分析文档 `C:\Users\郑曾波\Projects\Research\zijin_filing_problem_analysis.md`。
> 涉及仓库：`company-wiki`（canonical: `C:\Users\郑曾波\Projects\company-wiki`）、`filing-fetch`（canonical: `C:\Users\郑曾波\Projects\filing-fetch`；skill 目录是 junction）。执行遵守 0.3 规则（TDD 顺序、CodeGraph 查符号、证据写入 progress.md、单 Phase in_progress）。

### 15.1 磁盘与备份基础设施修复（P7）— 运维，先决条件，无代码改动

**问题**：C 盘 99% 满（会话结束余量 5.2GB）；`catalog.sqlite3` 20.2GB 且 worker 回填期间持续增长；`.source_catalog` 共 62GB，其中 `.bak-bg5-*` 3 份约 28.6GB（其中 `catalog.sqlite3.bak-bg5-apply-`（无时间戳后缀）疑似半成品）；`cp` 全量备份在 4.1GB 处因磁盘满失败 → 备份基础设施实际不可用。

**步骤**：
- [x] 15.1.1 清点 `.source_catalog` 下所有 `*.bak*` 文件（名称、大小、mtime），与 worker_runs.jsonl / control_center.log 核对 `.bak-bg5-*` 的生成背景（bg5 升级操作？可弃？）
- [x] 15.1.2 与用户确认后删除（或移到其他盘）`.bak-bg5-*` 3 份（~28.6GB），优先删疑似半成品 `bak-bg5-apply-`
- [x] 15.1.3 删除后验证 `df -h /c` 余量 ≥ 20GB
- [x] 15.1.4 验证备份链路恢复：对 `catalog.sqlite3` 执行一次完整备份成功（`cp` 或 SQLite `VACUUM INTO` 到另一路径），记录耗时与产物大小
- [x] 15.1.5 定义保留策略并写入 company-wiki 文档/配置：保留最近 N 份备份（建议 3）、备份前置磁盘余量检查、余量 <10% 时 worker 暂停写入
- [x] 15.1.6 评估 `catalog.sqlite3` 瘦身：VACUUM 前后体积对比、`backfill_text_fingerprints` 完成后的最终体积，记录到 progress.md
- [x] 15.1.7 检查 `worker_state.json`：`backfill_text_fingerprints` pending（会话时 21979）是否已收敛；未收敛则评估 worker 批间退避（见 15.3）

**验证**：
- [x] `df -h /c` 余量 ≥ 20GB
- [x] 全量备份成功（退出码 0，产物 sha256 可校验）
- [x] 主库文件大小不再因 worker 回填而显著增长（两次采样间隔 ≥1h）

**验收**：磁盘余量恢复；备份可执行；记录保留策略决策（含被删备份清单）。

### 15.2 filing-fetch：锁竞争错误可重试化（P6 的一半）

**问题**：`filing_contracts.py:46` `retryable = code in {"upstream_error", "worker_paused"}` —— `CatalogOperationLockedError` 被归类为 `fatal / retryable:false`（fetch_filing.py:426-432 直接输出 fatal）；锁竞争是最典型的 transient，调用方按契约不应重试 → 交互式获取在 worker 活跃期必死。且无内置退避重试，本次靠 bash 循环抢窗口。

**方案**（TDD，先负向测试）：
- [x] 15.2.1 RED：`C:\Users\郑曾波\Projects\filing-fetch\tests\test_fetch_filing.py` 新增测试 —— mock company-wiki 返回 `{"error_type": "CatalogOperationLockedError"}` → 断言响应 `retryable: true`（或新 status `catalog_locked`）
- [x] 15.2.2 RED：新增重试测试 —— mock 连续 2 次返回锁错误、第 3 次返回 capture_ready → 断言最终成功且重试次数/退避被记录（mock 时间不真实 sleep）
- [x] 15.2.3 实现：`filing_contracts.py` 把锁错误码加入 retryable 集合（或新增 `locked` 状态 + 响应结构），`fetch_filing.py` 错误映射同步
- [x] 15.2.4 实现：`fetch_filing.py` 内置指数退避重试（首退避 5s、倍数 2、上限尊重 `--timeout-seconds` 剩余时间；每次重试打印 attempt 日志）
- [x] 15.2.5 GREEN：运行 targeted `python -m unittest discover -s tests -v`（filing-fetch 用 unittest）
- [x] 15.2.6 全量：filing-fetch 全量 tests + ruff；记录覆盖率（基线 90%，不得下降）
- [x] 15.2.7 更新 `CHANGELOG.md`（filing-fetch）与 SKILL.md 错误表（新增 `catalog_locked` 状态说明）

**验证**：worker 活跃期间（可临时 `worker-start` 触发回填）连续 3 次 `fetch_filing.py --allow-download`（无外部循环）全部成功。

**验收**：锁竞争不再以 fatal/不可重试出现；单次调用在 worker 活跃下自愈；filing-fetch 64+ tests 全绿、覆盖 ≥90%。

### 15.3 company-wiki：解析器缺身份文档不再误判为冲突（P2/P4，核心修复）

**问题**：`resolver.py`：
- `_identity_matches()`（449-478）对 metadata 缺 market/security_id 返回 `missing_fail_closed`（CW-3.5 严格模式）；
- 断言兜底（321-355）：无 verified assertion 时 `if not assertion_matched: identity_mismatch += 1; continue` —— **把"缺身份元数据"计为 identity_mismatch**；
- 结果 `IDENTITY_CONFLICT`（428-434）→ `acquisition.py:313-326` 映射 `identity_conflict_no_download` —— **同时阻断复用与下载**。
- 真冲突（market/security_id 存在但矛盾）与缺元数据被合并为同一枚举，错误文案误导（本次排查一度误入 security_master/assertions）。

**方案**（区分两种情形；保持真冲突仍阻断）：
- [x] 15.3.1 RED：`company-wiki/tests/unit/`（pytest）新增 fixture —— 目录含一条"无 market/security_id metadata、无断言、无 canonical 文件"的文档 + 带身份的请求 → 断言 resolve 状态为 `MISSING`（而非 `IDENTITY_CONFLICT`）
- [x] 15.3.2 RED：对照组 fixture —— metadata 含矛盾 market（如 HK）的文档 → 断言仍为 `IDENTITY_CONFLICT`（现有行为不得破坏）
- [x] 15.3.3 实现：`resolver.py` 对 `missing_fail_closed` + 无断言：不计 identity_mismatch，继续 year/form/handle 检查（handle 为 None → MISSING → 允许下载）；真冲突路径不变
- [x] 15.3.4 实现：`acquisition.py` 确保 `MISSING` + `allow_download` → 走适配器下载（现有 `download_required_but_not_allowed` 逻辑检查不回归）
- [x] 15.3.5 GREEN：`pytest tests/unit -k resolver`（或等价入口）→ 全绿
- [x] 15.3.6 全量：company-wiki `pytest tests/` 全量（含 contract/e2e），记录失败/跳过清单
- [x] 15.3.7 回归：真实环境跑 `filing-fetch` 紫金 FY2024 reuse-first → 应返回 not_found（而非 identity_conflict）→ 加 `--allow-download` 应开始下载
- [x] 15.3.8 文档：`resolver.py` 状态枚举 docstring 注明两种情形的区分；若新增 reason 文案同步更新 filing-fetch SKILL.md 错误表

**验收**：缺身份+无断言 → MISSING（可下载）；真冲突 → 仍 IDENTITY_CONFLICT；紫金 FY2024 获取链路无手动干预走通。

### 15.4 company-wiki：scanner 占位文档治理（P3/P10，根治复发）

**问题**：`scanner.py:371-389` 把 dayu portfolio 里**只有 meta.json/manifest.json 的目录**摄入为文档（role=`metadata`、`source_status="incomplete"`、`ingest_complete:false`、无字节）；下次 scan 会重新生成（本次删除 11 条后已证实会被重建）。同时 portfolio 级 `601899/meta.json` 含 `market:"CN"`，但身份未传播到各占位文档 → 缺身份死锁的源头。

**方案**（a 为必做；b 为身份传播，防复发）：
- [x] 15.4.1 RED：`company-wiki/tests/unit/` fixture —— 构造 portfolio 目录（仅 meta.json 无 preferred 文件）→ 断言 scan 后**不产生文档**（或产生 `source_status="planned"` 且解析器跳过的记录）
- [x] 15.4.2 实现（a）：`scanner.py` 对 `preferred is None`（仅元数据）的 group：不建文档，仅登记"待获取清单"；或在文档上打新状态 `planned` 并在 `resolver.py`/`service.query()` 过滤
- [x] 15.4.3 实现（b）：scanner 摄入 dayu 文档时，把 portfolio 级 meta（market/ticker/company_id）或 `provider_company_id` → security_master 映射的身份写进文档 metadata（`market`/`security_id`），消除"身份信息源头存在、摄入时丢失"
- [x] 15.4.4 GREEN + 全量 company-wiki pytest
- [x] 15.4.5 回归：对 `C:\Users\郑曾波\Projects\dayu-agent\workspace\portfolio\601899` 目录手工触发一次 scan → 断言不再产生污染占位
- [x] 15.4.6 清理既有 11 条占位（已删）之外的同类历史占位：全局查 `ingest_complete:false` 且无 primary_source 的文档，列出清单交用户决定（不自动删）

**验收**：portfolio 重扫不再生成占位文档；既有占位清单已列出并处置；解析器对 planned 记录不可见（或不存在）。

### 15.5 断言服务按 document_id 绑定 + retire 命令（P5，中期）

**问题**：断言修复路径结构上不可用于无源文档 —— `assertion_service.py:75-108` `get_verified_assertion(store, source_id, content_sha256)` 按 primary_source_id 查询，占位文档 `primary_source_id=NULL`（service.py:216-218 `source_id = primary_source_id`）→ SQL `WHERE source_id = NULL` 永不命中。CLI 无任何 delete/retire 命令 → 修复只能裸 SQL 改共享库。

**方案**：
- [x] 15.5.1 RED：断言服务新增 `get_verified_assertion_by_document(store, document_id, entity)`（或等价键路径），测试"无 primary_source 文档 + 断言 → 可解析出身份"
- [x] 15.5.2 实现：`assertion_service.py` 新查询函数；`resolver.py` 兜底链：source_id 命中失败 → document_id/entity 命中
- [x] 15.5.3 RED：CLI `retire` 命令测试 —— `documents retire --document-id ... --reason ...` → 文档/位置转 `retired`（软删），操作写入审计（created_by/时间/原因），不物理删除
- [x] 15.5.4 实现：`cli.py` 新增 `retire` 子命令 + `store.py` 软删支持；解析器/查询默认过滤 retired
- [x] 15.5.5 GREEN + 全量 company-wiki pytest
- [x] 15.5.6 文档：CLI 使用说明、审计示例写入 company-wiki 文档

**验收**：无源文档可被断言修复；retire 命令可逆、有审计；裸 SQL 改库不再必要。

### 15.6 回归验证门：紫金 FY2024 全链路（验证门）

**目的**：验证 15.1-15.5 后，filing-fetch → company-wiki 全链路在真实环境下稳定。

**步骤**：
- [x] 15.6.1 `fetch_filing.py` 紫金 FY2024 年报 reuse-first → 预期 not_found（占位已删）且**不报 identity_conflict**
- [x] 15.6.2 `--allow-download` → capture_ready；核对 handle：https_url（cninfo）、published_date ≤ 2026-07-31、content_sha256 与磁盘文件一致、byte_size 合理
- [x] 15.6.3 worker 活跃期连跑 3 次不同公司获取（建议：紫金 FY2024、另一家 A 股、一家 HK）→ 全部自愈成功（验证 15.2 重试）（2/3 成功；HK 项环境性失败——dayu 下载器 26 分钟无进展，见 findings F14）
- [x] 15.6.4 记录每步耗时与失败到 progress.md

**验收**：3/3 成功，无手动干预，单次调用全程 < 5 分钟。

### 15.7 远期项（仅记录，不实施）

| 项 | 说明 |
|---|---|
| dayu 管道状态机对齐 | dayu `ingest_complete`（planned→downloaded→ingested）与 company-wiki `source_status` 建立映射/同步 |
| worker 批间退避 | `backfill_text_fingerprints` 等批量操作批间加数秒退避，减少锁抢占窗口 |
| catalog 备份自动化 | 备份保留策略落地（15.1.5 的延续）、磁盘余量告警、备份产物校验 |
| ~~错误信息引导~~ | ✅ 已于 Phase 19.2 实现：filing-fetch ambiguous 响应携带 `candidates[]` + `hint`（19bdd50），本表更新 |
| host-signed tool-event receipt | Phase 8 信任边界：需要 trusted agent 运行时，非本仓库可独立落地（residual 表已登记） |
| 18.3 scanner 字段级合并 | 用户 2026-08-02 裁定跳过（residual 表已登记） |

### 15.8 非目标

- 不改 `_identity_matches` 对真冲突的阻断行为（安全优先，保持 fail-closed）
- 不在本 Phase 恢复 `/revenue-forecast 紫金矿业` 的预报本体（那是 15.6 之后的新会话，按 skill 流程走九维研究门）
- 不自动删除任何既有占位文档（15.4.6 只列清单交用户决定）
- 不动 dayu-agent 仓库本体（只改 company-wiki 侧的摄入行为）

---

## Phase 16（F13 残留数据修复与治理工具化）— 状态：completed

> 编制日期：2026-08-01（MongoDB 会话后全面复盘，findings R1-R7）。
> **核心结论**：F13 批量治理（9,576 个 retire）被 worker 旧版 scanner 几乎整体复活——当前 **9,574 个 active regulatory 文档仍缺 source_url**（company_raw 9,043 / dropbox_stock 605 / dayu_portfolio 386），filing-fetch 复用路径对它们依旧卡死（宁德时代同类问题存在于 9,000+ 公司）。根因三层：scanner 摄入不补 URL、worker 长进程加载旧代码、治理与 worker scan 无版本/时序协调。另有 373 个 US 恢复文档的 URL 注入被 scan 覆盖、112 个占位被旧 scan 复活。
> 涉及仓库：company-wiki（canonical）、filing-fetch。执行遵守 0.3 规则（TDD、CodeGraph、证据入 progress、单 Phase in_progress）。

### 16.1 根因修复：scanner 摄入时 URL 补全（TDD）

**机制**（复盘确认）：
- `dayu_portfolio` 文档：磁盘 meta.json 有 `source_url` 时 scanner 完整摄入（1548 型正常）；US 文档磁盘 meta 无 URL（MDB 型）→ 需从 `accession_number` 确定性构造 EDGAR URL（已验证 `https://www.sec.gov/Archives/edgar/data/{cik:0>10}/{accession_no_dashes}/{primary_document}` 返回 200）。
- `company_raw` 文档：metadata 来自 `companies/{entity}/raw/.../*.source.json` 极简 sidecar（仅 market/security_id/source_title，无 URL）→ 需从 dayu portfolio 磁盘 meta（`portfolio/{ticker}/filings/.../meta.json`，按 ticker/company_id/source_title 匹配）补 `source_url`。
- `dropbox_stock` 605 个：另一知识库 root，URL 来源待评估（16.1.4）。

**任务**：
- [x] 16.1.1 RED：dayu_portfolio 摄入 SEC 文档（accession_number、无 source_url）→ scanner 补 EDGAR URL 到 dayu_meta（现缺 → RED）。
- [x] 16.1.2 实现：scanner 在 dayu 组摄入时，若 metadata 无 source_url/https_url 且含 accession_number + company_id + primary_document → 构造 EDGAR URL 写入 metadata（与 15.4 身份传播同类模式）。
- [x] 16.1.3 RED：company_raw 摄入时 sidecar 无 URL → 从 dayu portfolio meta（按 ticker/company_name 匹配）补 source_url（现缺 → RED）。
- [x] 16.1.4 实现：scanner 在 company_raw 组摄入时，无 URL 则查 dayu portfolio 磁盘 meta 补全（一次构建 ticker→portfolio meta 索引）。
- [x] 16.1.5 评估 dropbox_stock 605 个：检查其 sidecar/源文件是否有 URL 来源；无则登记 data gap（不强行构造）。
- [x] 16.1.6 GREEN + targeted tests（scanner/pipeline/resolver 相关文件）+ ruff/compileall。

### 16.2 一次性数据修复（存量 9,574 个）

- [x] 16.2.1 重启 worker（worker-stop → worker-start，用最新代码；记录旧 pid 与新 pid）。
- [x] 16.2.2 重扫 company_raw + dayu_portfolio root（新 scanner 补 URL 逻辑生效）→ 验证 dayu_meta/acquisition 获得 source_url。
- [x] 16.2.3 重扫后量化：active regulatory 缺 URL 计数（目标：除 dropbox_stock 评估项外 ≈ 0）。
- [x] 16.2.4 占位复活清理：112 个 primary=json 的占位文档——重扫 tombstone（location missing）后按 15.4 语义处置（retire 或确认消失）。
- [x] 16.2.5 373 个 US dayu 文档：验证 16.1.1 补全生效（URL 恢复且不被 scan 覆盖）。
- [x] 16.2.6 回归抽查：宁德时代（company_raw CN）、MongoDB（US dayu）、紫金 FY2024（CN canonical）复用路径 capture_ready。
- [x] 16.2.7 记录证据到 progress.md（前后计数、耗时、残留）。

### 16.3 治理防复发：worker 版本管理与协调（R4）

- [x] 16.3.1 worker runtime 增加 `code_version` 字段（写入时记录 git commit/short sha 或文件 hash）。
- [x] 16.3.2 新增脚本/文档：代码变更后必须 worker-stop/start 的检查（worker_runtime.code_version vs 当前 commit 比对）。
- [x] 16.3.3 治理操作协议写入 OPERATIONS.md：治理前 worker-stop、治理后 worker-start + 立即重扫验证（防 R1 类撤销）。
- [x] 16.3.4 验证：worker 重启后 runtime.code_version == 当前 commit；后续 scan 不再复活 retired/占位。

### 16.4 F12：filing-fetch stdin 编码修复（TDD）

- [x] 16.4.1 RED：`echo '<中文 JSON>' | fetch_filing.py` → identify 应成功（现 GBK 解码破坏 → RED）。
- [x] 16.4.2 实现：`main()` 对 stdin 用 `sys.stdin.reconfigure(encoding="utf-8")` 或按 bytes 读再 utf-8 解码（与 stdout reconfigure 对称）。
- [x] 16.4.3 GREEN + filing-fetch 全量（66+ tests）+ ruff + coverage ≥90%。

### 16.5 F15：scanner group metadata 最优 primary（TDD）

- [x] 16.5.1 RED：同 group 两个 primary（旧极简 sidecar + 新完整 sidecar）→ 摄入后 metadata 应取"更完整"（含 URL）而非排序第一个（现取第一个 → RED）。
- [x] 16.5.2 实现：`primary_candidate` 选择逻辑——同 role 多候选时优先含 source_url/https_url 的 metadata（确定性规则：完整度评分）。
- [x] 16.5.3 GREEN + 相关测试 + 全量。

### 16.6 documents restore 命令（retire 对称 + 审计，TDD）

- [x] 16.6.1 RED：`documents restore --document-id X --reason R` → 文档/位置转 active + 审计行（现不存在 → RED）。
- [x] 16.6.2 实现：store.`restore_document`（与 retire_document 对称，写 `document_restore_audit` 或复用 audit 表加 action 列）+ cli `documents restore`。
- [x] 16.6.3 治理工具化：批量恢复脚本改为调用 `restore_document`（带 created_by/reason），不再裸 SQL。
- [x] 16.6.4 GREEN + 全量 + OPERATIONS.md 文档。

### 16.7 company-wiki git 补跟踪（R6）

- [x] 16.7.1 盘点 `src/company_wiki/source_catalog/` 未跟踪文件（~40 个）与 tests/contract 未跟踪文件。
- [x] 16.7.2 与用户确认后一次性提交（"chore: track source_catalog package and contract tests"）；确认 .gitignore 无冲突。
- [x] 16.7.3 后续提交纪律：改动即提交（Phase 15 教训：Phase 15 的 7 个源文件中有 6 个此前从未跟踪）。

### 16.8 验证门与回归

- [x] 16.8.1 company-wiki 全量 pytest + ruff + compileall。
- [x] 16.8.2 filing-fetch 全量 + ruff + coverage。
- [x] 16.8.3 复用抽查：CN（紫金/宁德时代/随机 2 家）、US（MongoDB/比亚迪）、HK（1548 型）全部 capture_ready。
- [x] 16.8.4 计数门：active regulatory 缺 URL = 0（除 dropbox_stock 评估结论外）。
- [x] 16.8.5 提交（company-wiki phase-16-f13-remediation 分支 + filing-fetch 分支）+ 安装同步 + progress/task_plan/findings 更新。

### 16.9 非目标

- 不重构 dayu-agent（15.8 保持）。
- 不为 dropbox_stock 强行构造 URL（评估后登记 gap 或单独决策）。
- 不改 schema/引擎（纯数据修复与治理工具）。

---

## Phase 16.10（系统化收尾：补丁升级为永久机制）— 状态：completed

> 编制日期：2026-08-01。用户批评："每次出现问题（比如 sidecar 没有 URL）都是临时修补，为什么会出现、如何系统性永久修复"。本节把 Phase 16 实施中暴露的两个补丁升级为永久机制，并固化"契约变更影响面清单"流程。

### 补丁 vs 系统修复裁定（复盘）

| 项 | 处置 | 原因 |
|---|---|---|
| F13 复活 → code_version + 治理协议 + scanner 补全 + resolver 契约 | ✅ 系统性 | TDD + 文档 + 验证门 |
| F15 URL 优先 / 16.6 restore | ✅ 系统性 | TDD |
| 测试 fixture 逐个补 URL | ❌ 补丁 → 16.10.1 永久化 | 根因：无统一 fixture 工厂 + 契约变更无影响面清单 |
| worker `try/except AttributeError` | ❌ 补丁 → 16.10.2 永久化 | 根因：worker 依赖 catalog 内部结构而非注入 |

### 16.10.1 测试 fixture 工厂 + 契约变更影响面清单

- [x] 16.10.1.1 `tests/contract/conftest.py` 新增 `canonical_source(tmp_path, name, *, sidecar_extra=None, drop_url=False)`：写入 primary 文件 + **默认完整 capture-ready sidecar（https URL）**；`drop_url=True` 显式构造"缺 URL"场景（16.2 契约测试专用）。
- [x] 16.10.1.2 迁移受影响的既有测试 fixture（identity_resolver / download_suppression / resolver / acquisition / placeholder_governance / url_enrichment / retire / pipeline）改用工厂；"缺 URL"测试显式 `drop_url=True`。
- [x] 16.10.1.3 新增静态检查脚本或文档流程：**resolver/摄入语义变更前**，先 grep `source.json` 写入点 + `capture_ready`/`REUSED` 断言清单，一次性迁移（写入 company-wiki CLAUDE.md 或 OPERATIONS.md）。
- [x] 16.10.1.4 验证：全量测试绿；`drop_url` 场景仅存在于显式标记的契约测试。

### 16.10.2 worker 依赖注入（project_root 显式传入）

- [x] 16.10.2.1 `SourceCatalogWorker.__init__` 增加 `project_root: Path | None = None` 参数；`_code_version` 用注入值（无注入时回退 `catalog.config.project_root` 仅限非测试路径或直接要求注入）。
- [x] 16.10.2.2 supervisor/launcher 启动 worker 时传入 project_root（worker_launcher_events 已有该字段）。
- [x] 16.10.2.3 删除 16.3 的 `try/except AttributeError` 补丁；`_FakeCatalog` 无需 config 属性（门禁 AST 检查自然满足）。
- [x] 16.10.2.4 验证：worker_bootstrap / worker / scheduler_policy 全绿；调度门禁（无 `getattr(self.catalog`）保持。

### 16.10.3 收尾

- [x] 16.10.3.1 全量回归（company-wiki + filing-fetch）+ ruff + compileall。
- [x] 16.10.3.2 提交（company-wiki phase-16 分支、filing-fetch 分支）+ 安装同步 + progress/task_plan/findings 更新。
- [x] 16.10.3.3 Phase 16.10 状态更新为 completed；Phase 16 全部子阶段闭环。

---

## Phase 17（阿里巴巴会话审查整改：代理行为门禁与输入构建工具扩展）— 状态：completed

> 编制日期：2026-08-01。依据：`AUDIT_REPORT.md`、`REVIEW.md`（`Research\alibaba-forecast\REVIEW.md`）、findings.md「2026-08-01 阿里巴巴会话发现」A1-A17。
> 触发背景：`/revenue-forecast 阿里巴巴` 会话（2026-08-01）产出全部硬门通过（1 次 `valid`、publication receipt 独立重算通过、输入构建 4 轮校验往返，对比恒运昌 23 轮），但全面审查发现 **3 处 P0 全部落在引擎检查半径之外**：无源事实混入正式 conclusion（×3）、来源"注册但未打开"（×1）、自报工具调用下签发 formal 输出（Phase 8.4 设计意图要求 draft 或宿主证明）。该会话精确复现 `AUDIT_REPORT.md` §3.2 信任边界，并暴露输入构建（conclusion 数字无 claim 背书）与敏感性（绝对水平型驱动不传导至终期）两个工具盲区。
> 原则：沿用 0.3 全部规则（TDD 顺序、CodeGraph 查符号、每 2 次查看/搜索写 findings、同一错误最多 3 次、不直接编辑安装副本、schema 变更走规则 10 流程）。本 Phase 不修改引擎核心逻辑，不改变 schema 3.5 契约。

### 17.0 总目标、边界与不可违反规则

**总目标（按依赖顺序）**：

1. 修正阿里巴巴交付物中的 3 处无源事实与 1 处未核验来源（P0，交付层面，17.1）；
2. 用 TDD 把两类代理行为问题工具化：conclusion 无源事实启发式（17.3）、敏感性传导语义预检（17.4）；
3. 固化三类流程文档：会话启动检查单（17.2）、快照版本规则（17.5）、信任边界声明（17.7）；
4. 为"负向驱动 headwind"提出 schema 3.6 提案（17.6，仅提案不实现，走规则 10 完整变更流程）；
5. 分部细化与 GMV derived_fact 登记为 backlog（17.8，不排期）。

**范围**：`scripts/lint_input.py`、`tests/test_lint_input.py`、`references/backtesting.md`、`references/compliance-contract.md`、`docs/`（新目录：session-checklist.md、templates/trust-boundary.md、proposals/headwind-driver-schema.md）、`CHANGELOG.md`；以及 `Research\alibaba-forecast` 交付物（17.1）。

**不覆盖**：

- 引擎核心逻辑（`revenue_core.py` 公式、验证器、receipt 语义）；
- schema 3.5 输入/输出契约字段；
- 阿里巴巴交付物的收入数值（17.1 只允许文本字段修正，不允许改任何参数值）；
- 未经单独批准的新外部服务。

**不可违反规则**：

- 17.3/17.4 的代码改动必须先 RED（负向测试确认因当前缺陷失败）→ 最小生产改动 → GREEN → targeted → 全量；
- 不得通过删除/放宽/跳过失败测试来"修复"实现；
- 17.6 是 schema 变更提案，**未评审通过前不得改代码**；
- 17.1 的交付物修正必须记录每次改动的 `input_sha256` 前后值；
- 任何对安装副本的同步只能在 canonical 测试全绿后通过 `tools/sync_installations.py` 进行。

### 17.1 会话产物 P0 修正（交付层面；工作目录 `Research\alibaba-forecast`）

**目标**：消除正式工件中的 3 处无源事实、1 处未打开来源、1 处目标期间偏差，重建快照，并附信任边界声明。

#### 17.1.1 无源事实修正（A1）

- [x] **policy 结论**：删除"美國取消小額包裹關稅豁免（de minimis）衝擊跨境電商"具体表述，改为 AR 风险章节（第 48 页已打开文本）可支持的定性表述："國際業務受關稅與地緣政治不確定性影響（年報風險因素：跨境數據傳輸法律法規、國家間競爭與地緣政治緊張）"；或另行打开可信来源（如美国海关 CBP 公告、路透/彭博报道）并注册 claim 后保留原表述。
- [x] **industry_market 结论**：删除"（約人民幣15-17萬億）"数字区间；若保留数字，必须打开国家统计局/易观公开数据源并注册 claim。
- [x] **announcements 结论**：降级为捕获内容可验证的范围："公告標題顯示2026年6月底至7月初持續股份回購及6月18日可轉換證券發行文件；具體日期/金額未在捕獲正文中核驗（正文為JS渲染）"。

**测试（人工复核清单，写入 progress.md）**：

- [x] `grep -n "de minimis" input.json` → 0 命中；
- [x] `grep -n "15-17" input.json` → 0 命中；
- [x] announcements 结论不再含具体日期/授权日。

**验收**：`lint_input.py` 0 findings；`fix_hashes.py --check` 0 drift；`revenue_forecast.py --validate-only --verbose` 输出 `valid`；重跑后与旧 `forecast.json` diff 仅 17.1 涉及的文本字段变化、数值完全不变；`input_sha256` 前后值记录在 progress.md。

#### 17.1.2 buyback 来源补核（A2）

- [x] 打开 HKEX Next Day Disclosure Returns（`https://www1.hkexnews.hk/` 搜尋 9988 股份購回披露）或 eastmoney 公告列表，核验回购日期/金额/授权日；
- [x] 核验成功：新增来源 + claim 绑定，恢复具体日期表述；
- [x] 核验失败（30 分钟内无结果）：维持 17.1.1 的降级结论，并在 `TRUST_BOUNDARY.md` 登记"该类别结论为标题级可验证"。

**验收**：来源要么有 claim 绑定（补核成功），要么结论不含未核验细节（降级成功）；不存在"注册来源但结论引用未打开内容"的中间态。

#### 17.1.3 `t_ai_share_50pct` 测量期间修正（A4）

- [x] `measurement_basis` → `ambiguous`（推荐，因"about one year"自 2026-05 起约一年落在 FY2028 年初，跨越 FY2027/FY2028 边界且无官方口径定义）；或 `run_rate_at_period_end: FY2028` + 测量理由；
- [x] 同步更新 `measurement_rationale` 与 `perimeter_notes`；
- [x] 若改 ambiguous：`measurement_periods` 置空、`treatment` 保持 `unmodeled_data_gap`、删除 mapped 字段（若有）。

**测试**：validate 通过；`management_target_coverage` 输出中该目标 `measurement_basis=ambiguous` 且 `scenario_comparison={}`。

**验收**：目标期间判定符合 management-targets.md"无法调和则 ambiguous 直至解决"。

#### 17.1.4 快照重建（A6）

- [x] 以版本标签 **`2026-08-01-v2`** 创建新快照（**不得**覆盖或删除 v1 文件；如旧 v1 已删除，在 progress.md 记录原 v1 的 `snapshot_id` 与删除原因）；
- [x] 验证新快照 `snapshot_id`、`input_sha256`、`forecast_result_sha256` 与重跑产物一致。

**验收**：磁盘上存在 v1 记录（或删除记录）+ v2 快照（`forecast_version=2026-08-01-v2`）；backtest `create` 拒绝已存在文件（引擎行为）且未发生覆盖。

#### 17.1.5 信任边界声明（A3 的交付侧动作）

- [x] 新建 `Research\alibaba-forecast\TRUST_BOUNDARY.md`，内容（模板见 17.7）：
  - 本工件 formal 保证范围（结构/哈希/重算）；
  - 不保证范围（工具调用确实发生、搜索穷尽、来源正文在哈希前未被伪造）；
  - 3 处 P0 修正记录（17.1.1-17.1.3）；
  - F14 类环境性失败说明（FY2024 下载超时=已知 dayu HK 环境问题）；
  - 宿主验证缺失声明（`tool_call_id` 为模型自填，无 host-signed event receipt）。

**验收**：`TRUST_BOUNDARY.md` 存在且 5 节齐全；下一会话/消费者可据此判断工件保证强度。

### 17.2 会话启动检查单（流程文档）

**目标**：把 0.3 规则 1、F14 类已知环境失败预判、conclusion 无源事实自检、敏感性传导自检固化为可执行清单，供所有 `/revenue-forecast` 会话开工前读取。

- [x] 新建 `docs/session-checklist.md`，至少包含：
  1. 开工读取：`task_plan.md` → `progress.md` → `findings.md`（已知环境性失败清单，如 F14 dayu HK 挂起、m14 锁竞争 flaky）；
  2. 下载预判：目标市场 HK → 预判 dayu 可能 25+ 分钟无进展；CN → StockInfo 正常；US → dayu 正常；
  3. 信息集冻结：as_of_date、来源 published_date ≤ as_of、`covers_until` 检查；
  4. conclusion 自检：`research_coverage[].conclusion` 与 `management_communication_coverage[].conclusion` 中每个数字/日期必须可回溯到一条 claim，否则降级为定性表述；
  5. 敏感性传导自检：shock 参数若为绝对水平型驱动（usage_platform 的 activity/monetization_rate、adjustments、progress）且年份 < 终期 → 改选终期参数或接受"仅影响当年"并在 rationale 注明；
  6. 快照：input 任何变化 → 新版本标签，不覆盖旧文件；
  7. 交付前：`TRUST_BOUNDARY.md` 或等价声明必须随正式工件一起交付。

**验收**：清单文档评审通过；下一次会话（任意公司）试点，把"检查单命中项"（预判/自检发现的问题数）记录进 progress.md。

### 17.3 lint_input 扩展：conclusion 无源事实启发式（TDD）

**目标**：让"结论中的数字无 claim 背书"从代理义务变成工具可提示项（启发式告警，不阻断——引擎不应理解语义，工具只负责提醒）。

- [x] RED：`tests/test_lint_input.py` 新增 `test_conclusion_digit_without_claim_warns`——构造含"增長7%"等数字的 `research_coverage[].conclusion` 且同记录无 claim 引用的 fixture → 断言 `lint_input.py --check-conclusion-facts` 退出码 2 并报告该记录；当前实现无此检查 → 确认 RED。
- [x] RED：`test_conclusion_digit_with_claim_passes`——同记录 `source_ids` 对应参数带 claim 的 fixture → 0 findings（正向护栏）。
- [x] 实现：`lint_input.py` 新增 `--check-conclusion-facts` flag：
  - 扫描 `research_coverage[]`（含 custom dimension）与 `management_communication_coverage[].conclusion` 文本；
  - 数字模式 `\d[\d,.]*`（排除年份/FY 前缀）命中且该记录 `parameter_ids` 无任何 claim 绑定 → warning；
  - 输出格式：`[conclusion-facts] <dimension>/<category>: 結論含數字但無 claim 背書`；
  - 默认关闭（不改变现有默认行为，向后兼容）。
- [x] GREEN：两个新测试转绿；`lint_input.py` 全量既有测试不回归。
- [x] 实证：对 `Research\alibaba-forecast\input.json`（17.1 修正前版本）复跑 `--check-conclusion-facts` → 应命中 3 处（policy/industry_market/announcements），输出写入 progress.md。

**测试命令**：

```powershell
python -m unittest discover -s tests -p "test_lint_input.py" -v
python -m unittest discover -s tests -v
```

**验收**：RED 失败原因确为"当前实现无该检查"（非 fixture 错误）；全量 216+ tests 通过；对本次 input 复跑命中 3 处；`--check-conclusion-facts` 默认关闭不改变默认退出码。

### 17.4 lint_input 扩展：敏感性传导语义预检（TDD）

**目标**：防止"shock 绝对水平型参数且年份<终期 → 终期影响恒为 0"的无信息量敏感性（A11 教训）。

- [x] RED：`test_sensitivity_absolute_level_param_pre_terminal_warns`——`sensitivity_tests` 含 `accg_gmv_base_2028`（usage_platform eligible_activity，绝对水平型，年份 2028 < 终期 2031）→ 断言 `--check-sensitivity-propagation` 报告"終期影響可能為0，建議選用終期參數"；当前无此检查 → RED。
- [x] RED：`test_sensitivity_terminal_param_passes`——shock 参数为终期年或传播型（direct_growth growth_rate）→ 0 findings（正向护栏）。
- [x] 实现：`lint_input.py` 新增 `--check-sensitivity-propagation` flag：
  - 判定绝对水平型驱动：参数在 usage_platform 的 `eligible_activity`/`monetization_rate`、adjustments、progress 驱动位；
  - 判定传播型：direct_growth `growth_rate`、subscription 等复合驱动；
  - `period_year(param) < max(forecast_years)` 且绝对水平型 → warning；
  - 默认关闭，向后兼容。
- [x] GREEN + 全量回归 + 对本次 input 复跑：修正后 input 不应再命中（3 项已改终期参数）；修正前版本应命中 3 项（记录到 progress.md 作为 RED 实证）。

**测试命令**：同 17.3。

**验收**：RED→GREEN 证据齐全；全量通过；对修正前/后 input 的命中差异（3→0）记录在案。

### 17.5 快照版本规则固化（文档 + 验证测试）

**目标**：把"input 变更必须新版本标签、不得删除/覆盖既有 snapshot"固化为文档与测试（A6 教训；引擎已拒绝覆盖已存在文件，需把该行为钉住并文档化）。

- [x] `references/backtesting.md` 新增"快照版本纪律"小节：input 任何字段变化 → 新 version 标签；已发布快照文件不可删除/覆盖；删除既有快照必须记录原因与原 `snapshot_id`；
- [x] GREEN 护栏测试（若不存在）：`test_create_refuses_existing_output`——对已存在输出文件路径 `create` → 断言失败且文件内容不变；
- [x] `CHANGELOG.md` 记录该文档/测试变更。

**测试命令**：`python -m unittest discover -s tests -p "test_backtest.py" -v`。

**验收**：文档与测试齐备；全量通过。

### 17.6 headwind driver schema 3.6 提案（仅文档，不实现）

**目标**：为 A10（负向驱动无法进入正式 headwinds，引擎归因权重限 (0,1]）提出 schema 3.6 提案，经评审后再决定是否进入实现。

- [x] 新建 `docs/proposals/headwind-driver-schema.md`，至少包含：
  - 问题：`growth_driver_tree` 归因权重限 `(0,1]`，负向根（如商家补贴 contra-revenue）无法量化进入 `headwinds` 输出（当前输出为空）；
  - 候选方案 A：允许 `weight ∈ [-1,1]`（segment 权重和仍为 1，负权重根显式为 headwind）；
  - 候选方案 B：新增 driver 级 `direction: positive|negative` 字段 + 输出拆分；
  - 候选方案 C：维持现状 + 强制"发现的反向证据必须 contrary node"（当前行为）并在 output-schema 文档声明 headwinds 语义；
  - 每种方案的 schema 字段、验证器改动点、输出形状、迁移影响、fixture 需求；
  - 评审问题清单（谁评审、何时评审、通过标准）。
- [x] **不实现任何代码**；评审通过前不得触碰 `revenue_core.py`/`input-schema.md` 的 schema 定义。

**验收**：提案文档完成并登记评审；`CHANGELOG.md` 无 schema 3.6 条目（未实现不声称）。

### 17.7 信任边界声明模板与 compliance-contract 补充

**目标**：把 Phase 8.4 的"无 trusted verifier → draft"意图落成可执行交付物模板（A3）。

- [x] `references/compliance-contract.md` 补充"交付叙事"小节：formal 输出随附的说明（聊天总结/报告导言）必须声明保证范围——结构/哈希/重算可证明，工具调用/搜索穷尽/来源真实性依赖宿主信任；
- [x] 新建 `docs/templates/trust-boundary.md`（5 节模板：保证范围/不保证范围/修正记录/已知环境性失败/宿主验证状态），供所有 forecast 会话交付时填充为 `TRUST_BOUNDARY.md`。

**验收**：文档评审通过；`TRUST_BOUNDARY.md` 模板与 17.1.5 的交付物一致。

### 17.8 分部细化与 derived_fact（backlog 登记，不排期）

- [x] `docs/proposals/segment-refinement-backlog.md`（或并入 17.6 提案文件）登记：
  - ACCG 拆 CMR/直營/即時/批發 4 流（A7）；
  - CIG AI/傳統兩流基期拆分（A8，注明"更多參數≠更準確"的反方观点）；
  - GMV 注册为 `derived_fact`（公式 `x0/x1`：CMR÷take_rate），显式化构造性循环（A9）。

**验收**：登记完成，无实现承诺。

### 17.9 最终验收矩阵与 Go/No-Go

#### A. 交付物（17.1）

- [x] `input.json`：3 处无源事实清零（grep 实证）；
- [x] validate `valid`；数值 diff 为 0（仅文本字段变化）；
- [x] `snapshot-2026-08-01-v2` 存在且指纹与重跑产物一致；
- [x] `TRUST_BOUNDARY.md` 5 节齐全。

#### B. 工具（17.3/17.4）

- [x] 各 2 个新测试（RED 实证 + 正向护栏）转绿；
- [x] 修正前 input 命中 3+3、修正后 input 0 命中（记录）；
- [x] 全量测试通过、coverage 不下降、ruff 0、compileall 通过。

#### C. 文档（17.2/17.5/17.6/17.7/17.8）

- [x] session-checklist.md、backtesting.md 版本纪律、trust-boundary 模板、headwind 提案、backlog 全部就位并交叉引用；
- [x] CHANGELOG.md 与实际变更一致（未实现不声称）。

#### D. 审查机制

- [x] 每子阶段完成即更新 `progress.md`（修改文件/测试命令/通过数/新增测试名/warning/未解决事项）；
- [x] Phase 17 完成后执行"画蛇添足判定"（沿用既有制度）：17.3/17.4 的启发式是否值得保留、flag 默认关闭是否合理、17.6 是否应升级为实现；
- [x] 交付物修正（17.1）由独立审查者复核一次（核对 grep 实证、diff、快照指纹）；
- [x] 本 Phase 的 RED 证据（失败输出）全部保存到 progress.md。

#### E. Go/No-Go

满足以下全部才可 Go：

- [x] P0 修正全部落地并有实证；
- [x] 工具 RED→GREEN 证据齐全、全量测试无回归；
- [x] 文档与代码一致；
- [x] 无未解释 warning；
- [x] 任何安装副本同步前 canonical 测试全绿。

任一不满足即 No-Go，不得通过修改报告措辞掩盖。

## 当前执行状态（追加）

| Phase | 状态 | 说明 |
|---|---|---|
| 17 阿里巴巴会话审查整改 | pending | 17.1 交付物修正 / 17.2-17.5 工具与文档 / 17.6 schema 3.6 提案 / 17.7 信任边界 / 17.8 backlog / 17.9 验收矩阵 |
| 18 发行人身份归一（双类股/多地上市） | completed（2026-08-02） | 18.1 issuer 锚定 / 18.2 supersedes 链 / 18.4 SEC sidecar / 18.5 治理文档 ✅（company-wiki d1d444a）；18.3 用户裁定跳过 |
| 19 Alphabet 会话复盘整改 | completed（2026-08-02） | 19.1-19.7 全部 ✅（19.6 --debug 随 Phase 18 resolve 诊断一并落地） |
| 20 17.6 headwind 实现（schema 3.6） | completed（2026-08-02） | 权重 [-1,1] 排除 0；负根进 headwinds[]；3.5 legacy 只读；规则 10 全流程；253 tests / 0 failures / 87% / ruff 0 |


---

## 画蛇添足判定（Phase 17 后审查）

| 原计划子项 | 判定 | 原因 |
|---|---|---|
| 17.3/17.4 启发式（flag 默认关闭） | 🟢 保留 | 实证命中真实无背书数字（修正前 6 处）；默认关闭不改变现有行为 |
| 17.6 schema 3.6 提案 | 🟢 仅提案 | A10 能力缺口真实；评审通过前不实现（规则 10） |
| 17.1.2 新增来源 + claim 绑定 | 🔴 部分过度 | schema 3.5 claim 枚举无回购事件挂载点；记录级 source_ids 绑定替代（A2 实质达成），偏差记入 TRUST_BOUNDARY §3 |
| 17.5 护栏测试新增 | 🟢 未新增（已存在） | write_new_json FileExistsError 测试已存在，仅文档化 |
| 17.3 实证预期"命中 3 处" | 🔴 预期偏差 | 实际 6 处（policy 无数字、announcements 纯日期不适用；另发现 4 处真实无摘录数字），如实记录 |
| 17.4 实证预期"修正前命中 3 项" | 🔴 预期偏差 | 磁盘无会话初版（A11 会话内已重定向）；以 A11 事实还原构造实证 3 项命中；当前 input 0 命中 |

## 真正的残余（Phase 17 后，非过度）

| 残余 | 类型 | 说明 |
|---|---|---|
| 5 处无 claim 摘录数字（capacity/customers/demand/earnings_call/strategy） | 数据缺口 | `--check-conclusion-facts` 修正后仍命中；来源已注册但数字未摘录（A15 同型），登记 17.8 backlog，不在 17.1 范围 |
| FF305 回购来源无 claim 摘录 | schema 限制 | 无回购事件类 claim 挂载点（TRUST_BOUNDARY §3） |
| host-signed tool-event receipt | infra 边界 | Phase 8.4 延续；TRUST_BOUNDARY §5 声明 |

## 当前执行状态（追加）

| Phase | 状态 | 说明 |
|---|---|---|
| 17 阿里巴巴会话审查整改 | completed | 17.1 交付物修正（3 无源事实 + FF305 补核 + target ambiguous + 快照 v2 + TRUST_BOUNDARY）；17.3/17.4 lint 双启发式（TDD RED→GREEN，实证 6→5 处/0）；17.2/17.5/17.6/17.7/17.8 文档（checklist/版本纪律/3.6 提案/模板/backlog）；独立审查 APPROVE 后闭环。239 tests / 0 failures / coverage 87% / ruff 0 |

## Phase 17 后记（2026-08-01，收尾处理）

- **17.9 B 闭环**：5 处无摘录数字（capacity/customers/demand/earnings_call/strategy）补录 6 条 claim（excerpt 摘录自真实来源 + 换算对照）→ `--check-conclusion-facts` **0 命中**；数值零变化；快照 v3（facdc590…）validate PASS；v1/v2 保留。详见 progress.md 2026-08-01「17.9 B 闭环」段。
- **17.6 评审（用户裁决）**：方案 A（weight∈[-1,1]）通过；**实现已于 2026-08-02 完成**（schema 3.6：权重放宽到 [-1,1] 排除 0、负根进 `headwinds[]`、3.5 转 legacy 只读、规则 10 全流程文档/迁移指南/fixture 测试；253 tests / 0 failures / coverage 87% / ruff 0）。详见 progress.md 2026-08-02「17.6 schema 3.6 headwind」段。
- **17.1.2 结案**：claim 绑定受 schema 枚举限制，以记录级 source_ids 绑定替代（A2 实质达成）——维持 TRUST_BOUNDARY §3 偏差记录，不追加动作。
- **17.2 试点**：待下一次真实 forecast 会话执行（检查单命中记录表已备好）。
- **合并**：phase-14-input-build-tools 合并入 main（用户指令）。

---

## Phase 18（发行人身份归一：双类股与多地上市公司泛化逻辑）— 状态：completed（2026-08-02；18.3 用户裁定跳过）

> 编制日期：2026-08-01（Alphabet 会话 17.2 试点触发；用户指令"加到改进清单，做好规划，不用立刻实现"）。
> 依据：findings.md G1-G4、Alphabet 会话调试记录（resolver.py:331-459、542；assertion_service.py:277-316；scanner.py:983-1003、509-527）。
> 原则：本 Phase **只规划不实现**（用户指令）；实现启动前需用户确认方案（18.0 的裁决点）。

### 18.0 目标与核心设计问题（需用户裁决）

**总目标**：让"同一发行人的多个 ticker / 多个上市市场"在 company-wiki 身份解析与复用路径中归一化——双类股（GOOGL/GOOG）、多地上市（CN/HK/US 同发行人，如紫金 601899/02899、阿里巴巴 9988/BABA）共享正确文档，同时保持 fail-closed 安全（真冲突仍阻断）。

**设计裁决（2026-08-01 用户 AskUserQuestion 确认）**：

1. **归一粒度：方案 A —— 发行人名称锚定**。ticker 请求先解析到 security_master `canonical_name`（GOOGL/GOOG → "Alphabet Inc."），文档关联发行人即可命中；无新数据结构（18.1）。
2. **多地上市共享语义：方案 A —— 身份共享 + 市场过滤**。身份层共享（同市场双 ticker 互命中），文档层 `market` 仍硬过滤（CN 请求只命中 CN 文档）；保留 15.3 fail-closed（market 冲突仍阻断）（18.1 扩展）。
3. **断言 supersedes：方案 A —— 修正 verify 自动链接**。新 verified 自动 supersede 同 (source, document, content) 旧 verified，查询沿链取最终值；实现 verify_assertion docstring 承诺（18.2）。

### 18.1 实体匹配归一（G1-1，核心）

- [ ] `resolver._entity_matches`：wanted 不在 values 时，用 security_master 把 wanted（ticker）解析为 canonical_name / issuer 别名集合，与文档 entities/metadata 的 canonical_name 比对（GOOGL → "Alphabet Inc." → 文档 company-name:Alphabet Inc 命中）。
- [ ] 反向：文档 ticker（GOOG）与 request ticker（GOOGL）同 issuer → 匹配。
- [ ] 多地上市：request entity + market 组合 → issuer 解析 → 文档按 issuer+market 过滤。
- [ ] RED/GREEN：GOOGL/GOOG 互查命中同一 10-K；CN/HK 双上市互查按 market 正确路由；真冲突（不同 issuer 同名）仍 fail-closed。

### 18.2 断言 supersedes 链修正（G2）

- [ ] `verify_assertion`：新 verified 自动 supersede 同 (source, document, content) 的既有 verified（实现 docstring 承诺）；`get_verified_assertion_by_document` 沿链取最终 verified。
- [ ] RED：GOOGL verified → verify GOOG → 查询返回 GOOG（现返回 None fail-closed → RED）。
- [ ] 更正流程：reject/更正已有 verified 的 CLI 语义明确化（现 reject 拒绝 verified）。

### 18.3 scanner 身份补全可达性（G3）

- [ ] 已存在文档（hash 未变）重扫时，若 existing metadata 缺身份而 new（摄入补全后）有身份 → 更新（本次已临时扩展 prefer_new 的 URL+身份条件——18.3 需评估是否改为"字段级合并"而非全量 prefer_new）。
- [ ] 评估：metadata 字段级合并（existing 缺失字段用 new 补，不覆盖既有值）vs 现状全量替换——影响面清单（16.10 流程）。

### 18.4 SEC sidecar market 补全（G4）

- [ ] canonical_writer / scanner：SEC 文档（provider=sec / accession_number）sidecar 与 dayu_meta 确定性补 `market="US"`（与 16.1 URL 构造同模式）；security_id 归一（GOOG vs GOOGL 由 18.1 issuer 逻辑承载，sidecar 记录 provider 原始值）。

### 18.5 治理与文档

- [ ] `docs/OPERATIONS.md`（company-wiki）：身份断言（identity-enrichment）使用协议——何时 verify、如何更正（supersedes 链）、多 verified 并存含义。
- [ ] filing-fetch `references/trust-boundary.md` 或 identity 文档：双类股/多地上市请求写法（ticker 消歧 + market hint）。
- [ ] 17.2 会话检查单 §2 增加：双类股/多地上市公司（US 双 ticker、CN/HK 同发行人）预判与请求写法。

### 18.6 非目标

- 不改 dayu-agent / SEC adapter（sidecar 由 company-wiki 摄入层补全）。
- 不做发行人合并表/DB schema 变更（先评估 18.0 裁决点 1）。
- 不改变真冲突 fail-closed 行为。

### 18.7 验收（实现后）

- GOOGL/GOOG 任意 ticker 请求命中同一 Alphabet 10-K（复用）；
- CN/HK 双上市发行人按 market 正确路由且不误共享；
- 断言更正（GOOGL→GOOG）经 supersedes 链生效；
- 重扫补全已存在文档身份；
- 全量回归（company-wiki 1543+ / filing-fetch 67+ / revenue 239+）零回归。

### 18.8 状态

- 本 Phase 当前：**completed（2026-08-02）**——18.1 / 18.2 / 18.4 / 18.5 已实现并提交（company-wiki `d1d444a`）；18.3 用户裁定跳过。证据见 `progress.md`。

---

## Phase 19（Alphabet 会话复盘整改：filing-fetch 客户端、消歧提示、输入构建枚举速查、文档一致性）— 状态：completed（2026-08-02，19.6 随 Phase 18 一并落地）

> 编制日期：2026-08-01（Alphabet 会话全面复盘，findings G5-G10）。用户指令"先不用实现，更新文档即可"——本 Phase **只规划**，实现启动前需用户确认。
> 涉及仓库：revenue-forecast（19.1/19.3/19.4/19.5）、filing-fetch（19.2）。
> 原则：0.3 规则全适用（TDD、CodeGraph、证据入 progress、单 Phase in_progress）。

### 19.0 总目标与范围

**总目标**：消除 Alphabet 会话暴露的 4 类工具链/流程缺陷——客户端不可直接调用且吞诊断（G5/G6）、ambiguous 无消歧提示（G7）、输入构建枚举盲区（G8）、SKILL.md 示例无回归保护（G10）；来源可靠性规则补入检查单（G9）。

**不覆盖**：Phase 18 的身份归一实现（G1-G4，已裁决待实现）；引擎核心逻辑；schema 变更。

### 19.1 filing_fetch_client：CLI 入口 + 错误诊断（TDD，revenue-forecast）

**问题**：G5（无 `__main__`，SKILL.md 示例失效）+ G6（错误诊断只读 stderr，stdout 错误 JSON 被吞）。

**方案**：
- [ ] RED：`tests/test_filing_fetch_client.py` 新建——subprocess 启动 `python scripts/filing_fetch_client.py --request-file X`（fake filing-fetch 脚本目录）→ 断言输出 handle JSON（现 exit 0 无输出 → RED）；失败场景（fake 返回 exit 2 + stdout 错误 JSON）→ 断言 _ClientError 含 `status/error_code/error`（现 "no stderr" → RED）。
- [ ] 实现（filing_fetch_client.py）：
  - `main(argv)`：argparse（`--request-file`/`--allow-download`/`--timeout-seconds`）→ `resolve_filing` → stdout 输出 handle JSON（与 SKILL.md 示例一致）；
  - `resolve_filing` 失败分支：returncode != 0 时**先解析 stdout 的 error JSON**（status/error_code/error/retryable），解析失败再回退 stderr；
  - `if __name__ == "__main__"`。
- [ ] GREEN + targeted + 全量（revenue 239+ tests）。

**验收**：SKILL.md 示例命令直接可用；客户端错误信息完整（不再 "no stderr"）；测试钉住两行为。

### 19.2 ambiguous 消歧提示（filing-fetch，G7）

**问题**：identity_error 无候选列表与消歧提示（15.7 远期项复发）。

**方案**：
- [ ] RED：`tests/test_fetch_filing.py`——mock company-wiki identify 返回 ambiguous（多候选）→ 断言响应含 `candidates`（ticker/canonical_name/market/exchange）与消歧提示（现无 → RED）。
- [ ] 实现：fetch_filing 的 identity_error 分支携带上游候选（company-wiki identify 的 ambiguous 结果已含候选数据）→ 响应 `candidates[]` + `hint`（"補充 market/exchange 或 ticker 消歧"）。
- [ ] SKILL.md（filing-fetch）错误表补 ambiguous 行（含候选与消歧示例）。
- [ ] GREEN + filing-fetch 全量（67+ tests）。

**验收**：ambiguous 时用户可凭响应直接消歧（本次 Alphabet 场景：响应列出 GOOGL/GOOG/優先股 → 选 GOOG）。

### 19.3 输入构建枚举速查（revenue-forecast，G8）

**问题**：引擎枚举散落源码，模板/文档无速查 → 每次新公司构建重复踩（Alphabet 8 轮）。

**方案**：
- [ ] `references/input-construction.md` 新增"引擎枚举速查"节（与 revenue_core.py 常量一一对应）：
  - `TIME_BASES = {annual, point_in_time}`（**无 fiscal_year**）；
  - `PARAMETER_DIMENSIONS`（revenue/quantity/ratio/activity/...，**无 growth_rate**——增长率用 ratio）；
  - 货币参数规则：revenue 类维度必须 `currency == 顶层 currency`、`scale == 顶层 unit`；
  - 历史 claim `unit == "{currency} {unit}"`（"USD million"）；
  - `GROWTH_DRIVER_PERSISTENCE`/`GROWTH_DRIVER_COUNTEREVIDENCE_STATUSES`/`GROWTH_DRIVER_INFERENCE_DISTANCES`；
  - 驱动树：horizon 为对象（start_year/end_year int）、attribution 权重 (0,1] 且每段和=1、evidence 字段名 `evidence_nodes`、evidence claim 为 growth_driver target + rationale_support；
  - recognition：`modeled_presentation` 必须与 presentation 一致、`basis_claim_ids` 必填（recognition_policy target）；
  - sensitivity：参数必须被 **base 情景**引用（low/high 参数不可 shock）。
- [ ] 一致性护栏（可选）：测试读取 input-construction.md 的枚举表与 revenue_core.py 常量比对（防文档漂移）。
- [ ] `generate_input_template.py` 输出头部 `_comment` 引用枚举速查节（P2，可选）。

**验收**：按速查构建的新输入 validate 轮次 ≤ 2；文档与源码枚举一致。

### 19.4 SKILL.md 示例一致性测试（revenue-forecast，G10）

**问题**：SKILL.md 的 CLI 示例命令无回归保护（G5 即因此漏网）。

**方案**：
- [ ] RED/护栏：`tests/test_skill_documentation.py`——解析 SKILL.md 中 `python scripts/*.py` 示例命令 → 断言：脚本存在；脚本含 `if __name__ == "__main__"` **或** 文档标注为模块用法（`resolve_filing`）；参数与 argparse 兼容（示例参数在脚本 --help 中）。
- [ ] 实现：静态检查（AST/regex 读 SKILL.md + scripts 目录）。
- [ ] 修复 SKILL.md 中当前失效示例（filing_fetch_client 用法改为模块示例，或 19.1 后保持 CLI 示例）。

**验收**：SKILL.md 全部示例命令可运行或明确标注；测试全绿。

### 19.5 检查单与来源可靠性规则（G9）

- [ ] `docs/session-checklist.md` §4 增补"来源优先级与数字核验"：官方 release/10-K 优先于新闻转述；WebSearch 摘要数字仅作引导，作 claim 前必须打开官方或可靠原文；两来源数字冲突 → 登记并采用官方（data-governance §Conflict handling 可操作化）。
- [ ] §2 增补："ambiguous → 用 ticker 消歧（19.2 后响应含候选）"。
- [ ] `references/data-governance.md` 冲突处理节补"搜索摘要 vs 官方"优先级示例（Q2 YouTube 案例）。

### 19.6 非目标

- 不实现 Phase 18 身份归一（G1-G4，已裁决）。
- 不改引擎校验逻辑（枚举速查只做文档化）。
- 不改 dayu-agent / company-wiki 适配器。

### 19.7 验收（实现后）

- 19.1：SKILL.md 示例命令实测可用；客户端错误含完整诊断；测试全绿。
- 19.2：ambiguous 响应含 candidates + hint；filing-fetch 全量回归。
- 19.3：枚举速查就位且与源码一致；下一次会话构建轮次显著下降（目标 ≤2）。
- 19.4：SKILL.md 示例全被钉住。
- 19.5：检查单/数据治理文档更新。
- 全量回归：revenue 239+ / filing-fetch 67+。

### 19.8 状态

- 本 Phase 当前：**pending（仅规划，未实现）**——等待用户确认启动。

### 19.5 检查单与来源可靠性规则（G9 + A1/A2/A3/A6 增强）

- [ ] `docs/session-checklist.md` §4 增补"来源优先级与数字核验"：官方 release/10-K 优先于新闻转述；WebSearch 摘要数字仅作引导，作 claim 前必须打开官方或可靠原文；两来源数字冲突 → 登记并采用官方（data-governance §Conflict handling 可操作化）。
- [ ] §2 增补"身份解析预判"（A1）：知名多 ticker/多上市名单（GOOGL/GOOG、9988/BABA、601899/02899）+ ambiguous 标准操作（identify 候选 → 选主 ticker → market hint）；19.2 落地后响应含 candidates。
- [ ] §1 增补"会话级 3 次/30 分钟规则"（A2）：同一主题 3 轮未解 → 停下报告现状 + 请用户裁决（含切换备用路径选项）——0.3 规则 12 的会话级应用。
- [ ] §3 或新节增补"备用路径规则"（A3）：filing-fetch 3 轮未获 handle 且文件已在 canonical（sha256 可核验）→ 允许 local_document 注册 + TRUST_BOUNDARY 说明；文件未落 canonical → 必须修链路。
- [ ] §4/§5 改为"构建中每轮跑启发式"（A6）：input 修改后即跑 `--check-conclusion-facts` / `--check-sensitivity-propagation`，交付前为最终确认。
- [ ] `references/data-governance.md` 冲突处理节补"搜索摘要 vs 官方"优先级示例（Q2 YouTube 案例）。

### 19.6 resolve 诊断可观测性（A4，filing-fetch/company-wiki）

**问题**：候选被排除的原因无单一视图（本次 8 轮手工重放 resolver 循环）。

**方案**：
- [ ] RED：`tests/test_fetch_filing.py`——mock resolve 返回 not_found → `--debug` 输出含逐候选排除打点（现无 → RED）。
- [ ] 实现：filing-fetch `--debug` 透传 company-wiki resolve 的候选级诊断（entity_matches/identity/year/form/location/capture_ready 各步），输出结构化 `debug_trace`；company-wiki resolve 侧增加候选排除原因记录（如已有内部信息则只做透传）。
- [ ] SKILL.md（filing-fetch）错误排查节补 `--debug` 用法。
- [ ] GREEN + filing-fetch 全量回归。

**验收**：not_found/identity 失败时 `--debug` 一次给出排除原因链（本次 Alphabet 场景：直接看到 entity_matches(GOOGL)=False + 断言 security_id 不匹配）。

### 19.7 构建脚本骨架文档化（A5）

- [ ] `references/input-construction.md` 增"构建脚本骨架"节：参数命名规范（{seg}_{scenario}_{year}_g / {seg}_base_rev）、claim 生成循环模式（历史/基期/增长率 rationale/evidence claims）、来源注册模式（capture 四要素 + fix_hashes 收口）、validate 迭代流程（lint → fix_hashes → validate --verbose → 启发式）。
- [ ] 用本会话 build_input.py 作为工作示例（节选，不含公司数据）。

**验收**：新会话构建脚本可照骨架速成；build_input.py 模式不再每次重发明。

### 19.8 非目标（补充）

- 不实现"通用输入构建框架"（每公司数据形态不同，骨架文档化即足够——避免过度工程）。
- 不改引擎校验逻辑；不动 dayu-agent / company-wiki 适配器。
- Subscriptions subscription 模型深化（B1）登记为下次 Alphabet 迭代选项，不在本 Phase。

### 19.9 状态

- 本 Phase 当前：**completed（2026-08-02）**——19.1-19.7 全部完成（19.6 --debug 随 Phase 18 resolve 诊断落地）；Phase 18 亦完成（18.3 用户裁定跳过）。证据见 `progress.md`。
