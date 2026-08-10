# 三仓完全完成、真实复用与持续保证实施计划

> Plan ID：`FCAP-2026-08-09-r2`
>
> 状态：`plan_complete_ready_for_review`；所有实施 Phase 仍为 `pending`
>
> 基线：revenue `3ce9cc4d3ea91b15aad42eff1f55b72a44834dd7`；filing `c9799b722a97376f9717bcfacfa0685135dcbd15`；wiki `109a1a6a77d7f4b37f849207fbd9e5d8caf2bc07`
>
> 配套文档：[architecture_target.md](architecture_target.md)、[scenario_matrix.md](scenario_matrix.md)、[implementation_runbook.md](implementation_runbook.md)、[execution_matrix.md](execution_matrix.md)、[work_unit_registry.md](work_unit_registry.md)、[fc_execution_packet_template.md](fc_execution_packet_template.md)、[command_registry_plan.md](command_registry_plan.md)、[independent_review_protocol.md](independent_review_protocol.md)、[dynamic_assurance_plan.md](dynamic_assurance_plan.md)、[code_quality_plan.md](code_quality_plan.md)、[legacy_plan_disposition.md](legacy_plan_disposition.md)、[findings.md](findings.md)、[progress.md](progress.md)、[plan_self_audit.md](plan_self_audit.md)
>
> 本轮只制定计划；未授权任何产品代码、配置、数据库、真实根或 CI 实施。

## 1. 最终目标与可证明标准

| 用户目标 | 最终状态 | 必须同时满足的机器证据 |
|---|---|---|
| 1. 重构完全成功 | 唯一生产链使用 RootPolicy + adapter + normalized assertions；v1 双轨退役 | CodeGraph 生产可达性、legacy forbidden-pattern=0、真实 cutover/rollback、两周期 legacy hit=0 |
| 2. Dropbox 功能层面接入 | Dropbox-only filing 可 exact/latest 复用，安全边界有效 | EX-03、DBX-01~08、真实 T2 样本、external write=0 |
| 3. 功能和目标全部实现 | exact、missing/download、latest、artifact、identity、provenance 全闭环 | scenario matrix 所有 mandatory ID 通过，无 skip/known gap/pending |
| 4. 完善动态审核 | PR、nightly T2、weekly T3、release T4 均可自动阻断 | 新鲜度 gate、历史报告、失败演练、current triplet manifest |
| 5. 更多真实 E2E | fixture、真实代码、真实根、真实 provider、Windows/Linux 均有证据 | T0~T4 分层回执；Dropbox/dayu-only/companies-only 样本 |
| 6. 全面代码质量提升 | 单一策略源、无 root 特判、无伪证据、受控复杂度 | architecture gate、coverage/mutation/type/complexity ratchet、dead-code/reachability gate |

整体只能在所有 mandatory FC 为 `accepted`、最终 triplet 与 upstream 一致、真实证据未过期、closure ledger 可机器验证时标记 `complete`。完成计划不等于数学上不存在未知缺陷，但必须消除本计划枚举的已知缺陷并建立持续发现回归的机制。

## 2. 冻结的系统不变量

1. `companies` 是所有新下载文件的唯一 canonical write target。
2. companies、dayu、Dropbox 和未来根都可以是只读复用来源；“能 index”与“可 filing reuse”由 RootPolicy + normalized evidence 决定。
3. 复用优先于下载；未授权不得 discover/fetch；latest 只下载 gap 中获批候选。
4. 同一 content/document 跨根共享 identity、assertion 和 artifacts，不因路径复制处理结果。
5. 不猜 provenance；不删除旧 assertion/artifact/真实文件；迁移可逆。
6. filing-fetch 保持薄编排，revenue 不重做 catalog/resolver，company-wiki 不做收入预测。
7. 测试名、回执或文档不能替代生产调用者和真实用户链证据。

## 3. 依赖顺序

```text
Phase 0 baseline
  -> Phase 1 contracts/governance
  -> Phase 2 runtime control plane
  -> Phase 3 adapter/scanner unification
  -> Phase 4 catalog migration
  -> Phase 5 Dropbox + Phase 6 companies/dayu equivalence
  -> Phase 7 normalized resolver
  -> Phase 8 latest/download + Phase 9 artifacts
  -> Phase 10 full E2E
  -> Phase 11 dynamic assurance + Phase 12 cleanup + Phase 13 SLO
  -> Phase 14 progressive release
  -> Phase 15 independent closure
```

弱模型默认严格串行。只有 runbook 明确允许且 changed-file allowlist 不相交时才可并行。

## 4. 全局门禁

每个 Phase 的 exit gate 必须包含：

