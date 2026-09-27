"""Readability probe for the ENGLISH version of the annual report.

Usage: python -B en_anchor_probe.py <pdf> <out_json>

Uses PyMuPDF (read-only) over the saved bytes, counts ENGLISH anchor words,
writes extracted text next to the JSON so line/byte ranges are reproducible.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys

ANCHORS = ["Xiaomi", "Revenue", "Annual Report", "Segment", "Gross profit"]


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    pdf, out_json = sys.argv[1], sys.argv[2]
    with open(pdf, "rb") as fh:
        data = fh.read()

    import fitz

    doc = fitz.open(pdf)
    blocks = []
    for i in range(doc.page_count):
        blocks.append("=== PDF_PAGE %d ===\n%s" % (i + 1, doc[i].get_text("text")))
    doc.close()
    full = "\n".join(blocks)

    extract_path = out_json.replace(".json", "") + ".extracted.txt"
    with open(extract_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(full)
    with open(extract_path, "rb") as fh:
        extract_bytes = fh.read()

    anchors = {}
    for word in ANCHORS:
        count = full.count(word)
        entry = {"count": count, "first_line": None, "first_byte_offset": None, "context": None}
        if count:
            idx = full.find(word)
            entry["first_line"] = full[:idx].count("\n") + 1
            entry["first_byte_offset"] = len(full[:idx].encode("utf-8"))
            line_start = full.rfind("\n", 0, idx) + 1
            line_end = full.find("\n", idx)
            if line_end == -1:
                line_end = len(full)
            entry["context"] = full[line_start:line_end][:200]
        anchors[word] = entry

    # Chinese anchors measured too, for the mandated cross-language comparison
    zh = {}
    for word in ["小米", "收入", "年度報告", "分部", "毛利"]:
        zh[word] = {"count": full.count(word)}

    result = {
        "probe_utc": utc_now(),
        "pdf": pdf,
        "pdf_sha256": hashlib.sha256(data).hexdigest(),
        "pdf_bytes": len(data),
        "library": "PyMuPDF(fitz)",
        "extract_txt": extract_path,
        "extract_bytes": len(extract_bytes),
        "extract_sha256": hashlib.sha256(extract_bytes).hexdigest(),
        "total_chars": len(full),
        "en_anchors": anchors,
        "en_hit_count": sum(1 for w in ANCHORS if anchors[w]["count"] > 0),
        "zh_anchors": zh,
        "zh_hit_count": sum(1 for w in zh if zh[w]["count"] > 0),
    }
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({"en_hits": result["en_hit_count"],
                      "en_counts": {w: anchors[w]["count"] for w in ANCHORS},
                      "zh_hits": result["zh_hit_count"],
                      "total_chars": result["total_chars"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
