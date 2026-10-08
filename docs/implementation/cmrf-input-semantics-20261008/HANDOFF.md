# R6-RF-INPUT 交接（HANDOFF）

## 1. 修的共用机制、原实测问题与最小 RED

按 root_cause_remediation 责任组「P1 RF 输入单位与目标口径 + P1 RF 证据语义与实际消费」的共用层修复，非公司特判：

- **I1 单位**：US 实测把 5pp 构造成 `shock_value=5.0`（ratio）。最小 RED：`convert_input_quantity(5, pp→ratio)` 应 0.05；经正式 `calculate_sensitivities` 的 requested 值（0.8±0.05→0.75/0.85）与伪造 `input_quantity.engine_value=5.0` 被引擎拒绝。算术自洽的错输入不会被 clamp 或容差"修好"——修复在构建半段。
- **I2 目标口径**：季度 CC 指引/定性区间（mid-single、high-teens）/未定年达产无法入账，季×4、造中点、capacity plan 当 revenue promise 属伪年化。最小 RED：季度目标无转换不产生年度比较、`x0*4` 字面转换被拒、`capacity_plan/aspiration` 不得进 modeled/scenario_boundary、定性标签无 comparison_value。
- **I3 证据角色**：HK v3 同行"增长/竞争存在"事实自动升 triangulated；历史基数/会计政策被当未来机制支持。最小 RED：peer 两源两类型仍 limited+limitation、仅 history_base 拒、方向角色带数值拒、同摘录（按 excerpt_sha256）支持+反证拒。
- **I4 消费链**：NarrativeRef 文件存在≠RF input 消费。最小 RED：span 未进参数 claim_ids 时引擎以 `claim source ... is not registered on parameter` 拒绝；published_date unknown 具名拒绝；篡改 span 文字 `span_text_hash_mismatch`。

## 2. 公共接口（真实导入路径）

工作目录加入 `sys.path`（或以 `scripts/` 为根）后：

```python
from research.input_quantities import convert_input_quantity, build_sensitivity_test
record = convert_input_quantity(5, input_unit="pp", engine_unit="ratio")   # engine_value=0.05
test = build_sensitivity_test(parameter_id="util_2026", value=5,
                              input_unit="pp", shock_semantics="additive")  # percentage_point 0.05

from research.input_targets import build_management_target
built = build_management_target(statement, target_id=..., metric_name=...,
    source_id=..., locator=..., excerpt=..., verified_by=..., verified_date=...,
    raw_unit=..., raw_currency=..., raw_scale=..., period_label=...,
    measurement_basis="quarterly_period", target_quarter="Q2", raw_value=40.0,
    commitment_strength=..., rationale=..., measurement_rationale=...,
    perimeter_notes=..., source_capture=<capture dict>)
# -> {"target": ledger记录, "claims": [exact_value claim], "notes": {comparable, reason_code...}}

from research.input_evidence import bind_parameter_evidence
bound = bind_parameter_evidence(parameter, evidence_bindings=[
    {"role": "mechanism_direction", "source_id": "filing",
     "locator": "...", "excerpt": "..."},              # 经典摘录
    {"role": "mechanism_direction", "source_id": "narrative_transcript",
     "narrative_context": <validated NarrativeContext dict>, "span_id": "urn:..."},
], source=<source dict 或 None>, verified_by=..., verified_date=...)
# -> {"parameter"(含 claim_ids/source_ids), "claims", "sources"(narrative派生), "lineage"}
```

- 新合同字段（全部可选，旧输入缺省=原行为）：sensitivity test `input_quantity`（引擎重算两处并透传输出）；claim `evidence_role`（八值，见 `contracts/constants.py::GROWTH_DRIVER_EVIDENCE_ROLES`）；management target `raw_value_kind`/`raw_label`/`raw_target_value_low|high`/`target_quarter`/`currency_basis`/`presentation_basis`/`unmodeled_reason`，`measurement_basis` 新值 `quarterly_period`（转换复用 run-rate 的 normalization 公式机制）。
- 与卡的差异：无。`build_management_target` 的转换参数需带 `parameter_values`（与 `parameter_ids` 对齐）用于落盘 comparison_value；引擎独立用文档内参数值重算，不信任该列表。

