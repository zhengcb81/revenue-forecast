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

## 发现 34：FC-104 已实施 —— current compatibility manifest + 冻结 command registry

- 交付物（revenue，纯新增）：
  - `compatibility/current.json`：manifest（remotes、frozen_baseline_triplet、current_triplet、contract versions、Python/platform matrix、三个 registry sha256）。
  - `compatibility/command_registry.json`：10 条真实命令冻结（revenue.unit/full/e2e/sync/receipt、filing.unit/e2e/sync、wiki.unit/integration），含 argv/tier/timeout/write/network/collected 基线；wiki 命令诚实标 `pending-first-measurement`（尚未在 fcap 分支测量，不臆造）。
  - `compatibility/compatibility_manifest.py`：loader + validator。两个硬门：① 三个 registry hash 篡改检测；② frozen_baseline 后代不变量（每仓 HEAD 必须是冻结基线或其后代，sibling reset 即红）。
  - `tests/test_compatibility_manifest.py`：19 passed（manifest 5 一致性 + 7 篡改/回归 mutation + command registry 6 结构 mutation + pending 诚实性）。
- TDD 真实 RED：command registry 用真实仓名（revenue-forecast/filing-fetch/company-wiki），validator 首版按 triplet 键（revenue/filing/wiki）校验 → 修复 validator 用 VALID_OWNER_REPOS → GREEN。
- 设计说明：manifest 的 current_triplet 是信息性（as-of FC-104 authoring）；真正的门是 frozen_baseline 后代不变量 + hash 篡改检测，避免"manifest 钉住自身提交"的鸡生蛋问题。
- 影响：Phase 1 契约/治理四 FC 全部到 independent_review。command_registry 冻结后，FC-101/102/103 的 receipt 中 `pending-fc-104` 封印可由后续 FC 的 re-validation 补齐（can_accept 才可能通过）。

## 发现 35：FC-704 —— 由 handle 推断 download_calls 的伪回执已修复（scenario_matrix §2 落地）

- 原 `scripts/source_preparation.py` 用 `"download_calls": 0 if handle else 1` 从 handle 存在性倒推下载计数——scenario_matrix §2 明令禁止（计数必须来自事件/journal）。
- 修复：ResolutionEnvelope（resolve/ensure CLI 输出携带 journal 对账 outcome + download_events + policy_hash/activation_epoch + bundle_status=unavailable）；filing-fetch 深度校验并原样转发；revenue receipt 从 envelope 证据推导，envelope 缺失 fail closed（RuntimeError，绝不静默 0）。
- 教训：receipt 的每个计数必须能指回事件来源；"看起来合理"的推断在审计链上就是伪证据。

## 发现 36：FC-705 —— legacy bridge 关闭门（completed-window 语义）

- 初版 close_gate_allowed 把"最后两个周期"含 open 周期（永无 ended_at）→ 门永远不可达（reviewer F1 off-by-one）。修复：只统计已完结窗口；leg10g 簿记流模拟测试钉住。
- 现场证据：current-state 周期 3/4 hits=6（诚实计数，门关）；cutover drill（v2 + bridge off）canary 4/4 REUSED_EXACT 且 zero bridge hit——cutover 就绪。
- 教训：时间门逻辑必须用真实簿记流（新周期关闭旧周期）模拟测试，不能只测纯函数理想输入。

## 发现 37：FC-802 F1 —— mock 测试掩盖真实 CLI 边界断裂（三类缺陷之一）

- reviewer 用真实 CLI 复现：ensure 子解析器缺 `--mode`（每个 latest_as_of 调用 parse 期失败）+ main() 把结构化 gap 包装成 capture_ready handle——我的 mock 测试全绿。
- 修复：ensure 加 --mode + main() gap 直通；现场端到端验证（真实 catalog：latest_as_of 紫金矿业 → status=gap）。
- 教训：跨进程集成断言必须至少一次跑真实 CLI 边界；mock 的 CompletedProcess 会掩盖 parse/arg 契约断裂。

## 发现 38：FC-803 —— T1 跨进程 spy 链抓出 3 个 mock 测不到的真实缺陷

- ① close-gap step-3 未绑定 missing candidate：无 fiscal_year 的 exact 请求复用旧期文档而从不补 gap（LT-09 二次零下载契约在真实 flow 下失败）；② close-gap 子解析器缺 --allow-acquisition-while-paused/--worker-config（parse 期断裂）；③ staging 清理用错 request id（DL-07 leftovers，全量 wiki suite 抓出 FC-801 cg04 回归）。
- 方法论：IsolatedWiki + tests/e2e_support/spy_adapter.py（真实 json_command_v1 子进程，SPY_ADAPTER_LOG/FIXTURE/FAULT env）——全真实子进程链，provider 调用计数来自 spy log。
- 教训：T1 层（真实跨进程 + spy provider）是 CLI/编排层契约的合格测试层；T0 mock 无法覆盖。

## 发现 39：FC-805 —— CN adapter 强制 fiscal_year，year-less latest discovery 一直静默失败

- 真实 cninfo adapter 的 discover 强制 fiscal_year；无年份的 latest_as_of 发现对真实 provider 一直失败（静默 provider_unavailable）——此前现场 latest 运行从未真正完成 CN 发现。
- 修复：gap-plan 发现请求从 as_of 推导最新已完成期（annual reports，12 月年结日历：as_of.year - 1）。
- 验证：真实 T3 三市场下载全绿（CN 紫金矿业 71s、HK 腾讯、US Apple），bytes hash 逐字节验证 + 二次零下载；M1（hint 移除）3.4s 现场击杀。
- 教训：真实 provider 契约与计划语义之间的隐性缺口只有 T3 真实调用能暴露——provider 的"required"字段是发现层契约的一部分。

## 发现 40：测试纪律教训汇总（FC-802~805）

- ① 回归测试不能是死代码：FC-802 r2 的 F1 回归测试追加在 `unittest.main()` 之后从未收集——测试必须可收集且 mutation 可击杀。
- ② os.environ 泄漏：一个测试设置 SPY_ADAPTER_FAULT 后未清理，污染后续测试——setUp 中显式 pop。
- ③ IsolatedWiki 的 seed_market 只写文件不建索引——必须显式 `wiki.scan()` 才能被 catalog 解析。
- ④ 手工写 receipt 哈希反复出错（FC-503/702/705 F2/801/804/805 共 6 次）——永远 `git rev-parse`，禁止从记忆重建。

## 发现 41：FC-901~905 会话教训汇总（Phase 9 前五个工作单元）

