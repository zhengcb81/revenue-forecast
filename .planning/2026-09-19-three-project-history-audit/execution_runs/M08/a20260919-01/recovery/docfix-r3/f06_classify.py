"""Classify the exact cut that reproduces the disputed second-r2 claim.

Reads in binary (no newline translation, which is what produced the false negative
in the first probe), then prints the neighbourhood of the reproduced cut with
explicit repr and byte accounting, plus the line-ending census.

Usage: <iso venv python> -X utf8 -B f06_classify.py > f06_classify.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")
NL = chr(10)
CR = chr(13)

brute = json.load(open(os.path.join(HERE, "f06_brute.json"), encoding="utf-8"))
print("== classification of the reproduced cut for the disputed claim ==")

for card in CARDS:
    path = os.path.join(BASE, card, "a20260919-01", "oracle.md")
    raw = open(path, "rb").read()
    txt = raw.decode("utf-8")
    entry = brute[card]
    markers = entry["markers"]
    claim2 = entry["claims"][1]
    hit = [f for f in entry["found"] if f["claim"] == claim2][0]
    off = hit["char_offset"]
    prefix = txt[:off]
    pb = prefix.encode("utf-8")

    print("")
    print(f"-- {card} --")
    print(f"   crlf_pairs={txt.count(CR + NL)}  lf_total={txt.count(NL)}  "
          f"cr_total={txt.count(CR)}  mixed_endings={txt.count(CR + NL) != txt.count(NL)}")
    print(f"   r2_marker_starts={markers}  (second marker char offset)")
    print(f"   disputed_claim={claim2}")
    print(f"   reproduced_as: variant={hit['variant']} char_offset={off} "
          f"payload_bytes={hit['payload_bytes']}")
    print(f"   rehash_independent="
          f"{hashlib.sha256(pb).hexdigest() == claim2}")
    print(f"   cut_lands_on_line_boundary="
          f"{(off == 0) or (txt[off - 1] == NL)}")
    print(f"   distance_from_second_marker_chars={markers[1] - off}")
    print(f"   chars_just_before_cut={txt[max(0, off - 14):off]!r}")
    print(f"   chars_just_after_cut ={txt[off:off + 14]!r}")

    # Which line does the cut fall in, and what is that line?
    line_no = txt[:off].count(NL) + 1
    line_text = txt.split(NL)[line_no - 1]
    col = off - (txt[:off].rfind(NL) + 1)
    print(f"   cut_falls_in_line={line_no} column={col} of_that_line")
    print(f"   that_line={line_text!r}")

    # is the cut point identical in character terms across the cards?
    print(f"   prefix_endswith={txt[max(0, off - 12):off]!r}")
