"""Scratch: verify the exact middle group that closes C10/C11 without over-matching."""
import re

B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"
T = "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*"
TAB = "[" + " " + B + "t]"
RN = B + "r?" + B + "n"
TAIL = ("(?:" + J + "+|" + B + Q + "[^" + B + Q + B + "r" + B + "n]*" + B + Q + "|"
        + S + "[^" + S + B + "r" + B + "n]*" + S + ")")
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"

# the exact expression that closed C10/C11 earlier:
#   (?: J )? [ \t]* (?: J [ \t]* \r?\n [ \t]* )*
MID = "(?:" + J + ")?" + TAB + "*(?:" + J + TAB + "*" + RN + TAB + "*)*"
PAT = re.compile("(?:" + T + ")[ " + B + "t]*(?:" + MID + ")" + TAIL)
print("PATTERN =", PAT.pattern)
print()

CASES = [
    ("C1", "Negotiate\n" + SEC + "\ndoc=17", "Negotiate\n" + SEC),
    ("C10", "Bearer abc\n" + SEC, "Bearer abc\n" + SEC),
    ("C11", "Bearer\n\n" + SEC, "Bearer\n\n" + SEC),
    ("N5c", "Bearer\n" + SEC + "\ndoc=17", "Bearer\n" + SEC),
    ("N5d", "Bearer\n  " + SEC, "Bearer\n  " + SEC),
    ("N5e", "token\n" + M, "token\n" + M),
    ("N5", "Bearer " + M + "\ndoc=17\nstage=summarize", "Bearer " + M),
    ("O1", "Bearer\ndoc=17", "Bearer\ndoc=17"),
    ("O7", "Bearer\n  doc=17", "Bearer\n  doc=17"),
    ("D2", "Bearer \n" + SEC, "Bearer \n" + SEC),
    ("D5", "Bearer\r\n" + SEC, "Bearer\r\n" + SEC),
    ("U4", "Bearer " + SEC + " rejected", "Bearer " + SEC),
    ("M1", "Bearer\n" + M + "\ndoc=17", "Bearer\n" + M),
]
bad = []
for cid, text, want in CASES:
    m = PAT.match(text)
    got = m.group(0) if m else None
    ok = got == want
    bad.append(cid) if not ok else None
    print(f"{cid:4s} {'ok  ' if ok else 'DIFF'} {got!r}")
print()
print("failures:", bad)
