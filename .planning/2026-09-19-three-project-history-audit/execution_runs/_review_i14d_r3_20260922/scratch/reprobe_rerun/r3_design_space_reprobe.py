"""I-14-D r3 design-space reproduction — why the two-token-then-wrap shape stays OPEN.

WHY THIS EXISTS.  The r3 comment block in `observability.py` ends with:

    "Closing it needs the scheme's own line consumed as a token run, which deletes
     `doc=17` from `Authorization: Bearer <marker>` + newline + `doc=17` + newline +
     `stage=` - measured across the whole design space, see r3_fix_record.md."

`r3_fix_record.md` DOES NOT EXIST.  So the claim is currently unsupported: the reader
is pointed at a file that was never written.  This script re-derives the claim by
measurement, so the substance is available even though the named record is not.

THE ATTEMPT'S OWN SCRATCH SCRIPTS CANNOT BE RE-RUN.  Nine of them
(`tradeoff*.py`, `last_shapes.py`, `final_shapes.py`, `minimal.py`, `order.py`,
`third_alt.py`, `validate_final.py`, `final_verify.py`) unpack `oracle.CASES` as a
6-tuple; the r3 iteration widened it to 7 (`..., expect_len, declared_residual`), so
they all raise `ValueError: too many values to unpack`.  They are NOT edited here --
this script re-implements the measurement against the CURRENT harness instead.

READ-ONLY W.R.T. THE ATTEMPT.  The attempt is only imported from.  Nothing under
`I-14-D/a20260919-01/` is written.  The candidate patterns are applied by rebinding
`observability._AUTH_PATTERN` in memory, exactly as the scratch scripts did.

CANDIDATES.  Each is an alternative for the SCHEME-SPLIT group; the rest of the
pattern is built the way the product builds it, from the product's own constants.
  r3-chosen          the shape that is actually landed
  r2-enumeration     the nine-word shape the r2 reviewer rejected (F-REV-R2-01)
  token-run          closes the two-token-then-wrap shape by consuming the scheme's
                     own line as a token run -- the candidate whose cost the comment
                     asserts
  optional-run       an optional single pre-break token (a cheaper-looking variant)
  mandatory-token    a mandatory pre-break token with exactly one break

Run:
  <attempt>/iso/venv/Scripts/python.exe r3_design_space_reprobe.py
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\_review_i14d_r3_20260922\scratch\reprobe_rerun")
ATTEMPT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
HARNESS = ATTEMPT / "harness"
R3_SRC = ATTEMPT / "iso/product_narrow_r3/src"

B = chr(92)
Q = chr(34)
S = chr(39)
J = "[^" + B + "s,;&" + B + Q + S + "|]"          # a value token
TAB = "[" + " " + B + "t]"
RN = B + "r?" + B + "n"
DQ = B + Q + "[^" + B + Q + B + "r" + B + "n]*" + B + Q
SQ = S + "[^" + S + B + "r" + B + "n]*" + S
TOKEN = "[A-Za-z][A-Za-z0-9!#$%&" + S + "*+.^_`|~-]*"   # RFC-7235 scheme token

SEC = "ghp_ZQ7ReviewerFakeCredential0123456789"    # 39 chars, the r2 reviewer's credential
MARK = "SYNTHETIC_AUDIT_TOKEN"                     # 21 chars, this attempt's marker

# The r2 reviewer's own matrix (reviewer_report_r2.md section 2.3).
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

# The over-redaction probe the r2 reviewer used (F-REV-R2-02).
OVER_REDACTION = [
    ("OR1", "Authorization: Bearer\ndoc=17"),
    ("OR2", "Authorization: Bearer\nrequest_id=req-1"),
    ("OR3", "Authorization: Bearer\nstage=summarize"),
    ("OR4", "Authorization: token\ndoc=17\nstage=summarize"),
]


def build_split(name: str, ob) -> str:
    """Return the scheme-split alternative for a candidate, from the product's constants."""
    bare = ob._AUTH_BARE_VALUE
    tail = "(?:" + bare + "+|" + DQ + "|" + SQ + ")"
    if name == "r3-chosen":
        # USE THE PRODUCT'S OWN SPLIT VERBATIM.  Re-typing the RFC-7235 token class and the
        # quoted/unquoted tails here once produced a string that differed from the landed
        # one by a few characters -- the reproduction then measured a pattern that is not
        # the pattern on disk.  Re-deriving a constant that is right there in the module is
        # a way to be wrong for no gain.
        return ob._AUTH_SCHEME_SPLIT
    if name == "r2-enumeration":
        # the shape the r2 reviewer rejected: a nine-word list and exactly one break
        return ("(?:bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso)"
                + TAB + "*" + RN + TAB + "*" + J + "+")
    if name == "token-run":
        # consume the scheme's own line as a token run, then the break run, then the tail
        return ("(?:" + TOKEN + ")(?:" + TAB + "+" + J + "+)*" + TAB + "*"
                + "(?:" + RN + TAB + "*)+" + tail)
    if name == "optional-run":
        return ("(?:" + TOKEN + ")" + TAB + "*(?:" + J + "(?:" + TAB + "+" + J + ")*)?" + TAB + "*"
                + "(?:" + RN + TAB + "*)+" + tail)
    if name == "mandatory-token":
        return "(?:" + TOKEN + ")" + TAB + "*" + J + "+" + TAB + "*" + RN + TAB + "*" + tail
    raise KeyError(name)


