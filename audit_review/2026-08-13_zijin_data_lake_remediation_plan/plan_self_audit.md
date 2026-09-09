# 计划对抗式自审

> 自审对象：本目录的全部计划文档，不是产品实现。  
> 自审日期：2026-08-13。  
> 结论：计划在通过本文件列出的结构检查后可作为实施基线；所有产品工作仍为 `pending`，不得把“计划完整”解释为“问题已修复”。

## 1. 本次自审回答什么

1. 六个最终目标是否都有明确架构变化、原子任务、真实测试、运行证据和独立关闭门？
2. Dropbox 能否最终通过配置启停，而不是继续加路径硬编码？
3. 已下载文件、已处理 artifact、缺失最新期间和同期间修订版是否被分开测试？
4. 七份研报、官方网页、矿山/储量/地区/逐年贡献是否进入真实 consumer journey，而不仅是“被索引”？
5. revenue 的 generator、validate-only、draft/formal、publication、backtest 和 confidence 是否各有防伪门？
6. 一个能力较弱的实施模型能否仅凭单张任务卡知道允许改什么、先跑什么、如何判失败、何时必须停？
7. 动态审核是否真的被调度、能发现自身失灵，并阻止陈旧/跳过/自签证据发布？

## 2. 六项目标闭环检查

| 目标 | 架构落点 | 原子任务 | 关键场景 | 最终证据 | 自审 |
|---|---|---|---|---|---|
| G1 重构完全成功 | Reader/Writer 能力隔离；source/location/readiness 解耦；旧路径退役 | ZR-201～307、403～405、1002～1009 | READ、BR、UJ、AUD2 | read 指纹、CodeGraph caller=0、rollback、independent review | 覆盖 |
| G2 Dropbox 功能接入 | RootPolicy 3.0 + adapter；consumer-specific eligibility；private-user policy | ZR-401～405、501～510、1004/1006 | ROOT/BR、ZJ-02/03 | config false↔true subprocess、7 PDF canary、external-write=0 | 覆盖 |
| G3 所有功能目标 | local match × freshness；GapPlan；ProcessingDemand；mine/accounting/revenue bridge | ZR-301～307、406～408、507～509、601～713 | FRESH/AUTH/MINE/REV/ZJ | download/producer call ledger、reconciliation、可重放 forecast | 覆盖 |
| G4 动态审核 | machine registry、四级调度、freshness、SLI、release/self-test | ZR-801、901～905、1104 | AUD2-01～08 | 真实 schedule run、alert delivery、stale report rejection | 覆盖 |
| G5 真实 E2E | 三 subprocess、真实 roots 只读、真实 provider 隔离下载、七 PDF/网页 | ZR-102、802～806、1103 | 新旧全矩阵 | process trace、root fingerprint、call budget、第二次复用 | 覆盖 |
| G6 代码质量 | 契约单一真源、复杂度/类型/覆盖率 ratchet、硬编码/死路径 gate | ZR-104/105、701～705、906/907 | REV/AUD2 mutation | CI required checks、drift patrol、阈值只升不降 | 覆盖 |

自审结论：六项均具备从需求到运行证据的链；最终是否通过，只能由 Phase 11 的新鲜证据决定。

## 3. 已修正的计划内部缺陷

### PA-001：矿业 ADR 顺序原先不够严格

- 风险：弱模型可能先实现 `MineYearOperation`，再补会计/单位 ADR，导致紫金特例固化。
- 修正：ZR-605 现在显式依赖 ZR-610；ZR-609 还必须等待通用合成 E2E ZR-611。
- 防回归：dependency validator 必须拒绝未批准 ADR 就开始矿业代码。

### PA-002：紫金终验存在自依赖表达风险

- 风险：`ZR-705~713` 包含 ZR-709 自身，机器调度会形成环或被弱模型解释为可跳过。
- 修正：依赖改为 ZR-705～708、ZR-710～713、ZR-609、ZR-611，明确 ZR-709 最后运行。
- 防回归：Phase 0 生成 DAG 并要求拓扑排序成功、无 self-edge。

### PA-003：最终 soak 与动态审核口径不一致

- 风险：仅“两次 24h T2”无法证明 Daily/Weekly/Monthly 调度持续有效。
- 修正：ZR-1104 与动态计划统一为连续 7 次 Daily、2 次 Weekly、1 次 Monthly、1 次告警自检，加真实 rollback/re-activate。
- 防回归：自然时间戳、scheduler run ID 和独立告警回执必须可验证，不得手工补状态。

