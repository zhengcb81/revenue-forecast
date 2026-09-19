"""Manual adjudication after reading all 24 company-audit Markdown bodies."""
from pathlib import Path
import collections,hashlib,json,re
H=Path(__file__).resolve().parent; R=H.parents[3]
A='audit_review/2026-08-12_zijin_skill_run_audit/'; B='audit_review/2026-09-18_real_company_skill_audit/'
files=sorted(str(p.relative_to(R)).replace('\\','/') for d in (A,B) for p in (R/d).rglob('*.md'))
assert len(files)==24
C=[]
def c(f,a,b,v,t,q,e,fix): C.append(dict(case_id=f'CC-{len(C)+1:03}',file=f,start=a,end=b,verdict=v,target=t,rationale=q,evidence=e,remedy=fix))
RF='reviews/revenue/deep_clause_ledger.jsonl; reviews/revenue/item_ledger.jsonl'
CHK='reviews/company_cases/independent_checks.json'
for f in files:
 c(f,1,100000,'historical_only','历史运行、研究与限制的完整原文','全文逐段读。保留原日期、命令、来源、因果及限制；历史记录不是本轮重放，更不认证公司事实目前仍成立。工程声明按以下专项和其他独立账本复核。',CHK+'; '+RF,'保持信息截止、真实入口及失败证据；不得把研究底稿/结构通过写成正式预测完成。')
