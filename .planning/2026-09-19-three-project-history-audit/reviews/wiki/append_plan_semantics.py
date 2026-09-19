"""Persist reviewer-authored semantic conclusions; never run production code."""
from pathlib import Path
import json,re
H=Path(__file__).resolve().parent
W=Path('C:/Users/郑曾波/Projects/company-wiki')
B='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/'
P=B+'baseline/plan/'
f=H/'item_ledger.jsonl'; rows=[json.loads(s) for s in f.read_text(encoding='utf-8').splitlines() if s]
seen={r['id'] for r in rows}
def add(i,path,line,promise,hist,evidence,verdict,rec,**extra):
    if i in seen:return
    rows.append(dict(id=i,original=dict(repo='company-wiki',path=path,line=line),promise=promise,historical_status=hist,historical_evidence='v5冻结与审查仅限文档完整性；PR处置自述不等于对应领域reviewer CLOSED。',current_independent_evidence=evidence,verdict=verdict,recommendation=rec,**extra));seen.add(i)
add('WIKI-V5-SEM-04',P+'implementation_agent_prompts.md',81,'PR-089/105已把证据由manifest.md改为schema manifest.json + report.md','addressed in v4 draft, pending frozen review','同一冻结输入的implementation_agent_prompts.md:81仍命令写manifest.md；execution_playbook.md:39及143也同样；README:145–146与plan_review_findings.md:157(PR-089)要求manifest.json和report.md。51份hash当前一致，故不是审计期间漂移。','contradicted','下一代统一唯一机器证据接口；对全部可执行模板做正向工件名/字段关系核对，不能只扫禁用词。',severity='P2',scope='planning semantic consistency; no runtime bypass asserted')
add('WIKI-V5-SEM-05',P+'implementation_agent_prompts.md',231,'G10R三份prompt使用与DAG相同exact release join','PR-092 addressed; G10-PROMPT-S01 planned','prompt:231–234列G07E、条件G11M-L和BP/BF，遗漏gate_dag.v4.json:210在LLM_ENABLED要求的G11M-L-ADR；另两prompt:240/248引用同集；execution_playbook.md:880附近同样。BP的传递前驱通常已含ADR，故本结论是exact清单不相等，非已证明能越过机器Gate。','contradicted','让每种profile的展开入边与六模板输入精确比较；区别直接依赖和传递依赖。',severity='P2',scope='direct Gate×prose relation')
add('WIKI-V5-SEM-06',P+'execution_playbook.md',922,'G11A通过后NO_INDEX可进入D11B-A1','old direct successor remains in frozen playbook','execution_playbook.md:922写按ADR进入D11M或D11B-A1；:930–931及rollout_rollback_runbook.md:14/192要求两分支均先D11J，且machine DAG的D11B-A1有G11J前置。','contradicted','修正旧摘要出边并以展开DAG自动生成唯一下一步；不得沿旧一句跳过journal init。',severity='P2',scope='planning text; machine graph has the stronger barrier')
add('WIKI-V5-SEM-07',P+'rollout_rollback_runbook.md',278,'真实LLM迁移分支由ADR-11=SCHEMA_DELTA选择','PR-055/105 addressed in v4','runbook第8节错误写ADR-11为SCHEMA_DELTA；gate_dag.v4.json:202–206及同文第1节明定ADR-13为schema delta，ADR-11只有LLM_OFF/LLM_ENABLED。此分支按字面不可满足。','contradicted','统一决策ID与值域，增加所有prose decision=value对机器枚举的检查。',severity='P2',scope='planning branch consistency')

# Every PR row was reread as a table, against the complete final baseline prose.
# Persist exact original text and independent closure boundary, not keyword PASS.
special={55:'SEM-07: rollout的ADR编号仍不一致',61:'SEM-05: exact G10R prompt还漏一个具名决策前置',70:'SEM-01/02:逐ID registry虽结构闭合但Gate×Test及人数语义未全闭',77:'SEM-01/06:journal节点已建，但测试义务映射和旧下一步摘要仍有冲突',89:'SEM-04:可执行模板仍输出manifest.md',92:'SEM-05:补了G09P/G09，但整个exact join仍不相等',105:'SEM-04/05/06/07:全面同步承诺有现存反例'}
prp=W/P/'plan_review_findings.md'
for line,s in enumerate(prp.read_text(encoding='utf-8').splitlines(),1):
    m=re.match(r'\| (PR-(\d{3})) \|',s)
    if not m:continue
    cells=[t.strip() for t in s.strip().strip('|').split('|')]
    num=int(m[2]); ident=m[1]
    evidence=('逐项重读最终baseline全部实施/验收/状态/审查/回滚正文及315test/115node。原文状态仍为pending independent re-review；本文件:177–187要求每个P0/P1由相应领域reviewer明确CLOSED。v5最终test-dag-closure4:56明确未做内容级语义审查；冻结文件hash完整不能替代此关闭条件。')
    if num in special:evidence+=' 当前具体反例：'+special[num]+'；见同ledger相关WIKI-V5记录。'
    add('WIKI-PR-'+m[2],P+'plan_review_findings.md',line,ident+' | 问题：'+cells[2]+' | 候选处置：'+cells[3],cells[4],evidence,'contradicted' if num in special else 'insufficient_evidence','保留候选处置作为设计输入；在新revision逐条做语义关闭与实施证据，不能从v5冻结accepted推导此项CLOSED。',scope='historical proposed remedy / independent closeout',planning_assessment='候选处置明确、计划测试存在；尚无本条领域正式关闭凭证。'+special.get(num,''),assessment_limit='未执行未来功能；不因未实施把合理规划判为产品缺陷。')

f.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
p=H/'read_coverage.json';x=json.loads(p.read_text(encoding='utf-8'))
new=['v5-version-contract-review.md','v5-version-contract-review-rev2.md','v5-version-contract-review-rev3.md','v5-freeze-review-handover-docs.md','v5-freeze-review-handover-state.md','v5-freeze-boundary.md','v5-version-reference-inventory.md','findings.md','progress.md','baseline/plan/execution_playbook.md','baseline/plan/rollout_rollback_runbook.md']
x['full_text_read']=list(dict.fromkeys(x['full_text_read']+[B+n for n in new]));x['selected_sections_read']=[r for r in x['selected_sections_read'] if r['path'] not in x['full_text_read']]
x['semantic_assessment_records']['pr_findings']=105
x['uncompleted_main_clusters']=['v5 historical progress/revision/investigation and remainder incident','old worker full semantic deltas and version commitment mapping','freeze findings individual closure ledger']
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} records; {len(x["full_text_read"])} full-text files')