- 所有本 Phase FC receipt 为合法 JSON 且独立 review=`accepted`；
- `work_unit_registry.md` 的状态由 validator 推进，所有依赖 FC 已 accepted，且 execution lock 已释放；
- 所有命令来自冻结 command registry，collected 数未下降、无 unexpected skip/xfail；
- focused、全仓、跨仓当前 triplet 测试全部绿色；
- 相关 scenario IDs 无 skip/xfail/known-gap 绿化；
- 至少一个关键 mutation 被测试杀死；
- CodeGraph 显示新构件有 production caller，待退役构件 caller 按计划下降；
- production 相关 Phase 有副本演练、root fingerprint、真实只读 canary 和 rollback；
- 未触碰用户 dirty paths；无未说明 untracked 文件；
- plan/progress/findings 与实际状态一致。

## Phase 0（稳定基线与已知缺陷冻结）— 状态：completed（仅计划基线）

### FC-000：稳定 triplet

- 已确认三个仓库 HEAD 与 upstream 一致；company-wiki 的 `llm_cost_log.csv` 为用户既有 dirty file。
- CodeGraph 可用；结构基线分别为 revenue 114、filing 17、wiki 434 个已索引 Python 文件。
- 后续任何 FC 开始时必须重新验证，发生漂移则更新 plan version，不能沿用旧回执。

### FC-001：生产只读事实

- 三根已 index；Dropbox 只有一个活动半年报候选且没有 assertion。
- production artifacts 7712，source-bound=0。
- active v2 assertions=16，但运行时 flag/epoch 回执与 resolver 实际行为不一致。
- scan health 包含 155 completed_with_errors、15 interrupted。

### FC-002：缺陷到场景映射

- 已将 Dropbox、latest、artifact、控制平面、动态审核、硬编码和 Windows 编码问题映射到 `scenario_matrix.md`。
- Exit：findings 1~9、目标架构和 runbook 已形成；不代表任何产品缺陷已经修复。

### 历史计划状态归并（计划治理完成）

- [x] 三仓所有根级、review/audit、docs/plans、recovery 和 archive 计划已登记到 `legacy_plan_disposition.md`。
- [x] 历史 scoped completion 保留；审查完成与产品完成分开记账。
- [x] 仍必要的旧待办已映射到 r2 FC；不再需要的项目已 cancelled/superseded；条件性工作已降为 P2/P3。
- [x] 旧计划不再产生新 receipt 或恢复为独立执行入口。

## Phase 1（契约冻结与验收治理重建）— 状态：completed（FC-101~104 accepted 2026-08-10）

### FC-101：目标 ADR 与 owner contract

- Owner：三仓；文档先行。
- 目标文件：各仓 ADR/contract 文档，禁止产品逻辑修改。
- 固定 `RootPolicySnapshot`、`NormalizedFilingMetadata`、`ResolutionEnvelope`、`AcquisitionTrace`、`SourceBundle`、`ArtifactHandle`、`ActivationSnapshot` 的 owner、版本和兼容窗口。
- RED：contract ownership test 应因重复字段/第二策略源失败。
- 验收：同一字段只有一个 owner；N/N-1 兼容和删除期限明确；三仓文档 hash 写入 triplet manifest。

### FC-102：scenario registry 成为唯一测试语义源

- Owner：revenue；三仓引用相同 scenario IDs。
- 新增机器可读 registry，与 `scenario_matrix.md` 的 95 个 mandatory scenario 一一对应。
- 测试收集门验证：每个 mandatory ID 的全部声明层级均有对应测试；包含 T1 的 ID 至少由一个真实跨进程测试覆盖；T2/T3/T4 分别登记且不得互相替代。
- 禁止同一 ID 被两个测试以矛盾期望实现；禁止测试名声称 E2E 而 process_count<3。

### FC-103：receipt/closure validator

- Owner：revenue quality tools。
- 实现 runbook schema 2.0 validator、all-mandatory-WU closure gate、HEAD/plan/policy/command hash 校验。
- RED mutations：短 hash、占位 policy hash、pending review、丢失 closure file、陈旧 triplet、skip 场景、伪 reviewer、未来时间均必须失败。
- 实施 `independent_review_protocol.md` 的 implementer/reviewer 双 receipt 与身份隔离；实施者不能写 accepted。
- 验收：旧 25 份不完整 receipt 不得被新总门误判 accepted；closure ledger 只能由 validator 生成。

### FC-104：current compatibility manifest

- Owner：revenue。
- manifest 固定三仓远端、commit、contract versions、Python/platform matrix、config schema、scenario registry hash。
- CI 和本地 runner 只能消费 manifest，不在 workflow 内散落 commit。
- 按 `command_registry_plan.md` 只读盘点并冻结三仓真实命令；记录 collected 基线、tier、timeout、写入/网络预算和 registry hash。
- 验收：任一 sibling 漂移先红；更新 manifest 后完整 triplet 绿色才可合入。

