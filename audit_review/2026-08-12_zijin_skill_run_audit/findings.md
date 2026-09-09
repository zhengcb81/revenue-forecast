# 紫金矿业五年收入预测技能调用 — 发现记录

## 发现 1：本次运行采用“原生技能输入”和“旁路观察记录”分离

- 日期：2026-08-12
- 给 revenue-forecast 的业务任务仅为“紫金矿业，预测未来五年收入增速”。
- 用户额外关心的 filing reuse、Dropbox、矿山颗粒度、MD/切片/标签、网络新闻等不作为技能提示词注入，只在运行后按实际行为审计。
- 影响：可以区分技能原生能力与被审计提示诱导出来的行为。

## 发现 2：技能文件读取遇到权限边界

- `planning-with-files/SKILL.md` 已完整读取。
- `revenue-forecast/SKILL.md` 位于用户级技能目录，首次读取被当前 restricted filesystem 拒绝。
- 已通过权限系统获得只读访问，完整读取 revenue 与 filing-fetch 两份技能契约；没有通过复制、猜测或旧文档绕过。

## 发现 3：原生 revenue 工作流要求 filing-fetch 复用优先，下载不是默认动作

- revenue 技能指定唯一生产入口为 `scripts/source_preparation.py`，它应驱动 filing-fetch → SourceBundle → artifact selection → RevenueSourceRecord/reuse receipt。
- 默认调用必须是 read-only reuse；只有显式 `--allow-download` 才能下载。用户本轮要求观察下载行为，但没有直接授予“缺什么就下载什么”的开放授权，因此先执行只读复用，若缺失则记录缺口，不擅自加下载开关。
- “已索引”不等于“可复用”：必须是 active、capture-ready、位于注册 reusable root，并通过身份、期间、hash、HTTPS、发布日期等校验。
- filing-fetch 当前技能说明自己只获取监管财报；券商研报、新闻不属于该工具的下载范围，后续需分别观察 revenue 工作流是否采用其他采集路径。

## 发现 4：正式预测不能靠自由文本补数字

- revenue 技能要求至少两期历史收入、九维覆盖、管理层沟通完整性、参数级证据、矿业资源业务模型、低/基准/高情景和正式强校验。
- 正式结果只能来自 `scripts/revenue_forecast.py` 生成且验证通过的 JSON/Markdown；如果输入或来源门失败，不能用手写预测冒充正式结果。
- 这意味着本次不仅要观察技能搜索了什么，还要确认最终数值真正进入已验证 artifact。

## 发现 5：九维覆盖并不等于矿山颗粒度，矿业必须增加专属维度

- 九个核心维度是 company foundation、growth curve、industry market、competition、capacity、technology、policy、customers、demand；每项必须映射到实际使用参数、登记 data gap 或解释 immaterial。
- 对矿业还允许且应考虑 `reserves`、`processing`、`regulatory_permits` 等自定义维度。因此后续审计将检查技能是否主动增加这些记录，而不是仅用九维模板声称覆盖矿山、储量和许可。
- 储量、产量、金属价格或产能不能直接等于确认收入，必须经过可交付产量、销售/结算价格、产品结构及会计确认链路。

## 发现 6：增长驱动必须从模型参数和外部证据双向闭合

- 每个根驱动必须映射到基准情景真实使用的参数，并列因果链、领先指标、证伪条件和反证搜索。
- 证据三角验证要求至少两类证据和两个不同来源；多篇转述同一事实不算独立验证。
- 矿山投产、扩产或储量增长只能成为“可能供给”；还需要需求、价格、可交付约束和收入确认才能进入收入路径。

## 发现 7：运行记录可以证明结构完整性，但不能自行证明外部动作真实性

- 正式 artifact 的 hash、输入输出绑定和确定性重算可由程序验证。
- 工具是否真的调用、网页是否真正打开、搜索是否穷尽、源字节是否来自声明 URL，仍依赖宿主事件记录。
- 因此本次 progress 将保留实际工具调用顺序，最终还需提供 `TRUST_BOUNDARY.md`，明确结构证明与宿主信任的边界。

## 发现 8：管理层沟通门要求六类官方资料逐类结案

- 必须分别检查最新年报、业绩发布、业绩会、投资者演示、战略沟通和年报后的重大公告。
- 每类只能是 `checked`、带机器搜索事件的 `not_available`，或带原因码的 `not_applicable`；不能把“没有看到”写成“没有目标”。
- 任何落在五年期内且与确认收入可比的重大目标必须进入至少一个情景；含糊的累计/年度/run-rate 说法不能直接用于模型。

## 发现 9：技能的矿业模型支持储量消耗，但矿山级数据仍需研究者构造

- 指引建议在有期初/新增/消耗/期末储量时用 `reserve_depletion`，并强制库存流量和年度连续性；若只有可售产量，可用 `resource`；受加工能力约束时用 `capacity_utilization`。
- 对紫金矿业这种多金属、多矿山企业，单一“金当量储量”可能掩盖金、铜、锌、锂等不同单位、价格与回收率。后续需观察原生技能是否建立多个经济上不同的收入曲线，而非把所有矿合并进一个直接增速。
- 逐矿山逐年营收不是技能最小硬门，但用户明确关心；最终应把“技能原生是否产生”与“审计补充能否推导”分开报告。

## 发现 10：模型选择存在明确降级顺序

- `reserve_depletion` 需要每年 opening + additions − depletion = closing，以及跨年连续；信息不足时不能伪造储量桥。
- `resource` 只要求可售量 × 实现价格，更适合按金属建立收入曲线；`capacity_utilization` 适合加工能力约束。
- `direct_growth`/`direct_revenue` 只能作为透明回退，并会降低显式模型覆盖和置信度。后续将记录实际用了哪一级，而不是只看报告是否有数字。

## 发现 11：正式输入的颗粒度比一般研究报告高得多

- 每个参数必须具有稳定 ID、严格 `FYyyyy`、维度、时间口径、单位/币种/scale、类型、理由与 claim 绑定。
- 历史收入、报告总额、分部基数和调整必须对账；低/基准/高场景同一分部必须使用同一模型。
- 自定义 reserves/processing/permit 覆盖记录可以进入 schema，但其参数仍必须真正用于模型或明确登记 gap；仅在叙事里罗列矿山不算模型覆盖。

## 发现 12：正式交付必须同时保留 JSON、由同一 JSON 渲染的 Markdown 和信任边界

- 输出 validator 会重算分部公式、确认收入、约束、汇总、CAGR、增量贡献、敏感性、驱动归因、来源/claim/capture 绑定及 publication receipt。
- Markdown 不能由模型自由编写正式数字；必须由同一个已验证 JSON 渲染。聊天说明可以解释，但不能新增或覆盖正式数字和结论。
- 用户关心的逐矿山表若不在正式 schema 中，需要明确标为补充审计表，而不能和强校验的正式分部路径混为一谈。

## 发现 13：构造输入的推荐顺序本身也是本次要审计的行为

- 原生顺序是 template → 填值/摘录 → lint collect-all → fix hashes → validate-only verbose → 正式生成。
- 捕获对象严格只有九个字段；snapshot hash 只能来自捕获工具，不能由 hash 修复脚本伪造。
- 本次将记录技能是否遵循这一顺序、经历多少校验轮次，以及是否因为难度退回自由文本。

## 发现 14：冻结快照有严格不可变版本纪律

- 快照绑定完整 input、正式 forecast result、company、as-of、版本、引擎和 schema；输入任何字段变化都必须使用新版本，不能覆盖已有快照。
- 本次若正式 artifact 通过，将创建独立版本快照并验证确定性；若只能生成 draft，则按代码实际能力和技能硬门记录，不能将 draft 宣称为正式冻结成果。

## 发现 15：技能内部出现文档引用漂移

- `compliance-contract.md` 要求读取 `docs/session-checklist.md` 并按其第 7 节交付 `TRUST_BOUNDARY.md`。
- 在选定的 `.agents/skills/revenue-forecast` 技能目录中，该精确路径不存在。
- 递归枚举确认技能包含全部 `references/`，但不含任何 `session-checklist` 或 `trust-boundary` 文件；属于真实的打包/文档引用缺失，不是路径拼写或忽略规则假象。
- 这是技能包自身的可执行性问题；本轮不自行补文件或修改技能。若仓库副本存在模板，只能作为显式 fallback 并记录来源，不能声称技能包完整。