## 3. Git

- 仓库/分支：`C:/Users/郑曾波/Projects/_harness_worktrees/cmrf-20261008/rf-inputs` @ `codex/cmrf-input-semantics-20261008`
- 基线：`72ce94c160bbb5b9399c8716307588b443a72a83`
- 提交：见 handoff.json `commits`（I1-I3 实现+单测+PWF 为第一笔；E2E+docs 交接为第二笔）。未提交文件：无（本线全部入库）。

## 4. 测试（命令、退出码、结果）

RED（在基线 `72ce94c1` 上、实现之前）：`python -X utf8 -m pytest tests/test_input_quantity_conversion.py tests/test_management_target_semantics.py tests/test_evidence_input_lineage.py -q` → exit 1，52 failed（缺三模块 API + 真语义反例：peer 自动 triangulated、同摘录混用不拒）。

GREEN（当前 HEAD）：

| 命令 | exit | 结果 | 耗时 |
|---|---|---|---|
| `python -X utf8 -m pytest tests/test_input_quantity_conversion.py -q` | 0 | 23 passed | ~0.7s |
| `python -X utf8 -m pytest tests/test_management_target_semantics.py -q` | 0 | 13 passed | ~0.8s |
| `python -X utf8 -m pytest tests/test_evidence_input_lineage.py -q` | 0 | 17 passed | ~0.5s |
| `python -X utf8 -m pytest tests/test_input_semantics_e2e.py -q` | 0 | 8 passed（3×真实子进程链 + registry） | ~3.4s |
| 相关既有套件（targets/independent/structure/growth-tree/data-contract/output-report/scenarios-confidence/lint/input-construction/migration/golden） | 0 | 196 passed | ~6.5s |

全量集中回归（一次性，非 commit 门）：`python -X utf8 -m pytest tests -q --ignore=<5 个稀疏环境受限文件>` → 1387 passed / 99 failed / 4 errors。**99 个失败经基线对照全部预存**：在同一稀疏检出下于 `72ce94c1` 复跑同批文件同样失败（HEAD-only 差集为空），全部为工程治理/环境类（`uc` 模块与 assurance/audit_review 树不在稀疏检出、子进程路径 WinError 267 等），与本线无关。golden 行为锁 `tests/test_golden_behavior_lock.py` 未重算、1 passed。

- 真实原件：E2E 的 NarrativeRef bundle 是本地重签的离线 fixture（满足已发布 wire 合同校验），无网络/无模型。
- NOT_RUN：`tests/test_narrative_source_preparation_e2e.py`（需 CWP producer checkout + PyMuPDF；归 MAIN 集成大节点）。

## 5. 测试根与隔离

- E2E 用 `tempfile.mkdtemp` 独立根，registry 经 `REVENUE_PUBLICATION_REGISTRY` 指入测试根；tearDownClass 删除，结束无残留（测试内断言无隐藏目录）。峰值占用 <1 MB。
- 生产配置/原件/assurance/runs/output 零改动（`git status` 仅本线文件）。model_calls=0，费用 0。

## 6. 需 MAIN 接线与外部限制

- 接线点：三市场新研究输入构建改用三个 builder；安装闭包同步（`tools/sync_installations.py` 归 MAIN）。
- MAIN 大节点：用新 canonical 摘要跑三公司完整新研究 + 独立语义审查（机器检查不替代经济审查）；第二组三公司泛化；live narrative E2E。
- 限制：peer 剔除与角色约束是机器可查面，"文本是否真支持所宣称机制"仍靠独立审查；定性/区间目标未做端点证据绑定（后续需要时扩展 claim 端点结构）。
