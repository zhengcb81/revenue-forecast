# ZR-604 工作单元卡（preflight）— F2：从表格抽取、冲突保存与人工 review（双 assertion + resolution status）

- 领取时间：2026-08-22T02:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-604`，ZR-603 accepted + closure→ZR-604（phase=F_revenue_mining，F2 第四卡）；锁 ZR-604（owner=zr604-implementer）。
- 依赖：ZR-602（✅ basis 契约）、ZR-603（✅ ownership/geography）。Registry 依赖列=ZR-602,ZR-603。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F2 第四卡：**冲突保存与人工 review**——同一事实（definition/period/unit/scenario 相同）的多个参数值来源冲突时（如 Bisha 矿 kt/t 来自年报 vs 三季报），不静默覆盖旧值，而是保存双 assertion（primary/secondary）+ resolution status（accepted/rejected/pending_review/under_review），由人工或下游 review 决定取舍。Mandatory 证据：Bisha kt/t、3Q 状态、锂合计差额等冲突不静默覆盖；双 assertion+resolution status。
2. **production entrypoint 是什么？** `scripts/contracts/document.py::validate_parameters`（semantic_groups 冲突检测扩展）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 冲突静默失败（真实产品缺口）**：semantic_groups（document.py:471-479）检测到同语义键不同值时硬失败 `ForecastInputError("unresolved conflicting parameters for {key}: {ids}")`——没有"双 assertion+resolution status"机制，无法表达"两个来源都可信但值不同，需人工 review"。当前只能二选一（删除/修改参数值）。
4. **允许改哪些文件？** revenue：`scripts/contracts/constants.py`（+2 行 assertion/resolution 词汇）、`scripts/contracts/document.py`（+~15 行 helper + 2 行调用；validate_parameters 复杂度零增量——helper 提取模式复用 ZR-602/603）；新 `tests/test_zr604_conflict_resolution.py`；revenue receipts/ZR-604/**。禁止：改模型公式语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-605（MineYearOperation 输入合同）。本卡不做：表格抽取逻辑（wiki 侧）、会计 ADR 冻结（ZR-610）、冲突解决决策（人工 review 产物）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-603 accepted（closure.next=ZR-604）。
- [x] 现状事实（RED 探针）：document.py:471-479 semantic_groups 硬失败无双 assertion 机制——冲突无法表达 resolution status。

## Acceptance criteria
- **C1 双 assertion+resolution status**（杀 G1）：参数可携带 `assertion_status` ∈ {primary, secondary}（default primary 当缺省）和 `resolution_status` ∈ {accepted, rejected, pending_review, under_review}（default 无——无 resolution_status = 无冲突管理）。当 semantic_groups 检测到冲突（同 definition/period/unit/scenario 不同值）：若**所有**冲突参数均携带 `resolution_status` 且**至多一个**为 "accepted" → 允许共存（冲突已解决）；否则保持原行为硬失败（不静默覆盖，backward compatible）。
- **C2 词汇验证**：`assertion_status` 非法值 → ForecastInputError；`resolution_status` 非法值 → ForecastInputError。
- 质量门：全量无回归；ruff/ratchet 绿。

## 判定矩阵

| 场景 | 期望 |
|---|---|
| 同语义键不同值，无 resolution_status | ForecastInputError（backward compat） |
| 同语义键不同值，均带 resolution_status + 恰一个 accepted | 允许（冲突已解决） |
| 同语义键不同值，均带 resolution_status + 两个 accepted | ForecastInputError（多 accepted） |
| 同语义键不同值，部分带 resolution_status | ForecastInputError（不完全解决） |
| 同语义键同值 | 通过（无冲突） |
| assertion_status 非法 | ForecastInputError |
| resolution_status 非法 | ForecastInputError |
| 缺 assertion_status/resolution_status | 通过（additive，零破坏） |
