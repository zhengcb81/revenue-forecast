"""I-14-E-APPLY: retain v1's %TEMP% basetemp roots (oracle-addendum-C, C4 item 3).

v1's campaign died mid-flight (STATUS_CONTROL_C_EXIT); its per-run basetemps are
still sitting in ``%TEMP%\\i14eapply-*`` where a future same-named arm or an OS
temp cleanup would delete the exact artifacts CF-I14F-X1 requires.  This script
COPY-retains them into the attempt as one ZIP per root plus a per-file manifest
(relative path, executed absolute path + char count, bytes, sha256 <= 1 MiB).

Why ZIP instead of a tree copy: the deep targets exceed MAX_PATH (260) inside
``after/`` (measured 274-308 chars; the first PowerShell ``Copy-Item -Recurse``
attempt died file-by-file with "Could not find a part of the path").  Nothing is
moved or deleted: the %TEMP% originals stay untouched, and v1's arm logs /
bench-*.json are not opened at all.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path

ATT = Path(__file__).resolve().parents[1]
DEST = ATT / "after" / "v1-basetemps"
TEMP = Path(os.environ.get("TEMP", "."))


def sha256_small(path: Path) -> str | None:
    try:
        if path.stat().st_size > 1024 * 1024:
            return None
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    roots = sorted(p for p in TEMP.glob("i14eapply-*") if p.is_dir())
    if not roots:
        print("no %TEMP%/i14eapply-* roots found")
        return 1
    manifest = {"card": "I-14-E-APPLY", "attempt": "a20260921-01",
                "campaign": "v1 (interrupted; retained as disclosed history)",
                "taken_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "note": "copy-retention only; the %TEMP% originals were not modified",
                "roots": []}
    rc = 0
    for root in roots:
        files = [p for p in sorted(root.rglob("*")) if p.is_file()]
        zip_path = DEST / f"{root.name}.zip"
        if zip_path.exists():
            zip_path.unlink()
        entries = []
        zip_errors = []
        total = 0
        longest = ""
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for path in files:
                    rel = str(path.relative_to(root))
                    text = str(path)
                    try:
                        size = path.stat().st_size
                    except OSError:
                        size = None
                    if size:
                        total += size
                    if len(text) > len(longest):
                        longest = text
                    entries.append({"rel": rel, "path": text,
                                    "path_chars": len(text), "bytes": size,
                                    "sha256": sha256_small(path)})
                    try:
                        zf.write(path, rel)
                    except OSError as exc:
                        zip_errors.append(f"{rel}: {type(exc).__name__}: {exc}")
                        rc = 1
        except OSError as exc:
            zip_errors.append(f"ZIP-LEVEL: {type(exc).__name__}: {exc}")
            rc = 1
        entry = {
            "name": root.name, "source": str(root),
            "zip": str(zip_path),
            "zip_bytes": zip_path.stat().st_size if zip_path.exists() else None,
            "source_files": len(files), "source_bytes": total,
            "longest_path": longest, "longest_path_chars": len(longest),
            "zip_errors": zip_errors,
            "key_files": {
                name: any(e["rel"].endswith(name) for e in entries)
                for name in ("worker_launcher_events.jsonl", "worker_launcher.lock",
                             "worker_control.json", "worker_runtime.json",
                             "fake_worker_count.txt")},
            "manifest": entries,
        }
        manifest["roots"].append(entry)
        print(f"{root.name}: files={len(files)} bytes={total} "
              f"longest={len(longest)} zip={zip_path.name} "
              f"zip_bytes={entry['zip_bytes']} errors={len(zip_errors)}", flush=True)
    out = DEST / "v1-basetemp-manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"manifest -> {out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
