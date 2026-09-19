"""Preserve every fully read source paragraph and join authored semantic reviews.

This is a join, not an automatic reviewer. Manual review lives in the 117+145
unit reasons, 93 checklist groups, 31 model reasons, 103 document-context
reviews and explicit clause reviews. Repeated statements may share reasons;
source positions, revisions and original wording are never dropped.
"""
import hashlib,json,re
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
def read(name):return [json.loads(s) for s in (OUT/name).read_text(encoding='utf8').splitlines() if s]
manifest=json.loads((OUT/'source_read_manifest.json').read_text(encoding='utf8'))
units={x['item_id']:x for x in read('item_ledger.jsonl')}
checks=read('checklist_ledger.jsonl')
models=read('model_ledger.jsonl')
clauses=read('prose_clause_ledger.jsonl')+read('deep_clause_ledger.jsonl')
docs={}
for x in read('r4_document_ledger.jsonl'):
    file=x.get('source_file',x.get('file'));docs[file]=x
for x in read('additional_document_ledger.jsonl'):docs[x['source_file']]=x
for x in read('rf_fc_document_ledger.jsonl'):docs[x['source_file']]=x
for f,d in docs.items():
    d.setdefault('review_id','RF-DOC-'+hashlib.sha256(f.encode()).hexdigest()[:12])
    d.setdefault('reason',d.get('review_reason'))
    assert d.get('reason'),(f,d)

def blocks(lines):
    start=None
    for n,l in enumerate(lines+[''],1):
        if l.strip() and start is None:start=n
        if not l.strip() and start is not None:
            yield start,n-1,'\n'.join(lines[start-1:n-1]);start=None

def structural(body):
    # Only unambiguous navigation is excluded. Technical headings are claims,
    # even if their following paragraph repeats the same obligation.
    lines=body.splitlines()
    return all(re.fullmatch(r'\s*[-_*|: ]+\s*',l) or
        bool(re.fullmatch(r'#{1,6}\s*(?:目录|阶段总览|范围|验证|证据|结论|附录|变更记录|错误记录|Errors Encountered|非目标|验收|实施步骤|测试命令)\s*',l))
        for l in lines)

rows=[];file_rows=[];doc_group_rows=[]
for entry in manifest:
    f=entry['path']
    if entry['owner']!='history_revenue':continue
    assert entry['full_read_state']=='full_read',f
    p=ROOT/f;raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();lines=raw.decode('utf-8-sig').splitlines()
    own_card=f.startswith('assurance/unified_completion/receipts/')
    own_unit=f.split('/')[3] if own_card else None
    assert own_card or f in docs,('unreviewed prose file',f)
    d=docs.get(f)
    if d:
        doc_group_rows.append(dict(item_id=d['review_id'],source_file=f,source_file_sha256=sha,conclusion=d['conclusion'],reason=d['reason'],scope='Reviewer read the complete document, compared each technical assertion with its stated historical/accepted scope and current successor evidence. Shared contextual reasons do not certify every historic command/count as a fresh current run.',current_evidence=['item_ledger.jsonl','checklist_ledger.jsonl','model_ledger.jsonl','prose_clause_ledger.jsonl','deep_clause_ledger.jsonl','r4_document_ledger.jsonl','additional_document_ledger.jsonl','logs/']))
    frows=[]
    for begin,end,body in blocks(lines):
        is_structure=structural(body)
        ids=sorted({s for s in re.findall(r'\b(?:CA-\d{3}|ZR-\d{3,4}|FC-\d{3,4}|WU-[\w.]+)\b',body) if s in units})
        if own_unit:ids=sorted(set(ids)|{own_unit})
        caseids=[c['item_id'] for c in clauses if c['source_file']==f and any(begin<=n<=end for n in c.get('source_lines',[c.get('source_line',0)]))]
        checkids=[c.get('item_id',c.get('checklist_id')) for c in checks if c['source_file'].replace('\\','/')==f and begin<=c.get('source_line',c.get('line',0))<=end]
        modelids=[c['item_id'] for c in models if c['source_file'].replace('\\','/')==f and begin<=c['source_line']<=end]
        bindings=[]
        if not is_structure:
            if d:bindings.append({'semantic_item_id':d['review_id'],'review_conclusion':d['conclusion'],'review_reason':d['reason'],'scope':'Document-context comparison. More specific linked unit/leaf/clause takes precedence; historical facts are not asserted current defects.'})
            for uid in ids:
                u=units[uid];bindings.append({'semantic_item_id':uid,'review_conclusion':u['conclusion'],'implementation_conclusion':u.get('implementation_conclusion'),'review_reason':u['reason'],'scope':'Same logical obligation repeated here; original definition and all leaf criteria retained in item_ledger. A unit-level failure does not mean every subtest failed.'})
            for c in clauses:
                if c['item_id'] in caseids:bindings.append({'semantic_item_id':c['item_id'],'review_conclusion':c['conclusion'],'review_reason':c['reason'],'scope':'Explicitly split technical assertion.'})
            for c in checks+models:
                if c['item_id'] in checkids+modelids:bindings.append({'semantic_item_id':c['item_id'],'review_conclusion':c['conclusion'],'review_reason':c['reason'],'accuracy_conclusion':c.get('accuracy_conclusion'),'scope':c.get('assessment_scope',c.get('scope','Manual leaf assessment'))})
            assert bindings,(f,begin)
        item={'occurrence_id':f'RF-SRC-{len(rows)+1:06}', 'source_file':f,'line_start':begin,'line_end':end,'frozen_inventory_sha256':entry['sha256'],'reviewed_current_sha256':sha,'text_sha256':hashlib.sha256(body.encode()).hexdigest(),'original_text':body,'classification':'structural_navigation_excluded' if is_structure else 'reviewed_semantic_occurrence','review_bindings':bindings,'explicit_clause_ids':caseids,'checklist_leaf_ids':[s for s in checkids if s],'review_complete':True,'current_product_pass':False,'review_complete_meaning':'Source assertion independently assessed, including insufficient_evidence/not_deployed/superseded outcomes; not a product success certification.'}
        rows.append(item);frows.append(item)
    file_rows.append({'source_file':f,'frozen_inventory_sha256':entry['sha256'],'read_sha256':sha,'frozen_lines':entry['lines'],'read_lines':len(lines),'full_text_read':True,'semantic_audit_complete':True,'semantic_occurrences':sum(r['classification']=='reviewed_semantic_occurrence' for r in frows),'structural_occurrences':sum(r['classification']=='structural_navigation_excluded' for r in frows),'coverage_mechanism':'Complete full-text reading; manual semantic groups joined to every paragraph preserving exact text/hash/lines. No test or PASS count used to infer verdict.','review_evidence':['source_semantic_ledger.jsonl','document_semantic_groups.jsonl','item_ledger.jsonl','checklist_ledger.jsonl','prose_clause_ledger.jsonl','deep_clause_ledger.jsonl'],'concurrent_delta':sha!=entry['sha256']})
    entry.update(semantic_audit_complete=True,reviewed_sha256=sha,reviewed_lines=len(lines),semantic_evidence='source_semantic_ledger.jsonl',semantic_occurrence_count=file_rows[-1]['semantic_occurrences'])

