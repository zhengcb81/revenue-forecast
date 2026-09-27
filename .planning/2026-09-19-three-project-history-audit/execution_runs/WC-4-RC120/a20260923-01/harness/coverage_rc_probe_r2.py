"""F-02 evidence: which coverage step returns which raw rc.

commands.md P1 row Q3 records raw rc=0 for the coverage-subset command, while
evidence/rgm/coverage_subset_fixed.txt ends with
    Coverage failure: total of 73 is less than fail-under=84
This script reproduces, on a throwaway module inside the attempt directory,
what `coverage run` and `coverage report` each return when the measured total
is below the repository's .coveragerc fail_under=84, so the erratum can state
which step the rc=0 belongs to and which step exits non-zero.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
WORK = ATTEMPT / "harness" / "cov_probe_r2"
OUT = ATTEMPT / "evidence" / "rgm2" / "coverage_rc_probe_r2.txt"

RCINI = """[run]
branch = True

[report]
fail_under = 84
show_missing = True
"""

MOD = """def branchy(x):
    if x:
        return 1
    return 0


def never_called(a, b, c, d):
    total = a + b
    if total > 10:
        total -= 1
    for _ in range(3):
        total += c
    while c > 0:
        c -= 1
        total += d
    return total


print(branchy(1))
"""


def run(argv, cwd):
    proc = subprocess.run(argv, cwd=str(cwd), capture_output=True, timeout=300)
    return proc.returncode, ((proc.stdout or b"") + (proc.stderr or b"")).decode(
        "utf-8", "replace")


def main() -> int:
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / ".coveragerc").write_text(RCINI, encoding="utf-8")
    (WORK / "mod.py").write_text(MOD, encoding="utf-8")

    lines = ["# F-02 coverage rc probe (WC-4 r2)", ""]
    rc_run, out_run = run(
        [sys.executable, "-B", "-m", "coverage", "run", "mod.py"], WORK)
    lines += [f"## coverage run -m mod.py (fail_under=84 in .coveragerc)",
              f"raw_rc={rc_run}", out_run, ""]
    rc_rep, out_rep = run(
        [sys.executable, "-B", "-m", "coverage", "report"], WORK)
    lines += ["## coverage report (same .coveragerc, fail_under=84)",
              f"raw_rc={rc_rep}", out_rep, ""]
    rc_rep0, out_rep0 = run(
        [sys.executable, "-B", "-m", "coverage", "report", "--fail-under=0"], WORK)
    lines += ["## coverage report --fail-under=0 (control: same data, no gate)",
              f"raw_rc={rc_rep0}", out_rep0, ""]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"coverage run raw_rc={rc_run}")
    print(f"coverage report (fail_under=84) raw_rc={rc_rep}")
    print(f"coverage report --fail-under=0 raw_rc={rc_rep0}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
