"""I-07-A / a20260919-01 : helpers for the frozen sample matrix evidence.

READ-ONLY with respect to production. Only writes under the attempt directory
(passed in explicitly as --out). Every production open uses a SQLite "mode=ro"
URI and PRAGMA query_only=ON, mirroring the product's own read-only path
(company-wiki/src/company_wiki/source_catalog/store.py:551,556).

Usage:
  python i07a_helpers.py snapshot   --out <dir>   # V0 before / V5 after
  python i07a_helpers.py rehash     --out <dir>   # V1 manifest re-derivation
  python i07a_helpers.py observe    --out <dir>   # V2 read-only catalog observation
  python i07a_helpers.py iso-build  --out <dir>   # V3 isolated cases + config copy
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
FF = Path(r"C:\Users\郑曾波\Projects\filing-fetch")

CATALOG = CW / ".source_catalog" / "catalog.sqlite3"
CW_CONFIG = CW / "config" / "source_catalog.yaml"

MANIFEST = (RF / ".planning" / "2026-09-19-three-project-history-audit"
            / "execution_v2" / "sample_manifest.json")

# Frozen identities, copied from the plan manifest (see oracle.md section 2).
SAMPLES = [
    {
        "id": "CN-ZIJIN-2025",
        "market": "CN",
        "fiscal_year": 2025,
        "company_query": "601899",
        "provider": "cninfo",
        "provider_document_id": "1225023658",
        "raw": CW / "companies" / "\u7d2b\u91d1\u77ff\u4e1a" / "raw" / "financial_reports"
               / "annual"
               / "2026-03-20_cninfo_1225023658_\u7d2b\u91d1\u77ff\u4e1a\u96c6\u56e2\u80a1\u4efd\u6709\u9650\u516c\u53f82025\u5e74\u5e74\u5ea6\u62a5\u544a.pdf",
        "raw_sha256": "01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d",
        "raw_bytes": 79925886,
        "sidecar_sha256": "7f7570fe6565698f1962a9301b5e47dbe76fb3a5e8dfa5663a48fc3793bf20b5",
        "request": RF / "audit_review" / "2026-09-18_real_company_skill_audit"
                   / "requests" / "zijin_2025.json",
        "request_sha256": "08fb9a92ca65b4a2386db6e4ac35a51d7fc15ac24532d8ee74489cae32f31799",
        "original_observation": "raw reusable; review/artifact readiness incomplete",
    },
    {
        "id": "HK-XIAOMI-2025",
        "market": "HK",
        "fiscal_year": 2025,
        "company_query": "1810",
        "provider": "hkexnews",
        "provider_document_id": "12127452",
        "raw": CW / "companies" / "\u5c0f\u7c73\u96c6\u5718\uff0d\uff37" / "raw"
               / "financial_reports" / "annual"
               / "2026-04-28_hkexnews_12127452_2025\u5e74\u5ea6\u5831\u544a.pdf",
        "raw_sha256": "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c",
        "raw_bytes": 4405561,
        "sidecar_sha256": "8228741d299164380bde36a83df1267b59e9b46721bea7d8efee857aeeb8da71",
        "request": RF / "audit_review" / "2026-09-18_real_company_skill_audit"
                   / "requests" / "xiaomi_2025.json",
        "request_sha256": "891b3261c18137bcbd0a6d2ac4bf27b34703fdd7ab348cdc8c118599ce07655c",
        "original_observation": "raw saved; scan/registration failed",
    },
    {
        "id": "US-MSFT-2026",
        "market": "US",
        "fiscal_year": 2026,
        "company_query": "MSFT",
        "provider": "sec",
        "provider_document_id": "0001193125-26-323660",
        "raw": CW / "companies" / "MICROSOFT CORP" / "raw" / "financial_reports" / "annual"
               / "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm",
        "raw_sha256": "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff",
        "raw_bytes": 8585615,
        "sidecar_sha256": "1cbfb1a2ed055fa199806a5d01b96f325396506c472ebfabb80474ec712abb6a",
        "request": RF / "audit_review" / "2026-09-18_real_company_skill_audit"
                   / "requests" / "msft_2026.json",
        "request_sha256": "369f4682efdbe6e96d38cb724a240040d1b46dcf2b29e10a027bd20b077bf64d",
        "original_observation": "raw saved; scan/registration failed",
    },
]

ANCHORS = [
    ("RF/tools/slo_probe.py", RF / "tools" / "slo_probe.py"),
    ("RF/tools/tests/test_slo_probe.py", RF / "tools" / "tests" / "test_slo_probe.py"),
    ("RF/tools/release_readiness.py", RF / "tools" / "release_readiness.py"),
    ("CW/src/company_wiki/source_catalog/store.py",
     CW / "src" / "company_wiki" / "source_catalog" / "store.py"),
    ("CW/src/company_wiki/source_catalog/cli.py",
     CW / "src" / "company_wiki" / "source_catalog" / "cli.py"),
    ("CW/src/company_wiki/source_catalog/config.py",
     CW / "src" / "company_wiki" / "source_catalog" / "config.py"),
    ("CW/config/source_catalog.yaml", CW_CONFIG),
    ("PLAN/execution_v2/card_I-07-A.md",
     RF / ".planning" / "2026-09-19-three-project-history-audit" / "execution_v2"
     / "card_I-07-A.md"),
    ("PLAN/execution_v2/card_I-14-A.md",
     RF / ".planning" / "2026-09-19-three-project-history-audit" / "execution_v2"
     / "card_I-14-A.md"),
    ("PLAN/execution_v2/sample_manifest.json", MANIFEST),
    ("PLAN/audit_report.md",
     RF / ".planning" / "2026-09-19-three-project-history-audit" / "audit_report.md"),
    ("PLAN/implementation_plan.md",
     RF / ".planning" / "2026-09-19-three-project-history-audit" / "implementation_plan.md"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def win_ext(path: Path) -> Path:
    r"""Return a Windows extended-length form of an absolute path.

    The attempt directory is deep and the sample filenames are long, so
    ``shutil.copy2`` (which uses CopyFile2 through _winapi) fails with
    ERROR_PATH_NOT_FOUND (WinError 3) once the destination passes MAX_PATH.
    Python's own file IO tolerates long paths, so only the copy calls needed
    this; the prefix is applied to the absolute path only.
    """
    text = str(path)
    if len(text) < 240:
        return path
    if not path.is_absolute():
        text = str(path.absolute())
    if text.startswith("\\\\?\\"):
        return Path(text)
    if text.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + text[2:])
    return Path("\\\\?\\" + text)


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    return proc.stdout.strip()


def catalog_identity(catalog: Path) -> dict:
    item = catalog.stat()
    return {
        "path": str(catalog),
        "exists": True,
        "bytes": item.st_size,
        "mtime_iso": datetime.fromtimestamp(item.st_mtime).isoformat(),
        "wal_present": (catalog.parent / (catalog.name + "-wal")).exists(),
        "shm_present": (catalog.parent / (catalog.name + "-shm")).exists(),
        "wal_bytes": ((catalog.parent / (catalog.name + "-wal")).stat().st_size
                      if (catalog.parent / (catalog.name + "-wal")).exists() else None),
        "sha256_skipped": "49.7 GB - not hashed (size+mtime+WAL identity is the frozen witness)",
    }


def read_only_connect(catalog: Path) -> sqlite3.Connection:
    con = sqlite3.connect(catalog.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
    con.execute("PRAGMA query_only=ON")
    return con


def cmd_snapshot(args) -> int:
    out = Path(args.out)
    payload = {
        "captured_at_utc": now(),
        "repos": {
            "revenue-forecast": {"path": str(RF), "head": git(RF, "rev-parse", "HEAD"),
                                 "branch": git(RF, "rev-parse", "--abbrev-ref", "HEAD")},
            "company-wiki": {"path": str(CW), "head": git(CW, "rev-parse", "HEAD"),
                             "branch": git(CW, "rev-parse", "--abbrev-ref", "HEAD")},
            "filing-fetch": {"path": str(FF), "head": git(FF, "rev-parse", "HEAD"),
                             "branch": git(FF, "rev-parse", "--abbrev-ref", "HEAD")},
        },
        "porcelain": {
            "revenue-forecast": git(RF, "status", "--porcelain").splitlines(),
            "company-wiki": git(CW, "status", "--porcelain").splitlines(),
            "filing-fetch": git(FF, "status", "--porcelain").splitlines(),
        },
        "porcelain_product_only": {
            "revenue-forecast": git(RF, "status", "--porcelain", "--",
                                    "tools", "scripts", "tests", "assurance",
                                    "e2e", "references", "SKILL.md", "CHANGELOG.md"
                                    ).splitlines(),
            "company-wiki": git(CW, "status", "--porcelain", "--",
                                "src", "config", "scripts", "tests").splitlines(),
            "filing-fetch": git(FF, "status", "--porcelain", "--",
                                "scripts", "src", "tests").splitlines(),
        },
        "catalog": catalog_identity(CATALOG),
        "anchors_sha256": {name: sha256_file(path) for name, path in ANCHORS},
        "anchor_sizes": {name: path.stat().st_size for name, path in ANCHORS},
        "slo_probe_git": {
            "blob_at_head": git(RF, "rev-parse", "HEAD:tools/slo_probe.py"),
            "blob_of_worktree": git(RF, "hash-object", "tools/slo_probe.py"),
        },
    }
    write_json(out / "snapshot.json", payload)
    print(json.dumps({"ok": True, "wrote": str(out / "snapshot.json"),
                      "catalog_bytes": payload["catalog"]["bytes"],
                      "catalog_mtime": payload["catalog"]["mtime_iso"],
                      "rf_head": payload["repos"]["revenue-forecast"]["head"],
                      "cw_head": payload["repos"]["company-wiki"]["head"],
                      "ff_head": payload["repos"]["filing-fetch"]["head"]},
                     ensure_ascii=False, indent=2))
    return 0


def _sidecar_path(raw: Path) -> Path:
    return Path(str(raw) + ".source.json")


def cmd_rehash(args) -> int:
    out = Path(args.out)
    rows = []
    all_match = True
    for s in SAMPLES:
        raw = s["raw"]
        side = _sidecar_path(raw)
        req = s["request"]
        raw_sha = sha256_file(raw) if raw.is_file() else None
        side_sha = sha256_file(side) if side.is_file() else None
        req_sha = sha256_file(req) if req.is_file() else None
        req_data = json.loads(req.read_text(encoding="utf-8")) if req.is_file() else {}
        urn_expected = ("urn:company-wiki:document:sha256:" + (raw_sha or ""))
        urn_from_manifest = ("urn:company-wiki:document:sha256:" + s["raw_sha256"])
        checks = {
            "raw_exists": raw.is_file(),
            "raw_sha256_match": raw_sha == s["raw_sha256"],
            "raw_byte_size_match": (raw.stat().st_size == s["raw_bytes"]) if raw.is_file() else False,
            "sidecar_exists": side.is_file(),
            "sidecar_sha256_match": side_sha == s["sidecar_sha256"],
            "request_exists": req.is_file(),
            "request_sha256_match": req_sha == s["request_sha256"],
            "request_market_match": req_data.get("market") == s["market"],
            "request_fiscal_year_match": req_data.get("fiscal_year") == s["fiscal_year"],
            "request_document_kind_match": req_data.get("document_kind") == "annual_report",
            "request_company_query_match": req_data.get("company_query") == s["company_query"],
            "request_as_of_date_match": req_data.get("as_of_date") == "2026-09-18",
            "request_schema_version": req_data.get("schema_version"),
            "urn_built_from_real_bytes_equals_manifest_urn": urn_expected == urn_from_manifest,
        }
        match = all(bool(v) for k, v in checks.items()
                    if k != "request_schema_version")
        all_match = all_match and match
        rows.append({
            "id": s["id"], "market": s["market"], "fiscal_year": s["fiscal_year"],
            "provider": s["provider"], "provider_document_id": s["provider_document_id"],
            "raw_path": str(raw), "raw_sha256_actual": raw_sha,
            "raw_sha256_manifest": s["raw_sha256"],
            "raw_bytes_actual": raw.stat().st_size if raw.is_file() else None,
            "sidecar_path": str(side), "sidecar_sha256_actual": side_sha,
            "sidecar_sha256_manifest": s["sidecar_sha256"],
            "request_path": str(req), "request_sha256_actual": req_sha,
            "request_sha256_manifest": s["request_sha256"],
            "request_identity": {k: req_data.get(k) for k in
                                 ("market", "fiscal_year", "document_kind",
                                  "company_query", "as_of_date", "schema_version")},
            "document_id_urn": urn_from_manifest,
            "checks": checks, "all_checks_match": match,
            "original_observation": s["original_observation"],
        })
    payload = {"captured_at_utc": now(), "identity_rule": "hash+identity, never filename",
               "all_match": all_match, "samples": rows}
    write_json(out / "rehash.json", payload)
    print(json.dumps({"ok": True, "all_match": all_match,
                      "per_sample": {r["id"]: r["all_checks_match"] for r in rows}},
                     ensure_ascii=False, indent=2))
    return 0 if all_match else 1


OBS_SQL = {
    "documents": "SELECT document_id, primary_source_id, title, source_type, document_kind, "
                 "published_date, source_status, metadata_priority, first_seen_at, last_seen_at "
                 "FROM documents WHERE document_id = ?",
    "sources": "SELECT s.source_id, s.content_sha256, s.byte_size, s.mime_type, s.first_seen_at "
               "FROM sources s WHERE s.content_sha256 = ?",
    "locations": "SELECT location_id, root_id, relative_path, absolute_path, source_id, "
                 "document_id, role, location_status, observed_size, last_seen_run "
                 "FROM locations WHERE document_id = ? OR source_id IN "
                 "(SELECT source_id FROM sources WHERE content_sha256 = ?)",
    "artifacts": "SELECT artifact_id, artifact_role, path, content_sha256, byte_size, "
                 "generator_name, generator_version, status, error, created_at "
                 "FROM artifacts WHERE document_id = ? OR source_id IN "
                 "(SELECT source_id FROM sources WHERE content_sha256 = ?)",
    "evidence_spans": "SELECT COUNT(*) FROM evidence_spans WHERE document_id = ?",
    "document_entities": "SELECT COUNT(*) FROM document_entities WHERE document_id = ?",
}


def _one(con: sqlite3.Connection, sql: str, params: tuple) -> list:
    try:
        cur = con.execute(sql, params)
        cols = [d[0] for d in cur.description] if cur.description else []
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    except sqlite3.Error as exc:      # schema drift must be visible, not hidden
        return [{"__sql_error__": str(exc)}]


def cmd_observe(args) -> int:
    out = Path(args.out)
    before = catalog_identity(CATALOG)
    con = read_only_connect(CATALOG)
    try:
        roots = _one(con, "SELECT root_id, path, kind, priority, last_scanned_at FROM roots "
                          "ORDER BY priority", ())
        counts = {}
        for table in ("documents", "sources", "locations", "artifacts", "evidence_spans",
                      "document_entities", "source_metadata_assertions"):
            try:
                counts[table] = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            except sqlite3.Error as exc:
                counts[table] = f"ERROR: {exc}"
        samples = []
        for s in SAMPLES:
            did = "urn:company-wiki:document:sha256:" + s["raw_sha256"]
            sha = s["raw_sha256"]
            samples.append({
                "id": s["id"],
                "document_id": did,
                "documents": _one(con, OBS_SQL["documents"], (did,)),
                "sources": _one(con, OBS_SQL["sources"], (sha,)),
                "locations": _one(con, OBS_SQL["locations"], (did, sha)),
                "artifacts": _one(con, OBS_SQL["artifacts"], (did, sha)),
                "evidence_spans_count": _one(con, OBS_SQL["evidence_spans"], (did,)),
                "document_entities_count": _one(con, OBS_SQL["document_entities"], (did,)),
            })
        # multi-root same-bytes census: one content hash with >1 distinct root_id
        multi_root = _one(con,
                          "SELECT s.content_sha256, COUNT(DISTINCT l.root_id) AS root_count, "
                          "GROUP_CONCAT(DISTINCT l.root_id) AS roots, COUNT(*) AS loc_count "
                          "FROM sources s JOIN locations l ON l.source_id = s.source_id "
                          "GROUP BY s.content_sha256 HAVING COUNT(DISTINCT l.root_id) > 1 "
                          "ORDER BY root_count DESC, loc_count DESC LIMIT 20", ())
        # same document_id reachable from more than one root
        multi_root_docs = _one(con,
                               "SELECT document_id, COUNT(DISTINCT root_id) AS root_count, "
                               "GROUP_CONCAT(DISTINCT root_id) AS roots FROM locations "
                               "WHERE document_id IS NOT NULL "
                               "GROUP BY document_id HAVING COUNT(DISTINCT root_id) > 1 "
                               "ORDER BY root_count DESC LIMIT 20", ())
        # artifact status distribution for the three frozen documents
        art_status = _one(con,
                          "SELECT status, COUNT(*) AS n FROM artifacts WHERE document_id IN "
                          "(?, ?, ?) GROUP BY status",
                          tuple("urn:company-wiki:document:sha256:" + s["raw_sha256"]
                                for s in SAMPLES))
        # PRAGMA quick_check is deliberately NOT run here: on this 49.7 GB catalog it is a
        # full-file scan (RF/tools/release_readiness.py:61-65 replaces it for exactly that
        # reason, and the I-15-A note records 25.7M rows).  Production access in this card is
        # restricted to indexed point lookups; the no-write witness is (bytes, mtime, WAL)
        # plus the absence of any write statement in this module.
        quick = "not_run_by_design: full-file scan on a 49.7 GB catalog is out of scope for " \
                "this read-only state observation (see oracle.md, I-14-A M4)"
    finally:
        con.close()
    after = catalog_identity(CATALOG)
    payload = {
        "captured_at_utc": now(),
        "read_only": {
            "uri": CATALOG.resolve().as_uri() + "?mode=ro",
            "pragma": "query_only=ON",
            "writes_issued": 0,
        },
        "catalog_before": before,
        "catalog_after": after,
        "catalog_identity_unchanged": (before["bytes"], before["mtime_iso"]) ==
                                      (after["bytes"], after["mtime_iso"]),
        "table_counts": counts,
        "roots": roots,
        "pragma_quick_check": quick,
        "samples": samples,
        "multi_root_same_bytes": multi_root,
        "multi_root_same_document": multi_root_docs,
        "artifact_status_for_frozen_docs": art_status,
    }
    write_json(out / "observe_readonly.json", payload)
    summary = {
        "ok": True,
        "catalog_identity_unchanged": payload["catalog_identity_unchanged"],
        "quick_check": quick,
        "per_sample": {
            s["id"]: {
                "documents_rows": len([r for r in s["documents"] if "__sql_error__" not in r]),
                "sources_rows": len([r for r in s["sources"] if "__sql_error__" not in r]),
                "locations_rows": len([r for r in s["locations"] if "__sql_error__" not in r]),
                "artifacts_rows": len([r for r in s["artifacts"] if "__sql_error__" not in r]),
            } for s in samples},
        "multi_root_same_bytes_hits": len(multi_root),
        "multi_root_same_document_hits": len(multi_root_docs),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


ISO_CASES = {
    "case-01-indexed-quality": {
        "state": "indexed_quality_candidate",
        "state_origin": "live_production_observation",
        "note": "real indexed document observed read-only in the production catalog; "
                "the bytes are copied into the isolated root for reproducibility",
    },
    "case-02-present-unregistered": {
        "state": "present_unregistered",
        "state_origin": "live_production_observation",
        "note": "raw+sidecar exist and hash-match while the catalog has no documents row "
                "for that document_id",
    },
    "case-03-simulated-missing": {
        "state": "simulated_missing",
        "state_origin": "simulated_in_isolation",
        "note": "SIMULATION ONLY. The production original still exists. This case must never "
                "be cited as a real live missing sample (card_I-07-A clause 3).",
    },
}


def cmd_iso_build(args) -> int:
    out = Path(args.out)
    iso = out / "iso"
    root = iso / "catalog_root"
    cases = iso / "cases"
    if root.exists():
        shutil.rmtree(root)
    copied = []
    for s in SAMPLES:
        raw = s["raw"]
        side = _sidecar_path(raw)
        # mirror the production layout exactly: companies/<company>/raw/financial_reports/annual/<file>
        company = raw.parents[3].name
        raw_rel = (Path("companies") / company / "raw" / "financial_reports" / "annual"
                   / raw.name)
        dst_raw = root / raw_rel
        dst_side = dst_raw.parent / (dst_raw.name + ".source.json")
        Path(win_ext(dst_raw.parent)).mkdir(parents=True, exist_ok=True)
        Path(win_ext(dst_side.parent)).mkdir(parents=True, exist_ok=True)
        shutil.copy2(win_ext(raw), win_ext(dst_raw))
        shutil.copy2(win_ext(side), win_ext(dst_side))
        copied.append({
            "id": s["id"],
            "source_path": str(raw),
            "isolated_path": str(dst_raw),
            "source_sha256": s["raw_sha256"],
            "isolated_sha256": sha256_file(win_ext(dst_raw)),
            "sidecar_source_sha256": s["sidecar_sha256"],
            "sidecar_isolated_sha256": sha256_file(win_ext(dst_side)),
            "source_still_present_after_copy": raw.is_file(),
            "source_sha256_after_copy": sha256_file(raw),
        })

    # isolated catalog: minimal schema with ONLY the state rows the three cases need.
    cat_dir = iso / "catalog"
    cat_dir.mkdir(parents=True, exist_ok=True)
    db = cat_dir / "catalog.sqlite3"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    try:
        con.executescript(
            "CREATE TABLE roots (root_id TEXT PRIMARY KEY, path TEXT NOT NULL, "
            "kind TEXT NOT NULL, priority INTEGER NOT NULL);"
            "CREATE TABLE sources (source_id TEXT PRIMARY KEY, content_sha256 TEXT NOT NULL, "
            "byte_size INTEGER NOT NULL, mime_type TEXT NOT NULL);"
            "CREATE TABLE documents (document_id TEXT PRIMARY KEY, primary_source_id TEXT, "
            "title TEXT NOT NULL, source_type TEXT NOT NULL, document_kind TEXT NOT NULL, "
            "source_status TEXT NOT NULL, first_seen_at TEXT NOT NULL);"
            "CREATE TABLE locations (location_id TEXT PRIMARY KEY, root_id TEXT NOT NULL, "
            "relative_path TEXT NOT NULL, absolute_path TEXT NOT NULL, source_id TEXT, "
            "document_id TEXT, role TEXT NOT NULL, location_status TEXT NOT NULL, "
            "UNIQUE(root_id, relative_path));"
            "CREATE TABLE artifacts (artifact_id TEXT PRIMARY KEY, document_id TEXT NOT NULL, "
            "artifact_role TEXT NOT NULL, path TEXT NOT NULL, content_sha256 TEXT NOT NULL, "
            "generator_name TEXT NOT NULL, generator_version TEXT NOT NULL, status TEXT NOT NULL);"
        )
        con.execute("INSERT INTO roots VALUES (?,?,?,?)",
                    ("company_raw", str(root / "companies"), "company_raw", 10))
        # case-01: the CN sample is registered in the isolated catalog.
        cn = SAMPLES[0]
        cn_doc = "urn:company-wiki:document:sha256:" + cn["raw_sha256"]
        con.execute("INSERT INTO sources VALUES (?,?,?,?)",
                    ("src-cn-01", cn["raw_sha256"], cn["raw_bytes"], "application/pdf"))
        con.execute("INSERT INTO documents VALUES (?,?,?,?,?,?,?)",
                    (cn_doc, "src-cn-01",
                     "ZIJIN MINING GROUP 2025 ANNUAL REPORT (isolated copy)",
                     "filing", "annual_report", "active", "2026-09-20T00:00:00+00:00"))
        con.execute("INSERT INTO locations VALUES (?,?,?,?,?,?,?,?)",
                    ("loc-cn-01", "company_raw",
                     "companies/ZIJIN/raw/financial_reports/annual/cn-2025.pdf",
                     str(root / "companies" / "ZIJIN"), "src-cn-01", cn_doc, "primary",
                     "present"))
        con.execute("INSERT INTO artifacts VALUES (?,?,?,?,?,?,?,?)",
                    ("art-cn-01", cn_doc, "normalized",
                     str(cat_dir / "artifacts" / "cn-01.normalized.json"),
                     cn["raw_sha256"], "normalizer", "1.0.0", "valid"))
        # case-03: a document_id that has NO row anywhere (simulated missing).
        con.commit()
        state_counts = {}
        for table in ("roots", "sources", "documents", "locations", "artifacts"):
            state_counts[table] = con.execute(
                f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        con.close()

    case_docs = {
        "case-01-indexed-quality": {
            "sample_ids": ["CN-ZIJIN-2025"],
            "isolated_document_ids": ["urn:company-wiki:document:sha256:" +
                                      SAMPLES[0]["raw_sha256"]],
            "live_observation_ref": "observe_readonly.json",
        },
        "case-02-present-unregistered": {
            "sample_ids": ["HK-XIAOMI-2025", "US-MSFT-2026"],
            "isolated_document_ids": [],
            "live_observation_ref": "observe_readonly.json",
        },
        "case-03-simulated-missing": {
            "sample_ids": [],
            "query_identity": {
                "note": "identity intentionally NOT taken from a real absent file; declared "
                        "as a simulation because every plan sample exists on disk",
                "market": "CN", "document_kind": "annual_report", "fiscal_year": 2019,
                "as_of_date": "2026-09-18", "company_query": "000000",
            },
            "live_observation_ref": None,
        },
    }
    for name, meta in ISO_CASES.items():
        d = cases / name
        d.mkdir(parents=True, exist_ok=True)
        payload = dict(meta)
        payload["case"] = name
        payload["case_dir"] = str(d)
        payload["built_at_utc"] = now()
        payload.update(case_docs[name])
        payload["isolated_catalog"] = str(db)
        payload["isolated_root"] = str(root)
        payload["copied_files"] = copied
        write_json(d / "case.json", payload)

    # config copy with catalog_dir rebound (V4)
    cfg_dir = iso / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    original = CW_CONFIG.read_text(encoding="utf-8")
    rebound = original.replace('catalog_dir: "${PROJECT_ROOT}/.source_catalog"',
                              'catalog_dir: "' + str(cat_dir).replace("\\", "/") + '"')
    if rebound == original:
        print("ERROR: catalog_dir line not found verbatim; refusing to write a blind copy",
              file=sys.stderr)
        return 1
    (cfg_dir / "source_catalog.yaml").write_text(rebound, encoding="utf-8")
    changed = [(a, b) for a, b in zip(original.splitlines(), rebound.splitlines())
               if a != b]
    payload = {
        "built_at_utc": now(),
        "production_config_path": str(CW_CONFIG),
        "production_config_sha256_before": sha256_file(CW_CONFIG),
        "production_config_sha256_after": sha256_file(CW_CONFIG),
        "isolated_config_path": str(cfg_dir / "source_catalog.yaml"),
        "isolated_config_sha256": sha256_file(cfg_dir / "source_catalog.yaml"),
        "changed_lines": changed,
        "changed_line_count": len(changed),
        "catalog_dir_rebound_to": str(cat_dir),
    }
    write_json(iso / "config_rebind.json", payload)
    write_json(iso / "isolated_state.json", {
        "built_at_utc": now(), "isolated_catalog": str(db),
        "table_counts": state_counts, "copied": copied,
    })
    print(json.dumps({
        "ok": True,
        "isolated_root": str(root),
        "isolated_catalog": str(db),
        "table_counts": state_counts,
        "config_changed_line_count": len(changed),
        "production_config_unchanged":
            payload["production_config_sha256_before"] == payload["production_config_sha256_after"],
        "copies_hash_match": all(c["source_sha256"] == c["isolated_sha256"] for c in copied),
        "sources_still_present": all(c["source_still_present_after_copy"] for c in copied),
    }, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="I-07-A helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, fn in (("snapshot", cmd_snapshot), ("rehash", cmd_rehash),
                     ("observe", cmd_observe), ("iso-build", cmd_iso_build)):
        p = sub.add_parser(name)
        p.add_argument("--out", required=True)
        p.set_defaults(fn=fn)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