## 发现 16：技能主文档与 schema 参考存在版本漂移，需要以运行时代码裁决

- SKILL 声明当前 forecast schema 3.7、skill 4.0.0；`input-schema.md`、`output-schema.md` 和 `input-construction.md` 标题仍以 3.6 为主。
- 技能包包含 `schema-migration-3.6-to-3.7.md`，说明这可能是增量文档设计，但对弱模型存在误用旧 skeleton 的风险。
- 迁移文档说明 3.7 没有新增输入必填字段，只需把 schema_version 从 3.6 改为 3.7；新增的是输出 attestation、publication registry 和更严格完整性校验。
- 生成器应自动输出 3.7。下一步仍需核对本仓库当前运行时代码与用户级技能包是否同版本，构造输入时以实际将运行的代码和生成器为真相。

## 发现 17：3.7 正式输出即使通过也可能是 `unattested`

- 没有配置可运行的 `REVENUE_ATTESTATION_PROVIDER` 时，publication receipt 会标记 `unattested`；结构与计算仍可验证，但 invest-* 默认拒绝消费。
- 本次必须如实报告 attestation 状态和 publication registry 写入副作用，不能把正式 schema 等同于宿主签名。

## 发现 18：运行前代码基线已变化，技能包与当前关键运行文件一致

- 2026-08-12 23:04:23 +01:00：revenue `fb77fe1b982d378d7c7af2e98d79f842ee8be930`；filing `b7ef9cca0747b108184f00e3e519aeb046be9d2b`；wiki `460d2730719acb6e4fdf59886c568c847d10d028`。
- 三仓均在 `fcap` 分支且未配置 upstream，因此不能复用 2026-08-09 的 stable-triplet 结论。
- 用户/其他 agent 既有 dirty：revenue 的 `assurance/fc/FC-1203/00_wu_card.md` 和旧全面计划 findings；company-wiki 的 `.claude/settings.local.json` 删除、`llm_cost_log.csv` 修改。filing-fetch 工作树没有可见改动。本轮必须避开这些文件。
- 用户级技能包与当前 revenue 仓库的 SKILL、`revenue_core.py`、`source_preparation.py`、`generate_input_template.py` SHA-256 完全相同，故本次从仓库执行关键脚本不会混用旧版本。

## 发现 19：当前 revenue 生产入口仍是明确的单链编排

- CodeGraph 当前健康：143 files、2522 nodes、5194 edges；相比旧审计代码规模已有变化，因此本次只信当前图和实际运行。
- `prepare_source(request, allow_download=False, ...)` 是明确入口：子进程调用 filing-fetch client；只有调用者传入 `allow_download=True` 时才加 `--allow-download`。
- 代码把 filing-fetch 非零退出转换为 RuntimeError，说明 reuse-only miss 不会自动升级为下载；是否下载可由命令 trace 明确判定。
- CodeGraph 返回了 `reuse_receipt.download_calls` 的契约测试，但测试存在不等于真实紫金矿业调用成功，后续必须以实际输出验证。

## 发现 20：当前生产配置确实登记了三个数据湖 root，但策略仍是旧 kind 级模型

- revenue 与 filing-fetch 均通过显式配置定位 company-wiki；revenue 配置还定义了 CN/HK/US acquisition adapter 和 staging root。
- company-wiki `source_catalog.yaml` 当前 roots：`companies`（priority 10）、dayu portfolio（20）、Dropbox Stock（30）。
- `reusable_root_kinds` 为 `[company_raw, dayu_portfolio, directory]`，所以 Dropbox 的 `directory` kind 在配置层被放行；这只能证明配置意图，不能证明紫金矿业 Dropbox 文档已经 active/capture-ready 或生产复用成功。
- 配置注释仍提到 filing-fetch path allowance，而最新技能说明说 filing-fetch 配置只负责定位 wiki root；存在文档/注释漂移，后续以实际 handle validation 和运行 trace 为准。

## 发现 21：company-wiki 当前索引健康，但预处理能力分散在多套脚本中

- CodeGraph 当前为 455 files、9232 nodes、20842 edges，索引可用。
- `scripts/` 同时存在 `batch_process`、`build_extracts`、`extract_v2`、`pdf_extract_v2/v3`、`reprocess`、`tag_segments`、`search/query`、`collect_news/reports`、worker/scheduler 等多套入口。
- 目录结构只证明存在能力，不证明 revenue 原生运行会调用哪一条、目标文档已预处理或 worker 可安全提升优先级；后续必须查目标文档状态与实际调用者，不能用脚本存在替代行为证据。

## 发现 22：预处理与 worker 状态存在正式接口，但 SourceBundle 生产可达性仍需实跑验证

- `SourceCatalogService` 暴露 normalize、backfill text fingerprints、extract sections、summarize 等处理方法；worker CLI 有 `worker-status` 非 worker 子命令入口。
- 处理队列按 priority 排序的代码存在，但用户只授权调查，故本次不会创建任务、改 priority 或调用任何写入处理方法。
- `query_source_bundle` 当前图中只显示 service method 和两个 contract tests；这与 revenue 技能声称 source_preparation 经过 SourceBundle 之间仍需通过 revenue 当前调用链和实际返回 envelope 核对。

## 发现 23：company-wiki CLI 将只读检查和写入处理混在同一命令面

- 同一 CLI 同时提供只读 `status/query/evidence-list/sections-list/resolve/worker-status`，以及会写入的 `scan/normalize/summarize/extract-sections/ensure/close-gap/worker-*` 等。
- `worker-status` 没有 JSON 选项，但属于明确的只读状态入口；后续可以调用并保存原始文本。
- 本次操作 allowlist 仅包含只读子命令。即使发现目标文档未处理，也只记录可能的 normalize/extract/summarize 或 job priority 机制，不执行。

## 发现 24：后台 worker 正在运行，预处理总体积压很大

- worker PID 17012，desired=enabled、runtime=running、code_match=true，当前阶段 normalizing，并持有 live operation lock；本次不会暂停或调整它。
- catalog 指标：23,521 documents、13,830 active documents、46,581 physical locations、7,962 artifact rows。
- Markdown：3,358 completed、127 partial、20,020 pending；LLM summary：2,728 completed、122 pending、650 permanent failures。
- 这说明“文件已 index”与“已有可复用 MD/摘要/切片”在总体上差距很大；必须对紫金矿业目标文档逐个查，而不能按全局完成率推断。

## 发现 25：动态状态暴露多项非本任务但相关的健康问题

- 最近 scan 为 `completed_with_errors`：Dropbox 中一个空 XLSX 引发持续错误；另有 6 个 missing locations、16 次历史 interrupted scan。
- scheduler 的 `last_prune_error` 为 `AttributeError: 'SourceCatalogWorker' object has no attribute 'project_root'`。
- 标称只读 `status` 在受限只读 DB 下尝试写入并失败；说明状态查询初始化路径可能隐含 schema/migration/write 行为。
- 这些不会在本次修复，但会作为“额外发现”纳入最终建议。

## 发现 26：本次不能仅靠 catalog 前后 mtime 归因技能副作用

- 基线 DB 约 49.62 GB，worker 在本次运行前已持续 normalizing；它会独立写 catalog、artifact 和日志。
- 因此下载/索引/处理副作用必须依靠 filing/revenue receipt、目标文件精确路径/hash、调用参数和目标级 catalog 行变化联合证明；不能把整个 DB mtime 变化算到技能头上。

## 发现 27：目标级只读查询入口足以先建立紫金矿业基线

- `identify` 支持 query + market/exchange hint；`--refresh` 会刷新身份缓存，本次禁止使用。
- `query` 表面可按 text、entity、document_kind、source_status 和 limit 查询 catalog，但实际在 restricted read-only DB 下也尝试写入并失败；不能作为真正只读的审计入口。

## 发现 28：紫金矿业身份可由本地 verified cache 精确解析

