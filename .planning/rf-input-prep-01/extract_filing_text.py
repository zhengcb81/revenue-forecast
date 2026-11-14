"""Extract readable text from a registered original HTML filing.

Research-side only: this converts the already-captured original into text so the
author can open and check real pages. It never creates a capture record.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path


def to_text(raw: str) -> str:
    # Drop script/style, then turn block/row boundaries into newlines.
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)</(p|div|tr|h[1-6]|li|table)>", "\n", raw)
    raw = re.sub(r"(?i)</t[dh]>", " | ", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?s)<[^>]+>", "", raw)
    text = html.unescape(raw)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text


if __name__ == "__main__":
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    text = to_text(source.read_text(encoding="utf-8", errors="replace"))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"lines={len(lines)} chars={len(text)} -> {target}")
