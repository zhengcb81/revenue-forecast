"""Scratch: search middle-group shapes for one that closes every case at once."""
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

JQ = B + Q
E = J + "+"
F = TAB + "*" + RN + TAB + "*"
G = J + TAB + "*" + RN + TAB + "*"

VARIANTS = {
    "V1 (?:E?)G*": "(?:" + J + "?)" + G + "*",
    "V2 (?:E? (?:G)*)": "(?:" + J + "?" + "(?:" + G + ")*" + ")",
    "V3 F(G)*(E?)": F + "(?:" + G + ")*(" + J + "?)",
    "V4 (?:F)(?:G)*(?:E?)": F + "(?:" + G + ")*(?:" + J + "?)",
    "V5 G*(?:E?)": G + "*(" + J + "?)",
    "V6 (?:G)*(?:E?)": "(?:" + G + ")*(" + J + "?)",
    "V7 (?:E?)(?:G)*(?:E)": "(?:" + J + "?)" + "(?:" + G + ")*" + "(?:" + J + ")",
}
CASES = [
    ("C10", "Bearer abc\n" + SEC),
    ("C11", "Bearer\n\n" + SEC),
    ("N5c", "Bearer\n" + SEC + "\ndoc=17"),
    ("N5d", "Bearer\n  " + SEC),
    ("N5e", "token\n" + M),
    ("N5", "Bearer " + M + "\ndoc=17\nstage=summarize"),
    ("O1", "Bearer\ndoc=17"),
    ("O7", "Bearer\n  doc=17"),
    ("D5", "Bearer\r\n" + SEC),
    ("D2", "Bearer \n" + SEC),
    ("U4", "Bearer " + SEC + " rejected"),
    ("M1", "Bearer\n" + M + "\ndoc=17"),
]
EXPECT = {
    "C10": "Bearer abc\n" + SEC,
    "C11": "Bearer\n\n" + SEC,
    "N5c": "Bearer\n" + SEC,
    "N5d": "Bearer\n  " + SEC,
    "N5e": "token\n" + M,
    "N5": "Bearer " + M,
    "O1": "Bearer\ndoc=17",
    "O7": "Bearer\n  doc=17",
    "D5": "Bearer\r\n" + SEC,
    "D2": "Bearer \n" + SEC,
    "U4": "Bearer " + SEC,
    "M1": "Bearer\n" + M,
}
for name, MID in VARIANTS.items():
    try:
        pat = re.compile("(?:" + T + ")[ " + B + "t]*(?:" + MID + ")" + TAIL)
    except re.error as exc:
        print(name, "COMPILE FAIL", exc)
        continue
    bad = []
    for cid, text in CASES:
        m = pat.match(text)
        got = m.group(0) if m else None
        if got != EXPECT[cid]:
            bad.append(cid)
    print(f"{name:24s} fails: {bad}")
