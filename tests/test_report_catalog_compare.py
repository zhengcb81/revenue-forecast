"""Tests for G-RF-COMPARE-01; fake owner DTOs are synthetic, not production data."""
from __future__ import annotations

import copy
import io
import json
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from report_catalog import CatalogError, ReportCatalog  # noqa: E402
from report_catalog_compare import CompareError, compare_reports  # noqa: E402
import report_catalog_compare_cli as cli  # noqa: E402


def number(year: int, value: str, *, scenario: str = "base", **changes: Any) -> dict[str, Any]:
    result = {"value": value, "currency": "USD", "unit": "currency", "scale": 6,
              "period_start": None, "period_end": None, "period_kind": "FY",
              "fiscal_year": year, "basis": "consolidated", "scenario": scenario,
              "actual_or_forecast": "forecast", "analysis_subject_id": "SUBJ-1"}
    result.update(changes)
    return result


def metric(report_id: str, run_id: str, year: int, value: str, *, scenario: str = "base",
           source_as_of: str = "2026-10-20", **changes: Any) -> dict[str, Any]:
    definition_version = changes.pop("definition_version", "rf-consolidated-revenue/1")
    record = {"metric_id": "revenue", "definition_version": definition_version,
              "segment_id": None, "number": number(year, value, scenario=scenario, **changes),
              "provenance": {"owner": "revenue-forecast", "artifact_id": report_id,
                             "run_id": run_id, "observation_id": None, "source_refs": [],
                             "locator": None, "kind": "calculation", "quality": "owner_validated",
                             "source_as_of": source_as_of,
                             "missing_reason": "line_level_source_binding_unavailable"},
              "quality": "verified", "missing_reason": None}
    return record


def side(report_id: str, *, run_id: str | None = None, revision: str | None = None,
         info: str = "2026-10-20", metrics: list[dict[str, Any]] | None = None,
         company: dict[str, Any] | None = None, status: str = "validated") -> dict[str, Any]:
    run_id = run_id or f"RUN-{report_id}"
    company = company or {"entity_id": "ENT-1", "listing_id": "LST-1",
                          "analysis_subject_id": "SUBJ-1", "resolution_status": "resolved",
                          "display_name": "Example Co"}
    metrics = metrics if metrics is not None else [metric(report_id, run_id, 2025, "10.000000",
                                                           source_as_of=info),
                                                     metric(report_id, run_id, 2026, "12.000000",
                                                           source_as_of=info)]
    for row in metrics:
        if isinstance(row.get("provenance"), dict):
            row["provenance"]["source_as_of"] = info
    report = {"report_id": report_id, "run_id": run_id, "information_as_of": info,
              "status": status, "company": copy.deepcopy(company)}
    view = {"report": report, "metrics": metrics}
    run = {"run_id": run_id, "company": copy.deepcopy(company)}
    return {"schema_version": "rf-report-catalog/1", "catalog_revision": revision or f"REV-{report_id}",
            "view": view, "run_response": {"schema_version": "rf-report-catalog/1",
                                             "catalog_revision": revision or f"REV-{report_id}", "run": run}}


class FakeCatalog:
    def __init__(self, *sides: dict[str, Any]):
        self.sides = {item["view"]["report"]["report_id"]: item for item in sides}
        self.calls: list[tuple[str, str]] = []

    def get_report(self, report_id: str) -> dict[str, Any]:
        self.calls.append(("report", report_id))
        if report_id not in self.sides:
            raise CatalogError("not_found", "private path must not escape")
        item = self.sides[report_id]
        return {key: value for key, value in item.items() if key != "run_response"}

    def get_run(self, run_id: str) -> dict[str, Any]:
        self.calls.append(("run", run_id))
        for item in self.sides.values():
            if item["run_response"]["run"]["run_id"] == run_id:
                return item["run_response"]
        raise CatalogError("not_found", "missing")


def request(**changes: Any) -> dict[str, Any]:
    value = {"left_report_id": "R-OLD", "right_report_id": "R-NEW",
             "scenario": "base", "metric_ids": ["revenue"]}
    value.update(changes)
    return value


