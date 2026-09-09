# 三仓库资料复用、数据湖语义摄取与收入预测闭环 — 渐进式改进计划

> 计划编制日期：2026-08-13  
> 计划目录：`audit_review/2026-08-13_zijin_data_lake_remediation_plan/`  
> 本轮权限边界：只编制计划，不修改 revenue-forecast、filing-fetch、company-wiki 的产品代码、配置、数据库、索引、测试或 CI。  
> 实施状态：**未开始**。任何任务只有在代码、测试、证据、审计四类门禁全部通过后才可标记完成。

## 并发写入协议

- 本目录为本任务专属；不得编辑仓库根目录或其他 `audit_review/*` 任务的 `task_plan.md`、`findings.md`、`progress.md`。
- 每次修改前重新读取目标文件并记录 SHA-256/mtime；只用小范围补丁，不整文件覆盖。
- 若写前与读取时 hash 不同，视为并发冲突：停止写入、记录冲突、重新读取并人工合并；禁止 last-write-wins。
- 不清理、回滚、暂存、提交或改写其他程序的工作树变更。
- 实施者开始任何 phase 前必须重新验证代码现状；过时任务标记为“已无效（代码已变更）”，不得机械执行旧行号或旧假设。

## 计划编制阶段

### P0（建立独立计划与证据基线）— 状态：completed

- [x] 完整读取 `planning-with-files` 技能。
- [x] 创建任务专属 `task_plan.md`、`findings.md`、`progress.md`。
- [x] 读取最新紫金技能运行审计、旧全面改进计划及三个仓库当前状态。
- [x] 将已解决、仍存在、因代码变化待复核的问题分开，不把旧审计直接当当前事实。

### P1（设计完整实施路线、门禁和验收矩阵）— 状态：completed

- [x] 明确目标架构、责任边界和不可妥协的不变量。
- [x] 拆成弱模型可执行的原子任务，每项给出允许修改范围、禁止动作、测试、失败回滚和完成证据。
- [x] 设计单元、契约、集成、真实 E2E、并发、故障注入、迁移、回滚和动态审核。
- [x] 设计渐进式发布顺序，确保重构过程中旧路径持续可用或能安全回退。

### P2（对抗式计划审查与交付）— 状态：completed

- [x] 对照用户六项目标和本次紫金实测问题逐项建立需求—任务—测试—证据可追踪矩阵。
- [x] 设置阶段退出门、独立复核人和禁止自证规则。
- [x] 检查所有链接、编号、状态、依赖和验收标准；确认没有产品实现。
- [x] 交付完整计划及实施顺序摘要。

## 最终成功定义

本计划把用户要求固定为六个不可拆分的最终目标。任一目标未取得运行证据，三仓整体不得宣称完成。

| 目标 | 完成后必须成立 | 不能冒充完成的证据 |
|---|---|---|
| G1 重构完全成功 | read path 物理上无写能力；root、来源身份、location、处理状态和 consumer readiness 解耦；旧生产旁路 caller 为 0 | 新类/新表“已经存在”、合成单测通过、旧路径仍在生产可达 |
| G2 Dropbox 功能层面接入 | 完成一次通用 root/adapter 架构改造后，Dropbox 的允许/拒绝只由严格配置改变；filing 与 broker consumer 各按文档类型和隐私策略使用 | 代码中加入 Dropbox 路径特判、只扫描到文件、只在 validator 单测中通过 |
| G3 功能与目标全部实现 | 已有文件复用、最新期间/修订补齐、已有 MD/summary/chunk/tag 复用、缺件按需处理、财报/研报/网页/矿山事实进入预测闭环 | “文件找到了”但 safety/artifact 未 ready；逐矿数据缺失却伪造精确收入 |
| G4 完善动态审核 | PR、Daily、Weekly、Monthly 四层真实调度；报告有 freshness、triplet、样本、side-effect 和告警自检；过期或 blocked 会阻断发布 | runner 脚本存在但无人调度、skip 被记作绿色、实施者自签通过 |
| G5 真实 E2E 覆盖 | existing/partial/missing/stale/conflict、三 roots、七份研报、真实 provider、并发/中断/篡改、二次复用均有进程级场景 | mock 掉被验证核心、只测 happy path、required 场景 skip |
| G6 全面代码质量提升 | 单一契约真源、严格类型、复杂度/覆盖率 ratchet、硬编码/死路径/文档漂移为 required gate | 以重命名或搬文件代替降耦；降低阈值；保留“暂时”分支且无删除条件 |

