"""Run the RED->GREEN / mutation-proof matrix and record raw results.

Every run is a fresh pytest process with its own basetemp.  The fixed tree and
the production repos are only ever READ.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso"
FIXED = ISO / "fixed"
MUT = ATTEMPT / "scratch" / "mutants"
# pytest wipes --basetemp; keep it OUTSIDE the attempt so a stale handle can
# never make pytest delete attempt evidence (and so it cannot hang on Windows).
VACUITY_TEMP = Path(os.environ.get("TEMP", "/tmp")) / "b3-vacuity"
PYTHON = r"C:\Miniconda\python.exe"
SUMMARY_RE = re.compile(r"^(?:=+ )?(?:(\d+) failed)?[, ]*(?:(\d+) passed)?.*?in ",
                        re.MULTILINE)

# (run id, tests dir, extra env, purpose)
RUNS = [
    ("CTRL-A-fixed-w05c", FIXED, {}, "after: W05C suite on the fixed bytes"),
    ("CTRL-B-fixed-fc904", FIXED, {}, "after: FC-904 suite on the fixed bytes"),
    ("CTRL-C-prod-w05c", FIXED, {"B3_BYTES": "production"},
     "before-control: W05C suite on UNFIXED production bytes"),
    ("CTRL-D-prod-fc904", FIXED, {"B3_BYTES": "production"},
     "before-control: FC-904 suite on UNFIXED production bytes"),
    ("CTRL-E-prod-w05b", FIXED, {"B3_BYTES": "production"},
     "after: W05B regression on production bytes (REM-12 re-point)"),
    ("CTRL-F-fixed-w05b", FIXED, {"B3_BYTES": "fixed"},
     "after: W05B regression on the fixed bytes"),
    ("M1-rem11", MUT / "M1-rem11-bundle-none-closure", {},
     "mutation: REM-11 reverted -> W05C must go RED"),
    ("M2-rem13", MUT / "M2-rem13-docstring-old-wording", {},
     "mutation: REM-13 reverted -> W05C must go RED"),
    ("M3-rem14", MUT / "M3-rem14-json-misattribution", {},
     "mutation: REM-14 reverted -> W05C must go RED"),
    ("M4a-rem12-stale", MUT / "M4-rem12-stale-iso-binding",
     {"B3_BYTES": "fixed"},
     "mutation: REM-12 reverted -> W05B provenance must go RED"),
    ("M4b-vacuity-stale-iso", ATTEMPT / "scratch" / "vacuity", {},
     "vacuous-evidence proof: the I-05-B iso bytes pass the same 20 tests"),
]

# for the vacuity run, restrict to the 20 untouched carrier tests so the only
# variable is the bound bytes (the B3 provenance class is expected to fail on
# stale bytes and is reported separately)
RUN_EXTRA_ARGS = {
    "M4b-vacuity-stale-iso": ["-k", "TestW05B"],
}


def run_one_vacuity() -> dict:
    """Vacuity proof, two passes in the SAME directory so the probe binds the
    stale bytes before the carrier imports the module.

    pass 1: probe only        -> must PASS (proves the stale bytes are bound)
    pass 2: carrier only (-k) -> must PASS (proves the stale bytes suffice for
                                 20/20, i.e. the original evidence was vacuous)
    """
    tests_dir = ATTEMPT / "scratch" / "vacuity"
    basetemp = ATTEMPT / "scratch" / "runs" / "M4b-vacuity-stale-iso"
    if basetemp.exists():
        import shutil

        shutil.rmtree(basetemp)
    basetemp.mkdir(parents=True)
    env = dict(os.environ)
    env.pop("B3_BYTES", None)
    passes = []
    for pass_id, test_file, extra in (
            ("probe", "tests/test_aaa_provenance_probe.py",
             ["-k", "vacuity_harness or record_bound_bytes"]),
            ("carrier", "tests/test_w05b_verified_artifact_read.py",
             ["-k", "TestW05B"]),
    ):
        pass_temp = VACUITY_TEMP / pass_id
        if pass_temp.exists():
            import shutil

            shutil.rmtree(pass_temp)
        pass_temp.mkdir(parents=True, exist_ok=True)
        argv = [PYTHON, "-X", "utf8", "-B", "-m", "pytest",
                "-p", "no:cacheprovider",
                "--basetemp", str(pass_temp),
                "-q", *extra, test_file]
        proc = subprocess.run(argv, cwd=str(tests_dir), env=env, text=True,
                              encoding="utf-8", capture_output=True, timeout=600)
        tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
        passes.append({"pass": pass_id, "argv": argv,
                       "returncode": proc.returncode, "summary_line": tail})
    bound = tests_dir / "bound_bytes.json"
    return {
        "run_id": "M4b-vacuity-stale-iso",
        "purpose": ("vacuous-evidence proof: the I-05-B iso bytes pass the "
                    "same 20 tests"),
        "cwd": str(tests_dir),
        "argv": [p["argv"] for p in passes],
        "env": {},
        "returncode": max(p["returncode"] for p in passes),
        "summary_line": " | ".join(
            f"{p['pass']}: {p['summary_line']}" for p in passes),
        "failed_nodes": [],
        "error_nodes": [],
        "passes": passes,
        "bound_bytes": (json.loads(bound.read_text(encoding="utf-8"))
                        if bound.is_file() else None),
    }

TEST_FILES = {
    "w05c": "test_w05c_minimal_production.py",
    "fc904": "test_fc904_artifact_selection.py",
    "w05b": "test_w05b_verified_artifact_read.py",
    # mutation-run ids map to the suite whose fix they revert
    "M1-rem11": "test_w05c_minimal_production.py",
    "M2-rem13": "test_w05c_minimal_production.py",
    "M3-rem14": "test_w05c_minimal_production.py",
    "M4a-rem12": "test_w05b_verified_artifact_read.py",
    "M4b": "test_w05b_verified_artifact_read.py",
}


def pick(run_id: str) -> str:
    for key, filename in TEST_FILES.items():
        if key in run_id:
            return filename
    raise SystemExit(f"cannot pick a test file for {run_id}")


def run_one(run_id: str, tests_dir: Path, env_extra: dict, purpose: str) -> dict:
    target = tests_dir / "tests" / pick(run_id)
    basetemp = ATTEMPT / "scratch" / "runs" / run_id
    if basetemp.exists():
        import shutil

        shutil.rmtree(basetemp)
    basetemp.mkdir(parents=True)
    env = dict(os.environ)
    env.pop("B3_BYTES", None)
    env.update(env_extra)
    argv = [PYTHON, "-X", "utf8", "-B", "-m", "pytest",
            "-p", "no:cacheprovider", "--basetemp", str(basetemp),
            "-q", *RUN_EXTRA_ARGS.get(run_id, []), str(target)]
    proc = subprocess.run(argv, cwd=str(tests_dir), env=env, text=True,
                          encoding="utf-8", capture_output=True, timeout=900)
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    failed = sorted(set(re.findall(r"FAILED (\S+)", proc.stdout)))
    errors = sorted(set(re.findall(r"ERROR (\S+)", proc.stdout)))
    return {
        "run_id": run_id,
        "purpose": purpose,
        "cwd": str(tests_dir),
        "argv": argv,
        "env": env_extra,
        "returncode": proc.returncode,
        "summary_line": tail,
        "failed_nodes": failed,
        "error_nodes": errors,
    }


def main() -> int:
    only = sys.argv[1:] or None
    results = []
    for run_id, tests_dir, env_extra, purpose in RUNS:
        if only and run_id not in only:
            continue
        if run_id == "M4b-vacuity-stale-iso":
            record = run_one_vacuity()
        else:
            record = run_one(run_id, tests_dir, env_extra, purpose)
        results.append(record)
        print(f"[{record['returncode']}] {run_id:26s} {record['summary_line']}")
        for node in record["failed_nodes"]:
            print(f"        RED  {node.split('::')[-1]}")
        for node in record["error_nodes"]:
            print(f"        ERR  {node.split('::')[-1]}")
        if record.get("bound_bytes"):
            print(f"        bound bytes: "
                  f"{record['bound_bytes']['bound_sha256'][:8]} (stale="
                  f"{record['bound_bytes']['is_stale']})")
    out = ATTEMPT / "scratch" / "run_matrix.json"
    prior = []
    if out.exists():
        prior = json.loads(out.read_text(encoding="utf-8"))
        prior = [r for r in prior if r["run_id"] not in {x["run_id"] for x in results}]
    out.write_text(json.dumps(prior + results, indent=2), encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
