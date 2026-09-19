"""w02d_worker: one real subprocess for the W02D-P2 two-process barrier case.

argv: python w02d_worker.py <scratch_project> <barrier_dir> <result_json>

Loads the same override bootstrap, waits on a file-polling barrier until both
processes are ready, then runs ensure(request, recovery) against the SHARED
scratch catalog and writes its own result JSON (stdout/stderr captured by the
parent runner).  Never touches production.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

SCRATCH_PROJECT = Path(sys.argv[1])
BARRIER_DIR = Path(sys.argv[2])
RESULT_PATH = Path(sys.argv[3])
SAMPLES = Path(__file__).resolve().parent.parent / "samples" / "real_roots"

HK_SHA = "ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c"
HK_FILENAME = "2026-04-28_hkexnews_12127452_2025年度報告.pdf"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w02d_bootstrap  # noqa: E402

w02d_bootstrap.setup("override")

from company_wiki.source_catalog import (  # noqa: E402
    CatalogConfig,
    RootSpec,
    SourceCatalog,
)
from company_wiki.source_catalog.acquisition import (  # noqa: E402
    AcquisitionCoordinator,
    AdapterRegistry,
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


class DenyOnCallAdapter:
    name = "deny-on-call"
    version = "1.0.0"

    def __init__(self):
        self.calls = {"discover": 0, "fetch": 0}

    def discover(self, request):
        self.calls["discover"] += 1
        raise RuntimeError("deny-on-call: discovery must never run")

    def fetch(self, candidate, staging_dir):
        self.calls["fetch"] += 1
        raise RuntimeError("deny-on-call: fetch must never run")


def main() -> int:
    payload: dict = {"pid": __import__("os").getpid()}
    adapter = DenyOnCallAdapter()
    try:
        config = CatalogConfig(
            project_root=SCRATCH_PROJECT,
            catalog_dir=SCRATCH_PROJECT / ".source_catalog",
            roots=(
                RootSpec(
                    "company_raw",
                    SCRATCH_PROJECT / "companies",
                    "company_raw",
                    priority=10,
                    adapter_id="company_raw_v1",
                    reusable_for_filing=True,
                ),
            ),
        )
        catalog = SourceCatalog(config)
        catalog.scan()
        staging_root = config.catalog_dir / "staging"
        staging_root.mkdir(parents=True, exist_ok=True)
        registry = AdapterRegistry(cn=adapter, hk=adapter, us=adapter)
        service = SourceAcquisitionService(
            coordinator=AcquisitionCoordinator(
                catalog=catalog,
                adapters=registry,
                staging_root=staging_root,
            ),
            writer=CanonicalSourceWriter(catalog, staging_root=staging_root),
            journal=AcquisitionJournal(config.catalog_dir),
        )
        request = SourceRequest(
            entity="小米集團－Ｗ",
            security_id="01810",
            market="HK",
            document_kind="annual_report",
            fiscal_year=2025,
            fiscal_period="FY",
            provider="hkexnews",
            provider_document_id="12127452",
            as_of_date="2026-09-18",
            mode="exact",
            allow_download=False,
        )
        raw_path = (
            SCRATCH_PROJECT
            / "companies"
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
        # --- file-polling barrier: both processes must be ready ---
        ready = BARRIER_DIR / f"ready.{payload['pid']}"
        ready.write_text("1", encoding="utf-8")
        deadline = time.monotonic() + 60.0
        while time.monotonic() < deadline:
            others = [
                p
                for p in BARRIER_DIR.glob("ready.*")
                if p.stem != f"ready.{payload['pid']}"
            ]
            if others:
                break
            time.sleep(0.05)
        payload["barrier_released"] = bool(others)
        # --- concurrent ensure ---
        try:
            ensured = service.ensure(request, recovery=recovery)
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
        except Exception as exc:
            payload["status"] = "exception"
            payload["error_type"] = type(exc).__name__
            payload["error"] = str(exc)
        payload["provider_calls"] = dict(adapter.calls)
        payload["raw_sha256_after"] = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    except Exception as exc:  # environment failure before ensure
        payload["status"] = "setup_exception"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
    RESULT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload.get("status") in ("registered_existing", "reused") else 2


if __name__ == "__main__":
    sys.exit(main())
