# Progress：叙述性证据试点

## Session: 2026-09-26

### Phase 1：样本与基线

- **Status:** complete
- 已阅读 planning-with-files 技能并检查现有根计划、专项计划及 Git 状态。
- `PLAN_ID`、`PWF_PLAN_ROOT` 未设置，仓库当前没有 `.planning/`；为避免改变默认计划入口，在 `docs/plans/` 新建独立三文件计划。
- 基线 Git 状态：`CLAUDE.md`、`README.md`、`src/company_wiki/source_catalog/artifact_dag.py` 已有修改，均非本试点所作。
- 已登记 10 份 PDF、2 份 TXT；PDF 页数、字节数与 SHA-256 通过 PyMuPDF 和 hashlib 只读计算。只读 SQLite URI：`mode=ro&immutable=1`。
- 再融资两份样本为大写 `.PDF`；在现有 catalog 中均被归为 `other`。

### Phase 2：小范围只读试点

- **Status:** complete
- 逐页抽读 10 PDF、2 TXT；使用 PyMuPDF 页内偏移及 TXT 行号编制 11 张来源摘要正例和 2 张跳过负例，详见 findings.md。
- 对 P03 第 3 页和 P08 第 2 页渲染并视觉核对；截图仅存 Codex 可视化临时目录，未写回项目。
- 对 P04 只读查询现有章节索引：业务与技术一个片段覆盖 83 页、302,779 字符；P05/P06 当前归类 `other`。
- 只读查看 revenue-forecast 独立活动计划的当前状态，不修改或切换其绑定。

### Phase 3：实施方案与跨项目契约

- **Status:** complete
- 新增 `implementation_plan.md`：W0–W7 工作包、文档类型策略、来源/摘要契约、filing-fetch→earnings-transcripts 路由、Worker 状态机、隔离验收与迁移回滚。
- 只读核对 company-wiki 的 Worker stage 白名单、SourceBundle artifact role 白名单、来源导出 v1 结构及 acquisition 市场路由，标明新增 role 不会自动进入消费合同。

### Phase 4：复核与交付

- **Status:** complete
- 重新读取登记表逐文件校验：12/12 样本存在且 SHA-256 前缀吻合；另对 7 处 PDF 锚点与 2 处 TXT 版式锚点重查，9/9 命中。
- 四份新 Markdown 文件 UTF-8 可读，代码围栏配对。现有 `CLAUDE.md`、`README.md`、`artifact_dag.py` 的修改统计与本轮开始时相同；只新增本目录四份文档，未触碰其他计划或生产文件。
- 未验证在线抓取、全语料质量、实际节省的时间/空间；这些已列入实施门禁，未作为本轮成果声称。

## Test Results

| 检查 | 预期 | 观察 | 状态 |
|---|---|---|---|
| 样本基线 | 每类有可定位原文 | 10 PDF + 2 TXT；再融资文件可读 | pass |
| 正负例试点 | 来源摘要可锚到原文且保留限制 | 11 正例、2 跳过负例；页和行可回查 | pass (sample only) |
| 自动质量指标 | 在本轮有全样本标注 | 未进行全篇穷尽标注，召回/精确率未证实 | not tested |
| 样本哈希 | 12 个登记文件与源字节一致 | 12/12 前缀匹配 | pass |
| 证据锚点 | 指定 PDF 页或 TXT 行可回查 | 9/9 复查命中 | pass |
| 计划隔离 | 不改任何已有专项计划/产品文件 | Git 仅新增本目录 4 文件；原有 3 文件修改统计未变 | pass |

## Error Log

| 错误 | 次数 | 处置 |
|---|---:|---|
| GBK 控制台输出特殊字符失败 | 1 | 后续脚本 JSON ASCII 转义输出 |
| 小写扩展名过滤漏掉 `.PDF` | 1 | 只读 catalog 查标题后定位文件 |
| 一次补丁 hunk 匹配失败 | 1 | 缩小目标文件与匹配范围，重新应用成功 |
| 无界跨仓文件枚举遇隔离目录访问拒绝 | 1 | 改读已知计划文件，停止遍历隔离产物 |

## Next Step

本轮交付完成；未来从 `implementation_plan.md` W0 开始，先测契约和基线。

## Session: 2026-09-26（方案细化）

### Phase 5：实施细化与审查设计

