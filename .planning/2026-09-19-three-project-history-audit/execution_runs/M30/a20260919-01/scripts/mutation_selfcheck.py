"""Mutation self-check: prove the runner goes RED before trusting its GREEN.

Five scratch runs, all against COPIES under <attempt>/recovery/selfcheck, never against the
frozen evidence:

  A  corrupt the frozen positive expectation              -> expect rc 3 (negative verdict)
  B  neuter one negative case so it cannot be rejected     -> expect rc 3 (negative verdict)
  C  corrupt the frozen expected LENGTH (fidelity)         -> expect rc 2 (no verdict)
  D  remove cases.json from the scratch copy               -> expect rc 1 (harness error)
  E  the uncorrupted copy                                  -> expect rc 0 (green restored)

Card-specific note for M29-M31: these three models declare NO optional driver, so the N04
mutation cannot be neutered by naming a registered driver (the accepted M17-M20 version did
exactly that).  Module C of the card text asks instead that the frozen break be carried by
the STOCK-FLOW continuity case that these cards ship, so mutation B moves CONT-BREAK onto a
balancing two-year input: the bridge then accepts it, CONT-BREAK can no longer be rejected,
and the runner must report FAIL_not_rejected.  The mutation asserts that the unpatched
CONT-BREAK base input really is rejected first, so the neutering cannot silently become a
no-op.

Afterwards the frozen evidence files are re-hashed and compared with the hashes captured
before the mutations, so "the scratch runs did not touch the frozen oracle" is a
measurement, not a promise.

Usage:
  python -X utf8 -B mutation_selfcheck.py --card M29 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys

CARDS = {
    "M29": "commercial_launch",
    "M30": "finite_adoption",
    "M31": "inventory_sellthrough",
}

FROZEN_FILES = ("input.json", "oracle.json", "cases.json")

# The balancing two-year replacement for the continuity break: each year balances on its own AND
# year 2 opening equals year 1 closing, so the bridge check has nothing to refuse.
BALANCING_CONTINUITY = {
    "M29": {"years": [2027, 2029]},  # not applicable: M29 has no bridge; see NOTE below
    "M30": {"opening_unserved_market": [500, 350], "closing_unserved_market": [350, 350]},
    "M31": {"opening_inventory": [100, 85], "closing_inventory": [85, 85]},
}

# M29 (commercial_launch) has NO stock-flow bridge at all, so its CONT-BREAK case is a
# set_years case ([2027, 2029]) that is refused by the consecutive-fiscal-year rule.  The
# neutering mutation for M29 therefore replaces those years with the balancing two-year
# sequence [2027, 2028], which the model accepts.
BALANCING_YEARS = {"M29": [2027, 2028]}


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
        if os.path.isfile(out):
            doc = read_json(out)
            verdict = doc.get("verdict")
            exit_code_in_file = doc.get("exit_code")
        return {
            "label": label,
            "argv": argv,
            "raw_returncode": completed.returncode,
            "verdict_in_result_file": verdict,
            "exit_code_in_file": exit_code_in_file,
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

    # B-precondition: the UNPATCHED frozen negative must really be rejected
    reset_copies()
    cases_path = os.path.join(scratch, "evidence", card, "cases.json")
    input_path = os.path.join(scratch, "evidence", card, "input.json")
    cases = read_json(cases_path)
    input_doc = read_json(input_path)
    target = None
    for case in cases["cases"]:
        if case["id"] == "CONT-BREAK":
            target = case
            break
    if target is None:
        raise SystemExit("SELFCHECK ERROR: no CONT-BREAK case in the frozen cases.json")
    unpatched = run("B0_unpatched_continuity_break")
    unpatched["mutation"] = {"action": "none; the frozen CONT-BREAK case as generated"}
    unpatched["expected_rc"] = 0
    unpatched["note"] = ("the runner is green here because CONT-BREAK IS rejected, which is exactly "
                         "what the next mutation removes")
    unpatched_negative = None
    if os.path.isfile(unpatched["result_path"]):
        doc = read_json(unpatched["result_path"])
        for entry in doc.get("negatives", []):
            if entry["id"] == "CONT-BREAK":
                unpatched_negative = entry["verdict"]
    unpatched["cont_break_verdict_in_that_run"] = unpatched_negative
    runs.append(unpatched)
    if unpatched["raw_returncode"] != 0 or unpatched_negative != "PASS_rejected":
        raise SystemExit("SELFCHECK ERROR: the frozen CONT-BREAK case is not rejected by the product; "
                         "the neutering mutation would be meaningless")

    # B: neuter CONT-BREAK so the product accepts it
    reset_copies()
    cases = read_json(cases_path)
    for case in cases["cases"]:
        if case["id"] == "CONT-BREAK":
            original_case = copy.deepcopy(case)
            if card in BALANCING_YEARS:
                case["kind"] = "set_years"
                case["driver"] = None
                case.pop("index", None)
                case["value"] = list(BALANCING_YEARS[card])
            else:
                case["kind"] = "set_driver_multi"
                case["driver"] = None
                case.pop("index", None)
                case["value"] = copy.deepcopy(BALANCING_CONTINUITY[card])
    write_json(cases_path, cases)
    entry_b = run("B_neutered_negative_case")
    entry_b["mutation"] = {"file": "evidence/%s/cases.json" % card, "case": "CONT-BREAK",
                           "from": original_case, "to": [c for c in cases["cases"]
                                                         if c["id"] == "CONT-BREAK"][0],
                           "why": ("the mutated break balances in every year and across years, so the "
                                   "product accepts it and the negative case can no longer be rejected; "
                                   "the runner must say so. These three cards declare no optional "
                                   "driver, so the M17-M20 way of neutering a negative (naming a "
                                   "registered driver) does not apply here")}
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
    reset_copies()
    entry_e = run("E_uncorrupted_copy")
    entry_e["mutation"] = {"action": "none; byte copy of the frozen evidence"}
    entry_e["expected_rc"] = 0
    runs.append(entry_e)

    frozen_after = {name: sha256(os.path.join(evidence, name)) for name in FROZEN_FILES}
    frozen_unchanged = frozen_before == frozen_after
    all_as_expected = all(r["raw_returncode"] == r["expected_rc"] for r in runs)
    reds = [r["label"] for r in runs if r["expected_rc"] != 0]
    greens = [r["label"] for r in runs if r["expected_rc"] == 0]

    doc = {
        "card_id": card,
        "model_id": CARDS[card],
        "purpose": ("prove the runner's exit code carries the verdict: corrupt a COPY of the frozen "
                    "expectation or of a negative assertion and show the runner turns red, then show "
                    "green returns on the uncorrupted copy"),
        "scratch_root": scratch,
        "scratch_scope": "recovery/selfcheck only; the frozen evidence was never written to",
        "runner_sha256": sha256(os.path.join(attempt, "scripts", "run_card.py")),
        "exit_code_contract": {"0": "pass", "1": "harness error",
                               "2": "no verdict (missing expectation or fidelity mismatch)",
                               "3": "negative verdict"},
        "model_has_no_optional_driver": True,
        "neutering_strategy": ("CONT-BREAK is moved onto a fully balancing input; the M17-M20 strategy of "
                              "naming a registered optional driver is impossible here because these "
                              "three models declare no optional driver"),
        "frozen_evidence_sha256_before_mutations": frozen_before,
        "frozen_evidence_sha256_after_mutations": frozen_after,
        "frozen_evidence_unchanged": frozen_unchanged,
        "runs": runs,
        "red_labels": reds,
        "green_labels": greens,
        "all_mutations_produced_the_expected_exit_code": all_as_expected,
        "red_then_green": ("A/B/C/D are red (rc != 0) and E is green (rc = 0) only if "
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
