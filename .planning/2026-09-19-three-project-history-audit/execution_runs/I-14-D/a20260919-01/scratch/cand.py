"""Scratch: candidate r3 split pattern, second shape, full matrix + timing."""
import re
import time

J = r'[^\s,;&\"\x27|]'
T = r'[A-Za-z][A-Za-z0-9!#$%&' + "\x27" + r'*+.^_`|~-]*'
DQ = r'\"[^\"\r\n]*\"'
SQ = r"'[^'\r\n]*'"
# repetition group: ONE line of an optional token per iteration (J* so a blank line
# iterates too); tail: a token, or the same reached through further line breaks.
S = (r"(?:" + T + r")[ \t]*(?:" + J + r"*[ \t]*\r?\n[ \t]*)*"
     r"(?:" + J + r"+|" + DQ + r"|" + SQ + r"|(?:\r?\n[ \t]*)"
     r"(?:" + J + r"*[ \t]*\r?\n[ \t]*)*(?:" + J + r"+|" + DQ + r"|" + SQ + r"))")
P = re.compile(r"(?i)(?P<key>(?<![A-Za-z0-9])authorization\s*[:=]\s*|"
               r"(?<![A-Za-z0-9])bearer\s+)(?P<value>"
               + DQ + r"|" + SQ + r"|" + S + r"|" + J + r"+(?:[ \t]+" + J + r"+)*)")

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
    ("O2", "Authorization: Bearer\nrequest_id=req-1"),
    ("O3", "Authorization: Bearer\nstage=summarize"),
    ("O4", "Authorization: token\ndoc=17\nstage=summarize"),
    ("O5", "proxy-authorization: Bearer\ndoc=17"),
    ("O6", "Authorization: Bearer\r\ndoc=17"),
    ("O7", "Authorization: Bearer\n  doc=17"),
    ("U4", "Authorization: Bearer " + M + " rejected by provider"),
    ("U5", 'Authorization: "Bearer ' + M + '"'),
    ("U1", "monkey=banana doc=1\nstage=x"),
    ("U2", "url=https://example/x?page=2"),
    ("U3", "oauth=abc123"),
    ("E4b", "start-" + "x" * 170 + " token=" + M + " " + "y" * 120),
]
for cid, text in CASES:
    out = P.sub(lambda m: m.group("key") + R, text)
    leak = "LEAK" if (SEC in out or M in out) else "ok  "
    print(f"{cid:5s} {leak} {out!r}")

print()
print("=== timing (ReDoS sanity: adversarial inputs) ===")
adv = [
    "Authorization: Bearer" + "\n token*" * 200,
    "Authorization: Bearer" + "\n" * 300,
    "Authorization: Bearer " + "a " * 2000,
    "Authorization: Bearer\n" + "b" * 100000,
    ("Authorization: Bearer\n" + "z" * 40 + "\n") * 200,
]
for t in adv:
    t0 = time.perf_counter()
    P.sub(lambda m: m.group("key") + R, t)
    print(f"  len={len(t):>7}  {time.perf_counter() - t0:.4f}s")