def test_multiple_years_pair_by_explicit_period_and_right_minus_left():
    left = side("R-OLD", info="2026-10-20")
    right = side("R-NEW", info="2026-10-28",
                 metrics=[metric("R-NEW", "RUN-R-NEW", 2026, "15.000000"),
                          metric("R-NEW", "RUN-R-NEW", 2025, "13.000000")])
    catalog = FakeCatalog(left, right)
    result = compare_reports(request(), catalog=catalog)
    comparison = result["comparison"]
    assert comparison["left_information_as_of"] == "2026-10-20"
    assert comparison["right_information_as_of"] == "2026-10-28"
    assert [(row["left"]["number"]["fiscal_year"], row["delta"]["value"])
            for row in comparison["metrics"]] == [(2025, "3.000000"), (2026, "3.000000")]
    assert all(row["metric_id"] == "revenue" for row in comparison["metrics"])
    assert result["catalog_revisions"] == {"left": "REV-R-OLD", "right": "REV-R-NEW"}
    assert catalog.calls == [("report", "R-OLD"), ("run", "RUN-R-OLD"),
                             ("report", "R-NEW"), ("run", "RUN-R-NEW")]


def test_reverse_period_order_produces_stable_output():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2026, "12"),
                                   metric("R-OLD", "RUN-R-OLD", 2025, "10")])
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "13"),
                                     metric("R-NEW", "RUN-R-NEW", 2026, "15")])
    rows = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"]
    assert [item["left"]["number"]["fiscal_year"] for item in rows] == [2025, 2026]


def test_three_year_repeated_revenue_ids_pair_one_row_per_year():
    years = [2025, 2026, 2027]
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", year, value)
                                  for year, value in zip(years, ["10", "20", "30"])])
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", year, value)
                                   for year, value in zip(reversed(years), ["33", "22", "11"])])
    rows = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"]
    assert [row["left"]["number"]["fiscal_year"] for row in rows] == years
    assert [row["right"]["number"]["fiscal_year"] for row in rows] == years
    assert [row["delta"]["value"] for row in rows] == ["1", "2", "3"]
    assert len({(row["left"]["number"]["fiscal_year"], row["right"]["number"]["fiscal_year"])
                for row in rows}) == 3


def test_missing_year_keeps_one_missing_side_and_never_zero_fills():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10")])
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2026, "12")])
    rows = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"]
    assert len(rows) == 2
    assert rows[0]["left"]["number"]["fiscal_year"] == 2025 and rows[0]["right"] is None
    assert rows[1]["left"] is None and rows[1]["right"]["number"]["fiscal_year"] == 2026
    assert all(not item["comparable"] and item["delta"] is None and item["reasons"] for item in rows)
    assert "right_metric_missing_for_period" in rows[0]["reasons"]
    assert "left_metric_missing_for_period" in rows[1]["reasons"]


def test_ambiguous_same_semantic_period_fails_instead_of_last_wins():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10"),
                                   metric("R-OLD", "RUN-R-OLD", 2025, "11")])
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=FakeCatalog(left, side("R-NEW")))
    assert error.value.code == "ambiguous_metric"


@pytest.mark.parametrize(("field", "left_value", "right_value", "reason"), [
    ("definition_version", "rf-consolidated-revenue/1", "rf-consolidated-revenue/2", "definition_version_mismatch"),
    ("unit", "currency", "ratio", "unit_mismatch"),
    ("currency", "USD", "CNY", "currency_mismatch"),
    ("currency", "unknown", "unknown", "currency_unknown"),
    ("currency", "UNKNOWN", "UNKNOWN", "currency_unknown"),
    ("currency", " unknown ", " unknown ", "currency_unknown"),
    ("period_start", "unknown", "unknown", "period_start_unknown"),
    ("period_end", "unknown", "unknown", "period_end_unknown"),
    ("period_start", "2026-13-01", "2026-13-01", "period_start_invalid"),
    ("scale", 6, 8, "scale_mismatch"),
    ("basis", "consolidated", "segment", "basis_mismatch"),
    ("basis", "unknown", "unknown", "basis_unknown"),
    ("actual_or_forecast", "forecast", "actual", "actual_or_forecast_mismatch"),
    ("actual_or_forecast", "unknown", "unknown", "actual_or_forecast_unknown"),
])
def test_known_dimension_mismatch_is_not_converted(field: str, left_value: Any,
                                                    right_value: Any, reason: str):
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10", **{field: left_value})])
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "12", **{field: right_value})])
    row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
    assert row["comparable"] is False and row["delta"] is None and reason in row["reasons"]


