"""M01-M04-PROPAGATE unified arm harness — REAL child processes, RAW rc only.

Arms (oracle.md §4, frozen BEFORE this script first ran; PROPAGATION_CONTRACT §5 form
+ owner G1-a/E-F-G-S ruling, OWNER_DECISIONS §18 "A-1 = 1"):
  E  green control : runner NEW (iso/run_card.py), frozen cases.json        expect rc=0
  F  mutation arm  : runner NEW, NEG-CARD `expected` -> "ValueError"        expect rc=3
  B  inertness     : runner OLD (byte copy b5fcc685...), SAME mutated cases  expect rc=0 (measured control)
  G  rc-class arm  : runner NEW, NEG-CARD `expected` key DELETED            expect rc=2 + no_verdict
  S  structural    : runner NEW, ONE extra structurally broken case entry
                     (id N99-EXTRA-STRUCTURAL, usable expected, missing required
                      member `kind`)                                        expect rc=1

All runs are fresh subprocesses. Fixtures are COPIED from the historical
attempt's evidence dir into this attempt only; mutation applies to the copy.
Nothing under execution_runs/M01..M04/ is ever written: -B +
PYTHONDONTWRITEBYTECODE=1, cwd = the arm dir inside THIS attempt.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "M01-M04-PROPAGATE", "a20260922-01")
RUNS = os.path.join(PLAN, "execution_runs")
EVIDENCE = os.path.join(ATTEMPT, "evidence")

CARDS = ("M01", "M02", "M03", "M04")
ARM_ORDER = ("E", "F", "G", "S", "B")
ARM_RUNNER = {"E": "new", "F": "new", "G": "new", "S": "new", "B": "old"}
ARM_VARIANT = {"E": "frozen", "F": "mutated_value", "G": "deleted_key",
               "S": "extra_broken_entry", "B": "mutated_value"}
EXPECTED_RC = {"E": 0, "F": 3, "G": 2, "S": 1, "B": 0}
MUTATED_VALUE = "ValueError"
S_EXTRA_ID = "N99-EXTRA-STRUCTURAL"

HIST_RUNNER_SHA = "b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816"
EXPECTED_REGISTRY_SHA = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"
EXPECTED_EXTENSIONS_SHA = "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def setup(card):
    hist_attempt = os.path.join(RUNS, card, "a20260919-01")
    runners = {"new": os.path.join(ATTEMPT, "iso", "run_card.py"),
               "old": os.path.join(ATTEMPT, "iso", "run_card_before.py")}
    runner_sha = {role: sha256_file(p) for role, p in runners.items()}
    if runner_sha["old"] != HIST_RUNNER_SHA:
        raise SystemExit("before-copy is not the historical runner: %s" % runner_sha["old"])
    code_root = os.path.join(ATTEMPT, "iso", "code_root")
    reg_sha = sha256_file(os.path.join(code_root, "model_registry.py"))
    ext_sha = sha256_file(os.path.join(code_root, "model_extensions.py"))
    if (reg_sha, ext_sha) != (EXPECTED_REGISTRY_SHA, EXPECTED_EXTENSIONS_SHA):
        raise SystemExit("code_root hash mismatch: %s %s" % (reg_sha, ext_sha))
    py = os.path.join(hist_attempt, "iso", "venv", "Scripts", "python.exe")
    py_sha = sha256_file(py)
    frozen_cases = os.path.join(hist_attempt, "evidence", card, "cases.json")
    return {"card": card, "hist_attempt": hist_attempt, "runners": runners,
            "runner_sha256": runner_sha, "code_root": code_root,
            "code_root_sha256": {"model_registry.py": reg_sha,
                                 "model_extensions.py": ext_sha},
            "py": py, "py_sha256": py_sha,
            "frozen_cases": frozen_cases,
            "frozen_cases_sha256": sha256_file(frozen_cases)}


def build_evidence(env, arm_dir, variant):
    """Copy the card's historical evidence (top-level files) into this arm's attempt
    root, then apply this arm's cases.json variant to the COPY."""
    root = os.path.join(arm_dir, "evidence", env["card"])
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    src = os.path.join(env["hist_attempt"], "evidence", env["card"])
    copied = []
    for name in sorted(os.listdir(src)):
        s = os.path.join(src, name)
        if os.path.isfile(s):
            shutil.copyfile(s, os.path.join(root, name))
            copied.append(name)
    info = {"fixture_dir": root, "copied_files": len(copied),
            "frozen_cases_sha256": env["frozen_cases_sha256"],
            "arm_cases_sha256": None, "mutated_case": None,
            "mutated_case_index": None, "structural_extra": None}
    cases_path = os.path.join(root, "cases.json")
    if variant != "frozen":
        doc = json.load(open(cases_path, encoding="utf-8"))
        target, index = None, None
        for i, case in enumerate(doc["cases"]):
            if case.get("expected") == "ModelRegistryError":
                target, index = case, i
                break
        if target is None:
            raise SystemExit("no case with expected=ModelRegistryError")
        info["mutated_case"] = target["id"]
        info["mutated_case_index"] = index
        if variant == "mutated_value":
            target["expected"] = MUTATED_VALUE
        elif variant == "deleted_key":
            del target["expected"]
        elif variant == "extra_broken_entry":
            # oracle.md §4 S: exactly ONE structural fault - an extra case entry
            # missing the required structural member `kind`, with a USABLE
            # `expected` so the declaration precondition does not swallow it
            # (declaration fault -> rc=2; structural fault -> rc=1).
            doc["cases"].append({
                "id": S_EXTRA_ID,
                "expected": "ModelRegistryError",
                "why": "structural arm: entry missing required structural member `kind`",
            })
            info["structural_extra"] = S_EXTRA_ID
        with open(cases_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    info["arm_cases_sha256"] = sha256_file(cases_path)
    return info


def run_one(env, arm):
    role = ARM_RUNNER[arm]
    variant = ARM_VARIANT[arm]
    arm_dir = os.path.join(EVIDENCE, env["card"], arm)
    os.makedirs(arm_dir, exist_ok=True)
    info = build_evidence(env, arm_dir, variant)
    out_path = os.path.join(arm_dir, "out.json")
    if os.path.exists(out_path):
        os.remove(out_path)
    argv = [env["py"], "-X", "utf8", "-B", env["runners"][role],
            "--card", env["card"],
            "--attempt", arm_dir,
            "--code-root", env["code_root"],
            "--out", out_path]
    proc = subprocess.run(argv, cwd=arm_dir, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    stdout_path = os.path.join(arm_dir, "stdout.txt")
    stderr_path = os.path.join(arm_dir, "stderr.txt")
    with open(stdout_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(proc.stdout)
    with open(stderr_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(proc.stderr)
    with open(os.path.join(arm_dir, "rc.txt"), "w", encoding="ascii", newline="\n") as fh:
        fh.write("%d\n" % proc.returncode)

    doc = json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path) else None
    sem = (doc or {}).get("exit_code_semantics") or {}
    ncnt = (doc or {}).get("negative_counts") or {}
    rec = {
        "id": "%s/%s" % (env["card"], arm),
        "card": env["card"], "arm": arm,
        "runner_role": role, "runner_path": env["runners"][role],
        "runner_sha256": env["runner_sha256"][role],
        "cases_variant": variant,
        "mutated_case": info["mutated_case"],
        "mutated_case_index": info["mutated_case_index"],
        "structural_extra": info["structural_extra"],
        "frozen_cases_sha256": info["frozen_cases_sha256"],
        "arm_cases_sha256": info["arm_cases_sha256"],
        "evidence_copied_files": info["copied_files"],
        "fixture_dir": info["fixture_dir"],
        "argv": argv, "cwd": arm_dir,
        "interpreter": env["py"], "interpreter_sha256": env["py_sha256"],
        "env_extra": {"PYTHONDONTWRITEBYTECODE": "1"},
        "expected_rc": EXPECTED_RC[arm],
        "raw_rc": proc.returncode,
        "meets_expectation": proc.returncode == EXPECTED_RC[arm],
        "out_path": out_path,
        "out_written": doc is not None,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "verdict": sem.get("verdict"),
        "exit_code_in_doc": sem.get("exit_code"),
        "no_verdict_reason": (doc or {}).get("no_verdict_reason"),
        "mismatch_ids": sem.get("declared_expectation_mismatch_case_ids"),
        "unusable_ids": sem.get("declaration_unusable_case_ids"),
        "cases_declared_usable": sem.get("cases_json_declared_expectations_usable"),
        "mismatch_count": ncnt.get("declared_expectation_mismatch"),
        "missing_count": ncnt.get("declared_expectation_missing_in_cases_json"),
        "negative_summary": (doc or {}).get("negative_summary"),
        "stderr_tail": proc.stderr[-800:],
        "stdout_tail": proc.stdout[-600:],
    }
    dump_json(os.path.join(arm_dir, "run.json"), rec)
    return rec


def main():
    records = []
    for card in CARDS:
        env = setup(card)
        print("== %s runner_new=%s runner_old=%s py=%s"
              % (card, env["runner_sha256"]["new"][:12], env["runner_sha256"]["old"][:12],
                 env["py_sha256"][:12]), flush=True)
        for arm in ARM_ORDER:
            rec = run_one(env, arm)
            records.append(rec)
            print("  [%s/%s] raw_rc=%s expected=%s verdict=%r mismatch=%s unusable=%s "
                  "missing=%s mutated=%s out=%s"
                  % (rec["card"], arm, rec["raw_rc"], rec["expected_rc"], rec["verdict"],
                     rec["mismatch_ids"], rec["unusable_ids"], rec["missing_count"],
                     rec["mutated_case"], rec["out_written"]), flush=True)
    dump_json(os.path.join(EVIDENCE, "arms_raw.json"), records)

    raw_table = {}
    for rec in records:
        raw_table.setdefault(rec["card"], {})[rec["arm"]] = rec["raw_rc"]
    meets = all(r["meets_expectation"] for r in records)
    commands = {
        "card": "M01-M04-PROPAGATE",
        "attempt": "execution_runs/M01-M04-PROPAGATE/a20260922-01",
        "authority": "OWNER_DECISIONS.md §18 A-1 = 1 (①扩权); expected arms E=0/F=3/G=2/S=1",
        "note": "every entry is a REAL fresh child process; raw_rc is the process exit "
                "code as returned by the OS, recorded SEPARATELY from expected_rc",
        "interpreter_policy": "each card's own historical iso/venv python.exe with "
                              "-X utf8 -B + PYTHONDONTWRITEBYTECODE=1 (proven B5 pattern; "
                              "read-only execution, no __pycache__ anywhere)",
        "code_root": "iso/code_root (read-only copy; registry 9ec65295..., extensions 9939480b...)",
        "setup_commands": [
            {"what": "freeze oracle", "cmd": "write oracle.md (+ evidence/oracle_freeze.json sha/mtime)",
             "before": "any run"},
            {"what": "pre-run manifest", "cmd": "python -B scripts/build_manifest.py <runs> evidence/manifest_before.json",
             "raw_output": "manifest files=7722 bytes=99931221 sha=a03525360a8e8911399114223a28ab4ce9d5464e2d5ecca9cd59adedf9f02751"},
            {"what": "diff", "cmd": "python -B scripts/make_diff.py before/run_card.py iso/run_card.py changes.diff"},
            {"what": "post-run manifest", "cmd": "python -B scripts/build_manifest.py <runs> evidence/manifest_after.json"},
            {"what": "verify", "cmd": "python -B scripts/verify_manifest.py <runs> evidence/manifest_before.json evidence/manifest_after.json evidence/manifest_verification.json"},
        ],
        "runs": records,
        "raw_rc_table": raw_table,
        "expected_rc_per_arm": EXPECTED_RC,
        "all_arms_meet_expectation": meets,
    }
    dump_json(os.path.join(ATTEMPT, "commands.json"), commands)
    print("raw_rc_table:", json.dumps(raw_table))
    print("all_arms_meet_expectation:", meets)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
