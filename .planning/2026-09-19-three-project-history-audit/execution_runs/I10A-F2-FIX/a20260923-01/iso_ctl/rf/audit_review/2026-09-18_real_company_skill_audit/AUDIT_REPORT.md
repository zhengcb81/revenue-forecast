# revenue-forecast 真实公司实跑与独立审计报告

执行日期：2026-09-18—19。统一信息截止日：2026-09-18。用户要求：A股、港股、美股代表公司逐一实跑，独立审查研究、预测、filing-fetch复用/下载及company-wiki跨目录数据湖；本轮记录发现，暂不修改代码。

## 结论

**当前不能验收为三家公司完整预测成功。** 已实际执行三家公司的规定来源准备入口、已有文档复用与授权缺失文档下载，并独立核验原件、来源清单、哈希、目录和索引。三家公司均被真实前置问题挡住，正式模型输入未形成，`revenue_forecast.py`计算/发布阶段未执行，正式forecast JSON、Markdown及发布回执产出均为 **0/3**。没有用空模板报错、测试夹具、手填receipt或研究草案冒充完整运行。

已确认部分基础能力有效，但关键新文档链路失败：已有紫金年报可稳定零下载复用；四份历史年报的跨根文件与索引一致；小米、微软新年报实际落盘且sidecar匹配，却没有进入可查询索引。研究侧识别出三种对结果有实质影响的问题：紫金并表/权益与内部交易口径，小米年中实际与EV爬坡，微软截止日前分部重分类。

**预测准确性、正式敏感性、引擎产出的增长归因/置信度、快照与回测结果、本次正式发布及下游消费均尚未验证。** 研究草案可用于发现假设缺口，不能作为正式可投资预测或准确率提升证据。

## 样本与实测矩阵

| 样本 | 选择理由及财年 | 已执行流程 | 当前结果 |
|---|---|---|---|
| 紫金矿业 601899/CN | 资源周期、成熟矿山与锂/扩产项目并存；FY2025基期、拟预测FY2026–28 | 2025年报source preparation；filing-fetch两次reuse；2026H1 reuse及CNINFO授权获取 | 历史raw复用通过；正式来源因not_reviewed阻断；H1 discover HTTP403 |
| 小米集团 01810/HK | 手机成熟业务、IoT/互联网、EV商业化爬坡；FY2025基期、拟预测FY2026–28 | source preparation reuse；授权下载；下载后再次reuse | dayu-hkex下载及canonical原件/sidecar落盘通过；索引失败；再次reuse仍not_found |
| 微软 MSFT/US | 软件/云成长、传统授权及设备业务，分部口径变更；FY2026基期、拟预测FY2027–29 | source preparation reuse；授权下载；下载后再次reuse | dayu-sec下载及canonical原件/sidecar落盘通过；索引失败；再次reuse仍not_found |

这是三个有代表性的诊断样本，不构成对所有行业、生命周期或31个模型的实证验收。银行、保险、REIT、临床前/零收入企业、项目制和困境公司本轮未覆盖。

## 已通过的检查及边界

- **身份及已有raw复用**：紫金请求解析到verified active的601899/CN。两次filing-fetch响应字节完全相同，均calls=2、downloads=0，envelope parser/llm调用均0，outcome=reused_existing。证据：runs/03、13。
- **历史文件完整性**：独立agent用只读SQLite保存148条相关记录，对紫金FY2024/25、微软FY2024/25的20个location和8个artifact重算hash/size，全部匹配。紫金company_raw/Dropbox、微软company_raw/dayu的同字节副本及导出索引相符。范围限于抽样；不等于所有artifact可复用。
- **HK/US市场路由及真实落盘**：sidecar分别为dayu-hkex-cli和dayu-sec-cli，provider/URL/财期可查；独立核对新raw字节与sidecar SHA-256、大小一致。详见independent/acquisition_aftercheck.json。
- **未授权缺失不下载**：复用请求不带allow-download，没有悄悄启动下载；小米和微软返回not_found。
- **暂停状态保持**：背景worker事先为paused，授权获取后仍paused且原控制时间戳保持，没有擅自resume用户暂停的worker。没有进行删除/清理。
- **安全拒绝有效**：真实not_reviewed来源被source_preparation阻断。本报告不建议取消这条安全门。

边界：三家公司没有符合条件的仅Dropbox/dayu根、active且capture元数据完整的年/中报候选。历史同字节跨根核验通过，**外部根唯一副本直接返回handle未证实**；未为造测试而移动或删除canonical文件。

