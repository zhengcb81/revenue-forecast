"""Run the four REM-21 arms (E/F/B/G) for the M05-M08 batch with REAL processes.

Raw rc is read from the child process itself (subprocess returncode), never inferred.
Every path is redirected into this batch's own _scratch tree; nothing under
execution_runs/<CARD>/ is ever written.

Arms
  E  new runner, frozen cases.json (green control)
  F  new runner, mutated cases.json (one negative's "expected" -> "ValueError")
  B  OLD runner (byte copy of the historical runner), SAME mutated cases.json as F
  G  new runner, mutated cases.json (that negative's "expected" key DELETED)
"""
import hashlib
import json
import os
import subprocess
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = "M05-M08"
SCRATCH = os.path.join(ATTEMPT, "_scratch", BATCH)
OUTDIR = os.path.join(ATTEMPT, BATCH)
PY = os.path.join(PLAN, "execution_runs", "M05", "a20260919-01", "iso", "venv", "Scripts", "python.exe")
CODE_ROOT = os.path.join(SCRATCH, "code_root")
CARDS = ["M05", "M06", "M07", "M08"]

RUNNERS = {
    "new": os.path.join(OUTDIR, "run_card.py"),
    "old": os.path.join(OUTDIR, "run_card_before.py"),
}
ARM_RUNNER = {"E": "new", "F": "new", "B": "old", "G": "new"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def run_arm(arm, card):
    root = os.path.join(SCRATCH, arm)
    out_path = os.path.join(root, f"out_{card}.json")
    rr_path = os.path.join(root, f"formula_result_{card}.json")
    stdout_path = os.path.join(root, f"stdout_{card}.txt")
    stderr_path = os.path.join(root, f"stderr_{card}.txt")
    argv = [PY, "-X", "utf8", "-B", RUNNERS[ARM_RUNNER[arm]],
            "--card", card,
            "--attempt", root,
            "--code-root", CODE_ROOT,
            "--out", out_path,
            "--run-result-out", rr_path]
    proc = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    with open(stdout_path, "w", encoding="utf-8") as fh:
        fh.write(proc.stdout)
    with open(stderr_path, "w", encoding="utf-8") as fh:
        fh.write(proc.stderr)
    doc = json.load(open(out_path, "r", encoding="utf-8")) if os.path.exists(out_path) else None
    rr_doc = json.load(open(rr_path, "r", encoding="utf-8")) if os.path.exists(rr_path) else None
    sem = (doc or {}).get("exit_code_semantics", {})
    nsum = (doc or {}).get("negative_summary", {})
    ncnt = (doc or {}).get("negative_counts", {})
    negs = (doc or {}).get("negatives", [])
    return {
        "arm": arm,
        "card": card,
        "runner": RUNNERS[ARM_RUNNER[arm]],
        "runner_role": ARM_RUNNER[arm],
        "argv": argv,
        "cwd": root,
        "raw_rc": proc.returncode,
        "cases_json": os.path.join(root, "evidence", card, "cases.json"),
        "cases_json_sha256": sha256_file(os.path.join(root, "evidence", card, "cases.json")),
        "out_json": out_path,
        "out_json_sha256": sha256_file(out_path) if os.path.exists(out_path) else None,
        "run_result_out_json": rr_path,
        "run_result_out_sha256": sha256_file(rr_path) if os.path.exists(rr_path) else None,
        "run_result_out_identical_to_out": (doc == rr_doc) if (doc and rr_doc) else None,
        "verdict": sem.get("verdict"),
        "exit_code_in_doc": sem.get("exit_code"),
        "positive_ok": sem.get("positive_ok"),
        "continuity_ok": sem.get("continuity_ok"),
        "negatives_ok": sem.get("negatives_ok"),
        "cases_json_declared_expectations_usable": sem.get("cases_json_declared_expectations_usable"),
        "declared_expectation_mismatch_case_ids": sem.get("declared_expectation_mismatch_case_ids"),
        "declaration_unusable_case_ids": sem.get("declaration_unusable_case_ids"),
        "no_verdict_reason": (doc or {}).get("no_verdict_reason"),
        "negative_counts": ncnt,
        "negative_summary_failed": nsum.get("failed"),
        "negative_summary_not_judged": nsum.get("not_judged"),
        "declared_expectations_enforced": nsum.get("declared_expectations_enforced"),
        "declared_expectations_in_cases_json": nsum.get("declared_expectations_in_cases_json"),
        "declared_expectation_comparison": nsum.get("declared_expectation_comparison"),
        "negatives": [{k: e.get(k) for k in
                       ("id", "declared", "raised", "verdict", "judged",
                        "declared_expectation_ok", "declared_expectation_mismatch",
                        "declared_expectation_not_met", "declared_expectation_comparison")}
                      for e in negs],
        "negative_defaults_ok": (doc or {}).get("defaults_ok"),
        "negative_tolerances_ok": (doc or {}).get("tolerances_ok"),
    }


def main():
    results = []
    for arm in ("E", "F", "B", "G"):
        for card in CARDS:
            r = run_arm(arm, card)
            results.append(r)
            print(f"[{arm}/{card}] raw_rc={r['raw_rc']} verdict={r['verdict']!r} "
                  f"mismatch_ids={r['declared_expectation_mismatch_case_ids']} "
                  f"unusable_ids={r['declaration_unusable_case_ids']} "
                  f"counts={r['negative_counts']}", flush=True)
    with open(os.path.join(SCRATCH, "arms_raw.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)
    print("wrote", os.path.join(SCRATCH, "arms_raw.json"))


if __name__ == "__main__":
    main()