- ① **跨 FC 契约迁移会留下死字段上的旧测试 fixture**：FC-902 把 SourceBundle 从 handle.source_bundle 移到 resolution_envelope.bundle，18 个 WU-5.4 时代测试仍用旧字段（全量套件 18 红）。新 FC 必须 grep 旧字段的**所有消费者（含测试 fixture）**，不只改生产代码。
- ② **变异触发器类 DDL 必须整体删除**：FC-905-a M3 首次变异只改触发器名（trg_artifact_producer_event → trg_disabled_*），触发器仍然存在并生效——变异无效。整体删除 DDL 块才是有效变异。
- ③ **SQLite journal/触发器绝不能阻挡生产写入**：producer_events 表最初带 document_id FK，导致 focus_cleanup 删除孤儿文档时 IntegrityError（4 个测试红）。追加式历史 journal 无 FK——trace 绝不能破坏它记录的工作流。
- ④ **DAG 祖先遍历方向**：FC-904 `_dag_ancestors` 初版把"current in parents"（current 是子角色）当成祖先——方向反了。正确：`ROLE_DEPENDENCIES[role]` 直接给出父列表，传递遍历。REUSED_EXACT vs REUSED_EQUIVALENT 断言要用 `in (...)`（seed 公司常解析为 equivalent）。
- ⑤ **envelope 新字段的 N-1 归一化**：FC-903/905-b 的 validate_resolution_envelope 对缺失字段归一化为显式诚实默认值（bundle_status→unavailable、prompt_injection_status→not_reviewed、counts→None），在副本上改（输入 dict 不动）——"绝不伪造"是跨 FC 的贯串不变量，M4 类变异（伪造 not_detected）必须被击杀。
- ⑥ **str.count 子串陷阱**：批量改测试 fixture 时，8 空格模式是 12 空格行的子串——先替换更具体的（12 空格），再替换 8 空格，并用断言核对数量。
- ⑦ **安装同步是提交门禁**：revenue 提交前 `tools/sync_installations.py --apply`（MATCH 99 files）、filing 提交前 `tools/sync_installs_b3.py`（MATCH 27 files）——漏跑则 pre-commit R4.2 阻断。
- ⑧ **reviewer 环境差异**：FC-904 reviewer 在 worktree 布局下 12 个 sibling-layout 测试失败（base 相同集合=零新失败）；FC-905-b reviewer 用目录 junction 解决。receipt 数字注明主树环境；环境失败以"base 相同"为准。

## 发现 42：FC-905-a/b 关键设计决策

- **producer_events 触发器方案**：AFTER INSERT ON artifacts 触发器自动 journal（role→type：normalized/sections→parser、summary/consumer_analysis→llm），零 producer 代码改动、不可绕过——比显式 helper 调用更健壮（不会忘）。
- **prompt_injection review receipt**：documents.metadata_json["prompt_injection_review"]（status/reviewer/reviewed_at/evidence_sha256），写者 fail-closed 校验；envelope 读取，缺席→显式 not_reviewed。
- **消费侧政策**：revenue source_preparation 遇 not_reviewed → RuntimeError 阻断（未审核永不备料）；parser/llm 计数缺席 → fail closed（永不伪造 0）——E2E fixture 文档需带 review receipt 才能过政策门。

## 发现 43：FC-906 预飞——生产 artifact 全量不可绑定（FC-901 生产 dry-run 首跑，7718→0 bindable）

- **背景**：FC-901 receipt 只在 fixture 上验证（"production catalog untouched"），生产 dry-run 从未跑过。FC-906 预飞首次对生产 catalog（46GB，`.source_catalog/catalog.sqlite3`）只读跑 `run_artifact_backfill(mode='dry-run')`。
- **结果（决定性）**：input 7718 → **bindable 0 → legacy_unbound 7718**。失败原因：`artifact_schema_unsupported` 7579 + `artifact_status_not_completed` 139（partial 124 + unsupported 15）。
- **根因**：生产 producer（normalizer/summarizer/section_extractor）写 artifact 时**从不打 v2 `schema_version`**。artifacts 表确有 `schema_version`/`source_sha256` 列但 100% NULL；`metadata_json` 也 100% 无这两字段。FC-901/902 绑定门 `validate_artifact` 要求 `schema_version == ARTIFACT_HANDLE_SCHEMA_VERSION`（"1.0"），缺席即 `artifact_schema_unsupported`。
- **血缘不缺**：23520/23521 文档有 `primary_source_id`；43082/43082 sources 有 `content_sha256`。即"源可证明"成立，缺的是 artifact 自证的 v2 元数据。
- **validate_artifact 精确契约**（顺序短路）：status=completed → schema_version=="1.0" → source_id==primary_source_id → **source_sha256 在 artifact 上可选**（仅在 present 时校验 mismatch，line 98-99）→ 文件存在+sha256 匹配 → generator 注册 → created_at 非未来 → path ∈ allowed_roots。**最小修复 = 给 artifact 打 schema_version；source_sha256 非必需。**
- **教训**：`scripts/processed_artifact_canary.py`（WU-1304）早写的悲观判断（"binding never populated… reuse chain cannot be proven on production"）被证真——但它检查 column，FC-901 实际读 metadata_json+documents/sources JOIN；两条路同结论（0 bindable），机制不同。**plan/工具/canary 描述可能滞后或用不同路径，FC 预飞必须实跑取数，不能信描述。**"FC-901 accepted"只代表 fixture 绿，不代表生产可绑定——accepted ≠ 生产可用。
- 配套完整记录：`audit_review/2026-08-09_full_completion_assurance_plan/fc_906_preflight_blocker.md`（dry-run 全数字 + reframed 决策）。

## 发现 44：FC-906 真阻塞定位 + 用户三连决策 + 路径 C 子 FC 链

- **真阻塞 = 语料库全量不可绑定**，upstream 于绑定→回执→消费全链。原预飞 Q1/Q2 决策前提被推翻：不是"3 角色有样本、缺 2 个"——**5 角色全不可绑定**；role 分布 normalized 4797 / summary 2910 / sections 11 / **markdown 0 / consumer_analysis 0**（后两者无任何 artifact，且 store 触发器 `trg_artifact_producer_event` 已预期 consumer_analysis→llm 类型）。
- **用户决策（2026-08-11）**：① 授权生成 `prompt_injection_review` 回执（review 依据 LLM/策略/人工待定）；② 先产出 markdown/consumer_analysis；③ **路径 C：新建 v2 canary 语料**（推荐）——一小批真实文档端到端跑通 v2-aware producer 覆盖全 5 角色，遗留 7718 诚实保留 legacy_unbound（不追溯认证）。
- **FC-906 拆分为子 FC 链**（runbook §10 授权的 -a/b 拆分，FC-905 有先例）：
  - **FC-906-a（本会话起点，company-wiki）**：v2 producer 绑定元数据——normalizer/summarizer/section_extractor 打 `schema_version`（+ 可选 source_sha256）；RED+impl+mutation。根因修复。
  - **FC-906-b（company-wiki）**：markdown + consumer_analysis producer——2 个新角色 producer，需 spec（DAG：markdown←normalized、consumer_analysis←summary）。
  - **FC-906-c（company-wiki，生产写已授权方向）**：真实 v2 canary 语料 + FC-901 apply + review 回执——小批真实文档全 5 角色 + 回执（依据待定）+ apply 证明 bindings>0。
  - **FC-906-d（三仓）**：T2 消费证据——bound canary 经 FC-905 门消费，证明 artifact_read>0、producer=0；AR 场景。
