"""I-11-A: from the already-parsed MSFT tables, print the revenue disaggregation
tables and any cash-flow / unearned-revenue figures (read-only).

Usage: python -X utf8 -B tools/msft_products.py <msft.json> <ascii.txt>
"""

from __future__ import annotations

import json
import sys

WANT = [
    "Server products and cloud services",
    "Microsoft 365 Commercial products and cloud services",
    "Microsoft 365 Consumer products and cloud services",
    "LinkedIn",
    "Dynamics products and cloud services",
    "Windows",
    "Gaming",
    "Search and news advertising",
    "Enterprise and partner services",
    "Devices",
    "Total revenue",
    "Unearned revenue",
]


def main() -> int:
    src, out = sys.argv[1], sys.argv[2]
    report = json.load(open(src, encoding="utf-8"))
    lines = []
    for h in report["revenue_tables"]:
        idx = h["table_index"]
        rows = h["rows"]
        flat = " ".join(c["text"] for r in rows for c in r)
        score = sum(1 for w in WANT if w in flat)
        lines.append("=== table %d rows=%d wanted_hits=%d" % (idx, len(rows), score))
        if score >= 2:
            for r in rows:
                txt = " | ".join(c["text"] for c in r if c["text"])
                if txt:
                    lines.append("   " + txt)
    # every table that mentions any of the disaggregation line items
    lines.append("")
    lines.append("=== tables listing disaggregation rows ===")
    for h in report["revenue_tables"]:
        rows = h["rows"]
        hits = []
        for r in rows:
            txt = " | ".join(c["text"] for c in r if c["text"])
            for w in WANT:
                if w in txt:
                    hits.append(txt)
        if hits:
            lines.append("--- table %d" % h["table_index"])
            lines.extend("   " + t for t in hits)
    with open(out, "w", encoding="ascii", errors="replace") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
