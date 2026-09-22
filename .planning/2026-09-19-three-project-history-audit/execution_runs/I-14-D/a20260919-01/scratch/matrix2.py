"""Scratch: final matrix, with the full pattern printed and per-case diagnosis."""
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
print("SPLIT =", SPLIT)
print()

FULL_SRC = (r"(?i)(?P<key>(?<![A-Za-z0-9])authorization\s*[:=]\s*|"
            r"(?<![A-Za-z0-9])bearer\s+)(?P<value>"
            + r"\"[^\"\r\n]*\"|'[^'\r\n]*'|" + SPLIT + r"|" + J
            + r"+(?:[ \t]+" + J + r"+)*)")
FULL = re.compile(FULL_SRC)

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
R = "<redacted>"
CASES = [
    ("C1", "Authorization: Negotiate\n" + SEC + "\ndoc=17"),
    ("C2", "Authorization: AWS4-HMAC-SHA256\n" + SEC + "\ndoc=17"),
    ("C3", "Authorization: SCRAM-SHA-256\n" + SEC + "\ndoc=17"),
    ("C4", "Authorization: Hawk\n" + SEC + "\ndoc=17"),
    ("C5", "Authorization: Bot\n" + SEC + "\ndoc=17"),
    ("C6", "Authorization: Mutual\n" + SEC + "\ndoc=17"),
    ("C7", "Authorization: vapid\n" + SEC + "\ndoc=17"),
    ("C8", "Authorization: HOBA\n" + SEC + "\ndoc=17"),
    ("C9", "Authorization: Zzz\n" + SEC + "\ndoc=17"),
    ("C10", "Authorization: Bearer abc\n" + SEC),
    ("C11", "Authorization: Bearer\n\n" + SEC),
    ("C12", 'Authorization: Bearer\n"' + SEC + '"'),
    ("NEG", "Authorization: Negotiate\n" + M + "\ndoc=17"),
    ("N5c", "Authorization: Bearer\n" + M + "\ndoc=17"),
    ("N5d", "Authorization: Bearer\n  " + M),
    ("N5e", "authorization: token\n" + M),
    ("N5", "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize"),
    ("O1", "Authorization: Bearer\ndoc=17"),
    ("O4", "Authorization: token\ndoc=17\nstage=summarize"),
    ("O5", "proxy-authorization: Bearer\ndoc=17"),
    ("U4", "Authorization: Bearer " + M + " rejected by provider"),
    ("U5", 'Authorization: "Bearer ' + M + '"'),
]
for cid, text in CASES:
    out = FULL.sub(lambda m: m.group("key") + R, text)
    leak = "LEAK" if (SEC in out or M in out) else "ok  "
    print(f"{cid:5s} {leak} {out!r}")
