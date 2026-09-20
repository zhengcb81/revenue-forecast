"""Exit-code mutation self-check: prove the runner goes RED on a corrupted expectation.

The frozen evidence of the attempt is NEVER modified: every mutation is applied to a
scratch copy under recovery/selfcheck/<case>/ and the runner is invoked with
--attempt <scratch>, so the only thing that changes is the expectation the runner reads.
The product code under test is the attempt-local isolated snapshot and is identical for
all cases.

Cases (per card):
  A  corrupt the positive expectation in a scratch oracle.json        -> expect rc 2
  B  corrupt the expected exception name of the NEG-CARD case         -> expect rc 3
  C  neutralise the NEG-CARD mutation (make it a no-op)               -> expect rc 3
  D  delete positive.expected_float (expectation missing)             -> expect rc 2
  E  uncorrupted scratch copy (control)                               -> expect rc 0

Run (from an attempt root):
  python -X utf8 -B scripts/selfcheck_mutations.py --card M09 --attempt <attempt> \
      --python <attempt>/iso/venv/Scripts/python.exe
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

SCRATCH_REL = os.path.join("recovery", "selfcheck")


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def prepare(case_dir, card, attempt, frozen):
    shutil.rmtree(case_dir, ignore_errors=True)
    ev = os.path.join(case_dir, "evidence", card)
    os.makedirs(ev)
    os.makedirs(os.path.join(case_dir, "scripts"))
    written = {}
    for name in ("input.json", "oracle.json", "cases.json"):
        src = os.path.join(attempt, "evidence", card, name)
        dst = os.path.join(ev, name)
        shutil.copyfile(src, dst)
        written[name] = dst
    shutil.copyfile(os.path.join(attempt, "scripts", "run_card.py"),
                    os.path.join(case_dir, "scripts", "run_card.py"))
    frozen_hashes = {name: sha256_file(path) for name, path in written.items()}
    return ev, written, frozen_hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--code-root", default=None)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    card = args.card
    code_root = args.code_root or os.path.join(attempt, "iso", "checkout_scripts")
    frozen_dir = os.path.join(attempt, "evidence", card)
    scratch_root = os.path.join(attempt, SCRATCH_REL)

    frozen_before = {name: sha256_file(os.path.join(frozen_dir, name))
                     for name in ("input.json", "oracle.json", "cases.json",
                                  "observation_expected.json", "oracle_selfcheck.json")}
    code_before = sha256_file(os.path.join(code_root, "model_registry.py"))

    cases = {}
    for case_id in ("A", "B", "C", "D", "E"):
        case_dir = os.path.join(scratch_root, case_id)
        ev, written, _ = prepare(case_dir, card, attempt, frozen_before)

        mutation = ""
        if case_id == "A":
            doc = load_json(written["oracle.json"])
            original = list(doc["positive"]["expected_float"])
            doc["positive"]["expected_float"] = [999.0] * len(original)
            dump_json(written["oracle.json"], doc)
            mutation = "positive.expected_float %s -> %s" % (original, doc["positive"]["expected_float"])
        elif case_id == "B":
            doc = load_json(written["cases.json"])
            for case in doc["cases"]:
                if case["id"] == "NEG-CARD":
                    case["expected"] = "TypeError"
            dump_json(written["cases.json"], doc)
            mutation = "cases.json NEG-CARD expected -> TypeError"
        elif case_id == "C":
            doc = load_json(written["cases.json"])
            for case in doc["cases"]:
                if case["id"] == "NEG-CARD":
                    case["kind"] = "set_base_revenue"
                    case["value"] = 0
                    case.pop("driver", None)
                    case.pop("index", None)
            dump_json(written["cases.json"], doc)
            mutation = "cases.json NEG-CARD neutralised to a no-op (base_revenue = 0)"
        elif case_id == "D":
            doc = load_json(written["oracle.json"])
            doc["positive"].pop("expected_float", None)
            dump_json(written["oracle.json"], doc)
            mutation = "oracle.json positive.expected_float deleted (expectation missing)"
        else:
            mutation = "none (uncorrupted control copy)"

        out_json = os.path.join(case_dir, "run_result.json")
        stdout_path = os.path.join(case_dir, "stdout.txt")
        stderr_path = os.path.join(case_dir, "stderr.txt")
        argv = [args.python, "-X", "utf8", "-B",
                os.path.join(case_dir, "scripts", "run_card.py"),
                "--card", card, "--attempt", case_dir, "--code-root", code_root,
                "--out", out_json]
        with open(stdout_path, "w", encoding="utf-8", newline="\n") as out_handle, \
                open(stderr_path, "w", encoding="utf-8", newline="\n") as err_handle:
            completed = subprocess.run(argv, stdout=out_handle, stderr=err_handle,
                                       cwd=case_dir, check=False)
        text = open(stdout_path, "r", encoding="utf-8").read()
        verdict_line = [line for line in text.splitlines() if line.startswith("verdict:")]
        summary_line = [line for line in text.splitlines() if line.startswith("negative_summary:")]
        cases[case_id] = {
            "scratch_dir": case_dir,
            "argv": argv,
            "cwd": case_dir,
            "mutation": mutation,
            "raw_exit_code": completed.returncode,
            "expected_exit_code": {"A": 2, "B": 3, "C": 3, "D": 2, "E": 0}[case_id],
            "verdict_line": verdict_line[-1] if verdict_line else None,
            "negative_summary_line": summary_line[-1] if summary_line else None,
            "stdout_file": stdout_path,
            "stderr_file": stderr_path,
        }
        cases[case_id]["ok"] = (completed.returncode == cases[case_id]["expected_exit_code"])

    frozen_after = {name: sha256_file(os.path.join(frozen_dir, name)) for name in frozen_before}
    code_after = sha256_file(os.path.join(code_root, "model_registry.py"))

    result = {
        "card_id": card,
        "attempt_id": os.path.basename(attempt),
        "kind": "exit-code mutation self-check (red-then-green)",
        "frozen_evidence_not_modified": frozen_before == frozen_after,
        "frozen_hashes_before": frozen_before,
        "frozen_hashes_after": frozen_after,
        "product_code_under_test": {
            "path": os.path.join(code_root, "model_registry.py"),
            "sha256_before": code_before,
            "sha256_after": code_after,
            "unchanged": code_before == code_after,
            "note": "only expectations were mutated; the code under test was never touched",
        },
        "cases": cases,
        "all_cases_as_expected": all(v["ok"] for v in cases.values()),
        "restore_evidence": ("case E is an uncorrupted scratch copy of the same frozen evidence and "
                            "must return rc 0 again, which is the green half of the red-then-green "
                            "proof; the frozen evidence hashes are unchanged before and after"),
    }
    dump_json(os.path.join(attempt, "recovery", "selfcheck_result.json"), result)

    print("card", card)
    for case_id in sorted(cases):
        row = cases[case_id]
        print("case", case_id, "mutation:", row["mutation"])
        print("   raw_exit_code", row["raw_exit_code"], "expected", row["expected_exit_code"],
              "ok", row["ok"])
        print("   ", row["verdict_line"])
    print("frozen_evidence_not_modified", result["frozen_evidence_not_modified"])
    print("product_sha256_unchanged", code_before == code_after, code_after)
    print("all_cases_as_expected", result["all_cases_as_expected"])
    return 0 if result["all_cases_as_expected"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
