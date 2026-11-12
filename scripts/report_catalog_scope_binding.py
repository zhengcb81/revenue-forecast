"""Public RF scope-binding DTO, reader and owner-owned append-only state.

Everything this module reads from the report catalog goes through the owner's
public ``get_report`` / ``get_run`` / ``get_source_snapshot`` responses. It
never imports a private catalog helper, inspects a catalog index, opens a
neighbouring SQLite database or reads a neighbouring repository's layout.

Scope dimensions are explicit: accounting basis, fiscal-year end, segment
identifiers, period start/end, subject revision and measurement dimensions
are all supplied through public fields. Nothing defaults to IFRS, a 12-31
year end, a single segment or an FY-only period.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from contracts.evidence import canonical_sha256
from owner_file_lock import OwnerFileLock
from report_catalog import CatalogError
from report_catalog_subject_resolver import (
    HEX64, TOKEN, ScopeContractError, SubjectQuery, SubjectResolver, known_text, need,
)

BINDING_SCHEMA = "rf-report-scope-binding/1"
LOG_SCHEMA = "rf-report-scope-binding-log/1"
READ_SCHEMA = "rf-report-scope-bindings/1"
BINDING_ID = re.compile(r"^rfscope1-[a-f0-9]{64}$")
NOTE = ("Original report canonical fields are unchanged. This is a current verified-scope "
        "binding, not a claim that this subject was supplied when the forecast was published. "
        "Exact source hashes prove quotation provenance, not the economic meaning of a role.")
PATH_LIKE = re.compile(r"(?:[A-Za-z]:[\\/]|\\\\|/(?:Users|home|tmp|var)/)")
FORBIDDEN_KEYS = frozenset({"path", "relative_path", "original_path", "doc_root"})

COORDINATE_FIELDS = frozenset({
    "metric_id", "fiscal_year", "period_kind", "period_start", "period_end",
    "scenario", "basis",
})
WITNESS_FIELDS = frozenset({
    "role", "source_id", "source_snapshot_id", "content_sha256", "excerpt",
    "excerpt_sha256",
})
ROLES = frozenset({"reporting_entity", "accounting_basis", "revenue_perimeter",
                   "fiscal_calendar"})
EVIDENCE_FIELDS = frozenset({
    "report_id", "analysis_subject_id", "analysis_subject_revision",
    "expected_input_sha256", "expected_result_sha256", "accounting_basis",
    "fiscal_year_end", "segment_ids", "measure_kind", "currency", "unit", "scale",
    "basis", "covered_coordinates", "source_witnesses", "limitations", "verified_at",
})
BINDING_FIELDS = frozenset({
    "schema_version", "binding_id", "report_id", "run_id", "report_ref_sha256",
    "input_sha256", "result_sha256", "entity_id", "listing_id",
    "original_analysis_subject_id", "analysis_subject_id",
    "analysis_subject_revision", "subject_snapshot_sha256", "accounting_basis",
    "fiscal_year_end", "segment_ids", "measure_kind", "currency", "unit", "scale",
    "basis", "covered_coordinates", "source_witnesses", "limitations",
    "verified_at", "note",
})
HASH_FIELDS = ("report_ref_sha256", "input_sha256", "result_sha256",
               "subject_snapshot_sha256")


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def assert_public_pathless(value: Any) -> None:
    """Refuse physical locators without imposing a result size limit."""
    if isinstance(value, dict):
        for key, child in value.items():
            need(isinstance(key, str) and key not in FORBIDDEN_KEYS, "path_leak",
                 "public projection contains a path key")
            assert_public_pathless(child)
    elif isinstance(value, list):
        for child in value:
            assert_public_pathless(child)
    elif isinstance(value, str):
        need(PATH_LIKE.search(value) is None, "path_leak",
             "public projection contains a physical locator")


def _date(value: Any) -> date | None:
    if value is None:
        return None
    need(isinstance(value, str), "scope_evidence_invalid",
         "scope period date must be a string or null")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ScopeContractError("scope_evidence_invalid",
                                 "scope period date is not an ISO date") from exc


def coordinate_key(value: Any) -> tuple[Any, ...]:
    """Full explicit public period key; no FY/single-segment/12-31 default."""
    need(isinstance(value, dict) and set(value) == COORDINATE_FIELDS,
         "scope_evidence_invalid", "scope coordinate fields differ")
    need(isinstance(value.get("metric_id"), str) and TOKEN.fullmatch(value["metric_id"]),
         "scope_evidence_invalid", "scope metric identifier is invalid")
    year = value.get("fiscal_year")
    need(type(year) is int and 1 <= year <= 9999, "scope_evidence_invalid",
         "scope fiscal year is not an integer")
    need(known_text(value.get("period_kind"), 64), "scope_evidence_invalid",
         "scope period kind is unknown")
    need(isinstance(value.get("scenario"), str) and TOKEN.fullmatch(value["scenario"]),
         "scope_evidence_invalid", "scope scenario is invalid")
    need(known_text(value.get("basis"), 128), "scope_evidence_invalid",
         "scope basis is unknown")
    start, end = _date(value.get("period_start")), _date(value.get("period_end"))
    need(start is None or end is None or start <= end, "scope_evidence_invalid",
         "scope period dates are reversed")
    return (value["metric_id"], year, value["period_kind"], value.get("period_start"),
            value.get("period_end"), value["scenario"], value["basis"])


def _coordinate_sort_key(value: dict[str, Any]) -> str:
    return json.dumps(coordinate_key(value), ensure_ascii=False, sort_keys=True, default=str)


def _witness_shape(row: Any) -> dict[str, Any]:
    need(isinstance(row, dict) and set(row) == WITNESS_FIELDS, "scope_evidence_invalid",
         "source scope witness fields differ")
    need(row.get("role") in ROLES and isinstance(row.get("source_id"), str)
         and TOKEN.fullmatch(row["source_id"])
         and isinstance(row.get("source_snapshot_id"), str)
         and TOKEN.fullmatch(row["source_snapshot_id"])
         and isinstance(row.get("content_sha256"), str)
         and HEX64.fullmatch(row["content_sha256"])
         and isinstance(row.get("excerpt_sha256"), str)
         and HEX64.fullmatch(row["excerpt_sha256"])
         and isinstance(row.get("excerpt"), str) and bool(row["excerpt"]),
         "scope_evidence_invalid", "source scope witness is malformed")
    need(hashlib.sha256(row["excerpt"].encode("utf-8")).hexdigest() == row["excerpt_sha256"],
         "scope_evidence_invalid", "scope witness excerpt hash differs")
    return row


def validate_witnesses(rows: Any, *, catalog: Any, report_id: str) -> list[dict[str, Any]]:
    """Verify every witness against the exact captured source via public readers."""
    need(isinstance(rows, list) and bool(rows), "scope_source_missing",
         "scope source witnesses are absent")
    checked: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for row in rows:
        witness = _witness_shape(row)
        key = (witness["role"], witness["source_id"], witness["source_snapshot_id"],
               witness["excerpt_sha256"])
        need(key not in seen, "scope_duplicate_source", "scope witness is duplicated")
        seen.add(key)
        try:
            response = catalog.get_source_snapshot(report_id, witness["source_snapshot_id"])
        except CatalogError as exc:
            code = "scope_source_missing" if exc.code == "not_found" else "scope_source_unavailable"
            raise ScopeContractError(code, "registered source snapshot is unavailable") from exc
        except OSError as exc:
            raise ScopeContractError("scope_source_unavailable",
                                     "registered source snapshot could not be read") from exc
        need(isinstance(response, dict) and response.get("schema_version") == "rf-report-catalog/1"
             and isinstance(response.get("source_snapshot"), dict),
             "scope_source_unavailable", "public source snapshot response is incompatible")
        snapshot = response["source_snapshot"]
        encoded = snapshot.get("content_base64url")
        need(isinstance(encoded, str)
             and snapshot.get("source_id") == witness["source_id"]
             and snapshot.get("content_sha256") == witness["content_sha256"],
             "scope_evidence_invalid", "scope witness does not match its exact captured source")
        try:
            body = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
            text = body.decode("utf-8", errors="strict")
        except (ValueError, UnicodeError) as exc:
            raise ScopeContractError("scope_evidence_invalid",
                                     "captured source body is unreadable") from exc
        need(len(body) == snapshot.get("byte_size")
             and hashlib.sha256(body).hexdigest() == witness["content_sha256"]
             and witness["excerpt"] in text, "scope_evidence_invalid",
             "scope witness is not in this exact captured source")
        checked.append(witness)
    need({row["role"] for row in checked} == ROLES, "scope_source_missing",
         "required scope source roles are not all witnessed")
    return sorted(checked, key=lambda row: (row["role"], row["source_id"],
                                            row["source_snapshot_id"], row["excerpt_sha256"]))


def validate_evidence(value: Any, *, catalog: Any) -> dict[str, Any]:
    """Validate and normalize the public scope evidence, then verify its sources."""
    need(isinstance(value, dict) and set(value) == EVIDENCE_FIELDS,
         "scope_evidence_invalid", "scope evidence fields differ")
    need(isinstance(value.get("report_id"), str) and TOKEN.fullmatch(value["report_id"]),
         "scope_evidence_invalid", "scope report identifier is invalid")
    need(isinstance(value.get("analysis_subject_id"), str)
         and TOKEN.fullmatch(value["analysis_subject_id"])
         and type(value.get("analysis_subject_revision")) is int
         and value["analysis_subject_revision"] > 0,
         "scope_evidence_invalid", "scope subject identity is invalid")
    for field in ("expected_input_sha256", "expected_result_sha256"):
        need(isinstance(value.get(field), str) and HEX64.fullmatch(value[field]),
             "scope_evidence_invalid", f"{field} is not a SHA-256")
    for field in ("accounting_basis", "measure_kind", "currency", "unit", "basis"):
        need(known_text(value.get(field), 128), "scope_evidence_invalid",
             f"{field} must be an explicit known value")
    need(type(value.get("scale")) is int, "scope_evidence_invalid",
         "scope scale must be an integer")
    calendar = value.get("fiscal_year_end")
    need(isinstance(calendar, str) and re.fullmatch(r"\d{2}-\d{2}", calendar) is not None,
         "scope_evidence_invalid", "fiscal year end must be MM-DD")
    try:
        date(2000, int(calendar[:2]), int(calendar[3:]))
    except ValueError as exc:
        raise ScopeContractError("scope_evidence_invalid",
                                 "fiscal year end is not a calendar day") from exc
    segments = value.get("segment_ids")
    need(isinstance(segments, list) and bool(segments)
         and all(isinstance(item, str) and TOKEN.fullmatch(item) for item in segments)
         and len(set(segments)) == len(segments), "scope_evidence_invalid",
         "scope segment identifiers are absent or duplicated")
    limitations = value.get("limitations")
    need(isinstance(limitations, list)
         and all(isinstance(item, str) and bool(item.strip()) for item in limitations),
         "scope_evidence_invalid", "scope limitations are malformed")
    verified_at = value.get("verified_at")
    need(isinstance(verified_at, str), "scope_evidence_invalid",
         "scope verification clock is absent")
    try:
        parsed = datetime.fromisoformat(verified_at.replace("Z", "+00:00"))
        need(parsed.tzinfo is not None, "scope_evidence_invalid",
             "scope verification clock has no timezone")
    except ValueError as exc:
        raise ScopeContractError("scope_evidence_invalid",
                                 "scope verification clock is invalid") from exc
    coordinates = value.get("covered_coordinates")
    need(isinstance(coordinates, list) and bool(coordinates), "scope_evidence_invalid",
         "covered scope coordinates are absent")
    keys = [coordinate_key(row) for row in coordinates]
    need(len(keys) == len(set(keys)), "scope_evidence_invalid",
         "covered scope coordinates are duplicated")
    for row, key in zip(coordinates, keys):
        if str(key[2]).upper() == "FY" and key[4] is not None:
            need(key[4][5:] == calendar, "scope_period_calendar_mismatch",
                 "FY period end does not match the declared fiscal calendar")
    witnesses = validate_witnesses(value.get("source_witnesses"), catalog=catalog,
                                   report_id=value["report_id"])
    normalized = copy.deepcopy(value)
    normalized["covered_coordinates"] = sorted(copy.deepcopy(coordinates),
                                               key=_coordinate_sort_key)
    normalized["source_witnesses"] = witnesses
    return normalized


def _read_public_report(catalog: Any, evidence: dict[str, Any]) -> tuple[dict, dict, Any, str]:
    """Read one exact immutable report through the owner's public readers."""
    report_id = evidence["report_id"]
    try:
        response = catalog.get_report(report_id)
    except CatalogError as exc:
        raise ScopeContractError("scope_report_unavailable",
                                 "exact report is unavailable") from exc
    except OSError as exc:
        raise ScopeContractError("scope_report_unavailable",
                                 "exact report could not be read") from exc
    need(isinstance(response, dict) and response.get("schema_version") == "rf-report-catalog/1"
         and isinstance(response.get("view"), dict), "scope_report_unavailable",
         "public exact report response is incompatible")
    report = response["view"].get("report")
    need(isinstance(report, dict) and report.get("report_id") == report_id
         and isinstance(report.get("run_id"), str) and TOKEN.fullmatch(report["run_id"])
         and report.get("status") in {"validated", "published"}
         and isinstance(report.get("company"), dict), "scope_report_state_unavailable",
         "exact report is not a published immutable report")
    for field in ("input_sha256", "result_sha256"):
        need(isinstance(report.get(field), str) and HEX64.fullmatch(report[field]),
             "scope_anchor_mismatch", "exact report has no immutable anchors")
    need(report["input_sha256"] == evidence["expected_input_sha256"]
         and report["result_sha256"] == evidence["expected_result_sha256"],
         "scope_anchor_mismatch", "report immutable anchors differ")
    company = report["company"]
    need(isinstance(company.get("entity_id"), str) and TOKEN.fullmatch(company["entity_id"])
         and isinstance(company.get("listing_id"), str) and TOKEN.fullmatch(company["listing_id"])
         and company.get("resolution_status") == "resolved", "scope_identity_mismatch",
         "exact report has no resolved canonical identity")
    original_subject = company.get("analysis_subject_id")
    need(original_subject is None or (isinstance(original_subject, str)
         and TOKEN.fullmatch(original_subject)), "scope_identity_mismatch",
         "exact report has a malformed original subject")
    need(original_subject in (None, evidence["analysis_subject_id"]),
         "scope_identity_mismatch", "original and verified company scopes differ")
    try:
        run_response = catalog.get_run(report["run_id"])
    except (CatalogError, OSError) as exc:
        raise ScopeContractError("scope_report_unavailable",
                                 "exact report run is unavailable") from exc
    need(isinstance(run_response, dict) and isinstance(run_response.get("run"), dict)
         and run_response["run"].get("run_id") == report["run_id"]
         and run_response["run"].get("company") == company, "scope_identity_mismatch",
         "exact report and run identity do not agree")
    revision = response.get("catalog_revision")
    need(isinstance(revision, str) and bool(revision), "scope_report_unavailable",
         "public catalog revision is absent")
    return report, company, original_subject, revision


