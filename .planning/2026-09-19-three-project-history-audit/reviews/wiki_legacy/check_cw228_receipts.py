"""Read historical receipt files; never run recorded commands or write production."""
import hashlib,importlib.util,json,tempfile,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=Path('C:/Users/郑曾波/Projects/company-wiki')
path=ROOT/'tests/helpers/cw228_receipt.py'
spec=importlib.util.spec_from_file_location('cw228_audit_helper',path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
receipt_dir=ROOT/'artifacts/gates/cw-2.28'
index=json.loads((receipt_dir/'receipt-index.json').read_text(encoding='utf-8'))
out={'helper_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'schema_sha256':hashlib.sha256(helper.SCHEMA_PATH.read_bytes()).hexdigest(),'production_operations':False,'index_checks':[],'receipt_checks':[],'chain_errors':helper.validate_chain(receipt_dir)}
for key,entry in index['phases'].items():
 p=receipt_dir/entry['path'];actual=hashlib.sha256(p.read_bytes()).hexdigest();data=json.loads(p.read_text(encoding='utf-8'))
 out['index_checks'].append({'phase':key,'path':str(p),'expected':entry['sha256'],'actual':actual,'match':actual==entry['sha256']})
 out['receipt_checks'].append({'phase':key,'recorded_status':data['status'],'errors':helper.validate_receipt(data),'empty_product_hashes':not data.get('product_file_hashes_after'),'commands_without_stdout_hash':sum(c.get('stdout_sha256') is None for c in data.get('command_results',[])),'commands':len(data.get('command_results',[]))})
with tempfile.TemporaryDirectory(dir=HERE,prefix='isolated_receipt_chain_') as tmp:
 td=Path(tmp);base=json.loads((receipt_dir/'phase-0-attempt-0001.json').read_text(encoding='utf-8'))
 base['project_root']=str(td);base['command_results']=[];base['invariant_results']=[]
 prior=copy.deepcopy(base);prior['phase']=0;prior['attempt_id']='phase-0-attempt-0001'
 latest=copy.deepcopy(prior);latest['attempt_id']='phase-0-attempt-0002';latest['status']='FAIL'
 nextphase=copy.deepcopy(prior);nextphase['phase']=1;nextphase['attempt_id']='phase-1-attempt-0001'
 for data in (prior,latest,nextphase):(td/(data['attempt_id']+'.json')).write_text(json.dumps(data),encoding='utf-8')
 entries={}
 for data in (latest,nextphase):
  file=td/(data['attempt_id']+'.json');entries['phase-'+str(data['phase'])]={'path':file.name,'sha256':helper.sha256_file(file)}
 (td/'receipt-index.json').write_text(json.dumps({'phases':entries}),encoding='utf-8')
 out['latest_attempt_probe']={'indexed_phase0_status':'FAIL','old_phase0_status':'PASS','phase1_status':'PASS','validation_errors':helper.validate_chain(td),'observed':'validator allows old PASS to unlock next phase despite index selecting newer FAIL; empty commands/invariants accepted','production_access':False}
(HERE/'cw228_receipt_check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