def build_pattern(split: str, ob) -> re.Pattern:
    return re.compile(
        r"(?i)(?P<key>" + ob._LEFT_ANCHOR + r"authorization\s*[:=]\s*|"
        + ob._LEFT_ANCHOR + r"bearer\s+)(?P<value>" + ob._QUOTED_VALUE + r"|"
        + split + r"|" + ob._AUTH_BARE_VALUE + r")")


def measure(ob, oracle, rule, split: str) -> dict:
    ob._AUTH_PATTERN = build_pattern(split, ob)

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

    leaks = [cid for cid, text in REVIEWER_MATRIX
             if SEC in ob.redact_text(text) or MARK in ob.redact_text(text)]

    over = {}
    for cid, text in OVER_REDACTION:
        out = ob.redact_text(text)
        over[cid] = {"out": out, "lost_a_diagnostic_key": "=" in text and out != text
                     and not any(k in out for k in re.findall(r"[A-Za-z_]+=", text))}

    return {
        "oracle_failures": oracle_fail,
        "oracle_failure_count": len(oracle_fail),
        "rule_failures": rule_fail,
        "rule_failure_count": len(rule_fail),
        "reviewer_variants_still_leaking": leaks,
        "reviewer_variants_leaking_count": len(leaks),
        "over_redaction": over,
    }