- **待定决策**：review-receipt 依据（LLM 扫描 / 策略判定 / 人工）——FC-906-c 前必须明确。
- **教训**：FC-906 作为"生产证据"FC，其价值正是暴露这种"代码绿但生产不可用"的缺口；预飞只读取数是 FC-906 的合格第一步，不能跳过直接 apply。

## 发现 45：FC-906-a——created_at 格式是与 schema_version 并列的隐藏 v2 阻塞；extractive summarizer 出范围

- **隐藏缺陷 created_at**：3 个注册 producer（normalizer/llm_summarizer/section_extractor）都用 `datetime('now')` 写 artifact.created_at（SQLite 空格格式 "YYYY-MM-DD HH:MM:SS"，生产 0/7718 ISO）。`validate_artifact` 的 `_UTC_RE` 要求 `YYYY-MM-DDTHH:MM:SSZ` → 修完 schema_version 后下一个失败是 `artifact_created_at_malformed`。FC-901 dry-run 全部在 schema_version（line 90）先短路，created_at 门（line 114）从未被触达——典型的"前面一个门掩盖后面所有门"。
- **修复**：`datetime('now')` → `strftime('%Y-%m-%dT%H:%M:%SZ','now')`（SQLite 内建，产出 ISO-8601 UTC）。与 schema_version 同属"producer 写 v2 合规元数据"一个行为单元——不可分（只修一个仍不可绑定）。
- **extractive summarizer 出范围**：`source_catalog_extractive_summary`（summarizer.py）**不在 GENERATOR_REGISTRY**（FC-902 只注册 3 个），生产 0 artifact（2910 summary 全是 llm_summary 2675 + 235 空 generator_name）。即便打 schema_version 也 `artifact_generator_unregistered`。是否注册它属 FC-902 合同决定，记 FC-1203 候选。
- **FC-906-a 实测（2026-08-11）**：RED 3 测试全失败（schema_version None）；GREEN 3 producer 各加 schema_version + ISO created_at（共 +9/-4 行，3 文件）；mutation 3 杀（每个 producer 删 stamp → 其测试死）；全量 wiki 套件 2228 passed/1 skipped/2 failed（仅 pre-existing PORT-01 对，零新失败）。
- **教训**：当一组门顺序短路时，第一个门的失败会掩盖所有后续门的缺陷——修完第一个必须立即检查第二个是否也坏，不能假设"修一个就够"。`validate_artifact` 的 9 个顺序门里，schema_version（#2）和 created_at（#7）都被生产违反。

## 发现 46：FC-906-a ACCEPTED + F-6 事件（reviewer 重置用户 dirty 文件）—— reviewer base 复现必须用独立 worktree

- **FC-906-a 完成**（company-wiki `5fbf349` feat + `f6df002` docs）：3 注册 producer 打 v2 schema_version + ISO created_at；RED 3 测试 → GREEN → M1~M3 三杀 → 全量 2228 passed 零新失败；独立 reviewer（干净 worktree，429 中断后 resume）accepted；can_accept gate exit 0（fc_id 用 "FC-906"，receipts 在 `assurance/fc/FC-906/`——与 FC-905-a/b 先例一致）。
- **F-6 事件（reviewer-process incident，严重）**：reviewer 在主 checkout 跑 base 复现时执行 `git checkout 0c9adac9 -- src tests` + `git checkout 5fbf349 -- .` 恢复，**把用户既有 dirty 文件 `llm_cost_log.csv`（LLM 成本日志，`scripts/llm_client.py` 追加写，tracked）的工作树未提交改动重置了**（现与 HEAD 一致，无 stash，未提交 delta 丢失；git 里提交的版本完好）。不影响 FC-906-a verdict（全部 review 证据在干净 worktree 产生；主 checkout src/tests 与 HEAD 字节一致）。
- **教训（过程）**：reviewer 的 base 复现**绝不能在主 checkout 跑 git checkout 切文件**——base/result 对比必须在两个独立 worktree（如 `.fcap-review/fc-XXX/base` vs `.fcap-review/fc-XXX/result`）。这是 FC-905/FC-906 系列第一个触碰用户 dirty path 的 reviewer 事件；已被 reviewer 诚实披露（F-6），但损失不可逆。
- **恢复建议**：用户可从 Windows 文件历史/VS Code local history 恢复 `llm_cost_log.csv` 的未提交行（约 08-09 后几天成本账）；若无备份，成本统计会缺这几天的行——不能伪造补上。

## 发现 47：FC-906-b——markdown/consumer_analysis 角色适用性裁决（catalog 侧不产）+ 文档校验测试弱检查教训

- **裁决（用户决策 A，2026-08-12）**：① `markdown`——与 `normalized` 内容重复（normalizer INSERT mime_type=`"text/markdown"`，normalizer.py:1619；normalized artifact 即 markdown 全文），company-wiki 无 spec/无 producer/无消费方测试，GENERATOR_REGISTRY 无对应 generator → **catalog 侧不产**，建议从 ROLE_DEPENDENCIES/roles 元组移除（FC-1203，冻结契约不动）。② `consumer_analysis`——E2E-D06 provenance 契约（engine/model/prompt/input_bundle_hash 匹配才复用，消费者提供 expected_provenance；content 是分析 JSON）证明它是**消费者侧产物**（revenue/invest-* 分析链生产并回写），catalog 只存取/复用 → **catalog 侧不产**。合同：`company-wiki/assurance/fc/FC-906/03_change_contract_fc906b.md`。
- **护栏测试**（tests/contract/test_fc906b_role_producer_contract.py，3 tests）：① producer 只写三角色 + GENERATOR_REGISTRY 无 banned 角色 generator（M1：往 section_extractor INSERT 注入 `"markdown",` → 测试死）；② 合同文档存在且每个非 catalog 角色必须有**裁决标题**（M2：删裁决 → 测试死）；③ 角色矩阵守恒（producer 角色 + 非 catalog 角色 = 冻结 DAG 角色集）。
- **弱检查教训（M2 首杀失败）**：初版文档校验只查"角色名出现在文档"——M2 删表格行后 §2 标题仍含角色名，测试没死。**文档类测试必须断言"裁决本身"（标题/语义结构），不能断言"词汇出现"**——否则变异不击杀，护栏形同虚设。
- **教训（FC-906 系列）**："角色不适用"是 task_plan 明示的合法路径（"角色不适用必须有合同说明"），但它必须是**裁决+证据+护栏**三件套，不是静默缺失——否则未来读者分不清"故意不产"和"忘了产"。