## 4. 弱模型防跑偏审计

每张实施任务卡必须能机械回答以下 14 个问题；少一项就不能开始：

1. 唯一 work-unit ID 是什么？
2. 当前固定 triplet 和计划 hash 是什么？
3. 上游依赖是否已 `accepted`，而不是仅 `implemented`？
4. 允许修改的文件/表/配置 allowlist 是什么？
5. 明确禁止碰哪些生产资源、旧 artifact、registry 和计划文件？
6. 先建立的 RED/反例是什么，失败原因是否正是目标缺陷？
7. happy、negative、fault、mutation 四种 oracle 分别是什么？
8. 调用预算是多少：download/discovery/parser/LLM/DB write/registry append？
9. 如何证明没有隐藏 side effect？
10. 哪些命令必须逐字执行，何种 skip/blocked 语义适用？
11. 哪个 CodeGraph/静态架构检查证明没有旧 production caller 或硬编码？
12. 性能、兼容性和 N/N-1 阈值是什么？
13. rollback 如何做，如何证明恢复的是同一 canonical result？
14. 独立 reviewer 需要从哪些原始证据重算结论？

[implementation_runbook.md](implementation_runbook.md) 提供统一任务卡与 stop rule；[work_unit_registry.md](work_unit_registry.md) 提供 owner/依赖/目标/证据；[scenario_matrix.md](scenario_matrix.md) 提供 oracle。实施时必须把三者展开到 work-unit receipt，不能只引用一个模糊 phase 名。

## 5. 对“虚假完成”的攻击测试

| 攻击 | 计划应如何阻止 |
|---|---|
| 新建 Reader，但 production resolver 仍构造 Store | CodeGraph caller gate + initializer spy + OS read-only E2E |
| Dropbox 被写进配置，却仍因 companies 默认 allowlist 失败 | config false↔true 必须穿过 revenue→filing→wiki subprocess；v2 handle 不得 fallback |
| 新增一个 Dropbox `if` 让单例通过 | root/company/path literal architecture gate；future_lake 仅配置接入场景 |
| 文件 exact reuse，但 safety/artifact blocked 被报成总失败 | staged envelope 必须同时显示 reuse、download=0、blocker、next action |
| artifact backfill 写表成功但 consumer 不读 | apply 的退出 oracle 是真实 SourceBundle 命中和第二次 producer=0，不是行数增加 |
| 用 artifact INSERT trigger 冒充 parser/LLM 调用 | producer attempt/result ledger 与 artifact-created event 分表/分字段，失败 attempt 也记录 |
| 用 filename 年份判断“最新” | local match 与 provider freshness 正交；非自然年、revision、future 场景 |
| 未授权也偷偷下载 | provider metadata discovery 与 bytes fetch 分开计数；授权前 fetch=0 |
| 研报有 MD 就宣称可检索 | 7/7 还必须 table/chunk/tag/source binding、实体 precision/recall 和消费 trace |
| 把资源量当储量、权益产量再乘 ownership | typed fact +单位/口径/会计 mutation；独立会计 ADR gate |
| 用矿产量×现价冒充披露逐矿收入 | operating/commercial/accounting bridge + reconciliation；输出标 model estimate/gap |
| generator 的弱 linter 绿色就宣称有效 | 真实 `validate_document` 和 draft full-run 是 mandatory oracle |
| `validate-only` 返回 0 但偷偷注册 publication | registry SHA/size/mtime/rows + 文件树 + write API trap |
| duplicate claims/参数拆分把 confidence 做高 | adversarial confidence corpus；policy hash；rating cap 可重算 |
| runner 存在但 schedule 没运行 | scheduler run ID、freshness、原子报告、告警链；过期/blocked 阻断发布 |
| required E2E 因无凭据 skip 后 CI 绿色 | `blocked` 告警且 release 红；required skip 机器拒绝 |
| reviewer 与实现者同一人自签 | receipt validator 拒绝同一 identity；clean-worktree 独立重放 |
| 为过测试改 golden 或降低阈值 | baseline ratchet + golden-update 独立工作单元 + plan-drift 审批 |

## 6. E2E 真实性审计

真实 E2E 至少同时满足：

