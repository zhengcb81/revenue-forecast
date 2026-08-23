# ZR-1003 工作单元卡（preflight）— I：lifecycle/safety/RootPolicy shadow assertions

- 领取时间：2026-08-23T04:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-1003`（ZR-1002 closure → ZR-1003）；锁 ZR-1003（owner=zr1003-implementer，nonce 70bc645f…）。
- 依赖：ZR-1002（Reader 先上线，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 I 第三卡——shadow assertions 的 lifecycle/safety/RootPolicy 语义（registry："两动态周期 diff 全解释；active response 不变；rollback 仅关 flag"）。现状缺口（RED）：无综合套件验证断言生命周期（shadow→active→shadow）、prompt-injection safety fail-closed、错误 policy 拒绝激活、两周期确定性、active 响应不变、rollback flag-only 语义。
2. **production entrypoint 是什么？** company-wiki `activation.py`（apply/rollback）+ `assertion_service`（upsert）+ `prompt_injection.py`（record_prompt_injection_review——safety receipt）+ `reader.py`（ReadOnlyCatalogReader）。
3. **RED？** grep zr1003 → 零命中；既有测试（FC-202/203/ZR-1002）未覆盖 safety fail-closed、policy 拒绝、两周期确定性、flag-only 回滚语义。
4. **允许改哪些文件？** company-wiki：新 `tests/contract/test_zr1003_shadow_assertions.py`；revenue：receipts/ZR-1003/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog 写、下载、LLM。
5. **下一单元解锁？** ZR-1004（companies→dayu→Dropbox 小 cohort）。本卡不做：真实 cohort（ZR-1004）、broker cohort（ZR-1006）。

## Acceptance criteria

- **C1 lifecycle**：断言 shadow → apply → active → rollback → shadow 每阶段可见性正确。
- **C2 safety**：未评审 prompt-injection 文档 fail-closed（无 review receipt）；记录 not_detected 后 receipt 完整。
- **C3 RootPolicy**：错误 policy_hash 激活被拒（ActivationError）；正确 policy 激活成功。
- **C4 两动态周期 diff 全解释**：两次 apply→读→rollback 输出 canonical hash 一致（确定性）。
- **C5 active response 不变**：rollback+re-apply 前后 active 行全等（零漂移）。
- **C6 rollback 仅关 flag**：回滚后 visibility_state=shadow（flag 翻转）+ epoch 保留 + 数据完整 + journal rollback 记录。
- **C7 质量门**：company-wiki 回归（activation/ZR-1002）全绿 + revenue 全量零回归（基线 889+106）+ ruff + 独立 reviewer 复放。产品代码零改动。

## 边界

- hermetic：临时 catalog；生产 catalog 零触碰。
- 真实生产 shadow 周期观察由 CA-206 soak 收集。
