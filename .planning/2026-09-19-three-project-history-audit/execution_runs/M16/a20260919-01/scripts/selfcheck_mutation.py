"""Mutation self-check for one M-card attempt: prove the runner actually goes red.

The frozen evidence is NEVER modified. Every scenario runs the real
``scripts/run_card.py`` against a SCRATCH copy of the frozen input/oracle/cases placed in
``<attempt>/recovery/selfcheck/evidence/<CARD>/``, so the corruption exists only in the
scratch tree. After all scenarios the frozen files are re-hashed and compared with the
freeze-time sha256 recorded by ``scripts/oracle_<CARD>.py`` in ``oracle_selfcheck.json``.

Scenarios (each expects a specific exit code from the frozen runner contract)
  C-control                 scratch copies verbatim                      -> 0 pass
  A-corrupt-value           oracle positive.expected_float -> [999.0]    -> 2 no verdict
  F-corrupt-shape           oracle expected_output_shape.positive.length
                            -> 99 (structure/length not faithful)        -> 2 no verdict
  D-missing-expectation     oracle positive.expected_float deleted       -> 2 no verdict
  B-corrupt-negative-case   cases NEG-CARD value 1.1 -> 0.5 (now legal)  -> 3 refusal missing
  E-harness-error           --code-root points at a non-existent dir     -> 1 harness error

Standard library only; the child's stdout/stderr go straight to files (no pipes).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

FROZEN = ("input.json", "oracle.json", "cases.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=True, indent=1)
        handle.write("\n")


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def hash_frozen(evidence, card):
    """Keys match the freeze-time record written by scripts/oracle_<CARD>.py."""
    return {"evidence/%s/%s" % (card, name): sha256_file(os.path.join(evidence, name))
            for name in FROZEN}


def prepare_scratch(scratch_evidence, evidence, mutate):
    """Copy the frozen evidence verbatim, then apply the scenario mutation to the copy."""
    if os.path.isdir(scratch_evidence):
        shutil.rmtree(scratch_evidence)
    os.makedirs(scratch_evidence)
    for name in FROZEN:
        shutil.copyfile(os.path.join(evidence, name), os.path.join(scratch_evidence, name))
    notes = mutate(scratch_evidence) if mutate else []
    return notes


def mutation_value(scratch_evidence):
    def mutate(_):
        path = os.path.join(scratch_evidence, "oracle.json")
        doc = load_json(path)
        doc["positive"]["expected_float"] = [999.0]
        dump_json(path, doc)
        return ["oracle.json:positive.expected_float -> [999.0]"]
    return mutate


def mutation_shape(scratch_evidence):
    def mutate(_):
        path = os.path.join(scratch_evidence, "oracle.json")
        doc = load_json(path)
        doc["expected_output_shape"]["positive"]["length"] = 99
        dump_json(path, doc)
        return ["oracle.json:expected_output_shape.positive.length -> 99"]
    return mutate


def mutation_missing(scratch_evidence):
    def mutate(_):
        path = os.path.join(scratch_evidence, "oracle.json")
        doc = load_json(path)
        del doc["positive"]["expected_float"]
        dump_json(path, doc)
        return ["oracle.json:positive.expected_float deleted"]
    return mutate


def mutation_negative(scratch_evidence):
    def mutate(_):
        path = os.path.join(scratch_evidence, "cases.json")
        doc = load_json(path)
        case = doc["cases"][0]
        before = json.dumps(case.get("value"))
        case["value"] = {"__float__": 0.5}
        dump_json(path, doc)
        return ["cases.json:%s value %s -> {\"__float__\": 0.5} (now inside the driver domain)"
                % (case["id"], before)]
    return mutate


def run_child(venv_python, run_card, scratch_root, card, code_root, out_path, stdout_path,
              stderr_path):
    argv = [venv_python, "-X", "utf8", "-B", run_card,
            "--card", card,
            "--attempt", scratch_root,
            "--code-root", code_root,
            "--out", out_path]
    with open(stdout_path, "wb") as out_handle, open(stderr_path, "wb") as err_handle:
        completed = subprocess.run(argv, stdout=out_handle, stderr=err_handle, cwd=scratch_root)
    return completed.returncode, argv


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--venv-python", required=True)
    parser.add_argument("--code-root", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", args.card)
    run_card = os.path.join(attempt, "scripts", "run_card.py")
    scratch_root = os.path.join(attempt, "recovery", "selfcheck")
    scratch_evidence = os.path.join(scratch_root, "evidence", args.card)
    os.makedirs(scratch_root, exist_ok=True)

    selfcheck_doc = load_json(os.path.join(evidence, "oracle_selfcheck.json"))
    freeze_time_hashes = selfcheck_doc["frozen_file_sha256_at_freeze_time"]
    hashes_before = hash_frozen(evidence, args.card)

    scenarios = [
        ("C-control", None, 0, "frozen copies verbatim"),
        ("A-corrupt-value", mutation_value(scratch_evidence), 2,
         "corrupted positive expected value must not be able to hide behind a passing rc"),
        ("F-corrupt-shape", mutation_shape(scratch_evidence), 2,
         "corrupted expected output length must be caught by the fidelity check"),
        ("D-missing-expectation", mutation_missing(scratch_evidence), 2,
         "a missing expectation yields no verdict, never a pass"),
        ("B-corrupt-negative-case", mutation_negative(scratch_evidence), 3,
         "a negative case that is no longer refused must produce rc=3"),
        ("E-harness-error", None, 1,
         "an unusable --code-root is a harness error, not a case failure"),
    ]

    results = []
    for name, mutate, expected_rc, purpose in scenarios:
        notes = prepare_scratch(scratch_evidence, evidence, mutate)
        code_root = args.code_root
        if name == "E-harness-error":
            code_root = os.path.join(attempt, "iso", "does_not_exist_on_purpose")
        out_path = os.path.join(scratch_root, "run_result_%s.json" % name)
        stdout_path = os.path.join(scratch_root, "stdout_%s.txt" % name)
        stderr_path = os.path.join(scratch_root, "stderr_%s.txt" % name)
        raw_rc, argv = run_child(args.venv_python, run_card, scratch_root, args.card, code_root,
                                 out_path, stdout_path, stderr_path)
        triggered = None
        if os.path.isfile(out_path):
            child_doc = load_json(out_path)
            triggered = (child_doc.get("exit_code_semantics") or {}).get("triggered")
        results.append({
            "scenario": name,
            "purpose": purpose,
            "mutations_applied_to_the_scratch_copy": notes,
            "argv": argv,
            "raw_rc": raw_rc,
            "expected_rc": expected_rc,
            "rc_as_expected": raw_rc == expected_rc,
            "triggered_conditions": triggered,
            "stdout": os.path.relpath(stdout_path, attempt).replace("\\", "/"),
            "stderr": os.path.relpath(stderr_path, attempt).replace("\\", "/"),
            "run_result": os.path.relpath(out_path, attempt).replace("\\", "/"),
        })

    hashes_after = hash_frozen(evidence, args.card)
    unchanged = (hashes_before == hashes_after)
    matches_freeze_time = (hashes_after == freeze_time_hashes)

    doc = {
        "card_id": args.card,
        "attempt_id": os.path.basename(attempt),
        "purpose": "prove that the verdict-carrying runner really turns red under a corrupted "
                   "expectation or a negative case that is no longer refused, and that the "
                   "frozen oracle was not touched while doing so",
        "runner": os.path.relpath(run_card, attempt).replace("\\", "/"),
        "runner_sha256": sha256_file(run_card),
        "scratch_root": os.path.relpath(scratch_root, attempt).replace("\\", "/"),
        "frozen_evidence_never_modified_by_this_script": True,
        "frozen_hashes_before_selfcheck": hashes_before,
        "frozen_hashes_after_selfcheck": hashes_after,
        "frozen_hashes_recorded_at_freeze_time": freeze_time_hashes,
        "frozen_unchanged_by_the_selfcheck": unchanged,
        "frozen_still_equals_freeze_time_hashes": matches_freeze_time,
        "scenarios": results,
        "all_expected_rcs_observed": all(r["rc_as_expected"] for r in results),
        "observed_rc_set": sorted(set(r["raw_rc"] for r in results)),
        "completed_at_unix": time.time(),
        "completed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = os.path.join(attempt, "recovery", "selfcheck_result.json")
    dump_json(out, doc)

    for entry in results:
        print("scenario %-24s raw_rc=%s expected_rc=%s ok=%s triggered=%s"
              % (entry["scenario"], entry["raw_rc"], entry["expected_rc"],
                 entry["rc_as_expected"], entry["triggered_conditions"]))
    print("frozen unchanged by selfcheck: %s" % unchanged)
    print("frozen still equals freeze-time hashes: %s" % matches_freeze_time)
    print("all expected rcs observed: %s" % doc["all_expected_rcs_observed"])
    return 0 if (doc["all_expected_rcs_observed"] and unchanged and matches_freeze_time) else 4


if __name__ == "__main__":
    raise SystemExit(main())
