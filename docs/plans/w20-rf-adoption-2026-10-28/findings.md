# 调查发现

ROOT准备事实（2026-10-28）：新独立工区`C:\Users\郑曾波\Projects\revenue-forecast-w20-adoption`，基线`0991e25d5dca667a3fdafb7bc5ebf0e546a2272b`，分支`codex/w20-rf-adoption-20261028`。主仓tracked WIP未变；原件/模型未复制、无下载或收费。所有任务具体要求、allowlist、接口与独立审查要求见construction_card.md。

## A 调查结论（2026-10-28，作者完成；四路只读调查，关键结论附代码位置）

### A1 已有覆盖 vs 缺口（逐项）

| 本卡需求 | 现状 | 判定 |
|---|---|---|
| 来源信息→最终预测节点引用映射工具 | `tools/`无任何adoption观察工具（grep "adoption"仅命中`adoption_rate`驱动名）。最接近三件：(1) `tools/run_narrative_consumption_e2e.py:18-38`止步linked-input+consumption回执，不跑预测、不观察最终产物；(2) `scripts/research_support_diagnostics.py`（`economic-support-diagnostics/1`）是**输入侧**operating_research校准覆盖观察，明确声明"Input cells are not final output cells"；(3) `e2e/run_revenue_forecast_e2e.py`确定性CLI+golden但无narrative维度 | **缺工具**，按allowlist新建`tools/narrative_adoption_audit/`（单一owner） |
| RF最终产物引用链可观察点 | 输出JSON携带完整链：顶层`parameter_trace[]`(每参数`claim_ids`/`source_ids`)、`evidence_claims[]`、`sources[]`；投影节点引用字段：`segments[].base_revenue_parameter_id`、`segments[].scenarios[s].driver_parameter_ids{driver:[每年一param]}`、`segments[].recognition`(basis_claim_ids/progress_parameter_ids/carry_in_parameter_ids/派生basis_source_ids)、`growth_driver_analysis.drivers[].parameter_ids`与`evidence_nodes[].claim_ids/source_ids`、`research_coverage.dimensions[].parameter_ids/source_ids`、`management_target_coverage.{communications,targets}[].source_ids/claim_ids/mapped_parameter_ids`、`consolidated_forecast[s].adjustment_bridge[].parameter_ids`、`probability_weighted_forecast.probability_source_ids`（revenue_core.py:102-107; segments.py:213,239-241; drivers.py:558-584; targets.py:682-744） | 已有合同，直接消费 |
| 关键语义边界：input echo≠采用 | formal输出整体内嵌`input_document`且`parameter_trace`逐字等于输入parameters（revenue_report.py:456-459）——**若把parameter_trace当采用证据，则一切输入claim自动"采用"**，正是卡R3禁止的谬误。采用观察必须以**投影分析节点**的引用为准（scenario driver槽位/驱动树evidence节点/coverage/target/adjustment/probability/recognition），不以input_document/parameter_trace回显为准 | 观察规则冻结（见A2） |
| 叙述侧canonical ID | span/source为哈希派生urn：`urn:company-wiki:evidence-span:sha256:...`、`urn:company-wiki:source:sha256:...`；连接键=`span_id`(urn)、`source_sha256`==输入`capture.snapshot_sha256`（source_narrative_context.py:48-59 `_captured_parent`先例）。`claim_id`（输入侧与bundle summary侧）均只是**文档内display key**（document.py:626仅查文档内唯一；contracts 403行仅查非空） | 连接键冻结：urn/sha；claim文本仅单文档内解析，绝不跨文档拼接 |
| support/context_only/unresolved | reading /4（冻结基线0991e25d刚加入）：citation_views带`reading_support_use∈{support,context_only,unresolved}`+`reading_support_reason`（company_wiki_narrative_contracts.py:911-919）；/2为结构分区support_evidence_ids/context_evidence_ids恰好划分（contracts:920-926）；/1无citation_views。`narrative_citation_context.py`纯函数（no IO/clock/network）可整体复用：`reading_trace`/`resolve_span`/`trace_status`/`citation_trace`；context分区span被`narrative_citation_context_only`命名拒绝（:426-428） | 复用现有语义，不重造 |
| consumption回执（span→claim→param绑定） | `consume_narrative_input`(source_narrative_context.py:103-164)产出`revenue-narrative-consumption/1|3`：`{status: consumed|not_consumed, dependencies[]{span_id,locator,parser_name,parser_version,source_id,claim_id,parameter_id,formula_refs}, citation_trace}`；binding只允许`{span_id,claim_id,parameter_id,support_type}`+可选`{citation_group_id,citation_view}`；narrative定性claim只允许`rationale_support`；参数必须到达公式（`parameter_formula_refs`非空才绑） | 回执=采用侧事实来源 |
| 错版本/错hash/材料缺失诊断 | 现有命名错误码可定位：`NarrativeTransportError(status,reason)`（invalid wire→blocked/invalid_narrative_wire）；span身份`span_identity_mismatch`；缺hash宽松先例：`company_wiki_source.py:313`声明sha为空仍verified；prompt_review缺省`not_reviewed` | 沿用宽松政策：hash提供则必验、缺失记unknown不加门禁 |
| 确定性E2E部件 | 全部现成：合成wire builder `tests/test_du11_narrative_citation_wire.py::{draft,wire,resign,validated,span_id}`（产出过真实`validate_narrative_response`的request/body/receipt三件套）；reader子进程stub协议=stdout bundle、stderr receipt（test_du11_narrative_citation_e2e.py:65-74）；完整输入fixture `tests/fixtures/scoped_calibration_support/valid_calibrated.json`（direct_revenue，含claims/coverage/目标）与 `e2e/fixtures/biren_input.json`（direct_growth）；"consume前后数值不变+产物携带claim"断言先例（test_du11_narrative_citation_consumption.py:141-150）；CLI子进程先例（test_du11_narrative_citation_e2e.py:214-225）；owned-tree sentinel/恢复惯例（同文件:83-151） | 直接复用 |
| 公式可达性（"进入计算图"） | `scripts/forecast/dependencies.py::parameter_formula_refs(data,parameter_id,parameters)`纯函数返回`{segment,scenario,model,driver,output}`；逐参数调用是O(P×E)，大样本n/2n线性测试不可接受 | 自建一次性upstream闭包（worklist，O(P+E)），单测与`parameter_formula_refs`做差分一致性验证 |
| W16-BASIS交接 | 主仓`delivery/w16/handoff.{md,json}`：revenue_basis共享owner；root_acceptance留"验收语义采用"待办；ROOT账本`current_rf_adoption:"OPEN"`（company-wiki-w19-sina-statements CURRENT_STATUS.json:1889） | 本卡即其离线观察件 |

