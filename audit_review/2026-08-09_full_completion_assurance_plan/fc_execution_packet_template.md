# FC 执行包模板

> 每个 FC 开始前复制一份到实施期证据目录并填写。空字段、`TBD`、`N/A`（没有合同解释）都会被 validator 拒绝。本文件仅定义未来实施格式，本轮不创建任何真实执行包。

## 1. 目录结构

```text
assurance/fc/FC-NNN/
  00_preflight.json
  01_codegraph_before.json
  02_red_test.json
  03_change_contract.json
  04_focused_test.json
  05_repo_test.json
  06_cross_repo_test.json
  07_real_tier_test.json
  08_fault_mutation.json
  09_side_effect_reconciliation.json
  10_rollback.json
  11_implementer_receipt.json
  12_reviewer_receipt.json
  13_closure.json
```

不适用的层级仍需保留文件，并写入版本化 `not_applicable_reason_code` 和合同依据；不得删除文件表示不适用。

## 2. 00_preflight 必填清单

- [ ] `fc_id` 与 `work_unit_registry.md` 完全一致。
- [ ] base triplet 三个完整 40 位 hash 与 upstream 一致。
- [ ] plan/scenario/command/policy hashes 已固定。
- [ ] 所有 dependency receipts 为 accepted 且未被新提交失效。
- [ ] 三仓 dirty paths 已列出；用户文件明确排除。
- [ ] execution lock 唯一，锁包含 FC、owner、开始时间和超时。
- [ ] allowed files/forbidden paths/max diff budget 已由 reviewer 预批。
- [ ] 生产读写、真实下载、外部网络是否需要授权已明确；授权缺失则不开始。
- [ ] CodeGraph index healthy；若代码自基线变化，先刷新/确认 watcher 后再做影响分析。

## 3. 02_red_test 必填清单

- [ ] 测试从用户可见错误或契约错误出发，不只测试新 helper。
- [ ] 保存精确 command ID、test node IDs、退出码、失败断言和输出 hash。
- [ ] 失败原因正是目标缺陷；环境/语法/fixture 失败不算 RED。
- [ ] 当前错误行为没有被写成期望值。
- [ ] 至少包含一个 happy path、一个拒绝/失败 path 和一个回归 mutation oracle。
- [ ] 若测试意外绿色，先做 production reachability 检查；不得直接跳到实现。

## 4. 03_change_contract 必填清单

| 字段 | 要求 |
|---|---|
| Intended behavior delta | 一句话可观察行为，不描述“重构一下” |
| Allowed symbols/files | 由 CodeGraph 影响分析和 FC owner 确认 |
| Forbidden changes | 数据删除、扩大写权限、隐藏兼容、测试降级等 |
| Contract/schema delta | 版本、兼容窗口、消费者、迁移和 rollback |
| Expected call-edge delta | 哪些 production edge 必须新增，哪些 legacy edge 必须消失 |
| Data migration | none/dry-run/shadow/authorized apply；不能模糊 |
| Side-effect budget | discover/fetch/write/parser/LLM/artifact read 的上下界 |
| Diff budget | 文件数、代码行或模块边界；超出先拆 FC |

## 5. 测试阶梯

每一阶只有在上一阶证据合法时才能运行：

1. Focused：目标和直接回归测试。
2. Owner repo full：冻结 registry 的完整命令族。
3. Affected siblings：所有受契约/调用影响的 sibling 回归。
4. T1 current triplet：对应场景和通用 guards。
5. T2：真实 catalog/roots 只读，证据写隔离目录。
6. T3：真实 provider + 临时 wiki；需授权。
7. T4：生产最小 cohort；需当次 change-window 授权。
8. Fault/mutation：错误注入、关键 mutation、timeout/partial evidence。
9. Idempotency/rollback：相同请求重跑、before/apply/after/rollback/restored。

任一级失败，FC 立即转 `failed` 或 `blocked`；不得继续跑更高层寻找绿色结果覆盖失败。

## 6. 副作用对账模板

| 副作用 | 预算 | 实际 | 权威来源 | Verdict |
|---|---:|---:|---|---|
| provider discover | 场景定义 | 待执行 | event journal | pending |
| provider fetch | 场景定义 | 待执行 | provider trace | pending |
| canonical companies write | 场景定义 | 待执行 | filesystem journal | pending |
| dayu write | 0 | 待执行 | before/after fingerprint | pending |
| Dropbox write | 0 | 待执行 | before/after fingerprint | pending |
| parser | 场景定义 | 待执行 | producer trace | pending |
| LLM by role | 场景定义 | 待执行 | cost/event ledger | pending |
| artifact read | 场景定义 | 待执行 | bundle trace | pending |
| catalog mutations | FC 定义 | 待执行 | transaction journal | pending |

任何无法从权威日志确认的计数为 `unknown`，而 `unknown` 必须失败，不能按 0 处理。

## 7. Closure 条件

- [ ] Implementer receipt schema/hash 合法。
- [ ] Reviewer 使用干净 checkout 并完成协议全部步骤。
- [ ] changed files 未超 allowlist/diff budget。
- [ ] 所有 required commands 运行且 collected 数不下降。
- [ ] mandatory scenarios 在声明层级全部通过，无 skip/xfail。
- [ ] 负向、mutation、副作用和 rollback 证据通过。
- [ ] CodeGraph production reachability 达到预期、legacy edge 按预期下降。
- [ ] 没有新增 P1/P2 finding；低级 finding 有 owner、期限且不影响本 FC 验收。
- [ ] closure validator exit=0 并把 registry 状态推进到 accepted。

