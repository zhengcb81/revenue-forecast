"""Scratch: minimal test of the token-run middle group."""
import re

B = chr(92)
Q = chr(34)
S = chr(39)
D = r"[^\s,;&" + B + Q + S + "|]"
T = "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*"
TAB = "[ " + B + "t]"
RN = B + "r?" + B + "n"
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"

MID = "(?:" + D + "(?:" + TAB + "+" + D + ")*" + TAB + ")?"
BRK = "(?:" + RN + TAB + "*)+"
TAIL = "(?:" + D + "+|" + B + Q + "[^" + B + Q + RN + "]*" + B + Q + "|" + S + "[^" + S + RN + "]*" + S + ")"

tests = {
    "T only": "(?:" + T + ")",
    "T + MID": "(?:" + T + ")?" .replace("?", "") + MID,
    "T + MID + BRK": "(?:" + T + ")" + MID + BRK,
    "T + MID + BRK + TAIL": "(?:" + T + ")" + MID + BRK + TAIL,
    "T + MID(required) + BRK + TAIL": "(?:" + T + ")" + "(?:" + D + "(?:" + TAB + "+" + D + ")*" + TAB + ")" + BRK + TAIL,
}
for name, src in tests.items():
    p = re.compile(src)
    m = p.match("Bearer abc\n" + SEC)
    print(f"{name:34s} -> {m.group(0)!r}" if m else f"{name:34s} -> None")
    print("      ", src)
print()
# is the leftmost-first rule making MID match nothing and TAIL take 'abc'?
p = re.compile("(?:" + T + ")" + MID + BRK + TAIL)
m = p.match("Bearer abc\n" + SEC)
print("match:", repr(m.group(0)) if m else None)
p2 = re.compile("(?:" + T + ")" + MID)
print("T+MID on 'Bearer abc\\n...':", repr(p2.match("Bearer abc\n" + SEC).group(0)))
p3 = re.compile("(?:" + T + ")(?:" + D + "(?:" + TAB + "+" + D + ")*" + TAB + ")?(?:" + D + "+)")
print("T+MID+token:", repr(p3.match("Bearer abc\n" + SEC).group(0)))
