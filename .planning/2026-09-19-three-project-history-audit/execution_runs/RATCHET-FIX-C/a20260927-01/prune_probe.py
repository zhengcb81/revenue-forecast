"""Behavioural probe: run the SAME prune scenario battery against two versions
of prune_retired_evidence.py (pre-image vs post-split) and print a normalized
JSON transcript for diffing.

Usage: python prune_probe.py <path-to-prune-module.py> <fixed-tmp-root>

Windows note: company_wiki's normalizer uses ``multiprocessing spawn``, so the
child re-imports this file as ``__mp_main__``.  Every executable statement
lives in ``main()`` behind the standard guard; module level only defines.
"""
import gzip
import hashlib
import importlib.util
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(REPO / "src"))

import company_wiki.source_catalog as cat  # noqa: E402
from company_wiki.source_catalog.store import retire_document  # noqa: E402

ANNUAL = """\
第一节 释义

释义：本报告使用的术语与定义说明，包括公司与关联方的界定，以及财务指标的计量口径说明。

第三节 公司业务概要

主营业务：公司主要从事半导体设备的研发、生产与销售，产品覆盖刻蚀、薄膜、清洗等关键工艺环节。

第四节 经营情况讨论与分析

经营情况：报告期内公司营业收入稳步增长，主要得益于先进制程设备出货量提升与国产替代进程加速。
"""

NOW = datetime(2026, 9, 27, 12, 0, 0, tzinfo=timezone.utc)
NOW_FRESH = datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
NOW_NAIVE = datetime(2026, 9, 27, 12, 0, 0)
OLD = "2026-01-01T00:00:00+00:00"

SPAN_SQL = ("SELECT e.span_id, e.document_id, e.source_id, e.locator, "
            "e.page_number, e.paragraph_index, e.table_index, e.raw_text, "
            "e.span_json, e.parser_name, e.parser_version, e.parse_status "
            "FROM evidence_spans e ORDER BY e.span_id")

prune = None  # loaded in main()


