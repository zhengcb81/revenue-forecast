# Findings：叙述性证据试点

## Requirements

- 财务报表标准数值可由外部清洗数据接口提供；优先处理行业、主营业务、新业务、出海、风险和运营驱动的叙述。
- 覆盖年报、半年报、季报、招股书、再融资文件、投资者关系材料及英文财报电话会议。
- 电话会议从 earnings-transcripts 工具发现和抓取，原文 TXT 统一登记在 company-wiki；不翻译，做来源锚定的选择与摘要。
- 仅维护本计划目录，不改变现有项目计划、生产数据或 Worker 状态。

## Prior Read-only Findings

- 现有 source catalog 数据库约 46.27 GiB、约 2720 万 EvidenceSpan；高基数的全量切片及其 JSON/索引是首要排查对象，不能简单归因于 PDF 原件或仅仅归因于重复正文。精确空间分解尚未完成。
- 现有 section_extractor 只针对少数财报/招股书章节；投资者关系、再融资等高价值类型不在默认目标集合。
- earnings-transcripts 存量 43 份英文 TXT，约 2.44 MB，分属 6 家公司；原文混有网站编辑摘要和电话会议逐字稿，至少有两种版式、若干说话人/转写异常。
- 跨项目职责：company-wiki 提供可追溯来源和版本化导出；StockWiki 持有投资研究状态；revenue-forecast 消费驱动证据；invest-quick-scan 可消费轻量证据包。

## Sample Register

样本根路径：PDF 为 `C:/Users/郑曾波/Projects/company-wiki/companies/`；TXT 为 `C:/Users/郑曾波/Projects/earnings-transcripts/earnings-transcripts/transcripts/`。文件哈希是只读计算值；表内只展示前 12 位，完整值可按文件重新计算。

| 编号/类别 | 相对路径或文件名 | 页/行 | 大小 | SHA-256 前 12 位 | 试点用途 |
|---|---|---:|---:|---|---|
| P01 年报 | `中微公司/raw/financial_reports/中微公司：2025年年度报告.pdf` | 259 页 | 9,165,875 B | `d64c410832f2` | 大量财务表与业务讨论混排 |
| P02 半年报 | `中微公司/raw/financial_reports/中微公司：2025年半年度报告.pdf` | 188 页 | 6,361,468 B | `91ae4978b694` | 中期进展与期间增量 |
| P03 季报 | `中微公司/raw/financial_reports/中微公司：2026年第一季度报告.pdf` | 15 页 | 217,264 B | `ab7bb0076b2a` | 小文件中财务与业务信息相邻 |
| P04 招股书 | `中微公司/raw/prospectus/中微公司：首次公开发行股票并在科创板上市招股说明书.pdf` | 429 页 | 11,211,796 B | `19cdb41e03b2` | 基线业务、技术与风险 |
| P05 可转债 | `三角防务/raw/research/三角防务：1-1西安三角防务股份有限公司创业板向不特定对象发行可转换公司债券募集说明书.PDF` | 302 页 | 18,858,880 B | `2ea34bcb188f` | 项目用途、产能和阶段，首封面无可提文字 |
| P06 定向增发 | `三角防务/raw/research/三角防务：西安三角防务股份有限公司向特定对象发行股票并在创业板上市募集说明书（注册稿）.PDF` | 191 页 | 5,595,592 B | `cd803fe9528f` | 募集投向与注册稿状态 |
| P07 投资者关系 | `万润股份/raw/research/万润股份：投资者关系活动记录表20260515.pdf` | 6 页 | 153,851 B | `221467c15a24` | 套话与具体业务问答混合；有跨页问答 |
| P08 投资者关系 | `万润股份/raw/research/万润股份：投资者关系活动记录表20250430.pdf` | 13 页 | 236,281 B | `4455d6f099f5` | 密集业务问答 |
| P09 格式制度 | `中微公司/raw/investor_relations/中微公司：投资者关系管理办法（2025年8月）.pdf` | 7 页 | 167,252 B | `76e146985388` | 应跳过业务切片的负例 |
| P10 会议通知 | `八方股份/raw/research/八方股份：关于召开2025年年度暨2026年第一季度业绩说明会的通知.pdf` | 3 页 | 95,673 B | `823b2bdee3b6` | 文件名含“业绩说明会”但正文不含会议问答的负例 |
| T01 新版 TXT | `MSFT/MSFT_Q4_2026_earnings_call.txt` | 340 行 | 66,324 B | `4ac3b4f0fa1b` | 网站摘要与逐字稿并存、说话人冒号样式 |
| T02 旧版 TXT | `NVO/NVO_Q4_2024_earnings_call.txt` | 604 行 | 66,597 B | `d00e2a4537b8` | `Prepared Remarks`/`Questions & Answers`、说话人独立行 |

