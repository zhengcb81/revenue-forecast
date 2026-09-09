# 2026-08-09 旧计划完成度审计

> 这是对旧计划状态声明的当前证据复核，不修改旧计划。  
> 审查原则：代码存在 ≠ 生产接线；测试 ID 出现 ≠ 场景运行；旧 triplet accepted ≠ 当前功能仍通过；fixture 通过 ≠ 真实用户旅程通过。

## 1. 完成度分类

| 状态 | 含义 | 旧任务如何处理 |
|---|---|---|
| `retain_candidate_asset` | 机制/代码资产有历史可信证据或当前实现，但尚未在current triplet独立重放 | 不重写；先做兼容回归，通过后走already-satisfied |
| `revalidate_current` | 旧 triplet 曾通过，但证据陈旧、索引/配置/数据/调用链已变 | 保留实现，补当前重放后再决定 |
| `reopen_scope_gap` | accepted 的实际范围小于旧 phase/用户目标，或当前真实反例推翻 | 迁移为新版原子任务并先写RED |
| `implemented_not_operated` | runner/工具已实现，但调度、权限、告警、soak或生产接线未完成 | 保留工具，迁移运营接线和自然时间门 |
| `pending_migrate` | 旧计划明确未完成 | 移入新版，不在旧文件继续推进 |
| `superseded` | 原方案会固化不完整架构或与新目标冲突 | 取消旧执行入口，由新版替代 |

## 2. 总体判断

- 旧计划完成了大量有价值的基础资产：版本化 contract、activation snapshot/CAS、adapter骨架、严格身份、gap/download事务、artifact handle/bundle、三进程fixture、receipt/mutation/quality工具和若干真实canary。
- 但它没有达到“这三个仓库已经完整实现用户设计功能”的最终目标。最关键的差距不是最后五张表单，而是证据系统把若干局部机制误提升为全链完成。
- 旧计划当前最诚实的状态应是：**实现资产大部分完成；最终业务闭环和持续保证未完成；原 Phase 14 R9 不应继续删除旧路径；Phase 15 应由新版 closure 取代。**

## 3. Phase 逐项复核

| 旧 Phase | 旧声明 | 当前最小可信完成 | 反例/缺口 | 当前分类 | 新计划处置 |
|---|---|---|---|---|---|
| 0 基线 | completed | 当时的历史事实、缺陷和95需求清单已形成 | triplet、CodeGraph和生产数据均已漂移 | `retain_candidate_asset` | 旧证据封存；新版重新基线 |
| 1 契约/治理 | FC-101～104 accepted | contract/command/scenario/receipt工具骨架存在 | scenario registry 127/127证据路径缺失；receipt总门接结构校验；current triplet陈旧 | `reopen_scope_gap` | 升级 Evidence Registry/Closure 2.0/current-triplet fan-out |
| 2 runtime控制 | FC-201～205 accepted | activation snapshot、CAS、apply/rollback和flag约束已实现并在Phase14实操 | 中间态曾导致T4全missing；当前生产快照/epoch仍需独立核验；控制面不能替代目标架构 | `revalidate_current` | 保留控制面；做 current state/rollback/atomic bundle复验 |
| 3 RootPolicy/Adapter/Scanner | FC-301～305 accepted | 2.x schema、adapter和shadow parity资产存在 | production仍有v1 loader/kind模型；scanner仍shadow/legacy；CodeGraph陈旧；R9未完成 | `reopen_scope_gap` | 演进到RootPolicy 3.0并真正接生产reader/scanner |
| 4 Catalog/provenance migration | FC-401～405 accepted | dry-run、分桶、恢复和审查机制可复用 | 生产旧artifact 7718最初0 bindable；9506无active location；shadow binding生产读者/真源不统一 | `reopen_scope_gap` | 唯一validator/view→生产bundle→重新分桶→条件迁移 |
| 5 Dropbox filing | FC-501～505 complete | sidecar识别、目录扫描、内容去重和resolver层支持存在 | 真实replay选中companies canonical；四canary非排他；星环fail closed；filing/revenue Dropbox-only未证明 | `reopen_scope_gap` | 物理排他Dropbox-only三进程；配置false↔true；broker另建一等类型 |
| 6 companies/dayu/multi-root | FC-601～604 complete | company/dayu adapter parity，wiki resolver真实dayu-only样本和隔离三根一致性有证据 | dayu v2 master identity gap；filing默认companies containment；全consumer跨root未证明 | `reopen_scope_gap` | eligible location+policy snapshot贯穿三仓；真实dayu-only用户旅程 |
| 7 normalized resolver | FC-701～705 complete | strict identity、SQL pushdown、envelope/trace和legacy observer资产存在 | resolve/query仍可构造写型Store；全局canonical与request-eligible未分；raw lock错分 | `reopen_scope_gap` | 真CatalogReader、位置选择、稳定错误和分阶段receipt |
| 8 latest/download | FC-801～805 complete | gap/authorization/staging/single-flight和CN/HK/US真实provider测试资产存在 | local exact与freshness未正交；newer_revision未进filing actionable；current已授权不重下等场景证据不完整 | `reopen_scope_gap` | Freshness/GapPlan 2.0；授权哈希；missing/revision最小补齐 |
| 9 artifacts/source bundle | FC-901～906 complete | v2 producer stamp、ArtifactHandle、SourceBundle、selector、少量真实canary可复用 | 旧artifact大部不可证明；artifact_bindings无生产读者；producer INSERT≠真实调用；安全review和bundle状态分裂；研报全空 | `reopen_scope_gap` | source lifecycle+producer attempt ledger+ProcessingDemand+按需迁移 |
| 10 E2E | FC-1001～1005 complete | IsolatedLake、真实进程链、部分mutation/chaos骨架可保留 | 主三进程只覆盖companies exact；95 coverage仅ID marker/receipt；127 tier evidence全缺；真实partial/stale/broker/mine未覆盖 | `reopen_scope_gap` | 保留runner，替换为machine result registry和真实journey矩阵 |
| 11 动态审核 | FC-1101～1105 complete | Daily/Weekly脚本、report/release/fault工具已实现 | workflow无schedule；production callers=0；连续运行/告警/freshness未证明；manifest陈旧 | `implemented_not_operated` | 调度、凭据、告警、报告原子性、自然时间soak |
| 12 代码质量 | FC-1201～1205 complete | ruff/mypy/coverage/complexity ratchet和若干清理有价值 | FC-1201明确延迟v1/root hardcode；CC仍极高；部分阈值只是冻结债务；文档/skill/schema仍漂移 | `reopen_scope_gap` | 保留ratchet，逐热点拆分；hardcode=0；单一schema/docs真源 |
| 13 SLO/容量 | FC-1301～1304 complete | taxonomy、scan增量健康和SLO工具存在 | latest实际重复测exact；RSS非resolver；49GB/27M声明与实际probe不一致；调度未持续 | `reopen_scope_gap` | 修probe语义、真实子进程/查询类别/锁并发、趋势门 |
| 14 发布波次 | R0～R8 evidence/applied，R9 blocked | 部分生产flag已apply并做过rollback；R6/R7已有真实历史证据 | 波次不在71 FC状态机；R2观察不足；R9删除会在新缺陷关闭前移除回退；其他程序仍在推进 | `superseded`（R9）+`revalidate_current`（现态） | 立即冻结旧R9；生产状态只读盘点；新版最后阶段再删legacy |
| 15 总关闭 | FC-1501～1505 pending | closure gate/ledger早期原型正在形成 | gate漏filing/缺receipt/Phase14/场景/调度/当前triplet，当前只报5 pending | `pending_migrate` | 由新版Evidence Closure、独立审计、用户旅程、soak和ledger替代 |