- **Status:** complete
- 用户要求进一步细化，并加入审查与测试，让较弱模型也能按步骤实施。
- 已复核本目录四份计划文件及产品现有测试入口；本次仍只修改独立计划目录。
- 新增 `execution_cards.md`：固定 D1–D6 设计选择及停机点，将 W0–W7 写成依赖、步骤、预期结果、负向验证、回退与独立审查卡。
- 新增 `test_acceptance_plan.md`：12 份真实原文的 13 张探索卡、九层至少 36 件盲测留出集、对抗夹具、测试矩阵、指标定义与 W0 冻结门槛。样本总体质量与空间收益仍未测，明确标记 `UNDECIDED`。
- 新增 `review_protocol.md`：每卡 receipt、双层审查、P0–P3 严重性、`accepted_scoped/changes_required/blocked_decision` 裁决、发布与回退门禁。
- 修正 `implementation_plan.md`：默认使用关联旧 v1 的附属只读包，W0 核对真实导出身份/消费者；指出 `processing_demand.py` 纯内存，Worker 持久断点必须另外实现和测试。
- 只读验证 7 份规划文件 UTF-8 可读、相对链接均有效、代码围栏配对；Git 中原有 `CLAUDE.md`、`README.md`、`artifact_dag.py` 修改统计仍为 8/6/4 行，未触碰；只增改本计划目录。一次 `rg` 使用 Bash 式花括号在 PowerShell 中解析失败，改为显式文件列表后成功；不影响文件。
- 未运行产品测试或 Worker，因为本轮只有计划文档变更；未来测试命令及隔离前提已写入测试计划。

## Next Step（未来实施）

先执行 W0：确认真实导出/消费合同、耐重启状态真相源、留出集及基线门槛；通过独立审查后按 W1–W7 逐卡推进。此计划的完成不解除 Worker 暂停，也不允许直接清理生产数据库。

## Session: Worker 并发与丢任务恢复补充

### Phase 6

- **Status:** complete
- 只读核查：`service.py` 对长 normalize/summarize 调用持 `CatalogOperationLock`；`store.py` 为 WAL/`BEGIN IMMEDIATE` 的单写模型；`processing_demand.py` 纯内存；`producer_attempts` 为尝试审计而非任务真相源；`scripts/llm_client.py` 有可变限流/计数状态。现行 Worker 不适合直接多开。
- 新增 `worker_parallel_recovery.md`：R0–R4 分阶段演进，先单执行者完成 durable work key/lease epoch/暂停代际/幂等提交/恢复对账，再让不同文档的解析与模型计算受控并行；复杂高价值文档才按需启用多 agent 核验。
- 将消息/ACK/心跳丢失、旧执行者返回、文件与 DB 双写崩溃、模型超时、SQLite busy/磁盘满、source retired、暂停临界点写成可执行故障矩阵；不承诺远程调用恰好一次，只要求逻辑结果唯一且可恢复。
- 更新总方案 W6、执行卡 D4/W6、测试矩阵与审查清单；保留用户暂停与其他项目计划不变。没有启动 Worker，也没有改产品代码。
- 8 份 Markdown 的 UTF-8、相对链接与代码围栏通过只读检查；Git 中既有 3 个脏文件的差异统计保持 8/6/4 行，只改本独立计划目录。吞吐收益尚未测，明确要求 1/2/4 在途任务对照实验。

## Session: 可实施多文档并发方案

### Phase 7

