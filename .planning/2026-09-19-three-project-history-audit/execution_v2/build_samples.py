"""Extract existing audit identities into plan-only inputs. No provider/product imports."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
RF=P.parents[2]
OLD=RF/'audit_review/2026-09-18_real_company_skill_audit'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
acq=read(OLD/'independent/acquisition_aftercheck.json')
raw=read(OLD/'independent/raw_artifact_verification.json')
samples=[]
for sid,req,market,year in [('CN-ZIJIN-2025','zijin_2025.json','CN',2025),('HK-XIAOMI-2025','xiaomi_2025.json','HK',2025),('US-MSFT-2026','msft_2026.json','US',2026)]:
    if market=='CN':
        candidates=[d for d in raw['documents'] if d['company']=='Zijin' and '2025' in d['title']]
        assert len(candidates)==1, candidates
        d=candidates[0]
        loc=next(x for x in d['locations'] if x['root_id']=='company_raw')
        info={'document_id':d['document_id'],'path':loc['path'],'sha256':loc['sha256'],'byte_size':loc['byte_size'],'original_observation':'raw reusable; review/artifact readiness incomplete','evidence':'independent/raw_artifact_verification.json'}
    else:
        candidates=[f for f in acq['files'] if f['metadata']['market']==market and f['metadata']['fiscal_year']==year]
        assert len(candidates)==1,candidates
        f=candidates[0];m=f['metadata']
        info={'path':f['path'],'sidecar':f['sidecar'],'sha256':f['sha256'],'byte_size':f['size'],'provider':m['provider'],'provider_document_id':m['provider_document_id'],'original_observation':'raw saved; scan/registration failed','evidence':'independent/acquisition_aftercheck.json'}
    p=Path(info['path']);current=sha(p) if p.exists() else None
    sidecar=Path(info.get('sidecar',info['path']+'.source.json'))
    if not sidecar.is_file():raise FileNotFoundError('Required existing sample sidecar: '+str(sidecar))
    info['sidecar']=str(sidecar)
    info['planning_time_sidecar_sha256']=sha(sidecar)
    samples.append({'id':sid,'market':market,'fiscal_year':year,'request':read(OLD/'requests'/req),'request_path':str(OLD/'requests'/req),'request_sha256':sha(OLD/'requests'/req),**info,'planning_time_raw_sha256':current,'planning_time_raw_hash_matches':current==info['sha256'],'current_catalog_review_status':'not rechecked in this documentation revision','execution_status':'planned','required_recheck':'I-07-A checks current bytes and period; no production mutation'})
out={'scope':'Existing historical audit identities plus read-only raw hash check; no fresh filing or financial verification. Unbound entries block only their required live qualification.',
     'inputs':[{'path':str(OLD/x),'sha256':sha(OLD/x)} for x in ['independent/acquisition_aftercheck.json','independent/raw_artifact_verification.json']],
     'samples':samples,'unbound_live_samples':[{'id':x,'status':'unbound','rule':'Reviewer selects and freezes identity/period/as_of/provider/raw-state and required authority before execution; never delete production copies to manufacture absence.'} for x in ['CN-NEW-MISSING','HK-NEW-MISSING','US-NEW-MISSING','EXTERNAL-ONLY','HELDOUT-COMPANY']],
     'capture_rule':'Preserve actual captured_at; historical as_of and current retrieval date must not be forged. Unsupported reconstruction is blocked; a current-as_of run is a separate case.'}
(P/'sample_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'samples':len(samples),'raw_hash_matches':sum(x['planning_time_raw_hash_matches'] for x in samples),'unbound_live':len(out['unbound_live_samples'])},ensure_ascii=False))
