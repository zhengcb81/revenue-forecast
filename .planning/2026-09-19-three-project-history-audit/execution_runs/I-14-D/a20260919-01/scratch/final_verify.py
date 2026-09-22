"""Scratch: verify the final r3 split definition against every known case."""
import importlib.util
import re
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

# FINAL r3 definition: the r2 branch with (a) one RFC-7235 scheme token instead of the
# nine-word enumeration, (b) a RUN of line breaks instead of exactly one, and (c) a
# quoted continuation after the break.
SPLIT = ("(?:" + T + ")" + TAB + "*" + "(?:" + RN + TAB + "*)+"
         + "(?:" + J + "+|" + DQ + "|" + SQ + ")")

sys.path.insert(0, str(A / "iso" / "product_narrow" / "src"))
from company_wiki.source_catalog import observability as ob  # noqa: E402

spec = importlib.util.spec_from_file_location("oracle", A / "harness" / "run_i14d_oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
spec2 = importlib.util.spec_from_file_location("rule", A / "harness" / "run_rule_table_i14d.py")
rule = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(rule)
spec3 = importlib.util.spec_from_file_location("probe", A / "harness" / "authsplit_probe.py")
probe = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(probe)

ob._AUTH_PATTERN = re.compile(
    r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
    + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|" + SPLIT
    + r"|" + ob._AUTH_BARE_VALUE + r")")

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
VARIANTS = [
    ("C1", "Authorization: Negotiate\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C2", "Authorization: AWS4-HMAC-SHA256\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C3", "Authorization: SCRAM-SHA-256\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C4", "Authorization: Hawk\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C5", "Authorization: Bot\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C6", "Authorization: Mutual\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C7", "Authorization: vapid\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C8", "Authorization: HOBA\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C9", "Authorization: Zzz\n" + SEC + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("C10", "Authorization: Bearer abc\n" + SEC, None),
    ("C11", "Authorization: Bearer\n\n" + SEC, "Authorization: <redacted>"),
    ("C12", 'Authorization: Bearer\n"' + SEC + '"', "Authorization: <redacted>"),
    ("NEG", "Authorization: Negotiate\n" + M + "\ndoc=17", "Authorization: <redacted>\ndoc=17"),
    ("NEG2", "Authorization: Negotiate\n" + SEC + "\ndoc=17\nrequest_id=req-1",
     "Authorization: <redacted>\ndoc=17\nrequest_id=req-1"),
    ("NEG3", "Authorization: Zzz\n" + M, "Authorization: <redacted>"),
]
print("=== reviewer's 12 residual variants ===")
closed, openv = [], []
for cid, text, want in VARIANTS:
    out = ob.redact_text(text)
    leak = (SEC in out) or (M in out)
    (openv if leak else closed).append(cid)
    mark = "LEAK" if leak else ("ok  " if want is None or out == want else "DIFF")
    print(f"  {cid:5s} {mark} {out!r}")
print("closed:", closed)
print("open  :", openv)
print()
ofails = []
for case_id, kind, text, expected, contains, expect_len in oracle.CASES:
    out = ob.redact_text(text)
    if not (out == expected and all(c in out for c in contains)
            and (expect_len is None or len(out) == expect_len)):
        ofails.append(case_id)
print("oracle failures:", ofails)
print("rule failures  :", [cid for cid, t, e, k in rule.TABLE if ob.redact_text(t) != e])
pleaks = [cid for cid, t, e, p in probe.CASES
          if (probe.M if cid.startswith("M") else probe.SECRET) in ob.redact_text(t)]
print("probe leaks    :", pleaks)
print()
print("SPLIT =", SPLIT)
