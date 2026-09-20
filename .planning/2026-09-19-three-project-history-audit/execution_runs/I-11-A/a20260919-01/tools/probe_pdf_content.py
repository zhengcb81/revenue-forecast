"""I-11-A probe-4: inspect the content stream of one page (read-only, pure stdlib).

Usage: python -X utf8 -B tools\\probe_pdf_content.py <pdf> <page_object_number> [max_show]
"""

from __future__ import annotations

import re
import sys
import zlib

OBJ_RE = re.compile(rb"(\d+)\s+(\d+)\s+obj\b")


def offsets(data):
    return {int(m.group(1)): m.start() for m in OBJ_RE.finditer(data)}


def get(data, offs, num):
    s = offs.get(num)
    if s is None:
        return None
    e = data.find(b"endobj", s)
    return data[s:e if e != -1 else s + 1 << 20]


def stream(obj):
    m = re.search(rb"stream\r?\n", obj)
    if not m:
        return None
    s = m.end()
    e = obj.find(b"endstream", s)
    payload = obj[s:e]
    if b"/FlateDecode" in obj[:m.start()]:
        try:
            payload = zlib.decompress(payload)
        except zlib.error:
            return None
    return payload


def main() -> int:
    path, num = sys.argv[1], int(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
    data = open(path, "rb").read()
    offs = offsets(data)
    page = get(data, offs, num)
    m = re.search(rb"/Contents\s+(\d+)\s+0\s+R", page)
    cnum = int(m.group(1))
    cs = stream(get(data, offs, cnum))
    print("contents obj", cnum, "decoded bytes", len(cs) if cs else None)
    if cs:
        txt = cs.decode("latin-1")
        print("--- head ---")
        print(txt[:limit])
        print("--- show ops ---")
        shows = re.findall(r"(Tj|TJ|Td|TD|Tm|T\*|BT|ET|Do)", txt)
        from collections import Counter
        print(Counter(shows))
        print("--- Do operands ---")
        print(sorted(set(re.findall(r"/(\w+)\s+Do", txt)))[:20])
    return 0


if __name__ == "__main__":
    sys.exit(main())
