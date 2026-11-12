"""Public verified-scope comparison over the unchanged exact-report comparator.

This module is a consumer of ``compare_reports`` and the public scope/subject
readers. It does not import the comparator's private helpers, does not edit
frozen reports, and does not invent a second comparison arithmetic. The
current verified subject is applied only to an internal adapter view; the
canonical left/right metric rows in the response are always the originals.
"""
from __future__ import annotations

import copy
from typing import Any

from report_catalog_compare import compare_reports, validate_request
from report_catalog_scope_binding import (
    BINDING_ID, NOTE, ScopeBindingStore, assert_public_pathless, coordinate_key,
    exact_scope_pair,
)
from report_catalog_subject_resolver import SubjectResolver, need

SCHEMA_VERSION = "rf-verified-scope-comparison/1"
BASE_KEYS = frozenset({"left_report_id", "right_report_id", "scenario", "metric_ids"})
MISMATCH_FIELDS = (
    "entity_id", "listing_id", "analysis_subject_id", "analysis_subject_revision",
    "subject_snapshot_sha256", "accounting_basis", "fiscal_year_end", "segment_ids",
    "measure_kind", "currency", "unit", "scale", "basis",
)
DIMENSION_FIELDS = ("currency", "unit", "scale", "basis")


def validate_verified_request(value: Any) -> dict[str, Any]:
    """Six exact public fields; the four base ones keep the published contract."""
    need(isinstance(value, dict)
         and set(value) == BASE_KEYS | {"left_binding_id", "right_binding_id"},
         "invalid_request", "verified comparison request fields differ")
    validate_request({key: value[key] for key in BASE_KEYS})
    need(all(isinstance(value[key], str) and BINDING_ID.fullmatch(value[key])
             for key in ("left_binding_id", "right_binding_id")),
         "invalid_request", "comparison must select exact immutable scope bindings")
    return value


class _EffectiveSubjectCatalog:
    """Public-reader adapter that presents the verified subject to the comparator."""

    def __init__(self, catalog: Any, subjects: dict[str, str], run_subjects: dict[str, str]):
        self._catalog = catalog
        self._subjects = subjects
        self._run_subjects = run_subjects

    def get_report(self, report_id: str) -> dict[str, Any]:
        response = copy.deepcopy(self._catalog.get_report(report_id))
        subject = self._subjects.get(report_id)
        view = response.get("view") if isinstance(response, dict) else None
        if subject is not None and isinstance(view, dict) and isinstance(view.get("report"), dict):
            company = view["report"].get("company")
            if isinstance(company, dict):
                company["analysis_subject_id"] = subject
            metrics = view.get("metrics")
            if isinstance(metrics, list):
                for row in metrics:
                    if isinstance(row, dict) and isinstance(row.get("number"), dict):
                        row["number"]["analysis_subject_id"] = subject
        return response

    def get_run(self, run_id: str) -> dict[str, Any]:
        response = copy.deepcopy(self._catalog.get_run(run_id))
        subject = self._run_subjects.get(run_id)
        run = response.get("run") if isinstance(response, dict) else None
        if subject is not None and isinstance(run, dict) and isinstance(run.get("company"), dict):
            run["company"]["analysis_subject_id"] = subject
        return response


def _row_coordinate(metric_id: str, row: dict[str, Any] | None) -> tuple[Any, ...] | None:
    if row is None:
        return None
    number = row.get("number")
    if not isinstance(number, dict):
        raise ValueError("owner comparison row has no public number")
    return coordinate_key({"metric_id": metric_id,
                           "fiscal_year": number.get("fiscal_year"),
                           "period_kind": number.get("period_kind"),
                           "period_start": number.get("period_start"),
                           "period_end": number.get("period_end"),
                           "scenario": number.get("scenario"),
                           "basis": number.get("basis")})


def compare_verified_scope(request: Any, *, catalog: Any,
                           subject_resolver: SubjectResolver,
                           store: ScopeBindingStore) -> dict[str, Any]:
    """Compare two exact reports only where a current verified scope covers both."""
    validated = validate_verified_request(request)
    left, right, binding_revision = exact_scope_pair(
        catalog=catalog, store=store, subject_resolver=subject_resolver, request=validated)
    base = {key: validated[key] for key in BASE_KEYS}
    original = compare_reports(base, catalog=catalog)
    subjects = {left["report_id"]: left["analysis_subject_id"],
                right["report_id"]: right["analysis_subject_id"]}
    run_subjects = {left["run_id"]: left["analysis_subject_id"],
                    right["run_id"]: right["analysis_subject_id"]}
    effective = compare_reports(base, catalog=_EffectiveSubjectCatalog(
        catalog, subjects, run_subjects))

    scope_reasons = [f"scope_{field}_mismatch" for field in MISMATCH_FIELDS
                     if left[field] != right[field]]
    covered_keys = {
        "left": {coordinate_key(row) for row in left["covered_coordinates"]},
        "right": {coordinate_key(row) for row in right["covered_coordinates"]},
    }
    original_rows = original["comparison"]["metrics"]
    effective_rows = effective["comparison"]["metrics"]
    need(len(original_rows) == len(effective_rows), "scope_comparison_shape_mismatch",
         "public comparison shape changed between the original and verified views")
    rows: list[dict[str, Any]] = []
    for original_row, effective_row in zip(original_rows, effective_rows):
        need(original_row["metric_id"] == effective_row["metric_id"],
             "scope_comparison_shape_mismatch", "comparison metric order differs")
        extra: list[str] = []
        for side, binding in (("left", left), ("right", right)):
            key = _row_coordinate(original_row["metric_id"], original_row[side])
            if key is None or key not in covered_keys[side]:
                extra.append(f"{side}_scope_coordinate_not_covered")
                continue
            number = original_row[side]["number"]
            if any(number.get(field) != binding[field] for field in DIMENSION_FIELDS):
                extra.append(f"{side}_scope_metric_dimensions_mismatch")
            if number.get("analysis_subject_id") != binding["original_analysis_subject_id"]:
                extra.append(f"{side}_scope_subject_mismatch")
        reasons = sorted(set(list(effective_row["reasons"]) + scope_reasons + extra))
        comparable = bool(effective_row["comparable"]) and not scope_reasons and not extra
        rows.append({**effective_row, "left": original_row["left"],
                     "right": original_row["right"],
                     "delta": effective_row["delta"] if comparable else None,
                     "comparable": comparable, "reasons": reasons})
    output = {**original["comparison"], "metrics": rows,
              "scope_resolution": {"method": "current_verified_scope",
                                   "left_binding": left, "right_binding": right,
                                   "note": NOTE}}
    assert_public_pathless(output)
    need(store.read()[1] == binding_revision, "scope_store_changed",
         "scope store changed during comparison")
    return {"schema_version": SCHEMA_VERSION,
            "catalog_revisions": original["catalog_revisions"],
            "binding_revision": binding_revision, "comparison": output}