def build_scope_binding(*, catalog: Any, subject_resolver: SubjectResolver,
                        evidence: dict[str, Any]) -> dict[str, Any]:
    """Compose a deterministic public binding from owner readers and a subject port."""
    payload = validate_evidence(evidence, catalog=catalog)
    report, company, original_subject, _revision = _read_public_report(catalog, payload)
    query = SubjectQuery(entity_id=company["entity_id"], listing_id=company["listing_id"],
                         analysis_subject_id=payload["analysis_subject_id"],
                         analysis_subject_revision=payload["analysis_subject_revision"])
    snapshot = subject_resolver.resolve(query)
    need(snapshot.entity_id == company["entity_id"]
         and snapshot.listing_id == company["listing_id"]
         and snapshot.analysis_subject_id == payload["analysis_subject_id"]
         and snapshot.analysis_subject_revision == payload["analysis_subject_revision"],
         "scope_identity_mismatch", "resolved public subject does not match the report")
    value: dict[str, Any] = {
        "schema_version": BINDING_SCHEMA, "report_id": payload["report_id"],
        "run_id": report["run_id"], "report_ref_sha256": canonical_sha256(report),
        "input_sha256": payload["expected_input_sha256"],
        "result_sha256": payload["expected_result_sha256"],
        "entity_id": company["entity_id"], "listing_id": company["listing_id"],
        "original_analysis_subject_id": original_subject,
        "analysis_subject_id": payload["analysis_subject_id"],
        "analysis_subject_revision": payload["analysis_subject_revision"],
        "subject_snapshot_sha256": snapshot.snapshot_sha256,
        "accounting_basis": payload["accounting_basis"],
        "fiscal_year_end": payload["fiscal_year_end"],
        "segment_ids": list(payload["segment_ids"]),
        "measure_kind": payload["measure_kind"], "currency": payload["currency"],
        "unit": payload["unit"], "scale": payload["scale"], "basis": payload["basis"],
        "covered_coordinates": payload["covered_coordinates"],
        "source_witnesses": payload["source_witnesses"],
        "limitations": list(payload["limitations"]),
        "verified_at": payload["verified_at"], "note": NOTE,
    }
    value["binding_id"] = "rfscope1-" + canonical_sha256(value)
    assert_public_pathless(value)
    return value


