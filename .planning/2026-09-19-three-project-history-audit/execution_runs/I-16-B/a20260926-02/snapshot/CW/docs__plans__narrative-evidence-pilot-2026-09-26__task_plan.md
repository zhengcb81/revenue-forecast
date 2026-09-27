# 叙述性证据选择与摘要：小范围试点及实施方案

> 独立实施计划；不替代仓库根目录或任何已有专项计划。Phase 17 的旧库退役已完成；Phase 18 的离线 G1 选择、定位和草稿验证已完成一轮。当前仅在隔离模块、试点脚本、测试和本计划目录继续；不写生产 catalog、不启动 Worker、不改 revenue-forecast 或其他项目。

## Goal

用 10 份不同类型的 PDF 与 2 份英文 TXT 验证业务叙述选择、证据定位和摘要边界，形成 company-wiki 与 filing-fetch、StockWiki、revenue-forecast、invest-quick-scan 兼容的可实施方案。

## Next Step

Phase 17 的 F0–F5 已完成。G1 离线主样本和回归集已经复跑：12 件样本 1,289/1,289 locator 回读成功、18/18 锚点命中、13 条人工草稿通过引用/角色校验并完成实施者逐条核源；所有草稿仍是 `needs_review`，两份 IR 仍有不稳定表格定位。JSON 输入字节已实测，**不是数据库增量**。G1 的共享来源接入、真实持久存储差量和独立审查须等 G0。Revenue-forecast 最新可见节点为 progress Round 120、register §161：I-05-C 盘上 `accepted_scoped` 但仍携带 producer、`consumer_analysis` owner 和事件 schema 开放项；I-06-A 的最新 `accepted_scoped` 仅覆盖 store-side lifecycle，消费 CLI、跨进程等开放项仍在，生产晋升另需 owner commit。不得改共享接口、store、producer、service、DAG 或 Worker。

## Current Phase

Phase 18：隔离 G1 离线试点（本轮子项完成）；G0 跨项目合同冻结未通过；G1 共享集成、G2–G4 待门禁

## Phases

### Phase 1：样本与基线
- [x] 覆盖年报、半年报、季报、招股书、两类再融资、投资者关系、英文电话会议及低价值格式文档。
- [x] 对每份样本记录文件身份、尺寸、页数或行数、来源及已有规范化状态。
- **Status:** complete

### Phase 2：小范围只读试点
- [x] 抽取每类文档的业务片段与低价值片段，保留页码、段落、行号或字符区间。
- [x] 检查现有解析、章节、摘要的命中、误收、漏收和来源质量。
- [x] 记录候选选择/摘要策略和不可自动判断的情况。
- **Status:** complete

### Phase 3：实施方案与跨项目契约
- [x] 明确阶段化流水线、数据契约、Worker 调度和存储方案。
- [x] 明确 filing-fetch 接入英文 TXT 电话会议以及跨仓边界。
- [x] 给出验收指标、试点门槛、实施顺序、回滚与依赖。
- **Status:** complete

### Phase 4：复核与交付
- [x] 复核样本证据和方案的可执行性，标注未验证事项。
- [x] 核对 Git 状态，确认只新增本目录文件。
- **Status:** complete

### Phase 5：实施细化与审查设计（用户 2026-09-26 追加）
- [x] 将 W0–W7 展开为带输入、输出、允许修改范围、先后依赖、停机条件的实施卡。
- [x] 为 12 份真实样本、对抗样本、跨仓消费和空间迁移建立可复现测试矩阵。
- [x] 明确独立审查、证据收集、问题修复与放行规则；消除会让实施者自由猜测的设计歧义。
- [x] 校验新增规划文档及 Git 状态，保持既有计划和产品文件不变。
- **Status:** complete

### Phase 6：Worker 并发与丢任务恢复设计（用户追加）
- [x] 核对现行 Worker、catalog 操作锁、SQLite 事务、内存需求队列、调用审计和 LLMClient 状态。
- [x] 补充先可靠再并发的架构、租约代际、幂等提交、故障对账、暂停和多 agent 使用边界。
- [x] 将 W6 的实施卡、测试矩阵和独立审查同步到新设计。
- [x] 验证规划文件链接、代码围栏与 Git 隔离。
- **Status:** complete

