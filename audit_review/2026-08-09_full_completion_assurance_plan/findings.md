# 三仓完全完成计划 — 基线发现

## 发现 1：计划必须区分四类“完成”

- 日期：2026-08-09
- 内容：组件存在、fixture 通过、生产数据迁移、用户链成功是四种不同证据，禁止相互替代。
- 影响：每个工作单元必须分别定义代码证据、契约测试、跨进程 E2E、真实 canary 和生产发布证据。

## 发现 2：当前目标不是局部补丁

- 日期：2026-08-09
- 内容：六项期望同时涉及架构切换、数据治理、下载事务、处理产物、CI/E2E 和代码退役。
- 影响：计划必须采用渐进重构、双读影子、明确 cutover 和可演练回滚，不能一次性替换生产链。

## 待核实

- 最新稳定 HEAD 与工作区状态。
- WU-904/WU-905 后 v2 assertion、运行时开关和 activation epoch 的真实关系。
- Dropbox、dayu-only、SourceBundle、latest 的最新生产调用者和真实样本状态。
- 当前 CI 对 sibling commit、真实场景、Windows 中文路径和 release receipt 的覆盖。

## 发现 3：稳定基线已锁定

- 日期：2026-08-09 21:36 Europe/London 后
- revenue-forecast：`main@3ce9cc4d3ea91b15aad42eff1f55b72a44834dd7`，本地与 upstream 一致；仅本计划目录为新增未跟踪内容。
- filing-fetch：`main@c9799b722a97376f9717bcfacfa0685135dcbd15`，本地与 upstream 一致且产品工作区干净。
- company-wiki：`master@109a1a6a77d7f4b37f849207fbd9e5d8caf2bc07`，本地与 upstream 一致；保留用户既有的 `llm_cost_log.csv` 修改。
- CodeGraph：三仓均已初始化且可用；revenue 114 文件、filing 17 文件、wiki 434 文件。
- 影响：后续实施必须以这三个 commit 组成的 compatibility triplet 为初始基线，禁止继续使用旧 release manifest 或 CI 中过期 sibling pin 作为验收证据。

## 发现 4：关键 v2 构件仍未成为生产调用者

- CodeGraph 在最新稳定 HEAD 上确认：`SidecarFilingAdapter` 无生产调用者。
- `query_source_bundle` 只有两个 contract test 调用者。
- revenue 的 `select_reusable_artifacts` 有 24 个调用者，但全部来自测试。
- `validate_flag_state` 与 `atomic_rollback` 只被 WU-905 审计脚本和测试使用，没有生产解析器/扫描器调用者。
- latest/gap 的“只下载缺失项、导入、重解析、第二次零下载”主要存在于纯 policy/contract tests，CodeGraph 未找到对应的生产编排入口。
- 影响：计划必须以“删除测试专用孤岛、接入唯一生产入口”为明确工作，而不是继续增加平行 helper。

## 发现 5：生产数据、运行时声明和验收回执不一致

- 生产 catalog 已有 v2 列与 16 条 active assertions，但 WU-905 同时记录 `activated=false`、`v2_resolve_active=false`、`legacy_bridge_enabled=true`。
- resolver 不读取 flag 或 current activation epoch，只筛选 `visibility_state IN ('legacy','active')`；因此 assertion 数据状态已能改变生产响应，而文档开关不能真实控制或回滚该行为。
- 16 条 active assertions 出现在 company_raw/dayu location set，Dropbox 仍为 0；active dayu 样本同时有 company_raw 位置，尚不能证明 dayu-only 等价复用。
- artifacts 共 7712 条，具有 source hash + schema binding 的为 0。
- scan_runs 历史为 155 `completed_with_errors`、15 `interrupted`、26 `completed`；当前 canary 只把真实根前后变化当错误，不把扫描健康恶化当失败。
- 影响：第一批实施必须先修复运行时控制平面和审计真相，不得继续扩大 active assertion cohort。

## 发现 6：配置接入仍停留在 legacy kind 模型

- production `source_catalog.yaml` 仍为 schema 1.0，通过 `reusable_root_kinds=[company_raw, dayu_portfolio, directory]` 放行整个 kind。
- scanner 仍直接分支 `company_raw/dayu_portfolio/directory`，并写入 `acquisition/dayu_meta` 两种 legacy 容器；v2 scanner 打开即 fail closed。
- filing-fetch 另存一份 `allowed_handle_roots`，形成重复的安全策略来源。
- 影响：必须把 root 是否可复用、使用哪个 adapter、允许哪些文档、只读/写入能力和路由全部下沉到单一版本化 RootPolicy snapshot。