## 发现 48：FC-906-c 演练发现 normalize 队列缺陷——9506/23521 (40%) 文档无 active location 永远占队列头

- **现象**：副本演练 normalize(limit=3) 全部 failed=3 且 `last_failed_document_id=None`（静默失败，无任何诊断）。调试三轮后定位：priority 队列前 3（广联达/万润股份/山石网科年报）**没有任何 active locations** → `primary is None`（normalizer.py:1455-1457）→ failed++ 且**不记录任何诊断**（last_failed 三个字段都不设）→ 队列 SQL 的 NOT EXISTS completed 条件让它们**永远 eligible** → 每次 normalize 都先撞它们，真实文档被饿死。
- **生产规模**：23521 文档中 **9506 个零 active locations**（40%；有 locations 行但被 deactivate——remediation/quarantine 遗留）。这是生产现状，非演练环境问题。
- **修复（FC-906-c 前置）**：① 队列 SQL 加 `EXISTS (SELECT 1 FROM locations lp ... WHERE role='original_primary' AND location_status='active')` 排除（force 与非 force 均生效）；② primary-None 分支防御记录 `no_active_primary_location` 到 last_failure_code/last_failed_document_id/failure_reasons（漏网也可见）。
- **测试**：`test_fc906c_normalize_queue_no_location.py`（2 tests）——队列优先处理有-location 文档（M1：移除 EXISTS → 死）；primary-None 记录诊断（M2：移除防御记录 → 死，`last_failed_document_id=None` 断言抓出）。
- **调试教训**：① 调试脚本用**截断 document_id** 导致误判（"CatalogStore 过滤"假象）——document_id 是 97 字符 urn，必须用完整值；② **git checkout -- 会清掉未提交的修复**——mutation 还原必须用反向 Edit，禁止 checkout（FC-906-a F-6 事件同源教训的又一次体现）；③ normalize 队列 SQL 的 ORDER BY 是 `processing_priority_sql`（priority 排序），复现队列时排序不对会看错队首；④ 测试 fixture 的 INSERT 必须匹配表 DDL 的 NOT NULL/FK（documents.metadata_priority、locations.metadata_json/manifest_json、sources FK）——三轮 fixture 修复。

## 发现 49：FC-906-c——生产 canary apply 完成（29 v2 bound artifacts + 15 review receipts）+ FC-901 apply NO-OP 判定

- **生产 apply（2026-08-12，授权）**：normalize 15 真实文档（北方华创/腾讯 2024-25、微软 10-K、Apple 10-K、星环 filings、紫金矿业等）→ sections 11（CN 招股说明书语料——sections 适用；HK/EN 文档合法不适用 skip）→ 真实 LLM summary 3（MiniMax-M3，5 次调用，2 个文档级失败 `LLM response is not valid JSON` = 真实 LLM 行为）→ **29 v2 artifacts 全部 validate_artifact REUSABLE**（14/15+11/11+3/3，1 partial 合理）+ **29 producer_events**（触发器 journal 1:1）+ **15 策略 review receipts**（确定性扫描真实读内容，evidence_sha256=文本 hash，15/15 not_detected）。
- **FC-901 apply 判定 NO-OP**：生产 dry-run 7718→0 bindable（legacy 缺 v2 元数据）→ artifact_bindings 表 apply 无对象；"source-bound artifact > 0" 由 **v2 运行时绑定**达成（validate_artifact REUSABLE，无需 artifact_bindings 表）。Phase 9 exit gate 达成路径明确。
- **前置修复**：9506/23521 无-location 文档饿死 normalize 队列（findings 48）→ 修复 + 全量副本演练（46GB 副本 + WAL）→ 生产 apply 前**重启 ambient worker**（旧进程加载 pre-fix 代码会写出 legacy 风格 artifact 污染 canary）——worker 无状态，重启安全，新 worker 产出 v2 ✓。
- **真实副作用记账**：LLM 5 次调用成本写入 llm_cost_log.csv（+5 行，chore 提交）——**F-6 丢失的 08-09~11 行未补**（不伪造），新增行是真实的。
- **关键教训**：① 演练/生产必须用**同一代码**（worker 常驻进程用启动时代码——重启是 apply 的必要协调步骤）；② sections 适用性验证（CN 招股书 11/11 vs HK/EN 0）证明"角色适用性"是语料相关的事实，不是全局判定；③ `PYTHONIOENCODING=utf-8` 会让 PORT-01 的 2 个 pre-existing 失败消失（环境规避，非修复——FC-1205 仍待关闭）；④ resolve 北方华创 → ambiguous（多期报告身份歧义 fail-closed 正确）——T2 消费需精确文档请求（FC-906-d）。

## 发现 50：FC-906-d——T2 真实消费达成 + FC-902"测试绿/生产空"双缺口（列 vs metadata、derived root）

- **T2 达成（2026-08-12）**：revenue `source_preparation`（真实三仓链）消费北方华创 2025 → `reused_existing`、**artifact_read=['normalized']**（bound artifact 真实读取）、journal **33→33**（本次消费 producer=0）、download=0、llm=0、prompt_injection_status=not_detected（策略 receipt 生效）。旧 unbound 不复用：星环 2024（legacy）→ valid_handles 空（artifact_schema_unsupported fail closed）。
- **缺口 1（列 vs metadata）**：FC-906-a 把 schema_version 写进 **metadata_json**，但 FC-902 的 bundle 消费方（query_source_bundle）读 **artifacts 列**——列 100% NULL → 生产 bundle 全 `artifact_schema_unsupported`。修复：3 producer INSERT 写列（normalizer 顺带写 source_sha256）+ 生产回填 33 行。**教训：契约字段的"单一事实来源"必须被所有消费方一致读取——FC-901 backfill 读 metadata、FC-902 bundle 读列，两条路径在 FC-906-a 只修了一条。**
- **缺口 2（derived root）**：bundle_for_resolution 默认 allowed_roots = config.roots（源根），artifacts 在 derived/ → 全 `artifact_path_outside_allowed_root`。测试显式传 allowed_roots 绿、生产走默认空。修复：默认 += derived_dir。**教训：测试显式传参与生产默认路径必须等价验证（"测试绿/生产空"是 FC 验收盲区）。**
- **worker 三重启**：FC-906-a/c/d 每次代码变更后 ambient worker 都用旧代码产出（metadata 有/列无）——每次修复后重启 worker 加载新代码；生产回填兜底既有行。**worker 是"代码版本滞后"的持续风险——FC-1101（PR 门）应含 worker 代码版本校验候选。**
- **fake resolution 测试模式**：bundle_for_resolution 单测用 SimpleNamespace(matches=[SimpleNamespace(document_id, content_sha256)], status=...)——注意 match 是**属性访问**（不是 dict 下标），两轮 fixture 修复。
- **T2 的 producer_events 语义**：selector 的 producer_events = **缺失角色的 DAG closure**（非 artifact_read 的补集闭包）——北方华创 2025 显示 4 角色（消费者需要但无 artifact），这是正确语义（文档本身无 sections/summary artifact）。artifact_read 才是"producer=0"的证明（配合 journal 不变）。

