"""Bounded real public-reader clock validation; no FF/provider/model calls."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from tempfile import TemporaryDirectory
import time

import yaml

RF = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RF / "scripts"))
import company_wiki_source_reader_v2 as reader  # noqa: E402
from contracts.document import validate_evidence_claims, validate_sources  # noqa: E402
from contracts.evidence import text_sha256  # noqa: E402
from source_preparation import prepare_registered_source_result  # noqa: E402


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwp", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.cwp / "config/source_catalog.yaml"
    config_before = sha(config_path.read_bytes())
    original_environment = {key: os.environ.get(key) for key in ("PYTHONPATH", "PYTHONUTF8", "PYTHONDONTWRITEBYTECODE")}
    report = {"schema_version": "late-read-clock-validation/1", "as_of_date": "2026-10-08",
              "observed_at": datetime.now(timezone.utc).isoformat(), "status": "NOT_RUN",
              "scope": "actual registered-source public reader -> RF source/capture -> formal source/claim validation; no forecast or research PASS",
              "provider_calls": 0, "FF_calls": 0, "model_calls": 0, "download_events": 0,
              "production_writes": 0, "sources": [], "cleanup_complete": False}
    original_open = reader.open_source_version_v2
    temp_path = None
    try:
        os.environ["PYTHONPATH"] = str(args.cwp / "src")
        os.environ["PYTHONUTF8"] = "1"
        os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
        with TemporaryDirectory(prefix="rfclk-") as scratch:
            temp_path = Path(scratch)
            # Snapshot the existing database in read-only mode. This temporary
            # runtime fixture uses only public readers, with no synthetic rows.
            catalog_dir = temp_path / "catalog"
            catalog_dir.mkdir()
            with closing(sqlite3.connect((args.cwp / ".source_catalog/catalog.sqlite3").as_uri() + "?mode=ro", uri=True)) as upstream:
                with closing(sqlite3.connect(catalog_dir / "catalog.sqlite3")) as isolated:
                    upstream.backup(isolated)
            payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            payload["catalog_dir"] = str(catalog_dir)
            for root in payload["roots"]:
                root["path"] = root["path"].replace("${PROJECT_ROOT}", str(args.cwp)).replace("${USER_PROFILE}", str(Path.home()))
            isolated_config = temp_path / "source_catalog.yaml"
            isolated_config.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            for company in manifest["companies"]:
                item = next(row for row in company["minimum_registration_group"] if row.get("source_ref") and row["metadata"]["document_kind"] == "annual_report")
                ref, metadata = item["source_ref"], item["metadata"]
                candidate = {"status": "source_candidate", "source_ref": ref,
                    "byte_verification": "pending_verified_open", "document_kind": metadata["document_kind"],
                    "fiscal_year": metadata["fiscal_year"], "fiscal_period": metadata["fiscal_period"],
                    "resolution_outcome": "reused_existing", "download_events": 0}
                observed = []
                def observe(*pos, **kw):
                    result = original_open(*pos, **kw)
                    observed.append(result)
                    return result
                reader.open_source_version_v2 = observe
                started = time.monotonic()
                prepared = prepare_registered_source_result(candidate, as_of_date="2026-10-08",
                    company_wiki_catalog_config=isolated_config, timeout_seconds=45)
                source = prepared["source"]
                source_index = validate_sources({"sources": [source]}, date(2026, 10, 8), require_capture=True)
                body, receipt, actual_manifest = observed[0]
                assert len(observed) == 1 and sha(body) == ref["content_sha256"]
                assert source["capture"]["captured_date"] == receipt["read_at"][:10] > "2026-10-08"
                assert source["published_date"] == actual_manifest["published_date"] <= "2026-10-08"
                evidence = {"company": company["company"], "status": "PASS", "source_ref": ref,
                    "published_date": source["published_date"], "original_retrieved_at": actual_manifest["retrieved_at"],
                    "actual_read_at": receipt["read_at"], "captured_date": source["capture"]["captured_date"],
                    "host_timestamp": source["capture"]["host_receipt"]["timestamp"],
                    "read_schema": receipt["schema_version"], "raw_sha_verified": True,
                    "public_open_count": len(observed), "download_calls": source["reuse_receipt"]["download_calls"],
                    "duration_seconds": round(time.monotonic() - started, 3)}
                if ref["mime_type"] == "text/html":
                    # A small actual text-only slice of the opened raw HTML,
                    # recorded as a clock-contract inspection claim, not research.
                    match = re.search(rb'Revenue (?:is|are) recognized[^<]{40,400}', body)
                    if match is None:
                        match = re.search(rb'[Rr]evenue recognition[^<]{30,400}', body)
                    assert match is not None, "actual recognition text unavailable; do not fabricate excerpt"
                    excerpt = match.group().decode("utf-8")
                    checked = datetime.now(timezone.utc).date().isoformat()
                    locator = f"raw-utf8-bytes/{match.start()}:{match.end()}"
                    claim = {"claim_id": "actual-clock-inspection", "source_id": source["source_id"],
                        "target_type": "recognition_policy", "target_id": "clock-contract-inspection-only",
                        "support_type": "policy_support", "locator": locator, "excerpt": excerpt,
                        "excerpt_sha256": text_sha256(excerpt), "content_sha256": ref["content_sha256"],
                        "capture_receipt_sha256": source["capture"]["receipt_sha256"],
                        "verification_status": "opened_and_checked", "verified_by": "actual local byte-slice inspection",
                        "verified_date": checked}
                    validate_evidence_claims({"schema_version": "3.7", "evidence_claims": [claim]}, source_index, {}, date(2026, 10, 8))
                    evidence["actual_claim"] = claim
                report["sources"].append(evidence)
            report["status"] = "PASS"
    finally:
        reader.open_source_version_v2 = original_open
        for key, value in original_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        report["production_config_sha_before"] = config_before
        report["production_config_sha_after"] = sha(config_path.read_bytes())
        report["production_config_unchanged"] = report["production_config_sha_before"] == report["production_config_sha_after"]
        report["cleanup_complete"] = temp_path is not None and not temp_path.exists()
        report["environment_restored"] = all(os.environ.get(key) == value for key, value in original_environment.items())
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "sources": len(report["sources"]), "cleanup_complete": report["cleanup_complete"]}))


if __name__ == "__main__":
    main()