### Phase 1 exit gate

- FC-101~104 全部 accepted；旧 release manifest 明确标记 superseded，不删除历史。
- receipt validator mutation 100% killed；后续所有 FC 强制使用新 schema。

## Phase 2（真实运行时控制平面、epoch 与回滚）— 状态：completed（FC-201~205 accepted 2026-08-10）

### FC-201：持久化 RuntimePolicySnapshot

- Owner：company-wiki。
- Targets：`flags.py`、`policy.py`、`config.py`、`models.py`、`store.py`、CLI；允许新增单一 runtime policy 模块。
- 将 v2 scan/persist/resolve/bundle/legacy bridge、current epoch、active cohorts 变为持久化版本化 snapshot；禁止 WU 脚本硬编码 dict。
- 配置变更采用 compare-and-swap + policy hash；读取失败 fail closed。
- Tests：CTRL-01/02/05、未知 flag、依赖顺序、并发 snapshot。

### FC-202：resolver 强制 ActivationSnapshot

- Owner：company-wiki。
- Targets：`resolver.py`、`visibility_bridge.py`、`assertion_service.py`。
- request 起点固定 policy hash/epoch/cohort；SQL 查询必须同时过滤 decision、visibility、epoch、cohort。
- flag=false 时数据库 active row 绝不可见；legacy bridge 仅在 snapshot 明确允许时调用。
- Mutation：去掉 epoch 或 flag 条件必须被 CTRL-01/02 杀死。

### FC-203：真实 activation/rollback 事务

- Owner：company-wiki。
- 提供 preview/apply/rollback CLI；只能在 catalog transaction 中切 cohort/epoch 和 policy snapshot；生成 immutable receipt。
- rollback 以同一 request 的 before/after response trace 证明有效，不接受“dict 变了”。
- Tests：CTRL-03/04、重复 apply/rollback、进程中断、错误 cohort、陈旧 policy hash。

### FC-204：处置现有 16 active assertion

- 生产写入，必须另行取得用户 change-window 授权。
- 先 snapshot + integrity/row/hash baseline；在副本上将现状映射到合法 cohort/epoch。
- 独立 reviewer 决定：纳入正式 canary cohort，或回退 shadow；不得直接删除。
- 验收：回执、数据库状态、resolver 响应和 flag 全部一致；当前 WU-905 矛盾关闭。

### FC-205：控制面 adversarial gate

- CodeGraph 验证 production resolver/scan/bundle 均读取 RuntimePolicySnapshot。
- 禁止 production callers 直接读取硬编码 flags 或绕过 snapshot。
- T1 全部 CTRL 场景 + T4 最小 cohort rollback。

### Phase 2 exit gate

- CTRL-01~05 全绿；真实 rollback 可重复；没有“数据 active、flag inactive、响应已变化”的不一致。
- 未通过前禁止新增 active assertion、Dropbox cohort 或 artifact cohort。

## Phase 3（RootPolicy 2.x、Adapter Registry 与 Scanner 统一）— 状态：completed（FC-301~305 accepted 2026-08-10）

### FC-301：RootPolicy 2.x 配置迁移

- Owner：company-wiki；filing 只消费 policy snapshot hash。
- Targets：`config/source_catalog.yaml`、`config.py`、`models.py`、`policy.py`、`admission.py`。
- 为三根显式配置 adapter、profile、read_only、reusable kinds、allowed kinds、cohort、write target。
- 配置加载必须拒绝外部 root 可写、未知 adapter/profile、宽化路由和重复 root。
- 先新增 1.x->2.x loader/doctor，不立即改变生产扫描行为。

### FC-302：生产 AdapterRegistry 接线

- Owner：company-wiki。
- Targets：`adapters/registry.py`、`interface.py`、`company_raw.py`、`dayu.py`、`sidecar.py`、`scanner.py`。
- scanner 只能按 effective route 调 adapter；Sidecar/CompanyRaw/DayuAdapter 必须出现 production caller。
- adapter 输出统一 candidate/normalized metadata/evidence；scanner 不写 root-specific metadata container。
- CodeGraph gate：`SidecarFilingAdapter` production caller>=1；root-specific branch 新增=0。

### FC-303：v2 scanner shadow parity

- 移除 `v2 scanner unavailable` stub，先只在内存/副本 shadow。
- 对冻结 corpus 比较 v1/v2：document/source hash、kind、identity、location、exclusion reason、性能。
- 每个可解释差异登记 migration rule；不可解释差异阻断。
- Mutation：将 future root 回落 legacy path 必须被 EX-08 杀死。

### FC-304：未知未来 root 配置-only 证明

- 使用 temp `future_lake` + sidecar adapter，只改配置，不编辑 scanner/resolver。
- EX-08 从配置加载到 revenue consumer 全链通过。
- Architecture gate 扫描 production Python 中 root IDs/kinds/Dropbox 路径特判。

