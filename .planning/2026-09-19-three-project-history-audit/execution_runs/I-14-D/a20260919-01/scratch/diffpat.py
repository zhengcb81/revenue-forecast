"""Scratch: char-by-char diff of the authored pattern vs the known-good one."""
import re
from pathlib import Path

B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"

tmpl = (Path(__file__).resolve().parent / "r3_block_template.txt").read_text(encoding="utf-8")
resolved = tmpl.replace("_AUTH_SCHEME_DELIMS", "_DELIM")
resolved = resolved.replace("@T@", B + "t").replace("@N@", B + "r?" + B + "n")
ns = {"_DELIM": J}
exec(resolved, ns)
GOT = ns["_AUTH_SCHEME_SPLIT"]
T = ns["_AUTH_SCHEME_TOKEN"]
TAIL = ("(?:" + J + "+|" + B + Q + "[^" + B + Q + B + "r" + B + "n]*" + B + Q + "|"
        + S + "[^" + S + B + "r" + B + "n]*" + S + ")")
WANT = ("(?:" + T + ")[ " + B + "t]*(?:" + J + "*[ " + B + "t]*" + B + "r?" + B
        + "n[ " + B + "t]*)*" + TAIL)

print("GOT  =", repr(GOT))
print("WANT =", repr(WANT))
print()
for i, (a, b) in enumerate(zip(GOT, WANT)):
    if a != b:
        print(f"first difference at {i}: GOT {a!r} vs WANT {b!r}")
        print("   GOT  ...", repr(GOT[max(0, i - 30):i + 30]))
        print("   WANT ...", repr(WANT[max(0, i - 30):i + 30]))
        break
else:
    print("no difference in the common prefix; lengths", len(GOT), len(WANT))
print()
print("equal:", GOT == WANT)
print()
# and behaviourally, on the two hard cases
P = re.compile(GOT)
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
for t in ("Bearer abc\n" + SEC, "Bearer\n\n" + SEC):
    m = P.match(t)
    print(repr(t[:14]), "->", repr(m.group(0)) if m else None)
