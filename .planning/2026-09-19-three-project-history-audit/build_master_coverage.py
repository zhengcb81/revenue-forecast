"""Join independently reviewed sources without treating enumeration as semantic review."""
from pathlib import Path
import collections,csv,difflib,hashlib,json
P=Path(__file__).resolve().parent; R=P.parents[1]; W=R.parent/'company-wiki'; F=R.parent/'filing-fetch'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def key(p):return str(Path(p).resolve()).casefold()
scope=read(P/'inventory/scope_manifest.json'); selected=[z for z in scope if z['scope']!='excluded_business_content']; bypath={key(z['absolute_path']):z for z in selected}; coverage=collections.defaultdict(list)
def add(path,manifest,status,sha=None,detail=None):
 coverage[key(path)].append({'review_record':str(manifest.relative_to(P)),'status':status,'reviewed_sha256':sha,'detail':detail})
for name in ('cross_history','early_revenue','wiki_archive','aug09_plans','company_cases','wiki_legacy','aug13_independent','final_context'):
 p=P/'reviews'/name/'coverage.json'
 if not p.exists():continue
 obj=read(p); rows=obj if isinstance(obj,list) else obj.get('files',[])
 for z in rows:
  path=z.get('source_file') or z.get('path')
  if not path or not Path(path).is_absolute(): path=str((W if name=='wiki_archive' else R)/(z.get('file') or z.get('relative') or path))
  add(path,p,'semantic_reviewed',z.get('sha256'),z.get('read_status') or z.get('semantic_cases'))
p=P/'reviews/filing/item_ledger.jsonl'
for z in (json.loads(s) for s in p.read_text(encoding='utf8').splitlines()):
 if not any(v['review_record']==str(p.relative_to(P)) for v in coverage[key(z['source_file'])]):add(z['source_file'],p,'semantic_reviewed',z['file_sha256'])
p=P/'reviews/revenue/source_read_manifest.json'
for z in read(p):
 if z['full_read_state']=='full_read':add(R/z['path'],p,'semantic_reviewed' if z.get('semantic_audit_complete') else 'full_read_semantic_join_pending',z.get('reviewed_sha256') or z['sha256'],z.get('semantic_evidence'))
p=P/'reviews/revenue/wiki_fc_document_ledger.jsonl'
for z in (json.loads(s) for s in p.read_text(encoding='utf8').splitlines()):add(z['source_file'],p,'semantic_reviewed',z.get('sha256'))
p=P/'reviews/wiki/read_coverage.json'; obj=read(p)
for z in obj['read_manifest']:
 add(W/z['path'],p,'semantic_reviewed',z['sha256'],z['coverage'])
for z in obj.get('full_via_version_mapping',[]):
 path=W/z['path']; add(path,p,'semantic_reviewed',hashlib.sha256(path.read_bytes()).hexdigest(),z)
