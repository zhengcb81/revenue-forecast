# 计划编制发现与决策记录

## 发现 001：本计划必须与其他 planning-with-files 任务物理隔离

- 日期：2026-08-13
- 事实：用户明确告知另有程序同时修改计划文件；当前仓库也已有其他 audit/assurance 文件变更。
- 决策：本任务只写 `audit_review/2026-08-13_zijin_data_lake_remediation_plan/`。
- 影响：旧计划只读引用；不得为了“统一状态”直接更新其他任务计划。实施时若要归档旧计划，应另立经审核的状态迁移任务。

## 发现 002：计划中的“已完成”必须由当前代码和证据重新证明

- 日期：2026-08-13
- 事实：紫金审计运行期间三个仓库持续发生其他 agent 提交和工作树修改。
- 决策：旧审计结论是需求与回归用例来源，不自动等于当前缺陷仍存在；每个实施 phase 先做 plan-drift 检查。
- 影响：任务不得依赖易漂移行号；验收必须绑定 commit、测试命令、回执和产物 hash。

## 发现 003：旧全面计划的“accepted/complete”与最新真实用户运行存在证据冲突

- 日期：2026-08-13
- 旧计划声明：artifact bundle/selector、安全回执、真实三进程 E2E、动态审核和多数代码质量阶段已经 accepted/complete。
- 最新紫金运行事实：exact 文件虽复用且零下载，revenue-ready source 因 `not_reviewed` 失败；旧 MD/summary 无合格绑定；Dropbox 七份研报全部零 artifact/span/tag；live worker 下所谓只读 resolver 出现只读写失败和锁错误；合法 draft 的封存版本无法由 native renderer 渲染。
- 结论：旧计划的完成回执只能证明当时特定 fixture/canary/triplet，不足以证明真实用户旅程已完成。新计划必须新增“声明—生产行为一致性”门，禁止用模块测试或孤立 canary替代用户入口证据。

## 发现 004：应继承旧计划中已经成熟的治理资产，但不能继承完成状态

- 日期：2026-08-13
- 可继承资产：FC work-unit 思路、场景编号、独立 reviewer、mutation kill、triplet manifest、T0/T1/T2/T3/T4 分层、渐进 cohort/rollback、动态审核与 closure ledger。
- 必须重开或扩展的能力：真实只读 reader、共享安全审查闭环、legacy artifact 可审计迁移、Dropbox broker-research 语义摄取、consumer demand queue、矿山事实/运营/会计桥、revenue generator/validate-only/draft renderer。
- 影响：新计划采用“复用治理框架、重验业务闭环”的策略，避免从零重造，也避免错误沿用绿色状态。

## 发现 005：最新紫金运行给出了可直接固化为 E2E 的生产级反例

- 日期：2026-08-13
- 反例包括：三根重复位置但 exact reuse 消费失败、live writer 锁竞争、`not_reviewed` 阻断、旧 artifact 人工可读但生产不可复用、七份 Dropbox PDF 可读却未语义摄取、比较报告跨实体错归、HTTP 200/hash 正确但页面身份错误、2028 指引不得外推为 2030 事实、draft 计算成功但 renderer 失败。
- 决策：这些不是文档备注，而要成为 mandatory 场景；每个缺陷至少有正例、负例、故障注入和回归防倒退门。

## 发现 006：三个仓库的 CodeGraph 当前均可用于实施前结构核验

- 日期：2026-08-13
- revenue-forecast：148 files / 2,603 nodes / 4,317 edges。
- filing-fetch：17 files / 437 nodes / 1,120 edges。
- company-wiki：455 files / 9,232 nodes / 20,842 edges。
- 决策：未来每个涉及模块边界、调用链或删除 legacy 的 work unit，必须在固定 triplet 上保存 CodeGraph context/impact/caller 证据；但 CodeGraph 不能替代运行测试，且写后需等待索引同步。