完成保证的边界：全部任务完成并通过持续审核，可以证明“冻结需求、已知缺陷和纳入场景的行为在指定 triplet 上被关闭且有回归防护”；不能逻辑保证未来未知缺陷永远为零。动态审核、样本轮换、mutation 和 freshness 门专门控制这部分剩余风险。

## 状态、门禁与弱模型执行纪律

- work unit 只有 `pending → in_progress → implemented → independently_verified → accepted` 一条正向路径；也可进入 `blocked`、`superseded` 或 `cancelled_with_evidence`，不得直接从 pending 跳到 accepted。
- “完成代码”不等于完成任务。必须同时具备：目标 diff、要求的正反例测试、完整命令/退出码、side-effect ledger、机器 receipt、独立 reviewer 结论。
- 任一 mandatory 场景被 skip、xfailed、删掉、弱化断言、改 golden、降低阈值，phase 退出门自动失败。
- 弱模型每次只领取一个 ZR 编号，只能修改该任务卡的 allowlist；发现需要越界时必须停下写 plan-drift，不能顺手修复。
- 实施前必须重读 [implementation_runbook.md](implementation_runbook.md) 和目标 ZR 卡；测试设计以 [scenario_matrix.md](scenario_matrix.md) 的 oracle 为准，不能自行缩减。
- phase reviewer 必须与该 phase 的 implementer 不同；使用 clean worktree 重放，不接受实施者口述、手填调用次数或仅截图。
- 上游 contract、schema 或计划 hash 漂移时，下游任务自动回到 pending/revalidation；不得沿用旧 receipt。
- 各 phase 默认串行。仅当下文明确允许，且文件 allowlist、数据库、fixture、registry、worker 和报告目录均不共享时才可并行。

## 实施阶段总览

> 下列均是未来工作，本轮没有实施。原子任务的 owner、依赖、allowlist 模板和证据要求见 [work_unit_registry.md](work_unit_registry.md)；所有实施状态保持 `pending`。

### Phase 0：重新基线化、RED 证据与停线规则 — 状态：pending

**工作单元：** ZR-001～ZR-004。

**入口：** 获得三仓只读访问；本计划目录和旧计划文件 hash 可重算。

**必须执行：**

1. 冻结当日三仓完整 commit、branch、dirty files、skill 安装副本、配置、schema、CodeGraph commit/freshness 和所有关键命令版本。
2. 在隔离副本重放紫金用户旅程，逐项把旧结论分为 `still_failing / already_satisfied / superseded / blocked`，尤其重放 exact reuse、Dropbox、artifact、draft renderer、validate-only 和 publication registry。
3. 注册脱敏 golden corpus：FY2024/FY2025 财报、七份 Dropbox PDF、合法及错误身份网页、预测输入/结果；内容不复制进仓库，保存 hash、角色、实体、期间和访问规则。
4. 冻结 machine command registry、scenario registry、receipt schema、共享资源锁、side-effect ledger 和变更 allowlist。
5. 只读映射旧计划状态；不得修改其他 owner 正在写的旧计划。

**退出门：** ZR-001～004 全部 accepted；每个历史问题有当前证据；CodeGraph 与 HEAD 一致；没有产品改动；任何样本、命令或权限缺失均标 blocked，不能进入 Phase 1。

### Phase 1：测试护栏、可观测性和跨仓契约基座 — 状态：pending

**工作单元：** ZR-101～ZR-105。

