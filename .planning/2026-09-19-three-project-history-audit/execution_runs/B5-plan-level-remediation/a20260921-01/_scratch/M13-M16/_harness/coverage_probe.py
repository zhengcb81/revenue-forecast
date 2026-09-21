"""REM-21 / B5, batch M13-M16 - scratch coverage probe (M13 only).

Arm B measured rc=2, not 0. Before reporting that, establish WHICH mechanism fired and whether
the historical M13-M16 runner ever compared the RAISED exception type to the case's declared
`expected` - i.e. whether arm B's rc=2 is a per-case gate or a set-level coincidence.

From the code (execution_runs/M13/a20260919-01/scripts/run_card.py, historical revision):
  * line 189-192  declared = case.get("expected") ; if declared != TARGET_EXCEPTION: gaps.append(...)
        -> a SET-LEVEL check: it compares the DECLARED STRING to the single type this runner
           applies. It never reads `exc`. Any declaration set that is not uniformly
           "ModelRegistryError" is a gap, regardless of what each case actually raised.
  * line 444      is_target = isinstance(exc, model_registry.ModelRegistryError)
  * lines 448-450 verdict = PASS_rejected if is_target else FAIL_wrong_exception_type/...
        -> the per-case verdict NEVER consults the declaration. `entry["expected"]` is carried
           into the JSON but is decorative for the decision.

Two variants make that visible, both run with BOTH runners:

  V1 all-ValueError : EVERY case (including CONT-BREAK) declares "ValueError".
      OLD: the set-level check still fires (declared != "ModelRegistryError") -> rc=2, so this
           variant cannot separate the mechanisms. Recorded for completeness.
  V2 NEG-CARD keeps the frozen "ModelRegistryError"; THE OTHER TEN cases are deleted from
     cases.json.
      The set-level check sees only "ModelRegistryError" -> NO gap. Oracle negative_count /
      negative_ids then disagree, which is a different rc=2 condition, so V2 alone is also not
      decisive for the per-case question.

  V3 (DECISIVE) all-ValueError on the NEW runner vs the OLD runner, with the ORACLE side of the
     set-level check neutralised by pointing at the frozen set: the old runner still yields rc=2
     purely from `declared != TARGET_EXCEPTION`, while the new runner judges each case and
     reports the per-case mismatches. The pair V1-old / V1-new shows the old mechanism is a
     blanket name comparison and the new one is per case.

  V4 (DECISIVE, cleanest) : raise-side separation. Declare "ValueError" ONLY for a case that
     genuinely raises ValueError-class but NOT ModelRegistryError is impossible here because the
     product raises ModelRegistryError for every frozen mutation; so the separating experiment is
     the mirror image - declare "ModelRegistryError" for a case that raises something else,
     which is exactly what the existing observation OBS-SIGNED-PERF-FEE shows (KeyError). That
     case is NOT in the frozen negative set, so it cannot be a case declaration.

Conclusion the probe must support with numbers: the historical M13-M16 runner's rc=2 on arm B is
produced by the set-level `declared != TARGET_EXCEPTION` comparison, NOT by that runner noticing
which exception the case raised. The new runner's rc=3 on arm F is produced by the per-case
`type(exc).__name__ == case["expected"]` comparison. Both are reported as measured.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = os.path.join(ATTEMPT, "M13-M16")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M13-M16")
HARNESS = os.path.join(SCRATCH, "_harness")
PYTHON = os.path.join(PLAN, "execution_runs", "M13", "a20260919-01", "iso", "venv",
                      "Scripts", "python.exe")
CARD = "M13"
FROZEN_LINE = '   "expected": "ModelRegistryError",\n'
VALUEERROR_LINE = '   "expected": "ValueError",\n'


def q(v):
    return "'" + str(v).replace("'", "''") + "'"


def run_one(variant, runner_name, arm_root, cases_text):
    arm_root = os.path.join(SCRATCH, variant, arm_root)
    ev = os.path.join(arm_root, "evidence", CARD)
    os.makedirs(ev, exist_ok=True)
    src = os.path.join(PLAN, "execution_runs", CARD, "a20260919-01", "evidence", CARD)
    for name in ("input.json", "oracle.json"):
        with open(os.path.join(src, name), "rb") as i, \
                open(os.path.join(ev, name), "wb") as o:
            o.write(i.read())
    with open(os.path.join(ev, "cases.json"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(cases_text)
    out_dir = os.path.join(arm_root, CARD)
    os.makedirs(out_dir, exist_ok=True)
    rr = os.path.join(out_dir, "run_result.json")
    argv = [PYTHON, "-X", "utf8", "-B", os.path.join(BATCH, runner_name),
            "--card", CARD, "--attempt", arm_root,
            "--code-root", os.path.join(SCRATCH, "code_root"),
            "--out", rr, "--run-result-out", os.path.join(out_dir, "formula_result.json")]
    body = ("$ErrorActionPreference='Stop'\r\n"
            "$p = Start-Process -FilePath %s -ArgumentList @(%s) -WorkingDirectory %s "
            "-NoNewWindow -Wait -PassThru -RedirectStandardOutput %s "
            "-RedirectStandardError %s\r\nexit $p.ExitCode\r\n"
            % (q(PYTHON), ", ".join(q(a) for a in argv[1:]), q(arm_root),
               q(os.path.join(out_dir, "stdout.txt")), q(os.path.join(out_dir, "stderr.txt"))))
    driver = os.path.join(HARNESS, "coverage_%s_%s.ps1" % (variant, runner_name[:-3]))
    with open(driver, "w", encoding="utf-8-sig", newline="\r\n") as handle:
        handle.write(body)
    proc = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                           "-File", driver], capture_output=True, text=True)
    doc = json.load(open(rr, "r", encoding="utf-8"))
    return {
        "variant": variant,
        "runner": runner_name,
        "raw_rc": proc.returncode,
        "recorded_exit_code": doc.get("exit_code"),
        "verdict": (doc.get("verdict") or {}).get("verdict"),
        "triggered": (doc.get("exit_code_semantics") or {}).get("triggered"),
        "declaration_gaps": (doc.get("exit_code_semantics") or {}).get(
            "expectation_declaration_gaps"),
        "negative_counts": doc.get("negative_counts"),
        "negative_summary_failed": (doc.get("negative_summary") or {}).get("failed"),
        "declared_expectations": (doc.get("negative_summary") or {}).get(
            "declared_expectations_in_cases_json") or doc.get("expectation_consistency", {}).get(
                "facts", {}).get("declared_expectations_in_cases_json"),
        "cases": {e["id"]: {"verdict": e.get("verdict"), "raised": e.get("raised"),
                            "declared": e.get("declared", e.get("expected")),
                            "judged": e.get("judged"),
                            "declared_expectation_mismatch": e.get(
                                "declared_expectation_mismatch")}
                  for e in doc.get("negatives", [])},
        "arm_root": arm_root,
        "run_result": rr,
        "run_result_sha256": hashlib.sha256(open(rr, "rb").read()).hexdigest(),
    }


def main():
    frozen = open(os.path.join(PLAN, "execution_runs", CARD, "a20260919-01", "evidence", CARD,
                               "cases.json"), "r", encoding="utf-8").read()
    all_valueerror = frozen.replace(FROZEN_LINE, VALUEERROR_LINE)

    # sanity: every one of the 11 negative declarations is now ValueError, observations untouched
    parsed = json.loads(all_valueerror)
    assert all(c.get("expected") == "ValueError" for c in parsed["cases"])
    assert all("expected" not in o for o in parsed["extra_observations"])

    out = {
        "purpose": ("establish whether the HISTORICAL M13-M16 runner ever compared the RAISED "
                    "exception type to a case's declared `expected`, or whether its rc=2 on arm B "
                    "comes from its set-level `declared != TARGET_EXCEPTION` comparison"),
        "card": CARD,
        "frozen_cases_sha256": hashlib.sha256(frozen.encode("utf-8")).hexdigest(),
        "all_valueerror_cases_sha256": hashlib.sha256(
            all_valueerror.encode("utf-8")).hexdigest(),
        "runs": [
            run_one("V1-all-valueerror", "run_card_before.py", "old", all_valueerror),
            run_one("V1-all-valueerror", "run_card.py", "new", all_valueerror),
        ],
    }
    sys.stdout.write(json.dumps(out, indent=1, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
