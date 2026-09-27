# 完成度复核发现

## 发现 001：文本上的 complete/accepted 不是当前功能完成证据

- 日期：2026-08-13。
- 事实：旧计划中的 `findings.md`、`progress.md`、`task_plan.md` 和 `work_unit_registry.md` 在不同时间继续变化；最新紫金真实运行又暴露了复用成功但消费失败、Dropbox 未语义处理等问题。
- 决策：逐项验证 production reachability、命令、commit、receipt、side effects 和真实用户旅程；旧状态只作待核声明。

## 发现 002：必须新建统一计划而不是在两个既有计划上并发编辑

- 日期：2026-08-13。
- 事实：用户明确指出还有其他 planning-with-files 程序；旧计划文件最近仍被写入。
- 决策：本目录独占写入；最终给出旧计划关闭/迁移清单，由原 owner 或后续单一执行者处理。

## 发现 003：旧计划名义上完成 66/71 FC，但 Phase 14 不在 71 个 FC 状态机中

- 当前 `work_unit_registry.md` 有 71 行：3 个计划基线、63 个含 `accepted` 的实现项、5 个 FC-1501～1505 pending。
- Phase 14 的 R0～R9 被定义为“发布波次而非 FC”，不进入 71 项 closure 状态；当前账本称 R0～R8 已有不同程度 evidence/applied，R9 被至少一个自然时间窗口阻塞。
- 风险：仅验证“71 FC 全 accepted”不能证明 Phase 14 每波的 preview、授权、cohort、观察、rollback 和独立 reviewer 全部完成。
- 决策：统一新计划把每个遗留发布波次迁为有机器状态、依赖、receipt 和 reviewer 的正式工作单元；closure 必须同时消费功能单元和发布波次。

## 发现 004：当前正在编制的 FC-1501 closure gate 存在漏检面，不能直接作为最终真相

- `_accepted_receipts` 只搜索 revenue 与 company-wiki 的 assurance 目录，没有搜索 filing-fetch；例如 FC-903 的 filing receipt 可能完全未验证。
- accepted FC 找不到 receipt 时会静默跳过，不会报“缺失主证据”；它也没有逐项验证 reviewer receipt、closure、command registry、plan/policy/config hashes或 receipt 路径唯一性。
- scenario 检查只查看“找到的 implementer receipt”内显式列出的结果是否 skip/blocked，不证明 95 个 mandatory scenario 均有新鲜、真实层级匹配的结果。
- triplet 只检查 HEAD 是 frozen baseline 的后代，不要求等于 current compatibility manifest、upstream 或被审查 commit，也不检查 dirty tree/installed skill/config/schema。
- status 采用字符串包含 `accepted`/`pending`，格式化自然语言可被误解析；Phase 14 R0～R9 完全不在 gate 输入中。
- 决策：把现有 gate 视为诚实的早期 RED 原型，而不是 FC-1501 完成证据；新计划先写针对这些漏检面的 mutation/contract tests，再实现 closure 2.0。

## 发现 005：旧计划的完成数量与“所有预定目标达成”不能画等号

- 旧计划自身最终八个验收问题仍全部未勾选，并明确任一为否则整体 incomplete。
- Phase 11 虽标 COMPLETE，但 exit gate 记录连续 Daily T2 观察尚待积累；这说明 runner/门实现与持续运行达标是两件事。
- Phase 12 的 FC-1201 接受了 Interpretation A：只冻结 hardcode ratchet，v1 scanner 七分支、canonical writer/CLI 重构被推迟到 R9；因此“代码质量全面完成”是有条件的 scoped completion。
- 决策：保留已验证机制，不重复重写；但对每个用户痛点以当前 production journey 重新分类，证据不足或被反例推翻的旧 accepted 项进入 `revalidate/reopen`，而不是继承绿色。

## 发现 006：动态审核“工具已实现”，但“持续动态运行”没有生产接线证据

