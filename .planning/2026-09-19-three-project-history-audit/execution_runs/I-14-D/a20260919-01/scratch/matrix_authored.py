"""Scratch: run the full variant matrix against the AUTHORED r3 definition."""
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
TOKEN = ns["_AUTH_SCHEME_TOKEN"]

FULL = re.compile(r"(?i)(?P<key>(?<![A-Za-z0-9])authorization\s*[:=]\s*|"
                  r"(?<![A-Za-z0-9])bearer\s+)(?P<value>"
                  + r"\"[^\"\r\n]*\"|'[^'\r\n]*'|" + SPLIT + r"|"
                  + J + r"+(?:[ \t]+" + J + r"+)*)")

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
R = "<redacted>"
CASES = [
    ("C1", "Authorization: Negotiate\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C2", "Authorization: AWS4-HMAC-SHA256\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C3", "Authorization: SCRAM-SHA-256\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C4", "Authorization: Hawk\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C5", "Authorization: Bot\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C6", "Authorization: Mutual\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C7", "Authorization: vapid\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C8", "Authorization: HOBA\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C9", "Authorization: Zzz\n" + SEC + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("C10", "Authorization: Bearer abc\n" + SEC, "Authorization: " + R),
    ("C11", "Authorization: Bearer\n\n" + SEC, "Authorization: " + R),
    ("C12", 'Authorization: Bearer\n"' + SEC + '"', "Authorization: " + R),
    ("NEG", "Authorization: Negotiate\n" + M + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("N5c", "Authorization: Bearer\n" + M + "\ndoc=17", "Authorization: " + R + "\ndoc=17"),
    ("N5d", "Authorization: Bearer\n  " + M, "Authorization: " + R),
    ("N5e", "authorization: token\n" + M, "authorization: " + R),
    ("N5", "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize", "Authorization: " + R + "\ndoc=17\nstage=summarize"),
    ("RM", "Authorization: Bearer\nZQ7_REVIEWER_MARKER_9f3c", "Authorization: " + R),
    ("D2", "Authorization: Bearer \n" + SEC, "Authorization: " + R),
    ("D3", "Authorization:Bearer\n" + SEC, "Authorization:" + R),
    ("D5", "Authorization: Bearer\r\n" + SEC, "Authorization: " + R),
    ("D7", "stage=summarize Authorization: Bearer\n" + SEC + "\nrequest_id=req-1",
     "stage=summarize Authorization: " + R + "\nrequest_id=req-1"),
    ("O1", "Authorization: Bearer\ndoc=17", "Authorization: " + R),
    ("O2", "Authorization: Bearer\nrequest_id=req-1", "Authorization: " + R),
    ("O3", "Authorization: Bearer\nstage=summarize", "Authorization: " + R),
    ("O4", "Authorization: token\ndoc=17\nstage=summarize", "Authorization: " + R + "\nstage=summarize"),
    ("O5", "proxy-authorization: Bearer\ndoc=17", "proxy-authorization: " + R),
    ("O6", "Authorization: Bearer\r\ndoc=17", "Authorization: " + R),
    ("O7", "Authorization: Bearer\n  doc=17", "Authorization: " + R),
    ("U1", "monkey=banana doc=1\nstage=x", "monkey=banana doc=1\nstage=x"),
    ("U2", "url=https://example/x?page=2", "url=https://example/x?page=2"),
    ("U4", "Authorization: Bearer " + M + " rejected by provider", "Authorization: " + R),
    ("U5", 'Authorization: "Bearer ' + M + '"', "Authorization: " + R),
]
fails = []
for cid, text, want in CASES:
    got = FULL.sub(lambda m: m.group("key") + R, text)
    if got != want:
        fails.append(cid)
        print(f"{cid:5s} MISMATCH got={got!r} want={want!r}")
print("cases:", len(CASES), " mismatches:", len(fails), fails)