**入口：** Phase 0 accepted。

**必须执行：**

1. 先版本化跨仓八阶段 taxonomy、error/reason/event schema；unknown reason 必须 fail closed。
2. 建立真正启动 revenue → filing → wiki 三个 subprocess 的 hermetic runner；只允许在 provider/LLM 边界使用 spy。
3. 建立 closure/receipt validator，拒绝短 hash、自审、陈旧 triplet、缺命令、skip、越权写入和幸存 mutation。
4. 冻结类型、分支/复杂度、覆盖率、路径硬编码、死 production caller 和 encoding 基线，并设置只能提高不能降低的 ratchet。
5. 三仓 CI 绑定 current triplet；任一仓 contract 变化必须触发受影响组合，而不是继续验证旧 pin。

**允许并行：** ZR-102、ZR-103、ZR-104 可在 schema 和文件 allowlist互斥时并行；ZR-105 必须最后串行汇总。

**退出门：** taxonomy N/N-1 契约绿；T1 runner 能杀死至少一个注入缺陷；receipt mutation 全拒；quality 阈值冻结；current-triplet required gate 真实运行且 required test 无 skip。

### Phase 2：Catalog 真只读读模型与并发可靠性 — 状态：pending

**工作单元：** ZR-201～ZR-206。

**入口：** Phase 1 accepted；保存 production catalog 只读快照及 live-WAL 方案。

**必须执行：**

1. 把 `CatalogReader` 建成能力受限的 read port：`mode=ro`、`query_only`、有界 busy timeout；构造不得 mkdir、WAL、DDL、migration、seed 或 commit。
2. identify/query/status/resolve/bundle/health 全部接到同一只读 snapshot；schema 不兼容返回结构化错误，绝不自初始化。
3. 用 CodeGraph 和运行 spy 将所有只读生产 caller 从 `CatalogStore`/writer initializer 移除；旧 reader 只能是带 owner、期限和删除门的显式兼容开关。
4. 统一 SQLite busy/locked、operation lock、timeout 和 paused reason；filing retry 有 deadline、fake clock、上限和完整阶段回执。
5. 在 live writer 长事务、OS 只读目录、多进程、高容量 catalog 下做压力/故障测试；精确复用不得 pause worker 或取得 writer lock。

**退出门：** READ-01～12 全绿；Reader 前后 DB/WAL/SHM/目录指纹一致；writer initializer 对 read-only production入口 caller=0；50 并发无 deadlock/下载/结果串线；SLO 未超预算；独立 reviewer 复放。

### Phase 3：来源状态机、安全、派生产物谱系与旧产物迁移 — 状态：pending

**工作单元：** ZR-301～ZR-307。

**入口：** Phase 2 accepted；真实 Reader 可支撑无副作用盘点。

**必须执行：**

1. 以追加 assertion 表达 identity、capture、safety、freshness、artifact 和 semantic readiness；不再用单一 `active` 掩盖不同缺口。
2. prompt-injection receipt 绑定 source SHA、scanner/version、ruleset/evidence hash，并从 acquisition/worker 真实入口产生；`not_reviewed` 不能伪绿。
3. 建唯一 artifact validator/reusable view/SourceBundle 生产读取语义；`source_sha256` 必填，表列、metadata 和 shadow binding 不得各自为真源。
4. 分开记录 producer attempt/result 与 artifact-created event；失败但无 artifact 也有 attempt，本次 parser/LLM 调用数与历史事件严格分离。
5. 先 dry-run 五桶分类，再由决策门选择 shadow binding 或按需重处理；不可证明 lineage 的旧产物保留为 `legacy_untrusted`，不伪造、不覆盖、不删除。
6. SourceBundle role DAG 只重算缺件及依赖闭包；下游失败仍必须保留文件复用、下载数和 processing next action。

**退出门：** BR-01～26 中 artifact/readiness 场景全绿；100% legacy artifact 恰入一桶、两次 dry-run hash 一致；apply 后必须被真实 SourceBundle 消费；已处理 source 的第二次请求 parser/LLM=0；安全 blocked 不吞掉 reuse receipt。

