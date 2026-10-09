# 管理目标比较的指标、期间与覆盖

这是 schema 3.7 的可选输入扩展。旧年度金额目标、旧 `comparison_basis="annual_recognized_revenue"` 转换、旧快照和默认输出保持原契约。新对象版本为 `management-target-comparison/1`；不改原管理层 statement、raw unit/currency/scale 或 scope。

## 金额、季度、同比

年度金额：`comparison_basis={"schema_version":"management-target-comparison/1","metric_kind":"annual_revenue_level","period":"FY2028"}`。比较同一公司/分部 effective revenue 路径。

季度金额：

```json
{"schema_version":"management-target-comparison/1","metric_kind":"quarterly_revenue_level","period":"FY2027Q3","scenario_parameter_ids":{"low":["q3_low"],"base":["q3_base"],"high":["q3_high"]}}
```

每个引用是已进入年度 derived bridge 的 revenue 参数，具有 `period="FY2027"`、`measurement_period="FY2027Q3"`、对应 scenario、统一币种/scale 和已检查 claims。季度参数相加得到实际季度路径；不乘四。年度合计的其他季度和额外周仍须有自己的经营/确认依据。Q/H 期间标签、annual/TTM/run-rate/cumulative 口径不能互换。

同比：

```json
{"schema_version":"management-target-comparison/1","metric_kind":"year_over_year_growth","period":"FY2028","base_period":"FY2027","raw_ratio_basis":"percent"}
```

原文 70 percent 保留为 raw_target_value=70/raw_unit=percent，comparison_value=0.70。每个 scenario 使用自己 FY2028/FY2027 − 1。raw_ratio_basis 明确 percent、fraction 或 level_multiple；2 倍收入对应增长 1。`greater_than`/`less_than` 是严格界限，不受 approximately tolerance 软化。数值区间保持两个端点，不制造中心美元目标。

comparison 输出 metric_kind/period/unit、modeled_value、target_value 或 low/high、comparison、meets_target、status/reason；同比另列 base period/value、percentage_points 差。逐情景分母 × (1+ratio) 仅为 analyst_derived revenue benchmark，具有公式和美元差，不能改写为管理层发布的美元目标。缺/零/负基期保留 null，不除零或变为 0；基期未知可填 base_period=null 并保留 gap。

币种、scope 或季度桥不可比时 treatment=unmodeled_data_gap，comparison_value=null、mapped_scenarios=[]，保留原 rationale。季度 scenario_parameter_ids=null 明确没有比较路径。无需重复的 unmodeled_reason 或人工许可。年度/累计/期末运行率原契约继续适用；无法支持的 TTM 或 percentage-point 变化保留原文和明确 gap，不改名为年度收入同比。

主 Markdown 在管理目标覆盖附近展示原文、来源日期、指标/期间、各情景差与条件；没有市场 consensus 时，不称为市场超预期。

## 官方沟通范围

`checked_scope` 可选，版本 `management-communication-scope/1`，完整字段为 category、start_date、end_date、coverage_complete、items。每项含 item_ref、source_id、content_role、selected、read、skip_reason，可保留 published_date。content_role 是 business_original、discovery_index 或 index_notice。只有实际读取的 business_original 才计入 source_ids；发现元数据、Loading 和通知不能冒充全文读取。未选项必须记录 skip/materiality 原因，已选但未读项使范围 incomplete。

重大事件范围必须从已获得的最新 filing 的真实发布时间延伸到 as_of。早期 filing 自身存在不能证明此后范围检查完成。真实 W03 discovery 的 incomplete/unknown 应传为 coverage_complete=false，不能把未读填 checked。not_checked/incomplete 保留明确 gap。新 audit 输入使用 `audit_communication_coverage=true`：没有 scope 的 legacy checked 只诊断 semantically_unverified，旧无新增字段输入保持字节语义兼容，不补造搜索事件。

## 实际 recipe

```text
python -X utf8 -B tools/run_target_measurement_e2e.py --input <new-input.json> --output-root <absent-owned-root> --version <new-version>
```

依次运行 native validate、compute/render 和 snapshot，并将 registry 限定在新 output root。commands.json 记录实际命令、exit 和耗时。该 recipe 无来源或模型调用。它不证明原始来源真实或经济范围完成；MAIN 真实 source/narrative 消费与四路研究审查仍是 M2/M3 的工作。
