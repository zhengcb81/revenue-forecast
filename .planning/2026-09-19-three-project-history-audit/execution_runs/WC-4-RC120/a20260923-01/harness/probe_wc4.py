"""WC-4 = F12-RC120 rgm probe (RED/GREEN/MUTATION measurement).

Runs the PRODUCT CLI from a given iso tree under:
  * the F12 fault   : stdout = write end of a pipe whose READ end is closed
                      (same construction as the frozen I-09-C probe_f12.py B arm)
  * two baselines   : A = pipe with a live reader, C = stdout to a regular file
  * a normal matrix : N1 validate-only / N2 invalid JSON / N3 usage error /
                      N4 --version / N5 formal --output+--markdown

Judgement is mechanical against the frozen oracle (oracle.md §2-§4):
  stage=red   -> expect F12 raw rc == 120 (out of domain; defect reproduced)
  stage=green -> expect F12 raw rc == 2   (in domain) + product error text on
                 stderr + no CPython "Exception ignored on flushing sys.stdout"
  stage=mut*  -> expect F12 raw rc == 120 (revert brings the defect back)

The harness only reads Popen.returncode and never rewrites it.  Every write
stays inside the attempt directory (production tree untouched).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "rf"
RGMDIR = ATTEMPT / "evidence" / "rgm"
CLI = ISO / "scripts" / "revenue_forecast.py"

STAGE_EXPECT = {"red": 120, "mut1": 120, "mut2": 120, "green": 2}
FROZEN_DOMAIN = {0, 2}
NORMAL_EXPECT = {
    "N1_validate_only": 0,
    "N2_invalid_json": 2,
    "N3_usage_error": 2,
    "N4_version": 0,
    "N5_formal_output": 0,
}
BASELINE_EXPECT = {"A_pipe_reader": 0, "C_stdout_file": 0}


def child_env(stage: str) -> dict:
    env = dict(os.environ)
    env["REVENUE_PUBLICATION_REGISTRY"] = str(RGMDIR / "registry" / stage)
    return env


def argv_for(kind: str) -> list[str]:
    py = [sys.executable, "-B", str(CLI)]
    if kind == "validate":
        return py + [str(RGMDIR / "input_valid.json"), "--validate-only"]
    return py + ["--version"]


def run_sink(argv: list[str], sink: str, env: dict, stage: str) -> dict:
    outbox = RGMDIR / "stdout" / stage
    outbox.mkdir(parents=True, exist_ok=True)
    if sink == "pipe_noreader":
        r_fd, w_fd = os.pipe()
        proc = subprocess.Popen(
            argv, cwd=str(ISO), env=env, stdout=w_fd,
            stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
        )
        os.close(w_fd)
        os.close(r_fd)  # <-- the F12 fault: no reader
        _, err = proc.communicate(timeout=180)
        return {"raw_returncode": proc.returncode, "stderr": (err or b"").decode("utf-8", "replace")}
    if sink == "pipe_reader":
        proc = subprocess.run(
            argv, cwd=str(ISO), env=env, capture_output=True,
            stdin=subprocess.DEVNULL, timeout=180,
        )
        return {
            "raw_returncode": proc.returncode,
            "stdout": proc.stdout.decode("utf-8", "replace"),
            "stderr": proc.stderr.decode("utf-8", "replace"),
        }
    if sink == "file":
        path = outbox / f"{stage}_stdout.txt"
        with path.open("wb") as handle:
            proc = subprocess.run(
                argv, cwd=str(ISO), env=env, stdout=handle,
                stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, timeout=180,
            )
        return {
            "raw_returncode": proc.returncode,
            "stdout_file": str(path),
            "stderr": (proc.stderr or b"").decode("utf-8", "replace"),
        }
    if sink == "capture":
        proc = subprocess.run(
            argv, cwd=str(ISO), env=env, capture_output=True,
            stdin=subprocess.DEVNULL, timeout=180,
        )
        return {
            "raw_returncode": proc.returncode,
            "stdout": proc.stdout.decode("utf-8", "replace"),
            "stderr": proc.stderr.decode("utf-8", "replace"),
        }
    raise ValueError(sink)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=sorted(STAGE_EXPECT))
    args = parser.parse_args()
    stage = args.stage
    env = child_env(stage)
    outdir = RGMDIR / stage
    outdir.mkdir(parents=True, exist_ok=True)

    # ---- the F12 fault arm (validate-only, stdout pipe with no reader) ----
    f12 = run_sink(argv_for("validate"), "pipe_noreader", env, stage)
    # ---- baselines ----
    base_a = run_sink(argv_for("validate"), "pipe_reader", env, stage)
    base_c = run_sink(argv_for("validate"), "file", env, stage)

    # ---- normal-path matrix ----
    normal = {}
    normal["N1_validate_only"] = run_sink(argv_for("validate"), "capture", env, stage)
    bad = outdir / "bad_input.json"
    bad.write_text("{not json", encoding="utf-8")
    normal["N2_invalid_json"] = run_sink(
        [sys.executable, "-B", str(CLI), str(bad)], "capture", env, stage)
    normal["N3_usage_error"] = run_sink(
        [sys.executable, "-B", str(CLI)], "capture", env, stage)
    normal["N4_version"] = run_sink(
        [sys.executable, "-B", str(CLI), "--version"], "capture", env, stage)
    out_json = outdir / "n5.json"
    out_md = outdir / "n5.md"
    normal["N5_formal_output"] = run_sink(
        [sys.executable, "-B", str(CLI), str(RGMDIR / "input_valid.json"),
         "--output", str(out_json), "--markdown", str(out_md)],
        "capture", env, stage)
    normal["N5_artifacts"] = {
        "json_written": out_json.exists(),
        "markdown_written": out_md.exists(),
        "raw_returncode": normal["N5_formal_output"]["raw_returncode"],
    }

    # ---- mechanical judgement against the frozen oracle ----
    expect_f12 = STAGE_EXPECT[stage]
    stderr = f12.get("stderr", "")
    checks = {
        "f12_raw_rc": f12["raw_returncode"],
        "f12_expected_rc": expect_f12,
        "f12_matches_stage_expectation": f12["raw_returncode"] == expect_f12,
        "f12_in_frozen_domain_0_2": f12["raw_returncode"] in FROZEN_DOMAIN,
        "cpython_exception_ignored_present": "Exception ignored on flushing sys.stdout" in stderr,
        "product_error_text_present": "stdout flush failed" in stderr and "Errno" in stderr,
        "baseline_A_rc": base_a["raw_returncode"],
        "baseline_C_rc": base_c["raw_returncode"],
        "baselines_ok": (
            base_a["raw_returncode"] == BASELINE_EXPECT["A_pipe_reader"]
            and base_c["raw_returncode"] == BASELINE_EXPECT["C_stdout_file"]
        ),
        "normal_ok": all(
            normal[k]["raw_returncode"] == v for k, v in NORMAL_EXPECT.items()
        ),
        "normal_stdout_valid_ok": normal["N1_validate_only"]["stdout"].strip() == "valid",
        "n5_artifacts_ok": (
            normal["N5_artifacts"]["json_written"] and normal["N5_artifacts"]["markdown_written"]
        ),
    }
    if stage == "red":
        verdict_ok = (
            checks["f12_matches_stage_expectation"]
            and checks["cpython_exception_ignored_present"]
            and checks["baselines_ok"] and checks["normal_ok"]
        )
        verdict = "RED_REPRODUCED_OUT_OF_DOMAIN_120" if verdict_ok else "RED_NOT_REPRODUCED"
    elif stage == "green":
        verdict_ok = (
            checks["f12_matches_stage_expectation"]
            and checks["f12_in_frozen_domain_0_2"]
            and checks["product_error_text_present"]
            and not checks["cpython_exception_ignored_present"]
            and checks["baselines_ok"] and checks["normal_ok"]
            and checks["normal_stdout_valid_ok"] and checks["n5_artifacts_ok"]
        )
        verdict = "GREEN_IN_DOMAIN_2_WITH_ERROR_TEXT" if verdict_ok else "GREEN_NOT_MET"
    else:
        verdict_ok = checks["f12_matches_stage_expectation"]
        verdict = f"MUTATION_DETECTED_120_RETURNED_{stage}" if verdict_ok else f"MUTATION_NOT_DETECTED_{stage}"

    payload = {
        "card": "WC-4 = F12-RC120",
        "stage": stage,
        "iso_cli_sha256": __import__("hashlib").sha256(CLI.read_bytes()).hexdigest(),
        "python": sys.version,
        "harness_rewrites_child_rc": False,
        "f12_arm": {"construction": "stdout=pipe write end, read end closed (I-09-C probe_f12 B arm)", **f12},
        "baseline_A_pipe_reader": base_a,
        "baseline_C_stdout_file": base_c,
        "normal_matrix": normal,
        "checks": checks,
        "verdict": verdict,
        "verdict_ok": verdict_ok,
    }
    (outdir / "probe.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "stage": stage, "verdict": verdict, "verdict_ok": verdict_ok, **checks
    }, ensure_ascii=False, indent=2))
    return 0 if verdict_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
