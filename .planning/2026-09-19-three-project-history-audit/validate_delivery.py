"""Delivery integrity checks; never certifies product behavior or research accuracy."""
from pathlib import Path
import datetime,hashlib,json,re
P=Path(__file__).resolve().parent
cov=json.loads((P/'master_coverage.json').read_text(encoding='utf8'));errors=[];changes=[]
if cov['summary']['pending_files']:errors.append('Master coverage still has pending records')
for r in cov['files']:
 p=Path(r['source_file']);h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=r['current_sha256']:changes.append({'path':str(p),'covered_sha256':r['current_sha256'],'current_sha256':h})
if changes:errors.append('Sources changed since latest coverage join')
docs=['README.md','task_plan.md','findings.md','progress.md','audit_report.md','implementation_plan.md',
 'reviews/revenue/review.md','reviews/filing/review.md','reviews/wiki/review.md','reviews/wiki_legacy/review.md','reviews/aug13_independent/review.md',
 'reviews/wiki/cross_review.md','reviews/second_wave/filing_cross_review.md','reviews/second_wave/root_cross_review.md',
 'reviews/second_wave/final_review.md','reviews/revenue/final_plan_review.md',
 'execution_v2/README.md','execution_v2/START_HERE.md','execution_v2/dispatch.md',
 'execution_v2/revision_review.md','execution_v2/independent_dry_read.md','execution_v2/validation.json']
links=[];hashes={}
for rel in docs:
 p=P/rel
 if not p.exists():errors.append('Missing final document '+rel);continue
 raw=p.read_bytes();hashes[rel]=hashlib.sha256(raw).hexdigest()
 for target in re.findall(r'(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)',raw.decode('utf-8-sig')):
  if '://' in target or target.startswith('#'):continue
  q=target.strip('<>').split('#',1)[0];dst=(p.parent/q).resolve();ok=dst.exists()
  links.append(dict(document=rel,target=target,exists=ok))
  if not ok:errors.append('Broken link '+rel+' -> '+target)
ledgers=[]
for p in sorted((P/'reviews').rglob('*ledger.jsonl')):
 count=0
 try:
  for s in p.read_text(encoding='utf-8-sig').splitlines():
   if s.strip():json.loads(s);count+=1
 except Exception as exc:errors.append('Invalid JSONL '+str(p)+': '+str(exc))
 ledgers.append(dict(path=str(p.relative_to(P)),records=count,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Delivery readability, links, JSON integrity, source hash freshness and explicit coverage. Not semantic/product re-certification.',
 'coverage':cov['summary'],'source_hash_changes':changes,'links':links,'final_document_hashes':hashes,'ledger_files':ledgers,'errors':errors}
(P/'delivery_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'covered_paths':len(cov['files']),'links':len(links),'ledgers':len(ledgers),'errors':errors},ensure_ascii=False))
raise SystemExit(1 if errors else 0)
