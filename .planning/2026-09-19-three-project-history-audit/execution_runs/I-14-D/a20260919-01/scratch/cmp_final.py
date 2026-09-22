"""Scratch: exact comparison of the authored pattern with the audited good one."""
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
SPLIT = ns["_AUTH_SCHEME_SPLIT"]
T = ns["_AUTH_SCHEME_TOKEN"]

TAIL = ("(?:" + J + "+|" + B + Q + "[^" + B + Q + B + "r" + B + "n]*" + B + Q + "|"
        + S + "[^" + S + B + "r" + B + "n]*" + S + ")")
GOOD = "(?:" + T + ")[ " + B + "t]*(?:" + J + "[" + " " + B + "t]*" + B + "r?" + B + "n[ " + B + "t]*)*" + TAIL

print("SPLIT =", repr(SPLIT))
print("GOOD  =", repr(GOOD))
print("identical:", SPLIT == GOOD)
print()
for name, pat in (("SPLIT", SPLIT), ("GOOD", GOOD)):
    print(name, "->", repr(pat))
print()
# align the two strings to show where they diverge
import difflib
for line in difflib.unified_diff([GOOD], [SPLIT], "GOOD", "SPLIT", lineterm=""):
    print(line)