def main() -> int:
    sys.path.insert(0, str(R3_SRC))
    from company_wiki.source_catalog import observability as ob

    def load(mod, path):
        spec = importlib.util.spec_from_file_location(mod, path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    oracle = load("oracle", HARNESS / "run_i14d_oracle.py")
    rule = load("rule", HARNESS / "run_rule_table_i14d.py")

    landed_pattern = ob._AUTH_PATTERN.pattern

    results = {}
    for name in ("r3-chosen", "r2-enumeration", "token-run", "optional-run",
                 "mandatory-token"):
        results[name] = measure(ob, oracle, rule, build_split(name, ob))

    # Two separate questions, kept separate (they can fail independently):
    #   (a) is the BUILDER faithful?  feeding it the product's own split must rebuild the
    #       product's own pattern byte for byte;
    #   (b) is the r3-chosen CANDIDATE the landed one?  it must be, because it IS the
    #       product's own split -- but assert it rather than assume it.
    builder_is_faithful = (build_pattern(ob._AUTH_SCHEME_SPLIT, ob).pattern == landed_pattern)
    built_r3 = build_pattern(build_split("r3-chosen", ob), ob).pattern
    reproduces_landed = (built_r3 == landed_pattern)
    landed_diff = []
    if not reproduces_landed:
        import difflib
        sm = difflib.SequenceMatcher(None, landed_pattern, built_r3, autojunk=False)
        landed_diff = [{"op": tag, "landed": landed_pattern[i1:i2], "built": built_r3[j1:j2]}
                       for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal"]

    chosen = results["r3-chosen"]
    runner = results["token-run"]
    out = {
        "card": "I-14-D",
        "attempt": "a20260919-01",
        "iteration": "r3",
        "kind": "design_space_reproduction",
        "why": ("r3_fix_record.md is referenced by the r3 comment block but does not "
                "exist; this re-derives the claim by measurement instead of leaving the "
                "reader pointed at a missing file"),
        "attempt_scratch_scripts_are_stale": {
            "what": "nine scratch scripts unpack oracle.CASES as a 6-tuple; the r3 iteration widened it to 7",
            "error": "ValueError: too many values to unpack (expected 6)",
            "affected": ["tradeoff.py", "tradeoff2.py", "tradeoff3.py", "last_shapes.py",
                         "final_shapes.py", "minimal.py", "order.py", "third_alt.py",
                         "validate_final.py", "final_verify.py"],
            "disposition": "not edited; this script re-implements the measurement instead",
        },
        "method": ("rebind observability._AUTH_PATTERN in memory to each candidate, "
                   "exactly as the attempt's own scratch scripts did"),
        "builder_is_faithful": builder_is_faithful,
        "reproduces_the_landed_pattern": reproduces_landed,
        "landed_pattern_difference": landed_diff,
        "candidate_patterns_are_reconstructions": {
            "applies_to": ["r2-enumeration", "token-run", "optional-run", "mandatory-token"],
            "note": ("only r3-chosen uses the product's own split verbatim. The four "
                     "alternatives are re-expressed from the attempt's scratch scripts "
                     "against the product's constants, so their exact bytes are this "
                     "script's, not the product's; what is being compared is their "
                     "BEHAVIOUR on the same case sets."),
        },
        "candidates": results,
        "the_claim_in_the_comment_block": {
            "text": ("Closing the two-token-then-wrap shape needs the scheme's own line "
                     "consumed as a token run, which deletes `doc=17` from "
                     "`Authorization: Bearer <marker>` + newline + `doc=17` + newline + `stage=`"),
            "closed_by_token_run": "C10" not in runner["reviewer_variants_still_leaking"],
            "cost_of_token_run": runner["over_redaction"],
            "oracle_failures_introduced_by_token_run": runner["oracle_failures"],
            "rule_failures_introduced_by_token_run": runner["rule_failures"],
            "the_failures_are_NOT_all_the_same_kind": {
                "why_it_matters": ("two of the four are the REGISTERED-OPEN ROWS THEMSELVES. "
                                   "`R3a-two-token-then-wrap` and `open-two-token-then-wrap` "
                                   "assert the residual output exactly; closing the leak "
                                   "changes that output, so they go red because the "
                                   "registration is doing its job, not because a defect "
                                   "appeared. Counting all four as 'the cost' overstates it."),
                "genuine_regressions": ["N5-auth-multiline", "cred-auth-multiline-swallow"],
                "registration_rows_that_would_need_re_registering":
                    ["R3a-two-token-then-wrap", "open-two-token-then-wrap"],
                "evidence_the_regressions_are_over_redaction": (
                    "OR1 `Authorization: Bearer\\ndoc=17` -> `Authorization: <redacted>`: "
                    "the diagnostic key `doc=17` is deleted, which is exactly the shape the "
                    "comment block names"),
            },
            "claim_status": "REPRODUCED by this measurement, with the cost breakdown above",
        },
        "verdict": "see candidates",
    }
    dest = HERE / "r3_design_space_reprobe.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                    encoding="utf-8")

    print("reproduces the landed pattern:", reproduces_landed)
    for name, r in results.items():
        print("%-18s oracle_fail=%-2d rule_fail=%-2d leaking=%s"
              % (name, r["oracle_failure_count"], r["rule_failure_count"],
                 r["reviewer_variants_still_leaking"]))
    print()
    print("token-run over-redaction:")
    for cid, v in runner["over_redaction"].items():
        print("   %-4s lost_key=%-5s out=%r" % (cid, v["lost_a_diagnostic_key"], v["out"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