只读 catalog 基线：P04 已有 `normalized` 和 `sections` artifact，22,458 个 evidence spans；P05/P06 均被归入 `document_kind=other` 且没有解析产物；P07/P09 为 `investor_relations` 且当前无解析产物。P01–P04 的匹配记录为 `retired`，但 P04 仍有历史解析产物；这些查询不代表最新可消费状态。试点按原文直接读取，不以 `retired` 等同于文件缺失。

## Pilot Evidence

### 方法和证据范围

使用 PyMuPDF 1.26.7 只读打开 10 份 PDF，并对相关页使用 `page.get_text(sort=True)`，页码从 1 起；括号内偏移是该方法产生的**页内字符偏移**，从 0 起，尚不是生产 EvidenceSpan locator。对 2 份 TXT 读取原始 UTF-8 行。逐页检索仅用于找候选，随后人工阅读问答及上下文；中文来源做中文来源摘要，英文 TXT 做英文来源摘要。未调用 LLM、Worker、生产解析或下游投资分析。本轮结果是小样本的可行性与失效模式验证，**不构成整体召回率或成本节省率证明**。

### 试点来源摘要卡（人工抽样产物）

| 案例 | 原文定位与锚点 | 来源摘要 / 选择结果 | 必须保留的限定 |
|---|---|---|---|
| C01 年报新业务 | P01 PDF 第 40 页，页内 64 起“新产品开发已经取得了显著成效” | 多款 LPCVD/ALD 薄膜设备进入市场并获重要客户重复订单；EPI 处于客户端量产验证；湿法设备布局涉及**拟议**收购。选取产品进展，略过相邻口号式增长表述。 | “重复订单”“量产验证”“拟购买”是三种不同成熟度。 |
| C02 半年报中期方向 | P02 PDF 第 21 页，页首行业及业务讨论 | 半年报将自主研发、合作及潜在并购作为设备类别扩展方向，提出未来 5–10 年覆盖更广设备市场的愿景。需与年报更新做时间线。 | 未来覆盖是管理层计划，不是实现事实。 |
| C03 季报页内混排 | P03 PDF 第 3 页，页内 744 起“四款MOCVD 新产品” | 四款面向功率器件/显示应用的新产品进入客户端验证，部分获得批量订货；同页下半部转为收入、利润和非经常性损益。保留运营进展，财务表走结构化数据链。 | 不能按“季度财务页”整页跳过；“部分”不应扩大为全部四款。已视觉核对版面。 |
| C04 招股书历史基线 | P04 PDF 第 114 页，页内 55 起“第六节 业务与技术” | 招股时的刻蚀、MOCVD 产品、应用领域和客户阶段构成历史基线。相邻产品表需按产品保留关键用途。 | 招股书描述是其披露时点的状态，不能直接当 2026 年现状。 |
| C05 可转债项目 | P05 PDF 第 231 页，页内 518 起“项目建设的必要性”；第 13–14 页对应供应商/建设风险 | 项目论述从锻件向加工与零件交付延伸；蒙皮镜像铣项目受供应商产能和技术验证制约。建设理由与执行风险应成对呈现。 | 募投、产能消化和订单优势是预测/论证，不是已交付结果。 |
| C06 定增认证门槛 | P06 PDF 第 3 页，页内 132 起“募投项目供应商认证和产品认证的风险”；第 101 页为项目必要性 | 数字化集成中心向下游装配延伸，需要供应商及产品认证；文本给出认证时长的预计区间。项目逻辑和认证条件均应入选。 | 注册稿中的时间与达产安排为预计值；“无需”某项认证仅适用于文中明确的原有锻件项目。 |
| C07 IR 中试线 | P07 PDF 第 6 页，页内 198 起“16、问：” | 对硫化锂中试线，管理层表示当时预计 6 月底前建成并开展中试。单独保留问答与时间条件。 | 本样本不能证明后来按期建成；待后续来源验证。 |
| C08 IR 跨页问答 | P07 PDF 第 5 页问题 15 延续至第 6 页回答 | 车用沸石需求波动背景下，公司称推进石化催化分子筛，已有产品销售。页边界不能截断问答。 | 问题中的估值比较是投资者观点，不写作公司事实。 |
| C09 IR 错误前提 | P08 PDF 第 2 页，页内 61 起“2、问：”，随后问题 3 与回答 | 公司称非车用沸石已在石化催化及 VOCs 领域销售；问题 3 称 OLED 等业务收入不足 5%，回答明确纠正为所列两个 OLED 业务主体占比已超 25%。 | 必须区分投资者提问数字与管理层纠正；合作意向书不等于新增收入已实现。已视觉核对问答表格。 |
| C10 英文新式电话会 | T01 第 124 行起为 `Full Conference Call Transcript`，第 236–248 行讨论模型选择，第 252–258 行讨论容量 | **English source summary:** Management described enterprise model choice as part of its platform design. The CFO said demand still exceeded available capacity and efficiency gains were monetized quickly during the quarter. | 第 1–123 行含网站编辑摘要、词汇表等；来源为 Motley Fool 转写，不能把编辑摘要误标为管理层逐字发言。 |
| C11 英文旧式电话会 | T02 第 178 行起 `Questions & Answers`，第 184–212 行为双问题、多管理层回答 | **English source summary:** Management attributed prescription patterns partly to benefit-plan changes and starter-dose supply. On a separate CagriSema trial question, the development executive said it was too early to speculate on superiority. | 按两个子问题分别锚定答复；不能把“尚早判断”摘要成临床优势已证实。 |
| N01 制度负例 | P09 PDF 第 1–7 页 | 规定投资者关系管理职责、形式及合规要求，未发现具体业务动态；登记/检索原文即可，业务切片状态 `skipped_no_narrative`。 | 仅凭“投资者关系”文件名会误收。 |
| N02 会议通知负例 | P10 PDF 第 1–3 页 | 公告会议时间、地点和提问方式，并无正式会议回答；登记元数据与事件时间即可，业务切片状态 `skipped_event_notice`。 | 不能把“将回答问题”生成已经答复的问答。 |