## 发现 7：当前 CI/回执无法证明完整完成

- revenue CI 固定 filing `ad62592`、wiki `77669ae`；filing CI 固定 wiki `a42bb40`，均不是稳定基线 triplet。
- filing CI 排除 real-tool 与 real-download 测试，只执行 companies-root synthetic E2E。
- company CI 不执行 integration/acceptance、真实只读 canary、Dropbox/dayu-only 或三仓 E2E。
- 旧 release manifest HEAD 已过期，指向的 closure ledger 不存在；25 份 receipt 无通用 schema/admission validator，多份仍为 pending review。
- Windows 中文路径下的审计/测试子进程解码问题仍需列为 mandatory portability gate。
- 影响：动态审核必须重建为以当前 triplet、场景矩阵和机器可解析证据为中心的发布总门。

## 发现 8：仓库职责边界可保留，但接缝必须收敛

- filing-fetch 产品代码主体只有 `scripts/fetch_filing.py` 与 `scripts/filing_contracts.py`，适合继续保持薄编排器，而不应复制 catalog/root/admission 逻辑。
- revenue 的接缝集中在 `filing_fetch_client.py`、`source_preparation.py`、`company_wiki_source.py`，适合作为最终消费者 E2E 总入口。
- company-wiki 的 source_catalog 是复杂度中心，应独占 RootPolicy、adapter、normalized metadata、resolver、artifact bundle、activation epoch 和 catalog migration。
- 影响：计划不新建第四套规则引擎；跨仓动态总门由终端消费者 revenue 编排，各仓只维护自己拥有的契约与测试。

## 发现 9：已有测试资产丰富，应升级而非推倒重来

- company-wiki 已有 adapter/root policy/assertion/visibility/resolver/bundle/gap/download/rollback/capacity 等 contract tests，可作为重构护栏。
- filing-fetch 已有 isolated-wiki、real-tool、real-download 和 bundle 兼容测试，但 CI 覆盖层级不足。
- revenue 已有 source preparation、bundle selection、artifact invalidation 和 engine E2E 测试，但部分“E2E”只是组件级字典测试。
- 影响：实施应保留行为正确的现有测试，先把已知缺口测试从“期望 MISSING/仅类型断言”改为真正 RED，再接生产调用链；禁止靠删除或放宽测试获得绿色。

## 发现 10：计划结构自审已闭合，但不能替代实施证据

- `task_plan.md` 定义 16 个阶段，其中 Phase 0 只代表计划和基线完成；Phase 1–15 仍全部待实施。
- 计划拆分为 71 个 FC 工作单元，并用 `execution_matrix.md` 固化主链依赖、授权边界、放行包和停线条件。
- `scenario_matrix.md` 定义 63 个强制场景，覆盖精确复用、Dropbox、缺失/最新下载、衍生工件、安全失败、控制面、运维和 Windows 中文路径。
- 六项目标均有责任阶段、测试层级、证据要求和 Phase 15 终局验收；任何 `pending`、真实层 `skip`、陈旧收据、短哈希、仅 mock 证据或生产旁路都会阻止关闭。
- 影响：这份计划足以约束较弱模型按小步执行和停线，但“计划完整”不等于“问题已经消除”；必须完成全部工作单元并通过真实证据总门，才能作出完成结论。

## 发现 11：交付前结构校验通过

- 2026-08-09 最终只读校验确认：16 个 Phase、71 个 FC 工作单元、63 个 mandatory scenario 与计划声明一致。
- `task_plan.md` 引用的六份配套 Markdown 文件均存在；另有 `plan_self_audit.md` 记录计划层自审。
- 三仓 HEAD 仍与 upstream 一致；filing-fetch 无工作区变化，company-wiki 只保留用户既有的 `llm_cost_log.csv` 修改，revenue-forecast 只新增本计划目录。
- 抽样检查 FC-101/201/301/501/1001/1501 证实工作单元以具体契约、目标文件/调用链、测试或场景和可证伪验收为核心；其余单元受 `implementation_runbook.md` 的统一工作卡及证据要求约束。

## 发现 12：最新要求需要从“完整计划”进一步加固为“不可跳步执行包”