(OUT/'source_semantic_ledger.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf8')
(OUT/'document_semantic_groups.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in doc_group_rows),encoding='utf8')
(OUT/'source_semantic_file_manifest.json').write_text(json.dumps(file_rows,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'source_read_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
stats={'own_files_full_read_and_semantically_linked':len(file_rows),'source_occurrences':len(rows),'occurrence_kinds':dict(Counter(r['classification'] for r in rows)),'contextual_manual_groups':len(doc_group_rows),'explicit_prose_clauses':len(read('prose_clause_ledger.jsonl')),'deep_clauses':len(read('deep_clause_ledger.jsonl')),'concurrent_delta_files':[r['source_file'] for r in file_rows if r['concurrent_delta']],'unreviewed_owned_files':[],'other_owner_files':len(manifest)-len(file_rows),'meaning':'Source-review completeness, not all clauses implemented/PASS. Root and filing agents separately close their 84 source files; original397 inventory hash is preserved.'}
(OUT/'source_semantic_coverage.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(stats,ensure_ascii=False))

# These 29 separately assigned wiki FC records are a cross-project evidence
# supplement. They are not added to RF397 or counted a second time globally.
extra=[]
for d in read('wiki_fc_document_ledger.jsonl'):
    p=Path(d['source_file']);raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    for start,end,body in blocks(raw.decode('utf-8-sig').splitlines()):
        nav=structural(body);unit=units.get(d['related_unit'])
        extra.append({'occurrence_id':f'RF-WIKIFC-{len(extra)+1:05}','source_file':p.as_posix(),'line_start':start,'line_end':end,'frozen_read_sha256':d['sha256'],'reviewed_current_sha256':sha,'original_text':body,'text_sha256':hashlib.sha256(body.encode()).hexdigest(),'classification':'structural_navigation_excluded' if nav else 'reviewed_semantic_occurrence','historical_state':d['historical_state'],'review_conclusion':None if nav else d['conclusion'],'current_implementation_conclusion':None if nav else d['current_implementation_conclusion'],'review_reason':'Navigation only' if nav else d['reason'],'unit_id':d['related_unit'],'unit_current_reason':None if nav or not unit else unit['reason'],'evidence_scope':d['evidence_scope'],'current_product_pass':False})
(OUT/'wiki_fc_source_blocks.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in extra),encoding='utf8')
print('additional29 wiki FC source occurrences',len(extra))
