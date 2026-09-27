"""Read-only evidence for post-download registration failures."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sqlite3

root=Path.home()/"Projects"/"company-wiki"
audit=Path(__file__).parent
result={"audit_time_utc":datetime.now(timezone.utc).isoformat(),"files":[]}
with sqlite3.connect((root/".source_catalog/catalog.sqlite3").as_uri()+"?mode=ro",uri=True) as conn:
    conn.execute("PRAGMA query_only=ON")
    conn.row_factory=sqlite3.Row
    result["recent_scans"]=[dict(r) for r in conn.execute("SELECT * FROM scan_runs ORDER BY started_at DESC LIMIT 8")]
    for company in ["小米集團－Ｗ","MICROSOFT CORP"]:
        for sidecar in (root/"companies"/company/"raw/financial_reports/annual").glob("*.source.json"):
            meta=json.loads(sidecar.read_text(encoding="utf-8"))
            raw=sidecar.with_name(sidecar.name.removesuffix(".source.json"))
            sha=hashlib.sha256(raw.read_bytes()).hexdigest()
            counts={table:conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {field}=?",(value,)).fetchone()[0] for table,field,value in [("sources","content_sha256",sha),("documents","primary_source_id","urn:company-wiki:source:sha256:"+sha),("locations","absolute_path",str(raw)),("source_metadata_assertions","content_sha256",sha)]}
            result["files"].append({"path":str(raw),"sidecar":str(sidecar),"sha256":sha,"hash_matches_sidecar":sha==meta["content_sha256"],"size":raw.stat().st_size,"size_matches_sidecar":raw.stat().st_size==meta["byte_size"],"metadata":meta,"catalog_counts":counts})
for name in ["runtime_policy.json","worker_control.json"]:
    p=root/".source_catalog"/name
    result[name]=json.loads(p.read_text(encoding="utf-8"))
target=audit/"acquisition_aftercheck.json"
if target.exists():
    raise SystemExit("snapshot already exists")
target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"files":[{k:f[k]for k in ("path","sha256","hash_matches_sidecar","size_matches_sidecar","catalog_counts")}for f in result["files"]],"recent_scans":result["recent_scans"],"worker_control":result["worker_control.json"]},ensure_ascii=False,indent=2))