### FC-305：scanner cutover 与 v1 fallback

- 在副本和 T1 全绿后按 cohort 开启 v2 scanner；v1 保持只读 fallback。
- 两轮 shadow diff=0 后才允许 production dry shadow；真实根 before/after fingerprint 必须一致。

### Phase 3 exit gate

- 新 root 配置-only 成功；三 adapter 都有生产调用者；scanner root-specific metadata 写入归零。
- v1/v2 shadow 差异全部解释；无真实根写入。

## Phase 4（Catalog schema、历史 assertion 与 provenance 迁移）— 状态：completed（FC-401~405 accepted 2026-08-10）

### FC-401：可恢复 migration engine

- Owner：company-wiki。
- Targets：`migration.py`、`backfill_v2.py`、`store.py`、migration journal/CLI。
- 支持 dry-run、resume key、batch、cancel、idempotency、copy validation、rollback journal。
- 49GB catalog 必须在副本上完成全流程；禁止一次长事务和 Python 全表载入。

### FC-402：无猜测 assertion backfill

- 每份 filing 分为 `eligible`、`needs_review`、`unprovable`、`retired/conflict`。
- 字段只能来自 sidecar、provider metadata、正式披露内容或强 identity snapshot；文件名只能作 evidence hint，不能直接 capture-ready。
- SAFE-01~04、现有中国平安/星环科技失败样本必须保持 fail closed，直到证据补齐。

### FC-403：review/remediation workflow

- proposal 与 approval 分离；reviewer 必须看到 source bytes hash、字段证据、diff 和 policy hash。
- approval 工具只生成 shadow assertion；activation 由 Phase 2 控制面单独处理。
- 禁止源码中硬编码 `user-approved-*`、短 receipt id 或占位 policy hash。

### FC-404：migration quality ledger

- 按 root/market/kind 记录 coverage、missing fields、conflicts、duplicate location sets。
- production apply 前要求 companies/dayu/Dropbox 各自可解释分桶总和=输入总数。
- retired 文档不因迁移恢复；真实文件不改。

### FC-405：副本灾难演练

- 在副本模拟中断、磁盘不足、陈旧 schema、重复 assertion、错误 epoch、rollback 后重跑。
- 证明 restore point、journal 和 catalog hashes；未做全库 integrity 的大表必须有替代 hash/采样策略和风险说明。

### Phase 4 exit gate

- 副本迁移可中断恢复且幂等；所有输入进入明确分桶；零猜测 mutation 被杀死。
- production apply 仍需单独授权，不能因 Phase 4 代码绿色自动执行。

## Phase 5（Dropbox 功能级接入）— 状态：completed（FC-501~505 accepted 2026-08-10；4 真实 canary、resolver-MISSING 缺口关闭、exit gate 通过）

### FC-501：Dropbox RootPolicy 与 sidecar contract

- 明确 Dropbox 只读、可 filing reuse、允许 kinds、sidecar schema、symlink/junction policy、canonical priority。
- filing-fetch 删除/降级本地 root allowlist，只验证 policy snapshot 和 canonical path containment。
- DBX-02~06 先红后绿。

### FC-502：SidecarAdapter 生产扫描

- Dropbox candidate 必须通过 registry -> adapter -> admission -> normalized assertion；不得借用 `acquisition/dayu_meta`。
- 同目录普通研究文档仍可 index，但不能成为 filing。
- 重扫不重写真实 sidecar，不修改 Dropbox bytes/mtime。

### FC-503：Dropbox 历史候选治理

- 对真实 root 只读盘点 filings、缺失字段、重复到 companies 的 location set。
- 当前中国平安样本保持 unprovable，除非 reviewer 从正式 PDF/来源补齐所有字段。
- 不删除 companies 副本制造 Dropbox-only 证明。

### FC-504：真实 Dropbox-only canary 样本

- 从现有唯一文件选出至少 2 份强 provenance filing；若不存在，停在 blocked 并向用户申请一个专用真实 canary 文件/sidecar。
- 样本必须在 companies/dayu 无相同 document/content hash。
- 注册 hashed sample ID、期望 identity/period/provider，不泄露绝对路径。

### FC-505：Dropbox 全链 E2E

- EX-03、DBX-01~08 从 revenue source_preparation 启动，经过 filing-fetch/company-wiki 到 artifact selection。
- exact hit：provider/download/parser/LLM/external writes 全 0。
- rollback 同一请求恢复旧响应；root fingerprint 不变。

### Phase 5 exit gate

- 不再存在“配置有 Dropbox 但 resolver MISSING”绿测；原 known-gap 测试必须改为正确 RED/GREEN。
- 至少 2 个新鲜 Dropbox-only T2 样本通过；否则不能称 production Dropbox complete。

