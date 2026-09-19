"""Manual semantic decisions for remaining root context, not inferred PASS by keywords."""
from pathlib import Path
import json,csv,collections,re
P=Path(__file__).resolve().parent
B=json.loads((P/'scope.json').read_text(encoding='utf-8'))['blocks'];rules=[]
H='historical_only';U='insufficient_evidence';X='contradicted';S='supported_scoped';D='superseded'
def r(f,a,b,v,why,ev):rules.append((f,a,b,v,why,ev))
r('AGENTS.md',1,205,S,'现行source-only边界明确退役研究writer；规则是规范而非每条实现已达成。历史技术架构说明与当前保留模块相符。','AGENTS BOUNDARY-0；root archive审查codegraph证据')
r('AGENTS.md',31,52,U,'configdoctor声称发现配置问题及旧目录直接公司根/new raw可选仍与现代canonical/raw和注册adapter要求有缝；仅文档规范不证明runtime配置正确。','wiki GP002/doctor审查；filing FC805 v2 shadow关闭fixture')
r('CLAUDE.md',1,172,D,'旧Schema和研究Wiki行为已被AGENTS BOUNDARY-0覆盖；不把这些研究功能退役报成当前缺陷。','AGENTS source-only；root task BOUNDARY-0')
r('CLAUDE.md',3,20,X,'该文件仍自称所有ingest/lint/query须遵守，要求LLM维护研究wiki并把新原文直存公司根；未标退役，与当前AGENTS/README职责和canonical目录冲突。','README7–9/128；AGENTS7/16最高优先边界')
r('CLAUDE.md',148,172,X,'自动schema建议仍命令立即补213投资评估，与当前source-only相反；旧运行指标只支持4/25历史，不应自动成为活动实施任务。','同文件152时间；AGENTS边界；review_queue历史9批准与这里0也非同一快照')
r('PLANNING_STATUS.md',1,101,H,'逐状态按原日期审：plan-only、candidate、rejected、open和closed_superseded_incomplete均保留；没有把v5计划完成当实现完成。','wiki v5/R4审查；root旧CW3–10未闭合；filing验证')
r('PLANNING_STATUS.md',1,20,U,'最新不同作者accepted/rejected分裂说明技术局部认可与文档验收未同步；大test数字不能替代每门禁scope和环境。','R4A/R4B owners逐receipt判定；symlink7skip保留')
r('README.md',1,354,H,'完整读取当前README，示例/配置/结构是使用合同而非本轮实跑证明；没有执行下载/启动/ingest示例。','本轮只读；AGENTS；legacy/CW ledger当前边界')
r('README.md',3,18,S,'现行资料供应职责和StockWiki研究独占已明示，旧行业/投资功能不足属退役非当前bug。','AGENTS BOUNDARY-0；root archive审查')
r('README.md',108,110,S,'纯IngestService与source合同确实把写raw/研究语义排除且承认legacy批迁移待完成，不将合同通过夸成全部管线部署。','CW1–4源合同历史测试与规划边界')
r('README.md',126,128,U,'Pause/立即启动/默认三根/每小时scan/二次SHA仅部分历史真实窗口；当前paused生产和GP002错误配置不能由此宣称端到端可用。','filing pause/refcount/deadline反例；wiki GP002；WR7/29真实窗口仅当时范围')
r('README.md',309,311,S,'E2E目录仅config冒烟被明确提示，修正了把名称当真实管线覆盖的误解；integration是否真实下载仍须逐test核。','filing E2E_DESIGN及当前测试源码审查')
r('README.md',327,330,U,'四个历史文档链接仍指root，已迁docs/archive；导航漂移可让历史计划与现行状态混淆。','本轮inventory有archive17；独立路径存在检查root_context_checks.json')
r('README.md',350,354,S,'明确indexed不等于reusable，fixture绿不意味着production声明；0/7712和0/23513是8/9历史时点，不能无限延续成今天统计。','原354明示production unclaimed；当前GP002另证')
for f in ['_MOC_公司.md','_MOC_行业.md','_MOC_近期更新.md','index.md']:
 r(f,1,1000,D,'4月研究Wiki导航/问题列表/Dataview旧projection，后被source-only退役。统计和问题只作上下文，不复核每个投资命题或把导航当数据湖机器索引。','AGENTS/README；index最后更新时间4/19，current resolver/catalog与Markdown不同层')
