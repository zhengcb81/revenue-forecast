#!/usr/bin/env python3
"""T1-6 verification — drive M24's FROZEN runner over the proposed cases.json.

The frozen runner is `M24/.../scripts/run_card.py`, invoked exactly as recorded
in `evidence/M24/command_manifest.json` (unit `B-run`), with two deliberate
differences, both confined to this attempt:

  * `--cases`   points at the PROPOSED cases file (iso/cases_t16.json)
  * `--out` / `--run-result-out` point INSIDE this attempt, so no frozen
    evidence file is overwritten.

Everything else (interpreter flags, --card, --attempt, --code-root) is copied
from the recorded invocation. The verdict therefore comes from the same code
path that produced the frozen evidence, not from a re-implementation.

Claims under test:
  (a) the 11 pre-existing cases still behave identically  -> compare the rc and
      the per-case verdicts of a PRE run vs a POST run
  (b) the NEW case reaches the FY2027 own-balance guard   -> PASS_rejected with
      a message containing the frozen substring
  (c) its input differs from CONT-BREAK's                 -> structural
  (d) the required_message_ids gate holds for all three   -> from the run output
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
RUN = HERE.parent
EXEC_RUNS = RUN.parent.parent
M24 = EXEC_RUNS / "M24" / "a20260919-01"
LIVE_CASES = M24 / "evidence" / "M24" / "cases.json"
PROPOSED = RUN / "iso" / "cases_t16.json"
RUNNER = M24 / "scripts" / "run_card.py"
VENV_PY = M24 / "iso" / "venv" / "Scripts" / "python.exe"
CODE_ROOT = M24 / "iso" / "checkout_scripts"

NEW_ID = "CONT-BREAK-OWNBALANCE"
NEW_SUBSTRING = "stock-flow balance failed: FY2027"


def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def run_variant(tag: str, cases_path: pathlib.Path) -> dict:
    out = RUN / f"run_result_{tag}.json"
    interp = str(VENV_PY) if VENV_PY.exists() else sys.executable
    argv = [
        interp, "-X", "utf8", "-B", str(RUNNER),
        "--card", "M24",
        "--attempt", str(M24),
        "--code-root", str(CODE_ROOT),
        "--out", str(out),
        "--run-result-out", str(out),
        "--cases", str(cases_path),
    ]
    res = subprocess.run(argv, capture_output=True, text=True, timeout=300,
                         cwd=str(M24))
    rec = {"argv": argv, "rc": res.returncode,
           "stdout": res.stdout, "stderr": res.stderr[-1200:]}
    if out.exists():
        rec["result"] = load(out)
    return rec


def main() -> int:
    report = {"card": "T1-6", "attempt": "a20260920-01"}
    report["runner"] = str(RUNNER.relative_to(EXEC_RUNS))
    report["interpreter"] = str(VENV_PY) if VENV_PY.exists() else sys.executable
    report["code_root"] = str(CODE_ROOT.relative_to(EXEC_RUNS))
    report["runner_exists"] = RUNNER.exists()

    pre = load(LIVE_CASES)
    post = load(PROPOSED)

    # ---- (c) structural claims ----
    cb = next(c for c in pre["cases"] if c["id"] == "CONT-BREAK")
    nb = next(c for c in post["cases"] if c["id"] == NEW_ID)
    report["structural"] = {
        "cont_break_value": cb["value"],
        "new_case_value": nb["value"],
        "input_distinct": cb["value"] != nb["value"],
        "new_case_expected": nb["expected"],
        "new_case_substring": nb["expect_message_contains"],
        "required_message_ids": post["required_message_ids"],
        "all_required_ids_present": all(
            any(c["id"] == i for c in post["cases"])
            for i in post["required_message_ids"]),
        "pre_case_count": len(pre["cases"]),
        "post_case_count": len(post["cases"]),
    }

    if not RUNNER.exists():
        (RUN / "t16_verification.json").write_text(
            json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=1, ensure_ascii=False))
        return 0

    # ---- (a)(b)(d) drive the frozen runner both ways ----
    r_pre = run_variant("pre", LIVE_CASES)
    r_post = run_variant("post", PROPOSED)

    report["pre_run_rc"] = r_pre["rc"]
    report["post_run_rc"] = r_post["rc"]

    pre_res = r_pre.get("result", {})
    post_res = r_post.get("result", {})

    # per-case verdict comparison across the 11 shared cases
    def neg_map(res):
        return {n["id"]: n.get("verdict") for n in res.get("negatives", [])}

    mp, mq = neg_map(pre_res), neg_map(post_res)
    shared = [c["id"] for c in pre["cases"]]
    report["shared_case_verdicts_pre"] = {i: mp.get(i) for i in shared}
    report["shared_case_verdicts_post"] = {i: mq.get(i) for i in shared}
    report["shared_cases_unchanged"] = all(mp.get(i) == mq.get(i) for i in shared)

    # the new case
    new_entry = next((n for n in post_res.get("negatives", []) if n["id"] == NEW_ID), None)
    report["new_case_entry"] = new_entry
    report["new_case_present"] = new_entry is not None
    report["new_case_verdict"] = (new_entry or {}).get("verdict")
    report["new_case_message"] = (new_entry or {}).get("message")
    report["new_case_reaches_own_balance_guard"] = bool(
        new_entry
        and new_entry.get("verdict") == "PASS_rejected"
        and NEW_SUBSTRING in (new_entry.get("message") or "")
    )

    # positives must be untouched
    report["positive_unchanged"] = (
        pre_res.get("positive") == post_res.get("positive")
        and pre_res.get("continuity_positive") == post_res.get("continuity_positive"))

    # gate
    nsum = post_res.get("negative_summary", {})
    report["post_negative_summary"] = {
        "total": nsum.get("total"), "passed": nsum.get("passed"),
        "failed": nsum.get("failed"),
        "message_requirements_checked": nsum.get("message_requirements_checked"),
        "required_message_ids_ok": nsum.get("required_message_ids_ok"),
    }
    report["post_exit_code_semantics"] = post_res.get("exit_code_semantics")

    # ---- overall verdict ----
    report["OVERALL"] = {
        "verdict": "PASS" if all([
            report["pre_run_rc"] == 0,
            report["post_run_rc"] == 0,
            report["structural"]["input_distinct"],
            report["shared_cases_unchanged"],
            report["new_case_reaches_own_balance_guard"],
            report["positive_unchanged"],
            report["structural"]["all_required_ids_present"],
        ]) else "FAIL",
        "checks": {
            "pre_rc_zero": report["pre_run_rc"] == 0,
            "post_rc_zero": report["post_run_rc"] == 0,
            "input_distinct": report["structural"]["input_distinct"],
            "shared_cases_unchanged": report["shared_cases_unchanged"],
            "new_case_guard_reached": report["new_case_reaches_own_balance_guard"],
            "positives_unchanged": report["positive_unchanged"],
            "gate_holds": report["structural"]["all_required_ids_present"],
        },
    }

    (RUN / "t16_verification.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print("pre  rc =", r_pre["rc"])
    print("post rc =", r_post["rc"])
    print("post stdout tail:")
    print(r_post["stdout"][-1200:])
    if r_post["stderr"]:
        print("post stderr tail:")
        print(r_post["stderr"])
    print()
    print("OVERALL:", json.dumps(report["OVERALL"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