def test_unknown_canonical_identity_prevents_comparison_even_when_both_null():
    company = {"entity_id": "ENT-1", "listing_id": None, "analysis_subject_id": None,
               "resolution_status": "resolved", "display_name": "Example Co"}
    left = side("R-OLD", company=company, metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10",
                                                               analysis_subject_id=None)])
    right = side("R-NEW", company=company, metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "12",
                                                               analysis_subject_id=None)])
    row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
    assert not row["comparable"] and row["delta"] is None
    assert "canonical_listing_unknown" in row["reasons"]
    assert "canonical_subject_unknown" in row["reasons"]


def test_unresolved_company_identity_is_incompatible_not_comparable():
    company = {"entity_id": "ENT-1", "listing_id": None, "analysis_subject_id": None,
               "resolution_status": "unknown", "display_name": "Example Co"}
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=FakeCatalog(side("R-OLD", company=company),
                                                       side("R-NEW")))
    assert error.value.code == "incompatible"


def test_literal_unknown_entity_or_listing_is_not_known_identity():
    for field, reason in (("entity_id", "canonical_entity_unknown"),
                          ("listing_id", "canonical_listing_unknown")):
        company = {"entity_id": "ENT-1", "listing_id": "LST-1",
                   "analysis_subject_id": "SUBJ-1", "resolution_status": "resolved",
                   "display_name": "Example Co"}
        company[field] = "unknown"
        row = compare_reports(request(), catalog=FakeCatalog(
            side("R-OLD", company=company), side("R-NEW", company=company)))
        first = row["comparison"]["metrics"][0]
        assert first["comparable"] is False and first["delta"] is None
        assert reason in first["reasons"]


def test_non_consolidated_basis_is_out_of_top_level_scope():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10",
                                         basis="segment")])
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "12",
                                          basis="segment")])
    row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
    assert row["comparable"] is False and row["delta"] is None
    assert "left_basis_not_consolidated" in row["reasons"]
    assert "right_basis_not_consolidated" in row["reasons"]


def test_entity_mismatch_and_null_entity_are_named():
    other = {"entity_id": "ENT-2", "listing_id": "LST-1",
             "analysis_subject_id": "SUBJ-1", "resolution_status": "resolved",
             "display_name": "Other Co"}
    row = compare_reports(request(), catalog=FakeCatalog(side("R-OLD"),
                                                         side("R-NEW", company=other)))
    reasons = row["comparison"]["metrics"][0]["reasons"]
    assert row["comparison"]["metrics"][0]["comparable"] is False
    assert "canonical_entity_mismatch" in reasons


def test_listing_and_subject_mismatch_are_named_non_comparable():
    other_listing = {"entity_id": "ENT-1", "listing_id": "LST-2",
                     "analysis_subject_id": "SUBJ-1", "resolution_status": "resolved",
                     "display_name": "Example Co"}
    row = compare_reports(request(), catalog=FakeCatalog(side("R-OLD"),
                                                         side("R-NEW", company=other_listing)))
    assert row["comparison"]["metrics"][0]["comparable"] is False
    assert "canonical_listing_mismatch" in row["comparison"]["metrics"][0]["reasons"]

    other_subject = {"entity_id": "ENT-1", "listing_id": "LST-1",
                     "analysis_subject_id": "SUBJ-2", "resolution_status": "resolved",
                     "display_name": "Example Co"}
    right = side("R-NEW", company=other_subject,
                 metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "12",
                                 analysis_subject_id="SUBJ-2")])
    row = compare_reports(request(), catalog=FakeCatalog(side("R-OLD"), right))
    assert row["comparison"]["metrics"][0]["comparable"] is False
    assert "canonical_subject_mismatch" in row["comparison"]["metrics"][0]["reasons"]


def test_period_and_date_precision_are_preserved():
    left = side("R-OLD", info="2026-10-20T23:59:59+08:00",
                metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10")])
    right = side("R-NEW", info="2026-10-28",
                 metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "12")])
    result = compare_reports(request(), catalog=FakeCatalog(left, right))
    assert result["comparison"]["left_information_as_of"] == "2026-10-20T23:59:59+08:00"
    assert result["comparison"]["right_information_as_of"] == "2026-10-28"


