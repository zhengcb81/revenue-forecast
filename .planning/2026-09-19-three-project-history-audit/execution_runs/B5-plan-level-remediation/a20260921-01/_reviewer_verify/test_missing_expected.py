"""Reviewer test of the claim: 'missing `expected` -> rc=3' is FALSE.

Runs the UNPATCHED historical runner (byte copy = run_card_before.py) on a cases.json
whose first negative case's `expected` KEY IS DELETED, on real child processes.
Records the raw rc, stderr, and whether ANY output/evidence file was written.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RV = os.path.join(ATTEMPT, "_reviewer_verify", "missing_expected")
TARGETS = {
    "M05-M08": ("M05", "run_card_before.py", ["--out", "--run-result-out"]),
    "M09-M12": ("M09", "run_card_before.py",
                ["--out", "--formula-out", "--negative-out", "--stdout-out", "--stderr-out"]),
    "M25-M28": ("M25", "run_card_before.py", ["--out", "--run-result-out"]),
}


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


results = []
for batch, (rep, runner_name, flags) in TARGETS.items():
    card = rep
    root = os.path.join(RV, batch)
    shutil.rmtree(root, ignore_errors=True)
    ev = os.path.join(root, "evidence", card)
    os.makedirs(ev, exist_ok=True)
    src = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "evidence", card)
    for name in ("input.json", "oracle.json"):
        shutil.copyfile(os.path.join(src, name), os.path.join(ev, name))
    doc = json.load(open(os.path.join(src, "cases.json"), encoding="utf-8"))
    target = None
    for case in doc["cases"]:
        if isinstance(case.get("expected"), str) and case["expected"].strip():
            target = case["id"]
            break
    for case in doc["cases"]:
        if case["id"] == target:
            del case["expected"]
    with open(os.path.join(ev, "cases.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False)
    cr = os.path.join(root, "code_root")
    os.makedirs(cr, exist_ok=True)
    for name in os.listdir(src.replace(os.path.join("evidence", card), "iso/checkout_scripts")):
        pass
    csrc = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "iso", "checkout_scripts")
    for name in os.listdir(csrc):
        if os.path.isfile(os.path.join(csrc, name)):
            shutil.copyfile(os.path.join(csrc, name), os.path.join(cr, name))

    py = os.path.join(PLAN, "execution_runs", card, "a20260919-01", "iso", "venv",
                      "Scripts", "python.exe")
    runner = os.path.join(ATTEMPT, batch, runner_name)
    argv = [py, "-X", "utf8", "-B", runner, "--card", card, "--attempt", root,
            "--code-root", cr]
    for flag in flags:
        argv += [flag, os.path.join(root, flag.lstrip("-") + ".json")]
    before = set(os.listdir(root))
    proc = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    after = set(os.listdir(root))
    written = sorted(after - before)
    rec = {
        "batch": batch, "card": card, "deleted_key_case": target,
        "runner": os.path.relpath(runner, ATTEMPT),
        "runner_sha256": sha(runner),
        "runner_is_pristine_historical": sha(runner) == sha(
            os.path.join(PLAN, "execution_runs", card, "a20260919-01", "scripts", "run_card.py")),
        "raw_rc": proc.returncode,
        "files_written_in_arm_root": written,
        "out_json_written": any(f.startswith("out") for f in written),
        "stdout_tail": proc.stdout.strip().splitlines()[-4:],
        "stderr_tail": proc.stderr.strip().splitlines()[-8:],
        "exception_type_in_stderr": None,
    }
    for line in reversed(proc.stderr.strip().splitlines()):
        if "Error" in line or "Exception" in line:
            rec["exception_type_in_stderr"] = line.strip()
            break
    results.append(rec)
    print("%-8s %-4s deleted=%-10s raw_rc=%-3s files_written=%d  %s" % (
        batch, card, target, proc.returncode, len(written),
        (rec["exception_type_in_stderr"] or "")[:70]))
    sys.stdout.flush()

with open(os.path.join(RV, "missing_expected_results.json"), "w", encoding="utf-8") as fh:
    json.dump({"arms": results}, fh, ensure_ascii=False, indent=1)
print("\nwritten missing_expected_results.json")