### Phase 4：通用 roots 复用、时效判断和授权下载 — 状态：pending

**工作单元：** ZR-401～ZR-409。

**入口：** Phase 2 accepted；Phase 3 的 readiness/receipt contract accepted。

**必须执行：**

1. RootPolicy 3.0 对每个 root 显式定义 path、read_only、document kinds、consumer 权限、privacy、adapter、priority、symlink 和 canonical write target；移除按 `kind=directory` 自动授权。
2. core 只认识 root/adapter protocol，不认识 `Dropbox`、`dayu` 或公司路径；新增 future root 必须只改配置和 adapter fixture。
3. 分离逻辑 document/source、全局 canonical location 和本次 eligible location；选择顺序固定为 policy → health → priority → 稳定 tie-break，读取不得改 canonical。
4. filing 校验 resolver 传来的完整 policy snapshot/root_id/relative path/realpath；v2 不再回退 `<wiki>/companies` 默认 allowlist。
5. 把 local match 与 provider freshness 正交表达；exact/equivalent 不等于最新，支持 newer period、same-period revision、unknown、not published、future 和非自然年。
6. GapPlan 下载授权绑定 request/gap/policy/provider/accession/TTL/items/bytes/nonce；无授权仅 discovery，current 即使授权也不得重下，missing/newer_revision 只补最小集合。
7. 下载统一 staging → 校验 → companies canonical commit → re-resolve；并发 single-flight、中断恢复、损坏隔离和幂等重放都有 oracle。

**退出门：** 只改临时配置即可让 Dropbox 合格 filing 在拒绝/允许间切换，代码不变；dayu/Dropbox/companies/future root 使用同一 resolver；未授权下载=0、授权缺口下载精确=1、二次=0；provider unknown 不伪称最新；core root 名/path 硬编码=0；跨 root BR/ROOT/FRESH/AUTH 场景全绿。

### Phase 5：Dropbox 券商研报、网页来源与按需语义处理 — 状态：pending

**工作单元：** ZR-501～ZR-510。

**入口：** Phase 3、4 相关 contract accepted；取得私有文档处理授权的明确策略。

**必须执行：**

1. 将 `broker_research` 建成一等文档类型；sidecar 与原文分角色，文件名只作候选，首页/元数据/实体/证券/日期冲突 fail/review。
2. 支持多实体 section/table attribution，避免把比较研报中其他公司行绑定给紫金。
3. 生成页码和阅读顺序可逆的 normalized MD、结构化 table artifact、语义 chunk、tag 和 typed fact；保留 merged cell、脚注、单位、ownership 和截图定位。
4. 建 `ProcessingDemand` API 和公平调度：consumer 提需求但不能篡改全局优先级；依赖闭包、成本、deadline、幂等、retry 和 privacy 都进入 receipt。
5. `private_user` 文档未经授权不得发给外部 LLM；本地可做的步骤与外部处理分别计数。
6. 官方公告/新闻/HTML 必须验证 title/entity/date/source identity；HTTP 200 和内容 hash 不能替代身份校验；合格来源才能 capture→index→MD/chunk/tag。
7. 以七份真实 Dropbox PDF 和两个官方网页做 canary，并记录版权安全的 hash/定位而非复制全文。

**退出门：** 七份 PDF 7/7 有可信 metadata、MD、table、chunk、tag 与 source binding；长江多实体归属零错；关键矿山/储量查询达到冻结的 precision/recall；重复需求 producer=0；私有数据无未授权外发；错误网页身份被拒。

### Phase 6：矿山事实层、mine-year 运营模型和会计桥 — 状态：pending

**工作单元：** ZR-601～ZR-611。

**入口：** Phase 5 semantic contract accepted；先完成 ZR-610 独立会计审阅的通用矿业 ADR。

**必须执行：**