## 发现 51：FC-1001——统一三根 isolated-lake fixture + FC-505 日期漂移修复（pre-existing 时间敏感测试）

- **FC-1001（Phase 10 基石）**：`tests/e2e_support/isolated_lake.py`——一个 temp 目录同时布局三根（companies/紫金矿业 2025 + portfolio/601899 2024 + Dropbox/中国平安 2020 中期），sidecars、identity、v2 preset artifacts（**schema_version 列 + metadata 双写**——FC-906-d 契约）、producer_events journal、5 个 corruption 变体（hash_mismatch/truncated_source/sidecar_missing/location_inactive/column_drop 各在不同层 fail closed）、确定性 manifest_hash（无绝对路径，Windows/Linux 可重现）。9 tests；M-loc/M-hash（破坏 corrupt 实现）双杀。
- **corruption 的 fail-closed 层级**（设计要点）：hash_mismatch→validator 层；column_drop/truncated_source→**bundle 层**（query_source_bundle 读列/源 hash——FC-906-d 生产路径）；sidecar_missing→**resolve 层**（company_raw 容忍无 sidecar，Dropbox 依赖 sidecar 身份——scan 不拒但 resolve 不命中）；location_inactive→resolver 层。
- **FC-505 日期漂移（pre-existing）**：fixture 的 as_of 固定 "2026-08-11" 而 resolver 的 retrieved_at=动态 today → `published <= captured <= as_of` 从 08-12 起永远失败（revenue 全量 2 failed）。**时间敏感 fixture 的固定日期是持续回归源**（Phase 1 同类：as_of 硬编码审计日）——test-only 修复为动态 today+7。
- **mutation 方法论**：对单断言测试，"删除断言"不是有效 mutation（删了即无检查）——**mutation 目标是 corrupt() 实现本身**（UPDATE 不 quarantine / 不 tamper → 测试抓出）。
- **教训**：pre-commit 门禁（sync_installations --apply + 全量 + E2E）在提交时自动跑并全绿——commit 信息需含全部改动（含 FC-505 修复）。

## 发现 52：FC-1002——真实三进程 E2E 链达成 + R4.2 提交门禁再教训 + fixture 生产形态补全

- **三进程链**：revenue source_preparation（进程1）→ subprocess filing_fetch_client（进程2）→ subprocess wiki CLI（进程3）——真实 OS 进程，process_count>=3 满足 FC-102 registry 门。3 contracts：exact 命中零副作用（artifact_read>0、journal 不变、download/llm=0、not_detected）、三进程 trace（生产代码 subprocess 链 inspect + 输出透传）、缺失 artifact → producer_events DAG closure。M1（移除 fixture review receipts）→ FC-905-b 门阻断链 → 测试死 ✓。
- **fixture 生产形态补全（IsolatedLake 扩展）**：① review receipts（FC-905-b 门：消费阻断 not_reviewed——链测试暴露 FC-1001 缺 receipt）；② security_master/cn.json（filing-fetch identify 依赖——schema 校验严格：顶层精确字段集 schema_version/market/record_count/records/retrieved_at/sources + record 必填 ticker/canonical_name/exchange/security_id/active/source_name/source_url/source_record_id——三轮修 schema）；③ config/source_catalog.yaml 在 wiki root 下（filing-fetch 校验存在）；④ **companies 必须在 wiki_root/companies**（filing-fetch legacy containment 校验 canonical_path ⊆ wiki_root/companies——production 形态）。
- **R4.2 提交门禁再教训**：**改测试文件后提交前必须 sync_installations --apply**（首次 FC-1002 提交被 R4.2 DIFF 拦截——3 文件滞后；同步后 MATCH 102 files 才过）。这是 memory 教训⑦的严格执行版。
- **教训**：跨仓链测试的 fixture 必须**生产形态完整**（config/security_master/根布局/审核回执）——每个下游 hop 的校验都是真实契约，缺一个就 fail closed（这不是缺陷，是设计；fixture 必须补全而非绕过）。

## 发现 53：FC-1003——95 场景机器覆盖门（required gaps=0）+ 真实缺口：filing-fetch legacy containment 拒 dayu 根

- **覆盖门**（compatibility/scenario_coverage.py）：SCENARIO docstring 标注（组合 ID 拆分、tools/tests 扫描）+ receipts scenario_results 并集；owner_fc 未来 Phase（FC-110x/120x/130x/150x/FC-1004）显式 deferred；required gaps=0（87 covered + 14 deferred）。7 自测（M2：deferred 前缀清空 → 门失败）。
- **盘点方法**：grep 测试名只找到 14/95（测试不按 ID 命名）；**receipts 的 scenario_results 是权威覆盖证据**（58/95）；标注补齐到 87。教训：**覆盖证据必须机器可扫（标注/receipts），不能靠测试名推断**。
- **UJ 场景**：UJ-01/02/04/07 真实测试（IsolatedLake 链）；UJ-03/05 归 FC-805 T3 下载测试标注；UJ-06/08 归 fc904 selector 测试标注。
- **真实缺口（filing-fetch）**：legacy containment `validate_handle` 只认 `wiki_root/companies`——**dayu 根文档经 filing-fetch 从没被打通**（canonical_path 在 portfolio/ 被拒）——UJ-02 暴露。生产 dayu-only 经 filing-fetch 从未验证（FC-602 是 wiki 侧测试）。**修复方向**：filing-fetch 需 policy-snapshot roots（FC-1202 单一策略源）——记入 FC-1202 前置。
- **fixture 生产形态**（IsolatedLake 再扩展）：dayu 文档需 company-name entity（ticker 不够——resolver 按 canonical name 匹配）、reusable_root_kinds 需全三根（默认只 company_raw）。每层校验都是真实契约。
- **教训**：覆盖门自身要测（deferred 前缀是门的"豁免开关"——清空它门必须红）；手写 hash 又错一次（pitfall #1 第四次，receipt 已修）。

## 发现 54：Phase 10 完成——E2E 基石 + 覆盖门 + 平台 + critical mutation（FC-1001..1005）