- `identify --query 紫金矿业 --market CN` 返回唯一 verified、active、official-name exact 身份：SSE 601899，security_id 601899，cninfo org_id 9900004143。
- 未使用 `--refresh`，没有请求网络刷新身份缓存。
- 后续所有 filing 请求可用公司原名 + CN market；无需手工注入 entity/security_id，符合 filing-fetch schema 1.1。

## 发现 29：company-wiki 的“只读”命令并非真正只读

- `status` 与 `query` 均在数据库为只读时失败为 `attempt to write a readonly database`，而 `identify` 和 `worker-status` 成功。
- 推断是 CLI/service 初始化对部分子命令触发 schema/状态写入；这是从实际失败得出的行为证据，具体写点尚未做代码根因审计。
- 对用户关心的可审计复用不利：读者必须给予写权限才能查询，会模糊“零副作用”证明。后续建议把 audit/query path 设计成 SQLite 真正 read-only connection 并以测试锁定。

## 发现 30：本机具备 sqlite3 原生只读工具，可绕开有副作用的 CLI 做审计

- `C:\Miniconda\Library\bin\sqlite3.exe` 可用，支持 `-readonly`。
- 该路径只用于审计 catalog 表和目标行，不调用任何 migration/service 初始化；同时配合 `PRAGMA query_only=ON`。
- 首次包装命令在 JavaScript 解析层因引号失败，sqlite3 实际未启动，不产生数据库副作用。

## 发现 31：显式只读 catalog 查询已验证可行

- `sqlite3 -readonly` + `PRAGMA query_only=ON` 成功读取 18 张表，没有触发 service 初始化。
- 目标审计所需关系完整：documents ↔ locations/sources/entities；artifacts 含 role、path、generator、status、source_sha256；evidence_spans 含 locator、页码、段落/表格索引、raw_text、parser/status。
- 这允许逐文档验证“原文件→MD/摘要→切片→来源 hash 绑定”；标签若不在显式列中，需继续检查 metadata_json/span_json，而不能假定存在。

## 发现 32：紫金矿业 2024/2025 年报已经存在，2025 年报跨 companies 与 Dropbox 精确去重

- FY2025 年报：document hash `01819e...f343d`，80 MB，active，company_raw 和 Dropbox 两个 original location 指向同一 document；发布日期 2026-03-20，fiscal_year=2025，cninfo provider_document_id=1225023658。
- FY2024 年报：document hash `004f73...77a89`，32 MB，同样 active 且在 company_raw/Dropbox 两根精确去重；发布日期 2025-03-21。
- 目标查询未发现 dayu_portfolio 中的紫金矿业命中。
- 因此以 2026-08-12 为 as-of 的“最新年报”已在可复用 company_raw 中存在，原生 filing-fetch 没有理由下载 FY2025 年报；实际调用必须证明这一点。

## 发现 33：财报已有 MD 和大量切片，但当前绑定不满足新 artifact reuse 契约

- FY2025：normalized=`partial`、summary=`completed`、14,118 evidence spans；FY2024：normalized=`partial`、summary=`completed`、16,986 spans。
- 两份财报的 artifact `source_sha256` 都是 null。按 filing-fetch 技能当前“source hash + producer binding”规则，这些派生物不能被当作 binding-valid reusable artifacts。
- 这很可能导致 source preparation 复用原 PDF，却无法复用现有 MD/summary，而需要重新 capture/解析；必须以实际 reuse receipt 的 parser/LLM budget 验证。
- `partial` normalized 搭配上万 spans 也提示“有内容”不等于“解析完整”；后续要实测矿山/储量表是否可检索。

## 发现 34：Dropbox 六份券商研报全部已索引但完全未预处理

- 已发现 7 份 broker_research：2024-03 长江、2024-12 天风、2025-01 国盛、2025-03 民生、2026-03 国联民生与太平洋、2026-04 太平洋。
- 七份均 active、原 PDF 存在，但 `published_date=null`、artifact_count=0、evidence_span_count=0；其中长江证券文档 entity 仍是 unresolved。
- 这意味着它们虽然“被 index”，却没有 normalized.md、summary、切片或可验证 publication date，当前无法直接满足 revenue 的 source/capture/claim 契约。
- 本轮不现场 normalize、不调 worker priority；最终建议需解决 indexed→processed→bound→searchable 的统一状态机，而非为紫金矿业写特例。

## 发现 35：`.source.json` 被错误当作独立 annual_report 进入处理队列

- Dropbox 两份 PDF sidecar 被扫描成四个额外 active annual-report documents：既有带 location 的 JSON 源，也有无 location 的 ghost document。
- sidecar JSON 甚至生成 normalized/summary 和 1 个 evidence span，而真正 broker reports 没有任何处理产物。
- 部分 sidecar artifact source_sha256 为 null/空字符串，进一步污染 artifact 统计和 worker 优先级。
- 这是 admission/classification 的系统性缺陷：metadata sidecar 应绑定原文档而非竞争 annual_report 处理资源；需用一般性 sidecar-role 契约和 E2E 防回归。

## 发现 36：原生 revenue→filing-fetch→company-wiki 的第一次真实调用在“只读复用”入口即失败

- 命令没有 `--allow-download`，请求内容只有紫金矿业/CN/annual/FY2025/as-of。
- 完整错误链：source_preparation exit 1 → filing-fetch client exit 2 → filing-fetch fatal → company-wiki resolve exit 1 → `attempt to write a readonly database`。
- 这证明 E-006/E-007 不是审计 CLI 个别问题：正式复用主链的 resolve 同样隐含写权限依赖。
- 在严格零写环境中，filing-fetch 甚至无法读取一个已存在且 capture-ready 的 company_raw 年报；“reuse-only”当前不是操作系统层面的 read-only。
- 本次尚未下载、解析、LLM 或生成 source record；不能把失败调用算作复用成功。

## 发现 37：授予 catalog 写权限也没有使 reuse-only 主链可靠工作

- 第二次运行是与第一次完全相同的 FY2025 request，仍无 `--allow-download`；权限升级只解决沙箱只读限制。
- 命令约等待 60 秒后，company-wiki resolve 报 `database is locked`；filing-fetch 将它包装为 `fatal`、`retryable=false`，再由 revenue 包装为 upstream failure。
- filing-fetch 技能声称 `catalog_locked` 可重试直到 deadline，但实际主链中的这个锁错误被错误分类为 fatal，因此没有进入契约中的 backoff/retry。
- worker 当前正在 normalize 并持有 operation lock。一个本应只读的 exact resolve 既需要写权限又会被 writer 锁阻塞，表明生产复用路径与后台处理缺少真正的读写隔离。
- 仍未发生下载、parser/LLM 调用或成功复用；下一步必须先查明锁/初始化路径，不能反复撞锁。

## 发现 38：只读 resolve 需要写权限和写锁的直接根因是 `CatalogStore.__init__`

- CodeGraph 源码显示每次构造 `CatalogStore` 都立即 `_initialize()`：创建父目录、`PRAGMA journal_mode=WAL`、执行全量 DDL、运行 additive migrations、seed 每个缺失的 fingerprint-state 行并 commit。
- 该初始化不区分 resolve/query/status 和写入命令；即使后续 `fetchall` 本身只读，构造阶段已经需要 schema 写锁。
- `_seed_fingerprint_state` 可能对所有缺状态文档批量 INSERT，因此所谓 reuse-only 请求不仅是“可能写一点运行元数据”，而可能执行真实数据补种。
- 在 49.6GB catalog + 正在 normalize 的 writer 下，这个设计必然造成锁竞争；根因是 read model 与 migration/write model 未拆分，而不是 filing 文档不存在。
- 系统性改进方向应是显式 `CatalogReader`/read-only connection、迁移只在受控启动/maintenance 执行、resolver 禁止 DDL/seed，并对 OS read-only DB 与并发 writer 建真实 E2E。

## 发现 39：filing-fetch 的重试器只认结构化 `catalog_locked`，SQLite 锁文本没有被映射