def _shape(binding: Any) -> dict[str, Any]:
    need(isinstance(binding, dict) and set(binding) == BINDING_FIELDS,
         "scope_binding_invalid", "scope binding fields differ")
    need(binding.get("schema_version") == BINDING_SCHEMA
         and isinstance(binding.get("binding_id"), str)
         and BINDING_ID.fullmatch(binding["binding_id"])
         and binding["binding_id"] == "rfscope1-" + canonical_sha256(
             {key: value for key, value in binding.items() if key != "binding_id"}),
         "scope_binding_invalid", "scope binding ID does not reproduce")
    need(all(isinstance(binding.get(field), str) and HEX64.fullmatch(binding[field])
             for field in HASH_FIELDS), "scope_binding_invalid", "scope hash is invalid")
    need(isinstance(binding.get("note"), str) and binding["note"] == NOTE,
         "scope_binding_invalid", "scope disclosure is invalid")
    need(isinstance(binding.get("limitations"), list)
         and all(isinstance(item, str) for item in binding["limitations"]),
         "scope_binding_invalid", "scope limitations are malformed")
    coordinates = binding.get("covered_coordinates")
    need(isinstance(coordinates, list) and bool(coordinates), "scope_binding_invalid",
         "scope binding has no covered coordinates")
    keys = [coordinate_key(row) for row in coordinates]
    need(len(keys) == len(set(keys)), "scope_binding_invalid",
         "scope binding coordinates are duplicated")
    need(isinstance(binding.get("source_witnesses"), list) and binding["source_witnesses"],
         "scope_binding_invalid", "scope binding has no witnesses")
    for row in binding["source_witnesses"]:
        _witness_shape(row)
    assert_public_pathless(binding)
    return binding


