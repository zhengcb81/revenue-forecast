"""Focused tests for the owner ReportCatalog; all artifacts live in tmp_path."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from report_catalog import CatalogError, ReportCatalog, import_w09  # noqa: E402
from publication_registry import canonical_sha256  # noqa: E402
from revenue_core import run_forecast  # noqa: E402
from test_recognition_bridge import forecast_document, add_parameter  # noqa: E402
from test_data_contract import apply_parameter_contract, finalize_contract  # noqa: E402


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, allow_nan=False),
                    encoding="utf-8")


def _fixture(tmp_path: Path, data: dict | None = None):
    catalog = ReportCatalog(root=tmp_path, catalog_file=tmp_path / "catalog.jsonl")
    data = forecast_document() if data is None else data
    data["forecast_version"] = "catalog-test-v1"
    result = run_forecast(data)
    _write(tmp_path / "input.json", data)
    _write(tmp_path / "report.json", result)
    company = {"entity_id": "ENT-test", "listing_id": None,
               "analysis_subject_id": "subject-test", "resolution_status": "resolved",
               "display_name": result["company_name"]}
    run = {"run_id": "run-1", "parent_run_id": None, "company": company,
           "source_as_of": result["as_of_date"], "created_at": "2026-10-24T12:00:00Z",
           "status": "partial", "scenario_set": ["low", "base", "high"],
           "reporting_currency": result["currency"], "model_metadata": {},
           "artifact_revision": "synthetic-v1", "source_snapshot_refs": []}
    _write(tmp_path / "receipt-success.json",
           {"attempt_id": "attempt-ok", "status": "succeeded"})
    attempt = {"run_id": "run-1", "attempt_id": "attempt-ok", "status": "succeeded",
               "started_at": "2026-10-24T12:00:00Z", "ended_at": "2026-10-24T12:01:00Z",
               "report_ids": ["rf-one"], "error_code": None,
               "source_evidence": {"kind": "attempt_receipt_json",
                                   "artifact": catalog.artifact_ref(tmp_path / "receipt-success.json")}}
    report = {"report_id": "rf-one", "run_id": "run-1", "attempt_id": "attempt-ok",
              "company": company, "artifact_kind": "revenue_forecast",
              "artifact_revision": "catalog-test-v1", "input_sha256": result["input_sha256"],
              "result_sha256": result["result_sha256"], "created_at": "2026-10-24T12:01:00Z",
              "status": "validated", "schema_version": result["schema_version"],
              "engine_version": result["engine_version"], "information_as_of": result["as_of_date"],
              "forecast_horizon": "2026-2027", "supersedes_report_id": None,
              "missing_reason": None, "reporting_currency": result["currency"],
              "reporting_scale": 6, "forecast_artifact": catalog.artifact_ref(tmp_path / "report.json"),
              "input_artifact": catalog.artifact_ref(tmp_path / "input.json")}
    return catalog, data, result, run, attempt, report


def test_run_attempt_report_separate_and_failed_attempt_without_report(tmp_path):
    catalog, _, _, run, attempt, report = _fixture(tmp_path)
    _write(tmp_path / "receipt-failed.json",
           {"attempt_id": "attempt-failed", "status": "failed"})
    failed = {"run_id": "run-1", "attempt_id": "attempt-failed", "status": "failed",
              "started_at": "2026-10-25T12:00:00Z", "ended_at": "2026-10-25T12:01:00Z",
              "report_ids": [], "error_code": "synthetic_failure",
              "source_evidence": {"kind": "attempt_receipt_json",
                                  "artifact": catalog.artifact_ref(tmp_path / "receipt-failed.json")}}
    catalog.add_records(runs=[run], attempts=[attempt, failed], reports=[report])
    page = catalog.list_runs("ENT-test", analysis_subject_id="subject-test")
    assert len(page["items"]) == 1
    assert {a["attempt_id"] for a in page["items"][0]["attempts"]} == {"attempt-ok", "attempt-failed"}
    assert catalog.get_attempt("run-1", "attempt-failed")["attempt"]["report_ids"] == []
    assert [item["report_id"] for item in catalog.list_reports("ENT-test")["items"]] == ["rf-one"]
    with pytest.raises(CatalogError, match="attempt ID already registered"):
        catalog.add_records(attempts=[failed])


def test_same_run_multiple_reports_and_history_cannot_be_replaced(tmp_path):
    catalog, data, _, run, attempt, report = _fixture(tmp_path)
    data2 = copy.deepcopy(data)
    data2["forecast_version"] = "catalog-test-v2"
    result2 = run_forecast(data2)
    _write(tmp_path / "input2.json", data2)
    _write(tmp_path / "report2.json", result2)
    attempt["report_ids"] = ["rf-one", "rf-two"]
    report2 = {**report, "report_id": "rf-two", "artifact_revision": "catalog-test-v2",
               "input_sha256": result2["input_sha256"], "result_sha256": result2["result_sha256"],
               "created_at": "2026-10-24T12:02:00Z", "forecast_artifact":
               catalog.artifact_ref(tmp_path / "report2.json"), "input_artifact":
               catalog.artifact_ref(tmp_path / "input2.json")}
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report, report2])
    rows = catalog.list_reports("ENT-test")["items"]
    assert [row["report_id"] for row in rows] == ["rf-two", "rf-one"]
    assert catalog.list_reports("ENT-test")["resolved_latest_success_report_id"] == "rf-two"
    assert catalog.get_run("run-1")["run"]["attempts"][0]["report_ids"] == ["rf-one", "rf-two"]
    with pytest.raises(CatalogError, match="report ID already registered"):
        catalog.add_records(reports=[report])


def test_exact_read_model_calculation_sha_and_pathless_output(tmp_path):
    catalog, _, _, run, attempt, report = _fixture(tmp_path)
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    view = catalog.get_report("rf-one")
    assert view["view"]["report"]["report_id"] == "rf-one"
    assert view["view"]["calculation_node_ids"]
    assert catalog.get_model("rf-one")["state"] == "available"
    node = view["view"]["calculation_node_ids"][0]
    calculation = catalog.get_calculation("rf-one", node)["calculation"]
    assert calculation["report_id"] == "rf-one"
    assert calculation["output"]["provenance"]["artifact_id"] == "rf-one"
    direct = catalog.get_calculation("rf-one", "segment:0:base:2026")["calculation"]
    revenue_input = next(row for row in direct["inputs"] if row["name"] == "revenue")
    assert revenue_input["number"]["unit"] == "currency"
    assert revenue_input["number"]["currency"] == report["reporting_currency"]
    public = json.dumps([view, catalog.get_model("rf-one"), calculation], ensure_ascii=False)
    assert str(tmp_path) not in public
    assert "relative_path" not in public and "original_path" not in public
    (tmp_path / "report.json").write_text("{}", encoding="utf-8")
    with pytest.raises(CatalogError) as error:
        catalog.get_report("rf-one")
    assert error.value.code == "artifact_sha_mismatch"


def test_old_schema_and_missing_model_metadata_have_named_reasons(tmp_path):
    catalog, _, result, run, attempt, report = _fixture(tmp_path)
    legacy = copy.deepcopy(result)
    legacy["schema_version"] = "3.0"
    legacy["engine_version"] = None
    _write(tmp_path / "old.json", legacy)
    report.update({"status": "legacy", "schema_version": "3.0", "engine_version": None,
                   "missing_reason": "legacy_emitting_engine_unknown",
                   "forecast_artifact": catalog.artifact_ref(tmp_path / "old.json"),
                   "input_artifact": None})
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    view = catalog.get_report("rf-one")["view"]
    assert "legacy_emitting_engine_unknown" in view["quality_gaps"]
    assert view["calculation_node_ids"] == []
    assert catalog.get_model("rf-one")["missing_reason"] == "legacy_emitting_engine_unknown"
    node = catalog.get_calculation("rf-one", "consolidated:base:2027")["calculation"]
    assert node["trace_state"] == "unavailable"
    assert node["missing_reason"] == "legacy_emitting_engine_unknown"


def test_missing_field_and_incompatible_emitter_refused(tmp_path):
    catalog, _, result, run, attempt, report = _fixture(tmp_path)
    missing = copy.deepcopy(result)
    missing.pop("schema_version")
    _write(tmp_path / "missing.json", missing)
    report["forecast_artifact"] = catalog.artifact_ref(tmp_path / "missing.json")
    with pytest.raises(CatalogError) as error:
        catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    assert error.value.code == "artifact_schema_mismatch"
    incompatible = copy.deepcopy(result)
    incompatible["engine_version"] = "9.9.9"
    _write(tmp_path / "wrong-engine.json", incompatible)
    report["engine_version"] = "9.9.9"
    report["forecast_artifact"] = catalog.artifact_ref(tmp_path / "wrong-engine.json")
    with pytest.raises(CatalogError) as error:
        catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    assert error.value.code == "schema_incompatible"


def test_cursor_binds_catalog_revision(tmp_path):
    catalog, _, _, run, attempt, report = _fixture(tmp_path)
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    second = {**run, "run_id": "run-2", "created_at": "2026-10-26T12:00:00Z"}
    catalog.add_records(runs=[second])
    page = catalog.list_runs("ENT-test", limit=1)
    assert page["page"]["next_cursor"]
    third = {**run, "run_id": "run-3", "created_at": "2026-10-27T12:00:00Z"}
    catalog.add_records(runs=[third])
    with pytest.raises(CatalogError) as error:
        catalog.list_runs("ENT-test", cursor=page["page"]["next_cursor"], limit=1)
    assert error.value.code == "stale_cursor"


def test_attempt_links_must_be_complete_before_append(tmp_path):
    catalog, _, _, run, attempt, report = _fixture(tmp_path)
    attempt["report_ids"] = []
    with pytest.raises(CatalogError) as error:
        catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    assert error.value.code == "attempt_report_mismatch"
    assert not catalog.file.exists()
    attempt["report_ids"] = ["rf-one", "rf-missing"]
    with pytest.raises(CatalogError) as error:
        catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    assert error.value.code == "attempt_report_mismatch"
    assert not catalog.file.exists()


def test_reject_unmanaged_catalog_env_path(tmp_path, monkeypatch):
    monkeypatch.setenv("REVENUE_REPORT_CATALOG", str(tmp_path / "delivery" / "catalog.jsonl"))
    with pytest.raises(CatalogError) as error:
        ReportCatalog(root=tmp_path)
    assert error.value.code == "catalog_path_forbidden"
    allowed = tmp_path / "artifacts" / "report_catalog" / "test.jsonl"
    monkeypatch.setenv("REVENUE_REPORT_CATALOG", str(allowed))
    assert ReportCatalog(root=tmp_path).file == allowed.resolve()


def test_large_artifact_is_refused_before_reading(tmp_path, monkeypatch):
    huge = tmp_path / "large.json"
    with huge.open("wb") as handle:
        handle.seek(64 * 1024 * 1024)
        handle.write(b"x")
    original = Path.open

    def guarded(self, *args, **kwargs):
        if self == huge:
            raise AssertionError("oversized artifact was opened before size check")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    catalog = ReportCatalog(root=tmp_path, catalog_file=tmp_path / "catalog.jsonl")
    with pytest.raises(CatalogError) as error:
        catalog.artifact_ref(huge)
    assert error.value.code == "artifact_too_large"


def test_real_w09_import_requires_trusted_stockwiki_resolver(tmp_path):
    catalog = ReportCatalog(root=Path(__file__).resolve().parents[1],
                            catalog_file=tmp_path / "w09-not-written.jsonl")
    with pytest.raises(CatalogError) as error:
        import_w09(catalog, entity_id="ENT-unverified", analysis_subject_id=None,
                   identity_evidence={"authority": "stockwiki", "entity_id": "ENT-unverified",
                                      "resolution_status": "resolved", "source_revision": "fake",
                                      "lookup_receipt_sha256": "0" * 64})
    assert error.value.code == "identity_resolver_unavailable"
    assert not catalog.file.exists()


def test_growth_calculation_includes_actual_base_and_prior_modeled_revenue(tmp_path):
    data = forecast_document()
    segment = data["segments"][0]
    parameter_index = {row["parameter_id"]: row for row in data["parameters"]}
    for scenario, detail in segment["scenarios"].items():
        ids = detail["driver_parameter_ids"]["revenue"]
        for parameter_id in ids:
            parameter = parameter_index[parameter_id]
            parameter.update(value=0.1, unit="ratio")
            apply_parameter_contract(data, parameter, "ratio")
        detail.update(model="direct_growth", driver_parameter_ids={"growth_rate": ids})
    finalize_contract(data)
    catalog, _, result, run, attempt, report = _fixture(tmp_path, data)
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    first = catalog.get_calculation("rf-one", "segment:0:base:2026")["calculation"]
    later = catalog.get_calculation("rf-one", "segment:0:base:2027")["calculation"]
    initial = next(row["number"] for row in first["inputs"] if row["name"] == "previous_revenue")
    prior = next(row["number"] for row in later["inputs"] if row["name"] == "previous_revenue")
    assert initial["value"] == str(float(result["segments"][0]["base_revenue"]))
    assert initial["fiscal_year"] == result["base_year"]
    assert initial["actual_or_forecast"] == "actual"
    assert initial["unit"] == "currency"
    assert prior["value"] == first["output"]["number"]["value"]
    assert prior["fiscal_year"] == 2026
    assert prior["actual_or_forecast"] == "forecast"
    growth = next(row["number"] for row in first["inputs"] if row["name"] == "growth_rate")
    assert growth["unit"] == "ratio" and growth["currency"] is None and growth["scale"] == 0


def test_unit_sales_drivers_keep_quantity_and_monetary_denominator(tmp_path):
    data = forecast_document()
    segment = data["segments"][0]
    parameter_index = {row["parameter_id"]: row for row in data["parameters"]}
    for scenario, detail in segment["scenarios"].items():
        price_ids = detail["driver_parameter_ids"]["revenue"]
        quantity_ids = []
        for year, parameter_id in zip(data["forecast_years"], price_ids):
            parameter = parameter_index[parameter_id]
            parameter.update(value=5, unit="USD million / item")
            apply_parameter_contract(data, parameter, "revenue_per_unit")
            quantity_ids.append(add_parameter(data, f"units_{scenario}_{year}", 10,
                                              year, scenario, dimension="quantity"))
        detail.update(model="unit_sales",
                      driver_parameter_ids={"units": quantity_ids, "unit_revenue": price_ids})
    finalize_contract(data)
    catalog, _, _, run, attempt, report = _fixture(tmp_path, data)
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    node = catalog.get_calculation("rf-one", "segment:0:base:2026")["calculation"]
    numbers = {row["name"]: row["number"] for row in node["inputs"]}
    assert numbers["units"]["unit"] == "quantity"
    assert numbers["units"]["currency"] is None and numbers["units"]["scale"] is None
    assert numbers["unit_revenue"]["unit"] == "revenue_per_unit"
    assert numbers["unit_revenue"]["currency"] == "USD"
    assert numbers["unit_revenue"]["scale"] == 6
    assert numbers["timing_factor"]["unit"] == "ratio"
    assert "driver_physical_unit_not_projected" in node["missing_reason"]


def test_model_formula_does_not_claim_unprojected_recognition_output(tmp_path):
    data = forecast_document()
    segment = data["segments"][0]
    progress = {}
    for scenario in ("low", "base", "high"):
        progress[scenario] = [
            add_parameter(data, f"progress_{scenario}_{year}", 0.5, year, scenario,
                          dimension="ratio") for year in data["forecast_years"]]
    segment["recognition"].update(timing="over_time", progress_measure="verified output",
                                  progress_parameter_ids=progress)
    finalize_contract(data)
    catalog, _, _, run, attempt, report = _fixture(tmp_path, data)
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    node = catalog.get_calculation("rf-one", "segment:0:base:2026")["calculation"]
    assert node["trace_state"] == "unavailable" and node["output"] is None
    assert node["missing_reason"] == "recognition_or_constraint_transform_not_projected"


def test_caller_receipt_must_match_owner_resolver_response(tmp_path):
    catalog = ReportCatalog(root=tmp_path, catalog_file=tmp_path / "not-written.jsonl")
    forged = {"authority": "stockwiki", "entity_id": "ENT-fabricated",
              "resolution_status": "resolved", "source_revision": "fake",
              "lookup_receipt_sha256": "0" * 64}
    calls = []
    def resolver(entity_id):
        calls.append(entity_id)
        return {**forged, "entity_id": "ENT-real"}
    with pytest.raises(CatalogError) as error:
        import_w09(catalog, entity_id="ENT-fabricated", analysis_subject_id=None,
                   identity_evidence=forged, identity_resolver=resolver)
    assert error.value.code == "identity_unverified"
    assert calls == ["ENT-fabricated"] and not catalog.file.exists()


def test_cli_rejects_unmanaged_env_path_with_pathless_error(tmp_path, monkeypatch, capsys):
    from report_catalog_cli import main

    forbidden = tmp_path / "private" / "catalog.jsonl"
    monkeypatch.setenv("REVENUE_REPORT_CATALOG", str(forbidden))
    assert main(["list-runs", "--entity-id", "ENT-test"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    response = json.loads(captured.err)
    assert response["error"]["code"] == "catalog_path_forbidden"
    assert str(forbidden) not in captured.err

@pytest.mark.parametrize(
    ("changes", "expected_code"),
    [
        ({"reporting_currency": "CNY"}, "artifact_currency_mismatch"),
        ({"reporting_scale": 8}, "artifact_scale_mismatch"),
        ({"reporting_currency": "CNY", "reporting_scale": 8}, "artifact_currency_mismatch"),
        ({"reporting_scale": True}, "artifact_scale_mismatch"),
    ],
)
def test_registration_refuses_relabelled_frozen_money(tmp_path, changes, expected_code):
    catalog, _, result, run, attempt, report = _fixture(tmp_path)
    assert result["currency"] == "USD" and result["unit"] == "million"
    report.update(changes)
    with pytest.raises(CatalogError) as error:
        catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    assert error.value.code == expected_code
    assert not catalog.file.exists()
    assert not catalog.file.with_name(catalog.file.name + ".lock").exists()


@pytest.mark.parametrize(
    ("unit", "scale"),
    [("unit", 0), ("thousand", 3), ("million", 6), ("billion", 9), ("100m", 8)],
)
def test_supported_frozen_money_units_bind_exact_scale(tmp_path, unit, scale):
    data = forecast_document()
    data["unit"] = unit
    for parameter in data["parameters"]:
        if parameter.get("currency"):
            parameter["scale"] = unit
    finalize_contract(data)
    catalog, _, _, run, attempt, report = _fixture(tmp_path, data)
    report["reporting_scale"] = scale
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    number = catalog.get_report("rf-one")["view"]["metrics"][0]["number"]
    assert number["currency"] == "USD" and number["scale"] == scale
    assert number["value"] == "165.00000000000003"


def test_unknown_frozen_money_unit_fails_closed_before_registration(tmp_path):
    catalog, _, result, run, attempt, report = _fixture(tmp_path)
    result["unit"] = "unmapped_money_unit"
    result["result_sha256"] = canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"})
    _write(tmp_path / "report.json", result)
    report["result_sha256"] = result["result_sha256"]
    report["forecast_artifact"] = catalog.artifact_ref(tmp_path / "report.json")
    with pytest.raises(CatalogError) as error:
        catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    assert error.value.code == "artifact_unit_incompatible"
    assert not catalog.file.exists()


@pytest.mark.parametrize(
    ("changes", "expected_code"),
    [
        ({"reporting_currency": "CNY"}, "artifact_currency_mismatch"),
        ({"reporting_scale": 8}, "artifact_scale_mismatch"),
        ({"reporting_currency": "CNY", "reporting_scale": 8}, "artifact_currency_mismatch"),
    ],
)
def test_preexisting_catalog_wrong_money_metadata_is_refused_on_exact_reads(
        tmp_path, changes, expected_code):
    catalog, _, _, run, attempt, report = _fixture(tmp_path)
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    # Simulate an old, internally hashed index created by the defective version.
    # This does not tamper with or regenerate the frozen forecast artifact.
    entry = json.loads(catalog.file.read_text(encoding="utf-8"))
    entry["reports"][0].update(changes)
    entry["line_sha256"] = canonical_sha256(
        {key: value for key, value in entry.items() if key != "line_sha256"})
    _write(catalog.file, entry)
    old_bytes = catalog.file.read_bytes()
    for reader in (
        lambda: catalog.get_report("rf-one"),
        lambda: catalog.get_model("rf-one"),
        lambda: catalog.get_calculation("rf-one", "segment:0:base:2026"),
    ):
        with pytest.raises(CatalogError) as error:
            reader()
        assert error.value.code == expected_code
        assert catalog.file.read_bytes() == old_bytes



def test_public_report_catalog_cli_uses_only_the_selected_owner(tmp_path):
    owner = tmp_path / "active"
    _, _, _, run, attempt, report = _fixture(owner)
    catalog = ReportCatalog(root=owner)
    catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    empty = tmp_path / "empty"
    ReportCatalog(root=empty).file.parent.mkdir(parents=True)
    cli = Path(__file__).resolve().parents[1] / "scripts/report_catalog_cli.py"

    def call(root, *args):
        return subprocess.run([sys.executable, "-B", str(cli), "--owner-root", str(root), *args],
                              capture_output=True, encoding="utf-8", timeout=30, check=False)

    listed = call(owner, "list-reports", "--entity-id", run["company"]["entity_id"])
    assert listed.returncode == 0, listed.stderr
    row, = json.loads(listed.stdout)["items"]
    assert row["result_sha256"] == report["result_sha256"]
    report_id = row["report_id"]
    exact = call(owner, "get-report", "--report-id", report_id)
    assert exact.returncode == 0, exact.stderr
    assert json.loads(exact.stdout)["view"]["report"]["result_sha256"] == row["result_sha256"]
    assert str(owner) not in exact.stdout and str(owner) not in listed.stdout
    assert json.loads(call(empty, "list-reports", "--entity-id", run["company"]["entity_id"]).stdout)["items"] == []
    refused = call(empty, "get-report", "--report-id", report_id)
    assert refused.returncode == 2 and refused.stdout == ""
    assert str(empty) not in refused.stderr



def test_default_catalog_refuses_links_to_another_owner(tmp_path):
    other = tmp_path / "other"
    _, _, _, run, attempt, report = _fixture(other)
    other_catalog = ReportCatalog(root=other)
    other_catalog.add_records(runs=[run], attempts=[attempt], reports=[report])
    owner = tmp_path / "owner"
    (owner / "artifacts").mkdir(parents=True)
    try:
        (owner / "artifacts/report_catalog").symlink_to(other_catalog.file.parent, target_is_directory=True)
    except OSError:
        pytest.skip("directory links are unavailable")
    with pytest.raises(CatalogError) as refused:
        ReportCatalog(root=owner)
    assert refused.value.code == "catalog_path_forbidden"
