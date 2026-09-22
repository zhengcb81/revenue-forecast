"""Run the (frozen) final_integrity_check_v2 boundary tool and capture its raw
stdout/stderr/rc under evidence/r2/ with a given label — r2 namespace only.

Usage: python r2_run_check.py <label> <attempt_root> <src_attempt> <prod_root>
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

label, my, src, prod = sys.argv[1:5]
my_p = Path(my).resolve()
out_dir = my_p / "evidence" / "r2"
out_dir.mkdir(parents=True, exist_ok=True)

tool = my_p / "scratch" / "final_integrity_check_v2.py"
p = subprocess.run(
    [
        r"C:\Miniconda\python.exe",
        str(tool),
        str(my_p),
        src,
        prod,
    ],
    capture_output=True,
    cwd=str(my_p),
    timeout=600,
)
(out_dir / f"{label}.json").write_bytes(p.stdout)
(out_dir / f"{label}.stderr.txt").write_bytes(p.stderr)
(out_dir / f"{label}.rc.txt").write_text(str(p.returncode), encoding="ascii")
sys.stdout.buffer.write(p.stdout[:1500])
print()
print("rc =", p.returncode)
