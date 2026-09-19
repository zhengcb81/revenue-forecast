"""Individually authored review of frozen legacy obligations, not status inheritance."""
from pathlib import Path
import json,re,csv,hashlib
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
FC=r'''
000|历史三HEAD/upstream/dirty/索引基线只对旧日期有效；本轮索引存在遗漏，不能继承健康。
001|旧生产统计和fingerprint是时间点证据；09-18真实源准备结果已经不同，需当前同口径分桶。
002|问题到scenario映射完整性是计划资产，不是所有问题关闭；后继CA004保留了71项。
101|ownership/N-1合同可保留；最新R4仍明示更广消费者兼容未全做，旧表不授权跨版本组合。
102|95登记与197后继登记均不等于原子场景执行；需collected node与实际业务oracle，不能以marker覆盖替代。
103|旧结构validator允许exit零文字转述；FC703 r2/r3实例清楚显示原始exit2被记录0，不能从schema通过推断命令全绿。
104|旧current manifest只绑定旧组合；后继CA201吸收卡禁止真正workflow改动，需当前候选三仓扇出实证。
201|CAS/flag非法组合为可保留机制；未重新执行本轮并发snapshot故障，不认证今日生产每入口接线。
202|SQL epoch/cohort条件有旧mutation证据；需现生产reader和RuntimeContext同请求追踪，旗标值本身不足。
203|preview/apply/rollback旧隔离演练有用；本轮未授权操作生产开关，不把旧受测事务当今日已部署。
204|旧16断言最小cohort属于限定T4；不能扩展到所有根或今日财报，需现cohort内容和回滚证据。
205|旧caller>=1架构门不足以排除未索引代码与平行活路径；当前CodeGraph漏符号，需完整入口清单。
301|RootPolicy2.x doctor合同是机制；09-18扫描报告v2 flag配1.x无adapter_id，说明生产配置未满足该能力前提。
302|三adapter具生产调用不意味着每root都路由正确；09-18company_raw v2 scan失败，需逐root运行配置证据。
303|frozen corpus parity只覆盖冻结集；不能证明生产root/版本漂移后的parity，需现存配置与已知bad差异清单。
304|future-root只改config成立范围是已注册同构adapter；不能外推到所有来源或生产1.x loader。
305|两轮shadow旧fingerprint是历史资产；需要当前部署窗口、未解释diff及可运行fallback，不能只检查旧文件。
401|迁移resume/idempotency隔离算法与实际全库迁移不同；缺当前源/产物分桶及资源上界演练。
402|四分桶守恒不等于分桶语义正确；应从真实原文独立核对identity/period/source绑定，不反推猜测。
403|proposal/approval分权机制不认证每一生产数据修复已获批准；按明确ID及immutable evidence逐批复查。
404|coverage ledger输入守恒仅证总数闭合；错误实体/期间可在守恒内，需独立内容oracle。
405|47-source恢复旧演练有价值；不证明当前schema大库恢复，需冻结当前副本/完整性/RTO。
501|旧跨根containment修复范围窄；09-18技能文档仍描述wiki-root内路径，当前RootPolicy和技能边界需统一。
502|FC1203保留evaluate_candidate时明确称未接线政策；旧production trace不能扩展到整个统一admission链。
503|只读候选分桶可为0且应诚实拒绝；不把某次真实root两轮结果当当前所有Dropbox文件可用。
504|历史用户明确放宽排他性，因此4canary注册只证明注册与非排他复用；不再冒称Dropbox-only成功。
505|选companies副本不能证明Dropbox-only；09-18仍无排他合格样本，需保持独立样本缺口。
601|旧company_raw CN/HK/US exact成功不覆盖当前缺文件下载后的scan；09-18后者失败不否定当时exact样本。
602|历史dayu-only2样本曾验收；当前identity/policy/消费者端到端的等价仍需同HEAD证据，不能用wiki resolver单层证明。
603|扫描顺序和稳定ranking局部测试不证明当前所有location hash正确；应绑定本次根集合和选择理由。
604|同请求三根矩阵需要一路到source-preparation；旧resolver级成功与当前filing/path fence一致性分开。
701|normalized-only与legacy caller0为旧目标；当前完整索引不可靠，需枚举所有只读生产入口而非只查符号名。
702|强实体/市场/前导零拒绝是应保留护栏；当前不同名称/证券组合需从用户输入贯穿消费者的负例。
703|r1弱SQL断言被真正独立mutation揭露且r2修好，属于有效审计；r3把raw exit2写0暴露receipt语义缺陷。旧23k性能不等于今日49GB所有请求SLO。
704|journal权威download事件当前source_preparation仍读取；可信包络支持仅限成功返回路径，错误截断/失败无reuse receipt仍缺。
705|r1关闭门永不可达被r2completed-window修好，不报旧bug仍在；r2现场bridge hits6说明观测机制通过并非自然零hit退役窗口通过。
801|旧事务guard有效但reviewer已记request_id分叉会静默download_events0却未阻断；须当前跨进程关联ID负例，不能沿用测试约定代替运行强制。
802|r2死回归测试曾被独立审查拒绝，r3确认收集和精准kill；这是有效修复。后继latest/freshness语义依然必须独立覆盖，09-18失败不是该旧测试放置bug回归。
803|真实三进程spy链证明隔离候选binding/二次零fetch；provider是合成，不能认证当前CN/HK/US服务与生产配置。
804|两线程锁和retry局部有实证；旧CG-C4顺序执行并未形成contended场景。现跨进程/多gap/amendment与structured retry传播需另证。
805|reviewer报告独立复跑CN，registry总结三市场3/3可含实施者证据；分清独立复核覆盖。09-18CN403是新provider状态，HK/US扫描失败是当前部署链。
901|11tests证明分桶工具与shadow apply；其初次真实7718条全部legacy_unbound，说明工具PASS从未代表存量绑定成功。
902|bundle调用边存在仍曾在906-d发现列stamp和derived-root两处生产缺口；这证明fixture与真实producer契约未配对，而非bundle概念不存在。
903|转发合同字段可保留；当前未知版本策略和N-1消费者组合以最新R4/当前实现为准，旧9测试不能无限继承。
904|本轮11tests复跑通过，但mock subprocess/buildrecord，只证selector与最小DAG计划；producer_events是缺失角色列表，不是producer执行。
905|当前not_reviewed确实阻断，符合fail-closed；905-a合同称新review CLI或helper，但独立报告承认writer零生产caller却accepted，解释当前安全门无可用完成路径。
906|真实29v2/15receipt是小cohort；906-a metadata-only曾被906-d补列，canary成果不能覆盖7718遗留或新公司。rollback文档按时间删除行还需精确ID化才能安全执行。
1001|隔离三根fixture可保留，合成bytes/hash确定性不代表真实财报可读性/章节/期间正确。
1002|三进程确实比helper测试强，但所有数据预置review/binding；无法检测生产缺review、1.x配置与v2flag组合。
1003|87covered+14deferred并非95场景全部已执行；应逐条required tier/skip/defer保留，不把required gaps0当全行为通过。
1004|安装态/中文路径/Linux需当前副本与真实依赖版本；未重新运行不能从旧accepted恢复今日平台声明。
1005|八类mutation各一个kill只证明已定义攻击；本轮future same-time soak与reconcile(x,x)不在原攻击集，需独立oracle补齐。
1101|旧manifest驱动CI是资产；后继CA201吸收卡与当前三仓精确候选触发证明不同，不以状态计数担保接线。
1102|旧Daily一次手动执行明确scan error212恶化；9月后自然机制已修，不重复旧未部署结论；当前需最新自然账本验证数据质量达标。
1103|旧Weekly真实3市场有限时间成功与持续调度不同；9/8后skip门/weekly参数修复要保留，当前provider失败需非绿。
1104|dashboard/ledger新鲜度机器门不等于告警投递被确认；需现scheduler报告到release同一工件/ack证据。
1105|旧故障注入证明固定异常类，不能自动证明整个持续soak；后续自然时间修复与尚未满窗口分开判。
1201|有用户批准InterpretationA：注释清理+allowlist棘轮有效，canonical writer/cli/7scanner分支明确延后；不应把该accepted翻译为hardcode清零。
1202|doctor和重复allowlist处置资产须以本次同一policy贯穿为准；当前技能路径描述与实现不一致仍需收敛。
1203|删死符号与extractive注册有细粒度RED/kill证据；明确保留未接线admission供发布，不等于架构全部收敛。
1204|覆盖/type/CC棘轮是防恶化目标，不能声称技术债已下降；需当前baseline差分、排除表和重要分支覆盖。
1205|统一错误与UTF8早期修复不应泛化；现source_preparation非零只取stderr尾800字符丢结构证据，仍存在跨层诊断缺口。
1301|原registry竟有自依赖FC1301链，后继CA101处理DAG；taxonomy枚举仍不确保跨层原始阶段/可重试透传。
1302|增量scan-health历史样本不代表今日健康；09-18scan completed_with_errors且seen0应阻断流程而不是只在深层stderr。
1303|旧框架可留，但latest/RSS代理不等于完整用户请求真实p95/p99；缺现有负载、缓存冷热与锁等待度量。
1304|容量并发恢复均需当前完整链与自然窗口；不把少量固定case推演成持续稳定。
1501|原pending，从未有该旧版本总关闭；后继CA107/108/109 accepted不能补写历史完成。
1502|原独立最终审查pending；CA301后继明确未三干净checkout全重放，原义务尚无等价证据。
1503|原真实三根三市场用户旅程pending；CA302合成fixture缩范围，09-18真实0/3正式结果给出当前差距。
1504|原自然窗口pending；后继CA206纯函数不等价，9月部署修复后仍须原始ledger实际满足窗口，不能用预计日期。
1505|原六目标finalledgerpending；CA305只验状态文件等循环完成证据，不构成六个业务结果oracle。
'''
WU=r'''
101|当前triplet/config/安装态必须重冻，旧基线仅历史；collection与dirty保护不能证明业务成功。
102|后继IsolatedLake实现合成三根资产；与真实生产配置/安全review/缺文档分支的差异需独立矩阵。
103|forbidden-claim应比较原始义务与执行卡；CA206/302缩范围说明仅卡片完整性门未达此目标。
104|golden需标known_bad，现无本轮完整v1全trace对照；不能把旧错误行为固定成正确oracle。
201|职责边界继续有价值；source-preparation目前只有准备与DAG计划，没有自动满足producer调用义务。
202|字段强身份与证据合同需实际producer/consumer配对；906a/d元数据列错位是已知历史反例。
203|exact/latest/revision/授权为不同命题；FC803spy不涵盖今日下载后v2scanner失败。
204|五角色并非均有catalog producer，906b用户批准角色适用性；consumer_analysis须单独消费方生产owner。
205|caller>=1不足完整架构；当前CodeGraph漏磁盘符号，需完整索引覆盖和运行入口双证。
301|RootPolicy全部字段须与生产loader共同验证；09-18adapter_id缺失显示目标schema不能仅在fixture成立。
302|config-only限定已注册同构layout；未知layout必须拒绝，此边界不应宣传为任意root自动支持。
303|单一policy快照未由各consumer文档一致表达；需当前安装skill、配置和CLI实际同请求hash。
304|flag独立存在不证明旗标已接线；生产v2flag与1.xconfig混搭需预检互锁。
305|原子snapshot/breaker需从请求进程观察，不以状态机单测替代热加载/告警现场。
400|唯一assertionowner是设计不变量；需当前schema/migration/旧reader共同验证，旧DDL存在不算当前可读。
401|canonical语义hash应排除路径而绑定事实；已保存旧合同但缺所有当前adapter字段的roundtrip实证。
402|跨source/location/document/assertion事务需每故障点测试；本轮未运行生产writer，保持证据不足。
403|URL必须逐document强键绑定；根名/公司名匹配不能作为事实修复，原问题归后继admission审查。
404|legacybridge可回退与天然零hit是不同验收；旧FC705r2有bridge6，不应宣称退役完成。
500|零行为seam和后续功能修复分开；只读旧trace历史有效，不能重新认定当前默认链仍等价。
501|通用五段流水线必须真实scanner调用；1.xloader阻塞说明分层代码有了并不等于默认生产工作。
502|相同conformance套件要覆盖坏编码/TOCTOU/单文件容错；后续R4文件normalize批次中断保留待验证项。
503|admission同候选换root结果不变需真实强身份oracle；evaluate_candidate曾保留未接线不能算统一入口。
601|company_raw同构迁移保留旧有效样本不覆盖下载后重新扫描；两者需分别验收。
602|dayu弱/强identity及跨periodURL绑定须保持，当前独有location生产消费者证据不足。
603|parity允许修坏行为差异但必须有RED；无当前全frozen+真实分层diff不可认证。
604|逐rootcohort顺序及每次review/soak是部署义务，accepted adapter测试不能代替。
701|sidecar完整才可复用；缺字段应indexed_only，不能把拒绝当bug或自动猜测补齐。
702|focus字面迁配置是明确原目标；FC1201允许界定延期，不得将棘轮通过写作已清零。
703|强证券身份与新公司无companies目录是不同负例；合成紫金文档跨公司无法覆盖。
704|14个Dropbox场景独立保留，排他真实样本后来获用户放宽不改变fixture全部行为义务。
801|SQLpushdown旧弱断言由FC703纠正；应保持WHERE内实义验证，而非名字子串。
802|多location必须逐个存在/hash/policy过滤；选择companies重复件不能证明外部独有根。
803|同一snapshot bundle仍须producer真实列/路径匹配；906d曾发现两个生产缺口。
804|旧shadowdiff只对样本成立；需当前candidate/selected/reason差异，不能只看成功率。
805|100k/1m规模与300/750ms/256MB原阈值保留；旧23k查询延迟不是等价规模证明。
806|active失败应failclosed且下一请求回退，不能同请求静默v1；缺当前负例逐cohort记录。
901|默认dryrun及resume绑定机制可保留；当前完整库故障恢复证据需新snapshot，不运行生产迁移。
902|存量强绑定与输入守恒需独立实体/period检查；7718unbound不能为了指标强绑。
903|Dropbox遗留保持retired/indexed_only是正确护栏；不能以canary需求自动写sidecar。
904|restore需精确ID/字节/evidence/批准；FC906c按created_at时间删除回滚方案不能作为通用安全实现。
905|catalog切换原目标含exact/latest/bundle/worker；局部reader绿无法代表全六步上线。
906|两份独立副本ABCDE恢复路径与RTO原义务未获本轮新证；不操作生产库。
1000|真实source_preparation入口存在，但源准备不是正式预测；当前0/3链阻断未进入引擎。
1001|原子SourceBundle输出应区分stdout协议/阶段错误；当前上层stderr截断丢机器结构。
1002|filing保真与policy/path/hash适用边界须随最新R4版本矩阵复核，不能继承所有旧兼容宣称。
1003|原要求失效角色调用producer；当前只返回DAG角色列表，ProcessingDemand在成功后内存enqueue，缺真worker闭环。
1004|可执行文档与实际source-preparation应同步安装副本；文档更新不能先宣称全链闭合。
1005|逐consumer协议发布与回退是独立部署步骤；版本字段存在不是N/N-1所有方向测试。
1101|missing/incorrect/unwired要分别登记；latest最新期和更正版、部分覆盖不能合并一例。
1102|exact复用旧财报下载0可由09-18紫金两次支持；parser/LLM/审查门未达正式可用仍需区分。
1103|多rootcoverage与amendment action必须真实分层测；单FY合成spy不足以覆盖。
1104|下载raw落地并非成功；09-18HK/US下载后scan/resolve失败直接暴露原capture后二次resolve义务。
1105|跨FY/跨root旧artifact保存+新producer+二次零动作仍需完整真实旅程，不能拿两个单例相加。
1201|真实三进程harness有价值，但fixture自带review/完整schema必须另加未经修饰生产配置场景。
1202|原文明确前四层不得替代跨仓E2E；FC/CA后继过度汇总是此原义务未保留。
1301|真实root不变探针是授权边界，完整/抽样级别须明确；库WAL背景变化不能简单归被测读操作。
1302|只读discovery无合格样本0允许；同时明确不等于真实复用完成，原要求应保留。
1303|Dropbox-only无样本必须blocked；FC504后用户放宽是批准scope变更而非假造排他成功。
1304|真实MD+summary与复制库失效计划尚不同于一个normalized工件T2；按角色分开。
1305|taxonomy枚举需跨层一致，现错误尾截断和retryable丢失不支持全trace完整。
1306|10并发/24hsoak/缓存稳定/无僵尸各需独立数据；CA206测试文件纯函数完全不等价。
1401|精确三仓commitmatrix与安装路径不能依赖本机sibling偶然布局；旧worktree失败曾靠junction修复。
1402|12定向mutation只覆盖预先定义攻击，需增加生产配置与无review完成路径oracle，不以kill数字替代。
1403|逐波go/no-go是发布过程；仓库代码完成不会自动触发生产配置迁移。
1404|五种rollback分开证；错误后缺结构阶段让用户无法选择正确修复路径。
1405|任一commit变化manifest应失效；现117accepted冻结旧triplet，不能作为今日保证。
1406|机器state与原始业务验收要同义；CA305只查accepted会循环证明已缩范围义务。
1500|旧实现可用与两个自然零hit窗口同时成立才退役；旧观测计算器测试不满足。
1501|hardcode清理需逐批可回滚和真实caller0，当前索引漏符号使零结果不能当完整性证明。
1502|保留历史raw并明确N-1窗口是正确目标，删除后继不能代替历史数据可读恢复验证。
1503|三SKILL/README/help/样例/安装态一致性需现版本证据；09-18仍发现3.6/3.7文字漂移。
1504|独立复审确实曾抓FC703/705/802问题；范围冻结和跨层审查需要加强，不能否认所有独立评审无效。
1505|每历史finding必须关联真实结果、生产观测和残余风险；旧关闭矩阵只把义务转交不等于已兑现。
'''