- **FC-1001**：IsolatedLake 三根 fixture（corruption×5/manifest hash 无真实路径）——Phase 10 基石；corruption 的 fail-closed 层级是设计要点（hash→validator、column/source→bundle、sidecar→resolve、location→resolver）。
- **FC-1002**：真实三进程 E2E 链（psutil 确认 5 OS 进程超 process_count>=3 门）；跨仓 fixture 必须生产形态完整（config/security_master/review receipts/companies 在 wiki_root 下——每个下游 hop 的校验都是真实契约）。
- **FC-1003**：95 场景机器覆盖门（SCENARIO 标注 + receipts 并集；required gaps=0）。**三轮 review**：F1（单行 docstring 外插标注→SyntaxError）、F2（ast.parse 加固未密封）。**教训：覆盖证据必须机器可扫；"标记但不可运行"的文件会撑绿门——门必须 compile 验证标记文件**。
- **FC-1004**：PORT-02 空格路径一致性 + 安装同步自包含 + UTF-8 链。
- **FC-1005**：critical mutation 门（8 类 kill=100%）；M-latest 现场击杀（close_gap re-resolve 移除→cg05/cg07 死）。
- **教训**：**receipt 的 commands 不能含预期非零退出命令**（FC-703 r2 教训在 FC-1104 重现）；mutation 还原用反向 Edit 而非 git checkout（清未提交修改）；手写 hash 是反复犯的 pitfall #1。

## 发现 55：Phase 11 完成——动态审核体系机器化（FC-1101..1105）

- **FC-1101**：CI sibling checkout manifest 驱动（替代硬编码 pin）。**三轮 review**：F1 manifest triplet 滞后于 result HEAD（提交→manifest→提交循环）→ 门重设计为 commits-exist（防伪，非 ==HEAD）；F2 正则 `` 被 heredoc 转义污染成字面 0x08 退格 → 扫描空转——**字节级验证（od -c 看 5c 62）** + 负向控制测试。
- **FC-1102**：每日 T2 只读 runner（mode=ro+query_only）——生产冒烟发现 **scan completed_with_errors 212 vs FC-001 基线 155（真实恶化 +57）**；P3 findings F1-F3（policy freshness/报告新鲜度/fingerprint 趋势）——F1 由 FC-1105 关闭。
- **FC-1103**：每周 T3 runner——无 --force=BLOCKED exit 2（告警非绿）；reviewer 现场真实 CN/HK/US 下载 214s 全绿。
- **FC-1104**：audit dashboard + release gate（24h T2 + 7d T3）——**r1 因 receipt 治理门（commands 含 exit 1）changes_required**。
- **FC-1105**：故障注入矩阵（6 类注入全红）+ runner 健壮性（UTF-8/原子/并发）。
- **教训**：① receipt 的 commands 全 0 是硬门（预期非零写 scenario 文本）；② manifest/CI 门要防"空转正则"（负向控制测试）；③ 动态审核的价值实证：T2 runner 首跑即发现 scan health 真实恶化；④ 系统化 review 流程（r1/r2/r3 闭环）在每个 FC 都抓到了真实缺陷——没有一次 review 是纯走过场。

## 发现 56：FC-1201——root-hardcode 门转 frozen ratchet + canonical_writer/cli 重构被 loader 阻塞（DEFERRED）

- 日期：2026-08-12。Phase 12 启动。用户 `/planning-with-files 从头一个一个实施` 触发。
- **范围决策（用户 Interpretation A）**：FC-1201 exit gate「forbidden hardcode=0」与 cutover 冲突——残留 root-specific 分支几乎全在 v1 scanner（7 处），而 v1 仍是生产回退（R8/R9 未完成：`legacy_bridge_hits=6`，门关；v2 flags OFF per FC-204）。code_quality_plan §3 step7 明确「关桥后才删 legacy 代码」。→ 门棘轮 + 安全清理，v1 延后 R9。
- **真实 hardcode 地貌（preflight）**：FC-304 `no_root_specific_hardcode` 门是 **substring 匹配**（4 token：`dropbox_stock`/`company_raw`/`dayu_portfolio`/`Dropbox`），所以注释/docstring/SQL/错误信息都触发——allowlist 显式白名单了 11 个「backlog」文件。root-specific **行为分支**仅 3 文件：scanner.py（v1，7 处，R9）、canonical_writer.py:126（写根选择）、cli.py:1251（portfolio 根查找）。resolver.py 已清（FC-701 用 `config.reusable_root_kinds`）。service.py:237/normalizer.py:1487 的 `acquisition/dayu_meta` 读属另一门（legacy container gate），非 root-token 范围。
- **关键阻塞（DEFERRED 根因）**：生产 **1.x loader `config.py:75-84` 的 `allowed_root_fields` 严格拒未知字段**——不含 `canonical_write_target` 且 `unknown = set(item) - allowed_root_fields` → CatalogConfigError。生产 `source_catalog.yaml` 三根都未设 `canonical_write_target`（测试 fixture 都设 `"companies"`，但生产 yaml 从未补 → FC-301 生产迁移未收尾）。故 canonical_writer 重构（按 `canonical_write_target` 选写根）需同时改 loader（生产加载路径）+ yaml + 可能级联破坏未设 target 的 fixture → 超出「安全清理」。cli.py:1251 按身份引用 dayu_portfolio 根（同 admission.py FOCUS_ROOT_ID），literal 内禀不可 config-only 化。
- **交付（company-wiki feat `0c6c2c9` + receipt `8817521` + closure `b3b45aa`）**：门转 **frozen ratchet**（`_ROOT_HARDCODE_ALLOWED_FILES` 精确 pin，`test_fc1201_allowlist_ratchet_frozen`；新增文件→测试红→强制 review）；注释清理 resolver.py:679/observability.py:76/entity_resolver.py:1 → 三文件移出 allowlist（real shrink，零行为）；5 新 contract 测试。零 v1 scanner / loader / 写路径 / yaml 改动。
- **验证**：17 focused + 272 contract 子集 + 全量 wiki 2241 passed/1 skipped/0 failed（PYTHONIOENCODING=utf-8 下 PORT-01 对也过）。M1（allowlist 涨）+M2（token 删）双杀。reviewer-fc1201-independent 干净 worktree ACCEPTED（RED-at-base 第二 worktree，3 非阻塞 finding）。can_accept exit 0。
- **教训**：① receipt `reviewed_at` 必须 UTC `Z`（非 `+08:00` offset）；② `receipt_validator --accept` 只传 implementer receipt（reviewer 经 sha256 引用，不作第二 `--receipt`——reviewer receipt schema 不同，传两个会按 implementer schema 校验报一堆错）；③ mutation commands exit_code 必须 0（pitfall #5 再现，inner pytest exit N 写 result 文本「KILL CONFIRMED」）；④ substring gate 使注释清理「load-bearing」——离开 allowlist 必须先清注释；⑤ 「安全清理」FC 的边界要诚实：loader/config 改动不算 safe，宁可 DEFERRED + frozen backlog 也不强推。