## 发现 007：计划编制时的当前 triplet 已明显晚于紫金封存运行

- 日期：2026-08-13
- revenue-forecast：`5f76fcf82abe58d7ee43ffed843a6e8094b72315`。
- filing-fetch：`83c638e76e40890262746cdf02b6df495dcb4031`。
- company-wiki：`d17d8b82e8d650b02693b343f7d87ca5fdf53e99`。
- 影响：紫金运行时 renderer、contract 和 company-wiki 行为不能直接宣称仍未修复；新计划将它们列为 Phase 0 必须重放的回归用例。只有当前 triplet 真实重放绿色，才可标“已解决候选”；没有用户入口证据不得取消任务。

## 发现 008：当前代码上下文仍显示部分高风险契约形态

- revenue `render_markdown` 仍以 `validate_forecast_output(result)` 开始；是否已正确识别 draft receipt 需要运行时回归证明，不能仅凭源码片段下结论。
- filing `FilingFetchError.retryable` 仍只按结构化 code 集合决定；raw SQLite lock 是否已在更上游归一化需专门契约/E2E 验证。
- filing 仍有测试支持代码通过 `Path.home()/Projects/company-wiki` 指向生产仓库；计划必须建立“测试不得隐式依赖真实 sibling/root”的 AST/collection gate。
- company-wiki 的泛化查询首先命中旧 `scripts/ingested_db.py` 和 `ReviewQueue`，说明仓库同时存在 legacy 与 source_catalog 两套基础设施；实施前必须做生产 caller/死路径清查，而不是盲目在错误层新增第三套机制。

## 发现 009：并发计划风险当前受控，但其他工作树仍在变化

- revenue 当前有 Phase-14 ledger、旧全面计划 findings 和 assurance runs 变化；company-wiki 有用户/环境侧 settings、cost/coverage 变化；filing 工作树当前干净。
- 本计划目录仍是唯一由本任务写入的区域；这些状态只用于提示实施前固定 triplet，不纳入本轮改动。

## 发现 010：旧架构目标中的三仓职责边界仍应保留

- company-wiki 应是数据湖控制面和事实所有者：root/admission、identity、resolver、gap/download transaction、artifact/source bundle、migration 与数据质量。
- filing-fetch 应保持薄编排：校验 request、转发授权、深度校验并透明转发 envelope/handle/bundle/trace；不得复制 root/latest/artifact 安全策略。
- revenue-forecast 应是消费者和用户入口：消费 bundle、只重算失效角色、记录权威调用事件、完成收入契约与跨仓用户旅程。
- 新增 broker research、矿山事实和 consumer-demand queue 时必须遵守该边界，不能把 company-wiki 的语义事实职责塞进 revenue，也不能让 filing-fetch 变成通用网页/研报下载器。

## 发现 011：旧实施治理足够严格，应升级而非重写

- 可直接继承：一个 FC 一个上下文/提交、16 步生命周期、先 RED、固定 command registry、CodeGraph impact、diff allowlist、focused→repo→triplet→real tier、fault injection、mutation、回滚、实施者/审查者分离和机器 closure。
- 新计划需要增加：计划文件并发锁/hash 协议；用户旅程 evidence 优先于 work-unit receipt；真实生产反例必须进入 mandatory registry；测试对生产 sibling/root 的隐式引用禁止门；schema/data migration 先 shadow dual-read 再 cutover。

## 发现 012：旧 95 场景矩阵覆盖基础复用，但不足以关闭本轮问题

- 应保留 EX/DBX/DL/LT/AR/SAFE/CTRL/OPS/PORT/IDX/UJ/AUD/MIG 场景和 T0–T4 层级。
- 必须新增四组：`READ-*` 真只读与锁竞争、`BR-*` broker research/表格/多实体、`MINE-*` 矿山事实与会计桥、`REV-*` generator/validate-only/draft/formal/backtest。
- 旧 `DBX-*` 主要证明 Dropbox filing 安全，不等于 broker research 被预处理、可检索或被 revenue 使用；这两件事必须分开验收。

