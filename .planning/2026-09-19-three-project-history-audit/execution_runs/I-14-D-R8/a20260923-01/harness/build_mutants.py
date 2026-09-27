"""WC-1 / I-14-D-R8: MUTANTS (NINE-STEP step 7/9).

MUT-A = r8_fixed with FIX-1 (REM-06 key predicate) reverted   -> exactly the REM-06
        rows must go red, every R3-05/R5-08 row stays green.
MUT-B = r8_fixed with FIX-2 (F-REV-R3-05 after-break value) reverted -> exactly the
        R3-05 rows (incl. the 2 over-redaction pricing rows) go red, every REM-06
        row stays green.

Inverted edits are the byte-literal pairs recorded by harness/build_r8.py, each
asserted to occur exactly once.  Mutant trees live under %TEMP% (scratch);
judged raw runs go to evidence/mut_*.  Production/sealed trees are never touched.

Run:  python -B harness/build_mutants.py
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ATT = Path(__file__).resolve().parent.parent
SCRATCH = Path(os.environ.get("TEMP", r"C:\Temp")) / "i14dr8_mutants"
OBS_REL = Path("company_wiki") / "source_catalog" / "observability.py"

# import the literal edit pairs from the build script (same attempt)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_r8  # noqa: E402


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def revert(edits: list[tuple[str, str, str]], path: Path, keep: set[str]) -> dict:
    original = path.read_bytes()
    nl = "\r\n" if b"\r\n" in original else "\n"
    text = original.decode("utf-8")
    reverted = []
    for name, old, new in edits:
        if name not in keep:
            continue
        new_t = new.replace("\n", nl)
        old_t = old.replace("\n", nl)
        if text.count(new_t) != 1:
            raise SystemExit(f"mutant anchor failed ({name}) in {path}")
        text = text.replace(new_t, old_t)
        reverted.append(name)
    path.write_bytes(text.encode("utf-8"))
    return {"reverted_edits": reverted, "mutant_sha256": sha(path.read_bytes())}


def make_mutant(name: str, keep_revert: set[str]) -> dict:
    dst = SCRATCH / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(ATT / "iso" / "r8_fixed", dst,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    res = revert(build_r8.PRODUCT_EDITS, dst / OBS_REL, keep_revert)
    res["mutant"] = name
    res["tree"] = str(dst)
    return res


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    report = {
        "scratch_root": str(SCRATCH),
        "MUT-A": make_mutant("MUT-A-revert-REM06", {"const", "func"}),
        "MUT-B": make_mutant("MUT-B-revert-R305", {"auth"}),
    }
    out = ATT / "evidence" / "mutants_build.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
