"""Materialize the lead reviewer's full-text, section-specific adjudications.

The manual cases below were written after reading all 45 documents. Extraction
does not infer a PASS from checkboxes, old verdicts, tests counts, or keywords.
Every source block is retained, including navigation and historical limitations.
The verdict assesses the historical document claim; a referenced requirement's
current implementation verdict belongs to the independent project ledger.
"""
from pathlib import Path
import collections
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1]
P = 'docs/plans/painpoint-outcome-audit-2026-09-05/'
S = 'docs/plans/planning-sync-2026-09-04/'
CASES = []

def case(folder, filename, start, end, verdict, target, rationale, evidence, action):
    CASES.append(dict(case_id=f'CH-{len(CASES)+1:03}', relative=folder+filename,
                      start=start, end=end, verdict=verdict, assessment_target=target,
                      rationale=rationale, evidence=evidence, recommendation=action))

# Whole-document dispositions: these preserve historical scope, not product PASS.
# Narrower cases below override the pertinent paragraphs and table rows.
base = [
('README.md','historical_only','旧审计摘要与阅读入口','通读正文后确认其任务是审计与计划交付；明确未做生产E2E。117 accepted与原目标闭合被分开。9/9顶栏残留错误另列。','unit-ledger.md; current-delta-2026-09-09.md; 本轮structure_checks.json','保留旧摘要，现状以本次项目逐项账本及已日期化的差异为准。'),
('assurance-audit.md','historical_only','9/5–6完成保证审计断言','原要求对照确有价值；不能因历史CA/ZR全部accepted就否定反证，也不能把9/5调度/CI缺陷自动说成9/19仍存在。当前独立复查逐CA/ZR登记于revenue账本。','reviews/revenue/item_ledger.jsonl; current_recheck.json','分离原要求、后来缩水的卡、当前生产消费者与当前实际运行。'),
('assurance-independent-review.md','supported_scoped','独立审查的证据层级约束','本报告正确收窄三种过强表述：machine_valid不等于生产放行、孤立select不等于完整receipt重放、CA206测试oracle不等于生产自然窗口伪造。其收窄对本次结论仍适用。','reviews/revenue/当前CA206纯函数探针及CA302测试审查','保留这些限定；不能用局部分类器问题宣称已经发生生产越权发布。'),
('current-delta-2026-09-07.md','historical_only','带日期的并发代码/运行观察','观察只属于9/7。原35文件快照本轮复算24相同、11不同；差异不能归咎为历史篡改，也不能证明旧缺陷全部已修。','current_recheck.json; 原35文件snapshot','新报告按受影响符号重查，不复制旧HEAD的状态。'),
('current-delta-2026-09-09.md','historical_only','v5冻结、FC705观察与R9清理状态','这里是日期化观察与随后更正：v5 PLAN_ONLY、自然窗口预计值不是观测值、artifact_backfill零读者说法已撤销。','reviews/wiki/readonly_diagnostics.json; 本文件9/10–11更正','不得执行撤销的3a；自然窗口取实际事件而非预计日期。'),
('document-consistency-review.md','supported_scoped','文档同步方法和冻结范围','复核46唯一冻结输入hash仍相同；区分活动状态覆盖与不可变历史正确。旧251/150链接计数只证明当时链接，不证明现在产品链路。','anchor_checks.json; structure_checks.json','保留原签署，不修改旧输入hash使旧检查器适应新状态。'),
('execution-control-plane.md','superseded','R3控制面编排与领域验收要求','R4明确替代旧95门共同编排；原关于缺tier、skip、当前组合、真实自然运行的验收要求仍保留。通读未发现把计划步骤当已实施结果的合法依据。','simplified-execution-plan.md:13–37; r4-transition.md','只继承具体反例与结果要求，不重新搭建95门才能修局部故障。'),
('execution-data-plane.md','superseded','R3数据面编排与操作细则','70步数据细则覆盖稳定归档、policy/eligible、期间修订、跨进程需求、外发门、真实性能及broker语义。R4取代包间依赖，原领域约束不是已运行证据。','r4-transition.md; 本轮gap_plan反例; reviews/wiki_legacy','按真实请求路径收敛；逐对象验收保留，不把每个辅助动作再建审批平台。'),
('execution-handbook.md','superseded','旧R3接班与95门手册','旧手册有明确R4覆盖头。其命令/副作用/独立oracle要求仍有用，旧G0–G5全局流程已非活动编排。','simplified-execution-plan.md; r4-transition.md','未来使用单次结果包；命令、输入、原始rc、业务结果和未做范围完整记录。'),
('execution-independent-review.md','historical_only','R3计划可执行性复核','复核关闭的是WP06自等与WP09依赖歧义，且明示accepted_for_planning。正文的SHA绑定当时文档，不覆盖后来R4与新的源码。','execution-model-plane.md; execution-data-plane.md; r4-transition.md','保持设计通过与实现/部署/运行通过分栏，不把此review复用为代码验收。'),
('execution-model-plane.md','superseded','R3模型细则与三公司合同','48个模型/公司链步骤提供单位、矿业合并、generator、事务发布和真实origin回测的具体要求；R4仅取消旧跨包依赖。这些要求无法由新增模型公式单测全部代替。','reviews/revenue/31模型复跑与单位/发布/置信度审查; 9/18真实公司审计','保留独立来源和Decimal oracle、按时间回测、参数到输出消费；扩展行业不得绕过真实资料链。'),
('filing-audit.md','historical_only','9/5–6 filing与跨root旧审计','本轮filing代理独立复查全部原planning条款并运行隔离套件；旧报告不是当前provider E2E。deadline和失败计数等有当前反例，多根配置的新实场阻断另列。','reviews/filing/review.md; current_recheck.json','每条通过须对应具体分支、所用配置、市场及副作用边界。'),
('findings.md','historical_only','审计发现时序汇总','有明确9/10撤销过窄零读者结论，且指出文档冻结不等于实现。相同F008/F009重复编号会令仅按ID引用歧义；引用时必须加标题/日期/行。','本文件9–21、73–79; current_recheck.json; reviews/revenue','新台账使用稳定新ID并保留原行号，不能改写历史消除时间差。'),
('gp-audit.md','historical_only','GP001–010历史结果对照','10项表是9/6时点；9/8之后CI、daily、sections有后继变化。不能据它宣称参数错误现在还在，也不能用一个自然观察窗口覆盖真实公司链。','reviews/revenue/GP及非checkbox审查; current_recheck.json','以最新实际配置和运行证据重验适用项目，退出旧工具不作为重新实施任务。'),
('historical-projects-audit.md','historical_only','历史空间、章节、portfolio、v5和研究writer项目','H02/H03的局部成果和未闭链应并存；H05明确不得恢复已退出的研究型writer。原规模49GB/902秒是历史观测，不是本轮性能测量。','reviews/wiki_legacy; reviews/wiki; 本轮prune静态复读','不重启退休路线，按源文档可用性和实际consumer闭环验收。'),
('legacy-inheritance.md','supported_scoped','71FC与10waves的历史继承映射','完整读每一行；映射本身声明不继承accepted。缩写R1等丢后继的风险要求以原文展开；它不能直接授予successor当前产品资格。','reviews/revenue/item_ledger.jsonl: FC/WU原文与后继; 本文件R0–R9原文','保留全部原ID与每个原条款，不用后继总绿关闭前代未执行要求。'),
('progress.md','historical_only','多阶段实施/设计/审计进度','全文区分A阶段设计多次rejected、基线测试、B设计审查、文档完成及产品未改。记录生产-shm被只读测试打开的更正，说明只读SQL不等于文件零写。测试数仍只支持记录中的套件。','reviews/revenue/assurance runs A/B; 本文件9/11–12条目','对生产边界包含主库/WAL/SHM；不将设计rejected解释成产品新故障，不把设计更正当已实施。'),
('r4-independent-review.md','supported_scoped','R4设计delta复核','本轮回读修订正文：VR与AR分层、C.local不含真实worker、broker主责C、D.SAFE不授worker通行已明确。原两核心文档hash仍匹配旧复核。','structure_checks.json; simplified-execution-plan.md:19–37; simplified-test-matrix.md:84–100','保留分层，不额外要求真实AR先通过才能做隔离VR。'),
('r4-remediation-detail-review.md','supported_scoped','117映射和104编号项的文档复核','本轮独立计数104编号=88实施+16映射，117原ID/原痛点/原判定一一相同，36测试组、44步骤（38表格+6正文）成立。只支持结构与已修引用，不证明117能力实现。','structure_checks.json','对应当前代码的实施前设计仍须精确化，不再以计数PASS关闭业务。'),
('r4-remediation-steps.md','supported_scoped','具体修复动作与未执行验收合同','通读104项；H01分硬禁用和可信恢复、W02–10各实际consumer、FC903保留原字节、U117逐子条款、CL/AC真实条件均合理。这里是工作说明，没有完成运行结果。','structure_checks.json; current_recheck.json; reviews/filing; reviews/revenue','作为领域验收来源，新增当前scanner配置故障和行业模型验收；只推进本轮目标所需动作。'),
('r4-transition.md','supported_scoped','旧15WP到R4的迁移与约束保留','逐行覆盖WP00–14、7项减法和原始条款继承，强调减少流程不减少目标。当前应避免又造一套等价复杂全局gate平台。','simplified-execution-plan.md; r4-remediation-steps.md','新实施文档映射到结果链与旧条款，不能让旧框架互相等待。'),
('r4-unit-remediation-map.md','supported_scoped','117目标的路线表而非完成表','本轮独立join证实117行原ID、原痛点、旧判定无丢失，当前结果全待取证。每行路由不是完整子条款验收，也没有证明实现。','structure_checks.json; reviews/revenue/item_ledger.jsonl','读取原卡细则后判定；对已变化/退役项目按新证据处理而不照旧重做。'),
('remediation-plan-independent-review.md','supported_scoped','R1到R2设计审查','六类意见及R2更正逐项可对上正文：能力/效果分离、真实动作并集、授权子类、稳定snapshot、遗漏RED、外部费用不可回滚。原审查明确不签产品。','remediation-plan.md:233–323; r4-transition.md','保留领域约束，旧R2编排被R4替代；不得把accepted_for_planning解作产品修复。'),
('remediation-plan.md','superseded','R2/R3总整改编排','15WP及后加门级依赖在当时针对真实缺口；R4后来取代95门。多轮计划批准和数百结构检查没有自动执行任何WP中的真实链路。','r4-transition.md; simplified-execution-plan.md; structure_checks.json','未来从已证实故障的小结果闭环实施，保留原需求但不再堆叠统一审批图。'),
('retention-independent-review.md','supported_scoped','归档/回收静态可达性复核','主审重读当前prune和worker调用，目录年龄与DELETE集合脱钩仍存在，worker周期有apply=True；未执行任何删除，不能声称已造成生产丢失。归档覆盖/恢复风险由另一代理独立复读。','current_recheck.py说明; company-wiki/scripts/prune_retired_evidence.py; worker.py:770–815; reviews/wiki_legacy','恢复自动worker前关闭或修好精确归档资格；原始PDF与派生EvidenceSpan风险区别报告。'),
('revenue-audit.md','historical_only','旧模型与真实链路反证','9/5版本的单位/helper/发布/generator/置信度问题需按当前实际调用边界核对。31模型改进可修主引擎部分范围，不自动修孤立helper，也不证明预测准确性。','reviews/revenue/item_ledger.jsonl; reviews/revenue/模型逐项审查和97测试+216subtests','当前原条款审查优先；不要从无调用的旧helper错误推出所有31模型输出错误。'),
('simplified-execution-plan.md','supported_scoped','R4设计与阶段边界','全文复核44步骤，A/B本地读取不等D自然期，M独立；普通query不下载/pause，source身份不由path决定，实际写/外发各边界。适合作为约束，不是已实现声明。','structure_checks.json; 本轮真实3公司结果及config不匹配','本轮实施计划以最短真实成果链组织，并保留这些必要约束。'),
('simplified-test-matrix.md','supported_scoped','36组真实验收合同','36组定义与后段VR/AR路由明确。L04第五根、P06三市场首次再复用、M07真实不同公司等直接对应本轮未覆盖/失败点；不能用合成pages或内存队列冒充真实加工。','structure_checks.json; 9/18真实公司AUDIT_REPORT; reviews/wiki/第五root诊断','为每个适用case保存独立期望与实际证据，required未执行/skip单列。'),
('task_plan.md','historical_only','旧审计各Phase完成状态','Phase完成标记限定于审计和规划。其Next Step与后续A/B记录并非产品完成；原审计未生产重跑已明示。当前新审计独立覆盖更大范围。','本文件各阶段限定; reviews/revenue/A/B审查; scope_manifest.json','保留原三件套，新的规划使用本目录三件套，不覆盖旧active状态。'),
('unit-ledger.md','supported_scoped','旧117审计索引的范围与覆盖','本轮全行读取并独立join，25CA+92ZR确为117。旧判定是9/5–6，53contradicted不是53个当前模块坏，更不是本轮复跑117产品。','structure_checks.json; reviews/revenue/item_ledger.jsonl','原条款当前状态以本轮原单位审查为准，索引行只能定位旧证据。'),
('upstream-asset-audit.md','supported_scoped','上游资产事实与下游helper责任界限','上游raw/table→assertion/export不能由revenue同号纯算术测试替代；“名称检索无结果”本身也不能证明没有实现。这一证据纪律正确。','reviews/revenue/ZR601–604审查; reviews/wiki','验收每条生产边与实际消费，不按同名测试推定跨仓能力已具备。'),
('wiki-audit.md','historical_only','9/5–6 worker/加工/安全旧断言','旧报告明确未打开生产库/未重跑49GB，W02停机是当时事实。当前normalizer/summarizer/section/resolver/service已出现snapshot差异，必须按当前代码重查旧问题。','current_recheck.json; reviews/wiki; reviews/wiki_legacy; reviews/revenue/source preparation','保留已证实局部改进；sourceprep阻断与queue需求丢失需实际跨进程闭环。'),
]
for filename, verdict, target, rationale, evidence, action in base:
    case(P, filename, 1, 100000, verdict, target, rationale, evidence, action)