- 日期：2026-08-09。
- 用户再次明确要求较弱模型也不能因理解偏差跳过测试、检查点或审计，并且每个小项未真正实现就不得进入下一项。
- 当前主计划已经具备阶段、工作单元、场景、全局门禁和发布波次，但实施交接仍可继续增强：为每个 FC 工作单元生成统一可填写的执行清单，明确入口/出口状态机、允许文件、禁止动作、RED 证据、测试层级、负向测试、产物路径和独立审查签字。
- 影响：本轮只补强计划的执行约束、追踪矩阵和验收模板，不改变产品设计目标，也不实施产品变更。

## 发现 13：实施手册仍有可导致弱模型误解的命名与交接缺口

- 主计划统一使用 `FC-*` 标识，但实施手册的模板和 receipt 示例仍写成 `WU-X`；虽然语义可推断，弱模型可能创建两套编号或无法与 closure gate 一一对应。
- 当前 14 步生命周期很严格，但尚缺少一张包含全部 71 个 FC 的机器式状态登记表；实施者仍需从长篇主计划自行推导 owner、依赖和证据入口。
- “独立 reviewer”需要更明确的隔离条件：干净 checkout、不同会话/代理、不能复用实现者工作区与主观摘要，并需要单独的 reviewer receipt。
- “运行完整 CI 等价命令”仍是计划目标而非冻结命令；在 Phase 1 之前必须先建立 command registry，否则弱模型可能自行选择较小测试集并宣称等价。
- 影响：需要新增 FC 级验收登记表、测试/命令注册规则和独立审查协议，同时将手册的 `WU-X` 全部收敛为 `FC-*`。

## 发现 14：现有 63 场景覆盖主功能，但真实文件生命周期和审核自证还可加深

- 已有矩阵对 exact、Dropbox、download/latest、artifact、identity、安全、控制面、运维和跨平台覆盖较强。
- 尚可显式固化三类经常在真实使用中出现、但弱模型容易忽略的情况：索引陈旧/文件移动删除/损坏或锁定；从 revenue 用户入口发起的完整组合旅程；动态审核系统自身的漏报、过期证据、权限失败和版本升级兼容。
- T2 的“零写入”需要精确定义为“生产 catalog 和三个真实 source roots 零写入”；审计报告可以写入隔离的 audit output，否则实施者可能误解为 T2 完全不能生成证据。
- 影响：场景矩阵应增加 IDX、UJ、AUD 三组场景，并把新增数量、负责人和消费阶段同步到主计划、执行矩阵和 closure gate。

## 发现 15：r2 hardening 一致性校验通过

- 当前计划目录共有 14 份 Markdown；主计划 16 个 Phase、71 个 FC，与 `work_unit_registry.md` 的 71 项完全一一对应，无缺失或额外编号。
- 场景矩阵已从初版 63 项扩展为 95 项；95 个 ID 无重复，新增 IDX、UJ、AUD、MIG 四组覆盖 index/文件生命周期、组合用户旅程、审核自证和迁移恢复。
- 全部 Markdown 相对链接有效。旧 `WU-X` 和“63 场景”字样只存在于 findings/progress 的历史发现记录，不存在于当前操作性协议、模板或主计划。
- 三仓 HEAD 继续与 upstream 一致；filing-fetch 仍干净，company-wiki 仍只有用户既有 `llm_cost_log.csv` 修改，revenue 只新增本计划目录。
- 影响：r2 计划可以交付审阅；所有产品实施阶段保持 pending，不能把计划层校验误当成功能验收。

## 发现 16：历史计划并非只有一个目录，需要建立统一状态账本

- 日期：2026-08-09。
- revenue-forecast 除 r2 计划外，还有仓库根 `task_plan.md`、`IMPLEMENTATION_PLAN.md`、`review_audit/`、`audit_review/` 根计划、`2026-08-08_adversarial_plan/` 和 `2026-08-09_data_lake_refactor_plan/`。
- filing-fetch 有仓库根 `task_plan.md`；company-wiki 有根级 `task_plan.md`、`task_plan_v2.md`、recovery/review/verification 计划以及 `docs/plans/` 下四组活跃形态计划，另有明确 `docs/archive/` 历史文档。
- data-lake 旧计划包含大量 WU receipts、release manifest 和 closure mapping；不能因文件存在或 receipt 名称像“完成”就自动判定完成，必须核对当前 triplet、生产调用链和证据新鲜度。
- 影响：需要先创建跨计划 inventory/crosswalk，区分“当前主计划”“已完成历史”“被 r2 取代”“仍有独立价值”“阻塞/证据失效”，再回写各活跃计划的顶部状态，避免逐文件凭印象勾选。

