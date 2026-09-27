
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
if not args or args[0] != "download":
    raise SystemExit(31)

def value(name: str) -> str:
    return args[args.index(name) + 1]

base = Path(value("--base"))
ticker = value("--ticker")
record = Path(os.environ["FAKE_DAYU_RECORD"])
record.write_text(json.dumps(args, ensure_ascii=False), encoding="utf-8")
spec = json.loads(os.environ["FAKE_DAYU_META"])
filing = base / "portfolio" / ticker / "filings" / spec["document_id"]
filing.mkdir(parents=True)
files = []
for entry in spec["files"]:
    target = filing / entry["name"]
    target.write_bytes(entry["bytes"].encode("utf-8"))
    files.append({
        "name": entry["name"],
        "size": target.stat().st_size,
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "content_type": entry.get("content_type"),
        "source_url": entry.get("source_url", spec["source_url_prefix"] + entry["name"]),
    })
meta = {
    "document_id": spec["document_id"],
    "accession_number": spec["accession_number"],
    "ticker": ticker,
    "company_id": spec["company_id"],
    "form_type": spec["form_type"],
    "fiscal_year": spec["fiscal_year"],
    "fiscal_period": spec["fiscal_period"],
    "report_date": spec["report_date"],
    "filing_date": spec["filing_date"],
    "ingest_complete": True,
    "is_deleted": False,
    "primary_document": spec["primary_document"],
    "amended": False,
    "files": files,
}
(filing / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
print("download ok")
