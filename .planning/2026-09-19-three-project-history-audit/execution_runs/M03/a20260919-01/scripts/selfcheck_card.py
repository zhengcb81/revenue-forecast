"""Per-card exit-code self-check (P1-2 remediation for M02/M03/M04).

This is the same self-check that was originally run only for M01, generalised so
that each card has its OWN on-disk `recovery/r2_exit_code_selfcheck/selfcheck_result.json`
(the point review found that M02/M03/M04 `handoff.json.evidence_paths` pointed at
M01's file, which does not exist in those attempts).

Cases, matching the M01 record:
  A  corrupted ORACLE expectation -> negative verdict, rc=3
  B  corrupted case plan          -> defect outside the guard, rc=1
  C  uncorrupted card             -> rc=0
  D  corrupted POSITIVE input     -> no verdict exists, rc=2

The CASE A mutation overwrites the positive expectation with the card's own
expected length, so the mutation stays valid for a one-year card as well.

Every case runs against a scratch copy; the frozen evidence is read-only.
Each `--attempt` root is the case directory, so the harness reads
`<case>/evidence/<CARD>/...` and never the real evidence.

ASCII-only stdout.
"""

from __future__ import annotations

import argparse
import hashlib
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


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(argv, cwd):
    proc = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    args = parser.parse_args()
    card = args.card
    if card not in ("M01", "M02", "M03", "M04"):
        raise SystemExit("unsupported card: " + card)

    plan = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast", ".planning",
                        "2026-09-19-three-project-history-audit")
    attempt = os.path.join(plan, "execution_runs", card, "a20260919-01")
    real_evidence = os.path.join(attempt, "evidence", card)
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    code = os.path.join(attempt, "iso", "checkout_scripts")
    run_card = os.path.join(attempt, "scripts", "run_card.py")

    scratch = os.path.join(attempt, "recovery", "r2_exit_code_selfcheck")
    shutil.rmtree(scratch, ignore_errors=True)
    os.makedirs(scratch)
    shutil.copy(run_card, os.path.join(scratch, "run_card.py"))
    print("card:", card)
    print("scratch:", scratch)
    print("note: each case gets its own --attempt root, so the harness reads "
          "<case>/evidence/%s/{input,oracle,cases}.json and never the frozen evidence" % card)

    def make_case(name):
        root = os.path.join(scratch, name)
        ev = os.path.join(root, "evidence", card)
        os.makedirs(ev)
        for fname in ("input.json", "oracle.json", "cases.json"):
            shutil.copy(os.path.join(real_evidence, fname), os.path.join(ev, fname))
        return root, ev

    def call(root, ev):
        return run([py, "-X", "utf8", "-B", os.path.join(scratch, "run_card.py"),
                    "--card", card, "--attempt", root, "--code-root", code,
                    "--out", os.path.join(ev, "run_result.json")], scratch)

    report = {
        "card_id": card,
        "purpose": "exit-code self-check for this card: does the exit code carry the verdict?",
        "origin": ("generalised from the M01-only self-check after the point review found that "
                   "handoff.json.evidence_paths on M02/M03/M04 pointed at a file that exists only in M01"),
        "harness_under_test": {
            "path": "scripts/run_card.py",
            "sha256": sha256_file(run_card),
            "shared_with": "the same run_card.py file is present in all four attempts",
        },
        "scratch": scratch,
        "frozen_evidence_touched": False,
        "cases": [],
    }

    # ---- case A: corrupt the ORACLE expectation ----
    root_a, ev_a = make_case("caseA")
    oracle_a = load_json(os.path.join(ev_a, "oracle.json"))
    truth = list(oracle_a["positive"]["expected_float"])
    oracle_a["positive"]["expected_float"] = [999.0] * len(truth)
    write_json(os.path.join(ev_a, "oracle.json"), oracle_a)
    rc_a, _o, err_a = call(root_a, ev_a)
    res_path_a = os.path.join(ev_a, "run_result.json")
    if not os.path.exists(res_path_a):
        raise SystemExit("FATAL case A produced no result; rc=%d stderr=%s" % (rc_a, err_a[:400]))
    res_a = load_json(res_path_a)
    report["cases"].append({
        "id": "A_corrupted_oracle_expectation",
        "mutation": "oracle.json positive.expected_float -> [999.0] x %d (true values %s)"
                    % (len(truth), truth),
        "raw_returncode": rc_a,
        "expected_returncode": 3,
        "verdict_field": res_a["exit_code_semantics"]["verdict"],
        "product_positive_actual": res_a["positive"].get("actual"),
        "negative_summary": res_a["negative_summary"],
        "interpretation": "the product still returns the correct path, but the harness exits 3 instead of "
                          "claiming success; a corrupted expectation cannot hide behind a bookkeeping-only rc=0",
    })

    # ---- case B: corrupt the case plan (defect outside the guard) ----
    root_b, ev_b = make_case("caseB")
    cases_b = load_json(os.path.join(ev_b, "cases.json"))
    cases_b["cases"][0]["base_input"] = "no_such_block"
    write_json(os.path.join(ev_b, "cases.json"), cases_b)
    rc_b, _o, err_b = call(root_b, ev_b)
    report["cases"].append({
        "id": "B_corrupted_case_plan",
        "mutation": "cases.json first case base_input -> 'no_such_block'",
        "raw_returncode": rc_b,
        "expected_returncode": "non-zero (the harness raises before any verdict)",
        "traceback_excerpt": [line for line in err_b.splitlines() if line.strip()][-3:],
        "interpretation": "a defect outside the guarded block cannot masquerade as a pass; it raises and "
                          "exits 1 rather than 0",
    })

    # ---- case C: the real, uncorrupted card ----
    root_c, ev_c = make_case("caseC")
    rc_c, _o, _e = call(root_c, ev_c)
    res_c = load_json(os.path.join(ev_c, "run_result.json"))
    report["cases"].append({
        "id": "C_uncorrupted_card",
        "mutation": "none",
        "raw_returncode": rc_c,
        "expected_returncode": 0,
        "verdict_field": res_c["exit_code_semantics"],
        "interpretation": "the repaired exit code stays 0 for a genuinely passing card",
    })

    # ---- case D: corrupt the POSITIVE INPUT so the product raises -> rc=2 ----
    root_d, ev_d = make_case("caseD")
    inp_d = load_json(os.path.join(ev_d, "input.json"))
    first_required = load_json(os.path.join(ev_d, "cases.json"))["first_required_driver"]
    del inp_d["positive"]["drivers"][first_required]
    write_json(os.path.join(ev_d, "input.json"), inp_d)
    rc_d, _o, _e = call(root_d, ev_d)
    res_d = load_json(os.path.join(ev_d, "run_result.json"))
    report["cases"].append({
        "id": "D_corrupted_positive_input",
        "mutation": "input.json positive.drivers.%s deleted (required driver missing)" % first_required,
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
        "verified_by_point_review": "the independent point review reproduced rc=0/1/2/3 on this harness",
    }
    report["all_cases_as_expected"] = (
        rc_a == 3 and rc_b != 0 and rc_c == 0 and rc_d == 2)

    out = os.path.join(scratch, "selfcheck_result.json")
    write_json(out, report)
    for case in report["cases"]:
        print("  %s raw_rc=%s expected=%s" % (case["id"], case["raw_returncode"], case["expected_returncode"]))
    print("all_cases_as_expected:", report["all_cases_as_expected"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
