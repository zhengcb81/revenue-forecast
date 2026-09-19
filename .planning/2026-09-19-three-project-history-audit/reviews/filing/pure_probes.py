"""Independent audit probes: imported code + temp files, no production services."""
from pathlib import Path
import concurrent.futures, hashlib, importlib.util, json, os, sys, tempfile, threading
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4] / 'filing-fetch'
sys.path.insert(0, str(REPO / 'scripts'))
import fetch_filing as ff
from filing_contracts import validate_request
spec = importlib.util.spec_from_file_location('planverify', REPO / 'tools' / 'verify_plan_claims.py')
pv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pv)
results = {}

# Busy returned near deadline: call consumes time, then stale remaining permits excess sleep.
clock = [0.0]
def fail_near_deadline(**kwargs):
    clock[0] += 9.0
    raise ff.FilingFetchError('simulated busy after 9 seconds', code='catalog_busy')
with patch.object(ff.time, 'monotonic', side_effect=lambda:clock[0]), patch.object(ff.time, 'sleep', side_effect=lambda t:clock.__setitem__(0, clock[0]+t)), patch.object(ff.random, 'uniform', return_value=0), patch.object(ff, '_run_company_wiki_json', side_effect=fail_near_deadline):
    try:
        ff._run_company_wiki_json_retry(command=[], root=HERE, action='resolve', deadline=10.0)
    except ff.FilingFetchError as exc:
        results['deadline'] = {'budget':10.0, 'elapsed':clock[0], 'error_code':exc.code, 'message':str(exc)}
with patch.object(ff.time, 'monotonic', return_value=100.0):
    scope = ff.PausedWorkerScope(root=HERE, command_prefix=[], enabled=True, graceful_timeout_seconds=5, resume_wait_seconds=5, deadline=90.0)
    results['worker_remaining_after_deadline'] = scope._remaining()

# Logical concurrency: force both genuine reads before either genuine write.
# Serialize physical writes so the result tests read-modify-write, not OS rename timing.
with tempfile.TemporaryDirectory(dir=HERE / 'tests') as tmp:
    root = Path(tmp)
    barrier, write_lock = threading.Barrier(2), threading.Lock()
    original_read, original_write = ff._prune_pause_entries, ff._write_pause_entries
    ids, ids_lock = {}, threading.Lock()
    def fake_pid():
        with ids_lock:
            return ids.setdefault(threading.get_ident(), 10000 + len(ids))
    def synchronized_read(root):
        snapshot = original_read(root)
        barrier.wait(timeout=10)
        return snapshot
    def serialized_write(root, entries):
        with write_lock:
            return original_write(root, entries)
    def register():
        s = ff.PausedWorkerScope(root=root, command_prefix=[], enabled=True, graceful_timeout_seconds=5, resume_wait_seconds=5, deadline=90)
        return {'pid':fake_pid(), 'first':s._register(joined=False)}
    with patch.object(ff, '_prune_pause_entries', side_effect=synchronized_read), patch.object(ff, '_write_pause_entries', side_effect=serialized_write), patch.object(ff.os, 'getpid', side_effect=fake_pid):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            registered = list(pool.map(lambda _:register(), range(2)))
    results['refcount_interleaving'] = {'registrations':registered, 'retained_entries':ff._read_pause_entries(root)}

plan = '## Phase 1 — 状态：completed\n- [x] one\n## Phase 2 — 状态：completed\n- [x] two'
progress = '# 2026-09-19\nPhase 1 pytest passed\nPhase 2 only mentioned; no command or result for this phase.'
results['plan_unbound_evidence_probe'] = dict(zip(('problems','reports'), pv.verify(plan,progress)))
results['actual_plan_recognized_phases'] = [x['number'] for x in pv.parse_plan((REPO/'task_plan.md').read_text(encoding='utf-8'))]

receipt_dir=REPO/'assurance'/'fc'/'FC-903'
imp=(receipt_dir/'11_implementer_receipt.json').read_bytes()
rev=json.loads((receipt_dir/'12_reviewer_receipt.json').read_text(encoding='utf-8'))
results['fc903_binding']={'expected':rev['implementer_receipt_sha256'], 'actual':hashlib.sha256(imp).hexdigest(), 'lf_normalized':hashlib.sha256(imp.replace(b'\r\n',b'\n')).hexdigest()}
results['installed_copies'] = []
for location in ['.agents','.codex','.claude']:
    install=Path.home()/location/'skills'/'filing-fetch'
    for relative in ['SKILL.md','scripts/fetch_filing.py','scripts/filing_contracts.py','config/company_wiki.json']:
        row={'install':str(install), 'relative':relative, 'source_sha256':hashlib.sha256((REPO/relative).read_bytes()).hexdigest()}
        try:
            row['installed_sha256']=hashlib.sha256((install/relative).read_bytes()).hexdigest()
            row['matches']=row['installed_sha256']==row['source_sha256']
        except OSError as exc:
            row['error']=str(exc)
        results['installed_copies'].append(row)
(HERE/'tests'/'pure_probes.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
