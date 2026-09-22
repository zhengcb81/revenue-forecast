"""Measure candidate responses to F-REV-R4-05, on the r4 tree, in memory.

F-REV-R4-05: `Authorization: <non-tchar-token>\\n<credential>` persists the credential on r4
while `product_base` redacts it -- 31 unregistered, base-regressive shapes.

Two honest responses exist, and this script exists to price them:

  (a) REGISTER it -- add oracle `registered_open` rows and rule-table rows declaring the
      family, the way the two-token-then-wrap shape was declared.
  (b) FIX it -- widen the PRE-BREAK token from the RFC 7230 tchar class to the value-token
      class the rest of the pattern already uses, so `Bo?t` counts as a token.

(b) is only better than (a) if it costs nothing. This measures the cost: oracle failures,
rule-table failures, the reviewer's C1-C12 matrix, the non-tchar family, and the
over-redaction family.

Read-only: nothing under the attempt is written.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent / "I-14-D/a20260919-01"
R4_SRC = ATTEMPT / "iso/product_narrow_r4/src"
HARNESS = ATTEMPT / "harness"

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
MARK = "SYNTHETIC_AUDIT_TOKEN"

TCHAR = r"[A-Za-z0-9!#$%&'*+.^_`|~-]+"
VALUE_TOKEN = r"[^\s,;&\"'|]+"

# the reviewer's matrix
MATRIX = [
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
]

# the F-REV-R4-05 family, plus the shapes the earlier fixes closed
FAMILIES = [
    ("non-tchar-question", "Authorization: Bo?t\n" + MARK),
    ("non-tchar-question-secret", "Authorization: Bo?t\n" + SEC + "\ndoc=17"),
    ("non-tchar-slash", "Authorization: Bo/t\n" + MARK),
    ("non-tchar-equals", "Authorization: Bo=t\n" + MARK),
    ("non-tchar-colon", "Authorization: Bo:t\n" + MARK),
    ("non-letter-digit", "Authorization: 2foo\n" + MARK),
    ("r3-question-quoted", 'Authorization: Bot\n"' + SEC + '?x"'),
]

OVER = [
    ("OR1", "Authorization: Bearer\ndoc=17"),
    ("OR2", "Authorization: Bearer\nrequest_id=req-1"),
    ("OR3", "Authorization: 2024-01-01\nstatus=ok"),
    ("OR4", "Authorization: see the note\nstatus=ok"),
]


def load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build(ob, prebreak: str) -> re.Pattern:
    split = (r"(?:" + prebreak + r")[ \t]*"
             r"(?:(?:\r?\n)[ \t]*)+"
             r"(?:" + ob._AUTH_BARE_VALUE + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')")
    return re.compile(
        r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
        + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
        + split + r"|" + ob._AUTH_BARE_VALUE + r")")


def measure(ob, oracle, rule, prebreak, tree_pattern=None) -> dict:
    ob._AUTH_PATTERN = tree_pattern if prebreak is None else build(ob, prebreak)
    ofail = []
    for cid, kind, text, expected, contains, elen, residual in oracle.CASES:
        out = ob.redact_text(text)
        ok = [out == expected, all(c in out for c in contains),
              (elen is None) or (len(out) == elen)]
        if residual:
            ok = [out == residual]
        if not all(ok):
            ofail.append(cid)
    rfail = [cid for cid, text, exp, kind in rule.TABLE if ob.redact_text(text) != exp]
    leaks = {cid: (SEC in ob.redact_text(t)) or (MARK in ob.redact_text(t))
             for cid, t in MATRIX + FAMILIES}
    over = {cid: ob.redact_text(t) for cid, t in OVER}
    return {
        "oracle_failures": ofail, "rule_failures": rfail,
        "leaking": sorted(k for k, v in leaks.items() if v), "leak_map": leaks,
        "over_redaction": over,
    }


def main() -> int:
    sys.path.insert(0, str(R4_SRC))
    from company_wiki.source_catalog import observability as ob
    oracle = load("oracle", HARNESS / "run_i14d_oracle_r4.py")
    rule = load("rule", HARNESS / "run_rule_table_i14d_r4.py")

    tree_pattern = ob._AUTH_PATTERN
    results = {
        "r4-as-built": measure(ob, oracle, rule, None, tree_pattern),
        "widen-to-value-token": measure(ob, oracle, rule, VALUE_TOKEN, tree_pattern),
    }
    out = {
        "card": "I-14-D", "iteration": "r5",
        "question": "price the two responses to F-REV-R4-05: register the family, or widen the pre-break token",
        "candidates": results,
    }
    (HERE / "r5_measurement.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    for name, r in results.items():
        print("%-22s oracle_fail=%d rule_fail=%d" % (name, len(r["oracle_failures"]), len(r["rule_failures"])))
        print("   leaking: %s" % r["leaking"])
        for cid, o in r["over_redaction"].items():
            print("   over %-4s %r" % (cid, o))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
