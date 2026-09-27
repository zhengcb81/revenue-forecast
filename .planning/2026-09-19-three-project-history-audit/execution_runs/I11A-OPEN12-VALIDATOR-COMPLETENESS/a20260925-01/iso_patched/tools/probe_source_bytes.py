"""I-11-A step-2/3 probe: read-only inspection of the three bound raw filings.

Pure standard library (zlib). NO third-party PDF library is used and the global
Miniconda interpreter is never involved. Run under the attempt venv:

    <attempt>\iso\venv\Scripts\python.exe -X utf8 -B tools\probe_source_bytes.py

Outputs (evidence/I-11-A/):
  source_probe.json  - sha256/byte size/page count/font/ToUnicode facts per source
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ATTEMPT, "evidence", "I-11-A")

SOURCES = [
    {
        "source_doc_id": "CN-ZIJIN-AR2025",
        "path": r"C:\Users\郑曾波\Projects\company-wiki\companies\紫金矿业\raw\financial_reports\annual\2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf",
        "kind": "pdf",
    },
    {
        "source_doc_id": "HK-XIAOMI-AR2025",
        "path": r"C:\Users\郑曾波\Projects\company-wiki\companies\小米集團－Ｗ\raw\financial_reports\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf",
        "kind": "pdf",
    },
    {
        "source_doc_id": "US-MSFT-10K-FY2026",
        "path": r"C:\Users\郑曾波\Projects\company-wiki\companies\MICROSOFT CORP\raw\financial_reports\annual\2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm",
        "kind": "htm",
    },
]

REFERENCE_EXTRACTS = [
    {
        "artifact_id": "PRIOR-EXTRACT-ZIJIN",
        "path": r"C:\Users\郑曾波\Projects\revenue-forecast\audit_review\2026-09-18_real_company_skill_audit\ZIJIN\annual_2025_selected_pages.json",
    },
]


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_counts(data: bytes) -> dict:
    """Count /Type /Page objects and font encodings we can decode ourselves."""
    counts = {
        "page_objects": len(re.findall(rb"/Type\s*/Page[^s]", data)),
        "catalog_objects": len(re.findall(rb"/Type\s*/Catalog", data)),
        "font_objects": len(re.findall(rb"/Type\s*/Font", data)),
        "truetype_subtypes": len(re.findall(rb"/Subtype\s*/TrueType", data)),
        "type0_subtypes": len(re.findall(rb"/Subtype\s*/Type0", data)),
        "type1_subtypes": len(re.findall(rb"/Subtype\s*/Type1", data)),
        "tounicode_refs": len(re.findall(rb"/ToUnicode", data)),
        "flate_streams": len(re.findall(rb"/FlateDecode", data)),
        "objstm": len(re.findall(rb"/ObjStm", data)),
        "xrefstm": len(re.findall(rb"/XRef", data)),
        "encrypted": len(re.findall(rb"/Encrypt", data)),
    }
    return counts


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    report = {"sources": [], "reference_extracts": []}
    for src in SOURCES:
        entry = dict(src)
        with open(src["path"], "rb") as fh:
            data = fh.read()
        entry["byte_size"] = len(data)
        entry["sha256"] = sha256_file(src["path"])
        entry["magic"] = data[:8].decode("latin-1")
        if src["kind"] == "pdf":
            entry.update(pdf_counts(data))
            entry["header"] = data[:8].decode("latin-1")
            tail = data[-2048:]
            entry["has_eof"] = b"%%EOF" in tail
            sidecar = src["path"] + ".source.json"
            entry["sidecar_path"] = sidecar
            entry["sidecar_exists"] = os.path.exists(sidecar)
            if os.path.exists(sidecar):
                with open(sidecar, "rb") as fh:
                    raw = fh.read()
                entry["sidecar_sha256"] = hashlib.sha256(raw).hexdigest()
                entry["sidecar"] = json.loads(raw.decode("utf-8"))
        else:
            for token in [b"<html", b"<HTML", b"XBRL", b"ix:nonFraction", b"us-gaap:"]:
                entry["token_" + token.decode("latin-1").replace(":", "_")] = data.count(token)
            entry["charset_decl"] = re.findall(rb'charset=[^"\'>\s]+', data[:4000])
        report["sources"].append(entry)

    for ref in REFERENCE_EXTRACTS:
        entry = dict(ref)
        entry["byte_size"] = os.path.getsize(ref["path"])
        entry["sha256"] = sha256_file(ref["path"])
        with open(ref["path"], "rb") as fh:
            doc = json.loads(fh.read().decode("utf-8"))
        entry["pages"] = [p["pdf_page"] for p in doc["pages"]]
        entry["page_count"] = len(doc["pages"])
        entry["raw_path_recorded"] = doc["raw_path"]
        entry["source_sha256_recorded"] = doc["source_sha256"]
        report["reference_extracts"].append(entry)

    out = os.path.join(OUT_DIR, "source_probe.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("wrote", out)
    for s in report["sources"]:
        print(s["source_doc_id"], s["byte_size"], s["sha256"][:16],
              {k: v for k, v in s.items() if k in ("page_objects", "type0_subtypes",
                                                   "truetype_subtypes", "tounicode_refs",
                                                   "objstm", "encrypted")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
