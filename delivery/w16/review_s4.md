# W16 B05/B06 独立静态审查（S4，未参与实现）

- 工区：C:/Users/郑曾波/Projects/revenue-forecast-w16-basis @ commit 84e2152f（w16: optional revenue basis metadata）
- 方式：只读静态审查，未运行测试、未改文件、未联网。行号均为该 commit 实际行号。
- 结论：5 项检查全部 PASS；2 条 finding（1 低危 + 1 信息级）。

## 1. 校验是否在公开链上 — PASS

- CLI：`scripts/revenue_forecast.py:85` main → `prepare_forecast`（:47-51）→ `run_forecast`（formal 后再 `validate_forecast_output`）；`--validate-only` 走 draft 强验证。
- `scripts/revenue_core.py:63` `_build_forecast_draft` → `validate_document(data)`；:448 附近 `run_forecast` → `validate_published_forecast(result, data)`（强验证，含 W16 输出检查）。
- `scripts/contracts/document.py:1119`（fail-fast）与 :1197-1205（collect-all，gate 名 `historical_revenue`）调用 `validate_historical_revenue`；:220-230 调用唯一 owner `research/revenue_basis.py`（`parse_revenue_basis`、`validate_basis_against_document`、基年 `require_total_operations_for_base`）。
- `scripts/forecast/segments.py:551` 结果原样携带 `data["historical_revenue"]`；`revenue_report.py:1614-1615` `render_markdown` 先 `validate_forecast_output` 再渲染。
- 判定：接线在 validate_document → run_forecast → CLI 公开链上，不是独立 lint。

## 2. 报告是否说明实际 base 采用与口径/转换状态 — PASS

- `_base_adoption_lines`（revenue_report.py:1569-1606）：写明实际采用的 FY 观测、数值、口径标签（总额/原表 或 未声明）、source_ids、与报告总额参数比对（参数 ID、值、容差、差值）、换算状态（附DU5换算记录/未附原始值换算记录）。
- `reported_total_value` 取 `result["base_revenue"]`，经查 segments.py:423-425 即 `reported_total_revenue_parameter_id` 参数真值，标签诚实非"helper通过"式声明。
- 历史表新增 口径/换算 两列（:1679-1697）；`_basis_comparability_lines`（:1540-1566）三分支：同口径可比 / 不可比（含 statement_status 等理由）/ 口径未声明（不视为已核实），同比或"同比未定义"附理由。

## 3. CLI 8 案例齐全性与断言质量 — PASS（见 S4-1）

- 同口径正常：SameBasisSuite，断言输出 JSON `operations`/`engine_value=150.0` 与 Markdown 关键串（总额/原表、口径可比性、同口径可比、基数采用、usd_billion、与报告总额参数一致）。
- 持续经营替代总额：err_continuing，stderr 含 `continuing`+`total`。
- 期间混淆：err_quarter，stderr 含 `quarter`+`fiscal`。
- 无桥：diag_no_bridge，Markdown 含 不可比+statement_status+重述，且断言输出观测值保留 [140,150]（不被丢弃/改写）。
- 有桥：diag_bridged（双侧 restated）+ 案例一 components（continuing+discontinued=total，附 exact_value claim）。
- 币种尺度转换：案例一 input_quantity 0.15 USD billion→150 USD million；err_conversion 断言 stderr 含 `input_quantity`+`999`。
- 零/负基数：diag_zero_base，Markdown 含 同比未定义+zero；负基数在输入侧不可达（document.py:195 要求 value>=0），零基数即完备。
- legacy 缺元数据：diag_legacy，值保留、输出记录无 `revenue_basis` 键、Markdown 含 未声明 且无 已核实可比。
- 断言均落到 stderr 消息 / 输出 JSON / Markdown 具体内容；错误案例另断言退出码 2 且输出文件不存在（无孤儿工件）。

## 4. 真实子进程与独占目录 — PASS（见 S4-2）

- tests/test_w16_revenue_basis_cli.py:77-92 `subprocess.run([sys.executable, scripts/revenue_forecast.py, ...])`，真实 CLI 子进程，非 import 调用。
- setUp 每测试 `mkdtemp` 独占根目录，每案例再建独立子目录；`REVENUE_PUBLICATION_REGISTRY`、`PYTHONDONTWRITEBYTECODE` 指入案例目录；tearDown 先校验 resolved 路径位于系统 temp 才 rmtree（:50-57）。
- 中文+空格目录存在：案例目录 `基期 口格 same basis`（:138），并以同路径读取输出断言。

## 5. 输出校验 schema 版本门控是否可绕过 — PASS

- W16 equality 检查（revenue_report.py:511-538）门控为 `data is not None` 且 `requires_bound_input_schema`，后者仅 {3.7, 3.8, 3.9, 3.10}（schema_compatibility.py:68-76），与既有 W05 字段（company_name/currency 等）同一门控模式，非 W16 新开的旁门。
- 绕过面分析：旧 schema（≤3.6）输出走 `validate_legacy_output` → `_validate_forecast_output(result, None)`（:1471-1485）确实跳过该检查，但 (a) 新文档无法声明旧 schema——`validate_top_level`（document.py:97-105）仅收 3.7-3.10，而 `parse_revenue_basis` 对任何记录无 schema 门槛地执行，故携带 revenue_basis 的新发布必然落在受控版本；(b) 旧工件系 W16 前产物，不可能携带 basis 元数据；(c) `validate_forecast_output` 在 data=None 时回退 `result["input_document"]`（:1497-1498），run_forecast 恒嵌入，故 CLI/render/发布路径检查仍生效。未发现实际绕过路径。

## Findings

- S4-1 [低] 证据：CLI 矩阵的期间混淆仅覆盖 `period_kind="quarter"`（test:173-182）；施工卡点名的"年累计(ytd)"变体只在单元级覆盖（tests/test_w16_revenue_basis.py:188-190）。二者由同一 require 门（research/revenue_basis.py:191-198）拒绝，实际风险极低。建议：补一条 ytd 的 CLI 案例，或在测试注释中显式指明与 quarter 同门等价。
- S4-2 [信息] 证据：8 案例中仅成功案例（案例一）使用中文+空格目录，错误/诊断案例均为 ASCII 目录名，非 ASCII 路径下的失败路径（stderr 编码、退出码）未被 exercised。建议（可选）：让错误案例轮流使用非 ASCII/空格目录。
