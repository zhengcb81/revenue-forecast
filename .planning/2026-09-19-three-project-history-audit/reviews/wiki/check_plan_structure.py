"""Independent, read-only structural diagnostics, never product-test verdicts.
The author has read the full task plan, acceptance thresholds, state machine,
test acceptance plan and validator contract before constructing these checks.
"""
from pathlib import Path
import collections, json, re

HERE=Path(__file__).resolve().parent
ROOT=Path('C:/Users/郑曾波/Projects/company-wiki/docs/plans/source-catalog-worker-recovery-v5-2026-09-03/baseline/plan')
def read(name): return json.loads((ROOT/name).read_text(encoding='utf-8'))
dag=read('gate_dag.v4.json'); registry=read('test_id_registry.v4.json'); ops=read('operation_contracts.v4.json')
nodes={n['id']:n for n in dag['nodes']}
family_nodes={n for f in dag['families'].values() for n in f['nodes_per_instance']}
known=set(nodes)|family_nodes
def prerequisites(v):
    if not isinstance(v,dict): return []
    out=list(v.get('all',[]))+list(v.get('exactly_one',[]))+list(v.get('then_all',[]))
    for branch in v.get('any',[]): out+=prerequisites(branch)
    for branch in v.get('conditional',[]): out+=prerequisites(branch)
    return out
preds={i:prerequisites(n['requires']) for i,n in nodes.items()}
def ancestors(i, seen=None):
    seen=set() if seen is None else set(seen)
    if i in seen: raise ValueError('cycle '+i)
    seen.add(i); out=set(preds.get(i,[]))
    for p in tuple(out): out|=ancestors(p,seen)
    return out
topology_errors=[]
for i in nodes:
    try: ancestors(i)
    except ValueError as e: topology_errors.append(str(e))

node_rows=[]
for i,n in nodes.items():
    roles=dag['reviewer_rules']['node_role_overrides'].get(i,{}).get('roles',dag['reviewer_rules']['default_roles_on_pass'].get(n['type'],[]))
    matches=[o for o in ops['operations'] if o.get('node')==i]
    issues=[]
    if any(p not in known for p in preds[i]): issues.append('unknown prerequisite')
    if len(roles)!=n['reviewers_on_pass'] or len(roles)!=len(set(roles)): issues.append('role/cardinality mismatch')
    if n['type']=='OP' and (len(matches)!=1 or matches[0]['operation']!=n['operation']): issues.append('operation mapping mismatch')
    node_rows.append({'id':i,'type':n['type'],'requires':n['requires'],'reviewers':n['reviewers_on_pass'],'roles':roles,'operation':n.get('operation'),'structural_issues':issues,'scope':'declarative plan mapping only; no runtime execution asserted'})

texts={f:(ROOT/f).read_text(encoding='utf-8').splitlines() for f in ['test_acceptance_plan.md','ledger_validator_contract.md','task_plan.md','acceptance_thresholds.md']}
lifecycle=['introduced_at','variant_at','expected_red_at','required_green_at','revalidate_at']
test_rows=[]
for t in registry['tests']:
    issues=[]; refs={k:t.get(k,[]) for k in lifecycle}
    for k,vals in refs.items():
        if any(v not in known for v in vals): issues.append('unknown '+k)
        if len(vals)!=len(set(vals)): issues.append('duplicate '+k)
    condition=t.get('condition_id')
    c=registry['condition_definitions'].get(condition) if condition else None
    if condition and c is None: issues.append('undefined condition')
    if c and c['kind']=='BRANCH_LIFECYCLE':
        for k in lifecycle:
            union=set().union(*(set(case[k]) for case in c['cases'].values()))
            if union!=set(t[k]): issues.append('branch lifecycle union mismatch '+k)
    locations=[]
    pattern=re.compile(r'(?<![A-Za-z0-9_-])'+re.escape(t['id'])+r'(?![A-Za-z0-9_-])')
    for name, lines in texts.items():
        locations += [{'path':name,'line':ln,'text':s} for ln,s in enumerate(lines,1) if pattern.search(s)]
    if not locations: issues.append('no direct prose locator in four core docs')
    test_rows.append({'id':t['id'],'group':t['group'],**refs,'condition_id':condition,'prose_locations':locations,'structural_issues':issues,'scope':'stable test ID declaration; does not establish a test function exists or passed'})

payload={'method':'Independent stdlib parsing/relation checks; no original checker invoked; semantic observations are recorded separately','node_count':len(node_rows),'node_ids_unique':len(nodes)==len(dag['nodes']),'test_count':len(test_rows),'test_ids_unique':len({t['id'] for t in registry['tests']})==len(registry['tests']),'topology_errors':sorted(set(topology_errors)),'nodes':node_rows,'tests':test_rows}
(HERE/'plan_structure_checks.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# Compact lifecycle mapping (inspection aid, not review verdict)','']
for group,ts in __import__('itertools').groupby(sorted(test_rows,key=lambda t:(t['group'],t['id'])),lambda t:t['group']):
    lines += ['## '+group,'']
    for t in ts:
        lines.append(f"{t['id']} | intro={','.join(t['introduced_at'])} | variant={','.join(t['variant_at'])} | red={','.join(t['expected_red_at'])} | green={','.join(t['required_green_at'])} | re={','.join(t['revalidate_at'])} | cond={t['condition_id']} | issues={t['structural_issues']}")
(HERE/'plan_lifecycles_for_review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'nodes':len(node_rows),'tests':len(test_rows),'topology_errors':payload['topology_errors'],'node_issues':[{'id':n['id'],'issues':n['structural_issues']} for n in node_rows if n['structural_issues']],'test_issues':[{'id':t['id'],'issues':t['structural_issues']} for t in test_rows if t['structural_issues']]},ensure_ascii=True))