- 三仓 GitHub workflow 目前都只声明 push/pull_request；未见 schedule/cron 或 workflow_dispatch 触发 Daily T2、Weekly T3。
- FC-1102/1103 implementer receipt 明写 standalone tool，`scheduled deployment is a release-owner action`；CodeGraph/receipt 也记录 production callers 为 0。
- assurance/runs 当前只有少量手工/preflight报告，不能证明 Daily/Weekly 连续运行、报告 freshness、告警送达或 release gate 实际消费。
- 结论：FC-1102/1103 的 runner 机制可以保留为 `implemented_and_reviewed`，但 Phase 11 的“持续动态审核 COMPLETE”被当前接线证据否定。新计划必须迁移实际调度、权限、告警、freshness、sample rotation和自然时间 soak。

## 发现 007：current-triplet gate 实际仍是陈旧 pin + 祖先关系，不是当前三仓组合保证

- `compatibility/current.json` 的 `current_triplet` 仍是 revenue `1b41d62...`、filing `592fae6...`、wiki `f6eb584...`，而审查时 HEAD 已推进到 revenue `c3a0519...`、filing `83c638e...`、wiki `ef125ed...`。
- manifest 自身 note 明确把 current_triplet 降为 informational；closure gate 只检查当前 HEAD 是 frozen baseline 的 descendant。
- revenue workflow 只断言 manifest 有三个 current 字段，再按这个陈旧 manifest checkout sibling；它不证明当前三个 HEAD 的组合。filing workflow还从远端克隆 revenue 后消费其 manifest，存在最新仓库组合未同步验证窗口。
- 结论：FC-104/1101 是“可工作的固定兼容组合机制”，不能证明“每次验证当前三仓最新 triplet”。新计划应建立事件驱动的 compatibility candidate、精确 commit equality/attestation和跨仓变更 fan-out。

## 发现 008：若干 accepted receipt 自己已经披露未闭合问题

- FC-1102 披露 policy/schema freshness、atomic publish、fingerprint trend 等 P3 finding 尚需在 Phase 11 exit 前关闭；旧计划却随后直接把 Phase 11 标 COMPLETE。
- FC-1303 reviewer 明确指出 `latest` SLO 实际重复测 exact，RSS 测的是 probe shell 不是 resolver subprocess；因此 latest 和真实 resolver 内存预算未被证明。
- FC-1201 明确只完成 frozen ratchet/safe cleanup；v1 scanner、canonical writer 和 CLI 硬编码推迟到 R9。
- FC-504 主 implementer receipt 仍是 `independent_review`、内嵌 review pending；真实通过依赖 r2 reviewer/另一 implementer receipt。基于固定文件名读取首份 receipt 的 closure gate可能验证错误 revision。
- 决策：新完成度账本按“claim的最小真实范围”标记，不因为 registry status accepted 就扩大结论；所有 reviewer unresolved finding 必须有 owner、后继 work unit 和可验证关闭证据。

## 发现 009：95 场景 registry 是设计目录，不是可执行证据账本

- registry 有 95 个场景、127 个 tier entry，但当前 120/127 fixture 仍是 `pending:FC-*`；127/127 都至少含一个 `scenario-defined` 调用预算；127/127 声明的 evidence path 在三个仓库均不存在。
- coverage gate 把“可解析 test 文件里出现 `SCENARIO:` 字样”或“任意 implementer/reviewer receipt 里出现场景 ID”视为 covered；它不要求目标 test 被收集或通过，也不检查 receipt status、tier、fixture、oracle、调用预算、freshness或 evidence path。
- `_DEFERRED_FC` 是静态前缀，Phase 11～13 即使标完成，AUD/OPS/PORT 等 14 个场景仍永久 deferred；`accepted_fcs()` 函数定义了却没有参与 required 判定。
- 当前报告 `required_gaps=[]` 只能证明 95 个 ID 都在某处出现过，不能证明 95 个 mandatory 场景按其声明 tier 运行成功。
- 决策：保留 95 个需求 ID，但 closure 2.0 必须为每个 tier 生成不可缺省的 machine result；fixture、预算、命令、freshness和hash不得有 placeholder，marker 只能用于映射，不能作为 pass 证据。

