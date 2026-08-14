# ZR-101 工作单元卡（preflight）— 版本化跨仓八阶段 taxonomy

- 领取时间：2026-08-14T05:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-101`（阶段 C 首卡）；units.ZR-004.status=accepted + closure.next=ZR-101。
- 依赖：ZR-002（accepted ✅）。Registry 依赖列=ZR-002。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 契约基座：三仓各自报告"阶段/原因/事件"但无统一版本化 schema。本卡在 company-wiki 建立唯一真源：identity→consumer 八阶段 schema、原因→阶段归属、事件 schema；unknown reason/stage fail closed；N/N-1 contract tests。
2. **production entrypoint 是什么？** wiki `src/company_wiki/source_catalog/observability.py`（既有 reason taxonomy v1.1，~100 code，validate_reason fail-closed）→ 本卡在其上做 additive 升级为 2.0 阶段化 taxonomy，不破坏 1.1。
3. **哪个 current-triplet 行为是 RED？** 无八阶段 schema；REASONS 为扁平 dict 无阶段归属；无 stage event 校验；无 N/N-1 合同测试。这些缺失即 RED。
4. **允许改哪些文件？** wiki `src/company_wiki/source_catalog/observability.py`（additive）+ 新测试 `tests/unit/test_stage_taxonomy*.py`（或 contract）；revenue 侧 receipts/ZR-101/** 与 state.json。禁止：删除/重命名任何既有 1.1 code、改 catalog 写入路径、改其它产品模块。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-102~105（依赖 ZR-101）。本卡不重接任何生产调用方（事件发出方接线归 ZR-304/102）；不改 filing/revenue 的消费实现（跨仓消费接线归后续卡）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-004 accepted（机器状态 2026-08-14T05:2xZ；closure.next=ZR-101；phase=C_read_only_and_contracts）。
- [x] triplet 冻结：revenue `739d5aa4c05fd4cd58b6115e9726f5395542e36b`（ZR-004 closure，领取时重读）；filing `83c638e…`；wiki `ef125ed…`。
- [x] dirty allowlist：wiki 4 项既有环境 dirty（.claude/settings.local.json D、llm_cost_log.csv M、.coverage/coverage.json ?）——本卡不改这些文件。
- [x] 八阶段定义取自冻结 annex scenario_matrix §28：`identity/resolution/freshness/acquisition/safety/artifact/semantic/consumer`。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品）+ revenue（assurance 控制面收 receipt）。
- **Current-state drift verdict**：`still_missing`——无阶段化跨仓 taxonomy。
- **Acceptance criteria**：TAXONOMY_VERSION 2.0；八阶段枚举按 annex 顺序；每个注册 reason 归属≥1 阶段（无孤儿 code）；unknown reason/stage fail closed；StageEvent schema+校验；N/N-1 合同测试（N 拒绝未知、N-1 消费者优雅 fail closed、1.1 code 全为 2.0 子集）；wiki unit+contract 套件绿。
- **Stop conditions / handoff**：删除/改名 1.1 code、写 catalog、动其它生产模块 → 立即停止。
