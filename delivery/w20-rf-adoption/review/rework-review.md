# W20 R1 返工审查记录（rework-review，2026-10-29）

对应 ROOT 返工单：`company-wiki/docs/plans/du11-source-closure-2026-10-18/review/w20-reception-20261029/RETURN_RF.md`（verdict CHANGES_REQUESTED，受审 HEAD `7716c7da`）。本文件记录返工修复（`a1edda18`）、复审发现及最终修复（`e4657377`）两轮独立审查结论。原 2026-10-28 初审与终审（review/initial.*、review/final.*）保留不覆盖。

## 第一轮：返工复审（2026-10-29，全新独立 agent，复审 a1edda18）

三项 ROOT 返工逐条裁定（全部独立探针实测，探针在 repo 外临时目录自清）：

| 返工项 | 裁定 | 证据摘要 |
|---|---|---|
| RF-R1/P1 整链验证 | FIXED | foreign span（B span+A hash/claim/param）→ unverifiable、cited_by=0、5 条命名诊断；wrong_source_id/错locator/错parser/错claim target/错claim source/错claim material/跨run → 各自命名码；双合法来源互不串线零假诊断；缺hash仍宽松info；命名空间经capture映射（无跨域字符串直比） |
| RF-R2/P2 路径聚合 | FIXED | 同回执两dependency→used、years={2026,2027}、span item恰1条、无"several receipts"；拆回执/倒序并集逐字节一致；invalid路径保留命名诊断不吞valid |
| RF-R3/P2 gzip有界 | FIXED | ==limit通过、=limit+1→resource_limit、20MB炸弹流式<0.01s拒绝、截断/损坏→input_decompress_failed、压缩字节上限仍生效、失败不留半输出 |

新发现：**[P2] F1** —— 返工新引入：span_material parent_sha 只取 `source_ref`/`parent_source_refs[0]`，/3 多父投影（span 实际父在 refs[1]）的合法回执被误判 unverifiable（三条假诊断）。方向保守（不会假 used），但属合同合法路径上的真实误报。另有 [P3] F2（span_dependencies_aggregated 每span一条info，不阻塞）与收尾提醒（handoff 绑定旧 commit）。

**OPEN_findings=[F1]，verdict：CHANGES_REQUESTED**（三项 FIXED，唯 F1 须修）。

测试实测：37 暂时未到——第一轮时 36 passed（8.57s）+ 回归 106 passed（5.54s）+ ruff clean。

## 第二轮：F1 修复复验（2026-10-29，同一独立 agent 复验 e4657377）

修复：span_material 按每个 span 自身 `source_id` 在（source_ref + parent_source_refs）中解析实际父哈希；span item 展示字段同源。新增 RED→GREEN 测试 `test_projected_multi_parent_context_resolves_actual_span_parent`（真实 validate_narrative_response + 真实 consume + 真实 run_forecast，parent_count=2、实际父在 refs[1]）。

复验裁定（独立重放）：F1 **FIXED**（/3 多父正例 used、零 receipt_* 假诊断、展示哈希=实际父；对错误父的拦截未放松）；全部探针无回归（foreign/错source/错locator/错parser/错claim/缺hash/双来源/R2聚合/R3边界逐项复跑一致）；F2 维持不阻塞。语义安全核实：经真实 wire 校验的材料中 span.source_id 必属已声明父（/1 `_span`、/3 `_span_parent` 强制），parent_sha=None 回退仅存在于未校验宽松路径，符合"缺 hash 宽松、不加门禁"。

测试实测：`python -B -m pytest -q --tb=short -p no:cacheprovider tests/test_w20_narrative_adoption_audit.py tests/test_w20_narrative_adoption_e2e.py` → **37 passed（5.81s）**；回归 106 passed（3.44s）；ruff clean；工区 clean、探针自清。

**OPEN_findings=[]，verdict：PASS**

## 最终交付绑定

- implementation/tested/reviewed commit：`e4657377`（返工链：`7716c7da`→`a1edda18` 三项修复→`e4657377` 多父修复）
- 返工改动文件 SHA256（e4657377 时点）：
  - `tools/narrative_adoption_audit/audit.py` = `0329cc7275a6ff8b0cf3b499152973292f17e5d0a359638e569598593507bb43`
  - `tools/narrative_adoption_audit/cli.py` = `e790715c0187d21416c273a9b8456c61f622820ea68b7d4ea457a08029f37141`
  - `tests/test_w20_narrative_adoption_audit.py` = `484d630474ba70e5da2c49618c01059d026205d943ce8c8092854b826e18ab31`
  - `tools/narrative_adoption_audit/README.md`、`tests/test_w20_narrative_adoption_e2e.py` 本轮未改动（仍为 8b221153 时点 SHA，见 handoff.json）
- 新增命名诊断码：`receipt_source_mismatch`、`receipt_span_hash_mismatch`、`receipt_locator_mismatch`、`receipt_parser_mismatch`、`receipt_claim_source_mismatch`、`receipt_claim_material_mismatch`、`receipt_claim_target_mismatch`、`span_material_not_provided`、`input_decompress_failed`（CLI）、`span_dependencies_aggregated`（info）
