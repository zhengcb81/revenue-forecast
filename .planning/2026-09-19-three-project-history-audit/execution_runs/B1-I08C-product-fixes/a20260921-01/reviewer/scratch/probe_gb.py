"""Reviewer probe #4 — is REM-03 G-B load-bearing?

Oracle r1 §3.6 argues G-B (the sum gate) is the "stronger presentation claim" on
top of G-A (the per-segment identity gate).  This probe tests that claim by
constructing the one opening-base redistribution the two gates provably cannot
see together:

  * move opening base OUT of an untraced segment (a segment whose
    base_revenue_parameter_id is absent, so G-A `continue`s past it),
  * move the same amount INTO a traced segment, and add enough positive
    base_revenue so that the SUM gate still reconciles to the unchanged company
    total,
  * fix `parameter_trace` so the strong path's `parameter_trace ==
    data["parameters"]` require holds honestly (the untraced segment's flat
    model has one explicit parameter that absorbs the leftover),
  * rebuild every scenario path with the engine's own calculate_model_path.

Everything the strong path can recompute is recomputed correctly.  If the
resulting artifact is ACCEPTED, the 分部表 opening-base column is still not
bound in full, and G-B is not a backstop but a weaker sibling of G-A.
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
    ATTEMPT / "reviewer" / "scratch" / "probe_registry4.jsonl"
)
os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)

import revenue_core  # noqa: E402
import revenue_publication  # noqa: E402
import revenue_report  # noqa: E402
from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from revenue_core import calculate_cagr, calculate_model_path  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


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


def rebuild_segment_paths(segment, parameter_index, years):
    base = float(segment["base_revenue"])
    for scenario in ("low", "base", "high"):
        output = segment["scenarios"][scenario]
        recalculated = calculate_model_path(
            output["model"], base, output["driver_parameter_ids"],
            parameter_index, list(map(int, years)), scenario,
        )
        output["modeled_activity"] = recalculated["annual_revenue"]
        output["driver_values"] = recalculated["driver_values"]
        modeled = list(output["modeled_activity"].values())
        recognition = segment["recognition"]
        if recognition["timing"] == "over_time":
            progress = list(output["progress_values"].values())
            recognized = {y: v * f for y, v, f in zip(years, modeled, progress)}
        elif recognition["mode"] == "lagged_activity":
            lag = recognition["lag_years"]
            recognized = dict(zip(years, list(output["carry_in_revenue"]) + modeled[:-lag]))
        else:
            recognized = dict(zip(years, modeled))
        output["recognized_revenue"] = recognized
        if "effective_revenue" in output:
            output["effective_revenue"] = dict(recognized)


def rebuild_consolidated(result, years):
    for scenario in ("low", "base", "high"):
        annual = {}
        for year in years:
            total = 0.0
            for segment in result["segments"]:
                output = segment["scenarios"][scenario]
                eff = output.get("effective_revenue", output["recognized_revenue"])
                total += float(eff[year])
            for adjustment in result.get("adjustment_bridge", []):
                total += float(adjustment["annual_adjustment"][year])
            annual[year] = total
        consolidated = result["consolidated_forecast"][scenario]
        consolidated["annual_revenue"] = annual
        values = [float(annual[y]) for y in years]
        consolidated["terminal_revenue"] = values[-1]
        base = float(result["base_revenue"])
        consolidated["cagr"] = calculate_cagr(base, values[-1], len(years))
        consolidated["annual_growth"] = {}
        for i, y in enumerate(years):
            previous = base if i == 0 else float(annual[years[i - 1]])
            consolidated["annual_growth"][y] = None if previous == 0 else float(annual[y]) / previous - 1
        consolidated["incremental_revenue"] = values[-1] - base
        if isinstance(consolidated.get("incremental_contribution"), dict):
            consolidated["incremental_contribution"]["total"] = consolidated["incremental_revenue"]
        for bridge in consolidated["segment_bridge"]:
            segment = next(s for s in result["segments"] if s["name"] == bridge["name"])
            output = segment["scenarios"][scenario]
            bridge["annual_revenue"] = dict(
                output.get("effective_revenue", output["recognized_revenue"])
            )
    weighted = result.get("probability_weighted_forecast")
    probabilities = result.get("scenario_probabilities")
    if weighted and probabilities:
        weighted["terminal_revenue"] = sum(
            float(probabilities[s])
            * float(result["consolidated_forecast"][s]["terminal_revenue"])
            for s in ("low", "base", "high")
        )


def check(label, fn):
    try:
        fn()
    except ForecastInputError as exc:
        print(f"{label}: REJECTED <{exc}>")
        return "REJECTED"
    except Exception as exc:  # noqa: BLE001
        print(f"{label}: ERROR {type(exc).__name__} <{exc}>")
        return "ERROR"
    print(f"{label}: ACCEPTED")
    return "ACCEPTED"


honest = revenue_core.run_forecast(forecast_document())
years = list(map(str, honest["forecast_years"]))
print("A/B bases:", [(s["name"], s["base_revenue"], s.get("base_revenue_parameter_id")) for s in honest["segments"]])
print("company base:", honest["base_revenue"])

# ---------------------------------------------------------------------------
# Attack: shift 100 of opening base from untraced B into traced A, and add
# enough positive base to keep the SUM gate satisfied.
# ---------------------------------------------------------------------------
MOVE = 100.0            # taken out of Segment B
FREE = 60.0             # extra base added so the sum still reconciles
A_OLD, B_OLD = 100.0, 50.0

forged = copy.deepcopy(honest)
seg_a, seg_b = forged["segments"][0], forged["segments"][1]

# 1. untrace the segment we take base from, so G-A skips it
old_b_base_id = seg_b.pop("base_revenue_parameter_id")
print("removed base_revenue_parameter_id:", old_b_base_id)

# 2. move base out of B and into A; sum still equals the company base
seg_a["base_revenue"] = A_OLD + MOVE + FREE     # 260
seg_b["base_revenue"] = B_OLD - MOVE            # -50 -> invalid, so use 0 + Free
seg_b["base_revenue"] = B_OLD - MOVE
# keep everything non-negative: instead take MOVE from B's *growth* by flat 0 base
# -> simplest coherent choice: B keeps its honest base and A absorbs everything,
#    with the sum held at 150 by declaring B's base as (150 - A_new).
seg_b["base_revenue"] = 150.0 - seg_a["base_revenue"]  # = -110 -> negative
print("naive negative-B base:", seg_b["base_revenue"])

# The coherent version: B is untraced, so its base may be anything >= 0 as long
# as A + B == 150 and A matches its own trace parameter.
A_NEW = 150.0
seg_b["base_revenue"] = 150.0 - A_NEW  # 0.0
print("chosen A base:", A_NEW, " B base:", seg_b["base_revenue"])

# 3. make A's trace parameter agree with A's new base (parameter_trace is bound
#    to the embedded input, which declares A's base as 100 -> so the input
#    document must be edited too and re-anchored; an external consumer holding
#    the original input would reject that, which is exactly the boundary).
index = {p["parameter_id"]: p for p in forged["parameter_trace"]}
index["segment_a_base"]["value"] = A_NEW
for param in forged["input_document"]["parameters"]:
    if param["parameter_id"] == "segment_a_base":
        param["value"] = A_NEW
# B's flat model uses an explicit single parameter; re-point it at a value that
# reproduces the (zero) base, keeping the trace honest.
b_model = seg_b["scenarios"]["base"]["model"]
print("B model:", b_model, "drivers:", seg_b["scenarios"]["base"]["driver_parameter_ids"])
for driver, ids in seg_b["scenarios"]["base"]["driver_parameter_ids"].items():
    for pid_ in ids:
        if pid_ in index:
            index[pid_]["value"] = 0.0
for param in forged["input_document"]["parameters"]:
    if param["parameter_id"] in {p for ids in seg_b["scenarios"]["base"]["driver_parameter_ids"].values() for p in ids}:
        param["value"] = 0.0
forged["input_sha256"] = canonical_sha256(forged["input_document"])

rebuild_segment_paths(seg_a, index, years)
rebuild_segment_paths(seg_b, index, years)
rebuild_consolidated(forged, years)
rehash(forged)

print("\nforged opening bases:", [(s["name"], s["base_revenue"], s.get("base_revenue_parameter_id")) for s in forged["segments"]])
print("sum:", sum(float(s["base_revenue"]) for s in forged["segments"]), " company base:", forged["base_revenue"])
print()
check("receipt layer              ", lambda: revenue_publication.validate_publication_receipt(forged))
check("validate_forecast_output   ", lambda: revenue_report.validate_forecast_output(forged))
try:
    md = revenue_report.render_markdown(forged)
    rows = [ln for ln in md.splitlines() if ln.startswith("| Segment")]
    print("render_markdown ACCEPTED — 分部表 rows:")
    for row in rows:
        print("   ", row)
except ForecastInputError as exc:
    print("render_markdown REJECTED <", exc, ">")
