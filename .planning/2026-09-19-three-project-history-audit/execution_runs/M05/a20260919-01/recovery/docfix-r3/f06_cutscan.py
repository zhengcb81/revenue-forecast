"""F-M08-06 recon: is the second r2 section's claimed "pre-append sha256" reproducible?

For each card we take oracle.md, extract BOTH claimed pre-append hashes (first r2
section = claimed-v1, second r2 section = the disputed value), and then test every
candidate cut of the document, exhaustively over ALL byte positions.

Candidate payloads covered (this is a superset of "any line boundary"):
  A. txt[:off]                      for every character offset off   (as-is cut)
  B. txt[:off].rstrip()             subset of A (ends at a non-space char)
  C. txt[:off].rstrip() + "\n"      ==  txt[:j] + "\n" for every j
  D. txt[:off] with "\n" -> "\r\n"  ==  a prefix of txt.replace("\n", "\r\n")

All three families are enumerated in O(n) with incremental sha256 state, so the
scan is exhaustive over the whole document rather than sampled.

A claim that matches nowhere is a provenance gap: the value cannot be re-derived
from any prefix of the document at any line boundary OR any byte boundary, so it
cannot serve as a hash-ledger baseline.

Output is ASCII only. Re-run:
  <iso venv python> -X utf8 -B f06_cutscan.py > f06_cutscan.out.txt
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
MARKER = "## \u4fee\u8ba2 r2"  # "## revision r2"
CLAIM_RE = re.compile(
    "\u672c\u8282\u8ffd\u52a0\u524d `oracle\\.md` sha256 = `([0-9a-f]{64})`"
)


def index_prefixes(txt: str) -> dict[str, list[tuple[int, str, int]]]:
    """hash -> [(char_offset, variant, payload_bytes), ...] for all cut families."""
    table: dict[str, list[tuple[int, str, int]]] = {}

    h_plain = hashlib.sha256()
    h_nl = hashlib.sha256()
    h_crlf = hashlib.sha256()
    nbytes_plain = 0
    nbytes_crlf = 0

    def record(h, off: int, variant: str, nbytes: int) -> None:
        table.setdefault(h.copy().hexdigest(), []).append((off, variant, nbytes))

    record(h_plain, 0, "as-is", 0)
    record(h_crlf, 0, "CRLF-as-is", 0)
    h_nl = hashlib.sha256()
    h_nl.update(b"\n")
    record(h_nl, 0, "rstrip+NL", 1)  # "" .rstrip() + "\n"

    for i, ch in enumerate(txt):
        cb = ch.encode("utf-8")
        h_plain.update(cb)
        nbytes_plain += len(cb)
        if ch == "\n":
            crlf_b = b"\r\n"
        else:
            crlf_b = cb
        h_crlf.update(crlf_b)
        nbytes_crlf += len(crlf_b)

        off = i + 1
        record(h_plain, off, "as-is", nbytes_plain)
        record(h_crlf, off, "CRLF-as-is", nbytes_crlf)

        # C: txt[:off].rstrip() + "\n".  The image of rstrip() over all prefixes is
        # exactly { txt[:j] : j == 0 or txt[j-1] is not whitespace }, so record the
        # "+ \n" stream only at those j -- otherwise the label would over-claim.
        if off == 0 or not txt[off - 1].isspace():
            h_nl = h_plain.copy()
            h_nl.update(b"\n")
            record(h_nl, off, "rstrip+NL", nbytes_plain + 1)

        # B: txt[:off].rstrip() -- same hash as some txt[:j] with j <= off,
        # already present in the "as-is" family, so no extra stream needed.
    return table


def main() -> int:
    report: dict[str, object] = {}
    print("== F-M08-06 cut scan: can the claimed pre-append hashes be reproduced? ==")
    print("candidate cuts: every byte offset of the document (exhaustive, not sampled)")
    print("families: as-is | rstrip(subset of as-is) | rstrip+NL | CRLF-as-is")
    for card in CARDS:
        path = os.path.join(BASE, card, "a20260919-01", "oracle.md")
        raw = open(path, "rb").read()
        txt = raw.decode("utf-8")
        claims = CLAIM_RE.findall(txt)
        markers = [m.start() for m in re.finditer(re.escape(MARKER), txt)]
        table = index_prefixes(txt)

        print("")
        print(f"-- {card} --")
        print(f"   file_bytes={len(raw)} file_sha256={hashlib.sha256(raw).hexdigest()}")
        print(f"   r2_marker_count={len(markers)} char_offsets={markers}")
        print(f"   distinct_candidate_hashes={len(table)}")
        print(f"   claimed_pre_append_hashes_found={len(claims)}")
        entry = {
            "file_bytes": len(raw),
            "file_sha256_before": hashlib.sha256(raw).hexdigest(),
            "r2_marker_count": len(markers),
            "r2_marker_char_offsets": markers,
            "distinct_candidate_hashes": len(table),
            "claims": [],
        }
        for i, claim in enumerate(claims):
            hits = table.get(claim, [])
            label = "section1(kept)" if i == 0 else "section2(duplicate)"
            print(f"   [{i}] {label} claim={claim}")
            if hits:
                for off, variant, plen in hits[:8]:
                    print(
                        f"        REPRODUCED char_offset={off} variant={variant} "
                        f"payload_bytes={plen}"
                    )
                print(f"        total_matches={len(hits)}")
            else:
                print("        NOT REPRODUCIBLE: 0 matches over the exhaustive cut space")
            entry["claims"].append(
                {
                    "index": i,
                    "which": label,
                    "claim": claim,
                    "reproducible": bool(hits),
                    "matches": [
                        {"char_offset": o, "variant": v, "payload_bytes": n}
                        for o, v, n in hits
                    ],
                }
            )
        report[card] = entry

    out_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(out_dir, "f06_cutscan.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("")
    print("wrote f06_cutscan.json next to this script")
    return 0


if __name__ == "__main__":
    sys.exit(main())
