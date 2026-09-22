"""Scratch: what does EACH existing tree persist for the residual variants?

Prints the redact_text result of the frozen r2 tree and of the base tree side by
side, so the r3 target can be chosen from measurement instead of from a reading.
"""
import sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"

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
    ("C10b", "Authorization: Negotiate abc\n" + SEC),
    ("C11b", "Authorization: Negotiate\n\n" + SEC + "\ndoc=17"),
    ("N5c", "Authorization: Bearer\n" + M + "\ndoc=17"),
    ("N5d", "Authorization: Bearer\n  " + M),
    ("N5e", "authorization: token\n" + M),
    ("N5", "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize"),
    ("NEG", "Authorization: Negotiate\n" + M + "\ndoc=17"),
    ("O1", "Authorization: Bearer\ndoc=17"),
    ("O2", "Authorization: Bearer\nrequest_id=req-1"),
    ("O3", "Authorization: Bearer\nstage=summarize"),
    ("O4", "Authorization: token\ndoc=17\nstage=summarize"),
    ("O5", "proxy-authorization: Bearer\ndoc=17"),
    ("O6", "Authorization: Bearer\r\ndoc=17"),
    ("O7", "Authorization: Bearer\n  doc=17"),
]

TREES = ["product_base", "product_narrow_r2", "product_narrow"]


def load(tree: str):
    src = A / "iso" / tree / "src"
    for mod in [m for m in sys.modules if m.startswith("company_wiki")]:
        del sys.modules[mod]
    sys.path.insert(0, str(src))
    try:
        from company_wiki.source_catalog.observability import redact_text
        return redact_text
    finally:
        sys.path.remove(str(src))


results = {}
for tree in TREES:
    if not (A / "iso" / tree).is_dir():
        print(f"# tree missing: {tree}")
        continue
    fn = load(tree)
    results[tree] = {cid: fn(text) for cid, text in CASES}

for cid, text in CASES:
    print(f"--- {cid}: {text!r}")
    for tree in TREES:
        if tree in results:
            out = results[tree][cid]
            leak = "LEAK" if (SEC in out or M in out) else "redacted"
            print(f"    {tree:22s} {leak:8s} {out!r}")
