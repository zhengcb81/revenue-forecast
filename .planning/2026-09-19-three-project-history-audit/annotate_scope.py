"""Classify discovered paths; this is coverage bookkeeping, not semantic review."""
from pathlib import Path
import json, hashlib, difflib

PLAN=Path(__file__).resolve().parent
inv=PLAN/'inventory'
corpus=json.loads((inv/'all_documents.json').read_text(encoding='utf-8'))
rows=[]
for row in corpus['records']:
    p=row['path'].replace('\\','/')
    low=p.lower()
    scope='engineering_context'; owner={'revenue-forecast':'revenue','filing-fetch':'filing','company-wiki':'wiki'}[row['repo']]
    reason='工程文档关联背景；由审查者确定是否含独立承诺'
    if any('/web/docs/'+kind+'/' in '/'+low for kind in ['公司','行业','主题']) or '/web/docs/_moc_' in '/'+low:
        scope='excluded_business_content';reason='生成的公司/行业/主题投研正文，不是planning-with-files工程历史'
    elif any(s in low.split('/') for s in ['node_modules','.venv','venv','.pytest_cache']):
        scope='excluded_dependency_or_cache';reason='依赖库或临时测试缓存'
    else:
        if any(s in low.split('/') for s in ['plans','.planning','audit_review','review_audit','assurance','drills']) or Path(p).name.lower() in ['task_plan.md','findings.md','progress.md','planning_status.md'] or 'task_plan' in Path(p).name:
            scope='historical_plan_or_evidence';reason='规划/实施/审计/验收记录'
        if low.startswith('.review-zr407-20260818/company-wiki/'):
            owner='root_snapshot';reason+='；历史company-wiki快照，不等于当前部署'
    rows.append({**row,'scope':scope,'owner':owner,'scope_reason':reason,'semantic_review_status':'pending' if not scope.startswith('excluded') else 'out_of_scope'})
# Related evidence missed by filename heuristics: keep explicit record of expansion.
for repo,paths in {'filing-fetch':['e2e/E2E_DESIGN.md','references/contract-ownership.md','references/identity.md']}.items():
    root=PLAN.parents[2]/repo
    for rel in paths:
        path=root/rel;raw=path.read_bytes()
        rows.append({'repo':repo,'path':rel,'absolute_path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'lines':len(raw.decode('utf-8-sig').splitlines()),'scope':'engineering_context','owner':'filing','scope_reason':'人工补入实际端到端设计及身份/职责契约','semantic_review_status':'pending'})
(inv/'scope_manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
summary={}
for row in rows:
    key=row['repo']+'|'+row['scope'];summary.setdefault(key,{'files':0,'bytes':0});summary[key]['files']+=1;summary[key]['bytes']+=row['bytes']
(inv/'scope_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
snapshot=[]
for row in rows:
    if row['owner']!='root_snapshot':continue
    rel=row['path'].replace('\\','/').split('company-wiki/',1)[1]
    current=PLAN.parents[2]/'company-wiki'/rel
    old=Path(row['absolute_path']).read_text(encoding='utf-8-sig').splitlines()
    result={'snapshot':row['absolute_path'],'current':str(current),'source_sha256':row['sha256'],'scope':row['scope']}
    if current.is_file():
        raw=current.read_bytes();new=raw.decode('utf-8-sig').splitlines();result['current_sha256']=hashlib.sha256(raw).hexdigest()
        result['same_bytes']=result['current_sha256']==row['sha256']
        result['change_blocks']=[{'operation':op,'snapshot_start':i+1,'snapshot_end':j,'current_start':k+1,'current_end':l,'snapshot_lines':old[i:j],'current_lines':new[k:l]} for op,i,j,k,l in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes() if op!='equal']
    else:result['current_missing']=True
    snapshot.append(result)
(inv/'snapshot_differences.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2));print('snapshot_files',len(snapshot))