- **Status:** complete
- 用户指出概念方案不足以实际实施。只读检查现行 Worker v5 冻结计划、R4 C05/C07/D01–D04、`automation` 表/Store/Worker、source-catalog 长操作锁、catalog artifact 唯一约束、Windows 控制与解析进程。
- 关键纠正：R4 C05 已指定唯一现有持久 job/attempt 入口；`automation` 有 jobs/attempts/effects/outbox，但 CLI `status` 实测 `mode=off,status=not_configured,writes_performed=0`。当前 claim 是多事务，完成 attempt 的冲突被忽略，outbox 与 job 完成分开写。此前建议在 catalog 新建任务表不符合 R4；已在本计划所有执行入口改为复用/修复 AUTO。
- 新增 `worker_parallel_execution_plan.md`：N0–N6 交接、source 任务 DAG 与 job key、AutomationStore 原子 API、两个 SQLite/文件的 prepared→verified→visible saga、暂停线性化、Windows 子进程、F01–F16、P1/P2/P2M/P4 吞吐对照和运营回退。旧 `worker_parallel_recovery.md` 改为背景说明并指向新手册。
- 新增本目录 `README.md` 明确权威阅读顺序和 v5/R4 生产门禁；更新 implementation/execution/test/review 文档的 Worker 段。
- 只读运行现有 automation 三组单测：默认 pytest 临时根权限错误导致 9 passed/61 setup errors；指定经过边界验证的隔离 `--basetemp` 后 **70 passed**。这是旧单线程单元基线，不证明并发已可用。
- 未测真实吞吐、远程模型费用或 72 小时运行；均作为 N5/N6 未来门禁，不能写作已验证成果。未改生产代码/数据/其他计划，Worker 保持暂停。
- 最终机械核验：本目录 10 份 Markdown 的相对链接和代码围栏有效；主手册含完整 F01–F16、P1/P2/P2M/P4、N0–N6；全文检索未发现仍要求在 catalog 新建任务队列的执行指令。既有 `CLAUDE.md`/`README.md`/`artifact_dag.py` 修改统计仍为 8/6/4 行，保持原样。

## Session: 第二轮设计审查

### Phase 8

- **Status:** complete
- 发现并修正关键路径矛盾：并发手册曾把旧 `source.normalize` 放在新 DAG 前面；现有 `normalize_catalog` 会写整份 normalized 并重建所有旧 spans。新 DAG 改为从 immutable raw 做轻量 outline，仅可选只读复用已有效的旧 artifact；W2/W3 与测试矩阵同步增加 P04/P09 零全量增量断言。
- 发现并修正跨库竞态：AUTO job `succeeded` 先于 catalog `visible`，若只凭依赖状态会放行下游。下游保持 `PLANNED`，visible/源身份/覆盖账本核验后才升 `READY`；reconciler 补漏升，运行前/提交前再校验。来源退休按现有 JobStatus 合法迁移处理，不直接把 RUNNING 改 CANCELLED。
- 增加 Windows 路径身份、junction/symlink/reparse 检查、同卷暂存与跨卷复制重验的设计，故障矩阵扩为 F01–F20；更新主入口、实施卡、测试与审查。
- 本轮仅修订独立计划文档；未运行新 Worker、未修改产品代码或生产数据。F17–F20 与真实吞吐/空间收益仍待未来实施验证，不能写作已通过。
- 机械复核：本目录 10 份 Markdown 的相对链接/围栏均通过；主手册故障行 F01–F20 连续、无重复，DAG 无 `→ source.normalize`；进入本轮前已有三个脏文件的 diff 统计仍为 8/6/4 行，未碰其内容。

## Session: 第三轮反例审查与小样本验证

### Phase 9

- **Status:** complete
- 只读 PyMuPDF 1.26.7 小试：P08 IR 第 2 页的表格 bbox 占约 71.9% 页面，按现行快照函数的 bbox 排除规则，30 个正文块中 29 个被排除，多个问答进入 1×2 表格单元；P04 第 114 页产品/应用表也包含有用业务描述。P03 同页财务表只占约 1.4%，正文不能整页过滤。五个 PDF 页的 `sort=False/True` 字符长度均不同。由此收紧 W2 双视图、锚点覆盖、多原子锚与 W0 locator 裁决。
- 对生产 SQLite 使用 `mode=ro&immutable=1`、`PRAGMA query_only=ON`，固定 seed 20260926 在 rowid 空间抽取 1000 条旧 span：820 条 table cell、496 条 raw_text 空；平均 `span_json` 812.6 B，raw_text 16.9 B。DB 46.266 GiB，freelist 9 页。当前 Python SQLite 没有 dbstat，不能据样本报全库精确分解或空间节省率。
- 纯内存 SQLite FTS5 反例：`unicode61` 无法命中样本中的“硫化锂”“中试线”；trigram 可命中这两个三字词，但 `MATCH` 无法命中两字“出海”。现有 source_catalog 查询无显式全文 FTS；W5 增加中文短词、英文、时间过滤、按需回源与索引空间/p95 合同。
- C 盘当时空闲约 77.56 GiB，主库约 46.27 GiB；两份等大副本约 92.53 GiB，W7 增加独立存储/最坏空间硬门槛。另补 skip 文档不可读时不得假成功、原文 prompt injection 不可执行、一般公告/新闻/研报后续扩展边界。
- 最后对统计门槛再收紧：原计划每类 4 件、共 36 件只能作为盲测最低集成样本。W0 要预注册每类目标误差、文档聚类置信区间与正式样本量；证据不足为 `insufficient_evidence`，不得把小样本零失败说成可靠召回率。
- 只修改本独立计划目录；未运行产品解析写入/Worker/LLM/联网抓取，未修改生产数据、源码或其他项目计划。当前小试证明存在反例，**不证明**新选择器的质量、吞吐、索引时延或总体空间收益。

