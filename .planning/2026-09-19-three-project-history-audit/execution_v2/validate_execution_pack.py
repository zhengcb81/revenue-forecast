"""Plan structure integrity only; never grants implementation readiness or acceptance."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json,re
P=Path(__file__).resolve().parent
errors=[]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=read(P/'dispatch.json');cards=d['cards'];by={c['id']:c for c in cards}
if len(by)!=len(cards):errors.append('duplicate card IDs')
parents={f'I-{i:02}' for i in range(18)}
if set(c['parent'] for c in cards)!=parents:errors.append('parent coverage mismatch')
if any(c['status']!='planned' for c in cards):errors.append('Unexecuted card has non-planned status')
for c in cards:
    for field in ['id','parent','title','document','depends_on','effective_depends_on']:
        if field not in c:errors.append(c['id']+' missing '+field)
    if not (P/c['document']).exists():errors.append('missing card document '+c['document'])
    elif c['id'] not in (P/c['document']).read_text(encoding='utf-8-sig'):errors.append('card id absent from document '+c['id'])
    for dep in c['effective_depends_on']:
        if dep not in by:errors.append(c['id']+' unknown dependency '+dep)
    source=(P/c['source_document']).read_text(encoding='utf-8-sig')
    own=[x for x in cards if x['source_document']==c['source_document']]
    headings=[]
    for other in own:
        match=re.search(r'^#{2,3} '+re.escape(other['id'])+r'(?=\s|[·—:：]).*$',source,re.M)
        if match:headings.append((match.start(),other['id']))
    headings.sort()
    positions=[i for i,x in enumerate(headings) if x[1]==c['id']]
    if len(positions)!=1:errors.append('cannot uniquely bind source heading '+c['id'])
    else:
        i=positions[0];start=headings[i][0];end=headings[i+1][0] if i+1<len(headings) else len(source)
        section=source[start:end].strip()+'\n'
        expected=hashlib.sha256(section.encode('utf-8')).hexdigest()
        if expected!=c['source_section_sha256']:errors.append('stale extracted card source '+c['id'])
        clone=(P/c['document']).read_text(encoding='utf-8-sig').split('\n\n',1)[-1]
        if clone!=section:errors.append('single-card body differs from source '+c['id'])
order=[];active=[];done=set()
def visit(cid):
    if cid in done:return
    if cid in active:
        errors.append('dependency cycle: '+' -> '.join(active[active.index(cid):]+[cid]));return
    active.append(cid)
    for dep in by[cid]['effective_depends_on']:
        if dep in by:visit(dep)
    active.pop();done.add(cid);order.append(cid)
for cid in by:visit(cid)
old=[json.loads(x) for x in (P.parent/'reviews/revenue/model_ledger.jsonl').read_text(encoding='utf-8-sig').splitlines() if x.strip()]
expected_models={x['item_id'].removeprefix('RF-MODEL-') for x in old}
models=[x for x in cards if x['parent']=='I-10' and (x.get('model') or x.get('model_name'))]
actual_models={x.get('model',x.get('model_name')) for x in models}
if len(models)!=31 or actual_models!=expected_models:errors.append('31-model identity coverage differs from audit ledger')
links=[];hashes={}
for p in sorted(P.glob('*.md')):
    hashes[p.name]=sha(p)
    for target in re.findall(r'(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)',p.read_text(encoding='utf-8-sig')):
        if '://' in target or target.startswith('#'):continue
        target=target.strip('<>').split('#',1)[0]
        filesystem_target=re.sub(r':\d+$','',target)
        exists=(p.parent/filesystem_target).exists()
        links.append({'source':p.name,'target':target,'exists':exists})
        if not exists:errors.append('broken link '+p.name+' -> '+target)
samples=read(P/'sample_manifest.json')
if len(samples['samples'])!=3:errors.append('triplet sample count not 3')
if any(not s['planning_time_raw_hash_matches'] for s in samples['samples']):errors.append('sample raw hash mismatch at planning extraction')
if len(samples['unbound_live_samples'])!=5:errors.append('unbound live sample scope unexpectedly changed')
RF=P.parents[2]
roots={'revenue':RF,'revenue-forecast':RF,'wiki':RF.parent/'company-wiki','company-wiki':RF.parent/'company-wiki','filing':RF.parent/'filing-fetch','filing-fetch':RF.parent/'filing-fetch'}
source_bindings=[]
for filename,anchor_key in [('filing_cards.json','source_anchors'),('wiki_cards.json','anchors')]:
    payload=read(P/filename)
    for c in payload['cards']:
        for a in c.get(anchor_key,[]):
            path=Path(a['absolute_path']) if a.get('absolute_path') else roots[a['repo']]/a['path']
            exists=path.is_file();actual=sha(path) if exists else None
            ok=exists and actual==a['sha256']
            source_bindings.append({'card':c['id'],'path':str(path),'planned_sha256':a['sha256'],'current_sha256':actual,'matches':ok})
            if not ok:errors.append('source binding changed or missing: '+str(path))
for rel,expected in read(P/'model_cards.json')['source_snapshots'].items():
    path=RF/rel;actual=sha(path) if path.is_file() else None
    source_bindings.append({'card':'I-10','path':str(path),'planned_sha256':expected,'current_sha256':actual,'matches':actual==expected})
    if actual!=expected:errors.append('model source binding changed or missing '+str(path))
counts=Counter(c['parent'] for c in cards)
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'scope':'Documentation identity/coverage/dependency DAG/relative-link/JSON and planned-status checks only. No product execution, model arithmetic proof, or weaker-model implementation trial.',
     'cards':len(cards),'parents':dict(sorted(counts.items())),'models':len(models),
     'missing_models':sorted(expected_models-actual_models),'unexpected_models':sorted(str(x) for x in actual_models-expected_models),
     'topological_order':order,'links':links,'document_hashes':hashes,
     'source_bindings':source_bindings,
     'data_hashes':{p.name:sha(p) for p in P.glob('*.json') if p.name not in ['validation.json']},
     'sample_identity_count':len(samples['samples']),'unbound_live_samples':len(samples['unbound_live_samples']),
     'product_cards_executed':0,'weaker_model_implementation_trial':'not_run','errors':errors}
(P/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={k:out[k] for k in ['cards','parents','models','unbound_live_samples','product_cards_executed','weaker_model_implementation_trial']}
summary.update(error_count=len(errors),first_errors=errors[:10])
print(json.dumps(summary,ensure_ascii=False))
raise SystemExit(1 if errors else 0)
