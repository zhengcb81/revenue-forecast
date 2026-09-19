"""Read-only consumer probes against isolated minimal SQLite fixtures only."""
import hashlib,importlib.util,json,sqlite3,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=Path('C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/section_query.py')
spec=importlib.util.spec_from_file_location('audit_section_query',source)
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
out={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'production_access':False,'cases':[]}
with tempfile.TemporaryDirectory(dir=HERE,prefix='isolated_sections_') as tmp:
 db=Path(tmp)/'catalog.sqlite3';conn=sqlite3.connect(db)
 conn.executescript('CREATE TABLE documents(document_id TEXT,document_kind TEXT,title TEXT); CREATE TABLE artifacts(document_id TEXT,path TEXT,metadata_json TEXT,artifact_role TEXT,generator_name TEXT,generator_version TEXT,status TEXT,source_sha256 TEXT);')
 conn.execute('INSERT INTO documents VALUES(?,?,?)',('doc','annual_report','fixture only'))
 def add(version,status,path):
  entry={'role':'mda','title':'fixture','ordinal':'one','char_start':0,'char_end':5,'path':str(path),'span_ids':['nonexistent-span']}
  conn.execute('INSERT INTO artifacts VALUES(?,?,?,?,?,?,?,?)',('doc',str(path/'index.json'),json.dumps({'sections':[entry]}),'sections','source_catalog_section_extractor',version,status,'unverified-wrong-source-hash'));conn.commit()
 add('old-version','failed',Path(tmp)/'does-not-exist-old')
 result=module.SectionQueryService(db).list_sections(document_id='doc').to_dict()
 out['cases'].append({'id':'missing_failed_unbound_accepted','returned':result,'index_exists':Path(result['index_path']).exists(),'expectation':'should fail closed or report invalid/stale rather than ordinary usable result','observed':'returned count=1 despite failed status, nonexistent index/content, nonexistent span, arbitrary old version/source hash'})
 add('new-version','completed',Path(tmp)/'does-not-exist-new')
 result2=module.SectionQueryService(db).list_sections(document_id='doc').to_dict()
 out['cases'].append({'id':'multiple_versions_no_selection_contract','returned_index':result2['index_path'],'observed':'older inserted failed artifact returned; query has no ORDER BY, version, status or latest source filter','limitation':'one deterministic fixture, not a guarantee of SQLite row order in every database'})
 conn.close()
target=HERE/'section_probe.json';target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
