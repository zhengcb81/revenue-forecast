"""Scratch: one more targeted shape -- optional single pre-break token + break run."""
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
TAILQ = "(?:" + J + "+|" + DQ + "|" + SQ + ")"

SHAPES = {
    "S1 opt1tok + brkrun + tail": "(?:" + T + ")" + TAB + "*(?:" + J + TAB + "*)?" + "(?:" + RN + TAB + "*)+" + TAILQ,
    "S2 opt1tok + brk + tail": "(?:" + T + ")" + TAB + "*(?:" + J + TAB + "*)?" + RN + TAB + "*" + TAILQ,
    "S3 opt1tok + brkrun + tail(nospace)": "(?:" + T + ")" + TAB + "*(?:" + J + ")?" + "(?:" + TAB + "*" + RN + TAB + "*)+" + TAILQ,
    "S4 opt-run + brkrun + tail": "(?:" + T + ")" + TAB + "*(?:" + J + "(?:" + TAB + "+" + J + ")*)?" + "(?:" + TAB + "*" + RN + TAB + "*)+" + TAILQ,
}

sys.path.insert(0, str(A / "iso" / "product_narrow" / "src"))
from company_wiki.source_catalog import observability as ob  # noqa: E402

spec = importlib.util.spec_from_file_location("oracle", A / "harness" / "run_i14d_oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
spec2 = importlib.util.spec_from_file_location("rule", A / "harness" / "run_rule_table_i14d.py")
rule = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(rule)

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
]
for name, x in SHAPES.items():
    ob._AUTH_PATTERN = re.compile(
        r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
        + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|" + x
        + r"|" + ob._AUTH_BARE_VALUE + r")")
    openv = [cid for cid, t in VARS
             if (SEC in ob.redact_text(t)) or (M in ob.redact_text(t))]
    ofails = []
    for case_id, kind, text, expected, contains, expect_len in oracle.CASES:
        out = ob.redact_text(text)
        if not (out == expected and all(c in out for c in contains)
                and (expect_len is None or len(out) == expect_len)):
            ofails.append(case_id)
    rfails = [cid for cid, t, e, k in rule.TABLE if ob.redact_text(t) != e]
    print(f"{name:36s} open={openv}  oracle={ofails}  rule={rfails}")