- 从 revenue 用户入口启动真实 CLI/subprocess，不能直接调用内部 validator 代替。
- company-wiki catalog 和三个 root 是隔离 fixture 或 production 只读 canary；生产 read-only replay 的 byte/mtime/fingerprint 必须不变。
- provider、网络、LLM 只在明确边界用 fake/spy；被验证的 resolver、policy、bundle、processing、forecast、renderer 不能 mock。
- first run 与 second run 成对：第一轮按场景产生 0 或 1 次下载/处理，第二轮必须验证复用和调用归零。
- 每个 happy path 至少有一个身份/权限/篡改负例、一个故障注入和一个能杀死目标实现的 mutation。
- 七份 PDF、错误 strategy HTML、财报和矿山样本以 hash/locator 注册；测试日志不泄漏私有全文。
- T3/T4 的网络或私有处理授权缺失时状态是 blocked，不能用合成场景替代后标 pass。

结论：场景矩阵覆盖真实旅程的文件、处理、来源、模型和发布层；Phase 8/11 又从用户入口复验，避免单仓测试孤岛。

## 7. 尚需在实施期冻结的决策

这些不是计划遗漏，而是必须以当前事实/ADR 决定、禁止现在猜测的参数：

| 决策 | 最迟工作单元 | 决策证据 | 未决时行为 |
|---|---|---|---|
| 当前三仓 triplet、CodeGraph freshness、旧缺陷是否仍复现 | ZR-001 | clean replay、HEAD/hash | blocked |
| RootPolicy adapter/profile 合法枚举和 N-1 截止期 | ZR-401/402 | registry/consumer inventory | fail closed |
| 七 PDF 的私有数据能否使用外部 LLM | ZR-507 | 用户授权与 privacy policy | 仅本地处理/blocked |
| artifact 中可证明 bindable 的真实比例 | ZR-305 | 只读统一 validator dry-run | 0 时禁 apply，按需重处理 |
| 紫金逐矿 modeled coverage 阈值和 residual 上限 | ZR-610/609 前 | FY2025 口径、materiality ADR | 不切换，只 shadow |
| schema 3.8 字段与 3.7 兼容窗口 | ZR-711 | ADR、consumer inventory | 3.7 默认不变 |
| complexity/coverage/SLO 精确 ratchet | ZR-104 | 当前可重复基线 | 不得低于基线 |
| Daily/Weekly/Monthly 调度 owner、凭据和告警接收者 | ZR-902/903 前 | 运行环境与权限清单 | blocked/release 红 |

## 8. 并发与文件冲突自审

- 本计划使用独立目录，不修改旧 `audit_review/*` 计划。
- 所有新增计划文件由本任务单独拥有；子审查只读，未写文件。
- 编制过程使用写前读取/hash/mtime和局部补丁；发现 hash 漂移时应停止合并，禁止覆盖。
- 实施期间每个 work unit 还必须有独占 evidence 目录和 shared-resource lock；同一 SQLite、golden、registry、worker、workflow 或计划状态表不能并发写。
- [legacy_plan_disposition.md](legacy_plan_disposition.md) 只是状态建议投影；旧计划由其 owner 自行更新，避免两套 planning-with-files 互相覆盖。

## 9. 计划完整性结论

| 检查 | 结论 |
|---|---|
| 六项目标都有任务—测试—证据 | 通过 |
| 文件复用、最新补齐、artifact 复用分别建模 | 通过 |
| Dropbox 配置化接入且无路径特判 | 通过（目标态；当前尚未实现） |
| 研报 MD/table/chunk/tag/fact 与 consumer trace | 通过 |
| 逐矿事实、运营、商业、会计和公司对账 | 通过 |
| generator/validate-only/draft/formal/backtest/confidence | 通过 |
| 真实 E2E 与故障/mutation/二次复用 | 通过 |
| 动态调度、freshness、告警、自测、soak | 通过 |
| 弱模型 allowlist/stop/rollback/reviewer 纪律 | 通过 |
| 渐进迁移和 legacy 删除门 | 通过 |
| 产品实现是否已经完成 | **未通过；本轮明确未实施** |

最终判断：这是一套能够把已知问题逐项关闭、并降低重复审计成本的完整实施基线。它不允许以“代码写了”“测试数量多”或“索引里有文件”提前完成；只有 Phase 11 的机器 closure 和独立复验能改变整体状态。
