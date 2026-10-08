# R6-RF-INPUT 本线发现（持续更新）

## 结构核实（开工时）

- 实际入口与卡一致：`scripts/research/targets.py`（目标 ledger 校验+分析）、`scripts/contracts/evidence.py`（哈希/capture 合同）、`scripts/analysis/sensitivity.py`（shock 算术）、`scripts/company_wiki_narrative_reader.py` + `company_wiki_narrative_contracts.py`（NarrativeRef 有界读）、`scripts/narrative_source_preparation.py`（CLI）。不存在 scripts/management_targets.py。
- 证据角色/inference_distance 已有骨架：`evidence_nodes[].inference_distance` 四值、`evidence_status = triangulated | limited`（仅按支持节点的类型数≥2 且源数≥2），无角色概念、无 peer 语义、无同摘录支持/反证冲突检查——I3 的机制缺口被证实。
- sensitivity 四类 shock 的单位语义只在 `references/input-schema.md` §9 有文字，无机器可查的转换记录字段；`percentage_point` 的 `shock_value=5.0` 语义（±500pp）与请求值/钳制在输出中可见，但构建侧无任何防错——I1 的机制缺口被证实。
- 目标 ledger 只有 numeric 年度语义（`raw_target_value` 必填、measurement basis 四值）；季度/定性/区间/未定年无法进合同，`ambiguous` 是唯一兜底——I2 被证实。
- 测试基建重要事实：`tests/test_data_contract.py::finalize_contract` 会**整体重建** `evidence_claims` 和 `growth_driver_tree`——在其后再附加 claim/树会被清掉；所有附加型测试必须在已 finalize 的文档上直接 append（本线三个测试文件均如此处理）。
- `forecast_document()`（test_recognition_bridge）产出已 finalize 的合法文档，`as_of_date=2026-07-12`；新增 narrative 源的 published/captured 日期必须 ≤ 该日。
- growth-driver 参数映射规则：driver `parameter_ids` 中每个参数必须属于**被归因 segment** 的 base 路径（`_validate_growth_driver_parameters`）；测试树归因两个 segment 时参数必须覆盖两者。
- 引擎侧 claim 目标：evidence node 的 claim `target_id` 必须是**节点 evidence_id**（`growth_driver:node_x`），不是 driver_id——RED 期两次踩中。

## RED 证据（commit 前基线 72ce94c1）

- 52 failed / 1 passed（三文件合计）：
  - `ModuleNotFoundError: research.input_quantities / input_targets / input_evidence`（缺 API 的 RED）；
  - 真语义 RED：peer 两源两类型仍 `triangulated`（HK v3 复现）、同摘录支持+反证不被拒、`5.0` 伪 pp 输入在 requested 值中不可见地通过算术。
- 修正测试自身构造后 RED 稳定为 17+13+22 个断言级失败。

## GREEN 与实现要点