sync = [
('company-root-audit.md','根历史文档全文阅读与外部状态覆盖','原报告的8600行读取是一项历史审计；CW2.24的618仅有52+160范围证据，后续candidate/rejected应覆盖早先完成标题。当前根项目逐条重审由wiki_legacy执行。','reviews/wiki_legacy; 原根task_plan/findings/progress','不得按段落出现顺序或ALLDONE标题选最乐观状态。'),
('filing-fetch-audit.md','filing历史文档同步与receipt绑定','原文本、模式/exit说明确有过时；FC903绑定不匹配本轮仍独立确认，三安装副本已一致。旧hook问题有后继，不视作现状。','reviews/filing/review.md; reviews/filing/receipt_ledger.jsonl','保留旧receipt，追加可绑定的新验收；不把配置问题归为filing未部署。'),
('final-independent-review.md','预应用与文档同步PASS','PASS明确针对文档链接/冻结范围；后面仍列应用后待办，另有post-apply最终复核。不能把它既误解为产品PASS，也不能把旧待办说成一直未做。','revenue-post-apply-review.md; anchor_checks.json','按被签文件/当时hash/具体阶段解释PASS。'),
('findings.md','9/4–5同步发现','root完成与v5设计状态、GP尾项等均是当时文档不一致发现；原文有明确日期，不是9/19运行判断。','reviews/revenue; reviews/wiki; current_recheck.json','采用新证据覆盖当前状态，保留原发现时序。'),
('patch-review.md','补丁预应用审查','审查冻结字节、链接与侧页建议，不表示补丁当时已应用，更不是worker恢复许可。后续应用结果单独记载。','revenue-post-apply-review.md; anchor_checks.json','只保留其文档范围证据，不能跨阶段继承成功。'),
('progress.md','文档同步进度','从准备到全文覆盖到同步的日志能解释多次PASS的对象。无真实provider或收入预测输出证据。','同目录final-independent-review与post-apply-review','将同步完成与用户业务完成分开列。'),
('revenue-datalake-adr.md','五份旧ADR规范与实施资格','五份ADR冻结可证明合同未改；WU201缺receipt、202–205pending不因冻结变accepted。职责约束本身与当前源事实/下游分析分工一致。','reviews/revenue/WU201–205; anchor_checks.json','继承原规范，实施能力另验。'),
('revenue-forecast-audit.md','9/4–5 RF文档全读与GP线索','全读范围与93canonical定义有明确边界；排除210receipt当时可理解但不足覆盖本次每条要求。GP006/008后继改变，旧错误不直接搬成现状。','reviews/revenue; current_recheck.json; scope_manifest.json','本轮扩大到receipt/context/snapshots；各条现状用新证据。'),
('revenue-post-apply-review.md','六回链应用前后文档复核','先发现六链接缺失后有独立最终PASS；不能停在中间FAIL。GP自然时间/代码状态当时被限定，而不是产品全量验收。','本文件120–146; anchor_checks.json; current_recheck.json','保留先失败后修正的完整链，产品层不继承文档PASS。'),
('revenue-remediation-tail.md','remediation末段与隐藏副本覆盖','尾段原卡的约束仍需保留，阅读和hash仅证明覆盖。当前262原单位和每处出现的追溯另由RF代理登记。','reviews/revenue/item_ledger.jsonl; snapshot_mapping.json','不把剩余行读完等同目标通过。'),
('revenue-scope-inventory.md','93canonical文件范围声明','93/25163定义有排除范围，13不可读tmp明确UNKNOWN。历史范围不是本次769范围；本轮亦保留访问限制而不宣称消失文件已读。','scope_manifest.json; inventory/all_documents.json; snapshot_mapping.json','将枚举、全文、语义判定、动态运行分别计数。'),
('task_plan.md','旧同步任务四Phase完成','completed对应inventory/evidence/docs-sync/verification的文档任务；不是原三仓产品交付。原任务正确要求保留冻结字节。','anchor_checks.json; 同目录post-apply-review','新计划勿把审计完成自动转为实施完成。'),
('v5-baseline-audit.md','v5导入覆盖与路由审计','原基线全文覆盖13+10MD有限范围；9/4 pending与9/9 freeze是时序变化。本轮51冻结hash匹配仍不能证明315功能用例或48导入件实现。','reviews/wiki/readonly_diagnostics.json; reviews/wiki/item_ledger.jsonl','继续按每个合同语义审查，不以9188结构检查当运行测试。'),
]
for filename, target, rationale, evidence, action in sync:
    case(S, filename, 1, 100000, 'historical_only', target, rationale, evidence, action)

