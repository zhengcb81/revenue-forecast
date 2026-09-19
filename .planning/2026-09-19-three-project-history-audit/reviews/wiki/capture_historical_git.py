"""Read historical Git blobs with a command-local ownership exception.

Does not change Git config, worktree, branch or source files. Keeps the earlier
failed lookup in readonly_diagnostics.json intact.
"""
import json,subprocess,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;W=Path('C:/Users/郑曾波/Projects/company-wiki')
out={'scope':'read-only git; -c safe.directory only applies to this subprocess; earlier exit128 record is retained','commands':[]}
for args in [['rev-parse','9809127'],['show','9809127:config/source_catalog.yaml'],['show','9809127:tests/contract/test_gp002_scan_v2_wiring.py']]:
    cmd=['git','-c',f'safe.directory={W.as_posix()}','-C',str(W),*args]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    out['commands'].append({'command':cmd,'exit_code':r.returncode,'stdout':r.stdout.decode('utf-8','replace'),'stderr':r.stderr.decode('utf-8','replace'),'stdout_sha256':hashlib.sha256(r.stdout).hexdigest()})
(H/'historical_git_readonly.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{'args':r['command'][-2:],'exit_code':r['exit_code'],'stdout_sha256':r['stdout_sha256'],'stdout_chars':len(r['stdout'])} for r in out['commands']],ensure_ascii=False))
assert all(r['exit_code']==0 for r in out['commands'])
