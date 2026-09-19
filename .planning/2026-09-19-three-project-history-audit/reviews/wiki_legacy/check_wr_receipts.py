"""Read-only receipt integrity, sample arithmetic and capture-script timing audit."""
from pathlib import Path
import json,hashlib,ast,types,datetime
P=Path(__file__).resolve().parent;R=Path(r'C:/Users/郑曾波/Projects/company-wiki');G=R/'artifacts/gates/source-catalog-bg'
names=['wr-1-7-revalidation-20260729-attempt-0002.json','wr-4-5-7-attempt-0001.json','wr-8-9-final-acceptance-20260729.json','wr-10-7-final-acceptance-20260731.json','wr-10-9-step6-acceptance-20260802.json','wr-10-13-final-pilot-acceptance-20260802.json','wr-10-13-slow-canary-acceptance-20260802.json','wr-10-13-fingerprint-terminal-acceptance-20260802.json','bg5-apply-result-20260728T195200Z.json','cw228c-phase2-attempt-0001.json']
result={'scope':'historical archived receipts only; no DB/current worker/network calls','receipts':[],'pilots':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def walk_refs(d,jpath='$'):
 out=[]
 if isinstance(d,dict):
  for k,v in d.items():
   if isinstance(v,str) and v.startswith('artifacts') and v.endswith(('.json','.log','.md')):
    q=R/v;expected=d.get(k+'_sha256') or (d.get('sha256') if k in ['path','receipt'] else None)
    out.append(dict(json_path=jpath+'.'+k,path=v,exists=q.is_file(),expected=expected,actual=sha(q) if q.is_file() else None,match=(sha(q)==expected) if expected and q.is_file() else None))
   out+=walk_refs(v,jpath+'.'+k)
 elif isinstance(d,list):
  for i,v in enumerate(d):out+=walk_refs(v,f'{jpath}[{i}]')
 return out
for n in names:
 p=G/n;d=json.loads(p.read_text(encoding='utf-8-sig'));result['receipts'].append(dict(file=str(p),sha256=sha(p),references=walk_refs(d)))
for n in ['wr-6-pilot-30m-20260729-attempt-0002.json','wr-10-7-clean-pilot-30m-20260731.json','wr-10-13-final-pilot-30m-20260802.json']:
 p=G/n;d=json.loads(p.read_text(encoding='utf-8-sig'));s=d['samples'];calc={
 'sample_count':len(s),'observed_sample_window_minutes':(s[-1]['timestamp']-s[0]['timestamp'])/60,
 'pending_delta':s[0]['markdown_pending']-s[-1]['markdown_pending'],
 'normalized_delta':s[-1]['markdown_completed']-s[0]['markdown_completed'],
 'artifact_delta':s[-1]['artifact_rows']-s[0]['artifact_rows'],
 'runtime_all_running':all(x['runtime_state']=='running' for x in s),
 'production_worker_min':min(x['production_workers'] for x in s),
 'production_worker_max':max(x['production_workers'] for x in s),
 'foreign_worker_max':max(x['foreign_workers'] for x in s),
 'pytest_temp_worker_max':max(x['pytest_temp_workers'] for x in s),
 'raw_heartbeat_stale_count':sum((x['heartbeat_age'] or 0)>d['heartbeat_stale_threshold_seconds'] for x in s),
 'raw_heartbeat_max_seconds':max(x['heartbeat_age'] or 0 for x in s),
 'code_match_all':all(x.get('code_match') is True for x in s) if 'code_match' in s[0] else None,
 }
 result['pilots'].append(dict(file=str(p),sha256=sha(p),calculated=calc,reported_summary={k:v for k,v in d.items() if k not in ['samples','raw_samples','stockwiki_files','last_good_sample']},interpretation='Summary duration includes collection overhead and DB quick_check; do not call the entire duration continuously sampled. Delta/progress reflects first-last sample.'))
p=G/'wr-10-9-step6-login-20260802.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
result['step6_archived_capture']=dict(file=str(p),sha256=sha(p),capture_started_at=d['capture_started_at'],capture_ended_at=d['capture_ended_at'],snapshots=d['snapshots'],latest_launcher_events=d['launcher_events_tail'][-2:],interpretation='Linked archived capture contains one tag0 snapshot with null worker_status. Later findings24 says three repaired snapshots, but no replacement receipt is linked in acceptance. Starting/child_started supports historical new session only.')
# Execute exact AST main with every external function replaced and in-memory Path.
source=R/'scripts/wr109_step6_capture.py';tree=ast.parse(source.read_text(encoding='utf-8'));main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
elapsed=[];tags=[];saved={};clock=[0]
class Parser:
 def add_argument(self,*a,**kw):pass
 def parse_args(self):return types.SimpleNamespace(json_out='audit-memory',snapshots=['30','60','120'])
class MemoryPath:
 def __init__(self,p):self.p=p
 @property
 def parent(self):return self
 def mkdir(self,*a,**k):pass
 def write_text(self,v,**k):saved['payload']=json.loads(v)
def sleep(s):clock[0]+=s;elapsed.append(s)
def snap(tag):tags.append(dict(tag=tag,cumulative_sleep_seconds=clock[0]));return {'tag':tag}
ns=dict(argparse=types.SimpleNamespace(ArgumentParser=Parser),datetime=datetime,time=types.SimpleNamespace(sleep=sleep),Path=MemoryPath,json=json,Any=object,_registry_run_item=lambda:{},_launcher_events_tail=lambda:[],_process_events_tail=lambda:[],_control_log_tail=lambda:[],_snapshot=snap,print=lambda *a,**k:None)
exec(compile(ast.Module(body=[main],type_ignores=[]),str(source),'exec'),ns);exitcode=ns['main']()
result['capture_schedule_pure_probe']=dict(source=str(source),sha256=sha(source),exit_code=exitcode,waits=elapsed,snapshots=tags,external_operations=0,scope='Exact current main AST; dependencies fake; no sleeping, real commands, DB or file writes from captured main')
(P/'wr_receipt_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'receipts':len(names),'pilots':len(result['pilots']),'reference_hash_checks':sum(x['expected'] is not None for r in result['receipts'] for x in r['references']),'reference_mismatches':[x for r in result['receipts'] for x in r['references'] if x['match'] is False],'schedule':tags},ensure_ascii=False))
