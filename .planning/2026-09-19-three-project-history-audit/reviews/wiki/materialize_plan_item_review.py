"""Format previously read, reviewer-assessed plan nodes/tests into individual rows.
This is NOT a keyword-PASS classifier: no item receives runtime PASS. The 36
group assessments below are authored after reading all acceptance clauses and
315 lifecycle rows; exact definitions and individual lifecycle are preserved.
"""
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent
P='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/baseline/plan/'
R=Path('C:/Users/郑曾波/Projects/company-wiki')/P
C=json.loads((H/'plan_structure_checks.json').read_text(encoding='utf-8'))
GROUPS={
'authorization_revalidation':'freshness、撤销锚和purpose/subject均有负例；必须验证副作用前重新校验，不以旧receipt永久授权。',
'bootstrap_trust':'要求OS先于Python import验证解释器/vendor、持有identity；现有v5 checker隔离导入通过不等于未来生产bootstrap已完成。',
'bounded_write_faults':'DB提交前、提交后发布前、发布中和post-read四窗口区分清楚；以RPO=0、reconcile不重发provider作oracle。G11J的具名映射另有SEM-01缺口。',
'canary_a':'scan-only、normalize-persist和无LLM完整cycle分别有one-shot、精确写集合、pause和独立G，三阶段不能互相替代。',
'canary_b':'每primary/fallback独立授权、写合同和post-review，网络和未知计费边界明确；不能用stub成功代表真实供应商canary。',
'checkpoint':'以scan_runs提交和per-root outcome/fingerprint为事实源，包含DB/JSON崩溃窗口、离线与配置变化；实际新增root能力仍需部署配置测试。',
'durable_budget':'四维预算必须一次CAS预留且settlement守恒；未知结果保留成本不能自动重发。',
'end_to_end':'真实子进程、源轮换、故障/变异覆盖主要worker边界；计划范围未包括filing-fetch→canonical writer→exact resolve→revenue-forecast的外部用户旅程。',
'evidence_lifecycle':'源正文与secret分层，仓外批准sink有ACL/加密/TTL；不能把证据文件存在当实际权限边界验证。',
'existing_baseline':'十三个既有基线明确never-red，仅G11A受控只读窗口执行；不误把既有正确行为造红，也不能把旧测通过当新reader实现上线。',
'final_activation':'runtime-template和本次activation两份purpose独立批准、事后actual、补偿零删除与逐cycle重验均有合同；本轮不会执行。',
'global_safety':'路径隔离、source OS deny、网络拒绝、独立review及敏感信息边界均明确，mock/sentinel不能替代真实权限拒绝。',
'index_branch':'只在ADR-02选INDEX后实施；有幂等、中断、ENOSPC和峰值空间验证，生产迁移另有D/OP/G而非常规open顺带DDL。',
'journal_protocol':'intent/template与terminal actual分时以避免未来hash环，head anchor/CAS及receipt顺序可审；是否实现未由冻结记录证明。',
'ledger_validator':'假PASS/人数/分支/下一边/链头/授权等有负例，独立oracle/fixture可物化不可仅schema；是否覆盖所有prose关系仍见SEM-01/02。',
'llm':'current source+normalized绑定、cache逐文档rebind、队列dedupe、未知计费和主备权限均有明确oracle；吞吐需真实arrival/service与成本分布。',
'no_index_branch':'NO_INDEX不是NO_CHANGE：普通open零DDL与显式初始化仍需实施；不能靠禁用index就关闭schema生命周期要求。',
'observability_cancel':'liveness/VM/business分离，真实子进程在SQL开始后发pause并有数值SLA；handler清理、回调不重入和日志最小化明确。',
'observation':'至少2小时且连续5完整周期，失败清窗口，逐cycle精确写合同、结束pause；未用uptime替代成功。',
'parser_route_fixed':'14键route含unsupported，13实际路径按S/M或禁用与LIMIT/ERR/PAUSE模板展开；28固定ID本身不是完整展开后全部样本测试。',
'plan_contract':'六份G10C/G10R prompt与各自exact入边相符，防止未来依赖和合并审查；需同时补非G10的具名关系检查。',
'prelogin':'ARM、dormant CAS、login token分离，TTL/单次消费/第三方值保护及明确注销批准可验证；不能用facade代替真实OS双进程竞态。',
'process_generation':'approval/intent/contract/journal/receipt绑定同process generation，重启使旧capability失效；仅PID数字不够。',
'production_wrapper':'one-shot、不可写release/trust、typed PK/column/file precommit与OS deny覆盖真实生产封装；需生产实际配置而非fixture预迁移。',
'queue_performance':'warm30/cold-ish10/多规模与独立ordered-ID oracle，固定measurement mode和progress_n；exact VM模式条件选择合理，不把callback proxy当exact。',
'queue_semantics':'force/retry/terminal/重复location/parseable-primary和源S1→S2矩阵明确；不能通过删除外层locationless数据或提前LIMIT换性能。',
'request_ledger_migration':'只在A3+G07E后ADR-13选分支，NO_SCHEMA_DELTA不造迁移；schema更改含故障恢复及普通reader零DDL。',
'reset':'独立D/OP/G绑定failure generation和exact ancestor D、全部下游失效；reset-only不授予resume/arm/login或LLM。',
'retention_capacity':'tmp路径/符号链接/在用文件/ENOSPC与容量公式有oracle；生产delete/VACUUM/backup清理明确不在此合同，现存自动apply须另隔离。',
'scanner_correctness':'缓存、rehash、离线/中断/路径安全和battery-before-enumeration合同明确；需补runtime policy×root adapter组合的生产前置证明。',
'scanner_performance':'同拓扑同baseline与环境旧新各10次，P95≤120s且≥2倍，不能用历史427s作分母或漏扫换速度。',
'schema_lifecycle_shared':'NI/IDX生命周期采用closed branch case并集；missing/old schema显式拒绝、init/upgrade独立，ZR测试fixture显式准备而不复活eager DDL。',
'schema_registry':'枚举全部schema的ID/path/hash/size闭包，禁ambient/network；schema合法性与业务语义是两层证据。',
'startup':'正常登录仍重验release/runtime授权/circuit/generation等；G12C验收不是永久授予任何未来cycle。',
'supervisor_control':'完整cycle成功才清预算，交替签名与全局失败/无成功窗口持久化，pause有界、PID identity和Job Object处理明确。',
'validator_fixture':'要求base先OK、每mutation可物化并唯一primary error，避免目标检查空转仍被其他规则顺带拦截。',
}
assert set(GROUPS)=={t['group'] for t in C['tests']}
texts={n:(R/n).read_text(encoding='utf-8').splitlines() for n in ['test_id_registry.v4.json','gate_dag.v4.json']}
def lineno(name,i):
 p=re.compile(r'"id"\s*:\s*"'+re.escape(i)+'"')
 return next(n for n,s in enumerate(texts[name],1) if p.search(s))
