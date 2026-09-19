"""Independent metadata recheck of final audit delivery; no product imports/writes."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,re
H=Path(__file__).resolve().parents[2]
master=json.loads((H/'master_coverage.json').read_text(encoding='utf-8'))
delivery=json.loads((H/'delivery_validation.json').read_text(encoding='utf-8'))
rows=master['files'];counts=Counter(x['status'] for x in rows)
keys=[(x['repo'],x['relative'].replace('\\','/').casefold()) for x in rows]
by=defaultdict(Counter)
for x in rows:by[x['repo']][x['status']]+=1
full=counts['semantic_reviewed']+counts['mapped_text_and_delta_reviewed']
mixed=counts['engineering_only_business_body_excluded']+counts['mapped_engineering_only_business_body_excluded']
excluded=counts['excluded_business_raw']
sources_without_review=[x['source_file'] for x in rows if not x.get('review_records')]
refs=[]
def walk(value):
    if isinstance(value,dict):
        if 'review_record' in value:
            p=value['review_record'];refs.append({'path':p,'exists':(H/p).exists()})
        for v in value.values():walk(v)
    elif isinstance(value,list):
        for v in value:walk(v)
walk(rows)
docs=['README.md','audit_report.md','implementation_plan.md']
links=[]
for name in docs:
    p=H/name
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if re.match(r'^[a-z]+://',target):continue
        links.append({'document':name,'target':target,'exists':(p.parent/target.split('#')[0]).exists()})
plan=(H/'implementation_plan.md').read_text(encoding='utf-8')
work_items=re.findall(r'^\*\*(I-\d{2})[：:]',plan,re.M)
stages=re.findall(r'^## ([0-8])\.',plan,re.M)
hash_checks=[]
for name,expected in delivery['final_document_hashes'].items():
    p=H/name;actual=hashlib.sha256(p.read_bytes()).hexdigest()
    hash_checks.append({'path':name,'actual_sha256':actual,'matches_delivery_validation':actual==expected})
out={'scope':'summary-to-record reconciliation, review-reference/markdown-link existence, final-document freshness; not re-execution of 769 historical documents or product tests',
 'selected_rows':len(rows),'unique_repo_path_keys':len(set(keys)),'counts':dict(counts),'by_repo':{k:dict(v) for k,v in by.items()},'full_md_paths':full,'mixed_engineering_only_paths':mixed,'excluded_raw_paths':excluded,'equation_holds':full+mixed+excluded==len(rows)==769,'summary_status_matches_rows':dict(counts)==master['summary']['status'],'delivery_summary_matches_master':delivery['coverage']==master['summary'],
 'missing_review_records':sources_without_review,'review_reference_count_including_repeats':len(refs),'missing_review_reference_paths':sorted({r['path'] for r in refs if not r['exists']}),
 'markdown_links':links,'all_markdown_links_exist':all(r['exists'] for r in links),'work_items':work_items,'work_item_ids_exact_00_to_17':work_items==[f'I-{i:02}' for i in range(18)],'stages':stages,'stage_ids_exact_0_to_8':stages==list('012345678'),
 'delivery_validation_errors':delivery['errors'],'delivery_final_document_hash_checks':hash_checks,
 'reviewed_document_hashes':{f:hashlib.sha256((H/f).read_bytes()).hexdigest() for f in docs+['master_coverage.json','delivery_validation.json']}}
(H/'reviews/second_wave/final_review_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k not in {'markdown_links','delivery_final_document_hash_checks','reviewed_document_hashes','by_repo','work_items'}},ensure_ascii=False))
print(json.dumps({'delivery_hash_mismatches':[r['path'] for r in hash_checks if not r['matches_delivery_validation']]},ensure_ascii=False))
