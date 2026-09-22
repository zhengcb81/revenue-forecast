"""Scratch: isolate the N5 over-match in the Z4 shape."""
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
BRK = "(?:" + TAB + "*" + RN + TAB + "*)+"
MID = "(?:" + J + TAB + "*" + RN + TAB + "*)*"
TAIL = "(?:" + J + "+|" + DQ + "|" + SQ + ")"
M = "SYNTHETIC_AUDIT_TOKEN"
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"

SHAPES = {
    "Z4": HEAD + J + "+" + BRK + MID + TAIL,
    "Z4-nomid": HEAD + J + "+" + BRK + TAIL,
    "Z4-brk1": HEAD + J + "+" + TAB + "*" + RN + TAB + "*" + MID + TAIL,
}
for name, x in SHAPES.items():
    p = re.compile(x)
    for label, text in [("N5 ", "Bearer " + M + "\ndoc=17\nstage=summarize"),
                        ("N5c", "Bearer\n" + M + "\ndoc=17"),
                        ("C10", "Bearer abc\n" + SEC)]:
        m = p.match(text)
        print(f"{name:9s} {label} -> {m.group(0)!r}" if m else f"{name:9s} {label} -> None")
    print("   ", x)
