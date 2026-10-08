# R6-RF-INPUT 本线计划（单位、管理目标、证据角色与真实输入依赖）

工作树 `C:/Users/郑曾波/Projects/_harness_worktrees/cmrf-20261008/rf-inputs`，分支
`codex/cmrf-input-semantics-20261008`，基线 `72ce94c160bbb5b9399c8716307588b443a72a83`。
施工卡：company-wiki `docs/plans/cross-market-rf-e2e-2026-10-08/harness_lanes/rf_input_semantics.md`。
根级 `task_plan.md`/`findings.md`/`progress.md` 是仓库历史归档，本线不写；本线 PWF 全部在本目录。

## 责任机制六字段表（原 issue → 共用机制）

| # | 原症状/证据（实测） | 最小复现（RED） | 已证实根因（未证实假设单独标注） | 责任层与共用改动 | 原测试为何漏报 |
|---|---|---|---|---|---|
| I1 | US 敏感性把 5pp 构造成 `shock_value=5.0`（ratio），算术全绿、clamp 掩盖意图 | `convert_input_quantity(5, input_unit="pp", engine_unit="ratio")` 应 0.05；经正式 `calculate_sensitivities` 复核 requested 0.33/0.43（v=0.38） | 输入构建层没有显式人类单位转换；schema 只列 shock 类型无单位语义约束，写错单位后算术自洽（已证实）。[假设] 无机器可判"意图"，故只建显式转换，不做 ratio>1 通杀 | 新 `scripts/research/input_quantities.py`：`convert_input_quantity` + `build_sensitivity_test`；参数可选 `input_quantity` 溯源字段（validator/lint 同步重算） | 旧测试只测 engine 对给定数值的算术，不测"人类单位→契约单位"的构建半段 |
| I2 | 季度 CC 指引、mid-single/high-teens 定性区间、未定年达产目标无法进 ledger；季×4、造中点、capacity plan 当 revenue promise 属伪年化 | `build_management_target`：定性标签逐字保留且无 comparison_value；季度目标无显式转换时不产生年度比较；显式转换（带证据参数公式）才可比 | ledger 合同只有 numeric 年度值（已证实）。[假设] 扩 `quarterly_period` 基准 + `raw_value_kind`（numeric/numeric_range/qualitative_range）+ `currency_basis`/`presentation_basis`/`target_quarter`/`unmodeled_reason` 可覆盖三市场形态，需泛化 run-rate 转换机制到 quarterly/CC | 新 `scripts/research/input_targets.py`：`build_management_target`；`contracts/constants.py` + `research/targets.py` + `revenue_report.py` 同步严格解析（旧输入缺省=原行为） | 旧目标测试只有 annual numeric 正例和 ambiguous 负例；定性/季度形态无法表达故从未进测试 |
| I3 | 合法 claim ID＋真实原文不支持未来增长范围：历史基数/会计政策被当机制支持；peer 竞争事实自动升 triangulated（HK v3） | `bind_parameter_evidence`：方向角色不得带 extracted_value；范围角色必须带；peer_analogy 节点不得计入 triangulated 阈值；同摘录不得同时支持与反证 | 证据绑定无角色/距离约束，`evidence_status` 只数类型数与源数（已证实）。[假设] 角色六枚举+机器可检身份/数值缺失+peer 剔除能挡住已见误用；经济含义最终仍靠 MAIN 大节点独立审查 | 新 `scripts/research/input_evidence.py`：`bind_parameter_evidence`；claim 可选 `evidence_role`（document.py 严格解析）；`research/drivers.py` evidence_status 只数非 peer 支持节点并加 limitation | 旧 growth-driver 测试断言 triangulated 的算术推导本身，没有"角色×距离"的负例 |
| I4 | NarrativeRef 文件存在 ≠ RF input 消费；引用只进附录不进参数/driver 依赖 | NarrativeRef span→claim→parameter/driver 依赖后：换 span 内容 → 输入 hash 与 evidence_status/limitation 实变；仅存文件不绑依赖 → 构建器拒绝/测试断言未消费 | 正式输入只认 sources+claims+parameter.claim_ids 依赖链，无 NarrativeRef→claim 公共适配（已证实） | `input_evidence.py` 内 `narrative_span_binding`：用已发布 wire 合同（`company_wiki_narrative_contracts`）校验 span→正式 source/capture/claim；published_date unknown 具名拒绝 | 旧 narrative 测试只测传输/回放合同，从未把 span 接进正式输入跑 engine |

共享不变量：旧输入（无新字段）行为逐字节不变（golden 锁）；stable-fsum 跨 seed 精确验证不触碰；
assurance/runs、output、生产配置、compatibility/current.json、CI 工作流零改动；不为旧错误输入加公司白名单。

## 步骤

1. [x] 核实工作树/基线；读必读文档与实现入口（CodeGraph 式结构核实，见 findings.md）。
2. [ ] RED：`tests/test_input_quantity_conversion.py`、`test_management_target_semantics.py`、`test_evidence_input_lineage.py`（函数缺失 RED + 真语义错误/正例 RED）。
3. [ ] GREEN-1 单位：`input_quantities.py` + 参数 `input_quantity` 字段进 `contracts/document.py`/`lint_input.py`；正式 sensitivity 路径验证。
4. [ ] GREEN-2 目标：`input_targets.py` + 合同扩展（constants/targets/report 同步）。
5. [ ] GREEN-3 证据：`input_evidence.py` + `evidence_role`/peer 剔除进 document/drivers。
6. [ ] E2E `tests/test_input_semantics_e2e.py`：独立测试根 构建→lint→fix_hashes→engine→report→snapshot→registry；支持源变体/peer 变体（收入不变，evidence_status/limitation 变）。
7. [ ] 集中回归：rg 选相关既有测试清单集中跑 + golden 锁不漂移。
8. [ ] 交付：本目录五文件（task_plan/findings/progress/HANDOFF/handoff.json），Git 分批提交。

## 边界（每步适用）

- 不改：assurance/runs、output、config 生产配置、compatibility/current.json、CI、旧快照、封存第一组产物、根级历史 PWF。
- 旧 golden 不重哈希；新增行为全部走新字段+缺省策略。
- 不重建研究数据库/许可/签收；不越收入研究边界；不下载、不付费模型调用（model_calls=0）。