## 主要发现与优先级

### F01｜P1｜新年报已落盘，但生产扫描策略与根配置不匹配，不能入库复用

小米和微软的授权运行均报 `canonical file was written but exact provider identity did not resolve`。独立读取scan_runs进一步发现真正原因：

`scan_root_strategy: v2 scanner unavailable (fail closed): root 'company_raw' has no adapter_id (2.x policy required)`

两次扫描状态为completed_with_errors、files_seen=0。当前runtime policy中v2_scan_shadow=true，而company_raw配置没有adapter_id。新原件的SHA在sources/documents/locations/assertions四张表中均0条。写入者先复制raw/sidecar，调用扫描但没有将扫描报告的失败作为直接返回原因，之后exact resolve失败，被表述为身份问题。

**影响**：用户已支付下载/研究等待成本，文件存在却再次被判缺失；后续允许下载可能造成重复网络获取风险。本轮只重试reuse，没有再次允许下载，故不宣称已证明重复下载实际发生。

证据：runs/07、08、09、10；independent/acquisition_aftercheck.json；company-wiki/src/company_wiki/source_catalog/canonical_writer.py中的import_staged。建议未来修复扫描策略与根适配的一致性、失败透传、下载后恢复/再索引及重复调用验收；本轮未执行修复、切换flag或重建生产索引。

### F02｜P1｜已有原件capture_ready，正式消费仍缺少可执行的review步骤

紫金原件可以返回capture_ready和verified_input，但envelope为not_reviewed，bundle_usable=false。source_preparation拒绝是正确行为；问题在于现有主CLI和操作文档没有找到可操作的review/修复命令。库中有receipt记录函数，不能据此直接UPDATE生产数据库或手填not_detected。

证据：runs/02、03、13，independent/data_pipeline_review.md的IND-D01。建议区分raw-ready、review-ready、artifact-ready，并提供受支持的审查及最小补处理路径。

### F03｜P2｜错误分类、可重试属性和嵌套长文本损害可诊断性

source_preparation把缺文档not_found统一包装为upstream/exit3，而文件头将not_found/not_admissible列作exit1。CNINFO的HTTP403返回upstream_unavailable及retryable=true，上层转换成fatal/retryable=false，再经嵌套JSON字符串截断，根因只能从长字符串末段辨认。

HTTP403属于本次提供商访问失败，不能据此认定抓取算法错误；**错误语义丢失**是独立的接口契约问题。证据：runs/04、05、11、12。建议结构化保留stage、provider、error_code、retryable、cause和完整诊断附件。

### F04｜P2｜artifact存在不代表符合当前复用契约

抽查8个派生文件虽存在且hash匹配，但部分normalized为partial、缺schema或source_sha256，部分summary也缺绑定。紫金bundle具体拒绝原因为artifact_status_not_completed和artifact_schema_unsupported，valid_handles为空。

建议统计与索引分别展示“文件存在、已完成解析、当前契约可复用”，并提供旧artifact的受控升级/重算；不得只改schema标签伪装通过。证据：independent/raw_artifact_verification.json。

### F05｜P2｜索引新鲜度不足，not_found不等同原件不存在

基线四个根的last_scanned_at均2026-08-20，距信息日29天；该状态可能与用户暂停有关，本轮不擅自归因为后台缺陷。旧索引会遗漏之后出现的文件。应回传扫描新鲜度，并将“已下载未索引、已索引未合格、确实缺失”分别标识。

初次status运行另有审计runner超时竞态：timed_out=true但exit0且有统计stdout，不把它当作完全成功的健康检查，也不把它当作catalog损坏证据。

### F06｜P2｜技能文档版本与边界有冲突

filing-fetch正文仍宣称handle必须在companies子树，后部与配置又支持dayu/Dropbox注册根；应区分新raw写入与外部根复用。revenue的input-construction/compliance说明存在3.6旧文本，而当前模板/schema已3.7；capture键数及host_receipt说明可能诱导执行者删除必需字段。证据见独立审查及小米research.md。

补充静态观察：capture验证要求published<=captured<=as_of。9/19恢复研究、信息集仍9/18时，不能把实际获取时间伪填前一天。此历史信息集重建边界未在本轮正式输入中复现，列为后续专门验证项，而非本次三家失败的已证根因。

## 买方研究与模型实质审查

### 紫金：先解决口径，再讨论量价预测

