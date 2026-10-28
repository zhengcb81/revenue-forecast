# narrative-adoption-audit

只读的叙述证据采用观察工具（W20）。它回答一个问题：**RF 拿到了哪些来源业务信息，最终预测产物的哪些驱动/假设/情景/年度路径节点真正引用了它们**。本工具是诊断，不是许可：不评级、不产出"采用率"签收、不判断经济合理性——那些仍归 RF 验证与四个审查角色。

## 用法

```
python tools/narrative_adoption_audit/cli.py --forecast forecast.json \
  [--input input.json] [--snapshot snapshot.json] \
  [--consumption consumption.json ...] \
  [--narrative request.json bundle.json[.gz] receipt.json ...] \
  [--output report.json] [--max-items N] [--max-input-bytes N] [--pretty]
```

- 所有输入都是**显式文件**：最终 forecast 产物（必填）、可选的输入文档/快照交叉核对、显式 consumption 回执、显式公开叙述 wire 三件套（request JSON + bundle 字节[支持 .gz] + receipt 字节）。不扫目录、不联网、不开数据库、不跑模型。
- 输出默认打 stdout（canonical JSON，字节稳定）；`--output` 只写**不存在**的新文件，拒绝覆盖任何已存在文件，也拒绝与任何输入路径相同。
- 退出码：0=报告产出（诊断存在也算）；2=用法/IO/JSON/资源界错误。
- 资源界：`--max-items`（默认 20000）限制报告条目；`--max-input-bytes`（默认 64MiB）限制单文件。索一次构建，每条目 O(1) 查找，总体线性。

## 观察语义

采用 = canonical 引用链在最终产物的**投影节点**可观察（segment 情景 driver 槽位、base_revenue、recognition 基础、驱动树 evidence 节点、coverage 维度、管理目标/沟通、调整桥、情景概率、历史口径）。内嵌 `input_document` 与 `parameter_trace` 是输入回显，**不**算采用证据。

| item kind | 连接键 | 说明 |
|---|---|---|
| `span` | `span_id`（canonical urn） | 叙述 span；由 consumption 回执 join |
| `claim` / `source` / `summary_claim` | 文档内 display key | 绝不跨文档拼接；跨源同文本记 `display_key_collision_not_joined` |

状态机：

- `used` — 引用链在 ≥1 个投影节点可观察（`cited_by` 带定位与 actual IDs）。
- `not_used_when_provable` — 结构性可证不进图：claim 只挂在不进任何公式闭包的参数（`parameter_not_wired_to_any_node`）；span 被来源分区为 `context_only`/`unresolved`（按契约永不能作数字支撑）。
- `not_observed` — 材料在（span 运输了/summary 可读/源登记了）但无绑定或无投影引用。**不**断言模型没用。
- `unverifiable` — 绑定材料缺/错：claim/param 不在本输入、source_sha256 错配、receipt 公式引用与本输入依赖图不符（跨 run 拼接）、narrative wire 被契约拒绝、span 材料未提供。

口径观察（只核已有绑定，不另算收入）：`period_mismatch_at_node`、`unknown_segment_attribution`、`duplicate_capture_sha`、`target_currency_mismatch`。缺 hash 沿宽松政策记 `hash_missing_unknown`（info），不加新门禁；hash 提供则必验。

报告 schema：`rf-narrative-adoption-report/1`，含 `diagnostic_only_not_a_permission_gate=true`、`observation_scope`、逐 item `cited_by`、命名 reason/diagnostic 码、计数与资源块。同一输入重复执行字节稳定。

## 已知边界

见报告 `limitations` 字段：无执行追踪（观察的是声明的引用接线，不是模型内心）；引用缺失不能证明作者推理没用该材料；context 证据不是数字支撑；诊断不是许可。
