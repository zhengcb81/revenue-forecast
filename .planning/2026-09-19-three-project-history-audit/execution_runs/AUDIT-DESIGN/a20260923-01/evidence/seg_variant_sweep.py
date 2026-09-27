"""AUDIT-DESIGN: sweep boundary-normalisation variants for the three ruling bodies
in rulings_transcribed_2026-09-22.md and test each against the three RESPONSES-registered
hashes (OPEN-4 37413f78..1d98bb / OPEN-5 74f5c835..772b234 / OPEN-6 8aabac09..368d1).
Read-only; prints to stdout. Usage: python -X utf8 -B seg_variant_sweep.py <transcribed.md>
"""
import hashlib
import re
import sys
from pathlib import Path

TARGETS = [("37413f78", "1d98bb"), ("74f5c835", "772b234"), ("8aabac09", "368d1")]


def variants(b: bytes):
    yield "raw", b
    yield "s1_1", b[1:-1]
    yield "s2_2", b[2:-2]
    yield "strip_ws", b.strip()
    yield "strip_crlf", b.strip(b"\r\n")
    yield "strip_nl_space_tab", b.strip(b"\r\n \t")
    yield "l2_r1", b[2:-1]
    yield "l1_r2", b[1:-2]
    yield "l2_r0", b[2:]
    yield "l0_r2", b[:-2]
    yield "lf_only", b.replace(b"\r\n", b"\n")
    yield "lf_only_s1_1", b.replace(b"\r\n", b"\n")[1:-1]


def main() -> int:
    text = Path(sys.argv[1]).read_bytes()
    marks = [(m.start(), m.end(), m.group(0)) for m in re.finditer(rb"BEGIN[^\n]*|END[^\n]*", text)]
    bodies = []
    op = None
    for s, e, raw in marks:
        if raw.upper().startswith(b"BEGIN"):
            op = e
        elif raw.upper().startswith(b"END") and op is not None:
            bodies.append(text[op:s])
            op = None
    for i, b in enumerate(bodies):
        for name, v in variants(b):
            h = hashlib.sha256(v).hexdigest()
            hit = [t for t in targets() if h.startswith(t[0]) and h.endswith(t[1])]
            tag = f"   <<< MATCH {hit}" if hit else ""
            print(f"seg{i+1} {name:16s} bytes={len(v):6d} {h}{tag}")
    return 0


def targets():
    return TARGETS


if __name__ == "__main__":
    raise SystemExit(main())