### 对现行机制的直接检验

- P04 现有 `sections` 索引只含 `risk_factors`、`business_and_technology`、`important_events` 三个角色；其中 `business_and_technology` 覆盖 **83 页、302,779 字符**（页 114–196）。章级定位有用，但还须章内选择。现有 `normalized.md` 为 2,490,019 B，章节索引为 453,482 B；不能把章节 artifact 大小等同于最终摘要大小。
- 现行 `section_extractor.TARGET_DOCUMENT_KINDS` 包含年报、半年报、招股书、券商研报，未包含季报、投资者关系、再融资和电话会议；P03/P05–P08 的正例不进入该抽取范围。
- P05/P06 被归为 `other`，显示再融资识别和准入必须先修，随后才能按项目/风险抽取。
- P03 第 3 页及 P08 第 2 页的渲染图人工核对过：前者的运营叙述与财务段落在同页，后者一个表格单元连续承载多个问答。页级二元保留/丢弃均不够。
- T01 原文 65,980 字符，正式逐字稿从字符 7,214/第 124 行开始；网站尾注从字符 64,917/第 334 行开始。T02 原文 65,986 字符，准备发言从字符 545/第 20 行开始，问答从字符 27,770/第 178 行开始，尾注从字符 65,219/第 598 行开始。两种版式必须分别识别正文边界。

### 尚未验证