- `FilingFetchError.retryable` 仅对 `upstream_error`、`worker_paused`、`catalog_locked` 为 true；默认 code 是 `fatal`。
- `_run_company_wiki_json_retry` 只在捕获到 `exc.code == "catalog_locked"` 时指数退避。
- 当前 company-wiki CLI 将 `sqlite3.OperationalError: database is locked` 作为一般 failed JSON/非零退出返回；filing-fetch subprocess wrapper 没有把该形态归一到 `catalog_locked`，因此直接落入 fatal。
- 精确代码确认：只有 `structured.error_type == "CatalogOperationLockedError"` 才映射 `catalog_locked`；`OperationalError` 无论 error 文本是否 `database is locked` 都保留默认 fatal。
- 因此本次“契约声称会重试、真实却不重试”是确定的错误分类缺口，而非偶发日志格式。

## 发现 40：CodeGraph 对 `_run_company_wiki_json*` 的源码片段定位出现错位

- `codegraph_node(_run_company_wiki_json)` 返回片段实际从函数尾部继续到 retry；`codegraph_node(_run_company_wiki_json_retry)` 又返回了后续 identity 代码，而非完整目标函数。
- 结构位置/签名仍可信，但不能据错位 snippet 判断所有分支；下一步对已定位文件使用精确行读取，不重复搜索符号。
- 已按精确行读取完成核对；没有修改 filing-fetch。

## 发现 41：worker 会重启并连续占用写阶段，等待“自然空闲窗口”不是可靠复用策略

- 第二次状态采样时 worker PID 已从 17012 变为 21468，阶段从 normalize 转为 scan，仍持有 live operation lock。
- 这解释了为什么单次 30/60 秒等待不一定命中空闲；让用户手工等 worker 或暂停 worker 才能读 filing，不是可接受的数据湖读路径。
- filing-fetch 的 pause-around 只定义在“授权下载”步骤，reuse-only resolve 不会主动 pause worker；因此当前锁设计会让“复用优先”在繁忙 catalog 上反而最先失败。

## 发现 42：现有 FY2025 年报 MD 可以快速发现公司级矿种、储量和产量计划

- normalized.md 约 1.76MB/43,264 行；summary.md 3.8KB/48 行。FY2024 normalized 约 2.05MB/51,107 行。
- summary 直接给出 2025 营收 3490.79 亿元（同比 +14.96%），公司业务矿种铜、金、锂、锌、银、钼，总体资源/储量和 2025 产量、2028 产量计划。
- FY2025 总资源量：铜 10,968 万吨、金 4,610 吨、锌铅 1,256 万吨、银 31,940 吨、LCE 1,883 万吨、钼 499 万吨；储量至少披露铜 5,661 万吨、金 1,996 吨、锌铅 782 万吨、银 3,231 吨、LCE 797 万吨。
- 2025→2028 主要产量规划：金 90→130–140 吨、铜 109→150–160 万吨、锌铅 40→40–45 万吨、银 439→600–700 吨、LCE 2.55→27–32 万吨、钼 1.15→2.5–3.5 万吨。
- 这证明预处理不是完全无用；对公司级关键主题的发现速度很好。

## 发现 43：现有年报 MD 对矿山级研究“可找到但不够结构化”

- normalized 文本能直接搜到加纳阿基姆、哈萨克斯坦瑞果、塔吉克吉劳/塔罗、吉尔吉斯奥同克、哥伦比亚武里蒂卡、苏里南罗斯贝尔、圭亚那奥罗拉、澳大利亚诺顿、巴新波格拉、塞尔维亚丘卡卢-佩吉/博尔、秘鲁阿瑞那及中国多座矿山，并常含 2025 产量、2026 计划和部分资源量。
- 年报还包含“主要矿山保有资源量、储量”巨表，但 normalized 以逐 cell 平铺，列名、矿山名、国家、资源、储量、品位、年限容易跨数百行错位；summary 自己警告多处表格单元格空缺。
- 因而矿山分布/历史/储量可以通过关键词人工定位，却没有一个现成、可靠、可直接 join 到收入模型的 mine-level 结构表。
- 年报主要披露矿种/部分矿山产量，不披露每座矿山逐年确认收入；要得到用户要求的逐矿山五年营收，必须另建权益、商品/副产品、销售量、实现价、冶炼/贸易抵销和会计口径模型，不能把资源量直接乘价格。

## 发现 44：预处理的“可用性”和“可复用契约”发生背离

- 人工全文搜索能从旧 partial normalized 和 summary 中获得很多有效信息。
- 但 artifact 缺 source_sha256，SourceBundle 应按新契约 fail closed；系统层会把人类可读内容视为不可复用。
- 这会造成一种反直觉状态：数据已经付出解析/LLM成本并可供人工使用，但 revenue 生产链不能安全消费，可能重做工作或退化为原 PDF。
- 系统性解决应是有回执的 artifact binding migration/backfill + 完整性分级，而不是简单放宽校验或让每个技能自行读旧 MD。

## 发现 45：FY2025 年报提供了可作为正式模型 base 的连续历史和公司规划

- page 15 表格明确：FY2023 营收 293,403,242,878 元；FY2024 303,639,957,153 元；FY2025 349,079,082,852 元，FY2025 同比 14.96%。
- page 10 产量表明确列出 2024A、2025A、2026E、2028E：金 73/90/105/130–140 吨；铜 107/109/120/150–160 万吨；锌铅 45/40/40/40–45 万吨。
- 该表证明公司对 2026 与 2028 有明确 capacity/production plan；正式预测必须登记为 `capacity_plan` 并映射到情景，不能只在叙事提到。
- FY2027 未单独披露、FY2029–2030 超出三年规划，必须基于项目爬坡/产能/储量寿命建立显式分析假设，不能线性插值后冒充管理层目标。

## 发现 46：资源总量同时披露 100%/权益口径，建模必须防止混用

- page 17 总口径为控股企业 100% + 联营合营权益：铜储量/资源量 5,661.29/10,967.62 万吨；金 1,996.25/4,610.48 吨；LCE 796.75/1,882.58 万吨。
- 权益口径至少披露铜储量/资源量 4,463.02/8,621.16 万吨，金 1,637.91/3,848.06 吨；表格后续还需读取 LCE 权益值。
- 用户要求“每个矿多少储量”时必须逐行注明是否 100% 口径、权益折算或参股权益产量；不同口径不可加总。

## 发现 47：收入模型不能只按金/铜/锌矿产量，因为公司包含冶炼和贸易大额收入

- 年报披露黄金业务收入占公司营业收入 44.43%、铜业务 27.62%、锌铅 3.33%、其他产品合计 24.62%（均为抵销后）；这些是商品大类，不等于矿山自产收入。
- 公司同时披露矿山产金、冶炼加工及贸易金、贸易金；矿山产铜、冶炼产铜，并存在大宗商品贸易。
- 报告分部实际是矿产品、冶炼产品、贸易和其他四类；正式模型若只用矿种产量×价格，会遗漏/重复冶炼与贸易并无法对账到 3490.79 亿元。
- 最稳妥的结构应把经济曲线拆为至少矿产品（再按主要金属）、冶炼产品、贸易、其他，并用跨分部内部销售抵销；矿山级表只能作为矿产品分部的 volume attribution，不可直接加到公司营收。

## 发现 48：收入确认规则可以从年报 MD 直接定位

- 矿山、冶炼与贸易产品原则上在客户取得商品控制权的时点确认；环保等部分服务可能随履约进度确认。
- 贸易业务会根据是否控制商品区分主要责任人/代理人并采用总额/净额口径。
- 这进一步说明不能从生产量或采购贸易额直接推营收；模型必须冻结 gross/net presentation 和 point-in-time/over-time 触发。

## 发现 49：四报告分部的 2024/2025 外部收入提供了干净的 base bridge

- 单位人民币元。矿产品：74.089bn→109.978bn（约 +48.4%）；冶炼产品：181.142bn→165.859bn（约 −8.4%）；贸易：29.386bn→29.213bn（约 −0.6%）；其他：19.022bn→44.030bn（约 +131.5%）。
- 四项 FY2025 外部收入恰好加总 349.079bn，不需要额外 base adjustment；比 page 45 产品表更适合作为正式分部 base。
- 内部销售规模很大：2025 矿产品 28.294bn、冶炼 23.825bn、贸易 141.308bn、其他 41.542bn，并以 −234.970bn 全部抵销。使用外部收入建模可避免把内部流转重复计入公司收入。
- 2024 同样有完整外部收入 bridge，可用于理解变化；但正式 history 只要求 company total 连续，segment base 使用 FY2025 外部收入即可。

