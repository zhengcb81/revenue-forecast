"""I-11-A: scan every parsed MSFT table for the revenue disaggregation rows.

Usage: python -X utf8 -B tools/msft_scan_tables.py <htm> <ascii.txt>
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser


class TableGrab(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self._stack = []
        self._row = None
        self._cell = None
        self._attrs = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self._stack.append([])
        elif tag == "tr" and self._stack:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
            self._attrs = a

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None and self._stack:
            self._stack[-1].append(self._row)
            self._row = None
        elif tag == "table" and self._stack:
            self.tables.append(self._stack.pop())

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


NEEDLES = ["Server products and cloud services",
           "Microsoft 365 Commercial products and cloud services",
           "Search and news advertising",
           "Dynamics products and cloud services"]


def main() -> int:
    src, out = sys.argv[1], sys.argv[2]
    raw = open(src, "rb").read().decode("utf-8", "replace")
    p = TableGrab()
    p.feed(raw)
    lines = ["tables=%d" % len(p.tables)]
    for i, t in enumerate(p.tables):
        flat = " ".join(c for r in t for c in r)
        score = sum(1 for n in NEEDLES if n in flat)
        if score:
            lines.append("=== table %d rows=%d needles=%d" % (i, len(t), score))
            for r in t:
                txt = " | ".join(c for c in r if c)
                if txt:
                    lines.append("   " + txt)
    with open(out, "w", encoding="ascii", errors="replace") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[:120]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