## 发现 010：旧状态注册表本身违反自己的状态和 DAG 规则

- 文件声明状态只能取固定枚举，但 71 行中有 20 行把日期、reviewer、粗体和 phase 结论嵌入 status 单元格；在建 closure gate改用“字符串包含 accepted”绕过了枚举约束。
- FC-1301 的前置写成 `FC-1301(链)`，形成直接自依赖；Phase 13 四项又由同一 reviewer `reviewer-fc130x` 成组审核，降低了逐工作单元独立性。
- 部分 accepted 是“registry补记——closure时遗漏”，说明状态表不是由 validator 单写、原子推进的唯一真源。
- 决策：新计划采用严格 JSON/YAML state registry，状态与注释分字段；DAG 拓扑校验、自依赖/未知依赖、非法状态、状态跳跃和并发 CAS 都必须进入 CI mutation。

## 发现 011：CodeGraph 可查询但不能证明当前三仓结构快照新鲜

- revenue 索引约在最新提交前一分钟更新；filing DB/WAL 主更新时间停在 8月9日，company-wiki 停在8月10日，而两仓 HEAD 都已到8月13日。
- `codegraph_status` 只给文件/节点/边数量，不给 indexed commit；旧 receipts 多次承认索引缺文件后用 grep代替。
- 决策：本轮不在并发收尾期间重建索引；统一计划首阶段在取得独占锁后重建并把 indexed commit/hash写入审计 manifest。结构结论必须与运行测试配对。

## 发现 012：Dropbox “全链通过”实际上没有证明 Dropbox location 被消费

- FC-504 r2 明确放宽了 canary 排他性：四个 Dropbox PDF 的相同内容在 companies/dayu 仍有 active location。
- FC-505 独立 reviewer 对 DBX-01 的原文是：紫金两份 `REUSED_EXACT` 的 canonical path 位于 `company-wiki/companies`；星环两份因 dayu canonical URL 为 HTTP 而 fail closed。
- 因而该链证明的是“Dropbox sidecar 可帮助同一逻辑文档被识别，resolver可复用另一个 root 的 canonical副本”，不是“Dropbox-only 文件通过 filing→revenue 被消费”。
- FC-604 的三 root 一致性只在隔离 catalog 验证 company-wiki resolver 输出，未穿越 filing handle 的默认 companies containment和 revenue source-preparation。
- 结论：旧 Phase 5 的扫描/身份/去重资产可保留，但用户要求的功能层 Dropbox 接入仍未证明；新计划必须有真正物理排他的 Dropbox-only 和 dayu-only 三进程场景，并断言 selected location/root_id。

## 发现 013：receipt validator 的结构校验被 closure gate误当成接受校验

- `receipt_validator.validate_receipt` 只检查形状；commands可为空，scenario_results可为空，blocked/pending场景不在 skipped集合，`policy_sha256=not-applicable`可自由使用，也不验证命令实际重放。
- 它不读取 reviewer receipt、不重算 `reviewer_receipt_sha256`、不核对 implementer receipt hash、也不验证 reviewer unresolved finding 已关闭。
- `can_accept` 才要求内嵌 review accepted，但在建 closure gate只以默认结构模式调用 validator。
- 只读实测：FC-504 主 receipt 内嵌 review=`pending`，结构校验 exit 0；对同一文件执行 `--accept` exit 1。
- 结论：旧 FC-103 的库函数是有用起点，但实际总门接错 API；统一计划需把 revision selector、implementer/reviewer配对、hash重算、命令重放和finding closure合为一个不可绕过的 verifier。

## 发现 014：当前 closure 原型会把大量未证明目标压缩成“只剩五项 pending”