### Phase 7：可实际实施的多文档并发方案（用户追加）
- [x] 查 Worker v5/R4 C/D 现行归属与 `automation` 持久 job/attempt/effect/outbox 真实实现。
- [x] 将早期“新增 catalog 任务表”的错误方向改为复用 R4 C05 唯一入口；写明现行 AUTO 的原子性缺口。
- [x] 给出进程拓扑、job DAG/key、claim/finish 事务、两库/文件 saga、暂停线性化、故障注入、基准和灰度/回退卡。
- [x] 用隔离 basetemp 运行现有 automation 单测并记录真实基线；同步计划入口、执行卡和测试/审查。
- [x] 全面核验链接、矛盾表述、Git 隔离及最终状态。
- **Status:** complete

## Phase 8：第二轮设计审查（2026-09-26）

- [x] 复查新 DAG 与旧 `normalize_catalog` 的调用和空间目标，移除会隐式生成全量 normalized/spans 的前置。
- [x] 按现有 `JobStatus` 状态机审查两库 saga；明确上游 visible 后才升下游 READY，来源退休时按合法状态封存运行 attempt。
- [x] 补 Windows reparse/跨卷文件暂存边界及 F17–F20 故障注入，更新验收与审查入口。
- [x] 核对本独立计划内的引用、链接、围栏和 Git 修改范围；不启动 Worker，不改产品代码。
- **Status:** complete

## Phase 9：反例审查与小样本验证（用户追加）

- [x] 在已有 PDF 中只读测量正文/表格双视图、业务表、IR 问答和文本锚稳定性；用内存 SQLite 检验中文全文检索的短词反例。
- [x] 以只读 SQLite 随机抽取 1000 条旧 span、读取库页面与磁盘余量，明确样本局限；退休来源语义仍列为 W0 未验证项。
- [x] 将发现转化为 W0/W2/W3/W5/W7 的门禁和测试；保持跨仓与 Worker 状态不变。
- [x] 复核独立计划目录、链接与 Git 修改范围。
- **Status:** complete

## Phase 10：46 GiB 降容升级设计（用户追加）

- [x] 核查主库文件、freelist、样本 JSON 压缩、现有归档/自动 prune 门禁及本机空间容量。
- [x] 将“新来源止增”与“旧库文件实质缩小”分开，写出 S0–S5 迁移和回滚门槛。
- [x] 明确当前不能给出确定节省 GB 数或用 1000 行样本外推全库；提出隔离小批量测法与净总字节验收。
- [x] 核对只改独立计划目录，Worker 与生产库未动。
- **Status:** complete

## Phase 11：重复字段与空单元降容复核（用户追加）

- [x] 用第二个固定随机样本检查 `span_json` 是否重复序列化已有关系列，并把重复比例严格限定为样本观察值。
- [x] 将字段单次存储、正文单份保存、空表格单元不建 span、兼容读取适配器和全量精确 S0 账本纳入降容设计。
- [x] 复核有业务价值的表格/IR 内容必须保留，防止为了节省空间误删证据。
- [x] 核对规划文档和 Git 范围；不改代码、数据库、Worker 或其他项目计划。
- **Status:** complete

## Phase 12：旧库清空与干净重建可行性审查（用户追加）

- [x] 只读核对 catalog 输出目录、原始输入 root、独立 source_manifests 目录，以及混存在 `.source_catalog/` 的控制/审计文件。
- [x] 比较“直接删除后旧流程重跑”与“新 schema 影子重建后替换”，明确来源历史、消费者引用、Worker paused 状态和容量风险。
- [x] 为来源哈希核验、新格式门禁、影子重建、双读、切换、延后清理写出逐步审查条件。
- [x] 保持 planning-only；不删除文件、不运行扫描/Worker、不改配置或其他项目计划。
- **Status:** complete

## Phase 13：旧主库提前退役实测与快路径（用户追加）

