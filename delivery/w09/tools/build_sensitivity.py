"""Build the W09 sensitivity record from the native outputs and the bridge.

Every number here is either read from the native forecast output (sensitivities,
segment paths) or recomputed with Decimal from the component bridge. Nothing is
asserted from a preparation script's own PASS flags.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 40

WORKDIR = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-r1-research")
DELIVERY = WORKDIR / "delivery" / "w09"
MAIN = DELIVERY / "forecast" / "main-forecast.json"
STRESS = DELIVERY / "forecast" / "stress-forecast.json"
BRIDGE = DELIVERY / "research" / "component-bridge.json"
OUT = DELIVERY / "research" / "sensitivity.json"
SEALED = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec"
              r"\execution_replays\r1-remediation-01\phase_b\forecast")


def D(value) -> Decimal:
    return Decimal(str(value))


def main() -> int:
    forecast = json.loads(MAIN.read_text(encoding="utf-8"))
    stress = json.loads(STRESS.read_text(encoding="utf-8"))
    bridge = json.loads(BRIDGE.read_text(encoding="utf-8"))
    rows = {row["metric_id"]: row for row in bridge["rows"]}

    base = forecast["consolidated_forecast"]["base"]
    seg = {row["name"]: row["annual_revenue"] for row in base["segment_bridge"]}
    non_tides = {y: D(seg["非TIDES化学业务"][y]) for y in ("2026", "2027", "2028")}
    tides = {y: D(seg["TIDES（化学业务内）"][y]) for y in ("2026", "2027", "2028")}
    dm_fy25 = D(rows["dm_fy25"]["value"])
    residual_fy25 = D(rows["residual_fy25"]["value"])
    residual_h225 = D(rows["residual_h225"]["value"])
    non_h126 = D(rows["non_tides_h126"]["value"])

    # Residual sensitivity: what the implied H2/FY2028 D&M requirement becomes
    # when the residual H2 is not exactly flat. -10% / flat / +10% are stated
    # arithmetic conditions, never an empirical range.
    scenarios = []
    for label, factor in (("-10%", D("0.9")), ("flat", D("1")), ("+10%", D("1.1"))):
        residual_h226 = residual_h225 * factor
        dm_h226 = non_tides["2026"] - non_h126 - residual_h226
        dm_h226_yoy = dm_h226 / D(rows["dm_h225"]["value"]) - 1
        residual_fy28 = residual_fy25 * factor
        dm_fy28 = non_tides["2028"] - residual_fy28
        scenarios.append({
            "residual_h2_condition": label,
            "residual_h2_cny_million": str(residual_h226),
            "implied_dm_h2_cny_million": str(dm_h226),
            "implied_dm_h2_yoy": str(dm_h226_yoy),
            "residual_fy28_cny_million": str(residual_fy28),
            "implied_dm_fy28_cny_million": str(dm_fy28),
            "implied_dm_fy28_multiple_of_fy25": str(dm_fy28 / dm_fy25),
        })

    # Native sensitivity results, kept exactly as computed by the engine.
    native = []
    for row in forecast["sensitivities"]:
        native.append({
            "name": row["name"],
            "parameter_id": row["parameter_id"],
            "shock_type": row["shock_type"],
            "shock_value": row["shock_value"],
            "baseline_terminal_revenue": row["baseline_terminal_revenue"],
            "down_terminal_revenue": row["down_terminal_revenue"],
            "up_terminal_revenue": row["up_terminal_revenue"],
            "max_absolute_terminal_impact": row["max_absolute_terminal_impact"],
            "max_relative_terminal_impact": row["max_relative_terminal_impact"],
            "clamped": row.get("clamped"),
            "affected_derived_parameter_ids": row["dependency_recalculation"][
                "affected_derived_parameter_ids"],
        })

    stress_delta = {
        scenario: {y: stress["consolidated_forecast"][scenario]["segment_subtotal"][y]
                   - forecast["consolidated_forecast"][scenario]["segment_subtotal"][y]
                   for y in ("2026", "2027", "2028")}
        for scenario in ("low", "base", "high")
    }
    sealed_stress = json.loads((SEALED / "final3-shared-stress.json").read_text(encoding="utf-8"))
    sealed_delta = {
        scenario: {y: sealed_stress["consolidated_forecast"][scenario]["segment_subtotal"][y]
                   - json.loads((SEALED / "final3-forecast.json").read_text(encoding="utf-8"))[
                       "consolidated_forecast"][scenario]["segment_subtotal"][y]
                   for y in ("2026", "2027", "2028")}
        for scenario in ("low", "base", "high")
    }

    record = {
        "schema_version": "w09-sensitivity/1",
        "package_id": "W09-RF-RESEARCH",
        "purpose": ("Key sensitivities and falsifiers for the largest driver. Every number is a "
                    "conditional arithmetic consequence of a stated assumption; none is an empirical "
                    "forecast interval or probability."),
        "main_forecast_sha256": hashlib.sha256(MAIN.read_bytes()).hexdigest(),
        "stress_forecast_sha256": hashlib.sha256(STRESS.read_bytes()).hexdigest(),
        "base_paths": {
            "non_tides": {y: str(v) for y, v in non_tides.items()},
            "tides": {y: str(v) for y, v in tides.items()},
        },
        "native_sensitivities": native,
        "residual_condition_sensitivity": {
            "basis": ("Holds the old Base non-TIDES FY2026/FY2028 paths fixed and varies only the "
                      "assumed H2/FY2028 residual level around its FY2025 level. -10%/+10% are stated "
                      "arithmetic conditions, not an observed range, not a confidence interval."),
            "rows": scenarios,
            "reading": ("A higher residual assumption LOWERS the D&M growth the same non-TIDES total "
                        "requires; the requirement is a decomposition identity under a condition, not "
                        "a forecast of D&M."),
        },
        "stress_effect": {
            "main_vs_stress_delta_cny_million": stress_delta,
            "sealed_old_delta_cny_million": sealed_delta,
            "identical_to_sealed": stress_delta == sealed_delta,
            "mechanism": ("One shared Q4 acceptance/qualification disruption: 4,500 CNY million leaves "
                          "FY2026 (9,000 cohort x 50% exposure), of which 3,600 returns in FY2027 "
                          "(80% catch-up) and 900 is cancelled. FY2028 is unaffected because the shock "
                          "is a timing/cancellation event, not a level change."),
            "not_double_counted": ("TIDES (3,000) and non-TIDES (6,000) are the two mutually exclusive "
                                   "Chemistry pools; the same exposure/boundary/catch-up factors are "
                                   "applied once to each."),
        },
        "falsifiers": bridge["falsifiers"],
        "not_a_probability": True,
    }
    OUT.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"residual_rows": len(scenarios), "native_sensitivities": len(native),
                      "stress_delta_base": stress_delta["base"],
                      "identical_to_sealed": stress_delta == sealed_delta}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
