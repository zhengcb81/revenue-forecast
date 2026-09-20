"""Independent re-run check: re-run the bound product command in a THROWAWAY attempt
directory and prove that (a) the raw exit code is 0, and (b) the fresh run_result.json is
byte-identical to the frozen one. Nothing is written into the frozen evidence tree.

Run:
  python -X utf8 -B scripts/rerun_check.py --card M25 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = args.attempt_root
    ev = os.path.join(attempt, "evidence", card)
    tmp = os.path.join(attempt, "recovery", "rerun_check")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(os.path.join(tmp, "evidence", card), exist_ok=True)
    for name in ("input.json", "oracle.json", "cases.json"):
        shutil.copyfile(os.path.join(ev, name), os.path.join(tmp, "evidence", card, name))

    interpreter = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    with open(os.path.join(attempt, "binding.json"), "r", encoding="utf-8") as handle:
        binding = json.load(handle)
    code_root = binding["run_code_root"]
    argv = [interpreter, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "run_card.py"),
            "--card", card, "--attempt", tmp, "--code-root", code_root,
            "--out", os.path.join(tmp, "run_result.json")]
    proc = subprocess.run(argv, capture_output=True, text=True, cwd=attempt)
    with open(os.path.join(tmp, "stdout.txt"), "w", encoding="utf-8") as handle:
        handle.write(proc.stdout)
    with open(os.path.join(tmp, "stderr.txt"), "w", encoding="utf-8") as handle:
        handle.write(proc.stderr)

    fresh = os.path.join(tmp, "run_result.json")
    frozen = os.path.join(ev, "run_result.json")
    fresh_hash = sha256_file(fresh)
    frozen_hash = sha256_file(frozen)
    same_bytes = fresh_hash == frozen_hash

    # also compare the human-readable numbers the runner PRINTS against the evidence files
    checks = {}
    with open(os.path.join(ev, "stdout.txt"), "r", encoding="utf-8-sig") as handle:
        printed = handle.read()
    with open(fresh, "r", encoding="utf-8") as handle:
        result = json.load(handle)
    with open(os.path.join(ev, "oracle.json"), "r", encoding="utf-8") as handle:
        oracle_doc = json.load(handle)
    checks["positive_actual_printed"] = str(result["positive"]["actual"]) in printed
    checks["positive_expected_printed"] = str(oracle_doc["positive"]["expected_float"]) in printed
    checks["negatives_printed"] = all(
        ("negative: %s PASS_rejected" % entry["id"]) in printed
        for entry in result["negatives"])
    checks["negative_summary_printed"] = str(result["negative_summary"]) in printed
    checks["exit_semantics_printed"] = (
        "verdict: %s exit_code: %d" % (result["exit_code_semantics"]["verdict"],
                                       result["exit_code_semantics"]["exit_code"])) in printed
    checks["exit_code_matches"] = result["exit_code_semantics"]["exit_code"] == proc.returncode
    checks["raw_rc_zero"] = proc.returncode == 0
    checks["frozen_documents_unchanged_after_rerun"] = {
        name: sha256_file(os.path.join(ev, name))
        for name in ("input.json", "oracle.json", "cases.json", "run_result.json")}

    payload = {
        "card_id": card,
        "scratch": tmp,
        "argv": argv,
        "raw_rc": proc.returncode,
        "fresh_run_result_sha256": fresh_hash,
        "frozen_run_result_sha256": frozen_hash,
        "byte_identical": same_bytes,
        "printed_value_checks": checks,
        "note": ("the re-run wrote only into recovery/rerun_check/; the frozen evidence directory "
                 "was read but never written"),
    }
    with open(os.path.join(tmp, "rerun_check.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=1)

    print("rerun check for", card)
    print("  raw rc:", proc.returncode)
    print("  run_result.json byte-identical to frozen:", same_bytes)
    for key, value in checks.items():
        if key != "frozen_documents_unchanged_after_rerun":
            print("  %s: %s" % (key, value))
    ok = (proc.returncode == 0 and same_bytes
          and all(v for k, v in checks.items()
                  if k != "frozen_documents_unchanged_after_rerun"))
    print("  RERUN CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
