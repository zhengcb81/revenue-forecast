"""I-11-A: find and verify the page-index offset between this attempt's extractor
and the prior independent extraction artifact, then score agreement.

The prior artifact (revenue-forecast/audit_review/.../ZIJIN/annual_2025_selected_pages.json)
labels pages with an index that this tool tries to reproduce; the tool tests every
offset hypothesis rather than assuming one.

Usage:
  python -X utf8 -B tools/page_offset_match.py <mine.json> <prior.json> <out.json>
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter

NUM_RE = re.compile(r"\d[\d,]*\.?\d*")


def numbers(text: str) -> Counter:
    c = Counter()
    for raw in NUM_RE.findall(text):
        tok = raw.rstrip(".").replace(",", "")
        if tok:
            c[tok] += 1
    return c


def main() -> int:
    mine_path, prior_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    mine = {p["pdf_page"]: p["text"] for p in json.load(open(mine_path, encoding="utf-8"))["pages"]}
    prior = {p["pdf_page"]: p["text"] for p in json.load(open(prior_path, encoding="utf-8"))["pages"]}
    hypotheses = []
    for off in (-1, 0, 1, 2):
        inter = sorted(set(prior) & {p + off for p in mine})
        agree = 0
        only_mine_total = 0
        only_prior_total = 0
        details = []
        for pg in inter:
            m = numbers(mine[pg - off])
            p = numbers(prior[pg])
            om = sum((m - p).values())
            op = sum((p - m).values())
            only_mine_total += om
            only_prior_total += op
            exact = m == p
            agree += 1 if exact else 0
            details.append({
                "prior_page": pg,
                "mine_page": pg - off,
                "exact_multiset_match": exact,
                "only_mine_count": om,
                "only_prior_count": op,
                "only_prior_sample": sorted((p - m).elements())[:15],
                "only_mine_sample": sorted((m - p).elements())[:15],
            })
        hypotheses.append({
            "offset_prior_minus_mine": off,
            "pages_compared": len(inter),
            "pages_exact": agree,
            "only_mine_total": only_mine_total,
            "only_prior_total": only_prior_total,
            "details": details,
        })
    best = max(hypotheses, key=lambda h: (h["pages_exact"], -h["only_prior_total"] - h["only_mine_total"]))
    report = {
        "mine_pages": sorted(mine),
        "prior_pages": sorted(prior),
        "hypotheses": hypotheses,
        "best_offset_prior_minus_mine": best["offset_prior_minus_mine"],
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    for h in hypotheses:
        print("offset", h["offset_prior_minus_mine"], "compared", h["pages_compared"],
              "exact", h["pages_exact"], "only_mine", h["only_mine_total"],
              "only_prior", h["only_prior_total"])
    print("best offset (prior - mine):", best["offset_prior_minus_mine"])
    print("--- non-exact pages under best offset ---")
    for d in best["details"]:
        if not d["exact_multiset_match"]:
            print("prior p%d / mine p%d: only_mine %d %s | only_prior %d %s" % (
                d["prior_page"], d["mine_page"], d["only_mine_count"], d["only_mine_sample"][:8],
                d["only_prior_count"], d["only_prior_sample"][:8]))
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