- 对当前仓库运行 closure gate，仅报告 FC-1501～1505 pending；它没有报告陈旧 current triplet、Phase14 R9、动态未调度、127个缺失场景证据、Dropbox路径未消费、FC-1303代理SLO或revenue紫金真实失败。
- 这不是五个终审FC本身的问题，而是 gate输入域和验证语义太窄。
- 决策：旧 FC-1501～1505 不直接照搬执行；迁移为新版“证据系统修复→当前功能复验→自然时间soak→最终关闭”链，只有前述漏检mutation都被杀死后才允许生成closure ledger。

## 发现 015：严格 current-triplet 口径下，旧 71 项没有一项可直接继承为当前 complete

- 分类为31项 implemented-but-unverified、26项被当前行为反证、9项证据陈旧、5项pending；`verified_complete_current=0`。
- 这不否定大量代码资产，而是否定“历史accepted自动给当前HEAD担保”。
- 决策：所有功能单元初始pending；已有实现通过current RED/mutation/独立review后走`already_satisfied`快速路径，禁止无谓重写。

## 发现 016：生产 read path 会创建/迁移数据库

- `CatalogStore`构造包含mkdir、普通SQLite连接、WAL、DDL/migration/seed/commit；resolver service懒加载该Store。
- 隔离构造不存在DB后实际创建约237,568B数据库。独立readonly canary没有穿越production resolver。
- 决策：拆能力受限CatalogReader，使用不存在DB、OS只读、live WAL/future schema和DB/WAL/SHM/lock全fingerprint作为硬门。

## 发现 017：同一请求可能在v2 resolve与v1 ensure/close-gap之间漂移

- CLI resolve显式加载runtime policy；acquisition/close-gap内部直接构造缺省resolver，可回v1+legacy。
- current runtime flags中多个只在定义/架构处出现；snapshot值不代表production消费。
- 当前配置导出policy hash与runtime snapshot hash不相等，root也缺显式filing授权。
- 决策：引入必填immutable RuntimeContext贯穿所有阶段；policy snapshot可复算、hash一致；任何`None` fallback或事后贴hash的结果fail closed。

## 发现 018：dayu复用缺陷有真实数据影响，Dropbox v1扫描同时污染身份

- 实库有21个dayu-only active filings，当前filing companies containment会拒绝。
- Dropbox少量独有annual/semi中至少4个是`.pdf.source`标题且日期空的sidecar JSON假阳性；其余有其他root副本。
- 决策：T2必须选真实dayu-only unique sample；Dropbox filing先过sidecar identity清理，不得以已有companies副本冒充external-root成功。

## 发现 019：`newer_revision`只被描述，没有进入下载动作

- company GapPlan能表达newer_revision；filing和close-gap都只判断missing并常取第一项。
- revision仍可能依赖provider ID字典序，不能可靠代表filed_at/amendment顺序。
- 决策：actionable=`missing ∪ newer_revision`，明确0/1/多gap、max_items/bytes、remaining gap、post-commit re-discovery和二次零下载。

## 发现 020：派生产物数量很多，但可证明复用覆盖很低

- normalized 4,835仅177有schema+source SHA；summary 2,963仅4两者齐全；producer仍可能写空SHA，validator对空SHA不fail。
- shadow artifact_bindings无production reader；DAG依赖/失效主要只被测试使用。
- 决策：唯一validator/view先接production bundle，再做verified/recompute/quarantine五桶迁移；source SHA必填，不为提高比率猜绑定。

## 发现 021：producer event不能证明parser/LLM零调用

- 事件由artifact INSERT trigger按role推断，不能观察attempt/failure/retry/cache/update；extractive summary也可能被误算LLM。
- 决策：在真实producer调用边界记录invocation start/success/failure/cache_hit，并与边界spy对账；artifact-created另作审计事件。

## 发现 022：Dropbox隐私和prompt安全是P0数据治理风险

- active Dropbox文档约800份有completed summary；649份由source_catalog LLM summarizer生成，metadata为529份MiniMax-M3、120份mimo-v2.5-pro，但当前仅1份有关联prompt review。
- root未显式privacy class且worker不按privacy/receipt筛选。catalog不能证明历史网络路线/授权，不能武断判定曾违规或安全。
- 决策：先封堵未来：private+not_reviewed+无egress授权时外部LLM=0；再审计历史provider/model/egress receipt和处置范围。

