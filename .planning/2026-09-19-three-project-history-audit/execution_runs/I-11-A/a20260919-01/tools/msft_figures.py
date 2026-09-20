"""I-11-A: extract the revenue tables of the MSFT 10-K (inline XBRL HTM).

Pure stdlib html.parser, no third-party XML libraries: the venv has only pytest,
and the same offline constraint applies to this file's dependencies.

Usage: python -X utf8 -B tools/msft_figures.py <htm> <out.json> <ascii.txt>
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from html.parser import HTMLParser


class TableGrab(HTMLParser):
    """Collect every <table> as a list of rows of cell texts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self._stack = []
        self._row = None
        self._cell = None
        self._cell_attrs = {}
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self._stack.append([])
        elif tag == "tr" and self._stack:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
            self._cell_attrs = a
        self._depth += 1

    def handle_endtag(self, tag):
        self._depth -= 1
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            txt = re.sub(r"\s+", " ", "".join(self._cell)).strip()
            self._row.append({"text": txt, "colspan": self._cell_attrs.get("colspan"),
                              "context": self._cell_attrs.get("contextref") or self._cell_attrs.get("contextRef")})
            self._cell = None
        elif tag == "tr" and self._row is not None and self._stack:
            self._stack[-1].append(self._row)
            self._row = None
        elif tag == "table" and self._stack:
            self.tables.append(self._stack.pop())

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def main() -> int:
    htm_path, out_path, ascii_path = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(htm_path, "rb").read()
    text = raw.decode("utf-8", "replace")
    parser = TableGrab()
    parser.feed(text)
    rows_total = sum(len(t) for t in parser.tables)
    hit = []
    for ti, table in enumerate(parser.tables):
        flat = " ".join(c["text"] for r in table for c in r)
        # NOTE: the word "Revenue" is NOT required -- the disaggregation table in
        # the revenue-recognition note only carries the line-item names and the
        # years (R2 correction of the first filter, see oracle.md section R2).
        if ("Server products and cloud services" in flat
                or "Microsoft Cloud" in flat
                or "Productivity and Business Processes" in flat
                or "More Personal Computing" in flat
                or "remaining performance obligation" in flat):
            hit.append({"table_index": ti, "rows": table})
    report = {
        "source": htm_path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
        "tables_total": len(parser.tables),
        "rows_total": rows_total,
        "revenue_tables": hit,
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    lines = ["source sha256=%s byte_size=%d tables=%d rows=%d revenue_matching_tables=%d"
             % (report["sha256"], report["byte_size"], report["tables_total"],
                report["rows_total"], len(hit))]
    for h in hit:
        lines.append("--- table %d (%d rows)" % (h["table_index"], len(h["rows"])))
        for r in h["rows"]:
            lines.append("   | " + " | ".join(c["text"] for c in r))
    with open(ascii_path, "w", encoding="ascii", errors="replace") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[:80]))
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