## Phase 6（companies/dayu adapter 等价迁移与多根泛化）— 状态：completed（FC-601~604 accepted 2026-08-11）

### FC-601：CompanyRawAdapter 等价

- 在固定 corpus 比较 v1/v2 source/document/location/handle/bundle trace。
- companies-only EX-01 与 CN/HK/US 可用样本通过；下载 canonical writer 行为不变。

### FC-602：DayuAdapter 等价与 dayu-only 样本

- dayu metadata 通过 adapter 正规化，不再由 scanner 特判。
- 至少 2 个 dayu-only capture-ready 样本，其他根无相同 hash；修复“已 index 但 capture_incomplete”的真实原因。
- EX-02、dayu T2、HK/US 可用身份通过。

### FC-603：跨根去重与 deterministic location

- EX-04~07；相同 bytes 一个 document，多 locations，artifact 共享。
- canonical location 基于 policy priority +稳定 tie-break，不依赖扫描顺序。

### FC-604：三根一致性 canary

- 同一 request matrix 分别绑定 companies-only/dayu-only/Dropbox-only。
- 输出 contract 除 root/location provenance 外一致；任何 root-specific业务分支即失败。

### Phase 6 exit gate

- 三根都有唯一样本和真实 T2 证据；future root 配置-only 仍通过。
- company/dayu v1 scanner 可以进入退役观察，但此时尚不删除。

## Phase 7（Normalized Resolver、严格身份与 ResolutionEnvelope）— 状态：in_progress（FC-701 执行中）

### FC-701：normalized-only resolver

- Owner：company-wiki。
- resolver 只消费 active normalized assertion + RootPolicy snapshot；不读 `acquisition/dayu_meta`。
- 对 remediation/unprovable/retired/conflict 明确排除 reason。
- CodeGraph/AST gate 禁止 legacy metadata container production caller。

### FC-702：严格 identity 和 period

- 移除“非数字 security_id 当公司名 soft-match”等弱匹配。
- entity alias 只来自版本化 identity registry；market/security/form/period 冲突 fail closed。
- SAFE-01~07、中文/英文公司别名和前导零 ticker tests。

### FC-703：来源无关 SQL 与性能

- SQL pushdown 使用 entity/period/kind/status/root policy cohort，不在 Python 全表过滤。
- 真实 catalog p50/p95、candidate cap、并发读取 SLO；EX-07 确定性。

### FC-704：ResolutionEnvelope + AcquisitionTrace

- envelope 同时返回 handle、bundle、policy/epoch、真实 outcome、exclusion/debug trace。
- trace 从 journal/event 产生；精确区分 reused_existing、reused_after_discovery、downloaded_new、gap、ambiguous、rejected。
- 修复由 handle 推断 download_calls 的伪回执。

### FC-705：legacy bridge 观察与关闭条件

- legacy observer 必须通过真实 resolver seam 计数且不改真实根；period ledger 写入独立 audit 状态。
- 先确保所有 active request 不命中 bridge；连续两个>=24h 窗口 `legacy_bridge_hits=0` 后才允许关闭。

### Phase 7 exit gate

- normalized resolver 在三根 exact 场景全绿；legacy bridge 可观测、可关、可回滚。
- 仍命中 bridge 时不得进入最终 cleanup。

## Phase 8（latest/gap/授权下载完整闭环）— 状态：pending

### FC-801：CloseGap transaction contract

- Owner：company-wiki。
- 输入绑定 request_id、gap hash、policy hash、provider、allowed IDs、数量/bytes、expiry。
- 步骤固定：rediscover/validate -> fetch staging -> validate -> canonical commit -> scan/assert -> re-resolve。
- partial failure 的原子性和 journal 状态明确。

### FC-802：filing-fetch latest 编排

- filing-fetch 不再把 GAP 一律映射 not_found。
- allow_download=false 返回结构化 gap；allow_download=true 且授权有效时调用 close-gap，并返回最终 envelope。
- 不复制 provider/root/identity 规则。

### FC-803：最小下载与第二次零下载

- LT-01~10、DL-01~10 使用真实跨进程 spies。
- 只下载 gap missing/newer_revision，保留旧期可复用 handle；第二次相同请求 fetch/write=0。

### FC-804：并发、重试和恢复

- single-flight、catalog lock、有界重试、下载成功后中断、staging orphan、provider timeout。
- 所有 outcome 可从 journal 重建；不靠调用者手工重试完成 re-resolve。

### FC-805：真实 provider isolated E2E

- 在临时 wiki 上分别跑 CN/HK/US 最小样本；不写生产 catalog/真实根。
- 真实下载必须显式环境授权；未授权是 blocked，不计 pass。
- 保存 provider metadata hash、下载 bytes hash、首次/二次调用计数，避免固定“最新年份”导致漂移。

