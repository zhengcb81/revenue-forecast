"""Owner-managed, append-only index of exact revenue-forecast publications.

The catalog is deliberately separate from ``publication_registry``: that
registry proves an input/result publication, whereas this one records a
company/run/attempt/report relationship.  Queries consult only this index and
then open the one registered artifact by ID.  No query discovers artifacts by
walking ``delivery`` or ``output``.

Only owner code may call ``add_records``.  The public CLI accepts IDs and fixed
commands, never a filesystem path or SQL.  Artifact locators stay private in
the index and every read rechecks their byte SHA and declared schema.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any, Callable

from model_registry import MODEL_REGISTRY
from contracts.constants import MONETARY_DIMENSIONS
from owner_atomic_io import replace_file_bytes
from owner_file_lock import OwnerFileLock
from publication_registry import RegistryError, canonical_sha256, validate_registry_text
from revenue_backtest import validate_snapshot
from revenue_report import validate_published_forecast
from schema_compatibility import validating_engine_allowed
from research.input_quantities import (
    money_currency, money_scale_factor, money_unit_currency, money_unit_scale_factor,
)


SCHEMA_VERSION = "rf-report-catalog/1"
ENV_CATALOG = "REVENUE_REPORT_CATALOG"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SOURCE_REF_FIELDS = frozenset(
    {"document_id", "source_id", "content_sha256", "byte_size", "mime_type", "schema_version"}
)
MAX_ARTIFACT_BYTES = 64 * 1024 * 1024


class CatalogError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise CatalogError(code, message)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bounded_bytes(path: Path) -> bytes:
    """Inspect size first, then read at most the limit plus one byte."""
    _require(path.stat().st_size <= MAX_ARTIFACT_BYTES, "artifact_too_large",
             "artifact exceeds catalog limit")
    with path.open("rb") as handle:
        data = handle.read(MAX_ARTIFACT_BYTES + 1)
    _require(len(data) <= MAX_ARTIFACT_BYTES, "artifact_too_large",
             "artifact exceeds catalog limit")
    return data


def _frozen_reporting_scale(result: dict[str, Any]) -> int:
    """Resolve only the owner's supported scale spellings, without FX."""
    factor = money_scale_factor(result.get("unit"))
    _require(factor is not None, "artifact_unit_incompatible",
             "frozen report monetary unit has no supported owner scale")
    exponent = Decimal(str(factor)).normalize().as_tuple()
    _require(exponent.sign == 0 and exponent.digits == (1,) and
             isinstance(exponent.exponent, int), "artifact_unit_incompatible",
             "frozen report monetary unit is not an exact decimal scale")
    assert isinstance(exponent.exponent, int)
    return exponent.exponent


def _clean_id(value: Any, name: str) -> str:
    _require(isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,191}", value)),
             "invalid_id", f"{name} must be an opaque ID")
    return value


def _date(value: Any, name: str) -> str:
    _require(isinstance(value, str), "invalid_date", f"{name} is required")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CatalogError("invalid_date", f"{name} must be ISO date or timestamp") from exc
    return value