## 4. 71 FC 数量不能直接解释为 66/71 真完成

- 注册表有71行，其中3个只是计划基线、63行状态文本含accepted、5行pending。
- 20行status不是声明的合法枚举，而是混入日期/reviewer/Phase结论的自由文本；closure用substring判定。
- FC-1301直接依赖自己；Phase14 R0～R9不计入71行。
- accepted reviewer receipts包含大量low/info/pre-existing finding；部分finding本应在phase exit前关闭但未建立强制后继。
- 当前closure只验证找到的implementer receipt；缺receipt静默、filing目录遗漏、reviewer receipt不验、revision不选、Phase14不验。

因此“66/71”只能描述旧Markdown登记进度，不能作为用户目标完成比例。

## 5. 可直接保留、避免重复重构的资产

1. RuntimePolicySnapshot/ActivationSnapshot/CAS/rollback transaction。
2. adapter接口、normalized metadata、strict identity和provider normalization。
3. GapPlan/CloseGap、download authorization、staging、single-flight和真实CN/HK/US adapter测试。
4. ArtifactHandle/SourceBundle/ROLE_DEPENDENCIES/consumer selector的基本合同。
5. IsolatedLake和三subprocess测试支架。
6. receipt schema、mutation/quality工具的基本实现。
7. mypy/coverage/complexity基线和部分CI步骤。
8. Daily T2、Weekly T3、SLO/scan-health脚本的可复用计算部分。

保留的前提是：不得继承其旧完成状态；必须进入current-triplet回归，并修正已知证据/生产接线缺口。

## 6. 必须暂停或禁止直接继续的旧动作

- 暂停 R9 删除v1 scanner、visibility bridge、backfill/portfolio工具；新读模型、RootPolicy、真实三root consumer和新版E2E未完成前，删除会失去安全回退。
- 不得用现有 FC-1501 gate 将FC-150x逐个改accepted；必须先升级gate本身。
- 不得把95场景的marker coverage转换为pass；先产出127个tier级可验证结果。
- 不得把旧FC-505作为Dropbox-only通过证据；它明确选择companies路径。
- 不得把脚本存在作为动态审核已部署；必须有scheduler和新鲜报告。
- 不得为追求legacy binding率放宽source SHA、安全、identity或producer validator。

## 7. 旧计划关闭建议

旧目录在新版计划获得owner批准后可标为：

`closed_superseded_incomplete`，而不是 `complete`。

关闭包必须包含：

- 本文逐Phase映射；
- 71 FC→新版work unit的迁移表；
- R0～R9当前生产状态快照；
- FC-1501～1505替代关系；
- 所有旧receipt/commit/hash只读保留；
- 明确禁止从旧task_plan继续领取R9/FC-150x。

旧文件不删除、不重写历史；其owner只需加入一份指向新版manifest的terminal closure notice。
