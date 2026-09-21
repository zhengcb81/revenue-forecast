"""I-08-C r3 bookkeeping: archive the exploratory-phase artefacts that survive.

Run BEFORE the r3 pytest evidence run, because that run rewrites
`.pytest_cache/v/cache/*` and the attempt-local `__pycache__/*.pyc`.

Copies verbatim (bytes) plus a manifest with sizes, mtimes and sha256 so the
archive is self-describing and its chain of custody is checkable. Nothing is
deleted or rewritten in place.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

D = Path(__file__).resolve().parent.parent
ARCH = D / "exploratory"

SOURCES = [
    "pytest_cache_v_cache_lastfailed/.pytest_cache/v/cache/lastfailed",
    "pytest_cache_v_cache_nodeids/.pytest_cache/v/cache/nodeids",
    "pytest_cache_CACHEDIR.TAG/.pytest_cache/CACHEDIR.TAG",
    "pytest_cache_README.md/.pytest_cache/README.md",
    "pycache_pytest_pyc/__pycache__/test_i08c_consumer_rejection.cpython-313-pytest-9.1.1.pyc",
    "pycache_plain_pyc/__pycache__/test_i08c_consumer_rejection.cpython-313.pyc",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


records = []
ARCH.mkdir(exist_ok=True)
for spec in SOURCES:
    dest_rel, src_rel = spec.split("/", 1)
    src = D / src_rel
    entry: dict[str, object] = {"source_rel": src_rel, "archive_rel": f"exploratory/{dest_rel}/{Path(src_rel).name}"}
    if not src.exists():
        entry["status"] = "ABSENT_AT_ARCHIVE_TIME"
        records.append(entry)
        continue
    dest = ARCH / dest_rel / Path(src_rel).name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    st_src, st_dst = src.stat(), dest.stat()
    entry.update(
        {
            "status": "ARCHIVED",
            "bytes": st_src.st_size,
            "sha256": sha(src),
            "copy_sha256": sha(dest),
            "copy_is_byte_identical": sha(src) == sha(dest),
            "source_mtime_utc": datetime.fromtimestamp(st_src.st_mtime, timezone.utc).isoformat(),
            "source_mtime_preserved": abs(st_src.st_mtime - st_dst.st_mtime) < 1e-6,
        }
    )
    if src_rel.endswith(".pyc"):
        raw = src.read_bytes()
        import struct

        magic, flags, f1, f2 = struct.unpack("<HIII", raw[:14])
        entry["pyc_header"] = {
            "magic": magic,
            "flags": flags,
            "field1": f1,
            "field2": f2,
            "field1_as_utc": datetime.fromtimestamp(f1, timezone.utc).isoformat(),
            "interpretation": "flags==0 -> (source_mtime, source_size) id; matches the r2 verdict-run source, NOT the exploratory source",
        }
    records.append(entry)

# also write a plain nodeids extract so the r2 node set is readable without the cache
nf = D / ".pytest_cache/v/cache/nodeids"
manifest = {
    "card": "I-08-C",
    "attempt": "a20260919-01",
    "purpose": "preserve every surviving artefact of the exploratory (8/12) and r2-verdict test runs before the r3 run rewrites them",
    "archived_at_utc_container_clock": datetime.now(timezone.utc).isoformat(),
    "archived_before_r3_run": True,
    "records": records,
    "nodeids_r2_verdict_run_count": len(json.loads(nf.read_text(encoding="utf-8"))) if nf.exists() else None,
    "not_recoverable": [
        "the exploratory run's pytest stdout (never written to a file by the implementer of record)",
        "per-test pass/fail detail of the exploratory run (only the prose count '8 passed of 12' survives, in oracle.md revision r2 and in the original handoff.json oracle.provenance)",
        "the exploratory source revision of the test file (replaced in place before the r2 verdict run)",
        "the r2 verdict run's per-node cache entries beyond nodeids/lastfailed (lastfailed was already {} before this round)",
    ],
}
(D / "exploratory_manifest.json").write_text(
    json.dumps(manifest, indent=1, ensure_ascii=True) + "\n", encoding="utf-8"
)
print(json.dumps({r["status"]: 0 for r in records}, indent=1))
for r in records:
    print(r["status"], r.get("bytes"), r.get("sha256"), r["source_rel"])
print("nodeids_count =", manifest["nodeids_r2_verdict_run_count"])
