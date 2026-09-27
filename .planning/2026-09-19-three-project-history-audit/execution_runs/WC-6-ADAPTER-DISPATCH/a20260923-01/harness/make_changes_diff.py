"""WC-6 step 8: changes.diff = unified difflib diff of the iso-fixed product
files against their live-CW pre-image. NO GIT anywhere.

  python make_changes_diff.py

Rules enforced (any violation -> rc 3, no diff written):
  * exactly the expected product files may differ between iso/cw and live CW;
  * every difference is inside src/company_wiki/source_catalog/;
  * live CW itself is never opened for writing (read-only reads only).
"""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

from wc6_common import ATT, CW, EVID, ISO_CW, manifest_paths, sha256_file

#: the two files this card is allowed to change (task: 1-2 files, justified in decision.md)
ALLOWED = (
    "src/company_wiki/source_catalog/adapter_dispatch.py",
    "src/company_wiki/source_catalog/scanner.py",
)


def main() -> int:
    live = manifest_paths(CW)
    iso = manifest_paths(ISO_CW)
    changed = sorted(
        rel for rel in set(live) & set(iso)
        if live[rel]["sha256"] != iso[rel]["sha256"]
    )
    missing_in_iso = sorted(set(live) - set(iso))
    new_in_iso = sorted(set(iso) - set(live))
    extra = sorted(set(changed) - set(ALLOWED))
    ok = not extra and not missing_in_iso and not new_in_iso
    report = {
        "changed_files": changed,
        "expected_files": list(ALLOWED),
        "unexpected_changes": extra,
        "missing_in_iso": missing_in_iso,
        "iso_only_files": new_in_iso,
        "live_hashes": {r: live[r]["sha256"] for r in changed},
        "iso_hashes": {r: iso[r]["sha256"] for r in changed if r in iso},
        "ok": ok,
    }
    (EVID / "changes_diff_manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if not ok:
        print(json.dumps(report, indent=2))
        return 3

    chunks = []
    for rel in ALLOWED:
        a = (CW / rel).read_text(encoding="utf-8").splitlines(keepends=True)
        b = (ISO_CW / rel).read_text(encoding="utf-8").splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            a, b,
            fromfile=f"a/{rel}  (live pre-image, sha256 {live[rel]['sha256']})",
            tofile=f"b/{rel}  (iso fixed, sha256 {iso[rel]['sha256']})",
            n=3,
        ))
        if not diff:
            print(json.dumps({"fatal": "no diff produced for allowed file",
                              "file": rel}))
            return 3
        chunks.extend(diff)
    out = ATT / "changes.diff"
    text = "".join(chunks)
    out.write_text(text, encoding="utf-8", newline="")
    print(json.dumps({
        "changes.diff": str(out),
        "bytes": out.stat().st_size,
        "sha256": sha256_file(out),
        "files": list(ALLOWED),
        "added_lines": sum(1 for l in chunks if l.startswith("+") and not l.startswith("+++")),
        "removed_lines": sum(1 for l in chunks if l.startswith("-") and not l.startswith("---")),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