def test_metric_provenance_must_bind_exact_side_report_and_run():
    left = side("R-OLD")
    left["view"]["metrics"][0]["provenance"]["artifact_id"] = "R-NEW"
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=FakeCatalog(left, side("R-NEW")))
    assert error.value.code == "incompatible"


def test_wrong_run_identity_cannot_be_silently_used():
    left = side("R-OLD")
    left["view"]["report"]["company"]["entity_id"] = "ENT-OTHER"
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=FakeCatalog(left, side("R-NEW")))
    assert error.value.code == "incompatible"


def test_metric_provenance_run_id_replacement_is_refused():
    left = side("R-OLD")
    left["view"]["metrics"][0]["provenance"]["run_id"] = "RUN-R-NEW"
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=FakeCatalog(left, side("R-NEW")))
    assert error.value.code == "incompatible"


def test_metric_subject_must_match_its_own_run_company():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10",
                                         analysis_subject_id="SUBJ-OTHER")])
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=FakeCatalog(left, side("R-NEW")))
    assert error.value.code == "incompatible"


def test_unknown_metric_or_scenario_does_not_succeed_empty():
    with pytest.raises(CompareError) as unknown_metric:
        compare_reports(request(metric_ids=["made_up"]), catalog=FakeCatalog(side("R-OLD"), side("R-NEW")))
    assert unknown_metric.value.code == "unknown_metric"
    with pytest.raises(CompareError) as unknown_scenario:
        compare_reports(request(scenario="stress"), catalog=FakeCatalog(side("R-OLD"), side("R-NEW")))
    assert unknown_scenario.value.code == "unknown_scenario"
    legacy = side("R-OLD", status="legacy", metrics=[])
    with pytest.raises(CompareError) as legacy_unknown_scenario:
        compare_reports(request(scenario="stress"), catalog=FakeCatalog(legacy, side("R-NEW")))
    assert legacy_unknown_scenario.value.code == "unknown_scenario"


def test_legacy_missing_metrics_are_retained_as_explicit_non_comparable_row():
    left = side("R-OLD", status="legacy", metrics=[])
    right = side("R-NEW", status="legacy", metrics=[])
    row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
    assert row["left"] is None and row["right"] is None and row["delta"] is None
    assert not row["comparable"] and "left_legacy_metrics_unavailable" in row["reasons"]


def test_legacy_with_malformed_metric_rows_stays_legacy_not_delta():
    left = side("R-OLD", status="legacy", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10")])
    right = side("R-NEW", status="legacy", metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "12")])
    rows = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"]
    assert len(rows) == 1
    assert rows[0]["left"] is None and rows[0]["right"] is None and rows[0]["delta"] is None
    assert "left_legacy_metrics_unavailable" in rows[0]["reasons"]
    assert "right_legacy_metrics_unavailable" in rows[0]["reasons"]


def test_null_metric_value_is_unavailable_not_a_crash_or_zero():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10")])
    left["view"]["metrics"][0]["number"]["value"] = None
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "12")])
    row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
    assert row["comparable"] is False and row["delta"] is None
    assert "left_value_unavailable" in row["reasons"]


def test_invalid_period_kind_is_incompatible():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "10",
                                         period_kind="FYE")])
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=FakeCatalog(left, side("R-NEW")))
    assert error.value.code == "incompatible"


def test_exact_decimal_large_small_zero_left_and_low_ambient_precision():
    from decimal import Decimal, getcontext
    old_precision = getcontext().prec
    getcontext().prec = 2
    try:
        left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025,
                                               "0.00000000000000000000000000000000000001")])
        right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2025,
                                                "123456789012345678901234567890.00000000000000000000000000000000000002")])
        row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
        assert row["comparable"] is True
        assert Decimal(row["delta"]["value"]) == Decimal(
            "123456789012345678901234567890.00000000000000000000000000000000000001")
        assert "e" not in row["delta"]["value"].lower()
    finally:
        getcontext().prec = old_precision


def test_zero_left_yields_exact_delta_not_division():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "0.000000")])
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "12.500000")])
    row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
    assert row["comparable"] is True and row["delta"]["value"] == "12.500000"


def test_explicit_iso_period_dates_remain_comparable():
    changes = {"period_start": "2026-01-01", "period_end": "2026-12-31"}
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2026, "10", **changes)])
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2026, "12", **changes)])
    row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
    assert row["comparable"] is True and row["delta"]["value"] == "2"


