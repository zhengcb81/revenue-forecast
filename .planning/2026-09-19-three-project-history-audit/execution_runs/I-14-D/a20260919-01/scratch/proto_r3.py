"""Scratch: prototype the r3 _AUTH_SCHEME_SPLIT and check the closure matrix."""
import re

T = r"[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*"
J = r"[^\s,;&\"'|]"
Q = r"\"[^\"\r\n]*\"|'[^'\r\n]*'"
S = (r"(?:" + T + r")"
     r"(?:[ \t]*" + J + r"+)?(?:[ \t]*\r?\n)+[ \t]*"
     r"(?:" + J + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')")
KP = (r"(?i)(?P<key>(?<![A-Za-z0-9])authorization\s*[:=]\s*|"
      r"(?<![A-Za-z0-9])bearer\s+)(?P<value>")
BARE = J + r"+(?:[ \t]+" + J + r"+)*"
PAT = re.compile(KP + Q + r"|" + S + r"|" + BARE + r")")

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
RM = "ZQ7_REVIEWER_MARKER_9f3c"
R = "<redacted>"

print("S =", repr(S))
print()
cases = [
    # the 12 reviewer residual variants
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
    ("MARKER-neg", "Authorization: Negotiate\n" + M + "\ndoc=17"),
    # r2 family regression
    ("N5c", "Authorization: Bearer\n" + M + "\ndoc=17"),
    ("N5d", "Authorization: Bearer\n  " + M),
    ("N5e", "authorization: token\n" + M),
    ("D2", "Authorization: Bearer \n" + SEC),
    ("D3", "Authorization:Bearer\n" + SEC),
    ("D5", "Authorization: Bearer\r\n" + SEC),
    ("D7", "stage=summarize Authorization: Bearer\n" + SEC + "\nrequest_id=req-1"),
    ("D8", "Authorization: Bearer\t" + SEC),
    ("D10", "Authorization: Basic\n" + SEC),
    ("RM", "Authorization: Bearer\n" + RM),
    # over-redaction family (F-REV-R2-02)
    ("O1", "Authorization: Bearer\ndoc=17"),
    ("O2", "Authorization: Bearer\nrequest_id=req-1"),
    ("O3", "Authorization: Bearer\nstage=summarize"),
    ("O4", "Authorization: token\ndoc=17\nstage=summarize"),
    ("O5", "proxy-authorization: Bearer\ndoc=17"),
    ("O6", "Authorization: Bearer\r\ndoc=17"),
    ("O7", "Authorization: Bearer\n  doc=17"),
    # untouched family
    ("U1", "monkey=banana doc=1\nstage=x"),
    ("U2", "url=https://example/x?page=2"),
    ("U3", "oauth=abc123"),
    ("U4", "Authorization: Bearer " + M + " rejected by provider"),
    ("U5", 'Authorization: "Bearer ' + M + '"'),
]
for cid, text in cases:
    out = PAT.sub(lambda m: m.group("key") + R, text)
    print(f"{cid:12s} {text!r}")
    print(f"{'':12s} -> {out!r}")
