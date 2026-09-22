"""Scratch: audit the candidate's structure against the case that closes C10/C11."""
import re

B = chr(92)
T = r"[A-Za-z][A-Za-z0-9!#$%&" + chr(39) + r"*+.^_`|~-]*"
J = "[^" + B + "s,;&" + B + chr(34) + chr(39) + "|]"
TAIL = "(?:" + J + "+|" + B + chr(34) + "[^" + B + chr(34) + B + "r" + B + "n]*"
TAIL += B + chr(34) + "|" + chr(39) + "[^" + chr(39) + B + "r" + B + "n]*" + chr(39) + ")"

CAND = re.compile("(?:" + T + ")[ " + B + "t]*(?:" + J + "*[ " + B + "t]*" + B + "r?"
                  + B + "n[ " + B + "t]*)*" + TAIL)
print("CAND =", CAND.pattern)

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
probes = {
    "C10  bearer abc" + "\n" + "SEC": "Bearer abc\n" + SEC,
    "C11  bearer blank": "Bearer\n\n" + SEC,
    "N5c  bearer nl": "Bearer\n" + SEC + "\ndoc=17",
    "O1   diag key": "Bearer\ndoc=17",
    "U4   same line": "Bearer " + SEC + " rejected",
}
for name, t in probes.items():
    m = CAND.match(t)
    print(f"{name:20s} len(text)={len(t):3d} -> {m.group(0)!r}  (group len {len(m.group(0))})")

print()
# the SAME pattern but with the inline token REQUIRED to be present at most once
CAND2 = re.compile("(?:" + T + ")[ " + B + "t]*(?:" + J + ")?[ " + B + "t]*(?:" + J
                   + "*[ " + B + "t]*" + B + "r?" + B + "n[ " + B + "t]*)*" + TAIL)
print("CAND2 =", CAND2.pattern)
for name, t in probes.items():
    m = CAND2.match(t)
    print(f"{name:20s} -> {m.group(0)!r}  (group len {len(m.group(0))})")