def test_signed_zero_delta_is_preserved_not_normalized():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "0.0")])
    right = side("R-NEW", metrics=[metric("R-NEW", "RUN-R-NEW", 2025, "-0.0")])
    row = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]["metrics"][0]
    assert row["comparable"] is True
    assert row["delta"]["value"] == "-0.0"


def _large_comparison_result():
    years = list(range(1000, 1600))
    left_rows = [metric("R-OLD", "RUN-R-OLD", year, "10") for year in years]
    right_rows = [metric("R-NEW", "RUN-R-NEW", year, "11") for year in years]
    for row in left_rows + right_rows:
        row["provenance"]["locator"] = "source-section-" + ("x" * 1100)
    left = side("R-OLD", metrics=left_rows)
    right = side("R-NEW", metrics=right_rows)
    return compare_reports(request(), catalog=FakeCatalog(left, right))


def test_large_comparison_returns_every_period_and_full_provenance():
    result = _large_comparison_result()
    rows = result["comparison"]["metrics"]
    assert len(rows) == 600
    assert [row["left"]["number"]["fiscal_year"] for row in rows] == list(range(1000, 1600))
    assert all(row["left"]["provenance"]["locator"].endswith("x" * 1100) and
               row["right"]["provenance"]["locator"].endswith("x" * 1100) for row in rows)


def test_invalid_decimal_fails_without_silent_rounding():
    left = side("R-OLD", metrics=[metric("R-OLD", "RUN-R-OLD", 2025, "1e3")])
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=FakeCatalog(left, side("R-NEW")))
    assert error.value.code == "decimal_invalid"


def test_catalog_errors_are_distinguished_and_pathless(tmp_path):
    private = str(tmp_path / "private" / "catalog.jsonl")

    class Missing:
        def get_report(self, report_id: str) -> dict[str, Any]:
            raise CatalogError("not_found", private)
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=Missing())  # type: ignore[arg-type]
    assert error.value.code == "not_found"
    assert "private" not in str(error.value)

    class Offline:
        def get_report(self, report_id: str) -> dict[str, Any]:
            raise CatalogError("catalog_unavailable", private)
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=Offline())  # type: ignore[arg-type]
    assert error.value.code == "unavailable" and "private" not in str(error.value)


def test_cli_rejects_duplicates_nonfinite_oversize_and_arbitrary_args(monkeypatch, capsys, tmp_path):
    # Use a binary stdin shim because the public CLI reads bytes, not text.
    class BinaryInput:
        def __init__(self, raw: bytes):
            self.buffer = io.BytesIO(raw)
    monkeypatch.setattr(cli.sys, "stdin", BinaryInput(b'{"left_report_id":"R-OLD","left_report_id":"R-OLD"}'))
    assert cli.main(["compare"]) == 2
    assert json.loads(capsys.readouterr().err)["error"]["code"] == "invalid_json"
    monkeypatch.setattr(cli.sys, "stdin", BinaryInput(b'{"x":NaN}'))
    assert cli.main(["compare"]) == 2
    assert json.loads(capsys.readouterr().err)["error"]["code"] == "invalid_json"
    monkeypatch.setattr(cli.sys, "stdin", BinaryInput(b"x" * (cli.MAX_INPUT_BYTES + 1)))
    assert cli.main(["compare"]) == 2
    assert json.loads(capsys.readouterr().err)["error"]["code"] == "input_too_large"
    assert cli.main(["compare", "--catalog-file", str(tmp_path / "secret")]) == 2
    emitted = capsys.readouterr()
    assert emitted.out == ""
    assert json.loads(emitted.err)["error"]["code"] == "invalid_command"
    assert str(tmp_path) not in emitted.err and "secret" not in emitted.err


def test_cli_deeply_nested_json_fails_closed(monkeypatch, capsys):
    class BinaryInput:
        def __init__(self, raw: bytes):
            self.buffer = io.BytesIO(raw)

    monkeypatch.setattr(cli.sys, "stdin", BinaryInput(b"[" * 6000 + b"]" * 6000))
    assert cli.main(["compare"]) == 2
    emitted = capsys.readouterr()
    assert emitted.out == ""
    assert json.loads(emitted.err)["error"]["code"] == "invalid_json"


