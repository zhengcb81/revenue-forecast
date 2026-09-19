"""Persist completed manual reading and exact version line mappings. No product writes."""
from pathlib import Path
import json, hashlib, difflib
H=Path(__file__).resolve().parent
W=Path('C:/Users/郑曾波/Projects/company-wiki')
B='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/'
p=H/'item_ledger.jsonl'; rows=[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s]
for r in rows:
    if r['id'] in {'WIKI-PR-055','WIKI-PR-061','WIKI-PR-070','WIKI-PR-077','WIKI-PR-092'}:
        r['verdict']='insufficient_evidence'
        r['current_independent_evidence']=r['current_independent_evidence'].replace('当前具体反例：','处置部分成立，但相关语义关闭仍不足：')
        r['assessment_limit']='这些具体处置有设计改进；不把另一个残留冲突等同于原处置完全无效，也不因未实施把规划判为产品缺陷。'
    if r['id']=='WIKI-V5-SEM-04':
        r['current_independent_evidence']=r['current_independent_evidence'].replace(':39及143',':40及146').replace(':157(PR-089)',':154(PR-089)')
    if r['id']=='WIKI-V5-SEM-05':
        r['current_independent_evidence']=r['current_independent_evidence'].replace(':880附近',':875–879')
    if r['id']=='WIKI-V5-SEM-07':r['original']['line']=277
p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
c=H/'read_coverage.json';x=json.loads(c.read_text(encoding='utf-8'))
for n in ['baseline/history/plan_review_revision.v4.md','baseline/history/progress.v4.md','baseline/history/v4-freeze-integrity-incident-2026-09-03.md','baseline/investigation/worker-investigation-2026-08-20.md']:
    assert (W/B/n).exists(),n
    if B+n not in x['full_text_read']:x['full_text_read'].append(B+n)
x['selected_sections_read']=[r for r in x['selected_sections_read'] if r['path'] not in x['full_text_read']]
current_md={p.relative_to(W).as_posix() for p in (W/B).rglob('*.md')}
assert len(current_md)==46
assert current_md.issubset(set(x['full_text_read'])), sorted(current_md-set(x['full_text_read']))
old=json.loads((H/'old_version_mapping.json').read_text(encoding='utf-8'))
for r in old:
    a=(W/r['old_path']).read_text(encoding='utf-8-sig').splitlines()
    b=(W/r['baseline_path']).read_text(encoding='utf-8-sig').splitlines()
    ops=difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes()
    r['line_mapping']=[{'operation':tag,'old_start':i+1,'old_end':j,'baseline_start':k+1,'baseline_end':l,
        'review_basis':'full baseline semantic reading' if tag=='equal' else 'all old-side delta text independently read; additions also read in full baseline'} for tag,i,j,k,l in ops]
    r['semantic_read_method']='full corresponding baseline plus every old-side deletion/replacement in saved unified diff'
    r['coverage']='full_via_version_mapping'
    r['independent_pass_inheritance']=False
    assert sum(o['old_end']-o['old_start']+1 for o in r['line_mapping'])==len(a)
(H/'old_version_mapping.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
x['full_via_version_mapping']=[{'path':r['old_path'],'mapping':'old_version_mapping.json','coverage':r['coverage'],'semantic_read_method':r['semantic_read_method']} for r in old]
investigation=W/'docs/worker-investigation-2026-08-20.md'
base=W/B/'baseline/investigation/worker-investigation-2026-08-20.md'
x['investigation_duplicate']={'path':investigation.relative_to(W).as_posix(),'baseline_path':base.relative_to(W).as_posix(),'byte_equal':investigation.read_bytes()==base.read_bytes(),'text_equal':investigation.read_text(encoding='utf-8-sig').splitlines()==base.read_text(encoding='utf-8-sig').splitlines(),'sha256':hashlib.sha256(investigation.read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(base.read_bytes()).hexdigest()}
assert x['investigation_duplicate']['text_equal']
x['read_manifest']=[{'path':s,'sha256':hashlib.sha256((W/s).read_bytes()).hexdigest(),'lines':len((W/s).read_text(encoding='utf-8-sig').splitlines()),'coverage':'full_text_semantic'} for s in x['full_text_read']]
x['uncompleted_main_clusters']=['individual freeze closure claims ledger consolidation; root report cross-review']
x['boundary']='46 v5 MD full body; 15 old MD full common text plus all semantic deltas; no future worker implementation or production acceptance claimed. Separate JSON registry/DAG structural and per-item design review; other schemas are supporting references, not blanket schema semantic approval.'
c.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'v5 MD complete={len(current_md)}, old MD complete-via-mapping={len(old)}, old lines={sum(r["old_lines"] for r in old)}')
