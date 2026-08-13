# Phase 14 发布波次账本 — R0~R9 状态（2026-08-13）

> 每波协议：副本演练 → preview → 批准 → 最小 cohort → T2/T4 → 观察 → 扩大；失败立即回滚。
> 用户 standing 授权（2026-08-12「全部授权」）；FC-204/FC-906-c 生产写入先例。

| 波次 | 状态 | 证据 |
|---|---|---|
| R0 governance/triplet gate | **✓ COMPLETE** | CI manifest checkout（FC-1101）+ 三仓 ratchet/type/coverage/receipt 门全部 live（FC-1204/1205 receipt 记录）；无回退需求 |
| R1 runtime control plane | **BLOCKED（政策验证器拒绝，按设计）** | `runtime-policy apply` 被 CAS 门拒绝：`v2_resolve_active requires v2_resolve_shadow enabled; legacy_bridge_enabled conflicts with v2_resolve_active`。bridge 关闭被 WU-1500 时间门门控（period 3/4 hits=6，需 2 个连续 ≥24h 零 hit）→ R1 依赖 R8 前序（与 FC-204 决策一致：全局翻转会使 13,806 legacy-only 文档不可解析） |
| R2 v2 scanner dry shadow | **✓ APPLIED（观察期开始）** | `v2_scan_shadow=true` 生产 apply（snapshot `93ddf67e`）；回滚演练通过（apply→rollback `c7bd17f1`→re-apply `93ddf67e` 确定性恢复）；计划要求两周期 shadow diff 全解释后进 R3 |
| R3 companies cohort | BLOCKED by R2 观察期 | cohort canary-2026-08-10 已注册（FC-204，16 assertions：Apple/NVIDIA/比亚迪等） |
| R4 dayu-only cohort | BLOCKED by R3 | EX-02 真实样本已证（FC-602 replay） |
| R5 Dropbox-only cohort | BLOCKED by R4 | 4 真实 canary 已注册（FC-504）；DBX 全绿 |
| R6 SourceBundle/artifacts | **✓ EVIDENCE（已实际生产）** | 241 bound artifacts + producer_events 244 + T2 真实消费（FC-906-d；北方华创 artifact_read>0）——bundle 链已生产运行 |
| R7 latest/close-gap | **✓ EVIDENCE（已实际生产）** | T3 真实 CN/HK/US 下载 + 第二次零下载（FC-805）；gap 编排 live（FC-802/803） |
| R8 legacy bridge off | **BLOCKED（WU-1500 时间门）** | period 3 hits=6、period 4 hits=6、窗口 <24h——close gate 诚实关闭（2026-08-13T03:42Z 评估）。条件：2 个连续 ≥24h 零 hit 窗口 |
| R9 v1/legacy 删除 | BLOCKED by R8 | v1 scanner 7 分支 + backfill_v2/portfolio_promoter = R9 backlog（FC-1201 frozen ratchet 承重） |

## R2 观察协议（运行中）

- 每 ≥24h：`python scripts/legacy_observer.py --period N ... --canary-matrix`（WU-1500 时间门持续）
- 每周期：`shadow_parity`（v1/v2 diff 全解释，FC-303 migration ledger）+ T2 runner（新增量健康语义，FC-1302）
- R2 → R3 进入条件：两周期 diff 全解释

## 本会话可执行边界

R1/R3-R5/R8/R9 被时间门（≥24h 观察窗口）阻塞——计划明示的停线条件，非缺陷。R6/R7 生产证据已存在（FC-906-d/FC-805 receipts）。观察期结束后的继续执行按本账本协议。
