"""AUDIT-DESIGN independent reproduction of the parent's three-point D1 recheck.

Extracts the three BEGIN/END ruling bodies from
  execution_runs/I-06-A/a20260919-01/rulings_transcribed_2026-09-22.md
and hashes each body under boundary normalisation strip_lead=1/strip_tail=1
(i.e. drop one leading and one trailing byte, the enclosing newline of the
marker lines), printing prefix/suffix/length for comparison with the three
RESPONSES-registered values (OPEN-4 37413f78...1d98bb / OPEN-5 74f5c835...772b234
/ OPEN-6 8aabac09...368d1).

Read-only: prints to stdout only. Usage: python -X utf8 -B verify_transcription_segments.py <transcribed.md>
"""
import hashlib
import re
import sys
from pathlib import Path

EXPECTED = {
    "OPEN-4": ("37413f78", "1d98bb"),
    "OPEN-5": ("74f5c835", "772b234"),
    "OPEN-6": ("8aabac09", "368d1"),
}


def main() -> int:
    text = Path(sys.argv[1]).read_bytes()
    # find BEGIN/END pairs carrying a T2 label
    marks = [(m.start(), m.end(), m.group(0)) for m in re.finditer(rb"BEGIN[^\n]*|END[^\n]*", text)]
    bodies = []
    open_mark = None
    for start, end, raw in marks:
        upper = raw.upper()
        if upper.startswith(b"BEGIN"):
            open_mark = end
        elif upper.startswith(b"END") and open_mark is not None:
            bodies.append((text[open_mark:start], raw))
            open_mark = None
    print(f"segment pairs found: {len(bodies)}")
    for i, (body, endraw) in enumerate(bodies):
        label = f"seg{i+1}"
        for key in EXPECTED:
            if key.encode() in endraw or key.encode() in body[:400]:
                label = key
        norm = body[1:-1] if len(body) >= 2 else body
        h = hashlib.sha256(norm).hexdigest()
        exp = EXPECTED.get(label)
        verdict = ""
        if exp:
            verdict = f" expected=({exp[0]}..{exp[1]}) prefix_ok={h.startswith(exp[0])} suffix_ok={h.endswith(exp[1])}"
        print(f"{label}: bytes={len(body)} norm_bytes={len(norm)} sha256={h} end_marker={endraw[:60]!r}{verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