# Specific present-day evidence and corrections after the full reading.
case(P,'README.md',3,3,'contradicted','顶栏仍称artifact_backfill零生产读者','同目录findings与current-delta已在9/10明确撤回并撤销3a，README顶栏未同步。属于摘要陈旧，不能据此删除。','findings.md:9–15; current-delta-2026-09-09.md:29–47','新入口明确3a撤销，保留旧字节。')
case(P,'assurance-audit.md',7,12,'supported_scoped','验收范围收缩及accepted自证明','独立原卡/测试审查仍确认CA302真实三公司被同一_zijin_document和自比较代替，CA206纯测试calculator并非真实自然周期；当前31局部测试通过并不冲突。','reviews/revenue/item_ledger.jsonl:CA302/CA206/CA301/CA305','恢复原验收对象，别给旧receipt重新签字掩盖原范围。')
case(P,'assurance-audit.md',13,20,'supported_scoped','machine_valid分类不等于实际生产放行','本段及其独立复核需合读；当前独立审查不把schema校验视为产品release整体绕过的证据。','assurance-independent-review.md:22–57; reviews/revenue','未来对真正state transition/CI消费者做负例，不只测selector。')
case(P,'filing-audit.md',67,81,'supported_scoped','accession词序与候选hash问题','主审使用当前gap_plan.py纯函数重放4组反例：较新低ID漏报、旧高ID误报、缺period不明确、URL/date改变hash不变。无网络或DB。','current_recheck.json','比较明确期间/修订关系及发布时间，未知关系ambiguous，授权候选内容改变应使绑定失效。')
case(P,'filing-audit.md',90,102,'supported_scoped','deadline与失败计数','独立filing代理当前隔离反例仍见10秒预算9秒busy加5秒sleep走到14秒；过期scope仍最少10秒。失败后下载事实丢失亦有字段链证据。','reviews/filing/review.md; reviews/filing/probes','剩余时间传播所有层，阶段事实只追加不因末端错误清零。')
case(P,'historical-projects-audit.md',5,29,'supported_scoped','自动prune资格与归档集合脱钩','当前静态源码仍按旧日期目录判due，DELETE范围为全部retired，worker有apply=True入口；本轮没有删除实验、不能断言生产误删已发生。','company-wiki/scripts/prune_retired_evidence.py; company-wiki/src/company_wiki/source_catalog/worker.py:770–815; reviews/wiki_legacy','恢复后台前使删除不可达或以稳定归档的精确PK/hash集合限定。')
case(P,'findings.md',9,15,'supported_scoped','artifact_backfill删除前提已撤销','同一段保留初判又明确更正，不能只抽取旧零调用者句。撤销3a和保护CLI工具的处置合理。','current-delta-2026-09-09.md; reviews/revenue/R9后继','审调用者包括CLI/运维入口、合同保护与测试，不仅import。')
case(P,'findings.md',17,21,'supported_scoped','v5完成只覆盖冻结/计划','本轮重新核对51项hash与size全匹配；v5代理检查115DAG/315ID合法，但另发现正文关系矛盾，证明结构验证不等于完整语义或实现。','reviews/wiki/readonly_diagnostics.json; reviews/wiki/item_ledger.jsonl','报告保留局部通过，语义和部署单独验收。')
case(P,'findings.md',61,64,'supported_scoped','原任务缩成机制测试','CA302与CA206当前独立代码/纯探针支持；CA305accepted再自证无真实结果不能关闭原要求。','reviews/revenue/item_ledger.jsonl; CA302当前测试','最终验收者从原始目标和独立真实期望出发。')
case(P,'findings.md',69,72,'supported_scoped','回收风险仍须阻断','当前静态可达性复核支持风险，paused只控制当前执行而非修好代码；不推断已造成删除。','reviews/wiki_legacy; 本轮prune源码复读','部署任何worker前明确回收资格，不先恢复再观察。')
case(P,'document-consistency-review.md',26,33,'supported_scoped','46唯一冻结输入完整性','本轮独立复算47绑定对应46唯一文件，全hash相同。该结果不继承CA306的自比较测试，也不证明原产品目标完成。','anchor_checks.json','保留独立hash检查，最终业务另验。')
case(P,'r4-unit-remediation-map.md',168,171,'supported_scoped','3a正式撤销后的R9范围','撤销的是具体删除方案，不等于恢复其他retired研究writer。其余3b/3c仍须替代和回退证据。','reviews/revenue/R9; findings.md:9–15','不将这条历史计划当自动删除授权。')
case(S,'revenue-post-apply-review.md',6,17,'supported_scoped','最终PASS替代中间链接FAIL','全文见初次缺链接后120–146复核关闭，最终PASS范围是文档补丁。以时间顺序解释不矛盾。','本文件120–146; anchor_checks.json','中间FAIL保留为历史，不误报为现在未修。')
case(S,'revenue-post-apply-review.md',48,67,'historical_only','GP代码/窗口旧观测','本轮old35快照显示daily/weekly/quality/ledger已变；原blocked_code状态不能未经重查沿用。','current_recheck.json; reviews/revenue','当前有效性取新配置和实际事件，不能只等旧预计日期。')
case(S,'v5-baseline-audit.md',27,85,'historical_only','旧pending与导入路由','9/4未冻结状态后来被9/9正式51项冻结覆盖，本轮51文件一致。文档被后继完成不说明worker实现已部署。','reviews/wiki/readonly_diagnostics.json; reviews/wiki/item_ledger.jsonl','分别报告文档freeze与运行资格。')

