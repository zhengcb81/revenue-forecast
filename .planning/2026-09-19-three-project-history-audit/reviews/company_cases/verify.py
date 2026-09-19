"""Read-only independent recheck of preserved company-audit evidence; no product import."""
from pathlib import Path
import hashlib,json,math
H=Path(__file__).resolve().parent; R=H.parents[3]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
A=R/'audit_review/2026-08-12_zijin_skill_run_audit'; B=R/'audit_review/2026-09-18_real_company_skill_audit'
x=read(A/'outputs/input_v1.json'); y=read(A/'outputs/draft_result.json'); receipt=read(A/'outputs/validation_receipt.json'); post=read(A/'outputs/post_run_checks.json')
p={r['parameter_id']:r['value'] for r in x['parameters']}; totals={}; diffs=[]
for sc in ('low','base','high'):
    annual={str(z):0 for z in x['forecast_years']}
    for s in x['segments']:
        v=p[s['base_revenue_parameter_id']]
        for yr,g in zip(x['forecast_years'],s['scenarios'][sc]['driver_parameter_ids']['growth_rate']):
            v*=1+p[g]; annual[str(yr)]+=v
    old=y['consolidated_forecast'][sc]
    diffs.extend(abs(v-old['annual_revenue'][yr]) for yr,v in annual.items())
    cagr=(annual['2030']/p[x['reported_total_revenue_parameter_id']])**.2-1
    totals[sc]={'annual':annual,'cagr':cagr,'cagr_matches':math.isclose(cagr,old['cagr'],abs_tol=1e-12)}
logs=[]
for run in sorted((B/'runs').glob('*/run.json')):
    obj=read(run)
    logs.append({'run':str(run.relative_to(R)),'actual_child_exit':obj['exit_code'],'timed_out':obj['timed_out'],'log_hashes_match':all(sha(run.parent/f)==v for f,v in obj['outputs'].items())})
files=[]
for d in read(B/'independent/raw_artifact_verification.json')['documents']:
    for role in ('locations','artifacts'):
        for f in d[role]:
            path=Path(f['path'])
            files.append({'path':str(path),'role':role,'exists':path.exists(),'same_as_historical_hash':path.exists() and sha(path)==f['sha256']})
for f in read(B/'independent/acquisition_aftercheck.json')['files']:
    path=Path(f['path']); side=Path(f['sidecar'])
    files.append({'path':str(path),'role':'new_raw','same_as_historical_hash':path.exists() and sha(path)==f['sha256'],'sidecar_hash_matches_raw':sha(path)==read(side)['content_sha256'] if 'content_sha256' in read(side) else None})
result={'boundary':'Preserved evidence hash and independent arithmetic, not recreated historical execution or new forecast; no raw/source/registry mutation.',
 'aug12':{'result_file_matches_post_receipt':sha(A/'outputs/draft_result.json')==post['checked_result_file_sha256'],'embedded_result_hash_matches_receipt':y['result_sha256']==receipt['result_sha256'],'input_counts':{k:len(x[k]) for k in ('sources','parameters','evidence_claims','segments')},'max_annual_recalc_error':max(diffs),'scenarios':totals,'probability_weighted_terminal':sum(x['scenario_probabilities'][s]*totals[s]['annual']['2030'] for s in totals),'registry_before_after_record_equal':receipt['publication_registry_before']==receipt['publication_registry_after'],'registry_limitation':'Historical adjacent snapshots only; no present replay of old engine.'},
 'sep18_logs':logs,'raw_and_artifacts':files}
(H/'independent_checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'logs':len(logs),'log_hashes_match':all(r['log_hashes_match'] for r in logs),'raw_artifact_files':len(files),'file_hashes_match':all(r.get('same_as_historical_hash') for r in files),'aug12_recalc_error':max(diffs),'aug12_file_hash_matches':result['aug12']['result_file_matches_post_receipt']}))
