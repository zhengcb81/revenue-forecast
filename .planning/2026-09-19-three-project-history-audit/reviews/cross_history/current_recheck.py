"""Recheck selected old diagnostics against current bytes, using a pure planner only."""
from pathlib import Path
from types import SimpleNamespace
import hashlib, importlib.util, json, sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RF = HERE.parents[3]
CW = RF.parent / 'company-wiki'
snapshot = CW / 'docs/plans/painpoint-outcome-audit-2026-09-05/source-evidence-snapshot.json'
raw = json.loads(snapshot.read_text(encoding='utf-8-sig'))
comparisons = []
for row in raw['files']:
    p = Path(row['path'])
    sha = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    comparisons.append({'path': str(p), 'old_sha256': row['sha256'], 'current_sha256': sha,
                        'same_bytes': sha == row['sha256'], 'exists': p.is_file()})
path = CW / 'src/company_wiki/source_catalog/gap_plan.py'
spec = importlib.util.spec_from_file_location('audit_current_gap_plan', path)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
def candidate(accession, filed, url='https://example.invalid/filing.pdf'):
    return SimpleNamespace(fiscal_year=2025, provider_document_id=accession,
        filing_date=filed, source_url=url, amended=False, capture_ready=True)
old, new = candidate('z-old', '2026-03-01'), candidate('a-new', '2026-04-01')
def plan(local, remote):
    return mod.build_gap_plan(request_id='history-audit-synthetic', as_of_date='2026-09-19',
        document_kind='annual', entity='synthetic-audit-company', market='US',
        local_handles=local, remote_candidates=remote)
def observation(p):
    return {'reuse': [x.provider_document_id for x in p.reuse],
        'missing': [x.provider_document_id for x in p.missing],
        'newer_revision': [x.provider_document_id for x in p.newer_revision],
        'not_published': p.not_published, 'gap_hash': p.gap_hash}
a = plan([], [new])
b = plan([], [candidate('a-new','2026-05-01','https://example.invalid/replaced.pdf')])
probes = {
    'newer_date_lower_id': {'expected_newer': ['a-new'], 'actual': observation(plan([old],[old,new]))},
    'older_only_remote': {'expected_newer': [], 'actual': observation(plan([new],[old]))},
    'missing_same_period_two_revisions': {'expected': 'select known latest revision or explicit ambiguity', 'actual': observation(plan([],[old,new]))},
    'url_and_date_changed_same_gap_hash': {'expected_equal': False, 'actual_equal': a.gap_hash == b.gap_hash,
        'first': observation(a), 'changed': observation(b)}
}
out = {'scope': 'Independent pure-function synthetic probe; no provider, DB, scanner, worker, scheduler or prune executed.',
    'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'source_snapshot_comparison': comparisons, 'current_gap_probes': probes}
(HERE / 'current_recheck.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'same_old_bytes':sum(x['same_bytes'] for x in comparisons), 'total':len(comparisons),
    'changed':[x['path'] for x in comparisons if not x['same_bytes']], 'probes': probes}, ensure_ascii=False))