### Phase 8 exit gate

- latest 用户入口一次调用即可返回最新 capture-ready handle；第二次零下载。
- CN/HK/US T3 均有新鲜证据或明确用户批准的适用市场范围。

## Phase 9（SourceBundle 与处理产物真实复用）— 状态：pending

### FC-901：artifact 绑定迁移

- Owner：company-wiki。
- 对 7712 legacy artifacts 做 dry-run 分桶：bindable、hash mismatch、missing bytes、unknown generator、legacy_unbound。
- 只在 source/document/content/generator/schema 全可证明时绑定；否则保留不可复用。
- 生产 apply 需 change-window 授权；零删除。

### FC-902：bundle 进入 resolver 生产响应

- `query_source_bundle` 不再是测试/CLI 孤岛；ResolutionEnvelope 生成 snapshot-consistent SourceBundle。
- bundle 查询与 handle 使用同一 policy/epoch/document hash。
- CodeGraph production caller>=1；未知 artifact role fail closed。

### FC-903：filing-fetch 透明转发和兼容

- N/N-1 envelope/bundle contract；旧 company-wiki 无 bundle 时显式 `bundle_status=unavailable`，不是伪造空绿色。
- 不修改 artifact validity 决策。

### FC-904：revenue 真实消费 selector

- `source_preparation.py` 必须调用 selector；按 DAG 只重算缺失角色。
- 删除 `payload.get(selected_artifacts)` 无来源路径；记录 artifact_read 和 producer events。
- AR-01~09 从用户入口跨三进程运行。

### FC-905：可信 capture/安全回执

- `prompt_injection_status` 必须来自 scanner/reviewer receipt；未执行时为明确未审核状态并按政策阻断。
- parser/LLM/download 计数来自 trace/journal，不能由输出推断。
- Mutation：篡改 input/source/artifact hash、模型、prompt、schema 均触发最小失效。

### FC-906：生产 artifact canary

- normalized、markdown、sections、summary、consumer_analysis 各至少一个真实 bound 样本；角色不适用必须有合同说明。
- T2 证明 artifact_read>0 且对应 producer=0；旧 unbound 样本不复用。

### Phase 9 exit gate

- production source-bound artifact 不再为 0；真实用户链能复用处理结果。
- 所有 AR 场景绿色；伪零调用和硬编码 prompt status 删除。

## Phase 10（三仓跨进程 E2E 与真实场景矩阵）— 状态：pending

### FC-1001：统一 isolated lake fixture

- 创建三根真实目录布局、identity/provider snapshots、sidecars、artifacts、corruption variants。
- fixture manifest hash、无真实路径泄漏、无网络、无外部写；可在 Windows/Linux 重现。

### FC-1002：真实三进程 scenario runner

- 从 revenue source_preparation 启动，必须产生 revenue -> filing -> wiki 三个进程 trace。
- provider/parser/LLM 仅边界替换为 spy；catalog/resolver/adapter/bundle/consumer 使用产品代码。
- 标名 E2E 的测试若走单 helper，collection gate 直接失败。

### FC-1003：mandatory matrix 全覆盖

- 95 个 EX/DBX/DL/LT/AR/SAFE/CTRL/OPS/PORT/IDX/UJ/AUD/MIG 场景的所有适用 T1 ID 绿色。
- 场景 registry 自动检查遗漏、重复、skip、expected-failure 伪绿色。
- 已知失败测试必须删除“POST-FIX EXPECTED 注释”并真正断言目标行为。

### FC-1004：平台与安装形态

- Windows 中文用户名、空格路径、Linux、Python 支持版本；stdin/stdout JSON 统一 UTF-8。
- installed skill 与 repo source 同步；不依赖 sibling 固定相对路径。

### FC-1005：mutation/chaos suite

- mutation 至少覆盖：root 特判、epoch 条件、hash 检查、下载授权、latest re-resolve、artifact invalidation、zero-call event、path containment。
- critical mutation kill rate=100%；普通相关模块达到冻结阈值且不可回退。

### Phase 10 exit gate

- 当前 triplet T1 全矩阵绿色；Windows/Linux golden trace 语义一致。
- 不再有“E2E 允许真实链失败但错误 JSON 正确就 pass”的测试。

## Phase 11（持续动态审核与发布总门）— 状态：pending

### FC-1101：PR current-triplet gate

- 三仓 workflow 使用 compatibility manifest；任一仓 PR 均验证相关三仓组合。
- T0/T1、ruff、compile、type、coverage、mutation、receipt validator、CodeGraph architecture gate 必跑。
- 旧固定 pin 仅作为 N-1 兼容项，不得冒充 current。

### FC-1102：每日 production read-only runner