blocks = json.loads((HERE/'source_blocks.json').read_text(encoding='utf-8'))
files = json.loads((HERE/'files.json').read_text(encoding='utf-8'))
assert {x['relative'] for x in CASES} == {x['relative'] for x in blocks}
out=[]
for i, block in enumerate(blocks,1):
    matches=[c for c in CASES if c['relative']==block['relative'] and c['start']<=block['line_start']<=c['end']]
    assert matches, block
    c=matches[-1]
    original=block['original_text']
    units=sorted(set(re.findall(r'\b(?:CA|ZR|FC|WU)-\d+(?:\.\d+)?\b',original)))
    row={**block,'item_id':f'CH-B{i:04}', 'review_status':'reviewed',
         'case_id':c['case_id'],'verdict':c['verdict'],
         'assessment_target':c['assessment_target'],'rationale':c['rationale'],
         'independent_evidence':c['evidence'],'recommendation':c['recommendation'],
         'original_unit_references':units,
         'current_requirement_verdict_source':'../revenue/item_ledger.jsonl' if units else None,
         'scope_limit':'审查原句的目标、证据资格、后继与现状边界；本行不代表重新运行产品、外网或自然时间试验。'}
    out.append(row)
(HERE/'manual_cases.json').write_text(json.dumps(CASES,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'item_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in out),encoding='utf-8')
coverage=[]
for f in files:
    rr=f['path'].replace('\\','/')
    selected=[x for x in out if x['relative']==rr]
    coverage.append({'source_file':f['absolute_path'],'sha256':f['sha256'],'lines':f['lines'],
                     'read_ranges':[[1,f['lines']]],'read_status':'full_text_read',
                     'reviewed_source_blocks':len(selected),'pending_blocks':0,
                     'case_ids':sorted({x['case_id'] for x in selected}),
                     'coverage_kind':'manual file/section semantic decisions with every original block retained; no automatic product PASS'})
(HERE/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(files),'manual_decisions':len(CASES),'source_blocks':len(out),
                  'verdict_counts':dict(collections.Counter(x['verdict'] for x in out)),
                  'runtime_pass_inferred':False},ensure_ascii=False))