- 全语料的召回率、误收率、节省的数据库体积、LLM 费用与运行时长；本试点只有 12 份样本和有限人工片段。
- 英文电话会在线重新下载的可用性、FMP 来源校验和指定财年季度检索；本轮仅检查本地代码与已有 TXT。
- 现有来源版本中 `retired` 与下游可消费状态的完整影响；需在实施前做同文件多版本链路检查。

## 第二轮只读小样本实验（2026-09-26）

**方法**：不调用 Worker/LLM、不落盘解析产物。以 PyMuPDF 1.26.7 对 P03 第 3 页、P04 第 114 页、P08 第 2 页分别运行 `get_text('blocks', sort=True)` 与 `find_tables()`，按现行 `_pymupdf_page_snapshots` 的“块与表格 bbox 相交即排除正文”规则计数。另对 P05 第 231 页、P07 第 6 页比较 `get_text('text', sort=False/True)` 长度。对生产 `catalog.sqlite3` 使用 SQLite URI `mode=ro&immutable=1` 与 `PRAGMA query_only=ON` 读取元数据，并以固定随机种子 20260926 在 rowid 空间分散抽取 1000 条旧 `evidence_spans`；这是样本估计，**不是全库表/索引字节的精确分解**。尝试 `dbstat` 失败：当前 Python SQLite 没有该虚表，因此不把样本比例直接外推为准确的 46 GiB 构成。

| 观察 | 只读结果 | 对设计的影响 |
|---|---|---|
| 旧库容量/空闲页 | DB 46.266 GiB，4096 B/page，12,128,258 页，freelist 仅 9 页，WAL 当时 0 B | 不能把一次 `VACUUM` 当成主要节省路径；应先阻止新增高基数行，并在独立迁移中测表/索引占用。 |
| 迁移暂存容量 | 2026-09-26 C 盘空闲 83,279,212,544 B，约 77.56 GiB；一份与主库等大的副本约需 46.27 GiB，两份约需 92.53 GiB，尚未计 WAL/索引重建/备份增长。 | 现有 C 盘余量不足以同时放两份完整副本；W7 先核经验证的独立卷/快照和最坏空间预算，不能靠删除生产库临时腾空间。 |
| 旧 span 随机样本 | 1000 条中 820 条 locator 为 table cell，496 条 `raw_text` 为空；`raw_text` 平均 16.9 B，`span_json` 平均 812.6 B（p95 932 B）。JSON 含定位、结构值、来源和解析元数据，表上另有 3 个索引。 | 空表格单元和每单元 JSON/索引可能是大库的重要驱动；“46G 主要因为全文文本重复”过于简单。新流水线要按候选/选中单元存证据，禁止重新物化整表空单元。 |
| P08 IR 第 2 页 | 表格识别为 1 行 2 列，bbox 约占页面 71.9%；按旧排除规则 30 个正文块中 29 个被排掉，仅余约 4 字符，而表格单元含 864 字符和多个问答。 | 不能直接复用旧“表格优先、相交正文丢弃”的 PDF 快照函数；IR 需保留双视图并在大单元内拆问答。 |
| P04 招股书第 114 页 | 产品/应用表 bbox 约占 10.2%；27 个正文块中 7 个与表相交，表格单元含产品类别、应用领域等业务描述。 | 不能一概排除表格；应区分标准财务表和产品/客户/产能/募投等业务表，并校验表格提取与页文本的锚点覆盖。 |
| P03 季报第 3 页 | 财务表 bbox 约占 1.4%；32 个正文块仅 1 个相交，运营叙述仍在同页。 | 页级/表格级二元过滤仍不够；同页要按单元选择。 |
| PDF 文本偏移稳定性 | P03/P04/P05/P07/P08 五页 `sort=False` 与 `sort=True` 文本均不同，字符长度差分别为 157/190/55/213/59。 | 试点中的“页内字符偏移”只对指定提取方法有效，不能直接当持久 locator；新证据要绑定 parser 版本、精确片段 hash 与可回放的页/段/表锚，升级解析器时重验。 |

**仍待验证**：全库 table-cell/空单元比例与每张索引实际占用、不同 PDF 版式下双视图的召回/精确率、长期存储节省、按需回源时延、跨版本 locator 重验。旧来源 P01–P04 为 `retired` 的实际可消费语义仍要在隔离 catalog 中验证；只读 raw 试点不能证明这些来源当前可发布。

