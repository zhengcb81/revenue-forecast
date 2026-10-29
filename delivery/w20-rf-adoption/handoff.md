# W20-RF-ADOPTION 交接（handoff）

日期：2026-10-29（R1 返工更新；首版 2026-10-28）。卡号：W20-RF-ADOPTION（`docs/plans/w20-rf-adoption-2026-10-28/construction_card.md`）。状态：**READY_FOR_ROOT_REVIEW**（R1 返工完成，OPEN 清空）。

> **R1 返工（2026-10-29）**：ROOT 验收返工单三项已全部修复并经独立复审 PASS（见 `review/rework-review.md`）。受审实现 commit 由 `8b221153` 更新为 **`e4657377`**；测试由 26 项扩至 **37 项**。原 2026-10-28 初审/终审记录保留于 `review/initial.*`、`review/final.*` 不覆盖。
>
> - **RF-R1/P1**：receipt 解析重写为共享 owner 的整链验证——运输 span→canonical parent→capture 映射→RF 本地 source→claim 归属/材料/target→parameter→run formula 逐条已知边核对；错 source/hash/locator/parser/claim 配对/claim 材料/跨 run 全部命名 unverifiable；缺 hash 仍宽松 unknown。修复 ROOT 反例 foreign_span_with_existing_capture 与 wrong_explicit_source_id。
> - **RF-R2/P2**：canonical span 聚合全部合法依赖路径（cited_by 并集、内容排序、跨回执/顺序不变），invalid 路径保留命名诊断不吞 valid；替换误导性 "several receipts" 为 span_dependencies_aggregated。修复 two_valid_bindings。
> - **RF-R3/P2**：`_gunzip_bounded` 流式解压，展开量最多 limit+1 即命名 `resource_limit`；截断/损坏 → `input_decompress_failed`；失败 exit 2 不留半输出；压缩字节上限保留。修复 133B→100000B 炸弹反例。
> - 复审追加修复：/3 多父投影按 span 自身 source_id 解析实际父（parent_sha 不再固定 refs[0]），合法多父回执零假诊断。

## 交付了什么

只读的叙述证据采用观察工具 `tools/narrative_adoption_audit/`（纯核心 `audit.py` + 薄 CLI + README），报告 schema `rf-narrative-adoption-report/1`。它回答"RF 拿到了哪些来源业务信息、最终预测产物的哪些投影节点真正引用了它们"，显式输入（forecast/input/snapshot/consumption 回执/narrative wire 三件套）、默认 stdout、`--output` 只写新文件、无扫描/联网/DB/模型/时钟、字节稳定、线性资源界（`--max-items`/`--max-input-bytes`，压缩与解压两侧同时受界）。

核心语义（全部与既有合同对齐，不重造）：
- 采用 = canonical 引用链在**投影节点**（segment 情景 driver 槽位、base_revenue、recognition、驱动树 evidence、coverage、目标/沟通、adjustment、概率、历史口径、约束）可观察；内嵌 `input_document`/`parameter_trace` 回显**不是**采用证据。
- 四状态：`used` / `not_used_when_provable`（参数不进公式闭包；/4 能力位 context_only/unresolved——回执绑定也被 `context_span_bound_as_support` 标记而不服从）/ `not_observed`（材料在但无绑定或无投影引用，不断言没用）/ `unverifiable`（claim/param 不在本输入、hash 错配、`receipt_run_mismatch` 跨 run 拼接、wire 被契约拒绝），全部带 named reason + `cited_by`（node_type/location/actual IDs）。
- canonical 键（span urn/sha256）连接，display key（claim_id 文本）永不跨文档拼接（`display_key_collision_not_joined`）；hash 提供必验、缺失 `hash_missing_unknown` 宽松不加门禁。
- 口径观察（period_mismatch_at_node / unknown_segment_attribution / target_currency_mismatch / duplicate_capture_sha）只核已有绑定，不另算收入、不 LLM、不 rating；`diagnostic_only_not_a_permission_gate=true`。

## 测试与验证

