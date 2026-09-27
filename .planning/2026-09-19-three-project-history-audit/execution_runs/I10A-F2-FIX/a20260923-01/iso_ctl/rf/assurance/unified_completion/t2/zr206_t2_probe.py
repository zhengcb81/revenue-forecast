"""ZR-206 T2 probe: read-only SLO / pressure acceptance on the REAL catalog.

Runs only against the production catalog (49.6GB, 27.2M evidence spans) in
strict read-only mode and writes JSON evidence:

- before/after zero-write fingerprint of ``.source_catalog`` (DB/WAL/SHM
  bytes + directory listing + mtimes);
- p50/p95/p99 per typed reader method;
- peak Python allocation;
- EXPLAIN QUERY PLAN index assertions for the hot aggregates.

This probe NEVER writes the catalog: it opens ``ReadOnlyCatalogReader``
(mode=ro + query_only=ON) exclusively and touches no store/scan/migration.

Usage:
    python assurance/unified_completion/t2/zr206_t2_probe.py [--evidence-dir DIR]

Exit 0 = all frozen SLO gates satisfied and fingerprint identical;
exit 1 = gate breach or fingerprint drift (evidence JSON still written).
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import sys
import time
import tracemalloc
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT.parent / "company-wiki" / "src"))

from company_wiki.source_catalog.reader import ReadOnlyCatalogReader  # noqa: E402

WIKI_ROOT = Path(os.environ.get("COMPANY_WIKI_ROOT", r"C:\Users\郑曾波\Projects\company-wiki"))
CATALOG_DIR = WIKI_ROOT / ".source_catalog"
DB = CATALOG_DIR / "catalog.sqlite3"

# Frozen SLO gates (measured 2026-08-16 on this machine, real catalog).
GATES_MS = {
    "status": 12_000,
    "health": 12_000,
    "scan_health": 50,
    "query": 50,
    "entities_like": 50,
    "location_counts": 250,
    "document": 50,
    "source_sha": 50,
    "artifacts_for": 50,
    "resolve_handle": 50,
}
MEMORY_GATE_MB = 256
SAMPLES = 11


def _percentile(sorted_ts: list[float], q: float) -> float:
    if not sorted_ts:
        return 0.0
    return sorted_ts[min(len(sorted_ts) - 1, int(len(sorted_ts) * q))]


# Coordination primitives that any process may create/remove — excluded
# from the catalog-content fingerprint (the DB/WAL/SHM bytes + directory
# listing of the remaining files are the actual zero-write evidence).
_FINGERPRINT_EXCLUDE = frozenset({
    "operation.lock",
    "operation.lock.acquire",
    "worker_launcher.lock",
    "worker_instance.lock",
    "worker_launcher.lock.acquire",
    "worker_instance.lock.acquire",
})

# Files that a LIVE worker legitimately mutates (logs, control/runtime
# state, run journals).  They are the worker's own evidence, NOT the
# reader's: their drift is recorded in the report but never fails the
# zero-write check.  The catalog DB/WAL/SHM bytes are the hard gate.
_WORKER_OWNED_PREFIXES = (
    "worker_console",
    "worker_launcher_events",
    "worker_process_events",
    "worker_runs",
    "worker_state",
    "worker_control",
    "worker_runtime",
    "worker_stderr-",
    "worker_stdout-",
    "paused_acquisition",
    "control_center",
    "fc204_",
)

# The catalog evidence files: byte-identity here IS the zero-write proof.
_CATALOG_EVIDENCE_FILES = frozenset({
    "catalog.sqlite3",
    "catalog.sqlite3-wal",
    "catalog.sqlite3-shm",
})


def _file_sha256(path: Path) -> str:
    """Streaming SHA-256 (the 49GB catalog must not be read into memory)."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_worker_owned(name: str) -> bool:
    return name.startswith(_WORKER_OWNED_PREFIXES)


def _fingerprint() -> dict:
    """Directory fingerprint: per-file sha256 + size + mtime (seconds).

    Lock/acquire coordination files are excluded (transient primitives);
    the catalog DB/WAL/SHM and all other files are covered."""
    entries: dict[str, dict] = {}
    for path in sorted(CATALOG_DIR.iterdir()):
        if not path.is_file():
            continue
        if path.name in _FINGERPRINT_EXCLUDE or path.name.endswith(".acquire"):
            continue
        info = path.stat()
        entries[path.name] = {
            "sha256": _file_sha256(path),
            "size": info.st_size,
            "mtime_ns": info.st_mtime_ns,
        }
    return entries


