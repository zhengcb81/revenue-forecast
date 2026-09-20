"""I-11-A: extract the three bound figure pages of the Zijin annual report and
print them, plus locate the exact pages of the cited statements (read-only).

Usage: python -X utf8 -B tools/zijin_figures.py <pdf> <out.json> <ascii_report.txt>
"""

from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_text import Pdf, Page, classic_page_numbers, measured_positions  # noqa: E402

KEYWORDS = [
    "2026年公司主要矿产品产量计划",
    "①主营业务分行业、分产品、分地区、分销售模式情况",
    "②产销量情况分析表",
    "对外销售收入",
    "分部报告",
]


def main() -> int:
    pdf_path, out_path, ascii_path = sys.argv[1], sys.argv[2], sys.argv[3]
    data = open(pdf_path, "rb").read()
    pdf = Pdf(data)
    pages = classic_page_numbers(pdf)
    result = {"pdf": pdf_path, "classic_pages": len(pages), "pages": [], "keyword_pages": []}
    tol_stats = []
    for idx, objnum in enumerate(pages, start=1):
        page = Page(pdf, objnum)
        frags = page.fragments()
        text = ""
        if any(True for _ in ()):
            pass
        # only render pages that matter, but scan all for keyword locations
        joined = "".join(f[2] for f in frags)
        for kw in KEYWORDS:
            if kw in joined:
                result["keyword_pages"].append({"keyword": kw, "pdf_page": idx, "page_object": objnum})
    wanted = sorted({e["pdf_page"] for e in result["keyword_pages"]} |
                    {idx for idx in (45, 46, 47, 327, 328)})
    for idx in wanted:
        objnum = pages[idx - 1]
        page = Page(pdf, objnum)
        frags = page.fragments()
        text = __import__("pdf_text").page_text(frags)
        stats = measured_positions(frags)
        tol_stats.append({"pdf_page": idx, **stats})
        result["pages"].append({"pdf_page": idx, "page_object": objnum, "text": text,
                                "fragments": len(frags), **stats})
    result["tolerance_measurement"] = tol_stats
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    lines = []
    lines.append("keyword locations (scanned %d classic pages):" % len(pages))
    for e in result["keyword_pages"]:
        lines.append("  pdf_page=%d obj=%d keyword=%s" % (e["pdf_page"], e["page_object"],
                                                          e["keyword"].encode("unicode_escape").decode("ascii")))
    lines.append("rendered pages: %s" % wanted)
    lines.append("tolerance measurement (glyph-run y gaps):")
    for s in tol_stats:
        lines.append("  page %d max_gap<=0.8: %.3f min_gap>0.8: %.3f"
                     % (s["pdf_page"], s["max_gap_within_tolerance"], s["min_gap_above_tolerance"]))
    with open(ascii_path, "w", encoding="ascii") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