def parse(block):
    return {line.split('|',1)[0]:line.split('|',1)[1] for line in block.strip().splitlines()}

def main():
    rows=[json.loads(x) for x in (OUT/'item_ledger.jsonl').read_text(encoding='utf8').splitlines()]
    groups={'FC':parse(FC),'WU':parse(WU)}
    mapping={}
    source=ROOT/'audit_review/2026-08-13_three_repo_completion_rebaseline_plan/legacy_fc_status_registry.md'
    for n,line in enumerate(source.read_text(encoding='utf8').splitlines(),1):
        m=re.match(r'\| (FC-\d+) \| (.*?) \| ([ICSP]) \| (.*?) \| (.*?) \|',line)
        if m:mapping[m[1]]={'file':str(source.relative_to(ROOT)),'line':n,'historical_state':m[2],'classification_at_2026_08_13':m[3],'successors':re.findall(r'(?:CA|ZR)-\d+',m[5])}
    for row in rows:
        group,num=row['item_id'].split('-')
        if group not in groups:continue
        if num not in groups[group]:raise ValueError(row['item_id'])
        row['review_mode']='independent_obligation_and_successor_sufficiency_review'
        row['conclusion']='superseded'
        row['implementation_conclusion']='insufficient_evidence'
        row['reason']=groups[group][num]
        row['review_date']='2026-09-19'
        row['assessment_scope']='原义务、不同版本验收、后继覆盖及证据充分性复审；不宣称重跑全部旧测试。superseded仅表示旧领取入口失效。'
        row['legacy_transition']=mapping.get(row['item_id'])
        row['current_evidence']=['原始完整义务保留于original_claim，包含全部编号子场景和测试门。','逐项比较CA/ZR后继语义与当前代码/本轮隔离测试；具体解释见reason。','wiki assurance/fc 29份报告逐份阅读，拒绝轮次与最终接受分别保留。']
    (OUT/'item_ledger.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf8')
    with (OUT/'item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as f:
        names=['item_id','source_file','source_line','historical_state','conclusion','reason','review_mode']
        w=csv.DictWriter(f,fieldnames=names,extrasaction='ignore');w.writeheader();w.writerows(rows)
    print('legacy obligations independently compared:',sum(len(x) for x in groups.values()))
if __name__=='__main__':main()
