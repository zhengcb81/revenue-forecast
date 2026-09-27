# RED.md — CA-306 旧计划 terminal closure 与唯一入口切换（阶段 J 终局卡）

## 探针（全部在当前机器实跑）

- **G1 无 CA-306 验收套件**：glob tests/**/*ca306* → 零命中。
- **G2 无 terminal closure 验收**：6 个旧计划目录均无 TERMINAL_NOTICE（未关闭）；无"notice 契约 + 历史不可变 + disposition 完整 + FC-150x→accepted CA + 唯一入口"一体验收。
- **G3 真实现状（只读确认）**：legacy_disposition 71 FC rows 全有 successors、10 waves、5 closure items（FC-1501~1505 → CA-107~109/301~306）；README 唯一控制面在位；state current_phase=J_final_verification。

## 既有能力（不重复建设）

- legacy_disposition（parse/validate/verify：71 FC + 10 waves + 精确计数 + successor 全定义 + 无环）；state.json（accepted 真源）；CA-305 六问题 ledger（全部证据单元 accepted）；audit_review/README.md（唯一入口 + current_next/phase 镜像）。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_ca306_terminal_closure.py`（8 tests：C1 notice 契约；C2 历史不可变；C3 disposition 完整；C4 FC-150x→accepted CA（R9 via CA-304）+ 全部 mandatory accepted；C5 唯一入口），产品零改动、旧计划目录零触碰。
