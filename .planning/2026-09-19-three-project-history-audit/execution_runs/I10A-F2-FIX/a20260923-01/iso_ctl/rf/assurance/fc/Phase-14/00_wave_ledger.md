# Phase 14 发布波次账本 — R0~R9 状态（2026-08-13）

> 每波协议：副本演练 → preview → 批准 → 最小 cohort → T2/T4 → 观察 → 扩大；失败立即回滚。
> 用户 standing 授权（2026-08-12「全部授权」）；FC-204/FC-906-c 生产写入先例。

| 波次 | 状态 | 证据 |
|---|---|---|
| R0 governance/triplet gate | **✓ COMPLETE** | CI manifest checkout（FC-1101）+ 三仓 ratchet/type/coverage/receipt 门全部 live（FC-1204/1205 receipt 记录）；无回退需求 |
| R1 runtime control plane | **✓ APPLIED（2026-08-13，与 R8 组合翻转）** | 生产 snapshot `57569ea6`：bridge OFF + v2_persist_assertions + resolve_shadow + resolve_active 全链。T4 6/6 reused_exact（紫金×2/美团/Apple 两种形式/NVIDIA）；回滚演练通过（→`2757db65` 桥恢复→re-apply `57569ea6` 确定性）。**中间态教训**：bridge OFF + resolve_active OFF 对谁都不可见（v1 无桥、v2 未激活）——T4 抓到、立即回滚、组合翻转成功 |
| R2 v2 scanner dry shadow | **✓ APPLIED（观察期开始）** | `v2_scan_shadow=true` 生产 apply（snapshot `93ddf67e`）；回滚演练通过（apply→rollback `c7bd17f1`→re-apply `93ddf67e` 确定性恢复）；计划要求两周期 shadow diff 全解释后进 R3 |
| R3 companies cohort | **✓ EVIDENCE（组合翻转后生产验证）** | cohort 16 assertions 在生产 v2 reader 下活跃；T4 6/6 + 等价性 28/28 覆盖 |
| R4 dayu-only cohort | **✓ EVIDENCE** | EX-02 真实样本（FC-602）+ 等价性采样覆盖 dayu 断言文档 |
| R5 Dropbox-only cohort | **✓ EVIDENCE** | 4 真实 canary（FC-504）+ DBX 全绿 + T2 roots fingerprint 一致 |
| R6 SourceBundle/artifacts | **✓ EVIDENCE（已实际生产）** | 241 bound artifacts + producer_events 244 + T2 真实消费（FC-906-d；北方华创 artifact_read>0）——bundle 链已生产运行 |
| R7 latest/close-gap | **✓ EVIDENCE（已实际生产）** | T3 真实 CN/HK/US 下载 + 第二次零下载（FC-805）；gap 编排 live（FC-802/803） |
| R8 legacy bridge off | **✓ APPLIED（2026-08-13）** | 进入条件 v2 达成（计划修正案，findings 64/65）：canary drill 4/4 零 hit + **桥关闭等价性 28/28**（scripts/bridge_off_equivalence.py，含 entity-gate 尾随句点归一化修复 82bd40e）+ 观察窗口已过。与 R1 组合翻转（中间态被 T4 抓出并回滚）。R9 前需再观察一周期（cron 每日续跑） |
| R9 v1/legacy 删除 | **BLOCKED（R8 后再观察一周期）** | 时间门：24h 观察窗口（cron 每日续跑：observer 现在应记录零 hit 窗口 + T2 + shadow diff）。v1 scanner 7 分支 + backfill_v2/portfolio_promoter = R9 backlog（FC-1201 frozen ratchet 承重） |

## R2 观察协议（运行中）

- 每 ≥24h：`python scripts/legacy_observer.py --period N ... --canary-matrix`（WU-1500 时间门持续）
- 每周期：`shadow_parity`（v1/v2 diff 全解释，FC-303 migration ledger）+ T2 runner（新增量健康语义，FC-1302）
- R2 → R3 进入条件：两周期 diff 全解释

## 本会话可执行边界

R1/R3-R5/R8/R9 被时间门（≥24h 观察窗口）阻塞——计划明示的停线条件，非缺陷。R6/R7 生产证据已存在（FC-906-d/FC-805 receipts）。观察期结束后的继续执行按本账本协议。
