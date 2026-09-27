"""Build changes.diff = EXACTLY the three REST-B-owned files (repo-prefixed a/ b/ headers),
plus refactored/ pinned copies + manifest.json.

Inputs: production originals (READ) and %TEMP% iso_after refactored bytes.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
ISO = Path(r"C:\Users\郑曾波\AppData\Local\Temp\rf-rest-b\iso_after")
A = RF / (".planning/2026-09-19-three-project-history-audit/execution_runs/"
          "RF-RATCHET-REST-B/a20260923-01")
FILES = ["scripts/model_registry.py", "scripts/revenue_core.py",
         "scripts/revenue_publication.py"]


def main() -> None:
    chunks: list[str] = []
    manifest = {"built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "files": []}
    for rel in FILES:
        before = (RF / rel).read_bytes()
        after = (ISO / rel).read_bytes()
        b_lines = before.decode("utf-8").splitlines(keepends=True)
        a_lines = after.decode("utf-8").splitlines(keepends=True)
        diff = difflib.unified_diff(
            b_lines, a_lines,
            fromfile=f"a/{rel}", tofile=f"b/{rel}",
            n=3,
        )
        header = f"diff --git a/{rel} b/{rel}\n"
        body = header + "".join(diff)
        assert body.count("\n") > 3, f"empty diff for {rel}"
        chunks.append(body)
        # pin copies
        dest = A / "refactored" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ISO / rel, dest)
        manifest["files"].append({
            "path": rel,
            "before_sha256": hashlib.sha256(before).hexdigest(),
            "before_bytes": len(before),
            "after_sha256": hashlib.sha256(after).hexdigest(),
            "after_bytes": len(after),
            "diff_hunks": sum(1 for l in body.splitlines() if l.startswith("@@")),
        })
    out = "".join(chunks)
    (A / "changes.diff").write_text(out, encoding="utf-8", newline="\n")
    (A / "refactored" / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    touched = [rel for rel in FILES]
    assert len(touched) == 3
    print(f"changes.diff = {len(out.encode('utf-8'))} B, sections=3")
    for m in manifest["files"]:
        print(f"  {m['path']}: {m['before_sha256'][:12]} -> {m['after_sha256'][:12]} "
              f"hunks={m['diff_hunks']}")


if __name__ == "__main__":
    main()
