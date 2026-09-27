# RED.md — CA-305 六问题 machine closure ledger（阶段 J 第五卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-305 验收套件**：glob tests/**/*ca305* → 零命中。
- **G2 无六问题 ledger 验收**：六问题定义在 project_goal_and_pain_points.md §6；无"六问题逐项 → 证据单元（state accepted + receipts）→ 场景测试 → triplet 绑定 → reviewer 存在 → 每问独立 pass（非聚合百分比）"一体验收。
- **G3 真实现状（只读确认）**：六问题章节明确（6 条编号问题）；证据单元（CA-301~304/ZR-902~907 等）均已 accepted 且 11/12 receipts 在位；ZR-904 首轮 changes_required 但有 13_delta_review_receipt（delta accepted）。

## 既有能力（不重复建设）

- project_goal_and_pain_points.md §6（六问题冻结源）；state.json（accepted 状态真源）；receipts/**（11/12/13 receipts）；CA-301 receipt 全量重算已证（189/189 MATCH）；closure receipts 含 result_triplet 40-hex。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca305_six_problems.py`（7 tests：C1 六问题枚举；C2 证据单元 closed + receipts；C3 场景测试；C4 triplet 绑定 + state 确定性；C5 reviewer 存在（含 delta）；C6 每问独立 pass 非聚合），产品零改动。