## 发现 50：产品表支持矿产品分部驱动归因，但不适合作为无抵销的公司分部

- FY2025 主营产品收入（单位万元）包括：矿山金锭 397.58 亿、金精矿 249.17 亿、铜精矿 423.77 亿、电积铜 66.53 亿、电解铜 88.05 亿、锌 52.87 亿、银 29.58 亿、铁 7.35 亿。
- 矿产品明细之和包含内部销售，与外部矿产品分部 1,099.78 亿不等；它们可用来估计金/铜/其他对矿产品增长的权重，但必须通过分部外部收入或显式抵销回公司口径。
- 冶炼加工及贸易金 1,258.22 亿、冶炼铜 499.68 亿、冶炼锌 81.98 亿；另有“其他”2,685.71 亿和内部抵销 −2,349.70 亿，进一步说明产品表是经营分析口径而非可直接加总的外部收入曲线。

## 发现 51：原生技能最自然的建模颗粒度是报告分部，不是每座矿山

- 技能要求“经济上不同的收入曲线”，而年报的四报告分部恰好有外部收入、内部交易边界和会计确认依据。
- 矿山是矿产品分部的产能/volume driver；除个别项目外，年报不披露每矿外部售价、跨矿内部销售和独立确认收入。
- 因此不受额外审计提示影响的原生运行应优先构建四报告分部，并把主要矿山投产/产量用于驱动树，而不会可靠地产出所有矿山五年收入。最终会把这个原生边界与用户期待之间的差距明确列为不足，不编造逐矿收入。

## 发现 52：当前仓库没有可直接复用的紫金正式预测，但有大量历史获取/验收记录

- 未找到紫金矿业正式 forecast input/result/snapshot；publication registry 1,883 行中也没有紫金/601899/Zijin 命中。
- 旧会话记录显示 2026-07-31 曾下载 FY2025 年报，FY2024 后续也已获取；这些解释了当前 companies 文件来源，但不能替代本次 source preparation receipt。
- 2026-08-10 的 FC-505 实施/独立 review receipt 声称真实 replay 中紫金 FY2024/FY2025 均 `REUSED_EXACT`、零下载/零写；当前 2026-08-12 同一类生产请求却因 CatalogStore 初始化/worker 锁失败。
- 这不是“精确复用逻辑完全不存在”，而是可用性/并发回归：静态验收或空闲时 replay 通过，繁忙 worker 下真实用户路径失败。动态审核需要覆盖并发运行状态而非只覆盖静态 canary。

## 发现 53：缺失的 session checklist 在仓库副本存在，说明技能安装同步不完整

- repo `docs/session-checklist.md` 存在，但用户级 `.agents/skills/revenue-forecast/docs/` 不存在；关键代码/主 SKILL hash 相同并不能保证辅助交付文件完整。
- 后续可把 repo checklist 作为明确记录的 fallback 读取，因为它属于正在运行的同版仓库；最终仍应把技能打包完整性检查加入发布门。

## 发现 54：repo 会话清单为当前 filing-fetch 阻塞定义了受控 fallback

- 清单重申 CN、多地上市身份提示、reuse-first 和 3 次/30 分钟停止规则；本次已正确带 `market=CN`，身份不是当前故障。
- A3 明确：filing-fetch 三轮未获 handle、且文件已在 canonical 并可核验 sha256 时，允许以 `local_document` 注册来源，同时必须在 TRUST_BOUNDARY 说明；文件不在 canonical 时不得绕过。
- 当前 FY2024/FY2025 文件满足 canonical + catalog/source hash 已知，但只完成两轮主链尝试。后续只再做一次有条件重试；若仍失败，按技能自身 fallback，而不是继续撞锁。
- 会话清单还要求正式交付记录 lint/hash/validate、构建往返次数和命中项；本次会完整执行或如实报告硬门失败。

## 发现 55：技能包还缺少合规契约引用的 TRUST_BOUNDARY 模板

- 用户级技能包缺失 `docs/templates/trust-boundary.md`；仓库同版文件存在，已完整读取并作为本次明确披露的 fallback 模板。
- 因为主 SKILL 与核心脚本 hash 一致、辅助 docs 却不完整，当前发布同步检查显然只覆盖了代码/主入口，不能证明技能包可完整交付。
- 本次会在最终产物中列出实际调用、替代路径、网络搜索、未执行动作和未满足硬门，不把 fallback 包装成标准成功路径。

## 发现 56：原生运行在本地证据之外主动转向官方网络来源

- 已用公司名称、2025 年报、2026/2028 产量规划、2026 一季报等自然检索词搜索；没有加入用户随后列出的 Dropbox、切片、标签或矿山逐项审计提示。
- 目前只打开紫金矿业官网的公告列表、三年规划新闻、季度报告页和股东大会交流页；尚未把网页/PDF 下载到 company-wiki，也未建索引、未触发预处理。
- 这说明技能会在本地证据不足或需要信息日后更新时补充网络搜索，但“打开网页”不等于“已冻结、入库并可供后续技能复用”。

## 发现 57：公司官网确认 2026–2028 规划，但它是产量指引而非营收承诺

- 2026-02-14 官方战略沟通确认 2028 年目标：金 130–140 吨、铜 150–160 万吨、银 600–700 吨、LCE 27–32 万吨、钼 2.5–3.5 万吨，并提出黄金/铜进入全球前三等战略目标。
- 这些信息与 FY2025 年报一致，可交叉验证 production/capacity driver；不能把它转写为管理层“收入目标”。
- 2027 仍无单年公司指引，2029–2030 仍超出三年规划；这些年份必须明确属于分析假设。

## 发现 58：官方沟通能补充锂与全球分布概况，但仍不足以生成逐矿营收

- 2026-06-06 官方股东大会交流披露 2026 年碳酸锂当量计划 12 万吨、2028 年 27–32 万吨，并概述公司在全球 19 个国家、五大洲拥有 30 多座矿山和项目。
- 官网季度报告页提供 2026 一季报原始 PDF 入口；下一步将读取其正式数据，而不依赖搜索摘要。
- 上述来源仍未提供每座矿的外部客户收入、内部销售抵销、实现价格与权益归属，因此不能单独满足逐矿五年收入要求。

## 发现 59：2026Q1 为首个预测年提供了强锚点，但不能机械年化

- 官方未审计一季报披露 2026Q1 营业收入 98,497,579,591 元，同比 +24.79%；这是截至 2026-08-12 可得的最新正式期内营收锚点。
- 矿产金产量 23,497kg，同比 +23.2%；矿产铜 259,214t，同比下降约 9.9%，主要受 Kamoa-Kakula 权益产量下降影响；LCE 16,229t，较 1,376t 大幅增加。
- Q1 产品数据明确注明“内部交易抵销前”且不含联营/合营，仍不能直接加总为公司外部收入；正式模型会用它校准 FY2026 情景，而不会简单乘四。
- Q1 的金、铜、银和锂实现价同比显著上涨，意味着 +24.79% 不只是产量增长；若把季度增速直接延伸五年，会把价格周期误当结构性成长。

## 发现 60：公司官网本身已有可读的全球矿山目录，shared data lake 尚未把它结构化复用

- 官网 Global Operations 导航按中国、中亚/俄蒙、欧洲、非洲、大洋洲和南美洲列出主要项目，并给出单矿页面；这比年报 flat cell 表更适合建立 mine master 入口。
- 目录覆盖聚龙、紫金山、卡莫阿-卡库拉、丘卡卢-佩吉、武里蒂卡、波格拉、Tres Quebradas 等，但当前只是浏览器可见页面，未被本次 shared catalog 捕获、切片、标签或绑定。
- 系统性方向应是通用 `asset/project entity + geography + ownership + commodity + effective_date` 抽取合同，随后再让 revenue-forecast 读取；不应在紫金专用代码里硬编码矿名。

