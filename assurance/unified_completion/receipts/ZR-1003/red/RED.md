# RED.md — ZR-1003 lifecycle/safety/RootPolicy shadow assertions（阶段 I 第三卡）

## 探针（全部在当前机器实跑）

- **G1 无生命周期综合验证**：grep zr1003 → 零命中；既有测试（FC-202 snapshot 语义、FC-203 事务、ZR-1002 golden/rollback）未覆盖：断言全生命周期可见性（shadow→active→shadow）、prompt-injection safety fail-closed（未评审阻断）、错误 policy 激活拒绝、两动态周期确定性（diff 全解释）、active 响应跨 rollback 不变、rollback flag-only 语义（epoch/数据/journal 保留）。

## 既有能力（不重复建设）

- company-wiki `activation.py`（apply/rollback + journal）、`prompt_injection.py`（record_prompt_injection_review——sqlite3.Connection 语义，caller 拥有 commit）、`reader.py`、`assertion_service`。

## 结论

G1 为真实缺口（`still_missing`）；实施 = company-wiki `tests/contract/test_zr1003_shadow_assertions.py`（7 tests），产品零改动。
