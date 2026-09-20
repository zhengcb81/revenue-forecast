"""I-14-C: reproduce the pytest-side rc=2 mystery with raw child output."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATT = HERE.parent
sys.path.insert(0, str(HERE / "tests"))
import test_i14c_real_exit_redaction as t  # noqa: E402


def main() -> int:
    base = ATT / "after" / "cmd-A3" / "pytest" / "repro-tmp"
    base.mkdir(parents=True, exist_ok=True)
    run_dir = base / "run"
    run_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["I14C_RUN_ROOT"] = str(ATT)
    argv = [
        sys.executable, "-X", "utf8", "-B", str(t.DRIVER),
        "--scenario", "token-in-message",
        "--run-dir", str(run_dir),
        "--src", str(t.PRODUCT_SRC),
        "--tests-dir", str(t.PRODUCT_TESTS),
        "--cli-exit",
    ]
    print("argv=", argv)
    proc = subprocess.run(argv, cwd=str(run_dir), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    print("returncode=", proc.returncode)
    print("stdout=", proc.stdout.decode("utf-8", "replace")[:2000])
    print("stderr=", proc.stderr.decode("utf-8", "replace")[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
