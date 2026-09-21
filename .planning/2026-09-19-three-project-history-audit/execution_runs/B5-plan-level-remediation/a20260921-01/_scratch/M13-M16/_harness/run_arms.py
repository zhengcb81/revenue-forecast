"""REM-21 / B5, batch M13-M16 - scratch arm runner.

Runs every arm as a REAL child process with the batch's OWN isolated interpreter and captures
the RAW process exit code (never inferred, never masked by a wrapper).

Recovered B-unit argv (see <ATTEMPT>/evidence/batch_invocations.json key "M13" +
<PLAN>/execution_runs/M13/a20260919-01/scripts/run_product.ps1 + commands.json B-product-run):

  powershell -NoProfile -ExecutionPolicy Bypass -File <attempt>/scripts/run_product.ps1 \
      -AttemptRoot <attempt> -Card M13
  -> python.exe -X utf8 -B <attempt>/scripts/run_card.py \
         --card M13 --attempt <attempt> --code-root <attempt>/iso/checkout_scripts \
         --out <attempt>/evidence/M13/run_result.json \
         --run-result-out <attempt>/evidence/M13/formula_result.json
  -> exit $p.ExitCode        (the runner's rc is propagated, not masked)

Every path is redirected into this batch's own scratch and `-B` is passed everywhere, so no
__pycache__ can appear in a historical dir:

  python.exe -X utf8 -B <batch>/run_card.py|run_card_before.py \
      --card <CARD> --attempt _scratch/M13-M16/<arm> --code-root _scratch/M13-M16/code_root \
      --out _scratch/M13-M16/<arm>/<CARD>/run_result.json \
      --run-result-out _scratch/M13-M16/<arm>/<CARD>/formula_result.json

Start-Process with -RedirectStandardOutput/-RedirectStandardError is exactly the mechanism
run_product.ps1 used: it writes the child's RAW bytes, so stdout.txt/stderr.txt land on the
historical file names with no PowerShell re-encoding and no move-aside dance.

The console here is cp936 (GBK) and this OS still runs Windows PowerShell 5.1, which reads a
-File script as ANSI unless it carries a UTF-8 BOM.  The workspace path contains non-ASCII
characters, so each driver script is written UTF-8-with-BOM and invoked with -File; that keeps
the non-ASCII path inside a correctly-encoded file instead of on a command line.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

CARDS = ("M13", "M14", "M15", "M16")
ARMS = ("E", "F", "B", "G")
NEW_RUNNER = "run_card.py"
OLD_RUNNER = "run_card_before.py"

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = os.path.join(ATTEMPT, "M13-M16")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M13-M16")
HARNESS = os.path.join(SCRATCH, "_harness")
ISO = os.path.join(PLAN, "execution_runs", "M13", "a20260919-01")
PYTHON = os.path.join(ISO, "iso", "venv", "Scripts", "python.exe")


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def q(value):
    """PowerShell single-quoted literal (only ' needs doubling)."""
    return "'" + str(value).replace("'", "''") + "'"


def run_via_driver(driver_name, body):
    """Write a UTF-8-BOM .ps1 driver and run it with -File; return CompletedProcess."""
    path = os.path.join(HARNESS, driver_name)
    with open(path, "w", encoding="utf-8-sig", newline="\r\n") as handle:
        handle.write(body)
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", path],
        capture_output=True, text=True)


def main():
    out = {}
    for arm in ARMS:
        runner = os.path.join(BATCH, NEW_RUNNER if arm in ("E", "F", "G") else OLD_RUNNER)
        arm_dir = os.path.join(SCRATCH, arm)
        results = {}
        for card in CARDS:
            out_dir = os.path.join(arm_dir, card)
            os.makedirs(out_dir, exist_ok=True)
            run_result = os.path.join(out_dir, "run_result.json")
            formula_result = os.path.join(out_dir, "formula_result.json")
            stdout_txt = os.path.join(out_dir, "stdout.txt")
            stderr_txt = os.path.join(out_dir, "stderr.txt")
            argv = [PYTHON, "-X", "utf8", "-B", runner,
                    "--card", card,
                    "--attempt", arm_dir,
                    "--code-root", os.path.join(SCRATCH, "code_root"),
                    "--out", run_result,
                    "--run-result-out", formula_result]
            body = ("$ErrorActionPreference = 'Stop'\r\n"
                    "$p = Start-Process -FilePath %s -ArgumentList @(%s) -WorkingDirectory %s "
                    "-NoNewWindow -Wait -PassThru -RedirectStandardOutput %s "
                    "-RedirectStandardError %s\r\n"
                    "Write-Output ('raw_rc=' + $p.ExitCode)\r\n"
                    "exit $p.ExitCode\r\n"
                    % (q(PYTHON), ", ".join(q(a) for a in argv[1:]), q(arm_dir),
                       q(stdout_txt), q(stderr_txt)))
            proc = run_via_driver("drive_%s_%s.ps1" % (arm, card), body)
            results[card] = {
                "raw_rc": proc.returncode,
                "launcher_stdout": proc.stdout.strip(),
                "launcher_stderr": proc.stderr.strip()[:800],
                "argv": argv,
                "cwd": arm_dir,
                "runner": runner,
                "out_dir": out_dir,
                "run_result_path": run_result,
                "formula_result_path": formula_result,
                "stdout_path": stdout_txt,
                "stderr_path": stderr_txt,
                "run_result_bytes": os.path.getsize(run_result) if os.path.exists(run_result) else None,
                "run_result_sha256": sha256_file(run_result) if os.path.exists(run_result) else None,
                "formula_result_sha256": sha256_file(formula_result) if os.path.exists(formula_result) else None,
                "stdout_bytes": os.path.getsize(stdout_txt) if os.path.exists(stdout_txt) else None,
                "stderr_bytes": os.path.getsize(stderr_txt) if os.path.exists(stderr_txt) else None,
                "runner_sha256": sha256_file(runner),
            }
        out[arm] = results
    out["_meta"] = {
        "python": PYTHON,
        "python_sha256": sha256_file(PYTHON),
        "python_version": subprocess.run([PYTHON, "-c", "import sys;print(sys.version.split()[0])"],
                                         capture_output=True, text=True).stdout.strip(),
        "code_root": os.path.join(SCRATCH, "code_root"),
        "code_root_sha256": {
            name: sha256_file(os.path.join(SCRATCH, "code_root", name))
            for name in ("model_registry.py", "model_extensions.py")},
        "runner_sha256": {NEW_RUNNER: sha256_file(os.path.join(BATCH, NEW_RUNNER)),
                          OLD_RUNNER: sha256_file(os.path.join(BATCH, OLD_RUNNER))},
    }
    sys.stdout.write(json.dumps(out, indent=1, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
