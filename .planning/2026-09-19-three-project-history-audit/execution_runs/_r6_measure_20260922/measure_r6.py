"""Price candidate pre-break token classes for r6, using the rule the r5 review forced.

F-REV-R5-01: r5's class is a SWAP, not a widening -- it closed '?' and re-opened '&', "'", '|'
which r4 redacted. The rule adopted in response (REM-79): a class change must be judged by BOTH
differences, `old \\ new` and `new \\ old`, not by "the character that was pointed at now passes".

So every candidate below is scored on:
  * the full printable sweep at the pre-break position, reported as old \\ new and new \\ old
  * oracle failures and rule-table failures on the r5 row sets
  * the over-redaction family
  * the registered C10 residual

Candidates:
  r5-value-token   the class r5 shipped        [^\\s,;&\"'|]+
  r4-tchar         the class r4 shipped        [A-Za-z0-9!#$%&'*+.^_`|~-]+
  non-whitespace   [^\\s]+                     -- the whole run up to the line break

Read-only: nothing under the attempt is written.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent / "I-14-D/a20260919-01"
R5_SRC = ATTEMPT / "iso/product_narrow_r5/src"
HARNESS = ATTEMPT / "harness"

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"
MARK = "SYNTHETIC_AUDIT_TOKEN"

R5_CLASS = r"[^\s,;&\"'|]+"
R4_CLASS = r"[A-Za-z0-9!#$%&'*+.^_`|~-]+"
NONWS_CLASS = r"[^\s]+"

# every printable ASCII, swept at the pre-break position
PRINTABLE = [chr(c) for c in range(0x20, 0x7F)]

OVER = [
    ("OR1", "Authorization: Bearer\ndoc=17"),
    ("OR2", "Authorization: Bearer\nrequest_id=req-1"),
    ("OR3", "Authorization: 2024-01-01\nstatus=ok"),
    ("OR4", "Authorization: Bearer abc\n" + SEC),
]


def load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build(ob, cls: str) -> re.Pattern:
    split = (r"(?:" + cls + r")[ \t]*"
             r"(?:(?:\r?\n)[ \t]*)+"
             r"(?:" + ob._AUTH_BARE_VALUE + r"+|\"[^\"\r\n]*\"|'[^'\r\n]*')")
    return re.compile(
        r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
        + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
        + split + r"|" + ob._AUTH_BARE_VALUE + r")")


def sweep(ob, cls: str) -> set:
    """Which single characters at the pre-break position still let the credential through."""
    ob._AUTH_PATTERN = build(ob, cls)
    leaking = set()
    for ch in PRINTABLE:
        text = "Authorization: Bo" + ch + "t\n" + MARK
        if MARK in ob.redact_text(text):
            leaking.add(ch)
    return leaking


def measure(ob, oracle, rule, cls: str) -> dict:
    ob._AUTH_PATTERN = build(ob, cls)
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
    over = {cid: ob.redact_text(t) for cid, t in OVER}
    return {"oracle_failures": ofail, "rule_failures": rfail, "over_redaction": over}


def main() -> int:
    sys.path.insert(0, str(R5_SRC))
    from company_wiki.source_catalog import observability as ob
    oracle = load("oracle", HARNESS / "run_i14d_oracle_r5.py")
    rule = load("rule", HARNESS / "run_rule_table_i14d_r5.py")

    sweeps = {name: sweep(ob, cls) for name, cls in
              (("r5-value-token", R5_CLASS), ("r4-tchar", R4_CLASS),
               ("non-whitespace", NONWS_CLASS))}

    # THE RULE: both differences, not one.
    r5, r4, nw = sweeps["r5-value-token"], sweeps["r4-tchar"], sweeps["non-whitespace"]
    diffs = {
        "r5_minus_r4 (chars r4 redacted that r5 re-opened)": sorted(r4 - r5),
        "r4_minus_r5 (chars r5 closed that r4 leaked)": sorted(r5 - r4),
        "nonwhitespace_minus_r4": sorted(r4 - nw),
        "nonwhitespace_minus_r5": sorted(r5 - nw),
    }

    results = {}
    for name, cls in (("r5-value-token", R5_CLASS), ("r4-tchar", R4_CLASS),
                      ("non-whitespace", NONWS_CLASS)):
        results[name] = dict(measure(ob, oracle, rule, cls),
                             leaking_single_chars=sorted(sweeps[name]),
                             class_def=cls)

    out = {
        "card": "I-14-D", "iteration": "r6",
        "question": "which pre-break token class closes both families -- '?' AND '&' \" ' '|'?",
        "the_rule_applied": "both differences: old \\ new AND new \\ old (REM-79)",
        "sweep_space": "every printable ASCII at the pre-break position, one credential-persistence probe each",
        "differences": diffs,
        "candidates": results,
    }
    (HERE / "r6_measurement.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    for k, v in diffs.items():
        print("%-52s %s" % (k, v))
    print()
    for name, r in results.items():
        print("%-16s oracle_fail=%d rule_fail=%d leaking=%s"
              % (name, len(r["oracle_failures"]), len(r["rule_failures"]),
                 r["leaking_single_chars"]))
        for cid, o in r["over_redaction"].items():
            print("   over %-4s %r" % (cid, o))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