def load_prune(module_path: Path):
    spec = importlib.util.spec_from_file_location(
        "company_wiki.source_catalog.prune_retired_evidence",
        str(module_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules["company_wiki.source_catalog.prune_retired_evidence"] = module
    spec.loader.exec_module(module)
    return module


def make_catalog(root: Path):
    project = root / "project"
    source_root = root / "sources"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "a.txt").write_text(ANNUAL, encoding="utf-8")
    catalog = cat.SourceCatalog(cat.CatalogConfig(
        project_root=project,
        catalog_dir=project / ".source_catalog",
        roots=(cat.RootSpec("external", source_root, "directory"),),
    ))
    catalog.scan()
    catalog.normalize()
    doc = catalog.store.fetchone("SELECT document_id FROM documents")
    retire_document(catalog.store, document_id=doc["document_id"],
                    reason="probe", created_by="probe")
    return catalog


def span_rows(catalog) -> list[dict]:
    conn = sqlite3.connect(f"file:{catalog.config.database_path}?mode=ro",
                           uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(SPAN_SQL)]
    finally:
        conn.close()


def span_count(catalog) -> int:
    conn = sqlite3.connect(f"file:{catalog.config.database_path}?mode=ro",
                           uri=True)
    try:
        return int(conn.execute(
            "SELECT COUNT(*) FROM evidence_spans").fetchone()[0])
    finally:
        conn.close()


def sql_update(catalog, statement: str) -> None:
    conn = sqlite3.connect(f"file:{catalog.config.database_path}?mode=rw",
                           uri=True)
    try:
        conn.execute(statement)
        conn.commit()
    finally:
        conn.close()


def write_snapshot(path: Path, rows: list[dict]) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")) + "\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(path: Path, snapshot: Path, rows: list[dict],
                   overrides: dict | None = None) -> dict:
    manifest = {
        "schema_version": prune.MANIFEST_SCHEMA,
        "ok": True,
        "archive_path": str(snapshot),
        "archive_bytes": snapshot.stat().st_size,
        "archive_sha256": sha256_file(snapshot),
        "rows_in_archive": len(rows),
        "row_digests": {r["span_id"]: prune._row_digest(r) for r in rows},
        "verified_completed_at": OLD,
    }
    if overrides:
        manifest.update(overrides)
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return manifest


def good_archive(root: Path, catalog, tag: str = "2026-01-01",
                 mutate=None, overrides=None,
                 manifest_name: str = "m.manifest.json") -> Path:
    rows = span_rows(catalog)
    if mutate:
        rows = [mutate(dict(r)) for r in rows]
    d = root / "archive" / tag
    d.mkdir(parents=True, exist_ok=True)
    snap = d / "snapshot.jsonl.gz"
    write_snapshot(snap, rows)
    write_manifest(d / manifest_name, snap, rows, overrides)
    return root


def main() -> None:
    global prune
    module_path = Path(sys.argv[1])
    base_tmp = Path(sys.argv[2])
    if base_tmp.exists():
        shutil.rmtree(base_tmp)
    base_tmp.mkdir(parents=True)
    prune = load_prune(module_path)

    results: dict[str, object] = {}

    def rec(name, fn):
        try:
            results[name] = {"ok": True, "out": fn()}
        except Exception as exc:  # noqa: BLE001 - probe records everything
            results[name] = {"ok": False, "exc": type(exc).__name__,
                             "msg": str(exc)}

    def report_dict(report) -> dict:
        return report.to_dict()

    def receipt_of(report):
        if not report.receipt_path:
            return None
        return json.loads(Path(report.receipt_path).read_text(encoding="utf-8"))

    # ------------------------------------------------------------ fixtures --
    c1 = make_catalog(base_tmp / "c1")      # read-only scenarios
    c2 = make_catalog(base_tmp / "c2")      # apply happy path
    c3 = make_catalog(base_tmp / "c3")      # refusals (drift)
    c4 = make_catalog(base_tmp / "c4")      # archive byte drift

    fixture_counts = {f"c{i}": span_count(c) for i, c in
                      enumerate((c1, c2, c3, c4), start=1)}

    a_empty = base_tmp / "a_empty"
    a_empty.mkdir(parents=True, exist_ok=True)
    a_bare = base_tmp / "a_bare" / "archive" / "2026-05-01"
    a_bare.mkdir(parents=True, exist_ok=True)
    a_good = base_tmp / "a_good"
    good_archive(a_good, c1)
    a_fresh_root = base_tmp / "a_fresh"
    good_archive(a_fresh_root, c1)

    a_conflict = base_tmp / "a_conflict"
    good_archive(a_conflict, c1, "2026-01-01")
    d_conf = a_conflict / "archive" / "2026-01-02"
    d_conf.mkdir(parents=True, exist_ok=True)
    conflict_rows = []
    for row in span_rows(c1):
        mutated = dict(row)
        mutated["raw_text"] = (mutated["raw_text"] or "") + "CONFLICT"
        conflict_rows.append(mutated)
    snap_conf = d_conf / "snapshot2.jsonl.gz"
    write_snapshot(snap_conf, conflict_rows)
    write_manifest(d_conf / "m2.manifest.json", snap_conf, conflict_rows)

    a_bad = base_tmp / "a_bad" / "archive" / "bad"
    a_bad.mkdir(parents=True, exist_ok=True)
    rows1 = span_rows(c1)
    if not rows1:
        raise RuntimeError(f"fixture produced no evidence spans: {fixture_counts}")

    def _mk(name: str, overrides: dict, garbage_snapshot=None, drop=()) -> None:
        snap = a_bad / f"{name}.jsonl.gz"
        if garbage_snapshot is not None:
            snap.write_bytes(garbage_snapshot)
        else:
            write_snapshot(snap, rows1)
        manifest = {
            "schema_version": prune.MANIFEST_SCHEMA,
            "ok": True,
            "archive_path": str(snap),
            "archive_bytes": snap.stat().st_size,
            "archive_sha256": sha256_file(snap),
            "rows_in_archive": len(rows1),
            "row_digests": {r["span_id"]: prune._row_digest(r) for r in rows1},
            "verified_completed_at": OLD,
        }
        manifest.update(overrides)
        for key in drop:
            manifest.pop(key, None)
        (a_bad / f"{name}.manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    (a_bad / "m01.manifest.json").write_text("{not json", encoding="utf-8")
    _mk("m02", {"schema_version": "wrong-1.0"})
    _mk("m03", {"ok": False})
    _mk("m04", {"archive_path": str(base_tmp / "nowhere" / "gone.jsonl.gz")})
    _mk("m05", {"archive_bytes": 1})
    _mk("m06", {"archive_sha256": "0" * 64})
    _mk("m07", {}, garbage_snapshot=b"not a gzip stream at all")
    _mk("m08", {"rows_in_archive": len(rows1) + 1})
    bad_digests = {r["span_id"]: prune._row_digest(r) for r in rows1}
    bad_digests[next(iter(bad_digests))] = "f" * 64
    _mk("m09", {"row_digests": bad_digests})
    _mk("m10", {"verified_completed_at": "not-a-time"})
    _mk("m11", {}, drop=("archive_path",))

    results["fixture_span_counts"] = fixture_counts

    # ----------------------------------------------------------- scenarios --
    rec("dry_empty_archive_root", lambda: report_dict(
        prune.prune_retired_evidence(c1.config, a_empty, now=NOW)))
    rec("dry_bare_directory_no_manifest", lambda: report_dict(
        prune.prune_retired_evidence(
            c1.config, base_tmp / "a_bare", now=NOW, retention_days=0)))
    rec("dry_bad_manifest_battery", lambda: report_dict(
        prune.prune_retired_evidence(c1.config, base_tmp / "a_bad", now=NOW)))

    good_report = prune.prune_retired_evidence(c1.config, a_good, now=NOW)
    rec("dry_good_due", lambda: report_dict(good_report))
    rec("dry_good_due_plan_ids", lambda: list(good_report.plan.span_ids))
    rec("dry_good_within_retention", lambda: report_dict(
        prune.prune_retired_evidence(c1.config, a_fresh_root, now=NOW_FRESH)))
    rec("dry_with_frozen_plan_arg", lambda: report_dict(
        prune.prune_retired_evidence(c1.config, a_good, now=NOW,
                                     plan=good_report.plan)))
    rec("dry_conflict_archives", lambda: report_dict(
        prune.prune_retired_evidence(c1.config, a_conflict, now=NOW)))
    rec("naive_now_type_error", lambda: report_dict(
        prune.prune_retired_evidence(c1.config, a_good, now=NOW_NAIVE)))

    # --- apply happy path on c2 ---
    good2 = prune.prune_retired_evidence(c2.config, a_good, now=NOW)
    before2 = span_count(c2)
    applied = prune.prune_retired_evidence(c2.config, a_good, now=NOW,
                                           apply=True, plan=good2.plan)
    results["apply_happy"] = {
        "ok": True, "out": report_dict(applied), "before": before2,
        "after": span_count(c2), "receipt": receipt_of(applied),
        "receipt_files": sorted(
            p.name for p in (c2.config.catalog_dir / "artifacts"
                             / "gates").glob("prune-retired-*.json"))}
    again = prune.prune_retired_evidence(c2.config, a_good, now=NOW,
                                         apply=True, plan=good2.plan)
    results["apply_idempotent_second"] = {
        "ok": True, "out": report_dict(again), "after": span_count(c2),
        "receipt": receipt_of(again)}
    no_plan = prune.prune_retired_evidence(c2.config, a_good, now=NOW,
                                           apply=True)
    results["apply_without_plan_after_delete"] = {
        "ok": True, "out": report_dict(no_plan), "after": span_count(c2),
        "receipt": receipt_of(no_plan),
        "receipt_files": sorted(
            p.name for p in (c2.config.catalog_dir / "artifacts"
                             / "gates").glob("prune-retired-*.json"))}

    # --- refusals on c3 ---
    plan3 = prune.prune_retired_evidence(c3.config, a_good, now=NOW).plan
    tampered = prune.PrunePlan(
        span_ids=tuple(reversed(plan3.span_ids)),
        row_digests=plan3.row_digests, archives=plan3.archives,
        retention_days=plan3.retention_days, plan_hash=plan3.plan_hash)
    rec("refuse_tampered_plan_hash", lambda: report_dict(
        prune.prune_retired_evidence(c3.config, a_good, now=NOW, apply=True,
                                     plan=tampered)))

    sql_update(c3, "UPDATE evidence_spans SET raw_text = raw_text || 'DRIFT'")
    count_drift = span_count(c3)
    rec("refuse_row_digest_drift", lambda: report_dict(
        prune.prune_retired_evidence(c3.config, a_good, now=NOW, apply=True,
                                     plan=plan3)))
    results["refuse_row_digest_drift"]["count_before"] = count_drift
    results["refuse_row_digest_drift"]["count_after"] = span_count(c3)

    sql_update(c3, "UPDATE documents SET source_status = 'active' "
                   "WHERE document_id IN (SELECT DISTINCT document_id "
                   "FROM evidence_spans)")
    rec("refuse_status_drift", lambda: report_dict(
        prune.prune_retired_evidence(c3.config, a_good, now=NOW, apply=True,
                                     plan=plan3)))
    results["refuse_status_drift"]["count_after"] = span_count(c3)

    # --- archive byte drift on c4 ---
    plan4 = prune.prune_retired_evidence(c4.config, a_good, now=NOW).plan
    victim = a_good / "archive" / "2026-01-01" / "snapshot.jsonl.gz"
    victim.write_bytes(victim.read_bytes() + b"DRIFT")
    count4 = span_count(c4)
    rec("refuse_archive_byte_drift", lambda: report_dict(
        prune.prune_retired_evidence(c4.config, a_good, now=NOW, apply=True,
                                     plan=plan4)))
    results["refuse_archive_byte_drift"]["count_before"] = count4
    results["refuse_archive_byte_drift"]["count_after"] = span_count(c4)

    # ------------------------------------------------------- normalization --
    def normalize(value) -> str:
        text = value if isinstance(value, str) else json.dumps(
            value, ensure_ascii=False, default=str)
        text = text.replace(str(base_tmp), "<TMP>")
        text = re.sub(r"prune-retired-[0-9a-f]{16}\.json",
                      "prune-retired-<UUID>.json", text)
        text = re.sub(r"\b[0-9a-f]{40,64}\b", "<SHA>", text)
        return text

    print(json.dumps({k: normalize(v) for k, v in results.items()},
                     ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
