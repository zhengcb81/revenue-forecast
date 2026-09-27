# ZR-706 工作单元卡（preflight）— F1：FC-904 artifact selector 契约补全钉死

- 领取时间：2026-08-21T00:20Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-706`，ZR-705 accepted + closure→ZR-706（phase=F_revenue_mining）；锁 ZR-706（owner=zr706-implementer）。
- 依赖：ZR-701（✅）、ZR-705（✅）。Registry 依赖列=ZR-001。关联：FC-904（legacy_transition_matrix：revenue artifact selector 可留，ZR-306/706）。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F1 第六卡：**FC-904 revenue artifact selector 契约补全**。select_artifact_roles（company_wiki_source.py）实现 DAG 最小性（artifact_read/producer_events），test_fc904_artifact_selection.py 已覆盖 AR-01~08 + bundle 边界，但 **read/produced 互斥、自定义 roles 子集、consumer_analysis provenance 匹配即 read** 三处契约缺口无测试。
2. **production entrypoint 是什么？** `company_wiki_source.select_artifact_roles(handle, roles=..., expected_provenance=...)`（source_preparation.prepare_source 调用）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 read/produced 互斥无断言**：同一 role 不应同时出现在 artifact_read 与 producer_events（语义矛盾）。
   - **G2 自定义 roles 子集无测试**：roles 参数传子集（如仅 ("normalized",)）时 DAG closure 是否限于子集内。
   - **G3 provenance 匹配即 read 无测试**：AR-06 只测 mismatch 拒绝；expected_provenance 匹配时 consumer_analysis 应 read（无测试）。
4. **允许改哪些文件？** revenue：新测试 `tests/test_zr706_selector_contract.py`（补全钉死）；若探针发现真实缺口则修 company_wiki_source.py；revenue receipts/ZR-706/**。禁止：改 selector 契约语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-710（publication 事务 REV-09）。本卡不做：publication 事务/故障注入（ZR-710）、F2 矿业层。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-705 accepted（closure.next=ZR-706）。
- [x] triplet 冻结：revenue（ZR-705 closure 提交后）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：test_fc904 覆盖 AR-01~08 + no-bundle + malformed + prepare_source 集成；互斥/子集/provenance 匹配三处无测试。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（selector 契约补全测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3（预期 test-only；探针若发现缺口则修）。
- **Acceptance criteria**：
  - **C1 互斥（杀 G1）**：多种 bundle 形状（full valid / summary missing / normalized missing / tampered）下 artifact_read ∩ producer_events == ∅。
  - **C2 自定义 roles 子集（杀 G2）**：roles=("normalized",) 且 normalized 不可用 → produced 只含子集内 closure（不盲算子集外 role）；roles=("normalized", "summary") 且 summary missing → produced 含 summary（+ 其 DAG 依赖中在子集内的）。
  - **C3 provenance 匹配即 read（杀 G3）**：consumer_analysis artifact 的 provenance 与 expected_provenance 匹配 → consumer_analysis read（produced 不含它）；mismatch → 不 read + produced（AR-06 既有）。
  - 质量门：revenue tests/ 全量无回归（含 test_fc904）；ruff clean；ratchet 绿。
- **Stop conditions / handoff**：改 selector 契约语义、真实 catalog 写、下载、LLM → 立即停止。

## Annex：selector 契约判定矩阵

| 场景 | 期望 |
|---|---|
| 任何 bundle 形状 | artifact_read ∩ producer_events == ∅ |
| roles=("normalized",) 且 normalized 不可用 | produced = ("normalized",) 子集内 |
| roles=("normalized","summary") 且 summary missing | produced 含 summary（子集内 DAG） |
| consumer_analysis provenance 匹配 | read 含 consumer_analysis，produced 不含 |
| consumer_analysis provenance mismatch | read 不含，produced 含（AR-06 既有） |
