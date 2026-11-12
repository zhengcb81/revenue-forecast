"""Shared controlled B2 setup: public catalog wire only, no production state."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from rf_verified_scope import fixtures as fx


def _build_env(tmp_path: Path, *, accounting_basis: str = "IFRS",
              fiscal_year_end: str = "12-31", segment_ids: list[str] | None = None,
              years: tuple[int, ...] = (2025, 2026), period_kind: str = "FY",
              explicit_dates: bool = True,
              scenario: str = "base", left_subject: str | None = "SUBJ-1",
              right_subject: str | None = "SUBJ-1", verified_subject: str = "SUBJ-1",
              left_revision: int = 3, right_revision: int = 3,
              left_witnesses: list[dict[str, Any]] | None = None,
              right_witnesses: list[dict[str, Any]] | None = None,
              left_coordinates: list[dict[str, Any]] | None = None,
              right_coordinates: list[dict[str, Any]] | None = None,
              long_excerpt: str | None = None) -> dict[str, Any]:
    from report_catalog_scope_binding import ScopeBindingStore, build_scope_binding
    from report_catalog_subject_resolver import FrozenSubjectResolver, validate_subject_snapshot

    def calendar(year: int) -> tuple[str | None, str | None]:
        if not explicit_dates:
            return None, None
        start, end = fx.fy_dates(year, fiscal_year_end)
        if period_kind == "H1":
            return f"{year}-01-01", f"{year}-06-30"
        return start, end

    def coordinates() -> list[dict[str, Any]]:
        return [fx.coordinate(year, period_kind=period_kind, period_start=calendar(year)[0],
                              period_end=calendar(year)[1], scenario=scenario)
                for year in years]

    def rows(report_id: str, run_id: str, first: int, subject: str | None,
             info: str) -> list[dict[str, Any]]:
        return [fx.metric(report_id, run_id, year, f"{first + index}.000000",
                          period_kind=period_kind, period_start=calendar(year)[0],
                          period_end=calendar(year)[1], scenario=scenario, subject=subject,
                          source_as_of=info)
                for index, year in enumerate(years)]

    left_rows = rows("R-OLD", "RUN-R-OLD", 10, left_subject, "2026-10-20")
    right_rows = rows("R-NEW", "RUN-R-NEW", 13, right_subject, "2026-10-28")
    left_side = fx.side("R-OLD", subject=left_subject, info="2026-10-20", metrics=left_rows)
    right_side = fx.side("R-NEW", subject=right_subject, info="2026-10-28", metrics=right_rows)

    overrides: dict[tuple[str, str], dict[str, Any]] = {}
    witness_rows: dict[str, list[dict[str, Any]]] = {}
    for report_id, supplied in (("R-OLD", left_witnesses), ("R-NEW", right_witnesses)):
        source_rows = supplied if supplied is not None else fx.witnesses()
        if long_excerpt is not None:
            role = "revenue_perimeter"
            source_rows = [dict(row) for row in source_rows if row["role"] != role]
            source_rows.append(fx.witness(role, text=long_excerpt, excerpt=long_excerpt))
            snapshot_id = fx.ROLE_SNAPSHOT[role]
            overrides[(report_id, snapshot_id)] = fx.make_snapshot(
                report_id, snapshot_id, f"SRC-{role.upper().replace('_', '-')}", long_excerpt)
        witness_rows[report_id] = source_rows

    catalog = fx.PublicOnlyCatalog(left_side, right_side, snapshots=overrides)
    snapshots = [validate_subject_snapshot(fx.subject_snapshot(
        subject_id=verified_subject, revision=left_revision)),
        validate_subject_snapshot(fx.subject_snapshot(
            subject_id=verified_subject, revision=right_revision))]
    resolver = FrozenSubjectResolver(snapshots)
    store = ScopeBindingStore(tmp_path / "owner-data")

    def make_binding(report_id: str, revision: int, source_rows: list[dict[str, Any]],
                     coords: list[dict[str, Any]] | None) -> dict[str, Any]:
        payload = fx.evidence(report_id, coordinates=coords if coords is not None else coordinates(),
                              source_witnesses=source_rows, accounting_basis=accounting_basis,
                              fiscal_year_end=fiscal_year_end, segment_ids=segment_ids,
                              analysis_subject_id=verified_subject,
                              analysis_subject_revision=revision)
        return build_scope_binding(catalog=catalog, subject_resolver=resolver, evidence=payload)

    left = make_binding("R-OLD", left_revision, witness_rows["R-OLD"], left_coordinates)
    right = make_binding("R-NEW", right_revision, witness_rows["R-NEW"], right_coordinates)
    store.append(left)
    store.append(right)
    request = {"left_report_id": "R-OLD", "right_report_id": "R-NEW",
               "scenario": scenario, "metric_ids": ["revenue"],
               "left_binding_id": left["binding_id"], "right_binding_id": right["binding_id"]}
    return {"catalog": catalog, "resolver": resolver, "store": store, "left": left,
            "right": right, "request": request, "years": years,
            "left_evidence": fx.evidence("R-OLD"), "tmp_path": tmp_path}


@pytest.fixture
def build_env():
    """Expose the controlled setup factory as a pytest fixture."""
    return _build_env
