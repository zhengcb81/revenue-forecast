"""I-11-A probe-3: resolve the font objects of one page and inspect their encoding.

Usage: python -X utf8 -B tools\\probe_pdf_fonts.py <pdf> <classic_page_object_number>
Pure stdlib. Read-only.
"""

from __future__ import annotations

import re
import sys
import zlib

OBJ_RE = re.compile(rb"(\d+)\s+(\d+)\s+obj\b")


def object_offsets(data: bytes) -> dict:
    out = {}
    for m in OBJ_RE.finditer(data):
        out[int(m.group(1))] = m.start()
    return out


def get_object(data: bytes, offsets: dict, num: int) -> bytes | None:
    start = offsets.get(num)
    if start is None:
        return None
    end = data.find(b"endobj", start)
    return data[start:end if end != -1 else start + 65536]


def decode_stream(raw_obj: bytes) -> bytes | None:
    m = re.search(rb"stream\r?\n", raw_obj)
    if not m:
        return None
    s = m.end()
    e = raw_obj.find(b"endstream", s)
    if e == -1:
        return None
    payload = raw_obj[s:e]
    if b"/FlateDecode" in raw_obj[:m.start()]:
        try:
            payload = zlib.decompress(payload)
        except zlib.error:
            try:
                payload = zlib.decompressobj().decompress(payload)
            except zlib.error:
                return None
    return payload


def main() -> int:
    path, num = sys.argv[1], int(sys.argv[2])
    with open(path, "rb") as fh:
        data = fh.read()
    offsets = object_offsets(data)
    page = get_object(data, offsets, num)
    if page is None:
        print("page object not found")
        return 1
    fonts = re.search(rb"/Font\s*<<(.*?)>>", page, re.S)
    if not fonts:
        print("no /Font dict")
        return 1
    pairs = re.findall(rb"/(\w+)\s+(\d+)\s+0\s+R", fonts.group(1))
    print("font refs:", [(k.decode(), int(v)) for k, v in pairs])
    for name, ref in pairs:
        obj = get_object(data, offsets, int(ref))
        print("=== /%s -> %s 0 obj (bytes %d) ===" % (name.decode(), ref.decode(), len(obj or b"")))
        if obj is None:
            continue
        print(obj[:900].decode("latin-1"))
        for key in (b"/ToUnicode", b"/DescendantFonts", b"/Encoding"):
            m = re.search(key + rb"\s*(\d+)\s+0\s+R", obj)
            if m:
                sub = get_object(data, offsets, int(m.group(1)))
                print("--- %s -> obj %s (%d bytes)" % (key.decode(), m.group(1).decode(), len(sub or b"")))
                if sub:
                    print(sub[:600].decode("latin-1"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
