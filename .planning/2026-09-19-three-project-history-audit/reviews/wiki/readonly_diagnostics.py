"""Read-only historical byte checks and one audited config-doctor invocation.
No scan/store/worker entry is invoked; output is restricted to this directory.
"""
import collections
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
REPO = Path('C:/Users/郑曾波/Projects/company-wiki')
V5 = REPO/'docs/plans/source-catalog-worker-recovery-v5-2026-09-03'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    p = subprocess.run(['git', *args], cwd=REPO, capture_output=True)
    return {'args':list(args),'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8','replace'),'stderr':p.stderr.decode('utf-8','replace')}

manifest=json.loads((V5/'plan_manifest.v5.json').read_text(encoding='utf-8'))
records=[]
for e in manifest['normative_files']:
    path=V5/e['path']
    raw=path.read_bytes()
    records.append({'path':e['path'],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'hash_match':hashlib.sha256(raw).hexdigest()==e['sha256'],'size_match':len(raw)==e['size_bytes'],'equivalence_claim':e['equivalence']})
guards=[REPO/'config/source_catalog.yaml', REPO/'.source_catalog/runtime_policy.json', REPO/'.source_catalog/worker_control.json']
before={str(p):sha(p) for p in guards}
env=dict(os.environ)
env['PYTHONDONTWRITEBYTECODE']='1'
env['PYTHONIOENCODING']='utf-8'
env['PYTHONPATH']=str(REPO/'src')
cmd=[sys.executable,'-B',str(REPO/'scripts/config_doctor.py')]
p=subprocess.run(cmd,cwd=REPO,env=env,capture_output=True,timeout=30)
after={str(p):sha(p) for p in guards}
payload={'observed_at':datetime.now(timezone.utc).isoformat(),'scope':'independent byte verification; audited readonly config doctor using repository src; not a scan/activation/product acceptance','manifest_sha256':sha(V5/'plan_manifest.v5.json'),'normative_records':records,'normative_count':len(records),'normative_all_match':all(r['hash_match'] and r['size_match'] for r in records),'equivalence_claim_counts':dict(collections.Counter(r['equivalence_claim'] for r in records)),'doctor':{'command':cmd,'environment_overrides':{'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(REPO/'src')},'exit_code':p.returncode,'stdout':p.stdout.decode('utf-8','replace'),'stderr':p.stderr.decode('utf-8','replace')},'guards_before':before,'guards_after':after,'guard_bytes_unchanged':before==after,'current_head':git('rev-parse','HEAD'),'gp002_historical_config':git('show','9809127:config/source_catalog.yaml'),'gp002_historical_test':git('show','9809127:tests/contract/test_gp002_scan_v2_wiring.py')}
(HERE/'readonly_diagnostics.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'normative_count':len(records),'normative_all_match':payload['normative_all_match'],'doctor':payload['doctor'],'guard_bytes_unchanged':before==after},ensure_ascii=True))
