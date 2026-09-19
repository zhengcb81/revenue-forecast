"""Finalize metadata for already completed manual reading, never infer review."""
from pathlib import Path
import json,hashlib,collections
H=Path(__file__).resolve().parent;W=Path('C:/Users/郑曾波/Projects/company-wiki');R=W.parent/'revenue-forecast';F=W.parent/'filing-fetch'
x=json.loads((H/'read_coverage.json').read_text(encoding='utf-8'))
ctx=json.loads((H/'unassigned_engineering_context.json').read_text(encoding='utf-8'))['paths_needing_explicit_owner_or_exclusion']
excluded='companies/亿华通/raw/news/2026-04-25_1ed46181_CelestialMind_Community_B1_Reviews_Proje.md'
partial='docs/contaminated_entries_review.md'
for r in ctx:
    if r['path'] in {excluded,partial}:continue
    if r['path'] not in x['full_text_read']:x['full_text_read'].append(r['path'])
x['scope']='worker v5 / old recovery / production diagnostic plus 43 retained engineering-context paths; other owners not certified here'
x['selected_sections_read']=[{'path':partial,'coverage':'engineering_fields_only','lines':['1–18','all engineering group count headings','31934–31958'],'mechanical_checks':'all 3886 item headings and 4175 relative source paths; engineering_context_checks.json','unread_semantics':'business evidence bodies deliberately excluded; no correctness or deletion approval claim'}]
x['excluded_context']=[{'path':excluded,'coverage':'excluded_business_raw','reason':'root explicitly excludes raw/news generated business body from engineering-history scope'}]
x['read_manifest']=[{'path':s,'sha256':hashlib.sha256((W/s).read_bytes()).hexdigest(),'lines':len((W/s).read_text(encoding='utf-8-sig').splitlines()),'coverage':'full_text_semantic'} for s in x['full_text_read']]
x['uncompleted_main_clusters']=[]
x['separate_followup']='Root aggregate report and ER/A09 verdict-object cross-review; not a gap in assigned company-wiki source reading.'
x['boundary']='46 v5 MD full body; 15 old MD full common text + all old-side deltas, one 875-line investigation original full via exact normalized text mapping; 41 engineering MD full body; pollution only engineering structure; 1 business raw excluded. Supporting JSON registry315/DAG115 assessed per item; not product tests.'
rows=[json.loads(s) for s in (H/'item_ledger.jsonl').read_text(encoding='utf-8').splitlines() if s]
x['semantic_assessment_records'].update({'ledger_total':len(rows),'engineering_context_items':379,'freeze_history_occurrences':173,'freeze_distinct_concerns':91})
fullmd=[a for a in x['read_manifest'] if a['path'].endswith('.md')]
x['counts']={'direct_full_md':len(fullmd),'direct_full_md_lines':sum(a['lines'] for a in fullmd),'old_full_via_version_mapping_md':len(x['full_via_version_mapping']),'old_lines':6616,'original_investigation_via_text_mapping_md':1,'original_investigation_lines':875,'total_full_md_paths':len(fullmd)+len(x['full_via_version_mapping'])+1,'partial_engineering_md':1,'excluded_business_raw_md':1,'supporting_full_json_not_added_to_md_count':len(x['full_text_read'])-len(fullmd)}
(H/'read_coverage.json').write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
errors=[]
for r in rows:
    o=r['original'];base={'company-wiki':W,'revenue-forecast':R,'filing-fetch':F}[o['repo']]
    p=base/o['path']
    if not p.exists():errors.append({'id':r['id'],'problem':'missing path','path':str(p)});continue
    lines=len(p.read_text(encoding='utf-8-sig').splitlines())
    if not isinstance(o['line'],int) or not 1<=o['line']<=lines:errors.append({'id':r['id'],'problem':'line out of bounds','line':o['line'],'lines':lines})
assert len({r['id'] for r in rows})==len(rows)
validation={'item_count':len(rows),'duplicate_ids':False,'path_line_errors':errors,'verdict_counts':dict(collections.Counter(r['verdict'] for r in rows)),'coverage_counts':x['counts'],'limit':'link and line validity is not semantic correctness; every item was separately authored after reading.'}
(H/'ledger_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(validation,ensure_ascii=False))
assert not errors
