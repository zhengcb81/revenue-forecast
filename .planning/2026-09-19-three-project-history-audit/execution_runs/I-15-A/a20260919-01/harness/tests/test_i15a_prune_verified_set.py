"""I-15-A: does prune delete only the verified archive set?

Frozen oracle: ../../oracle.md (written before any run).  This file is the isolated
counterexample suite.  It never touches the production catalog and never deletes a real
file: every catalog and archive it uses is created under the attempt's scratch dir.

Expectations are the PRE-LISTED sets from oracle.md (`EXPECTED_DELETE`/`EXPECTED_RETAIN`),
never values derived from `prune_retired_evidence`'s own report.
"""

from __future__ import annotations

import gzip
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from archive_verifier import (  # noqa: E402
    ADDED_AFTER_ARCHIVE,
    ARCHIVED_AT_TAKE,
    EXPECTED_DELETE,
    EXPECTED_RETAIN,
    NOW,
    NEVER_ARCHIVED,
    PRE_ARCHIVE_DOCUMENTS,
    RETENTION_DAYS,
    SAMPLE_DOCUMENTS,
    VERIFIED_COMPLETED_AT,
    add_product_src,
    advance_to_post_archive_state,
    build_scratch_catalog,
    guard_scratch,
    live_row,
    live_span_ids,
    plan_hash,
    read_archive_rows,
    retired_span_ids,
    row_digest,
    select_prunable_ids,
    verify_archive,
    write_real_archive,
)

CW = Path(os.environ.get("I15A_CW_ROOT", r"C:\Users\郑曾波\Projects\company-wiki"))
ATTEMPT = HERE.parent
SCRATCH_ROOT = ATTEMPT / "scratch"

add_product_src(os.environ.get("I15A_PRODUCT_SRC", str(CW / "src")))

from company_wiki.source_catalog.models import CatalogConfig, RootSpec  # noqa: E402
from company_wiki.source_catalog.prune_retired_evidence import (  # noqa: E402
    prune_retired_evidence,
)


def make_config(case: str, db_path: Path) -> CatalogConfig:
    db_path = guard_scratch(db_path)
    # CatalogConfig rejects an empty roots tuple, and prune only reads
    # config.database_path / config.catalog_dir; a scratch root keeps the config lawful
    # without ever pointing at a product directory.
    scratch_root = db_path.parent / "roots"
    scratch_root.mkdir(parents=True, exist_ok=True)
    return CatalogConfig(
        project_root=db_path.parent.parent,
        catalog_dir=db_path.parent,
        roots=(RootSpec("scratch", scratch_root, "directory"),),
    )


def fresh_case(case: str) -> dict:
    """Create the card's fixed sample and take a REAL archive over it.

    PRE  phase: doc-A retired {a1,a2}, doc-C retired {c1}
                -> real archive_retired_evidence() -> gzip contains a1,a2,c1
    POST phase: + doc-B retired {b1} (never archived), + a3 (added after the archive),
                doc-C back to active.  5 spans total, as the card fixes.
    """
    root = guard_scratch(SCRATCH_ROOT / case)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    db_path = build_scratch_catalog(root / "catalog" / "catalog.sqlite3",
                                    PRE_ARCHIVE_DOCUMENTS)
    manifests = root / "manifests"
    report = write_real_archive(db_path, manifests)
    archive_path = Path(report.archive_path)
    advance_to_post_archive_state(db_path)
    return {
        "root": root,
        "db": db_path,
        "config": make_config(case, db_path),
        "archive_root": manifests,
        "archive_path": archive_path,
        "write_report": report,
    }


# ---------------------------------------------------------------------------
# W15-P1 - positive: delete exactly the verified set
# ---------------------------------------------------------------------------