- [x] 只读精确统计全部非 span 表、源/文档/位置/产物与 active 旧 span；核对 ADR-009 退休归档、H01 风险和 StockWiki 当前 provider 状态。
- [x] 在系统临时目录测得目录元数据 214.84 MiB、目录+全部 active span 2.849 GiB；两者外键无错误且 `quick_check=ok`，临时库已清理。
- [x] 只读测 zstd 六处样本压缩比与当前磁盘余量，明确完整压缩备份大小和恢复性仍待实际 F2 验证。
- [x] 写出 F0–F5 提前退役卡；同步实施方案、空间方案、执行卡、测试、审查、发现和入口；明确 active 查询保留、retired 查询失败关闭、完整备份、回滚和精确文件删除门槛。
- [x] 核对计划文档链接、围栏及 Git 范围；未改生产 DB、Worker、代码或其他活动计划。
- **Status:** complete

## Phase 14：新仓库与逐文档删除方案核查（用户追加）

- [x] 只读确认旧 SQLite `auto_vacuum=0`、`journal_mode=delete`，区分逐行删除与文件级实际释放空间。
- [x] 区分可逐件迁移清理的 raw 重复副本/derived 与不能逐件物理缩小的共享 SQLite、整包 gzip 归档。
- [x] 将新数据根、可选新代码仓、逐来源验证和 F0–F5 整库替换的先后关系写入退役卡。
- [x] 保持 planning-only；未创建新仓、迁移/删除任何原文或派生文件、改写旧库或启动 Worker。
- **Status:** complete

## Phase 15：不重要旧来源的原文删除设计（用户追加）

- [x] 只读核查 SourceManifest v1 的原路径/哈希校验、目录 source/location 状态与各输入 root 的边界；确认 `skipped_*` 不等于原文可删。
- [x] 将重复副本、唯一低价值来源、保留/阻断和外部只读输入分开；设计版本化处置状态、逐路径删除 intent/receipt 与崩溃恢复。
- [x] 写出 D0–D5 实施卡、误删反例、盲测/复审、旧 span 与下游引用门禁、实际同卷字节验收，并同步现有独立计划的入口、测试、审查和 Worker 手册。
- [x] 保持 planning-only；未删原文、未创建新仓、未改生产数据/代码/其他活动计划，Worker 仍暂停。
- **Status:** complete

## Phase 16：逐步骤空间增减实测与预算（用户追加）

- [x] 只读统计 `.source_catalog/`、`source_manifests/`、`companies/` 的当前文件逻辑长度、类型分布和 C 盘余量；区别总占用与可回收量。
- [x] 对未变化的完整旧 SQLite 运行不落盘 `zstd -3` 流计数，得到 5.773 GiB；以实测 2.849 GiB 活跃库计算 F1/F2/F5 净额和 F2 恢复试验峰值。
- [x] 将新包/索引、旧 derived、重复 raw、唯一低价值 raw 与归档/备份分别列为已知或待 D0/W 试点测定的变量；不能用负例小样本外推。
- [x] 写入独立逐步空间账，并同步快路径、空间方案和入口；未创建备份/影子库、新仓库或删除文件，Worker 保持暂停。
- **Status:** complete

## Phase 17：按用户授权实施旧库提前退役（完成）

- [x] 更新 F0–F5 计划：明确取消完整落盘恢复；改为源库/压缩包 SHA、`zstd -t`、全量解压流 SHA/长度相同，旧文件切回与 active/retired 查询差分仍为硬门槛。
- [x] 新增 `implementation_run_2026-09-26.md`，明确 I0–I6 输入、输出、拒绝条件、收据、风险和无落盘恢复约束；不混入 W/D 卡。
- [x] 实施只读查询的 `legacy_evidence_archived` 失败关闭与临时库合同测试；实施影子库/压缩流准备工具，临时目录测试含触发器、零 WAL/nonzero WAL 和 Worker pause。
- [x] 实施只读证据差分审计和带中断意图收据的精确文件切换/切回工具；临时 SQLite 验证审计门禁、Windows 零 WAL/SHM 移动与旧库回滚。
- [x] 完成 F0 生产只读冻结、F1 活跃影子库、F2 正式备份流式验证与 `prepared.json` 收据；完整落盘恢复演练按用户要求取消。
- [x] F3 active/retired 证据差分、catalog query/resolve 差分及当前三方入口调查通过；真实下游业务运行未执行，收据明确其边界。
- [x] F4 精确文件级切换，658 秒间隔的两次生产烟测通过；真实生产切回未做，临时 SQLite 故障夹具已验证切回工具。F5 按精确旧库文件 SHA/路径删除，准备前至清理后同卷可用空间净增 37.630 GiB。Worker 保持 paused。
- **Status:** complete

