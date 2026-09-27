#!/usr/bin/env python3
"""Isolated red/green/mutation harness for DEF-MSFT-CANONICAL-DUP.

Replays the company-wiki ``ensure --allow-download`` canonical-import path
for the MSFT FY2026 10-K request (provider_document_id=0001193125-26-323660)
against a throwaway workspace rebuilt under %TEMP%\\defmsftdup for every run.

Isolation rules honoured here:
  * NO network: the acquisition stage is stubbed at the AcquisitionCoordinator
    seam and returns the fixture DownloadCandidate/DownloadReceipt taken from
    the production provenance sidecar as STAGED.  Everything downstream of the
    downloader — canonical writer, import-time scan, exact-identity
    verification, acquisition journal, resolution envelope — runs unmodified
    production code from the selected canonical_writer variant.
  * NO production writes: the workspace, catalog DB, journal and staging tree
    are all inside %TEMP%; the production company-wiki tree is opened
    read-only for fixture bytes.
  * Variant selection goes through a shadow copy of the company_wiki package
    (sys.path[0]), so the production source file is never modified.

Usage:
  python run_case.py --case red_s1 [--out DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import sqlite3
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # <card>/rig/harness
RIG = HERE.parent                                      # <card>/rig
CARD = RIG.parent                                      # <card>/a20260926-01
VARIANTS = HERE / "variants"
FIXTURE = HERE / "fixture"

import tempfile

TMPROOT = Path(tempfile.gettempdir()) / "defmsftdup"
SHADOW = TMPROOT / "shadow"
WORKROOT = TMPROOT / "work"

PROD = Path(r"C:\Users\郑曾波\Projects\company-wiki")
CW_SRC = PROD / "src" / "company_wiki"
PROD_ANNUAL = PROD / "companies" / "MICROSOFT CORP" / "raw" / "financial_reports" / "annual"
PROD_STAGING = PROD / ".source_catalog" / "staging" / (
    "1eb6c299311836a2be1bf989e399c54ffa061513a532a9f5748ee742ab6d1838"
)

BASE_NAME = "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm"
SUFFIX_NAME = "2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30__095935f968b5.htm"
FIXTURE_SHA = "095935f968b53055cfa23f65ef8d60b8f0e414991a9b82b9582de1dac606b9e8"
ORPHAN_SHA = "e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff"

IDENTITY_ERROR = "canonical file was written but exact provider identity did not resolve"
SIDECAR_ERROR = "immutable provenance sidecar conflict"
COLLISION_ERROR = "canonical filename collision after hash suffix"

CASES: dict[str, dict] = {
    "red_s1":   {"variant": "asfound", "scenario": "S1", "expect": "red_identity"},
    "green_s1": {"variant": "fixed",   "scenario": "S1", "expect": "green_new"},
    "red_s4":   {"variant": "asfound", "scenario": "S4", "expect": "red_sidecar"},
    "green_s4": {"variant": "fixed",   "scenario": "S4", "expect": "green_dedup"},
    "m1_s1":    {"variant": "m1", "scenario": "S1", "expect": "mut_identity"},
    "m2_s4":    {"variant": "m2", "scenario": "S4", "expect": "mut_sidecar"},
    "m3_s1":    {"variant": "m3", "scenario": "S1", "expect": "mut_strict_verify"},
    "m4_s1":    {"variant": "m4", "scenario": "S1", "expect": "mut_collision"},
    "m5_s1":    {"variant": "m5", "scenario": "S1", "expect": "mut_backfill"},
    # S5 = the green_s4 post-state (both variants indexed) with the staging
    # payload re-seeded: forces import_staged through the duplicate branch.
    "dedup_s5": {"variant": "fixed", "scenario": "S5", "expect": "green_dedup_branch",
                 "reuse": "green_s4"},
    "m6_dedup": {"variant": "m6", "scenario": "S5", "expect": "mut_dedup_branch",
                 "reuse": "green_s4"},
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


# --------------------------------------------------------------------------
# workspace construction
# --------------------------------------------------------------------------
def seed_staging(work: Path) -> None:
    staged = (work / ".source_catalog" / "staging" / PROD_STAGING.name
              / "msft-20260630.htm")
    copy(PROD_STAGING / "msft-20260630.htm", staged)
    assert sha256_file(staged) == FIXTURE_SHA, "staged fixture bytes drifted"


def build_workspace(case: str, spec: dict) -> Path:
    scenario = spec["scenario"]
    work = WORKROOT / case
    reuse = spec.get("reuse")
    if reuse:
        # clone the seed workspace produced by an earlier case (indexed DB),
        # then re-seed the staging payload that run consumed
        seed = WORKROOT / reuse
        if not seed.exists():
            raise SystemExit(
                f"case {case} needs the seeded workspace {seed}; run --case {reuse} first"
            )
        if work.exists():
            shutil.rmtree(work)
        shutil.copytree(seed, work)
        seed_staging(work)
        return work

    if work.exists():
        shutil.rmtree(work)
    (work / "config").mkdir(parents=True)

    for name in ("source_catalog.yaml", "source_acquisition.yaml",
                 "source_catalog_worker.yaml", "minimal_config.yaml"):
        copy(FIXTURE / "config" / name, work / "config" / name)

    sc = work / ".source_catalog"
    copy(FIXTURE / "source_catalog" / "runtime_policy.json", sc / "runtime_policy.json")
    for name in ("cn.json", "hk.json", "us.json"):
        src = FIXTURE / "source_catalog" / "security_master" / name
        if src.exists():
            copy(src, sc / "security_master" / name)

    annual = work / "companies" / "MICROSOFT CORP" / "raw" / "financial_reports" / "annual"
    annual.mkdir(parents=True, exist_ok=True)
    copy(PROD_ANNUAL / BASE_NAME, annual / BASE_NAME)
    copy(PROD_ANNUAL / (BASE_NAME + ".source.json"), annual / (BASE_NAME + ".source.json"))
    if scenario in {"S4", "S5"}:
        copy(PROD_ANNUAL / SUFFIX_NAME, annual / SUFFIX_NAME)
        copy(PROD_ANNUAL / (SUFFIX_NAME + ".source.json"),
             annual / (SUFFIX_NAME + ".source.json"))

    # seeded staging payload: the receipt bytes this replay would otherwise
    # download from the provider (kept offline)
    seed_staging(work)
    return work


def ensure_shadow() -> Path:
    dest = SHADOW / "company_wiki"
    if not dest.exists():
        SHADOW.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            CW_SRC, dest,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    return dest


def set_variant(name: str) -> dict:
    src = VARIANTS / name / "canonical_writer.py"
    if not src.exists():
        raise SystemExit(f"variant not generated: {src}")
    target = SHADOW / "company_wiki" / "source_catalog" / "canonical_writer.py"
    pyc = SHADOW / "company_wiki" / "source_catalog" / "__pycache__"
    if pyc.exists():
        for stale in pyc.glob("canonical_writer*.pyc"):
            stale.unlink()
    shutil.copyfile(src, target)
    data = src.read_bytes()
    return {"variant": name, "sha256": hashlib.sha256(data).hexdigest().upper(),
            "bytes": len(data)}


# --------------------------------------------------------------------------
# inspection helpers
# --------------------------------------------------------------------------
def read_journal(work: Path) -> list[dict]:
    path = work / ".source_catalog" / "acquisition_attempts.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def db_inspect(work: Path) -> dict:
    db = work / ".source_catalog" / "catalog.sqlite3"
    if not db.exists():
        return {"db_exists": False}
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    out: dict = {"db_exists": True}
    out["counts"] = {
        "sources": con.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
        "documents": con.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
        "locations": con.execute("SELECT COUNT(*) FROM locations").fetchone()[0],
    }
    out["fixture_sha_sources"] = con.execute(
        "SELECT COUNT(*) FROM sources WHERE content_sha256=?", (FIXTURE_SHA,)
    ).fetchone()[0]
    out["orphan_sha_sources"] = con.execute(
        "SELECT COUNT(*) FROM sources WHERE content_sha256=?", (ORPHAN_SHA,)
    ).fetchone()[0]
    out["locations"] = [dict(r) for r in con.execute(
        "SELECT absolute_path, location_status, role FROM locations ORDER BY absolute_path"
    )]
    out["scan_runs"] = []
    for row in con.execute(
        "SELECT run_id, started_at, status, report_json FROM scan_runs ORDER BY started_at"
    ):
        item = dict(row)
        try:
            item["report"] = json.loads(item.pop("report_json"))
        except (TypeError, ValueError):
            item["report"] = None
        out["scan_runs"].append(item)
    con.close()
    return out


def annual_listing(work: Path) -> list[str]:
    annual = work / "companies" / "MICROSOFT CORP" / "raw" / "financial_reports" / "annual"
    return sorted(p.name for p in annual.iterdir()) if annual.exists() else []


def staged_remaining(work: Path) -> list[str]:
    staging = work / ".source_catalog" / "staging"
    if not staging.exists():
        return []
    return sorted(
        str(p.relative_to(staging)) for p in staging.rglob("*") if p.is_file()
    )


# --------------------------------------------------------------------------
# the run itself
# --------------------------------------------------------------------------
def run_ensure(work: Path) -> tuple[int, str, str, dict]:
    if str(SHADOW) not in sys.path:
        sys.path.insert(0, str(SHADOW))
    import company_wiki  # noqa: E402

    resolved = Path(company_wiki.__file__).resolve().parent
    if resolved != (SHADOW / "company_wiki").resolve():
        raise SystemExit(f"shadow import failed: {resolved} != {SHADOW / 'company_wiki'}")

    from company_wiki.source_catalog import cli  # noqa: E402
    from company_wiki.source_catalog.acquisition import (  # noqa: E402
        ACQUISITION_SCHEMA_VERSION,
        AcquisitionCoordinator,
        AcquisitionResult,
        AcquisitionStatus,
        DownloadCandidate,
        DownloadReceipt,
    )
    from company_wiki.source_catalog.resolver import SourceResolver  # noqa: E402

    payload = json.loads((FIXTURE / "fixture_payload.json").read_text(encoding="utf-8"))
    candidate = DownloadCandidate(**payload["candidate"])
    receipt_fields = dict(payload["receipt"])
    staged_path = work / ".source_catalog" / "staging" / PROD_STAGING.name / "msft-20260630.htm"
    receipt_fields["staged_path"] = str(staged_path)
    receipt = DownloadReceipt(**receipt_fields)

    class FixtureCoordinator(AcquisitionCoordinator):
        """Acquisition seam: serve the fixture bytes instead of the provider."""

        def resolve_or_stage(self, request, *, authorization=None):
            resolution = SourceResolver(self.catalog).resolve(request)
            return AcquisitionResult(
                schema_version=ACQUISITION_SCHEMA_VERSION,
                status=AcquisitionStatus.STAGED,
                resolution=resolution,
                adapter_name=receipt.adapter_name,
                candidate=candidate,
                receipt=receipt,
                reason="missing_source_downloaded_to_staging_pending_canonical_import",
            )

    cli.AcquisitionCoordinator = FixtureCoordinator

    argv = [
        "--config", str(work / "config" / "source_catalog.yaml"),
        "ensure",
        "--entity", "MICROSOFT CORP",
        "--market", "US",
        "--security-id", "MSFT",
        "--document-kind", "annual_report",
        "--as-of-date", "2026-09-27",
        "--fiscal-year", "2026",
        "--allow-download",
        "--acquisition-config", str(work / "config" / "source_acquisition.yaml"),
        "--allow-acquisition-while-paused",
    ]
    out_buf, err_buf = io.StringIO(), io.StringIO()
    started = time.time()
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        rc = cli.main(argv)
    duration = time.time() - started
    stdout, stderr = out_buf.getvalue(), err_buf.getvalue()
    parsed: dict = {}
    for text in (stdout, stderr):
        try:
            parsed = json.loads(text)
            break
        except ValueError:
            continue
    meta = {"duration_s": round(duration, 3), "argv": argv,
            "company_wiki_module": str(company_wiki.__file__)}
    return rc, stdout, stderr, {"json": parsed, **meta}


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def checks_for(expect: str, rc: int, stdout: str, stderr: str, parsed: dict,
               journal: list[dict], db: dict, annual: list[str],
               staged: list[str]) -> list[dict]:
    checks: list[dict] = []
    last = journal[-1] if journal else {}
    # ``ensure`` returns its dict directly when the request carries an
    # explicit --entity (no identity envelope), and wrapped in
    # ``source_ensure`` when identity was resolved from a company query.
    ensure = parsed.get("source_ensure")
    if not isinstance(ensure, dict):
        ensure = parsed if isinstance(parsed, dict) and (
            "attempt" in parsed or "acquisition" in parsed
        ) else {}
    attempt = ensure.get("attempt") or {}
    imp = ensure.get("canonical_import") or {}
    resolution = ensure.get("resolution") or parsed.get("resolution") or {}
    blob = (stdout or "") + "\n" + (stderr or "")
    scans = db.get("scan_runs") or []
    last_scan = scans[-1]["report"] if scans else None
    htm_files = [n for n in annual if n.endswith(".htm")]
    indexed_paths = {row["absolute_path"] for row in db.get("locations", [])
                     if row.get("location_status") == "active"}

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    if expect in {"red_identity", "mut_identity"}:
        add("rc_nonzero", rc != 0, f"rc={rc}")
        add("identity_error_raised", IDENTITY_ERROR in blob, blob[-400:])
        add("journal_canonical_import_failed",
            last.get("reason") == "canonical_import_failed",
            json.dumps(last, ensure_ascii=False))
        add("journal_canonical_path_null", last.get("canonical_path") in (None, ""),
            str(last.get("canonical_path")))
        add("journal_content_sha_is_fixture",
            last.get("content_sha256") == FIXTURE_SHA, str(last.get("content_sha256")))
        add("fixture_sha_not_indexed", db.get("fixture_sha_sources") == 0,
            str(db.get("fixture_sha_sources")))
        add("import_scan_failed_closed",
            last_scan is not None
            and last_scan.get("files_seen") == 0
            and any("v2 scanner unavailable (fail closed)" in e.get("error", "")
                    for e in last_scan.get("error_details", [])),
            json.dumps(last_scan, ensure_ascii=False)[:400])
        add("committed_file_left_unindexed",
            SUFFIX_NAME in htm_files
            and not any(SUFFIX_NAME in p for p in indexed_paths),
            f"htm={htm_files} indexed={sorted(indexed_paths)}")

    elif expect in {"red_sidecar", "mut_sidecar"}:
        add("rc_nonzero", rc != 0, f"rc={rc}")
        add("sidecar_conflict_raised", SIDECAR_ERROR in blob, blob[-400:])
        add("journal_canonical_import_failed",
            last.get("reason") == "canonical_import_failed",
            json.dumps(last, ensure_ascii=False))
        add("fixture_sha_not_indexed", db.get("fixture_sha_sources") == 0,
            str(db.get("fixture_sha_sources")))

    elif expect == "mut_collision":
        add("rc_nonzero", rc != 0, f"rc={rc}")
        add("collision_error_raised", COLLISION_ERROR in blob, blob[-400:])
        add("journal_canonical_import_failed",
            last.get("reason") == "canonical_import_failed",
            json.dumps(last, ensure_ascii=False))
        add("fixture_sha_not_indexed", db.get("fixture_sha_sources") == 0,
            str(db.get("fixture_sha_sources")))

    elif expect == "mut_strict_verify":
        # element 1 is intact here, so the import scan DOES index the file;
        # the mutation still rejects the AMBIGUOUS-but-committed match.
        add("rc_nonzero", rc != 0, f"rc={rc}")
        add("identity_error_raised", IDENTITY_ERROR in blob, blob[-400:])
        add("journal_canonical_import_failed",
            last.get("reason") == "canonical_import_failed",
            json.dumps(last, ensure_ascii=False))
        add("journal_canonical_path_null", last.get("canonical_path") in (None, ""),
            str(last.get("canonical_path")))
        add("import_scan_indexed_files",
            last_scan is not None and last_scan.get("files_seen", 0) >= 1,
            json.dumps(last_scan, ensure_ascii=False)[:400])
        add("fixture_sha_indexed_but_verification_rejected",
            db.get("fixture_sha_sources") == 1, str(db.get("fixture_sha_sources")))

    elif expect in {"green_new", "green_dedup"}:
        want_outcome = "downloaded_new" if expect == "green_new" else "deduplicated_after_download"
        add("rc_zero", rc == 0, f"rc={rc} stderr={stderr[-300:]}")
        add("ensure_status_imported_or_deduplicated",
            ensure.get("status") in {"imported", "deduplicated"},
            str(ensure.get("status")))
        add(f"journal_outcome_{want_outcome}",
            attempt.get("outcome") == want_outcome,
            json.dumps(attempt, ensure_ascii=False))
        add("canonical_path_hash_suffix_file",
            bool(attempt.get("canonical_path"))
            and attempt["canonical_path"].replace("\\", "/").endswith(SUFFIX_NAME),
            str(attempt.get("canonical_path")))
        add("content_sha_is_fixture",
            (imp.get("content_sha256") or attempt.get("content_sha256")) == FIXTURE_SHA,
            str(imp.get("content_sha256")))
        add("fixture_sha_indexed", db.get("fixture_sha_sources") == 1,
            str(db.get("fixture_sha_sources")))
        add("orphan_sha_indexed_too", db.get("orphan_sha_sources") == 1,
            str(db.get("orphan_sha_sources")))
        add("every_canonical_file_indexed",
            len(htm_files) > 0
            and all(any(name in p for p in indexed_paths) for name in htm_files),
            f"htm={htm_files} indexed={sorted(indexed_paths)}")
        add("staging_consumed", staged == [], str(staged))
        add("identity_backfill_intact",
            bool(resolution.get("request_id"))
            and resolution.get("request_id") == attempt.get("request_id"),
            f"resolution.request_id={resolution.get('request_id')} "
            f"attempt.request_id={attempt.get('request_id')}")
        add("import_scan_indexed_files",
            last_scan is not None and last_scan.get("files_seen", 0) >= 1,
            json.dumps(last_scan, ensure_ascii=False)[:400])

    elif expect == "mut_backfill":
        add("rc_zero_import_succeeded", rc == 0, f"rc={rc} stderr={stderr[-300:]}")
        mismatch = (resolution.get("request_id") != attempt.get("request_id"))
        add("identity_backfill_broken_by_mutation", mismatch,
            f"resolution.request_id={resolution.get('request_id')} "
            f"attempt.request_id={attempt.get('request_id')}")

    elif expect == "green_dedup_branch":
        add("rc_zero", rc == 0, f"rc={rc} stderr={stderr[-300:]}")
        add("journal_outcome_deduplicated_after_download",
            attempt.get("outcome") == "deduplicated_after_download",
            json.dumps(attempt, ensure_ascii=False))
        add("dedup_branch_taken_provenance_null",
            imp.get("provenance_path") is None,
            str(imp.get("provenance_path")))
        add("canonical_path_hash_suffix_file",
            bool(attempt.get("canonical_path"))
            and attempt["canonical_path"].replace("\\", "/").endswith(SUFFIX_NAME),
            str(attempt.get("canonical_path")))
        add("staging_consumed", staged == [], str(staged))
        add("no_new_file_created", len(htm_files) == 2, str(htm_files))
        add("fixture_sha_indexed", db.get("fixture_sha_sources") == 1,
            str(db.get("fixture_sha_sources")))
        add("identity_backfill_intact",
            bool(resolution.get("request_id"))
            and resolution.get("request_id") == attempt.get("request_id"),
            f"resolution.request_id={resolution.get('request_id')} "
            f"attempt.request_id={attempt.get('request_id')}")

    elif expect == "mut_dedup_branch":
        add("rc_zero_import_succeeded", rc == 0, f"rc={rc} stderr={stderr[-300:]}")
        add("dedup_branch_skipped_by_mutation",
            imp.get("provenance_path") is not None,
            f"provenance_path={imp.get('provenance_path')}")
    else:
        add("known_expectation", False, f"unknown expectation {expect}")
    return checks


VERDICT = {
    "red_identity": "RED_REPRODUCED",
    "red_sidecar": "RED_REPRODUCED",
    "green_new": "GREEN_PASSED",
    "green_dedup": "GREEN_PASSED",
    "green_dedup_branch": "GREEN_PASSED",
    "mut_identity": "MUTATION_CAUGHT",
    "mut_sidecar": "MUTATION_CAUGHT",
    "mut_collision": "MUTATION_CAUGHT",
    "mut_backfill": "MUTATION_CAUGHT",
    "mut_strict_verify": "MUTATION_CAUGHT",
    "mut_dedup_branch": "MUTATION_CAUGHT",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, choices=sorted(CASES))
    parser.add_argument("--out", type=Path, default=RIG / "cases")
    args = parser.parse_args()

    spec = CASES[args.case]
    started = time.time()
    result: dict = {
        "case": args.case,
        "variant": spec["variant"],
        "scenario": spec["scenario"],
        "expect": spec["expect"],
        "workspace_root": None,
        "network_calls": 0,
        "production_writes": 0,
    }
    try:
        ensure_shadow()
        result["variant_info"] = set_variant(spec["variant"])
        work = build_workspace(args.case, spec)
        result["workspace_root"] = str(work)
        result["pre_state"] = {
            "annual": annual_listing(work),
            "staged": staged_remaining(work),
        }
        rc, stdout, stderr, meta = run_ensure(work)
        journal = read_journal(work)
        db = db_inspect(work)
        annual = annual_listing(work)
        staged = staged_remaining(work)
        parsed = meta.pop("json", {})
        checks = checks_for(spec["expect"], rc, stdout, stderr, parsed,
                            journal, db, annual, staged)
        result.update({
            "rc": rc,
            "run": meta,
            "stdout": stdout,
            "stderr": stderr,
            "parsed_stdout": parsed,
            "journal": journal,
            "db": db,
            "post_state": {"annual": annual, "staged": staged},
            "checks": checks,
            "all_checks_ok": all(c["ok"] for c in checks),
        })
        result["verdict"] = VERDICT[spec["expect"]] if result["all_checks_ok"] else "UNEXPECTED"
    except Exception:
        result.update({
            "rc": None,
            "error": traceback.format_exc(),
            "checks": [{"name": "harness_completed", "ok": False,
                        "detail": "harness raised"}],
            "all_checks_ok": False,
            "verdict": "HARNESS_ERROR",
        })
    result["duration_s"] = round(time.time() - started, 3)

    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / f"{args.case}.json"
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"case": args.case, "rc": result.get("rc"),
                      "verdict": result["verdict"],
                      "failed_checks": [c["name"] for c in result["checks"] if not c["ok"]]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