z=obj['investigation_duplicate'];add(W/z['path'],p,'semantic_reviewed',z['sha256'],z)
poll=W/'docs/contaminated_entries_review.md'
add(poll,p,'engineering_only_business_body_excluded',hashlib.sha256(poll.read_bytes()).hexdigest(),'Engineering markers/structure/current paths checked; historical company facts excluded from this engineering-history audit. See wiki context and wiki_legacy supplemental ledgers.')
for z in obj.get('excluded_context',[]):add(W/z['path'],p,'excluded_business_raw',None,z['reason'])
# Snapshot text coverage is shared only after byte/line equality and manual delta review.
snapshots=[]
for z in selected:
 path=Path(z['absolute_path']); rel=z['path'].replace('\\','/')
 if rel.startswith('.review-zr407-20260818/company-wiki/'):
  source=W/rel.split('/company-wiki/',1)[1]
 elif rel.startswith('.review-zr407-20260818/filing-fetch/'):
  source=F/rel.split('/filing-fetch/',1)[1]
 else:continue
 a=path.read_text(encoding='utf-8-sig').splitlines();b=source.read_text(encoding='utf-8-sig').splitlines()
 blocks=[{'operation':op,'snapshot_range':[i+1,j],'canonical_range':[k+1,l],'snapshot_text':a[i:j],'canonical_text':b[k:l]} for op,i,j,k,l in difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes() if op!='equal']
 delta_judgment=None
 if not blocks:delta_judgment='Exact line text (possible EOL-only bytes) shares text judgment; no runtime PASS inheritance.'
 elif source.name=='evidence-span-v1.md':delta_judgment='Manual delta reviewed: old v1 did not include homepage_identity_contradiction; new wording defines PDF/sidecar title/publisher conflict as extraction-review signal, not investment judgment. Neither wording proves implementation. Scope preserved.'
 elif source.parent==F and source.name in ('task_plan.md','findings.md','progress.md'):delta_judgment='Manual delta reviewed: later status/retirement header only; old state retained historically. No retroactive closure or deployment PASS.'
 base=coverage.get(key(source),[])
 ready=any(v['status'] in ('semantic_reviewed','engineering_only_business_body_excluded','excluded_business_raw') for v in base)
 status='mapped_text_and_delta_reviewed' if ready and delta_judgment else 'snapshot_pending'
 if any(v['status']=='engineering_only_business_body_excluded' for v in base):status='mapped_engineering_only_business_body_excluded'
 add(path,P/'snapshot_review.json',status,z['sha256'],{'canonical':str(source),'judgment':delta_judgment,'mapped_records':base})
 snapshots.append({'snapshot':str(path),'source':str(source),'snapshot_sha256':z['sha256'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'blocks':blocks,'verdict':'historical_only','judgment':delta_judgment,'status':status})
(P/'snapshot_review.json').write_text(json.dumps(snapshots,ensure_ascii=False,indent=2),encoding='utf8')
rows=[]
for z in selected:
 path=Path(z['absolute_path']); matches=coverage.get(key(path),[]); states={v['status'] for v in matches}
 status=next((v for v in ('semantic_reviewed','mapped_text_and_delta_reviewed','engineering_only_business_body_excluded','mapped_engineering_only_business_body_excluded','excluded_business_raw','full_read_semantic_join_pending','snapshot_pending') if v in states),'pending')
 sha=hashlib.sha256(path.read_bytes()).hexdigest(); valid=[v for v in matches if v['reviewed_sha256']==sha]
 if status not in ('pending','excluded_business_raw') and not valid:status='hash_changed_recheck_required'
 rows.append(dict(repo=z['repo'],relative=z['path'],source_file=str(path),original_scope=z['scope'],inventory_sha256=z['sha256'],current_sha256=sha,hash_changed_since_inventory=sha!=z['sha256'],status=status,review_records=matches))
summary={'initial_selected_paths':len(selected),'status':dict(collections.Counter(z['status'] for z in rows)),'by_repo':{repo:dict(collections.Counter(z['status'] for z in rows if z['repo']==repo)) for repo in sorted({z['repo'] for z in rows})},'pending_files':[{'path':z['source_file'],'status':z['status']} for z in rows if z['status'] in ('pending','snapshot_pending','hash_changed_recheck_required','full_read_semantic_join_pending')],'boundary':'A review verdict is not product PASS. Text-equivalent versions share semantic judgments only. Business content excluded explicitly; no full runtime replay implied.'}
(P/'master_coverage.json').write_text(json.dumps({'summary':summary,'files':rows},ensure_ascii=False,indent=2),encoding='utf8')
with (P/'master_coverage.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['repo','relative','source_file','original_scope','inventory_sha256','current_sha256','hash_changed_since_inventory','status','review_records']);writer.writeheader();writer.writerows({**z,'review_records':'; '.join(v['review_record'] for v in z['review_records'])} for z in rows)
print(json.dumps({k:v for k,v in summary.items() if k!='pending_files'},ensure_ascii=False));print('Remaining',len(summary['pending_files']))