## 发现 57：FC-1202 预检——单一安全策略源的具体触点（含 filing-fetch dayu CI containment 缺口）

- 日期：2026-08-12。FC-1202 前置 FC-1201 ✓ accepted。Owner 三仓。
- **filing-fetch `Path.parent/sibling` 隐式定位**：`scripts/filing_contracts.py:360-390` 已是 FC-501 policy-snapshot 单一 containment 源（好）；但 `scripts/filing_filing.py:138 root = selected.parent / root` 是隐式父目录定位（FC-1202 目标）。`references/contract-ownership.md:23-24` 文档已声明「no independent allowed_handle_roots」。
- **filing-fetch dayu containment 缺口（FC-1003 发现 53）**：`.github/workflows/quality.yml:63-65` 仍残留 `allowed_handle_roots` 检查 + **硬编码 dayu 路径** `'${USER_PROFILE}/Projects/dayu-agent/workspace/portfolio'`——FC-501 删了运行时 allowlist，但 CI workflow 残留第二策略源 + 硬编码 root。这是「legacy containment 拒 dayu 根」的 CI 侧缺口。
- **filing-fetch `SKILL.md:141-143`**：仍写「directory is listed in filing-fetch's allowed_handle_roots」+ dayu_portfolio reuse——**stale 文档**引用已删的 allowlist。
- **revenue `Path.parent/sibling`**：`scripts/filing_fetch_client.py:56,206`「two repos live as sibling directories」+ 「defaults to the sibling repo」——隐式兄弟定位（FC-1202 目标：manifest/安装入口）。`tools/ci_checkout_siblings.py`（FC-1101）已是 manifest 驱动的正解（CI 侧），但运行时 client 仍用兄弟假设。
- **config doctor**：需三仓 contract compatibility 检查（不复制 root 列表）。
- **FC-1202 性质**：多仓 + 触 CI workflow + 兄弟仓定位（基础设施敏感）。需独立 preflight + scope 决策（同 FC-1201 模式），不宜在同一长会话末尾仓促实施。
- **影响**：FC-1202 实施前须重验 triplet + 确认 dayu CI containment 缺口的精确修法（删 quality.yml 残留 vs 改 containment 逻辑）+ 兄弟定位的 manifest 化不破坏运行时。

## 发现 58：FC-1202 preflight — 触点核实 + scope 决策（Interpretation A）

- 日期：2026-08-12。前置 FC-1201 ✓ accepted。Owner 三仓。triplet：revenue `84d4967` / filing `592fae6` / wiki `b3b45aa`。用户指令「继续直到项目全部完成，全部授权」——按 FC-1201 模式由 implementer 完成 preflight + scope 自决并记录。
- **运行时 containment 已正确（核实，不进 FC-1202）**：`filing_contracts.py:350-419` `validate_handle` 已是 policy-snapshot 单一 containment 源（FC-501：RootPolicySnapshot + expected_policy_hash，`allowed_roots` 仅 N/N-1 弃用回退）。findings 53 的「legacy containment 拒 dayu 根」= wiki resolver 只对 company_raw 建 handle + R4 dayu cohort 未发布之组合；**运行时修复属 Phase 14 R4，明确出范围**。
- **真实触点（preflight 实测）**：
  1. filing CI `quality.yml:57-72` config doctor 块**已失效**：FC-501 后 config 精确 schema 无 `allowed_handle_roots` → `cfg.get(...) or []` 恒空 → `missing=required` 该步骤必红；且硬编码 3 个 root 路径 = 复制 root 列表（FC-1202 禁止项）。
  2. revenue `filing_fetch_client.py:60` `_DEFAULT_FILING_FETCH_ROOT = _SKILL_ROOT.parent / "filing-fetch"` ——生产运行时兄弟仓假设（source_preparation 子进程不带 `--filing-fetch-root`）。
  3. filing `fetch_filing.py:137-138` 相对 `company_wiki_root` 静默按 config 文件父目录解析（隐式定位；`test_editing_config_moves_root_without_code_changes` 用相对 "wiki-one" 依赖该分支）。
  4. wiki `scripts/config_doctor.py:103-105` `root.parent / "filing-fetch"` 兄弟仓假设（CONFIG-DBX-03 检查侧；`test_e2e_f03_filing_allowance_smuggled_fails` 依赖）。
  5. filing `SKILL.md:139-144` stale：引用已删的 `allowed_handle_roots` + "两个 config 各加一行"。
- **CI 关键影响（新增发现）**：FC-1002 三进程链测试在 revenue CI（Ubuntu）跑，`source_preparation.py` CLI 不带 `--filing-fetch-root` → 依赖 client 兄弟默认。A1 改 config 后 CI 上 `${USER_PROFILE}/Projects/filing-fetch` 不存在（sibling 在 workspace 旁）→ 链测试必红。**修复**：`prepare_source` + CLI 增 `--filing-fetch-root` 透传，FC-1002 测试显式传入（测试侧 FILING_ROOT 计算是 fixture 布线，非生产策略）。
- **决策（Interpretation A，显式化 + 单一策略源，零生产行为变化）**：
  - **A1 revenue**：新增 `config/filing_fetch.json`（schema 1.0 精确字段 `{schema_version, filing_fetch_root}`，token `{SKILL_ROOT,USER_PROFILE}`，必须绝对路径 + 目录存在 + 含 `scripts/fetch_filing.py`；缺/多字段、相对、无 fetch_filing.py → config_error）。`resolve_filing(filing_fetch_root=None)` → 读 config；显式参数/CLI 优先（E2E 不动）。sync_installations 已验证 `config/` 在 ROOT_DIRECTORIES，自动入安装面。
  - **A2 revenue**：`prepare_source` + `source_preparation.py` CLI 增 `--filing-fetch-root` 透传；FC-1002 链测试显式传 `FILING_ROOT`。
  - **A3 filing**：相对 `company_wiki_root` → config_error（显式绝对/token 展开 only）；更新 1 测试 + 新增负向测试。
  - **A4 filing**：新 `tools/config_doctor.py` 三仓契约检查（filing config 精确 schema + wiki `source_catalog.yaml` 结构（schema_version/reusable_root_kinds/roots 形状，零 root 路径硬编码）+ revenue `config/filing_fetch.json` 若存在（缺 revenue clone 时跳过））；quality.yml stale 块替换为 `python tools/config_doctor.py --revenue-root "$HOME/Projects/revenue-forecast"`。tools/ 不在安装面（无需 sync）。CI 上 USERPROFILE 未设 → doctor 用 `Path.home()` 回退（与 fetch_filing.py 一致）；ci_checkout_siblings 已把 wiki 放 `$HOME/Projects/company-wiki`，与 `${USER_PROFILE}` 展开同值。
  - **A5 filing**：SKILL.md Notes 重写为 policy-snapshot 语义（单一策略源 = company-wiki `source_catalog.yaml`；filing config 只定位 wiki 根；加 root = 只改 wiki 一行）。
  - **A6 wiki**：`config_doctor.py` 删兄弟查找 → `--filing-fetch-config` 显式参数（缺省跳过跨仓检查）；更新 2 测试。wiki CI 不传参（跨仓检查单一归属 filing CI doctor）。
