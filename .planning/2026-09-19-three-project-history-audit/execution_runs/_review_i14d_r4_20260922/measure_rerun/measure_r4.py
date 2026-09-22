"""Measure `iso/product_narrow_r4` and a widened-scheme candidate, side by side.

r4 as built carries ONLY fix A (F-REV-R3-01: the two `?` characters removed from the
after-break character classes). Fix B (F-REV-R3-04: the scheme class requires a leading
letter, which is narrower than the ABNF the comment cites and is a persistence regression
against `product_base` for non-letter-initial schemes) is NOT in the tree; it is measured
here by rebinding the pattern in memory, so the two fixes can be judged apart.

Candidates:
  r4-as-built   the tree as it stands
  r4-widened    the same, with the scheme token class widened to the full RFC 7230 tchar
                (`[A-Za-z]...*` -> `[...]+`), i.e. a non-letter first character allowed

For each: oracle failures, rule-table failures, and the two probe families (the reviewer's
C1-C12 matrix and the non-letter-initial schemes it measured).

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

NARROW_TOKEN = "[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*"
WIDE_TOKEN = "[A-Za-z0-9!#$%&'*+.^_`|~-]+"

# the reviewer's matrix (reviewer_report_r3.md / reviewer_report_r2.md section 2.3)
REVIEWER_MATRIX = [
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

# F-REV-R3-01 and F-REV-R3-04 families
R3_FAMILIES = [
    ("dq-with-question-mark", 'Authorization: Bot\n"' + SEC + '?x"'),
    ("sq-with-question-mark", "Authorization: Bot\n'" + SEC + "?x'"),
    ("dq-no-question-mark", 'Authorization: Bot\n"' + SEC + '"'),
    ("non-letter-digit-scheme", "Authorization: 2foo\n" + SEC + "\ndoc=17"),
    ("non-letter-bang-scheme", "Authorization: !foo\n" + SEC + "\ndoc=17"),
    ("letter-scheme", "Authorization: afoo\n" + SEC + "\ndoc=17"),
    ("non-letter-marker", "Authorization: 2foo\n" + MARK + "\ndoc=17"),
]

OVER_REDACTION = [
    ("OR1", "Authorization: Bearer\ndoc=17"),
    ("OR2", "Authorization: Bearer\nrequest_id=req-1"),
]


def load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build_pattern(ob, token_class: str) -> re.Pattern:
    """Rebuild the auth pattern with a given scheme-token class, from the product's constants."""
    split = (r"(?:" + token_class + r")[ \t]*"
             r"(?:(?:\r?\n)[ \t]*)+"
             r"(?:" + ob._AUTH_BARE_VALUE + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')")
    return re.compile(
        r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
        + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
        + split + r"|" + ob._AUTH_BARE_VALUE + r")")


def measure(ob, oracle, rule, label: str, token_class, tree_pattern=None) -> dict:
    # The candidate for "the tree exactly as it stands" must use the pattern the tree had
    # AT IMPORT.  An earlier version read `ob._AUTH_PATTERN` here, but the previous candidate
    # had already rebound that global, so the two candidates silently measured the SAME
    # pattern -- a state leak between measurements, and it made the report say fix B changed
    # nothing when in fact it closes the non-letter family. Recorded, not quietly fixed.
    if token_class is None:
        if tree_pattern is None:
            raise SystemExit("FATAL: the tree-as-built candidate needs the import-time pattern")
        pattern = tree_pattern
    else:
        pattern = build_pattern(ob, token_class)
    ob._AUTH_PATTERN = pattern

    oracle_fail = []
    for case_id, kind, text, expected, contains, expect_len, residual in oracle.CASES:
        out = ob.redact_text(text)
        checks = [out == expected,
                  all(c in out for c in contains),
                  (expect_len is None) or (len(out) == expect_len)]
        if residual:
            checks = [out == residual]
        if not all(checks):
            oracle_fail.append(case_id)

    rule_fail = [cid for cid, text, exp, kind in rule.TABLE if ob.redact_text(text) != exp]

    leaks = {}
    for cid, text in REVIEWER_MATRIX + R3_FAMILIES:
        out = ob.redact_text(text)
        leaks[cid] = (SEC in out) or (MARK in out)

    over = {}
    for cid, text in OVER_REDACTION:
        out = ob.redact_text(text)
        over[cid] = out

    return {
        "token_class": token_class,
        "oracle_failures": oracle_fail,
        "rule_failures": rule_fail,
        "leaking": sorted(k for k, v in leaks.items() if v),
        "leak_map": leaks,
        "over_redaction": over,
    }


def main() -> int:
    sys.path.insert(0, str(R4_SRC))
    from company_wiki.source_catalog import observability as ob

    oracle = load("oracle", HARNESS / "run_i14d_oracle.py")
    rule = load("rule", HARNESS / "run_rule_table_i14d.py")

    # The tree now carries BOTH fixes, so the two candidates are separated by REBINDING the
    # token class in memory rather than by two trees:
    #   fix_A_only   the tree's own pattern rebuilt with the r3 token class -- i.e. what the
    #                tree would be if only the '?' fix had been applied
    #   fix_A_and_B  the tree exactly as it stands
    tree_pattern = ob._AUTH_PATTERN          # captured BEFORE any candidate rebinds it
    results = {
        "fix_A_only": measure(ob, oracle, rule, "fix_A_only", NARROW_TOKEN, tree_pattern),
        "fix_A_and_B": measure(ob, oracle, rule, "fix_A_and_B", None, tree_pattern),
    }

    out = {
        "card": "I-14-D",
        "iteration": "r4",
        "tree": "iso/product_narrow_r4",
        "fix_a": "F-REV-R3-01: the two '?' characters removed from the after-break character classes",
        "fix_b_measured_but_not_applied": "F-REV-R3-04: scheme token class widened from [A-Za-z]...* to the full tchar class",
        "method": "for the widened candidate the pattern is rebuilt in memory from the product's own constants; the tree is untouched",
        "candidates": results,
    }
    (HERE / "r4_measurement.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    for name, r in results.items():
        print("%-14s oracle_fail=%d rule_fail=%d" % (name, len(r["oracle_failures"]), len(r["rule_failures"])))
        print("   leaking: %s" % r["leaking"])
        for cid, o in r["over_redaction"].items():
            print("   over %-4s %r" % (cid, o))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