r('auto_discover_report.md',1,36,H,'候选不是已验证实体，报告要求人工审查；有限公司/归属于上市公司等高频泛词证实数量不代表实体质量，但旧研究扩展已退役。','原11–30直接泛词；原34人工审查；BOUNDARY-0')
r('contradiction_report.md',1,13,H,'200候选、0高置信度仅筛选遥测；未宣称200真实矛盾或所有事实正确，不能用0高置信推无矛盾。','报告正文；4月原计划可靠性缺口，现退役')
r('cross_verify_report.md',1,88,U,'按来源数称高可信未附独立source_id/hash；同公司季报跨13公司传播也可共用一份源，不能独立验证。保留旧方法缺陷，不给每个投资数字真假裁决。','原17东方电缆报告13来源13公司；污染3886条计数审查；BOUNDARY-0')
r('dashboard.md',1,23,H,'5/19重建结束与健康0/100、LLM0、parsed0并存，阶段代码完成不等于产品使用成功；不以旧LLM指标评价当前source-only。','原4/6/10/15；root archive实现范围')
r('dashboard_v2.md',1,68,U,'5/18健康88与测试100仅1/1及gate66.7%；注册/存在不能证明真实端到端质量，翌日dashboard0/100是指标定义不同，不直接同版回归。','原4/14/18–19/35–41/68；dashboard.md生成次日')
r('review_queue.md',1,84,H,'9条低风险assess标批准缺操作者/批准时间/内容hash；不回溯猜批准真伪，也不授权重执行，研究writer已退役。','原RQ001–009；CLAUDE统计0为旧快照不与后日期合一')
r('audit_worklog_2026-07-09.md',1,70,H,'47项旧工程审计逐项保留：路径/config/schema/大量无source/假闭环/测试副作用/cleanup风险；不是本轮再次证明每项现存。旧研究实现已退役，共通缺口映射当前专项。','root archive和root task/findings；当前filing配置与SectionQuery反例')
r('review_plan.md',1,42,D,'completed_audit_template/cancelled_open_items明确空checkbox非活动backlog；发现迁FCAP，不能把模板完结误认为修复完成。','PLANNING_STATUS；本文件closure说明')
r('verification_CW-2.24_plan.md',1,56,H,'completed_audit_only只原R1索引和R2规范化范围；三市场/最新/artifact等不在scope，不执行历史命令。','special/CW ledger；PLANNING_STATUS101明示618 vs52+160')
r('verification_CW-2.24_plan.md',25,25,U,'618全量checkbox没有对应完整收据；结果只52+160，不能继承全量测试已重跑。','原40/PLANNING_STATUS101')
r('verification_CW-2.24_plan.md',40,56,U,'现有记录支持当日R1/R2有限样本；git add不等于可复现交付；identity conflict扁平missing抹掉原因，目录不重复只human层。','filing当前错误包装；源原文52+160/已gitadd/index.md旧')
r('task_plan_v2.md',1,313,D,'旧事件总线/队列/反馈/投资评估设计明确8/9cancelled/superseded；未实现不是当前应补投资功能。共同source治理义务须迁FCAP，不随方案取消自动达成。','AGENTS BOUNDARY-0；本文件closure；root archive同期删除dead modules')
for f in ['temp_design.md','设计思想.md']:
 r(f,1,11,D,'相同原始研究愿景按版本分别保留；后经BOUNDARY-0拆分StockWiki研究与company-wiki资料，不把全部目标列当前功能缺失。','原文全文；AGENTS/README当前')
r('llm-wiki.md',1,75,H,'理念参考与示例不是已实施验收合同；LLM不遗忘/近零成本没有实测保证，来源和派生层分离原则仍有价值。','文件全文；现行source-only和immutable原件合同')
rows=[];struct=[];pending=[];files={x[0] for x in rules}
for b in B:
 if b['relative'] not in files:continue
 matches=[x for x in rules if x[0]==b['relative'] and x[1]<=b['line_start']<=x[2]]
 if not matches:pending.append(b);continue
 v=matches[-1]
 if re.fullmatch(r'#+\s+[^\n]+',b['original_text']) and not any(w in b['original_text'] for w in ['完成','状态','通过','缺','问题']):struct.append(b);continue
 rows.append(dict(b,item_id=f'WIKI-LEGACY-CONTEXT-{len(rows)+1:04d}',reviewer='history_filing',verdict=v[3],historical_claim=b['original_text'],historical_evidence_scope='原文完整阅读；现行规范与历史上下文分开',current_evidence=v[5],reason=v[4],recommendation='统一活动入口边界，保留历史但标明superseded；不得把历史数量当当前真值',manual_semantic_range=f'{v[0]}:{v[1]}-{v[2]}'))
(P/'context_item_ledger.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
with (P/'context_item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,data in [('context_structural_exclusions',struct),('context_pending',pending),('context_coverage',dict(files=len(files),reviewed=len(rows),structural=len(struct),pending=len(pending),verdicts=dict(collections.Counter(r['verdict'] for r in rows))))]:
 (P/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(files),len(rows),len(struct),len(pending))
