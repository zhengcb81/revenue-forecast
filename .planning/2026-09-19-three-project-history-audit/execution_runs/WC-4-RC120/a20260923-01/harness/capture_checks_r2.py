"""Capture the WC-4 r2 static checks as UTF-8 evidence files.

Writes (new files only, under evidence/rgm2/):
  ruff_r2.txt     - `ruff check` on the two delivered files (CI-pinned 0.15.18)
  ratchet_r2.txt  - harness/check_ratchet_own_file.py (same algorithm as
                    tools/tests/test_complexity_ratchet.py, frozen max 18)
Both files carry the exact argv and the raw rc.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
ISO = ATTEMPT / "iso" / "rf"
OUT = ATTEMPT / "evidence" / "rgm2"
CLI = ISO / "scripts" / "revenue_forecast.py"
TEST = ISO / "tests" / "test_stdout_flush_exit_domain.py"

CHECKS = [
    ("ruff_r2.txt", [sys.executable, "-m", "ruff", "check", str(CLI), str(TEST)]),
    ("ratchet_r2.txt", [sys.executable, "-B", str(ATTEMPT / "harness" / "check_ratchet_own_file.py")]),
]


def main() -> int:
    # the console code page is GBK while the paths are UTF-8
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    OUT.mkdir(parents=True, exist_ok=True)
    overall = 0
    for name, argv in CHECKS:
        proc = subprocess.run(argv, cwd=str(ISO), capture_output=True, timeout=600)
        out = (proc.stdout or b"").decode("utf-8", "replace")
        err = (proc.stderr or b"").decode("utf-8", "replace")
        (OUT / name).write_text(
            f"# argv: {' '.join(argv)}\n# cwd: {ISO}\n# raw_rc: {proc.returncode}\n\n"
            f"--- stdout ---\n{out}\n--- stderr ---\n{err}",
            encoding="utf-8",
        )
        print(f"{name}: raw_rc={proc.returncode}")
        for line in (out + err).splitlines():
            if line.strip():
                print("   ", line)
        if proc.returncode != 0:
            overall = 1
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