## 发现 023：revenue generator、validate-only、draft和publication均有当前可复现反例

- generator rc=0，但linter rc=2、engine报41项；缺management_targets、非法status和多类claim/dimension/history/hash错误。
- 有效fixture的validate-only返回0却创建676B registry。
- draft公共renderer因gate_ids contract失败；formal registry先append再写输出，缺事务/恢复/幂等。
- 决策：单一schema真源、真实engine generator门、纯prepare/validate、Draft/Formal分型和publication transaction分别建立原子单元，不能打包成一次大改。

## 发现 024：现有矿业模型不能兑现逐矿收入目标

- reserve_depletion可保留，但缺asset/location、mine×commodity×product、resource/reserve basis、ownership/consolidation、commercial adjustments、internal elimination和segment/group reconciliation。
- 紫金资料本身不披露逐矿2026～2030收入；逐矿输出必须是可勾稽模型估计或诚实data gap。
- 决策：通用opt-in矿业垂直层；紫金+第二异构矿企；非矿企回归防止系统被矿业化；禁止公司/矿名hardcode。

## 发现 025：R9强门当前4/4 RED，日常skip掩盖未完成

- 显式开启时，backfill_v2仍可import、`_scan_root_v1`存在、legacy flag存在、scanner hardcode allowlist存在。
- 决策：冻结旧R9；先完成新链和动态观察，再由CA-304分批删除。不得只改skip或测试预期使其变绿。

## 发现 026：Windows/环境错误必须控制变量，不能整批洗白或定罪

- 已观察中文临时目录WinError 5、GBK subprocess decode、长嵌套路径artifact失败和sandbox cryptography/Git权限噪声。
- 决策：先短ASCII可写basetemp控制组，再分别引入中文/空格/长路径/默认locale；基础设施与产品错误分类型，但跨平台失败本身属于目标缺口。

## 发现 027：多份“计划/manifest/权威执行”文件仍会让新接手者判断错入口

- `audit_review` 下有六个日期目录，其中至少三个看起来仍可执行；最新目录内部又有 task plan、manifest、authoritative plan、两个registry和多个审计/追踪文件。
- 即使内容互相一致，新接手者仍可能从旧R9、旧FC-150x或冻结ZR目录直接领取，或者把审计结论误当实施状态。
- 决策：创建根目录唯一 `README.md`，同时承担当前状态、下一卡、完整顺序和阅读路由；其余文件只按明确条件读取。旧文件不移动/删除，避免破坏hash、receipt和并发owner。

## 发现 028：现有旧目录的状态文字不统一，不能靠目录日期或标题判断可执行性

- 8月8日和旧data-lake计划已在文件头写superseded，但仍指向旧FCAP；旧FCAP文件头仍写“plan ready、所有phase pending”，与后续66/71实施账本和新版反证并存。
- 紫金skill-run是一次审计记录，不是实施计划；ZR目录是冻结的92个功能规格annex，却有自己的manifest和“实施未开始”文字；最新目录又同时出现manifest、task plan和“权威执行计划”。
- 决策：根README明确四类：唯一可执行入口、详细规范附录、历史审计证据、已取代旧计划。只有README可声明`current_phase/next_work_unit`；任何其他Markdown中的状态文字都不具备领取权。

## 发现 029：整合不能复制117张卡，否则会产生第三套真源

- 把25个CA、92个ZR和197个场景全文复制到新总计划，短期看似方便，长期会出现ID、状态、hash和验收口径双写漂移。
- 决策：根README只做控制面，固定目标、唯一游标、A～J阶段、去重映射、写边界和阅读路由；详细定义继续由冻结CA/ZR registry与scenario matrix单点持有。
- 新任务只需先读README；只有`current_next`指向某卡后才读其按需附录。这样既能让弱模型不迷路，也不牺牲可机器校验的单一事实源。