## 发现 013：动态审核必须同时检查“机制活着”和“业务目标仍然成立”

- 旧 PR/T2/T3/T4、freshness、sample rotation、fault self-test 设计应保留。
- 新增业务 SLI：exact reuse 成功率、download avoidance、artifact reuse hit、legacy-unbound 命中、consumer-ready 比率、broker table fidelity、entity misattribution、mine-fact conflict、forecast explicit-model share、backtest error、draft/formal render 成功率。
- 历史 `complete` 只能表示当时 accepted；任何动态证据过期、样本缺失或真实旅程失败，发布资格必须自动降为 blocked。

## 发现 014：Catalog 真只读缺陷在当前 company-wiki HEAD 上仍由源码直接确认

- 当前 `CatalogStore.__init__` 无模式参数，始终创建父目录并调用 `_initialize()`。
- `_initialize()` 始终执行 `PRAGMA journal_mode=WAL`、完整 DDL、additive migrations、schema meta 写入和 commit；migration 还会 seed fingerprint state。
- `fetchone`、`fetchall`、`status` 虽然查询本身只读，却只能在这个写能力构造完成后使用。
- 结论：Phase 2 不是“待确认是否需要”，而是确定需要。目标不是给现有构造器加一个脆弱布尔开关，而是拆出无法获得写能力的 Reader/只读连接工厂，并从所有 query/resolve/status 生产入口消除 writer 初始化。

## 发现 015：filing-fetch 的重试正确性仍依赖上游先产生精确 `catalog_locked`

- 当前 `_run_company_wiki_json_retry` 只对 `exc.code == "catalog_locked"` 退避，其余错误立即抛出。
- 因而必须在 wiki CLI→filing wrapper 契约边界覆盖 raw SQLite `locked`/`busy`、operation lock、timeout、worker paused 等所有实际形态，统一成版本化 reason code；仅测试重试循环本身不够。
- 验收需要从 revenue 用户入口制造 live-writer contention，证明错误分类、deadline、退避次数和最终成功/结构化失败均正确，且无下载/无重复写。

## 发现 016：当前 renderer 是否修复必须用同一封存 draft 重放，而非静态推断

- 当前 `render_markdown` 仍首先调用 `validate_forecast_output`；封存版本正是在这条路径把 draft 送进 formal-only 校验。
- validator 在之后提交中可能已经变化，因此 Phase 0 要用紫金 `input_v1.json` 或等价固定 fixture 重放 `run_forecast(mode='draft') -> render_markdown`。
- 只有同时通过 draft 正例、formal 正例、篡改 receipt 负例、registry 零写断言，才可把该问题标为已解决；否则进入 Phase 7。

## 发现 017：revenue 契约三项核心缺陷在当前 HEAD 仍存在

- schema runtime 为 3.7，但 input schema/construction/compliance 文档仍有 3.6；linter 的顶层必填集合缺 growth tree、management communication/targets 和 evidence claims。
- generator 仍存在 direct-revenue/ratio driver 错配、recognition 缺字段/claim、非法 `not_checked` 和缺 `management_targets`；现有测试只过弱 linter，未进入真实 validator/engine。
- CLI `--validate-only` 仍调用 formal `run_forecast`，formal 会注册 publication；测试没有断言 registry/filesystem 零变化。
- 当前 HEAD 的 draft+native renderer 只读重放仍稳定报 `publication_receipt gate_ids mismatch`。
- 因此 ZR-701~704 必须实际修改，不能在 Phase 0 取消；formal 强验证/registry/对抗测试则作为“已实现候选”重验。

## 发现 018：矿业模型库存在基础模型，但远未达到逐矿收入目标