class ReportCatalog:
    def __init__(self, *, root: Path | None = None, catalog_file: Path | None = None):
        self.root = (root or Path(__file__).resolve().parents[1]).resolve()
        configured = os.environ.get(ENV_CATALOG)
        managed_root = (self.root / "artifacts" / "report_catalog").resolve()
        if catalog_file is not None:
            # A trusted owner caller or isolated test can inject its own file.
            self.file = catalog_file.resolve()
        else:
            candidate = Path(configured).expanduser() if configured else managed_root / "catalog.jsonl"
            self.file = candidate.resolve()
            _require(managed_root.is_relative_to(self.root)
                     and self.file.is_relative_to(managed_root) and self.file.suffix == ".jsonl",
                     "catalog_path_forbidden", "catalog path must stay in owner-managed catalog root")

    def _artifact_path(self, ref: dict[str, Any]) -> Path:
        relative = ref.get("relative_path")
        _require(isinstance(relative, str) and bool(relative) and "\\" not in relative,
                 "invalid_artifact_ref", "registered artifact locator is invalid")
        assert isinstance(relative, str)
        parts = PurePosixPath(relative)
        _require(not parts.is_absolute() and not any(part in {"..", "."} for part in parts.parts),
                 "invalid_artifact_ref", "registered artifact locator is invalid")
        path = (self.root / Path(*parts.parts)).resolve()
        _require(path.is_relative_to(self.root), "invalid_artifact_ref",
                 "registered artifact escapes owner root")
        return path

    def artifact_ref(self, path: Path) -> dict[str, Any]:
        """Construct a private locator from an explicit owner-selected file."""
        resolved = path.resolve()
        _require(resolved.is_relative_to(self.root), "invalid_artifact_ref",
                 "artifact must stay under owner root")
        data = _bounded_bytes(resolved)
        return {"relative_path": resolved.relative_to(self.root).as_posix(),
                "bytes_sha256": _sha(data)}

    def _read_artifact(self, ref: dict[str, Any]) -> bytes:
        path = self._artifact_path(ref)
        try:
            data = _bounded_bytes(path)
        except CatalogError:
            raise
        except OSError as exc:
            raise CatalogError("artifact_unavailable", "registered artifact is unavailable") from exc
        _require(_sha(data) == ref.get("bytes_sha256"), "artifact_sha_mismatch",
                 "registered artifact byte SHA changed")
        return data

    def _read_json(self, ref: dict[str, Any]) -> dict[str, Any]:
        try:
            value = json.loads(self._read_artifact(ref))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise CatalogError("artifact_invalid_json", "registered artifact is not JSON") from exc
        _require(isinstance(value, dict), "artifact_invalid_json", "registered artifact must be an object")
        return value

    def _catalog_bytes(self) -> bytes:
        try:
            return self.file.read_bytes()
        except FileNotFoundError:
            return b""
        except OSError as exc:
            raise CatalogError("catalog_unavailable", "catalog cannot be read") from exc

    def _entries(self, raw_bytes: bytes | None = None) -> list[dict[str, Any]]:
        data = self._catalog_bytes() if raw_bytes is None else raw_bytes
        try:
            lines = data.decode("utf-8").splitlines()
        except UnicodeError as exc:
            raise CatalogError("catalog_corrupt", "catalog is not UTF-8") from exc
        entries: list[dict[str, Any]] = []
        previous: str | None = None
        for number, raw in enumerate(lines, 1):
            _require(bool(raw), "catalog_corrupt", f"blank catalog line {number}")
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise CatalogError("catalog_corrupt", f"invalid catalog line {number}") from exc
            _require(isinstance(entry, dict), "catalog_corrupt", f"invalid catalog line {number}")
            claimed = entry.get("line_sha256")
            payload = {key: value for key, value in entry.items() if key != "line_sha256"}
            _require(canonical_sha256(payload) == claimed, "catalog_corrupt",
                     f"catalog line {number} hash mismatch")
            _require(entry.get("prev_line_sha256") == previous, "catalog_corrupt",
                     f"catalog line {number} chain mismatch")
            _require(entry.get("schema_version") == SCHEMA_VERSION, "catalog_incompatible",
                     f"catalog line {number} schema unsupported")
            previous = claimed
            entries.append(entry)
        return entries

    def _index(self) -> tuple[dict[str, dict], dict[tuple[str, str], dict], dict[str, dict], str]:
        return self._index_entries(self._entries())

    def _index_entries(self, entries: list[dict[str, Any]]) -> tuple[dict[str, dict], dict[tuple[str, str], dict], dict[str, dict], str]:
        runs: dict[str, dict] = {}
        attempts: dict[tuple[str, str], dict] = {}
        reports: dict[str, dict] = {}
        for entry in entries:
            for run in entry.get("runs", []):
                run_id = _clean_id(run.get("run_id"), "run_id")
                _require(run_id not in runs, "catalog_corrupt", "duplicate run ID in catalog")
                runs[run_id] = run
            for attempt in entry.get("attempts", []):
                key = (_clean_id(attempt.get("run_id"), "run_id"),
                       _clean_id(attempt.get("attempt_id"), "attempt_id"))
                _require(key not in attempts, "catalog_corrupt", "duplicate attempt ID in catalog")
                attempts[key] = attempt
            for report in entry.get("reports", []):
                report_id = _clean_id(report.get("report_id"), "report_id")
                _require(report_id not in reports, "catalog_corrupt", "duplicate report ID in catalog")
                reports[report_id] = report
        for (run_id, _), attempt in attempts.items():
            _require(run_id in runs, "catalog_corrupt", "attempt has no catalog run")
            _require(attempt.get("status") in {"queued", "running", "succeeded", "failed", "cancelled", "unknown"},
                     "catalog_corrupt", "attempt status invalid")
        for report in reports.values():
            report_run_id = _clean_id(report.get("run_id"), "run_id")
            report_attempt_id = _clean_id(report.get("attempt_id"), "attempt_id")
            _require(report_run_id in runs, "catalog_corrupt", "report has no catalog run")
            _require((report_run_id, report_attempt_id) in attempts, "catalog_corrupt",
                     "report has no catalog attempt")
        self._verify_attempt_report_links(attempts, reports, code="catalog_corrupt")
        return runs, attempts, reports, entries[-1]["line_sha256"] if entries else "0" * 64

    @staticmethod
    def _verify_attempt_report_links(attempts: dict[tuple[str, str], dict],
                                     reports: dict[str, dict], *, code: str) -> None:
        linked: dict[tuple[str, str], set[str]] = {key: set() for key in attempts}
        for report_id, report in reports.items():
            key = (_clean_id(report.get("run_id"), "run_id"),
                   _clean_id(report.get("attempt_id"), "attempt_id"))
            _require(key in linked, code, "report has no matching attempt")
            linked[key].add(report_id)
        for key, attempt in attempts.items():
            declared = attempt.get("report_ids")
            _require(isinstance(declared, list) and
                     all(isinstance(value, str) for value in declared) and
                     len(declared) == len(set(declared)) and
                     set(declared) == linked[key],
                     code, "attempt report IDs disagree with catalog reports")

    def _validate_report_artifact(self, record: dict[str, Any]) -> dict[str, Any]:
        result = self._read_json(record["forecast_artifact"])
        _require(result.get("schema_version") == record.get("schema_version"),
                 "artifact_schema_mismatch", "report emitting schema changed")
        _require(result.get("engine_version") == record.get("engine_version"),
                 "artifact_schema_mismatch", "report emitting engine changed")
        currency = result.get("currency")
        _require(isinstance(currency, str) and bool(currency.strip()) and
                 record.get("reporting_currency") == currency,
                 "artifact_currency_mismatch",
                 "catalog currency differs from the frozen report currency")
        frozen_scale = _frozen_reporting_scale(result)
        _require(type(record.get("reporting_scale")) is int and
                 record["reporting_scale"] == frozen_scale,
                 "artifact_scale_mismatch",
                 "catalog scale differs from the frozen report monetary unit")
        _require(result.get("company_name") == record.get("company", {}).get("display_name"),
                 "artifact_identity_mismatch", "report company identity changed")
        _require(result.get("as_of_date") == record.get("information_as_of"),
                 "artifact_identity_mismatch", "report information date changed")
        _require(result.get("input_sha256") == record.get("input_sha256") and
                 result.get("result_sha256") == record.get("result_sha256"),
                 "artifact_sha_mismatch", "report embedded anchor changed")
        if record.get("status") in {"validated", "published"}:
            _require(validating_engine_allowed(record["schema_version"], record["engine_version"], "output"),
                     "schema_incompatible", "emitting schema and engine are incompatible")
            source_input = self._read_json(record["input_artifact"])
            _require(canonical_sha256(source_input) == record["input_sha256"],
                     "artifact_sha_mismatch", "bound input SHA changed")
            _require(canonical_sha256({k: v for k, v in result.items() if k != "result_sha256"}) ==
                     record["result_sha256"], "artifact_sha_mismatch", "result payload SHA changed")
            try:
                validate_published_forecast(result, source_input)
            except Exception as exc:
                raise CatalogError("report_validation_failed", "strong forecast validation failed") from exc
        for name in ("markdown_artifact", "snapshot_artifact"):
            ref = record.get(name)
            if ref is not None:
                if name == "snapshot_artifact":
                    snapshot = self._read_json(ref)
                    _require(snapshot.get("snapshot_id") == record.get("snapshot_id"),
                             "artifact_identity_mismatch", "snapshot ID changed")
                    _require(snapshot.get("input_sha256") == record.get("input_sha256") and
                             snapshot.get("forecast_result", {}).get("result_sha256") ==
                             record.get("result_sha256"), "artifact_identity_mismatch",
                             "snapshot is not a representation of this report")
                    try:
                        validate_snapshot(snapshot)
                    except Exception as exc:
                        raise CatalogError("snapshot_validation_failed", "frozen snapshot validation failed") from exc
                else:
                    self._read_artifact(ref)
        return result

    def _validate_attempt_source(self, attempt: dict[str, Any]) -> None:
        evidence = attempt.get("source_evidence")
        _require(isinstance(evidence, dict), "attempt_unverified", "attempt lacks owner evidence")
        assert isinstance(evidence, dict)
        kind = evidence.get("kind")
        if kind == "native_calls_jsonl":
            lines = self._read_artifact(evidence["artifact"]).decode("utf-8").splitlines()
            matches = [json.loads(line) for line in lines if line]
            matches = [line for line in matches if line.get("capture", {}).get("capture_id") ==
                       evidence.get("capture_id")]
            _require(len(matches) == 1, "attempt_unverified", "attempt capture not unique")
            capture = matches[0].get("capture", {})
            succeeded = matches[0].get("capture_exit") == 0 and capture.get("exit_code") == 0 and not capture.get("timed_out")
            _require((attempt["status"] == "succeeded") == succeeded,
                     "attempt_unverified", "attempt status contradicts recorder")
            if not succeeded:
                _require(attempt["status"] in {"failed", "cancelled", "unknown"},
                         "attempt_unverified", "failed capture status invalid")
        elif kind == "attempt_receipt_json":
            receipt = self._read_json(evidence["artifact"])
            _require(receipt.get("attempt_id") == attempt["attempt_id"],
                     "attempt_unverified", "attempt receipt ID mismatch")
            _require(receipt.get("status") == attempt["status"],
                     "attempt_unverified", "attempt receipt status mismatch")
        elif kind == "rf_job_record":
            # Kept behind the catalog owner boundary: only the RF-owned job
            # importer defines and validates this evidence format.
            from report_catalog_rf_job_import import _validate_job_attempt
            _validate_job_attempt(self, attempt)
        else:
            raise CatalogError("attempt_unverified", "unsupported owner attempt evidence")
        if attempt["status"] in {"failed", "cancelled"}:
            _require(bool(attempt.get("error_code")), "attempt_unverified", "failed attempt needs error code")

    def add_records(self, *, runs: list[dict] | None = None,
                    attempts: list[dict] | None = None,
                    reports: list[dict] | None = None,
                    before_append: Callable[[], None] | None = None) -> dict[str, Any]:
        """Append one verified batch; an optional trusted guard runs under its lock.

        The guard is owner-installed Python code, never a public DTO. It runs
        after all local validation and staging, immediately before the
        atomic replacement. It cannot make two independent owners atomic.
        """
        _require(before_append is None or callable(before_append),
                 "invalid_admission_guard", "pre-append guard must be callable")
        self.file.parent.mkdir(parents=True, exist_ok=True)
        lock = OwnerFileLock(self.file.with_name(self.file.name + ".lock"))
        if not lock.acquire():
            raise CatalogError("catalog_busy", "another catalog registration is active")
        try:
            if before_append is None:
                return self._add_records_locked(runs=runs, attempts=attempts, reports=reports)
            return self._add_records_locked(runs=runs, attempts=attempts, reports=reports,
                                            before_append=before_append)
        finally:
            lock.release()

    def _add_records_locked(self, *, runs: list[dict] | None = None,
                            attempts: list[dict] | None = None,
                            reports: list[dict] | None = None,
                            before_append: Callable[[], None] | None = None) -> dict[str, Any]:
        runs, attempts, reports = runs or [], attempts or [], reports or []
        _require(bool(runs or attempts or reports), "empty_batch", "catalog batch is empty")
        previous_bytes = self._catalog_bytes()
        entries = self._entries(previous_bytes)
        old_runs, old_attempts, old_reports, _ = self._index_entries(entries)
        next_runs, next_attempts, next_reports = dict(old_runs), dict(old_attempts), dict(old_reports)
        for run in runs:
            key = _clean_id(run.get("run_id"), "run_id")
            _require(key not in next_runs, "immutable_id", "run ID already registered")
            company = run.get("company", {})
            _clean_id(company.get("entity_id"), "entity_id")
            if company.get("analysis_subject_id") is not None:
                _clean_id(company["analysis_subject_id"], "analysis_subject_id")
            _require(company.get("resolution_status") == "resolved" and bool(company.get("display_name")),
                     "unresolved_identity", "run needs a resolved canonical company")
            _date(run.get("source_as_of"), "source_as_of")
            _date(run.get("created_at"), "created_at")
            next_runs[key] = run
        for attempt in attempts:
            attempt_key = (_clean_id(attempt.get("run_id"), "run_id"),
                           _clean_id(attempt.get("attempt_id"), "attempt_id"))
            _require(attempt_key not in next_attempts, "immutable_id", "attempt ID already registered")
            _require(attempt_key[0] in next_runs, "missing_run", "attempt has no registered run")
            _require(attempt.get("status") in {"queued", "running", "succeeded", "failed", "cancelled", "unknown"},
                     "invalid_attempt", "attempt status invalid")
            self._validate_attempt_source(attempt)
            next_attempts[attempt_key] = attempt
        for report in reports:
            key = _clean_id(report.get("report_id"), "report_id")
            _require(key not in next_reports, "immutable_id", "report ID already registered")
            run_id = _clean_id(report.get("run_id"), "run_id")
            attempt_id = _clean_id(report.get("attempt_id"), "attempt_id")
            _require(run_id in next_runs and (run_id, attempt_id) in next_attempts,
                     "missing_attempt", "report has no registered run and attempt")
            _require(next_attempts[(run_id, attempt_id)]["status"] == "succeeded",
                     "invalid_report", "report cannot bind to unsuccessful attempt")
            _require(report.get("company") == next_runs[run_id]["company"],
                     "artifact_identity_mismatch", "report canonical company differs from run")
            _require(report.get("status") in {"validated", "published", "legacy"},
                     "invalid_report", "report status invalid")
            if report["status"] == "legacy":
                _require(bool(report.get("missing_reason")), "invalid_report",
                         "legacy report needs missing reason")
            self._validate_report_artifact(report)
            next_reports[key] = report
        self._verify_attempt_report_links(next_attempts, next_reports,
                                          code="attempt_report_mismatch")
        payload = {"schema_version": SCHEMA_VERSION, "registered_at": _utc_now(),
                   "runs": runs, "attempts": attempts, "reports": reports,
                   "prev_line_sha256": entries[-1]["line_sha256"] if entries else None}
        line = {**payload, "line_sha256": canonical_sha256(payload)}
        serialized = json.dumps(line, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
        try:
            separator = b"\n" if previous_bytes and not previous_bytes.endswith(b"\n") else b""
            replace_file_bytes(self.file, previous_bytes + separator + serialized.encode("utf-8"),
                               before_replace=before_append)
        except OSError as exc:
            raise CatalogError("catalog_unavailable", "catalog append failed") from exc
        return {"schema_version": SCHEMA_VERSION, "catalog_revision": line["line_sha256"],
                "registered": {"runs": [r["run_id"] for r in runs],
                               "attempts": [a["attempt_id"] for a in attempts],
                               "reports": [r["report_id"] for r in reports]}}

    def _snapshot(self, revision: str, *, run_id: str | None = None,
                  state: str = "available", reasons: list[str] | None = None) -> dict:
        now = _utc_now()
        return {"owner": "revenue-forecast", "schema_version": SCHEMA_VERSION,
                "revision": revision, "run_id": run_id, "generated_at": None,
                "data_as_of": None, "retrieved_at": now, "state": state,
                "reason_codes": reasons or [], "capabilities": ["read", "exact_report", "calculation"]}

    @staticmethod
    def _page(items: list[dict], revision: str, *, cursor: str | None,
              limit: int, filter_key: str) -> tuple[list[dict], dict]:
        _require(1 <= limit <= 100, "invalid_limit", "limit must be 1..100")
        offset = 0
        if cursor:
            try:
                value = json.loads(base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4)))
            except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
                raise CatalogError("invalid_cursor", "cursor is invalid") from exc
            _require(isinstance(value, dict), "invalid_cursor", "cursor is invalid")
            _require(value == {"revision": revision, "filter": filter_key, "offset": value.get("offset")}
                     and isinstance(value.get("offset"), int) and value["offset"] >= 0,
                     "stale_cursor", "cursor does not match catalog snapshot and filter")
            offset = value["offset"]
        selected = items[offset:offset + limit]
        next_offset = offset + len(selected)
        next_cursor = None
        if next_offset < len(items):
            payload = json.dumps({"revision": revision, "filter": filter_key,
                                  "offset": next_offset}, sort_keys=True).encode("utf-8")
            next_cursor = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
        return selected, {"next_cursor": next_cursor, "snapshot_id": revision,
                          "total": len(items), "total_status": "exact"}

    @staticmethod
    def _public_attempt(attempt: dict) -> dict:
        return {key: attempt.get(key) for key in
                ("attempt_id", "status", "started_at", "ended_at", "report_ids", "error_code")}

    def get_attempt(self, run_id: str, attempt_id: str) -> dict:
        runs, attempts, reports, revision = self._index()
        key = (_clean_id(run_id, "run_id"), _clean_id(attempt_id, "attempt_id"))
        _require(key in attempts, "not_found", "attempt ID is not registered")
        attempt = attempts[key]
        self._validate_attempt_source(attempt)
        linked = sorted(r["report_id"] for r in reports.values()
                        if r.get("run_id") == run_id and r.get("attempt_id") == attempt_id)
        _require(linked == sorted(attempt.get("report_ids", [])), "catalog_corrupt",
                 "attempt report IDs disagree with catalog")
        output = {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                  "run_id": run_id, "attempt": self._public_attempt(attempt)}
        _assert_pathless(output)
        return output

    def _run_view(self, run: dict, attempts: dict, reports: dict, revision: str) -> dict:
        run_id = run["run_id"]
        rows = [self._public_attempt(a) for (rid, _), a in attempts.items() if rid == run_id]
        rows.sort(key=lambda row: (row.get("started_at") or "", row["attempt_id"]))
        for row in rows:
            self._validate_attempt_source(attempts[(run_id, row["attempt_id"])])
            actual = sorted(r["report_id"] for r in reports.values() if
                            r.get("run_id") == run_id and r.get("attempt_id") == row["attempt_id"])
            _require(actual == sorted(row.get("report_ids", [])), "catalog_corrupt",
                     "attempt report IDs disagree with catalog")
        public = {key: run.get(key) for key in ("run_id", "parent_run_id", "company", "source_as_of",
                 "created_at", "status", "scenario_set", "reporting_currency", "model_metadata",
                 "artifact_revision", "source_snapshot_refs")}
        public["attempts"] = rows
        public["snapshot"] = self._snapshot(revision, run_id=run_id,
                                            state="partial" if run.get("status") == "partial" else "available")
        return public

    def get_run(self, run_id: str) -> dict:
        runs, attempts, reports, revision = self._index()
        key = _clean_id(run_id, "run_id")
        _require(key in runs, "not_found", "run ID is not registered")
        output = {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                  "run": self._run_view(runs[key], attempts, reports, revision)}
        _assert_pathless(output)
        return output

    def list_runs(self, entity_id: str, *, analysis_subject_id: str | None = None,
                  information_as_of: str | None = None, cursor: str | None = None,
                  limit: int = 50) -> dict:
        _clean_id(entity_id, "entity_id")
        runs, attempts, reports, revision = self._index()
        rows = [self._run_view(run, attempts, reports, revision) for run in runs.values()
                if run["company"]["entity_id"] == entity_id and
                (analysis_subject_id is None or run["company"].get("analysis_subject_id") == analysis_subject_id) and
                (information_as_of is None or run["source_as_of"] == information_as_of)]
        rows.sort(key=lambda row: (row["created_at"], row["run_id"]), reverse=True)
        filter_key = canonical_sha256([entity_id, analysis_subject_id, information_as_of])
        selected, page = self._page(rows, revision, cursor=cursor, limit=limit, filter_key=filter_key)
        output = {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                  "items": selected, "page": page,
                  "snapshot": self._snapshot(revision, state="available" if rows else "empty")}
        _assert_pathless(output)
        return output

    @staticmethod
    def _public_report(report: dict) -> dict:
        return {key: report.get(key) for key in
                ("report_id", "run_id", "attempt_id", "company", "artifact_kind", "artifact_revision",
                 "input_sha256", "result_sha256", "created_at", "status", "schema_version",
                 "engine_version", "information_as_of", "forecast_horizon", "supersedes_report_id",
                 "missing_reason")}

    def list_reports(self, entity_id: str, *, analysis_subject_id: str | None = None,
                     information_as_of: str | None = None, cursor: str | None = None,
                     limit: int = 50) -> dict:
        _clean_id(entity_id, "entity_id")
        _, _, reports, revision = self._index()
        rows = [report for report in reports.values()
                if report["company"]["entity_id"] == entity_id and
                (analysis_subject_id is None or report["company"].get("analysis_subject_id") == analysis_subject_id) and
                (information_as_of is None or report["information_as_of"] == information_as_of)]
        rows.sort(key=lambda row: (row["created_at"], row["report_id"]), reverse=True)
        for row in rows:
            self._read_artifact(row["forecast_artifact"])
        selected, page = self._page(rows, revision, cursor=cursor, limit=limit,
                                    filter_key=canonical_sha256([entity_id, analysis_subject_id, information_as_of]))
        latest = next((row["report_id"] for row in rows if row["status"] in {"validated", "published"}), None)
        output = {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                  "items": [self._public_report(row) for row in selected], "page": page,
                  "snapshot": self._snapshot(revision, state="available" if rows else "empty"),
                  "resolved_latest_success_report_id": latest,
                  "resolved_at": _utc_now()}
        _assert_pathless(output)
        return output

    def _exact_report(self, report_id: str) -> tuple[dict, dict, str]:
        _, _, reports, revision = self._index()
        key = _clean_id(report_id, "report_id")
        _require(key in reports, "not_found", "report ID is not registered")
        record = reports[key]
        result = self._validate_report_artifact(record)
        return record, result, revision

    @staticmethod
    def _source_refs(result: dict) -> list[dict]:
        refs: list[dict] = []
        seen: set[tuple] = set()
        for source in result.get("sources", []):
            ref = source.get("company_wiki_trace", {}).get("source_ref")
            if not isinstance(ref, dict) or set(ref) != SOURCE_REF_FIELDS:
                continue
            if ref.get("schema_version") != "2.0" or not HEX64.fullmatch(str(ref.get("content_sha256"))):
                continue
            key = (ref["document_id"], ref["source_id"], ref["content_sha256"])
            if key not in seen:
                refs.append({field: ref[field] for field in SOURCE_REF_FIELDS})
                seen.add(key)
        return refs

    @staticmethod
    def _provenance(record: dict, *, kind: str, source_refs: list[dict] | None = None,
                    missing_reason: str | None = None) -> dict:
        return {"owner": "revenue-forecast", "artifact_id": record["report_id"],
                "run_id": record.get("run_id"), "observation_id": None,
                "source_refs": source_refs or [], "locator": None, "kind": kind,
                "quality": "owner_validated" if missing_reason is None else "partial",
                "source_as_of": record["information_as_of"], "missing_reason": missing_reason}

    @staticmethod
    def _decimal(value: Any, record: dict, *, year: int | None, scenario: str | None,
                 unit: str | None = "currency") -> dict:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            text = None
        else:
            text = format(Decimal(str(value)), "f")
        return {"value": text, "currency": record.get("reporting_currency") if unit == "currency" else None,
                "unit": unit, "scale": record.get("reporting_scale") if unit == "currency" else 0,
                "period_start": None, "period_end": None, "period_kind": "FY" if year else None,
                "fiscal_year": year, "basis": "consolidated", "scenario": scenario,
                "actual_or_forecast": "forecast", "analysis_subject_id":
                record["company"].get("analysis_subject_id")}

    def _metric(self, record: dict, *, value: Any, year: int, scenario: str,
                segment_id: str | None = None) -> dict:
        return {"metric_id": "revenue", "definition_version": "rf-consolidated-revenue/1" if
                segment_id is None else "rf-segment-revenue/1", "segment_id": segment_id,
                "number": self._decimal(value, record, year=year, scenario=scenario),
                "provenance": self._provenance(record, kind="calculation",
                                               missing_reason="line_level_source_binding_unavailable"),
                "quality": "verified" if record["status"] in {"validated", "published"} else "partial",
                "missing_reason": None if record["status"] in {"validated", "published"} else record["missing_reason"]}

    @staticmethod
    def _node_ids(result: dict) -> list[str]:
        ids: list[str] = []
        for scenario, forecast in result.get("consolidated_forecast", {}).items():
            for year in forecast.get("annual_revenue", {}):
                ids.append(f"consolidated:{scenario}:{year}")
        for index, segment in enumerate(result.get("segments", [])):
            for scenario, detail in segment.get("scenarios", {}).items():
                for year in detail.get("effective_revenue", detail.get("recognized_revenue", {})):
                    ids.append(f"segment:{index}:{scenario}:{year}")
        return ids

    def _sensitivity_input(self, item: dict, result: dict, record: dict) -> tuple[dict, str]:
        """Preserve native absolute shock dimensions; never infer them from magnitude."""
        if item.get("shock_type") == "relative":
            return self._decimal(item.get("shock_value"), record, year=None,
                                 scenario=None, unit="ratio"), "sensitivity_lineage_not_projected"
        rows = [p for p in result.get("parameter_trace", [])
                if p.get("parameter_id") == item.get("parameter_id")]
        if item.get("shock_type") == "absolute" and len(rows) == 1:
            parameter = rows[0]
            currency = money_currency(parameter.get("currency"))
            factor = money_unit_scale_factor(parameter.get("unit"))
            if (parameter.get("dimension") in MONETARY_DIMENSIONS and currency is not None
                    and money_unit_currency(parameter.get("unit")) == currency
                    and factor is not None and factor == money_scale_factor(parameter.get("scale"))):
                exponent = Decimal(str(factor)).normalize().as_tuple()
                if exponent.digits == (1,) and isinstance(exponent.exponent, int):
                    context = dict(record, reporting_currency=parameter["currency"],
                                   reporting_scale=exponent.exponent)
                    return self._decimal(item.get("shock_value"), context, year=None,
                                         scenario=None), "sensitivity_lineage_not_projected"
        value = self._decimal(None, record, year=None, scenario=None, unit=None)
        value["scale"] = None
        return value, "sensitivity_input_unit_unavailable"

    def get_report(self, report_id: str) -> dict:
        record, result, revision = self._exact_report(report_id)
        available = record["status"] in {"validated", "published"}
        metrics: list[dict] = []
        segment_paths: list[dict] = []
        drivers: list[dict] = []
        sensitivities: list[dict] = []
        citations: list[dict] = []
        source_refs = self._source_refs(result)
        for ref in source_refs:
            citations.append(self._provenance(record, kind="fact", source_refs=[ref],
                                              missing_reason="citation_locator_unavailable"))
        if available:
            for scenario, forecast in result.get("consolidated_forecast", {}).items():
                for year_text, value in forecast.get("annual_revenue", {}).items():
                    metrics.append(self._metric(record, value=value, year=int(year_text),
                                                scenario=scenario))
            for index, segment in enumerate(result.get("segments", [])):
                for scenario, detail in segment.get("scenarios", {}).items():
                    path_metrics = [self._metric(record, value=value, year=int(year_text),
                                                 scenario=scenario, segment_id=str(index))
                                    for year_text, value in detail.get("effective_revenue",
                                                                       detail.get("recognized_revenue", {})).items()]
                    segment_paths.append({"segment_id": str(index), "label": segment["name"],
                                          "parent_segment_id": None, "scenario": scenario,
                                          "metrics": path_metrics})
            for driver in result.get("growth_driver_analysis", {}).get("drivers", []):
                drivers.append({"driver_id": str(driver["driver_id"]), "parent_driver_id": None,
                                "label": str(driver.get("title") or driver["driver_id"]),
                                "mechanism": driver.get("thesis"), "linked_metric_ids": ["revenue"],
                                "provenance": [self._provenance(record, kind="interpretation",
                                                               missing_reason="driver_source_binding_not_projected")]})
            for index, item in enumerate(result.get("sensitivities", [])):
                input_change, sensitivity_reason = self._sensitivity_input(item, result, record)
                sensitivities.append({"sensitivity_id": f"sensitivity:{index}",
                                      "input_metric_id": str(item.get("parameter_id") or "unknown"),
                                      "input_change": input_change,
                                      "output_metric_id": "terminal_revenue",
                                      "output_change": self._decimal(item.get("max_absolute_terminal_impact"),
                                                                     record, year=None, scenario="base"),
                                      "provenance": [self._provenance(record, kind="calculation",
                                                                      missing_reason=sensitivity_reason)]})
        gaps = [str(value) for value in result.get("data_gaps", []) if isinstance(value, str)]
        if not available:
            gaps.append(record.get("missing_reason") or "legacy_model_unavailable")
        if result.get("management_target_coverage", {}).get("targets"):
            gaps.append("management_targets_not_projected")
        view = {"report": self._public_report(record), "executive_summary": None,
                "metrics": metrics, "segment_paths": segment_paths, "driver_tree": drivers,
                "sensitivities": sensitivities, "management_targets": [],
                "calculation_node_ids": self._node_ids(result) if available else [],
                "assumptions": [], "counter_evidence": [], "quality_gaps": gaps,
                "citations": citations, "snapshot": self._snapshot(revision,
                run_id=record.get("run_id"), state="available" if available else "partial",
                reasons=[] if available else [record["missing_reason"]])}
        _assert_pathless(view)
        return {"schema_version": SCHEMA_VERSION, "catalog_revision": revision, "view": view}

    def get_model(self, report_id: str) -> dict:
        """Return exact-report model metadata, not raw input with private locators."""
        record, result, revision = self._exact_report(report_id)
        if record["status"] not in {"validated", "published"}:
            return {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                    "report_id": report_id, "state": "unavailable",
                    "missing_reason": record.get("missing_reason") or "legacy_model_unavailable",
                    "segments": [], "parameters": []}
        source_map = {source.get("source_id"): source.get("company_wiki_trace", {}).get("source_ref")
                      for source in result.get("sources", [])}
        parameters = []
        for row in result.get("parameter_trace", []):
            refs = [source_map[source_id] for source_id in row.get("source_ids", [])
                    if isinstance(source_map.get(source_id), dict) and
                    set(source_map[source_id]) == SOURCE_REF_FIELDS]
            parameters.append({"parameter_id": row.get("parameter_id"), "kind": row.get("kind"),
                               "definition": row.get("definition"), "value": row.get("value"),
                               "unit": row.get("unit"), "period": row.get("period"),
                               "scenario": row.get("scenario"), "claim_ids": row.get("claim_ids", []),
                               "source_refs": refs})
        segments = [{"segment_id": str(index), "name": segment.get("name"),
                     "base_revenue": segment.get("base_revenue"),
                     "scenarios": {scenario: {"model": detail.get("model"),
                                              "formula": detail.get("formula"),
                                              "driver_parameter_ids": detail.get("driver_parameter_ids", {})}
                                   for scenario, detail in segment.get("scenarios", {}).items()}}
                    for index, segment in enumerate(result.get("segments", []))]
        view = {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                "report_id": report_id, "state": "available", "missing_reason": None,
                "emitting_schema_version": record["schema_version"],
                "emitting_engine_version": record["engine_version"],
                "segments": segments, "parameters": parameters}
        _assert_pathless(view)
        return view

    def get_calculation(self, report_id: str, node_id: str) -> dict:
        record, result, revision = self._exact_report(report_id)
        return self._calculation_from_validated(record, result, revision, node_id)

    def _calculation_from_validated(self, record: dict, result: dict, revision: str, node_id: str) -> dict:
        report_id = record["report_id"]
        _clean_id(node_id, "node_id")
        empty: dict[str, Any] = {"report_id": report_id, "node_id": node_id, "expression": None,
                 "inputs": [], "output": None, "constraint_adjustments": [],
                 "trace_state": "unavailable", "missing_reason": None}
        if record["status"] not in {"validated", "published"}:
            empty["missing_reason"] = record.get("missing_reason") or "legacy_model_unavailable"
            return {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                    "calculation": empty}
        if node_id not in self._node_ids(result):
            raise CatalogError("node_not_found", "node ID is absent from this exact report")
        parts = node_id.split(":")
        if parts[0] == "consolidated" and len(parts) == 3:
            _, scenario, year_text = parts
            year = int(year_text)
            forecast = result["consolidated_forecast"][scenario]
            inputs = []
            for bridge in forecast.get("segment_bridge", []):
                inputs.append({"name": bridge["name"],
                               "number": self._decimal(bridge["annual_revenue"][year_text], record,
                                                       year=year, scenario=scenario),
                               "provenance": self._provenance(record, kind="calculation",
                                                              missing_reason="segment_lineage_in_child_node")})
            for bridge in forecast.get("adjustment_bridge", []):
                if year_text in bridge.get("annual_adjustment", {}):
                    inputs.append({"name": bridge.get("name", "adjustment"),
                                   "number": self._decimal(bridge["annual_adjustment"][year_text], record,
                                                           year=year, scenario=scenario),
                                   "provenance": self._provenance(record, kind="calculation",
                                                                  missing_reason="adjustment_lineage_not_projected")})
            empty.update({"expression": "sum(segment effective revenue) + signed adjustments",
                          "inputs": inputs,
                          "output": self._metric(record, value=forecast["annual_revenue"][year_text],
                                                 year=year, scenario=scenario),
                          "trace_state": "partial", "missing_reason": "line_level_source_binding_unavailable"})
        elif parts[0] == "segment" and len(parts) == 4:
            _, index_text, scenario, year_text = parts
            segment = result["segments"][int(index_text)]
            detail = segment["scenarios"][scenario]
            year = int(year_text)
            inputs = []
            spec = MODEL_REGISTRY.get(detail.get("model"))
            if spec is None:
                empty["missing_reason"] = "emitting_model_dimensions_unavailable"
                return {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                        "calculation": empty}
            gaps = {"parameter_source_binding_not_projected"}
            for name, annual in detail.get("driver_values", {}).items():
                if isinstance(annual, dict) and year_text in annual:
                    dimension = spec.dimensions.get(name)
                    if dimension in MONETARY_DIMENSIONS:
                        number = self._decimal(annual[year_text], record, year=year,
                                               scenario=scenario)
                        if dimension != "revenue":
                            number["unit"] = dimension
                    elif dimension == "ratio":
                        number = self._decimal(annual[year_text], record, year=year,
                                               scenario=scenario, unit="ratio")
                    else:
                        # Model dimensions identify quantity/activity, but not
                        # the physical denominator or multiplier. Keep it unknown.
                        number = self._decimal(annual[year_text], record, year=year,
                                               scenario=scenario, unit=dimension)
                        number["scale"] = None
                        gaps.add("driver_physical_unit_not_projected")
                    inputs.append({"name": name, "number": number,
                                   "provenance": self._provenance(
                                       record, kind="assumption",
                                       missing_reason="parameter_source_binding_not_projected")})
            if spec.consumes_base_revenue:
                years = sorted(int(value) for value in result["forecast_years"])
                position = years.index(year)
                previous_year = years[position - 1] if position else result.get("base_year")
                previous_value = (detail.get("modeled_activity", {}).get(str(previous_year))
                                  if position else segment.get("base_revenue"))
                number = self._decimal(previous_value, record, year=previous_year,
                                       scenario=scenario)
                if not position:
                    number["actual_or_forecast"] = "actual"
                if previous_value is None:
                    gaps.add("previous_revenue_not_recorded")
                inputs.append({"name": "previous_revenue", "number": number,
                               "provenance": self._provenance(
                                   record, kind="calculation" if position else "fact",
                                   missing_reason="previous_revenue_source_binding_not_projected")})
            value = detail.get("effective_revenue", detail.get("recognized_revenue", {}))[year_text]
            if value != detail.get("modeled_activity", {}).get(year_text):
                # Recognition/constraints are a separate owner transform. Do
                # not label its effective result as the model formula output.
                empty["missing_reason"] = "recognition_or_constraint_transform_not_projected"
            else:
                empty.update({"expression": detail.get("formula"), "inputs": inputs,
                              "output": self._metric(record, value=value, year=year, scenario=scenario,
                                                     segment_id=index_text),
                              "trace_state": "partial", "missing_reason": ";".join(sorted(gaps))})
        _assert_pathless(empty)
        return {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                "calculation": empty}

    def get_calculation_trace(self, report_id: str, node_id: str) -> dict:
        from report_catalog_lineage import get_calculation_trace
        record, result, revision = self._exact_report(report_id)
        return {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                "trace": get_calculation_trace(self, record, result, revision, node_id)}

    def get_source_snapshot(self, report_id: str, snapshot_id: str) -> dict:
        from report_catalog_lineage import get_source_snapshot
        record, result, revision = self._exact_report(report_id)
        return {"schema_version": SCHEMA_VERSION, "catalog_revision": revision,
                "source_snapshot": get_source_snapshot(self, record, result, snapshot_id)}


