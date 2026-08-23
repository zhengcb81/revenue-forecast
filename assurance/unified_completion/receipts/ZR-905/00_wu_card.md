# ZR-905 工作单元卡（preflight）— H：审核机制自测试（八类 AUD2 失败模式全让 release 红）

- 领取时间：2026-08-22T23:50Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-905`（ZR-904 closure → ZR-905）；锁 ZR-905（owner=zr905-implementer，nonce bcb17234…）。
- 依赖：ZR-904（SLI/release gate，accepted ✅）、CA-107。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H 第四卡——**审核机制自测试**（scenario_matrix §9 八类 AUD2 场景：AUD2-01~08 全部必须让 release 红）。现状缺口（RED）：无单一套件把八类失败模式注入现有机制（ZR-902/903/904 的 ledger/freshness/release gate/sli）并断言全红——审核机制本身未经受检。
2. **production entrypoint 是什么？** 组合现有机制：ZR-902/903 的 freshness_status/release_gate（daily/weekly ledger）+ ZR-904 的 compute_sli/release_decision/validate_report/publish_all_pending + uc 的 manifest-verify（AUD2-07）+ strict_state 的 ReviewerGate（AUD2-08）。
3. **RED？** grep audit_self_test/AUD2 → 零命中；无八类失败注入套件。
4. **允许改哪些文件？** revenue：新 `tests/test_zr905_audit_self_test.py`；receipts/ZR-905/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog/root 写、下载、LLM、真实 Task Scheduler 注册、修改 manifest/state 真实文件（AUD2-07 用临时副本验证 manifest-verify 检测漂移）。
5. **下一单元解锁？** ZR-901（PR 门，需 ZR-801 处置）或 ZR-906（最终 ratchet，依赖 ZR-104 已闭）。本卡不做：真实 soak（CA-206）、PR 门（ZR-901）、最终 ratchet（ZR-906）。

## Acceptance criteria

- **C1 八类 AUD2 失败注入全红**（每类一个测试）：
  - AUD2-01 schedule 未运行：无 ledger → freshness missing + release gate blocked（脚本存在不算动态运行）；
  - AUD2-02 报告过期：stale ledger → blocked（旧绿不沿用）；
  - AUD2-03 wrapper 吞非零/半报告：pending 半报告（缺字段/hash 断裂）→ 发布拒绝 + release 红；非零退出传播；
  - AUD2-04 伪造 download/parser/LLM=0：catalog 伪造计数（downloads>0/reuse=0）→ SLI 红；
  - AUD2-05 缺样本：样本缺失 → blocked（不自动换样本——ZR-806 语义引用）；
  - AUD2-06 指标恶化：consumer_ready<0.9 → SLI 红（即使 unit 绿）；
  - AUD2-07 plan/registry hash 变化：manifest 漂移（临时副本注入）→ uc manifest-verify 非零；
  - AUD2-08 reviewer=implementer：strict_state 对同 reviewer 的 accepted 拒绝（ReviewerGateError）。
- **C2 恢复幂等**：修复失败条件后（补 ledger/换新报告/恢复计数）→ release 转绿（恢复幂等）。
- **C3 质量门**：全量回归零回退（基线 851 passed + 106 subtests）、ruff clean、ratchet 绿、skill-sync MATCH、独立 reviewer 复放。产品代码零改动。

## 边界

- hermetic：临时 ledger/report/catalog；AUD2-07 不触碰真实 manifest（subprocess 对临时 manifest 副本或 mock）；AUD2-08 直接 import strict_state 验证逻辑（不执行真实 state-update）。
- 测试全部 tmp_path/临时目录。