## 发现 17：初步状态摘要暴露“标题完成、清单未完成”的历史漂移

- revenue 根 `task_plan.md` 首页声称 13 Phase 全部完成，但仍有约 387 个未勾选项，并且内部已将至少一个“名义完成”阶段 reopen；该文件不能继续把首页总状态当权威完成证明。
- `review_audit/roadmap.md` 仍写“待批准，未实施”，但配套 `IMPLEMENTATION_PLAN.md` 已把 R0–R9 多数标记 completed，说明两份镜像未同步。
- company-wiki 的 `portfolio-reuse-fix` 首页称整体完成、Phase 7 默认跳过；随后 `portfolio-reuse-automatic` 采用 Strategy B 并称完成，旧 Phase 7 应被明确标为由后续计划 superseded，而不是长期 pending。
- company-wiki `catalog-space-remediation` 首页/阶段称全部完成，但正文仍保留大量未勾选设计清单；需要区分“历史执行结果已完成”与“模板/设计清单未回填”，并以 receipt/当前验证决定是否保持 completed。
- 明确位于 `docs/archive/`、`.recover-*` 或 `.mimocode/plans/` 的文件应登记为 archived/reference，不应重新激活其中的旧待办。

## 发现 18：旧 data-lake 计划不能按 receipt 文件存在批量标完成

- 旧 `2026-08-09_data_lake_refactor_plan/task_plan.md` 的 Phase 4–15 仍显式为 pending，runbook 只是 `runbook_complete_ready_for_review`；这与“计划写完”而不是“产品做完”一致。
- 目录中虽有 WU-101/102/104、201~205、301~305、902~906、1303~1306、1500/1503/1505 等 receipt 或工具产物，但最新生产审查已经证明 SidecarAdapter、SourceBundle、artifact selector、runtime flags/rollback/latest 等关键构件仍缺生产接线或证据相互矛盾。
- 因此这些旧 WU 最多只能标记为 `superseded_partial_evidence` 或“历史产物已生成但未满足当前验收”，不能把有 receipt 的 WU 自动升级为 completed。
- 旧计划的设计内容大部分被 r2 的 FC-201~1505 吸收并收紧；继续执行旧 WU 会造成两套状态机、场景编号、receipt schema 和发布门并存。
- 影响：旧 data-lake 主计划/runbook/进度应整体标为 `superseded_by_FCAP-r2`，保留证据只供迁移复核；其中仍必要的功能条目映射到 r2 FC，不再作为独立 pending 队列。

## 发现 19：审查型计划与产品实施计划必须分开记账

- `audit_review/task_plan.md`、`review_audit/task_plan.md` 和 `2026-08-08_adversarial_plan` 中打勾的是“完成审查/输出计划”，这些 scoped activities 可以保持 completed；其中产品 WU 明确仍 pending，不能因审查清单全勾而推断产品完成。
- `review_audit/roadmap.md` 的“待批准未实施”已被后来的 `IMPLEMENTATION_PLAN.md` 和稳定提交部分取代，但最新审查表明 R1–R9 的历史完成并未覆盖新的 data-lake/Dropbox/真实复用终局标准；两者都应转为 historical/superseded，而不是继续作为当前执行入口。
- `review_audit/task_plan.md` 唯一未勾项“用户裁定后开始实施”已失去独立意义：后续实施已经发生，且剩余目标进入 r2；该项应取消并注明 superseded，而非长期未完成。
- revenue 根 `task_plan.md` 具有长期追加账本性质。已勾的历史阶段保留 scoped completed；Phase 18/19 等仍开着的 identity、诊断、CLI/文档项目若与 r2 重叠，应转移到 FC-702/704/802/1205，原项标 superseded；不属于三仓 data-lake 目标的 revenue 独立 backlog 则降低优先级而非删除。

## 发现 20：company-wiki 子计划需要差异化处置