def _assert_pathless(value: Any) -> None:
    """Refuse accidental publication of a private Windows/Unix file locator."""
    if isinstance(value, dict):
        _require(not any(key in {"path", "relative_path", "original_path", "doc_root"} for key in value),
                 "path_leak", "public projection contains a path key")
        for child in value.values():
            _assert_pathless(child)
    elif isinstance(value, list):
        for child in value:
            _assert_pathless(child)
    elif isinstance(value, str):
        _require(not re.search(r"(?:[A-Za-z]:[\\/]|\\\\|/(?:Users|home|tmp|var)/)", value),
                 "path_leak", "public projection contains a physical locator")


def _read_registry_file(path: Path) -> list[dict]:
    """Verify retained registry rows with the existing publication owner."""
    try:
        return validate_registry_text(_bounded_bytes(path).decode("utf-8"))
    except (RegistryError, UnicodeError, ValueError) as exc:
        raise CatalogError("publication_registry_corrupt", "publication registry evidence is invalid") from exc



def _source_alias_stable_facts(value: Any) -> dict:
    """Keep every authority fact; only the two observation-time fields vary."""
    _require(isinstance(value, dict) and
             isinstance(value.get("issuer_proof_receipt_sha256"), str) and
             bool(HEX64.fullmatch(value["issuer_proof_receipt_sha256"])),
             "w09_import_conflict", "stored source identity proof is incompatible")
    query = value.get("issuer_proof_query")
    _require(isinstance(query, dict) and set(query) == {"entity_id", "listing_id", "as_of"}
             and isinstance(query.get("as_of"), str) and bool(query["as_of"]),
             "w09_import_conflict", "stored source identity query is incompatible")
    result = {key: child for key, child in value.items() if key != "issuer_proof_receipt_sha256"}
    result["issuer_proof_query"] = {key: child for key, child in query.items() if key != "as_of"}
    return result


