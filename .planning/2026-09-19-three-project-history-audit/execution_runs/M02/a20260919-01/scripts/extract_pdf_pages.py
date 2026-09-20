"""Standalone read-only PDF page probe for the M01-M04 disclosure mappings.

This script does NOT call any product code. It only opens already-downloaded
company raw PDFs read-only, searches for literal keywords, and dumps the
matching page text so that a disclosed figure can be quoted with page number.

ASCII-only stdout (GBK console safe).

Usage:
    python extract_pdf_pages.py <spec.json> <out.json>
"""

from __future__ import annotations

import json
import sys

import fitz  # PyMuPDF


def dump_spec(spec: dict) -> dict:
    results = []
    for doc in spec["docs"]:
        path = doc["path"]
        item = {
            "doc_id": doc["doc_id"],
            "path": path,
            "page_count": None,
            "searches": [],
            "error": None,
        }
        try:
            with fitz.open(path) as pdf:
                item["page_count"] = pdf.page_count
                for term in doc["terms"]:
                    hits = []
                    for page_index in range(pdf.page_count):
                        text = pdf.load_page(page_index).get_text("text")
                        if term in text:
                            hits.append({
                                "page_index": page_index,
                                "page_label": page_index + 1,
                                "text": text,
                            })
                    item["searches"].append({"term": term, "hit_count": len(hits), "hits": hits})
                if doc.get("pages"):
                    pages = []
                    for page_number in doc["pages"]:
                        text = pdf.load_page(page_number - 1).get_text("text")
                        pages.append({"page_label": page_number, "text": text})
                    item["explicit_pages"] = pages
        except Exception as exc:  # noqa: BLE001 - probe must record, not crash
            item["error"] = f"{type(exc).__name__}: {exc}"
        results.append(item)
    return {"spec_name": spec.get("spec_name"), "results": results}


def main() -> int:
    spec_path, out_path = sys.argv[1], sys.argv[2]
    with open(spec_path, "r", encoding="utf-8") as handle:
        spec = json.load(handle)
    payload = dump_spec(spec)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=1)
    total_hits = sum(s["hit_count"] for r in payload["results"] for s in r["searches"])
    print("spec:", payload["spec_name"])
    for r in payload["results"]:
        print("doc:", r["doc_id"], "pages:", r["page_count"], "error:", r["error"])
        for s in r["searches"]:
            print("  term:", s["term"], "hits:", s["hit_count"],
                  "pages:", [h["page_label"] for h in s["hits"]])
    print("total_hits:", total_hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
