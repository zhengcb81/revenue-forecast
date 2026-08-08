from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from revenue_backtest import (
    create_snapshot,
    evaluate_snapshot,
    validate_snapshot,
    write_new_json,
)  # noqa: E402
from revenue_core import (
    ENGINE_VERSION,
    ForecastInputError,
    build_host_receipt,
    canonical_sha256,
    run_forecast,
    text_sha256,
)  # noqa: E402
from revenue_report import validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def actuals_document() -> dict:
    data = {
        "actuals_schema_version": "2.0",
        "company_name": "Test Co",
        "actuals_as_of_date": "2028-03-01",
        "currency": "USD",
        "unit": "million",
        "sources": [
            {
                "source_id": "actual_filing",
                "source_type": "exchange_filing",
                "title": "FY2027 filing",
                "publisher": "Test Exchange",
                "url": "https://www.sec.gov/Archives/edgar/data/1/actual.htm",
                "published_date": "2028-02-20",
                "accessed_date": "2028-03-01",
                "page_or_section": "Revenue note",
            }
        ],
        "actual_company_revenue": {
            "2026": {
                "value": 160,
                "source_ids": ["actual_filing"],
                "claim_ids": ["claim_actual_company_2026"],
            },
            "2027": {
                "value": 170,
                "source_ids": ["actual_filing"],
                "claim_ids": ["claim_actual_company_2027"],
            },
        },
        "actual_segment_revenue": {
            "Segment A": {
                "2026": {
                    "value": 106,
                    "source_ids": ["actual_filing"],
                    "claim_ids": ["claim_actual_segment_2026"],
                },
                "2027": {
                    "value": 112,
                    "source_ids": ["actual_filing"],
                    "claim_ids": ["claim_actual_segment_2027"],
                },
            }
        },
    }
    for source in data["sources"]:
        capture = {
            "capture_schema_version": "1.0",
            "capture_method": "browser_open",
            "tool_name": "test-browser",
            "tool_call_id": f"fixture-{source['source_id']}",
            "captured_date": source["accessed_date"],
            "snapshot_sha256": "b" * 64,
            "content_treatment": "untrusted_data_only",
            "prompt_injection_status": "not_detected",
        }
        capture["host_receipt"] = build_host_receipt(
            issuer="fixture-host",
            environment="test",
            tool_name=capture["tool_name"],
            action="capture_open",
            event_sha256=text_sha256(f"fixture-open-{source['source_id']}"),
            timestamp=capture["captured_date"],
        )
        capture["receipt_sha256"] = canonical_sha256(capture)
        source["capture"] = capture
    claims = []
    for claim_id, target_id, value, year in (
        ("claim_actual_company_2026", "company:2026", 160, 2026),
        ("claim_actual_company_2027", "company:2027", 170, 2027),
        ("claim_actual_segment_2026", "segment:Segment A:2026", 106, 2026),
        ("claim_actual_segment_2027", "segment:Segment A:2027", 112, 2027),
    ):
        excerpt = f"Reported actual revenue for {target_id} is {value} USD million."
        claims.append(
            {
                "claim_id": claim_id,
                "source_id": "actual_filing",
                "target_type": "actual_revenue",
                "target_id": target_id,
                "support_type": "exact_value",
                "locator": "Revenue note",
                "excerpt": excerpt,
                "excerpt_sha256": text_sha256(excerpt),
                "content_sha256": "b" * 64,
                "capture_receipt_sha256": data["sources"][0]["capture"][
                    "receipt_sha256"
                ],
                "verification_status": "opened_and_checked",
                "verified_by": "test-research-agent",
                "verified_date": "2028-03-01",
                "extracted_value": value,
                "unit": "USD million",
                "period": f"FY{year}",
            }
        )
    data["evidence_claims"] = claims
    return data


