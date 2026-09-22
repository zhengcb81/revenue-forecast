"""Scratch: shape A with an end-of-line lookahead on the credential token."""
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
RUN = J + "+(?:" + TAB + "+" + J + "+)*"
BRKRUN = "(?:" + TAB + "*" + RN + TAB + "*)+"

SHAPES = {
    "A plain tail": "(?:" + T + ")" + RUN + BRKRUN + "(?:" + J + "+|" + DQ + "|" + SQ + ")",
    "G eol-tail": "(?:" + T + ")" + RUN + BRKRUN + "(?:" + J + "+(?=[ \\t]*(?:\\r?\\n|\\Z))|"
                  + DQ + "|" + SQ + ")",
}

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

for name, split in SHAPES.items():
    ob._AUTH_PATTERN = re.compile(
        r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
        + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
        + split + r"|" + ob._AUTH_BARE_VALUE + r")")
    ofails = []
    for case_id, kind, text, expected, contains, expect_len in oracle.CASES:
        out = ob.redact_text(text)
        if not (out == expected and all(c in out for c in contains)
                and (expect_len is None or len(out) == expect_len)):
            ofails.append(case_id)
    rfails = [cid for cid, text, exp, kind in rule.TABLE if ob.redact_text(text) != exp]
    pleaks = []
    for cid, text, exp, pred in probe.CASES:
        out = ob.redact_text(text)
        secret = probe.M if cid.startswith("M") else probe.SECRET
        if secret in out:
            pleaks.append(cid)
    print(f"--- {name}")
    print("    oracle failures:", ofails)
    print("    rule failures  :", rfails)
    print("    probe leaks    :", pleaks)
    for case_id, kind, text, expected, contains, expect_len in oracle.CASES:
        if case_id in ofails:
            print(f"      {case_id}: got {ob.redact_text(text)!r}  exp {expected!r}")
