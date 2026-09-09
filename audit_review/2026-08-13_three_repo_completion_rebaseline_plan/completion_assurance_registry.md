# CA 工作单元注册表：证据、动态审核与最终关闭

> 本表补足冻结的 92 个 `ZR-*` 产品工作单元。所有 `CA-*` 与 `ZR-*` 初始状态都是 `pending`。  
> 实施者必须按冻结 `implementation_runbook.md` 的 20 步卡片执行；实施者不能自行标 `accepted`。
> **本表不是任务入口。** 只能从根 [audit_review/README.md](../README.md) 的唯一`current_next`领取卡片；当前只有CA-001可领取，禁止在本表中自行挑卡或并行启动。

## 0. 通用卡片约束

每个 CA 单元必须在领取时补齐：精确 base triplet、plan/registry hash、allowlist、禁止目录、CodeGraph caller delta、RED 命令、正/负/fault/mutation、side-effect budget、证据路径、独立 reviewer 和 rollback。空一项即不能进入 `red_proved`。

状态枚举只能是：`pending / preflight_locked / red_proved / implemented / focused_green / triplet_green / real_tier_green / independent_review / accepted / blocked / superseded / already_satisfied`。状态与说明分字段；禁止 `accepted on ...` 一类自由文本。

## Phase 0：真实基线与历史迁移

### CA-001：计划输入锁与并发 CAS

- 依赖：无。
- 目标：冻结本目录、功能 annex、旧 FCAP、三仓和 shared resources 的 `path,size,mtime,SHA-256`；建立单 writer、TTL、owner 和 compare-and-swap。
- RED：另一个进程在领取后修改 registry/plan，旧工具仍允许 last-write-wins。
- 动作：实现 plan manifest validator 和 lock protocol；只允许最小 patch；冲突自动释放工作单元并要求重读三方合并。
- 正/负例：无变化可领取；任一 hash 漂移、过期锁、冒名 owner、两个 writer 同时提交均拒绝。
- side effects：只允许 assurance 目录；三个产品仓、旧计划、catalog、roots 零写。
- 验收：10 轮并发 mutation 无丢更新；本计划所有输入可离线重算；锁失败不会写半状态。

### CA-002：current triplet、upstream、dirty 与环境冻结

- 依赖：CA-001。
- 目标：记录三仓 40 位 HEAD/branch/upstream/remote-base/dirty allowlist、Python/Node/SQLite/Git/OS、installed skills、config/runtime policy/catalog schema/data fingerprint。
- RED：任一 sibling HEAD 改变、manifest pin 陈旧、未设置 upstream、dirty 文件未登记，旧 gate仍绿。
- 动作：区分“可验证 local-only commit”与“已推送 upstream”；两者都可审查，但发布资格不同；Git权限/unsafe-directory须分类为基础设施错误，不能伪装 ancestry failure。
- 验收：精确 equality gate；任何字段漂移立即使结果 stale；不会因只验证 baseline descendant 放行新组合。

### CA-003：CodeGraph 新鲜度与 production reachability manifest

- 依赖：CA-002；需要三个仓独占索引窗口。
- 目标：每仓重建/验证 CodeGraph，记录 indexed commit、parser/version、files/nodes/edges；为核心用户旅程冻结 entrypoint→caller/callee→跨仓进程边。
- RED：旧索引仍可被当 current 证据；只测 helper/seam 的测试被标 full-chain。
- 动作：为 CatalogStore writer initializer、v1 scanner、RootPolicy flags、artifact bindings、ProcessingDemand、filing handle validation、source preparation、publication registry、dynamic runners生成 production caller report。
- 必查旁路：`resolve`、`latest/ensure`、provider acquisition、`close_gap` 后重解是否消费同一个必填 RuntimeContext；任何 `runtime_policy=None` 回退和“结果先走v1、回执后贴v2 hash”都登记为阻断 finding。
- 验收：indexed commit 精确等于 CA-002 HEAD；已删除符号不出现；每个 full-chain claim 至少一条真实 production path 和 subprocess trace。

