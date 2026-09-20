"""Decisive brute force: recompute every candidate cut directly, no hash index.

This script deliberately contains no cleverness. For each card it reads oracle.md
in a single documented way, prints len(txt)/sha256(txt.encode()) so the read itself
is verifiable, then loops over every character offset and tests the four cut
families by hashing the payload on the spot.

Usage: <iso venv python> -X utf8 -B f06_brute.py > f06_brute.out.txt
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

BASE = (
    "C:/Users/\u90d1\u66fe\u6ce2/Projects/revenue-forecast/.planning/"
    "2026-09-19-three-project-history-audit/execution_runs"
)
CARDS = ("M05", "M06", "M07", "M08")
MARKER = "## \u4fee\u8ba2 r2"
CLAIM_RE = re.compile(
    "\u672c\u8282\u8ffd\u52a0\u524d `oracle\\.md` sha256 = `([0-9a-f]{64})`"
)
HERE = os.path.dirname(os.path.abspath(__file__))
result: dict[str, object] = {}

for card in CARDS:
    path = os.path.join(BASE, card, "a20260919-01", "oracle.md")
    raw = open(path, "rb").read()          # binary: no newline translation
    txt = raw.decode("utf-8")
    print("")
    print(f"-- {card} --")
    print(f"   read_mode=binary+utf-8  bytes={len(raw)}  chars={len(txt)}")
    print(f"   sha256(raw)={hashlib.sha256(raw).hexdigest()}")
    print(f"   sha256(txt.encode('utf-8'))={hashlib.sha256(txt.encode('utf-8')).hexdigest()}")
    print(f"   crlf_count={txt.count(chr(13) + chr(10))}  lone_cr={txt.count(chr(13)) - txt.count(chr(13) + chr(10))}")
    markers = [m.start() for m in re.finditer(re.escape(MARKER), txt)]
    print(f"   marker={MARKER!r} starts_at_char={markers}")
    claims = CLAIM_RE.findall(txt)
    print(f"   claims={len(claims)}")

    found: list[dict[str, object]] = []
    targets = set(claims)
    for off in range(len(txt) + 1):
        prefix = txt[:off]
        cands = [
            ("as-is", prefix),
            ("rstrip+NL", prefix.rstrip() + "\n"),
            ("rstrip", prefix.rstrip()),
            ("CRLF-as-is", prefix.replace("\n", "\r\n")),
        ]
        for variant, payload in cands:
            digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            if digest in targets:
                found.append(
                    {
                        "claim": digest,
                        "char_offset": off,
                        "variant": variant,
                        "payload_bytes": len(payload.encode("utf-8")),
                    }
                )
    for claim in claims:
        hits = [f for f in found if f["claim"] == claim]
        which = "section1(kept)" if claim == claims[0] else "section2(duplicate)"
        print(f"   {which} claim={claim}")
        if hits:
            for h in hits[:8]:
                print(
                    f"        MATCH char_offset={h['char_offset']} variant={h['variant']} "
                    f"payload_bytes={h['payload_bytes']}"
                )
            print(f"        total_matches={len(hits)}")
        else:
            print("        NO MATCH in the whole cut space (exhaustive brute force)")
    result[card] = {"claims": claims, "markers": markers, "found": found}

with open(os.path.join(HERE, "f06_brute.json"), "w", encoding="utf-8") as fh:
    json.dump(result, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print("")
print("wrote f06_brute.json")
sys.exit(0)
