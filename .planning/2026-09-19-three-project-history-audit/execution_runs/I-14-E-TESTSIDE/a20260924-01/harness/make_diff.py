"""I-14-E-TESTSIDE: build ``after/changes.diff`` (only ``tests/**`` files) plus a
per-file manifest, by diffing the attempt's iso copy against the read-only
production repo.

Neither side is written to: this is a pure read + ``git diff --no-index``.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
RF = ATTEMPT.parents[4]
CW = RF.parent / "company-wiki"
ISO = ATTEMPT / "iso"
OUT_DIFF = ATTEMPT / "after" / "changes.diff"
OUT_MANIFEST = ATTEMPT / "after" / "changes.manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def walk(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(root).parts
        if "__pycache__" in parts or path.suffix in {".pyc", ".pyo"}:
            continue
        out[path.relative_to(root).as_posix()] = path
    return out


def rewrite(hunk: str, rel: str, existed_before: bool, exists_after: bool) -> str:
    left = f"a/tests/{rel}" if existed_before else "/dev/null"
    right = f"b/tests/{rel}" if exists_after else "/dev/null"
    out = []
    for line in hunk.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        eol = line[len(stripped):]
        if stripped.startswith("diff --git "):
            out.append(f"diff --git {left} {right}{eol}")
        elif stripped.startswith("index ") or stripped.startswith("old mode") \
                or stripped.startswith("new mode"):
            continue
        elif stripped.startswith("--- "):
            out.append(f"--- {left}{eol}")
        elif stripped.startswith("+++ "):
            out.append(f"+++ {right}{eol}")
        else:
            out.append(line)
    return "".join(out)


def main() -> int:
    cw_files = walk(CW / "tests")
    iso_files = walk(ISO / "tests")
    rels = sorted(set(cw_files) | set(iso_files))
    changed: list[dict] = []
    hunks: list[str] = []
    for rel in rels:
        before = cw_files.get(rel)
        after = iso_files.get(rel)
        before_sha, after_sha = sha(before) if before else None, sha(after) if after else None
        if before_sha == after_sha:
            continue
        status = ("modified" if before and after
                  else "added" if after else "deleted")
        changed.append({
            "path": f"tests/{rel}",
            "status": status,
            "before_bytes": before.stat().st_size if before else 0,
            "after_bytes": after.stat().st_size if after else 0,
            "before_sha256": before_sha,
            "after_sha256": after_sha,
            "before_is_production_repo": True,
        })
        if before and after:
            proc = subprocess.run(
                ["git", "-c", "core.quotepath=false", "diff", "--no-index",
                 "--no-color", "--no-ext-diff", "--unified=3", "--", str(before), str(after)],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            text = proc.stdout.decode("utf-8", "replace")
            hunks.append(rewrite(text, rel, True, True))
        elif after:  # new file
            lines = after.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            body = "".join(f"+{ln}" if ln.endswith("\n") else f"+{ln}\n" for ln in lines)
            hunk = (f"diff --git a/tests/{rel} b/tests/{rel}\n"
                    f"--- /dev/null\n+++ b/tests/{rel}\n"
                    f"@@ -0,0 +1,{len(lines)} @@\n{body}")
            hunks.append(hunk)
        else:  # deleted
            lines = before.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
            body = "".join(f"-{ln}" if ln.endswith("\n") else f"-{ln}\n" for ln in lines)
            hunk = (f"diff --git a/tests/{rel} b/tests/{rel}\n"
                    f"--- a/tests/{rel}\n+++ /dev/null\n"
                    f"@@ -1,{len(lines)} +0,0 @@\n{body}")
            hunks.append(hunk)

    payload = {
        "card": "I-14-E-TESTSIDE",
        "attempt": "a20260924-01",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "production_repo": str(CW),
        "iso_repo": str(ISO),
        "diff_scope": "only company-wiki/tests/**; production repo read-only",
        "file_count": len(changed),
        "files": changed,
        "all_paths_under_tests": all(f["path"].startswith("tests/") for f in changed),
        "total_added_bytes": sum(max(0, f["after_bytes"] - f["before_bytes"]) for f in changed),
    }
    OUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OUT_MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    diff_text = "".join(hunks)
    OUT_DIFF.write_text(diff_text, encoding="utf-8", newline="")
    raw = OUT_DIFF.read_bytes()
    print(json.dumps({
        "files": [f["path"] for f in changed],
        "all_paths_under_tests": payload["all_paths_under_tests"],
        "changes.diff_bytes": len(raw),
        "changes.diff_sha256": hashlib.sha256(raw).hexdigest(),
        "changes.diff_sha256_16": hashlib.sha256(raw).hexdigest()[:16],
    }, indent=2, ensure_ascii=False))
    print("out:", OUT_DIFF)
    print("out:", OUT_MANIFEST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
