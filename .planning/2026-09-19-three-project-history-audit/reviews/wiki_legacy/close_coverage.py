from pathlib import Path
import json,collections,hashlib,csv
P=Path(__file__).resolve().parent;ROOT=Path(r'C:/Users/郑曾波/Projects/company-wiki')
scope=json.loads((P/'scope.json').read_text(encoding='utf-8'));rows=[];struct=[]
for prefix in ['special','cw','wr','root_logs','recovery','context','business']:
 rows.extend(json.loads(l) for l in (P/(prefix+'_item_ledger.jsonl')).read_text(encoding='utf-8').splitlines())
 q=P/(prefix+'_structural_exclusions.json')
 if q.exists():struct.extend(json.loads(q.read_text(encoding='utf-8')))
key=lambda x:(x['relative'],x['line_start'],x['line_end'])
expected={key(x) for x in scope['blocks'] if not x['relative'].startswith('docs/archive/')};seen=collections.Counter(key(x) for x in rows+struct)
missing=sorted(expected-set(seen));extras=sorted(set(seen)-expected);duplicates=[dict(key=k,count=v) for k,v in seen.items() if v>1]
files=[]
for f in scope['files']:
 if f.startswith('docs/archive/'):continue
 p=ROOT/f;b=[x for x in scope['blocks'] if x['relative']==f]
 files.append(dict(relative=f,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_hash_matches_inventory=all(x['file_sha256']==hashlib.sha256(p.read_bytes()).hexdigest() for x in b),blocks=len(b),reviewed=sum(x['relative']==f for x in rows),structural=sum(x['relative']==f for x in struct)))
result=dict(files=files,file_count=len(files),reviewed_occurrences=len(rows),structural_occurrences=len(struct),expected_blocks=len(expected),pending=missing,extra=extras,duplicates=duplicates,verdicts=dict(collections.Counter(x['verdict'] for x in rows)),handoff=dict(archive17='../wiki_archive/coverage.json',note='Root independently reviews all17 archives; excluded from this partition, not silently dropped'),scope_limitations=['1066 business log events audited for telemetry/lineage, not each financial fact','3886 contaminated business entries engineering counts/current exact-absence only; see separate supplemental ledger','No production worker/DB/download/write actions; historical health snapshots are not current health','Original versions retained; identical recovery text maps canonical semantic cases but old status is never replaced by newer PASS'])
(P/'item_ledger.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
(P/'coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'structural_exclusions.json').write_text(json.dumps(struct,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['files','scope_limitations']},ensure_ascii=False))