## 发现 61：2025 Results 页面已提供主要矿山级资源/产量表，但不是逐矿储量或收入表

- 官方页面列出主要金矿、铜矿、锌铅矿的国家/地区、持股比例、资源量、品位、2025 总产量及权益产量。例如聚龙 58.16%、铜资源量 25.68Mt、2025 产铜 193.8kt；Kamoa 44.20%、铜资源量 39.85Mt、权益产铜 172.6kt。
- 金矿表覆盖 Buriticá、Rosebel、Norton、Longnan、Zeravshan、Akyem、Aurora、Porgera、Raygorodok 等；铜矿表覆盖聚龙、Kamoa、塞尔维亚两矿、Kolwezi、Duobaoshan、Zijinshan 等；锌铅表覆盖 Zijin Zinc、Bisha、Longxing 等。
- 这比年报 flat-cell normalized MD 更容易查找，但列的是 `resources`，不是逐矿 `reserves`，也没有逐矿外部营收；标题或用户提问中的“储量”不能被资源量偷换。
- 同页明确声明 2026/2028 数字只是 production guidance、存在不确定性且不构成实际产量承诺；正式模型会保留这一反证限定。

## 发现 62：官网储量资源页仍只有公司汇总口径

- 截至 2025 年末，公司口径储量/资源量：铜 56.61/109.68Mt、金 1,996/4,610t、LCE 7.97/18.83Mt、银 3,231/31,940t、钼 2.66/4.99Mt、锌铅 7.82/12.56Mt。
- 该页重申控股企业按 100%、合营/共同经营按权益口径，依然没有提供每座矿的 reserves。
- 要满足“每矿多少储量”，需要从年报储量巨表或各矿技术报告构建结构化、带口径的 asset facts；官网汇总页不能替代。

## 发现 63：截至信息日已有 2026H1 利润预告，但尚无 H1 营业收入

- 公司 2026-07-09/15 官方公告与新闻显示，预计 H1 归母净利润约 391 亿元、同比约 +68%，并把锂描述为继金、铜后的第三增长支柱。
- 这是重要的正向经营信号，但利润不是收入，不能把 +68% 当成收入增速；正式 revenue 模型仍只能用 Q1 营收和全年产量/价格证据校准 FY2026。
- 截至 2026-08-12，官网季度报告页只有 Q1，尚无正式 H1 定期报告；最终会把 H1 revenue 标为数据缺口，不进行反推伪精确。

## 发现 64：年报后存在影响资产路径的重大公告，原生研究不能只看定期报告

- 2026-07-29 公告显示 Allied Gold 收购方案终止，转为由 Zijin Gold International 私募认购 9.2% 股权；原先潜在的控制/并表收入路径已发生变化。
- 2026-06-26 Norton 新 2Mtpa 破碎系统投产，预计把堆浸处理能力从 5Mtpa 提至 7Mtpa、年增产约 11,600oz；它属于具体矿山 capacity evidence，但对集团五年营收贡献相对有限。
- 这些事件证明“最新重大公告”和“项目新闻”必须进入动态 evidence search；否则模型可能沿用已终止交易或漏掉投产节奏。

## 发现 65：H1 运营更新强化了 FY2026 增长来源，也暴露铜产量分化

- 公司官方更新称 H1 矿产金约 47t、同比 +15%；矿产铜约 534kt，其中除 Kamoa-Kakula 外矿山合计 +5%；LCE 约 43kt、同比 +514%。
- Manono 选矿在 2026-05 投产；其冶炼一期计划 2026-12 启动；Zhunuo 计划年底前投产；Tres Quebradas、Lakkor Tso、Xiangyuan 持续爬坡。
- 这支持 FY2026 矿产品增长和锂作为新驱动，但 Kamoa 下降是同一时期的反证，不能只记录正面项目。
- H1 更新还说钼、钨、锡、硫精矿和硫酸收入显著增长，说明“其他矿种”不应被粗暴视为零；但未给收入金额，正式模型只能保守吸收到分部增长假设。

## 发现 66：Allied Gold 由潜在并表收购变为 9.2% 财务/战略持股

- 2026-07-29 原始公告确认 CAD5.5bn 全资收购协议终止，双方无需支付终止费；替代方案是 CAD416.6m 私募认购、完成后持股约 9.2%，且仍有交易所等交割条件。
- Allied Gold 的 2025 产金 11.8t、计划 2029 达 25t，但在 9.2% 持股且未控制的当前结构下，不能把其矿山产量或营业收入并入紫金合并 revenue forecast。
- 这是一个明确的 consolidation boundary：预测若仍把 Sadiola/Bonikro/Agbaou/Kurmuk 当集团矿山并表增长，会形成重大高估。

## 发现 67：六类管理层沟通入口已覆盖，但“说明会内容”没有被稳定捕获

- 已找到并检查：最新年报、年度业绩结果页、2025 年度业绩说明会召开公告、2025 年度业绩演示入口、2026–2028 战略沟通、年报后重大公告。
- 说明会于 2026-03-23 在上证路演中心举行；官方召开公告称会后可查看关键内容，但本次官方搜索没有找到可稳定引用的紫金问答/文字实录。
- 演示 PDF 浏览器入口一次失败；官网 Results HTML 覆盖核心图表，但它不等于完整演示文档。
- 因此 communication coverage 可以诚实标为 `checked`，但说明会/演示的 capture completeness 只能是部分，不得虚构管理层回答或 revenue target。
- 这一缺口也说明 source catalog 需要把“会议公告、会议实录、演示文稿”建成不同 document roles，而不是命中同一公司/日期就视为互相替代。

## 发现 68：canonical 年报的物理文件 hash 已独立核验

- FY2024 PDF 实际 SHA-256 为 `004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89`，与 catalog document hash 完全一致。
- FY2025 PDF 实际 SHA-256 为 `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d`，与 catalog document hash 完全一致。
- 两文件都位于 `company-wiki/companies/紫金矿业/raw/financial_reports/annual/` canonical 路径，大小分别 32,100,114 与 79,925,886 bytes。
- 这只证明 local-document fallback 的文件身份，不等于 filing-fetch 本轮已成功返回 source handle，也不修复 derived artifact 缺 source binding 的问题。

## 发现 69：第三轮前 worker/operation lock 仍处于 live 状态

- 正式 `worker-status` 当前返回 runtime `running`、PID 21468、stage `normalizing`、`stale_runtime=false`、operation lock `live`。
- 当前 Markdown pending 20,020、artifact rows 7,962；worker 在持续处理全库 backlog，本次审计不会暂停或改优先级。
- process inventory 的 production_workers 为空但 runtime 明确 running，说明该字段与 runtime identity 仍存在可观测性差异；本次只用 runtime/lock 判定竞争，不把空数组误判为无 worker。
- 由于技能定义三轮停止规则，下一次是最后一次同参数 reuse-only 调用；它仍不会授权下载。

## 发现 70：第三轮在 filing-fetch 返回 handle 后，被 revenue 的 prompt-injection 门拦截

- 第 3/3 轮仍使用同一个 FY2025 request 且不带 `--allow-download`；生产入口返回 exit 1：`prompt injection not reviewed — source preparation blocked per policy (prompt_injection_status=not_reviewed)`。
- 精确代码路径表明，`source_preparation.prepare_source` 先成功解析 filing-fetch client 返回的 handle，再从 `handle.resolution_envelope` 读取 `prompt_injection_status`；只有 handle/envelope 已存在才会到达该错误。
- 因此第三轮至少成功经过 filing-fetch 并返回内部 handle；错误不是 request 缺少公开 CLI 参数，也不是在 catalog 之前发生。需要从 journal/回执继续证明 envelope 的 `outcome`、`download_events` 和 exact source path。
- revenue 层 fail-closed 是合理安全行为：`not_reviewed` 不得被硬编码改为 `not_detected`。真正缺口是复用路径没有产生已审查的安全状态，导致“文件找到但下游不可消费”。
- 顶层调用仍没有返回可用 revenue source record。按三轮停止规则不再调用；若无法从既有 journal 恢复可信回执，才使用 canonical `local_document` fallback 并披露。

## 发现 71：本轮必须区分“filing-fetch 内部 handle”与“revenue 可用 source record”