### CA-004：旧 71 FC、R0～R9 与 FC-150x 机器处置表

- 依赖：CA-002、CA-003。
- 目标：把 `completion_audit.md` 的逐 Phase 结论固化到严格 registry；每项记录 `implemented_not_verified / contradicted / stale / pending / retained_asset / superseded`、最小真实 claim、新 ZR/CA successor 和证据 hash。
- RED：自由文本 `accepted`、自依赖 FC-1301、缺 filing receipt、Phase14 不在计数仍能过。
- 验收：71 FC + 10 rollout waves + 5 closure items 无遗漏/重复；DAG 无环；每个 contradicted/stale/pending 都有 successor；旧 owner 未写 terminal notice 前旧执行入口仍只读冻结。

## Phase 1：Evidence 与 Closure 2.0

### CA-101：严格工作单元状态机与 DAG

- 依赖：CA-004。
- 目标：用 machine JSON/YAML registry 替代 Markdown substring 判定；状态变化采用 CAS、依赖门和单向合法迁移。
- RED：非法状态、状态中夹日期、未知依赖、自依赖、环、pending→accepted 跳跃、两个 reviewer同时写。
- 验收：property test生成非法图全部拒绝；渲染 Markdown 只作只读视图；closure只读机器真源。

### CA-102：内容寻址 receipt schema

- 依赖：CA-101。
- 目标：implementer、reviewer、closure receipt 分型；绑定 WU、base/result/current triplet、plan/policy/config/schema/command/scenario/sample hashes、touched files、side effects、时间、身份。
- RED：commands/scenarios为空、`policy_sha256=not-applicable` 滥用、只填40/64位伪hash、结果commit不存在、改动文件未列出仍通过。
- 验收：receipt canonical hash 可重算；未知字段/版本按N/N-1策略；任何内容篡改必红。

### CA-103：revision selector 与独立 reviewer 配对

- 依赖：CA-102。
- 目标：不再“取第一个 implementer receipt”；显式选择最新有效 revision，验证 supersedes 链、实现者/复核者分离、reviewer→implementer hash、finding closure。
- RED：FC-504 类 r1/r2 混淆、主 receipt review=pending、reviewer接受旧revision、reviewer=self、缺 reviewer 文件。
- 验收：唯一有效 pair；rejected/changes_required revision不能被另一旧 accepted覆盖；未关闭 P1/P2/P3 finding有强制后继且阻断 phase exit。

### CA-104：命令注册与本次执行 attestation

- 依赖：CA-102。
- 目标：command registry 记录 argv、cwd、env allowlist、timeout、expected tier/collected、side-effect budget；receipt引用本次不可变 result artifact，不引用历史命令文字。
- RED：改短命令、少收集测试、`|| true`、结构化业务失败但process=0、基础设施错误伪作pass、复用旧stdout。
- 验收：result含exit/业务outcome/collected/pass/fail/skip/duration/stdout-stderr hash；同命令current code重放差异可见；秘密值不入 receipt。

### CA-105：197 场景逐 tier machine result registry

- 依赖：CA-104；冻结旧95与新102矩阵hash。
- 目标：每个 `scenario × required tier × triplet` 有 fixture/sample hash、oracle、预算、实际result、evidence path、freshness；marker只映射测试，不算pass。
- RED：`pending:FC-*` fixture、`scenario-defined`预算、缺evidence path、只出现SCENARIO文本、receipt status pending/blocked、T1替代T2。
- 验收：required result总数机器可算；无placeholder；缺一项即closure红；deferred由依赖状态动态计算而非静态前缀。

### CA-106：独立 oracle 与 side-effect ledger

- 依赖：CA-104、CA-105。
- 目标：标准化八阶段结果、provider/parser/LLM/worker/artifact read、DB/DDL/migration/publication、root fingerprints和锁等待；计数来自spy/journal/OS，而非结果倒推。
- RED：伪填download/parser/LLM=0、外部root被写、DB/WAL/SHM变化、失败吞掉前阶段、root样本被另root副本替代。
- 验收：被测summary与独立ledger不一致即红；隐私路径脱敏但hash可核；T2生产roots始终零写。