- `reserve_depletion/resource` 已存在，说明无需另起一套引擎；应扩展组合能力。
- 当前模型不足：mine×commodity×product、权益/并表、内部销售抵销、TC/RC、FX、副产品和报告分部会计桥。
- backtest 基础设施和防篡改测试是已实现候选，但尚未把紫金或真实滚动历史接入动态门。

## 发现 019：动态审核代码存在不等于动态机制正在运行

- revenue 仓已有 T2/T3 runner 和较强 PR CI，但当前 workflow 只见 push/PR 触发，没有 schedule。
- 新计划要求同时验收 runner、调度、凭据/本地 runner、报告新鲜度、release gate 消费和故障自测；缺任一层都不能称“完善动态审核”。

## 发现 020：Dropbox 已在配置中，但端到端仍有两层硬编码/兼容断点

- 当前 config 仍是 v1；resolver 仍按 root `kind` 放行，而不是完整 RootPolicySnapshot。
- filing `_handle_from_resolution` 未透明传递 policy snapshot，`validate_handle` 默认只允许 `<wiki>/companies`，所以 Dropbox-only/dayu-only 仍可能在下游被拒。
- GapPlan 已有 `newer_revision` 语义，但 filing close-gap 只处理 `missing`；“已有旧报告+只补最新”尚未完全闭环。
- raw `database is locked` 仍未统一成 `catalog_locked`。这些均进入确定性工作单元。

## 发现 021：company-wiki CodeGraph 索引健康不等于新鲜

- 子审查发现 company-wiki CodeGraph 的最后更新时间早于当前 HEAD 约三天；此前 status 只显示规模，没有显示与 HEAD 的 freshness。
- 决策：ZR-001 必须记录 `HEAD + CodeGraph indexed commit/mtime/hash`，索引落后则在获得授权后重建；结构结论同时由当前文件核对。任何 receipt 不能仅写“CodeGraph healthy”。

## 发现 022：Dropbox 是“物理已接入、语义未闭环”，且存在隐私默认风险

- 配置已有 Dropbox directory/reusable，但生产仍走旧 1.x root kind；sidecar adapter 已存在却未成为生产 dispatch 真源。
- scanner 在非重点目录会把支持文件包括 `.source.json` 当 primary；实体主要由路径公司目录名推断。
- page-aware parser 已保留表/cell 坐标，但 normalizer 把表格降成逐 cell bullet；section extractor只针对 filing，不是通用 chunk/tag/fact 系统。
- Dropbox 未显式 privacy class 时可能默认 public；私人券商研报进入外部 LLM 前必须有明确 privacy authorization。本计划把 `private_user`、本地/外部 producer capability 和零未授权外发列为硬门。

## 发现 023：artifact migration 当前有“影子写入无人读取”的闭环断点

- `artifact_backfill.py` apply 写 `artifact_bindings` shadow 表，但生产 SourceBundle 仍从 `artifacts` 列读取；没有生产 reader 消费 shadow binding。
- `validate_artifact` 对 source SHA 是“有值才比较”，不是强必填；backfill 从 metadata JSON 读取 schema/source hash，而 bundle 从 artifacts 列读取，迁移判定与消费者真源漂移。
- 决策：ZR-304/305 顺序必须是先统一唯一 reusable view/validator 并接入生产 bundle，再做 migration dry-run/apply；禁止为了提高绑定率先写 shadow rows。

## 发现 024：矿山数据层必须把文档、表格、chunk、fact 和预测模型分开

- `BrokerDocumentIdentityV1` 支持多实体和局部 attribution；`TableArtifactV1` 保存矩阵/表头/脚注/单位/页图；`SemanticChunkV1` 只做可逆检索；`MiningFactV1` append-only 保留 raw/normalized、期间、actual-estimate、ownership 与 conflict；`AssetRegistryV1` 区分单矿/矿群/运营公司/项目。
- company-wiki 只产事实候选/accepted facts 与证据；revenue 才拥有 analyst assumption、mine-year scenario 和会计桥。
- 这能防止“表格能搜到”被误当成“逐矿收入已经建模”。

