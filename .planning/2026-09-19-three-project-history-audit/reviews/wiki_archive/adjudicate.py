"""Manual full-body review of the 17 retired company-wiki archive documents."""
from pathlib import Path
import collections, hashlib, json, re
HERE=Path(__file__).resolve().parent
PLAN=HERE.parents[1]
WIKI=PLAN.parents[1].parent/'company-wiki'
CASES=[]
def case(f,start,end,v,target,reason,evidence,remedy):
    CASES.append(dict(id=f'WA-{len(CASES)+1:03}',file=f,start=start,end=end,verdict=v,
        target=target,rationale=reason,evidence=evidence,remedy=remedy))
B='company-wiki/AGENTS.md:3–29,170–171; docs/archive/CURRENT_STATUS.md; scripts/graph.py:6–7; scripts/models/__init__.py:2; scripts/llm_client.py:21–23'
base=[
('CURRENT_STATUS.md','supported_scoped','归档适用边界','逐条核对当前AGENTS和模块说明，研究writer退役、规范Graph和单线程约束有当前证据；9/4全文阅读是旧审计声明，本轮17文档另行全文阅读不沿用旧PASS。'),
('BUGFIX_REPORT.md','historical_only','旧下载目录与配置修复方案','正文是相对save_dir/多目录收集/人工复制方案和伪代码，未含正式运行结果或内容身份验证；已不是当前filing→wiki唯一canonical writer路线。相同错目录痛点不能由旧copy方案直接修当前adapter注册。'),
('CODE_REVIEW.md','historical_only','4月架构/代码/质量/测试审计','全部评分、51文件/59同名/41无测试/30%和一个月预测只属当时评估，无当前测量依据。跨模块同函数名和多import本身不能证明重复代码/循环依赖；后继模块与职责已变。'),
('GAP_FIX_PLAN.md','superseded','Query存回/矛盾检测/源建议三阶段','14/9/10测试和全勾选仅为旧记录；研究语义回写已由7/16边界退出，不要求恢复作为当前闭环。资料定位/来源缺口仍可保留，但须绑定source/locator。'),
('HARDCODE_FIXES.md','historical_only','规则配置化改进','规则从代码移到YAML提高可维护性，不自动提升实体/分类准确率或任意layout泛化。示例confidence0.95是声明值不是校准概率；结尾仍留验证/热重载未做。'),
('IMPLEMENTATION_STEPS.md','historical_only','8步完成与56测试','全文区分配置/下载/logger/README/tests/utils/docs/monitor；56=8+9+22+17数量自洽但没有三root真实链证据。旧download_v2已非当前指定市场链。'),
('IMPROVEMENT_PLAN.md','superseded','原始分类、问题匹配、自进化与监控','原始文档按类型、增量处理思路有保留价值；综合研究自进化/自动写页面不再是company-wiki产品义务。全部完成与原测试清单未勾选冲突需限定，不能从计划代码示例当完成。'),
('KARPATHY_COMPARISON.md','historical_only','旧84%理念匹配评分','全部比较/建议均阅读；权重和评分是主观框架匹配，不是资料正确率/真实旅程成功率。本文不重验外部gist引用，依据是本地历史文档内部论证；不能用相似目录推断全功能匹配。'),
('KARPATHY_COMPARISON_V2.md','historical_only','旧75.7%及无LLM差距','同日版本改变指标维度与加权口径，不能和84%比较改善/退步；2.2说LLM读取完全匹配，2.7又全部无LLM，评价层级混用。研究回写路线后继退役。'),
('KARPATHY_GAPS_PLAN.md','superseded','尚pending的LLM/Query/矛盾计划','全部未勾选只是4月版本计划，与其它同日完成说明属迭代未同步；不应重复排队实施研究writer。统一来源LLM客户端当前存在，不宜照旧说整个系统无LLM。'),
('LLM_INTEGRATION_PLAN.md','superseded','6阶段LLM集成与指标','当前LLMClient已存在且多provider，保留基础设施成果；综合评估填充80%/核心问题100%/自动3–5页面属于已退出研究目标。增加LLM调用和页面数量不是信息正确性。'),
('PHASE1_COMPLETE.md','historical_only','安全配置与测试基础设施11/11','测试清单主体是目录/文件存在、可导入、env覆盖；能支持基础设施窄范围，不能支持所有敏感信息清零或业务生产全链。未读取真实密钥/运行旧下载以复验。'),
('PHASE2_COMPLETE.md','superseded','40测试与models facade架构','当前graph.py明确规范实现，models弃用。旧两脚本迁移不足以证明所有脚本统一；40=12+15+5+8只支持列出的套件，不能外推100%代码覆盖。'),
('PLAN.md','superseded','原始知识库路线图和后继拓扑重构','全460行包含早期计划、不同日期进度和再次重构；不能按最后标题覆盖此前未勾选项。raw不可变/出处保留仍有效，自动研究Wiki/拓扑writer按当前边界退出。'),
('REFACTORING_PLAN.md','superseded','4阶段生产化计划709行','逐段读安全、配置、Graph、ingest、存储、异步、错误、监控、文档及所有DoD。设计伪代码不是可执行验收证据；88%coverage/2x/3x/错误率/无安全漏洞无当时完整运行日志不能认定达成。当前仍单线程，不恢复并发LLM。'),
('TESTING.md','historical_only','旧测试指南及coverage目标','命令/fixture/CI YAML是使用示例与目标，不是CI实际配置或执行。临时隔离/错误例/mock次数有方法价值；E2E目录名和10–30秒描述不能规定测试已覆盖用户链。旧phase文件当前给定路径不存在不能反推出当年没跑。'),
('source_suggestions.md','insufficient_evidence','0缺口0建议的输出','只有时间和两个零，无输入范围/样本/来源/分析链；不能证明系统已没有信息缺口，也不证明源发现实现错误。')]
for f,v,t,r in base:
    case(f,1,100000,v,t,r,B,'保留历史字节和日期；仅迁移当前source-oriented目标的独立验收，不重新运行旧有写入、迁移、调度或下载命令。')