## Session: 46 GiB 降容升级方案

### Phase 10

- **Status:** complete
- 只读核对：主库 46.266 GiB、WAL 0 B；目前 sqlite3 CLI/Python 均无 `dbstat`。全库 `COUNT/SUM(locator/raw_text)` 两次扫描耗时较长，主动中止，未改 DB。现有 gzip 归档功能不等于自动 prune 已安全，仍受 Worker v5/R4 H01 门禁约束。
- 以固定 seed 的同一 1000 条 span JSON 做仅内存 zlib 小试：812,588 B 原 JSON，逐行压缩 469,528 B，合并压缩 175,172 B（21.6%）。这只表明冷归档有潜力，未含索引/其他表/查询服务，不能外推“46 GiB→10 GiB”。
- 新建 [space_reduction_upgrade.md](space_reduction_upgrade.md)：S0 精确空间账本→S1 新数据止增→S2 可信冷归档→S3 独立卷紧凑库影子重建→S4 双读切换→S5 保留/回收，逐步验证质量、查询、引用、备份与净总磁盘字节。P01/P03/P04/P08/P09/T01 定为隔离小试范围；80% 派生字节下降仅为预注册挑战目标，非已达成数值。
- 本轮只编辑独立计划目录；未执行 prune、VACUUM、归档、生产 Worker 或项目代码写入。

## Session: 重复字段与空单元降容复核

### Phase 11

- **Status:** complete
- 对只读 immutable SQLite 再抽 1200 条 span（seed 20260927）：`span_json` 均值 815.5 B；7 个通用字段与关系列重复，估算 418,218 B；结构值又复制正文约 18,324 B。可复核分项之和为 436,542 B、约占样本 JSON 44.6%，不是全库可节省比例。
- 部分 table cell 还将正文重复放在 `raw_text` 与结构化值中；空 cell 也有 JSON 元数据壳。计划新增字段单次存储、正文单份保存、空 cell 不建 span、读取适配层及精确全量 S0 账本。
- 反向检查确认不能按文档类型粗暴丢表格：招股书产品/应用表与 IR 问答可能含高价值描述；仅过滤空格和经确认可由 API 供给的标准财务数据，仍需验证召回。
- 更新 `space_reduction_upgrade.md` 和本计划阶段记录；只增改独立计划文档，未改源码、生产库、Worker 或其他计划。
- 数字复核时发现旧记录的 460,942 B / 47.1% 比已列分项多 24,400 B；无可复核依据，已在 findings 和降容方案中撤回，后续需由固定脚本复算。

## Session: 46 GiB 旧 catalog 全量重建审查

### Phase 12

- **Status:** complete
- 只读核对 `config/source_catalog.yaml` 经正式配置加载后的 4 个输入 root 均存在，catalog_dir 指向 `.source_catalog`；另有独立 `source_manifests/`。项目文档确认 raw 输入为只读，normalized/summary、SQLite 和索引写到 `.source_catalog/`。
- 核对 `.source_catalog/` 同时包含 DB、Worker desired state/control/runtime、状态/运行日志、acquisition 与 cleanup 审计、security master、staging、derived 和 export/index。全删会损失运维/历史信息并可能破坏 Worker paused 状态；旧扫描约定对消失路径保留 `missing` 状态，空库不能复原已消失的来源历史。
- 评估结论：用**新格式在隔离 catalog_dir 从只读 raw 重建，再双读/消费核对后替换旧派生库**可能更清晰；先删再旧流程重跑会重建全量 normalized/spans，不能治本。新方案、R0–R5门禁、回滚和容量风险写入 `space_reduction_upgrade.md`。
- 重新确认 C 盘此前余量约 77.56 GiB；保留旧 DB 影子重建时给新库/临时/WAL/索引约 31.3 GiB，峰值未测。未运行 scan/Worker，未删除或复制数据库，未改配置、源码、raw 或其他项目计划。