- I1 `research/input_quantities.py`：单位族（share/money_usd/money_rmb/count）+ 别名表；跨族/跨币种拒；`ratio=5.0` 恒等保留（identity 表达式）；`build_sensitivity_test` 按 (unit, shock_semantics) 选 shock_type，错配即拒。引擎 `calculate_sensitivities` 对存在的 `input_quantity` 记录做两重机器校验：`engine_value == shock_value`（防记录与实际冲击脱钩）+ `validate_input_quantity_record` 重推导（防伪造换算）；记录透传进输出 sensitivities。
- I2 `research/input_targets.py` + 合同扩展：`quarterly_period` 第五基准（须 `target_quarter`；无转换不得声明年度 measurement_periods）；`raw_value_kind ∈ numeric|numeric_range|qualitative_range`；`currency_basis/presentation_basis` 枚举；`unmodeled_reason` 必填条件（qualitative/range/quarterly/ambiguous 且 unmodeled）；季度转换复用 run-rate 的 `comparison_basis+formula+parameter_ids` 机制（公式须引用 x0..xn 且逐输入有 checked 证据，引擎重算到 comparison_value）；`capacity_plan/aspiration` 不得进 `modeled_scenario/scenario_boundary`（builder 与引擎双重）；material in-horizon 门对无单点可比值的新形态不强制进情景。旧输入零影响（全部新键可选，缺省走原逻辑）。
- I3 `research/input_evidence.py` + 引擎：claim 可选 `evidence_role` 八值；方向角色不得带 `extracted_value`、`value_range` 必须是 exact_value 且带值、`recognition_policy` 必须 policy_support（进参数即自拒）、`counterevidence` 不得做参数支持；参数级"仅 history_base 不得支持假设"；`bind_parameter_evidence` 本地同规则 fail-fast + capture receipt 重算防绑定未验源。
- I3 引擎 triangulation：peer-based 节点（其 claim 带 `evidence_role=peer_analogy`）从 evidence_types/sources 统计中剔除，仅披露 limitation（"peer-analogy evidence is disclosed but excluded from triangulation" / peer-only 更强提示）；同 `excerpt_sha256` 同时出现在 contrary 与非 contrary 节点即拒（按摘录哈希判，同一文字复制成两个 claim 也拦得住）。
- I4 `narrative_span_binding`（input_evidence 内）：span 按 wire 合同重验（output_sha256/span_id 绑定重算→`span_text_hash_mismatch`/`span_identity_mismatch`），manifest↔source_ref content_sha256 一致，`published_date` 缺失→具名 `narrative_source_publication_unknown`；从 manifest/read_receipt 派生正式 revenue source（capture 含 host_receipt，receipt 重算）与 claim（locator=span locator、excerpt=raw_text、content_sha=content_sha256）；产出 parameter.claim_ids 依赖——只把 claim 放进文档而不进参数依赖会被引擎 `claim source ... is not registered on parameter` 拒绝（"文件存在≠消费"的机器面）。

## E2E（tests/test_input_semantics_e2e.py）

- 独立 tmp 根，真实子进程链：lint（exit 0 无 findings）→ fix_hashes --check（无漂移）→ revenue_forecast --output --markdown（formal，注册到测试根 publications.jsonl）→ revenue_backtest create → publication_registry lookup/audit。8 passed。
- 两变体（离线，无网络无模型）：
  - peer 变体：收入逐分位不变，`evidence_status triangulated→limited`，confidence limitations 出现 peer 剔除提示；
  - 支持源变体（换 NarrativeRef span 文字）：`input_sha256` 变、claim `excerpt_sha256` 变、registry 出现新 anchor，收入不变。
- unknown published_date 变体：具名拒绝，不产生输入。

## 边界遵守记录

- 未改：assurance/runs、output、config 生产配置、compatibility/current.json、CI 工作流、旧快照、tests/fixtures 金字（golden 行为锁 1 passed 未动）。
- 未用模型/网络（model_calls=0）；测试全部离线（narrative E2E 用本地重签 fixture，未跑需 CWP producer 的 test_narrative_source_preparation_e2e.py，属 MAIN 集成范围）。


## 全量回归归因（2026-10-08 收尾）

- 全量（排除 5 个稀疏环境受限文件 + live narrative E2E）：HEAD `99 failed / 1387 passed / 4 errors`。
- 严格对照：将 HEAD 失败的 31 个文件在基线 `72ce94c1`（临时稀疏 worktree，同 ignore 集）复跑 → `100 failed`，**HEAD-only 差集为空**（comm -23 无输出）：99 个失败全部预存，均为工程治理/环境类（`uc` 模块与 assurance/audit_review 树不在稀疏检出；compatibility 子进程 WinError 267 路径问题；registry/CI 门类测试依赖完整仓形态）。
- 结论：本线引入零个新失败；本线新增 4 测试文件 61 测试全绿；golden 锁未动。基线在同文件集多出的 1 个失败与 4 errors 为 flaky/环境差异，方向为基线更差，与本线无关。
- 基线 worktree 已删除（git worktree remove）。