c(A+'task_plan.md',1,90,'supported_scoped','隔离审计完成与产品未修复','此计划完成的是审计与低置信草案；原件复用、安全失败、隔离fallback和缺口分层，未声称正式来源全通过。仍需额外真实入口验收。',A+'trace/filing_fetch_events.md; '+CHK,'将审计完成、预测完成、修复完成设独立状态。')
c(A+'RUN_MANIFEST.md',1,86,'supported_scoped','当时封存与并发工作区边界','代码/产物hash和registry邻近前后记录可支持具体调用，不能追溯证明整个长会话无其他agent写入。独立重算保留结果file hash吻合。',CHK,'下一次将实际加载版本/安装副本/配置一起封存；不以HEAD一项证明运行版本。')
c(A+'TRUST_BOUNDARY.md',1,71,'supported_scoped','draft与未签名来源边界','明确不构成正式发布、四direct_growth与无回测。自报not_detected只是本次审阅结果，不等于共享review迁移或密码学attestation。',A+'trace/source_review.md; '+RF,'保留低置信与不确定性；不能以透明披露消除关键资料缺失。')
c(A+'mine_coverage_matrix.md',1,84,'supported_scoped','资源/储量/产量/并表与未来收入隔离','识别权益量不得二次乘权、资源不能当储量、矿群不是单矿、官方单位冲突、5.11kt差异和未来逐矿收入缺口。没有逐矿预测证据是此搜索语料边界，不是全球资料不存在。',A+'findings.md:379-425; '+A+'findings.md:519-564','按矿山经济可售量、净价和并表抵销重构；来源错配先隔离而非追求模型细化。')
c(A+'progress.md',1,126,'supported_scoped','停止重试、诚实草案和前后hash范围','三次source准备失败类型不同，最后零下载reuse与安全失败同时成立；renderer故障、其他agent并发变更均披露。不能从局部四文件同步外推完整安装同步。',A+'RUN_MANIFEST.md; '+CHK,'保存分阶段结果；当前已修故障另验，不把8/12故障自动继承为今天。')
c(A+'audit_report.md',1,268,'supported_scoped','隔离审计报告的有限有效性','全篇已读；65参数/32claim/4sources/4分部及三情景算术独立匹配。报告没有把8.15%CAGR和42分当准确率；原生完整流程失败仍成立。17ba renderer等历史缺陷须追后继修复而非重复归为当前。',CHK+'; '+RF,'优先真正来源准备和运营桥，不再靠isolated手动fallback认证产品可用。')
c(A+'dropbox_broker_report_audit.md',1,46,'supported_scoped','七PDF物理可读与语义不可用','hash检查/页码/不同预测终期支持有限结论；相似公司对比表可能错摘、flatten表格错配和published/artifact/span为空需分别治理。可读不等于当前有合格handle。',A+'findings.md:552-557','外部唯一来源端到端取证；抽表保留单元格、实体与单位。')
c(A+'findings.md',1,62,'historical_only','研究范围、安装与本地数据基线','基年/产量/内部抵销和必需沟通清单属于当时取数及原合同；四关键文件一致不等于完整docs/templates/session同步。',A+'RUN_MANIFEST.md; '+RF,'将完整部署manifest与已加载runtime单列。')
c(A+'findings.md',63,172,'historical_only','早期源门、raw/派生及目录诊断','未签名capture与下游默认拒绝、弱线索、CodeGraph/进程指标等是当时范围。目录存在不能替代source hash/schema/producer；静态可达不证明运行完成。当前host_signed能力探针另由本轮发现验证。',RF+'; '+A+'TRUST_BOUNDARY.md','把捕获、资格、审核、artifact选择与实际使用分离取证。')
c(A+'findings.md',173,277,'historical_only','物理raw、sidecar、旧派生及worker竞争','当前readonly改进及R4 sidecar分类有后继，不将旧初始化写DB或sidecar误判概括为永远未修。既有文件、四层绑定和运行状态迁移仍解释了旧green无法推出用户成功。',RF+'; '+B+'independent/data_pipeline_review.md','新文档默认路径与旧文档迁移两条都验；不以一个迁移canary代日常生产。')
c(A+'findings.md',278,395,'supported_scoped','矿业经营桥和旧绿canary的边界','生产worker竞争下可锁死而静态canary可绿；资源不等储量、量价归属不同，别用产量指导冒充公司收入。数字取数及缺口只适用当时材料。',A+'mine_coverage_matrix.md; '+A+'audit_report.md','真实运行矩阵带worker实际状态和竞争；运营桥以外销并表口径为核心。')
c(A+'findings.md',396,433,'supported_scoped','最新公告、反证及管理沟通覆盖层次','利润不能替营收、交易终止会改变并表、产能有在期权重、负面铜产量与正面锂同时记录。checked入口不代表capture完整，实录和会议公告不能互替。',A+'trace/web_events.md','大额驱动绑定最新事件与反证；全期管理目标不足不手填完成。')
c(A+'findings.md',435,483,'supported_scoped','F68–74原件reuse成功但revenue source失败','当前独立实核这些历史raw仍匹配；第三次handle/envelope/journal支持原件reuse，零parser/LLM只描述本轮事件，不证明旧处理从未发生。review/producer lineage缺口不能用假事件回填。',CHK+'; '+A+'trace/filing_fetch_events.md','只记录可证明的历史来源与真实新处理；failure receipt保留已完成上游阶段。')
c(A+'findings.md',485,497,'historical_only','generator弱测和validate-only写registry历史问题','原观察指出linter与强validator不同、只读命令副作用。当前后继输入generator/publication已有实质修复，不以旧失败冒充当前复现。',RF,'新模板送同一强入口；registry原子性另有本轮scratch反例需修。')
c(A+'findings.md',498,524,'supported_scoped','四direct_growth与逐矿模型适用范围','按四对外收入避免抵销错误，65参数确实足够算术；运营模型占比0、未来fade无源、没有逐矿收入都清楚披露。透明回退仍无样本外准确性证据。',CHK+'; '+A+'outputs/input_v1.json','优先补最大增量驱动经营上界，再决定分矿颗粒度。')
c(A+'findings.md',525,542,'supported_scoped','隔离HTML与错误strategy身份','HTTP200和hash不能证明语义身份；最终排除学校工程页且未注册来源是正确行为。关键词0命中+人工定位不是完整安全证明/平台签名，也未修共享not_reviewed。',A+'trace/source_review.md','entity/role/title/正文校验、真实review回执与失败恢复。')
c(A+'findings.md',544,577,'supported_scoped','draft算术与renderer失配的历史局部证据','独立从输入逐步乘法得到所有15个总额差0，原结果file hash吻合；支持当时draft而非formal。renderer旧故障需看当前后继；42分、三情景排序和六质量门不证明预测可采用。',CHK+'; '+RF,'评价计算、来源、研究充分性、准确性和发布分别给结论。')
c(A+'findings.md',579,589,'supported_scoped','并发改动及零写证据范围','长时段registry变动不能归因本次调用，紧邻before/after相同的记录支持限定运行零写；本轮不冒称重建了旧时进程环境。',CHK,'保存操作事件与前后原子证据，避免全局hash差异错误归因。')
c(A+'outputs/draft_report.md',1,115,'supported_scoped','低置信条件预测与显式局限','总额/贡献/概率加权为算术，20/60/20没有概率校准；±第一年增长率敏感性不覆盖所有期或联合变量。研究覆盖门可在缺口明列下通过，其含义是合规披露而非研究充分。',CHK,'新验收增经营约束、联合情景和独立负面参考，不以置信分数替准确性。')
c(A+'sources/README.md',1,5,'supported_scoped','隔离快照不是共享摄取','来源路径/职责界定合理；无canonical ingest声明，不能算company-wiki功能成功。',A+'trace/web_events.md','后续回到正式入口验证注册与再复用。')
c(A+'trace/filing_fetch_events.md',1,73,'supported_scoped','三次运行逐阶段证据','未获下载授权且reuse返回内部handle；只读失败/锁竞争/not_reviewed是不同原因。源可见和ready不同，old journal不会冒充本轮下载。',A+'findings.md:449-483; '+CHK,'保留嵌套结构化错误和预算、worker状态、实际调用事件。')
c(A+'trace/source_review.md',1,24,'supported_scoped','自报安全审阅边界','检查记录有具体来源hash及排除项，不能视为密码学签名或共享库已审查；零关键词命中并非安全完备性证明。',A+'TRUST_BOUNDARY.md; '+RF,'提供受支持hash绑定review入口与独立审查，不关闭安全门。')
c(A+'trace/web_events.md',1,59,'supported_scoped','访问/冻结/有效来源分别记录','所列访问和失败不等于落盘；最终只有2个有效HTML，策略页排除。仅浏览器读取的公告未冒充snapshot，这限制了参数证据而非可跳过它。',A+'findings.md:525-542','保留工具原日志和内容身份；缺失capture不得凭URL合成。')
c(B+'README.md',1,17,'supported_scoped','真实运行完成审计而非三家预测','13次命令hash独立重验全部匹配；0/3正式预测表述正确，357基线有起点限制，不认证更早工作树。',CHK+'; '+B+'audit_integrity_check.json','修通实际入口后再做模型/发布，不能把本次审计完成当业务完成。')
c(B+'independent/acceptance_checklist.md',1,53,'supported_scoped','事前经济和跨根审查准则','每条方法/拒绝替代已读；正确区分原件、派生、研究、预测与精度。DOC/OBS项目是基线待实测，不能从清单存在推为执行覆盖。',B+'independent/review.md','将清单每维挂实际run/sample/结论，不只打勾。')
c(B+'independent/data_pipeline_review.md',1,95,'supported_scoped','跨目录部分通过与新文档注册失败','本轮30文件再核旧hash一致（20location+8artifact+2new raw）；13原日志全匹配。生产adapter缺失及错误吞没见本轮其他代码审查。148记录只是三公司限定，不证明全库无external-only。',CHK+'; reviews/wiki/readonly_diagnostics.json; reviews/wiki/historical_git_readonly.json; '+RF,'保留已有raw恢复注册；未知计数不写0；配置/flag/实际入口组合验收。')
c(B+'independent/review.md',1,90,'supported_scoped','独立审查的经济与工程结论边界','全文没有把草案当正式预测；EV71.55%、Azure67.64%是增量集中度而非预测置信度；矿业67.31%是假设错误做法影响，并非本轮错误结果。原独立算术程序支持九个小米总额和微软假设乘积，但不能验证假设。',B+'independent/recompute_research.py; '+B+'independent/independent_research_recalculation.json; '+CHK,'经营反证优先最大贡献业务；正式之后仍需冻结样本外评估。')
c(B+'AUDIT_REPORT.md',1,114,'supported_scoped','0/3根因、通过范围及当前局限','通过raw保存/reuse不等于source/forecast可用，scan completed_with_errors files_seen0无法被exact identity错误替代。403是provider环境事实，错误语义丢失才是接口缺陷；结束后desired_state仍paused，保留用户原暂停意图。captured≤asof跨日未正式复现，保留待专测。',CHK+'; '+B+'independent/data_pipeline_review.md; '+RF,'用同原件恢复和同请求二次reuse；来源与研究完成之后才发布。')
c(B+'ZIJIN/research.md',1,65,'supported_scoped','资源周期/新矿并存及基年口径','完整审阅会计量纲、产销量、内部抵销、资源/储量、金属价格不同向、管理产量非收入等方法。基年闭合可复核，未产出未来表不能宣称资源模型已跑。',B+'independent/review.md:54-62; '+CHK,'先同口径历史运营桥/H1/范围/价格，再逐矿期权或爬坡。')
c(B+'XIAOMI/research.md',1,108,'supported_scoped','量价/实际桥/会计混合/信息空白','H1锁定、舍入披露不伪精确、MAU非付费用户、补贴不得重复扣、研发不是收入目标合理；透明direct_growth不代表高质量假设。生成模板成功只支持模板产出，仍未正式输入。',B+'independent/review.md:30-40','车型供需/产能和净价先补，复核高端化与销量组合；年度模型显式桥H1/H2。')
c(B+'XIAOMI/research_scenarios_NOT_FORMAL.md',1,43,'supported_scoped','九年度研究算术及非正式标识','低基高三情景有算术证据，其他/AI残差不能冒充成熟收入机制；范围不是概率区间。此处不要求为形式通过编造数据。',B+'independent/recompute_research.py','补EV产能/订单取消/车型和IoT季节性；正式结果另验。')
c(B+'MSFT/research.md',1,60,'supported_scoped','财年/最新重述/迁移与收入边界','正确撤回旧三分部模板、八线闭合、同source不等独立来源、RPO不能直接摊收入。72判断参数并无充分运营上界；模板缺父目录为可用性，不等经济模型失真。',B+'independent/review.md:42-52','容量需求净价、迁移蚕食、季度→全年、GAAP/CC/exTAC桥逐项补齐。')
c(B+'MSFT/scenario_draft.md',1,26,'supported_scoped','条件增速路径与终期风险','明确待验证与非概率；八线多率仍direct_growth，不能因拆分数多认证因果。历史闭合与终期乘积正确只支持算术。',B+'independent/recompute_research.py','最大Azure终期影响及所有年度衰减率需要经营/参考类约束。')
c(B+'MSFT/gates_and_target_ledger.draft.md',1,59,'supported_scoped','九维/六沟通/模糊指引转换和真实缺口','逐条审完；季度和全年、CC/GAAP、highteens精度区分正确。网页访问并非capture，AWS失败参考不能无调整硬套；validate-only需当前副作用门正确再用。',RF+'; '+B+'independent/review.md','保留定性原话与转换理由、信息时间；不倒填访问日期或以空模板验证冒充实跑。')
rows=[]; cov=[]
for f in files:
 p=R/f; raw=p.read_bytes(); ls=raw.decode('utf-8-sig').splitlines(); h=hashlib.sha256(raw).hexdigest(); head=''
 for n,line in enumerate(ls,1):
  if not line.strip():continue
  if re.match(r'^#{1,6}\s',line):head=line
  case=[z for z in C if z['file']==f and z['start']<=n<=z['end']][-1]
  rows.append(dict(occurrence_id=f'CCL-{len(rows)+1:05}',source_file=str(p),relative=f,line_start=n,line_end=n,file_sha256=h,original_text=line,heading=head,manual_case_id=case['case_id'],verdict=case['verdict'],assessment_target=case['target'],rationale=case['rationale'],evidence=case['evidence'],remedy=case['remedy'],reviewer='root',read_status='fully_read',review_scope='Engineering and research methodology; historical corporate facts not newly fetched/certified'))
 cov.append(dict(file=f,source_file=str(p),sha256=h,lines=len(ls),nonblank_occurrences=sum(bool(s.strip()) for s in ls),read_status='fully_read',semantic_cases=[z['case_id'] for z in C if z['file']==f]))
(H/'manual_cases.json').write_text(json.dumps(C,ensure_ascii=False,indent=2),encoding='utf-8')
(H/'item_ledger.jsonl').write_text(''.join(json.dumps(z,ensure_ascii=False)+'\n' for z in rows),encoding='utf-8')
summary=dict(files=len(cov),original_lines=sum(z['lines'] for z in cov),occurrences=len(rows),manual_cases=len(C),verdict_occurrences=dict(collections.Counter(z['verdict'] for z in rows)),boundary='All Markdown text reviewed; occurrences are not independent test pass counts. Historical company fact assertions are not reforecasted.')
(H/'coverage.json').write_text(json.dumps(dict(files=cov,summary=summary),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary))