1. 建 Asset Registry/alias timeline，明确单矿、矿群、公司聚合体、项目；Resource、Reserve、grade、capacity、permit、ownership、控制/权益法和地区均为带时点与证据的 typed fact。
2. 表格抽取保留冲突；数量级、口径、期间或权益不一致时并存 assertions 并进入 review，绝不静默择值。
3. `MineYearOperation` 使用 mine × commodity × product × year × scenario，明确 ore、contained、recovery、payability、saleable volume 和单位换算；缺失是 gap，不是 0。
4. 商业层显式表达 realized price、TC/RC、premium、by-product、FX、royalty；会计层表达控制合并、权益法、gross/net 和内部销售消除。
5. asset → external segment → company 必须对账；储量是可持续性约束，不直接乘价格创造收入；不闭合时诚实回退到分部并披露 residual/gap。
6. 先跑通通用多矿合成 E2E，再做紫金 pilot 和第二家不同结构矿企，证明没有公司/矿名硬编码。

**退出门：** MINE-01～24 全绿；单位、ownership、权益法、内部消除 mutation 全杀；逐矿贡献可重算且明确是模型估计；紫金覆盖率达到预先冻结阈值或显式 residual；第二家公司无需产品代码改动；生产硬编码公司/矿名=0。

### Phase 7：revenue 契约、生成器、纯验证、发布和置信度闭环 — 状态：pending

**工作单元：** ZR-701～ZR-713。

**入口：** Phase 1 contract 基座 accepted；矿业扩展依赖 ZR-610/611，其他 schema/purity work 可先行。

**必须执行：**

1. 先把 runtime/schema/docs/linter/generator 收敛到机器单一真源；修复 3.7/3.6 漂移、capture 10 键、management targets、claim/recognition/dimension 错误；不得放宽 validator 迁就模板。
2. generator → fixture filler → hash check → linter → `validate_document` → draft full run 必须一次闭环；linter 明确只是快速子集且不能 false-clean。
3. 抽出无 I/O 的 `prepare_forecast`；`--validate-only` 不签名、不注册、不写 output/snapshot/registry、不碰网络/subprocess，help 与行为一致。
4. draft/formal validator、receipt、renderer 和 consumer 边界分别闭环；draft 可渲染但 invest consumer 拒绝，formal publication prepare/commit 故障下无孤儿且成功精确注册一次。
5. schema 3.8 仅 additive opt-in，3.7 canonical hash 不变；矿业模型通过通用 registry，不在核心公式出现紫金分支。
6. 重验 immutable snapshot/backtest；建立真实 rolling-origin 紫金记录；置信度 policy 版本化并杀死 duplicate claim、参数拆分、other-revenue plug、zero-impact、单 observation 和 wrong-record 等博弈。

**允许并行：** ZR-701～705 与 Phase 6 的事实建模可在文件无交叉时并行；ZR-707、708、711、712 必须按 registry 依赖；ZR-709 最后运行，禁止自循环或越过依赖。

**退出门：** REV-01～22 与 revenue 旧 golden 全绿；generator 强验证通过；validate-only 文件树和 registry 字节不变；draft renderer 当前反例关闭；formal 故障原子；3.7 零回归；置信度攻击全部被抓；紫金五年 journey 可重放且不会伪称未披露逐矿收入。

### Phase 8：三仓真实 E2E、故障注入和跨平台验收 — 状态：pending

**工作单元：** ZR-801～ZR-806。

**入口：** 各功能 phase 的 mandatory work unit implemented；尚未独立验收的功能不能以 mock 代替。

**必须执行：**