### CA-107：三仓 Closure 2.0

- 依赖：CA-101～CA-106。
- 目标：搜索 revenue/filing/wiki 三仓全部 receipt；强制每个 required WU/release wave/scenario有唯一有效证据；验证精确 triplet、dirty/upstream、config/skill/data、freshness、review pairing、commands、rollback和动态窗口。
- RED：依次删除 filing receipt、reviewer、evidence；篡改hash；切换 sibling HEAD；留下FC150x pending/R9；使用陈旧 current manifest；每种都必须给精确原因。
- 验收：当前旧计划被诚实判 incomplete且原因集合包含已知缺口；不得只显示“剩五项”。

### CA-108：Closure mutation/negative suite

- 依赖：CA-107。
- 目标：建立至少30个critical mutation，覆盖漏仓、漏receipt、错revision、自签、命令缩减、skip/blocked、旧triplet、dirty、无schedule、半报告、代理SLO、伪零、缺样本、R9未过、finding未关。
- 验收：critical mutation kill=100%；新增 closure 分支必须同时新增 mutation；mutation runner失败不能用skip代替。

### CA-109：旧 gate 隔离与兼容输出

- 依赖：CA-107、CA-108。
- 目标：旧 `closure_gate.py/receipt_validator/scenario_coverage` 只能作为 migration reader 或被显式替换；workflow/release不得继续调用旧语义。
- RED：故意只运行旧 gate可得到绿时，新 architecture gate必须红。
- 验收：production/CI caller只指向Closure 2.0；旧历史 ledger仍可只读展示；无双写状态源。

## Phase 2：CI、调度与自然时间证据

### CA-201：跨仓 current-candidate PR fan-out

- 依赖：CA-107、ZR-105、ZR-901。
- 目标：任一仓PR生成精确 candidate triplet，对受影响三仓运行相同 required T0/T1/quality/schema/docs/receipt/mutation；旧pin仅用于N-1。
- RED：更改 filing 但只跑 filing；manifest落后HEAD；wiki coverage `|| true`；source E2E缺席。
- 验收：三仓check名称/contract一致，禁止浮动clone；collected/skip delta受门控；失败可追到具体仓/场景。

### CA-202：Daily T2 实际 scheduler

- 依赖：ZR-806、CA-107。
- 目标：真实 Windows runner每天抽样companies/dayu/Dropbox unique样本，测试Reader/live WAL、exact reuse、artifact/readiness、零写、锁和SLO。
- RED：脚本存在但schedule不存在、job停跑、样本不unique、resolver SQL代理、root fingerprint不进入判断。
- 验收：平台schedule/权限/runner身份可查；报告≤24h、atomic complete、精确triplet；缺run本身告警并阻断release。

### CA-203：Weekly/发布前 T3

- 依赖：ZR-805、CA-107。
- 目标：真实CN/HK/US provider在临时wiki做首次授权下载、二次零下载、amendment、single-flight和provider drift。
- RED：网络/凭据缺失被记pass、real tool tests永久ignore、下载写入真实wiki。
- 验收：报告≤7d；blocked也阻断release并发告警；provider/canonical调用精确对账。

### CA-204：Monthly broker/mine/forecast 泛化审核

- 依赖：ZR-510、ZR-609、ZR-709、CA-107。
- 目标：轮换真实broker样本、紫金shadow、第二矿企、非矿企；复验表格/错归、逐矿bridge、draft/formal、backtest/confidence。
- RED：硬编码紫金/601899/Dropbox仍能过固定样本。
- 验收：报告≤35d；样本registry固定+轮换；样本缺失是blocked；产品代码特例扫描为0。

### CA-205：原子报告、freshness、告警与 release 消费

