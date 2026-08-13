# CA-101 RED 证据

> 规则：RED 从公开/生产入口触发、先证明当前行为确实失败、由独立 oracle 验证。

## RED-A：状态机无迁移约束——pending→accepted 直接跳跃合法

**证据（2026-08-14 实测）**：`uc.cli state-update --unit X --status accepted` 对任意
单位有效（只要状态在 12 枚举内），不校验当前状态是否 pending、迁移是否单向合法。
CA-001~004 的实际 closure 流程依赖人工纪律而非机器门——`pending → accepted` 的一步
跳跃在机器上不会被拒绝。

## RED-B：任何调用者可写 accepted——无 reviewer 角色门

`state-update --status accepted` 不要求 reviewer 身份与 implementer 分离、不校验
reviewer receipt 存在；同一单位两个 reviewer 并发写仅靠通用 CAS 竞争（输者报错但
不区分"角色冲突"）。

## RED-C：DAG 无环校验缺失

`uc.dag` 只解析依赖边，不验环；`next_units` 对含环图静默返回（依赖永远不满足，
无明确 cycle 报告）。

## RED-D：无 per-unit 锁

locks 目录用于 control-page/资源锁，单位状态写入没有单位级单 writer 锁；并发
state-update 仅靠 state.json 的 CAS 冲突，没有单位锁语义（TTL/owner/renew）。

## 新工具对照（本卡实现）

`uc.strict_state`：状态枚举（CA registry 12 态 ∪ runbook 15 态）、单向合法迁移表、
依赖门（非 pending→blocked/superseded 的迁移要求依赖满足）、per-unit 锁、reviewer
身份字段（accepted 必须带 reviewer 且 ≠ implementer）、DAG 环检测；
`state-render` 生成只读 Markdown 视图；property tests 随机生成非法图/非法迁移全部
拒绝。
