"""Scratch: systematic search over the tail structure, full case set."""
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
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"

G = J + TAB + "*" + RN + TAB + "*"

STRUCTS = {
    "S1 tail=(J+|DQ|SQ)": "(?:" + G + ")*(?:" + J + "+|" + DQ + "|" + SQ + ")",
    "S2 tail-nested": "(?:" + G + ")*(?:" + RN + TAB + "*(?:" + G + ")*(?:"
                       + J + "+|" + DQ + "|" + SQ + ")|" + J + "+|" + DQ + "|" + SQ + ")",
    "S3 tail-brkfirst": "(?:" + RN + TAB + "*(?:" + G + ")*(?:" + J + "+|" + DQ
                        + "|" + SQ + ")|" + J + "+|" + DQ + "|" + SQ + ")",
    "S4 tail-brk-or-tok": "(?:" + J + "+|" + DQ + "|" + SQ + "|" + RN + TAB + "*(?:"
                          + G + ")*(?:" + J + "+|" + DQ + "|" + SQ + "))",
}
CASES = [
    ("C10", "Bearer abc\n" + SEC, "Bearer abc\n" + SEC),
    ("C11", "Bearer\n\n" + SEC, "Bearer\n\n" + SEC),
    ("C12", 'Bearer\n"' + SEC + '"', 'Bearer\n"' + SEC + '"'),
    ("N5c", "Bearer\n" + SEC + "\ndoc=17", "Bearer\n" + SEC),
    ("N5d", "Bearer\n  " + SEC, "Bearer\n  " + SEC),
    ("N5", "Bearer " + M + "\ndoc=17\nstage=summarize", "Bearer " + M),
    ("O1", "Bearer\ndoc=17", "Bearer\ndoc=17"),
    ("O7", "Bearer\n  doc=17", "Bearer\n  doc=17"),
    ("U4", "Bearer " + SEC + " rejected", "Bearer " + SEC),
    ("D5", "Bearer\r\n" + SEC, "Bearer\r\n" + SEC),
]
for name, TAIL in STRUCTS.items():
    pat = re.compile("(?:" + T + ")[ " + B + "t]*(?:" + G + ")*" + TAIL)
    bad = []
    for cid, text, want in CASES:
        m = pat.match(text)
        got = m.group(0) if m else None
        if got != want:
            bad.append(cid)
    print(f"{name:22s} fails {bad}")
    print("     ", pat.pattern)
