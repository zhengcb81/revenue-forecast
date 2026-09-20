import hashlib
import io
import json
import os
import sys

plan = sys.argv[1]
mark = "## \u8fd0\u884c\u540e\u5bf9\u8d26\uff08\u8ffd\u52a0\u8282\uff0c\u4e0d\u6539\u52a8\u4e0a\u65b9\u4efb\u4f55\u671f\u671b\u503c\uff09"
mb = mark.encode("utf-8")
sep = b"\n---\n\n"
ok_all = True
for card in ("M21", "M22", "M23", "M24"):
    a = os.path.join(plan, "execution_runs", card, "a20260919-01")
    md = os.path.join(a, "oracle.md")
    raw = open(md, "rb").read()
    i = raw.find(mb)
    frozen = raw[:i].rstrip(b"\n-").rstrip(b"\n")
    h = hashlib.sha256(frozen).hexdigest()
    rec = json.load(io.open(os.path.join(a, "recovery", "oracle_body_hash.json"), encoding="utf-8"))
    sm = json.load(io.open(os.path.join(a, "evidence", card, "source_manifest.json"), encoding="utf-8"))
    rr = json.load(io.open(os.path.join(a, "after", "rerun_sha256.json"), encoding="utf-8"))
    full = hashlib.sha256(raw).hexdigest()
    recon = frozen + sep + raw[i:]
    checks = {
        "prefix_sha==record": h == rec["oracle_md_frozen_body_sha256"],
        "record==manifest": rec["oracle_md_frozen_body_sha256"] == sm["oracle_document"]["sha256_frozen_body"],
        "record==rerun": rec["oracle_md_frozen_body_sha256"] == rr["oracle_md_sha256_body_before_append"],
        "full==manifest": full == sm["oracle_document"]["sha256_full_file_now"],
        "full==rerun": full == rr["oracle_md_sha256_after_append"],
        "reconstruction_identity": recon == raw,
        "bytes_match": len(frozen) == rec["oracle_md_frozen_body_bytes"],
        "marker_after_sep": raw[i - len(sep):i] == sep,
        "oracle_json_mtime<stdout": sm["oracle_document"]["mtime_ordering"]["oracle_json_precedes_run"],
    }
    ok = all(checks.values())
    ok_all = ok_all and ok
    print(card, "ALL-OK" if ok else "PROBLEM", json.dumps(checks))
print("overall", "OK" if ok_all else "PROBLEM")