def set_company_actual(data: dict, year: int, value: float) -> None:
    record = data["actual_company_revenue"][str(year)]
    record["value"] = value
    claim = next(
        item
        for item in data["evidence_claims"]
        if item["claim_id"] == record["claim_ids"][0]
    )
    excerpt = f"Reported actual revenue for company:{year} is {value} USD million."
    claim.update(
        {
            "extracted_value": value,
            "excerpt": excerpt,
            "excerpt_sha256": text_sha256(excerpt),
        }
    )


class BacktestTests(unittest.TestCase):
    def test_snapshot_is_deterministic_and_tamper_evident(self) -> None:
        data = forecast_document()
        left = create_snapshot(data, "v1")
        right = create_snapshot(data, "v1")
        self.assertEqual(left["snapshot_id"], right["snapshot_id"])
        tampered = copy.deepcopy(left)
        tampered["input_document"]["company_name"] = "Tampered"
        with self.assertRaisesRegex(ForecastInputError, "input binding mismatch"):
            evaluate_snapshot(tampered, actuals_document())

    def test_snapshot_file_cannot_be_overwritten(self) -> None:
        snapshot = create_snapshot(forecast_document(), "v1")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            write_new_json(path, snapshot)
            with self.assertRaises(FileExistsError):
                write_new_json(path, snapshot)

    def test_snapshot_creation_runs_independent_output_validation(self) -> None:
        snapshot = create_snapshot(forecast_document(), "v1")
        validate_forecast_output(snapshot["forecast_result"])
        self.assertEqual(
            snapshot["forecast_result_sha256"],
            canonical_sha256(snapshot["forecast_result"]),
        )

    def test_backtest_metrics_are_recomputed(self) -> None:
        snapshot = create_snapshot(forecast_document(), "v1")
        report = evaluate_snapshot(snapshot, actuals_document())
        expected_wape = (abs(165 - 160) + abs(181.5 - 170)) / (160 + 170)
        self.assertAlmostEqual(report["summary"]["wape"], expected_wape)
        self.assertEqual(report["summary"]["direction_accuracy"], 1.0)
        self.assertEqual(report["summary"]["interval_coverage"], 1.0)
        self.assertIn("Segment A", report["segment_year_results"])

    def test_direction_accuracy_is_not_hardcoded(self) -> None:
        snapshot = create_snapshot(forecast_document(), "v1")
        actuals = actuals_document()
        set_company_actual(actuals, 2026, 140)
        set_company_actual(actuals, 2027, 130)
        report = evaluate_snapshot(snapshot, actuals)
        self.assertEqual(report["summary"]["direction_accuracy"], 0.0)

    def test_actual_source_cannot_be_future_dated(self) -> None:
        snapshot = create_snapshot(forecast_document(), "v1")
        actuals = actuals_document()
        actuals["sources"][0]["published_date"] = "2028-03-02"
        with self.assertRaisesRegex(ForecastInputError, "future information leak"):
            evaluate_snapshot(snapshot, actuals)

    def test_actual_year_must_be_in_horizon(self) -> None:
        snapshot = create_snapshot(forecast_document(), "v1")
        actuals = actuals_document()
        actuals["actual_company_revenue"]["2029"] = {
            "value": 180,
            "source_ids": ["actual_filing"],
        }
        with self.assertRaisesRegex(ForecastInputError, "outside forecast horizon"):
            evaluate_snapshot(snapshot, actuals)

    def test_snapshot_forecast_result_tampering_is_rejected(self) -> None:
        snapshot = create_snapshot(forecast_document(), "v1")
        snapshot["forecast_result"]["consolidated_forecast"]["base"]["annual_revenue"][
            "2026"
        ] = 9999
        with self.assertRaisesRegex(ForecastInputError, "mismatch"):
            evaluate_snapshot(snapshot, actuals_document())

    def test_zero_actual_revenue_keeps_absolute_error_metrics(self) -> None:
        snapshot = create_snapshot(forecast_document(), "v1")
        actuals = actuals_document()
        set_company_actual(actuals, 2026, 0)
        set_company_actual(actuals, 2027, 0)
        report = evaluate_snapshot(snapshot, actuals)
        self.assertIsNone(report["summary"]["wape"])
        self.assertGreater(report["summary"]["mae"], 0)
        self.assertGreater(report["summary"]["mean_smape"], 0)
        self.assertGreater(report["company_year_results"]["2026"]["absolute_error"], 0)

    def test_accuracy_record_is_hash_linked(self) -> None:
        report = evaluate_snapshot(
            create_snapshot(forecast_document(), "v1"), actuals_document()
        )
        self.assertEqual(
            report["accuracy_record"]["backtest_id"], report["backtest_id"]
        )
        self.assertIn("record_sha256", report["accuracy_record"])
        self.assertIn("Segment A", report["segment_summaries"])
        self.assertIn("1", report["horizon_summaries"])

    def test_accuracy_record_flows_automatically_into_confidence(self) -> None:
        evaluation = evaluate_snapshot(
            create_snapshot(forecast_document(), "v1"), actuals_document()
        )
        data = forecast_document()
        data["historical_accuracy_records"] = [evaluation["accuracy_record"]]
        result = run_forecast(data)
        self.assertAlmostEqual(
            result["confidence"]["historical_accuracy"]["wape"],
            evaluation["summary"]["wape"],
        )
        self.assertGreater(result["confidence"]["components"]["historical_accuracy"], 0)

    def test_tampered_accuracy_record_is_rejected(self) -> None:
        evaluation = evaluate_snapshot(
            create_snapshot(forecast_document(), "v1"), actuals_document()
        )
        data = forecast_document()
        record = copy.deepcopy(evaluation["accuracy_record"])
        record["wape"] = 0
        data["historical_accuracy_records"] = [record]
        with self.assertRaisesRegex(ForecastInputError, "record hash mismatch"):
            run_forecast(data)

    def test_nonconsecutive_actual_years_are_flagged(self) -> None:
        actuals = actuals_document()
        del actuals["actual_company_revenue"]["2026"]
        report = evaluate_snapshot(create_snapshot(forecast_document(), "v1"), actuals)
        self.assertTrue(report["nonconsecutive_actual_years"])
        self.assertIsNone(report["company_year_results"]["2027"]["direction_correct"])

    def test_actual_source_must_postdate_fiscal_year_end(self) -> None:
        actuals = actuals_document()
        actuals["sources"][0]["published_date"] = "2027-11-01"
        with self.assertRaisesRegex(ForecastInputError, "predates fiscal year end"):
            evaluate_snapshot(create_snapshot(forecast_document(), "v1"), actuals)

    def test_forged_sensitivity_snapshot_is_rejected_after_full_rehash(self) -> None:
        # Phase 6 A1 RED (F-02 snapshot vector): forge sensitivity terminals,
        # recompute every hash including the publication receipt's verification
        # context and the snapshot id, and confirm validate_snapshot rejects the
        # forgery through the strong (input-required) path.
        from revenue_publication import (
            VerificationContext,
            build_publication_receipt,
            expected_publication_gates,
        )
        from revenue_report import validate_published_forecast

        data = forecast_document()
        parameter_id = data["segments"][0]["scenarios"]["base"]["driver_parameter_ids"][
            "revenue"
        ][1]
        data["sensitivity_tests"] = [
            {
                "name": "Core terminal revenue",
                "parameter_id": parameter_id,
                "shock_type": "percent",
                "shock_value": 0.1,
            }
        ]
        snapshot = create_snapshot(data, "v1")
        forged = copy.deepcopy(snapshot)
        result = forged["forecast_result"]
        sensitivity = result["sensitivities"][0]
        baseline = float(sensitivity["baseline_terminal_revenue"])
        sensitivity["down_terminal_revenue"] = 1.0
        sensitivity["up_terminal_revenue"] = baseline * 100.0
        impact = max(abs(1.0 - baseline), abs(baseline * 100.0 - baseline))
        sensitivity["max_absolute_terminal_impact"] = impact
        sensitivity["max_relative_terminal_impact"] = impact / baseline
        result["publication_receipt"] = build_publication_receipt(
            result,
            VerificationContext(
                result["input_sha256"],
                expected_publication_gates(result),
                ENGINE_VERSION,
            ),
        )
        result["result_sha256"] = canonical_sha256(
            {key: value for key, value in result.items() if key != "result_sha256"}
        )
        forged["forecast_result_sha256"] = canonical_sha256(result)
        identity = {
            key: forged[key]
            for key in (
                "company_name",
                "as_of_date",
                "forecast_version",
                "input_sha256",
                "forecast_result_sha256",
                "engine_version",
                "forecast_schema_version",
                "snapshot_schema_version",
            )
        }
        forged["snapshot_id"] = canonical_sha256(identity)
        with self.assertRaisesRegex(
            ForecastInputError, "sensitivity down terminal recomputation mismatch"
        ):
            evaluate_snapshot(forged, actuals_document())
        with self.assertRaisesRegex(
            ForecastInputError, "sensitivity down terminal recomputation mismatch"
        ):
            validate_published_forecast(result, snapshot["input_document"])

    def test_snapshot_swapped_input_and_result_anchored_hash_is_rejected(self) -> None:
        # R1.1 regression pin (N-01 D3): the snapshot validator already binds
        # the input fingerprint; swapping both input and result while anchoring
        # to the legitimate input hash must stay REJECTED even after the shared
        # verify_input_binding refactor (R1.1).
        from revenue_publication import (
            VerificationContext,
            build_publication_receipt,
            expected_publication_gates,
        )

        data = forecast_document()
        snapshot = create_snapshot(copy.deepcopy(data), "v1")
        attacker_input = copy.deepcopy(data)
        for parameter in attacker_input["parameters"]:
            if isinstance(parameter.get("value"), (int, float)) and parameter.get(
                "kind"
            ) in {"analyst_assumption", "scenario_stress"}:
                parameter["value"] = float(parameter["value"]) * 1.5
        forged_result = run_forecast(attacker_input)
        forged_result["input_sha256"] = snapshot["input_sha256"]
        forged_result["workflow_compliance_receipt"]["input_sha256"] = snapshot[
            "input_sha256"
        ]
        forged_result["workflow_compliance_receipt"]["receipt_sha256"] = (
            canonical_sha256(
                {
                    key: value
                    for key, value in forged_result[
                        "workflow_compliance_receipt"
                    ].items()
                    if key != "receipt_sha256"
                }
            )
        )
        forged_result["publication_receipt"] = build_publication_receipt(
            forged_result,
            VerificationContext(
                forged_result["input_sha256"],
                expected_publication_gates(forged_result),
                ENGINE_VERSION,
            ),
        )
        forged_result["result_sha256"] = canonical_sha256(
            {key: value for key, value in forged_result.items() if key != "result_sha256"}
        )
        forged = copy.deepcopy(snapshot)
        forged["forecast_result"] = forged_result
        forged["input_document"] = copy.deepcopy(attacker_input)
        forged["forecast_result_sha256"] = canonical_sha256(forged_result)
        identity = {
            key: forged[key]
            for key in (
                "company_name",
                "as_of_date",
                "forecast_version",
                "input_sha256",
                "forecast_result_sha256",
                "engine_version",
                "forecast_schema_version",
                "snapshot_schema_version",
            )
        }
        forged["snapshot_id"] = canonical_sha256(identity)
        with self.assertRaises(ForecastInputError):
            validate_snapshot(forged)

    def test_snapshot_legacy_unknown_engine_is_rejected(self) -> None:
        # Phase 6 B2 RED (F-10): a snapshot with a legacy schema must not accept
        # an arbitrary engine version; only CHANGELOG-documented pairs pass.
        snapshot = create_snapshot(forecast_document(), "v1")
        forged = copy.deepcopy(snapshot)
        forged["forecast_schema_version"] = "3.4"
        forged["engine_version"] = "9.9.9"
        with self.assertRaisesRegex(ForecastInputError, "not a"):
            validate_snapshot(forged)


if __name__ == "__main__":
    unittest.main()
