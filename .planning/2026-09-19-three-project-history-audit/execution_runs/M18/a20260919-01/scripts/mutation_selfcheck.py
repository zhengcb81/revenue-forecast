"""Mutation self-check: prove the runner goes RED before trusting its GREEN.

Five scratch runs, all against COPIES under <attempt>/recovery/selfcheck, never
against the frozen evidence:

  A  corrupt the frozen positive expectation              -> expect rc 3 (negative verdict)
  B  neuter one negative case so it cannot be rejected     -> expect rc 3 (negative verdict)
  C  corrupt the frozen expected LENGTH (fidelity)         -> expect rc 2 (no verdict)
  D  remove cases.json from the scratch copy               -> expect rc 1 (harness error)
  E  the uncorrupted copy                                  -> expect rc 0 (green restored)

Afterwards the frozen evidence files are re-hashed and compared with the hashes
captured before the mutations, so "the scratch runs did not touch the frozen
oracle" is a measurement, not a promise.

Usage:
  python -X utf8 -B mutation_selfcheck.py --card M17 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

# A REGISTERED driver of the card's model, used to neuter N04 (add_driver) so the
# product accepts it and the runner must report FAIL_not_rejected.  The script
# asserts the name really appears in the frozen positive input, so this cannot
# drift silently.
VALID_OPTIONAL_DRIVER = {
    "M17": "milestone_revenue",
    "M18": "other_revenue",
    "M19": "other_revenue",
    "M20": "usage_revenue",
}

CARDS = {
    "M17": "licensing_commercial",
    "M18": "advertising",
    "M19": "gaming",
    "M20": "cohort_subscription",
}

FROZEN_FILES = ("input.json", "oracle.json", "cases.json")


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, doc):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--interpreter", default=sys.executable,
                        help="interpreter used for the scratch runner child (the bound attempt venv)")
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    code_root = os.path.join(attempt, "iso", "checkout_scripts")
    scratch = os.path.join(attempt, "recovery", "selfcheck")

    frozen = {name: sha256(os.path.join(evidence, name)) for name in FROZEN_FILES}
    frozen_before = dict(frozen)

    valid_driver = VALID_OPTIONAL_DRIVER[card]
    positive = read_json(os.path.join(evidence, "input.json"))["positive"]
    if valid_driver not in positive["drivers"]:
        raise SystemExit("SELFCHECK ERROR: %s is not a driver of the frozen positive input"
                         % valid_driver)

    if os.path.isdir(scratch):
        shutil.rmtree(scratch)
    os.makedirs(os.path.join(scratch, "scripts"))
    os.makedirs(os.path.join(scratch, "evidence", card))
    shutil.copyfile(os.path.join(attempt, "scripts", "run_card.py"),
                    os.path.join(scratch, "scripts", "run_card.py"))

    def reset_copies():
        for name in FROZEN_FILES:
            shutil.copyfile(os.path.join(evidence, name),
                            os.path.join(scratch, "evidence", card, name))

    def run(label):
        out = os.path.join(scratch, "run_result_%s.json" % label)
        argv = [args.interpreter, "-X", "utf8", "-B", os.path.join(scratch, "scripts", "run_card.py"),
                "--card", card, "--attempt", scratch, "--code-root", code_root,
                "--out", out]
        completed = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                                   errors="replace")
        with open(os.path.join(scratch, "stdout_%s.txt" % label), "w", encoding="utf-8") as handle:
            handle.write(completed.stdout or "")
        with open(os.path.join(scratch, "stderr_%s.txt" % label), "w", encoding="utf-8") as handle:
            handle.write(completed.stderr or "")
        verdict = None
        exit_code_in_file = None
        negative_counts = None
        failed_negatives = None
        verdict_reasons = None
        if os.path.isfile(out):
            doc = read_json(out)
            verdict = doc.get("verdict")
            exit_code_in_file = doc.get("exit_code")
            negative_counts = doc.get("negative_counts")
            failed_negatives = (doc.get("negative_summary") or {}).get("failed")
            verdict_reasons = doc.get("verdict_reasons")
        return {
            "label": label,
            "argv": argv,
            "raw_returncode": completed.returncode,
            "verdict_in_result_file": verdict,
            "exit_code_in_result_file": exit_code_in_file,
            "negative_counts_in_result_file": negative_counts,
            "failed_negatives_in_result_file": failed_negatives,
            "verdict_reasons_in_result_file": verdict_reasons,
            "stdout_tail": (completed.stdout or "").splitlines()[-3:],
            "stdout_path": os.path.join(scratch, "stdout_%s.txt" % label),
            "stderr_path": os.path.join(scratch, "stderr_%s.txt" % label),
            "result_path": out,
        }

    runs = []

    # A: corrupt the positive expectation
    reset_copies()
    oracle_path = os.path.join(scratch, "evidence", card, "oracle.json")
    oracle = read_json(oracle_path)
    original_expected = list(oracle["positive"]["expected_float"])
    oracle["positive"]["expected_float"] = [v + 1 for v in original_expected]
    write_json(oracle_path, oracle)
    entry_a = run("A_corrupted_positive_expectation")
    entry_a["mutation"] = {"file": "evidence/%s/oracle.json" % card,
                           "field": "positive.expected_float",
                           "from": original_expected, "to": oracle["positive"]["expected_float"]}
    entry_a["expected_rc"] = 3
    runs.append(entry_a)

    # B: neuter a negative case (N04 add_driver becomes a valid optional driver)
    reset_copies()
    cases_path = os.path.join(scratch, "evidence", card, "cases.json")
    cases = read_json(cases_path)
    target = None
    for case in cases["cases"]:
        if case["id"] == "N04":
            target = case
            break
    if target is None:
        raise SystemExit("SELFCHECK ERROR: no N04 case in the frozen cases.json")
    original_driver = target["driver"]
    target["driver"] = valid_driver
    write_json(cases_path, cases)
    entry_b = run("B_neutered_negative_case")
    entry_b["mutation"] = {"file": "evidence/%s/cases.json" % card, "case": "N04",
                           "field": "driver", "from": original_driver, "to": valid_driver,
                           "why": ("a registered driver is accepted, so the negative case can no "
                                   "longer be rejected and the runner must say so")}
    entry_b["expected_rc"] = 3
    runs.append(entry_b)

    # C: corrupt the frozen expected length (fidelity mismatch -> no verdict)
    reset_copies()
    oracle = read_json(oracle_path)
    original_tolerances = list(oracle["positive"]["tolerances"])
    oracle["positive"]["expected_float"] = list(original_expected) + [original_expected[0]]
    oracle["positive"]["tolerances"] = list(original_tolerances) + [original_tolerances[0]]
    write_json(oracle_path, oracle)
    entry_c = run("C_corrupted_expectation_length")
    entry_c["mutation"] = {"file": "evidence/%s/oracle.json" % card,
                           "field": "positive.expected_float and positive.tolerances",
                           "from_length": len(original_expected),
                           "to_length": len(oracle["positive"]["expected_float"]),
                           "why": ("the frozen shape is internally consistent but no longer matches "
                                   "len(years), so no faithful comparison exists and the runner must "
                                   "refuse a verdict instead of comparing what it can")}
    entry_c["expected_rc"] = 2
    runs.append(entry_c)

    # D: remove cases.json (harness error)
    reset_copies()
    os.remove(cases_path)
    entry_d = run("D_missing_cases_file")
    entry_d["mutation"] = {"file": "evidence/%s/cases.json" % card,
                           "action": "deleted from the scratch copy"}
    entry_d["expected_rc"] = 1
    runs.append(entry_d)

    # E: uncorrupted copy -> green restored
    # F: tamper the DECLARED expectation of a negative case (the isinstance trap).
    # The case still raises ModelRegistryError, but the frozen cases.json declares "ValueError".
    # Because ModelRegistryError IS a ValueError subclass, an isinstance-based comparison would
    # silently pass; the runner must compare the EXACT type name and go red.
    reset_copies()
    cases = read_json(cases_path)
    declared_target = None
    for case in cases["cases"]:
        if case["id"] == "N02":
            declared_target = case
            break
    if declared_target is None:
        raise SystemExit("SELFCHECK ERROR: no N02 case in the frozen cases.json")
    original_declared = declared_target["expected"]
    declared_target["expected"] = "ValueError"
    write_json(cases_path, cases)
    entry_f = run("F_tampered_declared_expectation")
    entry_f["mutation"] = {"file": "evidence/%s/cases.json" % card, "case": "N02",
                           "field": "expected", "from": original_declared, "to": "ValueError",
                           "why": ("the case still raises ModelRegistryError, but the declaration "
                                   "says ValueError; ModelRegistryError is a ValueError subclass, so "
                                   "an isinstance comparison would pass silently. The runner must "
                                   "compare the EXACT type name and report the mismatch")}
    entry_f["expected_rc"] = 3
    runs.append(entry_f)

    reset_copies()
    entry_e = run("E_uncorrupted_copy")
    entry_e["mutation"] = {"action": "none; byte copy of the frozen evidence"}
    entry_e["expected_rc"] = 0
    runs.append(entry_e)

    frozen_after = {name: sha256(os.path.join(evidence, name)) for name in FROZEN_FILES}
    frozen_unchanged = frozen_before == frozen_after
    all_as_expected = all(r["raw_returncode"] == r["expected_rc"] for r in runs)

    doc = {
        "card_id": card,
        "model_id": CARDS[card],
        "purpose": ("prove the runner's exit code carries the verdict: corrupt a COPY of the frozen "
                    "expectation, of a negative assertion, or of a declared expectation, and show the "
                    "runner turns red, then show green returns on the uncorrupted copy"),
        "scratch_root": scratch,
        "scratch_scope": "recovery/selfcheck only; the frozen evidence was never written to",
        "runner_sha256": sha256(os.path.join(attempt, "scripts", "run_card.py")),
        "exit_code_contract": {"0": "pass", "1": "harness error",
                               "2": "no verdict (missing expectation or fidelity mismatch)",
                               "3": ("negative verdict, including a negative case that was not "
                                     "rejected with the exact type name declared in cases.json")},
        "valid_optional_driver_used_to_neuter_N04": valid_driver,
        "frozen_evidence_sha256_before_mutations": frozen_before,
        "frozen_evidence_sha256_after_mutations": frozen_after,
        "frozen_evidence_unchanged": frozen_unchanged,
        "runs": runs,
        "all_mutations_produced_the_expected_exit_code": all_as_expected,
        "red_then_green": ("A/B/C/D/F are red (rc != 0) and E is green (rc = 0) only if "
                           "all_mutations_produced_the_expected_exit_code is true"),
    }
    out = os.path.join(evidence, "mutation_selfcheck.json")
    write_json(out, doc)
    write_json(os.path.join(attempt, "recovery", "selfcheck_result.json"), doc)

    for r in runs:
        print("selfcheck %-38s rc=%s expected=%s verdict=%s"
              % (r["label"], r["raw_returncode"], r["expected_rc"], r["verdict_in_result_file"]))
    print("frozen_evidence_unchanged", frozen_unchanged)
    print("all_mutations_produced_the_expected_exit_code", all_as_expected, "->", out)
    return 0 if (all_as_expected and frozen_unchanged) else 3


if __name__ == "__main__":
    raise SystemExit(main())
