"""Audit the review's joins and source coverage, not the product being reviewed."""
import hashlib,json
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
def read(name):return [json.loads(s) for s in (OUT/name).read_text(encoding='utf8').splitlines() if s]
units=read('item_ledger.jsonl');checks=read('checklist_ledger.jsonl');models=read('model_ledger.jsonl')
cases=read('prose_clause_ledger.jsonl')+read('deep_clause_ledger.jsonl')+read('document_semantic_groups.jsonl')
assert len(units)==262 and len(checks)==776 and len(models)==31
ids=[x['item_id'] for x in units+checks+models+cases]
assert len(ids)==len(set(ids)),[i for i,n in Counter(ids).items() if n>1]
known=set(ids);rows=read('source_semantic_ledger.jsonl');files=json.loads((OUT/'source_semantic_file_manifest.json').read_text(encoding='utf8'))
missing=[];drift=[];filecounts={}
for f in files:
    p=ROOT/f['source_file'];raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    if sha!=f['read_sha256']:drift.append(f['source_file'])
    lines=raw.decode('utf-8-sig').splitlines();seen=set();hits=[r for r in rows if r['source_file']==f['source_file']]
    for r in hits:
        segment='\n'.join(lines[r['line_start']-1:r['line_end']])
        assert segment==r['original_text'],(f['source_file'],r['line_start'])
        assert hashlib.sha256(segment.encode()).hexdigest()==r['text_sha256']
        for b in r['review_bindings']:
            assert b['semantic_item_id'] in known,b
            assert b['review_reason'] and b['review_conclusion']
        assert r['classification']=='structural_navigation_excluded' or r['review_bindings'],r
        seen.update(range(r['line_start'],r['line_end']+1))
    absent=[n for n,l in enumerate(lines,1) if l.strip() and n not in seen]
    if absent:missing.append({'file':f['source_file'],'lines':absent})
    filecounts[f['source_file']]=len(hits)
assert not missing,missing
assert not drift,drift
assert len(files)==313
wiki=read('wiki_fc_source_blocks.jsonl');assert len({r['source_file'] for r in wiki})==29
report={'verification_scope':'Only review coverage, source text/hash and semantic-reference integrity; not a fresh product PASS','own_full_read_semantic_files':len(files),'source_occurrences':len(rows),'semantic_occurrences':sum(r['classification']=='reviewed_semantic_occurrence' for r in rows),'structural_navigation_occurrences':sum(r['classification']=='structural_navigation_excluded' for r in rows),'missing_nonblank_lines':missing,'source_changed_after_review':drift,'unique_semantic_record_ids':len(known),'unit_count':len(units),'checklist_count':len(checks),'model_count':len(models),'wiki_extra_documents':29,'wiki_extra_occurrences':len(wiki),'result':'PASS_FOR_REVIEW_JOIN_ONLY'}
(OUT/'review_join_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
coverage=json.loads((OUT/'coverage.json').read_text(encoding='utf8'))
coverage.update(own_full_read_and_semantically_reviewed_documents=313,other_owner_documents=84,own_unreviewed_documents=0,source_occurrences=len(rows),semantic_occurrences=report['semantic_occurrences'],structural_navigation_occurrences=report['structural_navigation_occurrences'],document_semantic_groups=119,explicit_prose_clauses=61,deep_clauses=27,caution='Review completeness, not all product promises fulfilled. Repeated logical obligations share manually authored reasons, with every source occurrence preserved. Other84 files are independently reviewed by root/filing. Three concurrent R4 source changes retain frozen/current hashes.')
(OUT/'coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