case('IMPLEMENTATION_STEPS.md',20,23,'contradicted','logger全替换的完成勾选',
     '同条写[x]替换所有print但括号仍待实施，不能把创建logger当所有调用者迁移完。','原文22行；后继实际worker日志字段问题见reviews/wiki_legacy','创建模块和迁移真实调用者分开验收。')
case('IMPROVEMENT_PLAN.md',263,294,'insufficient_evidence','四阶段全部完成',
     '263–282全部测试仍空框，290–294却全完成；没有可定位运行证据，清单和汇总互证不足。','本文件263–294','历史完成仅作为声明；当前退休目标不恢复，存续功能重新看真实入口。')
case('KARPATHY_COMPARISON.md',106,216,'insufficient_evidence','百分比评分和总体84%',
     '权重计算18+23.75+9+11.25+10+12=84可复算，但评分本身无观测样本/量表/独立裁判，不是功能或准确率证明。','该文件评分表；KARPATHY_COMPARISON_V2.md:141–152','评分可作历史主观看法保留，不纳入修复通过或准确性结论。')
case('KARPATHY_COMPARISON_V2.md',63,75,'contradicted','LLM读取完全匹配',
     '同段75承认缺LLM，后文129–135又全部无LLM；脚本抽取不能证明声称的LLM读取/理解功能。','本文件63–75,125–135','按具体行为而非名称或架构形似确定能力。')
case('KARPATHY_COMPARISON_V2.md',141,152,'insufficient_evidence','75.7平均分',
     '530/7=75.714数值可复算，维度数量/权重与前版不同；不能作历史改善趋势或准确性指标。','KARPATHY_COMPARISON.md:208–216','不要把主观自评分纳入测试通过率。')
case('HARDCODE_FIXES.md',187,207,'insufficient_evidence','所有规则配置化与动态加载泛化',
     '示例仅证明配置key设计，无多行业评估集、未说明runtime刷新且末尾热重载pending。规则配置化不等于语义摄取adapter已支持任何根。','本文件242–265；9/18真实company审计','验证选定配置实际进入真实消费者和真实资料分类，不只打印规则数量。')
case('LLM_INTEGRATION_PLAN.md',366,383,'insufficient_evidence','始终fallback和JSON正则降级',
     '失败返回规则结果会改变质量语义，计划未给出降级结果不可误称高质量的门；缓存也没绑定source/model/prompt/version。当前不能照旧把所有fallback视为成功。','本文件366–383；reviews/wiki/worker文档审查','保留fallback标记、source绑定与失败原因；按当前资料质量契约验收。')
