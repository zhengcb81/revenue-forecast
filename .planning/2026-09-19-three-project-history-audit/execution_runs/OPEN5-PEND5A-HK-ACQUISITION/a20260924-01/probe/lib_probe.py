"""Readability probe P3: alternate local PDF text extractors (read-only).

Usage: python -B lib_probe.py <pdf> <out_json> <fitz|pdfminer|pypdf> [max_pages]

Runs the named globally-installed extractor over the SAVED bytes, counts the HK
anchor words, and writes the full extracted text to <out_json>.extracted.txt so
line numbers / byte ranges are reproducible. No product-repo writes.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys

ANCHORS = ["小米", "收入", "年度報告", "分部", "毛利"]


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def extract(pdf: str, lib: str, max_pages: int):
    if lib == "fitz":
        import fitz  # PyMuPDF

        doc = fitz.open(pdf)
        n = doc.page_count
        limit = n if max_pages <= 0 else min(n, max_pages)
        blocks = []
        for i in range(limit):
            page = doc[i]
            blocks.append("=== PDF_PAGE %d ===\n%s" % (i + 1, page.get_text("text")))
        doc.close()
        return n, limit, "\n".join(blocks)
    if lib == "pdfminer":
        from pdfminer.high_level import extract_text

        text = extract_text(pdf, maxpages=max_pages if max_pages > 0 else 0)
        return None, None, text
    if lib == "pypdf":
        from pypdf import PdfReader

        reader = PdfReader(pdf)
        n = len(reader.pages)
        limit = n if max_pages <= 0 else min(n, max_pages)
        blocks = []
        for i in range(limit):
            blocks.append("=== PDF_PAGE %d ===\n%s" % (i + 1, reader.pages[i].extract_text() or ""))
        return n, limit, "\n".join(blocks)
    raise SystemExit("unknown library: %s" % lib)


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    pdf, out_json, lib = sys.argv[1], sys.argv[2], sys.argv[3]
    max_pages = int(sys.argv[4]) if len(sys.argv) > 4 else 0

    with open(pdf, "rb") as fh:
        data = fh.read()

    err = None
    total = probed = None
    full = ""
    try:
        total, probed, full = extract(pdf, lib, max_pages)
    except Exception as e:  # noqa: BLE001
        err = "%s: %s" % (type(e).__name__, e)

    extract_path = out_json.replace(".json", "") + ".extracted.txt"
    with open(extract_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(full or "")
    with open(extract_path, "rb") as fh:
        extract_bytes = fh.read()

    anchors = {}
    for word in ANCHORS:
        count = (full or "").count(word)
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

    result = {
        "probe_utc": utc_now(),
        "pdf": pdf,
        "pdf_sha256": hashlib.sha256(data).hexdigest(),
        "pdf_bytes": len(data),
        "library": lib,
        "library_version": _version(lib),
        "argv": sys.argv,
        "error": err,
        "classic_pages": total,
        "pages_probed": probed,
        "extract_txt": extract_path,
        "extract_bytes": len(extract_bytes),
        "extract_sha256": hashlib.sha256(extract_bytes).hexdigest(),
        "total_chars": len(full or ""),
        "cjk_chars": sum(1 for ch in (full or "") if "一" <= ch <= "鿿"),
        "anchors": anchors,
        "anchors_hit_count": sum(1 for w in ANCHORS if anchors[w]["count"] > 0),
        "anchors_total_occurrences": sum(anchors[w]["count"] for w in ANCHORS),
    }
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(json.dumps({"library": lib, "error": err, "hits": result["anchors_hit_count"],
                      "counts": {w: anchors[w]["count"] for w in ANCHORS},
                      "total_chars": result["total_chars"],
                      "cjk_chars": result["cjk_chars"]}, ensure_ascii=False))
    return 0 if result["anchors_hit_count"] >= 3 else 1


def _version(lib: str) -> str:
    try:
        if lib == "fitz":
            import fitz

            return getattr(fitz, "__doc__", "") or fitz.version[0]
        if lib == "pdfminer":
            import pdfminer

            return getattr(pdfminer, "__version__", "?")
        if lib == "pypdf":
            import pypdf

            return pypdf.__version__
    except Exception as e:  # noqa: BLE001
        return "unavailable: %s" % e
    return "?"


if __name__ == "__main__":
    sys.exit(main())