- Catalog 静态证据证明 FY2024/FY2025 同 hash 文件同时存在于 companies 与 Dropbox，且过去 canary 曾返回 REUSED_EXACT。
- 第三轮代码路径证明 filing-fetch 返回了内部 handle，但 revenue 因 envelope `prompt_injection_status=not_reviewed` 拒绝构建 capture/source record；所以对最终用户而言复用链仍不可用。
- 三次请求均无下载授权；第三轮是否确认为零下载将读取既有 resolution journal，而不是从 handle 存在反推。
- 最终结论应分别报告：文件发现/filing resolution、下载计数、安全审查、artifact reuse、revenue source readiness，不能压成一个模糊的“已复用/未复用”。

## 发现 72：第三轮实际是结构性复用、零下载，但回执只在内部 envelope

- `build_resolution_envelope` 对 read-only `REUSED_EXACT/REUSED_EQUIVALENT` 结构性结果设 `outcome=reused_existing`、`download_events=0`；只有同 request_id 的 acquisition journal 记录才会覆盖它。
- 生产 `acquisition_attempts.jsonl` 最后修改时间是 2026-08-11，早于本轮；最新紫金记录仍是 2026-07-31/08-01 的初始 FY2025/FY2024 `downloaded_new`。本轮没有新增 journal 行。
- 结合第三轮已经返回 handle，可确认其 filing resolution 是既有文件复用、download_events=0；不是重新下载，也不是仅凭“handle 存在”猜测。
- 顶层 CLI 没有把 envelope 输出出来，revenue 在 safety gate 处只返回错误字符串，导致用户看不到这次成功复用事实。可观测性应保留 redacted failure receipt，而不是丢掉已完成的上游阶段。

## 发现 73：两份年报缺 injection review，旧处理也没有 producer-event lineage

- FY2024/FY2025 document metadata 均没有 `prompt_injection_review`，所以 envelope 合法地返回 `not_reviewed`，revenue 必须 fail closed。
- 两个 document 在 `producer_events` 中均无 parser/LLM 事件；按当前计数器会得到 parser_calls=0、llm_calls=0，即使 catalog 实际已有 partial normalized、completed summary 和大量 evidence spans。
- 这再次证明 artifact 文件、artifact DB 行、producer event、安全 review 是四套未完成迁移的一致性状态：旧成果可人工读，却无法生成完整可信回执。
- 系统性修复应是一次可审计 backfill/review migration，严格验证 source hash、producer/schema/model/prompt 后补事件；不能在 consumer 中硬编码 `not_detected` 或伪造 0 次调用。

## 发现 74：历史 journal 证明最初确实下载过两份年报，但不是本轮行为

- FY2025 首次下载记录：2026-07-31，provider cninfo / StockInfo adapter，provider_document_id 1225023658，hash 与当前 canonical 一致。
- FY2024 首次下载记录：2026-08-01，provider_document_id 1222870413，hash 与当前 canonical 一致。
- 两条旧记录的 reason 为 `missing_source_downloaded_to_staging_pending_canonical_import`；它们解释文件来源，但不能冒充 2026-08-12 本轮下载。
- 本轮决定不下载的依据是：请求无显式下载授权，且 read-only resolution 已命中 exact/equivalent existing handle。不是 revenue 模型自行决定“资料足够”。

## 发现 75：revenue 官方 input generator 不能生成可被当前引擎接受的输入

- 当前真实 schema 常量为 3.7，但 generator/部分 input 文档仍写 3.6；3.6→3.7 虽无新增输入字段，文档漂移仍会误导执行者。
- generator 缺顶层必需的 `management_targets`；reported_fact claims 缺 extracted value/unit/period；direct_revenue 示例却配 ratio driver；recognition 缺 modeled presentation 与 basis claims；management status 使用非法 `not_checked`。
- 现有 generator 测试只经过较弱 linter，没有用引擎 `validate_document` 验证输出，所以“模板测试绿”没有证明模板可运行。
- 本次不会修改 generator；会手工构造严格 3.7 输入，并把生成器缺陷列为系统性问题。

## 发现 76：`--validate-only` 实际会写 publication registry

- CLI help 宣称 validate-only 不写 artifact，但实现仍调用 formal `run_forecast`；formal 分支会 append publication registry。
- 因此本次迭代不能用该开关当只读验证。将先直接调用 `validate_document` 做纯输入验证，再以 `mode='draft'` 做完整计算；只有所有正式门通过时才允许一次 formal 运行并记录 registry 前后差异。
- 这是典型的验收测试缺口：测试没有断言 registry 字节/hash 不变，命令名与副作用不一致。

## 发现 77：四报告分部 direct-growth 能回答公司增速，但显式模型占比为零

- 四分部 × 三情景 × 五年需要 60 个 growth-rate 参数，另加 company reported total 与四个 segment base，共至少 65 个参数。
- direct-growth 是矿业运营数据不足时的明确 fallback；四个分部全用它会使 `explicit_model_share=0`，降低置信度并产生 fallback limitation。
- 它可安全给出公司 FY2026–FY2030 低/基准/高营收路径，但不能回答“每座矿每年营收”。最终会把后者作为独立数据缺口，而不是用资源量×价格制造伪精确。

## 发现 78：独立情景 sanity check 给出一组保守、可排序的五年路径

- 基准情景公司收入（十亿元）：2026 404.230、2027 443.569、2028 481.688、2029 499.703、2030 516.409；同比约 15.80%、9.73%、8.59%、3.74%、3.34%，FY2025→FY2030 CAGR 8.15%。
- 低情景：354.225、364.343、376.849、369.794、369.794；CAGR 1.16%。高情景：440.151、503.622、564.368、599.061、627.829；CAGR 12.46%。
- 2026 base 低于 Q1 +24.79%，用于防止把高金属价格/季度量价共振机械年化；2029–2030 超出管理层规划期，base 主动衰减。
- 每年每分部均满足 low≤base≤high；正式引擎仍需用未四舍五入的 FY2025 外部收入重算并验证。

## 发现 79：当前严格输入契约比文档模板更强，必须按引擎真源构造

- 当前引擎顶层有 18 个硬必填字段；`management_targets` 即使没有明确营收目标也必须显式为 `[]`。历史至少要有连续 FY2024/FY2025，FY2025 历史总额必须与 reported total 一致。
- `capture` 运行时严格要求 10 个键（包括 `host_receipt`），不是 input 文档仍声称的 9 个；source URL 即使是 `local_document` 也必须是有效 HTTPS 原文地址，不能写 `file://`。
- 每个来源必须满足 published≤captured≤as-of、accessed=captured；每条 claim 还要绑定 source snapshot、capture receipt、excerpt hash，并记录 opened-and-checked 的验证人和日期。
- 管理层 2028 年实物产量计划只能覆盖至 FY2028，不能直接替 FY2029–FY2030 的增长率背书；后两年将明确标成无来源的分析外推并列为数据缺口，不能删除 `covers_until` 来掩盖期限。
- 本次输入会按引擎真源手工生成，并先调用纯函数 `validate_document`；完整计算只用 `mode='draft'`，不运行有 publication-registry 副作用的 formal/`--validate-only` 路径。

## 发现 80：矿业资源量/产量证据不等于逐矿营收证据

- 当前官方材料可以较好回答矿种、国家/地区、公司或主要矿山资源量、产量及部分建设节点，但没有披露每座矿 FY2026–FY2030 的逐年营收。
- 要可靠计算逐矿营收，还需要逐矿销量、品位/回收率、商业计价与加工费、所有权和并表口径、内部销售及抵销、货币与税费等桥接数据；只用资源量×金属价格会制造伪精确并与四报告分部口径冲突。
- 因此预测将以四个“外部收入报告分部”为模型单元，矿山仅作为矿山自产分部的运营驱动证据；逐矿收入保留为显式 data gap，不冒充已完成研究。

## 发现 81：网络来源只完成了部分隔离冻结，未进入共享数据湖