## Session: 提前退役旧主库的快路径验证

### Phase 13

- **Status:** complete
- 生产库只读元数据：49,677,344,768 B、WAL 0、17 张非 evidence_spans 表共 189,580 行；sources 43,112、documents 23,530、locations 46,606、artifacts 8,191。active 文档 13,839、retired 9,501。通过 `idx_documents_status_kind` + `idx_spans_document` 精确计数 active 旧 span 为 1,490,530（约 8.75 秒）。
- 系统临时目录两次原 DDL/数据/索引复制试验：目录表独立库 225,280,000 B（214.84 MiB）；目录+全部 active span 库 3,059,200,000 B（2.849 GiB，1,680,110 行，耗时约 143 秒）。均 `foreign_key_check` 无错误、`quick_check=ok`，临时目录自动清理；只证明大小和关系完整性，未通过实际服务/下游差分。
- 发现 `source_manifests/archive/2026-08-07/retired-evidence.jsonl.gz` 为 5,207,478,767 B、首条可解析为旧 span；ADR-009 记载 25,708,956 条退休证据归档，H01 独立复核指出校验与不可覆盖发布缺口，因此不能把它当唯一可恢复备份。`derived` 约 2.83 GB、`index` 约 45 MB，另行管理。
- zstd level 3 对 6 处各 8 MiB 旧 DB 的只读试压比例 12.2%–32.1%；完整快照大小未知。当前 C 盘空闲约 85,079,416,832 B（79.24 GiB）。StockWiki 当前 company-wiki provider disabled；revenue-forecast 使用 filing-fetch/source 目录链，真实合同仍列 F3 核对。
- 新增 `early_catalog_retirement.md`：推荐在完整可恢复压缩备份前提下，以 2.849 GiB 活跃子集替换主文件，先保住 active 旧查询；retired 查询必须明确归档不可用或冷读，不能伪报 not found。F0–F3 可独立准备，F4/F5 分别审生产切换和按确切路径清理；预计本机净节省依完整压缩文件实际大小计算。
- 同步总方案、执行卡、测试和审查门禁，未改生产 DB/源文件/Worker/配置/代码或其他活动计划。此次用户请求仍是方案讨论，没有执行旧文件删除。
- 最终 Git 状态另出现 `src/company_wiki/source_catalog/dayu_cli_adapter.py` 的未提交修改（121+/7−），本轮没有编辑该文件，也未据此改写计划外代码；此前已有 `CLAUDE.md`、根 `README.md`、`artifact_dag.py` 脏改动保持原有统计。此项属于并行工作区状态，实施 F 卡前要重新识别所有现存改动。

## Session: 新仓库与逐文档清理方案

### Phase 14

- **Status:** complete
- 只读 `PRAGMA` 确认生产 SQLite `auto_vacuum=0`、`journal_mode=delete`、freelist 9 页。逐来源删除其中的 span 行不会逐来源缩小 46.266 GiB 主文件；主文件仍需受控影子库切换与整文件退役。
- 明确可逐件核验和清理的是旧 derived（总计约 2.83 GB）及成功迁移后旧位置的 raw 重复副本；唯一 raw、source manifest、仍被消费者引用的产物不可删。5.21 GB 退休 gzip 为整包，另行审查。
- 在 `early_catalog_retirement.md` 增加可选新 Git 代码仓与优先的同项目隔离 v2 数据根，并规定逐件 raw 迁移的 hash、可读性、映射、消费者切换、回滚和精确路径清理门禁。新 Git 仓本身不会减少储存，迁移期复制原文会增加峰值占用。
- 本轮仅更新独立规划文档；未创建新仓、写生产数据、迁移或删除任何文件，Worker 保持暂停。

## Session: 不重要来源也回收旧原文

### Phase 15