def test_missing_catalog_is_not_found_and_writes_nothing(tmp_path):
    catalog = ReportCatalog(root=tmp_path, catalog_file=tmp_path / "catalog.jsonl")
    with pytest.raises(CompareError) as error:
        compare_reports(request(), catalog=catalog)
    assert error.value.code == "not_found"
    assert not (tmp_path / "catalog.jsonl").exists()
    assert not (tmp_path / "catalog.jsonl.lock").exists()


def test_public_cli_subprocess_transport_smoke():
    managed = ROOT / "artifacts" / "report_catalog" / "catalog.jsonl"
    if managed.exists():
        pytest.skip("managed production catalog exists; subprocess smoke must not read it")
    import subprocess

    payload = json.dumps(request()).encode("utf-8")
    completed = subprocess.run(
        [sys.executable, "-B", "scripts/report_catalog_compare_cli.py", "compare"],
        input=payload, capture_output=True, cwd=ROOT, timeout=60,
    )
    assert completed.returncode == 2
    assert completed.stdout == b""
    error = json.loads(completed.stderr.decode("utf-8"))
    assert error["schema_version"] == "rf-report-comparison/1"
    assert error["error"]["code"] == "not_found"
    assert "report_catalog" not in error["error"]["message"]
    assert not managed.exists()


def test_cli_success_envelope_keeps_comparison_fields_exact(monkeypatch, capsys):
    import report_catalog_compare as compare_module

    fake = FakeCatalog(side("R-OLD", info="2026-10-20"),
                       side("R-NEW", info="2026-10-28"))
    monkeypatch.setattr(compare_module, "ReportCatalog", lambda: fake)

    class BinaryInput:
        def __init__(self, raw: bytes):
            self.buffer = io.BytesIO(raw)

    payload = json.dumps(request()).encode("utf-8")
    monkeypatch.setattr(cli.sys, "stdin", BinaryInput(payload))
    assert cli.main(["compare"]) == 0
    emitted = capsys.readouterr()
    result = json.loads(emitted.out)
    assert set(result) == {"schema_version", "comparison", "catalog_revisions"}
    assert result["schema_version"] == "rf-report-comparison/1"
    assert result["catalog_revisions"] == {"left": "REV-R-OLD", "right": "REV-R-NEW"}
    comparison = result["comparison"]
    assert set(comparison) == {"left_report_id", "right_report_id", "left_information_as_of",
                               "right_information_as_of", "metrics", "explained_changes",
                               "unproven_changes"}
    assert comparison["explained_changes"] == []
    assert comparison["unproven_changes"]


def test_cli_writes_complete_response_larger_than_one_megabyte(monkeypatch, capsys):
    result = _large_comparison_result()
    monkeypatch.setattr(cli, "build_catalog", lambda _: object())
    monkeypatch.setattr(cli, "compare_reports", lambda request_value, *, catalog: result)

    class BinaryInput:
        def __init__(self, raw: bytes):
            self.buffer = io.BytesIO(raw)

    monkeypatch.setattr(cli.sys, "stdin", BinaryInput(json.dumps(request()).encode("utf-8")))
    assert cli.main(["compare"]) == 0
    output = capsys.readouterr().out
    assert len(output.encode("utf-8")) > 1024 * 1024
    decoded = json.loads(output)
    assert len(decoded["comparison"]["metrics"]) == 600
    rows = decoded["comparison"]["metrics"]
    assert [row["left"]["number"]["fiscal_year"] for row in rows] == list(range(1000, 1600))
    assert all(row["left"]["provenance"]["locator"].endswith("x" * 1100) and
               row["right"]["provenance"]["locator"].endswith("x" * 1100) for row in rows)


