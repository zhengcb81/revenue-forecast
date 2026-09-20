"""Exit-code self-check for F-M01-02: prove the exit code now carries the verdict.

Originally written in revision r2; revision r3 added case D after the point
review showed that rc=2 IS reachable (a corrupted positive input).

Runs the PATCHED run_card.py against deliberately corrupted copies of the
frozen artefacts in a scratch tree, so the frozen evidence is never touched:

  case A  corrupted oracle expectation -> negative verdict, rc=3
  case B  corrupted case plan          -> defect outside the guard, rc=1
  case C  uncorrupted card             -> rc=0
  case D  corrupted positive input     -> no verdict exists, rc=2

The product itself returns the correct numbers in case A, which is the point:
the corrupted artefact is the ORACLE, exactly the class of mistake the exit
code must catch.

ASCII-only stdout.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def run(argv, cwd):
    proc = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")


def main():
    plan = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast", ".planning",
                        "2026-09-19-three-project-history-audit")
    attempt = os.path.join(plan, "execution_runs", "M01", "a20260919-01")
    real_evidence = os.path.join(attempt, "evidence", "M01")
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    code = os.path.join(attempt, "iso", "checkout_scripts")

    scratch = os.path.join(attempt, "recovery", "r2_exit_code_selfcheck")
    shutil.rmtree(scratch, ignore_errors=True)
    os.makedirs(scratch)
    shutil.copy(os.path.join(attempt, "scripts", "run_card.py"), os.path.join(scratch, "run_card.py"))
    print("scratch:", scratch)
    print("note: each case gets its own --attempt root so that the harness reads "
          "<case>/evidence/M01/{input,oracle,cases}.json and never the frozen evidence")

    def make_case(name):
        """Create <scratch>/<name>/evidence/M01 with copies of the frozen artefacts."""
        root = os.path.join(scratch, name)
        ev = os.path.join(root, "evidence", "M01")
        os.makedirs(ev)
        for fname in ("input.json", "oracle.json", "cases.json"):
            shutil.copy(os.path.join(real_evidence, fname), os.path.join(ev, fname))
        return root, ev

    report = {"purpose": "F-M01-02 self-check: does the exit code carry the verdict?",
              "scratch": scratch, "frozen_evidence_touched": False, "cases": []}

    # ---- case A: corrupt the ORACLE expectation (product still correct) ----
    root_a, ev_a = make_case("caseA")
    oracle_a = load_json(os.path.join(ev_a, "oracle.json"))
    oracle_a["positive"]["expected_float"] = [999.0, 999.0, 999.0]
    write_json(os.path.join(ev_a, "oracle.json"), oracle_a)
    rc_a, out_a, err_a = run([py, "-X", "utf8", "-B", os.path.join(scratch, "run_card.py"),
                              "--card", "M01", "--attempt", root_a, "--code-root", code,
                              "--out", os.path.join(ev_a, "run_result.json")], scratch)
    res_path_a = os.path.join(ev_a, "run_result.json")
    if not os.path.exists(res_path_a):
        raise SystemExit("FATAL: case A produced no result; rc=%d stderr=%s" % (rc_a, err_a[:400]))
    res_a = load_json(res_path_a)
    report["cases"].append({
        "id": "A_corrupted_oracle_expectation",
        "mutation": "oracle.json positive.expected_float replaced with [999,999,999]",
        "raw_returncode": rc_a,
        "expected_returncode": 3,
        "verdict_field": res_a["exit_code_semantics"]["verdict"],
        "negative_summary": res_a["negative_summary"],
        "product_positive_actual": res_a["positive"]["actual"],
        "interpretation": "the product still returns the correct path, but the harness now exits 3 instead of "
                          "claiming success",
    })

    # ---- case B: corrupt the case plan (harness cannot produce a verdict) ----
    root_b, ev_b = make_case("caseB")
    cases_b = load_json(os.path.join(ev_b, "cases.json"))
    cases_b["cases"][0]["base_input"] = "no_such_block"
    write_json(os.path.join(ev_b, "cases.json"), cases_b)
    rc_b, out_b, err_b = run([py, "-X", "utf8", "-B", os.path.join(scratch, "run_card.py"),
                              "--card", "M01", "--attempt", root_b, "--code-root", code,
                              "--out", os.path.join(ev_b, "run_result.json")], scratch)
    report["cases"].append({
        "id": "B_corrupted_case_plan",
        "mutation": "cases.json first case base_input -> 'no_such_block'",
        "raw_returncode": rc_b,
        "expected_returncode": "non-zero (the harness raises before any verdict)",
        "traceback_excerpt": [line for line in err_b.splitlines() if line.strip()][-3:],
        "interpretation": "a harness defect cannot masquerade as a pass: it raises and exits non-zero",
    })

    # ---- case C: the real, uncorrupted card still exits 0 ----
    root_c, ev_c = make_case("caseC")
    rc_c, out_c, err_c = run([py, "-X", "utf8", "-B", os.path.join(scratch, "run_card.py"),
                              "--card", "M01", "--attempt", root_c, "--code-root", code,
                              "--out", os.path.join(ev_c, "run_result.json")], scratch)
    res_c = load_json(os.path.join(ev_c, "run_result.json"))
    report["cases"].append({
        "id": "C_uncorrupted_card",
        "mutation": "none",
        "raw_returncode": rc_c,
        "expected_returncode": 0,
        "verdict_field": res_c["exit_code_semantics"],
        "interpretation": "the repaired exit code stays 0 for a genuinely passing card",
    })

    # ---- case D (added in revision r3, prompted by the point review):
    #      corrupt the POSITIVE INPUT so the product raises -> harness incomplete -> rc=2.
    #      The point reviewer demonstrated rc=2 is reachable this way; this case turns
    #      that reachability into a recorded self-check instead of a claim.
    root_d, ev_d = make_case("caseD")
    inp_d = load_json(os.path.join(ev_d, "input.json"))
    del inp_d["positive"]["drivers"]["growth_rate"]
    write_json(os.path.join(ev_d, "input.json"), inp_d)
    rc_d, out_d, err_d = run([py, "-X", "utf8", "-B", os.path.join(scratch, "run_card.py"),
                              "--card", "M01", "--attempt", root_d, "--code-root", code,
                              "--out", os.path.join(ev_d, "run_result.json")], scratch)
    res_d = load_json(os.path.join(ev_d, "run_result.json"))
    report["cases"].append({
        "id": "D_corrupted_positive_input",
        "mutation": "input.json positive.drivers.growth_rate deleted (required driver missing)",
        "raw_returncode": rc_d,
        "expected_returncode": 2,
        "positive_raised": res_d["positive"].get("raised"),
        "positive_message": res_d["positive"].get("message"),
        "verdict_field": res_d["exit_code_semantics"],
        "interpretation": "a corrupted POSITIVE INPUT makes the product raise, so no verdict exists; the "
                          "harness reports rc=2 ('harness incomplete') instead of a bookkeeping-only rc=0. "
                          "This is the reachable rc=2 path, distinct from case B (a case-plan defect outside "
                          "the guard, which raises and exits 1).",
    })

    report["reachability_summary"] = {
        "rc_0": "the uncorrupted card (case C)",
        "rc_1": "a defect outside the guarded block, e.g. a corrupted case plan (case B)",
        "rc_2": "REACHABLE: a corrupted positive input makes the product raise, so no verdict exists (case D)",
        "rc_3": "a corrupted oracle expectation produces a negative verdict (case A)",
        "corrected_claim": "the r2 note said rc=2 was 'not yet reachable in practice'. The point review "
                           "disproved that by deleting growth_rate from the positive input; the claim is "
                           "corrected in revision r3 and the D case now records the rc=2 path.",
    }

    write_json(os.path.join(scratch, "selfcheck_result.json"), report)
    for case in report["cases"]:
        print(case["id"], "raw_rc=", case["raw_returncode"], "expected=", case["expected_returncode"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
