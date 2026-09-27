"""Build changes.diff: product pre-image vs iso (post-change), exactly 2 files."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]

PAIRS = [
    (
        Path(r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent\dayu\fins\downloaders\sec_downloader.py"),
        ATTEMPT / "iso" / "dayu_repo" / "dayu" / "fins" / "downloaders" / "sec_downloader.py",
        "dayu-agent/dayu-agent/dayu/fins/downloaders/sec_downloader.py",
    ),
    (
        Path(
            r"C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\dayu_cli_adapter.py"
        ),
        ATTEMPT
        / "iso"
        / "cw_repo"
        / "src"
        / "company_wiki"
        / "source_catalog"
        / "dayu_cli_adapter.py",
        "company-wiki/src/company_wiki/source_catalog/dayu_cli_adapter.py",
    ),
]


def main() -> int:
    chunks = []
    files = []
    for pre, post, label in PAIRS:
        proc = subprocess.run(
            ["git", "-c", "core.quotepath=false", "diff", "--no-index", "--no-color",
             "--", str(pre), str(post)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode not in (0, 1):
            print(proc.stderr, file=sys.stderr)
            return proc.returncode
        # rewrite the path headers to repo-relative a/<label> b/<label>
        rewritten = []
        for line in proc.stdout.splitlines(keepends=True):
            if line.startswith("diff --git "):
                rewritten.append(f"diff --git a/{label} b/{label}\n")
            elif line.startswith("--- "):
                rewritten.append(f"--- a/{label}\n")
            elif line.startswith("+++ "):
                rewritten.append(f"+++ b/{label}\n")
            else:
                rewritten.append(line)
        body = "".join(rewritten)
        if not body.strip():
            print(f"no diff for {label}", file=sys.stderr)
            return 2
        chunks.append(body.rstrip("\n") + "\n")
        files.append(
            {
                "path": label,
                "preimage_sha256": hashlib.sha256(pre.read_bytes()).hexdigest(),
                "preimage_bytes": pre.stat().st_size,
                "post_sha256": hashlib.sha256(post.read_bytes()).hexdigest(),
                "post_bytes": post.stat().st_size,
                "diff_added_lines": sum(
                    1 for line in body.splitlines() if line.startswith("+") and not line.startswith("+++")
                ),
                "diff_removed_lines": sum(
                    1 for line in body.splitlines() if line.startswith("-") and not line.startswith("---")
                ),
            }
        )

    text = "".join(chunks)
    out = ATTEMPT / "changes.diff"
    data = text.encode("utf-8")
    out.write_bytes(data)
    manifest = {
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "files": files,
        "file_count": len(files),
    }
    (ATTEMPT / "results" / "changes_diff_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
