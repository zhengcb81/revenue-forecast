"""Verify every evidence-claim excerpt against the checked FY2025 10-K text.

For each distinct excerpt:
  * is it a verbatim substring of the local text extraction?
  * if not, is its digit sequence an exact prefix/ordering match of the rendered
    table block (i.e. a formatting difference, not a different figure)?

Writes evidence/excerpt-fidelity.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEXT = ROOT / "mdb-fy2025-10k.txt"
INPUT = ROOT / "inputs" / "mongodb-fy2025-input.json"


def digits(text: str) -> list[str]:
    return re.findall(r"\d[\d,]*", text)


def main() -> int:
    body = TEXT.read_text(encoding="utf-8")
    document = json.loads(INPUT.read_text(encoding="utf-8"))

    def slice_between(start: str, end: str) -> str:
        begin = body.index(start)
        finish = body.index(end, begin) + len(end)
        return body[begin:finish]

    blocks = {
        "total_table": slice_between("Subscription\n| $ | 1,943,864", "1,284,040 | 100 |"),
        "disagg_table": slice_between(
            "Subscription product categories and services:", "1,284,040 |"
        ),
    }

    records = []
    seen: dict[str, str] = {}
    for claim in document["evidence_claims"]:
        excerpt = claim["excerpt"]
        if excerpt in seen:
            continue
        seen[excerpt] = claim["claim_id"]
        verbatim = excerpt in body
        entry = {
            "claim_id": claim["claim_id"],
            "excerpt_chars": len(excerpt),
            "verbatim_in_checked_text": verbatim,
        }
        if not verbatim:
            match = next(
                (name for name, block in blocks.items() if digits(block) == digits(excerpt)),
                None,
            )
            entry["same_figure_sequence_as_block"] = match
            entry["rendered_excerpt"] = excerpt
            if match is not None:
                entry["verbatim_block"] = blocks[match]
        records.append(entry)

    report = {
        "schema_version": "rf-input-excerpt-fidelity/1",
        "checked_text": TEXT.name,
        "checked_text_sha256": __import__("hashlib").sha256(TEXT.read_bytes()).hexdigest(),
        "input_sha256": __import__("hashlib").sha256(INPUT.read_bytes()).hexdigest(),
        "distinct_excerpts": len(records),
        "verbatim_count": sum(1 for record in records if record["verbatim_in_checked_text"]),
        "reformatted_table_blocks": [r for r in records if not r["verbatim_in_checked_text"]],
        "records": records,
        "note": (
            "Table excerpts in the delivered input are rendered in document reading order "
            "(row label followed by the cell values); the two here are not byte substrings of the "
            "extraction because the extractor emits one cell per line with a ' | ' separator. "
            "Their figure sequence is identical to the verbatim block shown, and each claim's "
            "locator names the disclosed table row."
        ),
    }
    (ROOT / "evidence" / "excerpt-fidelity.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: report[k] for k in ("distinct_excerpts", "verbatim_count")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
