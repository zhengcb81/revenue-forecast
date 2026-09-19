"""runner_child: one isolated scratch subprocess for card I-02-E cases.

argv:
  python runner_child.py <project> <spec_json> <result_json> <pid_file>

The spec names the mode (download | register), optional W02E injection
(point:mode), scan_pause_doc, and optional request_override (identity
conflict cases). The child installs the override bootstrap, builds
catalog/service/journal, runs ONE ensure call and writes a full result JSON.
Never touches production paths.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import w02e_bootstrap  # noqa: E402

w02e_bootstrap.setup("override")

from company_wiki.source_catalog import (  # noqa: E402
    CatalogConfig,
    RootSpec,
    SourceCatalog,
)
from company_wiki.source_catalog.acquisition import (  # noqa: E402
    AcquisitionCoordinator,
    AdapterRegistry,
    DownloadCandidate,
    DownloadReceipt,
)
from company_wiki.source_catalog.acquisition_journal import (  # noqa: E402
    AcquisitionJournal,
)
from company_wiki.source_catalog.acquisition_service import (  # noqa: E402
    SourceAcquisitionService,
    SourceRecoveryInput,
)
from company_wiki.source_catalog.canonical_writer import (  # noqa: E402
    CanonicalSourceWriter,
)
from company_wiki.source_catalog.resolver import SourceRequest  # noqa: E402

HK_FILENAME = "2026-04-28_hkexnews_12127452_2025年度報告.pdf"
HK_SHA = "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c"


class LocalSampleAdapter:
    name = "local-sample"
    version = "1.0.0"

    def __init__(self, sample_raw: Path):
        self._sample_raw = Path(sample_raw)
        self.calls = {"discover": 0, "fetch": 0}

    def discover(self, request):
        self.calls["discover"] += 1
        return (
            DownloadCandidate(
                candidate_id="hkexnews:12127452",
                provider="hkexnews",
                provider_document_id="12127452",
                market="HK",
                entity="小米集團－Ｗ",
                title="2025年度報告",
                source_url="https://example.invalid/hkexnews/12127452.pdf",
                document_kind="annual_report",
                filing_date="2026-04-28",
                fiscal_year=2025,
                fiscal_period="FY",
                language="zh",
            ),
        )

    def fetch(self, candidate, staging_dir):
        self.calls["fetch"] += 1
        destination = Path(staging_dir) / HK_FILENAME
        shutil.copyfile(self._sample_raw, destination)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        return DownloadReceipt(
            candidate_id=candidate.candidate_id,
            provider=candidate.provider,
            provider_document_id=candidate.provider_document_id,
            source_url=candidate.source_url,
            staged_path=str(destination),
            content_sha256=digest,
            byte_size=destination.stat().st_size,
            mime_type="application/pdf",
            retrieved_at="2026-09-18T00:00:00Z",
            http_status=200,
            adapter_name=self.name,
            adapter_version=self.version,
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    project = Path(sys.argv[1])
    spec = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    result_path = Path(sys.argv[3])
    pid_path = Path(sys.argv[4])
    pid_path.write_text(str(os.getpid()), encoding="utf-8")
    payload: dict = {"pid": str(os.getpid())}
    adapter = None
    config = None
    try:
        if spec.get("inject"):
            os.environ["W02E_INJECT"] = str(spec["inject"])
        os.environ["W02E_SCAN_PAUSE_DOC"] = str(spec.get("scan_pause_doc") or "")
        if spec.get("checkpoint_dir"):
            os.environ["W02E_CHECKPOINT_DIR"] = str(spec["checkpoint_dir"])
        companies = project / "companies"
        catalog_dir = project / ".source_catalog"
        config = CatalogConfig(
            project_root=project,
            catalog_dir=catalog_dir,
            roots=(
                RootSpec(
                    "company_raw",
                    companies,
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                    reusable_for_filing=bool(spec.get("reusable_root", True)),
                ),
            ),
        )
        catalog = SourceCatalog(config)
        catalog.scan()
        staging_root = catalog_dir / "staging"
        staging_root.mkdir(parents=True, exist_ok=True)
        adapter = LocalSampleAdapter(spec["sample_raw"])
        registry = AdapterRegistry(cn=adapter, hk=adapter, us=adapter)
        writer = CanonicalSourceWriter(
            catalog,
            staging_root=staging_root,
            stage_journal=AcquisitionJournal(catalog_dir),
        )
        service = SourceAcquisitionService(
            coordinator=AcquisitionCoordinator(
                catalog=catalog,
                adapters=registry,
                staging_root=staging_root,
            ),
            writer=writer,
            journal=AcquisitionJournal(catalog_dir),
        )
        override = spec.get("request_override") or {}
        request = SourceRequest(
            entity="小米集團－Ｗ",
            security_id="01810",
            market="HK",
            document_kind="annual_report",
            fiscal_year=2025,
            fiscal_period="FY",
            provider=override.get("provider", "hkexnews"),
            provider_document_id=override.get("provider_document_id", "12127452"),
            as_of_date="2026-09-18",
            mode="exact",
            allow_download=spec.get("mode") == "download",
        )
        if spec.get("mode") == "register":
            raw_path = (
                companies
                / "小米集團－Ｗ"
                / "raw"
                / "financial_reports"
                / "annual"
                / HK_FILENAME
            )
            recovery = SourceRecoveryInput(
                raw_path=str(raw_path),
                sidecar_path=str(raw_path) + ".source.json",
            )
            ensured = service.ensure(request, recovery=recovery)
        else:
            ensured = service.ensure(request)
        payload["status"] = ensured.status.value
        payload["resolution_status"] = ensured.resolution.to_dict().get("status")
        matches = ensured.resolution.matches or ()
        payload["match"] = (
            {
                "source_id": matches[0].source_id,
                "content_sha256": matches[0].content_sha256,
                "canonical_path": matches[0].canonical_path,
            }
            if matches
            else None
        )
        payload["provider_calls"] = dict(adapter.calls)
    except Exception as exc:
        payload["status"] = "exception"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
        payload["provider_calls"] = (
            dict(adapter.calls) if adapter else {"discover": 0, "fetch": 0}
        )
    payload["db"] = db_state(project)
    try:
        payload["journal_lines"] = [
            a.to_dict()
            for a in AcquisitionJournal(project / ".source_catalog").read_all()
        ]
    except Exception as exc:
        payload["journal_lines"] = [
            {"journal_read_error": f"{type(exc).__name__}: {exc}"}
        ]
    payload["raw_files"] = (
        [
            {
                "path": str(item.relative_to(project)),
                "sha256": sha256_file(item),
                "size": item.stat().st_size,
            }
            for item in sorted((project / "companies").rglob("*"))
            if item.is_file()
        ]
        if (project / "companies").is_dir()
        else []
    )
    staging_tree = project / ".source_catalog" / "staging"
    payload["staging_files"] = (
        sorted(
            str(item.relative_to(project))
            for item in staging_tree.rglob("*")
            if item.is_file()
        )
        if staging_tree.is_dir()
        else []
    )
    result_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


def db_state(project: Path) -> dict:
    catalog_dir = project / ".source_catalog"
    candidates = sorted(catalog_dir.glob("*.sqlite3"))
    if not candidates:
        return {}
    connection = sqlite3.connect(str(candidates[0]))
    connection.row_factory = sqlite3.Row
    try:
        return {
            "scan_runs": [
                dict(row)
                for row in connection.execute(
                    "SELECT run_id, status FROM scan_runs ORDER BY started_at"
                ).fetchall()
            ],
            "sources_rows": connection.execute(
                "SELECT COUNT(*) FROM sources WHERE content_sha256=?", (HK_SHA,)
            ).fetchone()[0],
            "documents_active": connection.execute(
                "SELECT COUNT(*) FROM documents WHERE document_id=? AND source_status='active'",
                ("urn:company-wiki:document:sha256:" + HK_SHA,),
            ).fetchone()[0],
            "locations_active_original": connection.execute(
                "SELECT COUNT(*) FROM locations WHERE role='original_primary' "
                "AND location_status='active' AND relative_path LIKE ?",
                ("%" + HK_FILENAME,),
            ).fetchone()[0],
        }
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
