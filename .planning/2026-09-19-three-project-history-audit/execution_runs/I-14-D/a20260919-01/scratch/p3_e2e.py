"""Scratch: P3 middle group, end-to-end through the real redact_text pipeline."""
import sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"
T = "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*"
TAB = "[" + " " + B + "t]"
RN = B + "r?" + B + "n"
DQ = B + Q + "[^" + B + Q + B + "r" + B + "n]*" + B + Q
SQ = S + "[^" + S + B + "r" + B + "n]*" + S
TAIL = "(?:" + J + "+|" + DQ + "|" + SQ + ")"
MID = "(?:" + J + "*" + TAB + "*" + RN + TAB + "*)*"
SPLIT = "(?:" + T + ")[ " + B + "t]*(?:" + MID + ")" + TAIL

# reuse the real pipeline: monkeypatch the r2 tree's _AUTH_SCHEME_SPLIT and rebuild
src = A / "iso" / "product_narrow" / "src"          # the r2 tree (bytes still intact)
sys.path.insert(0, str(src))
import re
from company_wiki.source_catalog import observability as ob

ob._AUTH_SCHEME_SPLIT = SPLIT
ob._AUTH_PATTERN = re.compile(
    r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
    + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
    + SPLIT + r"|" + ob._AUTH_BARE_VALUE + r")")

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
    ("N5", "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize",
     "Authorization: " + R + "\ndoc=17\nstage=summarize"),
    ("N5b", "Authorization: Bearer " + M + " rejected by provider", "Authorization: " + R),
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
    ("U5", 'Authorization: "Bearer ' + M + '"', "Authorization: " + R),
    ("U6", "password: 'iron steel'", "password: " + R),
]
fails = []
for cid, text, want in CASES:
    got = ob.redact_text(text)
    if got != want:
        fails.append(cid)
        print(f"{cid:5s} MISMATCH got={got!r} want={want!r}")
print(f"cases {len(CASES)}  mismatches {len(fails)}  {fails}")
