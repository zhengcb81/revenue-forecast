# FC 工作单元验收登记表

> 这是 71 个 FC 的唯一状态索引。详细行为以 `task_plan.md` 为准，执行纪律以 `implementation_runbook.md` 为准。实施时不得复制出第二张状态表。

## 1. 状态规则

- 合法状态：`pending`、`preflight_locked`、`red_proved`、`implemented`、`focused_green`、`repo_green`、`cross_repo_green`、`real_verified`、`rollback_verified`、`independent_review`、`accepted`、`blocked`、`failed`。
- 除 Phase 0 的计划基线外，当前全部为 `pending`。
- 状态只能由 validator 根据证据推进；自然语言、提交信息、PR 标签或实施者自评不能改变状态。
- 表中前置 FC 未全部 `accepted` 时，不得取得 execution lock。
- “主证据”是最低要求；task plan、scenario registry 或影响分析要求更多证据时取并集，不能取更小集合。

## 2. Phase 0：基线（计划层已完成）

| FC | 状态 | 前置 | Owner | 主证据/出口 |
|---|---|---|---|---|
| FC-000 | completed_plan_baseline | 无 | 三仓 | 三个 40 位 HEAD=upstream、dirty allowlist、CodeGraph health |
| FC-001 | completed_plan_baseline | FC-000 | company-wiki | 生产只读统计、root/catalog fingerprint、现状矛盾清单 |
| FC-002 | completed_plan_baseline | FC-001 | revenue | 已知缺陷→scenario/phase 映射，无未登记 P1/P2 |

## 3. Phase 1：契约与治理

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-101 | independent_review | FC-002 | 三仓 | ownership RED、ADR hashes、N/N-1 兼容表、重复 owner=0（receipt: assurance/fc/FC-101/；honest-implementer，待独立 reviewer） |
| FC-102 | independent_review | FC-101 | revenue | 95 scenario registry 一致性、重复/缺失/矛盾/假 E2E mutation（receipt: assurance/fc/FC-102/；硬覆盖门属 FC-1003） |
| FC-103 | independent_review | FC-101 | revenue | receipt validator 负向全集；旧 25 receipts 不得误通过（receipt: assurance/fc/FC-103/；已实测拒绝 FC-101 的 can_accept） |
| FC-104 | pending | FC-101、102、103 | revenue | current triplet manifest；sibling 漂移 RED；完整组合 GREEN |

## 4. Phase 2：运行时控制平面

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-201 | pending | FC-104 | company-wiki | CTRL-01/02/05；CAS、未知 flag、并发 snapshot、读取失败关闭 |
| FC-202 | pending | FC-201 | company-wiki | resolver flag/epoch/cohort SQL 条件；删除任一条件 mutation 必死 |
| FC-203 | pending | FC-202 | company-wiki | CTRL-03/04；preview/apply/rollback、重复/中断/陈旧 hash |
| FC-204 | pending | FC-203；用户写授权 | company-wiki | 16 active assertion 副本演练、T4 最小 cohort、响应级 rollback |
| FC-205 | pending | FC-204 | company-wiki | production caller reachability、CTRL 全集、双控制面 forbidden=0 |

## 5. Phase 3：RootPolicy 与扫描解耦

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-301 | pending | FC-205 | company-wiki | RootPolicy 2.x schema、1.x doctor、未知/可写外部 root fail closed |
| FC-302 | pending | FC-301 | company-wiki | 三 adapter production caller>=1；scanner root-specific branch 新增=0 |
| FC-303 | pending | FC-302 | company-wiki | v1/v2 frozen corpus shadow parity、差异 ledger、EX-08 mutation |
| FC-304 | pending | FC-303 | company-wiki | future_lake 配置-only T1；产品 Python diff=0 |
| FC-305 | pending | FC-304 | company-wiki | 两轮 shadow diff 解释完毕、真实根 fingerprint 不变、fallback 可用 |