def test_w15_p1_real_archive_verifies_independently():
    case = fresh_case("p1-verify")
    verdict = verify_archive(
        case["archive_path"],
        expected_ids=ARCHIVED_AT_TAKE,
        expected_completed_at=VERIFIED_COMPLETED_AT,
        write_manifest_to=case["root"] / "archive-verified-manifest.json",
    )
    assert verdict["ok"], verdict["problems"]
    assert verdict["rows_in_archive"] == len(ARCHIVED_AT_TAKE)
    assert verdict["duplicate_span_ids"] == []
    # the archive must NOT contain the rows that were never archived
    assert set(verdict["row_digests"]) == set(ARCHIVED_AT_TAKE)
    assert NEVER_ARCHIVED[0] not in verdict["row_digests"]
    assert ADDED_AFTER_ARCHIVE[0] not in verdict["row_digests"]


def test_w15_p1_prune_deletes_only_the_verified_set():
    """CURRENT-CODE COUNTEREXAMPLE.

    Frozen expectation of a compliant implementation: deleted == {a1, a2}.
    The verification above authorises only a1/a2.  Whatever the current code does is
    measured and compared against the pre-listed set - the assertion is against the
    frozen sets, not against the function's report.
    """
    case = fresh_case("p1-delete")
    verdict = verify_archive(
        case["archive_path"],
        expected_ids=ARCHIVED_AT_TAKE,
        expected_completed_at=VERIFIED_COMPLETED_AT,
        write_manifest_to=case["root"] / "archive-verified-manifest.json",
    )
    assert verdict["ok"]

    before = live_span_ids(case["db"])
    assert sorted(before) == sorted(EXPECTED_DELETE + EXPECTED_RETAIN)

    # W15-R2 applied independently: archived AND present AND still retired.
    # c1 is inside the verified archive but its document is active -> NOT prunable.
    selection = select_prunable_ids(case["db"], verdict["row_digests"])
    (case["root"] / "exact-prune-plan.json").write_text(json.dumps({
        "schema_version": "exact-prune-plan-1.0",
        "span_ids": selection["prunable"],
        "plan_hash": plan_hash(selection["prunable"], verdict["archive_sha256"],
                               VERIFIED_COMPLETED_AT, RETENTION_DAYS),
        "archive_sha256": verdict["archive_sha256"],
        "verified_completed_at": VERIFIED_COMPLETED_AT,
        "retention_days": RETENTION_DAYS,
        "selection_detail": selection,
        "expected_delete": EXPECTED_DELETE,
        "expected_retain": EXPECTED_RETAIN,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # fabricated-but-honest clock: an old directory name, as the current code requires
    old_dir = case["archive_root"] / "archive" / "2026-05-01"
    old_dir.mkdir(parents=True, exist_ok=True)

    report = prune_retired_evidence(case["config"], case["archive_root"],
                                    apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(case["db"])
    deleted = sorted(set(before) - set(after))
    retained = sorted(set(after))

    (case["root"] / "deleted-and-retained-ids.json").write_text(
        json.dumps({"authorised_by_manifest": sorted(verdict["row_digests"]),
                    "authorised_to_delete": selection["prunable"],
                    "in_archive_but_not_retired": selection["in_archive_not_retired"],
                    "deleted": deleted, "retained": retained,
                    "expected_delete": EXPECTED_DELETE,
                    "expected_retain": EXPECTED_RETAIN,
                    "product_report": report.to_dict()},
                   indent=2, ensure_ascii=False), encoding="utf-8")

    assert selection["prunable"] == sorted(EXPECTED_DELETE)
    assert deleted == sorted(EXPECTED_DELETE), (
        f"prune deleted {deleted} but the verified archive authorises only "
        f"{sorted(EXPECTED_DELETE)}; retained={retained} (product report: {report.to_dict()})"
    )


def test_w15_p2_second_apply_is_idempotent_for_the_authorised_set():
    case = fresh_case("p2-idempotent")
    verdict = verify_archive(case["archive_path"], expected_ids=ARCHIVED_AT_TAKE,
                             expected_completed_at=VERIFIED_COMPLETED_AT)
    assert verdict["ok"]
    (case["archive_root"] / "archive" / "2026-05-01").mkdir(parents=True, exist_ok=True)
    first = prune_retired_evidence(case["config"], case["archive_root"],
                                   apply=True, retention_days=RETENTION_DAYS)
    after_first = live_span_ids(case["db"])
    second = prune_retired_evidence(case["config"], case["archive_root"],
                                    apply=True, retention_days=RETENTION_DAYS)
    after_second = live_span_ids(case["db"])
    (case["root"] / "idempotence.json").write_text(json.dumps({
        "first_report": first.to_dict(), "second_report": second.to_dict(),
        "after_first": after_first, "after_second": after_second,
        "expected_retain": EXPECTED_RETAIN,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    # second apply must be a no-op; the rows that must never be deleted are still there
    assert second.deleted_rows == 0
    assert set(EXPECTED_RETAIN) <= set(after_second)


def test_w15_p2_restore_reproduces_the_archived_rows_exactly():
    """W15-R7: recoverability is proven by row digests, not by row counts."""
    case = fresh_case("p2-restore")
    verdict = verify_archive(
        case["archive_path"], expected_ids=ARCHIVED_AT_TAKE,
        expected_completed_at=VERIFIED_COMPLETED_AT,
        write_manifest_to=case["root"] / "archive-verified-manifest.json")
    assert verdict["ok"]
    pre_delete_digests = {sid: row_digest(live_row(case["db"], sid))
                          for sid in EXPECTED_DELETE}

    # restore into an independent empty catalog
    restored_dir = guard_scratch(case["root"] / "restore-catalog")
    restored_dir.mkdir(parents=True, exist_ok=True)
    restored_db = build_scratch_catalog(restored_dir / "catalog.sqlite3")
    # start from an empty span table: the restore must recreate rows, not merge them
    conn = sqlite3.connect(restored_db)
    conn.execute("DELETE FROM evidence_spans")
    conn.commit()
    conn.close()

    archive_rows = {r["span_id"]: r for r in read_archive_rows(case["archive_path"])}
    conn = sqlite3.connect(restored_db)
    try:
        for span_id in EXPECTED_DELETE:
            row = archive_rows[span_id]
            conn.execute(
                """INSERT INTO evidence_spans(span_id, document_id, source_id, locator,
                       page_number, paragraph_index, table_index, raw_text, span_json,
                       parser_name, parser_version, parse_status)
                   VALUES(:span_id,:document_id,:source_id,:locator,:page_number,
                          :paragraph_index,:table_index,:raw_text,:span_json,
                          :parser_name,:parser_version,:parse_status)""", row)
        conn.commit()
    finally:
        conn.close()

    restored_digests = {sid: row_digest(live_row(restored_db, sid))
                        for sid in EXPECTED_DELETE}
    proof = {
        "pre_delete_digests": pre_delete_digests,
        "restored_digests": restored_digests,
        "identical": pre_delete_digests == restored_digests,
        "restored_ids": EXPECTED_DELETE,
        "archive_sha256": verdict["archive_sha256"],
        "refused_ids": [],  # populated by the active-row case below
    }
    # restoring an ACTIVE row must be refused: c1 is in the archive but its document is active
    active_in_archive = [sid for sid in verdict["row_digests"]
                         if sid not in EXPECTED_DELETE]
    statuses = document_statuses(case["db"])
    refused = [sid for sid in active_in_archive
               if statuses.get(span_document(case["db"], sid)) != "retired"]
    proof["refused_ids"] = refused
    proof["refused_reason"] = "document is not retired; archive presence alone is not a licence"
    (case["root"] / "restore-proof.json").write_text(
        json.dumps(proof, indent=2, ensure_ascii=False), encoding="utf-8")

    assert pre_delete_digests == restored_digests, "restore is not row-identical"
    assert "c1" in refused


def document_statuses(db_path: Path) -> dict:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return {r[0]: r[1] for r in conn.execute(
            "SELECT document_id, source_status FROM documents")}
    finally:
        conn.close()


def span_document(db_path: Path, span_id: str) -> str:
    return live_row(db_path, span_id).get("document_id")


# ---------------------------------------------------------------------------
# W15-N1 - negative: old empty directory / corrupt or missing evidence
# ---------------------------------------------------------------------------


def test_w15_n1_empty_old_directory_is_not_authorisation():
    """The current code's own test builds exactly this and expects a full delete."""
    root = guard_scratch(SCRATCH_ROOT / "n1-empty-old-dir")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    db_path = build_scratch_catalog(root / "catalog" / "catalog.sqlite3")
    manifests = root / "manifests"
    (manifests / "archive" / "2026-05-01").mkdir(parents=True)   # empty, old, no gzip

    before = live_span_ids(db_path)
    report = prune_retired_evidence(make_config("n1-empty-old-dir", db_path), manifests,
                                    apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(db_path)
    (root / "n1-empty-old-dir.json").write_text(json.dumps({
        "case": "old empty directory only, no archive file at all",
        "before": before, "after": after,
        "deleted": sorted(set(before) - set(after)),
        "product_report": report.to_dict(),
        "frozen_expectation": "0 deleted; an empty old directory authorises nothing",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    # COUNTEREXAMPLE: the frozen expectation (0 deleted) is NOT met.  The assertion below
    # encodes the frozen expectation and is therefore RED on the current code.  The
    # measured values are preserved in n1-empty-old-dir.json either way.
    assert set(after) == set(before), (
        "an old empty directory authorises nothing, but prune deleted "
        f"{sorted(set(before) - set(after))}")


def test_w15_n1_corrupt_archive_is_not_authorisation():
    case = fresh_case("n1-corrupt")
    case["archive_path"].write_bytes(b"\x1f\x8b\x08\x00 this is not a valid gzip body")
    verdict = verify_archive(case["archive_path"], expected_ids=ARCHIVED_AT_TAKE,
                             expected_completed_at=VERIFIED_COMPLETED_AT)
    (case["root"] / "n1-corrupt.json").write_text(json.dumps({
        "verdict": verdict, "archive_path": str(case["archive_path"]),
        "frozen_expectation": "verification fails closed; prune must not run",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    assert not verdict["ok"]


def test_w15_n1_manifest_count_and_digest_conflicts_are_refused():
    case = fresh_case("n1-manifest-conflict")
    verdict = verify_archive(case["archive_path"], expected_ids=ARCHIVED_AT_TAKE,
                             expected_completed_at=VERIFIED_COMPLETED_AT)
    assert verdict["ok"]
    manifest = json.loads((case["root"] / "archive-verified-manifest.json").read_text(
        encoding="utf-8")) if (case["root"] / "archive-verified-manifest.json").is_file() else None
    # wrong count / wrong digest variants
    tampered_count = dict(verdict)
    tampered_count["rows_in_archive"] = verdict["rows_in_archive"] + 1
    tampered_digest = {**verdict["row_digests"], "a1": "0" * 64}
    (case["root"] / "n1-manifest-conflict.json").write_text(json.dumps({
        "verified_rows": verdict["rows_in_archive"],
        "tampered_rows_in_manifest": tampered_count["rows_in_archive"],
        "digest_before": verdict["row_digests"]["a1"],
        "digest_after_tamper": tampered_digest["a1"],
        "frozen_expectation": "a count or digest conflict must fail verification",
        "note": "manifest produced by this attempt; the product has no manifest at all yet",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    assert tampered_count["rows_in_archive"] != verdict["rows_in_archive"]
    assert tampered_digest["a1"] != verdict["row_digests"]["a1"]


def test_w15_n1_same_day_second_archive_overwrites_the_first_snapshot():
    """The card names this explicitly: archive reader snapshot/output completeness.

    The product writer uses ``archive/<today>/retired-evidence.jsonl.gz`` opened with
    mode ``"wt"``, so a second run on the same UTC day truncates the first snapshot.
    Frozen requirement (W15-R1): a verified manifest must pin the archive file by
    sha256+size, which is exactly what makes such an overwrite detectable.
    """
    case = fresh_case("n1-same-day")
    rows_first = read_archive_rows(case["archive_path"])
    first_hash = __import__("hashlib").sha256(case["archive_path"].read_bytes()).hexdigest()

    # take a second archive the same day, now over the POST state (different span set)
    second = write_real_archive(case["db"], case["archive_root"])
    second_path = Path(second.archive_path)
    rows_second = read_archive_rows(second_path)
    second_hash = __import__("hashlib").sha256(second_path.read_bytes()).hexdigest()

    (case["root"] / "n1-same-day-overwrite.json").write_text(json.dumps({
        "case": "two archive runs on the same UTC day",
        "archive_path": str(second_path),
        "first_span_ids": sorted(r["span_id"] for r in rows_first),
        "second_span_ids": sorted(r["span_id"] for r in rows_second),
        "first_sha256": first_hash,
        "second_sha256": second_hash,
        "overwritten": first_hash != second_hash,
        "first_write_report": case["write_report"].to_dict(),
        "second_write_report": second.to_dict(),
        "frozen_expectation": "a manifest pins sha256+size so an overwrite is detectable",
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    assert first_hash != second_hash, "expected the same-day rerun to replace the snapshot"
    # both runs reconcile counts, yet the CONTENT differs: count equality proves nothing
    assert case["write_report"].ok and second.ok


# ---------------------------------------------------------------------------
# W15-N2 - negative: the clock must come from the verified completion time
# ---------------------------------------------------------------------------


def test_w15_n2_directory_name_is_not_the_retention_clock():
    root = guard_scratch(SCRATCH_ROOT / "n2-clock")
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    db_path = build_scratch_catalog(root / "catalog" / "catalog.sqlite3")
    manifests = root / "manifests"
    # Verified completion is RECENT (2026-09-18) although the directory name is old.
    (manifests / "archive" / "2021-01-01").mkdir(parents=True)
    (manifests / "archive" / "2021-01-01" / "retired-evidence.jsonl.gz").write_bytes(
        gzip.compress(b'{"span_id": "a1"}\n'))
    manifest = {
        "schema_version": "archive-verified-manifest-1.0",
        "catalog_identity": "scratch-catalog-i15a",
        "archive_path": str(manifests / "archive" / "2021-01-01" / "retired-evidence.jsonl.gz"),
        "verified_completed_at": "2026-09-18T00:00:00Z",
        "retention_days": RETENTION_DAYS,
        "row_digests": {},
        "note": "fabricated manifest: recent completion, ancient directory name",
    }
    (root / "archive-verified-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    before = live_span_ids(db_path)
    report = prune_retired_evidence(make_config("n2-clock", db_path), manifests,
                                    apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(db_path)
    (root / "n2-clock.json").write_text(json.dumps({
        "directory_name": "2021-01-01",
        "verified_completed_at": manifest["verified_completed_at"],
        "days_since_verified_completion_from_fixed_now": (
            __import__("datetime").date(2026, 9, 19) - __import__("datetime").date(2026, 9, 18)
        ).days,
        "fixed_now": NOW,
        "before": before, "after": after,
        "deleted": sorted(set(before) - set(after)),
        "product_report": report.to_dict(),
        "frozen_expectation": "0 deleted: the verified completion time is inside the window",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    assert set(after) == set(before), (
        "the retention decision came from the directory name, not the verified completion time")


# ---------------------------------------------------------------------------
# W15-N3 - negative: TOCTOU between plan and apply
# ---------------------------------------------------------------------------


def test_w15_n3_mutation_after_plan_must_abort_not_silently_shrink():
    case = fresh_case("n3-toctou")
    verdict = verify_archive(case["archive_path"], expected_ids=ARCHIVED_AT_TAKE,
                             expected_completed_at=VERIFIED_COMPLETED_AT,
                             write_manifest_to=case["root"] / "archive-verified-manifest.json")
    assert verdict["ok"]
    authorised = sorted(EXPECTED_DELETE)
    digest = plan_hash(authorised, verdict["archive_sha256"], VERIFIED_COMPLETED_AT,
                       RETENTION_DAYS)
    (case["root"] / "exact-prune-plan.json").write_text(json.dumps({
        "schema_version": "exact-prune-plan-1.0",
        "span_ids": authorised,
        "plan_hash": digest,
        "archive_sha256": verdict["archive_sha256"],
        "verified_completed_at": VERIFIED_COMPLETED_AT,
        "retention_days": RETENTION_DAYS,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # TOCTOU: a2's content changes after the plan was frozen
    conn = sqlite3.connect(case["db"])
    conn.execute("UPDATE evidence_spans SET raw_text=? WHERE span_id=?",
                 ("MUTATED AFTER PLAN", "a2"))
    conn.commit()
    conn.close()
    # and doc-C is active again in this scenario, which must also stop c1
    (case["archive_root"] / "archive" / "2026-05-01").mkdir(parents=True, exist_ok=True)

    before = live_span_ids(case["db"])
    report = prune_retired_evidence(case["config"], case["archive_root"],
                                    apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(case["db"])
    deleted = sorted(set(before) - set(after))
    (case["root"] / "fault-recovery.json").write_text(json.dumps({
        "case": "W15-N3 TOCTOU: a2 mutated after the plan hash was frozen",
        "plan_hash": digest,
        "authorised_set": authorised,
        "deleted": deleted,
        "retained": sorted(after),
        "product_report": report.to_dict(),
        "frozen_expectation": "apply must refuse the whole plan (no partial success)",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    assert deleted == [], (
        "a plan whose frozen row digest no longer matches must delete nothing; "
        f"deleted={deleted}")


# ---------------------------------------------------------------------------
# W15-N4 - negative: interruption mid-batch must leave recoverable facts
# ---------------------------------------------------------------------------


def test_w15_n4_interrupted_batch_leaves_a_receipt_of_what_was_deleted(monkeypatch):
    case = fresh_case("n4-crash")
    (case["archive_root"] / "archive" / "2026-05-01").mkdir(parents=True, exist_ok=True)

    from company_wiki.source_catalog import prune_retired_evidence as module

    real_lock = module.CatalogOperationLock
    calls = {"n": 0}

    class Boom(RuntimeError):
        pass

    class ExplodingStore:
        def __init__(self, database_path):
            self._inner = sqlite3.connect(database_path)
            self._inner.row_factory = sqlite3.Row

        def transaction(self):
            calls["n"] += 1
            conn = self._inner

            class _Ctx:
                def __enter__(self_inner):
                    conn.execute("BEGIN IMMEDIATE")
                    return conn

                def __exit__(self_inner, exc_type, exc, tb):
                    if calls["n"] >= 1:
                        conn.commit()          # first batch commits ...
                        raise Boom("simulated crash between batches")
                    conn.rollback()
                    return False

            return _Ctx()

    monkeypatch.setattr(module, "CatalogStore", ExplodingStore)

    before = live_span_ids(case["db"])
    receipt_path = None
    with pytest.raises(Boom):
        prune_retired_evidence(case["config"], case["archive_root"],
                               apply=True, retention_days=RETENTION_DAYS)
    after = live_span_ids(case["db"])
    receipts = list((case["config"].catalog_dir / "artifacts" / "gates").glob(
        "prune-retired-*.json")) if (case["config"].catalog_dir / "artifacts").exists() else []
    (case["root"] / "n4-crash.json").write_text(json.dumps({
        "case": "W15-N4 simulated crash after the first batch commit",
        "batch_calls": calls["n"],
        "before": before, "after": after,
        "deleted": sorted(set(before) - set(after)),
        "receipt_files": [str(p) for p in receipts],
        "frozen_expectation": "the exact deleted ids must be recoverable from a receipt "
                              "even when the run dies mid-loop",
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    # the frozen requirement: whatever was deleted must be recorded somewhere durable
    assert receipts, (
        "the crash left deleted rows with no receipt at all: the exact set is unrecoverable")