1. 将旧 95 场景和 READ/BR/MINE/REV/ZJ/AUD2 注册为 machine scenarios；每项有 owner、tier、fixture、oracle、negative/fault、mutation、timeout、budget、freshness。
2. 从 revenue 用户入口覆盖 existing、partial、missing、stale、revision、conflict、safety blocked、artifact stale、三 root duplicate 和第二次复用。
3. 注入锁、竞态、崩溃、磁盘满、错误 hash、路径越界、错误网页身份、时钟和顺序扰动；失败后能恢复且不污染真实 root。
4. 覆盖 Windows 中文/空格/大小写、Linux 和 installed skill；禁止 `Path.home()`、固定 sibling repo 或生产 registry 隐式泄漏。
5. T3 在临时 wiki 中做 CN/HK/US 首次授权下载和二次零下载；T2 对真实 roots 只读 canary，所有 source/catalog 指纹不变。

**退出门：** mandatory 场景全部执行且无 skip；关键 mutation kill=100%；已有文件 download=0，缺口无授权=0，有授权精确=1，重跑=0；已处理 artifact producer=0；生产 roots/catalog 零写；紫金完整用户旅程结果和回执可重算。

### Phase 9：动态审核、质量预算和持续回归 — 状态：pending

**工作单元：** ZR-901～ZR-907。

**入口：** Phase 8 accepted；调度环境、凭据所有者和告警接收者明确。

**必须执行：**

1. PR 运行 current-triplet T0/T1、架构、类型、质量、receipt 和 mutation gate。
2. 真正调度 Daily Windows T2、Weekly/发布前 T3、Monthly 紫金完整 draft shadow；缺环境/凭据为 blocked 并告警，不是 skip-green。
3. 记录 reuse、download avoidance、artifact hit、consumer-ready、broker fidelity、misattribution、mine conflict、model share、backtest error、render、validate-only side effects、registry integrity 等 SLI。
4. release gate 检查报告 freshness（36h/9d/35d）、triplet、sample rotation、atomic completion、side effects 和趋势预算。
5. 用伪零下载、过期报告、错误 triplet、缺样本、半报告、wrapper 吞退出码等 mutation 自测审核机制。
6. 将 root/path/company 硬编码、死 production caller、复杂度、严格类型、critical coverage、文档/skill 漂移固化为不可降级 required checks。

**退出门：** 调度运行而非只存在脚本；自测能真实让 release 红并送达告警；所有报告原子、可验 hash、无自签；代码质量阈值较 Phase 1 只升不降；自然时间 soak 尚未完成时只能标 provisional。

### Phase 10：渐进迁移、影子运行、cohort 切换和回滚 — 状态：pending

**工作单元：** ZR-1001～ZR-1009；详细波次见 [migration_rollout_plan.md](migration_rollout_plan.md)。

**入口：** Phase 0～9 accepted；生产备份、容量、维护窗口和显式写入/下载授权已批准。

**必须执行：**

1. 先上线 Reader，writer 行为不变；再 shadow lifecycle/RootPolicy；任何 schema/data migration 都排在读路径稳定之后。
2. roots 以 companies → dayu → Dropbox → future root 小 cohort 激活；每 cohort 均可仅关 flag 回退。
3. legacy artifact 先 dry-run、再最小 canary；只有可证明 binding 且真实 bundle 会消费的记录才迁移，不可证明者按需重处理。
4. 七份研报按 1 → 3 → 7 扩大；mine facts/model 只做 shadow，与旧分部预测逐年 diff、对账和 backtest。
5. source/revenue 新链小 cohort cutover，观察 SLI/side effects；旧路由只有在两个动态周期 zero-hit、CodeGraph caller=0 和 N-1 期限批准后才能删除。

**退出门：** 每波都有 before/after fingerprint、diff、SLO、side-effect、回滚 receipt；一次真实 rollback/re-activate 成功；旧 artifact/snapshot/registry 未改写或删除；发生未解释 diff、孤儿、错误写 root、指标越界立即停止并回滚。

### Phase 11：独立终验、自然时间观察与项目关闭 — 状态：pending

**工作单元：** ZR-1101～ZR-1105。

**入口：** 所有 mandatory ZR 至少 independently_verified；无未登记 plan drift。

**必须执行：**

