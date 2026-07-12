"""Output validation and Markdown rendering for revenue-only forecasts."""

from __future__ import annotations

import math
from typing import Any

from revenue_core import (
    ForecastInputError,
    RESEARCH_COVERAGE_STATUSES,
    RESEARCH_DIMENSIONS,
    SCENARIOS,
    ENGINE_VERSION,
    FORECAST_SCHEMA_VERSION,
    calculate_model_path,
    calculate_cagr,
    calculate_confidence,
    canonical_sha256,
    parse_iso_date,
    require,
)


PROHIBITED_OUTPUT_KEYS = {
    "stock_price",
    "share_price",
    "target_price",
    "valuation",
    "pe",
    "ps",
    "dcf",
    "profit",
    "profit_margin",
    "gross_margin",
    "net_margin",
    "cash_flow",
    "free_cash_flow",
    "investment_rating",
    "investment_recommendation",
    "expected_return",
    "position_size",
    "portfolio_weight",
}


def _walk_keys(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            require(normalized not in PROHIBITED_OUTPUT_KEYS, f"prohibited non-revenue output key: {path}.{key}")
            _walk_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_keys(child, f"{path}[{index}]")


def validate_forecast_output(result: dict[str, Any]) -> None:
    for key in result:
        require(str(key).strip().lower() not in PROHIBITED_OUTPUT_KEYS, f"prohibited non-revenue output key: root.{key}")
    for key in ("consolidated_forecast", "confidence", "theme_analysis", "probability_weighted_forecast"):
        if result.get(key) is not None:
            _walk_keys(result[key], f"root.{key}")
    required = (
        "company_name",
        "as_of_date",
        "currency",
        "unit",
        "fiscal_year_end",
        "base_year",
        "forecast_years",
        "historical_revenue",
        "base_revenue",
        "segments",
        "consolidated_forecast",
        "confidence",
        "research_coverage",
        "parameter_trace",
        "sources",
        "evidence_claims",
        "schema_version",
        "engine_version",
        "input_sha256",
        "result_sha256",
    )
    for key in required:
        require(key in result, f"forecast output missing field: {key}")
    require(result["schema_version"] == FORECAST_SCHEMA_VERSION, "forecast output schema_version mismatch")
    require(result["engine_version"] == ENGINE_VERSION, "forecast output engine_version mismatch")
    hash_payload = {key: value for key, value in result.items() if key != "result_sha256"}
    years = list(map(str, result["forecast_years"]))
    base = float(result["base_revenue"])
    consolidated = result["consolidated_forecast"]
    parameter_index = {parameter["parameter_id"]: parameter for parameter in result["parameter_trace"]}
    segment_index = {segment["name"]: segment for segment in result["segments"]}
    require(len(segment_index) == len(result["segments"]), "forecast output contains duplicate segment names")
    for segment in result["segments"]:
        for scenario in SCENARIOS:
            output = segment["scenarios"][scenario]
            recalculated = calculate_model_path(
                output["model"], float(segment["base_revenue"]), output["driver_parameter_ids"],
                parameter_index, list(map(int, result["forecast_years"])), scenario,
            )
            require(recalculated["annual_revenue"] == output["modeled_activity"], f"segment modeled activity mismatch: {segment['name']}/{scenario}")
            modeled = list(output["modeled_activity"].values())
            recognition = segment["recognition"]
            if recognition["timing"] == "over_time":
                progress = list(output["progress_values"].values())
                expected_recognized = [value * factor for value, factor in zip(modeled, progress)]
            elif recognition["mode"] == "lagged_activity":
                lag = recognition["lag_years"]
                expected_recognized = list(output["carry_in_revenue"]) + modeled[:-lag]
            else:
                expected_recognized = modeled
            observed_recognized = list(output["recognized_revenue"].values())
            require(all(math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-9) for left, right in zip(expected_recognized, observed_recognized)), f"segment recognized revenue mismatch: {segment['name']}/{scenario}")
        for year in years:
            require(segment["scenarios"]["low"]["recognized_revenue"][year] <= segment["scenarios"]["base"]["recognized_revenue"][year] <= segment["scenarios"]["high"]["recognized_revenue"][year], f"segment scenario ordering mismatch: {segment['name']}/{year}")
    require(set(consolidated) == set(SCENARIOS), "consolidated_forecast must contain low/base/high")
    for scenario in SCENARIOS:
        forecast = consolidated[scenario]
        annual = forecast["annual_revenue"]
        require(list(annual) == years, f"annual revenue years mismatch in {scenario}")
        values = [float(annual[year]) for year in years]
        require(math.isclose(float(forecast["terminal_revenue"]), values[-1], rel_tol=1e-9, abs_tol=1e-9), f"terminal revenue mismatch in {scenario}")
        expected_cagr = calculate_cagr(base, values[-1], len(years))
        require(
            (expected_cagr is None and forecast["cagr"] is None)
            or math.isclose(float(forecast["cagr"]), float(expected_cagr), rel_tol=1e-9, abs_tol=1e-9),
            f"CAGR mismatch in {scenario}",
        )
        for year in years:
            previous = base if year == years[0] else float(annual[years[years.index(year) - 1]])
            expected_growth = None if previous == 0 else float(annual[year]) / previous - 1
            observed_growth = forecast["annual_growth"][year]
            require((expected_growth is None and observed_growth is None) or math.isclose(float(observed_growth), float(expected_growth), rel_tol=1e-9, abs_tol=1e-9), f"annual growth mismatch in {scenario}/{year}")
            segment_sum = sum(float(segment["annual_revenue"][year]) for segment in forecast["segment_bridge"])
            adjustment_sum = sum(float(adjustment["annual_adjustment"][year]) for adjustment in forecast["adjustment_bridge"])
            require(math.isclose(segment_sum + adjustment_sum, float(annual[year]), rel_tol=1e-9, abs_tol=1e-9), f"company bridge mismatch in {scenario}/{year}")
            for bridge in forecast["segment_bridge"]:
                require(math.isclose(float(bridge["annual_revenue"][year]), float(segment_index[bridge["name"]]["scenarios"][scenario]["recognized_revenue"][year]), rel_tol=1e-9, abs_tol=1e-9), f"segment bridge cross-check mismatch in {scenario}/{bridge['name']}/{year}")
        contribution = forecast["incremental_contribution"]
        require(math.isclose(float(contribution["total"]), float(forecast["incremental_revenue"]), rel_tol=1e-9, abs_tol=1e-9), f"incremental contribution mismatch in {scenario}")
    for year in years:
        require(
            consolidated["low"]["annual_revenue"][year]
            <= consolidated["base"]["annual_revenue"][year]
            <= consolidated["high"]["annual_revenue"][year],
            f"scenario ordering mismatch in output/{year}",
        )
    weighted = result.get("probability_weighted_forecast")
    probabilities = result.get("scenario_probabilities")
    require((weighted is None) == (probabilities is None), "probability output is inconsistent")
    if weighted is not None:
        for year in years:
            expected = sum(float(probabilities[scenario]) * consolidated[scenario]["annual_revenue"][year] for scenario in SCENARIOS)
            require(math.isclose(expected, float(weighted["annual_revenue"][year]), rel_tol=1e-9, abs_tol=1e-9), f"probability-weighted revenue mismatch in {year}")
        terminal = float(weighted["annual_revenue"][years[-1]])
        require(math.isclose(terminal, float(weighted["terminal_revenue"]), rel_tol=1e-9, abs_tol=1e-9), "probability-weighted terminal mismatch")
        expected_cagr = calculate_cagr(base, terminal, len(years))
        require((expected_cagr is None and weighted["expected_terminal_implied_cagr"] is None) or math.isclose(float(expected_cagr), float(weighted["expected_terminal_implied_cagr"]), rel_tol=1e-9, abs_tol=1e-9), "probability-weighted CAGR mismatch")
        require(math.isclose(terminal - base, float(weighted["incremental_revenue"]), rel_tol=1e-9, abs_tol=1e-9), "probability-weighted increment mismatch")
    require(isinstance(result["sources"], list) and result["sources"], "forecast output requires sources")
    require(isinstance(result["parameter_trace"], list) and result["parameter_trace"], "forecast output requires parameter trace")
    require(isinstance(result["evidence_claims"], list) and result["evidence_claims"], "forecast output requires evidence claims")
    coverage = result["research_coverage"]
    require(isinstance(coverage, dict), "research_coverage output must be an object")
    dimensions = coverage.get("dimensions")
    require(isinstance(dimensions, list) and len(dimensions) == len(RESEARCH_DIMENSIONS), "research_coverage output must contain nine dimensions")
    require([record.get("dimension") for record in dimensions] == list(RESEARCH_DIMENSIONS), "research_coverage dimensions are missing or out of order")
    parameter_ids = {parameter["parameter_id"] for parameter in result["parameter_trace"]}
    source_ids = {source["source_id"] for source in result["sources"]}
    recomputed_counts = {status: 0 for status in RESEARCH_COVERAGE_STATUSES}
    for record in dimensions:
        status = record.get("status")
        require(status in RESEARCH_COVERAGE_STATUSES, f"invalid research coverage status: {status}")
        recomputed_counts[status] += 1
        require(isinstance(record.get("conclusion"), str) and record["conclusion"].strip(), f"research coverage conclusion is required for {record['dimension']}")
        require(isinstance(record.get("revenue_mechanism"), str) and record["revenue_mechanism"].strip(), f"research coverage revenue mechanism is required for {record['dimension']}")
        require(set(record.get("parameter_ids", [])) <= parameter_ids, f"research coverage contains unknown parameter for {record['dimension']}")
        require(set(record.get("source_ids", [])) <= source_ids, f"research coverage contains unknown source for {record['dimension']}")
        if status == "data_gap":
            expected_gap = f"{record['dimension']}: {record['conclusion']}"
            require(expected_gap in result.get("data_gaps", []), f"research data gap missing from output: {record['dimension']}")
    require(coverage.get("counts") == recomputed_counts, "research_coverage counts mismatch")
    for sensitivity in result.get("sensitivities", []):
        baseline = float(sensitivity["baseline_terminal_revenue"])
        impact = max(abs(float(sensitivity["down_terminal_revenue"]) - baseline), abs(float(sensitivity["up_terminal_revenue"]) - baseline))
        require(math.isclose(impact, float(sensitivity["max_absolute_terminal_impact"]), rel_tol=1e-9, abs_tol=1e-9), f"sensitivity impact mismatch: {sensitivity['name']}")
        expected_relative = None if baseline == 0 else impact / baseline
        observed_relative = sensitivity["max_relative_terminal_impact"]
        require((expected_relative is None and observed_relative is None) or math.isclose(float(expected_relative), float(observed_relative), rel_tol=1e-9, abs_tol=1e-9), f"sensitivity relative impact mismatch: {sensitivity['name']}")
    confidence = result["confidence"]
    require(math.isclose(sum(float(value) for value in confidence["components"].values()), float(confidence["score"]), rel_tol=1e-9, abs_tol=1e-9), "confidence component total mismatch")
    expected_rating = "high" if confidence["score"] >= 80 else "medium" if confidence["score"] >= 55 else "low"
    require(confidence["rating"] == expected_rating, "confidence rating mismatch")
    require(all(confidence.get("quality_gates", {}).values()), "confidence quality gate failed")
    reconstructed_segments = []
    for segment in result["segments"]:
        reconstructed_segments.append({
            "name": segment["name"],
            "recognition": segment["recognition"],
            "scenarios": {
                scenario: {
                    "model": segment["scenarios"][scenario]["model"],
                    "driver_parameter_ids": segment["scenarios"][scenario]["driver_parameter_ids"],
                }
                for scenario in SCENARIOS
            },
        })
    reconstructed_adjustments = []
    for base_adjustment in consolidated["base"]["adjustment_bridge"]:
        reconstructed_adjustments.append({
            "name": base_adjustment["name"],
            "category": base_adjustment["category"],
            "scenario_parameter_ids": {
                scenario: next(item for item in consolidated[scenario]["adjustment_bridge"] if item["name"] == base_adjustment["name"])["parameter_ids"]
                for scenario in SCENARIOS
            },
        })
    reconstructed_data = {
        "segments": reconstructed_segments,
        "forecast_adjustments": reconstructed_adjustments,
        "historical_accuracy_records": result.get("historical_accuracy_records", []),
    }
    reconstructed_validated = {
        "parameter_index": parameter_index,
        "claim_index": {claim["claim_id"]: claim for claim in result["evidence_claims"]},
        "source_index": {source["source_id"]: source for source in result["sources"]},
        "as_of_date": parse_iso_date(result["as_of_date"], "as_of_date"),
        "research_coverage": {"counts": coverage["counts"]},
    }
    expected_confidence = calculate_confidence(reconstructed_data, reconstructed_validated, result, result.get("sensitivities", []))
    require(expected_confidence["components"] == confidence["components"], "confidence components recomputation mismatch")
    require(math.isclose(float(expected_confidence["score"]), float(confidence["score"]), rel_tol=1e-9, abs_tol=1e-9), "confidence score recomputation mismatch")
    theme = result.get("theme_analysis")
    if theme is not None:
        for scenario in SCENARIOS:
            values = theme["scenarios"][scenario]
            expected_theme_terminal = sum(float(list(segment_index[name]["scenarios"][scenario]["recognized_revenue"].values())[-1]) for name in theme["segment_names"])
            require(math.isclose(expected_theme_terminal, float(values["theme_terminal_revenue"]), rel_tol=1e-9, abs_tol=1e-9), f"theme terminal mismatch: {scenario}")
            counterfactual_parameter = parameter_index[values["counterfactual_parameter_id"]]
            require(math.isclose(float(counterfactual_parameter["value"]), float(values["counterfactual_terminal_revenue"]), rel_tol=1e-9, abs_tol=1e-9), f"theme counterfactual mismatch: {scenario}")
            expected_increment = float(values["theme_terminal_revenue"]) - float(values["counterfactual_terminal_revenue"])
            require(math.isclose(expected_increment, float(values["theme_incremental_revenue"]), rel_tol=1e-9, abs_tol=1e-9), f"theme increment mismatch: {scenario}")
            expected_elasticity = None if base == 0 else expected_increment / base
            require((expected_elasticity is None and values["theme_elasticity_to_company_base"] is None) or math.isclose(float(expected_elasticity), float(values["theme_elasticity_to_company_base"]), rel_tol=1e-9, abs_tol=1e-9), f"theme elasticity mismatch: {scenario}")
    require(result["result_sha256"] == canonical_sha256(hash_payload), "forecast result hash mismatch")