### 全文检索的最小反例

现有 `source_catalog/evidence_query.py` 的主要查询按精确 `source_id/document_id` 列出旧 spans；本仓 `source_catalog` Python 代码中未找到 FTS 虚表或 `MATCH` 查询。生产 SQLite 编译了 FTS5，但当前库无虚表。在**纯内存** SQLite 中插入一行含“硫化锂的中试线”的中文句子：`unicode61` 的 `MATCH` 对“硫化锂”“中试线”均返回 0；`trigram` 的 `MATCH` 对这两个三字词返回 1，但“出海”两字词返回 0（`LIKE '%出海%'` 可找到，索引是否有效和大库时延未测）。这证明不能把“引入 FTS5”直接写成中文全文检索已解决。W0/W5 要先定义中文两字词、英文词、精确短语、OCR 页和结果定位的查询合同，再比较轻量页级索引、trigram/分词器及按需回源的空间与 p95。新 DAG 不写全量 normalized 后，**现有证据列举接口无法自动替代全文检索**。

### 降容升级的附加只读/内存试验

对上述固定 seed 的 1000 条旧 `span_json` 仅在内存中测试 zlib：原 JSON 合计 812,588 B，逐行压缩合计 469,528 B，合并为一个压缩批次 175,172 B（原 JSON 的 21.6%）。大批量压缩能利用重复字段名，提示按来源的冷归档有潜力；这**不是**生产归档文件大小，更不是全库容量预测，未含 SQLite B-tree/索引、其它表、检索索引和备份。试图精确全库计数的只读扫描两次均因耗时较长主动中止；本机 Python/CLI SQLite 都没有 `dbstat`。精确分解及缩库预测必须在独立存储/副本上完成，详见[降容升级方案](space_reduction_upgrade.md)。

另一固定 seed（20260927）抽取 1200 行并把 `span_json` 解码后与关系列逐字段比较：1022 行为 table cell；JSON 平均 815.5 B。`span_id/source_id/locator/raw_text/parser_name/parser_version/parse_status` 七个字段与独立列逐行完全相等；这些键值在 JSON 内合计约 418,218 B，另有 table cell 的 `structured_value.raw_value/value` 再复制正文约 18,324 B。两项相加为 **436,542 B**，约占样本 JSON 的 **44.6%**（364 B/row）。之前记录的 460,942 B / 47.1% 比这两项多 24,400 B，未找到可复核的分项依据，故撤回该总数；W0 应用固定脚本复算。即使校正后，这仍只是样本 JSON 中已识别重复字段的比例，不是全库 DB 可回收率；行头、索引、其他结构和唯一业务字段未计。它支持 vNext 不重复嵌入身份/定位/parser 字段，正文也只存一次。

## 旧库提前退役的额外只读与临时库演练

生产库 `catalog.sqlite3` 当前 49,677,344,768 B（46.266 GiB）、WAL 0 B；`worker_control.json` 的 desired_state 为 paused。SQLite 中除 `evidence_spans` 外有 17 张表，共 189,580 行：其中 sources 43,112、documents 23,530、locations 46,606、artifacts 8,191。documents 中 active 13,839、retired 9,501，另有 upstream_rejected 189 与 quarantined 1。用 `idx_documents_status_kind` 和 `idx_spans_document` 的关联索引精确计数，active 文档共有 **1,490,530** 条旧 span（8.75 秒）；这不是对全表表/索引占用的分解。

在系统临时目录执行两次**不改源 DB**的 SQLite 复制试验，均完整复制原 DDL/非 span 数据和索引，并在结束后自动清理：

| 复制范围 | 临时 DB 大小 | 检查 | 实际意义 |
|---|---:|---|---|
| 17 张非 span 表 | 225,280,000 B = 214.84 MiB | 189,580 行，`foreign_key_check` 无错误，`quick_check=ok` | 来源、文档、位置、artifact、退役/恢复审计等目录状态可保存为小库；不是完整旧证据服务 |
| 上述目录 + active 的全部 1,490,530 条 span | 3,059,200,000 B = 2.849 GiB | 共 1,680,110 行、现有索引重建，`foreign_key_check` 无错误，`quick_check=ok`；总耗时约 143 秒 | 保持 active 旧证据热查询有真实空间基础；retired 旧证据仍需明确的归档/冷读状态及可恢复备份 |