## 6. Phase 4：Catalog 与 provenance 迁移

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-401 | pending | FC-305 | company-wiki | MIG-01/02/03/07；副本 dry-run/resume/idempotency/资源上界 |
| FC-402 | pending | FC-401 | company-wiki | SAFE-01~04、MIG-05；零猜测、四分桶守恒 |
| FC-403 | pending | FC-402 | company-wiki | proposal/approval/activation 分权；伪 receipt/policy hash mutation |
| FC-404 | pending | FC-403 | company-wiki | root/market/kind coverage ledger；输入=全部分桶之和 |
| FC-405 | pending | FC-404 | company-wiki | MIG-02/04/06/07/08；灾难恢复和 catalog integrity |

## 7. Phase 5：Dropbox 闭环

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-501 | pending | FC-205、301、405 | company-wiki/filing | DBX-02~06；只读 RootPolicy、sidecar、containment；第二 allowlist=0 |
| FC-502 | pending | FC-501 | company-wiki | registry→adapter→admission→assertion production trace；Dropbox 写=0 |
| FC-503 | pending | FC-502 | company-wiki | 真实只读候选分桶；中国平安等不可证明样本保持 fail closed |
| FC-504 | pending | FC-503；必要时用户样本授权 | company-wiki | >=2 Dropbox-only 新鲜样本；其他根同 hash=0；绝对路径不泄露 |
| FC-505 | pending | FC-504 | 三仓 | EX-03、DBX-01~08、IDX 适用项、external write=0、rollback trace |

## 8. Phase 6：companies/dayu 等价与多根泛化

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-601 | pending | FC-305、405 | company-wiki | CompanyRaw v1/v2 parity、EX-01、canonical writer 不变 |
| FC-602 | pending | FC-601 | company-wiki | >=2 dayu-only、EX-02、HK/US identity、capture failure 原因关闭 |
| FC-603 | pending | FC-602 | company-wiki | EX-04~07、AR-09；扫描顺序 mutation 不影响结果 |
| FC-604 | pending | FC-603、FC-505 | 三仓 | companies/dayu/Dropbox 同请求矩阵；root-specific 业务分支=0 |

## 9. Phase 7：统一 resolver

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-701 | pending | FC-604 | company-wiki | normalized-only production trace；legacy metadata caller=0 |
| FC-702 | pending | FC-701 | company-wiki | SAFE-01~07；别名/市场/前导零；弱匹配 mutation 必死 |
| FC-703 | pending | FC-702 | company-wiki | SQL pushdown、EX-07、OPS-03、p50/p95/内存预算 |
| FC-704 | pending | FC-703 | company-wiki | outcome/journal 对账；伪 download_calls mutation 必死 |
| FC-705 | pending | FC-704 | company-wiki | legacy observer 真实 seam、两个>=24h zero-hit 窗口、可回滚 |

## 10. Phase 8：latest 与下载

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-801 | pending | FC-704 | company-wiki | CloseGap contract；DL-02/03/07/09、LT-10；事务 journal |
| FC-802 | pending | FC-801 | filing-fetch | allow_download 两分支；GAP 不误映射 not_found；不复制策略 |
| FC-803 | pending | FC-802 | filing-fetch | DL-01~10、LT-01~10；只补 gap、第二次 fetch/write=0 |
| FC-804 | pending | FC-803 | company-wiki/filing | DL-08/09、OPS-02；single-flight、崩溃恢复、幂等 |
| FC-805 | pending | FC-804；真实下载授权 | filing-fetch | CN/HK/US T3、bytes/provider hash、首次/二次计数 |

## 11. Phase 9：工件复用

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-901 | pending | FC-405、704 | company-wiki | 7712 artifacts dry-run 分桶、MIG-01/03/05、零删除 |
| FC-902 | pending | FC-901 | company-wiki | SourceBundle production caller>=1、snapshot 一致、unknown role fail closed |
| FC-903 | pending | FC-902 | filing-fetch | N/N-1 bundle contract；unavailable 显式；转发不改决策 |
| FC-904 | pending | FC-903 | revenue | selector production caller；AR-01~09；最小 DAG 重算 |
| FC-905 | pending | FC-904 | 三仓 | journal 权威计数、prompt-injection receipt、hash/version mutation |
| FC-906 | pending | FC-905；必要时生产迁移授权 | 三仓 | 每类真实 bound artifact>=1；T2 artifact_read>0、producer=0 |