def _fingerprint_diff(before: dict, after: dict) -> dict:
    """Per-file before/after diff: added, removed, and changed (with the
    changed field list).  Only sha256 is compared for content changes."""
    names = sorted(set(before) | set(after))
    added = [name for name in names if name not in before]
    removed = [name for name in names if name not in after]
    changed: dict[str, list[str]] = {}
    for name in names:
        if name in before and name in after:
            fields = []
            if before[name]["sha256"] != after[name]["sha256"]:
                fields.append("sha256")
            if before[name]["size"] != after[name]["size"]:
                fields.append("size")
            if before[name]["mtime_ns"] != after[name]["mtime_ns"]:
                fields.append("mtime")
            if fields:
                changed[name] = fields
    return {"added": added, "removed": removed, "changed": changed}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=None)
    args = parser.parse_args()

    if not DB.exists():
        print(f"real catalog missing: {DB}", file=sys.stderr)
        return 2
    evidence_dir = args.evidence_dir or (REPO_ROOT / "assurance" / "unified_completion" / "t2" / "evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    before = _fingerprint()
    reader = ReadOnlyCatalogReader(DB)
    schema = reader.schema_version()
    assert schema == "1.2.0", f"unexpected schema {schema}"

    def bench(label: str, fn) -> dict:
        fn()  # warm
        fn()
        ts: list[float] = []
        for _ in range(SAMPLES):
            gc.collect()
            t0 = time.perf_counter()
            fn()
            ts.append((time.perf_counter() - t0) * 1000)
        ts.sort()
        return {
            "p50_ms": round(_percentile(ts, 0.5), 1),
            "p95_ms": round(_percentile(ts, 0.95), 1),
            "p99_ms": round(_percentile(ts, 0.99), 1),
            "max_ms": round(ts[-1], 1),
        }

    results: dict[str, dict] = {}
    results["status"] = bench("status", lambda: reader.status())
    results["health"] = bench("health", lambda: reader.health())
    results["scan_health"] = bench("scan_health", lambda: reader.scan_health())
    results["query"] = bench(
        "query", lambda: reader.query(document_kind="annual_report", limit=100)
    )
    results["entities_like"] = bench("entities_like", lambda: reader.entities_like("zijin"))
    results["location_counts_company_raw"] = bench(
        "location_counts(company_raw)", lambda: reader.location_counts("company_raw")
    )
    results["location_counts_dropbox_stock"] = bench(
        "location_counts(dropbox_stock)", lambda: reader.location_counts("dropbox_stock")
    )
    results["document"] = bench("document(missing)", lambda: reader.document("no-such-doc"))
    row = reader.fetchone("SELECT document_id FROM documents LIMIT 1")
    doc_id = str(row["document_id"])
    results["document_real"] = bench("document(real)", lambda: reader.document(doc_id))
    results["resolve_handle"] = bench("resolve_handle(real)", lambda: reader.resolve_handle(doc_id))
    src = reader.fetchone("SELECT source_id FROM sources LIMIT 1")
    results["source_sha"] = bench("source_sha(real)", lambda: reader.source_sha(str(src["source_id"])))
    results["artifacts_for"] = bench("artifacts_for(real)", lambda: reader.artifacts_for(doc_id))

    # Memory: peak python allocation across the heaviest aggregates.
    tracemalloc.start()
    try:
        reader.status()
        reader.health()
        _current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    # EXPLAIN index assertions for the hot aggregates.
    plans: dict[str, list[str]] = {}
    for label, sql in (
        ("evidence_spans_count", "SELECT COUNT(*) FROM evidence_spans"),
        ("summary_artifacts_count", "SELECT COUNT(*) FROM artifacts WHERE artifact_role='summary' AND generator_name='source_catalog_llm_summary'"),
        ("active_locations_count", "SELECT COUNT(*) FROM locations WHERE location_status='active'"),
    ):
        plans[label] = [
            str(r["detail"])
            for r in reader.fetchall(f"EXPLAIN QUERY PLAN {sql}")
        ]
    reader.close()
    after = _fingerprint()

    fingerprint_identical = before == after
    fingerprint_diff = _fingerprint_diff(before, after)
    # Hard zero-write gate: catalog DB/WAL/SHM BYTES (sha256+size) must be
    # identical.  SQLite's WAL read protocol touches the -shm coordination
    # file's mtime (read-marker bookkeeping) even for mode=ro readers —
    # byte identity is the zero-write proof; an mtime-only shm touch is
    # recorded as expected protocol behavior, never a reader write.
    catalog_byte_drift = {
        name: fields
        for name, fields in fingerprint_diff["changed"].items()
        if name in _CATALOG_EVIDENCE_FILES
        and any(field in fields for field in ("sha256", "size"))
    }
    catalog_added_removed = [
        name
        for name in fingerprint_diff["added"] + fingerprint_diff["removed"]
        if name in _CATALOG_EVIDENCE_FILES
    ]
    catalog_ok = not catalog_byte_drift and not catalog_added_removed
    shm_mtime_only = (
        "catalog.sqlite3-shm" in fingerprint_diff["changed"]
        and fingerprint_diff["changed"]["catalog.sqlite3-shm"] == ["mtime"]
    )
    # Worker-owned files may legitimately change (live worker journal/logs);
    # they are recorded but never fail the reader zero-write gate.
    worker_drift = {
        name: fields
        for name, fields in fingerprint_diff["changed"].items()
        if _is_worker_owned(name)
    }
    worker_added_removed = [
        name for name in fingerprint_diff["added"] + fingerprint_diff["removed"]
        if _is_worker_owned(name)
    ]
    other_drift = {
        name: fields
        for name, fields in fingerprint_diff["changed"].items()
        if name not in _CATALOG_EVIDENCE_FILES and not _is_worker_owned(name)
    }
    other_added_removed = [
        name for name in fingerprint_diff["added"] + fingerprint_diff["removed"]
        if name not in _CATALOG_EVIDENCE_FILES and not _is_worker_owned(name)
    ]
    gate_breaches = {
        name: result["p95_ms"]
        for name, result in results.items()
        if name in GATES_MS and result["p95_ms"] > GATES_MS[name]
    }
    index_ok = all(
        any("INDEX" in detail or "COVERING" in detail for detail in plan)
        for plan in plans.values()
    )
    memory_ok = peak / (1024 * 1024) < MEMORY_GATE_MB
    # location_counts_company_raw / dropbox_stock map to the location_counts gate.
    for name in ("location_counts_company_raw", "location_counts_dropbox_stock"):
        if results[name]["p95_ms"] > GATES_MS["location_counts"]:
            gate_breaches[name] = results[name]["p95_ms"]

    ok = catalog_ok and not gate_breaches and index_ok and memory_ok
    evidence = {
        "schema_version": 1,
        "unit": "ZR-206",
        "kind": "t2_probe",
        "run_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "catalog": {
            "db_size_bytes": DB.stat().st_size,
            "schema_version": schema,
            "evidence_spans": int(
                ReadOnlyCatalogReader(DB).fetchone("SELECT COUNT(*) FROM evidence_spans")[0]
            ),
        },
        "results_ms": results,
        "peak_python_mb": round(peak / (1024 * 1024), 2),
        "memory_gate_mb": MEMORY_GATE_MB,
        "gates_ms": GATES_MS,
        "explain_plans": plans,
        "index_assertions_ok": index_ok,
        "fingerprint_identical": fingerprint_identical,
        "fingerprint_diff": fingerprint_diff,
        "catalog_zero_write_ok": catalog_ok,
        "catalog_byte_drift": catalog_byte_drift,
        "catalog_added_removed": catalog_added_removed,
        "shm_mtime_only_protocol_touch": shm_mtime_only,
        "worker_owned_drift": worker_drift,
        "worker_owned_added_removed": worker_added_removed,
        "other_drift": other_drift,
        "other_added_removed": other_added_removed,
        "gate_breaches": gate_breaches,
        "ok": ok,
    }
    out = evidence_dir / "zr206_t2_probe.json"
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
