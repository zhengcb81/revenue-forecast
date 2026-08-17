# ZR-303 工作单元卡（preflight）— 统一 safety/identity/artifact/semantic readiness 决策图

- 领取时间：2026-08-17T20:45Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-303`；units.ZR-302.status=accepted + closure.next=ZR-303；`uc next` 解锁列表含 ZR-303。
- 依赖：ZR-301（readiness 求值器 ✅）、ZR-302（prompt-injection guard ✅）。Registry 依赖列=ZR-301,ZR-302。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 统一 readiness 决策。ZR-301 已提供逐源八阶段 shadow 求值（source_lifecycle.evaluate_source_readiness），ZR-302 已提供 safety receipt 缓存生命周期（prompt_injection_guard.evaluate_review）。但二者尚未合成**一个 machine decision graph**：consumer 需要"这个 source 对我是 ready 吗？卡在哪？下一步做什么？"。本卡把 identity/artifact/semantic（来自 ZR-301 求值）+ safety（来自 ZR-302 guard）合成单一决策图，输出每 blocker 的 next action，并保证状态不互相矛盾。
2. **production entrypoint 是什么？** 本卡 shadow 侧：新增 `readiness_graph.py`（纯函数/只读，输入 reader + 参数；输出 `ReadinessDecision`）。不接生产 CLI（后续卡接线）；不写 catalog。
3. **哪个 current-triplet 行为是 RED？** 没有单一决策图：ZR-301 的 safety 阶段只看"有 receipt"，ZR-302 的 guard 单独判缓存态，二者未合成；consumer 无法从一处得到完整 ready 判断 + blocker + next action。
4. **允许改哪些文件？** company-wiki 新增 `src/company_wiki/source_catalog/readiness_graph.py`（新模块，复杂度≤10）+ `tests/unit/test_readiness_graph.py`；revenue 侧 receipts/ZR-303/** 与 state.json。禁止：写 catalog、改 ZR-301/302 模块语义、接生产入口、改 reader/锁/schema。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-304（producer attempt/artifact journal）与 ZR-307（filing 分阶段 envelope）。本卡不接线生产入口；不做 artifact validator 归一（ZR-304）；不产生/失效 receipt 本身（ZR-302 已做）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-301/302 accepted（机器状态；closure.next=ZR-303）。
- [x] triplet 冻结（领取时重读）：revenue `26ec973…`（ZR-302 receipt commit 后）、filing `0e5d209…`、wiki `cbdb054…`。
- [x] 现状代码事实：`source_lifecycle.py` 提供 evaluate_source_readiness（八阶段 verdict+blocker+next_action，unknown 不满足）；`prompt_injection_guard.py` 提供 evaluate_review（hit/ignored/expired/tampered/absent → not_reviewed 不伪绿）；无合成决策图。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品新模块）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——无合成 readiness 决策图。
- **Acceptance criteria**：
  - `READINESS_GRAPH_SCHEMA_VERSION`/`SCHEMA`：版本化。
  - `evaluate_readiness(reader, source_id, *, policy_hash, source_sha256, now, ttl_seconds, requirements)`：合成 ZR-301 八阶段求值 + ZR-302 safety guard 缓存判定 → `ReadinessDecision{ready, blockers: [(stage, reason, next_action)], safety_cache_state, requirements}`：
    - safety 阶段改用 ZR-302 guard 结果：hit → satisfied；ignored/expired/tampered/absent → blocker（next action = 重新扫描/审查，绝不伪绿）；
    - 其余七阶段沿用 ZR-301 求值；unknown 一律不算 satisfied；
    - ready = 所有 required 阶段 satisfied；每个 blocker 带 next action；
    - 状态不互相矛盾：同一 source 的同一阶段在同一输入下必得同一 verdict（纯函数、无隐藏状态）。
  - 决策图无死路：每个 unsatisfied/unknown blocker 都有 next_action（映射表完备性测试）。
  - shadow 只读：只经 reader.fetchone/fetchall；无写路径断言。
  - hermetic 测试：safety guard 五态与 graph 的映射（hit→satisfied；ignored/expired/tampered/absent→blocker）、八阶段 blocker+next_action 完备性、unknown 不满足、确定性（同输入同输出）、requirements 驱动 ready、复杂度≤10。
  - wiki unit/contract 全绿；独立 reviewer 复放。
- **Stop conditions / handoff**：写 catalog、改 ZR-301/302 语义、接生产入口 → 立即停止。

## Annex：safety 阶段映射（来自 ZR-302 guard）

| guard cache_state | graph safety verdict | next action |
|---|---|---|
| hit | satisfied | — |
| ignored | unsatisfied | 用新 ruleset 重新扫描并记录 receipt |
| expired | unsatisfied | 重新审查（TTL 已过） |
| tampered | unsatisfied | 核对源字节，重新扫描/审查 |
| absent | unknown（无 receipt）→ blocker | 执行 prompt-injection 扫描（ZR-302 生成路径） |
