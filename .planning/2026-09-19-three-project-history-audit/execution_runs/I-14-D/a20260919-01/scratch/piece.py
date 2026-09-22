"""Scratch: extract the piece that actually closes C10/C11 by direct comparison."""
import re

B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"
T = "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*"
TAB = "[" + " " + B + "t]"
RN = B + "r?" + B + "n"
TAIL_A = "(?:" + J + "+|" + B + Q + "[^" + B + Q + B + "r" + B + "n]*" + B + Q + "|" + S + "[^" + S + B + "r" + B + "n]*" + S + ")"

# three candidate middle groups, all meant to be equivalent
MID_VARIANTS = {
    "bare-class": "(?:" + J + TAB + "*" + RN + TAB + "*)*",
    "grouped-class": "(?:(?:" + J + ")" + TAB + "*" + RN + TAB + "*)*",
    "grouped-class-opt": "(?:(?:" + J + ")" + TAB + "*" + RN + TAB + "*)*",
}
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
probes = [("C10", "Bearer abc\n" + SEC), ("C11", "Bearer\n\n" + SEC),
          ("N5c", "Bearer\n" + SEC + "\ndoc=17"), ("O1", "Bearer\ndoc=17")]

for name, MID in MID_VARIANTS.items():
    pat = re.compile("(?:" + T + ")[" + " " + B + "t]*(?:" + MID + ")?" + TAIL_A)
    print("==", name)
    print("   ", pat.pattern)
    for cid, t in probes:
        m = pat.match(t)
        print(f"    {cid:4s} -> {m.group(0)!r}" if m else f"    {cid:4s} -> None")
print()
# and the exact form the authoring script emits for the middle group
MID_EMITTED = "(?:" + J + TAB + "*" + RN + TAB + "*)*"
pat = re.compile("(?:" + T + ")[" + " " + B + "t]*(?:" + MID_EMITTED + ")?" + TAIL_A)
print("emitted-shape:", pat.pattern)
for cid, t in probes:
    m = pat.match(t)
    print(f"    {cid:4s} ->", repr(m.group(0)) if m else None)
print()
# now WITHOUT the trailing '?' (i.e. required), matching what the template currently has
pat2 = re.compile("(?:" + T + ")[" + " " + B + "t]*" + MID_EMITTED + TAIL_A)
print("no-optional:", pat2.pattern)
for cid, t in probes:
    m = pat2.match(t)
    print(f"    {cid:4s} ->", repr(m.group(0)) if m else None)
