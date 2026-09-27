"""WC-4 = F12-RC120 round-2 probe — reviewer finding F-01.

r1's fix wrapped only the *return value* of ``main()``::

    raise SystemExit(_finalize_exit_status(main()))

but argparse raises ``SystemExit`` from INSIDE ``main()`` (``--help`` / ``-h``
buffer the help text into stdout and then exit 0), so the wrapper was never
reached and the F12 fault still surfaced as raw rc=120 with no product error
text.  This probe measures exactly that path plus the r1 F12 arms and the
normal-path matrix, and judges them mechanically per stage.

Fault construction (unchanged from r1 / I-09-C probe_f12.py B arm):
stdout = write end of a pipe whose READ end is closed; only
``Popen.returncode`` is read, never rewritten.

Outputs go to ``evidence/rgm2/<stage>/`` — a NEW directory, so every r1
byte under ``evidence/rgm/`` stays untouched (append-only discipline).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "rf"
OUTROOT = ATTEMPT / "evidence" / "rgm2"
CLI = ISO / "scripts" / "revenue_forecast.py"
INPUT = ATTEMPT / "evidence" / "rgm" / "input_valid.json"

FROZEN_DOMAIN = {0, 2}
ERROR_TEXT = "stdout flush failed"
CPYTHON_TEXT = "Exception ignored on flushing sys.stdout"

# raw rc expected per arm and per stage
ARM_ORDER = [
    "f01_help_noreader",
    "f01_h_noreader",
    "f12_validate_noreader",
    "f12_version_noreader",
    "usage_noreader",
    "help_reader",
    "h_reader",
    "validate_reader",
    "version_reader",
    "usage_reader",
]
BROKEN = ("f01_help_noreader", "f01_h_noreader", "f12_validate_noreader",
          "f12_version_noreader", "usage_noreader")
READER_NORMAL = ("help_reader", "h_reader", "validate_reader",
                 "version_reader", "usage_reader")

BASE_NORMAL = {
    "usage_noreader": 2,
    "help_reader": 0,
    "h_reader": 0,
    "validate_reader": 0,
    "version_reader": 0,
    "usage_reader": 2,
}
# r1 delivery state, r2 wrapper absent (also = mutation 1, wrapper reverted):
# r1 already normalized the return-value arms to 2, only the argparse
# SystemExit path (F-01) is still out of domain at raw 120.
RED_EXPECT = dict(BASE_NORMAL, f01_help_noreader=120, f01_h_noreader=120,
                  f12_validate_noreader=2, f12_version_noreader=2)
GREEN_EXPECT = dict(BASE_NORMAL, f01_help_noreader=2, f01_h_noreader=2,
                    f12_validate_noreader=2, f12_version_noreader=2)
# mutation 2 (r1 oracle M-2): keep the catch, drop the stream neutralization
# -> every broken-pipe arm with buffered content is re-flushed at finalization
NOCATCH_EXPECT = dict(BASE_NORMAL, f01_help_noreader=120, f01_h_noreader=120,
                      f12_validate_noreader=120, f12_version_noreader=120)
# mutation 3 (F-08 supplementary arm): neutralize the stream but never catch
# the failure into rc=2 / product text -> broken-pipe arms fall back to 0
NEUTRALONLY_EXPECT = dict(BASE_NORMAL, f01_help_noreader=0, f01_h_noreader=0,
                          f12_validate_noreader=0, f12_version_noreader=0)

STAGE_EXPECT = {
    "red": RED_EXPECT,
    "green": GREEN_EXPECT,
    "mut1_revertwrap": RED_EXPECT,
    "mut2_nocatch": NOCATCH_EXPECT,
    "mut3_neutralonly": NEUTRALONLY_EXPECT,
}
STAGE_KIND = {
    "red": "red",
    "green": "green",
    "mut1_revertwrap": "mut1",
    "mut2_nocatch": "mut2",
    "mut3_neutralonly": "mut3",
}


def child_env(stage: str) -> dict:
    env = dict(os.environ)
    env["REVENUE_PUBLICATION_REGISTRY"] = str(OUTROOT / "registry" / stage)
    return env


def run_broken(argv: list[str], env: dict) -> dict:
    r_fd, w_fd = os.pipe()
    try:
        proc = subprocess.Popen(
            argv, cwd=str(ISO), env=env, stdout=w_fd,
            stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
        )
    finally:
        os.close(w_fd)
        os.close(r_fd)  # <-- F12/F-01 fault: no reader for the child's stdout
    _, err = proc.communicate(timeout=180)
    return {
        "raw_returncode": proc.returncode,
        "stderr": (err or b"").decode("utf-8", "replace"),
    }


def run_reader(argv: list[str], env: dict) -> dict:
    proc = subprocess.run(
        argv, cwd=str(ISO), env=env, capture_output=True,
        stdin=subprocess.DEVNULL, timeout=180,
    )
    return {
        "raw_returncode": proc.returncode,
        "stdout": proc.stdout.decode("utf-8", "replace"),
        "stderr": proc.stderr.decode("utf-8", "replace"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=sorted(STAGE_EXPECT))
    parser.add_argument("--note", default="")
    args = parser.parse_args()
    stage = args.stage
    expect = STAGE_EXPECT[stage]
    kind = STAGE_KIND[stage]
    env = child_env(stage)
    py = [sys.executable, "-B", str(CLI)]

    arms: dict[str, dict] = {}
    arms["f01_help_noreader"] = run_broken(py + ["--help"], env)
    arms["f01_h_noreader"] = run_broken(py + ["-h"], env)
    arms["f12_validate_noreader"] = run_broken(
        py + [str(INPUT), "--validate-only"], env)
    arms["f12_version_noreader"] = run_broken(py + ["--version"], env)
    arms["usage_noreader"] = run_broken(py, env)
    arms["help_reader"] = run_reader(py + ["--help"], env)
    arms["h_reader"] = run_reader(py + ["-h"], env)
    arms["validate_reader"] = run_reader(
        py + [str(INPUT), "--validate-only"], env)
    arms["version_reader"] = run_reader(py + ["--version"], env)
    arms["usage_reader"] = run_reader(py, env)

    checks: dict = {}
    for name in ARM_ORDER:
        checks[f"{name}.rc"] = arms[name]["raw_returncode"]
        checks[f"{name}.expected_rc"] = expect[name]
        checks[f"{name}.match"] = arms[name]["raw_returncode"] == expect[name]

    help_err = arms["f01_help_noreader"].get("stderr", "")
    checks["f01_help_in_frozen_domain_0_2"] = (
        arms["f01_help_noreader"]["raw_returncode"] in FROZEN_DOMAIN)
    checks["f01_help_product_error_text"] = (
        ERROR_TEXT in help_err and "Errno" in help_err)
    checks["f01_help_cpython_exception_ignored"] = CPYTHON_TEXT in help_err
    checks["all_arms_match_stage_expectation"] = all(
        checks[f"{name}.match"] for name in ARM_ORDER)
    checks["normal_reader_matrix_ok"] = all(
        checks[f"{name}.match"] for name in READER_NORMAL)
    checks["normal_stdout_shapes_ok"] = (
        arms["help_reader"]["stdout"].lstrip().startswith("usage:")
        and arms["h_reader"]["stdout"].lstrip().startswith("usage:")
        and arms["validate_reader"]["stdout"].strip() == "valid"
        and arms["version_reader"]["stdout"].startswith("revenue-forecast ")
        and "usage:" in arms["usage_reader"]["stderr"]
    )

    if kind == "red":
        verdict_ok = (
            checks["all_arms_match_stage_expectation"]
            and checks["f01_help_cpython_exception_ignored"]
            and not checks["f01_help_product_error_text"]
            and not checks["f01_help_in_frozen_domain_0_2"]
            and checks["normal_reader_matrix_ok"]
        )
        verdict = ("RED_F01_HELP_STILL_RAW_120_NO_PRODUCT_TEXT"
                   if verdict_ok else "RED_NOT_REPRODUCED")
    elif kind == "green":
        verdict_ok = (
            checks["all_arms_match_stage_expectation"]
            and checks["f01_help_in_frozen_domain_0_2"]
            and checks["f01_help_product_error_text"]
            and not checks["f01_help_cpython_exception_ignored"]
            and checks["normal_reader_matrix_ok"]
            and checks["normal_stdout_shapes_ok"]
        )
        verdict = ("GREEN_F01_HELP_IN_DOMAIN_2_WITH_ERROR_TEXT"
                   if verdict_ok else "GREEN_NOT_MET")
    elif kind == "mut1":
        verdict_ok = (
            checks["all_arms_match_stage_expectation"]
            and not checks["f01_help_in_frozen_domain_0_2"]
        )
        verdict = ("MUTATION_DETECTED_MUT1_HELP_BACK_TO_120"
                   if verdict_ok else "MUTATION_NOT_DETECTED_MUT1")
    elif kind == "mut2":
        verdict_ok = (
            checks["all_arms_match_stage_expectation"]
            and not checks["f01_help_in_frozen_domain_0_2"]
            and checks["f01_help_product_error_text"]
            and checks["f01_help_cpython_exception_ignored"]
        )
        verdict = ("MUTATION_DETECTED_MUT2_HELP_STILL_120_WITH_TEXT"
                   if verdict_ok else "MUTATION_NOT_DETECTED_MUT2")
    else:  # mut3_neutralonly
        verdict_ok = (
            checks["all_arms_match_stage_expectation"]
            and checks["f01_help_in_frozen_domain_0_2"]
            and not checks["f01_help_product_error_text"]
            and not checks["f01_help_cpython_exception_ignored"]
        )
        verdict = ("MUTATION_DETECTED_MUT3_HELP_0_WITHOUT_ERROR_TEXT_G2_BREACH"
                   if verdict_ok else "MUTATION_NOT_DETECTED_MUT3")

    payload = {
        "card": "WC-4 = F12-RC120",
        "round": "r2",
        "finding": "F-01 (P1): argparse SystemExit raised inside main() bypassed "
                   "_finalize_exit_status",
        "stage": stage,
        "note": args.note,
        "iso_cli_sha256": hashlib.sha256(CLI.read_bytes()).hexdigest(),
        "python": sys.version,
        "harness_rewrites_child_rc": False,
        "fault_construction": "stdout=pipe write end, read end closed",
        "arms": arms,
        "checks": checks,
        "verdict": verdict,
        "verdict_ok": verdict_ok,
    }
    outdir = OUTROOT / stage
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "probe.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "stage": stage, "verdict": verdict, "verdict_ok": verdict_ok,
        "iso_cli_sha256": payload["iso_cli_sha256"][:16],
        **{f"{n}.rc": arms[n]["raw_returncode"] for n in ARM_ORDER},
        "f01_help_product_error_text": checks["f01_help_product_error_text"],
        "f01_help_cpython_exception_ignored":
            checks["f01_help_cpython_exception_ignored"],
        "normal_reader_matrix_ok": checks["normal_reader_matrix_ok"],
        "normal_stdout_shapes_ok": checks["normal_stdout_shapes_ok"],
    }, ensure_ascii=False, indent=2))
    return 0 if verdict_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