- 按 `dynamic_assurance_plan.md` 在有三真实根权限的本地 Windows runner 定时执行 T2。
- 检查 exact samples、bundle samples、root fingerprints、scan health、legacy hits、schema drift、policy freshness、latency。
- 任何样本 skip、报告过期、completed_with_errors 增长超阈值均失败；只写 audit report，不写真实根/catalog。

### FC-1103：每周真实 provider isolated runner

- T3 CN/HK/US；临时 wiki，首次下载+第二次零下载；网络/凭据缺失产生 blocked alert，不计绿色。
- provider contract 漂移、空结果、限流和内容变化分类告警。

### FC-1104：动态 audit dashboard/ledger

- 保存最近 N 次 triplet、scenario、latency、call counts、root fingerprint token、失败原因和趋势。
- release gate 要求：PR green + 最近24h T2 green + 最近7天 T3 green + 无未关闭 P1/P2。

### FC-1105：审核机制自测试

- 故意注入陈旧 manifest、缺样本、扫描错误、active epoch 漂移、artifact 绑定下降、Dropbox MISSING，证明动态门会红。
- audit runner 自身的 Windows 编码、超时、并发、原子报告写入有测试。

### Phase 11 exit gate

- 连续至少 2 个每日 T2 周期绿色；一次 T3 全市场绿色；故障注入能阻断 release。
- 动态审核不是文档建议，而是非零退出、CI required check/本地 release gate 的硬门。

## Phase 12（硬编码、重复策略、死代码与复杂度治理）— 状态：pending

### FC-1201：root/source hardcode 清零

- 按 `code_quality_plan.md` 的分类和渐进顺序删除 scanner/resolver 中 root kind/ID、Dropbox 子目录、`acquisition/dayu_meta` 分支。
- AST gate 只允许 adapter/config fixture 中出现对应 token。
- EX-08 保证以后新增 root 无需改产品代码。

### FC-1202：单一安全策略源

- filing-fetch 删除独立 allowlist 决策；验证 company-wiki policy snapshot/path containment。
- 删除 revenue/filing 的 `Path.parent / sibling` 隐式生产定位，改用 manifest/显式配置/安装入口。
- config doctor 检查三仓 contract compatibility，不复制 root 列表。

### FC-1203：模块边界和 API 收敛

- 删除/合并只被测试调用且已由生产入口替代的 helper；保留纯 policy 时必须由生产服务调用。
- 用 CodeGraph 检查 dead production symbols、依赖环、跨层 import。
- 将超大函数拆为 resolver pipeline、adapter orchestration、transaction service；行为由既有场景锁定。

### FC-1204：类型、覆盖率、复杂度 ratchet

- filing 和关键 source modules 建立 branch coverage；critical modules>=95%，整体阈值不低于现状且逐阶段提升。
- 新/改关键函数 complexity<=10；存量超标必须在本阶段下降且设 ratchet。
- 对 public contracts 开严格 type check；ruff/compileall/unique test symbol 跨平台绿色。

### FC-1205：错误和编码一致性

- 统一结构化错误 schema、UTF-8 stdio、Windows OEM/locale boundary、日志 redaction。
- PORT-01~03，当前 audit_baseline 和 unique-test-symbol failures 必须关闭。

### Phase 12 exit gate

- forbidden hardcode=0、重复 root policy=0、关键 dead helper=0、Windows 编码错误=0。
- 代码质量门是 required check，不能只记录报告。

## Phase 13（可观测性、健康度、性能与容量）— 状态：pending

### FC-1301：统一 reason/outcome taxonomy

- resolve/admission/gap/download/artifact/rollback 使用版本化 reason codes。
- debug trace 可解释每个候选排除，不泄露绝对路径或敏感内容。

### FC-1302：scan health/error budget

- `completed_with_errors/interrupted` 不能只统计；定义增量、比例、连续失败和陈旧 root 阈值。
- canary 非零退出并生成 top reason/remediation link。

### FC-1303：真实 catalog SLO

- 49GB/27M evidence rows 上测 resolver、bundle、latest coverage、migration batch。
- 记录 p50/p95/p99、峰值内存、锁等待、并发读；设回归预算。

### FC-1304：容量和并发故障

- 大文件、海量 locations、重复候选、并发 scan/resolve/download、catalog lock、磁盘不足。
- OPS-02/03、DL-08/09，证明有界资源和恢复。

### Phase 13 exit gate

- T2 报告包含健康阈值和 SLO verdict；当前 155 error/15 interrupted 有可解释基线与清理/豁免 owner。

## Phase 14（渐进发布、真实 canary 与安全回滚）— 状态：pending

所有生产写入/下载均需当次显式授权。每一波必须：副本演练 -> preview -> 用户批准 -> 最小 cohort -> T2/T4 -> 观察 -> 扩大；失败立即回滚。