case('PHASE1_COMPLETE.md',178,188,'insufficient_evidence','没有敏感信息/可以安全推进的全局结论',
     '列出的11测试主要检查config一处和env模板，不能证明整个repo与历史日志无secret；不因本轮未发现而扩大该声明。','本文件43–78','限制结论到受检文件和实际断言；无需为审计打印真实secret。')
case('PHASE2_COMPLETE.md',176,185,'historical_only','打印API key的旧示例',
     '示例会将敏感值输出，和安全目标不相容；本轮只读示例不执行，不表明发生实际泄露。','本文件178–184','未来活跃文档只展示配置是否存在/脱敏摘要，归档不作为执行入口。')
case('PLAN.md',295,358,'historical_only','阶段重复编号/cron/数据数量',
     'Phase2 cron未勾，Phase5后续已配置；两个Phase4、后继4–5完成属于时序追加而非可由单行决定当前状态。53→204→14、5397→26316→123仅历史过程量，不证明业务准确。','本文件295–358','按时间和语义分别保留，不把旧未勾项自动变为今天新增任务。')
case('REFACTORING_PLAN.md',409,484,'insufficient_evidence','3x目标与2x样例及并发可靠性',
     '424要求3x，468测试仅2x；477成功率>0.8与最终错误<1%不是同一门。LLMClient当前明确非线程安全；不能以异步规划完成为吞吐量已获益。',B+'; 本文件424,468,477,684','如将来确需并发，先量化同一workload基线与隔离状态；本轮不实施。')
case('REFACTORING_PLAN.md',587,596,'insufficient_evidence','测试分层百分比汇成88%',
     '不同测试层覆盖集会重叠，不能按表格百分比直接推出整体88；没有统一文件/分支分母和coverage原件。','本文件587–596','单份coverage原始数据与实际收集列表、分支覆盖并存，不代替行为oracle。')
case('REFACTORING_PLAN.md',525,564,'insufficient_evidence','伪代码assert证明生产就绪',
     'full_pipeline_works等仅待实现占位函数；无源码/输入/日志/错误分支，与“无安全漏洞”“所有测试100%”并非可验证同义。','本文件529–564','从真实用户输入到可复用证据和输出建立可观察断言，精确说明未执行范围。')

rows=[]; coverage=[]
for f,_,_,_ in base:
    p=WIKI/'docs/archive'/f; raw=p.read_bytes(); lines=raw.decode('utf-8-sig').splitlines(); digest=hashlib.sha256(raw).hexdigest()
    heading=''; nrows=0
    for n,line in enumerate(lines,1):
        if not line.strip(): continue
        if re.match(r'^#{1,6}\s',line):heading=line
        c=[c for c in CASES if c['file']==f and c['start']<=n<=c['end']][-1]
        rows.append(dict(id=f'WAL-{len(rows)+1:05}',source_file=str(p),relative='docs/archive/'+f,
            line_start=n,line_end=n,file_sha256=digest,original_text=line,heading=heading,
            manual_case_id=c['id'],verdict=c['verdict'],rationale=c['rationale'],evidence=c['evidence'],remedy=c['remedy'],
            historical_markers=re.findall(r'完成|通过|pending|PASS|\[x\]|\[ \]',line,re.I),
            review_scope='retired historical applicability and evidence sufficiency; no live research writer replay',reviewer='root',read_status='fully_read'))
        nrows+=1
    coverage.append(dict(file='docs/archive/'+f,sha256=digest,lines=len(lines),occurrences=nrows,read_status='fully_read'))
(HERE/'manual_cases.json').write_text(json.dumps(CASES,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'item_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
(HERE/'coverage.json').write_text(json.dumps(dict(files=coverage,summary=dict(files=len(base),lines=sum(x['lines'] for x in coverage),occurrences=len(rows),manual_cases=len(CASES),pending=0,verdict_occurrences=dict(collections.Counter(x['verdict'] for x in rows)),note='Counts are source occurrences, not bugs or executed tests.')),ensure_ascii=False,indent=2),encoding='utf-8')
paths=['AGENTS.md','scripts/graph.py','scripts/models/__init__.py','scripts/llm_client.py','scripts/config_loader.py','scripts/config.py']
(HERE/'current_evidence_manifest.json').write_text(json.dumps([dict(path=str(WIKI/f),sha256=hashlib.sha256((WIKI/f).read_bytes()).hexdigest()) for f in paths],ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(files=len(base),lines=sum(x['lines'] for x in coverage),occurrences=len(rows),manual_cases=len(CASES)),ensure_ascii=False))