### A2 冻结设计（B实施依据）

**工具**：`tools/narrative_adoption_audit/`（`audit.py`纯核心 + `cli.py` + `README.md`）。无新DB/调度/权限；不改任何既有文件。

**CLI**：
```
python tools/narrative_adoption_audit/cli.py --forecast F.json \
  [--input I.json] [--snapshot S.json] \
  [--consumption C.json ...] \
  [--narrative request.json bundle.json[.gz] receipt.json[.l] ...] \
  [--output R.json] [--max-items N] [--max-input-bytes N] [--pretty]
```
默认报告JSON打stdout；`--output`只写**新**文件，已存在即拒绝（exit 2）；绝不写任何输入路径；无时钟、可重复执行字节稳定；exit 0=报告产出（含诊断也可），exit 2=用法/IO/JSON/资源界错误。不扫目录、不联网、不开DB、不跑模型。

**报告schema** `rf-narrative-adoption-report/1`（diagnostic_only_not_a_permission_gate=true；observation_scope=final_output_citation_chain_no_execution_trace）：`forecast`(result_sha256/input_sha256等)、`cross_checks`(input/snapshot/consumption绑定)、`node_index`计数、`items[]`、`counts`、`diagnostics[]`、`limitations[]`、`resource`。

**item**：`{kind: source|claim|span|summary_claim, id, id_scope: canonical|document_local_display_key, source_sha256?, input_source_id?, status, support_use?, cited_by[{node_type,location,ids}], reasons[]}`。

**状态机（观察≠裁决）**：
- `used`：canonical链在≥1个**投影节点**引用可观察（driver槽位/base_revenue/recognition/驱动树evidence节点/coverage dimension/target/communication/adjustment/probability；derived参数经`used_via_derived_parameter`）。
- `not_used_when_provable`：结构性可证不进计算图——claim仅挂在不进任何公式闭包的参数（`parameter_not_wired_to_any_node`）；context_only/unresolved分区span按契约不可为支撑（`context_partition_cannot_support`/`unresolved_support_cannot_support`）。
- `not_observed`：材料在（span运输了/summary可读/源登记了）但无绑定或无投影引用（`span_not_bound_in_consumption`/`summary_claim_spans_not_bound`/`source_without_observed_citation`）——**不**断言模型没用。
- `unverifiable`：绑定材料缺/错——receipt引用的claim/param不在本输入（`receipt_claim_not_in_input`/`receipt_parameter_not_in_input`）、source_sha256错配（`consumption_source_hash_mismatch`）、receipt formula_refs与输入实际公式不符（`receipt_run_mismatch`）、narrative wire拒绝（`narrative_wire_refused`）。缺hash→`hash_missing_unknown`宽松继续。

**named reason/diagnostic codes**：上述+`period_mismatch_at_node`（参数period年vs槽位年）、`unknown_segment_attribution`、`duplicate_capture_sha`（多版本同源）、`target_currency_mismatch`、`extracted_unit_mismatch`、`display_key_collision_not_joined`、`context_span_bound_as_support`（异常回执）、`node_family_missing:<name>`（旧格式info）、`old_reading_schema_no_support_partition`（/1 info）、`unknown_fields_ignored`。口径检查仅观察已有绑定，不另算收入、不LLM判因果、不产出任何rating。

**资源界**：`--max-items`默认20000、`--max-input-bytes`默认64MiB，超界exit 2命名错误；索引一次构建（dict），每item O(1)查，总体线性；不逐span重扫报告。

**测试包**（`tests/test_w20_narrative_adoption_audit.py`单元 + `tests/test_w20_narrative_adoption_e2e.py`真实CLI，先RED后实现）：
1 同源正确采用；2 同display t1跨source不假采用；3 context-only不当数字证据；4 summary可读无trace→not_observed；5 跨年度/币种/分部混用诊断；6 同证据多节点不重复计多源；7 旧格式（reading/1、draft无driver树、consumption/1无citation_trace）兼容；8 hash错配与无hash宽松；9 未知字段不造结论；10 n/2n线性与资源界；11 输入与既有输出不被覆盖。
E2E：direct_revenue（valid_calibrated+consume真实适配器[stub传输]+revenue_forecast.py CLI+audit CLI）与direct_growth（biren fixture）两类驱动模型；snapshot交叉核对；重复执行字节稳定；owned-tree sentinel/恢复。

**基线绿色证据**：`python -B -m pytest -q tests/test_recognition_bridge.py tests/test_du11_narrative_citation_context.py tests/test_du11_narrative_citation_consumption.py tests/test_research_support_diagnostics.py`（A节实测记录于progress.md）。