def validate_scope_binding(binding: Any, *, catalog: Any,
                           subject_resolver: SubjectResolver,
                           check_current: bool = True) -> dict[str, Any]:
    """Structural validation plus an optional re-read of exact public authorities."""
    value = _shape(binding)
    if not check_current:
        return value
    evidence = {
        "report_id": value["report_id"],
        "analysis_subject_id": value["analysis_subject_id"],
        "analysis_subject_revision": value["analysis_subject_revision"],
        "expected_input_sha256": value["input_sha256"],
        "expected_result_sha256": value["result_sha256"],
        "accounting_basis": value["accounting_basis"],
        "fiscal_year_end": value["fiscal_year_end"],
        "segment_ids": value["segment_ids"], "measure_kind": value["measure_kind"],
        "currency": value["currency"], "unit": value["unit"], "scale": value["scale"],
        "basis": value["basis"], "covered_coordinates": value["covered_coordinates"],
        "source_witnesses": value["source_witnesses"],
        "limitations": value["limitations"], "verified_at": value["verified_at"],
    }
    rebuilt = build_scope_binding(catalog=catalog, subject_resolver=subject_resolver,
                                  evidence=evidence)
    need(rebuilt == value, "scope_binding_stale",
         "scope binding no longer matches its exact public authorities")
    return value


