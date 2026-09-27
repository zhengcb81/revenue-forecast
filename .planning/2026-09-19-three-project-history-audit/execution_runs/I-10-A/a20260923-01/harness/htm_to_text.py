#!/usr/bin/env python
"""I-10-A harness: extract readable text from the SEC 10-K HTM source.

Pure stdlib. Normalization is deterministic and documented so a reviewer can
re-derive every quoted 原文 string from the raw HTM: tags are dropped, entity
references are unescaped (html.unescape), block-level elements emit newlines,
whitespace runs inside text are collapsed to single spaces, and one text line is
emitted per resulting block. Line numbers of the output are the mechanical
anchor used by disclosure_mapping.json quotes; the source's own printed page
markers, when present in the text, are what the mapping records as 页码.

Writes ONLY the output file given on argv[2]. Reads ONLY argv[1].
"""
from __future__ import annotations

import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

BLOCK_TAGS = {
    "p", "div", "tr", "table", "section", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "ul", "ol", "br", "hr", "blockquote", "pre", "td", "th",
}


class _Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in BLOCK_TAGS:
            self._flush()

    def handle_endtag(self, tag):
        if tag.lower() in BLOCK_TAGS:
            self._flush()

    def handle_data(self, data):
        self._buf.append(data)

    def _flush(self):
        if not self._buf:
            return
        text = "".join(self._buf)
        self._buf = []
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            self.parts.append(text)

    def finish(self):
        self._flush()
        return self.parts


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: htm_to_text.py <in.htm> <out.txt>", file=sys.stderr)
        return 1
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    raw = src.read_text(encoding="utf-8", errors="strict")
    parser = _Extractor()
    parser.feed(raw)
    parser.close()
    lines = parser.finish()
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"lines={len(lines)} out={dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