- 根 `task_plan.md` 和 filing-fetch 根 `task_plan.md` 的勾选历史任务可保留为“当时范围完成”，但最新终局审查已经否定它们对当前六目标的充分性；需要顶部状态声明当前工作转交 r2。
- `core-section-extraction` 的 13 项全部勾选，且目标是独立章节抽取能力；可保持 `completed`，仅降为 maintenance，不纳入 r2 关键路径。
- `portfolio-reuse-fix` 的 Strategy A 已完成后被回滚/替代，其 Phase 7 不应保持 pending；整份计划应关闭为 `superseded`，Phase 7 由后续 Strategy B/r2 吸收。
- `portfolio-reuse-automatic` 的 Strategy B 在其“dayu 配置驱动复用”窄范围可视为历史完成，但最新调查证明它没有实现任意 root/Dropbox 的完全泛化；应标 `completed_historical_scope + superseded_for_generalization`。
- `catalog-space-remediation` 首页“全部完成”与 Phase 5/6 pending、42 个未勾项冲突。已落地的 Phase 1–4 保留 completed；存储迁移 Phase 5 改为 conditionally_deprioritized（仅容量/SLO 触发），Phase 6 的持续验收转入 r2 FC-1302~1304/1504，旧独立队列关闭。

## 发现 21：company-wiki 的历史/复核文件已有结论，但状态行没有收口

- `task_plan_v2.md` 和 `review_plan.md` 顶部已经明确“历史计划/历史审查清单，不再执行”，其未勾项应统一视为 `cancelled_by_boundary/superseded`，不应保留为待办数量。
- `task_plan_cw_recovery_20260725.md` 是从会话恢复旧文本的草稿，且明确根 `task_plan.md` 是唯一活动计划；其中恢复任务和旧 pending 范围应标 archived/reference，不能与 r2 竞争执行优先级。
- `verification_CW-2.24_plan.md` 的 Phase 2 仍写 in_progress、若干清单未勾，但后文已经给出基于代码/生产/测试的逐项完成结论；这些复核项应补勾为 completed。其“index.md 人类视图”和 semantic near-duplicate 是可选后续，应分别降级为 P3/转入独立 backlog，不影响 r2 主线。
- filing-fetch 根 `task_plan.md` 六阶段和 75 项全部勾选，适合作为 v1.3.0 窄范围历史完成记录；最新 r2 发现的 latest、统一 resolver、Dropbox、动态审核等是新增/收紧目标，应在顶部声明由 r2 继续，而不是篡改旧完成证据。

## 发现 22：当前代码结构再次证明旧计划只能作为历史证据

- 三仓 CodeGraph 索引健康且规模与 r2 基线一致：revenue 114 files/1957 nodes，filing 17/437，wiki 434/8838。
- `SidecarFilingAdapter` 仍没有调用者；`query_source_bundle` 仍只有 2 个 contract test 调用者；revenue 的 `select_reusable_artifacts` 24 个调用者仍全部来自 tests。
- `validate_flag_state` 和 `atomic_rollback` 仍只被 WU-905 检查脚本与测试使用，没有 resolver/scanner/bundle 生产调用者。
- 影响：任何历史计划中“Dropbox/SourceBundle/artifact reuse/runtime rollback 已完成”的广义叙述都必须限定为组件或窄范围历史完成；当前终局状态仍由 r2 的 FC-201~1505 管理。

## Errors encountered（本轮计划对账）

| 日期 | 错误 | 尝试 | 处理 |
|---|---|---|---|
| 2026-08-09 | PowerShell 在 `foreach (...) { ... } | ConvertTo-Json` 处报 `An empty pipe element is not allowed` | 1 | 不重复原命令；下一次先赋值到数组变量，再单独 `ConvertTo-Json` |
| 2026-08-09 | 批量加状态覆盖时误写旧 data-lake 计划标题，`apply_patch` 找不到上下文 | 1 | 将补丁拆分；其余计划先成功更新，再读取真实标题 `多根 Filing Data Lake 解耦与端到端闭环` 后单独处理 |
| 2026-08-09 | company-wiki 多文件状态补丁在 catalog-space 首行上下文失败（文件编码/首行匹配差异） | 1 | 拆分补丁；其余 8 个计划先更新，再以稳定的第二行状态作为上下文单独更新 catalog-space |
| 2026-08-09 | 六份旧 progress 批量补丁再次在 catalog-space 首行上下文失败 | 1 | 不重复整批；先更新其余五份，再用第二个 `## 2026-08-06` 标题作上下文单独插入状态，成功 |
| 2026-08-09 | revenue `git diff --check` 发现两处新增 Markdown 行尾空格 | 1 | 精确移除旧 data-lake task/runbook 状态行尾空格；未做全文件格式化，避免噪声 diff |

