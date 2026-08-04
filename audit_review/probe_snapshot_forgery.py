# Diagnostic probe: forged sensitivity inside a rehashed snapshot.
# Read-only audit artifact; not part of the product test suite.
# Updated for Phase 6 A1: the public builder no longer self-issues receipts, so
# the probe simulates a fully-informed attacker who forges every hash INCLUDING
# the verification context, and confirms the strong validator still rejects.
import copy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
sys.path.insert(0, str(root / "tests"))

from revenue_core import canonical_sha256, ForecastInputError, ENGINE_VERSION
from revenue_report import validate_published_forecast
from revenue_backtest import create_snapshot, validate_snapshot
from revenue_publication import (
    VerificationContext,
    build_publication_receipt,
    expected_publication_gates,
)
from test_recognition_bridge import forecast_document

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

snapshot = create_snapshot(copy.deepcopy(data), "v1")
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
        result["input_sha256"], expected_publication_gates(result), ENGINE_VERSION
    ),
)
result["result_sha256"] = canonical_sha256(
    {k: v for k, v in result.items() if k != "result_sha256"}
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

try:
    validate_snapshot(forged)
    print("SNAPSHOT-STRONG: ACCEPTED")
except ForecastInputError as exc:
    print(f"SNAPSHOT-STRONG: REJECTED:{exc}")

try:
    validate_published_forecast(result, snapshot["input_document"])
    print("RESULT-STRONG: ACCEPTED")
except ForecastInputError as exc:
    print(f"RESULT-STRONG: REJECTED:{exc}")
