"""Scratch: prove the authored r3 definition is behaviourally identical to the prototype."""
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

# the prototype expression written with the ORIGINAL quoting, character for character
J = "[^" + B + "s,;&" + B + Q + S + "|]"
PROTO = ((r"(?:" + ns["_AUTH_SCHEME_TOKEN"] + r")[ \t]*"
          r"(?:" + J + r"[ \t]*\r?\n[ \t]*)*"
          r"(?:" + J + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')"))
print("authored  =", repr(SPLIT))
print("prototype =", repr(PROTO))
print("string-identical:", SPLIT == PROTO)
print()

P1 = re.compile(SPLIT)
P2 = re.compile(PROTO)
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
CASES = [
    "Bearer Negotiate\n" + SEC + "\ndoc=17",
    "Bearer\n" + SEC, "Bearer\r\n" + SEC, "Bearer\n  " + SEC, "Bearer  \n" + SEC,
    "Bearer\n\n" + SEC, "Bearer abc\n" + SEC, 'Bearer\n"' + SEC + '"',
    "Bearer\n" + M + "\ndoc=17", "Bearer\ndoc=17", "Bearer\n  doc=17",
    "Bearer" + M, 'Bearer "' + M + '"', "Bearer " + M + " rejected",
    "Bearer\n\n", "Bearer\n", "Bearer", "Bearer\n\n\n\n" + SEC,
    "Bearer\t" + SEC, "Bearer\x0b" + SEC, "token\n" + M,
]
bad = 0
for t in CASES:
    a, b = P1.match(t), P2.match(t)
    ga = a.group(0) if a else None
    gb = b.group(0) if b else None
    same = ga == gb
    bad += 0 if same else 1
    print(("ok  " if same else "DIFF"), repr(t[:26]), "->", repr(ga), "" if same else repr(gb))
print()
print("behavioural differences:", bad)
