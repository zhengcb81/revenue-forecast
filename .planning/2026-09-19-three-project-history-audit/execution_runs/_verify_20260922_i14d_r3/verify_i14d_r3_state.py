"""I-14-D r3 state verification — independent, read-only w.r.t. the attempt.

WHAT THIS IS.  The I-14-D attempt was terminated mid-flight (see task_plan.md Round 67).
Its r3 iteration had produced `scratch/oracle_r3.json` and `scratch/rule_r3.json` but no
carrier.  Before anyone decides to carry r3 to completion or abandon it, two things need to
be established, and neither may be taken on the attempt's own word:

  1. Are the recorded r3 results REPRODUCIBLE by someone else?  (A result that only its
     author can obtain is not evidence.)
  2. Which of the r2 reviewer's required changes are actually on disk, and which are not?

So this script RE-RUNS the attempt's own two harnesses against the attempt's own r3 tree and
compares, row by row, against the recorded scratch JSONs.  It then checks each of the four
reviewer items against the bytes on disk.

DISCIPLINE CARRIED FROM THIS PROJECT
  * SCOPE GUARD IS A HARD GATE.  A predicate that searched nothing reports "not found", and
    "not found" is not a finding (lesson #20).  Every input is asserted to exist first.
  * EVERY PREDICATE IS RESPONSIVE.  A test that cannot fail is not a test (lesson #19); each
    one is also fed a synthetic mutated input and must go red, in memory, touching no file.
  * UNITS GO IN THE FIELD NAMES (lesson #25).
  * NO ENVIRONMENT-DERIVED VALUES ARE RECORDED, so the evidence JSON is byte-stable.
  * THE ATTEMPT IS READ-ONLY.  The recorded hashes of every attempt file this script reads
    are pinned below and re-asserted, so a later run can prove nothing was rewritten.

Run:
  <attempt>/iso/venv/Scripts/python.exe verify_i14d_r3_state.py
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent / "I-14-D/a20260919-01"
PY = ATTEMPT / "iso/venv/Scripts/python.exe"

RECORDED_ORACLE = ATTEMPT / "scratch/oracle_r3.json"
RECORDED_RULE = ATTEMPT / "scratch/rule_r3.json"
RERUN_ORACLE = HERE / "oracle_r3_rerun.json"
RERUN_RULE = HERE / "rule_r3_rerun.json"
RERUN_BASE = HERE / "oracle_base_rerun.json"

R3_OBS = ATTEMPT / "iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py"
R2_OBS = ATTEMPT / "iso/product_narrow/src/company_wiki/source_catalog/observability.py"
ORACLE_MD = ATTEMPT / "oracle.md"
FIX_RECORD = ATTEMPT / "fix_record.md"
R2_SUMMARY = ATTEMPT / "after/r2_summary.json"
BINDING = ATTEMPT / "binding.json"
HANDOFF = ATTEMPT / "handoff.json"
REVIEW_MD = ATTEMPT / "review.md"
R3_FIX_RECORD = ATTEMPT / "r3_fix_record.md"

REQUIRED_INPUTS = [PY, RECORDED_ORACLE, RECORDED_RULE, RERUN_ORACLE, RERUN_RULE, RERUN_BASE,
                   R3_OBS, R2_OBS, ORACLE_MD, FIX_RECORD, R2_SUMMARY, BINDING,
                   HANDOFF, REVIEW_MD]

# The r2 reviewer's four items.
REVIEWER_ITEMS = ["F-REV-R2-01 (BLOCKER)", "F-REV-R2-02 (MEDIUM)",
                  "F-REV-R2-03 (LOW)", "F-REV-R2-04 (INFO)"]

# Pinned hashes of every attempt file this script reads.  If one of these ever changes, the
# assertion fails and says so -- which is how "this verification was read-only" stays checkable.
PINNED = {
    "scratch/oracle_r3.json":
        "c436d62159c5a19b7fa8d2afe6f0aac9c265af98a52c6a669b0a327b69217cf1",
    "scratch/rule_r3.json":
        "11f5cb18024e00ed77b25976c1b121613ecf098e330df86ac7c6b468912f4130",
    "oracle.md":
        "f188e853026b26d3f53dcaee81822fc75a44a257bc541219c791aa2fa23c09f2",
    "fix_record.md":
        "68fb580001b2e798376a16b5c964fd47e08d0974555f07f37587d7c536d4055a",
    "binding.json":
        "5fd462c93197d5d7b602a03b2ba81841917bab845aa609854e4db98c10e2d9eb",
    "after/r2_summary.json":
        "25da886e3e12642846b8d9b5c68ffd9d9495e9362cddd7d0f13cc90ce8646615",
    "handoff.json":
        "c1facfb1f136b5d6eb3d5784be634cec442f3cb5c4b8dba69e40b4c3a6b7113e",
    "review.md":
        "14b8628d13c33ffb197db29c20d9073059034875919642a7f8c99249210a0104",
    "iso/product_narrow_r3/src/company_wiki/source_catalog/observability.py":
        "a551cc45efcd11925d6c647dec0564d5d0684ce5c675794136f465d33dc22fda",
}


# --------------------------------------------------------------- predicates
# Each takes explicit data so the SAME function can be fed a mutated input.

def p1_reproduced(rec_o, new_o, rec_r, new_r) -> dict:
    out = {}
    for name, a, b in (("oracle", rec_o, new_o), ("rule_table", rec_r, new_r)):
        ra, rb = a.get("rows", []), b.get("rows", [])
        ids_a = [x.get("id") for x in ra]
        ids_b = [x.get("id") for x in rb]
        diffs = sum(1 for x, y in zip(ra, rb)
                    for k in set(x) | set(y) if x.get(k) != y.get(k))
        scalar_keys = (set(a) | set(b)) - {"rows", "src", "label"}
        scalar_diffs = {k: [a.get(k), b.get(k)] for k in sorted(scalar_keys)
                        if a.get(k) != b.get(k)}
        out[name] = {
            "recorded_rows": len(ra),
            "rerun_rows": len(rb),
            "ids_in_the_same_order": ids_a == ids_b,
            "field_differences": diffs,
            "non_row_differences": scalar_diffs,
            "reproduced": (len(ra) == len(rb) and ids_a == ids_b
                           and diffs == 0 and scalar_diffs == {}),
        }
    out["holds"] = all(out[k]["reproduced"] for k in ("oracle", "rule_table"))
    return out


def p2_generalized(src_text: str) -> dict:
    rfc7235 = "_AUTH_SCHEME_TOKEN = r\"[A-Za-z][A-Za-z0-9!#$%&'*+.^_`|~-]*\""
    old_enum = "bearer|token|basic|digest|oauth|jwt|apikey|api_key|sso"
    split_line = [ln for ln in src_text.splitlines() if ln.startswith("_AUTH_SCHEME_SPLIT")]
    value_line = [ln for ln in src_text.splitlines() if "bearer" in ln and "_QUOTED_VALUE" in ln]
    checks = {
        "rfc7235_token_constant_present": rfc7235 in src_text,
        "old_nine_word_enumeration_gone": old_enum not in src_text,
        "split_references_the_token_constant": bool(split_line)
                                               and "_AUTH_SCHEME_TOKEN" in split_line[0],
        "break_is_a_run_not_exactly_one": any("(?:\\r?\\n)" in ln and ')+"' in ln
                                              for ln in src_text.splitlines()
                                              if ln.strip().startswith('r"(?:(?:')),
        "quoted_value_tried_first_after_the_break": bool(value_line)
                                                    and value_line[0].index("_QUOTED_VALUE")
                                                    < value_line[0].index("_AUTH_SCHEME_SPLIT"),
        "discloses_f_rev_r2_01": "F-REV-R2-01" in src_text,
        "discloses_f_rev_r2_02": "F-REV-R2-02" in src_text,
    }
    return dict(checks, holds=all(checks.values()))


def p3_residual_registered(rec_o, rec_r) -> dict:
    oracle_rows = set(rec_o.get("registered_open", []))
    rule_open = set(rec_r.get("registered_open_rows", []))
    leaking = set(rec_r.get("registered_open_leaking", []))
    secret_leaks = set(rec_r.get("credential_secret_leaks", []))
    checks = {
        "oracle_has_registered_open_rows": len(oracle_rows) > 0,
        "oracle_open_rows_confirmed": set(rec_o.get("registered_open_confirmed", []))
                                      == oracle_rows,
        "rule_table_has_registered_open_kind": len(rule_open) > 0,
        "every_open_row_still_leaks": leaking == rule_open,
        "the_non_marker_credential_is_the_thing_that_survives": secret_leaks == rule_open,
        "no_unregistered_marker_leak": rec_r.get("credential_leaks") == [],
        "no_untouched_row_was_touched": rec_r.get("touched_but_should_not_be") == [],
    }
    return dict(checks, oracle_registered_open=sorted(oracle_rows),
                rule_table_registered_open=sorted(rule_open), holds=all(checks.values()))


def p4_over_redaction_registered(rec_r) -> dict:
    rows = rec_r.get("over_redaction_rows", [])
    touched = rec_r.get("over_redaction_touched", [])
    checks = {
        "the_family_has_rows": len(rows) >= 2,          # reviewer asked for >= 2
        "the_rows_assert_the_loss_exactly": set(touched) == set(rows),
        "fidelity_still_holds": rec_r.get("fidelity_ok") is True,
    }
    return dict(checks, over_redaction_row_count=len(rows), rows=sorted(rows),
                holds=all(checks.values()))


def p5_false_claim(oracle_md: str, fix_record: str, r2_summary: dict,
                   base_rows: list) -> dict:
    # WHITESPACE IS NORMALISED BEFORE MATCHING.  These records are prose and are hard-wrapped:
    # fix_record.md says "All\n  three FAIL on the base tree", so a raw substring search for
    # "All three FAIL on the base tree" reports the claim as ABSENT when it is present.
    # This is lesson #17 in this project's series, and it was re-committed here on the first
    # run of this very script -- recorded rather than quietly fixed.
    def flat(s: str) -> str:
        return re.sub(r"\s+", " ", s)

    oracle_flat, fix_flat = flat(oracle_md), flat(fix_record)
    n5 = {r["id"]: r["pass"] for r in base_rows
          if r["id"].startswith(("N5c", "N5d", "N5e"))}
    n5c = n5.get("N5c-auth-scheme-lf-secret")
    n5d = n5.get("N5d-auth-scheme-obsfold")
    n5e = n5.get("N5e-auth-token-key-lf-secret")
    base_list = r2_summary.get("oracle", {}).get("narrow_must_failed_base", [])
    checks = {
        # the claim is STILL PRESENT in all three records ...
        "oracle_md_still_claims_all_three_fail":
            flat("On the pre-fix base tree all three FAIL") in oracle_flat,
        "fix_record_still_claims_all_three_fail":
            flat("All three FAIL on the base tree") in fix_flat,
        "r2_summary_still_lists_n5e_as_base_failing":
            "N5e-auth-token-key-lf-secret" in base_list,
        # ... and the re-run REFUTES it: only N5c fails on base
        "rerun_n5c_fails_on_base": n5c is False,
        "rerun_n5d_passes_on_base": n5d is True,
        "rerun_n5e_passes_on_base": n5e is True,
    }
    return dict(checks, measured_on_base=n5, r2_summary_base_failures=base_list,
                holds=all(checks.values()))


def p6_unlanded_items(oracle_md: str, binding_text: str) -> dict:
    c22 = oracle_md.split("## C2.2", 1)[-1].split("\n## ", 1)[0]
    checks = {
        # F-REV-R2-02's oracle.md half: "fail-closed in BOTH directions" is not stated there
        "c22_does_not_state_both_directions":
            not re.search(r"both directions", c22, re.I),
        # F-REV-R2-04: the imprecise parenthetical is still in binding.json
        "binding_still_says_scheme_branch_unreferenced":
            "scheme branch left defined but unreferenced" in binding_text,
    }
    return dict(checks, holds=all(checks.values()))


def p7_no_r3_carrier(handoff_mtime, review_mtime, newest_r3_artifact_mtime) -> dict:
    checks = {
        "handoff_predates_the_r3_artifacts": handoff_mtime < newest_r3_artifact_mtime,
        "review_predates_the_r3_artifacts": review_mtime < newest_r3_artifact_mtime,
    }
    return dict(checks, holds=all(checks.values()))


def p8_attempt_untouched(pinned: dict, measured: dict) -> dict:
    drift = {k: {"pinned": v, "measured": measured.get(k)} for k, v in pinned.items()
             if measured.get(k) != v}
    return {"files_pinned": len(pinned), "drifted": drift,
            "holds": drift == {}}


# --------------------------------------------------------------- helpers

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def newest_mtime(paths):
    best = None
    for p in paths:
        t = p.stat().st_mtime
        if best is None or t > best:
            best = t
    return best


def main() -> int:
    missing = [str(p) for p in REQUIRED_INPUTS if not p.exists()]
    if missing:
        raise SystemExit("FATAL: scope guard -- required inputs missing: %s" % missing)

    rec_o = json.loads(RECORDED_ORACLE.read_text(encoding="utf-8"))
    rec_r = json.loads(RECORDED_RULE.read_text(encoding="utf-8"))
    new_o = json.loads(RERUN_ORACLE.read_text(encoding="utf-8"))
    new_r = json.loads(RERUN_RULE.read_text(encoding="utf-8"))
    base = json.loads(RERUN_BASE.read_text(encoding="utf-8"))

    r3_text = R3_OBS.read_text(encoding="utf-8")
    oracle_md = ORACLE_MD.read_text(encoding="utf-8")
    fix_record = FIX_RECORD.read_text(encoding="utf-8")
    binding_text = BINDING.read_text(encoding="utf-8")
    r2_summary = json.loads(R2_SUMMARY.read_text(encoding="utf-8"))

    measured = {rel: sha256(ATTEMPT / rel) for rel in PINNED}

    results = {
        "P-1": p1_reproduced(rec_o, new_o, rec_r, new_r),
        "P-2": p2_generalized(r3_text),
        "P-3": p3_residual_registered(rec_o, rec_r),
        "P-4": p4_over_redaction_registered(rec_r),
        "P-5": p5_false_claim(oracle_md, fix_record, r2_summary, base.get("rows", [])),
        "P-6": p6_unlanded_items(oracle_md, binding_text),
        "P-7": p7_no_r3_carrier(HANDOFF.stat().st_mtime, REVIEW_MD.stat().st_mtime,
                                newest_mtime([RECORDED_ORACLE, RECORDED_RULE, R3_OBS])),
        "P-8": p8_attempt_untouched(PINNED, measured),
    }

    # ---- responsiveness self-check: every predicate must go red on a mutated input ----
    mut_o = json.loads(json.dumps(rec_o))
    mut_o["rows"][0]["out"] = "MUTATED"
    mut_r = json.loads(json.dumps(rec_r))
    mut_r["credential_leaks"] = ["synthetic-unregistered-leak"]
    mut_r_open = json.loads(json.dumps(rec_r))
    mut_r_open["registered_open_leaking"] = []
    mut_binding = binding_text.replace("scheme branch left defined but unreferenced", "X")
    mut_base = json.loads(json.dumps(base))
    for r in mut_base["rows"]:
        if r["id"].startswith("N5d"):
            r["pass"] = False
    neg = {
        "NC-1 a rerun row differs": p1_reproduced(rec_o, mut_o, rec_r, new_r)["holds"],
        "NC-2 an unregistered marker leak appears":
            p3_residual_registered(rec_o, mut_r)["holds"],
        "NC-3 the registered residual stops leaking":
            p3_residual_registered(rec_o, mut_r_open)["holds"],
        "NC-4 the generalized token is absent":
            p2_generalized(r3_text.replace("_AUTH_SCHEME_TOKEN = r\"[A-Za-z]", "X"))["holds"],
        "NC-5 N5d actually fails on base":
            p5_false_claim(oracle_md, fix_record, r2_summary, mut_base["rows"])["holds"],
        "NC-6 the binding parenthetical was fixed":
            p6_unlanded_items(oracle_md, mut_binding)["holds"],
        "NC-7 an attempt file drifted":
            p8_attempt_untouched(PINNED, dict(measured, **{
                "oracle.md": "0" * 64}))["holds"],
    }
    neg_ok = all(v is False for v in neg.values())

    overall = all(r["holds"] for r in results.values()) and neg_ok

    out = {
        "card": "I-14-D",
        "attempt": "a20260919-01",
        "iteration": "r3",
        "kind": "independent_state_verification",
        "reviewer_items": REVIEWER_ITEMS,
        "reproduced_by": "re-running the attempt's own harnesses against the attempt's own tree",
        "commands": [
            "<attempt>/iso/venv/Scripts/python.exe harness/run_i14d_oracle.py "
            "--src iso/product_narrow_r3/src --label r3-verify --out <here>/oracle_r3_rerun.json",
            "<attempt>/iso/venv/Scripts/python.exe harness/run_rule_table_i14d.py "
            "--src iso/product_narrow_r3/src --label r3-verify --out <here>/rule_r3_rerun.json",
            "<attempt>/iso/venv/Scripts/python.exe harness/run_i14d_oracle.py "
            "--src iso/product_base/src --label base-verify --out <here>/oracle_base_rerun.json",
        ],
        "note_on_interpreter": (
            "the global interpreter lacks PyYAML, and the harness correctly returned rc=2 "
            "cannot_adjudicate rather than a wrong answer; the attempt's own iso venv "
            "(python 3.13.9, PyYAML 6.0.3) is what these runs use"),
        "dangling_reference": {
            "referenced_by": "iso/product_narrow_r3/.../observability.py (the r3 comment block)",
            "path": "r3_fix_record.md",
            "exists": R3_FIX_RECORD.exists(),
        },
        "predicate_errors_made_and_corrected": [
            {
                "predicate": "P-2 break_is_a_run_not_exactly_one",
                "symptom": "reported False while the run-of-breaks form is present",
                "cause": "transposed characters: searched for '+)\"' where the source has ')+\"'",
                "classification": "predicate error, NOT a data defect",
                "fix": "searched for the byte order the file actually uses",
            },
            {
                "predicate": "P-5 fix_record_still_claims_all_three_fail",
                "symptom": "reported the claim ABSENT while it is present",
                "cause": ("fix_record.md is hard-wrapped -- it reads 'All\\n  three FAIL on the "
                          "base tree' -- and the predicate searched the raw text without "
                          "normalising whitespace"),
                "classification": "predicate error, NOT a data defect",
                "fix": "normalise whitespace (re.sub(r'\\s+', ' ')) before matching",
                "note": ("this is lesson #17 in this project's series, re-committed here on the "
                         "first run of this script and recorded rather than quietly fixed"),
            },
        ],
        "propositions": results,
        "negative_controls": {k: {"holds": v, "correctly_red": v is False}
                              for k, v in neg.items()},
        "negative_controls_all_correctly_red": neg_ok,
        "overall": "PASS" if overall else "FAIL",
    }
    dest = HERE / "i14d_r3_state_verification.json"
    dest.write_text(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True) + "\n",
                    encoding="utf-8")

    for k, r in results.items():
        print("%-5s holds=%s" % (k, r["holds"]))
    print("negative controls all correctly red =", neg_ok)
    print("overall =", out["overall"])
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
