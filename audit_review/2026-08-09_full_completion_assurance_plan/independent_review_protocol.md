# 独立审查协议

## 1. 目的

独立审查不是阅读实施者总结，而是从冻结基线、代码 diff、命令注册表和原始证据重新证明 FC 是否满足验收。任何 FC 没有独立审查都不能进入 `accepted`。

## 2. 角色隔离

| 角色 | 可以做什么 | 禁止做什么 |
|---|---|---|
| Implementer | 写 RED、实现、运行测试、生成 implementer receipt | 自己批准 FC；修改 reviewer receipt；选择性隐藏失败命令 |
| Reviewer | 在干净 checkout 重放测试、检查 diff/证据、增加只读对抗检查 | 修改产品代码帮其通过；沿用 implementer 工作区；只看摘要 |
| Release owner | 验证 Phase package、授权发布波次、执行/监督回滚 | 绕过 blocked FC；把部分通过改为 pass |
| Closure validator | 机器校验状态、hash、依赖和新鲜度 | 接受自由文本替代字段；自动豁免 mandatory 证据 |

最低独立性：reviewer 必须是不同代理/会话，使用新的干净 checkout 或 worktree，不能读取实现者未纳入 receipt 的临时文件。若环境无法提供独立 reviewer，FC 状态保持 `independent_review`，不能 accepted。

## 3. Reviewer 固定流程

1. 从 current compatibility manifest 获取 base/result triplet，验证三个远端提交存在且 HEAD 精确匹配。
2. 重新计算 plan、scenario registry、command registry、policy、fixture 和 diff hashes。
3. 验证依赖 FC receipts 都已 accepted，并且没有被后续提交失效。
4. 从 CodeGraph 独立查询 callers/callees/impact；比较 receipt 中预期调用边变化。
5. 检查 changed files 全部位于 FC allowlist；检查用户 dirty paths 没有进入 diff。
6. 阅读 RED 测试和首次失败日志，确认测试先前确实因目标缺陷失败，而非语法、fixture 或环境错误。
7. 按 registry 重跑 focused、owner repo、affected sibling、T1 和适用真实层命令；记录 collected/passed/skipped、exit、duration 和 hashes。
8. 重放至少一个负向/故障注入和一个 mutation；确认不是测试本身被跳过。
9. 对有副作用的 FC 对账 event journal、filesystem fingerprint、catalog transaction 和授权预算。
10. 对可回滚 FC 使用同一 request 运行 before→apply→after→rollback→restored trace。
11. 搜索测试专用生产孤岛、root 特判、重复策略、伪计数、硬编码状态、旧 pin、skip/xfail/known-gap。
12. 生成 reviewer receipt；只允许 `accepted`、`changes_required`、`blocked`、`rejected` 四种 verdict。

## 4. Reviewer receipt

```json
{
  "schema_version": "2.0",
  "fc_id": "FC-NNN",
  "implementer_receipt_sha256": "64hex",
  "reviewer_identity": "non-empty-distinct-identity",
  "clean_checkout": true,
  "base_triplet": {"revenue": "40hex", "filing": "40hex", "wiki": "40hex"},
  "result_triplet": {"revenue": "40hex", "filing": "40hex", "wiki": "40hex"},
  "replayed_command_ids": [],
  "scenario_results": [],
  "mutation_results": [],
  "side_effect_reconciliation": {"passed": true},
  "codegraph_reachability": {"passed": true},
  "rollback": {"required": false, "passed": true},
  "unresolved_findings": [],
  "verdict": "accepted",
  "reviewed_at": "ISO-8601"
}
```

validator 必须拒绝 reviewer 与 implementer 身份相同、checkout 不干净、未重放 mandatory 命令、receipt hash 不匹配、场景减少、出现 skip、真实报告过期或 reviewer 修改产品代码的情况。

## 5. 审查深度

- 所有 FC 100% 审查，不抽样。
- 所有 critical mutation 100% 重放；普通 mutation 可以按 registry 固定集合执行，不能由 reviewer 临时缩减。
- T0/T1 结果必须在 result triplet 重跑；T2/T3 可消费满足 freshness 的独立报告，但必须重验 triplet、sample registry 和 report signature/hash。
- T4 必须在授权窗口由 release owner 与 reviewer 双方确认；录像或自然语言说明不能替代 trace/receipt。
- 任何 production caller、legacy caller、hardcode 或 dead-code 结论都必须附 CodeGraph query/result hash和必要的 AST/literal gate 结果。

## 6. Changes required 与重审

- reviewer 发现问题后写入 `unresolved_findings`，给出可复现证据、严重度、受影响场景和恢复条件；不得直接帮忙改代码。
- implementer 修正后必须产生新 result triplet 和新 receipt；旧 reviewer receipt 标记 superseded，不能覆盖。
- 重审必须重新执行所有受变更影响的命令；不能只验证上一次失败的单点。
- 三次不同修正仍无法通过时按 planning-with-files 三击协议升级用户，不得降低门槛。

## 7. Phase 与终局审查

- Phase reviewer 反向验证所有 FC receipts、场景覆盖、未决 finding、依赖和回滚，不接受“每个 FC 看似通过”但组合行为失败。
- Phase 10、11、14、15 必须另选 reviewer；不得由同一 reviewer 连续完成实现级、发布级和终局审查。
- 终局审查从六个用户目标出发重跑 UJ、AUD、EX/DBX、LT/DL、AR、PORT 和 MIG 关键旅程，并验证 legacy/旁路/硬编码关闭，不从“提交数量”推断完成度。