- **Status:** complete
- 只读核查 `SourceManifest v1`：原路径、SHA、大小绑定，`verify_file()` 要求文件仍存在；`immutable_status` 只有 verified/quarantined，不能描述按政策处置。现有业务 `skipped_*` 只是不生成切片，不能直接触发 raw 删除。
- catalog 只读 `locations` 分组显示 `company_raw` 的 original_primary active 7,524 件、observed_size 6,511,169,498 B；retired 9,046 件、18,641,858,464 B。这些是历史观察大小，不是当前物理占用或可删除量；`retired` 不等于低价值。Dropbox/dayu 是外部只读输入，不能纳入本项目删除动作。
- 新建 `raw_disposition_plan.md`：把内容选择与原文处置分开，允许对经完整覆盖和独立复审的唯一低价值来源逐件删除原文，或先清理同 SHA 重复副本；保留轻量历史身份、版本化处置状态和精确路径删除 receipt。加入来源/旧 span/下游引用、错误缺失、崩溃重放和真实同卷字节门禁。
- 同步入口、总实施、空间、旧库退役、执行卡、测试、审查和并发 Worker 手册。D0–D3 可只读准备，D4 与 F0–F5 的共享 SQLite 整文件退役分别审查；Worker 只提出候选，不并发删文件。本轮没有改生产代码/数据、启动 Worker、创建新仓或实际删除文件。

## Session: 分步骤空间增减账

### Phase 16

- **Status:** complete
- 只读 stat 统计：`.source_catalog/` 52,700,659,299 B（49.081 GiB），`source_manifests/` 5,207,479,410 B（4.850 GiB），`companies/` 25,173,861,091 B（23.445 GiB，33,129 文件）；三处合计 83,081,999,800 B（77.376 GiB）。公司 `raw/` 中 PDF 15,129 件、25,073,770,125 B（23.352 GiB），其可删除比例未知。
- 当前未变化的 49,677,344,768 B 旧 DB 只读 `zstd -3 --stdout` 流计数为 6,198,704,362 B（5.773 GiB，约 96 秒）；输出流只被计字节，**没有**保存备份或做恢复试验。之前 2.849 GiB 活跃临时库实测可用于预算，非生产交付。
- 若正式快照相同且留 C 盘，F1 +2.849 GiB、F2 +5.773 GiB、完整恢复临时再 +46.266 GiB（峰值较现状 +54.888 GiB），F5 删除原主库 −46.266 GiB，累计净释放 37.644 GiB。当前 C 空闲 79.217 GiB，理论峰值剩余 24.329 GiB，未含 WAL/其它进程和安全缓冲。
- 新产物/检索索引大小未知；旧 derived 最多 2.632 GiB 可审查回收，唯一低价值 raw 需 D0 逐件测。两份已知负例仅 262,925 B，不能外推。现有 4.850 GiB 退休归档与完整备份暂保留。空间账写在 `stepwise_space_budget.md`，只更新独立规划文档，未执行生产迁移、清理或 Worker。

## Session: 用户取消完整恢复演练并授权实施

### Phase 17（进行中）