- 依赖：CA-202～CA-204。
- 目标：pending临时文件→完整校验→原子publish；dashboard/release读取同一schema；告警送达有ack/重试；过期结果不可续命。
- RED：进程中断半报告、future timestamp、旧绿复制、告警sink失败、runner rc被吞。
- 验收：每种故障release红；恢复幂等；报告自身hash、triplet/sample/command完整。

### CA-206：不可豁免自然时间 soak

- 依赖：CA-205、ZR-904、ZR-905。
- 目标：累积连续7 Daily、2 Weekly、1 Monthly、1 alert drill；记录失败/恢复，禁止手工改时间或复制报告。
- 验收：窗口由可信时间和run IDs计算；任一必需run缺失/陈旧/样本重复不计；未满只可pending。

## Phase 3：终审、R9 与旧计划关闭

### CA-301：clean checkout 独立复放

- 依赖：全部mandatory ZR/CA功能单元、CA-206。
- 目标：独立 reviewer在三个干净checkout、精确candidate triplet重建环境；不复用实施者工作树/cache/未登记fixture。
- 验收：T0/T1全跑、required T2/T3/Monthly证据新鲜；所有receipt/hash重算；结果与candidate closure一致。

### CA-302：三类真实用户旅程终验

- 依赖：CA-301。
- 目标：从 revenue入口重放紫金复杂canary、第二异构矿企、非矿企；覆盖所有roots、existing/partial/missing/stale/amended、worker、下载、第二次复用。
- 验收：每条八阶段receipt、side-effect budget、输出/回溯/诚实gap；任何公司特例或绕过filing链失败。

### CA-303：架构、硬编码与代码质量终审

- 依赖：CA-301。
- 目标：CodeGraph production caller/impact、dead dual paths、root/company/path hardcode、模块边界、strict types、复杂度趋势、docs/schema/skill drift。
- 验收：core root/company硬编码0；legacy caller0；关键新/改函数CC≤10；历史高CC逐波下降而非只冻结；required CI无`|| true`。

### CA-304：R9 分批删除与真实 rollback drill

- 依赖：CA-206、CA-302、CA-303、ZR-1008。
- 目标：把当前 `R9_GATE=1` 四个RED转绿并分批移除 `_scan_root_v1`、legacy bridge/flags、无生产读者backfill/promoter；每批全矩阵和cohort rollback。
- 禁止：为了让测试绿只删测试/改skip；在两个动态周期legacy hit非0时删除；一次性大爆炸。
- 验收：符号/flags/callers均不存在；新链current journeys绿；真实rollback/re-activate结果一致。

### CA-305：六问题 machine closure ledger

- 依赖：CA-302～CA-304。
- 目标：对 `project_goal_and_pain_points.md` 六个成功问题生成需求→证据→场景→triplet→reviewer映射；不允许总体百分比替代单项。
- 验收：每问 `pass` 且所有子项pass；known limitation只能是非目标外延或诚实data gap，不能掩盖已承诺功能。

### CA-306：旧计划 terminal closure 与唯一入口切换

- 依赖：CA-305。
- 目标：由旧计划单一owner添加只读 terminal notice：`closed_superseded_incomplete`，指向新 closure ledger；保留所有历史receipt/hash；关闭R9/FC150x旧领取入口。
- 验收：71 FC、R0～R9、FC150x全部有最终successor结果；旧历史不改写；根`audit_review/README.md`始终是唯一可领取入口。

## 4. 主依赖链

```text
CA-001 -> CA-002 -> CA-003 -> CA-004
 -> CA-101 -> CA-102 -> CA-103/104 -> CA-105/106 -> CA-107 -> CA-108 -> CA-109
 -> ZR product phases 1..8
 -> CA-201 -> CA-202/203/204 -> CA-205 -> CA-206
 -> ZR rollout through ZR-1008
 -> CA-301 -> CA-302/303 -> CA-304 -> CA-305 -> CA-306
```

`ZR-1009` 与旧 Phase14 R9 由 `CA-304` 统一执行，不能并行。旧 `ZR-1101～1105` 的业务意图由 `CA-301～306` 取代；不得再运行一套较弱 closure。
