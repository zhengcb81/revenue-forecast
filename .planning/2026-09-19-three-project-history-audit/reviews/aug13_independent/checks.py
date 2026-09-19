"""Read frozen plans and exact pure closure function; writes only this audit dir."""
from pathlib import Path
import ast, collections, hashlib, json, re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
CA = ROOT / 'audit_review/2026-08-13_three_repo_completion_rebaseline_plan'
ZR = ROOT / 'audit_review/2026-08-13_zijin_data_lake_remediation_plan'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
frozen = []
for d in (CA, ZR):
    for n, s in enumerate((d/'PLAN_MANIFEST.md').read_text(encoding='utf-8').splitlines(), 1):
        m = re.match(r'\| `([^`]+\.md)` \| ([\d,]+) \| `([0-9a-f]{64})`', s)
        if m:
            name, size, expected = m.groups(); p = d/name
            frozen.append(dict(manifest=str((d/'PLAN_MANIFEST.md').relative_to(ROOT)), line=n, path=str(p.relative_to(ROOT)), expected_hash=expected, actual_hash=sha(p), hash_match=sha(p)==expected, size_match=p.stat().st_size==int(size.replace(',',''))))
snapshot=[]; current=None
for n,s in enumerate((CA/'input_snapshot.md').read_text(encoding='utf-8').splitlines(),1):
    m=re.match(r'## `([^`]+)`',s)
    if m: current=ROOT/'audit_review'/m.group(1)
    m=re.match(r'\| `([^`]+\.md)` \| (\d+) \| `([0-9a-f]{64})`',s)
    if m:
        name,size,expected=m.groups();p=current/name
        snapshot.append(dict(line=n,path=str(p.relative_to(ROOT)),hash_match=sha(p)==expected,size_match=p.stat().st_size==int(size),expected_hash=expected,actual_hash=sha(p)))
reg=ROOT/'assurance/unified_completion/scenarios/scenario_registry.json'
payload=json.loads(reg.read_text(encoding='utf-8'))
evidence=[]
for sid,row in payload['scenarios'].items():
    p=ROOT/row['evidence_path']; e=json.loads(p.read_text(encoding='utf-8'))
    evidence.append(dict(id=sid,tier=row['tier'],status=row['status'],fixture_hash=row.get('fixture_hash'),oracle=row.get('oracle'),path=str(p.relative_to(ROOT)),sha256=sha(p),fields=sorted(e),test_file=e.get('test_file'),test_repo=e.get('repo'),summary=e.get('summary')))
src=ROOT/'assurance/unified_completion/uc/scenarios.py'
tree=ast.parse(src.read_text(encoding='utf-8')); node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='closure_report')
ns={'Any':object};exec(compile(ast.Module(body=[node],type_ignores=[]),str(src),'exec'),ns)
fake={'counts':{'unique_total':197},'scenarios':{sid:{'status':'passed'} for sid in payload['scenarios']}}
probe=ns['closure_report'](fake)
state=json.loads((ROOT/'assurance/unified_completion/state.json').read_text(encoding='utf-8'))
result={'scope':'read-only files; exact AST pure function, no import/runtime/worker/DB/network','manifest_files':frozen,'input_snapshot':snapshot,'manifest_match':sum(x['hash_match'] and x['size_match'] for x in frozen),'snapshot_match':sum(x['hash_match'] and x['size_match'] for x in snapshot),'scenario_registry_sha256':sha(reg),'scenario_statuses':dict(collections.Counter(r['status'] for r in payload['scenarios'].values())),'fixture_hash_missing':sum(r.get('fixture_hash') is None for r in payload['scenarios'].values()),'oracle_missing':sum(r.get('oracle') is None for r in payload['scenarios'].values()),'evidence_fields_counts':dict(collections.Counter(','.join(x['fields']) for x in evidence)),'evidence':evidence,'label_only_scenario_probe':{'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'function_lines':[node.lineno,node.end_lineno],'input_all_evidence_tier_hash_removed':True,'output':probe},'state_units':dict(collections.Counter(r['status'] for r in state['units'].values())),'ca306_next':state['units']['CA-306'].get('closure',{}).get('next'),'note':'A passed summary is not a proof of execution per required tier; this probe concerns uc.scenarios.closure_report only, not every gate.'}
(OUT/'checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('manifest_files','input_snapshot','evidence')},ensure_ascii=False,indent=2))
