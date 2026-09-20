"""Generate changes.diff for I-06-A (pristine products -> candidate clone).

Also emits, for readability, the two candidate files as +only hunks.
"""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-06-A\a20260919-01"
)
PROD = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
SRC = ATTEMPT / "iso" / "rf"
DST = ATTEMPT / "iso" / "rf_fixed"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    out: list[str] = []
    pairs = [
        (
            PROD / "scripts" / "source_preparation.py",
            DST / "scripts" / "source_preparation.py",
            "a/revenue-forecast/scripts/source_preparation.py",
            "b/revenue-forecast/scripts/source_preparation.py",
        ),
    ]
    for left, right, fromfile, tofile in pairs:
        out.extend(
            difflib.unified_diff(
                left.read_text(encoding="utf-8").splitlines(keepends=True),
                right.read_text(encoding="utf-8").splitlines(keepends=True),
                fromfile=fromfile,
                tofile=tofile,
                n=3,
            )
        )
    for name in ("processing_demand_store.py", "w06a_candidate_patch.py"):
        path = DST / "scripts" / name
        body = path.read_text(encoding="utf-8").splitlines(keepends=True)
        out.append(f"--- /dev/null\n+++ b/revenue-forecast/scripts/{name}\n")
        out.append(f"@@ -0,0 +1,{len(body)} @@\n")
        out.extend("+" + line for line in body)
    diff_path = ATTEMPT / "changes.diff"
    diff_path.write_text("".join(out), encoding="utf-8", newline="\n")

    manifest = {
        "pristine_source_preparation_sha256": sha256_file(
            PROD / "scripts" / "source_preparation.py"
        ),
        "isolated_copy_source_preparation_sha256": sha256_file(
            SRC / "scripts" / "source_preparation.py"
        ),
        "candidate_clone_source_preparation_sha256": sha256_file(
            DST / "scripts" / "source_preparation.py"
        ),
        "candidate_files": {
            name: sha256_file(DST / "scripts" / name)
            for name in ("processing_demand_store.py", "w06a_candidate_patch.py")
        },
        "candidate_source_files_in_attempt": {
            name: sha256_file(ATTEMPT / "iso" / "candidate" / name)
            for name in ("processing_demand_store.py", "w06a_candidate_patch.py")
        },
        "product_repos_modified": False,
    }
    (ATTEMPT / "after" / "changes-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"diff_lines": len(out), **manifest}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