## Phase 18：按大节点推进新流水线与原文处置（进行中）

- [x] 回应用户的效率要求：以 [G0–G4 大节点审查节奏](milestone_review_cadence.md)替代 W/N/D 每张卡的独立签收和重复全量校验；保留删除、并发和跨项目合同的关键失败关闭。
- [x] 为 G1–G4 补充关键路径端到端测试、独立运行目录、run-id 清理/中断恢复和测试树基线一致性门槛；详细规则见[关键节点端到端测试计划](end_to_end_test_plan.md)。该项只完成计划设计，尚未执行 E2E，也未触及生产数据。
- [ ] G0 在 revenue-forecast I-05-C/I-06-A 与 Worker v5/R4 的最新正式合同上冻结本专题 source package、consumer mapping 和唯一 job owner。**当前保持关闭**：I-05-C 虽有盘上 `accepted_scoped`，其复审仍明确保留真实 producer 尚未实现、RF `consumer_analysis` 入口待 owner、InvocationTracker 持久事件 schema 待 reviewer 的开放项；I-06-A 的较新 `accepted_scoped` 仅验收 store-side lifecycle，RF caller/CLI、跨进程 claim、I-06-B consumption face 等仍是 carried-open，生产晋升还需 owner commit。旧的“D-W06 全部未决定”表述已更正；具体证据见[跨项目协调](cross_project_coordination_2026-09-26.md)。
- [x] G1a 完成 12 件隔离样本选择/分类、1,289 个选中证据 locator 回读与 18 个目标锚点精确映射；两份 IR 表格维持 `needs_review`，两份无业务动态的格式化文档标记跳过。6 件 PDF 为 `partial`，不当作完整覆盖。
- [x] G1b 建立 13 条人工来源摘要草稿；13/13 通过 evidence ID、source SHA、语言、角色和问答关系机械校验；另完成实施者逐条 source-support 审查，记录在 [G1 摘要来源支持审查](g1_summary_source_support_audit_v1.md)。所有草稿仍为 `needs_review`，这不是独立签字或生产验收；T01/T02 保持英文。
- [x] G1c-a 离线量测候选 evidence JSON：主样本 542,820 B / 52,196,853 B 原文（1.0399%）；四件回归集 202,661 B / 14,939,109 B（1.3566%）。逐件序列化字节与 fsynced 临时文件长度相同、均在选择上限内；这是输入包大小，不是 DB/索引实际增量或摘要成品大小。主样本和回归集各自定位/锚点零失败。
- [ ] G1c-b 共享来源扫描/目录/export 接入、生产保存差量与独立审查；只有 G0 冻结后才能做。不得由离线 JSON 字节估算永久存储量。
- [ ] G2 验证检索/export 与受影响消费者；G3 再考虑并发 Worker 灰度；G4 按冻结批次处理低价值 raw/派生文件。
- [x] D0 完成本地原文、sidecar、derived、index、artifact 与旧 span 的只读盘点及 source ID 关联；1,490,530 条 span 涉及 1,636 个 source ID，其中 1 个缺原文 location、329 个 source ID 跨 root 有位置。复用路径的历史大小冲突见 [D0 收据](d0_inventory_receipt_2026-09-27.md)。跨仓消费合同另由 G0/D1 门禁决定。
- [ ] D1 冻结 `SourceDisposition/v1`、正式 raw 保留/处置规范及查询/预览/export 行为；需处理 SourceManifest v1、旧 span 和三方消费者合同。G0 未通过前不改共享接口或 project-wide policy。
- [ ] D2 运行覆盖完整性的负例与独立复核，重点验证格式通知中的业务附件、业务表/IR 问答、OCR/附件缺口和跨公司用途；只有预注册误删门槛满足才放行。
- [ ] D3 在 D1/D2 通过后生成并冻结逐路径候选清单；D0 的 98,845,393 B SHA 别名差额仍只是基于 catalog hash 的理论候选上限，冻结前需引用/保留审查，D4 执行时对每个精确路径重新完整 SHA。
- **Status:** in progress