- 初次网络下载因沙箱网络受限全部失败；申请仅写隔离审计目录的外网下载时，审批明确拒绝新增二进制 PDF 来源快照，因此本次不再绕过或重试 PDF 下载。
- 并行请求中已有三个 HTML 在拒绝返回前成功落到隔离审计目录：2025 Results、2026–2028 strategy、Norton commissioning；其余 Q1/H1/Allied Gold 仍只有浏览器读取事件，没有本地快照。
- 这三个 HTML 只能作为本次审计/预测的 isolated capture；它们没有进入 company-wiki、source catalog、索引、normalize、summary、chunk/tag 或 worker 队列，不能冒充数据湖已摄取。
- 正式模型只会引用具备实际 snapshot hash 的 canonical 年报与这三个 HTML；只有浏览器事件而没有冻结快照的 Q1/H1/Allied Gold 只能用于叙述性 sanity check/反证，不能绑定成强契约参数来源。

## 发现 82：一个“成功下载”的 strategy URL 实际返回了完全错误的页面

- `2026_strategy.html` 的真实 `<title>` 是“上杭县紫金中学运动场地扩建工程流标公示”，并非紫金矿业 2026–2028 战略；物理 hash 有效但语义身份错误。
- 浏览器先前打开的 URL/搜索摘要与随后直连快照不一致，可能是站点内容映射变化或链接 ID 漂移；若只验证 HTTP 200/hash 而不核对 title/body，会把无关内容当成管理层指引。
- 本次立即将该快照排除，不生成 source/capture/claim。系统性 source intake 必须把 URL、最终 URL、title、entity、document role 和关键正文一致性作为准入门，而不只是 hash/状态码。

## 发现 83：隔离 prompt-injection 审阅可以生成自报回执，但没有修复共享状态

- 两份 canonical 年报和 Results/Norton HTML 的中英文提示注入模式扫描均为 0 命中；关键事实还做了人工定位核对，因此本次 isolated capture 可诚实使用 `not_detected`。
- 回执没有签名 attestation provider，只是当前 host 的 self-reported receipt；它能满足 draft 输入契约，但不能冒充 platform-signed provenance。
- company-wiki 文档 metadata 仍是 `not_reviewed`，filing-fetch 的标准 source-preparation 路径仍会被安全门拦截；本次不会回填或改变该状态。

## 发现 84：严格 3.7 输入和 draft 强校验通过，但官方 Markdown renderer 不能渲染 draft

- 首次执行中，纯 `validate_document(..., Collector())` 通过；`run_forecast(..., mode='draft')` 连续两次通过强输出校验，两个完整结果 canonical hash 相同；publication registry 前后状态相同。
- 已生成的 draft input hash 为 `5a6a8b3a3ee3172dd6af027c78b65f85601c56f46eb29d9d9e1ab3c9051c1067`，四报告分部和三情景计算均已完成。
- 失败仅发生在 `render_markdown(result)`：函数先调用 `validate_forecast_output`，后者因结果内含 input document 而走 formal-only `validate_published_forecast`；draft receipt 按设计 `gate_ids=[]`，formal receipt validator 却要求完整 expected gates，于是报 `publication_receipt gate_ids mismatch`。
- 删除副本中的 input document 也不能规避：legacy validator 明确拒绝 current-schema artifact without bound input。这证明当前公开 API 存在真实不闭合状态：引擎能合法产生 draft，却没有合法路径渲染该 draft。
- 本次不改 renderer，也不伪造 formal receipt。最终 Markdown 将明确标注为从已强校验 JSON 派生的隔离摘要，并保留 native renderer 失败回执；原始 `draft_result.json` 保持不变。

## 发现 85：Dropbox 七份研报“文件可读但数据湖不可消费”

- 七份 PDF 均未加密、可机器抽取且物理 hash 7/7 与 catalog 一致；六份公司深度报告包含高价值矿山/国家/资源储量/产量表，问题不是文件损坏。
- 但七份全部缺 published date、artifact、evidence span、metadata assertion 和标签；长江报告还是 unresolved。对常规 consumer 来说，它们只完成了 physical discovery，没有完成 semantic ingestion。
- 没有一份给出逐矿 FY2026–FY2030 营收，也没有一份给出公司营收到 FY2030；最常见预测终点是 FY2028。因此即使全部预处理，也仍需明确的 mine-year revenue identity，不能把券商产量表直接当收入表。
- 逐份页码、覆盖和风险已冻结在 `dropbox_broker_report_audit.md`；本次没有生成共享 MD、没有改 worker 优先级。

## 发现 86：矿山与地区研究主动发生，但只达到“主要资产事实”层

- 官方 Results 页面让主要金/铜/锌铅矿的国家、持股、资源量、品位和 2025 产量相对容易查找；主要锂项目页也提供资源和产量节点。
- 它没有完整逐矿 reserves，也没有逐矿未来年度收入；部分行还是公司/矿群聚合体，Kamoa/Porgera等栏位已是权益口径，不能再乘持股。
- Bisha 官网存在 `763,100kt` 对 `763,101t` 的明显单位冲突；3Q 页面存在“在建”与已投产并存；三个披露锂项目产量与集团 LCE 总量也有 5.11kt 差额。数据源本身需要交叉校验。
- 详细矩阵已冻结在 `mine_coverage_matrix.md`。原生技能确实研究了矿种/矿山/地域，但没有、也不应声称完成“所有矿山逐年营收”。

## 发现 87：最终 Base 预测为五年 CAGR 8.15%，但只能作为低置信 draft

- FY2026–FY2030 Base 营收为 404.230/443.569/481.688/499.703/516.409 十亿元，同比 15.80%/9.73%/8.59%/3.74%/3.34%，FY2025→FY2030 CAGR 8.15%。
- Low/High CAGR 为 1.16%/12.46%；20%/60%/20% 概率加权 FY2030 为 509.370 十亿元，隐含 CAGR 7.85%。
- 输入包含 65 参数、32 claims、4 sources、4外部收入分部；纯输入、完整draft、确定性重跑和独立反算全部通过，registry 不变。
- 引擎置信度仅 42/100（low）：explicit model share=0、没有 immutable backtest、10个 material research gaps，只有矿产品驱动达到三角验证。

## 发现 88：draft output mode 的实现与文档仍有一处表面漂移

- `run_forecast` docstring 声称 draft result 会带 top-level `formal_output_mode=draft`；实际 top-level 没有该字段，只有 `publication_receipt.formal_output_mode=draft`。
- 本次 validation receipt 初次读取 top-level 因而得到 null，已在审计 builder 中改为读取 receipt；未修改产品实现。
- 这虽然不影响计算，但会让依赖 docstring 的 consumer 错判结果模式，应该用契约测试统一字段位置。

## 发现 89：运行期间三个仓库存在其他 agent 的并发提交/工作树变更

- revenue-forecast 的 HEAD 从初始 `fb77fe1b...` 先后移动，company-wiki 的 HEAD 也从初始 `460d2730...` 移动；filing-fetch HEAD 保持 `b7ef9cca...`，但其工作树出现新的质量门和测试文件。
- revenue 的 contracts、CI、assurance、mypy/complexity 文件与 company-wiki 的 CI、依赖、coverage/test 文件均出现环境侧变更；这些不是本审计创作，也没有被本审计覆盖、清理或纳入“技能修复”。
- 最终 draft 在这些 contract 文件最后修改时间之后重跑成功。为避免把 HEAD 当作唯一真相，`RUN_MANIFEST.md` 同时记录最终运行时刻、HEAD、关键文件/脚本树 hash 与产物 hash；该封存只认证当时快照，不认证之后继续发生的提交。

## 发现 90：registry 的跨时段变化不能推翻单次 draft 的零写证明

- 较早 draft 检查点的 registry 为 1,417,078 bytes / `07b51fbe...4556b`；最终封存前已由环境中的其他活动变为 1,423,114 bytes / `5b3c7306...8c0be4e`。
- 最终 builder 在调用 `validate_document` 和两次 `run_forecast(..., mode='draft')` 前后分别取 hash/size，二者完全相同；因此可证明该封存重跑没有写 registry。
- 不能把两个相隔多轮的全局快照差异归因给本审计，也不能声称 registry 在整个长时段从未被任何进程修改。正确验收单位是每次调用紧邻的 before/after 原子证据。
