from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]/'filing-fetch'
commands={
 'pure_probes':[sys.executable,'-X','utf8','-B',str(HERE/'pure_probes.py')],
 'installed_surface':[sys.executable,'-B','tools/sync_installs_b3.py','--check'],
 'receipt_git_history_trusted':['git','-c','safe.directory='+str(REPO),'log','--format=%h %ad %s','--date=iso-strict','--','assurance/fc/FC-903/11_implementer_receipt.json','assurance/fc/FC-903/12_reviewer_receipt.json'],
 'hook_selection_trusted':['git','-c','safe.directory='+str(REPO),'config','--get','core.hooksPath'],
}
for name,cmd in commands.items():
 if len(sys.argv)>1 and name not in sys.argv[1:]: continue
 p=subprocess.run(cmd,cwd=REPO,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1'),capture_output=True,timeout=90)
 (HERE/'tests'/f'{name}.stdout.txt').write_bytes(p.stdout)
 (HERE/'tests'/f'{name}.stderr.txt').write_bytes(p.stderr)
 (HERE/'tests'/f'{name}.run.json').write_text(json.dumps({'command':cmd,'cwd':str(REPO),'exit_code':p.returncode,'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()},ensure_ascii=False,indent=2),encoding='utf-8')
 print(name,p.returncode,p.stdout.decode('utf-8',errors='replace')[:350])