1. 机器 closure gate 验证状态、hash、路径、triplet、freshness、命令、side effects 和 required scenario；pending/blocked/skip 不得被折算为完成。
2. 独立 reviewer 从 clean checkout 对抗式检查三仓生产 reachability、硬编码、旁路、测试孤岛、伪计数和文档漂移。
3. 重新执行 companies/dayu/Dropbox、旧+新、已处理+缺处理、broker/mine、CN/HK/US、Windows 中文路径和紫金完整旅程。
4. 完成连续 7 次 Daily T2、2 次 Weekly T3、1 次 Monthly 紫金 shadow、1 次告警链自检，以及真实 cohort rollback/re-activate；自然时间门不可人工豁免。
5. 生成机器需求—任务—场景—证据 closure ledger，并将旧计划状态只读投影为 keep/reopen/already-satisfied/deprioritize/cancel/superseded。

**最终退出门：** G1～G6 每项 machine pass；所有 mandatory scenario fresh；legacy production caller/hit=0；closure validator exit 0；两个独立 reviewer 无 blocking finding；只有此时 Phase 11 和整体计划才可标 `accepted/complete`。

## 交付文档与执行顺序

| 文档 | 作用 |
|---|---|
| [architecture_target.md](architecture_target.md) | 目标边界、数据模型、跨仓协议与全局不变量 |
| [implementation_runbook.md](implementation_runbook.md) | 弱模型逐工作单元执行法、side-effect/receipt/审查纪律 |
| [work_unit_registry.md](work_unit_registry.md) | ZR-001～ZR-1105 原子任务、owner、依赖和退出证据 |
| [scenario_matrix.md](scenario_matrix.md) | 继承旧 95 场景及新增真实场景、oracle 和调用预算 |
| [traceability_matrix.md](traceability_matrix.md) | 六目标、紫金实测缺陷、工作单元、测试和证据映射 |
| [dynamic_assurance_plan.md](dynamic_assurance_plan.md) | PR/Daily/Weekly/Monthly 调度、SLI、freshness 和自检 |
| [migration_rollout_plan.md](migration_rollout_plan.md) | shadow、canary、cohort、切换、回滚和 legacy 删除顺序 |
| [legacy_plan_disposition.md](legacy_plan_disposition.md) | 不改旧文件前提下的状态更新和降级/取消建议 |
| [plan_self_audit.md](plan_self_audit.md) | 对抗式检查依赖、虚假完成、弱模型跑偏和保证边界 |
| [findings.md](findings.md) / [progress.md](progress.md) | 计划依据、冲突风险和编制审计轨迹 |
| [PLAN_MANIFEST.md](PLAN_MANIFEST.md) | 最终文件 hash、编制范围和并发交接清单 |

实施者必须按 Phase 0 → 11 顺序推进；单个 phase 内只按 registry 已满足依赖领取任务。任何人不得仅凭本文件摘要跳过对应 runbook、场景矩阵和原子任务卡。

## Errors Encountered

| 编号 | 错误/风险 | 次数 | 处置 |
|---|---|---:|---|
| P-E001 | 用户明确提示其他程序也在调用 planning-with-files，存在同名计划并发覆盖风险 | 1 | 创建全新专属目录；启用写前 hash、mtime、小补丁和冲突即停协议 |
| P-E002 | company-wiki CodeGraph 可用但落后当前 HEAD，不能只凭 healthy 状态作为结构证据 | 1 | ZR-001 强制记录 indexed commit/freshness；实施前经授权重建或标 blocked |
| P-E003 | 计划编制期间 revenue HEAD 从 `5f76fcf...` 漂移到 `ac6ac357...`，另有程序新增代码/证据 | 1 | 不覆盖、不纳入本任务；未来实施必须重新冻结 triplet 并重放，旧行号仅作线索 |
| P-E004 | 初版任务依赖包含矿业 ADR 顺序不足、ZR-709 自环表达和 soak 口径不一致 | 1 | 对抗式自审已修正；Phase 0 仍需用机器 DAG/registry validator 防复发 |
