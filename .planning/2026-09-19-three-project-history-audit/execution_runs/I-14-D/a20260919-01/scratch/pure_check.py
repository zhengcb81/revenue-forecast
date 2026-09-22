"""Scratch: pure-matcher check of the current template on N5 and the variants."""
import re
from pathlib import Path

A = Path(__file__).resolve().parents[1]
B = chr(92)
S = chr(39)
tmpl = (A / "scratch" / "r3_block_template.txt").read_text(encoding="utf-8")
DELIM = r"[^\s,;&\"'|]"
resolved = tmpl.replace("_AUTH_SCHEME_DELIMS", "_DELIM")
resolved = resolved.replace("@T@", B + "t").replace("@N@", B + "r?" + B + "n")
ns = {"_DELIM": DELIM}
exec(resolved, ns)
SPLIT = ns["_AUTH_SCHEME_SPLIT"]
P = re.compile(SPLIT)
print("SPLIT =", SPLIT)
print()
M = "SYNTHETIC_AUDIT_TOKEN"
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
CASES = [
    ("N5", "Bearer " + M + "\ndoc=17\nstage=summarize"),
    ("N5c", "Bearer\n" + M + "\ndoc=17"),
    ("N5d", "Bearer\n  " + M),
    ("C10", "Bearer abc\n" + SEC),
    ("C11", "Bearer\n\n" + SEC),
    ("C12", 'Bearer\n"' + SEC + '"'),
    ("O1", "Bearer\ndoc=17"),
    ("O4", "token\ndoc=17\nstage=summarize"),
    ("D7", "Bearer\n" + SEC + "\nrequest_id=req-1"),
]
for cid, t in CASES:
    m = P.match(t)
    print(f"{cid:4s} -> {m.group(0)!r}" if m else f"{cid:4s} -> None")