def test_success_result_matches_dashboard_0_1_1_b_contract_read_only():
    root_text = os.environ.get("DASHBOARD_CONTRACT_ROOT")
    if not root_text:
        pytest.skip("set DASHBOARD_CONTRACT_ROOT to the read-only Dashboard contracts directory")
    schema_root = Path(root_text)
    manifest = schema_root / "fixtures" / "manifest.json"
    schema_file = schema_root / "schemas" / "dashboard.schema.json"
    if not manifest.exists() or not schema_file.exists():
        pytest.skip("Dashboard contract checkout is unavailable on this host")
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    if manifest_data.get("contract_version") != "0.1.1-b":
        pytest.skip("Dashboard contract version is not the frozen 0.1.1-b")
    jsonschema = pytest.importorskip("jsonschema")
    document = json.loads(schema_file.read_text(encoding="utf-8"))
    components = document["components"]
    left = side("R-OLD", info="2026-10-20")
    right = side("R-NEW", info="2026-10-21")
    comparison = compare_reports(request(), catalog=FakeCatalog(left, right))["comparison"]

    def validate(instance: Any, name: str) -> None:
        root = {"$schema": document["$schema"], "$id": document["$id"],
                "components": components,
                "$ref": f"#/components/schemas/{name}"}
        jsonschema.Draft202012Validator(root).validate(instance)

    validate(request(), "CompareRequest")
    validate(comparison, "ReportComparison")
    broken = copy.deepcopy(comparison)
    broken["metrics"][0]["comparable"] = False
    with pytest.raises(jsonschema.ValidationError):
        validate(broken, "ReportComparison")


# -- real ReportCatalog exact-read integration; fixtures are synthetic ----------


def _registered_catalog(tmp_path: Path):
    from test_report_catalog import _fixture

    catalog, _, result, run, attempt, report = _fixture(tmp_path)
    run["company"]["listing_id"] = "LST-test"
    second = {**report, "report_id": "rf-two", "created_at": "2026-10-24T12:03:00Z"}
    attempt["report_ids"] = ["rf-one", "rf-two"]
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report, second])
    return catalog, result, run, attempt, report, second


def _real_request() -> dict[str, Any]:
    return {"left_report_id": "rf-one", "right_report_id": "rf-two",
            "scenario": "base", "metric_ids": ["revenue"]}


def test_real_catalog_exact_pair_uses_owner_readers_and_zero_delta(tmp_path):
    catalog, _, _, _, _, _ = _registered_catalog(tmp_path)
    result = compare_reports(_real_request(), catalog=catalog)
    rows = result["comparison"]["metrics"]
    assert rows and all(row["comparable"] for row in rows)
    assert all(Decimal(row["delta"]["value"]) == 0 for row in rows)
    assert all("e" not in row["delta"]["value"].lower() for row in rows)
    assert {row["left"]["provenance"]["artifact_id"] for row in rows} == {"rf-one"}
    assert {row["right"]["provenance"]["artifact_id"] for row in rows} == {"rf-two"}
    assert all(row["left"]["number"]["currency"] == "USD" for row in rows)
    assert result["comparison"]["left_information_as_of"] == result["comparison"]["right_information_as_of"]


def test_real_catalog_legal_append_does_not_invalidate_exact_reports(tmp_path):
    catalog, _, run, attempt, report, _ = _registered_catalog(tmp_path)
    before = compare_reports(_real_request(), catalog=catalog)
    run2 = {**run, "run_id": "run-2", "created_at": "2026-10-24T13:00:00Z"}
    attempt2 = {**attempt, "run_id": "run-2", "report_ids": ["rf-three"]}
    third = {**report, "run_id": "run-2", "attempt_id": "attempt-ok",
             "report_id": "rf-three", "created_at": "2026-10-24T13:01:00Z"}
    catalog.add_records(runs=[run2], attempts=[attempt2], reports=[third])
    after = compare_reports(_real_request(), catalog=catalog)
    assert after["catalog_revisions"] != before["catalog_revisions"]
    assert after["comparison"]["metrics"] == before["comparison"]["metrics"]
    assert all(row["comparable"] for row in after["comparison"]["metrics"])


def test_real_catalog_tampered_frozen_bytes_fail_closed_pathless(tmp_path):
    catalog, _, _, _, _, _ = _registered_catalog(tmp_path)
    (tmp_path / "report.json").write_text("{}", encoding="utf-8")
    with pytest.raises(CompareError) as error:
        compare_reports(_real_request(), catalog=catalog)
    assert error.value.code == "incompatible"
    assert "report.json" not in str(error.value)


def test_real_catalog_missing_report_is_not_found(tmp_path):
    catalog, _, _, _, _, _ = _registered_catalog(tmp_path)
    request_value = {"left_report_id": "rf-one", "right_report_id": "rf-absent",
                     "scenario": "base", "metric_ids": ["revenue"]}
    with pytest.raises(CompareError) as error:
        compare_reports(request_value, catalog=catalog)
    assert error.value.code == "not_found"
