"""Mirror layout for the I-10-B verifier (verify_i10b.py after) per MODEL-ORACLE-ALIGN
NR-3: script + iso/rf/scripts live under THIS attempt's scratch so verification_*.json
never writes into the I-10-B or MODEL-ORACLE-ALIGN attempts.

Usage: python -X utf8 -B prepare_i10b.py --scripts <tree/scripts> --phase <tag>
Copies <tree/scripts> -> <attempt>/i10b_mirror/iso/rf/scripts (fresh) and returns paths.
The verifier itself lives at <attempt>/i10b_mirror/scripts/verify_i10b.py (copied once
from MODEL-ORACLE-ALIGN's attempt; source sha256 recorded in output).
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
A = RF / (".planning/2026-09-19-three-project-history-audit/execution_runs/"
          "RF-RATCHET-REST-B/a20260923-01")
SRC_VERIFIER = RF / (".planning/2026-09-19-three-project-history-audit/execution_runs/"
                     "MODEL-ORACLE-ALIGN/a20260922-01/scripts/verify_i10b.py")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts", required=True)
    ap.add_argument("--phase", required=True)
    args = ap.parse_args()

    mirror = A / "i10b_mirror"
    (mirror / "scripts").mkdir(parents=True, exist_ok=True)
    dest_verifier = mirror / "scripts" / "verify_i10b.py"
    shutil.copy2(SRC_VERIFIER, dest_verifier)

    iso_scripts = mirror / "iso" / "rf" / "scripts"
    if iso_scripts.exists():
        shutil.rmtree(iso_scripts)
    shutil.copytree(args.scripts, iso_scripts,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    ver_sha = hashlib.sha256(dest_verifier.read_bytes()).hexdigest()
    print(f"verifier sha256={ver_sha} (source {SRC_VERIFIER})")
    print(f"iso scripts from={args.scripts} phase={args.phase}")
    n = sum(1 for _ in iso_scripts.rglob("*.py"))
    print(f"iso scripts py files={n}")


if __name__ == "__main__":
    main()