`.source_catalog/derived` 约 2,826,010,634 B，`index` 约 45,052,670 B；`source_manifests/archive/2026-08-07/retired-evidence.jsonl.gz` 为 5,207,478,767 B，首条可解析为旧 span JSONL。ADR-009 记录 2026-08-07 归档 25,708,956 条 retired span，但 H01 独立复核指出该归档缺不可覆盖发布、逐项 hash 与稳定快照保证，不能直接替代完整旧库备份。StockWiki 生产 `config/source_provider.yaml` 当前 company-wiki provider 为 disabled；跨仓实际读路径仍需在切换前作差分验证。

只读抽取 6 处各 8 MiB 数据块做 zstd level 3 试压，比例分别约 15.3%、12.7%、12.7%、13.1%、12.2%、32.1%；**这不是完整 DB 压缩率**。当前磁盘空闲约 85,079,416,832 B（79.24 GiB）。完整压缩快照及恢复演练的峰值空间要在实际文件产生后判定，详见[提前退役审查卡](early_catalog_retirement.md)。

## 原文处置补充核查（2026-09-26）

- `src/company_wiki/source_contract/source_manifest.py` 中 `SourceManifest v1` 保存 source SHA、相对原路径、大小、`immutable_status`；`verify_file()` 在原路径不存在时失败。现有两个 immutable 状态未包含有意删除，因此需单独版本化 `SourceDisposition`，保留历史 manifest 而不伪称文件仍可回读。
- 生产 SQLite 只读查询的 `company_raw`/`original_primary`：active 7,524 个 location、历史 `observed_size` 合计 6,511,169,498 B；retired 9,046 个、合计 18,641,858,464 B。location 可能缺失/移动/不在 C 盘，且 retired 不能等同无价值；实际可回收字节须 D0 按真实路径/卷、SHA、别名和消费引用逐件核对。
- 旧源身份按 SHA，路径是 location；同 SHA 的重复副本可以在保住 canonical 一份且迁移所有路径引用后清理。唯一低价值原文删除会丧失未来原文回读/复核能力，不能仅由 `skipped_*`、未命中关键词或文档类型推出。详见[原文处置 D0–D5](raw_disposition_plan.md)。

## 逐步空间账补充只读实测（2026-09-26）

- 三处主要本项目数据目录的文件逻辑长度：`.source_catalog/` 52,700,659,299 B，`source_manifests/` 5,207,479,410 B，`companies/` 25,173,861,091 B；合计 83,081,999,800 B（77.376 GiB）。公司原文目录 PDF 15,129 个、25,073,770,125 B（23.352 GiB），不能据此认定均可删除。
- 在不落盘、不改生产 DB 的条件下用 `zstd -3 --stdout` 读取完整 49,677,344,768 B 主库并计输出流：6,198,704,362 B（5.773 GiB，耗时约 96 秒，输入前后 stat 长度与 mtime 一致）。此计数不是可恢复备份，正式 F2 仍需写快照、流/文件 SHA 与实际恢复验证。
- 以活跃临时库 3,059,200,000 B 和压缩流预算计算，同盘 F1/F2/F5 净释放约 37.644 GiB；完整恢复临时文件也在 C 时峰值增量约 54.888 GiB。C 盘当时空闲 85,058,437,120 B（79.217 GiB），理论峰值余量约 24.329 GiB，未含安全缓冲。逐步公式见[空间账](stepwise_space_budget.md)。

## Resources

- `AGENTS.md`（项目职责边界）
- `docs/plans/source-catalog-worker-recovery-v5-2026-09-03/`（现有独立 Worker 计划）
- `docs/plans/core-section-extraction/`（已有章节提取计划）
- `C:/Users/郑曾波/Projects/earnings-transcripts/earnings-transcripts/`（电话会议抓取与 TXT 样本）
