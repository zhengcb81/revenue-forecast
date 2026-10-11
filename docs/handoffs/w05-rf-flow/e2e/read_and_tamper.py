"""W05-RF-FLOW CLI E2E: published output reader + rehashed-tamper rejection.

Usage: read_and_tamper.py <forecast.json> <tamper: window|currency>

Reads the published artifact through the native strong reader
(``revenue_report.validate_forecast_output`` with its embedded bound input),
then tampers one substantive field and recomputes ``result_sha256`` — the
rehash must not make the forgery pass.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))

from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from revenue_report import validate_forecast_output  # noqa: E402


def rehash(result: dict) -> dict:
    result["result_sha256"] = canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    )
    return result


def main() -> int:
    result = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    tamper = sys.argv[2]
    validate_forecast_output(result)
    print(
        "reader: PASS schema=%s engine=%s windows=%s"
        % (
            result["schema_version"],
            result["engine_version"],
            [
                (p["parameter_id"], p["period_start"], p["period_end"], p["value"])
                for p in result["parameter_trace"]
                if p.get("time_basis") == "period_flow"
            ],
        )
    )
    forged = copy.deepcopy(result)
    if tamper == "window":
        target = next(
            item for item in forged["parameter_trace"]
            if item.get("time_basis") == "period_flow"
        )
        target["period_end"] = "2026-12-31"
        print(f"tamper: {target['parameter_id']} period_end -> 2026-12-31 (rehashed)")
    elif tamper == "currency":
        replacement = "USD" if forged["currency"] == "CNY" else "CNY"
        forged["currency"] = replacement
        print(f"tamper: currency -> {replacement} (rehashed)")
    else:
        raise SystemExit(f"unknown tamper kind: {tamper}")
    rehash(forged)
    try:
        validate_forecast_output(forged)
    except (ForecastInputError, TypeError) as exc:
        print(f"tamper rejected: {exc}")
        return 0
    print("tamper NOT rejected (FAIL)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