class ScopeBindingStore:
    """Append-only owner state for public scope bindings; no database, no caps."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.path = self.root / "artifacts" / "report_catalog" / "verified_scope_bindings.jsonl"

    def read(self) -> tuple[list[dict[str, Any]], str | None]:
        if not self.path.exists():
            return [], None
        try:
            raw = self.path.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise ScopeContractError("scope_store_unavailable",
                                     "scope store could not be read") from exc
        need(not raw or raw.endswith("\n"), "scope_store_invalid",
             "scope append line is truncated")
        bindings: list[dict[str, Any]] = []
        ids: set[str] = set()
        coordinates: dict[str, set[tuple[Any, ...]]] = {}
        previous: str | None = None
        for line_text in raw.splitlines():
            try:
                line = json.loads(line_text)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ScopeContractError("scope_store_invalid",
                                         "scope append line is not JSON") from exc
            need(isinstance(line, dict)
                 and set(line) == {"schema_version", "binding", "prev_line_sha256",
                                  "line_sha256"}
                 and line.get("schema_version") == LOG_SCHEMA
                 and line.get("prev_line_sha256") == previous
                 and line.get("line_sha256") == canonical_sha256(
                     {key: value for key, value in line.items() if key != "line_sha256"}),
                 "scope_store_invalid", "scope append chain differs")
            binding = _shape(line["binding"])
            need(binding["binding_id"] not in ids, "scope_store_invalid",
                 "scope binding is duplicated in the append chain")
            ids.add(binding["binding_id"])
            keys = {coordinate_key(row) for row in binding["covered_coordinates"]}
            known = coordinates.setdefault(binding["report_id"], set())
            need(not known.intersection(keys), "scope_binding_conflict",
                 "different bindings cover the same report coordinate")
            known.update(keys)
            bindings.append(binding)
            previous = line["line_sha256"]
        return bindings, previous

    def append(self, binding: dict[str, Any]) -> dict[str, Any]:
        value = _shape(binding)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock = OwnerFileLock(self.path.with_name(self.path.name + ".lock"))
        need(lock.acquire(), "scope_store_busy", "another scope append is active")
        try:
            rows, revision = self.read()
            for existing in rows:
                if existing["binding_id"] == value["binding_id"]:
                    return {"schema_version": READ_SCHEMA, "status": "already_present",
                            "binding": existing, "binding_revision": revision,
                            "reports_registered": 0}
            wanted = {coordinate_key(row) for row in value["covered_coordinates"]}
            need(not any(row["report_id"] == value["report_id"] and wanted.intersection(
                coordinate_key(item) for item in row["covered_coordinates"]) for row in rows),
                "scope_binding_conflict",
                "a different binding already covers this report coordinate")
            line: dict[str, Any] = {"schema_version": LOG_SCHEMA, "binding": value,
                                    "prev_line_sha256": revision}
            line["line_sha256"] = canonical_sha256(line)
            payload = _canonical_bytes(line) + b"\n"
            try:
                with self.path.open("ab") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
            except OSError as exc:
                raise ScopeContractError("scope_store_write_failed",
                                         "scope append could not be committed") from exc
            return {"schema_version": READ_SCHEMA, "status": "appended", "binding": value,
                    "binding_revision": line["line_sha256"], "reports_registered": 0}
        finally:
            lock.release()

    def list_bindings(self, report_id: str) -> tuple[list[dict[str, Any]], str | None]:
        rows, revision = self.read()
        return [row for row in rows if row["report_id"] == report_id], revision


def list_scope_bindings(*, catalog: Any, store: ScopeBindingStore,
                        subject_resolver: SubjectResolver, report_id: str) -> dict[str, Any]:
    """Read-only view; an absent scope store is never created."""
    try:
        response = catalog.get_report(report_id)
    except (CatalogError, OSError) as exc:
        raise ScopeContractError("scope_report_unavailable",
                                 "exact report is unavailable") from exc
    need(isinstance(response, dict) and isinstance(response.get("catalog_revision"), str),
         "scope_report_unavailable", "public catalog revision is absent")
    rows, revision = store.list_bindings(report_id)
    for row in rows:
        validate_scope_binding(row, catalog=catalog, subject_resolver=subject_resolver)
    need(store.read()[1] == revision, "scope_store_changed",
         "scope store changed while resolving")
    view = {"report_id": report_id, "state": "available" if rows else "unavailable",
            "bindings": rows,
            "missing_reason": None if rows else "comparison_scope_binding_absent"}
    return {"schema_version": READ_SCHEMA,
            "catalog_revision": response["catalog_revision"],
            "binding_revision": revision, "scope_view": view}


def exact_scope_pair(*, catalog: Any, store: ScopeBindingStore,
                     subject_resolver: SubjectResolver,
                     request: dict[str, Any]) -> tuple[dict, dict, str | None]:
    rows, revision = store.read()
    selected: list[dict[str, Any]] = []
    for side in ("left", "right"):
        report_id, binding_id = request[f"{side}_report_id"], request[f"{side}_binding_id"]
        matches = [row for row in rows if row["report_id"] == report_id
                   and row["binding_id"] == binding_id]
        need(len(matches) == 1, "scope_binding_not_found",
             "exact scope binding is absent for the requested report")
        validate_scope_binding(matches[0], catalog=catalog,
                               subject_resolver=subject_resolver)
        selected.append(matches[0])
    need(store.read()[1] == revision, "scope_store_changed",
         "scope store changed while resolving")
    return selected[0], selected[1], revision