- 用户明确要求不进行完整落盘恢复备份演练，其他步骤可实施。已把 F2 改为正式快照 SHA、`zstd -t`、完整解压流 SHA/长度与原库相同，并明列未来实际落盘恢复未演练的剩余风险；同盘峰值预算由 54.888 GiB 降为 8.622 GiB。新建 `implementation_run_2026-09-26.md` 作为本轮 I0–I6 执行卡。
- 产品代码新增 `EvidenceQueryArchivedError`，active-only catalog 中非 active 来源缺失旧 span 时明确返回 `legacy_evidence_archived`，旧完整库行为保持；CLI error taxonomy 版本 1.1 标该错误不可重试。相关证据/错误合同测试 27 passed。
- 新增 `scripts/retire_source_catalog_db.py`：只读原库、复制全部非 span 数据/active 旧 span/索引/触发器，逐表摘要、FK/quick_check，生成 zstd 快照并流式重验；不做切换/删除。临时库测试补触发器、Worker pause、零 WAL 可接受/非零 WAL 拒绝，3 passed；合并相关测试 29 passed。
- 生产预检仍为 `worker_control.paused`、主库 49,677,344,768 B、`operation.lock` 不存在、C 空闲约 85,025,054,720 B；现有 `-wal` 文件为 0 B、`-shm` 32,768 B（最近读连接留下），工具允许零 WAL 且每阶段重验，非零 WAL 阻断。`Get-CimInstance Win32_Process` 被访问拒绝，因此不能凭进程清单证明无其他 writer；用操作锁、源 hash/stat/WAL 前后重验补强。
- 尚未运行生产影子库/正式备份、切换或删除；下一步 F0/F1/F2 准备阶段，Worker 仍暂停。
- **随后执行更新（2026-09-26 17:08–17:55 UTC）**：生产 `run_id=20260926T170825Z-4a9c67e1` 的准备进程已启动，持有 `operation.lock`；F0 的完整源库 SHA 与只读 `quick_check` 通过，约 17:40 UTC 进入 F1。候选 `catalog.active.sqlite3.partial` 已到 3,055,796,224 B，正在逐表摘要/质量校验；尚无 `prepared.json`，F2 未开始，原主库仍为 49,677,344,768 B、旧 mtime 不变、WAL 0 B，Worker 仍 paused。**不得另启第二份准备进程。**
- 补充 `audit_catalog_retirement.py`（active 原文/页查询差分、retired 显式归档、同 SHA+locator 活跃碰撞识别）、`audit_catalog_consumers.py`（只读 metadata query/SourceResolver 配对差分、StockWiki provider disabled 检查）及 `cutover_source_catalog_db.py`（意图收据、精确旧库/侧文件 rename、切回、两次烟测、精确删除/中断续清理）。工具只在各阶段对应收据存在且 hash 相同时前进，未对生产执行切换/删除。
- Windows 临时夹具第一次 cutover 因测试建库连接未显式关闭遭 WinError 32；修复夹具后切换/切回通过。随后补充烟测间隔、精确旧文件删除和重命名中断后反向恢复测试，6 passed；先前查询/错误/迁移合并测试 31 passed。该失败证明生产若仍有占用句柄会拒绝切换，不能把重命名错误当成功。
- 只读按 `documents.primary_source_id` 分组核查，当前同时挂 active 与 non-active 文档的 source ID 数为 **0**；这是来源级查询截断风险的初筛，不代表所有 `evidence_spans.source_id` 完全无交叉。F3 仍要核实际 span locator 碰撞与来源查询行为。
- 增补消费依赖快照 SHA、精确侧文件白名单、Worker 二次检查和切换中断夹具后，合并测试重新运行 **33 passed**；`git diff --check` 无空白错误（仅已有文件行尾规范警告）。F1 此时仍运行，没有把夹具通过误记为生产验收。
- 约 18:20 UTC 只读 Win32 进程计数显示准备进程从 F0 起累计约 235 GB read transfer、约 14.98 GB write transfer；这些是进程 I/O 计数（含缓存/重复读），不是新增磁盘占用或 F1 单阶段数据量。可见旧 SQLite 的完整校验具有明显读放大；后续 W7 性能合同需按实际 read bytes/墙钟记录。
- 约 18:22 UTC 准备进程打印 `F2 compress and verify full decompression stream`，表示 F1 的逐表行数/字段摘要、活跃 span、外键与影子库 `quick_check` 已通过；候选实际文件暂为 3,055,796,224 B（尚为 `.partial`），旧库未切换。F2 压缩、`zstd -t`、完整流 SHA 与最终 `prepared.json` 尚在执行中，不能提前判为完成。
- 18:30:01 UTC 正式 `prepared.json` 发布：旧库 49,677,344,768 B / SHA `69f498a2…`，active-only 候选 3,055,796,224 B / SHA `63c359aa…`，完整 zstd 6,198,704,362 B / SHA `1bc09746…`；完整解压流 49,677,344,768 B / SHA `69f498a2…` 与源相同，`zstd -t=ok`、FK/quick_check=ok，active span 1,490,530 行摘要一致。备份无完整落盘恢复演练（用户排除），生产 DB 未切换、旧 DB 未删除。
- F3 真实证据差分 `evidence_audit.json` 已发布 `passed`：31 个 active 样本查询一致、25 个 retired 与 5 个其他非活跃样本均按预期归档失败关闭；源 ID 混用 0、样本 locator 碰撞 0。此收据明确 `consumer_contracts_checked=false`，不能单独允许 F4；消费端审计正在运行。
- 用户询问与 revenue-forecast 三项目在飞计划是否冲突。只读检查其 Round 117 与 I-11-B/I-05-C/I-06-A：当前 I-11-B 主体不碰本轮 SQLite，I-05-C 未来将改 CW DAG/service/processing_demand，I-06-A 可能落 store 持久需求；未来 W0/W6 必须复用正式合同。本轮新增 `cross_project_coordination_2026-09-26.md`，F4/F5 固定 14 个 CW 源码+生产配置及三项消费入口 SHA，变化则停。
- F3 消费者审计第一次因审计脚本误把 `fiscal_year` 当作文档主表列而失败；核真实 schema 后改从已核验的 `source_metadata_assertions` 抽样，确认临时 hardlink 清理，再重跑通过。`consumer_audit.json` 记录 6 组 metadata query、12 组无下载 resolve 均与旧库相同（reused_equivalent 2、missing 4、ambiguous 6）；StockWiki 的 company-wiki provider 仍 disabled。该审计未跑真实下游业务流程，收据如实标 `downstream_live_business_run_performed=false`。
- 预切换夹具改用仓库内 `--basetemp=.pytest_retirement` 避开受限系统 TEMP，相关 33 项通过；`git diff --check` 无空白错误。核了运行目录、三个精确文件、Worker paused、WAL 空、operation.lock 不存在。18:47:45 UTC F4 `cutover.json` 成功：3,055,796,224 B 的 active-only 候选成为生产 `catalog.sqlite3`，49,677,344,768 B 原库改名 `catalog.sqlite3.retiring.<run_id>` 并保留回滚，压缩备份仍在；尚未释放旧库空间。
- 18:52:17 UTC 第一轮 `smoke_1.json` 通过：生产/旧库/备份 SHA 与准备收据相同，active span 1,490,530，FK/quick_check=ok，真实 active EvidenceSpan 查询返回预期文档。随后生产只读 CLI `status` 返回 documents 23,530、sources 43,112、evidence_spans 1,490,530；`query` 和 `resolve --entity 微软 --document-kind annual_report --fiscal-year 2025` 正常返回（该 resolve 为 `missing`，原因是已有 Microsoft 10-K FY2025 capture_incomplete，与 F3 旧/候选差分一致）。F5 前仍需间隔至少 10 分钟的第二轮烟测及再次合同 SHA 核对。
- 19:03:16 UTC 第二轮 `smoke_2.json` 通过，距首轮 **658.450 秒**，三文件 SHA、FK/quick_check、active span 数和样本证据一致；18 个本仓/跨仓合同文件 SHA 未变化。附加的生产退休证据取样 SQL 因旧库扫描慢而主动停止；正式 F3 已对 25 个 retired 样本验证 `legacy_evidence_archived`，没有将附加尝试计为通过。
- 19:06:54 UTC `retired.json` 发布：精确旧文件 49,677,344,768 B 和记录的零 WAL/SHM 已删除；3,055,796,224 B 新主库及 6,198,704,362 B 完整备份仍在，Worker paused、无 operation.lock。清理前同卷空闲 75,756,457,984 B，清理后 125,431,902,208 B；准备前 85,026,582,528 B，故整轮实际净增 **40,405,319,680 B = 37.630 GiB**。理论文件净减少 40,422,844,182 B = 37.647 GiB；差额不能据此归因。用户排除的完整落盘恢复未做，真实下游业务流程未跑。