rows=[]
for t in C['tests']:
 defs=[x for x in t['prose_locations'] if re.match(r'^\|\s*`?'+re.escape(t['id'])+r'`?\s*\|',x['text'])]
 d=(defs or t['prose_locations'])[0]
 bad=t['id'] in {'WRITE-F01','WRITE-F02'}
 rows.append({'id':'WIKI-V5-TEST-'+t['id'],'original':{'repo':'company-wiki','path':P+d['path'],'line':d['line']},
 'promise':d['text'],'historical_status':'frozen planning obligation; Phase0–12 pending; not a passed product test',
 'historical_evidence':'test_id_registry.v4.json:'+str(lineno('test_id_registry.v4.json',t['id']))+'；v5测试/DAG复审只验证冻结/checker集合，其closure4:56排除内容语义复审。',
 'current_independent_evidence':{'definition_read':d,'lifecycle':{k:t[k] for k in ['introduced_at','variant_at','expected_red_at','required_green_at','revalidate_at','condition_id']},'structural_checks':t['structural_issues'],'semantic_assessment':GROUPS[t['group']],'test_not_run':True},
 'verdict':'contradicted' if bad else 'not_deployed','planning_assessment':'具名G11J/G10R义务与registry不一致；见WIKI-V5-SEM-01' if bad else '定义、层级和生命周期已读；本条声明有可验证意图及合法节点绑定，未赋予运行通过结论',
 'recommendation':'实施前先关闭SEM-01冲突。' if bad else '按该ID的选中分支、首绿/重验节点取得原始日志与独立oracle；正式实施证据未具备前保持规划状态。',
 'assessment_limit':'not_deployed仅指v5计划证据链未提供本条实施验收，不推断仓库任何其它分支都无类似功能。'})
for n in C['nodes']:
 bad=n['id'] in {'D07E','G07E','G11J'}
 rows.append({'id':'WIKI-V5-NODE-'+n['id'],'original':{'repo':'company-wiki','path':P+'gate_dag.v4.json','line':lineno('gate_dag.v4.json',n['id'])},
 'promise':n,'historical_status':'fixed DAG planning node; not executed implementation ledger',
 'historical_evidence':'baseline/plan/task_plan.md:813-829 Phase0–12 pending；v5冻结115节点计数不等于这些节点已PASSED。',
 'current_independent_evidence':'逐节点读取DAG并与gate_state_machine、task_plan、agent_review_gates对照；plan_structure_checks.json independently checks graph/roles/OP mapping，无悬空/环/role基数不符。',
 'verdict':'contradicted' if bad else 'not_deployed','planning_assessment':('SEM-02：本节点机器DAG要求2人，traceability:180错误写1人。' if n['id'] in {'D07E','G07E'} else 'SEM-01：正文G11J要求WRITE-F01/02但registry未列该重验节点。') if bad else '前驱/分支/角色/操作映射完整且结构自洽；节点具体行为需未来执行证据，不能仅由DAG存在判完成。',
 'recommendation':'新revision对齐机器与正文再实施。' if bad else '保留节点权限范围及独立D/OP/G；新证据写入实施ledger，不把冻结审查当运行完成。'})
target=H/'item_ledger.jsonl'
existing=[json.loads(s) for s in target.read_text(encoding='utf-8').splitlines() if s.strip()]
keep=[r for r in existing if not r['id'].startswith(('WIKI-V5-TEST-','WIKI-V5-NODE-'))]
target.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in keep+rows),encoding='utf-8')
print(json.dumps({'tests':len(C['tests']),'nodes':len(C['nodes']),'records':len(keep)+len(rows)}))
