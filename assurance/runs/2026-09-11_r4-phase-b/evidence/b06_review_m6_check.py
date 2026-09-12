"""M6 focused check: does the wider targeted set kill the envelope-wiring mutant?

M6: `build_resolution_envelope` keeps the S-13 conflict read but never applies
the identity/period/source gaps (`gaps = [] if handle.capture_ready else ...`).
Runs on the TEMP copy only; reverts and verifies the blob hash afterwards.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

TREE = Path(r"C:\Users\郑曾波\AppData\Local\Temp\b06_review")
REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
RESOLVER = TREE / "src" / "company_wiki" / "source_catalog" / "resolver.py"

OLD = "        gaps = _qualification_gaps(handle)\n"
NEW = (
    '        gaps = [] if getattr(handle, "capture_ready", False) '
    "else _qualification_gaps(handle)\n"
)
SELECTION = (
    "tests/contract/test_r4b06_qualification.py "
    "tests/contract/test_resolution_envelope_fc704.py "
    "tests/contract/test_fc902_bundle_in_resolver.py "
    "tests/contract/test_fc905_receipt_envelope.py "
    "tests/contract/test_zr404_envelope_trace_rationale.py "
    "tests/contract/test_fc1204_complexity_ratchet.py"
)


def blob_hash(path: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(REPO), "hash-object", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def main() -> None:
    pristine = RESOLVER.read_text(encoding="utf-8")
    expected_blob = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD:src/company_wiki/source_catalog/resolver.py"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert blob_hash(RESOLVER) == expected_blob, "temp copy drifted from HEAD before the run"
    assert pristine.count(OLD) == 1, "anchor not unique"
    result: dict[str, object] = {"expected_blob": expected_blob}
    try:
        RESOLVER.write_text(pristine.replace(OLD, NEW, 1), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", *SELECTION.split(), "-q", "-p", "no:cacheprovider"],
            cwd=str(TREE),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        result["mutant"] = {
            "exit": proc.returncode,
            "tail": [ln for ln in (proc.stdout or "").splitlines() if ln.strip()][-2:],
            "verdict": "killed" if proc.returncode != 0 else "SURVIVED",
        }
    finally:
        RESOLVER.write_text(pristine, encoding="utf-8")
    result["restored_blob"] = blob_hash(RESOLVER)
    result["restored_identical"] = result["restored_blob"] == expected_blob
    out = Path(__file__).with_name("b06_review_m6.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
