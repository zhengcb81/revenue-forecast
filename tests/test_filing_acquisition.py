"""Standalone filing acquisition contracts for revenue-forecast."""

from __future__ import annotations

import ast
from datetime import date, timedelta
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from filing_acquisition import (  # noqa: E402
    AcquisitionManager,
    AdapterRegistry,
    CanonicalSourceWriter,
    DownloadCandidate,
    DownloadReceipt,
    FilingAcquisitionError,
    SourceRequest,
    _redact,
    load_acquisition_config,
    resolve_filing,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class _FakeAdapter:
    def __init__(self, market: str, payload: bytes = b"%PDF-1.7\nstandalone") -> None:
        self.market = market
        self.name = f"fake-{market.lower()}"
        self.version = "1.0.0"
        self.payload = payload
        self.discover_calls = 0
        self.fetch_calls = 0

    def discover(self, request: SourceRequest) -> tuple[DownloadCandidate, ...]:
        self.discover_calls += 1
        return (
            DownloadCandidate(
                candidate_id=f"{self.market}:2025",
                provider={"CN": "cninfo", "HK": "hkexnews", "US": "sec"}[self.market],
                provider_document_id=f"{self.market}-2025",
                market=self.market,
                entity=request.entity,
                title=f"{request.entity} 2025 Annual Report",
                source_url="https://example.test/report.pdf",
                document_kind="annual_report",
                filing_date="2026-03-20",
                fiscal_year=2025,
                form_type={"CN": "annual_report", "HK": "FY", "US": "10-K"}[
                    self.market
                ],
                language={"CN": "zh", "HK": "zh", "US": "en"}[self.market],
            ),
        )

    def fetch(self, candidate: DownloadCandidate, staging_dir: Path) -> DownloadReceipt:
        self.fetch_calls += 1
        staging_dir.mkdir(parents=True, exist_ok=True)
        staged = staging_dir / f"{candidate.candidate_id.replace(':', '-')}.pdf"
        staged.write_bytes(self.payload)
        return DownloadReceipt(
            candidate_id=candidate.candidate_id,
            provider=candidate.provider,
            provider_document_id=candidate.provider_document_id,
            source_url=candidate.source_url,
            staged_path=str(staged),
            content_sha256=_sha256(staged),
            byte_size=staged.stat().st_size,
            mime_type="application/pdf",
            retrieved_at="2026-07-26T12:00:00Z",
            http_status=200,
            adapter_name=self.name,
            adapter_version=self.version,
        )


class FilingAcquisitionTests(unittest.TestCase):
    def _config(self, parent: Path, root_name: str = "wiki") -> tuple[Path, Path]:
        root = parent / root_name
        root.mkdir(parents=True)
        security = root / ".source_catalog" / "security_master"
        security.mkdir(parents=True)
        projects = parent / "projects"
        projects.mkdir(exist_ok=True)
        dayu_config = parent / "dayu-config"
        dayu_config.mkdir(exist_ok=True)
        adapters = {}
        for market, interface in (
            ("cn", "json_command_v1"),
            ("hk", "dayu_cli_v1"),
            ("us", "dayu_cli_v1"),
        ):
            project = projects / market
            project.mkdir(exist_ok=True)
            adapters[market] = {
                "name": f"fake-{market}",
                "version": "1.0.0",
                "interface": interface,
                "project_root": str(project),
                "config_root": None if market == "cn" else str(dayu_config),
                "command": [sys.executable, "-c", "raise SystemExit(99)"],
            }
        config = parent / f"{root_name}.json"
        config.write_text(
            json.dumps(
                {
                    "schema_version": "2.0",
                    "company_wiki_root": str(root),
                    "security_master_root": "${COMPANY_WIKI_ROOT}/.source_catalog/security_master",
                    "staging_root": "${COMPANY_WIKI_ROOT}/.source_catalog/revenue-forecast-staging",
                    "timeout_seconds": 30,
                    "adapters": adapters,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return config, root

    @staticmethod
    def _request(market: str = "US") -> dict:
        return {
            "entity": {"CN": "测试股份", "HK": "測試集團", "US": "ACME Inc."}[market],
            "market": market,
            "security_id": {"CN": "688001", "HK": "01234", "US": "ACME"}[market],
            "document_kind": "annual_report",
            "fiscal_year": 2025,
            # Far enough in the future that the dayu subprocess adapter's
            # real-clock ``retrieved_at`` always satisfies
            # ``filing_date <= captured_date <= as_of_date``. Hard-coding a
            # calendar date rots the moment the clock passes it (this test
            # silently broke two days after the v3.10.0 audit for that reason).
            "as_of_date": (date.today() + timedelta(days=7)).isoformat(),
        }

    @staticmethod
    def _existing(
        root: Path, request: dict, payload: bytes = b"%PDF-1.7\nexisting"
    ) -> Path:
        raw = (
            root
            / "companies"
            / request["entity"]
            / "raw"
            / "financial_reports"
            / "annual"
            / "2026-03-20_sec_existing_annual.pdf"
        )
        raw.parent.mkdir(parents=True)
        raw.write_bytes(payload)
        digest = _sha256(raw)
        sidecar = {
            "schema_version": "1.0",
            "request_id": "urn:revenue-forecast:source-request:sha256:" + "1" * 64,
            "company_name": request["entity"],
            "market": request["market"],
            "security_id": request["security_id"],
            "source_title": f"{request['entity']} 2025 Annual Report",
            "provider": "sec" if request["market"] == "US" else "cninfo",
            "provider_document_id": "existing-2025",
            "source_url": "https://example.test/existing.pdf",
            "document_kind": "annual_report",
            "form_type": "10-K" if request["market"] == "US" else "annual_report",
            "filing_date": "2026-03-20",
            "fiscal_year": 2025,
            "fiscal_period": "FY",
            "language": "en" if request["market"] == "US" else "zh",
            "amended": False,
            "content_sha256": digest,
            "byte_size": raw.stat().st_size,
            "mime_type": "application/pdf",
            "retrieved_at": "2026-07-01T12:00:00Z",
            "adapter_name": "fixture",
            "adapter_version": "1.0.0",
            "etag": None,
            "last_modified": None,
        }
        raw.with_name(raw.name + ".source.json").write_text(
            json.dumps(sidecar, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return raw

    @staticmethod
    def _security_snapshot(root: Path, market: str, records: list[dict]) -> None:
        security = root / ".source_catalog" / "security_master"
        security.mkdir(parents=True, exist_ok=True)
        (security / f"{market.lower()}.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "market": market,
                    "retrieved_at": "2026-07-01T00:00:00Z",
                    "sources": ["https://example.test/security-master"],
                    "record_count": len(records),
                    "records": records,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    @staticmethod
    def _security_record(
        *,
        canonical_name: str = "Advanced Micro Devices, Inc.",
        ticker: str = "AMD",
        aliases: list[str] | None = None,
    ) -> dict:
        return {
            "schema_version": "1.0",
            "canonical_name": canonical_name,
            "market": "US",
            "exchange": "NASDAQ",
            "ticker": ticker,
            "security_id": ticker,
            "aliases": aliases or ["AMD", "Advanced Micro Devices"],
            "active": True,
            "source_name": "SEC test snapshot",
            "source_url": "https://example.test/security-master",
            "source_record_id": f"urn:test:security:{ticker}",
            "identifiers": {"cik": "0000002488"},
        }

    @staticmethod
    def _replace_adapter_command(
        config_path: Path,
        market: str,
        *,
        project_root: Path,
        config_root: Path | None,
        command: list[str],
    ) -> None:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        adapter = payload["adapters"][market.lower()]
        adapter["project_root"] = str(project_root)
        adapter["config_root"] = str(config_root) if config_root else None
        adapter["command"] = command
        config_path.write_text(json.dumps(payload), encoding="utf-8")

    def test_scripts_have_no_company_wiki_runtime_dependency(self) -> None:
        forbidden_modules = {"company_wiki", "filing_fetch"}
        for path in sorted((SKILL_ROOT / "scripts").glob("*.py")):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                imported = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.update(
                            alias.name.split(".", 1)[0] for alias in node.names
                        )
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported.add(node.module.split(".", 1)[0])
                self.assertTrue(forbidden_modules.isdisjoint(imported), imported)
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("company_wiki.source_catalog.cli", text)

    def test_config_root_moves_without_source_project(self) -> None:
        with TemporaryDirectory() as temporary:
            parent = Path(temporary)
            first_config, first = self._config(parent, "wiki-one")
            second_config, second = self._config(parent, "wiki-two")
            self.assertEqual(
                load_acquisition_config(first_config).company_wiki_root, first.resolve()
            )
            self.assertEqual(
                load_acquisition_config(second_config).company_wiki_root,
                second.resolve(),
            )

    def test_default_config_needs_only_the_data_root_not_company_source_config(
        self,
    ) -> None:
        config = load_acquisition_config()
        self.assertTrue(config.company_wiki_root.is_dir())
        self.assertNotEqual(config.schema_version, "1.0")

    def test_config_rejects_staging_outside_data_root(self) -> None:
        with TemporaryDirectory() as temporary:
            parent = Path(temporary)
            config_path, _root = self._config(parent)
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            payload["staging_root"] = str(parent / "outside")
            config_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(FilingAcquisitionError, "escapes"):
                load_acquisition_config(config_path)

    def test_existing_sidecar_is_reused_without_adapter(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, root = self._config(Path(temporary))
            request = self._request()
            raw = self._existing(root, request)
            adapters = {market: _FakeAdapter(market) for market in ("CN", "HK", "US")}
            manager = AcquisitionManager(
                load_acquisition_config(config_path),
                AdapterRegistry.from_mapping(adapters),
            )
            handle = manager.resolve(request, allow_download=False)
            self.assertEqual(Path(handle["canonical_path"]), raw.resolve())
            self.assertTrue(handle["capture_ready"])
            self.assertEqual(sum(item.discover_calls for item in adapters.values()), 0)

    def test_missing_without_authorization_never_invokes_adapter(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, _root = self._config(Path(temporary))
            adapters = {market: _FakeAdapter(market) for market in ("CN", "HK", "US")}
            manager = AcquisitionManager(
                load_acquisition_config(config_path),
                AdapterRegistry.from_mapping(adapters),
            )
            with self.assertRaisesRegex(FilingAcquisitionError, "not reusable"):
                manager.resolve(self._request(), allow_download=False)
            self.assertEqual(sum(item.discover_calls for item in adapters.values()), 0)

    def test_fuzzy_identity_uses_local_snapshot_before_reuse(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, root = self._config(Path(temporary))
            self._security_snapshot(root, "US", [self._security_record()])
            request = self._request()
            request["entity"] = "Advanced Micro Devices, Inc."
            request["security_id"] = "AMD"
            raw = self._existing(root, request)
            adapters = {market: _FakeAdapter(market) for market in ("CN", "HK", "US")}
            manager = AcquisitionManager(
                load_acquisition_config(config_path),
                AdapterRegistry.from_mapping(adapters),
            )
            handle = manager.resolve(
                {
                    "company_query": "Advanced Micro Device",
                    "market": "US",
                    "document_kind": "annual_report",
                    "fiscal_year": 2025,
                    "as_of_date": "2026-07-26",
                },
                allow_download=False,
            )
            self.assertEqual(Path(handle["canonical_path"]), raw.resolve())
            self.assertEqual(handle["company_identity"]["security_id"], "AMD")
            self.assertTrue(handle["company_identity"]["verified"])
            self.assertEqual(sum(item.discover_calls for item in adapters.values()), 0)

    def test_ambiguous_identity_stops_before_adapter(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, root = self._config(Path(temporary))
            records = [
                self._security_record(
                    canonical_name="Alpha Holdings", ticker="ALP", aliases=["Shared"]
                ),
                self._security_record(
                    canonical_name="Beta Holdings", ticker="BET", aliases=["Shared"]
                ),
            ]
            self._security_snapshot(root, "US", records)
            adapters = {market: _FakeAdapter(market) for market in ("CN", "HK", "US")}
            manager = AcquisitionManager(
                load_acquisition_config(config_path),
                AdapterRegistry.from_mapping(adapters),
            )
            with self.assertRaisesRegex(FilingAcquisitionError, "ambiguous"):
                manager.resolve(
                    {
                        "company_query": "Shared",
                        "market": "US",
                        "document_kind": "annual_report",
                        "fiscal_year": 2025,
                        "as_of_date": "2026-07-26",
                    },
                    allow_download=True,
                )
            self.assertEqual(sum(item.discover_calls for item in adapters.values()), 0)

    def test_download_routes_exactly_once_by_market(self) -> None:
        for market in ("CN", "HK", "US"):
            with self.subTest(market=market), TemporaryDirectory() as temporary:
                config_path, _root = self._config(Path(temporary))
                adapters = {value: _FakeAdapter(value) for value in ("CN", "HK", "US")}
                manager = AcquisitionManager(
                    load_acquisition_config(config_path),
                    AdapterRegistry.from_mapping(adapters),
                )
                handle = manager.resolve(self._request(market), allow_download=True)
                self.assertTrue(handle["capture_ready"])
                self.assertEqual(adapters[market].discover_calls, 1)
                self.assertEqual(adapters[market].fetch_calls, 1)
                self.assertEqual(
                    sum(
                        item.discover_calls
                        for key, item in adapters.items()
                        if key != market
                    ),
                    0,
                )

    def test_cn_json_cli_contract_runs_in_an_external_process(self) -> None:
        with TemporaryDirectory() as temporary:
            parent = Path(temporary)
            config_path, _root = self._config(parent)
            project = parent / "stockinfo"
            project.mkdir()
            script = project / "fake_stockinfo.py"
            script.write_text(
                """
import hashlib
import json
from pathlib import Path
import sys

action = sys.argv[1]
payload = json.load(sys.stdin)
adapter = {"name": "fake-cn", "version": "1.0.0"}
if action == "discover":
    output = {
        "schema_version": "1.0",
        "status": "ok",
        "adapter": adapter,
        "candidates": [{
            "candidate_id": "cninfo:2025",
            "provider": "cninfo",
            "provider_document_id": "2025",
            "market": "CN",
            "title": "测试股份 2025 年年度报告",
            "source_url": "https://example.test/cn.pdf",
            "document_kind": "annual_report",
            "filing_date": "2026-03-20",
            "fiscal_year": 2025,
            "form_type": "annual_report",
            "language": "zh"
        }]
    }
else:
    staging = Path(sys.argv[sys.argv.index("--staging-dir") + 1])
    staging.mkdir(parents=True, exist_ok=True)
    source = staging / "cn.pdf"
    source.write_bytes(b"%PDF-1.7\\nCN CLI")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    output = {
        "schema_version": "1.0",
        "status": "ok",
        "adapter": adapter,
        "receipt": {
            "candidate_id": payload["candidate_id"],
            "provider": payload["provider"],
            "provider_document_id": payload["provider_document_id"],
            "source_url": payload["source_url"],
            "staged_path": str(source),
            "content_sha256": digest,
            "byte_size": source.stat().st_size,
            "mime_type": "application/pdf",
            "retrieved_at": "2026-07-26T12:00:00Z",
            "http_status": 200,
            "adapter_name": adapter["name"],
            "adapter_version": adapter["version"]
        }
    }
json.dump(output, sys.stdout, ensure_ascii=False)
""".strip(),
                encoding="utf-8",
            )
            self._replace_adapter_command(
                config_path,
                "CN",
                project_root=project,
                config_root=None,
                command=[sys.executable, str(script)],
            )
            handle = resolve_filing(
                request=self._request("CN"),
                config_path=config_path,
                allow_download=True,
            )
            self.assertEqual(handle["provider"], "cninfo")
            self.assertEqual(handle["collector_name"], "fake-cn")
            self.assertEqual(handle["acquisition_status"], "downloaded_new")

    def test_hk_and_us_dayu_cli_contracts_run_in_external_processes(self) -> None:
        for market in ("HK", "US"):
            with self.subTest(market=market), TemporaryDirectory() as temporary:
                parent = Path(temporary)
                config_path, _root = self._config(parent)
                project = parent / "dayu"
                project.mkdir()
                dayu_config = parent / "dayu-config-real"
                dayu_config.mkdir()
                script = project / "fake_dayu.py"
                script.write_text(
                    """
import hashlib
import json
from pathlib import Path
import sys

args = sys.argv[1:]
base = Path(args[args.index("--base") + 1])
ticker = args[args.index("--ticker") + 1]
forms = args[args.index("--forms") + 1:args.index("--start")]
market = "HK" if ticker == "01234" else "US"
filing = base / "portfolio" / ticker / "filings" / "2025"
filing.mkdir(parents=True, exist_ok=True)
source = filing / "annual.pdf"
source.write_bytes(b"%PDF-1.7\\n" + market.encode("ascii") + b" DAYU CLI")
digest = hashlib.sha256(source.read_bytes()).hexdigest()
entry = {
    "name": source.name,
    "size": source.stat().st_size,
    "sha256": digest,
    "content_type": "application/pdf",
    "source_url": "https://example.test/dayu.pdf"
}
meta = {
    "is_deleted": False,
    "ingest_complete": True,
    "fiscal_year": 2025,
    "fiscal_period": "FY",
    "form_type": "FY" if market == "HK" else "10-K",
    "filing_date": "2026-03-20",
    "source_title": ticker + " Annual Report",
    "document_id": "fake-dayu-" + ticker
}
if market == "HK":
    entry["source"] = "original"
    meta.update({
        "source_provider": "hkexnews",
        "source_id": "HK-2025",
        "source_url": entry["source_url"],
        "source_language": "zh",
        "files": [entry]
    })
else:
    meta.update({
        "accession_number": "0000000000-26-000001",
        "primary_document": source.name,
        "files": [entry]
    })
(filing / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
""".strip(),
                    encoding="utf-8",
                )
                self._replace_adapter_command(
                    config_path,
                    market,
                    project_root=project,
                    config_root=dayu_config,
                    command=[sys.executable, str(script)],
                )
                handle = resolve_filing(
                    request=self._request(market),
                    config_path=config_path,
                    allow_download=True,
                )
                self.assertEqual(
                    handle["provider"], "hkexnews" if market == "HK" else "sec"
                )
                self.assertEqual(
                    handle["collector_name"],
                    "fake-hk" if market == "HK" else "fake-us",
                )
                self.assertEqual(handle["acquisition_status"], "downloaded_new")

    def test_second_identical_import_reuses_canonical_bytes(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, root = self._config(Path(temporary))
            adapters = {market: _FakeAdapter(market) for market in ("CN", "HK", "US")}
            config = load_acquisition_config(config_path)
            first = AcquisitionManager(
                config, AdapterRegistry.from_mapping(adapters)
            ).resolve(self._request(), allow_download=True)
            raw_before = tuple(
                path
                for path in (root / "companies").rglob("*")
                if path.is_file() and not path.name.endswith(".source.json")
            )
            second = AcquisitionManager(
                config,
                AdapterRegistry.from_mapping(
                    {market: _FakeAdapter(market) for market in ("CN", "HK", "US")}
                ),
            ).resolve(self._request(), allow_download=True)
            raw_after = tuple(
                path
                for path in (root / "companies").rglob("*")
                if path.is_file() and not path.name.endswith(".source.json")
            )
            self.assertEqual(first["snapshot_sha256"], second["snapshot_sha256"])
            self.assertEqual(raw_before, raw_after)

    def test_download_hash_reuses_legacy_raw_without_sidecar(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, root = self._config(Path(temporary))
            request = self._request()
            legacy = root / "companies" / request["entity"] / "raw" / "legacy-name.pdf"
            legacy.parent.mkdir(parents=True)
            payload = b"%PDF-1.7\nlegacy exact bytes"
            legacy.write_bytes(payload)
            adapters = {
                market: _FakeAdapter(market, payload=payload)
                for market in ("CN", "HK", "US")
            }
            manager = AcquisitionManager(
                load_acquisition_config(config_path),
                AdapterRegistry.from_mapping(adapters),
            )
            handle = manager.resolve(request, allow_download=True)
            raw_files = tuple(
                path
                for path in (root / "companies").rglob("*")
                if path.is_file() and not path.name.endswith(".source.json")
            )
            self.assertEqual(raw_files, (legacy.resolve(),))
            self.assertEqual(Path(handle["canonical_path"]), legacy.resolve())
            self.assertEqual(
                handle["acquisition_status"], "deduplicated_after_download"
            )

    def test_adapter_cannot_escape_request_specific_staging(self) -> None:
        class EscapingAdapter(_FakeAdapter):
            def __init__(self, outside: Path) -> None:
                super().__init__("US")
                self.outside = outside

            def fetch(
                self, candidate: DownloadCandidate, staging_dir: Path
            ) -> DownloadReceipt:
                self.outside.parent.mkdir(parents=True, exist_ok=True)
                self.outside.write_bytes(self.payload)
                return DownloadReceipt(
                    candidate_id=candidate.candidate_id,
                    provider=candidate.provider,
                    provider_document_id=candidate.provider_document_id,
                    source_url=candidate.source_url,
                    staged_path=str(self.outside),
                    content_sha256=_sha256(self.outside),
                    byte_size=self.outside.stat().st_size,
                    mime_type="application/pdf",
                    retrieved_at="2026-07-26T12:00:00Z",
                    http_status=200,
                    adapter_name=self.name,
                    adapter_version=self.version,
                )

        with TemporaryDirectory() as temporary:
            config_path, _root = self._config(Path(temporary))
            config = load_acquisition_config(config_path)
            adapters = {
                "CN": _FakeAdapter("CN"),
                "HK": _FakeAdapter("HK"),
                "US": EscapingAdapter(config.staging_root / "outside-request.pdf"),
            }
            with self.assertRaisesRegex(FilingAcquisitionError, "escapes"):
                AcquisitionManager(
                    config, AdapterRegistry.from_mapping(adapters)
                ).resolve(self._request(), allow_download=True)

    def test_capture_after_as_of_is_not_reused(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, root = self._config(Path(temporary))
            request = self._request()
            self._existing(root, request)
            request["as_of_date"] = "2026-06-30"
            with self.assertRaisesRegex(FilingAcquisitionError, "not reusable"):
                resolve_filing(
                    request=request,
                    config_path=config_path,
                    allow_download=False,
                )

    def test_malformed_relevant_sidecar_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, root = self._config(Path(temporary))
            request = self._request()
            raw = self._existing(root, request)
            raw.with_name(raw.name + ".source.json").write_text(
                "{not-json", encoding="utf-8"
            )
            with self.assertRaisesRegex(FilingAcquisitionError, "invalid provenance"):
                resolve_filing(
                    request=request,
                    config_path=config_path,
                    allow_download=True,
                )

    def test_error_redaction_hides_common_secret_forms(self) -> None:
        redacted = _redact("Authorization: Bearer-secret API_KEY=abc123 token=xyz987")
        self.assertNotIn("Bearer-secret", redacted)
        self.assertNotIn("abc123", redacted)
        self.assertNotIn("xyz987", redacted)
        self.assertGreaterEqual(redacted.count("[REDACTED]"), 3)

    def test_immutable_sidecar_refuses_conflicting_rewrite(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.pdf.source.json"
            CanonicalSourceWriter._write_immutable(path, {"value": 1})
            with self.assertRaisesRegex(FilingAcquisitionError, "immutable"):
                CanonicalSourceWriter._write_immutable(path, {"value": 2})

    def test_tampered_sidecar_fails_closed(self) -> None:
        with TemporaryDirectory() as temporary:
            config_path, root = self._config(Path(temporary))
            request = self._request()
            raw = self._existing(root, request)
            raw.write_bytes(b"tampered")
            with self.assertRaisesRegex(FilingAcquisitionError, "SHA-256"):
                resolve_filing(
                    request=request,
                    config_path=config_path,
                    allow_download=False,
                )

    def test_isolated_copy_runs_without_company_wiki_source_tree(self) -> None:
        with TemporaryDirectory() as temporary:
            parent = Path(temporary)
            copied = parent / "revenue-forecast"
            shutil.copytree(SKILL_ROOT / "scripts", copied / "scripts")
            config_path, root = self._config(parent, "isolated-wiki")
            request = self._request()
            request_path = parent / "request.json"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            environment = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONUTF8": "1",
                "PYTHONPATH": str(copied / "scripts"),
                "TEMP": os.environ.get("TEMP", temporary),
                "TMP": os.environ.get("TMP", temporary),
            }
            completed = subprocess.run(
                [
                    sys.executable,
                    str(copied / "scripts" / "filing_acquisition.py"),
                    "--config",
                    str(config_path),
                    "--request-file",
                    str(request_path),
                ],
                cwd=copied,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                timeout=30,
            )
            # Phase 6 B1 (F-04): the deprecated acquisition CLI must hard-fail
            # and must never produce a capture-ready handle; filing-fetch is the
            # single canonical owner.
            self.assertEqual(
                completed.returncode, 3, completed.stderr or completed.stdout
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "error")
            self.assertIn("filing_fetch_client", payload["error"])
            self.assertNotIn("handle", payload)

    def test_deprecated_acquisition_cli_hard_fails_even_with_allow_download(
        self,
    ) -> None:
        # Phase 6 B1 RED (F-04): even with --allow-download the deprecated CLI
        # must hard-fail and never route a download through the old owner.
        with TemporaryDirectory() as temporary:
            parent = Path(temporary)
            copied = parent / "revenue-forecast"
            shutil.copytree(SKILL_ROOT / "scripts", copied / "scripts")
            config_path, root = self._config(parent, "isolated-wiki")
            request_path = parent / "request.json"
            request_path.write_text(json.dumps(self._request()), encoding="utf-8")
            environment = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONUTF8": "1",
                "PYTHONPATH": str(copied / "scripts"),
                "TEMP": os.environ.get("TEMP", temporary),
                "TMP": os.environ.get("TMP", temporary),
            }
            completed = subprocess.run(
                [
                    sys.executable,
                    str(copied / "scripts" / "filing_acquisition.py"),
                    "--allow-download",
                    "--config",
                    str(config_path),
                    "--request-file",
                    str(request_path),
                ],
                cwd=copied,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                timeout=30,
            )
            self.assertEqual(completed.returncode, 3)
            self.assertIn("deprecated", (completed.stdout + completed.stderr).lower())


if __name__ == "__main__":
    unittest.main()