## Decisions Made

| 决定 | 原因 |
|---|---|
| 本计划固定在 `docs/plans/narrative-evidence-pilot-2026-09-26/` | 现有根计划和专项计划都有各自状态；避免改变其入口及活动指针 |
| 试点只读运行，对真实文档做人工标注与轻量统计 | 用户要求先验证方案，且不影响现有任务和生产队列 |
| 再融资样本使用存量 `.PDF` 原文和只读目录查询 | 初次仅搜小写 `.pdf` 漏掉了大写扩展名；其现有 catalog 分类均为 `other` |
| 实施方案另存 `implementation_plan.md` 并保持 planning-only | 完整写清未来代码落点与门禁，同时不改既有 Worker/revenue-forecast 计划 |
| 默认采用 `NarrativeEvidencePackage/v1` 附属只读包 | 冻结旧 SourceExportBundle v1，W0 核实导出身份和实际消费者；不兼容则停止 W5 裁决 |
| Worker 持久状态不依赖 `processing_demand.py` | 该模块纯内存；R4 C05 已指定唯一现有持久 job/attempt 入口。应修复/接入 `automation`，不在 catalog 再建任务队列 |
| 跳过切片与原文处置独立 | 唯一原文一旦删除便不能靠 SHA/URL 保证恢复；旧 SourceManifest v1 不能表示有意删除，须有版本化处置记录与消费合同 |
| 量化业务目标不能被相邻 PDF 片段截断 | 半年报把“超过60%的设备市场”拆成“超”与“过60%…”两个 locator；选择器将两个片段按预算成组保留，草稿引用两者，不能只凭首片摘要数字 |

## Errors Encountered

| 错误 | 次数 | 处置 |
|---|---:|---|
| Windows GBK 控制台无法输出 PDF 中的部分 Unicode 字符 | 1 | 只读脚本输出改用 `json.dumps(ensure_ascii=True)`；不改变源文件 |
| 文件枚举只匹配小写 `.pdf`，漏掉再融资 `.PDF` | 1 | 从只读 catalog 标题查询定位，再按真实扩展名纳入样本 |
| 首次大补丁末尾任务计划匹配行缺少 `- [ ]` 前缀，整次补丁未应用 | 1 | 去除多余 hunk，仅对 findings.md 定向应用，现已成功 |
| 跨仓无界 `rg --files -uu` 遍历隔离运行目录时出现访问拒绝且输出膨胀 | 1 | 改为直接读取已知独立计划路径，不重复全仓搜索 |
| 用 Bash 花括号形式指定多个文件导致 PowerShell 参数解析错误 | 1 | 改为对已知目录限定 `rg -g '*.py'` 查询 |
| 生产 Python SQLite 未编译 `dbstat`，精确表/索引空间查询失败 | 1 | 不外推 1000 行样本；W7 改为先准备经审查的离线工具或副本方法 |
| 文档补丁引用句与实际内容不符，整次补丁未应用 | 2 | 先 `rg` 定位原句，再以更小的精确补丁重试 |
| 验收表把 P09 制度 PDF 误写为 TXT | 1 | 改为 P04/P09 PDF 加 T01 TXT 的三类选择性物化对照 |
| 全库 `COUNT/SUM(locator/raw_text)` 只读扫描长时间占用资源 | 2 | 主动中止，采用明确标为样本的 1000 行估计；精确分解归 S0 离线工具/副本 |
| 切换夹具的 SQLite 建库连接未显式关闭，Windows 拒绝重命名 | 1 | 修正夹具以 `closing` 关闭连接，并保留生产切换对持续占用句柄的拒绝；夹具重新通过 |

## Scope Boundary

company-wiki 只负责来源、解析质量、证据定位、检索和来源摘要；投资判断与预测留在 StockWiki 和下游。本轮已获授权实施旧库提前退役，明确排除完整备份落盘恢复演练。W/D 各卡仍按各自质量与处置门禁推进。
