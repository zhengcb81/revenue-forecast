"""I-14-E-TESTSIDE-R3: build the DELIVERED after/changes.diff = exactly this
card's application (pristine -> fixed bootstrap test), plus a manifest.

Why not harness/make_diff.py's iso-vs-CW diff: after the R1 iso copy the real
company-wiki/tests ADVANCED on three unrelated modules (2 modified, 1 added),
so a raw iso-vs-CW diff conflates external repo drift with this card's change.
That full diff is preserved verbatim as disclosure evidence; the delivered
changes.diff must carry ONLY the application (R1 delivered file_count=1).

Application sides:
  before = before/test_file_original.py  (sha256 32515aa6...c005c1, = the
           product test file's original bytes; also = current real repo bytes)
  after  = iso/tests/contract/test_source_catalog_worker_bootstrap.py
           (the applied green version, sha256 a1cfeb13...67fb0)
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_diff import rewrite  # noqa: E402  (header-rewrite helper, read-only)

ATTEMPT = Path(__file__).resolve().parents[1]
ORIGINAL = ATTEMPT / "before" / "test_file_original.py"
APPLIED = ATTEMPT / "iso" / "tests" / "contract" / "test_source_catalog_worker_bootstrap.py"
REL = "contract/test_source_catalog_worker_bootstrap.py"
OUT_DIFF = ATTEMPT / "after" / "changes.diff"
OUT_MANIFEST = ATTEMPT / "after" / "changes.manifest.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=false", "diff", "--no-index", "--no-color",
         "--no-ext-diff", "--unified=3", "--", str(ORIGINAL), str(APPLIED)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    hunk = rewrite(proc.stdout.decode("utf-8", "replace"), REL, True, True)
    OUT_DIFF.write_text(hunk, encoding="utf-8", newline="")
    raw = OUT_DIFF.read_bytes()
    payload = {
        "card": "I-14-E-TESTSIDE-R3",
        "attempt": "a20260926-01",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "diff_scope": "only company-wiki/tests/**; production repo read-only; "
                      "delivered diff = exactly this card's application",
        "application_source": "before/test_file_original.py -> "
                              "iso/tests/contract/test_source_catalog_worker_bootstrap.py",
        "file_count": 1,
        "files": [{
            "path": f"tests/{REL}",
            "status": "modified",
            "before_bytes": ORIGINAL.stat().st_size,
            "after_bytes": APPLIED.stat().st_size,
            "before_sha256": sha(ORIGINAL),
            "after_sha256": sha(APPLIED),
            "before_is_production_repo": True,
            "before_equals_current_production_repo_bytes": True,
        }],
        "all_paths_under_tests": True,
        "total_added_bytes": max(0, APPLIED.stat().st_size - ORIGINAL.stat().st_size),
        "changes.diff_bytes": len(raw),
        "changes.diff_sha256": hashlib.sha256(raw).hexdigest(),
        "disclosure_repo_drift_not_this_cards_change": {
            "note": "company-wiki/tests advanced AFTER the a20260924-01 iso copy "
                    "on three unrelated modules; those deltas are NOT this card's "
                    "application and are excluded from changes.diff on purpose",
            "full_iso_vs_current_cw_diff": "after/disclosure-iso-vs-cw-full.diff",
            "drift_detail": "after/disclosure-drift.json",
        },
    }
    OUT_MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    print(json.dumps({"files": [f["path"] for f in payload["files"]],
                      "changes.diff_bytes": len(raw),
                      "changes.diff_sha256": payload["changes.diff_sha256"]},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
