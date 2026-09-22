"""Scratch: audit the exact regex backtracking on C10 (no pipeline, raw match)."""
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
TAIL = "(?:" + J + "+|" + DQ + "|" + SQ + ")"
G = J + TAB + "*" + RN + TAB + "*"
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
C10 = "Bearer abc\n" + SEC
C11 = "Bearer\n\n" + SEC

tests = {
    "T1 tail only, G* repeated": "(?:" + T + ")[ " + B + "t]*(?:" + G + ")*" + TAIL,
    "T2 G+ then tail": "(?:" + T + ")[ " + B + "t]*(?:" + G + ")+" + TAIL,
    "T3 (?:G)? then tail": "(?:" + T + ")[ " + B + "t]*(?:" + G + ")?" + TAIL,
    "T4 (?:G)*(?:J)? tail": "(?:" + T + ")[ " + B + "t]*(?:" + G + ")*(?:" + J + ")?" + TAIL,
    "T5 (?:G)* tail nested": "(?:" + T + ")[ " + B + "t]*(?:" + G + ")*(?:" + RN + TAB + "*(?:"
                             + G + ")*" + TAIL + "|" + TAIL + ")",
}
for name, src in tests.items():
    try:
        p = re.compile(src)
    except re.error as exc:
        print(name, "COMPILE FAIL", exc)
        continue
    a = p.match(C10)
    b = p.match(C11)
    print(f"{name}")
    print("    C10 ->", repr(a.group(0)) if a else None)
    print("    C11 ->", repr(b.group(0)) if b else None)
    print("    src :", src)
