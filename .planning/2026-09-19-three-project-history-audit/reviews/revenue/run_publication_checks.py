from pathlib import Path
from datetime import datetime,timezone
import subprocess,sys,os,json,hashlib,time
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONIOENCODING']='utf8'
files=['tests/test_publication_pipeline.py','tests/test_publication_registry.py','tests/test_attestation.py','tests/test_zr710_publication_txn.py']
jobs=[('publication_tests',[sys.executable,'-m','pytest',*files,'-q','-p','no:cacheprovider','--basetemp='+str(OUT/'scratch/publication-tests')]),('publication_probe',[sys.executable,str(OUT/'probe_publication.py')])]
for label,command in jobs:
 start=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
 result=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 (OUT/f'logs/{label}.stdout.txt').write_bytes(result.stdout);(OUT/f'logs/{label}.stderr.txt').write_bytes(result.stderr)
 manifest={'started_at':start,'duration_seconds':time.monotonic()-clock,'command':command,'cwd':str(ROOT),'exit_code':result.returncode,'stdout':f'logs/{label}.stdout.txt','stderr':f'logs/{label}.stderr.txt','files_sha256':{x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in files},'scope':'Isolated publication regression and synthetic attestation counterexample; no real catalog or source data writes.'}
 (OUT/f'logs/{label}.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 print(label,result.returncode,result.stdout.decode('utf8'),result.stderr.decode('utf8'))
