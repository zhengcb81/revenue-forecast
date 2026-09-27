"""Archive the reviewed (r1) revisions BEFORE the P1/P2 fix touches them.

Old files are never overwritten in this attempt: every file the reviewer verified
gets a byte-identical copy under harness/archive/ with its sha256 recorded, so the
pre-image of each r2 change is auditable.

Usage:
  <iso-python> -X utf8 -B harness/archive_r1.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
ARCHIVE = HERE / "archive"

FILES = {
    "oracle.r1-post-reviewer-fill.md": "oracle.md",
    "review.r1-post-reviewer-verdict.md": "review.md",
    "binding.r1.json": "binding.json",
    "commands.r1.json": "commands.json",
    "decision.r1.md": "decision.md",
    "handoff.r1.json": "handoff.json",
    "changes.r1.diff": "changes.diff",
    "cases.r1.json": "harness/cases.json",
    "frozen_expectations.r1.json": "harness/frozen_expectations.json",
    "run_cases.r1.py": "harness/run_cases.py",
    "mutate.r1.py": "harness/mutate.py",
    "tolerance_sweep.r1.py": "harness/tolerance_sweep.py",
    "test_i14b_natural_window.r1.py": "harness/tests/test_i14b_natural_window.py",
    "natural_window.after-r1.py": "iso/natural_window.py",
    "natural_window.before-r0.py": "before/natural_window.baseline.py",
    "mutations.r1.json": "evidence/mutations.json",
    "tolerance_sweep.r1.json": "evidence/tolerance_sweep.json",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    records = []
    for copy_name, source_rel in FILES.items():
        source = ATTEMPT / source_rel
        target = ARCHIVE / copy_name
        if not source.is_file():
            records.append({"copy": copy_name, "source": source_rel, "status": "SOURCE_MISSING"})
            continue
        source_hash = sha256(source)
        shutil.copy2(source, target)
        copy_hash = sha256(target)
        records.append({
            "copy": f"harness/archive/{copy_name}",
            "source": source_rel,
            "source_sha256": source_hash,
            "copy_sha256": copy_hash,
            "byte_identical": source_hash == copy_hash,
            "size_bytes": target.stat().st_size,
        })

    doc = {
        "card": "I-14-B",
        "attempt_id": "a20260919-01",
        "purpose": ("pre-image archive of every file the independent reviewer verified, taken BEFORE the "
                    "P1/P2 changes_required fix. r1 = the reviewed revision; r2 = the fixed revision."),
        "archived_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "files": records,
        "all_byte_identical": all(r.get("byte_identical") for r in records if r.get("status") != "SOURCE_MISSING"),
    }
    (ARCHIVE / "MANIFEST.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"archived": len(records),
                      "all_byte_identical": doc["all_byte_identical"]}, indent=2))
    for record in records:
        print(f'{record["copy"]}  <-  {record["source"]}  {record.get("source_sha256", "")[:16]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