## 发现 23：旧 data-lake 目录自身只是计划编制完成

- 旧主文件顶部明确 `plan_complete_ready_for_review_v3`，其 Phase 0 代表目标/计划完成；后续大量功能清单未勾。
- 旧 progress 明确写“当前仅开展计划编制；未修改产品代码、配置、测试、生产 catalog 或真实资产”，随后虽有部分 receipt/工具增量，但不能反向把主计划所有功能标完成。
- 影响：该目录顶部统一覆盖为 superseded 最符合事实；progress 追加停止旧 WU 队列说明，不能逐个把 64 个旧工作单虚假勾成完成。

## 发现 24：catalog-space 的真实进度允许精确拆分，而非整体“完成/未完成”

- progress 证明 Phase 1.1/1.2 已完成：9,578 文档四路对账、生产退役 9,499、stub 删除 77、mismatch=0，并有 receipt。
- Phase 2.1 已归档 25,708,956 evidence rows 且行数对账一致；Phase 2.3 prune 工具和 90 天保护已实现，当前因未到期正确拒绝回收；2.2 采用 ADR-009 的替代设计而非新增 `archived_at`。
- Phase 3 已交付粒度提案，Phase 4 已交付 `size-report` 并在 49.27GB 生产 catalog 运行；Phase 6 的 ADR/文档收尾完成。
- 用户 D4 明确“不迁 D:”；因此旧 Phase 5 存储迁移应标 `cancelled_by_D4`，未来若容量/SLO 触发只能重新立项，不能保持 pending。
- 连续四周增长率、长期健康/SLO 属持续运维而非旧一次性收尾，转入 r2 FC-1302~1304/1504；旧计划整体应标 `completed_historical_scope_with_transferred_monitoring`，不是笼统全部完成。

## 发现 25：状态覆盖已消除主要入口歧义，仍需处理一个旧延期项

- 已检查 18 个主要非归档计划入口：全部已有明确最新状态或已更新原状态行；CW-2.24 verification 从 3 个 Phase 中的漏勾状态回填为 10/10 完成。
- filing-fetch 根计划和 company-wiki 根/core-section 保留历史范围 completed；旧 review/audit/data-lake/portfolio/recovery/v2 计划已经明确停止、取消或转入 r2。
- `IMPLEMENTATION_PLAN.md` 仍有一项 `verify_plan_claims 进 CI：推迟到 R8` 未勾；后续仓库已经出现对应 verifier/CI 资产，但 r2 要求重建 current-triplet/receipt/scenario 总门。因此该旧项应标 `superseded`，不能继续 pending，也不能以旧实现直接宣告当前完成。
- 历史计划仍保留空复选框是为了不篡改原执行证据；每个文件顶部覆盖和 `legacy_plan_disposition.md` 已对这些空框作集合级处置。活动待办统计只能读取 r2 registry，不能再把旧空框相加。

## 发现 26：最终结构与工作区范围校验通过

- 当前 r2 目录共 15 份 Markdown；16 Phase、71 个 task FC 与 71 个 registry FC 集合完全一致；95 个 scenario 无重复；内部链接无缺失。
- 18 个主要非归档历史计划入口全部已有最新 disposition；`IMPLEMENTATION_PLAN.md` 和 CW-2.24 verification 的活动空框均归零。
- 三仓 HEAD 仍与 upstream 一致。本轮 tracked diff 除 company-wiki 用户既有 `llm_cost_log.csv` 外全部是 `.md`；没有产品代码、配置、数据库、测试或 CI 修改。
- 行尾检查首次只发现两处本轮 Markdown trailing whitespace，已精确修正；CRLF 提示是 Git 工作区换行提示，不是内容错误。

## 发现 27：portfolio-automatic 的原空框属于被放弃的 Strategy A，不能伪勾为完成

