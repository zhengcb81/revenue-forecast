"""Scratch: trace the S2 structure on C10 step by step."""
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

G = J + TAB + "*" + RN + TAB + "*"
TAIL2 = ("(?:" + RN + TAB + "*(?:" + G + ")*(?:" + J + "+|" + DQ + "|" + SQ + ")|"
         + J + "+|" + DQ + "|" + SQ + ")")
pat = re.compile("(?:" + T + ")[ " + B + "t]*(?:" + G + ")*" + TAIL2)
print("pattern =", pat.pattern)

for text in ["Bearer abc\n" + SEC, "Bearer\n\n" + SEC]:
    print()
    print("text    =", repr(text))
    m = pat.match(text)
    print("match   =", repr(m.group(0)) if m else None)
    # incremental: how far does each piece get?
    p1 = re.compile("(?:" + T + ")[ " + B + "t]*")
    m1 = p1.match(text)
    print("  scheme+ws consumes:", repr(m1.group(0)), "-> rest", repr(text[len(m1.group(0)):]))
    rest = text[len(m1.group(0)):]
    p2 = re.compile("(?:" + G + ")*")
    m2 = p2.match(rest)
    print("  (G)* consumes      :", repr(m2.group(0)), "-> rest", repr(rest[len(m2.group(0)):]))
    rest2 = rest[len(m2.group(0)):]
    p3 = re.compile(TAIL2)
    m3 = p3.match(rest2)
    print("  tail consumes      :", repr(m3.group(0)) if m3 else None, "on", repr(rest2))
