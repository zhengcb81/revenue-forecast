"""I-11-A: cross-validate this attempt's extractor against the prior independent
extraction artifact on every overlapping page (read-only).

Both sides are text for the same raw PDF bytes; the comparison is over the set of
numeric tokens (thousands-separated and plain integers/decimals) because those are
what the frozen propositions cite.

Usage:
  python -X utf8 -B tools/crosscheck_extract.py <mine.json> <prior.json> <out.json>
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter

NUM_RE = re.compile(r"\d[\d,]*\.?\d*")


def numbers(text: str) -> Counter:
    out = Counter()
    for raw in NUM_RE.findall(text):
        tok = raw.rstrip(".")
        tok = tok.replace(",", "")
        if not tok:
            continue
        out[tok] += 1
    return out


def main() -> int:
    mine_path, prior_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    mine = json.load(open(mine_path, encoding="utf-8"))
    prior = json.load(open(prior_path, encoding="utf-8"))
    mine_pages = {p["pdf_page"]: p["text"] for p in mine["pages"]}
    prior_pages = {p["pdf_page"]: p["text"] for p in prior["pages"]}
    overlap = sorted(set(mine_pages) & set(prior_pages))
    report = {
        "mine": {"path": mine_path, "sha256_of_pdf": mine.get("pdf"), "pages": sorted(mine_pages)},
        "prior": {"path": prior_path, "source_sha256_recorded": prior.get("source_sha256"),
                  "pages": sorted(prior_pages)},
        "overlap_pages": overlap,
        "per_page": [],
        "totals": {},
    }
    total_mine = Counter()
    total_prior = Counter()
    for pg in overlap:
        m = numbers(mine_pages[pg])
        p = numbers(prior_pages[pg])
        total_mine += m
        total_prior += p
        only_mine = sorted((m - p).elements())
        only_prior = sorted((p - m).elements())
        report["per_page"].append({
            "pdf_page": pg,
            "mine_numeric_tokens": sum(m.values()),
            "prior_numeric_tokens": sum(p.values()),
            "only_mine": only_mine[:40],
            "only_prior": only_prior[:40],
            "only_mine_count": sum((m - p).values()),
            "only_prior_count": sum((p - m).values()),
            "exact_multiset_match": m == p,
        })
    report["totals"] = {
        "pages_compared": len(overlap),
        "pages_exact": sum(1 for r in report["per_page"] if r["exact_multiset_match"]),
        "mine_tokens": sum(total_mine.values()),
        "prior_tokens": sum(total_prior.values()),
        "only_mine_total": sum((total_mine - total_prior).values()),
        "only_prior_total": sum((total_prior - total_mine).values()),
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(report["totals"], ensure_ascii=True, indent=1))
    for r in report["per_page"]:
        if not r["exact_multiset_match"]:
            print("page", r["pdf_page"], "differs: only_mine", r["only_mine"][:12],
                  "only_prior", r["only_prior"][:12])
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
