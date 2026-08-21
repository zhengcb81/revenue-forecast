# ZR-610 工作单元卡（preflight）— F2：会计 ADR 冻结（无产品代码）

- 领取时间：2026-08-22T03:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-610`，ZR-604 accepted + closure→ZR-610（phase=F_revenue_mining）；锁 ZR-610（owner=zr610-implementer）。
- 依赖：ZR-604（✅ 冲突解决）。Registry 依赖列=ZR-604。

## 领取前五问

1. **推进哪个用户目标/痛点？** 冻结通用矿业数据、单位、ownership/consolidation/internal-sales ADR——将 F2 前四卡（ZR-601~604）的设计决策固化为会计 ADR，明确逐矿贡献是模型估计（非披露事实），为 ZR-605~611 的实现提供冻结的会计框架。
2. **production entrypoint 是什么？** 无产品代码——产出为 ADR 文档（`assurance/unified_completion/receipts/ZR-610/adr_mining_accounting.md`）。
3. **哪个 current-triplet 行为是 RED？** 无产品代码改动——RED = ADR 文档未冻结 + 独立会计 reviewer 未接受。
4. **允许改哪些文件？** 无产品代码改动。仅：revenue receipts/ZR-610/**（ADR 文档 + receipt）。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-605（MineYearOperation 输入合同——依赖 ZR-604+ZR-610）。本卡不做：输入合同实现（ZR-605）、商业量价层（ZR-606）、内部交易（ZR-607）。

## Acceptance criteria
- **C1 ADR 文档冻结**（杀 RED）：ADR 文档覆盖 8 条会计决策（逐矿贡献=模型估计、resource≠reserve、basis 元数据、ownership timeline、单位一致性、冲突解决、地区层级、ADR 边界）。
- **C2 独立会计 reviewer accepted**：独立会计 reviewer 审查 ADR 的会计合理性与通用矿业实务一致性，verdict=accepted。
- **C3 逐矿贡献=模型估计声明**：ADR 明确声明逐矿贡献是模型估计（非披露事实），模型输出不携带"disclosed"标记。

## 判定矩阵

| 场景 | 期望 |
|---|---|
| ADR 覆盖 8 条决策 | 通过 |
| 独立会计 reviewer accepted | 通过 |
| 逐矿贡献=模型估计声明存在 | 通过 |
| ADR 缺少某条决策 | changes_required |
| 会计 reviewer changes_required | changes_required |
