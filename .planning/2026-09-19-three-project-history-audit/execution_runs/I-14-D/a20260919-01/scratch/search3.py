"""Scratch: test the 'optional inline token + break-run loop + plain tail' shape."""
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
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"

SHAPES = {
    "P1 (?:J)? ws (?:J*ws RN ws)*": "(?:" + J + ")?" + TAB + "*(?:" + J + "*" + TAB + "*"
                                    + RN + TAB + "*)*",
    "P2 (?:J)? ws (?:J*ws RN ws)* +tail": "(?:" + J + ")?" + TAB + "*(?:" + J + "*"
                                          + TAB + "*" + RN + TAB + "*)*",
    "P3 (?:J*ws RN ws)* + tail": "(?:" + J + "*" + TAB + "*" + RN + TAB + "*)*",
    "P4 (?:J* ws RN ws)*(?:J)?": "(?:" + J + "*" + TAB + "*" + RN + TAB + "*)"
                                 + "(?:" + J + ")?",
}
CASES = [
    ("C10", "Bearer abc\n" + SEC, "Bearer abc\n" + SEC),
    ("C11", "Bearer\n\n" + SEC, "Bearer\n\n" + SEC),
    ("C12", 'Bearer\n"' + SEC + '"', None),
    ("N5c", "Bearer\n" + SEC + "\ndoc=17", "Bearer\n" + SEC),
    ("N5d", "Bearer\n  " + SEC, "Bearer\n  " + SEC),
    ("N5", "Bearer " + M + "\ndoc=17\nstage=summarize", "Bearer " + M),
    ("O1", "Bearer\ndoc=17", "Bearer\ndoc=17"),
    ("O7", "Bearer\n  doc=17", "Bearer\n  doc=17"),
    ("U4", "Bearer " + SEC + " rejected", "Bearer " + SEC),
    ("D5", "Bearer\r\n" + SEC, "Bearer\r\n" + SEC),
]
for name, MID in SHAPES.items():
    src = "(?:" + T + ")[ " + B + "t]*(?:" + MID + ")" + TAIL
    try:
        pat = re.compile(src)
    except re.error as exc:
        print(name, "COMPILE FAIL", exc)
        continue
    bad = []
    for cid, text, want in CASES:
        m = pat.match(text)
        got = m.group(0) if m else None
        if want is not None and got != want:
            bad.append((cid, got))
    print(f"{name:36s} fails {[b[0] for b in bad]}")
    print("      ", src)
