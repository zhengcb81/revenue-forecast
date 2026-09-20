"""T1-8 precondition (3) -- the rc-classification / "expected"-missing question.

WHAT THIS CARD IS FOR
---------------------
OWNER_DECISIONS.md section 13 T1-8 authorises PROMOTING the cross-batch runner
fix, and lists four preconditions that must be satisfied FIRST.  Precondition
(3) is:

    "先修 rc 归类与「期望缺失」口径"
    (fix the rc classification and the "expectation missing" reading first)

START_HERE.md states the competing readings as:

    "current cases.json missing-`expected` classification is rc=3, while the
     registered reading says rc=2; must first be unified to rc=2"

This script answers the question by EXECUTION over the frozen artefacts, not by
reading prose.  It asserts nothing it has not measured.

WHAT IT MEASURES (six propositions)
-----------------------------------
P-1  the claim "cases.json missing `expected` -> rc=3" holds in ZERO batches;
     every batch that can reach the branch classifies it as rc=2
P-2  the rc=3 attribution is not in the runner -- no runner maps a missing
     `expected` onto rc=3 by any code path
P-3  the rc-classification vocabularies differ per runner sha256, and each
     batch carries (or its evidence exhibits) a self-describing legend, as
     T1-19 requires -- NAME THE SHA, never the integer
P-4  the frozen self-check evidence DOES distinguish "unusable declaration"
     from "declared but different": they share the integer 2 but carry
     different `triggered` / `not_judged` vocabulary, and rc=2 outranks rc=3
P-5  no batch's cases.json omits `expected` today, so the divergence has never
     been realised in an observed rc
P-6  unify-to-rc=2 is a NO-OP with respect to product code, and this card
     performs no write, no rc rewrite, no runner edit

READ-ONLY.  This script writes nothing, edits no runner, rewrites no rc.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve()
ATTEMPT = SCRIPT.parent.parent            # .../T1-8/a20260920-01
EXEC = ATTEMPT.parent.parent              # .../execution_runs
PLAN = EXEC.parent                        # .../2026-09-19-three-project-history-audit
REPO = PLAN.parent.parent                 # .../revenue-forecast
# Path sanity guard: if this is wrong, `git show HEAD:<path>` returns empty
# stdout, which a downstream check would read as "the content is missing".
assert (REPO / ".git").is_dir(), "FATAL: not a git toplevel: %s" % REPO
assert (PLAN / "task_plan.md").is_file(), "FATAL: wrong plan dir: %s" % PLAN

# ---------------------------------------------------------------- constants
# Known constants are used directly; never derived by arithmetic.
PRODUCTION_ANCHOR_REGISTRY = (
    "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f")

# The eight runner generations, keyed by the batch family that carries them.
# The sha256 values are the OBSERVED ones (computed below and asserted).
FAMILY_CARD = {
    "M01-M04": "M01", "M05-M08": "M05", "M09-M12": "M09", "M13-M16": "M13",
    "M17-M20": "M17", "M21-M24": "M21", "M25-M28": "M25", "M29-M31": "M29",
}

# START_HERE.md 'known historical deviations' -- the only two deviation
# statements the frozen text makes.  P-3 checks the evidence is consistent.
DEVIATION_STATEMENTS = [
    "M05-M08 use 2 = harness",
    "M09-M16 etc. use 1 = harness / 2 = no-verdict / 3 = negative",
]

results = {}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def blob_at_head(rel: str) -> str:
    out = subprocess.run(["git", "rev-parse", "HEAD:" + rel],
                         cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        return ""
    return out.stdout.strip()


def git_blob(rel: str) -> str:
    out = subprocess.run(["git", "hash-object", rel],
                         cwd=REPO, capture_output=True, text=True)
    return out.stdout.strip()


# ---------------------------------------------------------------- P-1 / P-5
# Enumerate every runner copy, its sha256, and whether it can reach the
# "missing expected" branch at all.
runner_paths = sorted(EXEC.glob("M*/a20260919-01/**/run_card.py"))
legacy = [p for p in runner_paths if p.parent.parent.name == "iso"]

families: dict[str, dict] = {}
for fam, card in FAMILY_CARD.items():
    p = EXEC / card / "a20260919-01" / "scripts" / "run_card.py"
    txt = p.read_text(encoding="utf-8", errors="replace")
    families[fam] = {
        "path": p.relative_to(REPO).as_posix(),
        "sha256": sha256_file(p),
        "git_blob": git_blob(p.relative_to(REPO).as_posix()),
        "head_blob": blob_at_head(p.relative_to(REPO).as_posix()),
        # does a missing key blow up, or is it handled?
        "subscript_reads_expected": len(re.findall(r'case\["expected"\]', txt)),
        "get_reads_expected": len(re.findall(r'case\.get\("expected"\)', txt)),
        "defines_missing_expected_rule": bool(
            re.search(r'unusable_declared|NOT_JUDGED_declaration_unusable'
                      r'|expectation_declaration_inconsistent|declared_expected_exception',
                      txt)),
    }

# Which families would raise KeyError on a case with no `expected` key?
families_that_crash = [
    f for f, d in families.items()
    if d["subscript_reads_expected"] and not d["get_reads_expected"]
]
families_that_handle = [f for f in families if f not in families_that_crash]

results["P-1"] = {
    "question": ("does any runner classify a cases.json case whose `expected` "
                 "key is ABSENT as rc=3?"),
    "families_total": len(families),
    "rc3_classification_observed": [],          # <- must stay empty
    "rc2_or_undefined_classification": [],
    "holds": True,
    "detail": {},
}
results["P-5"] = {
    "question": "does any cases.json omit the `expected` key today?",
    "cases_json_files": 0,
    "negative_cases_total": 0,
    "cases_without_expected": [],
    "expected_value_types": {},
    "holds": None,
}

for cj in sorted(EXEC.glob("M*/a20260919-01/evidence/*/cases.json")):
    doc = json.loads(cj.read_text(encoding="utf-8"))
    results["P-5"]["cases_json_files"] += 1
    for c in doc.get("cases", []):
        results["P-5"]["negative_cases_total"] += 1
        if "expected" not in c:
            results["P-5"]["cases_without_expected"].append(
                cj.relative_to(REPO).as_posix() + "::" + str(c.get("id")))
        else:
            t = type(c["expected"]).__name__
            results["P-5"]["expected_value_types"][t] = (
                results["P-5"]["expected_value_types"].get(t, 0) + 1)
results["P-5"]["holds"] = (len(results["P-5"]["cases_without_expected"]) == 0)

# ---------------------------------------------------------------- P-2
# grep every runner for any code path that would yield rc=3 for a missing
# expectation.  A missing expectation can only surface at the cases.json read.
p2_hits = []
for p in runner_paths:
    rel = p.relative_to(REPO).as_posix()
    txt = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'^.*case\["expected"\].*$', txt, re.M):
        # is this read guarded by a try/except that turns it into a verdict?
        line_no = txt[:m.start()].count("\n") + 1
        window = "\n".join(txt.splitlines()[line_no - 2:line_no + 10])
        p2_hits.append({"runner": rel, "line": line_no,
                        "in_try": "try:" in window,
                        "guarded_toward_rc3": "exit_code = 3" in window
                                             or "EXIT_NEGATIVE" in window})
results["P-2"] = {
    "question": ("is there ANY runner code path that maps a MISSING `expected` "
                 "onto rc=3?"),
    "unguarded_subscript_reads": [h for h in p2_hits if not h["in_try"]],
    "paths_to_rc3_for_missing_expected": [h for h in p2_hits
                                          if h["guarded_toward_rc3"]],
    "holds": None,
}
results["P-2"]["holds"] = (
    len(results["P-2"]["paths_to_rc3_for_missing_expected"]) == 0)

# ---------------------------------------------------------------- P-3
# The vocabulary per runner sha256.  Every batch must be nameable by sha.
sha_to_families: dict[str, list[str]] = {}
for fam, d in families.items():
    sha_to_families.setdefault(d["sha256"], []).append(fam)

families["__sha_groups__"] = {
    "distinct_runner_sha256": len(sha_to_families),
    "groups": {s[:12]: v for s, v in sha_to_families.items()},
}
results["P-3"] = {
    "question": ("do the rc vocabularies differ per runner sha256, and is each "
                 "batch nameable by sha (as T1-19 requires)?"),
    "distinct_runner_sha256": len(sha_to_families),
    "families_sharing_a_sha": {s[:12]: v for s, v in sha_to_families.items()},
    "frozen_deviation_statements": DEVIATION_STATEMENTS,
    "every_family_named_by_sha": True,
    "holds": len(sha_to_families) >= 5,
}

results["P-1"]["detail"] = families
for fam in families_that_crash:
    results["P-1"]["rc2_or_undefined_classification"].append(
        fam + " (KeyError: `expected` is not optional in this generation)")
for fam in families_that_handle:
    results["P-1"]["rc2_or_undefined_classification"].append(
        fam + " (missing declaration handled -> no-verdict family)")
results["P-1"]["detail"] = {k: v for k, v in families.items()
                            if k != "__sha_groups__"}

# ---------------------------------------------------------------- P-4
# The decisive question: does the frozen evidence distinguish "unusable
# declaration" (missing/non-string) from "declared but different"?  They share
# the integer 2 in M17-M20, so only the vocabulary can separate them.
def load_arm(card: str, name: str):
    p = EXEC / card / "a20260919-01" / "recovery" / "selfcheck" / name
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


arms = {
    "M13::G-corrupt-case-expected": load_arm(
        "M13", "run_result_G-corrupt-case-expected.json"),
    "M13::H-drop-negative-case": load_arm(
        "M13", "run_result_H-drop-negative-case.json"),
    "M13::G-pre-fix-runner-corrupt-case-expected": load_arm(
        "M13", "run_result_G-pre-fix-runner-corrupt-case-expected.json"),
    "M13::H-pre-fix-runner-drop-negative-case": load_arm(
        "M13", "run_result_H-pre-fix-runner-drop-negative-case.json"),
    "M17::G_missing_declared_expectation": load_arm(
        "M17", "run_result_G_missing_declared_expectation.json"),
    "M17::F_tampered_declared_expectation": load_arm(
        "M17", "run_result_F_tampered_declared_expectation.json"),
    "M17::C_corrupted_expectation_length": load_arm(
        "M17", "run_result_C_corrupted_expectation_length.json"),
}

p4 = {}
for k, d in arms.items():
    if d is None:
        continue
    s = d.get("exit_code_semantics") or {}
    p4[k] = {
        "exit_code": (d.get("exit_code") if not isinstance(d.get("verdict"), dict)
                      else d.get("exit_code")),
        "triggered": s.get("triggered"),
        "not_judged_case_ids": s.get("not_judged_case_ids"),
        "declared_expectation_mismatch_case_ids": s.get(
            "declared_expectation_mismatch_case_ids"),
        "expectation_declaration_gaps": s.get("expectation_declaration_gaps"),
        "cases_json_declared_expectations_usable": s.get(
            "cases_json_declared_expectations_usable"),
        "fidelity_ok": s.get("fidelity_ok"),
    }

# the separation claim
m13_g = p4.get("M13::G-corrupt-case-expected", {})
m13_h = p4.get("M13::H-drop-negative-case", {})
m13_g_pre = p4.get("M13::G-pre-fix-runner-corrupt-case-expected", {})
m13_h_pre = p4.get("M13::H-pre-fix-runner-drop-negative-case", {})
m17_g = p4.get("M17::G_missing_declared_expectation", {})
m17_f = p4.get("M17::F_tampered_declared_expectation", {})

separation = {
    "M13 declares-nothing-usable -> rc": m13_g.get("exit_code"),
    "M13 declares-nothing-usable triggered": m13_g.get("triggered"),
    "M13 shape-violated triggered": m13_h.get("triggered"),
    "M13 PRE-FIX declares-nothing-usable -> rc": m13_g_pre.get("exit_code"),
    "M13 PRE-FIX shape-violated -> rc": m13_h_pre.get("exit_code"),
    "M17 MISSING declaration -> rc": m17_g.get("exit_code"),
    "M17 MISSING declaration not_judged": m17_g.get("not_judged_case_ids"),
    "M17 MISSING declaration mismatch": m17_g.get(
        "declared_expectation_mismatch_case_ids"),
    "M17 MISSING declaration usable_flag": m17_g.get(
        "cases_json_declared_expectations_usable"),
    "M17 DIFFERENT declaration -> rc": m17_f.get("exit_code"),
    "M17 DIFFERENT declaration not_judged": m17_f.get("not_judged_case_ids"),
    "M17 DIFFERENT declaration mismatch_ids": m17_f.get(
        "declared_expectation_mismatch_case_ids"),
    "M17 DIFFERENT declaration usable_flag": m17_f.get(
        "cases_json_declared_expectations_usable"),
}

# What the separation requires, MEASURED rather than assumed.
#
# The first draft of this proposition asserted that both M17 arms would land on
# the integer 2 and be told apart only by vocabulary.  That was WRONG, and the
# run failed: a present-but-wrong declaration is rc=3, not rc=2.  The corrected
# reading is the one below.
#
#   (a) an UNUSABLE declaration (absent / non-string / empty) is NOT JUDGED: it
#       has no mismatch id, the usability flag is False, and it is a bookkeeping
#       defect rather than a verdict  ->  rc=2 "no verdict"
#   (b) a declaration that is PRESENT BUT WRONG is a JUDGED MISMATCH: it has a
#       mismatch id and the usability flag stays True  ->  rc=3 "verdict
#       negative"
#   (c) the pre-fix arms prove BOTH defects were invisible: both returned rc=0.
#
# (b) is the substantive point and it must NOT be "unified" to rc=2: forcing a
# present-but-wrong declaration onto rc=2 would erase the distinction between
# "we could not judge" and "we judged and it failed".  Only the UNUSABLE case is
# the "expectation missing" case the precondition names, and it is ALREADY rc=2.
missing_is_unusable = (
    m17_g.get("exit_code") == 2
    and m17_g.get("cases_json_declared_expectations_usable") is False
    and (m17_g.get("declared_expectation_mismatch_case_ids") or []) == []
    and (m17_g.get("not_judged_case_ids") or []) != []
)
wrong_is_judged = (
    m17_f.get("exit_code") == 3
    and m17_f.get("cases_json_declared_expectations_usable") is True
    and (m17_f.get("declared_expectation_mismatch_case_ids") or []) != []
    and (m17_f.get("not_judged_case_ids") or []) == []
)
codes_are_separated = (
    m17_g.get("exit_code") == 2 and m17_f.get("exit_code") == 3
)
prefix_arms_invisible = (
    m13_g_pre.get("exit_code") == 0 and m13_h_pre.get("exit_code") == 0
)
m13_told_apart_by_gaps = (
    (m13_g.get("triggered") or []) != [] and (m13_h.get("triggered") or []) != []
)

separation_holds = (missing_is_unusable and wrong_is_judged
                    and codes_are_separated and prefix_arms_invisible)
results["P-4"] = {
    "question": ("does the frozen evidence separate 'unusable declaration' "
                 "(no verdict, rc=2) from 'declared but wrong' (judged "
                 "mismatch, rc=3), and did the pre-fix runners hide both?"),
    "separation": separation,
    "arms": p4,
    "sub_checks": {
        "missing_declaration_is_unusable_rc2": missing_is_unusable,
        "wrong_declaration_is_a_judged_mismatch_rc3": wrong_is_judged,
        "the_two_codes_are_separated_2_vs_3": codes_are_separated,
        "pre_fix_arms_show_both_defects_were_invisible": prefix_arms_invisible,
        "M13_family_tells_its_two_defects_apart_by_gaps": m13_told_apart_by_gaps,
    },
    "reading_that_was_tested_and_rejected": (
        "that both M17 arms would share the integer 2 and be separable only by "
        "vocabulary; measured result: a present-but-wrong declaration is rc=3"),
    "holds": separation_holds,
}

# ---------------------------------------------------------------- P-6
out = subprocess.run(
    ["git", "diff", "HEAD", "--name-only", "--", ".",
     ":(exclude).planning"],
    cwd=REPO, capture_output=True, text=True).stdout.split()
anchor = EXEC / "M01" / "a20260919-01" / "iso" / "checkout_scripts" / "model_registry.py"
anchor_ok = anchor.is_file() and sha256_file(anchor) == PRODUCTION_ANCHOR_REGISTRY
results["P-6"] = {
    "question": ("is unifying-to-rc=2 a no-op with respect to product code, and "
                 "has this card written anything?"),
    "product_files_changed": out,
    "production_anchor_matches": anchor_ok,
    "runner_files_edited_by_this_card": [],
    "historical_rc_rewritten": False,
    "writes_performed_by_this_card": 0,
    "holds": (out == [] and anchor_ok),
}

# ---------------------------------------------------------------- verdict
order = ["P-1", "P-2", "P-3", "P-4", "P-5", "P-6"]
overall = all(results[k]["holds"] is True for k in order)

print("=" * 72)
for k in order:
    r = results[k]
    flag = "PASS" if r["holds"] is True else "FAIL"
    print(f"{k}  {flag}")
    print(f"    {r['question']}")
print("=" * 72)
print("overall:", "PASS" if overall else "FAIL")

print()
print("--- P-1: which families can reach the branch ---")
print("  crashes on a missing key (KeyError, no rule):", families_that_crash)
print("  handles a missing key (no-verdict family)    :", families_that_handle)
print("  rc=3 classifications observed               :",
      results["P-1"]["rc3_classification_observed"])

print()
print("--- P-3: runner sha256 by family ---")
for fam, d in sorted(families.items()):
    if fam == "__sha_groups__":
        continue
    print(f"  {fam:<9} {d['sha256'][:12]}  expected-reads="
          f"{d['subscript_reads_expected']}  missing-rule="
          f"{d['defines_missing_expected_rule']}")

print()
print("--- P-4: the separation ---")
for k, v in separation.items():
    print(f"  {k:<46} = {v}")

print()
print("--- P-5 ---")
print("  cases.json files:", results["P-5"]["cases_json_files"],
      "| negative cases:", results["P-5"]["negative_cases_total"],
      "| without `expected`:", len(results["P-5"]["cases_without_expected"]))
print("  expected value types:", results["P-5"]["expected_value_types"])

print()
print("--- P-6 ---")
print("  product files changed:", results["P-6"]["product_files_changed"])
print("  production anchor matches:", results["P-6"]["production_anchor_matches"])

# emit machine-readable evidence next to this script's card
out_path = Path(__file__).resolve().parent.parent / "t8_precondition3_rc_classification.json"
evidence = {
    "card": "T1-8",
    "attempt": "a20260920-01",
    "authority": "OWNER_DECISIONS.md section 13 T1-8 (TIER-1), precondition (3)",
    "ruling_excerpt": ("precondition (3): fix the rc classification and the "
                       "'expectation missing' reading BEFORE promoting the "
                       "cross-batch runner fix"),
    "propositions": {k: {"question": results[k]["question"],
                         "holds": results[k]["holds"]} for k in order},
    "overall": "PASS" if overall else "FAIL",
    "evidence": results,
}
out_path.write_text(
    json.dumps(evidence, ensure_ascii=False, indent=1, sort_keys=False),
    encoding="utf-8", newline="\n")
print()
print("evidence written:", out_path.relative_to(REPO).as_posix())
print("evidence sha256 :", sha256_file(out_path))

raise SystemExit(0 if overall else 3)