## 发现 025：全局 canonical location 与“本次请求可读位置”必须分离

- 当前 resolver 仍可能从全局 canonical location 构造 handle；若该位置不符合本 consumer policy，而同 document 在另一个已允许 root 有健康位置，通用数据湖语义仍会失败。
- 目标选择顺序应是：同 document 的 active locations → request policy eligibility → health → root priority → 稳定 tie-break；读取不能顺手更新全局 canonical。
- document/source/artifact identity 不随位置变化；新下载写目标仍只有 companies canonical root。

## 发现 026：producer event 与真实 parser/LLM attempt 不能混为一谈

- 当前 artifact INSERT trigger 只能证明创建 artifact；producer失败无 artifact时没有事件，UPSERT/update也不等于真实调用。
- 需要两个账本：artifact-created journal 与 producer attempt/result ledger。后者记录attempt、依赖、实际parser/LLM次数、成功/失败和输出artifact。
- consumer receipt 必须区分历史生产事件与 `calls_this_request`；否则“零调用复用”仍可能是伪证据。

## 发现 027：exact/equivalent 与 freshness 是两个正交问题

- 本地匹配至少分 exact/equivalent/missing/ambiguous/unusable；远端新鲜度另分 current/newer_period/newer_revision/not_published/unknown/future。
- 不能用文件mtime、`as_of_year-1`或空provider结果声称最新；非自然年、修订版、多form/语言需要adapter规则。
- GapPlan的 actionable 集合必须包含 `missing ∪ newer_revision`（以及coverage policy要求的newer_period），授权绑定gap/policy/candidate/hash/TTL/预算。

## 发现 028：revenue 还需要关闭置信度可博弈与 formal 半发布风险

- 重复claim、等价参数拆分、`other_revenue`插头、零影响sensitivity、单个低误差backtest、错公司/模型/as-of accuracy record 都必须不能抬高分数。
- ConfidencePolicy 要版本化并写入结果，缺backtest、fallback高、unattested evidence等应有rating cap。
- formal publication 要做 prepare/commit 原子流程；output/registry/sign/rename失败不能产生“registry有记录但artifact不存在”的孤儿。

## 发现 029：计划编制期间 revenue HEAD 再次漂移，证明 Phase 0 重新基线不可省略

- 计划初次冻结时 revenue HEAD 为 `5f76fcf82abe58d7ee43ffed843a6e8094b72315`；最终结构自审时已变为 `ac6ac35726c33d61499079c6dbe12b70ccab2e8c`，而 filing/company HEAD 仍分别为 `83c638e76e40890262746cdf02b6df495dcb4031`、`d17d8b82e8d650b02693b343f7d87ca5fdf53e99`。
- revenue 还出现了本任务未创建的 `tools/closure_gate.py`、对应测试和 assurance/audit 目录；company-wiki 仍有用户/环境工作树变更。本任务未读取后覆盖、未暂存、未回滚这些内容。
- 决策：本计划记录的是需求和实施协议，不把编制中的任何 triplet 当作未来执行基线。ZR-001 必须在领取首个产品任务时重新冻结 HEAD、dirty allowlist、CodeGraph freshness和当前行为；若新代码已关闭某缺陷，只能经相同用户旅程证据标 `already_satisfied`，不能机械重复实施。

## 发现 030：计划自审发现并关闭三处依赖/门禁表达风险

- 原 ZR-605 未强制等待矿业 ADR，现已依赖 ZR-610；紫金 pilot ZR-609 还必须等待通用多矿 E2E ZR-611。
- 原 ZR-709 范围写法包含自身，现改为显式排除 ZR-709 的依赖集合，避免 DAG 自环。
- 原最终观察门低于动态计划要求，现统一为 7 次 Daily、2 次 Weekly、1 次 Monthly、1 次告警自检和一次真实 rollback/re-activate；自然时间不能人工豁免。
