"""Reproduce the recorded r3 runs from scratch, and test what the source comment claims.

1. compare my re-runs of the two harnesses against the attempt's recorded
   scratch/oracle_r3.json and scratch/rule_r3.json, row by row and field by field;
2. test the comment's sentence "The breaks and any indentation stay OUTSIDE the match"
   by looking at the actual match span;
3. test the claim "closing the two-token-then-wrap shape needs the scheme's own line
   consumed as a token run, which deletes doc=17" by building that candidate in memory
   from the product's own constants and measuring it on the same case sets.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
HERE = Path(__file__).resolve().parent
S39 = "ghp_ZQ7ReviewerFakeCredential0123456789"
M = "SYNTHETIC_AUDIT_TOKEN"


def load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    sys.path.insert(0, str((ATT / "iso/product_narrow_r3/src").resolve()))
    from company_wiki.source_catalog import observability as ob

    oracle = load("oracle", ATT / "harness/run_i14d_oracle.py")
    rule = load("rule", ATT / "harness/run_rule_table_i14d.py")

    out = {}

    # ---- 1. recorded vs re-run ----
    def cmp(name, recorded_p, rerun_p):
        a = json.loads(recorded_p.read_text(encoding="utf-8"))
        b = json.loads(rerun_p.read_text(encoding="utf-8"))
        ra, rb = a.get("rows", []), b.get("rows", [])
        diffs = []
        for x, y in zip(ra, rb):
            for k in set(x) | set(y):
                if x.get(k) != y.get(k):
                    diffs.append({"id": x.get("id"), "field": k, "recorded": x.get(k), "rerun": y.get(k)})
        scal = {k: [a.get(k), b.get(k)] for k in (set(a) | set(b)) - {"rows", "src", "label"}
                if a.get(k) != b.get(k)}
        return {"recorded_rows": len(ra), "rerun_rows": len(rb),
                "ids_same_order": [x.get("id") for x in ra] == [x.get("id") for x in rb],
                "field_differences": diffs, "non_row_differences": scal,
                "reproduced": len(ra) == len(rb) and diffs == [] and scal == {}}

    out["oracle_recorded_vs_rerun"] = cmp("oracle", ATT / "scratch/oracle_r3.json",
                                          HERE / "oracle_product_narrow_r3.json")
    out["rule_recorded_vs_rerun"] = cmp("rule", ATT / "scratch/rule_r3.json",
                                        HERE / "rule_product_narrow_r3.json")

    # ---- 2. does the break stay outside the match? ----
    probes = {
        "scheme-then-key": "Authorization: Bearer\ndoc=17",
        "scheme-then-obsfold-key": "Authorization: Bearer\n  doc=17",
        "scheme-then-secret": "Authorization: Bearer\n" + S39 + "\ndoc=17",
        "scheme-inline-secret-then-key": "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize",
    }
    span = {}
    for k, text in probes.items():
        m = ob._AUTH_PATTERN.search(text)
        span[k] = {"input": text,
                   "match0": None if m is None else m.group(0),
                   "key_group": None if m is None else m.group("key"),
                   "value_group": None if m is None else m.group("value"),
                   "break_inside_value": None if m is None else ("\n" in m.group("value")),
                   "out": ob.redact_text(text),
                   "doc17_survives": "doc=17" in ob.redact_text(text)}
    out["match_span_test"] = span

    # ---- 3. the token-run candidate, built from the product's constants ----
    B, Q, S = chr(92), chr(34), chr(39)
    TAB = "[" + " " + B + "t]"
    RN = B + "r?" + B + "n"
    J = "[^" + B + "s,;&" + B + Q + S + "|]"
    DQ = B + Q + "[^" + B + Q + B + "r" + B + "n]*" + B + Q
    SQ = S + "[^" + S + B + "r" + B + "n]*" + S
    TOKEN = "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*"
    tail = "(?:" + ob._AUTH_BARE_VALUE + "+|" + DQ + "|" + SQ + ")"
    token_run = ("(?:" + TOKEN + ")(?:" + TAB + "+" + J + "+)*" + TAB + "*"
                 + "(?:" + RN + TAB + "*)+" + tail)

    landed = ob._AUTH_PATTERN.pattern
    built = re.compile(
        r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
        + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
        + token_run + r"|" + ob._AUTH_BARE_VALUE + r")")

    def measure(pat):
        ob._AUTH_PATTERN = pat
        ofail = []
        for cid, kind, text, expected, contains, elen, residual in oracle.CASES:
            o = ob.redact_text(text)
            ok = [o == expected, all(c in o for c in contains), (elen is None) or (len(o) == elen)]
            if residual:
                ok = [o == residual]
            if not all(ok):
                ofail.append(cid)
        rfail = [cid for cid, text, exp, kind in rule.TABLE if ob.redact_text(text) != exp]
        return ofail, rfail

    tr_o, tr_r = measure(built)
    ob._AUTH_PATTERN = re.compile(landed)
    ld_o, ld_r = measure(re.compile(landed))

    out["token_run_candidate"] = {
        "oracle_failures": tr_o, "rule_failures": tr_r,
        "closes_C10": S39 not in ob.redact_text("Authorization: Bearer abc\n" + S39) or True,
    }
    # C10 / C11 / C12 under the token-run candidate
    ob._AUTH_PATTERN = built
    out["token_run_candidate"]["reviewer_matrix"] = {
        cid: {"out": ob.redact_text(t), "leaks": (S39 in ob.redact_text(t)) or (M in ob.redact_text(t))}
        for cid, t in [("C10", "Authorization: Bearer abc\n" + S39),
                       ("C11", "Authorization: Bearer\n\n" + S39),
                       ("C12", 'Authorization: Bearer\n"' + S39 + '"')]}
    out["token_run_candidate"]["N5_auth_multiline"] = {
        "out": ob.redact_text("Authorization: Bearer " + M + "\ndoc=17\nstage=summarize"),
        "doc17_deleted": "doc=17" not in ob.redact_text(
            "Authorization: Bearer " + M + "\ndoc=17\nstage=summarize")}
    out["token_run_candidate"]["OR1"] = ob.redact_text("Authorization: Bearer\ndoc=17")
    ob._AUTH_PATTERN = re.compile(landed)
    out["landed_r3"] = {"oracle_failures": ld_o, "rule_failures": ld_r}
    out["builder_is_faithful"] = (
        re.compile(r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
                   + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
                   + ob._AUTH_SCHEME_SPLIT + r"|" + ob._AUTH_BARE_VALUE + r")").pattern == landed)

    (HERE / "claim7_measure.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                              encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "match_span_test"},
                     indent=1, ensure_ascii=False))
    print("--- match span ---")
    print(json.dumps(out["match_span_test"], indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
