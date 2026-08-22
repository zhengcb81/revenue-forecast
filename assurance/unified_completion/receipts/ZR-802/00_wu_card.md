# ZR-802 工作单元卡（preflight）— G 首卡：组合旅程 existing/partial/missing/stale/conflict across roots

- 领取时间：2026-08-23T09:05Z（本地 +0100）
- 唯一入口：`audit_review/README.md` §0；`current_next=ZR-802`，ZR-709 accepted + closure→ZR-802；锁 ZR-802（owner=zr802-implementer）。
- 依赖：ZR-801（machine registry）——按 §7 由 CA-105 唯一实现吸收（`assurance/unified_completion/scenarios/scenario_registry.json`，197 场景已建）；其余前置（各功能 phase 出口）已在 A~F 闭环中达成。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 G 真实 E2E 首卡——把五种文档状态（existing/partial/missing/stale/conflict）×跨根组合成完整用户旅程，从 revenue 入口走三进程链，钉死第二次调用幂等复用与逐阶段调用预算对账。现状缺口：fc1003_uj 仅单发四场景（UJ-01/02/04/07），无 partial/stale 状态、无二次调用幂等、无跨状态预算矩阵。
2. **production entrypoint 是什么？** `scripts/source_preparation.py` 子进程链（revenue → filing-fetch → company-wiki 三进程），fake 多根 fixture catalog（company_raw + dayu_portfolio 双 root）。
3. **RED？** grep zr802/combined journey → 零命中；现有 UJ 测试无第二次调用断言、无 partial artifacts 角色、无 stale 年份拒绝、无跨根 conflict 组合矩阵。
4. **允许改哪些文件？** revenue：新 `tests/test_zr802_combined_journeys.py`；receipts/ZR-802/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 catalog/root 写、下载、LLM。（预期 test-only，与 ZR-709 同型）
5. **下一单元解锁？** ZR-803（chaos/property/mutation）。本卡不做：真实 provider T3 下载（ZR-805）、生产 catalog T2 样本（ZR-806）、Windows/Linux 平台矩阵（ZR-804）。

## Acceptance criteria

- **C1 五状态 × 跨根组合旅程（三进程）**：每状态一次完整 `source_preparation.py` 子进程链（revenue→filing-fetch→company-wiki），fixture catalog 含双 root：
  - existing：FY2024 exact 命中 companies 根 → 复用成功，download/parser/llm=0；
  - partial：文档仅部分 artifact 角色可用 → artifact_read 只含已有角色、producer_events 只含缺失角色的 DAG 闭包（不盲跑全量重算）；
  - missing：两根均无匹配 → 结构化失败、download=0、无伪造 handle；
  - stale：请求 FY2024 但仅有 FY2023 文档 → 不以旧充新，结构化原因且零下载；
  - conflict：跨根同实体同期不同 hash 两份 → fail closed 冲突原因、零下载。
- **C2 第二次调用幂等**：existing/partial 两状态的重复调用返回相同 source 身份（source_id/content hash），昂贵调用仍为 0（ZJ-10 合同复用语义）。
- **C3 阶段 receipt 与调用预算准确**：每个 record 的 reuse_receipt 计数与场景预期精确相等（非 ≤）；八阶段证据链字段（identity/resolution/freshness/acquisition/safety/artifact/semantic/consumer 的可观测投影：capture/safety/artifact_read/producer_events/bundle_status/outcome）逐一存在且与场景一致。

## 边界

- T1 hermetic：临时 roots/catalog，零真实 catalog 写、零网络、零 LLM；
- oracle 来自独立子进程 stdout/stderr + fixture DB 直查（不信任被测函数 summary）；
- 产品代码零改动（若发现真实缺陷按流程 RED 登记另行处理）。