- 其 progress 明确：2026-08-04 初稿 Phase 0–6 是 `ensure` 自动提升 Strategy A，当时“全部实施阶段均 pending”；随后用户改选 Strategy B，并显式移除自动提升 hook/开关/测试。
- Strategy B 实际完成项是配置化 reusable roots、dayu metadata enrichment、identity 归一、filing handle root 配置、陈旧防护、真实 dayu-only 零下载 E2E、ADR/OPERATIONS/SKILL 文档，以及后续普通重扫 re-enrich 和 busy_timeout 收尾。
- 因此不能把原 38 个 Strategy A 空框批量改成 `[x]`；正确做法是把原 Phase 0–6 全部标为 `cancelled_by_Strategy_B`，并新增一组 Strategy B 的实际 `[x]` closure checklist。泛化不足继续转 r2。
- 影响：计划状态既满足“完成项明确勾选”，又不会错误声称被回滚的自动提升功能存在。

## 发现 28：company-wiki 三份历史计划位于 `docs/plans/`，不是仓库根部 `audit_review/`

- 最终归并时首次按旧审计目录猜测路径，三个 `rg` 均返回“系统找不到指定的路径”。
- 随后用 `rg --files -g "task_plan.md"` 定位到实际文件：`docs/plans/portfolio-reuse-fix/`、`docs/plans/portfolio-reuse-automatic/`、`docs/plans/catalog-space-remediation/`。
- 后续只使用已解析出的精确路径，不再依赖目录名猜测。

## 发现 29：历史状态归并和当前计划结构已形成可机器核验的单一真相

- 18 个主要非归档计划入口均在前 15 行内包含最新状态；归档/恢复文件由 `legacy_plan_disposition.md` 集中登记，未篡改历史证据。
- FCAP r2 当前保持 15 份 Markdown、16 个 Phase、71/71 个一致的 FC、95/95 个唯一场景；内部 Markdown 链接缺失为 0。
- registry 明确只有 FC-000~002 三项“计划基线”完成，剩余 68 个产品 FC 全部 pending；旧计划中的空框已集合级处置为取消、取代、归档、降级或转入 r2，不再计入活动 backlog。
- 三仓 `git diff --check` 均通过；除 company-wiki 用户既有的 `llm_cost_log.csv` 外，本轮变化全部是 Markdown 计划/进度文档。

## 发现 30：FC-101 已实施 —— 七契约单一所有权注册表 + 守卫测试 + ADR + 消费者声明

- 交付物（纯新增，未触碰任何产品代码/配置/数据库/CI）：
  - `revenue-forecast/compatibility/contract_registry.json`：机器可读单一所有权源，七个契约各一 owner（company-wiki），含 version/introduced_by_fc/consumed_by_repos/N-1/compat_window/deletion_deadline/canonical_doc_path。
  - `revenue-forecast/compatibility/contract_registry.py`：stdlib-only loader + validator（`validate(data)->list[str]`），供测试与后续 FC-103/104 复用。
  - `revenue-forecast/tests/test_contract_registry.py`：RED→GREEN 守卫，4 个一致性用例 + 5 个 mutation oracle（拒第二 owner 列表、owner 自消费、缺删除期限、短 hash、闭合集外契约）。
  - `company-wiki/docs/adr/ADR-010-fcap-contract-ownership.md`：owner 声明 ADR（遵循 ADR-001~009 格式、引用 scope note、声明 schema/兼容窗口影响）。
  - `filing-fetch/references/contract-ownership.md`：消费者声明（薄编排边界、禁止第二策略源）。
- TDD 纪律：先写测试跑出 RED（注册表不存在，9 failed）→ 创建数据/ADR/声明 → 9 passed GREEN → mutation oracle 全部命中。
- 范围澄清：FC-101 的 RED 测试是**注册表内部一致性**（单 owner/闭合集合/版本+兼容+删除期限）。跨仓"代码无第二策略源"的 AST 门属 FC-205/705/1201（旧 legacy 代码仍在，现在扫必然红），不在 FC-101 scope。
- 剩余收尾：三仓 ADR/registry hash 写入 triplet manifest 由 FC-104 完成；本 FC 的 `accepted` 状态受 honest-implementer 模式约束，停在 `independent_review`，待独立 reviewer。
- 影响：契约所有权靶心冻结，后续 FC-201~905 在不变版本号上接线；receipt validator（FC-103）落地后可机器拒绝伪 owner / 第二策略源。

## 发现 31：`tools/tests/test_audit_baseline.py` 既有 Windows 编码失败（PORT-01，归 FC-1205）

