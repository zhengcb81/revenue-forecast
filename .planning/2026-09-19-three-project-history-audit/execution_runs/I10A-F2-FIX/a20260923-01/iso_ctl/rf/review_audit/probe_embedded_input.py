# Adversarial probe (review_audit): embedded input_document tampering.
# Tests whether a published result's embedded input_document can be modified
# while keeping input_sha256 and all hashes valid.
import copy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
sys.path.insert(0, str(root / "tests"))

from revenue_core import canonical_sha256, ForecastInputError, run_forecast
from revenue_report import validate_forecast_output, validate_published_forecast
from revenue_publication import (
    VerificationContext,
    build_publication_receipt,
    expected_publication_gates,
    validate_publication_receipt,
)
from revenue_core import ENGINE_VERSION
from test_recognition_bridge import forecast_document


def resign(result):
    result["publication_receipt"] = build_publication_receipt(
        result,
        VerificationContext(
            result["input_sha256"], expected_publication_gates(result), ENGINE_VERSION
        ),
    )
    result["result_sha256"] = canonical_sha256(
        {k: v for k, v in result.items() if k != "result_sha256"}
    )


def check(label, result):
    try:
        validate_forecast_output(result)
        print(f"{label}: ACCEPTED")
    except (ForecastInputError, TypeError) as exc:
        print(f"{label}: REJECTED:{str(exc)[:120]}")


data = forecast_document()
data["sensitivity_tests"] = [
    {
        "name": "Core terminal revenue",
        "parameter_id": data["segments"][0]["scenarios"]["base"][
            "driver_parameter_ids"
        ]["revenue"][1],
        "shock_type": "percent",
        "shock_value": 0.1,
    }
]
legit = run_forecast(copy.deepcopy(data))
check("A0 baseline legitimate", legit)

# Attack A1: tamper embedded input evidence text, keep input_sha256, resign hashes
a1 = copy.deepcopy(legit)
a1["input_document"]["sources"][0]["capture"]["checked_excerpt"] = (
    "TAMPERED EXCPT: management secretly guided 50% growth"
)
resign(a1)
check("A1 embedded excerpt tampered + rehash", a1)

# Attack A2: does input_sha256 still match embedded doc after A1?
print(
    "A2 embedded doc hash matches input_sha256:",
    canonical_sha256(a1["input_document"]) == a1["input_sha256"],
)

# Attack B: tamper embedded input parameter value, keep stored numbers, resign
b1 = copy.deepcopy(legit)
for p in b1["input_document"]["parameters"]:
    if p["parameter_id"] == data["sensitivity_tests"][0]["parameter_id"]:
        if isinstance(p.get("value"), (int, float)):
            p["value"] = float(p["value"]) * 2.0
resign(b1)
check("B1 embedded parameter tampered + rehash (no engine rerun)", b1)

# Attack C: embed an input that fails the input contract (missing capture),
# but keep the result computed from the legitimate input.
c1 = copy.deepcopy(legit)
del c1["input_document"]["sources"][0]["capture"]["receipt_sha256"]
resign(c1)
check("C1 embedded input contract-broken + rehash", c1)

# Attack D: swap embedded input entirely with a different valid input,
# keep input_sha256 of original, resign.
d1 = copy.deepcopy(legit)
data2 = forecast_document()
data2["forecast_version"] = "attacker-version"
data2["sensitivity_tests"] = data["sensitivity_tests"]
d1["input_document"] = copy.deepcopy(data2)
resign(d1)
check("D1 embedded input swapped + rehash", d1)
