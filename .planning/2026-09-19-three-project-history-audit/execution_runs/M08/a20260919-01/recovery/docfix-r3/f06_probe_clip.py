"""Dump the exact characters around the byte cut that reproduces the disputed hash.

The exhaustive scan (f06_cutscan.py) reproduces BOTH claims for every card. The
first claim sits on a line boundary; the second does not. This script prints the
neighbourhood so the cut can be classified precisely, and re-verifies the cut by
re-hashing it independently.

Usage: <iso venv python> -X utf8 -B f06_probe_clip.py > f06_probe_clip.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")
MARKER = "## \u4fee\u8ba2 r2"
CLAIM_RE = re.compile(
    "\u672c\u8282\u8ffd\u52a0\u524d `oracle\\.md` sha256 = `([0-9a-f]{64})`"
)

scan = json.load(open(os.path.join(HERE, "f06_cutscan.json"), encoding="utf-8"))
print("== exact character neighbourhood of each reproduced cut ==")
for card in CARDS:
    txt = open(os.path.join(BASE, card, "a20260919-01", "oracle.md"), encoding="utf-8").read()
    entry = scan[card]
    print("")
    print(f"-- {card} --")
    for claim in entry["claims"]:
        off = claim["matches"][0]["char_offset"]
        variant = claim["matches"][0]["variant"]
        payload = txt[:off]
        if variant == "rstrip+NL":
            payload = payload.rstrip() + "\n"
        ok = hashlib.sha256(payload.encode("utf-8")).hexdigest() == claim["claim"]
        # classify: does the cut land at the start of a line?
        line_start = off == 0 or txt[off - 1] == "\n"
        print(f"   {claim['which']}: cut char_offset={off} variant={variant} rehash_ok={ok}")
        print(f"      ends_at_line_start={line_start} "
              f"payload_bytes={len(payload.encode('utf-8'))}")
        lo = max(0, off - 26)
        hi = min(len(txt), off + 26)
        print(f"      before[{lo}:{off}] = {txt[lo:off]!r}")
        print(f"      after [{off}:{hi}] = {txt[off:hi]!r}")
        print(f"      after_bytes  = {txt[off:hi].encode('utf-8')!r}")
