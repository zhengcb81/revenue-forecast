# S2 独立静态审查：W16 B02/B03 语义（revenue_basis）

- 工区：`C:/Users/郑曾波/Projects/revenue-forecast-w16-basis` @ 84e2152f（只读）
- 范围：`scripts/research/revenue_basis.py`（全文）、`scripts/contracts/document.py` L161-255、
  `tests/test_w16_revenue_basis.py`；辅证 `scripts/revenue_report.py` L1521-1606、
  `scripts/lint_input.py`/`generate_input_template.py` diff、`scripts/forecast/segments.py` L551。
- 审查人未参与实现；未改文件、未联网。

## 1. revenue_basis 可选性（B02）— PASS
- 接线：document.py L220 `basis = parse_revenue_basis(record)`；L221 `if basis is not None:`
  才进入 `validate_basis_against_document` / L229-230 基期检查。
- 无 `revenue_basis` 键时 `parse_revenue_basis` 立即返回 None（revenue_basis.py L94-95）；
  其唯一前置 `require(isinstance(record, dict))` 与 document.py L177-180 重复，不可能产生新报错。
- 证据：test_w16 `test_parse_returns_none_for_legacy_records`、`test_legacy_history_is_unchanged`
  （validate_document 通过且 `result["historical_revenue"] ==` 原输入）。
- run_forecast 对 legacy 输出零变化；仅报告新增诊断小节（见 S2-2，Info）。

## 2. 复用既有层，无平行复制（B02）— PASS
- input_quantity：`validate_input_quantity_record`（DU5）全量复验（revenue_basis.py L328），并复用
  DU5 `money_currency` 校验文档币种（L336-342），无第二货币/单位表——`_engine_unit_currency`
  查的就是 DU5 `_UNIT_DESCRIPTIONS`（L353-359）。
- components claims：走 `contracts.evidence.validate_claim_ids`（L231-238），与记录级同一规则；
  组件值对齐复用抽取出的 `validate_historical_claim_alignment`（L242-248，消息前缀区分）。
- 组件合计用 Decimal + 文档自身 reconciliation_tolerance（L249-262），未另造容差语义。
- 例外见 finding S2-1（正则小重复，非表复制）。

## 3. 不可比保留观测+理由；not_declared 不被说成已核实（B03）— PASS
- `basis_comparable` 三态：comparable / not_comparable（reason 点名 operations 或
  statement_status 差异）/ not_declared（reason 指明哪侧未声明）（revenue_basis.py L362-392）。
- 报告渲染（revenue_report.py L1540-1566）：not_comparable 输出
  "不可比（reason）；观测值保留，不得当作可比增长；同比…仅按数值列示"；not_declared 输出
  "口径未声明…沿用既有数值比较，不视为已核实口径"。全文无"已核实可比"措辞
  （test_w16 `test_legacy_render_marks_basis_undeclared` 显式断言 NotIn）。
- 模型侧仅锚定基期总额：segments.py L551 原样携带 historical_revenue，引擎不从历史序列
  静默派生"可比增长"；同比仅存在于诊断视图并带状态标签。

## 4. 基期 operations!=total 清晰错误且仅当声明时（B03）— PASS
- `require_total_operations_for_base` 首行 `if basis is None: return`（L277-278），legacy 基期
  仅保留数值对账（document.py L239-255），不受影响。
- 声明时错误消息含年份、非法 operations 值与整改指引（"declare operations=total or move…"，
  L278-284）；仅由 `if basis is not None` 分支在 `year == base_year` 时调用（document.py L229-230）。
- 证据：`test_base_year_continuing_operations_is_rejected`、
  `test_mixed_statement_status_is_not_an_input_error`（非基期差异不阻断，其余部分可继续）。
- 输出侧防篡改：render_markdown 将 historical（含 basis）钉在绑定输入上
  （revenue_report.py L530-537；`test_output_rejects_tampered_basis`）。

## 5. 无新增人工审查/许可门 — PASS
- revenue_basis.py 无任何 review/approval/manual 词汇或状态机；lint_input 仅复用同一 owner
  产出 finding（`if "revenue_basis" in record` 才检查，legacy 无 finding）；template 仅加说明文字。
- unknown 口径在 parse 期即拒（L100-117），不存在 unknown→人工队列路径。

## Findings
- S2-1 / Low / 证据：revenue_basis.py L355 `re.sub(r"[-\s]+","_",…)` 复制了 DU5
  `_normalize_unit`（input_quantities.py L169）的同一正则；`validate_input_quantity_record`
  返回的 `expected` 已含 DU5 规范化后的 engine_unit。/ 建议：改用 `expected["engine_unit"]`
  做纯表查找，消除正则双写（今日语义一致，仅为漂移风险，不构成第二货币表）。
- S2-2 / Info / 证据：legacy 输入的渲染报告新增"口径可比性/基数采用"两节（revenue_report.py
  L1683-1699），下游做报告逐字节比对的工具会看到 diff。/ 建议：如需字节稳定，可为 legacy
  文档省略未声明小节；当前"未声明"措辞符合 B02（不把未声明说成已核实），可不改。

## 结论
5 项全 PASS；2 条 finding（1 Low、1 Info），均不阻塞 B02/B03 验收。
