"""Scratch: Z4-nomid against the FULL auth pattern (not the sub-pattern)."""
import re

B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"
T = "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*"
TAB = "[" + " " + B + "t]"
RN = B + "r?" + B + "n"
DQ = B + Q + "[^" + B + Q + B + "r" + B + "n]*" + B + Q
SQ = S + "[^" + S + B + "r" + B + "n]*" + S
HEAD = "(?:" + T + ")" + TAB + "*"
TAIL = "(?:" + J + "+|" + DQ + "|" + SQ + ")"

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"

SHAPES = {
    "Z4-brk1": HEAD + J + "+" + TAB + "*" + RN + TAB + "*" + TAIL,
    "Z4-brkrun": HEAD + J + "+" + "(?:" + TAB + "*" + RN + TAB + "*)+" + TAIL,
    "Z4-run-brkrun": HEAD + J + "+(?:" + TAB + "+" + J + "+)*" + "(?:" + TAB + "*" + RN + TAB + "*)+" + TAIL,
    "Z8 1tok-brkrun": HEAD + J + "+" + "(?:" + TAB + "*" + RN + TAB + "*)+" + "(?:" + DQ + "|" + SQ + "|" + J + "+)",
    "Z9 1tok-brkrun-nospace": HEAD + J + "+" + RN + TAB + "*" + TAIL,
}
CASES = [
    ("C10", "Authorization: Bearer abc\n" + SEC),
    ("C11", "Authorization: Bearer\n\n" + SEC),
    ("C10b", "Authorization: Bearer\n\n\n" + SEC),
    ("N5c", "Authorization: Bearer\n" + M + "\ndoc=17"),
    ("N5d", "Authorization: Bearer\n  " + M),
    ("N5", "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize"),
    ("D2", "Authorization: Bearer \n" + SEC),
    ("D7", "stage=summarize Authorization: Bearer\n" + SEC + "\nrequest_id=req-1"),
]
for name, x in SHAPES.items():
    full = re.compile(r"(?i)(?P<key>(?<![A-Za-z0-9])authorization\s*[:=]\s*|"
                      r"(?<![A-Za-z0-9])bearer\s+)(?P<value>"
                      + DQ + "|" + SQ + "|" + x + "|" + J + TAB + "*(?:" + TAB + "+" + J + "+)*)")
    print("==", name)
    for cid, t in CASES:
        m = full.search(t)
        print(f"    {cid:5s} match={m.group(0)!r}" if m else f"    {cid:5s} match=None")
