"""Reviewer probe #5 — negative-base redistribution.

G-B (the sum gate) is the only gate that constrains a segment WITHOUT a
base_revenue_parameter_id, and the input-side rule `base revenue cannot be
negative` (contracts/document.py:922) is NOT mirrored by either new output gate.
If nothing else rejects a negative per-segment opening base, then:

    A' = A + 950,  B' = B - 950   (sum unchanged -> G-B passes)
    A has a trace parameter (re-pointed + re-anchored), B has none (G-A skips)

is a redistribution that still renders a 分部表 opening-base column that is not
the artifact's own story.  This probe asks only whether the gates FIRE; it does
not assert the presentation value is reachable without also editing the input
document and its anchor.
"""
from __future__ import annotations

import copy
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
    ATTEMPT / "reviewer" / "scratch" / "probe_registry5.jsonl"
)
os.environ.pop("REVENUE_ATTESTATION_PROVIDER", None)
os.environ.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)

import revenue_core  # noqa: E402
import revenue_publication  # noqa: E402
import revenue_report  # noqa: E402
from contracts.evidence import ForecastInputError, canonical_sha256  # noqa: E402
from revenue_core import calculate_cagr, calculate_model_path  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

MOVE = 950.0


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


def rebuild(segment, parameter_index, years):
    base = float(segment["base_revenue"])
    for scenario in ("low", "base", "high"):
        output = segment["scenarios"][scenario]
        r = calculate_model_path(
            output["model"], base, output["driver_parameter_ids"],
            parameter_index, list(map(int, years)), scenario,
        )
        output["modeled_activity"] = r["annual_revenue"]
        output["driver_values"] = r["driver_values"]
        modeled = list(output["modeled_activity"].values())
        recognition = segment["recognition"]
        if recognition["timing"] == "over_time":
            progress = list(output["progress_values"].values())
            rec = {y: v * f for y, v, f in zip(years, modeled, progress)}
        elif recognition["mode"] == "lagged_activity":
            lag = recognition["lag_years"]
            rec = dict(zip(years, list(output["carry_in_revenue"]) + modeled[:-lag]))
        else:
            rec = dict(zip(years, modeled))
        output["recognized_revenue"] = rec
        if "effective_revenue" in output:
            output["effective_revenue"] = dict(rec)


def rebuild_consolidated(result, years):
    for scenario in ("low", "base", "high"):
        annual = {}
        for year in years:
            total = sum(
                float(
                    s["scenarios"][scenario].get(
                        "effective_revenue", s["scenarios"][scenario]["recognized_revenue"]
                    )[year]
                )
                for s in result["segments"]
            )
            annual[year] = total
        c = result["consolidated_forecast"][scenario]
        c["annual_revenue"] = annual
        values = [float(annual[y]) for y in years]
        c["terminal_revenue"] = values[-1]
        base = float(result["base_revenue"])
        c["cagr"] = calculate_cagr(base, values[-1], len(years))
        c["annual_growth"] = {}
        for i, y in enumerate(years):
            prev = base if i == 0 else float(annual[years[i - 1]])
            c["annual_growth"][y] = None if prev == 0 else float(annual[y]) / prev - 1
        c["incremental_revenue"] = values[-1] - base
        if isinstance(c.get("incremental_contribution"), dict):
            c["incremental_contribution"]["total"] = c["incremental_revenue"]
        for bridge in c["segment_bridge"]:
            seg = next(s for s in result["segments"] if s["name"] == bridge["name"])
            out = seg["scenarios"][scenario]
            bridge["annual_revenue"] = dict(
                out.get("effective_revenue", out["recognized_revenue"])
            )


honest = revenue_core.run_forecast(forecast_document())
years = list(map(str, honest["forecast_years"]))
seg_a, seg_b = honest["segments"][0], honest["segments"][1]
print("honest:", [(s["name"], s["base_revenue"], s.get("base_revenue_parameter_id")) for s in honest["segments"]])
print("B driver ids:", json.dumps(seg_b["scenarios"]["base"]["driver_parameter_ids"]) if False else seg_b["scenarios"]["base"]["driver_parameter_ids"])
print("B formula:", seg_b["scenarios"]["base"].get("formula"))

forged = copy.deepcopy(honest)
fa, fb = forged["segments"][0], forged["segments"][1]
fa["base_revenue"] = float(fa["base_revenue"]) + MOVE
fb["base_revenue"] = float(fb["base_revenue"]) - MOVE
print("forged bases:", [fa["base_revenue"], fb["base_revenue"]],
      "sum:", fa["base_revenue"] + fb["base_revenue"], "company base:", forged["base_revenue"])

index = {p["parameter_id"]: p for p in forged["parameter_trace"]}
index[fa["base_revenue_parameter_id"]]["value"] = fa["base_revenue"]
for param in forged["input_document"]["parameters"]:
    if param["parameter_id"] == fa["base_revenue_parameter_id"]:
        param["value"] = fa["base_revenue"]
        param.pop("constraints", None)
forged["input_sha256"] = canonical_sha256(forged["input_document"])
rebuild(fa, index, years)
rebuild(fb, index, years)
rebuild_consolidated(forged, years)
rehash(forged)

print("\nmodeled_activity after rebuild:", {s["name"]: s["scenarios"]["base"]["modeled_activity"] for s in forged["segments"]})
for label, fn in (
    ("receipt layer           ", lambda: revenue_publication.validate_publication_receipt(forged)),
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
