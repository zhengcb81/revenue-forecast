"""Scratch: validate the AUTHORED r3 template against the real tables, end to end."""
import importlib.util
import re
import sys
from pathlib import Path

A = Path(__file__).resolve().parents[1]
B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"
DELIM = r"[^\s,;&\"'|]"      # the value delimiter class, single token

tmpl = (A / "scratch" / "r3_block_template.txt").read_text(encoding="utf-8")
resolved = tmpl.replace("_AUTH_SCHEME_DELIMS", "_DELIM")
resolved = resolved.replace("@T@", B + "t").replace("@N@", B + "r?" + B + "n")

sys.path.insert(0, str(A / "iso" / "product_narrow" / "src"))
from company_wiki.source_catalog import observability as ob  # noqa: E402

ns = {"_DELIM": DELIM}
exec(resolved, ns)
SPLIT = ns["_AUTH_SCHEME_SPLIT"]
print("SPLIT =", SPLIT)
print()

ob._AUTH_SCHEME_SPLIT = SPLIT
ob._AUTH_PATTERN = re.compile(
    r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
    + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
    + SPLIT + r"|" + ob._AUTH_BARE_VALUE + r")")

spec = importlib.util.spec_from_file_location("oracle", A / "harness" / "run_i14d_oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
spec2 = importlib.util.spec_from_file_location("rule", A / "harness" / "run_rule_table_i14d.py")
rule = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(rule)
spec3 = importlib.util.spec_from_file_location("probe", A / "harness" / "authsplit_probe.py")
probe = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(probe)

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"
VARS = [
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
    ("NEG2", "Authorization: Negotiate\n" + SEC + "\ndoc=17\nrequest_id=req-1"),
]
print("=== variant closure ===")
leaks = []
for cid, text in VARS:
    out = ob.redact_text(text)
    leak = (SEC in out) or (M in out)
    leaks.append(cid) if leak else None
    print(f"  {cid:5s} {'LEAK' if leak else 'ok  '} {out!r}")
print("open variants:", leaks)
print()
ofails = []
for case_id, kind, text, expected, contains, expect_len in oracle.CASES:
    out = ob.redact_text(text)
    if not (out == expected and all(c in out for c in contains)
            and (expect_len is None or len(out) == expect_len)):
        ofails.append(case_id)
print("oracle failures:", ofails)
rfails = [cid for cid, text, exp, kind in rule.TABLE if ob.redact_text(text) != exp]
print("rule failures  :", rfails)
pleaks = []
for cid, text, exp, pred in probe.CASES:
    out = ob.redact_text(text)
    secret = probe.M if cid.startswith("M") else probe.SECRET
    if secret in out:
        pleaks.append(cid)
print("probe leaks    :", pleaks)
