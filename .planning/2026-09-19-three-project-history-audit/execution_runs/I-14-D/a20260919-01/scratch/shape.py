"""Scratch: identify the exact middle-group shape that closes C10/C11."""
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

VARIANTS = {
    "A optional-token-then-break": "(?:" + J + ")?[ " + B + "t]*(?:" + J + TAB + "*" + RN + TAB + "*)*",
    "B optional-bareclass-break": "[" + " " + B + "t]*(?:" + J + TAB + "*" + RN + TAB + "*)*",
    "C inline-then-breakrun": "(?:" + J + ")?[ " + B + "t]*(?:" + J + "*" + TAB + "*" + RN + TAB + "*)*",
    "D plain": "(?:" + J + TAB + "*" + RN + TAB + "*)*",
}
probes = [
    ("C10", "Bearer abc\n" + SEC, "Bearer abc\n" + SEC),
    ("C11", "Bearer\n\n" + SEC, "Bearer\n\n" + SEC),
    ("N5c", "Bearer\n" + SEC + "\ndoc=17", "Bearer\n" + SEC),
    ("N5d", "Bearer\n  " + SEC, "Bearer\n  " + SEC),
    ("O1", "Bearer\ndoc=17", "Bearer\ndoc=17"),
    ("O7", "Bearer\n  doc=17", "Bearer\n  doc=17"),
    ("U4", "Bearer " + SEC + " rejected", "Bearer " + SEC),
]
for name, MID in VARIANTS.items():
    pat = re.compile("(?:" + T + ")[ " + B + "t]*(?:" + MID + ")" + TAIL)
    ok = 0
    print("==", name)
    for cid, text, want in probes:
        m = pat.match(text)
        got = m.group(0) if m else None
        if cid in ("C10", "C11"):
            good = got == want
        elif cid in ("N5c", "O1", "O7"):
            good = got == want
        else:
            good = got == want
        ok += good
        print(f"    {cid:4s} {'ok  ' if good else 'DIFF'} {got!r}")
    print(f"    score {ok}/{len(probes)}")