def _num(value: Any) -> str:
    if value is None:
        return "—"
    return f"{float(value):,.2f}"


def _pct(value: Any) -> str:
    if value is None:
        return "—"
    return f"{float(value) * 100:.1f}%"


def _escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(result: dict[str, Any]) -> str:
    validate_forecast_output(result)
    years = list(map(str, result["forecast_years"]))
    lines: list[str] = [
        f"# {_escape(result['company_name'])}营收预测",
        "",
        f"- 信息截止日：{result['as_of_date']}",
        f"- 财年截止日：{result['fiscal_year_end']}",
        f"- 币种与单位：{result['currency']} {result['unit']}",
        f"- 基期营收：{_num(result['base_revenue'])}",
        f"- 预测版本：{_escape(result.get('forecast_version', '—'))}",
        "",
        "## 核心营收结论",
        "",
        "| 情景 | 终值营收 | CAGR | 营收增量 |",
        "|---|---:|---:|---:|",
    ]
    for scenario in SCENARIOS:
        forecast = result["consolidated_forecast"][scenario]
        lines.append(f"| {scenario} | {_num(forecast['terminal_revenue'])} | {_pct(forecast['cagr'])} | {_num(forecast['incremental_revenue'])} |")
    if result.get("probability_weighted_forecast") is not None:
        weighted = result["probability_weighted_forecast"]
        lines.extend([
            "",
            "### 概率加权路径",
            "",
            f"- 概率：Low {_pct(result['scenario_probabilities']['low'])}；Base {_pct(result['scenario_probabilities']['base'])}；High {_pct(result['scenario_probabilities']['high'])}。",
            f"- 加权终值：{_num(weighted['terminal_revenue'])}；隐含CAGR：{_pct(weighted['expected_terminal_implied_cagr'])}。",
            f"- 校准理由：{_escape(weighted['probability_rationale'])}",
        ])

    lines.extend(["", "## 历史营收", "", "| 年度 | 营收 | 来源ID |", "|---:|---:|---|"])
    for record in result["historical_revenue"]:
        lines.append(f"| {record['year']} | {_num(record['value'])} | {_escape(', '.join(record['source_ids']))} |")

    coverage = result["research_coverage"]
    counts = coverage["counts"]
    lines.extend([
        "",
        "## 九维研究覆盖",
        "",
        f"- 进入模型：{counts['modeled_driver']}；数据缺口：{counts['data_gap']}；当前不重要：{counts['immaterial']}。",
        "- 本表用于防止研究漏项，不直接给CAGR或置信度加分。",
        "",
        "| 维度 | 状态 | 结论 | 营收传导 | 参数ID | 来源ID | 理由 |",
        "|---|---|---|---|---|---|---|",
    ])
    for record in coverage["dimensions"]:
        lines.append(
            f"| {_escape(record['dimension'])} | {_escape(record['status'])} | {_escape(record['conclusion'])} | "
            f"{_escape(record['revenue_mechanism'])} | {_escape(', '.join(record['parameter_ids']) or '—')} | "
            f"{_escape(', '.join(record['source_ids']) or '—')} | {_escape(record.get('rationale', '—'))} |"
        )

    lines.extend(["", "## 年度情景路径", "", "| 年度 | Low | Base | High | Base同比 |", "|---:|---:|---:|---:|---:|"])
    for year in years:
        lines.append(
            f"| {year} | {_num(result['consolidated_forecast']['low']['annual_revenue'][year])} | "
            f"{_num(result['consolidated_forecast']['base']['annual_revenue'][year])} | "
            f"{_num(result['consolidated_forecast']['high']['annual_revenue'][year])} | "
            f"{_pct(result['consolidated_forecast']['base']['annual_growth'][year])} |"
        )

    lines.extend(["", "## 三情景经营驱动", "", "| 分部 | 情景 | 驱动 | 年度 | 参数ID | 数值 |", "|---|---|---|---:|---|---:|"])
    for segment in result["segments"]:
        for scenario in SCENARIOS:
            output = segment["scenarios"][scenario]
            for driver, values in output["driver_values"].items():
                ids = output["driver_parameter_ids"].get(driver, [])
                for index, year in enumerate(years):
                    parameter_id = ids[index] if index < len(ids) else "default"
                    lines.append(f"| {_escape(segment['name'])} | {scenario} | {_escape(driver)} | {year} | {_escape(parameter_id)} | {_num(values[year])} |")

    lines.extend(["", "## 分部驱动与收入确认", "", "| 分部 | 模型 | 基期营收 | 确认时点 | 触发条件 | 列报 |", "|---|---|---:|---|---|---|"])
    for segment in result["segments"]:
        recognition = segment["recognition"]
        model = segment["scenarios"]["base"]["model"]
        lines.append(
            f"| {_escape(segment['name'])} | {_escape(model)} | {_num(segment['base_revenue'])} | "
            f"{_escape(recognition['timing'])} | {_escape(recognition['trigger'])} | {_escape(recognition['presentation'])} |"
        )

    lines.extend(["", "## Base情景增量归因", "", "| 项目 | 终值营收增量 |", "|---|---:|"])
    contribution = result["consolidated_forecast"]["base"]["incremental_contribution"]
    for item in contribution["segments"]:
        lines.append(f"| {_escape(item['name'])} | {_num(item['terminal_incremental_revenue'])} |")
    lines.append(f"| 公司级调整 | {_num(contribution['adjustments'])} |")
    lines.append(f"| 合计 | {_num(contribution['total'])} |")

    lines.extend(["", "## 敏感性", ""])
    if result["sensitivities"]:
        lines.extend(["| 参数 | 冲击类型 | 请求值(下/上) | 有效值(下/上) | 截断 | 下行终值 | 基准终值 | 上行终值 | 最大相对影响 |", "|---|---|---|---|---|---:|---:|---:|---:|"])
        for item in result["sensitivities"]:
            lines.append(
                f"| {_escape(item['parameter_id'])} | {_escape(item['shock_type'])} | {_num(item['requested_values']['down'])}/{_num(item['requested_values']['up'])} | "
                f"{_num(item['effective_values']['down'])}/{_num(item['effective_values']['up'])} | {_escape(item['clamped'])} | {_num(item['down_terminal_revenue'])} | "
                f"{_num(item['baseline_terminal_revenue'])} | {_num(item['up_terminal_revenue'])} | {_pct(item['max_relative_terminal_impact'])} |"
            )
    else:
        lines.append("未配置确定性敏感性测试。")

    confidence = result["confidence"]
    lines.extend([
        "",
        "## 预测置信度",
        "",
        f"- 等级：{confidence['rating']}",
        f"- 分数：{confidence['score']:.1f}/100",
        f"- 驱动证据覆盖率：{_pct(confidence['driver_evidence_coverage'])}",
        "",
        "| 组成 | 得分 |",
        "|---|---:|",
    ])
    for name, score in confidence["components"].items():
        lines.append(f"| {_escape(name)} | {score:.1f} |")
    lines.extend(["", "### 质量硬门", ""])
    lines.extend([f"- {_escape(name)}：{'通过' if passed else '失败'}" for name, passed in confidence["quality_gates"].items()])

    if result.get("theme_analysis") is not None:
        lines.extend(["", "## 主题反事实", "", "| 情景 | 主题终值 | 反事实终值 | 主题增量 | 占公司终值 |", "|---|---:|---:|---:|---:|"])
        for scenario in SCENARIOS:
            item = result["theme_analysis"]["scenarios"][scenario]
            lines.append(f"| {scenario} | {_num(item['theme_terminal_revenue'])} | {_num(item['counterfactual_terminal_revenue'])} | {_num(item['theme_incremental_revenue'])} | {_pct(item['theme_share_of_company_terminal'])} |")

    lines.extend(["", "## 反证指标与数据缺口", ""])
    indicators = result.get("disconfirming_indicators", [])
    gaps = result.get("data_gaps", [])
    lines.append("### 反证指标")
    lines.extend([f"- {_escape(item)}" for item in indicators] or ["- 未提供。"])
    lines.extend(["", "### 数据缺口"])
    lines.extend([f"- {_escape(item)}" for item in gaps] or ["- 未记录数据缺口。"])

    lines.extend(["", "## 参数—证据claim映射", "", "| 参数ID | 身份 | 数值 | 期间 | 维度 | Claim ID | 来源ID | 支持类型 | 定位 | 短摘录 |", "|---|---|---:|---|---|---|---|---|---|---|"])
    claims = {claim["claim_id"]: claim for claim in result["evidence_claims"]}
    for parameter in result["parameter_trace"]:
        claim_ids = parameter.get("claim_ids", [])
        if not claim_ids:
            lines.append(f"| {_escape(parameter['parameter_id'])} | {_escape(parameter['kind'])} | {_num(parameter['value'])} | {_escape(parameter['period'])} | {_escape(parameter['dimension'])} | — | — | — | — | — |")
        for claim_id in claim_ids:
            claim = claims[claim_id]
            lines.append(f"| {_escape(parameter['parameter_id'])} | {_escape(parameter['kind'])} | {_num(parameter['value'])} | {_escape(parameter['period'])} | {_escape(parameter['dimension'])} | {_escape(claim_id)} | {_escape(claim['source_id'])} | {_escape(claim['support_type'])} | {_escape(claim['locator'])} | {_escape(claim['excerpt'])} |")

    lines.extend(["", "## 参数来源", "", "| ID | 等级 | 类型 | 发布方 | 日期 | 定位 | 标题 |", "|---|---:|---|---|---|---|---|"])
    for source in result["sources"]:
        lines.append(
            f"| [{_escape(source['source_id'])}]({_escape(source['url'])}) | {_escape(source.get('source_rank', '—'))} | "
            f"{_escape(source['source_type'])} | {_escape(source['publisher'])} | {_escape(source['published_date'])} | "
            f"{_escape(source['page_or_section'])} | {_escape(source['title'])} |"
        )
    lines.append("")
    return "\n".join(lines)