| 波次 | 内容 | 进入条件 | 退出条件 | 回滚 |
|---|---|---|---|---|
| R0 | 新 governance/triplet gate | Phase 1 | required checks 生效 | 回退 workflow/manifest |
| R1 | runtime control plane | Phase 2 副本绿 | CTRL T4 真实响应可回滚 | policy epoch rollback |
| R2 | v2 scanner dry shadow | Phase 3 | 两周期 diff 全解释 | flag off，无数据删除 |
| R3 | companies cohort | Phase 4/6 | exact/bundle/SLO 绿 | cohort rollback |
| R4 | dayu-only cohort | R3 | EX-02/T2 绿 | cohort rollback |
| R5 | Dropbox-only cohort | Phase 5/R4 | DBX 全绿、external write=0 | cohort rollback |
| R6 | SourceBundle/artifacts | Phase 9 | AR T2 绿 | bundle flag off |
| R7 | latest/close-gap | Phase 8 | T3/T4、二次零下载 | latest flag off，exact 保持 |
| R8 | legacy bridge off | 两个>=24h zero-hit | 全矩阵绿 | bridge flag 临时恢复 |
| R9 | v1/legacy code删除 | R8 再观察一周期 | forbidden gate=0 | revert release commit |

发布 receipt 必须记录 before/after triplet、policy epoch/cohort、scenario、SLO、root fingerprints、catalog hashes、side effects、rollback command 和 reviewer。

## Phase 15（独立终审、关闭已知问题与持续运维）— 状态：pending

### FC-1501：机器 closure gate

- 验证所有 mandatory FC accepted、所有 scenario mandatory passed、真实报告新鲜、无 pending/blocked/known-gap。
- 验证 release manifest 所有路径存在、HEAD 与 upstream/current triplet 一致、config/policy/plan hash 正确。

### FC-1502：独立对抗式代码审查

- reviewer 不复用实施者结论；从 architecture_target 反向检查 production callers、旁路、硬编码、伪计数、skip、人工数据库步骤和不可回滚状态。
- CodeGraph 检查 Sidecar/Bundle/Selector/Flags/CloseGap 的生产可达性以及 legacy caller=0。

### FC-1503：真实用户旅程复验

- companies-only、dayu-only、Dropbox-only exact；旧期+latest；真实 bound artifact；CN/HK/US isolated download；Windows 中文路径。
- 每个结果生成可重放 trace，不暴露私有绝对路径。

### FC-1504：观察期与回滚演练

- 至少两个>=24h T2 周期、最近7天 T3、legacy hit=0、shadow diff=0、无 scan health/SLO 回归。
- 从已发布状态执行一次最小 cohort rollback/re-activate 演练。

### FC-1505：最终 closure ledger

- 由工具生成，不手写；逐条映射六项目标、scenario IDs、receipts、triplet、真实报告和独立 review。
- 只有 closure validator exit 0 才更新状态为 `complete`。

### 最终验收问题

- [ ] 新增一个符合 adapter contract 的 root 是否只改配置即可 exact/latest/artifact 复用？
- [ ] Dropbox-only 真实样本是否从 revenue 用户入口返回且所有昂贵调用为 0？
- [ ] 已有旧报告时是否只下载缺失最新报告，第二次零下载？
- [ ] 已处理产物是否按角色真实复用，篡改/版本变化是否最小失效？
- [ ] flag/epoch/cohort 是否真实控制 resolver，并能改变同一请求响应完成回滚？
- [ ] CI 是否验证当前三仓 triplet，动态 runner 是否能因真实回归阻断发布？
- [ ] 所有 known-gap、pending review、旧 pins、缺失 ledger、Windows 编码问题是否关闭？
- [ ] scanner/resolver 是否不再含 root-specific/legacy metadata 硬编码？

任一答案为否：整体状态仍为 `incomplete`。

## Errors Encountered

| 日期 | 错误/风险 | 处理 |
|---|---|---|
| 2026-08-09 | 旧 release manifest HEAD 过期且 closure ledger 路径不存在 | 新 Phase 1 重建 manifest/receipt/closure validator，旧证据只读保留 |
| 2026-08-09 | production 有 16 active v2 assertions，但 WU-905 声称 reader 未激活 | Phase 2 作为最高优先级，冻结扩大 cohort，先修控制平面和真实 rollback |
| 2026-08-09 | Dropbox 缺少真实唯一样本 | Phase 5 设置明确 blocked/用户批准路径，禁止用重复文件伪造成功 |
| 2026-08-09 | artifacts 7712 条但 source-bound=0 | Phase 9 先 dry-run 分桶，无法证明的保留为 legacy_unbound |
| 2026-08-09 | Windows 中文路径出现 UTF-8 subprocess 失败 | PORT-01 和 FC-1205 设为 mandatory required gate |
