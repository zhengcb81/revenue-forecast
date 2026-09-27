"""Audit-only: hash selected known raw/derived files; never changes data lake."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

audit = Path(__file__).parent
baseline = json.loads((audit / "catalog_baseline.json").read_text(encoding="utf-8"))
def check_file(path, expected_hash, expected_size):
    p = Path(path)
    if not p.is_file():
        return {"path": path, "exists": False}
    before = p.stat()
    with p.open("rb") as f:
        sha = hashlib.file_digest(f, "sha256").hexdigest()
    after = p.stat()
    return {"path":path,"exists":True,"sha256":sha,"hash_matches":sha==expected_hash,"byte_size":after.st_size,"size_matches":after.st_size==expected_size,"mtime_unchanged_during_read":before.st_mtime_ns==after.st_mtime_ns,"mtime_ns":after.st_mtime_ns}

result = {"audit_time_utc":datetime.now(timezone.utc).isoformat(),"source_baseline":"catalog_baseline.json","documents":[]}
for company, entries in baseline["companies"].items():
    for e in entries:
        d = e["document"]
        if d["source_status"]!="active" or d["document_kind"]!="annual_report" or d["published_date"] is None:
            continue
        item={"company":company,"document_id":d["document_id"],"title":d["title"],"published_date":d["published_date"],"locations":[],"artifacts":[]}
        for loc in e["locations"]:
            if loc["location_status"]!="active":
                continue
            sha = loc["source_id"].rsplit(":",1)[1]
            verified=check_file(loc["absolute_path"],sha,loc["observed_size"])
            verified.update({"root_id":loc["root_id"],"role":loc["role"],"manifest":json.loads(loc["manifest_json"]) if loc["manifest_json"] else None})
            item["locations"].append(verified)
        for art in e["artifacts"]:
            verified=check_file(art["path"],art["content_sha256"],art["byte_size"])
            verified.update({k:art[k] for k in ("artifact_role","status","generator_name","generator_version","schema_version","source_sha256")})
            verified["metadata"]=json.loads(art["metadata_json"])
            item["artifacts"].append(verified)
        result["documents"].append(item)
output=audit/"raw_artifact_verification.json"
if output.exists():
    raise SystemExit("audit snapshot exists; not overwritten")
output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"saved":str(output),"documents":[{"company":d["company"],"title":d["title"],"locations":[{"root":l["root_id"],"role":l["role"],"exists":l["exists"],"hash_matches":l.get("hash_matches")}for l in d["locations"]],"artifacts":[{"role":a["artifact_role"],"status":a["status"],"hash_matches":a.get("hash_matches"),"schema_version":a["schema_version"],"source_sha256":a["source_sha256"]}for a in d["artifacts"]]}for d in result["documents"]]},ensure_ascii=False,indent=2))
