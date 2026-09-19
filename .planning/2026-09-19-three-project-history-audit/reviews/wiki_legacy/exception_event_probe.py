from pathlib import Path
import ast,json,hashlib
HERE=Path(__file__).resolve().parent
path=Path('C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/worker.py')
raw=path.read_bytes();tree=ast.parse(raw.decode('utf-8-sig'))
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='SourceCatalogWorker')
fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_write_unhandled_exception_event')
# Execute the exact source method only; no package import, worker instance, DB, process, or filesystem event writer.
ns={};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(path),'exec'),ns)
events=[]
class Sink:
 def _write_process_event(self,event,**kw):events.append(dict(event=event,**kw))
marker='SYNTHETIC_AUDIT_TOKEN_NOT_A_REAL_SECRET'
ns[fn.name](Sink(),RuntimeError('Authorization: Bearer '+marker))
result=dict(source_file=str(path),source_sha256=hashlib.sha256(raw).hexdigest(),source_lines=[fn.lineno,fn.end_lineno],method_only=True,production_access=False,events=events,synthetic_marker_persisted=marker in events[0]['message_redacted'],conclusion='Truncating str(exc) to 200 chars does not redact content. This proves no automatic redaction on this method path, not actual secret exposure.')
(HERE/'exception_event_probe.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
