"""Reviewer probe #2: the 'consistent re-basing' attack on REM-03.

Attacker goal: shift 1000 of opening base into Segment A so the official 分部表
opening-base column prints a different split, while keeping the company total
untouched (which is what the oracle says was never forgeable).

The attacker is granted EVERYTHING a hash-recomputing, fully-informed attacker
can do: mutate parameter_trace, recompute the segment model with the engine's own
calculate_model_path, rebuild recognition + effective revenue, rebuild the
consolidated paths, and recompute all self-hashes.  The only thing kept is
input_document / input_sha256 (the embedded input anchor).
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit\execution_runs"
    r"\B1-I08C-product-fixes\a20260921-01"
)
REPO = ATTEMPT / "reviewer" / "scratch" / "fixed_rf"
sys.path.insert(0, str(REPO / "tests"))
sys.path.insert(0, str(REPO / "scripts"))
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
os.environ["REVENUE_PUBLICATION_REGISTRY"] = str(
    ATTEMPT / "reviewer" / "scratch" / "probe_registry2.jsonl"
)
os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)

import revenue_core  # noqa: E402
import revenue_publication  # noqa: E402
import revenue_report  # noqa: E402
from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from revenue_core import calculate_cagr, calculate_model_path  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

DELTA = 1000.0


def rehash(pkg):
    receipt = pkg["publication_receipt"]
    receipt["validated_payload_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k not in ("result_sha256", "publication_receipt")}
    )
    receipt["receipt_sha256"] = canonical_sha256(
        {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    )
    pkg["result_sha256"] = canonical_sha256(
        {k: v for k, v in pkg.items() if k != "result_sha256"}
    )
    return pkg


def rebuild_segment(segment, parameter_index, years):
    """Recompute everything inside one segment from its (new) base_revenue."""
    base = float(segment["base_revenue"])
    for scenario in ("low", "base", "high"):
        output = segment["scenarios"][scenario]
        recalculated = calculate_model_path(
            output["model"],
            base,
            output["driver_parameter_ids"],
            parameter_index,
            list(map(int, years)),
            scenario,
        )
        output["modeled_activity"] = recalculated["annual_revenue"]
        modeled = list(output["modeled_activity"].values())
        recognition = segment["recognition"]
        if recognition["timing"] == "over_time":
            progress = list(output["progress_values"].values())
            output["recognized_revenue"] = {
                year: value * factor
                for year, value, factor in zip(years, modeled, progress)
            }
        elif recognition["mode"] == "lagged_activity":
            lag = recognition["lag_years"]
            expected = list(output["carry_in_revenue"]) + modeled[:-lag]
            output["recognized_revenue"] = dict(zip(years, expected))
        else:
            output["recognized_revenue"] = dict(zip(years, modeled))
        if "effective_revenue" in output:
            output["effective_revenue"] = dict(output["recognized_revenue"])


def rebuild_consolidated(result, years):
    """Rebuild consolidated paths from the (forged) segments using the engine."""
    for scenario in ("low", "base", "high"):
        annual = {}
        for year in years:
            total = 0.0
            for segment in result["segments"]:
                output = segment["scenarios"][scenario]
                effective = output.get("effective_revenue", output["recognized_revenue"])
                total += float(effective[year])
            for adjustment in result.get("adjustment_bridge", []):
                total += float(adjustment["annual_adjustment"][year])
            annual[year] = total
        consolidated = result["consolidated_forecast"][scenario]
        consolidated["annual_revenue"] = annual
        values = [float(annual[year]) for year in years]
        consolidated["terminal_revenue"] = values[-1]
        consolidated["cagr"] = calculate_cagr(
            float(result["base_revenue"]), values[-1], len(years)
        )
        consolidated["annual_growth"] = {}
        for index, year in enumerate(years):
            previous = (
                float(result["base_revenue"])
                if index == 0
                else float(annual[years[index - 1]])
            )
            consolidated["annual_growth"][year] = (
                None if previous == 0 else float(annual[year]) / previous - 1
            )
        consolidated["incremental_revenue"] = values[-1] - float(result["base_revenue"])
        if isinstance(consolidated.get("incremental_contribution"), dict):
            consolidated["incremental_contribution"]["total"] = consolidated[
                "incremental_revenue"
            ]
        for bridge in consolidated["segment_bridge"]:
            segment = next(
                s for s in result["segments"] if s["name"] == bridge["name"]
            )
            output = segment["scenarios"][scenario]
            bridge["annual_revenue"] = dict(
                output.get("effective_revenue", output["recognized_revenue"])
            )
    weighted = result.get("probability_weighted_forecast")
    probabilities = result.get("scenario_probabilities")
    if weighted and probabilities:
        years_list = list(years)
        weighted["terminal_revenue"] = sum(
            float(probabilities[s]) * float(result["consolidated_forecast"][s]["terminal_revenue"])
            for s in ("low", "base", "high")
        )


honest = revenue_core.run_forecast(forecast_document())
years = list(map(str, honest["forecast_years"]))
print("years:", years)
print("segment_bridge names:", [b["name"] for b in honest["consolidated_forecast"]["base"]["segment_bridge"]])
print("adjustment_bridge:", honest["consolidated_forecast"]["base"].get("adjustment_bridge"))
print("has effective_revenue:", ["effective_revenue" in s["scenarios"]["base"] for s in honest["segments"]])

forged = copy.deepcopy(honest)
index = {
    p["parameter_id"]: p for p in forged["parameter_trace"]
}
# 1. shift base into segment A in the presentation field ...
forged["segments"][0]["base_revenue"] = float(forged["segments"][0]["base_revenue"]) + DELTA
# 2. ... and into its source parameter, so G-A's identity bind still holds
pid = forged["segments"][0]["base_revenue_parameter_id"]
index[pid]["value"] = float(index[pid]["value"]) + DELTA
# 3. rebuild the segment model from the new base
rebuild_segment(forged["segments"][0], index, years)
# 4. company total unchanged (documented as never forgeable) -> rebuild paths
rebuild_consolidated(forged, years)
rehash(forged)

print("\nforged segment bases:", [s["base_revenue"] for s in forged["segments"]])
print("forged company base :", forged["base_revenue"])
print("segment_bridge annual (base, FY1):", [b["annual_revenue"][years[0]] for b in forged["consolidated_forecast"]["base"]["segment_bridge"]])
print("consolidated base FY1:", forged["consolidated_forecast"]["base"]["annual_revenue"][years[0]])

print("\n--- checks ---")
for label, fn in (
    ("receipt layer      ", lambda: revenue_publication.validate_publication_receipt(forged)),
    ("validate_forecast_output", lambda: revenue_report.validate_forecast_output(forged)),
    ("validate_published_forecast", lambda: revenue_report.validate_published_forecast(forged, forged["input_document"])),
):
    try:
        fn()
        print(f"{label}: ACCEPTED")
    except ForecastInputError as exc:
        print(f"{label}: REJECTED <{exc}>")
    except Exception as exc:  # noqa: BLE001
        print(f"{label}: ERROR {type(exc).__name__} <{exc}>")

try:
    md = revenue_report.render_markdown(forged)
    rows = [line for line in md.splitlines() if "Segment A" in line or "Segment B" in line]
    print("\nrender_markdown ACCEPTED; 分部表 rows:")
    for row in rows[:4]:
        print("   ", row)
except ForecastInputError as exc:
    print("\nrender_markdown REJECTED <", exc, ">")
