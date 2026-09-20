"""I-11-A probe-2: dump the object dictionary of a given page (read-only).

Usage: python -X utf8 -B tools\\probe_pdf_page.py <pdf> <page_no> [max_bytes]
Pure stdlib.
"""

from __future__ import annotations

import re
import sys


def find_page_objects(data: bytes):
    """Return {objnum: raw_bytes} for every classic /Type /Page object."""
    out = {}
    for m in re.finditer(rb"(\d+)\s+0\s+obj\b", data):
        num = int(m.group(1))
        start = m.start()
        end = data.find(b"endobj", start)
        if end == -1:
            continue
        body = data[start:end]
        if re.search(rb"/Type\s*/Page[^s]", body):
            out[num] = body
    return out


def main() -> int:
    path = sys.argv[1]
    page_no = int(sys.argv[2])
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
    with open(path, "rb") as fh:
        data = fh.read()
    pages = find_page_objects(data)
    nums = sorted(pages)
    print("classic page objects:", len(nums), "first:", nums[:5], "last:", nums[-5:])
    target = nums[page_no - 1] if page_no - 1 < len(nums) else None
    print("page index", page_no, "-> obj", target)
    if target is None:
        return 1
    body = pages[target]
    print("--- page obj bytes:", len(body))
    print(body[:limit].decode("latin-1"))
    # dump the content stream prefix if it is inline
    for m in re.finditer(rb"stream\r?\n", body):
        s = m.end()
        e = body.find(b"endstream", s)
        raw = body[s:e]
        print("--- stream bytes:", len(raw), "prefix:", raw[:60])
    return 0


if __name__ == "__main__":
    sys.exit(main())