年报两年四分部对外收入可闭合。FY2025内部交易为234970.146412百万元，若将含内部交易的分部收入直接相加，会相对349079.082852百万元公司收入高估约67.31%。年报摘要矿产铜约109万吨，与不含非控股企业的产销表生产878180吨、销售884943吨不是同一口径。储量、权益产量、并表产量、外销结算量必须分开。

资源模型适用于可售量与净结算价；reserve_depletion还需要可采经济储量与同单位消耗链。新矿须按投产/爬坡/回收率/库存分阶段，不能用已宣布产能替代全年销量。冶炼及贸易的总净额取决于实际控制权，不能按毛利高低改收入定义。最新H1、价格情景和收购范围桥未完整取得，故没有发布三年数值预测。详见ZIJIN/research.md。

### 小米：锁定已实现收入，显式审查EV增量与季节性

底稿以年报五条曲线闭合，2026H1收入208063.227百万元，较2025H1下降，不能延续FY2025高增长直接外推。手机需量价拆分；IoT需补贴/品类/地区桥；互联网不能把期末MAU当平均付费用户，EV收入与AI/服务舍入披露不能被假精确拆分。

研究算术草案已把H1锁定并反推H2，但仍缺EV可交付产能/订单取消、新车型净ASP、独立竞争和历史季节性检验。草案low/base/high是条件路径，不是统计预测区间；没有概率或覆盖率校准。独立agent检查其算术与关键贡献集中度，不能将算术正确提升为投资可用批准。详见XIAOMI/research.md、research_assumptions.json、research_scenarios_NOT_FORMAL.md。

### 微软：新分部桥优先于更复杂的公式

研究者发现截止日前9/2官方8-K/IR已重分类，按新口径八产品线重建FY2025/26历史，不能继续用旧三分部表并声称截至9/18完整。云/订阅未披露的绝对usage、净价、平均席位不应杜撰；direct_growth回退比假造经营恒等式诚实，但长期增速仍须供给/需求/合同转化支撑。

草案的Azure与M365假设对终期贡献高度集中；需要计算资源供给、利用率、价格/产品组合、客户优化与竞争的反证。Q1指引、全年目标、constant currency、ex-TAC与GAAP口径要分别桥接，不能将“high-teens”等模糊指引直接当精确报告值。详见MSFT/research.md、scenario_draft.md、gates_and_target_ledger.draft.md及真实web响应存档。

三家公司共同缺口：正式capture/claim、完整管理沟通和目标检查、独立负向参考类、公司特定敏感性与冻结样本外评估。九维表和模型数量都不能替代这些工作。独立审查文档是最终质量意见，研究agent的自检不视作独立批准。

## 证据导航、现场与完成边界

- `runs/01...13/`：每次真实命令、cwd、UTC时间、耗时、退出码、stdout/stderr及哈希。
- `requests/`：实际请求；`run_capture.py`仅为本轮审计记录器，外层退出0不代表被记录命令成功，应读取run.json.exit_code。
- `independent/`：由独立agent保存的catalog基线/后验、raw/artifact重算、下载后检查、流程与经济审查；最终意见见[review.md](independent/review.md)。
- `ZIJIN/`、`XIAOMI/`、`MSFT/`：公司研究底稿、原文定位、研究用假设及明确标识的非正式算术。
- `implementation_baseline.json`：恢复执行期间的代码/配置哈希基线，不冒充9/18初始状态；工作区已有上一轮方法升级改动，本轮不将其算作审计修复。

本轮仅新增审计目录内文档/日志/研究辅助脚本，生产代码和配置没有由本轮修复；实际授权CLI新增了小米和微软raw/sidecar及相应执行记录。新raw保留原状，未删除staging、移动历史原件、改review状态或开启worker。

`audit_integrity_check.json`核验13组stdout/stderr哈希全部匹配，并检查恢复期间基线中357份产品代码/配置文件无变化。此核验有明确起点，不是对9/18之前已有工作区修改的追溯证明。

本次无法继续正式预测的依据是[当前SKILL](../../SKILL.md)第3步要求财报使用`single production entry scripts/source_preparation.py`，以及[compliance contract](../../references/compliance-contract.md)规定`missing captures ... are hard failures`。这是现有流程的真实阻断，不是要求用户再次批准已授权下载。绕过入口、伪造receipt或修改配置会改变本轮“只审查、不修改”的测试条件，因此未采取。

后续验收顺序：先恢复正式来源准备与新文档入索引，验证同请求第二次零下载；再用三家真实证据形成完整输入并运行计算/发布，独立审查结果、敏感性和目标桥；最后冻结快照，开展未来可得实际值的样本外检验。本轮报告并未声称这些未执行步骤已经完成。