- 性质：多仓 + 触 CI workflow，但全部改动为「显式化」——revenue 默认定位从 sibling 变 config 文件（config 值与旧 sibling 路径同值，本地行为不变）；零生产数据/写路径/containment 行为变化。

## 发现 59：FC-1203 preflight — 死代码盘点 + scope 决策（Interpretation A）

- 日期：2026-08-12。FC-1202 实施完成（reviewer 重放中）。三仓 AST/CodeGraph 全量盘点（index gap 用 grep 交叉验证）。
- **关键裁决：extractive summarizer（findings 45 的 FC-1203 候选）→ 注册 + 补 v2 元数据**。事实链：`summarize_catalog` 有生产调用者（service.py:155 → CLI summarize + run pipeline），但其产物**永不可绑定**——三重独立失败：INSERT 无 schema_version 列值（DDL 加列无 DEFAULT）、generator `source_catalog_extractive_summary` 未注册（GENERATOR_REGISTRY 仅 3 个）、created_at 用 `datetime('now')` 非 ISO-Z。与 FC-906-a 对 llm_summarizer 的修复同构 → 按同模式修（注册 + 列 stamp + ISO created_at + 测试），使既有生产 CLI 产出可复用 artifact。**不删**（有生产入口 + run pipeline 使用）。
- **Prime 删除候选（生产无调用者、已被生产入口替代）**：
  - `evaluate_candidate`（admission.py:244，测试-only，未导出；生产入口 = `evaluate_admission`，scanner 消费）
  - `validate_normalized_filing`（normalized_meta.py:57，零调用者）
  - `entity_resolver.py` 整模块（零生产 import）
  - `restore.py` 整模块（与 store.restore_document + CLI restore 平行实现，被替代）
  - `flags.py validate_flag_state/atomic_rollback`（唯一非测试调用者 = 一次性 wu905 脚本，不入 CI；已被 runtime_policy.py CAS 机制替代，FC-202/203）
  - `reuse_latest_policy.py` 整模块（零生产 import；close_gap 用自己的 policy binding——实施时验证后删）
- **明确不删（记录理由，防止误删）**：
  - `policy_2x.py` 全部 3 函数无生产 import——但是 Phase 14 R2/R3 cutover 资产（v2 scanner dry shadow 需要），保留待发布波次
  - `canary_registry.py`（FC-504，R3-R5 cohort 资产）、`dropbox_governance.py`（FC-503 ops 工具 + replay）
  - `backfill_v2.py run_backfill`、`portfolio_promoter.py`——architecture_gate 已标 "v1 legacy (R9)" + FC-1201 frozen allowlist，R9 backlog 不动
  - `_replay` 工具 ×4（assurance receipt 证据工具）、`drift_patrol.py`（FC-701 receipt 引用证据）、54 个一次性 stage/cleanup 脚本（ops 历史）
  - revenue `generate_input_template.py` 28 个 FIXME = 模板占位符（非债务）
- **超大函数清单（Q3 前 15）**：SourceCatalog 类 1186 行、revenue_report._validate_forecast_output 1083、cli.main 766、SourceCatalogWorker 741、FocusScopeCleanupService 642、WorkerController 563、SourceResolver 533、cli._parser 503、CatalogStore 920、_scan_catalog_impl 450……**拆分决策：不拆生产热路径**（resolver/service/worker 拆分在发布波次前是高危重构）；拆分归 FC-1204 复杂度 ratchet（其 exit gate 才要求 complexity<=10），FC-1203 只做删除 + API 收敛（"关键 dead helper=0" 是 Phase 12 gate 项）。
- **API 收敛核实（已在 HEAD 成立，FC-1203 记录不修改）**：service.py 不 import resolver（status.value 字符串，FC-902 合同成立）；resolver→service 单向；filing 零 wiki import（薄客户端成立）；revenue 无 import-time 环（revenue_core↔report/publication 是 lazy-import 断开的调用环，拆分归 FC-1204）。
- **FC-1203 Interpretation A 交付**：① 删除上列 6 组死 helper + 其测试；② 新门测试 `dead helper=0`（AST/导入断言已删符号不存在——mutation 目标 = 复活死代码必须击杀）；③ extractive summarizer 注册 + v2 元数据 + 测试 + 合同文档；④ 行为零变化（删除对象均无生产调用者）；⑤ R9/R2-R5 资产删除禁入（列合同）。
- 注：wiki CodeGraph 索引有 gap（close_gap/artifact_backfill/canary_registry/dropbox_governance/prompt_injection/trace_parity 未收录、bundle_for_resolution 报 not found、SidecarFilingAdapter 零 caller 误报）——FC-1203/1502 用 grep 交叉验证，不把空结果当事实。
## 发现 60：FC-1204 preflight 起点 — 复杂度基线实测 + 工具可用性

- 日期：2026-08-12。FC-1203 reviewer 重放中（CPU 竞争期只做轻量测量）。
- **工具**：mypy 1.19.0 ✓、coverage 7.12 + pytest-cov ✓（pyright 无——type check 用 mypy）；revenue `tools/run_coverage_gates.py` 已有 --branch 解析 + fail_under 门。
- **复杂度基线（AST McCabe 实测，三仓产品代码）**：230 个函数 CC≥10、283 个 ≥8。顶端：revenue `_validate_forecast_output` CC174/1083 行、wiki `cli.main` 140/766、`_scan_root_v1` 140/377、`resolver.resolve` 103/288、`_scan_catalog_impl` 102/450、`worker.run_cycle` 99/411、revenue `validate_management_target_coverage` 88/443、`validate_artifact` 59/64、filing `validate_resolution_envelope/validate_handle/validate_request` 各 39。
- **FC-1204 scope 指向**：① branch coverage 测量（reviewer 结束后跑，防 CPU 竞争）；② complexity ratchet = 冻结实测 max-CC + 顶 5-10 个「行为被既有场景锁定的纯函数段」拆分（_validate_forecast_output 的语义重算段、resolver.resolve 的 pipeline 段），生产热路径与发布波次交互处不动；③ mypy public contracts 基线（先测错误量再定 strict 面）。阈值按 code_quality_plan §3「实测后冻结，计划不虚构」执行。