- revenue 全量 `pytest tests/ tools/tests/` 结果：371 passed / 1 failed；唯一失败是 `AuditBaselineTests::test_collects_baseline_facts`，报 `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd4`（子进程读取阶段，GBK/OEM 字节）。
- 已确认非 FC-101 回归：FC-101 未修改 `tools/audit_baseline.py` 或其测试（`git diff HEAD` 为空），失败在隔离单测中同样复现；根因是子进程输出含中文用户名路径字节，被强制 utf-8 解码失败 —— 即计划已登记的 PORT-01「Windows 中文路径 subprocess UTF-8 失败」。
- 按 `command_registry_plan.md` §3，该命令登记为"现状 finding"而非 required-green；修复 owner = FC-1205（统一错误 schema + UTF-8 stdio + Windows OEM/locale 边界）。
- 影响：FC-101 的 repo-green 基线记为"除既有 PORT-01 失败外全绿"；不影响 FC-101 验收（FC-101 是纯新增、与 audit_baseline 无调用关系）。

## 发现 32：FC-102 已实施 —— 95 场景机器可读 registry + 完整性 validator + 覆盖门基础

- 交付物（revenue-only，纯新增）：
  - `compatibility/scenario_registry.json`：95 个 mandatory scenario，每条按声明层级分解为独立 tier entry（T1/T2/T3/T4 不可互相替代），含 owner_fc、process_count、fixture/sample(pending:FC)、oracle、side_effect budget、timeout、freshness、evidence path。
  - `compatibility/scenario_registry.py`：loader + validator（结构、闭合 95、tier 分解、跨进程 process_count>=3 防假 E2E、side-effect key 白名单）。
  - `tests/test_scenario_registry.py`：硬编码 95 个预期 ID 强校验 registry↔matrix 一一对应 + 5 一致性 + 6 mutation oracle。
- TDD 真实 RED：首轮 validator 把 T0/T1 合法的 `freshness_window=None` 误判为 missing → 修复为允许 None → GREEN。该 RED 命中目标行为（validator 过严），非环境问题。
- 范围澄清：FC-102 交付 registry + 完整性 validator + 覆盖门基础。"每个 mandatory ID 都有真实跨进程测试覆盖"的硬门属 FC-1003（Phase 10），现在多数测试尚未存在，故硬门未启用；FC-102 的覆盖工具软报告、Phase 10 转硬。
- 影响：场景语义单一源建立；后续 FC-505/803/904/1003 等按 registry 登记测试，coverage gate 可机器核验"无遗漏/重复/矛盾/假 E2E"。

## 发现 33：FC-103 已实施 —— receipt/closure validator（schema 2.0）+ can_accept 门

- 交付物（revenue，纯新增）：
  - `tools/receipt_validator.py`：schema 2.0 校验器，遵循 verify_closure_ledger 模式。两级判据：`validate_receipt`（结构：schema/fc_id∈71 闭集/triplet 40-hex/plan+policy+command hash/changed⊆allowed/命令 exit=0/无 skip 场景/implementer≠reviewer/非未来时间/mutation killed）；`can_accept`（更严：结构 OK + 真实封印无 pending-fc-104 + 独立 reviewer accepted + 非未来时间）。
  - `tools/tests/test_receipt_validator.py`：1 正向 + 16 负向 mutation（短 base/result/plan/policy/command hash、占位 policy、fc_id 越界、changed 越界、命令 exit≠0、skip/xfail 场景、mutation 存活、伪 reviewer=implementer、未来时间、accepted 空 reviewer、缺 reviewer hash）+ 3 个 can_accept 门 + 旧不完整 receipt 拒绝 + FC_IDS=71。22 passed。
- 实战验证：对真实 FC-101 receipt，`validate_receipt` 返回 OK（结构合法），`can_accept` 正确拒绝（pending-fc-104 封印 + decision 非 accepted）—— validator 按设计把 FC-101 锁在 independent_review，honest-implementer 模式被机器强制。
- TDD 说明：validator 模块先写，自审发现 `_triplet_problems` 一处 walrus 笔误已修；负向 mutation suite 即 RED-oracle 证明（每个坏 receipt 被拒）。
- 范围：closure ledger 的生成入口已就位；旧 25 份不完整 receipt 因缺 schema 2.0 字段被结构性拒绝（`test_legacy_incomplete_receipt_is_not_accepted`）。
- 影响：所有后续 FC receipt 现在可被机器校验；accepted 状态只能由独立 reviewer 通过 can_accept 推进，封印待 FC-104。