def _w09_registered_replay(catalog: ReportCatalog, run: dict, attempts: list[dict],
                          reports: list[dict], *, fresh_proof: dict | None,
                          verify_current: Callable[[], None]) -> dict | None:
    """Return the first exact immutable admission after fresh owner verification.

    Stored proof is lineage, never the current authority. The operation must
    validate the owner again before reusing the first observation's bytes.
    """
    if not catalog.file.exists():
        return None
    observed = _bounded_bytes(catalog.file)
    matches = [line for line in catalog._entries()
               if any(item.get("run_id") == run["run_id"] for item in line["runs"])]
    if not matches:
        return None
    _require(len(matches) == 1 and len(matches[0]["runs"]) == 1,
             "w09_import_conflict", "W09 run does not have one immutable original admission")
    line = matches[0]
    stored = line["runs"][0]
    if fresh_proof is not None:
        original_proof = stored.get("source_bound_identity_evidence")
        _require(_source_alias_stable_facts(original_proof) == _source_alias_stable_facts(fresh_proof),
                 "w09_import_conflict", "current source identity authority differs from the first W09 admission")
        run["source_bound_identity_evidence"] = original_proof
    _require(line["runs"] == [run] and line["attempts"] == attempts and line["reports"] == reports,
             "w09_import_conflict", "W09 immutable IDs bind different admission content or company scope")
    for attempt in attempts:
        catalog._validate_attempt_source(attempt)
    for report in reports:
        catalog._validate_report_artifact(report)
    verify_current()
    _require(_bounded_bytes(catalog.file) == observed, "catalog_busy",
             "catalog changed while verifying W09 replay")
    return {"schema_version": SCHEMA_VERSION, "catalog_revision": line["line_sha256"],
            "registered": {"runs": [run["run_id"]],
                           "attempts": [a["attempt_id"] for a in attempts],
                           "reports": [r["report_id"] for r in reports]}}


