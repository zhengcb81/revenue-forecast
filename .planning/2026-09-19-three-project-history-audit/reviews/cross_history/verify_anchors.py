"""Independent byte checks only; no project validator, network or database."""
from pathlib import Path
import hashlib, json, difflib

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1]
RF = PLAN.parents[1]
PROJECTS = RF.parent
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
m = json.loads((RF / 'assurance/unified_completion/manifests/plan_inputs.json').read_text(encoding='utf-8-sig'))
items = m['entries'] + (list(m.get('sources', {}).values()) if isinstance(m.get('sources'),dict) else m.get('sources', []))
checks = []
for item in items:
    if not isinstance(item, dict) or 'rel_path' not in item:
        checks.append({'unhandled_schema': item})
        continue
    p = RF / item['rel_path']
    checks.append({'relative': item['rel_path'], 'exists': p.is_file(),
        'expected': item.get('sha256'), 'actual': digest(p) if p.is_file() else None,
        'matches': p.is_file() and digest(p) == item.get('sha256')})
snapshots = []
scope = json.loads((PLAN / 'inventory/scope_manifest.json').read_text(encoding='utf-8'))
for row in scope:
    rel = row['path'].replace('\\','/')
    prefix = '.review-zr407-20260818/filing-fetch/'
    if row['repo'] != 'revenue-forecast' or not rel.startswith(prefix):
        continue
    snap, current = Path(row['absolute_path']), PROJECTS / 'filing-fetch' / rel[len(prefix):]
    a, b = snap.read_text(encoding='utf-8-sig').splitlines(), current.read_text(encoding='utf-8-sig').splitlines()
    changes = [dict(tag=t, snapshot_start=i+1, snapshot_end=j, current_start=k+1, current_end=l,
                    snapshot_lines=a[i:j], current_lines=b[k:l])
               for t,i,j,k,l in difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes() if t != 'equal']
    snapshots.append({'snapshot': str(snap), 'current': str(current),
        'snapshot_sha256': digest(snap), 'current_sha256': digest(current),
        'same_lines': a == b, 'changes': changes})
result = {'manifest_sha256': digest(RF / 'assurance/unified_completion/manifests/plan_inputs.json'),
          'raw_bindings': len(checks), 'unique_paths': len({x.get('relative') for x in checks}),
          'checks': checks, 'filing_snapshots': snapshots,
          'scope': 'Byte integrity and exact text deltas only; not a product test or a historical execution replay.'}
(HERE / 'anchor_checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'bindings':len(checks), 'unique':result['unique_paths'],
    'bad':[x for x in checks if not x.get('matches')], 'snapshots':len(snapshots),
    'deltas':[{'path':x['snapshot'], 'blocks':len(x['changes'])} for x in snapshots]}, ensure_ascii=False))
