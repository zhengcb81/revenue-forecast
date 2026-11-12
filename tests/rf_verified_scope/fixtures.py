"""Synthetic public-wire fixtures for the RF B2 verified-scope contract.

Only public ReportCatalog response shapes are produced here: ``get_report``,
``get_run`` and ``get_source_snapshot``. No catalog internals, neighbouring
repository, production database or company data is involved.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from report_catalog import CatalogError  # noqa: E402

CATALOG_SCHEMA = "rf-report-catalog/1"
VERIFIED_AT = "2026-11-12T00:00:00+00:00"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def number(year: int, value: str, *, scenario: str = "base", period_kind: str = "FY",
           period_start: str | None = None, period_end: str | None = None,
           subject: str | None = "SUBJ-1", currency: str = "USD", unit: str = "currency",
           scale: int = 6, basis: str = "consolidated") -> dict[str, Any]:
    return {"value": value, "currency": currency, "unit": unit, "scale": scale,
            "period_start": period_start, "period_end": period_end,
            "period_kind": period_kind, "fiscal_year": year, "basis": basis,
            "scenario": scenario, "actual_or_forecast": "forecast",
            "analysis_subject_id": subject}


def metric(report_id: str, run_id: str, year: int, value: str, *,
           source_as_of: str = "2026-10-20", **changes: Any) -> dict[str, Any]:
    definition_version = changes.pop("definition_version", "rf-consolidated-revenue/1")
    return {"metric_id": "revenue", "definition_version": definition_version,
            "segment_id": None, "number": number(year, value, **changes),
            "provenance": {"owner": "revenue-forecast", "artifact_id": report_id,
                           "run_id": run_id, "observation_id": None, "source_refs": [],
                           "locator": None, "kind": "calculation", "quality": "owner_validated",
                           "source_as_of": source_as_of,
                           "missing_reason": "line_level_source_binding_unavailable"},
            "quality": "verified", "missing_reason": None}


def company(*, entity_id: str = "ENT-1", listing_id: str = "LST-1",
            subject: str | None = "SUBJ-1") -> dict[str, Any]:
    return {"entity_id": entity_id, "listing_id": listing_id,
            "analysis_subject_id": subject, "resolution_status": "resolved",
            "display_name": "Example Co"}


def side(report_id: str, *, run_id: str | None = None,
         subject: str | None = "SUBJ-1", entity_id: str = "ENT-1",
         listing_id: str = "LST-1", info: str = "2026-10-20",
         metrics: list[dict[str, Any]] | None = None,
         status: str = "validated") -> dict[str, Any]:
    run_id = run_id or f"RUN-{report_id}"
    resolved_company = company(entity_id=entity_id, listing_id=listing_id, subject=subject)
    rows = metrics if metrics is not None else [metric(report_id, run_id, 2025, "10.000000",
                                                      source_as_of=info, subject=subject),
                                                metric(report_id, run_id, 2026, "12.000000",
                                                       source_as_of=info, subject=subject)]
    for row in rows:
        if isinstance(row.get("provenance"), dict):
            row["provenance"]["source_as_of"] = info
    report = {"report_id": report_id, "run_id": run_id, "information_as_of": info,
              "status": status, "company": copy.deepcopy(resolved_company),
              "input_sha256": sha("input-" + report_id),
              "result_sha256": sha("result-" + report_id),
              "schema_version": CATALOG_SCHEMA}
    return {"schema_version": CATALOG_SCHEMA, "catalog_revision": f"REV-{report_id}",
            "view": {"report": report, "metrics": rows},
            "run_response": {"schema_version": CATALOG_SCHEMA,
                             "catalog_revision": f"REV-{report_id}",
                             "run": {"run_id": run_id,
                                     "company": copy.deepcopy(resolved_company)}},
            "input_sha256": report["input_sha256"],
            "result_sha256": report["result_sha256"]}


def make_snapshot(report_id: str, snapshot_id: str, source_id: str, text: str) -> dict[str, Any]:
    raw = text.encode("utf-8")
    return {"schema_version": "rf-report-source-snapshot/1", "report_id": report_id,
            "snapshot_id": snapshot_id, "source_id": source_id,
            "content_sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw),
            "media_type": "text/markdown",
            "content_base64url": base64.urlsafe_b64encode(raw).decode("ascii").rstrip("="),
            "source": {"url": "https://example.invalid/source", "publisher": "example"}}


ROLE_TEXT = {
    "reporting_entity": "The reporting entity is Example Co.",
    "accounting_basis": "These statements follow the stated accounting basis.",
    "revenue_perimeter": "Group revenue covers every disclosed segment.",
    "fiscal_calendar": "The fiscal year ends on the disclosed calendar date.",
}
ROLE_SNAPSHOT = {role: f"SNAP-{role.upper().replace('_', '-')}" for role in ROLE_TEXT}


def witness(role: str, *, source_id: str | None = None,
            snapshot_id: str | None = None, text: str | None = None,
            excerpt: str | None = None, content_sha256: str | None = None) -> dict[str, Any]:
    source_id = source_id or f"SRC-{role.upper().replace('_', '-')}"
    snapshot_id = snapshot_id or ROLE_SNAPSHOT[role]
    text = text if text is not None else ROLE_TEXT[role]
    excerpt = excerpt if excerpt is not None else text
    return {"role": role, "source_id": source_id, "source_snapshot_id": snapshot_id,
            "content_sha256": content_sha256 or hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "excerpt": excerpt, "excerpt_sha256": hashlib.sha256(excerpt.encode("utf-8")).hexdigest()}


def witnesses(**changes: Any) -> list[dict[str, Any]]:
    rows = [witness(role) for role in ROLE_TEXT]
    if changes:
        rows = [dict(row, **changes.get(row["role"], {})) for row in rows]
    return rows


def snapshots_for(report_id: str) -> dict[tuple[str, str], dict[str, Any]]:
    return {(report_id, snapshot_id): make_snapshot(report_id, snapshot_id,
                                                     f"SRC-{role.upper().replace('_', '-')}",
                                                     text)
            for role, (snapshot_id, text) in
            ((role, (ROLE_SNAPSHOT[role], ROLE_TEXT[role])) for role in ROLE_TEXT)}


class FakeCatalog:
    """Public-reader-only catalog double; private attributes are never defined."""

    def __init__(self, *sides: dict[str, Any],
                 snapshots: dict[tuple[str, str], dict[str, Any]] | None = None):
        self.sides = {item["view"]["report"]["report_id"]: item for item in sides}
        self.snapshots = dict(snapshots or {})
        for item in sides:
            report_id = item["view"]["report"]["report_id"]
            for key, value in snapshots_for(report_id).items():
                self.snapshots.setdefault(key, value)
        self.calls: list[tuple[str, str]] = []

    def get_report(self, report_id: str) -> dict[str, Any]:
        self.calls.append(("get_report", report_id))
        item = self.sides.get(report_id)
        if item is None:
            raise CatalogError("not_found", "report ID is not registered")
        return {key: value for key, value in item.items() if key != "run_response"}

    def get_run(self, run_id: str) -> dict[str, Any]:
        self.calls.append(("get_run", run_id))
        for item in self.sides.values():
            if item["run_response"]["run"]["run_id"] == run_id:
                return item["run_response"]
        raise CatalogError("not_found", "run ID is not registered")

    def get_source_snapshot(self, report_id: str, snapshot_id: str) -> dict[str, Any]:
        self.calls.append(("get_source_snapshot", f"{report_id}/{snapshot_id}"))
        snapshot = self.snapshots.get((report_id, snapshot_id))
        if snapshot is None:
            raise CatalogError("not_found", "source snapshot is absent from this exact report")
        return {"schema_version": CATALOG_SCHEMA,
                "catalog_revision": f"REV-{report_id}", "source_snapshot": snapshot}


class PublicOnlyCatalog(FakeCatalog):
    """Any private attribute access is a hard failure, not a silent fallback."""

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AssertionError(f"private catalog member requested: {name}")
        raise AttributeError(name)


def subject_snapshot(*, entity_id: str = "ENT-1", listing_id: str = "LST-1",
                     subject_id: str = "SUBJ-1", revision: int = 3,
                     scope_kind: str = "consolidated_reporting_group",
                     perimeter_coverage: str = "complete_as_disclosed") -> dict[str, Any]:
    members = [{"entity_id": entity_id, "role": "primary_issuer"}]
    return {"schema_version": "rf-report-subject-snapshot/1",
            "entity_id": entity_id, "listing_id": listing_id,
            "analysis_subject_id": subject_id, "analysis_subject_revision": revision,
            "scope_kind": scope_kind, "perimeter_coverage": perimeter_coverage,
            "memberships": members, "evidence_sha256": sha(f"evidence-{subject_id}-{revision}")}


def coordinate(year: int, *, period_kind: str = "FY", period_start: str | None = None,
               period_end: str | None = None, scenario: str = "base",
               metric_id: str = "revenue", basis: str = "consolidated") -> dict[str, Any]:
    return {"metric_id": metric_id, "fiscal_year": year, "period_kind": period_kind,
            "period_start": period_start, "period_end": period_end,
            "scenario": scenario, "basis": basis}


def fy_dates(year: int, fiscal_year_end: str) -> tuple[str, str]:
    """Explicit calendar: a 6-30 year ends in June, a 12-31 year in December."""
    month, day = fiscal_year_end.split("-")
    if month == "12" and day == "31":
        return f"{year}-01-01", f"{year}-12-31"
    return f"{year - 1}-07-01", f"{year}-{month}-{day}"


def evidence(report_id: str, *, coordinates: list[dict[str, Any]] | None = None,
             source_witnesses: list[dict[str, Any]] | None = None,
             accounting_basis: str = "IFRS", fiscal_year_end: str = "12-31",
             segment_ids: list[str] | None = None,
             analysis_subject_id: str = "SUBJ-1", analysis_subject_revision: int = 3,
             measure_kind: str = "group_reported_total_as_disclosed",
             currency: str = "USD", unit: str = "currency", scale: int = 6,
             basis: str = "consolidated", limitations: list[str] | None = None,
             verified_at: str = VERIFIED_AT) -> dict[str, Any]:
    start, end = fy_dates(2025, fiscal_year_end)
    rows = coordinates if coordinates is not None else [
        coordinate(2025, period_start=start, period_end=end),
        coordinate(2026, period_start=fy_dates(2026, fiscal_year_end)[0],
                   period_end=fy_dates(2026, fiscal_year_end)[1]),
    ]
    return {"report_id": report_id,
            "analysis_subject_id": analysis_subject_id,
            "analysis_subject_revision": analysis_subject_revision,
            "expected_input_sha256": sha("input-" + report_id),
            "expected_result_sha256": sha("result-" + report_id),
            "accounting_basis": accounting_basis, "fiscal_year_end": fiscal_year_end,
            "segment_ids": segment_ids if segment_ids is not None else ["SEG-A", "SEG-B"],
            "measure_kind": measure_kind, "currency": currency, "unit": unit,
            "scale": scale, "basis": basis, "covered_coordinates": rows,
            "source_witnesses": source_witnesses if source_witnesses is not None else witnesses(),
            "limitations": limitations if limitations is not None else [],
            "verified_at": verified_at}


def write_subject_fixture(path: Path, *snapshots: dict[str, Any]) -> None:
    path.write_text(json.dumps({"schema_version": "rf-subject-snapshot-fixture/1",
                                "snapshots": list(snapshots)}, ensure_ascii=False,
                               sort_keys=True, separators=(",", ":")), encoding="utf-8")