def import_w09(catalog: ReportCatalog, *, entity_id: str, analysis_subject_id: str | None,
               identity_evidence: dict[str, Any], listing_id: str | None = None,
               identity_resolver: Callable[[str], dict[str, Any]] | None = None,
               source_alias_resolver: Callable[..., dict[str, Any]] | None = None) -> dict:
    """Explicitly register the fixed, already-frozen W09 main/stress package.

    ``entity_id`` must come from the StockWiki identity owner.  This function
    requires a trusted owner-installed resolver to obtain the public StockWiki
    response; caller JSON alone never proves identity. It then checks W09's
    registry, recorder and frozen bytes before append. It does not run research.
    """
    # An owner-installed resolver must perform the public StockWiki lookup.
    # The CLI deliberately installs none until that public seam is available.
    # Caller-provided JSON and its self-claimed hash cannot establish authority.
    _require(callable(identity_resolver), "identity_resolver_unavailable",
             "W09 import requires an owner-installed public StockWiki identity resolver")
    _clean_id(entity_id, "entity_id")
    assert identity_resolver is not None
    resolved_identity = identity_resolver(entity_id)
    _require(isinstance(resolved_identity, dict) and resolved_identity == identity_evidence,
             "identity_unverified", "identity evidence differs from the public StockWiki resolution")
    if analysis_subject_id is not None:
        _clean_id(analysis_subject_id, "analysis_subject_id")
    _require(isinstance(identity_evidence, dict) and
             identity_evidence.get("authority") == "stockwiki" and
             identity_evidence.get("entity_id") == entity_id and
             identity_evidence.get("resolution_status") == "resolved" and
             isinstance(identity_evidence.get("source_revision"), str) and
             bool(identity_evidence["source_revision"]) and
             isinstance(identity_evidence.get("lookup_receipt_sha256"), str) and
             bool(HEX64.fullmatch(identity_evidence["lookup_receipt_sha256"])),
             "identity_unverified", "W09 import requires an explicit StockWiki identity receipt")
    package = catalog.root / "delivery" / "w09"
    run_path = package / "recorder" / "w09-rf-research-20261023" / "run.json"
    native_path = package / "recorder" / "native-calls.jsonl"
    registry_path = package / "registry" / "publications.jsonl"
    run_receipt = json.loads(_bounded_bytes(run_path))
    native_calls = [json.loads(line) for line in _bounded_bytes(native_path).decode("utf-8").splitlines()]
    registry = _read_registry_file(registry_path)
    _require(run_receipt.get("schema_version") == "1.0" and
             run_receipt.get("run_id") == "w09-rf-research-20261023",
             "w09_receipt_invalid", "W09 run receipt is incompatible")
    source_alias_needed = identity_evidence.get("display_name") != run_receipt.get("company_query")
    _require(not source_alias_needed or callable(source_alias_resolver),
             "identity_unverified", "identity receipt company name differs from W09")
    company = {"entity_id": entity_id, "listing_id": listing_id,
               "analysis_subject_id": analysis_subject_id, "resolution_status": "resolved",
               "display_name": run_receipt["company_query"]}
    run = {"run_id": run_receipt["run_id"], "parent_run_id": None, "company": company,
           "source_as_of": run_receipt["as_of_date"], "created_at": run_receipt["created_at"],
           "status": "succeeded", "scenario_set": ["low", "base", "high"],
           "reporting_currency": "CNY", "model_metadata": {"engine_version": "4.3.0",
           "research_package": "W09-RF-RESEARCH"}, "artifact_revision": "W09-RF-RESEARCH",
           "source_snapshot_refs": [], "source_evidence": catalog.artifact_ref(run_path)}
    run["identity_evidence"] = identity_evidence
    attempts: list[dict] = []
    reports: list[dict] = []
    for variant in ("main", "stress"):
        forecast_path = package / "forecast" / f"{variant}-forecast.json"
        input_path = package / "forecast" / f"{variant}-input.json"
        markdown_path = package / "forecast" / f"{variant}-forecast.md"
        snapshot_path = package / "snapshots" / f"{variant}-v1.json"
        result = json.loads(_bounded_bytes(forecast_path))
        snapshot = json.loads(_bounded_bytes(snapshot_path))
        _require(result.get("company_name") == company["display_name"] and
                 result.get("as_of_date") == run["source_as_of"],
                 "w09_receipt_invalid", "W09 forecast identity mismatch")
        forecast_publications = [entry for entry in registry if entry.get("artifact_type") == "forecast"
                                 and entry.get("input_sha256") == result.get("input_sha256") and
                                 entry.get("result_sha256") == result.get("result_sha256") and
                                 entry.get("validation_status") == "validated"]
        snapshot_publications = [entry for entry in registry if entry.get("artifact_type") == "snapshot"
                                 and entry.get("artifact_id") == snapshot.get("snapshot_id") and
                                 entry.get("input_sha256") == result.get("input_sha256") and
                                 entry.get("result_sha256") == snapshot.get("forecast_result_sha256")]
        _require(bool(forecast_publications) and bool(snapshot_publications),
                 "w09_publication_missing", "W09 private registry lacks a matching formal publication")
        calls = [call for call in native_calls if call.get("request_id") == f"w09-{variant}-compute"]
        _require(len(calls) == 1, "w09_receipt_invalid", "W09 compute capture is not unique")
        capture = calls[0]["capture"]
        _require(calls[0].get("capture_exit") == 0 and capture.get("exit_code") == 0 and
                 not capture.get("timed_out"), "w09_receipt_invalid", "W09 compute capture failed")
        attempt_id = capture["capture_id"]
        bytes_sha = catalog.artifact_ref(forecast_path)["bytes_sha256"]
        report_id = "rf-" + canonical_sha256({"input_sha256": result["input_sha256"],
                                               "result_sha256": result["result_sha256"],
                                               "bytes_sha256": bytes_sha})
        attempt = {"run_id": run["run_id"], "attempt_id": attempt_id, "status": "succeeded",
                   "started_at": capture.get("runtime_observation", {}).get("observed_at"),
                   "ended_at": forecast_publications[-1]["registered_at"],
                   "report_ids": [report_id], "error_code": None,
                   "source_evidence": {"kind": "native_calls_jsonl", "artifact": catalog.artifact_ref(native_path),
                                       "capture_id": attempt_id}}
        years = result["forecast_years"]
        report = {"report_id": report_id, "run_id": run["run_id"], "attempt_id": attempt_id,
                  "company": company, "artifact_kind": "revenue_forecast",
                  "artifact_revision": result["forecast_version"],
                  "input_sha256": result["input_sha256"], "result_sha256": result["result_sha256"],
                  "created_at": forecast_publications[-1]["registered_at"], "status": "validated",
                  "schema_version": result["schema_version"], "engine_version": result["engine_version"],
                  "information_as_of": result["as_of_date"],
                  "forecast_horizon": f"{min(years)}-{max(years)}", "supersedes_report_id": None,
                  "missing_reason": None, "reporting_currency": result["currency"],
                  "reporting_scale": _frozen_reporting_scale(result),
                  "forecast_artifact": catalog.artifact_ref(forecast_path),
                  "input_artifact": catalog.artifact_ref(input_path),
                  "markdown_artifact": catalog.artifact_ref(markdown_path),
                  "snapshot_artifact": catalog.artifact_ref(snapshot_path),
                  "snapshot_id": snapshot["snapshot_id"]}
        attempts.append(attempt)
        reports.append(report)
    if source_alias_needed:
        # Validate the complete frozen reports and their native evidence BEFORE
        # asking the trusted owner whether their primary original binds this
        # canonical issuer. Nothing has been appended at this point.
        from report_catalog_source_alias import w09_primary_source_refs
        for attempt in attempts:
            catalog._validate_attempt_source(attempt)
        for report in reports:
            catalog._validate_report_artifact(report)
        frozen_results = [catalog._read_json(report["forecast_artifact"]) for report in reports]
        source_refs = w09_primary_source_refs(frozen_results, run_receipt["company_query"])
        assert source_alias_resolver is not None
        proof = source_alias_resolver(entity_id, run_receipt["company_query"], source_refs, identity_evidence)
        run["source_bound_identity_evidence"] = proof
        def verify_identity_before_append() -> None:
            # This is called under the catalog lock AFTER its final expensive
            # artifact/index checks. The factory pins as_of for this operation.
            # It is the last owner lookup before append, not a cross-owner lock.
            assert source_alias_resolver is not None
            _require(source_alias_resolver(entity_id, run_receipt["company_query"], source_refs,
                                           identity_evidence) == proof,
                     "identity_unverified", "source-bound identity changed before admission")
        receipt = _w09_registered_replay(catalog, run, attempts, reports, fresh_proof=proof,
                                         verify_current=verify_identity_before_append)
        if receipt is None:
            receipt = catalog.add_records(runs=[run], attempts=attempts, reports=reports,
                                          before_append=verify_identity_before_append)
    else:
        def verify_current_identity() -> None:
            _require(identity_resolver(entity_id) == identity_evidence,
                     "identity_unverified", "canonical identity changed before W09 replay")
        receipt = _w09_registered_replay(catalog, run, attempts, reports, fresh_proof=None,
                                         verify_current=verify_current_identity)
        if receipt is None:
            receipt = catalog.add_records(runs=[run], attempts=attempts, reports=reports)
    receipt["source_package"] = "W09-RF-RESEARCH"
    receipt["source_run_id"] = run["run_id"]
    receipt["source_registry_sha256"] = _sha(_bounded_bytes(registry_path))
    receipt["source_native_calls_sha256"] = _sha(_bounded_bytes(native_path))
    receipt["identity_authority"] = "owner_installed_stockwiki_public_resolver"
    receipt["identity_receipt_sha256"] = identity_evidence["lookup_receipt_sha256"]
    if source_alias_needed:
        receipt["identity_binding_mode"] = "source_bound_primary_annual"
        receipt["identity_alias_proof_sha256"] = run["source_bound_identity_evidence"]["issuer_proof_receipt_sha256"]
    receipt["failed_attempt_sample"] = "OPEN_no_recorded_failure"
    return receipt