## Session: 用户要求减少重复审查和测试

### Phase 18（计划节奏修订）

- 用户指出逐小节点复核过多且拖慢进度。审查确认旧方案中 W/N/D 每卡独立签收、每次保存全套 hash、F 路径反复哈希 46 GB、Worker F01–F20 各 10 次和额外 72 小时 soak 属于重复成本。本轮 F5 已在执行中，未中途改动其删除门禁。
- 新建 `milestone_review_cadence.md`，将后续审查合并为 G0 合同、G1 W1–W4 集成小试、G2 检索消费、G3 Worker 受控发布、G4 物理迁移/删除批次。普通代码修改只跑相关测试与轻量自检；大库完整校验只在准备/不可逆切换执行，重复观察烟测可用轻量状态/读取；原文真正删除前仍逐文件只做一次完整 SHA。输入改变只重开受影响节点。
- 同步 `execution_cards.md`、`review_protocol.md`、`test_acceptance_plan.md`、`worker_parallel_execution_plan.md`、`raw_disposition_plan.md` 与入口 README。Worker 保留 20 个故障模式各一次确定性注入，对竞态点做 3 次真进程复验及一次至少 100 job 的有界混合负载；不再加本专题 72 小时隔离 soak，外部 v5/R4 的正式门禁仍服从或复用其收据。物理删除人审按批次，逐文件技术身份核查不省。