- 单元 35（`tests/test_w20_narrative_adoption_audit.py`）：卡测试包 11 项全覆盖 + /4 能力位三态 + elimination/sum_cap/linked_ratio 差分 + formula_refs 缺失/错配 + CLI 失败分支 + wire 拒绝链路 + R1 返工整链反例 5 例 + R2 聚合 3 例（含顺序/拆回执不变性）+ R3 gzip 2 例 + /3 多父正例。
- e2e 2（`tests/test_w20_narrative_adoption_e2e.py`，真实子进程）：direct_revenue 全链（stub 传输→真 `run_narrative_consumption_e2e.py`→真 `revenue_forecast.py`×2→真 `revenue_backtest.py` create→真 audit CLI×5；数值前后不变+result_sha256 变化；字节稳定重跑；sentinel/恢复收据）与 direct_growth（biren 正式产物 + unwired 变体 → `not_used_when_provable`）。fixture 全 synthetic。
- 回归：recognition_bridge + DU11 wire/context/consumption + support_diagnostics + reading_support_use 共 106 passed；ruff clean。
- ROOT 探针本地重放（a1edda18 后）：foreign_span→unverifiable+命名诊断；wrong_explicit_source_id→unverifiable+receipt_source_mismatch；two_valid_bindings→used+slot_years[2026,2027]；gzip_bound→rejected resource_limit。
- 独立审查：2026-10-28 初审（S1+S2）14 项 OPEN 修复后终审 PASS（`review/final.*`）；2026-10-29 R1 返工独立复审两轮——三项返工 FIXED + 追加 /3 多父修复，**OPEN_findings=[]，verdict PASS**（`review/rework-review.md`）。

## 关键提交

- `c71b79e2` A 调查冻结（结论：仓内无既有采用观察工具；`run_narrative_consumption_e2e` 止步 linked-input；`research_support_diagnostics` 是输入侧校准观察）
- `65af44b9` B 实现+测试全绿（RED 先行：ModuleNotFoundError 记录于 progress.md）
- `5f88ac3f` C 启动（PWF 更新）
- `8b221153` 初审修复（F1/F2 P0 等 14 项）
- `7716c7da` 交接文档（ROOT 验收受审 HEAD）
- `a1edda18` R1 返工：三项 ROOT 问题修复（RF-R1 整链验证 / RF-R2 聚合 / RF-R3 gzip 有界）
- `e4657377` R1 返工追加：/3 多父按 span 实际父解析（复审 F1）——**tested_code_commit = reviewed_code_commit = e4657377**

## 已知局限（详见报告 limitations 与 README）

- 无执行追踪：观察的是最终产物声明的引用接线，引用缺失不能证明作者推理没用该材料，也不能证明模型内心。
- wired 闭包在畸形（非合同）形状上比引擎略宽（保守方向；真实形状下与引擎 `parameter_uses` 探针一致）。
- `--pretty` 分支无直接单测（独占创建由 `open("x")` 保证，复审探针已验证）。
- `span_dependencies_aggregated` 为每个被绑定 span 发一条 info 诊断（复审裁定不阻塞，可选降噪：仅 >1 路径或存在 invalid 时发）。
- 本工具不替 ROOT 跑真实收费预测；ROOT PWF 的 actual RF adoption 是否关闭仍由 ROOT 用真实材料决定。

## 跨仓阻塞 / ROOT followups

- 无本范围阻塞。ROOT 后续可：（1）用真实脱敏 RF 产物+真实 consumption 回执跑一遍 CLI 做真实材料观察（本卡受"不运行真实预测"限制未做）；（2）决定是否在主线薄接线（如报告管道挂 adoption 段）；（3）考虑 `parameter_uses`/`parameter_formula_refs` 提供批量 upstream 接口供外部观察工具复用（本工具自建了 O(P+E) worklist 闭包）。

## 清理

测试全部在 pytest owned 临时树（sentinel+基线快照+teardown 逐项断言恢复+收据可选 env `W20_PWF_RECEIPTS`）；publication registry 追加后置只读，teardown 先 `chmod` 再删；独立审查探针在仓库外临时目录自清（两轮复审均确认 zero 残留）。每轮全套运行后 `git status --porcelain` 均空；fixtures（tests/fixtures、e2e/fixtures）零改动（diff 空）。
