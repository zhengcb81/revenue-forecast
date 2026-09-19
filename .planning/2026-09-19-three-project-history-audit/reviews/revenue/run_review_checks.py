"""Read-only product checks; all outputs and pytest scratch stay in this review."""
from pathlib import Path
from datetime import datetime,timezone
import subprocess,sys,os,json,hashlib,time
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
files=['tests/test_models.py','tests/test_model_registry_contract.py','tests/test_model_integration_bounds.py','tests/test_model_extensions.py','tests/test_model_economic_guardrails.py','tests/test_buy_side_accuracy.py','tests/test_lifecycle_forecasts.py']
command=[sys.executable,'-m','pytest',*files,'-q','-p','no:cacheprovider','--basetemp='+str(OUT/'scratch/model-tests')]
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONIOENCODING']='utf-8'
start=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
result=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(OUT/'logs/model_tests.stdout.txt').write_bytes(result.stdout)
(OUT/'logs/model_tests.stderr.txt').write_bytes(result.stderr)
manifest={'started_at':start,'duration_seconds':time.monotonic()-clock,'command':command,'cwd':str(ROOT),'exit_code':result.returncode,'stdout':'logs/model_tests.stdout.txt','stderr':'logs/model_tests.stderr.txt','test_files_sha256':{x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in files},'scope':'Synthetic formula/domain/time/bridge/backtest-contract/lifecycle checks; no real-company forecast accuracy certification.'}
(OUT/'logs/model_tests.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(result.stdout.decode('utf8'));print(result.stderr.decode('utf8'));print('exit_code',result.returncode)
