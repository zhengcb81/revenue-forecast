"""I-11-A probe-5: dump positioned fragments of one page, to check line grouping.

Usage: python -X utf8 -B tools\\probe_fragments.py <pdf> <page_no> [first] [count]
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_text import Pdf, Page, classic_page_numbers  # noqa: E402


def main() -> int:
    path, page_no = sys.argv[1], int(sys.argv[2])
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    count = int(sys.argv[4]) if len(sys.argv) > 4 else 40
    data = open(path, "rb").read()
    pdf = Pdf(data)
    pages = classic_page_numbers(pdf)
    page = Page(pdf, pages[page_no - 1])
    frags = page.fragments()
    print("fragments:", len(frags))
    ordered = sorted([f for f in frags if f[2].strip()], key=lambda f: (-f[1], f[0]))
    for x, y, t in ordered[first:first + count]:
        print("x=%8.2f y=%8.2f | %s" % (x, y, t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
