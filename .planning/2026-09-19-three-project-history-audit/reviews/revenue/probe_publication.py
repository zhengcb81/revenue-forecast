"""Audit-only synthetic probe; no real publication or source catalog touched."""
import json,os,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
os.environ['REVENUE_PUBLICATION_REGISTRY']=str(OUT/'scratch/publication-probe-registry.jsonl')
os.environ['REVENUE_ATTESTATION_PROVIDER']=str(Path(__file__).resolve())
from revenue_core import run_forecast,attestation_capability
from revenue_report import validate_forecast_output
from test_recognition_bridge import forecast_document
result=run_forecast(forecast_document())
validate_forecast_output(result)
print(json.dumps({'synthetic_only':True,'provider_setting_is_this_python_source_file':True,'provider_invocation_protocol_implemented':False,'capability':attestation_capability(),'publication_attestation':result['publication_receipt']['attestation_status'],'source_receipts': [{'signature_present':'signature' in s['capture']['host_receipt'],'issuer':s['capture']['host_receipt']['issuer']} for s in result['sources']],'validator':'accepted','scope':'This proves host_signed label does not require actual source signatures or provider invocation; not evidence that underlying company facts are forged.'},ensure_ascii=False,indent=2))

from unittest.mock import patch
import revenue_forecast
probe_root=OUT/'scratch/publication-failure-probe';probe_root.mkdir(exist_ok=True)
input_path=probe_root/'input.json';input_path.write_text(json.dumps(forecast_document()),encoding='utf8')
registry=probe_root/'registrations.jsonl';os.environ['REVENUE_PUBLICATION_REGISTRY']=str(registry)
output_path=probe_root/'out.json'
before=len(registry.read_text(encoding='utf8').splitlines()) if registry.exists() else 0
with patch.object(sys,'argv',['revenue_forecast.py',str(input_path),'--output',str(output_path)]),patch.object(revenue_forecast,'_atomic_write_text',side_effect=OSError('audit synthetic output failure')):
 rc=revenue_forecast.main()
after=len(registry.read_text(encoding='utf8').splitlines()) if registry.exists() else 0
print(json.dumps({'case':'registry_committed_then_output_write_fails','synthetic_only':True,'cli_exit_code':rc,'registry_entries_added':after-before,'output_exists':output_path.exists(),'scope':'Per-file atomicity exists; this case contradicts whole-publication transaction/no-orphan claim.'},ensure_ascii=False,indent=2))
