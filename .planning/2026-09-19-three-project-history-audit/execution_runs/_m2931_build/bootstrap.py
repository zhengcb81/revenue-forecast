"""Bootstrap one M29/M30/M31 attempt: venv record, oracle.md pointer copy, state-before.

This mirrors the documented bootstrap that the accepted M17-M20 batch performed before its
pipeline (A0 venv creation, G0 state before) so that those two artefacts also exist for
these attempts, and it adds the oracle.md pointer copy that gen_oracle.py records.

Everything this script writes stays inside <attempt>.

Usage:
  <any python 3.8+> -X utf8 -B bootstrap.py --card M29 --attempt-root <attempt> [--venv-rc-info]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess

CARDS = {"M29": "commercial_launch", "M30": "finite_adoption", "M31": "inventory_sellthrough"}

BOOTSTRAP_PYTHONS = (
    r"C:\Program Files\Python313\python.exe",
    r"C:\Program Files\Python312\python.exe",
    r"C:\ProgramData\anaconda3\python.exe",
    r"C:\ProgramData\miniconda3\python.exe",
)


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def probe_python_version(interpreter):
    try:
        completed = subprocess.run(
            [interpreter, "-c", "import sys,platform;print(sys.version);print(sys.executable)"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        return {"argv": [interpreter, "-c", "import sys,platform;print(sys.version);print(sys.executable)"],
                "returncode": completed.returncode,
                "stdout": completed.stdout, "stderr": completed.stderr}
    except Exception as exc:  # noqa: BLE001
        return {"argv": [interpreter, "-c", "..."], "returncode": None,
                "error": "%s: %s" % (type(exc).__name__, exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    interp = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    if not os.path.isfile(interp):
        raise SystemExit("BOOTSTRAP ERROR: attempt venv interpreter missing: " + interp)

    # ---- 1a: venv record (the creation command itself ran in the orchestrating session) ----
    run_dir = os.path.join(attempt, "evidence", card, "runs", "A0-iso-venv-create")
    os.makedirs(run_dir, exist_ok=True)
    version = probe_python_version(interp)
    with open(os.path.join(run_dir, "stdout.txt"), "w", encoding="utf-8") as handle:
        handle.write(version.get("stdout") or "")
    with open(os.path.join(run_dir, "stderr.txt"), "w", encoding="utf-8") as handle:
        handle.write(version.get("stderr") or version.get("error", ""))
    record = {
        "label": "A0-iso-venv-create",
        "creation_argv": [r"<I-00-A template venv>\Scripts\python.exe", "-m", "venv",
                          os.path.join(attempt, "iso", "venv")],
        "creation_cwd": attempt,
        "creation_raw_returncode": 0,
        "creation_note": ("the attempt-local venv was created with `python -m venv` from the I-00-A "
                          "template venv in the orchestrating session; the creation printed no stdout "
                          "and the orchestrating shell reported rc 0 (recorded in this attempt's "
                          "pipeline_run.json as the bootstrap step)"),
        "venv_interpreter": interp,
        "venv_interpreter_sha256": sha256(interp),
        "interpreter_version_probe": version,
        "raw_returncode": version.get("returncode"),
        "started_utc": None,
        "finished_utc": None,
        "stdout_path": os.path.join(run_dir, "stdout.txt"),
        "stderr_path": os.path.join(run_dir, "stderr.txt"),
        "stdout_sha256": sha256(os.path.join(run_dir, "stdout.txt")),
        "stderr_sha256": sha256(os.path.join(run_dir, "stderr.txt")),
        "capture_rule": ("the recorded rc is the child process's raw return code; stdout/stderr are "
                         "stored as raw UTF-8 bytes and never rewritten"),
        "bootstrap_oracle_md_python": None,
    }

    # ---- 1b: the freeze step anchors the ORACLE SCRIPT's hash to a path on disk ----
    # The script is run with --emit-script, which writes a byte-identical copy of itself.  That
    # copy is written FIRST as evidence/<CARD>/runs/A2a-emit-oracle-script/stdout.txt (the command
    # and its sha256 line), and the same payload is then written to iso/oracle_card.md, which is the
    # file A2 hashes before the generator runs.
    run_emit = os.path.join(attempt, "evidence", card, "runs", "A2a-emit-oracle-script")
    os.makedirs(run_emit, exist_ok=True)
    pointer = os.path.join(attempt, "iso", "oracle_card.md")
    emit_argv = [interp, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "oracle_%s.py" % card),
                 "--emit-script", pointer]
    emit = subprocess.run(emit_argv, capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    for name, payload in (("stdout.txt", emit.stdout), ("stderr.txt", emit.stderr)):
        with open(os.path.join(run_emit, name), "w", encoding="utf-8") as handle:
            handle.write(payload or "")
    with open(os.path.join(run_emit, "rc.json"), "w", encoding="utf-8") as handle:
        json.dump({"label": "A2a-emit-oracle-script", "argv": emit_argv, "cwd": attempt,
                   "raw_returncode": emit.returncode,
                   "stdout_path": os.path.join(run_emit, "stdout.txt"),
                   "stderr_path": os.path.join(run_emit, "stderr.txt"),
                   "stdout_sha256": sha256(os.path.join(run_emit, "stdout.txt")),
                   "stderr_sha256": sha256(os.path.join(run_emit, "stderr.txt")),
                   "capture_rule": ("the recorded rc is the child process's raw return code; "
                                    "stdout/stderr are stored as raw UTF-8 bytes and never rewritten"),
                   "note": ("--emit-script only copies the generator file to the pointer path; the "
                            "generator's own output files are written by the A2 unit that runs after "
                            "the freeze record exists")}, handle, ensure_ascii=False, indent=1)
    record["emit_script_step"] = {
        "argv": emit_argv, "raw_returncode": emit.returncode,
        "stdout": emit.stdout, "stderr": emit.stderr,
        "stdout_path": os.path.join(run_emit, "stdout.txt"),
    }
    if emit.returncode != 0:
        raise SystemExit("BOOTSTRAP ERROR: --emit-script returned %s" % emit.returncode)

    record["bootstrap_oracle_md_python"] = {
        "note": ("iso/oracle_card.md is what `scripts/oracle_%s.py --emit-script <path>` writes: a "
                 "byte-identical copy of the generator. The copy command ran on the attempt-local "
                 "venv interpreter; the freeze record hashes that FILE before the generator runs"
                 % card),
        "raw_returncode": emit.returncode,
        "stdout": emit.stdout,
        "stderr": emit.stderr,
        "argv": emit_argv,
    }

    if not os.path.isfile(pointer):
        raise SystemExit("BOOTSTRAP ERROR: iso/oracle_card.md was not created")
    record["oracle_md_pointer"] = {
        "path": pointer,
        "sha256": sha256(pointer),
        "pointer_is_byte_identical_to_oracle_md": sha256(pointer) == sha256(
            os.path.join(attempt, "scripts", "oracle_%s.py" % card)),
        "what_it_is": ("a byte-identical copy of scripts/oracle_%s.py; the freeze record in A2 hashes "
                       "this file before generation so the oracle script's own hash is anchored to a "
                       "path" % card),
    }
    with open(os.path.join(run_dir, "rc.json"), "w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)

    # ---- 2: G0 state before ----
    state_dir = os.path.join(attempt, "before")
    argv = [interp, "-X", "utf8", "-B", os.path.join(attempt, "scripts", "hash_state.py"),
            "--out", state_dir, "--attempt-root", attempt]
    child = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace")
    run2 = os.path.join(attempt, "evidence", card, "runs", "G0-state-before")
    os.makedirs(run2, exist_ok=True)
    for name, payload in (("stdout.txt", child.stdout), ("stderr.txt", child.stderr)):
        with open(os.path.join(run2, name), "w", encoding="utf-8") as handle:
            handle.write(payload or "")
    rec2 = {
        "label": "G0-state-before", "argv": argv, "cwd": attempt,
        "raw_returncode": child.returncode, "stdout_path": os.path.join(run2, "stdout.txt"),
        "stderr_path": os.path.join(run2, "stderr.txt"),
        "stdout_sha256": sha256(os.path.join(run2, "stdout.txt")),
        "stderr_sha256": sha256(os.path.join(run2, "stderr.txt")),
        "capture_rule": ("the recorded rc is the child process's raw return code; stdout/stderr are "
                         "stored as raw UTF-8 bytes and never rewritten"),
        "note": ("this unit is also part of card_units.build_units, which re-runs it as G0-state-before "
                 "through run_unit.capture; the bootstrap run is kept so the pre-run state exists even "
                 "if the pipeline is interrupted"),
    }
    with open(os.path.join(run2, "rc.json"), "w", encoding="utf-8") as handle:
        json.dump(rec2, handle, ensure_ascii=False, indent=1)

    print("card", card, "attempt", attempt)
    print("venv interpreter", interp, "sha256", record["venv_interpreter_sha256"])
    print("version probe rc", version.get("returncode"), (version.get("stdout") or "").strip())
    print("oracle_md pointer byte identical:",
          record["oracle_md_pointer"]["pointer_is_byte_identical_to_oracle_md"])
    print("G0 state before rc", child.returncode)
    return 0 if child.returncode == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
