"""Scratch: run the r2 ORACLE and RULE TABLE against the C1-C12-closing shape.

This measures exactly what the trade-off costs, using the attempt's own tables.
"""
import importlib.util
import json
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
TAIL = "(?:" + J + "+|" + DQ + "|" + SQ + ")"
RUN = J + "+(?:" + TAB + "+" + J + "+)*"
BRKRUN = "(?:" + TAB + "*" + RN + TAB + "*)+"
SPLIT = "(?:" + T + ")" + RUN + BRKRUN + TAIL
# variant F: the credential must not be a diagnostic key (a token that starts a
# `key=value` line would be followed by `=`), so require a non-key token.
SPLIT_F = ("(?:" + T + ")" + RUN + BRKRUN + "(?:" + J + "+(?![=:])|" + DQ + "|" + SQ + ")")
# variant G: credential token must be the last thing on its line
SPLIT_G = ("(?:" + T + ")" + RUN + BRKRUN + "(?:" + J + "+(?=[ \\t]*(?:\\r?\\n|\\Z))|"
           + DQ + "|" + SQ + ")")

for name, split in (("A", SPLIT), ("F", SPLIT_F), ("G", SPLIT_G)):
    print(f"--- shape {name} ---")
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
    print("   oracle failures:", ofails)
    print("   rule   failures:", rfails)


sys.path.insert(0, str(A / "iso" / "product_narrow" / "src"))
from company_wiki.source_catalog import observability as ob  # noqa: E402

ob._AUTH_PATTERN = re.compile(
    r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
    + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
    + SPLIT + r"|" + ob._AUTH_BARE_VALUE + r")")

# reuse the attempt's own tables, evaluated against this shape
spec = importlib.util.spec_from_file_location("oracle", A / "harness" / "run_i14d_oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
spec2 = importlib.util.spec_from_file_location("rule", A / "harness" / "run_rule_table_i14d.py")
rule = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(rule)