## 12. Phase 10：跨进程 E2E

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1001 | pending | FC-505、604、805、906 | revenue | 三根 fixture、corruption/lock/move variants、manifest hash、外写=0 |
| FC-1002 | pending | FC-1001 | revenue | revenue→filing→wiki 三进程 trace；边界 spy；process_count>=3 |
| FC-1003 | pending | FC-1002 | 三仓 | 95 scenario registry 全覆盖；无重复/遗漏/skip/伪绿色 |
| FC-1004 | pending | FC-1003 | 三仓 | PORT-01~03、安装态、Windows 中文/空格、Linux golden trace |
| FC-1005 | pending | FC-1004 | 三仓 | critical mutation kill=100%；chaos/fault injection 全绿 |

## 13. Phase 11：动态审核

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1101 | pending | FC-1005 | 三仓/revenue | current-triplet required gate；T0/T1/quality/architecture 全集 |
| FC-1102 | pending | FC-1101 | revenue + Windows runner | 每日 T2、AUD-01~05/08、只读 fingerprint、隔离 audit output |
| FC-1103 | pending | FC-1101、805 | filing/revenue | 每周 T3、AUD-06、CN/HK/US、首次/二次零下载 |
| FC-1104 | pending | FC-1102、1103 | revenue | dashboard/ledger、freshness/SLO/triplet gate、历史不可覆盖 |
| FC-1105 | pending | FC-1104 | revenue | AUD-01~08 故障注入；每类漏报均让 release 非零退出 |

## 14. Phase 12：代码质量

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1201 | pending | FC-701、1005 | company-wiki | root/source hardcode AST gate=0；EX-08 |
| FC-1202 | pending | FC-1201 | 三仓 | 单一 RootPolicy；重复 allowlist=0；隐式 sibling path=0 |
| FC-1203 | pending | FC-1202 | 三仓 | dead production symbols、依赖环、test-only helper；行为场景无回归 |
| FC-1204 | pending | FC-1203 | 三仓 | coverage/type/complexity ratchet；阈值下降 mutation/CI 必败 |
| FC-1205 | pending | FC-1204 | 三仓 | 统一错误 schema、PORT-01~03、日志脱敏、编码失败关闭 |

## 15. Phase 13：运行质量

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1301 | pending | FC-704、905 | 三仓 | 版本化 reason taxonomy；trace 完整且路径/内容脱敏 |
| FC-1302 | pending | FC-1301 | company-wiki | OPS-01、AUD-05；scan health 阈值和非零退出 |
| FC-1303 | pending | FC-703、1302 | company-wiki | 49GB catalog SLO；p50/p95/p99、内存、锁等待、回归预算 |
| FC-1304 | pending | FC-1303 | company-wiki/filing | OPS-02/03、DL-08/09、MIG-07；容量/并发/恢复 |

## 16. Phase 15：总关闭

| FC | 状态 | 前置 | Owner | 主测试/证据 |
|---|---|---|---|---|
| FC-1501 | pending | Phase 14 R9 | revenue | 所有 FC/scenario/receipt/freshness/triplet 的机器 closure |
| FC-1502 | pending | FC-1501 | 独立 reviewer | CodeGraph 反向审查、旁路/硬编码/skip/人工步骤=0 |
| FC-1503 | pending | FC-1502 | 独立 reviewer + 三仓 | UJ-01~08、三 root-only、CN/HK/US、Windows 真实旅程 |
| FC-1504 | pending | FC-1503 | release owner | 两个>=24h T2、最近7天 T3、rollback/re-activate 演练 |
| FC-1505 | pending | FC-1504 | closure validator | 六目标 evidence map、最终 ledger exit=0、状态更新为 complete |

## 17. 阶段放行规则

Phase 14 的 R0–R9 是发布波次而非 FC，不计入 71 个 FC；每波必须消费前置 Phase release package 并生成独立 release receipt。一个 Phase 只有在本表中其全部 FC=`accepted`、对应 mandatory scenarios 全部通过、`unresolved_findings` 为空且独立 phase review=`pass` 后才能放行。

